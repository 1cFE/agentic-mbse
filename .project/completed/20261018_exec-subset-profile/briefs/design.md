Design EXEC-SUBSET-CONTRACT Item 1 from `.project/active/exec-subset-profile/spec.md` (reviewed; resolutions in `spec-review.md`).

Output: `.project/active/exec-subset-profile/design.md`.

Read: the spec, spec-review (Resolutions), `briefs/align.md` (owner gates R1–R3), the epic `.project/backlog/epic_executable-subset-contract.md` (Item 1 + boundaries with Items 2–5), the prototype `.project/concepts/convince-me-exec-subset/evidence/`, and the existing shared modules in `src/agentic_mbse/sysml/` (`executable_profile.py`, `reference_use.py`, `hierarchy.py`, `aggregation.py`, `constraint_facts.py`, `expression_facts.py`, `errors.py`). Read-only access: ~/src/sysml-codegen (b5663c07) incl. `.project/adr/0007-*.md`, ~/src/dc3.

Intent [AGENT, ratified by owner 2026-10-15]: one declared contract of which (shape, context) pairs the generator admits, refuses, excludes or omits, with evidence, that generator, L6 and guidance will later consume. Item 1 builds the contract, facts, evaluator, inventory and evidence — not consumer wiring.

**R1 is an owner gate.** Your design must present the capability-policy ownership decision and the fact/decision/consumer boundary as a clear recommendation with the alternatives you rejected and their costs — written so the owner can approve or redirect it in one read. Do not treat it as decided. The epic's suggested direction (pure `sysml/subset_profile.py`, `SUBSET_PROFILE_VERSION`, neutral reasons, separate fact extraction) is [INFERRED] — evaluate it on its merits against the precedent the spec names (`reference_use.py:395` already holds a capability decision in the fact layer) and ADR 0007. Put the R1 decision in its own clearly marked section near the top. Note: the R1 decision should later land as an ADR; draft its text in the design.

R2 and R3 remain owner gates as in the spec. If any design choice would make a rule refuse a (shape, context) the pinned generator admits, stop and say so rather than designing around it.

What I want from the design, beyond the command's normal shape:
- **Engineering quality bar**: clean module boundaries, no duplicated model interpretation, the evaluator as a pure function of explicit facts, closed validated vocabularies, deterministic ordering, structured unverified results. Show the data model (records, facts, results) concretely — types, not prose.
- **Probe harness design**: how Item 1 runs read-only generator probes at b5663c07 in isolated temp trees with exact package identity captured; how probe records are stored and tied to (rule, shape, context); how the "refused requires probe" invariant is enforced by a test rather than by convention.
- **Where things live**: rule records/matrix/site account/probe records (package data vs tests data vs .project), with the cross-check tests readable after the item folder is archived.
- **De-risk flags**: name explicitly any assumption about SysIDE behavior you could not verify by reading — especially ES-004 occurrence/multiplicity facts before elaboration, and equivalence of the shared binding-shape fact with codegen's helpers. For each, say whether a spike or learning test is needed before planning, and what it must show. I will decide whether to run one.
- Decide and record ambiguities the spec deferred to design (location, reason-vocabulary extension vs sibling set, dedup/identity policy, scanner reuse vs hardening, probe scope beyond the minimum), with reasoning.
