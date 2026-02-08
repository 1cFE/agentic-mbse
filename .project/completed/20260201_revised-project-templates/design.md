# Design: Revised Project Templates (D1.2)

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-01 20:42:27 UTC
**Branch:** revamp-architecture

## Overview

Revise 5 existing project templates to align with the 4-directory information architecture. Each template has a specific transformation: OVERVIEW.md gains structured entity tables, BACKLOG.md gains YAML frontmatter, MODELING_GUIDE.md gains skill extraction markers, MODELING_PROCESS.md and README.md get path and reference updates.

## Related Artifacts

- **Spec:** `.project/active/revised-project-templates/spec.md`
- **Epic:** `.project/backlog/epic_architecture-structure.md` (D1.2)
- **Architecture:** `.project/concepts/architecture-redesign/information-architecture.md`
- **Architecture:** `.project/concepts/architecture-redesign/workflows.md`
- **D1.1 templates:** `project_templates/{KNOWLEDGE,ARCHITECTURE,REQUIREMENTS,VALIDATION_MATRIX,EPIC_GUIDE,epic_template}.md.template`

---

## Research Findings

### Current Template Analysis

All 5 templates live in `project_templates/` and are plain markdown files. No YAML frontmatter exists in any current template. All references use `modeling_pm/` paths.

**OVERVIEW.md.template** (172 lines):
- Sections: What We're Building, Why SysMLv2, Technical Approach, Technology Stack (includes Model Organization + Project Management trees), Success Criteria (Must/Should/Nice), Current Status, Project Risks, Getting Started, Key Contacts, Resources.
- Uses `<!-- -->` HTML comments for user-fillable placeholders.
- No structured entity tables (G-XXX, AQ-XXX).
- Content that must move: Technical Approach (→ ARCHITECTURE.md), Model Organization tree (→ ARCHITECTURE.md), Project Management tree (→ now work/ + project/), Current Status (→ BACKLOG.md/status), Key Contacts (remove).

**BACKLOG.md.template** (107 lines):
- Priority-bucket format: P0 through P4 sections with markdown headings.
- Each item uses bold-key format: `**Status**: READY`, `**Priority**: P0`.
- References `modeling_pm/completed/`, `modeling_pm/OVERVIEW.md`, `modeling_pm/MODELING_GUIDE.md`, `modeling_pm/MODELING_PROCESS.md`.
- No YAML frontmatter. Completely replaced by new format.

**MODELING_GUIDE.md.template** (282 lines):
- 12 sections. Needs section-by-section skill marker assignment.
- References `LOCAL_GUIDE.md` in opening note (must update to REQUIREMENTS.md per D1.3).
- Cross-references: `OVERVIEW.md`, `models/README.md`, `SOURCE_INDEX.md`, pattern docs.

**MODELING_PROCESS.md.template** (817 lines):
- References to old paths: `modeling_pm/MODELING_GUIDE.md` (line 808), `modeling_pm/OVERVIEW.md` (line 809), `SOURCE_INDEX.md` (line 810 — root level, now `knowledge/SOURCE_INDEX.md`).
- Quick Links section references `OVERVIEW.md` and `MODELING_GUIDE.md` without path prefix — these are relative and stay correct since MODELING_PROCESS.md will be in the same directory (`project/`).
- Phase 1.1 references reading `models/README.md` and `SOURCE_INDEX.md` — SOURCE_INDEX path needs update.
- References section at bottom has explicit `modeling_pm/` paths that need updating.

**README.md.template** (212 lines):
- Document purpose table references `SOURCE_INDEX.md`, `modeling_pm/OVERVIEW.md`, `modeling_pm/backlog/BACKLOG.md`, `modeling_pm/learnings/RAW_LEARNINGS.md`, `modeling_pm/MODELING_GUIDE.md`, `modeling_pm/MODELING_PROCESS.md`.
- Project Structure section has `modeling_pm/` tree.
- Resources section has `modeling_pm/` links.
- Command table lists 11 entries (9 commands + 2 backlog sub-commands).
- No `LOCAL_GUIDE.md` reference (already absent from README).

