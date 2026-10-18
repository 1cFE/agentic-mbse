# Implementation Plan: Reliable arXiv extraction

**Work item:** ARXIV-EXTRACTION
**Status:** In Progress
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

- [x] Confirm the code still matches the base: `git diff --stat 8b027bbc HEAD -- src tests docs pyproject.toml` prints nothing.
- [x] Run `uv run pytest tests/ -q > /tmp/arxiv-baseline.txt 2>&1`.
- [x] Record below: pass/fail/skip counts, the node IDs of every failure and error, and whether failures come from environment (for example a missing `SYSIDE_LICENSE_KEY`) or code.
- [x] Record `pandoc --version` (expect 3.1.3) and the pymupdf version, since phase 1 and 3 tests depend on both.

**Baseline failure set:** 3 failures, all environmental (see Phase 0 Completion).

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

- [x] **Fixture** `tests/fixtures/arxiv_2610.14224v1_page.html` (NEW). Trim from `ref/2610.14224.html` per the design's trim note. Keep `<head>` and all chrome outside the article verbatim, including the page's one `data:` icon. Inside the article keep title, authors, abstract, two sections holding at least two figures with captions, one table and one math element, two bibliography entries and one appendix. Insert one tiny `data:image/png` `<img>` inside the article, marked by an HTML comment as the only synthetic edit. Open with a comment naming the source URL, fetch date (2026-10-18) and edits. Keep it under 80 KB. Do the trim with a throwaway script outside the repo; commit only the fixture.
- [x] **Tests** `tests/test_arxiv_html.py` (NEW): the stencil above. Pick the `CHROME` and `PAPER` strings by reading the fixture; each chrome string must appear in the page, so a bad trim fails loudly.
- [x] **Module** `src/agentic_mbse/extraction/arxiv_html.py` (NEW): `ArxivConversionError`, `MIN_CONTENT_CHARS = 100`, `select_article`, `_run_pandoc(html, pandoc_path)`, `convert_article`, and `_preprocess_html` / `_postprocess_markdown` moved verbatim from `pandoc_convert.py:33-63`. Stdlib only (the PDF route runs on a core install). No import of `pandoc_convert`.
  - `_run_pandoc` writes the temp file and calls `subprocess.run` (module-level `import subprocess`, so existing `patch("subprocess.run")` tests keep working). It does not call `shutil.which`. A missing Pandoc shows up as `FileNotFoundError` from `subprocess.run` and becomes `ArxivConversionError("Pandoc not found ...")`. This keeps tests that stub `subprocess.run` working on machines without Pandoc. Callers that need a silent availability check keep their own (`pandoc_convert._pandoc_available`).
  - `convert_article` = `select_article` → wrap as `<html><body>{article}</body></html>` → `_preprocess_html` → `_run_pandoc` → `_postprocess_markdown` → length check.
- [x] **`pandoc_convert.py`**: delete the moved helpers and import them from `arxiv_html` (keep the names importable from `pandoc_convert` until phase 5, so nothing else changes this phase). `convert_arxiv_html` (`:187-263`) keeps its fetch, its `_pandoc_available` → `FileNotFoundError` check and its whole-page conversion for now, but runs Pandoc through `_run_pandoc`.
- [x] **`web_backend.py`**: `_extract_with_arxiv_pandoc` (`:246-295`) and `_fallback_pandoc` (`:298-333`) call `_run_pandoc` and keep returning `None` on any failure. Remove the "keep flags in sync" comments.
- [x] **Test imports**: tests importing `_preprocess_html` / `_postprocess_markdown` from `pandoc_convert` switch to `arxiv_html` (Implementation Notes "Test migration").

### Validation

- [x] Green (see strategy). The Pandoc-free selection test runs and passes in every environment; the real-Pandoc test runs locally (Pandoc present).
- [x] `grep -n "pandoc_convert" src/agentic_mbse/extraction/arxiv_html.py` returns nothing (invariant 10).
- [x] `grep -n '"--markdown-headings=atx"' src/` hits only `arxiv_html.py` (one runner, D6).
- [x] Manual: `wc -c tests/fixtures/arxiv_2610.14224v1_page.html` is under ~80 KB; open the head comment and confirm source URL, date and the one synthetic edit are recorded. (87.8 KB; see Phase 1 Deviations)

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

- [x] **`types.py:107-124`**: `PipelineResult.warnings: list[str] = field(default_factory=list)`.
- [x] **`pipeline.py`**: `_try_arxiv_shortcut` (`:172-226`) returns `(PipelineResult | None, list[str])`. Warn on: ignored `--html-path` (Pandoc absent, `:188-189`), identified ID with no HTML available, and any exception (fetch error, conversion error). Keep the log line. Stay silent on no ID and on Pandoc absent without `--html-path`. `extract_pdf` (`:380-386` and the base-extraction error return at `:398`, and the normal return) attaches the warnings to whichever result it returns.
- [x] **`web_backend.py`**: when the arXiv Pandoc attempt fails or is short (`:414-417`), add an actionable warning to the result's warnings. Initialize `extraction_warnings` before Step 3 so fallback and image warnings share one list; it already flows into `metrics.json` (`:509-511`) and `ExtractionResult.warnings`. The `D16` skip of `_fallback_pandoc` waits for phase 5.
- [x] **`extract_cli.py`**: one helper (for example `_print_warnings(label, warnings)`) that writes to `sys.stderr`. Use it in the web route (replace the stdout block at `:240-243`) and in the PDF branch. In the PDF branch (`:500-531`), print warnings and write `metrics.json` (with `"warnings"` when non-empty) before the `if result.error` check at `:502`; on success the later `metrics.json` write includes the same warnings. The output dir already exists at that point (`:483`).

