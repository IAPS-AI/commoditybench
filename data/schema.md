# Dataset schema & sourcing methodology

A CommodityBench dataset is a JSON Lines (`.jsonl`) file: one classification question
per line. Blank lines and lines starting with `#` are ignored.

## Question fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | yes | Stable unique id, e.g. `cisco-c9300-001`. |
| `item_name` | string | yes | Short product/commodity name. |
| `description` | string | yes | The text shown to the model: what the item is, its function, and salient technical specs. **This is the only item information the model sees.** |
| `gold_eccn` | string | yes | Ground-truth ECCN (e.g. `5A002.a.1`) or `EAR99`. |
| `manufacturer` | string | no | Vendor, when applicable. |
| `source_url` | string | no | Where the ground-truth label was published. |
| `source_type` | string | no | Provenance (see below). Default `manufacturer_self_classification`. |
| `verified` | bool | no | `true` only once a human confirmed the label against its source. Default `false`. |
| `category` | string | no | Single-digit CCL category, for stratified analysis. |
| `difficulty` | string | no | `easy` \| `medium` \| `hard` (annotator judgment). |
| `notes` | string | no | Free-form annotator notes. |

### `source_type` values

- `manufacturer_self_classification` — a vendor's published ECCN for a real product.
- `bis_advisory_opinion` — a BIS advisory opinion / public guidance.
- `bis_faq_example` — a worked example from BIS training material or FAQs.
- `ccats` — a Commodity Classification (CCATS) determination, where available.
- `synthetic_from_ccl` — constructed from CCL entry text (use sparingly; see caveat).
- `other` — anything else; explain in `notes`.

## The `verified` flag is load-bearing

`run_eval --verified-only` drops every question with `verified == false`. **Always use
`--verified-only` for any number you report.** Unverified rows exist only to let you
exercise the harness end-to-end before the labeled set is built. The bundled
`questions.example.jsonl` is intentionally **all unverified** and must never be cited as
a result.

## Sourcing methodology (manufacturer self-classifications)

The hard part of this benchmark is ground truth. Our primary source is **manufacturer
self-classifications**: real commercial products that vendors publish with an official
ECCN on their export-compliance pages.

**Start from BIS's own index.** BIS maintains an opt-in page listing companies that
publish ECCN information for their products:
<https://www.bis.gov/licensing/classify-your-item/publicly-available-classification-information>.
That is the canonical, authoritative entry point — work outward from the companies it
links. The list (archived at `ccats-website-table-april-2018.pdf`) is distilled by CCL
category in [`sources/bis-listed-eccn-publishers.md`](sources/bis-listed-eccn-publishers.md),
which is the sourcing plan. Beyond it, manufacturer "export compliance" pages and
distributor aggregators (Digi-Key, Mouser) are acceptable *fallbacks* with weaker
provenance.

**Two hard rules (learned the hard way):**
1. **Provenance must be human-checkable.** The `source_url` must actually *display* the
   ECCN to a person who opens it. A value scraped from a page's backend data field that a
   human can't see on the page does **not** qualify — even if the number is right. (This
   sank the round-1 Thorlabs items: thorlabs.com served the ECCN via a hidden data field,
   not visible text.) When the page doesn't show it, find a document that does (e.g. a
   purchase invoice listing the ECCN) and cite that instead.
2. **Prefer companies on the BIS list.** For a BIS-facing benchmark, a self-classification
   from a company on BIS's own index is more defensible than one from an arbitrary page.

### ⚠️ The accuracy caveat (read before trusting any label)

On that same page, BIS states the published classifications are *"for informational
purposes only,"* that **"BIS will not validate or be responsible for the accuracy of the
classification information,"** and that inclusion is not a BIS endorsement. Self-classified
ECCNs are therefore **strong but not authoritative** signals. Treat them as candidate
labels that a human must confirm before flipping `verified` to `true`. Where a vendor's
self-classification looks inconsistent with the controlling CCL text, record the
disagreement in `notes` rather than silently trusting either.

### Per-item curation checklist

1. Pull the product + its published ECCN from the vendor's export-compliance page.
2. Write a `description` from the product's own datasheet — **functional and technical
   characteristics only**. Exclude the vendor name and the ECCN from the description, or
   the task becomes a lookup instead of a classification.
3. Record `source_url` (deep-link to the page bearing the ECCN) and `manufacturer`.
4. Sanity-check the ECCN against the controlling CCL category/entry; note any doubt.
5. A second annotator confirms → set `verified: true`.

### Balancing the set

- **Stratify across CCL categories** (0–9) and product groups (A–E) so the benchmark
  isn't dominated by, say, Category 5 networking gear.
- **Include EAR99 items.** Much of the real workload is deciding an item is *not* on the
  CCL; a benchmark without EAR99 examples overstates difficulty discrimination.
- **Vary difficulty.** Mix obvious cases with ones that turn on a specific technical
  threshold (clock speed, encryption key length, laser wavelength), where classification
  genuinely hinges on a parameter in the `description`.

### On `synthetic_from_ccl`

Generating questions by paraphrasing CCL entry text is fast and reproducible but
**structurally favors the RAG condition** (the answer is in the retrieved text) and tests
reading comprehension more than classification judgment. Keep any synthetic items clearly
labeled and report them as a separate slice, never blended into the headline number.
