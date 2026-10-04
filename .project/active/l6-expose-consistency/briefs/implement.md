# Brief: implement — l6-expose-consistency

Execute `.project/active/l6-expose-consistency/plan.md` phase by phase, checking off boxes and adding short implementation notes as you go. Read `design.md` first for the decisions (D1–D6) and invariants; the plan is derived from it. `spec.md` is the contract.

## Orchestrator decisions (execution-detail tier, [AGENT])

- **Gate ruling.** The repo-wide `ruff check`, `ruff format --check`, and `mypy src/` already fail on untouched code (119 ruff, 78 files to reformat, 91 mypy). For this item the gate is: those counts do not grow, every file you create is fully clean under all three tools, and the lines you change in existing files introduce no new ruff or mypy finding. Do not reformat `adr002.py`, `level6_architecture.py`, or `test_adr002.py` wholesale; keep the diff to the change. Record the before/after counts in the plan notes.
- **Baseline.** Default suite today: 1922 passed, 1 skipped, 33 deselected (slow corpus). It must end at the same or higher passed count with zero failures.
- **Do not reopen design decisions.** If something cannot be implemented as the design says, stop and report instead of improvising.

## Quality bar

- The predicate rename is the only structural change in `adr002.py`; the two guards are each a few lines with a comment that names the design decision (D2, D3) and says why the check skips EXPOSE, in plain words.
- The predicate docstring follows design D4 / Invariant 3 exactly: what the code checks, nothing more.
- Tests are readable: one assertion group per spec criterion, fixtures loaded through the existing `discover_sysml_files` / `load_sysml_model` helpers (which need `Path` objects), expected values spelled out, no `>=` where the design says exact.
- Delete the scratch probe directory `build/l6probe/` when done; it is gitignored but should not linger.

Commit nothing; the orchestrator commits. Finish with the ARTIFACT line pointing at `plan.md`, plus a short list of every file you created or changed.
