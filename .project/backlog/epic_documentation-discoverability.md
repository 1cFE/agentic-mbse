# EPIC-DOC-001: Documentation Discoverability Overhaul

**Priority**: P0 (Critical - User-facing failure)
**Status**: In Progress
**Created**: 2026-01-12
**Updated**: 2026-01-13
**Research**:
- `.project/research/20260112-064217_sysmlv2-agent-discoverability-failure.md`
- `project/research/20260112-222249_chunking-indexing-strategy.md`

---

## Problem Statement

Our sysmlv2-doc-analyzer agent consistently fails to help users discover standard library functions like `NumericalFunctions::sum`. A team using our toolkit spent **hours** trying to find a basic function that existed all along. This happened because:

1. **Missing documentation**: KerML spec (which defines the standard library) wasn't extracted from PDF
2. **No navigable index**: Large spec documents (14K+ lines) have no roadmap for agents
3. **Wrong agent strategy**: Agent confidently says "doesn't exist" when it simply can't find something
4. **No validation fallback**: No agent can run `syside check` to test if code actually works
5. **Monolithic agent**: Single agent tries to cover all documentation, leading to missed searches

---

## Solution: INDEX.md Approach + Specialized Agents

After research ([chunking-indexing-strategy.md](../../project/research/20260112-222249_chunking-indexing-strategy.md)), we chose a lightweight indexing approach over document chunking:

**Key insight**: For grep-based retrieval with Claude's large context window, we don't need to physically chunk documents. We need **structured indexes** that tell agents what's in each section.

**Implementation**:
- Every `full_document.md` gets a companion `INDEX.md`
- INDEX.md contains section hierarchy with line numbers and AI-generated summaries
- Agents read INDEX.md first, then use targeted `Read` with offset/limit
- Scripts automate index generation with checksum-based incremental updates

**Agent Architecture**: Split the monolithic `sysmlv2-doc-analyzer` into specialized agents by documentation source, enabling parallel research and focused expertise.

---

## Success Criteria

1. ~~Agent can correctly answer "How do I sum values over a collection?"~~ **ENABLED** - INDEX.md now shows `sum` in section 9.4.7
2. ~~All critical SysML v2 specs extracted and indexed~~ **DONE** - KerML + Parts 1-3 extracted, indexed
3. [x] ~~Standard library functions documented in a greppable quick reference~~ **SUPERSEDED** - kerml-expert agent with INDEX.md provides this
4. [ ] Agent never says "doesn't exist" - only "couldn't find in my documentation"
5. [ ] Validation agent can test snippets with `syside check`
6. [ ] Specialized agents enable parallel documentation research

---

## Completed Items

### P0-1: Extract Missing PDF Specifications ✅
**Status**: DONE
**Completed**: 2026-01-12

Extracted critical PDFs to markdown:
- `docs/sysmlv2/SysML_KerMLSpec/full_document.md` (13,958 lines)
- `docs/sysmlv2/SysML_Spec_v2_Part1/full_document.md`

---

### P0-2: Generate Section Indexes ✅
**Status**: DONE
**Completed**: 2026-01-13

Created automated indexing tooling instead of manual quick reference.

**Scripts created**:

| Script | Purpose | Location |
|--------|---------|----------|
| `generate_index.py` | Create INDEX.md with AI summaries | `scripts/generate_index.py` |
| `read_section.py` | Read specific section by number | `scripts/read_section.py` |

**Usage**:
```bash
# Generate index (calls Claude ~100 times for summaries)
python3 scripts/generate_index.py docs/sysmlv2/SysML_KerMLSpec/

# Dry-run to see sections without generating summaries
python3 scripts/generate_index.py --dry-run docs/sysmlv2/SysML_KerMLSpec/

# Force regeneration even if checksum matches
python3 scripts/generate_index.py --force docs/sysmlv2/SysML_KerMLSpec/

# Read a specific section
python3 scripts/read_section.py docs/sysmlv2/SysML_KerMLSpec/ 9.4.7

# Read with context lines
python3 scripts/read_section.py docs/sysmlv2/SysML_KerMLSpec/ 7.2.1 --context 10
```

