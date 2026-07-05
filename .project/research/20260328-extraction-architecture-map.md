---
date: 2026-03-28T18:30:00-07:00
researcher: Claude
topic: "Extraction architecture: modes, modules, outputs, and raw source saving"
tags: [research, extraction, architecture]
status: complete
last_updated: 2026-03-28
---

# Research: Extraction Architecture Map

**Date**: 2026-03-28 18:30 PDT
**Researcher**: Claude
**Research Type**: Architecture

## Research Questions

A) Map all extraction modes: entry points, shared modules, outputs
B) Does the library save original/raw sources during fetches? When and how?

## Summary

- The `extract` CLI has **5 entry points** (single URL, batch URLs, single file, directory scan, check mode) that fan out through **3 extraction pipelines** (PDF pipeline, DOCX backends, web backend)
- The PDF pipeline has an **arXiv HTML shortcut** (Step 1) that fetches HTML from arxiv.org and converts via Pandoc — this is a web fetch hidden inside the PDF path
- A URL classified as PDF downloads to a temp file and **re-enters `cmd_extract()`**, running through the identical PDF pipeline (including the arXiv shortcut)
- All pipelines converge on `ExtractionResult` or `PipelineResult` and write to a per-document output directory
- Raw source saving exists **only for web extraction** via `--raw-html` flag; the arXiv shortcut and PDF URL download paths discard their fetched content after conversion
- The arXiv shortcut and general web backend both convert HTML→markdown but use **different tools and pre-processing** for good reason (known structure vs. arbitrary pages)

## A) Architecture Diagram

### Complete Extraction Flow

```
                          ┌───────────────────────────────────┐
                          │     CLI: cmd_extract(args)         │
                          │     extract_cli.py:309             │
                          └──────────┬────────────────────────┘
                                     │
          ┌──────────────────────────┼───────────────────────────┐
          │                          │                           │
     URL input?                --urls-from?               File/dir path
          │                          │                           │
          ▼                          ▼                           ▼
 ┌─────────────────┐   ┌───────────────────┐      ┌──────────────────────┐
 │ _extract_url()  │   │ _extract_urls_    │      │ discover_documents() │
 │ :196            │◄──│ from_file() :273  │      │ :60                  │
 └────────┬────────┘   │ (loops, calls     │      └──────────┬───────────┘
          │            │  _extract_url)    │                  │
          │            └───────────────────┘       ┌──────────┴──────────┐
          ▼                                        │                     │
 ┌─────────────────┐                         .pdf files            .docx files
 │  classify_url() │                               │                     │
 │ web_backend:65  │                               │                     │
 │ (HEAD request)  │                               │                     │
 └────────┬────────┘                               │                     │
          │                                        │                     │
   ┌──────┴──────┐                                 │                     │
   │             │                                 │                     │
 "html"        "pdf"                               │                     │
   │             │                                 │                     │
   │             ▼                                 │                     │
   │     ┌────────────────┐                        │                     │
   │     │_extract_pdf_   │    re-enters           │                     │
   │     │url() :245      │──cmd_extract()──►──────┘                     │
   │     │download to tmp │    (same PDF                                 │
   │     └────────────────┘     pipeline)                                │
   │                                               │                     │
   ▼                                               ▼                     ▼
┌──────────────┐                     ┌──────────────────┐   ┌──────────────────┐
│  WEB BACKEND │                     │   PDF PIPELINE   │   │  DOCX BACKENDS   │
│ web_backend  │                     │  extract_pdf()   │   │_run_extraction() │
│   .py        │                     │  pipeline.py:331 │   │extract_cli:116   │
│              │                     │                  │   │                  │
│ trafilatura  │                     │ ┌──────────────┐ │   │ docling_backend  │
│ + sanitize   │                     │ │Step 1: arXiv │ │   │ pandoc_backend   │
│ + pandoc     │                     │ │HTML shortcut │ │   │ pymupdf_backend  │
│   fallback   │                     │ │(early return │ │   │                  │
└──────────────┘                     │ │if arXiv PDF) │ │   └──────────────────┘
                                     │ └──────┬───────┘ │
                                     │   success? ──yes──► return PipelineResult
                                     │        │ no       │   source="pandoc_arxiv"
                                     │        ▼          │
                                     │ Step 2: pymupdf   │
                                     │ Step 3: tables    │
                                     │ Step 4: quality   │
                                     │ Step 5: budget    │
                                     │ Step 6: Claude    │
                                     │ Step 7: merge     │
                                     │ Step 8: result    │
                                     └──────────────────┘
```

