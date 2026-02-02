# Scripts

Scripts for document processing and project setup. These are used to prepare documentation for specialist agents (sysml-expert, kerml-expert, syside-expert).

## Document Processing Overview

The documentation pipeline converts source materials (PDFs, websites) into searchable, indexed markdown that agents can navigate efficiently.

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Source PDFs   │────▶│  m-scout PDF     │────▶│ full_document.md│
│   (SysML specs) │     │  processor       │     │                 │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
┌─────────────────┐     ┌──────────────────┐              ▼
│ docs.sensmetry  │────▶│  m-scout docs    │     ┌─────────────────┐
│ .com            │     │  scraper         │     │ generate_index  │
└─────────────────┘     └──────────────────┘     │ .py             │
                                                  └────────┬────────┘
┌─────────────────┐     ┌──────────────────┐              ▼
│ syside package  │────▶│  sync_stdlib.py  │────▶┌─────────────────┐
│ (installed)     │     │                  │     │ INDEX.md        │
└─────────────────┘     └──────────────────┘     │ (with summaries)│
                                                  └─────────────────┘
```

### Design Decision: INDEX.md vs Physical Chunking

We chose lightweight `INDEX.md` files over physical document chunking because:

1. **Claude's 200K context window** makes physical chunks unnecessary
2. **Grep-based retrieval** with line number offsets is fast and precise
3. **Less complexity** - no chunk database, no embeddings to maintain
4. **Checksum tracking** allows incremental updates when sources change

See `.project/completed/20260113_doc-index-tooling/spec.md` for the full rationale.

---

## Scripts in This Directory

### generate_index.py

Creates `INDEX.md` files from `full_document.md` with AI-generated section summaries.

**Produces:**
- `INDEX.md` with YAML frontmatter (checksum, line counts)
- Hierarchical section headers with line ranges
- 1-2 sentence AI summaries for each section

**Usage:**
```bash
# Generate index for a document
./generate_index.py docs/sysmlv2/SysML_KerMLSpec/

# Preview sections without generating summaries
./generate_index.py --dry-run docs/sysmlv2/SysML_KerMLSpec/

# Force regeneration even if checksum matches
./generate_index.py --force docs/sysmlv2/SysML_KerMLSpec/

# Limit indexing depth (default: 3)
./generate_index.py --depth 2 docs/sysmlv2/SysML_KerMLSpec/
```

**External calls:**
```bash
# Generates summaries via Claude CLI
claude -p "<prompt with section content>"
```

---

### read_section.py

Reads specific sections from documents using INDEX.md line ranges.

**Usage:**
```bash
# Read a section
./read_section.py docs/sysmlv2/SysML_KerMLSpec/ 9.4

# Read with context lines
./read_section.py docs/sysmlv2/SysML_KerMLSpec/ 7.2.1 --context 5

# Raw output (no header)
./read_section.py docs/sysmlv2/SysML_KerMLSpec/ 7 --raw
```

**External calls:** None (pure Python)

---

### sync_stdlib.py

Syncs SysML v2 standard library from the installed syside package to `docs/sysmlv2/stdlib/`.

**Produces:**
- Copies of all `.kerml` and `.sysml` files from syside
- `VERSION.md` with sync metadata
- `INDEX.md` with quick reference tables and file summaries

**Usage:**
```bash
# Sync stdlib (fails if already exists)
./sync_stdlib.py

# Preview what would be synced
./sync_stdlib.py --dry-run

# Overwrite existing stdlib
./sync_stdlib.py --force
```

**External calls:**
```bash
# Generates file summaries via Claude CLI
claude -p "<prompt with file content>"
```

---

### replicate_setup.sh

Development setup script that symlinks Claude commands/agents into `~/.claude/` for testing.

**Usage:**
```bash
./replicate_setup.sh
```

---

## External Tools (m-scout)

These scripts live in `~/m-scout/` and are used for initial document extraction.

### PDF Processor

Extracts PDFs to markdown. Supports two backends: **PyMuPDF** (recommended) and **Docling**.

**Location:** `~/m-scout/tools/pdf_processing/processors/pdf_process.py`

#### PyMuPDF (Recommended)

```bash
cd ~/m-scout && source pdf_env/bin/activate
PYTHONPATH=/home/reid/m-scout python tools/pdf_processing/processors/pdf_process.py \
    --pymupdf --force \
    /path/to/document.pdf
