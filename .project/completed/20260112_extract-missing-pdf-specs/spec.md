# Spec: Extract Missing PDF Specifications

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-01-12T16:19:10+00:00
**Complexity:** LOW
**Epic:** `.project/backlog/epic_documentation-discoverability.md` (P0-1)

---

## Business Goals

### Why This Matters

The sysmlv2-doc-analyzer agent consistently fails to help users discover standard library functions like `NumericalFunctions::sum`. A team spent hours trying to find a basic function that existed all along. The root cause: we never extracted the KerML specification (which defines the standard library) from PDF to searchable markdown.

This is the critical first step in the documentation discoverability overhaul. Without extracted specs, downstream improvements (quick reference, agent prompt updates) have no authoritative source to reference.

### Success Criteria

- [ ] Agent can grep for "NumericalFunctions" in extracted KerML documentation
- [ ] Agent can grep for standard library definitions in extracted content
- [ ] Extracted documents are in agent-searchable location (`docs/sysmlv2/`)

### Priority

P0 (Critical) - Blocking item for documentation discoverability epic. No dependencies; can start immediately.

---

## Problem Statement

### Current State

The `docs/sysmlv2/` directory contains extracted specs for Part2, Part3, and IntroGuide, but is missing:
- **KerML Specification** - Defines the standard library (NumericalFunctions, SequenceFunctions, etc.)
- **Part1 Specification** - Main language specification

These PDFs exist at `/home/reid/fusion_modeling/agent_literature/SysML/` but were never processed.

### Desired Outcome

Both critical PDFs extracted to markdown with hierarchical chunking, copied to `docs/sysmlv2/`, and searchable by the sysmlv2-doc-analyzer agent.

---

## Scope

### In Scope

1. Extract `SysML_KerMLSpec.pdf` using m-scout Docling processor
2. Extract `SysML_Spec_v2_Part1.pdf` using m-scout Docling processor
3. Copy extracted output directories to `agentic-mbse/docs/sysmlv2/`
4. Verify searchability via grep tests

### Out of Scope

- Medium/low priority PDFs (MBSE_20, PySysML Report) - can be added later
- Creating standard library quick reference (P0-2 - separate item)
- Updating agent system prompt (P0-3 - separate item)
- Auto-generating library index from .kerml files (P1-1)

### Edge Cases & Considerations

- **Large documents**: Part1 is ~5.4MB, may produce many chunks. Chunk size tuning needed.
- **Existing partial extractions**: If any partial output exists, use `--force` to reprocess cleanly.
- **Image extraction**: Docling extracts figures as PNGs. These should be preserved but are secondary to text content.

---

## Requirements

### Functional Requirements

1. **FR-1**: Use m-scout Docling processor with hybrid chunker for both PDFs
2. **FR-2**: Tune `--max-chunk-tokens` to produce chunks that are:
   - No more than ~200 lines per chunk document
   - Long enough to capture meaningful sections (chapters, major subsections)
3. **FR-3**: Process both critical PDFs:
   - `/home/reid/fusion_modeling/agent_literature/SysML/SysML_KerMLSpec.pdf`
   - `/home/reid/fusion_modeling/agent_literature/SysML/SysML_Spec_v2_Part1.pdf`
4. **FR-4**: Copy extracted directories to `docs/sysmlv2/`:
   - `SysML_KerMLSpec/` (with full_document.md, chunks/, images/)
   - `SysML_Spec_v2_Part1/` (with full_document.md, chunks/, images/)
5. **FR-5**: [INFERRED] Verify extraction success by checking `summary.json` shows `processing_completed: true`

### Non-Functional Requirements

- **NFR-1**: [INFERRED] Chunk files should have descriptive names reflecting document structure (e.g., `003_Standard_Library.md`)

---

## Acceptance Criteria

### Core Functionality

- [ ] KerML spec extracted to markdown at `docs/sysmlv2/SysML_KerMLSpec/full_document.md`
- [ ] Part1 spec extracted to markdown at `docs/sysmlv2/SysML_Spec_v2_Part1/full_document.md`
- [ ] Both directories include `summary.json` with `processing_completed: true`
- [ ] Chunk files exist in `chunks/` subdirectories

### Verification

- [ ] `grep -r "NumericalFunctions" docs/sysmlv2/SysML_KerMLSpec/` returns matches
- [ ] `grep -r "standard library" docs/sysmlv2/SysML_KerMLSpec/` returns matches
- [ ] Chunk files average no more than ~200 lines each

### Quality & Integration

- [ ] No broken references or corrupted output in extracted markdown
- [ ] Existing docs in `docs/sysmlv2/` are not affected

---

## Implementation Notes

### m-scout Command Reference

```bash
# Correct path (underscore, not hyphen as in epic)
MSCOUT_PDF=/home/reid/m-scout/tools/pdf_processing/processors/pdf_process.py

# Process with Docling + hybrid chunker
python $MSCOUT_PDF --docling --use-hybrid-chunker --max-chunk-tokens <TBD> <pdf_path>

# Force reprocess if needed
python $MSCOUT_PDF --docling --use-hybrid-chunker --force --max-chunk-tokens <TBD> <pdf_path>
```

### Chunk Size Tuning

Default is 5000 tokens. During implementation:
1. Start with a higher value (e.g., 8000-10000 tokens)
2. Check average lines per chunk file
3. Adjust until chunks are ~200 lines or less while capturing meaningful sections
4. Document the final value chosen

### Output Structure

For each PDF `document.pdf`, m-scout creates:
```
document/
├── summary.json          # Processing metadata
├── full_document.md      # Complete markdown conversion
├── chunks/               # Hierarchical text chunks
│   ├── 000_Introduction.md
│   ├── 001_Chapter_1.md
│   └── ...
└── images/               # Extracted figures (PNG)
```

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_documentation-discoverability.md`
- **Research:** `.project/research/20260112-064217_sysmlv2-agent-discoverability-failure.md`
- **Design:** `.project/active/extract-missing-pdf-specs/design.md` (to be created)
- **Source PDFs:** `/home/reid/fusion_modeling/agent_literature/SysML/`
- **m-scout docs:** `/home/reid/m-scout/docs/04-tools-pdf-processing.md`

---

**Next Steps:** After approval, proceed to `/_my_design` (or implement directly given LOW complexity)