### Two HTML→Markdown Paths (and Why They're Different)

The codebase has two distinct HTML-to-markdown conversion paths. They share
Pandoc flags but are intentionally different in approach:

```
                    ┌─────────────────────────────────────────────┐
                    │          HTML → Markdown Conversion          │
                    ├──────────────────────┬──────────────────────┤
                    │   arXiv Shortcut     │   Web Backend        │
                    │   pandoc_convert.py  │   web_backend.py     │
                    ├──────────────────────┼──────────────────────┤
                    │                      │                      │
  Trigger:          │ PDF has arXiv ID +   │ User passes URL to   │
                    │ HTML available at    │ `extract https://..` │
                    │ arxiv.org/html/{id}  │                      │
                    │                      │                      │
  Input HTML:       │ LaTeXML-generated    │ Arbitrary web page   │
                    │ (known structure)    │ (unknown structure)  │
                    │                      │                      │
  Pre-processing:   │ arXiv-specific:      │ Security-focused:    │
                    │ - strip <figure>     │ - strip <script>,    │
                    │   tags (fix tables)  │   <style>, <iframe>  │
                    │ - strip LaTeXML CSS  │ - strip CSS-hidden   │
                    │   transform wrappers │   elements           │
                    │                      │ - strip zero-width   │
                    │                      │   Unicode chars      │
                    │                      │                      │
  Primary tool:     │ Pandoc (structural   │ trafilatura (article │
                    │ converter — works    │ extractor — handles  │
                    │ well on known HTML)  │ arbitrary layouts)   │
                    │                      │                      │
  Fallback:         │ (none — falls        │ Pandoc (same flags   │
                    │  through to full     │ as arXiv path, but   │
                    │  PDF pipeline)       │ no pre/post-process) │
                    │                      │                      │
  Post-processing:  │ arXiv-specific:      │ (none — trafilatura  │
                    │ - strip \hspace{0pt} │  handles cleanup)    │
                    │ - strip LaTeXML      │                      │
                    │   comment artifacts  │                      │
                    │                      │                      │
  Output metadata:  │ None (raw markdown   │ YAML frontmatter:    │
                    │ returned as          │ source_url, title,   │
                    │ PipelineResult)      │ author, content_hash │
                    │                      │ access_date          │
                    │                      │                      │
  Output type:      │ PipelineResult       │ ExtractionResult     │
                    │ (internal to PDF     │ (CLI-level result)   │
                    │  pipeline)           │                      │
                    └──────────────────────┴──────────────────────┘

  Shared between both: Pandoc invocation flags (identical):
    pandoc -f html-native_divs-native_spans
           -t markdown-header_attributes
           --wrap=none --markdown-headings=atx
    (web_backend.py:167 has a sync comment pointing to pandoc_convert.py:178-186)
