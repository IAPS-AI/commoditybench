# CLAUDE.md — working context for CommodityBench

Read this first when starting a session on this repo. It captures current state and how
to continue. (Repo: **IAPS-AI/commoditybench**, private. Maintainer: Maxwell, IAPS.)

## What this is

A benchmark measuring how well LLMs perform **commodity classification** — assigning an
item its correct **Export Control Classification Number (ECCN)** under the US **Commerce
Control List (CCL)**, the task BIS performs. Goal: quantify model capability as input to a
possible IAPS recommendation about whether BIS should use LLMs for this. Stretch goal:
RAG over the CCL, evaluated with vs. without retrieval.

## Status (as of 2026-06-24)

- **Harness: done and tested.** ECCN parsing + graded scoring, 3 provider adapters,
  concurrent eval runner, dataset loader/validator. 25 passing tests.
- **Dataset: 29 candidate questions** in `data/questions.jsonl`, all real products with
  published ECCNs. **Verification is in progress** (see below). 8 distinct ECCNs across
  CCL Categories 3/5/6 + EAR99.
- **Not done:** finishing human sign-off; expanding categories; building the RAG index;
  running any eval. **No accuracy numbers exist yet and none should be cited.**

## Repo map

```
src/commoditybench/
  eccn.py          # ECCN parse/normalize + GRADED scoring (exact/eccn/group/category, EAR99). CORE.
  dataset.py       # pydantic Question schema + JSONL loader (verified_only gate)
  prompts.py       # provider-agnostic prompt + answer JSON schema (+ optional RAG context)
  run_eval.py      # CLI: concurrent eval, scoring, aggregation, results
  models/          # base.py (interface + JSON parse/fallback), {anthropic,openai,gemini}_model.py, registry.py
  rag/             # stretch: CCL retrieval (retriever.py + build_index.py) — index NOT built yet
data/
  questions.jsonl          # the candidate dataset (verify before citing)
  questions.example.jsonl  # synthetic fixtures for smoke-testing only (never a result)
  schema.md                # field schema + sourcing methodology + provenance rules
  verification_worksheet.md# generated; the human verification tracker
  sources/bis-listed-eccn-publishers.md  # BIS list distilled by category = the sourcing plan
ccats-website-table-april-2018.pdf       # the BIS public-classification list (source doc)
human-review-sources/    # purchase invoices used as provenance (committed)
scripts/
  build_dataset.py # validate <file> | template
  make_worksheet.py# regenerate data/verification_worksheet.md from questions.jsonl
tests/             # pytest (eccn scoring + aggregation math)
```

## How to run (Windows; use `py -3.12`)

```bash
py -3.12 -m pytest -q                                          # 25 tests
PYTHONPATH=src py -3.12 scripts/build_dataset.py validate data/questions.jsonl
py -3.12 scripts/make_worksheet.py                            # regen worksheet after dataset edits
# Eval (needs provider SDKs + API keys in .env): pip install -e ".[all]"
PYTHONPATH=src py -3.12 -m commoditybench.run_eval --dataset data/questions.jsonl \
  --models claude-opus-4-8 --verified-only --workers 8
```
Default Anthropic model is `claude-opus-4-8` (adaptive thinking + structured outputs).
Headline accuracy is over ALL questions (errors/unparsed = 0); `--verified-only` is
mandatory for any reported number.

## Provenance rules (NON-NEGOTIABLE — the maintainer enforces these)

1. **A label's `source_url` must DISPLAY the ECCN to a human who opens it.** A value
   scraped from a page's hidden backend field does NOT qualify even if correct. (This
   disqualified Thorlabs — thorlabs.com serves the ECCN via an internal `eccnTL` data
   feed, never rendered on the page.) If the page doesn't show it, cite a document that
   does (e.g. a purchase invoice).
2. **Prefer companies on the BIS public-classification list** (`data/sources/...`). It's a
   BIS-facing benchmark, so BIS-listed self-classifications are more defensible.
3. **Manufacturer beats distributor.** Digi-Key was found WRONG on 2 Microchip parts vs.
   Microchip's own tool — cross-check distributor data against the maker when possible.
4. **`verified: true` is the maintainer's act**, not the assistant's. Agents can confirm a
   value is human-visible + matches, but a human flips the flag.

## Verification state (what's pending)

Run `py -3.12 scripts/make_worksheet.py` then open `data/verification_worksheet.md` — the
table links each item to its source (with the part to search for tool-based sources).

- **2 VERIFIED** (Thorlabs KM100, BB1-E02 — via invoices in `human-review-sources/`).
- **21 confirmed human-visible + value-matched by automated agents, awaiting maintainer
  sign-off:** 9 ADI (Tier A, BIS-listed, `analog.com/.../view-export-classification.html`),
  7 Microchip (Tier B, `microchipdirect.com/exportcontroldata/`), 5 Digi-Key (Tier B).
  Maintainer is spot-checking ~2 per source, then says "confirmed" per source → flip those
  rows to `verified: true`.
- **6 Thorlabs (Tier C):** ECCN not human-visible. Pending the maintainer's decision:
  invoice-verify (the 1550 nm `6A995` lasers are the valuable hard cases), find another
  human-visible source, or drop.

## Immediate next steps (in order)

1. **Apply the maintainer's sign-off**: set `verified: true` on the rows they confirm
   (edit `data/questions.jsonl`; keep notes/source intact), then `make_worksheet.py`.
2. **Resolve the 6 Thorlabs** per the maintainer's choice.
3. **Expand categories** (the empty ones: 0,1,2,7,9) from BIS-listed publishers — see the
   sourcing map. Strong leads: DRS Infrared/Pelco (Cat 6), LND (Cat 0/1), Rockwell Collins
   (Cat 7), SKF (Cat 2), Cisco (Cat 5 — has a public part-lookup tool), LeCroy/Vectron
   (Cat 3). Use the same agent pattern: confirm human-visible ECCN + capture source_url
   + quote; everything starts `verified: false`.
4. **Then** consider: build the RAG index from the eCFR (15 CFR 774 Supp. No. 1; see
   `rag/build_index.py` TODO), and run a first eval.

## Open issues / flags

- **Provider comparability is NOT equalized**: Claude runs with thinking/effort; GPT/Gemini
  at temp=0. Documented in README "Comparability & limitations". Decide before any
  head-to-head ranking.
- **MX10A** (Thorlabs, `5B991`): group-letter (B = test/production equip) looked off for a
  component during review; still unverified/Tier C anyway.
- **Distribution skew**: heavy on Cat 5 + EAR99. Categories 0/1/2/4/7/8/9 thin or empty.

## Environment / tooling

- `gh` authed as `maxwell-k-roberts` with access to `IAPS-AI`. Commit on a branch or main;
  end commit messages with `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
- Python: `py -3.12`. For PDFs use the Read tool; for blocked/JS pages use
  `node C:/Users/maxwe/tools/fetch.mjs "<url>" --wait 6000`.
- Helper from a prior session: `C:/Users/maxwe/tools/mchpeccn.mjs <part>` hits Microchip's
  export-control API (returns ECCN JSON) — useful for cross-checking Microchip parts.
- Manufacturer export endpoints (ADI, Microchip, Thorlabs) are session/XHR-gated; plain
  curl returns empty. Use a headless browser (the fetch.mjs tool) or a research agent.

## Memory

Durable facts are in the session memory dir (`MEMORY.md` index): IAPS org URL, project
overview, BIS index + accuracy caveat, and the dataset provenance rules. They load
automatically; this file is the project-local complement.
