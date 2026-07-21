# Implementation Plan: GAP-CLOSE Item 4 — Profile Default-Deny Totalization

**Status:** Complete
**Created:** 2026-07-18
**Last Updated:** 2026-07-18

## Source Documents

- **Spec:** [`spec.md`](spec.md)
- **Epic:** `../sysml-codegen/.project/backlog/epic_gap_close.md#item-4-profile-default-deny-totalization-f7-f8-promoted-diagnostics`
- **Verification:** `../sysml-codegen/.project/research/20260718_gap-review-verification.md` (F7, F8, hygiene 9)
- **Gap review:** `../sysml-codegen/.project/research/20260718-123558_constraint-expression-final-gap-review.md` (F7, F8, promoted diagnostics)
- **Inherited contract:** `../sysml-codegen/.project/active/numerical-constraint-profile/{spec,design}.md`
- **Design disposition:** No separate design by deliberate stage selection. The spec and epic fix the adjacent guard order, diagnostic outcome, and v3 boundary; this plan supplies sequencing and validation only.

## Implementation Strategy

**Phasing rationale:** First add only the six malformed-arity round trips, the contradictory serialized ratio, and the promoted-diagnostic assertions. Preserve their isolated RED output before changing production code. Then land the two adjacent guards and immediately prove the existing well-formed matrix and semantic version did not move. Finally correct promotion semantics, sync the codegen assertion, and run paired gates.

**Critical path:** RED evidence → arity and dimension guards → unchanged well-formed decisions → promoted reason/message correction → paired focused and full validation.

**First proof point:** The new codec-boundary tests fail on the current Item 4 implementation for exactly the verified reasons: malformed `xor`/`implies` warn, the contradictory ratio admits, and a promoted diagnostic retains warning semantics.

**Stop condition:** If any well-formed input changes `Eligibility`, or `PROFILE_SEMANTIC_VERSION` moves from `executable-profile/v3`, stop. Record the case and diff without adapting the expected result or continuing to codegen.

**Dirty-work discipline:** Before edits, record `git status --short`, Item 4 path diffs, and `git diff -- tests/fixtures` in both repositories. Do not stash, reset, restore, reformat unrelated files, or run fixture capture scripts. At every phase, inspect only Item 4 paths and compare fixture output with the recorded baseline.

---

## Phase 1: Isolated pre-fix RED contracts

### Goal

Add the smallest regression set that reaches all three defects through their public boundaries, then preserve the failing command output before production edits.

### Assumption Under Test

The verified failures are independently reproducible in the current dirty worktrees and do not depend on direct-only construction or unrelated GAP-CLOSE changes.

### Test Stencil (Write This First)

```python
@pytest.mark.parametrize(
    ("operator", "count"),
    [(op, n) for op in ("xor", "implies") for n in (0, 1, 3)],
)
def test_malformed_binary_connective_round_trip_blocks(operator, count):
    facts = facts_for(OperatorNode(operator=operator, operands=operands(count), operand_type=None))
    parsed = parse(serialize(facts))
    decision = evaluate_profile(parsed).decisions[0]
    assert decision.eligibility is Eligibility.BLOCK
    assert decision.diagnostics[0].reason == "block_unsupported_node"
    assert f"{count} operands, expected 2" in decision.diagnostics[0].message
```

```python
def test_contradictory_equal_unit_ratio_round_trip_blocks():
    parsed = parse(serialize(facts_for(equal_unit_ratio("LengthUnit", "TimeUnit"))))
    decision = evaluate_profile(parsed).decisions[0]
    assert decision.eligibility is Eligibility.BLOCK
    assert decision.diagnostics[0].reason == "block_derived_unit_unsupported"
```

```python
def test_numerical_containment_promotes_semantics():
    diagnostic = decide(mixed_numerical_and_boolean()).diagnostics[0]
    assert diagnostic.force == "error"
    assert diagnostic.reason == "block_non_numerical_containment"
    assert "separate" in diagnostic.message and "rewrite" in diagnostic.message
    assert "is not executed" not in diagnostic.message
```

### Changes Required

- [x] **Companion tests first:** Extend `tests/test_sysml/test_executable_profile_v3.py` with the parameterized 0/1/3 `xor`/`implies` cases using `constraint_facts.serialize()` then `constraint_facts.parse()` before `evaluate_profile()`. Add promoted cases covering each warning family that can be promoted: bare Boolean, non-numerical equality, `xor`, and `implies`.
- [x] **Ratio test first:** Extend `tests/test_sysml/test_executable_profile_arithmetic.py` with a full `ConstraintFacts` serialize/parse regression whose ratio operands carry the same exact unit and contradictory dimensions.
- [x] **Codec anchor:** Reuse the public round-trip helpers and retain the byte-identity pins in `tests/test_sysml/test_expression_ir_serialize.py` and `tests/test_sysml/test_constraint_facts_serialize.py`; do not add a codec or fact-model invariant.
- [x] **Codegen RED:** Change only the expected promoted contract in `../sysml-codegen/tests/conformance/test_constraint_non_numerical.py`; require the new blocking reason/message and forbid `"is not executed"` in the halt text.
- [x] Run each new defect selection separately on the pre-fix implementation and paste the three RED commands, failures, and exit codes into this plan's implementation notes before touching production code.

