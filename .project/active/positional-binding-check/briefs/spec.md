Write the spec for EXEC-SUBSET-CONTRACT **Item 4: Positional-binding hazard and check**.

Output: `.project/active/positional-binding-check/spec.md`.

## Source of truth

- The epic `.project/backlog/epic_executable-subset-contract.md`: read Item 4 in full, the Prototype findings (positional prototype: 125 fusion-tea mismatches, 0 in each dc3 tree), Why This Epic (the -7 vs 7 cross-route divergence), Root causes (positional behavior history: codegen `3bdf0b74`/`936315c8`, `f0a7b0a9`, `bd352744`), Owner decision D1, and Items 1 and 5 for boundaries.
- Align record: `.project/active/positional-binding-check/briefs/align.md` (gates R4-1..R4-3).
- Item 1 is merged (`ccd57d83`); its shared facts live in `src/agentic_mbse/sysml/` (`subset_facts.py`, `subset_extraction.py`, `fact_refs.py`, `reference_use.py`) and its archive is `.project/completed/20261018_exec-subset-profile/`. Reuse shared facts and identity types rather than re-deriving model interpretation. Existing L2 checks and their failure-reporting pattern live under `src/agentic_mbse/validation/`.
- Prototype evidence: `.project/concepts/convince-me-exec-subset/` (positional prototype script and logs). Feasibility only.
- Read-only sibling repos: `~/src/fusion-tea` (pinned `f96ad312c63e8c66695971b12feab971f3ba6eb3`; AD-008 in `modeling_project/ARCHITECTURE.md` and WI-076 notes carry the input-positional evidence; `RAW_LEARNINGS.md:80` is about output-tuple ordering and must not be cited for inputs), `~/src/dc3` (`808464d`, `60b44d5`), `~/src/sysml-codegen` (`b5663c07`; `tests/fixtures/modeled_default_fidelity/PROVENANCE.md`; the open POSITIONAL-FORMAL-REDEFINITION item). Never modify them; use `git archive`/`git worktree` into a scratch dir for pinned revisions.

## Settled items (provenance)

- [OWNER] D1, as written in the epic.
- [INHERITED: epic] Describe it as a likely authoring hazard in valid SysML; no unconditional language-validity error. Use resolved identities and implied/explicit relationship evidence, not name-set equality. Cover CalculationUsage and ConstraintUsage, inheritance, explicit renaming (`in local redefines a = ...` is not a swap), anonymous features, omitted/defaulted inputs, multiple targets, and unavailable evidence (reported separately using the existing L2 failure pattern).
- [INHERITED: epic] Record the 125 pinned fusion-tea findings by stable owner/input/target identity, not count. Adding a mismatch fails; a disappearing legacy finding requires baseline reconciliation.
- [INHERITED: epic] Retain the cross-route counterexample (native -7, generated/TEAx 7) and the SysIDE 0.8.4 observations listed in Item 4 scope 3 as durable fixtures; `/tmp/consumer-audit-byname/` artifacts are not acceptance evidence.
- [INHERITED: epic] `docs/patterns/semantic-hazards.md` cites KerML `checkFeatureParameterRedefinition`; the constructor named-argument passage is not proof of calc-usage syntax. Guidance updates per Item 4 scope 6, linking (not replacing) the existing self-binding contract.

## Gates — record as open, do not decide

R4-1 (suppression/disposition mechanism beyond D1), R4-2 (generator binding behavior), R4-3 (fusion-tea edits). See align record.

## What I want from the spec

- Requirements graded per `.claude/rules/capture-fidelity.md`.
- Evaluatable success criteria, each naming the artifact or test that proves it, including how the 125-finding baseline is stored, keyed and reconciled, and how "inability to inspect cannot silently pass" is tested.
- Where the epic or code leaves something ambiguous, decide and record it `[INFERRED]` with reasoning, unless it touches R4-1..R4-3.
- Keep it proportionate: this is one check plus fixtures, a register and guidance edits, not a framework.
