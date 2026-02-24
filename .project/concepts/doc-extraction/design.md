# Design: PDF Extraction Pipeline (Stage 4)

**Created:** 2026-02-23
**Status:** Draft
**Parent:** `.project/concepts/doc-extraction/requirements.md`
**Branch:** `doc-ingest-clean`

---

## 1. Architecture Overview

### 1.1 Data Flow Diagram

```
                         ┌────────────┐
                         │  PDF Path  │
                         └──────┬─────┘
                                │
                    ┌───────────▼────────────┐
                    │  arXiv Detection (FR-2) │
                    │  pdftotext page 1 regex │
                    └───────┬──────────┬─────┘
                     found  │          │ not found
                            │          │
               ┌────────────▼──┐   ┌───▼──────────────────┐
               │ Pandoc Convert │   │ pymupdf4llm Extract  │
               │ (HTML → MD)   │   │ (per-page, BEST_V1)  │
               └──────┬────────┘   └───────┬──────────────┘
                      │                    │
                      │              list[PageResult]
                      │                    │
                      │         ┌──────────▼───────────┐
                      │         │ Ensemble Detection    │
                      │         │ 1. GMFT (all pages)   │
                      │         │ 2. Img2Table (GMFT-   │
                      │         │    empty pages)       │
                      │         │ 3. Docling (optional, │
                      │         │    remaining pages)   │
                      │         │ saves cropped images  │
                      │         └──────────┬───────────┘
                      │                    │
                      │         dict[int, list[DetectedTable]]
                      │                    │
                      │         ┌──────────▼───────────┐
                      │         │ Table Enhancement     │
                      │         │ secondary filters →   │
                      │         │ assess quality →      │
                      │         │ Claude FP filter +    │
                      │         │ extraction if failed/ │
                      │         │ suspect               │
                      │         └──────────┬───────────┘
                      │                    │
                      │         dict[int, list[DetectedTable]]
                      │         (enhanced, some from Claude)
                      │                    │
                      │         ┌──────────▼───────────┐
                      │         │ Quality Gate (FR-5)   │
                      │         │ (per-page assessment) │
                      │         └──────────┬───────────┘
                      │                    │
                      │         list[PageAssessment]
                      │                    │
                      │         ┌──────────▼───────────┐
                      │         │ Router (FR-7)         │
                      │         │ (per-page decisions)  │
                      │         └─┬──────┬──────┬──────┘
                      │           │      │      │
                      │         keep   gmft   claude
                      │           │      │      │
                      │         ┌─▼──────▼──────▼──┐
                      │         │ Merge (FR-7)      │
                      │         │ (assemble pages)  │
                      │         └──────┬───────────┘
                      │                │
                      └────────────────▼
                              ┌────────────────┐
                              │ PipelineResult  │
                              │  .markdown      │
                              │  .metrics       │
                              │  .decisions[]   │
                              │  .cost          │
                              └────────────────┘
```

### 1.2 Key Design Decisions

1. **Table detection is an ensemble; enhancement operates at two granularities.** Detection uses GMFT (primary) → Img2Table (GMFT-empty pages) → Docling (optional third pass). No confidence threshold — Claude is the FP filter. Table-level enhancement (Claude from cropped images) runs first. Page-level enhancement (Claude full-page replacement) runs second for math garbling and low density. Both share a single per-document Claude budget, with table enhancement deducted first (higher ROI).

2. **The pipeline is a data pipeline, not an object graph.** Functions transform data types in sequence. No abstract base classes, no registry patterns, no plugin systems. The pipeline shape is code.

3. **Enhancement is substitution, not patching.** When Claude or GMFT enhances a page, the result replaces the page's markdown entirely (Claude) or replaces/appends table blocks (GMFT). Table-level Claude enhancement replaces individual table markdown within a page. No line-level splicing.

4. **Budget is a resource constraint on the orchestrator, not a property of enhancers.** The orchestrator allocates budget across table and page enhancement. Individual enhancers don't know about budgets.

---

## 2. Module Layout

All production code lives in `src/agentic_mbse/extraction/`.

### 2.1 New Modules

| Module | Responsibility | Lines (est.) |
|--------|---------------|:---:|
| `pipeline.py` | Pipeline entry point: `extract_pdf()`, orchestration | ~250 |
| `quality_gate.py` *(replace)* | Per-page quality assessment, routing decisions | ~200 |
| `types.py` | All pipeline data types (`PageResult`, `PageAssessment`, `PageDecision`, `PipelineResult`, etc.) | ~120 |
| `metrics.py` | Canonical `compute_metrics()` + `ExtractionMetrics` + ground truth scoring | ~150 |
| `tables.py` | Ensemble table detection (GMFT + Img2Table + Docling), secondary filters, table quality assessment, Claude FP filter + table enhancement, markdown table utilities | ~400 |
| `claude_enhance.py` | Claude vision page extraction via CLI | ~100 |
| `pandoc_convert.py` | arXiv detection + Pandoc HTML→MD conversion | ~120 |

### 2.2 Existing Module Disposition (C-3)

| File | Disposition | Rationale |
|------|------------|-----------|
| `base.py` | **Keep** | `ExtractionResult`, `check_processing_needed`, `get_output_dir`, `write_summary`, timeout helpers — all still used by DOCX/legacy paths |
| `pymupdf_backend.py` | **Refactor** | Keep `CompositeHeaderDetector` and the existing `extract()` for legacy CLI path. Add new `extract_pages()` that returns `list[PageResult]` for the pipeline |
| `docling_backend.py` | **Keep as-is** | Still used for DOCX extraction. Not part of the PDF pipeline |
| `pandoc_backend.py` | **Keep as-is** | DOCX→MD via Pandoc. Orthogonal to the new `pandoc_convert.py` (which handles arXiv HTML) |
| `quality_gates.py` | **Replace** | Old module operates on full-document RepairRequest objects. New `quality_gate.py` operates per-page with PageAssessment. Different interface, different granularity |
| `table_extraction.py` | **Replace** | Old module uses RepairRequest-based interface, single-detector. New `tables.py` uses ensemble detection (GMFT + Img2Table + Docling) with DetectedTable objects |
| `table_repair.py` | **Remove** | Legacy Claude table repair, fully superseded |
| `ai_repair.py` | **Remove** | Region-based AI repair, superseded by full-page Claude enhancement. `render_page_image()` utility moves to `claude_enhance.py` |
| `claude_structure.py` | **Remove** | Two-phase structural repair, superseded by quality-gated Claude full-page replacement |
| `postprocess.py` | **Keep, not called by pipeline** | See §2.4 for detailed rationale |
| `index.py` | **Keep as-is** | Orthogonal to extraction pipeline |

### 2.4 postprocess.py: Kept But Not Called by the Pipeline

**`extract_pages()` does NOT call `postprocess()`.** This is a deliberate decision.

The existing `extract()` function in `pymupdf_backend.py` calls `postprocess()` which runs: `promote_bold_headers()`, `promote_plain_headers()`, `reject_noise_headers()`, `strip_running_headers()`, `strip_page_numbers()`, `repair_ligatures()`, `promote_figure_captions()`. Several of these are a promote-then-demote pattern (SC-5 violation):

- `promote_bold_headers()` aggressively promotes bold text to headings
- `reject_noise_headers()` then filters out false promotions
- `promote_plain_headers()` promotes unnumbered text, creating more false positives

The new `extract_pages()` relies on `CompositeHeaderDetector` (which runs inside pymupdf4llm during extraction) for heading detection, and the quality gate + Claude for pages where headings are wrong. This avoids the regex accumulation anti-pattern.

**What's lost by not calling postprocess():**
- `repair_ligatures()` — fi/fl/ff ligature repair. Minor cosmetic improvement. Could be added to the pipeline later as a pure per-page transform if needed.
- `strip_page_numbers()` / `strip_running_headers()` — page number and header removal. Claude vision output doesn't include these. pymupdf4llm pages may still have them. Acceptable: these are cosmetic, not quality-affecting for downstream use.

**What's preserved:**
- `postprocess.py` remains in the codebase because:
  1. The old `extract()` function still calls it (backward compat for `--backend pymupdf`)
  2. `_is_noise_header()` is imported by `claude_structure.py` (which is being removed, so this dependency also goes away)
  3. The Pandoc post-processing in `pandoc_convert.py` uses its own inline transforms (strip `\hspace{0pt}`, HTML comments), not `postprocess()`

**Quality parity (IC-1):** Stage 3 experiments did NOT use postprocess() — the pipeline scripts called `extract_pymupdf_pages()` directly (see `shared.py:180`). So the production pipeline without postprocess() matches what Stage 3 proved.

### 2.5 Removal Strategy

Modules marked **Remove** will be deleted. They have no consumers outside `extract_cli.py`'s `--enhance`/`--fix-tables`/`--structure-only` flags, which will be replaced by the new pipeline. The `--enhance` and `--structure-only` flags on the CLI are superseded by the quality gate's automatic routing.

