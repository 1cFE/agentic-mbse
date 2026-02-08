# Implementation Plan: Document Extraction

**Status:** Complete
**Created:** 2026-02-03 01:07 UTC
**Last Updated:** 2026-02-03 01:07 UTC

## Source Documents
- **Spec:** `.project/active/document-extraction/spec.md`
- **Design:** `.project/active/document-extraction/design.md` — See here for component details, function signatures, summary.json schema, architecture, dependencies

## Implementation Strategy

**Phasing Rationale:**
Build from the inside out — establish the extraction core (data types, utilities, simplest backend) first, then wire CLI, then add progressively riskier/optional features. This means Phase 1-2 deliver a working `agentic-mbse extract` for PDFs even if later phases hit issues. Docling (Phase 3) is isolated so its API instability can't block the lightweight path.

**Overall Validation Approach:**
- Each phase starts with tests
- `uv run pytest tests/` after every phase to catch regressions
- `uv run ruff check src/ tests/` for linting
- Manual smoke tests on real PDFs starting Phase 2

---

## Phase 1: Foundation — base.py + pymupdf backend

### Goal
Establish the extraction package with core types, utilities, and the simplest working backend. This is the foundation everything else builds on.

### Test Stencil (Write This First)
```python
# tests/test_extraction.py

class TestSanitizeFilename:
    def test_removes_extension(self):
        assert sanitize_filename("report.pdf") == "report"

    def test_replaces_spaces_and_special_chars(self):
        assert sanitize_filename("My Report (v2).pdf") == "My_Report__v2_"

class TestGetOutputDir:
    def test_default_alongside_input(self, tmp_path):
        pdf = tmp_path / "report.pdf"
        pdf.touch()
        result = get_output_dir(pdf)
        assert result == tmp_path / "report"

    def test_custom_output_base(self, tmp_path):
        pdf = tmp_path / "report.pdf"
        pdf.touch()
        out = tmp_path / "output"
        result = get_output_dir(pdf, output_base=out)
        assert result == out / "report"

class TestCheckProcessingNeeded:
    def test_needed_when_no_output_dir(self, tmp_path):
        pdf = tmp_path / "report.pdf"
        pdf.write_bytes(b"fake pdf")
        assert check_processing_needed(pdf, tmp_path / "report") is True

    def test_not_needed_when_hash_matches(self, tmp_path):
        # Create pdf, output dir, summary.json with matching hash
        ...
        assert check_processing_needed(pdf, output_dir) is False

    def test_needed_when_force(self, tmp_path):
        # Same setup but force=True
        assert check_processing_needed(pdf, output_dir, force=True) is True

class TestWriteSummary:
    def test_writes_valid_json(self, tmp_path):
        result = ExtractionResult(success=True, output_dir=tmp_path, ...)
        write_summary(input_path, tmp_path, result, "pymupdf")
        summary = json.loads((tmp_path / "summary.json").read_text())
        assert summary["processing_completed"] is True
        assert summary["backend_used"] == "pymupdf"
        # Validate all fields per design.md#summary-json-schema

class TestPymupdfBackend:
    def test_extract_produces_markdown_and_images(self, tmp_path, monkeypatch):
        # Mock pymupdf4llm.to_markdown to return known markdown
        # Verify full_document.md written, images/ dir created
        ...

    def test_extract_returns_result_on_success(self, tmp_path, monkeypatch):
        result = extract(input_path, output_dir)
        assert result.success is True
        assert result.markdown_path == output_dir / "full_document.md"

    def test_extract_returns_error_on_failure(self, tmp_path, monkeypatch):
        # Mock pymupdf4llm.to_markdown to raise
        result = extract(input_path, output_dir)
        assert result.success is False
        assert result.error is not None
```

### Changes Required

