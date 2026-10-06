# Implementation Plan: Approve Research with No New Insights

**Status:** Complete. Implemented 2026-10-05 at `b6d1667`; [audit](audit.md) fixes A1, A3, A4, A6 applied the same day (see Audit fixes).
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

- [x] Write tests 1-11 per the [design table](design.md#validation-approach) and the names above.
- [x] Run `uv run pytest tests/test_pm_operations.py::TestApproveResearch tests/test_pm_cli.py::TestPmApproveResearchMain -v` against unchanged `src/`.
- [x] Record the result in Implementation Notes below: each failing test ID and its one-line failure, and the list of tests that passed.
- [x] **Stop condition.** If an expected-red test passes, or fails for a different reason than listed, the test is not exercising the change. Fix the test before touching `src/`.

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

- [x] `src/agentic_mbse/pm/operations.py:11-16`: add `import os`.
- [x] `src/agentic_mbse/pm/operations.py:910-1000` (`approve_research`): apply D5 normalization, the D4 `is_file()` refusal, the D2 type check in place of the guard at `:936-940`, the D1 gate around the registry read at `:943-946`, and the D3 message and derived `files_modified`. Keep exactly one `shutil.move` (I2).
- [x] Update the docstring: an empty list approves with no insights; `None` is refused.

### Validation

**Automated:**
- [x] `uv run pytest tests/test_pm_operations.py tests/test_pm_cli.py` → all pass, including every test that was red in Step 1.
- [x] `uv run pytest tests/` → no regressions (default selection).
- [x] `uv run ruff check src/ tests/` and `uv run ruff format --check src/ tests/` → clean for every file this item touches; both gates were already failing repo-wide before this item (see Phase 1 Completion).
- [x] `uv run mypy src/` → no errors in files this item touches; the gate was already failing repo-wide before this item (see Phase 1 Completion).

**Manual:**
- [x] Read the final `approve_research`: the check order matches [Implementation Notes](design.md#implementation-notes), the gate carries its comment, and there is one move statement and no second result-building branch (I2, I6).

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

- [x] `src/agentic_mbse/cli/pm_cli.py:560`: subcommand help string.
- [x] `src/agentic_mbse/cli/pm_cli.py:562`: `--insights` help string.
- [x] `claude/commands/research.md`: add the one line after `:79`; lines `75-79` unchanged.
- [x] `claude/skills/toolkit-awareness/SKILL.md:90`: replace the description cell only.

No change coordination is needed: no file is added or renamed, and both shipped files are already tool-owned in the init lists and `scripts/replicate_setup.sh` (design, Research Findings).

### Validation

**Automated:**
- [x] `uv run pytest tests/` → green.
- [x] `uv run ruff check src/ tests/`, `uv run ruff format --check src/ tests/`, `uv run mypy src/` → clean for every file this item touches; all three were already failing repo-wide before this item, with unchanged counts (see Phase 2 Completion).

**Manual:**
- [x] `git diff claude/ src/agentic_mbse/cli/pm_cli.py` matches the design's exact text character for character (SC6).
- [x] `uv run agentic-mbse pm approve-research --help` shows both new help strings.

### Final step: tracking (leave `close` to the owner)

- [x] `.project/CURRENT_WORK.md`: update the `research-approval-empty-insights` line under Active Work and the `Research approval` row in the remaining-work table to say implemented on the branch, all gates green, audit next.
- [x] `.project/backlog/BACKLOG.md:81`: update the `PM-APPROVE-RESEARCH-EMPTY-INSIGHTS` **Status** line to the same state.
- [x] Set this plan's **Status** to Complete and fill in Implementation Notes.

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

### Phase 1 Completion

**Completed:** 2026-10-05.

**Red-before-green evidence (Step 1, against unchanged `src/`).** `git diff --quiet src/` was clean, and `src/` at `c7014a8` equals `2a229f4` (`git diff --stat 2a229f4 HEAD` touches only this folder). Run: `uv run pytest tests/test_pm_operations.py::TestApproveResearch tests/test_pm_cli.py::TestPmApproveResearchMain -v` → 10 failed, 11 passed.

Failed, each for the reason the plan predicted:

- `test_empty_list_approves_without_touching_knowledge[archived]`, `[undecodable]`, `[missing]`: `assert False` where `False = OperationResult(success=False, message='No insights provided', ids_assigned={}, files_modified=[], warnings=[]).success`.
- `test_non_list_insights_refused[none]`: `assert 'No insights provided' == 'Insights must be a list of InsightInput, got NoneType; pass [] to approve with no insights'`.
- `test_non_list_insights_refused[json_string]`: `AttributeError: 'str' object has no attribute 'source'`. The plan predicted `'title'`. `str` has a `.title` method, so the first field lookup in the build loop succeeds and the second fails. The cause is the one the plan named: the truthy string gets past the guard into the build loop. The test is valid as written.
- `test_pending_directory_refused[empty]`: `assert 'No insights provided' == 'Not a regular file: <tmp>/knowledge/research/pending; name one research document in <tmp>/knowledge/research/pending'`.
- `test_pending_directory_refused[one]`: `AssertionError: assert not True`. A side probe of the same call shows today's effect: message `Approved research: pending. Created insights: DI-001`; files afterwards `knowledge/KNOWLEDGE.md` (with DI-001) and `knowledge/research/approved/pending/20260202-120000_r.md`.
- `test_dotdot_escape_refused[empty]`: `assert 'No insights provided' == "File '<tmp>/knowledge/KNOWLEDGE.md' is not in <tmp>/knowledge/research/pending"`.
- `test_dotdot_escape_refused[one]`: `AssertionError: assert not True`. Side probe: message `Approved research: KNOWLEDGE.md. Created insights: DI-001`; `KNOWLEDGE.md` now sits at `knowledge/research/approved/KNOWLEDGE.md` and the pending document is untouched.
- `TestPmApproveResearchMain::test_empty_insights_approves`: `assert 1 == 0` where `1 = main()`; captured stdout `No insights provided`.

Passed, as the plan expected (pins and guards): `test_happy_path` (now asserting the exact message and `files_modified` order), `test_file_not_in_pending[empty]`, `[one]`, `test_missing_file[empty]`, `[one]`, `test_mints_above_archive_note`, `test_insights_argument_is_required`, `test_project_root_with_dotdot_approves`, `test_blank_field_refused_before_any_write`, `TestPmApproveResearchMain::test_missing_insights_is_usage_error`, `test_null_insights_is_usage_error`.
**Actual changes:**
- `src/agentic_mbse/pm/operations.py`: added `import os`. In `approve_research`: `os.path.normpath` on both the joined pending path and `pending_dir` before `relative_to` (D5); an `is_file()` refusal after the exists check (D4); `isinstance(insights, list)` in place of the `if not insights` guard (D2); `all_ids` and `warnings` start empty and the `KNOWLEDGE.md` read runs under `if insights:`, with a comment that the test is safe only after the list check (D1); the message clause and `files_modified` are derived from `ids_assigned` and `entries` (D3, I6). One `shutil.move`, one `OperationResult(success=True, ...)`. Docstring states the empty-list and `None` behavior.
- `tests/test_pm_operations.py`: helpers `_pending_doc`, `_one_insight`, `_tree_state`, and the shared mark `_LIST_SIZES` (ids `empty`, `one`) above `TestApproveResearch`. `test_happy_path` now pins the exact message and `files_modified` order. `test_file_not_in_pending` and `test_missing_file` are parametrized over `_LIST_SIZES` and assert their refusal message and an unchanged tree. Added tests 1-5b and 11 under the plan's names.
- `tests/test_pm_cli.py`: `import pytest`; helper `_make_research_project`; class `TestPmApproveResearchMain` with tests 8-10 calling `main()` through a monkeypatched `sys.argv` in a real temp project.

**Gates after the change.** `uv run pytest tests/`: 2073 passed, 1 skipped, 33 deselected (baseline 2056 passed + 17 new cases). The other three gates were already failing before this item, with identical counts before and after:

| Gate | Baseline (unchanged `src/`, `c7014a8` = `2a229f4` for `src/`) | After Phase 1 | Files this item touches |
|------|------|------|------|
| `uv run ruff check src/ tests/` | `Found 118 errors.` | `Found 118 errors.` | `All checks passed!` |
| `uv run ruff format --check src/ tests/` | `78 files would be reformatted, 77 files already formatted` | same | `operations.py` and `test_pm_operations.py` each carry one pre-existing hunk (`operations.py:219` in the backlog renderer, `test_pm_operations.py:2533`, now `:2666`); the `+`/`-` lines of `ruff format --diff` on both files are identical before and after. `pm_cli.py` and `test_pm_cli.py` are formatted. |
| `uv run mypy src/` | `Found 91 errors in 19 files (checked 60 source files)` | same | no error in `pm/operations.py` or `cli/pm_cli.py` |

**Mutation check (extra, not in the plan).** Each mutation of the new code was applied alone, then `TestApproveResearch` and `TestPmApproveResearchMain` were run and the file restored. All caught: gate removed (always read `KNOWLEDGE.md`) → test 1 (all three) and test 8; only the file path normalized → 5b; no file-path normalization → 5a (both) and 5b; `is_file` check removed → test 4 (both); type check removed → test 2 (both); `KNOWLEDGE.md` always in `files_modified` → test 1 (all three).

**Issues:**
- The plan predicted `AttributeError ... 'title'` for test 2 `json_string`; the actual error names `'source'`. Explained in the red evidence above; same cause.
- The `Not a regular file` f-string ran to 103 columns on one line (project limit 100). It is wrapped in parentheses as the formatter lays it out, matching the type-check message beside it. Message text is the design's, unchanged.

**Deviations:**
- `_tree_state` is a new helper beside the existing `_file_bytes`. `_file_bytes` sees only files, so it cannot show that a refusal created no `approved/` directory (I1 names the mkdir). `_tree_state` adds directories, so one equality covers "document still pending, `approved/` not created, `KNOWLEDGE.md` unchanged or still absent" for every refusal test, including `test_file_not_in_pending`, where `approved/` exists by setup.
- Tests 2, 4, and 5a assert the design's exact messages rather than the plan's "contains `pass []`" / "starts with `Not a regular file`" / "`is not in`". This is stricter and pins the design's wording.
- Test 11 uses two insights, a valid one followed by one with a blank `context`, so it shows the first is not appended before the second is refused.

### Phase 2 Completion

**Completed:** 2026-10-05.

**Actual changes:**
- `src/agentic_mbse/cli/pm_cli.py:560-568`: subcommand help `Approve a pending research file and record any insights`; `--insights` help `JSON array of InsightInput objects; '[]' approves with no insights`. Both calls are split across lines as `ruff format` lays them out; the handler is untouched.
- `claude/commands/research.md`: lines 75-79 unchanged; the design's sentence added as its own paragraph after line 79.
- `claude/skills/toolkit-awareness/SKILL.md:90`: description cell replaced with the design's text.
- Tracking: `CURRENT_WORK.md` (Active Work line and the `Research approval` row), `backlog/BACKLOG.md:81`, this spec's **Status** line, and the `research-approval-empty-insights` row in `active/README.md`.

**Verification.**
- Help baseline before the edit: `uv run pytest tests/test_pm_cli.py -k help` → 3 passed. Before the edit, `grep` found the old help strings and skill text only in `pm_cli.py:560`, `:562`, and `SKILL.md:90`, and no other copy of the shipped `research.md` or skill text outside `.project/`.
- A script pulled the four strings out of design.md (the `research.md` line, the `SKILL.md` cell, both help strings) and found each exactly once in its target file. It found the operation messages in `operations.py` the same way. `git diff 2a229f4 -- claude/commands/research.md` shows 2 insertions and no deletions.
- `uv run agentic-mbse pm approve-research --help` prints the new `--insights` help, and `uv run agentic-mbse pm --help` prints the new subcommand help (both wrapped by argparse at terminal width).
- Gates: `uv run pytest tests/` → 2073 passed, 1 skipped, 33 deselected. `ruff check src/ tests/` → `Found 118 errors.`; `ruff format --check src/ tests/` → `78 files would be reformatted, 77 files already formatted`; `mypy src/` → `Found 91 errors in 19 files (checked 60 source files)`. All three counts equal the pre-change baseline. `ruff check` passes on all four touched Python files, `mypy` reports nothing in `pm/operations.py` or `cli/pm_cli.py`, and the only `ruff format` hunks in touched files are the two pre-existing ones from Phase 1 (identical `+`/`-` lines).

**Issues:** none.

**Deviations:**
- `research.md` gains a blank line before the new sentence, so the change adds two source lines, not one. Without it, Markdown joins the sentence into line 79's paragraph. That would make one paragraph span two source lines, which the owner's markdown rule (one line per paragraph) forbids. With it, the sentence is its own paragraph, like the `If the user rejects the report` paragraph below it. The sentence is the design's text, character for character.
- `active/README.md` was not in the plan's tracking list. Its row still said "implementation not started", so it was updated with the other status lines.

### Audit fixes

**Completed:** 2026-10-05, as a resume of the implement session per [briefs/implement_audit_fixes.md](briefs/implement_audit_fixes.md). Input: [audit.md](audit.md), verdict Certify, advisories A1-A6. Rulings: fix A1, A3, A4, A6; record A2 and A5.

**A1. The document is now taken from and moved within the project the OS resolves.**
- *Problem, reproduced at `HEAD` (`d6ea9fc`; `src/` equals `b6d1667`).* Project root `text_proj/link/..`, where `link` points to `os_proj/target`. The OS reads it as `os_proj`; `os.path.normpath` reads it as `text_proj`. Both hold `knowledge/research/pending/20260202-120000_r.md`. With `[]` and with one insight, `text_proj`'s document landed in `os_proj/knowledge/research/approved/`, `os_proj`'s document stayed pending, and the one-insight call wrote DI-001 to `os_proj`'s `KNOWLEDGE.md`.
- *Change, the orchestrator's shape.* New private helper `_path_below(path, base)` in `src/agentic_mbse/pm/operations.py` (after `_append_csv_row`). It returns the part of `path` below `base` with `..` collapsed, or `None` if `path` is not textually under `base` or the collapsed part starts with `..`. `approve_research` builds `pending_dir` from the root as given, refuses with the existing `File '...' is not in ...` message when the helper returns `None`, and rebuilds the document path as `pending_dir / below`. That one path serves the exists check, the regular-file check, and the move. `KNOWLEDGE.md` and `approved/` are built from the same root as given, as at the base. One move and one result remain.
- *Visible change from `b6d1667`.* The "is not in" refusal for a `..` escape now names the path as the caller gave it (`<root>/knowledge/research/pending/../../KNOWLEDGE.md`), not a textually collapsed target. A textual target can be wrong once a symlink precedes `..`, which is what the audit found. For a path without `..` the message is byte-identical to the base.
- *One call this shape refuses that `b6d1667` accepted.* Probed at `c37ff53`, `HEAD`, and the fix: root `proj/sub/..` (no symlink) with an absolute document path `proj/knowledge/research/pending/<doc>`. `c37ff53` refuses (`is not in`), `HEAD` approved it, and the fix refuses as the base did. Matching two spellings of one directory would need symlink resolution, which D5 rejects. No shipped surface produces it: the CLI root comes from `Path.cwd()`. I judged this a consequence of the ruled shape, not a case where the shape is wrong, and recorded it in D5. The same probe confirmed that a symlink to a directory given as the document is still refused (`Not a regular file`) and that `c37ff53` approved it.
- *Tests.*
  - New `test_symlinked_root_with_dotdot_stays_in_os_project[empty, one]`, the audit's probe. It asserts its own premise (`os.path.samefile(root, os_proj)`, `normpath(root) == text_proj`), then that `os_proj`'s document moved into `os_proj/approved/`, `files_modified[-1]` is that file, `os_proj`'s `KNOWLEDGE.md` holds as many records as insights passed, and `text_proj`'s whole tree is unchanged.
  - Test 5a's expected message now names the path as given. It is parametrized over two escape spellings (`leading`: `pending/../../KNOWLEDGE.md`; `behind_subdir`: `pending/sub/../../../KNOWLEDGE.md`, with `sub` existing). The second spelling catches a version that checks only the first segment for `..` without collapsing.
  - Test 5b is unchanged and still meaningful. A root containing `..` with a relative document path must approve, and it fails if the full document path is normalized while `pending_dir` is not.
  - New `test_dotdot_inside_pending_approves` pins the design's claim that `pending/sub/../doc.md` still works. Not in the brief; added because no test held that claim.
- *Red against `HEAD`.* Run with `HEAD`'s `src/` (`git diff --quiet src/` clean, and `git diff --quiet b6d1667 HEAD -- src/`): 6 failed, 21 passed. Failures: `test_symlinked_root_with_dotdot_stays_in_os_project[empty]` and `[one]`, `AssertionError: assert not True` where `True = (os_proj/knowledge/research/pending/20260202-120000_r.md).exists()`; `test_dotdot_escape_refused[leading-empty]`, `[leading-one]`, `[behind_subdir-empty]`, `[behind_subdir-one]`, message mismatch, `HEAD` printing `File '<tmp>/knowledge/KNOWLEDGE.md' is not in ...` where the test expects the path as given. `test_dotdot_inside_pending_approves` and the A3 test passed at `HEAD`, as pins of existing behavior.

**A3. Non-empty warnings are pinned.** New `test_non_empty_approval_returns_registry_warnings`. `KNOWLEDGE.md` holds a valid DI-001 and a DI-002 with status `bogus`, so the parser warns once (`Invalid Status 'bogus'...`) and the registry read warns once (`DI-002 ... its ID stays reserved`). A one-insight approval mints DI-003 and must return the parser's warnings first, then one reservation warning located at DI-002 in `KNOWLEDGE.md`. The pattern follows `test_reports_reserved_id_after_parse_warnings`.

**Mutation check of the fixes.** Each mutation applied alone, `TestApproveResearch` and `TestPmApproveResearchMain` run, file restored (`cmp` against a saved copy). All caught:
- The audit's suggested fix (normalize the root once and use it everywhere) → the A1 test, both sizes.
- No collapse below `pending/` → 5a `behind_subdir`, both sizes.
- No climb-out refusal → 5a, all four.
- Refuse every `..` → 5b, the A1 test, and `test_dotdot_inside_pending_approves`.
- Drop all warnings / only parse warnings / only reservation warnings (the audit's three survivors) → the A3 test, each time.

**A4.** `claude/commands/research.md:81` and the design's Implementation Notes now carry the orchestrator's sentence: "If the user approves the report with no accepted insights (every candidate skipped, or none proposed), still make the call, ...". The paragraph stays separate from line 79.

**A6.** This plan's **Status** line no longer says uncommitted. The backlog Problem of `PM-APPROVE-RESEARCH-EMPTY-INSIGHTS` now points at `operations.py:936-940` at `c37ff53` (checked with `git show`), not the stale `:664-668`.

**A2 and A5, recorded.**
- `PM-APPROVE-RESEARCH-MOVE-SAFETY` gains case (c), symlinks inside `pending/`. It cites the audit's probe and records the tightening that a symlink to a directory given as the document is now refused. Case (b) gains the A5 sentence.
- The item's closing line now says this item causes none of the three gaps but makes (b) and (c) cheaper. The old "Neither gap is made worse" was no longer true once A2 and A5 were recorded. Its title, Status, Source, and Goal now name (c). Its `operations.py:910` and `:983-991` pointers are base line numbers, so they now say "at `c37ff53`".
- Design Potential Risks gains one line for A2.

**Design amendments.** D5 now describes the shape built, with one line recording that the first form normalized both full paths and why A1 showed that was wrong. It adds a rejected-alternative note for the audit's normalize-the-root suggestion (orchestrator ruling) and the refused-absolute-path consequence above. The Architecture sketch, the check-order note, and the Component Overview line for `research.md` were updated to match, and the Status line records the amendment.

**Gates after the fixes.** `uv run pytest tests/`: 2079 passed, 1 skipped, 33 deselected (2073 + 6 new cases). `uv run ruff check src/ tests/`: `Found 118 errors.` `uv run ruff format --check src/ tests/`: `78 files would be reformatted, 77 files already formatted`. `uv run mypy src/`: `Found 91 errors in 19 files (checked 60 source files)`. All three equal the pre-item baseline. `ruff check` passes on the four touched Python files. `mypy` reports nothing in `pm/operations.py` or `cli/pm_cli.py`. The only `ruff format` hunks in touched files are the two pre-existing ones, with `+`/`-` lines identical to the baseline.

**Not changed:** tracking status lines in `CURRENT_WORK.md`, `active/README.md`, the backlog **Status** of `PM-APPROVE-RESEARCH-EMPTY-INSIGHTS`, and the spec's **Status**. They say certified and close next, which still holds.

---

**Status**: Complete
