# Spec: Reliable arXiv extraction

**Work item:** ARXIV-EXTRACTION
**Status:** Draft (revised after spec review), with one open owner gate (shortcut default, R3). Implementation in progress: plan Phases 0–7 of 0–8 done (2026-10-18); Phase 8 (live Harness² check) remains.
**Owner:** Reid Westwood
**Created:** 2026-10-18
**Revised:** 2026-10-18 (incorporates `spec_review.md` Resolutions)
**Branch:** `fix/arxiv-extraction`
**Base:** local `main` at `8b027bbc`

Grades: `[NEED]` = the owner stated it; `[HARD]` = an existing interface or behavior forces it; `[INFERRED]` = derived here or decided by the orchestrator under delegated authority (challengeable on evidence); `[INHERITED]` = taken from an upstream document, cited.

## Problem

**[NEED]** Downstream consumers can keep Pandoc on PATH safely: no citation substitution, no missing figures, no arXiv chrome. Their current workarounds (hiding Pandoc from PATH for PDFs, stripping data-image references) become unnecessary.

When it finds an arXiv ID, the PDF pipeline takes a shortcut: it replaces PDF extraction with conversion of the paper's arXiv HTML version. Today the shortcut fires whenever Pandoc is available and a first-page regex finds any arXiv ID, so it can replace an unrelated PDF with a cited paper. It returns before PDF image extraction and does not download HTML images, which leaves figure references with no saved assets. Users cannot turn it off through the CLI.

The direct arXiv HTML route downloads images but converts the whole page. Its output includes the issue-report dialog, navigation, the table of contents outside the paper, the footer, funder logos and inline base64 UI icons.

**[INHERITED]** Origin and the consumers' workarounds: personal-os queue report `queue/2026-10-18-agentic-mbse-arxiv-pdf-shortcut-drops-figures-and.md` (2026-10-18). This is development work for agentic-mbse, tracked under `.project/`.

## Investigation evidence

Independently reproduced on 2026-10-18 at `517f3e11`. The extraction source and CLI have no diff from this worktree's base. Pandoc 3.1.3, freshly fetched `https://arxiv.org/html/2610.14224`:

- A generated unrelated PDF with first-page text `Prior work: arXiv:2610.14224` was identified as that paper. A controlled shortcut run with fetching and conversion stubbed returned Harness² content for that PDF.
- Real conversion through `_try_arxiv_shortcut`, using saved HTML and a configured image directory, kept 35 image references but wrote zero image files. These references include UI assets, so 35 is not a figure count.
- Sanitization followed by real web Pandoc conversion produced 255,877 characters and 16 inline data-image references, including the issue dialog, navigation, footer and funder logos. All 16 sat in chrome outside the paper.
- Source inspection confirmed there is no shortcut-disable argument. The web fallback already logs a warning, so the original report's claim of completely silent fallback is too broad. That warning is absent from the returned extraction warnings.
- `extract --check` (`check.py`, `probe_pandoc`) calls `detect_arxiv_id`, `check_arxiv_html` and `convert_arxiv_html` directly, outside the pipeline. It reports "2 chars" because it takes `len()` of the returned `(markdown, bytes)` tuple.

Temporary reproduction artifacts: `/tmp/arxiv-investigation-1topu2hb/` (`citation-only.pdf`, `raw.html`, `web.md`, `pdf-shortcut.md`). These paths are supporting local evidence, not required test fixtures. The report's earlier seven-figure and 23-PDF-image counts were not independently reproduced and are not acceptance thresholds.

## Scope

Repair automatic arXiv substitution, local figure persistence, paper-only extraction, explicit shortcut control and fallback diagnostics. Cover the PDF CLI and Python pipeline, `extract --check`'s Pandoc probe, and the direct arXiv HTML route. Share arXiv cleanup and image behavior where practical.

Out of scope: general website boilerplate extraction, OCR, PDF figure segmentation quality, personal-os changes, and changing the existing latest-version selection policy.

## Requirements

### R1: Preserve paper figures in both routes

**[INFERRED]** A successful PDF HTML shortcut with a configured image output directory MUST download the paper's externally referenced images and rewrite successful references to relative local paths, using the existing output layout. The direct HTML route MUST behave the same way. Image counts MUST reflect files actually persisted. The invariant across routes: every rewritten reference points at an existing file, and every failed one keeps its original reference.

