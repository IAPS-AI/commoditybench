# Methodology (draft for Issue Brief)

> Working copy, synced to the Google doc as of 2026-06-25 (Maxwell's edits to sections 1–3
> folded in) plus the revised Section 4. Dataset is now fully verified (34/34).

## Methodology

### Building the dataset

Every question pairs a real commodity with the ECCN that its manufacturer — or another
authoritative source — assigned to it. Labels were verified by human review after being
sourced by AI-assisted research. The benchmark currently holds 34 questions. Items come from
manufacturer export-classification tools and self-classifications (e.g. Analog Devices,
Microchip, Honeywell), authorized distributors, and purchase invoices. They span CCL
Categories 1, 2, 3, 5, 7, and 9, plus EAR99 — items subject to the EAR but not listed on the
Control List. EAR99 items are about a quarter of the set by design to test for
overclassification.[^1]

[^1]: The set is somewhat small and unevenly distributed — Categories 0, 4, 6, and 8 are not
yet represented, and Category 5 and EAR99 are over-weighted.

### Framing the task and prompting the models

We evaluate models across three vendors and both weight classes. The primary comparison is
among three contemporary frontier models — **GPT-5.5** (OpenAI, high reasoning effort),
**Claude Opus 4.8** (Anthropic, adaptive thinking), and **Qwen3-235B-A22B** (Alibaba, an
open-weight 235-billion-parameter mixture-of-experts model served on our own hardware) — each
run in *both* the closed-book and the agentic conditions described below. We also report two
weaker closed-book-only baselines, **GPT-4o** (no reasoning) and the smaller open **Qwen3-32B**,
and a cross-generation ladder of Anthropic's Opus line (4.1 → 4.5 → 4.6 → 4.7 → 4.8), run
closed-book, to test whether newer general-purpose models are getting better at this specific
task. The ladder is reported separately from the main leaderboard: it was run on the original
23-item verified set only, so its scores are not pooled with the 34-item results (a mixed-n
comparison would flatter the 23-item runs). Every model gets the same framing.
For each question it receives an item name and a plain-language description of the kind a
manufacturer or buyer would write: physical characteristics, function, and key technical
parameters. The model must reply with a structured JSON object holding three fields: the
ECCN, the CCL category (0–9, or EAR99), and a short reasoning statement citing the
controlling text or parameters. A system prompt sets the analyst role and answer rules; the
user prompt carries the item. Both are reproduced in the Appendix.

### Scoring: graded partial credit, with EAR99 as its own class

An ECCN is hierarchical — a leading digit for the category (e.g. 3 = Electronics), a letter
for the product group (e.g. A = systems and equipment), three digits for the entry, and
optional subparagraphs that narrow the control. The benchmark scores on a graded scale rather
than all-or-nothing, because in a real workflow getting the category and product group right
is materially more useful than a random guess even when the final subparagraph is wrong. Each
prediction earns credit at the most specific level it gets right:

| Level | What matches | Credit |
| :-: | :-: | :-: |
| Exact | The full ECCN, including subparagraph | 1.0 |
| ECCN | The five-character entry (e.g. 3A001), wrong subparagraph | 0.7 |
| Group | Category + product group (e.g. 3A) | 0.4 |
| Category | Category only (e.g. 3) | 0.2 |
| None | Nothing matches | 0.0 |

We report two headline numbers: exact-match accuracy (did the model produce the
classification BIS would assign?) and the graded score (how close it came on average).
Together they separate a model that is in the right neighborhood from one that is guessing.

EAR99 is its own equivalence class. Predicting EAR99 when the answer is EAR99 is a full
match; predicting a real control number for an EAR99 item, or vice versa, scores zero and
earns no partial credit — even if the category "would have" matched. Confusing "not
controlled" with a real control, in either direction, is a serious error with real licensing
consequences, and the scoring reflects that.

### Experimental conditions

We run the benchmark in two conditions:

**Closed-book (no tools).** The model classifies from its own parametric knowledge, with no
access to the regulation text. This measures what a model knows off the shelf, and is the
condition all three models were run in.

**Agentic (tools).** The model is given tools to read the actual Control List and is told to
look entries up rather than classify from memory. We parsed the CCL from the eCFR (637
entries) into a navigable index and exposed four read-only tools — list the ten categories;
read a category's full outline, including the catch-all "basket" entries; read a specific
entry's full text down to its numeric thresholds; and keyword-search the list — plus a
terminal tool the model calls to submit its answer. A revised system prompt walks the model
through an analyst's order of review: narrow to a category, read the whole outline, check the
item against each candidate entry's actual thresholds, resolve to the most specific
subparagraph, and conclude EAR99 only once no entry — specific or catch-all — applies. (The
full prompt and tool descriptions are in the Appendix.)

All three frontier models — GPT-5.5, Claude Opus 4.8, and Qwen3-235B — were run in both
conditions. (The harness's tool-use loop, originally implemented for the Anthropic model, was
extended to OpenAI and any OpenAI-compatible endpoint, so GPT and open-weight models get the
same tools.) The tool effect can therefore be read two ways. The cleaner reading is
**within-model**: comparing a model's tooled score against its own closed-book score isolates
the effect of giving the model the source BIS would most plausibly put in front of it, holding
the model and its inference settings fixed — what grounding in the primary source buys, with
nothing else varying. The tools were also run across models under equal tool access, but that
cross-model reading inherits the equalization caveat below.

One caveat applies to every *cross-model* comparison, in either condition: the models were not
run under identical inference settings. Each runs in its strongest native configuration
(GPT-5.5, Opus 4.8, and Qwen3 with reasoning enabled; GPT-4o at a fixed deterministic setting;
and, in the generation ladder, each Opus generation in whichever reasoning surface its API
supports, since the API diverges across generations). Cross-model figures are therefore best
read as a capability snapshot rather than a strictly controlled ranking. The within-model tool
comparison does not have this problem, because the model is held fixed and only tool access
changes.

---

## Notes on this revision

- **Model set expanded (§2)** to reflect the frontier-comparison runs: the primary comparison
  is now GPT-5.5, Opus 4.8, and the open-weight Qwen3-235B, each run in *both* conditions;
  GPT-4o and Qwen3-32B are demoted to closed-book baselines; the Opus 4.1→4.8 generation ladder
  is introduced. (Supersedes the earlier "three models, agentic = Opus only" framing.)
- **Agentic is no longer Opus-only (§4).** The tool-use loop was extended to OpenAI and
  OpenAI-compatible endpoints, so all three frontier models were tooled. The within-model
  reading is retained as the cleaner one; a cross-model tooled comparison also exists but
  carries the equalization caveat.
- **Not-equalized caveat** now applies to *every* cross-model comparison (both conditions and
  the generation ladder), not just the closed-book one.
- Sections 1–3 mirror the current Google-doc text, including the §1 footnote on set size.
- **Done 2026-07-01: 34-item re-aggregation.** The `verified` flags were flipped in the run
  files and the pooled results (site + `dashboard/site_data.json`) are now computed over the
  full 34-item verified set (10 runs, 456 observations). The Opus generation ladder is excluded
  from that pooling (23-item run; see §2) and lives on the standalone trendline page. Numbers
  in the earlier findings docs (`results/*_findings.md`) predate this re-aggregation.
- **Gold-label correction 2026-07-01:** `lnd-2517-he3` (He-3 neutron detector tube) was
  corrected from `1C232` to `EAR99` — 1C232's Controls note decontrols devices containing
  <1 g of He-3, and this tube's fill is ~2.9 mg. All runs containing the item were re-scored
  and their summaries regenerated before the 34-item aggregation above.
