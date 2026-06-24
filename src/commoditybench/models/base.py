"""Common interface every provider adapter implements."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from ..eccn import extract_eccn
from ..prompts import SYSTEM_PROMPT, build_user_prompt
from ..dataset import Question


@dataclass
class Prediction:
    """A model's answer for one question, plus what we needed to score and audit it."""

    predicted_eccn: str
    reasoning: str = ""
    raw_response: str = ""
    parsed_ok: bool = True  # whether the JSON parsed cleanly (vs. fallback extraction)
    error: Optional[str] = None  # set if the call failed; predicted_eccn will be ""
    usage: dict = field(default_factory=dict)


class ClassifierModel(ABC):
    """A provider/model the benchmark can call.

    Subclasses implement :meth:`_complete`, returning the raw assistant text (expected to
    be the JSON object described in ``prompts.ANSWER_SCHEMA``). The base class handles
    prompt assembly, JSON parsing, and the ECCN-extraction fallback so every provider is
    scored identically.
    """

    #: A short, stable identifier used in result filenames and tables.
    name: str

    def __init__(self, name: str, model_id: str, **kwargs):
        self.name = name
        self.model_id = model_id
        self.options = kwargs

    @abstractmethod
    def _complete(self, system: str, user: str) -> tuple[str, dict]:
        """Return ``(assistant_text, usage_dict)`` for the given prompts."""

    def classify(self, question: Question, context: Optional[str] = None) -> Prediction:
        """Classify a question. ``context`` injects retrieved CCL excerpts (RAG mode)."""
        user = build_user_prompt(question, context=context)
        try:
            text, usage = self._complete(SYSTEM_PROMPT, user)
        except Exception as exc:  # noqa: BLE001 - surface any provider error per-item
            return Prediction(
                predicted_eccn="", raw_response="", error=f"{type(exc).__name__}: {exc}"
            )
        return self._parse(text, usage)

    @staticmethod
    def _parse(text: str, usage: dict) -> Prediction:
        """Parse the assistant text into a :class:`Prediction`.

        Strips any reasoning trace first (so a thinking model's discarded
        intermediate ECCNs can't pollute extraction), then tries strict JSON, then a
        lenient ``{...}`` slice, then falls back to scanning free text for an ECCN so a
        chatty model still gets scored.
        """
        text = _strip_reasoning(text)
        obj = _try_json(text)
        if obj is not None and isinstance(obj.get("eccn"), str):
            return Prediction(
                predicted_eccn=obj["eccn"].strip(),
                reasoning=str(obj.get("reasoning", "")),
                raw_response=text,
                parsed_ok=True,
                usage=usage,
            )
        # Fallback: recover an ECCN from prose.
        recovered = extract_eccn(text)
        return Prediction(
            predicted_eccn=str(recovered) if recovered.is_valid else "",
            reasoning="",
            raw_response=text,
            parsed_ok=False,
            usage=usage,
        )


def _strip_reasoning(text: str) -> str:
    """Drop a reasoning model's chain-of-thought before parsing.

    Hybrid reasoning models (e.g. Qwen3 via vLLM) prepend a ``<think>...</think>``
    trace to the answer in the ``content`` field. That trace routinely contains braces
    and candidate ECCNs the model ultimately rejects, which would corrupt both the JSON
    slice and the prose fallback. The final answer is whatever follows the last closing
    tag; if the trace is unclosed (truncated), leave the text alone for the fallback.
    """
    if "</think>" in text:
        return text.rsplit("</think>", 1)[-1].strip()
    return text


def _try_json(text: str) -> Optional[dict]:
    text = text.strip()
    # Strip a markdown code fence if present.
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        pass
    # Lenient: grab the first {...} span.
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except (json.JSONDecodeError, ValueError):
            return None
    return None
