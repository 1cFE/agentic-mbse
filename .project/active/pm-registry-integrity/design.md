# Design: Escaped Pipes and Registry ID Integrity

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-10-04 16:12 PDT
**Updated:** 2026-10-04
**Branch:** pm-registry-integrity
**Commit:** fd8e9d3 (spec contract at `5c15ab1`)
**Backlog Item:** PM-MATRIX-ESCAPED-PIPE

## Overview

Make PM reads and writes of the seven registries lossless, and make every ID allocator count every ID its registry file names. Three changes do it: one inverse pair for table cells, one ID discovery path for all seven prefixes, and a backlog writer that writes back the document it read.

## Related Artifacts

- **Spec (contract):** [spec.md](spec.md) at `5c15ab1`. Six success criteria, acceptance evidence E1 to E4.
- **Spec reviews:** [spec-review.md](spec-review.md) (per-registry exposure, probes 1 to 5) and [spec-review-2.md](spec-review-2.md) (token-max probe).
- **Brief:** [briefs/design.md](briefs/design.md). Verified fusion-tea facts: [briefs/spec_review.md](briefs/spec_review.md).
- **Product lens:** [product-lens.md](product-lens.md).
- **fusion-tea copies and E4 harness:** `.orchestrate-logs/ft-snapshot/` (gitignored): `e4_check.py`, `snapshot_parse.py`, `baseline.json`.
- **Design scratch:** `.orchestrate-logs/design-scratch/gfm_pipe_check.py` and `backlog_roundtrip.py` (gitignored).
- **Historical contract:** `.project/completed/20260203_d4.4-operations/spec.md:73`.
- No epic and no Required Reading. No decision register exists in this repo (`.project/adr/` is absent), so no ADR entries were read or are proposed.

## The Point

[INHERITED: product-lens.md, from claude/skills/project-structure/SKILL.md] Other artifacts cite registry IDs (`SV-`, `DI-`, `PR-`, `AD-`, `WI-`, `G-`, `AQ-`) by spelling. A record that silently disappears, or an ID minted twice, makes those citations ambiguous. The product lens's falsifier is "a supported registry entry disappears silently or an extant registry ID is reused."

Both happen today:

- Reads drop valid rows. The table splitter treats `\|` as a cell boundary (`parser.py:109`).
- Writes delete or corrupt records. The backlog writer rebuilds `BACKLOG.md` from parsed data (`operations.py:155`). `update_validation` has its own splitter that writes into the wrong column (`operations.py:1148`). `add_validation` writes pipes unescaped (`operations.py:194`).
- Allocators count only parsed records (`operations.py:58`), so a dropped record's ID can be minted again.

[AGENT, from the brief] Every decision below is judged by one question: does it keep a record from disappearing, or an ID from being issued twice? A design that passes the tests but leaves a third way to split a row, or a second place that knows how IDs are numbered, has missed the point.

## Research Findings

- **Two splitters, both naive.** `parser.py:109` and `operations.py:1148` split on every `|`. Spec review 2 confirmed these are the only pipe splitters in `src/`.
- **One row writer, no escaping.** `_format_table_row` (`operations.py:194`) is used by `promote_requirement` (`:395`), `add_validation` (`:517`), and `register_intent` (`:760`, `:786`). `update_validation` builds its row inline (`:1158`).
- **Eight allocation sites, all fed by parsed IDs.** `add_insight` (`:311`), `promote_requirement` (`:392`), `register_decision` (`:429`), `add_validation` (`:514`), `approve_research` (`:673`, loop at `:694`), `register_intent` G and AQ (`:742-743`, loops at `:758`, `:784`), `add_item` (`:966-974`).
- **The backlog writer dumps typed data.** `_write_backlog` (`operations.py:155-160`) serializes `BacklogData`. Its three callers are `add_epic` (`:923`), `add_item` (`:1008`), and `close_item` (`:1107`). `close_item` rewrites three frontmatters and moves the directory first (`:1078-1104`).
- **`parse_frontmatter` warns only on read failures.** Missing file, no opening or closing delimiter, malformed YAML, non-mapping (`parser.py:204-239`). It also turns top-level date and boolean scalars into strings (`:241-246`).
- **Reusable pieces.** `_strip_html_comments` (`parser.py:54`) already defines "outside HTML comments" for every parser. `approve_research` already builds every entry before its first write (`operations.py:675`).
- **GFM reference behaviour, checked.** markdown-it-py 4.0.0 with GFM tables renders `x \| y` as one cell `x | y`, renders `` `p\|q` `` as code `p|q`, keeps `a \\| b` as one cell, and splits `` `m|n` `` at the bare pipe. pandoc's gfm reader agrees except on `\\|`, where it splits. Script: `.orchestrate-logs/design-scratch/gfm_pipe_check.py`.
- **fusion-tea's backlog is plain YAML.** Its frontmatter re-dumps byte-identical from the raw mapping and from the typed model (`.orchestrate-logs/design-scratch/backlog_roundtrip.py`). It has no YAML comments (`sr2_probe.py`, probe A).
- **Token maxima on fusion-tea.** SV token max 135 equals the row max. DI token max 14 against 11 parsed (the archive note). PR 7 against 5 heading-shaped. AD 8 against 8. No G or AQ tokens (`sr2_probe.py`, probes B and C).
- **Probes reproduce.** Probes 1 to 5 from the spec review reproduce at `fd8e9d3`.
- **Nothing shipped describes this behaviour.** No file under `claude/`, `docs/`, or `project_templates/` describes ID allocation or pipe escaping, so no user-facing text needs rewording.

