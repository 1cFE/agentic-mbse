# Implementation Plan: `agentic-mbse extract --check`

**Status:** Complete
**Created:** 2026-02-27
**Last Updated:** 2026-02-27

## Source Documents
- **Spec:** `.project/active/extract-check/spec.md`
- **Design:** `.project/active/extract-check/design.md` — See here for component details, function signatures, data types, architecture

## Implementation Strategy

**Phasing Rationale:**
Phase 1 builds the entire core module (types + page selection + all 6 probes) because the probes are independent, small functions that all follow the same pattern. Testing them together validates the cross-module imports and probe isolation in one pass. Phase 2 adds aggregation and formatting on top of proven probes. Phase 3 wires into the CLI — the lowest-risk step since all logic is already tested.

**Overall Validation Approach:**
- Each phase starts with tests
- `uv run pytest tests/test_check.py -v` after each phase
- `uv run pytest tests/ -v` for regression check after each phase
- `uv run ruff check src/ tests/` for linting

---

## Phase 1: Core Module — Types, Page Selection, All 6 Probes

### Goal
Create `check.py` with all data types, page selection logic, and all 6 probe functions. This is the riskiest phase — it validates that private cross-module imports work and that each probe correctly distinguishes PASS/FAIL/NOT_INSTALLED/UNTESTED/SKIPPED.

### Test Stencil (Write This First)

```python
# tests/test_check.py — Phase 1 tests
from agentic_mbse.extraction.check import (
    ProbeStatus, ProbeResult, SelectedPages,
    select_pages, probe_pymupdf, probe_gmft, probe_img2table,
    probe_docling, probe_pandoc, probe_claude,
)
from agentic_mbse.extraction.types import PageResult

class TestSelectPages:
    def test_finds_math_page(self):
        """Page with highest math garble score >= 1.0 selected."""
        pages = [
            PageResult(0, "# Title\n\nClean text."),
            PageResult(1, "# Math\n\n~~garbled~~ ~~math~~ ~~eq~~ \ufffd\ufffd"),
        ]
        selected = select_pages(pages)
        assert selected.math == 1

    def test_no_math_returns_none(self):
        """No pages with severity >= 1.0 → math is None."""
        pages = [PageResult(0, "# Clean\n\nNo math here.")]
        selected = select_pages(pages)
        assert selected.math is None

    def test_finds_table_page(self):
        pages = [
            PageResult(0, "# Title\n\nNo tables."),
            PageResult(1, "# Data\n\n| A | B |\n|---|---|\n| 1 | 2 |"),
        ]
        selected = select_pages(pages)
        assert selected.tables == 1

    def test_no_tables_returns_none(self):
        pages = [PageResult(0, "# Clean\n\nNo tables.")]
        selected = select_pages(pages)
        assert selected.tables is None

    def test_always_includes_page_0(self):
        pages = [PageResult(0, "# Page 0")]
        selected = select_pages(pages)
        assert selected.headings == 0

class TestProbePymupdf:
    def test_pass(self):
        pages = [PageResult(0, "# Content\n\nSome text here.")]
        result = probe_pymupdf(pages)
        assert result.status == ProbeStatus.PASS

    def test_fail_empty(self):
        pages = [PageResult(0, "")]
        result = probe_pymupdf(pages)
        assert result.status == ProbeStatus.FAIL

class TestProbeGmft:
    # ... mock _detect_gmft, test PASS/NOT_INSTALLED/UNTESTED/FAIL
    pass

class TestProbeClaude:
    # ... mock invoke_claude + render_page_image + shutil.which
    # test PASS/NOT_INSTALLED/SKIPPED/FAIL
    pass
```

### Changes Required

