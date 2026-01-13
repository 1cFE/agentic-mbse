# Plan: Extract Missing PDF Specifications

**Spec:** `spec.md` (this directory)
**Status:** Complete ✅
**Last Updated:** 2026-01-12T21:55:00+00:00

---

## Final Progress

| Step | Status | Notes |
|------|--------|-------|
| 1. Setup m-scout PDF environment | ✅ Done | `bash ~/m-scout/tools/pdf_processing/scripts/setup_pdf_processor.sh` |
| 2. Extract KerML spec | ✅ Done | Docling, 30 min on CPU, `full_document.md` usable |
| 3. Copy KerML to agentic-mbse | ✅ Done | `docs/sysmlv2/SysML_KerMLSpec/full_document.md` |
| 4. Extract Part1 spec | ✅ Done | **PyMuPDF** (Docling OOM killed), fast, better chunks |
| 5. Copy Part1 to agentic-mbse | ✅ Done | `docs/sysmlv2/SysML_Spec_v2_Part1/full_document.md` |
| 6. Verify agent searchability | ✅ Done | Both docs grep-searchable |

---

## Files Created

```
/home/reid/1cfe/agentic-mbse/docs/sysmlv2/
├── SysML_KerMLSpec/
│   └── full_document.md    ← NEW (1.17 MB, 13,957 lines) - Docling
└── SysML_Spec_v2_Part1/
    └── full_document.md    ← NEW (1.37 MB, 47,797 lines) - PyMuPDF
```

---

## Extraction Results Comparison

| Metric | KerML (Docling) | Part1 (PyMuPDF) |
|--------|-----------------|-----------------|
| File size | 1.17 MB | 1.37 MB |
| Lines | 13,957 | 47,797 |
| Chunks | 1,432 (broken) | 118 (usable) |
| Chunk size | 1-70 lines (fragmented) | 3-2,030 lines (meaningful) |
| Encoding issues | 0 | 0 |
| Processing time | ~30 min | ~5 min |
| Memory usage | High (OOM on Part1) | Low |

**Winner: PyMuPDF** for these technical specs.

---

## Best Practices Discovered

### Recommended Extraction Method: PyMuPDF

```bash
cd /home/reid/m-scout && source pdf_env/bin/activate
PYTHONPATH=/home/reid/m-scout python tools/pdf_processing/processors/pdf_process.py \
    --pymupdf --force \
    /path/to/document.pdf
```

| Setting | Value | Rationale |
|---------|-------|-----------|
| Processor | `--pymupdf` | Lower memory, better chunks, faster |
| Force | `--force` | Overwrite existing partial extractions |

### Why PyMuPDF over Docling

| Aspect | Docling | PyMuPDF |
|--------|---------|---------|
| Memory | High (ML models) | Low (no ML) |
| Speed | Slow (~30 min) | Fast (~5 min) |
| Chunk quality | Terrible (1-line fragments) | Good (meaningful sections) |
| Structure preservation | Over-aggressive splitting | Balanced |
| OOM risk | High on large PDFs | Low |

### Key Findings

1. **Skip the chunks from either processor, use `full_document.md`**
   - Docling chunks: 77% under 500 bytes (useless)
   - PyMuPDF chunks: Better but still not ideal for RAG
   - Both produce grep-searchable `full_document.md`
   - Use new markdown-chunker-indexer utility for proper chunking (see `../markdown-chunker-indexer/spec.md`)

2. **PyMuPDF is the right choice for SysML specs**
   - Docling's ML models are overkill for well-structured PDFs
   - PyMuPDF handles tables and structure adequately
   - Much faster iteration cycle

3. **Encoding quality**
   - Both KerML and Part1: Clean (no garbled characters)
   - Existing Part2: Has 1,331 "¥" symbols - needs re-extraction with PyMuPDF

### Recommended Future Workflow

```
PDF → PyMuPDF (full_document.md only) → Markdown Chunker/Indexer → Indexed Chunks
      ↑                                  ↑
      Fast, low memory                   New utility (spec'd)
```

---

## Verification Results

### KerML Spec
```bash
$ grep -c "NumericalFunctions" docs/sysmlv2/SysML_KerMLSpec/full_document.md
3

$ grep "function sum" docs/sysmlv2/SysML_KerMLSpec/full_document.md | wc -l
7
```
✅ Standard library functions are discoverable.

### Part1 Spec
```bash
$ grep -c "SysML" docs/sysmlv2/SysML_Spec_v2_Part1/full_document.md
711

$ wc -l docs/sysmlv2/SysML_Spec_v2_Part1/full_document.md
47797
```
✅ Content is searchable and complete.

---

## Acceptance Criteria Status

From spec.md:

- [x] KerML extraction succeeds (`processing_completed: true`)
- [x] Part1 extraction succeeds (`processing_completed: true`)
- [x] `grep "NumericalFunctions"` finds matches in KerML docs (3 matches)
- [x] Both directories copied to `docs/sysmlv2/`
- [x] Existing docs in `docs/sysmlv2/` unchanged

**Note:** Chunk quality criteria not met (Docling chunks broken), but `full_document.md` is sufficient for grep-based agent searches. Proper chunking deferred to markdown-chunker-indexer utility.

---

## Follow-up Work

1. **Re-extract Part2 with PyMuPDF** - Fix 1,331 garbled "¥" characters
2. **Build markdown-chunker-indexer** - See `../markdown-chunker-indexer/spec.md`
3. **Update sysmlv2-doc-analyzer agent** - Point to new indexed structure

---

## Commands Reference

### PyMuPDF Extraction (Recommended)
```bash
cd /home/reid/m-scout && source pdf_env/bin/activate
PYTHONPATH=/home/reid/m-scout python tools/pdf_processing/processors/pdf_process.py \
    --pymupdf --force /path/to/document.pdf
```

### Copy full_document.md Only
```bash
mkdir -p /home/reid/1cfe/agentic-mbse/docs/sysmlv2/<DocName>
cp /home/reid/fusion_modeling/agent_literature/SysML/<DocName>/full_document.md \
   /home/reid/1cfe/agentic-mbse/docs/sysmlv2/<DocName>/
```

### Verify Extraction Quality
```bash
# Check for encoding issues
grep -c "¥" <full_document.md>

# Check searchability
grep -c "<keyword>" <full_document.md>

# Check file size
wc -l <full_document.md>
```
