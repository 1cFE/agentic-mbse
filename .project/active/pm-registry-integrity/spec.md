# Spec: Escaped Pipes and Registry ID Integrity

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-10-04 09:28 PDT
**Complexity:** MEDIUM
**Branch:** harness-right-size
**Backlog Item:** PM-MATRIX-ESCAPED-PIPE

## Problem

[INHERITED: ../../backlog/BACKLOG.md, PM-MATRIX-ESCAPED-PIPE] The shared Markdown table parser treats escaped literal pipes as column separators. Valid validation rows disappear with warnings, and ID allocation considers only parsed records. A fresh temporary matrix containing valid `SV-033`, escaped-pipe `SV-034`, and malformed `SV-035` parsed only `SV-033`; adding a validation entry minted `SV-034` again. Other registries use the same allocator and can lose IDs when their records fail parsing. Existing artifacts refer to these IDs, so reuse can make a reference ambiguous.

## Success Criteria

- [ ] [INHERITED: ../../backlog/BACKLOG.md, PM-MATRIX-ESCAPED-PIPE] A cell containing `\|rel dev\|` remains one cell, its parsed value contains literal `|rel dev|`, and adjacent columns retain their intended meanings.
- [ ] [INHERITED: ../../backlog/BACKLOG.md, PM-MATRIX-ESCAPED-PIPE] In the three-record reproduction, the valid escaped-pipe row is retained, the malformed row remains diagnosed, and the next SV ID is greater than `SV-035`; no existing ID is reused and neither old row is rewritten by adding the new entry.
- [ ] [INHERITED: ../../backlog/BACKLOG.md, PM-MATRIX-ESCAPED-PIPE] ID creation for SV, DI, PR, AD, WI, G, and AQ cannot reuse a syntactically valid ID still present in its registry because the enclosing record was omitted by parsing. Evidence covers each registry's actual format and preserves current increasing numeric ID behavior.
- [ ] [INFERRED] Ordinary tables and successful registry operations retain their existing parsed values, warning behavior for malformed records, and externally referenced ID spelling.

## Known Requirements

- **[INHERITED]** The reported failure is in shared PM parsing and allocation, not only the two Fusion TEA cells; all seven prefixes are in scope. Source: `../../backlog/BACKLOG.md`, PM-MATRIX-ESCAPED-PIPE.
- **[INFERRED]** Registry formats remain supported in their native representation: table rows, heading records, and work-item frontmatter. Reserving a malformed record's ID does not make its other content valid.

## Non-Goals

- Repairing existing duplicate IDs and their references, or adding persistent history for deleted records.

## Open Questions / Deferred to design

- The backlog proposes raw `| PREFIX-N |` scanning for every registry, but several registries use headings or frontmatter. Design must choose format-aware discovery and where that information enters allocation; a table-only scan cannot satisfy the all-registry criterion.
- Define escaping behavior for consecutive backslashes, delimiter positions, and formatting when a newly appended cell contains a literal pipe. Read/write behavior should agree without requiring hand edits.
- The historical operations spec promises deleted IDs are never reused, while the current allocator only examines existing records. This repair guarantees IDs in extant records; any stronger historical-reservation contract needs explicit disposition before claiming global non-reuse.

## Related Artifacts

- **Backlog:** [PM-MATRIX-ESCAPED-PIPE](../../backlog/BACKLOG.md).
- **Evidence:** [October 4 reconciliation](../../reports/2026-10-04-0901-status-report.md#what-is-actually-broken-or-missing).
- **Historical contract:** [PM operations spec](../../completed/20260203_d4.4-operations/spec.md).
- **Current code:** `src/agentic_mbse/pm/parser.py:109`, `src/agentic_mbse/pm/operations.py:58`, and validation allocation at `:514`.
- **Product lens:** [Review ledger](product-lens.md).

**Next Steps:** Review this draft, then use `$my-design` for escaping and format-aware ID protection.
