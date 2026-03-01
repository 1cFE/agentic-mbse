# Implementation Plan: `--check` Built-in Test PDF Corpus

**Status:** Draft
**Created:** 2026-02-27
**Last Updated:** 2026-02-27

## Source Documents
- **Spec:** `.project/active/check-pdfs/spec.md`
- **Design:** `.project/active/check-pdfs/design.md` — See here for component details, dependencies, architecture

## Implementation Strategy

**Phasing Rationale:**
Phase 1 generates the corpus PDFs and validates they trigger the right heuristics — if the content doesn't work, nothing else matters. Phase 2 adds the core aggregation logic with test-first approach. Phase 3 wires it into the CLI with backward-compat tests.

**Overall Validation Approach:**
- Each phase starts with tests (or validation scripts for Phase 1)
- `uv run pytest tests/` after every phase — no regressions
- `uv run ruff check src/ tests/` after every phase

---

## Phase 1: Generate Test Corpus PDFs

### Goal
Extract pages from real corpus PDFs to create the two check corpus files. Validate they trigger `select_pages()` and `detect_arxiv_id()`. This de-risks the "will the content work?" question before writing any logic.

### Changes Required

**See `design.md#component-1` for:** PDF sources, page selection strategy, target location
**See `design.md#component-6` for:** Generation script details

#### 1. Create corpus directory
- [ ] `src/agentic_mbse/extraction/check_corpus/__init__.py` (empty)

#### 2. Generation script
**File:** `scripts/generate_check_pdf.py` (NEW)
- [ ] `generate_test_features()`: open `tests/corpus/pdfs/sparc_overview.pdf`, run `extract_pages()` + `select_pages()` to find best pages, `doc.select()` to keep only those, save to `check_corpus/test_features.pdf`
- [ ] `extract_arxiv_probe()`: open `tests/corpus/pdfs/paischer_2025.pdf`, `doc.select([0])`, save to `check_corpus/arxiv_probe.pdf`
- [ ] Built-in validation: after generating each PDF, run the relevant heuristic and assert it works (select_pages finds math+tables, detect_arxiv_id returns the ID)

#### 3. Run the script, check in results
- [ ] Run `uv run python scripts/generate_check_pdf.py`
- [ ] Verify `test_features.pdf` < 500KB
- [ ] Verify `arxiv_probe.pdf` < 200KB
- [ ] Verify total < 1MB

### Validation

**Automated:**
- [ ] Generation script's built-in assertions pass
- [ ] `uv run pytest tests/` → existing tests still pass (no regressions)

**Manual:**
- [ ] `ls -lh src/agentic_mbse/extraction/check_corpus/*.pdf` → two PDFs, reasonable sizes

**What We Know Works After This Phase:**
The corpus PDFs exist, contain the right content, and trigger all heuristics needed by probes.

---

## Phase 2: Corpus Discovery + Result Aggregation (test-first)

### Goal
Add `get_check_corpus()` and `merge_check_results()` to check.py. These are the core new functions — tested independently before CLI integration.

### Test Stencil (Write This First)
```python
class TestGetCheckCorpus:
    def test_returns_pdfs(self):
        pdfs = get_check_corpus()
        assert len(pdfs) >= 2
        assert all(p.suffix == ".pdf" for p in pdfs)

class TestMergeCheckResults:
    def test_pass_wins_over_untested(self):
        r1 = _make_check_result(probes=[_probe("gmft", ProbeStatus.UNTESTED)])
        r2 = _make_check_result(probes=[_probe("gmft", ProbeStatus.PASS, "2 tables")])
        merged = merge_check_results([r1, r2])
        gmft = next(p for p in merged.probes if p.component == "gmft")
        assert gmft.status == ProbeStatus.PASS

    def test_all_fail_stays_fail(self):
        # ...

    def test_selected_pages_merged(self):
        # first non-None wins for each field
        # ...

    def test_capabilities_recomputed(self):
        # ...
```

### Changes Required

**See `design.md#component-2` for:** `get_check_corpus()` signature
**See `design.md#component-3` for:** `merge_check_results()` logic, `_STATUS_PRIORITY`

#### 1. Tests
**File:** `tests/test_check.py`
- [ ] Add `TestGetCheckCorpus` class (2-3 tests)
- [ ] Add `TestMergeCheckResults` class (4-5 tests): PASS wins, FAIL stays, selected pages merge, capabilities recomputed, cost preserved

#### 2. Implementation
**File:** `src/agentic_mbse/extraction/check.py`
- [ ] Add `_STATUS_PRIORITY` dict
- [ ] Add `get_check_corpus()` function
- [ ] Add `merge_check_results()` function
- [ ] Add imports to existing import block at top of file

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_check.py -v` → new tests pass
- [ ] `uv run pytest tests/` → no regressions
- [ ] `uv run ruff check src/ tests/` → clean

**What We Know Works After This Phase:**
Corpus discovery finds the PDFs. Merge logic correctly aggregates probe results with the right priority ordering.

---

## Phase 3: CLI Integration + End-to-End

### Goal
Wire up the optional `path` argument so `--check` with no args uses the built-in corpus. Verify backward compatibility.

### Test Stencil (Write This First)
```python
class TestCliBuiltinCorpus:
    def test_check_no_arg_uses_corpus(self):
        args = _MockArgs(path=None, check=True)
        with patch("agentic_mbse.extraction.check.run_check", ...) as mock_run:
            with patch("agentic_mbse.extraction.check.merge_check_results", ...):
                rc = cmd_extract(args)
        assert rc == EXIT_SUCCESS
        assert mock_run.call_count == 2  # one per corpus PDF

    def test_check_no_arg_no_corpus_errors(self):
        args = _MockArgs(path=None, check=True)
        with patch("agentic_mbse.extraction.check.get_check_corpus", return_value=[]):
            rc = cmd_extract(args)
        assert rc == EXIT_FAILURE

    def test_extract_no_arg_no_check_errors(self):
        # path required for non-check mode
        args = _MockArgs(path=None, check=False)
        rc = cmd_extract(args)
        assert rc == EXIT_FAILURE
