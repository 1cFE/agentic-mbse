# Audit: Reliable arXiv extraction (ARXIV-EXTRACTION)

**Verdict:** Needs Work (one owner ruling; no code defect blocks)
**Audited:** 2026-10-18
**Branch:** `fix/arxiv-extraction`
**Commit:** `373a34df` (implementation `b1d61475..373a34df`, base `8b027bbc`)

---

## The Point

**[NEED]** Downstream consumers (personal-os `kg add`) can keep Pandoc on PATH safely: no citation substitution, no missing figures, no arXiv chrome. Their two workarounds become unnecessary: hiding Pandoc from PATH for PDFs, and stripping `data:` image links.

The owner's verbatim done-condition (personal-os queue report `queue/2026-10-18-agentic-mbse-arxiv-pdf-shortcut-drops-figures-and.md`, Need): "(1) the PDF pipeline's arXiv HTML shortcut keeps the paper's figures … and only fires for the paper itself … or it can be turned off with a CLI flag. (2) The arXiv HTML route (pandoc-arxiv) drops arXiv's page header, footer, funder logos and inline base64 icon images, leaving the paper. Then personal-os kg add can put pandoc back on PATH and stop stripping data: images."

Owner constraints: the shortcut ships on by default, set in one constant (open gate). No public `PipelineConfig` field or CLI flag is removed or renamed.

## Summary

The engineering is solid. Identity, opt-out, paper-only selection, figure saving on both routes, the warnings channel and `--check` alignment all work as specified. The code reads like its neighbors, and the tests exercise real HTML, real generated PDFs and real Pandoc, with stubs only at the network and subprocess boundaries. Full suite: 2909 passed, only the 3 known environmental failures.

One thing stops certification. It is a product question, not a code bug. The output still carries 12 `data:image/svg+xml` links (about 32 KB on Harness²). The owner's done-condition says `kg add` should be able to stop stripping `data:` images. The spec decided to keep these links as paper content, but it based that on an evidence line that turns out to be wrong. The owner needs to rule on it.

## Product Judgment

**Is this the right piece of work?** Yes, for four of the five things the owner named. Pandoc on PATH no longer substitutes cited papers, figures are saved, chrome is gone, and there is an off switch. The fifth, "stop stripping `data:` images," is not shown to be safe.

**The open finding (product-lens audit-F1, smell 3 fired).** I checked it and it is true in the code and in the live output.

- The spec's investigation line says the base web output's "16 inline data-image references … all 16 sat in chrome outside the paper" (`spec.md:29`). That is wrong. I compared the base run's output (`/tmp/arxiv-investigation-1topu2hb/web.md`) with this branch's live output (`/tmp/harness2-web/output.md`). 12 of the 16 `data:image/svg+xml` links are byte-identical in both. They come from the 12 LaTeXML `<svg class="ltx_picture">` elements inside the article: the title graphic and the C1–C8 component icons. Only 4 SVG links (Font Awesome UI icons) and 1 PNG (footer logo) were chrome. This branch removed those 5.
- The owner's report counted "about 15 inline data:image/svg+xml base64 icons, about 37k" chars. That count and size match the 12 in-article pictures plus the 4 UI icons. So what the owner called "icons to drop" is mostly what the spec then kept.
- The spec's `[INFERRED]` rule "Cleanup removes nothing inside the recognized paper container for being a data URI" (R4, and design invariant 6) rests on the false evidence line. It works against the owner's stated done-condition. Nobody surfaced that conflict to the owner (capture-fidelity law 4).

**Impact if unaddressed.** `kg add` cannot drop its `data:` stripping without taking about 32 KB of inline base64 per paper like this one. Or it keeps stripping, and the owner's done-condition isn't met.

**What the owner needs to decide.** Three options:

- **Accept them as paper content.** No code change. `kg add` either keeps them or keeps a stripping step. The spec's evidence line gets corrected.
- **Externalize them (my recommendation).** Write each in-article `data:image/svg+xml` image to `images/` as an `.svg` file and point the ref at it, using the same count and warning rules as other figures. This keeps the paper content that R4 protects. It also leaves no `data:` links in `output.md`, so the workaround really is unnecessary. The change is small and local to `persist_images` in `arxiv_html.py`.
- **Drop them.** Simplest, but it deletes real paper content: the component icons carry meaning in the text.

Other lens findings, checked:

- **audit-F2 (a failed download keeps a remote ref).** The spec allows this explicitly (R1: a failed ref keeps its original reference and warns). Not a blocker.
- **audit-F3 (title logo).** See the follow-up assessment below. It is decided together with F1.
- **audit-F4 (PDF-URL provenance).** Pre-existing. See below.

The earlier ledger entry (design review, gate CLEAR) had no open BLOCK.

## Blockers

1. **Owner ruling needed: in-article `data:` image links still ship, against the owner's done-condition.** Where: `arxiv_html.py:333-337` (`persist_images` skips `data:` refs), `spec.md:29` (the wrong evidence), `spec.md:77` (the rule built on it). Live evidence: 12 `data:image/svg+xml` refs, about 32 KB of 246 KB, on both routes for 2610.14224. To resolve: the owner picks one of the three options above. If the owner accepts them, this closes with a spec correction and no code change. In every case, correct the spec's investigation line.

## Advisory

Ranked by importance.

1. **Some image-fetch failures crash the run instead of warning.** `persist_images` catches only `OSError` and `ImageFetchError` (`arxiv_html.py:343`). Two fetch failures are neither. An invalid URL raises `ValueError`; I reproduced it with `http://[::1/x.png`. A broken chunked response raises `http.client.IncompleteRead`, which comes from `HTTPException` (I traced this in the stdlib; I did not reproduce it). On the PDF route, `persist_images` runs outside the shortcut's `try` (`pipeline.py:268-273`), and the CLI doesn't wrap `extract_pdf` (`extract_cli.py:530`). So one bad figure aborts that document, and in a batch, the rest of the run. At base, both routes caught `Exception` here and warned. Pandoc percent-encodes spaces, so everyday filenames are safe, and the risk is low. Fix: also catch `ValueError` and `http.client.HTTPException` in `persist_images`. Then the R1 rule (a failed figure keeps its ref and warns) holds for every fetch failure.
2. **A web double failure loses the reason.** The arXiv conversion can fail and trafilatura can then return nothing. When that happens, `extract_web_content` returns an error result without the "arXiv paper conversion failed (…)" warning (`web_backend.py:251-256`, then its error return). The implementer recorded this in the Phase 5 Issues. The user sees a failure but not the cause.
3. **A generic Pandoc runner lives under an arXiv private name.** The non-arXiv whole-page fallback imports the private `_run_pandoc` from `arxiv_html` and catches `ArxivConversionError` for ordinary web pages (`web_backend.py:22-31`, `:153-159`). One runner (D6) is right. But its name and error type say "arXiv", and a private name is crossing modules. Make it public (`run_pandoc`) with a neutral error, or document the choice.
4. **The two routes produce slightly different text for the same paper.** The web route sanitizes the article slice (`web_backend.py:244-247`); the PDF route does not. Live, that gave 244,277 vs 244,110 chars. The design chose this (D17a), and each route is tested on its own, so nothing hides it. It is still worth knowing when comparing outputs.
5. **A small docs inaccuracy.** `docs/extraction-internals.md` says the Pandoc configuration is "in `convert_article`, the only place Pandoc runs for arXiv or the web fallback." The flags live in `_run_pandoc` (`arxiv_html.py:204-213`), which both `convert_article` and `_fallback_pandoc` call. Name `_run_pandoc` as the owner of the flags.
6. **The web route builds its `ArxivSource` late.** It selects from `fetched.text()` (`web_backend.py:243`), then builds `ArxivSource.from_fetch(fetched)` only for the image base at Step 4a (`:333-338`). The PDF route builds one source and uses it for both (`pipeline.py:236-270`). Building it once at the top of the arXiv branch would make the two routes read the same way.
7. **`detect_arxiv_id` has no in-repo caller.** It is kept as a public wrapper (`pandoc_convert.py:123-128`). Design D2 chose this for external callers, so this is a note, not a defect.

