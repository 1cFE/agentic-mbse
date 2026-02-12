# Implementation Plan — Iteration 1 (Retry 2)

## Status Summary

| Spec | Status | Notes |
|------|--------|-------|
| 01-establish-baselines | DONE (commit 61cffd8) | 7/7 baselines exist, compare.py works, all tests pass |
| 02-custom-header-detector | IN PROGRESS | Task 1 (H1 noise fix) DONE; Task 2 (custom hdr_info callback) next |
| 03-italic-header-promotion | NOT STARTED | No `promote_italic_headers()` function in postprocess.py |

## Current Metrics vs Targets

| Paper | Current heading_count | Target | Current H1 | Target H1 |
|-------|-----------------------|--------|------------|-----------|
| sparc_overview | 5 | ≥ 10 | 1 | — |
| helios_design | 7 | ≥ 20 | 0 | — |
| energy_amplifier | 96 | 30–80 | 64 | ≤ 5 |

## Lessons from Previous Retry

The first retry completed only spec-01 (baselines) and ran out of context/turns before touching specs 02 and 03. Key learnings:
1. The `hdr_info` callback approach is correct — the existing `_academic_header_detector` stub proves the API works
2. The H1 noise rejection fix (`#{2,6}` → `#{1,6}`) is a one-line prerequisite that should be done first
3. Italic header promotion was previously implemented successfully in commit `cf615ae` (now reverted by experiment-init reset) — the approach is proven
4. energy_amplifier takes ~689 seconds to extract — corpus tests are slow; avoid unnecessary re-runs

## Dependency Graph

```
Task 1 (H1 noise fix)  ─────────────────┐
                                          │
Task 2 (custom hdr_info) ────────────────┼──→ Task 4 (update baselines + verify)
                                          │
Task 3 (italic promotion) ──────────────┘
```

Tasks 1, 2, 3 are independent of each other. Task 4 must run after all three.

---

## Task 1: Extend noise header rejection to H1 [spec-02] [DONE]

- **What**: Change `_NOISE_HEADER_RE` regex in `postprocess.py` from `#{2,6}` to `#{1,6}` so that H1-level noise headers (math symbols, equation fragments) are also demoted. Add unit tests for H1 noise rejection.
- **Why**: energy_amplifier has 64 false H1 headings containing math symbols. The current noise rejection skips H1 entirely, so these survive postprocessing. This is a prerequisite for the custom detector (Task 2) — even if the custom detector reduces false H1s, any that slip through must be caught by the noise filter.
- **Files**:
  - `src/agentic_mbse/extraction/postprocess.py` — line 290: `#{2,6}` → `#{1,6}` ✓
  - `tests/test_postprocess.py` — add H1 noise rejection tests ✓
- **Verified by**:
  1. `uv run pytest tests/test_postprocess.py -v` — all 96 tests pass including 7 new H1 tests ✓
  2. `uv run ruff check src/agentic_mbse/extraction/postprocess.py tests/test_postprocess.py` — all checks passed ✓
- **Depends on**: nothing
- **Completed**: Changed regex pattern to include H1 headers, added comprehensive tests for H1 math symbols, equation fragments, brackets, and legitimate titles

---

## Task 2: Implement custom multi-signal `hdr_info` callback [spec-02]

- **What**: Replace the commented-out `_academic_header_detector()` in `pymupdf_backend.py` with an `AcademicHeaderDetector` class and wire it as `hdr_info=` to `pymupdf4llm.to_markdown()`. The class must:
  1. **Pre-scan** the PDF in `__init__` using pymupdf to build a font frequency table (most-frequent font = body font)
  2. **Reject math spans**: text containing `∫∑∏∂√≈≠≤≥±×÷→←∞•=+[]{}` returns `""` (no heading)
  3. **Reject short fragments**: single-word spans under 4 chars that aren't section numbers return `""`
  4. **Detect numbered section headers**: `\d+\.?\s+[A-Z]` or `\d+\.\d+\.?\s+` patterns, confirmed by font differentiation from body text (different family, bold flag, or italic flag). Map depth: top-level → H2, sub-sections → H3, sub-sub → H4
  5. **Detect all-caps short titles**: `ABSTRACT`, `REFERENCES`, etc. → H2
  6. **Detect title text**: largest font on page 1 → H1 (only one per document)
  7. **Default**: return `""` for unrecognized spans (let postprocess promoters handle remaining cases)