Modules marked **Replace** will have their old files deleted and new files created. The old `quality_gates.py` has no external consumers — tests (`test_quality_gates.py`) will be rewritten for the new interface.

---

## 3. Type System

Pipeline data types live in `src/agentic_mbse/extraction/types.py`. Metrics types (`ExtractionMetrics`, `GroundTruth`, `AccuracyScore`) live in `src/agentic_mbse/extraction/metrics.py` (see §4.7).

```python
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from agentic_mbse.extraction.metrics import ExtractionMetrics


class PageAction(str, Enum):
    """What to do with a page's markdown."""
    KEEP = "keep"                    # Use pymupdf4llm output as-is
    GMFT_REPLACE = "gmft_replace"    # Replace tables with GMFT tables
    GMFT_APPEND = "gmft_append"      # Append GMFT tables (pymupdf found 0)
    STRIP_FALSE = "strip_false"      # Strip false-positive tables (ColN headers)
    STRIP_BROKEN = "strip_broken"    # Strip broken tables (<br> artifacts)
    CLAUDE_REPLACE = "claude_replace" # Replace entire page with Claude output


@dataclass
class PageResult:
    """Per-page markdown from base extraction."""
    page_num: int   # 0-indexed
    markdown: str


@dataclass
class DetectedTable:
    """A single table found by any detector in the ensemble.

    After table enhancement (§4.4), some DetectedTable objects may contain
    Claude-extracted markdown instead of detector DataFrame output. The
    `source` field tracks extraction provenance. The `detector` field
    tracks which detector found the table. The `extraction_failed` flag
    indicates the detector found the table but extraction failed.
    """
    markdown: str                          # May be empty if extraction_failed
    confidence: float
    num_rows: int
    num_cols: int
    avg_cell_length: float
    image_path: Path | None = None         # Cropped table image (for Claude enhancement)
    extraction_failed: bool = False        # Detected but couldn't extract
    detector: str = "gmft"                 # "gmft" | "img2table" | "docling"
    source: str = "gmft"                   # "gmft" | "img2table" | "docling" | "claude_cropped"


@dataclass
class PageAssessment:
    """Quality assessment for a single page."""
    page_num: int
    needs_claude: bool = False
    needs_gmft: bool = False
    reasons: list[str] = field(default_factory=list)
    severity: float = 0.0

    # Raw signal values (for decision logging)
    math_garble_score: float = 0.0
    table_anomaly: bool = False
    heading_anomaly: bool = False
    low_text_density: bool = False


@dataclass
class PageDecision:
    """Routing decision for a single page."""
    page_num: int
    action: PageAction
    reasons: list[str] = field(default_factory=list)
    details: dict[str, float | bool | str | list[str]] = field(default_factory=dict)


@dataclass
class CostRecord:
    """Cost tracking for a Claude enhancement (page-level or table-level)."""
    page_num: int
    cost_usd: float
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    elapsed_seconds: float = 0.0
    table_index: int | None = None  # None = page-level, int = table-level


@dataclass
class PipelineResult:
    """Complete result of the extraction pipeline."""
    markdown: str
    metrics: ExtractionMetrics
    decisions: list[PageDecision] = field(default_factory=list)
    cost: list[CostRecord] = field(default_factory=list)
    total_cost_usd: float = 0.0
    source: str = ""        # "pandoc_arxiv" | "pdf_pipeline"
    elapsed_seconds: float = 0.0
    error: str | None = None
```

### 3.1 Type Flow (SC-2)

```
PDF path
  → extract_pages()          → list[PageResult]
  → detect_tables_ensemble() → dict[int, list[DetectedTable]]  (GMFT → Img2Table → Docling)
  → filter_tables()          → dict[int, list[DetectedTable]]  (secondary filters applied)
  → enhance_tables()         → dict[int, list[DetectedTable]]  (failed/suspect → Claude)
  → assess_page()            → PageAssessment  (per page)
  → route_page()             → PageDecision    (per page)
  → enhance page if needed   → str             (per page markdown)
  → merge                    → PipelineResult
```

Every type is produced by exactly one component and consumed by the next. No orphan types.

---

## 4. Component Interfaces

### 4.1 Pipeline Entry Point (`pipeline.py`)

```python
@dataclass
class PipelineConfig:
    """Configuration for the extraction pipeline."""
    claude_budget_usd: float = 2.0
    claude_cost_per_page_usd: float = 0.078  # Stage 1D: Sonnet average
    claude_model: str = "sonnet"
    enable_tables: bool = True               # Master toggle for table detection
    enable_img2table: bool = True            # Img2Table on GMFT-empty pages
    enable_docling: bool = False             # Docling third pass (optional, off by default)
    enable_claude: bool = True
    arxiv_html_path: Path | None = None      # Override for arXiv HTML
    dry_run: bool = False                    # Show decisions, don't call Claude
    page_image_dir: Path | None = None       # Pre-rendered page images
    quality_gate: QualityGateConfig = field(default_factory=QualityGateConfig)


def extract_pdf(
    pdf_path: Path,
    config: PipelineConfig | None = None,
) -> PipelineResult:
    """Extract a PDF to markdown using the quality-gated pipeline.

    This is the main entry point. It:
    1. Checks for arXiv HTML shortcut (FR-2)
    2. Runs pymupdf4llm base extraction (FR-3)
    3. Runs GMFT table extraction if enabled (FR-4)
    4. Assesses each page via quality gate (FR-5)
    5. Routes pages to enhancements within budget (FR-6, FR-7)
    6. Merges enhanced pages into final markdown
    7. Computes metrics (FR-11)

    Returns PipelineResult with markdown, metrics, decisions, and cost.
    """
```

This is the **only** function most callers need. The CLI calls it. Tests call it. The config dataclass has sensible defaults matching Stage 3's proven values.

### 4.2 arXiv Detection and Pandoc Conversion (`pandoc_convert.py`)

```python
def detect_arxiv_id(pdf_path: Path) -> str | None:
    """Extract arXiv ID from PDF page 1 text.

    Sequence (from Stage 1B):
    1. pymupdf page 1 text extraction
    2. Regex: arXiv:\d{4}\.\d{4,5}(v\d+)?
    3. Fallback: check PDF Creator field for 'arXiv'

    Returns arXiv ID string or None.
    """


def check_arxiv_html(arxiv_id: str) -> str | None:
    """Check if arXiv HTML is available via HTTP HEAD.

    Returns the HTML URL if available, None otherwise.
    Timeout: 5 seconds. Failure → return None (silent skip).
    """


def convert_arxiv_html(
    html_source: str | Path,
    pandoc_path: str = "pandoc",
) -> str:
    """Convert arXiv HTML to markdown via Pandoc.

    Config (from Stage 1B, experiment iter-16):
    - Pre-process: strip <figure> tags, CSS transform wrappers
    - pandoc -f html-native_divs-native_spans
             -t markdown-header_attributes
             --wrap=none --markdown-headings=atx
    - Post-process: strip \\hspace{0pt}, HTML comment artifacts

    Args:
        html_source: URL or local file path to arXiv HTML.
        pandoc_path: Path to pandoc binary.

    Returns:
        Clean markdown string.

    Raises:
        subprocess.CalledProcessError: If pandoc fails.
    """
```

### 4.3 Base Extraction (`pymupdf_backend.py` — refactored)

The existing `extract()` function (full-document, returns `ExtractionResult`) is preserved for backward compatibility. A new function is added:

```python
def extract_pages(pdf_path: Path) -> list[PageResult]:
    """Extract per-page markdown using pymupdf4llm with BEST_V1 config.

    Uses page_chunks=True for per-page output with full-document header
    calibration (IdentifyHeaders scans all pages for font statistics).

    Config (from Stage 1A, experiments 6-8):
    - table_strategy="lines"
    - ignore_code=True
    - hdr_info=CompositeHeaderDetector (font-size + bold)
    - force_text=True, write_images=False, dpi=150

    Returns list of PageResult, 0-indexed page numbers.
    """
```

The `CompositeHeaderDetector` stays in this file. It's battle-tested and used by both the old `extract()` and new `extract_pages()`.

### 4.4 Ensemble Table Detection and Enhancement (`tables.py`)

