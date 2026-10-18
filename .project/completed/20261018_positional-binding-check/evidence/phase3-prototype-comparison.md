# Phase 3: the 17 prototype fixtures, prototype versus production

**Recorded:** 2026-10-18 · SysIDE 0.8.4 · production rule `src/agentic_mbse/validation/positional_binding.py` over `src/agentic_mbse/sysml/parameter_redefinition_extraction.py`

Each row compares `.project/concepts/convince-me-exec-subset/evidence/04-detector-fixtures.log` with what the production extractor and rule give on the copy in `tests/fixtures/positional_binding/prototype/`. Package prefixes are omitted (each fixture's package is its own name). The prototype printed flagged inputs; production prints one finding per (owner, input, target). "Same" means the flagged inputs agree, the verdict agrees, and the findings equal the fixture header.

Result: **17 of 17 agree. No difference to surface.**

| Fixture | Prototype (log) | Prototype flagged inputs | Production findings (owner \| input \| target) | Same flagged inputs |
|---|---|---|---|---|
| `assert_constraint_byname` | PASS | - | none | yes |
| `assert_constraint_reversed` | FLAG | q::k::lim q::k::x | q::k \| lim \| Le::x<br>q::k \| x \| Le::lim | yes |
| `calc_anonymous_inputs` | PASS | - | none | yes |
| `calc_defaulted_trailing` | PASS | - | none | yes |
| `calc_explicit_rename` | PASS | - | none | yes |
| `calc_in_order` | PASS | - | none | yes |
| `calc_omitted_first` | FLAG | q::c::b | q::c \| b \| Sub::a | yes |
| `calc_reversed` | FLAG | q::c::a q::c::b | q::c \| a \| Sub::b<br>q::c \| b \| Sub::a | yes |
| `calc_reversed_byname` | PASS | - | none | yes |
| `calc_reversed_redefines_keyword` | PASS | - | none | yes |
| `calc_untyped_new_params` | PASS | - | none | yes |
| `constraint_reversed` | FLAG | q::k::lim q::k::x | q::k \| lim \| Le::x<br>q::k \| x \| Le::lim | yes |
| `inherit_def_extends` | PASS | - | none | yes |
| `inherit_def_no_params_usage_reversed` | FLAG | q::c::a q::c::b | q::c \| a \| Sub::b<br>q::c \| b \| Sub::a | yes |
| `inherit_def_reordered` | FLAG | Sub2::a Sub2::b | Sub2 \| a \| Sub::b<br>Sub2 \| b \| Sub::a | yes |
| `inherited_usage_redefined_in_subpart` | FLAG | Q2::c::a Q2::c::b | Q2::c \| a \| Sub::b<br>Q2::c \| b \| Sub::a | yes |
| `multiple_types` | FLAG | q::c::a q::c::b | q::c \| a \| Add::q<br>q::c \| a \| Sub::b<br>q::c \| b \| Add::p<br>q::c \| b \| Sub::a | yes |

Input outcome totals over the 17 fixtures, production: explicit 9, new_parameter 75, implicit_mismatch 15, anonymous 2, implicit_matching 9; special_parameter and anonymous_target 0. These equal the prototype's log line (`{'explicit': 9, 'new_parameter': 75, 'implicit_mismatch': 15, 'anonymous': 2, 'implicit_matching': 9}`). Pinned by `tests/test_validation/test_positional_binding.py::test_the_prototype_fixtures_reproduce_the_prototype_outcome_totals`.

Naive control: the name-set detector (`04-detector.py:naive_scan`, reproduced in the test) is wrong on exactly the 9 fixtures marked `naive-control: wrong`, the same 9 as `04-detector-naive-control.log`. Pinned by `test_a_name_set_detector_fails_exactly_the_nine_marked_fixtures`.

Discrimination check (run once, not kept): with the role exclusion removed, 6 requirement fixtures fail; with D7 removed, 3 pure rule tests fail and no fixture does. That matches the learning test: SysIDE 0.8.4 gives explicit inputs no implied targets (R1b), so D7 has no fixture case.

Reproduce: `uv run pytest tests/test_validation/test_positional_binding.py tests/test_validation/test_positional_binding_rule.py -v`.
