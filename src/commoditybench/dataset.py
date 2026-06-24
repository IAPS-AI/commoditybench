"""Benchmark dataset: the question schema and a JSONL loader.

Each line in a ``.jsonl`` dataset file is one classification question. See
``data/schema.md`` for the full field documentation and the sourcing methodology.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator, Optional

from pydantic import BaseModel, Field


class Question(BaseModel):
    """A single commodity-classification question with a ground-truth ECCN."""

    id: str = Field(..., description="Stable unique id, e.g. 'cisco-c9300-001'.")
    item_name: str = Field(..., description="Short product/commodity name.")
    description: str = Field(
        ...,
        description="The text shown to the model: what the item is, its function and "
        "salient technical specs. This is the classification input.",
    )
    gold_eccn: str = Field(..., description="Ground-truth ECCN or 'EAR99'.")

    manufacturer: Optional[str] = Field(None, description="Vendor, when applicable.")
    source_url: Optional[str] = Field(
        None, description="Where the ground-truth label was published."
    )
    source_type: str = Field(
        "manufacturer_self_classification",
        description="Provenance: manufacturer_self_classification | bis_advisory_opinion "
        "| bis_faq_example | ccats | synthetic_from_ccl | other.",
    )
    verified: bool = Field(
        False,
        description="True only once a human has confirmed the label against its source. "
        "Unverified items MUST NOT be used to report headline accuracy.",
    )
    category: Optional[str] = Field(
        None, description="Single-digit CCL category, for stratified analysis."
    )
    difficulty: Optional[str] = Field(
        None, description="Optional: easy | medium | hard (annotator judgment)."
    )
    notes: Optional[str] = Field(None, description="Free-form annotator notes.")


def load_questions(path: str | Path, *, verified_only: bool = False) -> list[Question]:
    """Load a JSONL dataset file into a list of :class:`Question`.

    Args:
        path: Path to a ``.jsonl`` file (one JSON object per line; blank lines and
            ``#``-prefixed comment lines are skipped).
        verified_only: If True, drop questions whose ``verified`` flag is False. Use this
            when computing headline metrics so unverified placeholders never leak in.
    """
    questions: list[Question] = []
    for line in iter_jsonl(path):
        q = Question.model_validate(line)
        if verified_only and not q.verified:
            continue
        questions.append(q)
    return questions


def iter_jsonl(path: str | Path) -> Iterator[dict]:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            yield json.loads(line)
