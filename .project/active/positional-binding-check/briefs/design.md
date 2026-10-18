Design EXEC-SUBSET-CONTRACT Item 4 from `.project/active/positional-binding-check/spec.md` (reviewed; Resolutions in `spec-review.md`).

Output: `.project/active/positional-binding-check/design.md`. Keep it proportionate: one L2 check, its facts, the pin-list mechanism, fixtures, the reproduction, the hazard register and guidance edits.

Read: the spec, spec-review, `briefs/align.md` (gates; R4-1 decided; owner boundary: do not touch Item 2 or sysml-codegen), `product-lens.md`, the epic's Item 4. Existing code: `src/agentic_mbse/validation/` (L2 checks, `level2_structure.py`, the L2 failure pattern, severity handling), and Item 1's shared facts in `src/agentic_mbse/sysml/` (`subset_facts.py`, `subset_extraction.py`, `fact_refs.py`, `reference_use.py`). Prototype: `.project/concepts/convince-me-exec-subset/` (positional script and logs). Read-only: ~/src/fusion-tea (f96ad312), ~/src/dc3, ~/src/sysml-codegen (b5663c07).

Intent [AGENT]: detect implicit positional redefinition onto a differently named formal as an authoring-hazard finding, with D1's policy (new blocks, pinned legacy warns, and a pinned warning does not by itself fail L2), honest unverifiable results, and no change to generator behavior or consumer projects.

What I want:
- **Engineering bar:** the redefinition fact is extracted once, in the shared fact layer (reuse Item 1's identity types and helpers where they fit; don't duplicate model interpretation). The check is a thin decision over that fact. Pin-list parsing is strict and closed (unknown keys fail). Deterministic ordering. Every inspection failure is a named, structured unverifiable result.
- **Concrete data model:** the fact type, the finding identity, the pin-list file format and its location/discovery in a target project, the result shape — as types, not prose.
- **The L2 integration:** exactly how a pinned positional warning is excluded from L2's failure rule without changing any other code's behavior, and how stale and out-of-scope pins are reported.
- **The reproduction:** how the 125 prototype identities are extracted from the prototype log into a reference file, how the fusion-tea and dc3 runs execute on `git archive` copies, and how fusion-tea's L2 status is measured with and without the check and pin list.
- **De-risk flags:** name any SysIDE 0.8.4 behavior the design relies on but you could not verify by reading — especially how implicit versus explicit redefinitions surface in the API, how `subject`/`actor`/`stakeholder` parameters are distinguishable, and inherited/anonymous cases. For each, say whether a learning test is needed before planning and what it must show. I will decide whether to run one.
- Decide and record what the spec left to design, with reasoning.
