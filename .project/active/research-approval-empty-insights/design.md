# Design: Approve Research with No New Insights

**Status:** Accepted by the orchestrator 2026-10-05 (D5 ratified; no separate design review). D5's shape and the `research.md` sentence amended 2026-10-05 after [audit](audit.md) A1 and A4.
**Owner:** Reid W
**Created:** 2026-10-05 20:49 PDT
**Branch:** research-approval-empty-insights
**Commit at writing:** 9e3a847
**Complexity:** LOW

## Overview

Make `approve_research` accept an explicit empty insight list: the document moves to `approved/`, nothing touches `KNOWLEDGE.md`, and the result says no insights were created. Tighten the path checks so the newly cheap call cannot move something that is not a pending document, and update the shipped `/research` instructions so agents actually make the call.

## Related Artifacts

- **Spec:** [spec.md](spec.md) (reviewed and revised; resolutions in [spec-review.md](spec-review.md)).
- **Product lens:** [product-lens.md](product-lens.md) (CLEAR).
- **Backlog:** `PM-APPROVE-RESEARCH-EMPTY-INSIGHTS` and the out-of-scope `PM-APPROVE-RESEARCH-MOVE-SAFETY` in [BACKLOG.md](../../backlog/BACKLOG.md).
- **Historical contract:** FR-9 in [PM operations spec](../../completed/20260203_d4.4-operations/spec.md) (no minimum insight count).
- **Brief:** [briefs/design.md](briefs/design.md).
- No epic, no Required Reading, no ADR index (`.project/adr/` does not exist).

## The Point

[INHERITED: backlog PM-APPROVE-RESEARCH-EMPTY-INSIGHTS] Research is sometimes approved without producing a new domain insight: a source-registration round, a bounded negative result, a confirmation of what is already known. Today the operation refuses an explicit empty list with `No insights provided`, so the document stays in `knowledge/research/pending/` and operators move it by hand, bypassing the supported operation.

[INHERITED: product-lens.md] `/research` keeps two separate user decisions: approve the report, and accept or skip each insight. Only accepted insights enter `KNOWLEDGE.md`. The falsifier: a user approves a useful report while skipping every insight, and approval is refused, the report stays pending, or an unaccepted insight enters `KNOWLEDGE.md`.

[AGENT, from the brief] Users reach the operation only through the shipped `/research` command, so the instruction change there is part of the repair.

## Research Findings

- **The function** is `approve_research` at `src/agentic_mbse/pm/operations.py:910-1000`. Order today: containment check (`:921-928`), exists check (`:930-934`), empty-list guard (`:936-940`), registry read (`:943-946`), build and validate entries (`:948-981`), append each entry (`:984-986`), move (`:988-991`), result (`:993-1000`).
- **The registry read exists only to number new entries.** `parse_knowledge` and `_registry_ids` feed `all_ids`, which feeds `_next_id` (`:944-967`). Nothing else in the function uses them. Their warnings are the only warnings the function returns.
- **Probes at 9e3a847** (inline script on temp projects):
  - `insights=None` returns `success=False, "No insights provided"`.
  - An undecodable `KNOWLEDGE.md` raises `UnicodeDecodeError` from `parse_knowledge` (`parser.py:689-693` catches only `FileNotFoundError`).
  - `pending_file="knowledge/research/pending"` with one insight succeeds, mints DI-001, and moves the whole queue to `approved/pending/`.
  - `pending_file="knowledge/research/pending/../../KNOWLEDGE.md"` with one insight succeeds. It appends DI-001 to `KNOWLEDGE.md`, then moves `KNOWLEDGE.md` itself into `approved/`. The containment check at `:922-928` compares path text and does not collapse `..`.
