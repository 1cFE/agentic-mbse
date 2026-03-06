---
date: 2026-02-23T16:00:00-06:00
researcher: Claude
topic: "Exhaustive survey of table detection and extraction tools for borderless/space-aligned tables"
tags: [research, doc-extraction, tables, table-detection, borderless, survey]
status: complete
last_updated: 2026-02-23
---

# Survey: Table Detection & Extraction Tools for Borderless/Space-Aligned Tables

**Date**: 2026-02-23
**Researcher**: Claude
**Research Type**: Tool Survey / Landscape Analysis

## Problem Statement

GMFT (AutoTableDetector, using Microsoft Table Transformer) detects only **15/28 tables** in the aries_cost_account government cost report. PyMuPDF `find_tables()` detects **0 real tables** on the same document (its 26 "detections" are prose paragraphs). The missing 13 tables are **space-aligned tables with NO grid lines, NO borders** -- aligned only by whitespace and column spacing.

This survey catalogs every viable tool/approach for detecting and extracting such tables, with specific assessment of borderless table handling.

---

## 1. Deep Learning Table Detection Models

### 1.1 Microsoft Table Transformer (TATR)

- **What it is**: DETR-based object detection model fine-tuned on PubTables-1M for table detection and structure recognition
- **HuggingFace**: `microsoft/table-transformer-detection`, `microsoft/table-transformer-structure-recognition-v1.1-all`
- **Package**: `pip install table-transformer` (or use via `transformers` library directly)
- **License**: MIT
- **Actively maintained**: Yes (last updated May 2025)
- **Borderless table handling**: Trained on PubTables-1M which includes borderless academic tables. The model detects tables as object regions regardless of border presence. However, PubTables-1M is predominantly scientific/academic papers -- government report tables are out-of-distribution.
- **Confidence threshold tuning**: The `post_process_object_detection(outputs, threshold=0.9, target_sizes=target_sizes)` method allows adjusting the detection confidence threshold. Default is often 0.5-0.9; lowering it increases recall at the cost of precision.
- **Benchmarks**: AP 42.0 on COCO 2017 val. On ICDAR-2013: 75% exact match when trained on PubTables-1M, 65% on FinTabNet, 81% combined.
- **Fine-tuning**: HuggingFace provides official object detection training scripts for fine-tuning on custom datasets. Fine-tuning on a small set of government report pages (even 50-100 annotated tables) could dramatically improve detection for this domain.
- **This is what GMFT wraps.** GMFT's `AutoTableDetector` is a thin wrapper around this model. Tuning GMFT means tuning this model's threshold or swapping the underlying model.
- **Strengths**: Fast inference, good on academic/scientific tables, well-documented, easy to fine-tune
- **Weaknesses**: PubTables-1M training bias toward bordered/gridded tables; government report tables are out-of-distribution; no explicit borderless table category in training data

