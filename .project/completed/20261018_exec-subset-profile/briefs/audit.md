Audit EXEC-SUBSET-CONTRACT Item 1 as implemented on branch `exec-subset-profile` (implementation commits from 9721bc1b through 044e32c1; base 23d9ef32 for the code diff), against `.project/active/exec-subset-profile/spec.md` (with Change Log; SA-1 accepted), `design.md` (rev 2; R1 decided by owner 2026-10-18), and `plan.md` (all phases ticked, with implementation notes and orchestrator rulings). Read-only access to ~/src/sysml-codegen (b5663c07) and ~/src/dc3; do not modify them.

Do not self-certify on the implementer's reports. Verify independently:

- Every spec success criterion: met, met-with-recorded-limit, or not met — with evidence you checked. Known shortfall to judge, not excuse: the dc3 baseline run is INCOMPLETE and B8 appears only as `unconfirmed` (see `acceptance.md`). Say whether the spec criterion as written is met, and whether the reason is sound.
- R2 safety mechanically: can the evaluator emit `refused` for any (shape, context) without a certifying probe? Try to break it (e.g. a record edit, a missing observation, a code mismatch) in a scratch copy and confirm a test fails.
- Engineering quality: placeholder code, TODOs, dead code, duplicated model interpretation beyond the approved occurrence port, silent fallbacks, exception swallowing, nondeterminism, vocabularies not closed/validated, decision layer importing SysIDE, any `sysml_codegen` import, `SI_*` names outside evidence fields.
- Tests: if you can run them, run `uv run pytest tests/`, `uv run mypy src/`, `uv run ruff check src/ tests/` and compare against the recorded baseline (118 ruff / 97–98 mypy / 3 environment pytest failures at 8b027bbc). If your permissions block running commands, say so; the orchestrator runs them separately.
- `agentic-mbse validate` output unchanged by Item 1 (check the recorded diff evidence).
- Site account: 502 rows reconcile; spot-check a sample of dispositions against codegen source yourself.
- Untracked `.codex/`, `AGENTS.md`, `.project/TRIAGE_MEMORIES.md` and the modified `.gitignore` are not part of this work; ignore them.

Produce the audit artifact (`.project/active/exec-subset-profile/audit.md`) with a verdict and must-fix / should-fix items.
