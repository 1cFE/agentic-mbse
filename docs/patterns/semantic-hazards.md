# Semantic Hazards

This register lists SysML v2 constructs that are valid, parse cleanly, and still mean something other than what an author usually expects. Each entry states the expected reading, what the language text says, what the tools were observed to do, how to write the construct safely, and what checks it.

**How citations read.** A path with no repository prefix (such as `tests/fixtures/positional_binding/`) is in the agentic-mbse source at the release that ships this file; `.project/` and `tests/` are in the source repository, not in an installed project. A path in another repository carries its revision, written `repository@revision:path`. Tool behavior is stated for the versions named in each entry only.

<a id="positional-input-binding"></a>
## Positional input binding

**Verified with:** SysIDE 0.8.4 (native evaluation); sysml-codegen `b5663c07` with TEAx `8d877460` (generated evaluation).

### What an author expects

An author writes a calculation usage and gives each input the name of the definition's parameter, in whatever order is convenient:

<!-- @positional-example expect="p::c|b|Sub::a; p::c|a|Sub::b" -->
```sysml
calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
part p {
    attribute big : Real = 10.0;
    attribute small : Real = 3.0;
    calc c : Sub { in b = small; in a = big; }
}
```

The expected reading is "`a` gets `big`, `b` gets `small`, so `c` is 10 - 3 = 7". That is not what the model says.

### What the language says (KerML text)

An input declared without `:>>` or `redefines` binds to the definition's parameter **at the same position**, not to the parameter with the same name. The rule is KerML constraint `checkFeatureParameterRedefinition` (KerML 8.3.3.3.4, Feature): a parameter of a step or behavior "must redefine the parameter at the same position" of each direct supertype. Positions count every directed feature (`in`, `out`, `inout`) and exclude the result parameter. The constraint's text exempts a parameter that has its own explicit redefinition only for invocation expressions.

So in the example above, `b` lands on `Sub::a` and `a` lands on `Sub::b`. The model is valid SysML and no validator error is expected.

### What SysIDE 0.8.4 does (observed)

Each observation names the fixture or test that shows it.

- **Reversed inputs swap.** The example evaluates natively to -7, not 7 (`tests/fixtures/positional_binding/native_values/sub_reversed.sysml`, `tests/test_validation/test_positional_binding_native_values.py`). Written in definition order it gives 7 (`tests/fixtures/positional_binding/native_values/sub_in_order.sysml`); written by name with `:>>` in reverse order it gives 7 (`tests/fixtures/positional_binding/native_values/sub_reversed_byname.sysml`).
- **An input with an explicit redefinition gets no positional one, but still takes up its position.** This goes further than the KerML text above, which exempts only invocation expressions. With `in local redefines a = 10; in b = 3;`, `b` still lands on position 2, `Sub::b` (`tests/fixtures/positional_binding/native_values/sub_rename.sysml`; `tests/learning/test_syside_input_redefinition.py`).
- **Mixing spellings leaves a parameter unbound.** With `in b = 3; in :>> a = 10;`, both inputs land on `Sub::a`, nothing binds `Sub::b`, and native evaluation gives no value at all (`tests/fixtures/positional_binding/native_values/sub_mixed.sysml`, `tests/fixtures/positional_binding/spelling/mixed_spelling.sysml`).
- **A parameterless subdefinition passes positions through.** With `calc def Sub3 :> Sub;` and a usage typed by `Sub3` with reversed inputs, the inputs land on `Sub::a` and `Sub::b` as if the usage were typed by `Sub` (`tests/fixtures/positional_binding/prototype/inherit_def_no_params_usage_reversed.sysml`).
- **An `out` parameter counts.** In `calc def O { out o : Real; in a : Real; in b : Real; }`, a usage's first input lands on `O::o`. SysIDE then reports `redefinition-direction-conformance`, but that diagnostic is not a parser error, so `validate` level 1 passes the model; level 2 reports it as two positional findings (`tests/fixtures/positional_binding/l1/out_before_in.sysml`, `.project/active/positional-binding-check/evidence/phase1-fixture-truth.md`).
- **Subject, actor and stakeholder count toward positions.** In a requirement or case, a usage that leaves out the subject puts its first ordinary input on the subject slot, and SysIDE reports a subject-position error. The same holds for actors and stakeholders (`tests/fixtures/positional_binding/requirements/`).
- **A multiply-typed input lands on one parameter per type** (`tests/fixtures/positional_binding/prototype/multiple_types.sysml`).
- **Constraints behave the same way.** Constraint usages, `assert constraint` and constraints nested in requirements bind their inputs by position (`tests/fixtures/positional_binding/prototype/constraint_reversed.sysml`, `tests/fixtures/positional_binding/prototype/assert_constraint_reversed.sysml`, `tests/fixtures/positional_binding/requirements/requirement_nested_constraint_reversed.sysml`).

