# Brief: /_my_audit — goal-layer-port (`WRAP-SPLIT` Item 2)

Audit the implementation of `.project/active/goal-layer-port/` against its spec as a fresh, independent auditor. You wrote none of it. Write the audit to `.project/active/goal-layer-port/audit.md`. Do not fix anything and do not commit. Start no background tasks. End with `ARTIFACT: <path>`.

## What to audit

- The contract is `spec.md` (SC1–SC12, as revised after review), read with `briefs/align.md`, the Resolutions in `spec-review.md` and `design-review.md`, and `design.md`. The plan's "Progress notes" and orchestrator notes record every deviation; judge each one.
- The code and text: `git diff origin/main...HEAD` in this worktree (branch `goal-layer-port`, base `33511c4`). Shipped surfaces: `docs/patterns/design-choices.md`, `docs/goal-layer-decisions.md`, `project_templates/` (process template, goal runbook and templates, narrative test), `skills/run-goal`, `skills/narrate-goal`, the one-line edits to other skills and `docs/patterns/constraints.md`, `src/agentic_mbse/cli/__init__.py`, tests, fixture.
- The evidence: `.project/active/goal-layer-port/evidence/` (its README maps each SC). The orchestrator ran O1–O3 itself, because they need fusion-tea, a scratch target outside the repo, or a live `claude -p`: the SC6 delta check, the fusion-tea F1 commit, the SC8 rehearsal and the SC4 dry run. You cannot read fusion-tea; its branch diff (`evidence/fusion-tea/branch-diff.txt`, branch `goal-layer-mr7`, base `b06585709`) and the snapshot at `.orchestrate-logs/fusion-tea-snapshot/` (`2b1e9f9d5`) are your view of it. Treat orchestrator-written evidence as claims to check against what you can see, not as given.
- The migration ledger's Item 2 section in `.project/active/wrap-split-migration-ledger.md`.

## Weigh hardest

1. **The owner's central direction** ([OWNER-VERBATIM] 2026-10-11): "it is important that you find the right level for this rule -- we have specific patterns which agentic-mbse is supposed to enforce, this should fit into that". Does the shipped rule read as one of agentic-mbse's own patterns, stated once and reached where modelers and reviewers act (SC5), with MR-7's force (SC6)?
2. **The port is a port** (SC12) and **nothing points at fusion-tea** (SC2, SC3), checked by running the commands, not by reading the evidence's claims.
3. **No loss for fusion-tea** (SC7–SC9): every removed line has a destination the branch diff shows or that existed at the base.
4. **Engineering quality**: tests that would catch the regressions they name; installer code in the style of its surroundings; no placeholder, TODO or dead text.
5. Run `uv run pytest tests/` yourself. Ruff and mypy are judged at `main`'s parity (118 and 88 findings on `main` with all extras; see the plan's orchestrator note): no new finding in a touched file.

Give a verdict (Certify, Certify with follow-ups, or Needs Work), each finding graded must-fix or advisory with a file:line basis, and one line per SC: met, not met, or not verifiable here (say why). Keep it plain and short.
