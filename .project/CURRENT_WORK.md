# Current Work

**Last Updated**: 2026-10-04
**Checkout**: `harness-right-size` at `ce80472`; three commits beyond local `main` (`88e2489`).

[OWNER] Reports successful operation in Fusion TEA and requested reconciliation of tracking against actual remaining work. The [status report](reports/2026-10-04-0901-status-report.md#tracking-reconciliation--progress) carries investigation progress, evidence, and limits. This refresh updates local tracking; sibling repositories were inspected read-only.

## Current state

The September workflow repairs and harness right-sizing are implemented and installed in Fusion TEA. Focused trials and a bounded process review passed. Fusion TEA continued work through September 30 on `goal/magnet-material-comparison` (`97fabad31`). The old July constraint integration blockers are resolved by merged successor work; they are no longer active blockers.

## Active Work

- [pm-registry-integrity](active/pm-registry-integrity/spec.md) — standalone `PM-MATRIX-ESCAPED-PIPE`; draft spec complete; product-lens CLEAR; owner review next.
- [research-approval-empty-insights](active/research-approval-empty-insights/spec.md) — standalone `PM-APPROVE-RESEARCH-EMPTY-INSIGHTS`; draft spec complete; product-lens CLEAR; owner review next.
- [native-skill-distribution](active/native-skill-distribution/spec.md) — standalone `NATIVE-DISTRIBUTION-RECONCILIATION`; draft spec complete; product-lens CLEAR; owner review next.

## Concrete remaining work

| Work | Current status | Next action |
|------|----------------|-------------|
| L6 EXPOSE validation | Closed 2026-10-04: certified repair archived to [completed/20261004_l6-expose-consistency](completed/20261004_l6-expose-consistency/); fusion-tea consumer validation confirmed all spec criteria in situ | None for the item. Follow-ups filed in the [backlog](backlog/BACKLOG.md): `DOCS-DOTTED-PATH-BOUNDARY` (with deep-chain regression coverage), `VALIDATE-CLI-FULL-REPORT`, `L6-COMPLETENESS-PATH-FILTER`, `L6-FORMULA-COMPLETENESS`, `L6-EXPOSE-CLEANUPS`, `L6-LIBRARY-ALIAS-SOURCE` |
| Native skill distribution | Installed Fusion TEA workflows differ from the `native-claude-codex-skills` source; native installer remediation is uncommitted and awaits final verification | Reconcile source with consumer changes and finish installer verification before distributing that branch |
| PM registry integrity | Escaped-pipe rows disappear; `add-validation` freshly reproduced reuse of `SV-034` | Fix escaped-pipe splitting and protect ID allocation against malformed rows; tracked P2 |
| Research approval | Explicit empty insight list freshly reproduced refusal to approve/move the document | Support approval with zero new insights; tracked P2 |
| Extraction provenance | Machine-readable provenance and saved-raw-byte fidelity remain filed P2 work | Implement a scoped provenance contract; retain current downstream workarounds until then |

No implementation session is currently recorded as running in this checkout. Native implementation is in a sibling worktree; its residual distribution spec is tracked here; the retained local active folders are indexed in [active/README.md](active/README.md).

## Up next

[INHERITED: backlog/BACKLOG.md] No P0 items are recorded. Existing P1 priorities remain the PDF extraction epic (OCR integration outstanding) and PDF skill deployment/Docling MCP setup. The epic's near-empty-section summarization fix retains its explicit item-level P2 priority. OCR and summarization are ready backlog work; deployment needs design revision. These gaps do not establish a broken Fusion TEA modeling/study pipeline.

[AGENT] Assess the reproduced registry ID-reuse defect before a broader workflow change. Finish native source reconciliation when preparing a portable installation. This recommendation does not change recorded priorities.

## Reconciled dispositions

- Constraint-wave profile semantics, GAP-CLOSE local totalization/docs, and CONSTRAINT-EXEC remediation are implemented and integrated. Paired smoke and TEAx normalization evidence supersede the old merge/compatibility blockers. Historical item evidence remains in its existing folders.
- Harness right-sizing is complete within its recorded scope. Token savings remain unmeasured; that measurement is not an implementation blocker.
- Modeling workflow repairs/trials are complete. The older request for independent implementation certification is an unperformed broader check, not evidence of failed operation. September 14 right-sizing permits review scope to follow actual risk; its bounded review does not certify the native installer.
- Docling and Pandoc deep-dives were closed March 6; their remaining research phases are not active work. Iteration-loop is shelved in the backlog.
- Artifact scaffolding and C4 plain-subtype documentation/test work remain unimplemented drafts. FORMULA teaching is implemented. Command-refresh is an undecomposed July draft with substantial overlap with September work; its remaining scope needs reconciliation before execution.
