.project/active/native-skill-distribution/plan.md

## Brief from the orchestrator

The Phase 9 re-check certified the `--dev` folder-link fix (`audit.md` § "Re-check: Phase 9", committed `b93b886`). Fix three of its advisories on `nsd-integration` (worktree `/home/reid/1cfe/agentic-mbse-nsd`, HEAD `b1d5d23`). Read the advisories in `audit.md` (§ "Advisories (Phase 9)") and the auditor's scratch cases in `.orchestrate-logs/audit-scratch/p9/` (`transitions.py` reproduces advisory 1). Advisory 3 is already done by the orchestrator (`b1d5d23`).

### What to fix [AGENT, orchestrator]

1. **The fallback line says what happened** (advisory 1, `installation.py:365-383`). Today `install_dev_bundle` prints "Copied … instead of linking it" whenever `copy_tree` returns, even when nothing was written. Make the printed line true in each case the auditor found:
   - files were copied → say copied, and why it was not linked;
   - nothing was written (every file owner-edited and preserved) → say the folder was kept as it is;
   - the folder still holds a `SKILL.md` that is a file link (an old per-file `--dev` folder with a lost manifest) → say Codex will not list that skill, and how to fix it (plain `init`, or remove the folder and re-run). This is the case closest to B1, a silent Codex gap, so it must not read as success.
   Keep it small: one honest line per bundle, decided from the outcome, not a new reporting subsystem. Leave `link_directory`'s empty-folder rule alone (the Claude alias relies on it); the empty-folder case just needs a true line.
2. **Pin the two unpinned behaviours** (advisory 2, mutants P12, P14): a test whose `decide` counts its calls, showing an owner is asked once, not twice, about an entry `permit` refused under `--dev` (the guard at `installation.py:375-376`); and widen `test_next_steps_are_the_same_with_and_without_dev` (`tests/test_cli.py:467`) to compare the whole closing output, so a returned warning above "Next steps:" fails it. Show each new test kills its mutant.
3. **Report a redirected `.agents/skills` once** (advisory 5): the fallback calls `parents()` a second time through `copy_tree`, so the "Skipped … parent … is not a real directory" line and the Skipped entry appear twice. Fix it without weakening the redirect check.
4. **Advisory 4, record only:** add to `evidence/audit-scope.md`'s follow-up list: "Codex discovery under `--dev` rests on observed Codex behaviour (folder links listed, `SKILL.md` file links skipped; `evidence/spike-dev-codex-links.md`, codex-cli 0.160.0). Re-run `discovery_probe.py` on a `--dev` target when the Codex version in use changes."

Tests for item 1 cover each case, derived from the tree where a sample is needed (SC5, I4).

### Rules

- Add the work as Phase 9 notes in `plan.md` (a short "Re-check advisories" subsection), not a new phase.
- Worktree and scratch only. No writes to `/home/reid/1cfe/agentic-mbse`, the native worktree or `/home/reid/1cfe/fusion-tea`. Do not switch branches. Do not edit `audit.md` or `product-lens.md`.
- Gate (SC12 parity rule, `evidence/lint-parity.md`): full `uv run pytest tests/` green; `ruff check` and `ruff format --check` clean on every file you change, with no repo-wide count above the record; `mypy` no worse on changed files.
- No rehearsal re-run is needed unless you change behaviour on a path the rehearsal exercises (it never reaches the fallback); say which.
- Commit as you go (code + tests; notes), subject leading with the decision. No background tasks. Finish in this session.
- End with a summary: what changed (file:line), the printed line in each case (paste them), the mutant results for P12 and P14, the gate numbers, and the commits. Then `ARTIFACT: .project/active/native-skill-distribution/plan.md`.
