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

- **Harness: done and tested.** ECCN parsing + graded scoring, provider adapters,
  concurrent eval runner, dataset loader/validator. **40 passing tests.** Tagged **`v1.0`**.
- **Dataset: 34 questions** in `data/questions.jsonl` = **23 verified** (round-1, signed
  off) + **11 new candidates** (`verified: false`) added this session to fill empty
  categories. Spans CCL Categories **1/2/3/5/7/9 + EAR99**. (See verification state below.)
- **Open-weight track added.** The OpenAI adapter now drives ANY OpenAI-compatible
  endpoint via `base_url` + `api_key_env` + a `structured` mode (`json_schema|json_object|
  none`) + `top_p`/`extra_body` passthrough. `qwen3-32b` runs on **RunPod public
  endpoints** in thinking mode (temp 0.6 / top_p 0.95 / top_k 20, 16k budget;
  `RUNPOD_API_KEY`). The shared parser (`models/base.py`) now strips `<think>…</think>`
  before extraction and falls back to `reasoning_content` when `content` is empty, so a
  reasoning model is scored on its answer, not plumbing.
- **First multi-model comparison run done** (run-id `comparison`, 23 verified Qs, no
  tools, all 100% parse / 0 errors): **claude-opus-4-8** exact 0.26 / grade 0.44 ·
  **gpt-4o** 0.17 / 0.37 · **qwen3-32b** 0.04 / 0.16. NOT equalized (Claude/Qwen3 reason,
  GPT-4o at temp 0) — a capability snapshot, not a controlled ranking. Models over-classify
  (reach for controlled ECCNs on EAR99 items) and anchor on 3A001.
- **Dashboard microsite:** `dashboard/index.html` (self-contained, data embedded, offline;
  ranked leaderboard + per-model drill-down + grade ladder + computed insights). Regenerate
  with `scripts/build_dashboard.py --summary results/<run>__summary.json`.
- **Agentic CCL-navigation tooling: built + tested.** `commoditybench/ccl/` parses the
  CCL from the eCFR into a navigable index and exposes it as tools the model calls
  (`--agentic`). First within-model A/B on Claude Opus 4.8 (23 verified Qs) shows a large
  lift from tools — exact 0.30→0.52, mean grade 0.45→0.60. See
  `results/agentic_ab_findings.md` for the per-pattern breakdown (tools fix *recall*
  failures like the 3A991/EAR99 catch-alls; they don't fix the *judgment* call of 5A002
  vs. mass-market 5A992.c). Two loop-robustness bugs were found and fixed post-run; the
  confirming re-run is **now unblocked** — Anthropic + OpenAI keys are in `.env` and verified
  working this session.
- **Not done:** sign-off on the 11 new candidates; Cat **0/4/6/8 still empty** (cutting the
  non-visible Thorlabs lasers this session emptied Cat 6); equalized comparison; RAG index.
  All cited accuracy is over the 23-verified set; keep the not-equalized / A-B-tool-lift
  framing when citing.

## Repo map

```
src/commoditybench/
  eccn.py          # ECCN parse/normalize + GRADED scoring (exact/eccn/group/category, EAR99). CORE.
  dataset.py       # pydantic Question schema + JSONL loader (verified_only gate)
  prompts.py       # provider-agnostic prompt + answer JSON schema (+ optional RAG context)
  run_eval.py      # CLI: concurrent eval, scoring, aggregation, results
  models/          # base.py (interface + JSON parse/fallback + <think>-strip), registry.py,
                   #   {anthropic,openai,gemini}_model.py — openai_model.py also drives any
                   #   OpenAI-compatible endpoint (RunPod/vLLM/Ollama): qwen3-32b is registered there
  ccl/             # AGENTIC condition: parsed CCL + navigation tools the model calls
                   #   parse_ecfr.py (eCFR XML -> ccl_index.json), index.py (CCLIndex:
                   #   category_outline/read/search), tools.py (tool specs + CCLToolbox)
  rag/             # stretch: CCL retrieval (retriever.py + build_index.py) — index NOT built yet
data/
  ccl/ccl_index.json       # parsed CCL (637 ECCN entries) for the agentic tools; committed
  ccl/ccl_supp1.xml        # raw eCFR source for the index (reproducibility)
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
  build_dashboard.py + dashboard_template.html  # generate the results microsite
dashboard/index.html     # generated results dashboard (committed; embeds the run's data)
tests/             # pytest (eccn scoring + aggregation math + parser/<think>-strip)
```

## How to run (Windows; use `py -3.12`)

