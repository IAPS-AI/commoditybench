"""Tests for the shared answer parser, including reasoning-model output handling."""

from commoditybench.models.base import ClassifierModel, _strip_reasoning


def test_strip_reasoning_removes_think_block():
    text = '<think>Maybe {3A001}? No.</think>\n{"eccn": "EAR99"}'
    assert _strip_reasoning(text) == '{"eccn": "EAR99"}'


def test_strip_reasoning_handles_unopened_closing_tag():
    # vLLM reasoning parsers sometimes emit the trace then a bare closing tag.
    text = 'reasoning about 5A002 then concluding</think>{"eccn": "EAR99"}'
    assert _strip_reasoning(text) == '{"eccn": "EAR99"}'


def test_strip_reasoning_leaves_plain_text_untouched():
    text = '{"eccn": "EAR99"}'
    assert _strip_reasoning(text) == text


def test_parse_recovers_answer_after_reasoning_with_rejected_eccns():
    # The trace mentions 3A001 (considered, rejected); the real answer is EAR99.
    # Stripping the trace must prevent the fallback from scraping 3A001.
    text = (
        '<think>Could be 3A001.a.5 given the converter... actually the speed is too '
        'low, so it is not listed.</think>\n'
        '{"eccn": "EAR99", "category": "EAR99", "reasoning": "below thresholds"}'
    )
    pred = ClassifierModel._parse(text, usage={})
    assert pred.predicted_eccn == "EAR99"
    assert pred.parsed_ok is True


def test_parse_fallback_extracts_eccn_from_prose():
    # No JSON, but a clear ECCN in prose -> recovered via fallback, parsed_ok False.
    pred = ClassifierModel._parse("The classification is 3A001.a.1.a here.", usage={})
    assert pred.predicted_eccn == "3A001.a.1.a"
    assert pred.parsed_ok is False
