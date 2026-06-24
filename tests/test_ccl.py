"""Tests for the CCL index + navigation tools (the agentic-condition data layer).

These exercise the parsed ``data/ccl/ccl_index.json`` and the toolbox dispatcher. They
need no API key. If the index hasn't been built, they skip rather than fail.
"""

from __future__ import annotations

import pytest

from commoditybench.ccl import CCLIndex
from commoditybench.ccl.index import DEFAULT_INDEX_PATH
from commoditybench.ccl.tools import CCLToolbox, anthropic_tools, openai_tools

pytestmark = pytest.mark.skipif(
    not DEFAULT_INDEX_PATH.exists(),
    reason="CCL index not built (run commoditybench.ccl.parse_ecfr).",
)


@pytest.fixture(scope="module")
def index() -> CCLIndex:
    return CCLIndex.load()


def test_index_loads_all_categories(index: CCLIndex):
    assert len(index) > 500  # the CCL has ~600+ ECCN entries
    cats = {c["category"] for c in index.list_categories()}
    assert cats == set("0123456789")


def test_known_entries_present_and_parsed(index: CCLIndex):
    for head in ["3A001", "3A991", "5A002", "5A992", "5A991", "6A004"]:
        e = index.get(head)
        assert e is not None and e.eccn == head
        assert e.category == head[0] and e.group == head[1]
        assert e.text  # has controlling text


def test_get_tolerates_subparagraphs_and_formatting(index: CCLIndex):
    # A full ECCN with subparagraphs resolves to its head entry.
    assert index.get("3A001.a.5.b.2").eccn == "3A001"
    assert index.get("eccn 5a992.c").eccn == "5A992"


def test_catchalls_flagged(index: CCLIndex):
    # The basket entries models forget are flagged is_catchall.
    assert index.get("5A992").is_catchall
    assert index.get("3A991").is_catchall
    assert index.get("3A001").is_catchall is False


def test_category_outline_groups_and_shows_catchalls(index: CCLIndex):
    outline = index.category_outline("5")
    group_a = {e["eccn"] for e in outline["entries_by_group"]["A"]}
    # Controlled entry and both catch-alls visible together in one outline.
    assert {"5A001", "5A002", "5A991", "5A992"} <= group_a


def test_mass_market_encryption_text_retrievable(index: CCLIndex):
    # The 5A992.c mass-market-encryption rule (biggest error cluster) is in the text.
    text = index.read("5A992")["text"].lower()
    assert "mass market" in text and "encryption" in text


def test_read_missing_eccn_returns_helpful_payload(index: CCLIndex):
    r = index.read("5A993")  # not a real ECCN
    assert r["found"] is False and "message" in r


def test_search_finds_relevant_entries(index: CCLIndex):
    hits = index.search("analog to digital converter sampling rate resolution")
    assert any(h["eccn"].startswith("3A") for h in hits)


def test_tool_specs_well_formed():
    names = {t["name"] for t in anthropic_tools()}
    assert names == {
        "list_ccl_categories",
        "get_category_outline",
        "read_eccn",
        "search_ccl",
    }
    # OpenAI format wraps each in a function envelope with the same names.
    assert {t["function"]["name"] for t in openai_tools()} == names


def test_toolbox_dispatch_and_trace(index: CCLIndex):
    tb = CCLToolbox(index)
    assert len(tb.call("list_ccl_categories")) == 10
    assert tb.call("read_eccn", {"eccn": "3A991"})["found"] is True
    assert tb.call("get_category_outline", {"category": "3"})["category"] == "3"
    assert tb.call("unknown_tool", {})["error"]  # unknown tool -> error payload, no raise
    assert len(tb.calls) == 4  # every call is recorded in the audit trail