### The two execution routes disagree, for calculation usages

For the reversed calculation usage, native SysIDE evaluation and generated execution give different answers:

| Fixture | Native SysIDE 0.8.4 | Generated, sysml-codegen `b5663c07` + TEAx `8d877460` |
|---|---|---|
| `tests/fixtures/positional_binding/native_values/gen_byname/` (inputs by name) | 7 | 7 |
| `tests/fixtures/positional_binding/native_values/gen_reversed/` (inputs reversed, unprefixed) | -7 | 7 |

The generator wires each input to the parameter with the same declared name, so the generated route gives the intended 7 while the native model says -7. Consequence: a passing generated run says nothing about whether the native model is correct. Generated-side log: `.project/active/positional-binding-check/evidence/cross-route/eval_generated.log`.

This divergence is claimed for calculation usages only. Constraint usages were not run through both routes, and sysml-codegen's own fixture notes say constraint actuals bind positionally there too (`sysml-codegen@b5663c07:tests/fixtures/modeled_default_fidelity/PROVENANCE.md`, "Authoring note"), so the routes may agree for constraints.

### How to write it safely

Pick the definition's parameter you mean, then use one of these:

- **Bind by name** with `:>>`. Order then does not matter.
- **Write the inputs in definition order**, with the definition's parameter names.
- **Rename deliberately** with `redefines`, when the usage needs its own name for a parameter.

<!-- @positional-example expect="none" -->
```sysml
calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
part p {
    attribute big : Real = 10.0;
    attribute small : Real = 3.0;
    calc by_name : Sub { in :>> b = small; in :>> a = big; }
    calc in_order : Sub { in a = big; in b = small; }
    calc renamed : Sub { in minuend redefines a = big; in subtrahend redefines b = small; }
}
```

In a requirement or case usage, declare `subject` (and any `actor` or `stakeholder`) before the ordinary inputs.

Renaming to avoid a self-binding (see `docs/patterns/plant-idiom.md`, "Binding a modelled value into a calculation") means renaming the parameter in the calculation **definition**. Renaming only the usage's input does not rename the parameter; the new name lands on whatever parameter sits at that position.

### What checks it

`validate` level 2 runs the positional-binding check. It reports an authored input of a calculation or constraint (usages and definitions, including requirements, cases and `assert constraint`) whose positional target has a different name. Each finding is one (owner, input, target) triple, its identity.

| Code | Severity | When |
|---|---|---|
| `L2_POSITIONAL_BINDING` | ERROR, `reason_code` `POSITIONAL_SWAP` | An input lands by position on a differently named parameter. Fails L2. |
| `L2_POSITIONAL_BINDING` | ERROR, `reason_code` `POSITIONAL_SPECIAL_SLOT` | The parameter it lands on is a subject, actor or stakeholder slot. Fails L2. |
| `L2_POSITIONAL_BINDING` | WARNING | The finding's identity is pinned as legacy (below). Does not by itself fail L2. |
| `L2_POSITIONAL_PIN_STALE` | ERROR | A pin matches no finding in a validated file, or its file does not exist. Fails L2. |
| `L2_POSITIONAL_PIN_LIST_INVALID` | ERROR | The pin list cannot be read or breaks its format. The check runs as if there were no list. Fails L2. |
| `L2_CHECK_UNVERIFIABLE` | ERROR, `reason_code` `POSITIONAL_<cause>` | An owner or input could not be inspected, for example because its type did not resolve. Fails L2. Never reads as clean. |

