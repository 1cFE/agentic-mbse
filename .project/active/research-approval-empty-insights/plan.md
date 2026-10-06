# Implementation Plan: Approve Research with No New Insights

**Status:** Draft
**Created:** 2026-10-05
**Last Updated:** 2026-10-05
**Branch:** research-approval-empty-insights (plan written at `2a229f4`)
**Complexity:** LOW, one implementation session

## Source Documents

- **Spec:** [spec.md](spec.md). Criteria SC1-SC7, numbered in spec order as the design's [Validation Approach](design.md#validation-approach) does.
- **Design:** [design.md](design.md), accepted 2026-10-05 including D5. It fixes the decisions ([Key Decisions](design.md#key-decisions)), the check order and exact shipped wording ([Implementation Notes](design.md#implementation-notes)), the invariants ([Required Invariants](design.md#required-invariants)), and tests 1-10 ([Validation Approach](design.md#validation-approach)). This plan points at those sections and does not restate them.
- **Brief:** [briefs/plan.md](briefs/plan.md).

## The Point

[INHERITED: backlog PM-APPROVE-RESEARCH-EMPTY-INSIGHTS] Research is sometimes approved without producing a new domain insight: a source-registration round, a bounded negative result, a confirmation of what is already known. Today `approve-research` refuses an explicit empty insight list with `No insights provided`. The document stays in `knowledge/research/pending/`, and operators move it by hand, bypassing the supported operation.

[INHERITED: product-lens.md] `/research` asks the user two separate things: approve the report, and accept or skip each insight. Only accepted insights enter `KNOWLEDGE.md`. The repair has failed if a user approves a useful report while skipping every insight and approval is refused, the report stays pending, or an unaccepted insight enters `KNOWLEDGE.md`.

[AGENT, from the design brief] Users reach the operation only through the shipped `/research` command. The instruction change there is part of the repair, not polish.

## Implementation Strategy

**Phasing rationale.** Two phases. Phase 1 is all behavior: every test first, then the one function change. Phase 2 is all words: help strings, shipped text, tracking.

[AGENT] This differs from the brief's suggested cut in one place. The brief put CLI tests 8-10 in Phase 2. Test 8 (`--insights '[]'` through `main()`) is the user-visible form of the defect. If it is written after the operation changes, it is green on first run and the red evidence for the user's actual symptom is lost. So all ten tests, plus one added test (below), are written in Phase 1 before the code changes. Tests 9 and 10 pin existing behavior and could live in either phase; they go in Phase 1 to keep the test file edit in one place.

**Critical path.** Write tests 1-11 → run them and record red/green against current code → change `approve_research` → green → project gates → Phase 2 text edits → gates → tracking.

**First proof point.** Test 1's three cases and test 8 fail against current code with `No insights provided`. That proves the tests reproduce the backlog defect before anything changes.

**Added test (plan decision).** [AGENT] Invariant I1 says every refusal, including field validation inside the build loop, returns before any write. `TestApproveResearch` has no test of the build-loop refusal today, and the design's list does not add one. The D1 gate sits directly above the build loop, so this is the refusal most exposed to a reordering slip. Test 11 below pins it. It is expected green against current code.

---

## Phase 1: Operation and CLI behavior, test-first

### Goal

`approve_research` accepts `[]`, never touches `KNOWLEDGE.md` on that path, refuses `None`/non-lists, a non-file pending path, and a `..` escape, and keeps non-empty output byte-identical. All of it is proven by tests that were seen failing first where they should fail.

### Assumption Under Test

The design's single-path change ([Core Concept](design.md#core-concept), [Architecture](design.md#architecture)) satisfies SC1-SC5 and SC7 with no change to the CLI handler. In particular: the CLI passes `'[]'` through untouched (`pm_cli.py:66-76`), so fixing the operation fixes the command.

### Test names (fixed here; the design left naming open)

Operation tests go in `TestApproveResearch` (`tests/test_pm_operations.py:1263`). CLI tests go in a new class `TestPmApproveResearchMain` beside `TestPmApproveResearch` (`tests/test_pm_cli.py:417`). The existing mocked CLI tests stay as they are.

| # | Name | Design row / source |
|---|------|---------------------|
| 1 | `test_empty_list_approves_without_touching_knowledge[archived, undecodable, missing]` | design test 1 |
| 2 | `test_non_list_insights_refused[none, json_string]` | design test 2 (one parametrized test) |
| 3 | `test_insights_argument_is_required` | design test 3 |
| 4 | `test_pending_directory_refused[empty, one]` | design test 4 |
| 5a | `test_dotdot_escape_refused[empty, one]` | design test 5, escaping path |
| 5b | `test_project_root_with_dotdot_approves` | design test 5, valid document |
| 6 | `test_file_not_in_pending[empty, one]`, `test_missing_file[empty, one]` | design test 6 (existing tests, parametrized and given the nothing-moved asserts) |
| 7 | `test_happy_path` | design test 7 (existing, extended) |
| 8 | `TestPmApproveResearchMain::test_empty_insights_approves` | design test 8 |
| 9 | `TestPmApproveResearchMain::test_missing_insights_is_usage_error` | design test 9 |
| 10 | `TestPmApproveResearchMain::test_null_insights_is_usage_error` | design test 10 |
| 11 | `test_blank_field_refused_before_any_write` | [AGENT] plan addition for I1 |

Shared setup: a `_pending_doc(root, name="20260202-120000_r.md")` helper that creates `pending/` and one document, and a `_one_insight()` helper returning a valid `InsightInput`. Parametrize list size as `[[], [_one_insight()]]` with ids `empty`, `one`.

### Test Stencil (write first)

```python
@pytest.mark.parametrize("knowledge", ["archived", "undecodable", "missing"])
def test_empty_list_approves_without_touching_knowledge(self, tmp_path, knowledge):
    k_path = tmp_path / "knowledge" / "KNOWLEDGE.md"
    if knowledge == "archived":
        _write_archived_knowledge(tmp_path)  # a read would warn about DI-014
    elif knowledge == "undecodable":
        k_path.parent.mkdir(parents=True)
        k_path.write_bytes(b"\xff\xfe# not utf-8\x80")  # a read would raise
    before = k_path.read_bytes() if k_path.exists() else None
    doc = _pending_doc(tmp_path)

    result = approve_research(tmp_path, pending_file=str(doc), insights=[])

    approved = tmp_path / "knowledge" / "research" / "approved" / doc.name
    assert result.success
    assert result.message == f"Approved research: {doc.name}. No insights created"
    assert (result.ids_assigned, result.warnings) == ({}, [])
    assert result.files_modified == [str(approved)]
    assert not doc.exists() and approved.read_text(encoding="utf-8") == "# Research\n"
    assert (k_path.read_bytes() if k_path.exists() else None) == before
```

### Setup gotchas for the tests

- **Test 5a needs `pending/` to exist.** The kernel resolves `pending/../../KNOWLEDGE.md` one segment at a time, so a missing `pending/` makes today's code fail at `File not found` instead of reproducing the real defect. Create the directory, use `_setup_knowledge`, and snapshot `KNOWLEDGE.md` bytes.
- **Test 5b must use a relative `pending_file`.** Pass a `project_root` like `tmp_path / "proj" / "sub" / ".."` (create `sub`) with `pending_file="knowledge/research/pending/<doc>"`. This is the case that breaks if D5 normalizes only the file path and not `pending_dir`.
- **Test 8 runs in the project root.** Create `work/BACKLOG.md`, `monkeypatch.chdir(root)`, set `sys.argv` as `tests/test_cli.py:316-339` does, and pass the document path relative to the root. The operation joins relative paths to the project root, not the working directory (`operations.py:917-919`), so running from the root keeps both readings the same. Do not create `KNOWLEDGE.md`; assert it is still absent afterwards.
- **Test 9 asserts on `SystemExit`.** argparse raises it inside `parse_args`, so use `pytest.raises(SystemExit)` and check `.code == 2` and that stderr names `--insights`.
- **"Nothing moved" checks** in tests 2, 4, 5a, 6, 9, 10, 11: document (or queue) still in `pending/`, `approved/` not created, `KNOWLEDGE.md` bytes unchanged.

### Step 1: write tests 1-11, run them, record red/green

- [ ] Write tests 1-11 per the [design table](design.md#validation-approach) and the names above.
- [ ] Run `uv run pytest tests/test_pm_operations.py::TestApproveResearch tests/test_pm_cli.py::TestPmApproveResearchMain -v` against unchanged `src/`.
- [ ] Record the result in Implementation Notes below: each failing test ID and its one-line failure, and the list of tests that passed.
- [ ] **Stop condition.** If an expected-red test passes, or fails for a different reason than listed, the test is not exercising the change. Fix the test before touching `src/`.

Expected result against current code (`2a229f4`):

| # | Expected | Expected failure against current code |
|---|----------|----------------------------------------|
| 1 (all 3) | red | `assert result.success` fails; message is `No insights provided` (the empty-list guard at `operations.py:936`) |
| 2 `none` | red | message `No insights provided` does not contain `pass []` |
| 2 `json_string` | red | `AttributeError: 'str' object has no attribute 'title'` from the build loop (`"[]"` is truthy, so the guard passes it) |
| 3 | green | pin: Python already raises `TypeError` |
| 4 `empty` | red | message is `No insights provided`, not `Not a regular file...` |
| 4 `one` | red | `assert not result.success` fails; today the whole queue moves to `approved/pending/` and DI-001 is minted |
| 5a `empty` | red | message is `No insights provided`, not `... is not in ...` |
| 5a `one` | red | `assert not result.success` fails; today DI-001 is appended and `KNOWLEDGE.md` itself moves into `approved/` |
| 5b | green | guard for D5's "normalize both sides" |
| 6 (all 4) | green | pin: containment and exists checks already run before the guard |
| 7 | green | pin for I5: message and `files_modified` order are already as asserted |
| 8 | red | returns `1`, stdout `No insights provided` |
| 9, 10 | green | pins: argparse and `_validate_json_list` already exit 2 |
| 11 | green | pin for I1: the blank-field refusal already returns before the first append |

### Step 2: change the operation

**See** [Key Decisions D1-D5](design.md#key-decisions), [Architecture](design.md#architecture), and [Implementation Notes](design.md#implementation-notes) for the check order, the gate comment, the zero-path initialization, `files_modified` construction, and the exact messages.

- [ ] `src/agentic_mbse/pm/operations.py:11-16`: add `import os`.
- [ ] `src/agentic_mbse/pm/operations.py:910-1000` (`approve_research`): apply D5 normalization, the D4 `is_file()` refusal, the D2 type check in place of the guard at `:936-940`, the D1 gate around the registry read at `:943-946`, and the D3 message and derived `files_modified`. Keep exactly one `shutil.move` (I2).
- [ ] Update the docstring: an empty list approves with no insights; `None` is refused.

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_pm_operations.py tests/test_pm_cli.py` → all pass, including every test that was red in Step 1.
- [ ] `uv run pytest tests/` → no regressions (default selection).
- [ ] `uv run ruff check src/ tests/` and `uv run ruff format --check src/ tests/` → clean.
- [ ] `uv run mypy src/` → clean.

**Manual:**
- [ ] Read the final `approve_research`: the check order matches [Implementation Notes](design.md#implementation-notes), the gate carries its comment, and there is one move statement and no second result-building branch (I2, I6).

**What we know works after this phase:** both surfaces approve with `[]` and leave `KNOWLEDGE.md` alone in all three states; omission and non-lists are refused; a non-file or escaping path is refused before any write; non-empty approval output is unchanged.

---

## Phase 2: Shipped text, help strings, tracking

### Goal

Agents running `/research` know to call the operation when every insight is skipped, and the help and skill text stop implying insights are always registered (SC6).

### Assumption Under Test

Bet B2 ([Key Bets](design.md#key-bets)): one explicit sentence in the approval step is enough for an agent to route "approved, all skipped" to `--insights '[]'`. No automated test pins this text (design, Research Findings). The check is a diff read against the design's exact wording.

### Test Stencil

No new test. The help-string edit is covered by the existing help-text subprocess tests continuing to pass; nothing pins the old strings (checked: no test contains `extract insights` or `InsightInput objects`). Before editing, re-run `uv run pytest tests/test_pm_cli.py -k help` to have a green baseline.

### Changes Required

Use the exact text in [Implementation Notes](design.md#implementation-notes). Do not paraphrase.

- [ ] `src/agentic_mbse/cli/pm_cli.py:560`: subcommand help string.
- [ ] `src/agentic_mbse/cli/pm_cli.py:562`: `--insights` help string.
- [ ] `claude/commands/research.md`: add the one line after `:79`; lines `75-79` unchanged.
- [ ] `claude/skills/toolkit-awareness/SKILL.md:90`: replace the description cell only.

No change coordination is needed: no file is added or renamed, and both shipped files are already tool-owned in the init lists and `scripts/replicate_setup.sh` (design, Research Findings).

### Validation

**Automated:**
- [ ] `uv run pytest tests/` → green.
- [ ] `uv run ruff check src/ tests/`, `uv run ruff format --check src/ tests/`, `uv run mypy src/` → clean.

**Manual:**
- [ ] `git diff claude/ src/agentic_mbse/cli/pm_cli.py` matches the design's exact text character for character (SC6).
- [ ] `uv run agentic-mbse pm approve-research --help` shows both new help strings.

### Final step: tracking (leave `close` to the owner)

- [ ] `.project/CURRENT_WORK.md`: update the `research-approval-empty-insights` line under Active Work and the `Research approval` row in the remaining-work table to say implemented on the branch, all gates green, audit next.
- [ ] `.project/backlog/BACKLOG.md:81`: update the `PM-APPROVE-RESEARCH-EMPTY-INSIGHTS` **Status** line to the same state.
- [ ] Set this plan's **Status** to Complete and fill in Implementation Notes.

**What we know works after this phase:** the repair reaches users through `/research` on their next `agentic-mbse init`, and tracking shows the item is ready for audit.

---

## Invariant coverage

Every invariant in [Required Invariants](design.md#required-invariants) maps to named tests.

| Invariant | Tests | Notes |
|-----------|-------|-------|
| I1. Refuse before any write | 2, 4, 5a, 6, 11 | each asserts nothing moved, `approved/` absent, `KNOWLEDGE.md` unchanged; 11 covers the build-loop refusal |
| I2. One move | 1, 7 | both list sizes reach `approved/`; that it is one statement is checked by the Phase 1 manual code read |
| I3. Zero insights never touches `KNOWLEDGE.md` | 1 (all three states), 8 | the undecodable case fails if anything reads the file; the archived case fails on a stray warning |
| I4. Absence is not emptiness | 2, 3, 9, 10 | Python `None`/string and CLI omission/`null` |
| I5. Non-empty output unchanged | 7, plus existing `test_mints_above_archive_note` | exact message and `files_modified` order |
| I6. Result is derived | 1, 7 | exact `files_modified`, `ids_assigned`, and message on both sizes |

## Risk Management

See [Potential Risks](design.md#potential-risks). Phase-specific:

- **Phase 1: a test passes for the wrong reason.** Mitigated by the Step 1 red/green table and its stop condition.
- **Phase 1: half-applied D5.** Test 5b fails if only one side of the containment comparison is normalized.
- **Phase 2: wording drift.** Mitigated by copying from the design and checking the diff character for character.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:**
**Red-before-green evidence (Step 1, against `2a229f4`):** failing test IDs with one-line failure; passing test IDs.
**Actual changes:**
**Issues:**
**Deviations:**

### Phase 2 Completion
**Completed:**
**Actual changes:**
**Issues:**
**Deviations:**

---

**Status**: Draft → In Progress → Complete
