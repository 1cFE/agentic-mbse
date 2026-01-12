# Plan: Extract Missing PDF Specifications

**Spec:** `spec.md` (this directory)
**Status:** In Progress
**Last Updated:** 2026-01-12T20:45:00+00:00

---

## Current Progress

| Step | Status | Notes |
|------|--------|-------|
| 1. Setup m-scout PDF environment | ✅ Done | `bash ~/m-scout/tools/pdf_processing/scripts/setup_pdf_processor.sh` |
| 2. Extract KerML spec | ✅ Done | 30 min on CPU, 1,432 chunks (fragmented), `full_document.md` usable |
| 3. Copy KerML to agentic-mbse | ✅ Done | `docs/sysmlv2/SysML_KerMLSpec/full_document.md` |
| 4. Extract Part1 spec | ⏳ Running | User running manually (~90 min expected on CPU) |
| 5. Copy Part1 to agentic-mbse | ⏸️ Pending | Wait for extraction to complete |
| 6. Verify agent searchability | ⏸️ Pending | grep tests for "NumericalFunctions", "sum", etc. |

---

## Files Created

```
/home/reid/1cfe/agentic-mbse/docs/sysmlv2/
├── SysML_KerMLSpec/
│   └── full_document.md    ← NEW (1.17 MB, 13,957 lines)
└── SysML_Spec_v2_Part1/
    └── (pending)           ← User running extraction
```

---

## Extraction Commands

### KerML Spec (completed)
```bash
cd /home/reid/m-scout && source pdf_env/bin/activate
PYTHONPATH=/home/reid/m-scout python tools/pdf_processing/processors/pdf_process.py \
    --docling --use-hybrid-chunker --max-chunk-tokens 10000 \
    /home/reid/fusion_modeling/agent_literature/SysML/SysML_KerMLSpec.pdf
```

### Part1 Spec (user running)
```bash
cd /home/reid/m-scout && source pdf_env/bin/activate
PYTHONPATH=/home/reid/m-scout python tools/pdf_processing/processors/pdf_process.py \
    --docling --use-hybrid-chunker --max-chunk-tokens 10000 --force \
    /home/reid/fusion_modeling/agent_literature/SysML/SysML_Spec_v2_Part1.pdf
```

### Copy Commands (after Part1 completes)
```bash
# Copy Part1 full_document.md only (skip broken chunks)
mkdir -p /home/reid/1cfe/agentic-mbse/docs/sysmlv2/SysML_Spec_v2_Part1
cp /home/reid/fusion_modeling/agent_literature/SysML/SysML_Spec_v2_Part1/full_document.md \
   /home/reid/1cfe/agentic-mbse/docs/sysmlv2/SysML_Spec_v2_Part1/
```

### Verification Commands
```bash
# Test KerML searchability
grep -c "NumericalFunctions" /home/reid/1cfe/agentic-mbse/docs/sysmlv2/SysML_KerMLSpec/full_document.md
grep "function sum" /home/reid/1cfe/agentic-mbse/docs/sysmlv2/SysML_KerMLSpec/full_document.md | head -3

# Test Part1 searchability (after copy)
grep -c "SysML" /home/reid/1cfe/agentic-mbse/docs/sysmlv2/SysML_Spec_v2_Part1/full_document.md
```

---

## Best Practices Discovered

### Optimal Extraction Settings

| Setting | Value | Rationale |
|---------|-------|-----------|
| Processor | `--docling` | Better structure preservation than PyMuPDF |
| Chunker | `--use-hybrid-chunker` | Enables `merge_peers=True` for less fragmentation |
| Max tokens | `--max-chunk-tokens 10000` | Higher value reduces fragmentation (though still problematic) |
| Environment | `PYTHONPATH=/home/reid/m-scout` | Required for imports to work |

### Key Findings

1. **Skip the chunks, use `full_document.md`**
   - Docling's chunking is fundamentally broken for these specs
   - 77% of chunks are under 500 bytes (1-line fragments)
   - The `full_document.md` is grep-searchable and sufficient for agent use
   - A separate chunking/indexing utility is planned (see `../markdown-chunker-indexer/spec.md`)

2. **Encoding quality varies by document**
   - KerML extraction: Clean (no garbled characters)
   - Part2 (existing): Has 1,331 "¥" symbols (garbled bullet points) - needs re-extraction
   - Part1: TBD (check after extraction completes)

3. **Processing time on CPU**
   - KerML (1.7 MB): ~30 minutes
   - Part1 (5.4 MB): ~90 minutes estimated
   - Consider GPU if available for future extractions

4. **NNPACK warnings are harmless**
   - Thousands of `Could not initialize NNPACK! Reason: Unsupported hardware` warnings
   - Just means GPU acceleration unavailable, CPU fallback works fine
   - Does not affect output quality

### Recommended Future Workflow

```
PDF → Docling (full_document.md only) → Markdown Chunker/Indexer → Indexed Chunks
      ↑                                  ↑
      Skip chunk generation              New utility (spec'd)
```

1. Extract PDF to `full_document.md` using Docling
2. **Skip** Docling's built-in chunking (it's broken)
3. Use new markdown-chunker-indexer utility (when built) to create proper chunks with:
   - Hierarchy-aware splitting
   - YAML frontmatter with breadcrumb context
   - Multi-tier index with hyperlinks

---

## Quality Assessment

### KerML Extraction

| Metric | Value | Assessment |
|--------|-------|------------|
| File size | 1.17 MB | ✓ Complete |
| Line count | 13,957 | ✓ Substantial |
| "NumericalFunctions" mentions | 3 | ✓ Searchable |
| "function sum" definitions | 7 | ✓ Content present |
| Garbled characters (¥) | 0 | ✓ Clean encoding |
| Chunk quality | Poor (1,432 fragments) | ✗ Don't use chunks |

### Part1 Extraction (pending)

| Metric | Value | Assessment |
|--------|-------|------------|
| Processing | In progress | ~90 min on CPU |
| Expected size | ~3-4 MB | Based on PDF size ratio |

---

## Related Work

- **This feature:** P0-1 in epic_documentation-discoverability.md
- **Next feature:** `../markdown-chunker-indexer/spec.md` - proper chunking solution
- **Blocked:** P0-2 (Standard Library Quick Reference) - needs indexed chunks

---

## Resume Checklist

When resuming this work:

1. [ ] Check if Part1 extraction completed:
   ```bash
   ls -la /home/reid/fusion_modeling/agent_literature/SysML/SysML_Spec_v2_Part1/
   cat /home/reid/fusion_modeling/agent_literature/SysML/SysML_Spec_v2_Part1/summary.json
   ```

2. [ ] If complete, copy `full_document.md` to agentic-mbse:
   ```bash
   mkdir -p /home/reid/1cfe/agentic-mbse/docs/sysmlv2/SysML_Spec_v2_Part1
   cp /home/reid/fusion_modeling/agent_literature/SysML/SysML_Spec_v2_Part1/full_document.md \
      /home/reid/1cfe/agentic-mbse/docs/sysmlv2/SysML_Spec_v2_Part1/
   ```

3. [ ] Verify searchability:
   ```bash
   grep -c "SysML" /home/reid/1cfe/agentic-mbse/docs/sysmlv2/SysML_Spec_v2_Part1/full_document.md
   ```

4. [ ] Check for encoding issues:
   ```bash
   grep -c "¥" /home/reid/1cfe/agentic-mbse/docs/sysmlv2/SysML_Spec_v2_Part1/full_document.md
   ```

5. [ ] Update spec.md status to "Complete" if all acceptance criteria met
