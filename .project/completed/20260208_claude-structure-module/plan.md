# Implementation Plan: Claude Structure Module — Core Implementation

**Status:** Complete
**Created:** 2026-02-08 16:06 UTC
**Last Updated:** 2026-02-08 16:06 UTC

## Source Documents
- **Spec:** `.project/active/claude-structure-module/spec.md`
- **Design:** `.project/active/claude-structure-module/design.md` ← See here for component details, dependencies, architecture

## Implementation Strategy

**Phasing Rationale:**
Phase 1 tackles all pure functions (no I/O, no mocks needed) — this is ~60% of the logic and includes the trickiest algorithm (`apply_insertions` with reverse-order, dedup, ambiguity). Phase 2 adds the Claude subprocess helper and Phase A (style detection with caching), establishing the invocation pattern. Phase 3 completes with Phase B (chunked repair) and the orchestrator. Each phase builds strictly on the previous one.

**Overall Validation Approach:**
- Each phase starts with tests
- Each phase ends with `uv run pytest tests/test_claude_structure.py -v` + `uv run pytest tests/ -x` (no regressions)
- `uv run ruff check src/agentic_mbse/extraction/claude_structure.py tests/test_claude_structure.py` after each phase

---

## Phase 1: Data Structures + Pure Functions

### Goal
Build all components that require zero I/O: dataclasses, gate heuristic, JSON parser, chunking, header application, running header strip. These are fully testable without mocks and represent the core algorithmic complexity.

### Test Stencil (Write This First)

```python
# tests/test_claude_structure.py — Phase 1 test stencil

class TestDocumentStyle:
    def test_to_dict_from_dict_round_trip(self):
        style = DocumentStyle(doc_type="academic_paper", heading_convention="numbered_bold",
                              has_toc=True, running_headers=["Author Name"], page_number_format="bare")
        assert DocumentStyle.from_dict(style.to_dict()) == style

    def test_json_serialization(self):
        style = DocumentStyle(...)
        json_str = json.dumps(style.to_dict())
        assert DocumentStyle.from_dict(json.loads(json_str)) == style

class TestNeedsClaudeStructure:
    def test_sparse_headers_returns_true(self):
        # 1 header across 20 pages → 0.05/page → True
        md = _build_md(num_pages=20, headers=["## Introduction"])
        assert needs_claude_structure(md) is True

    def test_dense_headers_returns_false(self):
        # 10 headers across 20 pages with mixed levels → 0.5/page → False
        md = _build_md(num_pages=20, headers=["## S1", "### S1.1", "## S2", ...])
        assert needs_claude_structure(md) is False

    def test_high_noise_fraction_returns_true(self):
        # 10 headers, 5 are noise (math operators) → 0.5 noise → True
        md = _build_md(num_pages=20, headers=["## A >= 15", "## 1 x", ...])
        assert needs_claude_structure(md) is True

    def test_zero_depth_variance_with_enough_headers_returns_true(self):
        # 5 ## headers, no ### → flat → True (because hpp >= 0.1)
        md = _build_md(num_pages=20, headers=["## S1", "## S2", "## S3", "## S4", "## S5"])
        assert needs_claude_structure(md) is True

    def test_zero_depth_variance_sparse_does_not_double_trigger(self):
        # 1 ## header across 20 pages → sparse triggers first, depth_variance irrelevant
        md = _build_md(num_pages=20, headers=["## Only"])
        assert needs_claude_structure(md) is True

    def test_corpus_profile_2241_returns_false(self):
        md = _build_md(num_pages=30, headers=[...])  # 7 ## + 8 ### from baseline
        assert needs_claude_structure(md) is False

class TestParseJsonResponse:
    def test_bare_json(self):
        assert _parse_json_response('{"key": "val"}') == {"key": "val"}

    def test_fenced_json(self):
        assert _parse_json_response('```json\n{"key": "val"}\n```') == {"key": "val"}

    def test_prose_wrapped_json(self):
        assert _parse_json_response('Here is the result:\n{"key": "val"}\nDone.') == {"key": "val"}

    def test_invalid_json_returns_none(self):
        assert _parse_json_response("not json at all") is None

class TestChunking:
    def test_small_doc_single_chunk(self):
        lines = _build_lines(num_pages=10)
        chunks = _chunk_by_pages(lines, chunk_size=25, overlap=3)
        assert len(chunks) == 1

    def test_50_pages_two_chunks_with_overlap(self):
        lines = _build_lines(num_pages=50)
        chunks = _chunk_by_pages(lines, chunk_size=25, overlap=3)
        assert len(chunks) == 2
        # Overlap: last 3 pages of chunk 0 == first 3 pages of chunk 1
        assert chunks[0].end_page > chunks[1].start_page  # overlap exists

    def test_100_pages_correct_count(self):
        lines = _build_lines(num_pages=100)
        chunks = _chunk_by_pages(lines, chunk_size=25, overlap=3)
        assert len(chunks) >= 4

    def test_overlap_pages_in_adjacent_chunks(self):
        lines = _build_lines(num_pages=50)
        chunks = _chunk_by_pages(lines, chunk_size=25, overlap=3)
        # The text of the overlap region should appear in both chunks
        ...

class TestApplyInsertions:
    def test_single_insertion_before(self):
        md = "Some intro text\n\nThe main body starts here."
        ins = [HeaderInsertion(anchor_text="The main body starts", level=2,
                               title="Introduction", insert_position="before")]
        result, inserted, skipped, warnings = apply_insertions(md, ins)
        assert "## Introduction" in result
        assert inserted == 1 and skipped == 0

    def test_single_insertion_after(self):
        ...

    def test_multiple_insertions_reverse_order(self):
        # Two insertions at different positions; both should land correctly
        ...

    def test_anchor_not_found_skips_with_warning(self):
        md = "Some text here."
        ins = [HeaderInsertion(anchor_text="nonexistent text", level=2,
                               title="Missing", insert_position="before")]
        result, inserted, skipped, warnings = apply_insertions(md, ins)
        assert inserted == 0 and skipped == 1
        assert any("not found" in w for w in warnings)

    def test_ambiguous_anchor_skips_with_warning(self):
        md = "Repeated line\n\nRepeated line"
        ins = [HeaderInsertion(anchor_text="Repeated line", level=2,
                               title="Ambiguous", insert_position="before")]
        result, inserted, skipped, warnings = apply_insertions(md, ins)
        assert skipped == 1
        assert any("ambiguous" in w.lower() for w in warnings)

    def test_duplicate_header_prevention(self):
        md = "## Introduction\n\nThe content starts here."
        ins = [HeaderInsertion(anchor_text="The content starts", level=2,
                               title="Introduction", insert_position="before")]
        result, inserted, skipped, warnings = apply_insertions(md, ins)
        assert skipped == 1
        assert result.count("## Introduction") == 1  # not duplicated

class TestStripDetectedHeaders:
    def test_removes_matching_lines(self):
        md = "Content A\n\nAuthor Name\n\nContent B\n\nAuthor Name\n\nContent C"
        result = strip_detected_headers(md, ["Author Name"])
        assert "Author Name" not in result
        assert "Content A" in result and "Content C" in result

    def test_preserves_non_matching(self):
        md = "Content A\n\nDifferent Text\n\nContent B"
        result = strip_detected_headers(md, ["Author Name"])
        assert "Different Text" in result
```

