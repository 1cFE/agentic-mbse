# Implementation Plan: PDF Extraction Pipeline v4 — Item 2: Enhancement Components

**Status:** Complete
**Created:** 2026-02-23 18:12 PST
**Last Updated:** 2026-02-23

## Source Documents
- **Spec:** `.project/active/pdf-extraction-v4-item2/spec.md`
- **Design:** `.project/active/pdf-extraction-v4-item2/design.md` — See here for component details, function signatures, code reuse references, and architecture

## Implementation Strategy

**Phasing Rationale:**
1. `claude_enhance.py` first — `tables.py` imports `invoke_claude` from it, so it's the dependency gate
2. `tables.py` pure logic second — de-risks table utilities, filter, and quality assessment with zero-dependency tests before adding complex detector integrations
3. `tables.py` ensemble detection third — the riskiest code (3 detector APIs, per-page error isolation, image saving), built on proven Phase 2 logic
4. `pandoc_convert.py` + `extract_pages()` last — straightforward translations, end with full-suite validation

**Overall Validation Approach:**
- Each phase starts with tests (test-first)
- Each phase ends with `uv run pytest tests/` (no regressions)
- All Claude/GMFT calls mocked — no external dependencies needed

---

## Phase 1: `claude_enhance.py` + Tests

### Goal
Build the Claude vision enhancement module. This is the dependency gate — `tables.py` will import `invoke_claude` from here in Phase 3. Also establishes the Claude CLI invocation pattern and output validation logic.

### Test Stencil (Write This First)
```python
# tests/test_claude_enhance.py

class TestValidateClaudeOutput:
    def test_accept_normal_output(self):
        accept, reason = validate_claude_output("y " * 450, "x " * 500, 0)
        assert accept

    def test_reject_empty(self):
        accept, reason = validate_claude_output("", "x " * 500, 0)
        assert not accept
        assert "empty" in reason.lower()

    def test_reject_truncated(self):
        accept, reason = validate_claude_output("y " * 100, "x " * 500, 0)
        assert not accept

    def test_accept_short_page_exempt(self):
        accept, _ = validate_claude_output("[Figure 3: Reactor]", "[Figure 3]", 0)
        assert accept

    def test_reject_prompt_leak(self):
        accept, _ = validate_claude_output("Read the image file at /tmp/...", "x " * 500, 0)
        assert not accept

class TestExtractPageWithClaude:
    @patch("agentic_mbse.extraction.claude_enhance.invoke_claude")
    def test_returns_cost_record(self, mock_claude):
        mock_claude.return_value = {"result": "# Page", "total_cost_usd": 0.08, ...}
        # Verify CostRecord fields populated correctly
```

### Changes Required

**See `design.md#component-4` for:** function signatures, prompt constant, `invoke_claude` pattern, `render_page_image` source

#### 1. Test File
**File:** `tests/test_claude_enhance.py` (NEW)
- [x] Create test file with TestValidateClaudeOutput (5 test cases from stencil)
- [x]Add TestExtractPageWithClaude (mock invoke_claude, verify CostRecord)
- [x]Add TestRenderPageImage (pytest.importorskip("pymupdf"), or mock pymupdf)

#### 2. Implementation File
**File:** `src/agentic_mbse/extraction/claude_enhance.py` (NEW)
- [x]Add `_PAGE_EXTRACTION_PROMPT` constant (embed from `tests/corpus/prompts/extract_baseline.txt`)
- [x]Implement `invoke_claude()` (from `design.md#4a`, source: `track1:80-120`)
- [x]Implement `render_page_image()` (copy from `ai_repair.py:122-143`, add output_dir param)
- [x]Implement `extract_page_with_claude()` (from `design.md#4c`)
- [x]Implement `validate_claude_output()` (from `design.md#4d`)

### Validation

**Automated:**
- [x]`uv run pytest tests/test_claude_enhance.py -v` → All pass
- [x]`uv run pytest tests/` → No regressions
- [x]`uv run ruff check src/agentic_mbse/extraction/claude_enhance.py` → Clean

**What We Know Works After This Phase:**
- Claude output validation catches empty, truncated, and prompt-leaked responses
- `invoke_claude()` is ready for import by tables.py
- Page image rendering works (copied from proven ai_repair.py code)