```python
def detect_tables_ensemble(
    pdf_path: Path,
    save_images: bool = True,
    enable_img2table: bool = True,
    enable_docling: bool = False,
) -> dict[int, list[DetectedTable]]:
    """Detect tables using the ensemble: GMFT → Img2Table → Docling.

    Step 1: GMFT (primary) — AutoTableDetector for detection,
    AutoTableFormatter for DataFrame extraction. No confidence
    threshold — all detections kept (Claude handles FP rejection).
    Saves cropped images for all detections (needed for Claude).

    Step 2: Img2Table (on GMFT-empty pages) — Img2TableDetector with
    borderless_tables=True. Finds tables GMFT's deep learning model
    can't see: small tables, space-aligned, text-embedded. Added 4
    tables on aries (p35, p37, p39, p94).

    Step 3: Docling (optional, on still-empty pages) — DocLayNet-trained
    detection via MCP. Detected 34 tables on aries (vs 28 GT). Safety
    net for maximum recall.

    DetectedTable.extraction_failed is set to True when a detector finds
    a table but extraction returns null or empty. The image is still
    saved (needed for Claude enhancement).

    Returns dict mapping 0-indexed page number → list of DetectedTable.
    Returns empty dict if no detectors are installed.
    """


def _detect_gmft(pdf_path: Path, save_images: bool = True) -> dict[int, list[DetectedTable]]:
    """GMFT detection pass. Returns empty dict if gmft not installed."""


def _detect_img2table(
    pdf_path: Path,
    gmft_pages: set[int],
    save_images: bool = True,
) -> dict[int, list[DetectedTable]]:
    """Img2Table detection on pages where GMFT found nothing.

    Uses Img2TableDetector(borderless_tables=True) from the gmft
    package (already installed as GMFT dependency).

    Args:
        pdf_path: Path to PDF.
        gmft_pages: Pages where GMFT already found tables (skip these).
        save_images: Save cropped table images.

    Returns dict mapping page number → list of DetectedTable.
    DetectedTable.detector will be "img2table".
    """


def _detect_docling(
    pdf_path: Path,
    covered_pages: set[int],
) -> dict[int, list[DetectedTable]]:
    """Docling detection on pages where GMFT and Img2Table found nothing.

    Uses Docling MCP server for detection. Optional — returns empty
    dict if Docling MCP is not available.

    Returns dict mapping page number → list of DetectedTable.
    DetectedTable.detector will be "docling".
    """


def filter_tables(
    tables: list[DetectedTable],
) -> tuple[list[DetectedTable], list[str]]:
    """Apply secondary false-positive filters to detected tables.

    Heuristics (from Stage 1C/2, ground truth scoring):
    - avg_cell_length > 80 → reject (prose blocks)
    - num_rows == 1, num_cols > 4 → reject (layout artifacts)

    NO confidence threshold — the v2 investigation proved 10/11
    confidence-filtered detections were real tables. Claude handles
    FP rejection during enhancement (caught all 5 FPs on aries).

    Tables with extraction_failed=True pass through the filter (they
    have no DataFrame to assess) — Claude table enhancement handles them.

    Returns (kept_tables, rejection_reasons).
    """


def assess_table_quality(table: DetectedTable) -> tuple[bool, list[str]]:
    """Assess whether a detected table needs Claude enhancement.

    Triggers (from table-image spike):
    1. extraction_failed=True — detector found a table but extraction
       returned null. 7/15 aries GMFT tables fell into this category;
       Claude recovered all 7 from the cropped images.
    2. Suspect quality — very few rows relative to image height,
       garbled column names, single-column output from multi-column
       image. On aries p4, GMFT produced 7 rows; Claude extracted 22.

    Returns (needs_enhancement, reasons).
    """


def enhance_table_with_claude(
    table: DetectedTable,
    model: str = "sonnet",
    timeout: int = 120,
) -> tuple[DetectedTable, CostRecord]:
    """Extract table from cropped image using Claude vision.

    Uses the table-specific prompt (not the full-page prompt):
    "Extract this table as a markdown pipe table... Output ONLY the
    markdown table, no commentary." Zero reasoning leakage across
    47 Claude calls in the table-image spike.

    If Claude returns 0 rows (identifies image as not-a-table),
    returns a DetectedTable with markdown="" — the caller treats this
    as a confirmed false positive and drops the table. This caught
    p42 and p48 on aries_cost_account. Claude is the FP filter for
    the entire ensemble — the confidence threshold is redundant.

    Requires table.image_path to be set.

    Returns (enhanced_table, cost_record).
    enhanced_table.source will be "claude_cropped".
    """


# Table markdown utilities (from Stage 3 shared.py)
def strip_pipe_tables(markdown: str) -> str: ...
def replace_tables(page_markdown: str, tables: list[DetectedTable]) -> str: ...
def insert_tables_at_end(page_markdown: str, tables: list[DetectedTable]) -> str: ...
def has_br_in_tables(markdown: str) -> bool: ...
def has_col_headers(markdown: str) -> bool: ...
def count_pipe_rows(markdown: str) -> int: ...
```

**Why Claude table extraction lives in `tables.py` rather than `claude_enhance.py`:** This is a table concern, not a page concern. `claude_enhance.py` does full-page replacement with a different prompt, different image (full page), and produces page-level markdown. Table enhancement uses a table-specific prompt, a cropped image, and produces a table. They share `claude` CLI invocation mechanics (a small helper could be shared), but the domain logic is different.

### 4.5 Quality Gate and Routing (`quality_gate.py`)

This module covers both quality assessment and routing decisions. They live together because routing is a direct function of assessment — `route_page()` consumes a `PageAssessment` and produces a `PageDecision`. Splitting them into separate modules would create a two-file dependency for the most common operation (assess → route).

The module name reflects the primary concept (quality gate) rather than the secondary one (routing) because the quality gate is the novel contribution — routing is a straightforward decision table.

```python
@dataclass
class QualityGateConfig:
    """Thresholds for quality gate detection.

    All defaults from Stage 3 experiments, traced to ground truth.
    """
    math_severity_threshold: float = 1.0     # Stage 3 quality_gate.py
    text_density_min_chars: int = 200         # Stage 3: < 200 = sparse page
    heading_density_max: float = 3.0          # Stage 3: > 3.0 headings/page = over-detection
    heading_anomaly_boost: float = 0.5        # Stage 3 h5: boost Claude severity


def _count_headings(markdown: str) -> int:
    """Count ATX headings in markdown (lines starting with # + space).

    This is a lightweight helper used by the orchestrator for the
    document-level heading anomaly check. It counts headings from raw
    page markdown, NOT from PageAssessment (which doesn't store heading
    counts — that's a metrics concern, not a quality signal).
    """


def assess_page(
    page_markdown: str,
    page_num: int,
    config: QualityGateConfig | None = None,
) -> PageAssessment:
    """Assess a single page's extraction quality.

    Detection dimensions (FR-5):
    - Math garbling: strikethroughs, replacement chars, bracket operators
    - Table anomaly: <br> in tables, ColN auto-headers
    - Text density: < 200 chars

    Note: Does NOT compute heading counts. Heading anomaly is a document-
    level check (assess_heading_anomaly) that runs after all pages are
    assessed. The per-page assessment only produces quality signals.
    """


def assess_heading_anomaly(
    total_headings: int,
    total_pages: int,
    config: QualityGateConfig | None = None,
) -> tuple[bool, list[str]]:
    """Document-level heading anomaly check.

    Signals:
    - 0 headings in >2 page doc → anomaly
    - Density > 3.0 headings/page → anomaly (over-detection)
    """


def route_page(
    assessment: PageAssessment,
    gmft_tables: list[DetectedTable] | None,
    page_markdown: str,
    within_claude_budget: bool,
) -> PageDecision:
    """Decide what to do with a page based on assessment and available resources.

    Routing logic (FR-7, from Stage 3 H5):
    1. needs_claude AND within_budget → CLAUDE_REPLACE
    2. needs_claude AND NOT within_budget AND needs_gmft → GMFT_REPLACE (fallback)
    3. needs_gmft (table-only) → GMFT_REPLACE or GMFT_APPEND
    4. ColN headers, no GMFT → STRIP_FALSE
    5. <br> artifacts, no GMFT → STRIP_BROKEN
    6. else → KEEP

    When both table and math issues exist, Claude wins (full-page handles both).
    """


def prioritize_pages(
    assessments: list[PageAssessment],
    budget_pages: int,
) -> list[int]:
    """Select highest-severity pages within budget.

    Sorts by severity descending, takes top N, returns in page order.
    """
```

### 4.6 Claude Enhancement (`claude_enhance.py`)

```python
def render_page_image(
    pdf_path: Path,
    page_num: int,
    dpi: int = 200,
    output_dir: Path | None = None,
) -> Path:
    """Render a single PDF page to a PNG image.

    Args:
        pdf_path: Path to PDF.
        page_num: 0-indexed page number.
        dpi: Resolution (default 200, from Stage 1D).
        output_dir: Where to save. Defaults to temp dir.

    Returns path to the PNG file.
    """


def extract_page_with_claude(
    pdf_path: Path,
    page_num: int,
    model: str = "sonnet",
    prompt: str | None = None,
    image_path: Path | None = None,
    timeout: int = 120,
) -> tuple[str, CostRecord]:
    """Extract a single page using Claude vision.

    Mode: Pure vision (page image only, no supplemental text).
    Stage 1D proved supplemental text provides no benefit.

    If image_path is provided, uses that image. Otherwise renders
    the page from the PDF.

    Returns (markdown, CostRecord).
    Raises TimeoutError if Claude doesn't respond within timeout.
    """
```

The prompt defaults to the `extract_baseline.txt` content, embedded as a constant (not loaded from file at runtime).

#### Claude Output Sanity Check (NFR-4)

