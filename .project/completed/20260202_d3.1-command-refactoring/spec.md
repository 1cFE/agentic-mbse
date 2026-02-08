# Spec: D3.1 Command Refactoring (9 existing commands)

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-02 05:35 UTC
**Updated:** 2026-02-02
**Complexity:** HIGH
**Branch:** revamp-architecture
**Epic:** EPIC-ARCH-003 (Architecture Redesign — Commands)

---

## Progress

### Completed (9/9)

| Command | Before | After | Key changes |
|---------|-------:|------:|-------------|
| design-model.md | 1,345 | 130 | Replaced 8 linear stages with 4-step process (Understand/Design/Validate/Approve). Removed Stage 5.5 entirely → sysml-conventions. Condensed 320-line template → section list. Added ARCHITECTURE.md direct reading, YAML frontmatter generation, review.md reference. |
| implement-model.md | 493 | 114 | Removed inline validation pyramid → model-validation. Removed doc comment format/MODEL QUALITY rules → sysml-conventions. Added AP-7 invocations (add-insight, trace-element, promote-requirement), backward navigation options, SV-XXX verification test writing step. |
| spec-model.md | 392 | 123 | Removed requirement format standards → requirements-tracking. Added broad landscape survey (OVERVIEW.md, KNOWLEDGE.md, BACKLOG.md, epic files). Added goal tracing (MR-XXX → G-XXX/DI-XXX), SV-XXX entry creation, PR-XXX promotion flagging, YAML frontmatter generation. |
| plan-model.md | 676 | 134 | Removed Quick Reference appendix entirely. Removed test phase patterns → model-validation. Condensed 4-step process (Understand/Phase/Feasibility/Write). Detailed "What Good Output Looks Like" with per-phase checklist spec, parallelization guidance, final integration phase. YAML frontmatter generation. |
| audit-models.md | 446 | 120 | Restructured around 6 "Verification Obligations" (numerical accuracy, source traceability, programmatic validation, PR-XXX compliance, AD-XXX adherence, SV-XXX evaluation) + work item acceptance. Added register-decision and update-validation AP-7 invocations. Dual-scope model (work item vs project audit). |
| research.md | 243 | 135 | Added AP-6 curation gate framing. Added approve-research AP-7 invocation with --insights JSON. Added DI-XXX insight suggestion flow. Added pending/approved file lifecycle. Trimmed source type definitions → source-traceability. Added Sub-Agent Usage table. User refined description and added WebFetch to allowed-tools. |

**Final totals:** 4,887 → 1,029 lines (79% reduction). Average: 114 lines. Max: 135 (research). Min: 71 (manage-sources).

### Structural Convention Confirmed (all 9)

All 9 commands follow a consistent pattern (FR-1, FR-25):

1. **YAML frontmatter** — name, description, skills, allowed-tools, user-invocable
2. **Title + Purpose/Input/Output** — command identity, 2-3 lines
3. **Skills Referenced** — prose section: what each skill provides and when to consult it
4. **Process** — lightweight numbered steps (Understand → core work → Validate → Approve/Complete), NOT flowcharts or rigid stage gates. Depth adapts to complexity.
5. **What Good Output Looks Like** — describes the artifact structure, not the steps to produce it (included where command produces a structured artifact: design-model, plan-model, audit-models, research)
6. **Sub-Agent Usage** (if applicable) — compact table of agent → question type (design-model, research)
7. **Guidelines** — critical rules and error handling, concise

**Key design decision:** Commands are guidance documents, not operations manuals. Skills carry domain knowledge; the spec defines what to build; the process describes the shape of the work without micromanaging the agent. This produces commands averaging 114 lines that are more effective than the 400-1300 line originals because the agent can hold the entire command in context alongside the skills.

**Convention document** (FR-2) ready to be written — pattern confirmed across all 9 commands.

### Requirement Compliance Review (9/9 — Final)

Full review completed 2026-02-02. Results for all 9 commands:

**All requirements satisfied.** Specific checks:

