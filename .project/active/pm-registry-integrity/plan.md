# Implementation Plan: Escaped Pipes and Registry ID Integrity

**Status:** In Progress (Phases 1, 2, 3a, and 3b complete)
**Created:** 2026-10-04
**Last Updated:** 2026-10-04
**Branch:** pm-registry-integrity
**Base commit:** `e5bd0db`. Every `file:line` below is as of this commit, and line numbers shift as phases land.
**Backlog Item:** PM-MATRIX-ESCAPED-PIPE

## Source Documents

- **Spec (contract):** [spec.md](spec.md). Success criteria C1 to C6, acceptance evidence E1 to E4.
- **Design:** [design.md](design.md). See it for components, signatures, decisions D1 to D11, invariants I1 to I9, refusals R1 to R9, and the token cases in Appendix A.
- **Design review and re-check:** [design-review.md](design-review.md). RC1 is applied in `e5bd0db`.
- **Brief:** [briefs/plan.md](briefs/plan.md).

## The Point

[INHERITED: product-lens.md, from claude/skills/project-structure/SKILL.md] Other artifacts cite registry IDs (`SV-`, `DI-`, `PR-`, `AD-`, `WI-`, `G-`, `AQ-`) by spelling. A record that silently disappears, or an ID minted twice, makes those citations ambiguous. The product lens's falsifier: "a supported registry entry disappears silently or an extant registry ID is reused."

Both happen today. This was reproduced at `e5bd0db` with `.orchestrate-logs/spec-review-scratch/probe.py`:

- **Reads drop valid rows.** The table splitter treats `\|` as a cell boundary (`parser.py:109`). On fusion-tea's matrix this drops `SV-035`.
- **Writes corrupt or delete records.**
  - `update_validation` writes the new status into the Source column and rewrites `\|rel dev\|` as `\ | rel dev\ |` (`operations.py:1148`).
  - `add_validation` writes pipes unescaped (`operations.py:194`).
  - The backlog writer rebuilds `BACKLOG.md` from parsed data, so it deletes a work item with `status: in-progress` (`operations.py:155`).
- **Allocators count only parsed records** (`operations.py:58`), so a dropped record's ID is minted again. The three-record matrix gets a second `SV-034`, and the backlog above gets a second `WI-002`.

[AGENT, from the brief] The plan's job: implement the design in an order where every phase leaves the PM suite green, and each defect is proven closed by a test that was red first.

## Legend

- **C1 to C6** are the spec's Success Criteria in order: C1 escaped pipes, C2 one escape rule, C3 round-trip, C4 no ID minted twice, C5 no record lost on write, C6 nothing else changes.
- **E1 to E4** are the spec's acceptance evidence. **D**, **I**, and **R** numbers are the design's decisions, invariants, and refusals.
- The bracket at the end of each checklist line names what that item serves.

## Implementation Strategy

**Phasing rationale.** The phases follow the design's three seams ([design.md#architecture](design.md#architecture)): table cells, ID allocation, and backlog writes.

