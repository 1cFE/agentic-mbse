---
date: 2026-02-06T18:00:00-06:00
researcher: Claude
topic: "GPU-Accelerated PDF Extraction on Voltage Park"
tags: [research, pdf-extraction, gpu, voltage-park, docling, mineru, marker]
status: complete
last_updated: 2026-02-06
---

# Research: GPU-Accelerated PDF Extraction on Voltage Park

**Date**: 2026-02-06 18:00 CST
**Researcher**: Claude
**Research Type**: Integration / Feasibility / Platform

## Research Question

How good would a GPU-enabled "brute force" method perform for PDF extraction compared to our existing baselines? How do we deploy and test this on Voltage Park (H100 GPUs), and how does it fit into the larger knowledge database ingestion strategy?

## Summary

- **Three GPU-accelerated tools are viable candidates**: Docling (GPU-accelerated TableFormer, 6x speedup), MinerU 2.5 (1.2B VLM, 2-4 pages/sec on H100, state-of-the-art on OmniDocBench), and Marker (25 pages/sec on H100, best speed). All have Docker images and H100 support.
- **Voltage Park provides 1x H100 VMs at $1.99/hr** with SSH access to Ubuntu + pre-installed CUDA. Data transfer via scp/rsync. No ingress/egress fees. A full evaluation across all 7 test documents with all 3 tools can be completed in **~2-3 hours of GPU time (~$4-6)**.
- **MinerU 2.5 is the most promising "brute force" candidate**: its VLM backend scores 90.67 on OmniDocBench and 88.22 TEDS on tables — the highest published scores for any open-source tool. It handles tables, equations, and layout in a single unified model.
- **The GPU extraction approach fits naturally into the knowledge database pipeline**: Voltage Park could serve as an "extraction station" — batch-process PDFs pulled from Zotero, produce high-quality markdown, push results back via scp, then commit to git. The cost for processing the initial 5-10 document corpus would be ~$2-4.
- **Key risk**: Voltage Park bills for stopped instances. You must terminate to stop charges, which destroys local data. The workflow must be "upload → process → download → terminate" in a single session.

## Detailed Findings

### Current Baselines (What We're Comparing Against)

| Method | Overall Quality | Tables | Structure | Equations | Cost | Speed |
|--------|----------------|--------|-----------|-----------|------|-------|
| **Auto pipeline** (pymupdf4llm, CPU) | 2.68/5 | 2.00/5 | 2.64/5 | ~1.5/5 | $0 | ~10s/65pp |
| **Manual agent** (Sonnet vision, per-page) | 3.71/5 | 3.71/5 | 3.86/5 | 5.0/5 | $0.31/page | ~3 min/page |
| **v2 concept target** (L1+L2, CPU) | 3.5/5 | 3.5/5 | 3.5/5 | ~2.0/5 | $0 | ~2 min/65pp |
| **v2 concept target** (--enhance) | 4.0/5 | 4.0/5 | 4.0/5 | 4.0/5 | $0.45-1.20/doc | ~10 min/65pp |

The question for this research: **can a GPU pipeline match or beat the v2 --enhance target (4.0/5) without requiring claude -p calls, and at what cost/speed?**

### Tool 1: Docling with GPU Acceleration

**What it does differently on GPU**: Docling's layout analysis model (DocLayNet-trained) and TableFormer both run on CUDA. GPU provides ~6x speedup over CPU and enables larger batch sizes.

| Parameter | CPU | H100 GPU |
|-----------|-----|----------|
| Processing speed | ~4s/page | ~0.7s/page (estimated from 6x) |
| `layout_batch_size` | 4 | 64 |
| `table_batch_size` | 2 | 4 (GPU batching limited — known issue) |
| `ocr_batch_size` | 4 | 64 |
| TableFormer accuracy | 93.6-97.9% | Same (model is identical) |
| VRAM required | N/A | ~4-8 GB |

**Key insight**: Docling's GPU acceleration improves *speed* dramatically but not *accuracy* — the same models run, just faster. The quality improvement from Docling comes from using it at all (vs pymupdf4llm), not from GPU vs CPU. However, GPU makes Docling practical for full-document extraction (the reason it times out on our current CPU setup).

