# Phase 6 fixes, sysml-codegen side (audit S2, S3 routing, S7)

Done 2026-10-21 on sysml-codegen `subset-profile-screen`, commits `4708f22d` and `a6cdb912` (on top of `4e037a88`). Nothing the generator accepts or refuses changed.

## What changed

- S2: backlog row `[ATTRIBUTE-MULTIPLICITY-DEFAULT-COUNT]`. Re-ran `evidence/guidance-examples/m_attr` and `m_attr_spec` at `4e037a88`: `check` exit 0, `generate` exit 0 with no warning, writes `pack__cells[0]` and `[1]` only; control `m_ok` writes three. Owner-held (RG-1).
- S3 routing: backlog row `[SILENT-LOSSES-UNREPORTED]` for String values and calc-usage result expressions, which the retired copy reported as `omitted` and nothing reports now (apart from L6's `L6_DESIGN_ATTR_UNEXTRACTABLE` under `designs/`). It points at RG-2 and RG1-3. The copy's three other `omitted` contexts (conditional branch, indexed reference, unsupported callable, `e268357f:src/agentic_mbse/sysml/subset_profile_rules.toml:326,483,546`) are named there but were not re-checked.
- S7: `site_account.csv` lost its `matrix_row` and `rule` columns; a header line says the account is only where the generator refuses, and that "the contract" in the kept coverage_limitation and note text means the copy at `e268357f`. `site_scan.py` no longer reads the columns; `witnesses.py` picks the mutated sites by role and file (public_capability rows plus stub-cause rows, then the shared sites), which is the same 79 sites as before; `test_mutator.py` now checks all 79 build (was the 11 shared-rule rows plus 6 shared sites); the matrix-ID form test is gone.
- S7 records: `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]` retired as moot (the screen it would carry was removed); `[ITEM-OWNED-PART-REFUSED]` no longer mentions the screen or a `rg1_pending` disagreement; `modeling-assumptions.md` § 10 no longer says the contract reports the calc-usage result; `CURRENT_WORK.md` says `check` prints only the generator's answer, and lines 13 and 21 no longer describe the contract or the L6 subset lines as live. The brief's `git grep` found nothing else stale: the other hits are the extraction-diagnostic screen and unrelated "disagreement" names.

## Checks

- Suite, Phase 9 command, against agentic-mbse worktree at `0a6d8247` with Agent A's uncommitted edits: 8503 passed, 9 failed, 9 skipped, 124 deselected. The 9 failures are the base 9 in `evidence/baseline.md`. The pass count is 61 above the audit's 8442: 62 new `test_mutator` cases, less the removed matrix-ID test.
- Byte manifest `compare` against the Item 2b base: 0 differences. Refusal records: 0 of 173 differ.
- `ruff check src/ tests/`: 94 errors, as at base. mypy not re-run (no `src/` change).
