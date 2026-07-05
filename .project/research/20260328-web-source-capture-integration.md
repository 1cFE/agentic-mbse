---
date: 2026-03-28
researcher: Claude
topic: "Integration design for web source capture and HTML extraction into agentic-mbse"
tags: [research, architecture, extraction, web-capture, html, sanitization]
status: complete
---

# Research: Web Source Capture Integration for agentic-mbse

**Date**: 2026-03-28
**Research Type**: Architecture / Integration Design

## Context

Two research reports from fusion-tea identify a gap: agentic-mbse has excellent PDF extraction but no HTML/URL extraction capability. Claude Code's WebFetch returns Haiku paraphrases, not actual content — making it fundamentally unsuitable for capturing citable source material. The question is: what's the right way to add web source capture to agentic-mbse?

**Input research:**
- `fusion-tea/.project/research/20260328-source-capture-pipeline-feasibility.md`
- `fusion-tea/.project/research/20260328-web-content-sanitization-for-llm-pipelines.md`

---

## The Problem in One Sentence

agentic-mbse can extract PDFs superbly but cannot fetch a URL and produce clean markdown — the one missing piece needed by automated research pipelines.

---

## Existing Architecture Analysis

### What We Have

The extraction module (`src/agentic_mbse/extraction/`) is a mature, well-factored system:

| Component | Pattern | Notes |
|-----------|---------|-------|
| `pipeline.py` | 8-step orchestrator | Quality-gated, budget-aware, early-exit on arXiv |
| `extract_cli.py` | Subcommand registration | `register_extract_subcommand(subparsers)` pattern |
| `types.py` | Pydantic-style dataclasses | `PipelineResult`, `CostRecord`, `ExtractionMetrics` |
| `base.py` | Shared utilities | `ExtractionResult`, `sanitize_filename()`, `write_summary()` |
| `pandoc_convert.py` | URL-aware HTML→MD | arXiv-only: `detect_arxiv_id()` → `check_arxiv_html()` → `convert_arxiv_html()` |
| `postprocess.py` | Backend-agnostic cleanup | Ligatures, headers, page numbers |
| `metrics.py` | Quality measurement | `compute_metrics()` on markdown output |
| `index.py` | TOC generation | Section parsing, optional AI summaries |

### Key Design Patterns to Follow

1. **Backends are pluggable**: pymupdf4llm / docling / pandoc — new backends slot in alongside
2. **Pipeline stages are error-isolated**: Each step wrapped in try/except, logs but continues
3. **Results are typed**: `PipelineResult` carries markdown + metrics + decisions + cost
4. **CLI registration is modular**: `register_extract_subcommand()` adds argparse group
5. **arXiv shortcut is precedent**: `pandoc_convert.py` already fetches URLs, preprocesses HTML, runs Pandoc — this is exactly the pattern to generalize

### What's Missing

- No general URL fetching (only arXiv)
- No HTML sanitization (hidden content stripping)
- No content extraction for arbitrary HTML (only Pandoc conversion)
- No metadata capture (URL, access date, content hash)
- No CLI subcommand for web content

---

## Design Options

### Option A: Extend `extract` Subcommand

Add URL support directly to `agentic-mbse extract`:

```
agentic-mbse extract https://example.com/article.html
agentic-mbse extract paper.pdf           # existing behavior
agentic-mbse extract report.docx         # existing behavior
```

**Pros**: Single entry point, users don't learn a new command, consistent output format.
**Cons**: The extraction pipeline is deeply PDF-oriented (quality gates, page routing, Claude vision). Bolting HTML onto it requires either (a) a separate code path inside `extract` or (b) forcing HTML through PDF abstractions that don't fit.

### Option B: New `fetch` Subcommand

Dedicated subcommand for URL→markdown:

```
agentic-mbse fetch https://example.com/article.html
agentic-mbse fetch https://example.com/article.html --output sources/
agentic-mbse fetch urls.txt              # batch mode
```

**Pros**: Clean separation, purpose-built for the use case, no risk of destabilizing PDF pipeline.
**Cons**: Two commands for "give me markdown from this source" — users must know which to use.

### Option C: Thin Dispatch in `extract`, Implementation Separate

`extract` detects input type (URL vs PDF vs DOCX) and dispatches to the appropriate backend. HTML/URL goes to a new `web_backend.py`, PDFs go to existing pipeline:

```
agentic-mbse extract https://example.com/article.html  # dispatches to web_backend
agentic-mbse extract paper.pdf                          # dispatches to pdf pipeline
```

**Pros**: Single user-facing command, clean internal separation, follows existing backend pattern.
**Cons**: `extract` CLI grows more complex, but this is manageable.