**Why Docling failed on 2237/2238**: Likely a memory or timeout issue on CPU. With 80GB H100 VRAM + 1TB system RAM on Voltage Park, these constraints disappear entirely.

**Setup on H100**:
```python
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions, AcceleratorOptions, AcceleratorDevice
)

accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CUDA)
pipeline_options = PdfPipelineOptions(
    accelerator=accelerator_options,
    do_table_structure=True,
    table_structure_options=TableStructureOptions(
        mode=TableFormerMode.ACCURATE
    )
)
pipeline_options.ocr_options.ocr_batch_size = 64
pipeline_options.layout_options.layout_batch_size = 64
```

**Docker image**: `ghcr.io/docling-project/docling-serve-cu128`
**Install**: `pip install docling` + CUDA PyTorch

### Tool 2: MinerU 2.5 (VLM Backend) — Most Promising

**Architecture**: A 1.2B-parameter vision-language model purpose-built for document parsing. Two-stage: (1) low-res layout analysis → (2) high-res per-region recognition. Handles tables, equations, OCR, and reading order in a single unified model.

| Metric | Value | Source |
|--------|-------|--------|
| OmniDocBench overall | **90.67** (SOTA) | MinerU paper, CVPR 2025 benchmark |
| TEDS (table structure) | **88.22** (SOTA) | OmniDocBench |
| TEDS-S (table structure simplified) | **92.38** (SOTA) | OmniDocBench |
| Formula recognition | High (UniMERNet-class) | Integrated in VLM |
| H200 throughput | 4.47 pages/sec | Official benchmark |
| A100 throughput | 2.12 pages/sec | Official benchmark |
| **H100 estimated** | **~3 pages/sec** | Interpolated |
| VRAM needed | ~25 GB peak | Community reports |
| Model size | 1.2B params | Paper |

**Why MinerU 2.5 is the strongest candidate**:

1. **Tables**: 88.22 TEDS is the highest published score on OmniDocBench, outperforming GPT-4o, Gemini 2.5 Pro, and all other open-source tools. Specifically improved for "borderless/semi-structured tables" — exactly our failure mode.
2. **Equations**: Integrated UniMERNet-class formula recognition outputs LaTeX — our pymupdf4llm pipeline garbles equations entirely.
3. **Headers/structure**: Unified layout model handles section hierarchy. Limitation: only H1-level headings reliably detected.
4. **Page artifacts**: Handled automatically by the layout model (headers/footers classified and excluded).
5. **End-to-end**: One command processes the full document. No pipeline assembly required.

**Processing our 7-doc corpus on H100**:

| Document | Pages | Est. Time (3 pp/s) |
|----------|-------|---------------------|
| 2232 (Fusion Markets) | ~30 | 10s |
| 2233 (D-T MCF TEA) | ~30 | 10s |
| 2235 (Global Fusion AI) | ~40 | 13s |
| 2236 (Digital Twins) | ~80 | 27s |
| 2237 (LANL PJMIF) | 65 | 22s |
| 2238 (CBFR) | ~40 | 13s |
| 2241 (ICRH Fokker-Planck) | ~30 | 10s |
| **Total** | **~315** | **~105s (~2 min)** |

**Setup on H100**:
```bash
# Install
pip install uv && uv pip install -U "mineru[all]"

# Process a document
mineru -p document.pdf -o output_dir/

# Pipeline backend (fallback, CPU-capable)
mineru -p document.pdf -o output_dir/ -b pipeline
```

**Docker**:
```bash
wget https://gcore.jsdelivr.net/gh/opendatalab/MinerU@master/docker/global/Dockerfile
docker build -t mineru:latest -f Dockerfile .
docker run --gpus all --shm-size 32g -p 30000:30000 -p 7860:7860 -p 8000:8000 --ipc=host -it mineru:latest /bin/bash
```

### Tool 3: Marker — Best Speed

