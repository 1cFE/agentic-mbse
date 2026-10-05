# Audit: Escaped Pipes and Registry ID Integrity

**Verdict:** Certified with follow-ups (Certify: zero blockers). Re-checked at `b801fd5`: A1 closed, five advisories remain; the final verdict and follow-up list are in [Re-check](#re-check).
**Audited:** 2026-10-04
**Branch:** pm-registry-integrity
**Commit:** `9357192` (source and tests last changed at `b8bbf8d`; `git diff --stat b8bbf8d..HEAD -- src/ tests/` is empty)
**Base:** `e5bd0db`

---

## The Point

[INHERITED: product-lens.md, from claude/skills/project-structure/SKILL.md] Other artifacts cite registry IDs (`SV-`, `DI-`, `PR-`, `AD-`, `WI-`, `G-`, `AQ-`) by spelling. A record that silently disappears, or an ID minted twice, makes those citations ambiguous.

Before this branch both happened:

- **Reads dropped valid rows.** The table splitter treated `\|` as a cell boundary, so fusion-tea's `SV-035` vanished from the parse.
- **Writes deleted or corrupted records.** `update-validation` wrote the new status into the wrong column and mangled escaped pipes. `add-validation` wrote pipes unescaped. The backlog writer rebuilt `BACKLOG.md` from parsed data, deleting any work item the parser rejected, and erased every item when the YAML was malformed.
- **Allocators counted only parsed records,** so a dropped record's ID was minted again.

The brief's audit question: can a supported registry record still disappear silently, or an ID present in a registry file still be minted twice, through any PM read or write?

## Summary

The implementation delivers all six spec criteria, and every one is pinned by a test that fails when the behaviour regresses. I proved this by breaking the source 23 ways in a scratch copy: every mutation was caught by the tests named for it. Each refusal R1 to R9 has a test that compares every file's bytes before and after. E3 and E4 reproduce at HEAD, the full suite passes 2050, and no base test line was removed.

The answer to the audit question is "no" for every path the spec names. One pre-existing path remains outside it (A1): if a section's commented example table sits above the real table, an add writes inside the comment and the next add mints the same ID. It is not a regression, no template or PM operation produces that layout, and fusion-tea is not exposed. But it is the one remaining way a PM write loses a record silently, so it is the first follow-up.

## Product Judgment

**This is the right piece of work.** The product lens (fallback method, gate CLEAR; see `product-lens.md`) derived the same point independently from the shipped commands and templates. No owner-grade or HARD-grade source is contradicted.

What the lens raised, checked against the code:

- **Dashboard still hides a repeated-key list** (lens DO, smells ii and v). Still true: `parse_backlog` (`parser.py:554-558`) uses the default loader, and `test_default_keeps_last_wins` pins it. The design chose this on purpose (D9: read-only consumers unchanged), and writes now refuse such a file, so nothing is deleted. Advisory A2.
- **`update-validation` refuses a valid row with an inline HTML comment** (lens c). Still true (`operations.py:1450-1463`). Design RC1/R7 chose it. fusion-tea is not exposed: all 134 parsed rows on the real matrix copy update cleanly (probe P2). Advisory A3.
- **Three hand-kept definitions of "the table under a heading"** (lens smell iii). The lens called it weak because "where they differ, the result is a refusal". That is wrong in one case: `_insert_table_row` (`operations.py:422-460`) does not skip HTML comments while the parser and `_raw_table_rows` do, and that difference produces a wrong write. Advisory A1.
- **`close-item` can half-close when `design.md` has no frontmatter.** Unchanged from base and already a recorded design Non-Goal. No new action.

No structural smell rises to a product contradiction. The lens's smell (i), a test that updates only the Registry copy of a row that also appears in Summary and Archive tables, is defensible: it matches the region the parser reads.

## Blockers

None.

## Advisory

Ranked by importance. None blocks certification.

**A1. A table add can still write a record where the parser cannot see it, then mint its ID again.** Closed in-item at `c3f3517`; see Re-check. Pre-existing; the insert loop is byte-identical to base `_append_table_row` (`e5bd0db` `operations.py:229-238`).

- Concern: `_insert_table_row` (`operations.py:422-460`) finds "the table under the heading" on the raw text. If a commented example table sits between the heading and the real table, it takes the commented rows as the table and inserts the new row inside the comment.
- Evidence: probe P1 (`.orchestrate-logs/audit-scratch/audit_probe.py`). `register-intent` and `add-validation` each report success twice, both times minting `G-001` or `SV-001`, and the parser reads zero records afterwards.
- Impact: the user is told "Added", but the record is invisible to every reader, and the next add reuses its ID. This is the falsifier, reached through a layout the templates do not produce (they put the comment after the table). The spec's C3 test and C4 wording do not cover it: C3's evidence is the escape round-trip, and C4 excludes IDs that appear only inside comments.
- What should change: locate the table on comment-blanked text, as `_raw_table_rows` already does with `_strip_html_comments(text, keep_lines=True)`, and insert into the original lines at that index. Add a test with the comment above the real table for SV, PR, G, and AQ.

**A2. The dashboard read path still hides a repeated-key list without a warning.** `parse_backlog` (`parser.py:554-558`) loads with last-wins, so `agentic-mbse status` shows only the second `standalone:` list. Writes refuse the same file (R1), so no record is deleted, but the dashboard misstates what the file holds. What should change: have read-only callers warn, not refuse, on a repeated key.

**A3. `update-validation` refuses a valid row that holds an inline HTML comment.** `operations.py:1450-1463`, pinned by `test_refuses_row_with_inline_comment_and_leaves_file_unchanged`. Base updated such a row correctly. This is the one new refusal on a call that used to succeed without damage. `audit-models.md:33` routes SV status changes only through this command, so the user must move the comment by hand. The message says so, and the file is untouched. What should change: decide whether the rewrite should carry a comment in a non-Status cell through unchanged.

**A4. The closing-delimiter rule changed for every frontmatter reader, not only the backlog writer.** `parse_frontmatter` (`parser.py:301`) now closes only on an unindented `---`. A file whose closing line is ` ---` used to read normally. It now reads as empty with "No closing frontmatter delimiter" (probe P7). This reaches `state.py`, the dashboard, and `close-item`'s rewrite of `spec.md`, `design.md`, and `plan.md` (`operations.py:155`). Design D9 chose it. But the design's Integration Strategy says "`parse_frontmatter` gains only a defaulted keyword", which understates the change. Exposure is low, but fusion-tea's work-item files could not be checked from this sandbox.

**A5. `_write_backlog` keeps a `BacklogData` branch that only tests use.** `operations.py:235-236`. Every production caller passes the loaded document (`:1221`, `:1303`, `:1391`). The branch exists so six base test call sites stay unchanged under the additions-only rule, and the docstring says so. That justification holds. Side effect: the base `TestWriteBacklogRoundTrip` tests (`test_pm_operations.py:269`, `:281`) now exercise only this test branch, not the production write path. Production write-back is covered by the new carry-forward tests and the fusion-tea round trip. What should change: move the typed form into a test helper when existing tests may be edited.

**A6. R7's message misnames one cause.** When a row parses but its Status is not the ninth cell (a custom header), `update-validation` refuses (`operations.py:1439`), which is correct. The message blames a pipe or a comment (`:1443-1445`). What should change: say that Status must be the ninth column.

## Findings Detail

### Plan completion

All phases verified. Every checkbox in Phases 1 to 4 matches the code at HEAD:

- The two strict-xfail markers are gone: `grep -rn xfail tests/` finds nothing.
- Every named test exists and passes.
- The gates meet the parity rule I reran: ruff 118 findings repo-wide, PM-scoped "All checks passed!"; format 78 files, 8 hunks in the four edited files; mypy 91 errors, 0 under `src/agentic_mbse/pm/`.
- The full suite gives 2050 passed, 1 skipped, 33 deselected. That is base 1932 plus the 118 new PM tests.

No placeholder code, debug output, or new TODO in the diff. The two TODOs in `operations.py` (`:1138`, `:1502`) predate this branch.

### Spec conformance

Each criterion is traced to tests that fail when the behaviour regresses. "Killed" means I broke that behaviour in a scratch copy (`.orchestrate-logs/audit-scratch/mutate.py`) and the named tests failed.

| Criterion | Tests that pin it | Regression check |
|---|---|---|
| C1 Escaped pipes | `test_pm_parser.py::TestSplitTableRow` (`test_escaped_pipe_is_content`, `test_escaped_pipe_inside_code_span` for the code span, `test_escaped_backslash_before_pipe_stays_one_cell` pinning `\\|`); `TestParseValidationMatrix::test_escaped_pipe_keeps_columns`; E1 | naive splitter: killed, 14 failures. E4 rerun: PASS, 14 of 14 |
| C2 One escape rule | `TestUpdateValidation::test_escaped_row_changes_only_status`: whole-file equality, only `\| pending \|` becomes `\| passing \|` | unescaped rewrite: killed. One splitter left in `src/` (grep) |
| C3 Round-trip | `test_value_with_pipe_round_trips` in `TestAddValidation` (SV), `TestPromoteRequirement` (PR), `TestRegisterIntent` (G and AQ together) | unescaped writer: killed, 9 failures. Holds on every template layout; see A1 for the commented-table layout |
| C4 No ID minted twice | `TestAddInsight::test_archive_note_reserves_di_014` (DI-001 to DI-011 under a note naming DI-014 gives DI-015); E1; E2's seven `test_mints_above_unparsed_record`; `TestRegistryIds::test_token_boundary` (12 Appendix A rows), `test_skips_html_comments`, `test_templates_reserve_nothing` | parsed-only allocator: killed, 25 failures. Comments counted: killed, 15. Hyphen excluded on the left: killed. Letter allowed on the left: killed |
| C5 No record lost on write | `test_carries_forward_invalid_item` in `TestAddItem`, `TestAddEpic`, `TestCloseItem` (whole-frontmatter equality plus the one edit); E2 WI; malformed YAML refused by `test_refuses_unreadable_frontmatter`, `TestAddEpic::test_refuses_malformed_yaml`, `TestCloseItem::test_refusal_leaves_item_active` | typed-view writer (base behaviour): killed. R1 to R5 below |
| C6 Nothing else changes | E3 rerun at HEAD; 0 deleted test lines; full suite; `TestSplitTableRow::test_unescaped_rows_split_as_before` (C6.3); `TestNextId` unchanged (C6.2); every E2 case asserts a single inserted block, so no other line is re-spelled (C6.1) | E3: five files identical, the matrix gains only `SV-035` and loses only its old Type warning |

**C6.1 also holds on real data.** On copies of fusion-tea's files (probes P2 and P3):

- 134 no-op `update-validation` calls changed zero lines.
- `add-item` changed the frontmatter by exactly one appended mapping.
- `close-item WI-053` changed only that item's `status` and `completed`.

**Known Requirements met.** All seven registries are covered (E2 has one case each). Each format stays native: table rows, heading records, and frontmatter mappings. Reserving an ID does not validate its record: `SV-034` is still warned at `row 33`.

**Non-goals respected.** No duplicate repair, no persistent high-water mark, and no scan of WI directory names.

### Design conformance

The implementation follows D1 to D11 and I1 to I9. The deviations recorded in the plan are each justified and none weakens an invariant:

- R7 also checks that the Status cell matches the parsed record.
- `_backlog_list` treats a null value as absent.
- `_load_backlog` starts from an empty `BacklogData` when the frontmatter has no keys.
- R9 refuses a heading whose only table is in a later section (orchestrator decision).

**Refusal register (brief item 2).** Every refusal test snapshots every file under the project root with `_file_bytes` and asserts equality afterwards. For `close-item` that includes the item directory, so a move would fail the test.

| # | Tests | Regression check |
|---|---|---|
| R1 | `TestAddItem::test_refuses_unreadable_frontmatter` (malformed, no frontmatter, `standalone` twice, `items` twice, indented closer); `TestAddEpic::test_refuses_malformed_yaml`; `TestCloseItem::test_refusal_leaves_item_active` (2); reader: `TestParseFrontmatter::test_unique_keys_rejects_repeat`, `test_indented_dashes_stay_in_block_scalar`; `TestAddItem::test_keeps_items_after_indented_dashes` | accepting warnings, the last-wins loader, and the indented closer: each killed |
| R2 | `test_refuses_non_list_standalone`, `test_refuses_non_list_epic_items`, `TestAddEpic::test_refuses_non_list_epics` | killed |
| R3 | `TestAddItem::test_refuses_duplicate_epic_names`, `TestCloseItem::test_refuses_duplicate_work_item_ids` | first match wins: killed |
| R4 | `TestAddItem::test_refuses_rejected_epic_quoting_warning`, `TestCloseItem::test_refuses_invalid_item_quoting_warning` | killed |
| R5 | `TestAddEpic::test_refuses_name_of_rejected_epic` | duplicate check on parsed epics only: killed |
| R6 | `TestUpdateValidation::test_refuses_duplicate_rows`, `test_commented_example_rows_are_not_found`, `test_ignores_rows_outside_registry_section` | first match, commented candidates, and whole-file candidates: each killed |
| R7 | `test_refuses_unparsed_row`, `test_refuses_comment_in_status_cell`, `test_refuses_row_with_inline_comment_and_leaves_file_unchanged` | removing the check: killed |
| R8 | `TestEscapeTableCell::test_refuses_line_breaks_and_comment_markers`, `TestAddValidation::test_refuses_comment_marker`, `TestPromoteRequirement::test_refuses_line_break`, `TestRegisterIntent::test_refused_second_goal_writes_nothing` | escape accepting markers: killed, 8 failures |
| R9 | `test_missing_section_refuses` (no heading, no table, table only in a later section) in `TestPromoteRequirement` and `TestAddValidation`; `TestRegisterIntent::test_missing_questions_section_writes_nothing` | later-section insert (base): killed |

I7 (refuse before the first write) is also pinned. Making `close-item` rewrite `spec.md` before validating was caught by 4 tests. Making `register-intent` write after each row was caught by 1.

**The parser and the update path agree on the region.** `_raw_table_rows` (`operations.py:472-491`) starts at the same heading as the parser (`parser.py:121`) and ends at or after the parser's end. So every row the parser reads is a candidate, and R6/R7 cannot be bypassed by a row the parser reads but the lookup misses.

**Original defect probes rerun at HEAD.** All are closed or refused:

- `spec-review-scratch/probe.py`: probe 1 mints `SV-036`. Probe 2 lands `passing` in Status with `\|rel dev\|` intact. Probe 3 mints `WI-003` and keeps `WI-002`. Probe 5 refuses and keeps `WI-001`. Probe 4 is unchanged: `register-decision` still refuses on fusion-tea until `## Key Decisions` exists.
- `design-review-scratch/comment_value_probe.py` and `recheck_d4_probe.py`: comment-marker values refused, comment-bearing rows refused.
- `loss_paths_probe.py` sections 1 and 3 exercise rejected design alternatives, not shipped code. The shipped boundary gives `DI-001-DI-014` → DI 1 and 14 (probe P5).

**Design-text note.** The Integration Strategy's "no outward changes" omits the read-side delimiter change (A4).

### Code integrity

- **One of each.** `_split_table_row` is the only pipe splitter in `src/`. `_id_pattern` (`operations.py:66-74`) is the only regex that numbers IDs; the parser's per-prefix regexes only validate. The two `WI-{n:03d}` lines (`state.py:162`, `operations.py:1328`) are pre-existing input normalization, not allocation.
- **No dead code or leftovers.** Every new helper has a caller. `_append_table_row` is still used by `promote_requirement` and `add_validation`.
- **Failure honesty is good.** No broad `except`. Each `except ValueError` wraps a named raiser (`_format_table_row`, `_insert_table_row`, `_load_backlog`, `_backlog_target`, `_backlog_list`). `_registry_ids` catches only `FileNotFoundError`. `_load_backlog` refuses on any reader warning, and today every warning `parse_frontmatter` emits is a genuine short read (`parser.py:286-322`). The docstring warns that a future benign warning would start refusing writes.
- **`_UniqueKeyLoader` is sound.** It records each mapping's own keys on first flatten (`parser.py:244-249`) and compares them after construction (`:251-264`). The merge override and the chained-merge cases are tested.
- **Duplicated section logic** (A1) and the test-only `BacklogData` branch (A5) are the two structural notes.

**Additions-only (brief item 5).** Holds:

- `git diff --stat e5bd0db..HEAD -- tests/` shows 1229 insertions and 0 deletions, in two files. `conftest.py` is unchanged.
- Hunks land at class ends or after helpers. I checked the ones beside `_setup_validation_matrix` and `_setup_backlog`, which add new helpers after the existing bodies.
- No existing test is weakened. All 1932 base tests still pass.

**Behaviour a fusion-tea user will notice (brief item 6).** Exit codes and stdout success messages are unchanged. Warnings go to stderr only (`cli/pm_cli.py:39-42`).

- **New stderr lines.** Each allocating command prints one reservation warning per unparsed number:
  - `add-insight`: `DI-014`.
  - `add-validation`: `SV-034`.
  - `promote-requirement`: 6, alongside its refusal.

  `update-validation` now also prints the parse warnings on every call (on fusion-tea, `SV-034`'s Type warning).
- **Tracebacks become clean refusals.** `promote-requirement` and `register-intent` on fusion-tea, which lacks those sections, used to raise `ValueError`. They now exit 1 with "Section heading … not found", and the file is unchanged (probe P4).
- **New refusals on calls that used to succeed.** Each replaces a silent loss or a wrong target:
  - R1 to R5 on backlogs that were being deleted from.
  - R6 on duplicate or commented SV rows.
  - R7 on raw-pipe rows, which used to be corrupted.
  - R8 on values that wrote unreadable rows.
  - R9 on a heading with no table, which used to write into a later section.

  The one exception is A3. fusion-tea's real matrix, backlog, and knowledge copies hit none of these (probes P2 to P4).
- **Message changes.** `close-item` on an invalid item now says "present but not a valid record" instead of "not found". On malformed YAML it quotes the reader's warning. The asserted fragments "already exists", "not found", and "BACKLOG.md" are kept.
- **Backlog body.** A rejected work item now stays in the frontmatter but is absent from the rendered dashboard body. Before, it was deleted from both. fusion-tea's frontmatter round-trips byte-identical.
- **Frontmatter reads.** See A4.

---

## Certification

**Checked and verified:**

- Reran G1 to G4 and the full suite, with the counts above.
- Reran E4 at HEAD: PASS, 14 of 14, minting `SV-136` and `DI-015`.
- Reran the E3 snapshot at HEAD and compared it with `baseline.json`: identical except `SV-035` added and its warning removed.
- Reran the spec-review and design-review probes.
- Ran 23 source mutations covering C1 to C6, R1 to R9, I7, D6, and D7. All were caught.
- Ran eight new probes (P1 to P8), including every PM write against copies of fusion-tea's real files.
- Confirmed no xfail remains and no base test line was removed.
- Read every changed source line and the key new tests (E1, E2's helper, the WI carry-forward tests, every refusal test's assertions).
- Appended the audit product-lens block to `product-lens.md`.

**Marked:** nothing. Per the brief, the orchestrator updates `plan.md`, `spec.md`, the backlog, and `CURRENT_WORK.md`. My recommendation:

- All plan phases (1, 2, 3a, 3b, 4) are verified complete.
- Spec criteria C1 to C6 are verified met. (The C3 caveat from A1 is lifted at re-check.)

**Follow-ups:** see [Re-check](#re-check) for the final list.

**Not checked:**

- fusion-tea's live repo and its work-item `spec.md`, `design.md`, and `plan.md` frontmatter (outside the sandbox). The orchestrator has since scanned them for A4; see Re-check.
- The CLI end to end: I called the operations directly and read the CLI's print path (`cli/pm_cli.py:39-91`), but did not run `agentic-mbse pm …` commands.
- CRLF files. `update-validation` and the backlog writer rewrite line endings to LF, as at base.
- Comment-marker values in heading registries and backlog fields (a design Non-Goal).
- Concurrency between two PM writes.
- Every layout variant of the commented-table case beyond probe P1.
- The product-lens instruction file itself. The lens ran on the fallback method, as at design review.

---

## Re-check

**Re-checked:** 2026-10-04 at `b801fd5` (source and tests last changed at `c3f3517`, the A1 fix). Bounded to the A1 fix and to whether anything else moved.

**Final verdict: Certified with follow-ups.** Zero blockers. A1 is closed, and advisories A2 to A6 stand as written above.

**What changed.** `_insert_table_row` (`operations.py:422-470`) now finds the heading and the table on comment-blanked text, so a commented table is never the target. After inserting, it re-blanks the text and refuses if the new row reads as blank, which means it landed inside a comment. Design D9's R9 row is amended to match. Six tests were added.

**(1) My A1 reproduction is fixed.** I reran probe P1 (`.orchestrate-logs/audit-scratch/audit_probe.py`) with a commented example table above the real one:

- `register-intent` mints `G-001` then `G-002`, and `add-validation` mints `SV-001` then `SV-002`.
- Both rows land in the real table, the parser reads them back, and the commented example is unchanged.
- A table that exists only inside a comment refuses, and so does a row that would fall inside a comment opening on the table's last line. In both cases the file is unchanged. The tests are `test_missing_section_refuses[table only in a comment]` and `test_refuses_row_that_would_land_in_a_comment`, and both compare every file's bytes.
- Probes P2 to P8 give the same results as at audit.

**(2) Removing either new piece makes tests fail.** Both mutations were added to `mutate.py`:

- Deleting the post-insert check fails `TestAddValidation::test_refuses_row_that_would_land_in_a_comment`.
- Reverting the search to raw text fails all four `test_skips_commented_table_above_real_table` cases (SV, PR, G, AQ).
- Under that second mutation, `test_missing_section_refuses[table only in a comment]` still passes. The post-insert check catches the same case as a backstop, so the file stays unchanged. Only the message differs: it says the comment opens on line 5 instead of saying no table was found (`.orchestrate-logs/audit-scratch/a1_backstop.py`). No row can be lost; the test just does not pin which message the user sees.
- The other 23 mutations from the audit are all still caught.

**Why the post-insert check is exact.** The row cannot hold a comment marker (R8 refuses one first), and inserting a marker-free line cannot change how existing comments pair. So the check refuses exactly when the row lands inside a comment, and never otherwise.

**(3) Nothing else moved.**

- Full suite: 2056 passed, 1 skipped, 33 deselected. That is the audit's 2050 plus the 6 new tests.
- Gates at parity: ruff 118 repo-wide, PM-scoped "All checks passed!"; format 78 files, 8 hunks in the four edited files; mypy 91 errors, 0 under `src/agentic_mbse/pm/`.
- No base test line removed: `git diff e5bd0db..HEAD -- tests/` is 1337 insertions and 0 deletions. The one line the fix edited (the `ids=` list of `test_missing_section_refuses`) was added on this branch, not at base.
- E4 rerun: PASS, 14 of 14, minting `SV-136` and `DI-015`. E3 rerun: identical to baseline except `SV-035` added and its warning removed.

**A4's exposure is answered, as reported by the orchestrator.** `acceptance-evidence.md` records a scan of 1138 fusion-tea frontmatter files with no indented closing `---`. I could not verify this myself, because fusion-tea is outside this sandbox. On that evidence, the stricter delimiter rule changes nothing on real data. A4 stays only as a note that the design's Integration Strategy understates the read-side change.

**Recommendation for tracking.** All plan phases are complete, including the post-audit A1 fix. Spec criteria C1 to C6 are met with no caveat.

**Remaining follow-ups (backlog-ready):**

1. `PM-DASHBOARD-REPEATED-KEY`: read-only `parse_backlog` should warn on a repeated frontmatter key, so `status` stops silently showing only the last list (A2).
2. `PM-UPDATE-VALIDATION-COMMENT`: decide whether `update-validation` should carry an inline HTML comment in a non-Status cell through unchanged instead of refusing the row (A3).
3. `PM-WRITE-BACKLOG-TYPED-FORM`: move `_write_backlog`'s `BacklogData` form into a test helper and point `TestWriteBacklogRoundTrip` at the document write path (A5).
4. `PM-R7-MESSAGE`: when an SV row parses but Status is not its ninth cell, R7's message should say so instead of blaming pipes or comments (A6).

**Not checked in this pass:**

- Anything outside the A1 fix beyond the reruns listed above.
- The orchestrator's 1138-file fusion-tea scan, which is outside the sandbox.
- Comment layouts beyond the ones the six tests and probe P1 cover.
