## spec — 2026-10-04 — rev .project/active/pm-registry-integrity/spec.md

Point (re-derived): Preserve registry entries and their usable identities so later modeling work can respect accumulated goals, knowledge, requirements, architecture decisions, and verification criteria. [source: claude/skills/project-structure/SKILL.md; project_templates/{KNOWLEDGE,REQUIREMENTS,VALIDATION_MATRIX,ARCHITECTURE,OVERVIEW}.md.template, grade: INHERITED]
Falsifier: A supported registry entry disappears silently or an extant registry ID is reused, making downstream references ambiguous.
Findings: None.
Gate: CLEAR

## design_review — 2026-10-04 — rev .project/active/pm-registry-integrity/design.md
Note: the product-lens instruction file (`~/.claude/scripts/product-lens.md` and its pack source) was unreadable from this stage's sandbox; the lens ran on the fallback method (independent point, falsifier, DO/DON'T findings by source grade, two structural smells). No `.project/product/` or `.project/adr/` exists, so no owner-verbatim sources were available.
Point (re-derived): The registry files (DI, G/AQ, AD, PR, SV, and WI's `BACKLOG.md` frontmatter) are the durable record that later modeling work reads and cites by ID. PM scripts own all mutation, ID assignment, and format enforcement of that record, so every scripted write must leave the record intact and mint IDs that keep citations unambiguous. [source: claude/skills/project-structure/SKILL.md:31-81; project_templates/MODELING_PROCESS.md.template:82; claude/commands/status.md:84; claude/commands/backlog.md:90; project_templates/BACKLOG.md.template:8-14, grade: INHERITED]
Falsifier: After a PM operation, a record that was in a registry file (including the `BACKLOG.md` frontmatter) is gone or changed without the user being told, or a newly minted ID repeats a number the file already names.
Findings:
- No DON'T or DO contradiction at owner or HARD grade. D8 (write back the loaded document) fits "Scripts own BACKLOG.md" (backlog.md:90) and the template's "the frontmatter wins" (BACKLOG.md.template:9-14). D5/D6 fit the templates, which keep example IDs inside HTML comments. D3/D10 refusals are the "format enforcement" status.md:84 assigns to scripts. [INHERITED]
- Non-gating: `audit-models.md:33` routes SV status changes only through `pm update-validation`; D4's refusal on an unparsed row leaves no scripted path, so the refusal message should say the row must be repaired by hand. Disposition: folded into design-review m4. [INHERITED: claude/commands/audit-models.md:33, claude/commands/status.md:84]
- Non-gating: under D8 a carried-forward invalid work item stays in the frontmatter but is absent from the rendered body; the design should state this. Disposition: design-review m6. [INHERITED: BACKLOG.md.template:10-14]
- Non-gating: the per-prefix record-ID regexes in parser.py (`:324`, `:400`, `:488`, `:529`, `:742`, `:766`) validate records and do not number them; the design should say so, so they are not read as a second numbering authority. Disposition: design-review n5. [AGENT: design.md:36]
Smells: None fired. (a) The allocator's whole-file scan is not a consumer compensating for a parser guarantee: the invariant is "IDs the file names", owned by operations.py and stated in D5/I5. (b) D8 moves an invariant (the writer no longer keeps the frontmatter schema-valid by deletion; it carries invalid records forward) and says so in Core Concept 3 and D9.
Gate: CLEAR — no owner/HARD contradiction and no fired smell; the three findings are disclosure and message wording.
