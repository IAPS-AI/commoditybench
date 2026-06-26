"""OpenAI (GPT) adapter.

Uses the Chat Completions API in JSON mode. The model id and any sampling options are
passed through from the registry so new GPT models can be added without code changes.

The same adapter also drives any OpenAI-compatible endpoint (vLLM, SGLang, RunPod public
endpoints, local Ollama): pass ``base_url`` and the env var holding that service's key via
``api_key_env``. Because hosted open-weight endpoints don't all honor strict
``json_schema``, ``structured`` selects how hard we constrain the output — the base
parser's lenient JSON/prose fallback recovers the ECCN either way.
"""

from __future__ import annotations

import json
import os
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_exponential

from .base import ClassifierModel
from ..prompts import ANSWER_SCHEMA

DEFAULT_MODEL = "gpt-4o"


class OpenAIModel(ClassifierModel):
    def __init__(
        self,
        name: str = "gpt-4o",
        model_id: str = DEFAULT_MODEL,
        *,
        max_tokens: int = 4096,
        temperature: float = 0.0,
        top_p: Optional[float] = None,
        reasoning_effort: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key_env: str = "OPENAI_API_KEY",
        structured: str = "json_schema",  # "json_schema" | "json_object" | "none"
        extra_body: Optional[dict] = None,
        **kwargs,
    ):
        """OpenAI / OpenAI-compatible adapter.

        ``reasoning_effort`` (``"minimal"|"low"|"medium"|"high"``) selects a reasoning
        model (GPT-5 / o-series). When set, the call switches to that family's required
        param surface — ``max_completion_tokens`` instead of ``max_tokens``, the
        ``reasoning_effort`` knob, and NO ``temperature``/``top_p`` (those 400 on
        reasoning models). When ``None`` the adapter behaves as before (chat models like
        GPT-4o and most open-weight endpoints) with ``max_tokens`` + temperature/top_p.
        """
        super().__init__(name, model_id, **kwargs)
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.reasoning_effort = reasoning_effort
        self.base_url = base_url
        self.api_key_env = api_key_env
        self.extra_body = extra_body  # non-OpenAI sampling params (vLLM: top_k, min_p, ...)
        if structured not in ("json_schema", "json_object", "none"):
            raise ValueError(f"invalid structured mode: {structured!r}")
        self.structured = structured
        self._client = None

    def _token_sampling_kwargs(self, *, min_tokens: int = 0) -> dict:
        """Token-budget + sampling params, branched on reasoning vs chat models.

        Reasoning models (``reasoning_effort`` set) require ``max_completion_tokens`` and
        reject ``temperature``/``top_p``; chat models use ``max_tokens`` + sampling. Pass
        ``min_tokens`` to floor the budget (the agentic loop needs more headroom than a
        one-shot answer)."""
        budget = max(self.max_tokens, min_tokens)
        kw: dict = {}
        if self.reasoning_effort is not None:
            kw["max_completion_tokens"] = budget
            kw["reasoning_effort"] = self.reasoning_effort
        else:
            kw["max_tokens"] = budget
            kw["temperature"] = self.temperature
            if self.top_p is not None:
                kw["top_p"] = self.top_p
        if self.extra_body is not None:
            kw["extra_body"] = self.extra_body
        return kw

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI

            api_key = os.environ.get(self.api_key_env)
            if not api_key:
                raise RuntimeError(f"{self.api_key_env} is not set.")
            self._client = OpenAI(
                api_key=api_key, base_url=self.base_url, max_retries=8
            )
        return self._client

    def _response_format(self) -> Optional[dict]:
        if self.structured == "json_schema":
            return {
                "type": "json_schema",
                "json_schema": {
                    "name": "eccn_classification",
                    "schema": ANSWER_SCHEMA,
                    "strict": True,
                },
            }
        if self.structured == "json_object":
            return {"type": "json_object"}
        return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=30))
    def _complete(self, system: str, user: str) -> tuple[str, dict]:
        kwargs = dict(
            model=self.model_id,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            **self._token_sampling_kwargs(),
        )
        fmt = self._response_format()
        if fmt is not None:
            kwargs["response_format"] = fmt
        resp = self.client.chat.completions.create(**kwargs)
        msg = resp.choices[0].message
        text = msg.content or ""
        # Some OpenAI-compatible servers (vLLM with a reasoning parser) route the whole
        # generation into reasoning_content and leave content empty; fall back to it so
        # the answer JSON isn't lost. The base parser strips the trace either way.
        if not text:
            text = getattr(msg, "reasoning_content", None) or getattr(
                msg, "reasoning", ""
            ) or ""
        usage = {}
        if resp.usage:
            usage = {
                "input_tokens": resp.usage.prompt_tokens,
                "output_tokens": resp.usage.completion_tokens,
            }
        # Normalize to a plain JSON string for the base parser.
        try:
            return json.dumps(json.loads(text)), usage
        except (json.JSONDecodeError, ValueError):
            return text, usage

    # --- Agentic CCL-navigation path -------------------------------------------------
    def classify_agentic(self, question, *, toolbox=None):
        """Classify by letting the model walk the CCL via tools, then submit an answer.

        The OpenAI / OpenAI-compatible counterpart of ``AnthropicModel.classify_agentic``:
        the model calls the CCL navigation tools (executed by ``toolbox``) and finishes by
        calling ``submit_classification``, whose validated arguments are the answer.

        Two transports, because OpenAI blocks *function tools + reasoning_effort* on Chat
        Completions for the GPT-5 reasoning models (400: "use /v1/responses instead"):
          * Reasoning OpenAI models (``reasoning_effort`` set, no custom ``base_url``) ->
            the **Responses API**, chaining turns via ``previous_response_id`` so the
            server preserves reasoning state across tool calls.
          * Everything else (non-reasoning chat models like GPT-4o, and OpenAI-compatible
            vLLM/RunPod endpoints — verified on the public Qwen3 endpoint) -> the **Chat
            Completions** tool loop.
        """
        if self.reasoning_effort is not None and self.base_url is None:
            return self._classify_agentic_responses(question, toolbox)
        return self._classify_agentic_chat(question, toolbox)

    def _classify_agentic_chat(self, question, toolbox):
        """Agentic loop over the Chat Completions tool-calling interface."""
        from .agentic import (
            AGENTIC_SYSTEM_PROMPT,
            DEFAULT_MAX_STEPS,
            SUBMIT_TOOL_DESCRIPTION,
            SUBMIT_TOOL_NAME,
            prediction_from_submission,
            submit_tool_input_schema,
        )
        from ..ccl.tools import CCLToolbox, openai_tools
        from ..prompts import build_user_prompt

        toolbox = toolbox or CCLToolbox()
        tools = openai_tools() + [
            {
                "type": "function",
                "function": {
                    "name": SUBMIT_TOOL_NAME,
                    "description": SUBMIT_TOOL_DESCRIPTION,
                    "parameters": submit_tool_input_schema(),
                    "strict": True,
                },
            }
        ]
        messages = [
            {"role": "system", "content": AGENTIC_SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(question)},
        ]
        usage = {"input_tokens": 0, "output_tokens": 0, "steps": 0}
        # Agentic turns interleave reasoning + several tool calls; give them more room
        # than a one-shot answer (min 8192) so a turn isn't truncated mid-tool-call.
        sampling = self._token_sampling_kwargs(min_tokens=8192)

        for _ in range(DEFAULT_MAX_STEPS):
            try:
                resp = self._agentic_turn(tools, messages, sampling)
            except Exception:  # noqa: BLE001 - drop to forced-submit recovery below
                break
            if resp.usage:
                usage["input_tokens"] += resp.usage.prompt_tokens or 0
                usage["output_tokens"] += resp.usage.completion_tokens or 0
            usage["steps"] += 1

            choice = resp.choices[0]
            msg = choice.message
            tool_calls = list(msg.tool_calls or [])
            submit = next(
                (tc for tc in tool_calls if tc.function.name == SUBMIT_TOOL_NAME), None
            )
            if submit is not None:
                return prediction_from_submission(
                    _safe_json(submit.function.arguments),
                    usage=usage,
                    tool_trace=toolbox.calls,
                )

            nav = [tc for tc in tool_calls if tc.function.name != SUBMIT_TOOL_NAME]
            # Stop and force a submission if the model answered without calling a nav tool
            # or the turn truncated (a half-formed tool_call can't be echoed back).
            if not nav or choice.finish_reason == "length":
                break

            # Echo the assistant tool_calls, then one tool message per call (OpenAI
            # requires a response for EVERY tool_call id before the next turn).
            messages.append(
                {
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in nav
                    ],
                }
            )
            for tc in nav:
                result = toolbox.call(tc.function.name, _safe_json(tc.function.arguments))
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                )

        # Loop ended without a submission (prose answer, truncation, step cap, or error).
        return self._force_submit(tools, messages, usage, toolbox, sampling)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=30))
    def _agentic_turn(self, tools: list, messages: list, sampling: dict):
        """One chat-completions call in the agentic loop (SDK retries 429/5xx)."""
        return self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            **sampling,
        )

    def _force_submit(self, tools, messages, usage, toolbox, sampling):
        """Force a final ``submit_classification`` call over the research so far."""
        from .agentic import SUBMIT_TOOL_NAME, prediction_from_submission
        from .base import Prediction

        history = list(messages)
        # The loop only breaks in states where the last message is a fully-answered
        # tool/user/assistant turn (never a dangling assistant tool_call), so a plain
        # nudge + forced tool_choice is safe.
        history.append(
            {"role": "user", "content": "Provide your final classification now."}
        )
        try:
            resp = self.client.chat.completions.create(
                model=self.model_id,
                messages=history,
                tools=tools,
                tool_choice={"type": "function", "function": {"name": SUBMIT_TOOL_NAME}},
                **sampling,
            )
            if resp.usage:
                usage["input_tokens"] += resp.usage.prompt_tokens or 0
                usage["output_tokens"] += resp.usage.completion_tokens or 0
            usage["steps"] += 1
            tcs = resp.choices[0].message.tool_calls or []
            submit = next(
                (tc for tc in tcs if tc.function.name == SUBMIT_TOOL_NAME), None
            )
            if submit is not None:
                return prediction_from_submission(
                    _safe_json(submit.function.arguments),
                    usage=usage,
                    tool_trace=toolbox.calls,
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

    # --- Responses-API agentic path (GPT-5 reasoning models) -------------------------
    def _responses_tools(self):
        """CCL tools + the submit tool in Responses-API (flat) function format."""
        from .agentic import SUBMIT_TOOL_DESCRIPTION, SUBMIT_TOOL_NAME, submit_tool_input_schema
        from ..ccl.tools import TOOL_SPECS

        tools = [
            {
                "type": "function",
                "name": t.name,
                "description": t.description,
                "parameters": t.input_schema,
                "strict": False,
            }
            for t in TOOL_SPECS
        ]
        tools.append(
            {
                "type": "function",
                "name": SUBMIT_TOOL_NAME,
                "description": SUBMIT_TOOL_DESCRIPTION,
                "parameters": submit_tool_input_schema(),
                "strict": True,
            }
        )
        return tools

    def _classify_agentic_responses(self, question, toolbox):
        """Agentic loop over the Responses API (function tools + reasoning state).

        Chains turns with ``previous_response_id`` so the server keeps the reasoning
        context across tool round-trips; each turn we only send the new
        ``function_call_output`` items.
        """
        from .agentic import (
            AGENTIC_SYSTEM_PROMPT,
            DEFAULT_MAX_STEPS,
            SUBMIT_TOOL_NAME,
            prediction_from_submission,
        )
        from ..ccl.tools import CCLToolbox
        from ..prompts import build_user_prompt

        toolbox = toolbox or CCLToolbox()
        tools = self._responses_tools()
        max_output_tokens = max(self.max_tokens, 16384)
        usage = {"input_tokens": 0, "output_tokens": 0, "steps": 0}
        # First turn carries the system prompt (instructions) + the question. Keep the
        # question message so a forced submit can re-send it if the first turn fails before
        # a response exists to chain from (previous_response_id would be None).
        user_msg = {"role": "user", "content": build_user_prompt(question)}
        next_input = [user_msg]
        prev_id = None
        # Tool outputs owed to the model for the latest response's function calls. They
        # are normally consumed by the next turn; if the loop instead exits on the step
        # cap, they must still be sent to the forced submit, or the Responses API 400s
        # ("No tool output found for function call ...").
        pending_outputs: list = []

        for _ in range(DEFAULT_MAX_STEPS):
            try:
                resp = self._responses_turn(tools, next_input, prev_id, max_output_tokens,
                                            AGENTIC_SYSTEM_PROMPT)
            except Exception:  # noqa: BLE001 - drop to forced-submit recovery
                break
            if resp.usage:
                usage["input_tokens"] += resp.usage.input_tokens or 0
                usage["output_tokens"] += resp.usage.output_tokens or 0
            usage["steps"] += 1
            prev_id = resp.id
            pending_outputs = []  # this response's calls are now the owed outputs

            calls = [it for it in resp.output if getattr(it, "type", None) == "function_call"]
            submit = next((c for c in calls if c.name == SUBMIT_TOOL_NAME), None)
            if submit is not None:
                return prediction_from_submission(
                    _safe_json(submit.arguments), usage=usage, tool_trace=toolbox.calls
                )

            nav = [c for c in calls if c.name != SUBMIT_TOOL_NAME]
            # Answer the nav calls now; their outputs are owed to prev_id. If the loop
            # continues, the next turn consumes them; if it breaks here (step cap OR an
            # incomplete/truncated turn that still emitted calls), they ride into the
            # forced submit, so the chained response never has an unanswered call (400).
            if nav:
                next_input = [
                    {
                        "type": "function_call_output",
                        "call_id": c.call_id,
                        "output": json.dumps(toolbox.call(c.name, _safe_json(c.arguments)),
                                             ensure_ascii=False),
                    }
                    for c in nav
                ]
                pending_outputs = next_input
            if not nav or resp.status == "incomplete":
                break

        return self._force_submit_responses(
            tools, prev_id, usage, toolbox, pending_outputs, user_msg
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=30))
    def _responses_turn(self, tools, input_items, prev_id, max_output_tokens, instructions):
        """One Responses-API call in the agentic loop (SDK retries 429/5xx)."""
        kwargs = dict(
            model=self.model_id,
            input=input_items,
            tools=tools,
            tool_choice="auto",
            reasoning={"effort": self.reasoning_effort},
            max_output_tokens=max_output_tokens,
        )
        if prev_id is None:
            kwargs["instructions"] = instructions  # system prompt on the first turn
        else:
            kwargs["previous_response_id"] = prev_id
        return self.client.responses.create(**kwargs)

    def _force_submit_responses(self, tools, prev_id, usage, toolbox,
                                pending_outputs=None, user_msg=None):
        """Force a final ``submit_classification`` call via the Responses API.

        ``pending_outputs`` are any tool outputs owed to ``prev_id``'s function calls (step
        cap or a truncated turn); they must precede the nudge so the chained response is
        valid. ``user_msg`` is the original item prompt — re-sent when there is no prior
        response to chain from (``prev_id is None``, e.g. the first turn errored), so the
        model isn't asked to classify a question it was never shown."""
        from .agentic import AGENTIC_SYSTEM_PROMPT, SUBMIT_TOOL_NAME, prediction_from_submission
        from .base import Prediction

        nudge = {"role": "user", "content": "Provide your final classification now."}
        kwargs = dict(
            model=self.model_id,
            tools=tools,
            tool_choice={"type": "function", "name": SUBMIT_TOOL_NAME},
            reasoning={"effort": self.reasoning_effort},
            max_output_tokens=max(self.max_tokens, 16384),
        )
        if prev_id is None:
            # No conversation to chain from: re-send the system prompt AND the item, or the
            # model classifies blind. pending_outputs is empty in this case (no calls yet).
            kwargs["instructions"] = AGENTIC_SYSTEM_PROMPT
            kwargs["input"] = ([user_msg] if user_msg else []) + [nudge]
        else:
            kwargs["previous_response_id"] = prev_id
            kwargs["input"] = (pending_outputs or []) + [nudge]
        try:
            resp = self.client.responses.create(**kwargs)
            if resp.usage:
                usage["input_tokens"] += resp.usage.input_tokens or 0
                usage["output_tokens"] += resp.usage.output_tokens or 0
            usage["steps"] += 1
            submit = next(
                (it for it in resp.output
                 if getattr(it, "type", None) == "function_call" and it.name == SUBMIT_TOOL_NAME),
                None,
            )
            if submit is not None:
                return prediction_from_submission(
                    _safe_json(submit.arguments), usage=usage, tool_trace=toolbox.calls
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


def _safe_json(raw: str) -> dict:
    """Parse a tool-call arguments string; never raise (a bad arg string -> {})."""
    try:
        val = json.loads(raw or "{}")
        return val if isinstance(val, dict) else {}
    except (json.JSONDecodeError, ValueError, TypeError):
        return {}
