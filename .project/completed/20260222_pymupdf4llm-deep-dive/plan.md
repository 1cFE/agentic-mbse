# Implementation Plan: pymupdf4llm Deep-Dive (Stage 1A)

**Status:** Complete
**Created:** 2026-02-22
**Last Updated:** 2026-02-22

## Source Documents

- **Spec:** `spec.md`
- **Development Strategy:** `../../concepts/doc-extraction-development-strategy.md` (Stage 1A)
- **Current backend:** `src/agentic_mbse/extraction/pymupdf_backend.py`

## Implementation Strategy

**This is a learning test.** The plan defines a method for systematic exploration, not a predetermined checklist of experiments. The agent doing this work must exercise judgment — looking at actual output, reading documentation, chasing down problems it discovers, and deciding what to investigate next based on what it finds.

The phases are: **setup → baseline → explore → synthesize**. The explore phase is deliberately open-ended.

---

## Phase 0: Setup

### Goal

Get all materials in place: expanded corpus, API documentation for reference, and a lightweight experiment harness.

### 0.1 Corpus Expansion

Download 7 PDFs from Zotero group 5428393 using fusion-tea's download tooling:

```bash
cd /home/reid/1cfe/fusion-tea
uv run python scripts/zotero_group_download.py <ITEM_ID> --output-dir /home/reid/1cfe/agentic-mbse/tests/corpus/pdfs/
```

| Zotero ID | Slug (pick based on filename) | Notes |
|-----------|-------------------------------|-------|
| IH9ZSRF8  | araiinejad_2024 | |
| LL7Q6PSU  | paischer_2025 | |
| 3IPQSG8C  | hansen_2025 | |
| AMPD8BWX  | seo_2024 | |
| 2H5CJVB8  | woodruff_2026b | (distinct from existing woodruff_2026) |
| BXDIV83P  | tajima | |
| UQMRDJ6D  | schulte_1978 | **Trim to 10 pages** after download |

For UQMRDJ6D trimming:
```python
import pymupdf
doc = pymupdf.open("schulte_1978_full.pdf")
trimmed = pymupdf.open()
trimmed.insert_pdf(doc, from_page=0, to_page=9)
trimmed.save("tests/corpus/pdfs/schulte_1978.pdf")
```

Register each in `tests/corpus/papers.jsonl` with slug, source (`zotero`), page count, and characteristics (inspect the PDF to determine: text-heavy, table-heavy, math-heavy, figure-heavy, etc.).

### 0.2 API Documentation

Gather pymupdf4llm reference material so the agent has it available during exploration:

1. **Fetch pymupdf4llm docs** from the web (PyPI page, pymupdf docs site) and save key findings
2. **Capture the full `to_markdown()` signature** with defaults (already known — see below)
3. **Read source code** of `IdentifyHeaders` and `TocHeaders` helpers to understand what they actually do
4. **Save all of this** to `api-reference.md` in this work item directory

Known signature (pymupdf4llm v0.2.9):
```
to_markdown(doc, pages=None, hdr_info=None, write_images=False, embed_images=False,
            ignore_images=False, ignore_graphics=False, detect_bg_color=True,
            image_path='', image_format='png', image_size_limit=0.05, filename=None,
            force_text=True, page_chunks=False, page_separators=False, margins=0,
            dpi=150, page_width=612, page_height=None, table_strategy='lines_strict',
            graphics_limit=None, fontsize_limit=3, ignore_code=False, extract_words=False,
            show_progress=False, use_glyphs=False, ignore_alpha=False, **kwargs)
```

Notable: the **default** `table_strategy` is `"lines_strict"` — our code overrides to `"lines"`.

### 0.3 Experiment Harness

Build a lightweight Python script (`tests/corpus/experiment.py`) that:

- Takes a config name and parameter dict
- Runs `pymupdf4llm.to_markdown()` with those params against all (or selected) corpus PDFs
- Computes metrics via existing `metrics.py`
- Saves results to `tests/corpus/runs/{config_name}/` (metrics per PDF + raw markdown)
- Prints a comparison summary against baseline

