# Design: Reliable arXiv extraction

**Work item:** ARXIV-EXTRACTION
**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-10-18
**Branch:** `fix/arxiv-extraction` at `74613d3a`

## Overview

The arXiv shortcut fires only on trusted own-ID evidence. It and the direct HTML route convert only the paper's article element, save its images locally, and report every fallback in the result. One new module holds the HTML-side logic both routes share.

## Related Artifacts

- Spec: `.project/active/arxiv-extraction/spec.md`
- Spec review and resolutions: `.project/active/arxiv-extraction/spec_review.md`
- Spike: `.project/active/arxiv-extraction/spike-margin-stamp.md`
- Prior designs this builds on: `.project/completed/20260705_web-extraction-quality/design.md` (Pandoc arXiv route), `.project/completed/20260705_arxiv-latest-version/` (latest-version fetch), `.project/completed/20260705_extraction-provenance/` (raw bytes, hash)
- Rules: `capture-fidelity.md`, `working-voice.md` and `markdown-formatting.md` live in the main checkout. This session could not read them (permission denied). Grades follow the vocabulary in `spec_review.md`.
- No `.project/adr/` exists in this worktree, so there are no prior decision records to check.

## The Point

**[NEED]** Downstream consumers can keep Pandoc on PATH safely. That means no citation substitution, no missing figures and no arXiv chrome in output. Their workarounds (hiding Pandoc from PATH for PDFs, stripping data-image references) then become unnecessary.

Today Pandoc on PATH is a hazard. A PDF that merely cites an arXiv paper can be replaced by that paper. A correct substitution loses its figures. The direct HTML route converts arXiv's whole page, so issue dialogs, navigation, footers and UI icons land in the output. When the shortcut gives up, the user can't see why. Every later stage checks against one test: a consumer runs `extract` with Pandoc on PATH, no workarounds, and gets the right paper, its figures on disk, and nothing but the paper.

## Research Findings

**The shortcut** (`pipeline.py:172-226`). It returns early, before PDF image extraction (`pipeline.py:380-386`). It decides identity with `detect_arxiv_id` (`pandoc_convert.py:71-105`): the first `arXiv:` regex hit anywhere in page-1 text, then a Creator-metadata fallback. Every exception is logged at `debug` and dropped (`pipeline.py:224-226`). An ignored `--html-path` is silent (`pipeline.py:188-189`).

**Two copies of the arXiv Pandoc call.** `convert_arxiv_html` (`pandoc_convert.py:187-263`) fetches or reads, then preprocesses and runs Pandoc. `_extract_with_arxiv_pandoc` (`web_backend.py:246-295`) repeats the same preprocessing and flags. `_fallback_pandoc` (`web_backend.py:298-333`) repeats the flags a third time. Comments warn that they must stay in sync.

**Image download exists, web route only.** `_download_arxiv_images` (`web_backend.py:58-150`) rewrites `![alt](url){attrs}` refs in Pandoc markdown to `images/<name>`, skips `data:` URIs, caps size, and warns on failure. It downloads a repeated URL twice (`x1.png`, `x1_2.png`, `web_backend.py:109-118`). It resolves root-relative refs against `https://arxiv.org` and collapses `//`. Its tests (`tests/test_web_images.py`) patch `web_backend.urllib.request.urlopen`.

**Output layout is shared.** Both routes write markdown into an output directory and images into `<output>/images/`, referenced as `images/<name>`. The web route uses `output_dir / "images"` (`web_backend.py:76`). The PDF CLI sets `extracted_images_dir = output_dir / "images"` (`extract_cli.py:484-496`). `ImageCollector` writes `images/<rel_name>` refs (`pipeline.py:73-76`).

