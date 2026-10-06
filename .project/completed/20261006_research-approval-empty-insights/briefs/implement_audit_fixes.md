# Brief: implement (audit fixes) — research-approval-empty-insights

**Sent:** 2026-10-05 by the orchestrator, as a resume of the implement session. **Input:** `audit.md` in the item folder (verdict Certify, six advisories A1-A6). Read the audit's evidence for each finding before changing anything.

## Rulings on the advisories (all [AGENT], orchestrator, 2026-10-05)

**A1 — fix now.** The change introduced it: the containment check uses normalized paths, while the registry path and the `approved/` destination are built from the caller's unnormalized `project_root` (`operations.py:927-928` versus `:963` and `:1011`). With a root that contains a symlink followed by `..`, the document is taken from one tree and moved into another.

Do not take the audit's suggested fix (normalize the root once and build everything from it). `os.path.normpath` on a root that contains a symlink followed by `..` names a different directory than the OS resolves, so every path would be consistent but could point at the wrong project. Leave `project_root` exactly as the caller gave it, and normalize only the part of the path below `pending/`:

1. Build `pending_dir` from the root as given, as the base commit did.
2. Take the document path relative to `pending_dir` with the existing textual `relative_to`. A failure is the existing "is not in" refusal.
3. Collapse `..` in that relative part only. If the collapsed relative path climbs out (its first part is `..`), refuse with the same "is not in" message.
4. Rebuild the document path as `pending_dir` joined with the collapsed relative path, and use that one path for the exists check, the regular-file check, and the move.

The result: the root means what the OS says it means, the check and the move use the same path, `pending/sub/../doc.md` still works, and `pending/../../KNOWLEDGE.md` is still refused. If you find a case where this shape is wrong, say so with a probe and propose the alternative; do not silently pick another.

Tests: keep test 5a and 5b honest under the new shape. Add the audit's A1 probe as a test: a `project_root` spelled through a symlink followed by `..`, where the OS-resolved project and the normpath-collapsed project are different directories that both exist. Assert the document is taken from and moved within the OS-resolved project, and the other tree is untouched. Show it red against the current `HEAD` first.

Update design D5 in place to describe the shape actually built (amend the text; one line recording that the first form normalized both full paths and the audit's A1 showed why that was wrong).

**A3 — fix now.** Add a test that pins the warnings on a non-empty approval: with a `KNOWLEDGE.md` that makes the registry read warn, a one-insight approval returns those warnings. It must fail if the warnings are dropped. Design invariant I5 claims this and nothing checks it.

**A4 — fix now.** The new `/research` sentence covers "skips every insight" and misses the case where no candidates were proposed, which is the usual shape of a source-registration round. Replace the sentence with:

> If the user approves the report with no accepted insights (every candidate skipped, or none proposed), still make the call, with `--insights '[]'`. The file moves to `approved/` and no DI-XXX entries are created, so tell the user that instead of reporting IDs.

Update the design's Implementation Notes to carry this text.

**A6 — fix now.** Correct `plan.md:3` and the backlog item's stale `operations.py:664-668` pointer.

**A2 — recorded, not fixed.** A symlinked directory inside `pending/` lets a call move a file that lives outside `pending/`. That follows from the design's choice not to resolve symlinks, it needs write access to `pending/` to set up, and the base had the same exposure with one insight. Add one line to the design's Potential Risks, and add it as case (c) to `PM-APPROVE-RESEARCH-MOVE-SAFETY` in the backlog, citing the audit's probe. Also record there the audit's observed change: a symlink to a directory given as the document is now refused.

**A5 — recorded.** Add one sentence to `PM-APPROVE-RESEARCH-MOVE-SAFETY` case (b): zero-insight approvals make a same-name overwrite more likely to come up, per the audit's product-lens note.

## Bar and boundaries

Same as the first brief: one path, one move, refuse before any write, non-empty output unchanged, real temp projects, no leftovers. Record what you did under a new "Audit fixes" note in `plan.md`. Run and report all four gates with counts. Do not commit. Do not touch the untracked research file from another session. Finish with `ARTIFACT: <path>`.
