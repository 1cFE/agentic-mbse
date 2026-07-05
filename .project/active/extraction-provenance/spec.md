# Spec: Extraction Provenance & Raw Source Saving

**Status:** Implemented
**Owner:** Reid W
**Created:** 2026-03-28 17:50 PDT
**Complexity:** MEDIUM
**Branch:** webfetch-tools

---

## Business Goals

### Why This Matters

Every extraction output should be self-describing. Today, only the web backend embeds provenance metadata (YAML frontmatter) in its markdown output. PDF and DOCX pipelines write plain markdown and rely on sidecar JSON files (`metrics.json`, `summary.json`) that can get separated from `output.md` during moves, copies, or LLM context assembly.

Worse, two extraction paths fetch content from the network — PDF URL downloads and the arXiv HTML shortcut — but discard the fetched artifacts after conversion with no option to preserve them and no record of the source URL in the output.

Making all extraction outputs self-describing and all fetched sources preservable closes these gaps with minimal disruption to the existing architecture.

### Success Criteria

- [ ] Any `output.md` from any extraction path tells you what it came from, when it was extracted, and what tool produced it — without needing sidecar files
- [ ] Fetched-from-network content (PDF URLs, arXiv HTML, web HTML) can be preserved locally via a flag
- [ ] Existing workflows that consume plain markdown can opt out of frontmatter

### Priority

P2 — Quality-of-life improvement that builds on the just-shipped web source capture feature. No external blockers.

---

## Problem Statement

### Current State

The three extraction pipelines handle provenance inconsistently:

| Pipeline | Frontmatter in markdown? | Source URL recorded? | Raw source preservable? |
|----------|-------------------------|---------------------|------------------------|
| Web → HTML | Yes (6 fields) | Yes | Yes (`--raw-html`) |
| Web → PDF URL | No | No | No (temp file deleted) |
| PDF (local) | No | N/A (local file) | N/A (user has it) |
| PDF → arXiv shortcut | No | No | No (temp file deleted) |
| DOCX (local) | No | N/A (local file) | N/A (user has it) |

The web backend's `_build_frontmatter()` is local to `web_backend.py` and not reusable by other pipelines. The `--raw-html` flag only applies to the web HTML path.

### Desired Outcome

All extraction paths produce markdown with YAML frontmatter by default, using a common field set. A single flag enables saving raw source artifacts for any path that fetches from the network. Users who want clean markdown can opt out of frontmatter.

---

## Scope

### In Scope

- Universal YAML frontmatter on all extraction output markdown (default on)
- `--no-frontmatter` opt-out flag
- A flag to save raw source artifacts for all network-fetched content
- Shared frontmatter builder usable by all pipelines
- Updating the web backend to use the shared builder (not its own copy)

### Out of Scope

