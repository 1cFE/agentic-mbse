# Design: Reliable arXiv extraction

**Work item:** ARXIV-EXTRACTION
**Status:** Draft (revised after design review)
**Owner:** Reid Westwood
**Created:** 2026-10-18
**Revised:** 2026-10-18 (incorporates `design_review.md` Resolutions)
**Branch:** `fix/arxiv-extraction` at `5abcbd46`

## Overview

The arXiv shortcut fires only on trusted own-ID evidence. It and the direct HTML route convert only the paper's article element, save its images locally, and report every fallback in the result. One new module holds the HTML-to-markdown path both routes share.

## Related Artifacts

- Spec: `.project/active/arxiv-extraction/spec.md`
- Spec review and resolutions: `.project/active/arxiv-extraction/spec_review.md`
- Design review and resolutions: `.project/active/arxiv-extraction/design_review.md`
- Spike, including the paper-container addendum: `.project/active/arxiv-extraction/spike-margin-stamp.md`
- Saved real pages (untracked, fetched 2026-10-18): `.project/active/arxiv-extraction/ref/` (`1706.03762.html`, `2310.06825.html`, `2610.14224.html`)
- Prior designs this builds on: `.project/completed/20260705_web-extraction-quality/design.md` (Pandoc arXiv route), `.project/completed/20260705_arxiv-latest-version/` (latest-version fetch), `.project/completed/20260705_extraction-provenance/` (raw bytes, hash)
- Rules: `.claude/rules/` (capture-fidelity, working-voice, markdown-formatting).
- No `.project/adr/` exists in this worktree, so there are no prior decision records to check.

## The Point

**[NEED]** Downstream consumers can keep Pandoc on PATH safely. That means no citation substitution, no missing figures and no arXiv chrome in output. Their workarounds (hiding Pandoc from PATH for PDFs, stripping data-image references) then become unnecessary.

Today Pandoc on PATH is a hazard. A PDF that merely cites an arXiv paper can be replaced by that paper. A correct substitution loses its figures. The direct HTML route converts arXiv's whole page, so issue dialogs, navigation, footers and UI icons land in the output. When the shortcut gives up, the user can't see why. Every later stage checks against one test: a consumer runs `extract` with Pandoc on PATH, no workarounds, and gets the right paper, its figures on disk, and nothing but the paper.

## Research Findings

**The shortcut** (`pipeline.py:172-226`). It returns early, before PDF image extraction (`pipeline.py:380-386`). It decides identity with `detect_arxiv_id` (`pandoc_convert.py:71-105`): the first `arXiv:` regex hit anywhere in page-1 text, then a Creator-metadata fallback. Every exception is logged at `debug` and dropped (`pipeline.py:224-226`). An ignored `--html-path` is silent (`pipeline.py:188-189`).

**Three copies of the Pandoc call.** `convert_arxiv_html` (`pandoc_convert.py:187-263`) fetches with bare `urllib` or reads a file, then preprocesses and runs Pandoc. `_extract_with_arxiv_pandoc` (`web_backend.py:246-295`) repeats the same preprocessing and flags. `_fallback_pandoc` (`web_backend.py:298-333`) repeats the flags a third time. Comments warn that they must stay in sync.

**Image download exists, web route only.** `_download_arxiv_images` (`web_backend.py:58-150`) rewrites `![alt](url){attrs}` refs in Pandoc markdown to `images/<name>`, skips `data:` URIs, caps size, and warns on failure. It downloads a repeated URL twice (`x1.png`, `x1_2.png`, `web_backend.py:109-118`). It resolves root-relative refs against `https://arxiv.org` and collapses `//`. Relative refs resolve with `urljoin(page_url, ref)` (`web_backend.py:101`). Its tests (`tests/test_web_images.py`) patch `web_backend.urllib.request.urlopen`.

**Output layout is shared.** Both routes write markdown into an output directory and images into `<output>/images/`, referenced as `images/<name>`. The web route uses `output_dir / "images"` (`web_backend.py:76`). The PDF CLI sets `extracted_images_dir = output_dir / "images"` (`extract_cli.py:484-496`). `ImageCollector` writes `images/<rel_name>` refs (`pipeline.py:73-76`).

**Warnings have no PDF channel.** `PipelineResult` (`types.py:107-124`) has no `warnings` field. The PDF CLI writes `metrics.json` from `metrics.to_dict()` alone (`extract_cli.py:531`). An error result skips all output at `if result.error: ... continue` (`extract_cli.py:502-505`). `_print_pipeline_summary` (`extract_cli.py:171-188`) prints no warnings. The web route returns `ExtractionResult.warnings` (`base.py:28`), adds them to `metrics.json` (`web_backend.py:509-511`), and prints them to stdout (`extract_cli.py:240-243`). Its arXiv fallback only logs (`web_backend.py:416`). When trafilatura returns under 100 characters, it converts the whole page with `_fallback_pandoc` (`web_backend.py:423-432`).