### Validation

- [x] Arity selection fails 6 cases because the decisions are not `BLOCK`; no parse/serialize failure occurs.
- [x] Ratio selection fails because the contradictory serialized ratio is `ADMIT`.
- [x] Companion promotion and licensed codegen halt selections fail only on the corrected reason/message assertions.
- [x] Existing focused profile tests remain green before production edits, proving the RED set is isolated.

**What We Know Works After This Phase:** Every requested defect has a public-boundary regression that is RED for the intended reason, with no production or fixture change.

---

## Phase 2: Adjacent arity and dimension guards

### Goal

Make malformed binary connectives and contradictory ratio facts default-deny while leaving every well-formed decision and v3 unchanged.

### Assumption Under Test

Two local ordering corrections are sufficient: an exact-two arity gate before `xor`/`implies` warning/recursion, and dimension comparison before equal-unit ratio admission.

### Test Stencil (Write This First)

```python
@pytest.mark.parametrize("operator", ["xor", "implies"])
def test_binary_connective_well_formed_decisions_stay_pinned(operator):
    assert decide(pure_boolean_binary(operator)).eligibility is Eligibility.NON_NUMERICAL
    assert decide(numerical_binary(operator)).eligibility is Eligibility.BLOCK

def test_valid_ratio_decisions_stay_pinned():
    assert decide(same_unit_same_dimension_ratio()).eligibility is Eligibility.ADMIT
    assert decide(different_unit_same_dimension_ratio()).eligibility is Eligibility.BLOCK
```

### Changes Required

- [x] **`src/agentic_mbse/sysml/executable_profile.py`:** Add the exact-two arity gate immediately inside the existing `xor`/`implies` proposition branch. Emit the adjacent connective gate's existing named `block_unsupported_node` shape with the actual count and `expected 2`; do not walk malformed operands.
- [x] **Same file:** In `_quantity_ratio_fact`, compare dimensions after malformed/unknown-unit checks and before equal exact-unit admission. Return `block_derived_unit_unsupported` for contradictory dimensions; retain the existing same-dimension/different-unit result.
- [x] Update the ratio helper docstring so its stated guard order matches the code. Do not change `REASON_CODES`, public interfaces, schema versions, or `PROFILE_SEMANTIC_VERSION`.

### Validation

- [x] New arity and ratio round-trip tests are green.
- [x] `uv run pytest tests/test_sysml/test_executable_profile.py tests/test_sysml/test_executable_profile_matrix.py tests/test_sysml/test_executable_profile_arithmetic.py tests/test_sysml/test_executable_profile_v3.py -q` is green except for the deliberately still-RED promoted-text assertions.
- [x] Compare the pre/post well-formed decision signatures for valid binary `xor`/`implies`, valid ratio families, and the frozen v3 equality/inequality matrix. Any `Eligibility` change triggers the stop condition.
- [x] `PROFILE_SEMANTIC_VERSION == "executable-profile/v3"`; expression and constraint-facts schema pins remain v1.
- [x] Item 4 path diff contains only the two guards, their docstring, and tests. Fixture diff matches the recorded baseline in both repositories.

**What We Know Works After This Phase:** Wire-valid malformed inputs block at the profile boundary, while the certified well-formed outcome matrix and all version pins are unchanged.

---

## Phase 3: Promoted diagnostic totalization and paired gates

### Goal

Make every containment-promoted warning describe a blocking mixed assertion, synchronize codegen's halt contract, and prove both repositories together.

### Assumption Under Test

Promotion can totalize the diagnostic at the existing fold point without changing traversal, containment policy, or any well-formed outcome.

### Test Stencil (Write This First)

```python
for predicate in promoted_warning_family_cases():
    decision = decide(predicate)
    assert decision.eligibility is Eligibility.BLOCK
    assert {(d.reason, d.force) for d in decision.diagnostics} == {
        ("block_non_numerical_containment", "error")
    }
    assert all("separate" in d.message and "rewrite" in d.message for d in decision.diagnostics)
    assert all("is not executed" not in d.message for d in decision.diagnostics)
```

### Changes Required

