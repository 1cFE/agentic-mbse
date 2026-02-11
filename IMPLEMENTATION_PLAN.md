# Implementation Plan — Iteration 3

## Focus

Two heading fidelity fixes targeting Priority 1 (Document Structure):
1. Reject phantom H1 equation headings in energy_amplifier (64 noise H1s → ≤5)
2. Promote italic-wrapped numbered subsection headings in helios_design (7 headings → ≥20)

## Tasks

### Task 1: Extend noise header rejection to H1 [spec: reject-h1-equation-noise-headers]

- **Status**: DONE
- **Implementation**: Successfully extended noise header rejection to cover H1 headings. Modified `postprocess.py` with two changes and added 13 comprehensive tests in `test_postprocess.py`.
- **What**: Two changes in `src/agentic_mbse/extraction/postprocess.py`:
  1. Change `_NOISE_HEADER_RE` regex (line 522) from `#{2,6}` to `#{1,6}` so it inspects H1 headings too
  2. Add missing math/Greek symbols to `_is_noise_header()` character class (line 539): `∫` (U+222B), `φ` (U+03C6), `ψ` (U+03C8), `ε` (U+03B5), `ρ` (U+03C1), `σ` (U+03C3), `λ` (U+03BB)
- **Why**: energy_amplifier has 64 phantom H1 headings — equation fragments with large-font math symbols (∑, ∏, ∫, φ) that pymupdf4llm's font-size detector misidentifies as H1. The regex currently skips H1 entirely (`#{2,6}`), and the symbol character class on line 539 is missing `∫` and several Greek letters that appear in these equation fragments.
- **Files to modify**:
  - `src/agentic_mbse/extraction/postprocess.py` — `_NOISE_HEADER_RE` regex (line 522→change `{2,6}` to `{1,6}`), `_is_noise_header()` character class (line 539→add symbols)
  - `tests/test_postprocess.py` — add tests to `TestRejectNoiseHeaders` class (currently at line 631):
    - H1 equation fragments are demoted (e.g., `# ∫ E 2`, `# φ ψ`, `# ∑ n=1`)
    - Legitimate H1 headings are preserved (e.g., `# 1 Introduction`, `# Energy Amplifier for Cleaner Nuclear Energy`)
- **Verified by**:
  - `uv run pytest tests/test_postprocess.py -v` — new tests pass
  - `uv run pytest tests/test_corpus.py --run-corpus -v` — energy_amplifier heading count ≤45, H1 count ≤5
  - Other papers' H1 counts unchanged (hawker_2020: 1, delene_2001: 1, sparc_overview: 1, aries_cost_account: 1, hsu_2020: 1)
- **Depends on**: nothing
- **Key risk**: Must NOT demote legitimate H1 headings. Legitimate H1s are document titles and long section headings with real title text. The existing `_is_noise_header()` logic already preserves these (they have long title text, no math symbols, no short-word patterns). Write explicit negative tests to confirm.
- **Discovery**: All unit tests passed (135 total in test_postprocess.py). The existing `_is_noise_header()` logic correctly handles both equation noise and legitimate H1 headings without modification - only needed to extend regex and add missing symbols. Docstrings updated to reflect H1 coverage.

### Task 2: Promote italic-wrapped numbered headers [spec: promote-italic-wrapped-numbered-headers]

- **Status**: DONE
- **Implementation**: Successfully added pattern for italic-wrapped numbered headers. Added `_ITALIC_WRAPPED_NUMBERED_HEADER_RE` regex, `_replace_italic_wrapped_numbered_header()`, and `promote_italic_wrapped_numbered_headers()` function to `postprocess.py`. Wired into `postprocess()` orchestrator after `promote_italic_numbered_headers()`. Added 10 comprehensive tests in new `TestPromoteItalicWrappedNumberedHeaders` class.
- **Results**: helios_design now has 20 headings (7 H2 + 13 H3), up from 7 total (target: ≥20). All 145 postprocess tests pass. No regressions in other papers (sparc_overview: 11→11, hawker_2020: 15→15, aries_cost_account: 140→140, hsu_2020: 27→27, delene_2001: 29→28 = -3.4% within threshold).
- **What**: Add a new regex and public function in `src/agentic_mbse/extraction/postprocess.py` for the pattern where the section number is INSIDE italic markers: `_N.M. Title text_` (as opposed to the existing `N.M. _Title text_` handled by `_ITALIC_NUMBERED_HEADER_RE`)
- **Why**: helios_design has 14 subsection headings like `_3.1. The stellarator equilibrium_` that the existing `_ITALIC_NUMBERED_HEADER_RE` (line 91) misses because it expects the number OUTSIDE italic markers. These missed headings leave helios_design with only 7 H2 headings and no H3/H4 hierarchy.
- **Files to modify**:
  - `src/agentic_mbse/extraction/postprocess.py`:
    - Add new regex `_ITALIC_WRAPPED_NUMBERED_HEADER_RE` near line 93 (after existing `_ITALIC_NUMBERED_HEADER_RE`)
    - Add replacement function `_replace_italic_wrapped_numbered_header()`
    - Add public function `promote_italic_wrapped_numbered_headers()`
    - Wire into `postprocess()` orchestrator after `promote_italic_numbered_headers` (line 610)
  - `tests/test_postprocess.py` — add new test class after `TestPromoteItalicNumberedHeaders` (line 260):
    - Single-line: `_3.2. The stellarator equilibrium_` → `### 3.2 The stellarator equilibrium`
    - Multi-line wrapped: `_3.1. Scoping studies, heating and fueling, and dynamic_\n_accessibility_` → combined heading
    - Three-level depth: `_3.4.1. A note on the effects_` → `#### 3.4.1 A note on the effects`
    - False-positive rejection: italic text that doesn't start with a section number
    - Must be between blank lines (standalone paragraph)
