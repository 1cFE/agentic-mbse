Review the design at .project/active/generated-results-guidance/design.md (EXEC-SUBSET-CONTRACT Item 5, rescoped) against its spec (spec.md, with spec-review.md Resolutions) and the spike results (spike/RESULTS.md). Write design-review.md in the same folder. Do not edit the design.

Intent, with provenance:
- [OWNER] "Mitigate actual risk, not ceremony." [AGENT, ratified by owner at launch] A modeller following the shipped workflow would catch a model that passes `sysml-codegen check` and generates but computes different numbers than the native model; better docs alone do not meet it.
- [INHERITED: ADR 0004] The generator is the only authority on generation; agentic-mbse keeps no copy of its rules and never imports sysml-codegen; a missing tool reports "not compared"/"not checked", never fine.
- Owner-reserved: RG-1 (what the generator accepts/refuses/builds), RG-2 (String / dropped result-expression guidance; the item only files and flags), RG-3 (pushes, merges, PRs, ADR filing). Delegated: sysml-codegen backlog rows on a branch; a new sysml-codegen command that does not change what the generator builds.

Questions I most want answered:
1. Engineering quality of the proposed `sysml-codegen compare` command: is the architecture clean (where it lives in sysml-codegen, the new public accessor over the instance graph, how native evaluation is invoked, exit codes 0/1/2/3, the compared-of-total summary)? Is anything a disguised second evaluator or a copy of generator rules?
2. Can it give a false pass? Look hard at the "not compared" classification (outputs depending on a part multiplicity, per-index values, no native value), exit 0 meaning "at least one compared and none differ", and the count and verdict checks. Would a real model like dc3's (/home/reid/src/dc3/models, which sums over parts per the shipped guidance) end up mostly "not compared" while exiting 0? If so, is that honest enough, or must the exit code or output change?
3. Does each element reduce one of the spec's four risks, and is anything ceremony?
4. Is the RG-1 boundary held (the corpus byte-identity check; no change to emitted packages)?
5. Is the plan-ready handoff complete: phases, the remaining unchecked assumption (can the generator tell which outputs depend on a multiplicity), simkit provisioning, merge order?
Mark findings must-fix or should-fix. Sibling repos (read-only): /home/reid/src/subset-conformance/sysml-codegen, /home/reid/src/dc3.