- [x] **`src/agentic_mbse/sysml/executable_profile.py`:** At the existing `contains_numerical` promotion fold, replace each non-numerical diagnostic's force, reason, and message together. **[AGENT] Plan decision:** register `block_non_numerical_containment`. Use one concise message: the numerical assertion contains a non-numerical `<construct>` and generation stops; separate it into its own assertion or rewrite it as a numerical comparison. Leave unpromoted warning reason/message text unchanged.
- [x] **`../sysml-codegen/tests/conformance/test_constraint_non_numerical.py`:** Keep the Phase 1 corrected halt assertion aligned with the companion reason/message. Do not edit codegen production for this item.
- [x] Re-run the well-formed decision comparison before any broad gate. Stop on outcome drift; expected diagnostic-only changes in already-blocked mixed assertions must be reviewed explicitly.

### Validation

**Focused and optimized:**

- [x] Companion: `uv run pytest tests/test_sysml/test_executable_profile.py tests/test_sysml/test_executable_profile_matrix.py tests/test_sysml/test_executable_profile_arithmetic.py tests/test_sysml/test_executable_profile_v3.py tests/test_sysml/test_expression_ir_serialize.py tests/test_sysml/test_constraint_facts_serialize.py -q`.
- [x] Companion optimized: repeat that selection with `uv run python -O -m pytest ...`.
- [x] Codegen focused, with the licensed sibling environment: `uv run pytest tests/conformance/test_constraint_non_numerical.py tests/conformance/test_constraint_lowering.py tests/conformance/test_constraint_migration_mapping.py tests/conformance/test_snapshot_constraint_parity.py -q`.
- [x] Codegen optimized: repeat the focused selection with `uv run python -O -m pytest ...`.

**Full and static gates:**

- [x] Companion suite of record: `uv run pytest tests/` using the repository's default non-slow selection. Do not run paid/slow corpus tests.
- [x] Licensed codegen suite of record against this companion worktree: `uv run pytest tests/` using codegen's default non-execution selection; record license skips/deselections.
- [x] `uv run mypy src/` in both repositories; no new errors. Run targeted mypy on `src/agentic_mbse/sysml/executable_profile.py` first for fast feedback.
- [x] Ruff check and format-check only the touched Python files in each repository.
- [x] Run path-scoped `git diff --check` on Item 4 files in each repository. Do not repair unrelated dirty-work whitespace.
- [x] Re-run public codec byte-identity tests. Compare `git diff -- tests/fixtures` in each repository with the recorded pre-edit output; it must be identical. No capture script or fixture rewrite is allowed for this item.
- [x] Compare final `git status --short` with the recorded baseline. All pre-existing entries remain intact; only the planned companion source/tests/plan and the one codegen conformance test may be new or changed by Item 4.

**What We Know Works After This Phase:** All three defects are green through the public codec/profile/codegen boundaries, v3 and well-formed decisions are unchanged, and the paired focused, optimized, full, static, diff, and fixture gates pass without disturbing either dirty worktree.

---

## Risk Management

- **Silent semantic expansion:** Run the well-formed decision comparison after each production hunk. Stop rather than re-pin.
- **Diagnostic partial promotion:** Test every promotable warning family and assert reason, message, and force together.
- **Codec-only blind spot:** Every malformed fact test serializes and parses `ConstraintFacts` before evaluation.
- **Cross-repository drift:** Change one codegen assertion only, then run it against the updated companion before the full licensed suite.
- **Dirty-work damage:** Use recorded path-scoped baselines and never clean, stash, reset, restore, or bulk-format.

## Implementation Notes

### Phase 1 Completion

**Completed:** 2026-07-18 16:07 PDT
**RED evidence:**
- `uv run pytest tests/test_sysml/test_executable_profile_v3.py -k malformed_binary_connective_round_trip_blocks -q` exited 1: all 6 codec-roundtrip cases returned `NON_NUMERICAL`, with no codec failure.
- `uv run pytest tests/test_sysml/test_executable_profile_arithmetic.py::test_contradictory_equal_unit_ratio_round_trip_blocks -q` exited 1: the serialized contradictory ratio returned `ADMIT`.
- `uv run pytest tests/test_sysml/test_executable_profile_v3.py -k numerical_containment_promotes_error_semantics -q` exited 1: all 4 warning families retained their `warn_*` reason after promotion.
- Licensed sibling gate, after loading `../agentic-mbse/.env`: `uv run pytest tests/conformance/test_constraint_non_numerical.py::test_malformed_numerical_fixture_halts_naming_fix -q` exited 1 because the halt retained `warn_non_numerical_predicate` and `is not executed`.
- Existing tests excluding the new RED contracts: v3 5 passed / 10 deselected; arithmetic 49 passed / 1 deselected.
**Deviations:** None.

### Phase 2 Completion

