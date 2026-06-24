"""Google (Gemini) adapter.

Uses the ``google-genai`` SDK with JSON response formatting. System instruction and
schema are passed via the generation config.
"""

from __future__ import annotations

import os

from tenacity import retry, stop_after_attempt, wait_exponential

from .base import ClassifierModel
from ..prompts import ANSWER_SCHEMA

DEFAULT_MODEL = "gemini-2.0-flash"


class GeminiModel(ClassifierModel):
    def __init__(
        self,
        name: str = "gemini-2.0-flash",
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
            from google import genai

            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise RuntimeError("GEMINI_API_KEY is not set.")
            self._client = genai.Client(api_key=api_key)
        return self._client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, max=30))
    def _complete(self, system: str, user: str) -> tuple[str, dict]:
        from google.genai import types

        resp = self.client.models.generate_content(
            model=self.model_id,
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
                response_mime_type="application/json",
                response_schema=ANSWER_SCHEMA,
            ),
        )
        text = resp.text or ""
        usage = {}
        if getattr(resp, "usage_metadata", None):
            usage = {
                "input_tokens": resp.usage_metadata.prompt_token_count,
                "output_tokens": resp.usage_metadata.candidates_token_count,
            }
        return text, usage
