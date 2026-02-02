# Product Backlog

Prioritized list of epics and features.

**Last Updated**: 2026-01-26 (EPIC-CMDREV-001 created)

---

## Priority Legend

- **P0**: Critical - Blocking, do immediately
- **P1**: High - Important, do soon
- **P2**: Medium - Valuable, do when possible
- **P3**: Low - Nice to have, do eventually

---

## In Progress

*No items in progress*

---

## P0 - Critical Priority

*No P0 epics*

---

## P1 - High Priority

### [EPIC-CMDREV-001] MBSE Command System Revision

**Priority**: P1
**Effort**: 8-10 days (~8 with parallelization)
**Status**: Ready
**Epic File**: `.project/backlog/epic_command-revision.md`
**Research**: `.project/research/20260126-161628_python-vs-mbse-command-comparison.md`

**Problem**: MBSE commands are 2x longer than Python equivalents, lack project management maturity, and have inconsistent structure. Missing key commands like `/review-model` and `/project-status`.

**Goal**: Revise command system to match Python system maturity - lean commands (~300 lines avg), consistent structure, full PM workflow.

**Stages** (4 total, 10 backlog items):

| Stage | Focus | Items | Effort |
|-------|-------|-------|--------|
| **1** | Command Harmonization + `/review-model` | 1.1 Template, 1.2 Core cmds, 1.3 Support cmds, 1.4 Review cmd | 4.5 days |
| **2** | PM Enhancement | 2.1 EPIC_GUIDE + template, 2.2 `/project-status` | 2.5 days |
| **3** | Design Refactor + Agents | 3.1 design-model refactor, 3.2 Agent consolidation | 2.5 days |
| **4** | Additional Improvements | 4.1 `/quick-model`, 4.2 Template streamlining | 1.5 days |

**Parallelization**: Stages 2+3 can run in parallel after Stage 1

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

**Potential components**:
- `RAW_EXAMPLES.md` or structured storage for captured examples
- `/record-example` skill (similar to `/record-learning`)
- Example retrieval integrated into `/design-model`, `/implement-model`, etc.
- Similarity matching (semantic search or structured queries)

**Relationship to learnings**:
- Learnings capture insights about *how to model* (process knowledge)
- Examples capture *what was modeled successfully* (artifact knowledge)
- Both accelerate agent workflows through accumulated experience

---

### [TASK-PDF-001] Investigate PDF Extraction Header Consistency

**Priority**: P2
**Effort**: 2-4 hours
**Status**: Ready

**Problem**: Different PDF extraction tools produce different markdown header formats:
- KerML (via Docling?): `## 7.2.1 Title` - clean, enables depth-3 indexing (111 sections)
- Part1 (via PyMuPDF?): `##### **7 Title**` for depth-2, `**7.2.1 Title**` (bold only) for depth-3
  - This limits us to depth-2 indexing (52 sections)

**Goal**: Achieve consistent `## {number} Title` format across all specs to enable depth-3 indexing.

**Investigation tasks**:
- [ ] Identify which tool was used for each extraction (check m-scout processing logs)
- [ ] Compare Docling vs PyMuPDF output on same PDF
- [ ] Check if either tool has options to normalize header format
- [ ] Document recommended extraction settings for consistent output
- [ ] Re-extract Part1 if better format is achievable

**Tools to investigate**:
- `/home/reid/m-scout/tools/pdf-processing/` - current extraction scripts
- Docling: `pip install docling` - may have better structure preservation
- PyMuPDF: `pip install pymupdf` - faster but less structure-aware

**Success criteria**:
- All spec documents use `## {number} Title` format
- `generate_index.py --depth 3` works on all specs
- Consistent 100+ sections indexed per major spec

---

### [EPIC-LCOE-001] LCOE Costing Patterns

**Priority**: P2
**Effort**: TBD (needs research sync with fusion-tea)
**Status**: Tracking
**External Work**: `~/1cfe/fusion-tea`

**Problem**: The MBSE → sysml-codegen → teax-simkit pipeline needs nested cost model patterns validated and tooling upgraded.

