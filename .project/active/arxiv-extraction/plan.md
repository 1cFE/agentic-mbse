# Implementation Plan: Reliable arXiv extraction

**Work item:** ARXIV-EXTRACTION
**Status:** Draft
**Created:** 2026-10-18
**Last Updated:** 2026-10-18
**Branch:** `fix/arxiv-extraction` (worktree `/home/reid/src/agentic-mbse-worktrees/arxiv-extraction`), base local `main` at `8b027bbc`. `src/`, `tests/`, `docs/` and `pyproject.toml` have no diff from the base at planning time.

## Source Documents

- **Spec:** `.project/active/arxiv-extraction/spec.md` (requirements R1–R5, acceptance table)
- **Design:** `.project/active/arxiv-extraction/design.md` ← component details, signatures, decisions D1–D16, invariants 1–11
- **Reviews:** `spec_review.md`, `design_review.md` (Resolutions are incorporated in the design)
- **Spike:** `spike-margin-stamp.md` (margin stamp shape; paper-container addendum)
- **Fixture source:** `ref/2610.14224.html` (untracked, fetched 2026-10-18). If missing, re-fetch `https://arxiv.org/html/2610.14224v1`.

## The Point

**[NEED]** Downstream consumers can keep Pandoc on PATH safely and drop their workarounds. Today they hide Pandoc from PATH when extracting PDFs and strip data-image references from output. After this work, those workarounds are unnecessary.

Today Pandoc on PATH is a hazard in four ways:

- **Wrong paper.** A PDF that merely cites an arXiv paper gets replaced by that paper, because any first-page `arXiv:` match counts as identity.
- **Lost figures.** A correct substitution returns before any image is saved, so figure refs point nowhere.
- **Chrome in output.** The direct arXiv HTML route converts the whole page: issue dialog, navigation, footer, funder logos, UI icons.
- **Silent fallback.** When the shortcut gives up, nothing in the result or on disk says why. There is no way to turn the shortcut off.

The test every phase serves: a consumer runs `extract` with Pandoc on PATH and no workarounds, and gets the right paper, its figures on disk, and nothing but the paper. When something falls back, they see a warning.

**[OWNER] Reserved gates the plan must keep:**

- Default-on is open. The shortcut ships on provisionally, written in exactly one constant (`ARXIV_SHORTCUT_DEFAULT`, design D10, invariant 8). Flipping it is one line plus one docs sentence.
- No existing public `PipelineConfig` field or CLI flag is removed or renamed (invariant 9). Only additions.

## Implementation Strategy

**Phasing rationale.** The paper boundary is locked first, on a real page, before anything depends on it. Then the work moves from shared plumbing to user-facing behavior, so each phase lands green and can be committed alone:

1. Lock the paper boundary and move the shared HTML code into one module, with no behavior change.
2. Build the warnings channel, so every later fallback has somewhere to report.
3. Fix identity (the wrong-paper bug).
4. Add the opt-out control and CLI flag.
5. Turn on paper-only conversion in both routes.
6. Save images in both routes.
7. Align `--check`, write docs, run the full verification.
8. Run the live Harness² check (recorded, non-blocking).

**Deviation from the orchestrator's suggested order** `[AGENT]`: the warnings channel moves from fifth to second. Identity conflicts (phase 3), paper-only fallbacks (phase 5) and image failures (phase 6) all produce warnings (D13). Building the channel first lets each of those phases assert its warning end to end, instead of retrofitting assertions later. Paper-only conversion (R4) had no slot in the suggested order; it goes before images because image persistence needs the loader's serving URL (D15), which phase 5 introduces.

**Critical path.** Fixture → `arxiv_html` core → warnings channel → loader and paper-only wiring → image persistence. Identity (3) and opt-out (4) are off the critical path and could swap.

**First proof point.** Phase 1's two fixture tests: `select_article` on the trimmed real page keeps every paper part and drops every chrome string (no Pandoc needed), and `convert_article` on the same page through real Pandoc yields markdown whose figure refs match the image-ref pattern. If either fails, bets B1 or B4 are wrong and the design needs revisiting before more code is written.

**Green, for every phase** `[AGENT]`:

- [ ] Focused tests pass: `uv run pytest tests/test_arxiv_html.py tests/test_pandoc_convert.py tests/test_pipeline.py tests/test_web_backend.py tests/test_extract_cli.py tests/test_check.py` plus any new test file the phase adds.
- [ ] `uv run ruff check src/ tests/` and `uv run ruff format --check src/ tests/` are clean on touched files.
- [ ] `uv run mypy src/` is clean on touched files.
- [ ] `uv run pytest tests/` shows no failure outside the phase 0 baseline set.
- [ ] Commit the phase on `fix/arxiv-extraction`, then tick its boxes and fill its Implementation Notes entry here.

Run extract commands that call the Claude CLI per CLAUDE.md (redirect to a temp file and read it back). None of this plan's tests need the Claude CLI.

---

## Phase 0: Record the baseline

### Goal

Know which tests already fail at the base, so "no new failures" is checkable.

### Steps