**The source URL is already known.** `_extract_pdf_url` stores `fetched.final_url` on `args.source_url_override` (`extract_cli.py:273`), and only the frontmatter uses it. PDF URLs and batch URLs re-enter `cmd_extract` with a shallow copy of `args` (`extract_cli.py:271-274`), so new flags reach them without extra plumbing.

**`--check` has its own path.** `probe_pandoc` (`check.py:328-346`) calls `detect_arxiv_id`, `check_arxiv_html` and `convert_arxiv_html` directly, and reports `len()` of the returned tuple. `compute_capabilities` sets `arxiv_shortcut` when the substring `"arXiv"` appears in the probe detail (`check.py:416-431`). `ProbeResult` is a plain dataclass (`check.py:63-69`).

**Dependencies.** BeautifulSoup and lxml are in the optional `[web]` extra (`pyproject.toml:36`). The PDF shortcut runs on a core install, so shared code on its path can't depend on them.

**Real page structure** (spike addendum, design review, `ref/`). Each saved page has exactly one `<article` tag, and its class includes `ltx_document`. On `ref/2610.14224.html` every `<button>`, `<dialog>` and header `<nav>` sits before the article (lines 71–184). The article spans lines 242–4484. Footers and funder logos sit after it. The page's one `data:` image sits outside the article. Inside the article, `aria-hidden` appears only on two icon-font spans in a link (lines 306, 308). Paper figures are relative refs like `2610.14224v1/intro_teaser.png`, which resolve against `/html/`. No page has a `<base href>`.

**Existing arXiv fixture** `tests/fixtures/arxiv_1706.03762_latest.html` is 1 KB of figure tags with no chrome. It is fine for version tests and does not represent page structure.

**Margin stamp** (spike, `[AGENT]` verified on 3 real PDFs): pymupdf `get_text("dict")` returns the stamp as one line with `dir == (0, -1)`, `x1 ≤ 44` pt, text `arXiv:<id>v<N>  [<cat>]  <date>`. Prose citations come out horizontal. Creator metadata is useless.

## Core Concept

The design makes three decisions explicit where today they are implicit, and it routes each one through a single function that both routes call.

1. **Is this PDF the arXiv paper?** Only a trusted source can answer: the rotated margin stamp on page 1, or the arxiv.org URL the PDF came from. Prose never counts. If the sources disagree or there are none, the answer is no, and normal PDF extraction runs.
2. **What part of the HTML is the paper?** The paper is the one `<article class="ltx_document">` element that LaTeXML emits. Everything arXiv wraps around it is chrome. Selecting that element *is* the chrome removal; nothing inside it is filtered. If the element is missing or ambiguous, the conversion fails, and the route takes its existing fallback.
3. **Where do the figures live?** Every image ref in the converted markdown is resolved against one base URL and fetched or copied once into `images/`. The base is the URL that served the page, or a `file://` URL for a local HTML file, with `<base href>` applied on top. One loader produces that base for both routes. Refs that can't be saved stay as written and produce one warning each.

Each decision that ends in a fallback produces a warning string. The warning travels in the returned result and is saved to `metrics.json` and printed to stderr. That is the same channel for both routes, extended to `PipelineResult`.

This is the right shape because each of the spec's failures comes from one of these decisions made badly or twice. Substitution came from a weak identity test. Missing figures came from image persistence living only in the web route. Chrome came from converting the whole page. Silence came from fallbacks that returned `None`. Making one function own each decision fixes the failure in both routes at once, and it gives tests one pure function per decision to hit with real bytes.

Module split: `arxiv_html.py` owns the whole HTML-to-markdown path (load, select, convert, persist images). `pandoc_convert.py` owns the PDF side (identity, the shortcut default, the HTML-availability probe, version helpers) and keeps `convert_arxiv_html` as a wrapper that delegates to `arxiv_html`. Imports run one way: `pandoc_convert` may import `arxiv_html`, and `arxiv_html` never imports `pandoc_convert`.

