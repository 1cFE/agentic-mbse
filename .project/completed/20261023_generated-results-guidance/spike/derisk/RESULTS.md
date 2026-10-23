# Phase 1 de-risk: design bets B1 (shapes), B2, B3, B4

Run 2026-10-22. agentic-mbse `generated-results-guidance` (Phase 0 commit `697e94f5`). sysml-codegen branch `native-generated-compare` at `origin/main` `6190f996`, read-only (no sysml-codegen code changed). TEAx `8d877460`. SysIDE 0.8.4. Interpreter: dc3's venv through `spike/codegen.sh`, as in the spike. Scratch under `/tmp/grg-impl/derisk/`. Afterwards `git status --short` is empty in sysml-codegen and TEAx; dc3 shows only its pre-existing untracked folder (see `evidence/baseline.md`).

## Gate result: FAIL. Stop before Phase 2.

| Bet | Verdict | In one line |
|---|---|---|
| B2 (multiplicity mark) | **holds** | Every value SysIDE gets wrong because of a multiplicity was marked; nothing at `[1]` or on a named subset was marked. No generated model can read a `[0]` slot. |
| B3 (effective usage as scope and bound) | **holds** | On the dc3-shaped model the effective usage gives value 10.0 and bound 3, matching generated 10.0 and 3 built. The slot root gives 2.0 and 1. |
| B4 (SysIDE sees redefinitions above the scope) | **fails** | Two shapes. SysIDE returns the inner default, while the generated package returns the redefined value the model means. |
| B1 (shapes) | **fails for units**; holds for Integer, Boolean (native side), split files and two indexed levels | SysIDE gives no value for any expression with a unit annotation (`2.0 [kg]`). |

Separately from the bets, the Boolean shape exposed a gap in the design's comparison rule: the package writes `1.0` for a Boolean output. Details are under B1 below.

## What failed, and what it means for the design

### B4 fails: SysIDE misses redefinitions that are not on the scope element itself

`evaluate_feature` takes one scope element. It applies redefinitions written in that element's own body. It does not apply two other kinds, both of which the generator does apply.

**Shape 1: a redefinition reached through a re-typing (`outer_retyping`).** The outer usage re-types `middle` as `HotMiddle`. `HotMiddle` re-types `inner` as `HotInner`, and `HotInner` redefines `k = 7.0`. So `outer.middle.inner.tripled` means `7 × 3 = 21`.
- The generator's effective usage for the innermost step is `HotMiddle::inner`. That is the right usage, so B3 holds here.
- With that usage as scope, SysIDE gives `tripled` 3.0 and `k` 1.0: the `Inner` default. The generated value is 21.0.
- SysIDE gives 21.0 only with the type `HotInner` as scope. The outer usages (`outer::middle`, `outer`) also give 3.0.

**Shape 2: a calc usage inside a part whose input value is redefined on that part (`named_subsets`, `split_files`).** `rack_2 :> racks { :>> capacity = 4.0; }` contains the calc usage `d` (`in x = capacity`), declared in `Rack`. The model means `rack_2.d.y = 8.0`.
- The probe's scope for a calc usage's output is the calc usage itself (`Rack::d`), the spike's rule. With it, SysIDE gives 4.0 (from the `Rack` default 2.0). The generated value is 8.0. `split_files` repeats this: `cart.motor.t.y` gives native 6.0, generated 12.0, because `motor` redefines `power = 4.0`.
- No other single scope gives the right value. With `rack_2` as scope, the calc usage `d` evaluates to the usage object, and `y` gives a diagnostic: `Invalid operator '*' for types 'element' and 'rational'` (`output/diagnose.txt`).
- `rack_1.d.y` agrees only because `rack_1` redefines nothing.

**Consequence.** In both shapes the result is a **false difference on a correct package**: `compare` would exit 1 and the workflow would tell the modeller to file a generator bug. The design expected B4's danger to be the reverse, both routes agreeing on a wrong value. That was not observed here, but nothing rules it out.

dc3 has both shapes. Its facility is a specialised part def that redefines subsystem parts. Its named parts redefine values (`rack_1 { :>> distribution_voltage = 380.0 [V]; … }`, `server_1 { part :>> psu : 'DC Server Power Supply' { :>> efficiency = 0.96; } }`), and those parts' definitions hold the calculations. I did not run dc3 through the probe. From its source, many dc3 outputs are of these kinds.