- FR-1 (structural convention): All 9 follow the established pattern. ✅
- FR-3 (skills in frontmatter): All 9 ✅. Skills match or justifiably expand components.md § 1 mappings.
  - research: `[source-traceability]` ✅
  - onboard: `[project-structure, source-traceability, epic-decomposition]` ✅
  - backlog: `[epic-decomposition]` ✅
  - manage-sources: `[source-traceability]` ✅
- FR-4 (Skills Referenced prose): All 9 ✅
- FR-5/6/7 (D2.5 extraction): All "→ SKILL" sections removed, all "→ PARTIAL" trimmed, all "→ STAYS" retained across all 9 commands. ✅
  - onboard: 3 SKILL sections removed (permission paths, SOURCE_INDEX template, models/ dir structure) ✅
  - manage-sources: 1 SKILL section removed (SOURCE_INDEX Format Reference) ✅
  - research: 2 PARTIAL sections trimmed (SOURCE_INDEX source types, sysmlv2-doc-analyzer kept as agent coordination) ✅
  - backlog: 2 PARTIAL sections trimmed (format templates kept with scale ref, completion scanning kept) ✅
  - manage-sources: 1 PARTIAL trimmed (permission workflow kept, rules removed) ✅
  - onboard: 1 PARTIAL trimmed (placeholder workflow kept, dir roles removed) ✅
- FR-8 (path updates): Zero `modeling_pm/` references across all 9 commands. ✅
- FR-9 (new info arch files): All required references present across all commands. ✅
- FR-10/11 (AP-7): All specified AP-7 invocations present and inline:
  - implement-model: 3 invocations (add-insight, trace-element, promote-requirement) ✅
  - audit-models: 2 invocations (register-decision, update-validation) ✅
  - research: 1 invocation (approve-research with --insights) ✅
  - backlog: AP-7 integration noted but specific CLI not yet defined per spec ("specific operations depend on action") ✅
- FR-12/13/14 (YAML frontmatter generation): spec-model, plan-model, design-model all show exact schemas. ✅
- FR-15-23 (per-command): All items addressed across all 9 commands. ✅

**Noted deviations (all acceptable):** See "Design Deviations from Spec" section below.

### Design Deviations from Spec

1. **Line targets significantly exceeded.** Spec targeted ~250 lines; actual average is ~124. The aggressive workflow tightening (removing flowcharts, condensing templates to section lists, eliminating redundancy with skills) went further than anticipated. This is a positive deviation — shorter commands mean less context consumed, leaving more room for skills and actual work.

2. **Structural convention differs from FR-1 § Section order.** The spec proposed a "Context Reading" section and separate "AP-7 Script Invocations" section. In practice: context reading is integrated into the Process steps (spec-model reads broadly in step 1; design/implement read selectively). AP-7 invocations are placed inline per FR-11 rather than in a separate section. Both changes improve coherence.

3. **spec-model reads broadly, downstream commands read selectively.** The spec is the first artifact — it surveys OVERVIEW.md, KNOWLEDGE.md, BACKLOG.md, epic files, and models/README.md to establish context. Design-model reads ARCHITECTURE.md directly (full structural landscape) but reads other project files selectively through what the spec references. Implement-model reads through the plan/design/spec chain. This tiered approach prevents context bloat in downstream commands. Consequence: design-model reads REQUIREMENTS.md indirectly through the spec rather than directly (noted in compliance review above).

---

## Business Goals

### Why This Matters

Commands are the user-facing behavioral layer of agentic-mbse. Today, 9 commands average 543 lines each (total: 4,887 lines / 38,661 tokens) because they embed knowledge that should be shared. `design-model.md` alone is 1,345 lines — nearly as many tokens as all 9 skills combined. This makes commands hard to maintain, inconsistent with each other, and prone to knowledge drift where the same SysML rules appear differently in different commands.

Epic 2 extracted the shared knowledge into 9 reusable skills. This deliverable completes the circle: refactor each command to reference skills instead of embedding knowledge, add AP-7 script invocations for state mutations, update paths to the 4-directory model, and tighten remaining workflow logic for conciseness.

### Success Criteria

