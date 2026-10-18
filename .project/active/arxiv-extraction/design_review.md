# Design Review: Reliable arXiv extraction (ARXIV-EXTRACTION)

**Design:** `.project/active/arxiv-extraction/design.md` (at `1c5df2e3`)
**Spec:** `.project/active/arxiv-extraction/spec.md`, with `spec_review.md` Resolutions
**Review File:** `.project/active/arxiv-extraction/design_review.md`
**Product lens:** `.project/active/arxiv-extraction/product-lens.md` (reviewer derivation; the lens script was unreadable this session)
**Date:** 2026-10-18

Severity key: **must-fix** = fix in the design before `/_my_plan`. **suggestion** = improves the design, does not block.

---

## The Point

**[NEED]** Downstream consumers can keep Pandoc on PATH safely: no citation substitution, no missing figures, no arXiv chrome. Their workarounds (hiding Pandoc from PATH for PDFs, stripping data-image references) then become unnecessary.

Today a PDF that merely cites an arXiv paper can be replaced by that paper. A correct substitution saves no figures. The direct HTML route converts the whole arXiv page, so dialogs, navigation, footers and UI icons land in the output. When the shortcut gives up, the consumer can't see why. The test every stage answers to: run `extract` with Pandoc on PATH, no workarounds, and get the right paper, its figures on disk, and nothing but the paper.

**[OWNER]** reserved gates: the shortcut default is open (the design must keep it a one-line flip), and no public `PipelineConfig` field or CLI flag is removed or renamed.

## Fundamental Assessment

**Sound.** This is the right piece of work, and the approach fits the problem.

- **Right work.** The design's point matches the owner's goal word for word. Each of its three decisions maps onto one of the owner's three outcomes, and the fallback warnings cover "can see why". The product-lens derivation found no owner or `[HARD]` contradiction and no fired structural smell. Both reserved gates are respected (D10, Invariant 9).
- **Right approach.** The core idea is plain and correct: decide identity from trusted evidence only, convert only the `<article class="ltx_document">` element, and save images through one function both routes call. I checked the load-bearing claims against the code and the saved pages:
  - The three Pandoc call sites are real duplicates (`pandoc_convert.py:235-251`, `web_backend.py:274-288`, `web_backend.py:312-326`).
  - Each saved page has exactly one `<article` tag, and its class includes `ltx_document` (`ref/*.html`).
  - On `ref/2610.14224.html`, every `<button>`, `<dialog>` and header `<nav>` sits before the article (lines 71–184; the article spans lines 242–4484). The footers and funder logos sit after it. Inside the article, `aria-hidden` appears only on two icon-font spans in a link (lines 306, 308).
  - Paper figures are relative refs like `2610.14224v1/intro_teaser.png`. No page has a `<base href>`.
- **Complexity matches.** One new module, a handful of pure functions, one exception type. Nothing is built for a hypothetical future. The tri-state control (D10) is the only piece that looks heavier than needed, and it earns its place (see Dimension 3).

The issues below are about module wiring, one unpinned data-flow detail, and stale grades. None of them touches the foundation.

---

## Dimensional Review

### 1. Spec Compliance

**Assessment:** Concerns

Every requirement has a design element. The Validation table maps each acceptance row to a test. The gaps:

- **R1 image base for the PDF route is not pinned down (must-fix, M2).** D7 says the base is "the page URL for fetched HTML". In the PDF route, which URL is that? D3 says `convert_arxiv_html` keeps its signature `(markdown, raw_bytes)` and does its own fetch (today with bare `urllib`, `pandoc_convert.py:213-218`). That signature cannot return the post-redirect URL. The Architecture diagram instead shows the PDF route doing "check_arxiv_html ─► fetch bytes ─► convert_article" itself. These two readings give different code. Real refs are relative (`2610.14224v1/x.png`), so `urljoin` is only right when the base is exactly the URL that served the page, without a trailing slash. If the base is the pre-redirect URL and arXiv ever redirects to `/html/<id>v1/`, every figure resolves to a wrong path, every download fails, and the PDF route warns once per figure.
- **R4 "no chrome" has a double-failure leak (suggestion, m5).** On the web route, if article conversion fails and trafilatura returns under 100 characters, `_fallback_pandoc` converts the whole page (`web_backend.py:423-432`). Chrome and UI data URIs then reach the output under backend `pandoc-fallback`. The spec only forbids *claiming* a paper-only conversion, so this is compliant. But it is the one path where the owner's "no arXiv chrome" outcome can still fail. The design should say whether that is accepted, or skip `_fallback_pandoc` for arXiv URLs.
- **R5 warnings on the PDF error path (suggestion, m3).** D12 attaches shortcut warnings to the base-extraction error result. But the CLI hits `if result.error: ... continue` (`extract_cli.py:501-504`) before it writes `metrics.json`. The design should say the stderr helper runs before that branch. It should also say whether an error result writes `metrics.json` at all; today it doesn't.
- **Capture fidelity.** The design carries spec grades faithfully in most places. Two slips:
  - The "Web stdout to stderr" risk says the move is "required by the spec". The spec (an `[INFERRED]` item) requires printing to stderr. Removing the stdout print is the design's own choice. That's a fine choice; it should be stated as a decision, not attributed to the spec.
  - B1 is still marked `[AGENT, unverified in this session]`. The spike addendum verified it on three pages (see M3).

### 2. Pattern Consistency

**Assessment:** Pass

- It reuses the existing `images/<name>` layout, the `metrics.json["warnings"]` convention, `fetch_url` and `USER_AGENT`, `_preprocess_html` and `_postprocess_markdown`, and the function-local import style the extraction modules already use.
- `ArxivConversionError` replacing `None` returns is a better pattern than what it replaces, and it is confined to the new module's API.
- D9 (inject `fetch_image` instead of patching `urlopen`) moves away from the current test pattern (`test_web_images.py`). The design states this and the reason. It's the right call.

### 3. Abstraction Quality

**Assessment:** Concerns

- **`arxiv_html.py` is the right seam (D3).** It holds one job: turn arXiv HTML into local markdown (select, convert, resolve, persist). It is importable on a core install (stdlib only), so the PDF route can use it without the `[web]` extra. Putting it in `web_backend.py` would make the PDF route import the web backend. That rejection is correct.
- **The dependency direction between `arxiv_html` and `pandoc_convert` is circular (must-fix, M1).** `arxiv_html.convert_article` needs `_preprocess_html`, `_postprocess_markdown` and `_run_pandoc`, which D6 and the Component Overview leave in `pandoc_convert.py`. And `pandoc_convert.convert_arxiv_html` calls `arxiv_html.convert_article` (D3). That is a module import cycle. A function-local import would paper over it, but the real problem is that `pandoc_convert.py` ends up with five unrelated jobs: PDF identity, the shortcut default, the HTTP HEAD probe, version helpers, and the HTML-to-markdown runner. The fix is to give each module one direction:
  - `arxiv_html.py` owns the whole HTML → markdown path: `_preprocess_html`, `_postprocess_markdown` (both are LaTeXML-specific), `_run_pandoc`, selection, conversion and images. It imports nothing from `pandoc_convert`.
  - `pandoc_convert.py` keeps PDF identity, `ARXIV_SHORTCUT_DEFAULT`, `check_arxiv_html`, the version helpers, and the thin `convert_arxiv_html` wrapper. It imports from `arxiv_html`.
  - `web_backend._fallback_pandoc` calls `arxiv_html._run_pandoc`. A general fallback importing from a module named for arXiv is a small naming wart. It is better than a cycle. If that bothers the implementer, `_run_pandoc` can take its own tiny home, but don't add a module just for this.
