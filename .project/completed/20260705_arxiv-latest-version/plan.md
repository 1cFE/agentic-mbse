# Implementation Plan: Fetch Latest arXiv Version

**Status:** Draft
**Created:** 2026-07-05
**Last Updated:** 2026-07-05

## Source Documents
- **Spec:** `.project/active/arxiv-latest-version/spec.md`
- **Design:** `.project/active/arxiv-latest-version/design.md` ← component details, decisions, invariants

## Implementation Strategy

**Phasing Rationale:**
Build the two pure helpers first and prove the shakiest link (recovering the
fetched version from real served HTML, `design.md#key-bets` B2) before wiring
any call site. Then wire the narrower PDF path (mockable HEAD, small data flow),
then the web path (fetch-ordering + retry + provenance — most moving parts).

**Critical Path:**
`strip_arxiv_version` + `resolve_fetched_version` (P1) → PDF path uses them (P2)
→ web path uses them (P3). Nothing downstream works until the helpers exist.

**First Proof Point:**
Phase 1 test: `resolve_fetched_version(<saved arxiv HTML>, "1706.03762")` returns
`7`. If the version can't be read from a real page, provenance degrades and we
revisit before wiring (design flags this as the risk to de-risk first).

**Overall Validation Approach:**
- Each phase starts with tests.
- Automated (`uv run pytest`, `ruff`, `mypy`) + manual per phase.
- Network integration tests marked `slow` so the default suite stays offline.

---

## Phase 1: Pure Helpers + Unit Tests

### Goal
Add `strip_arxiv_version` and `resolve_fetched_version` to `pandoc_convert.py`
(see `design.md#component-overview`). No I/O. Prove version recovery against a
real saved arXiv HTML page.

### Assumption Under Test
The served latest HTML exposes its version in `{id}vN/` asset paths well enough
to recover it (B2). A figure-less page returns `None` cleanly.

### Test Stencil (Write This First)
```python
# tests/test_pandoc_convert.py — new classes
class TestStripArxivVersion:
    def test_versioned_id(self):
        assert strip_arxiv_version("2401.12345v3") == ("2401.12345", 3)
    def test_bare_id_unchanged(self):
        assert strip_arxiv_version("2401.12345") == ("2401.12345", None)
    def test_versioned_html_url(self):
        assert strip_arxiv_version("https://arxiv.org/html/2401.12345v2") \
            == ("https://arxiv.org/html/2401.12345", 2)

class TestResolveFetchedVersion:
    def test_recovers_from_asset_path(self):
        html = '<img src="1706.03762v7/x1.png">'
        assert resolve_fetched_version(html, "1706.03762") == 7
    def test_none_when_no_asset_path(self):
        assert resolve_fetched_version("<p>no figures</p>", "1706.03762") is None
```

### Changes Required

**See `design.md#implementation-notes`** for the exact regexes (id strip
`^(\d{4}\.\d{4,5})v(\d+)$`; URL sub `(/html/\d{4}\.\d{4,5})v\d+`; version recover
`{id}v(\d+)/`).

#### 1. Test fixture
**File:** `tests/fixtures/arxiv_1706.03762_latest.html` (NEW)
- [x] Save a trimmed real arXiv HTML page that contains `1706.03762v7/…` asset
      paths (a few `<img src>` lines are enough — no need for the full 186 KB).

#### 2. Test file
**File:** `tests/test_pandoc_convert.py` (extend)
- [x] Add `TestStripArxivVersion` and `TestResolveFetchedVersion` (stencil above).
- [x] Add one test loading the fixture → `resolve_fetched_version` returns `7`.

#### 3. Implementation
**File:** `src/agentic_mbse/extraction/pandoc_convert.py`
- [x] Add `strip_arxiv_version(id_or_url) -> tuple[str, int | None]` (pure).
- [x] Add `resolve_fetched_version(html, bare_id) -> int | None` (pure).

### Validation
**Automated:**
- [x] `uv run pytest tests/test_pandoc_convert.py` → new tests pass
- [x] `uv run pytest tests/` → no regressions
- [x] `uv run ruff check src/ tests/` and `uv run mypy src/` → pass

**Manual:**
- [x] In a REPL, `resolve_fetched_version(open(fixture).read(), "1706.03762")` → `7`
      (covered by `test_recovers_from_real_fixture`)

**What We Know Works After This Phase:**
Version strip (id + URL forms) and version recovery from a real page — the B2
risk is resolved before any wiring.

---

## Phase 2: PDF Path

### Goal
Make the PDF-derived arXiv shortcut fetch latest and record the resolved
version. See `design.md#architecture` (PDF path) and `#component-overview`.

### Assumption Under Test
Stripping to bare in `check_arxiv_html` still resolves (HEAD 200), and the D5
fallback to the versioned URL fires when bare is unavailable.

### Test Stencil (Write This First)
```python
# tests/test_pandoc_convert.py — update TestCheckArxivHtml
def test_strips_to_bare_and_returns_bare(self, mock_urlopen):
    # HEAD bare → 200
    result = check_arxiv_html("2510.07314v1")
    assert result == "https://arxiv.org/html/2510.07314"   # was v1

def test_falls_back_to_versioned_when_bare_unavailable(self, mock_urlopen):
    # HEAD bare → 404, HEAD versioned → 200
    result = check_arxiv_html("2510.07314v1")
    assert result == "https://arxiv.org/html/2510.07314v1"
```