Not flagged: an input bound by name (`:>>`) or renamed with `redefines`; an input with no name; new inputs that do not land on a definition parameter; subject, actor and stakeholder inputs themselves (their own position is SysIDE's subject-position check). Level 2's metrics print the number of inputs inspected and the count of each outcome.

**Limits.**

- The check reads the redefinitions SysIDE resolves. It was verified on SysIDE 0.8.4 only.
- An unresolved type, supertype or redefinition target is detected by its placeholder target (a target with no owning relationship). That test was verified only on these shapes: a misspelled type, an unresolved supertype, an unresolved `:>>` on an input, an unresolved usage `:>>`, and a partial run whose definitions were not loaded (`tests/fixtures/positional_binding/unresolved/`, `tests/fixtures/positional_binding/partial_run/`, `tests/learning/test_syside_input_redefinition.py`). An unresolved reference of another shape could still read as clean.
- A finding whose owner or target has no qualified name (for example an anonymous `assert constraint`) cannot be pinned; name the owner or repair the binding.
- Validating a subfolder that does not contain the definitions it uses reports its owners as unverifiable, not clean.
- The check does not evaluate anything. It says where an input lands, not whether the value is wrong.

### Legacy pins (the pin list)

A project that already has positional mismatches can record them as legacy so they warn instead of block until they are migrated. A pin records a mismatch that existed at the revision the list was recorded against. **A new mismatch is repaired, not pinned**: bind it by name (`in :>> <formal> = ...`) or rename it deliberately (`in <name> redefines <formal> = ...`). Pinning a new mismatch is a disposition reserved to the project owner. Nothing generates or updates the list; it is written and reviewed by hand, and its integrity rests on that review.

A pinned finding's message carries this text, and it means what it says: "Pinned as legacy; this does not show that native values are correct or that the native and generated routes agree." The level 2 summary reports pinned warnings as their own count: "(N pinned positional warnings; not a value or route-parity check)".

**Format.** TOML, schema `positional-pins/v1`. Every key below is required; unknown keys, wrong types, duplicate identities, an absolute `file`, or `..` in `file` make the list invalid.

```toml
schema = "positional-pins/v1"

[recorded_against]
revision = "f96ad312c63e8c66695971b12feab971f3ba6eb3"   # the project revision the mismatches existed at
date = 2026-10-15

[[pin]]
owner = "aries_integrated_plant::heat_exchangers::evaluate"
input = "pbli_available_in"
target = "integrated_heat_electricity::'Network Heat Driven Closure'::divertor_available_in"
file = "models/designs/aries_cs_integrated/plant.sysml"
line = 270
```

Copy `owner`, `input`, `target`, `file` and `line` from the finding's message, which prints all five; copy them for legacy findings only. A pin matches on owner, input and target. `line` is kept for review.

**Where the list is found.**

- By default, `validate` finds the project root above the validated path (a folder holding `work/BACKLOG.md`, `.agentic-mbse/install.json` or `.claude/`) and reads only `<project root>/positional-pins.toml`. A file anywhere else is ignored; the `Positional pin list` metric prints the path it looked at.
- `--positional-pins FILE` names a list anywhere. `--positional-pins-root DIR` says which tree its `file` paths describe; without it they resolve against the list's own folder. `--positional-pins-root` without `--positional-pins` is a usage error.

**A pin's `file` matters for scope.** Matching ignores the file, so an owner moved to another file still matches. But on a run that validates only part of the tree, an unmatched pin whose file exists and was not validated is counted as out of scope, while one whose file was validated is stale. So an owner moved into an unvalidated file reads as a stale pin on a partial run. A pin whose owner or input failed inspection is not judged at all; the inspection failure is already the blocking error.

### Evidence and upstream

- Fixtures: `tests/fixtures/positional_binding/` (each file's header states its expected findings), run by `tests/test_validation/test_positional_binding.py`.
- Tree reproduction, including fusion-tea `f96ad312` (125 mismatches, value effect unknown) and two dc3 revisions (none): `.project/active/positional-binding-check/evidence/run-trees.md`.
- Native behavior pinned by learning tests: `tests/learning/test_syside_input_redefinition.py`.
- sysml-codegen records parser positional behavior in `sysml-codegen@b5663c07:tests/fixtures/modeled_default_fidelity/PROVENANCE.md` and tracks POSITIONAL-FORMAL-REDEFINITION in `sysml-codegen@b5663c07:.project/backlog/BACKLOG.md`.
- A draft finding for sysml-codegen about its by-name wiring (the -7 versus 7 above) is at `.project/active/positional-binding-check/evidence/upstream-codegen-finding.md`. **It is unfiled** until it is filed in sysml-codegen.

## Candidates, not yet reproduced

These are named as possible hazards. No reproduction has been retained for either, so this register makes no claim about their semantics yet.

- **Output override.** Overriding a calculation's result on a usage. Not yet reproduced.
- **`[*]` and `[0]` on one collection.** A named subset occurrence exposes both the library's `[*]` collection feature and the design's `[0]` redefinition. Not yet reproduced.