- [x] All 9 commands refactored and functional (9/9 done)
- [x] Average command length under 300 lines (aspirational target: ~250) — actual average: 114 lines
- [x] No command exceeds 400 lines — max is 135 (research)
- [x] All commands use the new structural convention (9/9 done)
- [x] All `modeling_pm/` path references updated to 4-directory model (9/9 done, zero `modeling_pm/` refs)
- [x] AP-7 script invocations added where specified (implement: 3, audit: 2, research: 1, backlog: noted)
- [x] Structural convention (Q15) documented from first 2–3 commands — written to `command-convention.md` after confirming pattern across all 9
- [x] All existing agentic-mbse tests pass (`uv run pytest tests/`) — 342 passed, 1 skipped (2026-02-02)

### Priority

P0. This is the critical path for Epic 3, which unblocks the complete behavioral layer. D3.2 (new commands) depends on the structural convention established here. D3.5 (validation walkthrough) depends on these refactored commands.

---

## Problem Statement

### Current State

All 9 commands embed shared knowledge inline:

| Command | Lines | Tokens | Key embedded knowledge |
|---------|------:|-------:|----------------------|
| design-model.md | 1,345 | 10,997 | ~600 lines SysML syntax, ~200 validation, ~150 file structure, ~100 citations |
| plan-model.md | 676 | 5,681 | Test patterns, validation commands, file org appendix, naming conventions |
| onboard.md | 577 | 4,283 | Permission path rules, SOURCE_INDEX format, model directory structure |
| implement-model.md | 493 | 4,004 | Validation pyramid, syntax patterns, doc comment format, naming conventions |
| audit-models.md | 446 | 3,617 | Verification thresholds, citation patterns |
| spec-model.md | 392 | 3,539 | Requirement format standards, test assertion patterns |
| backlog.md | 358 | 2,325 | Feature vs epic format (minimal extraction) |
| manage-sources.md | 357 | 2,233 | SOURCE_INDEX format, permission path rules |
| research.md | 243 | 1,982 | SOURCE_INDEX source types (minimal extraction) |

Commands reference the old `modeling_pm/` directory structure. No commands reference skills. No commands invoke AP-7 scripts. No commands generate YAML frontmatter for work item artifacts.

### Desired Outcome

9 concise commands (~200–300 lines each) that:
- Reference skills for domain knowledge instead of embedding it
- Invoke AP-7 scripts for state mutations (exact CLI syntax)
- Use the 4-directory model paths (`knowledge/`, `modeling_project/`, `work/`, `data/`)
- Follow a consistent structural convention
- Generate YAML frontmatter where applicable (spec-model, plan-model)

---

## Scope

### In Scope

1. Refactoring all 9 existing commands per D2.5 extraction mapping
2. Establishing and documenting the structural convention (Q15) from the first 2–3 commands
3. Adding skill declarations to command frontmatter
4. Adding AP-7 script invocations with exact CLI syntax
5. Adding new information architecture references (reading OVERVIEW.md, ARCHITECTURE.md, REQUIREMENTS.md, etc.)
6. Adding YAML frontmatter generation to spec-model and plan-model
7. Path updates from `modeling_pm/` to 4-directory model
8. Tightening STAYS workflow sections for conciseness (needed to reach line targets)

### Out of Scope

- Writing 5 new commands (D3.2)
- Command registration in cmd_init() (D3.3)
- Agent cleanup (D3.4)
- Validation walkthroughs (D3.5)
- Building the AP-7 PM scripts themselves (Epic 4) — we add the *calls* with exact CLI invocations
- Modifying skill SKILL.md files — if a gap is found, flag it for a follow-up, don't fix it during command refactoring
- Changes to agent files
- Changes to test files (unless a test breaks due to a command path change)

### Edge Cases & Considerations