- **Module convention.** Every public operation reports caller-input problems as `OperationResult(success=False, message=...)`. Private helpers raise `ValueError`, and the operations catch it and convert it (e.g. `:663-667`, `:1204-1205`). No public operation raises for bad input. No other public operation has a required list argument; `register_intent` treats `None` as "not given" because its lists are optional (`:1006-1011`).
- **Message style.** Success messages carry no trailing period ("Traced element 'X' in f", `:904`). The non-empty approval message is `Approved research: {name}. Created insights: {ids}` (`:996`).
- **CLI.** `cmd_pm_approve_research` (`pm_cli.py:346-358`) needs no change. `_validate_json_list` (`pm_cli.py:56-75`) passes `[]` through as an empty list. It rejects malformed JSON, non-arrays (including `null`), and invalid items with exit 2. `_dispatch` (`pm_cli.py:78-91`) prints warnings to stderr and `result.message` to stdout. Argparse `required=True` (`pm_cli.py:562`) makes a missing `--insights` exit 2.
- **CLI through the real parser in-process.** `main()` (`cli/__init__.py:1062`) calls `parser.parse_args()` with no argv. `tests/test_cli.py:316-339` drives it by monkeypatching `sys.argv`. `find_project_root` walks up from the working directory to `work/BACKLOG.md` (`cli/__init__.py:166-181`).
- **Shipped text.** The approval step is `claude/commands/research.md:75-79`. The skill row is `claude/skills/toolkit-awareness/SKILL.md:90`. No test pins the text of either file. `tests/test_cli.py:152-157` and `:440` check only that the skill directory exists.
- **Change coordination: none needed.** `research.md` and `toolkit-awareness` are already in the init lists (`MBSE_COMMANDS`, `MBSE_SKILLS` in `cli/__init__.py`) and in `scripts/replicate_setup.sh:57` and `:76`. Both are tool-owned, so content changes reach target repos on re-init. No file is added or renamed.
- **Consumer.** fusion-tea does not call `approve-research` or parse its message (orchestrator search, 2026-10-05). Wording is free.

## Core Concept

Approval is two things in sequence: record the accepted insights, then move the document. An empty list is the case where the first step has nothing to do, not a separate kind of approval. So the function keeps one path. The only steps that change are the ones that existed to serve the insights. The registry read exists to number new entries, so it runs only when there are entries to number. The result already describes what was written, so it is built from the entries list: no entries means no `KNOWLEDGE.md` in `files_modified`, no IDs, and a message that says none were created.

Removing the guard also removes the accidental protection it gave. Today the guard is the only thing that stops a cheap call from moving the whole `pending/` directory, or a file reached with `..`, without a visible DI to show it happened. So the path checks become real checks: the path is normalized, then must lie under `pending/`, exist, and be a regular file. All of this runs before anything is written. Finally, the guard's other job, refusing a missing list, moves to an explicit type check. Emptiness (`[]`) and absence (`None`) stop sharing one falsy test.

## Key Bets

- **B1.** The `KNOWLEDGE.md` read in this function serves only ID numbering. *If false → skipping it on the zero-insight path silently drops some other check.* Verified by reading `operations.py:943-981`: the read feeds only `all_ids` and `warnings`.
- **B2.** One explicit sentence in the shipped `/research` approval step is enough for an agent to route "report approved, every insight skipped" to `--insights '[]'`. *If false → agents keep skipping the call or moving files by hand, and the repair never reaches users even though the operation works.*
- **B3.** No consumer parses the approval message. *If false → the new zero-insight message breaks a parser.* Verified for fusion-tea by the orchestrator. The non-empty message is unchanged, so only the new case could be affected.

## Key Decisions

