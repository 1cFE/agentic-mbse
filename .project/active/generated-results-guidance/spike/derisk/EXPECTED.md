# Expected results for the Phase 1 probe (written before any run)

`probe_derisk.py` reads the table below and checks every traced item against it. Each row is one item (or a family of indexed items, `[*]`) in one model.

## How to read a row

- **kind.** `value` is an output channel. `count` is one (owning occurrence, part usage with an explicit multiplicity) pair.
- **item.** For `value`: the occurrence path, then the output (`pack.total`; a calc usage adds its own name, `pack.cells[*].d.y`). For `count`: the owning occurrence path, `/`, the part usage's segment (`pack/cells`).
- **intended.** What the model means in SysML. For a count, the number of parts the model asks for.
- **generated.** The value the generated package should compute, or for a count the number of occurrences the generator should build. `-` means not a pass condition.
- **native.** What SysIDE should return with the effective usage as scope. For a count, the multiplicity bound evaluated in the owner's effective usage. `-` means not a pass condition (a marked item whose native value is known to be wrong or unknown).
- **result.** `agree`: not marked, native equals generated. `differ`: not marked, native and generated differ with the values given. `nc multiplicity <path> (<n>)`: marked by the B2 rule, with that cause.

A traced item that matches no row is a FAIL, and so is a row that matches no traced item. Numbers agree within 1e-9 relative; Booleans and integers must match exactly.

## Which bet each model tests

- B1 shapes: `units_int_bool`, `split_files`, `nested_indexed` (trace under two indexed levels), plus the reused spike models.
- B2: `default_count_literal`, `default_count`, `zero_unread` (and the refused `zero_slot` / `zero_variants`), `one_slot`, `named_subsets`, `nested_indexed`, `dc3_redefinition` (racks), `s1_gen` (pack.total).
- B3: `dc3_redefinition` (value and count under the effective usage).
- B4: `outer_redefinition` (value redefined in nested bodies two levels below the outer usage), `outer_retyping` (the outer usage re-types the middle part, whose type re-types the inner part), `split_files` (a calc usage inside a part whose input value is redefined on the containing usage).

## Rows

| model | kind | item | intended | generated | native | result |
|---|---|---|---|---|---|---|
| s1_gen | value | host.doubled.r | 6.0 | 6.0 | 6.0 | agree |
| s1_gen | value | host.neg_load | -3.0 | -3.0 | -3.0 | agree |
| s1_gen | value | host.pack.total | 7.5 | 7.5 | - | nc multiplicity host.pack.cells (3) |
| s1_gen | count | host.pack/cells | 3 | 3 | 3 | agree |
| default_count | value | pack.cells[*].d.y | 6.4 | 6.4 | 6.4 | nc multiplicity pack.cells (2) |
| default_count | value | pack.total | 9.6 | 6.4 | - | nc multiplicity pack.cells (2) |
| default_count | count | pack/cells | 3 | 2 | 3 | differ |
| default_count_literal | value | pack.cells[*].d.y | 6.4 | 6.4 | 6.4 | nc multiplicity pack.cells (3) |
| default_count_literal | value | pack.total | 9.6 | 9.6 | - | nc multiplicity pack.cells (3) |
| default_count_literal | count | pack/cells | 3 | 3 | 3 | agree |
| gen_reversed | value | plant.diff.r | -7.0 | 7.0 | -7.0 | differ |
| gen_byname | value | plant.diff.r | 7.0 | 7.0 | 7.0 | agree |
| zero_unread | value | holder.free | 3.0 | 3.0 | 3.0 | agree |
| one_slot | value | pack.cell[*].d.y | 5.0 | 5.0 | 5.0 | agree |
| one_slot | value | pack.total | 5.0 | 5.0 | 5.0 | agree |
| one_slot | count | pack/cell | 1 | 1 | 1 | agree |
| named_subsets | value | room.rack_1.d.y | 4.0 | 4.0 | 4.0 | agree |
| named_subsets | value | room.rack_2.d.y | 8.0 | 8.0 | 8.0 | agree |
| named_subsets | value | room.named_total | 6.0 | 6.0 | 6.0 | agree |
| named_subsets | value | room.racks[*].d.y | 4.0 | - | - | nc multiplicity room.racks (2) |
| named_subsets | value | room.rack_sum | 6.0 | - | - | nc multiplicity room.racks (2) |
| named_subsets | count | room/racks | 2 | 2 | 2 | agree |
| dc3_redefinition | value | site.electrical.scaled | 10.0 | 10.0 | 10.0 | agree |
| dc3_redefinition | value | site.facility_load | 6.0 | 6.0 | 6.0 | agree |
| dc3_redefinition | value | site.electrical.racks[*].d.y | 2.0 | 2.0 | 2.0 | nc multiplicity site.electrical.racks (3) |
| dc3_redefinition | count | site.electrical/racks | 3 | 3 | 3 | agree |
| outer_redefinition | value | outer.middle.inner.tripled | 21.0 | 21.0 | 21.0 | agree |
| outer_retyping | value | outer.middle.inner.tripled | 21.0 | 21.0 | 21.0 | agree |
| units_int_bool | value | box.double_mass | 4.0 | 4.0 | 4.0 | agree |
| units_int_bool | value | box.double_grams | 1000.0 | 1000.0 | 1000.0 | agree |
| units_int_bool | value | box.n2 | 6 | 6 | 6 | agree |
| units_int_bool | value | box.heavy | True | True | True | agree |
| split_files | value | cart.motor.t.y | 12.0 | 12.0 | 12.0 | agree |
| split_files | value | cart.motor.boosted | 5.0 | 5.0 | 5.0 | agree |
| split_files | value | cart.cart_power | 10.0 | 10.0 | 10.0 | agree |
| nested_indexed | value | pack.modules[*].cells[*].d.y | 3.0 | 3.0 | 3.0 | nc multiplicity pack.modules (2) |
| nested_indexed | count | pack/modules | 2 | 2 | 2 | agree |
| nested_indexed | count | pack.modules[*]/cells | 3 | 3 | 3 | nc multiplicity pack.modules (2) |

