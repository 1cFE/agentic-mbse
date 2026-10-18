Audit EXEC-SUBSET-CONTRACT Item 4 as implemented on branch `positional-binding-check` (base `ccd57d83`; implementation commits from `4ab5a33b` through `73be541e`), against `.project/active/positional-binding-check/spec.md`, `design.md` (rev 1) and `plan.md` (all phases ticked, with notes), plus `briefs/align.md` (gates; R4-1 decided; owner boundary: no Item 2, no sysml-codegen writes). Read-only: ~/src/fusion-tea (f96ad312), ~/src/dc3, ~/src/sysml-codegen (do not run anything in its checkout).

Do not self-certify on the implementer's reports. Verify independently:
- Every spec success criterion: met / met with recorded limit / not met, with evidence you checked.
- Detection correctness: read the rule and extractor; try to construct a swap the check misses or a correct model it flags (mixed spelling, explicit rename, subject/actor/stakeholder, unresolved types, inheritance, anonymous, multiple types). Check that the placeholder-typing path can never yield a clean pass.
- D1 policy mechanics: only pinned `L2_POSITIONAL_BINDING` warnings are exempt from L2's pass rule; stale vs out-of-scope vs not-judged pins behave as designed; strict pin parsing; root-only discovery.
- Reproduction independence: the fusion-tea pin list and comparison come from the prototype log, not the check's output.
- Engineering quality: duplication with Item 1, determinism, closed vocabularies, silent fallbacks, exception swallowing, dead code, TODOs.
- Guidance edits: accuracy against KerML and the learning tests; no claim beyond the evidence.
- The repository checks are run separately by the orchestrator; if you cannot run commands, say so rather than inferring results.
- Ignore the six unrelated working-tree edits (`.gitignore`, `.project/EPIC_GUIDE.md`, `.project/README.md`, `.project/active/README.md`, `.project/backlog/README.md`, `.project/epic_template.md`).

Produce `.project/active/positional-binding-check/audit.md` with a verdict and must-fix / should-fix items.