| Metric | Value |
|--------|-------|
| H100 throughput (batch) | ~25 pages/sec |
| H100 throughput (with OCR) | ~9.3 pages/sec |
| VRAM per worker | ~3.5 GB |
| Parallel workers on H100 (80GB) | ~22 |
| With `--use_llm` | Cross-page table merging, equation refinement, form extraction |
| Table quality (base) | Good, improved significantly with --use_llm |
| Equation quality | Surya/Texify integrated; --use_llm adds LLM refinement |

**Processing our 7-doc corpus on H100**:

~315 pages / 25 pages/sec = **~13 seconds** (without OCR)
~315 pages / 9.3 pages/sec = **~34 seconds** (with OCR)

**Why Marker is interesting but secondary**: Speed is extraordinary but table accuracy is lower than MinerU/Docling. The `--use_llm` mode requires an external LLM API key (Gemini, Claude, etc.) which adds cost and latency — at that point it's similar to our v2 --enhance approach. Best used as a fast first pass with MinerU/Docling for table-heavy pages.

**Setup on H100**:
```bash
pip install marker-pdf[full]
# Ensure CUDA PyTorch installed
export TORCH_DEVICE=cuda

# Single document
marker_single document.pdf --output_dir output/

# Batch directory
marker input_dir/ --workers 22 --output_dir output/

# With LLM enhancement
export GOOGLE_API_KEY=your-key
marker_single document.pdf --use_llm --output_dir output/
```

### Voltage Park Platform Operational Guide

#### Provisioning

1. **Log in**: dashboard.voltagepark.com (account already exists with balance)
2. **Deploy**: Select VM → 1x H100 GPU → $1.99/hr
3. **SSH key**: Attach your SSH public key during deployment
4. **Boot time**: "near-instant" for VMs

#### Connecting

```bash
ssh ubuntu@<Public_IP>
# IP shown in dashboard after deployment
```

The instance comes with:
- Ubuntu (likely 22.04)
- CUDA pre-installed (verify with `nvidia-smi`)
- conda pre-installed
- Jupyter Notebook launchable from dashboard
- 1x H100 80GB SXM5
- Multi-NVMe local storage (root + additional unmounted drives)

#### Getting Data On

```bash
# From your local machine:
scp -r /home/reid/1cfe/literature/2237/LA-UR-25-24580.pdf ubuntu@<IP>:~/pdfs/
scp -r /home/reid/1cfe/literature/22*/  ubuntu@<IP>:~/pdfs/

# Or rsync for the full literature directory:
rsync -avz --include='*/' --include='*.pdf' --exclude='*' \
  /home/reid/1cfe/literature/ ubuntu@<IP>:~/pdfs/
```

#### Getting Data Off

```bash
# From your local machine:
scp -r ubuntu@<IP>:~/results/ /home/reid/1cfe/literature/gpu-extraction/

# Or rsync:
rsync -avz ubuntu@<IP>:~/results/ /home/reid/1cfe/literature/gpu-extraction/
```

#### Storage

- **Local NVMe**: Persists across reboots, destroyed on termination
- **VAST NFS**: Persistent shared storage (attachable). Deploy via dashboard ("Deploy Storage"), mount via NFS. **Not available for VMs** — only bare metal.
- For a short evaluation session, local storage is fine

#### Billing

| Item | Detail |
|------|--------|
| 1x H100 VM | $1.99/hr |
| Billing granularity | Microsecond-level |
| Stopped instance | **Still billed at $1.99/hr** |
| Termination | Stops billing, destroys all data |
| Data transfer fees | **None** (no ingress/egress) |
| Minimum commitment | None |

**Critical operational rule**: When done, **terminate** (not stop) the instance. Stopping still bills. Budget ~3 hours for the full evaluation = **~$6**.

#### Important Notes

- Voltage Park merged with Lightning AI (Jan 2026). Platform still operational under Voltage Park branding.
- No Docker pre-installed by default — install with `sudo apt install docker.io` then `sudo usermod -aG docker $USER` if needed.
- For container workloads with GPU: install nvidia-container-toolkit.

---

