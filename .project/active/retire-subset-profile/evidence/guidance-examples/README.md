# Checks of the Phase 2 guidance examples

Each folder holds a full model built around one shipped example (`model.sysml`) and the output of `uv run --frozen sysml-codegen check --models <folder>` (`check.txt`), run 2026-10-21 from the sysml-codegen worktree on branch `subset-profile-screen`. These add to `../probes.md`; they test the examples as written, not the limits in general.

| folder | example it checks | exit | answer |
|---|---|---|---|
| `a_ok` | guide limit 1, correct (assert on `Heater`) | 0 | builds (3 modules) |
| `a_bad` | guide limit 1, incorrect (assert in `calc def PowerCalc`) | 1 | `SI_CONSTRAINT_UNATTACHED`, owner `calc_def` |
| `m_ok` | guide limit 2, `Cell[3]` | 0 | builds |
| `s_ok3` | guide limit 3, correct (`sum(cells.capacity)` on the part, one value per input) | 0 | builds (2 modules) |
| `s_bad3` | guide limit 3, incorrect (`in capacities = cells.capacity` with three cells) | 1 | `SI_OCCURRENCE_AMBIGUOUS`, "has 3 concrete occurrences" |
| `c1` | `constraints.md`, "Checking a Calculation's Result" correct form | 0 | builds (3 modules) |
| `c2` | `syntax-reference.md` Syntax 2 and 3 as corrected | 0 | builds (3 modules) |
| `c3` | `semantic-operators.md` "Correct: assert prefix, on a part" (plus a dummy calc so there is something to generate) | 0 | builds (3 modules) |
| `m_attr` | `mbse-concepts.md` old form: `default := 2` in the part def, `:>> cell_count = 3` in the usage | 0 | builds, but `generate.txt` and the generated package hold only `pack__cells[0]` and `pack__cells[1]`: two cells, not three, no warning |
| `m_attr_spec` | same, redefined in a specializing part def `BigPack :> Pack` | 0 | builds two cells, as above |

Two side findings while writing the examples, not in the guidance:

- A constraint def formal named `value` is refused (`CONSTRAINT_NAME_UNSAFE`, "collides with generated binding 'value'"). The examples use `amount`.
- The original `semantic-operators.md` temperature example (`Temperature` type, `1000 [K]` in the predicate) does not load: `Temperature` is not an ISQ type. With `ThermodynamicTemperatureValue` the generator refuses the quantity type. The corrected example uses a `Real` attribute in kelvin.

Not checked: the count when the base part def declares the attribute without a value and a specializing part def sets it.
