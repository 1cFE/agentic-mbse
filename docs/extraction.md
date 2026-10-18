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
| `--html-path PATH` | auto-detect | arXiv HTML file for the Pandoc shortcut. Uses this file instead of identifying the paper; cannot be combined with `--no-arxiv-shortcut` |
| `--arxiv-shortcut` / `--no-arxiv-shortcut` | [see below](#the-arxiv-shortcut) | Replace a PDF with its arXiv HTML version when the PDF identifies itself as an arXiv paper. `--no-arxiv-shortcut` forces normal PDF extraction with Pandoc still on PATH. See [The arXiv shortcut](#the-arxiv-shortcut) |

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
| `images/` | Saved images, referenced from `output.md` as `images/<name>` |
| `metrics.json` | Quality metrics: character count, heading count/distribution, table row count, math symbol count, figure references, extraction time, and `image_count` (image files saved under `images/`; the per-item summary line shows the same count). A `warnings` list is added when anything fell back or was not saved (see below). Written for failed extractions too, so their warnings are kept |
| `decisions.json` | Per-page quality gate decisions: what action was taken and why |
| `cost.json` | Per-call Claude API costs (only written when Claude was used) |

If `--index` is passed, an additional `INDEX.md` is generated with section headings extracted from the markdown.

## How the Pipeline Works

PDFs go through an 8-step pipeline:

1. **arXiv shortcut** — If the PDF identifies itself as an arXiv paper and Pandoc is available, converts the paper's arXiv HTML version instead, with its figures saved to `images/`. This produces clean markdown without needing Claude. Skips remaining steps on success. See [The arXiv shortcut](#the-arxiv-shortcut).

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

## The arXiv shortcut

When a PDF is an arXiv paper, the pipeline can replace PDF extraction with a Pandoc conversion of the paper's arXiv HTML version. The HTML version has exact headings, equations and tables, at no Claude cost.

**When it fires.** The PDF must name its own arXiv ID through trusted evidence:

- the stamp arXiv prints rotated in the left margin of page 1 (`arXiv:2610.14224v1 [cs.AI] 9 Oct 2026`), or
- the arxiv.org URL the PDF was downloaded from (`arxiv.org/abs/<id>` or `arxiv.org/pdf/<id>`), when you extract a PDF URL.

An arXiv ID anywhere in the text, such as a citation, never counts. If the stamp and the URL name different papers, or page 1 carries two stamps, the PDF is extracted normally and a warning says why. PDFs that didn't come from arXiv (publisher versions, author builds) carry no stamp, so they go through normal PDF extraction. That is intended.

**What it produces.** Only the paper is converted: the single `<article class="ltx_document">` arXiv wraps it in. The site header, navigation, issue-report dialog, footers, funder logos and UI icons are left out. Images that belong to the paper are kept and saved as files in `images/`, referenced as `images/<name>`. Figures are downloaded once each. Small diagrams the HTML embeds inline as `data:` images are written out as files too, under content-hash names, so `output.md` has no `data:` links. The one other thing removed inside the paper is the download button LaTeXML attaches to each code listing, whose text is the listing shown right below it. An image that can't be saved keeps its original reference and adds one warning. Without an images directory (Python use only, see below), figure references and inline `data:` images stay as written. When the page has no recognized article element, the shortcut is skipped with a warning and the PDF is extracted normally.

**Turning it off.** The shortcut is on by default. Pass `--no-arxiv-shortcut`, or `PipelineConfig(arxiv_shortcut=False)` in Python, to extract the PDF itself with Pandoc still on PATH. `--arxiv-shortcut` turns it on explicitly. `--html-path` gives the HTML file to convert, and runs whatever the default is. Combining it with `--no-arxiv-shortcut` is an error: the CLI exits with status 2, and `PipelineConfig` raises `ValueError`. The flag applies to local PDFs, PDF URLs, `--urls-from` batches and `--check`.

**`--check`.** The Pandoc probe applies the same rule: it reports whether the PDF is identified as an arXiv paper and fetches nothing when it isn't. With `--no-arxiv-shortcut` it reports the shortcut as disabled. When it converts, it reports the converted character count. The `arxiv_shortcut` capability is on only when `extract` would take the shortcut: enabled, the paper identified, and its HTML version available and converted. It does not download images.

**Python use without an images directory.** `extract_pdf` saves figures only when `PipelineConfig.extracted_images_dir` is set (the CLI always sets it to `<output>/images`). Without it, the converted markdown keeps arXiv's relative figure references, which do not resolve locally, and its inline `data:` images.

**Direct arXiv HTML URLs.** `agentic-mbse extract https://arxiv.org/html/<id>` uses the same paper-only conversion and figure saving. If the conversion fails, the page is extracted with trafilatura (backend `trafilatura`) and a warning names the reason. The whole page is never converted with Pandoc.

### Warnings

Fallbacks and unsaved images are reported three ways:

- in the returned result (`PipelineResult.warnings`, `ExtractionResult.warnings`),
- in `metrics.json` under `warnings`,
- on stderr.

Web-extraction warnings go to stderr only; they used to be printed to stdout. A shortcut that simply doesn't apply (no Pandoc, no arXiv evidence, turned off) is not a warning.

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
| **Pandoc** | arXiv HTML shortcut for clean conversion | arXiv shortcut skipped; falls through to normal pipeline (with a warning if `--html-path` was given) |
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
