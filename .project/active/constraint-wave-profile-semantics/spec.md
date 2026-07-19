# Spec: Constraint-Wave Profile Semantics

**Status:** Complete — owner waived provenance-only gates after audit; no re-audit requested
**Owner:** Reid W
**Created:** 2026-07-18 21:02 PDT
**Revised:** 2026-07-19
**Complexity:** MEDIUM
**Branch:** `constraint-exec-epic`
**Epic:** CONSTRAINT-WAVE-REMEDIATION — Item 1 (R-1, R-2)

---

## Problem

Executable-profile v3 is default-deny, but two facts captured by `ConstraintUsageFact` are not
fully classified at the profile decision boundary. Operand category is not checked for ordering,
and assertion polarity is not carried in `UsageDecision`. This leaves the public profile contract
incomplete at the boundary that guarantees every admitted assertion can execute with its modeled
meaning.

### Established facts and reproductions

- **R-1 is reproduced at the profile boundary.** On companion revision `54a95d2`, live String
  ordering (`label1 < label2`) and Boolean ordering (`armed <= ready`) both return `ADMIT` with no
  diagnostic. The current profile has the same gap: ordering calls `unit_compatibility`, which
  returns `ok` for two dimensionless non-quantity operands, but never checks whether their
  categories are numerical. The existing matrix covers compatible quantity ordering and
  integer/real ordering, not Boolean, String, enumeration, or mixed non-numeric ordering. Source:
  primary review R-1; current `src/agentic_mbse/sysml/executable_profile.py`,
  `_walk_comparison` and `unit_compatibility`; and
  `tests/test_sysml/test_executable_profile_matrix.py`.
- **R-2 is reproduced at the profile boundary.** Live extraction preserves a negated assertion as
  `is_negated=True`, but `evaluate_profile` does not read that field. Its `UsageDecision` therefore
  contains the form-selected positive source predicate IR and no classified polarity. Existing
  companion tests prove fact capture and separately test profile decisions, but do not pin a live
  or codec-roundtripped positive/negated decision matrix for both inline and definition-typed
  assertions. Source: primary review R-2; current
  `src/agentic_mbse/sysml/executable_profile.py`, `_evaluate_usage`;
  `tests/test_sysml/test_constraint_fact_shapes.py`; and
  `tests/test_sysml/test_executable_profile_v3.py`.
- **The primary review's downstream wrong-verdict premise is incorrect.** The review says the
  positive `effective_predicate` is all that codegen lowers, implying that negation is ignored.
  Sysml-codegen revision `512786c` and the current tree already apply usage polarity downstream:
  lowering derives `expected_value = not is_negated`, the catalog carries both values, and the
  compiler applies polarity when deriving status and simple margin. A direct generated-execution
  test pins a negated inline assertion's verdict and margin. The defect remains real, but it is an
  incomplete profile contract and a second semantic path, not an established downstream
  wrong-verdict. Source: sysml-codegen `constraint_lowering.py`, `generation/modules.py`,
  `generation/predicate_compiler.py`, and
  `tests/execution/test_constraint_execution.py`; reconciliation research, R-2 dataflow.
- **The runtime value path remains numerical.** The owner ratified retaining the IEEE-double
  generated data path on 2026-07-18. On 2026-07-19 the owner also ratified the agent recommendation
  that every non-whitelisted ordering category pair BLOCK as malformed numerical ordering.
  Host-language comparison behavior is not modeled semantics, and this correction does not add a
  typed runtime. The recommendation and its rationale remain agent-grade despite ratification.
- **Both corrections change the public profile contract.** The companion publishes
  `PROFILE_SEMANTIC_VERSION = "executable-profile/v3"`; sysml-codegen hard-pins that value at its
  shared live/snapshot lowering gate. The companion package is currently `0.1.1`, and codegen's
  dependency floor is `agentic-mbse>=0.1.1`. The correction therefore needs a new profile semantic
  version, a companion package release/version floor, a codegen guard update, and exact-revision
  compatibility evidence.

### Decision provenance

The owner's literal 2026-07-19 response to the agent's expanded R-1 and R-2 recommendations was:
“ok got it. agreed with both decisions. please capture in the spec/plan and proceed with
orchestration”. This approves both semantics for implementation. It does not make the expanded
formulations or their rationale owner-originated; those remain agent recommendations ratified by
the owner.

The approved recommendations make ordering admission a numerical-category whitelist and preserve
negated assertions through separate, decision-carried polarity. They do not fold polarity into the
positive source predicate IR.

## Success Criteria

