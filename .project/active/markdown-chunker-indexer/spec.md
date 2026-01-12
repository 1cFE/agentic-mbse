# Spec: Markdown Chunker & Indexer

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-01-12T20:30:00+00:00
**Complexity:** MEDIUM
**Epic:** `.project/backlog/epic_documentation-discoverability.md`

---

## Business Goals

### Why This Matters

The current PDF extraction pipeline (Docling) produces `full_document.md` files that are searchable but creates unusable chunks - 77% are under 500 bytes (single-line fragments). Agents cannot effectively discover documentation because:

1. **No hierarchy context** - Section 7.6.3.1 is meaningless without knowing what Section 7, 7.6, and 7.6.3 contain
2. **No intelligent traversal** - Agents must grep blindly rather than navigate a semantic roadmap
3. **No multi-document routing** - No way to know whether KerML, Part1, Part2, or Part3 has the answer

This utility creates a post-processing step that transforms raw `full_document.md` into properly structured, indexed chunks that enable agent-based document discovery.

### Success Criteria

- [ ] Agent can identify which document (KerML/Part1/Part2/Part3) contains "NumericalFunctions::sum"
- [ ] Agent can navigate from document index → relevant section → specific chunk
- [ ] Each chunk is self-contained with enough context to be useful independently
- [ ] Index structure supports both grep-based search and future vector search
- [ ] All state lives in markdown files (no external database)

### Priority

High - This is the structural foundation for all documentation discoverability improvements. Blocks P0-2 (Standard Library Quick Reference) and enables the sysmlv2-doc-analyzer agent to actually work.

---

## Problem Statement

### Current State

The m-scout PDF processing pipeline produces:
- `full_document.md` - Complete markdown (1.1MB, 14K lines) - **searchable but unwieldy**
- `chunks/chunk_NNN.md` - 1,432 tiny fragments - **useless for retrieval**

**Chunk analysis (KerML spec):**
| Size bucket | Count | Percentage |
|-------------|-------|------------|
| < 500 bytes | 1,113 | 77.7% |
| 500-1000 bytes | 92 | 6.4% |
| 1000-5000 bytes | 181 | 12.6% |
| > 5000 bytes | 46 | 3.2% |

Root causes:
- Docling's `respect_headers=True` breaks at every header regardless of size
- No post-processing to consolidate micro-chunks
- Hierarchy info captured but not actionable
- No frontmatter, no document context, generic naming

### Desired Outcome

A **markdown post-processor** that takes `full_document.md` and produces:

1. **Meaningful chunks** - Individual `.md` files with 256-512 tokens, self-contained with context
2. **Rich frontmatter** - YAML metadata with breadcrumb/stack, parent section summaries
3. **Multi-tier index** - Markdown/YAML files with hyperlinks enabling agent traversal
4. **Future-ready** - Structure supports adding embeddings for vector search later

---

## Scope

### In Scope

1. **Markdown Chunker**
   - Input: `full_document.md` (from Docling extraction)
   - Output: Individual `.md` chunk files with YAML frontmatter
   - Hierarchy-aware splitting (respects headers but consolidates small sections)
   - Configurable chunk size with overlap

2. **Frontmatter Generator**
   - Breadcrumb/stack context (Section 7 > 7.6 > 7.6.3 > 7.6.3.1)
   - Parent section titles and summaries
   - Source document reference
   - Chunk position metadata

3. **Index Generator**
   - Document-level index (which spec has what content)
   - Section-level index with summaries and hyperlinks
   - Supports agent traversal via links
   - Markdown or YAML format (determine in design)

4. **Vector Search Foundation**
   - Design chunk structure to support future embedding storage
   - Trade study in design phase for embedding approach

### Out of Scope

- PDF extraction (use existing m-scout Docling pipeline)
- ChromaDB or external database integration
- Modifications to sysmlv2-doc-analyzer agent (separate effort)
- Real-time embedding generation in v1 (design for it, implement later)
- Automatic re-indexing on source changes

### Edge Cases & Considerations

- **Very short sections**: Some spec sections are just 1-2 sentences - need minimum chunk size or consolidation with siblings
- **Code blocks**: KerML syntax blocks should not be split mid-block
- **Tables**: Spec contains many tables - preserve table integrity
- **Cross-references**: Specs reference other sections - capture these in metadata?
- **Nested headers**: Some specs go 5+ levels deep (7.6.3.1.2) - how deep to track?

---

## Requirements

### Functional Requirements

1. **FR-1**: Utility MUST accept `full_document.md` as input and produce individual `.md` chunk files
2. **FR-2**: Each chunk file MUST include YAML frontmatter with breadcrumb/stack context showing parent section hierarchy
3. **FR-3**: Frontmatter MUST include parent section titles (e.g., what is Section 7 about, what is 7.6 about)
4. **FR-4**: Utility MUST generate index file(s) with summaries and hyperlinks to enable agent traversal
5. **FR-5**: Index SHOULD support multi-tier navigation (document → section → chunk)
6. **FR-6**: Chunks SHOULD target 256-512 tokens with configurable overlap
7. **FR-7**: Chunking MUST preserve code block and table integrity (no mid-element splits)
8. **FR-8**: [INFERRED] Utility SHOULD be runnable as CLI tool for integration with existing workflows
9. **FR-9**: [INFERRED] Output structure MUST be compatible with Claude Code file discovery (individual .md files)

### Non-Functional Requirements