- Changes to extraction logic (quality gates, backends, sanitization, table detection)
- Changes to sidecar JSON files (they continue to exist; frontmatter supplements, doesn't replace)
- Saving copies of local PDF/DOCX files (the user already has them on disk)
- Changes to `--check` mode (diagnostic, produces no output markdown)
- Changes to INDEX.md frontmatter (different purpose — structural index)

### Edge Cases & Considerations

- **arXiv shortcut early return**: `extract_pdf()` returns a `PipelineResult` — frontmatter must be added either inside the pipeline or at the CLI write site (`extract_cli.py:485`). Design should decide which.
- **PDF-from-URL re-entry**: `_extract_pdf_url()` re-enters `cmd_extract()` with a temp file path. The source URL context is lost at re-entry. Need to thread source URL through somehow (args attribute, or save before re-entry).
- **Existing web backend frontmatter**: Already has `_build_frontmatter()` with web-specific fields. Must migrate to shared builder without breaking existing output format.
- **`content_hash` semantics change**: Web backend currently hashes extracted markdown. This spec changes it to hash the original source for change detection. The web backend's existing behavior changes — this is intentional.

---

## Requirements

### Functional Requirements

> Requirements are from user's request unless marked [INFERRED].

**YAML Frontmatter**

1. **FR-1**: All extraction output markdown MUST include YAML frontmatter by default, using a common field set across all pipelines.

2. **FR-2**: The common frontmatter field set MUST include:
   - `source` — source identifier: URL (after redirects) for network-fetched content, or local file path for local files
   - `source_type` — one of: `url`, `local_file`
   - `extracted_at` — ISO 8601 UTC timestamp of when extraction ran
   - `content_hash_sha256` — SHA-256 hash of the **original source content** (raw HTML bytes, PDF bytes, DOCX bytes) for change detection
   - `backend` — extraction backend/pipeline that produced the output (e.g., `trafilatura`, `pandoc-fallback`, `pdf_pipeline`, `pandoc_arxiv`, `docling`, `pandoc`)

3. **FR-3**: The web backend MAY include additional fields beyond the common set:
   - `title` — page title (from trafilatura metadata, if available)
   - `author` — author name (from trafilatura metadata, if available)

4. **FR-4**: A `--no-frontmatter` CLI flag MUST be supported to suppress frontmatter on all extraction output. When set, output markdown MUST be identical to what the pipelines produce today (plain markdown, no `---` block).

5. **FR-5**: A shared frontmatter builder function MUST be created in a common location (e.g., `base.py` or a new `frontmatter.py`) and used by all pipelines. The web backend's existing `_build_frontmatter()` MUST be replaced by the shared version.

6. **FR-6**: [INFERRED] For local files where `source_type` is `local_file`, the `source` field SHOULD contain the original filename (not a full absolute path, to avoid leaking filesystem structure).

**Raw Source Saving**

7. **FR-7**: A CLI flag MUST be supported to save raw source artifacts locally for all extraction paths that fetch content from the network. The saved artifact is the original fetched bytes before any transformation.

8. **FR-8**: When raw source saving is enabled, the following artifacts MUST be saved in the output directory:

   | Extraction path | Saved artifact | Filename |
   |----------------|---------------|----------|
   | Web → HTML | Raw fetched HTML (pre-sanitization) | `raw.html` |
   | Web → PDF URL | Downloaded PDF bytes | `raw.pdf` |
   | PDF → arXiv shortcut | Fetched arXiv LaTeXML HTML | `raw.html` |

9. **FR-9**: Raw source saving MUST NOT apply to local file extraction (PDF from disk, DOCX from disk) — the user already has the source.

10. **FR-10**: The existing `--raw-html` flag's relationship to the new flag MUST be resolved. Two options (defer final decision to design):
    - **Option A (preferred — simplicity):** Replace `--raw-html` with a single `--save-source` flag that covers all network-fetched content. Deprecate `--raw-html` with a warning pointing to `--save-source`.
    - **Option B:** Keep `--raw-html` for web-only HTML saving, add `--save-source` as a superset that also covers PDF URL downloads and arXiv HTML. `--raw-html` becomes an alias or subset.

**Content Hash Semantics**

11. **FR-11**: The `content_hash_sha256` frontmatter field MUST hash the **original source content** (the bytes that were fetched or read), not the extracted markdown. This enables change detection: if the source changes, the hash changes, signaling that re-extraction may be needed.

12. **FR-12**: [INFERRED] For each source type, the hash input MUST be:

    | Source | Hash input |
    |--------|-----------|
    | Web HTML | Raw fetched HTML bytes (pre-sanitization) |
    | Web → PDF URL | Downloaded PDF bytes |
    | PDF (local) | PDF file bytes on disk |
    | PDF → arXiv shortcut | Fetched arXiv HTML bytes |
    | DOCX (local) | DOCX file bytes on disk |

    Note: This aligns with the existing `file_hash` in DOCX's `summary.json` (which hashes the source file), but changes the web backend's current behavior (which hashes extracted markdown).

### Non-Functional Requirements

13. **NFR-1**: Existing extraction behavior MUST NOT change when `--no-frontmatter` is used — output is byte-identical to current behavior.

14. **NFR-2**: All existing tests MUST continue to pass. Tests that assert on `output.md` content will need updating to account for frontmatter (or use `--no-frontmatter`).

15. **NFR-3**: The shared frontmatter builder MUST NOT introduce new dependencies beyond what's already available in each pipeline's context.

---

## Acceptance Criteria

### Frontmatter

- [ ] `uv run agentic-mbse extract paper.pdf` produces `output.md` with YAML frontmatter containing `source`, `source_type: local_file`, `extracted_at`, `content_hash_sha256`, and `backend`
- [ ] `uv run agentic-mbse extract doc.docx` produces `output.md` with the same common frontmatter fields
- [ ] `uv run agentic-mbse extract https://example.com` produces markdown with common fields plus `title` and `author` (if available)
- [ ] `uv run agentic-mbse extract --no-frontmatter paper.pdf` produces plain markdown with no `---` block (identical to current behavior)
- [ ] An arXiv paper extracted via the PDF pipeline's shortcut has frontmatter with `source` set to the arxiv.org HTML URL and `backend: pandoc_arxiv`
- [ ] A PDF extracted from a URL has frontmatter with `source` set to the original URL and `backend: pdf_pipeline`

### Raw Source Saving

- [ ] `uv run agentic-mbse extract --save-source https://example.com` (or equivalent flag per design) saves `raw.html` in the output directory
- [ ] `uv run agentic-mbse extract --save-source https://arxiv.org/pdf/2411.06644` saves `raw.pdf` in the output directory
- [ ] An arXiv paper that triggers the HTML shortcut with `--save-source` saves `raw.html` (the fetched LaTeXML HTML)
- [ ] `--save-source` on a local PDF does NOT save a copy (the user already has it)
- [ ] `--raw-html` is either deprecated with a warning or aliased (per design decision)

### Content Hash

- [ ] `content_hash_sha256` for a local PDF matches `sha256(pdf_file_bytes)`
- [ ] `content_hash_sha256` for a web page matches `sha256(raw_fetched_html_bytes)`, NOT `sha256(extracted_markdown)`
- [ ] Re-extracting an unchanged source produces the same `content_hash_sha256`

### Quality & Integration

- [ ] All existing tests pass (`uv run pytest tests/`)
- [ ] Shared frontmatter builder has unit tests
- [ ] `--no-frontmatter` has a test confirming no `---` in output
- [ ] `--save-source` has tests for each network-fetch path (mocked HTTP)

---

## Related Artifacts

- **Research:** `.project/research/20260328-extraction-architecture-map.md` (sections B and C)
- **Predecessor:** `.project/active/web-source-capture/spec.md` (FR-5, FR-9 — web-only frontmatter and `--raw-html`)
- **Design:** `.project/active/extraction-provenance/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
