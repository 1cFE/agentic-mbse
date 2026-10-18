Review `.project/active/positional-binding-check/spec.md` — the spec for EXEC-SUBSET-CONTRACT Item 4 (positional-binding hazard and check).

Context: the epic `.project/backlog/epic_executable-subset-contract.md` (Item 4, D1, Items 1/3/5 boundaries); the align record `briefs/align.md` (gates R4-1..R4-3 and the owner's boundary: do not touch Item 2 or sysml-codegen); `product-lens.md`. Item 1 is merged; its shared facts are in `src/agentic_mbse/sysml/`. Read-only: ~/src/fusion-tea (f96ad312), ~/src/dc3, ~/src/sysml-codegen (b5663c07). Do not modify them.

Intent [AGENT]: detect the demonstrated silent wrong-value hazard (implicit positional redefinition onto a differently named formal; native -7 vs generated 7) as an authoring-hazard finding in valid SysML, with D1's block-new/warn-pinned policy, without changing generator behavior or editing consumer projects.

Review hard on:
- Detection correctness: is the specified rule (implied redefinition target ≠ input name, no explicit redefinition accounting for it) exactly the hazard? Check against KerML semantics and the SysIDE 0.8.4 observations in epic Item 4 scope 3. Look for false positives (explicit rename, by-name `:>>`, in-order implicit, anonymous, defaulted/omitted inputs, inheritance) and false negatives.
- Does the scope (calc and constraint usages and definitions, incl. subtypes) match the prototype that produced 125, and is the reproduction criterion actually checkable?
- The L2 success-on-warning change (`level2_structure.py:450`): is the exemption minimal and safe, and does it avoid changing other codes' behavior?
- Reuse of Item 1 shared facts; no duplicated model interpretation.
- The fusion-tea consequence on pin move: is it stated honestly and routed to the owner (R4-3)?
- Provenance grading per `.claude/rules/capture-fidelity.md`; criteria objectively checkable.

Do not edit the spec. Produce the review artifact with a verdict and must-fix / should-fix items.