- [ ] Confirm the code still matches the base: `git diff --stat 8b027bbc HEAD -- src tests docs pyproject.toml` prints nothing.
- [ ] Run `uv run pytest tests/ -q > /tmp/arxiv-baseline.txt 2>&1`.
- [ ] Record below: pass/fail/skip counts, the node IDs of every failure and error, and whether failures come from environment (for example a missing `SYSIDE_LICENSE_KEY`) or code.
- [ ] Record `pandoc --version` (expect 3.1.3) and the pymupdf version, since phase 1 and 3 tests depend on both.

**Baseline failure set:** _(fill in)_

---

## Phase 1: Paper boundary and the shared HTML module

### Goal

Create `extraction/arxiv_html.py` with the paper selector and the one Pandoc runner, prove both on a trimmed real arXiv page, and route today's three Pandoc calls through the runner. User-visible behavior does not change in this phase: `select_article` and `convert_article` exist and are tested but nothing calls them yet.

### Assumption under test

- B1: the trimmed real page has exactly one `<article class="ltx_document">`, every paper part is inside it, and every chrome element is outside it.
- B4: real Pandoc turns the article's figures into `![alt](src){attrs}` refs that the image-ref pattern (today `web_backend.py:53`) matches, with relative `2610.14224v1/<file>` sources.
- Moving the helpers and collapsing three Pandoc calls into one keeps all existing tests green.

### Test stencil (write first)

```python
# tests/test_arxiv_html.py
FIXTURE = Path(__file__).parent / "fixtures" / "arxiv_2610.14224v1_page.html"
CHROME = ["<dialog", "Report Issue", "ltx_page_footer", "<nav", DATA_URI_ICON_PREFIX]  # take exact strings from the fixture
PAPER = [TITLE, "Abstract", SECTION_HEADING, APPENDIX_HEADING, BIB_ENTRY_TEXT, "ltx_equation", "ltx_tabular", IN_ARTICLE_DATA_URI]

def test_select_article_keeps_paper_drops_chrome():          # runs without Pandoc
    page = FIXTURE.read_text(encoding="utf-8")
    article = select_article(page)
    assert article is not None and article.lstrip().lower().startswith("<article")
    for s in CHROME: assert s in page and s not in article
    for s in PAPER:  assert s in article

@pytest.mark.parametrize("html", [NO_ARTICLE, TWO_ARTICLES, ARTICLE_WITHOUT_LTX_CLASS, "<articles>x</articles>"])
def test_select_article_fails_closed(html):
    assert select_article(html) is None

@pytest.mark.skipif(shutil.which("pandoc") is None, reason="needs Pandoc")
def test_convert_article_real_pandoc_on_fixture():
    md = convert_article(FIXTURE.read_text(encoding="utf-8"))
    assert len(_MD_IMAGE_RE.findall(md)) >= 2               # B4
    assert "2610.14224v1/" in md and IN_ARTICLE_DATA_URI_MD in md
    for s in CHROME_TEXT: assert s not in md
```

Also: `convert_article` raises `ArxivConversionError` for no article, for `subprocess.run` raising `FileNotFoundError` (Pandoc missing), for a non-zero return, for `TimeoutExpired`, and for output under `MIN_CONTENT_CHARS`; the Pandoc command `_run_pandoc` builds carries today's four flags.

### Changes required

**See design:** module split and import direction (`design.md#core-concept`, D3, D6, invariant 10); selection rule (D4, Implementation Notes "Selection scan", "Wrapping the fragment"); error type (D5); fixture trim (Implementation Notes "Fixture trim").

- [ ] **Fixture** `tests/fixtures/arxiv_2610.14224v1_page.html` (NEW). Trim from `ref/2610.14224.html` per the design's trim note. Keep `<head>` and all chrome outside the article verbatim, including the page's one `data:` icon. Inside the article keep title, authors, abstract, two sections holding at least two figures with captions, one table and one math element, two bibliography entries and one appendix. Insert one tiny `data:image/png` `<img>` inside the article, marked by an HTML comment as the only synthetic edit. Open with a comment naming the source URL, fetch date (2026-10-18) and edits. Keep it under 80 KB. Do the trim with a throwaway script outside the repo; commit only the fixture.
- [ ] **Tests** `tests/test_arxiv_html.py` (NEW): the stencil above. Pick the `CHROME` and `PAPER` strings by reading the fixture; each chrome string must appear in the page, so a bad trim fails loudly.
- [ ] **Module** `src/agentic_mbse/extraction/arxiv_html.py` (NEW): `ArxivConversionError`, `MIN_CONTENT_CHARS = 100`, `select_article`, `_run_pandoc(html, pandoc_path)`, `convert_article`, and `_preprocess_html` / `_postprocess_markdown` moved verbatim from `pandoc_convert.py:33-63`. Stdlib only (the PDF route runs on a core install). No import of `pandoc_convert`.
  - `_run_pandoc` writes the temp file and calls `subprocess.run` (module-level `import subprocess`, so existing `patch("subprocess.run")` tests keep working). It does not call `shutil.which`. A missing Pandoc shows up as `FileNotFoundError` from `subprocess.run` and becomes `ArxivConversionError("Pandoc not found ...")`. This keeps tests that stub `subprocess.run` working on machines without Pandoc. Callers that need a silent availability check keep their own (`pandoc_convert._pandoc_available`).
  - `convert_article` = `select_article` → wrap as `<html><body>{article}</body></html>` → `_preprocess_html` → `_run_pandoc` → `_postprocess_markdown` → length check.
