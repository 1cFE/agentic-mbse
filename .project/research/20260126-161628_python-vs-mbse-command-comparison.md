---
date: 2026-01-26T16:16:28-07:00
researcher: Claude
topic: "Comprehensive comparison of Python agentic coding system vs MBSE textual modeling system"
tags: [research, commands, comparison, project-management, mbse, refactoring]
status: complete
last_updated: 2026-01-26
---

# Research: Python vs MBSE Agentic Coding System Comparison

**Date**: 2026-01-26 16:16:28 MST
**Researcher**: Claude
**Research Type**: Architecture / Codebase / Process Comparison

## Research Question

Comprehensive comparison between the Python agentic coding system (`/home/reid/agentic-project-init/`) and the MBSE textual modeling system (`/home/reid/1cfe/agentic-mbse/claude/`) to inform revision of the MBSE commands, addition of new commands, and improvement of project management techniques.

## Executive Summary

| Aspect | Python System | MBSE System | Gap Analysis |
|--------|---------------|-------------|--------------|
| **Total Commands** | 16 commands | 9 commands | MBSE missing 7 command types |
| **Average Command Length** | 237 lines | 476 lines | MBSE commands 2x longer (bloated) |
| **Workflow Stages** | 2-6 stages | 4-8 stages | MBSE overly complex |
| **Project Management** | Comprehensive PM system | Lightweight backlog | MBSE lacks mature PM |
| **Sub-Agent Usage** | General-purpose (Explore, Task) | Domain-specific (kerml-expert, sysml-expert, etc.) | Both mature |
| **Validation Integration** | Test-first approach | 8-level quality pyramid | Both mature |
| **Maturity** | Highly refined, battle-tested | Evolved but inconsistent | MBSE needs harmonization |

## Detailed Findings

### 1. Command Inventory Comparison

#### Python System Commands (16 total, ~3,800 lines)

| Command | Lines | Purpose | Stages |
|---------|-------|---------|--------|
| `_my_spec` | 255 | Requirements definition | 2 |
| `_my_design` | 314 | Technical design | 3 (iterative cycle) |
| `_my_plan` | 368 | Implementation planning | 3 |
| `_my_implement` | 185 | Execute implementation | 3 |
| `_my_code_review` | 466 | Audit implementation | 6 |
| `_my_code_quality` | 243 | Quality checks | 6 |
| `_my_review_design` | 195 | Design document review | 4 |
| `_my_project_manage` | 500 | Multi-mode PM (status, decompose, close, backlog) | Multi-mode |
| `_my_project_find` | 142 | Quick context lookup | N/A |
| `_my_git_manage` | 563 | Git/worktree operations | Multi-action |
| `_my_research` | 169 | Codebase exploration | 4 |
| `_my_quick_edit` | 102 | Small changes | 4 |
| `_my_capture` | 45 | Mark conversation for review | N/A |
| `_my_memorize` | 82 | Create memory artifact | 8 |
| `_my_recall` | 55 | Retrieve past conversations | N/A |
| `_my_audit_implementation` | 42 | Audit completed phases | 4 |

**Average lines per command: 237**

#### MBSE System Commands (9 total, ~4,281 lines)

| Command | Lines | Purpose | Stages |
|---------|-------|---------|--------|
| `spec-model` | 393 | Model requirements (MR-XXX format) | 4 |
| `design-model` | 1,345 | Semantic model design + prototyping | 8+ |
| `plan-model` | 676 | Refinement planning | 4 |
| `implement-model` | 493 | Execute model refinement | 4 |
| `audit-models` | 446 | Verify against baseline | 5 |
| `research` | 243 | Domain exploration | 4 |
| `manage-sources` | 357 | SOURCE_INDEX.md lifecycle | 4 |
| `backlog` | 359 | Work item management (2 modes) | 2 modes |
| `onboard` | 578 | Project setup | 5 |

**Average lines per command: 476** (2x Python average)

### 2. Command Structure Comparison

#### Spec Commands: `_my_spec` (255 lines) vs `spec-model` (393 lines)