**Source**: [microsoft/table-transformer-detection on HuggingFace](https://huggingface.co/microsoft/table-transformer-detection), [GitHub](https://github.com/microsoft/table-transformer)

### 1.2 CascadeTabNet

- **What it is**: Cascade Mask R-CNN with HRNet backbone for end-to-end table detection AND structure recognition. Explicitly classifies tables as "bordered" or "borderless."
- **Package**: No pip package; clone from GitHub: `github.com/DevashishPrasad/CascadeTabNet`
- **License**: MIT
- **Actively maintained**: No -- last significant commit was 2020 (CVPR 2020 Workshop). Issues are open and unanswered since 2022.
- **Borderless table handling**: **Explicit borderless category.** The model predicts segmentation masks for both bordered and borderless tables, with different processing strategies for each. For borderless tables, it predicts individual cells then arranges them into rows/columns by position.
- **Benchmarks**: Strong on ICDAR-2013, ICDAR-2019, and TableBank at time of publication (2020). However, superseded by later models on most benchmarks. Cross-domain performance is poor -- "its performance decreased severely when tested on different domains" (from TDeLTA paper).
- **Strengths**: Explicit bordered/borderless distinction; instance segmentation approach
- **Weaknesses**: Stale codebase (2020, depends on old mmdetection/PyTorch); no pip package; requires significant setup effort; likely inferior to newer models

**Source**: [GitHub](https://github.com/DevashishPrasad/CascadeTabNet), [Paper](https://arxiv.org/pdf/2004.12629)

### 1.3 LayoutLMv3

- **What it is**: Multimodal transformer that jointly processes visual features (patch embeddings) and text features (OCR tokens, 2D spatial embeddings). Pre-trained on document understanding tasks including layout analysis.
- **Package**: `pip install transformers` (use via HuggingFace)
- **License**: CC-BY-NC-SA-4.0 (non-commercial)
- **Actively maintained**: Microsoft continues to maintain via HuggingFace Transformers
- **Borderless table handling**: As a general document understanding model, it learns table regions from visual + text cues. Can potentially detect tables by text alignment patterns even without borders. However, it requires fine-tuning for table detection specifically -- not a plug-and-play detector.
- **Benchmarks**: State-of-the-art on DocILE, FUNSD, CORD, and other document understanding benchmarks
- **Strengths**: Multimodal (uses both visual and text features), strong on diverse document types
- **Weaknesses**: Non-commercial license (CC-BY-NC-SA-4.0); requires fine-tuning for table detection; heavier model than TATR; complex setup

**Source**: [LayoutLMv3 topic](https://www.emergentmind.com/topics/layoutlmv3)

### 1.4 DiT (Document Image Transformer)

- **What it is**: Self-supervised pre-trained vision transformer for document images. Used as backbone for document layout analysis, table detection, text detection.
- **Package**: Available via HuggingFace Transformers
- **License**: CC-BY-NC-SA-4.0 (non-commercial)
- **Actively maintained**: Yes (Microsoft Research)
- **Borderless table handling**: As a general-purpose document vision backbone, it learns document structure from large-scale pre-training. Table detection requires fine-tuning on a downstream task.
- **Benchmarks**: Strong results on PubLayNet, ICDAR-2019 for document layout analysis
- **Strengths**: Strong vision backbone; can be combined with LayoutLMv3 for multimodal processing
- **Weaknesses**: Non-commercial license; requires fine-tuning; not a standalone table detector

**Source**: [Microsoft Research](https://www.microsoft.com/en-us/research/lab/microsoft-research-asia/articles/dit-self-supervised-pre-training-for-document-image-transformers/)

### 1.5 DocLayout-YOLO

- **What it is**: YOLO-v10 based model specifically designed for document layout analysis. Trained on DocSynth-300K (diverse synthetic documents) with a Global-to-Local Controllability module.
- **Package**: `pip install doclayout-yolo`
- **License**: Apache-2.0
- **Actively maintained**: Yes (OpenDataLab, October 2024 release)
- **Borderless table handling**: Trained on DocSynth-300K which includes diverse table types. As a layout detection model, it identifies table regions among other document elements (text, figures, titles, etc.). The synthetic training data likely includes borderless tables.
- **Benchmarks**: Integrated into PDF-Extract-Kit 1.0 as the default layout detector. DocLayout-YOLO is described as "more accurate and faster" than alternatives.
- **Strengths**: Fast (YOLO-based); diverse training data; Apache-2.0 license; integrated into MinerU/PDF-Extract-Kit ecosystem
- **Weaknesses**: Primarily a layout detector (detects "table" regions among other elements), not specialized for table structure; limited to bounding box detection (no structure recognition)

**Source**: [GitHub](https://github.com/opendatalab/DocLayout-YOLO), [PyPI](https://pypi.org/project/doclayout-yolo/)

### 1.6 YOLOv8 Table Detection

- **What it is**: YOLOv8 fine-tuned specifically for table detection in documents, with explicit bordered/borderless classification
- **Package**: `pip install ultralytics` + fine-tuned weights from HuggingFace
- **Models**: `foduucom/table-detection-and-extraction` on HuggingFace
- **License**: AGPL-3.0 (Ultralytics)
- **Actively maintained**: Yes (Ultralytics maintains YOLOv8; community fine-tunes for tables)
- **Borderless table handling**: **Explicit bordered/borderless distinction.** The YOLOv8s model is "fine-tuned on a vast dataset and achieved high accuracy in detecting tables and distinguishing between bordered and borderless ones."
- **Benchmarks**: High accuracy reported on custom datasets; no standard ICDAR numbers published for the fine-tuned variants
- **Strengths**: Very fast inference; explicit borderless detection; well-maintained YOLO ecosystem; easy to fine-tune with Ultralytics CLI
- **Weaknesses**: AGPL-3.0 license for Ultralytics framework; community fine-tuned models may not generalize to government reports; multiple competing fine-tuned checkpoints with varying quality

**Source**: [foduucom on HuggingFace](https://huggingface.co/foduucom/table-detection-and-extraction), [Medium article](https://iamrajatroy.medium.com/document-intelligence-series-part-1-table-detection-with-yolo-1fa0a198fd7)

### 1.7 Surya

- **What it is**: OCR, layout analysis, reading order, and table recognition toolkit supporting 90+ languages. Uses a custom architecture that "outperforms table transformer."
- **Package**: `pip install surya-ocr`
- **Related**: `tabled` library (`pip install tabled-pdf`) for table extraction to markdown/csv using Surya
- **License**: GPL-3.0 (Surya), GPL-3.0 (tabled)
- **Actively maintained**: Yes (VikParuchuri, very active development through 2024-2025)
- **Borderless table handling**: Surya's table recognition detects rows, columns, and cells. The architecture is designed for "complex layouts and rotated tables." However, specific borderless table handling is not documented.
- **Benchmarks**: Claims to "outperform table transformer" but specific benchmark numbers for detection (vs structure recognition) are not published in the README. The benchmarking system uses `penalized_iou_score()` for evaluation.
- **Strengths**: Active development; integrated OCR + layout + table pipeline; multi-language; custom architecture
- **Weaknesses**: GPL-3.0 license; no published detection benchmarks on standard datasets; documentation sparse on borderless handling; GPU recommended

**Source**: [GitHub](https://github.com/VikParuchuri/surya), [tabled](https://github.com/VikParuchuri/tabled)

### 1.8 PaddleOCR / PP-Structure / PP-TableMagic

- **What it is**: Comprehensive document analysis toolkit from PaddlePaddle with dedicated table detection, structure recognition, and cell detection modules. Includes separate models for "wired" (bordered) and "wireless" (borderless) tables.
- **Package**: `pip install paddlepaddle paddleocr` (or `pip install paddlex` for the full pipeline)
- **License**: Apache-2.0
- **Actively maintained**: Yes (very active, PaddlePaddle community, 2025 updates)
- **Borderless table handling**: **Explicitly supports wireless/borderless tables with dedicated models.** PP-TableMagic (General Table Recognition v2) includes table classification to distinguish wired/wireless, then routes to the appropriate structure recognition model. This is the most architecturally complete approach to borderless tables among all tools surveyed.
- **Benchmarks**: RapidTable (which uses PP-Structure models) achieves the **highest scores in OmniDocBench** table recognition (mAP ~82.5). PaddleOCR "performs well with accurate table predictions" on frameless tables specifically, per OmniDocBench evaluation.
- **Strengths**: Explicit wired/wireless table pipeline; top benchmark scores; Apache-2.0 license; comprehensive ecosystem; good English support
- **Weaknesses**: PaddlePaddle framework dependency (not PyTorch); somewhat complex setup; documentation primarily in Chinese with English translations of varying quality; GPU strongly recommended

**Source**: [PP-TableMagic docs](https://paddlepaddle.github.io/PaddleX/3.3/en/pipeline_usage/tutorials/ocr_pipelines/table_recognition_v2.html), [PP-Structure table](https://github.com/PaddlePaddle/PaddleOCR/blob/main/ppstructure/table/README.md)

### 1.9 DocTR

- **What it is**: Document Text Recognition library from Mindee. Primarily OCR (text detection + recognition), NOT table detection.
- **Package**: `pip install python-doctr[torch,viz]`
- **License**: Apache-2.0
- **Actively maintained**: Yes (v1.0.1, joined PyTorch ecosystem)
- **Borderless table handling**: **Not applicable.** DocTR is an OCR engine, not a table detector. It detects text regions (words, lines) but does not identify table structures.
- **Relevance**: Could be used as an OCR component within a larger pipeline (e.g., OCR text positions could feed into table detection heuristics), but is not a table detection tool itself.

**Source**: [GitHub](https://github.com/mindee/doctr), [PyPI](https://pypi.org/project/python-doctr/)

---

## 2. Traditional/Hybrid Tools

### 2.1 Camelot

- **What it is**: Python library for extracting tables from text-based PDFs. Two parsing modes: Lattice (grid lines) and Stream (whitespace-based).
- **Package**: `pip install camelot-py[cv]`
- **License**: MIT
- **Actively maintained**: Partially. Latest PyPI release is 1.0.9. The `atlanhq/camelot` repo has limited recent activity but community forks exist.
- **Borderless table handling**: **Stream mode is specifically designed for borderless tables.** It uses PDFMiner to group characters into words/sentences using margins, then detects table structure by whitespace gaps. Features like `split_text=True` help with merged strings.
- **Strengths**: Mature, well-documented; Stream mode explicitly for borderless tables; returns DataFrames; good for consistent-format documents
- **Weaknesses**: **Text-based PDFs only** (no scanned/OCR documents); requires specifying page numbers; Stream mode needs consistent spacing; struggles with complex layouts; no table region detection (you need to know where tables are or process entire pages); accuracy declines on dense/irregular layouts
- **Key limitation for your use case**: Camelot can EXTRACT borderless tables but struggles to DETECT them reliably on pages with mixed content. You'd need another tool to identify table regions first.

**Source**: [Documentation](https://camelot-py.readthedocs.io/), [GitHub](https://github.com/atlanhq/camelot)

### 2.2 Tabula (tabula-py)

- **What it is**: Python wrapper around tabula-java for PDF table extraction. Like Camelot, has Lattice and Stream modes.
- **Package**: `pip install tabula-py` (requires Java 8+)
- **License**: MIT
- **Actively maintained**: Yes (tabula-py updates through 2024)
- **Borderless table handling**: Stream mode for tables without ruling lines, similar concept to Camelot's Stream. However, "Tabula does better table detection for Stream cases, but it still fails to give good parsing output."
- **Strengths**: Battle-tested; used extensively in journalism/data extraction; Stream mode for borderless; Java-backed (robust PDF parsing)
- **Weaknesses**: Requires Java runtime; detection via `guess=True` can conflict with Stream mode (set `guess=False`); text-based PDFs only; similar limitations to Camelot for complex layouts
- **Note**: The `guess` option auto-detects table regions but is known to make conflicts with stream mode. For reliable borderless extraction, use `stream=True, guess=False` with explicit area specification.

**Source**: [Documentation](https://tabula-py.readthedocs.io/), [PyPI](https://pypi.org/project/tabula-py/)

### 2.3 pdfplumber

- **What it is**: Python library for detailed PDF parsing -- extracts characters, lines, rectangles, and tables with visual debugging.
- **Package**: `pip install pdfplumber`
- **License**: MIT
- **Actively maintained**: Yes (v0.11.8 August 2024, active development)
- **Borderless table handling**: pdfplumber infers table structure from both explicit lines AND text alignment patterns. When grid lines are absent, it "relies on spatial relationships between text elements by analyzing gaps, indentation, and alignment to group words into rows and columns." The `debug_tablefinder()` method is excellent for understanding what it detects.
- **Strengths**: Excellent visual debugging; fine-grained control over detection parameters; works well for financial/tabular documents; active community
- **Weaknesses**: Can over-detect (finds "tables" in regular text); needs parameter tuning per document type; text-based PDFs only; no ML-based detection

**Source**: [GitHub](https://github.com/jsvine/pdfplumber), [PyPI](https://pypi.org/project/pdfplumber/)

### 2.4 img2table

- **What it is**: OpenCV-based table detection and extraction for PDFs and images. Lightweight, no deep learning required.
- **Package**: `pip install img2table`
- **License**: MIT
- **Actively maintained**: Yes (v1.4.0 February 2025)
- **Borderless table handling**: **Has explicit `borderless_tables` parameter** (alpha feature). Requires providing an OCR engine when borderless mode is enabled. Can only extract borderless tables with 3+ columns. Multi-line cells may cause issues.
- **Integration with GMFT**: GMFT v0.3+ includes an `Img2TableDetector` that wraps img2table, with config options `implicit_rows`, `implicit_columns`, `borderless_tables`, and `min_confidence`. This means you can use img2table's borderless detection THROUGH GMFT's interface.
- **Strengths**: Lightweight; no GPU needed; explicit borderless support; MIT license; integrated with GMFT
- **Weaknesses**: Borderless detection is alpha quality; requires OCR engine for borderless mode; minimum 3 columns; relies on line detection which may not work for fully space-aligned tables

**Source**: [GitHub](https://github.com/xavctn/img2table), [borderless example](https://github.com/xavctn/img2table/blob/main/examples/borderless.ipynb), [PyPI](https://pypi.org/project/img2table/)

### 2.5 deepdoctection

- **What it is**: Python library for document analysis pipelines using deep learning. Can parse documents detecting layout structures including tables with full table semantics.
- **Package**: `pip install deepdoctection[pt]` (PyTorch) or `deepdoctection[tf]` (TensorFlow)
- **License**: Apache-2.0
- **Actively maintained**: Yes (active through 2024-2025)
- **Borderless table handling**: **Acknowledged weakness.** A GitHub issue (#361, August 2024) specifically raises borderless table detection as a limitation: "for borderless tables, the accuracy of row, column and cell detection could be prone to error." The library works great for bordered tables but struggles with borderless ones.
- **Strengths**: Composable pipeline architecture; supports multiple model backends; Apache-2.0 license; good documentation
- **Weaknesses**: Borderless tables are a known weak point; complex dependency tree; slower than simpler tools

**Source**: [GitHub](https://github.com/deepdoctection/deepdoctection), [Issue #361](https://github.com/deepdoctection/deepdoctection/issues/361)

---

## 3. End-to-End Document Understanding

### 3.1 Docling (IBM)

- **What it is**: Open-source document conversion toolkit using DocLayNet for layout analysis and TableFormer for table structure recognition.
- **Package**: `pip install docling`
- **License**: MIT
- **Actively maintained**: Yes (10k GitHub stars in first month, #1 trending repo on GitHub Nov 2024)
- **Borderless table handling**: **TableFormer explicitly handles tables "with partial or no borderlines."** Uses OTSL (Optimized Table Structure Language) tokenization that reduces token count ~80% vs HTML while improving accuracy. TEDS scores: 91% to 98.5% on simple tables, 88.7% to 95% on complex tables.
- **Benchmarks**: Top-tier table structure recognition. However, in your existing experiments, Docling times out on 67% of the corpus (driven by TableFormer complexity on large tables).
- **Per-page extraction**: Works at 7-9s/page, viable for targeted use
- **Strengths**: Excellent table structure recognition including borderless; MIT license; well-engineered; integrated pipeline
- **Weaknesses**: **Very slow for full documents** (300s timeout on 10/15 corpus docs); per-page mode is viable but expensive; complex dependency chain; RapidOCR backend is poor for English text

**Source**: [GitHub](https://github.com/docling-project/docling), [Technical Report](https://research.ibm.com/publications/docling-technical-report)

### 3.2 Unstructured.io

- **What it is**: Document processing library for converting various document formats into structured elements.
- **Package**: `pip install unstructured` (OSS) or `pip install unstructured-client` (API)
- **License**: Apache-2.0 (OSS version)
- **Actively maintained**: Yes (multiple releases through Jan 2025)
- **Borderless table handling**: Uses ML-based table detection but has documented accuracy issues. A December 2024 GitHub issue reports "does not identify tables properly in complex PDFs, sometimes missing last few rows or entire columns."
- **Strengths**: Handles many document types; API and OSS options; good for general document processing
- **Weaknesses**: Table detection accuracy issues on complex PDFs; less control over detection parameters than specialized tools; API costs for hosted version

**Source**: [GitHub](https://github.com/Unstructured-IO/unstructured), [Issue #3804](https://github.com/Unstructured-IO/unstructured/issues/3804)

### 3.3 Marker-PDF

- **What it is**: Fast PDF-to-markdown converter by Vik Paruchuri (same author as Surya). Uses Surya for OCR/layout and custom models for structure.
- **Package**: `pip install marker-pdf`
- **License**: GPL-3.0
- **Actively maintained**: Yes (very active, 2024-2025)
- **Borderless table handling**: Can use `--use_llm` flag to leverage Gemini 2.0 Flash for table formatting. For borderless tables, `OCR_ALL_PAGES=true` forces OCR on all pages, which can help when table layouts aren't recognized.
- **Benchmarks**: Tested against FinTabNet for table extraction
- **Strengths**: Fast; integrated pipeline; LLM-assisted mode for difficult tables; active development
- **Weaknesses**: GPL-3.0 license; LLM mode adds cost and latency; without LLM mode, table detection relies on Surya which may miss borderless tables

**Source**: [GitHub](https://github.com/datalab-to/marker), [PyPI](https://pypi.org/project/marker-pdf/)

### 3.4 MinerU (magic-pdf)

- **What it is**: PDF-to-markdown/JSON converter from OpenDataLab. Uses DocLayout-YOLO for layout detection and StructEqTable/TableMaster for table recognition.
- **Package**: `pip install magic-pdf[full]` or `pip install mineru`
- **License**: AGPL-3.0
- **Actively maintained**: Yes (very active, v2.6.2 October 2025)
- **Borderless table handling**: Uses DocLayout-YOLO for detection (trained on DocSynth-300K diverse documents) and StructEqTable-InternVL2-1B for table recognition. StructEqTable "delivers good results even with complex tables" in an end-to-end manner. In OmniDocBench, MinerU demonstrated "superior end-to-end table performance."
- **Benchmarks**: Top performer on OmniDocBench. MinerU + Mathpix are the best pipeline tools, significantly outperforming Marker.
- **Strengths**: State-of-the-art end-to-end pipeline; diverse training data; cross-page table merging; active development
- **Weaknesses**: AGPL-3.0 license; complex installation (conda recommended); requires GPU for best performance; heavy dependencies

**Source**: [GitHub](https://github.com/opendatalab/MinerU), [PyPI](https://pypi.org/project/mineru/)

### 3.5 Nougat (Meta)

- **What it is**: Neural Optical Understanding for Academic Documents. End-to-end transformer that converts document images directly to Markdown.
- **Package**: `pip install nougat-ocr`
- **License**: CC-BY-NC (non-commercial)
- **Actively maintained**: Partially (Facebook Research, less active since late 2023)
- **Borderless table handling**: Trained on scientific papers, converts tables to LaTeX format. Does not explicitly detect table regions -- it processes entire pages and outputs markdown/LaTeX including tables.
- **Strengths**: End-to-end (no separate detection step); good for academic documents; handles math well
- **Weaknesses**: Non-commercial license; slow; limited to scientific document style; hallucinates on out-of-distribution documents; government reports would likely be problematic

**Source**: [GitHub](https://github.com/facebookresearch/nougat), [HuggingFace](https://huggingface.co/docs/transformers/en/model_doc/nougat)

### 3.6 GOT-OCR 2.0

- **What it is**: General OCR Theory -- unified end-to-end model (580M params) for OCR including tables, math, charts, and more. Outputs in markdown, LaTeX, HTML.
- **Package**: Available via HuggingFace Transformers (`stepfun-ai/GOT-OCR2_0`)
- **License**: Apache-2.0
- **Actively maintained**: Yes (merged to HuggingFace Transformers Feb 2025)
- **Borderless table handling**: Trained on ~0.3M rendered table images from LaTeX sources. Can generate structured output (markdown/HTML) for tables. As an end-to-end model, it processes visual input directly without separate detection.
- **Benchmarks**: Included in OmniDocBench evaluation alongside Nougat and PaddleOCR
- **Strengths**: End-to-end; Apache-2.0 license; compact model (580M params); multi-format output
- **Weaknesses**: Primarily trained on Chinese + academic documents; government report tables are out-of-distribution; relatively new, less battle-tested

**Source**: [GitHub](https://github.com/Ucas-HaoranWei/GOT-OCR2.0), [HuggingFace](https://huggingface.co/docs/transformers/en/model_doc/got_ocr2)

### 3.7 RapidTable

- **What it is**: Dedicated table recognition library using PP-Structure models and modelscope algorithms. Separate models for wired/wireless tables.
- **Package**: `pip install rapid-table`
- **License**: Apache-2.0
- **Actively maintained**: Yes (September 2025 release)
- **Borderless table handling**: **Includes explicit `lineless_table_rec` algorithm** for borderless tables. Separate processing paths for wired and wireless tables.
- **Benchmarks**: **Highest table recognition scores in OmniDocBench** (mAP ~82.5). Top performer among OCR-based approaches.
- **Strengths**: Top benchmark performance; explicit borderless support; Apache-2.0; lightweight; ONNX-based inference
- **Weaknesses**: Based on PP-Structure (PaddlePaddle ecosystem); documentation primarily in Chinese; may need PaddleOCR for text recognition

**Source**: [GitHub](https://github.com/RapidAI/RapidTable), [PyPI](https://pypi.org/project/rapid-table/)

---

## 4. Vision LLM Approaches

### 4.1 Claude Vision for Table Detection

- **What it is**: Using Claude's vision capabilities to identify table regions in page images
- **API**: Anthropic Messages API with image input
- **Borderless table handling**: Claude can identify tables by visual semantics (columnar alignment, numerical patterns, header rows) regardless of borders. In the table-image spike, Claude correctly identified 2/15 GMFT false positives as non-tables (p42, p48 on aries).
- **Detection approach**: Send full-page images with a structured output prompt asking Claude to identify table regions with approximate bounding boxes. Claude can return JSON with table locations.
- **Strengths**: Understands document semantics; can detect tables by content/structure regardless of visual formatting; can distinguish tables from prose; no training required
- **Weaknesses**: Expensive ($0.078/page); slow (10-15s/call); bounding box coordinates are approximate (not pixel-precise); not designed as an object detector; may miss subtle tables
- **Key finding from existing experiments**: Claude extraction from cropped images achieves exact GT match on 4/5 papers. The bottleneck is detection, not extraction.

**Source**: [Claude Vision docs](https://platform.claude.com/docs/en/build-with-claude/vision), [Claude Vision Object Detection](https://github.com/Doriandarko/Claude-Vision-Object-Detection)

### 4.2 Gemini 2.0/2.5 Bounding Box Detection

- **What it is**: Google's Gemini models can return pixel-coordinate bounding boxes for detected objects in images, including document elements.
- **API**: Google Vertex AI / Gemini API
- **Borderless table handling**: Gemini can detect tables by visual structure and return normalized coordinates (0-1000 scale) in `[y_min, x_min, y_max, x_max]` format.
- **Detection approach**: Send page image with prompt like "Detect all tables in this document page and return their bounding boxes as JSON." Gemini returns structured JSON with `box_2d` coordinates and labels.
- **Strengths**: Native bounding box output; can be prompted for specific detection tasks; enterprise pricing options; fast with Flash models
- **Weaknesses**: API cost; requires Google Cloud setup; coordinate precision varies; marker-pdf already uses Gemini 2.0 Flash for table formatting
- **Notable**: Gemini 2.0-Flash achieves comparable accuracy to Claude 3.5 Sonnet at much lower cost. This makes it attractive for table detection as a pre-filter.

**Source**: [Vertex AI bounding box docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/bounding-box-detection), [Spatial understanding notebook](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/use-cases/spatial-understanding/spatial_understanding.ipynb)

### 4.3 GPT-4V / GPT-4o for Table Detection

- **What it is**: OpenAI's vision models can identify and extract tables from document images
- **API**: OpenAI API with image input
- **Borderless table handling**: Similar to Claude -- can detect tables by semantic content
- **Strengths**: Strong vision capabilities; structured output mode
- **Weaknesses**: Cost; speed; similar limitations to other vision LLMs for precise detection

### 4.4 Hybrid: VLM Detection + Specialized Extraction

The most promising approach from the literature combines:
1. **Detection**: Vision LLM (Gemini Flash or Claude) identifies table regions in full page
2. **Cropping**: Extract table regions as cropped images using bounding boxes
3. **Extraction**: Send cropped images to specialized table extraction (Claude, GMFT formatter, etc.)

This "detect with VLM, extract with specialist" pattern is described in Roboflow's research and used by marker-pdf with Gemini.

**Source**: [Roboflow: Table and Figure Understanding](https://blog.roboflow.com/table-and-figure-understanding/)

---

## 5. GMFT Tuning

### 5.1 Confidence Threshold

GMFT's `AutoTableDetector` wraps Microsoft Table Transformer. The confidence threshold is applied in post-processing:

- **Current behavior**: The pipeline uses `confidence >= 0.98` as the filter threshold
- **GMFT's behavior**: GMFT passes through the raw confidence scores from TATR; the 0.98 threshold is applied in the pipeline code, not in GMFT itself
- **TATR's post-processing**: `image_processor.post_process_object_detection(outputs, threshold=X)` accepts any threshold value
- **Effect of lowering**: On aries_cost_account, lowering from 0.98 to 0.95 would recover ~3 more tables (confidence 0.976-0.980) but risks more false positives

### 5.2 Alternative Detectors via GMFT

GMFT v0.3+ supports alternative detectors through its plugin system:

```python
from gmft.detectors.img2table import Img2TableDetector, Img2TableDetectorConfig

config = Img2TableDetectorConfig(
    borderless_tables=True,    # Enable borderless detection (alpha)
    implicit_rows=False,
    implicit_columns=False,
    min_confidence=50
)
detector = Img2TableDetector(config=config)
```

This gives borderless detection through img2table's algorithm while keeping GMFT's formatting pipeline.

### 5.3 Custom TATR Models

GMFT's `TATRDetector` loads the model from HuggingFace. In principle, you could:
1. Fine-tune `microsoft/table-transformer-detection` on annotated government report pages
2. Point GMFT at the fine-tuned model checkpoint
3. Use the fine-tuned model for detection while keeping GMFT's extraction pipeline

This requires creating training data (annotating table regions in aries-style documents) but would directly address the out-of-distribution problem.

### 5.4 GMFT Configuration Summary

| Config | Default | Adjustable | Effect |
|--------|---------|-----------|--------|
| Detection confidence | Passed through | Yes (in pipeline code) | Lower = more recall, more FPs |
| Detector backend | TATRDetector | Yes (Img2TableDetector) | Different detection algorithm |
| `borderless_tables` | False (img2table only) | Yes | Enable borderless detection |
| Formatter threshold | 0.3 | Yes (TATRFormatConfig) | Affects row/column recognition |
| Large table assumption | Auto | Yes (AutoFormatConfig) | Algorithmic rows for large tables |

**Source**: [GMFT Config Guide](https://gmft.readthedocs.io/en/latest/config.html), [GMFT detectors](https://gmft.readthedocs.io/en/latest/detectors/img2table.html)

---

## 6. Benchmark Landscape

### 6.1 Key Datasets

| Dataset | Domain | Borderless? | Size | Notes |
|---------|--------|------------|------|-------|
| PubTables-1M | Scientific papers | Some | 1M tables | TATR training data; academic bias |
| FinTabNet | Financial reports | Many | 113K tables | Complex, often borderless |
| ICDAR-2013 | Mixed documents | Some | 238 tables | Classic benchmark, small |
| ICDAR-2019 | Mixed documents | Yes | Modern | Updated from 2013 |
| DocSynth-300K | Synthetic diverse | Yes | 300K | DocLayout-YOLO training |
| PubTabNet | Scientific papers | Some | 568K | Table structure recognition |
| OmniDocBench | Diverse real-world | Yes (categorized) | CVPR 2025 | **Most relevant benchmark** -- categorizes tables by frame type |
| TableBank | Diverse | Yes | 417K | Word/LaTeX documents |

### 6.2 OmniDocBench Results (Most Relevant)

OmniDocBench (CVPR 2025) is the most relevant benchmark because it explicitly categorizes tables by frame type (bordered, partially bordered, borderless) and evaluates on diverse real-world documents.

**Top performers on table recognition (overall):**
1. RapidTable (~82.5 mAP) -- best OCR-based
2. MinerU -- best pipeline tool
3. Mathpix -- best commercial
4. PaddleOCR -- strong on frameless tables specifically

**On frameless/borderless tables specifically:**
- PaddleOCR performs well with accurate predictions
- Qwen2-VL-7B exhibits errors on frameless tables
- Pipeline tools (MinerU, Mathpix) handle challenging tables better than end-to-end models

### 6.3 Critical Gap: No Government Report Dataset

**None of the standard benchmarks include government cost reports.** PubTables-1M is scientific papers. FinTabNet is SEC filings. ICDAR is mixed but small. The aries_cost_account style -- large format, many space-aligned tables, mixed narrative and tabular content, government formatting conventions -- is essentially unrepresented.

This means any benchmark numbers should be treated as upper bounds for your use case. Models trained on PubTables-1M or FinTabNet will likely underperform on government reports.

---

## 7. Comparison Matrix

### 7.1 Detection Capability Assessment

| Tool | Detects borderless? | Method | Speed | License | Pip installable? |
|------|---------------------|--------|-------|---------|-----------------|
| **TATR (via GMFT)** | Partial (15/28 aries) | DL object detection | Fast | MIT | Yes (`gmft`) |
| **DocLayout-YOLO** | Likely (diverse training) | DL object detection | Very fast | Apache-2.0 | Yes (`doclayout-yolo`) |
| **YOLOv8 fine-tuned** | Explicit borderless category | DL object detection | Very fast | AGPL-3.0 | Yes (`ultralytics`) |
| **PP-Structure** | Yes (dedicated wireless models) | DL classification + detection | Medium | Apache-2.0 | Yes (`paddleocr`) |
| **Surya** | Unknown/undocumented | DL custom architecture | Medium | GPL-3.0 | Yes (`surya-ocr`) |
| **CascadeTabNet** | Explicit borderless category | DL instance segmentation | Medium | MIT | No (clone repo) |
| **img2table** | Alpha borderless support | OpenCV + OCR | Fast | MIT | Yes (`img2table`) |
| **Camelot Stream** | Extraction only (not detection) | Text spacing heuristics | Fast | MIT | Yes (`camelot-py`) |
| **pdfplumber** | Inferred from alignment | Text position analysis | Fast | MIT | Yes (`pdfplumber`) |
| **Gemini 2.0 Flash** | Yes (visual semantics) | VLM bounding boxes | Slow | API | N/A (API) |
| **Claude Vision** | Yes (visual semantics) | VLM analysis | Slow | API | N/A (API) |
| **Docling/TableFormer** | Yes (partial/no borders) | DL transformer | Very slow | MIT | Yes (`docling`) |
| **MinerU** | Likely (DocLayout-YOLO based) | DL pipeline | Medium | AGPL-3.0 | Yes (`magic-pdf`) |

### 7.2 Relevance to the Specific Problem

For space-aligned tables without borders in government reports, ranked by likely effectiveness:

| Rank | Approach | Why | Effort | Risk |
|------|----------|-----|--------|------|
| 1 | **Gemini Flash page-level detection** | VLMs understand table semantics regardless of formatting; cheap; returns bounding boxes | Medium (API integration) | Coordinate precision; API dependency |
| 2 | **PP-Structure / RapidTable** | Top benchmark performer; explicit wireless table models; proven on diverse documents | Medium (PaddlePaddle setup) | Framework dependency; English performance |
| 3 | **DocLayout-YOLO** | Diverse synthetic training; fast; Apache-2.0; integrated with MinerU | Low (pip install) | Unproven on government reports |
| 4 | **Fine-tuned TATR** | Direct fix for the problem (train on your data); keeps GMFT pipeline | High (need annotated data) | Annotation effort; may not generalize |
| 5 | **Claude page-level detection** | Already in pipeline; accurate but expensive | Low (already integrated) | Cost ($0.078/page for detection alone) |
| 6 | **GMFT Img2TableDetector borderless** | Zero new dependencies; GMFT already in pipeline | Low (config change) | Alpha quality; 3+ column requirement |
| 7 | **MinerU end-to-end** | Top OmniDocBench results; handles diverse tables | Medium (heavy install) | AGPL-3.0; complex dependencies |
| 8 | **pdfplumber heuristics** | Lightweight; text-position based detection | Medium (custom heuristics) | Over-detection on prose; tuning needed |
| 9 | **YOLOv8 fine-tuned** | Explicit borderless category; very fast | Medium (model selection + testing) | AGPL-3.0; community models vary |
| 10 | **Docling per-page** | Proven table recognition quality | Low (already tested) | 7-9s/page; timeout risk |

---

## 8. Recommended Experiments

Based on this survey, the following experiments are ordered by expected value-to-effort ratio for resolving the aries_cost_account detection gap (13 missing borderless tables).

### Experiment A: GMFT Img2TableDetector with `borderless_tables=True` (Effort: 1 hour)

**Rationale**: Zero new dependencies. GMFT already supports this detector. Just swap the detector config.

```python
from gmft.detectors.img2table import Img2TableDetector, Img2TableDetectorConfig

config = Img2TableDetectorConfig(borderless_tables=True, min_confidence=50)
detector = Img2TableDetector(config=config)
# Run on aries_cost_account pages
```

**Expected outcome**: Marginal improvement at best. img2table's borderless detection is alpha and relies on OCR text positions, which may not work well for the specific aries layout.

### Experiment B: Gemini 2.0 Flash Page-Level Detection (Effort: 3-4 hours)

**Rationale**: Gemini Flash is cheap ($0.0375/1M input tokens), returns native bounding boxes in JSON, and understands document semantics. Use it to detect table regions, then crop + send to Claude for extraction.

```python
# Pseudocode
for page_image in aries_pages:
    response = gemini.generate(
        image=page_image,
        prompt="Detect all tables on this page. Return JSON array with bounding boxes: [{box_2d: [y0,x0,y1,x1], label: 'table'}]"
    )
    for table_bbox in response.tables:
        cropped = crop_image(page_image, table_bbox)
        markdown = claude.extract_table(cropped)
```

**Expected outcome**: High. Gemini Flash can likely detect most of the 13 missing tables since it understands columnar numeric data as "table" regardless of borders. Cost would be ~$0.002/page for detection + $0.076/table for Claude extraction.

### Experiment C: DocLayout-YOLO Standalone Detection (Effort: 2-3 hours)

**Rationale**: Fast, Apache-2.0, diverse training data, pip-installable. Test whether its training on DocSynth-300K catches space-aligned tables that TATR misses.

```python
from doclayout_yolo import YOLOv10

model = YOLOv10("path/to/doclayout_yolo_model")
results = model.predict(page_image)
table_boxes = [r for r in results if r.label == "table"]
```

**Expected outcome**: Uncertain. DocSynth-300K is synthetic and may not include government report style tables, but the diverse training could provide better generalization than PubTables-1M.

### Experiment D: PP-Structure / RapidTable (Effort: 4-6 hours)

**Rationale**: Top OmniDocBench scores; explicit wireless table models; proven on diverse documents. Higher effort due to PaddlePaddle installation.

```python
from rapid_table import RapidTable

engine = RapidTable()
result, _ = engine(page_image)  # Returns HTML table
```

**Expected outcome**: High for table recognition (converting detected table images to structured output). Moderate for detection -- need to pair with PP-Structure's layout detection for table region identification.

### Experiment E: Custom Page-Level Heuristic Detection (Effort: 4-6 hours)

**Rationale**: Since the aries tables are space-aligned numeric data, a simple heuristic could detect them: identify pages with multiple lines of column-aligned numbers/text separated by consistent whitespace. Use PyMuPDF's text extraction with position data.

```python
import pymupdf
# For each page, extract text blocks with positions
# Look for: multiple consecutive lines with similar x-positions (columns)
# with numeric content and consistent vertical spacing
```

**Expected outcome**: Moderate. This approach is fragile and document-specific, but could work well for the aries_cost_account format specifically. Not generalizable.

---

## 9. Key Takeaways

1. **The bottleneck is detection, not extraction.** This is confirmed by the table-image spike (Claude extracts accurately from any detected table). The survey confirms no single tool solves borderless detection reliably for government reports.

2. **VLM-based detection (Gemini Flash) is the most promising new approach.** It's cheap, understands document semantics, and returns bounding boxes natively. This sidesteps the training data distribution problem entirely.

3. **PP-Structure/RapidTable has the best benchmark numbers** on diverse table types including borderless, but requires PaddlePaddle framework.

4. **GMFT has more tuning knobs than we've used.** The Img2TableDetector with `borderless_tables=True` is untested. Lowering TATR confidence threshold from 0.98 to 0.95 would recover ~3 more detections.

5. **Fine-tuning TATR on government report data** would directly address the out-of-distribution problem but requires annotation effort (~50-100 annotated table regions).

6. **No standard benchmark includes government cost reports.** All published numbers are on scientific papers, financial filings, or synthetic documents. Our aries_cost_account is genuinely novel territory.

7. **The multi-approach strategy is correct.** Given the domain gap, the most robust approach is a detection ensemble: GMFT for bordered tables (which it handles well) + a VLM or PP-Structure detector for borderless tables.

---

## Sources

### Deep Learning Models
- [microsoft/table-transformer-detection on HuggingFace](https://huggingface.co/microsoft/table-transformer-detection)
- [Table Transformer GitHub](https://github.com/microsoft/table-transformer)
- [CascadeTabNet GitHub](https://github.com/DevashishPrasad/CascadeTabNet)
- [LayoutLMv3](https://www.emergentmind.com/topics/layoutlmv3)
- [DiT - Microsoft Research](https://www.microsoft.com/en-us/research/lab/microsoft-research-asia/articles/dit-self-supervised-pre-training-for-document-image-transformers/)
- [DocLayout-YOLO GitHub](https://github.com/opendatalab/DocLayout-YOLO)
- [YOLOv8 table detection on HuggingFace](https://huggingface.co/foduucom/table-detection-and-extraction)
- [Surya GitHub](https://github.com/VikParuchuri/surya)
- [PaddleOCR PP-Structure](https://github.com/PaddlePaddle/PaddleOCR/blob/main/ppstructure/table/README.md)
- [PP-TableMagic Documentation](https://paddlepaddle.github.io/PaddleX/3.3/en/pipeline_usage/tutorials/ocr_pipelines/table_recognition_v2.html)
- [DocTR GitHub](https://github.com/mindee/doctr)

### Traditional/Hybrid Tools
- [Camelot Documentation](https://camelot-py.readthedocs.io/)
- [Tabula-py Documentation](https://tabula-py.readthedocs.io/)
- [pdfplumber GitHub](https://github.com/jsvine/pdfplumber)
- [img2table GitHub](https://github.com/xavctn/img2table)
- [img2table borderless example](https://github.com/xavctn/img2table/blob/main/examples/borderless.ipynb)
- [deepdoctection GitHub](https://github.com/deepdoctection/deepdoctection)
- [deepdoctection borderless issue #361](https://github.com/deepdoctection/deepdoctection/issues/361)

### End-to-End Document Understanding
- [Docling GitHub](https://github.com/docling-project/docling)
- [Docling Technical Report](https://research.ibm.com/publications/docling-technical-report)
- [Unstructured.io GitHub](https://github.com/Unstructured-IO/unstructured)
- [Marker-PDF GitHub](https://github.com/datalab-to/marker)
- [MinerU GitHub](https://github.com/opendatalab/MinerU)
- [Nougat GitHub](https://github.com/facebookresearch/nougat)
- [GOT-OCR 2.0 GitHub](https://github.com/Ucas-HaoranWei/GOT-OCR2.0)
- [RapidTable GitHub](https://github.com/RapidAI/RapidTable)

### Vision LLM Approaches
- [Claude Vision API Docs](https://platform.claude.com/docs/en/build-with-claude/vision)
- [Gemini Bounding Box Detection](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/bounding-box-detection)
- [Gemini Spatial Understanding Notebook](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/use-cases/spatial-understanding/spatial_understanding.ipynb)
- [Table and Figure Understanding with CV](https://blog.roboflow.com/table-and-figure-understanding/)

### GMFT Tuning
- [GMFT GitHub](https://github.com/conjuncts/gmft)
- [GMFT Config Guide](https://gmft.readthedocs.io/en/latest/config.html)
- [GMFT Img2Table Detector](https://gmft.readthedocs.io/en/latest/detectors/img2table.html)
- [GMFT Advanced](https://gmft.readthedocs.io/en/latest/advanced.html)

### Benchmarks & Surveys
- [OmniDocBench (CVPR 2025)](https://arxiv.org/abs/2412.07626)
- [OmniDocBench GitHub](https://github.com/opendatalab/OmniDocBench)
- [PDF-Extract-Kit](https://github.com/opendatalab/PDF-Extract-Kit)
- [Deep Learning for Table Detection and Structure Recognition: A Survey](https://dl.acm.org/doi/10.1145/3657281)
- [PubTables-1M Paper](https://www.researchgate.net/publication/363906967_PubTables-1M_Towards_comprehensive_table_extraction_from_unstructured_documents)
- [Borderless Tables Detection GitHub](https://github.com/ShakilMahmudShuvo/Borderless-Tables-Detection)
- [SEMv3: Table Separation Line Detection (IJCAI-24)](https://www.ijcai.org/proceedings/2024/0132.pdf)
- [PDF Extraction Benchmark 2025](https://procycons.com/en/blogs/pdf-data-extraction-benchmark/)
- [VLM Table Recognition Benchmark (IJCAI 2025)](https://arxiv.org/html/2412.20662v2)