- [ ] **`pandoc_convert.py`**: delete the moved helpers and import them from `arxiv_html` (keep the names importable from `pandoc_convert` until phase 5, so nothing else changes this phase). `convert_arxiv_html` (`:187-263`) keeps its fetch, its `_pandoc_available` → `FileNotFoundError` check and its whole-page conversion for now, but runs Pandoc through `_run_pandoc`.
- [ ] **`web_backend.py`**: `_extract_with_arxiv_pandoc` (`:246-295`) and `_fallback_pandoc` (`:298-333`) call `_run_pandoc` and keep returning `None` on any failure. Remove the "keep flags in sync" comments.
- [ ] **Test imports**: tests importing `_preprocess_html` / `_postprocess_markdown` from `pandoc_convert` switch to `arxiv_html` (Implementation Notes "Test migration").

### Validation

- [ ] Green (see strategy). The Pandoc-free selection test runs and passes in every environment; the real-Pandoc test runs locally (Pandoc present).
- [ ] `grep -n "pandoc_convert" src/agentic_mbse/extraction/arxiv_html.py` returns nothing (invariant 10).
- [ ] `grep -n '"--markdown-headings=atx"' src/` hits only `arxiv_html.py` (one runner, D6).
- [ ] Manual: `wc -c tests/fixtures/arxiv_2610.14224v1_page.html` is under ~80 KB; open the head comment and confirm source URL, date and the one synthetic edit are recorded.

**What we know works after this phase:** the paper boundary on a real page is pinned by a test that needs no Pandoc; real Pandoc produces matchable figure refs from the article alone; one Pandoc runner serves every call site; behavior is unchanged.

---

## Phase 2: The warnings channel

### Goal

Give the PDF route a warnings field and give both routes one way to surface warnings: in the returned result, in `metrics.json["warnings"]`, and on stderr. Convert today's silent shortcut and web fallbacks into warnings.

### Assumption under test

The PDF CLI can print and persist warnings before its `if result.error` branch without disturbing the existing output layout, and moving web warnings from stdout to stderr breaks no existing test that matters.

### Test stencil (write first)

```python
# tests/test_pipeline.py
def test_shortcut_exception_becomes_warning(tmp_path):        # was debug-only (pipeline.py:224-226)
    with patch(f"{_PANDOC}._pandoc_available", return_value=True), \
         patch(f"{_PANDOC}.detect_arxiv_id", side_effect=RuntimeError("boom")):
        result = extract_pdf(sample_pdf, PipelineConfig(enable_claude=False))
    assert result.source != "pandoc_arxiv" and any("boom" in w for w in result.warnings)

def test_ignored_html_path_warns(): ...                       # Pandoc absent + arxiv_html_path set
def test_warnings_on_base_extraction_error_result(): ...      # extract_pages raises → error result still carries shortcut warnings

# tests/test_extract_cli.py
def test_pdf_warnings_in_stderr_and_metrics_even_on_error(tmp_path, capsys): ...
def test_web_warnings_go_to_stderr_not_stdout(tmp_path, capsys): ...

# tests/test_web_backend.py
def test_arxiv_pandoc_failure_warns_and_keeps_trafilatura_backend(): ...
```

### Changes required

**See design:** D12 (where warnings travel), D13 (which outcomes warn), invariant 7, Architecture diagram.

- [ ] **`types.py:107-124`**: `PipelineResult.warnings: list[str] = field(default_factory=list)`.
- [ ] **`pipeline.py`**: `_try_arxiv_shortcut` (`:172-226`) returns `(PipelineResult | None, list[str])`. Warn on: ignored `--html-path` (Pandoc absent, `:188-189`), identified ID with no HTML available, and any exception (fetch error, conversion error). Keep the log line. Stay silent on no ID and on Pandoc absent without `--html-path`. `extract_pdf` (`:380-386` and the base-extraction error return at `:398`, and the normal return) attaches the warnings to whichever result it returns.
- [ ] **`web_backend.py`**: when the arXiv Pandoc attempt fails or is short (`:414-417`), add an actionable warning to the result's warnings. Initialize `extraction_warnings` before Step 3 so fallback and image warnings share one list; it already flows into `metrics.json` (`:509-511`) and `ExtractionResult.warnings`. The `D16` skip of `_fallback_pandoc` waits for phase 5.
- [ ] **`extract_cli.py`**: one helper (for example `_print_warnings(label, warnings)`) that writes to `sys.stderr`. Use it in the web route (replace the stdout block at `:240-243`) and in the PDF branch. In the PDF branch (`:500-531`), print warnings and write `metrics.json` (with `"warnings"` when non-empty) before the `if result.error` check at `:502`; on success the later `metrics.json` write includes the same warnings. The output dir already exists at that point (`:483`).

