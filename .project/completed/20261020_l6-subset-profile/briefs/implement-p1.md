Implement **Phase 1 only** of `.project/active/l6-subset-profile/plan.md` (EXEC-SUBSET-CONTRACT Item 3): the baseline, then the shared extraction session alone. Then stop and report. (Orchestrator verified: `src/` and `tests/` are unchanged since `ebb3d467`.)

Read the plan's standing rules and Phase 1, plus the design sections it cites (D14, I10, B5, Appendix C).

Rules:
- Owner boundary: no Item 2 artifacts; no writes to ~/src/sysml-codegen; sibling repos read-only via `git archive` into scratch dirs.
- Never stage the six unrelated working-tree edits (`.gitignore`, `.project/EPIC_GUIDE.md`, `.project/README.md`, `.project/active/README.md`, `.project/backlog/README.md`, `.project/epic_template.md`). Stage explicit paths only. Never run repo-wide `ruff format`.
- The session must change no level's results: the with/without equality test covers L2–L6 on the repo fixtures and the three consumer trees. Results must be identical, not just counts.
- **Stop rule:** if any level's results differ with the session, or fusion-tea's `validate --complete` wall time is more than 10% slower than baseline, stop and report with the evidence; do not tune around it.
- Tick checkboxes with notes; commit with outcome-led subjects ending `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Finish with the baseline numbers (repo checks; per-tree `validate --complete` pass/fail and issue counts; fusion-tea wall time), the equality results, the session timing, and the ARTIFACT line (plan.md).
