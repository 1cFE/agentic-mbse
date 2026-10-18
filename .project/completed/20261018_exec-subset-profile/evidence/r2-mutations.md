# R2 mutation tests (audit M1 mutation part, A2)

**Result: every mutation is caught.** 14 mutations, each applied alone in a scratch copy, each made at least one test fail or error. The audit's blocker conditions, mutation (a′) and the `consumer_placement` fallback, are both caught.

## How it ran

- **Scratch copy:** `git archive ce0ad1ff` (the final implementation revision) into `/tmp/af/scratch`, `git init` there so each mutation reverts with `git checkout -- . && git clean -fdq`, this repo's `.env` copied in for the SysIDE key, `uv sync --frozen`. The working tree was never mutated.
- **Tests run per mutation:** `tests/test_subset_probe_evidence.py`, `tests/test_subset_matrix.py` and `tests/test_sysml/` (the evidence gate, the matrix join and every evaluator and records test). Baseline on the unmutated copy: 1422 passed, 1 skipped.
- **Script:** `r2-mutations.py` (the edits, one function per mutation). **Full output:** `r2-mutations.log`.

## Results

| # | Mutation | Caught by |
|---|---|---|
| m1 | A refused admission cites an unrelated probe (`binding-source/expression_source/owner_instantiated` cites the `owner_package` probe) | The loader, at import: "probe 'binding-source__expression_source__owner_package' does not probe binding-source__expression_source__owner_instantiated". All 9 importing test modules error |
| m2 | A new refused admission with no evidence (`indexed-reference` at `calc_result_expression`) | The loader: "outcome refused requires evidence". 9 modules error |
| m3 | A refused admission also cites a nonexistent probe whose id has the right prefix | `test_cited_probe_certifies_its_own_pair_at_the_pinned_identity`, `test_evaluator_reproduces_each_cited_probe`, `test_stripping_the_shapes_evidence_makes_it_unconfirmed` (each for the nonexistent id), and the version digest |
| m4 | **(a′)** An admitted pair flipped to refused, keeping its own probe (`binding-source/expression_source/owner_uninstantiated`) | `test_cited_probe_certifies_its_own_pair_at_the_pinned_identity` (expected outcome mismatch), `test_evaluator_reproduces_probe`, the matrix's `test_shared_rule_row_contexts_are_the_record_contexts_with_its_outcome`, `test_narrowed_roots_report_incomplete_scope`, and the version digest |
| m4b | S1: the omitted partner flipped to refused, leaving `indexed-reference/indexed_reference` with no non-refused probe | The loader: "a refused shape needs a probe of a context it is not refused in (admitted, omitted or excluded) or a no_admitted_context statement". 9 modules error |
| m5 | A refused probe's observed code changed (`SI_INDEXED_SOURCE_UNSUPPORTED` → `SI_EXPRESSION_SOURCE_UNSUPPORTED`) | `test_stored_observation_re_judges_as_recorded`, `test_cited_probe_certifies_its_own_pair_at_the_pinned_identity`, the matrix's `test_every_cited_probe_exists_and_certifies` |
| m6a | A cited observation deleted | The same three, plus `test_every_certified_record_probe_is_cited` |
| m6b | A cited observation's `certifies` flipped to false | The same four |
| m7 | A refused probe's error line moved outside the construct (to line 99) | The same three as m5 |
| m8 | `_unreached` places an unreached owner as `OWNER_INSTANTIATED` | 11 tests: evaluator reproduction of the three `owner_uninstantiated` probes (evidence and instantiation suites), binding placement, default and narrowed roots |
| m9 | **`consumer_placement`'s fallback changed to `OWNER_INSTANTIATED`** (`subset_profile.py`, the audit's `:848`) | `test_a_consumer_attached_as_neither_calculation_nor_constraint_is_owner_other` (new, audit A2) and `test_an_unverified_check_does_not_hide_a_refusal` |
| m10 | S1 omission check: the dropped literal `4271.5` reported as mentioned in a generated file | `test_stored_observation_re_judges_as_recorded` (judge: `omitted_element_present`), `test_cited_probe_certifies_its_own_pair_at_the_pinned_identity`, the matrix's certify test for ES-005 and CALC-USAGE-BARE-RESULT-DROP |
| m11 | The loader's non-refused-partner gate removed | `test_a_refused_shape_needs_a_probe_of_a_context_it_is_not_refused_in` only. The packaged records still satisfy the gate, so only the synthetic loader test notices; that test is the gate's guard |
| m12 | S3 reverted: `INCOMPLETE` outranks `REFUSED` again | `test_an_unverified_check_does_not_hide_a_refusal` and the three failure-injection tests that now expect `REFUSED_INCOMPLETE` |

## The omission check can fail (S1)

The three `other_expression_site` probes certify `omitted` by checking that a unique literal in the dropped expression appears in no generated file. A check that can never fail proves nothing, so one throwaway probe tested it, in a second scratch clone (never committed here): the same model with the literal `4274.5` moved into `Twice`'s compiled return expression (`return r : Real = 4274.5 * v;`) and the calc usage's bare result removed. The generator ran (exit 0), the literal appeared in `modules/fx/twice.py` and `handwritten/fx/twice_impl.py`, and the judge refused to certify it: `failed_check = omitted_element_present`. Log: `omission-literal-discrimination.log`. So a literal the generator compiles does reach the output, and the omission check catches it.