## Recommended Evaluation Plan

### Phase 1: Environment Setup [~30 min, $1.00]

**Objective**: Get a working H100 instance with all three tools installed and test PDFs uploaded.

**Steps**:

1. Deploy 1x H100 VM on Voltage Park dashboard
2. SSH in, verify GPU: `nvidia-smi`
3. Upload test corpus:
   ```bash
   # From local machine — upload all 7 test PDFs
   scp /home/reid/1cfe/literature/2232/*.pdf ubuntu@<IP>:~/pdfs/2232.pdf
   scp /home/reid/1cfe/literature/2233/*.pdf ubuntu@<IP>:~/pdfs/2233.pdf
   scp /home/reid/1cfe/literature/2235/*.pdf ubuntu@<IP>:~/pdfs/2235.pdf
   scp /home/reid/1cfe/literature/2236/*.pdf ubuntu@<IP>:~/pdfs/2236.pdf
   scp /home/reid/1cfe/literature/2237/*.pdf ubuntu@<IP>:~/pdfs/2237.pdf
   scp /home/reid/1cfe/literature/2238/*.pdf ubuntu@<IP>:~/pdfs/2238.pdf
   scp /home/reid/1cfe/literature/2241/*.pdf ubuntu@<IP>:~/pdfs/2241.pdf
   ```
4. Install tools:
   ```bash
   # Create a clean environment
   conda deactivate  # VP ships conda; deactivate it
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.local/bin/env

   # MinerU (the primary candidate)
   uv venv ~/mineru-env --python 3.12
   source ~/mineru-env/bin/activate
   uv pip install -U "mineru[all]"

   # Docling (for comparison)
   uv venv ~/docling-env --python 3.12
   source ~/docling-env/bin/activate
   uv pip install docling torch torchvision --index-url https://download.pytorch.org/whl/cu128

   # Marker (for comparison)
   uv venv ~/marker-env --python 3.12
   source ~/marker-env/bin/activate
   uv pip install marker-pdf[full]
   ```
5. Upload the evaluation script (see Phase 2)

**Success criteria**:
- [ ] `nvidia-smi` shows H100 80GB
- [ ] All 7 PDFs are in `~/pdfs/`
- [ ] `mineru --help` runs without error
- [ ] `python -c "import docling; print('ok')"` succeeds
- [ ] `marker_single --help` runs without error
- [ ] Each tool can process a single test page without crashing

### Phase 2: Extraction Benchmark [~1 hr, $2.00]

**Objective**: Process all 7 documents with all 3 GPU tools and produce comparable markdown output.

**Steps**:

1. **MinerU extraction** (all 7 docs):
   ```bash
   source ~/mineru-env/bin/activate
   mkdir -p ~/results/mineru
   for pdf in ~/pdfs/*.pdf; do
     name=$(basename "$pdf" .pdf)
     echo "Processing $name..."
     time mineru -p "$pdf" -o ~/results/mineru/"$name"/
   done
   ```
   Expected time: ~2 minutes total.

2. **Docling extraction** (all 7 docs):
   ```bash
   source ~/docling-env/bin/activate
   mkdir -p ~/results/docling
   # Use a script — Docling needs Python API
   python ~/eval_docling.py ~/pdfs/ ~/results/docling/
   ```
   Script `eval_docling.py`:
   ```python
   import sys, time
   from pathlib import Path
   from docling.document_converter import DocumentConverter, PdfFormatOption
   from docling.datamodel.pipeline_options import (
       PdfPipelineOptions, AcceleratorOptions, AcceleratorDevice,
       TableStructureOptions, TableFormerMode
   )

   input_dir, output_dir = Path(sys.argv[1]), Path(sys.argv[2])
   acc = AcceleratorOptions(device=AcceleratorDevice.CUDA)
   opts = PdfPipelineOptions(accelerator=acc, do_table_structure=True)
   opts.table_structure_options = TableStructureOptions(mode=TableFormerMode.ACCURATE)

   converter = DocumentConverter(format_options={
       "pdf": PdfFormatOption(pipeline_options=opts)
   })

   for pdf in sorted(input_dir.glob("*.pdf")):
       print(f"Processing {pdf.name}...")
       t0 = time.time()
       result = converter.convert(pdf)
       md = result.document.export_to_markdown()
       out = output_dir / pdf.stem
       out.mkdir(parents=True, exist_ok=True)
       (out / "full_document.md").write_text(md)
       print(f"  Done in {time.time()-t0:.1f}s, {len(md)} chars")
   ```
   Expected time: ~5-10 minutes total.