**See `design.md` for:**
- Data type definitions → `design.md#1-data-types`
- Page selection logic → `design.md#2-page-selection`
- All 6 probe function signatures and logic → `design.md#3-component-probes`
- Private import rationale → `design.md` Research Findings, "Private function imports"

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_check.py` (NEW — write first)
- [x] Create test file with imports
- [x] `TestSelectPages`: 5 tests (finds math, no math → None, finds tables, no tables → None, page 0)
- [x] `TestProbePymupdf`: 2 tests (pass, fail empty)
- [x] `TestProbeGmft`: 4 tests (not_installed, pass with tables, untested no table page, runtime error)
- [x] `TestProbeImg2table`: 3 tests (not_installed, untested no table page, pass)
- [x] `TestProbeDocling`: 1 test (not_installed)
- [x] `TestProbePandoc`: 5 tests (not_installed, no arXiv → pass, arXiv no HTML → pass, arXiv converted → pass with char count, conversion error → fail)
- [x] `TestProbeClaude`: 4 tests (budget zero skipped, not_installed, pass, fail parse error)

#### 2. Implementation File
**File:** `src/agentic_mbse/extraction/check.py` (NEW)
- [x] Data types: `ProbeStatus`, `OverallStatus`, `ProbeResult`, `SelectedPages`, `CheckResult` (per `design.md#1-data-types`)
- [x] `select_pages(pages)` (per `design.md#2-page-selection`)
- [x] `probe_pymupdf(pages)` (per `design.md#3.1`)
- [x] `probe_gmft(pdf_path, table_page)` (per `design.md#3.2`)
- [x] `probe_img2table(pdf_path, table_page)` (per `design.md#3.3`)
- [x] `probe_docling(pdf_path)` (per `design.md#3.4`)
- [x] `probe_pandoc(pdf_path)` — includes full `convert_arxiv_html()` path (per `design.md#3.5`)
- [x] `probe_claude(pdf_path, page_num, model, budget)` (per `design.md#3.6`)

### Validation

**Automated:**
- [x] `uv run pytest tests/test_check.py -v` → All 24 tests pass
- [x] `uv run pytest tests/ -v` → No regressions (970 passed, 1 skipped)
- [x] `uv run ruff check src/agentic_mbse/extraction/check.py tests/test_check.py`

**Manual:**
- [x] Verify private imports resolve: `python -c "from agentic_mbse.extraction.check import probe_gmft"`

**What We Know Works After This Phase:**
- All 6 probes correctly return the right ProbeStatus for each scenario
- Page selection correctly identifies math/table pages or returns None
- Cross-module imports from tables.py, quality_gate.py, pandoc_convert.py work

---

## Phase 2: Output + Aggregation — Capabilities, Overall Status, Formatting

### Goal
Add capability mapping, overall status computation, and both output formatters (human table + JSON). This phase validates 1-indexed display, UNTESTED handling in capabilities, and JSON schema compliance.

### Test Stencil (Write This First)

```python
# tests/test_check.py — Phase 2 additions

class TestComputeCapabilities:
    def test_all_pass(self):
        probes = [_probe("pymupdf4llm", PASS), _probe("gmft", PASS), ...]
        caps = compute_capabilities(probes, SelectedPages(headings=0, math=1, tables=2))
        assert caps["base_extraction"] is True
        assert caps["table_detection"] is True

    def test_untested_counts_as_ok(self):
        probes = [_probe("gmft", UNTESTED), ...]
        caps = compute_capabilities(probes, SelectedPages(headings=0))
        assert caps["table_detection"] is True

class TestComputeOverall:
    def test_pass(self):
        assert compute_overall([_probe("pymupdf4llm", PASS)]) == OverallStatus.PASS

    def test_untested_not_degraded(self):
        probes = [_probe("pymupdf4llm", PASS), _probe("gmft", UNTESTED)]
        assert compute_overall(probes) == OverallStatus.PASS

class TestFormatJson:
    def test_valid_json(self):
        result = _make_check_result()
        parsed = json.loads(format_check_json(result))
        assert "components" in parsed

    def test_pages_1_indexed(self):
        result = _make_check_result(math_page=4)  # 0-indexed
        parsed = json.loads(format_check_json(result))
        assert parsed["selected_pages"]["math"] == 5  # 1-indexed

class TestPrintCheckTable:
    def test_pages_1_indexed(self, capsys):
        print_check_table(_make_check_result(math_page=4))
        assert "5 (math" in capsys.readouterr().out
```

### Changes Required

**See `design.md` for:**
- Capability mapping table → `design.md#4-capability-mapping`
- Overall status logic → `design.md#5-overall-status`
- Human output format → `design.md#6.1`
- JSON output format → `design.md#6.2`
- 1-indexed decision → `design.md` DD-2

**Specific file changes:**

