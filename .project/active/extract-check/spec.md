# Spec: `agentic-mbse extract --check` — Pipeline Component Verification

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-02-27 10:45
**Complexity:** MEDIUM
**Branch:** doc-ingest-clean
**Parent:** EPIC-PDFV4-001

---

## Business Goals

### Why This Matters

The PDF extraction pipeline has 6 optional components (Claude, GMFT, Img2Table, Docling, Pandoc, pymupdf4llm). Each degrades gracefully when missing or broken — the pipeline always produces output. This robustness becomes an observability blind spot: a user can run a full extraction batch, see `ok` with `$0.00` cost, and have no idea they're getting degraded output because Claude silently failed on every page.

The trigger for this spec: Claude Code's `--output-format json` changed from returning a single JSON object to a JSON array. `invoke_claude()` parsed it incorrectly, threw `AttributeError`, which was caught by a broad `except Exception` at `debug` log level. Every Claude call failed silently. The quality gate correctly identified pages needing Claude, allocated budget, and the pipeline reported `claude_replace` decisions — but no Claude enhancement actually happened. The user saw `ok` and moved on. This cost hours of wasted time extracting documents at degraded quality.

This is not just about the Claude bug (which will be fixed separately). Any optional component can break in ways that import checks and `shutil.which` can't catch: wrong library version, missing GPU drivers, network issues, auth failures, format changes. The only way to know it works is to run it.

### Success Criteria

- [ ] A user can run `agentic-mbse extract --check <pdf>` before a batch and know exactly which components are working
- [ ] A broken Claude invocation (like the JSONL bug) is caught by `--check` before wasting time on a full extraction
- [ ] The check reports what quality level to expect ("tables will not be enhanced", "math-heavy pages will not be re-extracted") given the available components
- [ ] Machine-readable output (JSON) enables CI integration for environments where extraction quality matters

### Priority

High. This is directly motivated by a real user-facing failure in the active PDF pipeline work. Should be implemented alongside or immediately after the `invoke_claude()` fix (`.project/active/v4-claude-invocation-and-logging/design.md`).

---

## Problem Statement

### Current State

- `_is_available()` in `extract_cli.py` checks pymupdf4llm/docling/pandoc for DOCX backend selection — import checks only
- `tables.py` catches `ImportError` on GMFT/Img2Table and returns empty results silently
- `pandoc_convert.py` checks `shutil.which("pandoc")`
- Claude has zero pre-flight check — `invoke_claude()` calls `subprocess.run(["claude", ...])` and catches failure at `debug` level
- `--dry-run` only skips Claude calls — it doesn't verify any component works
- No centralized health check, no status report, no smoke test

### Desired Outcome

A single command that probes every pipeline component against a real PDF and reports pass/fail with actionable detail. Catches not just "is it installed?" but "does it actually work end-to-end?"

---

## Scope

### In Scope

- `--check` flag on the `extract` subcommand
- Probing all 6 pipeline components with real invocations (not just import checks)
- Intelligent page selection from the user's PDF to exercise each component
- Human-readable table output to stdout
- Machine-readable JSON output option
- Quality impact summary ("what you'll get" given available components)

### Out of Scope

- Auto-installation or auto-fix of broken components (diagnosis only)
- A separate top-level `agentic-mbse doctor` command (may be added later, but `--check` on `extract` is the right first step — it uses the actual document)
- Continuous monitoring or watch mode
- Performance benchmarking (only functional verification)

### Edge Cases & Considerations

- User provides a 1-page PDF with no tables and no math — some components can't be exercised. Report "untested" vs "pass" vs "fail".
- User has no PDF at all — should `--check` work without a PDF for basic import/binary checks?
- GMFT/Img2Table require page images which require pymupdf — if pymupdf is broken, table detectors can't be tested.
- Claude smoke test costs real money (~$0.001). This MUST be clearly communicated.
- Network-dependent checks (Claude, arXiv HTML fetch) may fail due to network, not component issues.

---

## Requirements

### Functional Requirements

#### FR-1: Page Selection from User's PDF

The check command MUST accept a PDF path and select 1–3 pages that collectively exercise the pipeline's key capabilities. Selection criteria:

- **A page with math content** — detected via Unicode math symbol density or `~~strikethrough~~` garbling in pymupdf4llm output. Exercises: Claude page enhancement, quality gate math detection.
- **A page with tables** — detected via pipe table markers (`|`) or GMFT detection. Exercises: GMFT, Img2Table, table filtering, Claude table enhancement.
- **Page 1** — always included. Exercises: arXiv ID detection, base extraction, heading detection.

