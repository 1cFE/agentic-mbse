# Spike: native-vs-generated comparison (design bets B1, B2, and the positional premise)

Run 2026-10-22 on branch `generated-results-guidance` (agentic-mbse `d5a26bdc`). SysIDE 0.8.4. sysml-codegen worktree `/home/reid/src/subset-conformance/sysml-codegen` at `53d3cb1bfd5a6cd229818edfb71b9f4e4ea1052b` (branch `subset-profile-screen`); its `src/` is identical to `origin/main` `6190f996f81d17e9e8c195120fa3a9bb2bedb6a5` (`git diff --stat origin/main HEAD -- src` is empty). TEAx simkit from `/home/reid/src/teax` at `8d877460ac4f6f264561d916e40c1708adb13397`. sysml-codegen, TEAx and dc3 have no changes after the runs (`git status --short` empty in each).

## Summary of Findings

**B1 (native value by path) partly holds.** One generic call works for plain attributes, inherited attributes, calc usage results, attributes bound to a calc result, nested part attributes, and attributes computed from an expression. It fails for anything that ranges over a part multiplicity. SysIDE's evaluator does not expand `cells : Cell[3]` into three parts. So `sum(cells.capacity)` returns one cell's value (2.5, not 7.5) and `size(cells)` returns 1, with no diagnostic. This is the shape the design's main example (the default count) depends on.

**B2 (channel trace before emission) holds, but not where the design said.** `ModuleOutput` (`resolution/models.py:179-196`) carries no source feature or path. The trace exists one layer earlier, in the instance graph: the projection's private `_Projection.output_channels` maps each output port to its channel (`elaboration/project.py:403-413`). Each port names its calc node and output declaration, the node's scope is an occurrence path with per-step indexes, and every declaration id is the SysIDE element id (`elaboration/identity.py:70-87`). So the native feature is found by id, not by parsing names. Indexed occurrences trace fine (`pack.cells[1]`), but SysIDE cannot evaluate a specific index. The native value for `cells[1].d.y` is the per-definition value, which agrees only because every occurrence has the same value.

**D6 side question: native verdicts are available with one extra step.** `evaluate_feature` on an `assert constraint` usage returns the usage object, not a Boolean. Evaluating the constraint's result expression with the usage as scope returns `True` / `False`, for both a def-typed usage and an inline body. The generated package writes a per-constraint `actual_value`, which matched.

**S3 premise is false: current sysml-codegen binds by name, not by position.** At `main` code, `gen_reversed` (`in b = small; in a = big;`) passes `check` (exit 0), generates (exit 0), wires `a ← big`, `b ← small`, and gives 7.0. Native SysIDE gives -7.0. The −7 vs 7 split from `b5663c07` is still there, so `docs/patterns/semantic-hazards.md:47-58` is not stale. `gen_byname` gives 7.0 on both routes.

**Does option (a) stand?** Yes, with three changes the design needs before planning (I did not edit the design, per the brief):

- Channels whose value ranges over a multiplicity cannot be compared natively. They must be reported "not compared", or the comparison reports a false difference on a correct package (S2: the literal `Cell[3]` model gives generated 9.6, native 3.2).
- The default-count defect is not caught by comparing output values. Both the buggy and the correct package differ from the native value. What does catch it: SysIDE evaluates the redefined count (`cell_count` and the multiplicity's upper bound in `pack`'s scope) as 3, while the generator built 2 occurrences. A count check (native multiplicity bound against built occurrences) would detect it. The design's "differ (the default-count reproducer)" test needs a different fixture; `gen_reversed` is a real one.
- The trace reads a private projection class and the instance graph, not `ComputationGraph`. sysml-codegen's plan has to expose that, or carry source ids on `ModuleOutput`.

## Question / Goal

The design (`../design.md`, Key Bets) proposes `sysml-codegen compare`: evaluate a model natively with SysIDE and through the generated package, then compare outputs. It rests on:

- B1: `Compiler().evaluate_feature(feature, scope=<owning usage>)` gives the native value for the shapes generated models use, named only by path.
- B2: the generator can trace each emitted numeric channel to one SysML feature and occurrence path before emission, without parsing channel names.
- Premise (design line 46): current generator binds inputs by position, like SysIDE, so the old −7 vs 7 finding is obsolete.

Confirmed if the probes return the expected native values, a full channel-to-feature trace, and matching numbers; refuted otherwise.

## Log

### S1: native paths (B1)

Command (agentic-mbse root):

```bash
uv run pytest .project/active/generated-results-guidance/spike/native-path/test_native_path.py -s -q -p no:cacheprovider
```

