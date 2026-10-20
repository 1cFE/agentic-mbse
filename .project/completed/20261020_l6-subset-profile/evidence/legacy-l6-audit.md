# Legacy L6 check audit (EXEC-SUBSET-CONTRACT Item 3, Phase 8)

**Written:** 2026-10-19. **Sources:** design Appendix A; `spikes/f4-codegen-citations.md` (read at sysml-codegen `b5663c07` from a `git archive` export). Phase 8 re-read the six codegen sites it cites from a fresh export (`git get-tar-commit-id` = `b5663c07e987a892e27d21e68cec40d0656574ee`, extracted under `/tmp`); nothing ran in it and nothing was written in `~/src/sysml-codegen`. Codegen paths are relative to `src/sysml_codegen/` in that export. agentic-mbse lines are at this branch after Phase 7.

**What this decides.** Each of the 17 issue codes L6's legacy checks emit, plus manifest and setup failures, gets a category. The category and the execution target decide how the issue is shown (`src/agentic_mbse/validation/execution_target.py`, `LEGACY_CATEGORY` and `display()`):

- **own applicability:** an ADR-002 or project rule. Its own severity under every target.
- **kept:** its own severity under every target. Either native correctness, or a generator-only cause was not shown.
- **kept (follow-up):** kept, and the spike found it errors on shapes codegen `b5663c07` accepts. Whether to retire or reclassify it is backlog `L6-LEGACY-CHECKS-ON-ACCEPTED-SHAPES`, not this item.
- **generator-only:** the cause exists only in the generator. Its own severity under unset and `generated`; folded into the native INFO summary under `native`.

Under unset and `generated` no row changes severity. The one legacy relaxation in this item is the String case, done by suppression, not by category (design D10).

## Every legacy L6 code

| Code | What the check does | Today | Category | unset | generated | native | Evidence for the category |
|---|---|---|---|---|---|---|---|
| `V1_CALC_DEF_LOCATION` | A calc def in a `designs/` file instead of `library/` (`adr002.py` `check_calc_def_locations`) | ERROR | own applicability | ERROR | ERROR | ERROR | ADR-002 placement rule; not a generator check |
| `V2_DYNAMIC_EXPRESSION` | A design attribute whose value references design attributes, outside the EXPOSE and FORMULA exemptions (`check_static_expressions`) | ERROR | own applicability | ERROR | ERROR | ERROR | ADR-002 Rule 3 |
| `V4_UNSUPPORTED_OPERATOR` | A design attribute value using an operator outside `+ - * / [` (`check_supported_operators`) | ERROR | own applicability | ERROR | ERROR | ERROR | ADR-002 rule; codegen has no "V4" and renders `^` as `**` (`elaboration/project.py:795`) |
| `V4_STATIC_FUNCTION_INVOCATION` | A function call inside a static design expression (`check_static_function_invocations`) | WARNING | kept | WARNING | WARNING | WARNING | Partial: codegen refuses non-`sum` calls when it builds modules (`elaboration/project.py:806-810`) and accepts `sum`, which this check also flags |
| `L6_MISSING_QUALIFIED_NAME` | A calc def or calc usage with no qualified name (`check_qualified_names`) | ERROR | generator-only | ERROR | ERROR | INFO (summary) | Confirmed (weak): codegen's graph identity needs a qualified name (`elaboration/identity.py:71-76`, `IdentityBoundaryError`); a native route reads the element itself |
| `L6_INVALID_QUALIFIED_NAME` | A qualified name with an unquoted space, a leading `::` or `_`, or an empty segment (`check_qualified_names`) | ERROR | kept (follow-up) | ERROR | ERROR | ERROR | Not generator-only: codegen sanitizes every segment with agentic's `sanitize_name` (`core/qualified_names.py:10-17`) |
| `L6_CALC_DEF_NO_OUTPUT` | A calc def with no `out` or `return` parameter (`check_calc_def_structure`) | ERROR | kept | ERROR | ERROR | ERROR | Native correctness: a calc with no output computes nothing on any route |
| `L6_CALC_DEF_NO_DIRECTION` | A calc def parameter with no direction (`check_calc_def_structure`) | WARNING | kept | WARNING | WARNING | WARNING | Native correctness |
| `L6_INVALID_BINDING_FORMAT` | A calc usage binding whose resolved path uses the wrong separator (`check_binding_formats`) | ERROR | kept (follow-up) | ERROR | ERROR | ERROR | Not generator-only: codegen resolves bindings by element identity and reads no separator (`elaboration/elaborate.py:2130-2170`, `:2286-2355`) |
| `L6_DESIGN_ATTR_INCOMPLETE` | A design attribute with no value and no binding (`check_design_attr_completeness`) | ERROR | kept | ERROR | ERROR | ERROR | Not generator-only: codegen accepts a valueless input with no default (`elaboration/project.py:565-579`) |
| `L6_DESIGN_ATTR_UNEXTRACTABLE` (String value) | A design attribute whose String value the static evaluator cannot read | ERROR | replaced by the contract's `omitted` | WARNING | WARNING | INFO (summary) | Gate R3-1: suppressed by the contract's `string-value-omission` subject ids (design D10); the contract's finding takes its place |
| `L6_DESIGN_ATTR_UNEXTRACTABLE` (other value) | A design attribute whose value L6's static evaluator cannot reduce to a number | ERROR | kept | ERROR | ERROR | ERROR | Partial: codegen compiles references, `^` and `sum` (`elaboration/elaborate.py:978-1065`), which this check rejects |
| `L6_ANONYMOUS_RETURN` | A calc def whose `return` has no declared name (`check_anonymous_returns`) | ERROR | generator-only | ERROR | ERROR | INFO (summary) | Confirmed: codegen V8 refuses the whole run (`extraction/extractor.py:191-215`, REQ-EXT-11); SysIDE names the result `result`, so a native route has an output |
| `L6_BODY_ASSIGNMENT_IMPL_LOSS` | A named calc def output set by a body assignment (`check_body_assignment_impl_loss`) | WARNING | generator-only | WARNING | WARNING | INFO (summary) | Confirmed: codegen drops the body-assignment target as a parameter (`extraction/extractor.py:249-264`) and marks the output `MANUAL_REQUIRED`, "no expression AST" (`extraction/expression_compiler.py:265-274`) |
| `L6_CONSTRAINT_MALFORMED_NUMERICAL` | A constraint the shared executable profile blocks as malformed numerical (`check_constraint_executability`) | ERROR | kept | ERROR | ERROR | ERROR | Gate R3-1: keeps its severity and scope under every target |
| `L6_CONSTRAINT_NON_NUMERICAL` | A constraint the shared executable profile marks non-numerical (`check_constraint_executability`) | WARNING | kept | WARNING | WARNING | WARNING | The decision is agentic's shared executable profile, which codegen consumes (`elaboration/elaborate.py:296`); not codegen-specific |
| `L6_CALC_DEF_NO_INSTANTIATION` | A part def owning calc usages that no part usage instantiates, by simple name (`check_calc_bearing_instantiation`) | ERROR | generator-only | ERROR | ERROR | INFO (summary) | Confirmed: codegen gives such a calc no node (`elaboration/elaborate.py:771-777`, `owner_has_no_occurrences`). Caveat: a native route that evaluates instances has nothing to evaluate either. Simple-name collision noted below |
| `L6_ATTR_REDEF_EXPR_DROPPED` | An `attribute :>> x = <expr>` redefinition with a computed value (`check_attr_redef_expression_dropped`) | WARNING | kept (follow-up) | WARNING | WARNING | WARNING | Not generator-only: the codegen scan it described (`hierarchy_resolver`) is deleted (`tests/helpers/live_extraction.py:9-10`); the current scan treats both spellings alike (`elaboration/elaborate.py:832-898`) |
| Manifest failures | An unusable `designs/*/manifest.yaml`, or a subsystem it expects that the model lacks (`_check_manifests`) | fail | own applicability | fail | fail | fail | Project manifest rule |
| Setup failures | No models path, or the model fails to load | fail | own applicability | fail | fail | fail | L6 cannot run |