## Findings Detail

### Plan completion

All phases (0–8) were verified complete. Every step and validation box is ticked, and each has an Implementation Notes entry with its deviations recorded. The unticked boxes at `plan.md:56-60` are the per-phase template, not a phase. I found no TODOs, placeholders or dead code in the changed source. `test_web_images.py` was deleted after its cases moved, as planned.

### Spec conformance

- **R1 figures.** Met. Both routes call `persist_images` (`pipeline.py:268-273`, `web_backend.py:333-340`). A URL repeated in the page is fetched once and saved as one file. On failure, every ref to it stays as written and one warning is added (`arxiv_html.py:322-363`). Local HTML resolves through a `file://` base and `<base href>` (`arxiv_html.py:67-91`, `:304-311`). `image_count` is the number of files saved. The count reaches `metrics.json` and the summary line on both routes. The no-images-dir limitation is documented. Live: 19 of 19 figures on both routes. Gap: Advisory 1.
- **R2 identity.** Met. Only the margin stamp and an arxiv.org source URL count, and a conflict between them warns and falls back (`pandoc_convert.py:45-120`). `--html-path` remains an override. `--check` applies the same rule and reports `len(markdown)` (`check.py:333-372`).
- **R3 opt-out.** Met. The default is written once, in `ARXIV_SHORTCUT_DEFAULT = True` (`pandoc_convert.py:22`). The help text reads it. The opt-out returns before any identity, probe or Pandoc work (`pipeline.py:216-217`). The contradiction with `--html-path` fails in the CLI (exit 2, `extract_cli.py:368-374`) and in Python (`ValueError`, `pipeline.py:170-175`). The flag reaches local PDFs, PDF URLs, batches and `--check`. The batch PDF-URL recursion bug (pre-existing) was fixed along the way. The owner gate stays open, shipped on, as the owner asked.
- **R4 paper only.** Met as written: an exact `<article class="ltx_document">` selection that fails closed (`arxiv_html.py:135-156`). SVG `<object>` figures are rewritten to `<img>` (D17). Whole-page Pandoc never runs for arXiv (`web_backend.py:262-265`). Live: 0 chrome hits on both routes. The written requirement's premise conflicts with the owner goal: see Blocker 1.
- **R5 fallbacks.** Met. Every PDF-route fallback warns, and opt-out and "doesn't apply" stay silent (`pipeline.py:183-252`). The web fallback warns and keeps `backend: trafilatura`. Warnings reach the result, `metrics.json` (written for error results too) and stderr through one helper (`extract_cli.py:174-180`). Raw bytes and the hash are the fetched page on both routes. The provenance tests pass.
- **Reserved interfaces.** Held. The diff only adds `PipelineConfig.pdf_source_url`, `PipelineConfig.arxiv_shortcut`, `PipelineResult.warnings`, `ProbeResult.arxiv_shortcut_applies` and `--[no-]arxiv-shortcut`. Nothing was removed or renamed. Recorded behavior changes: `convert_arxiv_html` raises `ArxivConversionError` instead of `CalledProcessError`, and web warnings moved from stdout to stderr. Both are documented.
- **Non-goals.** Respected: no OCR, no general boilerplate removal, no version-policy change, no personal-os edits.

### Design conformance

The implementation follows the design, including amendments D17 and D17a and the D14 note. Invariants 1–11 hold. I spot-checked them in code: the raw bytes are hashed, not the slice; `arxiv_html.py` has no import of `pandoc_convert`; there is one Pandoc flag list; the default appears in one place; whole-page Pandoc is skipped for arXiv. The deviations are all recorded with reasons in the plan:

- `convert_article` now takes the article fragment, with `extract_article` split out for D17a.
- `persist_images` takes its fetcher as a required argument.
- The fixture is 115 KB, over the ~80 KB aim.
- The exception contract changed earlier than planned.

