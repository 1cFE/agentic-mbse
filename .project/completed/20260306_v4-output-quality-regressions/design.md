# Design: v4 Pipeline Output Quality Regressions

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-02-27 21:30 PST
**Branch:** `doc-ingest-clean`
**Last Commit:** `f4446b2`

## Overview

Four targeted fixes to the v4 extraction pipeline: (1) postprocess cleanup of running headers/page numbers/ligatures on the final merged markdown, (2) GMFT cross-reference step that boosts severity on pages where GMFT found tables pymupdf missed, causing them to route to Claude instead of GMFT_APPEND, (3) equation-fragment detection in the quality gate, and (4) image extraction re-enabled in `extract_pages()`.

## Related Artifacts

- **Spec:** `.project/active/v4-output-quality-regressions/spec.md`
- **Research:** `.project/research/20260227-210000_extraction-quality-failures.md`
- **Pipeline internals:** `docs/extraction-internals.md`
- **Parent design:** `.project/concepts/doc-extraction/design.md`

---

## Research Findings

### Existing Postprocess Functions (postprocess.py)

Three functions needed, all pure `str → str`:

| Function | Mechanism | Scope | Notes |
|----------|-----------|-------|-------|
| `strip_running_headers()` | Frequency counting (threshold=3) across blank-line-delimited blocks | Full document | Cannot run per-page — each header appears once per page |
| `strip_page_numbers()` | Regex: bare `\d{1,4}` and `**\d{1,4}**` between `\n\n...\n\n` | Works per-page or full | No dependency on document context |
| `repair_ligatures()` | Regex: U+FB00–FB04 → ASCII | Works anywhere | No context dependency |

Also available: `normalize_image_paths(md, images_dir)` — replaces absolute paths with relative `images/` paths. Needed after image extraction.

Functions NOT to re-integrate (per spec FR-4): `promote_bold_headers`, `promote_plain_headers`, `reject_noise_headers`, `clean_header_artifacts`.

**References:** `postprocess.py:161-168` (page numbers), `postprocess.py:197-244` (running headers), `postprocess.py:263-269` (ligatures), `postprocess.py:252-255` (image paths).

### Pipeline Step Ordering (pipeline.py)

Current 8-step pipeline:

```
1. arXiv shortcut        → early return
2. Base extraction        → list[PageResult]
3. Table detection        → dict[int, list[DetectedTable]]
3b. Table filter/enhance  → final_tables
4. Quality gate           → list[PageAssessment]
5. Budget allocation      → set[int] claude_pages
6. Claude page enhance    → dict[int, str] claude_results
7. Route and merge        → list[str] merged_pages
8. Assemble              → PipelineResult
```

Step 4 (quality gate) runs AFTER step 3 (table detection), but doesn't receive GMFT results. Steps 3 and 4 are already adjacent — inserting a cross-reference between 4 and 5 is natural.

### Image Handling in pymupdf4llm

The `to_markdown()` API accepts:
- `write_images=True/False` — whether to save embedded images
- `image_path=str` — directory for saved images
- Images are referenced in markdown with absolute paths: `![](absolute/path/to/image.png)`

`extract_pages()` (line 141-150) passes `write_images=False`. The old `extract()` (line 172-188) passes `write_images=True, image_path=str(images_dir)`.

`PipelineConfig` already has `page_image_dir: Path | None = None` for pre-rendered page images for Claude vision. This is a different concept from extracted document images (figures, charts embedded in the PDF). A new field `extracted_images_dir` is needed to avoid confusion between the two.

### Route Page Rule Analysis (quality_gate.py:343-418)

Current rule 5 (lines 410-415):
```python
if has_tables and not assessment.needs_gmft and not assessment.needs_claude:
    has_existing_tables = _has_pipe_tables(page_markdown)
    if not has_existing_tables:
        return PageDecision(assessment.page_num, PageAction.GMFT_APPEND, ...)
```

