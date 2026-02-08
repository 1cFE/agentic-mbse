# Design: Document Extraction

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-03 00:36 UTC
**Branch:** pdf-extract
**Commit:** 2d07054

---

## Overview

Integrate document extraction (PDF and DOCX to structured markdown) directly into agentic-mbse as a new `extract` CLI subcommand, replacing the external m-scout dependency with a self-contained pipeline that produces `full_document.md` + `images/` + optional `INDEX.md`.

## Related Artifacts

- **Spec:** `.project/active/document-extraction/spec.md`
- **Reference implementation:** `~/m-scout/tools/pdf_processing/`
- **Existing scripts:** `scripts/generate_index.py`, `scripts/read_section.py`

## Research Findings

### Existing CLI Patterns (`src/agentic_mbse/cli/__init__.py`)

- Subcommands registered via `subparsers.add_parser()` at line:1071
- Handler functions return `EXIT_SUCCESS` (0) or `EXIT_FAILURE` (1)
- Complex subcommand groups delegated to separate modules (pm_cli pattern at line:1161-1164)
- Lazy imports used in `pm_cli.py` to avoid loading heavy dependencies at startup

### Reference Implementation Analysis (`~/m-scout/tools/pdf_processing/`)

The m-scout implementation provides a working extraction pipeline with:

1. **`pdf_process.py`**: Entry point with processor selection, file discovery, hash-based skip detection, and automatic fallback (Docling → PyMuPDF)
2. **`pdf_processor_docling.py`**: Docling-based extraction — converts PDF, exports markdown, chunks via HierarchicalChunker, saves images. Key settings: `do_table_structure=True`, `generate_picture_images=True`
3. **`pdf_processor_pymupdf.py`**: PyMuPDF4LLM fallback — `pymupdf4llm.to_markdown()` with `write_images=True`, chapter extraction, paragraph-based chunking
4. **`pdf_naming.py`**: Utilities for sanitized filenames and output paths

### Key Simplification for agentic-mbse

The spec explicitly states **no physical chunking** (out of scope). The agentic-mbse philosophy is `full_document.md` + `INDEX.md`. This means we can drop all the chunking logic (HierarchicalChunker, HybridChunker, chunk splitting) and focus on:
- Full document markdown export
- Image extraction
- Summary metadata
- Optional index generation (via existing `generate_index.py`)

### Existing Scripts to Integrate

- **`scripts/generate_index.py`** (317 lines): Parses numbered section headers, generates AI summaries via `claude -p`. Has checksum-based change detection. Currently standalone — needs to be callable as a library function.
- **`scripts/read_section.py`** (147 lines): Reads specific sections using INDEX.md line ranges. Already works with `full_document.md` output format.

### DOCX Considerations

- Docling supports DOCX natively via its `DocumentConverter`
- Pandoc is the proven fallback for DOCX → markdown conversion
- Pandoc can extract images with `--extract-media`

### Dependency Landscape

| Package | Purpose | Size Impact |
|---------|---------|-------------|
| `docling` | Primary extractor (ML-based table/image detection) | Heavy (~500MB+ with models) |
| `pymupdf4llm` | PDF fallback (fast, reliable) | Moderate (~50MB) |
| `pandoc` (system) | DOCX fallback | System binary |

Current `pyproject.toml` uses optional dependencies for `dev` group (line:29-35). Same pattern applies for `extract`.

## Proposed Design

### Architecture Overview

```
agentic-mbse extract <file-or-dir> [options]
        │
        ▼
┌─────────────────┐
│  extract_cli.py  │  CLI argument parsing + orchestration
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌────────────────┐
│  extractors/     │     │  index.py       │  (moved from scripts/)
│  ├─ base.py      │     │  generate_index  │
│  ├─ docling.py   │     │  + read_section  │
│  └─ pymupdf.py   │     └────────────────┘
└─────────────────┘
```

### Component 1: CLI Registration (`src/agentic_mbse/cli/__init__.py`)

Add `extract` subcommand registration following the existing delegation pattern (like `pm` at line:1161-1164).