Existing pieces it composes with: `check_arxiv_html` and the version helpers (unchanged); `_preprocess_html` and `_postprocess_markdown` (moved unchanged, now applied to the article only); `_download_arxiv_images` (moved and generalized); `strip_hidden_content` (still the web route's pre-pass); `fetch_url` (the HTML network boundary); the `images/` output layout and the `metrics.json["warnings"]` convention.

## Key Bets

- **B1. Real arXiv HTML holds the whole paper, and only the paper, inside exactly one `<article>` whose class includes `ltx_document`.** Title, authors, abstract, sections, bibliography and appendices sit inside it. Header, navigation, issue dialog, footers and funder logos sit outside it. `[AGENT, verified: spike addendum on 3 pages; design review on ref/2610.14224.html]` *If false on some future page → selection drops paper parts or keeps chrome. The selection test on the pinned fixture guards the known shape, and an unrecognized shape falls back with a warning.*
- **B2. arXiv-served PDFs carry the margin stamp as text pymupdf can read, and other PDFs essentially never contain a rotated left-margin line in the full stamp shape.** `[AGENT, spike on 3 papers]` *If false → either genuine papers stop substituting (acceptable, spec R2) or a non-arXiv PDF substitutes. The second case needs a rotated line matching `arXiv:<id>v<N> [<cat>] <date>`, which body text or a citation would not produce.*
- **B3. arXiv's UI elements are absent from inside the article in the served HTML.** `[AGENT, verified on ref/2610.14224.html: every button and dialog sits before the article; inside it only two aria-hidden icon-font spans in a link]` *If false → small UI strings leak into output. The fixture assertions catch it, and the fix is one targeted removal in the selection step, not a new mechanism.*
- **B4. Pandoc markdown image refs (`![alt](src){attrs}`) are the complete set of figures that need saving.** Persistence works on converted markdown, as it does today. Alt text containing `]` would not match the ref pattern; LaTeXML figures use `alt="Refer to caption"`, so this is unlikely for arXiv. *If false (a figure shows up only as raw HTML `<img>`, or with a bracketed alt) → that figure keeps a remote ref. The fixture's figure assertions would show it.* **Falsified 2026-10-18 (Phase 1): figures embedded as `<object type="image/svg+xml">` produce no ref at all; see D17.**
- **B5. arXiv's relative figure refs (`<id>vN/<file>`) resolve correctly against the serving URL `https://arxiv.org/html/<id>[vN]` without a trailing slash.** `[AGENT, ref/ pages; today's web route already depends on it at web_backend.py:101]` The loader strips a trailing slash from arXiv `/html/` URLs rather than trusting it. *If false → every figure resolves to a wrong path, every download fails, and the route warns once per figure.*

## Key Decisions

- **D1. Identity evidence = margin stamp ∪ arxiv.org source URL.** A stamp is a page-1 line that is vertical (`|dir.x| < 0.05`), has `x1` within the left 15% of page width, and fully matches `arXiv:(\d{4}\.\d{4,5})v\d+ \[[^\]]+\] \d{1,2} \w{3} \d{4}` (whitespace-tolerant). A source URL counts when it matches `arxiv.org/(abs|pdf)/<id>[vN][.pdf]`. More than one distinct stamp ID, or a stamp and a URL that name different bare IDs, is a conflict. *Rejected: Creator metadata (useless per spike); a post-fetch title cross-check (extra network work, and B2 makes it redundant; spec makes it optional); exact stamp coordinates (vary by paper).*
- **D2. `identify_arxiv_paper()` replaces the logic inside `detect_arxiv_id`, which stays as a thin wrapper.** It lives in `pandoc_convert.py`, beside the code it replaces. Any external caller of the public `detect_arxiv_id` gets the safe rule. *Rejected: deleting `detect_arxiv_id` (needless break); keeping the old regex for "soft" signals (prose is never evidence).*
- **D3. A new module `extraction/arxiv_html.py` owns the whole HTML-to-markdown path.** That covers the loader, article selection, `_preprocess_html` and `_postprocess_markdown` (moved from `pandoc_convert.py`), the Pandoc runner, `convert_article` and image persistence. `pandoc_convert.convert_arxiv_html` stays where it is, with its signature and return type unchanged, and delegates to `load_arxiv_html` and `convert_article`. `pandoc_convert` may import `arxiv_html`; `arxiv_html` never imports `pandoc_convert`. No public function moves. *Rejected: leaving the HTML helpers in `pandoc_convert.py` (creates an import cycle with `convert_article`); putting the module in `web_backend.py` (the PDF route would import the web backend).*
- **D4. Article selection is a fail-closed string scan.** The page must contain exactly one `<article` opening tag and exactly one `</article>`, and the opening tag's class must include `ltx_document`. The slice from the opening tag through the closing tag goes to Pandoc unchanged. Any other shape raises `ArxivConversionError("no recognized arXiv article container")`. *Rejected: BeautifulSoup (in the `[web]` extra only, and the PDF route must run on a core install); stdlib `html.parser` span tracking (line/column offsets and depth tracking for the same fail-closed outcome); a deny-list of chrome selectors (open-ended, and what R4 warns against).*
- **D5. One failure type, `ArxivConversionError(reason)` in `arxiv_html.py`, covers unrecognized structure, Pandoc missing, Pandoc failure or timeout, and output shorter than `MIN_CONTENT_CHARS = 100`.** Both routes catch it and turn `reason` into a warning. `web_backend` imports `MIN_CONTENT_CHARS` in place of its own `_MIN_CONTENT_LENGTH`. *Rejected: `None` returns (what made fallbacks silent); per-cause exceptions (no caller acts on the difference).*
- **D6. One Pandoc runner `_run_pandoc(html, pandoc_path)` in `arxiv_html.py`.** All three current invocations call it: `convert_article` directly, and the general `_fallback_pandoc` by importing it from `arxiv_html`. `pandoc_convert` no longer runs Pandoc itself. *Rejected: leaving the "keep flags in sync" comments; a separate module just for the runner.*
- **D7. Image refs resolve with `urljoin(base, ref)` against one base URL.** The base is the loader's serving URL: the post-redirect URL for fetched HTML, or `Path(html).resolve().as_uri()` for a local file. A `<base href>` read from the full raw HTML is joined on top. `http(s)` results are downloaded, `file:` results are copied if they exist, and anything else stays as written with a warning. Repeated `//` in the path collapses, as today. This one rule covers every R1 case. A root-relative ref in a local file becomes `file:///…`, which doesn't exist, so it stays put and warns. No arXiv base is guessed. *Rejected: separate code paths per source kind; keeping the hard-coded `https://arxiv.org` prefix (equal to `urljoin` for arxiv.org pages, wrong for local files).*
- **D8. Persistence dedupes by resolved URL.** One fetch per URL, and every occurrence is rewritten to the same file. A different URL with a taken basename gets `stem_N.ext`, as today. A failed URL leaves every occurrence untouched and produces one warning. The saved count is the number of files written. *Rejected: today's one-download-per-occurrence (spec R1).*
- **D9. The image network boundary is one injectable `fetch_image(url, *, max_bytes, timeout) -> bytes`.** It raises on HTTP error and on oversize. Tests stub only this, `fetch_url` for page loads, and `subprocess.run` for Pandoc where Pandoc isn't the subject. *Rejected: patching `urllib.request.urlopen` in a module namespace (couples tests to imports).*
- **D10. Shortcut control is a tri-state `PipelineConfig.arxiv_shortcut: bool | None = None`, with the default in one constant `ARXIV_SHORTCUT_DEFAULT = True` in `pandoc_convert.py`.** `resolve_arxiv_shortcut(explicit: bool | None) -> bool` returns `explicit` when it is set and the constant otherwise. Automatic detection runs when it returns `True`. `arxiv_html_path` is an explicit override, so it runs unless the caller set `arxiv_shortcut=False`. That combination raises `ValueError` in `__post_init__`. The CLI uses `argparse.BooleanOptionalAction` (`--arxiv-shortcut` / `--no-arxiv-shortcut`, default `None`), and its help text names the constant's value. Flipping the owner gate is one line plus one docs sentence, and `--html-path` keeps working either way. *Rejected: a plain `bool` field (if the default flipped to off, every `--html-path` user would also need `--arxiv-shortcut` or hit the contradiction error); `--no-arxiv-shortcut` alone (no way to turn it on if the default flips).*
- **D11. `PipelineConfig.pdf_source_url: str | None = None` carries the URL the PDF came from.** The CLI fills it from `fetched.final_url`. *Rejected: reusing `PipelineResult.source_url`'s name (that field means the HTML provenance).*
- **D12. `PipelineResult.warnings: list[str]` (new).** Shortcut warnings are carried into whichever result `extract_pdf` returns, including the normal-path result and the base-extraction error result. In the PDF CLI branch, warnings are printed and written to `metrics.json["warnings"]` before the `if result.error` branch, so an error result also persists its warnings. One CLI helper prints warnings to stderr for both routes. Web warnings print to stderr only; this design drops their stdout copy. *Rejected: logging alone (spec R1 rules it out); printing web warnings to both streams (two printers would drift).*
- **D13. Which outcomes warn.** Ignored `--html-path`, identity conflict, identified paper with no HTML available, fetch error, `ArxivConversionError`, and each image that wasn't saved all warn. On the PDF route, no evidence, opt-out, and Pandoc absent without `--html-path` don't. Those are the ordinary "shortcut doesn't apply" cases, and every non-arXiv PDF hits one. On the web route, an arXiv URL without Pandoc does warn, deliberately: the user asked for an arXiv page and gets trafilatura output instead. *Rejected: warning on every PDF-route non-firing (noise on every normal PDF).*
- **D14. `--check` reuses `identify_arxiv_paper`, `resolve_arxiv_shortcut` and `convert_arxiv_html`.** It reports `len(markdown)`. The `arxiv_shortcut` capability comes from a new `ProbeResult.arxiv_identified: bool = False` field, not the substring `"arXiv"`, which a "shortcut disabled" detail would also contain. It doesn't download images: it is a probe, not an extraction. *Rejected: running the full shortcut inside `--check` (writes files).*
  - **D14 amendment (2026-10-18, orchestrator `[AGENT]`).** The capability field is `ProbeResult.arxiv_shortcut_applies` (renamed from `arxiv_identified` before release), true only when `extract` would take the shortcut: enabled, paper identified, HTML version available and converted. An identified paper with no HTML version reports the capability false, because `--check` exists to predict `extract` (spec_review L2-3 resolution).
