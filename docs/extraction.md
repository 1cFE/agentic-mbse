# PDF & DOCX Extraction

Extract PDF and DOCX documents into structured markdown for use as domain knowledge in MBSE projects.

## Quick Start

```bash
# Extract a single PDF
uv run agentic-mbse extract paper.pdf

# Extract all PDFs and DOCXs in a directory
uv run agentic-mbse extract papers/
```

This creates an output directory named after the input file (e.g., `paper/`) containing `output.md` and supporting metadata files.

## CLI Reference

```
agentic-mbse extract <path> [options]
```

`<path>` can be a single PDF/DOCX file or a directory containing documents.

### General Options

| Flag | Default | Description |
|------|---------|-------------|
| `--output, -o DIR` | alongside input | Output base directory |
| `--force, -f` | off | Reprocess even if output already exists |
| `--index` | off | Generate an `INDEX.md` with section headings after extraction |
| `--summarize` | off | Include AI summaries in INDEX.md (requires `--index`) |

### PDF Pipeline Options

| Flag | Default | Description |
|------|---------|-------------|
| `--budget USD` | 2.0 | Claude spending limit in USD (0 = no Claude) |
| `--model {opus,sonnet,haiku}` | sonnet | Claude model for enhancement |
| `--no-tables` | off | Disable all table detection |
| `--no-img2table` | off | Disable Img2Table second-pass table detection |
| `--docling` | off | Enable Docling third-pass table detection |
| `--dry-run` | off | Show quality gate decisions without calling Claude |
| `--html-path PATH` | auto-detect | arXiv HTML file for Pandoc shortcut (overrides auto-detect) |

### DOCX Options

| Flag | Default | Description |
|------|---------|-------------|
| `--backend {docling,pymupdf,pandoc}` | auto | Force extraction backend (DOCX only) |
| `--timeout SECONDS` | 600 | Backend timeout for DOCX extraction |

## Output Files

For each PDF, the pipeline writes to `<output_dir>/`:

| File | Contents |
|------|----------|
| `output.md` | The extracted markdown |
| `metrics.json` | Quality metrics: character count, heading count/distribution, table row count, math symbol count, figure references, extraction time |
| `decisions.json` | Per-page quality gate decisions: what action was taken and why |
| `cost.json` | Per-call Claude API costs (only written when Claude was used) |

If `--index` is passed, an additional `INDEX.md` is generated with section headings extracted from the markdown.

## How the Pipeline Works

PDFs go through an 8-step pipeline:

1. **arXiv shortcut** — If the PDF has an arXiv ID and Pandoc is available, tries to convert the HTML version directly. This produces clean markdown without needing Claude. Skips remaining steps on success.

2. **Base extraction** — Uses pymupdf4llm to convert each page to markdown. This is the only step that can cause a hard failure.

3. **Ensemble table detection** — Detects tables using GMFT (primary), optionally Img2Table (second pass), and optionally Docling (third pass). Runs independently of the base extraction.

4. **Table filtering and enhancement** — Filters out low-quality detected tables, then optionally sends poor-quality tables to Claude for re-extraction. Uses the same `--budget` pool as page enhancement.

5. **Quality gate** — Assesses each page for problems: math garbling (strikethroughs, replacement characters, bracket-encoded operators), table anomalies (`<br>` artifacts, auto-generated `ColN` headers), and low text density. Also checks for document-level heading anomalies.

6. **Budget allocation** — Ranks pages needing Claude by severity score and selects the top N that fit within the remaining budget (after table enhancement spending).

7. **Claude page enhancement** — Sends selected pages to Claude for vision-based re-extraction. Each result is validated against the original before acceptance.

8. **Route and merge** — Each page gets routed to a final action based on the quality assessment and available results:
   - **KEEP** — page is fine, use as-is
   - **CLAUDE_REPLACE** — replace with Claude's re-extraction (math/density issues, within budget)
   - **GMFT_REPLACE** — replace inline tables with GMFT-detected tables (table anomalies)
   - **GMFT_APPEND** — append GMFT tables that pymupdf4llm missed
   - **STRIP_FALSE** — remove falsely-detected tables (ColN auto-headers from diagrams)
   - **STRIP_BROKEN** — remove broken tables (`<br>` artifacts)

The final markdown is assembled from all merged pages with output metrics computed.

## Cost Control

The `--budget` flag controls how much the pipeline can spend on Claude API calls. The budget is shared between table enhancement and page re-extraction.

| Budget | Behavior |
|--------|----------|
| `--budget 2.0` (default) | Up to $2.00 of Claude calls, prioritized by severity |
| `--budget 0` | No Claude calls at all — pymupdf4llm + table detection only |
| `--budget 0.50` | Light enhancement — only the worst pages get Claude |

Use `--dry-run` to preview what the quality gate would decide without spending anything:

```bash
uv run agentic-mbse extract paper.pdf --dry-run
```

This runs the full pipeline through table detection and quality assessment, writes `decisions.json` showing what *would* happen, but skips all Claude API calls. The output markdown reflects pymupdf4llm + table detection only.

The `--model` flag also affects cost: `haiku` is cheapest, `sonnet` (default) balances quality and cost, `opus` is most expensive but highest quality.

## Dependencies

**pymupdf4llm** and **Img2Table** are included in the base install — no extras needed for core PDF extraction and table detection.

The following optional dependencies enhance the pipeline but are not required. The pipeline degrades gracefully when they are missing.

| Dependency | What it does | When missing |
|------------|-------------|--------------|
| **GMFT** | Primary table detection from page images | Tables only detected by Img2Table; install via `agentic-mbse[extract-tables]` |
| **Docling** | Third-pass table detection | Off by default; enable with `--docling` after installing `agentic-mbse[extract-full]` |
| **Pandoc** | arXiv HTML shortcut for clean conversion | arXiv shortcut skipped; falls through to normal pipeline |
| **Claude API** (`ANTHROPIC_API_KEY`) | Page re-extraction and table enhancement | Same as `--budget 0` — quality gate still runs, but no Claude calls |

### Install extras

```bash
# Table detection with GMFT
uv add agentic-mbse[extract-tables]

# Full (GMFT + Docling)
uv add agentic-mbse[extract-full]
```

## DOCX Extraction

DOCX files use a separate backend path (not the PDF pipeline). The backend is auto-selected:

1. **Docling** (preferred) — full-featured conversion
2. **Pandoc** (fallback) — simpler conversion via the `pandoc` CLI tool

Force a specific backend with `--backend`:

```bash
uv run agentic-mbse extract report.docx --backend pandoc
```

If the chosen backend fails and no backend was explicitly requested, the pipeline automatically tries the next available option.
