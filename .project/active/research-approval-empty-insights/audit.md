# Audit: Approve Research with No New Insights

**Verdict:** Certify
**Audited:** 2026-10-05
**Branch:** research-approval-empty-insights
**Commit:** b6d1667 (base c37ff53)

---

## The Point

[INHERITED: backlog PM-APPROVE-RESEARCH-EMPTY-INSIGHTS] Research is sometimes approved without producing a new domain insight: a source-registration round, a bounded negative result, a confirmation of what is already known. Before this change, `approve-research` refused an explicit empty insight list with `No insights provided`. The document stayed in `knowledge/research/pending/`, and operators moved it by hand, bypassing the supported operation.

[INHERITED: product-lens.md] `/research` asks the user two separate things: approve the report, and accept or skip each insight. Only accepted insights enter `KNOWLEDGE.md`. The repair has failed if a user approves a useful report while skipping every insight and approval is refused, the report stays pending, or an unaccepted insight enters `KNOWLEDGE.md`.

[AGENT, from the brief] Users reach the operation only through the shipped `/research` command, so the sentence added there is part of the repair. It is how an agent learns to pass `--insights '[]'`.

## Summary

The repair works on both surfaces. `--insights '[]'` approves and moves the document, never reads or writes `KNOWLEDGE.md`, and reports "No insights created". Omission and `null` stay usage errors, and non-empty output is byte-identical to the base for ordinary inputs. The shipped `/research` step tells agents to make the call.

There are no blockers. The main advisory is that the D5 path fix normalizes only two of the four paths the function uses. With a project root that contains a symlink followed by `..`, the document is taken from one directory tree and moved into another. No shipped surface can produce such a root, but it is a regression in the public Python API that a one-line change would remove.

## Product Judgment

**This is the right piece of work.** It restores what the original operations contract always allowed (FR-9 sets no minimum insight count) and removes the reason operators moved files by hand. The fix reaches users through the `/research` instruction, not only through the operation.

- **Product-lens (audit stage, appended to [product-lens.md](product-lens.md)): Gate DISPOSED.** Its one finding (audit-F1, a `[DO]` finding) is the silent overwrite of a same-name file in `approved/`. Zero-insight approvals make that path more common, but this change neither causes nor worsens the gap. It is already filed as part (b) of `PM-APPROVE-RESEARCH-MOVE-SAFETY`. I agree with the deferral; see A5.
- **Earlier ledger block (spec stage): CLEAR,** nothing open.
- **Structural smells:** none fired. No test passes by choosing one route: the CLI tests drive `main()` through the real parser, root discovery, and operation. The empty list is not a special category. It flows through the same path and differs only where no insight exists to number. No two representations need manual syncing.
- **The two agent-grade scope additions hold up on the evidence.** Refusing a non-regular file (spec-review L3-4 (c)) and refusing a `..` escape (design D5) each block a call that was never valid. Without them, the cheap `[]` call could move the whole pending queue, or move `KNOWLEDGE.md` itself into `approved/`. The plan's red evidence shows both happened at the base with one insight. Neither loses a valid call. D5's execution has a gap (A1), but the decision is right.

## Blockers

None.

## Advisory

Ranked by importance.

**A1. The `..` fix normalizes only some of the paths, so a symlinked root can split the work across two directory trees.** `src/agentic_mbse/pm/operations.py:927-928` normalizes the pending path and `pending_dir`. `k_path` (`:963`) and `approved_dir` (`:1011`) are still built from the raw `project_root`. `os.path.normpath` collapses `..` as text, while the OS resolves `link/..` to the symlink target's parent. The two can then disagree.
- *Probe:* `project_root = A/link/..`, where `link` points to `X/Y`. The OS reads this as `X`; `normpath` reads it as `A`. At HEAD, both `[]` and one insight moved **A's** pending document into **X's** `approved/`, and the one-insight call wrote DI-001 to **X's** `KNOWLEDGE.md`. At c37ff53 the same non-empty call acted on X consistently (X's document, X's registry).
- *Reach:* a regression this change introduced, in the exported Python API (`pm/__init__.py:21`). The CLI cannot reach it, because `find_project_root` starts from `Path.cwd()` (`cli/__init__.py:172`), a physical path with no `..`. No caller in `src/` passes a root with `..`. Test 5b (`tests/test_pm_operations.py:1475`) covers `..` in the root without a symlink, where both readings agree.
- *Cosmetic side of the same gap:* `files_modified` reports unnormalized paths (`.../sub/../knowledge/...`), while refusal messages report normalized ones.
- *What should change:* derive every path in the function from one normalized root, so the containment check and every action see the same tree.

