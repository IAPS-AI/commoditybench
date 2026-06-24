"""Tests for ECCN parsing, normalization, and graded scoring."""

import pytest

from commoditybench.eccn import (
    parse,
    extract_eccn,
    normalize_eccn_text,
    score_prediction,
)


# --- parsing -------------------------------------------------------------------------

def test_parse_full_eccn():
    e = parse("3A001.a.1.a")
    assert (e.category, e.group, e.number, e.subparagraph) == ("3", "A", "001", "a.1.a")
    assert e.head == "3A001"
    assert str(e) == "3A001.a.1.a"
    assert e.is_valid


def test_parse_head_only():
    e = parse("5A002")
    assert e.head == "5A002"
    assert e.subparagraph is None
    assert str(e) == "5A002"


def test_parse_ear99_variants():
    # All of these must parse to EAR99 through `parse` itself, incl. the hyphenated form.
    for text in ["EAR99", "ear99", " EAR 99 ", "EAR-99", "ECCN: EAR99"]:
        assert parse(text).is_ear99


@pytest.mark.parametrize("dirty,clean", [
    ("ECCN 3A001", "3A001"),
    ("3 A 001 . a", "3A001.A"),
    ("3a001.", "3A001"),
    ("5A002.a.1..b", "5A002.A.1.B"),
])
def test_normalize(dirty, clean):
    assert normalize_eccn_text(dirty) == clean


def test_parse_unparsable():
    e = parse("I am not sure")
    assert not e.is_valid
    assert e.head is None


def test_extract_from_prose():
    e = extract_eccn("Based on the specs, this falls under 3A001.a and is controlled.")
    assert e.head == "3A001"
    assert e.subparagraph == "a"


def test_extract_ear99_from_prose():
    assert extract_eccn("This is a consumer item, so EAR99 applies.").is_ear99


# --- scoring -------------------------------------------------------------------------

def test_exact_match():
    s = score_prediction("3A001.a.1.a", "3A001.a.1.a")
    assert s.exact_match and s.eccn_match and s.group_match and s.category_match
    assert s.level == "exact" and s.grade == 1.0


def test_subparagraph_wrong_but_head_right():
    s = score_prediction("3A001.b", "3A001.a.1.a")
    assert not s.exact_match
    assert s.eccn_match and s.group_match and s.category_match
    assert s.level == "eccn" and s.grade == 0.7


def test_group_match_only():
    s = score_prediction("3A002", "3A001")
    assert not s.eccn_match and s.group_match and s.category_match
    assert s.level == "group" and s.grade == 0.4


def test_category_match_only():
    s = score_prediction("3B001", "3A001")
    assert not s.group_match and s.category_match
    assert s.level == "category" and s.grade == 0.2


def test_total_miss():
    s = score_prediction("9A001", "3A001")
    assert not s.category_match
    assert s.level == "none" and s.grade == 0.0


def test_ear99_correct():
    s = score_prediction("EAR99", "EAR99")
    assert s.exact_match and s.ear99_correct and s.grade == 1.0


def test_ear99_vs_ccl_is_total_miss():
    # Predicting "not controlled" when it is controlled shares no credit.
    s = score_prediction("EAR99", "3A001.a")
    assert s.grade == 0.0 and s.level == "none"
    s2 = score_prediction("3A001.a", "EAR99")
    assert s2.grade == 0.0 and s2.level == "none"


def test_unparsable_prediction_scores_zero_and_flags():
    s = score_prediction("no idea", "3A001")
    assert not s.parsed
    assert s.grade == 0.0


def test_bad_gold_label_raises():
    with pytest.raises(ValueError):
        score_prediction("3A001", "not-an-eccn")


def test_empty_prediction_scores_zero():
    s = score_prediction("", "3A001")
    assert not s.parsed and s.grade == 0.0 and s.level == "none"


def test_ear99_hyphen_prediction_scores_exact():
    # A model answering "EAR-99" in clean output must match an EAR99 gold.
    s = score_prediction("EAR-99", "EAR99")
    assert s.exact_match and s.ear99_correct