3. **Marker extraction** (all 7 docs):
   ```bash
   source ~/marker-env/bin/activate
   mkdir -p ~/results/marker
   marker ~/pdfs/ --workers 10 --output_dir ~/results/marker/
   ```
   Expected time: ~15 seconds total.

4. **Record timing and metadata**:
   ```bash
   # Capture GPU utilization during processing
   nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total \
     --format=csv -l 5 > ~/results/gpu_log.csv &
   ```

**Success criteria**:
- [ ] All 7 documents processed by all 3 tools without crashes
- [ ] Each tool's output directory contains markdown for each document
- [ ] Processing times recorded for each tool × document combination
- [ ] GPU utilization logged

### Phase 3: Quality Comparison [~30 min, $1.00]

**Objective**: Compare GPU-extracted output against our existing baselines on the same 7 pages from document 2237 that the manual agent tested.

**Steps**:

1. **Extract the 7 comparison pages** from each tool's output for document 2237:
   - Pages 14, 16, 18, 25, 40, 41, 45 (0-indexed)
   - Slice the relevant sections from each tool's full_document.md

2. **Score each extraction** on the same 4 dimensions used in the comparison report:
   - Table Fidelity (1-5)
   - Structure (1-5)
   - Equation quality (1-5)
   - Completeness (1-5)

3. **Build a comparison matrix**:

   | Page | Auto (pymupdf) | Manual (Sonnet) | Docling GPU | MinerU GPU | Marker GPU |
   |------|---------------|-----------------|-------------|------------|------------|
   | 14 (Table 2) | 2.33 | 4.33 | ? | ? | ? |
   | 16 (Table 3) | 2.25 | 3.00 | ? | ? | ? |
   | 18 (Table 4) | 2.67 | 2.67 | ? | ? | ? |
   | 25 (Table 6) | 2.33 | 4.33 | ? | ? | ? |
   | 40 (Table 9) | 2.00 | 4.33 | ? | ? | ? |
   | 41 (LCOE eq.) | 2.00 | 4.33 | ? | ? | ? |
   | 45 (Table 10) | 2.33 | 4.00 | ? | ? | ? |

4. **Spot-check other documents** for overall quality — look at 2-3 pages each from at least 3 other documents.

5. **Download all results** before terminating:
   ```bash
   # From local machine:
   rsync -avz ubuntu@<IP>:~/results/ /home/reid/1cfe/literature/gpu-extraction/
   ```

**Success criteria**:
- [ ] Comparison matrix filled in for all 7 pages × 3 GPU tools
- [ ] At least one GPU tool achieves mean score >= 3.5/5 on the 7 comparison pages
- [ ] Specific strengths/weaknesses identified per tool (e.g., "MinerU best on tables, Marker best on equations")
- [ ] All results downloaded to local machine
- [ ] Instance **terminated** (not stopped)

### Phase 4: Analysis and Decision [Local, no GPU cost]

**Objective**: Determine which GPU approach (if any) to integrate into the pipeline and how.

**Steps**:

1. Write a comparison report (same format as the existing evaluation-report.md)
2. Answer the key questions:
   - Does any GPU tool beat the v2 --enhance target (4.0/5) without VLM API calls?
   - What's the cost/quality tradeoff vs our other approaches?
   - Is the quality gain worth the operational complexity of GPU provisioning?
3. Decide on integration path (see Architecture Insights below)

**Success criteria**:
- [ ] Comparison report written with quantitative scores
- [ ] Clear verdict: "GPU extraction is/isn't worth integrating because..."
- [ ] If worth it: specific integration plan with estimated effort
- [ ] If not: documented reasons and alternative recommendations

