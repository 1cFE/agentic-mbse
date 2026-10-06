# Spec Review: Approve Research with No New Insights

**Spec:** `.project/active/research-approval-empty-insights/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md` (not readable from this sandbox; reviewed against the five lenses in `/_my_spec_review` and `capture-fidelity.md` instead)
**Review File:** `.project/active/research-approval-empty-insights/spec-review.md`
**Date:** 2026-10-05
**Code checked at:** `c37ff53` on branch `research-approval-empty-insights`

---

## Reality Check

**Sound.** The spec is about the right work item, and the Problem section is accurate. A probe at `c37ff53` confirmed it: an explicit `[]` returns `success=False, "No insights provided"` and the document stays in `pending/` (`src/agentic_mbse/pm/operations.py:936-940`).

The core bet is sound too. Accepting `--insights '[]'` keeps the CLI surface unchanged, and it is what `/research` already produces when every insight is skipped. The original contract never required a non-empty list. FR-9 says "for each insight: assign … append" with no minimum (`.project/completed/20260203_d4.4-operations/spec.md:170-181`). The guard was added during implementation, so removing it restores the original contract rather than changing it.

The `[INHERITED]` tags on criteria 1 and 2 trace faithfully to the backlog Goal (`.project/backlog/BACKLOG.md:77-87`). "Leaves the knowledge registry unchanged" is a fair reading of "mints nothing … no DI written." Sizing is consistent: LOW matches the backlog's 0.5 day, and it stays there even if L2-1 adds a doc line.

The defects are all in what the spec leaves unsaid at the edges, so this is a Revise, not a Rework.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** Some code pointers are stale. One pointer the brief calls stale is correct.

- `operations.py:635` is stale. The function starts at `operations.py:910`; the guard is at `:936`.
- `pm_cli.py:562` is **not** stale, contrary to the brief. It lands exactly on the `--insights` `required=True` argument. The subparser block runs `pm_cli.py:559-563`.
- `research.md:65` is the `§4 Approve and Capture Insights` heading. That works as a pointer to the approval gate (`:69-71`). The call instruction itself is at `:77-79`.
- The header's `Branch: harness-right-size` is stale. The branch is `research-approval-empty-insights`.
- Outside the spec, the backlog Problem's `operations.py:664-668` is also stale. The orchestrator may want to fix it when the item closes.

**L1-2 · Direct claim:** The Non-Goal clause "repairing the separate registry ID-allocation defect" names a defect that no longer exists. PR #15 (`pm-registry-integrity`) repaired it, and `tests/test_pm_operations.py:1351` (`test_mints_above_archive_note`) covers the fix for this very operation. Delete the clause rather than reword it. A non-goal about finished work only anchors future readers on it.

**L1-3 · Rewrite request:** The single Known Requirement has two problems.

- **Wrong citation.** It cites "the historical PM operations spec's approve-research contract" for "the existing user approval gate remains." FR-9 says nothing about a user gate. The gate lives only in `claude/commands/research.md:69-71`.
- **Redundant with a Non-Goal.** It duplicates the Non-Goal "automatically approving a document," and its first clause ("This changes which approved research outcomes the operation accepts") describes the change rather than requiring anything.

Ask the spec agent to keep the gate constraint in one place, cite `research.md:69-71` for it, and cite FR-9 for what it actually supports: there was never a non-empty rule.

**L1-4 · Rewrite request:** The spec dropped one sentence of the backlog Goal: "A test covers both, and asserts the document lands in `approved/` with no DI written." The criteria are testable as written, so this is low stakes. Still, the backlog names a verification obligation, and the spec should either carry it or state that the plan carries it. Both cases matter: explicit `[]` lands in `approved/` with no DI written, and a missing `--insights` is still rejected. Neither has a test today. `tests/test_pm_cli.py:417-456` covers only valid JSON, invalid JSON, and an invalid item.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim, with a recommendation:** The open question "whether command instructions need a short clarification" is a spec-stage question. Only its wording belongs to design. It should become a success criterion.

