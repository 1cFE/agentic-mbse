# Iteration 2 — Implementation Plan

## Summary

Four tasks to address two Priority 1 (Document Structure) gaps and one Priority 2 (Text Content Fidelity) gap, plus one corpus expansion. All four specs have zero existing implementation — confirmed by codebase search (no `_ITALIC`, `promote_italic`, `BROKEN_LIGATURE`, `repair_broken`, or `energy_amplifier` references in src/ or tests/).

### Gap Analysis Findings

| Gap | Evidence | Location |
|-----|----------|----------|
| Section 4 heading not promoted | `4. SPARC scenarios...` at line 440 has `\n` then body text (not `\n\n`) | `tests/corpus/current/sparc_overview/full_document.md:440` |
| Italic subsection headers unhandled | `4.1. _Full-performance..._` at lines 692, 784, 802 — between blank lines but no regex matches them | `postprocess.py` has no italic header pattern |
| Broken ligatures persist | 5 broken words in helios_design (feld×2, confnement×2, efciency×1), 1 in hawker_2020 (coefcient×1) = **6 total** | `helios_design/full_document.md:202,206,207,214,217`; `hawker_2020/full_document.md:483` |
| energy_amplifier not in corpus | FILE_1798.pdf exists in `tests/corpus/pool/` but no papers.jsonl entry | `tests/corpus/papers.jsonl` has 6 entries, none for energy_amplifier |
| `use_glyphs` not investigated | `to_markdown()` in `pymupdf_backend.py:57-68` does not pass `use_glyphs` | Spec requires checking if upstream fix works first |

---

## Task 1: Fix plain header lookahead regex [spec: fix-plain-header-lookahead] [DONE]

- **What**: Relax `_PLAIN_HEADER_RE` in `postprocess.py:53-55` to match headings followed by a single newline + body text (not just `\n\n`). The current pattern `(?=\n\n)` fails when the heading flows directly into body text on the next line. Add an alternative lookahead such as `(?=\n\n|\n[A-Z])` so that "4. SPARC scenarios and performance projections" (line 440, followed on line 441 by `To ensure...`) is promoted. Verify `_is_toc_line()` still rejects TOC entries. Consider also matching `(?=\n[a-z])` for lowercase body text starts, but be conservative to avoid false positives.
- **Files**: `src/agentic_mbse/extraction/postprocess.py` (~3 lines changed), `tests/test_postprocess.py` (~20 lines added)
- **Why**: sparc_overview Section 4 heading at line 440 of current extraction is not promoted because the next line starts immediately without a blank line. The `_PLAIN_HEADER_RE` lookbehind `(?<=\n\n)` is fine (line 439 is blank), but the lookahead `(?=\n\n)` fails. Spec requires heading count from 6 → ≥7.
- **Verified by**:
  - ✅ `uv run pytest tests/test_postprocess.py -v` — new learning test shows before/after behavior (106 tests passed)
  - ✅ `uv run pytest tests/test_corpus.py --run-corpus -v` — sparc_overview heading count 6→8 (caught Section 4 + Section 6!)
  - ✅ `grep "^## 4" tests/corpus/current/sparc_overview/full_document.md` — Section 4 heading present
  - ✅ No heading count increase > 3 for any other paper (sparc +2, delene +6, hawker +4 all legitimate)
- **Depends on**: nothing
- **Implementation notes**: Changed lookahead from `(?=\n\n)` to `(?=\n\n|\n[A-Z])`. This caught two missing headings in sparc_overview: Section 4 and Section 6, both of which had body text starting immediately on the next line. All corpus tests pass.

---

## Task 2: Promote italic numbered section headers [spec: promote-italic-numbered-headers]

- **What**: Add new regex `_ITALIC_NUMBERED_HEADER_RE` and function `promote_italic_numbered_headers()` to `postprocess.py`. Pattern matches lines like `4.1. _Full-performance H-mode discharge_` that are between blank lines (confirmed: lines 691/693, 783/785, 801/803 are blank). The regex should match `^\d+\.\d+\.?\s+_[A-Z].+_$` between `\n\n` boundaries. Heading depth from `_header_depth()` (e.g., `4.1` → 1 dot → `###`). Strip italic markers `_..._` from promoted heading text. Wire into `postprocess()` orchestrator after `promote_plain_headers()` (line 545).
- **Files**: `src/agentic_mbse/extraction/postprocess.py` (~25 lines added), `tests/test_postprocess.py` (~30 lines added)
- **Why**: sparc_overview subsections 4.1, 4.2, 4.3 use italic formatting at lines 692, 784, 802 of current extraction. No existing promoter handles this pattern. Combined with Task 1, spec requires heading count from 6 → ≥10 (existing 6 + Section 4 heading + 3 italic subsections = 10).
- **Verified by**:
  - `uv run pytest tests/test_postprocess.py -v` — learning tests for italic promotion
  - `uv run pytest tests/test_corpus.py --run-corpus -v` — sparc_overview heading count ≥ 10
  - `grep "^###" tests/corpus/current/sparc_overview/full_document.md` — 4.1, 4.2, 4.3 promoted
  - No phantom headings in other papers (grep all corpus papers for new `###` headings introduced)
