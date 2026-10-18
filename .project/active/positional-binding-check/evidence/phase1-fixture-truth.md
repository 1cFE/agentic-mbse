# Phase 1 fixture truth

**Recorded:** 2026-10-18 · SysIDE 0.8.4 · branch `positional-binding-check` at `ff44256b` plus Phase 1 changes

Answers to each Phase 1 assumption in the plan, with the command or test that shows it.

## 1. Does `validate` reject `out_before_in` at L1? No.

Fixture: `tests/fixtures/positional_binding/l1/out_before_in.sysml` (`calc def O { out o : Real; in a : Real; in b : Real; }`, used as `calc u : O { in a = 1; in b = 2; }`).

`uv run agentic-mbse validate --level=1 tests/fixtures/positional_binding/l1/` → **exit 0**, "Level 1: Syntax Validation ... Errors: 0, Warnings: 0".

Full `uv run agentic-mbse validate tests/fixtures/positional_binding/l1/` → exit 1, but only because L2 reports two `LITERAL_BINDING`-style warnings ("Input 'a' bound to literal value in calc 'out_before_in::q::u'"). Nothing reports the direction error. Phase 5 adds what the positional check says about it.

Why: SysIDE's error is not a parser diagnostic. Read from `syside.try_load_model`:

| Bucket | Contents |
|---|---|
| `diagnostics.parser` | empty |
| `diagnostics.sema` | empty |
| `diagnostics.validation` | `redefinition-direction-conformance` (Error, "Redefining feature must have a compatible direction"); `namespace-distinguishability` (Warning) |

L1 reads only `diagnostics.parser` (`src/agentic_mbse/validation/level1_syntax.py:72-79`).

**Correction to the design's wording.** The design and learning findings call this error "semantic" and place it in `diagnostics.sema`. It is in a third bucket, `diagnostics.validation`. M1's `reference-error`s are in `sema`. So the proposed `VALIDATE-SEMA-DIAGNOSTICS` follow-up must read both `sema` and `validation` to catch this case.

Consequence: the design's Appendix A expectation for this row ("the test asserts `validate` fails at L1") does not hold. Per plan Phase 1 item 2, no L1-rejection test is written and the fixture is not turned into an L2 fixture. Surfaced as an owner item in `plan.md` Implementation Notes. Det-6 for `out_before_in` stays open.

## 2. Learning-test lines (`tests/learning/test_syside_input_redefinition.py`, section "Plan phase 1")

| Assumption | Answer | Test |
|---|---|---|
| B3 for library formals: `Requirements::RequirementCheck::subj` reads `SubjectMembership` | Yes. Its `owning_type` is `Requirements::RequirementCheck` | `test_p1_library_subject_formal_reads_subject_membership` |
| The same for `Cases::Case::subj` (target of a subject-less `case def`) | Yes | `test_p1_the_library_subject_a_subject_less_case_def_lands_on_reads_subject_membership` |
| Library formals carry a UUIDv5, so Item 1's `ElementRef` accepts them | Yes | `test_p1_library_formals_carry_reload_stable_uuid5_identities` |
| `inout` inputs get implied redefinitions the same way `in` inputs do | Yes: `inout b = 3; inout a = 10;` gives `b` → `P::S::a`, `a` → `P::S::b`, both implied | `test_p1_inout_inputs_are_redefined_by_position` |
| B4: `str(qualified_name)` spells quoted names as the prototype log does, stable across loads | Yes. Only names that need quotes are quoted: `'Quoted Pkg'::'Net Closure'::a`, `P::'Net Closure'::a`. That is the log's form (`integrated_heat_electricity::'Network Heat Driven Closure'::divertor_available_in`). Two loads give equal strings | `test_p1_quoted_qualified_names_match_the_prototype_log_spelling` |
| D9: an anonymous `assert constraint : Le { ... }` gives `ElementRef.qualified_name is None` through `subset_extraction._element_ref` | Yes, kind `AssertConstraintUsage`. Its inputs also have no qualified name, but keep their declared names | `test_p1_an_anonymous_assert_owner_has_no_qualified_name_through_element_ref` |

`uv run pytest tests/learning -q` → 49 passed (43 before, 6 new).

## 3. Native values (XR-1)

`tests/test_validation/test_positional_binding_native_values.py`, on `tests/fixtures/positional_binding/native_values/`:

| Fixture | Native value | Evaluation diagnostics |
|---|---|---|
| `sub_in_order` | 7 | none |
| `sub_reversed` | -7 | none |
| `sub_reversed_byname` | 7 | none |
| `sub_rename` | 7 | none |
| `sub_mixed` | `None` | "Invalid operator '-' for types 'integer' and 'element'" |
| `gen_byname/` | 7 | none |
| `gen_reversed/` | -7 | none |

One detail not in the learning test: for the mixed spelling, the evaluation report itself fails with that type error. The learning test only asserted the value was `None`. The new test asserts both.

## 4. The 17 prototype detector fixtures load cleanly

Each of `.project/concepts/convince-me-exec-subset/evidence/04-fixtures/detector/*.sysml` loaded with `syside.try_load_model`:

- All 17: 0 parser, 0 sema diagnostics, and `contains_errors()` false.
- One warning: `calc_omitted_first` gives `namespace-distinguishability: Member name 'b' shadows calc_omitted_first::Sub::b` (in `validation`). It is a warning, not an error, so the fixture is copied unchanged.
- `gen_byname` and `gen_reversed` load with no diagnostics.

Nothing to surface before Phase 3 copies them.

Note for Phase 3: the 17 prototype files use quoted package names (`package 'calc_reversed'`), so their identities read `'calc_reversed'::q::c` in production. Their headers will carry that spelling. New fixtures use unquoted names, as the design asks.

## 5. Consumer-tree facts (read-only)

**fusion-tea `f96ad312`** (`git ls-tree`): the export carries all three project-root markers: `work/BACKLOG.md` (blob), `.agentic-mbse/install.json` (blob) and `.claude/` (tree). So in Phase 6, `find_project_root` from `scratch/fusion-tea/models` will find `scratch/fusion-tea` as the root. Run 1 then looks for `scratch/fusion-tea/positional-pins.toml`, which the export does not contain. Run 3 does not need to create a marker.

**dc3** paths for Phase 2's fixtures (D22), checked with `git cat-file -e`:

- `60b44d5:work/learnings/RAW_LEARNINGS.md` exists; line 29 is the WI-008 positional entry (`calc c : D { in b_in = y; in a_in = x; }`). At `808464d` the file exists but has no such entry.
- `60b44d5:work/active/WI-008_generator-idiom/design.md` exists; line 63 is the "Binding identity" bullet. It does not exist at `808464d`.
- `60b44d5:models/designs/ac_coupled/ac_facility.sysml` exists; lines 226-227 are `in eta_01_in = ...; in eta_02_in = ...;` inside `calc rack_1_server_1_efficiency : 'Serial Path 8'`. `'Serial Path 8'` is at `models/library/analyses/energy/path_efficiency.sysml:109`. The path needs the `models/` prefix the design left out.

**`scripts/subset_profile/probe.py`** still defines `git` (`:83`), `resolve_rev` (`:89`), `sibling_state` (`:93`) and `export_tree` (`:102`).
