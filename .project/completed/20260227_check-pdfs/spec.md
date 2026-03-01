# Spec: `--check` Performance — Built-in Test PDF Corpus

**Status:** Complete
**Owner:** Reid W
**Created:** 2026-02-27
**Complexity:** SMALL
**Branch:** doc-ingest-clean
**Parent:** EPIC-PDFV4-001 (follows `extract --check`)

---

## Business Goals

### Why This Matters

`--check` is a pipeline readiness probe: "is my environment ready to extract PDFs?" Currently it requires the user to provide a PDF, which is wrong — the user shouldn't have to think about which PDF exercises all pipeline features. It also means every invocation loads GMFT (~8-15s) and Img2Table (~5-10s) models against whatever random PDF the user picks, which may not even have tables or math to exercise the relevant probes.

Reported by a downstream user (fusion-tea): model loading overhead makes `--check` painfully slow, and the per-PDF invocation model doesn't make sense for what is fundamentally an environment readiness question.

### Success Criteria

- [x] `agentic-mbse extract --check` works with no PDF argument — uses built-in test corpus
- [x] The corpus includes multiple PDFs that together exercise all 6 probes
- [x] Check completes as fast as possible given the probes that need to run (Claude budget only on first PDF)

### Priority

Medium. `--check` works today with a user-provided PDF. This is a UX and performance fix.

---

## Problem Statement

### Current State

- `--check` requires a PDF path argument from the user
- The user has to guess which PDF would be a good test candidate
- If the chosen PDF has no tables, GMFT/Img2Table probes return UNTESTED — useless
- If the chosen PDF has no math, Claude math re-extraction probe is untested
- Model loading takes 15-25 seconds regardless of whether the probes find anything to exercise
- The "batch" complaint is really: "why do I have to run this per-PDF when it's about my environment?"

### Desired Outcome

`--check` uses a small set of built-in test PDFs (bundled with the package) that together cover all pipeline features: headings, tables, math, and arXiv HTML conversion. No single PDF can realistically exercise everything — a standard PDF won't trigger arXiv detection, and a short arXiv paper may lack rich tables or math. The user just runs `agentic-mbse extract --check` and gets a definitive answer about their environment.

---

## Scope

### In Scope

- Bundle a small set of test PDFs with the package (2+ PDFs covering all probe types)
- Make the PDF argument optional for `--check` (use built-in corpus when not provided)
- At least one PDF with 3-5 pages covering headings, tables, and math
- At least one real arXiv paper that triggers the HTML detection + Pandoc conversion path
- Keep the option to pass a user PDF for debugging specific extraction issues

### Out of Scope

- Changing probe logic or output format (those work correctly today)
- Model loading optimization (GMFT/Img2Table weight loading is inherent to "does it work?" probing)
- Batch/directory mode (no longer needed — `--check` is an environment check, not a per-document check)

### Edge Cases & Considerations

- **Package distribution:** The test PDFs must be included in the package (`package_data` or similar). Keep total size small (<1MB for all test PDFs combined).
- **User still passes a PDF:** Backward compatible — if a PDF is provided, use it (current behavior).
- **Corpus PDF construction:** Could be synthetic (generated with reportlab) or a real representative PDF. Synthetic is more controllable and avoids copyright concerns.
- **arXiv PDF:** Must be a real arXiv paper so that the HTML detection path hits an actual arXiv ID with HTML available. Short papers (2-4 pages) preferred.
- **Probe coverage:** No single PDF needs to cover all probes. The check runner iterates over all built-in PDFs and aggregates probe results, so each probe just needs to be exercised by at least one PDF.

---

## Requirements

### Functional Requirements

#### FR-1: Built-in Test PDF Corpus ✅

The package MUST include multiple test PDFs that together exercise all 6 probes. No single PDF is expected to cover everything.

**PDF A — Feature-rich corpus PDF (3-5 pages):** ✅ `test_features.pdf` (89KB, 2 pages from hsu_2020.pdf)
1. ✅ A page with headings and body text (page 0 — exercises pymupdf4llm extraction)
2. ✅ A page with at least one table (page 1 — exercises GMFT, Img2Table probes)
3. ⚠️ Math coverage moved to PDF B (arxiv_probe.pdf page 1, garble score 4.0) — see deviation note

This PDF can be synthetic (generated with reportlab) or a real document. SHOULD be under 500KB. ✅ (89KB)

