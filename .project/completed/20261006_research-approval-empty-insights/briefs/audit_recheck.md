# Brief: audit re-check — research-approval-empty-insights

**Sent:** 2026-10-05 by the orchestrator, as a resume of the audit session. **Scope:** bounded. Check only what changed since your audit: `git diff d6ea9fc..HEAD`. Do not re-audit what you already certified.

## Rulings on your advisories (all [AGENT], orchestrator; full text in `briefs/implement_audit_fixes.md`)

- **A1 fixed, but not with your suggested shape.** Normalizing the root once would make every path consistent while possibly naming a different project than the OS resolves, because `normpath` collapses a symlink followed by `..` as text. The ruling was: leave `project_root` as given, collapse `..` only in the part of the path below `pending/`, refuse if it climbs out, and use the rebuilt path for the exists check, the file check, and the move. Built as `_path_below` (`src/agentic_mbse/pm/operations.py:539`). Challenge this ruling if your probe evidence says it is wrong.
- **A3 fixed:** a test pins the warnings on a non-empty approval.
- **A4 fixed:** the `/research` sentence now covers "every candidate skipped, or none proposed."
- **A6 fixed:** stale pointers corrected.
- **A2 and A5 recorded, not fixed:** in the design's risks and in backlog item `PM-APPROVE-RESEARCH-MOVE-SAFETY` (new case (c), and a sentence on case (b)).

## What the implementer reported (verify, do not trust)

- The A1 probe reproduced on `d6ea9fc`'s code and is now a test, run with an empty list and one insight. Against the old code: 6 failed, 21 passed.
- One call is now refused that the first version accepted: a root containing `..` together with an absolute document path spelled without it. The implementer says the base `c37ff53` refuses it too, so it is not a regression from the base.
- The `..` refusal message now prints the path as the caller gave it.
- Seven deliberate breaks, each caught, including the "normalize the root once" alternative.
- Gates: pytest 2079 passed, 1 skipped, 33 deselected; ruff check 118; ruff format 78 files; mypy 91 errors in 19 files. All three static counts equal the base.

## What to check

1. Does your A1 probe now pass, for an empty list and for one insight, with nothing written to the wrong tree?
2. Is `_path_below` correct at its edges: the path equal to `pending/` itself, `pending/sub/../doc.md`, `pending/../../KNOWLEDGE.md`, `pending/sub/../../../x`, an absolute path outside the project, a trailing slash? Does anything now disagree between the path checked and the path moved?
3. Is non-empty behavior still identical to the base for ordinary inputs (message, IDs, `files_modified`, warnings, resulting `KNOWLEDGE.md`)?
4. Do the new tests fail when they should? Re-run your three warning mutations and one A1 mutation.
5. Are the static-gate finding sets still identical to the base?
6. Do the design (D5 as amended), the plan's "Audit fixes" note, and the backlog item describe what was built, without overclaiming?

Update `audit.md` with a dated re-check section and a final verdict, and correct any tracking line that the fixes made stale. Do not fix code. Do not commit. Do not touch the untracked research file from another session. If you use a worktree, remove it. Finish with the verdict and `ARTIFACT: <path>`.
