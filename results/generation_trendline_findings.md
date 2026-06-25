# Cross-generation trendline — findings

A **METR-style trendline**: ECCN-classification capability plotted against each model's
**release date**, holding the provider and tier constant and varying only the *generation*.
Where the existing runs compared *across models* (one generation, several providers) and
*within a model* (tools vs. no tools), this measures **across generations of the same
Opus line**, to see whether newer models are getting better at the BIS task.

## Method

- **Ladder:** the five Claude **Opus** generations callable as of 2026-06-25. Older
  generations (Opus 3, Sonnet/Haiku 3.x, Opus 4 / Sonnet 4) are already **retired** and
  return 404, so the ladder cannot reach further back than Opus 4.1.

  | Generation | Released (Models API `created_at`) | Native reasoning config |
  |---|---|---|
  | Opus 4.1 | 2025-08-05 | extended thinking (`budget_tokens`); **no** `effort` |
  | Opus 4.5 | 2025-11-24 | extended thinking + `effort=high` |
  | Opus 4.6 | 2026-02-04 | adaptive thinking + `effort=high` |
  | Opus 4.7 | 2026-04-14 | adaptive thinking + `effort=high` |
  | Opus 4.8 | 2026-05-28 | adaptive thinking + `effort=high` |

- **Native-config snapshot, NOT equalized.** Each generation runs in its strongest
  *native* reasoning surface, because the API diverges across generations: 4.1/4.5 predate
  adaptive thinking and 400 on it; 4.1 has no `effort` parameter; 4.7/4.8 400 on
  `budget_tokens`. Configs were confirmed empirically (a per-model 400-probe), not guessed.
  `max_tokens=8192` on all five so no generation is truncated (a confound that would
  otherwise penalise the newer adaptive models). This mirrors the existing `comparison`
  run's framing: a **capability snapshot**, not a controlled ranking.
- **Dataset:** the **23 verified** questions (`--verified-only`). All accuracy is over all
  23 (errors/unparsed = 0).
- **Reproduce:**
  ```bash
  PYTHONPATH=src py -3.12 -m commoditybench.run_eval --dataset data/questions.jsonl \
    --models claude-opus-4-1 claude-opus-4-5 claude-opus-4-6 claude-opus-4-7 claude-opus-4-8 \
    --verified-only --workers 6 --run-id gen
  PYTHONPATH=src py -3.12 scripts/build_generation_trendline.py \
    --notools results/gen__summary.json --out dashboard/generation_trendline.html
  ```

## Results — no tools (`gen`, 23 verified, 0 errors, 100% parse)

| Generation | Released | exact | eccn | group | grade |
|---|---|---|---|---|---|
| Opus 4.1 | 2025-08 | 0.348 | 0.435 | 0.565 | 0.461 |
| Opus 4.5 | 2025-11 | 0.391 | 0.522 | 0.609 | 0.517 |
| Opus 4.6 | 2026-02 | 0.391 | 0.478 | 0.609 | 0.504 |
| Opus 4.7 | 2026-04 | 0.391 | 0.478 | 0.565 | 0.487 |
| Opus 4.8 | 2026-05 | **0.217** | **0.348** | 0.565 | **0.396** |

## Interpretation

- **The no-tools trendline is flat, then dips.** From Opus 4.1 → 4.7 capability is
  essentially flat (exact 0.35→0.39, grade 0.46→0.50 — a one-question wobble), and **Opus
  4.8 is the lowest point** on every metric (exact 0.22, grade 0.40). Newer Opus
  generations are **not** better at raw, unaided ECCN classification on this set; the
  newest is somewhat worse.
- **Consistent with the known failure mode.** The project's standing finding is that
  models **over-classify** — reaching for controlled ECCNs on EAR99 items and anchoring on
  familiar codes. A more capable, more confident model can over-classify *more*, which is a
  plausible read of the 4.8 dip. The flat-then-down shape says general capability gains are
  not translating into BIS-task accuracy without grounding in the CCL.
- **`group`/`category` accuracy is steady (~0.57–0.61 across all five).** Every generation
  lands the right CCL neighbourhood at about the same rate; what moves (and degrades on
  4.8) is pinning the *exact* ECCN. That's a recall/judgment gap, not a "doesn't understand
  the domain" gap — the same diagnosis the agentic tooling was built to address.

### Caveats (read the shape, not the points)

- **n = 23.** One question ≈ 0.043 of the score. The 4.1↔4.7 differences are within noise;
  only the 4.8 dip (≈3–4 questions below the cluster) is suggestive, and still small-n.
- **Not equalized** (native configs differ by generation) — a capability snapshot. Don't
  read it as "4.1 ≈ 4.7 as models," only as "on this task, in each one's native config,
  unaided accuracy didn't rise."
- Distribution skew carries over from the dataset (heavy Cat 5 + EAR99); empty Cat 0/4/6/8.

## Tools condition — PENDING (not run)

The plan was to draw the trendline for **both** conditions (the headline ask was tools +
no-tools across generations). The agentic (CCL-navigation) run **did not complete**: the
Anthropic API account hit its **credit balance** partway through. Opus 4.1 agentic ran
~19/23 before credits depleted; 4.5/4.6/4.7/4.8 agentic returned billing 400s for every
item. Those billing-failed outputs were **deleted** rather than committed (they would read
as all-zero results). The no-tools run above completed *before* credits ran out and is
clean.

**To finish:** add API credits, then
```bash
PYTHONPATH=src py -3.12 -m commoditybench.run_eval --dataset data/questions.jsonl \
  --models claude-opus-4-1 claude-opus-4-5 claude-opus-4-6 claude-opus-4-7 claude-opus-4-8 \
  --verified-only --agentic --workers 6 --run-id gen_agentic
PYTHONPATH=src py -3.12 scripts/build_generation_trendline.py \
  --notools results/gen__summary.json --agentic results/gen_agentic__summary.json \
  --out dashboard/generation_trendline.html
```
The trendline builder already renders the tools series (solid lines) the moment a
`gen_agentic__summary.json` is passed; the page shows a "tools condition pending" banner
until then. The open question the tools run answers: does CCL grounding bend the flat
no-tools line **upward**, and does the lift **grow** with generation (newer models use the
tools better) or stay flat? The within-model A/B on Opus 4.8 (exact 0.27→0.56, grade
0.41→0.64 over all 34) says tools help a lot for *that* generation; whether older
generations capture the same lift is the cross-generation question.
