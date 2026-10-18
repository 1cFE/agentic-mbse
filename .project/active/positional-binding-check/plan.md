# Implementation Plan: Positional-binding hazard and check (EXEC-SUBSET-CONTRACT Item 4)

**Status:** Implementation in progress (Phases 1-3 done)
**Created:** 2026-10-18
**Last Updated:** 2026-10-18
**Branch:** `positional-binding-check` (base `main` at `ccd57d83`)

## Source Documents

- **Spec:** `.project/active/positional-binding-check/spec.md` (revised after review)
- **Design:** `.project/active/positional-binding-check/design.md`, revision 1. Component details, types, decisions D1–D22, invariants I1–I8 and Appendices A–C live there. This plan links to them and does not restate them.
- **Design review and resolutions:** `.project/active/positional-binding-check/design-review.md`
- **Observed SysIDE 0.8.4 behavior:** `.project/active/positional-binding-check/learning-findings.md`, pinned by `tests/learning/test_syside_input_redefinition.py` (43 tests)
- **Gates and owner boundary:** `.project/active/positional-binding-check/briefs/align.md`

## The Point

In SysML v2, an unprefixed input on a calculation or constraint usage, such as `in b = 3;`, binds to the definition's parameter by position, not by name (KerML 8.3.3.3.4, `checkFeatureParameterRedefinition`). An author who writes correctly named inputs in a different order than the definition gets a silent swap. The model is valid SysML and nothing warns.

The swap gives wrong values, and the two execution routes disagree. For `calc def Sub { in a; in b; return r = a - b; }` with the inputs written in reverse order, native SysIDE 0.8.4 gives -7 and sysml-codegen `b5663c07` with TEAx gives 7. So a generated run passing says nothing about native correctness. fusion-tea `f96ad312` has 125 such mismatches whose value effect is unknown. sysml-codegen has known about the behavior since July, but nothing reached authors.

This item gives authors that warning. It adds one L2 check (`L2_POSITIONAL_BINDING`), the fixtures that prove it, a semantic-hazard register entry and guidance edits. The policy is D1 `[AGENT] (ratified by owner, 2026-10-15)`: new mismatches block; explicitly pinned legacy mismatches warn until migration; a pin certifies neither native values nor agreement between routes. That a pinned warning does not by itself fail L2 is `[AGENT]` (spec review L2-2, decided by the orchestrator as execution of D1). An inspection failure never reads as clean (epic principle 5).

The work must not change how either route binds (gate R4-2), must not edit fusion-tea (R4-3), must not touch sysml-codegen or any Item 2 artifact (owner boundary, `briefs/align.md`), and must not describe fusion-tea as clean. What the check would mean for fusion-tea when it moves its agentic-mbse pin is measured here as evidence. Acting on it is the owner's item under R4-3.

## Implementation Strategy

**Phasing rationale.** The hard part is reading SysIDE correctly; everything after that is pure code. So the plan proves the reading first, then builds outward:

1. Phase 1 records the test baseline and settles the remaining SysIDE questions before any code. The main one: does `validate` reject the `out_before_in` model at L1? L1 reads only parser diagnostics, and the error SysIDE gives for it is probably semantic.
2. Phases 2 and 3 build the fact layer and the pure rule, with the fixture suite from design Appendix A. By the end of Phase 3, the 17 prototype cases and every new fixture give their exact expected identities. That is the first proof point.
3. Phase 4 adds the pin list as pure parsing plus discovery.
4. Phase 5 wires everything into L2 and the CLI, and runs the existing fixtures through the check.
5. Phase 6 reproduces the prototype's tree results. This is the premise check against real consumer trees. It comes after L2 integration because the reproduction runs the production `validate` path.
6. Phases 7 and 8 write the shipped text: the register first, because the guidance edits link to it.

**Critical path.** Phase 1 → 2 → 3 → 5 → 6. Phase 4 can be built alongside Phase 3; it only needs the `FindingIdentity` type. Phases 7 and 8 need Phase 6's numbers and paths for the register, but the guidance edits in Phase 8 need only the register's anchor.

**First proof point.** End of Phase 3: `uv run pytest tests/test_validation/test_positional_binding.py` passes, with exact identity sets for all 17 prototype fixtures, the 9 the naive control got wrong marked as such, and the Appendix A cases. If the extractor plus rule cannot reproduce `04-detector-fixtures.log` there, nothing later is worth building.

**Biggest risks.**
- The fusion-tea run (Phase 6) gives a different identity set than the prototype's 125, or dc3 is not zero. That is a premise surprise: stop and surface (see "Premise-surprise rule" below).
- Guidance edits (Phase 8) break sysml-codegen's conformance test, which reads this checkout. Invariant I8 lists every rule; the test is run read-only as evidence.
- Existing fixtures gain positional or unverifiable findings (Phase 5). Each is listed and justified before any test expectation changes.

### What "green" means at the end of every phase

Every phase ends with all three of these true. The phase's checkboxes include them; they are not repeated in full each time.

- **G1. No new test failures versus `ccd57d83`.** Run `uv run pytest tests/` and compare the failing node IDs with the baseline recorded in Phase 1 (`evidence/baseline-ccd57d83.md`). Any failure not in the baseline is a regression, unless the phase's own tests list it as an expected, justified change.
- **G2. Every new or modified file is clean under ruff.** `uv run ruff check <files>` and `uv run ruff format --check <files>`, for exactly the files the phase touched. Format a file with `uv run ruff format <file>` one file at a time. **Never run repo-wide `ruff format`**: it rewrites unrelated files.
- **G3. Every new or modified Python file is clean under mypy.** For `src/`: `uv run mypy src/` reports no error in a touched file, and its total error count is not above the Phase 1 baseline (the learning test found 97 pre-existing errors in `src/`; Phase 1 records the exact count). For tests and scripts: `uv run mypy --follow-imports=silent <files>` reports no errors.

Get the touched-file list with `git diff --name-only ccd57d83 -- src tests scripts` plus untracked files.

**Do not commit the unrelated working-tree changes** present at plan time (`.gitignore`, `.project/EPIC_GUIDE.md`, `.project/README.md`, `.project/active/README.md`, `.project/backlog/README.md`, `.project/epic_template.md`). They are not this item's. Stage files by name.

### Premise-surprise rule

`[INHERITED: align record]` If the fusion-tea run differs from the 125 prototype identities, or either dc3 tree is not zero findings and zero unverifiable, the implementer stops. Do not tune the detector, the rule, the reference builder or the pin list toward the expected numbers. Write the itemized difference (added, missing, changed target) to the evidence log, record it under Implementation Notes, and end the session by surfacing it to the orchestrator or owner. The same applies to any other place this plan says "surface": record the observation and its evidence, do not patch around it.

### Spec criteria, labelled for tracing

The spec's success criteria have no IDs, so this plan labels them by section and bullet order. Each phase's done condition cites these labels.

| Label | Spec criterion (short) |
|---|---|
| Det-1 | Fixture set covering 17 prototype cases; exact identity sets per fixture |
| Det-2 | The 9 cases the naive name-set control got wrong |
| Det-3 | Mixed spelling and reversed deliberate rename |
| Det-4 | Requirement and case parameter fixtures |
| Det-5 | dc3 out-of-order and dc3 swap fixtures |
| Det-6 | Valid shapes near the old heuristic (`inherit_def_extends`, extra inputs, `def_adds_first_input`, `out_before_in`) |
| Det-7 | Multiple-types fixture with a stated result |
| Det-8 | Existing fixtures run through the check; new findings listed and justified |
| Pol-1 | Unpinned ERROR fails; pinned WARNING passes; changed target = new ERROR + stale; unmatched pin = stale and fails |
| Pol-2 | No pin list = all ERROR; malformed, unreadable or headerless list = reported error |
| Pol-3 | Partial scope: out-of-scope pins counted, not stale; in-scope unmatched pin still stale |
| Pol-4 | Pinned message and register say a pin certifies nothing; summary reports pinned count separately |
| Pol-5 | Every other L2 code keeps its pass/fail behavior |
| Insp-1 | Injected read failures give `L2_CHECK_UNVERIFIABLE`, L2 fails, other owners still reported, pins cannot downgrade |
| Insp-2 | Unverifiable only from real evidence failure; `inherit_def_extends` must pass |
| Insp-3 | Inputs-inspected metric; zero inspected fails a consumer reproduction |
| Base-1 | fusion-tea pin list built from the prototype log: 125 distinct identities |
| Base-2 | `run_trees.py` reproduction: fusion-tea comparison, dc3 zero, inspected counts, fusion-tea L2 with and without the check |
| Base-3 | Slow pytest wrapping the comparison, skipping with a named reason |
| Base-4 | Mutation (new ERROR) and stale (rewrite to `in :>>`) runs in the evidence log |
| XR-1 | Four-spelling native evaluation pytest (7, -7, 7, 7) |
| XR-2 | Generated/TEAx side as a script plus captured log |
| Reg-1 | `docs/patterns/semantic-hazards.md` positional entry, shipped, with path and constraint-name test |
| Reg-2 | Guidance files teach by-name or definition order, qualify "Order does not matter", link the register |
| Reg-3 | New or changed SysML examples parse and have their stated positional findings |
| Reg-4 | Draft upstream finding for sysml-codegen, linked and marked unfiled |
| Repo-1 | `pytest`, `mypy src/`, `ruff check` pass; evidence states licence-dependent and slow tests |

