# Changelog

Historical record of completed work.

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