This rule fires ONLY when `not needs_claude`. If the cross-reference step sets `needs_claude=True` on these pages, rule 5 never fires. Instead, rule 1 (`needs_claude + within_budget → CLAUDE_REPLACE`) handles them. Rule 2 (`needs_claude + !within_budget + needs_gmft + has_tables → GMFT_REPLACE`) handles the over-budget fallback.

No changes needed to `route_page()` itself — the cross-reference step is sufficient.

### Test Patterns

All pipeline tests mock external dependencies (`extract_pages`, `detect_tables_ensemble`, `extract_page_with_claude`, `shutil.which`) while running real business logic (`assess_page`, `route_page`, `allocate_budget`). Helper functions `_page()`, `_table()`, `_cost()` create synthetic typed objects. See `test_pipeline.py:36-112`.

---

## Proposed Design

### Architecture: Four Orthogonal Changes

The four fixes are independent. Each touches a different part of the pipeline and can be implemented/tested separately.

```
                      Changed
                      ┌──────┐
1. arXiv shortcut     │      │
2. Base extraction  ← │ (4)  │  Add images_dir param
3. Table detection    │      │
3b. Table filter      │      │
4. Quality gate     ← │ (3)  │  Add equation-fragment signal
  4b. GMFT xref    ← │ (2)  │  NEW STEP: boost severity
5. Budget allocation  │      │
6. Claude enhance     │      │
7. Route and merge    │      │
  7b. Postprocess   ← │ (1)  │  NEW STEP: cleanup final md
8. Assemble           │      │
                      └──────┘
```

### Component 1: Postprocess Cleanup (FR-1, FR-2, FR-3)

**What:** Apply `strip_page_numbers()`, `strip_running_headers()`, and `repair_ligatures()` to the final merged markdown before computing metrics.

**Where:** `pipeline.py`, between the current page join (line 421) and metrics computation (line 423).

**Interface:**

```python
def _postprocess_final(markdown: str, extracted_images_dir: Path | None = None) -> str:
    """Apply deterministic cleanup to the final merged markdown.

    Selectively applies ONLY the safe str→str transforms from
    postprocess.py. Does NOT apply header promotion/demotion.
    """
```

This is a new private function in `pipeline.py` that calls the three postprocess functions directly (not the `postprocess()` orchestrator, which includes the excluded header promotion logic).

**Data flow:**
```
merged_pages → "\n\n".join() → _postprocess_final() → final_markdown → compute_metrics()
```

**Why not call `postprocess()` directly?** The `postprocess()` orchestrator applies header promotion/demotion functions that the spec explicitly excludes (FR-4). Calling the three safe functions individually avoids re-introducing the promote-then-demote pattern.

**Testing:** Add tests to `test_pipeline.py`:
- Test that running headers are stripped from merged output
- Test that page numbers are stripped
- Test that ligatures are repaired
- Test that existing header formatting is NOT modified (FR-4)

### Component 2: GMFT Cross-Reference (FR-7, FR-8, FR-10)

**What:** After quality gate assessment (step 4) and before budget allocation (step 5), iterate over pages. For any page where GMFT detected tables but pymupdf produced no pipe tables: set `needs_claude=True`, set `needs_gmft=True`, and boost severity by a configurable amount.

**Where:** `pipeline.py`, new step 4b between current steps 4 and 5.

**Interface:**

```python
def _cross_reference_gmft(
    assessments: list[PageAssessment],
    pages: list[PageResult],
    detected_tables: dict[int, list[DetectedTable]],
    severity_boost: float = 1.5,
) -> None:
    """Boost severity on pages where GMFT found tables pymupdf missed.

    Mutates assessments in-place.
    """
```

**Dependency:** Uses `has_pipe_tables()` from `quality_gate.py`. Currently named `_has_pipe_tables()` (private). Rename to `has_pipe_tables()` (drop underscore) to make it a public API, since it's now consumed cross-module. Note: `tables.py` already has a public `has_col_headers()` and `has_br_in_tables()` following this pattern. The function logically belongs in `quality_gate.py` (it's a page-level assessment helper) rather than `tables.py` (which deals with detected table objects).