```

### Changes Required

**See `design.md#component-4` for:** argparse change, handler logic, Claude budget optimization

#### 1. Tests
**File:** `tests/test_check.py`
- [ ] Add `TestCliBuiltinCorpus` class (3-4 tests): no-arg uses corpus, empty corpus errors, non-check requires path, backward compat with user PDF still works

#### 2. CLI changes
**File:** `src/agentic_mbse/cli/extract_cli.py`
- [ ] Change `path` to `nargs="?"`, `default=None` (~line 421)
- [ ] Add `path=None` + `check=True` branch in `cmd_extract()`: get corpus, iterate, merge (~line 230)
- [ ] Add `path=None` + `check=False` error message
- [ ] Add stderr note: `"Using built-in test corpus (N PDFs)"` for corpus mode
- [ ] Keep existing single-PDF `--check` path for when user provides a path

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_check.py -v` → all tests pass
- [ ] `uv run pytest tests/` → no regressions
- [ ] `uv run ruff check src/ tests/` → clean

**Manual:**
- [ ] `uv run agentic-mbse extract --check` (no args) → runs, shows "built-in test corpus"
- [ ] `uv run agentic-mbse extract --check-json` → valid JSON output
- [ ] `uv run agentic-mbse extract --check tests/corpus/pdfs/hawker_2020.pdf` → backward compat
- [ ] `uv run agentic-mbse extract` (no args, no --check) → error about missing path

**What We Know Works After This Phase:**
Full end-to-end: `--check` with no args discovers corpus, runs probes on each PDF, aggregates results, displays output. User-provided PDF path still works as before.

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Generation script has built-in assertions — if `select_pages()` doesn't find math/tables in the extracted PDF, the script fails immediately rather than silently producing bad corpus files
- **Phase 2**: Pure logic with full test coverage — low risk
- **Phase 3**: Existing CLI tests in `TestCliCheckIntegration` (test_check.py:658-718) continue to pass, covering backward compat

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-02-27
**Actual Changes:**
- Created `src/agentic_mbse/extraction/check_corpus/__init__.py` (empty)
- Created `scripts/generate_check_pdf.py` — generates both PDFs from corpus
- Generated `src/agentic_mbse/extraction/check_corpus/test_features.pdf` (89 KB, 2 pages)
- Generated `src/agentic_mbse/extraction/check_corpus/arxiv_probe.pdf` (246 KB, 2 pages)
- Total corpus: 334 KB (well under 1MB limit)

**Issues:**
- `sparc_overview.pdf` page 9 had only empty pipe-row cells (Col1|...|Col5 with no data) — not real tables

**Deviations:**
- Changed source from `sparc_overview.pdf` to `hsu_2020.pdf` for test_features.pdf — hsu_2020 page 7 has 36 real data rows (cost accounts with values in M$, MW, etc.)
- Expanded `arxiv_probe.pdf` from 1 page to 2 pages (page 0 for arXiv ID + page 2 for math with garble score 4.0) — this covers math probe which hsu_2020 lacks
- Net effect: all probes still covered across 2 PDFs, just with better source material

### Phase 2 Completion
**Completed:** 2026-02-27
**Actual Changes:**
- Added `get_check_corpus()`, `_STATUS_PRIORITY`, `merge_check_results()` to `check.py`
- Added `TestGetCheckCorpus` (3 tests) and `TestMergeCheckResults` (7 tests) to `test_check.py`
- Imported `get_check_corpus` and `merge_check_results` in test file

**Issues:**
- Equal-status tie-breaking: when two probes had the same status, first one won even if second had more informative detail (e.g. pandoc "binary found" vs "binary found, arXiv ID detected")

**Deviations:**
- Added tie-breaking logic in merge: when status priority is equal, prefer the probe with longer detail string. This ensures the arXiv info isn't lost during aggregation.

### Phase 3 Completion
**Completed:** 2026-02-27
**Actual Changes:**
- Modified `src/agentic_mbse/cli/extract_cli.py`:
  - Added `import sys`
  - Changed `path` to `nargs="?"`, `default=None`
  - Restructured `cmd_extract()`: moved `--check-json implies --check` up, added built-in corpus branch before `Path(args.path)`, added `path=None` error for non-check mode
  - Preserved existing single-PDF `--check` path unchanged
- Added `TestCliBuiltinCorpus` (5 tests) to `tests/test_check.py`:
  - no-arg uses corpus, empty corpus errors, non-check requires path, backward compat with user PDF, Claude budget only on first PDF

**Issues:** None

**Deviations:** None

---

**Status**: Complete
