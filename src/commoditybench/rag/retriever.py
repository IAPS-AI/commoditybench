"""Retriever interface for the RAG condition.

``CCLRetriever`` looks up the most relevant CCL chunks for a question and returns them
as a single text block to inject into the prompt. The default implementation reads a
Chroma index built by ``build_index.py``; swap in any vector store or a hybrid keyword
retriever by implementing :meth:`retrieve`.
"""

from __future__ import annotations

from pathlib import Path

from ..dataset import Question

DEFAULT_INDEX_DIR = ".rag_index"
DEFAULT_COLLECTION = "ccl"


class CCLRetriever:
    def __init__(
        self,
        index_dir: str | Path = DEFAULT_INDEX_DIR,
        *,
        collection: str = DEFAULT_COLLECTION,
        top_k: int = 6,
    ):
        self.index_dir = Path(index_dir)
        self.collection_name = collection
        self.top_k = top_k
        self._collection = None

    @property
    def collection(self):
        if self._collection is None:
            import chromadb

            if not self.index_dir.exists():
                raise RuntimeError(
                    f"No CCL index at {self.index_dir}. Build one first: "
                    "`python -m commoditybench.rag.build_index`."
                )
            client = chromadb.PersistentClient(path=str(self.index_dir))
            self._collection = client.get_collection(self.collection_name)
        return self._collection

    def retrieve(self, question: Question) -> str:
        """Return a newline-joined block of the top-k most relevant CCL excerpts."""
        query = f"{question.item_name}. {question.description}"
        res = self.collection.query(query_texts=[query], n_results=self.top_k)
        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        chunks = []
        for doc, meta in zip(docs, metas):
            eccn = (meta or {}).get("eccn", "")
            header = f"[{eccn}] " if eccn else ""
            chunks.append(f"{header}{doc}")
        return "\n\n".join(chunks)