- **Why**: spec-02 requires replacing font-size-only detection. The default `IdentifyHeaders` promotes any span larger than the most-frequent font size, which causes:
  - energy_amplifier: 64 false H1s from math display formulas at 13-18pt
  - sparc_overview: misses headers at 10pt NimbusRomNo9-Med (smaller than 10.7pt body)
  - helios_design: misses italic subsections at 10pt (same size as body)
- **Files**:
  - `src/agentic_mbse/extraction/pymupdf_backend.py` — replace `_academic_header_detector` function with `AcademicHeaderDetector` class; uncomment/wire `hdr_info=detector` in `extract()`
  - `tests/test_extraction.py` — update line 248 assertion from `"hdr_info" not in call_kwargs` to verify `hdr_info` IS passed as the detector
- **Verified by**:
  1. `uv run pytest tests/test_extraction.py -v` — updated assertion passes
  2. `uv run pytest tests/test_postprocess.py -v` — no regressions in postprocess
  3. `uv run ruff check src/agentic_mbse/extraction/pymupdf_backend.py`
  4. Quick corpus spot-check on a fast paper (hawker_2020, 14 pages): `uv run pytest tests/test_corpus.py::TestCorpus::test_all_papers_extract_successfully --run-corpus -v` then check `tests/corpus/current/hawker_2020/metrics.json` for heading_count >= 12 (baseline: 14)
- **Depends on**: nothing (independent of Task 1 and 3)

### Implementation Notes

**Approach A (preferred)**: Class with `__call__`:

```python
class AcademicHeaderDetector:
    """Custom header detector using font metadata + section numbering."""

    def __init__(self, doc_path: str):
        """Pre-scan PDF to build font frequency table."""
        import pymupdf
        doc = pymupdf.open(doc_path)
        # Count font occurrences across all pages
        font_counts: dict[str, int] = {}
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        key = span["font"]
                        font_counts[key] = font_counts.get(key, 0) + len(span["text"])
        doc.close()
        # Most-frequent font family = body text
        self.body_font = max(font_counts, key=font_counts.get) if font_counts else ""

    def __call__(self, span, page=None) -> str:
        """Classify a span as heading or not."""
        text = span["text"].strip()
        # ... rejection rules, then detection rules
```

**Critical test update**: `tests/test_extraction.py` line 248 currently asserts `"hdr_info" not in call_kwargs`. This MUST be changed to assert that `hdr_info` IS the detector instance.

**Regression safety**: The custom detector defaults to returning `""` (no heading) for unrecognized spans. This is conservative — the postprocess promoters (`promote_bold_headers`, `promote_plain_headers`, and the new `promote_italic_headers`) will catch anything the upstream detector misses. This layered approach means the detector can be cautious without losing coverage.

---

## Task 3: Implement italic-wrapped numbered header promotion [spec-03]

- **What**: Add `promote_italic_headers()` function to `postprocess.py` and wire it into the orchestrator. Must handle:
  1. `_X.Y. Title text_` → `### X.Y Title text` (entire heading wrapped in italic)
  2. `X.Y. _Title text_` → `### X.Y Title text` (number outside, title in italic)
  - Must only match standalone lines (between blank lines, like `_PLAIN_HEADER_RE` does)
  - Must NOT promote TOC entries (reuse `_is_toc_line()`)
  - Wire into `postprocess()` after `promote_plain_headers()` and before `clean_header_artifacts()`
- **Why**: spec-03 safety net for italic subsections that the upstream detector may miss. helios_design has 15+ italic subsections like `_3.1. Scoping studies_`; sparc_overview has subsections like `4.1. _Full-performance H-mode discharge_`
- **Files**:
  - `src/agentic_mbse/extraction/postprocess.py` — add function + wire into orchestrator
  - `tests/test_postprocess.py` — add unit tests for both italic variants
- **Verified by**:
  1. `uv run pytest tests/test_postprocess.py -v` — all tests pass including new italic tests
  2. `uv run ruff check src/agentic_mbse/extraction/postprocess.py tests/test_postprocess.py`
- **Depends on**: nothing (independent of Tasks 1 and 2)

### Implementation Notes

Two regex patterns needed:

```python
# Fully italic: _3.1. Title text_ (between blank lines)
_ITALIC_HEADER_FULL_RE = re.compile(
    r"(?<=\n\n)_(\d+(?:\.\d+)*)\.?\s+(.+?)_(?=\n\n)",
)

# Partial italic: 3.1. _Title text_ (number outside italic)
_ITALIC_HEADER_PARTIAL_RE = re.compile(
    r"(?<=\n\n)(\d+(?:\.\d+)*)\.?\s+_(.+?)_(?=\n\n)",
)
```

Reuse `_header_depth()` and `_is_toc_line()` already in the file. The replacement function is the same pattern as `_replace_plain_header`.

---

## Task 4: Update baselines, verify targets, fix regressions [spec-01, spec-02, spec-03]

- **What**:
  1. Run full corpus extraction: `uv run pytest tests/test_corpus.py::TestCorpus::test_all_papers_extract_successfully --run-corpus -v`
  2. Verify target metrics against spec requirements:
     - `sparc_overview` heading_count ≥ 10
     - `helios_design` heading_count ≥ 20
     - `energy_amplifier` H1 ≤ 5 and heading_count 30–80
     - Zero math symbols in any heading: `grep -P '^#{1,6} .*[∫∑∏∂√≈≠≤≥±×÷→←∞•]' tests/corpus/current/*/full_document.md`
     - No regressions on hawker_2020, aries_cost_account, hsu_2020, delene_2001 (heading counts ≥ 90% of baseline)
  3. If targets met: copy `tests/corpus/current/*/metrics.json` → `tests/corpus/baseline/*/metrics.json` for all 7 papers
  4. If regressions found: adjust detector/promoters and re-run (do NOT update baselines to accept regressions)
  5. Final verification: `uv run pytest tests/ -v` (full test suite)
  6. Add `heading_regression_pct` overrides to `papers.jsonl` if needed for papers whose heading count changed dramatically (prevents false regression alarms in future iterations)
- **Why**: Baselines must reflect the improved pipeline output. The regression test compares current vs baseline — stale baselines would cause false failures.
- **Files**: `tests/corpus/baseline/*/metrics.json` (7 files), possibly `tests/corpus/papers.jsonl`
- **Verified by**:
  1. `uv run pytest tests/test_corpus.py --run-corpus -v` — all 4 tests pass
  2. `python3 tests/corpus/compare.py` — shows improvements for sparc/helios/energy_amplifier, no regressions for others
  3. `uv run pytest tests/ -v` — full test suite passes
- **Depends on**: Tasks 1, 2, 3

---

## Execution Order

1. **Task 1** (H1 noise fix) — smallest change, immediate impact on energy_amplifier, <5 minutes
2. **Task 2** (custom hdr_info callback) — largest change, highest impact, ~30 minutes
3. **Task 3** (italic header promotion) — medium change, safety net, ~15 minutes
4. **Task 4** (update baselines + verify) — integration task, depends on all above, ~20 minutes (plus ~700s for energy_amplifier extraction)

Tasks 1–3 can be done in any order. Task 4 must be last.

## Risk Notes

- **Regression risk**: The custom `hdr_info` callback replaces `IdentifyHeaders` entirely. Conservative default (return `""`) plus layered postprocess promoters mitigate this. Still, run a quick spot-check on a fast paper (hawker_2020) after Task 2 before proceeding to Task 4.
- **hdr_info API surface**: The existing `_academic_header_detector` stub already uses the `(span, page)` signature, proving the API accepts callables. The class-based approach (`__call__`) is standard Python and should work. If somehow it doesn't, fall back to a closure that captures the pre-scan data.
- **energy_amplifier extraction time**: 241 pages, ~689 seconds. The full corpus test will take ~15 minutes. Don't re-run unnecessarily — run targeted spot-checks on fast papers first.
- **Test update required**: `tests/test_extraction.py:248` asserts `"hdr_info" not in call_kwargs`. This assertion MUST be updated in Task 2 — it will fail as soon as the detector is wired in.
- **Interaction between Tasks 2 and 3**: If the custom detector successfully detects italic headers (because it checks the italic flag), `promote_italic_headers()` will find fewer matches. This is fine — the postprocess promoter is a safety net, not a primary mechanism. The two approaches are complementary, not conflicting. A line already promoted to `## X` by the detector won't match the italic promotion regex.