- [x] No ordering assertion or negated assertion reaches code generation with operand category or
      assertion polarity left unclassified by the executable profile.
- [x] For each of `<`, `<=`, `>`, and `>=`, an exhaustive left/right matrix covers the full
      eight-category vocabulary: `boolean`, `string`, `integer`, `real`, `enum`, `quantity`,
      `unresolved`, and `unknown`. Only `(integer, integer)`, `(integer, real)`, `(real, integer)`,
      `(real, real)`, and `(quantity, quantity)` may proceed to existing numerical/unit checks.
      Every other one of the 64 ordered category pairs BLOCKs, including every numeric ×
      non-numeric pair and its reversal. Compatible exact-unit quantity and integer/real rows retain
      their current outcomes; incompatible or unprovable whitelisted rows retain their current
      distinct BLOCK reasons.
- [x] Each malformed ordering comparison produces exactly one stable reason-grade diagnostic with
      constraint identity, source location when present (using `<no location>` otherwise), and
      actionable repair text. A compound assertion with N malformed ordering comparisons produces
      N diagnostics in deterministic expression-walk order, one usage-level `BLOCK`, the same N L6
      `ERROR`s in the same order, and one codegen preflight halt before compiler or target-tree
      mutation.
- [x] `UsageDecision` and profile output classify and carry assertion polarity for every
      executable-form usage and carry or validate the corresponding expected truth. Admission
      requires `type(is_negated) is bool`: `None`, strings such as `"false"`, integers such as `0`
      or `1`, and every other non-Boolean direct or codec value produce exactly one named polarity
      diagnostic and one `BLOCK` without walking the predicate body.
- [x] Positive and negated inline and definition-typed assertions ADMIT whenever the selected
      positive predicate body admits. For the same body, the profile-selected effective IR remains
      the unchanged positive source predicate IR and has identical serialized bytes regardless of
      assertion polarity.
- [x] For positive/negated × inline/definition-typed rows, the exact serialized bytes of the
      positive source predicate remain identical across extraction or constraint-facts codec input,
      `UsageDecision`, lowering, concrete constraint and catalog entry, and the predicate compiler
      input. Live and codec routes also produce identical decisions, polarity, expected truth, and
      diagnostics.
- [x] Codegen consumes and verifies the decision-carried polarity rather than independently
      treating unclassified usage metadata as semantic authority. Decision polarity, catalog
      polarity, and `expected_value == not is_negated` agree; missing or contradictory values fail
      before compilation or target-tree mutation.
- [x] Generated paired executions use the same positive body under both polarities and satisfy the
      exact-once truth table below. Each pair has identical raw `actual_value`; positive expects
      `True`, negated expects `False`; nonzero simple margin changes sign exactly once; zero is
      normalized to `0.0`; non-finite evaluation is indeterminate for both polarities.

      | Source predicate case | Raw `actual_value`, both polarities | Positive status / margin | Negated status / margin |
      |---|---|---|---|
      | True with source margin `m > 0` | `True` | `satisfied` / `m` | `violated` / `-m` |
      | False with source margin `m < 0` | `False` | `violated` / `m` | `satisfied` / `-m` |
      | Strict boundary (`<` or `>`) | `False` | `violated` / `0.0` | `satisfied` / `0.0` |
      | Inclusive boundary (`<=` or `>=`) | `True` | `satisfied` / `0.0` | `violated` / `0.0` |
      | Non-finite operand | `None` | `indeterminate` / `None` | `indeterminate` / `None` |

- [x] `CONSTRAINT_USAGE_FACT_FIELD_CONSUMERS` is the named exhaustive consumer-completeness map,
      and `test_constraint_usage_fact_field_consumers_are_exhaustive` asserts that its keys equal
      `dataclasses.fields(ConstraintUsageFact)` exactly:
      `identity`, `location`, `source`, `owner`, `scope`, `membership_kind`, `is_negated`,
      `actuals`, `omitted_default_formals`, `predicate`, and `inherited_into`. Each key names its
      profile consumer or tested decision-irrelevant rationale. A static/test assertion fails when
      a dataclass field is added, removed, or renamed without updating that map.
- [x] The constraints guide states the selected ordering and negation behavior and contains no
      claim that contradicts the executable matrix or the separate-polarity contract.
- [x] Compatibility tests prove all three pairings: old codegen rejects the corrected companion's
      new profile semantic version; corrected codegen rejects the old companion's v3 semantic
      version; and one corrected candidate pair passes. Each candidate artifact is identified by
      package version and SHA-256 hash. Package metadata declares the raised companion floor, the
      resolved lock selects a companion version satisfying that floor, and runtime reports the
      corrected package/profile versions. Release-readiness certification is deferred to parent
      Epic Item 8.