The spike ran as written; I did not fix anything in it. Output:

```
probe_native::host.load -> (3.0, [])
probe_native::host.doubled_load -> (6.0, [])
probe_native::host.doubled.r -> (6.0, [])
probe_native::host.pack_total -> (2.5, [])
probe_native::host.pack.total -> (2.5, [])
probe_native::host.pack.cell_count -> (3, [])
probe_native::host.load_positive -> (<syside.core.AssertConstraintUsage object ...>, [])
probe_native::host.load_negative -> (<syside.core.AssertConstraintUsage object ...>, [])
```

Against the README's expected values: `load`, `doubled_load`, `doubled.r` and `cell_count` match. `pack_total` and `pack.total` give 2.5, not 7.5: `sum(cells.capacity)` over `cells : Cell[cell_count]` with `cell_count = 3` sums one cell. No diagnostic is reported. The constraint paths return the usage itself.

Follow-up probe for multiplicity and constraint verdicts. Model `native-path/model_extra/model.sysml`: a literal `Cell[3]` with `sum` and `size`, a subsetting part, `assert constraint` usages typed by a def and with an inline body, and a Boolean attribute. Command:

```bash
uv run python .project/active/generated-results-guidance/spike/native-path/probe_extra.py
```

Output (trimmed):

```
probe_extra::host.packlit.total -> (2.5, [])      # Cell[3], sum(cells.capacity); intended 7.5
probe_extra::host.packlit.n -> (1, [])            # size(cells); intended 3
probe_extra::host.packredef.total -> (2.5, [])
probe_extra::host.pos_flag -> (True, [])          # Boolean attribute
--- load_positive (typed by Positive { in v; v > 0.0 }, v = load = 3.0)
  evaluate(def.result_expression, scope=usage) -> True []
  evaluate_feature(OperatorExpression, scope=usage) -> True []   # the body expression, inherited as a feature
  evaluate_feature(Feature result, scope=usage) -> Performances::BooleanEvaluation::result []
--- load_negative (v = -load)
  evaluate(def.result_expression, scope=usage) -> False []
--- inline_neg (assert constraint inline_neg { load < 0.0 })
  evaluate(usage.result_expression, scope=inline_neg) -> False []
```

So a literal multiplicity behaves the same as an attribute-driven one: the evaluator treats the part feature as one value. For constraints, one generic rule works: take the usage's own `result_expression`, else the definition's, and evaluate it with the usage as scope. The `result` feature does not work (it returns the library feature).

dc3 does not exercise multiplicity natively. Its native walker (`/home/reid/src/dc3/scripts/models/evaluate_paths.py`) uses named parts (`rack_1`, `server_2`) rather than `[n]`, so "dc3 walks deeper paths the same way" says nothing about `sum` over occurrences.

Verdict, B1: **partly**. Holds for attribute, inherited attribute, calc usage result, attribute bound to a calc result, nested part attribute, computed attribute, Boolean attribute. Fails for `sum` (and `size`) over a part multiplicity, literal or attribute-driven: wrong value, no diagnostic. Constraint verdicts: holds with the result-expression step, not with a bare `evaluate_feature` on the usage.

### S2: channel trace (B2)

**How simkit is provided.** dc3 declares `teax-simkit` as an editable path dependency on `../teax/packages/teax-simkit` (`/home/reid/src/dc3/pyproject.toml:9,27`). sysml-codegen's own tests require `TEAX_SIMKIT_PATH` pointing at the same tree (`tests/helpers/teax_discovery.py`). sysml-codegen's venv cannot run simkit (no `pandas`), so `spike/codegen.sh` runs dc3's venv interpreter with the subset-conformance `sysml-codegen/src` and `agentic-mbse/src` first on `PYTHONPATH`, plus the simkit tree, the SysIDE key from `agentic-mbse/.env`, and `PYTHONDONTWRITEBYTECODE=1`. Resolution check:

```
$ spike/codegen.sh -c "import sysml_codegen, agentic_mbse, simkit, syside; ..."
/home/reid/src/subset-conformance/sysml-codegen/src/sysml_codegen/__init__.py
/home/reid/src/subset-conformance/agentic-mbse/src/agentic_mbse/__init__.py
/home/reid/src/teax/packages/teax-simkit/simkit/__init__.py 0.8.4
```

**Models** (in `channel-trace/models/`):