If the PDF lacks math or tables, the check MUST report which component categories could not be exercised ("no math pages found — Claude equation enhancement untested").

Page selection MUST use only fast operations (pymupdf4llm extraction + heuristic scanning), not Claude or GMFT, to avoid circular dependencies.

#### FR-2: Component Probes

Each component MUST be tested with a real invocation, not just an import or binary check. The check MUST probe these components in dependency order:

| # | Component | Probe | Pass Condition |
|---|-----------|-------|----------------|
| 1 | **pymupdf4llm** | Extract selected pages | Returns non-empty markdown for each page |
| 2 | **GMFT** | Run `_detect_gmft()` on the table page (if found) | Returns without error (0 tables is OK — it means the page had no GMFT-detectable tables, not that GMFT is broken). If no table page found, test against any page. |
| 3 | **Img2Table** | Run `_detect_img2table()` on the same page | Returns without error |
| 4 | **Docling** | [INFERRED] Run Docling table detection on one page if installed | Returns without error |
| 5 | **Pandoc** | Check binary availability AND, if page 1 has arXiv ID, download arXiv HTML and run full Pandoc conversion to markdown | Binary exists. If arXiv: HTML downloaded, converted via Pandoc, non-empty markdown produced. |
| 6 | **Claude** | Run `invoke_claude()` with a minimal prompt (~10 tokens) against one selected page image | Returns a parseable response with `result` field and `total_cost_usd` > 0 |

Components MUST be tested independently where possible. A GMFT failure MUST NOT prevent the Claude check from running.

When a component is not installed (ImportError, binary missing), the probe MUST report `not installed` distinctly from `installed but broken`.

#### FR-3: Claude Smoke Test

The Claude probe MUST actually invoke Claude, not just check for the binary. This is the critical requirement — the JSONL bug would have been caught by any real invocation.

The probe MUST:
- Render one page as an image (reuse `render_page_image()`)
- Call `invoke_claude()` with a short extraction prompt
- Parse the response (exercising the JSON parsing path)
- Report: model used, response received, cost incurred, parse success

The probe SHOULD use the cheapest available model (haiku) to minimize cost.

The check MUST clearly communicate to the user that the Claude probe costs a small amount (~$0.001–$0.01) before running it. If `--budget 0` is also passed, the Claude probe MUST be skipped with a note explaining why.

#### FR-4: Human-Readable Output

The default output MUST be a clear table to stdout:

```
Pipeline component check for: paper.pdf (14 pages)
Selected pages: 1 (headings), 4 (math+equations), 7 (tables)

  Component     Status       Detail
  ─────────     ──────       ──────
  pymupdf4llm   pass         3 pages extracted (1847 chars avg)
  GMFT          pass         2 tables detected on page 7
  Img2Table     pass         0 additional tables (page 7)
  Docling       not installed
  Pandoc        pass         binary found, arXiv ID detected (2401.12345)
  Claude        pass         haiku responded, 43 tokens, $0.002

Expected quality with current setup:
  ✓ Base text extraction
  ✓ Table detection and enhancement (GMFT + Img2Table)
  ✓ Math/equation re-extraction (Claude)
  ✓ arXiv HTML shortcut (Pandoc + arXiv ID found)
  ✗ Third-pass table detection (Docling not installed)
```

When a component fails, the detail MUST include the error message (truncated if long), not just "fail":

```
  Claude        FAIL         invoke_claude() raised: AttributeError: 'list' object has no attribute 'get'
```

#### FR-5: Machine-Readable JSON Output

When `--json` is passed (or combined as `--check --json`), the check MUST output a JSON object to stdout:

```json
{
  "pdf": "paper.pdf",
  "pages": 14,
  "selected_pages": {"headings": 1, "math": 4, "tables": 7},
  "components": {
    "pymupdf4llm": {"status": "pass", "detail": "3 pages extracted (1847 chars avg)"},
    "gmft": {"status": "pass", "detail": "2 tables detected on page 7"},
    "img2table": {"status": "pass", "detail": "0 additional tables"},
    "docling": {"status": "not_installed", "detail": null},
    "pandoc": {"status": "pass", "detail": "binary found, arXiv ID: 2401.12345"},
    "claude": {"status": "pass", "detail": "haiku responded", "cost_usd": 0.002, "model": "haiku"}
  },
  "capabilities": {
    "base_extraction": true,
    "table_detection": true,
    "table_enhancement": true,
    "math_reextraction": true,
    "arxiv_shortcut": true,
    "docling_tables": false
  },
  "overall": "pass"
}
```