## Core Concept

Every loss in the Problem has the same shape. A tool acts on its parsed view of a registry file when it should act on the file. The splitter's view drops a row. The allocator counts the view. The backlog writer writes the view back. The fix keeps the parsed view for the jobs it does well: lookups, warnings, and the backlog dashboard. It sends three actions through the file itself:

1. **One inverse pair reads and writes cells.** `_split_table_row` reads a row the way GitHub does: a pipe right after a backslash is content, and that one backslash is dropped. `_escape_table_cell` puts a backslash before every pipe. Escaping and then splitting returns the original value for every single-line string, by construction. Every row reader calls the splitter, and every row writer formats through the escape.
2. **An ID is taken if the file names it.** One function finds every same-prefix ID token in the registry file outside HTML comments. `_next_id` takes the maximum over those tokens and the parsed IDs, then mints one above it. One regex defines what a token is, and both the scan and `_next_id` use it.
3. **The backlog writer writes back the document it read.** `add-item`, `add-epic`, and `close-item` load the frontmatter of `BACKLOG.md` as a plain YAML mapping, apply their one edit to it, and dump it. A record the validator rejects is never dropped, because the writer no longer rebuilds lists from validated data. The parsed view still decides what the operation may do, and it renders the body.

These pieces build on existing code. `_strip_html_comments` defines "outside HTML comments" for both the parser and the scan. `parse_frontmatter` stays the only frontmatter reader on the PM read path. `_next_id`'s padding is unchanged. `approve_research`'s "build everything, then write" pattern is how refusals avoid partial writes.

## Key Bets

- **B1. The registry file is a full enough record of the IDs in use.** IDs leave a registry file only by deletion, or by archiving under a note that names the range. fusion-tea's three archive notes work this way (`KNOWLEDGE.md:11`, `REQUIREMENTS.md:5`, `ARCHITECTURE.md:5`). This is the spec's narrowed contract ([AGENT], spec Decisions). *If false → an ID that leaves without a trace gets reused. Preventing that would need a persistent high-water mark, which the spec rules out.*
- **B2. ID tokens outside HTML comments are records, citations, or archive notes, not noise.** On fusion-tea the token maxima exceed the parsed maxima only through archive notes (Research Findings). Every shipped template holds its example IDs only inside HTML comments (spec-review L3-1). *If false → the scan skips many numbers. The spec accepts such gaps. But if a template ever carries an ID outside a comment, the first minted IDs change and existing tests fail (`test_pm_operations.py:497`, `:577`, `:845`).*
- **B3. Real backlogs are plain YAML that survives `safe_load` then `dump` unchanged.** fusion-tea's does, byte for byte. *If false (comments, anchors, or quoting style matter to users) → each write still drops that formatting, as today. Records survive, but their text changes.*
- **B4. GitHub's table rule is the reading that matters, and markdown-it-py shows it.** markdown-it-py was run here. cmark-gfm, GitHub's renderer, was not run. *If false → a `\\|` cell renders differently on GitHub than it parses. The impact is negligible today: no registry file contains `\\|` (spec-review L3-4).*