#### 1. Tests
**File:** `tests/test_check.py` (extend)
- [x] `TestComputeCapabilities`: 3 tests (all pass, untested counts as ok, not_installed → false)
- [x] `TestComputeOverall`: 4 tests (pass, degraded, fail, untested not degraded)
- [x] `TestFormatJson`: 3 tests (valid JSON, pages 1-indexed, null for missing content)
- [x] `TestPrintCheckTable`: 2 tests (pages 1-indexed, missing content message)
- [x] Add test helper `_probe(component, status)` and `_make_check_result()`

#### 2. Implementation
**File:** `src/agentic_mbse/extraction/check.py` (extend)
- [x] `_probe_ok(probes, component)` helper (per `design.md#4`)
- [x] `compute_capabilities(probes, selected)` (per `design.md#4`)
- [x] `compute_overall(probes)` (per `design.md#5`)
- [x] `format_check_json(result)` with 1-indexed pages (per `design.md#6.2`)
- [x] `print_check_table(result)` with 1-indexed pages + missing content messages (per `design.md#6.1`)

### Validation

**Automated:**
- [x] `uv run pytest tests/test_check.py -v` → All 36 tests pass (Phase 1 + Phase 2)
- [x] `uv run pytest tests/ -v` → No regressions (982 passed, 1 skipped)
- [x] `uv run ruff check src/agentic_mbse/extraction/check.py tests/test_check.py`

**Manual:**
- [x] Visually inspect `print_check_table` output via capsys test assertions

**What We Know Works After This Phase:**
- Capability mapping correctly treats UNTESTED as "component works"
- Overall status correctly ignores NOT_INSTALLED and UNTESTED
- JSON output matches spec schema with 1-indexed pages
- Human output shows missing content messages when math/tables absent

---

## Phase 3: CLI Integration + Orchestrator

### Goal
Wire `--check` and `--check-json` into `cmd_extract()`, implement the `run_check()` orchestrator, and handle CLI edge cases (multi-file, DOCX, empty input, exit codes).

### Test Stencil (Write This First)

```python
# tests/test_check.py — Phase 3 additions

class TestRunCheck:
    def test_pymupdf_failure_returns_fail(self):
        with patch("...extract_pages", side_effect=RuntimeError("corrupt")):
            result = run_check(Path("/fake.pdf"))
        assert result.overall == OverallStatus.FAIL
        assert result.probes[0].status == ProbeStatus.FAIL

    def test_all_probes_run_independently(self):
        # Mock GMFT to fail, verify Claude still runs
        ...

class TestCliCheckIntegration:
    def test_exit_code_pass(self):
        # Mock run_check → OverallStatus.PASS
        assert cmd_extract(args) == 0

    def test_exit_code_fail(self):
        # Mock run_check → OverallStatus.FAIL
        assert cmd_extract(args) == 2

    def test_multiple_files_rejected(self):
        # args.path = directory with 2 PDFs
        assert cmd_extract(args) == EXIT_FAILURE

    def test_check_json_implies_check(self):
        # args.check_json = True, args.check = False initially
        ...
```

### Changes Required