Claude full-page replacement is NOT accepted unconditionally. Before substituting Claude output for a page, a lightweight sanity check runs:

```python
def validate_claude_output(
    claude_markdown: str,
    original_markdown: str,
    page_num: int,
) -> tuple[bool, str]:
    """Sanity-check Claude output before accepting it.

    Rejects if:
    1. Claude output is empty or whitespace-only
    2. Character count drops >50% vs original (Claude hallucinated a
       near-empty page or truncated content)
    3. Claude output contains the literal prompt text (prompt leak)

    Returns (accept, reason).
    """
```

On rejection, the page falls back to GMFT enhancement (if table issues) or keeps pymupdf4llm output. The rejection is logged in `PageDecision.details` with the reason.

This replaces the fine-grained cross-validation from `ai_repair.py` (which compared individual number sets). Full-page replacement can't use number-level cross-validation because Claude rewrites everything including surrounding text. The 50% character threshold is conservative — Stage 1D showed Claude output is typically 80-120% of pymupdf4llm character count for the same page. A >50% drop means something went wrong.

### 4.7 Metrics (`metrics.py`) — Single Source of Truth

The canonical metrics implementation lives in `src/agentic_mbse/extraction/metrics.py`. The experiment scripts in `tests/corpus/metrics.py` will be replaced by imports from this module.

```python
# src/agentic_mbse/extraction/metrics.py

def compute_metrics(markdown: str) -> ExtractionMetrics:
    """Compute extraction quality metrics.

    This is the canonical implementation. tests/corpus/ imports from here.

    Definitions:
    - heading_count: lines starting with # followed by space/tab
    - heading_by_level: count # symbols to determine level
    - table_row_count: lines with >= 2 pipe characters
    - math_symbol_count: Unicode math ranges (U+2200-22FF, U+2100-214F,
      U+27C0-27EF, U+0370-03FF)
    - figure_ref_count: regex for "figure N" / "fig. N"
    """


@dataclass
class GroundTruth:
    """Human-verified metrics for a document."""
    slug: str
    pages: int
    headings: int | None = None
    heading_levels: dict[int, int] | None = None
    data_tables: int | None = None
    table_data_rows: int | None = None
    expected_metric_table_rows: int | None = None
    display_equations: int | None = None
    has_inline_math: bool | None = None
    notes: str = ""


@dataclass
class AccuracyScore:
    """Comparison of detected vs ground truth for one dimension."""
    detected: int
    ground_truth: int
    delta: int
    error_pct: float
    category: str  # "exact", "close", "over", "under", "miss"


def load_ground_truth(path: Path | None = None) -> dict[str, GroundTruth]:
    """Load ground truth from JSONL file."""


def score_against_ground_truth(
    metrics: ExtractionMetrics,
    gt: GroundTruth,
) -> dict[str, AccuracyScore | None]:
    """Score extraction metrics against ground truth."""
```

**Migration:** `tests/corpus/metrics.py` becomes a thin shim:
```python
# tests/corpus/metrics.py — redirect to canonical implementation
from agentic_mbse.extraction.metrics import (
    ExtractionMetrics, GroundTruth, AccuracyScore,
    compute_metrics, load_ground_truth, score_against_ground_truth,
)
```

This ensures the production pipeline and experiment scripts use identical metric definitions. No drift possible.

---

## 5. Pipeline Orchestration (`pipeline.py`)

### 5.1 Main Flow

```python
def extract_pdf(pdf_path: Path, config: PipelineConfig | None = None) -> PipelineResult:
    if config is None:
        config = PipelineConfig()

    t0 = time.time()

    # Step 1: arXiv shortcut (FR-2)
    arxiv_result = _try_arxiv_shortcut(pdf_path, config)
    if arxiv_result is not None:
        return arxiv_result

    # Step 2: Base extraction (FR-3)
    pages = pymupdf_backend.extract_pages(pdf_path)

    # Step 3: Ensemble table detection (FR-4, optional)
    detected_pages = {}
    if config.enable_tables:
        detected_pages = _try_detect_tables(pdf_path, config)  # returns {} on ImportError

    # Step 3b: Filter and enhance tables (FR-4, table detection follow-up)
    # Table enhancement runs BEFORE the quality gate so the gate sees
    # final table state. Table-level Claude costs are deducted from the
    # shared budget first (higher ROI than page-level enhancement).
    filtered_tables: dict[int, list[DetectedTable]] = {}
    table_filter_reasons: dict[int, list[str]] = {}
    table_cost_records: list[CostRecord] = []
    table_claude_spend = 0.0
    for page_num, raw_tables in detected_pages.items():
        kept, reasons = filter_tables(raw_tables)
        table_filter_reasons[page_num] = reasons
        page_tables = []
        for table in kept:
            needs_enhance, enhance_reasons = assess_table_quality(table)
            if (needs_enhance and config.enable_claude and not config.dry_run
                    and table_claude_spend < config.claude_budget_usd):
                enhanced, cost = enhance_table_with_claude(table, config.claude_model)
                table_cost_records.append(cost)
                table_claude_spend += cost.cost_usd
                if enhanced.markdown:  # Claude produced output
                    page_tables.append(enhanced)
                # else: Claude says not-a-table → drop (false positive filter)
            else:
                if table.markdown:  # Skip extraction-failed tables without Claude
                    page_tables.append(table)
        if page_tables:
            filtered_tables[page_num] = page_tables

    # Step 4: Quality gate (FR-5)
    assessments = [assess_page(p.markdown, p.page_num) for p in pages]

    # Step 4b: Document-level heading check
    # Heading count is computed directly from page markdown, NOT stored on
    # PageAssessment (which is a per-page quality signal, not a metric).
    total_headings = sum(
        _count_headings(p.markdown) for p in pages
    )
    has_heading_anomaly, _ = assess_heading_anomaly(total_headings, len(pages))
    if has_heading_anomaly:
        for a in assessments:
            if a.needs_claude:
                a.severity += config.quality_gate.heading_anomaly_boost

    # Step 5: Budget allocation (FR-6)
    # Remaining budget after table enhancement goes to page-level Claude
    remaining_budget = config.claude_budget_usd - table_claude_spend
    claude_budget = EnhancerBudget(
        total_usd=max(0.0, remaining_budget),
        cost_per_page_usd=config.claude_cost_per_page_usd,
    )
    selected_set = allocate_budget(assessments, claude_budget, "needs_claude")

    # Step 6: Claude page enhancement (FR-6, optional)
    claude_results: dict[int, str] = {}
    cost_records: list[CostRecord] = list(table_cost_records)  # Include table costs
    if config.enable_claude and not config.dry_run:
        for page_num in sorted(selected_set):
            md, cost = extract_page_with_claude(pdf_path, page_num, ...)
            # Sanity check (NFR-4): reject if output is empty or truncated >50%
            original_md = pages[page_num].markdown
            accept, reject_reason = validate_claude_output(md, original_md, page_num)
            if accept:
                claude_results[page_num] = md
                cost_records.append(cost)
            else:
                logger.warning(f"Claude page {page_num} rejected: {reject_reason}")
                cost_records.append(cost)  # Still track the spend

    # Step 7: Route and merge (FR-7)
    decisions = []
    final_pages = []
    for page in pages:
        pn = page.page_num
        assessment = assessments[pn]
        filtered = filtered_tables.get(pn)
        within_budget = pn in selected_set

        decision = route_page(assessment, filtered or None, page.markdown, within_budget)

        # Capture table filter reasons in decision details (FR-8/SC-7)
        if pn in table_filter_reasons:
            decision.details["table_filter"] = table_filter_reasons[pn]

        decisions.append(decision)

        # Apply decision
        if decision.action == PageAction.CLAUDE_REPLACE and pn in claude_results:
            final_pages.append(claude_results[pn])
        elif decision.action == PageAction.GMFT_REPLACE:
            final_pages.append(replace_tables(page.markdown, filtered))
        elif decision.action == PageAction.GMFT_APPEND:
            final_pages.append(insert_tables_at_end(page.markdown, filtered))
        elif decision.action == PageAction.STRIP_FALSE:
            final_pages.append(strip_pipe_tables(page.markdown))
        elif decision.action == PageAction.STRIP_BROKEN:
            final_pages.append(strip_pipe_tables(page.markdown))
        else:  # KEEP
            final_pages.append(page.markdown)

    # Step 8: Assemble and compute metrics (FR-11)
    markdown = "\n\n".join(final_pages)
    metrics = compute_metrics(markdown)
    elapsed = time.time() - t0

    return PipelineResult(
        markdown=markdown,
        metrics=metrics,
        decisions=decisions,
        cost=cost_records,
        total_cost_usd=sum(c.cost_usd for c in cost_records),
        source="pdf_pipeline",
        elapsed_seconds=elapsed,
    )
```

This is **pseudocode** showing the orchestration logic. The actual implementation will handle error isolation (NFR-3) with try/except around each enhancement step.

### 5.2 arXiv Shortcut

