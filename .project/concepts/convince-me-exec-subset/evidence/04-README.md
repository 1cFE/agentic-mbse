# Claim 4 evidence: positional-binding hazard and check

Claim: in the end state, the positional-binding hazard is caught by `L2_POSITIONAL_BINDING` using resolved redefinition evidence. Explicit by-name (`in :>> b`) and deliberate rename (`in local redefines a`) pass. The recommended by-name form gives the correct value both natively and through codegen.

Run at 2026-10-15T13:53Z. SysIDE 0.8.4.

| Repository | Revision | Tree state |
|---|---|---|
| agentic-mbse | `d546a00f3b26ff20aa023c8e090d7ca764a09619` | dirty: pre-existing `.project/` edits and untracked files from the session start; no source changes |
| sysml-codegen | `b5663c07e987a892e27d21e68cec40d0656574ee` | clean |
| dc3 (checkout; venv used for codegen + TEAx) | `60b44d53460fccd2f44811d8abfd42bc270e90b2` | clean |
| dc3 baseline models | `808464df85d50521e4fbb9ba7cceb63d382aa832` via `git archive` to scratch | read-only copy |
| fusion-tea `models/` | `f96ad312c63e8c66695971b12feab971f3ba6eb3` | clean, scanned in place read-only |
| teax (simkit runtime) | `8d877460ac4f6f264561d916e40c1708adb13397` | clean |

Scratch root: `/tmp/claude-1000/-home-reid-src-agentic-mbse/8cecfa0f-3dca-4be9-bcbc-86b4acc4ae95/scratchpad/` (`dc3-base/`, `dc3-fixed/`, `c4/`).

## Commands (run from this `evidence/` directory)

```bash
# Values: native SysIDE, and codegen generate -> sealed load -> TEAx execute_pipeline
/home/reid/src/dc3/.venv/bin/python -I 04-eval.py > 04-eval.log 2>&1

# Detector: fixtures, naive control, pinned trees, mutation control, injected-failure control
P=/home/reid/src/agentic-mbse/.venv/bin/python
S=/tmp/claude-1000/-home-reid-src-agentic-mbse/8cecfa0f-3dca-4be9-bcbc-86b4acc4ae95/scratchpad
$P -I 04-detector.py fixtures   > 04-detector-fixtures.log
$P -I 04-detector.py naive      > 04-detector-naive-control.log
$P -I 04-detector.py tree dc3-base   $S/dc3-base/models  > 04-detector-tree-dc3-base.log
$P -I 04-detector.py tree dc3-fixed  $S/dc3-fixed/models > 04-detector-tree-dc3-fixed.log
$P -I 04-detector.py tree fusion-tea /home/reid/src/fusion-tea/models > 04-detector-tree-fusion-tea.log
$P -I 04-detector.py mutate $S/dc3-fixed/models $S/c4/dc3-fixed-mutated > 04-detector-mutation-control.log
$P -I 04-detector.py unverified > 04-detector-unverified-control.log
```

Fixtures: `04-fixtures/gen_byname/`, `04-fixtures/gen_reversed/` (generation), `04-fixtures/detector/*.sysml` (17 cases; each header states `expect` and the expected flagged inputs, written before the run).

## Results

- **Values** (`04-eval.log`), intended `a - b = 10 - 3 = 7`:
  - in-order unprefixed: native 7.
  - reversed unprefixed: native **−7**, generated **7**.
  - reversed `:>>`: native 7, generated 7.
  - explicit rename: native 7.
- **Fixtures**: 17/17 match their expectation (`04-detector-fixtures.log`).
- **Naive name-set control**: wrong on 9/17 fixtures (`04-detector-naive-control.log`). It misses every swap and flags the deliberate rename.
- **Pinned trees**:
  - dc3 baseline: 0 findings (302 implicit same-name inputs).
  - dc3 repaired: 0 findings (391).
  - fusion-tea: **125 findings** (5,573 matching). See the surprise below.
- **Mutation control**: swapping two in-order unprefixed inputs in a copy of the dc3 repaired tree (`designs/ac_coupled/ac_facility.sysml:226-227`) raises findings from 0 to 2, at those two lines.
- **Injected-failure control**: a simulated SysIDE inspection error is reported as `UNVERIFIED` (2 results), not as clean.

## Surprises

1. **The generated and native routes disagree on the same text.** codegen `b5663c07` wires an unprefixed calc-usage input by its declared name. SysIDE binds it by position. For `in b = 3; in a = 10;` native gives −7 and generated gives 7. The hazard is therefore a cross-route divergence as well as a native wrong value.
2. **fusion-tea `f96ad312` is not clean under this rule.** It has 125 implicit redefinitions to differently named formals, across 9 files and 6 calc defs. 57 of them are in `designs/aries_cs_integrated/plant.sysml` `plant_ledger::evaluate`, which declares the `electric_*` inputs first while `'Integrated Plant Ledger'` declares them last. They demonstrate real implicit name/target mismatches. The toy establishes name-based generated wiring, but the affected fusion-tea routes were not regenerated or compared; harmlessness is not established. The inspected definitions are described as opaque; absence of a native body does not establish overall cross-route equivalence. The epic's "pinned consumers pass" criterion therefore conflicts with the rule unless owner decision 3 (severity and intentional-use policy) makes these non-blocking, or fusion-tea migrates to `:>>`. fusion-tea's generated package was not regenerated in this check; the by-name wiring is shown on the toy fixture only.
3. **One development fix during the run.** The first fixture run flagged `inherit_def_extends` as UNVERIFIED, because SysIDE's `inherited_features` still lists already-redefined parent inputs. The detector now excludes inputs that an owned input redefines. The fixture expectation was not changed.
4. The dc3 mutation swaps two factors of a product (`'Serial Path 8'`), so the swap is value-neutral there. The detector flags the binding regardless of value; the value consequence is shown on the toy calc.

Scope limits: only calculation and constraint owners (usages and definitions, with subtypes) are scanned, not action or analysis-case parameters beyond those kinds. Out-parameters are not checked. This is a throwaway prototype, not repo source.

## Audit clarification (2026-10-15)

The “naive” control checks whether authored names occur among formal names; it is not an exact implementation of the original epic's owned-redefinition-name-set expression. Its 9/17 failure count applies to this control only. The detector remains a prototype: skipping all implied relationships when any explicit redefinition exists and treating a missing declared name as anonymous need broader semantic tests. Diagnostic suggestions are not automatic fixes: choose the intended formal from source/definition evidence, not blindly the currently inferred positional target.
