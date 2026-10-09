# Current Work

**Last Updated**: 2026-10-09
**Checkout**: `wrap-split`, branched from `main` at `8f43a09` after PR #16 merged. Holds the `WRAP-SPLIT` epic's planning artifacts.

[OWNER] Reports successful operation in Fusion TEA and requested reconciliation of tracking against actual remaining work. The [status report](reports/2026-10-04-0901-status-report.md#tracking-reconciliation--progress) carries investigation progress, evidence, and limits. This refresh updates local tracking; sibling repositories were inspected read-only.

## Current state

The September workflow repairs and harness right-sizing are implemented and installed in Fusion TEA. Focused trials and a bounded process review passed. Fusion TEA continued work through September 30 on `goal/magnet-material-comparison` (`97fabad31`). The old July constraint integration blockers are resolved by merged successor work; they are no longer active blockers.

## Active Work

- [WRAP-SPLIT epic](backlog/epic_wrap-split.md) — wrap the agentic-mbse / fusion-tea split; five items, ~10 days; product-lens CLEAR. Research audit: [wrap-split audit](research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md).
- [native-skill-distribution](active/native-skill-distribution/spec.md) — `NATIVE-DISTRIBUTION-RECONCILIATION`, adopted as `WRAP-SPLIT` Item 1; spec rewritten to the epic's Item 1 scope 2026-10-09, reviewed (Revise), and revised the same day with the review's resolutions and the Align decisions; effort now 2 days. Designed and planned; implementing on `nsd-integration` in worktree `/home/reid/1cfe/agentic-mbse-nsd`: Phases 1–5 of 8 done 2026-10-09 (merge, shipped text regenerated from `main` `06ac41d`, `claude/` removed, the tree is the only inventory, legacy links adopted, adapters' agent rule fixed); next Phase 6 (content and catalog evidence). Open owner question: the wheel has never packaged `docs/syside/python/v0.8.4/syside/` (strict xfail in `tests/test_packaged_guidance_contract.py`). One owner question parked: which install mode (`init` or `init --dev`) fusion-tea's post-merge step uses. First on the epic's critical path.
- [research-seam-port](active/research-seam-port/spec.md) — `WRAP-SPLIT` Item 5: port fusion-tea's research acquisition seam (the `research-acquire` skill plus an `agentic-mbse research` CLI) and rework `/manage-sources` to follow the registry's rules. Spec drafted 2026-10-08/09; design page approved by owner 2026-10-09 ([page](mental-alignment-v2/runs/20261006-150340_research-process-end-state_fresh.html)); product-lens CLEAR. Next: `/_my_spec_review` in a fresh session. One owner question open: may a goal delegate insight approval (does not affect Item 5's code).

## Concrete remaining work

| Work | Current status | Next action |
|------|----------------|-------------|
| L6 EXPOSE validation | Closed 2026-10-04: certified repair archived to [completed/20261004_l6-expose-consistency](completed/20261004_l6-expose-consistency/); fusion-tea consumer validation confirmed all spec criteria in situ | None for the item. Follow-ups filed in the [backlog](backlog/BACKLOG.md): `DOCS-DOTTED-PATH-BOUNDARY` (with deep-chain regression coverage), `VALIDATE-CLI-FULL-REPORT`, `L6-COMPLETENESS-PATH-FILTER`, `L6-FORMULA-COMPLETENESS`, `L6-EXPOSE-CLEANUPS`, `L6-LIBRARY-ALIAS-SOURCE` |
| Native skill distribution | Installed Fusion TEA workflows differ from the `native-claude-codex-skills` source; native installer remediation is uncommitted and awaits final verification | Now `WRAP-SPLIT` Item 1: reconcile source with `main`'s content and finish installer verification; Items 2, 4 and 5 register on the reconciled layout |
| PM registry integrity | Closed 2026-10-04: certified repair archived to [completed/20261004_pm-registry-integrity](completed/20261004_pm-registry-integrity/); merged to `main` in PR #15 (`c37ff53`) | fusion-tea's pin is at `c37ff53` (verified in its `pyproject.toml` 2026-10-05). Remaining there: escape the two raw pipes in its `SV-034` row by hand. Follow-ups filed in the [backlog](backlog/BACKLOG.md) at P3: `PM-DASHBOARD-REPEATED-KEY`, `PM-UPDATE-VALIDATION-COMMENT`, `PM-WRITE-BACKLOG-TYPED-FORM`, `PM-R7-MESSAGE` |
| Research approval | Closed 2026-10-06: certified repair archived to [completed/20261006_research-approval-empty-insights](completed/20261006_research-approval-empty-insights/) and merged to `main` in PR #16 (`8f43a09`). `--insights '[]'` approves and moves the document without touching `KNOWLEDGE.md`, and the shipped `/research` step tells agents to make that call | fusion-tea's pin is still at `c37ff53` (verified 2026-10-09): move it and re-run init to pick up the `/research` text. Follow-up filed in the [backlog](backlog/BACKLOG.md) at P3: `PM-APPROVE-RESEARCH-MOVE-SAFETY` |
| Extraction provenance | Machine-readable provenance and saved-raw-byte fidelity remain filed P2 work | Implement a scoped provenance contract; retain current downstream workarounds until then |

No implementation session is currently recorded as running in this checkout. Native implementation is in a sibling worktree; its residual distribution spec is tracked here; the retained local active folders are indexed in [active/README.md](active/README.md).

## Up next

[INHERITED: backlog/BACKLOG.md] No P0 items are recorded. Existing P1 priorities remain the PDF extraction epic (OCR integration outstanding) and PDF skill deployment/Docling MCP setup. The epic's near-empty-section summarization fix retains its explicit item-level P2 priority. OCR and summarization are ready backlog work; deployment needs design revision. These gaps do not establish a broken Fusion TEA modeling/study pipeline.

[AGENT] The registry ID-reuse defect is repaired, closed (2026-10-04), and merged in PR #15. The `WRAP-SPLIT` epic (P1) is the active planning thread: Item 1 (native source reconciliation) unblocks Items 2, 4 and 5; Item 3 runs in parallel in sysml-codegen. This recommendation does not change recorded priorities.

## Reconciled dispositions

- Constraint-wave profile semantics, GAP-CLOSE local totalization/docs, and CONSTRAINT-EXEC remediation are implemented and integrated. Paired smoke and TEAx normalization evidence supersede the old merge/compatibility blockers. Historical item evidence remains in its existing folders.
- Harness right-sizing is complete within its recorded scope. Token savings remain unmeasured; that measurement is not an implementation blocker.
- Modeling workflow repairs/trials are complete. The older request for independent implementation certification is an unperformed broader check, not evidence of failed operation. September 14 right-sizing permits review scope to follow actual risk; its bounded review does not certify the native installer.
- Docling and Pandoc deep-dives were closed March 6; their remaining research phases are not active work. Iteration-loop is shelved in the backlog.
- Artifact scaffolding and C4 plain-subtype documentation/test work remain unimplemented drafts. FORMULA teaching is implemented. Command-refresh is an undecomposed July draft with substantial overlap with September work; its remaining scope needs reconciliation before execution.
