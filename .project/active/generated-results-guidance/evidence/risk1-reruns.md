# Phase R: Risk 1 re-runs on current sysml-codegen `main`

Run 2026-10-22. sysml-codegen branch `native-generated-compare` at `6190f996` (= `origin/main`; no sysml-codegen code changed on the branch). TEAx `8d877460`. SysIDE 0.8.4. Licence from agentic-mbse `.env`. Interpreter: dc3's venv through `spike/codegen.sh`, as in the spike and Phase 1 (it has SysIDE, `pandas` and simkit's other dependencies; TEAx `teax-simkit` and the sysml-codegen and agentic-mbse sources go first on `PYTHONPATH`; no bytecode written). Packages and runs went to `/tmp/grg-impl/phaseR/<case>/`. Afterwards `git status --short` is empty in sysml-codegen and TEAx; dc3 shows only its pre-existing untracked folder.

`compare` does not exist (plan Phases 2-5 are parked), so the native value comes from SysIDE where Phase 1 showed it is trustworthy (no unit annotation, no redefinition above the scope, no part multiplicity), and otherwise is worked out by hand from the model and labelled "by hand". The dc3 `compare` run is skipped.

## Results

Exit codes: 0 builds, 1 refused. "Generated" is what the package built and returned when run once at the model's own values. "Native or intended" is SysIDE's value, or the value the model means where SysIDE cannot be trusted or has none.

