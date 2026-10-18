# Session check (Phase 1 stop condition)

**Outcome: the stop rule fired, so Phase 1 is stopped before the commit and the before/after run.** The with/without test differs on one repo fixture, `tests/fixtures/sump_pump`. The evidence below says the session does not cause the difference: that fixture gives different results from one fresh load to the next with today's code and no session. Whether that counts as a B5 failure, and how the test should treat the fixture, is the owner's call.

## What differs

- `tests/test_validation/test_session.py::test_level_results_are_identical_with_and_without_session[sump_pump]` fails. Across runs the differing level was L6 (extra ERROR `Constraint 'Station::station::pump_fit' is a malformed numerical statement: missing_predicate`), and once L2.
- The other 13 repo fixtures give identical L2–L6 results with and without the session.

## Why it is not the session

- `sump_pump/` holds three copies of the same model (`right/`, `seed/`, `wrong/`), each declaring root packages `Drainage` and `Station`. Pointing a level at `sump_pump/` loads all three together, so `Station`'s `private import Drainage::*` can resolve to any of the three `Drainage` packages. Only `right/`'s `Drainage` defines `CapacityCoversDemand`, the type of `pump_fit`.
- `session-check-scripts/repeat_l6_check.py` loads `sump_pump/` fresh 10 times in one process and runs today's `check_constraint_executability` on each load, with no session. Six runs of 10 gave the `pump_fit` ERROR on 6, 10, 7, 8, 5 and 7 of the 10 loads. Holding every model alive (as the session does) or not made no difference.
- `session-check-scripts/fixture_determinism.py` runs each of L2–L6 standalone 8 times per fixture with no session: `sump_pump` varies at L2, L4 and L6. Every other fixture, and `sump_pump/right`, `sump_pump/seed` and `sump_pump/wrong` on their own, give the same result every time.

So the with/without comparison on `sump_pump/` compares two draws from a result that already varies today.

## Consumer trees: identical, and twice as fast

`scripts/l6_subset/run_consumers.py session-equality` exports each tree with `git archive` and runs L1–L6 in one process: first standalone, as the base runner does, then all inside one `ValidationSession`. It compares each level's full result (success, every issue string, warnings, metrics, every structured issue), not the five issue lines the text prints. Raw record: `session-equality.json`.

| Tree | L1–L6 identical | Standalone (s) | One session (s) | Model loads in session | Constraint extractions |
|---|---|---|---|---|---|
| fusion-tea `f96ad312` | all six | 407.8 | 205.7 | 1 | 1 |
| dc3 `808464d` | all six | 34.6 | 17.3 | 1 | 1 |
| dc3 `60b44d5` | all six | 25.2 | 12.7 | 1 | 1 |

- The code was this checkout's working tree (HEAD `0d69c883` plus the uncommitted session change, `session-equality.json` → `code` has its hash). The change is saved as `session-uncommitted.patch`.
- The timing is in process, not the plan's subprocess `before-after` run (that needs the session committed). For comparison, the subprocess `validate --complete` baseline took 410.9 s on fusion-tea (`baseline-consumers.md`), close to the 407.8 s standalone figure.
- The machine was not idle for the whole run: another agent's test suites (`~/src/subset-conformance`) started partway through. Each run uses one core of 12. The halving matches what removing one of two ~200 s extractions predicts.
- dc3 and fusion-tea HEAD and `git status` were unchanged before and after.

## Other repository checks with the session change

- Full suite: the 6 baseline failures, plus the `sump_pump` case above. Two existing tests patched the old name `extract_identified_constraint_facts` on the L4 and L6 modules to inject facts (`test_item12_checks.py:211`, `test_level4_reconciliation.py:71`); they now patch `constraint_facts`, the name the levels call, and pass.
- mypy: 97 errors, the same set as the baseline. ruff check: the baseline 118 findings, nothing new. ruff format: every touched file is clean.
