Audit EXEC-SUBSET-CONTRACT **Item 3: L6 integration and execution-target settings** — `.project/active/l6-subset-profile`.

Output: `.project/active/l6-subset-profile/audit.md` with a `**Verdict:**` line (Certify or Needs Work).

## What to audit against

- `spec.md` (the contract), `design.md` rev 1, `plan.md` (all 11 phases ticked, with notes), `briefs/align.md` (owner decisions and gate outcomes, graded there). The implementing session's notes are claims to verify, not facts.
- Branch `l6-subset-profile`, base `ebb3d467` (`git diff ebb3d467..HEAD`).
- Evidence: `evidence/before-after.md`, `dc3-baseline-l6.md`, `dc3-repaired-l6.md`, `legacy-l6-audit.md`, `repository-checks.md`, `baseline.md`.

## The bar

Hold a high engineering bar, not "it runs". In particular look for:

- Placeholder code, TODOs, dead branches, swallowed exceptions, tests that assert nothing or test the mock.
- Any state that reads as "will generate" when it is not: `CLEAR`, `REFUSED_INCOMPLETE`, `unconfirmed`, `unverified` presentation under every target (Item 1 product-lens impl-F1/F2).
- Native summaries hiding check failures; a crash or failed inspection passing under any target.
- Severity: every cell of the table in `src/agentic_mbse/validation/execution_target.py` against the spec and the align decisions. Only the four codes the plan names may be lowered under native.
- Settings: `src/agentic_mbse/project_settings.py` closed key set, malformed TOML / unknown value / unknown key are errors; CLI override precedence; `init --execution-target` never changes another byte of `pyproject.toml`.
- One shared extraction session per run (`src/agentic_mbse/validation/session.py`): cache keys sound (path, size, `mtime_ns`), no stale-model risk across runs, no leak of the context variable.
- Whether the R3-1 gate outcome holds: no existing L6 error was net-relaxed for unset or `generated` except the String-value replacement recorded in `briefs/align.md`.

## Two items the implementer flagged for a decision — give a recommendation for each

1. **Phase 7 Surprise 1** (plan.md, Phase 7 notes): a design attribute calling any non-`sum` function (e.g. `abs(2.0)`) now fails L6 as `L6_CHECK_ERROR` under every target, where at `ebb3d467` it was only a `V4_STATIC_FUNCTION_INVOCATION` WARNING. No consumer tree is affected (0 check errors on all three). Is this a correct "a broken check never passes" outcome, or a misclassification — a deliberate refusal from a shared walker being treated as a crash, which would make it a net new failure (R3-2 shape) for user models? If misclassified, say what the right outcome is (the implementer's alternative: a WARNING that V2 could not inspect the attribute, like D15).
2. **Phase 9 uv side effect**: `init --execution-target` on a directory with no `pyproject.toml` creates a file holding only the table, which makes uv treat that directory as its own project (separate `.venv`, `uv lock` succeeds instead of erroring, a nested directory stops using the parent's environment). Is creating the file acceptable, or should `init` refuse and print the line instead?

## Rules

- Read-only on `~/src/sysml-codegen`, `~/src/dc3`, `~/src/fusion-tea` (use `git archive` exports if needed). Do not touch any Item 2 artifact.
- Green for this repo: no new failures relative to `evidence/baseline.md` (6 known pytest failures, ruff 118, mypy 97); touched files clean under ruff check, ruff format --check and mypy. Never run repo-wide `ruff format`.
- Do not fix code. Write findings with `file:line`, severity (must-fix / should-fix / note), and a concrete failure scenario. Commit `audit.md` only (explicit path staging; never stage `.gitignore`, `.project/EPIC_GUIDE.md`, `.project/README.md`, `.project/active/README.md`, `.project/backlog/README.md`, `.project/epic_template.md`).
- Plain language per `.claude/rules/working-voice.md`.