### Recommendation: Option C

This follows the existing pattern where `extract` already dispatches between PDF and DOCX backends. Adding URL/HTML as a third backend is the natural extension. The key constraint: the web backend should be a self-contained module that shares types (`ExtractionResult`, metrics) but not the PDF-specific pipeline.

---

## Proposed Architecture

### New Files

```
src/agentic_mbse/extraction/
    web_backend.py      # URL fetch + sanitize + extract + metadata
    sanitize.py         # HTML sanitization (BeautifulSoup pre-pass) — reusable
```

### `web_backend.py` — Core Pipeline

```
fetch_url(url) → raw HTML string
    ↓
sanitize_html(html) → cleaned HTML string     [sanitize.py]
    ↓
extract_content(html, url) → markdown + metadata   [trafilatura]
    ↓
ExtractionResult(markdown, metadata, metrics)
```

**Functions:**

- `fetch_url(url: str, timeout: int = 30) -> str` — `urllib.request` (already used in `pandoc_convert.py`), returns HTML. Handles redirect, encoding detection, User-Agent header.
- `extract_web_content(url: str, output_dir: Path | None = None) -> WebExtractionResult` — Full pipeline: fetch → sanitize → extract → optionally write .md with YAML frontmatter + metrics.json.

**Output format** (matches PDF extraction pattern):

```
output_dir/
    article-title.md         # Markdown with YAML frontmatter
    metrics.json              # ExtractionMetrics (char_count, heading_count, etc.)
```

**YAML frontmatter** in the .md:

```yaml
---
source_url: "https://example.com/article"
access_date: "2026-03-28T14:30:00-05:00"
content_hash_sha256: "a1b2c3..."
title: "Article Title"
author: "Author Name"
extraction_tool: "trafilatura"
---
```

### `sanitize.py` — Reusable HTML Sanitization

Extracted as its own module because:
1. The `/research` command could use it independently (sanitize HTML from WebFetch before analysis)
2. Future tools (source enrichment, batch processing) will need it
3. It's testable in isolation

**Core function**: `strip_hidden_content(html: str) -> str`

Based on the research reports' recommended 3-layer approach:
1. Remove `<script>`, `<style>`, `<noscript>`, `<iframe>`, `<embed>`, `<object>`
2. Remove CSS-hidden elements (`display:none`, `visibility:hidden`, `opacity:0`, `font-size:0`, off-screen positioned)
3. Remove `hidden` attribute, `aria-hidden="true"` elements
4. Strip zero-width Unicode characters

This is the gap no standard Python library fills — trafilatura/readability/html2text all miss CSS-hidden text.

### CLI Integration

In `extract_cli.py`, detect URL input and dispatch:

```python
def cmd_extract(args):
    path = args.input
    if path.startswith(("http://", "https://")):
        from agentic_mbse.extraction.web_backend import extract_web_content
        result = extract_web_content(path, output_dir=args.output)
        ...
    elif path.endswith(".pdf"):
        # existing PDF pipeline
        ...
```

Add URL-specific flags:
- `--no-sanitize` — Skip the BeautifulSoup hidden-content stripping (for trusted sources)
- `--raw-html` — Also save the raw HTML alongside markdown (for archival)

### Dependencies

| Dependency | Purpose | Status |
|-----------|---------|--------|
| `trafilatura` | Article extraction + metadata | New — `uv add trafilatura` |
| `beautifulsoup4` | HTML sanitization pre-pass | New — `uv add beautifulsoup4` |
| `lxml` | Fast HTML parser for BeautifulSoup | Likely already installed (transitive dep of trafilatura) |
| `urllib.request` | URL fetching | stdlib, already used in `pandoc_convert.py` |

**trafilatura** is the right choice over alternatives:
- Best benchmarked F1 (0.883) for content extraction
- Outputs markdown directly (since v1.9)
- Extracts metadata (title, author, date, URL)
- Actively maintained (2.0.0)
- Handles boilerplate removal (nav, ads, sidebars) — critical for non-academic pages

---

## What About the arXiv Shortcut?

`pandoc_convert.py` currently handles arXiv HTML→markdown via Pandoc. Two options:

**Option 1: Leave it alone.** arXiv HTML has LaTeXML-specific quirks (CSS transforms, special `<figure>` handling) that the general trafilatura path might not handle as well. The arXiv shortcut is battle-tested and works.

**Option 2: Route arXiv through the new web backend.** Simpler codebase, one path for all HTML.