**A2. A symlinked directory inside `pending/` lets `[]` move a file from outside `pending/` into `approved/`, with nothing written to show it happened.** Probe: `pending/sub` → `<root>/outside/`, then `approve-research pending/sub/secret.md` with `[]` succeeds and moves `outside/secret.md` into `approved/`. At the base this needed a non-empty list and left a visible DI. This is the same "removing the guard lowers the barrier" argument that brought the directory case and D5 into scope. It differs in needing someone to have put a symlinked directory inside `pending/` first. The design rejected `Path.resolve()` on purpose (D5), so this is a known consequence rather than a slip, but neither the design nor the backlog records it. *What should change:* add one line to `PM-APPROVE-RESEARCH-MOVE-SAFETY` (or a design note) saying symlinks inside `pending/` are trusted. No code change is needed for certification.

**A3. Nothing pins the warnings on a non-empty approval, though invariant I5 says they are unchanged.** I ran 14 source mutations. Three survived, and all three remove warnings from the non-empty path: drop every warning, drop only the parse warnings, drop only the registry-reservation warnings. The plan's invariant table maps I5 to `test_happy_path` and `test_mints_above_archive_note` (`tests/test_pm_operations.py:1292`, `:1369`), and neither asserts `warnings`. Today the warnings are identical to the base: I compared base and HEAD output on archived, plain, and missing `KNOWLEDGE.md` (see Spec conformance, SC4). The risk is forward-looking. The registry read now sits inside the new `if insights:` gate, the spot a later edit is most likely to touch. Dropping the DI-014 reservation warning that `pm-registry-integrity` just added would then pass the suite. *What should change:* assert the exact warnings in `test_mints_above_archive_note`.

**A4. The new `/research` sentence names "skips every insight" but not "no insight was proposed."** `claude/commands/research.md:81` reads "If the user approves the report but skips every insight, still make the call". The backlog's own motivating cases, a source-registration round and a bounded negative result, are where the agent may propose no candidate at all. An agent that reads the sentence literally may not map "nothing proposed" to "skipped every insight" and may skip the call. That is the bypass this item removes, and it rests on Bet B2. *What should change:* a phrasing that covers both, such as "approves the report with no accepted insights (every candidate skipped, or none proposed)". The paragraph above it (`:79`, "assigns DI-XXX IDs ... Report the assigned IDs to the user") reads correctly as the general rule, with the new paragraph as the stated exception. The two do not pull in different directions.

**A5. Same-name overwrite in `approved/` (product-lens audit-F1).** `shutil.move` at `operations.py:1014` silently replaces an approved document of the same name. The lens reproduced this with `[]`. This change makes approvals cheaper, so the path may run more often. File names carry a timestamp to the second, so a real collision is rare. The gap predates this change and is filed at P3 as `PM-APPROVE-RESEARCH-MOVE-SAFETY` (b). No action for this item.

**A6. Tracking leftovers.** `plan.md:3` still says "uncommitted at hand-off to the orchestrator"; the work is committed at b6d1667. The backlog Problem's `operations.py:664-668` pointer (`.project/backlog/BACKLOG.md`, item `PM-APPROVE-RESEARCH-EMPTY-INSIGHTS`) is still stale, as spec review L1-1 noted. Fix at close.

## Findings Detail