- **D10's tri-state earns its place.** A plain `bool` default would make `--html-path` users hit the contradiction error the day the default flips to off. `None` plus one resolver is the smallest thing that keeps the flip to one line. The cost is that `config.arxiv_shortcut` can't be read directly; callers must go through `resolve_arxiv_shortcut`. That function is named but never defined (see m1).
- **`image_base` and `read_base_href` exist only for spec R1's local-file case.** No real arXiv page has a `<base href>`. They're cheap and spec-driven, so keep them, but keep them small.

### 4. Duplication Avoidance

**Assessment:** Concerns

- The design removes the real duplication: three Pandoc invocations become one (D6), and the two arXiv conversions become one `convert_article` (D3).
- **Two ways to load arXiv HTML bytes remain (part of M2).** `convert_arxiv_html` fetches with bare `urllib` and keeps the old URL-or-path dispatch. The PDF route, per the Architecture diagram, fetches on its own. The web route uses `fetch_url`. Once M2 is resolved, there should be one loader that returns bytes plus the URL that served them, and `convert_arxiv_html` should use it (or the PDF route should stop calling `convert_arxiv_html`, leaving it as the `--check` and compatibility entry point).
- **Two minimum-content constants.** The Component Overview says `arxiv_html` "holds the shared minimum-content constant", but `web_backend._MIN_CONTENT_LENGTH` (`web_backend.py:36`) also gates trafilatura and the Pandoc fallback. Say whether web imports it from `arxiv_html` or keeps its own (suggestion, m4).
- **The routes' inputs still differ.** The web route selects the article from sanitized HTML (`strip_hidden_content` re-serializes through bs4/lxml, `html_sanitize.py:61-90`). The PDF route selects from raw bytes. So the same page can convert slightly differently by route. This is inherited, and the PDF route can't sanitize without bs4. It does undercut D4's reason for rejecting bs4 ("re-serializing could change MathML"): the web route has always re-serialized. The real reason for `html.parser` is the core-install constraint, which D4 also gives. Suggest the design lead with that reason (m6).

### 5. Data Structure Clarity

**Assessment:** Concerns

The main types are explicit: `ArxivIdentity` is a frozen dataclass with clear fields, `PipelineResult.warnings` is a typed list, and the `persist_images` signature is given. Gaps a plan would have to invent (m1):

- `ImagePersistResult` has no field list. Presumably `markdown`, `saved_count` and `warnings`.
- `resolve_arxiv_shortcut` appears in D14 and the Component Overview with no signature or semantics. Presumably `(config_value: bool | None) -> bool`.
- `ArxivConversionError` has no stated home module.
- D14's "explicit 'paper identified' outcome on the probe" implies a new field on `ProbeResult` (`check.py`), but the design doesn't name it.
- `ArxivIdentity.conflict` and `arxiv_id` overlap: a conflict always means `arxiv_id is None`. Fine, but say it in the type comment so nobody constructs both.

### 6. Route Safety

**Assessment:** Pass

Every fallback is explicit and fails closed:

- No evidence, conflict, or ambiguous container → normal extraction (Core Concept items 1–2, D4).
- D13 lists exactly which outcomes warn and which stay silent, and gives the reason. Warning only on outcomes that are not the ordinary "shortcut doesn't apply" case is the right line. Every non-arXiv PDF would otherwise warn.
- Invariant 4 forbids any network or Pandoc work without evidence, and the Validation table asserts it with call checks.
- The contradiction case (`--no-arxiv-shortcut` with `--html-path`) is an argparse error at the CLI and a `ValueError` in Python.

One asymmetry worth a sentence (m7): "Pandoc missing" is silent on the PDF route without `--html-path` (D13), but on the web route an arXiv URL with no Pandoc raises `ArxivConversionError` and warns (D5). That's defensible, since the user asked for an arXiv page, but say so. It means every arXiv web extraction on a machine without Pandoc gains a new warning.

### 7. Bets & Decisions Integrity

**Assessment:** Concerns