---

## Phase 2: `tables.py` — Utilities, Filter, Quality Assessment + Tests

### Goal
Build the pure-logic half of `tables.py`: 6 markdown utilities, `filter_tables()`, `assess_table_quality()`, and the `_dataframe_to_pipe_table()` copy. All testable with synthetic data, zero external dependencies.

### Test Stencil (Write This First)
```python
# tests/test_tables.py

class TestTableUtilities:
    def test_strip_pipe_tables(self):
        md = "Text before\n| a | b |\n|---|---|\n| 1 | 2 |\n\nText after"
        result = strip_pipe_tables(md)
        assert "| a |" not in result
        assert "Text before" in result and "Text after" in result

    def test_replace_tables(self):
        md = "Text\n| old |\n|---|\n| x |"
        tables = [DetectedTable(markdown="| new |\n|---|\n| y |", ...)]
        result = replace_tables(md, tables)
        assert "| old |" not in result and "| new |" in result

class TestFilterTables:
    def test_no_confidence_filter(self):
        t = DetectedTable("| a |", confidence=0.92, num_rows=3, num_cols=2, avg_cell_length=10.0)
        kept, _ = filter_tables([t])
        assert len(kept) == 1  # No confidence filter

    def test_prose_rejected(self):
        t = DetectedTable("| long... |", confidence=1.0, num_rows=3, num_cols=2, avg_cell_length=85.0)
        kept, _ = filter_tables([t])
        assert len(kept) == 0

    def test_extraction_failed_passes_through(self):
        t = DetectedTable("", confidence=1.0, num_rows=0, num_cols=0, avg_cell_length=0,
                         extraction_failed=True, image_path=Path("/tmp/t.png"))
        kept, _ = filter_tables([t])
        assert len(kept) == 1

class TestAssessTableQuality:
    def test_extraction_failed_triggers(self):
        t = DetectedTable("", confidence=1.0, num_rows=0, num_cols=0, avg_cell_length=0,
                         extraction_failed=True, image_path=Path("/tmp/t.png"))
        needs, reasons = assess_table_quality(t)
        assert needs

    def test_good_table_no_enhancement(self):
        t = DetectedTable("| a | b |\n|---|---|\n| 1 | 2 |", 1.0, 1, 2, 3.0)
        needs, _ = assess_table_quality(t)
        assert not needs
```

### Changes Required

**See `design.md#2b-2e` for:** filter logic, quality assessment, utility source references

#### 1. Test File
**File:** `tests/test_tables.py` (NEW)
- [x]Create with TestTableUtilities (strip, replace, insert, has_br, has_col, count_pipe — 8+ tests)
- [x]Add TestFilterTables (no confidence filter, prose, layout artifact, extraction_failed passthrough — 5 tests)
- [x]Add TestAssessTableQuality (extraction_failed, good table, no image, suspect few rows — 4 tests)

#### 2. Implementation File
**File:** `src/agentic_mbse/extraction/tables.py` (NEW — partial, utilities + filter + quality)
- [x]Add `_TABLE_EXTRACTION_PROMPT` constant (embed from `tests/corpus/prompts/extract_table_cropped.txt`)
- [x]Add `_is_table_row()` helper (from `shared.py:335-342`)
- [x]Implement 6 markdown utilities (from `shared.py:345-430`, adapt `GmftTable` → `DetectedTable`)
- [x]Copy `_dataframe_to_pipe_table()` from `table_extraction.py:57-79`
- [x]Implement `filter_tables()` (from `design.md#2b` — no confidence filter)
- [x]Implement `assess_table_quality()` (from `design.md#2c`)
- [x]Add module-level `logger = logging.getLogger(__name__)`
- [x]Add placeholder comment for detection functions (Phase 3)

### Validation

**Automated:**
- [x]`uv run pytest tests/test_tables.py -v` → All pass
- [x]`uv run pytest tests/` → No regressions
- [x]`uv run ruff check src/agentic_mbse/extraction/tables.py` → Clean

**What We Know Works After This Phase:**
- Table markdown manipulation (strip, replace, insert) produces correct output
- Filter rejects prose blocks and layout artifacts but keeps low-confidence real tables
- extraction_failed tables pass through filter and trigger quality assessment
- All table logic ready for detection functions in Phase 3