### Plan completion

All phases verified. Phase 1 (tests 1-11 written first, then the operation change) and Phase 2 (help strings, shipped text, tracking) match their checklists.

- **Red-before-green evidence is consistent with the code.** I did not re-run the tests against base `src/`. I re-derived the expected failures from the base code and confirmed several by probe at c37ff53: `[]` gives `No insights provided`; one insight with the `pending/` directory or a `..` path succeeds and mints DI-001. The `'source'` versus `'title'` deviation is explained correctly in the plan (`str.title` exists).
- **No TODOs, placeholders, or commented-out code** in the diff to `src/`, `tests/`, or `claude/`.
- **Deviations are recorded and sound.** The blank line in `research.md` keeps the new sentence its own paragraph. `_tree_state` and the exact-message assertions tighten the tests. The `active/README.md` status update matches the other tracking lines.
- **No unrelated code edits.** The implementation commit's `CURRENT_WORK.md` changes are status lines for this item. The PM-registry-integrity row and the checkout line were updated in the earlier spec-revision commit 9e3a847, and they are accurate (PR #15 merged at c37ff53).

### Spec conformance

For each criterion, the evidence that would fail if it were violated:

- **SC1. `[]` succeeds on both surfaces, moves the document, mints nothing. Verified.** Operation: `test_empty_list_approves_without_touching_knowledge` (`tests/test_pm_operations.py:1393`, three `KNOWLEDGE.md` states). CLI: `test_empty_insights_approves` (`tests/test_pm_cli.py:474`). Mutation "zero path skips the move" was caught. The orchestrator's live CLI run and the product-lens's run in an `init`-created project agree.
- **SC2. `KNOWLEDGE.md` left exactly as found, and success and warnings do not depend on it. Verified.** Test 1 compares bytes in the archived and undecodable cases and checks the file is still absent in the missing case. It also asserts `warnings == []`. Mutation "always read KNOWLEDGE.md" was caught: the archived case gets a DI-014 warning, and the undecodable case raises. Code: the read sits under `if insights:` (`operations.py:966`).
- **SC3. Omission stays a caller error on both surfaces. Verified.** CLI: `test_missing_insights_is_usage_error` (exit 2) and `test_null_insights_is_usage_error` (exit 2), `tests/test_pm_cli.py:492`, `:506`. Malformed JSON and invalid items are still covered by the mocked tests at `tests/test_pm_cli.py:446`, `:453`. Python: `test_insights_argument_is_required` (`TypeError`) and `test_non_list_insights_refused[none]`. Mutation "coerce `None` to `[]`" was caught.
- **SC4. Non-empty behavior retained; existing refusals hold; non-regular files and `..` escapes refused. Verified for every project root without a symlink followed by `..` (see A1).**
  - *Base versus HEAD:* I ran the same non-empty approvals on archived, plain, and missing `KNOWLEDGE.md`, plus the existing refusal cases. Message, IDs, `files_modified`, warnings, resulting `KNOWLEDGE.md` text, and refusal messages are identical.
  - *Refusal paths:* for ordinary paths `normpath` changes nothing, so existing refusal messages print the same path as before. Only a path containing `..` prints differently, and no test or doc pins those messages beyond the new tests.
  - *Tests:* `test_happy_path` pins the exact message and `files_modified` order (mutation "swap order" caught). `test_file_not_in_pending` and `test_missing_file` run for both list sizes (mutation "drop exists check" caught). `test_pending_directory_refused` (mutation "drop `is_file`" caught). `test_dotdot_escape_refused` and `test_project_root_with_dotdot_approves` (mutation "normalize only the file side" caught).
  - *Gap:* warnings are verified by comparison only, not pinned by a test (A3).
