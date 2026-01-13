# Spec: Documentation Index Tooling

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-01-12T22:45:00+00:00
**Completed:** 2026-01-13T00:45:00+00:00
**Complexity:** MEDIUM
**Epic:** `.project/backlog/epic_documentation-discoverability.md`

---

## Business Goals

### Why This Matters

Our sysmlv2-doc-analyzer agent fails to help users discover standard library functions because it lacks a navigable index of documentation structure. Users spent hours searching for `NumericalFunctions::sum` that existed all along.

Rather than chunking documents into fragments, we need a lightweight indexing approach: a structured `INDEX.md` file that maps section numbers to line ranges with AI-generated summaries. This gives agents (and humans) a roadmap of what's in each document without the complexity of a chunking pipeline.

### Success Criteria

- [x] Agent can quickly identify which section contains "NumericalFunctions" by reading INDEX.md
- [x] Human users can navigate large spec documents using section numbers
- [x] Index generation is automated and reproducible
- [x] Indexes are version-controlled alongside source documents

### Priority

High - This is the structural foundation for documentation discoverability improvements. Enables P0-2 (Standard Library Quick Reference) and improves sysmlv2-doc-analyzer effectiveness.

---

## Problem Statement

### Current State

- `full_document.md` files exist (14K-48K lines) but have no navigable structure
- Agent must grep blindly, then guess appropriate offset/limit for reading
- No summaries of what each section contains
- Docling's chunk output is unusable (77% under 500 bytes)

### Desired Outcome

- Every `full_document.md` has a companion `INDEX.md` with:
  - Section hierarchy with line numbers
  - AI-generated summaries describing each section's content
  - Machine-parseable format for tooling
- Scripts to generate indexes and read specific sections

---

## Scope

### In Scope

1. **`generate_index.py`** - Script to create INDEX.md from full_document.md
   - Parses numbered section headers (e.g., "## 7.2.1 Title")
   - Calls Claude headless to generate 1-2 sentence summaries
   - Outputs structured INDEX.md with YAML frontmatter
   - Supports configurable depth (default: 3)
   - Uses checksums for incremental updates

2. **`read_section.py`** - Script to read a specific section from a document
   - Parses INDEX.md to find line ranges
   - Reads full_document.md with appropriate offset/limit
   - Convenience tool primarily for human users

3. **INDEX.md format specification**
   - Human-readable markdown
   - Machine-parseable structure (regex-extractable line numbers)
   - YAML frontmatter with metadata and checksums

### Out of Scope

- Physical chunking of documents into separate files
- Vector embeddings or semantic search
- Automatic re-indexing on file changes (manual trigger only)
- Integration with sysmlv2-doc-analyzer agent (separate task)
- Processing non-numbered-section documents

### Edge Cases & Considerations

- **Very short sections**: Some sections are 2-4 lines. Still index them; summary may note "brief overview" or similar.
- **Missing sections in hierarchy**: Document may have 7.1, 7.3 but no 7.2. Handle gracefully.
- **Non-standard headers**: Some `##` headers aren't numbered sections (e.g., "## Notes"). Skip these.
- **Large sections**: Some sections exceed 1000 lines. Summary should note this.
- **Unicode issues**: Some PDF extractions have encoding artifacts. Don't fail on these.
- **Existing INDEX.md**: Use checksums to determine if regeneration needed.

---

## Requirements

### Functional Requirements

#### Script 1: `generate_index.py`

1. **FR-1**: Script MUST accept a path to `full_document.md` or its containing folder
2. **FR-2**: Script MUST parse markdown headers matching pattern `^## (\d+(?:\.\d+)*)\s+(.+)$`
3. **FR-3**: Script MUST calculate line ranges for each section (start line to next section start - 1)
4. **FR-4**: Script MUST build breadcrumb hierarchy (e.g., "7 Language > 7.2 Root" for section 7.2.1)
5. **FR-5**: Script MUST call `claude -p` to generate a 1-2 sentence summary for each section
6. **FR-6**: Script MUST output INDEX.md in the same directory as full_document.md
7. **FR-7**: Script MUST include YAML frontmatter with:
   - `document`: Base name of the document
   - `generated`: ISO 8601 timestamp
   - `source_checksum`: MD5/SHA256 of full_document.md
   - `total_lines`: Line count
   - `depth`: Max depth indexed
   - `section_count`: Number of sections indexed
8. **FR-8**: Script MUST support `--depth INT` option (default: 3)
9. **FR-9**: Script MUST support `--force` flag to regenerate even if checksums match
10. **FR-10**: Script MUST support `--dry-run` flag to show sections without generating summaries
11. **FR-11**: Script SHOULD skip regeneration if source_checksum in existing INDEX.md matches current file
12. **FR-12**: Script SHOULD use Claude Haiku model for summaries (cost efficiency)
13. **FR-13**: Script SHOULD show progress during summary generation (e.g., "Processing section 15/111...")

