# Audit: Neutral Constraint Facts — Production Schemas and Extraction (Item 1)

**Verdict:** Certify
**Audited:** 2026-07-12
**Branch:** `constraint-exec-epic`
**Commit:** `16005d3` (range `ce9a8ef..16005d3`, five phase commits)

---

## Summary

Item 1 delivers what the spec, design (rev 2 + MF4 addendum), and plan require. The three
production modules are in place, the six source forms extract correctly against live SysIDE, both
banned heuristics are absent (independently grepped, not just guard-tested), the wire format carries
no library leaks, and the re-anchored golden asserts fact fields only with the real
`ISQBase::LengthUnit` dimension rather than the fabricated `ISQBase::Length` strip artifact. The
item's gate — the default suite — is green (1319 passed, 1 skipped, 33 deselected); ruff/format clean
on all touched files; the `-m ""` corpus suite was correctly excluded per the standing OWNER
instruction. Phase 5, finished by the orchestrator, is verified against actual state; the withdrawn
`-m ""` session claim did not need to hold because that selection is out of scope for this item.

I audited the actual code and ran the tests myself. Every claim below is execution-backed or
grep-backed.

## Findings

### Plan completion

All five phases verified complete.

- **Phase 1** (schemas + serializer): `expression_facts.py` (110 lines), `constraint_facts.py`
  (372 lines) exist; `serialize`/`parse` present; exports wired in `sysml/__init__.py`. Round-trip
  and pinned-version tests green.
- **Phase 2** (extractor): `constraint_extraction.py` (631 lines) present; the six-form dispatch,
  MF4 dimension path, and neutralization are implemented as designed (traced below). 14/14 extraction
  tests green.
- **Phase 3** (re-anchor): `test_constraint_fact_shapes.py` rewritten to drive the production
  extractor; `production_facts.json` is a separate artifact; `golden.json` untouched read-only oracle.
  7/7 green.
- **Phase 4** (retire capture module): `tests/constraint_fact_learning.py` is gone
  (`ls` confirms absent; the diff shows −535 lines). No orphan imports — the only two remaining
  mentions of the name are a docstring in the guard test and the extractor's module docstring, not
  imports (`grep -rn constraint_fact_learning tests/ src/`).
- **Phase 5** (final gates): banned-heuristic guard present and green (3/3); default suite green;
  exports complete. The plan's `-m ""` gate re-scope note is honest about the withdrawn session claim.

No placeholder code, TODOs, or partial implementations found in the three production modules.

### Spec conformance

Walked all ten success criteria with per-item evidence.

1. **Six source forms extract via production code** — ✓ `production_facts.json` form counter:
   `inline` 21, `requirement_constraint` 2, `definition_typed` 2, `plain_usage` 1,
   `named_usage_reference` 1, `satisfy` 1. `test_six_forms_extract_and_are_distinct` green.
2. **Facts semantically match S1 golden values** (membership, polarity, ownership, actuals + formal
   targets, omitted defaults, inheritance) — ✓ `test_membership_polarity_ownership_actuals_and_inheritance_match_s1_oracle`
   maps each S1 golden field to its production field and passes.
3. **Operand leaf facts match S1 type/unit evidence; Item-3 decision NOT asserted** — ✓ operand
   categories present: boolean, string, integer, real, enum, quantity, plus explicit `unknown`/
   `unresolved`. The "dimension known, exact unit unknown" state is verified
   (`test_quantity_feature_unknown_unit_...`: `unit=None, dimension=ISQBase::LengthUnit`). Zero
   `decision` fields in the production golden (grep count 0); the re-anchor test excludes them.
4. **Feature reference keeps source_name / qualified target / chain segments, no role tag** — ✓
   `test_no_role_tag_on_feature_reference` asserts the dataclass fields are *exactly*
   `{source_name, target, target_types, chain_segments}` — no role field exists.
5. **No SysIDE Python type name or str(enum) repr** — ✓ every `IdentityFact.kind` value in the
   golden is a SysML v2 metaclass name (`AssertConstraintUsage`, `ConstraintDefinition`,
   `PartDefinition`, …) — the spec explicitly permits these as neutral. `FeatureDirectionKind`,
   `RequirementConstraintKind`, and `object at 0x` all grep to 0 occurrences.
6. **ConstraintDefinitionFact carries predicate + formals-with-defaults + source identity; each
   usage exactly one ConstraintSource** — ✓ schema at `constraint_facts.py:98-125`. Note the
   documented Phase 2 deviation: within the single `ConstraintSource`, `constraint_definition` and
   `asserted_constraint` are unconditional raw reads (matching the S1 golden), while
   `effective_predicate_source` is form-derived. The object is still one `ConstraintSource` with one
   `form` per usage — the "exactly one" requirement holds.
7. **Neither banned heuristic in production** — ✓ independent grep over the three modules: no
   `removesuffix(`, no `startswith(`, no `ConstraintFactShapeProbe` literal, no namespace-prefix
   test. Only matches are the words "namespace-prefix" inside explanatory docstrings/comments.
8. **Versioned JSON round-trips byte-identically at the pinned pair** — ✓ `schema_version` =
   `constraint-facts/v1`, predicate nodes carry `predicate-tree/v0`. `test_round_trip_over_real_facts`
   and the hand-built `test_round_trip_is_byte_identical` both green.
9. **Golden re-anchored, fact-fields-only, decision excluded; capture module retired** — ✓ (see Phase
   3 / Phase 4 above).
10. **Suite green, ruff clean** — ✓ default suite 1319 passed / 1 skipped / 33 deselected in 18s;
    ruff check + ruff format clean on all seven touched source/test files.