**Changes to `__init__.py`**: Inside `main()`, after the pm registration block (line:1164), add:

```python
# extract command (delegated to extract_cli module)
from agentic_mbse.cli.extract_cli import register_extract_subcommand
register_extract_subcommand(subparsers)
```

This matches the pm_cli import pattern — inside `main()`, not at module level — so extraction dependencies are only loaded when the CLI is actually invoked.

**CLI interface:**

```
agentic-mbse extract <path> [options]

Positional:
  path                  PDF/DOCX file or directory containing documents

Options:
  --output DIR, -o DIR  Output directory (default: alongside input file)
  --backend BACKEND     Force backend: docling, pymupdf, pandoc (default: auto)
  --timeout SECONDS     Timeout for primary extractor (default: 600)
  --force, -f           Reprocess even if already done
  --index               Generate INDEX.md after extraction
  --summarize           Include AI summaries in INDEX.md (requires --index)
  --fix-tables          Run two-pass table repair via Claude headless mode
```

### Component 2: Extract CLI Module (`src/agentic_mbse/cli/extract_cli.py`)

**Purpose:** Argument parsing, file discovery, orchestration of extraction + post-processing.

**Key functions:**

```python
def register_extract_subcommand(subparsers) -> None:
    """Register the 'extract' subcommand."""

def cmd_extract(args: argparse.Namespace) -> int:
    """Main extract command handler."""

def discover_documents(path: Path) -> list[Path]:
    """Find all PDF/DOCX files in path. Single file: validate extension and return.
    Directory: flat listing only (no recursive glob) — matches m-scout behavior.
    Returns sorted list."""

def select_backend(file_path: Path, requested: str | None) -> str:
    """Select extraction backend. Auto mode: docling → pymupdf (PDF) or docling → pandoc (DOCX)."""
```

**Orchestration flow in `cmd_extract`:**

1. Validate input path exists
2. Discover documents (PDF/DOCX)
3. For each document:
   a. Check if processing needed (hash-based, skip if unchanged unless `--force`)
   b. Select backend (auto or forced)
   c. Run primary extractor with timeout
   d. On failure/timeout → run fallback extractor
   e. Write `summary.json` metadata
4. If `--index`: run index generation on each `full_document.md`
5. If `--fix-tables`: run table repair pass
6. Print summary (processed/skipped/failed counts)

### Component 3: Extractor Backends (`src/agentic_mbse/extraction/`)

New package with a simple base class and backend implementations.

#### `base.py` — Common types and interface

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class ExtractionResult:
    """Result of a document extraction."""
    success: bool
    output_dir: Path
    markdown_path: Path | None = None
    image_count: int = 0
    char_count: int = 0
    error: str | None = None
    backend_used: str = ""

def sanitize_filename(name: str) -> str:
    """Create filesystem-safe name from document filename."""
    # Port from m-scout pdf_naming.py

def get_output_dir(input_path: Path, output_base: Path | None = None) -> Path:
    """Determine output directory for a given input file."""

def check_processing_needed(input_path: Path, output_dir: Path, force: bool = False) -> bool:
    """Check if file needs (re)processing via hash comparison with summary.json."""

def write_summary(input_path: Path, output_dir: Path, result: ExtractionResult, backend: str) -> None:
    """Write summary.json metadata file."""

def run_with_timeout(func, args, timeout: int):
    """Run func(*args) in a child process with timeout.
    Returns func's return value, or None on timeout.
    Uses multiprocessing.Process + Queue."""