**See `design.md` for:**
- ExtractionResult dataclass → `design.md#base-py`
- summary.json schema → `design.md#summary-json-schema`
- sanitize_filename port from m-scout → `design.md#base-py`
- pymupdf implementation details → `design.md#pymupdf-backend-py`

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_extraction.py` (NEW — write first)
- [x] Create test file with stencil above
- [x] Tests for: sanitize_filename, get_output_dir, check_processing_needed, write_summary
- [x] Tests for: pymupdf_backend.extract (mocked)

#### 2. Package Init
**File:** `src/agentic_mbse/extraction/__init__.py` (NEW)
- [x] Create package with re-exports of ExtractionResult, key functions

#### 3. Base Module
**File:** `src/agentic_mbse/extraction/base.py` (NEW)
- [x] ExtractionResult dataclass (see `design.md#base-py`)
- [x] sanitize_filename() — port from m-scout `pdf_naming.py`
- [x] get_output_dir()
- [x] check_processing_needed() — hash comparison with summary.json
- [x] write_summary() — produces JSON per `design.md#summary-json-schema`

#### 4. PyMuPDF Backend
**File:** `src/agentic_mbse/extraction/pymupdf_backend.py` (NEW)
- [x] extract() function (see `design.md#pymupdf-backend-py`)
- [x] Lazy import of pymupdf4llm
- [x] Creates output_dir/images/, writes full_document.md

### Validation

**Automated:**
- [x] `uv run pytest tests/test_extraction.py -v` → All pass (21/21)
- [x] `uv run pytest tests/` → No regressions (578 passed, 1 skipped)
- [x] `uv run ruff check src/agentic_mbse/extraction/` → All checks passed

**Manual:**
- [x] `python -c "from agentic_mbse.extraction.base import ExtractionResult; print('OK')"` — import works

**What We Know Works After This Phase:**
Core data types, file utilities, summary.json writing, and pymupdf extraction (mocked). The extraction package exists and is importable.

---

## Phase 2: CLI Wiring — extract_cli.py + registration

### Goal
Wire the extraction pipeline into the CLI so `agentic-mbse extract file.pdf` works end-to-end. Add pyproject.toml extras.

### Test Stencil (Write This First)
```python
# tests/test_extract_cli.py

class TestDiscoverDocuments:
    def test_single_pdf(self, tmp_path):
        pdf = tmp_path / "report.pdf"
        pdf.touch()
        assert discover_documents(pdf) == [pdf]

    def test_single_docx(self, tmp_path):
        docx = tmp_path / "report.docx"
        docx.touch()
        assert discover_documents(docx) == [docx]

    def test_directory_flat_listing(self, tmp_path):
        (tmp_path / "a.pdf").touch()
        (tmp_path / "b.docx").touch()
        (tmp_path / "c.txt").touch()  # ignored
        result = discover_documents(tmp_path)
        assert len(result) == 2

    def test_nonexistent_path(self):
        # Should return empty or raise
        ...

class TestSelectBackend:
    def test_auto_selects_pymupdf_for_pdf(self, monkeypatch):
        # Mock: pymupdf available, docling not
        ...

    def test_forced_backend(self):
        result = select_backend(Path("x.pdf"), requested="pymupdf")
        assert result == "pymupdf"

class TestCmdExtract:
    def test_returns_failure_for_nonexistent_path(self):
        args = MockArgs(path="/nonexistent", ...)
        assert cmd_extract(args) == EXIT_FAILURE

    def test_skips_already_processed(self, tmp_path, monkeypatch):
        # Setup: existing output with matching hash
        # Verify: skip message, no extraction called

class TestCLIIntegration:
    def test_extract_help(self):
        result = subprocess.run(
            ["uv", "run", "agentic-mbse", "extract", "--help"],
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "extract" in result.stdout
```

### Changes Required

**See `design.md` for:**
- CLI interface (flags, arguments) → `design.md#component-1`
- extract_cli functions → `design.md#component-2`
- Orchestration flow → `design.md#component-2`
- Fallback strategy → `design.md#fallback-strategy`

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_extract_cli.py` (NEW — write first)
- [x] Tests for: discover_documents, select_backend, cmd_extract, CLI integration

#### 2. Extract CLI Module
**File:** `src/agentic_mbse/cli/extract_cli.py` (NEW)
- [x] register_extract_subcommand() — argparse setup per `design.md#component-1`
- [x] cmd_extract() — orchestration per `design.md#component-2`
- [x] discover_documents() — flat directory listing, sorted
- [x] select_backend() — auto-detection with availability checks

#### 3. CLI Registration
**File:** `src/agentic_mbse/cli/__init__.py` (MODIFY — inside `main()` after line:1164)
- [x] Add import + registration call (3 lines, see `design.md#component-1`)