**Logic:**
```python
for assessment in assessments:
    pnum = assessment.page_num
    if pnum not in detected_tables:
        continue
    page_md = pages[pnum].markdown
    if has_pipe_tables(page_md):
        continue  # pymupdf produced pipe tables — no structural failure
    # GMFT found tables but pymupdf produced only flat text
    assessment.needs_claude = True
    assessment.needs_gmft = True  # fallback if Claude over budget
    assessment.severity += severity_boost
    assessment.reasons.append(
        f"GMFT_XREF: GMFT found {len(detected_tables[pnum])} table(s) "
        f"but pymupdf produced no pipe tables (severity +{severity_boost})"
    )
```

**Why mutate in-place?** Matches the existing heading anomaly pattern at `pipeline.py:299-302`, which also mutates assessments after the initial quality gate pass.

**Effect on routing:** After the cross-reference, these pages have `needs_claude=True`. Budget allocation (step 5) selects them by severity. `route_page()` rule 1 fires (`needs_claude + within_budget → CLAUDE_REPLACE`). If over budget, rule 2 fires (`needs_claude + !within_budget + needs_gmft + has_tables → GMFT_REPLACE`). Rule 5 never fires because `needs_claude` is True.

**Spec FR-8/FR-9 reconciliation:** The spec describes the over-budget fallback as "GMFT_APPEND" (FR-8), but the actual routing rule 2 produces GMFT_REPLACE. In practice these are equivalent here: `replace_tables()` calls `strip_pipe_tables()` (a no-op since pymupdf produced no pipe tables) then `insert_tables_at_end()`. The net effect is append. FR-9 ("no duplicate table data") is satisfied because the primary path is CLAUDE_REPLACE (which fully replaces the page, eliminating garbled text). The GMFT_REPLACE fallback only fires when Claude budget is exhausted — in that degraded case, the garbled flat-text remains alongside the appended table, which is an accepted trade-off documented in the spec.

**Configuration:** Add `gmft_xref_severity_boost: float = 1.5` to `QualityGateConfig`. Add a docstring note that this field is consumed by `_cross_reference_gmft()` in `pipeline.py`, not by `quality_gate.py` itself — it lives here because it's a quality-assessment threshold alongside the other gate thresholds. The value 1.5 was chosen to outweigh single-strikethrough pages (severity 0.5) but not pages with heavy garbling (severity 2.0+). This means GMFT-missed-table pages compete fairly with character-garbling pages for Claude budget.

**Testing:** Add tests to `test_pipeline.py`:
- Page with GMFT tables + no pymupdf pipe tables → needs_claude=True, severity boosted
- Page with GMFT tables + pymupdf pipe tables → no change (pymupdf got it right)
- Page with no GMFT tables → no change
- End-to-end: GMFT-missed-table page within budget → CLAUDE_REPLACE action
- End-to-end: GMFT-missed-table page over budget → GMFT_REPLACE action

### Component 3: Equation-Fragment Detection (FR-11)

**What:** Add a new signal to the quality gate that detects equation rendering failures — standalone equation numbers like `(2.2)` preceded by short lines with italic text fragments.

**Where:** `quality_gate.py`, new function `_assess_equation_fragments()` called from `assess_page()`.

**Interface:**

```python
def _assess_equation_fragments(md: str) -> tuple[float, list[str]]:
    """Detect equation-fragment rendering failures.

    Looks for isolated equation numbers (e.g., "(2.2)") preceded by
    short lines with heavy italic content — a pattern pymupdf4llm
    produces when it fails to render equations as LaTeX.

    Returns (severity_score, reasons).
    """
```

**Heuristic:**

```python
# Pattern 1: Standalone equation number on its own line
_EQUATION_NUMBER_RE = re.compile(r"^\s*\((\d+(?:\.\d+)?)\)\s*$")

# Pattern 2: Short italic fragment lines (< 60 chars, contains _..._)
# e.g., "_C_ = _CEEDB_" or "_Pnew_"
_ITALIC_MARKER_RE = re.compile(r"_[^_]+_")
```