### Changes Required
**See `design.md#key-decisions`** (D5 fallback) and `#required-invariants`.

**Specific file changes:**
- [x] `pandoc_convert.py` `check_arxiv_html()`: strip to bare, HEAD bare;
      on non-200/error, HEAD the original versioned URL; return whichever is 200.
      (Split the HEAD probe into `_arxiv_html_head_ok()` mechanism helper.)
- [x] `tests/test_pandoc_convert.py`: **replaced** `test_returns_url_on_200` with
      `test_strips_to_bare_and_returns_bare` (expects bare URL); added
      `test_falls_back_to_versioned_when_bare_unavailable`; added `_mock_head()`.
- [x] `pipeline.py` `_try_arxiv_shortcut()`: after `convert_arxiv_html`,
      `resolve_fetched_version(raw_bytes.decode(...))` and set
      `source_url = f"https://arxiv.org/html/{bare_id}v{n}"` when `n` found,
      else keep the fetched URL. (`bare_id` from `strip_arxiv_version`.)
- [x] `check.py` `probe_pandoc()`: confirmed no change needed — it consumes the
      URL `check_arxiv_html` returns; tests still pass.

### Validation
**Automated:**
- [x] `uv run pytest tests/test_pandoc_convert.py tests/test_pipeline.py tests/test_check.py` → 186 passed
- [x] `uv run pytest tests/` → no regressions (1201 passed / 1 skipped)
- [x] `ruff` → pass (mypy pre-existing errors unrelated to these files)

**Manual:**
- [ ] `uv run agentic-mbse extract --check <arxiv-pdf>` (redirect to temp file per
      CLAUDE.md) → probe reports arXiv HTML converted. *(deferred to end-to-end
      manual check; unit-covered)*

**What We Know Works After This Phase:**
PDF-derived extraction fetches latest, falls back to the pinned version if bare
is gone, and records the resolved version in provenance.

---

## Phase 3: Web Path

### Goal
Normalize the arXiv URL before fetching, retry the original on failure, and
write the versioned `source`. See `design.md#architecture` (web path) and
`#implementation-notes` (ordering gotcha).

### Assumption Under Test
Normalizing `url` before the step-1 fetch upgrades to latest without breaking
the step-3 routing (which keys on `final_url`), and bare/non-arXiv URLs are
unaffected.

### Test Stencil (Write This First)
```python
# tests/test_web_backend.py
def test_versioned_arxiv_url_normalized_before_fetch(monkeypatch):
    seen = {}
    def fake_fetch(u, **k): seen["url"] = u; return FetchResult(b"<img src='2401.00001v5/x.png'>", u, "text/html")
    monkeypatch.setattr(web_backend, "fetch_url", fake_fetch)
    extract_web_content("https://arxiv.org/html/2401.00001v1", output_dir=tmp)
    assert seen["url"] == "https://arxiv.org/html/2401.00001"   # stripped

def test_non_arxiv_url_untouched(monkeypatch): ...   # regression
```

### Changes Required
**See `design.md#implementation-notes`** — normalize BEFORE the step-1 fetch
(`web_backend.py:362`), not at the `:386` route check.

**Specific file changes:**
- [x] `web_backend.py` `extract_web_content()`: before fetch, if the URL is a
      versioned arXiv HTML URL, `strip_arxiv_version` → fetch bare; a
      `[bare, original]` candidate list retries the original on bare failure
      (D5). Flat loop, no nested try/except.
- [x] `web_backend.py` (frontmatter build): when `backend == "pandoc-arxiv"`, set
      `source` to the versioned URL via `resolve_fetched_version(html, bare_id)`
      (`bare_id` from new `_ARXIV_ID_IN_URL_RE`); fall back to `final_url`.
- [x] `web_backend.py`: `log.info` the upgrade (`requested vN → fetched vM`) when
      requested and resolved versions differ (D4 silent-upgrade visibility).
- [x] `tests/test_web_backend.py`: normalization test, non-arXiv regression test,
      D5 fallback test, versioned-`source` test.

### Validation
**Automated:**
- [x] `uv run pytest tests/test_web_backend.py tests/test_web_images.py` → 33 passed
- [x] `uv run pytest tests/` → no regressions (1205 passed / 1 skipped)
- [x] `ruff` → pass (mypy pre-existing errors unrelated to these files)

**Manual:**
- [x] `uv run agentic-mbse extract https://arxiv.org/html/1706.03762v1 -o /tmp/aiayn`
      → `output.md` frontmatter `source: "https://arxiv.org/html/1706.03762v7"`;
      11 v7 images pulled locally; backend `pandoc-arxiv`, 68,379 chars.
- [x] Non-arXiv URL with a `1234.56789v2`-shaped path fetched verbatim
      (`test_non_arxiv_url_untouched`).

**What We Know Works After This Phase:**
Both entry points fetch the latest version and record it; bare and non-arXiv
inputs are unaffected — all spec success criteria met.