### Code integrity

The new module is cohesive. The routes share loading, selection, conversion and persistence, with no copied logic between them. The broad `except Exception` blocks at base were narrowed to named failures (`pipeline.py:250`, `web_backend.py:156`). `probe_pandoc` keeps its `except Exception`; it reports FAIL, as at base. Findings: Advisory 1–7.

**Tests.** The tests use real HTML: a trimmed real arXiv page, run through real Pandoc. The PDFs are generated with pymupdf and read by the real detector. Stubs sit at `fetch_url`, `fetch_image`, `subprocess.run` and `urlopen`. There are two exceptions, both justified: the CLI forwarding tests stub `extract_pdf` (they test plumbing, and real-PDF CLI tests also exist), and one provenance test stubs `extract_article` because its small fixture has no article. Each route has its own nine-figure acceptance test through a shared helper (`tests/helpers/arxiv_page.py`). No test passes by picking one route.

### Phase 8 follow-ups (assessed as asked)

1. **The title logo is not saved.** This is a follow-up, not a defect. The logo is a relative `<img>` inside a LaTeXML `<svg>` picture. Pandoc turns that picture into one `data:` URI, so no markdown ref to the logo ever exists. R1 covers the paper's figures, and this is a decoration. It is tied to Blocker 1: if the owner picks "externalize," the saved `.svg` would still point at an unresolved `harnessmind_logo.png`. That needs its own small fix, or acceptance.
2. **PDF-URL provenance: the source names the PDF, the hash covers the HTML.** This predates the branch, as claimed. R5 is not violated. I checked against `8b027bbc`:
   - The frontmatter precedence `source_url_override or result.source_url` is identical at base (`extract_cli.py:515` at base, `:554` now).
   - At base, the shortcut hashed the fetched HTML bytes (`compute_source_hash(raw_bytes)`). The base page-1 regex also matched the arXiv stamp, so arXiv PDF URLs already took the shortcut and produced this mismatch.
   - The branch hashes the same original fetched bytes (`pipeline.py:280`), never the article slice. That is exactly what R5 protects.
   - One nuance: URL-only evidence now lets stampless PDFs from arxiv.org take the shortcut too, so slightly more PDFs reach this state. The shape is unchanged.

   It belongs with the filed extraction-provenance work. Recording the fetched HTML version for PDF URLs (`PipelineResult.source_url` is computed but dropped by the CLI) would fix it.

---

## Certification

**What I checked:**

- I read the spec, the design (with D17, D17a and the D14 amendment), the plan and its notes, and the earlier product-lens ledger.
- I reviewed the full source diff for `arxiv_html.py`, `pandoc_convert.py`, `pipeline.py`, `types.py`, `web_backend.py`, `check.py`, `extract_cli.py` and both docs.
- I ran the full suite with Pandoc 3.1.3 and `SYSIDE_LICENSE_KEY`: 2909 passed, 3 failed, 1 skipped, 14 deselected, 1 xfailed. The 3 failures are the known baseline: PIL and two `test_index.py` hard-coded paths. Focused extraction suites: 402 passed, none skipped, so real Pandoc ran.
- `ruff check` is clean on touched files. mypy is at its 97-error baseline, none in touched modules.
- I compared the data URIs in the base investigation output and the Phase 8 live output, and reproduced the `ValueError` escape.
- I checked the public-interface reservation and the R5 provenance claim against `8b027bbc`.
- I appended the product-lens verdict to `product-lens.md`.

**What I marked:**

- Plan phases 0–8 were already ticked by the implementer, and I verified them; no boxes changed.
- The spec has no checkboxes to mark.
- There is no parent epic.
- I updated `CURRENT_WORK.md` to "needs work".

**Not checked:**

- I did not re-run the Phase 8 live network check. I used its recorded outputs in `/tmp/harness2-*`.
- I did not run the slow corpus tests.
- I did not test the narrowed-except finding for `IncompleteRead` against a live chunked server.
- I did not check behavior on arXiv layouts other than the three saved reference pages.
- I did not exercise Windows `file://` path handling.
- I did not review the personal-os consumer code.

