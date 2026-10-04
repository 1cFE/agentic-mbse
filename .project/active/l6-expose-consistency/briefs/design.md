# Brief: design — l6-expose-consistency

Work item: `.project/active/l6-expose-consistency/spec.md` (read it first; also read `product-lens.md` beside it).

## Intent (orchestrator reading of the spec; provenance marked)

[INHERITED: spec] Three L6 checks classify the same design-attribute expression. The static-expression check (`check_static_expressions`, `src/agentic_mbse/validation/adr002.py:563`) accepts a pure EXPOSE binding (`attribute x : Real = my_calc.output_val`) via `_is_expose_pattern` (`adr002.py:389`). Two other checks reject the same binding: the supported-operator check (`check_supported_operators`, `adr002.py:94`) reports `.` as an unsupported operator because `extract_operators` (`src/agentic_mbse/sysml/expression.py:98`) surfaces the feature-chain operator; and the design-attribute completeness check (`check_design_attr_completeness`, `src/agentic_mbse/validation/level6_architecture.py:475`) tries `evaluate_true_static_expression` on the binding and reports `L6_DESIGN_ATTR_UNEXTRACTABLE`. Both participate in the combined route `validate_architecture` (`level6_architecture.py:977`).

[AGENT, verified by orchestrator 2026-10-04] The spec's premise holds: sysml-codegen (`/home/reid/1cfe/sysml-codegen/src/sysml_codegen/resolution/models.py:243`, `OutputAlias`) handles EXPOSE_PURE in two shapes — shape A on a part definition, shape B on a part usage — by surfacing the calc output channel. A pure EXPOSE design attribute does not need a numeric default for codegen. The L6 completeness check is behind codegen, not ahead of it.

[AGENT] Goal: the three checks share one semantic classification of a design-attribute expression (true static / EXPOSE / FORMULA / derived) instead of each re-deriving policy. The repair is consistency, not new expression support.

## Decisions already taken (orchestrator, execution-detail tier; owner ratified "go" with no reserved gates)

- [AGENT] Scope stays on EXPOSE per the spec. The sibling FORMULA inconsistency (completeness check rejects `area = length * width`, which `check_static_expressions` accepts under F6; `tests/test_l8_extractability.py` asserts the rejection) is out of scope. Record it as a Non-Goal / follow-up with one line of reasoning, and shape the shared classifier so FORMULA could be added without restructuring. Do not change FORMULA behaviour or that test.
- [AGENT] Owner left the "shared extractor vs. V4-check-only" question to you. Decide it in the design with recorded reasoning. Consider: `extract_operators` is a shared utility with other callers; changing its contract has a wider blast radius than teaching the V4 check that an EXPOSE binding has no operators to check. Prefer the smallest change that makes policy live in one place.

## Constraints and facts to design against

- `_is_expose_pattern` requires a `FeatureChainExpression`, a first chain member resolving to a sibling `CalculationUsage` or `PartUsage` (same owner), and a single attribute/output target. That is the supported boundary; do not widen it. Specifically, do not admit an arbitrary dotted reference just because it contains `.`.
- The regression referent `tests/fixtures/adr002_violations/v2_expose_pattern.sysml` lives outside any `designs/` path, so `check_design_attr_completeness(design_path_filter="designs")` and the combined L6 route skip it today. The spec requires the fix to be proven through the combined L6 route in a checked design location, so the design must specify positive and negative control fixtures under a `designs/` path (and the `library/` calc def they need). Look at `tests/fixtures/l8_extractability/` for the existing layout convention.
- Controls the spec requires: unsupported operators still fire V4; absent design values still fire `L6_DESIGN_ATTR_INCOMPLETE`; unextractable static defaults still fire `L6_DESIGN_ATTR_UNEXTRACTABLE`; invalid reference targets (a chain whose first member does not resolve to a sibling calc/part usage) still fire; arithmetic over a calc output still fires `V2_DYNAMIC_EXPRESSION`.
- Both pure EXPOSE shapes must stay accepted: on a part definition and on a part usage (`docs/patterns/expose-pattern.md`).
- Non-goals (spec): new expression support, codegen behaviour, modeling-workflow changes.

## Quality bar

Clean, well-architected code: one place owns the "what kind of design expression is this" decision; checks consume it. No duplicated heuristics, no path-string hacks beyond what the existing checks already do. Tests run via `uv run pytest tests/`. Note any open question you cannot settle from the spec and this brief, and decide-and-record rather than leaving it open.

Produce `.project/active/l6-expose-consistency/design.md`.