- **NFR-1**: All state MUST live in markdown/YAML files (no external database)
- **NFR-2**: Output SHOULD be human-readable (not just machine-readable)
- **NFR-3**: Design SHOULD enable future vector search integration without restructuring

---

## Acceptance Criteria

### Core Functionality

- [ ] Running utility on KerML `full_document.md` produces chunk files with frontmatter
- [ ] Each chunk frontmatter includes breadcrumb path (e.g., `stack: ["8. Syntax", "8.2 Lexical Structure", "8.2.2 Literals"]`)
- [ ] Each chunk frontmatter includes parent section summaries
- [ ] Index file(s) generated with hyperlinks to chunk files
- [ ] Chunk files average 256-512 tokens (not 1-line fragments)
- [ ] Code blocks and tables are not split mid-element

### Quality & Integration

- [ ] Output chunks are valid markdown with valid YAML frontmatter
- [ ] Index hyperlinks resolve correctly
- [ ] Utility can process all 4 SysML specs (KerML, Part1, Part2, Part3)
- [ ] Processing time reasonable (< 1 min per document)

---

## Research Summary

### Chunking Best Practices (from research)

| Strategy | Best For | Our Use |
|----------|----------|---------|
| Markdown Header Splitting | Structured docs | Primary - split on headers |
| Recursive Character Splitting | Large sections | Secondary - split oversized chunks |
| Semantic Chunking | Knowledge bases | Future - with embeddings |

**Recommended hybrid approach:**
1. First pass: Split on markdown headers (preserve structure)
2. Second pass: Recursively split any chunks exceeding target size
3. Store full header hierarchy as frontmatter metadata

### Context Preservation Techniques

**Breadcrumb Pattern** - Most applicable to our needs:
```yaml
---
source: SysML_KerMLSpec.pdf
chunk_id: kerml-8.2.2.4
breadcrumb: "8. Syntax > 8.2 Lexical Structure > 8.2.2 Literals > 8.2.2.4 Numeric Values"
stack:
  - title: "8. Syntax"
    summary: "Defines the textual notation grammar for KerML"
  - title: "8.2 Lexical Structure"
    summary: "Lexical elements: whitespace, comments, identifiers, literals"
  - title: "8.2.2 Literals"
    summary: "Boolean, string, and numeric literal syntax"
---
# 8.2.2.4 Numeric Values

DECIMAL_VALUE = DECIMAL_DIGIT+
EXPONENTIAL_VALUE = DECIMAL_VALUE ('e' | 'E') ('+' | '-')? DECIMAL_VALUE
```

### Lightweight Vector Search Options

| Option | Pros | Cons |
|--------|------|------|
| Faiss + JSON | Fast, file-based, git-friendly | Separate embedding files |
| Frontmatter embeddings | Self-contained | Large files, slow to parse |
| NumPy arrays | Simplest, no deps | Memory limits at scale |
| Design-only (v1) | Ship faster | No vector search initially |

**Recommendation:** Design for Faiss + JSON in v1, implement in v2.

### Tools Identified

- **Chonkie** - Lightweight chunking library (9.7MB), multiple strategies
- **md2chunks** - Context-enriched markdown chunking with hierarchy
- **sentence-transformers** - Local embeddings when needed
- **Faiss** - File-based vector index for future use

---

## Example Output Structure

```
docs/sysmlv2/SysML_KerMLSpec/
├── full_document.md          # Original extraction (keep for reference)
├── INDEX.md                  # Document-level index with section summaries
├── chunks/
│   ├── 001_introduction.md   # Named chunks with frontmatter
│   ├── 002_scope.md
│   ├── 008_syntax_overview.md
│   ├── 008.2_lexical_structure.md
│   ├── 008.2.2_literals.md
│   ├── 008.2.2.4_numeric_values.md
│   └── ...
└── sections/                 # Optional: section-level indices
    ├── 08_syntax.md          # Index for Section 8 with links to chunks
    └── ...
```

**INDEX.md example:**
```markdown
# SysML KerML Specification Index

## Document Overview
The Kernel Modeling Language (KerML) specification defines...

## Sections

### [1. Scope](chunks/001_scope.md)
Defines the scope and purpose of the KerML specification.

### [8. Syntax](sections/08_syntax.md)
Defines the textual notation grammar for KerML.
- [8.2 Lexical Structure](chunks/008.2_lexical_structure.md)
- [8.2.2 Literals](chunks/008.2.2_literals.md)
  - [8.2.2.4 Numeric Values](chunks/008.2.2.4_numeric_values.md)

### [9. Standard Library](sections/09_standard_library.md)
Defines built-in types and functions.
- [9.2 Numerical Functions](chunks/009.2_numerical_functions.md) ← *Contains sum, product, abs*
```

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_documentation-discoverability.md`
- **Predecessor:** `.project/active/extract-missing-pdf-specs/spec.md` (P0-1)
- **Research:** Embedded in this spec (from subagent research)
- **Design:** `.project/active/markdown-chunker-indexer/design.md` (to be created)

---

## Open Questions for Design Phase

1. **Index format**: Markdown with links vs YAML with paths - trade-offs?
2. **Chunk naming**: Hierarchical (008.2.2.4_...) vs sequential (chunk_042)?
3. **Summary generation**: Manual vs LLM-generated vs extracted from content?
4. **Embedding storage**: Frontmatter vs separate files vs deferred?
5. **Section consolidation**: When to merge small sibling sections?

---

**Next Steps:** After approval, proceed to `/_my_design` for architecture and trade studies
