"""Tests for run_eval._aggregate — the headline-metric math.

The key property: errored and unparseable predictions must count as wrong (denominator =
all n), so two models with different failure rates stay comparable. The reviewer flagged
that the original code divided by the non-errored count, which would let a model that
fails its hardest items score higher.
"""

from commoditybench.eccn import score_prediction
from commoditybench.run_eval import _aggregate


def _row(rid: str, predicted: str, gold: str, error: str | None = None) -> dict:
    score = score_prediction(predicted or "x", gold)  # score is ignored when error set
    return {"id": rid, "gold_eccn": gold, "predicted_eccn": predicted, "error": error,
            "score": score.to_dict()}


def test_errors_count_as_wrong_in_denominator():
    # 2 correct, 2 errored. Headline accuracy must be 2/4 = 0.5, not 2/2 = 1.0.
    rows = [
        _row("a", "3A001", "3A001"),
        _row("b", "5A002", "5A002"),
        _row("c", "", "3A001", error="APITimeoutError"),
        _row("d", "", "5A002", error="RateLimitError"),
    ]
    agg = _aggregate("m", rows)
    assert agg["n"] == 4
    assert agg["attempted"] == 2
    assert agg["errors"] == 2
    assert agg["exact_accuracy"] == 0.5  # over all n
    assert agg["exact_accuracy_attempted"] == 1.0  # over non-errored only (diagnostic)
    assert agg["error_rate"] == 0.5


def test_unparseable_counts_as_wrong_not_excluded():
    # An unparseable-but-returned answer (no error) is a scored 0, included in n.
    rows = [
        _row("a", "3A001", "3A001"),
        {"id": "b", "gold_eccn": "5A002", "predicted_eccn": "", "error": None,
         "score": score_prediction("", "5A002").to_dict()},
    ]
    agg = _aggregate("m", rows)
    assert agg["n"] == 2
    assert agg["errors"] == 0
    assert agg["exact_accuracy"] == 0.5
    assert agg["parse_rate"] == 0.5  # one answer failed to parse


def test_partial_credit_in_mean_grade():
    rows = [
        _row("a", "3A001.a.1.a", "3A001.a.1.a"),  # 1.0
        _row("b", "3A002", "3A001"),  # group match -> 0.4
    ]
    agg = _aggregate("m", rows)
    assert agg["mean_grade"] == 0.7  # (1.0 + 0.4) / 2


def test_all_errors_no_zero_division():
    rows = [_row("a", "", "3A001", error="boom")]
    agg = _aggregate("m", rows)
    assert agg["attempted"] == 0
    assert agg["exact_accuracy"] == 0.0
    assert agg["exact_accuracy_attempted"] == 0.0
