# Brief: design — research-approval-empty-insights

**Sent:** 2026-10-05 by the orchestrator. **Stage:** `/_my_design`. **Spec:** `.project/active/research-approval-empty-insights/spec.md` (reviewed and revised; resolutions in `spec-review.md`).

## What this work is for

[AGENT, re-derived] Research approved with no new insight goes through the supported operation, so nobody moves the file by hand. Accepting `--insights '[]'` is the mechanism. The user reaches the operation only through the shipped `/research` command, so the instruction change there is part of the repair, not a doc afterthought.

## Owner rulings

- [OWNER] (2026-10-05) No reserved gates. The orchestrator decides and records. You decide the spec's open questions and record each decision with its reasoning in the design; do not ask.

## Scale

This is a LOW item, about half a day. Write a design sized to that: the decisions, the shape of the change, the test list. No alternatives survey for choices that have one sensible answer. If you find a decision that is not obvious, say so plainly at the top of your result so I can route it to a design review.

## Engineering bar

- One code path moves the file to `approved/`. The zero-insight case must not duplicate the move or grow a parallel copy of the function.
- The result is built from what happened. `files_modified`, `ids_assigned`, and the message derive from the entries actually written, not from a special-case string bolted on beside the old one.
- Validation order stays "refuse before any write." All path checks (under `pending/`, exists, is a regular file) run before anything is appended or moved, for empty and non-empty lists alike.
- Match the module's existing conventions in `src/agentic_mbse/pm/operations.py`: caller errors come back as `OperationResult(success=False, ...)` with a message that says what to do.
- Tests assert behavior on real temp projects, not mocks of the operation, wherever the spec criterion is about files on disk.

## Facts verified by the orchestrator (at `c37ff53` plus the spec commits)

- Function at `operations.py:910`; empty-list guard at `:936`; knowledge parse at `:943`; append loop then move at `:983-991`; result at `:993-1000`.
- `None` trap: the guard is `if not insights`. After the change, a branch written as `if not insights:` would treat `insights=None` as explicit emptiness and approve silently. The spec forbids that. The signature already makes `insights` a required keyword of type `list[InsightInput]`; decide how a `None` (or non-list) at runtime fails and record why.
- CLI: handler `pm_cli.py:346`; `_validate_json_list` at `pm_cli.py:56` already rejects malformed JSON, non-arrays, and invalid items with the usage exit code, and passes `[]` through. `_dispatch` at `pm_cli.py:78` prints warnings and `result.message` only. Registration and help text at `pm_cli.py:559-562` ("Approve a research file and extract insights"; "JSON array of InsightInput objects") describe insights as always present.
- `parse_knowledge` (`parser.py:684`) warns "File not found" on a missing file and raises on an undecodable one. The zero-insight path must not surface either.
- Existing tests: operations at `tests/test_pm_operations.py:1265-1360`; CLI at `tests/test_pm_cli.py:419-455` (these mock `_op_approve_research`). There is no end-to-end CLI test of this command through argparse today.
- Shipped text to change: `claude/commands/research.md:75-79` and `claude/skills/toolkit-awareness/SKILL.md:90`. Check whether any test under `tests/` pins the text of either file, and whether `scripts/replicate_setup.sh` or `cmd_init()` needs a coordinated change (CLAUDE.md "Change Coordination"). I expect not, since no file is added or renamed; confirm.
- fusion-tea does not parse the approval message (searched 2026-10-05). Message wording is free.

## Decisions to make and record

1. How the zero-insight path stays independent of `KNOWLEDGE.md` (spec criterion 2) while non-empty approval keeps its current parse-and-warn behavior.
2. How `None` or a non-list fails in Python: structured failure result or exception. [AGENT] My lean is a structured failure, matching the module's convention, with a message that names `[]` as the way to say "no insights." Challenge it if the module's other operations point the other way.
3. The zero-insight success message. [AGENT] It should state the file name, that it was approved, and that no insights were created. The non-empty message stays byte-for-byte as it is today.
4. The refusal message for a pending path that is not a regular file.
5. Exact replacement wording for `research.md:75-79`, the toolkit-awareness row, and the argparse help strings. Keep the `/research` change to a line or two: on approval with every insight skipped, call with `--insights '[]'`; report assigned IDs only when there are any.
6. The test list, mapped to spec criteria. Include: operation with `[]` (file moved, `KNOWLEDGE.md` byte-identical, and the missing-`KNOWLEDGE.md` variant), the Python-caller result fields, `None`, directory-as-file for empty and non-empty lists with nothing moved, non-empty regression, and CLI through the real parser for `--insights '[]'` (exit 0, message) and for a missing `--insights` (usage error).

Finish with `ARTIFACT: <path>`.
