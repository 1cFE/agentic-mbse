# Spec: Fetch Latest arXiv Version

**Status:** Implementation Complete
**Owner:** Reid W
**Created:** 2026-07-05 10:11
**Complexity:** LOW
**Branch:** webfetch-tools

---

## Problem

Both arXiv extraction paths build version-pinned HTML URLs and fetch exactly
that version, even when a newer one exists on arXiv.

- **Web path** (`web_backend.py:386`): a user passes an arXiv HTML URL with an
  explicit version (`https://arxiv.org/html/2401.12345v1`); we fetch it as-is.
- **PDF path** (`pandoc_convert.py:71,113`): `detect_arxiv_id` pulls the version
  out of the PDF's page-1 text (`arXiv:2401.12345v1`), and `check_arxiv_html`
  builds a v1 HTML URL from it. A PDF downloaded months ago is the most common
  source of a stale version.

The result: we extract superseded content (v1) when the authors have since
published corrections (v2, v3, …). For a knowledge base meant to capture the
current state of a paper, that's the wrong artifact.

arXiv makes the fix cheap: the **bare** `/html/{id}` URL (no version suffix)
serves the latest version directly — confirmed, 200 with no redirect, served v7
for a known multi-version paper. A too-high version 404s. So resolving to latest
is just dropping the version suffix; no API call or version-probing is required.
(The `export.arxiv.org` API was unreachable from the test environment — avoid
depending on it.)

## Success Criteria

- [x] When either path has a version-pinned arXiv id/URL and a newer version
      exists, extraction fetches the newest version instead of the pinned one.
- [x] The extracted output records the version actually fetched, so a reader can
      tell which version the content came from (not just the requested one).
- [x] A bare (already-latest) arXiv id/URL still works and is not broken by the
      version-stripping logic.
- [x] If latest-version resolution fails (network error, unexpected arXiv
      response), extraction still succeeds by falling back to the
      requested/pinned version rather than erroring out.

## Known Requirements

- **[HARD]** arXiv serves the latest version from the bare `/html/{id}` URL
  (no version suffix). This is the resolution mechanism the feature relies on.
- **[HARD]** Both entry points must be covered: the web URL path in
  `web_backend.py` and the PDF-derived path via `detect_arxiv_id` /
  `check_arxiv_html` in `pandoc_convert.py`.
- **[NEED]** Provenance is preserved: the reader of an extracted artifact can
  see which arXiv version the content actually came from.
- **[NEED]** Resolution is resilient — a failure to determine/fetch the latest
  version degrades to the requested version, never to a failed extraction.
- **[INFERRED]** Default behavior is to fetch the latest version. This is the
  stated goal of the feature; whether users can opt out is deferred (below).

## Non-Goals

- Changing extraction quality, layout, or the Pandoc pipeline itself.
- Version handling for non-arXiv sources.
- Diffing or reconciling content across versions — we fetch one version (latest),
  not a comparison.

## Open Questions / Deferred to design

- **Silent upgrade vs. pinning.** Default is to fetch latest. Should there be a
  way to pin the exact requested version (a flag, or honoring an explicit
  version in a user-supplied URL)? Someone citing v1 deliberately may want v1.
  Deferred — decide in design whether an opt-out is worth the surface.
- **How to read back the fetched version.** The served HTML embeds the version
  (e.g. `1706.03762v7` appears in the page); design picks the exact mechanism
  (parse served HTML, canonical link, or a lightweight check) and where it lands
  in frontmatter.
- **Whether to surface the upgrade to the user** (log line / warning that
  "requested v1, fetched v7") vs. handling it silently.

---

## Related Artifacts

- **Prior work:** `.project/active/web-extraction-quality/` (arXiv → Pandoc
  routing this builds on)
- **Design:** `.project/active/arxiv-latest-version/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
