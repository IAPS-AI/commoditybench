# Agentic CCL navigation — results (Claude Opus 4.8 + cross-model)

**Question:** does giving a model *tools to read the actual Commerce Control List* raise
ECCN-classification accuracy — and is the gain real, or an artifact of tuning the tools to
this dataset? Two runs over the **34-question** set (23 verified + 11 newer candidates):

- **Cross-model, no tools** (`expanded`): claude-opus-4-8, gpt-4o, qwen3-32b — capability snapshot.
- **Within-model, agentic** (`expanded_agentic`): claude-opus-4-8 calls four CCL tools
  (`list_ccl_categories`, `get_category_outline`, `read_eccn`, `search_ccl`) then submits.
  Mean 4.7 tool calls/item, 0 errors.

The interactive write-up of all of this is the site at `dashboard/index.html`
(`scripts/build_site.py`).

## Headline — within-model tool lift

| Metric | No tools | + tools | Lift |
|---|---|---|---|
| Exact accuracy (all 34) | 0.265 | **0.559** | +0.29 (**+111%**) |
| Mean graded score (all 34) | 0.409 | **0.641** | +0.23 (+57%) |
| Mean graded score (verified 23) | 0.409 | **0.648** | +0.24 |
| Mean graded score (new 11) | 0.409 | **0.627** | +0.22 |

## Cross-model, no tools (not equalized — Claude/Qwen3 reason, GPT-4o temp 0)

| Model | Exact (all) | Grade (all) |
|---|---|---|
| Claude Opus 4.8 | 0.26 | 0.41 |
| GPT-4o | 0.18 | 0.39 |
| Qwen3-32B (open) | 0.00 | 0.10 |

## Is the lift overfit to the dataset? No — three independent checks

1. **Generalizes to categories that didn't exist when the tools were built.** The 11 new
   items (Cats 1/2/7/9) were added *after* the agentic tooling. Their lift (0.41→0.63) is
   essentially identical to the verified set's (0.41→0.65). The tools can't have been
   tuned to them.
2. **The lift survives a fully generic prompt + unbiased tools.** The system prompt was
   stripped of every dataset-specific ECCN (it teaches only the general order of review:
   specific control → catch-all → EAR99, check thresholds, resolve the leaf); the tool
   descriptions were de-exampled; and the search ranker's catch-all up-weight was removed.
   Grade held (0.60 hinted → 0.59 generic on the verified set), so the gain is reading the
   list, not prompt hints.
3. **It beats a planted trap.** The Nachi super-precision bearing (gold EAR99) was added as
   a deliberate over-classification lure toward a controlled materials entry. No-tool Claude
   took the bait (`2A001.a`); with tools it read the entry's thresholds and cleared it (EAR99).

## Where tools help — and where they don't (per CCL category, mean grade)

| Category | No tools → tools | Read |
|---|---|---|
| 7 Navigation & Avionics | 0.78 → **1.00** | Nails the 7A994/7A003 IMU split by reading thresholds |
| 3 Electronics | 0.28 → **0.94** | Biggest win — catch-all recall + thresholds |
| 2 Materials Processing | 0.00 → 0.50 | Trap beaten; a distributor-buried ECCN still missed |
| 5 Telecom & Info-Security | 0.30 → 0.52 | Helped, but crypto + networking over-control persist |
| 9 Aerospace | 0.50 → 0.50 | Flat (one item over-controlled) |
| 1 Materials & Chemicals | 0.13 → 0.30 | Hard niche (neutron-detector controls); mixed |
| EAR99 | 0.62 → 0.62 | Net flat: some EAR99 recovered, offset by over-control |

**The pattern:** tools decisively fix *recall* failures (an entry the model forgot exists,
a threshold it half-remembered). They barely move — and can worsen — *judgment* calls about
whether borderline language applies.

### The double-edged finding (kept, not hidden)
Reading the `5A991` telecom catch-all reliably tempts the model to **over-control ordinary
Ethernet PHYs that BIS classifies EAR99** (`lan8720a`, `lan8742a`, `ksz8794` → `5A991.b.4.a`).
A GPS antenna coax cable was likewise over-thought into a navigation ECCN. Giving the model
more text is not strictly safe: it raises recall but can lower precision on near-threshold
items. This is a generalizable limitation, not a dataset artifact.

## Reproduce

```bash
PYTHONPATH=src py -3.12 -m commoditybench.run_eval --dataset data/questions.jsonl \
  --models claude-opus-4-8 gpt-4o qwen3-32b --run-id expanded
PYTHONPATH=src py -3.12 -m commoditybench.run_eval --dataset data/questions.jsonl \
  --models claude-opus-4-8 --agentic --workers 4 --run-id expanded_agentic
PYTHONPATH=src py -3.12 scripts/build_site.py   # -> dashboard/index.html
```

Per-question rows carry the full agentic tool-trace in `usage.tool_calls`; the site's
"Every item" table renders it (click a row). Runs include unverified items and are **not
citable as headline accuracy** — `--verified-only` numbers are the reportable ones; the
verified slice is broken out above and toggleable on the site.