```

**`summary.json` schema** (written by `write_summary`):

```json
{
  "source_file": "report.pdf",
  "source_format": "pdf",
  "processed_at": "2026-02-03T00:36:00",
  "backend_used": "pymupdf",
  "processing_completed": true,
  "file_hash": "md5:abc123...",
  "statistics": {
    "total_images": 15,
    "total_characters": 125000,
    "file_size_bytes": 2048576
  },
  "error": null
}
```

Fields:
- `source_file` (str): Original filename
- `source_format` (str): `"pdf"` or `"docx"`
- `processed_at` (str): ISO 8601 timestamp
- `backend_used` (str): `"docling"`, `"pymupdf"`, or `"pandoc"`
- `processing_completed` (bool): `true` on success, `false` on error
- `file_hash` (str): `"md5:<hex>"` for change detection
- `statistics` (object): `total_images` (int), `total_characters` (int), `file_size_bytes` (int)
- `error` (str | null): Error message if `processing_completed` is `false`

#### `docling_backend.py` — Docling extractor

```python
def extract(input_path: Path, output_dir: Path, timeout: int = 600) -> ExtractionResult:
    """Extract document using Docling.

    Supports both PDF and DOCX.
    Runs in a subprocess with timeout to handle memory issues.
    Saves full_document.md + images/.
    """
```

Key implementation details:
- **Lazy import**: `docling` only imported inside the function (heavy dependency)
- **Timeout via `multiprocessing`**: Run extraction in a child process with configurable timeout. This handles both wall-clock timeout and memory exhaustion (child process killed cleanly)
- **Docling settings**: `do_table_structure=True`, `generate_picture_images=True`, `do_ocr=False`
- **Export**: `result.document.export_to_markdown()` for full document, iterate `result.document.pictures` for images
- **Image path rewriting**: Ensure markdown references point to `images/` relative path

#### `pymupdf_backend.py` — PyMuPDF4LLM extractor (PDF only)

```python
def extract(input_path: Path, output_dir: Path) -> ExtractionResult:
    """Extract PDF using PyMuPDF4LLM.

    Fast, reliable fallback. No timeout needed (completes quickly).
    """
```

Key implementation details:
- Uses `pymupdf4llm.to_markdown(str(path), write_images=True, image_path=str(images_dir), image_format="png", dpi=150, page_chunks=False)`
- Produces `full_document.md` with embedded `![](images/...)` references
- No chunking (spec: out of scope)

#### `pandoc_backend.py` — Pandoc extractor (DOCX only)

```python
def extract(input_path: Path, output_dir: Path) -> ExtractionResult:
    """Extract DOCX using Pandoc subprocess.

    Proven best-in-class for DOCX. Requires pandoc system binary.
    """
```

Key implementation details:
- Runs `pandoc --from=docx --to=markdown --extract-media=images/ -o full_document.md input.docx` via `subprocess.run`
- Check for `pandoc` binary availability, raise clear error if missing
- Post-process image paths to be relative

### Component 4: Index Generation (`src/agentic_mbse/extraction/index.py`)

**Purpose:** Move `generate_index.py` logic into a callable library module. Keep `scripts/generate_index.py` as a thin CLI wrapper for backward compatibility.

```python
def generate_index(
    doc_path: Path,
    depth: int = 3,
    summarize: bool = False,
    force: bool = False,
) -> Path | None:
    """Generate INDEX.md for a full_document.md file.

    Returns path to INDEX.md on success, None if skipped (up to date).
    """

def parse_sections(content: str, max_depth: int) -> list[Section]:
    """Parse numbered section headers from markdown."""

def read_section(doc_path: Path, section_num: str, context: int = 0) -> str:
    """Read a specific section using INDEX.md metadata."""
```

The existing `Section` dataclass and `build_hierarchy`, `format_index_md`, `generate_summary` functions port directly. The `--summarize` flag controls whether AI summaries are generated (maps to `--summarize` on the extract CLI, which sets `summarize=True`).

**Script refactoring:** `scripts/generate_index.py` and `scripts/read_section.py` are reduced to thin wrappers that import from the library. Example for `generate_index.py`:

```python
#!/usr/bin/env python3
"""Generate INDEX.md — thin wrapper around agentic_mbse.extraction.index."""
from agentic_mbse.extraction.index import cli_main

if __name__ == "__main__":
    cli_main()