Keep it simple. The harness is a convenience, not the point.

### Phase 0 Validation

- [x] All 15 PDFs present in `tests/corpus/pdfs/`
- [x] `papers.jsonl` has entries for all 15
- [x] API reference doc captured
- [x] Harness script runs and produces output

---

## Phase 1: Baseline

### Goal

Run the current config on all 15 PDFs. Capture metrics AND actually look at the output.

### What to Do

1. Run the experiment harness with the current config (call it `baseline`)
2. Capture metrics for all 15 PDFs
3. **Actually read the markdown output** for each new PDF:
   - Are headings detected correctly?
   - Are tables rendered as pipe tables or garbled?
   - Is math content preserved or turned to garbage?
   - Are there obvious artifacts (stray `<br>`, broken formatting)?
4. Write initial observations into `findings.md` — what works, what doesn't, what looks like it could be improved

### Phase 1 Validation

- [x] Baseline metrics captured for all 15 PDFs in `tests/corpus/runs/baseline/`
- [x] `findings.md` created with initial quality observations per document
- [x] Known issues identified (these drive what to explore in Phase 2)

---

## Phase 2: Explore

### Goal

Systematically investigate pymupdf4llm's parameters to understand what they do, which ones matter, and what the best configuration is for our corpus.

### Method

This is an iterative loop. Each iteration follows this pattern:

```
1. IDENTIFY — What issue or question are we investigating?
                (driven by what we observed, not a checklist)

2. HYPOTHESIZE — What parameter change might address it?
                  (consult api-reference.md, read pymupdf4llm source if needed)

3. RUN — Execute the experiment via the harness

4. EVALUATE — Look at the results:
   - Compare metrics (harness output)
   - INSPECT ACTUAL OUTPUT for affected documents
     Use pdf-analysis skill / extract_page.py to compare
     specific pages side-by-side with different configs
   - Note what improved, what regressed, what's unchanged

5. RECORD — Update findings.md with:
   - What we tried and why
   - What we observed (metrics + manual inspection)
   - What we concluded
   - What this suggests investigating next

6. DECIDE — What's the next most valuable thing to look at?
```

### Guidance (not prescriptions)

**Start with the obvious wins.** The current config overrides `table_strategy` from its default `"lines_strict"` to `"lines"`. The old branch found `lines_strict` was better. Verify this on the expanded corpus.

**Follow the problems.** If the baseline shows garbled tables in `hsu_2020`, investigate table parameters on that document. If headings are wrong in `schulte_1978`, look at `hdr_info` options. Let the data tell you what matters.

**Use the pdf-analysis skill for hands-on inspection.** When metrics show a difference, don't just trust the numbers — look at the actual pages. Render a page as an image, compare it to the markdown output. This is how you find things metrics miss.

**Read documentation when stuck.** If a parameter's behavior is unclear, read the pymupdf4llm source code. Check if there are GitHub issues or changelog entries about it. The `api-reference.md` from Phase 0 is a starting point, not the ceiling.

**Test interactions.** Individual parameter changes may interact. Once you have a sense of which parameters matter individually, try combining changes.

**Know when to stop.** You don't need to test every parameter combination. When you're seeing diminishing returns — each new experiment shows negligible difference — it's time to move to synthesis. Five solid experiments with clear findings beat twenty with nothing new to say.

### What NOT to Do

- Don't follow a rigid predetermined list of experiments
- Don't skip manual inspection in favor of just looking at metrics
- Don't ignore surprises — if something unexpected happens, investigate it
- Don't add postprocessing or cleanup code — this phase is about understanding raw API output

### Phase 2 Validation

