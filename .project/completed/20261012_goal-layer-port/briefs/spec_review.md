# Brief: /_my_spec_review — goal-layer-port (`WRAP-SPLIT` Item 2)

Review `.project/active/goal-layer-port/spec.md` as a fresh, independent reviewer. You did not write it. Write your review to `.project/active/goal-layer-port/spec-review.md`. Do not edit the spec and do not commit. Start no background tasks. End with `ARTIFACT: <path>`.

Context to read: the Align record `.project/active/goal-layer-port/briefs/align.md` (it amends the epic), the spec brief `briefs/spec.md`, the epic `.project/backlog/epic_wrap-split.md` § Item 2, and the product-lens ledger beside the spec. fusion-tea files are in the read-only snapshot `.orchestrate-logs/fusion-tea-snapshot/` (fusion-tea commit `2b1e9f9d5`); you cannot read `/home/reid/1cfe/fusion-tea` itself.

Weigh these hardest, in order:

1. **The owner's central direction.** [OWNER-VERBATIM] 2026-10-11: "it is important that you find the right level for this rule -- we have specific patterns which agentic-mbse is supposed to enforce, this should fit into that". Does the spec's map of agentic-mbse's enforcement levels match the shipped files (verify the cited lines)? Are the levels it chooses, and SC5's "fits" checks, a sound reading of that direction, or do they miss a level where modelers and reviewers actually act, or over-spread the rule?
2. **Fidelity to MR-7.** Check the obligation list and SC6 against fusion-tea `modeling_project/REQUIREMENTS.md:87-107` in the snapshot. Nothing general dropped, nothing fusion-specific kept as general, grades preserved.
3. **Behaviour-preserving port.** Would the success criteria catch a port that quietly changed the runbook's method or broke the citations existing fusion-tea goals rely on?
4. **Checkability.** Can an auditor verify every SC from files and commands? Flag any SC that is vague, unverifiable, or that selects an implementation rather than an outcome.
5. **Scope and budget.** The item has a two-day ceiling. Flag scope that belongs to Items 3, 4 or 5, and anything the spec could shed.

Grade each finding must-fix or advisory, with a file:line basis. Keep the review short and plain.