### Validation

- [x] Green.
- [x] Manual: run `uv run agentic-mbse extract <small local pdf> --budget 0 --html-path /tmp/does-not-exist.html -o /tmp/arxiv-p2`. The load fails, the run falls through to PDF extraction, stderr shows one warning, and `/tmp/arxiv-p2/<doc>/metrics.json` contains it.

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

- [x] **`tests/test_arxiv_identity.py`** (NEW): the stencil, all four design fixtures (citation-only, stamp plus cited prose ID, two stamps, stamp vs URL) plus the positive URL-only case. Generate PDFs in `tmp_path`; commit none.
- [x] **`pandoc_convert.py`**: add `ArxivIdentity` and `identify_arxiv_paper(pdf_path, pdf_source_url=None)` using `get_text("dict")` on page 1 only. `detect_arxiv_id` (`:71-105`) returns `identify_arxiv_paper(pdf_path).arxiv_id`. Drop the Creator-metadata fallback.
- [x] **`pipeline.py`**: `PipelineConfig.pdf_source_url: str | None = None` (append; touch no existing field). `_try_arxiv_shortcut` calls `identify_arxiv_paper(pdf_path, config.pdf_source_url)`; a conflict warns (D13); no evidence is silent.
- [x] **`extract_cli.py:487-499`**: pass `pdf_source_url=getattr(args, "source_url_override", None)`.
- [x] **Test migration**: `test_pipeline.py` tests that stub `detect_arxiv_id` (`:152-230`, `:730-750`, `:1463-1480`) stub `identify_arxiv_paper` returning an `ArxivIdentity`, or use generated PDFs. `test_check.py` stubs of `detect_arxiv_id` keep working through the wrapper until phase 7.

### Validation

- [x] Green.
- [x] Manual: generate the citation-only PDF and run `uv run agentic-mbse extract <pdf> --budget 0 -o /tmp/arxiv-p3` with Pandoc on PATH. `output.md` is the PDF's own text, not Harness², and no network call is made (run with networking unavailable, or watch for no `fetch` line).

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

- [x] **`pandoc_convert.py`**: `ARXIV_SHORTCUT_DEFAULT = True` and `resolve_arxiv_shortcut`.
- [x] **`pipeline.py`**: `PipelineConfig.arxiv_shortcut: bool | None = None` (append) and `__post_init__` raising `ValueError` for `arxiv_shortcut=False` with `arxiv_html_path` set. `_try_arxiv_shortcut` returns `(None, [])` before any work when `arxiv_shortcut is False`; it runs automatic detection only when `resolve_arxiv_shortcut(config.arxiv_shortcut)` is true; `arxiv_html_path` runs unless explicitly disabled.
- [x] **`extract_cli.py`**: add `--arxiv-shortcut/--no-arxiv-shortcut` (`argparse.BooleanOptionalAction`, `default=None`) near `--html-path` (`:793`); help text names the default by reading the constant. Reject the contradiction with `parser.error`-style exit 2 at the top of `cmd_extract` (exit code 2 is already used for `--check` FAIL; the test asserts the usage message, not only the code). Pass `arxiv_shortcut=args.arxiv_shortcut` into `PipelineConfig`. The `--check` probe takes the flag in phase 7.
- [x] Review the diff: the default's value is written only in `ARXIV_SHORTCUT_DEFAULT`; the field, the CLI default and the help text all read it or default to `None` (invariant 8).

### Validation

- [x] Green.
- [x] Manual: `uv run agentic-mbse extract --help` shows both flag forms and the default; `uv run agentic-mbse extract x.pdf --no-arxiv-shortcut --html-path y.html` exits 2 with a clear message.

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

- [x] **`arxiv_html.py`**: `ArxivSource` (with `from_fetch` and `image_base`), `load_arxiv_html(source, *, timeout)` calling `http.fetch_url` for URLs and reading the file for paths.
- [x] **`pandoc_convert.convert_arxiv_html`**: becomes the wrapper over `load_arxiv_html` and `convert_article`. Keep its signature, return type and the `_pandoc_available` → `FileNotFoundError` check (an existing test pins it at `tests/test_pandoc_convert.py:305-313`). Other failures now raise `ArxivConversionError` where they used to raise `CalledProcessError`; update the docstring. In-repo callers catch `Exception`, so no caller changes. `[AGENT]` plan decision: the design fixes signature and return type but not exception types; this is the narrowest change that keeps the pinned contract.
- [x] **`pipeline._try_arxiv_shortcut`**: load through `load_arxiv_html`, convert with `convert_article`, catch `ArxivConversionError` and fetch errors into warnings. Hash `source.raw_bytes`; compute fetched version as today (`:207-214`). Keep `raw_source_bytes` as the raw bytes.
- [x] **`web_backend.py`**: the arXiv branch (`:410-417`) builds `ArxivSource.from_fetch(fetched)`, runs `convert_article` on the sanitized HTML, and turns `ArxivConversionError` into a warning. For arXiv URLs skip Step 3b (`:423-432`). Delete `_extract_with_arxiv_pandoc`; replace `_MIN_CONTENT_LENGTH` with `arxiv_html.MIN_CONTENT_CHARS`. Saved `raw.html` (`:514-515`) stays `fetched.text()`.
- [x] **Remove the phase 1 re-exports** (none were created; see Phase 1 Deviations) of `_preprocess_html` / `_postprocess_markdown` from `pandoc_convert` once nothing imports them there.
- [x] **Test migration**: `tests/test_pandoc_convert.py:239-303` inputs wrap content in `<article class="ltx_document">…</article>` and stub Pandoc output of at least `MIN_CONTENT_CHARS`; that change is the intended R4 behavior, so record it in Implementation Notes. `test_pipeline.py` tests that stub `convert_arxiv_html` stub `arxiv_html.load_arxiv_html` / `convert_article` or `fetch_url` + `subprocess.run` instead.