| Aspect | Python (_my_spec) | MBSE (spec-model) | Assessment |
|--------|-------------------|-------------------|------------|
| **Stages** | 2 (Capture, Document) | 4 (Context, Scoping, Definition, Document) | MBSE more complex |
| **User interaction** | Scoping → Questions → Investigation Offer | Multiple confirmation checkpoints | MBSE has more gates |
| **Requirements format** | FR-1, FR-2 (simple) | MR-XXX with EARS format, Type, Rationale, Validation | MBSE more formal |
| **Success criteria** | Checkbox acceptance criteria | Evaluatable + machine-checkable criteria | MBSE more rigorous |
| **Unique Python** | Codebase investigation offer, RFC 2119 keywords | - | Python more user-centric |
| **Unique MBSE** | - | Regression safety criteria, Library vs Designs awareness | MBSE domain-aware |

**Key Difference**: Python spec is lean and user-centric; MBSE spec is formal and domain-aware but verbose.

#### Design Commands: `_my_design` (314 lines) vs `design-model` (1,345 lines)

| Aspect | Python (_my_design) | MBSE (design-model) | Assessment |
|--------|-------------------|-------------------|------------|
| **Length** | 314 lines | 1,345 lines | MBSE 4.3x longer |
| **Stages** | 3 (Setup, Research-Refine-Reflect cycle, Finalization) | 8+ (Pre-flight, Outline, Research, Alternatives, Detail, Finalize, Prototype, Iterate, Approve) | MBSE much more complex |
| **Iteration model** | RESEARCH → REFINE → REFLECT loop | Linear with iteration stages | Python more elegant |
| **Prototyping** | None (deferred to implement) | Embedded prototyping (Stages 6-8) | MBSE validates earlier |
| **Alternatives** | Section when uncertain | Mandatory Stage 3 | Similar |
| **Output** | design.md | design.md + validated prototype + validation report | MBSE delivers more |

**Key Difference**: Python design is a pure design document; MBSE design includes actual prototyping and validation. This is a **major workflow difference** - MBSE front-loads work that Python defers.

#### Plan Commands: `_my_plan` (368 lines) vs `plan-model` (676 lines)

| Aspect | Python (_my_plan) | MBSE (plan-model) | Assessment |
|--------|-------------------|-------------------|------------|
| **Input** | Spec + Design | Design + Validated Prototype | MBSE has more input |
| **Philosophy** | De-risk early, test-first | Refine prototype to production | Different goals |
| **Test integration** | Test stencils per phase | Minimal (relies on validation pyramid) | Python stronger |
| **Duplication avoidance** | "Reference design.md extensively" | Similar principle | Both good |
| **Feasibility check** | Implicit in phasing | Explicit Step 4: Validate Plan Feasibility | MBSE more explicit |
| **Parallelization** | Not addressed | Sub-agent parallelization strategy section | MBSE has this |

**Key Difference**: Python plan is test-centric; MBSE plan is refinement-centric since prototype already exists from design.

#### Implement Commands: `_my_implement` (185 lines) vs `implement-model` (493 lines)

| Aspect | Python (_my_implement) | MBSE (implement-model) | Assessment |
|--------|-------------------|-------------------|------------|
| **Length** | 185 lines | 493 lines | MBSE 2.7x longer |
| **Stage 0** | MANDATORY understanding phase | Skipped (assumes understood) | Python more careful |
| **Progress tracking** | TodoWrite + plan checkboxes | Same + traceability matrix | MBSE adds traceability |
| **Validation** | Run tests per CLAUDE.md | 8-level quality pyramid | Both comprehensive |
| **Batch editing** | Not addressed | Detailed batch editing patterns | MBSE has efficiency guidance |
| **Critical thinking** | "Do NOT blindly follow the plan" | Less emphasized | Python stronger here |

**Key Difference**: Python emphasizes understanding-before-action; MBSE has more mechanical efficiency patterns.

### 3. Commands Missing from MBSE System

| Python Command | Purpose | MBSE Need |
|----------------|---------|-----------|
| `_my_code_review` | Comprehensive audit against spec/design | **HIGH** - `/audit-models` is codebase-comparison only |
| `_my_code_quality` | Run and fix quality issues | **MEDIUM** - Validation pyramid exists but no fix workflow |
| `_my_review_design` | Critical design review (6 dimensions) | **HIGH** - No design review before implementation |
| `_my_project_manage` | Multi-mode PM with status, decompose, close | **HIGH** - Only have `/backlog` for add/clear |
| `_my_project_find` | Quick context lookup | **MEDIUM** - Useful for orientation |
| `_my_git_manage` | Git/worktree operations | **LOW** - Less relevant for modeling |
| `_my_quick_edit` | Small changes bypass | **MEDIUM** - Not everything needs full workflow |
| Memory commands | Capture, memorize, recall | **LOW** - Nice to have |

