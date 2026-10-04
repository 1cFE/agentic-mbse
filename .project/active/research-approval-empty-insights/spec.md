# Spec: Approve Research with No New Insights

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-10-04 09:28 PDT
**Complexity:** LOW
**Branch:** harness-right-size
**Backlog Item:** PM-APPROVE-RESEARCH-EMPTY-INSIGHTS

## Problem

[INHERITED: ../../backlog/BACKLOG.md, PM-APPROVE-RESEARCH-EMPTY-INSIGHTS] Research can be approved without producing a new domain insight, such as a source-registration round, a bounded negative result, or confirmation of existing knowledge. The public PM operation rejects an explicit empty insight list with `No insights provided`, leaving the document in `knowledge/research/pending/`. Operators must move approved research by hand, bypassing the supported approval operation.

## Success Criteria

- [ ] [INHERITED: ../../backlog/BACKLOG.md, PM-APPROVE-RESEARCH-EMPTY-INSIGHTS] `approve-research` with explicit `--insights '[]'` succeeds, moves the existing valid pending document to `knowledge/research/approved/`, creates no DI entries or IDs, and leaves the knowledge registry unchanged. The direct Python operation has the same behavior.
- [ ] [INHERITED: ../../backlog/BACKLOG.md, PM-APPROVE-RESEARCH-EMPTY-INSIGHTS] Omitting `--insights` remains a caller error; explicit emptiness is distinct from malformed JSON or an invalid insight payload.
- [ ] [INFERRED] Non-empty approval retains its current insight creation behavior. Existing missing-file and pending-location validation still rejects invalid requests without moving research or mutating knowledge.
- [ ] [INFERRED] The operation's result and CLI guidance accurately describe a zero-insight approval, including changed files and assigned IDs; they do not claim knowledge was modified when it was untouched.

## Known Requirements

- **[INHERITED]** This changes which approved research outcomes the operation accepts; the existing user approval gate remains. Source: `claude/commands/research.md:65` and the historical PM operations spec's approve-research contract.

## Non-Goals

- Changing research curation, automatically approving a document, or repairing the separate registry ID-allocation defect.

## Open Questions / Deferred to design

- Exact success-message wording and whether command instructions need a short clarification for explicit zero-insight approval.
- Approved-destination collisions and broader transactional/file-move behavior keep their current semantics; any defect discovered there should be surfaced separately rather than silently widening this repair.

## Related Artifacts

- **Backlog:** [PM-APPROVE-RESEARCH-EMPTY-INSIGHTS](../../backlog/BACKLOG.md).
- **Evidence:** [October 4 reconciliation](../../reports/2026-10-04-0901-status-report.md#what-is-actually-broken-or-missing).
- **Historical contract:** [PM operations spec](../../completed/20260203_d4.4-operations/spec.md).
- **Approval workflow:** [Shipped research command](../../../claude/commands/research.md).
- **Current code:** `src/agentic_mbse/pm/operations.py:635` and CLI registration in `src/agentic_mbse/cli/pm_cli.py:562`.
- **Product lens:** [Review ledger](product-lens.md).

**Next Steps:** Review this draft, then use `$my-design` for the approval operation and result reporting.
