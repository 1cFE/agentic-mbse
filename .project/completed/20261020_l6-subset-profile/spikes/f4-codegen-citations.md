# F4: Appendix A codegen citations checked against sysml-codegen `b5663c07`

Read-only. sysml-codegen was exported with `git -C ~/src/sysml-codegen archive b5663c07 > /tmp/l6-spike-codegen.tar` (`git get-tar-commit-id` → `b5663c07e987a892e27d21e68cec40d0656574ee`), extracted with `tarfile`'s `data` filter and absolute symlinks skipped, into `/tmp/l6-spike-codegen`. Nothing was run in it. Codegen paths below are relative to `src/sysml_codegen/` in the export unless they start with `tests/`. agentic-mbse lines are at `00e2b202`.

The reading was done by a subagent. Four claims were spot-checked by hand: V8 at `extraction/extractor.py:191-215`, the `sum`-only refusal at `elaboration/project.py:806-810`, the deletion note at `tests/helpers/live_extraction.py:9-10`, and the absence of any `V4` in `src/sysml_codegen`.

## Main finding

Codegen at `b5663c07` builds an instance graph (`elaboration/elaborate.py`) and turns it into modules (`elaboration/project.py`). Its only entry is `run_codegen` (`cli/__init__.py:1144`). The old extractors that several agentic-mbse comments cite (`hierarchy_resolver`, `usage_extractor`, `computed_attribute_extractor.py`) have been deleted. So several "generator-only" causes in Appendix A describe a generator that no longer exists.

## Rows (Appendix A, "generator-only if shown" and the two "kept unless shown")

| Row | Verdict | Codegen site at `b5663c07` | Reasoning |
|---|---|---|---|
| `V4_STATIC_FUNCTION_INVOCATION` | PARTIAL | `elaboration/project.py:806-810` (`function_qn != ["NumericalFunctions", "sum"]` → `_fail(... "unsupported invocation survived ...")`) | Codegen has no "static default" step. A non-literal design value becomes a computed node (`elaborate.py:1016-1065`). Calls other than `sum` are refused when modules are built; `sum` is accepted and rendered (`project.py:806-815`). The cause holds for `sqrt`-like calls and is false for `sum`. The boundary fixture's claim (`sum` fires V4 and no contract finding) is consistent with this. |
| `L6_MISSING_QUALIFIED_NAME` | CONFIRMED (weak) | `elaboration/identity.py:71-76` (`IdentityBoundaryError`: no reload-stable qualified declaration identity); `elaborate.py:737` skips null-name features | Codegen needs a qualified name for stable graph identity, not for EQN or ADR-001. Depending on the site, a missing name raises or is skipped without a message. |
| `L6_INVALID_QUALIFIED_NAME` | NOT generator-only | `core/qualified_names.py:10-17` re-exports agentic's `sanitize_name` (`agentic_mbse/sysml/qualified_names.py:20-37`) | Codegen never refuses a space, a leading `_` or `::`. It sanitizes each segment. The related failure is a collision after sanitizing (`project.py:214`, `:364`, `:387` `SI_RENDERING_COLLISION`; `cli/__init__.py:196-230` `DUPLICATE_OUTPUT_PATH`), which this check does not test. |
| `L6_INVALID_BINDING_FORMAT` | NOT generator-only | `elaborate.py:2130-2170` (`_binding_evidence`), `:2286-2355` (`_resolve_semantic_reference`) | Bindings are resolved by element identity. No codegen code reads `::` or `.` in binding text. |
| `L6_DESIGN_ATTR_UNEXTRACTABLE` (other) | PARTIAL | `elaborate.py:978-1065`; `project.py:794-822`; refusals at `project.py:806-810` and `:817-821` | Codegen no longer needs a numeric default. It compiles operators (including `^` as `**`), sibling and chain references, calc outputs and `sum`. Only non-`sum` calls and unsupported IR are refused. The legacy static evaluator rejects all references and `^`, so this check fires on shapes codegen accepts. Not checked: which of those reach the check after V2's FORMULA exemption. |
| `L6_ANONYMOUS_RETURN` | CONFIRMED | `extraction/extractor.py:191-215` (`# REQ-EXT-11 (V8)` … `ExactExtractionError` "anonymous `return` … no output channel") | Runs over every calc def (`extractor.py:77-88`), used or not, so one anonymous return refuses the whole run. |
| `L6_BODY_ASSIGNMENT_IMPL_LOSS` | CONFIRMED | `extractor.py:249-264` (body-assignment target dropped); `:138-144` (only an inline output expression kept); `extraction/expression_compiler.py:265-274` (`no expression AST` → `MANUAL_REQUIRED`); `elaborate.py:1701-1702` | Output channel survives, auto-impl is lost, as claimed. |
| `L6_CALC_DEF_NO_INSTANTIATION` | CONFIRMED, with a caveat | `elaborate.py:771-777` (`"owner_has_no_occurrences"`); `:1195-1199`, `:1219-1227` (no node per scope) | A calc usage in a never-instantiated part def gets no node, silently. Caveat: any instance-evaluating native route would also have nothing to evaluate, so "generator-only" is arguable. Codegen matches owners by declaration id (`occurrences_for_type(owner_id)`), so it has no simple-name collision; the agentic check matches by simple name (`level6_architecture.py:716-721`) and can miss an uninstantiated def masked by a same-named one. |
| `L6_ATTR_REDEF_EXPR_DROPPED` | NOT generator-only; cited code deleted | `tests/helpers/live_extraction.py:9-10` (`hierarchy_resolver` deleted); current scan `elaborate.py:832-898` | The current scan takes every `Feature` subtype with a qualified name and a redefinition value (`elaborate.py:833-838`, `:888-895`), so `attribute :>> x = expr` and `:>> x = expr` are treated alike. Unverified risk: if a redefinition member has no qualified name, `elaborate.py:838` drops both forms. |
| `L6_DESIGN_ATTR_INCOMPLETE` (kept) | NOT generator-only | `project.py:565-579` (`ValueSite.NONE` → `EntryPointType.DESIGN_ATTRIBUTE`, `default_value=None`) | Codegen accepts a valueless design attribute as an input with no default. |
| `L6_CONSTRAINT_NON_NUMERICAL` (kept) | Codegen excludes it; decision is agentic's | `elaborate.py:296` (`NON_NUMERICAL → ("excluded", "non_numerical")`); `project.py:1228-1233` | True that it will not execute in codegen, but the decision comes from agentic's shared executable profile, so it is not codegen-specific. |

