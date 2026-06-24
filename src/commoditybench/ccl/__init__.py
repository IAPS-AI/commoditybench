"""The Commerce Control List as a navigable structure.

This package turns the eCFR source for the CCL (15 CFR 774, Supplement No. 1) into a
structured, queryable index and exposes it as a set of *tools* a model can call while
classifying — the agentic-navigation condition of the benchmark. The model walks the CCL
the way a human BIS analyst does: pick the category, read its outline (seeing the high-
performance controls and the ``x991``/``x992`` catch-alls side by side), then read the
controlling text of candidate entries to check thresholds before committing to an ECCN.

Layout:
    parse_ecfr.py  -> build data/ccl/ccl_index.json from the eCFR XML
    index.py       -> CCLIndex: load the JSON and answer outline/read/search queries
    tools.py       -> provider-agnostic tool specs + a dispatcher over a CCLIndex
"""

from .index import CCLIndex, CCLEntry, DEFAULT_INDEX_PATH

__all__ = ["CCLIndex", "CCLEntry", "DEFAULT_INDEX_PATH"]