**Context from fusion-tea**:
- Research and Stage 1-3 of cost patterns de-risking done in fusion-tea (see `~/1cfe/fusion-tea/.project/backlog/epic-cost-patterns-derisking.md`)
- Demo model: `~/1cfe/fusion-tea/models/tests/coffee_maker/` with `generate_costs.py` evaluator
- **CAUTION**: Commit d2c71b85 in fusion-tea was overwritten when applying agentic-mbse updates - need to verify fusion-tea state matches expectations

**agentic-mbse implications**:
- May need enforcement rules for cost modeling patterns
- Pattern documentation may belong in `docs/patterns/`
- When ready, roll validated patterns back to agentic-mbse templates

**Tracking only** - active development happens in fusion-tea and sysml-codegen repos.

---

### [EPIC-VIZ-001] Visualization Tool Integration

**Priority**: P2
**Effort**: TBD
**Status**: Tracking
**External Work**: `~/1cfe/fusion-tea/proof_of_concept/`

**Problem**: Need to visualize SysML model structure for stakeholder communication and debugging.

**Context from fusion-tea**:
- Visualization POC complete (see `~/1cfe/fusion-tea/.project/backlog/epic_visualization-poc.md`)
- Cytoscape.js demo: `~/1cfe/fusion-tea/proof_of_concept/cytoscape_demo.html`
- Extraction pipeline: `~/1cfe/fusion-tea/proof_of_concept/extraction/`
- Web server: `~/1cfe/fusion-tea/proof_of_concept/web/`
- Uses coffee_maker model as test fixture: `~/1cfe/fusion-tea/models/tests/coffee_maker/`

**agentic-mbse implications**:
- When visualization stabilizes, may roll back into agentic-mbse as a standard tool
- Could become `agentic-mbse visualize` command or web service
- Would need to work with any SysML project, not just fusion-tea

**Tracking only** - active development continues in fusion-tea POC.

---

## P3 - Low Priority

*No epics yet*

---

## Completed

| Item | Completed | Duration | Notes |
|------|-----------|----------|-------|
| EPIC-DOC-001: Documentation Discoverability | 2026-01-13 | 2 days | INDEX.md approach, 4 specialized agents, stdlib sync |
| ITEM-BACKPORT-001: Backport fusion-tea Patterns | 2026-01-13 | 0.5 days | Added 3 validated patterns to MODELING_GUIDE.md.template |
| ITEM-GUIDE-001: Progressive Disclosure Restructure | 2026-01-15 | 1 day | MODELING_GUIDE.md reduced from 1497→205 lines, 12 pattern docs created |
| ITEM-DEVMODE-001: Development Mode (--dev flag) | 2026-01-15 | 1 day | `agentic-mbse init --dev` creates symlinks for tool-owned files |
| ITEM-LEARNING-001: Learning Feedback Loop | 2026-01-15 | 1 day | `/record-learning` skill + RAW_LEARNINGS.md template |
| ITEM-SYSIDE-001: SysIDE v0.8.4 Upgrade | 2026-01-16 | 0.5 days | CLI + Python package + versioned docs with compatibility symlinks |
| ITEM-RENAME-001: Rename `project/` to `modeling_pm/` | 2026-01-23 | 1 day | CLI, templates, commands, agents all updated; 4-phase implementation |
| ITEM-REGTEST-001: Model Regression Testing | 2026-01-23 | 1 day | pytest infrastructure for SysML models; tests/models/ + command updates |
| ITEM-SYMLINK-001: Tool-Owned File Safety | 2026-01-23 | 1 day | Hash-based modification detection; LOCAL_GUIDE.md template |

---

## Ideas / Future Considerations

**Agent Improvements**:
- Enhanced error message interpretation (suggest imports automatically)
- Integration tests for agent responses
- Agent self-correction patterns (try → fail → research → retry)

**Learning System Extensions** (after ITEM-LEARNING-001):
- Automatic categorization of learnings via LLM
- Similarity detection to avoid duplicate learnings
- Periodic digest generation from RAW_LEARNINGS.md
- Hook-based auto-capture on debugging success

**Documentation**:
- Documentation versioning aligned with syside releases
- Post-processing script to normalize PDF extraction headers
- Support for `**7.2.1 Title**` bold-only headers in generate_index.py

**Developer Experience**:
- Watch mode for dev symlinks (auto-reload on changes)
- `agentic-mbse diff` command to compare project vs templates
- Migration tool for updating user-owned files with new features