```

**Why the split is justified:** arXiv LaTeXML HTML has a predictable, consistent
structure where Pandoc excels — the pre/post-processing targets specific LaTeXML
artifacts (`<figure>` wrapping, `\hspace{0pt}`, CSS transform spans). General
web pages are wildly varied, so trafilatura (purpose-built for article extraction
from messy HTML) is the right primary tool, with Pandoc as a degraded fallback.
Merging them would either compromise arXiv quality or add unnecessary complexity
to the general path.

### Module Reuse Map

```
┌──────────────────────────────────────────────────────────────────────┐
│                         SHARED MODULES                               │
│                                                                      │
│  http.py ──────────────── fetch_url(), head_content_type()           │
│  │                        USER_AGENT constant                        │
│  │  Used by: web_backend.py, pandoc_convert.py, extract_cli.py      │
│  │                                                                   │
│  base.py ──────────────── ExtractionResult, sanitize_filename()      │
│  │                        get_output_dir(), write_summary()          │
│  │  Used by: ALL pipelines                                           │
│  │                                                                   │
│  metrics.py ─────────────  compute_metrics(), ExtractionMetrics      │
│  │  Used by: PDF pipeline (pipeline.py), web_backend.py              │
│  │                                                                   │
│  html_sanitize.py ─────── strip_hidden_content()                     │
│  │  Used by: web_backend.py only                                     │
│  │                                                                   │
│  Pandoc flags ─────────── Identical flags used in two places:        │
│     pandoc_convert.py:176-184  (arXiv shortcut)                      │
│     web_backend.py:169-178     (general web fallback)                │
│     (linked by sync comment at web_backend.py:167)                   │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐  ┌───────────────────┐  ┌────────────────┐
│     PDF PIPELINE         │  │   DOCX BACKENDS   │  │  WEB BACKEND   │
│                          │  │                   │  │                │
│ pipeline.py              │  │ docling_backend   │  │ web_backend.py │
│  └─ extract_pdf()        │  │ pandoc_backend    │  │  └─ extract_   │
│     ├─ pandoc_convert    │  │ pymupdf_backend   │  │     web_       │
│     │  (arXiv shortcut   │  │                   │  │     content()  │
│     │   FETCHES HTML     │  │                   │  │                │
│     │   from arxiv.org!) │  │                   │  │ ┌─ trafilatura │
│     ├─ pymupdf_backend   │  │                   │  │ │  (primary)   │
│     │  (base extraction) │  │                   │  │ └─ _fallback_  │
│     ├─ tables.py         │  │                   │  │    pandoc()    │
│     │  (ensemble detect) │  │                   │  │    (secondary) │
│     ├─ equations.py      │  │                   │  │                │
│     ├─ quality_gate.py   │  │                   │  │ html_sanitize  │
│     ├─ claude_enhance    │  │                   │  │  (pre-pass)    │
│     └─ postprocess.py    │  │                   │  │                │
└──────────────────────────┘  └───────────────────┘  └────────────────┘
```

### Entry Points Summary

| # | Entry Point | Trigger | Code Location |
|---|-------------|---------|---------------|
| 1 | **Single URL** | `extract https://...` | `extract_cli.py:385-386` → `_extract_url()` |
| 2 | **Batch URLs** | `extract --urls-from file.txt` | `extract_cli.py:381-382` → `_extract_urls_from_file()` |
| 3 | **Single file** | `extract paper.pdf` or `extract doc.docx` | `extract_cli.py:400` → `discover_documents()` → loop |
| 4 | **Directory** | `extract papers/` | `extract_cli.py:400` → `discover_documents()` → loop |
| 5 | **Check mode** | `extract --check [paper.pdf]` | `extract_cli.py:339-377,405-438` (diagnostic, no extraction) |

Note: Entry points 1 and 2 (URL paths) can **feed into** the PDF pipeline. When
`classify_url()` returns `"pdf"`, `_extract_pdf_url()` downloads the PDF to a
temp file and re-enters `cmd_extract()`, which runs the full PDF pipeline
(including the arXiv shortcut at Step 1).

### Outputs Per Pipeline

