# Product Backlog

Prioritized list of epics and features.

**Last Updated**: 2026-02-23

---

## Priority Legend

- **P0**: Critical - Blocking, do immediately
- **P1**: High - Important, do soon
- **P2**: Medium - Valuable, do when possible
- **P3**: Low - Nice to have, do eventually

---

## In Progress

### [EPIC-PDFV4-001] PDF Extraction Pipeline v4 — Quality-Gated Per-Page Pipeline

**Priority**: P1
**Effort**: 5.5 days (4 items)
**Status**: Ready
**Epic**: `.project/backlog/epic_pdf-extraction-v4.md`
**Design**: `.project/concepts/doc-extraction/design.md`

**Problem**: v3 pipeline operates at document level with pattern-based structure repair. Stage 3/4 experiments proved per-page quality-gated routing with ensemble table detection is superior (70% heading error reduction, 86% table recall).

**Goal**: Replace v3 with per-page pipeline: `extract_pdf()` → quality gate → route each page to best available enhancer within budget. Remove 5 deprecated modules.

---

## P0 - Critical Priority

*No P0 epics*

---

## P1 - High Priority

*No P1 epics*

---

## P2 - Medium Priority

### [ITEM-EXAMPLES-001] Example Store for Modeling Agents

**Priority**: P2
**Effort**: TBD (needs design)
**Status**: Idea

**Problem**: Modeling agents lack access to successful prior examples when tackling new modeling tasks. Each session starts fresh without leveraging patterns that worked well in similar situations.

**Goal**: Build an "example store" similar to the learning feedback loop, but focused on capturing and retrieving successful model fragments, patterns, and solutions.

**Key questions to explore**:
- What constitutes a "successful example"? (validated models, user-approved patterns, etc.)
- How should examples be indexed for similarity search? (by domain, pattern type, structure?)
- What metadata is needed? (context, constraints solved, related learnings)
- How do agents query the store during workflows?
- Should examples be curated or auto-captured?

---

### [ITEM-DOCLING-001] PDF Skill Deployment — Docling MCP Setup in Init

**Priority**: P2
**Effort**: 2-3 days
**Status**: Spec drafted
**Spec**: `.project/active/pdf-skill-deployment/spec.md`

**Problem**: The `pdf-analysis` skill ships a 3-tier extraction pipeline but Tier 2 (Docling MCP) requires manual setup. Users get references to `mcp__docling__*` tools that don't exist out of the box.

**Goal**: `agentic-mbse init` auto-configures Docling MCP server with tier-appropriate resource limits. Adaptive skill prompt based on system capabilities.

---

### [ITEM-PM-STUBS-001] Complete PM Operations Stubs

**Priority**: P2
**Effort**: 1-2 days
**Status**: Ready

**Problem**: Two PM operations in `src/agentic_mbse/pm/operations.py` have incomplete implementations:
1. **Line 849**: `impact_query()` — `affected_work_items` always returns empty list (needs model→work-item mapping)
2. **Line 1134**: `supersede_insight()` — Raises `NotImplementedError` (needs full supersession flow per `workflows.md § 6.1`)

**Goal**: Implement both operations fully, or document them as intentional limitations.

---

### [EPIC-LCOE-001] LCOE Costing Patterns

**Priority**: P2
**Effort**: TBD (needs research sync with fusion-tea)
**Status**: Tracking
**External Work**: `~/1cfe/fusion-tea`

**Problem**: The MBSE → sysml-codegen → teax-simkit pipeline needs nested cost model patterns validated and tooling upgraded.

**Tracking only** - active development happens in fusion-tea and sysml-codegen repos.

---

### [EPIC-VIZ-001] Visualization Tool Integration

**Priority**: P2
**Effort**: TBD
**Status**: Tracking
**External Work**: `~/1cfe/fusion-tea/proof_of_concept/`

**Problem**: Need to visualize SysML model structure for stakeholder communication and debugging.

**Tracking only** - active development continues in fusion-tea POC.

---

## P3 - Low Priority

### [ITEM-ARCH-WALKTHROUGHS] Architecture Validation Walkthroughs

**Priority**: P3
**Effort**: 2-3 hours
**Status**: Deferred

**Problem**: EPIC-ARCH-003 D3.5 interactive validation walkthroughs were not completed. These require running each new command in a real target project and verifying end-to-end behavior.

**Goal**: Run all 14 commands + 5 new commands in fusion-tea or a test project to verify proper behavior.

---

## Completed

| Item | Completed | Duration | Notes |
|------|-----------|----------|-------|
| EPIC-PDFV3-001: PDF Extraction v3 | 2026-02-08 | 3 days | 4-layer pipeline, Claude structure repair, 4/5 new docs pass |
| EPIC-ARCH-001: Architecture Structure | 2026-02-03 | 3 days | 4-directory architecture, templates, cmd_init rewiring |
| EPIC-ARCH-002: Architecture Knowledge | 2026-02-03 | 2 days | 9 new skills, context measurement, extraction mapping |
| EPIC-ARCH-003: Architecture Commands | 2026-02-03 | 3 days | 14 commands refactored/created, registration, agent cleanup |
| EPIC-ARCH-004: Architecture PM Engine | 2026-02-03 | 3 days | 8 parsers, state derivation, dashboard, 14 operations, CLI |
| EPIC-DOC-001: Documentation Discoverability | 2026-01-13 | 2 days | INDEX.md approach, 4 specialized agents, stdlib sync |
| ITEM-BACKPORT-001: Backport fusion-tea Patterns | 2026-01-13 | 0.5 days | Added 3 validated patterns to MODELING_GUIDE.md.template |
| ITEM-GUIDE-001: Progressive Disclosure Restructure | 2026-01-15 | 1 day | MODELING_GUIDE.md reduced from 1497→205 lines, 12 pattern docs |
| ITEM-DEVMODE-001: Development Mode (--dev flag) | 2026-01-15 | 1 day | `agentic-mbse init --dev` creates symlinks for tool-owned files |
| ITEM-LEARNING-001: Learning Feedback Loop | 2026-01-15 | 1 day | `/record-learning` skill + RAW_LEARNINGS.md template |
| ITEM-SYSIDE-001: SysIDE v0.8.4 Upgrade | 2026-01-16 | 0.5 days | CLI + Python package + versioned docs with compatibility symlinks |
| ITEM-RENAME-001: Rename `project/` to `modeling_pm/` | 2026-01-23 | 1 day | CLI, templates, commands, agents all updated |
| ITEM-REGTEST-001: Model Regression Testing | 2026-01-23 | 1 day | pytest infrastructure for SysML models |
| ITEM-SYMLINK-001: Tool-Owned File Safety | 2026-01-23 | 1 day | Hash-based modification detection |
| ~~EPIC-CMDREV-001: Command System Revision~~ | — | — | **Superseded** by EPIC-ARCH-002 + EPIC-ARCH-003 |
| ~~TASK-PDF-001: Header Consistency~~ | — | — | **Superseded** by EPIC-PDFV3-001 (Claude structure repair handles this) |

---

## Ideas / Future Considerations

**Agent Improvements**:
- Enhanced error message interpretation (suggest imports automatically)
- Integration tests for agent responses
- Agent self-correction patterns (try → fail → research → retry)

**Learning System Extensions**:
- Automatic categorization of learnings via LLM
- Similarity detection to avoid duplicate learnings
- Periodic digest generation from RAW_LEARNINGS.md
- Hook-based auto-capture on debugging success

**Developer Experience**:
- Watch mode for dev symlinks (auto-reload on changes)
- `agentic-mbse diff` command to compare project vs templates
- Migration tool for updating user-owned files with new features