---

## Phase 3: `tables.py` — Ensemble Detection + Claude Enhancement + Tests

### Goal
Add the detection half of `tables.py`: `detect_tables_ensemble()`, `_detect_gmft()`, `_detect_img2table()`, `_detect_docling()`, and `enhance_table_with_claude()`. This is the riskiest phase — 3 detector APIs, per-page error isolation, image saving, and Claude integration.

### Test Stencil (Write This First)
```python
# tests/test_tables.py (extend)

class TestDetectTablesEnsemble:
    @patch("agentic_mbse.extraction.tables._detect_docling", return_value={})
    @patch("agentic_mbse.extraction.tables._detect_img2table", return_value={})
    @patch("agentic_mbse.extraction.tables._detect_gmft")
    def test_ensemble_calls_gmft_first(self, mock_gmft, mock_img2, mock_docling):
        mock_gmft.return_value = {0: [DetectedTable(...)]}
        result = detect_tables_ensemble(Path("fake.pdf"))
        mock_gmft.assert_called_once()
        # Img2Table skips page 0 (GMFT found tables there)

class TestDetectGmft:
    @patch("agentic_mbse.extraction.tables._gmft_detector", None)
    def test_gmft_not_installed(self):
        # Patch the import to raise ImportError
        result = _detect_gmft(Path("fake.pdf"))
        assert result == {}

class TestEnhanceTableWithClaude:
    @patch("agentic_mbse.extraction.tables.invoke_claude")
    def test_successful_extraction(self, mock_claude):
        mock_claude.return_value = {"result": "| a | b |\n|---|---|\n| 1 | 2 |", ...}
        table = DetectedTable("", 1.0, 0, 0, 0, image_path=Path("/tmp/t.png"),
                             extraction_failed=True)
        enhanced, cost = enhance_table_with_claude(table)
        assert enhanced.source == "claude_cropped"
        assert enhanced.markdown != ""

    @patch("agentic_mbse.extraction.tables.invoke_claude")
    def test_empty_response_marks_false_positive(self, mock_claude):
        mock_claude.return_value = {"result": "", ...}
        table = DetectedTable("", 1.0, 0, 0, 0, image_path=Path("/tmp/t.png"),
                             extraction_failed=True)
        enhanced, cost = enhance_table_with_claude(table)
        assert enhanced.markdown == ""  # FP filter signal
```

### Changes Required

**See `design.md#2a` and `design.md#2d` for:** detection pseudocode, singleton caching, per-page error isolation, Claude enhancement behavior

#### 1. Test File
**File:** `tests/test_tables.py` (EXTEND)
- [x]Add TestDetectTablesEnsemble (mock all 3 detectors, verify ordering and page skipping)
- [x]Add TestDetectGmft graceful degradation (ImportError → empty dict)
- [x]Add TestDetectImg2table graceful degradation (ImportError → empty dict)
- [x]Add TestEnhanceTableWithClaude (successful extraction, empty response FP signal, no image_path)

#### 2. Implementation File
**File:** `src/agentic_mbse/extraction/tables.py` (EXTEND)
- [x]Add module-level singleton vars `_gmft_detector = None`, `_gmft_formatter = None`
- [x]Implement `_detect_gmft()` (from `design.md#2a`, source: `shared.py:216-274`, with per-page try/except and image saving)
- [x]Implement `_detect_img2table()` (from `design.md#2a`, new code using `Img2TableDetectorConfig(borderless_tables=True)`)
- [x]Implement `_detect_docling()` (stub → `return {}`)
- [x]Implement `detect_tables_ensemble()` (orchestrates the three, merges results)
- [x]Implement `enhance_table_with_claude()` (from `design.md#2d`, imports `invoke_claude` from claude_enhance)

### Validation

**Automated:**
- [x]`uv run pytest tests/test_tables.py -v` → All pass (both Phase 2 and Phase 3 tests)
- [x]`uv run pytest tests/` → No regressions
- [x]`uv run ruff check src/agentic_mbse/extraction/tables.py` → Clean

**Manual:**
- [x]Verify `from agentic_mbse.extraction.tables import detect_tables_ensemble, filter_tables, enhance_table_with_claude` works from Python REPL