**Completed:** 2026-07-18 16:07 PDT
**Actual changes:** Added the exact-two `xor`/`implies` arity guard before warning or operand traversal; moved contradictory-dimension rejection before equal-unit ratio admission; updated the ratio guard-order docstring; added explicit valid-binary eligibility pins.
**Well-formed comparison:** Focused profile/matrix/arithmetic/v3 gate passed 127 tests with only the 4 deliberately RED promotion assertions deselected. Valid two-operand `xor`/`implies`, identical-unit ratios, differing-unit ratios, and the frozen v3 matrix retained their eligibility. `PROFILE_SEMANTIC_VERSION` remains `executable-profile/v3`; schema code and fixtures are untouched.
**Deviations:** None.

### Phase 3 Completion

**Completed:** 2026-07-18 16:13 PDT
**Gate evidence:**
- Companion focused: 168 passed. Companion optimized: 168 passed, with pytest's expected `-O` assertion warning.
- Licensed codegen focused: 69 passed. Licensed codegen optimized: 69 passed, with pytest's expected `-O` assertion warning.
- Companion suite of record: 1,524 passed / 1 skipped / 33 deselected.
- Licensed codegen suite of record: 2,511 passed / 26 skipped / 9 deselected.
- Targeted mypy with skipped imports is clean for `src/agentic_mbse/sysml/executable_profile.py`. Branch-wide mypy ran in both repositories and reproduced existing debt outside Item 4 paths: 21 companion errors in 8 files and 76 codegen errors in 17 files. Item 4 added no mypy error; codegen production was not edited.
- Ruff and format-check pass on all touched Python files. Path-scoped `git diff --check` passes in both repositories. Public expression and constraint-facts byte-identity tests are included in the 168-test focused gate.
- The post-promotion well-formed comparison is unchanged. The only changes to already-blocked mixed assertions are the intended warning-to-error reason/message corrections; eligibility remains `BLOCK`.
**Fixture/dirty-work comparison:** Fixture diffs were empty before edits and remain empty in both repositories. No capture script ran. Exact final status is recorded below; every baseline entry remains present. Item 4 adds only the companion source/tests/plan/spec status and the coordinated codegen conformance assertion.
**Deviations:** Full-repository mypy is not a green baseline in either dirty worktree. The path-scoped Item 4 type gate is clean, and no unrelated mypy debt was edited.

### Exact Cross-Repository Status Record

Pre-edit companion status:

```text
 M .project/CURRENT_WORK.md
?? .orchestrate-logs/
?? .project/active/gap-profile-totalization/
```

Final companion status:

```text
 M .project/CURRENT_WORK.md
 M src/agentic_mbse/sysml/executable_profile.py
 M tests/test_sysml/test_executable_profile.py
 M tests/test_sysml/test_executable_profile_arithmetic.py
 M tests/test_sysml/test_executable_profile_v3.py
?? .orchestrate-logs/
?? .project/active/gap-profile-totalization/
```

Pre-edit codegen status:

```text
 M .project/CURRENT_WORK.md
 M .project/backlog/BACKLOG.md
 M scripts/capture_extraction_snapshots.py
 M src/sysml_codegen/analysis/constraint_lowering.py
 M src/sysml_codegen/cli/__init__.py
 M src/sysml_codegen/contracts/verify.py
 M src/sysml_codegen/generation/modules.py
 M src/sysml_codegen/orchestration/pipeline_builder.py
 M src/sysml_codegen/resolution/models.py
 M src/sysml_codegen/snapshot/capture.py
 M src/sysml_codegen/snapshot/graph_rebuild.py
 M src/sysml_codegen/snapshot/serializer.py
 M src/sysml_codegen/templates/constraint_module.py.jinja2
 M tests/conformance/test_constraint_lowering.py
 M tests/conformance/test_seal_step9.py
 M tests/execution/test_constraint_execution.py
 M tests/unit/test_cli_generation.py
 M tests/unit/test_concrete_constraint_model.py
 M tests/unit/test_constraint_emission.py
 M tests/unit/test_predicate_compiler.py
 M tests/unit/test_verify_package.py
?? .claude/projects/
?? .project/active/gap-boundary-guards/
?? .project/active/gap-lowering-integrity/
?? .project/active/gap-runtime-contract/
?? .project/backlog/epic_gap_close.md
?? .project/research/20260718-123558_constraint-expression-final-gap-review.md
?? .project/research/20260718_gap-review-verification.md
?? src/sysml_codegen/analysis/source_referent.py
?? tests/conformance/test_constraint_lowering_integrity.py
?? tests/conformance/test_constraint_snapshot_identity.py
?? tests/unit/test_source_referent.py
```

Final codegen status is exactly the pre-edit block above plus:

```text
 M tests/conformance/test_constraint_non_numerical.py
```

---

**Status:** Complete