```

#### Docling (Alternative)

```bash
cd ~/m-scout && source pdf_env/bin/activate
PYTHONPATH=/home/reid/m-scout python tools/pdf_processing/processors/pdf_process.py \
    --docling \
    --use-hybrid-chunker \
    --max-chunk-tokens 10000 \
    /path/to/document.pdf
```

#### Why PyMuPDF over Docling

| Aspect | Docling | PyMuPDF |
|--------|---------|---------|
| Memory | High (ML models, OOM on large PDFs) | Low (no ML) |
| Speed | Slow (~30 min) | Fast (~5 min) |
| Chunk quality | Poor (77% under 500 bytes) | Better (meaningful sections) |
| OOM risk | High on large PDFs | Low |

**Recommendation:** Use `--pymupdf` unless you need Docling's ML-based table extraction.

#### What Was Actually Used

| Document | Processor | Settings | Source |
|----------|-----------|----------|--------|
| KerML | Docling | `--docling --use-hybrid-chunker --max-chunk-tokens 10000` | `summary.json` |
| Part1 | PyMuPDF | Docling OOM killed, auto-fallback | `summary.json` |
| Part2, Part3 | Unknown | Extracted earlier, no metadata | - |

Source metadata (where available): `/home/reid/fusion_modeling/agent_literature/SysML/*/summary.json`

**Produces:**
```
document/
├── summary.json          # Processing metadata (processor_used, statistics)
├── full_document.md      # Complete markdown conversion
├── chunks/               # Hierarchical text chunks (deprecated - we use INDEX.md instead)
└── images/               # Extracted figures (PNG)
```

**Documentation:** `~/m-scout/docs/04-tools-pdf-processing.md`

---

### Syside Docs Scraper

Scrapes syside documentation from docs.sensmetry.com.

**Location:** `~/m-scout/tools/syside_docs/scrape_docs.py`

**Usage:**
```bash
# Setup environment
source ~/m-scout/pdf_env/bin/activate

# Edit scraper to set output directory
# OUTDIR = pathlib.Path("/home/reid/1cfe/agentic-mbse/docs/syside/python/vX.Y.Z")

# Run scraper
python ~/m-scout/tools/syside_docs/scrape_docs.py

deactivate
```

**Post-processing:**
1. Update symlinks in `docs/syside/api/` to point to new version
2. Update `docs/syside/VERSION.md`

---

## Processing Checklist

### Adding a New PDF Specification

1. Extract PDF with m-scout (use PyMuPDF):
   ```bash
   cd ~/m-scout && source pdf_env/bin/activate
   PYTHONPATH=/home/reid/m-scout python tools/pdf_processing/processors/pdf_process.py \
       --pymupdf --force /path/to/spec.pdf
   ```

2. Copy to docs:
   ```bash
   cp -r /path/to/spec/ docs/sysmlv2/
   ```

3. Generate index:
   ```bash
   ./scripts/generate_index.py docs/sysmlv2/spec/
   ```

4. Verify:
   ```bash
   grep -r "key term" docs/sysmlv2/spec/
   ./scripts/read_section.py docs/sysmlv2/spec/ 1.1
   ```

### Updating Syside Version

1. Update package: `uv sync` (after updating pyproject.toml)
2. Sync stdlib: `./scripts/sync_stdlib.py --force`
3. Scrape docs (see m-scout scraper section above)
4. Update `docs/syside/VERSION.md`

### Regenerating All Indexes

```bash
for dir in docs/sysmlv2/*/; do
    if [[ -f "$dir/full_document.md" ]]; then
        ./scripts/generate_index.py --force "$dir"
    fi
done
```

---

## Related Documentation

- **Epic:** `.project/completed/epic_documentation-discoverability.md`
- **INDEX.md spec:** `.project/completed/20260113_doc-index-tooling/spec.md`
- **Chunking rationale:** `.project/completed/20260113_markdown-chunker-indexer-DEPRECATED/spec.md`
- **Agent design:** `.project/completed/20260113_specialized-doc-agents/spec.md`