**Warnings have no PDF channel.** `PipelineResult` (`types.py:107-124`) has no `warnings` field. The PDF CLI writes `metrics.json` from `metrics.to_dict()` alone (`extract_cli.py:531`) and prints no warnings (`_print_pipeline_summary`, `extract_cli.py:171-188`). The web route returns `ExtractionResult.warnings` (`base.py:28`), adds them to `metrics.json` (`web_backend.py:509-511`), and prints them to stdout (`extract_cli.py:240-243`). Its arXiv fallback only logs (`web_backend.py:416`).

**The source URL is already known.** `_extract_pdf_url` stores `fetched.final_url` on `args.source_url_override` (`extract_cli.py:273`), and only the frontmatter uses it. PDF URLs and batch URLs re-enter `cmd_extract` with a shallow copy of `args` (`extract_cli.py:271-274`), so new flags reach them without extra plumbing.

**`--check` has its own path.** `probe_pandoc` (`check.py:328-346`) calls `detect_arxiv_id`, `check_arxiv_html` and `convert_arxiv_html` directly, and reports `len()` of the returned tuple. `compute_capabilities` sets `arxiv_shortcut` when the substring `"arXiv"` appears in the probe detail (`check.py:416-431`).

**Dependencies.** BeautifulSoup and lxml are in the optional `[web]` extra (`pyproject.toml:36`). The PDF shortcut runs on a core install. So the shared article selection can't depend on bs4. The stdlib `html.parser` is enough to find one element's span.

**Existing arXiv fixture** `tests/fixtures/arxiv_1706.03762_latest.html` is 1 KB of figure tags with no chrome. It is fine for version tests and does not represent page structure.

**Margin stamp** (spike, `[AGENT]` verified on 3 real PDFs): pymupdf `get_text("dict")` returns the stamp as one line with `dir == (0, -1)`, `x1 ≤ 44` pt, text `arXiv:<id>v<N>  [<cat>]  <date>`. Prose citations come out horizontal. Creator metadata is useless.

## Core Concept

The design makes three decisions explicit where today they are implicit, and it routes each one through a single function that both routes call.

1. **Is this PDF the arXiv paper?** Only a trusted source can answer: the rotated margin stamp on page 1, or the arxiv.org URL the PDF came from. Prose never counts. If the sources disagree or there are none, the answer is no, and normal PDF extraction runs.
2. **What part of the HTML is the paper?** The paper is the one `<article class="ltx_document">` element that LaTeXML emits. Everything arXiv wraps around it is chrome. Selecting that element *is* the chrome removal; nothing inside it is filtered. If the element is missing or ambiguous, the conversion fails, and the route takes its existing fallback.
3. **Where do the figures live?** Every image ref in the converted markdown is resolved against one base URL and fetched or copied once into `images/`. The base is the page URL, or a `file://` URL for a local HTML file, with `<base href>` applied on top. Refs that can't be saved stay as written and produce one warning each.

Each decision that ends in a fallback produces a warning string. The warning travels in the returned result and is saved to `metrics.json` and printed to stderr. That is the same channel for both routes, extended to `PipelineResult`.

This is the right shape because each of the spec's failures comes from one of these decisions made badly or twice. Substitution came from a weak identity test. Missing figures came from image persistence living only in the web route. Chrome came from converting the whole page. Silence came from fallbacks that returned `None`. Making one function own each decision fixes the failure in both routes at once, and it gives tests one pure function per decision to hit with real bytes.