Non-goals respected: no equality/unit gate verdicts, no `ExpressionIR` canonical algebra, no
sysml-codegen consumption, no CLI/manifest emitter. The `is_droppable_constraint` type-level path in
`syside_adapter.py` was left intact beside the new facts, as the design's Integration Strategy states.

### Design conformance

Implementation follows the design.

- **Dispatch order (MF2)** traced in `_classify` (`constraint_extraction.py:468-488`): membership gate
  first (`RequirementConstraintMembership` → `requirement_constraint`), then the `AssertConstraintUsage`
  isinstance gate (inside it: `asserted is not self` → `named_usage_reference`; no owned
  `result_expression` → `definition_typed`; else `inline`), then the `SatisfyRequirementUsage` gate,
  then `plain_usage` fallback. This is exactly the design's ordering. The
  requirement-constraint-misclassified-as-inline bug has a dedicated regression test
  (`test_requirement_constraint_not_misclassified_as_inline`, extraction test:50-53), green.
- **MF4 structural dimension** in `_unit_definition_qn` / `_quantity_feature_dimension` /
  `_unit_annotation_fact` (`:210-256`): dimension is the type in the referent's typing chain that
  conforms to `MeasurementReferences::MeasurementUnit`, selected by conformance not position — no
  suffix strip. Golden carries `ISQBase::LengthUnit` (25×) and `ISQBase::MassUnit` (2×); bare
  `ISQBase::Length`/`Mass` grep to 0. The MF4 surfaced finding (that `ISQBase::Length` is a strip
  fabrication) is correctly reflected: the production golden uses the real QN and the re-anchor test
  documents the change as a decision preservation.
- **Tagged owner totality (MF3/D6)** in `_owning_definition` (`:512-522`): all four kinds tested —
  `part_def`, `calc_def`, `requirement_def`, and `package` (including the package-scoped direct usage
  `direct_owned` and the package-scoped `satisfied_limit`), in `test_membership_polarity_ownership_survive`
  (extraction test:88-92) and `test_owning_definition_present_and_tagged_on_every_usage`. The walk
  raises loudly if it ever falls through — no silent fallback.
- **Two-level versioning (D4/D9)**, **all-fields-present / explicit null (D3)**, **canonical JSON
  (D2)**, **@dataclass carrier (D1)**, **module layering / one-way imports (D8)** all present as
  designed. `expression_facts` imports neither syside nor `constraint_facts`; `constraint_extraction`
  is the only syside-touching module.

Two documented deviations, both reasoned and verified against the S1 oracle, neither a scope or
goal-level conflict:
- `operand_type` is computed for every non-Boolean-connective node (not only reference/literal leaves)
  so unit-bearing arithmetic (`1 [m] + 1 [m]`) carries its quantity fact. Resolved against a genuine
  ambiguity between two design statements; verified against all 14 `type_units` cases.
- `definitions[]`/`contexts[]` use structural relevance filters (effective-predicate-source set;
  `is_implied` / standard-library-origin exclusion) rather than S1's fixture-coupled namespace filter.
  Reproduces the golden's membership exactly and is the principled replacement, not a regression.

### Code integrity

No slop or failure-honesty issues found.

- No god functions; `_classify` and `_operand_type_fact` are linear dispatches readable from their
  signatures.
- No policy buried in utilities; no backwards-compat shims.
- The only broad-ish except is `_conforms` catching `(TypeError, ValueError)` narrowly around a
  conformance probe — appropriate, not a swallow-all.
- Invariant violations fail loudly: `_owning_definition` raises `ValueError` on fall-through rather
  than returning a safe default; `_identity_required` raises rather than returning `None`;
  `allow_nan=False` is the serialize-time backstop behind the extraction-time non-finite diagnostic.

---

## Certification

Certified against spec, design, and plan. Verified by execution and independent inspection:

- Ran all four Item 1 test files (29 passed) and the full default suite (1319 passed, 1 skipped,
  33 deselected).
- Independently grepped the three production modules for both banned heuristics and for library
  leaks — clean.
- Independently inspected `production_facts.json` for forms, dimensions, decision fields, direction
  tokens, schema versions, and `IdentityFact.kind` values — all correct.
- Traced the MF2 dispatch order, MF4 dimension path, and MF3 owner totality against the design and
  their tests.
- Confirmed the capture module is deleted, S1 fixtures retained, and no orphan imports remain.
- Ran ruff check / ruff format on all seven touched files — clean.

Marked complete: all ten spec success criteria, all five plan phases.

**Not checked:**
- The `-m ""` full corpus suite and `test_corpus_integration.py` — deliberately NOT run per the
  standing OWNER instruction (disjoint PDF-extraction subsystem, slow, real API spend). The item's
  gate is the default suite, which passed. Module-disjointness (only `tests/test_sysml/` files
  reference the Item 1 modules) was accepted from the plan's recorded grep, not re-run.
- Cross-repo sysml-codegen consumption of these schemas — out of scope (producer side only); I
  cannot read that repo from here.
- The full 14-case `type_units` equality matrix by exhaustive structural equality — the re-anchor
  asserts a curated subset (all category/enumeration values plus the five unit/dimension cases by
  targeted assertion). I relied on those passing tests plus JSON inspection; I did not independently
  re-derive all 14 cases against live SysIDE beyond what the tests exercise.
- Repo-wide ruff/mypy debt (131 ruff, ~26 mypy errors) lives entirely in files this item never
  touched (the `extraction/` PDF subsystem); confirmed unrelated and out of scope, not re-litigated.
