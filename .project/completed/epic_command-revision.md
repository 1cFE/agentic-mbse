# Epic: MBSE Command System Revision

**Epic ID**: EPIC-CMDREV-001
**Status**: Ready
**Priority**: P1
**Created**: 2026-01-26
**Estimated Effort**: 8-10 days

---

## Executive Summary

Revise the MBSE command system to match the maturity, consistency, and project management capabilities of the Python agentic coding system. This involves harmonizing command structure, adding missing commands, strengthening PM workflows, and streamlining verbose commands.

**Critical Success Factor**: Commands are lean (~300 lines avg vs current ~476), structurally consistent, and support full PM workflow (status, decompose, close).

---

## Why This Epic?

**Current State**:
- MBSE commands average 476 lines vs Python's 237 lines (2x bloat)
- `design-model` is 1,345 lines (4.3x the Python equivalent)
- No design review command before implementation
- PM support is minimal (backlog add/clear only, no status reporting)
- No epic decomposition guide or template for modeling work
- Command structure varies (2-8 stages, inconsistent headers)
- 6 sub-agent types add cognitive overhead

**Future State**:
- Commands average ~300 lines with consistent structure
- New `/review-model` validates designs before implementation
- Full PM workflow with `/project-status` (status, decompose, close modes)
- EPIC_GUIDE.md provides modeling work decomposition methodology
- Sub-agents consolidated from 6 to 3 types
- `/quick-model` supports small changes without full workflow

---

## Success Criteria

- [ ] Average command length reduced from ~476 to ~300 lines
- [ ] All commands follow consistent header/stage format
- [ ] `/review-model` command exists and catches design issues
- [ ] `/project-status` supports status, decompose, close modes
- [ ] EPIC_GUIDE.md exists for modeling work decomposition
- [ ] `design-model` refactored to ~600 lines (from 1,345)
- [ ] Sub-agents consolidated to 3 types
- [ ] `/quick-model` command exists for small changes
- [ ] `implement-model` has Stage 0 understanding phase
- [ ] All existing tests pass

---

## Stages and Backlog Items

This epic is organized into 4 sequential stages. Each stage contains related backlog items that should be completed before moving to the next stage.

### Stage 1: Command Structure Harmonization + Review Model

**Goal**: Establish consistent command structure and add design review capability.

**Why First**: Creates the template that all subsequent work will follow. `/review-model` fills the most critical gap in the workflow.

---

#### Item 1.1: Command Structure Template [1 day]

**Type**: Implementation
**Effort**: 1 day (spec 1h, design 1h, plan 0.5h, execute 5h)
**Dependencies**: None

**Objective**: Define and document a standard command structure template that all MBSE commands will follow.

**Current State**:
- ❌ No documented command template
- ⚠️ Commands vary from 2-8 stages with inconsistent naming
- ⚠️ Headers vary in format and content
- ❌ No standard checkpoint/gate language

**Scope**:
1. **Analyze Python command patterns** - Extract consistent elements from `_my_spec`, `_my_design`, `_my_plan`, `_my_implement`
2. **Define command template**:
   - Standard header format (Purpose, Input, Output)
   - Stage naming convention (3-5 stages max)
   - Checkpoint/gate language patterns
   - Error handling section format
   - Guidelines section format
3. **Document in CLAUDE.md** or create `docs/command-template.md`
4. **Create checklist** for command compliance

**Out of Scope**:
- Actually refactoring existing commands (Items 1.2, 1.3)
- Creating new commands (Item 1.4)

**Success Criteria**:
- [ ] Command template documented with examples
- [ ] Checklist for verifying command compliance
- [ ] Template approved for use in subsequent items

**Deliverables**:
- `.project/active/command-template/spec.md`
- `.project/active/command-template/design.md`
- `docs/command-template.md` or section in CLAUDE.md

---

#### Item 1.2: Harmonize Core Workflow Commands [1.5 days]

**Type**: Implementation
**Effort**: 1.5 days (spec 0.5h, design 1h, plan 0.5h, execute 10h)
**Dependencies**: Item 1.1

**Objective**: Refactor the 4 core workflow commands to follow the new template.

