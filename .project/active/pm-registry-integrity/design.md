# Design: Escaped Pipes and Registry ID Integrity

**Status:** Draft (revised after design review)
**Owner:** Reid W
**Created:** 2026-10-04 16:12 PDT
**Updated:** 2026-10-04 16:38 PDT
**Branch:** pm-registry-integrity
**Commit:** 5c038fc (spec contract at `5c15ab1`; design review at `26d987c`)
**Backlog Item:** PM-MATRIX-ESCAPED-PIPE

## Overview

Make PM reads and writes of the seven registries lossless, and make every ID allocator count every ID its registry file names. Three changes do it: one inverse pair for table cells, one ID discovery path for all seven prefixes, and a backlog writer that writes back the document it read.

## Related Artifacts

- **Spec (contract):** [spec.md](spec.md) at `5c15ab1`. Six success criteria, acceptance evidence E1 to E4.
- **Spec reviews:** [spec-review.md](spec-review.md) (per-registry exposure, probes 1 to 5) and [spec-review-2.md](spec-review-2.md) (token-max probe).
- **Design review:** [design-review.md](design-review.md), with all findings accepted in its Resolutions. Probes in `.orchestrate-logs/design-review-scratch/` (gitignored).
- **Briefs:** [briefs/design.md](briefs/design.md) and [briefs/design_revise.md](briefs/design_revise.md). Verified fusion-tea facts: [briefs/spec_review.md](briefs/spec_review.md).
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
- **`parse_frontmatter` warns on read failures, but can also read less than the file without warning.** It warns on a missing file, a missing opening or closing delimiter, malformed YAML, or a non-mapping (`parser.py:204-239`), and it turns top-level dates and booleans into strings (`:241-246`). Two hand edits cut its read short silently (design review M4). PyYAML keeps the last of two duplicate keys. And the closing-delimiter check uses `.strip()` (`parser.py:219`), so an indented `---` inside a block scalar ends the frontmatter early.
- **The parser strips HTML comments before it splits rows** (`parser.py:482`, `:523`, `:735`). So a cell value containing `<!--` or `-->` does not read back, and it can pair with a marker elsewhere in the file (design review M2, `comment_value_probe.py`).
- **The matrix template holds row-shaped examples inside a comment.** `VALIDATION_MATRIX.md.template:28-30` holds `SV-001` and `SV-002` rows inside an HTML comment. A row lookup that does not skip comments sees them.
- **Reusable pieces.** `_strip_html_comments` (`parser.py:54`) already defines "outside HTML comments" for every parser. `approve_research` already builds every entry before its first write (`operations.py:675`).
- **GFM reference behaviour, checked.** cmark-gfm, GitHub's renderer, keeps `a \\| b` as one cell, unescapes `` `p\|q` `` to code `p|q`, and splits `` `m|n` `` at the bare pipe (design review, `cmark_gfm_pipes.py`). markdown-it-py 4.0.0 agrees on every case (`.orchestrate-logs/design-scratch/gfm_pipe_check.py`). pandoc's gfm reader differs only on `\\|`, where it splits.
- **fusion-tea's backlog is plain YAML.** Its frontmatter re-dumps byte-identical from the raw mapping and from the typed model (`.orchestrate-logs/design-scratch/backlog_roundtrip.py`). It has no YAML comments (`sr2_probe.py`, probe A).
- **Token maxima on fusion-tea.** SV token max 135 equals the row max. DI token max 14 against 11 parsed (the archive note). PR 7 against 5 heading-shaped. AD 8 against 8. No G or AQ tokens (`sr2_probe.py`, probes B and C). No copy has a hyphen-preceded token.
- **Probes reproduce.** Probes 1 to 5 from the spec review reproduce at `fd8e9d3`.
- **Nothing shipped describes this behaviour.** No file under `claude/`, `docs/`, or `project_templates/` describes ID allocation or pipe escaping, so no user-facing text needs rewording.

## Core Concept

Every loss in the Problem has the same shape. A tool acts on its parsed view of a registry file when it should act on the file. The splitter's view drops a row. The allocator counts the view. The backlog writer writes the view back. The fix keeps the parsed view for the jobs it does well: lookups, warnings, and the backlog dashboard. It sends three actions through the file itself:

1. **One inverse pair reads and writes cells.** `_split_table_row` reads a row the way GitHub does: a pipe right after a backslash is content, and that one backslash is dropped. `_escape_table_cell` puts a backslash before every pipe, and it refuses the few values no row can carry. Escaping and then splitting returns the original value, by construction. Every row reader calls the splitter, and every row writer formats through the escape.
2. **An ID is taken if the file names it.** One function finds every same-prefix ID token in the registry file outside HTML comments. `_next_id` takes the maximum over those tokens and the parsed IDs, then mints one above it. One regex defines what a token is, and both the scan and `_next_id` use it.
3. **The backlog writer writes back the document it read.** `add-item`, `add-epic`, and `close-item` load the frontmatter of `BACKLOG.md` as a plain YAML mapping and apply their one edit to it.
   - Each one finds its target in the file and refuses unless exactly one mapping matches.
   - The writer no longer rebuilds lists from validated data, so a record the validator rejects is never dropped.
   - The parsed view still decides what the operation may do, and it renders the body.

These pieces build on existing code. `_strip_html_comments` defines "outside HTML comments" for both the parser and the scan. `parse_frontmatter` stays the only frontmatter reader. `_next_id`'s padding is unchanged. `approve_research`'s "build everything, then write" pattern is how refusals avoid partial writes.

## Key Bets

- **B1. The registry file is a full enough record of the IDs in use.** IDs leave a registry file only by deletion, or by archiving under a note that names the range. fusion-tea's three archive notes work this way (`KNOWLEDGE.md:11`, `REQUIREMENTS.md:5`, `ARCHITECTURE.md:5`). This is the spec's narrowed contract ([AGENT], spec Decisions). *If false → an ID that leaves without a trace gets reused. Preventing that would need a persistent high-water mark, which the spec rules out.*
- **B2. ID tokens outside HTML comments are records, citations, or archive notes, not noise.** On fusion-tea the token maxima exceed the parsed maxima only through archive notes (Research Findings). Every registry template holds its example IDs only inside HTML comments. The one exception is `AD-001` in `EPIC_GUIDE.md.template`, which is not a registry file. *If false → the scan skips many numbers. The spec accepts such gaps. But if a registry template ever carries an ID outside a comment, the first minted IDs change and existing tests fail (`test_pm_operations.py:497`, `:577`, `:845`).*
- **B3. Real backlogs are plain YAML whose values survive `safe_load` then `dump`.** fusion-tea's survives byte for byte. On hand-edited YAML, the design review saw comments, block-scalar style, quoting, flow lists, and anchor names change, but no value. *If false (that formatting matters to users) → each write still drops it, as today. Records survive, but their text changes.*

## Key Decisions

All decisions below are agent-grade by construction. D2, D6, D8, and D9 settle the spec's Open Questions.

- **D1. One splitter, in `parser.py` beside `_parse_markdown_table`.**
  - Algorithm: split on every pipe not preceded by a backslash, replace each `\|` with `|`, strip each cell, then drop the empty edge cells that a leading and trailing pipe produce. Dropping edge cells is today's rule (`parser.py:110-114`).
  - Code spans get no special handling, exactly as in GFM. `\|` inside backticks is unescaped, and a bare pipe inside backticks splits.
  - Callers: `_parse_markdown_table` and `update_validation`.
  - *Rejected: tracking backtick spans (GFM does not do it); keeping a second splitter in `operations.py` (that is the defect being removed).*
- **D2. `\\|` follows GitHub's rule, confirmed with cmark-gfm.** A pipe right after a backslash never splits, and only that one backslash is removed, so `\\|` reads as `\|`. A splitter test pins it. *Rejected: pandoc's reading, where `\\` is a literal backslash and the pipe then splits. It is not GitHub's behaviour, and it would make the writer escape backslashes too.*
- **D3. The writer escape lives beside the splitter, and `_format_table_row` applies it to every cell.**
  - `_escape_table_cell` puts a backslash before every pipe.
  - It raises `ValueError` on a line break, on `<!--`, and on `-->` (D9, R8). No single-line row can read back a line break. The parser strips comment markers before it splits rows.
  - *Rejected: escaping only the free-text columns (two rules to keep in sync); rewriting line breaks as `<br>` or comment markers as entities (the value would not read back identical, so criterion 3 would fail).*
- **D4. `update_validation` rewrites one row from its split cells.**
  - **Candidate rows.** It lists the rows under `## Verification Registry`, up to the next `## ` heading and outside HTML comments, whose first split cell is the ID. That is the region the parser reads, so the template's commented example rows are never candidates.
  - **Comment exclusion.** `_strip_html_comments(text, keep_lines=True)` blanks each comment but keeps its newlines, so line numbers still match the file.
  - **Refusals.** It needs exactly one candidate (R6), and that row must parse as a record (R7). On a row with raw pipes, the ninth cell is not the Status column.
  - **Write.** It splits the **original file line** at the candidate's line number (not the comment-stripped copy, which is only used to find it), sets the Status cell, and writes `_format_table_row(cells)` back over that line. Split and format are inverses, so every other cell's value is unchanged and `\|rel dev\|` is written back as `\|rel dev\|`. If the original line carries an inline HTML comment, `_format_table_row` raises on the marker; the operation turns that into an R7 refusal and the file is untouched (RC1).
  - *Rejected: splicing the Status cell by character offset (needs a second splitter API that returns spans); today's "first matching row anywhere in the file" (a malformed duplicate earlier in the file takes the write); a whole-file scan with comments skipped (a summary table elsewhere would read as a duplicate, and the scope would differ from the parser's).*