### Changes Required

**See `design.md` for:**
- Data structure definitions → `design.md#data-structures`
- `needs_claude_structure` logic → `design.md#1-needs_claude_structure`
- `apply_insertions` algorithm → `design.md#4-apply_insertions`
- `strip_detected_headers` behavior → `design.md#5-strip_detected_headers`
- Chunking algorithm → `design.md#chunking-helper`
- JSON parser → `design.md#json-response-parser`
- Page marker regex → `design.md#page-marker-parsing`

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_claude_structure.py` (NEW — write first)
- [ ] Create file with imports and test helper `_build_md()` for generating markdown with PAGE markers and headers
- [ ] Create test helper `_build_lines()` for chunking tests
- [ ] `TestDocumentStyle` — 3 tests (round-trip, JSON, missing fields)
- [ ] `TestParseJsonResponse` — 4 tests (bare, fenced, prose-wrapped, invalid)
- [ ] `TestNeedsClaudeStructure` — 6 tests (sparse, dense, noise, depth_variance, corpus profiles)
- [ ] `TestChunking` — 4 tests (small doc, 50p, 100p, overlap verification)
- [ ] `TestApplyInsertions` — 6 tests (before, after, multiple, not found, ambiguous, duplicate prevention)
- [ ] `TestStripDetectedHeaders` — 2 tests (removal, preservation)

#### 2. Implementation File
**File:** `src/agentic_mbse/extraction/claude_structure.py` (NEW)
- [ ] Module docstring, imports (`re`, `json`, `dataclasses`, `pathlib`, `typing`)
- [ ] Import `_is_noise_header` from `postprocess.py`
- [ ] `_PAGE_MARKER_RE` regex (own copy per design)
- [ ] `_HEADER_RE = re.compile(r"^(#{2,6}) (.+)$", re.MULTILINE)`
- [ ] `DocumentStyle` dataclass with `to_dict()` / `from_dict()`
- [ ] `HeaderInsertion` dataclass
- [ ] `_parse_json_response()` helper
- [ ] `_Chunk` dataclass + `_chunk_by_pages()` helper
- [ ] `needs_claude_structure()` — pure function
- [ ] `apply_insertions()` — returns `(md, inserted, skipped, warnings)`
- [ ] `strip_detected_headers()` — targeted line removal

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_claude_structure.py -v` → all ~25 tests pass
- [ ] `uv run pytest tests/ -x` → no regressions (799+ existing tests still pass)
- [ ] `uv run ruff check src/agentic_mbse/extraction/claude_structure.py tests/test_claude_structure.py`
- [ ] `uv run ruff format --check src/agentic_mbse/extraction/claude_structure.py tests/test_claude_structure.py`