- **D15. One loader, `load_arxiv_html(source, *, timeout) -> ArxivSource`, serves both routes.** For a URL it calls `fetch_url` and builds the result with `ArxivSource.from_fetch`. For a path it reads the file. The web route already holds a `FetchResult` and calls `ArxivSource.from_fetch` directly. `from_fetch` is the one place the serving URL is normalized: a trailing slash on an arXiv `/html/<id>[vN]/` URL is stripped (B5). *Rejected: `convert_arxiv_html` keeping its own bare-`urllib` fetch (its `(markdown, bytes)` return can't carry the serving URL); a separate fetch in the PDF route (a second loader to keep in sync).*
- **D16. For arXiv URLs the whole-page Pandoc fallback does not run.** When article conversion fails, the web route returns the trafilatura result with a warning, even if it is short. If trafilatura returns nothing, the extraction fails as it does today. *Rejected: running `_fallback_pandoc` after a failed article conversion (the only path left that could put chrome in output).*

## Architecture

```
PDF input ─► extract_pdf
              │ arxiv_shortcut False? ───────────────────────────────────┐
              │ html_path given? ─► load_arxiv_html(path) ─┐             │
              │ identify_arxiv_paper(pdf, pdf_source_url)  │             │
              │   none ───────────────────────────────────┼──────────┐  │
              │   conflict ─► warn ───────────────────────┼──────────┤  │
              │   id ─► check_arxiv_html ─► load_arxiv_html(url) ─┐  │  │
              │                                           ▼       ▼  ▼  ▼
              │              ArxivSource ─► convert_article ── fail ─► warn ─► normal PDF pipeline
              │                                  │ ok                                  │
              │              persist_images(md, source.image_base, images dir)          │
              ▼                                  ▼                                     ▼
          PipelineResult(markdown, image_count, warnings, raw bytes, source_url)
              ▼
          CLI: warnings → stderr, metrics.json{warnings}; then output.md, images/ (or FAIL)

arXiv HTML URL ─► fetch_url ─► ArxivSource.from_fetch ─► strip_hidden_content ─► convert_article
                                                                     │ ok          │ fail ─► warn ─► trafilatura (no whole-page Pandoc)
                                                                     ▼
                                              persist_images(md, source.image_base, output/images)
                                                                     ▼
                                              ExtractionResult(warnings) ─► metrics.json, stderr
```

Data flow: raw bytes are hashed and saved exactly as fetched. `convert_article` works on a decoded copy. The base href is read from the full raw HTML, because `<base>` sits in `<head>`, outside the article. Image persistence runs on converted markdown, so it only sees refs from the article. Fetched-version provenance (`resolve_fetched_version`) is computed as today.

Boundaries: `arxiv_html` is pure apart from page loads (through `fetch_url`), Pandoc (through `_run_pandoc`) and image I/O (through the injected `fetch_image` and the filesystem under `images_dir`). Identity is pure over PDF bytes. The HTML-availability HEAD probe stays in `check_arxiv_html`.

## Required Invariants

1. Raw source bytes saved and hashed are the fetched bytes, never the article fragment (R5 `[HARD]`).
2. Every rewritten image ref points at a file that exists under the images directory. Every ref that isn't saved is byte-identical to its Pandoc output.
3. `image_count` equals the number of image files that call wrote.
4. A PDF without trusted own-ID evidence never reaches `check_arxiv_html`, a fetch, or Pandoc. With `arxiv_shortcut=False`, `identify_arxiv_paper` isn't called either.
5. The shortcut substitutes only the ID its evidence names. Prose IDs never enter the decision.
6. Nothing inside the selected article is removed for being a data URI or an image.
7. Every fallback listed in D13 yields exactly one warning in the returned result, `metrics.json`, and stderr, including on a base-extraction error result.
8. `ARXIV_SHORTCUT_DEFAULT` is the only place the default is written in code.
9. No existing `PipelineConfig` field or CLI flag is removed or renamed.
10. `arxiv_html` never imports `pandoc_convert`. Imports between the two run only from `pandoc_convert` to `arxiv_html`.
11. Whole-page HTML never reaches Pandoc for an arXiv URL.

## Component Overview

- **`extraction/arxiv_html.py` (new).** The HTML-to-markdown path: `ArxivSource`, `load_arxiv_html`, `select_article`, `convert_article`, `persist_images`, `ImagePersistResult`, `fetch_image`, `ArxivConversionError`, `MIN_CONTENT_CHARS`, plus the moved `_preprocess_html`, `_postprocess_markdown` and the new `_run_pandoc`. Signatures are in Implementation Notes.
- **`extraction/pandoc_convert.py`.** The PDF side: adds `identify_arxiv_paper`, `ArxivIdentity`, `ARXIV_SHORTCUT_DEFAULT` and `resolve_arxiv_shortcut`. `detect_arxiv_id` becomes a wrapper. It keeps `_pandoc_available`, `check_arxiv_html`, `strip_arxiv_version` and `resolve_fetched_version`. `convert_arxiv_html` keeps its signature and becomes a wrapper over `arxiv_html.load_arxiv_html` and `arxiv_html.convert_article`. The private `_preprocess_html` and `_postprocess_markdown` move to `arxiv_html`.
- **`extraction/pipeline.py`.** New `PipelineConfig` fields `arxiv_shortcut` and `pdf_source_url`, plus `__post_init__` validation. `_try_arxiv_shortcut` returns `(result | None, warnings)`. It loads through `load_arxiv_html`, converts with `convert_article`, persists images into `extracted_images_dir` against `source.image_base`, and sets `image_count`. `extract_pdf` attaches shortcut warnings to every result it returns.
- **`extraction/types.py`.** `PipelineResult.warnings`.
- **`extraction/web_backend.py`.** The arXiv branch builds an `ArxivSource` from its fetch, calls `convert_article` and `persist_images`, and turns `ArxivConversionError` into a fallback warning. It skips `_fallback_pandoc` for arXiv URLs (D16). `_download_arxiv_images`, `_extract_with_arxiv_pandoc` and `_MIN_CONTENT_LENGTH` go away. `_fallback_pandoc` calls `arxiv_html._run_pandoc`.
- **`extraction/check.py`.** `ProbeResult.arxiv_identified`. `probe_pandoc(pdf, *, arxiv_shortcut)` and `run_check(..., arxiv_shortcut)` follow D14. `compute_capabilities` reads the new field.
- **`cli/extract_cli.py`.** Adds the `--arxiv-shortcut/--no-arxiv-shortcut` flag. It reports a usage error (exit 2) when `--no-arxiv-shortcut` and `--html-path` are both given. It fills `pdf_source_url` from `source_url_override`, passes the flag to `run_check`, and prints and persists warnings before the error branch (D12) through one stderr helper.
- **Docs.** `docs/extraction.md`: automatic substitution, the evidence it needs, the escape hatch, the default, and the programmatic no-images-dir limitation. `docs/extraction-internals.md`: the module split and the supported container.
- **Fixtures.** `tests/fixtures/arxiv_2610.14224v1_page.html` (trimmed real page, see Implementation Notes). PDFs are generated in tests with pymupdf.

## Non-Goals

- General website boilerplate removal and non-LaTeXML arXiv layouts.
- Recovering genuine papers that lack a stamp or arXiv URL (publisher or author builds).
- Old-style arXiv IDs (`hep-th/9901001`). The current regex doesn't support them either.
- Changing latest-version selection, OCR, or PDF figure quality.
- Image download in `--check`, and image persistence when no images directory is configured.
- Changes to personal-os.

## Implementation Notes

- **Fixture trim.** Start from `ref/2610.14224.html` (untracked local copy, fetched 2026-10-18). If it's gone, re-fetch the pinned `https://arxiv.org/html/2610.14224v1`. Keep `<head>` (meta generator, title) and every chrome element outside the article verbatim: header, navigation, issue dialog, footers, funder logos, the data-URI icon. Repeated list items may be shortened. Inside the article keep the title, authors, abstract, two sections that between them hold at least two figures with captions, one table and one math element, two bibliography entries and one appendix. Delete the other sections. Insert one tiny `data:image/png` `<img>` inside the article, marked by an HTML comment as the only synthetic edit. Open with a comment naming the source URL, fetch date and edits. Aim under 80 KB.
- **Stamp fixtures.** Generate them with `page.insert_text((x, y), "arXiv:2610.14224v1  [cs.AI]  9 Oct 2026", rotate=90)` at x ≈ 30. Generate four PDFs: a citation-only PDF, a stamp plus a cited prose ID, two different stamps, and a stamp that disagrees with `pdf_source_url`. Assert the actual `dir` in one test, so a pymupdf change shows up there.
- **Selection scan.** Match `<article` case-insensitively and only when followed by whitespace or `>`, so `<articles` doesn't count. Count openings and `</article>` closings over the whole page. Read the class from the one opening tag.
- **Wrapping the fragment for Pandoc.** Write `<html><body>{article}</body></html>` with UTF-8. Pandoc doesn't need `<head>`, and keeping it out means the page `<title>` can't reach the body.
- **Test migration.** Move `tests/test_web_images.py` cases to `tests/test_arxiv_html.py` against `persist_images` with a stubbed `fetch`. Rewrite the duplicate-URL expectation to one file. Tests that import `_preprocess_html` or `_postprocess_markdown` from `pandoc_convert` switch to `arxiv_html`. Imports of `convert_arxiv_html` stay as they are. Tests in `test_pipeline.py` that stub `detect_arxiv_id` change to stub `identify_arxiv_paper`, or to use generated PDFs.
- **Web stdout to stderr.** Existing CLI tests that read web warnings from stdout need updating.

```python
class ArxivConversionError(Exception): ...           # str(exc) is the warning reason

@dataclass(frozen=True)
class ArxivSource:
    raw_bytes: bytes      # exactly as fetched or read
    html: str             # decoded raw_bytes
    serving_url: str      # post-redirect http(s) URL, trailing slash stripped; or file:// URI
    @property
    def image_base(self) -> str: ...                  # serving_url joined with <base href>, if any

@dataclass(frozen=True)
class ImagePersistResult:
    markdown: str         # refs rewritten for saved images only
    saved_count: int      # files written
    warnings: list[str]   # one per URL not saved
```

```python
def load_arxiv_html(source: str | Path, *, timeout: int = 30) -> ArxivSource: ...
def select_article(html: str) -> str | None: ...
def convert_article(html: str, pandoc_path: str = "pandoc") -> str: ...   # raises ArxivConversionError
def persist_images(markdown: str, base: str, images_dir: Path, *, fetch=fetch_image) -> ImagePersistResult: ...
def fetch_image(url: str, *, max_bytes: int = 10 * 1024 * 1024, timeout: int = 15) -> bytes: ...
```

```python
@dataclass(frozen=True)
class ArxivIdentity:      # pandoc_convert.py
    arxiv_id: str | None          # e.g. "2610.14224v1"; None = don't substitute
    evidence: tuple[str, ...]     # ("stamp",), ("url",), ("stamp", "url")
    conflict: str | None = None   # reason when sources disagree; if set, arxiv_id is None

def identify_arxiv_paper(pdf_path: Path, pdf_source_url: str | None = None) -> ArxivIdentity: ...
def resolve_arxiv_shortcut(explicit: bool | None) -> bool: ...
def convert_arxiv_html(html_source: str | Path, pandoc_path: str = "pandoc") -> tuple[str, bytes]: ...  # unchanged signature; delegates
```

## Potential Risks

- **A future page breaks B1** (for example, newer LaTeXML wraps the paper differently). Mitigation: unrecognized structure falls back with a warning, so output is never worse than PDF extraction or trafilatura. The live audit run checks the current page.
- **Shortcut hit rate drops**, because author and publisher PDFs no longer substitute. The spec accepts this. The docs say so.
- **Output on stdout changes.** Web warnings move to stderr. The spec requires stderr output; dropping the stdout copy is this design's choice (D12).
- **New warning on Pandoc-less machines.** Every arXiv web extraction without Pandoc now warns (D13).

## Integration Strategy

The change replaces internals behind existing entry points: `extract_pdf`, `extract_web_content`, `convert_arxiv_html` and `run_check`. Public additions are `PipelineConfig.arxiv_shortcut`, `PipelineConfig.pdf_source_url`, `PipelineResult.warnings`, `ProbeResult.arxiv_identified`, `--arxiv-shortcut/--no-arxiv-shortcut`, and the `arxiv_html` module. `convert_arxiv_html` keeps its module and signature. Callers that construct `PipelineConfig()` today get the same automatic behavior as before, under the safer identity rule. Downstream consumers drop their workarounds as separate work.

## Validation Approach

| Spec criterion | Test |
|---|---|
| Figures are portable | Real fixture through both routes, stubbed `fetch_url` and `fetch_image`, serving URL in the real `https://arxiv.org/html/<id>` shape: files exist under `images/`, refs are relative, counts match. One case serves the page from a trailing-slash URL and still resolves figures correctly |
| Failures are honest | `persist_images` with a failing URL, an oversized URL, a URL used twice, and two URLs sharing a basename. CLI test asserts warnings in `metrics.json` and stderr for both routes, including a PDF base-extraction error |
| Local HTML images resolve | Temp dir with an HTML file holding absolute, `<base href>`-relative, file-relative and missing refs |
| Citations cannot substitute | Generated PDFs through the real `identify_arxiv_paper`. Negative and conflict cases assert `check_arxiv_html` and the converter are never called. The stamp case substitutes |
| `--check` predicts `extract` | Citation-only PDF: no identification, no network, `arxiv_identified` false. `--no-arxiv-shortcut`: probe skipped and capability false. Character count equals `len(markdown)` |
| Users can force PDF extraction | Opt-out with Pandoc available, contradictory flags (exit 2, `ValueError`), PDF URL and batch forwarding |
| Paper alone, no Pandoc needed | `select_article` on the real fixture: chrome strings (dialog, navigation, footer, funder logos, the page's data-URI icon) are outside the slice; title, abstract, a section heading, bibliography and appendix are inside. Runs in every CI environment |
| Paper alone, through Pandoc | Real fixture through `convert_article` with real Pandoc (skip if Pandoc is absent): chrome strings and UI data URIs absent; title, sections, references, appendix, figure caption, table, math and the in-article data URI present |
| Fallback visible | Pandoc failure, short output, and a page with no article → per-route fallback plus a warning. For an arXiv URL with short trafilatura output, `_fallback_pandoc` is never called. An ignored `--html-path` warns |
| Provenance unchanged | Existing hash, save-source and fetched-version tests pass unchanged |
| Live check | At audit: a bounded Harness² run with Pandoc on PATH, recorded per the spec |

Run `uv run pytest tests/test_arxiv_html.py tests/test_pandoc_convert.py tests/test_pipeline.py tests/test_web_backend.py tests/test_extract_cli.py tests/test_check.py`, `uv run ruff check src/ tests/`, and `uv run mypy src/`.

## Next-Stage Handoff

- **Fixed:** D1–D16, the invariants, the module split, and the tri-state control with the default in `ARXIV_SHORTCUT_DEFAULT`.
- **Open owner gate:** whether the shortcut is on by default (R3). The design ships `True` provisionally. Flipping it changes one constant and one docs sentence.
- **First task:** build the trimmed fixture from `ref/2610.14224.html` and lock in the Pandoc-free selection test on it. The rest of the work builds on that fixture.
- **Plan's choice:** how to order the phases. A suggested order is identity → `arxiv_html` and its fixture → the PDF route → the web route → CLI, check and docs.


## Amendment (2026-10-18, orchestrator `[AGENT]`)

**D17. Rewrite SVG figure objects to images before Pandoc.** Phase 1 found that Pandoc drops LaTeXML figures embedded as `<object type="image/svg+xml" data="…svg" class="ltx_graphics …">`: on 2610.14224, 4 of 9 figures produced no image reference of any kind, only their captions. All three reference pages use this form inside `article.ltx_document` (3, 1 and 4 such objects). The article pre-processing step in `arxiv_html` rewrites each such `<object>` to `<img src="<data>" alt="<object's fallback text or 'Refer to caption'>" …>`, keeping `width`/`height`/`id`/`class`, before Pandoc runs. The figures then become ordinary markdown image refs, and D7 persistence saves them like any other figure. Scope: only `<object>` elements with `type="image/svg+xml"` and the `ltx_graphics` class; other objects are left alone. Rejected: post-processing raw HTML in the markdown, which would need a second persistence path.

---
Next Step: After approval → `/_my_plan`

**D17a (2026-10-18, orchestrator `[AGENT]`). One step order for both routes: select, rewrite, then sanitize.** Phase 5 found that the web route's sanitizer (`html_sanitize.py:36`) deletes every `<object>` before article selection, so D17 alone would fix only the PDF route. The web route now selects the article from the raw fetched page, applies the D17 `<object>` → `<img>` rewrite, and then runs the existing sanitizer on that slice only. The PDF route runs the same select and rewrite steps. Raw-byte saving and hashing are unchanged, because they use the fetched bytes, not the slice. Rejected: teaching the sanitizer to keep `ltx_graphics` objects, which would widen what the sanitizer lets through for every web page.

**D18 (2026-10-18, orchestrator `[AGENT]`, from audit round 1). Externalize in-article `data:` images.** Inline SVG drawings inside the article become `data:image/svg+xml` links after Pandoc (12 on 2610.14224: title graphic, component icons). Consumers strip `data:` links today, and the owner's goal is that they no longer have to. When an image directory is configured, `persist_images` decodes each `data:` image ref, writes it once under `images/` (content-hash filename, extension from the media type), and rewrites every occurrence to the relative path; an undecodable one stays as written with a warning. Without an image directory, `data:` refs stay inline, matching the remote-ref rule. Rejected: dropping them, which loses paper content; accepting them inline, which keeps the consumer workaround.