## Codegen citations inside agentic-mbse L6 code

| Citation (agentic `00e2b202`) | Accurate at `b5663c07`? | Correct site |
|---|---|---|
| `adr002.py:38` "matching codegen V4" | No. No `V4` exists in codegen (only V7, V8, V11). | `project.py:806-810` for calls; `^` is accepted (`project.py:795`). |
| `adr002.py:189-191` "codegen cannot evaluate them at design scope … codegen V4's steer-to-calc-def guidance" | Partly: true for non-`sum` calls; no V4 guidance exists. | `project.py:806-815` |
| `adr002.py:456` "FORMULA compiler rejects any FeatureChainExpression" | No, stale. Chains resolve at `elaborate.py:2286-2355`. The surviving chain refusal is for calc def outputs. | `extraction/calc_compat_renderer.py:102-103` |
| `adr002.py:468-483` `_classify_attribute_expression` (`computed_attribute_extractor.py`), "foreign … must STILL fire" | No. File deleted (`tests/conformance/test_register_contract.py:172-181` pins its absence). Calc-output references are supported through producer edges (`elaborate.py:2296-2311`). | `elaboration/expression_evidence.py:333-347` |
| `adr002.py:500` "Self-reference → codegen drops it (REQ-CA-07)" | REQ-CA-07 not found. Most likely fails as a cycle, not dropped. Not checked exactly. | `elaboration/graph.py:865-910` (probable) |
| `adr002.py:517`, `:589`, `level6_architecture.py:166` "Item 5" / "Item-5 sanitization" | Project-history labels; the sanitizer lives in agentic. | `agentic_mbse/sysml/qualified_names.py:20-37` |
| `level6_architecture.py:533` "Codegen wires the alias to its source" | Yes. | `elaborate.py:982-1012` |
| `level6_architecture.py:547` "codegen cannot extract a numeric default" | No (see UNEXTRACTABLE row). | n/a |
| `level6_architecture.py:583-584`, `:613` "codegen's V8", "no output channel" | Yes. | `extraction/extractor.py:191-215` |
| `level6_architecture.py:771` "loses auto-impl … deferred-capture" | Behaviour yes; "deferred-capture" is not a codegen name. | `expression_compiler.py:265-274`, `extractor.py:249-264` |
| `level6_architecture.py:847`, `:895` `hierarchy_resolver._extract_single_redefinition` "scans only ReferenceUsage" | No, stale; module deleted. | `elaborate.py:832-898` |
| `common.py:82` "Reuses pattern from test_sysml_parsing.py:82-100" | Not a codegen citation; the file exists in neither repo. | none (design already deletes it) |

## Not checked

- Nothing was run; every verdict is from reading code.
- All places `IdentityBoundaryError` is raised and where it surfaces.
- The `function_qn` codegen sees for `sqrt`, and for `sum` reached through a wrapper.
- Whether redefinition members have a qualified name in SysIDE 0.8.4.
- The self-reference cycle path, and where `project.py:806`'s refusal surfaces to the user.
- Codegen imports agentic's expression IR through an editable path (`>=0.1.3`); the agentic copy read was HEAD, which may differ from what codegen used at `b5663c07`.
