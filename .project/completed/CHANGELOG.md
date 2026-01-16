# Changelog

Historical record of completed work.

---

## [2026-01-15] - ITEM-LEARNING-001: Agent Learning Feedback Loop

**Type**: Item
**Duration**: 1 day
**Priority**: P1

### Summary

Created a lightweight system for agents to record insights when they discover solutions, building institutional memory that improves future agent performance.

### Deliverables

- `claude/skills/record-learning/SKILL.md` - Skill for capturing learnings
- `project_templates/RAW_LEARNINGS.md.template` - Template for learnings storage
- Updated `cmd_init()` to create `project/learnings/` directory

### Key Features

- User-invocable via `/record-learning` command
- Agent can self-invoke when discovering noteworthy patterns
- Requires user approval before recording (never autonomous)
- Structured entry format: timestamp, category, problem, solution, generalization

---

## [2026-01-15] - ITEM-DEVMODE-001: Development Mode for Init

**Type**: Item
**Duration**: 1 day
**Priority**: P1

### Summary

Added `--dev` flag to `agentic-mbse init` that creates symlinks for tool-owned files instead of copies, enabling bidirectional editing between agentic-mbse source and domain projects.

### Deliverables

- `--dev` CLI flag for init subcommand
- Symlink creation for all tool-owned files (commands, agents, skills, hooks, templates)
- Source checkout detection (errors if used with pip-installed package)
- Platform detection (errors on Windows)
- Auto-updates `.gitignore` with tool-owned paths

### Lessons Learned

- Symlinks must use absolute paths for reliability
- Need to detect pip-installed vs source checkout via `__file__` inspection

---

## [2026-01-15] - ITEM-GUIDE-001: Progressive Disclosure Restructure

**Type**: Item
**Duration**: 1 day
**Priority**: P1

### Summary

Restructured `MODELING_GUIDE.md.template` from 1,497 lines to 205 lines using progressive disclosure pattern. Detailed reference material extracted to 12 pattern docs in `docs/patterns/`.

### Deliverables

**Pattern Documents Created** (12 total):
- `semantic-operators.md` (568 lines) - Assignment, redefinition, binding semantics
- `syntax-reference.md` (364 lines) - 10 core syntax patterns
- `mbse-concepts.md` (270 lines) - Allocation, parametric, cost patterns
- `definitions-usages.md` (260 lines) - Core def vs usage principle
- `expose-pattern.md` (287 lines) - The EXPOSE pattern for interfaces
- `adr002-calculations.md` (241 lines) - Calculation architecture
- `doc-comments.md` (298 lines) - Documentation standards
- `package-naming.md` (251 lines) - Naming conventions
- `common-mistakes.md` (353 lines) - Anti-patterns to avoid
- `constraints.md` (291 lines) - Constraint expressions
- `cross-file-binding.md` (297 lines) - Multi-file imports

**Updated Files**:
- `project_templates/MODELING_GUIDE.md.template` - Reduced from 1,497→205 lines
- `docs/patterns/README.md` - Index of all 12 pattern docs

### Lessons Learned

- Progressive disclosure significantly improves readability
- Extracting to separate pattern docs enables better discoverability via grep
- Pattern docs are larger than source sections due to added structure (examples, common mistakes)

---

## [2026-01-13] - ITEM-BACKPORT-001: Backport fusion-tea Patterns

**Type**: Item
**Duration**: 0.5 days
**Priority**: P1

### Summary

Backported validated modeling patterns from the fusion-tea domain project into agentic-mbse templates.

### Deliverables

Added to `MODELING_GUIDE.md.template`:
- Cost Model Imports section (NumericalFunctions::sum)
- Multiplicity Cost Aggregation Pattern
- Part Redefinition Pattern (dot notation vs redefines)
- Parameterized Multiplicity Pattern

### Lessons Learned

- Bidirectional sync between source and domain projects needs automation (→ ITEM-DEVMODE-001)
- Validated patterns should flow from real usage, not theoretical design

---

## [2026-01-13] - EPIC-DOC-001: Documentation Discoverability Overhaul

**Type**: Epic
**Duration**: 2 days (2026-01-12 to 2026-01-13)
**Priority**: P0 (Critical)

### Summary

Complete overhaul of documentation discoverability infrastructure. Users were unable to find standard library functions like `NumericalFunctions::sum` because the KerML spec wasn't extracted and agents had no navigable index. This epic fixed the root causes through PDF extraction, INDEX.md-based navigation, specialized agents, and stdlib sync.

