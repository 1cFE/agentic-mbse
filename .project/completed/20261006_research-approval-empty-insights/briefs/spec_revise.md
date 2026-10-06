# Brief: spec (revise) — research-approval-empty-insights

**Sent:** 2026-10-05 by the orchestrator. **Stage:** `/_my_spec`, revision mode. **Target:** `.project/active/research-approval-empty-insights/spec.md`. **Input:** `spec-review.md` in the same folder (verdict: Revise) and `briefs/spec_review.md` for the verified facts.

Revise the existing spec in place. Do not re-interview and do not restructure it. Apply the rulings below, record them in the review's Resolutions section, and keep the spec short. Per the correction law, amend or delete corrected content; do not add prose about what was removed.

## What this work is for

[AGENT, re-derived] Research approved with no new insight goes through the supported operation, so nobody moves the file by hand. Accepting `--insights '[]'` is the mechanism.

## Provenance rules for this revision

- [OWNER] (2026-10-05) No reserved gates; the orchestrator decides and records.
- Every ruling below is `[AGENT]` (orchestrator, 2026-10-05). In the spec, new or sharpened criteria that come from these rulings are `[INFERRED]`. Criteria traced to the backlog stay `[INHERITED]`. Nothing becomes `[NEED]` or `[HARD]`.

## Rulings on the review findings

1. **L2-1 accepted.** Add a success criterion: the shipped `/research` command (`claude/commands/research.md`, approval step near `:77`) tells the agent that "report approved, every insight skipped" is called with `--insights '[]'`, and no longer tells it to report assigned IDs when none exist. The `approve-research` row in `claude/skills/toolkit-awareness/SKILL.md:90` no longer implies insights are always registered. Remove the matching open question. Exact wording stays with design.
2. **L3-1 accepted.** Split criterion 4 by observer. CLI user: exit code 0 and a message that states the document was approved with no insights created (no dangling `Created insights:`). Python caller: `ids_assigned` is empty and `files_modified` lists the approved path and does not list `KNOWLEDGE.md`. Drop the phrase "CLI guidance."
3. **L3-2 accepted.** State the outcome: a zero-insight approval leaves `knowledge/KNOWLEDGE.md` exactly as found (byte-identical; a missing file stays missing), and its success and warnings do not depend on that file's presence or contents. How is design's.
4. **L3-3 accepted.** Criterion 2 covers both surfaces: at the CLI, omitting `--insights` is a usage error; in Python, `insights` stays a required argument and `None` is not treated as an explicit empty list.
5. **L3-4, directory-as-file: brought into scope, against the reviewer's recommendation to file it separately.** Reason: today `approve-research knowledge/research/pending --insights '[]'` is refused only by the empty-list guard. Removing that guard makes the exact call this item ships able to move the whole pending queue. The fix is one validation (the pending path must be a regular file) and it only rejects calls that were never valid. Add it to criterion 3 as `[INFERRED]`: a pending path that is not a regular file is refused with nothing moved, for empty and non-empty lists alike.
6. **L3-4, the other two gaps: out of scope, filed.** (a) If the move fails after insights were appended, the DIs stay and a retry duplicates them. (b) An existing file of the same name in `approved/` is silently overwritten. Neither is made worse by this change. File one P3 backlog item `PM-APPROVE-RESEARCH-MOVE-SAFETY` in `.project/backlog/BACKLOG.md` covering both, citing the review's probe evidence, and link it from the spec's Non-Goals as a one-line decision record.
7. **L3-5 resolved by the orchestrator.** I searched `/home/reid/1cfe/fusion-tea` (branch `goal/magnet-material-comparison`) on 2026-10-05. No code there calls `approve-research` or parses its message; the only hits are docs and completed-item records. The message wording is a design detail, not an interface. Record that in Resolutions; no spec change beyond that.
8. **Cleanup, all accepted.** Fix the header branch to `research-approval-empty-insights`. Replace the stale `operations.py:635` pointer with `:910` (function) and `:936` (guard); keep `pm_cli.py:562`, which the reviewer confirmed is correct (my brief was wrong on that). Delete the ID-allocation non-goal. Fix the Known Requirement so the approval gate cites `claude/commands/research.md:69-71` only, and drop it if it only duplicates a Non-Goal. Carry the backlog's test obligation ("a test covers both, and asserts the document lands in `approved/` with no DI written") as `[INHERITED]`. Move the parked-scope bullet from Open Questions to Non-Goals. Update `Next Steps` to point at `/_my_design`.

## Also update tracking

- `.project/CURRENT_WORK.md`: the checkout line is stale (PR #15 merged; this item is on branch `research-approval-empty-insights` from `main` at `c37ff53`). Fix the checkout line, the PM registry integrity row's "not yet merged," and this item's Active Work line (spec reviewed and revised; design next). Change nothing else there.
- Backlog item `PM-APPROVE-RESEARCH-EMPTY-INSIGHTS` status line: spec reviewed and revised 2026-10-05.

Set the spec Status to reflect that it was reviewed and revised. Finish with `ARTIFACT: <path>`.
