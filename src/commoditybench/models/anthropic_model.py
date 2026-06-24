"""Anthropic (Claude) adapter.

Uses the Messages API with native structured outputs (``output_config.format``) so the
answer arrives as schema-valid JSON, and adaptive thinking for the reasoning-heavy
classification task. Defaults to Claude Opus 4.8.
"""

from __future__ import annotations

import os

from tenacity import retry, stop_after_attempt, wait_exponential

from .base import ClassifierModel
from ..prompts import ANSWER_SCHEMA

DEFAULT_MODEL = "claude-opus-4-8"


class AnthropicModel(ClassifierModel):
    def __init__(
        self,
        name: str = "claude-opus-4-8",
        model_id: str = DEFAULT_MODEL,
        *,
        effort: str = "high",
        max_tokens: int = 4096,
        thinking: bool = True,
        **kwargs,
    ):
        super().__init__(name, model_id, **kwargs)
        self.effort = effort
        self.max_tokens = max_tokens
        self.thinking = thinking
        self._client = None

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
            output_config={
                "effort": self.effort,
                "format": {"type": "json_schema", "schema": ANSWER_SCHEMA},
            },
        )
        if self.thinking:
            kwargs["thinking"] = {"type": "adaptive"}

        resp = self.client.messages.create(**kwargs)
        # With output_config.format, the first text block is schema-valid JSON.
        text = next((b.text for b in resp.content if b.type == "text"), "")
        usage = {
            "input_tokens": resp.usage.input_tokens,
            "output_tokens": resp.usage.output_tokens,
        }
        return text, usage
