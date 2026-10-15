Write the spec for EXEC-SUBSET-CONTRACT **Item 1: Capability inventory, boundary design and shared profile**.

Output: `.project/active/exec-subset-profile/spec.md`.

## Source of truth

- The epic: `.project/backlog/epic_executable-subset-contract.md`. Read it in full: Executive Summary, Evidence and regression revisions (pinned revisions), Prototype findings and their limits, Design principles, Success Criteria, Item 1 (your scope), Items 2–4 (boundaries you must not absorb), Owner decisions D1–D3.
- Origin record: `.project/backlog/item_generator-subset-patterns.md` (read its historical claims through the epic's corrections).
- Orchestration align record: `.project/active/exec-subset-profile/briefs/align.md` — reserved gates and ratified gap handling.
- Prototype evidence: `.project/concepts/convince-me-exec-subset/` (template.html and evidence folder). Feasibility observations only, not acceptance evidence.
- Existing code to extend, not duplicate: `src/agentic_mbse/sysml/executable_profile.py` (27-member `REASON_CODES`, `EligibilityDiagnostic.__post_init__` membership check), plus `reference_use.py`, `hierarchy.py`, `aggregation.py`, `constraint_facts.py`, `expression_facts.py`.
- Read-only sibling repos: sysml-codegen at `~/src/sysml-codegen` (pinned capability baseline `b5663c07`, currently checked out at that commit), dc3 at `~/src/dc3` (`808464d` baseline, `60b44d5` repaired). Do not modify them. Use isolated temp trees (`git worktree` or `git archive` into your scratch dir) if you need a specific revision.

## Intent (what the spec must serve)

[AGENT] (ratified by owner 2026-10-15) One declared statement of which model shapes the generator admits, refuses, excludes or silently omits, with evidence, so generator, L6 and guidance consume one contract instead of drifting. Item 1 builds that contract — the inventory, the rule records, the shared facts/evaluator — not its consumers. Codegen integration is Item 2; L6 severity and execution-target settings are Item 3; positional binding is Item 4.

## Settled items (provenance marked)

- [OWNER] D1, D2, D3 as written in the epic (approved 2026-10-15).
- [OWNER-via-epic] Out of scope: implementing new language support; stricter policy is a behavior change requiring explicit review, not a side effect.
- [OWNER-via-epic] agentic-mbse must never import sysml-codegen or its types; do not use `ElaborationCode` or consumer-specific identifiers as the shared vocabulary.
- [AGENT] (ratified 2026-10-15) D2's full 500-site candidate account (441 codegen, 59 agentic-mbse) is built in Item 1 at the pinned revision, each site classified in scope / handled elsewhere / explicit follow-up with evidence and owner. Per-site stable codes and mutation tests remain Item 2.
- [AGENT] (ratified 2026-10-15) Item 1 does not claim generator-verified rules. Each rule record carries an evidence status (e.g. prototype-observed, pending Item 2 independent fixture). Item 1 tests verify the agentic-mbse evaluator and facts against agentic-mbse fixtures.
- [AGENT] (ratified 2026-10-15) "Inventory complete relative to the pinned generator surface" means complete relative to the scanner's recognized forms plus an explicit list of known blind spots.

## Reserved owner gates — do not decide these; record them as open in the spec

- R1: capability-policy ownership / fact-decision-consumer boundary. The epic recommends pure `sysml/subset_profile.py` with `SUBSET_PROFILE_VERSION`; the spec may state this as the recommended direction for design to evaluate, marked `[INFERRED]`, with owner approval required after design.
- R2: any shared rule that would refuse something the pinned generator currently admits. Requirements must forbid this without explicit owner approval.
- R3: absorption of GENERATOR-SUBSET-PATTERNS and disposition of remaining capability gaps. The spec records a proposed disposition only.

## What I want from the spec

- Requirements graded per the capture-fidelity rule (`[HARD]`/`[NEED]`/`[INFERRED]`/`[INHERITED]`), with epic-sourced items as `[INHERITED: epic]` unless the epic records them as owner decisions.
- Evaluatable success criteria. The epic's Item 1 criteria are the floor; make each one checkable (what artifact, what test, what count or identity).
- Clear in/out boundaries against Items 2–4, especially: what of ES-001..ES-012 Item 1 implements as evaluator rules versus records as candidates pending fixtures; what the capability/refusal matrix and 500-site account deliverables look like and where they live.
- Engineering bar: no duplicated model interpretation, no silent clean results on detector or enumeration failure, deterministic ordering, structured unverified results. Hold that bar in the requirements.
- Where the epic or code is ambiguous and you can't settle it from the sources, decide and record the call as `[INFERRED]` with reasoning rather than stopping, unless it touches R1–R3.