**See `design.md` for:**
- Orchestrator logic → `design.md#8-orchestrator`
- CLI argument registration → `design.md#7.1`
- Command handler → `design.md#7.2`
- Exit codes → `design.md#7.3`
- Cost warning → `design.md#9`
- Edge case handling → `design.md#7.2` (Major #3, Minor #4, #5)

**Specific file changes:**

#### 1. Tests
**File:** `tests/test_check.py` (extend)
- [x] `TestRunCheck`: 3 tests (pymupdf failure → fail, all probes run independently, normal flow)
- [x] `TestCliCheckIntegration`: 5 tests (exit code 0/1/2, multiple files rejected, check-json implies check)

#### 2. Orchestrator
**File:** `src/agentic_mbse/extraction/check.py` (extend)
- [x] `run_check(pdf_path, claude_model, claude_budget)` (per `design.md#8`)
- [x] Cost warning to stderr (per `design.md#9`)

#### 3. CLI
**File:** `src/agentic_mbse/cli/extract_cli.py` (modify)
- [x] Add `--check` argument to `register_extract_subcommand()` (per `design.md#7.1`)
- [x] Add `--check-json` argument with `dest="check_json"` (per `design.md#7.1`)
- [x] Add early return block in `cmd_extract()` (per `design.md#7.2`)
- [x] Input validation: empty docs, multi-file, non-PDF (per `design.md#7.2`)
- [x] Exit code mapping: PASS→0, DEGRADED→1, FAIL→2 (per `design.md#7.3`)

### Validation

**Automated:**
- [x] `uv run pytest tests/test_check.py -v` → All 44 tests pass (Phase 1 + 2 + 3)
- [x] `uv run pytest tests/ -v` → No regressions (990 passed, 1 skipped)
- [x] `uv run ruff check src/ tests/`

**Manual (integration — requires real PDF):**
- [ ] `uv run agentic-mbse extract --check tests/corpus/<any>.pdf` → table output, exit 0
- [ ] `uv run agentic-mbse extract --check-json tests/corpus/<any>.pdf` → valid JSON
- [ ] `uv run agentic-mbse extract --check --budget 0 tests/corpus/<any>.pdf` → Claude: skipped
- [ ] `uv run agentic-mbse extract --check tests/corpus/` → error: multiple files
- [ ] Verify exit code: `echo $?` after each command

**What We Know Works After This Phase:**
- Complete end-to-end `--check` flow
- All edge cases handled (multi-file, DOCX, empty, budget 0)
- Exit codes match FR-7
- Human and JSON output correct
- No side effects (no output files written)

---

## Environment Setup

**See CLAUDE.md for full environment rules**

Key commands:
```bash
uv run pytest tests/test_check.py -v    # Phase tests
uv run pytest tests/ -v                  # Full regression
uv run ruff check src/ tests/           # Lint
uv run ruff format src/ tests/          # Format
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: If private imports break, we discover immediately in the first test run. The fix is straightforward — adjust import path or make the function public.
- **Phase 2**: JSON schema validation in tests catches format mismatches against the spec early.
- **Phase 3**: CLI edge cases are explicitly tested. The `--check` code path is completely isolated from the extraction path — no risk of breaking existing extraction.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-02-27
**Actual Changes:**
- Created `tests/test_check.py` — 24 tests across 7 test classes
- Created `src/agentic_mbse/extraction/check.py` — data types, page selection, 6 probes
- Added thin import-guard wrapper functions (`_try_import_gmft`, `_try_import_img2table`, `_try_import_docling`) for testability — allows mocking the import check independently from the detection function

**Issues:** None

**Deviations:**
- Design showed direct `try: from gmft... except ImportError` inline in each probe. Instead, extracted to `_try_import_gmft()` etc. wrapper functions. This makes test patching cleaner (`patch("...check._try_import_gmft", side_effect=ImportError)` vs needing to mock builtins.__import__). No functional difference — same import check, same error path.
- `probe_pymupdf` takes `pages: list[PageResult]` only (not `pdf_path + pages` as in design 3.1). The `pdf_path` parameter was unused in the design's own implementation, so removed it.

### Phase 2 Completion
**Completed:** 2026-02-27
**Actual Changes:**
- Extended `tests/test_check.py` with 12 new tests (36 total), plus `_probe()` and `_make_check_result()` helpers
- Extended `src/agentic_mbse/extraction/check.py` with: `_probe_ok()`, `compute_capabilities()`, `compute_overall()`, `format_check_json()`, `print_check_table()`, `_CAPABILITY_LABELS`, `_page_1indexed()`

**Issues:** Accidentally imported `sys` (for Phase 3 stderr) — caught by ruff, removed.

**Deviations:**
- Used `+`/`-` markers instead of Unicode checkmarks (per design 6.1) for terminal compatibility — matches the design doc's explicit note.

### Phase 3 Completion
**Completed:** 2026-02-27
**Actual Changes:**
- Extended `tests/test_check.py` with 8 new tests (44 total): TestRunCheck (3), TestCliCheckIntegration (5)
- Added `run_check()` orchestrator to `check.py` with cost warning to stderr
- Modified `extract_cli.py`: added `--check` and `--check-json` arguments, early return block with input validation and exit code mapping
- Added `_MockArgs` helper to test file (mirrors test_extract_cli.py pattern, adds check/check_json fields)

**Issues:**
- Initial CLI tests tried to patch `agentic_mbse.cli.extract_cli.run_check` but the import is local (inside `cmd_extract`), so `run_check` isn't a module attribute. Fixed by patching at the source: `agentic_mbse.extraction.check.run_check`.

**Deviations:**
- None — implementation matches design closely.

---

**Status**: ~~Draft~~ → ~~In Progress~~ → **Complete**