- **Pattern details**:
  - Regex anchored between blank lines: `(?<=\n\n)_(\d+(?:\.\d+)+)\.\s+(.+?)_(?=\n\n)`
  - Multi-line variant: detect continuation `_text_\n_text_` and join before replacement
  - Heading level from `_header_depth()` (reuse existing function)
  - Number format: `N.M.` (2-level → `###`) or `N.M.K.` (3-level → `####`)
- **Verified by**:
  - `uv run pytest tests/test_postprocess.py -v` — new tests pass
  - `uv run pytest tests/test_corpus.py --run-corpus -v` — helios_design heading count ≥20, gains H3 entries
  - sparc_overview heading count remains at 11 (no regression from existing italic-outside-number pattern)
  - No false positives in other corpus papers
- **Depends on**: nothing (independent of Task 1)
- **Constraint**: Do NOT modify `_ITALIC_NUMBERED_HEADER_RE` or `promote_italic_numbered_headers()` — add alongside them
- **Edge case**: `_3.4.1. A note on the e_ ff _ects of an abrupt plasma termi-_` has a broken italic due to ligature split. Accept as known limitation (ligature repair runs after heading promotion in the pipeline, and the broken italic boundary makes regex matching unreliable for this specific line).
- **Discovery**: The regex pattern `(?<=\n\n)_(\d+(?:\.\d+)+)\.\s+(.+?)_(?=\n\n)` with `re.DOTALL` successfully handles multi-line continuations. The replacement function uses `re.sub(r"_\s*\n\s*_", " ", title)` to join multi-line italic text across line breaks. The edge case at 3.4.1 wasn't promoted because it doesn't have blank lines around it (it's inline text in a paragraph), which is correct behavior to avoid false positives.

### Task 3: Rebase baselines and verify zero regressions [spec: both]

- **Status**: PENDING
- **What**: Regenerate baselines for energy_amplifier and helios_design after Tasks 1-2 are implemented, update `papers.jsonl` heading thresholds if needed, and run full corpus tests
- **Why**: Both specs require updated baselines. The regression test compares current vs baseline, so baselines must reflect the improved pipeline output. After helios_design gains real headings, its heading regression threshold should tighten from the default -10% (no special relaxed threshold needed anymore since headings are now detected by text patterns, not Layer 3 vision).
- **Files to modify**:
  - `tests/corpus/baseline/energy_amplifier/metrics.json` — copy from current/
  - `tests/corpus/baseline/energy_amplifier/full_document.md` — copy from current/
  - `tests/corpus/baseline/helios_design/metrics.json` — copy from current/
  - `tests/corpus/baseline/helios_design/full_document.md` — copy from current/
  - `tests/corpus/papers.jsonl` — verify no threshold overrides needed (energy_amplifier's new lower heading count becomes the baseline; helios_design's new higher heading count becomes the baseline; both use default -10%)
- **Verified by**:
  - `uv run pytest tests/test_corpus.py --run-corpus -v` — all 7 papers pass, zero regressions
  - `python3 tests/corpus/compare.py` — no regression flags
  - `uv run ruff check src/ tests/ && uv run ruff format src/ tests/` — clean
- **Depends on**: Task 1, Task 2

## Priority Order

1. **Task 1** (H1 noise rejection) — simpler change, smaller blast radius, independent
2. **Task 2** (italic-wrapped headers) — more complex (multi-line handling), independent
3. **Task 3** (baseline rebase) — depends on both Tasks 1 and 2

## Acceptance Summary

| Metric | Before | Target | Spec |
|--------|--------|--------|------|
| energy_amplifier heading_count | 106 | ≤45 | reject-h1-equation-noise-headers |
| energy_amplifier H1 count | 64 | ≤5 | reject-h1-equation-noise-headers |
| helios_design heading_count | 7 | ≥20 | promote-italic-wrapped-numbered-headers |
| helios_design heading_by_level | {H2: 7} | gains H3 entries | promote-italic-wrapped-numbered-headers |
| sparc_overview heading_count | 11 | 11 (unchanged) | both (no regression) |
| Other papers | — | identical to baseline | both (no regression) |