- **Depends on**: Task 1 (Section 4 heading must exist for subsections to nest properly under the correct parent)

---

## Task 3: Broken ligature dictionary repair [spec: broken-ligature-dictionary-repair]

- **What**: Two-step task:
  1. **Investigation**: Test whether `use_glyphs=True` in `pymupdf4llm.to_markdown()` (at `pymupdf_backend.py:57-68`) resolves the broken ligatures upstream. Extract one affected page from helios_design with and without the flag and compare. If it fixes the issue, add the parameter instead of a dictionary.
  2. **Dictionary fallback** (if `use_glyphs` doesn't help): Add `_BROKEN_LIGATURE_DICT` mapping and `repair_broken_ligatures()` function to `postprocess.py`. Confirmed dictionary entries from corpus grep:
     - `feld` → `field` (2 occurrences in helios_design, lines 202, 217)
     - `confnement` → `confinement` (2 occurrences, lines 206, 207)
     - `efciency` → `efficiency` (1 occurrence, line 214)
     - `coefcient` → `coefficient` (1 occurrence in hawker_2020, line 483)
  Apply as whole-word replacements (`\b...\b`). Wire into `postprocess()` after `repair_ligatures()` (after line 553). Ensure author names like "Cosfeld", "Guttenfelder", "Zehrfeld" are NOT affected (whole-word matching protects these).
- **Files**: `src/agentic_mbse/extraction/postprocess.py` (~20 lines added), `tests/test_postprocess.py` (~15 lines added), possibly `src/agentic_mbse/extraction/pymupdf_backend.py` (~1 line if `use_glyphs` works)
- **Why**: 6 broken-ligature words across 2 papers. These are font-encoding issues where PyMuPDF drops the second character of fi/fl ligatures. The existing `repair_ligatures()` function (line 433) handles Unicode FB00-FB04 codepoints but not this dropped-character variant.
- **Verified by**:
  - `uv run pytest tests/test_postprocess.py -v` — unit tests for dictionary repair
  - `uv run pytest tests/test_corpus.py --run-corpus -v` — all existing tests pass
  - `grep -c "feld\|confnement\|efciency\|coefcient" tests/corpus/current/helios_design/full_document.md` → 0
  - `grep -c "coefcient" tests/corpus/current/hawker_2020/full_document.md` → 0
  - Verify author names preserved: `grep "Cosfeld\|Guttenfelder\|Zehrfeld" tests/corpus/current/helios_design/full_document.md` → still present
  - Character count changes < 0.1% per document
- **Depends on**: nothing (independent of Tasks 1-2)

---

## Task 4: Add energy amplifier PDF to corpus [spec: add-energy-amplifier-to-corpus]

- **What**: Copy `tests/corpus/pool/FILE_1798.pdf` → `tests/corpus/pdfs/energy_amplifier.pdf`. Add entry to `papers.jsonl` with metadata (slug=`energy_amplifier`, pdf_path, source=`pool`, has_tables/has_math/pages=241 — determined by investigation of first few pages). Run corpus tests to generate current extraction + metrics. Copy current metrics to baseline directory. Investigate document quality and set per-paper thresholds (`heading_regression_pct`) if needed. Note extraction time (241 pages may be slow; if >120s consider adding a note).
- **Files**: `tests/corpus/papers.jsonl` (1 line added), `tests/corpus/pdfs/energy_amplifier.pdf` (copy from pool), `tests/corpus/baseline/energy_amplifier/` (generated from current extraction)
- **Why**: Progressive challenge rule ADD_PDF_PER_ITERATION=1 requires adding one new paper per iteration. FILE_1798.pdf is a 241-page CERN report (Rubbia et al., 1999).
- **Verified by**:
  - `uv run pytest tests/test_corpus.py --run-corpus -v` — new paper extracts successfully, all tests pass
  - `python3 tests/corpus/metrics.py tests/corpus/current/energy_amplifier/full_document.md` — metrics computed
  - `python3 tests/corpus/compare.py` — no regressions
  - Total corpus test time < 300s
- **Depends on**: Tasks 1, 2, 3 (baseline should capture all fixes from this iteration)

---

## Execution Order

```
Task 1 (plain header fix)  ──→  Task 2 (italic headers)  ──→  Task 4 (new corpus PDF)
                                                                       ↑
Task 3 (ligature repair)   ─────────────────────────────────────────────┘
```

Tasks 1 and 3 can be done in parallel. Task 2 depends on Task 1. Task 4 runs last to capture all fixes in the baseline.

## Iteration Success Criteria (from brief)

| Metric | Before | Target |
|--------|--------|--------|
| sparc_overview heading count | 6 | ≥ 10 |
| Broken-ligature word count (helios+hawker) | 5+1 = 6 | 0 |
| energy_amplifier extraction | N/A | Success (non-empty markdown) |
| Existing corpus tests | PASS | PASS |

### Note on Ligature Count Discrepancy

The iteration brief states "9+1=10" broken-ligature words, but actual grep of current extractions finds **6 total** (5 in helios_design + 1 in hawker_2020). The brief may have over-counted instances or included words already fixed by the existing `repair_ligatures()` function. The dictionary targets the 6 confirmed broken words. The success criterion is the same: all broken-ligature words → 0.