```python
def _try_arxiv_shortcut(pdf_path: Path, config: PipelineConfig) -> PipelineResult | None:
    """Attempt arXiv HTML extraction. Returns None if not applicable."""
    if not _pandoc_available():
        return None

    html_source = config.arxiv_html_path
    if html_source is None:
        arxiv_id = detect_arxiv_id(pdf_path)
        if arxiv_id is None:
            return None
        html_url = check_arxiv_html(arxiv_id)
        if html_url is None:
            return None
        html_source = html_url

    markdown = convert_arxiv_html(html_source)
    metrics = compute_metrics(markdown)

    return PipelineResult(
        markdown=markdown,
        metrics=metrics,
        decisions=[],  # No per-page decisions for Pandoc path
        source="pandoc_arxiv",
    )
```

### 5.3 Error Isolation (NFR-3)

Each enhancement step is wrapped in try/except:

```python
def _try_detect_tables(pdf_path: Path, config: PipelineConfig) -> dict[int, list[DetectedTable]]:
    """Try ensemble table detection. Returns empty dict on any failure."""
    try:
        return detect_tables_ensemble(
            pdf_path,
            enable_img2table=config.enable_img2table,
            enable_docling=config.enable_docling,
        )
    except ImportError:
        return {}
    except Exception as exc:
        logger.warning(f"Table detection failed: {exc}")
        return {}
```

Same pattern for Claude: if a page fails, the router falls back (Claude → GMFT → keep). The base extraction (pymupdf4llm) is the only step that can't fail silently — if it fails, the pipeline returns an error result.

---

## 6. Budget Mechanism (SC-4)

Budget is a parameter of the pipeline orchestration, not of any enhancer. The allocation function is generic — not hardcoded to Claude.

### 6.1 Budget Allocation

```python
@dataclass
class EnhancerBudget:
    """Budget for a single cost-bearing enhancer."""
    total_usd: float          # Max spend for this enhancer per document
    cost_per_page_usd: float  # Estimated cost per page invocation

    @property
    def max_pages(self) -> int:
        if self.cost_per_page_usd <= 0:
            return 0
        return int(self.total_usd / self.cost_per_page_usd)


def allocate_budget(
    assessments: list[PageAssessment],
    budget: EnhancerBudget,
    needs_field: str = "needs_claude",
) -> set[int]:
    """Select highest-severity pages within a budget.

    Generic over any enhancer — the `needs_field` parameter controls which
    assessment flag to check. Sorts eligible pages by severity descending,
    takes top N within budget, returns the set of selected page numbers.

    Args:
        assessments: Per-page quality assessments.
        budget: Budget for this enhancer.
        needs_field: Attribute name on PageAssessment to filter by.

    Returns:
        Set of 0-indexed page numbers selected for enhancement.
    """
    eligible = [a for a in assessments if getattr(a, needs_field, False)]
    ranked = sorted(eligible, key=lambda a: a.severity, reverse=True)
    selected = ranked[:budget.max_pages]
    return {a.page_num for a in selected}
```

### 6.2 Configuration

```python
@dataclass
class PipelineConfig:
    claude_budget_usd: float = 2.0               # FR-6: default $2.00/document
    claude_cost_per_page_usd: float = 0.078       # Stage 1D: Sonnet average
    claude_model: str = "sonnet"
    # Future: add more budgeted enhancers here
    # gemini_budget_usd: float = 1.0
    # gemini_cost_per_page_usd: float = 0.05
```

### 6.3 Usage in Orchestrator

```python
# In extract_pdf():
claude_budget = EnhancerBudget(
    total_usd=config.claude_budget_usd,
    cost_per_page_usd=config.claude_cost_per_page_usd,
)
claude_selected = allocate_budget(assessments, claude_budget, "needs_claude")

# Future second enhancer:
# gemini_budget = EnhancerBudget(config.gemini_budget_usd, config.gemini_cost_per_page_usd)
# gemini_selected = allocate_budget(assessments, gemini_budget, "needs_ocr")
# Page overlap: if a page is selected by both, the router resolves priority.
```

### 6.4 Adding a Second Budgeted Enhancer

To add Gemini OCR alongside Claude:
1. Add `gemini_budget_usd` + `gemini_cost_per_page_usd` to `PipelineConfig`
2. Add `needs_ocr: bool` to `PageAssessment`
3. Add `GEMINI_REPLACE` to `PageAction`
4. Call `allocate_budget(assessments, gemini_budget, "needs_ocr")` — reuses the same function
5. Update `route_page()` with priority (e.g., Claude wins over Gemini for pages needing both)
6. Add the enhancer function

No budget logic is duplicated — `allocate_budget()` handles any enhancer. Page overlap (same page selected by two enhancers) is resolved in `route_page()` which already has a priority chain.

---

## 7. Evolvability Analysis (SC-3b)

The requirements list 6 plausible near-term iterations. Here's how each is accommodated:

### "Adding a missing table detection heuristic to the quality gate"

**Files changed:** `quality_gate.py` (1 file)

Partially addressed by the Img2Table + Docling ensemble — most "missing" tables are now detected. For remaining cases, add a new detection function (e.g., `_assess_missing_tables(page_markdown)`) and call it from `assess_page()`. If detected, set `needs_gmft=True`. The router already handles GMFT_APPEND for pages where pymupdf found 0 tables but the ensemble found some.

### "Adding a heading-accuracy check that routes to a different enhancer"

**Files changed:** `quality_gate.py` + `pipeline.py` (2 files)

Add a new signal to `PageAssessment` (e.g., `needs_heading_fix: bool`). Add a new `PageAction` (e.g., `HEADING_FIX`). Add the enhancer function. Update `route_page()` with the priority and `extract_pdf()` with the execution.

### "Swapping Claude for a different LLM"

**Files changed:** `claude_enhance.py` → rename/generalize, or add `gemini_enhance.py` (1-2 files)

The enhancer interface is: `(pdf_path, page_num, **kwargs) → (markdown, CostRecord)`. Any LLM that can process a page image and return markdown fits this interface. The pipeline orchestration doesn't know or care what model is being called.

### "Adding a Pandoc+GMFT hybrid for arXiv papers"

**Files changed:** `pipeline.py` (1 file)

In `_try_arxiv_shortcut()`, after Pandoc conversion, also run GMFT and use `replace_tables()` to substitute GMFT tables into the Pandoc markdown. The table utilities are already standalone functions.

### "Tuning quality gate thresholds based on new corpus data"

**Files changed:** `quality_gate.py` (1 file, update `QualityGateConfig` defaults)

All thresholds are in `QualityGateConfig`. Change the defaults. Or pass a custom config from the caller.

### "Adding a document-level check (scanned document → OCR)"

**Files changed:** `quality_gate.py` + `pipeline.py` (2 files)

Add a document-level check after base extraction (analogous to `assess_heading_anomaly()`). If triggered, boost severity on all pages or set a flag that routes all pages to an OCR enhancer.

**Verdict:** Every iteration touches 1-2 files. The quality gate + router + enhancer pattern is composable without architectural changes.

---

## 8. Provenance (SC-7, FR-8, FR-9)

### 8.1 Decision Log

`PipelineResult.decisions` is a list of `PageDecision`, one per page. Each contains:
- `page_num`: which page
- `action`: what was done (enum value)
- `reasons`: human-readable explanation list
- `details`: raw signal values (severity, math_garble_score, etc.)

Example:
```json
{
    "page_num": 4,
    "action": "claude_replace",
    "reasons": [
        "math garbling: 5 strikethroughs (severity 2.0)",
        "math garbling: 3 bracket operators (severity 1.0)",
        "total severity 3.0 — within Claude budget"
    ],
    "details": {
        "math_garble_score": 3.0,
        "table_anomaly": false,
        "low_text_density": false,
        "severity": 3.0
    }
}
```

### 8.2 Cost Log

`PipelineResult.cost` is a list of `CostRecord`, one per Claude invocation (page-level or table-level):
```json
{
    "page_num": 4,
    "cost_usd": 0.078,
    "input_tokens": 1523,
    "output_tokens": 892,
    "model": "sonnet",
    "elapsed_seconds": 22.4,
    "table_index": null
}
```

Table-level enhancement produces records with `table_index` set:
```json
{
    "page_num": 12,
    "cost_usd": 0.076,
    "input_tokens": 1102,
    "output_tokens": 645,
    "model": "sonnet",
    "elapsed_seconds": 18.1,
    "table_index": 0
}
```

### 8.3 Persistence

The CLI writes these to disk alongside the output:
```
output_dir/
  output.md          # Final markdown
  metrics.json       # ExtractionMetrics
  decisions.json     # list[PageDecision]
  cost.json          # list[CostRecord] (only if Claude was used)
```

This matches the Stage 3 experiment output format, preserving compatibility with ground truth scoring scripts.

---

## 9. Public API Surface (SC-8)

### 9.1 For Most Callers (CLI, scripts)

```python
from agentic_mbse.extraction.pipeline import extract_pdf, PipelineConfig
from agentic_mbse.extraction.types import PipelineResult

result = extract_pdf(Path("paper.pdf"))
# or
result = extract_pdf(Path("paper.pdf"), PipelineConfig(claude_budget_usd=0))
```

