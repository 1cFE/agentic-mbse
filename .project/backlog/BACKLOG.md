# Product Backlog

Prioritized list of epics and features.

**Last Updated**: 2026-01-13 (backlog refresh)

---

## Priority Legend

- **P0**: Critical - Blocking, do immediately
- **P1**: High - Important, do soon
- **P2**: Medium - Valuable, do when possible
- **P3**: Low - Nice to have, do eventually

---

## In Progress

*No epics currently in progress*

---

## P0 - Critical Priority

*No P0 epics*

---

## P1 - High Priority

### [ITEM-BACKPORT-001] Backport fusion-tea Modeling Patterns

**Priority**: P1
**Effort**: 0.5-1 day
**Status**: Ready

**Context**: The `~/1cfe/fusion-tea` project serves as our primary development domain for testing agentic-mbse. During modeling work, new patterns were developed (particularly around structured costing) and TOOL_OWNED files may have been modified directly.

**Problem**: Changes made in downstream projects don't automatically flow back to agentic-mbse. We need to:
1. Identify what changed in fusion-tea's tool-owned files
2. Evaluate which changes should be incorporated into agentic-mbse
3. Back-merge valuable patterns and fixes

**Scope**:
- [ ] Diff fusion-tea's `.claude/` against agentic-mbse's `claude/` directory
- [ ] Diff fusion-tea's `project/MODELING_GUIDE.md` against template
- [ ] Diff fusion-tea's `project/MODELING_PROCESS.md` against template
- [ ] Review costing pattern developments for generalization
- [ ] Identify any command/agent improvements made on-the-fly
- [ ] Back-incorporate changes to appropriate agentic-mbse files

**Files to compare** (TOOL_OWNED from `cli/__init__.py`):
- Commands: `design-model.md`, `implement-model.md`, `plan-model.md`, `spec-model.md`, etc.
- Agents: `kerml-expert.md`, `sysml-expert.md`, `syside-expert.md`, `sysmlv2-validator.md`
- Templates: `MODELING_GUIDE.md.template`, `MODELING_PROCESS.md.template`

**Deliverables**:
- Updated templates/commands/agents in agentic-mbse
- New patterns in `docs/patterns/` if applicable
- Documentation of what was backported

**Related**: ITEM-GUIDE-001 (restructuring guides), ITEM-DEVMODE-001 (avoiding future backports)

---

### [ITEM-GUIDE-001] Progressive Disclosure for Modeling Guides

**Priority**: P1
**Effort**: 1-2 days
**Status**: Ready
**Depends on**: ITEM-BACKPORT-001 (to know full scope of content)

**Design Principle**: Progressive disclosure - show users what they need when they need it, with clear paths to deeper information.

**Problem**: The `MODELING_GUIDE.md` and `MODELING_PROCESS.md` templates are accumulating content:
- Conditional expression syntax (now in `docs/patterns/conditionals.md`)
- Costing patterns (from fusion-tea work)
- Growing list of quick-reference rules
- Syntax examples that could be separate reference docs

This creates:
- Overwhelming initial experience for new users
- Difficulty finding specific information
- Maintenance burden when patterns evolve
- Inconsistent depth across topics

**Solution**: Establish `docs/patterns/` as the home for detailed reference material. Keep guides focused on:
- **MODELING_GUIDE.md**: Essential syntax (one example each), with links to patterns
- **MODELING_PROCESS.md**: Workflow steps, with links to detailed how-tos

**Proposed Structure**:
```
docs/patterns/
├── README.md                    # Index of all patterns
├── conditionals.md              # (exists) Conditional expressions
├── costing.md                   # (new) Structured costing patterns
├── constraints.md               # (new) Constraint expression patterns
├── requirements-traceability.md # (new) Requirement linking patterns
├── units-quantities.md          # (new) SI units and quantities
└── faq/
    ├── common-errors.md         # Parser error interpretations
    └── import-patterns.md       # Standard library imports
```

**Success Criteria**:
- [ ] MODELING_GUIDE.md is ≤300 lines (currently ~600+)
- [ ] Each syntax section is ≤20 lines with link to pattern doc
- [ ] All pattern docs are self-contained and parser-verified
- [ ] `docs/patterns/README.md` serves as navigable index
- [ ] Agents can discover patterns via grep/glob

**Acceptance Test**: New user can read MODELING_GUIDE in 10 minutes and know where to find details.

---

### [ITEM-DEVMODE-001] Development Mode for Domain Projects

**Priority**: P1
**Effort**: 1-2 days
**Status**: Ready

**Problem**: The current workflow for development domains (like fusion-tea) is friction-heavy:

| Approach | Pain Point |
|----------|------------|
| Make changes in agentic-mbse, re-init | Slow iteration, context switching |
| Make changes in domain project, backport later | Manual merge work, drift risk |

**Goal**: Enable a "development mode" where tool-owned files are symlinked rather than copied, so changes flow bidirectionally without manual intervention.

**Proposed Solution**:

```bash
# Current behavior (default)
agentic-mbse init /path/to/project

# Development mode - symlinks instead of copies
agentic-mbse init --dev /path/to/project

# Or explicit symlink flag
agentic-mbse init --symlink-tools /path/to/project
```

**Implementation Details**:

1. **New flag**: `--dev` or `--symlink-tools` in `cmd_init()`
2. **Behavior change**: For TOOL_OWNED files, create symlinks instead of copies:
   ```python
   if args.dev:
       dst.symlink_to(src)  # Point to source in agentic-mbse
   else:
       shutil.copy2(src, dst)  # Current behavior
   ```
3. **Path resolution**: Symlinks must point to absolute paths in the installed package or repo
4. **Git handling**: Symlinks commit fine; document in README

**Considerations**:
- Symlinks work on Linux/macOS; Windows may need special handling
- Need to handle case where agentic-mbse is pip-installed vs. local repo
- `--dev` implies local repo development; pip-installed packages shouldn't use this
- May want `agentic-mbse init --dev --repo /path/to/agentic-mbse` for explicit source

**Success Criteria**:
- [ ] `--dev` flag creates symlinks for tool-owned files
- [ ] Changes in either location are immediately visible in both
- [ ] Clear error if symlink source doesn't exist
- [ ] Works with `replicate_setup.sh` pattern
- [ ] Documentation explains when to use dev mode

**Future Enhancement**: Watch mode that auto-syncs on file changes (lower priority).

---

### [ITEM-LEARNING-001] Agent Learning Feedback Loop

**Priority**: P1
**Effort**: 2-3 days
**Status**: Ready

**Vision**: Create a lightweight system for agents to record insights when they struggle, building institutional memory that improves future agent performance.

**Problem**: Agents repeatedly encounter the same challenges:
- Missing imports for standard library functions
- Syntax that looks right but doesn't parse
- Patterns that work but aren't documented
- Workarounds discovered through trial and error

Currently, these learnings are lost when the conversation ends.

**Proposed Architecture**:

```
Entry Points (3):
├── /record-learning          # Explicit slash command
├── skills/record-learning.md # Claude skill (can be invoked by agents)
└── hooks/learning-hook.sh    # (optional) Auto-trigger on certain events

Core Script:
└── scripts/record_learning.py
    ├── Input: learning text, optional conversation reference
    ├── Output: appends to project/learnings/RAW_LEARNINGS.md
    └── Format: timestamped, categorized, with source reference

Learnings Storage:
└── project/learnings/
    ├── RAW_LEARNINGS.md      # Append-only log of agent insights
    └── REVIEWED.md           # Human-verified, ready for formalization

Formalization (manual process):
└── Human reviews RAW_LEARNINGS.md periodically
    ├── Verify insight is correct (test with parser, check docs)
    ├── Generalize if applicable
    ├── Create pattern doc in docs/patterns/ or FAQ entry
    └── Update agents to reference new pattern
```

**Entry Point Details**:

1. **Slash Command** (`/record-learning`):
   ```markdown
   # Record Learning Command

   Capture an insight or pattern discovered during modeling work.

   Usage: /record-learning <description>

   Example: /record-learning The 'sum' function requires importing
   NumericalFunctions, not just using NumericalFunctions::sum directly
   ```

2. **Skill File** (`skills/record-learning.md`):
   - Can be invoked by agents when they solve a tricky problem
   - Includes guidance on what makes a good learning
   - Calls `record_learning.py` under the hood

3. **Hook** (optional, lower priority):
   - Could trigger on repeated validation failures followed by success
   - Or on long debugging sessions that eventually resolve
   - More complex; defer to v2

**Learning Format**:
```markdown
## 2026-01-13T14:32:00Z

**Category**: Import Pattern
**Source**: fusion-tea modeling session
**Conversation**: (optional reference)

**Problem**: Tried to use `sum(collection)` but got "unresolved reference"

**Solution**: Must import the function explicitly:
```sysml
import NumericalFunctions::sum;
attribute total : Real = sum(costs);
```

**Generalization**: All stdlib functions need explicit imports; can't use
qualified names directly in expressions without import.

---
```

**Success Criteria**:
- [ ] `/record-learning` command captures insights to file
- [ ] Skill file enables agents to self-record learnings
- [ ] RAW_LEARNINGS.md accumulates actionable insights
- [ ] At least one learning is formalized into a pattern doc (proof of concept)
- [ ] Agents can discover formalized patterns in future sessions

**Future Enhancements**:
- Automatic categorization of learnings
- Similarity detection to avoid duplicates
- Periodic digest/summary generation
- Integration with agent system prompts

---

## P2 - Medium Priority

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

## P3 - Low Priority

*No epics yet*

---

## Completed

| Epic | Completed | Duration | Notes |
|------|-----------|----------|-------|
| EPIC-DOC-001: Documentation Discoverability | 2026-01-13 | 2 days | INDEX.md approach, 4 specialized agents, stdlib sync |

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
