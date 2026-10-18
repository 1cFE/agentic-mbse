# Smoke probes re-run after the Phase 3 edit

Plan Phase 3, Manual (P-9). The four Phase 1 smoke probes were re-run with `probe.py run --all --agentic-rev 83f48525` (the commit that moves the allowlist and adds `invocation_uses`) and compared with the committed Phase 1 observations (agentic-mbse `0ac48bc0`). Paths under the temp tree are normalized before comparing. The committed `observation.json` files are unchanged; this file is the record of the re-run.

| Probe | Certifies | Fields that differ |
|---|---|---|
| `binding-source__expression_source__owner_instantiated` | True | `identity.agentic_rev` |
| `conditional-expression__conditional_unresolved_branch__calc_definition_feature_value` | True | `identity.agentic_rev` |
| `invocation-callable__explicit_operator__attribute_value` | True | `identity.agentic_rev` |
| `string-value-omission__string_value__attribute_value__redefinition_shorthand` | True | `identity.agentic_rev` |

**Result:** every field except the agentic-mbse revision is identical: exit code, `ERROR:` lines, generated file list and hashes, catalog names, mentions and certification.