```bash
py -3.12 -m pytest -q                                          # 40 tests
PYTHONPATH=src py -3.12 scripts/build_dataset.py validate data/questions.jsonl
py -3.12 scripts/make_worksheet.py                            # regen worksheet after dataset edits
# Eval (needs provider SDKs + API keys in .env): pip install -e ".[all]"
PYTHONPATH=src py -3.12 -m commoditybench.run_eval --dataset data/questions.jsonl \
  --models claude-opus-4-8 --verified-only --workers 8
# Multi-model comparison (incl. open-weight Qwen3-32B on RunPod; needs RUNPOD_API_KEY):
PYTHONPATH=src py -3.12 -m commoditybench.run_eval --dataset data/questions.jsonl \
  --models claude-opus-4-8 gpt-4o qwen3-32b --verified-only --workers 8 --run-id comparison
PYTHONPATH=src py -3.12 scripts/build_dashboard.py --summary results/comparison__summary.json
# AGENTIC condition (Claude only): model navigates the CCL via tools before answering.
PYTHONPATH=src py -3.12 -m commoditybench.run_eval --dataset data/questions.jsonl \
  --models claude-opus-4-8 --verified-only --agentic --workers 4
# Rebuild the CCL index from the eCFR (already committed; only if it needs refreshing):
PYTHONPATH=src py -3.12 -m commoditybench.ccl.parse_ecfr --fetch
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

- **23 VERIFIED** (`verified: true`): 2 Thorlabs invoices (KM100, BB1-E02) + 21 round-1 items
  signed off this session (9 ADI Tier A, 7 Microchip Tier B, 5 Digi-Key Tier B). The 6
  non-human-visible Thorlabs (incl. the 1550 nm `6A995` lasers) were **cut** — that emptied
  Cat 6.
- **11 NEW candidates (`verified: false`), added this session — awaiting sign-off.** Human-
  visible ECCN confirmed by agents; flip after a spot-check (worksheet links each one):
  - **Cat 7** (4): 3 ADI IMUs/gyros (`7A994` ×2, `7A003.d.1`; **Tier A**, same ADI tool) +
    Honeywell HGuide i300 (`7A994`, manufacturer page, Tier B).
  - **Cat 1** (3): LND neutron detectors — `1A999` ×2 (BF3, B10-lined) + `1C232` (He-3).
    Tier B, LND public FAQ; **ECCN assigned by family, not per-part** — clean for the two
    1A999; the `1C232` rests on the FAQ's "certain models" hedge.
  - **Cat 2** (2): `2B999.j` bronze gear pump (Tier B distributor; ECCN sits in the
    product-name string) + a P4/ABEC-7 super-precision bearing that is **EAR99** (a
    deliberate over-classification trap vs 2A001).
  - **Cat 9** (2): 2 Piper aircraft parts, `9A991.d`. **Tier C / lowest confidence** —
    PilotsHQ appears to template the BIS aircraft-parts default; cross-check vs OEM or drop.

## Immediate next steps (in order)

1. **Sign off the 11 new candidates**: spot-check ~2 per source via the worksheet, then set
   `verified: true` on the confirmed rows (edit `data/questions.jsonl`; keep notes/source
   intact) and `make_worksheet.py`. The Piper Cat-9 pair is the weakest — decide drop vs
   keep first. Then re-run the comparison + dashboard on the larger verified set.
2. **Re-run the agentic A/B** (now unblocked — keys are in `.env`) to confirm the tool-lift
   numbers after the two loop-robustness fixes.
3. **Backfill still-empty categories 0/4/6/8.** Cat 6 regressed to empty (Thorlabs lasers
   cut) — re-source via DRS Infrared/Pelco (thermal cameras, 6A003) per the sourcing map.
   Cat 4 = Apple/HP/Oracle ECCN matrices; Cat 8 (marine) has few public sources. Cat 0 has
   essentially no commercial product with a visible ECCN (reactors/facilities) — likely a
   BIS FAQ example or skip. Strong unfinished Cat-9 lead: Boeing Distribution `9A991`
   connector pages (WAF-blocked from this box; open in a real browser).
4. **Equalize the comparison** (a real decision before any head-to-head ranking — see Open
   issues) or keep labeling every cross-model table "not equalized."
5. **Then** the RAG stretch: build the index from the eCFR (15 CFR 774 Supp. No. 1; see
   `rag/build_index.py` TODO) and A/B it.

## Open issues / flags

- **Provider comparability is NOT equalized**: Claude & Qwen3 run with reasoning on;
  GPT-4o at temp=0. The `comparison` run and the dashboard are explicitly labeled a
  capability snapshot, not a ranking. Decide before any head-to-head claim.
- **New-candidate provenance caveats** (carry into sign-off): LND ECCNs are family-level
  (per-part `1C232` unconfirmed); the Oberdorfer `2B999.j` lives in a distributor product-
  name string, not a dedicated field; the Piper `9A991.d` pair looks distributor-templated.
- **Distribution skew**: still heavy on Cat 5 + EAR99 (EAR99 = 9 of 34). Categories
  **0/4/6/8 empty**; 1/2/9 now thin (1–3 each). Cat 6 emptied when the Thorlabs lasers were cut.

## Environment / tooling

- `gh` authed as `maxwell-k-roberts` with access to `IAPS-AI`. Commit on a branch or main;
  end commit messages with `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.
- Python: `py -3.12`. For PDFs use the Read tool; for blocked/JS pages use
  `node C:/Users/maxwe/tools/fetch.mjs "<url>" --wait 6000`.
- Helper from a prior session: `C:/Users/maxwe/tools/mchpeccn.mjs <part>` hits Microchip's
  export-control API (returns ECCN JSON) — useful for cross-checking Microchip parts.
- Manufacturer export endpoints (ADI, Microchip, Thorlabs) are session/XHR-gated; plain
  curl returns empty. Use a headless browser (the fetch.mjs tool) or a research agent.
- **ADI export tool** (`analog.com/.../view-export-classification.html`) only renders results
  under the REAL Chrome engine — headless Chromium fails its JS via `ERR_HTTP2_PROTOCOL_ERROR`
  and returns an empty form / placeholder row. A reusable Playwright driver (launches
  `channel:"chrome"`, types the part into the search box, reads the US ECCN cell + cross-checks
  the `FetchExportClassificationData` JSON) is at `C:/Users/maxwe/tools/adichrome.mjs`.
- For open-weight evals, `RUNPOD_API_KEY` (RunPod public endpoints, ~$10/1M tokens) joins the
  three provider keys in `.env`; `.env.example` lists all four.

## Memory

Durable facts are in the session memory dir (`MEMORY.md` index): IAPS org URL, project
overview, BIS index + accuracy caveat, and the dataset provenance rules. They load
automatically; this file is the project-local complement.