**Two imports.** One function call.

### 9.2 For Dry-Run / Debugging

```python
from agentic_mbse.extraction.quality_gate import assess_page, QualityGateConfig
from agentic_mbse.extraction.types import PageAssessment

# Assess a single page with custom thresholds
assessment = assess_page(markdown_text, page_num=0)
```

### 9.3 For Testing / Extending

```python
from agentic_mbse.extraction.types import (
    PageResult, PageAssessment, PageDecision, PageAction,
    DetectedTable, CostRecord, PipelineResult,
)
from agentic_mbse.extraction.quality_gate import assess_page, route_page
from agentic_mbse.extraction.tables import (
    detect_tables_ensemble, filter_tables, replace_tables,
)
```

Total public surface: **1 function** for normal use, **3-4 functions** for debugging/testing, **~10 types** for extending.

### 9.4 Package Exports

`__init__.py` will export:
```python
# Existing exports (backward compatibility)
from agentic_mbse.extraction.base import (
    ExtractionResult,
    check_processing_needed,
    get_output_dir,
    sanitize_filename,
    write_summary,
)

# New pipeline exports
from agentic_mbse.extraction.pipeline import extract_pdf, PipelineConfig
from agentic_mbse.extraction.types import PipelineResult
```

---

## 10. CLI Integration (FR-10)

The `extract` subcommand gets new flags for the pipeline:

```
agentic-mbse extract <pdf_path> [options]

New pipeline options:
  --output, -o DIR          Output directory (default: alongside input)
  --html-path PATH          arXiv HTML for Pandoc shortcut (overrides auto-detect)
  --budget FLOAT            Claude budget in USD (default: 2.0, 0 = no Claude)
  --no-tables               Disable all table detection
  --no-img2table            Disable Img2Table second-pass detection
  --docling                 Enable Docling third-pass detection (off by default)
  --dry-run                 Show quality gate decisions without calling Claude
  --model MODEL             Claude model (default: sonnet)

Legacy options (preserved for backward compatibility):
  --backend {docling,pymupdf,pandoc}   Force single-backend extraction
  --fix-tables              Legacy table repair (deprecated)
  --enhance                 Legacy AI enhancement (deprecated)
  --structure-only          Legacy structural repair (deprecated)
```

**Behavior change:** When `--backend` is NOT specified and the input is a PDF, the new pipeline (`extract_pdf()`) is used instead of the old single-backend path. When `--backend` IS specified, the old path is preserved for backward compatibility.

This means `agentic-mbse extract paper.pdf` automatically uses the quality-gated pipeline, while `agentic-mbse extract paper.pdf --backend pymupdf` uses the old direct extraction.

---

## 11. Dependency Management (NFR-1)

```python
# tables.py
def _detect_gmft(pdf_path: Path, save_images: bool = True) -> dict[int, list[DetectedTable]]:
    try:
        from gmft.auto import AutoTableDetector, AutoTableFormatter
        from gmft.pdf_bindings.pdfium import PyPDFium2Document
    except ImportError:
        return {}  # GMFT not installed — silent degradation
    ...

def _detect_img2table(pdf_path: Path, gmft_pages: set[int], ...) -> dict[int, list[DetectedTable]]:
    try:
        from gmft.detectors.img2table import Img2TableDetector
    except ImportError:
        return {}  # Img2Table not available — silent degradation
    ...

# pandoc_convert.py
def _pandoc_available() -> bool:
    return shutil.which("pandoc") is not None

# claude_enhance.py
def _claude_available() -> bool:
    return shutil.which("claude") is not None
```

**Degradation path (SC-6):**

```
Full pipeline:  arXiv check → pymupdf4llm → GMFT+Img2Table+Docling → table enhance → quality gate → Claude pages → merge
No Docling:     arXiv check → pymupdf4llm → GMFT+Img2Table         → table enhance → quality gate → Claude pages → merge
No Img2Table:   arXiv check → pymupdf4llm → GMFT                   → table enhance → quality gate → Claude pages → merge
No Pandoc:                    pymupdf4llm → GMFT+Img2Table+Docling  → table enhance → quality gate → Claude pages → merge
No Claude:                    pymupdf4llm → GMFT+Img2Table+Docling  → (no enhance)  → quality gate →               merge
No detectors:                 pymupdf4llm →                                           quality gate → Claude pages → merge
Minimal:                      pymupdf4llm →                                                                         merge
```