- **The stated bets are honest claims about reality,** each with an "if false" consequence. B2 rests on the spike's three PDFs and a stamp shape that body text won't produce. That's strong enough given that a miss only drops the shortcut.
- **B1 and B3 are stale (must-fix, M3).** B1 says the real page "was not readable here" and is unverified. The spike addendum (committed before the design) verified it on three pages, and I confirmed it above. B3 (no arXiv UI inside the article) also holds on `ref/2610.14224.html`: every button and dialog sits before the article. The design should re-grade both as spike-verified, cite the addendum and `ref/`, and shrink the Next-Stage Handoff's "De-risk first" item to "build the fixture from `ref/2610.14224.html` and keep a selection test on it". The fixture source in Implementation Notes points at `/tmp/arxiv-investigation-1topu2hb/raw.html`, which may be gone. `ref/2610.14224.html` is the pinned copy.
- **Hidden bet: the URL that served the page is the right base for relative refs.** Real refs are `<id>vN/<file>`, relative to `/html/`. `urljoin` gets that right only if the base has no trailing slash. Today's web route already depends on this (`web_backend.py:101`). The PDF route would newly depend on it, through whichever URL M2 settles on. State it as a bet, with "if false → every figure fails to download and warns", and have the fixture test use the real URL shape.
- **Hidden bet: Pandoc emits every figure as `![alt](src){attrs}` that `_MD_IMAGE_RE` can match.** B4 covers raw-HTML `<img>`. It doesn't cover alt text containing `]` (a caption with brackets), which the regex `!\[([^\]]*)\]` (`web_backend.py:53`) won't match. Pandoc writes LaTeXML figures with `alt="Refer to caption"`, so this is unlikely for arXiv. Noting it as part of B4 is enough.
- **Decisions name their rejected alternatives.** Every D has a "Rejected:" clause with a reason. D4's reason should lead with the dependency constraint (m6).

### 8. Reader Comprehension

**Assessment:** Pass

A reader skims the Overview and Core Concept and knows what the system does: three decisions, each owned by one function, each fallback warning. The Architecture diagram is dense but readable. Terms are introduced before use. The only comprehension gaps are the undefined names in m1, and a reader who hits `resolve_arxiv_shortcut` in D14 has nowhere to look.

---

## Issues by Severity

### Critical

None.

### Major (must-fix before `/_my_plan`)