### D1.1 Template Patterns

The new templates from D1.1 establish conventions:
- **Empty-state pattern**: Header row only for tables, format examples in `<!-- -->` comments.
- **No fake data**: No example rows that look like real content.
- **Concise intro**: 1-2 sentence description, then optional reference to parent docs.
- **Cross-references**: Use relative paths assuming the file's installed location.

### Existing Command Set (for README)

The 9 existing commands (from `claude/commands/`): `/onboard`, `/research`, `/spec-model`, `/design-model`, `/plan-model`, `/implement-model`, `/audit-models`, `/manage-sources`, `/backlog`. Plus `/record-learning` as a skill.

---

## Proposed Design

### Template 1: OVERVIEW.md.template

**Transformation**: Restructure from generic project overview to Role 3 (Project Intent) document.

**Section structure** (in order):

```
# [Project Name]                          ← Keep, rename from "Project Overview"

## Project Summary                        ← Keep (was "What We're Building" + "Why SysMLv2")
  Merged into one concise section.
  2-3 paragraphs, user fills in.

## Goals Registry                         ← NEW (FR-1.1)
  Table: ID | Goal | Priority | Status | Source | Traced Requirements
  Empty header row only.
  Format example in HTML comment.

## Analysis Questions                     ← NEW (FR-1.2)
  Brief intro: "Questions the models must be able to answer."
  Table: ID | Question | Implies | Source | Status
  Empty header row only.
  Format example in HTML comment.

## Scope                                  ← NEW (FR-1.3)
  ### In Scope
  ### Out of Scope
  ### Future Phases

## Success Criteria                       ← REVISED (was Must/Should/Nice)
  Simplified to a single section with
  user-fillable checkboxes.

## Project Risks                          ← Keep (table format unchanged)

## Getting Started                        ← Keep
  Update paths:
  - MODELING_GUIDE.md → project/MODELING_GUIDE.md context (but relative
    link stays same since both in project/)
  - backlog/BACKLOG.md → work/BACKLOG.md
  - active/ → work/active/
  - SOURCE_INDEX.md → knowledge/SOURCE_INDEX.md

## Resources                              ← Keep
  Update paths. Add references to new docs:
  knowledge/SOURCE_INDEX.md, project/REQUIREMENTS.md,
  project/ARCHITECTURE.md, project/VALIDATION_MATRIX.md

REMOVED:
- "Technical Approach" section → ARCHITECTURE.md
- "Technology Stack" section (Model Organization + Project Management trees) → ARCHITECTURE.md + work/ structure
- "Current Status" section → BACKLOG.md / /status
- "Key Contacts" section → removed
- "Why SysMLv2" → folded into Project Summary if user wants it
```

**Key design choices**:
- Goals Registry and Analysis Questions tables use the exact column schemas from information-architecture.md section 3 Role 3.
- Format examples in HTML comments match the style established by D1.1 templates.
- Getting Started paths are relative (OVERVIEW.md lives in `project/`, so sibling references like `MODELING_GUIDE.md` stay the same, but references to `work/` and `knowledge/` need `../` prefix or description-only references).
- Since OVERVIEW.md is at `project/OVERVIEW.md`, cross-references to sibling files in `project/` use bare filenames. References to files outside `project/` use description text (e.g., "See `work/BACKLOG.md`") rather than relative links, since the depth relationship may vary.

### Template 2: BACKLOG.md.template

**Transformation**: Complete replacement of the priority-bucket format with YAML frontmatter + rendered dashboard body.

**Structure**:

```yaml
---
epics: []
standalone: []
---
```

Followed by a markdown body that serves as both documentation and an example of the rendered format:

```markdown
# Project Backlog

<!-- This file has two parts:
     1. YAML frontmatter (above) — machine-readable state, source of truth
     2. Markdown body (below) — human-readable dashboard, rendered from frontmatter

     The frontmatter is authoritative. When scripts update state (status changes,
     new items, completions), they update both the YAML and re-render the body.
     If the body drifts from the frontmatter, the frontmatter wins. -->

No epics or work items yet. Use `/spec-model` to start a work item,
or `/backlog` to manage the backlog.

<!-- Rendered dashboard format when populated:

## Epic: [Epic Name]
**Goal**: G-XXX | **Priority**: P0 | **Status**: active
**Epic file**: [epic-{name}.md](backlog/epic-{name}.md)

| Item | Scale | Status | Notes |
|------|-------|--------|-------|
| [Item name] | standard | active | |

## Standalone Items

| Item | Scale | Priority | Status | Notes |
|------|-------|----------|--------|-------|
| [Item name] | trivial | P1 | backlog | |

-->
```

**Key design choices**:
- Empty lists (`[]`) not empty sections — valid YAML that a parser can read without special-casing.
- The rendered dashboard format is shown in a comment, not as actual content that looks like real data.
- Brief explanatory text for the user ("No epics or work items yet...") provides guidance in the empty state.
- The comment explains the frontmatter/body relationship clearly — this is important for users who will initially edit BACKLOG.md manually before PM scripts (Epic 4) exist.

### Template 3: MODELING_GUIDE.md.template

**Transformation**: Add skill extraction markers. No content removed.

**Section-by-section marker assignments**:

| Section heading | Marker | Rationale |
|-----------------|--------|-----------|
| *(Header, note, related docs)* | No marker | Navigation — stays in guide |
| `## Core Principle: Definitions vs Usages` | No marker | **Pure rule** — the fundamental library/usage distinction |
| `## The EXPOSE Pattern` | `<!-- SKILL: moves to project-structure -->` | Reference material — how to use the pattern |
| `## Calculation Architecture (ADR-002)` | No marker | **Pure rule** — what's allowed in design files |
| `## Package Structure` | No marker | **Pure rule** — directory structure requirement |
| `## Naming Conventions` | No marker | **Pure rule** — naming standards |
| `## Documentation Standards` | No marker | **Pure rule** — the entire section stays unmarked. The rule ("every def requires a doc comment") and the code block showing the format are inseparable — the format *is* the rule. 18 lines total; not worth splitting. |
| `## Standard Imports` | `<!-- SKILL: moves to sysml-conventions -->` | Reference material — which imports to use |
| `## Key Syntax Patterns` | `<!-- SKILL: moves to sysml-conventions -->` | Reference material — syntax examples |
| `## Validation Checklist` | No marker | **Pure rule** — what to check before committing |
| `## Model Regression Testing` | `<!-- SKILL: moves to model-validation -->` | Reference/how-to material — testing methodology |
| `## Tools and Scripts` | `<!-- SKILL: moves to toolkit-awareness -->` | Reference material — CLI commands |
| `## Questions?` | No marker | Navigation — stays in guide |
| `## Pattern Documentation Index` | `<!-- SKILL: moves to sysml-conventions -->` | Reference material — pattern doc links |

**Additional changes**:
- Opening note: Update `[LOCAL_GUIDE.md](LOCAL_GUIDE.md)` reference to `[REQUIREMENTS.md](REQUIREMENTS.md)` per D1.3 decision.
- Related Docs `[OVERVIEW.md](OVERVIEW.md)` link — stays correct (both in `project/`).

**Marker format**: Place the comment on the line immediately before the section heading:

```markdown
<!-- SKILL: moves to sysml-conventions -->
## Standard Imports
```

This makes `grep "<!-- SKILL:" project_templates/MODELING_GUIDE.md.template` produce a clean extraction manifest.

**Pure-rules coherence verification**: After markers are placed, the unmarked sections form this flow:
1. Core Principle (definitions vs usages)
2. Calculation Architecture (ADR-002)
3. Package Structure
4. Naming Conventions
5. Documentation Standards (rule + format — kept whole)
6. Validation Checklist

This is a coherent, logical progression: what types exist → where calculations go → where files go → how to name things → how to document → what to check. The marked sections (EXPOSE pattern details, imports, syntax, testing, tools, pattern index) are supplementary reference material that enriches but isn't essential to the rules flow.

### Template 4: MODELING_PROCESS.md.template

**Transformation**: Path updates and new document references. Content structure unchanged.

**Path substitutions** (every occurrence of each pattern):