### Validation

- [ ] Green.
- [ ] Manual: run `uv run agentic-mbse extract <small local pdf> --budget 0 --html-path /tmp/does-not-exist.html -o /tmp/arxiv-p2`. The load fails, the run falls through to PDF extraction, stderr shows one warning, and `/tmp/arxiv-p2/<doc>/metrics.json` contains it.

**What we know works after this phase:** every route has one reporting channel that reaches the result, disk and stderr, including on PDF error results. Today's silent fallbacks now warn.

---

## Phase 3: Trusted identity

### Goal

The shortcut fires only on trusted own-ID evidence: the rotated margin stamp, or the arxiv.org URL the PDF came from. This closes the wrong-paper bug.

### Assumption under test

- B2: a generated PDF with `insert_text(..., rotate=90)` at x ≈ 30 produces a line that pymupdf reports as vertical and left-margin, and the full stamp regex matches it; horizontal prose citations never match.
- The stamp and URL rules in D1 produce the right answer for every spec case (citation-only, arXiv-origin citing another ID, conflicting stamps, stamp vs URL disagreement, genuine stamp).

### Test stencil (write first)

```python
# tests/test_arxiv_identity.py (NEW) — real pymupdf, generated PDFs
def make_pdf(path, *, stamp=None, stamps=(), prose=None):
    doc = pymupdf.open(); page = doc.new_page()
    for i, s in enumerate(([stamp] if stamp else []) + list(stamps)):
        page.insert_text((30 + 8 * i, 500), s, rotate=90)
    if prose: page.insert_text((72, 90), prose)
    doc.save(path)

def test_stamp_line_is_vertical(tmp_path):                    # pins the pymupdf behavior B2 relies on
    ...; assert line["dir"] == pytest.approx((0, -1), abs=0.05)

def test_citation_only_is_not_identity(tmp_path):
    p = make_pdf(tmp_path / "c.pdf", prose="Prior work: arXiv:2610.14224")
    assert identify_arxiv_paper(p) == ArxivIdentity(None, ())

def test_stamp_wins_over_cited_prose_id(tmp_path):            # arXiv-origin PDF citing another ID
    p = make_pdf(..., stamp="arXiv:2610.14224v1  [cs.AI]  9 Oct 2026", prose="see arXiv:1706.03762")
    assert identify_arxiv_paper(p).arxiv_id == "2610.14224v1"

def test_two_stamps_conflict(tmp_path): ...                   # arxiv_id None, conflict set
def test_stamp_vs_source_url_conflict(tmp_path): ...          # pdf_source_url names another bare ID
def test_source_url_alone_identifies(tmp_path): ...           # "https://arxiv.org/pdf/2610.14224v1"
def test_same_id_different_version_is_not_conflict(tmp_path): ...

# tests/test_pipeline.py
def test_negative_and_conflict_never_probe_or_convert(tmp_path):   # invariant 4
    with patch(f"{_PANDOC}.check_arxiv_html") as head, patch("subprocess.run") as run: ...
    head.assert_not_called(); run.assert_not_called()
```

### Changes required

**See design:** D1 (evidence rules, regexes, conflict), D2 (`detect_arxiv_id` becomes a wrapper), D11 (`pdf_source_url`), invariants 4–5, Implementation Notes "Stamp fixtures", `ArxivIdentity` signature.

- [ ] **`tests/test_arxiv_identity.py`** (NEW): the stencil, all four design fixtures (citation-only, stamp plus cited prose ID, two stamps, stamp vs URL) plus the positive URL-only case. Generate PDFs in `tmp_path`; commit none.
- [ ] **`pandoc_convert.py`**: add `ArxivIdentity` and `identify_arxiv_paper(pdf_path, pdf_source_url=None)` using `get_text("dict")` on page 1 only. `detect_arxiv_id` (`:71-105`) returns `identify_arxiv_paper(pdf_path).arxiv_id`. Drop the Creator-metadata fallback.
- [ ] **`pipeline.py`**: `PipelineConfig.pdf_source_url: str | None = None` (append; touch no existing field). `_try_arxiv_shortcut` calls `identify_arxiv_paper(pdf_path, config.pdf_source_url)`; a conflict warns (D13); no evidence is silent.
- [ ] **`extract_cli.py:487-499`**: pass `pdf_source_url=getattr(args, "source_url_override", None)`.
- [ ] **Test migration**: `test_pipeline.py` tests that stub `detect_arxiv_id` (`:152-230`, `:730-750`, `:1463-1480`) stub `identify_arxiv_paper` returning an `ArxivIdentity`, or use generated PDFs. `test_check.py` stubs of `detect_arxiv_id` keep working through the wrapper until phase 7.

### Validation

- [ ] Green.
- [ ] Manual: generate the citation-only PDF and run `uv run agentic-mbse extract <pdf> --budget 0 -o /tmp/arxiv-p3` with Pandoc on PATH. `output.md` is the PDF's own text, not Harness², and no network call is made (run with networking unavailable, or watch for no `fetch` line).