#### Script 2: `read_section.py`

14. **FR-14**: Script MUST accept document path and section number as arguments
15. **FR-15**: Script MUST parse INDEX.md to find line range for requested section
16. **FR-16**: Script MUST read full_document.md with appropriate offset/limit
17. **FR-17**: Script MUST output section content with header showing section info and line range
18. **FR-18**: Script SHOULD support `--context INT` for extra lines before/after (default: 0)
19. **FR-19**: Script SHOULD support `--raw` flag to output content only without header
20. **FR-20**: Script MUST exit with clear error if section not found in INDEX.md

#### INDEX.md Format

21. **FR-21**: INDEX.md MUST use markdown headers matching section depth (## for depth 1, ### for depth 2, etc.)
22. **FR-22**: Each section entry MUST include `**Lines:** {start}-{end}` for machine parsing
23. **FR-23**: Each section entry MUST include AI-generated summary (1-2 sentences)
24. **FR-24**: Parent sections SHOULD include `**Subsections:** 7.1, 7.2, 7.3` listing
25. **FR-25**: INDEX.md MUST be valid markdown that renders well in GitHub/viewers

### Non-Functional Requirements

26. **NFR-1**: Summary generation for 100+ sections SHOULD complete in < 10 minutes
27. **NFR-2**: Scripts MUST work with Python 3.10+ without additional dependencies beyond stdlib
28. **NFR-3**: Scripts MUST handle documents up to 50K lines
29. **NFR-4**: Scripts MUST provide clear error messages for common failure modes

---

## Acceptance Criteria

### Core Functionality

- [ ] `generate_index.py docs/sysmlv2/SysML_KerMLSpec/` creates INDEX.md
- [ ] INDEX.md contains all depth-3 sections with line numbers
- [ ] Each section has an AI-generated summary
- [ ] Running script again with unchanged source skips regeneration (checksum match)
- [ ] Running with `--force` regenerates regardless of checksum
- [ ] Running with `--dry-run` shows sections without calling Claude
- [ ] `read_section.py docs/sysmlv2/SysML_KerMLSpec/ 9.4` outputs Function Library content
- [ ] Line numbers in INDEX.md are accurate (verified by spot-checking)

### Quality & Integration

- [ ] Scripts are executable (`chmod +x`)
- [ ] Scripts have `--help` output explaining usage
- [ ] Scripts work on all existing `full_document.md` files in `docs/sysmlv2/`
- [ ] INDEX.md renders correctly in GitHub markdown preview
- [ ] No external Python dependencies required

---

## Technical Notes

### INDEX.md Structure

```markdown
---
document: SysML_KerMLSpec
generated: 2026-01-12T22:45:00Z
source_checksum: sha256:abc123...
total_lines: 13957
depth: 3
section_count: 111
---

# SysML KerML Specification Index

## 7 Language Description
**Lines:** 959-2845 | **Subsections:** 7.1, 7.2, 7.3, 7.4

Informative description of KerML constructs and usage patterns covering Root, Core, and Kernel layers.

### 7.1 Language Description Overview
**Lines:** 963-974

Introduces the three-layer structure and notation conventions used in examples.

### 7.2 Root
**Lines:** 975-1262 | **Subsections:** 7.2.1, 7.2.2, 7.2.3

Root layer providing elements, relationships, annotations, and namespaces.

#### 7.2.1 Root Overview
**Lines:** 977-980

Brief overview of Root layer capabilities.

...
```

### Header Parsing Pattern

```python
# Match numbered sections like "## 7.2.1 Title"
pattern = re.compile(r'^## (\d+(?:\.\d+)*)\s+(.+)$')
```

### Claude Headless Invocation

```bash
claude -p "Summarize this documentation section in 1-2 sentences. Focus on what concepts or functions it defines, not meta-commentary. Section: {title}

{content}"
```

### Checksum Comparison

```python
import hashlib

def get_file_checksum(path: Path) -> str:
    content = path.read_bytes()
    return f"sha256:{hashlib.sha256(content).hexdigest()}"
```

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_documentation-discoverability.md`
- **Research:** `project/research/20260112-222249_chunking-indexing-strategy.md`
- **Design:** `.project/active/doc-index-tooling/design.md` (to be created if needed)

---

## Open Questions

1. **Summary prompt tuning**: Should we iterate on the prompt to get better summaries, or is a simple prompt sufficient?
2. **Section content limits**: For very large sections (1000+ lines), should we truncate content sent to Claude for summarization?
3. **Header pattern variants**: Some documents may use `#` instead of `##` for top-level sections. Support both?

---

**Next Steps:** After approval, proceed to implementation (complexity is low enough to skip detailed design)
