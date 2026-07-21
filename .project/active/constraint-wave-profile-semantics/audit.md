# Audit: Constraint-Wave Profile Semantics (Item 1)

**Verdict:** Implementation and spec conformance verified
**Scope:** Remaining provenance-only gates waived by owner after audit; no re-audit performed
**Audited:** 2026-07-19
**Branch:** `constraint-exec-epic` (both repositories)
**Commit:** agentic-mbse `4ed2a07`; sysml-codegen `512786c`

---

## Summary

The remediated implementation conforms to the approved profile-v4 and codegen design. Fresh normal
and optimized checks prove source-identity rejection before graph/output mutation, four-route
positive-IR and polarity continuity, compound diagnostic preservation, one neutral body with
per-usage polarity, mixed-polarity TEAx execution, package/skew controls, and the shared Items 2/4/6
landing unit.

After this audit, the owner said: “yeah I don't need those gates at this point. please amend, but
don't re-audit. I want to discuss the larger context before we continue rerunning.” The
clean-overlay and pre-edit-hash requirements were agent-authored process gates, so they no longer
block Item 1. No missing provenance is claimed to exist, and this disposition is not a re-audit.

## Findings

### Plan completion

- **Implementation phases are behaviorally complete.** The prior source-identity defect is closed:
  inline identity is reconciled to the usage, definition-typed identity is reconciled to the unique
  referenced definition, and contradictions raise before source-key construction
  (`../sysml-codegen/src/sysml_codegen/analysis/constraint_lowering.py:690`,
  `../sysml-codegen/src/sysml_codegen/analysis/constraint_lowering.py:713`,
  `../sysml-codegen/src/sysml_codegen/analysis/constraint_lowering.py:945`). Lowering sentinels prove
  owner expansion and constraint-ID minting remain untouched
  (`../sysml-codegen/tests/conformance/test_constraint_lowering.py:636`). Integrated absent/populated
  target sentinels prove no clear/setup or byte mutation
  (`../sysml-codegen/tests/conformance/test_constraint_profile_route_parity.py:129`).
- **Equivalent kept coverage satisfies filename-specific behavioral stencils.** The integrated
  codegen route test covers positive/negated inline/definition live and codec continuity
  (`../sysml-codegen/tests/conformance/test_constraint_profile_route_parity.py:91`); the compound
  diagnostic sentinel covers profile, L6, codegen halt, and target preservation
  (`../sysml-codegen/tests/conformance/test_constraint_profile_route_parity.py:185`); and the kept
  emission/execution tests cover one body, two wrappers, reversed order, and exact-once behavior
  (`../sysml-codegen/tests/unit/test_constraint_emission.py:160`,
  `../sysml-codegen/tests/execution/test_constraint_execution.py:647`). These outcomes satisfy the
  plan even though some tests do not use the companion-side filenames in the original stencil.
- **Owner disposition after audit.** No durable pre-edit per-path/untracked/fixture manifest exists,
  and the corrected wheels were built from the active shared-wave trees rather than reconstructed
  clean reviewed overlays (`evidence.md:226`). The owner waived those agent-authored gates. Current
  bytes and behavior remain the evidence of record; unavailable history is not asserted.

### Spec conformance

- **Ordering and polarity:** Verified. Profile v4 validates complementary Boolean decision fields
  (`src/agentic_mbse/sysml/executable_profile.py:120`), applies the closed ordering matrix and exact
  malformed-arity diagnostic (`src/agentic_mbse/sysml/executable_profile.py:557`), and rejects
  non-Boolean polarity before predicate walking (`src/agentic_mbse/sysml/executable_profile.py:920`).
- **Diagnostic cardinality and mutation order:** Verified. Two malformed compound leaves retain
  deterministic profile order, become two L6 errors, and halt codegen without clearing or setting up
  the populated target (`../sysml-codegen/tests/conformance/test_constraint_profile_route_parity.py:185`).
- **Positive-IR route continuity:** Verified. Licensed live extraction and the public codec produce
  equal decisions, concrete records, catalogs, compiled plans, polarity pairs, and positive
  predicate bytes for positive/negated inline/definition rows
  (`../sysml-codegen/tests/conformance/test_constraint_profile_route_parity.py:91`).