**What we know works after this phase:** a citation can no longer substitute content; arXiv PDFs with a stamp, or fetched from an arxiv.org URL, still take the shortcut.

---

## Phase 4: Shortcut control and the CLI flag

### Goal

Let users force normal PDF extraction with Pandoc on PATH, through `--no-arxiv-shortcut` and `PipelineConfig.arxiv_shortcut=False`, with the default in one constant.

### Assumption under test

The tri-state field plus one constant (D10) keeps `--html-path` working under either default, and the flag reaches PDF URL and batch paths through the existing shallow copy of `args` (`extract_cli.py:271-274`) with no extra plumbing.

### Test stencil (write first)

```python
def test_opt_out_skips_identity_probe_and_pandoc(tmp_path):      # invariant 4, second sentence
    with patch(f"{_PANDOC}.identify_arxiv_paper") as ident, patch(f"{_PANDOC}.check_arxiv_html") as head, \
         patch("subprocess.run") as run, patch(f"{_PANDOC}._pandoc_available", return_value=True):
        r = extract_pdf(stamp_pdf, PipelineConfig(arxiv_shortcut=False, enable_claude=False))
    ident.assert_not_called(); head.assert_not_called(); run.assert_not_called()
    assert r.source != "pandoc_arxiv" and r.warnings == []          # opt-out is not a failure

def test_opt_out_with_html_path_raises():
    with pytest.raises(ValueError): PipelineConfig(arxiv_shortcut=False, arxiv_html_path=Path("x.html"))

def test_resolve_arxiv_shortcut_uses_constant(monkeypatch):
    monkeypatch.setattr(pandoc_convert, "ARXIV_SHORTCUT_DEFAULT", False)
    assert resolve_arxiv_shortcut(None) is False and resolve_arxiv_shortcut(True) is True

def test_html_path_runs_even_if_default_off(monkeypatch): ...    # explicit override wins

# tests/test_extract_cli.py
def test_cli_contradiction_exits_2(): ...                        # --no-arxiv-shortcut --html-path x
def test_flag_reaches_pdf_url_and_batch(): ...                   # _extract_pdf_url / --urls-from forward args
def test_help_names_default(): ...                               # help text contains the constant's value
```

### Changes required

**See design:** D10 (tri-state, constant, `resolve_arxiv_shortcut`, `BooleanOptionalAction`), invariants 4, 8, 9.

- [ ] **`pandoc_convert.py`**: `ARXIV_SHORTCUT_DEFAULT = True` and `resolve_arxiv_shortcut`.
- [ ] **`pipeline.py`**: `PipelineConfig.arxiv_shortcut: bool | None = None` (append) and `__post_init__` raising `ValueError` for `arxiv_shortcut=False` with `arxiv_html_path` set. `_try_arxiv_shortcut` returns `(None, [])` before any work when `arxiv_shortcut is False`; it runs automatic detection only when `resolve_arxiv_shortcut(config.arxiv_shortcut)` is true; `arxiv_html_path` runs unless explicitly disabled.
- [ ] **`extract_cli.py`**: add `--arxiv-shortcut/--no-arxiv-shortcut` (`argparse.BooleanOptionalAction`, `default=None`) near `--html-path` (`:793`); help text names the default by reading the constant. Reject the contradiction with `parser.error`-style exit 2 at the top of `cmd_extract` (exit code 2 is already used for `--check` FAIL; the test asserts the usage message, not only the code). Pass `arxiv_shortcut=args.arxiv_shortcut` into `PipelineConfig`. The `--check` probe takes the flag in phase 7.
- [ ] Review the diff: the default's value is written only in `ARXIV_SHORTCUT_DEFAULT`; the field, the CLI default and the help text all read it or default to `None` (invariant 8).

### Validation

- [ ] Green.
- [ ] Manual: `uv run agentic-mbse extract --help` shows both flag forms and the default; `uv run agentic-mbse extract x.pdf --no-arxiv-shortcut --html-path y.html` exits 2 with a clear message.

**What we know works after this phase:** users can force PDF extraction with Pandoc on PATH; contradictory settings fail clearly; the default lives in one line.

---

## Phase 5: Paper-only conversion in both routes

### Goal

Both routes load HTML through one loader, convert only the article, and fall back with a warning when the article isn't recognized. For arXiv URLs, the whole-page Pandoc fallback no longer runs.

### Assumption under test

- The web route's sanitizer (`strip_hidden_content`, bs4) preserves the single `<article class="ltx_document">` so selection still succeeds on sanitized HTML.
- B5: `ArxivSource.from_fetch` with a trailing-slash `/html/<id>/` URL normalizes it, so later `urljoin` against `2610.14224v1/<file>` gives `https://arxiv.org/html/2610.14224v1/<file>`.
- Raw bytes saved and hashed stay the fetched bytes (invariant 1).

### Test stencil (write first)

