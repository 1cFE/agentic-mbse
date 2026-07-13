# Spec Review: Neutral Constraint Facts — Production Schemas and Extraction

**Spec:** `.project/active/constraint-facts/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/constraint-facts/spec-review.md`
**Date:** 2026-07-12
**Epic:** CONSTRAINT-EXEC, Item 1

---

## Reality Check

**Sound.** The spec is about the right work item, the Problem section is accurate against the
code (the type-level collapse to "plain" and dropped predicates are real — `syside_adapter.py:410`
`is_droppable_constraint`, and Appendix A confirms no membership/negation capture exists), and
the core requirements are directionally correct. All six S1 source forms are named and match the
golden's distinct `source_form` values exactly. The two banned heuristics are `[HARD]` requirements
with principled structural replacements, not advisory notes. Code-facing claims (`:269` subtype
sweep with `include_subtypes`, `:410` droppability, `data_models.py:1-5` "imported by downstream
packages") are all true.

This is a well-built, faithful spec. It clears Stage 0 comfortably, so the audit below is about
sharpening a strong draft, not rescuing a broken one. The findings cluster on one real hole:
**operand type/unit facts — the thing Item 3 consumes — are under-specified, and the way the spec
re-anchors the S1 golden risks pulling the Item-3 eligibility decision back into this item.**

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (concept content that did not reach the spec):** The concept's "Neutral
Constraint Facts" paragraph states a hard rule about the leaf vocabulary this item owns:
*"References keep source name, qualified target, and feature-chain segments; they do not
pre-classify a value as channel, parameter, or intermediate — that is codegen's job."* The spec
never carries this forward. It is exactly the kind of leaf-vocabulary invariant Item 1 is
supposed to freeze (Open Questions calls the "feature-ref and literal field shapes" this item's
own), and Item 5's strict resolver depends on the reference *not* arriving pre-classified. The
golden already obeys it (`FeatureReferenceExpression` carries `source_name` / `target` /
`target_types`, no role tag), so this is a capture omission, not a design change. Add it as a
requirement on the reference leaf shape.

**L1-2 · Question to the user (the `type_units` golden entangles facts with Item-3 decisions):**
The spec's Non-Goal is explicit: *"Eligibility / executable-profile decisions … is Item 3. This
item captures the facts."* But the Tests requirement re-anchors golden tests from S1's fixtures
including `type_units.sysml` and `golden.json`, and the serialization criterion demands byte-stable
round-trip. The S1 `golden.json` `type_units.equality_cases[]` entries each carry a `decision`
field whose values *are* the equality-gate verdicts —
`block_real_equality_requires_tolerance`, `support_enum_same_enumeration`,
`block_unit_conversion_required`, etc. (see `test_constraint_fact_shapes.py:98-137`). If the
production extractor must reproduce `golden.json`, it must reproduce those decisions — which is the
Item-3 gate this spec's Non-Goal disowns. **How does the re-anchoring split fact from decision?**
The spec needs to say plainly: Item 1 extracts operand *facts* (type category, enumeration
identity, unit/dimension state), and the `decision` labels are Item 3's — dropped from Item 1's
golden, or kept only in an Item-3-owned test. As written, "match S1's golden values" + "byte-stable
round-trip" silently imports the eligibility gate into Item 1. **This is the highest-stakes
finding.**

**L1-3 · Rewrite request (operand type/unit facts are not in the schema requirements):** The brief's
must-get-right #4 says Item 3 needs "operand type/unit facts sufficient for the equality/unit
gates," and the concept assigns the leaf fact vocabulary to this item. But the spec's Known
Requirements enumerate the `source_forms.constraints[]` fields (identity, membership, polarity,
owner/scope, actuals, defaults, inheritance, location) and never require operand **type category**
(Boolean / String / Integer / Real), **enumeration identity**, or the **unit/dimension** fact as
first-class leaf facts. The one unit sentence (lines 110-114) covers only the "dimension known,
exact unit unknown" state, not the general requirement that every operand's type and unit are
recoverable facts. The Success Criteria "match S1's golden values" list (lines 40-43) omits
type/unit entirely. Since Item 3 cannot run its gate without these, this item must state that it
freezes them. Describe what the leaf fact must carry; don't defer the whole predicate to Item 2
and leave the operand facts homeless between the two items.

**L1-4 · Direct claim (a library-coupled value leaked into the neutral contract):** The S1 golden
serializes actual direction as `"direction": "FeatureDirectionKind.In"` (golden.json lines 417,
435, 619, 911, 929). That string is `str(syside.FeatureDirectionKind.In)` — a SysIDE Python enum's
`repr`, not a neutral value. This is "the vocabulary three repos consume" and byte-stable
serialization is load-bearing, so a SysIDE-library artifact frozen into the wire format is a real
shape defect: it couples the neutral contract to a SysIDE enum's string form and violates the
concept's "structure survives; reconstructed text does not" principle in spirit. The spec should
require the production schema to neutralize library-coupled operand values (a stable enum member
name like `in`, not `FeatureDirectionKind.In`), rather than inherit the capture module's
`str(enum)`.

### Lens 2 — Problem & Approach

**L2-1 · If-then tradeoff (the predicate/leaf boundary is the load-bearing bet, and it is only in
Open Questions):** The spec's whole approach rests on one split — Item 1 owns the leaf fact
vocabulary, Item 2 owns the tree — but that split lives entirely in Open Questions, not in a
requirement. This is fine **if** the leaf facts Item 1 must freeze are enumerated concretely
enough that Item 2 and Item 3 can build against them without re-litigating (L1-1, L1-3 are exactly
the leaf facts that are missing). It is a problem **if** "leaf fact vocabulary" stays a phrase and
the operand type/unit/no-pre-classification facts fall into the gap between the two items. Given
Item 3 depends on Items 1 **and** 2, the safest resolution is to promote the concrete leaf-fact
list (type category, enumeration identity, unit/dimension, source-name/qualified-target,
un-pre-classified) into a Known Requirement here, so the boundary is a contract, not a note.

**L2-2 · Question to the user (owner/scope grade for Item 5's `owning_part_def_qn` need):** The
brief's #4 says Item 5 needs "`owning_part_def_qn`-grade identity facts." The spec carries `owner`
(kind/name/qualified_name) and `scope`. In the golden, `owner` is sometimes a `PartDefinition`
(`inline_owner_reference` → `ProbePart`), sometimes a `CalculationDefinition` (`calc_owned`),
sometimes a `PartUsage` (`direct_owned` → `direct_usage`), and inherited assertions carry
`inherited_into` listing the parts they land on. Item 4/5 key multiplicity expansion by
"owning definition + feature" and expect an `owning_part_def_qn` grade. **Is `owner.qualified_name`
plus `inherited_into` sufficient for Item 5 to derive the owning-part-definition identity in the
inherited and direct-usage cases, or does the schema need an explicit resolved owning-part-def
field?** This is a cross-item coordination point worth stating, not resolving silently — the owner
fact is present, but its grade against Item 5's need is not asserted.

### Lens 3 — Pipeline Risk

**L3-1 · Rewrite request ("match golden values" vs "byte-stable round-trip" are conflated):** Two
distinct properties wear one phrase. The production schema will not be byte-identical to S1's
`golden.json`: the version tag changes from `constraint-fact-learning-test/v1`, the
`FeatureDirectionKind.In` leak should be neutralized (L1-4), and field layout may shift. So
"match S1's golden values" must mean *semantic value equality of the facts*, while "byte-stable
round-trip" is a property of the *production* serialization (serialize → parse → serialize
identical). Design needs to know whether S1's `golden.json` is a byte-compared oracle or a
semantic reference that gets regenerated. State it: the S1 golden is the semantic oracle; a new
production golden is generated and byte-compared against itself.

**L3-2 · Question to the user (does this item productionize `type_units` extraction at all?):**
Related to L1-2/L1-3 but distinct in pipeline terms. The S1 golden has two fixtures. The
`source_forms` facts clearly become production `ConstraintUsageFact`s. But the `type_units`
`equality_cases` operand facts (types, unit, dimension) live in a *separate* test-only structure
in S1. **Does Item 1's production extractor emit operand type/unit facts into the usage/leaf
schema, or does it only extract `source_forms`?** If the latter, Item 3 has no fact source until
Item 2's leaves carry types — and it is unclear Item 2's `ExpressionIR` leaves carry unit/dimension
at all. The spec must name where operand type/unit facts are produced, or Item 3's dependency is on
a fact nobody committed to ship.

**L3-3 · Direct claim (no success criterion guards the operand-fact requirement):** Even if L1-3 is
fixed in the requirements, the Success Criteria have no line that would fail if the production
extractor dropped operand type/unit facts — the "match golden values" criterion lists only
`source_forms` fields. A `[HARD]`/`[NEED]`-grade fact with no matching success criterion is the
spec's own definition of a gap. Add a criterion that operand type category, enumeration identity,
and unit/dimension state extract and match the S1 evidence.

### Lens 4 — Hygiene

**L4-1 · Rewrite request (minor):** The Related Artifacts "Concept (binding, but see note)" entry
honestly records that the concept was unreadable during authoring and transmits its content via S1
+ brief. That is the right call under the capture-fidelity surfacing law. Now that the concept is
readable in-repo (`.project/reference/constraint-execution-concept.md`), the incorporated-review
pass should re-point that citation at the readable copy and confirm no contradiction — L1-1 is one
concept item that did not survive the indirect transmission, which is precisely the risk that note
flagged.

### Lens 5 — Reader Comprehension

No findings. The spec is well-organized and a tired engineer can skim it and know the work item,
the bets, and the deferrals. Provenance tags are honest and mostly correct (see L5-adjacent note:
the two banned-heuristic requirements are `[HARD]` and genuinely forced by S1's carry-forward
evidence, not dressed-up preferences — that grading is right).

---

## Engagement Summary

**Overall take:** This is a strong, faithful spec — the six forms are pinned, the banned heuristics
are real requirements, and the code claims hold. It is not ready to be the contract for one reason:
the operand type/unit facts that Item 3 consumes are under-specified, and the way it re-anchors the
S1 golden risks dragging the Item-3 eligibility *decision* back into this item, contradicting its
own Non-Goal. Fix the fact/decision boundary and the leaf-fact enumeration and this approves.

**Here's what I need you to weigh in on:**

1. **[L1-2, L3-2]** The `type_units` golden carries `decision` fields that are the Item-3 equality
   gate. Decide how re-anchoring splits fact from decision, and whether Item 1's extractor emits
   operand type/unit facts at all — otherwise byte-stable golden reproduction imports Item 3's job
   into Item 1.
2. **[L1-3, L2-1, L3-3]** Promote the concrete leaf-fact list (type category, enumeration identity,
   unit/dimension state, un-pre-classified references) into a Known Requirement with a matching
   Success Criterion. Right now the load-bearing boundary lives only in Open Questions and the
   operand facts are homeless between Items 1 and 2.
3. **[L1-4]** Neutralize the `FeatureDirectionKind.In` library-enum leak in the serialized fact —
   it's a SysIDE `str(enum)` frozen into a cross-repo wire contract.
4. **[L1-1]** Carry forward the concept's "references are not pre-classified as
   channel/parameter/intermediate" rule as a requirement on the reference leaf shape.
5. **[L2-2]** Confirm `owner` + `inherited_into` give Item 5 the `owning_part_def_qn`-grade identity
   it needs (owner can be a PartUsage or CalculationDefinition, not always a part-def QN).

---

## Verdict (epic-orchestrator framing)

**Approved-with-must-fixes.** The work item is sound and the spec is faithful; the must-fixes are
targeted edits, not a rework.

**Must-fix (each load-bearing):**

- **M1 — Split fact from Item-3 decision in the re-anchored golden (L1-2, L3-2).** Load-bearing
  because the spec's own Non-Goal disowns eligibility, yet byte-stable reproduction of S1's
  `golden.json` reproduces its `decision` verdicts. Unresolved, Item 1 either violates its Non-Goal
  or leaves Item 3 without a committed fact source.
- **M2 — Enumerate the leaf fact vocabulary as a requirement + success criterion (L1-3, L3-3,
  L2-1).** Load-bearing because Item 3's equality/unit gate (brief #4) consumes operand type
  category, enumeration identity, and unit/dimension state, and today those are neither required
  nor guarded by any success criterion — they fall into the Item-1/Item-2 gap.
- **M3 — Neutralize the `FeatureDirectionKind.In` library-enum leak (L1-4).** Load-bearing because
  this is the vocabulary three repos consume with byte-stable serialization; a SysIDE `str(enum)`
  frozen into the wire format couples the neutral contract to the parser library and multiplies
  downstream (stakes #1).
- **M4 — Carry forward "references are not pre-classified" (L1-1).** Load-bearing because Item 5's
  strict resolver relies on the reference arriving un-roled, and this item owns the reference leaf
  shape; the concept states it and the transmission dropped it.

**Nice-to-have:**

- **N1 — Distinguish "match golden values" (semantic) from "byte-stable round-trip" (production
  serialization) in the Success Criteria wording (L3-1).**
- **N2 — Assert the owner/scope grade against Item 5's `owning_part_def_qn` need (L2-2).**
- **N3 — Re-point the concept citation at the now-readable in-repo copy and confirm no
  contradiction (L4-1).**

---

## Resolutions

*(To be filled in as the owner resolves findings; keyed by ID. The spec agent reads this section to
incorporate the review — the reviewer does not edit `spec.md`.)*

---

**Verdict:** Revise (Approved-with-must-fixes) — the work item is sound; the must-fixes are targeted edits.
**Next Steps:** Record resolutions above, then return to the spec-agent session (or re-run
`/_my_spec`) pointed at this review to incorporate. The reviewer does not edit the spec. Design
must still resolve the Item 1 / Item 2 predicate-representation boundary in coordination with Item
2's `ExpressionIR` design.