Existing pieces it composes with: `check_arxiv_html` and the version helpers (unchanged); `_preprocess_html` and `_postprocess_markdown` (unchanged, now applied to the article only); `_download_arxiv_images` (moved and generalized); `strip_hidden_content` (still the web route's pre-pass); `fetch_url` and `USER_AGENT` (the network boundary); the `images/` output layout and the `metrics.json["warnings"]` convention.

## Key Bets

- **B1. Real arXiv HTML holds the whole paper, and only the paper, inside exactly one `<article>` whose class includes `ltx_document`.** Title, authors, abstract, sections, bibliography and appendices sit inside it. Header, TOC sidebar, issue dialog, LaTeXML footer, arXiv footer and funder logos sit outside it. `[AGENT, unverified in this session]` This rests on LaTeXML's documented output and the investigation's finding that all 16 data-image refs sat in chrome. The real `raw.html` was not readable here. *If false → selection drops paper parts or keeps chrome, and R4 fails on real pages.* The plan's first task checks this against the real page (see Next-Stage Handoff).
- **B2. arXiv-served PDFs carry the margin stamp as text pymupdf can read, and other PDFs essentially never contain a rotated left-margin line in the full stamp shape.** `[AGENT, spike on 3 papers]` *If false → either genuine papers stop substituting (acceptable, spec R2) or a non-arXiv PDF substitutes. The second case needs a rotated line matching `arXiv:<id>v<N> [<cat>] <date>`, which body text or a citation would not produce.*
- **B3. arXiv-injected UI inside the article is absent from the served HTML.** The "report issue" buttons are added by page script at view time. `[AGENT, unverified]` *If false → small UI strings leak into output. The fixture assertions catch it, and the fix is one targeted removal in the selection step, not a new mechanism.*
- **B4. Pandoc markdown image refs (`![alt](src){attrs}`) are the complete set of figures that need saving.** Persistence works on converted markdown, as it does today. *If false (a figure shows up only as raw HTML `<img>`) → that figure keeps a remote ref. The fixture's figure assertions would show it.*

## Key Decisions

- **D1. Identity evidence = margin stamp ∪ arxiv.org source URL.** A stamp is a page-1 line that is vertical (`|dir.x| < 0.05`), has `x1` within the left 15% of page width, and fully matches `arXiv:(\d{4}\.\d{4,5})v\d+ \[[^\]]+\] \d{1,2} \w{3} \d{4}` (whitespace-tolerant). A source URL counts when it matches `arxiv.org/(abs|pdf)/<id>[vN][.pdf]`. More than one distinct stamp ID, or a stamp and a URL that name different bare IDs, is a conflict. *Rejected: Creator metadata (useless per spike); a post-fetch title cross-check (extra network work, and B2 makes it redundant; spec makes it optional); exact stamp coordinates (vary by paper).*
- **D2. `identify_arxiv_paper()` replaces the logic inside `detect_arxiv_id`, which stays as a thin wrapper.** It lives in `pandoc_convert.py`, beside the code it replaces. Any external caller of the public `detect_arxiv_id` gets the safe rule. *Rejected: deleting `detect_arxiv_id` (needless break); keeping the old regex for "soft" signals (prose is never evidence).*
- **D3. A new module `extraction/arxiv_html.py` owns the HTML side: article selection, article conversion, image base, image persistence.** Both routes call it. `pandoc_convert.convert_arxiv_html` keeps its signature and becomes "load bytes, then `convert_article`". *Rejected: growing `pandoc_convert.py` (it already mixes PDF identity and HTTP probes); putting it in `web_backend.py` (the PDF route would import the web backend).*
- **D4. Article selection uses stdlib `html.parser` to find the span of the single `article.ltx_document`, then slices the original text.** Inner markup is passed to Pandoc byte for byte, so math, tables and in-article data URIs can't be altered by a re-serializer. Zero or several matches → `ArxivConversionError("no recognized arXiv article container")`. *Rejected: BeautifulSoup (in `[web]` only, and re-serializing could change MathML); a regex (breaks on attribute order); a deny-list of chrome selectors (open-ended, and what R4 warns against).*
- **D5. One failure type, `ArxivConversionError(reason)`, covers unrecognized structure, Pandoc missing, Pandoc failure or timeout, and output shorter than the shared 100-character minimum.** Both routes catch it and turn `reason` into a warning. *Rejected: `None` returns (what made fallbacks silent); per-cause exceptions (no caller acts on the difference).*
- **D6. One Pandoc runner `_run_pandoc(html, pandoc_path)` in `pandoc_convert.py`.** All three current invocations call it, including the general `_fallback_pandoc`. *Rejected: leaving the "keep flags in sync" comments.*
- **D7. Image refs resolve with `urljoin(base, ref)` against one base URL.** The base is the page URL for fetched HTML, or `Path(html).resolve().as_uri()` for a local file. A `<base href>` read from the full raw HTML is joined on top. `http(s)` results are downloaded, `file:` results are copied if they exist, and anything else stays as written with a warning. Repeated `//` in the path collapses, as today. This one rule covers every R1 case. A root-relative ref in a local file becomes `file:///…`, which doesn't exist, so it stays put and warns. No arXiv base is guessed. *Rejected: separate code paths per source kind; keeping the hard-coded `https://arxiv.org` prefix (equal to `urljoin` for arxiv.org pages, wrong for local files).*
- **D8. Persistence dedupes by resolved URL.** One fetch per URL, and every occurrence is rewritten to the same file. A different URL with a taken basename gets `stem_N.ext`, as today. A failed URL leaves every occurrence untouched and produces one warning. The saved count is the number of files written. *Rejected: today's one-download-per-occurrence (spec R1).*
- **D9. The network boundary is one injectable `fetch_image(url, *, max_bytes, timeout) -> bytes`.** It raises on HTTP error and on oversize. Tests stub only this, and `subprocess.run` for Pandoc where Pandoc isn't the subject. *Rejected: patching `urllib.request.urlopen` in a module namespace (couples tests to imports).*
- **D10. Shortcut control is a tri-state `PipelineConfig.arxiv_shortcut: bool | None = None`, with the default in one constant `ARXIV_SHORTCUT_DEFAULT = True` in `pandoc_convert.py`.** `None` means "automatic detection follows the default". `arxiv_html_path` is an explicit override, so it runs unless the caller set `arxiv_shortcut=False`. That combination raises `ValueError` in `__post_init__`. The CLI uses `argparse.BooleanOptionalAction` (`--arxiv-shortcut` / `--no-arxiv-shortcut`, default `None`), and its help text names the constant's value. Flipping the owner gate is one line plus one docs sentence, and `--html-path` keeps working either way. *Rejected: a plain `bool` field (if the default flipped to off, every `--html-path` user would also need `--arxiv-shortcut` or hit the contradiction error); `--no-arxiv-shortcut` alone (no way to turn it on if the default flips).*
- **D11. `PipelineConfig.pdf_source_url: str | None = None` carries the URL the PDF came from.** The CLI fills it from `fetched.final_url`. *Rejected: reusing `PipelineResult.source_url`'s name (that field means the HTML provenance).*
- **D12. `PipelineResult.warnings: list[str]` (new).** Shortcut warnings are carried into whichever result `extract_pdf` returns, including the normal-path result and the base-extraction error result. One CLI helper prints warnings to **stderr** for both routes, and the PDF branch writes `metrics.json["warnings"]` the same way the web route does. *Rejected: logging alone (spec R1 rules it out); keeping web warnings on stdout (spec requires stderr, and two printers would drift).*
- **D13. Which outcomes warn.** Ignored `--html-path`, identity conflict, identified paper with no HTML available, fetch error, `ArxivConversionError`, and each image that wasn't saved all warn. No evidence, opt-out, and Pandoc absent without `--html-path` don't. Those are the ordinary "shortcut doesn't apply" cases, and every non-arXiv PDF hits one. *Rejected: warning on every non-firing (noise on every normal PDF).*
- **D14. `--check` reuses `identify_arxiv_paper`, `resolve_arxiv_shortcut` and `convert_arxiv_html`.** It reports `len(markdown)`. The `arxiv_shortcut` capability comes from an explicit "paper identified" outcome on the probe, not the substring `"arXiv"`, which a "shortcut disabled" detail would also contain. It doesn't download images: it is a probe, not an extraction. *Rejected: running the full shortcut inside `--check` (writes files).*

## Architecture

```
PDF input ─► extract_pdf
              │ arxiv_shortcut False? ─────────────────────────────┐
              │ html_path given? ── load file ─┐                   │
              │ identify_arxiv_paper(pdf, pdf_source_url)          │
              │   none ─────────────────────────────────────────┐  │
              │   conflict ─► warn ─────────────────────────────┤  │
              │   id ─► check_arxiv_html ─► fetch bytes ─┐      │  │
              │                                          ▼      ▼  ▼
              │                 arxiv_html.convert_article ── fail ─► warn ─► normal PDF pipeline
              │                         │ ok                                      │
              │                 arxiv_html.persist_images (if images dir)          │
              ▼                         ▼                                         ▼
          PipelineResult(markdown, image_count, warnings, raw bytes, source_url)
              ▼
          CLI: output.md, images/, metrics.json{warnings}, stderr

arXiv HTML URL ─► fetch_url ─► strip_hidden_content ─► arxiv_html.convert_article
                                                         │ ok            │ fail ─► warn ─► trafilatura
                                                         ▼
                                       arxiv_html.persist_images(base = final_url ⊕ <base href>)
                                                         ▼
                                       ExtractionResult(warnings) ─► metrics.json, stderr
```

Data flow: raw bytes are hashed and saved exactly as fetched. `convert_article` works on a decoded copy. The base href is read from the full raw HTML, because `<base>` sits in `<head>`, outside the article. Image persistence runs on converted markdown, so it only sees refs from the article.

Boundaries: `arxiv_html` is pure apart from Pandoc (through `_run_pandoc`) and image I/O (through the injected `fetch_image` and the filesystem under `images_dir`). Identity is pure over PDF bytes. Network HEAD and GET stay in `check_arxiv_html` and `fetch_url`.

## Required Invariants

1. Raw source bytes saved and hashed are the fetched bytes, never the article fragment (R5 `[HARD]`).
2. Every rewritten image ref points at a file that exists under the images directory. Every ref that isn't saved is byte-identical to its Pandoc output.
3. `image_count` equals the number of image files that call wrote.
4. A PDF without trusted own-ID evidence never reaches `check_arxiv_html`, a fetch, or Pandoc. With `arxiv_shortcut=False`, `identify_arxiv_paper` isn't called either.
5. The shortcut substitutes only the ID its evidence names. Prose IDs never enter the decision.
6. Nothing inside the selected article is removed for being a data URI or an image.
7. Every fallback listed in D13 yields exactly one warning in the returned result, `metrics.json`, and stderr.
8. `ARXIV_SHORTCUT_DEFAULT` is the only place the default is written in code.
9. No existing `PipelineConfig` field or CLI flag is removed or renamed.

## Component Overview

- **`extraction/arxiv_html.py` (new).** `select_article(html) -> str | None`, `read_base_href(html) -> str | None`, `image_base(source, raw_html) -> str`, `convert_article(html, pandoc_path) -> str` (raises `ArxivConversionError`), `persist_images(markdown, base, images_dir, *, fetch=fetch_image) -> ImagePersistResult`, `fetch_image(...)`. It holds the shared minimum-content constant.
- **`extraction/pandoc_convert.py`.** Adds `identify_arxiv_paper`, `ArxivIdentity`, `ARXIV_SHORTCUT_DEFAULT`, `resolve_arxiv_shortcut` and `_run_pandoc`. `detect_arxiv_id` becomes a wrapper. `convert_arxiv_html` loads bytes and calls `convert_article`. Its signature and return type don't change.
- **`extraction/pipeline.py`.** New `PipelineConfig` fields `arxiv_shortcut` and `pdf_source_url`, plus `__post_init__` validation. `_try_arxiv_shortcut` returns `(result | None, warnings)`, persists images into `extracted_images_dir`, and sets `image_count`. `extract_pdf` attaches shortcut warnings to every result it returns.
- **`extraction/types.py`.** `PipelineResult.warnings`.
- **`extraction/web_backend.py`.** The arXiv branch calls `convert_article` and `persist_images`, and turns `ArxivConversionError` into a fallback warning. `_download_arxiv_images` and `_extract_with_arxiv_pandoc` go away. `_fallback_pandoc` calls `_run_pandoc`.
- **`extraction/check.py`.** `probe_pandoc(pdf, *, arxiv_shortcut)` and `run_check(..., arxiv_shortcut)` follow D14.
- **`cli/extract_cli.py`.** Adds the `--arxiv-shortcut/--no-arxiv-shortcut` flag. It reports a usage error (exit 2) when `--no-arxiv-shortcut` and `--html-path` are both given. It fills `pdf_source_url` from `source_url_override`, writes PDF `metrics.json["warnings"]`, passes the flag to `run_check`, and prints warnings to stderr through one helper.
- **Docs.** `docs/extraction.md`: automatic substitution, the evidence it needs, the escape hatch, the default, and the programmatic no-images-dir limitation. `docs/extraction-internals.md`: the shared module and the supported container.
- **Fixtures.** `tests/fixtures/arxiv_2610.14224v1_page.html` (trimmed real page, see Implementation Notes). PDFs are generated in tests with pymupdf.

## Non-Goals

- General website boilerplate removal and non-LaTeXML arXiv layouts.
- Recovering genuine papers that lack a stamp or arXiv URL (publisher or author builds).
- Old-style arXiv IDs (`hep-th/9901001`). The current regex doesn't support them either.
- Changing latest-version selection, OCR, or PDF figure quality.
- Image download in `--check`, and image persistence when no images directory is configured.
- Changes to personal-os.

## Implementation Notes

- **Fixture trim.** Start from `/tmp/arxiv-investigation-1topu2hb/raw.html`. If it's gone, re-fetch the pinned `https://arxiv.org/html/2610.14224v1`. Keep `<head>` (meta generator, title) and every chrome element outside the article verbatim: header, TOC nav, issue dialog, footers, funder logos, data-URI icons. Repeated list items may be shortened. Inside the article keep the title, authors, abstract, two sections that between them hold at least two figures with captions, one table and one math element, two bibliography entries and one appendix. Delete the other sections. Insert one tiny `data:image/png` `<img>` inside the article, marked by an HTML comment as the only synthetic edit. Open with a comment naming the source URL, fetch date and edits. Aim under 80 KB.
- **Stamp fixtures.** Generate them with `page.insert_text((x, y), "arXiv:2610.14224v1  [cs.AI]  9 Oct 2026", rotate=90)` at x ≈ 30. Generate four PDFs: a citation-only PDF, a stamp plus a cited prose ID, two different stamps, and a stamp that disagrees with `pdf_source_url`. Assert the actual `dir` in one test, so a pymupdf change shows up there.
- **`html.parser` offsets.** `getpos()` returns (line, column). Precompute line-start offsets, slice from the start of the article's start tag to the end of its matching end tag, and track nested `<article>` depth.
- **Wrapping the fragment for Pandoc.** Write `<html><body>{article}</body></html>` with UTF-8. Pandoc doesn't need `<head>`, and keeping it out means the page `<title>` can't reach the body.
- **Test migration.** Move `tests/test_web_images.py` cases to `tests/test_arxiv_html.py` against `persist_images` with a stubbed `fetch`. Rewrite the duplicate-URL expectation to one file. Tests in `test_pipeline.py` that stub `detect_arxiv_id` change to stub `identify_arxiv_paper`, or to use generated PDFs.
- **Web stdout to stderr.** Existing CLI tests that read web warnings from stdout need updating.

```python
@dataclass(frozen=True)
class ArxivIdentity:
    arxiv_id: str | None          # e.g. "2610.14224v1"; None = don't substitute
    evidence: tuple[str, ...]     # ("stamp",), ("url",), ("stamp", "url")
    conflict: str | None = None   # human-readable reason when sources disagree

def identify_arxiv_paper(pdf_path: Path, pdf_source_url: str | None = None) -> ArxivIdentity: ...
def persist_images(markdown: str, base: str, images_dir: Path, *, fetch=fetch_image) -> ImagePersistResult: ...
```

## Potential Risks

- **B1 is wrong for some pages** (for example, the article sits under a different tag on newer LaTeXML). Mitigation: unrecognized structure falls back with a warning, so output is never worse than PDF extraction or trafilatura. The live audit run checks the real page.
- **Shortcut hit rate drops**, because author and publisher PDFs no longer substitute. The spec accepts this. The docs say so.
- **`html.parser` and the slice disagree on malformed HTML.** LaTeXML output is well-formed. Any mismatch shows up as a selection failure, not silent corruption.
- **Output on stdout changes.** Web warnings move to stderr. This is a visible CLI change, required by the spec.

## Integration Strategy

The change replaces internals behind existing entry points: `extract_pdf`, `extract_web_content`, `convert_arxiv_html` and `run_check`. Public additions are `PipelineConfig.arxiv_shortcut`, `PipelineConfig.pdf_source_url`, `PipelineResult.warnings`, `--arxiv-shortcut/--no-arxiv-shortcut`, and the `arxiv_html` module. Callers that construct `PipelineConfig()` today get the same automatic behavior as before, under the safer identity rule. Downstream consumers drop their workarounds as separate work.

## Validation Approach

| Spec criterion | Test |
|---|---|
| Figures are portable | Real fixture through both routes, stubbed `fetch_image`: files exist under `images/`, refs are relative, counts match |
| Failures are honest | `persist_images` with a failing URL, an oversized URL, a URL used twice, and two URLs sharing a basename. CLI test asserts warnings in `metrics.json` and stderr for both routes |
| Local HTML images resolve | Temp dir with an HTML file holding absolute, `<base href>`-relative, file-relative and missing refs |
| Citations cannot substitute | Generated PDFs through the real `identify_arxiv_paper`. Negative and conflict cases assert `check_arxiv_html` and the converter are never called. The stamp case substitutes |
| `--check` predicts `extract` | Citation-only PDF: no identification, no network. `--no-arxiv-shortcut`: probe skipped. Character count equals `len(markdown)` |
| Users can force PDF extraction | Opt-out with Pandoc available, contradictory flags (exit 2, `ValueError`), PDF URL and batch forwarding |
| Paper alone | Real fixture through `convert_article` with real Pandoc (skip if Pandoc is absent): chrome strings and UI data URIs absent; title, sections, references, appendix, figure caption, table, math and the in-article data URI present |
| Fallback visible | Pandoc failure, short output, and a page with no article → per-route fallback plus a warning. An ignored `--html-path` warns |
| Provenance unchanged | Existing hash, save-source and fetched-version tests pass unchanged |
| Live check | At audit: a bounded Harness² run with Pandoc on PATH, recorded per the spec |

Run `uv run pytest tests/test_arxiv_html.py tests/test_pandoc_convert.py tests/test_pipeline.py tests/test_web_backend.py tests/test_extract_cli.py tests/test_check.py`, `uv run ruff check src/ tests/`, and `uv run mypy src/`.

## Next-Stage Handoff

- **Fixed:** D1–D14, the invariants, the module split, and the tri-state control with the default in `ARXIV_SHORTCUT_DEFAULT`.
- **Open owner gate:** whether the shortcut is on by default (R3). The design ships `True` provisionally. Flipping it changes one constant and one docs sentence.
- **De-risk first:** B1 and B3. Build the trimmed fixture from the real page and run `select_article` over it before any other work. Check that exactly one `article.ltx_document` exists, that the chrome strings sit outside it, and that no UI buttons sit inside it. If that fails, stop and revise D4 before building on it.
- **Plan's choice:** how to order the phases. A suggested order is identity → `arxiv_html` and its fixture → the PDF route → the web route → CLI, check and docs.

---
Next Step: After approval → `/_my_plan`