| Old reference | New reference | Notes |
|---------------|--------------|-------|
| `modeling_pm/MODELING_GUIDE.md` | `project/MODELING_GUIDE.md` | References section |
| `modeling_pm/OVERVIEW.md` | `project/OVERVIEW.md` | References section |
| `modeling_pm/backlog/` | `work/backlog/` | Any backlog path references |
| `modeling_pm/active/` | `work/active/` | Active work item references |
| `modeling_pm/research/` | `knowledge/research/` | Research pipeline references |
| `modeling_pm/learnings/` | `work/learnings/` | Learnings references |
| `modeling_pm/completed/` | `work/completed/` | Archive references |
| `SOURCE_INDEX.md` (root-level) | `knowledge/SOURCE_INDEX.md` | Phase 1.1 reading list, References section |
| `MODELING_GUIDE.md` (relative) | No change | Same directory (`project/`) — relative links stay valid |
| `OVERVIEW.md` (relative) | No change | Same directory (`project/`) — relative links stay valid |

After substitution: `grep -c "modeling_pm" project_templates/MODELING_PROCESS.md.template` must return 0.

**New document references to add** (contextually appropriate locations):

| Document | Where to reference | Context |
|----------|-------------------|---------|
| `knowledge/KNOWLEDGE.md` | Phase 1.1 (Read Core Documents, ~91) | Add to reading list: "Check KNOWLEDGE.md for existing domain insights" |
| `project/ARCHITECTURE.md` | Phase 2 Architecture & Design intro (~179) | "Record architectural decisions in ARCHITECTURE.md" |
| `project/REQUIREMENTS.md` | Phase 2.2 (~220) and Phase 3 (~334) | "Check REQUIREMENTS.md for project-specific rules" |
| `project/VALIDATION_MATRIX.md` | Phase 3.4 Validation Plan (~411) | "Update VALIDATION_MATRIX.md with verification criteria" |
| `knowledge/SOURCE_INDEX.md` | Phase 1.1 (~94) | Path update for existing reference |

**References section** (bottom of file, ~805-811): Replace all `modeling_pm/` paths with new locations.

### Template 5: README.md.template

**Transformation**: Update directory structure, document table, and resource links.

**Document purpose table** (currently lines 28-38): Replace with:

| Document | Purpose | Managed By |
|----------|---------|------------|
| **README.md** | Project overview (this file) | You |
| **CLAUDE.md** | AI operating rules, environment setup | You |
| **knowledge/SOURCE_INDEX.md** | Domain knowledge sources | `/manage-sources` |
| **knowledge/KNOWLEDGE.md** | Curated domain insights | `/research` |
| **project/OVERVIEW.md** | Project goals and intent | You |
| **project/ARCHITECTURE.md** | Model architecture decisions | You |
| **project/REQUIREMENTS.md** | Project-specific modeling rules | You |
| **project/VALIDATION_MATRIX.md** | System verification criteria | You |
| **project/MODELING_GUIDE.md** | SysML syntax reference | Static (don't edit) |
| **project/MODELING_PROCESS.md** | MBSE methodology | Static (don't edit) |
| **work/BACKLOG.md** | Work item pipeline | `/backlog` |
| **work/learnings/RAW_LEARNINGS.md** | Captured insights | `/record-learning` |

**"What You Edit" section** (lines 40-56): Update paths:
- `modeling_pm/OVERVIEW.md` → `project/OVERVIEW.md`
- Add `project/ARCHITECTURE.md`, `project/REQUIREMENTS.md`, `project/VALIDATION_MATRIX.md` to user-editable list
- `SOURCE_INDEX.md` → `knowledge/SOURCE_INDEX.md`
- `modeling_pm/backlog/BACKLOG.md` → `work/BACKLOG.md`
- `modeling_pm/learnings/RAW_LEARNINGS.md` → `work/learnings/RAW_LEARNINGS.md`
- `modeling_pm/active/*` → `work/active/*`
- `modeling_pm/MODELING_GUIDE.md` → `project/MODELING_GUIDE.md`
- `modeling_pm/MODELING_PROCESS.md` → `project/MODELING_PROCESS.md`

**Command table** (lines 76-89): Keep the existing 9 commands + 2 backlog sub-commands. No changes needed — command names haven't changed. Add a brief note after the table: "Additional commands may be available in later toolkit versions."

**Project Structure section** (lines 146-178): Replace `modeling_pm/` tree with:

```
knowledge/                   # "What do we know?"
├── SOURCE_INDEX.md          #   Domain knowledge sources
├── KNOWLEDGE.md             #   Curated domain insights
├── sources/                 #   Local reference materials
└── research/                #   Research pipeline
    ├── pending/             #     Unapproved research
    └── approved/            #     User-approved research

project/                     # "What are we building and how?"
├── OVERVIEW.md              #   Project goals and intent
├── ARCHITECTURE.md          #   Model architecture decisions
├── REQUIREMENTS.md          #   Project-specific rules
├── VALIDATION_MATRIX.md     #   System verification criteria
├── MODELING_GUIDE.md        #   SysML reference (static)
├── MODELING_PROCESS.md      #   MBSE methodology (static)
└── intent/                  #   Raw user documents

work/                        # "What's in progress?"
├── BACKLOG.md               #   Work item dashboard
├── EPIC_GUIDE.md            #   Epic decomposition guide (static)
├── backlog/                 #   Epic decomposition files
├── active/                  #   In-progress work
├── completed/               #   Archived work
├── analysis/                #   Model analysis reports
└── learnings/
    └── RAW_LEARNINGS.md     #   Process knowledge

data/                        # Machine-readable evidence
└── traceability_matrix.csv
```

Keep the `models/` tree as-is (unchanged by the architecture redesign).

**Resources section** (lines 206-212): Update all `modeling_pm/` references to new paths.

---

## Potential Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| MODELING_GUIDE.md skill markers placed on wrong boundaries | Medium | The marker-to-skill mapping is documented in the design and derived from workflows.md § 1.2. Epic 2 can adjust boundaries during extraction. |
| Relative links break when templates are installed to new paths | Low | OVERVIEW.md, MODELING_GUIDE.md, and MODELING_PROCESS.md all install to `project/` — their relative links to each other stay valid. Cross-directory references use description text or `../` paths. |
| BACKLOG.md empty YAML confuses users before PM scripts exist | Low | Explanatory comment in template body explains the frontmatter/body relationship. Users can manually edit the YAML until Epic 4 automates it. |
| README.md document table grows large (12 rows vs current 8) | Low | The architecture has more documents — this is inherent. Table remains scannable. |

## Integration Strategy

These 5 revised templates are consumed by two downstream deliverables:

1. **D1.4 (`cmd_init()` rewiring)**: Reads templates from `project_templates/` and installs them to their new destinations. D1.4 changes the destination paths; D1.2 changes the template content. These are independent — D1.2 templates work at the new paths without needing D1.4-specific adjustments.

2. **`replicate_setup.sh`** (also D1.4): Uses the same templates. No template-side changes needed for script compatibility.

The MODELING_GUIDE.md skill markers integrate with **Epic 2**: `grep -r "<!-- SKILL:" project_templates/MODELING_GUIDE.md.template` produces the extraction manifest.

## Validation Approach

1. **Markdown validity**: Each template must be valid markdown — no broken tables, no unclosed HTML comments.
2. **Empty-state check**: Install each template to a temp directory and visually verify it reads well with no user content.
3. **Path consistency**: `grep -r "modeling_pm" project_templates/` must return zero matches after all 5 templates are updated.
4. **YAML validity**: Parse BACKLOG.md.template's frontmatter with a YAML parser to confirm `epics: []` and `standalone: []` are valid.
5. **Cross-reference check**: Verify all inter-document links in the templates point to paths that exist in the new architecture.
6. **Existing tests**: `uv run pytest tests/` must pass (templates are not directly tested, but CLI tests reference template names).
7. **Skill marker audit**: Count `<!-- SKILL:` occurrences and verify each maps to exactly one skill from the catalog (5 skills total).

---

**Next Step:** After approval → `/_my_plan` or `/_my_implement`
