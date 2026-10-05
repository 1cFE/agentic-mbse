# Brief: close — pm-registry-integrity

**Stage:** `/_my_close`. **Item:** `.project/active/pm-registry-integrity/` (standalone, backlog `PM-MATRIX-ESCAPED-PIPE`). Owner asked for close on 2026-10-04 after the audit verdict Certified with follow-ups (`audit.md`, including its Re-check section).

What to do, per your command: archive the item folder to `.project/completed/` with the date prefix, write the CHANGELOG entry, and update tracking (`CURRENT_WORK.md`, `active/README.md` if it indexes this folder, the backlog item's status). File the four remaining advisory follow-ups from `audit.md` as backlog items with the IDs the audit proposed: `PM-DASHBOARD-REPEATED-KEY`, `PM-UPDATE-VALIDATION-COMMENT`, `PM-WRITE-BACKLOG-TYPED-FORM`, `PM-R7-MESSAGE`. Each gets a one-paragraph Problem and Goal drawn from the audit, priority P3 unless the audit says otherwise, and a pointer to the archived item. The `briefs/` folder, `acceptance-evidence.md`, and both spec reviews move with the item; they are the orchestration trail.

Two downstream notes for the CHANGELOG entry: fusion-tea's agentic-mbse pin must move after merge, and fusion-tea's `SV-034` row still holds two raw pipes that need escaping by hand; neither is in this item's scope. Also record the PM operations contract change: "IDs are never reused" (2026-02 operations spec) is narrowed to IDs present in the registry file, per the spec's Decisions section.

Commit the close with a subject that leads with the decision. End with `ARTIFACT: <path of the completed folder>`.