---

## Phase 1: Baseline and fixture truth

### Goal

Record what "no new failures" is measured against, and settle the SysIDE questions the design left for this phase, before writing production code. Nothing here changes `src/`.

### Assumption Under Test

- `validate` rejects `out_before_in` at L1. **Expected (unverified): it does not.** `SysideAdapter.load_model` uses `syside.try_load_model`, which returns a model despite semantic errors, and L1 reads only `diagnostics.parser` (`level1_syntax.py:72-79`). The `redefinition-direction-conformance` error is very likely in `diagnostics.sema`.
- A library formal such as `Requirements::RequirementCheck::subj` reads `SubjectMembership` as its owning membership (bet B3, needed by D20's special-slot reason).
- An `inout` input gets implied redefinitions the same way an `in` input does.
- `str(element.qualified_name)` spells quoted names the same way the prototype log does, and is stable across two loads (bet B4).
- An anonymous `assert constraint : Le { ... }` owner gives `ElementRef.qualified_name is None` through `_element_ref` (D9).
- The 17 prototype detector fixtures and `gen_reversed/`, `gen_byname/` load with no parser or semantic errors, and natively evaluate to the recorded values.

### Test Stencil (Write This First)

```python
# tests/learning/test_syside_input_redefinition.py (append, new section "Plan phase 1")
def test_p1_library_subject_formal_reads_subject_membership():
    model = load_inline("requirement def R { subject v; in lo; }")
    v = feature(model, "P::R::v")
    (target,) = implied_redefinition_targets(v)
    assert str(target.qualified_name) == "Requirements::RequirementCheck::subj"
    assert isinstance(target.owning_membership, syside.SubjectMembership)

def test_p1_inout_inputs_are_redefined_by_position():
    model = load_inline("calc def S { inout a; inout b; } part q { calc c : S { inout b = 3; inout a = 10; } }")
    assert implied_targets(model, "P::q::c::b") == ["P::S::a"]

def test_p1_quoted_qualified_names_match_the_prototype_log_spelling():
    ...  # owner in package with a quoted calc def name, two loads, equal strings, matches log form
```

```python
# tests/test_validation/test_positional_binding_native_values.py (NEW; XR-1)
@pytest.mark.parametrize("spelling, expected", [("in_order", 7), ("reversed", -7), ("reversed_byname", 7), ("rename", 7)])
def test_sub_native_value(spelling, expected):
    assert evaluate_r(FIXTURES / "native_values" / f"sub_{spelling}.sysml") == expected

def test_mixed_spelling_has_no_native_value():
    assert evaluate_r(FIXTURES / "native_values" / "sub_mixed.sysml") is None
```

### Changes Required

**See `design.md` for:** Implementation Notes (the two learning-test lines), Next-Stage Handoff ("First plan phase"), Appendix A row `out_before_in`, Validation Approach "Cross-route".

#### 1. Baseline
**File:** `.project/active/positional-binding-check/evidence/baseline-ccd57d83.md` (NEW)
- [x] Confirm the branch has no product change yet: `git diff --stat ccd57d83 HEAD -- src scripts docs skills agents project_templates` is empty, and under `tests/` only `tests/learning/` differs. Run from the repo root (pathspecs are relative to the current directory).
- [x] Run `uv run pytest tests/ --ignore=tests/learning` on HEAD. Because nothing else differs, this is the `ccd57d83` result. Record pass/fail/skip counts and every failing node ID.
- [x] Run `uv run mypy src/` and record the error count. Run `uv run ruff check src/ tests/` and record the result.
- [x] Record the SysIDE version, `uv run python -c "import agentic_mbse; print(agentic_mbse.__file__)"`, and whether `SYSIDE_LICENSE_KEY` is set (yes/no only, never the value).

#### 2. The L1 question
**File:** `tests/fixtures/positional_binding/l1/out_before_in.sysml` (NEW), with a header citing learning-findings R4
- [x] Write the fixture from design Appendix A.
- [x] Run `uv run agentic-mbse validate --level=1 tests/fixtures/positional_binding/l1/` and record exit code and output in `evidence/phase1-fixture-truth.md`.
- [x] ~~**If L1 fails it:** add a test in `tests/test_validation/test_positional_binding.py` asserting L1 fails (Det-6). Done.~~ Not applicable: L1 passes it.
- [x] **If L1 passes it (expected):** do not write the L1-rejection test and do not turn the fixture into an L2 pass/flag fixture. Record what L1, and a full `validate`, report for it (including any positional finding once Phase 5 exists). Surface it as an owner item in Implementation Notes: the design's expected result for this row does not hold, and the honest fix is the proposed `VALIDATE-SEMA-DIAGNOSTICS` follow-up, not this item. Continue with Phase 2; nothing else depends on this row. Det-6 for `out_before_in` stays open until the owner decides.

#### 3. Learning-test lines
**File:** `tests/learning/test_syside_input_redefinition.py` (MODIFY: new section "Plan phase 1")
- [x] B3 library formal membership (stencil above). If the library formal does not read `SubjectMembership`, record it: D20 then needs a different role read for library targets. Surface it; the finding itself is unaffected (design B3).
- [x] `inout` positional redefinition.
- [x] B4 quoted names: one model with a quoted package or def name, loaded twice. Assert equal `str(qualified_name)` and the spelling form the log uses, for example `integrated_heat_electricity::'Network Heat Driven Closure'::divertor_available_in`.
- [x] Anonymous `assert constraint` owner: `subset_extraction._element_ref` gives `qualified_name is None`.
- [x] Update `learning-findings.md` with a "Plan phase 1" section recording each result.

#### 4. Retained prototype models and native values
**Files:** `tests/fixtures/positional_binding/native_values/` (NEW): `sub_in_order.sysml`, `sub_reversed.sysml`, `sub_reversed_byname.sysml`, `sub_rename.sysml`, `sub_mixed.sysml`, plus copies of `04-fixtures/gen_reversed/` and `04-fixtures/gen_byname/`, each with a header citing its prototype source path
- [x] Write `tests/test_validation/test_positional_binding_native_values.py` (stencil above). Evaluate with `Compiler.evaluate_feature`, as `04-eval.py:46-54` does. Add `gen_byname` → 7 and `gen_reversed` → -7.
- [x] Load each of the 17 files in `04-fixtures/detector/` and record in `evidence/phase1-fixture-truth.md` whether each has parser or semantic diagnostics. Any with errors are surfaced before Phase 3 copies them.

#### 5. Consumer-tree facts for later phases (read-only)
- [x] `git -C /home/reid/src/fusion-tea ls-tree --name-only f96ad312` and `git -C ... ls-tree f96ad312 work/BACKLOG.md .claude .agentic-mbse/install.json`. Record which project-root markers the export will carry. Run 3 in Phase 6 depends on it.
- [x] `git -C /home/reid/src/dc3 cat-file -e 60b44d5:designs/ac_coupled/ac_facility.sysml` (adjust for `models/` prefix) and the WI-008 files at `808464d`, so Phase 2's dc3 fixtures cite paths that exist.
- [x] Confirm `scripts/subset_profile/probe.py` still has `export_tree`, `git`, `resolve_rev` and `sibling_state` (lines 83–102 at plan time).

### Validation

**Automated:**
- [x] `uv run pytest tests/learning/ tests/test_validation/test_positional_binding_native_values.py` → pass
- [x] G1, G2, G3 (for the learning test file and the new test module)

**Manual:**
- [x] `evidence/baseline-ccd57d83.md` and `evidence/phase1-fixture-truth.md` exist and state each answer above.

**Done when (traces to XR-1, Det-6 for `out_before_in`):** the baseline is recorded; the native-values test passes with 7, -7, 7, 7, `None` for mixed, and the two gen fixtures; each phase-1 assumption has a recorded answer; any answer that contradicts the design is in Implementation Notes as a surfaced item.

---

## Phase 2: Fact types, extractor and fixtures

### Goal

Build the one new fact: for each authored input of a calc or constraint owner, its declared name, direction, role and every resolved redefinition marked implied or explicit. Include the placeholder test (D19), so an owner whose type did not resolve becomes a failure instead of a clean owner of new parameters. Write the Appendix A fixtures now, because the extractor tests read them.

### Assumption Under Test

The SysIDE observations in `learning-findings.md` (R1–R6, M1, S4) hold when read through production code paths (`SysideAdapter`, `_element_ref`, `safe_location`), not only through the learning test's inline helpers. In particular, the `owning_relationship is None` test separates every M1 placeholder shape from every resolved target in the fixture set.

### Test Stencil (Write This First)

```python
# tests/test_sysml/test_parameter_redefinition_extraction.py (NEW)
def test_mixed_spelling_gives_b_an_implied_target_and_the_by_name_input_an_explicit_one():
    facts = extract(FIX / "spelling" / "mixed_spelling.sysml")
    b = only(facts, declared_name="b")
    assert [(r.formal.qualified_name, r.origin) for r in b.redefinitions] == [("P::Sub::a", Origin.IMPLIED)]
    anon = only(facts, declared_name=None)
    assert [(r.formal.qualified_name, r.origin) for r in anon.redefinitions] == [("P::Sub::a", Origin.EXPLICIT)]

def test_unresolved_owner_type_is_a_failure_and_its_inputs_are_not_facts():
    facts = extract(FIX / "unresolved" / "unresolved_type.sysml")
    assert {f.cause for f in facts.failures} == {RedefinitionFailureCause.UNRESOLVED_OWNER_TYPE}
    assert not [f for f in facts.facts if f.owner.qualified_name == "P::q::c"]

def test_raising_heritage_read_fails_one_input_and_keeps_the_rest():
    facts = extract(FIX / "prototype" / "calc_reversed.sysml", read_heritage=raise_for("b"))
    assert causes(facts) == [RedefinitionFailureCause.REDEFINITIONS_UNREADABLE]
    assert [f.declared_name for f in facts.facts] == ["a"]
```

### Changes Required

**See `design.md` for:**
- Fact, failure and aggregate types → `design.md#data-model`
- Owner enumeration, reads and seams → D3, D4, D5, D19; Component Overview `parameter_redefinition_extraction.py`
- Reuse of Item 1 helpers → D2; the private-import precedent at `subset_extraction.py:42-46`
- Direction and name reads → Implementation Notes (first two bullets)
- Relation to Item 1's `formal_targets` → D21

#### 1. Fixtures
**Directory:** `tests/fixtures/positional_binding/` (NEW). One file per Appendix A row. Each file opens with a comment header listing its expected identities (owner|input|target), reasons and unverifiable results, and its source (prototype path, learning-test name, or dc3 revision and path).
- [x] `prototype/`: copy the 17 files from `04-fixtures/detector/`, adding the header from `04-detector-fixtures.log` expanded per target (Appendix A row 1). Mark the 9 cases `04-detector-naive-control.log` got wrong with `naive-control: wrong` in the header.
- [x] `spelling/`: `mixed_spelling`, `reversed_deliberate_rename`.
- [x] `types/`: `multiple_types_with_rename`, `subpart_restated_type_swap`, `subpart_deliberate_rename`, `usage_extra_inputs`, `def_adds_first_input`. (`multiple_types` is one of the 17.)
- [x] `requirements/`: `requirement_subject_renamed`, `requirement_actor`, `case_actor`, `requirement_stakeholder`, `requirement_in_param_swapped`, `requirement_nested_constraint_reversed`, `requirement_def_without_subject`, `case_def_without_subject`, `anonymous_assert_reversed`. Usage fixtures restate the subject, and any actor or stakeholder, before ordinary inputs (design Implementation Notes).
- [x] `dc3/`: `dc3_wi008_out_of_order`, `dc3_serial_path_swap`, each a minimal model citing its dc3 revision and path (D22).
- [x] `unresolved/`: `unresolved_type` (calc and constraint), `unresolved_supertype`, `unresolved_input_redefinition`.
- [x] `partial_run/defs/` and `partial_run/designs/` (non-self-contained), and `partial_scope/` (a self-contained subfolder layout for Phase 5's scope test, inputs bound to valued attributes so `LITERAL_BINDING` does not mask results).
- [x] Use unquoted package names in new fixtures. `requirement_def_without_subject` and `case_def_without_subject` carry SysIDE semantic errors by design (learning-findings M4); their headers say so.

#### 2. Fact types
**File:** `src/agentic_mbse/sysml/parameter_redefinition_facts.py` (NEW)
- [x] Types exactly as `design.md#data-model`, with the sort orders stated there. Module docstring states the L2-internal status (D1). Imports nothing from SysIDE (I6).

#### 3. Adapter map
**File:** `src/agentic_mbse/sysml/syside_adapter.py` (MODIFY: closed type map at `:172-283`, enumeration table at `:150-169`)
- [x] Add `Redefinition`, `SubjectMembership`, `ActorMembership`, `StakeholderMembership` to the closed map and its licence-free name set (D5).
- [x] Record the four `include_subtypes=True` sweeps in the enumeration table.

#### 4. Extractor
**File:** `src/agentic_mbse/sysml/parameter_redefinition_extraction.py` (NEW)
- [x] `extract_parameter_redefinitions(model, *, list_owners=..., read_owned_features=..., read_heritage=...)` per Component Overview. Order: enumerate and de-duplicate owners (D5); tier guard (D4); owner placeholder test (D19); list `in`/`inout` owned features; role from owning membership; redefinitions from `heritage` filtered to `Redefinition` (D3); per-input placeholder test (D19); target owning type, name and role.
- [x] Every owner and input yields exactly one fact or one failure (I4). A failure on one owner does not stop the others.

#### 5. Extractor tests
**File:** `tests/test_sysml/test_parameter_redefinition_extraction.py` (NEW)
- [x] Stencil cases above, plus: every failure cause reachable through a seam or fixture (`OWNERS_UNLISTED`, `INPUTS_UNLISTED`, `REDEFINITIONS_UNREADABLE`, `UNRESOLVED_OWNER_TYPE` for typo type and unresolved supertype, `UNRESOLVED_INPUT_REDEFINITION`, `partial_run/designs/` alone giving unverifiable owners).
- [x] Tier guard with a stub owner reading `StandardLibrary` (R6: the sweeps never return one, so the guard is tested by stub, never by expecting library owners).
- [x] Roles on the requirement fixtures; `owning_type` is a usage in `subpart_restated_type_swap` (S4).
- [x] D2: `subset_extraction._element_ref` and `subset_extraction._IdentityError` exist.
- [x] D21: for each constraint-usage input in the constraint fixtures, Item 1's `ActualFact.formal_targets` equals this fact's full target set (both origins). Read Item 1's facts; do not edit Item 1's modules. If they differ, record and surface; do not change either module to make them agree.
- [x] Facts and failures come out in the stated sort order; two extractions of one model are equal (I5).

### Validation

**Automated:**
- [x] `uv run pytest tests/test_sysml/test_parameter_redefinition_extraction.py tests/learning/` → pass
- [x] G1, G2, G3

**Manual:**
- [x] `git diff ccd57d83 -- src/agentic_mbse/sysml/subset_*.py src/agentic_mbse/sysml/fact_refs.py src/agentic_mbse/sysml/*_extraction.py` shows no change to Item 1's modules (only the two new files).

**Done when (traces to Det-1 fixture set, Insp-1 and Insp-2 at the fact level):** every Appendix A fixture exists with its header; the extractor yields the redefinitions the learning test observed; every M1 shape is a failure; the D21 consistency test passes or its difference is surfaced.

---

## Phase 3: The pure rule and the fixture suite

### Goal

Implement `decide` without pins: the rule's step order, D6–D9 and D20. Then assert the exact identity set for every fixture. This is the first proof point.

### Assumption Under Test

The finding rule over resolved redefinitions reproduces the prototype's 17 results (`04-detector-fixtures.log`) and the learning-test expectations, and a detector that compares name sets fails the suite.

### Test Stencil (Write This First)

```python
# tests/test_validation/test_positional_binding_rule.py (NEW; pure, no SysIDE)
def test_other_inputs_explicit_redefinition_does_not_exempt_b():
    facts = facts_of(input_("b", implied("P::Sub::a", "a")), input_(None, explicit("P::Sub::a", "a")))
    assert identities(decide(facts)) == {("P::q::c", "b", "P::Sub::a")}

def test_special_role_target_gets_special_slot_reason():
    facts = facts_of(input_("lo", implied("Requirements::RequirementCheck::subj", "subj", role=SUBJECT)), owner="P::X")
    (f,) = decide(facts).findings
    assert f.reason is FindingReason.SPECIAL_SLOT

# tests/test_validation/test_positional_binding.py (NEW; fixture suite)
@pytest.mark.parametrize("fixture", all_fixtures(), ids=str)
def test_fixture_gives_exactly_its_header_identities(fixture):
    expected = parse_header(fixture)
    result = decide(extract_parameter_redefinitions(load(fixture.load_root)))
    assert identity_set(result) == expected.identities
    assert reasons(result) == expected.reasons
    assert unverifiable(result) == expected.unverifiable
```

### Changes Required

**See `design.md` for:** the rule and its step order → Core Concept, Implementation Notes (step list); D6, D7, D8, D9, D20; `PositionalFinding`, `PositionalResult`, `InputOutcome` → `design.md#data-model`.

#### 1. Decision module (rule part)
**File:** `src/agentic_mbse/validation/positional_binding.py` (NEW)
- [x] `FindingReason`, `PositionalFinding`, `PositionalResult`, `InputOutcome`, and `decide(facts, pins=None, validated_files=())`. In this phase `pins` is always absent, so `pinned` is always false and `stale`/`out_of_scope` are empty.
- [x] Step order exactly as Implementation Notes. One outcome per inspected input, with the prototype's outcome names.
- [x] Imports neither SysIDE nor the filesystem (I6). `FindingIdentity` is defined in `positional_pins.py` per the design; if Phase 4 is not started yet, create that module with only `FindingIdentity` now.

#### 2. Pure rule tests
**File:** `tests/test_validation/test_positional_binding_rule.py` (NEW)
- [x] Each step of the rule; D6 (one finding per target, multiple-typed and S4 row 3 give two per input); both D7 branches; D8 (`anonymous_target`); D9 (no qualified name → identity `None`); D20 (`SPECIAL_SLOT` for subject, actor and stakeholder targets, user and library); role exclusion; sorted output.

#### 3. Fixture suite
**File:** `tests/test_validation/test_positional_binding.py` (NEW, or extend the Phase 1 file if it already holds the L1 test)
- [x] Parametrized over every fixture under `tests/fixtures/positional_binding/` except `native_values/`, `l1/` and `baselines/`. Multi-file fixtures load their whole directory.
- [x] A naive-control test: for each fixture marked `naive-control: wrong`, a name-set comparison (input names versus definition formal names) gives a different result from the header. This shows the suite would fail such a detector (Det-2). Assert the count is 9.
- [x] `inherit_def_extends` gives no finding and no unverifiable result (Insp-2).

### Validation

**Automated:**
- [x] `uv run pytest tests/test_validation/test_positional_binding.py tests/test_validation/test_positional_binding_rule.py` → pass
- [x] G1, G2, G3

**Manual:**
- [x] Compare the 17 prototype results with `04-detector-fixtures.log` line by line; any difference is surfaced, not fixed in the header.

**Done when (traces to Det-1, Det-2, Det-3, Det-4, Det-5, Det-6 except `out_before_in`, Det-7, Insp-2):** the fixture suite passes with exact identity sets, including the mixed-spelling, multiple-types, subject-slot, anonymous-assert and dc3 rows.

---

## Phase 4: The pin list

### Goal

Parse the pin list strictly, find it only at the project root, resolve its paths against a pin root, and teach `decide` to downgrade pinned identities and to judge unmatched pins as stale or out of scope.

### Assumption Under Test

A strict, closed TOML schema with root-only discovery gives the same verdict for a model regardless of which path inside the project is validated, and never picks up a stray file outside the project.

### Test Stencil (Write This First)

```python
# tests/test_validation/test_positional_pins.py (NEW)
def test_unknown_key_in_a_pin_is_invalid(tmp_path):
    path = write_pins(tmp_path, pin_extra={"note": "x"})
    result = load(path, pin_root=tmp_path)
    assert isinstance(result, PinListInvalid) and result.reason_code == "unknown_key"

def test_discovery_ignores_a_pin_file_below_the_root(tmp_path):
    (tmp_path / "work").mkdir(); (tmp_path / "work" / "BACKLOG.md").write_text("")
    (tmp_path / "models" / "x").mkdir(parents=True); (tmp_path / "models" / "x" / "positional-pins.toml").write_text(VALID)
    assert discover(tmp_path / "models" / "x") == PinListAbsent(project_root=tmp_path, looked_at=tmp_path / "positional-pins.toml")

def test_unmatched_pin_in_an_existing_unvalidated_file_is_out_of_scope():
    result = decide(facts_of(), pins=pinlist(pin(file="models/b.sysml")), validated_files={"models/a.sysml"}, pin_root_files={"models/b.sysml"})
    assert result.out_of_scope and not result.stale
```

### Changes Required

**See `design.md` for:** D10 (format), D11 (discovery), D12 (pin root), D13 (scope), D14 (error codes), I2, I3; the pin-list file → `design.md#the-pin-list-file`; `Pin`, `PinList`, `PinListAbsent`, `PinListInvalid`, `StalePin` → `design.md#data-model`.

#### 1. Pin module
**File:** `src/agentic_mbse/validation/positional_pins.py` (NEW, or extend if Phase 3 created it)
- [x] `FindingIdentity`, `Pin`, `PinList`, `PinListAbsent`, `PinListInvalid`, `PinListResult`.
- [x] `load(path, pin_root) -> PinListResult` with `tomllib`. Invalid on: unreadable file, TOML syntax error, wrong or missing `schema`, missing `recorded_against` or either field, non-date `date`, empty `revision`, unknown key at any level, wrong type, missing pin key, non-positive `line`, duplicate identity, absolute `file`, `..` in `file`. Each with its own `reason_code`.
- [x] `discover(validated_path) -> Path | PinListAbsent` using `find_project_root(start=...)`; looks only at `<root>/positional-pins.toml`.
- [x] Never writes a file (I3).

#### 2. Project root
**File:** `src/agentic_mbse/cli/__init__.py:122-136` (MODIFY)
- [x] `find_project_root(start: Path | None = None)`; default `Path.cwd()`. Existing callers unchanged. Markers unchanged (`work/BACKLOG.md`, `.agentic-mbse/install.json`, `.claude/`).
- [x] If importing from `cli/` into `validation/` creates an import cycle, move the function's body to a small shared module and keep the `cli` name as a re-export. Record the choice in Implementation Notes.

#### 3. Pins in the decision
**File:** `src/agentic_mbse/validation/positional_binding.py` (MODIFY)
- [x] `decide` marks a finding `pinned` only on exact identity match; never for identity `None` (D9), never for failures (I2).
- [x] Unmatched pins: stale `not_found_in_validated_file` if the pinned file was validated, stale `pinned_file_missing` if it does not exist under the pin root, out of scope if it exists but was not validated (D13). Keep `decide` pure: file existence is passed in by the caller as data.
- [x] Changed target for a pinned owner/input: the new identity is an unpinned finding and the old pin is stale (Pol-1).

#### 4. Tests
**Files:** `tests/test_validation/test_positional_pins.py` (NEW); additions to `tests/test_validation/test_positional_binding_rule.py`
- [x] Every invalid case above, one test each; a valid file round-trips; output order sorted regardless of entry order.
- [x] Discovery: each of the three markers found from the validated path; no root above the path gives `PinListAbsent(None, None)`; a pin file below the root is ignored; a `positional-pins.toml` in a parent of the project root is ignored.
- [x] Pin root: a pin's `file` resolves against the pin file's directory by default and against an explicit pin root when given.
- [x] Pure decide: pinned, unpinned, unpinnable, stale (both reasons), out of scope, changed target.

### Validation

**Automated:**
- [x] `uv run pytest tests/test_validation/test_positional_pins.py tests/test_validation/test_positional_binding_rule.py` → pass
- [x] `uv run pytest tests/test_cli.py` → no new failures (the `find_project_root` change)
- [x] G1, G2, G3

**Done when (traces to Pol-1, Pol-2 and Pol-3 at the pure level):** strict parsing rejects every listed defect with its own reason; discovery looks only at the project root; stale and out-of-scope are decided as D13 states.

---

## Phase 5: L2 integration and the CLI

### Goal

Wire the check into L2 and `validate`, change the pass rule in exactly one place, and run the existing fixtures through it.

### Assumption Under Test

Excluding only `(L2_POSITIONAL_BINDING, WARNING)` from L2's failure count leaves every other L2 code's pass/fail behavior unchanged, and existing fixtures gain no positional or unverifiable finding that is not justified.

### Test Stencil (Write This First)

```python
# tests/test_validation/test_positional_binding_policy.py (NEW)
def test_pinned_mismatch_is_a_warning_and_l2_passes(policy_project):
    result = validate_structure(str(policy_project / "models"), positional_pins=None, pin_root=None)  # discovered at root
    codes = [(i.code, i.severity) for i in result.issues]
    assert codes == [(L2_POSITIONAL_BINDING, WARNING)]
    assert result.success
    assert "does not show that native values are correct" in result.issues[0].message

def test_unpinned_mismatch_fails_l2(policy_project_without_pins):
    result = validate_structure(str(policy_project_without_pins / "models"))
    assert not result.success and {i.severity for i in positional(result)} == {ERROR}

def test_pins_root_without_pins_is_a_usage_error(cli):
    assert cli("validate", "--positional-pins-root", "x", "models").returncode == 2
```

### Changes Required

**See `design.md` for:** `design.md#architecture`; `design.md#issues-and-metrics` (codes, severities, messages, metrics, summary line); D14, D15 (message prints five fields), D16; I1, I2, I5.

#### 1. Issue codes
**File:** `src/agentic_mbse/sysml/types.py` (MODIFY)
- [ ] Add `L2_POSITIONAL_BINDING`, `L2_POSITIONAL_PIN_STALE`, `L2_POSITIONAL_PIN_LIST_INVALID`.

#### 2. Render and check
**File:** `src/agentic_mbse/validation/positional_binding.py` (MODIFY)
- [ ] `render(result) -> (issues, metrics)` with the messages and metric names in `design.md#issues-and-metrics`. Swap messages say "a likely authoring hazard in valid SysML", name both repairs and print owner, input, target, file and line. No message calls the construct invalid.
- [ ] `check(model, path, files, pins_file, pin_root)` wires extraction, discovery or load, decide and render. Failures render as `L2_CHECK_UNVERIFIABLE` with `reason_code` `POSITIONAL_<cause>`. An invalid pin list renders `L2_POSITIONAL_PIN_LIST_INVALID` and the check runs as if no list existed.
- [ ] `is_pinned_positional_warning(issue)`.

#### 3. L2, runner, output
**Files:** `src/agentic_mbse/validation/level2_structure.py:402-450`, `src/agentic_mbse/validation/runner.py:44-100`, `src/agentic_mbse/validation/common.py:123-151` (MODIFY)
- [ ] `validate_structure(models_path, positional_pins=None, pin_root=None)` calls `check` once after the existing four checks.
- [ ] `success` = no issue other than pinned positional warnings (I1). This is the only change to the success line.
- [ ] `run_all_checks` passes the two options to L2 with `functools.partial`; `QUALITY_CHECKS` keeps its shape.
- [ ] `print_result` header gains "(N pinned positional warnings; not a value or route-parity check)" when L2 passes with pinned warnings.

#### 4. CLI
**File:** `src/agentic_mbse/cli/__init__.py` (`cmd_validate` at `:353-365`, parser near `:762`) (MODIFY)
- [ ] `--positional-pins FILE` and `--positional-pins-root DIR`. Usage errors: root without pins; root not a directory (D12).

#### 5. Existing-fixture scan
**File:** `scripts/positional_binding/scan_existing_fixtures.py` (NEW)
- [ ] Runs the check over every fixture directory under `tests/fixtures/` (whole directories, so multi-file fixtures resolve) except `positional_binding/`. Writes `evidence/existing-fixture-scan.md` listing every positional finding and unverifiable result, with its file and line.
- [ ] Run it **before** running the full suite. For each entry, write the justification in the evidence file. Only then update any affected test expectation, citing the evidence entry (Det-8). Do not suppress a finding to keep an old expectation.

#### 6. Tests
**Files:** `tests/test_validation/test_positional_binding_policy.py` (NEW), `tests/test_validation/test_positional_binding.py` (MODIFY), `tests/test_cli.py` (MODIFY)
- [ ] Policy (Pol-1, Pol-2, Pol-4): with a pin list, an unpinned mismatch fails L2, a pinned one passes with nothing else present, a changed target gives a new ERROR plus a stale pin, an unmatched pin fails; no list gives all ERRORs; malformed, unreadable and headerless lists each give `L2_POSITIONAL_PIN_LIST_INVALID`. Inputs bound to valued attributes so `LITERAL_BINDING` does not mask results.
- [ ] Scope (Pol-3): validate the self-contained `partial_scope/` subfolder; pins outside are counted out of scope with no issue; an in-scope unmatched pin is stale. A second case validates `partial_run/designs/` alone and shows unverifiable owners.
- [ ] Unverifiable through L2 (Insp-1): inject a raising owner sweep, a raising `owned_features` read for one owner, a raising `heritage` read for one input. Each gives `L2_CHECK_UNVERIFIABLE` naming the element, L2 fails, findings on other owners still appear, and a pin for the affected input changes nothing. Also the M1 fixtures through L2.
- [ ] Metrics (Insp-3): `Positional inputs inspected` and the other metrics in `design.md#issues-and-metrics` are present; the summary line text.
- [ ] Pass rule (Pol-5): a model with a pinned positional warning plus one other L2 warning still fails L2.
- [ ] Determinism (I5): two runs on one fixture tree give identical issue lists.
- [ ] CLI: both options reach L2; both usage errors.

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_validation/` → no new failures beyond those justified in `evidence/existing-fixture-scan.md`
- [ ] `uv run pytest tests/test_validation/test_integration_regression.py tests/test_validation/test_level2_integration.py` → pass (Pol-5)
- [ ] G1, G2, G3

**Manual:**
- [ ] `uv run agentic-mbse validate --level=2 tests/fixtures/positional_binding/prototype/` (or one fixture dir) → see `L2_POSITIONAL_BINDING` ERRORs with the five fields and both repairs.
- [ ] Error case: `uv run agentic-mbse validate --level=2 --positional-pins-root /tmp models/` → usage error.
- [ ] If Phase 1 found that L1 passes `out_before_in`, run full `validate` on it now and add what L2 reports to the surfaced item.

**Done when (traces to Pol-1 to Pol-5, Insp-1, Insp-3 metric, Det-8):** the policy, scope, unverifiable, metrics and CLI tests pass; the existing-fixture scan is in evidence with every entry justified; the regression tests pass.

---

## Phase 6: Reproduction on the consumer trees

### Goal

Show the production check reproduces the prototype's results on real trees, measure what it would change for fusion-tea, and show that new mismatches block and stale pins fail. This is the item's premise check.

### Assumption Under Test

The production check finds exactly the prototype's 125 fusion-tea identities and zero findings in each dc3 tree. If not, the premise-surprise rule applies: stop and surface.

### Test Stencil (Write This First)

```python
# tests/test_validation/test_positional_binding_reference.py (NEW)
def test_reference_builder_reproduces_the_committed_pin_list(tmp_path):
    out = tmp_path / "fusion-tea-f96ad312.toml"
    build_reference(PROTOTYPE_LOG, out)
    assert out.read_bytes() == BASELINE.read_bytes()
    pins = load(BASELINE, pin_root=tmp_path)
    assert len(pins.pins) == 125 and len({p.identity for p in pins.pins}) == 125
    assert len({p.file for p in pins.pins}) == 9

# tests/test_validation/test_positional_binding_trees.py (NEW; -m slow)
@pytest.mark.slow
def test_fusion_tea_matches_the_prototype_identities():
    repo = os.environ.get("POSITIONAL_BINDING_FUSION_TEA_REPO") or pytest.skip("POSITIONAL_BINDING_FUSION_TEA_REPO not set")
    ...
```

### Changes Required

**See `design.md` for:** Appendix B (reference file, Runs 0–3, mutation, stale, dc3, slow test); D17 (Run 0); I3 (only the builder generates pins); I7 (sibling repos untouched).

#### 1. Reference builder
**Files:** `scripts/positional_binding/build_reference.py` (NEW), `tests/fixtures/positional_binding/baselines/fusion-tea-f96ad312.toml` (NEW, generated, committed)
- [ ] Parse `04-detector-tree-fusion-tea.log` only, per Appendix B "Reference file". Target names carry inner quotes (`'integrated_heat_electricity::'Network Heat Driven Closure'::divertor_available_in'`): take the text between the first `'` after "redefines " and the `' by position` suffix.
- [ ] Assert 125 entries, 125 distinct identities, 9 distinct files, and that each input's last segment equals its declared name. Write the TOML with `revision = "f96ad312c63e8c66695971b12feab971f3ba6eb3"` and `date = 2026-10-15`.
- [ ] Reference test (stencil above).

#### 2. Reproduction script
**File:** `scripts/positional_binding/run_trees.py` (NEW), following `scripts/subset_profile/run_trees.py` and importing `export_tree`, `git`, `resolve_rev`, `sibling_state` from `scripts/subset_profile/probe.py`
- [ ] Record each sibling's HEAD and status before and after; fail if either changed (I7).
- [ ] fusion-tea Runs 0, 1, 2, 3 exactly as Appendix B. Run 0 asserts `agentic_mbse.__file__` resolves inside the archived `ccd57d83` `src/` (D17). Run 3's marker step uses the Phase 1 finding.
- [ ] Assert Run 1's non-positional issues equal Run 0's issues.
- [ ] Compare Run 2's identities with the reference: itemize added, missing, changed target. Compare outcome counts with the prototype (`implicit_matching` 5,573, `implicit_mismatch` 125, `new_parameter` 1,956). Zero inspected inputs fails the run (Insp-3).
- [ ] Record fusion-tea's L2 success and issue counts by code for Run 0 (without the check), Run 1 (with the check, no pins) and Run 2 (with pins). This is the R4-3 evidence: what moving fusion-tea's agentic-mbse pin would do, and whether the pin list alone would let its L2 pass.
- [ ] Mutation and stale runs, each on a fresh copy with Run 2's override options; site selection by the stated source-text rules, written to evidence before the check runs.
- [ ] dc3 `808464d` and `60b44d5`: no pin options; 0 findings, 0 unverifiable; compare `implicit_matching` with 302 and 391.
- [ ] Write `evidence/run-trees.md` and `evidence/run-trees.json` with every revision (this checkout, fusion-tea, both dc3) and the SysIDE version.

#### 3. Slow test
**File:** `tests/test_validation/test_positional_binding_trees.py` (NEW)
- [ ] Per Appendix B "Slow test". Skip reason names the missing variable. The evidence states whether it ran or skipped; a skip is never reported as a pass (Base-3).

#### 4. Generated side of the counterexample
**Files:** `.project/active/positional-binding-check/evidence/cross-route/eval_generated.py` (NEW), `evidence/cross-route/eval_generated.log` (NEW)
- [ ] Run with the dc3 venv (codegen `b5663c07`, TEAx `8d877460`) on the retained `gen_reversed/` and `gen_byname/` copies. Record both versions and both results (expected 7 and 7). No agentic-mbse code or test imports sysml-codegen (I7). If the environment cannot be found, record that and surface it; XR-2 stays open.

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_validation/test_positional_binding_reference.py` → pass
- [ ] `POSITIONAL_BINDING_FUSION_TEA_REPO=/home/reid/src/fusion-tea POSITIONAL_BINDING_DC3_REPO=/home/reid/src/dc3 uv run pytest tests/test_validation/test_positional_binding_trees.py -m slow` → pass
- [ ] G1, G2, G3 (scripts included)

**Manual:**
- [ ] `uv run python scripts/positional_binding/run_trees.py --final-rev <HEAD>` → `evidence/run-trees.md` shows: 125 WARNINGs, 0 positional ERRORs, 0 unverifiable, 0 stale for Run 2; Run 3 equal to Run 2; dc3 zeros; mutation gives one or more new ERRORs and L2 fails; stale gives exactly one stale pin, no new ERROR of any code, and L2 fails.
- [ ] `git -C /home/reid/src/fusion-tea status --short` and the same for dc3 and sysml-codegen → unchanged from before the run.

**STOP condition.** If Run 2's identities differ from the reference in any way, or either dc3 tree has a finding or unverifiable result, stop here. Apply the premise-surprise rule. Do not start Phase 7. Differences in inspected-input counts alone are explained in the evidence, and do not stop the run unless they come with an identity difference.

**Done when (traces to Base-1, Base-2, Base-3, Base-4, XR-2, Insp-3):** the reference builder test passes; `evidence/run-trees.md` records all runs and revisions with no identity difference; fusion-tea's L2 with and without the check, and with and without pins, is recorded; the generated-side log is captured.

---

## Phase 7: The hazard register and pin-list docs

### Goal

Write the shipped register entry with a stable anchor, the pin-list docs, and the draft upstream finding, and test their citations.

### Assumption Under Test

Every path and revision the register cites exists, and the register can state the hazard without a line that sysml-codegen's conformance scan counts as an owner-qualified binding (I8).

### Test Stencil (Write This First)

```python
# tests/test_shipped_text.py (MODIFY)
def test_semantic_hazards_register_cites_the_kerml_constraint_and_existing_paths():
    text = (REPO / "docs/patterns/semantic-hazards.md").read_text()
    assert "checkFeatureParameterRedefinition" in text
    assert '<a id="positional-input-binding"></a>' in text or "## Positional input binding" in text
    for path in agentic_mbse_paths(text):
        assert (REPO / path).exists(), path

def test_register_says_a_pin_certifies_nothing_and_is_legacy_only():
    text = register_text()
    assert "does not show that native values are correct" in text
    assert "recorded_against" in text
```

### Changes Required

**See `design.md` for:** Appendix C (register contents), D15 (legacy-only rule and five fields), D18 (citation form), B6 (placeholder limit), I8 (the qualified-binding pattern matches prose).

#### 1. Register
**File:** `docs/patterns/semantic-hazards.md` (NEW)
- [ ] Positional entry with anchor `positional-input-binding`, covering every Appendix C bullet. "Actual semantics" separates KerML text from SysIDE 0.8.4 observations on named fixtures. Cross-route divergence claimed for calc usages only. Limits include B6 and the D13 note that a pin's `file` matters for scope.
- [ ] Pin-list section (the shipped docs D15 asks for): the format, root-only discovery and the two CLI options, "pins only for mismatches that existed at `recorded_against`", repairs instead of pins for new mismatches, and that pinning a new mismatch is the owner-reserved disposition (R4-1). Pin-list integrity rests on review of the file (R4-1 outcome).
- [ ] "Candidates, not yet reproduced": output override and `[*]`/`[0]`, marked "not yet reproduced". If Phase 1–6 retained a reproduction for either, write it in full instead.
- [ ] Citations per D18; Phase 6's evidence paths as `.project/active/positional-binding-check/...`; Phase 1's answer for `out_before_in` stated as observed.
- [ ] No line matches `\bin\s+[\w']+\s*=\s*[^;=\n]*::` and no line matches `in x = x`. Write qualified targets as "`b` lands on `Sub::a`" (I8).
- [ ] Add the file to `docs/patterns/README.md`'s index if that index lists every pattern doc.

#### 2. Draft upstream finding
**File:** `.project/active/positional-binding-check/evidence/upstream-codegen-finding.md` (NEW)
- [ ] Records the name-based wiring at `b5663c07`, the native positional result, the fixtures, the Phase 6 generated-side log, the relation to POSITIONAL-FORMAL-REDEFINITION and the surfaced conflict with its "follows parser redefinition identity" text (spec, "Surfaced conflict"). Proposes no binding change. Marked unfiled. Nothing is written in sysml-codegen.
- [ ] Includes D21's observation (Item 1's `formal_targets` carries the positional reading without the implied/explicit mark), for the owner and Item 2's agent.

#### 3. Tests
**File:** `tests/test_shipped_text.py` (MODIFY); check `tests/test_packaged_guidance_contract.py` for the wheel contract and extend it if it lists files individually
- [ ] The register ships in the wheel (`pyproject.toml:58` maps `docs/` into `agentic_mbse_data/docs`).
- [ ] Cites `checkFeatureParameterRedefinition`; states the legacy-only rule and the placeholder limit; the pinned-warning wording matches the message `render` emits (Pol-4).
- [ ] Every agentic-mbse path it cites exists. Sibling citations checked with `git -C <sibling> cat-file -e <rev>:<path>` when the checkout is present, else skipped with a named reason.
- [ ] The register has no line matching I8's two patterns.

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_shipped_text.py tests/test_packaged_guidance_contract.py` → pass
- [ ] G1, G2, G3

**Done when (traces to Reg-1, Reg-4, Pol-4 register half):** the register exists with its anchor and every Appendix C topic; its citation tests pass; the draft upstream finding is in evidence and linked from the register as unfiled.

---

## Phase 8: Guidance edits, codegen conformance evidence, final checks

### Goal

Teach by-name or definition-order inputs in the guidance files, qualify "Order does not matter", link the register, check every new or changed example, and prove sysml-codegen's conformance test still passes against this checkout.

### Assumption Under Test

The guidance edits in Appendix C can be made without breaking any rule codegen's `tests/conformance/test_self_binding_guidance_contract.py` enforces (I8).

### Test Stencil (Write This First)

```python
# tests/test_validation/test_positional_examples.py (NEW)
@pytest.mark.parametrize("example", marked_fences(SHIPPED_TREES), ids=lambda e: f"{e.path}:{e.line}")
def test_marked_example_has_exactly_its_stated_positional_findings(example, tmp_path):
    result = run_l2_on(example.source, tmp_path)
    assert result.parsed
    assert positional_identities(result) == example.expected
    if example.is_by_name:
        assert not codes(result) & {"L2_SELF_NAMED_BINDING"}

def test_marked_fences_exist():
    assert marked_fences(SHIPPED_TREES), "no @positional-example markers found"
```

### Changes Required

**See `design.md` for:** Appendix C (each file's edit), I8 (every codegen rule), Validation Approach "Changed examples" (the marker form), "Guidance and a cross-repo constraint" research notes.

#### 1. Guidance edits
- [ ] `docs/patterns/plant-idiom.md` (`:298`, `:74-79`, new short paragraph): qualify "Order does not matter"; say D-5 renames the definition's parameter; by-name and definition-order forms; link `semantic-hazards.md#positional-input-binding`. No `@pinned` block changes; the `@authoritative` marker stays the only one.
- [ ] `skills/sysml-conventions/SKILL.md` (`:129`, `:218-226`) and `project_templates/MODELING_GUIDE.md.template` (`:145-152`): the "rename" clarification, one line on order versus `:>>`, the register link. Keep the text `plant-idiom.md` and the phrase "Binding a modelled value into a calculation"; add no `@authoritative` marker.
- [ ] `agents/sysml-expert.md` (`:117-139`): one sentence on binding by name or in definition order, and declaring `subject` first, with the link.
- [ ] Every new or changed SysML fence carries `<!-- @positional-example expect="none" -->` or `expect="<owner>|<input>|<target>; ..."` directly above it, and binds a distinct unqualified path (`in :>> a = big;`).
- [ ] Before saving each file, check it against I8's line patterns. A self-check script is fine; do not copy codegen's test into this repo.

#### 2. Example test
**File:** `tests/test_validation/test_positional_examples.py` (NEW)
- [ ] Collect marked fences from `docs/`, `skills/`, `agents/`, `project_templates/`; load each (wrap in a package if the fence is a fragment, stated in the test); assert parse success and exactly the stated positional identities; by-name examples have no `L2_SELF_NAMED_BINDING` (Reg-3).
- [ ] Shipped-text assertions for Reg-2 in `tests/test_shipped_text.py`: each edited file links the register; `plant-idiom.md`'s "Order does not matter" line is qualified.

#### 3. Re-install and codegen conformance evidence
**File:** `.project/active/positional-binding-check/evidence/codegen-conformance.md` (NEW)
- [ ] Re-run `uv run agentic-mbse install-commands --assistant claude --link-mode symlink` (the install mode this checkout uses, per `.project/CURRENT_WORK.md`). Record the mode, because I8's `.claude/` scan skips symlinks.
- [ ] From `/home/reid/src/sysml-codegen`, run its `tests/conformance/test_self_binding_guidance_contract.py` read-only with its own environment. Record codegen's resolved `agentic_mbse.__file__` (it must be under `/home/reid/src/agentic-mbse/src`), this checkout's branch and HEAD, and the full test output. Write nothing in sysml-codegen. If it fails, fix the guidance here and re-run; never edit codegen's test.

#### 4. Final repository checks
**File:** `.project/active/positional-binding-check/evidence/repository-checks.md` (NEW)
- [ ] `uv run pytest tests/` → no new failures versus the Phase 1 baseline. List which test modules needed `SYSIDE_LICENSE_KEY`.
- [ ] `uv run pytest tests/ -m slow` with the two tree variables set → record which slow tests ran and which skipped, with reasons.
- [ ] `uv run mypy src/` → error count not above baseline, none in touched files. `uv run ruff check src/ tests/` → pass, or exactly the baseline's findings.
- [ ] `uv run ruff format --check` on every touched file.
- [ ] Update `.project/CURRENT_WORK.md`'s Item 4 row: next step `/_my_audit`; open owner items listed (see below).

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_validation/test_positional_examples.py tests/test_shipped_text.py` → pass
- [ ] codegen conformance test → pass, captured in evidence
- [ ] G1, G2, G3

**Manual:**
- [ ] Read each edited guidance passage once as an author would: does it say input order on a calc usage matters, and show both repairs?

**Done when (traces to Reg-2, Reg-3, Repo-1):** the guidance edits are in, every marked example has its stated findings, codegen's conformance test passes against this checkout with its import path recorded, and the repository checks evidence is written.

---

## Owner items this plan produces evidence for, but does not act on

- **R4-3, fusion-tea's pin move.** Phase 6 records fusion-tea's L2 without the check, with it and no pins, and with the pin list. Whether and how fusion-tea adds the pin list or migrates its 125 bindings is the owner's decision. No fusion-tea file is written.
- **R4-1.** Any "intentional positional use" disposition beyond D1's legacy pin. Not built.
- **R4-2.** Any change to generator binding. Not touched; the draft upstream finding records the discrepancy.
- **Filing the upstream finding** in sysml-codegen: the owner's call (or Item 2's). Listed at close.
- **D21 observation** for the owner and Item 2's agent: Item 1's `formal_targets` carries the native positional reading.
- **`out_before_in`**, if Phase 1 finds L1 passes it.
- **Follow-up for the orchestrator to file:** `VALIDATE-SEMA-DIAGNOSTICS` (design Next-Stage Handoff).
- **ADR candidate** at acceptance: the pin-list file contract (D10–D13).

## Environment Setup

See `CLAUDE.md`. All commands via `uv run` from the repo root. `SYSIDE_LICENSE_KEY` must be set in `.env` for every test that loads a model. sysml-codegen, dc3 and fusion-tea checkouts are read-only: read them only through `git -C <repo> archive`, `ls-tree`, `cat-file` and `status`.

## Risk Management

See `design.md#potential-risks` for the full list. Phase-specific mitigations:

- **Phase 1:** if a learning-test line contradicts a design bet (B3, B4), surface it before Phase 2 uses the bet. B4 failing would make Phase 6's comparison show spurious differences, so it must be known first.
- **Phase 2:** multi-file fixtures loaded as one file read as unresolved (D19). Always load the fixture's directory.
- **Phase 3:** if a prototype fixture disagrees with `04-detector-fixtures.log`, the header is not edited to match the code. Surface it.
- **Phase 4:** a `cli` → `validation` import cycle from `find_project_root`. Move the body to a shared module if needed.
- **Phase 5:** the existing-fixture scan runs before the full suite, so a new finding is justified before any expectation changes.
- **Phase 6:** the venv's editable install can shadow the archived base `src/` in Run 0; the script asserts `agentic_mbse.__file__`. Any identity difference stops the run.
- **Phase 8:** a prose line like "`in b = 3` binds `Sub::a`" counts as an owner-qualified site in codegen's scan. Write targets as "`b` lands on `Sub::a`".

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-10-18

**Actual Changes:**
- `evidence/baseline-ccd57d83.md`: pytest 6 failed / 3647 passed / 8 skipped / 14 deselected / 1 xfailed (all 6 environment failures: pandoc probe, missing `PIL`, a stale `/home/reid/1cfe` path); mypy `src/` 97 errors in 19 files; ruff `src/ tests/` 118 pre-existing errors (117 in `tests/`), so G2 is per touched file; SysIDE 0.8.4; key in `.env` yes, in shell no.
- `evidence/phase1-fixture-truth.md`: every Phase 1 answer.
- `tests/fixtures/positional_binding/l1/out_before_in.sysml`.
- `tests/learning/test_syside_input_redefinition.py`: section "Plan phase 1", 6 tests (B3 for `RequirementCheck::subj` and `Cases::Case::subj`, library-formal UUIDv5, `inout`, B4 quoted names, D9 anonymous assert). All confirm the design's bets.
- `tests/fixtures/positional_binding/native_values/` (5 `sub_*.sysml`, `gen_byname/`, `gen_reversed/`) and `tests/test_validation/test_positional_binding_native_values.py`: 7, -7, 7, 7, `None` for mixed, 7 and -7. XR-1 met.
- `learning-findings.md`: "Plan phase 1" section.
- G1: full suite 6 failed (the same 6) / 3703 passed. G2, G3 clean on the two touched test files.

**Issues:**
- **Surfaced owner item: L1 passes `out_before_in`.** `validate --level=1` exits 0. SysIDE's `redefinition-direction-conformance` error is in `diagnostics.validation`, a third bucket; L1 reads only `diagnostics.parser`. Design Appendix A's row for this fixture does not hold. No L1-rejection test was written and the fixture stays out of the L2 suite, as the plan says. Det-6 for `out_before_in` stays open until the owner decides; the honest fix is the `VALIDATE-SEMA-DIAGNOSTICS` follow-up, which must read `validation` as well as `sema` (the design and learning findings named only `sema`). Phase 5 adds what full `validate` reports for it.
- The mixed spelling's native evaluation also fails its evaluation report ("Invalid operator '-' for types 'integer' and 'element'"); the test asserts that too.

**Deviations:**
- The prototype's 17 fixtures use quoted package names (`package 'calc_reversed'`). SysIDE drops quotes a name does not need, so their identities read `calc_reversed::q::c` (checked on `calc_reversed`). The files are not edited.
- dc3: `RAW_LEARNINGS.md:29` and `WI-008_generator-idiom/design.md:63` exist at `60b44d5`, not `808464d`; `ac_facility.sysml` needs the `models/` prefix. Phase 2's dc3 fixtures cite `60b44d5`.

### Phase 2 Completion
**Completed:** 2026-10-18

**Changes Made:**
- Fixtures under `tests/fixtures/positional_binding/`, one per Appendix A row, each with a comment header of `// finding: owner | input | target [| SPECIAL_SLOT]` and `// unverifiable: CAUSE @ file:line` lines (or `none`), its source, and `naive-control: wrong` on the 9 prototype cases the control got wrong. `prototype/` (17 copies, original prototype header kept below), `spelling/` (2), `types/` (5), `requirements/` (9), `dc3/` (2), `unresolved/` (3). Multi-file fixtures `partial_run/`, `partial_run/designs/` and `partial_scope/` carry their header in an `expect.txt` and load as a directory.
- `src/agentic_mbse/sysml/parameter_redefinition_facts.py`: the fact, failure and aggregate types; the aggregate rejects unsorted input.
- `src/agentic_mbse/sysml/syside_adapter.py`: `Redefinition`, `SubjectMembership`, `ActorMembership`, `StakeholderMembership` in the closed map and name set; the D5 sweep row in the enumeration table. The file's one pre-existing format difference (a 3-line wrap at `element_id`) was formatted with it, per G2.
- `src/agentic_mbse/sysml/parameter_redefinition_extraction.py`: `extract_parameter_redefinitions` with the three seams; `sweep_owners`, `owned_features`, `heritage_relationships` are the defaults.
- `tests/test_sysml/test_parameter_redefinition_extraction.py`: 32 tests. All 9 failure causes are reached (owner sweep, owned features, heritage, tier, placeholder type and supertype, input `:>> zz`, partial run, stub identity, stub membership, a target-less redefinition). Also roles, S4 owning types, `inout`, `out` not an input, D2, D21 on 6 constraint fixtures, order and repeated-load determinism.
- G1: 6 failed (the baseline 6) / 3735 passed. G2 clean on all four files. G3: `mypy src/` 97 errors, none in touched files; the test file is clean.

**Issues:**
- **Determinism bug in the design's fact sort key, fixed.** `(location, input.element_id)` ordered an anonymous owner's two inputs on one line at random: SysIDE gives anonymous elements a fresh UUIDv4 per load, so the id tie-break changed between runs (the anonymous-assert test failed 1 run in 3). The key is now location, owner name, declared name, then the target list, with no element id. Facts it cannot separate say the same thing. A repeated-load test on the anonymous-assert fixture pins it. Phase 3's finding order follows the same rule.
- D21 holds: on all 6 constraint fixtures, Item 1's `formal_targets` equals each input's full target set (both origins), compared per usage as a multiset because Item 1 keys actuals by SysIDE `name`. Nothing to surface beyond D21's planned observation.

**Deviations:**
- An owner's own relationships unreadable through `read_heritage` is recorded as `REDEFINITIONS_UNREADABLE` (the cause list has no owner-specific one). A feature whose direction cannot be read fails its owner with `INPUTS_UNLISTED`, because the owner's input list is then incomplete.
- A placeholder target on any input redefinition, implied or explicit, is `UNRESOLVED_INPUT_REDEFINITION`; D19 names only explicit ones, and no implied placeholder has been observed.
- The redefined formal's `name` is SysIDE's effective `name` (the slot's name); only the input uses `declared_name` (R5).

### Phase 3 Completion
**Completed:** 2026-10-18. First proof point met.

**Changes Made:**
- `src/agentic_mbse/validation/positional_pins.py`: `FindingIdentity` only (frozen, ordered, all three parts required). Phase 4 adds the rest.
- `src/agentic_mbse/validation/positional_binding.py`: `FindingReason`, `InputOutcome`, `PositionalFinding`, `PositionalResult` and `decide(facts)`. The rule runs in the design's step order; D6, D7 (both branches), D8, D9 and D20 as stated.
- `tests/test_validation/test_positional_binding_rule.py`: 24 pure tests. Each rule step, D6 (multiple types, S4 row 3, one mismatched target of two), both D7 branches, D8, D9 (anonymous owner, unnamed target formal), D20 (all three roles; library and user targets on one input; same-named special target), failures passed through, every outcome counted, sorted output, and I6 checked on the three pure modules' imports.
- `tests/test_validation/test_positional_binding.py`: the fixture suite, parametrized over all 41 L2 fixtures (17 prototype, 2 spelling, 5 types, 9 requirements, 2 dc3, 3 unresolved, `partial_run/` whole and `designs/` alone, `partial_scope/`). Each must give exactly its header's findings (owner, input, target, reason) and unverifiable results (cause, file:line). Also the prototype's outcome totals, the naive control, Insp-2 on `inherit_def_extends`, and "unresolved owners count no new parameters".
- `evidence/phase3-prototype-comparison.md`: the 17-row comparison with `04-detector-fixtures.log`.
- G1: 6 failed (the baseline 6) / 3805 passed. G2 clean on all four files. G3: `mypy src/` 97 errors, none in touched files; both test files clean.

**Results:**
- The 17 prototype fixtures give exactly the prototype's flagged inputs, expanded per target; `multiple_types` gives four findings. 17 of 17 agree; nothing to surface.
- Outcome totals over the 17 equal the prototype's log: explicit 9, new_parameter 75, implicit_mismatch 15, anonymous 2, implicit_matching 9.
- The name-set control is wrong on exactly the 9 marked fixtures (Det-2).
- Mixed spelling, reversed deliberate rename, multiple types with rename, S4 row 3 (four findings), subject-slot (`SPECIAL_SLOT` on `RequirementCheck::subj` and `Case::subj`), anonymous assert (two findings without identity), both dc3 shapes (including the quoted `'Serial Path 8'` target), `def_adds_first_input`, `usage_extra_inputs`, and the unresolved and partial-run rows all match their headers.
- Discrimination check, run once: removing the role exclusion fails 6 requirement fixtures; removing D7 fails 3 pure tests and no fixture (no SysIDE 0.8.4 case, R1b).

**Deviations:**
- `decide` takes only the facts in this phase, and `PositionalResult` has no `stale`, `out_of_scope` or `pin_list`, and `PositionalFinding` no `pinned`. The plan's `decide(facts, pins=None, validated_files=())` would have been a parameter nothing could use yet; Phase 4 adds the parameters and fields together with the behavior.
- `PositionalFinding` carries `owner: ElementRef` beside the identity, so a finding without identity (D9) can still name its owner's kind and location when rendered. `PositionalResult.inputs_inspected` is the sum of the outcome counts (Insp-3's metric).
- Findings sort by location, owner name, input name, target name, with no element id, for the reason recorded in Phase 2.
- Header format: `// finding: owner | input | target [| SPECIAL_SLOT]`, `<none>` for an owner without qualified name; `// unverifiable: CAUSE @ file:line`; multi-file fixtures hold it in `expect.txt`.

### Phase 4 Completion
**Completed:** 2026-10-18

**Changes Made:**
- `src/agentic_mbse/validation/positional_pins.py`: `FindingIdentity`, `Pin`, `PinList`, `PinListAbsent`, `PinListInvalid`, `PinListResult`, the closed `PinListDefect` vocabulary (17 reason codes), `load(path, pin_root)` and `discover(validated_path)`. `load` rejects every listed defect with its own code, plus three the plan did not list: an empty identity part, a `file` naming no file (`""`, `.`) and a `file` with backslashes (it could never match a POSIX path). A TOML datetime is rejected as not a date (Python's `datetime` is a `date` subclass). Pins come out sorted by identity. Neither function writes (tested).
- `src/agentic_mbse/project_root.py` (NEW): `find_project_root(start=None)` and `MANIFEST`. `cli/__init__.py` imports both names from it, so `agentic_mbse.cli.find_project_root` is the same function and `cli.installation.MANIFEST` the same constant. A relative `start` is taken from the working directory (`Path.absolute`, no symlink resolution, so existing callers see the same paths).
- `src/agentic_mbse/validation/positional_binding.py`: `PinScope` (the pin list plus the validated and existing files, relative to the pin root, as data), `StaleReason`, `StalePin`; `PositionalFinding.pinned`; `PositionalResult.stale`, `out_of_scope`, `not_judged`; `decide(facts, pins)`.
- Tests: `tests/test_validation/test_positional_pins.py` (65), 12 pin tests added to `test_positional_binding_rule.py`; the Phase 3 calls now pass `None` explicitly.
- G1: 6 failed (the baseline 6) / 3882 passed. G2 clean on all 8 touched files. G3: `mypy src/` 97 errors, none in touched files; the three test files clean.

**Issues:**
- `find_project_root` moved, as the plan allowed: `cli/__init__.py` imports `agentic_mbse.validation`, so `validation` importing `cli` is a cycle. The marker constant `MANIFEST` moved with it, because `cli/installation.py` cannot be imported without running `cli/__init__.py`. `installation.py` now imports `MANIFEST` from `project_root.py`; its value is unchanged.

**Deviations:**
- **A pin whose owner or input failed inspection is "not judged", not stale.** D13 would call it stale (`not_found_in_validated_file`), which claims the input was checked and the mismatch is gone. The plan's Insp-1 line says a pin for an affected input "changes nothing". So an unmatched pin is not judged when a failure's subject has the pin's owner or `owner::input` as its qualified name, or when the owner population could not be listed. It gives no issue; Phase 5 shows it as a metric. The failure is already the blocking ERROR. A failure with no qualified name (an owner whose `:>>` did not resolve) cannot be tied to a pin, so such a pin is still judged by its file.
- `decide(facts, pins: PinScope | None)` instead of `decide(facts, pins, validated_files, pin_root_files)`: file data travels with the pin list it describes, so there is no parameter that only matters when a list exists. `None` means no usable list.
- The I6 import test no longer lists `positional_pins.py`: it is the pin loader, which design Architecture says touches the filesystem. The test now also forbids the decision module from importing the extractor, and allows `pathlib`'s pure path types only.
- `check()` will live in a separate module in Phase 5, not in `positional_binding.py`: it calls the extractor (SysIDE) and reads the filesystem, which would break I6 for the decision module.

### Phase 5 Completion

### Phase 6 Completion

### Phase 7 Completion

### Phase 8 Completion

---

**Status:** Draft
**Next Step:** `/_my_implement` starting at Phase 1. After all phases, `/_my_audit`.