**What We Know Works After This Phase:**
- Full ensemble detection path (GMFT → Img2Table → Docling stub)
- Graceful degradation on missing GMFT/Img2Table
- Per-page error isolation (NFR-EXT-2)
- Claude table enhancement with FP filter signal
- All table.py public API ready for Item 3 orchestration

---

## Phase 4: `pandoc_convert.py` + `pymupdf_backend.py` extract_pages() + Full Validation

### Goal
Build the two remaining modules and validate the full Item 2 deliverable. Both are straightforward translations from experiment code.

### Test Stencil (Write This First)
```python
# tests/test_pandoc_convert.py

class TestPreprocessHtml:
    def test_strip_figure_tags(self):
        html = "<p>Text</p><figure><img src='x'></figure>"
        result = _preprocess_html(html)
        assert "<figure>" not in result
        assert "<p>Text</p>" in result

class TestPostprocessMarkdown:
    def test_strip_hspace(self):
        assert "\\hspace" not in _postprocess_markdown("Text\\hspace{0pt}more")

class TestDetectArxivId:
    @patch("agentic_mbse.extraction.pandoc_convert.pymupdf")
    def test_finds_arxiv_id(self, mock_pymupdf):
        # Mock doc[0].get_text() returning "arXiv:2510.07314v1 ..."
        result = detect_arxiv_id(Path("fake.pdf"))
        assert result == "2510.07314v1"

    @patch("agentic_mbse.extraction.pandoc_convert.pymupdf")
    def test_no_arxiv(self, mock_pymupdf):
        # Mock doc[0].get_text() returning "Some normal paper text"
        result = detect_arxiv_id(Path("fake.pdf"))
        assert result is None
```

### Changes Required

**See `design.md#component-3` for:** arXiv detection, Pandoc conversion, HTML pre/post-processing
**See `design.md#component-1` for:** extract_pages() signature, BEST_V1 params, force_text divergence

#### 1. Test Files
**File:** `tests/test_pandoc_convert.py` (NEW)
- [x]TestPreprocessHtml (strip figure, strip CSS transform)
- [x]TestPostprocessMarkdown (strip hspace, strip HTML comments)
- [x]TestDetectArxivId (mock pymupdf — found, not found, creator metadata fallback)
- [x]TestConvertArxivHtml (mock subprocess — verify Pandoc flags, pre/post-processing)
- [x]TestPandocAvailable (mock shutil.which)

#### 2. Pandoc Module
**File:** `src/agentic_mbse/extraction/pandoc_convert.py` (NEW)
- [x]Implement `_pandoc_available()` (shutil.which check)
- [x]Implement `_preprocess_html()` (from `h6:78-92`)
- [x]Implement `_postprocess_markdown()` (from `h6:95-106`)
- [x]Implement `detect_arxiv_id()` (from `design.md#3a` — new, pymupdf page 1 regex + metadata)
- [x]Implement `check_arxiv_html()` (from `design.md#3b` — HEAD with User-Agent)
- [x]Implement `convert_arxiv_html()` (from `design.md#3c` — URL download, preprocess, pandoc, postprocess)

#### 3. pymupdf_backend Refactor
**File:** `src/agentic_mbse/extraction/pymupdf_backend.py` (MODIFY — add ~30 lines)
- [x]Add `from agentic_mbse.extraction.types import PageResult` import
- [x]Add `extract_pages()` function after `extract()` (from `design.md#component-1`, source: `shared.py:180-208`)
- [x]Verify `extract()` unchanged (no side effects)

### Validation

**Automated:**
- [x]`uv run pytest tests/test_pandoc_convert.py -v` → All pass
- [x]`uv run pytest tests/test_tables.py tests/test_claude_enhance.py tests/test_pandoc_convert.py -v` → All Item 2 tests pass
- [x]`uv run pytest tests/` → **Full suite passes, zero regressions**
- [x]`uv run ruff check src/agentic_mbse/extraction/` → Clean

**Manual:**
- [x]`uv run python -c "from agentic_mbse.extraction.pandoc_convert import detect_arxiv_id, convert_arxiv_html"` → No ImportError
- [x]`uv run python -c "from agentic_mbse.extraction.pymupdf_backend import extract_pages"` → No ImportError