`overall` MUST be:
- `"pass"` — all installed components work
- `"degraded"` — some components broken or missing, pipeline will still produce output
- `"fail"` — pymupdf4llm broken (pipeline cannot run at all)

#### FR-6: Quality Impact Summary

After the component table, the check MUST print a summary of what extraction quality the user can expect given available components. This maps directly to pipeline capabilities:

| Capability | Requires | Impact When Missing |
|------------|----------|-------------------|
| Base text extraction | pymupdf4llm | Pipeline cannot run |
| Table detection | GMFT or Img2Table | Tables in pymupdf4llm output only (may have `<br>` artifacts, `ColN` headers) |
| Table enhancement | Claude + table detector | Detected tables with extraction failures won't be recovered |
| Math re-extraction | Claude | Math-heavy pages keep garbled Unicode instead of LaTeX |
| arXiv shortcut | Pandoc + network | arXiv papers go through full PDF pipeline instead of clean HTML conversion |
| Third-pass table detection | Docling | Borderless tables missed by GMFT+Img2Table won't be caught |

#### FR-7: Exit Code

The command MUST return meaningful exit codes for CI use:

| Exit Code | Meaning |
|-----------|---------|
| 0 | All installed components pass |
| 1 | One or more installed components failed (broken, not just missing) |
| 2 | pymupdf4llm failed (pipeline cannot run) |

`not_installed` components do NOT cause a non-zero exit code. Only components that are installed but broken trigger failure.

### Non-Functional Requirements

- **NFR-1: Speed.** The full check (excluding Claude) SHOULD complete in under 30 seconds for a typical PDF. Claude adds its own latency (~5–15s).
- **NFR-2: Cost transparency.** The Claude probe cost MUST be reported to the user. No hidden spending.
- **NFR-3: No side effects.** The check MUST NOT write output files (no `output.md`, `decisions.json`, etc.). Temporary files (page images) MUST be cleaned up.
- **NFR-4: Independence.** A failure in one component probe MUST NOT prevent other probes from running. Each probe is isolated.

---

## Acceptance Criteria

### Core Functionality

- [ ] `agentic-mbse extract --check paper.pdf` runs all 6 component probes and prints a status table
- [ ] A broken `invoke_claude()` (e.g., the JSONL parsing bug) is reported as `FAIL` with the error message
- [ ] A missing optional component (e.g., GMFT not installed) is reported as `not_installed`, not `FAIL`
- [ ] Claude probe uses haiku and reports actual cost
- [ ] When `--budget 0` is passed alongside `--check`, Claude probe is skipped with explanation
- [ ] Page selection finds math, table, and heading pages from the provided PDF
- [ ] When the PDF has no math/table pages, the check reports which components were untested
- [ ] Pandoc probe runs full arXiv HTML conversion (not just a HEAD check) when an arXiv ID is found
- [ ] `--check --json` outputs valid JSON to stdout with all component statuses
- [ ] Exit code is 0 when all installed components pass, 1 when any installed component fails
- [ ] Quality impact summary tells the user what to expect

### Quality & Integration

- [ ] Existing tests continue to pass
- [ ] No output files are written during `--check` (no side effects)
- [ ] Temporary files (rendered page images) are cleaned up
- [ ] Check completes in <30s for a typical PDF (excluding Claude)
- [ ] Unit tests cover: page selection logic, each probe in isolation (mocked), JSON output format, exit code logic
- [ ] Integration test (manual): run `--check` with real PDF, verify Claude probe works end-to-end

---

## Related Artifacts

- **Triggering bug:** `.project/active/v4-claude-invocation-and-logging/design.md`
- **Pipeline architecture:** `.project/concepts/doc-extraction/design.md`
- **Pipeline requirements:** `.project/concepts/doc-extraction/requirements.md`
- **User-facing docs:** `docs/extraction.md`
- **Developer docs:** `docs/extraction-internals.md`
- **Ground truth (page characteristics):** `tests/corpus/ground_truth.jsonl`

---

**Next Steps:** After approval, proceed to `/_my_design`