**The design's stated fallback (B4), not applied:** "the generator's redefinition index tells which features are redefined above the innermost scope, and those items become not compared, with the reason 'redefined above the evaluation scope'." Two things about it are untested:
- whether the generator's redefinition data can identify both shapes, in particular Shape 2, where the redefinition sits on the occurrence that contains the calc usage, not above it;
- how much it would leave uncompared on dc3. Shape 2 would cover every calc usage in a part that redefines one of its inputs.

**For the design to decide (not decided here):** whether a native value can come from somewhere other than one `evaluate_feature` scope. The diagnostic shows the type as scope gives the right value in Shape 1. This item does not explore that, because it would be a redesign.

### B1 fails for units

The generator accepts a unit only as an annotation on a `Real` (`Real = 2.0 [kg]`, sysml-codegen fixture `unit_annotation_lanes`). It refuses quantity types (`ISQ::MassValue`: `unsupported exact type 'ISQBase::MassValue'`). It uses the number as written: `500.0 [g]` gives 500.0, and `grams * 2.0` gives 1000.0.

SysIDE, by default, returns no value for any expression that reaches a unit annotation: `Operator '[' is not model-level evaluable`. That applies to `mass`, `grams`, and everything computed from them.
- Under the design's D5, that is the cause "no native value", so the item is not compared. It is safe, not a false difference. But every value downstream of a unit annotation goes uncompared, and dc3 writes unit annotations throughout (`1000.0 [V]`, `60.0 [Hz]`).
- With `experimental_quantities=True`, SysIDE converts to SI base units: `mass` 2.0, `double_mass` 4.0 (agrees), `grams` 0.5, `double_grams` 1.0. The generated value is 1000.0. So turning quantities on gives a false difference for any non-base unit (g, kW, kWh). Which number is right is the generator's call (RG-1); this records the mismatch only.

The design names no fallback for B1 beyond "each gets a test before release". The D5 "no native value" cause already covers the default behaviour.

### Comparison-rule gap: Boolean and Integer outputs are written as floats