- **Neutral body and exact-once execution:** Verified. Catalog grouping is source-keyed
  (`../sysml-codegen/src/sysml_codegen/generation/constraint_catalog.py:46`), compilation is
  polarity-neutral (`../sysml-codegen/src/sysml_codegen/generation/modules.py:131`), and wrappers
  apply the catalog pair once (`../sysml-codegen/src/sysml_codegen/templates/constraint_module.py.jinja2:35`).
  Fresh TEAx execution passed the true, false, strict-zero, inclusive-zero, and non-finite paired
  rows in reversed usage order (`../sysml-codegen/tests/execution/test_constraint_execution.py:647`).
- **Package and skew:** Verified for the existing immutable artifacts. Package/runtime/lock identity
  is companion `0.1.2`, profile v4, and codegen floor `agentic-mbse>=0.1.2`
  (`src/agentic_mbse/__init__.py:7`, `../sysml-codegen/pyproject.toml:24`,
  `../sysml-codegen/tests/unit/test_package_metadata.py:10`). A fresh offline rebuild of the
  wheelhouse manifest and four pinned inputs was byte-identical to retained evidence. Fresh installs
  proved old/new and new/old runtime rejection, the exact resolver conflict with no unrelated
  unsatisfied package, and successful new/new resolution.
- **Schema and stored-byte preservation:** Implementation inspection and kept shape/codec tests found
  no Item 1 change to the `ConstraintFacts` schema or snapshot-v3 shape. No claim is made about
  unavailable pre-edit hashes; the owner removed that stronger process gate after audit.
- **Historical closure:** Retained clean-revision probes and the independently rerun controls prove
  R-1/profile R-2 RED at companion `54a95d2`, active-v4 GREEN, and unchanged downstream negated
  execution at codegen `512786c`. The retained helper hash matches the implementation record.

### Design conformance

The implementation follows D1-D11 and invariants I1-I15 on the inspected paths. Source identity is
now reconciled before reusable-key creation; positive predicate bytes remain separate from polarity;
one source-keyed body serves opposite-polarity usages; and the frozen generation plan is compiled and
rendered before output clear/setup (`../sysml-codegen/src/sysml_codegen/generation/constraint_plan.py:16`,
`../sysml-codegen/src/sysml_codegen/cli/__init__.py:982`). The prior malformed-arity wording deviation
is also closed at `src/agentic_mbse/sysml/executable_profile.py:573`.

### Code integrity

No new abstraction-quality or failure-honesty defect was found. The identity reconciliation helper
has one explicit job and fails on contradictions. The neutral compiler, per-usage finalizer, and
read-only plan remain separate responsibilities. Touched production Ruff and format checks pass in
both repositories, and both `git diff --check` runs pass.

---

## Certification

- Fresh companion profile/validation/package selection: **417 passed** normally and **417 passed**
  under `python -O`.
- Fresh integrated source-identity/route/compound selection: **8 passed** normally and **8 passed**
  under `python -O`.
- Fresh TEAx execution in the documented pandas-bearing companion environment: **15 passed**
  normally and **15 passed** under `python -O`. The ordinary codegen environment still lacks
  `pandas`; that environment failure is not an implementation failure.
- Fresh exact Items 2/4/6 overlap union: **614 passed** normally and **614 passed** under
  `python -O`.
- Fresh offline skew controls: old codegen/new companion rejected v4, new codegen/old companion
  rejected v3, the resolver rejected exactly `agentic-mbse>=0.1.2` versus `==0.1.1`, and new/new
  installed successfully. Rebuilt manifest and pinned inputs exactly matched retained evidence.
- Newly proven spec criteria and equivalent behavioral plan stencils were marked complete. After
  audit, the owner removed the stored-byte provenance process gate without requesting re-audit.

**Remaining blockers:** None within Item 1's amended scope. The owner removed clean-overlay and
pre-edit-hash provenance as certification gates after this audit. Their absence remains recorded.

**Not checked:** PR/remote state beyond confirming no audit action changed it; a fresh full suite in
either repository; historical byte equality that depends on unavailable pre-edit manifests; or
clean-overlay source provenance that was not recorded when the candidates were built. These are not
required by the owner-amended Item 1 scope.