## Changes made after `check`, before the probe ran

The table above was first written with the models as drafted. `sysml-codegen check` then refused some of them, so the models and rows changed as listed here. The probe had not run when these changes were made. Every refusal is recorded with its output in `RESULTS.md`.

- **zero_slot** (`total = sum(x.v)` over `x : X[0]`): refused, `SI_OCCURRENCE_MISSING … has no concrete occurrence`. Its three rows were removed. Five more ways of reading a `[0]` slot were tried (`models_refused/zero_variants/`; the first model is `models_refused/zero_slot/`); all are refused. In their place, **zero_unread** is the dc3 shape: a `[0]` redefinition that nothing reads, with one unrelated value (`holder.free`).
- **named_subsets, dc3_redefinition**: a computed attribute inside an indexed part (`attribute doubled : Real = capacity * 2.0` in `Rack`) is refused, `REGISTRY_CLASS_NAME_COLLISION`. Replaced by a calc usage (`calc d : Double { in x = capacity; }`), the shape the spike models already use. Rows renamed from `doubled` / `double_power` to `d.y`.
- **outer_redefinition, outer_retyping**: `out` is a SysML keyword (my parse error); renamed to `tripled`. The output row is now `outer.middle.inner.tripled`.
- **dc3_redefinition, named_subsets, outer_*, split_files**: a value bound with `=` in a definition cannot be redefined (SysIDE `feature-value-overriding`, my modelling error). Those definition values are now `default` values.
- **units_int_bool**: an `ISQ::MassValue` attribute is refused (`unsupported exact type 'ISQBase::MassValue'`). The generator's accepted unit form is a unit annotation on a `Real` (sysml-codegen fixture `unit_annotation_lanes`), so the model uses `Real = 2.0 [kg]` and adds a non-base unit, `Real = 500.0 [g]` (row `box.double_grams`, intended 1000.0, the number written).
- **split_files**: `boosted = t.y + 1.0` (a calc usage's result read inside an expression) is refused, `elaboration_feature_declaration_unindexed`, in one file as well as two, so the cause is the shape, not the split. Changed to `boosted = power + 1.0`. Rows: `boosted` 5.0, `cart_power` 10.0.

## Notes on rows that are not obvious

- **default_count `pack.total`.** Generated 6.4 is the defect (2 cells built for 3). The value is marked, so the defect is caught by the count row (`differ`), not by the value.
- **zero_unread counts.** There is no count row for `holder/x`: a slot with no occurrences has no occurrence record to group by. If the probe can find it some other way, that is recorded; if not, it is a gap in the count check to report (it is not one of the four bets).
- **named_subsets `rack_sum`.** In SysML the two members of `racks` are `rack_1` and `rack_2` (2.0 + 4.0 = 6.0). The generator builds `racks[0]` and `racks[1]` from the shared declaration and `rack_1`, `rack_2` as their own slots, so its value may be 4.0. SysIDE reads one part (2.0). The row only requires the mark; the generated value is recorded as an observation about the design's D5 concern, not a pass condition.
- **dc3_redefinition contrast.** The probe also prints the native value and bound with the slot root as scope (`Facility::electrical`), expected `scaled` 2.0 and bound 1. That shows why the effective usage matters; it is not a pass condition.
- **nested_indexed.** Every `d.y` sits inside both `pack.modules[i]` (2) and `cells[j]` (3). The cause names the outermost slot with a count other than 1. The native value is still checked, because B1 says the trace (feature and calc-usage scope) must hold under two indexed levels even though the item is not compared.