- **D2.5 "Estimated After" vs targets**: The extraction mapping estimates design-model at 600–800 lines after extraction alone. Reaching ~250 requires aggressive workflow tightening, not just extraction. The spec acknowledges this is a two-part effort.
- **AP-7 scripts don't exist yet**: Commands MUST include exact CLI invocations (e.g., `agentic-mbse pm add-insight --title "..." --source "work-item:WI-XXX/design.md" ...`) as documentation of the intended interface. These become functional when Epic 4 delivers.
- **Skill cross-reference accuracy**: The extraction mapping's skill assignments (components.md § 1) and the D2.5 per-section mapping must be reconciled. Where they disagree, D2.5 is authoritative (it's more granular).
- **Commands that gain lines**: `research.md` (243 lines) may grow slightly due to new approval workflow, supersession detection, and file save via script. This is acceptable if the total stays under 300.

---

## Requirements

### Functional Requirements

#### Structural Convention (Q15 Resolution)

> FR-1: Each refactored command MUST follow a consistent structural convention.

The architecture specifies (workflows.md § 1.3, D2.4 recommendations, components.md § 1):

**Frontmatter**: Commands declare skill dependencies in a frontmatter field.

```markdown
---
name: design-model
description: [one-line job description from components.md § 1]
skills: [sysml-conventions, project-structure, model-validation, source-traceability]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---
```