---

## Integration with Knowledge Database Strategy

The knowledge database epic (KNOW-DB in fusion-tea) describes a pipeline:

```
Zotero → pyzotero download → agentic-mbse extract → SOURCE_INDEX.md → git
```

GPU-accelerated extraction fits into this pipeline in two possible architectures:

### Architecture A: "Extraction Station" (Batch Processing)

```
Zotero → pyzotero download → [GPU instance] → scp results back → git

1. Pull new PDFs from Zotero locally
2. scp PDFs to Voltage Park H100 instance
3. Run MinerU/Docling/Marker on all PDFs (batch mode)
4. scp results back to local machine
5. Run agentic-mbse post-processing (index generation, SOURCE_INDEX registration)
6. Terminate GPU instance
7. git commit
```

**When to use**: When you have a batch of 5-10+ new documents to process. The fixed overhead of provisioning an instance (~5 min) amortizes well over many documents.

**Cost model**:

| Corpus Size | GPU Time | VP Cost | Cost/Doc |
|-------------|----------|---------|----------|
| 5 documents (~200 pages) | ~15 min (incl. setup) | $0.50 | $0.10 |
| 10 documents (~500 pages) | ~25 min (incl. setup) | $0.83 | $0.08 |
| 50 documents (~2500 pages) | ~60 min (incl. setup) | $2.00 | $0.04 |

Compare to v2 --enhance (Layer 3 claude -p): $0.45-1.20/document. **GPU extraction is 5-15x cheaper per document at batch scale**.

### Architecture B: "Local-First with GPU Fallback"

```
Zotero → download → agentic-mbse extract (local, CPU, Layers 1+2) → check quality
  ├── Quality OK → git commit
  └── Quality insufficient → queue for GPU re-extraction
                             → batch GPU session when queue hits N documents
```

**When to use**: When most documents extract acceptably on CPU and only a few need GPU treatment. Avoids provisioning overhead for single documents.

### Architecture C: "API Service" (Future)

If GPU extraction proves consistently superior, a persistent MinerU or Docling API service on a reserved GPU instance could serve multiple projects:

```
Zotero → download → POST pdf to extraction API → get markdown → git
```

This only makes sense at scale (>100 documents/month) where the fixed cost of a reserved instance ($1.99/hr × 24 × 30 = ~$1,435/mo) is justified. Not relevant now, but worth noting for the future.

### Recommendation for KNOW-DB Epic

**Start with Architecture A** for the initial corpus ingestion (Item 4 in the epic). The workflow would be:

1. Complete KNOW-DB Items 1-3 (Zotero setup, single-source E2E, automation script) using the existing CPU pipeline
2. For Item 4 (First Corpus Ingestion, 5-10 documents):
   - Download all PDFs from Zotero locally
   - Provision a VP H100 for ~30 minutes
   - Batch-extract all documents with the best GPU tool (likely MinerU)
   - Download results, run local post-processing (index generation, SOURCE_INDEX registration)
   - Terminate instance
   - Total GPU cost: ~$1

This approach separates the extraction quality question from the Zotero integration question. The automation script (Item 3) doesn't care *how* the markdown was produced — it just needs the output directory structure.

---

## Architecture Insights

### The Three-Path Decision Tree

After the GPU evaluation, we'll have data to choose between three extraction paths:

| Path | Quality Target | Cost | Speed | Operational Complexity |
|------|---------------|------|-------|----------------------|
| **v2 L1+L2** (CPU, postprocessing + GMFT) | 3.5/5 | Free | Fast (minutes) | None (local) |
| **v2 --enhance** (CPU + claude -p) | 4.0/5 | $0.45-1.20/doc | Slow (minutes/doc) | Needs claude CLI |
| **GPU extraction** (MinerU/Docling/Marker) | **TBD** (predicted 3.5-4.5/5) | $0.04-0.10/doc | Fast (seconds/doc) | Needs VP provisioning |