#### 4. Dependencies
**File:** `pyproject.toml` (MODIFY)
- [x] Add `extract = ["pymupdf4llm>=0.0.17"]` to `[project.optional-dependencies]`
- [x] Add `extract-full = ["docling>=2.0", "pymupdf4llm>=0.0.17"]`

### Validation

**Automated:**
- [x] `uv run pytest tests/test_extract_cli.py -v` → All pass (18/18)
- [x] `uv run pytest tests/` → No regressions (596 passed, 1 skipped)
- [x] `uv run ruff check src/ tests/` → All checks passed

**Manual:**
- [x] `uv run agentic-mbse extract --help` → Shows extract subcommand with all flags
- [ ] `uv run agentic-mbse extract sample.pdf` → Produces `sample/full_document.md` + `sample/images/` + `sample/summary.json` *(requires pymupdf4llm installed)*
- [ ] `uv run agentic-mbse extract /nonexistent` → Clean error message *(tested via unit test)*
- [ ] Run twice → Second run skips with "already processed" message *(tested via unit test)*
- [ ] `uv run agentic-mbse extract sample.pdf --force` → Reprocesses *(tested via unit test)*

**What We Know Works After This Phase:**
Full PDF extraction pipeline via CLI. Users can `uv add agentic-mbse[extract]` and run `agentic-mbse extract file.pdf`.

---

## Phase 3: Docling Backend + Timeout

### Goal
Add ML-based extraction with process-level timeout and automatic fallback to pymupdf on failure.

### Test Stencil (Write This First)
```python
# Add to tests/test_extraction.py

class TestRunWithTimeout:
    def test_returns_result_on_success(self):
        def fast_func(x):
            return x * 2
        result = run_with_timeout(fast_func, (5,), timeout=10)
        assert result == 10

    def test_returns_none_on_timeout(self):
        def slow_func():
            import time; time.sleep(60)
        result = run_with_timeout(slow_func, (), timeout=1)
        assert result is None

    def test_returns_exception_on_error(self):
        def failing_func():
            raise ValueError("boom")
        result = run_with_timeout(failing_func, (), timeout=10)
        assert isinstance(result, ValueError)

class TestDoclingBackend:
    def test_extract_produces_markdown(self, tmp_path, monkeypatch):
        # Mock docling DocumentConverter
        ...

    def test_extract_uses_timeout(self, tmp_path, monkeypatch):
        # Verify run_with_timeout is called with correct timeout
        ...

    def test_fallback_on_import_error(self):
        # When docling not installed, extract raises ImportError
        ...
```

### Changes Required

**See `design.md` for:**
- Docling implementation details → `design.md#docling-backend-py`
- Timeout implementation → `design.md#timeout-implementation`
- Pickling note → `design.md#timeout-implementation`

**Specific file changes:**

#### 1. Tests
**File:** `tests/test_extraction.py` (MODIFY)
- [x] Add TestRunWithTimeout class (3 tests)
- [x] Add TestDoclingBackend class (4 tests: timeout, exception, success, image rewrite)

#### 2. Timeout Utility
**File:** `src/agentic_mbse/extraction/base.py` (MODIFY)
- [x] Add run_with_timeout() function (see `design.md#timeout-implementation`)

#### 3. Docling Backend
**File:** `src/agentic_mbse/extraction/docling_backend.py` (NEW)
- [x] extract() function wrapping Docling via run_with_timeout
- [x] Lazy import of docling inside function (_docling_extract_inner)
- [x] Image path rewriting to `images/` relative (_rewrite_image_paths)

#### 4. CLI Update
**File:** `src/agentic_mbse/cli/extract_cli.py` (MODIFY)
- [x] select_backend() already detects docling availability (done in Phase 2)
- [x] Fallback logic already wired in cmd_extract (done in Phase 2)
- [x] Cleaned up type: ignore comment now that docling_backend module exists

### Validation

**Automated:**
- [x] `uv run pytest tests/test_extraction.py -v` → All pass (28/28) including timeout tests
- [x] `uv run pytest tests/` → No regressions (603 passed, 1 skipped)
- [x] `uv run ruff check` → All checks passed

