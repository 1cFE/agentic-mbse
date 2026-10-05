# Spec: Escaped Pipes and Registry ID Integrity

**Status:** Implemented and audited (Certified with follow-ups, 2026-10-04; see audit.md). Awaiting owner close.
**Owner:** Reid W
**Created:** 2026-10-04 09:28 PDT
**Complexity:** MEDIUM
**Branch:** pm-registry-integrity
**Backlog Item:** PM-MATRIX-ESCAPED-PIPE

## Problem

[INHERITED: product-lens.md, from claude/skills/project-structure/SKILL.md] Other artifacts cite registry IDs (`SV-`, `DI-`, `PR-`, `AD-`, `WI-`, `G-`, `AQ-`) by spelling. A record that silently disappears, or an ID minted twice, makes those citations ambiguous. The PM tooling has two defects:

1. **Records are lost or corrupted.** PM reads drop or misread valid records, and PM writes delete or corrupt records they could not parse.
2. **IDs are minted twice.** Every allocator numbers new IDs from parsed records only (`operations.py:58`), so the ID of a record the parser left out can be issued again.

Evidence for record loss:

- fusion-tea's real `VALIDATION_MATRIX.md` holds 135 `SV-` rows (max `SV-135`) and parses to 133 records with two warnings. `SV-035` is a valid GFM row (`\|rel dev\|`, status `passing`) that the splitter at `parser.py:109` drops by shifting its Type column. `SV-034` is genuinely malformed (raw `|rel dev|`) and should stay diagnosed. The next real ID is `SV-136`, so this file shows loss, not reuse. (briefs/spec_review.md, orchestrator-verified facts)
- `update-validation` has its own splitter (`operations.py:1148`). On an escaped row it reports success, writes the new status into the Source column, leaves Status unchanged, and rewrites `\|rel dev\|` as `\ | rel dev\ |`. (spec-review.md L3-2, probe 2)
- `add-validation` writes a description containing `|` without escaping it (`operations.py:194`), so the tool creates rows its own parser then drops. (spec-review.md L3-3)
- The backlog writer (`operations.py:155`, shared by `add-item`, `add-epic`, and `close-item`) rewrites `BACKLOG.md` from parsed data. A work item with an invalid field is deleted. With malformed YAML, `add-item` succeeds and erases every work item. (spec-review.md L2-2, probes 3 and 5)

Evidence for ID reuse:

- A fresh matrix holding valid `SV-033`, escaped-pipe `SV-034`, and malformed `SV-035` parses only `SV-033`, and `add-validation` mints a second `SV-034`. Reuse happens when the dropped record holds the highest ID. The fixture's labels are the reverse of fusion-tea's file by design; the fixture does not need to mirror it. (`.project/reports/2026-10-04-0901-status-report.md:64`; spec-review.md probe 1)
- A work item with `status: in-progress` is dropped by the parser, and `add-item` mints its ID (`WI-002`) again. (spec-review.md L2-2, probe 3)
- On fusion-tea, live exposure today is SV, DI, and WI. AD is latent: `ARCHITECTURE.md` has drifted to `## AD-NNN` headings with no `## Key Decisions` section, so it parses to zero records, but `register-decision` refuses to write until that section exists (`operations.py:446-451`). fusion-tea has also restarted DI, PR, and AD numbering after archiving, leaving notes such as "Previous entries (DI-001 through DI-014) archived" (`KNOWLEDGE.md:11`), and its `REQUIREMENTS.md:65` cites "archived DI-014" by spelling. (spec-review.md L1-3, L1-4)

## Success Criteria

- [x] [INHERITED: BACKLOG.md PM-MATRIX-ESCAPED-PIPE, Problem and original Goal (1)] **Escaped pipes.** Splitting a registry table row follows GitHub's GFM table rule ([GFM spec §4.10, Tables extension](https://github.github.com/gfm/#tables-extension-)): `\|` is a literal pipe inside the cell, including inside code spans. A cell holding `\|rel dev\|` stays one cell, parses to `|rel dev|`, and adjacent columns keep their meaning. The behavior of `\\|` is pinned by a test. Evidence: E1, E4, and a splitter test with a pipe inside a code span.
- [x] [INFERRED] **One escape rule for every row reader and writer.** Every operation that reads or rewrites a registry table row applies the same escape rule, and updating a row changes only the targeted cell. Evidence: a test running `update-validation` on an escaped row, where the new status lands in Status and every other cell, including `\|rel dev\|`, is unchanged.
- [x] [INFERRED] **Round-trip.** A value written by a PM add operation to a table registry (SV, PR, G, AQ) reads back identical through the parser, including a value containing `|`. Evidence: for each table registry (SV, PR, G, AQ), a test that adds a free-text value containing `|` and reads it back.
- [x] [AGENT] (orchestrator, 2026-10-04: the only reading that also covers drifted structure and archive notes, and E4 as ratified already says "above every ID in the file") **No ID minted twice.** A newly minted ID is numerically greater than every same-prefix ID token that appears in the registry file outside HTML comments, whether or not the parser accepted its record. Evidence: E1, E2, E4, and a test whose `KNOWLEDGE.md` holds records `DI-001` to `DI-011` under an archive note naming `DI-014`, where the next ID is `DI-015`.
  - A token stands alone: `MAG-001` is not `G-001`. Tokens inside code spans count.
  - Allocation stays strictly above the max, with no gap filling. The archive-note protection depends on this.
  - HTML comments are excluded because every shipped template holds example IDs inside them (`project_templates/*.md.template`), and existing tests assert the first minted IDs.
  - Accepted costs: a prose mention of a high number skips numbers permanently (a gap, never a reuse), and an ID that appears only inside an HTML comment is not protected.
  - `PR-1` and `PR-001` both count as 1, as today (`operations.py:63-67`). Whether fusion-tea treats them as the same ID is that project's convention, not settled here.