---

## Round 2

**Verdict:** Needs Work (docs only: three stale sentences; the code is certifiable)
**Audited:** 2026-10-18
**Commit:** `2e4ff5a4` (round-2 changes `ec75552a..2e4ff5a4`)

### Summary

The round-1 must-fix is resolved in code, and so are the five suggestions taken. The new code meets the bar:

- It reads like its neighbors.
- The two routes share one image path.
- Every new except names its exceptions.
- The tests run real HTML, real Pandoc and real `data:` payloads.

One thing is left. Three sentences in the docs still describe the old behavior. They tell readers that `data:` images are never touched and nothing inside the article is removed. That is the opposite of what the code now does, on exactly the point the consumer relies on. The fix is docs only, and a targeted re-check of those lines is enough to certify.

### Round-1 must-fix: in-article `data:` links (resolved in code)

The orchestrator chose to externalize them, as design D18 `[AGENT]`, which was the round-1 recommendation. The owner never ruled. D18 meets the owner's verbatim done-condition ("stop stripping data: images") and drops no paper content, so the conflict is gone. It no longer needs an owner decision.

- **How it works.** `persist_images` treats a `data:` ref as one more image source (`arxiv_html.py:322-354`, `:384-393`, `:403-441`). It decodes the payload, writes it once under a content-hash name, and rewrites every occurrence. An undecodable payload stays inline with one warning, and the warning cuts the payload to 40 characters. `saved_count` counts distinct files.
- **Live evidence (`/tmp/harness2-d18-*`, which I re-inspected).** Both routes have 0 `data:` occurrences in `output.md`. Each has 31 files, made of 19 figures plus 12 in-article pictures, with `image_count` 31 and no warnings.
- **Spec correction.** The wrong evidence line at `spec.md:29` is corrected with a dated note.
- **A falsified bet (B3), handled properly.** D18's live rerun found 6 more `data:` links. They were `data:text/plain` copies attached to LaTeXML's code-listing download buttons, about 36 KB. `extract_article` now drops exactly that button shape (`arxiv_html.py:48`, `:200`). The design records the falsification. I checked that nothing is lost: I decoded all 6 payloads from `ref/2610.14224.html` and searched for their lines in the live output. Every line I spot-checked is present, and the only differences are Markdown escaping (backticks become quotes, `<` becomes `\<`). The listing text renders inline, so the button was pure duplication.

### Taken suggestions

| # | Round-1 suggestion | Status |
|---|---|---|
| 1 | Image failures crash the run | Resolved. `_IMAGE_FAILURES = (OSError, ValueError, http.client.HTTPException, ImageFetchError)` (`arxiv_html.py:386`), named, not bare. Ref resolution moved inside the `try`, which catches my round-1 reproducer `http://[::1/x.png`. Tests cover `ValueError`, `IncompleteRead`, `RemoteDisconnected`, a timeout, and an `IncompleteRead` through the PDF route |
| 2 | A web double failure loses the reason | Resolved. The error result carries `extraction_warnings` (`web_backend.py:286`), and the CLI FAIL branch prints them (`extract_cli.py:258`). Tested at both layers |
| 3 | A generic runner wears an arXiv name | Resolved. The public `run_pandoc` raises a neutral `PandocError` (`arxiv_html.py:51`, `:209`). `convert_article` re-raises it as `ArxivConversionError` with the cause chained, so arXiv callers are unchanged. No private name crosses modules |
| 5 | Docs name the wrong owner of the Pandoc flags | Resolved (`docs/extraction-internals.md:310-314`) |
| 6 | The web route builds its `ArxivSource` late | Resolved. One `source` feeds both the article and `image_base` (`web_backend.py:244-253`), the same shape as the PDF route |
| 4, 7 | Route sanitize asymmetry; `detect_arxiv_id` shim | Left deliberately, as recorded. Both are notes, not defects |