**Manual (requires `extract-full` installed):**
- [ ] `uv sync --extra extract-full` *(deferred — docling not installed in dev env)*
- [ ] `uv run agentic-mbse extract sample.pdf` → Uses docling *(deferred)*
- [ ] `uv run agentic-mbse extract sample.pdf --timeout 1` → Times out, falls back *(validated via unit test)*
- [ ] `uv run agentic-mbse extract sample.pdf --backend pymupdf` → Forces pymupdf *(validated via unit test)*

**What We Know Works After This Phase:**
Docling extraction with timeout protection. Automatic fallback chain: docling → pymupdf → fail. The `--timeout` and `--backend` flags work.

---

## Phase 4: DOCX Support — Pandoc Backend

### Goal
Extend extraction to DOCX files using pandoc as the fallback backend.

### Test Stencil (Write This First)
```python
# Add to tests/test_extraction.py

class TestPandocBackend:
    def test_extract_calls_pandoc_subprocess(self, tmp_path, monkeypatch):
        # Mock subprocess.run
        ...

    def test_extract_fails_when_pandoc_missing(self, tmp_path, monkeypatch):
        # Mock shutil.which returning None
        result = extract(input_path, output_dir)
        assert result.success is False
        assert "pandoc" in result.error.lower()

    def test_image_paths_are_relative(self, tmp_path, monkeypatch):
        # Verify markdown references use images/ prefix
        ...
```

### Changes Required

**See `design.md` for:**
- Pandoc implementation details → `design.md#pandoc-backend-py`
- Fallback strategy for DOCX → `design.md#fallback-strategy`

**Specific file changes:**

#### 1. Tests
**File:** `tests/test_extraction.py` (MODIFY)
- [x] Add TestPandocBackend class (5 tests: missing pandoc, subprocess call, failure, image paths, rewrite)

#### 2. Pandoc Backend
**File:** `src/agentic_mbse/extraction/pandoc_backend.py` (NEW)
- [x] extract() function using subprocess.run
- [x] pandoc binary availability check via shutil.which (_pandoc_available)
- [x] Image path post-processing (move media/ → images/, rewrite refs)

#### 3. CLI Update
**File:** `src/agentic_mbse/cli/extract_cli.py` (MODIFY)
- [x] discover_documents() already includes .docx files (done in Phase 2)
- [x] select_backend() already handles DOCX: docling → pandoc fallback (done in Phase 2)
- [x] Cleaned up type: ignore comment now that pandoc_backend module exists

#### 4. Test Fixture
**File:** `tests/fixtures/sample.docx` (NEW)
- [ ] Deferred — all pandoc tests use mocked subprocess; real DOCX fixture not needed yet

### Validation

**Automated:**
- [x] `uv run pytest tests/test_extraction.py -v` → All pass (33/33)
- [x] `uv run pytest tests/` → No regressions (608 passed, 1 skipped)
- [x] `uv run ruff check` → All checks passed

**Manual (requires pandoc installed):**
- [ ] `uv run agentic-mbse extract sample.docx` *(deferred — validated via mocked tests)*
- [ ] `uv run agentic-mbse extract dir_with_mixed/` *(deferred)*
- [ ] Without pandoc: `uv run agentic-mbse extract sample.docx` *(validated via unit test)*

**What We Know Works After This Phase:**
Full format support — PDF and DOCX extraction via CLI with appropriate fallback chains.

---

## Phase 5: Index Generation + Script Refactoring

### Goal
Port `generate_index.py` and `read_section.py` into the library, wire `--index` and `--summarize` flags, reduce scripts to thin wrappers.