- **Cells come first.** E1's parse half and the round-trip both depend on the splitter. Phase 2's ID scan should also run on files the parser already reads correctly.
- **ID discovery comes second.** It is small and pure, and it closes ID reuse in six registries at once.
- **The backlog write-back comes last.** It is the largest behaviour change ([design.md#next-stage-handoff](design.md#next-stage-handoff)), and it reuses `_single_match` from Phase 3a.
- **Part 3 is split into two phases.** Phase 3a covers table lookups and refusals; Phase 3b covers the backlog write-back. Each fits in one session and can be reviewed on its own.

**Critical path.** Splitter and escape (P1) → `_registry_ids` at all eight allocation sites (P2) → `_single_match` and the table refusals (P3a) → frontmatter reader and backlog document writer (P3b) → acceptance (P4) → the orchestrator's E3 snapshot and E4.

**First proof point.** First, the three red runs at the start of Phase 1. Then `test_escaped_row_changes_only_status` goes green at the end of Phase 1. That proves the one splitter and escape fix a write path, not only a read.

**Red-first protocol** [brief]:

- Before any `src/` edit, write the three red-first tests, run them against the base, and paste the output into the Implementation Record:
  - `TestAddValidation::test_e1_three_record_reproduction` (E1). Phases 1 and 2 fix it together.
  - `TestUpdateValidation::test_escaped_row_changes_only_status` (C2). Phase 1 fixes it.
  - `TestAddInsight::test_archive_note_reserves_di_014` (C4). Phase 2 fixes it.
- After the red run, mark E1 and the archive-note test with `@pytest.mark.xfail(strict=True, reason="fixed in Phase 2")`.
  - While a strict-xfail test fails, the suite stays green.
  - When Phase 2 makes it pass, the suite turns red until the marker is removed, so the marker cannot be forgotten.
- **Why E1 stays red after Phase 1.** The splitter makes the escaped `SV-034` parse. But the allocator still counts only parsed IDs, so it mints `SV-035`, a duplicate of the malformed row. Only Phase 2's scan reserves 35.

**Phase gates.** Every phase ends with these four, named in its checklist. The full suite (`uv run pytest tests/`) runs in Phase 4.

- **G1** `uv run pytest tests/test_pm_*.py`
- **G2** `uv run ruff check src/ tests/`
- **G3** `uv run ruff format --check src/ tests/`
- **G4** `uv run mypy src/`

> **Surfaced, not resolved: G2 to G4 fail on the untouched base.** The brief assumes they pass, but at `e5bd0db` none of them does:
>
> - `ruff check src/ tests/` reports 118 findings.
> - `ruff format --check src/ tests/` would reformat 78 files.
> - `mypy src/` reports 91 errors in 19 files.
>
> None of the ruff-check findings or mypy errors are in the files this item edits. Three of the four edited files do carry 8 existing formatting hunks: `operations.py`, `test_pm_operations.py`, and `test_pm_parser.py`. Fixing the base is out of scope, so no phase can pass these gates literally. **[AGENT] (orchestrator, 2026-10-04) Decision: the parity rule below stands.** It matches the repo's own pre-PR gate (commit `81b478a`, "parity rule, not green rule"), and a formatting-only commit would touch 78 files and muddy the diff. Each gate passes when:
>
> - **G2:** the repo-wide count is no higher than 118, and `uv run ruff check src/agentic_mbse/pm/ tests/test_pm_operations.py tests/test_pm_parser.py` prints "All checks passed!".
> - **G3:** the repo-wide count is no higher than 78. Also, `uv run ruff format --diff src/agentic_mbse/pm/parser.py src/agentic_mbse/pm/operations.py tests/test_pm_parser.py tests/test_pm_operations.py | grep -c '^@@'` still prints 8, which means all new code is formatted.
> - **G4:** `uv run mypy src/` reports no more than 91 errors, and none of them are under `src/agentic_mbse/pm/`.
>
> Rejected alternative: a formatting-only first commit on the four edited files. It would change existing test lines and move the additions-only baseline; not worth it for a parity gate.

**Ground rules:**

- **No new module** (D11). New helpers go where [design.md#component-overview](design.md#component-overview) puts them.
- **Existing tests stay unchanged**, in particular `TestNextId` and `TestAppendTableRow` ([design.md#implementation-notes](design.md#implementation-notes)). Add new tests beside them.
- **Test placement** [brief]:
  - Splitter, escape, and frontmatter-reader tests go in `tests/test_pm_parser.py`.
  - Allocation, refusal, and `TestRegistryIds` tests go in `tests/test_pm_operations.py`.
  - `TestRegistryIds` sits beside `TestNextId`, because `_registry_ids` lives beside `_next_id` in `operations.py`. No new test file.
- **Match the test file's idioms.** Import the operation inside the test, build projects with the `_setup_*` helpers, and use `tmp_path`.
- **Every refusal test checks that no file changed:** it compares every file's bytes before and after (design.md, Validation Approach).
- **Keep the existing message fragments that tests assert:**
  - "already exists": `add-epic` duplicate, `test_pm_operations.py:1057`
  - "not found": `add-item` with a missing epic, `:948`
  - "BACKLOG.md": `close-item` on an item missing from the backlog, `:1187`
- **E3's snapshot and E4 belong to the orchestrator.** Do not run or edit `.orchestrate-logs/ft-snapshot/e4_check.py` or `snapshot_parse.py`. You may read the fusion-tea copies in that folder to understand real data.

**Choices this plan makes inside the brief** (recorded for review):

1. **Part 3 is split into Phases 3a and 3b.** Content and order are the same as the brief's part (3). It just takes two sessions instead of one.
2. **Phase 1 turns `update_validation`'s formatting `ValueError` into a refusal.** That is R7's comment-marker clause (RC1). Phase 1 switches this caller onto an escape that raises (D3). Without the refusal, a comment-bearing row would crash with a traceback between Phase 1 and Phase 3a. The rest of R7, and R6, stay in Phase 3a with `_single_match`.
3. **Phase 1 makes `register_intent` format every row before its first append.** So an R8 refusal on a later goal writes nothing (I7). The single in-memory write (D10, m2) stays in Phase 3a.
4. **Each E2 case is written in the phase whose fix makes it pass.** SV, PR, G, AQ, DI, and AD are written in Phase 2; WI in Phase 3b. Phase 4 runs all seven together. Writing them only in Phase 4 would duplicate Phase 2's per-site allocation tests.

---

## Phase 1: Table cells, one inverse pair

### Goal

Every row reader splits with `_split_table_row`. Every row writer formats through `_escape_table_cell`. So `\|` is content everywhere, and a value containing `|` round-trips (D1 to D3). This phase delivers C1 and C3, and C2 except the lookup scoping that Phase 3a finishes.

### Assumption Under Test

Swapping one splitter and escape pair into the two callers has two effects, and only two:

- No parsed value changes for a row without `\|` (I2).
- The `update-validation` corruption is fixed without touching any other cell.

### Test Stencil (Write This First)

```python
# tests/test_pm_operations.py, module level; rows copied from .orchestrate-logs/spec-review-scratch/probe.py
_E1_ROWS = {
    "valid": "| SV-033 | plain | baseline | test | x | 1e-6 | s | t | passing |",
    "escaped": "| SV-034 | bar (\\|rel dev\\| <= 1e-6) | baseline | test | x | 1e-6 | s | t | passing |",
    "malformed": "| SV-035 | bar (|rel dev| <= 1e-6) | baseline | test | x | 1e-6 | s | t | passing |",
}

class TestAddValidation:
    @pytest.mark.xfail(strict=True, reason="fixed in Phase 2")  # added after the red run
    def test_e1_three_record_reproduction(self, tmp_path):
        from agentic_mbse.pm.operations import add_validation

        vm = _write_matrix(tmp_path, list(_E1_ROWS.values()))
        parsed = parse_validation_matrix(vm)
        assert [e.id for e in parsed.data] == ["SV-033", "SV-034"]
        assert parsed.data[1].description == "bar (|rel dev| <= 1e-6)"
        assert any(w.location == "row 2" for w in parsed.warnings)  # malformed SV-035 stays warned
        result = add_validation(
            tmp_path, description="new", type="baseline", mechanism="test", expected="e", tolerance="t"
        )
        assert result.ids_assigned["SV"] == "SV-036"

class TestUpdateValidation:
    def test_escaped_row_changes_only_status(self, tmp_path):
        from agentic_mbse.pm.operations import update_validation

        vm = _write_matrix(tmp_path, [_E1_ROWS["escaped"].replace("passing", "pending")])
        before = vm.read_text(encoding="utf-8")
        assert update_validation(tmp_path, sv_id="SV-034", status="passing").success
        assert vm.read_text(encoding="utf-8") == before.replace("| pending |", "| passing |")
```

`_write_matrix(root, rows)` writes `modeling_project/VALIDATION_MATRIX.md`: a `## Verification Registry` heading, the nine-column header and separator, then one line per row. It returns the path.

### Changes Required

**See design.md for:** the splitter and escape algorithm ([Implementation Notes](design.md#implementation-notes)), D1 to D4, I1 to I3, and the escape and splitter cases (Validation Approach).

**Step 0. Red runs on the base, before any `src/` edit** [brief]

- [x] Add the `_E1_ROWS` and `_write_matrix` helpers to `tests/test_pm_operations.py` [E1]
- [x] Write `TestAddValidation::test_e1_three_record_reproduction` [E1, C1, C4]
- [x] Write `TestUpdateValidation::test_escaped_row_changes_only_status` [C2]
- [x] Write `TestAddInsight::test_archive_note_reserves_di_014`; its stencil is in Phase 2 [C4]
- [x] Run `uv run pytest tests/test_pm_operations.py -v -k "e1_three_record or escaped_row_changes_only_status or archive_note_reserves"`. All three must fail. Paste the failure lines into the Implementation Record [brief]
- [x] Mark E1 and the archive-note test `xfail(strict=True, reason="fixed in Phase 2")` [brief]

What each red run should show at the base:

- **E1** fails at the parsed-IDs assert, because only `SV-033` parses.
- **The escaped-row test** fails because Status stays `pending` and the Source cell becomes `passing`.
- **The archive-note test** fails because it mints `DI-012`.

**Tests (write before the code)**

- [x] `test_pm_parser.py::TestSplitTableRow`: the five splitter cases from design.md's Validation Approach, including `\\|`, which reads as `\|` [D1, D2, C1]
- [x] `TestSplitTableRow::test_unescaped_rows_split_as_before`: rows without backslash-pipe split exactly as today's three-line split does [I2, C6]
- [x] `test_pm_parser.py::TestEscapeTableCell`: `a|b`, `a\|b`, `\\|`, and a trailing `\` survive escape-then-split. `\n`, `\r`, `<!--`, and `-->` raise `ValueError` [D3, I1, I3, R8]
- [x] `test_pm_parser.py::TestParseValidationMatrix::test_escaped_pipe_keeps_columns`: Description holds `|rel dev|`, and Type stays `baseline` [C1]
- [x] `TestFormatTableRow::test_escapes_pipes` [D3]
- [x] `test_value_with_pipe_round_trips` in `TestAddValidation`, `TestPromoteRequirement` (pipe in `requirement`), and `TestRegisterIntent` (goal and question) [C3]
- [x] `TestAddValidation::test_refuses_comment_marker` and `TestPromoteRequirement::test_refuses_line_break`: each refuses, and the file is unchanged [R8, I7]
- [x] `TestRegisterIntent::test_refused_second_goal_writes_nothing`: the second goal holds `<!--`, and `OVERVIEW.md` is unchanged [R8, I7]
- [x] `TestUpdateValidation::test_refuses_row_with_inline_comment_and_leaves_file_unchanged` [RC1, R7]

**Code**

- [x] `parser.py`: add `_split_table_row` and `_escape_table_cell` beside `_parse_markdown_table` [D1, D2, D3]
- [x] `parser.py:109-114`: `_parse_markdown_table` splits header and data rows with `_split_table_row` [D1]
- [x] `operations.py:19`: import `_split_table_row` and `_escape_table_cell` from `parser.py` [D11]
- [x] `operations.py:194`: `_format_table_row` escapes every cell [D3]
- [x] `operations.py:1148-1158`: `update_validation` splits the original line with `_split_table_row` and writes it back with `_format_table_row`. A `ValueError` from formatting becomes an R7 refusal ("the row holds an HTML comment marker; edit it by hand"), and the file is untouched [D4, RC1]
- [x] `operations.py:395-404` and `:517-530`: `promote_requirement` and `add_validation` format the row inside a `try`. A `ValueError` becomes a refusal that names the marker and the value [R8]
- [x] `operations.py:748-798`: `register_intent` first validates, mints, and formats every goal and question row, then appends them. A `ValueError` refuses before the first append [R8, I7]

### Validation

**Automated:**

- [x] G1 `uv run pytest tests/test_pm_*.py`: all pass, and E1 and the archive-note test report XFAIL
- [x] G2 `uv run ruff check src/ tests/` (pass rule above)
- [x] G3 `uv run ruff format --check src/ tests/` (pass rule above)
- [x] G4 `uv run mypy src/` (pass rule above)

**Manual:**

- [x] In a scratch project (see Environment), run `add-validation` with a description containing `a | b`, then `update-validation --status passing SV-001`. Expect: the file holds `a \| b`, the row parses back as `a | b`, and Status is `passing`.

**What We Know Works After This Phase:**

- `\|` reads as a literal pipe in every table registry. Rows without it parse exactly as before.
- Every table add writes a pipe that reads back. A value no row can carry is refused.
- `update-validation` changes only the Status cell on an escaped row.
- **Not yet:**
  - Allocation still counts only parsed IDs, so E1 is still XFAIL.
  - `update-validation` still takes the first matching row anywhere in the file (fixed in Phase 3a).

---

## Phase 2: ID discovery, one path for all seven prefixes

### Goal

Every allocator counts every same-prefix ID its registry file names outside HTML comments (D5, D6), and reports an ID that is reserved but not parsed (D7). This closes C4 for all seven prefixes. WI's write side still deletes invalid items until Phase 3b.

### Assumption Under Test

The token scan reserves archive-note IDs and unparsed IDs. It does not move the first ID minted from any shipped template (B2).

This was checked at the base with `.orchestrate-logs/plan-scratch/template_tokens.py`: no registry template holds an ID token outside an HTML comment. The existing first-ID tests guard it too (`test_pm_operations.py:388`, `:497`, `:538`, `:577`, `:913`).

### Test Stencil (Write This First)

```python
class TestAddInsight:
    def test_archive_note_reserves_di_014(self, tmp_path):  # written in Phase 1 Step 0
        from agentic_mbse.pm.operations import add_insight

        records = "\n".join(_format_insight_entry(_insight(f"DI-{n:03d}")) for n in range(1, 12))
        note = "Previous entries (DI-001 through DI-014) archived.\n\n"
        _write_knowledge(tmp_path, "# Domain Knowledge\n\n" + note + records)
        result = add_insight(
            tmp_path, title="t", source="s", context="c", model_implications="m", analysis_implications="a"
        )
        assert result.ids_assigned["DI"] == "DI-015"

class TestRegistryIds:
    @pytest.mark.parametrize(("text", "prefix", "numbers"), _APPENDIX_A)  # every row of Appendix A
    def test_token_boundary(self, tmp_path, text, prefix, numbers):
        path = tmp_path / "REGISTRY.md"
        path.write_text(text + "\n", encoding="utf-8")
        found = _registry_ids(path, prefix, []).data
        assert sorted({int(t.split("-")[1]) for t in found}) == numbers
```

Shared E2 helper. It follows design.md's "E2's 'exactly the one new record'":

```python
def _assert_one_record_added(before: str, after: str, new_id: str, *, table: bool) -> None:
    a, b = before.splitlines(), after.splitlines()
    ops = [op for op in difflib.SequenceMatcher(None, a, b).get_opcodes() if op[0] != "equal"]
    assert len(ops) == 1 and ops[0][0] == "insert"  # one contiguous block of added lines
    added = b[ops[0][3] : ops[0][4]]
    assert sum(new_id in line for line in added) == 1
    if table:
        assert len([line for line in added if line.strip()]) == 1  # one row; the rest are blank separators
```

### Changes Required

**See design.md for:** D5 to D7, I4, I5, Appendix A, and the Architecture table of which prefix lives in which file.

**Tests**

- [x] `TestRegistryIds::test_token_boundary`, parametrized over every row of design.md's Appendix A [D6, C4]
- [x] `TestRegistryIds`: tokens inside HTML comments do not count [D5, C4]
- [x] `TestRegistryIds`: one warning per distinct unparsed number, with its first spelling as the location [D7]
- [x] `TestRegistryIds`: a parsed `PR-1` covers a `PR-001` mention [D7]
- [x] `TestRegistryIds`: a missing file returns the parsed IDs and no warning [D5]
- [x] Module helper `_assert_one_record_added` [E2]
- [x] E2, SV: `TestAddValidation::test_mints_above_unparsed_record`, where the dropped row has an invalid Status [E2, C4]
- [x] E2, PR: `TestPromoteRequirement::test_mints_above_unparsed_record`, where the dropped row has a `**PR-00N**` ID cell [E2, C4]
- [x] E2, G and AQ: `TestRegisterIntent::test_mints_above_unparsed_record`, parametrized over G and AQ with decorated ID cells [E2, C4]
- [x] E2, DI: `TestAddInsight::test_mints_above_unparsed_record`, where the dropped record has an invalid Status [E2, C4]
- [x] E2, AD: `TestRegisterDecision::test_mints_above_unparsed_record`, where the dropped record has an invalid Status [E2, C4]
- [x] `TestApproveResearch::test_mints_above_archive_note`: two insights mint `DI-015` and `DI-016`, because the running list starts from the scan [D5, C4]
- [x] `TestRegisterIntent::test_multiple_goals_mint_above_unparsed`: the running list for G [D5, C4]
- [x] `TestAddItem::test_mints_above_invalid_item`: an `in-progress` `WI-002` makes it mint `WI-003`. This checks the ID only; the write side is fixed in Phase 3b [C4]
- [x] `TestAddValidation::test_reports_reserved_id_after_parse_warnings`: the parse warnings come first, then one reservation warning naming `SV-035` [D7]

**Code**

- [x] `operations.py`, beside `_next_id`: add `_id_pattern(prefix)` with the D6 boundary, and `_registry_ids(path, prefix, parsed_ids)` returning `ParseResult[list[str]]` [D5, D6, D7]
- [x] `operations.py:58-70`: `_next_id` matches with `_id_pattern(prefix).fullmatch`. Its signature and padding are unchanged [D5, I5]
- [x] `add_insight` `:310-312`: feed `_next_id` from `_registry_ids`, with its warnings after the parse warnings [D5, D7, I4]
- [x] `promote_requirement` `:391-393`: same [D5, D7, I4]
- [x] `register_decision` `:428-430`: same [D5, D7, I4]
- [x] `add_validation` `:513-515`: same [D5, D7, I4]
- [x] `approve_research` `:672-678`: the running list starts from `_registry_ids` [D5, D7, I4]
- [x] `register_intent` G and AQ `:742-743`: both running lists start from `_registry_ids` [D5, D7, I4]
- [x] `add_item` `:966-974`: same [D5, D7, I4]
- [x] Remove the two strict-xfail markers once they report XPASS [brief]

### Validation

**Automated:**

- [x] G1 `uv run pytest tests/test_pm_*.py`: all pass, with no XFAIL left
- [x] G2 `uv run ruff check src/ tests/`
- [x] G3 `uv run ruff format --check src/ tests/`
- [x] G4 `uv run mypy src/`

**Manual:**

- [x] In a scratch project holding the E1 matrix, run `add-validation` through the CLI. Expect `SV-036`, with the reservation warning for `SV-035` printed on stderr.

**What We Know Works After This Phase:**

- No allocator mints an ID its registry file names, for any of the seven prefixes. E1 and the archive-note test are green.
- Templates still mint `-001` first.
- **Not yet:** the backlog writer still deletes invalid work items (fixed in Phase 3b).

---

## Phase 3a: Table lookups and refusals

### Goal

A write that targets or inserts into a table now finds exactly one place, or refuses before writing:

- `_single_match` is the one "exactly one" rule (M1, I9).
- `update_validation` picks from candidate rows (D4, R6, R7).
- Table inserts go through `_insert_table_row`, and `register_intent` writes once (D10, m2, R9).

### Assumption Under Test

`update_validation` will look only inside the `## Verification Registry` section, with HTML comments blanked. The existing happy path must keep working on the template, whose commented example rows include `SV-001` (design-review re-check, call 3). If the blanking were wrong, R6 would refuse the existing `TestUpdateValidation::test_happy_path`.

### Test Stencil (Write This First)

```python
class TestUpdateValidation:
    def test_ignores_commented_example_rows(self, tmp_path):
        from agentic_mbse.pm.operations import add_validation, update_validation

        root = _setup_validation_matrix(tmp_path)  # template: example SV-001 and SV-002 rows inside <!-- -->
        add_validation(root, description="real", type="baseline", mechanism="test", expected="x", tolerance="t")
        assert update_validation(root, sv_id="SV-001", status="passing").success

    def test_refuses_duplicate_rows(self, tmp_path):
        from agentic_mbse.pm.operations import update_validation

        vm = _write_matrix(tmp_path, [_E1_ROWS["valid"], _E1_ROWS["valid"].replace("plain", "copy")])
        before = vm.read_text(encoding="utf-8")
        result = update_validation(tmp_path, sv_id="SV-033", status="failing")
        assert not result.success
        assert vm.read_text(encoding="utf-8") == before
```

### Changes Required

**See design.md for:** D4 (candidate rows, the write rule, RC1), D9 (lookups, the R6, R7, and R9 rows), and D10.

**Tests**

- [x] `test_pm_parser.py`: `_strip_html_comments(text, keep_lines=True)` blanks each comment but keeps the line count [D4]
- [x] `TestSingleMatch` in `test_pm_operations.py`: returns the single pair. With no match, or with several, it raises a `ValueError` naming every location [D9, I9]
- [x] `TestUpdateValidation::test_refuses_duplicate_rows`: the refusal names every matching line [R6, I9]
- [x] `TestUpdateValidation::test_ignores_commented_example_rows` [D4, R6]
- [x] `TestUpdateValidation::test_ignores_rows_outside_registry_section`: an `SV-` row under another heading is not a candidate [D4]
- [x] `TestUpdateValidation::test_refuses_unparsed_row`: a row with raw pipes. The message says the pipe must be written as backslash-pipe, by hand [R7]
- [x] `TestRegisterIntent::test_missing_questions_section_writes_nothing` [R9, D10, m2]
- [x] `TestPromoteRequirement::test_missing_section_refuses` and `TestAddValidation::test_missing_section_refuses` [R9, I7]
- [x] `test_missing_section_refuses[table only in a later section]` in both classes: the heading is present with no table under it, and a later `## ` section has a table. The operation refuses, names the heading, and leaves the file unchanged [R9, I7; orchestrator decision 2026-10-04]

**Code**

- [x] `parser.py:54`: `_strip_html_comments` gains the keyword `keep_lines` (default `False`). With `True`, each comment is replaced by the newlines it held [D4]
- [x] `operations.py`: add `_single_match(matches, what, where)` [D9, I9]
- [x] `operations.py:1138-1168`: `update_validation` lists candidate rows per D4 and takes one through `_single_match` (R6). It refuses unless that row parses as a record (R7), then rewrites the original file line at that index (RC1) [D4, R6, R7]
  - "Parses as a record" can be tested as "the row's ID is among `parse_validation_matrix`'s IDs". That test is exact because the candidate is unique.
- [x] `operations.py:213-245`: extract the pure `_insert_table_row(text, section_heading, row) -> str`. `_append_table_row` becomes read, insert, write, with the same signature [D10]
- [x] `_insert_table_row`: before any table line is seen, the search stops at the next `## ` heading, so a heading with no table under it refuses [R9; orchestrator decision 2026-10-04]
- [x] `promote_requirement` and `add_validation`: move the append into the same `try` as the format, so a missing heading or table refuses [R9, I7]
- [x] `register_intent`: insert every goal and question row into one in-memory copy of `OVERVIEW.md`, then write once. A `ValueError` refuses [D10, m2, R9, I7]

### Validation

**Automated:**

- [x] G1 `uv run pytest tests/test_pm_*.py`. The existing `TestUpdateValidation::test_happy_path` and `test_not_found` pass unchanged
- [x] G2 `uv run ruff check src/ tests/`
- [x] G3 `uv run ruff format --check src/ tests/`
- [x] G4 `uv run mypy src/`

**Manual:**

- [x] On a scratch matrix with two `SV-001` rows, run `update-validation`. Expect a refusal naming both lines, and no file change.

**What We Know Works After This Phase:**

- Every table write targets exactly one place, or refuses with every file untouched (I7, I9).
- C2 and C3 are complete.

---

## Phase 3b: Backlog write-back

### Goal

`add-item`, `add-epic`, and `close-item` edit the frontmatter document they loaded, instead of rebuilding it from validated data (D8). Around that edit:

- Lookups go through `_single_match` (R3 to R5).
- List checks guard each append (R2).
- The frontmatter reader refuses a short read (R1).

This closes C5 and E2's WI case.

### Assumption Under Test

Two things must hold:

- Writing back the loaded mapping keeps every record the validator rejects.
- Extracting `_parse_backlog_mapping` leaves `parse_backlog`'s output unchanged (I8, which E3's backlog snapshot also checks).

B3 (fusion-tea's frontmatter writes back byte-identical) was already shown by `.orchestrate-logs/design-scratch/backlog_roundtrip.py`.

### Test Stencil (Write This First)

```python
class TestAddItem:
    def test_mints_above_unparsed_record(self, tmp_path):  # E2, WI case
        from agentic_mbse.pm.operations import add_item

        path = _write_raw_backlog(tmp_path, standalone=[_wi("WI-001"), _wi("WI-002", status="in-progress")])
        before = parse_frontmatter(path).data
        result = add_item(tmp_path, name="new", scale="standard", priority="P1")
        assert result.ids_assigned["WI"] == "WI-003"
        after = parse_frontmatter(path).data
        before["standalone"].append(after["standalone"][-1])
        assert after == before and after["standalone"][-1]["id"] == "WI-003"
```

`_write_raw_backlog(root, epics=(), standalone=())` writes the frontmatter with `yaml.dump` from raw mappings, because `BacklogData` cannot hold an invalid record. `_wi(id, **overrides)` returns one valid standalone mapping with any fields overridden.

### Changes Required

**See design.md for:** D8, D9 (R1 to R5, lookups, the two short-read cases), I6, I7, the `close-item` ordering in Architecture, and Implementation Notes (merge keys, "unreadable means any warning", new mappings as `model_dump(mode="json")`).

**Tests: reader, in `test_pm_parser.py`**

- [x] `TestParseFrontmatter::test_indented_dashes_stay_in_block_scalar` [R1, M4]
- [x] `TestParseFrontmatter::test_unique_keys_rejects_repeat`, covering a top-level key, a nested key, and a `<<` merge key, which is not a repeat [R1, M4]
- [x] `TestParseFrontmatter::test_default_keeps_last_wins` [R1]
- [x] Existing `TestParseBacklog` tests pass unchanged after the extraction [I8]

**Tests: operations, in `test_pm_operations.py`**

- [x] Helpers `_write_raw_backlog` and `_wi` [E2]
- [x] E2, WI: `TestAddItem::test_mints_above_unparsed_record` (the stencil above) [E2, C4, C5]
- [x] `test_carries_forward_invalid_item` in `TestAddItem`, `TestAddEpic`, and `TestCloseItem`: the frontmatter changes only at the target [C5, I6]
- [x] `TestAddItem::test_refuses_unreadable_frontmatter`, parametrized over five cases: malformed YAML, no frontmatter, `standalone` twice, `items` twice in one epic, and a closing `---` that is only indented [R1]
- [x] `TestAddItem::test_keeps_items_after_indented_dashes` [R1, M4]
- [x] `TestAddEpic::test_refuses_malformed_yaml` [R1, I7]
- [x] `TestCloseItem::test_refusal_leaves_item_active`: the directory is still in `work/active/`, and `spec.md` is unchanged [R1, I7]
- [x] `TestAddItem::test_refuses_non_list_standalone` and `TestAddItem::test_refuses_non_list_epic_items` [R2]
- [x] `TestAddEpic::test_refuses_non_list_epics` [R2]
- [x] `TestAddItem::test_refuses_duplicate_epic_names`: one rejected and one valid epic named `X` [R3, M1]
- [x] `TestCloseItem::test_refuses_duplicate_work_item_ids` [R3, M1]
- [x] `TestAddItem::test_refuses_rejected_epic_quoting_warning` and `TestCloseItem::test_refuses_invalid_item_quoting_warning` [R4]
- [x] `TestAddEpic::test_refuses_name_of_rejected_epic` [R5, M1]

**Code**

- [x] `parser.py:219` and `operations.py:83`: only an unindented `---` closes the frontmatter (`rstrip()` replaces `strip()`) [R1, M4]
- [x] `parser.py:193`: `parse_frontmatter` gains the keyword `unique_keys` (default `False`). With `True`, it loads with a SafeLoader subclass that rejects a repeated key in any mapping. The check runs before `<<` merges are flattened, and it reports through the existing malformed-YAML warning [R1, M4]
- [x] `parser.py:251-465`: extract `_parse_backlog_mapping` unchanged: same loop bodies, messages, and locations. `parse_backlog` becomes `parse_frontmatter` plus `_parse_backlog_mapping` [D8, I8]
- [x] `operations.py`: add `_load_backlog(path)`, returning the document (read with `unique_keys=True`) and its typed view [D8, R1]
  - Any warning on an existing file is R1. The docstring must say so.
  - A missing or empty file starts from a dumped `BacklogData()`, so a fresh write matches today's output.
- [x] `operations.py`: add `_backlog_list`. An absent key creates the list; a present non-list refuses [R2]
- [x] `operations.py`: add `_raw_epics` and `_raw_work_items`, whose locations use the parser's warning format [D9, R3, R4, R5]
- [x] `operations.py:155`: `_write_backlog` dumps a document, or a `BacklogData` converted first (the docstring says the typed form is for fixtures and fresh backlogs). It renders the body from the typed view of the edited document [D8]
- [x] `add_epic` `:904-923`: R1, then R5 through `_raw_epics`, then R2, then append `EpicEntry(...).model_dump(mode="json")`. The R5 message keeps "already exists" [D8, R5]
- [x] `add_item` `:962-1008`: R1, then mint, then R3 and R4 for `--epic`, then R2, then append the model dump. The epic "not found" wording stays [D8, R3, R4]
- [x] `close_item` `:1045-1107`: R1, R3, and R4 all run before the first `_update_frontmatter_fields`. Then set `status` and `completed` on the one matching mapping [D8, I7]

### Validation

**Automated:**

- [x] G1 `uv run pytest tests/test_pm_*.py`. The existing `TestWriteBacklogRoundTrip`, `TestAddEpic`, and `TestCloseItem` tests pass unchanged
- [x] G2 `uv run ruff check src/ tests/`
- [x] G3 `uv run ruff format --check src/ tests/`
- [x] G4 `uv run mypy src/`

**Manual:**

- [x] On a scratch `BACKLOG.md` holding an `in-progress` `WI-002`, run `add-item`. Expect `WI-003`, a frontmatter that differs only by the added mapping, and `WI-002`'s parse warning printed by the CLI.

**What We Know Works After This Phase:**

- No backlog write drops or alters a record it does not target.
- An unreadable or ambiguous backlog is refused before any file changes.
- C5 is complete, and E2 now has all seven cases.

---

## Phase 4: Acceptance

### Goal

Run E2 across all seven registries, the E3 suite check, and the full suite. Map every criterion to its evidence. Then hand E3's snapshot and E4 to the orchestrator.

### Assumption Under Test

Nothing else changed (C6). The existing tests pass unmodified, and the full suite is as green as at the base.

### Test Stencil

None. This phase adds no behaviour.

### Checklist

- [ ] `uv run pytest tests/test_pm_operations.py -v -k mints_above_unparsed` passes seven cases: SV, PR, G, AQ, DI, AD, WI [E2]
- [ ] `grep -n xfail tests/test_pm_*.py` finds nothing [brief]
- [ ] `git diff e5bd0db -- 'tests/test_pm_*.py' | grep -c '^-[^-]'` prints 0, meaning existing test lines are untouched. Otherwise, explain each removed line in the Implementation Record [C6]
- [ ] E3 suite check: G1 `uv run pytest tests/test_pm_*.py` is green [E3, C6]
- [ ] Full suite: `uv run pytest tests/` passes everything that passed at the base (1932 passed, 1 skipped, 33 deselected), plus the new tests [C6]
- [ ] G2 `uv run ruff check src/ tests/`
- [ ] G3 `uv run ruff format --check src/ tests/`
- [ ] G4 `uv run mypy src/`
- [ ] Fill in the Evidence Map in the Implementation Record [C1 to C6]
- [ ] Do not run E3's snapshot or E4. Record that they are ready for the orchestrator [brief]

**What We Know Works After This Phase:** every criterion has passing, named evidence in this repo's suite. Only the fusion-tea checks remain, and the orchestrator runs them.

---

## Orchestrator-Run Acceptance Checks (after Phase 4)

The implementer does not run these.

- **E3 snapshot.** Run `.orchestrate-logs/ft-snapshot/snapshot_parse.py` on the fusion-tea copies and compare with `baseline.json`. Expected: identical, except that `SV-035` appears and its warning disappears (I8).
- **E4.** Run `.orchestrate-logs/ft-snapshot/e4_check.py`. Expected, per design.md's Validation Approach:
  - `SV-035` parses with Type `baseline`, Status `passing`, and literal `|rel dev|` in Description and Expected.
  - `SV-034` is still warned, at `row 33`.
  - The new row is `SV-136`, added as one line.
  - The next DI on the `KNOWLEDGE.md` copy is `DI-015`.

## Environment Setup

- Run every command through `uv run`, per CLAUDE.md.
- **Scratch project for the manual checks:**
  - Make a temporary directory holding `work/BACKLOG.md`, so the CLI's `find_project_root` finds it.
  - Add the registry file under test, copied from `project_templates/` or written by hand.
  - Run commands from inside it with `uv run --project <repo root> agentic-mbse pm <command>`. Use `--help` for flags.

## Risk Management

See [design.md#potential-risks](design.md#potential-risks) for the user-facing risks. The risks specific to each phase:

- **Phase 1: a splitting change could alter a parsed value elsewhere** (E3 would fail).
  - Mitigation: the I2 test, and parser warning text left untouched.
  - Backstop: the orchestrator's snapshot.
- **Phase 2: a registry template could gain an ID outside a comment**, which would shift the first minted ID.
  - Checked at the base: there are none.
  - The existing first-ID tests catch it.
- **Phase 3a: section scoping could blank the wrong lines**, so R6 would refuse the template's happy path.
  - `test_happy_path` and `test_ignores_commented_example_rows` catch it.
- **Phase 3b: four risks.**
  - The extraction could change a warning's location or text (E3). Keep the loop bodies verbatim; the existing `TestParseBacklog` tests catch it.
  - The repeated-key loader could misread a `<<` merge as a repeat. It is tested explicitly.
  - `close-item` could refuse after its side effects. `test_refusal_leaves_item_active` pins the ordering.

## Implementation Record

### Base (`e5bd0db`, recorded at planning)

- **G1:** `tests/test_pm_*.py`: 224 passed.
- **G2:** 118 ruff findings repo-wide. None in `src/agentic_mbse/pm/`, `test_pm_operations.py`, or `test_pm_parser.py`; 5 are in `test_pm_dashboard.py`.
- **G3:** 78 files would be reformatted repo-wide. Of the four edited files, `operations.py`, `test_pm_operations.py`, and `test_pm_parser.py` carry 8 existing hunks.
- **G4:** 91 mypy errors in 19 files. None in `src/agentic_mbse/pm/`.
- **Full suite:** 1932 passed, 1 skipped, 33 deselected.
- **Probes:** `.orchestrate-logs/spec-review-scratch/probe.py` reproduces E1's reuse, the `update-validation` corruption, and the WI deletion. `.orchestrate-logs/plan-scratch/template_tokens.py` finds no registry ID token outside a comment in any template.

### Phase 1 Completion

**Completed:** 2026-10-04. Not committed; the orchestrator commits after review.

**Red runs (Step 0):** run on the base source (`e5bd0db`'s `src/`, plan commit `f08e445`) before any `src/` edit, with `uv run pytest tests/test_pm_operations.py -v -k "e1_three_record or escaped_row_changes_only_status or archive_note_reserves"`. All three failed where predicted:

```
FAILED tests/test_pm_operations.py::TestAddInsight::test_archive_note_reserves_di_014 - AssertionError: assert 'DI-012' == 'DI-015'
FAILED tests/test_pm_operations.py::TestAddValidation::test_e1_three_record_reproduction - AssertionError: assert ['SV-033'] == ['SV-033', 'SV-034']
FAILED tests/test_pm_operations.py::TestUpdateValidation::test_escaped_row_changes_only_status - AssertionError: [...]
E     - | SV-034 | bar (\|rel dev\| <= 1e-6) | baseline | test | x | 1e-6 | s | t | passing |
E     + | SV-034 | bar (\ | rel dev\ | <= 1e-6) | baseline | test | x | 1e-6 | passing | t | pending |
======================= 3 failed, 80 deselected in 0.32s =======================
```

The escaped-row diff shows both halves of the defect: `passing` lands in the Source column while Status stays `pending`, and `\|rel dev\|` is rewritten as `\ | rel dev\ |`.

After the source change, E1 still fails, but now only at its last assert: `assert 'SV-035' == 'SV-036'` (checked with `--runxfail`). The parse half passes. The archive-note test still mints `DI-012`. Both report XFAIL, as planned.

**Actual Changes:**

- `parser.py`:
  - Added `_split_table_row(line)` and `_escape_table_cell(value)` between `_strip_html_comments` and `_parse_markdown_table`. The splitter is the design's `re.split(r"(?<!\\)\|")`, then unescape, strip, and today's edge-cell drop. The escape raises `ValueError` on `\n`, `\r`, `<!--`, and `-->`, then backslashes every pipe.
  - `_parse_markdown_table` splits with `_split_table_row`. Its docstring says so.
- `operations.py`:
  - Imports both helpers from `parser.py`.
  - `_format_table_row` escapes every cell. Its docstring states I3 and the `ValueError`.
  - `promote_requirement` and `add_validation` format inside a `try`. A `ValueError` returns a refusal, with the parse warnings, before `_append_table_row`. The append stays outside the `try` until Phase 3a.
  - `register_intent` validates, mints, and formats every goal and question row into `goal_rows` and `question_rows` first, then appends them. A refusal on any row writes nothing. The appends still read and write the file once per row; the single write is Phase 3a.
  - `update_validation` splits with `_split_table_row` and writes back with `_format_table_row`. A `ValueError` from formatting becomes the R7 comment-marker refusal. It still takes the first matching line anywhere in the file (Phase 3a).
- `tests/test_pm_parser.py` (23 new cases): `TestSplitTableRow` (5 named cases, plus `test_unescaped_rows_split_as_before` over 8 rows), `TestEscapeTableCell` (9 cases), and `TestParseValidationMatrix::test_escaped_pipe_keeps_columns`.
- `tests/test_pm_operations.py` (11 new cases, 2 of them strict XFAIL): the three Step 0 tests, `TestFormatTableRow::test_escapes_pipes`, three `test_value_with_pipe_round_trips`, and four refusal tests. Each refusal test compares every file's bytes before and after.

**Refusal wording** (D9 leaves wording open):

- The escape's message names the value and the marker: `'a <!-- b' contains '<!--', which a table cell cannot hold; reword the value without it`.
- Operations prefix it with what was not written: `Requirement not added: `, `Verification not added: `, `Goal '<goal>': `, or `Question '<question>': `. The last two match `register_intent`'s existing per-item messages.
- `update_validation`'s R7 refusal does not quote the escape's message. That message tells the user to reword a value they typed, but here the fix is in the file: `SV-001's row in VALIDATION_MATRIX.md holds an HTML comment marker, so it cannot be rewritten. Move the comment out of the row by hand, then retry.` A comment marker is the only possible cause. `read_text` folds `\r` into `\n`, and the file is split on `\n`, so no cell can hold a line break.

**Gates:**

| Gate | Result | Parity bar |
|---|---|---|
| G1 `pytest tests/test_pm_*.py` | 256 passed, 2 xfailed (E1 and the archive-note test) | base 224 passed; +34 new cases |
| G2 `ruff check src/ tests/` | 118 repo-wide; PM-scoped check prints "All checks passed!" | ≤ 118 |
| G3 `ruff format --check src/ tests/` | 78 files repo-wide; 8 hunks in the four edited files | ≤ 78; still 8 hunks |
| G4 `mypy src/` | 91 errors in 19 files; 0 under `src/agentic_mbse/pm/` | ≤ 91; none in `pm/` |

**Manual check:** done in a scratch project holding the backlog and matrix templates. `add-validation --description "a | b"` minted `SV-001`, and the file holds `| SV-001 | a \| b | baseline | test | x | t |  |  | pending |`. `update-validation --status passing SV-001` then set Status. The row parses back as `('SV-001', 'a | b', 'passing')` with no warnings. `add-validation --description "a <!-- b"` exits 1 with the refusal above.

**Issues:**

- The fusion-tea copies were read but not run (allowed by the brief). In `.orchestrate-logs/ft-snapshot/*.md`, only one line contains `\|`: `VALIDATION_MATRIX.md:61`, which is `SV-035`. So by I2, no other parsed value on the copies should change. E3's snapshot is still the orchestrator's check.
- Interim `update_validation` behaviour on a bare template, until Phase 3a:
  - `SV-001` still matches the commented example row and rewrites it. This is unchanged from the base.
  - `SV-002` now refuses with the comment-marker message, because that example row ends in `-->`. At the base it rewrote the comment's example row.
  - Phase 3a's comment-blanked candidate search turns both into "not found".

**Deviations:**

- **New test helpers the plan did not name:**
  - `_file_bytes(root)` maps every file under `root` to its bytes. Phases 3a and 3b should reuse it for their refusal tests.
  - `_insight(di_id)` and `_write_knowledge(root, text)` were needed by the archive-note stencil. Phase 2's DI and `approve_research` tests can reuse them.
- **`TestFormatTableRow::test_escapes_pipes` also pins I3.** A value ending in a backslash is formatted, then split back unchanged.
- **`register_intent` returns `files_modified=[str(overview_path)]` unconditionally.** The old conditional bookkeeping always produced that single entry, because the function refuses up front when there is neither a goal nor a question. Its two `if goals:` / `if questions:` blocks became `for g in goals or []` loops, one nesting level shallower.
- **No helper names changed.**

**For Phase 2:**

- Remove both `xfail` markers when they report XPASS. With `strict=True`, an XPASS fails the suite.
- E1's remaining gap is exactly the scan: it mints `SV-035` today.

### Phase 2 Completion

**Completed:** 2026-10-04. Not committed; the orchestrator commits after review.

**Red runs:** the ten allocation tests were written first and run against Phase 1's source (`9aa8b57`) before any `src/` edit, with `uv run pytest tests/test_pm_operations.py -q -k "mints_above or mint_above or reports_reserved or e1_three_record or archive_note_reserves"`. Every fixture's parse precondition held, and each test failed at the ID it minted:

```
E   AssertionError: assert 'DI-002' == 'DI-003'
E   AssertionError: assert 'PR-002' == 'PR-003'
E   AssertionError: assert 'AD-002' == 'AD-003'
E   AssertionError: assert 'SV-002' == 'SV-003'
E   AssertionError: assert [] == ['SV-035']
E   AssertionError: assert {'DI-012': 'F...13': 'Second'} == {'DI-015': 'F...16': 'Second'}
E   AssertionError: assert ['G-002'] == ['G-003']
E   AssertionError: assert ['AQ-002'] == ['AQ-003']
E   AssertionError: assert {'G-002': 'fi...03': 'second'} == {'G-003': 'fi...04': 'second'}
E   AssertionError: assert 'WI-002' == 'WI-003'
================= 10 failed, 89 deselected, 2 xfailed in 0.56s =================
```

`TestRegistryIds` was written next, with `_registry_ids` imported at module top. Its red run is a collection `ImportError`, because the helper did not exist yet. After the source change, E1 and the archive-note test reported `XPASS(strict)`, which failed the suite as designed; both markers are now removed, and `grep -n xfail tests/test_pm_*.py` finds nothing.

**Actual Changes:**

- `operations.py`:
  - Added `_id_pattern(prefix)`, the D6 regex `(?<![A-Za-z0-9])PREFIX-(\d+)(?!\d)`. Its docstring says it is the only definition of how an ID is numbered (I5).
  - `_next_id` uses `_id_pattern(prefix).fullmatch` in place of its own `^PREFIX-(\d+)$`. Signature, padding, and the five `TestNextId` cases are unchanged.
  - Added `_registry_ids(path, prefix, parsed_ids) -> ParseResult[list[str]]` beside `_next_id`. Data is `parsed_ids` followed by every token in the file after `_strip_html_comments`. One warning per distinct number no parsed ID holds, located at its first spelling. A missing file (`FileNotFoundError`, the parsers' idiom) returns `parsed_ids` with no warning.
  - Imports `_strip_html_comments` from `parser.py` and `ParseResult` from `types.py`.
  - All eight allocation sites feed `_next_id` from `_registry_ids`: `add_insight`, `promote_requirement`, `register_decision`, `add_validation`, `approve_research` (running list), `register_intent` G and AQ (two running lists), `add_item`. The local is named `taken`, after the design's "an ID is taken if the file names it."
  - Each site returns its parse warnings, then the scan's (D7). Where a function has several returns after the scan, a local `warnings` list carries both, so refusals after the scan report them too.
- `tests/test_pm_operations.py` (34 new cases):
  - `TestRegistryIds` (24): `test_token_boundary` over all 12 Appendix A rows (`_APPENDIX_A`), `test_skips_html_comments`, `test_templates_reserve_nothing` (7 registry templates), `test_data_is_parsed_ids_then_tokens`, `test_one_warning_per_unparsed_number_at_first_spelling`, `test_parsed_id_covers_padded_mention`, `test_missing_file_returns_parsed_ids`.
  - E2 (6 cases): `test_mints_above_unparsed_record` in `TestAddValidation` (invalid Status), `TestPromoteRequirement` (`**PR-002**`), `TestRegisterIntent` (G and AQ, decorated cells), `TestAddInsight` and `TestRegisterDecision` (invalid Status). Each checks the parse precondition, the minted ID, and `_assert_one_record_added`.
  - Running lists and reporting (4): `TestApproveResearch::test_mints_above_archive_note` (`DI-015`, `DI-016`), `TestRegisterIntent::test_multiple_goals_mint_above_unparsed` (`G-003`, `G-004`), `TestAddItem::test_mints_above_invalid_item` (`WI-003`, ID only), `TestAddValidation::test_reports_reserved_id_after_parse_warnings`.

**Reservation warning wording** (D7 leaves it open): `SV-035 is named in VALIDATION_MATRIX.md but is not a parsed record; its ID stays reserved`. The message names the ID itself because the CLI prints only file and message, not location (`cli/pm_cli.py:39`).

**Gates:**

| Gate | Result | Parity bar |
|---|---|---|
| G1 `pytest tests/test_pm_*.py` | 292 passed, no XFAIL | Phase 1: 256 passed + 2 xfailed; +34 new cases |
| G2 `ruff check src/ tests/` | 118 repo-wide; PM-scoped check prints "All checks passed!" | ≤ 118 |
| G3 `ruff format --check src/ tests/` | 78 files repo-wide; 8 hunks in the four edited files | ≤ 78; still 8 hunks |
| G4 `mypy src/` | 91 errors in 19 files; 0 under `src/agentic_mbse/pm/` | ≤ 91; none in `pm/` |

G3 first showed 10 hunks: two new test lines were over-long. They were laid out by hand the way `ruff format` wanted, without formatting the whole file, so the 8 base hunks stay as they were.

**Manual check:** a scratch project held the backlog template and the E1 matrix. `agentic-mbse pm add-validation --description new --type baseline --mechanism test --expected e --tolerance t` exited 0 with `Added verification SV-036: new`, wrote `| SV-036 | new | baseline | test | e | t |  |  | pending |` after the malformed row, and printed two warnings on stderr in this order: the parser's `Invalid Type 'rel dev'` for the malformed row, then `SV-035 is named in VALIDATION_MATRIX.md but is not a parsed record; its ID stays reserved`.

**Issues:**

- `register_decision`'s missing-`## Key Decisions` refusal still returns no warnings, as at the base. The scan runs before it but only reads.
- In `OVERVIEW.md`, a question's Source cell citing `G-00N` now reserves that goal number. This is the spec's accepted cost (a gap at most), and the reservation warning names the citation when no such goal parses.
- `add_item` still rewrites `BACKLOG.md` from parsed data, so in `test_mints_above_invalid_item` the invalid `WI-002` is still deleted on write. The test checks the ID only, as planned; Phase 3b fixes the write.

**Deviations:**

- **Test helpers the plan did not name:** `_write_archived_knowledge(root)` (shared by the Phase 1 archive-note test, which now uses it, and the `approve_research` case), `_decision(ad_id)`, `_write_overview(root, goal_rows, question_rows)`, and the `_OVERVIEW_GOAL_ROWS` and `_OVERVIEW_QUESTION_ROWS` fixtures.
- **`_write_raw_backlog` and `_wi` were added here, not in Phase 3b.** `test_mints_above_invalid_item` needs a backlog holding an invalid item, which `BacklogData` cannot hold. Both follow the plan's signatures. Phase 3b reuses them and only needs to tick its helper checkbox.
- **Two tests beyond the plan's list.** `test_templates_reserve_nothing` pins B2 directly, so a template that gains an ID outside a comment fails by name rather than through a shifted first ID. `test_data_is_parsed_ids_then_tokens` pins the data contract: parsed IDs first, then every token, duplicates kept. That is the design's "parsed IDs plus every token" taken literally; `_next_id` only needs the maximum.
- **`fullmatch` versus the old `^...$` match:** they differ only for an ID ending in a newline, which no parser emits (every record ID is a stripped cell or a regex group).
- **No helper names changed.**

**For Phase 3a and 3b:**

- `promote_requirement`, `add_validation`, and `register_intent` already hold a local `warnings` list (parse plus reservation). Phase 3a's refusals should return it.
- Phase 3b's `add_item` must keep feeding `_next_id` from `_registry_ids(backlog_path, "WI", <parsed IDs>)` after the switch to `_load_backlog`, and must keep `warnings = [*parse warnings, *taken.warnings]`.
- `-k mints_above_unparsed` currently selects 6 cases (SV, PR, G, AQ, DI, AD). Phase 3b's WI case must keep the name `TestAddItem::test_mints_above_unparsed_record` for Phase 4's count of seven.

### Phase 3a Completion

**Completed:** 2026-10-04. Not committed; the orchestrator commits after review.

**Red runs:** the eleven operation tests were written first and run against Phase 2's source (`e9fd8b1`) before any `src/` edit, with `uv run pytest tests/test_pm_operations.py -q -k "commented_example or refuses_duplicate_rows or outside_registry_section or refuses_unparsed_row or comment_in_status_cell or missing_section_refuses or missing_questions_section"`:

```
E   ValueError: Section heading '## Requirements' not found in /tmp/.../REQUIREMENTS.md
E   ValueError: No table found under '## Requirements' in /tmp/.../REQUIREMENTS.md
E   ValueError: Section heading '## Verification Registry' not found in /tmp/.../VALIDATION_MATRIX.md
E   ValueError: No table found under '## Verification Registry' in /tmp/.../VALIDATION_MATRIX.md
E   ValueError: Section heading '## Analysis Questions' not found in /tmp/.../OVERVIEW.md
E   AssertionError: assert not True    (commented SV-001: success=True, 'Updated SV-001 status to passing')
E     - SV-002 not found in VALIDATION_MATRIX.md
E     + SV-002's row in VALIDATION_MATRIX.md holds an HTML comment marker, so it cannot be rewritten. [...]
E   AssertionError: assert not True    (duplicate SV-033: 'Updated SV-033 status to failing')
E   assert [4] == [10]                 (the Summary row before the registry took the write)
E   AssertionError: assert not True    (unparsed SV-035: 'Updated SV-035 status to failing')
E   AssertionError: assert not True    (comment in Status cell: 'Updated SV-001 status to passing')
================= 11 failed, 1 passed, 125 deselected in 0.68s =================
```

- The one pass is `test_ignores_commented_example_rows`, as expected. At the base, the first match is already the real row. The test guards the new R6 against the template's commented `SV-001`.
- `TestSingleMatch` was added next, with `_single_match` imported at module top. Its red run is a collection `ImportError`.
- `TestStripHtmlComments` red: `TypeError: _strip_html_comments() got an unexpected keyword argument 'keep_lines'` (2 failed, 1 passed; the default-behaviour case passes).
- The R9 later-section case (orchestrator decision) was red on this phase's first-pass source, before the `_insert_table_row` change: both operations reported success after writing into the later section's table.

  ```
  E   AssertionError: assert not True    (OperationResult(success=True, message='Added requirement PR-001: r', ...))
  E   AssertionError: assert not True    (OperationResult(success=True, message='Added verification SV-001: d', ...))
  FAILED tests/test_pm_operations.py::TestPromoteRequirement::test_missing_section_refuses[table only in a later section]
  FAILED tests/test_pm_operations.py::TestAddValidation::test_missing_section_refuses[table only in a later section]
  ================= 2 failed, 4 passed, 136 deselected in 0.38s ==================
  ```

**Actual Changes:**

- `parser.py`: `_strip_html_comments` gains the keyword `keep_lines` (default `False`). With `True`, each comment becomes the newlines it held. The default output is unchanged.
- `operations.py`:
  - Added `_single_match(matches, what, where)` beside `_registry_ids`, typed with a module `TypeVar` `T` (as in `types.py`). None gives `"{what} not found in {where}"`, the wording all three existing not-found messages already use (`update_validation`, `add_item`'s epic, `close_item`). Several gives `"{what} appears N times in {where} (loc, loc); deduplicate by hand, then retry"`.
  - Extracted `_insert_table_row(text, section_heading, row) -> str` from `_append_table_row`. `_append_table_row` is now read, insert, write, with the same signature. The loop bodies are verbatim except for one added branch (R9, orchestrator decision): before any table line is seen, the search stops at the next `## ` heading, a bare `##` included. A table under a `### ` subheading inside the section is still found, as the parser reads it.
  - Added `_raw_table_rows(text, section_heading, row_id)`. It returns `("line N", index)` pairs for D4's candidate rows: the first line equal to the heading (the parser's `^heading\s*$`), up to the next `## ` heading, on comment-blanked text.
  - `promote_requirement` and `add_validation` call `_append_table_row` inside the same `try` as the format, so R8 and R9 both refuse before any write.
  - `register_intent` inserts every goal and question row into one in-memory copy of `OVERVIEW.md` and writes once. A missing section refuses with `Intent not registered in OVERVIEW.md: Section heading '## Analysis Questions' not found`.
  - `update_validation` follows D4. It parses the matrix, takes the one candidate through `_single_match` (R6), checks R7, then splits and rewrites the original file line at that index (RC1). Every result after the parse now carries the parse warnings, as the other operations' results do.
- `tests/test_pm_parser.py` (3 new): `TestStripHtmlComments`.
- `tests/test_pm_operations.py` (17 new): `TestSingleMatch` (3); `TestUpdateValidation` (7): `test_ignores_commented_example_rows`, `test_commented_example_rows_are_not_found` (SV-001 and SV-002 on the bare template), `test_refuses_duplicate_rows`, `test_ignores_rows_outside_registry_section`, `test_refuses_unparsed_row`, `test_refuses_comment_in_status_cell`; `test_missing_section_refuses` in `TestPromoteRequirement` and `TestAddValidation` (3 each: no heading, no table, table only in a later section); `TestRegisterIntent::test_missing_questions_section_writes_nothing`. Every refusal test compares every file's bytes before and after.

**Refusal wording** (D9 leaves it open):

- R6: `SV-001 appears 2 times in VALIDATION_MATRIX.md (line 5, line 6); deduplicate by hand, then retry`. Not found keeps today's `SV-999 not found in VALIDATION_MATRIX.md`.
- R7, the row is not a rewritable record: `SV-035's row in VALIDATION_MATRIX.md does not parse as a record, so its Status cannot be updated. Fix the row by hand, then retry: a pipe inside a cell must be written as \|, and an HTML comment must move out of the row.` The parse warnings returned with it name what is invalid.
- R7, a comment marker in another cell: Phase 1's message, unchanged.
- R9: `<What> not added to <FILE>: Section heading '## X' not found` or `No table found under '## X'`.

**Gates:**

| Gate | Result | Parity bar |
|---|---|---|
| G1 `pytest tests/test_pm_*.py` | 312 passed | Phase 2: 292 passed; +20 new cases. `test_happy_path` and `test_not_found` pass unchanged |
| G2 `ruff check src/ tests/` | 118 repo-wide; PM-scoped check prints "All checks passed!" | ≤ 118 |
| G3 `ruff format --check src/ tests/` | 78 files repo-wide; 8 hunks in the four edited files | ≤ 78; still 8 hunks |
| G4 `mypy src/` | 91 errors in 19 files; 0 under `src/agentic_mbse/pm/` | ≤ 91; none in `pm/` |

The table shows the rerun after the R9 change. G3 first showed 13 hunks: five new lines were over-long. They were laid out by hand the way `ruff format` wanted, so the 8 base hunks stay as they were. `git diff e5bd0db -- 'tests/test_pm_*.py' | grep -c '^-[^-]'` prints 0.

**Manual check:** a scratch project held the backlog template and a matrix with two `SV-001` rows and a raw-pipe `SV-002`.

- `update-validation --status passing SV-001` exited 1 with the R6 message naming line 5 and line 6.
- `SV-002` exited 1 with the R7 message. The CLI also printed the parser's `Invalid Type 'rel dev'` warning.
- The matrix's sha256 was unchanged after both.
- On the bare template, `SV-001` exited 1 with `SV-001 not found in VALIDATION_MATRIX.md`.
- After `add-validation --description "a | b"`, `SV-001` updated the real row (`| SV-001 | a \| b | ... | passing |`), and the commented examples were untouched.
- The R9 reproduction (`## Requirements` with the prose `None yet.`, then a `## Glossary` table) now refuses with `Requirement not added to REQUIREMENTS.md: No table found under '## Requirements'`, and the file is unchanged.

**Issues:**

- **R9 case: a heading with no table under it, while a later section has one.** [AGENT] (orchestrator decision, 2026-10-04) Fixed in this phase under R9.
  - At the base, and in this phase's first pass, the inserter took the first table in any later section. `promote_requirement` reported `Added requirement PR-001` and wrote the row into a `## Glossary` table, where `parse_requirements` does not read it.
  - The design's "keep the loop verbatim" governed the extraction mechanics, not this behaviour. R9 is the governing rule.
  - No fusion-tea copy was exposed: none has a `## Requirements`, `## Goals Registry`, or `## Analysis Questions` heading.
- **Known pre-existing behaviour, left as is** (orchestrator decision, 2026-10-04): `update_validation` on a missing `VALIDATION_MATRIX.md`, and `register_intent` on a missing `OVERVIEW.md`, raise `FileNotFoundError`, as at the base. Neither is on D9's refusal list, and neither loses a record.
- **Not updated: design.md's refusal-test table.** Its R9 row does not name the later-section case. design.md is outside this session's edit scope; this plan's Phase 3a Tests checklist records the case.

**Deviations:**

- **R7 checks the Status cell, not only the ID.** The plan's test was "the row's ID is among the parsed IDs". The code also requires the original line's ninth cell to equal the parsed record's Status. This closes three gaps:
  - A comment inside the Status cell. `_format_table_row` never sees it, because the cell is overwritten before formatting. At Phase 2's source the comment was silently deleted; `test_refuses_comment_in_status_cell` now pins the refusal. RC1 says a comment-bearing row refuses.
  - A matrix whose header puts Status somewhere other than the ninth column. Before, that write landed in the wrong cell. Header lookup is still a Non-Goal; this only refuses.
  - A parsed row with fewer than nine cells, which would otherwise raise `IndexError`.
- **New helper name:** `_raw_table_rows`. The design only says `update_validation` "builds its pairs from D4's candidate rows". The name matches the design's backlog finders, `_raw_epics` and `_raw_work_items`, which also feed `_single_match`.
- **`_insert_table_row`'s two messages drop `in {path}`,** because the pure function has no path. Each caller's refusal names the file instead. So Phase 1's R8 prefixes became `Requirement not added to REQUIREMENTS.md: ` and `Verification not added to VALIDATION_MATRIX.md: `. No test asserted the old prefixes.
- **`update_validation` returns the parse warnings** on every result after its parse, success included. This is a new diagnostic (C6.5 allows them). It is what tells the user why R7 refused.
- **The candidate section is the first `## Verification Registry`,** as in the parser. The end test `##\s` is per line, so a bare `##` line does not end the section. That only widens it, which errs safe.

**For Phase 3b:**

- `_single_match(matches, what, where)` is ready. The "not found" wording matches the existing `Epic '{epic}' not found in BACKLOG.md` and `{wi_id} not found in BACKLOG.md` if `what` is `f"Epic '{name}'"` or the WI ID and `where` is `"BACKLOG.md"`. Then the existing `"not found"` and `"BACKLOG.md"` assertions (`test_pm_operations.py:948`, `:1187` at base) hold.
- Its several-match message lists locations as given, so `_raw_epics` and `_raw_work_items` should pass the parser's `epics[i]`, `epics[i].items[j]`, and `standalone[k]` strings.
- `_file_bytes(root)` is the refusal-test helper; `_write_raw_backlog` and `_wi` exist from Phase 2.

### Phase 3b Completion

**Completed:** 2026-10-04. Not committed; the orchestrator commits after review.

**Red runs:** all 30 new tests were written first and run against Phase 3a's source (`7822989`) before any `src/` edit. 26 failed, each where predicted:

```
tests/test_pm_parser.py:86: AssertionError: assert {'goal': 'first'} == {'Status': 'a...--\nsecond\n'}      (indented --- closed the frontmatter)
tests/test_pm_parser.py:100: TypeError: parse_frontmatter() got an unexpected keyword argument 'unique_keys'   (x2, rejects_repeat)
tests/test_pm_parser.py:119: TypeError: parse_frontmatter() got an unexpected keyword argument 'unique_keys'   (x2, merge override)
tests/test_pm_operations.py:1654: AssertionError: assert ({'epics': [],...}]} == {'epics': [],...}]}      (E2 WI: in-progress WI-002 deleted)
tests/test_pm_operations.py:1668: AssertionError: assert {'epics': [{'...andalone': []} == ...           (add-item: WI-002 and WI-003 deleted)
tests/test_pm_operations.py:1681: AssertionError: assert not True                                      (x5, every unreadable frontmatter was overwritten)
tests/test_pm_operations.py:1716: IndexError: list index out of range                                  (indented ---: every item after it deleted)
tests/test_pm_operations.py:1726: AssertionError: assert not True                                      (non-list standalone replaced)
tests/test_pm_operations.py:1736: AssertionError: assert not True                                      (non-list epic items replaced)
tests/test_pm_operations.py:1776: assert not True                                                      (duplicate epic X: rejected X deleted)
tests/test_pm_operations.py:1788: assert 'not a valid record' in "Epic 'X' not found in BACKLOG.md"
tests/test_pm_operations.py:1949: AssertionError: assert {'epics': [{'...andalone': []} == ...           (add-epic: invalid item and rejected epic deleted)
tests/test_pm_operations.py:1960: assert not True                                                      (add-epic over malformed YAML)
tests/test_pm_operations.py:1973: assert not True                                                      (non-list epics replaced)
tests/test_pm_operations.py:1986: assert not True                                                      (second epic beside a rejected one)
tests/test_pm_operations.py:2140: AssertionError: assert {'epics': [{'...andalone': []} == ...           (close-item: rejected epic and invalid items deleted)
tests/test_pm_operations.py:2177: assert 'Malformed YAML' in 'WI-001 not found in BACKLOG.md'
tests/test_pm_operations.py:2176: AssertionError: assert not True                                      (standalone twice: WI-001 closed, WI-002 deleted)
tests/test_pm_operations.py:2194: AssertionError: assert not True                                      (duplicate WI-001: first one closed)
tests/test_pm_operations.py:2208: assert 'not a valid record' in 'WI-001 not found in BACKLOG.md'
================= 26 failed, 4 passed, 223 deselected in 0.31s =================
```

The 4 passes are behaviour pins, expected to pass before and after: `test_default_keeps_last_wins` (read-only callers keep last-wins), `test_null_standalone_starts_a_list`, and `test_fresh_backlog_matches_typed_write[missing]` and `[empty]` (a fresh write matches today's typed write).

**Actual Changes:**

- `parser.py`:
  - Added `_UniqueKeyLoader`, a `yaml.SafeLoader` subclass, with `_MERGE_TAG`, at the end of the shared helpers. It records each mapping's keys as written the first time the mapping is flattened, then compares the constructed keys after construction. A repeat raises `ConstructorError`, which `parse_frontmatter` already reports as its "Malformed YAML" warning.
  - `parse_frontmatter(path, *, unique_keys=False)`. Only an unindented `---` closes the frontmatter (`rstrip()`). It loads with `_UniqueKeyLoader` when `unique_keys` is set, else with `yaml.SafeLoader`, which is what `safe_load` used.
  - Extracted `_parse_backlog_mapping(raw, fp) -> ParseResult[BacklogData]` from `parse_backlog`. No diff hunk falls inside the loop bodies. `parse_backlog` is now `parse_frontmatter` plus `_parse_backlog_mapping`, with the warnings in the same order.
- `operations.py`:
  - Imports `_parse_backlog_mapping` and `parse_frontmatter`, and no longer imports `parse_backlog`.
  - `_update_frontmatter_fields` uses `rstrip()` for the closing delimiter.
  - `_write_backlog(path, document)` takes a document or a `BacklogData`. It dumps the document and renders the body from `_parse_backlog_mapping` of that document.
  - New backlog helpers beside it:
    - `_load_backlog` returns the document and its typed view, else raises R1.
    - `_backlog_list` returns the list to append to, else raises R2.
    - `_raw_epics` and `_raw_work_items` are the finders. Both use `_entries_of`, so a lookup finds nothing in a non-list.
    - `_backlog_target` applies R3 through `_single_match`, then R4. `_with_parse_warnings` formats R4's and R5's quoted warnings.
    - `_work_item_ids` lists the parsed IDs, for minting and for R4.
  - `add_epic`: R1, then R5 through `_raw_epics`, then R2, then appends `EpicEntry(...).model_dump(mode="json")`.
  - `add_item`: R1, then mint, then R3 and R4 for `--epic`, then R2, then appends the model dump. Minting still feeds `_next_id` from `_registry_ids(backlog_path, "WI", ...)`, with `warnings = [*parse warnings, *taken.warnings]`.
  - `close_item`: R1, R3, and R4 all run before the first `_update_frontmatter_fields`. At step 3 it sets `status` and `completed` on the one matching mapping, then writes.
- `tests/test_pm_parser.py` (6 new cases), all in `TestParseFrontmatter`: `test_indented_dashes_stay_in_block_scalar`, `test_unique_keys_rejects_repeat` (top-level and nested key), `test_unique_keys_merge_override_is_not_a_repeat` (a merge override, and a chained merge under a deeper anchor), and `test_default_keeps_last_wins`.
- `tests/test_pm_operations.py` (24 new cases):
  - `TestAddItem` (15): `test_mints_above_unparsed_record` (E2 WI), `test_carries_forward_invalid_item`, `test_refuses_unreadable_frontmatter` (5 cases), `test_keeps_items_after_indented_dashes`, `test_refuses_non_list_standalone`, `test_refuses_non_list_epic_items`, `test_null_standalone_starts_a_list`, `test_fresh_backlog_matches_typed_write` (missing and empty), `test_refuses_duplicate_epic_names`, `test_refuses_rejected_epic_quoting_warning`.
  - `TestAddEpic` (4): `test_carries_forward_invalid_item`, `test_refuses_malformed_yaml`, `test_refuses_non_list_epics`, `test_refuses_name_of_rejected_epic`.
  - `TestCloseItem` (5): `test_carries_forward_invalid_item`, `test_refusal_leaves_item_active` (malformed YAML, and `standalone` twice), `test_refuses_duplicate_work_item_ids`, `test_refuses_invalid_item_quoting_warning`.
  - Every refusal test compares every file's bytes before and after with `_file_bytes`. Every carry-forward test compares the loaded frontmatter with the one before, plus the single edit.

**Refusal wording** (D9 leaves wording open):

- R1: `BACKLOG.md cannot be read whole, so writing it back could delete records. Fix it by hand, then retry: <the reader's warning>`. For a repeated key, the warning names the key and its line.
- R2: `'standalone' in BACKLOG.md is not a list, so appending to it would discard it. Fix it by hand, then retry.` The location is `epics`, `standalone`, or `epics[i].items`.
- R3 uses `_single_match`. "Not found" keeps the existing `Epic 'X' not found in BACKLOG.md` and `WI-001 not found in BACKLOG.md`. A duplicate gives `WI-001 appears 2 times in BACKLOG.md (epics[0].items[0], standalone[0]); deduplicate by hand, then retry`.
- R4: `WI-002 is in BACKLOG.md at standalone[1] (Invalid status 'in-progress') but is not a valid record. Fix it by hand, then retry.`
- R5: `Epic 'X' already exists in BACKLOG.md at epics[0]`. A rejected epic adds its parse warning: `at epics[0] (Invalid status 'bogus', expected one of: draft, active, completed)`.

**Gates:**

| Gate | Result | Parity bar |
|---|---|---|
| G1 `pytest tests/test_pm_*.py` | 342 passed | Phase 3a: 312 passed; +30 new cases. `TestWriteBacklogRoundTrip`, `TestAddEpic`, `TestCloseItem`, and `TestParseBacklog` pass unchanged |
| G2 `ruff check src/ tests/` | 118 repo-wide; PM-scoped check prints "All checks passed!" | ≤ 118 |
| G3 `ruff format --check src/ tests/` | 78 files repo-wide; 8 hunks in the four edited files | ≤ 78; still 8 hunks |
| G4 `mypy src/` | 91 errors in 19 files; 0 under `src/agentic_mbse/pm/` | ≤ 91; none in `pm/` |

G3 first showed 9 hunks: one new test line was over-long. It was laid out by hand the way `ruff format` wanted, so the 8 base hunks stay as they were. `git diff e5bd0db -- 'tests/test_pm_*.py' | grep -c '^-[^-]'` prints 0.

**Manual check:** a scratch project held a `BACKLOG.md` with a valid `WI-001` and an `in-progress` `WI-002`.

- `add-item --name Third --scale standard --priority P1` exited 0 with `Added work item WI-003: Third`.
  - The frontmatter diff is exactly the added `WI-003` mapping, including `completed: null`.
  - stderr printed `Invalid status 'in-progress'`, then `WI-002 is named in BACKLOG.md but is not a parsed record; its ID stays reserved`.
  - The re-rendered body lists `WI-001` and `WI-003` but not `WI-002`, as D8 says.
- `close-item WI-002` (with `work/active/WI-002_second/`) exited 1 with the R4 message above. Every file's hash was unchanged, and the directory stayed in `work/active/`.
- With a second `standalone:` key added, `add-item` exited 1 with R1 naming `found repeated key 'standalone'`. Every file's hash was unchanged.

**Issues:**

- **The first loader design false-refused a valid merge.** The obvious override checks a mapping's own keys inside `construct_mapping`, before the merge is flattened. But when a mapping is merged into a shallower one, PyYAML flattens it early, while constructing the parent. Its keys then include the merged keys before its own check runs, so `k: 1` overriding a merged `k: 0` reads as a repeat. The probe is `.orchestrate-logs/impl-3b-scratch/unique_keys_probe.py` (gitignored). The shipped loader records keys on the first flatten instead. `test_unique_keys_merge_override_is_not_a_repeat[chained merge under a deeper anchor]` pins it.
- **R1's line numbers count from the first frontmatter line.** File line 4 reads as "line 3". The existing "Malformed YAML" warning has always counted this way. Changing it would alter existing warning text, which E3 compares, so it was left alone.
- **A carried-forward invalid record is now in the frontmatter but not in the dashboard body** (D8). Before, it was deleted from both.

**Deviations:**

- **`_backlog_list` treats a null value like an absent key** (`standalone:` with nothing after it). It does not refuse under R2. [AGENT]
  - Replacing a null discards nothing, so R2's message ("appending would discard it") would be false.
  - `standalone:` with nothing after it is how a hand-written empty list naturally reads, and today's writer also turned it into a list.
  - `test_null_standalone_starts_a_list` pins it.
- **`_load_backlog` starts from a dumped `BacklogData()` whenever the loaded mapping is empty.** The plan named a missing and an empty file. This rule also covers an empty frontmatter (`---\n---`, which `test_pm_cli.py`'s status fixture uses). No record can be lost, and the first write matches today's typed write. `test_fresh_backlog_matches_typed_write` pins the missing and empty cases.
- **`_write_backlog`'s docstring says only test fixtures pass a `BacklogData`.** The plan wrote "fixtures and fresh backlogs". But fresh backlogs go through `_load_backlog`, which hands every operation a document.
- **R4's validity test is passed to `_backlog_target` as `parsed`**: whether the typed view holds the name or ID. This is the design re-check's "valid if and only if the typed view holds that ID or name". It is exact because the raw match is unique.
- **The merge case is its own test.** `test_unique_keys_rejects_repeat` covers the top-level and nested keys. The `<<` merge case is `test_unique_keys_merge_override_is_not_a_repeat`, because it asserts the opposite outcome. It also adds the chained-merge case.
- **`test_refusal_leaves_item_active` has two cases.** At the base, malformed YAML already refused, but with a misleading "WI-001 not found". The repeated-`standalone` case is the one where the base closed the item and deleted the other list. Both assert the reader's warning is in the message.
- **Three pin tests beyond the plan's list:** `test_null_standalone_starts_a_list`, and `test_fresh_backlog_matches_typed_write` for missing and empty.
- **New helper names.**
  - Source: `_UniqueKeyLoader` (with `_MERGE_TAG`), `_entries_of`, `_with_parse_warnings`, `_backlog_target`, `_work_item_ids`.
  - Tests: `_write_backlog_text`, `_epic`, `_UNREADABLE_BACKLOGS`. Phase 2's `_write_raw_backlog` now delegates to `_write_backlog_text`.
  - No design name changed.

**For Phase 4:**

- `uv run pytest tests/test_pm_operations.py -k mints_above_unparsed` already selects and passes 7 cases (SV, PR, G, AQ, DI, AD, WI).
- `grep -n xfail tests/test_pm_*.py` finds nothing, and the removed-base-lines check prints 0.
- C5 evidence: the three `test_carries_forward_invalid_item` tests, E2's WI case, and the R1 to R5 tests listed above.
- The full suite (`uv run pytest tests/`) was not run in this phase. No test outside `tests/test_pm_*.py` calls the backlog operations or the frontmatter reader.

### Phase 4 Completion

**Completed:**
**Full suite result:**
**Gate results:**

### Evidence Map (filled in Phase 4)

| Criterion | Evidence (test node IDs) |
|---|---|
| C1 Escaped pipes | |
| C2 One escape rule | |
| C3 Round-trip | |
| C4 No ID minted twice | |
| C5 No record lost on write | |
| C6 Nothing else changes | |
| E1 | |
| E2 (seven cases) | |
| E3 suite check | |

---

**Status:** Draft → In Progress → Complete