- [x] The correction does not change the `ConstraintFacts` schema or snapshot-v3 payload shape.
      Existing facts and snapshot-v3 payloads are re-profiled under the installed corrected
      profile; their stored bytes do not pretend to encode a historical `UsageDecision`.
- [x] The companion suite, focused codegen profile/lowering/generation/execution tests, and the
      three compatibility pairings pass normally and under optimized Python where execution is
      applicable. Evidence records exact companion and codegen revisions and runs companion
      evidence first.
- [x] The R-1 and profile-level R-2 reproductions are RED on companion `54a95d2` and GREEN under
      the selected contract. Downstream R-2 evidence explicitly preserves the already-present
      codegen polarity behavior and proves the new decision-to-codegen contract.

## Known Requirements

- **[INFERRED]** Ordering is executable only for integer/real pairs and compatible exact-unit
  quantity pairs. Every other category pair BLOCKs as malformed numerical ordering; host-language
  comparison behavior does not widen the profile. Agent recommendation in the 2026-07-19
  reconciliation, ratified by the owner through the response recorded in Decision provenance.
- **[INFERRED]** Negated assertions remain supported by preserving the positive source predicate
  and carrying assertion polarity separately through the profile decision. Agent recommendation in
  the 2026-07-19 reconciliation, ratified by the owner through the response recorded in Decision
  provenance.
- **[NEED]** Supported modeled assertions execute for each concrete design state. Original owner
  concept: `../sysml-codegen/.project/concepts/constraint-execution-and-design-space-studies.md`,
  Goals.
- **[NEED]** Predicate meaning, bindings, concrete context, polarity, and result evidence survive
  into execution instead of being copied into or reinterpreted by study code. Original owner
  concept: `../sysml-codegen/.project/concepts/constraint-execution-and-design-space-studies.md`,
  Problem, Design Principles 2–3, and Required Invariants.
- **[NEED]** A false supported predicate is evaluation evidence, not an execution failure; study
  policy remains separate from modeled assertion meaning. Original owner concept:
  `../sysml-codegen/.project/concepts/constraint-execution-and-design-space-studies.md`, Design
  Principles 1 and 4.
- **[HARD]** Profile admission is a total compiler contract. An unrecognized, unresolved,
  incompatible, unsupported, or polarity-unknown executable row cannot be admitted by fallthrough.
  Ordering uses the category whitelist above, and executable assertion polarity must be an actual
  Boolean. Current v3 invariant I1 and the compiler's float/unit behavior force this boundary.
- **[HARD]** Profile and codegen use one assertion meaning: the decision-selected positive source
  predicate bytes plus decision-carried polarity. Those bytes remain unchanged through the
  decision, lowering, concrete/catalog, and compiler seams. Polarity is applied exactly once when
  codegen derives status and simple margin; raw `actual_value` stays the source predicate result.
- **[HARD]** Live and snapshot routes share the same profile and lowering gate. A decision change
  therefore changes both routes and must preserve codec parity rather than adding capture-time
  semantics to snapshots.
- **[HARD]** A profile decision change bumps `PROFILE_SEMANTIC_VERSION`. The current sysml-codegen
  guard intentionally rejects any value other than `executable-profile/v3`; silently retaining v3
  would hide a changed public decision procedure.
- **[HARD]** The coordinated compatibility boundary includes the companion package version, the
  sysml-codegen dependency floor and resolved lock, the profile-version guard, both version-skew
  rejection directions, and one passing companion/codegen candidate pair whose artifacts are
  identified by package version and SHA-256 hash. The companion suite runs before its consumers.
- **[INFERRED]** Item 1 proves candidate-pair compatibility; parent Epic Item 8 owns
  release-readiness certification. This is an agent-authored scope correction surfaced by
  design-review M1 on 2026-07-19, not an owner-originated decision.
- **[INHERITED]** Numerical ordering over integer/real operands and quantities with identical,
  structurally proven exact units remains admitted. Required conversion, incompatible dimensions,
  unknown exact units, unresolved operands, malformed operand facts, and unsupported derived units
  retain their existing distinct outcomes. Source: numerical-profile spec/design and current v3
  matrix. The admitted-set details originated as agent recommendations ratified by the owner on
  2026-07-18 and remain agent-grade.