**Current State**:
- ⚠️ `spec-model.md` (393 lines) - verbose, 4 stages
- ⚠️ `plan-model.md` (676 lines) - very verbose, 4 steps + validation
- ⚠️ `implement-model.md` (493 lines) - verbose, 4 stages
- ⚠️ `audit-models.md` (446 lines) - verbose, 5 stages

**Scope**:
1. **spec-model.md** → ~280 lines target
   - Standardize header
   - Consolidate to 3 stages (Context, Requirements, Document)
   - Streamline MR-XXX guidance
2. **plan-model.md** → ~400 lines target
   - Standardize header
   - Consolidate to 3 stages (Read, Phase, Validate)
   - Move detailed examples to reference doc
3. **implement-model.md** → ~350 lines target
   - Standardize header
   - Add Stage 0: Understanding (from Python pattern)
   - Consolidate efficiency patterns
4. **audit-models.md** → ~300 lines target
   - Standardize header
   - Consolidate to 4 stages

**Out of Scope**:
- `design-model.md` (Stage 3)
- Support commands (research, manage-sources, backlog, onboard)

**Success Criteria**:
- [ ] All 4 commands follow template from Item 1.1
- [ ] Combined line count reduced by 30%+ (2,008 → ~1,330)
- [ ] No functionality removed (verified by walkthrough)
- [ ] implement-model has Stage 0 understanding phase

**Deliverables**:
- `.project/active/core-command-harmonization/spec.md`
- `.project/active/core-command-harmonization/plan.md`
- Updated `claude/commands/{spec,plan,implement,audit}-model.md`

---

#### Item 1.3: Harmonize Support Commands [1 day]

**Type**: Implementation
**Effort**: 1 day (spec 0.5h, design 0.5h, plan 0.5h, execute 5.5h)
**Dependencies**: Item 1.1

**Objective**: Refactor the 4 support commands to follow the new template.

**Current State**:
- ⚠️ `research.md` (243 lines) - reasonably sized but inconsistent structure
- ⚠️ `manage-sources.md` (357 lines) - verbose
- ⚠️ `backlog.md` (359 lines) - verbose for 2 modes
- ⚠️ `onboard.md` (578 lines) - very verbose

**Scope**:
1. **research.md** → ~180 lines target
2. **manage-sources.md** → ~220 lines target
3. **backlog.md** → ~220 lines target
4. **onboard.md** → ~350 lines target

**Out of Scope**:
- Adding new modes to backlog (Stage 2)
- Core workflow commands (Item 1.2)

**Success Criteria**:
- [ ] All 4 commands follow template from Item 1.1
- [ ] Combined line count reduced by 35%+ (1,537 → ~970)
- [ ] No functionality removed

**Deliverables**:
- `.project/active/support-command-harmonization/spec.md`
- `.project/active/support-command-harmonization/plan.md`
- Updated `claude/commands/{research,manage-sources,backlog,onboard}.md`

---

#### Item 1.4: Create Review Model Command [1 day]

**Type**: Implementation
**Effort**: 1 day (spec 1h, design 2h, plan 0.5h, execute 4.5h)
**Dependencies**: Item 1.1

**Objective**: Create `/review-model` command for design validation before implementation, adapted from Python's `_my_review_design`.

**Current State**:
- ❌ No design review command exists
- ⚠️ Design issues discovered during implementation (expensive)
- ✅ Python `_my_review_design` provides proven pattern

**Scope**:
1. **Adapt 6-dimensional review** for modeling context:
   - Spec Compliance - Does design address all MR-XXX requirements?
   - Pattern Consistency - Does it follow MODELING_GUIDE patterns?
   - Library/Designs Separation - Are definitions vs usages correct?
   - Traceability Completeness - Are all sources cited?
   - Constraint Coverage - Are physics/engineering limits defined?
   - Validation Readiness - Will it pass quality pyramid levels 1-3?
2. **Define review output format** - Pass/Concerns/Fail per dimension
3. **Follow command template** from Item 1.1

**Out of Scope**:
- Automated validation (relies on human review)
- Integration with CI/CD

**Success Criteria**:
- [ ] Command follows template (~250 lines)
- [ ] 6 review dimensions defined with clear criteria
- [ ] Output format enables actionable feedback
- [ ] Tested on existing design document

**Deliverables**:
- `.project/active/review-model-command/spec.md`
- `.project/active/review-model-command/design.md`
- `.project/active/review-model-command/plan.md`
- New `claude/commands/review-model.md`

