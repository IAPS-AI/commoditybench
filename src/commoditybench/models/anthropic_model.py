"""Anthropic (Claude) adapter.

Uses the Messages API with native structured outputs (``output_config.format``) so the
answer arrives as schema-valid JSON, and adaptive thinking for the reasoning-heavy
classification task. Defaults to Claude Opus 4.8.

Also implements the **agentic CCL-navigation** path (:meth:`AnthropicModel.classify_agentic`):
a manual tool-use loop where the model calls the ``ccl.tools`` to walk the Commerce
Control List, then ends by calling ``submit_classification`` with its final answer.
"""

from __future__ import annotations

import json
import os
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_exponential

from .base import ClassifierModel, Prediction
from .agentic import (
    AGENTIC_SYSTEM_PROMPT,
    DEFAULT_MAX_STEPS,
    SUBMIT_TOOL_DESCRIPTION,
    SUBMIT_TOOL_NAME,
    prediction_from_submission,
    submit_tool_input_schema,
)
from ..ccl.tools import CCLToolbox, anthropic_tools
from ..dataset import Question
from ..prompts import ANSWER_SCHEMA, build_user_prompt

DEFAULT_MODEL = "claude-opus-4-8"


def _strip_thinking(messages: list) -> list:
    """Copy ``messages`` with ``thinking``/``redacted_thinking`` blocks removed.

    Needed before a tool-forced (thinking-disabled) call: the API rejects thinking
    blocks in history when thinking is off. Assistant tool_use blocks are kept, so
    tool_use/tool_result pairing stays intact.
    """
    out = []
    for m in messages:
        content = m.get("content")
        if m.get("role") == "assistant" and isinstance(content, list):
            kept = [b for b in content if getattr(b, "type", None) not in
                    ("thinking", "redacted_thinking")]
            if not kept:
                continue  # an assistant turn that was thinking-only — drop it
            out.append({"role": "assistant", "content": kept})
        else:
            out.append(m)
    return out