- [x] [AGENT] (orchestrator, 2026-10-04: E2's WI case requires it, and the 2026-02 operations spec already promised a malformed backlog fails rather than corrupts) **No record lost on write.** No PM write deletes an existing record or alters any record other than the one it targets. When a write cannot keep a record, it refuses with an error that names what it could not keep, and a refused write leaves every file unchanged (`close_item` moves the item directory and rewrites its frontmatter before it writes `BACKLOG.md`, `operations.py:1078-1107`, so a late refusal would half-close an item). Evidence: E2's WI case, plus tests where `add-item`, `add-epic`, and `close-item` meet a work item with an invalid field and a `BACKLOG.md` with malformed YAML.
- [x] [INFERRED] **Nothing else changes.** Evidence: E3.
  1. No operation renumbers, re-pads, or re-spells an existing ID; `PR-1` stays `PR-1`.
  2. New IDs keep the `PREFIX-NNN` form with three-digit minimum padding (`operations.py:70`).
  3. Parsed values of rows without `\|` are unchanged.
  4. Rows containing `\|` change to the unescaped value. That change is the fix, and it includes PR, G, and AQ rows that parse with shifted columns today.
  5. Malformed records stay diagnosed; new diagnostics may be added.

### Acceptance evidence

[INFERRED] (ratified by owner, 2026-10-04: "those hold. proceed.") The four checks below are the item's acceptance evidence. The criteria above cite them by number.

- **E1.** The three-record reproduction (Problem) becomes a pytest test. It is red before the fix (only `SV-033` parses; the allocator mints `SV-034` again) and green after (escaped `SV-034` parses, malformed `SV-035` stays warned, next ID `SV-036`).
- **E2.** Each of the seven registries gets a fixture whose highest ID sits in a record that fails parsing. The add operation mints above it, and the file diff is exactly the one new record. Table (SV, PR, G, AQ), heading (DI, AD), and frontmatter (WI) registries each get their own case.
- **E3.** The existing PM suite (`tests/test_pm_*.py`) stays green, and a parse snapshot of copies of fusion-tea's real registry files is identical before and after, except for `SV-035` appearing.
- **E4.** End-to-end on a copy of fusion-tea's real matrix, run by the orchestrator: `SV-035` is present with literal `|rel dev|` in the right columns and status `passing`; `SV-034` is still warned; the new row is minted above every ID in the file, with nothing else rewritten.

[AGENT] (orchestrator, 2026-10-04) Clarifications to the ratified wording, each so the check matches its intent:

- E2's "exactly the one new record" includes the blank separator lines that appends add (`operations.py:199-210`, `:461-468`).
- E2's PR, G, and AQ fixtures drop their row with a decorated ID cell such as `**PR-007**`, since an escaped pipe does not drop rows in those tables.
- E3 allows `SV-035`'s warning to disappear and allows new diagnostics, such as one reporting that `SV-034` is present but unparsed and its ID reserved.
- E4 and the snapshot half of E3 read gitignored copies of a private sibling repo (`.orchestrate-logs/ft-snapshot/`). The orchestrator runs them and records the result in the audit; they are not CI tests.
- E4 also records the next DI the allocator would mint on the `KNOWLEDGE.md` copy. Expected `DI-015`: the live records end at `DI-011`, and the archive note at `KNOWLEDGE.md:11` names `DI-014`. A record-shaped scan would mint `DI-012` and fail this.
- E2's WI case is judged on the YAML frontmatter. The `BACKLOG.md` body is a dashboard re-rendered from the kept records on every write.

## Known Requirements

- **[INHERITED: BACKLOG.md PM-MATRIX-ESCAPED-PIPE, Goal as filed 2026-08-21 (`35fa2b6`) and as rewritten 2026-10-04 (`6960ae4`)]** All seven registries are in scope: SV, DI, PR, AD, WI, G, AQ.
- **[INFERRED]** Registry formats stay supported in their native representation: table rows, heading records, and work-item frontmatter. Reserving a malformed record's ID does not make its other content valid.

**[INHERITED: spec-review.md L2-1, checked against the code at `ccf87c0`]** Each registry is exposed differently:

| Registry | File and format | Dropped from the parse today by | Effect of an escaped pipe | What PM writes do to the file |
|---|---|---|---|---|
| SV | `VALIDATION_MATRIX.md`, table under `## Verification Registry` | invalid ID, Type, Mechanism, or Status (warned); rows after a prose line or outside the section (silent) | drops the row (a pipe before the Type column fails the Type check; a later pipe fails a later check) | `add_validation` inserts one row; `update_validation` rewrites one row through its own splitter |
| PR | `REQUIREMENTS.md`, table under `## Requirements` | invalid ID cell such as `**PR-007**` (warned); rows outside the scanned table (silent) | keeps the row; later columns shift with no warning | `promote_requirement` inserts one row; raises if the section heading is missing |
| G, AQ | `OVERVIEW.md`, tables under `## Goals Registry` and `## Analysis Questions` | same as PR | same as PR | `register_intent` inserts one row per goal or question; raises if the section heading is missing |
| DI | `KNOWLEDGE.md`, `### DI-NNN: title` headings | invalid Status (warned); heading drift such as `## DI-` or a missing colon (silent) | n/a | `add_insight` and `approve_research` append at end of file |
| AD | `ARCHITECTURE.md`, `### AD-NNN:` headings under `## Key Decisions` | invalid Status (warned); headings outside that section (silent; fusion-tea's case) | n/a | `register_decision` refuses if the section is missing, else inserts |
| WI | `work/BACKLOG.md` YAML frontmatter | invalid id, scale, status, or priority (warned); an invalid epic drops all its items; malformed YAML drops every record (warned) | n/a | `add_item`, `add_epic`, and `close_item` rewrite the whole file from parsed data, deleting dropped records |

## Non-Goals

- Repairing existing duplicate IDs and their references, or adding persistent history for deleted records.
- Deleted IDs are not protected: a deleted ID can be minted again once the registry file no longer names it.
- Archived IDs are protected only while the registry file still names them, as fusion-tea's archive notes do today.
- WI IDs also appear in directory names (`work/active/WI-NNN_*`, `work/completed/*_WI-NNN_*`), which the guarantee does not scan; a reused WI ID there makes `resolve_work_item` raise on ambiguity (`state.py:193`).

## Decisions

- [AGENT] (orchestrator, 2026-10-04) The historical contract "IDs are never reused" (`.project/completed/20260203_d4.4-operations/spec.md:73`) was never implemented, and this item narrows it to IDs present in the registry file, with no persistent high-water mark. Reasoning: max-plus-one over parsed records has always reused a deleted highest ID, and the whole-file rule already protects archived ranges for as long as the file names them. Limits are under Non-Goals.

## Open Questions / Deferred to design

- How allocation finds same-prefix ID tokens. Orchestrator steer: one whole-file token scan outside HTML comments, the same for tables, headings, and frontmatter. Any alternative must meet the "No ID minted twice" criterion on drifted structure (fusion-tea's `## AD-001` and `### PR-1` headings) and on prose mentions (fusion-tea's archive notes naming `DI-014` and `PR-007`), which rules out detection of record-shaped text alone.
- What `\\|` (an escaped backslash before a pipe) means, and how writes emit a literal pipe in a new cell so the round-trip criterion holds.
- How the backlog writer carries forward a work item it cannot validate. E2's WI fixture uses a work item with an invalid field (such as `status`), and `add-item` must still mint above it and keep it, so carrying forward is required for that case; design chooses the mechanism (raw text or a preserved YAML node) and which other failures refuse (an invalid epic, a non-mapping entry). Malformed YAML refuses.

## Related Artifacts

- **Backlog:** [PM-MATRIX-ESCAPED-PIPE](../../backlog/BACKLOG.md).
- **Evidence:** [October 4 reconciliation](../../reports/2026-10-04-0901-status-report.md#what-is-actually-broken-or-missing).
- **Spec reviews:** [spec-review.md](spec-review.md) and [spec-review-2.md](spec-review-2.md), with resolutions; orchestrator-verified fusion-tea facts in [briefs/spec_review.md](briefs/spec_review.md).
- **Historical contract:** [PM operations spec](../../completed/20260203_d4.4-operations/spec.md).
- **Current code:** table splitter `src/agentic_mbse/pm/parser.py:109`; allocator `src/agentic_mbse/pm/operations.py:58`, validation allocation at `:514`, `update_validation` splitter at `:1148`, backlog writer at `:155`.
- **fusion-tea copies:** `.orchestrate-logs/ft-snapshot/` (gitignored; read by E3 and E4).
- **Product lens:** [Review ledger](product-lens.md).

**Next Steps:** Owner runs `/_my_close`, then `/_my_pre_pr` on branch `pm-registry-integrity`.