| Case | Model (`probes/…`) | `check` | `generate` | Generated | Native or intended | Verdict |
|---|---|---|---|---|---|---|
| Default count, redefined on the usage | `default_count_usage` | 0 | 0 | 2 cells built (`pack__cells[0]`, `[1]`); `pack.total` 6.4 | count 3 (SysIDE `cell_count` in scope `pack`); `pack.total` 9.6 by hand (3 × 3.2; SysIDE cannot total over a multiplicity) | **confirmed** |
| Default count, redefined in a specializing def | `default_count_spec` | 0 | 0 | 2 cells built | count 3 (SysIDE `cell_count`, scope `pack` and scope `BigPack`) | **confirmed** |
| Positional binding, inputs in reverse order, unprefixed | `positional_reversed` | 0 | 0 | `plant.diff.r` 7.0 (wired by name) | −7.0 (SysIDE `Plant::result`, scope `plant`; binds by position) | **confirmed** (differs) |
| Positional binding, by-name control (`in :>> b`) | `positional_byname` | 0 | 0 | 7.0 | 7.0 (SysIDE) | control, agrees |
| String value dropped | `string_dropped` | 0 | 0 | no channel, input or file holds `fuel_unit`, `label` or `"liter"` (grep of the package); `gen.t.r` 4.0 | `gen.label` = `"liter"` (SysIDE) | **confirmed** (dropped, no warning). Flag only (RG-2) |
| Calc usage with its own result expression | `result_expression` | 0 | 0 | the run fails: `ValidationError … fx__site__m__v  Input should be a valid number [input_value=None]` | 3.0 (SysIDE on the usage's result expression, `v * 3.0` with `v = x = 1.0`); the definition's body gives 2.0 | **confirmed** (expression and binding dropped); fails at run, not silently. Flag only (RG-2 / RG1-3) |
| Two calc defs with one simple name | `calc_def_simple_name` | 0 | 0 | the run fails: `PipelineValidationError: Module type 'libb.TwiceModule' is not registered`. `modules/libb/twice.py` is written and the pipeline names `libb.TwiceModule`, but `__init__.py` registers only `liba.TwiceModule` | `site.ra` 2.0, `site.rb` 3.0 (SysIDE) | **confirmed** (was unconfirmed); fails at run, not silently |
| Unresolved conditional branch, outside a predicate: as an attribute value | `cond_branch_attribute` | 1 | 1 | `SI_EVIDENCE_INCOMPLETE` (`evidence_resolved_target_missing`) | n/a | **refused** |
| … as a calc usage's result expression | `cond_branch_in_result` | 0 | 0 | the run fails on `fx__site__m__v` = None, as `result_expression` | 1.0 (SysIDE on the result expression) | the result-expression case above, not a separate one |
| Indexed reference (`qs#(1).v`), outside a predicate: as an attribute value | `indexed_ref_attribute` | 1 | 1 | `SI_INDEXED_SOURCE_UNSUPPORTED` (`evidence_indexed_reference_unsupported`) | n/a | **refused** |
| … as a calc usage's result expression | `indexed_ref_in_result` | 0 | 0 | the run fails on `fx__site__m__v` = None | 4273.5 (SysIDE on the result expression) | the result-expression case above |
| Unsupported callable, outside a predicate: as an attribute value (`product`) | `callable_attribute` | 1 | 1 | `SI_EXPRESSION_SOURCE_UNSUPPORTED` (`evidence_expression_kind_unsupported`, "only NumericalFunctions::sum is supported") | n/a | **refused** |
| … as a calc usage's result expression (`max`) | `callable_in_result` | 0 | 0 | the run fails on `fx__site__m__v` = None | 4271.5 by hand (`max(1.0, 4271.5)`; SysIDE: "Function 'max' is not a model-level evaluable function") | the result-expression case above |
| Conditional as the guide teaches it (Risk 3) | `conditional_guide` | 1 | 1 | `SI_EVIDENCE_INCOMPLETE` on `if x > y? x - y else y - x` | n/a | **refused** |
| Conditional in a calc def, as `conditionals.md` teaches it (Risk 3) | `conditional_calc_def` | 1 | 1 | `SI_EVIDENCE_INCOMPLETE` on the same expression | n/a | **refused** |
| `min` with `NumericalFunctions::*`, as `kerml-expert.md` teaches the import (Risk 3) | `min_attribute` | 1 | 1 | `SI_EXPRESSION_SOURCE_UNSUPPORTED`: "invocation of 'NumericalFunctions::min' … only NumericalFunctions::sum is supported" | n/a | **refused** |
| Assert on a part, violated at the model's values (Risk 2) | `assert_verdict` | 0 | 0 | `load_negative` `status: violated` (`actual_value` False, margin −3.0); report `headline: violation`; outputs still written: `host.doubled_load` 6.0, `host.neg_load` −3.0 | `doubled_load` 6.0, `neg_load` −3.0 (SysIDE); `0.0 − 3.0 > 0.0` is false by hand | **confirmed**: outputs are computed while a verdict is violated |

## What this means

- **Generate-but-wrong numbers, confirmed at `6190f996`:** the default count (both forms) and positional binding. These are the two cases where a package runs, returns numbers, and the numbers differ from the model's meaning. Both are already warned in the shipped guide (`MODELING_GUIDE.md.template:106` and `:216`; `L2_POSITIONAL_BINDING`).
- **Generate-but-lost, confirmed:** the String value is dropped with no warning and the package runs. RG-2: filed and flagged only, no guidance.
- **Generate, then the run fails:** the calc-usage result expression and the calc def simple-name collision. Neither returns a wrong number at the model's own values; both raise when the package runs. Not checked: whether a modeller who fills in the null `fx__site__m__v` input gets a number (it would be the definition's `2.0 * v`, not the usage's expression). So for these two the risk is a package that cannot run, not a silent wrong result.
- **The three formerly `omitted` places are not separate cases any more.** Each is refused at an attribute value (this run) and at the other sites the generator's stored cases cover (binding value, calc def feature value, constraint predicate, calc result expression: `tests/expectations/refusal_cases/cases/{conditional-expression,indexed-reference,invocation-callable}__*.json` at `6190f996`, each `refused`). The only place each still generates is as a calc usage's own result expression, where it is dropped with the whole expression: the result-expression case.
- **Risk 3 backing:** the conditional (both taught forms) and `min` are refused by `check`. The generator's stored cases also show `max`, `size` and `product` refused (`invocation-callable__unsupported_callable__attribute_value{__max,__size,}`).
- **Risk 2 backing:** a generated package records `violated`, sets the report headline to `violation`, and still writes every output. Not re-checked here: that SysIDE's native evaluation runs no assertions (the spec cites dc3 `scripts/models/evaluate_paths.py:6-7`; `evaluate_feature` returned values with no diagnostic, which is consistent but does not prove it).

## Guidance outcomes (for Phase 5, which is parked)

| Case | Outcome |
|---|---|
| Default count | already warned (`:106`); pin when Phase 5 runs |
| Positional | already warned; `semantic-hazards.md` "Verified with" gains this `6190f996` row when Phase 5 runs |
| String, result expression | flag only (RG-2); no guidance |
| Calc def simple name | confirmed. The design's outcome was "warn (distinct calc def names) only if confirmed". Not added here: guidance text is Phase 5, which is parked. The failure is loud (the package does not run), so the warning reduces rework rather than a silent wrong result |
| Three formerly `omitted` places | refused where taught; nothing to add beyond the Risk 3 qualifier |
| Conditional, `min` | backs the Risk 3 qualifier |
| Assert verdict | backs the Risk 2 statement |

## Commands

From `.project/active/generated-results-guidance/`:

```bash
for d in evidence/probes/*/; do c=$(basename $d)
  ./spike/codegen.sh -m sysml_codegen check --models $d > $d/check.txt 2>&1
  ./spike/codegen.sh -m sysml_codegen generate --models $d \
      --output /tmp/grg-impl/phaseR/$c/pkg --package-name $c > $d/generate.txt 2>&1
done
# run each package once, and ask SysIDE (output: evidence/probes/run_phase_r.txt, INFO lines removed)
cd evidence/probes && ../../spike/codegen.sh run_phase_r.py
```

## Files

- `probes/<case>/model.sysml`, with `check.txt` and `generate.txt` beside it.
- Model sources: `default_count_usage`, `positional_reversed`, `positional_byname` are copies of `spike/derisk/models/{default_count,gen_reversed,gen_byname}`; `default_count_spec` is `.project/completed/20261022_retire-subset-profile/evidence/guidance-examples/m_attr_spec`; `string_dropped`, `result_expression`, `cond_branch_*`, `indexed_ref_*` and `callable_*` are copies of sysml-codegen `tests/fixtures/refusal_cases/` cases (`string-value-omission__string_value__attribute_value__read_by_attribute`, `calc-usage-result__bare_result__other_expression_site`, and the `…__attribute_value` and `…__other_expression_site` variants of `conditional-expression__conditional_unresolved_branch`, `indexed-reference__indexed_reference` and `invocation-callable__unsupported_callable`). `calc_def_simple_name`, `conditional_guide`, `conditional_calc_def`, `min_attribute` and `assert_verdict` are new.
- `probes/run_phase_r.py` and its output `probes/run_phase_r.txt`.
