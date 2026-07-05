# Audit: Fetch Latest arXiv Version

**Verdict:** Certify
**Audited:** 2026-07-05
**Branch:** webfetch-tools
**Commit:** 90113c0 (changes uncommitted in working tree)

---

## Summary

The feature does what the spec asked: both arXiv paths now strip the version
suffix, fetch arXiv's bare `/html/{id}` URL (which serves latest), and record
the served version in provenance. All four success criteria are met, the design
decisions (D1–D5) and invariants are followed, and the relevant test suites pass
(142 tests across pandoc_convert, web_backend, pipeline). One real but trivial
defect: the extracted `_arxiv_html_head_ok` helper introduces a new mypy
`no-any-return` error, and the plan's completion notes claim mypy is clean for
these files — it isn't. One-line fix, does not affect runtime behavior.

## Findings

### Plan completion

All three phases verified complete.

- **Phase 1 (pure helpers):** `strip_arxiv_version` and `resolve_fetched_version`
  exist and are pure (`pandoc_convert.py:118,134`). Fixture
  `tests/fixtures/arxiv_1706.03762_latest.html` carries real `1706.03762v7/`
  asset paths; `test_recovers_from_real_fixture` proves the B2 risk resolved.
- **Phase 2 (PDF path):** `check_arxiv_html` prefers bare, falls back to
  versioned (`pandoc_convert.py:166`); the HEAD probe is split into
  `_arxiv_html_head_ok` (`:151`). `_try_arxiv_shortcut` recovers the version and
  sets the versioned `source_url` (`pipeline.py:207-214`).
- **Phase 3 (web path):** `extract_web_content` normalizes before the step-1
  fetch with a `[bare, original]` candidate loop for the D5 fallback
  (`web_backend.py:366-391`), and sets versioned `source` in step 4
  (`:446-459`).

One plan item was deferred, not done: the Phase 2 manual `extract --check` run
(`plan.md:151-154`), left as "unit-covered." Acceptable — the Phase 3 live
end-to-end run (`extract …/1706.03762v1` → recorded v7, 11 images) exercises the
same conversion path. Not a gap.

### Spec conformance

- **SC1 — pinned id/URL fetches newest.** Met. Both paths strip to bare; arXiv
  serves latest. Web: `web_backend.py:371-372`. PDF: `check_arxiv_html`
  `pandoc_convert.py:173-176`.
- **SC2 — output records the version actually fetched.** Met, with one
  documented degradation. `source` carries `…/{id}v{N}` recovered from asset
  paths (`web_backend.py:453-455`, `pipeline.py:212-214`). A figure-less paper
  has no `{id}vN/` path, so version is unknown and `source` records the bare URL
  (no version). This is the accepted B2 degradation, not a defect.
- **SC3 — bare (already-latest) id/URL still works.** Met. `strip_arxiv_version`
  is a no-op on bare input; `candidates` collapses to a single fetch
  (`web_backend.py:374`). Covered by `test_bare_id_unchanged`,
  `test_bare_html_url_unchanged`.
- **SC4 — resolution failure degrades to requested version, never errors.** Met.
  Web: candidate loop retries the original URL when bare fetch throws
  (`web_backend.py:377-384`), verified by
  `test_bare_fetch_failure_falls_back_to_requested`. PDF: `check_arxiv_html`
  HEAD-falls-back to the versioned URL (`:177-178`), verified by
  `test_falls_back_to_versioned_when_bare_unavailable`. Only a genuine
  double-failure (both URLs unreachable) errors out — correct.

Non-goals respected: no `build_frontmatter` schema change (versioned URL rides
the existing `source` field), no pin/opt-out flag, no non-arXiv version handling,
no cross-version diffing.

### Design conformance

Implementation follows the design.

- **D1** (strip-before-fetch), **D2** (parse `{id}vN/` from served HTML), **D3**
  (versioned URL into existing `source`), **D4** (silent upgrade + log line at
  `web_backend.py:456-459`), **D5** (fallback to requested) — all present.
- Invariants hold: `strip_arxiv_version` does no I/O; extraction never fails
  *because of* version resolution; `content_hash` covers the bytes actually
  fetched (web hashes `fetched.content` `:444`; PDF hashes `raw_bytes` `:205`).
- Helpers live in `pandoc_convert.py` as designed; `probe_pandoc` (`check.py:338`)
  correctly needed no change — it consumes whatever URL `check_arxiv_html`
  returns, which is now bare/latest.

### Code integrity

- **New mypy error, `pandoc_convert.py:161`.** `_arxiv_html_head_ok` does
  `return resp.status == 200`; `resp.status` is `Any` from `urlopen`, so mypy
  reports `Returning Any from function declared to return "bool"`
  (`no-any-return`). The original code compared the same value inside an `if`
  (never returned it), so this error is **newly introduced** by the extraction,
  and the plan's Phase 1/2/3 notes ("mypy pre-existing errors unrelated to these
  files") are inaccurate for this file. Fix: `return bool(resp.status == 200)`.
- **Two mechanisms derive the bare id.** PDF path uses `strip_arxiv_version`
  (`pipeline.py:211`); web path uses a separate `_ARXIV_ID_IN_URL_RE`
  (`web_backend.py:238,450`). Minor duplication, but justified — the inputs
  differ (a bare id string vs. a `final_url` that may have redirected), and the
  URL regex must anchor on `/html/`. Not worth unifying.
- No god functions, no silent invariant-swallowing fallbacks, no dead
  compat shims. The web fetch fallback is a flat candidate loop (no nested
  try/except), matching the design's "depth is a smell" note. The broad
  `except Exception` in `_arxiv_html_head_ok` (`:162`) is correct — it is a
  reachability probe where any failure legitimately means "not available," and
  the docstring says so.

---

## Certification

Certifying the feature. Verified and marked:

- **Spec:** all four success criteria (SC1–SC4) marked met.
- **Plan:** all three phases were already checked off by the implementer; I
  re-verified each against the code and confirm they are genuinely complete.
- **Left open (non-blocking):** the mypy `no-any-return` at
  `pandoc_convert.py:161` — one-line fix, no runtime impact. Recommend fixing
  before commit so the "mypy clean" claim holds.

Behavior is correct and matches the design; the single finding is a
type-checking cleanliness regression, not a functional defect.
