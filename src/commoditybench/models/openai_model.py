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
        base_url: Optional[str] = None,
        api_key_env: str = "OPENAI_API_KEY",
        structured: str = "json_schema",  # "json_schema" | "json_object" | "none"
        extra_body: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(name, model_id, **kwargs)
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.base_url = base_url
        self.api_key_env = api_key_env
        self.extra_body = extra_body  # non-OpenAI sampling params (vLLM: top_k, min_p, ...)
        if structured not in ("json_schema", "json_object", "none"):
            raise ValueError(f"invalid structured mode: {structured!r}")
        self.structured = structured
        self._client = None

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
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        if self.top_p is not None:
            kwargs["top_p"] = self.top_p
        if self.extra_body is not None:
            kwargs["extra_body"] = self.extra_body
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