If GPU extraction reaches 4.0+/5, it **replaces** `--enhance` as the quality layer — cheaper, faster, and no VLM API dependency. The v2 concept's Layer 3 (claude -p) would become a last-resort for the ~5% of pages that even GPU tools can't handle.

If GPU extraction reaches 3.5/5 (comparable to v2 L1+L2), it validates that dedicated ML models match our post-processing approach but doesn't justify the operational overhead.

### How GPU Tools Map to the v2 Concept Layers

| v2 Layer | GPU Equivalent | Notes |
|----------|---------------|-------|
| Layer 1: pymupdf4llm + postprocessing | MinerU/Marker full pipeline | GPU tools do layout, tables, equations, headers all at once |
| Layer 2: GMFT table extraction | Docling TableFormer (already GPU-accelerated) | Docling's TableFormer is the same model GMFT wraps, just integrated |
| Layer 3: claude -p AI repair | VLM fallback (Marker --use_llm) | Same idea: use a vision model for what deterministic extraction can't handle |

The key insight: **GPU tools collapse Layers 1+2 into a single pass**. MinerU's VLM handles text, tables, equations, and layout simultaneously. This is architecturally simpler than our multi-layer pipeline.

---

## Feasibility Assessment

### Technical Feasibility: HIGH

- All three tools have H100 support and published benchmarks
- Docker images exist for all three
- Voltage Park provides pre-installed CUDA environment
- The evaluation can be completed in a single 2-3 hour session
- Data transfer via scp is simple and reliable

### Operational Feasibility: MEDIUM

- Requires manual provisioning and SSH session management
- Must remember to terminate (not stop) instance to avoid billing
- No persistent state between sessions — must upload/download each time
- Could be automated with a script using Voltage Park API (but not worth it for occasional batch jobs)

### Cost Feasibility: HIGH

- Evaluation: ~$6 for 3 hours of H100
- Ongoing batch extraction: $0.04-0.10 per document
- Much cheaper than claude -p at $0.45-1.20 per document
- No ingress/egress fees

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Tool installation fails on VP instance | Low | Medium | Test with one tool first; Docker as fallback |
| MinerU quality disappoints on fusion papers | Medium | Medium | We have 2 other tools to test; data-driven decision |
| GPU doesn't improve over CPU Docling quality | Medium | Low | Speed improvement alone is valuable for batch processing |
| Forget to terminate instance | Medium | High ($48/day!) | Set a phone timer; script termination into workflow |
| VP has no available H100 VMs | Low | Low | Try at off-peak time; platform has 40K GPUs |
| Output format incompatible with our pipeline | Low | Medium | All tools output markdown; post-processing can normalize |

---

## Recommendations

### Immediate Next Step

**Run the 4-phase evaluation plan above.** Total investment: ~$6 and ~3 hours of hands-on time. This produces hard data to compare against our existing baselines.

### Preparation Before Provisioning

1. **Gather all 7 test PDFs** into a single directory for easy upload
2. **Write the evaluation scripts locally** (Docling Python script, scoring rubric, comparison template)
3. **Prepare the upload/download commands** with actual file paths
4. **Set a timer** for 3 hours from instance creation to remind yourself to terminate

### If GPU Extraction Wins (4.0+/5)

1. Add GPU extraction as an option in the `agentic-mbse extract` CLI: `--backend mineru` / `--backend docling-gpu` / `--backend marker`
2. These would require the user to have the tool installed (likely in a separate venv with CUDA)
3. For the knowledge database pipeline (KNOW-DB), add a "GPU extraction station" workflow to the automation script
4. Consider whether the v2 Layer 3 (claude -p) is still needed or if GPU extraction subsumes it

### If GPU Extraction Is Comparable (3.5/5)

1. Continue with v2 concept as planned (Layers 1+2+3 on CPU)
2. Note GPU tools as a future option when operational simplicity improves (e.g., if Voltage Park adds cloud-init or if Docling GPU becomes easy to run locally)
3. Still useful for batch processing speed — consider for large corpus ingestion even if quality is similar

---

## Open Questions

