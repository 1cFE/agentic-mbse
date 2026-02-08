# Design: Claude Structure Module — Core Implementation

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-08 15:44 UTC
**Branch:** pdf-extract
**Commit:** 4dae861

---

## Overview

New module `claude_structure.py` that uses Claude to detect document style (Phase A) and insert markdown headers via text-anchored structured diffs (Phase B). It provides the structural backbone that regex header promotion cannot: handling slide decks, italic subsections, unnumbered bold headings, and OCR scans.

## Related Artifacts

- **Spec:** `.project/active/claude-structure-module/spec.md`
- **Epic:** `.project/backlog/epic_pdf-extraction-v3.md` (Item 2)
- **Baseline:** `.project/reports/20260208_pdfv3-baseline.md`

---

## Research Findings

### Existing Claude Invocation Pattern

**File:** `src/agentic_mbse/extraction/ai_repair.py:208-214`

All Claude calls use `subprocess.run(["claude", "-p", prompt, ...])` with:
- `capture_output=True, text=True` for string I/O
- `timeout=120` seconds
- Images passed as filename with `cwd=str(image_path.parent)`
- No `--model` flag used anywhere in the codebase yet

For this module, we'll add `--model haiku` (Phase A) and `--model sonnet` (Phase B) per design decision D7. The `claude` CLI accepts `--model <alias>` where aliases include `haiku`, `sonnet`, `opus`.

### Page Marker Format

**File:** `src/agentic_mbse/extraction/pymupdf_backend.py:73`

Markers are `<!-- PAGE:N -->` where N is **1-indexed** (from pymupdf4llm metadata).

**File:** `src/agentic_mbse/extraction/quality_gates.py:19`

Regex: `r"^<!--\s*PAGE:(\d+)\s*-->$"` — we'll reuse this exact pattern.

### Image Rendering

**File:** `src/agentic_mbse/extraction/ai_repair.py:122-143`

`render_page_image(pdf_path, page_num, dpi=200)` returns a `Path` to a temp PNG. Caller owns cleanup. Uses `pymupdf` with DPI-to-matrix conversion. Page numbers are **0-indexed**.

### Postprocess Header Promotion

**File:** `src/agentic_mbse/extraction/postprocess.py:109-148`

Regex header promotion runs in `postprocess()` (called by pymupdf_backend) **before** any Layer 2/3/4 enhancement. This means by the time `claude_structure.py` sees the markdown, regex-promoted headers are already in place. The module must detect these existing headers and avoid duplicating them.

### Test Mocking Pattern

**File:** `tests/test_ai_repair.py:236-243`

```python
@patch("agentic_mbse.extraction.ai_repair.render_page_image")
@patch("agentic_mbse.extraction.ai_repair.subprocess.run")
def test_successful_table_repair(self, mock_run, mock_render):
    mock_render.return_value = Path("/tmp/test_page.png")
    mock_run.return_value = MagicMock(returncode=0, stdout="...")
```

Uses `unittest.mock.patch` as decorators, stacked (innermost is last param). We'll follow this exact pattern.

### Pipeline Integration Point

**File:** `src/agentic_mbse/cli/extract_cli.py:252-269`

Currently: L2 (GMFT) → L3 (AI repair). The new structural pass will be inserted between these as the new L3, pushing AI repair to L4. But this is Item 3 scope — the module itself is standalone.

### Existing Dataclass Patterns

**File:** `src/agentic_mbse/extraction/base.py:17-42`

Uses `@dataclass` from stdlib. Serialization is manual via `json.dumps()` in `write_summary()`. No pydantic or dataclass-json. We'll follow the same pattern with manual `to_dict()`/`from_dict()` for JSON serialization.

---

## Proposed Design

### Module Location

`src/agentic_mbse/extraction/claude_structure.py`

### Data Structures

