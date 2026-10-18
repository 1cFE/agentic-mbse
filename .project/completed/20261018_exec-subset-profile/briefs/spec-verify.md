You now have read access to ~/src/sysml-codegen (checked out at b5663c07), ~/src/dc3 and ~/src/fusion-tea. Do not modify them; use `git show <rev>:<path>` or `git -C ... worktree add` into a scratch dir for the pinned dc3 revisions (808464d, 60b44d5).

Verify the spec's cross-repository claims against the actual sources and amend the spec where they are wrong or thin:

1. dc3 U1–U7 (`.project/active/toolkit-upstream-findings.md`) and T-001 B1–B9 (`work/orchestration/goals/study-ready-baseline/evidence/T-001-blocker-inventory.md`) — confirm the matrix-row list names them correctly and note anything the spec misreads (e.g. U7 is not a refusal).
2. sysml-codegen's existing successfully-generating fixture corpus at b5663c07 — confirm it exists, roughly where, and that "run the evaluator read-only over it" is a well-defined criterion. Name the corpus location in the criterion.
3. The generator diagnostic codes the ES table cites (SI_CONSTRAINT_UNATTACHED, SI_RENDERING_COLLISION for String referents, SI_EXPRESSION_SOURCE_UNSUPPORTED, SI_EVIDENCE_INCOMPLETE, SI_MULTIPLICITY_*) — confirm they exist in codegen and that the refused scope each row claims is consistent with the code paths raising them.
4. ADR 0007 — find it (agentic-mbse, codegen, or elsewhere) and update the R1 open question accordingly.
5. On D2's grade: keep your capture-fidelity reasoning, but apply it consistently. The epic says D1–D3 were "approved by the owner during the 2026-10-15 discussion" and does not record who originated them, so "ratified by owner" is the honest grade. Fine as you have it.

Keep edits surgical. End with a short list of what changed and the ARTIFACT line.
