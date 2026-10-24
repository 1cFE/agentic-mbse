Review the spec at .project/active/generated-results-guidance/spec.md (EXEC-SUBSET-CONTRACT Item 5, rescoped). Write the review next to it as spec-review.md.

Context and provenance:
- [OWNER, 2026-10-22] Item 5 was rescoped to four actual risks: "what is risk that remains that we should mitigate? not ceremony, actual risk", then "agreed" to the four risks in the spec. The 212-fence inventory and the 100% coverage target are out by owner decision.
- [OWNER, at orchestration launch] The goal is that a modeller following the shipped workflow would catch a model that passes `sysml-codegen check` and generates, but computes different numbers than the native model. Better docs alone do not meet it.
- [INHERITED: ADR 0004, .project/adr/0004-generator-is-the-only-generation-authority.md] The generator is the only authority on generation; agentic-mbse keeps no copy of its rules and never imports sysml-codegen.
- Reserved for the owner (do not decide, flag if the spec decides them): RG-1 what the generator accepts/refuses/builds; RG-2 the String policy; RG-3 pushes, merges, PRs, ADR filing.
- [OWNER-delegated] The orchestrator may file generate-but-wrong cases as sysml-codegen backlog rows on a branch, and may let design propose a new sysml-codegen command (for example a native-vs-generated comparison) as long as it does not change what the generator builds.
- Known conflict: agentic-mbse .project/completed/20261018_positional-binding-check/evidence/upstream-codegen-finding.md (native -7 vs generated 7) disagrees with sysml-codegen backlog [POSITIONAL-FORMAL-REDEFINITION]. The spec defers reconciliation to design.

Sibling repos for reading evidence (read-only): /home/reid/src/subset-conformance/sysml-codegen (the generator, branch with the latest backlog) and /home/reid/src/dc3 (the consumer project whose parity test and adapter the spec cites: tests/models/test_generated_parity.py, scripts/models/package_comparison.py).

What I want from the review: whether each success criterion is testable and actually reduces the stated risk; whether any criterion is ceremony that does not reduce risk (say so plainly); whether the factual claims in Problem are true (check them against the files and the generator code, e.g. that a part-owned assert reports and continues in a generated package, that the min identity differs numerically, the count of places teaching refused functions); missing risks; and anything the spec settles that belongs to design or to the owner. Mark findings must-fix or should-fix. Do not edit the spec.