- **D1. The zero-insight path does not touch `KNOWLEDGE.md`.** The registry read runs only when the list is non-empty. Non-empty approval keeps its read, its warnings, and its crash on an undecodable file, all exactly as today. *Rejected: keep the read and drop its warnings on the zero path.* An undecodable file would still raise, so success would still depend on the file's contents, which spec criterion 2 rules out.
- **D2. A missing or non-list `insights` returns a structured failure.** An `isinstance(insights, list)` check takes the old guard's place. Message: `Insights must be a list of InsightInput, got {type name}; pass [] to approve with no insights`. The signature stays `insights: list[InsightInput]`, keyword-only, no default, so omitting it still raises `TypeError` from Python itself. *Rejected: raise `TypeError` for `None`.* The module never raises for caller input, and `None` already returns `success=False` today, so an exception would change behavior for existing callers. *Rejected: no check at all.* `None` would then fail only because the build loop happens to iterate the list, as an exception. A later edit that guards the loop would turn absence into a silent approval, which is the trap the spec forbids. The type check must come before the D1 gate; that ordering is what makes the gate's truthiness test safe.
- **D3. Messages.** Zero insights: `Approved research: {name}. No insights created`. Non-empty: unchanged, byte for byte. Both share the `Approved research: {name}.` prefix and differ only in the clause built from `ids_assigned`.
- **D4. A pending path that is not a regular file is refused.** A `pending_path.is_file()` check runs right after the existing exists check, which keeps its `File not found` message. Message: `Not a regular file: {path}; name one research document in {pending_dir}`. Applies to empty and non-empty lists alike, per spec criterion 3.
- **D5. `..` is collapsed only below `pending/`.** The root is used exactly as the caller gave it, so it names the directory the OS resolves, symlinks and `..` included. `pending_dir` is built from that root. The document path is taken relative to `pending_dir` with the textual `relative_to`; a failure is the existing `File '...' is not in ...` refusal. `os.path.normpath` then collapses `..` in that relative part only, and if the result climbs out (its first part is `..`) the call gets the same refusal. The document path is rebuilt as `pending_dir` joined with the collapsed part, and that one path serves the exists check, the regular-file check, and the move. The refusal names the path as the caller gave it. A `..` that stays inside (`pending/sub/../doc.md`) still works, and so does a root containing `..` with a relative document path. A document path spelled differently from the root, such as an absolute path when the root contains `..`, is refused, as at the base; matching two spellings of one directory would need symlink resolution. **[AGENT] (ratified by orchestrator, 2026-10-05; shape set by orchestrator ruling on audit A1, same day); see the note at the end of this section.** The first form applied `os.path.normpath` to both full paths; audit A1 showed that with a root holding a symlink followed by `..` it took the document from one tree and moved it into another, because `normpath` and the OS read `link/..` differently. *Rejected: `Path.resolve()`.* It follows symlinks, so `pending_dir` would have to be resolved too, and a symlinked pending document would start being refused. Nobody asked for that change. *Rejected: normalize the root once and build every path from it* (audit A1's suggestion). Every path would agree, but `normpath` of a root holding a symlink followed by `..` can name a different project than the OS resolves. *Rejected: file it under `PM-APPROVE-RESEARCH-MOVE-SAFETY`.* That would leave the `[]` call this item ships able to move `KNOWLEDGE.md` or any other file under the project into `approved/` with nothing written to show it happened.
- **D6. Shipped wording.** Exact text is in Implementation Notes. `research.md` gains one line and keeps its existing lines. The skill row and the two argparse help strings stop implying insights are always present.
- **D7. CLI tests run through the real parser in-process.** They call `main()` with a monkeypatched `sys.argv`, as `tests/test_cli.py:316-339` does, inside a real temp project. *Rejected: `subprocess` with `uv run agentic-mbse`.* It is slower and depends on the installed entry point. The existing subprocess tests check help text only.

**Note on D5.** The spec review brought the directory case into scope (resolution L3-4 (c)) under this rule: one validation that refuses only calls that were never valid, needed because removing the guard lowers the barrier. The `..` case meets the same rule. It differs in one way: passing the directory is a plausible slip, while a `..` path needs a deliberately odd argument. The orchestrator ratified D5 on 2026-10-05 and amended spec criterion 4 to match: the criterion is about documents inside `pending/`, and a path that leaves `pending/` once `..` is collapsed is refused. Reasoning: the containment check already claims to enforce this, the fix is one line, and no valid call is lost.

## Architecture

The function keeps its shape: validate, number, write, report. Changes are marked.

```
below = path under pending_dir, ".." collapsed below it      # D5; refuse if not under or climbs out
pending_path = pending_dir / below                            # D5; root used as given
refuse unless exists; is_file()                               # D4 adds is_file
refuse unless isinstance(insights, list)                      # D2, replaces `if not insights`
taken_ids, warnings = [], []
if insights: read KNOWLEDGE.md -> taken_ids, warnings         # D1
entries = build and validate each insight (may refuse)        # unchanged; no-op for []
append each entry to KNOWLEDGE.md                             # unchanged; no-op for []
move pending_path to approved/                                # the single move, unchanged
return result from entries: files_modified, ids_assigned, msg # D3
```

- **Data flow for `[]`:** path checks, type check, skip the read, build nothing, append nothing, move, report `files_modified=[approved]`, `ids_assigned={}`, `warnings=[]`.
- **Data flow for non-empty:** identical to today, except the two new path refusals.
- **CLI:** unchanged code path. `'[]'` arrives as an empty list, the operation succeeds, and `_dispatch` prints the message and exits 0. `--insights` omitted stops at argparse (exit 2); `'null'` stops at `_validate_json_list` (exit 2).

## Required Invariants

- **I1. Refuse before any write.** Every refusal, including field validation inside the build loop, returns before the first append, the `approved/` mkdir, or the move.
- **I2. One move.** The function has exactly one move statement, shared by both list sizes.
- **I3. Zero insights never touches `KNOWLEDGE.md`.** No read and no write, so its bytes and its absence are preserved and it cannot add warnings.
- **I4. Absence is not emptiness.** `insights` has no default. `None` and non-lists refuse with a structured failure and move nothing.
- **I5. Non-empty output is unchanged.** Same message, same `files_modified` order (`[KNOWLEDGE.md, approved]`), same IDs and warnings.
- **I6. The result is derived.** `files_modified` includes `KNOWLEDGE.md` only when entries were appended, and the message clause comes from `ids_assigned`. No branch builds a parallel result.

## Component Overview

- **`approve_research`** (`src/agentic_mbse/pm/operations.py:910`) carries all behavior changes: D1, D2, D3, D4, D5, plus a docstring that says an empty list approves with no insights and `None` is refused. It needs an `import os` (current imports at `:11-16`).
- **Argparse registration** (`src/agentic_mbse/cli/pm_cli.py:560`, `:562`) gets two help-string edits. The handler is untouched.
- **`claude/commands/research.md:75-79`** gets one added line for approval with no accepted insights.
- **`claude/skills/toolkit-awareness/SKILL.md:90`** gets a reworded description cell.
- **Tests** go in `tests/test_pm_operations.py` (class `TestApproveResearch`, `:1263`) and `tests/test_pm_cli.py` (a new class beside `TestPmApproveResearch`, `:418`). See Validation Approach.

## Non-Goals

- Failed-move-after-append and same-name overwrite in `approved/` stay as they are; filed as `PM-APPROVE-RESEARCH-MOVE-SAFETY` (spec Non-Goals).
- Element types inside a non-empty list are not checked. A list holding something other than `InsightInput` fails as it does today. The CLI already validates items, and the type annotation covers Python callers.
- The user approval gate at `research.md:69-71` is unchanged, and so is the missing `uv run` prefix in the `research.md` call example.
- `SKILL.md:85`'s claim that PM mutations "succeed fully or not at all" stays; it belongs to `PM-APPROVE-RESEARCH-MOVE-SAFETY`.

## Implementation Notes

- **Keep the check order.** The order is: containment with `..` collapsed below `pending/`, exists, `is_file`, type check, gated read. The gate is written `if insights:`, which is safe only because the type check ran first. Put a short comment on the gate saying so.
- **Initialize for the zero path.** `warnings` and the taken-ID list start empty before the gate, so the build loop and the result need no special case.
- **`files_modified`.** Build it as `KNOWLEDGE.md` only if entries were appended, then the approved path. This keeps today's order for non-empty approvals.
- **Exact replacement text.** `research.md`: keep lines 75-79 as they are, and add one line after line 79:
  > If the user approves the report with no accepted insights (every candidate skipped, or none proposed), still make the call, with `--insights '[]'`. The file moves to `approved/` and no DI-XXX entries are created, so tell the user that instead of reporting IDs.
- **`SKILL.md:90` description cell:**
  > Approve pending research and register any accepted domain insights (`'[]'` approves with none)
- **`pm_cli.py:560` subcommand help:** `Approve a pending research file and record any insights`.
- **`pm_cli.py:562` `--insights` help:** `JSON array of InsightInput objects; '[]' approves with no insights`. It contains no `%`, so argparse formatting is safe.

## Potential Risks

- **Target repos keep the old instruction until re-init.** An agent running an older installed `research.md` will not know about `'[]'`. That resolves itself once the consumer moves its pin and re-runs init; see Integration Strategy.
- **D5 refuses a path that worked before.** Only paths whose `..` segments leave `pending/` are affected. Any such path used today would have moved a file from outside the queue into `approved/`, so no valid use is lost.
- **Symlinks inside `pending/` are trusted.** A symlinked directory inside `pending/` lets a call move a file that lives outside `pending/`, and with `[]` nothing is written to show it (audit A2). This follows from D5 not resolving symlinks, needs write access to `pending/` to set up, and the base had the same exposure with one insight; filed as case (c) of `PM-APPROVE-RESEARCH-MOVE-SAFETY`.

## Integration Strategy

The change replaces a manual workaround (moving the file by hand) with the supported call. Operation and CLI changes take effect wherever the package is installed. The `/research` and skill text reaches a target repo on `agentic-mbse init` re-run, because both are tool-owned. fusion-tea pins agentic-mbse by commit, so it picks this up when its pin moves past the merge and it re-runs init.

## Validation Approach

Spec criteria, in spec order: **SC1** `[]` succeeds on both surfaces; **SC2** `KNOWLEDGE.md` left exactly as found; **SC3** omission is a caller error; **SC4** non-empty behavior retained, existing refusals hold, non-regular file refused; **SC5** accurate reporting per observer; **SC6** shipped text; **SC7** tests cover `[]` and missing `--insights`.

Operation tests, on real temp projects (`tests/test_pm_operations.py`):

| # | Test | Asserts | Criteria |
|---|------|---------|----------|
| 1 | Empty list approves, parametrized over `KNOWLEDGE.md` state: fusion-tea shape (`_write_archived_knowledge`, `:536`; a read would warn about DI-014), undecodable bytes (a read would raise), missing | success; document only in `approved/`, content unchanged; `KNOWLEDGE.md` bytes identical, or still absent; `ids_assigned == {}`; `files_modified == [approved]`; `warnings == []`; exact message | SC1, SC2, SC5, SC7 |
| 2 | `None` and the string `"[]"` refused | not success; message contains `pass []`; document still pending; `approved/` not created; `KNOWLEDGE.md` unchanged | SC3, I4 |
| 3 | Omitting `insights=` | raises `TypeError` (pins "stays required") | SC3 |
| 4 | `pending/` directory as the file, parametrized `[]` / one insight | not success; message starts `Not a regular file`; queue still in `pending/`; `approved/` absent; `KNOWLEDGE.md` unchanged | SC4, I1 |
| 5 | `pending/../../KNOWLEDGE.md`, parametrized `[]` / one insight; plus a valid document approved with a `project_root` that contains `..` | escaping path: not success, `is not in` message, `KNOWLEDGE.md` in place and unchanged; valid document: approved | SC4 (D5) |
| 6 | Existing `test_file_not_in_pending` and `test_missing_file`, parametrized `[]` / one insight | still refused; nothing moved; `KNOWLEDGE.md` unchanged | SC4, I1 |
| 7 | Existing `test_happy_path`, extended | exact message `Approved research: 20260202-120000_hts.md. Created insights: DI-001, DI-002`; `files_modified == [KNOWLEDGE.md, approved]` | SC4, I5 |

CLI tests through `main()` in a real temp project with `work/BACKLOG.md` (`tests/test_pm_cli.py`):

| # | Test | Asserts | Criteria |
|---|------|---------|----------|
| 8 | `pm approve-research <pending doc> --insights '[]'` | returns 0; stdout is exactly the zero-insight message; stderr empty; document in `approved/`; no `KNOWLEDGE.md` created (no DI written) | SC1, SC5, SC7 |
| 9 | Same call without `--insights` | `SystemExit` code 2; stderr names `--insights`; document still pending | SC3, SC7 |
| 10 | `--insights 'null'` | returns 2; stderr says it must be a JSON array; document still pending | SC3 |

The existing mocked CLI tests (`tests/test_pm_cli.py:418-455`) stay as they are.

Manual checks: read the diff of `research.md` and `SKILL.md` against the exact text above (SC6). Run `uv run pytest tests/test_pm_operations.py tests/test_pm_cli.py`, then `uv run ruff check src/ tests/`, `uv run ruff format --check src/ tests/`, and `uv run mypy src/`.

## Next-Stage Handoff

- **Fixed:** D1-D7, the messages, the exact shipped wording, and the test list above.
- **Open:** helper names and how tests 1, 4, 5, and 6 share setup (a small `_pending_doc` fixture or helper is fine); whether test 2's two cases share one parametrized test.
- **De-risk first:** none needed. Build the operation change and tests 1-7 first. The CLI tests and text edits depend on nothing else.

---
Next Step: `/_my_plan`.
