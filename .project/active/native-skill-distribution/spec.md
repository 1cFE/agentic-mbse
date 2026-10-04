# Spec: Native Skill Source Distribution Reconciliation

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-10-04 09:28 PDT
**Complexity:** MEDIUM
**Branch:** harness-right-size
**Backlog Item:** NATIVE-DISTRIBUTION-RECONCILIATION

## Problem

[INHERITED: ../../reports/2026-10-04-0901-status-report.md] Fusion TEA operates with native instructions adapted from September toolkit workflow changes and later consumer edits, while the native source branch remains at `955295b` with uncommitted installer remediation. Sixteen source bundles differ from the installed consumer. A distribution built from the older source cannot reproduce the working portable workflow behavior; accepting its older payloads during reinstall can restore older orchestration and validation procedures. Ownership handling can preserve modified files, so overwrite is not unconditional.

The existing native migration already has provenance-graded requirements in the sibling `native-skills/plan.md`; it is not being respecified. This item covers the later source/consumer reconciliation and distributable verification gap. It is tracked here so the current repository's backlog has one durable contract for that residual work.

## Success Criteria

- [ ] [INFERRED] Each of the sixteen observed bundle differences has a recorded disposition: portable toolkit behavior carried into native source, a target-owned customization retained in the consumer, or an intentional source difference with its reason. No unresolved difference can silently restore obsolete toolkit workflow behavior on an accepted update.
- [ ] [INHERITED: ../harness-right-size/requirements.md] A clean native installation exposes the reconciled portable workflow behavior, including brief/skippable stages when responsibilities are already met, scoped delegation, and independent review sized to source/math, design, and shared-consumer risk.
- [ ] [INHERITED: sibling native-skills/plan.md] Source, packaged resources, and a fresh installed target agree within native runtime adaptation. Native workflow/role discovery and supporting-resource access work for the existing Claude/Codex selections; reinitialization preserves ownership decisions and does not write through destination symlinks.
- [ ] [INFERRED] The already implemented A–K installer remediations have current verification and an independent disposition of the original findings before the reconciled source is described as ready for distribution. Existing consumer studies are supporting operation evidence, not a substitute for installer verification.
- [ ] [INFERRED] Installing or updating the reconciled instruction pack preserves the consumer's protected project files and executable-runtime pins; verification records identify which instruction and runtime sources were exercised.

## Known Requirements

- **[INHERITED]** The native migration's requirement-bearing plan, accepted-remediation record, and original audit remain the contract/evidence for installer behavior. Their provenance grades remain unchanged. Source: `/home/reid/1cfe/agentic-mbse-native-skills/.project/active/native-skills/{plan,remediation,audit}.md`.
- **[INHERITED]** Process simplification must protect other model instances, modeling design quality, and source/math fidelity. Source: `../harness-right-size/requirements.md`.
- **[INFERRED]** Reconciliation selects portable consumer changes rather than copying Fusion TEA's entire instruction tree; consumer-specific goal/study procedures remain owned by the target project.

## Non-Goals

- A second native migration, new workflow names or platform/runtime support, executable-model/runtime upgrades, or reproduction of Fusion TEA's full study suite.

## Open Questions / Deferred to design

- Inventory and classify the sixteen differences against current consumer state before deciding the exact portable payload. Newer Fusion TEA edits may alter that inventory; sixteen is the observed reconciliation baseline, not a permanent bundle count.
- Choose the source/worktree integration and packaging approach, while preserving uncommitted installer remediation and existing consumer ownership decisions.
- Reconcile the native plan's older inferred fresh-stage-context rule with September author continuity and risk-based review. The current harness requirements are the scope for portable workflow reconciliation; the conflicting older procedure must not be silently reinstated.
- Set a bounded verification/re-review scope that covers installer repairs, source/package/install parity, protected files, and representative native operation; do not infer statistical token savings or cross-platform certification from existing evidence.

## Related Artifacts

- **Backlog:** [NATIVE-DISTRIBUTION-RECONCILIATION](../../backlog/BACKLOG.md).
- **Evidence:** [October 4 reconciliation](../../reports/2026-10-04-0901-status-report.md#what-is-actually-broken-or-missing).
- **Existing migration contract:** [Native requirements and plan](/home/reid/1cfe/agentic-mbse-native-skills/.project/active/native-skills/plan.md).
- **Existing remediation:** [Accepted fixes](/home/reid/1cfe/agentic-mbse-native-skills/.project/active/native-skills/remediation.md) and [original audit](/home/reid/1cfe/agentic-mbse-native-skills/.project/active/native-skills/audit.md).
- **Current process:** [Harness requirements](../harness-right-size/requirements.md) and [workflow repair record](../modeling-workflow-outcomes/draft.md).
- **Consumer report:** [Fusion TEA harness report](/home/reid/1cfe/fusion-tea/.project/active/harness-right-size/report.md).
- **Product lens:** [Review ledger](product-lens.md).

**Next Steps:** Review this draft, then use `$my-design` to select portable changes and sequence native distribution verification.
