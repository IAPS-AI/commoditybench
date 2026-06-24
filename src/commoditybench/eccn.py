"""Parsing, normalization, and graded scoring of Export Control Classification Numbers.

An ECCN under the US Commerce Control List (CCL, Supplement No. 1 to Part 774 of the
EAR) has the shape ``CGNNN`` plus optional dotted subparagraphs, e.g. ``3A001.a.1.a``:

    - ``C``  : a single-digit **category** (0-9). See ``CATEGORY_NAMES``.
    - ``G``  : a single-letter **product group** (A-E). See ``GROUP_NAMES``.
    - ``NNN``: a three-digit identifier within the category/group.
    - ``.a.1.a`` : optional subparagraph path narrowing the control.

Items that are "subject to the EAR" but not described by any CCL entry are classified
``EAR99`` — a real, common answer that we treat as a first-class label, not a category.

Scoring is **graded** rather than all-or-nothing, because in a real classification
workflow getting the category and product group right (e.g. "this is 3A — Electronics,
systems/equipment") is materially more useful than a random guess even when the exact
subparagraph is wrong. ``score_prediction`` reports each level so analyses can choose
which one to headline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Optional

CATEGORY_NAMES = {
    "0": "Nuclear Materials, Facilities, and Equipment (and Miscellaneous)",
    "1": "Materials, Chemicals, Microorganisms, and Toxins",
    "2": "Materials Processing",
    "3": "Electronics",
    "4": "Computers",
    "5": "Telecommunications (Part 1) and Information Security (Part 2)",
    "6": "Sensors and Lasers",
    "7": "Navigation and Avionics",
    "8": "Marine",
    "9": "Aerospace and Propulsion",
}

GROUP_NAMES = {
    "A": "Systems, Equipment, and Components",
    "B": "Test, Inspection, and Production Equipment",
    "C": "Materials",
    "D": "Software",
    "E": "Technology",
}

# Head of a well-formed ECCN: category digit, group letter, three digits.
_ECCN_HEAD_RE = re.compile(r"^([0-9])([A-E])([0-9]{3})(.*)$")


@dataclass(frozen=True)
class ECCN:
    """A parsed ECCN. ``is_ear99`` items carry no category/group/number."""

    raw: str
    is_ear99: bool = False
    category: Optional[str] = None
    group: Optional[str] = None
    number: Optional[str] = None
    subparagraph: Optional[str] = None  # e.g. "a.1.a", without a leading dot

    @property
    def head(self) -> Optional[str]:
        """The 5-char ``CGNNN`` head (no subparagraph), or None for EAR99/unparsable."""
        if self.is_ear99 or self.category is None:
            return None
        return f"{self.category}{self.group}{self.number}"

    @property
    def is_valid(self) -> bool:
        return self.is_ear99 or self.head is not None

    def __str__(self) -> str:
        if self.is_ear99:
            return "EAR99"
        if self.head is None:
            return self.raw
        return self.head + (f".{self.subparagraph}" if self.subparagraph else "")


def normalize_eccn_text(text: str) -> str:
    """Uppercase, strip, and collapse common punctuation/spacing noise.

    Handles things like ``"3 A 001"``, ``"3a001 .a.1"``, ``"ECCN 5A002"`` and trailing
    periods. Does not validate — that's ``parse``'s job.
    """
    t = text.strip().upper()
    t = re.sub(r"^ECCN[:\s]*", "", t)  # drop a leading "ECCN" label
    t = t.replace(" ", "")
    t = re.sub(r"\.+", ".", t)  # collapse repeated dots
    t = t.strip(".")
    return t


def parse(text: str) -> ECCN:
    """Parse a raw model output or label into an :class:`ECCN`.

    Returns an ECCN with ``is_valid == False`` (no head, not EAR99) when the text does
    not contain a recognizable classification — callers should treat that as "no answer".
    """
    raw = text.strip()
    norm = normalize_eccn_text(raw)

    if norm == "EAR99":
        return ECCN(raw=raw, is_ear99=True)

    m = _ECCN_HEAD_RE.match(norm)
    if not m:
        return ECCN(raw=raw)  # unparsable / no classification found

    category, group, number, rest = m.groups()
    # Canonical ECCN form keeps the head uppercase (3A001) and the subparagraph
    # lowercase (.a.1.a); normalization upper-cased everything, so undo it here.
    subparagraph = rest.strip(".").lower() or None
    return ECCN(
        raw=raw,
        category=category,
        group=group,
        number=number,
        subparagraph=subparagraph,
    )


def extract_eccn(text: str) -> ECCN:
    """Best-effort recovery of an ECCN from a free-text blob.

    Prefer feeding models a structured-output schema so the answer arrives clean. This
    is the fallback for prose like ``"This item is classified under 3A001.a."``. It scans
    for EAR99 first, then the first ``CGNNN`` token (optionally followed by subparagraphs).
    """
    upper = text.upper()
    if re.search(r"\bEAR\s*99\b", upper):
        return ECCN(raw="EAR99", is_ear99=True)

    m = re.search(r"\b([0-9][A-E][0-9]{3}(?:\.[0-9A-Z]+)*)\b", upper)
    if m:
        return parse(m.group(1))
    return ECCN(raw=text.strip())


# --- Scoring -------------------------------------------------------------------------

# Partial-credit weights for the graded score. Exact match earns the full 1.0; coarser
# correct-ness earns progressively less. Tune here if the research design calls for it.
GRADE_WEIGHTS = {
    "exact": 1.0,
    "eccn": 0.7,  # correct CGNNN head, wrong/over-precise subparagraph
    "group": 0.4,  # correct category + product group (e.g. "3A")
    "category": 0.2,  # correct category only (e.g. "3")
    "none": 0.0,
}


@dataclass(frozen=True)
class Score:
    exact_match: bool
    eccn_match: bool  # CGNNN head matches (ignores subparagraph)
    group_match: bool  # category + group match
    category_match: bool  # category matches
    ear99_correct: bool  # both predicted and gold are EAR99
    parsed: bool  # the prediction was a recognizable ECCN/EAR99 at all
    grade: float  # weighted partial credit in [0, 1]
    level: str  # the best level reached: exact|eccn|group|category|none

    def to_dict(self) -> dict:
        return asdict(self)


def score_prediction(predicted: str, gold: str) -> Score:
    """Grade a predicted ECCN string against the gold label.

    EAR99 is handled as its own equivalence class: EAR99-vs-EAR99 is a full exact match;
    EAR99-vs-a-CCL-entry (in either direction) shares no category and scores 0. This is
    deliberate — confusing "not controlled" with a real control number is a serious error.
    """
    p = parse(predicted)
    g = parse(gold)

    # Gold should always be valid; guard anyway so a bad label fails loudly in tests.
    if not g.is_valid:
        raise ValueError(f"Gold label is not a valid ECCN or EAR99: {gold!r}")

    parsed = p.is_valid

    if g.is_ear99 or p.is_ear99:
        exact = p.is_ear99 and g.is_ear99
        return _build_score(
            exact_match=exact,
            eccn_match=exact,
            group_match=exact,
            category_match=exact,
            ear99_correct=exact,
            parsed=parsed,
        )

    exact = str(p) == str(g) and parsed
    eccn = p.head == g.head and p.head is not None
    group = (
        p.category == g.category
        and p.group == g.group
        and p.category is not None
    )
    category = p.category == g.category and p.category is not None

    return _build_score(
        exact_match=exact,
        eccn_match=eccn,
        group_match=group,
        category_match=category,
        ear99_correct=False,
        parsed=parsed,
    )


def _build_score(
    *,
    exact_match: bool,
    eccn_match: bool,
    group_match: bool,
    category_match: bool,
    ear99_correct: bool,
    parsed: bool,
) -> Score:
    if exact_match:
        level = "exact"
    elif eccn_match:
        level = "eccn"
    elif group_match:
        level = "group"
    elif category_match:
        level = "category"
    else:
        level = "none"
    return Score(
        exact_match=exact_match,
        eccn_match=eccn_match,
        group_match=group_match,
        category_match=category_match,
        ear99_correct=ear99_correct,
        parsed=parsed,
        grade=GRADE_WEIGHTS[level],
        level=level,
    )