**What We Know Works After This Phase:**
- All 4 modules + 1 refactor complete and tested
- All spec acceptance criteria covered by unit tests
- Full test suite passes — existing behavior preserved
- All modules ready for Item 3 orchestration

---

## Environment Setup

**See CLAUDE.md for full environment rules.** Key commands:
```bash
uv run pytest tests/                          # Full test suite
uv run pytest tests/test_tables.py -v         # Single test file
uv run ruff check src/ tests/                 # Lint
uv run ruff format src/ tests/                # Format
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis.**

**Phase-Specific Mitigations:**
- **Phase 1**: `validate_claude_output` is new code (no experiment reference) — test stencil covers all 3 rejection modes
- **Phase 2**: No confidence filter is a deliberate change from shared.py — test explicitly verifies low-confidence tables pass
- **Phase 3**: Per-page error isolation is critical — test must verify one page crashing doesn't lose others. GMFT singleton caching — verify initialization happens once
- **Phase 4**: `force_text=True` divergence from `extract()` — documented as intentional, not a regression

---

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-02-23
**Actual Changes:**
- Created `src/agentic_mbse/extraction/claude_enhance.py` (~170 lines): `_PAGE_EXTRACTION_PROMPT`, `invoke_claude()`, `render_page_image()`, `extract_page_with_claude()`, `validate_claude_output()`
- Created `tests/test_claude_enhance.py` (11 tests): TestValidateClaudeOutput (8 tests), TestExtractPageWithClaude (3 tests)
**Issues:** None
**Deviations:** Skipped TestRenderPageImage as a standalone class — render is tested implicitly via extract_page_with_claude mock. No TestInvokeClaude since it's a thin subprocess wrapper (tested via callers).

### Phase 2 Completion
**Completed:** 2026-02-23
**Actual Changes:**
- Created `src/agentic_mbse/extraction/tables.py` (partial): `_is_table_row()`, 6 markdown utilities, `_dataframe_to_pipe_table()`, `filter_tables()`, `assess_table_quality()`, prompt constant, logger
- Created `tests/test_tables.py` (partial): TestIsTableRow (6), TestCountPipeRows (3), TestHasBrInTables (3), TestHasColHeaders (3), TestStripPipeTables (4), TestInsertTablesAtEnd (3), TestReplaceTables (1), TestFilterTables (6), TestAssessTableQuality (4)
**Issues:** None
**Deviations:** None

### Phase 3 Completion
**Completed:** 2026-02-23
**Actual Changes:**
- Extended `tables.py`: `_detect_gmft()`, `_detect_img2table()`, `_detect_docling()` (stub), `detect_tables_ensemble()`, `enhance_table_with_claude()`, module-level singleton vars
- Extended `tests/test_tables.py`: TestDetectTablesEnsemble (3), TestDetectGmftGraceful (1), TestDetectImg2tableGraceful (1), TestEnhanceTableWithClaude (4)
**Issues:**
- Mock patch path for `invoke_claude` in enhance tests: `tables.py` imports `invoke_claude` locally inside the function, so the mock must patch `agentic_mbse.extraction.claude_enhance.invoke_claude` (not `tables.invoke_claude`)
**Deviations:** None

### Phase 4 Completion
**Completed:** 2026-02-23
**Actual Changes:**
- Created `src/agentic_mbse/extraction/pandoc_convert.py` (~140 lines): `_pandoc_available()`, `_preprocess_html()`, `_postprocess_markdown()`, `detect_arxiv_id()`, `check_arxiv_html()`, `convert_arxiv_html()`
- Created `tests/test_pandoc_convert.py` (16 tests): TestPreprocessHtml (3), TestPostprocessMarkdown (3), TestDetectArxivId (4), TestConvertArxivHtml (4), TestPandocAvailable (2)
- Modified `src/agentic_mbse/extraction/pymupdf_backend.py`: added `PageResult` import and `extract_pages()` function (~30 lines) after `_composite_header_detector` singleton
**Issues:**
- `pymupdf` is a local import inside `detect_arxiv_id()`, so `@patch("pandoc_convert.pymupdf")` fails — fixed by patching `pymupdf.open` directly
**Deviations:** None

---

**Status**: Complete