The instance graph types every output port as `python_type float`, including `heavy : Boolean` and `n2 : Integer`. The run files hold `1.0` for `heavy` and `6.0` for `n2`. SysIDE gives `True` and `6`.
- The probe compares Booleans exactly by type, so `heavy` failed (native `True`, generated `1.0`). `n2` passed, because the probe compares an int with a float numerically.
- D8 says "Booleans and integers must match exactly". The generated side carries no Boolean or Integer type, so the design needs to state how a generated `1.0` compares with a native `True`, and where the declared type comes from (the SysIDE feature's type is one source).
- I classed this as a design gap, not a failed bet, because SysIDE's value is right. The orchestrator may weigh it differently. Whether outputs should keep their type is a generator question (RG-1).

## What held

### B2 holds

The rule as run: mark every node whose scope lies inside an occurrence of a slot with more than or fewer than one occurrence, then mark everything downstream over input and alias edges. The cause names the outermost such slot.

- Every value where native SysIDE is wrong because of a multiplicity was marked: `s1_gen host.pack.total` (2.5 against 7.5), `default_count pack.total`, `default_count_literal pack.total` (3.2 against 9.6), `named_subsets room.rack_sum` (2.0 against 4.0).
- Nothing at `[1]` was marked (`one_slot`: index 0, compared, agrees). Named subsets were not marked (`rack_1`, `rack_2`, `named_total`).
- Indexed values two levels deep were marked with the outermost slot (`pack.modules (2)`), and so were counts nested inside an indexed occurrence.

**The `[0]` rule has no input, and needs none.** `check` refuses every way I tried to read a `[0]` slot. The models are in `models_refused/`, and the output is in `output/checks.txt`:

| model | read form | `check` |
|---|---|---|
| `zero_slot` | `attribute total = sum(x.v)` | exit 1, `SI_OCCURRENCE_MISSING … has no concrete occurrence` |
| `zero_variants/z_scalar_expr` | `attribute t = x.v * 2.0` | exit 1, `SI_OCCURRENCE_MISSING` |
| `zero_variants/z_alias` | `attribute t = x.v` | exit 1, `SI_OCCURRENCE_MISSING` |
| `zero_variants/z_scalar_binding` | `calc c : Id { in a = x.v; }` | exit 1, `SI_OCCURRENCE_MISSING` |
| `zero_variants/z_sum_binding` | `calc c : Id { in a = sum(x.v); }` | exit 1, `SI_EXPRESSION_SOURCE_UNSUPPORTED` (expression binding) |
| `zero_variants/z_constraint` | `assert constraint { sum(x.v) >= 0.0 }` | exit 1, `SI_CONSTRAINT_BLOCKED` and `SI_OCCURRENCE_MISSING` |

Graph validation also refuses an aggregation reference with no edges (`elaboration/graph.py`, `_validate_calculation_payload`: "typed IR reference {ordinal} has {count} permitted edges" when the count is 0 and the graph has no diagnostics). The probe found no zero-edge aggregation reference in any model.

`zero_unread` is the dc3 shape: a `[0]` redefinition that nothing reads. It generates, has no occurrence for `x`, and its one value agrees.

**Answer to the design's Open item ("the exact data for the zero-occurrence mark"):** no graph field is needed. No projectable instance graph contains a node that reads an empty slot, because the generator refuses such models, and graph validation forbids a zero-edge aggregation reference.

Two observations; neither fails the bet:
- **`named_subsets rack_sum`: generated 4.0, where SysML means 6.0.** The generator builds `racks[0]` and `racks[1]` from the shared declaration and builds `rack_1` and `rack_2` as separate slots. So `sum(racks.capacity)` adds two default capacities, 2.0 + 2.0, and ignores `rack_2`'s 4.0. The value is marked, so `compare` would not call it agreement, but it would not flag it either. This is the case design D5 worried about (members given their own values). Whether that generated value is a defect is the generator owner's call (RG-1).
- **The count check cannot see a `[0]` slot.** Count rows are grouped from occurrence records, and an empty slot has none. If the generator built 0 parts where the model asks for some, no count row would exist. This is a gap in D7's coverage, not one of the four bets.

### B3 holds

`dc3_redefinition` mirrors `dc_facility.sysml`. `'Native Facility' :> Facility` writes `part :>> electrical { attribute :>> load = 5.0; part :>> racks[3]; }`.

| item | effective usage as scope | slot root as scope (the spike's rule) | generated / built |
|---|---|---|---|
| `site.electrical.scaled` (`load * 2.0`) | 10.0, scope `'Native Facility'::electrical` | 2.0, scope `Facility::electrical` | 10.0 |
| count `site.electrical/racks` | 3, usage `'Native Facility'::electrical::racks` | 1 | 3 |
| `site.facility_load` (`electrical.load + 1.0`) | 6.0, scope `site` | 6.0 | 6.0 |

### B1 shapes that held

- **Split files** (`split_files`, two files): `cart.motor.boosted` 5.0 and `cart.cart_power` 10.0 agree. Its one failing row, `cart.motor.t.y`, is B4 Shape 2 and has nothing to do with the file split.
- **Two indexed levels** (`nested_indexed`): every `pack.modules[i].cells[j].d.y` traced to `Double::y` with the calc usage as scope, native 3.0 = generated 3.0, and marked `multiplicity pack.modules (2)`.
- **Integer** (`n2`): native 6, generated 6.0, numerically equal.
- **Boolean** (`heavy`): native `True` is right. The generated side is the comparison-rule gap above.

`check` refused two of the B1 shapes as first drafted, before the probe ran. Both refusals are recorded, not worked around:
- a computed attribute inside an indexed part (`attribute doubled = capacity * 2.0` in `Rack[2]`): `REGISTRY_CLASS_NAME_COLLISION … grandparent collision`;
- a calc usage's result read inside an expression (`boosted = t.y + 1.0`): `elaboration_feature_declaration_unindexed`.

The models use the shapes the generator accepts instead. `EXPECTED.md` § "Changes made after `check`" lists every change.

## Commands

From `.project/active/generated-results-guidance/spike/`:

```bash
# every model must pass check before it counts (outputs: output/checks.txt)
for d in derisk/models/*/ derisk/models_refused/zero_slot derisk/models_refused/zero_variants/*/; do
  ./codegen.sh -m sysml_codegen check --models "$d"
done

# the probe: trace, B2 marks, counts, native, generated, checked against EXPECTED.md
./codegen.sh derisk/probe_derisk.py            # exit 1; full output: output/probe_derisk.txt

# diagnostics for the failures (not pass conditions): output/diagnose.txt
./codegen.sh derisk/diagnose.py
```

`probe_derisk.py` exits 1. The summary line:

```
SUMMARY dc3_redefinition=PASS default_count=PASS default_count_literal=PASS gen_byname=PASS gen_reversed=PASS named_subsets=FAIL nested_indexed=PASS one_slot=PASS outer_redefinition=PASS outer_retyping=FAIL s1_gen=PASS split_files=FAIL units_int_bool=FAIL zero_unread=PASS
```

The failing rows, verbatim:

```
FAIL value room.rack_2.d.y  native 4.0  generated 8.0  mark -
     feature NamedSubsets::Double::y, scope NamedSubsets::Rack::d
FAIL value outer.middle.inner.tripled  native 3.0  generated 21.0  mark -
     feature OuterRetyping::Inner::tripled, scope OuterRetyping::HotMiddle::inner
FAIL value cart.motor.t.y  native 6.0  generated 12.0  mark -
     feature SplitLib::Triple::y, scope SplitLib::Motor::t
FAIL value box.double_grams  native None  generated 1000.0  mark -
     native diagnostics: ["Operator '[' is not model-level evaluable"]
FAIL value box.double_mass  native None  generated 4.0  mark -
     native diagnostics: ["Operator '[' is not model-level evaluable"]
FAIL value box.heavy  native True  generated 1.0  mark -
```

The key diagnostic lines:

```
evaluate_feature(OuterRetyping::Inner::tripled, scope=OuterRetyping::HotMiddle::inner) -> (3.0, [])
evaluate_feature(OuterRetyping::Inner::tripled, scope=OuterRetyping::HotInner) -> (21.0, [])
evaluate_feature(NamedSubsets::Rack::d, scope=NamedSubsets::Room::rack_2) -> ('<syside.core.CalculationUsage object …>', [])
evaluate_feature(NamedSubsets::Double::y, scope=NamedSubsets::Room::rack_2) -> (None, ["Invalid operator '*' for types 'element' and 'rational'"])
evaluate_feature(UnitsIntBool::Box::double_grams, scope=UnitsIntBool::box, {'experimental_quantities': True}) -> (1.0, [])
```

## Files

- `EXPECTED.md`: expected values, written before the probe ran, with the changes `check` forced listed separately.
- `models/`: the 14 models the probe runs. Five are copies: `s1_gen`, `default_count` and `default_count_literal` from `../channel-trace/models/`, and `gen_reversed` and `gen_byname` from `tests/fixtures/positional_binding/native_values/`.
- `models_refused/`: `zero_slot` and the five `zero_variants`, kept as the record of the `[0]` refusals.
- `probe_derisk.py`: the probe. `diagnose.py`: the failure diagnostics.
- `output/`: `probe_derisk.txt` (full probe output, with INFO and WARNING lines removed), `diagnose.txt`, `checks.txt`.
- `identity_record.sh`: the byte-identity recorder used in Phase 0 and at the end of this phase. The "before" records for these models are in `/tmp/grg-impl/identity-before/spike/derisk_*`, generated on the untouched `6190f996` code, all 14 exit 0. The file list is `/tmp/grg-impl/identity-before/tree-sha256-derisk.txt`, sha256 `b2b7e6eed1a0f4c34fb0fc3d3dbd4f9360b76334ab6bef0b4e93f35a6fb1b9a0`. A second generation of the Phase 0 spike models and of dc3 gave identical bytes.

## Not checked

- dc3 itself was not run through the probe. The dc3 statements above come from reading its source.
- Verdict comparison (D9) is Phase 4 and was not part of this gate.
- Whether the generator's redefinition data can drive the B4 fallback was not looked at.
- `probe_derisk.py` finds an indexed slot's display name by removing a trailing `[n]` from the display segment. That is fine for a throwaway probe. Production code must use the graph's display helpers (plan Phase 2).