```
PDF Pipeline Output (per document):
  output_dir/
  ├── output.md          ← final merged markdown
  ├── metrics.json       ← char count, headings, table rows, timing
  ├── decisions.json     ← per-page routing decisions (KEEP/CLAUDE_REPLACE/etc.)
  ├── cost.json          ← Claude API cost records (if budget > 0)
  ├── profile.json       ← per-step timing (if --profile)
  └── images/
      ├── page_NNN_*.png ← extracted figures from pymupdf
      ├── page_NNN_table_N.png  ← table crop images
      └── page_NNN_eq_N.png     ← equation crop images

  NOTE: When the arXiv shortcut fires (Step 1 early return), only output.md
  and metrics.json are written. No decisions.json, cost.json, or images/
  because steps 2-8 are skipped entirely.

DOCX Backend Output (per document):
  output_dir/
  ├── output.md          ← converted markdown
  ├── summary.json       ← source hash, backend, stats, processing status
  └── images/            ← extracted images (if docling backend)

Web Backend Output (per URL):
  output_dir/
  ├── {title}.md         ← markdown with YAML frontmatter (auto-dir mode)
  │   OR output.md       ← (when --output dir provided)
  ├── metrics.json       ← char count, headings, timing
  └── raw.html           ← original fetched HTML (only if --raw-html)

Check Mode Output:
  (stdout only — no files written)
  ├── Table: component status (pymupdf, gmft, Claude, equations)
  └── JSON: machine-readable status (if --check-json)
```

### All Web Fetches in the Codebase

Three distinct places perform HTTP fetches during extraction:

| Fetch | Module | What's fetched | Raw saved? |
|-------|--------|----------------|------------|
| Web backend: page fetch | `http.py:30` via `web_backend.py:225` | Arbitrary HTML page | Yes, if `--raw-html` |
| arXiv shortcut: HTML fetch | `pandoc_convert.py:158-161` | arXiv LaTeXML HTML | No (temp file deleted) |
| PDF URL download | `http.py:30` via `extract_cli.py:254` | PDF binary | No (temp file deleted) |

Note: `pandoc_convert.py` uses `urllib.request` directly rather than the shared
`fetch_url()` from `http.py` — it only imports the `USER_AGENT` constant. This
is a minor inconsistency but doesn't cause issues since the arXiv fetch is simple
(no redirect tracking or charset detection needed).

## B) Raw Source Saving: When and How

### Web Extraction: `--raw-html` flag

**Yes**, the web backend supports saving the original fetched HTML.

- **Flag**: `--raw-html` CLI argument (`extract_cli.py:744-747`)
- **Implementation**: `web_backend.py:314-315`
- **What's saved**: The **pre-sanitization** HTML (`fetched.text()`) — this is the raw HTTP response body decoded to string
- **Where**: `output_dir/raw.html`
- **When**: Only when explicitly requested via `--raw-html`
- **Default**: Off (raw HTML is not saved)

```python
# web_backend.py:314-315
if save_raw_html:
    (output_dir / "raw.html").write_text(fetched.text(), encoding="utf-8")
```

The `fetched.text()` call returns the original bytes decoded with the server-provided charset (or UTF-8 fallback). This is called on the original `FetchResult` object, so it returns the **unsanitized** HTML even though the sanitized version was used for extraction.

### PDF URL Downloads: No raw save

When a URL is classified as PDF (`_extract_pdf_url()`, `extract_cli.py:245-270`):
1. The PDF is downloaded via `fetch_url()` from `http.py`
2. Written to a `tempfile.NamedTemporaryFile`
3. A shallow copy of args is created with `path` pointing to the temp file
4. **`cmd_extract()` is re-entered** — the temp file goes through the full PDF pipeline (including the arXiv shortcut, quality gates, Claude enhancement, etc.)
5. The temp file is **deleted** in the `finally` block

There is **no option** to preserve the downloaded PDF. The pipeline writes its derived outputs (output.md, metrics.json, etc.) but the original PDF bytes are discarded.

### arXiv HTML Shortcut: No raw save