```python
# tests/test_arxiv_html.py
def test_from_fetch_strips_trailing_slash():
    src = ArxivSource.from_fetch(FetchResult(content=b"...", final_url="https://arxiv.org/html/2610.14224v1/", content_type="text/html"))
    assert src.serving_url == "https://arxiv.org/html/2610.14224v1"
def test_load_local_file_serving_url_is_file_uri(tmp_path): ...
def test_image_base_applies_base_href(): ...

@pytest.mark.skipif(not _has_bs4(), reason="needs [web] extra")
def test_selection_survives_sanitizer():
    assert select_article(strip_hidden_content(FIXTURE.read_text())) is not None

# tests/test_web_backend.py — real fixture, stubbed fetch_url, real Pandoc (skip if absent)
def test_arxiv_web_route_outputs_paper_only(tmp_path): ...       # chrome absent, paper parts present, backend pandoc-arxiv
def test_unrecognized_container_falls_back_to_trafilatura_with_warning(tmp_path): ...
def test_arxiv_url_short_trafilatura_never_calls_fallback_pandoc(tmp_path):   # D16, invariant 11
    with patch("agentic_mbse.extraction.web_backend._fallback_pandoc") as fb: ...
    fb.assert_not_called()
def test_raw_bytes_and_hash_unchanged(tmp_path): ...            # save_source raw.html == fetched bytes

# tests/test_pipeline.py
def test_pdf_shortcut_converts_article_only(tmp_path): ...      # stamp PDF, stubbed check_arxiv_html + fetch_url, real Pandoc
def test_pdf_shortcut_no_article_falls_back_with_warning(tmp_path): ...
```

### Changes required

**See design:** D15 (loader, `ArxivSource`, `from_fetch` normalization), D5, D13, D16, invariants 1 and 11, Architecture diagram, Data flow paragraph.

- [ ] **`arxiv_html.py`**: `ArxivSource` (with `from_fetch` and `image_base`), `load_arxiv_html(source, *, timeout)` calling `http.fetch_url` for URLs and reading the file for paths.
- [ ] **`pandoc_convert.convert_arxiv_html`**: becomes the wrapper over `load_arxiv_html` and `convert_article`. Keep its signature, return type and the `_pandoc_available` → `FileNotFoundError` check (an existing test pins it at `tests/test_pandoc_convert.py:305-313`). Other failures now raise `ArxivConversionError` where they used to raise `CalledProcessError`; update the docstring. In-repo callers catch `Exception`, so no caller changes. `[AGENT]` plan decision: the design fixes signature and return type but not exception types; this is the narrowest change that keeps the pinned contract.
- [ ] **`pipeline._try_arxiv_shortcut`**: load through `load_arxiv_html`, convert with `convert_article`, catch `ArxivConversionError` and fetch errors into warnings. Hash `source.raw_bytes`; compute fetched version as today (`:207-214`). Keep `raw_source_bytes` as the raw bytes.
- [ ] **`web_backend.py`**: the arXiv branch (`:410-417`) builds `ArxivSource.from_fetch(fetched)`, runs `convert_article` on the sanitized HTML, and turns `ArxivConversionError` into a warning. For arXiv URLs skip Step 3b (`:423-432`). Delete `_extract_with_arxiv_pandoc`; replace `_MIN_CONTENT_LENGTH` with `arxiv_html.MIN_CONTENT_CHARS`. Saved `raw.html` (`:514-515`) stays `fetched.text()`.
- [ ] **Remove the phase 1 re-exports** of `_preprocess_html` / `_postprocess_markdown` from `pandoc_convert` once nothing imports them there.
- [ ] **Test migration**: `tests/test_pandoc_convert.py:239-303` inputs wrap content in `<article class="ltx_document">…</article>` and stub Pandoc output of at least `MIN_CONTENT_CHARS`; that change is the intended R4 behavior, so record it in Implementation Notes. `test_pipeline.py` tests that stub `convert_arxiv_html` stub `arxiv_html.load_arxiv_html` / `convert_article` or `fetch_url` + `subprocess.run` instead.

### Validation

- [ ] Green, including existing provenance tests (raw-byte hash, save-source, fetched version) unchanged.
- [ ] Manual: `uv run agentic-mbse extract --html-path .project/active/arxiv-extraction/ref/2610.14224.html <stamp pdf> -o /tmp/arxiv-p5` (stamp PDF from the phase 3 helper). `grep -c "data:image" /tmp/arxiv-p5/output.md` is 0, and `grep -E "Report Issue|ltx_page_footer" /tmp/arxiv-p5/output.md` finds nothing.

**What we know works after this phase:** both routes emit the paper alone; unrecognized pages fall back visibly; no path puts whole-page arXiv HTML through Pandoc.

---

## Phase 6: Image persistence in both routes

### Goal

Every figure in the converted article is saved once under `images/` and referenced by a relative path, in both routes; every image not saved keeps its original ref and warns once.

### Assumption under test

One resolution rule (`urljoin(image_base, ref)`, D7) covers fetched arXiv pages, trailing-slash URLs, local files with and without `<base href>`, and unresolvable refs, without per-source code paths.

### Test stencil (write first)