## Key Decisions

All decisions below are agent-grade by construction. D2, D6, D8, and D9 settle the spec's Open Questions.

- **D1. One splitter, in `parser.py` beside `_parse_markdown_table`.**
  - Algorithm: split on every pipe not preceded by a backslash, replace each `\|` with `|`, strip each cell, then drop the empty edge cells that a leading and trailing pipe produce. Dropping edge cells is today's rule (`parser.py:110-114`).
  - Code spans get no special handling, exactly as in GFM. `\|` inside backticks is unescaped, and a bare pipe inside backticks splits.
  - Callers: `_parse_markdown_table` and `update_validation`.
  - *Rejected: tracking backtick spans (GFM does not do it, and markdown-it splits `` `m|n` ``); keeping a second splitter in `operations.py` (that is the defect being removed).*
- **D2. `\\|` follows GitHub's rule.** A pipe right after a backslash never splits, and only that one backslash is removed, so `\\|` reads as `\|`. A splitter test pins it. *Rejected: pandoc's reading, where `\\` is a literal backslash and the pipe then splits. It is not GitHub's behaviour, and it would make the writer escape backslashes too.*
- **D3. The writer escape lives beside the splitter, and `_format_table_row` applies it to every cell.** `_escape_table_cell` puts a backslash before every pipe. It raises `ValueError` on a line break, because no single-line row can read back a multi-line value. *Rejected: escaping only the free-text columns (two rules to keep in sync); turning line breaks into `<br>` (the value would not read back identical, so criterion 3 would fail).*
- **D4. `update_validation` rewrites the row from its split cells.**
  - It finds the row with the shared splitter, sets the Status cell, and writes `_format_table_row(cells)`. Split and format are inverses, so every other cell's value is unchanged and `\|rel dev\|` is written back as `\|rel dev\|`.
  - It refuses without writing when the row is present but its ID is not a parsed record. On a row with raw pipes, the ninth cell is not the Status column.
  - *Rejected: splicing the Status cell by character offset (needs a second splitter API that returns spans); keeping today's "write the ninth cell of any matching row" (on fusion-tea's malformed `SV-034` it would overwrite part of the description and report success).*