- **M1. Import cycle between `arxiv_html` and `pandoc_convert`.** `convert_article` needs the pre/post-processors and `_run_pandoc` from `pandoc_convert`, and `convert_arxiv_html` needs `convert_article`. Move the HTML → markdown helpers into `arxiv_html.py` so the dependency runs one way. `pandoc_convert.py` keeps identity, the default, the HEAD probe, version helpers and the thin wrapper. (Dimension 3)
- **M2. The PDF route's load path and image base URL are unspecified.** D3 (keep `convert_arxiv_html`, which can't return a final URL) and the Architecture diagram (the PDF route fetches itself) disagree. Pick one: the PDF route loads bytes through one loader that returns the serving URL (`fetch_url`'s `final_url`), passes that URL to `image_base`, and calls `convert_article` and `persist_images`. `convert_arxiv_html` becomes a wrapper over the same loader, used by `--check` and external callers. State the "base = the serving URL, no trailing slash" bet. (Dimensions 1, 4, 7)
- **M3. B1 and B3 are graded unverified, but the spike addendum verified them.** Re-grade both, cite the addendum and `ref/`, point the fixture build at `ref/2610.14224.html`, and shrink "De-risk first" to a permanent selection test. Also fix the "required by the spec" attribution on removing stdout warnings. (Dimensions 1, 7)

### Minor (suggestions)

- **m1.** Define `ImagePersistResult`'s fields, `resolve_arxiv_shortcut`'s signature, `ArxivConversionError`'s module, and the new `ProbeResult` outcome field. (Dimension 5)
- **m2.** Add a Pandoc-free test that runs `select_article` on the real fixture and asserts chrome strings are outside the slice and paper strings inside. The Validation table's "Paper alone" row skips when Pandoc is absent, so without this the core of R4 can go untested in CI. (Dimension 1)
- **m3.** Say that the CLI prints and persists shortcut warnings before the `if result.error` branch (`extract_cli.py:501`), or accept that they are dropped on base-extraction failure. (Dimension 1)
- **m4.** Say whether `web_backend._MIN_CONTENT_LENGTH` is replaced by the shared constant. (Dimension 4)
- **m5.** Decide whether the whole-page `_fallback_pandoc` runs for arXiv URLs after the article route fails. If it does, chrome can reach output on a double failure. Skipping it for arXiv URLs is one condition. (Dimension 1)
- **m6.** Lead D4's rejection of bs4 with the core-install constraint. The MathML reason is weak, since the web route already re-serializes through bs4. (Dimension 4)
- **m7.** State the web-route Pandoc-missing warning as deliberate, since it is new user-visible output. (Dimension 6)
- **m8. Simpler selection is available.** Each real page has exactly one `<article` tag (`ref/*.html`). A string scan works and fails closed: require exactly one `<article` opening and one `</article>`, check the opening tag's class for `ltx_document`, and slice. That skips the `getpos()` line/column arithmetic and depth tracking in Implementation Notes. If the HTML has anything unusual (nested articles, `<article` in a script or comment), the counts won't match and the route falls back with a warning, which is the same outcome D4 gives malformed input. Keep `html.parser` if the implementer prefers it. Either way, the fail-closed rule is what matters. (Dimension 3)

---

## Recommendations

1. Fix the module direction (M1). It is the one structural change, and it makes `pandoc_convert.py` coherent again.
2. Pin the PDF route's loader and image base (M2). Without it, two implementers write different code, and one of them ships figures that never download.
3. Refresh B1/B3 and the fixture source (M3). It changes the plan's first phase from "verify" to "build the fixture and lock in a test".
4. Fill the small interface gaps (m1) and add the Pandoc-free selection test (m2) so R4's core is always exercised.
5. Take or reject m3–m8 as one-line edits.

---

## Resolutions

Recorded by the orchestrator, 2026-10-18. All `[AGENT]`; neither reserved gate is touched.

- **M1** — Accept. Imports go one way: `pandoc_convert` → `arxiv_html` is not allowed; `arxiv_html` owns HTML-to-markdown helpers and the single Pandoc runner, `pandoc_convert` keeps PDF identity, the default constant, the availability check and version helpers.
- **M2** — Accept. One loader returns the fetched bytes plus the serving URL; both routes use that URL as the image base. State the no-trailing-slash assumption and normalize it in the loader rather than trusting it.
- **M3** — Accept. Re-grade B1/B3 as verified (spike addendum + `ref/`), point the fixture source at `ref/2610.14224.html`, and record dropping the stdout copy of web warnings as a design choice.
- **m1** — Accept. Define every named type and function.
- **m2** — Accept. Pandoc-free selection test on the real fixture.
- **m3** — Accept. The CLI prints and persists warnings before the error branch; an error result also writes its warnings to `metrics.json`.
- **m4** — Accept. One shared minimum-content constant; `web_backend` imports it.
- **m5** — Accept the skip: for arXiv URLs, the whole-page Pandoc fallback does not run; the trafilatura result is returned with a warning. Removes the only path that can leak chrome.
- **m6, m7** — Accept as wording.
- **m8** — Accept the fail-closed string scan for article selection. It is simpler and fails the same way on anything unusual.

---

**Overall:** Revise. The foundation is sound. The three must-fix items are targeted edits to the design, not rework.
**Next Steps:** Once resolutions are recorded, re-run `/_my_design` (or return to the design-agent session) and point it at this review to incorporate. The reviewer does not edit the design.