### Validation

- [x] Green, including existing provenance tests (raw-byte hash, save-source, fetched version) unchanged.
- [x] Manual: `uv run agentic-mbse extract --html-path .project/active/arxiv-extraction/ref/2610.14224.html <stamp pdf> -o /tmp/arxiv-p5` (stamp PDF from the phase 3 helper). `grep -c "iVBORw0KGgoAAAANSUhEUgAAAAsAAAAO" /tmp/arxiv-p5/output.md` is 0 (the footer logo, the page's only chrome data URI), and `grep -E "Report Issue|Instructions for reporting errors|major funders" /tmp/arxiv-p5/output.md` finds nothing. `data:image/svg+xml` refs from LaTeXML pictures inside the article are paper content and may remain (invariant 6).

**What we know works after this phase:** both routes emit the paper alone; unrecognized pages fall back visibly; no path puts whole-page arXiv HTML through Pandoc.

---

## Phase 6: Image persistence in both routes

### Goal

Every figure in the converted article is saved once under `images/` and referenced by a relative path, in both routes; every image not saved keeps its original ref and warns once.

### Added by design amendment D17 (2026-10-18)

- [x] Test first: on the real fixture, every `<object type="image/svg+xml" class="ltx_graphics …">` inside the article (figures 5, 6, 7, 9 of 2610.14224) yields a markdown image ref after conversion, and is persisted like any other figure. Then implement the `<object>` → `<img>` rewrite in `arxiv_html` pre-processing (design D17).

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

- [x] **`arxiv_html.py`**: `fetch_image` (User-Agent from `http.USER_AGENT`, reads `max_bytes + 1`, raises on oversize and HTTP error), `ImagePersistResult`, and `persist_images`. Move `_MD_IMAGE_RE` from `web_backend.py:53` here. Keep `//` collapsing in the path; drop the hard-coded `https://arxiv.org` prefix (D7).
- [x] **`pipeline._try_arxiv_shortcut`**: when `config.extracted_images_dir` is set, run `persist_images(markdown, source.image_base, config.extracted_images_dir)`; set `image_count` from `saved_count`; append its warnings. Without an images dir, refs stay remote (documented limitation, phase 7). Check `PipelineResult`'s image-count field name in `types.py` before wiring.
- [x] **`web_backend.py`**: replace `_download_arxiv_images` (`:58-150`) with `persist_images(full_markdown, source.image_base, output_dir / "images")` at `:487-492`; delete the old function.
- [x] **Tests**: migrate `tests/test_web_images.py` cases into `tests/test_arxiv_html.py` against `persist_images` with an injected fetch; rewrite the duplicate-URL expectation to one file; delete `tests/test_web_images.py` once every case has a home. Add the CLI test that a failed image on each route shows in `metrics.json["warnings"]` and stderr.

### Validation

- [x] Green.
- [x] Manual: repeat the phase 5 `--html-path` run with a temp copy of the fixture next to a `2610.14224v1/` folder holding two small PNGs; `/tmp/arxiv-p6/images/` holds them, `output.md` refs `images/<name>`, and `metrics.json` reports the matching count.

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
- [ ] For each route record: fetched source URL and version (frontmatter), backend, saved image count versus files in `images/`, any dangling refs (`grep -o "](images/[^)]*)"` each checked for existence), data-URI refs by type (`grep -o "data:image/[a-z+]*" output.md | sort | uniq -c`): in-article `data:image/svg+xml` refs are expected and legitimate (LaTeXML pictures such as the title logo and inline diagrams; paper content under invariant 6), while the footer `[LOGO]` PNG (`iVBORw0KGgoAAAANSUhEUgAAAAsAAAAO`) and any other chrome data URI must be absent, chrome strings absent (`Report Issue`, footer and nav text chosen in phase 1), and every warning printed.
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
**Completed:** 2026-10-18
**Baseline:** at `423ceffa` (no diff from `8b027bbc` in `src tests docs pyproject.toml`): 3 failed, 2779 passed, 1 skipped, 14 deselected, 1 xfailed.

- `tests/test_equations.py::TestDetectEquations::test_returns_detected_equations`: environment, `PIL` is not installed in the venv.
- `tests/test_index.py::TestScriptBackwardCompat::test_generate_index_script_runs` and `::test_read_section_script_runs`: environment, the tests hard-code `cwd="/home/reid/1cfe/agentic-mbse"`, which does not exist on this machine.

Environment setup the numbers depend on, for later sessions:

- The worktree venv was created fresh. `uv sync --extra web --extra dev` is needed: without `[web]` the bs4/trafilatura tests fail, without `[dev]` there is no mypy.
- `SYSIDE_LICENSE_KEY` is not in this worktree. Without it 7 `tests/test_sysml/` modules error at collection and the run aborts. Source it per command from the main checkout: `set -a; . /home/reid/src/agentic-mbse/.env; set +a`.
- Pandoc is not on the default PATH. Pandoc 3.1.3 lives at `~/.local/opt/pandoc-3.1.3/bin`; prepend it to PATH so the real-Pandoc tests run instead of skipping.
- pymupdf 1.26.7.
- Lint and type baselines: `uv run mypy src/` reports 97 errors in 19 files at base (none in `arxiv_html.py`, `pandoc_convert.py`, `web_backend.py`, `pipeline.py`, `types.py`; pre-existing ones in `check.py` and `extract_cli.py`). `ruff format --check` already fails at base on `pandoc_convert.py`, `web_backend.py`, `pipeline.py`, `test_pipeline.py`, `test_extract_cli.py`, `test_web_backend.py` and `test_pandoc_convert.py`. "Clean on touched files" is read as: new files are formatted, and edits add no new lint or format findings; untouched pre-existing drift is not mass-reformatted.

### Phase 1 Completion
**Completed:** 2026-10-18
**Actual Changes:**
- New `src/agentic_mbse/extraction/arxiv_html.py`: `ArxivConversionError`, `MIN_CONTENT_CHARS`, `select_article` (fail-closed scan per D4), `_run_pandoc` (the one Pandoc command; `FileNotFoundError`, timeout and non-zero exit become `ArxivConversionError`), `convert_article`, and `_preprocess_html` / `_postprocess_markdown` moved verbatim. Stdlib only, no import of `pandoc_convert`.
- `pandoc_convert.py`: helpers deleted and imported from `arxiv_html`; `convert_arxiv_html` keeps its fetch, its `_pandoc_available` → `FileNotFoundError` check and whole-page conversion, and runs Pandoc through `_run_pandoc`.
- `web_backend.py`: `_extract_with_arxiv_pandoc` and `_fallback_pandoc` call `_run_pandoc` and still return `None` on failure. The "keep flags in sync" comments, the `shutil`/`tempfile` imports and the separate `_pandoc_available` pre-check are gone; a missing Pandoc now surfaces as `ArxivConversionError` from the runner.
- New fixture `tests/fixtures/arxiv_2610.14224v1_page.html` (87,828 bytes), trimmed by a throwaway script kept outside the repo (`/tmp/arxiv-trim/trim.py`).
- New `tests/test_arxiv_html.py` (24 tests): selection on the real fixture (8 chrome markers asserted present in the page and absent from the slice, 10 paper markers present), 7 fail-closed shapes, case/quote tolerance, the runner's command and three failure modes, `convert_article`'s article-only input and failure modes, and the real-Pandoc fixture conversion. The `_preprocess_html` / `_postprocess_markdown` test classes moved here from `tests/test_pandoc_convert.py`.
- Full suite: 2797 passed, same 3 baseline failures. mypy unchanged at 97 (none in touched files). New files formatted; ruff clean on touched files.

**Issues:**
- **Premise issue for Phase 6 (B4), surfaced and parked.** Real Pandoc on the fixture drops figures that LaTeXML emits as `<object type="image/svg+xml" data="2610.14224v1/<file>.svg">`. On 2610.14224 that is 4 of 9 figures (Figures 5, 6, 7, 9): their captions survive, but no image ref of any kind is produced, so Phase 6's `persist_images` will never see them. B4 says such a figure "keeps a remote ref"; in fact it disappears. Today's routes lose the same figures, so Phases 1–2 do not change this. It works against the spec's "no missing figures" goal. A likely fix is a targeted rewrite of SVG `<object>` to `<img src=...>` in `_preprocess_html`, which is a design change to decide before Phase 6. Phase 6's image-count expectations depend on this decision.
- **Phase 8 expectation is wrong for this paper.** LaTeXML inline `<svg>` pictures inside the article (the title logo, a Section 1 picture) come out of Pandoc as `data:image/svg+xml` refs. Under invariant 6 they are paper content and stay. Phase 8's "`grep -c data:image` … 0 for this paper" should expect these in-article SVG data URIs and check only that chrome data URIs (the footer `[LOGO]` PNG) are absent.

**Deviations:**
- Fixture size is 87.8 KB, over the ~80 KB aim. Chrome is verbatim except nested TOC entries. The only small table (Table 3) is in Section 4, so the kept sections are Section 1 (Figure 2) and Section 4 (Table 3, math, Figure 8 as `<img>`), plus the front-matter teaser figure, the first two bibliography entries and Appendix B. The page's "contents of the appendix" banner between the bibliography and Appendix A was deleted with the other content.
- The stencil's `ltx_page_footer` chrome string does not occur on the real page; the footers are `arxiv-html-footer` and `ds-site-footer`, and those are asserted instead.
- No re-export of `_preprocess_html` / `_postprocess_markdown` from `pandoc_convert`. Nothing outside it needed them there once `web_backend` imports them from `arxiv_html` and their tests moved, so Phase 5's "remove the phase 1 re-exports" step has nothing left to do.
- **Exception contract (accepted deviation, for the changelog):** `convert_arxiv_html` now raises `ArxivConversionError` where it raised `subprocess.CalledProcessError` (non-zero Pandoc exit) or let `subprocess.TimeoutExpired` escape. This lands in Phase 1 rather than Phase 5 because the shared runner owns those failures. Pandoc missing still raises `FileNotFoundError` from the pre-check. In-repo callers catch `Exception`.
- The real-Pandoc test imports `_MD_IMAGE_RE` from `web_backend` until Phase 6 moves it into `arxiv_html`.

### Phase 2 Completion
**Completed:** 2026-10-18
**Actual Changes:**
- `types.py`: `PipelineResult.warnings: list[str]` (appended after the provenance fields).
- `pipeline.py`: `_try_arxiv_shortcut` returns `(PipelineResult | None, list[str])`. It warns on an ignored `arxiv_html_path` (Pandoc absent), an identified ID with no HTML version, and any exception (message carries the exception text). It stays silent on no ID and on Pandoc absent without `arxiv_html_path`. The debug log line with traceback is kept. `extract_pdf` attaches the shortcut warnings to the shortcut result, the base-extraction error result and the normal result.
- `arxiv_html.py`: new `_convert_document(document, pandoc_path)` = pre-process → `_run_pandoc` → post-process → `MIN_CONTENT_CHARS` check. `convert_article` now selects, wraps and calls it.
- `pandoc_convert.convert_arxiv_html` and the web route's arXiv branch both call `_convert_document`, so the pre/run/post sequence exists once.
- `web_backend.py`: `_extract_with_arxiv_pandoc` deleted (the web arXiv branch calls `_convert_document` directly); `_MIN_CONTENT_LENGTH` replaced by `arxiv_html.MIN_CONTENT_CHARS`. An `ArxivConversionError` in the arXiv branch adds `arXiv Pandoc conversion failed (<reason>); used trafilatura instead` to `extraction_warnings`, which is now created before Step 3 and later extended with image warnings. It already flows into `metrics.json` and `ExtractionResult.warnings`.
- `extract_cli.py`: `_print_warnings(label, warnings)` writes to stderr and serves both routes; the web route's stdout warning block is gone. The PDF branch prints warnings and writes `metrics.json` (with `"warnings"` when non-empty) before `if result.error`; the later duplicate `metrics.json` write was removed, so there is one write.
- Tests: `test_pipeline.py` (existing shortcut tests now assert their warnings or their absence; new: ignored `--html-path`, warnings on a base-extraction error result, and a real generated PDF with an unreadable `arxiv_html_path` through the real pipeline). `test_web_backend.py` (real fixture page at an arXiv URL with Pandoc missing, short output and a Pandoc error: backend stays `trafilatura`, one warning in the result and in `metrics.json`; a non-arXiv page has no warning). `test_extract_cli.py` new `TestWarningsChannel` (PDF error result keeps warnings in stderr and `metrics.json` with no `output.md`; success with warnings; no warnings means no key and empty stderr; a real PDF through `cmd_extract` with a missing `--html-path`; web warnings on stderr only). `test_pandoc_convert.py` stubs now return at least `MIN_CONTENT_CHARS`, plus a short-output test.
- Full suite: 2810 passed, same 3 baseline failures. mypy unchanged at 97. ruff clean on touched files; format hunk counts on touched files are at or below base.
- Manual check run: `extract /tmp/arxiv-trim/small.pdf --budget 0 --html-path /tmp/does-not-exist.html -o /tmp/arxiv-p2` exits 0, stdout shows `[pdf_pipeline]`, stderr shows exactly one warning naming the missing file, and `metrics.json` contains it.

**Issues:**
- The first manual run showed a full traceback on stderr because I had raised the shortcut's log line to `warning`. The warning channel already tells the user; the log line went back to `debug` with `exc_info`, as before.
- Until Phase 3, `detect_arxiv_id` is still the weak first-page regex. So a citation-only PDF whose cited paper has no HTML version now gets the "identified but arXiv serves no HTML version" warning. Phase 3 removes the false identification and with it this warning.

**Deviations:**
- The minimum-length check now applies to `convert_arxiv_html`, so the PDF shortcut falls back with a warning on Pandoc output under 100 characters. The plan scheduled this with Phase 5's test migration. It came earlier because routing both arXiv conversions through `_convert_document` removed the last copy of the pre/run/post sequence. Changelog note: `convert_arxiv_html` raises `ArxivConversionError` for output under `MIN_CONTENT_CHARS`.
- `_extract_with_arxiv_pandoc` and `_MIN_CONTENT_LENGTH` were removed in this phase rather than Phase 5. Phase 5 swaps the web branch's `_convert_document(html)` for `convert_article` on the `ArxivSource`.
- `_try_arxiv_shortcut` still catches `Exception` (now with a warning instead of silence). Phase 5 narrows it to `ArxivConversionError` and the loader's fetch/read errors when the loader lands.
- PDF `metrics.json` is now written for error results too (zero metrics, plus warnings when present). The skip check keys on `output.md`, so a failed document is still retried on the next run.

### Phase 3 Completion
**Completed:** 2026-10-18. Code and tests written by the implement session; tests run and verified by the orchestrator because the resumed session lost test permission (harness issue).
**Actual Changes:** `identify_arxiv_paper` and `ArxivIdentity` in `pandoc_convert.py` (stamp + arxiv.org source URL per D1; `detect_arxiv_id` is a thin wrapper; Creator-metadata fallback removed). `PipelineConfig.pdf_source_url` added (no field renamed/removed). Shortcut uses the identity rule and warns on conflict; CLI fills `pdf_source_url` from fetched PDF URLs. New `tests/helpers/arxiv_pdfs.py` (generated stamp PDFs), `tests/test_arxiv_identity.py`; real-PDF pipeline tests show citation-only and conflict PDFs never reach the HTML check or Pandoc, and a stamp substitutes its own ID. Old mock-based `TestDetectArxivId` removed.
**Issues:** None in code. Verification: focused extraction suites 318 passed; full suite 2833 passed, 3 failed (the same 3 environmental baseline failures), 1 skipped. Ruff: only the pre-existing `index.py` N806. mypy: 97 errors, equal to baseline.
**Deviations:** None. Manual check (orchestrator): citation-only PDF with Pandoc 3.1.3 on PATH extracted via `pdf_pipeline`, 49 chars of its own text, no Harness² content.

### Phase 4 Completion
**Completed:** 2026-10-18
**Actual Changes:**
- `pandoc_convert.py`: `ARXIV_SHORTCUT_DEFAULT = True` (the only place the default is written; invariant 8) and `resolve_arxiv_shortcut(explicit)`, which reads the constant at call time.
- `pipeline.py`: `PipelineConfig.arxiv_shortcut: bool | None = None`, appended after `pdf_source_url`; no existing field touched (invariant 9). `__post_init__` raises `ValueError` for `arxiv_shortcut=False` with `arxiv_html_path`. `_try_arxiv_shortcut` returns `(None, [])` before any other work (Pandoc probe, identity, HEAD probe) when there is no `arxiv_html_path` and `resolve_arxiv_shortcut(config.arxiv_shortcut)` is false. One check covers both explicit opt-out and a default-off build, because opt-out with an HTML path cannot exist. An explicit `arxiv_html_path` runs under either default.
- `extract_cli.py`: `--arxiv-shortcut/--no-arxiv-shortcut` (`argparse.BooleanOptionalAction`, `default=None`) after `--html-path`. Its help explains the evidence rule and the contradiction, and names the default by reading `pandoc_convert.ARXIV_SHORTCUT_DEFAULT` at registration (module attribute, not a value import, so a flip changes the help). `cmd_extract` rejects `--no-arxiv-shortcut` with `--html-path` first thing, printing an argparse-style `agentic-mbse extract: error: …` line to stderr and returning the new `EXIT_USAGE = 2`. `PipelineConfig` gets `arxiv_shortcut=args.arxiv_shortcut`.
- Tests:
  - `test_pipeline.py::TestShortcutControl` runs real stamp PDFs through `_run_shortcut`. That helper was lifted out of `TestArxivIdentityInPipeline._run` so both classes share it. The class covers opt-out skipping identity, the HTML probe and Pandoc with no warning; the `ValueError`; `resolve_arxiv_shortcut` under both constant values; the shipped default being on; a default-off build skipping detection; explicit on overriding default off; and `arxiv_html_path` running under default off.
  - `test_extract_cli.py::TestArxivShortcutFlag` covers the contradiction (exit 2, message names both flags, `extract_pdf` not called), forwarding of `None/True/False` into `PipelineConfig`, forwarding through a PDF URL and through a `--urls-from` batch, help naming `on`/`off` from the constant, and parser defaults for both forms.
  - The `MockArgs` stubs in `test_extract_cli.py`, `test_check.py` and `test_profile.py` gained `arxiv_shortcut=None`.
- Full suite: 2849 passed, same 3 baseline failures. mypy unchanged at 97. ruff clean on touched files; format hunk counts at or below base.
- Manual: `extract --help` shows `[--arxiv-shortcut | --no-arxiv-shortcut]` and "(default: on)". `extract small.pdf --no-arxiv-shortcut --html-path y.html` exits 2 with the error line and creates no output directory.

**Issues:**
- **Pre-existing bug fixed: batch PDF URLs recursed forever.** `_extract_pdf_url` shallow-copies `args` and calls `cmd_extract`, but the copy kept `urls_from`, so `cmd_extract` re-entered batch mode on the same file (`RecursionError`). The new batch forwarding test found it. A PDF URL inside `--urls-from` never worked before this. The fix sets `pdf_args.urls_from = None` on the copy. The plan's premise that the flag reaches batch inputs "with no extra plumbing" holds once the recursion is gone.

**Deviations:**
- Exit 2 comes from a named `EXIT_USAGE` constant in `extract_cli.py` rather than a bare `2`. The `--check` FAIL path still returns a literal `2` as before; it was left untouched.
- `--check` does not take the flag yet; that is Phase 7 as planned.

### Phase 5 Completion
**Completed:** 2026-10-18
**Actual Changes:**
- `arxiv_html.py`:
  - New `ArxivSource` (frozen: `raw_bytes`, `html`, `serving_url`). `from_fetch` normalizes the serving URL: a trailing slash after `arxiv.org/html/<id>[vN]` is dropped (B5); other URLs are untouched. `image_base` joins any `<base href>` onto the serving URL.
  - New `load_arxiv_html(source, *, timeout)`. http(s) strings go through `http.fetch_url`; anything else is read as a local file whose serving URL is its `file://` URI.
  - The module now imports `http` (stdlib-only) and still never imports `pandoc_convert`.
- `pandoc_convert.convert_arxiv_html`: now the thin wrapper, `_pandoc_available` → `FileNotFoundError`, then `load_arxiv_html`, then `convert_article`. Signature and return type are unchanged, and it returns the raw fetched bytes. Its bare-`urllib` fetch is gone. Docstring updated.
- `pipeline._try_arxiv_shortcut`:
  - Loads through `load_arxiv_html` (the `arxiv_html_path` Path or the probed URL) and converts with `convert_article`.
  - The `try` now covers only identification, loading and conversion, and catches `ArxivConversionError`, `OSError` (fetch, HTTP and file errors), `UnicodeDecodeError` and `pymupdf.FileDataError` (an unreadable PDF during identification). Each becomes the existing warning. The Phase 2 `except Exception` is gone.
  - Provenance is built outside the `try` from `source.raw_bytes` and `source.html`, so a bug there raises instead of turning into a warning.
- `web_backend.py`:
  - The arXiv branch runs `convert_article` on the (sanitized) page. Its warning now reads `arXiv paper conversion failed (<reason>); used trafilatura instead`.
  - The whole-page Pandoc fallback (Step 3b) is skipped for arXiv URLs (D16, invariant 11).
  - Image download resolves against `ArxivSource.from_fetch(fetched).serving_url` instead of the raw `final_url`. The `_convert_document` import is gone, so `_convert_document` is now private to `arxiv_html`. Saved `raw.html` and the hash still use the fetched page.
- Tests:
  - `test_arxiv_html.py`: `TestArxivSource` (raw bytes kept, trailing slash dropped on arXiv only, `<base href>` absolute and relative), `TestLoadArxivHtml` (URL through `fetch_url` with timeout and post-redirect URL, local file URI, str path, missing file), and a bs4-gated check that selection survives `strip_hidden_content` on the real fixture.
  - `test_pandoc_convert.py::TestConvertArxivHtml` rewritten around article-shaped pages. It checks that only the article reaches Pandoc, that the raw bytes include the chrome, that URLs go through `fetch_url`, pre/post-processing, the short-output error, a no-article page raising before Pandoc, and missing Pandoc.
  - `test_pipeline.py`: the `convert_arxiv_html` stubs are replaced by the fetch boundary (`arxiv_html.fetch_url` serving the real fixture) plus the Pandoc subprocess. The two `RuntimeError("boom")` identity stubs became a realistic `URLError` from the fetch. New `TestShortcutPaperOnly` covers real-Pandoc article-only output from a stamp PDF, no-article fallback with a warning and no Pandoc call, provenance (raw bytes, sha256 and fetched `v1` source URL), and an unreadable PDF warning while base extraction reports the error.
  - `test_web_backend.py`: real-Pandoc paper-only web output, unrecognized container falling back to trafilatura with the warning in `metrics.json`, arXiv short output never calling `_fallback_pandoc`, a non-arXiv short page still using it, raw bytes and hash equal to the fetched page, and figure refs resolving against the normalized trailing-slash URL.
- Full suite: 2873 passed, same 3 baseline failures. mypy at 97. ruff clean on touched files. Format hunks are at or below base except that `test_pandoc_convert.py` is now fully formatted; its one pre-existing hunk sat in the class this phase rewrote.
- Manual: `extract --html-path ref/2610.14224.html <stamp pdf> --budget 0 -o /tmp/arxiv-p5` gives `[pandoc_arxiv]` with 242,611 characters and 15 `##` sections. The footer logo PNG and the chrome strings (`Report Issue`, `Instructions for reporting errors`, `major funders`) occur 0 times. 12 `data:image/svg+xml` refs remain, all LaTeXML pictures inside the article (title logo, diagrams). The investigation's whole-page run had 16 chrome data-image refs.

**Issues:**
- **Premise issue for D17 on the web route, surfaced for Phase 6.** `html_sanitize.strip_hidden_content` (the web route's default pre-pass) deletes every `<object>` tag as a "dangerous tag" (`html_sanitize.py:36`). It runs before article selection, so on the web route the SVG figure objects D17 rewrites are already gone when `arxiv_html` pre-processing runs. D17 as written would fix the PDF route only. Options for Phase 6: rewrite SVG objects to `<img>` before sanitizing (in `arxiv_html`, applied by the web route ahead of `strip_hidden_content`); or select the article from the raw page and sanitize only the slice with the rewrite first; or exempt `ltx_graphics` SVG objects from the sanitizer. This is a design decision, so it is left to Phase 6 and not resolved here.
- When an arXiv page's article conversion fails and trafilatura returns nothing, the extraction fails as before (D16). That error result carries no warnings, because `ExtractionResult` error returns never did. The failure itself is reported.

**Deviations:**
- The web route sanitizes before selecting the article, as the plan expected; the bs4 selection test confirms the article survives sanitizing.
- `arxiv_html_path` is passed to the loader as a `Path`. A URL given as `--html-path` was never supported, because `Path("https://…")` collapses `//`. This phase doesn't change that.
- The plan's `test_pipeline.py` migration option "stub `load_arxiv_html` / `convert_article`" was not used. Tests stub the network (`fetch_url`) and Pandoc (`subprocess.run`) boundaries instead, so the loader, selection and pre/post-processing run for real.
- **For the changelog:** `convert_arxiv_html` now converts only the page's `<article class="ltx_document">` and raises `ArxivConversionError` for a page without one. URLs are fetched through `http.fetch_url`, which honors the response charset and sends the same User-Agent. Web warnings for a failed arXiv conversion now say "arXiv paper conversion failed".

### Phase 6 Completion
**Completed:** 2026-10-18
**Acceptance (orchestrator brief):** on the real fixture, all 9 figures of 2610.14224, including the SVG Figures 5, 6, 7 and 9, end up as relative `images/<name>` refs to files that exist. The saved count equals the files written, in both routes. One shared assertion (`tests/helpers/arxiv_page.py::assert_all_figures_saved`) checks this in three places, each through real Pandoc:
- `test_arxiv_html.py::test_all_nine_fixture_figures_persist` (module level)
- `test_web_backend.py::test_arxiv_web_route_outputs_paper_only_with_all_figures_saved` (web route, real sanitizer)
- `test_pipeline.py::TestShortcutFigures::test_all_nine_figures_saved_with_real_pandoc` (PDF route)

**Actual Changes:**
- `arxiv_html.py`:
  - New `extract_article(html)` = `select_article` plus the D17 rewrite. Each `<object>` with `type="image/svg+xml"`, class `ltx_graphics` and a `data` URL becomes `<img src=… alt=… id class width height>`. The alt is the object's fallback text, or "Refer to caption". Other objects are untouched. It raises `ArxivConversionError("no recognized arXiv article container")`.
  - `convert_article` now takes the extracted article fragment, not the page. `_convert_document` was folded into it, since it had no other caller.
  - Image persistence added: `_MD_IMAGE_RE` (moved from `web_backend`), `MAX_IMAGE_BYTES`, `ImageFetcher`, `ImageFetchError`, `fetch_image(url, *, max_bytes, timeout)` (User-Agent from `http.USER_AGENT`, reads `max_bytes + 1`), `ImagePersistResult`, and `persist_images(markdown, base, images_dir, fetch)`.
  - `persist_images` resolves each ref with `urljoin(base, ref)` and collapses `//` in the path. Distinct URLs are read once: http(s) through `fetch`, `file:` copied from disk, any other scheme a warning. A colliding basename gets `stem_N.ext`. Saved refs become `images/<name>` with their attribute block kept. A URL that can't be saved leaves every one of its refs byte-identical and adds one warning. `data:` refs are never touched.
- D17a step order in both routes:
  - `convert_arxiv_html` and the PDF shortcut call `convert_article(extract_article(source.html))`.
  - The web arXiv branch calls `extract_article(fetched.text())` on the raw page, sanitizes only that slice (when `sanitize`), then `convert_article`. The whole-page sanitize still feeds trafilatura and metadata. Raw-byte save and hash are unchanged.
- `pipeline._try_arxiv_shortcut`: when `extracted_images_dir` is set, runs `persist_images(markdown, source.image_base, extracted_images_dir, fetch_image)`. It sets `PipelineResult.image_count` from `saved_count` and returns the image warnings, which `extract_pdf` attaches to the result. Without an images dir, refs stay as the page wrote them.
- `web_backend.py`: Step 4a calls `persist_images(full_markdown, ArxivSource.from_fetch(fetched).image_base, output_dir / "images", fetch_image)`. `_download_arxiv_images`, its `_MD_IMAGE_RE` and the now-unused `urllib.request`/`urljoin` imports were deleted. The file is fully ruff-formatted, as it was at base.
- `persist_images` takes the fetcher as a required argument rather than a default. Each route passes `fetch_image`, and the tests stub the name in that route's namespace (`web_backend.fetch_image`; `arxiv_html.fetch_image` for the PDF route, which imports it at call time). A bound default argument could not have been stubbed that way.
- Fixture `tests/fixtures/arxiv_2610.14224v1_page.html` regenerated (115,118 bytes). It adds Section 2's heading and intro plus subsection 2.2 (Figures 3 and 4), so all nine figures are present. The trim script is `/tmp/arxiv-trim/trim_v2.py`, and the head comment records the change.
- Tests:
  - New `tests/helpers/arxiv_page.py`: fixture path, the nine `FIGURES`, a `serve_figure` stub and `assert_all_figures_saved`.
  - `test_arxiv_html.py`: `TestExtractArticle` (real fixture: four objects rewritten, all nine figure `src`s present, exact `<img>` for Figure 5; fallback text as alt; non-`ltx_graphics` and non-SVG objects untouched; no article raises). `TestConvertArticle` on fragments; its real-Pandoc test now requires the nine figure refs in page order. `TestPersistImages` (14 cases: attributes kept, root-relative and absolute, same URL twice gives one fetch and one file, same URL failing gives one warning and both refs kept, partial failure, `_2`/`_3` collisions, `//` collapse, `data:` untouched, no-op, local HTML with `<base href>` covering absolute/relative/based/root-relative/missing, local HTML without base, unsupported scheme). `TestFetchImage` (User-Agent, oversize raises, oversize through persist). Every `tests/test_web_images.py` case has a home here, so that file is deleted.
  - `test_web_backend.py`: the nine-figure web acceptance; one failed SVG figure (count 8, ref kept, warning in result and `metrics.json`); the trailing-slash serving URL test now asserts the fetched figure URL; the version-provenance test stubs `extract_article` (its 1 KB fixture has no article).
  - `test_pipeline.py::TestShortcutFigures`: nine-figure PDF acceptance, a failed figure, no images dir (nothing fetched, refs kept), and `--html-path` copying local figures without fetching.
  - `test_extract_cli.py::TestFigureWarningsThroughCli`: one failed figure on each route reaches `metrics.json["warnings"]` and stderr, and the saved one is on disk and referenced.
- Full suite: 2892 passed, same 3 baseline failures. mypy at 97. ruff clean on touched files. Format hunk counts are at or below base on touched files; new files are fully formatted.
- Manual: copied the fixture to `/tmp/arxiv-p6-page/paper.html` with `2610.14224v1/{intro_teaser,components}.png` beside it, then ran `extract --html-path … stamp.pdf --budget 0 -o /tmp/arxiv-p6`. Exit 0. `images/` holds exactly those two files, `output.md` refs `images/intro_teaser.png` and `images/components.png`, and stderr and `metrics.json` carry 7 warnings, one per missing figure, each naming its `file://` URL.

**Issues:**
- **Saved-image count is not in `metrics.json` or CLI output.** The plan's manual step expected "`metrics.json` reports the matching count". It doesn't, on either route: `metrics.json` comes from `compute_metrics` (its `figure_ref_count` counts refs, including in-article data URIs), and neither CLI summary prints `image_count`. The count is reported on `PipelineResult.image_count` and `ExtractionResult.image_count`, which the acceptance tests check against the files. This was not changed here; Phase 7's acceptance sweep flags it against the spec row "report matching saved-image counts".

**Deviations:**
- `convert_article` changed contract from page to article fragment, and `extract_article` is new (design D3 listed `convert_article(html)` on the page). D17a needs a step between selection and conversion where the web route sanitizes, so selection-plus-rewrite and conversion became two calls. Neither function branches on the route.
- `persist_images` signature: `fetch` is a required positional argument, and the fetcher is called as `fetch(url)`, using `fetch_image`'s own size and timeout defaults (design sketch: `fetch=fetch_image` keyword default).
- The fixture grew past the ~80 KB aim to 115 KB so the nine-figure acceptance could run on it.

### Phase 7 Completion
**Completed:**
**Acceptance sweep (criterion → test):**
**Deviations:**

### Phase 8 Record
**Completed:**
**Result:**

---

**Status:** Draft → In Progress → Complete