**INDEX.md format**:
```markdown
---
document: SysML_KerMLSpec
generated: 2026-01-13T00:19:29Z
source_checksum: sha256:2796da486d53...
total_lines: 13958
depth: 3
section_count: 111
---

# SysML_KerMLSpec Index

## 7 Language Description
**Lines:** 959-2845 | **Subsections:** 7.1, 7.2, 7.3, 7.4

Informative description of KerML constructs covering Root, Core, and Kernel layers.

### 9.4.7 Numerical Functions
**Lines:** 13216-13231

Abstract functions for arithmetic operations, comparison operators,
utility functions (isZero, abs, max, min), and collection aggregations
(sum, product) on NumericalValue types.
```

**Indexes generated**:
- [x] `docs/sysmlv2/SysML_KerMLSpec/INDEX.md` (111 sections)
- [x] `docs/sysmlv2/SysML_Spec_v2_Part1/INDEX.md`
- [x] `docs/sysmlv2/SysML_Spec_v2_Part2/INDEX.md`
- [x] `docs/sysmlv2/SysML_Spec_v2_Part3/INDEX.md`

**Spec**: `.project/active/doc-index-tooling/spec.md`

---

### P2-1: Generate Indexes for All Specs ✅
**Status**: DONE
**Completed**: 2026-01-13

All spec documents now have INDEX.md files generated.

---

## Remaining Items

### P0-3: Split Documentation Agent into Specialized Agents
**Effort**: 4-6 hours
**Dependencies**: P0-2
**Status**: TODO
**Spec**: `.project/active/specialized-doc-agents/spec.md`

Replace monolithic `sysmlv2-doc-analyzer` with specialized agents by documentation source:

| Agent | Corpus | Primary Use Cases |
|-------|--------|-------------------|
| `kerml-expert` | KerML spec + INDEX.md | Standard library, type system, language semantics |
| `sysml-expert` | Parts 1-3 + INDEX.md | Modeling constructs, requirements, usage patterns |
| `syside-expert` | syside docs | Parser, evaluation, tooling integration |
| `sysmlv2-validator` | syside CLI | Syntax validation, error interpretation |

**Benefits**:
- Focused corpus per agent reduces false negatives
- Enables parallel research (spawn multiple agents at once)
- Each agent uses INDEX.md-first strategy
- All agents include "never claim doesn't exist" rule

**Acceptance Criteria**:
- [ ] 4 new agents created with focused prompts
- [ ] Each agent uses INDEX.md-first search strategy
- [ ] "Never claim doesn't exist" rule in all agents
- [ ] task-model commands updated to use specialized agents
- [ ] Old sysmlv2-doc-analyzer deprecated

---

### P1-2: Create Standard Library Quick Reference
**Status**: SUPERSEDED
**Reason**: The `kerml-expert` agent with INDEX.md provides equivalent functionality. INDEX.md section 9.4 summaries list all standard library functions. If a quick reference is still desired, it can be auto-generated later.

---

### P1-3: Add Standard Library Files to Searchable Corpus ✅
**Status**: DONE
**Completed**: 2026-01-13
**Spec**: `.project/active/stdlib-corpus/spec.md`

Created `scripts/sync_stdlib.py` to sync the full syside standard library to `docs/sysmlv2/stdlib/`:

**Script features**:
- Copies all `.kerml` and `.sysml` files preserving directory structure
- Generates `INDEX.md` with Quick Reference + file summaries (via `claude -p`)
- Generates `VERSION.md` with syside version tracking
- Supports `--dry-run` and `--force` flags

**Output structure**:
```
docs/sysmlv2/stdlib/
├── INDEX.md           # Quick Reference + ~94 file summaries
├── VERSION.md         # syside version, sync timestamp
├── Kernel Libraries/  # 36 files (functions, types, semantics)
├── Systems Library/   # 21 files (Part, Port, Action, etc.)
└── Domain Libraries/  # 37 files (SI, ISQ, Analysis, etc.)
```

**Usage**:
```bash
python scripts/sync_stdlib.py              # Sync and generate INDEX.md
python scripts/sync_stdlib.py --dry-run    # Preview without copying
python scripts/sync_stdlib.py --force      # Regenerate even if up-to-date
```