1. **MinerU output format**: Does MinerU 2.5 output standard markdown with `##` headers, `|` pipe tables, and `$LaTeX$` equations? Or does it use HTML/custom format? This determines how much post-processing we'd need.

2. **Marker license**: Marker is GPL-3.0. If we integrate it into agentic-mbse (MIT license), we'd need to handle it as an optional external tool, not a bundled dependency. MinerU is AGPL-3.0 — same concern.

3. **Multi-page table stitching**: Does MinerU 2.5 handle tables that span page breaks? The existing research notes this as "MinerU claims improved long/complex tables" but doesn't confirm cross-page stitching specifically.

4. **Voltage Park API automation**: The VP API (`cloud-api.voltagepark.com`) could potentially automate the provision→upload→process→download→terminate workflow. Worth investigating if GPU extraction becomes a regular workflow.

5. **Local GPU option**: If Reid has or gets an RTX 4090 (24GB), MinerU would run at ~1.7 pages/sec locally — slower than H100 but eliminates the provisioning overhead entirely. Worth considering for the long term.

---

## Source References

### Voltage Park Platform
- [Voltage Park Pricing](https://www.voltagepark.com/pricing) — $1.99/hr per H100
- [Voltage Park Infrastructure](https://www.voltagepark.com/infrastructure) — Dell PowerEdge XE9680 specs
- [GPT-OSS Deployment Example](https://support.voltagepark.com/article/example-deploying-gpt-oss-on-voltage-park) — Practical SSH + install workflow
- [VAST NFS Mount Options](https://support.voltagepark.com/support/troubleshooting/options-for-mounting-vast-nfs-shares) — Storage options
- [Lightning AI / Voltage Park Merger](https://lightning.ai/blog/lightning-ai-voltage-park-merger-ai-cloud) — Jan 2026 merger context

### Docling GPU
- [Docling RTX GPU Acceleration](https://docling-project.github.io/docling/getting_started/rtx/) — Setup guide, 6x speedup claim
- [Docling GPU Support](https://docling-project.github.io/docling/usage/gpu/) — CUDA configuration
- [Docling GPU Hardware Acceleration (DeepWiki)](https://deepwiki.com/docling-project/docling/9.3-gpu-and-hardware-acceleration) — Batch size recommendations
- [Docling Technical Report](https://arxiv.org/html/2408.09869v5) — TableFormer accuracy

### MinerU
- [MinerU GitHub](https://github.com/opendatalab/MinerU) — 48.8K stars, AGPL-3.0
- [MinerU 2.5 Paper](https://arxiv.org/html/2509.22186v2) — Architecture, benchmarks
- [MinerU Docker Deployment](https://opendatalab.github.io/MinerU/quick_start/docker_deployment/) — Official Dockerfile
- [MinerU Performance Discussion #1226](https://github.com/opendatalab/MinerU/discussions/1226) — Community benchmarks
- [OmniDocBench (CVPR 2025)](https://github.com/opendatalab/OmniDocBench) — Benchmark methodology

### Marker
- [Marker GitHub](https://github.com/datalab-to/marker) — 31.3K stars, GPL-3.0
- [Marker Docker (oss_container)](https://github.com/datalab-to/oss_container) — H100 benchmarks
- [Marker --use_llm Documentation](https://deepwiki.com/datalab-to/marker/3.1-command-line-interface) — LLM integration options
- [Procycons PDF Benchmark 2025](https://procycons.com/en/blogs/pdf-data-extraction-benchmark/) — Docling vs Marker vs Unstructured

### Existing Project Context
- `.project/active/document-extraction/evaluation-report.md` — Current baseline: 2.68/5
- `/home/reid/1cfe/literature/2237/comparison/REPORT.md` — Manual agent baseline: 3.71/5
- `.project/research/20260206_scientific-pdf-extraction.md` — 64-source tool landscape
- `.project/concepts/pdf-extraction-v2.md` — v2 three-layer pipeline concept
- `/home/reid/1cfe/fusion-tea/.project/backlog/epic-knowledge-database-integration.md` — KNOW-DB pipeline