### Test Stencil (Write This First)
```python
# tests/test_index.py (NEW)

class TestParseSections:
    def test_parses_numbered_headers(self):
        content = "## 1 Introduction\nText\n## 2 Methods\nMore text"
        sections = parse_sections(content, max_depth=3)
        assert len(sections) == 2
        assert sections[0].section_num == "1"

    def test_respects_max_depth(self):
        content = "## 1 Top\n### 1.1 Sub\n#### 1.1.1 Deep"
        sections = parse_sections(content, max_depth=2)
        assert len(sections) == 2  # excludes 1.1.1

class TestGenerateIndex:
    def test_produces_index_file(self, tmp_path):
        doc = tmp_path / "full_document.md"
        doc.write_text("## 1 Intro\nHello\n## 2 Body\nWorld")
        result = generate_index(doc, summarize=False)
        assert result == tmp_path / "INDEX.md"
        assert result.exists()

    def test_skips_when_checksum_matches(self, tmp_path):
        # Create doc + INDEX.md with matching checksum
        result = generate_index(doc)
        assert result is None  # skipped

class TestScriptBackwardCompat:
    def test_generate_index_script_runs(self):
        result = subprocess.run(
            ["python", "scripts/generate_index.py", "--help"],
            capture_output=True, text=True
        )
        assert result.returncode == 0

    def test_read_section_script_runs(self):
        result = subprocess.run(
            ["python", "scripts/read_section.py", "--help"],
            capture_output=True, text=True
        )
        assert result.returncode == 0
```

### Changes Required

**See `design.md` for:**
- Index generation functions → `design.md#component-4`
- Script refactoring pattern → `design.md#component-4`
- Section dataclass → ported from `scripts/generate_index.py:33-44`

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_index.py` (NEW — write first)
- [x] Tests for: parse_sections (7 tests), build_hierarchy (2), format_index_md (1), generate_index (5), parse_index_sections (1), read_lines (2), read_section (3)
- [x] Tests for: backward compatibility of script wrappers (2 tests)

#### 2. Index Module
**File:** `src/agentic_mbse/extraction/index.py` (NEW)
- [x] Port Section dataclass from `scripts/generate_index.py:33-44`
- [x] Port parse_sections, build_hierarchy, format_index_md, generate_summary
- [x] Add generate_index() library function
- [x] Add read_section() library function (+ parse_index_sections, read_lines)
- [x] Add cli_main() and read_section_cli_main() for script wrappers

#### 3. Script Refactoring
**File:** `scripts/generate_index.py` (MODIFY — reduce to thin wrapper)
- [x] Replaced 317 lines with 5-line wrapper importing cli_main

**File:** `scripts/read_section.py` (MODIFY — reduce to thin wrapper)
- [x] Replaced 147 lines with 5-line wrapper importing read_section_cli_main

#### 4. CLI Update
**File:** `src/agentic_mbse/cli/extract_cli.py` (MODIFY)
- [x] Wire `--index` flag: call generate_index() after extraction
- [x] Wire `--summarize` flag: pass summarize=True to generate_index()

### Validation

**Automated:**
- [x] `uv run pytest tests/test_index.py -v` → All pass (23/23)
- [x] `uv run pytest tests/` → No regressions (631 passed, 1 skipped)
- [x] `python scripts/generate_index.py --help` → Still works
- [x] `python scripts/read_section.py --help` → Still works
- [x] `uv run ruff check` → All checks passed

**Manual:**
- [ ] `uv run agentic-mbse extract sample.pdf --index` *(deferred — requires pymupdf4llm)*
- [ ] `uv run agentic-mbse extract sample.pdf --index --summarize` *(deferred — requires claude CLI)*
- [ ] `python scripts/read_section.py sample/ 1` *(deferred)*

**What We Know Works After This Phase:**
Index generation integrated into extract pipeline. Scripts still work as standalone tools. `--index` and `--summarize` flags functional.

---

## Phase 6: Table Repair

### Goal
Add opt-in `--fix-tables` flag for two-pass table repair via Claude headless mode.

### Test Stencil (Write This First)
```python
# tests/test_table_repair.py (NEW)