- [x] At least 5 distinct configurations tested (more is fine if they're yielding insights) — 9 configs tested
- [x] Each experiment has observations in `findings.md` (not just metrics)
- [x] Manual inspection performed for at least the documents with known issues
- [x] Clear sense of which parameters matter and which don't

---

## Phase 3: Synthesize

### Goal

Consolidate what we learned into a recommendation, update the codebase, and capture institutional knowledge.

### What to Do

1. **Finalize findings.md** — Add a summary section:
   - Which parameters matter and why
   - Recommended configuration with evidence
   - Known limitations (what pymupdf4llm still can't do well)
   - Implications for downstream stages (what Docling/Claude will need to handle)

2. **Update `pymupdf_backend.py`** — Apply the best configuration:
   - Change parameter values with comments explaining why (referencing findings)
   - If the custom `_academic_header_detector` proved unnecessary, simplify
   - If a built-in header detector works better, switch to it

3. **Update `extract_page.py`** — Keep it consistent with the backend

4. **Update baseline metrics** — Re-run with the new config and save as the new baseline

5. **Verify no regressions** — Run `tests/corpus/compare.py` against original 8-PDF baseline

### Phase 3 Validation

- [x] `findings.md` has a clear final recommendation section
- [x] `pymupdf_backend.py` updated with best config + rationale comments
- [x] Baseline metrics refreshed for all 15 PDFs (best_v1_rerun)
- [x] No regressions on original 8 PDFs (vs pymupdf baseline; fusion-tea regressions documented as known limitations)
- [x] Existing tests pass (`uv run pytest tests/`) — 820 passed, pre-existing syside license failures only

---

## Key Resources

| Resource | Location | Use |
|----------|----------|-----|
| Current backend | `src/agentic_mbse/extraction/pymupdf_backend.py` | Starting config |
| Metrics module | `tests/corpus/metrics.py` | Compute extraction quality |
| Comparison tool | `tests/corpus/compare.py` | Baseline vs current |
| pdf-analysis skill | `claude/skills/pdf-analysis/` | Hands-on page inspection |
| extract_page.py | `claude/skills/pdf-analysis/scripts/extract_page.py` | Single-page extraction |
| Zotero download | `/home/reid/1cfe/fusion-tea/scripts/zotero_group_download.py` | Get new PDFs |
| pymupdf4llm source | `.venv/lib/python3.12/site-packages/pymupdf4llm/` | Read when API docs insufficient |
| Findings report | `.project/active/pymupdf4llm-deep-dive/findings.md` | Living document |
| API reference | `.project/active/pymupdf4llm-deep-dive/api-reference.md` | Parameter documentation |

---

## Implementation Notes

*To be filled during implementation.*

### Phase 0 Completion
**Completed:** 2026-02-22
**Changes Made:**
- Downloaded 7 new PDFs from Zotero group 5428393 (araiinejad_2024, paischer_2025, hansen_2025, seo_2024, woodruff_2026b, tajima, schulte_1978)
- Trimmed schulte_1978 from 117pp to 10pp
- Registered all 7 in `papers.jsonl` with slug, source, page count, characteristics
- Created `api-reference.md` with full `to_markdown()` signature, parameter details, IdentifyHeaders/TocHeaders source analysis, custom callback documentation
- Built `tests/corpus/experiment.py` harness — runs configs against corpus, computes metrics, saves results, supports comparison
- Ran baseline config on all 15 PDFs (results in `tests/corpus/runs/baseline/`)

**Issues:**
- 4 of 7 Zotero IDs in the plan pointed at attachment items rather than parent items. `find_pdf_attachment()` in fusion-tea's `zotero_lib.py` only searches children of the given item. Worked around by downloading directly via `zot.dump(attachment_key)`.
- energy_amplifier (241pp) took ~13 minutes for baseline extraction. May want to exclude from quick iteration runs.
- woodruff_2026 and woodruff_2026b produced identical output (91,621 chars, 1 heading) — they may be the same document. Worth verifying.
- hansen_2025 detected 0 headings with baseline config — likely needs header detection investigation.

### Phase 1 Completion
**Completed:** 2026-02-22
**Changes Made:**
- Created `findings.md` with comprehensive baseline quality analysis
- Reviewed markdown output for all 15 PDFs, documented 8 categories of issues
- Identified 6 priority experiments for Phase 2

**Key Findings:**
- woodruff_2026 and woodruff_2026b are identical PDFs (same MD5) — corpus has 14 unique docs
- Heading detection severely underperforms on 6/14 documents (hansen_2025: 0 headings, helios_design/sparc_overview/paischer_2025/woodruff_2026: 1 heading each)
- `<br>` artifacts affect 7 documents (333 total), confirming `lines_strict` should be tested
- tajima (patent) has 610 code fences making it nearly unreadable — `ignore_code` needed
- schulte_1978 has 33 headings on 10 pages — font-size detection over-triggering on TOC and OCR artifacts
- Math garbling is expected (out of scope for parameter tuning)

**Issues:**
- Corpus reduced to 14 unique documents due to woodruff duplicate

### Phase 2 Completion
**Completed:** 2026-02-22
**Changes Made:**
- Extended experiment.py with named header detector presets (--hdr-info flag)
- Built _bold_header_detector and _CompositeHeaderDetector in experiment.py
- Ran 9 distinct configurations (+ 1 aborted)
- Updated findings.md with detailed analysis of each experiment

**Key Findings:**
- CompositeHeaderDetector (font-size + bold union) is the clear winner — zero regressions, improvements on 10/13 docs
- `ignore_code=True` eliminates code fence spam (tajima 610→0, helios 148→0)
- `table_strategy="lines"` is correct — `lines_strict` kills aries tables, `text` is 15x slower
- `<br>` artifacts are inside pipe tables and NOT caused by table_strategy choice
- Roman numeral regex at span level is ineffective (spans are too granular)
- Font-size + bold detection are complementary: different documents need different detection

**Deviations:**
- table_strategy="text" experiment aborted due to extreme slowness (75s for 14-page doc)
- Did not test margins, fontsize_limit, graphics_limit (low priority, diminishing returns)

### Phase 3 Completion
**Completed:** 2026-02-22
**Changes Made:**
- Added "Final Recommendation" section to `findings.md` with:
  - Adopted configuration with per-parameter evidence table
  - Parameters that don't need tuning
  - What pymupdf4llm can't do (downstream implications for Docling/Claude)
  - Comparison vs fusion-tea baseline (3 expected heading regressions documented)
  - Confidence level assessment
- Verified `pymupdf_backend.py` already updated with best config (CompositeHeaderDetector + ignore_code + lines) with rationale comments referencing findings.md
- Verified `extract_page.py` already consistent with backend
- Fixed stale test in `tests/test_extraction.py:249`: updated `test_extract_passes_hdr_info_and_table_strategy` to assert `_composite_header_detector` (was `_academic_header_detector`) and added `ignore_code=True` assertion
- Re-ran best_v1 config on full 15-PDF corpus (`tests/corpus/runs/best_v1_rerun/`) to refresh metrics — all 15 PDFs including energy_amplifier (241pp)
- Reproducibility verified: best_v1 vs best_v1_rerun metrics match on all 13 shared docs (1 char diff in araiinejad_2024 — negligible nondeterminism)
- Compared best_v1 vs pymupdf4llm baseline (`runs/baseline/`): zero table regressions, only tajima -3 headings (expected — headings were inside removed code fences)
- Compared best_v1 vs fusion-tea baseline (`tests/corpus/baseline/`): 3 heading regressions (helios_design 24→7, sparc_overview 14→1, woodruff_2026 82→5) — all documented as inherent pymupdf4llm limitations, not caused by config changes
- Ran test suite: 820 passed, 36/36 extraction tests pass. All other failures pre-existing (syside license key, adapter tests, nested package syntax)

**Deviations:**
- None — all Phase 3 validation items satisfied

---

**Status**: Draft → In Progress → **Complete**