### 4. Project Management Comparison

#### Python System PM Structure

```
.project/
├── CURRENT_WORK.md              # Active work tracker
├── EPIC_GUIDE.md                # Decomposition methodology (328 lines!)
├── epic_template.md             # Template for new epics
├── active/
│   └── {item_name}/
│       ├── spec.md
│       ├── design.md
│       └── plan.md
├── backlog/
│   ├── BACKLOG.md               # Prioritized epic list
│   └── epic_*.md                # Individual epic files
├── completed/
│   ├── {YYYYMMDD}_{item_name}/  # Archived items
│   └── CHANGELOG.md
├── research/
├── reports/
└── memories/
```

**Key Features**:
- **EPIC_GUIDE.md**: 328-line decomposition methodology with Goldilocks principle
- **Hierarchical numbering**: 1, 2, 3 or 4.1, 4.2 for parts + items
- **Status flow**: Draft → Ready → In Progress → Complete
- **Priority system**: P0-P3 (4 tiers)
- **Multi-mode project management command**: status, decompose, close, backlog

#### MBSE System PM Structure

```
modeling_pm/
├── OVERVIEW.md                  # Project scope & goals
├── MODELING_GUIDE.md            # SysML conventions
├── MODELING_PROCESS.md          # Workflow methodology
├── active/                      # Currently worked features
├── backlog/
│   └── BACKLOG.md               # Simple priority list
└── completed/
    └── {YYYYMMDD}_{feature}/    # Archived features
```

**Key Features**:
- **Lightweight**: No epic guide, no epic template, no multi-mode PM
- **Backlog command**: Only add and clear modes
- **Missing**: Status reporting, epic decomposition, close workflow

#### PM Gap Analysis

| Feature | Python | MBSE | Gap |
|---------|--------|------|-----|
| Epic decomposition guide | 328 lines, comprehensive | None | **CRITICAL** |
| Epic template | 8 sections, detailed | None | **CRITICAL** |
| Status reporting | Full status with gap analysis | None | **HIGH** |
| Item decomposition | Goldilocks principle, task types | None | **HIGH** |
| Multi-mode PM command | 4 modes | 2 modes (add/clear only) | **HIGH** |
| Project find/context | Quick lookup command | None | **MEDIUM** |
| Archive workflow | CHANGELOG.md, completion notes | Minimal | **MEDIUM** |

### 5. Language and Style Comparison

#### Command Header Pattern

**Python (consistent)**:
```markdown
# [Command] Command

**Purpose:** [Single line]
**Input:** [File/data expected]
**Output:** [File/artifact produced]

## Overview
[2-3 sentences explaining role]
```

**MBSE (inconsistent)**:
```markdown
# [Command] Model Command

**Purpose:** [Sometimes single line, sometimes multi-line]
**Input:** [Sometimes detailed, sometimes brief]
**Output:** [File path]

## Overview
[Varies from 2 sentences to full paragraphs with bullet lists]
```

#### Stage Naming

| Python | MBSE |
|--------|------|
| Stage 0: Understanding | Stage 1: Plan Analysis |
| Stage 1: Capture | Stage 2: Research |
| Stage 2: Document | Stage 3: Alternatives |
| | Stage 4: Detail |
| | Stage 5: Finalize |
| | Stage 6: Prototype |
| | Stage 7: Iterate |
| | Stage 8: Approve |

**Assessment**: Python uses cleaner, numbered stages with clear purposes. MBSE has too many stages with inconsistent naming.

#### Checkpoint Language

**Python** (concise):
```markdown
**Wait for user approval** before proceeding
```

**MBSE** (verbose):
```markdown
**Wait for user confirmation** before proceeding to the next stage. If user requests changes, incorporate feedback and re-present scope understanding. Only proceed when user explicitly approves.
```

