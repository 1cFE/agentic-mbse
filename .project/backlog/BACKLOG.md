# Product Backlog

Prioritized list of epics and features.

**Last Updated**: 2026-03-06

---

## Priority Legend

- **P0**: Critical - Blocking, do immediately
- **P1**: High - Important, do soon
- **P2**: Medium - Valuable, do when possible
- **P3**: Low - Nice to have, do eventually

---

## In Progress

### [EPIC-PDFV4-002] PDF Extraction Quality & Features

**Priority**: P1
**Effort**: ~6 days (6 items)
**Status**: In Progress (Items 1-4 complete, Items 5-6 remaining)
**Epic**: `.project/backlog/epic_pdf-extraction-improvements.md`

**Problem**: v4 pipeline shipped with quality regressions (running headers, GMFT routing, equation detection) and no image output (figures, table crops all discarded). These are the "last mile" issues before production-quality extraction.

**Goal**: Fix quality regressions, build unified image output pipeline (figures + table crops + future equation crops via single ImageCollector mechanism), add OCR for scanned PDFs.

**Items**: ~~(1) Quality gate+routing fixes~~ ✅, ~~(2) Unified image output~~ ✅, ~~(3) Pipeline profiling~~ ✅, ~~(4) Equation region detection~~ ✅, (5) OCR integration, (6) Summarize hallucination fix

---

## P0 - Critical Priority

*No P0 epics*

---

## P1 - High Priority

### [ITEM-DOCLING-002] PDF Skill Deployment — Docling MCP Setup in Init

**Priority**: P1
**Effort**: 2-3 days
**Status**: Needs design revision (spec+design from Feb 6, pre-v4)
**Active**: `.project/active/pdf-skill-deployment/`

**Problem**: The `pdf-analysis` skill ships a 3-tier extraction pipeline but Tier 2 (Docling MCP) requires manual setup. Users get references to `mcp__docling__*` tools that don't exist out of the box.

**Goal**: `agentic-mbse init` auto-configures Docling MCP server. Revisit design to align with v4 pipeline architecture and current best practices.

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

### [ITEM-ITERATION-LOOP] Experiment Iteration Loop

**Priority**: P3
**Effort**: TBD (spec exists, needs design)
**Status**: Shelved
**Active**: `.project/active/iteration-loop/`

**Problem**: Running unattended iterative experiments (e.g., PDF extraction quality improvement) requires manual orchestration of fresh-context cycles, prompt templates, and result comparison.

**Goal**: Build an outer-loop + inner-loop shell script system with prompt templates and an IterationSpecAgent for running unattended iterative experiments with fresh context per cycle.

---

### [ITEM-ARTIFACT-SCAFFOLD] Artifact Scaffolding via PM Script

**Priority**: P2
**Effort**: 1-2 days
**Status**: Spec complete
**Active**: `.project/active/artifact-scaffolding/`

**Problem**: 5 commands tell agents to manually fill in YAML frontmatter templates. Agents don't reliably follow these: they skip fields, use wrong formats, or invent non-standard fields, silently breaking PM automation.

**Goal**: Single `agentic-mbse pm create-artifact --type <type>` command that creates files with correctly populated frontmatter and scaffolded body sections. Commands change from "write this frontmatter" to "run this script, then fill in the body."

---

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
| EPIC-PDFV4-001: PDF Extraction v4 | 2026-02-27 | ~5 days | Quality-gated per-page pipeline, 4 items, extract --check |
| EPIC-PDFV4-002 Item 1: Quality Regressions | 2026-03-01 | 3 days | Equation fragment detection, GMFT xref routing, postprocess cleanup |
| EPIC-PDFV4-002 Item 2: Unified Image Output | 2026-03-01 | 1 day | ImageCollector/ImageEntry pattern, figure+table crop pipeline |
| EPIC-PDFV4-002 Item 3: Pipeline Profiling | 2026-03-01 | 0.5 days | PipelineProfile dataclass, --profile flag, profile.json output |
| EPIC-PDFV4-002 Item 4: Equation Region Detection | 2026-03-01 | 1 day | LayoutPredictor integration, NMS, --no-equations flag |
| Subprocess TTY Fix | 2026-03-01 | 0.5 days | start_new_session=True for Claude CLI subprocess calls |
| Docling Deep-Dive | 2026-03-06 | — | Research complete (Phases 0-2). Phases 3-4 not needed. |
| Pandoc Deep-Dive | 2026-03-06 | — | Research complete (Phases 1-4). Findings integrated into v4. |
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