- **[INHERITED]** Profile outcomes remain `ADMIT`, `BLOCK`, `NON_NUMERICAL`, and `UNASSESSED`;
  `BLOCK` means generation error and `NON_NUMERICAL` means warn-and-catalog. Source:
  numerical-profile design D1/D4–D6. These mechanisms are agent-grade, including ratified items.
- **[INHERITED]** Inline and definition-typed assertions are the executable source forms.
  Assert-by-reference blocks; satisfy, require/assume, and plain usages remain unassessed. Source:
  completed executable-profile spec/design and current code.
- **[INFERRED]** R-1 and R-2 diagnostics should extend the current reason-grade diagnostic model
  rather than create a parallel channel. This follows the requirement for consistent L6/codegen
  behavior; exact reason-code spelling and repair wording are design work.

## Non-Goals

- Non-numerical equality execution, tolerance semantics, or general typed-value expansion.
- Defining Boolean, String, enumeration, or host-language ordering semantics. These categories are
  malformed numerical ordering under R-1.
- Folding assertion polarity into or otherwise rewriting the form-selected positive source
  predicate IR. R-2 keeps polarity as a separate classified value.
- Temporal monitoring, requirement-satisfaction execution, study policy, or optimizer behavior.
- Profile feature expansion beyond the R-1/R-2 correction selected here.
- Reworking unrelated expression nodes, actual resolution, occurrence identity, snapshot format,
  generated-name safety, package sealing, or the remaining PR-wave findings.

## Open Questions / Deferred to design

- Choose the exact R-1 and malformed-polarity diagnostic codes and repair wording within the current
  reason-grade diagnostic model.
- Choose whether `UsageDecision` carries both polarity and derived expected truth or carries
  polarity and validates expected truth at the consumer boundary. Either design must preserve one
  authoritative application path and reject missing or contradictory values.
- Define the exact public field names, construction invariants, exhaustive consumer checks, and
  matrix-test organization for decision-carried polarity without changing the selected semantics.
- Choose documentation wording and the exact new profile semantic/package version identifiers.

---

## Related Artifacts

- **Epic:** `../sysml-codegen/.project/backlog/epic_constraint_pr_wave_remediation.md`, Item 1
- **Required Reading:**
  - `../sysml-codegen/.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md`,
    R-1, R-2, recommendations, and open questions
  - `../sysml-codegen/.project/research/20260719-065712_constraint-profile-semantics-and-license-reconciliation.md`
  - `../sysml-codegen/.project/active/numerical-constraint-profile/spec.md`
  - `../sysml-codegen/.project/active/numerical-constraint-profile/design.md`, D2 and I1–I4
  - `../sysml-codegen/.project/concepts/constraint-execution-and-design-space-studies.md`, original
    owner concept
  - `../sysml-codegen/.project/concepts/constraint-execution-and-design-space-studies-claude.md`,
    executable-profile, negation, and invariants sections
  - `.project/reference/constraint-execution-concept.md`, executable-profile, polarity, and
    invariants sections
  - `.project/completed/20260713_executable-profile/spec.md`
  - `.project/completed/20260713_executable-profile/design.md`
- **Owner-ratified agent records:**
  - `../sysml-codegen/.project/active/numerical-constraint-profile/spec-review.md`
  - `../sysml-codegen/.project/active/numerical-constraint-profile/design-review.md`
- **Current spec review:** `.project/active/constraint-wave-profile-semantics/spec-review.md`
- **Current design review:** `.project/active/constraint-wave-profile-semantics/design-review.md`, M1
- **Current companion surfaces:**
  - `src/agentic_mbse/sysml/executable_profile.py`
  - `tests/test_sysml/test_executable_profile_matrix.py`
  - `tests/test_sysml/test_executable_profile_v3.py`
  - `tests/test_sysml/test_constraint_fact_shapes.py`
  - `docs/patterns/constraints.md`
- **Downstream compatibility surfaces:**
  - `../sysml-codegen/src/sysml_codegen/analysis/constraint_lowering.py`
  - `../sysml-codegen/src/sysml_codegen/generation/modules.py`
  - `../sysml-codegen/src/sysml_codegen/generation/predicate_compiler.py`
  - `../sysml-codegen/tests/conformance/test_constraint_lowering.py`
  - `../sysml-codegen/tests/execution/test_constraint_execution.py`
- **Design:** `.project/active/constraint-wave-profile-semantics/design.md` (after spec review)

---

**Next Steps:** Rerun `my-spec-review` against the revised owner-ratified agent recommendations.
After the spec review is resolved, proceed to `my-design`.