When the PDF pipeline's Step 1 detects an arXiv paper (`pipeline.py:171-207` → `pandoc_convert.py:132-204`):
1. `detect_arxiv_id()` extracts the arXiv ID from PDF page 1 text or metadata
2. `check_arxiv_html()` sends a HEAD request to `arxiv.org/html/{id}`
3. `convert_arxiv_html()` fetches the full HTML, pre-processes (strip LaTeXML artifacts), writes to a temp file, runs Pandoc, post-processes, **deletes temp file**
4. Pipeline returns immediately with `source="pandoc_arxiv"` — steps 2-8 are skipped

No raw HTML is preserved. The `--html-path` flag can supply a local HTML file instead of fetching, but the fetched-from-network case has no save option.

### DOCX Extraction: No raw save

DOCX files are processed in-place from their original location. The original file is never copied or moved — it stays where the user put it.

### Summary Table

| Pipeline | Saves raw source? | How | Flag |
|----------|-------------------|-----|------|
| Web → HTML | Yes | `raw.html` in output dir | `--raw-html` |
| Web → PDF URL | No | Temp file deleted after extraction | — |
| PDF (local file) | No | Reads from original path | — |
| PDF → arXiv shortcut | No | Fetched HTML → temp file → deleted after Pandoc | — |
| DOCX | No | Reads from original path | — |

## C) YAML Frontmatter: When, How, and Why

### Current State

Only **one** of the three extraction pipelines embeds YAML frontmatter in the
output markdown. The others store metadata in sidecar JSON files:

```
                 Metadata in markdown?     Metadata in sidecar files?
                 ────────────────────      ─────────────────────────
Web backend      YES — YAML frontmatter   metrics.json
PDF pipeline     NO                        metrics.json, decisions.json, cost.json
DOCX backends    NO                        summary.json
INDEX.md         YES — YAML frontmatter   (is itself a sidecar)
```

### Web Backend Frontmatter (the only one)

Built by `_build_frontmatter()` at `web_backend.py:92-111`, prepended to the
markdown at `web_backend.py:284`:

```yaml
---
source_url: "https://en.wikipedia.org/wiki/Fusion_energy"
access_date: "2026-03-28T18:30:00+00:00"
content_hash_sha256: "a1b2c3..."
title: "Fusion energy"
author: "Wikipedia contributors"
extraction_tool: "trafilatura 2.1.0"
---
```

**Fields:**
| Field | Source | Always present? |
|-------|--------|-----------------|
| `source_url` | `FetchResult.final_url` (after redirects) | Yes |
| `access_date` | `datetime.now(timezone.utc)` | Yes |
| `content_hash_sha256` | SHA-256 of extracted markdown (not raw HTML) | Yes |
| `title` | trafilatura metadata | Only if trafilatura finds one |
| `author` | trafilatura metadata | Only if trafilatura finds one |
| `extraction_tool` | `trafilatura.__version__` or `"pandoc (fallback)"` | Yes |

**Why it was added here:** The web backend was designed for research source
capture where provenance is critical — you need to know where the content came
from, when it was fetched, and whether it's changed. The frontmatter embeds this
directly in the markdown so it travels with the content if the file is moved or
the sidecar files are lost.

### PDF Pipeline: Metadata in Sidecar Files Only

`extract_pdf()` returns a `PipelineResult` with `markdown` as a plain string.
The CLI writes it directly to `output.md` with no frontmatter:

```python
# extract_cli.py:485
(output_dir / "output.md").write_text(result.markdown)
```

Metadata is spread across sidecar files:
- **`metrics.json`** — char count, headings, table rows, extraction time
- **`decisions.json`** — per-page routing (KEEP, CLAUDE_REPLACE, GMFT_REPLACE, etc.)
- **`cost.json`** — Claude API cost records (pages enhanced, tokens, dollars)
- **`profile.json`** — per-step timing breakdown (if `--profile`)

There is no `source_url` or `access_date` because PDFs are local files — the
user already knows where they came from. The `summary.json` written by DOCX
backends includes `file_hash` for change detection, but the PDF pipeline doesn't
write `summary.json` (it uses the existence of `output.md` as its skip check).

