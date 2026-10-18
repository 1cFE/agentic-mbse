# Learning Test: how SysIDE 0.8.4 surfaces calc and constraint input redefinitions

**Date:** 2026-10-18 · **Branch:** positional-binding-check · **Base commit:** 42ee0dc1 · **SysIDE:** 0.8.4 · **Serves:** design R1–R6 (`design.md`, De-risk flags); design review M1, M4, S4 (`design-review.md`)

## Summary of Findings

R1(a) confirms the spec. In `in b = 3; in :>> a = 10;`, SysIDE gives `b` an implied redefinition of `Sub::a`, and `:>> a` carries only its explicit redefinition of `Sub::a`. The mixed-spelling criterion can be checked from resolved evidence, so bet B2 holds and there is no premise surprise.

Per flag:

- **R1: confirms.** Inputs that have an explicit redefinition never also get an implied one, even with several types. So the `multiple_types_with_rename` fixture expects only (q::c, b, Add::q). One new fact: the mixed spelling has no native value at all, not -7 or 7.
- **R2: confirms B3.** Subject, actor and stakeholder are each told apart by the type of their owning membership. All three count toward positions. A usage that skips one makes SysIDE report an error.
- **R3: confirms.** An input gets one implied redefinition per type, and each target's `owning_type` is the definition that declares it.
- **R4: contradicts one assumption.** Positions do count the `out` parameter, as the KerML text says. But SysIDE then rejects the model with an error. So the `out_before_in` fixture fails at level 1 (syntax) and never reaches L2.
- **R5: confirms.**
- **R6: one part contradicted, no harm to the design.** The four sweeps do reach requirement, case and `assert constraint` owners. But standard-library owners never come back from them, so the library exclusion in D4 never has anything to remove.

The design review (`design-review.md`) added three questions. Two of them need an owner decision before planning:

- **M1 (unresolved type): confirms the review's concern, and contradicts how the design planned to catch it.** When a calc or constraint usage's type does not resolve, its inputs get no implied redefinition. They look exactly like new parameters, so a swap passes silently. The design's `TARGET_UNRESOLVED` would not fire, because the type is not missing. SysIDE points it at a shared placeholder element that reads normally. The placeholder can be recognized from the API: it is the only kind of type target with no owning relationship.
- **M4 (requirement or case with no subject): premise surprise for the owner.** The first ordinary `in` of a subject-less requirement or case definition does implicitly redefine the library `subj`, as the review feared. But SysIDE itself reports that model as an error ("Subject must be the first input parameter"). So it is not a correct model that the check would wrongly flag. It is an incorrect model that no validation level reports today, and the positional check would report it under the wrong name. Which way to go is the owner's call; see the M4 section.
- **S4 (formal ownership): confirms the review.** A target formal can be owned by a usage, not only a definition. When a redefining usage also restates its type, each implied input gets two targets, one owned by the parent usage and one by the definition. With the rule as designed this produces no false flag on a deliberate rename, because explicit inputs still carry no implied targets.

What this means for the plan:

- The rule and fact shape stand as designed.
- Fixture expectations change in two places: `multiple_types_with_rename` (one finding, not two) and `out_before_in` (a level 1 rejection, not an L2 result).
- Requirement and case fixtures must restate the subject, and any actor or stakeholder, before the ordinary inputs. Otherwise SysIDE rejects them.
- M1 and M4 change what the check must treat as unverifiable or excluded. They need decisions before the plan (see their sections).

## Question / Goal

The design's check reads, for each authored input of a calc or constraint owner, every redefinition SysIDE resolved for it, marked implied or explicit. Six flags (R1–R6) named the parts of that surface nobody had observed. This test answers each one with a kept test, and records what SysIDE does even where the rule would accept either answer.

## Per-flag findings

All tests are in `tests/learning/test_syside_input_redefinition.py`. The models are built inline against `calc def Sub { in a; in b; return r = a - b; }`, `calc def Add { in p; in q; }` and `constraint def Le { in x; in lim; }`, inside package `P`. Redefinitions are read from `feature.heritage.relationships`, filtered to `syside.Redefinition`, as D3 specifies.

