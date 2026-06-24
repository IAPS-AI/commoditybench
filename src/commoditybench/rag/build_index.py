"""Build a vector index of the Commerce Control List for the RAG condition.

Pipeline (to be fleshed out in phase 2):
    1. Acquire the CCL. The authoritative source is the eCFR — Supplement No. 1 to
       Part 774 of the EAR (15 CFR 774). The eCFR offers a structured API and bulk XML
       (https://www.ecfr.gov/), which is far cleaner to parse than scraped HTML/PDF.
    2. Chunk by ECCN entry (one chunk per ECCN, optionally split long entries by
       subparagraph), keeping the ECCN as metadata so retrieval results are citable.
    3. Embed and persist to a Chroma collection at ``.rag_index/``.

This module currently provides the chunking + indexing skeleton. The CCL acquisition
step is left as the next concrete task — see TODO below.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from .retriever import DEFAULT_COLLECTION, DEFAULT_INDEX_DIR


@dataclass
class CCLChunk:
    eccn: str
    title: str
    text: str


def load_ccl_chunks(source: Path) -> list[CCLChunk]:
    """Parse the CCL into per-ECCN chunks.

    TODO(phase 2): implement parsing of the eCFR XML for 15 CFR 774 Supplement No. 1.
    The eCFR bulk XML marks each ECCN with structured headings, so chunks can be split
    cleanly on ECCN boundaries with the ECCN captured as metadata.
    """
    raise NotImplementedError(
        "CCL acquisition/parsing is the next task. Download 15 CFR 774 Supp. No. 1 "
        "from the eCFR (https://www.ecfr.gov/) and implement per-ECCN chunking here."
    )


def build_index(
    chunks: list[CCLChunk],
    index_dir: str | Path = DEFAULT_INDEX_DIR,
    collection: str = DEFAULT_COLLECTION,
) -> None:
    import chromadb

    client = chromadb.PersistentClient(path=str(index_dir))
    col = client.get_or_create_collection(collection)
    col.add(
        ids=[f"{c.eccn}-{i}" for i, c in enumerate(chunks)],
        documents=[f"{c.title}\n{c.text}" for c in chunks],
        metadatas=[{"eccn": c.eccn, "title": c.title} for c in chunks],
    )
    print(f"Indexed {len(chunks)} CCL chunks into {index_dir}/{collection}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the CCL RAG index.")
    ap.add_argument(
        "--source",
        required=True,
        help="Path to the downloaded CCL (eCFR XML for 15 CFR 774 Supp. No. 1).",
    )
    ap.add_argument("--index-dir", default=DEFAULT_INDEX_DIR)
    args = ap.parse_args()
    chunks = load_ccl_chunks(Path(args.source))
    build_index(chunks, index_dir=args.index_dir)


if __name__ == "__main__":
    main()