- `s1_native`: S1's model unchanged. `check` exits 1: `SI_EXPRESSION_SOURCE_UNSUPPORTED ... reference='-load'` (the `in v = -load` binding). Kept as the record of that refusal.
- `s1_gen`: S1's model with `in v = -load` replaced by `attribute neg_load : Real = 0.0 - load;` and `in v = neg_load`. `check` exits 0 (6 modules).
- `default_count`: the backlog reproducer (`m_attr`: `cell_count default := 2`, usage redefines it to 3) plus `attribute total : Real = sum(cells.capacity);` in `Pack`. `check` exits 0 (3 modules).
- `default_count_literal`: the same with `Cell[3]` and no count attribute. `check` exits 0 (4 modules).

**Probe.** `channel-trace/probe_channels.py` does, for one model:

1. Load and build the exact context as `prepare` does, decode the sealed instance graph, and run `_Projection(graph).run()`. For each `(port, channel)` in `output_channels`, read the calc node, the output declaration id, and the occurrence chain (display segment, occurrence index, containment declaration id per step).
2. Load the same files with SysIDE, index every element by `element_id`, and evaluate the output declaration with scope = the calc usage (when the node is a calc usage) or the innermost occurrence's declaration.
3. Generate through `run_codegen`, load with TEAx's `ProvisionalPackageLoader`, run `execute_pipeline`, and read each channel's value through the run manifest. Output files are named by alias (`host__pack_total.json`), and the manifest maps channel to file.

Commands (from `spike/`; scratch output under `/tmp/grg-spike/`, outside both repos):

```bash
cd channel-trace
../codegen.sh probe_channels.py models/s1_gen /tmp/grg-spike/s1_gen probe_gen
../codegen.sh probe_channels.py models/default_count /tmp/grg-spike/default_count default_count
../codegen.sh probe_channels.py models/default_count_literal /tmp/grg-spike/default_count_literal default_count_literal
```

Results:

| model | channel | occurrence (pre-emission) | native feature, scope | native | generated | agree |
|---|---|---|---|---|---|---|
| s1_gen | `probe_gen__host__doubled__r` | `host` | `Scale::r`, `Host::doubled` | 6.0 | 6.0 | yes |
| s1_gen | `probe_gen__host__neg_load__neg_load` | `host` | `Host::neg_load`, `host` | -3.0 | -3.0 | yes |
| s1_gen | `probe_gen__host__pack__total__total` | `host.pack` | `Pack::total`, `Host::pack` | 2.5 | 7.5 | no (native wrong) |
| default_count | `Packs__pack__cells[0]__d__y` | `pack.cells[0]` (index 0) | `Double::y`, `Cell::d` | 6.4 | 6.4 | yes |
| default_count | `Packs__pack__cells[1]__d__y` | `pack.cells[1]` (index 1) | `Double::y`, `Cell::d` | 6.4 | 6.4 | yes |
| default_count | `Packs__pack__total__total` | `pack` | `Pack::total`, `pack` | 3.2 | 6.4 | no (both wrong; intended 9.6) |
| default_count_literal | `cells[0..2]__d__y` (3 channels) | `pack.cells[i]` | `Double::y`, `Cell::d` | 6.4 | 6.4 | yes |
| default_count_literal | `Packs__pack__total__total` | `pack` | `Pack::total`, `pack` | 3.2 | 9.6 | no (native wrong) |

Every output channel traced to a calc node, an output declaration, and an occurrence path, and every declaration id resolved to a SysIDE element. No channel name was parsed. Aliases (`host__doubled_load`, `host__pack_total`) are not separate channels; the manifest maps them onto the traced channel.

The default-count defect shows: the generator builds 2 cells for a redefined count of 3. But the value comparison does not isolate it, because native `sum` is wrong in both models.

Constraints in `s1_gen`: the package writes `probe_gen__host__load_positive__<hash>__evaluation.json` with `"actual_value": true` and `..._load_negative_...` with `"actual_value": false` (`v = -3.0`, `"status": "violated"`). These match the native verdicts from S1's follow-up for the same bindings. I did not join them through `usage_qualified_name` in code; the catalog carries it (`ConstraintCatalogEntry`, `resolution/models.py:351-381`).

Count follow-up: does SysIDE see the count the generator got wrong?

```bash
../codegen.sh probe_count.py models/default_count
```

```
evaluate_feature(Packs::pack::cell_count, scope=pack) -> 3 []
evaluate_feature(Packs::Pack::cell_count, scope=pack) -> 3 []
evaluate_feature(Packs::Pack::cells, scope=pack) -> <syside.core.PartUsage ...> []
  multiplicity upper_bound in scope pack -> 3
```