- **Who actually calls the operation.** FR-9 names `/research` as the caller, and users in target repos reach `approve-research` only through that command.
- **What the command says today.** `research.md:77` tells the agent to pass "structured JSON of approved DI-XXX entries". `:79` says the operation "assigns DI-XXX IDs … Report the assigned IDs to the user."
- **The gap.** Nothing tells the agent that "report approved, every insight skipped" means calling with `'[]'`. An agent can reasonably skip the call, treat the case as an error, or move the file by hand, which is the bypass this item exists to remove.

The outcome in the brief is "research approved with no new insight goes through the supported operation." That outcome is not reached if the shipped instructions never route the case to the operation.

Recommended criterion, tagged `[INFERRED]`: the shipped `/research` approval instructions cover approving a report with no accepted insights. They direct the call with an explicit empty list and don't ask the agent to report IDs when none were assigned. The cost is a line or two in `claude/commands/research.md`, which is tool-owned and reaches target repos on re-init. `claude/skills/toolkit-awareness/SKILL.md:90` ("Approve pending research and register domain insights") is a one-word tweak; design can take it or leave it.

### Lens 3 — Pipeline Risk

**L3-1 · Rewrite request:** Split criterion 4 by observer. As written, a message-only change could satisfy it.

The CLI prints only `result.message` and warnings, then exits 0 or 1 (`pm_cli.py:78-89`). `files_modified` and `ids_assigned` reach only Python callers. The criterion needs two observable halves:

