---
name: pdf-analysis
description: >
  This skill should be used when the user asks to "extract PDF", "analyze this PDF",
  "read this paper", "get the table from page X", "extract content from document",
  "convert PDF to markdown", "what does this PDF say", or mentions PDF page extraction,
  document analysis, or paper reading. Provides a 3-tier extraction pipeline
  (pymupdf4llm → Docling MCP → image fallback) with memory-safe single-page workflows.
allowed-tools: Read, Write, Bash, Glob, Grep
user-invocable: true
---

# PDF Analysis

Extract and analyze content from PDF documents using a 3-tier fallback pipeline optimized for accuracy and memory safety.

**Page numbering is 0-indexed** (first page = 0).

The extraction script is at `.claude/skills/pdf-analysis/scripts/extract_page.py` relative to the project root.

## Extraction Pipeline

Try each tier in order. Advance to the next only when the current tier produces inadequate results.

<!-- TIER_HINT_START -->
**System tier: {DOCLING_TIER} — Max {MAX_PAGES} pages per Docling call.**
<!-- TIER_HINT_END -->

### Tier 1: pymupdf4llm (Fast, Default)

Extract page content as markdown using pymupdf4llm. This is the fastest method and works well for text-heavy pages.

```bash
uv run python .claude/skills/pdf-analysis/scripts/extract_page.py <pdf_path> <page> --mode markdown
```

**Evaluate the output.** If text reads coherently, tables are recognizable, and key data is present — stop here. Escalate to Tier 2 only if:
- Tables are garbled or structure is lost
- Column text is interleaved
- Layout-dependent content is unreadable

<!-- DOCLING_START -->
### Tier 2: Docling MCP (High-Fidelity Tables)

For pages with complex tables or layouts, use the Docling MCP server. **Critical memory constraint: never send a multi-page PDF to Docling.**

**Step 1** — Extract the target page as a single-page PDF:
```bash
uv run python .claude/skills/pdf-analysis/scripts/extract_page.py <pdf_path> <page> --mode pdf --output /tmp/page_<N>.pdf
```

**Step 2** — Convert via Docling MCP:
Use `mcp__docling__convert_document_into_docling_document` with source `/tmp/page_<N>.pdf`. This returns a `document_key`.

**Step 3** — Export to markdown:
Use `mcp__docling__export_docling_document_to_markdown` with the document key.

**Timeout/failure** — If Docling is slow (>30s) or unresponsive, fall back to Tier 3. Do not retry.

<!-- DOCLING_END -->

### Tier 3: Image + Vision (Universal Fallback)

Render the page as a 200 DPI PNG and analyze visually.

```bash
uv run python .claude/skills/pdf-analysis/scripts/extract_page.py <pdf_path> <page> --mode image --output /tmp/page_<N>.png
```

Then read the image with the Read tool and reconstruct the content as markdown. Preserve numerical values exactly. Describe figures and diagrams.

## Quick Start Workflow

1. **Get PDF info** — determine page count and structure:
   ```bash
   uv run python .claude/skills/pdf-analysis/scripts/extract_page.py <pdf_path> --info
   ```

2. **Extract target pages** — start with Tier 1 for each page of interest:
   ```bash
   uv run python .claude/skills/pdf-analysis/scripts/extract_page.py <pdf_path> <page> --mode markdown
   ```

3. **Evaluate and escalate** — only move to Tier 2/3 for pages that need it.

## When to Skip Tiers

| Situation | Start At |
|-----------|----------|
| Text-heavy page, no tables | Tier 1 |
<!-- DOCLING_START -->
| Page with important tables | Tier 1, escalate to Tier 2 if garbled |
<!-- DOCLING_END -->
| Scanned PDF (no text layer) | Tier 3 directly |
| Diagrams or figures to describe | Tier 3 directly |
| Equations or math notation | Tier 3 directly |

## Script Reference

The bundled extraction script supports all three modes:

| Flag | Purpose |
|------|---------|
| `--info` | Show page count and metadata |
| `--mode markdown` | Tier 1: pymupdf4llm extraction |
| `--mode pdf` | Tier 2 prep: single-page PDF for Docling |
| `--mode image` | Tier 3: render as PNG |
| `--dpi N` | Image resolution (default: 200) |
| `--output PATH` | Output file path |

## Additional Resources

### Reference Files

For backend comparison, troubleshooting, and advanced workflows:
- **`references/extraction-details.md`** — Detailed backend comparison, Docling MCP invocation steps, multi-page batch patterns, and troubleshooting guide
