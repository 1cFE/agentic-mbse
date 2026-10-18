Review `.project/active/exec-subset-profile/spec.md` — the spec for EXEC-SUBSET-CONTRACT Item 1 (capability inventory, boundary design and shared profile).

Context to read: the epic `.project/backlog/epic_executable-subset-contract.md` (Item 1 and the boundaries with Items 2–4), the align record `.project/active/exec-subset-profile/briefs/align.md` (owner-reserved gates R1–R3 and ratified gap handling), and the spec briefs in `briefs/`. You have read access to ~/src/sysml-codegen (at b5663c07) and ~/src/dc3; do not modify them.

Intent the spec must serve [AGENT, ratified by owner 2026-10-15]: one declared contract of which model shapes the generator admits, refuses, excludes or silently omits, with evidence, that generator, L6 and guidance will consume instead of drifting. Item 1 builds the contract, not its consumers.

Review hard on:
- Whether every success criterion is objectively checkable and actually proves the epic's Item 1 criteria (inventory complete relative to the pinned surface; deferred cases owned with coverage limits; accepted near-neighbors stay accepted; detector failure / incomplete scope cannot look clean).
- R2 safety: is there any path by which a rule as specified could refuse a shape the pinned generator admits? The spec now accepts "code-read" evidence for some refusals (ES-003/ES-012 unified, ES-005 min/max, ES-004 ordered/nonunique). Test whether that evidence standard is strong enough, and whether the corpus criterion would catch an overbroad rule.
- Scope creep or under-scope against Items 2–5 and D2.
- Provenance grading correctness per `.claude/rules/capture-fidelity.md`.
- Anything the design stage cannot act on because the spec left it ambiguous.

Do not edit the spec. Produce the review artifact with a verdict and must-fix / should-fix items.
