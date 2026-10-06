# Current Work

**Last Updated**: 2026-10-05
**Checkout**: `research-approval-empty-insights`, branched from `main` at `c37ff53` after PR #15 merged.

[OWNER] Reports successful operation in Fusion TEA and requested reconciliation of tracking against actual remaining work. The [status report](reports/2026-10-04-0901-status-report.md#tracking-reconciliation--progress) carries investigation progress, evidence, and limits. This refresh updates local tracking; sibling repositories were inspected read-only.

## Current state

The September workflow repairs and harness right-sizing are implemented and installed in Fusion TEA. Focused trials and a bounded process review passed. Fusion TEA continued work through September 30 on `goal/magnet-material-comparison` (`97fabad31`). The old July constraint integration blockers are resolved by merged successor work; they are no longer active blockers.

## Active Work

- [research-approval-empty-insights](active/research-approval-empty-insights/spec.md) — standalone `PM-APPROVE-RESEARCH-EMPTY-INSIGHTS`; implemented on the branch 2026-10-05 per its [plan](active/research-approval-empty-insights/plan.md); certified 2026-10-05 by [audit](active/research-approval-empty-insights/audit.md) with no blockers and six advisories (A1: the `..` fix leaves the `KNOWLEDGE.md` and `approved/` paths unnormalized, a one-line fix); close next.
- [native-skill-distribution](active/native-skill-distribution/spec.md) — standalone `NATIVE-DISTRIBUTION-RECONCILIATION`; draft spec complete; product-lens CLEAR; owner review next.

## Concrete remaining work

| Work | Current status | Next action |
|------|----------------|-------------|
| L6 EXPOSE validation | Closed 2026-10-04: certified repair archived to [completed/20261004_l6-expose-consistency](completed/20261004_l6-expose-consistency/); fusion-tea consumer validation confirmed all spec criteria in situ | None for the item. Follow-ups filed in the [backlog](backlog/BACKLOG.md): `DOCS-DOTTED-PATH-BOUNDARY` (with deep-chain regression coverage), `VALIDATE-CLI-FULL-REPORT`, `L6-COMPLETENESS-PATH-FILTER`, `L6-FORMULA-COMPLETENESS`, `L6-EXPOSE-CLEANUPS`, `L6-LIBRARY-ALIAS-SOURCE` |
| Native skill distribution | Installed Fusion TEA workflows differ from the `native-claude-codex-skills` source; native installer remediation is uncommitted and awaits final verification | Reconcile source with consumer changes and finish installer verification before distributing that branch |
| PM registry integrity | Closed 2026-10-04: certified repair archived to [completed/20261004_pm-registry-integrity](completed/20261004_pm-registry-integrity/); merged to `main` in PR #15 (`c37ff53`) | fusion-tea's pin is at `c37ff53` (verified in its `pyproject.toml` 2026-10-05). Remaining there: escape the two raw pipes in its `SV-034` row by hand. Follow-ups filed in the [backlog](backlog/BACKLOG.md) at P3: `PM-DASHBOARD-REPEATED-KEY`, `PM-UPDATE-VALIDATION-COMMENT`, `PM-WRITE-BACKLOG-TYPED-FORM`, `PM-R7-MESSAGE` |
| Research approval | Implemented 2026-10-05 on `research-approval-empty-insights`: `--insights '[]'` approves and moves the document without touching `KNOWLEDGE.md`, and the shipped `/research` step tells agents to make that call | Certified 2026-10-05 ([audit](active/research-approval-empty-insights/audit.md), no blockers; advisories A1-A6). Next: close, then `/_my_pre_pr`; P2 |
| Extraction provenance | Machine-readable provenance and saved-raw-byte fidelity remain filed P2 work | Implement a scoped provenance contract; retain current downstream workarounds until then |

No implementation session is currently recorded as running in this checkout. Native implementation is in a sibling worktree; its residual distribution spec is tracked here; the retained local active folders are indexed in [active/README.md](active/README.md).

## Up next

[INHERITED: backlog/BACKLOG.md] No P0 items are recorded. Existing P1 priorities remain the PDF extraction epic (OCR integration outstanding) and PDF skill deployment/Docling MCP setup. The epic's near-empty-section summarization fix retains its explicit item-level P2 priority. OCR and summarization are ready backlog work; deployment needs design revision. These gaps do not establish a broken Fusion TEA modeling/study pipeline.

[AGENT] The registry ID-reuse defect is repaired, closed (2026-10-04), and merged in PR #15. Finish native source reconciliation when preparing a portable installation. This recommendation does not change recorded priorities.

## Reconciled dispositions

- Constraint-wave profile semantics, GAP-CLOSE local totalization/docs, and CONSTRAINT-EXEC remediation are implemented and integrated. Paired smoke and TEAx normalization evidence supersede the old merge/compatibility blockers. Historical item evidence remains in its existing folders.
- Harness right-sizing is complete within its recorded scope. Token savings remain unmeasured; that measurement is not an implementation blocker.
- Modeling workflow repairs/trials are complete. The older request for independent implementation certification is an unperformed broader check, not evidence of failed operation. September 14 right-sizing permits review scope to follow actual risk; its bounded review does not certify the native installer.
- Docling and Pandoc deep-dives were closed March 6; their remaining research phases are not active work. Iteration-loop is shelved in the backlog.
- Artifact scaffolding and C4 plain-subtype documentation/test work remain unimplemented drafts. FORMULA teaching is implemented. Command-refresh is an undecomposed July draft with substantial overlap with September work; its remaining scope needs reconciliation before execution.