New in this item, outside this table: the contract's findings (severity by outcome and target, design "The severity table"), the two advisories (at most WARNING), and `L6_CHECK_ERROR` / `L6_SETTING_INVALID` (ERROR under every target).

## Lowered under native

Every severity `execution-target = "native"` lowers. This table, `tests/fixtures/l6/native_lowered.toml` and the `LEGACY_GENERATOR_ONLY` entries of `LEGACY_CATEGORY` must list the same codes; `tests/test_validation/test_execution_target.py::test_audit_lowered_table_matches_fixture` checks it.

| Code | Today | Under native | Why it is generator-only |
|---|---|---|---|
| `L6_MISSING_QUALIFIED_NAME` | ERROR | INFO (summary) | Codegen's graph identity needs a qualified name (`elaboration/identity.py:71-76`) |
| `L6_ANONYMOUS_RETURN` | ERROR | INFO (summary) | Codegen V8 (`extraction/extractor.py:191-215`) |
| `L6_CALC_DEF_NO_INSTANTIATION` | ERROR | INFO (summary) | Codegen builds no node for it (`elaboration/elaborate.py:771-777`) |
| `L6_BODY_ASSIGNMENT_IMPL_LOSS` | WARNING | INFO (summary) | Codegen loses auto-impl for it (`extraction/extractor.py:249-264`, `extraction/expression_compiler.py:265-274`) |

Totals: 3 ERROR → INFO and 1 WARNING → INFO. The spec proposed up to 7 and 4. The other candidate rows keep today's severity under `native`, because the spike did not show a generator-only cause for them.

## Notes

- **Simple-name collision in `L6_CALC_DEF_NO_INSTANTIATION`.** The check collects the simple names of every part usage's types and compares a part def's simple name against that set (`level6_architecture.py`, `check_calc_bearing_instantiation`). A part def that nobody instantiates is missed when another part def with the same simple name is instantiated. Codegen matches by declaration id (`occurrences_for_type(owner_id)`), so it has no such gap. Not fixed here (spec non-goal); recorded so a reader does not trust the check's silence.
- **Kept (follow-up) rows** (`L6_INVALID_QUALIFIED_NAME`, `L6_INVALID_BINDING_FORMAT`, `L6_ATTR_REDEF_EXPR_DROPPED`) error or warn on shapes codegen `b5663c07` accepts. They stay unchanged under every target; backlog `L6-LEGACY-CHECKS-ON-ACCEPTED-SHAPES` decides each.
- **Not checked:** every verdict about codegen comes from reading code, not running it (inherited from the spike). Whether `IdentityBoundaryError` surfaces for every missing-name site was not traced.
