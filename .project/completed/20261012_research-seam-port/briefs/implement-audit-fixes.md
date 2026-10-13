# Brief: /_my_implement — audit follow-ups, research-seam-port

The audit (`audit.md`, Certify with follow-ups) left three follow-ups and some advisories. The orchestrator is fixing them before merge in one phase. Follow `briefs/implement.md` (the shared bar, environment facts and finish steps). Add a "Phase 7: audit follow-ups" section to `plan.md` with checkboxes and Implementation Notes, and commit once.

## Fix

1. **F1: registered text cannot hide the index.** `register` refuses any caller-supplied text that it writes into the index block and that contains `<!--`: the title, the three sentences, and a keyed source's `key_label` and `key_display`. Use the same rule and message style `add-entry` uses (`index.py`). The refusal is `precondition_failed` before capture, with a receipt when `--run` is given. Add the row to the design's Behaviour Changes table, then a test per field kind.
2. **F2: `init` stops telling users to hand-edit the index.** Its closing output (`src/agentic_mbse/cli/__init__.py:687-689`, per the audit) points at `/manage-sources` instead. Find and update any test that pins the old wording.
3. **F3: a misspelled config table fails closed.** A key under `[tool.agentic-mbse]` other than `research`, or a `[tool.agentic_mbse]` table (underscore form), is a configuration fault, which gives the failing guard, as an unknown key inside `[tool.agentic-mbse.research]` already does (D4). agentic-mbse reads no other target config today, so this blocks nothing. Update D4's wording in the design and the hook guide in `docs/research-seam.md`. Add tests for both spellings, each using a source that registers when the fault is absent.
4. **U4: `retire`'s rollback skips a parked artifact that no longer exists,** as the snapshot did (`source_registry.py:1172,1176`). Add a test.

## Advisories to apply

- Fix the evidence file names in the migration ledger and `plan.md` that point at files that don't exist. The real files are in `evidence/`: `o1-baseline.md`, `o1-parity-early.md`, `o1-fusion-tea-branch.md`, `fusion-tea-runbook.md`, and `dry-run/README.md` with its streams.
- In `evidence/dry-run/README.md`, add one line under O2a: the orchestrator chose a copper question instead of the design's aluminium 6061 because the shipped `research-acquire` skill uses the aluminium request as its own example, and a dry run that repeats the example tests less.
- Close the audit's doc gaps around `--adequacy` (it affects only a bounded negative; say so where the skill and guide tell the agent to use it), `--budget`, and the runbook's class table. Be exact about what the CLI does.

Leave the rollback-of-a-failed-final-index-write advisory alone. The old scripts behave the same way.

## Exit

Use the same exit check as every phase: the full suite with no new failures (the last count was 2,748 passed), `tests/test_research -m ""` green, ruff and mypy at baseline, and criterion 5's grep clean. Report the numbers.