**Recommendation: Option 1 (leave it).** The arXiv shortcut is specifically tuned for LaTeXML output and integrated into the PDF pipeline's early-exit logic. Disturbing it adds risk for no user-visible benefit. If someone passes an arXiv HTML URL to `extract`, we can detect it and route to the existing shortcut.

---

## Integration with `/research` and `/manage-sources` Commands

### `/research` Command Impact

The research command currently uses WebSearch + WebFetch. With the new web backend available:

1. Research agents can use `Bash(uv run agentic-mbse extract <url>)` to capture full source content
2. This produces citable markdown with metadata — far richer than WebFetch's Haiku summaries
3. WebFetch remains useful for quick checks ("does this URL have what I need?") before committing to full extraction

No changes needed to the command itself — the agent just gains a better tool in its toolkit.

### `/manage-sources` Command Impact

`manage-sources` currently records source metadata in `knowledge/SOURCE_INDEX.md`. A natural extension:

```
/manage-sources add https://example.com/paper.html
→ Runs agentic-mbse extract <url> → saves to knowledge/sources/
→ Registers in SOURCE_INDEX.md with metadata from extraction
```

This is a future enhancement, not a prerequisite. The core extraction capability should land first.

---

## Scope Boundaries

### In Scope for agentic-mbse

- **URL→markdown extraction**: Fetch, sanitize, extract article content, save with metadata
- **HTML sanitization**: Reusable module for stripping prompt injection vectors
- **CLI integration**: `agentic-mbse extract <url>` dispatching to web backend
- **Batch URL processing**: `agentic-mbse extract urls.txt` reading URLs from a file

### Out of Scope (belongs in consuming projects like fusion-tea)

- **Source enrichment workflows**: Re-fetching existing thin sources — this is pipeline-specific logic
- **Phase 1a prompt redesign**: Telling research agents to use curl instead of WebFetch — this is prompt engineering
- **Trust boundary injection**: Adding "EXTERNAL DATA" framing to LLM prompts — this is per-pipeline
- **Rate limiting / politeness**: Delays between batch fetches — add if users request it
- **JavaScript rendering**: No headless browser. If a page requires JS, it's out of scope.

---

## Implementation Estimate

| Phase | Effort | Description |
|-------|--------|-------------|
| 1. `sanitize.py` | 0.5 day | Hidden content stripping, zero-width char removal, tests |
| 2. `web_backend.py` | 1 day | Fetch, sanitize, extract, metadata, output formatting |
| 3. CLI integration | 0.5 day | URL detection in extract, new flags, URL-from-file batch mode |
| 4. Tests | 0.5 day | Unit tests for sanitize, integration tests for web extraction |
| **Total** | ~2.5 days | |

### Dependencies to Add

```bash
uv add trafilatura beautifulsoup4
uv add --dev responses  # for mocking HTTP in tests (if not already present)
```

---

## Risks

1. **trafilatura quality on non-article pages**: Company homepages, Wikipedia, and institutional pages may not extract as cleanly as journal articles. Mitigation: fallback to pandoc conversion (already available) if trafilatura returns empty/short content.

2. **Dependency weight**: trafilatura pulls in ~15 transitive deps. This is acceptable for a toolkit that already depends on pymupdf, docling, etc.

3. **Encoding edge cases**: Non-UTF-8 pages, mixed encoding, broken HTML. Mitigation: trafilatura handles most of this; `sanitize.py` should be defensive about encoding.

---

## Decision Points for Implementation

1. **Should `sanitize.py` be in `extraction/` or a top-level `utils/`?** Recommendation: `extraction/` — it's part of the extraction pipeline and doesn't have broader utility yet.

2. **Should we save raw HTML alongside markdown?** Recommendation: opt-in via `--raw-html` flag, default off. Raw HTML is a security liability if accidentally fed to an LLM.

3. **Should batch mode read URLs from stdin or a file?** Recommendation: file (one URL per line), consistent with other batch tools. Stdin can be added later.

4. **Should metadata go in YAML frontmatter or a sidecar `.meta.yaml`?** Recommendation: YAML frontmatter in the .md file. This matches the existing source document format in fusion-tea's `knowledge/sources/` and keeps metadata co-located with content.

---

## Sources

- fusion-tea research: Source Capture Pipeline Feasibility (2026-03-28)
- fusion-tea research: Web Content Sanitization for LLM Pipelines (2026-03-28)
- agentic-mbse codebase: `src/agentic_mbse/extraction/` (v4 pipeline architecture)
- agentic-mbse codebase: `src/agentic_mbse/cli/extract_cli.py` (CLI patterns)
- agentic-mbse codebase: `src/agentic_mbse/extraction/pandoc_convert.py` (arXiv URL precedent)
