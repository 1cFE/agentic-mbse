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

---

## Solution: INDEX.md Approach

After research ([chunking-indexing-strategy.md](../../project/research/20260112-222249_chunking-indexing-strategy.md)), we chose a lightweight indexing approach over document chunking:

**Key insight**: For grep-based retrieval with Claude's large context window, we don't need to physically chunk documents. We need **structured indexes** that tell agents what's in each section.

**Implementation**:
- Every `full_document.md` gets a companion `INDEX.md`
- INDEX.md contains section hierarchy with line numbers and AI-generated summaries
- Agents read INDEX.md first, then use targeted `Read` with offset/limit
- Scripts automate index generation with checksum-based incremental updates

---

## Success Criteria

1. ~~Agent can correctly answer "How do I sum values over a collection?"~~ **ENABLED** - INDEX.md now shows `sum` in section 9.4.7
2. ~~All critical SysML v2 specs extracted and indexed~~ **DONE** - KerML extracted, indexed
3. [ ] Standard library functions documented in a greppable quick reference
4. [ ] Agent never says "doesn't exist" - only "couldn't find in my documentation"
5. [ ] Validation agent can test snippets with `syside check`

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
**Status**: DONE (KerML), IN PROGRESS (Part1)
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
- [ ] `docs/sysmlv2/SysML_Spec_v2_Part1/INDEX.md` (in progress)

**Spec**: `.project/active/doc-index-tooling/spec.md`

---

## Remaining Items

### P0-3: Update Agent System Prompt
**Effort**: 1 hour
**Dependencies**: P0-2
**Status**: TODO

Update `claude/agents/sysmlv2-doc-analyzer.md` to:

1. **Check INDEX.md FIRST** to understand document structure
2. **Never say "doesn't exist"** - say "I couldn't find this in my documentation"
3. **Use targeted reads** - read INDEX.md, find section, read with offset/limit

**Key changes**:
```markdown
## Search Strategy (UPDATED)

### For Any Query

1. **FIRST**: Read INDEX.md to understand document structure and find relevant sections
2. **SECOND**: Use section line numbers to read targeted content with offset/limit
3. **THIRD**: If not found, search other specs' INDEX.md files

### For Function/Library Questions

When user asks about functions (sum, size, collect, etc.):
1. Read SysML_KerMLSpec/INDEX.md
2. Look for section 9.4 Function Library and its subsections
3. Read the specific subsection (e.g., 9.4.7 Numerical Functions for `sum`)

### CRITICAL: Never Claim Something Doesn't Exist

If you cannot find something:
- SAY: "I couldn't find [X] in my documentation corpus"
- DO NOT SAY: "[X] doesn't exist in SysML v2"
```

**Acceptance Criteria**:
- [ ] Agent prompt updated with INDEX.md-first strategy
- [ ] "Never claim doesn't exist" rule added
- [ ] Agent uses targeted reads with offset/limit

---

### P1-1: Add Validation Agent
**Effort**: 3-4 hours
**Dependencies**: None
**Status**: TODO

Create `claude/agents/sysmlv2-validator.md` to test SysML v2 snippets with `syside check`.

**Purpose**: When user asks "does this work?" or reports syntax errors, validate with actual parser.

**Agent workflow**:
1. Write snippet to temp file
2. Run `uv run syside check <file>`
3. Interpret results and suggest fixes (especially imports)

**Acceptance Criteria**:
- [ ] Agent can write temp files and run syside check
- [ ] Agent suggests imports for "No Type named X" errors
- [ ] Agent cleans up temp files

---

### P1-2: Create Standard Library Quick Reference
**Effort**: 2-3 hours
**Dependencies**: P0-2
**Status**: TODO

While INDEX.md helps find sections, a dedicated `STANDARD_LIBRARY_REFERENCE.md` would provide:
- Function signatures in table format
- Import examples for each package
- Common usage patterns

This can be auto-generated from INDEX.md section 9.4 content or from `.kerml` source files.

**Acceptance Criteria**:
- [ ] Reference file at `docs/sysmlv2/STANDARD_LIBRARY_REFERENCE.md`
- [ ] All Kernel Function Library packages documented
- [ ] Import patterns shown for each package

---

### P1-3: Add Kernel Library Files to Searchable Corpus
**Effort**: 2-3 hours
**Dependencies**: None
**Status**: TODO

Copy `.kerml` files to docs directory for direct grepping:
```bash
mkdir -p docs/sysmlv2/kernel_library
cp -r .venv/lib/python3.12/site-packages/syside/sysml.library/Kernel\ Libraries/* \
      docs/sysmlv2/kernel_library/
```

**Acceptance Criteria**:
- [ ] Agent can grep for function names in .kerml source
- [ ] Files are tracked/versioned appropriately

---

### P2-1: Generate Indexes for All Specs
**Effort**: 1-2 hours (mostly wait time)
**Dependencies**: P0-2
**Status**: TODO

Run `generate_index.py` on all spec documents:
```bash
python3 scripts/generate_index.py docs/sysmlv2/SysML_Spec_v2_Part2/
python3 scripts/generate_index.py docs/sysmlv2/SysML_Spec_v2_Part3/
```

**Acceptance Criteria**:
- [ ] All `full_document.md` files have companion INDEX.md
- [ ] All indexes use consistent depth (3)

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
└── P0-2: Generate section indexes ✅
    └── [Milestone: Agent CAN find "sum" in INDEX.md]

Next (This Week):
├── P0-3: Update agent prompt (1 hour)
│   └── [Milestone: Agent USES INDEX.md effectively]
├── P1-1: Add validation agent (3-4 hours)
└── P1-2: Create quick reference (2-3 hours)
    └── [Milestone: Complete discoverability solution]

Later:
├── P1-3: Add .kerml to corpus (2-3 hours)
├── P2-1: Index all specs (1-2 hours)
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
