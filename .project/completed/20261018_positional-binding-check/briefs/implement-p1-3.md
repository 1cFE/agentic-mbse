Implement **Phases 1, 2 and 3** of `.project/active/positional-binding-check/plan.md` (EXEC-SUBSET-CONTRACT Item 4), in order, then stop and report.

Read the plan's standing rules and Phases 1–3 in full, plus the design sections, `learning-findings.md` and `briefs/align.md` they cite.

Rules:
- Owner boundary: do not touch Item 2 or sysml-codegen; sibling repos (~/src/sysml-codegen, ~/src/dc3, ~/src/fusion-tea) are read-only — use `git archive` into a scratch dir. Verify their `git status` unchanged at the end.
- Never stage or commit the unrelated working-tree edits (`.gitignore`, `.project/EPIC_GUIDE.md`, `.project/README.md`, `.project/active/README.md`, `.project/backlog/README.md`, `.project/epic_template.md`). Never run repo-wide `ruff format`.
- Do not edit Item 1's modules (`subset_*`, `occurrence_*`, `fact_refs.py`) beyond what the design explicitly allows; read-only consistency checks only.
- Engineering bar: fact extracted once in the shared layer; pure check; closed reason vocabulary; deterministic ordering; every inspection failure a named structured unverifiable result. Test-first per the plan's stencils.
- If Phase 1 shows L1 passes `out_before_in`, record it as an owner item in the plan and continue, as the plan says.
- Tick checkboxes with implementation notes; commit per phase or finer, outcome-led subjects, each ending `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Finish with per-phase outcome, baseline numbers, the 17-case identity results, any surprise, and the ARTIFACT line (plan.md).
