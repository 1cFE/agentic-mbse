# Subtype-Aware Enumeration Decision Table (PIPELINE-TRUTH Item 4)

`SysideAdapter.elements_of_type(model, kind)` matches `kind` **exactly** and never its subtypes;
`is_instance` on the same adapter *is* hierarchy-aware. That asymmetry silently blinds every
model-wide enumeration to the subtypes of the type it queries. `elements_of_type(...,
include_subtypes=True)` opts into the subtype sweep; `exclude=EXCLUDED_CONSTRAINT_TYPES` subtracts
the requirement-side usages. The default stays `include_subtypes=False` — this is **opt-in per call
site**, recorded here so each choice is deliberate.

Every `elements_of_type` / `is_instance` type name resolves through the adapter's `TYPE_MAP`; an
unmapped name **raises `ValueError`** rather than silently no-opping (D6/INV-F).

Droppability is single-sourced (INV-D): `is_droppable_constraint(elem)` / `EXCLUDED_CONSTRAINT_TYPES
= ("RequirementUsage",)` in `syside_adapter.py`. Both repos consume it.

| # | Repo | Call site | Base type | Decision | Rationale |
|---|------|-----------|-----------|----------|-----------|
| 1 | codegen | `extractor.py` `report_dropped_constraints` / `collect_constraint_manifest` | `ConstraintUsage` | **include_subtypes=True, EXCLUDE `RequirementUsage`** | `assert` (`AssertConstraintUsage`) and `require`/plain are dropped predicates; `RequirementUsage` + its `satisfy` subtype are requirement-side |
| 2 | codegen | `constraint_extractor.py` `extract_all_constraints` | `ConstraintUsage` | **DELETED** | zero callers, false docstring — removed with Item 4 |
| 3 | codegen | `parameter_groups.py` design-attr sweep | `AttributeUsage` | **KEEP exact-type (opt-OUT)** | an `EnumerationUsage` entry point needs non-float EP typing (Item 5); flipping now would mint mistyped EPs |
| 4 | codegen | `Part*/Calc*` def/usage sweeps | those | **KEEP exact-type (opt-OUT)** | no supported model produces connection/interface/view/case/analysis subtypes (Out of Scope) |
| 5 | agentic-mbse | `level3_dataflow.py` import sweep | `Import` (abstract) | **include_subtypes=True** + fix the `imported_membership` guard + re-key the graph by importing package | abstract-type query matched zero → dep graph always `{}` → circular check structurally always passed |
| 6 | agentic-mbse | `level4_constraints.py` constraint sweep | `ConstraintUsage` | **include_subtypes=True, EXCLUDE `RequirementUsage`** (mirror row 1) | undercounted asserts |
| 7 | agentic-mbse | `level6_architecture.py` non-executable assert WARN | `ConstraintUsage` | **include_subtypes=True, EXCLUDE `RequirementUsage`** (mirror row 1) + remove the `except: constraints = []` swallow (D7) | assert constraints never received the WARN; the swallow masked the fix |
| 8 | agentic-mbse | the `AttributeUsage` enum sites | `AttributeUsage` | **KEEP exact-type (opt-OUT)** (mirror row 3) | same enum reasoning; keep the two repos aligned |

**Satisfy note (deliberate exclusion).** `SatisfyRequirementUsage` is a `RequirementUsage` subtype,
so the `RequirementUsage` exclusion drops `satisfy` assertions too. This is accepted: no supported
model uses `satisfy`, it is semantically requirement-side, and the report's scanned/excluded counts
keep a swept-and-excluded `satisfy` observable rather than silent. Revisit when a supported model
asserts via `satisfy`.

**Kinds & folding.** `require`/`assume` constraints are plain `ConstraintUsage`s (the require/assume
flag lives on the `RequirementConstraintMembership`, not a distinct usage type), so they fold to the
`PLAIN` kind — a documented v2 limitation, revisited by the constraint-execution epic.