Algorithm:
1. Find lines matching `_EQUATION_NUMBER_RE`
2. For each match, look at the preceding 5 non-blank lines
3. Count how many are short (< 60 chars) and contain italic markers (`_..._`)
4. If ≥ 2 such lines precede the equation number → severity +1.0

**Why severity 1.0?** Matches the `math_severity_threshold` default (1.0), ensuring a standalone equation fragment is enough to flag a page for Claude.

**False positive mitigation:**
- Only triggers on standalone equation numbers (not inline `(2.2)` in paragraph text)
- Requires ≥ 2 short italic fragment lines in the vicinity
- Normal italic text in paragraphs is long (> 60 chars) and doesn't precede standalone equation numbers

**Testing:** Add tests to `test_quality_gate.py`:
- Equation fragment pattern (short italic lines + `(2.2)`) → severity ≥ 1.0
- Normal italic text in paragraph → no signal
- Equation number inline in paragraph text → no signal
- Equation number without preceding italic fragments → no signal

### Component 4: Image Extraction (FR-5, FR-6)

**What:** Re-enable image extraction in `extract_pages()` by adding an `images_dir` parameter and passing it through to pymupdf4llm. Normalize image paths in the postprocess step.

**Where:** `pymupdf_backend.py` (add parameter), `pipeline.py` (pass through), `extract_cli.py` (create directory), postprocess step (normalize paths).

**Changes:**

1. **`PipelineConfig`** (`pipeline.py`): Add `extracted_images_dir: Path | None = None`. Named distinctly from the existing `page_image_dir` (pre-rendered page PNGs for Claude vision) to avoid confusion — `extracted_images_dir` is for document-embedded figures/charts saved by pymupdf4llm.

2. **`extract_pages()`** (`pymupdf_backend.py:124-157`): Add `extracted_images_dir: Path | None = None` parameter. When provided, pass `write_images=True, image_path=str(extracted_images_dir)` to `to_markdown()`.

    ```python
    def extract_pages(
        pdf_path: Path,
        extracted_images_dir: Path | None = None,
    ) -> list[PageResult]:
    ```

    In the `to_markdown()` call:
    ```python
    chunks = to_markdown(
        str(pdf_path),
        write_images=extracted_images_dir is not None,
        image_path=str(extracted_images_dir) if extracted_images_dir else None,
        ...
    )
    ```

3. **`extract_pdf()`** (`pipeline.py`): Pass `config.extracted_images_dir` to `extract_pages()`. In the postprocess step, call `normalize_image_paths()` when `extracted_images_dir` is set.

4. **`cmd_extract()`** (`extract_cli.py`): Create `output_dir / "images"` before calling `extract_pdf()`. Pass it via config.

    ```python
    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / "images"
    images_dir.mkdir(exist_ok=True)
    config = PipelineConfig(
        ...,
        extracted_images_dir=images_dir,
    )
    result = extract_pdf(doc, config=config)
    ```

    Remove the duplicate `output_dir.mkdir()` that currently happens after extraction.

**Image path flow:**
```
pymupdf4llm writes: ![](/absolute/path/to/output_dir/images/doc-0-0.png)
    ↓
Pages go through pipeline (quality gate, Claude, merge)
    ↓
_postprocess_final() calls normalize_image_paths(md, extracted_images_dir)
    ↓
Output: ![](images/doc-0-0.png)
```

**Claude-replaced pages:** When Claude replaces a page, the pymupdf4llm image references for that page are lost (Claude produces text placeholders like `[Figure N: caption]`). The extracted image files remain on disk but are unreferenced. This is acceptable — orphan images are harmless and the alternative (passing images to Claude for re-linking) adds complexity for marginal benefit.