### 6. Validation Integration Comparison

#### Python System

- **Test-first philosophy**: Every plan phase starts with test stencil
- **Continuous verification**: Run tests after each phase
- **Quality checks**: Project-specific via CLAUDE.md commands
- **Manual verification**: Explicit manual test steps in plan

#### MBSE System

- **8-level quality pyramid**: Comprehensive validation levels
- **Prototyping in design**: Validate before planning (Stages 6-8)
- **syside integration**: Parser-based syntax validation
- **ADR-002 compliance**: Architectural decision record checking
- **Traceability matrix**: Automated traceability validation

**Assessment**: Both systems have mature validation. Python is test-centric; MBSE is quality-pyramid-centric. Neither is clearly superior.

### 7. Sub-Agent Usage Comparison

#### Python System

| Agent Type | Purpose | Usage Pattern |
|------------|---------|---------------|
| Explore | Codebase search | `Task(subagent_type="Explore", thoroughness="medium")` |
| general-purpose | Complex analysis | Multi-step investigations |

**Simple, generic approach**: Two agent types cover all needs.

#### MBSE System

| Agent Type | Purpose | Usage Pattern |
|------------|---------|---------------|
| Explore | Codebase/model search | Same as Python |
| general-purpose | Complex analysis | Same as Python |
| kerml-expert | KerML standard library | Function signatures, imports |
| sysml-expert | SysML modeling patterns | Parts, ports, constraints |
| syside-expert | Parser tooling | Expression evaluation |
| sysmlv2-validator | Syntax validation | Error interpretation |

**Domain-specific approach**: Six agent types for specialized SysML knowledge.

**Assessment**: MBSE's domain-specific agents are valuable but add complexity. Consider consolidating to fewer agents with broader scopes.

### 8. Document Template Comparison

#### Spec Template

**Python** (48 lines of structure):
- Business Goals, Why This Matters, Success Criteria, Priority
- Problem Statement (Current State, Desired Outcome)
- Scope (In Scope, Out of Scope, Edge Cases)
- Requirements (FR-1, FR-2, NFR)
- Acceptance Criteria
- Related Artifacts

**MBSE** (118 lines of structure):
- Everything in Python PLUS:
- Modeling Scope, Current State with file paths
- MR-XXX format with Type, Description, Priority, Rationale, Validation
- Evaluatable Success Criteria (human + machine-checkable)
- Regression Safety Criteria
- Assumptions & Risks sections
- Traceability section

**Assessment**: MBSE template is more comprehensive but 2.4x longer. Consider streamlining.

#### Design Template

**Python** (40 lines):
- Overview, Related Artifacts
- Research Findings
- Design Alternatives (if applicable)
- Design Decisions (if applicable)
- Proposed Design (high-level to detailed)
- Potential Risks, Integration Strategy, Validation Approach

**MBSE** (320 lines):
- All Python sections PLUS:
- Current Model State (existing definitions, instances, gaps)
- Detailed model element specifications with SysML code stencils
- Cross-File Bindings table
- Traceability Strategy section
- Implementation Checklist (phased)
- Common Pitfalls & Quick Reference

**Assessment**: MBSE template includes implementation details that arguably belong in plan. Consider separating concerns.

### 9. Key Architectural Patterns

#### Python System Patterns

1. **Iterative Refinement**: RESEARCH → REFINE → REFLECT cycle
2. **Test-First**: Every phase starts with test stencil
3. **User-Centric**: Specs capture user requirements, not engineer assumptions
4. **Progressive Disclosure**: Overview → Details → Tactical
5. **Deviations Tracking**: Document actual vs planned
6. **File:Line References**: Specific code references
7. **Risk Management**: Early identification, mitigation strategies

#### MBSE System Patterns

1. **Front-Loaded Validation**: Prototype in design, refine in implement
2. **Domain-Specific Agents**: kerml-expert, sysml-expert, etc.
3. **Source-Driven**: SOURCE_INDEX.md discovers knowledge sources
4. **Quality Pyramid**: 8-level validation framework
5. **Traceability Matrix**: Automated element tracking
6. **Library vs Designs**: Clear separation pattern

### 10. Complexity Analysis

#### Lines of Code per Concept

