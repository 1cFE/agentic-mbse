Good work on Phases 0–2; the shared module reads cleanly. Continue with Phases 3 and 4 of plan.md, then stop.

Orchestrator decision on your SVG finding [AGENT]: design amendment D17 (end of design.md) rewrites LaTeXML `<object type="image/svg+xml" class="ltx_graphics …">` to `<img>` in arxiv_html pre-processing; a Phase 6 task was added for it. Not in scope for this session; leave it for Phase 6. Also noted your Phase 8 correction (paper SVG data URIs are legitimate); fold it into plan Phase 8 text now.

Same rules as before: test-first, per-phase commits with decision-led subjects and the Co-Authored-By line, plan boxes and Implementation Notes filled before each commit, real PDF bytes via the generated stamp fixtures (spike-margin-stamp.md), no new lint/type findings in touched code. Reserved: the default stays one constant; no removals/renames of public config fields or flags. End with ARTIFACT: <plan path>.