The web char-count fix is also correct. Images are now saved on the body before frontmatter (`web_backend.py:325-343`), and `compute_metrics(markdown)` runs after that (`:355`). The web and PDF routes now count the same thing: the body as written. A test pins `metrics.json` against `output.md`.

### Blockers

1. **Docs contradict the code on `data:` images and article cleanup.** The spec's Completion section requires the behavior to be documented, and these sentences describe the old behavior:
   - `docs/extraction-internals.md:316` says "`data:` URIs are never touched." In fact, with an images directory they are decoded and saved under `images/<hash>.<ext>`.
   - `docs/extraction-internals.md:306` says "Nothing inside it is removed." In fact, LaTeXML listing download buttons are removed (B3).
   - `docs/extraction.md:107` says in-article "`data:` URIs are kept" and that figures are "downloaded". The consumer-facing statement should say that in-article `data:` images are saved to `images/` as files, so `output.md` has no `data:` links when an images directory is configured. It should also say that, without an images directory, they stay inline.

   Impact if unaddressed: a consumer reading the docs would conclude it still needs its `data:` stripping workaround. Undoing that workaround is the point of this item. Fix: amend those three sentences. A targeted re-check is enough.

### Advisory (new code)

1. **The spec's R4 wording is now out of date.** It says "Cleanup removes nothing inside the recognized paper container for being a data URI" (`spec.md:77`). That still holds for images, which are saved rather than removed. But the listing-button removal deletes a `data:` link inside the container. It is removed because it is a duplicate UI button, not because it is a data URI, so the spec's letter holds. A one-line amendment to R4 naming the B3 exception would keep the spec honest. This is an `[AGENT]` decision, surfaced in the plan and accepted by the orchestrator. The owner hasn't seen it, but it serves the owner's goal of no `data:` links.
2. **The listing-button regex depends on exact markup** (`arxiv_html.py:48`). It matches only the literal `<div class="ltx_listing_data"><a …>…</a></div>`. If LaTeXML changes its attribute order or whitespace, the buttons would come back, about 36 KB of `data:text/plain` per paper. Nothing would warn, because `persist_images` only sees image refs. The fixture test pins today's shape. This is low risk and a reasonable trade for a narrow removal. A test asserting that no `data:` text remains on the full fixture would catch drift. The image helper checks only `data:image`.
3. **`ValueError` is now caught across the whole per-ref block** (`arxiv_html.py:420-431`). That covers resolve, decode, read and write. It is named and documented, but a real programming error that raises `ValueError` inside this block would become a warning instead of a crash. The trade is acceptable given the R1 rule that every failure warns, but note it.

### Verification

- **Full suite** (Pandoc 3.1.3 on PATH, `SYSIDE_LICENSE_KEY` set): 2928 passed, 3 failed, 1 skipped, 14 deselected, 1 xfailed. The 3 failures are the known baseline: PIL and two `test_index.py` hard-coded paths.
- **Focused extraction suites:** 421 passed, none skipped.
- **Lint and types:** `ruff check` is clean on every touched file, the touched new files are formatted, and mypy is at its 97-error baseline.
- **Tests stub only at the network and subprocess boundaries,** and the new `data:` tests use real base64 and percent-encoded payloads.

### Certification (round 2)

**Checked:**

- The source and docs diff `373a34df..2e4ff5a4`.
- The plan's "Post-audit fixes" notes and the D18 and B3 entries in the design.
- The spec correction.
- The live D18 outputs: `data:` counts, file counts, and listing text survival against the decoded payloads.
- Both test suites, lint and types.

**Marked:** nothing new. The plan phases were already ticked and the spec has no checkboxes. `CURRENT_WORK.md` is updated, and the product-lens ledger has a round-2 note.

**Not checked:**

- I did not re-run the live network check; I used the recorded `/tmp/harness2-d18-*` outputs.
- I did not run the slow corpus tests.
- I did not check arXiv layouts beyond the saved reference pages.
- The title-logo follow-up and the owner's default-on gate stay open, and neither blocks.