- **D5. One ID discovery path, in `operations.py` beside `_next_id`.**
  - **One definition.** `_id_pattern(prefix)` is the only regex that says how an ID is numbered. The parser's per-prefix regexes (`parser.py:324`, `:400`, `:488`, `:529`, `:742`, `:766`) validate record IDs; they do not number them. Every ID they accept also fully matches `_id_pattern`.
  - **The scan.** `_registry_ids(path, prefix, parsed_ids)` returns a `ParseResult[list[str]]`. Its data is the parsed IDs plus every token `_id_pattern` finds in the file after `_strip_html_comments`. Its warnings are described in D7. On a missing file it returns the parsed IDs with no warning: the parser has already warned, and the operation creates the file.
  - **Allocation.** `_next_id(prefix, ids)` keeps its signature and padding. It matches with `_id_pattern(prefix).fullmatch` instead of its own regex. All eight allocation sites feed `_next_id` from `_registry_ids`.
  - *Rejected: detecting only record-shaped text per format (it mints `DI-012` on fusion-tea's `KNOWLEDGE.md` and fails the archive-note test; spec-review-2 L3-1); passing a path to `_next_id` (puts I/O in a pure helper pinned by five tests, `test_pm_operations.py:54-70`).*
- **D6. The token boundary is `(?<![A-Za-z0-9])PREFIX-(\d+)(?!\d)`.**
  - **Left side.** The prefix must not follow a letter or digit, so `MAG-001` is not `G-001`. A hyphen is allowed before it, so the archive range `DI-001-DI-014` reserves both 1 and 14.
  - **Right side.** Only the digit run has to end, so a citation with a suffix (`SV-034a`, `SV-034-x`) still reserves its number.
  - **The number** is `int(digits)`, so `PR-1` and `PR-001` both count as 1, as today.
  - **The E4 harness** uses a narrower left boundary that also excludes a hyphen. So its file maximum is never above the scan's, and E4's bar is unchanged.
  - Appendix A pins the cases.
  - *Rejected: excluding a hyphen on the left (`DI-001-DI-014` would reserve only DI 1; design review M3); excluding letters and hyphens on the right (`SV-034a` would not reserve 34). Under-counting is the direction that reuses IDs. Over-counting costs a gap at most.*
- **D7. Reservation diagnostics go in the operation result, not the parser.**
  - Each allocating operation returns its parse warnings, then the warnings from `_registry_ids`.
  - There is one warning per distinct number that no parsed record holds. Its location is the first spelling seen, for example `SV-034`. Its message reads like "named in VALIDATION_MATRIX.md but not a parsed record; its ID stays reserved."
  - Matching is by number, so a parsed `PR-1` covers a `PR-001` mention.
  - *Rejected: rewording parser warnings to name the ID. That changes E3's snapshot for every rejected row, and E3 allows new diagnostics, not altered ones.*
- **D8. The backlog writer writes back the loaded document.** [AGENT] This deviates from the brief's steer, with reasoning re-derived. The design review endorsed the deviation.
  - **Load.** `_load_backlog(path)` returns two things. One is the frontmatter mapping, read through `parse_frontmatter(path, unique_keys=True)`. The other is its typed view, built by `_parse_backlog_mapping`, which is extracted unchanged from `parse_backlog`.
  - **Edit.** Each operation finds its target in the mapping (D9, R3 to R5), checks it against the typed view, then edits the mapping. `add-item` appends one work-item mapping. `add-epic` appends one epic mapping. `close-item` sets `status` and `completed` on one mapping.
  - **Write.** `_write_backlog` dumps the mapping and renders the body from its typed view. It also accepts a `BacklogData`, which it dumps first. That form exists for test fixtures and fresh backlogs, and its docstring says so.
  - **Dashboard.** A carried-forward invalid record stays in the frontmatter but is missing from the rendered body. It shows up only as a parse warning. This matches the template's "the frontmatter wins" (`BACKLOG.md.template:9-14`). It is also how the spec's "re-rendered from the kept records" (`spec.md:65`) reads, where the kept records mean the valid ones.
  - *Rejected: the steer's mechanism, where the parser keeps each rejected work item's raw mapping and the writer re-emits it beside the typed ones.*
    - To keep E2's one-record diff, it must put each rejected item back at its original index in its original list. That means position bookkeeping across three kinds of list.
    - It still drops unknown keys and rejected epics unless it is extended further.
    - The kept mappings add a field to `BacklogData`, which changes E3's backlog snapshot.
    - Writing back the document keeps all of these by construction, with no new types.
- **D9. Every refusal this design adds, in one place.**
  - Each refusal returns `OperationResult(success=False)` before the operation's first write (I7).
  - Each message names the record or value and says what to change.
  - Today's input checks, such as empty fields and invalid enums, are unchanged.

  | # | Operations | Refuses when | The message says |
  |---|---|---|---|
  | R1 | `add-item`, `add-epic`, `close-item` | `BACKLOG.md` exists and its frontmatter cannot be read whole: no opening `---`, no unindented closing `---`, malformed YAML, a key repeated within one mapping, or a non-mapping | the reader's warning (which key, which line), to fix by hand |
  | R2 | `add-item`, `add-epic` | the list to extend (`standalone`, `epics`, or the target epic's `items`) exists but is not a list | the key, and that appending would discard it |
  | R3 | `add-item --epic`, `close-item` | no mapping matches the target, or several do | "not found", or every matching location, to deduplicate by hand |
  | R4 | `add-item --epic`, `close-item` | the one matching mapping is not a valid record | "present but not a valid record", quoting the parser warning at that location or its epic's |
  | R5 | `add-epic` | an epic mapping with that name already exists, valid or rejected | its location, plus its parser warning if it is rejected |
  | R6 | `update-validation` | no candidate row (D4) has the ID, or several do | "not found", or every matching line |
  | R7 | `update-validation` | the one candidate row does not parse as a record, or its original line holds an HTML comment marker | fix the row by hand; if it has more cells than the header, a pipe inside a cell must be written as backslash-pipe; a comment inside the row must be moved out of it |
  | R8 | `promote-requirement`, `add-validation`, `register-intent` | a cell value holds a line break, `<!--`, or `-->` | the offending marker and the value, to reword without it |
  | R9 | `promote-requirement`, `add-validation`, `register-intent` | a target section heading is missing, or no table outside HTML comments sits under it before the next `## ` heading (a table in a later section does not count) | the missing heading; or, when the new row would land inside a comment that opens on the table's last line, the line number of that comment |

  - **Lookups: each piece exists once.** What counts as a match is defined once per record kind. The "exactly one" rule is implemented once.
    - **The rule.** `_single_match(matches, what, where)` in `operations.py` takes `(location, match)` pairs, returns the single pair, and raises `ValueError` naming every location when there are none or several. R3 and R6 go through it.
    - **Backlog matches.** `_raw_epics(document, name)` and `_raw_work_items(document, wi_id)` produce the pairs. Their location strings use the parser's warning format (`epics[1]`, `epics[1].items[0]`, `standalone[2]`), so R4 can quote the matching warning.
    - **Matrix matches.** `update_validation` builds its pairs from D4's candidate rows.
    - **`add-epic`.** It uses the same `_raw_epics` finder and refuses on any match (R5). So it checks duplicates against the file, not the parsed data.
  - **R1's two short-read cases** come from design review M4.
    - **Repeated keys.** `parse_frontmatter(path, unique_keys=True)` loads with a SafeLoader subclass that rejects a repeated key in any mapping. It reports this through its existing warning, which R1 quotes. [AGENT] The resolution names top-level keys. The same loader check also covers nested mappings at no extra cost, and a second `items:` inside one epic hides a list the same way. Read-only callers keep the default, so `state.py` and the dashboard read as today.
    - **The closing delimiter.** Only an unindented `---` closes the frontmatter: `rstrip()` replaces `strip()` at `parser.py:219` and at `operations.py:83`. In YAML, a block scalar's content is indented, so an unindented `---` is never content. A `---` inside `goal: |` is now read as content rather than refused.
  - **Everything else is carried forward unchanged:** work items and epics with invalid or missing fields, non-mapping entries, unknown keys, and unknown top-level keys. A missing or empty `BACKLOG.md` is an empty backlog, as today.
  - *Rejected:*
    - *refusing on any record that fails validation (fails E2's WI case, spec OQ3);*
    - *refusing on an untargeted invalid epic or non-mapping entry (once the document is written back, nothing forces it);*
    - *first-match lookups (an item lands inside a rejected duplicate epic, and every view loses it; design review M1);*
    - *rejecting repeated keys for every reader (changes read-only consumers, while only the writer would delete the hidden data);*
    - *naming the short-read cases as Non-Goals (that would leave "everything else is carried forward" false).*
- **D10. Table add operations finish every check before their one write.**
  - **Extraction.** `_insert_table_row(text, section_heading, row) -> str` is extracted from `_append_table_row` (`operations.py:213-245`). It is pure and raises `ValueError` for a missing heading or table. `_append_table_row` becomes read, insert, write, so it keeps its signature and its tests.
  - **Single-row operations.** `promote_requirement` and `add_validation` format the row, then append it. Both steps raise before any write. Each operation turns that `ValueError` into a refusal (R8, R9).
  - **`register_intent`.** Today it validates and appends one goal at a time (`operations.py:748-798`). It will build every goal and question row first, insert them all into one in-memory copy of `OVERVIEW.md`, then write once. A missing `## Analysis Questions` section therefore refuses before any goal row is written.
  - *Rejected: the interleaved loop (a refused second goal leaves the first one written, against criterion 5's "a refused write leaves every file unchanged"); a separate check that every section exists (a second copy of `_append_table_row`'s section search).*
- **D11. No new module.**
  - The splitter and the escape are parsing concerns, so they live in `parser.py`. ID discovery, lookups, and the backlog document are allocation and write concerns, so they live in `operations.py`.
  - `operations.py` will import `_split_table_row`, `_escape_table_cell`, `_strip_html_comments`, and `_parse_backlog_mapping` from `parser.py`. `src/` has no such cross-module private import today; only tests do this. These are package-internal helpers, and none of ruff's selected rules flag it (`pyproject.toml:76`).
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
BACKLOG.md ─> parse_frontmatter(unique_keys=True) ─> document (dict)   [R1]
document ─> _parse_backlog_mapping ─> typed view (validity, warnings)
document ─> _raw_epics / _raw_work_items ─> _single_match ─> target   [R3, R5]
target checked against typed view                                    [R4]
operation edits the target or appends to its list                     [R2]
_write_backlog ─> yaml.dump(document) + _render_backlog_body(typed view of the edited document)
```

- `parse_backlog` becomes `parse_frontmatter` plus `_parse_backlog_mapping`, with identical output. `state.py:208`, the dashboard, and E3's snapshot see no change.
- The existing tests build their fixtures through `_write_backlog`'s `BacklogData` form (`test_pm_operations.py:163`, `:175`, `:902`, `:1134`).

**`close-item` ordering.**

- Today it resolves the directory, checks `work/active/`, parses the backlog, and finds the item. Then it rewrites three frontmatters, moves the directory, and writes `BACKLOG.md` (`operations.py:1026-1107`).
- Under D8 and D9, `_load_backlog` and the R3 and R4 lookups run before the first rewrite, and the final dump cannot refuse.
- So a refused `close-item` leaves the item in `work/active/` with every file untouched.

## Required Invariants

- **I1.** For every single-line value with no leading or trailing whitespace and no comment marker, formatting it into a row and splitting the row returns the value in the same position.
- **I2.** For a row with no backslash right before a pipe, `_split_table_row` returns exactly what today's split returns.
- **I3.** `_format_table_row` puts a space on each side of every delimiter, so a value ending in a backslash never escapes the next delimiter.
- **I4.** A minted ID's number is greater than every parsed ID's number and every same-prefix token's number in its file outside HTML comments. Allocation is max + 1 and never fills gaps.
- **I5.** `_id_pattern` is the only definition of how an ID is numbered. `_next_id` and `_registry_ids` both use it. The parser's record regexes validate and do not number.
- **I6.** After a backlog write, the frontmatter equals the frontmatter as `parse_frontmatter` loaded it, plus the operation's one edit. No epic or work-item mapping other than the target is added, removed, reordered, or changed. Unknown top-level date and boolean scalars come back as strings, because the loader stringifies them (`flag: yes` is written as `flag: 'True'`). No record is affected, and today's writer deletes such keys outright.
- **I7.** In every PM write operation, every refusal returns before the first file write.
- **I8.** Parser output on fusion-tea's registry copies is unchanged, except that `SV-035` appears and its warning disappears (E3).
- **I9.** A write that targets an existing record finds it in the file and proceeds only when exactly one record matches (`_single_match`). For tables, that means outside HTML comments.

## Component Overview

| Helper | Location | Change | Role |
|---|---|---|---|
| `_split_table_row`, `_escape_table_cell` | `parser.py`, beside `_parse_markdown_table` | new | the inverse pair; the escape refuses R8's values (D1 to D3) |
| `_parse_markdown_table` | `parser.py:59` | changed | splits header and data rows with `_split_table_row` |
| `_strip_html_comments` | `parser.py:54` | changed | `keep_lines=False` option: each comment becomes the newlines it held (D4) |
| `parse_frontmatter` | `parser.py:193` | changed | unindented closing delimiter; `unique_keys=False` option (R1) |
| `_parse_backlog_mapping` | `parser.py`, from `:251-465` | extracted | loaded mapping to `BacklogData` plus warnings; `parse_backlog` calls it (D8) |
| `_id_pattern`, `_registry_ids` | `operations.py`, beside `_next_id` | new | token definition, file scan, reservation warnings (D5 to D7) |
| `_next_id` | `operations.py:58` | changed | same signature and output; matches with `_id_pattern` |
| `_format_table_row` | `operations.py:194` | changed | escapes every cell |
| `_insert_table_row` | `operations.py`, from `:213-245` | extracted | pure insertion raising R9; `_append_table_row` wraps it (D10) |
| `_load_backlog`, `_backlog_list` | `operations.py` | new | document plus typed view, else R1; the list to append to, else R2 |
| `_raw_epics`, `_raw_work_items`, `_single_match` | `operations.py` | new | the finders and the one lookup rule (D9) |
| `_write_backlog` | `operations.py:155` | changed | dumps a document, or a `BacklogData` converted first; renders the body from its typed view (D8) |
| `_update_frontmatter_fields` | `operations.py:73` | changed | unindented closing delimiter, matching `parse_frontmatter` |

- **Operations that change.** The eight allocation sites use `_registry_ids`. `add_item`, `add_epic`, and `close_item` edit the document. `update_validation` follows D4. The table add operations follow D10.
- **Unchanged.** `types.py`, the public operation signatures, and the CLI. The CLI prints the new warnings and refusal messages through its existing paths (`cli/pm_cli.py:39`).

## Non-Goals

- **Repairing malformed records,** such as fusion-tea's `SV-034`, or validating a reserved record's content. Reserving an ID does not make its record valid (spec Known Requirements).
- **Escaping in the backlog body and the status dashboard.** Both render names for display and are never parsed back. If they used `_escape_table_cell`, a multi-line name would crash a write after `close-item`'s side effects.
- **Refusing comment markers in heading-registry and backlog values.** Out of scope because criterion 3 and resolution M2 cover table cells only. The residual risk is narrow. A `-->` written into a DI or AD value can hide records only if an unclosed `<!--` already sits earlier in the file. Those records would then be hidden from both the parser and the scan.
- **Keeping YAML comments, anchors, or quoting style** in `BACKLOG.md` frontmatter. PyYAML drops them today and still will (B3).
- **Looking up columns by header in `update_validation`.** It still writes the ninth cell of a parsed row, which is Status in every shipped layout.
- **Making `close-item` transactional against malformed frontmatter** in `spec.md`, `design.md`, or `plan.md`. `_update_frontmatter_fields` (`operations.py:73-96`) can still raise partway through a close, and so can `shutil.move`. Those are crashes, not refusals, and no registry record is lost. They are listed here because they are the remaining half-close paths.
- **The spec's own Non-Goals stand:** deleted IDs, archived IDs no longer named in the file, and WI directory names.

## Implementation Notes

- **Splitter and escape.** The splitter is `re.split(r"(?<!\\)\|", line)` followed by `cell.replace("\\|", "|")`. The escape checks for line breaks and comment markers, then applies `value.replace("|", "\\|")`. I1 holds because each `\|` in escaped text is one inserted backslash plus one original pipe.
- **Pure extraction.** `_parse_backlog_mapping` and `_insert_table_row` must keep the same loop bodies, messages, and warning locations as the code they come from. E3 compares warning lists.
- **Unreadable means any warning.** `_load_backlog` treats any `parse_frontmatter` warning on an existing file as R1. Its docstring should say so, so that a benign warning added there later does not silently start refusing writes.
- **The repeated-key check.** Inspect each mapping node's own keys before PyYAML flattens `<<:` merges, so a merge override is not reported as a repeat.
- **New mappings keep today's shape.** Append new items and epics as `Model(...).model_dump(mode="json")`, which is what today's writer emits. E2's WI diff is then one mapping, including `completed: null`.
- **R4's quoted warning.** Pick the parse warnings whose location equals the match's location, or is the enclosing `epics[i]` for an item inside a rejected epic.
- **Existing tests stay unchanged.** In particular `TestNextId` (`test_pm_operations.py:54-70`), which pins `_next_id`'s signature, and `TestAppendTableRow` (`:248-285`).
- **E1's fixture labels are reversed from fusion-tea by design.** The fixture has escaped `SV-034` and malformed `SV-035`. Do not "correct" it.

## Potential Risks

- **Users will see new refusals (R1 to R9).** Each covers a case that was silent corruption, a wrong target, or a raw exception before. Mitigation: every message names the record and says what to change.
- **A duplicate the user did not know about now blocks a write.** R3, R5, and R6 refuse until the user deduplicates by hand. That is the intent: guessing the target is the defect.
- **A prose mention of a large number inflates every later ID.** An example is `SV-2026`. The spec accepts this. The reservation warning names the token, so the user can find it.

## Integration Strategy

- **No outward changes.** No CLI, command, template, or type changes, and no public signature changes; `parse_frontmatter` gains only a defaulted keyword. Shipped docs say nothing about allocation or escaping.
- **New output.** Operation results gain reservation warnings. A missing section in a table registry now returns a refusal instead of raising (R9).
- **fusion-tea gets the fix on its next pin move.** Expected effects there:
  - Its matrix gains `SV-035`.
  - Its backlog frontmatter writes back byte-identical (B3).
  - `add-insight` mints `DI-015`.
  - `register-decision` still refuses until a `## Key Decisions` section exists.
  - `promote-requirement` refuses cleanly, instead of raising, until a `## Requirements` table exists.

## Validation Approach

Test names below are proposals for the plan. The tables avoid backslash examples because GFM unescapes them inside table cells; the cell cases are listed under the tables.

**By criterion.**

| Criterion | Evidence | Where |
|---|---|---|
| 1. Escaped pipes | E1. The splitter cases below. A matrix row with an escaped pipe in its Description keeps its columns. | `test_pm_parser.py::TestSplitTableRow`; `TestAddValidation::test_e1_three_record_reproduction` |
| 2. One escape rule | `update-validation` on an escaped row: Status changes, and every other cell's text, escaped pipes included, is unchanged. R6 and R7 tests below. | `TestUpdateValidation::test_escaped_row_changes_only_status` |
| 3. Round-trip | For SV, PR, G, and AQ: add a value containing a pipe and read it back equal. The escape cases below. R8 tests below. | `test_value_with_pipe_round_trips` in `TestAddValidation`, `TestPromoteRequirement`, `TestRegisterIntent` (G and AQ) |
| 4. No ID twice | E1. E2's seven fixtures. The archive-note test: `DI-001` to `DI-011` plus a note naming `DI-014` gives `DI-015`. The boundary cases (Appendix A). HTML-comment exclusion. One reservation warning per distinct number. | `test_mints_above_unparsed_record` in each operation's class; `TestAddInsight::test_archive_note_reserves_di_014`; `TestRegistryIds` |
| 5. No record lost on write | E2's WI case. An invalid-field item beside `add-item`, `add-epic`, and `close-item` is carried forward, and the frontmatter diff touches only the target. R1 to R5 tests below. | `test_carries_forward_invalid_item` in `TestAddItem`, `TestAddEpic`, `TestCloseItem` |
| 6. Nothing else changes | E3: the existing suite stays green. The orchestrator runs the snapshot. | whole suite |

**Each refusal has a named test.** Every refusal test also asserts that every file is unchanged.

| Refusal | Test (class in `test_pm_operations.py` unless noted) |
|---|---|
| R1 | `TestAddItem::test_refuses_unreadable_frontmatter`, parametrized: malformed YAML, no frontmatter, top-level `standalone` twice, `items` twice in one epic, closing `---` only indented. `TestAddEpic::test_refuses_malformed_yaml`. `TestCloseItem::test_refusal_leaves_item_active` (directory still in `work/active/`, `spec.md` unchanged). |
| R1 delimiter | `test_pm_parser.py::TestParseFrontmatter::test_indented_dashes_stay_in_block_scalar`; `TestAddItem::test_keeps_items_after_indented_dashes` |
| R1 repeated keys | `test_pm_parser.py::TestParseFrontmatter::test_unique_keys_rejects_repeat`; `::test_default_keeps_last_wins` |
| R2 | `TestAddItem::test_refuses_non_list_standalone`; `TestAddItem::test_refuses_non_list_epic_items`; `TestAddEpic::test_refuses_non_list_epics` |
| R3 | `TestAddItem::test_refuses_duplicate_epic_names` (a rejected and a valid epic `X`); `TestCloseItem::test_refuses_duplicate_work_item_ids` |
| R4 | `TestAddItem::test_refuses_rejected_epic_quoting_warning`; `TestCloseItem::test_refuses_invalid_item_quoting_warning` |
| R5 | `TestAddEpic::test_refuses_name_of_rejected_epic` |
| R6 | `TestUpdateValidation::test_refuses_duplicate_rows`; `TestUpdateValidation::test_ignores_commented_example_rows` (template with real `SV-001`) |
| R7 | `TestUpdateValidation::test_refuses_unparsed_row` (raw pipes; the message names the escape); `TestUpdateValidation::test_refuses_row_with_inline_comment_and_leaves_file_unchanged` |
| R8 | `test_pm_parser.py::TestEscapeTableCell::test_refuses_line_breaks_and_comment_markers`; `TestAddValidation::test_refuses_comment_marker`; `TestRegisterIntent::test_refused_second_goal_writes_nothing` |
| R9 | `TestRegisterIntent::test_missing_questions_section_writes_nothing`; `TestPromoteRequirement::test_missing_section_refuses` |

**Splitter cases** (`TestSplitTableRow`):

- `\|rel dev\|` in a cell reads as `|rel dev|`, and the cells after it keep their columns.
- `` `p\|q` `` reads as `` `p|q` ``: the escape works inside a code span.
- `` `m|n` `` splits at the bare pipe, as GFM does.
- `a \\| b` stays one cell and reads as `a \| b` (D2).
- A row without escapes splits the same as before, with edge cells dropped.

**Escape cases** (`TestEscapeTableCell`): `a|b`, `a\|b`, `\\|`, and a value ending in `\` each survive escape-then-split unchanged. Values containing `\n`, `\r`, `<!--`, or `-->` raise.

**Boundary cases.** `TestRegistryIds::test_token_boundary` is parametrized over every row of Appendix A.

**E2's "exactly the one new record."** Compare line lists before and after the write:

- Every change must be an added line.
- The added lines must form one contiguous block: the new record plus its blank separators.
  - For SV, PR, G, and AQ the record is one row.
  - For DI and AD it is the whole multi-line record: the heading and its field lines.
- Exactly one added line may carry the new ID.

For WI, compare the loaded frontmatter mappings instead: after must equal before with one mapping appended.

**E4, run by the orchestrator after implementation.** Expected results:

- `SV-035` parses with Type `baseline`, Status `passing`, and literal `|rel dev|` in Description and Expected.
- `SV-034` is still warned, at `row 33`.
- The new row is `SV-136`, added as one line.
- The next DI on the `KNOWLEDGE.md` copy is `DI-015`.

**Tooling gates.** Run `uv run mypy src/`, `uv run ruff check src/ tests/`, and `uv run ruff format --check src/ tests/`.

## Next-Stage Handoff

- **Fixed:** D1 to D11, I1 to I9, the token boundary, the refusal register R1 to R9, and keeping parser warnings unchanged.
- **Open:**
  - helper and test names (except `_next_id`, `_format_table_row`, `_append_table_row`, and `_write_backlog`, which existing tests import);
  - the exact wording of warnings and refusals, within D9's "says what to change";
  - where new test classes sit within the named test files.
- **De-risk first:** write E1 and E2's WI case as failing tests. Then build in this order:
  1. the splitter, escape, `_insert_table_row`, and `update_validation`;
  2. ID discovery at all eight sites;
  3. the frontmatter reader fixes, then the backlog document writer and its lookups, which is the largest behaviour change;
  4. the remaining E2 cases, the refusal tests, and the full suite.

## Appendix A: Token boundary cases

| Text in the registry file | Counts as | Why |
|---|---|---|
| `MAG-001` | no `G` token | `G` follows a letter |
| `` `SV-034` `` | SV 34 | a backtick is not a letter or digit; code spans count |
| `PR-1` | PR 1 | same number as `PR-001` |
| `SV-034a` | SV 34 | only the digit run must end |
| `SV-034-x` | SV 34 | same |
| `DI-001-DI-014` | DI 1 and DI 14 | a hyphen may precede a token, so a joined range reserves its upper end |
| `X-SV-001` | SV 1 | a hyphen may precede a token; a gap at most |
| `**PR-007**` | PR 7 | E2's decorated-ID fixture |
| `id: WI-002` | WI 2 | frontmatter is scanned like any other text |
| `DI-001 through DI-014` | DI 1 and DI 14 | the archive note is what protects `DI-014` |
| `<!-- SV-900 -->` | not counted | inside an HTML comment |
| `<!-- unclosed SV-900` | SV 900 | an unclosed comment is not stripped, the same as in the parser |

---

**Next Step:** a bounded re-check by the design reviewer (D6, D9, the lookups, the escape cases, the E2 wording), then `/_my_plan`.