```python
# tests/test_arxiv_html.py — persist_images with an injected fetch (D9)
def fake_fetch(table):
    def f(url, *, max_bytes, timeout):
        v = table[url]
        if isinstance(v, Exception): raise v
        return v
    return f

def test_saves_and_rewrites(tmp_path):
    md = "![a](2610.14224v1/x1.png){width=50%} ![b](2610.14224v1/x2.png)"
    r = persist_images(md, "https://arxiv.org/html/2610.14224v1", tmp_path / "images", fetch=fake_fetch({...: b"P1", ...: b"P2"}))
    assert r.saved_count == 2 and "](images/x1.png){width=50%}" in r.markdown
    assert all((tmp_path / "images" / n).exists() for n in ("x1.png", "x2.png"))

def test_same_url_twice_one_file(tmp_path): ...              # D8: one fetch, both refs → images/x1.png
def test_same_url_twice_failure_one_warning(tmp_path): ...   # both refs unchanged, len(warnings) == 1
def test_basename_collision_gets_suffix(tmp_path): ...       # different URLs, same name → x1_2.png
def test_oversize_leaves_ref_and_warns(tmp_path): ...
def test_data_uri_untouched(tmp_path): ...                    # invariant 6
def test_local_html_refs(tmp_path): ...   # absolute http → fetched; <base href>-relative; file-relative → copied; missing → unchanged + warning

# route tests: real fixture → files exist under images/, refs relative, image_count == saved files,
# warnings in result + metrics.json + stderr (CLI); trailing-slash serving URL still resolves
```

### Changes required

**See design:** D7 (resolution), D8 (dedupe, naming, counts), D9 (`fetch_image` boundary), invariants 2, 3, 6, `ImagePersistResult` fields, Implementation Notes "Test migration".

- [ ] **`arxiv_html.py`**: `fetch_image` (User-Agent from `http.USER_AGENT`, reads `max_bytes + 1`, raises on oversize and HTTP error), `ImagePersistResult`, and `persist_images`. Move `_MD_IMAGE_RE` from `web_backend.py:53` here. Keep `//` collapsing in the path; drop the hard-coded `https://arxiv.org` prefix (D7).
- [ ] **`pipeline._try_arxiv_shortcut`**: when `config.extracted_images_dir` is set, run `persist_images(markdown, source.image_base, config.extracted_images_dir)`; set `image_count` from `saved_count`; append its warnings. Without an images dir, refs stay remote (documented limitation, phase 7). Check `PipelineResult`'s image-count field name in `types.py` before wiring.
- [ ] **`web_backend.py`**: replace `_download_arxiv_images` (`:58-150`) with `persist_images(full_markdown, source.image_base, output_dir / "images")` at `:487-492`; delete the old function.
- [ ] **Tests**: migrate `tests/test_web_images.py` cases into `tests/test_arxiv_html.py` against `persist_images` with an injected fetch; rewrite the duplicate-URL expectation to one file; delete `tests/test_web_images.py` once every case has a home. Add the CLI test that a failed image on each route shows in `metrics.json["warnings"]` and stderr.

### Validation

- [ ] Green.
- [ ] Manual: repeat the phase 5 `--html-path` run with a temp copy of the fixture next to a `2610.14224v1/` folder holding two small PNGs; `/tmp/arxiv-p6/images/` holds them, `output.md` refs `images/<name>`, and `metrics.json` reports the matching count.

**What we know works after this phase:** both routes produce portable output: figures on disk, relative refs, honest counts, one warning per unsaved image.

---

## Phase 7: `--check` alignment, docs, full verification

### Goal

`extract --check` predicts what `extract` will do and reports real character counts; the docs explain automatic substitution, its evidence, the escape hatch and the default; the whole spec acceptance table is ticked against tests.

### Assumption under test

Reusing `identify_arxiv_paper`, `resolve_arxiv_shortcut` and `convert_arxiv_html` in the probe gives the same decision as the pipeline for every phase 3 fixture.

### Test stencil (write first)

```python
# tests/test_check.py
def test_probe_citation_only_identifies_nothing_and_fetches_nothing(tmp_path):
    with patch("agentic_mbse.extraction.check.check_arxiv_html") as head: r = probe_pandoc(citation_pdf, arxiv_shortcut=None)
    head.assert_not_called(); assert r.arxiv_identified is False
def test_probe_opt_out_skips_and_capability_false(): ...     # run_check(..., arxiv_shortcut=False) → capabilities["arxiv_shortcut"] False
def test_probe_reports_len_of_markdown(): ...                # stub convert_arxiv_html → ("x" * 1234, b"") → "1234 chars"
def test_capability_reads_field_not_substring(): ...         # detail "arXiv shortcut disabled" + arxiv_identified False → False
```

### Changes required

**See design:** D14, `check.py` component note, Docs component note, Non-Goals.