class AnthropicModel(ClassifierModel):
    def __init__(
        self,
        name: str = "claude-opus-4-8",
        model_id: str = DEFAULT_MODEL,
        *,
        effort: Optional[str] = "high",
        max_tokens: int = 4096,
        thinking_mode: str = "adaptive",
        thinking_budget: int = 4096,
        thinking: Optional[bool] = None,
        **kwargs,
    ):
        """Adapter for one Claude generation.

        ``thinking_mode`` selects the reasoning surface so a single adapter can drive
        models from different generations (their reasoning APIs diverge):
          * ``"adaptive"`` — ``thinking={"type": "adaptive"}`` (Opus 4.6+, Sonnet 4.6).
          * ``"extended"`` — ``thinking={"type": "enabled", "budget_tokens": N}`` for
            Claude-4-era models (Opus 4.1, 4.5) that predate adaptive thinking and 400
            on it. ``thinking_budget`` must be < ``max_tokens``.
          * ``"off"``      — no thinking block.
        ``effort`` is passed in ``output_config`` only when not ``None`` — Opus 4.1 has
        no effort parameter and 400s if it's sent. ``thinking=False`` is accepted as a
        back-compat alias for ``thinking_mode="off"``.
        """
        super().__init__(name, model_id, **kwargs)
        if thinking is False:
            thinking_mode = "off"
        self.effort = effort
        self.max_tokens = max_tokens
        self.thinking_mode = thinking_mode
        self.thinking_budget = thinking_budget
        self._client = None

    def _thinking_param(self) -> Optional[dict]:
        if self.thinking_mode == "adaptive":
            return {"type": "adaptive"}
        if self.thinking_mode == "extended":
            return {"type": "enabled", "budget_tokens": self.thinking_budget}
        return None  # "off"

    def _output_config(self, *, include_format: bool) -> Optional[dict]:
        """Assemble ``output_config``, omitting ``effort`` when the model lacks it."""
        oc: dict = {}
        if self.effort is not None:
            oc["effort"] = self.effort
        if include_format:
            oc["format"] = {"type": "json_schema", "schema": ANSWER_SCHEMA}
        return oc or None

    @property
    def client(self):
        if self._client is None:
            import anthropic  # imported lazily so the dep is optional per-provider

            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise RuntimeError("ANTHROPIC_API_KEY is not set.")
            self._client = anthropic.Anthropic(api_key=api_key, max_retries=8)
        return self._client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=30))
    def _complete(self, system: str, user: str) -> tuple[str, dict]:
        kwargs = dict(
            model=self.model_id,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_config=self._output_config(include_format=True),
        )
        thinking = self._thinking_param()
        if thinking is not None:
            kwargs["thinking"] = thinking

        resp = self.client.messages.create(**kwargs)
        # With output_config.format, the first text block is schema-valid JSON.
        text = next((b.text for b in resp.content if b.type == "text"), "")
        usage = {
            "input_tokens": resp.usage.input_tokens,
            "output_tokens": resp.usage.output_tokens,
        }
        return text, usage

    # --- Agentic CCL-navigation path -------------------------------------------------
    def classify_agentic(
        self, question: Question, *, toolbox: Optional[CCLToolbox] = None
    ) -> Prediction:
        """Classify by letting the model walk the CCL via tools, then submit an answer.

        Runs a manual tool-use loop: the model calls the navigation tools (executed by
        ``toolbox``) and finishes by calling ``submit_classification``, whose validated
        input is the answer. ``thinking`` blocks are echoed back verbatim each turn (we
        append the whole ``response.content``), as the API requires.
        """
        toolbox = toolbox or CCLToolbox()
        tools = anthropic_tools() + [
            {
                "name": SUBMIT_TOOL_NAME,
                "description": SUBMIT_TOOL_DESCRIPTION,
                "input_schema": submit_tool_input_schema(),
                "strict": True,  # guarantees the submitted answer validates the schema
            }
        ]
        # Agentic turns interleave thinking + several tool calls, so give them more
        # room than a one-shot answer — too small a budget truncates a tool_use block,
        # which then 400s when echoed back. Min 8192.
        max_tokens = max(self.max_tokens, 8192)
        messages = [{"role": "user", "content": build_user_prompt(question)}]
        usage = {"input_tokens": 0, "output_tokens": 0, "steps": 0}

        for _ in range(DEFAULT_MAX_STEPS):
            try:
                resp = self._agentic_turn(tools, messages, max_tokens)
            except Exception:  # noqa: BLE001 - drop to the forced-submit recovery below
                break
            usage["input_tokens"] += resp.usage.input_tokens
            usage["output_tokens"] += resp.usage.output_tokens
            usage["steps"] += 1

            tool_uses = [b for b in resp.content if b.type == "tool_use"]
            submit = next((b for b in tool_uses if b.name == SUBMIT_TOOL_NAME), None)
            if submit is not None:
                return prediction_from_submission(
                    dict(submit.input), usage=usage, tool_trace=toolbox.calls
                )

            # Stop walking and force a submission if the model answered in prose without
            # submitting, or if the turn truncated (a partial tool_use can't be echoed).
            nav = [b for b in tool_uses if b.name != SUBMIT_TOOL_NAME]
            if not nav or resp.stop_reason == "max_tokens":
                break

            # Execute navigation tools and feed all results back in one user turn.
            messages.append({"role": "assistant", "content": resp.content})
            results = [
                {
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": json.dumps(toolbox.call(tu.name, dict(tu.input)),
                                          ensure_ascii=False),
                }
                for tu in nav
            ]
            messages.append({"role": "user", "content": results})

        # The loop ended without a submission (prose answer, truncation, step cap, or a
        # turn error). Force one clean submit from the research so far.
        return self._force_submit(tools, messages, usage, toolbox)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=30))
    def _agentic_turn(self, tools: list, messages: list, max_tokens: int):
        """One Messages API call in the agentic loop (SDK retries 429/5xx internally)."""
        kwargs = dict(
            model=self.model_id,
            max_tokens=max_tokens,
            system=AGENTIC_SYSTEM_PROMPT,
            messages=messages,
            tools=tools,
        )
        oc = self._output_config(include_format=False)
        if oc is not None:
            kwargs["output_config"] = oc
        thinking = self._thinking_param()
        if thinking is not None:
            kwargs["thinking"] = thinking
        return self.client.messages.create(**kwargs)

    def _force_submit(
        self, tools: list, messages: list, usage: dict, toolbox: CCLToolbox
    ) -> Prediction:
        """Force the model to emit a final ``submit_classification`` call.

        Uses ``tool_choice`` to require the submit tool (incompatible with extended
        thinking, so thinking is off here) over the research transcript with thinking
        blocks stripped (the API rejects them when thinking is disabled).
        """
        history = _strip_thinking(messages)
        if history and history[-1]["role"] == "assistant":
            history.append(
                {"role": "user", "content": "Provide your final classification now."}
            )
        # Forced tool_choice is incompatible with thinking, so thinking is already off
        # here; only effort (when the model supports it) rides in output_config.
        fkwargs = dict(
            model=self.model_id,
            max_tokens=2048,
            system=AGENTIC_SYSTEM_PROMPT,
            messages=history,
            tools=tools,
            tool_choice={"type": "tool", "name": SUBMIT_TOOL_NAME},
        )
        oc = self._output_config(include_format=False)
        if oc is not None:
            fkwargs["output_config"] = oc
        try:
            resp = self.client.messages.create(**fkwargs)
            usage["input_tokens"] += resp.usage.input_tokens
            usage["output_tokens"] += resp.usage.output_tokens
            usage["steps"] += 1
            submit = next(
                (b for b in resp.content
                 if b.type == "tool_use" and b.name == SUBMIT_TOOL_NAME),
                None,
            )
            if submit is not None:
                return prediction_from_submission(
                    dict(submit.input), usage=usage, tool_trace=toolbox.calls
                )
        except Exception as exc:  # noqa: BLE001 - report rather than crash the run
            return Prediction(
                predicted_eccn="",
                error=f"{type(exc).__name__}: {exc}",
                usage={**usage, "tool_calls": toolbox.calls},
            )
        return Prediction(
            predicted_eccn="",
            error="agentic loop produced no submit_classification call",
            usage={**usage, "tool_calls": toolbox.calls},
        )