**Testing:**
- Test that `extract_pages()` with `extracted_images_dir` passes `write_images=True` to pymupdf4llm (mock `to_markdown`)
- Test that `extract_pages()` without `extracted_images_dir` passes `write_images=False` (backward compat)
- Test that `_postprocess_final()` normalizes absolute image paths to relative
- CLI test: verify `PipelineConfig.extracted_images_dir` is set when output dir exists

---

## Potential Risks

| Risk | Likelihood | Mitigation |
|------|:---:|-----------|
| Equation-fragment heuristic has false positives on normal italic text | Low | Requires standalone equation number + ≥2 short italic lines — unlikely in running paragraphs |
| GMFT cross-reference makes too many pages compete for Claude budget, exhausting it | Medium | 1.5 severity is moderate. Budget allocation already rank-orders by severity. Worst case: some lower-priority pages don't get Claude. |
| Image extraction changes pymupdf4llm timing/behavior | Low | `write_images` is a well-tested parameter. Old pipeline uses it. |
| strip_running_headers removes legitimate content that happens to repeat | Low | Threshold=3, only short standalone paragraphs. Same function used successfully by old pipeline. |

---

## Integration Strategy

All four changes integrate into the existing pipeline without restructuring:

- **Components 1 & 4** (postprocess + images): New step 7b between merge and assemble. No changes to any existing step.
- **Component 2** (GMFT xref): New step 4b between quality gate and budget allocation. No changes to quality gate or route_page.
- **Component 3** (equation fragments): New signal inside `assess_page()`. Follows existing pattern of other signals.
- **route_page() is unchanged.** The cross-reference step modifies assessments so existing routing rules produce the correct actions.

---

## Validation Approach

### Automated Testing

Each component gets unit tests following existing patterns:

| Component | Test File | New Tests |
|-----------|-----------|:---------:|
| 1. Postprocess | `test_pipeline.py` | ~5 |
| 2. GMFT xref | `test_pipeline.py` + `test_quality_gate.py` | ~5 |
| 3. Equation fragments | `test_quality_gate.py` | ~4 |
| 4. Image extraction | `test_pipeline.py` + `test_extract_cli.py` | ~4 |

### Manual Verification

Re-extract the TEA cost analysis document and verify acceptance criteria:
```bash
uv run agentic-mbse extract --force --model sonnet \
    "/home/reid/1cfe/fusion-tea/knowledge/raw/Araiinejad and Shirvan - 2025 - ..."
```

Check:
- `output.md`: zero running headers, zero bare page numbers
- `decisions.json`: pages 2, 3, 6, 8, 9, 10 routed to `claude_replace` (not `gmft_append`)
- `cost.json`: total < $2.00
- `images/`: PNG files exist
- `output.md`: contains `![](images/...)` references
- Table 2: rendered as pipe table, no garbled flat-text duplication
- Equation 2.2: rendered as LaTeX by Claude

### Regression Check

```bash
uv run pytest tests/ -x
```

---

## Files Changed Summary

| File | Changes |
|------|---------|
| `pipeline.py` | Add `extracted_images_dir` to config, add `_cross_reference_gmft()` step 4b, add `_postprocess_final()` step 7b, pass extracted_images_dir to extract_pages |
| `quality_gate.py` | Add `gmft_xref_severity_boost` to config (with cross-module usage comment), rename `_has_pipe_tables` → `has_pipe_tables`, add `_assess_equation_fragments()`, call it from `assess_page()` |
| `pymupdf_backend.py` | Add `extracted_images_dir` parameter to `extract_pages()`, conditionally enable `write_images` |
| `extract_cli.py` | Create `output_dir/images/` before extraction, pass `extracted_images_dir` to config |
| `test_pipeline.py` | Tests for postprocess, GMFT xref, image handling |
| `test_quality_gate.py` | Tests for equation fragment detection, `has_pipe_tables` (now public) |
| `test_extract_cli.py` | Test config mapping for extracted_images_dir |

---

**Next Step:** After approval → `/_my_plan` for implementation phasing
