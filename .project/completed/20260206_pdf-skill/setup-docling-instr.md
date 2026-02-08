# Prompt: Set Up Docling MCP Server for PDF Analysis

You are setting up the Docling MCP server for Claude Code CLI to enable
high-fidelity PDF extraction, particularly for research papers with complex
tables, figures, and numerical data.

## Context

This is part of an `agentic-mbse` toolchain that uses a three-tier PDF
extraction strategy:
1. **pymupdf4llm** — fast first-pass extraction (default)
2. **Docling MCP** — targeted single-page conversion for garbled tables
3. **pymupdf → PNG → visual read** — last-resort fallback

## Setup Instructions

Run the setup script at `./setup-docling-mcp.sh`. This script:

1. **Detects the system environment** (RAM, GPU, CPU cores)
2. **Classifies into a tier** (constrained/moderate/comfortable)
3. **Creates a wrapper script** at `~/.local/bin/docling-mcp-wrapper.sh` that:
   - Changes CWD to `/tmp` before launch (critical: avoids pydantic_settings
     picking up project `.env` files, which causes `ValidationError:
     extra_forbidden` on unrelated env vars like `SYSIDE_LICENSE_KEY`)
   - Sets thread limits (`OMP_NUM_THREADS`, `MKL_NUM_THREADS`, etc.)
     proportional to available resources
   - Sets `CUDA_VISIBLE_DEVICES=""` to prevent PyTorch GPU probe overhead
     on CPU-only machines
   - Sets `TOKENIZERS_PARALLELISM=false` to avoid fork warnings
4. **Tests the server** can start without errors
5. **Registers with Claude Code** via `claude mcp add --scope user`
6. **Generates an environment report** at `~/.docling-mcp-env.md`

## Known Issues & Fixes (from real debugging)

### Issue 1: pydantic_settings reads `.env` from CWD
Docling MCP uses `pydantic_settings` with `env_file=".env"`. If you run the
MCP server from a project directory that has a `.env` file containing variables
not in Docling's Settings model (which uses `extra="forbid"`), you get:

```
ValidationError: 1 validation error for Settings
some_key
  Extra inputs are not permitted [type=extra_forbidden]
```

**Fix**: The wrapper script does `cd /tmp` before launching the server.

### Issue 2: OOM on 8GB machines
Docling loads RT-DETR (layout model) + TableFormer (table structure model)
into RAM. On CPU-only 8GB machines, this competes with the OS and Claude Code.

Additionally, `DoclingParseV2DocumentBackend` has a known memory leak that
accumulates ~4GB per conversion without releasing. EasyOCR (if triggered) also
leaks memory in containerized environments.

**Fix**: 
- Never send full multi-page PDFs to Docling on constrained systems
- Always extract individual pages as separate single-page PDFs using pymupdf first
- Thread limits reduce parallel memory pressure
- OCR is not explicitly disabled (no MCP-level toggle), but Docling auto-skips
  OCR for digital-native PDFs with extractable text

### Issue 3: First run downloads ~500MB of models
The layout detection and table structure models are downloaded to
`~/.cache/docling/` on first use. This is a one-time cost but will spike
memory during download+load.

## Post-Setup Verification

After running the script:

```bash
claude
# Inside Claude Code:
/mcp
# Should show: docling · ✔ connected
```

Test with a real PDF:
```
Convert the PDF document at /path/to/test.pdf into DoclingDocument and return its document-key
```

## Integration with pdf-analysis Skill

The pdf-analysis skill should reference the environment report at
`~/.docling-mcp-env.md` to determine:
- Which tier the system is classified as
- Maximum recommended pages per Docling call
- Whether to prefer PNG fallback over Docling for memory safety

The skill's CLAUDE.md should include:

```markdown
## Docling MCP Usage Constraints

Read ~/.docling-mcp-env.md to determine system tier and limits.

### Single-Page Extraction (REQUIRED before Docling on constrained/moderate tiers)
```python
import pymupdf
doc = pymupdf.open("paper.pdf")
single = pymupdf.open()
single.insert_pdf(doc, from_page=N, to_page=N)
single.save("/tmp/page_N.pdf")
single.close()
doc.close()
```

### PNG Fallback (when Docling fails or is too slow)
```python
import pymupdf
doc = pymupdf.open("paper.pdf")
page = doc[N]
pix = page.get_pixmap(matrix=pymupdf.Matrix(200/72, 200/72))  # 200 DPI
pix.save("/tmp/page_N.png")
doc.close()
```
Then visually inspect the PNG and manually reconstruct the markdown.
```