**Manual:**
- [ ] Read `needs_claude_structure()` and verify the three-metric logic matches design
- [ ] Read `apply_insertions()` and trace through a 3-insertion example mentally

**What We Know Works After This Phase:**
- All data structures serialize correctly
- Gate heuristic produces correct decisions for all 7 corpus profiles in baseline
- Header insertion handles all edge cases (not found, ambiguous, duplicate, reverse-order)
- Chunking produces correct windows with overlap
- JSON parser handles Claude's common response wrappers
- Running header strip works on known patterns

---

## Phase 2: Claude Integration — _call_claude + detect_document_style

### Goal
Build the subprocess helper and Phase A (style detection with disk caching). This establishes the Claude invocation pattern reused by Phase B.

### Test Stencil (Write This First)

```python
# Add to tests/test_claude_structure.py — Phase 2

class TestCallClaude:
    @patch("agentic_mbse.extraction.claude_structure.subprocess.run")
    def test_successful_call(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout='{"result": true}')
        text, warnings = _call_claude("prompt", [], model="haiku")
        assert text == '{"result": true}'
        assert warnings == []

    @patch("agentic_mbse.extraction.claude_structure.subprocess.run")
    def test_retry_on_failure(self, mock_run):
        mock_run.side_effect = [
            MagicMock(returncode=1, stdout=""),  # first attempt fails
            MagicMock(returncode=0, stdout='{"ok": true}'),  # retry succeeds
        ]
        text, warnings = _call_claude("prompt", [], model="haiku", retries=1)
        assert text == '{"ok": true}'
        assert mock_run.call_count == 2

    @patch("agentic_mbse.extraction.claude_structure.subprocess.run")
    def test_timeout_returns_none(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=120)
        text, warnings = _call_claude("prompt", [], model="haiku")
        assert text is None
        assert any("timed out" in w for w in warnings)

    @patch("agentic_mbse.extraction.claude_structure.subprocess.run")
    def test_claude_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        text, warnings = _call_claude("prompt", [], model="haiku")
        assert text is None
        assert any("not found" in w for w in warnings)

class TestDetectDocumentStyle:
    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_valid_response(self, mock_claude, mock_render, tmp_path):
        mock_render.return_value = Path("/tmp/page.png")
        mock_claude.return_value = (
            '{"doc_type":"academic_paper","heading_convention":"numbered_bold",'
            '"has_toc":true,"running_headers":[],"page_number_format":"bare"}',
            [],
        )
        md = "<!-- PAGE:1 -->\nTitle\n<!-- PAGE:2 -->\nBody\n<!-- PAGE:3 -->\nMore"
        style, warnings = detect_document_style(md, Path("test.pdf"), tmp_path)
        assert style.doc_type == "academic_paper"
        assert (tmp_path / "style.json").exists()

    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_cache_hit(self, mock_claude, mock_render, tmp_path):
        # Pre-write cache
        cache = {"doc_type":"slide_deck","heading_convention":"slide_titles",
                 "has_toc":False,"running_headers":["Footer"],"page_number_format":"none"}
        (tmp_path / "style.json").write_text(json.dumps(cache))
        style, warnings = detect_document_style("md", Path("test.pdf"), tmp_path)
        assert style.doc_type == "slide_deck"
        mock_claude.assert_not_called()

    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_malformed_json_fallback(self, mock_claude, mock_render, tmp_path):
        mock_render.return_value = Path("/tmp/page.png")
        mock_claude.return_value = (None, ["claude -p failed"])
        md = "<!-- PAGE:1 -->\nText"
        style, warnings = detect_document_style(md, Path("test.pdf"), tmp_path)
        assert style.doc_type == "unknown"
        assert len(warnings) > 0

    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_timeout_fallback(self, mock_claude, mock_render, tmp_path):
        mock_render.return_value = Path("/tmp/page.png")
        mock_claude.return_value = (None, ["timed out"])
        style, warnings = detect_document_style("<!-- PAGE:1 -->\nX", Path("t.pdf"), tmp_path)
        assert style.doc_type == "unknown"

    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_fewer_than_3_pages_handled(self, mock_claude, mock_render, tmp_path):
        mock_render.return_value = Path("/tmp/page.png")
        mock_claude.return_value = ('{"doc_type":"word_doc","heading_convention":"unnumbered_bold",'
                                     '"has_toc":false,"running_headers":[],"page_number_format":"none"}', [])
        md = "<!-- PAGE:1 -->\nShort doc"
        style, warnings = detect_document_style(md, Path("test.pdf"), tmp_path)
        assert style.doc_type == "word_doc"
```