| Concept | Python Lines | MBSE Lines | Ratio |
|---------|--------------|------------|-------|
| Explain spec process | ~50 | ~120 | 2.4x |
| Explain design iteration | ~30 | ~150 | 5x |
| Define output template | ~40 | ~320 | 8x |
| Sub-agent usage guidance | ~20 | ~100 | 5x |
| Error handling section | ~15 | ~40 | 2.7x |

**Assessment**: MBSE commands are consistently 2-8x longer for equivalent concepts. This suggests:
- Bloat from accumulated edits over time
- Lack of cross-command consistency
- Over-specification of edge cases

## Recommendations

### Priority 1: Harmonize Command Structure

**Problem**: MBSE commands are 2x longer on average with inconsistent structure.

**Actions**:
1. Adopt Python's consistent header format
2. Reduce stages to 3-4 per command (matching Python)
3. Move detailed examples to separate reference docs
4. Standardize checkpoint/gate language

### Priority 2: Add Missing Commands

**Commands to add** (in order of priority):
1. **`/review-model`** - Design review before implementation (like `_my_review_design`)
2. **`/project-status`** - Multi-mode PM with status reporting (like `_my_project_manage`)
3. **`/quick-model`** - Small changes without full workflow (like `_my_quick_edit`)
4. **`/fix-models`** - Quality issue fixing workflow (like `_my_code_quality`)

### Priority 3: Strengthen Project Management

**Actions**:
1. Create `EPIC_GUIDE.md` for modeling projects
2. Create `epic_template.md` for work item structure
3. Add decompose and close modes to `/backlog`
4. Add status reporting mode
5. Create `/project-find` for quick context

### Priority 4: Refactor Design Command

**Problem**: `design-model` at 1,345 lines is too long and embeds prototyping.

**Options**:
- **Option A**: Keep embedded prototyping but streamline to ~600 lines
- **Option B**: Split into `/design-model` (pure design) + `/prototype-model` (validation)
- **Option C**: Make prototyping optional via flag

**Recommendation**: Option A - embedded prototyping is valuable, but the command needs trimming.

### Priority 5: Add Understanding Phase to Implement

**Problem**: `implement-model` lacks Python's Stage 0 understanding phase.

**Actions**:
1. Add mandatory Stage 0: Understanding Before Action
2. Include codebase exploration offer
3. Add "Do NOT blindly follow the plan" guidance

### Priority 6: Consolidate Sub-Agents

**Problem**: Six agent types add complexity.

**Options**:
- **Option A**: Keep all six (current state)
- **Option B**: Consolidate to three: `sysmlv2-expert` (combines kerml+sysml), `syside-expert`, `sysmlv2-validator`
- **Option C**: Single `sysmlv2-doc-analyzer` that handles all SysML questions

**Recommendation**: Option B - reduces complexity while preserving specialization.

### Priority 7: Template Streamlining

**Actions**:
1. Reduce spec template from 118 to ~70 lines
2. Reduce design template from 320 to ~150 lines
3. Move implementation checklists from design to plan
4. Create separate quick-reference docs for syntax patterns

## Summary Metrics

| Metric | Python | MBSE | Target for MBSE |
|--------|--------|------|-----------------|
| Commands | 16 | 9 | 13 (+4 new) |
| Avg lines/command | 237 | 476 | ~300 |
| Stages per command | 2-6 | 4-8 | 3-5 |
| PM features | Comprehensive | Minimal | Match Python |
| Template lines | ~90 | ~440 | ~200 |

## Open Questions

1. Should prototyping remain embedded in design or become separate command?
2. How to handle the library/designs dichotomy in PM templates?
3. Should MBSE adopt Python's memory commands?
4. How to balance domain-specific detail with command brevity?

## Related Artifacts

- Python commands: `/home/reid/agentic-project-init/claude-pack/commands/`
- MBSE commands: `/home/reid/1cfe/agentic-mbse/claude/commands/`
- Python PM: `/home/reid/agentic-project-init/project-pack/`
- MBSE templates: `/home/reid/1cfe/agentic-mbse/project_templates/`

---

**Next Steps**:
1. Create spec for command harmonization
2. Prioritize missing commands
3. Draft EPIC_GUIDE.md for modeling
4. Refactor design-model.md (~1345 → ~600 lines)