### R1: implied redefinitions next to, and on, explicit inputs

**Observed.** Shapes are listed as declared name, then each redefinition as (target, implied or explicit). The native value is SysIDE's `Compiler.evaluate_feature` on `c.r`; the intended answer is 10 - 3 = 7.

| Spelling | Inputs and their redefinitions | Native value |
|---|---|---|
| `in b = 3; in :>> a = 10;` (mixed) | `b`: Sub::a implied · (no name): Sub::a explicit | none (`None`) |
| `in b = 3; in a = 10;` (reversed, all implied) | `b`: Sub::a implied · `a`: Sub::b implied | -7 |
| `in :>> b = 3; in :>> a = 10;` (reversed, all explicit) | (no name): Sub::b explicit · (no name): Sub::a explicit | 7 |
| `in y redefines b = 3; in x redefines a = 10;` | `y`: Sub::b explicit · `x`: Sub::a explicit | 7 |
| `in local redefines a = 10; in b = 3;` | `local`: Sub::a explicit · `b`: Sub::b implied | 7 |

- (a) `b` carries an implied redefinition of `Sub::a`. Bet B2 holds. The spec's mixed-spelling criterion ("flagged at `b`; the `:>> a` input is not flagged") can be met from resolved evidence.
- (b) An input with an explicit redefinition carries no implied one. That holds for the `:>>` form, for the `redefines` keyword form, and under several types (R3 below).
- An explicit input still takes up its position. In the deliberate-rename row, `b` lands on position 2 (`Sub::b`), not position 1.
- In the mixed spelling, both inputs land on `Sub::a` and nothing binds `Sub::b`. SysIDE evaluates `a - b` to no value instead of a wrong number. The epic's scope 3 values (-7 reversed implicit, 7 reversed explicit, 7 rename) all reproduce.
- `owned_redefinitions` returns the same list as `heritage`, implied entries included. D3's choice of `heritage` is safe either way.

**Pinned by.** `test_r1a_mixed_spelling_gives_b_an_implied_redefinition_of_sub_a`, `test_r1a_mixed_spelling_leaves_sub_b_unbound_and_native_evaluation_yields_nothing`, `test_r1_reversed_fully_implicit_swaps_both_targets_and_evaluates_to_minus_7`, `test_r1_reversed_fully_explicit_carries_only_explicit_targets_and_evaluates_to_7`, `test_r1b_explicit_redefines_keyword_inputs_carry_no_implied_redefinition`, `test_r1_deliberate_rename_first_leaves_the_next_input_on_its_own_position`, `test_r1_owned_redefinitions_also_lists_implied_redefinitions`.

**Verdict.** Confirms B2 and the spec's two spelling criteria. For R1(b), the answer settles the design's conditional row: `multiple_types_with_rename` gets no (q::c, x, Add::p) finding.

### R2: subject, actor and stakeholder parameters

**Observed.**