### Deliverables

**Scripts**:
- `scripts/generate_index.py` - Generate INDEX.md with AI summaries from full_document.md
- `scripts/read_section.py` - Read specific sections by number using INDEX.md
- `scripts/sync_stdlib.py` - Sync syside standard library to docs/sysmlv2/stdlib/

**Documentation**:
- `docs/sysmlv2/SysML_KerMLSpec/INDEX.md` - 111 sections indexed
- `docs/sysmlv2/SysML_Spec_v2_Part1/INDEX.md` - Part 1 indexed
- `docs/sysmlv2/SysML_Spec_v2_Part2/INDEX.md` - Part 2 indexed
- `docs/sysmlv2/SysML_Spec_v2_Part3/INDEX.md` - Part 3 indexed
- `docs/sysmlv2/stdlib/` - 94 library files with INDEX.md

**Agents**:
- `claude/agents/kerml-expert.md` - KerML spec + standard library
- `claude/agents/sysml-expert.md` - SysML Parts 1-3
- `claude/agents/syside-expert.md` - syside tooling
- `claude/agents/sysmlv2-validator.md` - Syntax validation
- `claude/agents/deprecated/sysmlv2-doc-analyzer.md` - Old monolithic agent

### Items Completed

| Item | Completed | Notes |
|------|-----------|-------|
| extract-missing-pdf-specs | 2026-01-12 | KerML + Part1 extracted via PyMuPDF |
| doc-index-tooling | 2026-01-13 | INDEX.md approach, scripts created |
| specialized-doc-agents | 2026-01-13 | 4 new agents, old agent deprecated |
| stdlib-corpus | 2026-01-13 | 94 files synced with INDEX.md |
| markdown-chunker-indexer | 2026-01-13 | DEPRECATED - superseded by INDEX.md approach |

### Lessons Learned

- INDEX.md with line numbers is simpler and more effective than physical document chunking
- PyMuPDF produces better output than Docling for structured PDFs (faster, less memory)
- Specialized agents enable parallel research and focused expertise
- AI-generated summaries scale well for documentation indexes

---

## [2026-01-10] - Init File Ownership

**Type**: Item
**Duration**: 1 day

### Summary

Modified `agentic-mbse init` to distinguish between user-owned files (preserved on re-init) and tool-owned files (always updated). Users can now safely re-run `init` to get latest tool improvements without losing customizations.

### Deliverables

- Updated `src/agentic_mbse/cli/__init__.py` with user/tool file categorization
- `USER_OWNED_TEMPLATES` and `TOOL_OWNED_TEMPLATES` constants
- Three-way output: Created / Updated / Skipped
- Updated CLAUDE.md with file ownership documentation

### Lessons Learned

- Clear separation of ownership prevents user frustration
- Explicit feedback (created/updated/skipped) builds trust

---

## [2026-01-09] - Replicate Setup Script

**Type**: Item
**Duration**: 1 day

### Summary

Created `scripts/replicate_setup.sh` to replicate `agentic-mbse init` behavior for development in this repo without requiring the CLI to be installed. Enables dogfooding the MBSE commands.

### Deliverables

- `scripts/replicate_setup.sh` - ~210 lines, installs commands/agents/skills/hooks
- Updated `.gitignore` for generated files (project/, models/library/, SOURCE_INDEX.md)
- Updated CLAUDE.md with directory clarification (.project/ vs project/)

### Lessons Learned

- Placeholder substitution pattern (`{SYSML_DOCS_PATH}`) works well for portability
- Clear documentation of directory purposes prevents confusion

---

## [2026-01-09] - Conditional Expression Pattern Documentation

**Type**: Item
**Duration**: 1 day

### Summary

Created single source of truth for SysML v2 conditional expression syntax at `docs/patterns/conditionals.md`. Fixed incorrect C-style ternary syntax in MODELING_GUIDE.md.template.

### Deliverables

- `docs/patterns/README.md` - Pattern directory purpose
- `docs/patterns/conditionals.md` - Comprehensive conditional syntax reference
- Updated `project_templates/MODELING_GUIDE.md.template` Syntax 10

### Lessons Learned

- Single source of truth prevents documentation drift
- Parser-verified examples prevent incorrect syntax from propagating

---