- **SC5. Accurate reporting to each observer. Verified.** CLI: test 8 asserts exit 0, the exact stdout `Approved research: 20260202-120000_r.md. No insights created`, and empty stderr. Python: test 1 asserts `ids_assigned == {}` and `files_modified == [approved]`. Mutations "old message format" and "`KNOWLEDGE.md` always in `files_modified`" were both caught.
- **SC6. Shipped text. Verified by reading. No test pins it, as the design states.** `claude/commands/research.md:81` and `claude/skills/toolkit-awareness/SKILL.md:90` match the design's exact wording character for character. The skill row reads cleanly. `git grep` over every tracked file outside `.project/` and `tests/` finds no other description of `approve-research`. `project_templates/`, `docs/`, `scripts/replicate_setup.sh`, and `README.md` have none, so nothing still says an insight is required. Both help strings show in `--help`. A4 is a wording advisory, not a gap against the criterion.
- **SC7. Tests cover explicit `[]` and a missing `--insights`. Verified.** Test 8 asserts the document lands in `approved/` with no DI written. Writing a DI would create `KNOWLEDGE.md`, so its continued absence proves none was written. Test 9 covers the missing flag.
- **Non-goals respected.** The approval gate is unchanged. The move-after-append and overwrite gaps are untouched and filed. Element types in a non-empty list are not checked. The `uv run` prefix in the `research.md` example and `SKILL.md:85` are unchanged.

### Design conformance

The implementation follows the design. D1-D7 are each where the design placed them, in the check order from Implementation Notes: normalize, containment, exists, `is_file`, type check, gated read. The gate carries its comment (`operations.py:960-962`).

- **I1 (refuse before any write):** holds. `test_blank_field_refused_before_any_write` plus `_tree_state` caught the mutation "create `approved/` before the build loop".
- **I2 (one move):** holds. One `shutil.move` (`:1014`).
- **I3 (zero insights never touches `KNOWLEDGE.md`):** holds.
- **I4 (absence is not emptiness):** holds.
- **I5 (non-empty output unchanged):** holds by comparison, not pinned for warnings (A3).
- **I6 (result derived):** holds. The message clause comes from `ids_assigned` and `files_modified` from `entries` (`:1017-1019`).

D5 is the one place the design itself falls short. It reasoned that "both sides need" normalizing for a root with `..`, but left the two action paths unnormalized (A1). The design's rejected-alternative note covers why `resolve()` was not used, which is sound. It does not cover the split this creates.

**Symlinks.** Asked directly by the brief. Probed at c37ff53 and HEAD with both list sizes:

- **Symlink in `pending/` to a regular file**, anywhere, including `KNOWLEDGE.md`: `is_file()` follows it and passes. `shutil.move` moves the link itself, never the target. Non-empty: same as the base. `[]`: newly accepted, which is the intended change. `KNOWLEDGE.md` is never moved.
- **Symlink to a directory:** the base approved it with one insight (moved the link, minted DI-001). HEAD refuses both sizes with `Not a regular file`. This is a small tightening, consistent with SC4's "not a regular file". No design note mentions it; it needs none.
- **Dangling symlink:** `File not found` at both commits.
- **Symlinked subdirectory inside `pending/`:** escapes `pending/` (A2).
- **`pending/<symlink>/../doc.md`:** the base followed the OS and moved the file outside `pending/`. HEAD collapses the `..` as text and moves `pending/doc.md` instead. That is the safer direction. But D5's claim that the refusal "names the real target" is not true once a symlink precedes `..`.

### Code integrity

