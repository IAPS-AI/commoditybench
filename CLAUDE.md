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
- **Results website (NEW): `dashboard/index.html`** via `scripts/build_site.py` (+
  `site_template.html`). Self-contained/offline, swaggin export-control identity (ECCN
  grade-ladder decoder; amber=controlled / teal=cleared). Shows BOTH the cross-model
  leaderboard (no tools) AND the within-model tool lift, with All/Verified toggles,
  per-category lift, "where tools break" case studies, and a per-item explorer that renders
  the agent's CCL tool-trace. Regenerate: `scripts/build_site.py --crossmodel
  results/expanded__summary.json --agentic results/expanded_agentic__summary.json`. (Old
  single-run `build_dashboard.py` kept for one-off summaries.)
- **Agentic CCL-navigation tooling: built, hardened, A/B'd on the full 34.** `commoditybench/ccl/`
  parses the CCL from the eCFR (637 entries) into a navigable index + tools (`--agentic`).
  Within-model lift on Claude Opus 4.8 over all 34: **exact 0.27→0.56, grade 0.41→0.64**
  (verified-only grade 0.41→0.65), 0 errors. **Overfitting-hardened** (commit `b721a36`):
  generic order-of-review prompt with no dataset ECCNs, de-exampled tool descriptions,
  removed the catch-all search up-weight — and the lift held, generalized to the 11 new
  categories added afterward, and beat a planted over-classification trap. Tools fix
  *recall* gaps (catch-alls, thresholds) but not *judgment* calls; reading the 5A991 telecom
  catch-all even induces over-control of EAR99 Ethernet PHYs (double-edged). Full write-up:
  `results/agentic_ab_findings.md`. Runs: `expanded` (cross-model) + `expanded_agentic`.
- **Cross-generation trendline (NEW, branch `cross-generation-trendline`).** A METR-style
  plot of capability vs. **model release date** across the **Opus generation ladder**
  (4.1→4.5→4.6→4.7→4.8; older gens are retired/404 as of 2026-06-25). The Anthropic adapter
  now drives older generations via per-model `thinking_mode` (`extended` for 4.1/4.5 which
  predate adaptive thinking) + optional `effort` (4.1 has none); configs verified by a 400
  probe. **No-tools run done** (run-id `gen`, 23 verified, 0 errors): the trendline is
  **flat then dips** — exact 0.35→0.39 across 4.1–4.7, then **4.8 lowest at 0.22** (grade
  0.40); `group`/`category` steady ~0.57–0.61. Newer Opus isn't better at unaided ECCN
  classification here; over-classification plausibly worsens it. **Tools (agentic) half
  NOT done — API credits ran out mid-run** (billing 400s; failed outputs deleted). Trendline
  page: `dashboard/generation_trendline.html` (shows a "tools pending" banner); builder
  `scripts/build_generation_trendline.py`; writeup `results/generation_trendline_findings.md`.
  **Now also folded into the main results website** (`scripts/build_site.py --generations`):
  a new "02 · Across generations" section with a METR-style timeline (signature element — the
  teal grade line vs. a dotted "if scale transferred" reference it conspicuously fails to
  follow, plus a per-generation grade-ladder strip), and the hero reframed around the unified
  thesis *the lever is grounding, not scale*. `dashboard/generation_trendline.html` is kept as
  the standalone lightweight artifact.
- **Subscription harness for the tools condition (NEW): `cc_harness/`.** Runs the agentic
  (read-the-CCL) condition through a **Claude Code session on a Max subscription** instead of
  burning API credits (the API agentic cross-gen run died on a credit wall). The folder is
  self-contained: `CLAUDE.md` (the agentic system prompt + tool guide, auto-loaded so the
  session *is* the model under test), `ccl.py` (the 4 CCL tools as a CLI — `categories/outline/
  read/search`, vendored verbatim from `ccl/index.py`), vendored `ccl_index.json`, `questions.jsonl`
  (the 23 verified items **sanitized** to id+name+description — no gold, no category), `record.py`
  (writes answers to `../../cc_results/<label>__answers.jsonl`, **outside the repo** so runs can't
  peek and no gold sits beside the questions), and `PROMPT.txt`. Grade with
  `scripts/grade_cc_runs.py` (same graded scorer + run_eval-shaped output; prints the tool lift
  vs. the no-tools `gen` baseline by label). **Caveat:** Claude Code's `/model` only exposes
  current-gen (Opus 4.8 / Sonnet 4.6 / Haiku 4.5), so this yields the tools condition for those
  (completing the 4.8 tool-lift point + a cross-tier tools comparison), not the full 4.1→4.8 ladder.
- **Not done:** sign-off on the 11 new candidates; Cat **0/4/6/8 still empty**; equalized
  comparison; RAG index. Cross-model headline accuracy should still cite the 23-verified set;
  keep the not-equalized / tool-lift framing. The expanded runs include unverified items (for
  the site) and are flagged NOT CITABLE by the harness.

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
  build_site.py + site_template.html      # CURRENT results website: cross-model + tool-lift,
                   #   ingests TWO runs (expanded + expanded_agentic) -> dashboard/index.html
  build_dashboard.py + dashboard_template.html  # legacy single-run microsite (one summary)
dashboard/index.html     # generated results website (committed; embeds both runs' data)
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
  --models claude-opus-4-8 --agentic --workers 4 --run-id expanded_agentic
# Build the results WEBSITE (cross-model + tool-lift + across-generations timeline):
PYTHONPATH=src py -3.12 scripts/build_site.py \
  --crossmodel results/expanded__summary.json --agentic results/expanded_agentic__summary.json \
  --generations results/gen__summary.json   # --generations optional; section hides if absent
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
   keep first. The agentic explorer on the site is a fast spot-check aid: the parts where
   tools went *wrong* (`lnd-2311-b10`, the two Piper items) may be tool errors OR bad labels.
   Then re-run `expanded` + `expanded_agentic` and rebuild the site on the larger verified set.
2. **DONE this session — agentic tooling complete.** Built + overfitting-hardened + A/B'd on
   the full 34 (exact 0.27→0.56, grade 0.41→0.64; lift generalizes to the new categories and
   survives a generic prompt). Results website built (`scripts/build_site.py`). See
   `results/agentic_ab_findings.md`. Remaining tool ideas if revisited: a precision guardrail
   for the 5A991 telecom over-control (double-edged finding), and add the agentic condition to
   gpt-4o/qwen3 (only the Anthropic adapter has `classify_agentic`).
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
  `node tools/fetch.mjs "<url>" --wait 6000`. The ECCN-verification helpers are now
  **vendored in `tools/`** (was `C:/Users/maxwe/tools/`); see `tools/README.md` for the
  per-machine setup (`npm install playwright`; `adichrome.mjs` needs a real Chrome).
- Helper from a prior session: `node tools/mchpeccn.mjs <part>` hits Microchip's
  export-control API (returns ECCN JSON) — useful for cross-checking Microchip parts.
- Manufacturer export endpoints (ADI, Microchip, Thorlabs) are session/XHR-gated; plain
  curl returns empty. Use a headless browser (the fetch.mjs tool) or a research agent.
- **ADI export tool** (`analog.com/.../view-export-classification.html`) only renders results
  under the REAL Chrome engine — headless Chromium fails its JS via `ERR_HTTP2_PROTOCOL_ERROR`
  and returns an empty form / placeholder row. A reusable Playwright driver (launches
  `channel:"chrome"`, types the part into the search box, reads the US ECCN cell + cross-checks
  the `FetchExportClassificationData` JSON) is at `tools/adichrome.mjs`.
- For open-weight evals, `RUNPOD_API_KEY` (RunPod public endpoints, ~$10/1M tokens) joins the
  three provider keys in `.env`; `.env.example` lists all four.

## Memory

Durable facts are in the session memory dir (`MEMORY.md` index): IAPS org URL, project
overview, BIS index + accuracy caveat, and the dataset provenance rules. They load
automatically; this file is the project-local complement.