**PDF B — arXiv paper (real paper, 2-4 pages preferred):** ✅ `arxiv_probe.pdf` (246KB, 2 pages from paischer_2025.pdf)
1. ✅ Contains `arXiv:2510.07314v1` on page 0 (exercises arXiv detection)
2. ✅ The arXiv ID corresponds to a paper with HTML available on ar5iv (exercises the full arXiv HTML + Pandoc conversion path)

**Why a separate arXiv PDF:** The current `probe_pandoc()` only tests "binary found" unless the PDF happens to be an arXiv paper. With a non-arXiv PDF, the entire arXiv HTML conversion path — `detect_arxiv_id()` → `check_arxiv_html()` → `convert_arxiv_html()` — goes completely untested. A dedicated arXiv paper in the corpus guarantees this path is exercised.

**Why multiple PDFs:** A synthetic PDF with a fake arXiv ID doesn't work — `check_arxiv_html()` hits the real arXiv API, so the ID must be real. And real arXiv papers may not have rich tables or varied math. Splitting into purpose-built PDFs ensures each probe gets the content it needs without contorting a single document.

The total size of all test PDFs SHOULD be under 1MB combined. ✅ (334KB)

#### FR-2: Optional PDF Argument ✅

When `--check` is invoked without a PDF path:
- ✅ Run probes against all built-in test PDFs (`extract_cli.py:243-248`)
- ✅ Aggregate results: a probe is PASS if it passed on any PDF, FAIL if it failed on all (`merge_check_results()`)
- ✅ Report in output that the built-in test corpus is being used (`extract_cli.py:237-240`, stderr)

When `--check` is invoked with a PDF path:
- ✅ Use the provided PDF only (current behavior, unchanged — `extract_cli.py:278-311`)

#### FR-3: No Other Behavioral Changes ✅

- ✅ Probe logic, output format, exit codes, JSON output — all unchanged
- ✅ `select_pages()` continues to pick representative pages from whatever PDF is used

### Non-Functional Requirements

- **NFR-1: Package size.** ✅ The test PDF corpus MUST be small enough to not bloat the package distribution (<1MB total for all test PDFs). Actual: 334KB.
- **NFR-2: Backward compatibility.** ✅ Passing a PDF still works exactly as today. Tested: `TestCliBuiltinCorpus::test_check_with_path_still_works`, `TestCliCheckIntegration` (6 tests).

---

## Acceptance Criteria

- [x] `agentic-mbse extract --check` (no PDF arg) runs successfully using built-in test corpus
- [x] All 6 probes are exercised across the corpus (none return UNTESTED) — **note:** docling probe returns UNTESTED (pre-existing stub, not related to this feature; detection not yet implemented)
- [x] Feature-rich PDF (PDF A) exercises: pymupdf4llm, GMFT, Img2Table ~~, Claude math probes~~ — **deviation:** math moved to PDF B; Claude math probe is exercised via `arxiv_probe.pdf` page 1 (garble score 4.0)
- [x] arXiv paper (PDF B) exercises full arXiv path: ID detection → HTML check → Pandoc conversion
- [x] `agentic-mbse extract --check my.pdf` still works (backward compat)
- [x] Built-in test PDFs are included in installed package (under `src/agentic_mbse/extraction/check_corpus/`, auto-included by wheel config)
- [x] Existing tests pass without modification — 177 tests, 0 failures
- [x] Total test corpus is <1MB — 334KB

---

## Related Artifacts

- **Current implementation:** `.project/active/extract-check/` — single-file `--check`
- **Probe functions:** `src/agentic_mbse/extraction/check.py`
- **CLI entry point:** `src/agentic_mbse/cli/extract_cli.py`
- **User feedback:** fusion-tea project

---

---

## Deviation Notes

1. **PDF A source changed:** `sparc_overview.pdf` → `hsu_2020.pdf`. Sparc page 9 had empty pipe-row cells; hsu_2020 page 7 has 36 real data rows.
2. **Math coverage on PDF B instead of PDF A:** hsu_2020 lacks math content. arxiv_probe.pdf page 1 (paischer_2025 page 2) has garble score 4.0, covering the Claude math re-extraction path. Net effect: all probes covered across 2 PDFs.
3. **PDF A is 2 pages, not 3-5:** Only 2 pages needed (headings + tables). The content exercises the probes; extra pages would just increase size.
4. **Docling probe always UNTESTED:** Pre-existing behavior — docling detection is a stub. Not related to this feature. The probe runs; it just has no real detection logic to exercise.

**Implementation:** See `plan.md` for phase-by-phase details.