### Changes Required

**See `design.md` for:**
- `_call_claude` helper → `design.md#subprocess-call-helper`
- `detect_document_style` logic → `design.md#2-detect_document_style--phase-a`
- Error handling strategy → `design.md#error-handling-strategy`
- Prompt design → `design.md#2-detect_document_style--phase-a` (Phase A prompt)

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_claude_structure.py` (MODIFY)
- [ ] Add `import subprocess` and mock imports
- [ ] `TestCallClaude` — 4 tests (success, retry, timeout, not found)
- [ ] `TestDetectDocumentStyle` — 5 tests (valid, cache hit, malformed, timeout, short doc)

#### 2. Implementation File
**File:** `src/agentic_mbse/extraction/claude_structure.py` (MODIFY)
- [ ] Add `import subprocess`, `import tempfile`
- [ ] Import `render_page_image` from `ai_repair`
- [ ] `_call_claude()` — subprocess helper with retry logic
- [ ] `_PHASE_A_PROMPT` template string
- [ ] `_FALLBACK_STYLE` — default DocumentStyle for error cases
- [ ] `detect_document_style()` — cache check → render images → call Claude → parse → cache result

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_claude_structure.py -v` → all ~34 tests pass (25 from Phase 1 + 9 new)
- [ ] `uv run pytest tests/ -x` → no regressions
- [ ] `uv run ruff check` + `uv run ruff format --check`

**Manual:**
- [ ] Verify `_call_claude` builds correct command: `["claude", "-p", "--model", model, prompt, *images]`
- [ ] Verify cache is written as `style.json` in output_dir
- [ ] Verify fallback DocumentStyle has all required fields

**What We Know Works After This Phase:**
- Claude subprocess calls with retry, timeout handling, and error fallback
- Phase A style detection with disk caching (cache hit skips Claude)
- Image rendering integration (mocked but call signature verified)
- Graceful degradation when Claude is unavailable

---

## Phase 3: repair_structure + enhance_structure Orchestrator

### Goal
Complete the module: Phase B chunked repair and the top-level orchestrator that composes everything. After this phase, the module is feature-complete and ready for Item 3 (pipeline integration).

### Test Stencil (Write This First)