---

## Environment Setup

**See CLAUDE.md** — `uv run` for everything; `extract --check` output must be
redirected to a temp file when run from the Bash tool.

---

## Risk Management

**See `design.md#potential-risks`.**

**Phase-Specific Mitigations:**
- **Phase 1:** B2 (version recovery) is proven against a real saved page before
  any wiring — if it fails, stop and revisit provenance mechanism.
- **Phase 2:** D5 fallback keeps extraction working if bare is unavailable; the
  updated existing test guards against silent behavior drift.
- **Phase 3:** regression tests on bare + non-arXiv URLs guard the fetch-ordering
  change; the retry keeps a bare-fetch failure from breaking extraction.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-07-05
**Actual Changes:**
- Added `strip_arxiv_version()` and `resolve_fetched_version()` to
  `src/agentic_mbse/extraction/pandoc_convert.py` (new "arXiv version
  normalization" section, both pure/no-I/O). One shared regex
  `_ARXIV_VERSION_RE = r"(\d{4}\.\d{4,5})v(\d+)"` handles id and URL forms
  uniformly — no input-type branching (single job).
- Added `tests/fixtures/arxiv_1706.03762_latest.html` — trimmed real page
  excerpt retaining `1706.03762v7/…` asset paths (body elided, ~1 KB).
- Extended `tests/test_pandoc_convert.py`: `TestStripArxivVersion` (6 cases inc.
  multi-digit version, 4-digit id) and `TestResolveFetchedVersion` (4 cases inc.
  dot-escaping regression and the real-fixture load).

**Validation:** `test_pandoc_convert.py` 30 passed; full suite 1200 passed / 1
skipped / 33 deselected; ruff clean. B2 (version recovery from real markup)
confirmed via `test_recovers_from_real_fixture`.

**Issues:** None. (mypy reports pre-existing errors in `validation/runner.py`,
unrelated to this change; `pandoc_convert.py` is clean.)

**Deviations:** Fixture is a hand-trimmed excerpt rather than the full 186 KB
page — matches the plan's "a few `<img src>` lines are enough."

### Phase 2 Completion
**Completed:** 2026-07-05
**Actual Changes:**
- `pandoc_convert.py`: rewrote `check_arxiv_html()` to prefer the bare (latest)
  URL and fall back to the requested version if bare is unavailable (D5). Split
  the HEAD reachability probe into `_arxiv_html_head_ok()` (mechanism); the
  prefer-latest/fallback policy lives in `check_arxiv_html()`.
- `pipeline.py` `_try_arxiv_shortcut()`: after conversion, recover the served
  version from `raw_bytes` via `resolve_fetched_version()` and set `source_url`
  to the versioned URL; falls back to the fetched URL when no version is found.
- `check.py` `probe_pandoc()`: unchanged (consumes the returned URL as before).
- `tests/test_pandoc_convert.py`: replaced the old `test_returns_url_on_200`
  (asserted versioned URL) with `test_strips_to_bare_and_returns_bare`; added
  `test_falls_back_to_versioned_when_bare_unavailable` and a `_mock_head()`
  helper. The 404/timeout/connection-error tests still pass (now two HEADs).

**Validation:** targeted 186 passed; full suite 1201 passed / 1 skipped; ruff
clean.

**Issues:** None.

**Deviations:** Renamed the updated test rather than editing in place (clearer
intent). Behavior change to `check_arxiv_html`'s return value is intended, as
flagged in the plan.

### Phase 3 Completion
**Completed:** 2026-07-05
**Actual Changes:**
- `web_backend.py`: import `strip_arxiv_version`/`resolve_fetched_version`; added
  `_ARXIV_ID_IN_URL_RE` (captures the bare id from an arXiv HTML URL).
- `extract_web_content()` Step 1: normalize a versioned arXiv URL to bare before
  fetching; fetch a `[bare, original]` candidate list so a bare failure retries
  the original (D5). Replaced the single-try fetch with a flat loop (no added
  nesting).
- `extract_web_content()` Step 4: for `pandoc-arxiv`, recover the served version
  from `html` and set `source` to the versioned URL; log the upgrade when the
  requested and served versions differ. Frontmatter `source` now uses this
  `source_url` instead of `final_url`.
- `tests/test_web_backend.py`: added 4 tests — bare-URL normalization, non-arXiv
  verbatim (regression), D5 bare-failure fallback, and versioned-`source` (loads
  the Phase 1 fixture, patches the Pandoc extractor).

**Validation:** web tests 33 passed; full suite 1205 passed / 1 skipped; ruff
clean. **Live end-to-end:** `extract https://arxiv.org/html/1706.03762v1`
recorded `source: ".../1706.03762v7"`, pulled 11 v7 images, no stale v1 refs.

**Issues:** None. No circular import (pandoc_convert does not import web_backend).

**Deviations:** Used a candidate-list loop rather than nested try/except for the
D5 fallback (flatter, per abstraction-quality "depth is a smell"). Added a
dedicated D5 fallback test beyond the plan's three.

---

**Status**: Draft → In Progress → **Complete**