**[INFERRED]** Repeated references to one URL are downloaded once, and every occurrence is rewritten to the same local file. If that download fails, every occurrence stays remote and one warning is emitted.

**[INFERRED]** For a local HTML source (`--html-path`) with no page URL: absolute http(s) image URLs are downloaded. Relative paths resolve against `<base href>` if present, otherwise against the HTML file's directory; the file is copied if it exists. Anything unresolvable stays as written, with a warning. The code does not guess a remote arXiv base.

**[INFERRED]** Download failures MUST be observable. Observable means all three: in the returned result's warnings, in the warnings/metrics persisted alongside the output (the mechanism the web route uses, extended to PDF results), and printed to stderr by the CLI. Programmatic extraction without a configured image directory MAY keep remote references; that limitation must be documented. Preserve paper figure captions, tables and mathematical content through cleanup.

### R2: Require evidence that the PDF is the identified paper

**[INFERRED]** Identity is conservative. A first-page occurrence of an arXiv ID alone MUST NOT authorize substitution, and IDs found only in body prose are never identity evidence. Substitution requires own-ID evidence from a trusted source. Candidate sources include the arXiv margin stamp and the arxiv.org URL a PDF was fetched from. Design chooses the exact evidence set. The stamp hypothesis must be verified against real arXiv PDFs before the design relies on it. A post-fetch title cross-check is a design option, not a requirement. Checking only for arXiv Creator metadata cannot tell citations apart in an arXiv-origin PDF, so it is insufficient on its own.

**[INFERRED]** Expected outcomes:
- Ambiguous identity continues through normal PDF extraction.
- False negatives on genuine papers that lack trusted own-ID evidence (publisher versions, author builds, unreadable stamps) are acceptable. They fall through to normal PDF extraction, and design does not try to recover them.
- An arXiv-origin PDF citing another ID substitutes only for the ID its own-ID evidence names, never for the cited ID.
- Conflict means two trusted sources name different IDs (ignoring the version suffix), or more than one candidate sits in a trusted position. Conflict goes to normal PDF extraction.

**[HARD]** Explicitly supplied `--html-path` (`arxiv_html_path`) remains a deliberate source override, not an automatic identity decision.

**[INFERRED]** `extract --check` MUST apply the same identity rule as the pipeline, so its report predicts what `extract` will do. It MUST report the converted character count, not the tuple length.

### R3: Provide explicit opt-out

**[INFERRED]** Add `--no-arxiv-shortcut` and a corresponding Python `PipelineConfig` control. When the shortcut is disabled, extraction MUST NOT detect an ID, probe or fetch arXiv HTML, or invoke HTML conversion for PDF input. Normal PDF extraction proceeds with Pandoc still on PATH. Direct HTML URL extraction remains available.

**Open owner gate:** whether the shortcut is on by default. The owner reserved this decision. **Provisional default: on**, so design and implementation can proceed. Changing it later means changing one default value and its docs.

**[INFERRED]** Combining `--no-arxiv-shortcut` with `--html-path` MUST produce a clear CLI argument error, and the equivalent contradictory Python configuration MUST fail clearly. Help text and extraction documentation MUST explain automatic substitution and this escape hatch. The control applies to every CLI path that uses the PDF pipeline, including PDF URLs and batch inputs where supported, and to `extract --check`'s Pandoc probe.

### R4: Convert only the paper

**[INFERRED]** Both arXiv Pandoc routes MUST select the paper content before conversion. Surrounding arXiv header and navigation, issue dialogs, site footer, funder logos and UI icons MUST NOT appear in output. Cleanup MUST preserve paper title, authors, abstract, sections, references, appendices, figures, captions, tables and math. Cleanup removes nothing inside the recognized paper container for being a data URI.

**[INFERRED]** Fixtures MUST represent real arXiv/LaTeXML structure, including surrounding chrome and an article body. If a paper container cannot be recognized, the route MUST NOT claim a paper-only conversion of the full page. Instead it takes its existing fallback with an observable diagnostic: trafilatura for the direct HTML route, and normal PDF extraction for the PDF shortcut. The design must define the supported structures.

### R5: Report fallbacks and shortcut failures