```python
# Add to tests/test_claude_structure.py — Phase 3

class TestRepairStructure:
    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_single_chunk_valid_response(self, mock_claude, mock_render):
        mock_render.return_value = Path("/tmp/page.png")
        mock_claude.return_value = (
            '[{"anchor_text":"The reactor design","level":2,"title":"Reactor Design","insert_position":"before"}]',
            [],
        )
        style = DocumentStyle(doc_type="academic_paper", ...)
        md = "<!-- PAGE:1 -->\nIntro text\n<!-- PAGE:2 -->\nThe reactor design uses..."
        insertions, warnings = repair_structure(md, Path("test.pdf"), style)
        assert len(insertions) == 1
        assert insertions[0].title == "Reactor Design"

    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_multi_chunk_dedup(self, mock_claude, mock_render):
        # 50-page doc → 2 chunks, same insertion in overlap → deduplicated
        ...

    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_invalid_anchor_rejected(self, mock_claude, mock_render):
        mock_render.return_value = Path("/tmp/page.png")
        mock_claude.return_value = (
            '[{"anchor_text":"nonexistent text in doc","level":2,"title":"Bad","insert_position":"before"}]',
            [],
        )
        style = DocumentStyle(...)
        md = "<!-- PAGE:1 -->\nActual content here"
        insertions, warnings = repair_structure(md, Path("test.pdf"), style)
        assert len(insertions) == 0
        assert any("anchor" in w.lower() for w in warnings)

    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_malformed_json_skips_chunk(self, mock_claude, mock_render):
        mock_render.return_value = Path("/tmp/page.png")
        mock_claude.return_value = (None, ["parse failed"])
        style = DocumentStyle(...)
        insertions, warnings = repair_structure("<!-- PAGE:1 -->\nText", Path("t.pdf"), style)
        assert len(insertions) == 0
        assert len(warnings) > 0

class TestEnhanceStructure:
    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_happy_path(self, mock_claude, mock_render, tmp_path):
        mock_render.return_value = Path("/tmp/page.png")
        # Phase A returns style, Phase B returns insertions
        mock_claude.side_effect = [
            ('{"doc_type":"academic_paper","heading_convention":"unnumbered_bold",'
             '"has_toc":false,"running_headers":[],"page_number_format":"none"}', []),
            ('[{"anchor_text":"The main results","level":2,"title":"Results","insert_position":"before"}]', []),
        ]
        md = "<!-- PAGE:1 -->\nIntro\n\nThe main results show that..."
        result, metadata = enhance_structure(md, Path("test.pdf"), tmp_path)
        assert "## Results" in result
        assert metadata["headers_inserted"] == 1

    @patch("agentic_mbse.extraction.claude_structure.render_page_image")
    @patch("agentic_mbse.extraction.claude_structure._call_claude")
    def test_phase_a_failure_graceful(self, mock_claude, mock_render, tmp_path):
        mock_render.return_value = Path("/tmp/page.png")
        mock_claude.return_value = (None, ["claude unavailable"])
        md = "<!-- PAGE:1 -->\nSome text"
        result, metadata = enhance_structure(md, Path("test.pdf"), tmp_path)
        assert metadata["phase_a"]["doc_type"] == "unknown"
        assert metadata["headers_inserted"] == 0
```

### Changes Required

**See `design.md` for:**
- `repair_structure` logic → `design.md#3-repair_structure--phase-b`
- Chunking step → `design.md#3-repair_structure--phase-b` (Step 1)
- Per-chunk validation → `design.md#3-repair_structure--phase-b` (Step 2, item 5)
- Merge/dedup → `design.md#3-repair_structure--phase-b` (Step 3)
- Orchestrator composition → `design.md#6-enhance_structure--orchestrator`
- Phase B prompt → `design.md#3-repair_structure--phase-b` (Phase B prompt)

**Specific file changes:**

#### 1. Test File
**File:** `tests/test_claude_structure.py` (MODIFY)
- [ ] `TestRepairStructure` — 4 tests (single chunk, multi-chunk dedup, invalid anchor, malformed JSON)
- [ ] `TestEnhanceStructure` — 2 tests (happy path, Phase A failure)