- [ ] **`check.py`**: `ProbeResult.arxiv_identified: bool = False` (`:63-69`); `probe_pandoc(pdf, *, arxiv_shortcut=None)` (`:328-346`) returns early when disabled, otherwise uses `identify_arxiv_paper` and reports `len(markdown)`; `run_check(..., arxiv_shortcut=None)` (`:555`, `:611`) forwards it; `compute_capabilities` (`:416-431`) reads the field. No image download in the probe.
- [ ] **`extract_cli.py`**: pass `arxiv_shortcut=args.arxiv_shortcut` to both `run_check` calls (`:385`, `:445`).
- [ ] **`docs/extraction.md`**: automatic substitution and the evidence it requires (stamp or arxiv.org source URL; prose citations never count); author and publisher PDFs don't substitute; `--no-arxiv-shortcut` / `PipelineConfig(arxiv_shortcut=False)` and the contradiction with `--html-path`; the current default (one sentence, so a flip edits one sentence); image persistence and the programmatic no-images-dir limitation; warnings on stderr and in `metrics.json`; web warnings moved from stdout to stderr.
- [ ] **`docs/extraction-internals.md`**: the `arxiv_html` / `pandoc_convert` split and import direction, the supported container (`<article class="ltx_document">`, exactly one), and the fallback per route.
- [ ] **Spec acceptance sweep**: walk `spec.md#acceptance-and-verification` and the design's Validation Approach table; next to each row, record in Implementation Notes the test node ID that proves it. Any row without a test is a gap to close in this phase.

### Validation

- [ ] Green, plus `uv run pytest tests/ -m ""` compared with the phase 0 baseline if the slow corpus runs in this environment (record if it doesn't).
- [ ] Manual: `uv run agentic-mbse extract --check <citation-only.pdf> > /tmp/check-out.txt 2>&1` (CLAUDE.md workaround), then read it: the Pandoc probe names no arXiv ID and the shortcut capability is off. With `--no-arxiv-shortcut` the probe says it is disabled.

**What we know works after this phase:** `--check` and `extract` agree; users can read how substitution works and how to turn it off; every spec criterion has a named test.

---

## Phase 8: Live Harness² check (recorded, non-blocking)

### Goal

Corroborate the fixtures against today's real arXiv pages: a consumer's run with Pandoc on PATH and no workarounds.

### Steps

- [ ] Record date, `pandoc --version`, and the branch commit.
- [ ] Web route: `uv run agentic-mbse extract https://arxiv.org/html/2610.14224 -o /tmp/harness2-web > /tmp/harness2-web.txt 2>&1`.
- [ ] PDF route: `uv run agentic-mbse extract https://arxiv.org/pdf/2610.14224 -o /tmp/harness2-pdf --budget 0 > /tmp/harness2-pdf.txt 2>&1`. This exercises both the stamp and the arxiv.org source URL.
- [ ] For each route record: fetched source URL and version (frontmatter), backend, saved image count versus files in `images/`, any dangling refs (`grep -o "](images/[^)]*)"` each checked for existence), `grep -c "data:image"` (expect only in-article ones, 0 for this paper), chrome strings absent (`Report Issue`, footer and nav text chosen in phase 1), and every warning printed.
- [ ] If network is unavailable, record that and stop. Either way this step does not block close. Any surprise against a bet (B1, B2, B5) gets surfaced in the record, not silently patched.

**Record:** _(fill in)_

---

## Risk Management

**See `design.md#potential-risks`** for the design-level risks.

Phase-specific mitigations:

- **Phase 1, fixture trim drops a needed structure.** Every chrome and paper string the tests check must be asserted present in the page first, so a bad trim fails at the assertion that names the missing string.
- **Phase 1, Pandoc absent in CI.** The selection test needs no Pandoc; real-Pandoc tests skip cleanly. `_run_pandoc` detects absence from `subprocess.run`, so stubbed tests don't depend on `shutil.which`.
- **Phase 2, output-stream change.** Web warnings move to stderr. Search `tests/` for assertions on web warnings in stdout and update them; note the change in docs (phase 7).
- **Phase 3, pymupdf `dir` values change across versions.** One test pins the generated stamp's `dir`, so a library change fails there with a clear message rather than in every identity test.
- **Phase 5, sanitizer re-serialization breaks the article scan.** The bs4-gated test runs selection on sanitized fixture HTML. If it fails, select the article from raw `fetched.text()` and sanitize only the slice (design-compatible: sanitization stays the web pre-pass). Record either outcome.
- **Phase 5, exception contract of `convert_arxiv_html`.** Pandoc-missing keeps `FileNotFoundError`; other failures become `ArxivConversionError`. Documented in the docstring and Implementation Notes.
- **Phase 6, image-count field and existing PDF images.** The shortcut returns before PDF image extraction, so `images/` holds only HTML images on that path. Confirm the field name on `PipelineResult` and that nothing else counts `images/` (for example `ImageCollector.total_image_count`, `pipeline.py:93-98`) on the shortcut path.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 0 Completion
**Completed:**
**Baseline:**

### Phase 1 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 2 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 3 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 4 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 5 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 6 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 7 Completion
**Completed:**
**Acceptance sweep (criterion → test):**
**Deviations:**

### Phase 8 Record
**Completed:**
**Result:**

---

**Status:** Draft → In Progress → Complete
