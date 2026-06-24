"""Stretch goal: retrieval-augmented classification over the Commerce Control List.

The idea: index the CCL (Supplement No. 1 to Part 774 of the EAR) so that, at
classification time, the most relevant ECCN entries are retrieved and handed to the
model alongside the item description. ``run_eval --rag`` then A/B-tests model accuracy
with vs. without retrieval.

This subpackage is intentionally a thin, swappable scaffold — see ``retriever.py`` and
``build_index.py``. It requires the optional ``rag`` extra (``pip install -e .[rag]``).
"""