Each level works correctly. The quality gate still runs (it's deterministic, no deps) — it just can't route to unavailable enhancers.

---

## 12. Configuration (C-4)

### 12.1 Pipeline Config

`PipelineConfig` is a flat dataclass with Stage 3-proven defaults:

| Parameter | Default | Source |
|-----------|---------|--------|
| `claude_budget_usd` | 2.0 | Stage 3 H5: $2/doc budget, $0.12/doc average |
| `claude_cost_per_page_usd` | 0.078 | Stage 1D: observed Sonnet average across 8 experiments |
| `claude_model` | "sonnet" | Stage 1D: best quality/cost ratio |
| `enable_tables` | True | Stage 3 H1: 1% table error |
| `enable_img2table` | True | Table spike v2: +4 tables on aries, 86% combined recall |
| `enable_docling` | False | Table spike v2: 34 detections (~100% recall) — optional safety net |
| `enable_claude` | True | Stage 3 H5: 70% heading error (vs 89% without) |
| `dry_run` | False | — |
| `quality_gate` | `QualityGateConfig()` | Stage 3 quality_gate.py thresholds |

### 12.2 Quality Gate Config

`QualityGateConfig` has threshold defaults:

| Parameter | Default | Source |
|-----------|---------|--------|
| `math_severity_threshold` | 1.0 | Stage 3 quality_gate.py: no false positives on dev set |
| `text_density_min_chars` | 200 | Stage 3: correctly flags figure-only pages |
| `heading_density_max` | 3.0 | Stage 3: catches paischer_2025 over-detection |
| `heading_anomaly_boost` | 0.5 | Stage 3 H5: boosts Claude priority for heading-troubled docs |

All constants are traceable to specific experiments (SC-9).

---

## 13. Test Strategy (SC-10)

### 13.1 Unit Tests — Quality Gate

Test each detection dimension with synthetic markdown (no PDFs, no network):

```python
class TestMathGarbling:
    def test_strikethrough_high(self):
        md = "Some ~~garbled~~ text ~~more~~ and ~~again~~ content"
        a = assess_page(md, 0)
        assert a.needs_claude
        assert a.math_garble_score >= 2.0

    def test_strikethrough_low(self):
        md = "One ~~strike~~ only"
        a = assess_page(md, 0)
        assert a.math_garble_score >= 0.5
        assert a.math_garble_score < 1.0  # Below threshold

    def test_replacement_chars(self):
        md = "Text with \ufffd\ufffd characters"
        a = assess_page(md, 0)
        assert a.needs_claude

    def test_bracket_operators(self):
        md = "Eq: [/][+][-][*] many operators"
        a = assess_page(md, 0)
        assert a.needs_claude

    def test_clean_page(self):
        md = "## Introduction\n\nThis is normal text with no issues."
        a = assess_page(md, 0)
        assert not a.needs_claude
        assert not a.needs_gmft

class TestTableAnomaly:
    def test_br_in_tables(self):
        md = "| A | B |\n|---|---|\n| x<br>y | z |"
        a = assess_page(md, 0)
        assert a.needs_gmft
        assert a.table_anomaly

    def test_col_headers(self):
        md = "| Col1 | Col2 | Col3 |\n|---|---|---|\n| a | b | c |"
        a = assess_page(md, 0)
        assert a.needs_gmft

class TestTextDensity:
    def test_sparse_page(self):
        md = "[Figure 3]"
        a = assess_page(md, 0)
        assert a.low_text_density

    def test_normal_page(self):
        md = "x " * 200
        a = assess_page(md, 0)
        assert not a.low_text_density
```

### 13.2 Unit Tests — Routing

Test each routing action with mock assessments (no PDFs, no network):

```python
class TestRouting:
    def test_keep(self):
        a = PageAssessment(page_num=0)  # No issues
        d = route_page(a, None, "text", within_claude_budget=True)
        assert d.action == PageAction.KEEP

    def test_claude_replace(self):
        a = PageAssessment(page_num=0, needs_claude=True, severity=2.0)
        d = route_page(a, None, "text", within_claude_budget=True)
        assert d.action == PageAction.CLAUDE_REPLACE

    def test_claude_over_budget_fallback_gmft(self):
        a = PageAssessment(page_num=0, needs_claude=True, needs_gmft=True, severity=2.0)
        tables = [DetectedTable("| a | b |", 1.0, 2, 2, 5.0)]
        d = route_page(a, tables, "| Col1 |\n", within_claude_budget=False)
        assert d.action == PageAction.GMFT_REPLACE

    def test_gmft_replace(self):
        a = PageAssessment(page_num=0, needs_gmft=True, table_anomaly=True)
        tables = [DetectedTable("| a | b |", 1.0, 2, 2, 5.0)]
        d = route_page(a, tables, "| x<br>y |", within_claude_budget=True)
        assert d.action == PageAction.GMFT_REPLACE

    def test_gmft_append(self):
        a = PageAssessment(page_num=0)  # No issues flagged
        tables = [DetectedTable("| a | b |", 1.0, 2, 2, 5.0)]
        d = route_page(a, tables, "Some text, no tables", within_claude_budget=True)
        assert d.action == PageAction.GMFT_APPEND

    def test_strip_false(self):
        a = PageAssessment(page_num=0, needs_gmft=True, table_anomaly=True)
        md = "| Col1 | Col2 |\n|---|---|\n| x | y |"
        d = route_page(a, None, md, within_claude_budget=True)  # No GMFT available
        assert d.action == PageAction.STRIP_FALSE

    def test_strip_broken(self):
        a = PageAssessment(page_num=0, needs_gmft=True, table_anomaly=True)
        md = "| a<br>b | c |\n|---|---|\n| x | y |"
        d = route_page(a, None, md, within_claude_budget=True)
        assert d.action == PageAction.STRIP_BROKEN
```

### 13.3 Unit Tests — GMFT Filter

```python
class TestTableFilter:
    def test_no_confidence_filter(self):
        """Low-confidence detections pass through — Claude handles FP rejection."""
        t = DetectedTable("| a |", 0.92, 3, 2, 10.0)
        kept, reasons = filter_tables([t])
        assert len(kept) == 1  # No confidence filter (v2 finding)

    def test_prose_cells(self):
        t = DetectedTable("| long text... |", 1.0, 3, 2, 85.0)
        kept, _ = filter_tables([t])
        assert len(kept) == 0

    def test_layout_artifact(self):
        t = DetectedTable("| a | b | c | d | e |", 1.0, 1, 5, 3.0)
        kept, _ = filter_tables([t])
        assert len(kept) == 0

    def test_real_table_passes(self):
        t = DetectedTable("| a | b |", 1.0, 5, 3, 12.0)
        kept, _ = filter_tables([t])
        assert len(kept) == 1

    def test_img2table_detection_passes(self):
        """Img2Table detections use same secondary filters."""
        t = DetectedTable("| a | b |", 0.0, 3, 2, 8.0, detector="img2table")
        kept, _ = filter_tables([t])
        assert len(kept) == 1
```

### 13.4 Unit Tests — Table Quality Assessment and Enhancement

```python
class TestTableQualityAssessment:
    def test_extraction_failed_triggers_enhancement(self):
        t = DetectedTable("", 1.0, 0, 0, 0.0,
                       image_path=Path("/tmp/table.png"),
                       extraction_failed=True)
        needs, reasons = assess_table_quality(t)
        assert needs
        assert "extraction_failed" in reasons[0].lower()

    def test_good_table_no_enhancement(self):
        t = DetectedTable("| a | b |\n|---|---|\n| 1 | 2 |", 1.0, 1, 2, 3.0)
        needs, _ = assess_table_quality(t)
        assert not needs

    def test_suspect_quality_few_rows(self):
        # Image is large but only 1 data row — suspect
        t = DetectedTable("| a | b |\n|---|---|\n| 1 | 2 |", 1.0, 1, 2, 3.0,
                       image_path=Path("/tmp/large_table.png"))
        # Suspect quality detection depends on image size vs row count
        # Specific thresholds TBD during implementation
        ...

class TestTableEnhancement:
    def test_claude_empty_response_marks_false_positive(self):
        """Claude returning 0 rows = confirmed false positive (spike: aries p42, p48)."""
        # Mock Claude returning empty → table dropped
        ...

    def test_claude_extracts_from_cropped_image(self):
        """Claude extracts from cropped image when GMFT DataFrame fails."""
        # Mock Claude returning pipe table → table accepted with source="claude_cropped"
        ...

    def test_no_enhancement_without_image(self):
        """Table without image_path cannot be enhanced."""
        t = DetectedTable("", 1.0, 0, 0, 0.0, extraction_failed=True)
        # Should not attempt Claude without an image
        ...
```

### 13.5 Unit Tests — Table Utilities

```python
class TestTableUtilities:
    def test_strip_pipe_tables(self):
        md = "Text before\n| a | b |\n|---|---|\n| 1 | 2 |\n\nText after"
        result = strip_pipe_tables(md)
        assert "| a |" not in result
        assert "Text before" in result
        assert "Text after" in result

    def test_replace_tables(self):
        md = "Text\n| old | table |\n|---|---|\n| x | y |"
        tables = [DetectedTable("| new | data |\n|---|---|\n| a | b |", 1.0, 1, 2, 3.0)]
        result = replace_tables(md, tables)
        assert "| old |" not in result
        assert "| new |" in result

    def test_insert_tables_at_end(self):
        md = "Just text, no tables."
        tables = [DetectedTable("| a | b |\n|---|---|\n| 1 | 2 |", 1.0, 1, 2, 3.0)]
        result = insert_tables_at_end(md, tables)
        assert result.startswith("Just text")
        assert "| a | b |" in result
```

### 13.5 Unit Tests — Metrics

```python
class TestMetrics:
    def test_heading_count(self):
        md = "# H1\n## H2\n### H3\nNot a heading"
        m = compute_metrics(md)
        assert m.heading_count == 3
        assert m.heading_by_level == {1: 1, 2: 1, 3: 1}

    def test_table_rows(self):
        md = "| a | b |\n|---|---|\n| 1 | 2 |"
        m = compute_metrics(md)
        assert m.table_row_count == 3  # header + separator + data

    def test_math_symbols(self):
        md = "The integral ∫ and sum ∑ of α + β"
        m = compute_metrics(md)
        assert m.math_symbol_count >= 4  # ∫, ∑, α, β
```

### 13.6 Unit Tests — Claude Sanity Check (NFR-4)

```python
class TestClaudeSanityCheck:
    def test_accept_normal_output(self):
        original = "x " * 500  # 1000 chars
        claude = "y " * 450    # 900 chars (90% of original)
        accept, _ = validate_claude_output(claude, original, 0)
        assert accept

    def test_reject_empty_output(self):
        accept, reason = validate_claude_output("", "x " * 500, 0)
        assert not accept
        assert "empty" in reason.lower()

    def test_reject_truncated_output(self):
        original = "x " * 500  # 1000 chars
        claude = "y " * 100    # 200 chars (20% of original — >50% drop)
        accept, reason = validate_claude_output(claude, original, 0)
        assert not accept
        assert "drop" in reason.lower() or "50%" in reason

    def test_accept_short_page(self):
        # Short pages (< 200 chars) are exempt from ratio check
        # since Claude may legitimately produce less for figure-only pages
        original = "[Figure 3]"  # 10 chars
        claude = "[Figure 3: Reactor diagram]"
        accept, _ = validate_claude_output(claude, original, 0)
        assert accept
```

### 13.7 Unit Tests — Pandoc Convert

```python
class TestArxivDetection:
    def test_detect_arxiv_id(self):
        # Mock pymupdf to return page text with arXiv ID
        ...

    def test_no_arxiv(self):
        # Mock pymupdf to return text without arXiv ID
        ...

class TestPandocConvert:
    def test_strip_figure_tags(self):
        html = "<p>Text</p><figure><img src='x'><figcaption>Cap</figcaption></figure>"
        result = _preprocess_html(html)
        assert "<figure>" not in result

    def test_strip_hspace(self):
        md = "Text\\hspace{0pt}more"
        result = _postprocess_markdown(md)
        assert "\\hspace" not in result
```

### 13.8 Integration Tests — Corpus

```python
class TestCorpusIntegration:
    """Integration tests against real corpus PDFs.

    These tests require corpus PDFs in tests/corpus/pdfs/ and are
    marked with @pytest.mark.corpus to allow skipping in CI.
    """

    @pytest.mark.corpus
    def test_hawker_2020_quality_parity(self):
        """Verify production pipeline matches Stage 3 H5 on hawker_2020."""
        result = extract_pdf(PDFS_DIR / "hawker_2020.pdf",
                            PipelineConfig(claude_budget_usd=0))
        gt = load_ground_truth()["hawker_2020"]
        scores = score_against_ground_truth(result.metrics, gt)
        # Table quality should match H1 (1% error)
        assert scores["table_rows"].error_pct <= 10

    @pytest.mark.corpus
    def test_all_corpus_extract_successfully(self):
        """Every corpus PDF produces non-empty output (IC-3)."""
        for pdf in sorted(PDFS_DIR.glob("*.pdf")):
            result = extract_pdf(pdf, PipelineConfig(
                claude_budget_usd=0, enable_tables=False))
            assert result.markdown, f"{pdf.name} produced empty output"
            assert result.error is None, f"{pdf.name}: {result.error}"
```

### 13.9 Regression Detection

The test strategy catches:
- **Quality gate stops detecting math garbling:** `TestMathGarbling` tests fail
- **GMFT tables merged incorrectly:** `TestTableUtilities.test_replace_tables` fails
- **Table enhancement skipped for failed extraction:** `TestTableQualityAssessment.test_extraction_failed_triggers_enhancement` fails
- **Claude table false-positive rejection broken:** `TestTableEnhancement.test_claude_empty_response_marks_false_positive` fails
- **Routing regression:** `TestRouting` covers every action
- **Claude produces garbage:** `TestClaudeSanityCheck` catches empty/truncated output
- **Table filter reasons lost:** Table filter reasons captured in `PageDecision.details["table_filter"]` — visible in decisions.json
- **Metrics drift from ground truth:** `TestCorpusIntegration` compares against Stage 3 baselines

---

## 14. Experiment-to-Production Traceability (SC-9)

Every constant has a source:

| Constant | Value | Source |
|----------|-------|--------|
| Strikethrough severity (3+) | 2.0 | Stage 3 `quality_gate.py:21` — hawker 5/5 correct, 0 false positives |
| Strikethrough severity (1+) | 0.5 | Stage 3 `quality_gate.py:23` — below threshold alone |
| Replacement char severity (2+) | 2.0 | Stage 3 `quality_gate.py:28` — Unicode salad in math pages |
| Bracket operator severity (3+) | 1.0 | Stage 3 `quality_gate.py:34` — `[/][+]` patterns in garbled equations |
| Math threshold | 1.0 | Stage 3 `quality_gate.py:47` — cumulative score triggers Claude |
| Text density | 200 chars | Stage 3 `quality_gate.py:56` — figure-only pages |
| Heading density max | 3.0 | Stage 3 `quality_gate.py:69` — paischer_2025 = 68/24 = 2.83 headings/page |
| Heading anomaly boost | 0.5 | Stage 3 `h5_quality_gated.py:133` — side-effect heading improvement |
| GMFT confidence filter | **Removed** | Table spike v2: 10/11 filtered detections were real tables. Claude handles FP rejection. |
| GMFT cell length | 80 | Stage 2: hsu_2020 prose blocks avg 85-120 chars, data tables avg 5-20 |
| GMFT single-row cols | >4 | Stage 2: layout artifacts in hsu_2020 CAS descriptions |
| Img2Table: GMFT-empty pages only | — | Table spike v2: 7-page overlap with GMFT, 4 unique pages. Running on all pages would duplicate. |
| Img2Table: borderless=True | — | Table spike v2: borderless mode finds space-aligned tables (p35, p37, p39, p94 on aries) |
| Docling: optional third pass | — | Table spike v2: 34 detections on aries (vs 28 GT). ~6 over-detections, but likely near-complete recall. |
| Docling: off by default | — | Table spike v2: slow, requires MCP server. Diminishing returns after GMFT+Img2Table (86% recall). |
| Claude budget | $2.00 | Stage 3 H5: hold-out energy_amplifier (241pp) stays within budget |
| Claude cost/page | $0.078 | Stage 1D: observed Sonnet average across 8 experiments |
| Claude cost/table | $0.076 | Table-image spike: observed Sonnet average across 27 tables |
| Claude model | Sonnet | Stage 1D: best quality/cost ratio |
| Table enhance: extraction_failed trigger | — | Spike Track 1: 7/15 aries tables, GMFT detect OK, DataFrame null. Claude recovered all 7 |
| Table enhance: false-positive rejection | Claude returns 0 rows | Spike Track 1: p42, p48 on aries correctly rejected |
| No multi-pass / vote-resolve | — | Spike Tracks 2-3: zero accuracy gain on non-aries, anchoring failure on aries p4 (9 vs 22 rows) |
| No PyMuPDF find_tables() | — | Spike Track 0: 0 real tables on aries, over-detects prose paragraphs |
| No sequential review | — | Spike Track 3: 41% more expensive, worse on badly-extracted tables (anchors to GMFT structure) |
| Claude as FP filter | Perfect | Table spike v2: caught all 5 FPs on aries (3 from 0.90-0.98 range + 2 from original set) |

---

## 15. Anti-Pattern Prevention (SC-5)

### No Promote-Then-Demote

The old branch had:
1. `promote_bold_headers()` — aggressively promotes bold text to headings
2. `reject_noise_headers()` — filters out false promotions

The new pipeline doesn't have this pattern. The `CompositeHeaderDetector` runs once during pymupdf4llm extraction. If the headings are wrong, the quality gate detects it and routes to Claude for full-page replacement. There's no "fix-up" layer that undoes a previous layer's work.

### No Dormant Code (IC-6)

Every module is imported by `pipeline.py` or the CLI. The test for this:
```python
def test_no_dormant_modules():
    """Every module in extraction/ is imported by pipeline or CLI."""
    extraction_dir = Path("src/agentic_mbse/extraction")
    modules = {f.stem for f in extraction_dir.glob("*.py") if f.stem != "__init__"}

    # Modules that must be reachable from pipeline.py or __init__.py
    from agentic_mbse.extraction import pipeline  # triggers all pipeline imports
    imported = set()
    # ... inspect sys.modules for all extraction.* modules
    assert modules - imported == set()  # No unreachable modules
```

---

## 16. Migration Path (C-5)

The existing `ExtractionResult` type is preserved in `base.py` and remains in `__init__.py` exports. It's used by:
- `extract_cli.py` (old single-backend path)
- `pymupdf_backend.extract()` (old full-document extraction)
- `docling_backend.extract()`
- `pandoc_backend.extract()`
- Tests

The new `PipelineResult` is a different type for a different purpose. `ExtractionResult` represents a single-backend extraction with file paths. `PipelineResult` represents a multi-stage pipeline result with inline markdown, metrics, and decisions.

The CLI bridges them: when using the new pipeline, it creates the output directory structure and writes the `PipelineResult` artifacts. When using `--backend` (old path), it uses `ExtractionResult` as before.

No migration needed — both types coexist.

---

## 17. Implementation Order

### Phase 1: Types and Infrastructure
- `types.py` — pipeline data types (PageResult, PageAssessment, PageDecision, etc.)
- `metrics.py` — canonical ExtractionMetrics, compute_metrics(), ground truth scoring
- Update `__init__.py` with new exports
- Update `tests/corpus/metrics.py` to import from `agentic_mbse.extraction.metrics`

### Phase 2: Components (parallelizable)
- `quality_gate.py` — assess_page, route_page, prioritize_pages
- `tables.py` — detect_tables_ensemble (GMFT + Img2Table + Docling), filter_tables, assess_table_quality, enhance_table_with_claude, table markdown utilities
- `pandoc_convert.py` — arXiv detection + Pandoc conversion
- `claude_enhance.py` — render_page_image, extract_page_with_claude
- `pymupdf_backend.py` — add `extract_pages()`

### Phase 3: Orchestration
- `pipeline.py` — extract_pdf, _try_arxiv_shortcut, error isolation
- Wire into CLI (`extract_cli.py`)

### Phase 4: Tests
- Unit tests for each component (Phases 1-2)
- Integration tests against corpus (Phase 3)
- Remove deprecated modules and update test_extract_cli.py

### Phase 5: Cleanup
- Delete: `table_repair.py`, `ai_repair.py`, `claude_structure.py`
- Delete old `quality_gates.py` (replaced by new `quality_gate.py`)
- Delete old `table_extraction.py` (replaced by new `tables.py`)
- Update `test_quality_gates.py`, `test_table_extraction.py`, etc.
- Deprecation warnings on `--fix-tables`, `--enhance`, `--structure-only`

---

## 18. Acceptance Checklist

### Design Checklist (from requirements §10)

- [x] **SC-1: Clean Component Boundaries** — §4 defines each component with input/output types
- [x] **SC-2: Data Types Reflect Reality** — §3 maps PageResult → PageAssessment → PageDecision → PipelineResult
- [x] **SC-3: Per-Page Routing Is First-Class** — §1.2 decision #1, §4.5 route_page(), §5.1 merge loop
- [x] **SC-3b: Pipeline Not Hardcoded** — §7 analyzes 6 near-term iterations, all 1-2 files
- [x] **SC-4: Budget Awareness Composable** — §6 shows budget as pipeline parameter, not enhancer property
- [x] **SC-5: No Promote-Then-Demote** — §15 explicitly addresses
- [x] **SC-6: Graceful Degradation** — §11 shows full → minimal degradation path
- [x] **SC-7: Provenance as Design Concern** — §8 defines decision/cost logging in data types
- [x] **SC-8: Minimal Surface Area** — §9 shows 2 imports for normal use
- [x] **SC-9: Experiment Traceability** — §14 traces every constant to Stage 3 and table-image spike
- [x] **SC-10: Test Strategy** — §13 covers unit, integration, and regression tests
- [x] Architecture diagram — §1.1
- [x] Disposition of every existing module — §2.2
- [x] Type definitions — §3
- [x] Public API surface — §9
- [x] Dependency management — §11
