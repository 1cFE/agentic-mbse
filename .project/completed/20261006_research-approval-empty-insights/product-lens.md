## spec — 2026-10-04 — rev .project/active/research-approval-empty-insights/spec.md

Point (re-derived): Research preserves separate user decisions about approving the report and accepting each insight; only approved structured insights enter the actionable knowledge feed. [source: claude/commands/research.md §4; project_templates/KNOWLEDGE.md.template, grade: INHERITED]
Falsifier: A user approves a useful report while skipping every insight, but approval is refused, the report stays pending, or an unaccepted insight enters KNOWLEDGE.md.
Findings: None.
Gate: CLEAR

## audit — 2026-10-05 — rev b6d1667 (work: `git diff c37ff53..b6d1667 -- src tests claude`)

Point (re-derived): When the user approves a research report, `pm approve-research` moves it from `pending/` to `approved/` however many insights the user accepted (0, 1 or N). KNOWLEDGE.md receives exactly the accepted insights and nothing else. A refused call has no side effects. The approval stays an explicit user decision, so an omitted decision is not read as "approve with none". [source: `claude/commands/research.md:70-71,75-79` @c37ff53 (report and insights are separate decisions); `.project/concepts/architecture-redesign/main.md:33,38,55` (AP-1 0/1/N, AP-6 explicit curation, atomic mutations); `.project/completed/20260203_d4.4-operations/spec.md` FR-9; `claude/skills/toolkit-awareness/SKILL.md:85`; `project_templates/KNOWLEDGE.md.template` — grade: INHERITED, no owner-graded source exists]
Falsifier: In a project created by `init`, the user approves a report and skips every insight, and the agent runs `agentic-mbse pm approve-research knowledge/research/pending/<f> --insights '[]'`. The point is violated if any of these happen: exit is non-zero, the doc stays in `pending/`, KNOWLEDGE.md bytes change, the `/research` instructions don't say to make this call, or omitting `--insights` (or passing `null`) approves the doc.
Findings:
- audit-F1 [DO] Zero-insight approval opens a new and, per the backlog, common route to an existing gap: if `approved/` already holds a file with the same name, the move silently overwrites it. That approved doc is the record a DI's Source cites, so it is destroyed. The work does not cause the gap and does not fix it. — `research.md` Output line + `KNOWLEDGE.md.template` (DI Source = "approved research doc") + `SKILL.md:85` (INHERITED) — disposition: DEFERRED → backlog `PM-APPROVE-RESEARCH-MOVE-SAFETY` (filed 2026-10-05 at spec review, part (b))
Gate: DISPOSED (audit-F1)