SysIDE evaluates the redefined bound as 3. The instance graph holds 2 occurrences of `cells`. A count check would catch the defect where the value comparison cannot.

Verdict, B2: **holds for the trace, partly for the native match.** Plain and nested occurrences: trace and value both hold. Indexed occurrences: the trace holds (index recorded per step), but SysIDE evaluates per definition, not per index. Agreement there only shows that every occurrence matches the definition's value. Aggregations over a multiplicity: the trace holds, the native value is wrong (B1). The design's stated basis (`ModuleOutput` keeps source information, `resolution/models.py:196`) is wrong: the trace is in the instance graph and the private projection, not in `ComputationGraph`.

### S3: positional binding (premise check)

Commands (from `spike/`, `F=/home/reid/src/subset-conformance/agentic-mbse/tests/fixtures/positional_binding/native_values`):

```bash
./codegen.sh -m sysml_codegen check --models $F/gen_reversed
./codegen.sh -m sysml_codegen generate --models $F/gen_reversed --output /tmp/grg-spike/gen-gen_reversed --package-name gen_reversed
./codegen.sh channel-trace/probe_channels.py $F/gen_reversed /tmp/grg-spike/run-gen_reversed gen_reversed
# same three for gen_byname
```

Wiring read from `pipelines/pipeline.yaml`, module `*__plant__diff`.

| fixture | check | generate | wiring | native `diff.r` | generated `diff.r` / `plant.result` |
|---|---|---|---|---|---|
| `gen_reversed` (`in b = small; in a = big;`) | 0 | 0 | `a ← plant__big`, `b ← plant__small` | -7.0 | 7.0 / 7.0 |
| `gen_byname` (`in :>> b = small; in :>> a = big;`) | 0 | 0 | `a ← plant__big`, `b ← plant__small` | 7.0 | 7.0 / 7.0 |

Verdict: current sysml-codegen **binds by name**. It does not refuse and does not bind by position. This is the same result as at `b5663c07` (`.project/completed/20261018_positional-binding-check/evidence/cross-route/eval_generated.log`). The design's reading of `elaboration/elaborate.py:2181-2193` and `occurrence.py:251-254` as positional does not match the observed behaviour. `semantic-hazards.md:47-58` stays correct. The comparison would flag `gen_reversed` as a difference, which makes it a good "differ" fixture.

## Reproduction

From the agentic-mbse root, with `SYSIDE_LICENSE_KEY` in `.env`, dc3's venv at `/home/reid/src/dc3/.venv`, and TEAx at `/home/reid/src/teax`:

1. S1: `uv run pytest .project/active/generated-results-guidance/spike/native-path/test_native_path.py -s -q -p no:cacheprovider`, then `uv run python .project/active/generated-results-guidance/spike/native-path/probe_extra.py`.
2. S2: `cd .project/active/generated-results-guidance/spike/channel-trace` and run the three `../codegen.sh probe_channels.py ...` commands above, then `../codegen.sh probe_count.py models/default_count`.
3. S3: from `spike/`, run the S3 commands above.

`codegen.sh` writes no bytecode; package and run output goes to `/tmp/grg-spike/`. Afterwards, `git status --short` in sysml-codegen and TEAx should be empty. pytest under `uv run` can leave `__pycache__` in `native-path/`; delete it.

## Open Questions / Follow-ups

- **Multiplicity aggregations.** How should `compare` know a channel ranges over a multiplicity, so it reports "not compared"? Likely from the computed node's expression IR referencing a slot with more than one occurrence. Not probed.
- **Count check.** A native-bound against built-occurrence count check would catch `[ATTRIBUTE-MULTIPLICITY-DEFAULT-COUNT]`. This is new scope for the design (an owner or design call), not tested beyond the one probe.
- **Indexed values.** Can a SysML model give different values per index (for example through subsetting parts with redefinitions)? If so, per-index native values are unavailable. `packredef` in `model_extra` used `:>> capacity := 4.0` on a subset part, but its native `sum` still read one value, so this was not settled.
- **Verdict join.** The native-to-generated verdict join through `usage_qualified_name` / `owner_instance_path` was not written in code; it was only compared by eye for two constraints.
- **Not checked:** quantities with units (`experimental_quantities`), Integer/Boolean output channels (none of these models emitted one), calc usages nested inside indexed occurrences more than one level deep, and models split across several files.
- **Back-reference.** The spike procedure asks for a back-reference in `design.md` at B1/B2. The brief said not to change the design, so none was written. The design's B1 and B2 bullets and line 46 need updating from this file.