```python
@dataclass
class DocumentStyle:
    doc_type: str           # "academic_paper" | "slide_deck" | "technical_report" | "ocr_scan" | "word_doc"
    heading_convention: str # "numbered_bold" | "unnumbered_bold" | "italic_subsections" | "slide_titles" | "mixed"
    has_toc: bool
    running_headers: list[str]    # patterns detected as running headers
    page_number_format: str       # "bare" | "bold" | "none" | "footer"

    def to_dict(self) -> dict: ...

    @classmethod
    def from_dict(cls, d: dict) -> "DocumentStyle": ...
```

`DocumentStyle` is a plain dataclass with manual JSON serialization. The `running_headers` field is a list of string patterns (e.g., `["Author Name", "Journal Title"]`) rather than compiled regexes, so it serializes cleanly.

```python
@dataclass
class HeaderInsertion:
    anchor_text: str        # text snippet to locate in markdown (not a line number)
    level: int              # 2-6, mapping to ## through ######
    title: str              # header text to insert
    insert_position: str    # "before" | "after" the anchor_text
```

`HeaderInsertion` is ephemeral (not cached to disk), so no serialization needed. It represents one instruction: "insert `## {title}` before/after the line containing `anchor_text`".

**Why no `confidence` field:** The spec suggests one as [INFERRED], but it adds complexity without clear benefit — Claude's JSON response doesn't naturally produce confidence scores, and validation (anchor matching, level consistency) is a better acceptance criterion than a synthetic score. If needed later, it's a trivial addition.

### Function Signatures

```python
# --- Gate ---
def needs_claude_structure(md: str) -> bool

# --- Phase A ---
def detect_document_style(
    md: str,
    pdf_path: Path,
    output_dir: Path,
    model: str = "haiku",
) -> tuple[DocumentStyle, list[str]]

# --- Phase B ---
def repair_structure(
    md: str,
    pdf_path: Path,
    style: DocumentStyle,
    model: str = "sonnet",
) -> tuple[list[HeaderInsertion], list[str]]

# --- Application ---
def apply_insertions(md: str, insertions: list[HeaderInsertion]) -> tuple[str, int, int, list[str]]

# --- Running header strip ---
def strip_detected_headers(md: str, patterns: list[str]) -> str

# --- Orchestrator ---
def enhance_structure(
    md: str,
    pdf_path: Path,
    output_dir: Path,
    phase_a_model: str = "haiku",
    phase_b_model: str = "sonnet",
) -> tuple[str, dict]
```

Every function that can produce warnings returns `tuple[result, list[str]]`. Exception: `apply_insertions()` returns `tuple[str, int, int, list[str]]` — `(modified_md, inserted_count, skipped_count, warnings)` — to provide explicit metrics rather than inferring counts from warning list length. The orchestrator `enhance_structure()` composes them and returns `tuple[str, dict]` matching the established pattern from `ai_repair.repair_document()` (`extract_cli.py:256`).

### Component Design

#### 1. `needs_claude_structure(md: str) -> bool`

Pure function. No I/O. Computes three metrics from the markdown text:

1. **`headers_per_page`**: Count lines matching `^#{2,6} ` divided by count of `<!-- PAGE:N -->` markers. Threshold: `< 0.1` → needs Claude.
2. **`noise_fraction`**: Among lines matching `^#{2,6} `, what fraction are "noise" (reuses `_is_noise_header()` logic from `postprocess.py:294-315`)? Threshold: `> 0.3` → needs Claude.
3. **`depth_variance`**: Among valid (non-noise) headers, do multiple levels exist (## and ### and/or ####)? Zero depth variance is a **weak signal** — it only triggers when `headers_per_page >= 0.1` (i.e., there are a reasonable number of headers but they're all flat). This prevents false positives on short, legitimately simple documents (e.g., a 2-page doc with just `## Introduction` and `## Conclusion`).

**Trigger logic:** Returns `True` if `headers_per_page < 0.1` OR `noise_fraction > 0.3` OR (`headers_per_page >= 0.1` AND zero depth variance).

**Implementation note:** We'll import and reuse `_is_noise_header` from postprocess.py rather than duplicating it. Since it's a private function, we'll reference it as `from agentic_mbse.extraction.postprocess import _is_noise_header`. This is acceptable within the same package — it's a stable utility function.

#### 2. `detect_document_style()` — Phase A

**Inputs:** Markdown text, PDF path, output directory, model name.

**Cache check:** If `{output_dir}/style.json` exists, load and return `DocumentStyle.from_dict()`.

**If not cached:**

1. Extract first ~200 lines of markdown (up to but not including the line after `<!-- PAGE:4 -->`, giving us pages 1–3 worth of content).
2. Render pages 0, 1, 2 as thumbnails via `render_page_image(pdf_path, page_num, dpi=150)`. Lower DPI (150 vs 200) because style detection needs layout, not OCR detail.
3. Build prompt asking Claude to classify the document. Prompt requests a JSON response with the `DocumentStyle` fields.
4. Call `subprocess.run(["claude", "-p", "--model", model, prompt, img0, img1, img2], ...)` with `cwd` set to the temp directory containing images.
5. Parse JSON from `stdout` via `_parse_json_response()` (see below). Validate required fields exist.
6. On malformed JSON: retry once. On second failure: return a fallback `DocumentStyle(doc_type="unknown", heading_convention="unknown", has_toc=False, running_headers=[], page_number_format="none")` with warning.
7. Write successful result to `{output_dir}/style.json`.
8. Clean up temp images in `finally` block.

**Prompt design (Phase A):**

```
You are analyzing a PDF document's structure. Based on the page images and
the first few pages of extracted markdown below, classify the document.

Return ONLY a JSON object with these fields:
- doc_type: one of "academic_paper", "slide_deck", "technical_report", "ocr_scan", "word_doc"
- heading_convention: one of "numbered_bold", "unnumbered_bold", "italic_subsections", "slide_titles", "mixed"
- has_toc: true if the document has a table of contents
- running_headers: list of repeated header/footer text strings (empty list if none)
- page_number_format: one of "bare", "bold", "none", "footer"

Markdown (first ~200 lines):
```{markdown}```
```

**Why 3 pages, not more:** Style is evident from the first few pages. Sending more increases cost without improving classification accuracy. The epic specifies "first 3 pages" explicitly.

#### 3. `repair_structure()` — Phase B

**Inputs:** Full markdown text, PDF path, `DocumentStyle` from Phase A, model name.

**Step 1 — Chunking:**

Split markdown into chunks using `<!-- PAGE:N -->` markers:
- Target: ~25 pages per chunk (adjustable)
- Overlap: 3 pages (last 3 pages of chunk N are the first 3 pages of chunk N+1)
- Each chunk is a contiguous slice of lines from the markdown

Algorithm:
```
page_starts = {N: line_index for each <!-- PAGE:N --> marker}
sorted_pages = sorted(page_starts.keys())
chunk_size = 25
overlap = 3

chunks = []
i = 0
while i < len(sorted_pages):
    start_page = sorted_pages[i]
    end_page_idx = min(i + chunk_size, len(sorted_pages))
    end_page = sorted_pages[end_page_idx] if end_page_idx < len(sorted_pages) else None

    start_line = page_starts[start_page]
    end_line = page_starts[end_page] if end_page else len(lines)

    chunks.append(ChunkInfo(start_page, end_page, start_line, end_line, lines[start_line:end_line]))
    i += chunk_size - overlap
```

**Step 2 — Per-chunk Claude call:**

For each chunk:
1. Pick 1–2 representative page images from the chunk (first page + middle page if chunk > 10 pages). **Index conversion:** `_Chunk.start_page` is 1-indexed (from PAGE markers); call `render_page_image(pdf_path, chunk.start_page - 1)` for the 0-indexed pymupdf page.
2. Build prompt with: style context (from Phase A, serialized as brief description), chunk markdown, instruction to identify headings.
3. Call `subprocess.run(["claude", "-p", "--model", model, prompt, img1, img2], ...)`.
4. Parse JSON response via `_parse_json_response()` as `list[dict]`, convert to `list[HeaderInsertion]`.
5. Validate each insertion:
   - `anchor_text` must appear in the chunk's markdown (exact substring match)
   - `level` must be 2–6
   - `insert_position` must be "before" or "after"
   - Reject any insertion that fails validation, with warning
6. Clean up temp images.

**Prompt design (Phase B):**

```
You are adding markdown section headers to a document excerpt.
The document is a {style.doc_type} with {style.heading_convention} heading style.

For each heading you identify, return a JSON array of objects with:
- anchor_text: a unique text snippet (15-60 chars) from the line where or near where the heading should go
- level: heading level (2 for ##, 3 for ###, etc.)
- title: the heading text
- insert_position: "before" to insert the heading before the anchor line

Rules:
- Use text that appears EXACTLY in the markdown below as anchor_text
- Do NOT include any existing markdown headers (lines starting with #) — only identify MISSING headers
- Keep the heading hierarchy consistent (## for top-level, ### for subsections)

Markdown excerpt:
```{chunk_markdown}```
```

**Step 3 — Merge across chunks:**

Collect all `HeaderInsertion` objects from all chunks. Deduplicate: if two insertions have the same `anchor_text` and `title`, keep only one (prefer the one from the chunk where the anchor is not in the overlap zone).

**Step 4 — Return:** `(merged_insertions, all_warnings)`

#### 4. `apply_insertions()`

**Inputs:** Full markdown text, list of `HeaderInsertion`.

**Algorithm:**

1. Split markdown into lines.
2. For each insertion, find the line index where `anchor_text` appears:
   - Search for `anchor_text` as a substring in each line
   - If found in exactly one line: use that line index
   - If found in multiple lines: skip with warning ("ambiguous anchor")
   - If found in zero lines: skip with warning ("anchor not found")
3. Sort found insertions by line index, descending (so insertions don't shift indices of subsequent insertions).
4. For each insertion (in reverse order):
   - Build header line: `"#" * insertion.level + " " + insertion.title`
   - Check if the header already exists within ±2 lines (prevents duplication with regex-promoted headers)
   - If `insert_position == "before"`: insert header + blank line before the anchor line
   - If `insert_position == "after"`: insert blank line + header after the anchor line
5. Rejoin lines and return `(joined_text, inserted_count, skipped_count, warnings)`.

**Why explicit counters:** The spec requires `headers_inserted` and `headers_skipped` in metadata. Inferring these from `len(insertions) - len(warnings)` is lossy because warnings include multiple failure categories (anchor not found, ambiguous anchor, duplicate header). Explicit counters are unambiguous.

**Why reverse order:** Inserting lines changes indices. Processing from bottom to top preserves indices for subsequent insertions (same pattern as `ai_repair.repair_document` at `ai_repair.py:289`).

**Duplicate prevention:** Before inserting, check if a header with the same title (normalized: lowercase, stripped of leading `#` and whitespace) already exists within ±2 lines of the insertion point. If so, skip with warning "header already exists". This handles the case where regex promotion already placed the header correctly.

#### 5. `strip_detected_headers()`

**Inputs:** Markdown text, list of running header patterns from `DocumentStyle.running_headers`.

Targeted removal: for each pattern string, remove any line that equals the pattern after normalization (case-insensitive, whitespace-collapsed), regardless of whether it's between blank lines. This is more aggressive than `postprocess.strip_running_headers()` (which uses frequency-based detection on standalone blocks), but safe because patterns come from Phase A's explicit detection — false positives are unlikely when Claude has identified a specific running header string.

#### 6. `enhance_structure()` — Orchestrator

Composes all components:

```python
def enhance_structure(md, pdf_path, output_dir, phase_a_model="haiku", phase_b_model="sonnet"):
    warnings = []
    metadata = {"phase_a": None, "phase_b": None, "headers_inserted": 0, "headers_skipped": 0}

    # Phase A
    style, a_warnings = detect_document_style(md, pdf_path, output_dir, model=phase_a_model)
    warnings.extend(a_warnings)
    metadata["phase_a"] = style.to_dict()

    # Running header strip (post-Phase-A)
    if style.running_headers:
        md = strip_detected_headers(md, style.running_headers)

    # Phase B
    insertions, b_warnings = repair_structure(md, pdf_path, style, model=phase_b_model)
    warnings.extend(b_warnings)

    # Apply
    md, inserted, skipped, apply_warnings = apply_insertions(md, insertions)
    warnings.extend(apply_warnings)

    metadata["headers_inserted"] = inserted
    metadata["headers_skipped"] = skipped
    metadata["warnings"] = warnings
    return md, metadata
```

### Error Handling Strategy

| Failure | Behavior | Fallback |
|---------|----------|----------|
| `claude` CLI not found | `FileNotFoundError` caught | Return unchanged markdown + warning |
| Claude returns non-zero exit code | Retry once | Skip that phase/chunk + warning |
| Claude returns malformed JSON | Retry once | Phase A: fallback `DocumentStyle`; Phase B: skip chunk |
| `subprocess.TimeoutExpired` | Caught | Same as non-zero exit code |
| `render_page_image` fails | Caught per-image | Proceed without that image (or skip chunk if no images available) |
| Anchor text not found | Per-insertion skip | Warning + skip that insertion |
| Ambiguous anchor (multiple matches) | Per-insertion skip | Warning + skip that insertion |

All warnings are collected in lists and returned to the caller. No exceptions escape the module except for truly unexpected errors (programming bugs).

### JSON Response Parser

Claude's `-p` mode doesn't enforce JSON output. Responses may be wrapped in markdown fences (`` ```json ... ``` ``), contain leading/trailing prose, or include other formatting. A shared helper strips these before parsing:

```python
def _parse_json_response(text: str) -> Any | None:
    """Parse JSON from Claude's stdout, stripping common wrappers.

    Handles: bare JSON, markdown-fenced JSON (```json ... ```),
    leading/trailing prose around a JSON block. Returns None if
    no valid JSON found.
    """
```

This is ~10 lines (regex to extract fenced blocks, then `json.loads`), reused by both Phase A and Phase B, and eliminates unnecessary retries caused by markdown-wrapped responses.

### Subprocess Call Helper

To avoid duplicating the retry/error-handling logic, extract a helper:

```python
def _call_claude(
    prompt: str,
    image_paths: list[Path],
    model: str,
    timeout: int = 120,
    retries: int = 1,
) -> tuple[str | None, list[str]]:
    """Call claude -p with optional images and retry logic.

    Returns (stdout_text, warnings) or (None, warnings) on failure.
    """
```

This encapsulates: building the command (`["claude", "-p", "--model", model, prompt, *image_names]`), setting `cwd`, handling `FileNotFoundError`, `TimeoutExpired`, non-zero return codes, and retry.

### Chunking Helper

```python
@dataclass
class _Chunk:
    start_page: int       # 1-indexed page number
    end_page: int | None  # None = end of document
    start_line: int       # line index in full markdown
    end_line: int         # line index (exclusive)
    text: str             # the chunk's markdown text

def _chunk_by_pages(
    lines: list[str],
    chunk_size: int = 25,
    overlap: int = 3,
) -> list[_Chunk]:
```

### Page Marker Parsing

Reuse the regex from `quality_gates.py:19`:

```python
_PAGE_MARKER_RE = re.compile(r"^<!--\s*PAGE:(\d+)\s*-->$")
```

We'll define our own copy rather than importing the private `_PAGE_MARKER_RE` from quality_gates — it's a one-line regex and avoids cross-module coupling on private names.

For `needs_claude_structure()`, we parse page markers to count pages, and `^#{2,6} ` to count headers.

---

## Potential Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Claude returns headers for text that already has regex-promoted headers | Medium | Low | `apply_insertions()` checks ±2 lines for existing headers with same title |
| `anchor_text` is too generic (e.g., "Introduction") and matches multiple locations | Medium | Medium | Prompt instructs Claude to use 15-60 char unique snippets; validation rejects ambiguous matches |
| Chunk boundaries split a heading's context from its content | Medium | Low | 3-page overlap ensures context spans boundaries; dedup handles duplicates |
| `needs_claude_structure()` misclassifies well-structured docs as needing Claude | Low | Low | Conservative thresholds tuned to corpus profiles (0.1 headers/page, 0.3 noise); wrong direction costs money but doesn't degrade quality |
| Phase A caching prevents re-detection after document re-extraction | Low | Low | Cache is in output_dir which gets regenerated with `--force`; also keyed to the output directory, not the PDF |

---

## Integration Strategy

This module is **standalone** — Item 3 wires it into the pipeline. The integration surface is:

1. **Caller provides:** `md` (post-postprocess markdown), `pdf_path`, `output_dir`
2. **Module returns:** `(modified_md, metadata_dict)`
3. **No imports from this module by existing code** — only Item 3 adds the import in `extract_cli.py`
4. **Reuses from existing code:**
   - `render_page_image()` from `ai_repair.py:122` (imported, not copied)
   - `_is_noise_header()` from `postprocess.py:294` (imported for `needs_claude_structure`)

---

## Validation Approach

### Test File: `tests/test_claude_structure.py`

**Test categories:**

1. **`TestNeedsClaudeStructure`** (~6 tests)
   - Sparse headers (0.05/page) → True
   - Dense headers (0.5/page) → False
   - High noise fraction → True
   - Zero depth variance → True
   - Mixed triggers → True
   - Well-structured document profile → False

2. **`TestDocumentStyle`** (~3 tests)
   - `to_dict()` / `from_dict()` round-trip
   - JSON serialization/deserialization
   - Handles missing optional fields gracefully

3. **`TestDetectDocumentStyle`** (~5 tests, all mock `subprocess.run` and `render_page_image`)
   - Valid JSON response → correct `DocumentStyle`
   - Cache hit → no subprocess call
   - Malformed JSON → retry once → fallback
   - Timeout → fallback
   - `claude` not found → fallback

4. **`TestChunking`** (~4 tests)
   - 10-page document → 1 chunk
   - 50-page document → 2 chunks with overlap
   - 100-page document → correct number of chunks
   - Overlap pages appear in adjacent chunks

5. **`TestRepairStructure`** (~4 tests, all mock subprocess)
   - Single chunk → valid `list[HeaderInsertion]`
   - Multi-chunk → merged, deduplicated
   - Invalid anchor in response → rejected with warning
   - Malformed JSON → skip chunk with warning

6. **`TestApplyInsertions`** (~6 tests)
   - Single insertion before anchor
   - Single insertion after anchor
   - Multiple insertions (reverse-order correctness)
   - Anchor not found → skip with warning
   - Ambiguous anchor → skip with warning
   - Duplicate header prevention (existing header within ±2 lines)

7. **`TestStripDetectedHeaders`** (~2 tests)
   - Known pattern removed from multiple locations
   - Non-matching content preserved

8. **`TestEnhanceStructure`** (~2 tests, full orchestration with mocks)
   - Happy path: Phase A → strip → Phase B → apply
   - Phase A failure → graceful degradation

**Total: ~32 tests**

### Mocking Strategy

All `subprocess.run` and `render_page_image` calls mocked via `@patch`:
```python
@patch("agentic_mbse.extraction.claude_structure.render_page_image")
@patch("agentic_mbse.extraction.claude_structure.subprocess.run")
def test_detect_style_valid(self, mock_run, mock_render):
    mock_render.return_value = Path("/tmp/page.png")
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout='{"doc_type": "academic_paper", ...}',
    )
```

### Corpus Profile Validation

For `needs_claude_structure()`, we'll create test fixtures based on the baseline report metrics:

| Document | ## Hdrs | Pages | Headers/Page | Expected |
|----------|---------|-------|-------------|----------|
| 2241 (ICRH) | 7 | 30 | 0.23 | `False` |
| 2232 (Handley) | 7 | 17 | 0.41 | `False` |
| 2236 (Digital Twins) | 19 | 66 | 0.29 | `False` |
| safety (slides) | 0 | 14 | 0.00 | `True` |
| fusion-std (OCR) | 0 | 4 | 0.00 | `True` |
| hazards (Word) | 0 | 8 | 0.00 | `True` |
| 2243 (slides) | 57 | 127 | 0.45 | `True` (noise > 0.3) |

---

**Next Step:** After approval → `/_my_plan`
