# Spec: Reliable arXiv extraction

**Work item:** ARXIV-EXTRACTION
**Status:** Draft — specified; implementation not started
**Owner:** Reid Westwood
**Created:** 2026-10-18
**Branch:** `fix/arxiv-extraction`
**Base:** local `main` at `8b027bbc`

## Problem

The PDF pipeline automatically substitutes arXiv HTML whenever Pandoc is available and a first-page regex finds an arXiv ID. This can replace an unrelated PDF with a cited paper. The shortcut returns before PDF image extraction and does not download HTML images, leaving figure references without saved assets. Users cannot disable the shortcut through the CLI.

The direct arXiv HTML route downloads images, but converts the whole page. Its output includes the issue-report dialog, navigation, table of contents outside the paper, footer, funder logos and inline base64 UI icons. Consumers currently hide Pandoc from PATH for PDFs and strip data-image references themselves.

Origin: personal-os queue report `queue/2026-10-18-agentic-mbse-arxiv-pdf-shortcut-drops-figures-and.md` (2026-10-18). This is development work for agentic-mbse, tracked under `.project/`.

## Investigation evidence

Independently reproduced on 2026-10-18 at `517f3e11`; extraction source and CLI have no diff from this worktree's base. Pandoc 3.1.3, freshly fetched `https://arxiv.org/html/2610.14224`:

- A generated unrelated PDF with first-page text `Prior work: arXiv:2610.14224` was identified as that paper. A controlled shortcut run with fetching/conversion stubbed returned Harness² content for that PDF.
- Real conversion through `_try_arxiv_shortcut`, using saved HTML and a configured image directory, retained 35 image references but wrote zero image files. These references include UI assets, so 35 is not a figure count.
- Sanitization followed by real web Pandoc conversion produced 255,877 characters and 16 inline data-image references, including the issue dialog, navigation, footer and funder logos.
- Source inspection confirmed no shortcut-disable argument. The web fallback already logs a warning; the original report's claim of completely silent fallback is too broad. That warning is absent from the returned extraction warnings.

Temporary reproduction artifacts: `/tmp/arxiv-investigation-1topu2hb/` (`citation-only.pdf`, `raw.html`, `web.md`, `pdf-shortcut.md`). These paths are supporting local evidence, not required test fixtures. The report's earlier seven-figure/23-PDF-image counts were not independently reproduced and are not acceptance thresholds.

## Scope

Repair automatic arXiv substitution, local figure persistence, extraction of the paper alone, explicit shortcut control, and fallback diagnostics. Cover the PDF CLI and Python pipeline and the direct arXiv HTML route. Share arXiv cleanup/image behavior where practical.

Out of scope: general website boilerplate extraction, OCR, PDF figure segmentation quality, personal-os changes, and changing the existing latest-version selection policy.

## Requirements

### R1 — Preserve paper figures in both routes

A successful PDF HTML shortcut with a configured image output directory MUST download the paper's externally referenced images and rewrite successful references to relative local paths using the existing output layout. The direct HTML route MUST provide the same behavior. Image counts MUST reflect files actually persisted. Repeated references, relative/root-relative/absolute URLs and failed downloads MUST be handled consistently across routes.

Download failures MUST be observable and MUST NOT leave a rewritten local reference to a nonexistent file. Preserve the remote reference when retrieval fails. Programmatic extraction without a configured image directory MAY retain remote references; that limitation must be documented. Preserve paper figure captions, tables and mathematical content through cleanup.

### R2 — Require evidence that the PDF is the identified paper

A first-page occurrence of an arXiv ID alone MUST NOT authorize substitution. Identification MUST distinguish the paper's own identifier from prose citations and resolve conflicting evidence conservatively. Ambiguous identity MUST continue through normal PDF extraction. The design must document the identity evidence it trusts and its limits; checking only for arXiv Creator metadata is insufficient to distinguish citations in an arXiv-origin PDF.

Regression coverage MUST include a plain unrelated PDF citing an ID, an arXiv-origin PDF citing another ID, conflicting IDs, and a genuine paper with its own arXiv identifier. Explicitly supplied `--html-path` remains a deliberate source override rather than an automatic identity decision.

### R3 — Provide explicit opt-out

