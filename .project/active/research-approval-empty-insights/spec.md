# Spec: Approve Research with No New Insights

**Status:** Reviewed and revised 2026-10-05 ([review](spec-review.md), verdict Revise; resolutions recorded there)
**Owner:** Reid W
**Created:** 2026-10-04 09:28 PDT
**Complexity:** LOW
**Branch:** research-approval-empty-insights
**Backlog Item:** PM-APPROVE-RESEARCH-EMPTY-INSIGHTS

## Problem

[INHERITED: ../../backlog/BACKLOG.md, PM-APPROVE-RESEARCH-EMPTY-INSIGHTS] Research can be approved without producing a new domain insight, such as a source-registration round, a bounded negative result, or confirmation of existing knowledge. The public PM operation rejects an explicit empty insight list with `No insights provided`, leaving the document in `knowledge/research/pending/`. Operators must move approved research by hand, bypassing the supported approval operation.

## Success Criteria

- [ ] [INHERITED: ../../backlog/BACKLOG.md, PM-APPROVE-RESEARCH-EMPTY-INSIGHTS] `approve-research` with explicit `--insights '[]'` succeeds, moves the existing valid pending document to `knowledge/research/approved/`, creates no DI entries or IDs, and leaves the knowledge registry unchanged. The direct Python operation has the same behavior.
- [ ] [INFERRED] A zero-insight approval leaves `knowledge/KNOWLEDGE.md` exactly as found: byte-identical if present, still missing if missing. Its success and its warnings do not depend on that file's presence or contents.
- [ ] Omitting the insight list stays a caller error on both surfaces.
  - [INHERITED: ../../backlog/BACKLOG.md, PM-APPROVE-RESEARCH-EMPTY-INSIGHTS] CLI: omitting `--insights` is a usage error. Explicit emptiness is distinct from malformed JSON or an invalid insight payload.
  - [INFERRED] Python: `insights` stays a required argument, and `None` is not treated as an explicit empty list.
- [ ] [INFERRED] Non-empty approval of a regular file retains its current insight creation behavior. Existing missing-file and pending-location validation still rejects invalid requests without moving research or mutating knowledge. A pending path that is not a regular file, such as the `pending/` directory itself, is refused with nothing moved, for empty and non-empty lists alike.
- [ ] [INFERRED] A zero-insight approval is reported accurately to each observer.
  - CLI user: exit code 0, and a message stating the document was approved with no insights created. The message does not end in an empty `Created insights:`.
  - Python caller: `ids_assigned` is empty, and `files_modified` lists the approved path and does not list `KNOWLEDGE.md`.
- [ ] [INFERRED] The shipped `/research` command's approval step (`claude/commands/research.md:75-79`) tells the agent that a report approved with every insight skipped is a call with `--insights '[]'`, and no longer tells it to report assigned IDs when none exist. The `approve-research` row in `claude/skills/toolkit-awareness/SKILL.md:90` no longer implies insights are always registered.
- [ ] [INHERITED: ../../backlog/BACKLOG.md, PM-APPROVE-RESEARCH-EMPTY-INSIGHTS] Tests cover both explicit `[]` and a missing `--insights`: "A test covers both, and asserts the document lands in `approved/` with no DI written."

## Non-Goals

- Changing research curation or the user's approval gate (`claude/commands/research.md:69-71`), or approving a document automatically.
- A move that fails after insights were appended, and a same-name file already in `approved/`, keep their current behavior because this change makes neither worse. Filed as [PM-APPROVE-RESEARCH-MOVE-SAFETY](../../backlog/BACKLOG.md).

## Open Questions / Deferred to design

- Exact wording of the zero-insight success message, the `/research` approval step, and the toolkit-awareness row.
- How the zero-insight path stays independent of `KNOWLEDGE.md`, and whether a Python `None` fails as a structured result or an exception.

## Related Artifacts

- **Backlog:** [PM-APPROVE-RESEARCH-EMPTY-INSIGHTS](../../backlog/BACKLOG.md).
- **Evidence:** [October 4 reconciliation](../../reports/2026-10-04-0901-status-report.md#what-is-actually-broken-or-missing).
- **Historical contract:** [PM operations spec](../../completed/20260203_d4.4-operations/spec.md).
- **Approval workflow:** [Shipped research command](../../../claude/commands/research.md).
- **Current code:** `src/agentic_mbse/pm/operations.py:910` (function) and `:936` (empty-list guard); CLI registration in `src/agentic_mbse/cli/pm_cli.py:562`.
- **Review:** [Spec review](spec-review.md).
- **Product lens:** [Review ledger](product-lens.md).

**Next Steps:** Proceed to `/_my_design` for the approval operation, its result reporting, and the shipped `/research` instructions.