### DOCX Backends: Metadata in `summary.json`

`write_summary()` at `base.py:105-131` writes a JSON sidecar:

```json
{
  "source_file": "document.docx",
  "source_format": "docx",
  "processed_at": "2026-03-28T18:30:00+00:00",
  "backend_used": "docling",
  "processing_completed": true,
  "file_hash": "md5:abc123...",
  "statistics": { "total_images": 5, "total_characters": 42000, "file_size_bytes": 1024000 }
}
```

No frontmatter in the markdown output.

### INDEX.md: Has Its Own Frontmatter

The optional `--index` post-step generates `INDEX.md` with frontmatter
(`index.py:266-281`):

```yaml
---
document: paper_name
generated: 2026-03-28T18:30:00
source_checksum: sha256:abc123...
total_lines: 5000
depth: 3
section_count: 42
---
```

This is a structural index, not source metadata — different purpose.

### Is There a Good Reason to Not Always Add Frontmatter?

**Arguments for keeping the current inconsistency:**

1. **PDF/DOCX are local files — provenance is obvious.** You have the source
   file sitting right there. Adding `source_file: paper.pdf` to the markdown
   is redundant with the directory structure (`paper/output.md` ← from
   `paper.pdf`).

2. **PDF pipeline markdown is intermediate, not archival.** It's a working
   extraction meant to be consumed by downstream tools (LLM context, search
   indexes). YAML frontmatter can confuse naive markdown parsers, corrupt
   copy-paste into LLM prompts, or interfere with heading detection.

3. **The sidecar pattern is already established.** `metrics.json`,
   `decisions.json`, `cost.json` already contain structured metadata that's
   easier to parse programmatically than YAML-in-markdown. Adding frontmatter
   would duplicate data that's already in sidecars.

4. **Web content is ephemeral — PDFs aren't.** A web page can change or
   disappear tomorrow; the `source_url` and `access_date` frontmatter records
   a snapshot in time. A PDF sitting on your disk won't change unless you
   replace it (and `file_hash` catches that).

**Arguments for adding frontmatter everywhere:**

1. **Consistency.** All extraction outputs should be self-describing. If you
   move `output.md` away from its sidecar files, you lose all context about
   what produced it, when, and from what source.

2. **LLM consumption.** When feeding extracted markdown to an LLM as context,
   frontmatter tells the LLM what it's reading — source, date, extraction
   quality. This is valuable for research workflows where multiple sources
   are combined.

3. **The PDF URL and arXiv paths DO fetch from the web** but produce no
   provenance record in the markdown. If you extract a PDF from a URL, the
   output.md has no record of where it came from (the temp file is deleted,
   and no summary.json is written for PDFs).

4. **The sidecar files are fragile.** Directory moves, partial copies, or
   cleanup scripts can separate `output.md` from its `metrics.json`. Frontmatter
   survives because it's part of the content.

**Assessment:**

The current split is *defensible* but there's a real gap for the **PDF-from-URL**
and **arXiv shortcut** paths — these fetch content from the web but produce
`output.md` with no provenance at all. At minimum, those two paths should record
`source_url` and `access_date` somewhere.

For local PDF/DOCX, the case is weaker — the source file is right there.
But a lightweight frontmatter block (just `source_file`, `extracted_at`,
`backend`) would make every `output.md` self-describing without much cost.

### Summary Table

| Pipeline | Frontmatter? | Metadata location | Provenance gap? |
|----------|-------------|-------------------|-----------------|
| Web → HTML | Yes (6 fields) | In markdown + metrics.json | No |
| Web → PDF URL | No | metrics.json, decisions.json (no source_url) | **Yes** — no record of source URL |
| PDF (local) | No | metrics.json, decisions.json | Minor — source file is local |
| PDF → arXiv shortcut | No | metrics.json only (no decisions/cost) | **Yes** — no record of arxiv.org URL |
| DOCX (local) | No | summary.json | Minor — source file is local |
| INDEX.md | Yes (structural) | In the index file itself | N/A (different purpose) |

