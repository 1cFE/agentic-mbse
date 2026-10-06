# Brief: audit — research-approval-empty-insights

**Sent:** 2026-10-05 by the orchestrator. **Stage:** `/_my_audit`, fresh session. **Item:** `.project/active/research-approval-empty-insights/` (`spec.md`, `spec-review.md`, `design.md`, `plan.md`, `briefs/`). **Code under audit:** the implementation commit at `HEAD` on branch `research-approval-empty-insights`, against base `c37ff53` (`git diff c37ff53..HEAD -- src tests claude`).

## What this work is for

[AGENT, re-derived] Research approved with no new insight goes through the supported operation, so nobody moves the file by hand. The shipped `/research` instruction is part of the repair: it is how an agent learns to pass `--insights '[]'`. Certify against that outcome and the spec's seven criteria, not against "the tests pass."

## Rulings the audit should know

- [OWNER] (2026-10-05) No reserved gates; the orchestrator decides and records. Stage subagents run on Opus 5.5.
- [AGENT] (orchestrator) Two scope additions beyond the backlog item, both recorded: a pending path that is not a regular file is refused (spec-review resolution L3-4 (c)), and a path that leaves `pending/` once `..` is collapsed is refused (design D5, spec criterion 4 amended). Both are agent-grade and challengeable: if either is wrong on the evidence, say so.
- [AGENT] No design review was run. The design's one non-obvious decision (D5) was ruled by the orchestrator. Treat the design with the skepticism a missing review warrants.
- Every spec criterion is `[INHERITED]` or `[INFERRED]`. None is owner-stated.

## What the implementer reported (verify, do not trust)

- New and changed tests: 10 failed and 11 passed against unchanged `src/`, as the plan predicted, with each failure message recorded in `plan.md`. Six deliberate breaks of the new code were each caught by a test.
- Gates after the change: `uv run pytest tests/` 2073 passed, 1 skipped, 33 deselected (2056 before). `uv run ruff check src/ tests/` 118 errors, `uv run ruff format --check src/ tests/` 78 files would be reformatted, `uv run mypy src/` 91 errors in 19 files. The implementer says those three counts are identical on unchanged code and none of the new complaints is in a touched file. Check that claim directly (for example with `git stash` or a worktree at `c37ff53`), since a pre-existing red gate can hide a new error.
- Deviations: `research.md` gained a blank line plus the design's sentence; a new test helper `_tree_state`; some assertions tightened to exact messages; `active/README.md` status updated.

## What the orchestrator checked itself (2026-10-05, on the working tree now committed)

- `tests/test_pm_operations.py` and `tests/test_pm_cli.py`: 220 passed.
- Real CLI in a scratch project (`uv run agentic-mbse pm approve-research ...`): the `pending/` directory with `[]` exits 1 with `Not a regular file`; `pending/../../KNOWLEDGE.md` with `[]` exits 1 with `is not in`; a missing `--insights` exits 2; `--insights null` exits 2; a real pending file with `[]` exits 0 with `Approved research: a.md. No insights created`, the file is in `approved/`, the other pending file is untouched, and `KNOWLEDGE.md` has the same SHA-1 before and after.
- fusion-tea (a sibling repo you cannot read) does not call `approve-research` from code or parse its message.

## Points I want the audit to attack

- **Criteria coverage.** For each of the seven spec criteria, name the test or evidence that would fail if the criterion were violated. Mutate the source yourself where the mapping is doubtful.
- **Engineering quality of `approve_research`** (`src/agentic_mbse/pm/operations.py:911`). Is it one clear path, or has the function become hard to read? Is the `os.path.normpath` use correct on both sides, and does anything downstream (the move destination, `files_modified`, messages) now disagree between normalized and unnormalized paths? Is the `isinstance(insights, list)` check too strict for any existing caller in `src/` or `tests/`?
- **Regression in the non-empty path.** Message, `files_modified` order, IDs, and warnings must be unchanged. Refusal messages for existing cases now print a normalized path; say whether that matters to any test or doc.
- **Symlinks.** `is_file()` follows symlinks and `normpath` does not resolve them. State what happens for a symlink in `pending/` and whether that is a behavior change from `c37ff53`.
- **The shipped text.** Read `claude/commands/research.md` around the approval step as an agent would. Does the paragraph above the new sentence ("assigns DI-XXX IDs ... Report the assigned IDs to the user") still read correctly beside it, or do the two now pull in different directions? Does the toolkit-awareness row read cleanly? Check that no other shipped file (`claude/`, `project_templates/`, `docs/`, `scripts/replicate_setup.sh`) still describes the command as requiring at least one insight.
- **Test quality.** Real temp projects for on-disk claims; no assertion that passes vacuously; parametrization rather than copies; the `_tree_state` helper earns its place.
- **Leftovers.** TODOs, placeholder code, commented-out code, unrelated edits, tracking files that overclaim.

## Boundaries

- Do not fix findings. Write them to the audit artifact with severity and evidence.
- Do not touch or commit `.project/research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md`; it is from another session.
- Do not run `close` or `pre_pr`. If you stash or use a worktree to check the baseline, restore the tree exactly and say so.

Finish with the verdict and `ARTIFACT: <path>`.