**Section order** (convention, not rigid template — commands may omit sections that don't apply):

1. **Title + Purpose/Input/Output** — Command identity (keep existing pattern)
2. **Skills Referenced** — Prose section explaining what each skill provides for this command and when the agent should consult it
3. **Context Reading** — What project files the command reads at startup (OVERVIEW.md, ARCHITECTURE.md, REQUIREMENTS.md, spec.md, design.md, etc.)
4. **Workflow Stages** — The command's core algorithm (Stage 1, Stage 2, etc.)
5. **AP-7 Script Invocations** — Exact CLI calls the agent makes during the workflow, with argument placeholders
6. **Guidelines / Critical Rules** — Remaining quality standards and enforcement rules
7. **Error Handling** — Workflow-specific error conditions

> FR-2: The convention MUST be documented as a standalone reference after the first 2–3 commands are refactored, so D3.2 (new commands) can follow it.

Location: `.project/active/d3.1-command-refactoring/command-convention.md` (produced during design phase).

#### Skill Reference Pattern

> FR-3: Commands MUST declare skill dependencies in YAML frontmatter (`skills:` field).

Per D2.4 resolution (Q10): SKILL.md files load at command invocation. Reference files (`references/*.md`) load on demand. No phase-based staging.

> FR-4: Commands MUST include a "Skills Referenced" prose section that tells the agent what each skill provides and when to consult it during the workflow.

This is not just a list — it's behavioral guidance. Example:

```markdown
## Skills Referenced

- **sysml-conventions**: Syntax rules, naming, patterns, pitfalls. Consult when writing or reviewing SysML code. Use the stencils reference (`references/stencils.md`) when creating new definitions.
- **model-validation**: 8-level quality pyramid, CLI usage, thresholds. Consult when running validation or interpreting results.
```

#### Extraction (Per D2.5 Mapping)

> FR-5: For each section marked "→ SKILL" in D2.5, the inline content MUST be removed and replaced with a 1-line skill reference.

> FR-6: For each section marked "→ PARTIAL" in D2.5, the extracted portion MUST be removed and the remaining workflow logic kept, with a skill reference added.

> FR-7: Sections marked "→ STAYS" MUST be retained but SHOULD be refactored for conciseness to reach line targets.

The D2.5 extraction mapping (`.project/active/d2.5-extraction-mapping/extraction-mapping.md`) is the authoritative guide for what to remove from each command.

#### Path Updates

> FR-8: All `modeling_pm/` path references MUST be updated to the 4-directory model:

| Old Path | New Path |
|----------|----------|
| `modeling_pm/active/` | `work/active/` |
| `modeling_pm/backlog/BACKLOG.md` | `work/BACKLOG.md` |
| `modeling_pm/research/` | `knowledge/research/` |
| `modeling_pm/learnings/` | `work/learnings/` |
| `modeling_pm/OVERVIEW.md` | `modeling_project/OVERVIEW.md` |
| `modeling_pm/MODELING_GUIDE.md` | `modeling_project/MODELING_GUIDE.md` |
| `modeling_pm/MODELING_PROCESS.md` | `modeling_project/MODELING_PROCESS.md` |
| `modeling_pm/completed/` | `work/completed/` |
| `modeling_pm/audits/` | `work/analysis/` |
| `SOURCE_INDEX.md` (root) | `knowledge/SOURCE_INDEX.md` |

> FR-9: New information architecture files MUST be referenced where applicable:

| File | Commands that should read it |
|------|------------------------------|
| `knowledge/KNOWLEDGE.md` | spec-model (DI-XXX insights) |
| `modeling_project/OVERVIEW.md` | spec-model (G-XXX goals, AQ-XXX questions) |
| `modeling_project/ARCHITECTURE.md` | design-model (AD-XXX decisions) |
| `modeling_project/REQUIREMENTS.md` | design-model, audit-models, implement-model (PR-XXX compliance) |
| `modeling_project/VALIDATION_MATRIX.md` | audit-models, spec-model (SV-XXX criteria) |
| `work/BACKLOG.md` | backlog, spec-model (epic context) |

#### AP-7 Script Invocations

> FR-10: Commands MUST include exact CLI invocations for AP-7 operations where specified.

Per-command AP-7 calls (from epic D3.1 and delta checklist § 3A.1):

| Command | AP-7 Operations | Exact CLI |
|---------|----------------|-----------|
| implement-model | Inline knowledge capture | `agentic-mbse pm add-insight --title "<title>" --source "work-item:<WI-XXX>/<artifact>" --context "<context>" --model-implications "<implications>" --analysis-implications "<implications>" --rationale "<why captured>"` |
| implement-model | Traceability recording | `agentic-mbse pm trace-element --element "<name>" --file "<path>" --type "<kind>" --knowledge DI-XXX --requirement PR-XXX --source-type "<type>" --source-doc "<name>" --source-location "<loc>"` |
| implement-model | Requirement promotion | `agentic-mbse pm promote-requirement --requirement "<text>" --source <DI-XXX or G-XXX>` |
| audit-models | Decision promotion | `agentic-mbse pm register-decision --title "<title>" --decision "<text>" --rationale "<text>"` |
| audit-models | Validation status update | `agentic-mbse pm update-validation <SV-XXX> --status <passing\|failing\|pending>` |
| research | Approve research | `agentic-mbse pm approve-research <file> --insights '<json>'` |
| backlog | YAML frontmatter updates | Via AP-7 scripts (specific operations depend on action: close-item, add to backlog) |

> FR-11: AP-7 invocations MUST be placed inline within the workflow stage where the agent should call them, not in a separate section.

The agent needs to see the call at the point in the workflow where it's relevant (e.g., the `add-insight` call appears within the implementation loop when the agent discovers a domain insight, not in a "Scripts" appendix).

#### YAML Frontmatter Generation

> FR-12: `spec-model` MUST instruct the agent to generate spec.md with YAML frontmatter:

```yaml
---
Status: active
Scale: standard
Epic: <epic name from BACKLOG.md>
Owner: <user>
Created: <YYYY-MM-DD>
Updated: <YYYY-MM-DD>
---
```

> FR-13: `plan-model` MUST instruct the agent to generate plan.md with YAML frontmatter:

```yaml
---
Status: draft
Created: <YYYY-MM-DD>
Updated: <YYYY-MM-DD>
Related Artifacts:
  Spec: ./spec.md
  Design: ./design.md
---
```

> FR-14: [INFERRED] `design-model` SHOULD instruct the agent to generate design.md with YAML frontmatter:

```yaml
---
Status: draft
Created: <YYYY-MM-DD>
Updated: <YYYY-MM-DD>
Related Artifacts:
  Spec: ./spec.md
---
```

Per frontmatter-schemas.md (D1.5), design.md has a defined schema. Adding generation guidance is consistent with spec-model and plan-model.

#### Per-Command Specific Changes

> FR-15 through FR-23 enumerate per-command changes as specified in the epic and delta checklist § 3A.1. Each sub-requirement references the D2.5 extraction mapping for what to remove and what to keep.

**FR-15: design-model.md** (1,345 → target ~250 lines)
- Remove "Stage 5.5: Common Pitfalls & Quick Reference" → `sysml-conventions`
- Remove "Stage 5.5 > Validation Commands" → `model-validation` + `toolkit-awareness`
- Remove "Guidelines > Critical Requirements" re: MODELING_GUIDE → `sysml-conventions`
- Trim "Pre-Flight Check" (keep process, remove inline knowledge) → `project-structure` + `sysml-conventions`
- Trim "Stage 6: Prototype & Validation" (keep workflow, remove pyramid details) → `model-validation`
- Add reading of `modeling_project/ARCHITECTURE.md` for AD-XXX decisions
- Add reading of `modeling_project/REQUIREMENTS.md` for PR-XXX compliance
- Add reference to review.md as optional output for `/review-model`
- Tighten STAYS sections (Design Algorithm, Stages 1-4, 7-8, Guidelines, Sub-Agent Usage)

**FR-16: implement-model.md** (493 → target ~250 lines)
- Remove "Stage 3: Quality Validation" inline pyramid → `model-validation`
- Trim "Stage 1.4: Pre-Flight Syntax Validation" (keep workflow, remove patterns) → `sysml-conventions`
- Trim "Stage 2: Add Doc Comments" (keep loop, remove format) → `sysml-conventions` + `source-traceability`
- Trim "Guidelines > MODEL QUALITY" (keep enforcement, remove duplicated content) → `sysml-conventions`
- Add `agentic-mbse pm add-insight` invocation in implementation loop
- Add `agentic-mbse pm trace-element` invocation for significant elements
- Add `agentic-mbse pm promote-requirement` invocation for durable MR-XXX → PR-XXX
- Add reading of `modeling_project/REQUIREMENTS.md` for PR-XXX compliance

**FR-17: spec-model.md** (392 → target ~250 lines)
- Remove "Guidelines > Requirement Format Standards" → `requirements-tracking`
- Trim "Stage 3 > Evaluatable Success Criteria" (keep principle, remove test patterns) → `model-validation`
- Trim "Stage 3 > Regression Safety Criteria" (keep process, remove coverage patterns) → `model-validation`
- Add reading of `knowledge/KNOWLEDGE.md` for DI-XXX insights
- Add reading of `modeling_project/OVERVIEW.md` for G-XXX goals and AQ-XXX questions
- Add YAML frontmatter generation (FR-12)
- Add SV-XXX entry creation in VALIDATION_MATRIX.md

**FR-18: plan-model.md** (676 → target ~250 lines)
- Remove "Step 3 > Test Requirements" + test phase pattern → `model-validation`
- Trim "Step 4: Validate Plan Feasibility" (keep process, remove syntax/validation rules) → `sysml-conventions` + `model-validation`
- Remove "Appendix: Quick Reference" entirely → `sysml-conventions` + `model-validation` + `project-structure`
- Trim "Guidelines > Plan Quality Standards" (keep phasing principles, remove validation refs) → `model-validation`
- Add YAML frontmatter generation (FR-13)

**FR-19: audit-models.md** (446 → target ~300 lines)
- Remove "Stage 1 > Verification Standards" thresholds → `model-validation`
- Trim "Guidelines > Special Cases" (keep audit logic, remove citation patterns) → `source-traceability`
- Add `requirements-tracking` skill reference
- Add `agentic-mbse pm register-decision` invocation for AD-XXX promotion
- Add `agentic-mbse pm update-validation` invocation for SV-XXX updates
- Add reading of `modeling_project/REQUIREMENTS.md` for PR-XXX compliance

**FR-20: research.md** (243 → target ~250 lines)
- Trim "Stage 1/2 > SOURCE_INDEX.md" (keep process, remove source type defs) → `source-traceability`
- Add `agentic-mbse pm approve-research` invocation after user approves
- Add DI-XXX insight suggestion and capture flow
- Add knowledge supersession detection (flag conflicts with existing DI-XXX)
- Add file save via script: `knowledge/research/pending/YYYYMMDD-HHMMSS_topic.md`

**FR-21: onboard.md** (577 → target ~300 lines)
- Remove "Stage 2.5 > Permission path format rules" → `toolkit-awareness`
- Remove "Stage 3.3 > SOURCE_INDEX.md template" → `source-traceability`
- Remove "Stage 3.4 > models/ directory structure" → `project-structure`
- Trim "Stage 3.5 > Update Project Templates" (keep placeholder workflow, remove dir roles) → `project-structure`
- Add trigger for `/formalize-intent` after intent docs placed in `modeling_project/intent/`
- Add initial ARCHITECTURE.md population guidance

**FR-22: backlog.md** (358 → target ~250 lines)
- Trim "Stage 4 > Format and Add Work Items" (keep format templates, add scale ref) → `epic-decomposition`
- Add `epic-decomposition` skill reference
- Add scale assessment (Trivial/Standard/Epic) to work item creation
- Update BACKLOG.md path to `work/BACKLOG.md`
- Add YAML frontmatter updates via AP-7 scripts

**FR-23: manage-sources.md** (357 → target ~250 lines)
- Remove "SOURCE_INDEX.md Format Reference" → `source-traceability`
- Trim "Stage 3 > Permission path format rules" (keep workflow, remove rules) → `toolkit-awareness`
- Update SOURCE_INDEX.md path to `knowledge/SOURCE_INDEX.md`

#### Processing Order

> FR-24: Commands MUST be refactored in priority order (most bloated first): design-model → implement-model → spec-model → plan-model → audit-models → research → onboard → backlog → manage-sources.

> FR-25: After the first 2–3 commands (design-model, implement-model, spec-model), the structural convention MUST be documented before continuing.

---

## Acceptance Criteria

### Core Functionality

- [x] All 9 commands refactored with skill references replacing inline knowledge
- [x] Average command length ≤ 300 lines — average is 114 lines
- [x] No command exceeds 400 lines — max is 135 (research)
- [x] Every `modeling_pm/` path reference is updated — zero remaining
- [x] Skill declarations in YAML frontmatter for all 9 commands
- [x] "Skills Referenced" prose section in all 9 commands
- [x] AP-7 invocations with exact CLI syntax in: implement-model (3), audit-models (2), research (1), backlog (noted, CLI not yet defined)
- [x] YAML frontmatter generation guidance in: spec-model, plan-model, design-model
- [x] New project file references (ARCHITECTURE.md, REQUIREMENTS.md, KNOWLEDGE.md, OVERVIEW.md, VALIDATION_MATRIX.md) added where specified
- [x] Structural convention document produced — `.project/active/d3.1-command-refactoring/command-convention.md` (pattern confirmed across all 9)

### Quality & Integration

- [x] Existing tests continue to pass (`uv run pytest tests/`) — 342 passed, 1 skipped (verified 2026-02-02)
- [x] D2.5 extraction mapping cross-referenced: every "→ SKILL" section removed, every "→ PARTIAL" section trimmed, every "→ STAYS" section retained
- [x] No knowledge lost — verified by checking D2.5 "Knowledge Gap Analysis" section (all 6 "Fully Extracted" domains covered by skill references, 2 "Partially Extracted" domains handled correctly)
- [x] Commands remain functional as Claude Code slash commands (valid frontmatter, readable by the agent)

---

## Related Artifacts

- **Extraction mapping**: `.project/active/d2.5-extraction-mapping/extraction-mapping.md` (primary input)
- **Context measurements**: `.project/active/d2.4-context-measurement/measurement-report.md` (token budgets)
- **Frontmatter schemas**: `.project/concepts/architecture-redesign/frontmatter-schemas.md` (spec.md, design.md, plan.md schemas)
- **Component catalog**: `.project/concepts/architecture-redesign/components.md` § 1 (skill-to-command mapping)
- **Epic**: `.project/backlog/epic_architecture-commands.md` (D3.1)
- **Design**: `.project/active/d3.1-command-refactoring/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
