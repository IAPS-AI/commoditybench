"""A small registry mapping friendly names to configured model adapters.

The CLI accepts these names with ``--models``. Add an entry here to enroll a new model
in the benchmark; no other code needs to change. Model ids are the provider's current
strings — update them as providers ship new versions.
"""

from __future__ import annotations

from typing import Callable

from .base import ClassifierModel


def _anthropic(model_id: str, **kw) -> Callable[[], ClassifierModel]:
    from .anthropic_model import AnthropicModel

    return lambda name: AnthropicModel(name=name, model_id=model_id, **kw)


def _openai(model_id: str, **kw) -> Callable[[], ClassifierModel]:
    from .openai_model import OpenAIModel

    return lambda name: OpenAIModel(name=name, model_id=model_id, **kw)


def _gemini(model_id: str, **kw) -> Callable[[], ClassifierModel]:
    from .gemini_model import GeminiModel

    return lambda name: GeminiModel(name=name, model_id=model_id, **kw)


# name -> factory(name) -> ClassifierModel. Edit ids here as providers update models.
_REGISTRY: dict[str, Callable[[str], ClassifierModel]] = {
    # --- Anthropic (Claude) ---
    "claude-opus-4-8": _anthropic("claude-opus-4-8"),
    "claude-sonnet-4-6": _anthropic("claude-sonnet-4-6"),
    # --- OpenAI (GPT) ---
    "gpt-4o": _openai("gpt-4o"),
    "gpt-4o-mini": _openai("gpt-4o-mini"),
    # --- Google (Gemini) ---
    "gemini-2.0-flash": _gemini("gemini-2.0-flash"),
    "gemini-1.5-pro": _gemini("gemini-1.5-pro"),
    # --- Open weights via RunPod public endpoints (OpenAI-compatible) ---
    # RunPod's hosted LLM menu is small; Qwen3-32B is the strongest text model.
    # Run in thinking mode with the sampling settings the Qwen3 model card requires
    # (temp 0.6 / top_p 0.95 / top_k 20); greedy decoding is explicitly discouraged in
    # thinking mode (repetition/degradation). Thinking is on by default, so the response
    # carries a <think> trace and json_schema can't be enforced -> structured="none";
    # the base parser strips the trace and recovers the answer JSON. Budget is large
    # enough for the trace plus the answer.
    "qwen3-32b": _openai(
        "Qwen/Qwen3-32B-AWQ",
        base_url="https://api.runpod.ai/v2/qwen3-32b-awq/openai/v1",
        api_key_env="RUNPOD_API_KEY",
        structured="none",
        temperature=0.6,
        top_p=0.95,
        max_tokens=16384,
        extra_body={"top_k": 20, "min_p": 0},
    ),
}


def available_models() -> list[str]:
    return sorted(_REGISTRY)


def build_model(name: str) -> ClassifierModel:
    if name not in _REGISTRY:
        raise KeyError(
            f"Unknown model {name!r}. Available: {', '.join(available_models())}"
        )
    return _REGISTRY[name](name)