Add `--no-arxiv-shortcut` and a corresponding Python `PipelineConfig` control, enabled by default for backward compatibility. When disabled, extraction MUST NOT detect an ID, probe/fetch arXiv HTML, or invoke HTML conversion for PDF input; normal PDF extraction proceeds with Pandoc still on PATH. Direct HTML URL extraction remains available.

Combining `--no-arxiv-shortcut` with `--html-path` MUST produce a clear CLI argument error; the equivalent contradictory Python configuration MUST fail clearly. Help text and extraction documentation MUST explain automatic substitution and this escape hatch. Apply the control to every CLI path that uses the PDF pipeline, including PDF URLs and batch inputs where supported.

### R4 — Convert only the paper

Both arXiv Pandoc routes MUST select the paper content before conversion and remove surrounding arXiv header/navigation, issue dialogs, site footer, funder logos and UI icons. Cleanup MUST preserve paper title, authors, abstract, sections, references, appendices, figures, captions, tables and math. Remove UI data-image icons by their page context; do not blanket-delete potentially legitimate embedded paper figures.

Fixtures MUST represent real arXiv/LaTeXML structure, including surrounding chrome and an article body. If a paper container cannot be recognized, do not silently claim successful paper-only conversion of the full page: use the existing route fallback with an observable diagnostic. The implementation design must define supported structures and the fallback boundary.

### R5 — Report fallback and partial image failures

When the direct HTML arXiv conversion fails or yields insufficient content and trafilatura is used, retain accurate backend provenance and include an actionable warning in the returned result and persisted warnings/metrics. Keep the existing log warning. Successful fallback remains a successful extraction. PDF shortcut failure continues to normal PDF extraction; opt-out is not an extraction failure.

Preserve raw-source saving and hashing of original fetched bytes, and existing fetched-version provenance. Cleanup MUST NOT replace saved raw HTML with the cleaned article fragment.

## Acceptance and verification

| Criterion | Required evidence |
|---|---|
| Figures are portable | Offline fixture with multiple paper images: both routes save bytes under the output image directory, reference existing relative files, and report matching saved-image counts |
| Failures are honest | Controlled failed and oversized image responses leave no dangling local references and expose warnings; repeated references have consistent handling |
| Citations cannot substitute content | Real small PDF fixtures for R2 exercise detection and pipeline selection; negative cases never invoke HTML conversion, positive identity still permits the shortcut |
| Users can force PDF extraction | CLI/config tests cover opt-out with Pandoc available, contradictory options, and applicable PDF URL/batch forwarding |
| Output contains the paper alone | Realistic HTML fixture passes both conversions: chrome/UI assets absent; paper sections, references, appendices, figure/caption, table and math survive |
| Legitimate embedded figures survive | Fixture includes a paper data-image alongside UI data-image icons; cleanup preserves the former and removes the latter |
| Fallback is visible | Force Pandoc failure and short output; verify successful fallback backend and returned/persisted warning |
| Provenance is unchanged | Existing raw-byte hash/save-source and fetched-version tests pass with article cleanup enabled |
| Live result corroborates fixtures | Record an optional bounded Harness² run with Pandoc version, fetched source/version, saved paper-image count, chrome checks and download failures; network availability is not a unit-test prerequisite |

Run focused extraction tests (`test_pandoc_convert.py`, `test_pipeline.py`, `test_web_backend.py`, `test_extract_cli.py`) and lint/type checks appropriate to changed code. Tests must exercise real HTML cleanup and real PDF identifier interpretation; subprocess/network stubs are appropriate at external boundaries. Pin representative HTML locally so changing arXiv chrome cannot make regression tests nondeterministic.

## Design questions to settle next

- Which PDF layout/metadata evidence reliably identifies the paper's own arXiv ID, and how is ambiguity rejected?
- Which article-container variants are supported, and where does extraction fall back when they are absent?
- How should shared image persistence adapt to `PipelineConfig.extracted_images_dir` versus the web output root, including warning/count propagation?

## Completion

All requirements and acceptance criteria above are implemented and verified, CLI behavior documented, and downstream consumers can use Pandoc on PATH without citation substitution or missing downloaded paper figures. This spec does not authorize modifying personal-os; downstream workaround removal is separate consumer work.