- In a requirement def, all of `subject`, `actor`, `stakeholder` and an ordinary `in` appear in `owned_features` with direction `In`.
- Their `owning_membership` types are `SubjectMembership`, `ActorMembership`, `StakeholderMembership` and plain `FeatureMembership`. A use case def's subject and actor give the same result.
- An ordinary input's membership is plain `FeatureMembership`, not `ParameterMembership`. The role test should check for the three special types, not for a general parameter membership.
- A requirement def's subject has an implied redefinition of `Requirements::RequirementCheck::subj`. A use case def's subject has one of `UseCases::UseCase::subj`.
- A usage subject with a new name (`subject veh` against `R`'s `subject v`) has implied redefinitions of `R::v` and of the library `subj`. The name rule would flag it if roles were not excluded. That confirms the design needs the role exclusion.
- **The subject counts toward positions.** `requirement r : R { subject v : V; in hi = 3; in lo = 1; }`, against `R { subject v; in lo; in hi; }`, gives `hi` → `R::lo` and `lo` → `R::hi`. That is the design's expected (r, hi, R::lo), (r, lo, R::hi).
- If the usage leaves the subject out, the first `in` lands on the subject: `hi` → `R::v` and `RequirementCheck::subj`. SysIDE then reports the error `requirement-usage-subject-parameter-position`.
- Actors and stakeholders also count toward positions. If the usage leaves one out, the next ordinary input lands on it: `hi` → `R::d`. Even untyped, an actor or stakeholder is a part, so a literal value there is always a SysIDE `type-error`.
- A `require constraint k : Le { in lim = 5; in x = 3; }` inside a requirement def is an ordinary `ConstraintUsage` owned through a `RequirementConstraintMembership`. Its inputs swap the same way: `lim` → `Le::x` and `x` → `Le::lim`.

**Pinned by.** `test_r2_special_parameters_are_inputs_told_apart_by_owning_membership_type`, `test_r2_an_ordinary_input_is_none_of_the_three_special_memberships`, `test_r2_definition_subjects_implicitly_redefine_the_library_subj`, `test_r2_a_renamed_usage_subject_implicitly_redefines_the_definition_subject`, `test_r2_subject_counts_toward_positions_of_the_other_inputs`, `test_r2_omitting_the_subject_puts_the_first_input_on_the_subject_and_is_an_error`, `test_r2_an_actor_or_stakeholder_also_counts_toward_positions[actor|stakeholder]`, `test_r2_a_constraint_nested_in_a_requirement_is_an_ordinary_constraint_owner`.

**Verdict.** Confirms B3 and the requirement fixtures' expected identities. One consequence for the plan: a requirement or case usage fixture must restate the subject, and any actor or stakeholder, before its ordinary inputs. Otherwise SysIDE reports a level 1 error first. The spec's "not flagged" special-parameter fixtures should be written that way.

### R3: multiple types and the owning definition

**Observed.**

- With `calc c : Sub, Add { in b = 3; in a = 10; }`, input `b` gets `Sub::a` and `Add::p`, and input `a` gets `Sub::b` and `Add::q`. All are implied, in type order.
- Each target's `owning_type` is its declaring definition (`P::Sub` or `P::Add`).
- With `calc c : Sub, Add { in x redefines a = 10; in b = 3; }`, input `x` carries only Sub::a (explicit), with no implied Add::p. Input `b` carries Sub::b and Add::q, both implied.
- For `calc def Sub3 :> Sub;` used as `calc c : Sub3 { in b = 3; in a = 10; }`, `b` → `Sub::a`, and the target's `owning_type` is `P::Sub`.
- Definition-to-definition inheritance is positional too. `calc def Sub2 :> Sub { in b; in a; }` gives `b` → Sub::a and `a` → Sub::b. `calc def D :> Sub { in c; }` gives `c` → Sub::a.

**Pinned by.** `test_r3_each_input_gets_one_implied_redefinition_per_type`, `test_r3_an_explicit_input_with_several_types_gets_no_implied_redefinition`, `test_r3_a_parameterless_subdefinition_resolves_to_the_supertype_formals`, `test_r3_definition_to_definition_inheritance_is_positional_too`.

**Verdict.** Confirms the `multiple_types` expectations, (q::c, b, Sub::a), (q::c, b, Add::p), (q::c, a, Sub::b), (q::c, a, Add::q). It also confirms the parameterless-subdefinition fixture (Sub::a, owned by Sub), `inherit_def_reordered` and `def_adds_first_input` (D, c, Sub::a).

Explicit inputs never carry implied targets in 0.8.4. So D7's second branch, which matches targets with the same owning definition, never fires on observed data. The branch stays correct; it just has no SysIDE case to act on today.

Observation, not a design change: in `multiple_types_with_rename`, nothing binds `Add::p`. That is an unbound formal, not a positional mismatch, and the check does not report it.

### R4: an `out` parameter before the inputs

**Observed.**

- With `calc def O { out o; in a; in b; }` used as `calc u : O { in a = 1; in b = 2; }`, `a` → `O::o` and `b` → `O::a`. Positions count the `out` parameter, as KerML 8.4.4.7.1 says.
- SysIDE rejects this model with the error `redefinition-direction-conformance`, because an `in` cannot redefine an `out`.
- A trailing `return` parameter does not shift positions: `calc def O2 { in a; in b; return r; }` binds `a` → `O2::a` and `b` → `O2::b`.

**Pinned by.** `test_r4_positions_count_an_out_parameter_and_syside_rejects_the_model`, `test_r4_a_trailing_return_parameter_does_not_shift_input_positions`.

**Verdict.** Confirms the KerML reading, and with it the design's "(u, a, O::o), (u, b, O::a)" row.

It contradicts one thing the design assumed: that the `out_before_in` fixture is a model that loads. SysIDE rejects it, so `validate` fails at L1 and L2 never runs on it. The plan has to choose between two options:

- Keep it as a fixture that records the L1 rejection.
- Load it in a test that tolerates load errors, to assert the facts.

Either way, it cannot be an L2 pass-or-flag fixture under `validate`.

### R5: anonymous and inherited inputs

**Observed.**

- `declared_name` is `None` for `in : Real = 10` and for `in :>> b`.
- `name` is not `None` for them. It falls back to the redefined formal's name, even when the redefinition is implied: the anonymous input reads `name == "a"` because it implicitly redefines `Sub::a`. The rule must use `declared_name`, as the design does. Using `name` would make anonymous inputs look like they match.
- An inherited input that is not redeclared (`calc c : Sub { in b = 3; }`, where `a` is not restated) is not in `owned_features`. It appears only in `inherited_features`.

**Pinned by.** `test_r5_anonymous_and_by_name_inputs_have_no_declared_name`, `test_r5_an_inherited_input_that_is_not_redeclared_is_not_an_owned_feature`.

**Verdict.** Confirms both claims, with the warning above about `name`.

### R6: owner enumeration and document tiers

**Observed.**

- The four `SysideAdapter.elements_of_type(..., include_subtypes=True)` sweeps (`CalculationUsage`, `ConstraintUsage`, `CalculationDefinition`, `ConstraintDefinition`), de-duplicated by `element_id`, return these owners: `RequirementDefinition`, `RequirementUsage`, `UseCaseDefinition`, `UseCaseUsage`, `AnalysisCaseDefinition`, `VerificationCaseDefinition`, `AssertConstraintUsage`, a nested `require constraint` (`ConstraintUsage`), plain calc and constraint usages and definitions.
- **Standard-library owners do not appear.** `model.elements` is an alias for `model.nodes`. Its docstring says that by default it covers only the documents created for this model, even though the model holds 94 standard-library documents (`stdlib_docs`).
- Every owner returned had a readable tier, and it was `Project`.

**Pinned by.** `test_r6_the_four_subtype_sweeps_reach_requirement_case_and_assert_owners`, `test_r6_sweeps_never_return_standard_library_owners_and_every_tier_reads`.

**Also run once, not kept as a test:** the same sweep on dc3's `models/` tree, read only. It returned 159 distinct owners (40 calc usages, 99 assert constraint usages, 14 calc defs, 6 constraint defs), all `Project` tier, with no tier read failures. That is evidence for B5 on one real tree.

**Verdict.** Confirms owner coverage and B5 on these inputs. It contradicts the design's expectation that "standard-library owners appear and carry the `StandardLibrary` tier". They do not appear. D4's library exclusion is harmless, but nothing reaches it through this sweep. The plan should not write a test expecting library owners from these sweeps.

## Design review questions

These answer the SysIDE questions raised in `design-review.md`. The tests are in the same file, under section headers M1, M4 and S4.

### M1: an owner whose type does not resolve

**Observed.** Two shapes, with the same result for a calc usage and a constraint usage. The first is a typo in the type name: `calc c : Sbu { in b = 3; in a = 10; }` and `constraint k : Lee { ... }`. The second is a partial run: `validate` given only `designs/`, while `calc def Sub` and `constraint def Le` live in a sibling `defs/` folder.

- **The inputs get no implied redefinition at all.** Their `heritage` holds only an implied `FeatureTyping` and an implied `Subsetting`. That is exactly what an input of an untyped calc has, and an untyped calc has no formals. By the design's rule, every input reads as a new parameter, so a swap passes clean.
- **The typing is not missing.** The owner keeps its explicit `FeatureTyping`, but the type is a stand-in element (a placeholder).
  - The placeholder is a `syside.Classifier` named `<placeholder Classifier>`, with qualified name `'<placeholder Classifier>'`.
  - It has no owning relationship and no owning namespace. Every real type has an owning relationship.
  - It lives in a synthetic document `memory://placeholders.sysml`.
  - One placeholder element is shared: the calc and the constraint point at the same `element_id`.
- **The same happens for other unresolved references:**
  - An unresolved supertype (`calc def D :> Missing`) gives an explicit `Subclassification` to the placeholder Classifier.
  - An unresolved explicit redefinition on an input (`in :>> zz`) gives a `Redefinition` whose target is a `syside.Feature` named `<placeholder Feature>`, also with no owning relationship. Reading it raises nothing.
  - A usage whose own `:>>` target does not resolve (`calc :>> cc` in a part def whose supertype is missing) has no name and no qualified name. Its inputs get no redefinitions.
- **The diagnostics are semantic errors with a location, not a link to the owner.**
  - The loader returns `reference-error` diagnostics at Error severity, such as "No Type named 'Sbu' found.". In the partial run there is also "No Namespace named 'Defs' found." on the import line.
  - They are in `diagnostics.sema`. `diagnostics.parser` is empty, and L1 reads only the parser diagnostics.
  - Each diagnostic carries a file, line, column and message. Nothing in it names the owner element, so tying it to an owner means matching locations.
- **A tier check gives no signal.** `SysideAdapter.document_tier` on the placeholder reads `Project`.
- **Placeholders do not come back from sweeps.** A `model.elements(Classifier, include_subtypes=True)` sweep does not return the placeholder.
- When the `defs/` folder is loaded too, the same usage resolves normally: `b` implicitly redefines `Defs::Sub::a`.

**Can "unresolved type of this owner" be told apart from the API?** Yes, from the owner itself, without the diagnostics. Look at the target of each explicit `FeatureTyping`, `Subclassification` or `Redefinition` on the owner, and on each input's own explicit redefinitions. A target with `owning_relationship is None` is a placeholder. I checked this on these shapes only. Matching the name `<placeholder ...>` or the document URL would also work on these shapes, but that is a name test, and the adapter's rules exclude URL and name tests.

**Pinned by.** `test_m1_an_unresolved_type_gives_the_inputs_no_implied_redefinition`, `test_m1_inputs_of_an_unresolved_owner_look_exactly_like_new_parameters`, `test_m1_the_loader_reports_a_semantic_reference_error_with_a_location_only`, `test_m1_the_owner_keeps_an_explicit_typing_to_a_shared_placeholder_classifier`, `test_m1_the_placeholder_reads_as_a_project_tier_element`, `test_m1_placeholders_are_not_returned_by_model_sweeps`, `test_m1_unresolved_supertypes_and_redefinitions_also_target_placeholders`, `test_m1_a_partial_run_without_the_definitions_behaves_like_a_typo`.

**Verdict.** It confirms the review's H1: an owner whose type did not resolve passes clean under the design as written. It contradicts the design's assumption that `TARGET_UNRESOLVED` ("a redefinition whose target cannot be read") covers unresolved evidence. The target reads fine; it is a placeholder.

This affects the design in three places:

- The extractor needs an explicit placeholder test on owner typings, supertypes and input redefinitions to report these owners as unverifiable.
- An input with an unresolved `:>> zz` would otherwise be recorded as explicitly redefining a target named `<placeholder Feature>`, and never flagged.
- An owner with an unresolved `:>>` has no qualified name, so any finding on it is unpinnable (D9).

The spec's partial-scope test must either use a self-contained subfolder or expect unverifiable results.

### M4: requirement and case definitions with no subject

**Observed.**

- In a definition with two ordinary inputs and no `subject`, `actor` or `stakeholder` (`requirement def X { in lo : Real; in hi : Real; }`), the first input `lo` has an implied redefinition of the library subject.
  - The same holds for `case def`, `use case def`, `analysis def` and `verification def`.
  - The targets are `Requirements::RequirementCheck::subj`, `Cases::Case::subj`, `UseCases::UseCase::subj`, `AnalysisCases::AnalysisCase::subj` and `VerificationCases::VerificationCase::subj`.
- The second input `hi` gets no redefinition at all. The other inputs do not shift onto anything; the library types have only the one positional parameter.
- `lo` stays an ordinary input. Its owning membership is plain `FeatureMembership`, so the role exclusion does not cover it.
- **SysIDE reports every one of these definitions as an error.** The code is `requirement-definition-subject-parameter-position` or `case-definition-subject-parameter-position`, and the message is "Subject must be the first input parameter". It is a semantic diagnostic, so L1 does not see it today (see M1).
- **A requirement usage typed by such a def** gets both the definition's formals and the library subject:
  - In declaration order, `requirement r : R { in lo = 1; in hi = 3; }` gives `lo` → `R::lo` and `RequirementCheck::subj`, and `hi` → `R::hi`.
  - Swapped, `hi` → `R::lo` and `subj`, and `lo` → `R::hi`.
  - SysIDE adds a `requirement-usage-subject-parameter-position` error for the usage.

**Pinned by.** `test_m4_the_first_ordinary_input_lands_on_the_library_subject_and_is_an_error` (five kinds), `test_m4_a_usage_of_a_subject_less_requirement_def_also_lands_on_the_library_subject`.

**Verdict: premise surprise, for the owner.** The review's mechanism is confirmed: `lo` lands on the library `subj`, and the rule as designed flags (X, lo, `…::subj`). That includes the in-order usage, where `lo` gets a second target `RequirementCheck::subj` alongside its matching `R::lo`.

The review's premise does not hold. It assumed this is a correct requirement definition that the check would wrongly flag. SysIDE says it is not correct: in SysML v2 a requirement or case's first input is its subject. So the check would not be putting an ERROR on a valid model. It would be reporting a real model error, which no level reports today, under the positional-binding code and with a by-name repair hint that does not fit.

The owner has three choices (I have not chosen one):

- **(a)** Let the finding stand as designed. Correct in outcome, misleading in message.
- **(b)** The review's candidate rule: an implied target that is itself a subject, actor or stakeholder parameter is not a positional finding. This leaves the SysIDE error unreported unless something else reads semantic diagnostics.
- **(c)** Report the subject-position error as what it is, for example by reading SysIDE's semantic diagnostics, which M1 also points toward. Then exempt it from the positional finding.

I'd lean to (c) if M1 is resolved by reading semantic diagnostics, and to (a) otherwise, because an ERROR with an imperfect message beats silence on a model SysIDE rejects.

### S4: what owns the formals of a usage redefined in a subpart

**Observed.** Three shapes, all accepted by SysIDE without errors.

| Parent `Q1` | Redefining usage | Each input's targets (owner, its metatype) |
|---|---|---|
| `calc c : Sub;` | `calc :>> c { in b = 3; in a = 10; }` | `b` → `Sub::a` (Sub, CalculationDefinition); `a` → `Sub::b` |
| `calc c : Sub { in a; in b; }` | `calc :>> c { in b = 3; in a = 10; }` | `b` → `Q1::c::a` (Q1::c, CalculationUsage); `a` → `Q1::c::b` |
| `calc c : Sub { in a; in b; }` | `calc :>> c : Sub { in b = 3; in a = 10; }` | `b` → `Q1::c::a` (CalculationUsage) and `Sub::a` (CalculationDefinition); `a` → `Q1::c::b` and `Sub::b` |

The deliberate rename `in local redefines a = 10; in b = 3;` behaves the same way in each row:

- `local` carries one explicit target: `Sub::a` in row 1, `Q1::c::a` in rows 2 and 3.
- `local` carries no implied target.
- `b` gets the same targets as in the table, all matching its name.

**Pinned by.** `test_s4_a_parent_usage_without_inputs_leaves_the_definition_owning_the_formals`, `test_s4_a_parent_usage_that_restates_inputs_owns_the_formals_itself`, `test_s4_restating_the_type_too_gives_targets_owned_by_both_usage_and_definition`.

**Verdict.** It confirms the review's S4. A target's owner is a usage whenever the parent usage restates its inputs, so the field should be named for the owning type, not a definition.

It confirms H3's shape in row 3: an input gets implied targets owned by both a usage and a definition. D7 would treat that as the several-owners case.

It does not confirm H3's feared false flag. The deliberate rename is never flagged, because an explicit input carries no implied target for D7 to judge (R1b). A swapped input in row 3 yields two findings per input, one per owner, the same way a multiple-typed input does. The fixture for that shape should expect four identities: (Q4::c, b, Q1::c::a), (Q4::c, b, Sub::a), (Q4::c, a, Q1::c::b), (Q4::c, a, Sub::b).

## Incidental observations

- `heritage.relationships` also holds implied `FeatureTyping` and `Subsetting` entries. For example, an input with a literal value gets an implied typing by `ScalarValues::Positive`. The extractor has to filter by `syside.Redefinition`, as the prototype did.
- On a `ModelError`, SysIDE's `Diagnostics` object cannot be iterated directly. Read `.errors`, `.sema`, `.parser` (or `.all`) instead. Each message has `.code`, `.severity`, `.message`, `.filename`, `.line` and `.col`.

## Tests Written

- `tests/learning/test_syside_input_redefinition.py`: 43 tests (38 functions; the actor/stakeholder test runs twice and the M4 definition test runs once per kind, five times). Each section header names its flag. Each test loads an inline model with `syside.load_model(sysml_source=...)`. The R6 tests and the M1 partial-run test write files under `tmp_path` and load it through `SysideAdapter.load_model`, the way production loads. Rejected models are loaded through `pytest.raises(syside.ModelError)`, and the test asserts the exact error codes.
- `tests/learning/__init__.py`: package marker, matching the other test directories.
- Location: the orchestrator asked for `tests/learning/`. The design had suggested `tests/test_sysml/test_parameter_redefinition_surface.py`. I followed the orchestrator. `tests/learning/` did not exist before, so this file starts that convention.

## Reproduction

```bash
uv sync
uv run pytest tests/learning/test_syside_input_redefinition.py -v
uv run ruff check tests/learning && uv run ruff format --check tests/learning
uv run mypy --follow-imports=silent tests/learning/
```

`SYSIDE_LICENSE_KEY` must be set in `.env`. Plain `uv run mypy tests/learning/` follows imports into `src/` and reports 97 errors that were already there in `src/`. None are in the new files.

## Open Questions / Follow-ups

- How the plan handles `out_before_in`, given that SysIDE rejects it (R4).
- Owner decision on M4: (a), (b) or (c) above.
- Design decision on M1: the placeholder test (`owning_relationship is None`) and whether to read SysIDE's semantic diagnostics. The placeholder test was checked only on the shapes above.
- Not checked: quoted owner names in finding identities (B4), and implied redefinitions on `inout` parameters. The prototype counted `inout` as input. These tests use `in` only.
- Not checked: ordering among subject, actor and stakeholder themselves, which the spec puts out of scope.