- **One clear path, not a mode switch.** `approve_research` (`operations.py:911-1027`) still reads as validate, number, write, move, report. The empty list is not a sentinel mode. It flows through the same steps, and only the registry read is gated, with a comment saying why the truthiness test is safe. The four refusal blocks follow the module's existing idiom. No new parameters.
- **The `isinstance(insights, list)` check is not too strict for any caller.** The only caller in `src/` is the CLI, which always passes a list (`_validate_json_list`, `cli/pm_cli.py:71-75`). No test passes a tuple or other sequence. A Python caller passing a non-empty tuple worked before and is now refused with a clear message. The signature says `list`, and fusion-tea does not call the operation (orchestrator, 2026-10-05). Acceptable.
- **Failure honesty:** no broad excepts, no silent fallbacks. `None` now gets a structured refusal that names the fix (`pass []`) instead of the misleading `No insights provided`.
- **Test quality:** good. On-disk claims run on real temp projects. `_tree_state` (`tests/test_pm_operations.py:1279`) earns its place. It is the only helper that shows a refusal created no `approved/` directory, and it caught a mutation that `_file_bytes` would have missed. Refusal tests are parametrized over list size (`_LIST_SIZES`, `:1288`) instead of copied. No assertion is vacuous: each refusal snapshots the tree before the call. Gap: A3.
- **Gates.** Claim checked against a worktree at c37ff53, comparing finding sets with line numbers stripped:
  - `ruff check src/ tests/`: identical findings (118 errors). The four touched Python files pass alone.
  - `ruff format --check src/ tests/`: identical file list (78). The `ruff format --diff` hunks in the two touched files that still need formatting (`operations.py`, `test_pm_operations.py`) are line-for-line identical to the base.
  - `mypy src/`: identical error set (91 errors in 19 files). One "See missing-imports" note line moved to a different file. mypy prints that note once per run, so it is not an error.
  - The implementer's claim holds: nothing new in any gate.
- **Leftovers:** A6 only.

---

## Certification

**Checked:**

- Read every upstream artifact: spec, spec review, design, plan, earlier product-lens block, briefs list.
- Read the full diff c37ff53..b6d1667 for `src/`, `tests/`, `claude/`, and tracking.
- Ran `uv run pytest tests/`: 2073 passed, 1 skipped, 33 deselected. The two PM test files alone: 220 passed.
- Compared ruff check, ruff format, and mypy finding sets at c37ff53 and HEAD.
- Ran 14 source mutations of `approve_research` in a separate worktree at HEAD: 11 caught, 3 survived (A3).
- Compared non-empty approval output and refusal messages at base and HEAD.
- Probed symlinks, a symlinked `..` root, and a symlinked subdirectory at both commits.
- Grepped all tracked shipped files for stale `approve-research` descriptions.
- Checked both help strings live.
- Ran the product-lens at audit stage (Gate DISPOSED).

**Marked:**

- All seven spec success criteria `[x]`. SC4 carries the A1 caveat recorded above.
- Plan phases were already checked by the implementer. I verified them and left them checked.
- No epic.
- `CURRENT_WORK.md`, `active/README.md`, the backlog **Status** line, and the spec **Status** line now say certified.

**Tree hygiene:**

- I used two temporary git worktrees (c37ff53 and HEAD, under `/tmp`) and no stash. Both are removed. I also ran `git worktree prune`, which only drops records of worktrees whose directories no longer exist. The main working tree was never edited except for this audit's tracking files.
- The product-lens subagent reported that one of its probes ran in the repo by mistake and created an untracked `knowledge/research/`, which it then deleted. I confirmed afterwards that `git status` shows only the pre-existing untracked `.project/research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md`, and that the tracked `knowledge/KNOWLEDGE.md` has no diff.
- Nothing is committed by this audit.

**Not checked:**

- I did not re-run the new tests against base `src/` to reproduce the plan's red table. I relied on reading the base code and on targeted probes at c37ff53.
- I did not run the slow corpus tests (`-m slow`). This change does not touch extraction or validation.
- I did not test on Windows or macOS. `os.path.normpath` and `relative_to` behave differently there, for example drive letters and case-insensitive paths.
- I did not test an agent following the new `/research` text in a live session (Bet B2). SC6 is verified as text only.
- I did not read fusion-tea. The claim that it neither calls nor parses `approve-research` is the orchestrator's.
- Re-init delivery of the changed `research.md` and `SKILL.md` to a target repo is inferred from both files being tool-owned and listed in `MBSE_COMMANDS` and `MBSE_SKILLS`. The product-lens ran `init` in a scratch project, but I did not diff the installed copies myself.
