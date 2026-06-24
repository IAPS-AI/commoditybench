"""OpenAI (GPT) adapter.

Uses the Chat Completions API in JSON mode. The model id and any sampling options are
passed through from the registry so new GPT models can be added without code changes.
"""

from __future__ import annotations

import json
import os

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
        **kwargs,
    ):
        super().__init__(name, model_id, **kwargs)
        self.max_tokens = max_tokens
        self.temperature = temperature
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI

            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY is not set.")
            self._client = OpenAI(api_key=api_key, max_retries=8)
        return self._client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=30))
    def _complete(self, system: str, user: str) -> tuple[str, dict]:
        resp = self.client.chat.completions.create(
            model=self.model_id,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "eccn_classification",
                    "schema": ANSWER_SCHEMA,
                    "strict": True,
                },
            },
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        text = resp.choices[0].message.content or ""
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