**[INFERRED]** When the direct HTML arXiv conversion fails or yields insufficient content and trafilatura is used, keep accurate backend provenance and include an actionable warning in the returned result and the persisted warnings/metrics. Keep the existing log warning. A successful fallback remains a successful extraction.

**[INFERRED]** PDF shortcut failure continues to normal PDF extraction and produces a warning, observable as in R1. An explicit `--html-path` that is ignored (for example, because Pandoc is missing) produces a warning. Opt-out is not an extraction failure and produces no warning.

**[HARD]** Preserve raw-source saving, hashing of the original fetched bytes, and existing fetched-version provenance. Cleanup MUST NOT replace saved raw HTML with the cleaned article fragment.

## Acceptance and verification

| Criterion | Required evidence |
|---|---|
| Figures are portable | Offline fixture with multiple paper images: both routes save bytes under the output image directory, reference existing relative files, and report matching saved-image counts |
| Failures are honest | Controlled failed and oversized image responses leave no dangling local references; warnings appear in the returned result, persisted metrics and CLI stderr; one URL referenced twice yields one file, or on failure two remote references and one warning |
| Local HTML images resolve | `--html-path` fixture with absolute, `<base href>`-relative, file-relative and unresolvable references; each behaves per R1 |
| Citations cannot substitute content | Real PDF bytes parsed by the real detector (fixture origin is a design choice; generated PDFs are acceptable) cover: a plain unrelated PDF citing an ID; an arXiv-origin PDF citing another ID; conflicting IDs; a genuine paper with trusted own-ID evidence. Negative and conflict cases never invoke HTML conversion; the positive case still permits the shortcut |
| `--check` predicts `extract` | `extract --check` on the citation-only PDF reports no identified paper and fetches nothing; with opt-out it skips the probe; it reports the real character count |
| Users can force PDF extraction | CLI/config tests cover opt-out with Pandoc available, contradictory options, and applicable PDF URL/batch forwarding |
| Output contains the paper alone | Realistic HTML fixture passes both conversions: chrome and UI assets absent; paper sections, references, appendices, figure/caption, table and math survive; one small embedded data-URI image inside the article survives |
| Fallback is visible | Force Pandoc failure, short output and an unrecognized container; verify the per-route fallback and the returned/persisted warning; an ignored `--html-path` warns |
| Provenance is unchanged | Existing raw-byte hash/save-source and fetched-version tests pass with article cleanup enabled |
| Live result corroborates fixtures | Required recorded check at audit when network is available: a bounded Harness² run with Pandoc on PATH and no data-image stripping, recording Pandoc version, fetched source/version, saved paper-image count, chrome checks and download failures. If network is unavailable, record that; it does not block |

Run focused extraction tests (`test_pandoc_convert.py`, `test_pipeline.py`, `test_web_backend.py`, `test_extract_cli.py`, plus the `--check` tests) and lint/type checks appropriate to the changed code. Tests must exercise real HTML cleanup and real PDF identifier interpretation. Subprocess and network stubs are appropriate at external boundaries. Pin representative HTML locally, so changing arXiv chrome cannot make regression tests nondeterministic.

## Design questions to settle next

- Which PDF layout, metadata and source-URL evidence reliably identifies the paper's own arXiv ID? Verify the margin-stamp hypothesis against real arXiv PDFs.
- Which article-container variants are supported?
- How should shared image persistence adapt to `PipelineConfig.extracted_images_dir` versus the web output root? How do warnings reach `PipelineResult`, which has no warnings field today?

## Completion

All requirements and acceptance criteria above are implemented and verified, and CLI behavior is documented. Downstream consumers can use Pandoc on PATH with no citation substitution, no missing downloaded paper figures, and no arXiv chrome or UI data-image references. Their Pandoc-hiding and data-image-stripping workarounds are therefore unnecessary. The R3 default-on gate is either answered by the owner or still recorded as open with the provisional default shipped. This spec does not authorize modifying personal-os; removing the downstream workarounds is separate consumer work.

## Related Artifacts

- **Spec review:** `.project/active/arxiv-extraction/spec_review.md` (Resolutions incorporated 2026-10-18)
- **Origin:** personal-os queue report cited in Problem
- **Design:** `.project/active/arxiv-extraction/design.md` (to be created)