---

### P2-2: Documentation Coverage Dashboard
**Effort**: 4-6 hours
**Dependencies**: P0-2
**Status**: TODO (Low Priority)

Script to audit documentation coverage and index freshness.

**Acceptance Criteria**:
- [ ] Script checks all expected INDEX.md files exist
- [ ] Reports checksum mismatches (stale indexes)
- [ ] Shows coverage gaps

---

## Implementation Order

```
Completed:
├── P0-1: Extract PDFs ✅
├── P0-2: Generate section indexes ✅
├── P2-1: Index all specs ✅
└── P1-3: Sync stdlib to docs ✅
    └── [Milestone: Infrastructure complete - all documentation indexed and searchable]

Next:
└── P0-3: Split into specialized agents (4-6 hours)
    ├── kerml-expert
    ├── sysml-expert
    ├── syside-expert
    └── sysmlv2-validator
    └── [Milestone: Complete discoverability solution]

Later:
└── P2-2: Coverage dashboard (4-6 hours)
```

---

## Script Documentation

### `scripts/generate_index.py`

Generate INDEX.md from full_document.md with AI-generated summaries.

```
usage: generate_index.py [-h] [--depth DEPTH] [--force] [--dry-run] path

Arguments:
  path           Path to full_document.md or containing folder

Options:
  --depth DEPTH  Max header depth to index (default: 3)
  --force        Regenerate even if checksum matches
  --dry-run      Show sections without generating summaries
```

**How it works**:
1. Parses headers matching `## {number} {title}` (e.g., `## 7.2.1 Root Overview`)
2. Calculates line ranges for each section
3. Builds breadcrumb hierarchy (e.g., "7 Language > 7.2 Root")
4. Calls `claude -p` to generate 1-2 sentence summary for each section
5. Outputs INDEX.md with YAML frontmatter (includes source checksum)

**Incremental updates**: Re-running skips regeneration if source checksum matches.

### `scripts/read_section.py`

Read a specific section from a document using INDEX.md.

```
usage: read_section.py [-h] [--context CONTEXT] [--raw] path section

Arguments:
  path           Path to full_document.md or containing folder
  section        Section number (e.g., "7", "7.2", "7.2.1")

Options:
  --context INT  Extra lines before/after section (default: 0)
  --raw          Output content only without header
```

**Example**:
```bash
$ python3 scripts/read_section.py docs/sysmlv2/SysML_KerMLSpec/ 9.4.7
# 9.4.7 Numerical Functions
# Lines 13216-13231 from full_document.md

## 9.4.7 Numerical Functions
...
```

---

## Design Decisions

### Why INDEX.md instead of chunking?

1. **Claude's context window is huge**: 200K tokens. A 500-line section (10K tokens) is 5% of context.
2. **Grep already works**: Agent greps, finds line number, reads with offset/limit. No chunking needed.
3. **Simpler architecture**: No chunk files to manage, no vector database, no embedding costs.
4. **Human-readable**: INDEX.md is useful for humans too, not just agents.

### Why depth 3?

Analysis of KerML spec showed:
- Depth 1 (e.g., "7"): 11 chunks, avg 1,198 lines - too coarse
- Depth 2 (e.g., "7.2"): 30 chunks, avg 439 lines - good for navigation
- Depth 3 (e.g., "7.2.1"): 111 chunks, avg 119 lines - good for summaries

Depth 3 provides good granularity for summaries while depth 2 subsection listings help with navigation.

### Why AI-generated summaries?

Human-written summaries would be better but don't scale. AI summaries are:
- Good enough for navigation (tells you what's in each section)
- Automatically generated (no manual effort)
- Consistent in style
- Can be regenerated if document changes

---

## References

- Research: `.project/research/20260112-064217_sysmlv2-agent-discoverability-failure.md`
- Chunking research: `project/research/20260112-222249_chunking-indexing-strategy.md`
- Spec: `.project/active/doc-index-tooling/spec.md`
- External feedback: `/home/reid/1cfe/fusion-tea/project/research/20260112-061548_sysmlv2-discovery-reflection.md`
- Standard library source: `.venv/lib/python3.12/site-packages/syside/sysml.library/`