- **CLI user:** exit code 0. The message says the research was approved and that no insights were created, rather than ending in an empty `Created insights: ` (today's format at `operations.py:996`).
- **Python caller:** `success` is true and `ids_assigned` is empty. `files_modified` names the approved document and not `knowledge/KNOWLEDGE.md`. Today it always lists both (`operations.py:998`).

"CLI guidance" is also ambiguous. It could mean the result message, the argparse help strings (`pm_cli.py:560`, `:562`, "Approve a research file and extract insights"), or the shipped command docs (L2-1). The rewrite should say which.

**L3-2 · If-then tradeoff:** "Leaves the knowledge registry unchanged" needs a precise test, and the spec should say whether `KNOWLEDGE.md` can affect a zero-insight approval. I recommend it be settled in the spec, as an outcome. Here is what happens today, confirmed by probe:

- **Missing `KNOWLEDGE.md` does not block approval.** `parse_knowledge` warns `File not found: …/KNOWLEDGE.md` and returns no entries. A non-empty approval then creates the file through `_append_section`.
- **An undecodable `KNOWLEDGE.md` crashes the operation.** `parse_knowledge` catches only `FileNotFoundError` (`src/agentic_mbse/pm/parser.py:689-693`), so a decode or permission error raises.

**If** design keeps the parse on the zero-insight path, two things go wrong. A repo with no `KNOWLEDGE.md` gets a misleading file-not-found warning on an approval that never needed the file. An unreadable `KNOWLEDGE.md` crashes an approval that writes nothing to it. **If** the spec states the outcome, design is free to choose the mechanism (skip the read, or keep it and suppress the warnings).

Recommended outcome, tagged `[INFERRED]`, two parts:

- A zero-insight approval leaves `KNOWLEDGE.md` exactly as found. Byte-identical if present; still absent if absent.
- Its success, and the warnings it prints, do not depend on the state of `KNOWLEDGE.md`.

This is not widening. It is what "mints nothing" means once you look at what the operation reads.

**L3-3 · Direct claim:** Criterion 2 protects absence at the CLI only. Argparse `required=True` already rejects a missing `--insights` with exit 2. The Python layer is unprotected, and there the risk is real.

- **Today.** `insights=None` hits the falsy guard and returns `"No insights provided"`. Omitting the keyword raises `TypeError`, because it is a required keyword-only argument.
- **If design deletes the guard,** `None` raises `TypeError` at `for inp in insights` (`operations.py:952`), after the knowledge file has been parsed. Ugly, but still a caller error.
- **If design adds a default** (`insights: list | None = None`) or normalizes `None` to `[]`, absence silently approves. That is the exact conflation the backlog forbids.

Criterion 1 already says the Python operation has "the same behavior." Criterion 2 needs the matching clause: at the Python layer, absence (an omitted argument or `None`) is never treated as an explicit empty list. Whether that surfaces as a structured failure or an exception is design's call.

**L3-4 · Direct claim:** Parking transactional behavior out of scope is honest. This change creates no new partial-failure case: with zero insights, no append happens before the move, so the operation either moves the file or fails with nothing written.

The spec also says "any defect discovered there should be surfaced separately." This review found three gaps that exist today. Each falls short of FR-9's "file move and KNOWLEDGE.md appends are all-or-nothing" and of the shipped claim that PM mutations "succeed fully or not at all" (`claude/skills/toolkit-awareness/SKILL.md:85`):

- **(a) Failed move after appends.** Entries are appended first and the file is moved second (`operations.py:983-991`). If the move raises, the new DIs are already minted and the research stays pending. A retry mints duplicates. This affects only the non-empty path.
- **(b) Silent overwrite on name collision.** If `approved/` already holds a file with the same name, `shutil.move` overwrites it without a warning. Probe: the earlier approved file's content was replaced. This affects both paths.
- **(c) The pending directory is accepted as the "file."** It passes both existing checks, and the operation moves the whole queue into `approved/pending/`. Probe: `success=True, "Approved research: pending."` This affects both paths. Today `[]` is stopped by the guard, so (c) needs non-empty insights and mints visible DIs. After this change, `approve-research knowledge/research/pending --insights '[]'` moves the entire queue with no DI to show it happened. This is the one place the change lowers a barrier.

Recommendation: file (a)-(c) as one separate backlog item and keep them out of this repair. **If** the orchestrator judges (c) too likely to leave, the fix is a one-line "the path names a regular file" check before any writes. But that check also changes non-empty behavior, which conflicts with criterion 3's "retains its current … behavior" as written. Criterion 3 would need amending to allow it. I'd file it separately.

**L3-5 · Question to the orchestrator:** The driving consumer is fusion-tea's `goal-research-seam` (backlog "Downstream", spec R-C3/R-C4). It will hit the zero-insight path on every source-only round. I could not read the sibling repo from this sandbox. **Does that seam read the CLI message text or the exit code, or does it call the Python API and read `ids_assigned`/`files_modified`?**

- **If it parses the message,** the zero-insight message is an interface. "Exact success-message wording" can't be freely deferred, and criterion 3 should say the non-empty message format (`operations.py:996`) is preserved.
- **If it reads only the exit code or the Python result,** wording is fairly design's call.

### Lens 4 — Hygiene

**L4-1 · Rewrite request:** Three small fixes.

- **Wrong command in Next Steps.** "use `$my-design`" should be `/_my_design`.
- **A decision filed as a question.** The second Open Questions bullet ("Approved-destination collisions and broader transactional/file-move behavior keep their current semantics") is a scope decision, not a question. It belongs in Non-Goals, as one line.
- **Stale branch** in the header (see L1-1).

### Lens 5 — Reader Comprehension

No findings. The spec is short and reads in one pass. The one undefined term, "knowledge registry," is handled by L3-2.

---

## Engagement Summary

**Overall take:** The spec is about the right defect and the core bet holds: accepting `[]` restores what FR-9 always allowed. Its weak spots are the edges. It does not say how the fix reaches the `/research` user. It lets a message-only change satisfy the reporting criterion. It leaves Python absence and the `KNOWLEDGE.md` dependency unstated. Each fix is a clause or two, and none widens the repair.

**Here's what I need you to weigh in on:**

1. **[L2-1]** Promote the `/research` instruction from open question to an `[INFERRED]` success criterion: the shipped approval steps route "report approved, all insights skipped" to the operation with `'[]'`. Without it, the fix may never reach the user.
2. **[L3-1]** Split criterion 4 into what the CLI user sees (exit 0, accurate message) and what a Python caller sees (`ids_assigned` empty, `files_modified` without `KNOWLEDGE.md`). Say which "CLI guidance" is meant.
3. **[L3-2]** State the outcome for `KNOWLEDGE.md`: left exactly as found (absent stays absent), and a zero-insight approval's success and warnings don't depend on it. Mechanism stays with design.
4. **[L3-3]** Add the Python counterpart to criterion 2: `None` or an omitted argument is never treated as an explicit empty list.
5. **[L3-4]** Accept the transactional parking as honest, and file the three gaps that exist today (failed move after appends, silent overwrite on collision, directory accepted as the file) as a separate backlog item. Decide whether the directory case (c) stays parked; I recommend it does.
6. **[L3-5]** Check in fusion-tea whether the seam parses the CLI message. If it does, message wording is an interface, not a design detail.
7. **[L1-1, L1-2, L1-3, L1-4, L4-1]** Cleanup: fix the stale pointers and branch, delete the finished ID-allocation non-goal, fix the Known Requirement's citation and its overlap with the Non-Goal, carry the backlog's test obligation, and move the parked-scope bullet to Non-Goals.

---

## Resolutions

[AGENT] Rulings by the orchestrator, 2026-10-05, under the owner's "no reserved gates" ruling. Applied to the spec the same day. New or sharpened criteria from these rulings are `[INFERRED]`; nothing was upgraded to `[NEED]` or `[HARD]`.

- **L1-1 · Accepted.** Header branch is now `research-approval-empty-insights`. The `operations.py:635` pointer is replaced with `:910` (function) and `:936` (guard). `pm_cli.py:562` is kept; it is correct. The backlog Problem's `operations.py:664-668` pointer is not changed in this revision.
- **L1-2 · Accepted.** The ID-allocation non-goal is deleted.
- **L1-3 · Accepted.** The Known Requirement only duplicated the Non-Goal on automatic approval, so it is dropped. The Non-Goal now cites the approval gate at `claude/commands/research.md:69-71`.
- **L1-4 · Accepted.** The backlog's test obligation is carried as an `[INHERITED]` success criterion, quoted.
- **L2-1 · Accepted.** New `[INFERRED]` criterion: the `/research` approval step routes "report approved, every insight skipped" to `--insights '[]'` and stops asking for IDs when none exist; the `SKILL.md:90` row stops implying insights are always registered. The matching open question is removed. Wording stays with design.
- **L3-1 · Accepted.** The reporting criterion is split by observer: CLI user (exit 0, message states no insights were created) and Python caller (`ids_assigned` empty, `files_modified` lists the approved path and not `KNOWLEDGE.md`). "CLI guidance" is dropped.
- **L3-2 · Accepted.** New `[INFERRED]` criterion: `KNOWLEDGE.md` is left exactly as found (byte-identical; missing stays missing), and the approval's success and warnings do not depend on it. Mechanism stays with design.
- **L3-3 · Accepted.** The omission criterion covers both surfaces: CLI usage error, and in Python `insights` stays required and `None` is not an explicit empty list.
- **L3-4 (c) · Brought into scope, against the reviewer's recommendation.** Reason: today `approve-research knowledge/research/pending --insights '[]'` is refused only by the empty-list guard, so removing the guard lets the exact call this item ships move the whole pending queue. The fix is one validation that rejects only calls that were never valid. Criterion 3 now refuses a non-regular-file pending path with nothing moved, for empty and non-empty lists alike, and its "retains current behavior" clause is narrowed to regular files.
- **L3-4 (a), (b) · Out of scope, filed.** Failed move after appends, and silent overwrite on a name collision in `approved/`. Neither is made worse by this change. Filed as P3 `PM-APPROVE-RESEARCH-MOVE-SAFETY` in `.project/backlog/BACKLOG.md` and linked from the spec's Non-Goals.
- **L3-5 · Resolved.** The orchestrator searched `/home/reid/1cfe/fusion-tea` (branch `goal/magnet-material-comparison`) on 2026-10-05. No code there calls `approve-research` or parses its message; the only hits are docs and completed-item records. Message wording is a design detail, not an interface. No spec change.
- **L4-1 · Accepted.** Next Steps points at `/_my_design`. The parked-scope bullet moved from Open Questions to Non-Goals, merged with the L3-4 (a)/(b) record. Branch fixed with L1-1.
- **Lens 5 ·** No findings; nothing to resolve.

---

**Verdict:** Revise
**Next Steps:** Once the orchestrator records resolutions above, re-run `/_my_spec` (or resume the spec-agent session) and point it at this review to incorporate them. The reviewer does not edit the spec.
