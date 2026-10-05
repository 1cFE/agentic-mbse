# Brief: implement — pm-registry-integrity

**Stage:** `/_my_implement`. **Plan:** `.project/active/pm-registry-integrity/plan.md`. **Design:** `design.md` (approved). **Spec:** `spec.md` (contract). One session per phase; this session implements the phase named in the line at the bottom. Read the plan's Implementation Record first and resume where the checkboxes stop. Do not implement a later phase.

## What this work is for

[AGENT, re-derived] Registry entries and their IDs are stable referents that other artifacts cite by spelling. The code you write closes the paths by which a record disappears or an ID is issued twice. When a detail is not settled by plan or design, pick the option that cannot lose a record, record it in the Implementation Record, and continue.

## Rules for this session

- **Red first is mandatory where the plan says so.** Paste the failing run's relevant lines into the Implementation Record before you touch source.
- **Quality bar.** Code that reads as if it had always been in `parser.py` and `operations.py`: typed, small functions, docstrings in the file's existing style, no duplicated splitting or ID logic anywhere. Follow the design's names (`_split_table_row`, `_escape_table_cell`, `_registry_ids`, `_single_match`, `_insert_table_row`) unless a name is clearly wrong, and say so if you change one.
- **Gates G1 to G4** per the plan's parity rule (decided by the orchestrator; see the note in the plan). Record the actual counts in the Implementation Record.
- **Do not run or edit** `.orchestrate-logs/ft-snapshot/e4_check.py` or `snapshot_parse.py`. You may read the fusion-tea copies there.
- **Do not commit.** The orchestrator commits each phase after reviewing the diff. Do not touch the backlog, `CURRENT_WORK.md`, or any file outside `src/agentic_mbse/pm/`, `tests/test_pm_*.py`, and the plan.
- Tick the plan's checkboxes as you complete items and fill in the phase's Completion section with what changed, deviations, and anything the next phase needs to know.

End with the phase's gate results in a short table and the line `ARTIFACT: .project/active/pm-registry-integrity/plan.md`.

