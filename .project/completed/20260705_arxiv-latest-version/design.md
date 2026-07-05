# Design: Fetch Latest arXiv Version

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-05 10:14
**Branch:** webfetch-tools
**Commit:** 90113c0

---

## Overview

Normalize version-pinned arXiv identifiers/URLs to the bare form before
fetching, so arXiv serves the latest version, and record the version we
actually got. Applies to both the web URL path and the PDF-derived path.

## Related Artifacts

- **Spec:** `.project/active/arxiv-latest-version/spec.md`
- **Prior work:** `.project/active/web-extraction-quality/` (arXiv → Pandoc routing this builds on)

## Research Findings

**arXiv version behavior (verified against `arxiv.org`):**
- Bare `/html/{id}` (no `vN` suffix) serves the **latest** version directly —
  200, no redirect. Confirmed: bare `1706.03762` served v7.
- An explicit `/html/{id}vN` serves exactly that version.
- A too-high version (`v99`) returns 404.
- `export.arxiv.org` API was unreachable from the test environment — not used.
- The served latest HTML has **no** canonical link / og:url / citation meta
  carrying the version. The only version marker is in LaTeXML **asset paths**:
  image `src` values are prefixed `{id}v{N}/…` (e.g. `1706.03762v7/x1.png`).

**Code touchpoints:**
- **Web path** — `web_backend.py`: `extract_web_content()` fetches `url` at
  step 1 (`:362`), then routes on `_is_arxiv_html_url(final_url)` at `:386`.
  arXiv HTML regex at `:232`. Image refs already parsed by
  `_download_arxiv_images()` (`:54`), which keys on the same `{id}vN/` paths.
- **PDF path** — `pandoc_convert.py`: `detect_arxiv_id()` (`:71`) returns an id
  that may include `vN` (`(?:v\d+)?`); `check_arxiv_html(arxiv_id)` (`:113`)
  HEAD-checks and returns the versioned URL. Callers: `pipeline.py:192`
  (`_try_arxiv_shortcut`, real extraction) and `check.py:335` (`probe_pandoc`,
  diagnostic only).
- **Provenance** — `frontmatter.build_frontmatter()` records `source` (the URL).
  No version field; the versioned URL in `source` is the natural home.

## Core Concept

The whole feature rests on one fact: **arXiv serves the latest version from the
bare `/html/{id}` URL.** So "fetch latest" is not a lookup — it is a string
normalization done *before* the fetch: strip the `vN` suffix from the arXiv
identifier (PDF path) or URL (web path), then let the existing fetch/route/
convert machinery run unchanged.

Two things differ only in *where the version-pinned identifier lives*:
- PDF path holds an **id** (`2401.12345v1`) → strip in `check_arxiv_html`.
- Web path holds a **URL** (`…/html/2401.12345v1`) → strip at the top of
  `extract_web_content`, before the step-1 fetch.

Provenance is recovered *after* the fetch: the served HTML's asset paths carry
`{id}v{N}/`, so we read the resolved version back out and write the versioned
URL into `source`. This reuses the exact `{id}vN/` pattern the image downloader
already depends on — no new source of truth.

This composes with existing pieces rather than adding parallel mechanisms:
`pandoc_convert` stays the arXiv-knowledge home (new helpers live there),
`_download_arxiv_images` already understands asset paths, `build_frontmatter`
already records the source URL.

## Key Bets

- **B1.** arXiv reliably serves the latest version from the bare `/html/{id}`
  URL. *If false → we fetch the wrong version, or a 404, and the whole approach
  collapses to a no-op.* (Verified for the current arXiv HTML service.)
- **B2.** The resolved version is recoverable from the served HTML's asset
  paths (`{id}vN/`). *If false → we still fetch latest content, but can't record
  which version — the provenance NEED degrades to "latest, version unknown."*

## Key Decisions

- **D1.** Resolve latest by **stripping the version suffix** and letting arXiv
  serve the bare URL. *Rejected: querying `export.arxiv.org` (unreachable in
  testing, adds a dependency) and HEAD-probing `v2,v3,…` upward (N requests,
  racy).*
- **D2.** Recover the fetched version by **parsing `{id}vN/` from the served
  HTML asset paths**. *Rejected: a second fetch of `/abs/{id}` just to read the
  version (extra request for secondary data); relying on the redirect chain
  (bare URL returns 200 with no redirect, so nothing to read).*
- **D3.** Record provenance by writing the **versioned URL into the existing
  `source` frontmatter field**. *Rejected: adding an `arxiv_version` field to
  `build_frontmatter` — more schema surface for one source type.*
- **D4.** **Silent upgrade by default**, with a log line noting `requested vN →
  fetched vM`. No pin/opt-out flag in this change. *Rejected: a `--pin-version`
  flag — contradicts the spec's stated goal ("fetch the most recent"), and the
  normalization already returns the requested version, so a flag is a trivial
  future add if wanted.* (Open question from spec — see Handoff.)
- **D5.** On fetch failure of the bare URL, **fall back to the original
  version-pinned URL/id**. *Rejected: failing outright — violates the spec's
  resilience criterion.*

## Architecture

Two shared helpers, placed in `pandoc_convert.py` (the arXiv home), consumed by
both paths:

```
strip_arxiv_version(id_or_url) -> (bare, requested_version | None)   # pure string op
resolve_fetched_version(html, bare_id) -> int | None                 # parse {id}vN/ from HTML
```

**Web path** (`extract_web_content`):
```
url → strip_arxiv_version → bare_url ──fetch──▶ (fail? retry original url)
    → existing sanitize / arXiv-route / Pandoc / image-download (unchanged)
    → resolve_fetched_version(html) → set source = ".../html/{id}vN"
```

**PDF path** (`check_arxiv_html` + `_try_arxiv_shortcut`):
```
arxiv_id → strip_arxiv_version → HEAD bare (200? use bare : HEAD original)
        → convert_arxiv_html(url) → resolve_fetched_version(raw_bytes)
        → source_url = ".../html/{id}vN"
```

`probe_pandoc` (`check.py`) only needs the strip so its diagnostic fetch hits
latest; it records no provenance.

## Required Invariants

- A bare (unversioned) arXiv id/URL is unchanged by `strip_arxiv_version`
  (no-op) — already-latest inputs keep working.
- `strip_arxiv_version` does no I/O; it cannot fail on the network.
- Extraction never fails *because of* version resolution: if the bare fetch
  fails, the original identifier is retried (D5); if the version can't be read
  back, `source` falls back to the bare URL and extraction still succeeds.
- The `content_hash` covers the bytes actually fetched (the latest version) —
  hash reflects real output, not the requested version.

## Component Overview

- **`strip_arxiv_version` / `resolve_fetched_version`** — new, in
  `pandoc_convert.py`. First is a regex strip of `vN`; second matches
  `{id}v(\d+)/` in served HTML. Both pure, no I/O.
- **`check_arxiv_html`** (`pandoc_convert.py:113`) — modified: strip to bare,
  HEAD bare, fall back to HEAD versioned (D5).
- **`extract_web_content`** (`web_backend.py:330`) — modified: normalize `url`
  before step-1 fetch; retry original on failure; set versioned `source`.
- **`_try_arxiv_shortcut`** (`pipeline.py:172`) — modified: recover version from
  `raw_bytes`, set versioned `source_url`.
- **`probe_pandoc`** (`check.py:328`) — modified: strip only.

## Non-Goals

- Version handling for `/abs/` or `/pdf/` arXiv URLs, or non-arXiv sources.
- A user-facing flag to pin a specific version (deferred — D4).
- Cross-version diffing or reconciliation — we fetch one version (latest).

## Implementation Notes

- **Web path ordering matters:** normalize `url` *before* the step-1 fetch
  (`web_backend.py:362`), not at the step-3 route check (`:386`). Routing keys on
  `final_url`, which will already be bare.
- **Reuse the image regex intent:** `resolve_fetched_version` should match the
  same `{id}vN/` shape `_download_arxiv_images` relies on (`web_backend.py:54`).
- **arXiv id regex** for the strip: `^(\d{4}\.\d{4,5})v(\d+)$` on the id;
  `(/html/\d{4}\.\d{4,5})v\d+` sub on the URL. Match the existing patterns at
  `pandoc_convert.py:89` and `web_backend.py:232`.
- **Figure-less papers** may have no `{id}vN/` asset path → version unknown →
  record bare `source`. Acceptable; log at debug.

## Potential Risks

- **arXiv changes latest-version serving (B1).** Mitigation: D5 fallback to the
  requested version keeps extraction working; only the "upgrade" is lost.
- **Asset-path version marker changes (B2).** Mitigation: provenance degrades to
  "version unknown," content is still correct; low blast radius.
- **Unexpected upgrade surprises a user who wanted v1.** Mitigation: log line
  makes the upgrade visible; pin flag is a documented future option (D4).

## Integration Strategy

Pure augmentation of the existing arXiv paths — no new files, no API changes to
`build_frontmatter`. The Pandoc routing, image download, and metrics flow are
untouched. Both entry points converge on the same two helpers.

## Validation Approach

- **Unit:** `strip_arxiv_version` (versioned → bare + N; bare → unchanged, None;
  URL and id forms). `resolve_fetched_version` (asset-path HTML → N; no-asset
  HTML → None).
- **Integration (network, mark slow):** bare-id extraction of a known
  multi-version paper (`1706.03762`) records `v7` in `source`; a `v1` URL
  upgrades to latest.
- **Regression:** a bare arXiv URL and a non-arXiv URL extract unchanged.
- **Manual:** `extract` a `…v1` arXiv URL; confirm log shows `requested v1 →
  fetched vN` and frontmatter `source` carries the resolved version.

## Next-Stage Handoff

- **Fixed:** strip-before-fetch mechanism (D1); provenance via versioned
  `source` (D3); both paths covered; resilience fallback (D5).
- **Open:** whether to add a pin/opt-out flag (D4) — recommend not now; revisit
  if users report unwanted upgrades. Whether to surface the upgrade as a
  user-visible message vs. debug log.
- **De-risk first:** confirm `resolve_fetched_version` finds the version on a
  real served page (B2) before wiring provenance — it's the shakiest link.

---

**Next Step:** After approval → `/_my_plan` or `/_my_implement`.