- **D5. One ID discovery path, in `operations.py` beside `_next_id`.**
  - `_id_pattern(prefix)` is the only regex that says what an ID looks like.
  - `_registry_ids(path, prefix, parsed_ids)` returns a `ParseResult[list[str]]`. Its data is the parsed IDs plus every token `_id_pattern` finds in the file after `_strip_html_comments`. Its warnings are one per token whose number no parsed record holds.
  - `_next_id(prefix, ids)` keeps its signature and padding. It matches with `_id_pattern(prefix).fullmatch` instead of its own regex.
  - All eight allocation sites feed `_next_id` from `_registry_ids`.
  - *Rejected: detecting only record-shaped text per format (it mints `DI-012` on fusion-tea's `KNOWLEDGE.md` and fails the archive-note test; spec-review-2 L3-1); passing a path to `_next_id` (puts I/O in a pure helper pinned by five tests, `test_pm_operations.py:54-70`).*
- **D6. The token boundary is `(?<![A-Za-z0-9-])PREFIX-(\d+)(?!\d)`.**
  - Left side: the prefix must not be glued to a letter, digit, or hyphen, so `MAG-001` is not `G-001`.
  - Right side: only the digit run has to end, so a citation with a suffix still reserves its number.
  - The E4 harness and both review probes use this same boundary.
  - The number is `int(digits)`, so `PR-1` and `PR-001` both count as 1, as today.
  - Appendix A pins the cases.
  - *Rejected: a right boundary that also excludes letters and hyphens. `SV-034a` would then not reserve 34, and under-counting is the direction that reuses IDs.*
- **D7. Reservation diagnostics go in the operation result, not the parser.** Each allocating operation returns its parse warnings, then the warnings from `_registry_ids`. Example: location `SV-034`, message "named in VALIDATION_MATRIX.md but not a parsed record; its ID stays reserved." Matching is by number, so a parsed `PR-1` covers a `PR-001` mention. *Rejected: rewording parser warnings to name the ID. That changes E3's snapshot for every rejected row, and E3 allows new diagnostics, not altered ones.*
- **D8. The backlog writer writes back the loaded document.** [AGENT] This deviates from the brief's steer, with reasoning re-derived.
  - `_load_backlog(path)` returns the frontmatter mapping, read through `parse_frontmatter`, and its typed view, built by `_parse_backlog_mapping`. That function is extracted unchanged from `parse_backlog`.
  - Operations look up their target in the typed view, then edit the mapping. `add-item` appends one work-item mapping. `add-epic` appends one epic mapping. `close-item` sets `status` and `completed` on one mapping.
  - `_write_backlog` dumps the mapping and renders the body from its typed view.
  - *Rejected: the steer's mechanism, where the parser keeps each rejected work item's raw mapping and the writer re-emits it beside the typed ones.*
    - To keep E2's one-record diff, it must put each rejected item back at its original index in its original list. That is position bookkeeping across three kinds of list.
    - It still drops unknown keys and rejected epics unless extended further.
    - The kept mappings add a field to `BacklogData`, which changes E3's backlog snapshot.
    - Writing back the document keeps all of these by construction, with no new types.
- **D9. The backlog writer refuses in exactly two cases, both before any file is touched.**
  - Case 1: `BACKLOG.md` exists but its frontmatter cannot be read as a mapping. That means no opening delimiter, no closing delimiter, malformed YAML, or YAML that is not a mapping. These are exactly the conditions `parse_frontmatter` warns on, and the error quotes that warning.
  - Case 2: the list the operation must extend exists but is not a list. That is `epics` for `add-epic`, `standalone` for `add-item`, or the target epic's `items` for `add-item` with an epic. Appending would mean replacing it.
  - Everything else is carried forward unchanged: work items and epics with invalid or missing fields, non-mapping entries, unknown keys, and unknown top-level keys.
  - A missing or empty `BACKLOG.md` is an empty backlog, as today.
  - *Rejected: refusing on any record that fails validation (fails E2's WI case, spec OQ3); refusing on an invalid epic or a non-mapping entry (once the document is written back, nothing forces it).*
- **D10. Table add operations format every row before their first write.**
  - `promote_requirement` and `add_validation` already format before appending. They now turn D3's `ValueError` into a refusal.
  - `register_intent` today validates and appends one goal at a time (`operations.py:748-798`). It will build every goal and question row first, then append, in the same shape as `approve_research`.
  - *Rejected: leaving the interleaved loop. A refused second goal would leave the first one written, against criterion 5's "a refused write leaves every file unchanged."*
- **D11. No new module.**
  - The splitter and the escape are parsing concerns, so they live in `parser.py`. ID discovery and the backlog document are allocation and write concerns, so they live in `operations.py`.
  - `operations.py` imports `_split_table_row`, `_escape_table_cell`, `_strip_html_comments`, and `_parse_backlog_mapping` from `parser.py`. The tests already import private helpers this way, and none of ruff's selected rules flag it (`pyproject.toml:76`).
  - *Rejected: a `pm/tables.py` module for two functions a few lines long.*

## Architecture

There are three seams. Each has one owner and named callers.

**Table cells.** The pair lives in `parser.py`.

```
read:  _parse_markdown_table (parser.py:59) ─┐
       update_validation (operations.py:1118) ┴─> _split_table_row ─┐ inverse pair
write: _format_table_row (operations.py:194) ──> _escape_table_cell ─┘ (parser.py)
       callers: promote_requirement, add_validation, register_intent, update_validation
```

- Rows with no backslash before a pipe split exactly as before, so their parsed values are unchanged (criterion 6.3).
- Rows with `\|` now parse to the unescaped value (criterion 6.4). This includes PR, G, and AQ rows that parse with shifted columns today.

**ID allocation.**

```
parse_<registry>(path) ─> parsed IDs ───────────────────────────┐
file text ─> _strip_html_comments ─> _id_pattern(prefix).finditer ┴─> _registry_ids
_registry_ids.data ─> _next_id ─> PREFIX-NNN (max + 1)
_registry_ids.warnings ─> OperationResult.warnings (after the parse warnings)
```

| Prefix | File | Operations |
|---|---|---|
| DI | `KNOWLEDGE.md` | `add_insight`, `approve_research` |
| AD | `ARCHITECTURE.md` | `register_decision` |
| PR | `REQUIREMENTS.md` | `promote_requirement` |
| SV | `VALIDATION_MATRIX.md` | `add_validation` |
| G, AQ | `OVERVIEW.md` | `register_intent` |
| WI | `BACKLOG.md` | `add_item` |

Operations that mint several IDs in one call start their running list from `_registry_ids`, then append each new ID. They do the same with parsed IDs today.

**Backlog writes.**

```
BACKLOG.md ─> parse_frontmatter ─> document (dict) ─> _parse_backlog_mapping ─> typed view
typed view ─> target lookups and warnings
operation edits one mapping in the document
_write_backlog ─> yaml.dump(document) + _render_backlog_body(typed view of the edited document)
```

- `parse_backlog` becomes `parse_frontmatter` plus `_parse_backlog_mapping`, with identical output. `state.py:208`, the dashboard, and E3's snapshot see no change.
- `_write_backlog` accepts either a `BacklogData`, which it dumps first, or a loaded document. The existing tests build their fixtures through the `BacklogData` form (`test_pm_operations.py:902`, `:1134`).

**`close-item` ordering.**

- Today it resolves the directory, checks `work/active/`, parses the backlog, and finds the item. Then it rewrites three frontmatters, moves the directory, and writes `BACKLOG.md` (`operations.py:1026-1107`).
- Under D8 and D9 every refusal falls in the first half. `_load_backlog` and the item lookup run before the first rewrite, and the final dump cannot refuse.
- So a refused `close-item` leaves the item in `work/active/` with every file untouched.

## Required Invariants

- **I1.** For every single-line value with no leading or trailing whitespace, formatting it into a row and splitting the row returns the value in the same position.
- **I2.** For a row with no backslash right before a pipe, `_split_table_row` returns exactly what today's split returns.
- **I3.** `_format_table_row` puts a space on each side of every delimiter, so a value ending in a backslash never escapes the next delimiter.
- **I4.** A minted ID's number is greater than every parsed ID's number and every same-prefix token's number in its file outside HTML comments. Allocation is max + 1 and never fills gaps.
- **I5.** `_id_pattern` is the only definition of an ID token. `_next_id` and `_registry_ids` both use it.
- **I6.** After a backlog write, the frontmatter equals the loaded frontmatter plus the operation's one edit. No epic or work-item mapping other than the target is added, removed, reordered, or changed.
- **I7.** In every PM write operation, every refusal returns before the first file write.
- **I8.** Parser output on fusion-tea's registry copies is unchanged, except that `SV-035` appears and its warning disappears (E3).

## Component Overview

- **`_split_table_row`, `_escape_table_cell`** (`parser.py`, new, beside `_parse_markdown_table`). The inverse pair for one row and one cell value.
- **`_parse_markdown_table`** (`parser.py:59`, changed). Splits header and data rows with `_split_table_row`. Nothing else changes.
- **`_parse_backlog_mapping`** (`parser.py`, extracted from `parse_backlog` at `:251-465`). Validates a loaded frontmatter mapping into `BacklogData` and appends warnings. `parse_backlog` calls it.
- **`_id_pattern`, `_registry_ids`** (`operations.py`, new, beside `_next_id`). The token definition, and the file scan with its reservation warnings.
- **`_next_id`** (`operations.py:58`, changed). Same signature and output; matches with `_id_pattern`.
- **`_format_table_row`** (`operations.py:194`, changed). Escapes every cell.
- **`_load_backlog`** (`operations.py`, new). Returns the document and its typed view, or raises `ValueError` with D9's first-case message. A missing or empty file gives an empty document.
- **`_backlog_list`** (`operations.py`, new). Returns the list to append to under a key. It creates the list when the key is absent or null, and raises `ValueError` when the key holds something else (D9, second case).
- **`_write_backlog`** (`operations.py:155`, changed). Dumps a document, or a `BacklogData` converted first, and renders the body from the document's typed view.
- **Operations** (`operations.py`, changed).
  - All eight allocation sites use `_registry_ids`.
  - `add_item`, `add_epic`, and `close_item` edit the document.
  - `update_validation` uses the inverse pair and refuses unparsed rows.
  - The three table add operations refuse multi-line values before writing.
- **Unchanged.** `types.py`, the public operation signatures, and the CLI. The CLI prints the new warnings through `_print_warnings` (`cli/pm_cli.py:39`).

## Non-Goals

- **Repairing malformed records,** such as fusion-tea's `SV-034`, or validating a reserved record's content. Reserving an ID does not make its record valid (spec Known Requirements).
- **Escaping in the backlog body and the status dashboard.** Both render names for display and are never parsed back. If they used `_escape_table_cell`, a multi-line name would crash a write after `close-item`'s side effects.
- **Keeping YAML comments, anchors, or quoting style** in `BACKLOG.md` frontmatter. PyYAML drops them today and still will (B3).
- **Looking up columns by header in `update_validation`.** It still writes the ninth cell of a parsed row, which is Status in every shipped layout.
- **Making `close-item` transactional against malformed frontmatter** in `spec.md`, `design.md`, or `plan.md`. `_update_frontmatter_fields` (`operations.py:73-96`) can still raise partway through a close. That is a crash, not a refusal, and no registry record is lost. It is listed here because it is the one remaining half-close path.
- **Turning `_append_table_row`'s missing-section error into a refusal** (`operations.py:225-226`).
- **The spec's own Non-Goals stand:** deleted IDs, archived IDs no longer named in the file, and WI directory names.

## Implementation Notes

- **Splitter and escape.** The splitter is `re.split(r"(?<!\\)\|", line)` followed by `cell.replace("\\|", "|")`. The escape is `value.replace("|", "\\|")`. I1 holds because each `\|` in escaped text is one inserted backslash plus one original pipe.
- **Pure extraction.** `_parse_backlog_mapping` must keep the same loop bodies, warning text, and warning locations. E3 compares warning lists.
- **Unreadable means any warning.** `_load_backlog` treats any `parse_frontmatter` warning on an existing file as unreadable. Its docstring should say so, so that a benign warning added there later does not silently start refusing writes.
- **Top-level normalization is harmless.** `parse_frontmatter` stringifies top-level dates and booleans. The writer only touches `epics` and `standalone`, which are lists, so no record is affected.
- **New mappings keep today's shape.** Append new items and epics as `Model(...).model_dump(mode="json")`, which is what today's writer emits. E2's WI diff is then one mapping, including `completed: null`.
- **Raw lookups.** `close-item` takes the first work-item mapping, in any epic's `items` or in `standalone`, whose `str(id)` equals the ID. `add-item` takes the first epic mapping whose `str(name)` matches. The typed view has already confirmed the target is a valid record.
- **Existing tests stay unchanged.** In particular `TestNextId` (`test_pm_operations.py:54-70`), which pins `_next_id`'s signature.
- **E1's fixture labels are reversed from fusion-tea by design.** The fixture has escaped `SV-034` and malformed `SV-035`. Do not "correct" it.

## Potential Risks

- **Users will see new refusals.** `update-validation` refuses a row that does not parse. Backlog writes refuse a file whose frontmatter cannot be read. Table adds refuse a multi-line value. Each of these was silent corruption before. Mitigation: every message names the record or field and the reason.
- **A prose mention of a large number inflates every later ID.** An example is `SV-2026`. The spec accepts this. The reservation warning names the token, so the user can find it.
- **Duplicate IDs or epic names can mislead the raw lookup.** The lookup takes the first mapping with that ID or name. That can be a rejected one when a valid duplicate follows it. This only happens in a backlog that already has the defect this item prevents.
- **B4 rests on markdown-it-py, not GitHub's own renderer.** If GitHub differs on `\\|`, only D2's test and one sentence change.

## Integration Strategy

- **No outward changes.** No CLI, command, template, or type changes, and no public signature changes. Shipped docs say nothing about allocation or escaping.
- **New warnings.** Operation results gain reservation warnings, which print to stderr as other warnings do.
- **fusion-tea gets the fix on its next pin move.** Expected effects there:
  - Its matrix gains `SV-035`.
  - Its backlog frontmatter writes back byte-identical (B3).
  - `add-insight` mints `DI-015`.
  - `register-decision` still refuses until a `## Key Decisions` section exists.

## Validation Approach

The table avoids backslash examples on purpose, because GFM unescapes them inside table cells. The cell cases are listed below it.

| Criterion | Evidence | Where |
|---|---|---|
| 1. Escaped pipes | E1. The splitter cases below. A matrix row with an escaped pipe in its Description keeps its columns. | `test_pm_parser.py`; `TestAddValidation` |
| 2. One escape rule | `update-validation` on an escaped row: Status changes, and every other cell's text, escaped pipes included, is unchanged. Refusal on an unparsed row, with the file unchanged. | `TestUpdateValidation` |
| 3. Round-trip | For SV, PR, G, and AQ: add a value containing a pipe and read it back equal. The escape cases below. A multi-line value is refused with the file unchanged. | `TestAddValidation`, `TestPromoteRequirement`, `TestRegisterIntent`; parser tests |
| 4. No ID twice | E1. E2's seven fixtures. The archive-note test: `DI-001` to `DI-011` plus a note naming `DI-014` gives `DI-015`. The Appendix A cases. HTML-comment exclusion. The reservation warning. | each operation's test class; a `TestRegistryIds` class beside `TestNextId` |
| 5. No record lost on write | E2's WI case. `add-item`, `add-epic`, and `close-item` beside an invalid-field item: it is carried forward, and the frontmatter diff touches only the target. Malformed YAML refuses with every file unchanged. A refused `close-item` leaves the directory in `work/active/`. | `TestAddItem`, `TestAddEpic`, `TestCloseItem` |
| 6. Nothing else changes | E3: the existing suite stays green. The orchestrator runs the snapshot. | whole suite |

**Splitter cases** (criterion 1):

- `\|rel dev\|` in a cell reads as `|rel dev|`, and the cells after it keep their columns.
- `` `p\|q` `` reads as `` `p|q` ``: the escape works inside a code span.
- `` `m|n` `` splits at the bare pipe, as GFM does.
- `a \\| b` stays one cell and reads as `a \| b` (D2).
- A row without escapes splits the same as before, with edge cells dropped.

**Escape cases** (criterion 3): `a|b`, `a\|b`, `\\|`, and a value ending in `\` each survive escape-then-split unchanged. A value containing `\n` or `\r` raises.

- **E2's "exactly the one new record."** Compare line lists. There must be only added lines: exactly one carrying the new ID, and the rest blank separators. For WI, compare the loaded frontmatter mappings instead: after must equal before with one mapping appended.
- **E4, run by the orchestrator after implementation.** Expected results:
  - `SV-035` parses with Type `baseline`, Status `passing`, and literal `|rel dev|` in Description and Expected.
  - `SV-034` is still warned, at `row 33`.
  - The new row is `SV-136`, added as one line.
  - The next DI on the `KNOWLEDGE.md` copy is `DI-015`.
- **Tooling gates.** Run `uv run mypy src/`, `uv run ruff check src/ tests/`, and `uv run ruff format --check src/ tests/`.

## Next-Stage Handoff

- **Fixed:** D1 to D11 and I1 to I8. Also fixed: the token boundary, the refusal list, and keeping parser warnings unchanged.
- **Open:**
  - helper names (except `_next_id`, `_format_table_row`, and `_write_backlog`, which tests import);
  - the exact wording of warnings and refusals;
  - where new test classes sit within the named test files.
- **De-risk first:** write E1 and E2's WI case as failing tests. Then build in this order:
  1. the splitter, escape, and `update_validation`;
  2. ID discovery at all eight sites;
  3. the backlog document writer, which is the largest behaviour change;
  4. the remaining E2 cases and the full suite.

## Appendix A: Token boundary cases

| Text in the registry file | Counts as | Why |
|---|---|---|
| `MAG-001` | no `G` token | `G` follows a letter |
| `` `SV-034` `` | SV 34 | a backtick is not an identifier character; code spans count |
| `PR-1` | PR 1 | same number as `PR-001` |
| `SV-034a` | SV 34 | only the digit run must end |
| `SV-034-x` | SV 34 | same |
| `**PR-007**` | PR 7 | E2's decorated-ID fixture |
| `X-SV-001` | no `SV` token | joined to a longer identifier by a hyphen |
| `id: WI-002` | WI 2 | frontmatter is scanned like any other text |
| `DI-001 through DI-014` | DI 1 and DI 14 | the archive note is what protects `DI-014` |
| `<!-- SV-900 -->` | not counted | inside an HTML comment |
| `<!-- unclosed SV-900` | SV 900 | an unclosed comment is not stripped, the same as in the parser |

---

**Next Step:** `/_my_design_review` in a fresh session, then `/_my_plan`.