```

The `cli_main()` function in `extraction/index.py` contains the argparse setup and orchestration currently in `scripts/generate_index.py:main()`. Same pattern for `read_section.py` → `extraction/index.read_section_cli_main()`.

### Component 5: Table Repair (`src/agentic_mbse/extraction/table_repair.py`)

**Purpose:** Two-pass table repair using Claude headless mode.

```python
def repair_tables(markdown_path: Path) -> bool:
    """Fix broken markdown tables using Claude headless mode.

    Pass 1: Identify broken tables (malformed columns, missing headers)
    Pass 2: Send each broken table to 'claude -p' for repair

    Returns True if any tables were repaired.
    """
```

Key implementation details:
- Parse markdown for table blocks (lines starting with `|`)
- Validate each table (consistent column counts, header separator row)
- For broken tables, call `claude -p "Fix this markdown table: ..."` via subprocess
- Replace broken table with repaired version in-place
- This is opt-in (`--fix-tables` flag)

### Fallback Strategy

```
PDF:   docling (with timeout) → pymupdf4llm → fail with message
DOCX:  docling (with timeout) → pandoc      → fail with message
```

Backend selection logic in `select_backend()`:

1. If `--backend` specified: use that, fail if unavailable
2. Auto mode: check what's installed, prefer docling, fall back as above
3. If nothing installed: print install instructions and exit

### Timeout Implementation (`base.py :: run_with_timeout`)

Uses `multiprocessing.Process` with a `Queue` for the result:

```python
import multiprocessing

def run_with_timeout(func, args, timeout):
    """Run func(*args) in a child process with timeout.

    Located in base.py. Used by docling_backend.extract().
    ExtractionResult with Path fields is picklable (dataclass + Path).
    """
    queue = multiprocessing.Queue()

    def wrapper(q, *a):
        try:
            result = func(*a)
            q.put(result)
        except Exception as e:
            q.put(e)

    proc = multiprocessing.Process(target=wrapper, args=(queue, *args))
    proc.start()
    proc.join(timeout=timeout)

    if proc.is_alive():
        proc.terminate()
        proc.join(5)
        if proc.is_alive():
            proc.kill()
        return None  # Timed out

    return queue.get_nowait() if not queue.empty() else None
```

This cleanly handles memory exhaustion (child process killed by OS) and wall-clock timeout. Note: `ExtractionResult` contains `Path` objects and primitive types — all picklable via `multiprocessing.Queue` without issue.

### Dependencies Configuration (`pyproject.toml`)

```toml
[project.optional-dependencies]
extract = ["pymupdf4llm>=0.0.17"]
extract-full = ["docling>=2.0", "pymupdf4llm>=0.0.17"]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "mypy>=1.0",
    "ruff>=0.1",
]
```

See [Design Decisions: Tiered Dependency Extras](#decision-tiered-dependency-extras) for rationale.

### Output Structure

For `agentic-mbse extract report.pdf --index`:

```
report/
├── full_document.md     # Complete markdown document
├── INDEX.md             # Section index with line numbers (optional)
├── summary.json         # Processing metadata
└── images/
    ├── figure_001.png
    ├── figure_002.png
    └── ...
```

### File Layout

```
src/agentic_mbse/
├── cli/
│   ├── __init__.py          # +3 lines: register extract subcommand
│   ├── extract_cli.py       # NEW: CLI arg parsing + orchestration (~200 lines)
│   └── pm_cli.py            # (existing, unchanged)
├── extraction/
│   ├── __init__.py           # NEW: package init, re-exports
│   ├── base.py               # NEW: ExtractionResult, utilities (~80 lines)
│   ├── docling_backend.py    # NEW: Docling extraction (~100 lines)
│   ├── pymupdf_backend.py    # NEW: PyMuPDF4LLM extraction (~60 lines)
│   ├── pandoc_backend.py     # NEW: Pandoc DOCX extraction (~70 lines)
│   ├── index.py              # NEW: Index generation (ported from scripts/, ~200 lines)
│   └── table_repair.py       # NEW: Table repair via Claude (~80 lines)
└── ...

tests/
├── test_extract_cli.py       # NEW: CLI tests (~200 lines)
├── test_extraction.py        # NEW: Backend unit tests (~250 lines)
└── fixtures/
    ├── sample.pdf            # NEW: Small test PDF
    └── sample.docx           # NEW: Small test DOCX