#### 2. Implementation File
**File:** `src/agentic_mbse/extraction/claude_structure.py` (MODIFY)
- [ ] `_PHASE_B_PROMPT` template string
- [ ] `repair_structure()` — chunk → per-chunk Claude call → validate → merge/dedup
- [ ] `enhance_structure()` — orchestrator composing Phase A → strip → Phase B → apply

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_claude_structure.py -v` → all ~40 tests pass
- [ ] `uv run pytest tests/ -x` → no regressions (799+ existing tests still pass)
- [ ] `uv run ruff check` + `uv run ruff format --check`
- [ ] `uv run mypy src/agentic_mbse/extraction/claude_structure.py` → no errors

**Manual:**
- [ ] Verify `enhance_structure()` return signature matches `ai_repair.repair_document()` pattern
- [ ] Verify Phase B prompt includes style context from Phase A
- [ ] Verify chunk overlap dedup logic handles identical insertions from adjacent chunks
- [ ] Count lines: module should be ~300 lines, test file ~250 lines (per epic estimates)

**What We Know Works After This Phase:**
- Full module is feature-complete with all 8 public functions
- All ~40 tests pass with mocked Claude calls
- End-to-end orchestrator (Phase A → strip → Phase B → apply) works correctly
- Error handling covers all failure modes (Claude unavailable, malformed JSON, timeout, invalid anchors)
- No regressions on existing 799+ tests
- Module is ready for Item 3 (pipeline integration)

---

## Environment Setup

**See CLAUDE.md for full environment rules**

All commands via `uv run`:
- Tests: `uv run pytest tests/test_claude_structure.py -v`
- Full suite: `uv run pytest tests/ -x`
- Lint: `uv run ruff check src/agentic_mbse/extraction/claude_structure.py tests/test_claude_structure.py`
- Format: `uv run ruff format src/agentic_mbse/extraction/claude_structure.py tests/test_claude_structure.py`
- Types: `uv run mypy src/agentic_mbse/extraction/claude_structure.py`

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: `apply_insertions` reverse-order logic is the trickiest algorithm — test stencil covers it with specific multi-insertion and edge-case tests before any code is written
- **Phase 2**: `_call_claude` retry logic must handle both `subprocess.TimeoutExpired` and `FileNotFoundError` — test stencil explicitly covers both
- **Phase 3**: Chunk overlap dedup is subtle — test stencil includes a 50-page doc that produces 2 chunks with a shared insertion in the overlap zone

## Implementation Notes

*TO BE FILLED DURING IMPLEMENTATION*

### Phase 1 Completion
**Completed:** 2026-02-08
**Actual Changes:**
- Created `src/agentic_mbse/extraction/claude_structure.py` with: `DocumentStyle`, `HeaderInsertion`, `_Chunk` dataclasses; `_parse_json_response()`, `_chunk_by_pages()`, `needs_claude_structure()`, `apply_insertions()`, `strip_detected_headers()` functions
- Created `tests/test_claude_structure.py` with 32 tests across 7 test classes (TestDocumentStyle:3, TestParseJsonResponse:6, TestNeedsClaudeStructure:7, TestChunking:5, TestApplyInsertions:6, TestStripDetectedHeaders:5)
**Issues:**
- `_PAGE_MARKER_RE` needed `re.MULTILINE` flag — the quality_gates.py version works without it because it uses line-by-line `.match()`, but our `findall()` on full string requires multiline
- Chunking math: 50 pages with chunk_size=25, overlap=3 produces 3 chunks (stride=22), not 2 as the plan stencil estimated. Fixed test expectations.
**Deviations:**
- Added 7 extra tests beyond plan stencil: `test_array_json`, `test_empty_string_returns_none`, `test_no_pages_returns_true`, `test_chunk_text_field_matches_lines`, `test_case_insensitive_match`, `test_whitespace_collapsed_match`, `test_empty_patterns_no_change`
- No `confidence` field on `HeaderInsertion` (per design rationale — validation is a better acceptance criterion)

### Phase 2 Completion
**Completed:** 2026-02-08
**Actual Changes:**
- Added `_call_claude()` subprocess helper with retry logic, timeout/FileNotFoundError handling
- Added `_PHASE_A_PROMPT` template, `_FALLBACK_STYLE` default
- Added `detect_document_style()` with cache check → render images → call Claude → parse → cache result
- Added imports: `subprocess`, `Path`, `render_page_image` from `ai_repair`
- Added 10 new tests: `TestCallClaude` (5 tests), `TestDetectDocumentStyle` (5 tests)
**Issues:**
- None
**Deviations:**
- Added `test_all_retries_exhausted` test beyond plan stencil (verifies retry count when all attempts fail)
- `_call_claude` mocked at module level rather than mocking `subprocess.run` for `detect_document_style` tests — cleaner and avoids tight coupling to subprocess internals

### Phase 3 Completion
**Completed:** 2026-02-08
**Actual Changes:**
- Added `_PHASE_B_PROMPT` template string with style context and chunk markdown
- Added `_validate_insertion()` helper for per-insertion validation (anchor exists, level 2-6, valid position)
- Added `repair_structure()` — chunk → per-chunk Claude call with representative page images → validate each insertion → deduplicate across chunks
- Added `enhance_structure()` orchestrator — Phase A → strip running headers → Phase B → apply insertions → return metadata
- Added 6 new tests: `TestRepairStructure` (4 tests: single chunk, multi-chunk dedup, invalid anchor, malformed JSON), `TestEnhanceStructure` (2 tests: happy path, Phase A failure)
**Issues:**
- None
**Deviations:**
- Module is 684 lines (spec estimated ~300) — larger due to prompt templates, comprehensive validation, and error handling. Tests are 637 lines (spec estimated ~250) — more thorough coverage than estimated.
- Extracted `_validate_insertion()` as a helper (not in plan) — cleaner than inline validation in the repair loop

---

**Status**: Draft → In Progress → Complete