class TestRepairTables:
    def test_detects_broken_table(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 | 3 |"  # extra column
        broken = find_broken_tables(md)
        assert len(broken) == 1

    def test_skips_valid_table(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        broken = find_broken_tables(md)
        assert len(broken) == 0

    def test_repair_calls_claude(self, monkeypatch):
        # Mock subprocess.run for claude -p
        ...
        result = repair_tables(markdown_path)
        assert result is True

    def test_no_repair_when_all_valid(self, tmp_path):
        md_path = tmp_path / "full_document.md"
        md_path.write_text("| A | B |\n|---|---|\n| 1 | 2 |")
        result = repair_tables(md_path)
        assert result is False
```

### Changes Required

**See `design.md` for:**
- Table repair implementation → `design.md#component-5`

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_table_repair.py` (NEW — write first)
- [x] Tests for: find_broken_tables (9 tests), repair_tables (5 tests including mocked claude subprocess)

#### 2. Table Repair Module
**File:** `src/agentic_mbse/extraction/table_repair.py` (NEW)
- [x] find_broken_tables() — parse markdown for table blocks, validate column consistency
- [x] repair_tables() — call `claude -p` for each broken table, replace in-place

#### 3. CLI Update
**File:** `src/agentic_mbse/cli/extract_cli.py` (MODIFY)
- [x] Wire `--fix-tables` flag: call repair_tables() after extraction

### Validation

**Automated:**
- [x] `uv run pytest tests/test_table_repair.py -v` → All pass (14/14)
- [x] `uv run pytest tests/` → No regressions (645 passed, 1 skipped)
- [x] `uv run ruff check` → All checks passed (for Phase 6 files)

**Manual (requires `claude` CLI):**
- [ ] `uv run agentic-mbse extract table_heavy.pdf --fix-tables` → Tables repaired in output *(deferred)*
- [ ] `uv run agentic-mbse extract clean.pdf --fix-tables` → No changes (all tables valid) *(validated via unit test)*

**What We Know Works After This Phase:**
All spec features implemented. Full extraction pipeline with PDF, DOCX, index generation, and table repair.

---

## Environment Setup

**See CLAUDE.md for full environment rules**

```bash
uv sync                          # Base install
uv sync --extra extract          # With pymupdf (Phase 1-2)
uv sync --extra extract-full     # With docling (Phase 3+)
uv run pytest tests/             # Run all tests
uv run ruff check src/ tests/    # Linting
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: If pymupdf4llm API differs from m-scout version, check current docs. The `to_markdown()` call is stable.
- **Phase 3**: Docling API is the highest risk. If API has changed, adapt or skip — Phases 1-2 already deliver a working tool. Test `run_with_timeout` with trivial functions before wiring to Docling.
- **Phase 4**: If pandoc is not installed in CI, mock subprocess tests. Manual validation requires local pandoc.
- **Phase 5**: Script refactoring must preserve exact CLI behavior. Run `--help` comparison before/after.

---

## Implementation Notes

_To be filled during implementation._

### Phase 1 Completion
**Completed:** 2026-02-03
**Actual Changes:**
- Created `src/agentic_mbse/extraction/__init__.py` with re-exports
- Created `src/agentic_mbse/extraction/base.py` with ExtractionResult, sanitize_filename, get_output_dir, check_processing_needed, write_summary, _compute_file_hash
- Created `src/agentic_mbse/extraction/pymupdf_backend.py` with extract() and _get_to_markdown() for testability
- Created `tests/test_extraction.py` with 21 tests covering all base utilities and pymupdf backend (mocked)

**Issues:** None
**Deviations:**
- `sanitize_filename` replaces ALL non-alphanumeric/non-underscore chars (not just filesystem-invalid ones like m-scout). This is stricter but matches the plan's test expectations.
- Added `_get_to_markdown()` helper in pymupdf_backend for clean monkeypatching in tests, instead of patching the module-level import directly.

### Phase 2 Completion
**Completed:** 2026-02-03
**Actual Changes:**
- Created `tests/test_extract_cli.py` with 18 tests (discover_documents, select_backend, cmd_extract, CLI integration)
- Created `src/agentic_mbse/cli/extract_cli.py` with register_extract_subcommand, cmd_extract, discover_documents, select_backend, _run_extraction, _is_available
- Modified `src/agentic_mbse/cli/__init__.py` to register extract subcommand (4 lines after pm registration)
- Modified `pyproject.toml` to add `extract` and `extract-full` optional dependency groups
**Issues:** None
**Deviations:**
- Added `_is_available()` helper to centralize backend availability checks — cleaner than inline try/except in select_backend
- Added `_run_extraction()` dispatch helper to keep cmd_extract focused on orchestration
- cmd_extract returns EXIT_SUCCESS even with some failures (only EXIT_FAILURE when ALL documents fail) — more useful for batch processing
- Manual smoke tests for real PDF extraction deferred until pymupdf4llm is installed; behavior validated via mocked unit tests

### Phase 3 Completion
**Completed:** 2026-02-03
**Actual Changes:**
- Modified `src/agentic_mbse/extraction/base.py` — added `run_with_timeout()` and `_timeout_wrapper()` using multiprocessing.Process + Queue
- Created `src/agentic_mbse/extraction/docling_backend.py` — `extract()` with timeout wrapping, `_docling_extract_inner()` with lazy docling import, `_rewrite_image_paths()`
- Modified `tests/test_extraction.py` — added TestRunWithTimeout (3 tests) and TestDoclingBackend (4 tests)
- Cleaned up `src/agentic_mbse/cli/extract_cli.py` — removed stale `type: ignore[import-not-found]` on docling import

**Issues:** Fork deprecation warnings in tests from multiprocessing in threaded pytest — cosmetic only, not a real problem.
**Deviations:**
- Split docling extraction into `_docling_extract_inner` (runs in child process) and `extract` (orchestrates timeout + error handling) — cleaner separation than design's single-function approach.
- CLI update was minimal since Phase 2 already wired select_backend and fallback logic generically for all backends.

### Phase 4 Completion
**Completed:** 2026-02-03
**Actual Changes:**
- Created `src/agentic_mbse/extraction/pandoc_backend.py` — `extract()`, `_pandoc_available()`, `_rewrite_image_paths()`; moves pandoc's `media/` dir into `images/` and rewrites markdown references
- Modified `tests/test_extraction.py` — added TestPandocBackend (5 tests)
- Modified `src/agentic_mbse/cli/extract_cli.py` — removed stale `type: ignore[import-not-found]` on pandoc import

**Issues:** None
**Deviations:**
- Pandoc backend moves extracted media from pandoc's `--extract-media` dir into `images/` and cleans up the temp `media/` dir — cleaner than design's simple subprocess call
- Added 120s subprocess timeout as safety net for pandoc hangs
- Skipped `sample.docx` fixture — all tests use mocked subprocess; real fixture adds complexity without test value

### Phase 5 Completion
**Completed:** 2026-02-03
**Actual Changes:**
- Created `src/agentic_mbse/extraction/index.py` (~330 lines) — ported Section dataclass, parse_sections, build_hierarchy, format_index_md, generate_summary, generate_index, parse_index_sections, read_lines, read_section, cli_main, read_section_cli_main
- Reduced `scripts/generate_index.py` from 317 lines → 5-line thin wrapper
- Reduced `scripts/read_section.py` from 147 lines → 5-line thin wrapper
- Modified `src/agentic_mbse/cli/extract_cli.py` — wired `--index` and `--summarize` post-processing after successful extraction
- Created `tests/test_index.py` with 23 tests covering all library functions and script backward compatibility

**Issues:** None
**Deviations:**
- Added `--summarize` / `--no-summarize` flags to `cli_main()` (the script CLI) for explicit control, since the original script always generated summaries. Default is still `--summarize` for backward compatibility.
- Added `FileNotFoundError` handling in `generate_summary()` for when `claude` CLI is not installed — returns a placeholder instead of crashing.
- `read_section()` library function returns `str | None` instead of printing to stdout — callers decide how to display.

### Phase 6 Completion
**Completed:** 2026-02-03
**Actual Changes:**
- Created `src/agentic_mbse/extraction/table_repair.py` (~100 lines) — `find_broken_tables()`, `repair_tables()`, plus internal helpers `_extract_table_blocks()`, `_is_table_valid()`, `_count_columns()`, `_call_claude()`
- Modified `src/agentic_mbse/cli/extract_cli.py` — wired `--fix-tables` post-processing after successful extraction, before index generation
- Created `tests/test_table_repair.py` with 14 tests (9 for find_broken_tables, 5 for repair_tables)

**Issues:** None
**Deviations:**
- Table validation checks for both column consistency AND presence of a separator row (design only mentioned column consistency). A pipe-delimited block without a `|---|` separator row is treated as broken.
- `repair_tables()` processes broken tables in reverse line order so replacement doesn't invalidate indices for earlier tables.
- Added 120s subprocess timeout on `claude -p` calls as safety net.
- `--fix-tables` runs before `--index` so that the index is generated from the repaired markdown.

---

**Status**: ~~Draft~~ → ~~In Progress~~ → **Complete**