```

### Testing Strategy

1. **Unit tests for backends**: Mock the actual library calls (`docling`, `pymupdf4llm`, `subprocess` for pandoc), verify output structure and error handling
2. **Unit tests for CLI**: MockArgs pattern (matching `test_cli.py:13-17`), test argument parsing and orchestration flow
3. **Integration tests**: Use small fixture PDF/DOCX, verify end-to-end output
4. **Index generation tests**: Port/extend from existing `generate_index.py` usage
5. **Timeout tests**: Verify child process is terminated on timeout
6. **Hash-based skip tests**: Verify reprocessing logic

## Design Decisions

### Decision: Tiered Dependency Extras

**Context:** Docling is a heavy dependency (~500MB+ with ML models). Its performance advantage over pymupdf needs benchmarking before requiring all users to adopt it.

**Chosen approach: Tiered extras**
```toml
extract = ["pymupdf4llm>=0.0.17"]
extract-full = ["docling>=2.0", "pymupdf4llm>=0.0.17"]
```

- `uv add agentic-mbse[extract]` — lightweight, pymupdf-only (~50MB)
- `uv add agentic-mbse[extract-full]` — adds docling with ML-based table/image detection
- Auto-selection logic uses the best available backend at runtime
- After benchmarking confirms docling's value, we can reconsider making it the default

## Potential Risks

1. **Docling version compatibility**: Docling's API has changed between versions. Pin to a specific major version range and test during benchmarking.
2. **Memory exhaustion**: Docling on large PDFs can consume >8GB RAM. The subprocess timeout approach mitigates this but may leave orphan processes. Use `proc.kill()` as last resort.
3. **Pandoc availability**: System dependency that varies by platform. Clear error message with install instructions is essential.
4. **Image path consistency**: Different backends produce different image naming. Need to normalize to `images/figure_NNN.png` format and update markdown references.
5. **Large output files**: A 1000-page PDF may produce a 10MB+ markdown file. This is acceptable for agentic-mbse's philosophy but should be noted.

## Integration Strategy

- The `extract` subcommand is fully additive — no existing functionality changes
- `scripts/generate_index.py` and `scripts/read_section.py` continue to work as standalone scripts (backward compatible)
- Index generation logic is shared between the standalone scripts and the extraction pipeline
- Output format (`full_document.md` + `INDEX.md` + `images/`) is already what existing agents and scripts expect
- `read_section.py` works immediately on any extracted document without changes

## Validation Approach

### Automated Tests
- Unit tests with mocked backends (no real PDF processing in CI)
- Integration tests with small fixture documents (< 1MB)
- CLI argument parsing and error path coverage

### Benchmarking (NFR-1 through NFR-3)

Benchmarking is a **separate follow-up work item** after core extraction is implemented. It requires a working extraction pipeline to run against. Deliverables:

1. **`scripts/benchmark_extraction.py`**: Runnable harness that:
   - Takes a directory of test documents as input
   - Runs each available backend against each document
   - Records: wall-clock time, peak RSS (via `resource.getrusage`), output char count, image count
   - Outputs a summary table (stdout) and detailed `benchmarks.json`
   - Quality assessment remains manual (human review of markdown output)

2. **Test corpus**: Assembled in `tests/fixtures/benchmark/` with categories: text-heavy, table-heavy, image-heavy, large (500+ pages), mixed. Large files excluded from git (`.gitignore`), documented with download instructions.

3. **Results**: Documented in `.project/active/document-extraction/benchmarks.md`, informing whether to adjust fallback ordering or tier defaults.

This will be tracked as a separate backlog item referenced from the spec.

### Manual Verification
- Extract a real-world spec PDF and verify output usability
- Run `read_section.py` on extracted output to confirm compatibility
- Verify image references render correctly in markdown viewers

---

**Next Step:** After approval → `/_my_plan` to create implementation phases, or `/_my_implement` if the scope is clear enough to proceed directly.