## Code References

- `extract_cli.py:309` — `cmd_extract()` main handler with dispatch logic
- `extract_cli.py:196` — `_extract_url()` URL dispatch
- `extract_cli.py:245` — `_extract_pdf_url()` PDF download + re-entry into `cmd_extract()`
- `extract_cli.py:273` — `_extract_urls_from_file()` batch mode
- `web_backend.py:193` — `extract_web_content()` main web pipeline
- `web_backend.py:114` — `_extract_with_trafilatura()` primary HTML extractor
- `web_backend.py:155` — `_fallback_pandoc()` secondary HTML extractor (same Pandoc flags)
- `web_backend.py:314-315` — raw HTML save logic
- `web_backend.py:65` — `classify_url()` HEAD-based content type routing
- `pipeline.py:331` — `extract_pdf()` 8-step PDF pipeline
- `pipeline.py:171` — `_try_arxiv_shortcut()` Step 1 early return (fetches HTML!)
- `pipeline.py:357-367` — Step 1 invocation and early return check
- `pandoc_convert.py:71` — `detect_arxiv_id()` PDF metadata scan
- `pandoc_convert.py:113` — `check_arxiv_html()` HEAD check for HTML availability
- `pandoc_convert.py:132` — `convert_arxiv_html()` fetch + preprocess + Pandoc + postprocess
- `pandoc_convert.py:33` — `_preprocess_html()` arXiv-specific HTML cleanup
- `pandoc_convert.py:54` — `_postprocess_markdown()` arXiv-specific markdown cleanup
- `http.py:30` — `fetch_url()` shared HTTP fetch
- `http.py:56` — `head_content_type()` shared HEAD check
- `base.py:17` — `ExtractionResult` shared result type
- `metrics.py` — `compute_metrics()` shared metrics computation

## Recommendations

### Provenance gaps (highest value)

1. **PDF-from-URL path has no provenance.** `_extract_pdf_url()` downloads a PDF, runs the pipeline, deletes the temp file. The resulting `output.md` has no record of where it came from. At minimum, the source URL should be recorded — either as YAML frontmatter in `output.md` or in a sidecar file (e.g., `source.json`).

2. **arXiv shortcut has no provenance.** When `_try_arxiv_shortcut()` succeeds, the `PipelineResult` has `source="pandoc_arxiv"` but no URL. The CLI writes `output.md` and `metrics.json` with no trace of which arXiv ID or URL was used. Recording `arxiv_id` and `html_url` would make these outputs self-describing.

### Raw source saving

3. **Consider `--save-source` for URL paths.** The PDF URL path could copy downloaded bytes into the output dir before deleting the temp file. Small change in `_extract_pdf_url()`.

4. **Thread `--raw-html` to arXiv shortcut.** The raw LaTeXML HTML could be preserved if the flag were plumbed through `PipelineConfig` → `_try_arxiv_shortcut()` → `convert_arxiv_html()`.

### Frontmatter consistency

5. **Lightweight frontmatter for all outputs would be low-cost and high-value.** A minimal block (`source`, `extracted_at`, `backend`) on every `output.md` would make all extraction outputs self-describing without breaking downstream consumers. The web backend's richer frontmatter (with `content_hash`, `author`, etc.) could remain web-only.

6. **If adding universal frontmatter, keep it optional.** A `--no-frontmatter` flag would let users who feed output.md into frontmatter-sensitive tools opt out.

### Minor inconsistencies

7. `pandoc_convert.py` does its own `urllib.request` fetch rather than using `fetch_url()` from `http.py` — it only imports `USER_AGENT`. Low priority but could be unified if `http.py` grows retry/logging features.

8. PDF pipeline doesn't write `summary.json` (uses `output.md` existence as skip check). DOCX backends do. This means PDF outputs lack the `file_hash` change-detection that DOCX outputs have.
