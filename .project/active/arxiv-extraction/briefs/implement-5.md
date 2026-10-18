Two orchestrator calls [AGENT], then Phase 8:

1. Saved-image count: persist `image_count` in metrics.json for both routes and include it in the CLI's per-item summary line (e.g. "(N chars, M images, Xs)"). Tests for both.
2. `--check` capability: `arxiv_shortcut` capability must be true only when extract would actually take the shortcut, i.e. identified AND an HTML version is available (and the shortcut is enabled). `--check` exists to predict extract (spec_review L2-3 resolution). Amend design D14 with one line recording this and fix the code/tests.

Commit those as one small commit once green. Then run Phase 8, the live Harness² check: `extract https://arxiv.org/html/2610.14224` and the arXiv PDF of 2610.14224 with Pandoc on PATH, budget 0, output to a scratch directory outside the repo. Record in plan Phase 8: Pandoc version, fetched source and version, saved paper-image count vs. figure count (expect 9 figures), files present for every image ref, chrome absent (issue dialog, nav, footer, funder logos), any download failures. Network failure is non-blocking; record it if so. Commit the record. End with ARTIFACT: <plan path>.