---

### Stage 2: Project Management Enhancement

**Goal**: Add comprehensive PM support for modeling projects.

**Why Second**: Establishes the PM foundation (EPIC_GUIDE) that the PM command will implement. Depends on command template from Stage 1.

---

#### Item 2.1: EPIC_GUIDE and Epic Template [1 day]

**Type**: Implementation
**Effort**: 1 day (spec 1h, design 1.5h, plan 0.5h, execute 5h)
**Dependencies**: Stage 1 complete

**Objective**: Create EPIC_GUIDE.md and epic_template.md for modeling project management, adapted from Python equivalents.

**Current State**:
- ❌ No epic decomposition guide for modeling
- ❌ No epic template
- ✅ Python EPIC_GUIDE.md (328 lines) provides proven pattern
- ✅ Python epic_template.md (131 lines) provides structure

**Scope**:
1. **Adapt EPIC_GUIDE.md** for modeling context:
   - Goldilocks principle (0.5-2 days per item)
   - Task types for modeling: Research, Modeling, Integration, Validation
   - Workflow cycle estimates adapted for modeling
   - Decomposition process
   - Anti-patterns
2. **Adapt epic_template.md** for modeling:
   - Add modeling-specific sections (affected models, validation approach)
   - Keep core structure from Python
3. **Add to project_templates/** for installation via `agentic-mbse init`

**Out of Scope**:
- PM command implementation (Item 2.2)

**Success Criteria**:
- [ ] EPIC_GUIDE.md explains modeling work decomposition
- [ ] epic_template.md provides complete epic structure
- [ ] Both added to project_templates/
- [ ] CLI updated to install new templates

**Deliverables**:
- `.project/active/pm-templates/spec.md`
- `.project/active/pm-templates/design.md`
- `project_templates/EPIC_GUIDE.md.template`
- `project_templates/epic_template.md.template`
- Updated `src/agentic_mbse/cli/__init__.py`

---

#### Item 2.2: Project Status Command [1.5 days]

**Type**: Implementation
**Effort**: 1.5 days (spec 1h, design 2h, plan 1h, execute 8h)
**Dependencies**: Item 2.1

**Objective**: Create `/project-status` command with status, decompose, and close modes, adapted from Python's `_my_project_manage`.

**Current State**:
- ⚠️ `/backlog` only has add and clear modes
- ❌ No status reporting with gap analysis
- ❌ No epic decomposition workflow
- ❌ No work item close/archive workflow
- ✅ Python `_my_project_manage` (500 lines) provides proven pattern

**Scope**:
1. **Status mode** (default):
   - Current work summary
   - Recent completions
   - Blockers and risks
   - Gap analysis
   - Recommended next steps
2. **Decompose mode** (`/project-status decompose <epic>`):
   - Read epic file
   - Apply EPIC_GUIDE principles
   - Generate backlog items
   - User review and approval
3. **Close mode** (`/project-status close [item]`):
   - Detect completed items (via plan.md checkboxes)
   - Archive to completed/
   - Update CHANGELOG
   - Update backlog status

**Out of Scope**:
- Git worktree management (not needed for modeling)
- Memory commands

**Success Criteria**:
- [ ] Command follows template (~400 lines)
- [ ] Status mode produces actionable report
- [ ] Decompose mode creates well-sized items per EPIC_GUIDE
- [ ] Close mode properly archives work
- [ ] All 3 modes tested

**Deliverables**:
- `.project/active/project-status-command/spec.md`
- `.project/active/project-status-command/design.md`
- `.project/active/project-status-command/plan.md`
- New `claude/commands/project-status.md`

---

### Stage 3: Design Command Refactoring + Sub-Agent Consolidation

**Goal**: Streamline the most verbose command and simplify agent ecosystem.

**Why Third**: Depends on command template from Stage 1. Most complex refactoring, benefits from patterns established in earlier stages.

---

#### Item 3.1: Design Model Command Refactoring [1.5 days]

**Type**: Implementation
**Effort**: 1.5 days (spec 1h, design 2h, plan 1h, execute 8h)
**Dependencies**: Stage 1 complete

**Objective**: Refactor `design-model` from 1,345 lines to ~600 lines while maintaining functionality.

**Current State**:
- ❌ `design-model.md` is 1,345 lines (4.3x Python equivalent)
- ⚠️ 8+ stages vs Python's 3
- ⚠️ Embedded examples that could be reference docs
- ⚠️ Verbose sub-agent usage guidance
- ✅ Embedded prototyping is valuable (keep)

**Scope**:
1. **Analyze content** - Identify duplicates, verbose sections, extractable examples
2. **Reduce stages** from 8+ to 4-5:
   - Pre-flight + Setup → Stage 1: Setup
   - Research + Alternatives → Stage 2: Research & Alternatives
   - Detail + Finalize → Stage 3: Design Specification
   - Prototype + Iterate + Approve → Stage 4: Validate & Approve
3. **Extract detailed examples** to `docs/command-reference/design-model-examples.md`
4. **Streamline sub-agent guidance** - consolidate with Item 3.2
5. **Apply command template** from Stage 1

**Out of Scope**:
- Changing the design-then-prototype workflow
- Sub-agent consolidation (Item 3.2)

**Success Criteria**:
- [ ] Command reduced to ~600 lines (55% reduction)
- [ ] 4-5 stages with clear boundaries
- [ ] All functionality preserved (verified by walkthrough)
- [ ] Examples extracted to reference doc

**Deliverables**:
- `.project/active/design-model-refactor/spec.md`
- `.project/active/design-model-refactor/design.md`
- `.project/active/design-model-refactor/plan.md`
- Refactored `claude/commands/design-model.md`
- New `docs/command-reference/design-model-examples.md`

---

#### Item 3.2: Sub-Agent Consolidation [1 day]

**Type**: Implementation
**Effort**: 1 day (spec 0.5h, design 1.5h, plan 0.5h, execute 5.5h)
**Dependencies**: Item 3.1

**Objective**: Consolidate sub-agents from 6 types to 3 types.

**Current State**:
- ⚠️ 6 sub-agent types: kerml-expert, sysml-expert, syside-expert, sysmlv2-validator, Explore, general-purpose
- ⚠️ kerml-expert and sysml-expert overlap significantly
- ✅ sysmlv2-doc-analyzer already combines documentation search
- ⚠️ Commands reference agents inconsistently

**Scope**:
1. **Define consolidated agent set**:
   - `sysmlv2-doc-analyzer` (existing) - combines kerml + sysml documentation search
   - `syside-expert` - parser/tooling questions
   - `sysmlv2-validator` - syntax validation and error interpretation
   - (Explore and general-purpose are system agents, not MBSE-specific)
2. **Update agent definitions** in `claude/agents/`
3. **Update all commands** to reference consolidated agents
4. **Document agent usage** - when to use which agent

**Out of Scope**:
- Changing agent implementation (just consolidation)
- System agents (Explore, general-purpose)

**Success Criteria**:
- [ ] MBSE-specific agents reduced from 4 to 3
- [ ] All commands updated to use consolidated agents
- [ ] Agent usage documented clearly
- [ ] No functionality lost

**Deliverables**:
- `.project/active/agent-consolidation/spec.md`
- `.project/active/agent-consolidation/design.md`
- Updated `claude/agents/sysmlv2-doc-analyzer.md` (if needed)
- Removed/archived `claude/agents/kerml-expert.md`, `claude/agents/sysml-expert.md`
- Updated agent references in all commands

---

### Stage 4: Additional Improvements

**Goal**: Complete remaining improvements from research recommendations.

**Why Last**: Lower priority items that build on foundation from Stages 1-3.

---

#### Item 4.1: Quick Model Command [1 day]

**Type**: Implementation
**Effort**: 1 day (spec 0.5h, design 1h, plan 0.5h, execute 6h)
**Dependencies**: Stage 1 complete

**Objective**: Create `/quick-model` command for small changes without full workflow, adapted from Python's `_my_quick_edit`.

**Current State**:
- ❌ No lightweight editing path
- ⚠️ Small changes require full spec→design→plan→implement
- ✅ Python `_my_quick_edit` (102 lines) provides proven pattern

**Scope**:
1. **Define when to use** - changes under 3 hours, single file, clear scope
2. **Define when NOT to use** - multi-file, architectural changes, new definitions
3. **Streamlined workflow**:
   - Understand objective
   - Optional: quick plan
   - Execute with validation
   - Document changes
4. **Still requires validation pass** - no shortcuts on quality

**Out of Scope**:
- Skipping validation
- Multi-file changes

**Success Criteria**:
- [ ] Command follows template (~120 lines)
- [ ] Clear criteria for when to use
- [ ] Validation still required
- [ ] Tested on small change scenario

**Deliverables**:
- `.project/active/quick-model-command/spec.md`
- `.project/active/quick-model-command/design.md`
- New `claude/commands/quick-model.md`

---

#### Item 4.2: Template Streamlining [0.5 days]

**Type**: Implementation
**Effort**: 0.5 days (spec 0.5h, design 0.5h, plan 0h, execute 3h)
**Dependencies**: Stages 1-3 complete

**Objective**: Streamline spec and design output templates embedded in commands.

**Current State**:
- ⚠️ Spec template in spec-model.md is ~118 lines of structure
- ⚠️ Design template in design-model.md is ~320 lines of structure
- ⚠️ Implementation checklists in design template belong in plan

**Scope**:
1. **Streamline spec template** → ~70 lines
   - Remove redundant sections
   - Consolidate metadata
2. **Streamline design template** → ~150 lines
   - Move implementation checklists to plan
   - Reduce verbose sections
3. **Update commands** with streamlined templates

**Out of Scope**:
- project_templates/ files (user-owned, different concern)

**Success Criteria**:
- [ ] Spec template reduced to ~70 lines
- [ ] Design template reduced to ~150 lines
- [ ] No critical information removed
- [ ] Implementation checklists in plan only

**Deliverables**:
- `.project/active/template-streamlining/spec.md`
- Updated templates in `claude/commands/spec-model.md`
- Updated templates in `claude/commands/design-model.md`

---

## Dependencies

**External**:
- None

**Internal**:
- Research complete: `.project/research/20260126-161628_python-vs-mbse-command-comparison.md`

**Stage Dependency Graph**:
```
Stage 1: Command Harmonization + Review Model
├── Item 1.1: Command Template (no deps)
├── Item 1.2: Core Commands (depends on 1.1)
├── Item 1.3: Support Commands (depends on 1.1)
└── Item 1.4: Review Model (depends on 1.1)

Stage 2: PM Enhancement (depends on Stage 1)
├── Item 2.1: EPIC_GUIDE + Template (depends on Stage 1)
└── Item 2.2: Project Status Command (depends on 2.1)

Stage 3: Design Refactor + Agents (depends on Stage 1)
├── Item 3.1: Design Model Refactor (depends on Stage 1)
└── Item 3.2: Agent Consolidation (depends on 3.1)

Stage 4: Additional Improvements (depends on Stages 1-3)
├── Item 4.1: Quick Model Command (depends on Stage 1)
└── Item 4.2: Template Streamlining (depends on Stages 1-3)
```

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Removing content breaks functionality | High | Manual walkthrough after each refactor; keep reference docs |
| Sub-agent consolidation confuses users | Medium | Clear migration notes; update all command references |
| PM changes conflict with existing workflows | Medium | Make new modes additive, not breaking |
| Scope creep from "one more improvement" | Medium | Strict scope boundaries per item; defer to future epic |

---

## Timeline

**Total Effort**: 10 days (sequential), ~8 days with parallelization

| Stage | Items | Effort | Dependencies |
|-------|-------|--------|--------------|
| **Stage 1** | 1.1, 1.2, 1.3, 1.4 | 4.5 days | None |
| **Stage 2** | 2.1, 2.2 | 2.5 days | Stage 1 |
| **Stage 3** | 3.1, 3.2 | 2.5 days | Stage 1 |
| **Stage 4** | 4.1, 4.2 | 1.5 days | Stages 1-3 |

**Parallelization opportunities**:
- Within Stage 1: Items 1.2, 1.3, 1.4 can run in parallel after 1.1
- Stage 2 and Stage 3 can run in parallel (both depend only on Stage 1)
- Stage 4 items can run in parallel

---

## Lessons Learned (Post-Completion)

*Fill in after epic is complete*

**What Went Well**:
- TBD

**What Could Improve**:
- TBD

**Surprises**:
- TBD

---

**Last Updated**: 2026-01-26
**Next Action**: Begin Stage 1, starting with Item 1.1 (Command Template)
**Research Reference**: `.project/research/20260126-161628_python-vs-mbse-command-comparison.md`
