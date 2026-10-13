# Brief: /_my_audit — research-seam-port (`WRAP-SPLIT` Item 5)

Audit the implementation on branch `research-seam-port` (base `ac5fb1a`) against `spec.md`, and write the audit to `.project/active/research-seam-port/audit.md`. Do not fix code. Do not commit. Start no background tasks. End with `ARTIFACT: <path>`.

## Read

- `spec.md` (the contract: nine success criteria), `design.md` (D1–D18, I1–I8, the Behaviour Changes table), `design-review.md` with its Resolutions, `plan.md` (every phase's Implementation Notes, where deviations are recorded), `briefs/align.md`, and every file in `evidence/`, all beside this brief.
- The fusion-tea code this port must preserve: the read-only snapshot `.orchestrate-logs/fusion-tea-snapshot/` (fusion-tea `0a833b9f7`, unchanged at `c42ed1d8a`). You cannot read fusion-tea itself. Criteria 2, 4, 6 and 7 rest on orchestrator-run evidence in `evidence/`. Check that evidence for consistency and completeness, not by re-running it.

## What to check, in priority order

1. **Behaviour preservation, independently.** Don't trust the design's table or the phase notes. Compare `src/agentic_mbse/research/` with the snapshot scripts:
   - ladder order;
   - outcomes and their messages;
   - class precedence;
   - request key;
   - receipt, return, negative, manifest-row and index-block bytes;
   - the four-files-or-nothing commit and its rollback;
   - `retire` and `verify`.
   List every behaviour difference you find, and classify each as listed in the design table, recorded in a phase's notes, or unrecorded. An unrecorded difference that could change fusion-tea's data or a caller's result is a finding.
2. **The hold-out hook fails closed** (D3–D5, I4, review M1 and M2). Look for any path through `register`, `retire` or `add-entry` that proceeds unchecked while a guard is configured.
3. **Each spec criterion is met, with evidence.** For each one, give the evidence and a verdict (met, partly met, not met). Criterion 5: run the grep yourself. Criterion 9: run `uv run pytest tests/`, `uv run pytest tests/test_research -m ""`, `uv run ruff check src/ tests/` and `uv run mypy src/`. The baselines are in `.orchestrate-logs/baseline-{pytest,ruff,mypy}.txt` (2,217 passed; ruff 118; mypy 88).
4. **Engineering quality.** Is it typed, are the module boundaries clean, is there any dead code? Do the tests check behaviour, and would they catch a regression? Look for placeholder code, TODOs, skipped tests, `# type: ignore` or `noqa` without a reason, and loosened golden values.
5. **Shipped text.** `skills/research-acquire/`, `skills/manage-sources/`, `docs/research-seam.md`, the `run-goal` and runbook edits, and `docs/source-index.md`:
   - Do they read as agentic-mbse's general rules?
   - Do they match what the CLI actually does: flags, outputs, refusals, exit codes?
   - Does `manage-sources` meet the owner's ruling? [OWNER-VERBATIM] 2026-10-09: "MORE useful as a general skill which allows direct user management while it folows and enforces the rules".

Out of scope: decisions the Align record settled, and design choices the review accepted, unless the code shows they fail.

## Verdict

Give one of: Certify, Certify with follow-ups, or Do not certify. List findings with severity:
- **Must-fix before merge**: a defect, data risk, or criterion not met.
- **Follow-up**: worth a backlog line.
- **Advisory**.

Give each finding a file:line and a concrete failure scenario. Keep must-fix to what is truly blocking.
