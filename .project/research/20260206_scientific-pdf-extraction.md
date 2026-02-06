# Scientific PDF extraction: a field guide to solving every failure mode

**The single most important finding: no tool solves everything, but a layered hybrid pipeline can.** The best approach for extracting structured content from nuclear fusion research papers combines pymupdf4llm for fast text extraction with targeted ML models for the specific elements it garbles — GMFT or Docling's TableFormer for borderless tables, UniMERNet or Surya for equations, custom heuristics for headers, and simple post-processing for ligatures and page artifacts. Each of the five failure modes described has practical, code-ready solutions available today, and the 2025–2026 tool landscape has matured dramatically around exactly these problems.

The field is converging on two architectural patterns: **modular pipelines** (MinerU, Marker, PDF-Extract-Kit) that chain specialized models for layout, tables, equations, and OCR; and **end-to-end VLMs** (Granite-Docling, olmOCR, Nougat) that process page images holistically. For techno-economic data in fusion papers, the pipeline approach wins — it gives you control over each extraction stage and lets you optimize the component that matters most (tables) independently.

---

## Borderless tables: the hardest problem, now tractable with ML

This is the user's highest-priority failure mode and the area where the gap between old and new tools is widest. pymupdf4llm's `lines_strict` strategy depends on detecting visible cell borders via line-art analysis — a fundamentally doomed approach for academic tables that use whitespace alignment instead of rules. **ML-based approaches outperform rule-based tools by 20–30 percentage points** on scientific tables: Docling's TableFormer achieves **93.6% average accuracy** versus Tabula at 67.9% and Camelot at 73.0%.

**GMFT (Give Me Formatted Tables)** is the most actionable drop-in replacement. It wraps Microsoft's Table Transformer (DETR-based, trained on **PubTables-1M** — 947K annotated tables from PubMed Central scientific papers), requires no GPU, installs with `pip install gmft`, and outputs Pandas DataFrames, CSV, Markdown, or LaTeX in ~5 lines of code. Because the training data is overwhelmingly scientific papers with borderless tables, it handles exactly the failure case pymupdf4llm misses. Processing runs at ~1.4s per page and ~1.2s per table on CPU with only ~270MB of model weights. It supports multi-header tables (`enable_multi_header=True`) and spanning cells (`semantic_spanning_cells=True`).

For maximum accuracy on complex tables with merged cells and multi-row headers, **Docling's TableFormer** is the strongest option. A 2025 benchmark on sustainability reports showed **97.9% accuracy** on complex table extraction, and a separate academic benchmark found Docling "achieves the best overall performance across datasets for table detection." TableFormer was explicitly designed for "partial or no borderlines, empty cells, rows or columns, cell spans and hierarchy." The trade-off is speed — Docling processes at ~4 seconds per page versus GMFT's sub-second table extraction.

**MinerU 2.5** (released 2025, **48.8K GitHub stars**) specifically claims "drastically improved parsing for rotated tables, borderless/semi-structured tables, and long/complex tables" using a decoupled two-stage VLM pipeline. Its 1.2B parameter model claims state-of-the-art on OmniDocBench, surpassing GPT-4o and Gemini 2.5 Pro on table recognition. It outputs tables in HTML format, which preserves complex structures better than Markdown pipe tables. **PaddleOCR's PP-StructureV3** takes a clever approach: it classifies tables as "wired" (bordered) or "wireless" (borderless) first, then routes each to a specialized recognition model (`SLANeXt_wired` vs `SLANeXt_wireless`).

For the hardest cases — deeply merged cells, spanning headers, tables split across pages — a **VLM fallback** is the emerging best practice. Render the page at 300+ DPI, send to GPT-4o or Gemini with a structured prompt requesting the table as Markdown or JSON, then cross-validate against the deterministic extraction. This hybrid approach costs ~$0.01–0.03 per page but catches the ~5–10% of tables that defeat even the best ML models. Marker's `--use_llm` flag implements this pattern, merging tables across pages and fixing column alignment using an LLM pass.

The recommended integration for the existing pipeline:

```python
from gmft.auto import AutoTableDetector, AutoTableFormatter
from gmft.pdf_bindings import PyPDFium2Document

detector = AutoTableDetector()
formatter = AutoTableFormatter()
doc = PyPDFium2Document("fusion_paper.pdf")
for page in doc:
    tables = detector.extract(page)
    for table in tables:
        ft = formatter.extract(table)
        df = ft.df()  # Pandas DataFrame with actual structure
```

---

## Header detection: heuristics first, ML if needed

pymupdf4llm's `IdentifyHeaders` class creates a `{font_size: '# '}` mapping by scanning the document and treating the most popular font size as body text. When bold section headers (e.g., "1. Introduction", "2. Methods") use the same point size as body text, they receive `**bold**` markers instead of `#` headers. The fix is straightforward because pymupdf4llm exposes a **custom `hdr_info` callback** that replaces the font-size heuristic entirely:

```python
import re
def detect_academic_headers(span, page=None):
    text = span["text"].strip()
    is_bold = bool(span["flags"] & 16)  # bit 4 = bold
    if is_bold and re.match(r'^\d+\.\d+\.\d+\.?\s', text): return "### "
    if is_bold and re.match(r'^\d+\.\d+\.?\s', text): return "### "
    if is_bold and re.match(r'^\d+\.?\s+[A-Z]', text): return "## "
    if is_bold and text.isupper() and len(text) < 60: return "## "
    return ""

md = pymupdf4llm.to_markdown(doc, hdr_info=detect_academic_headers)
```

This callback receives each text span's font metadata (size, flags for bold/italic, font name) and returns the header prefix. Combining **bold detection + section numbering regex + all-caps detection + line length** catches the vast majority of academic paper headers. A complementary approach is pymupdf4llm's `TocHeaders` class, which uses the PDF's bookmark tree instead of font analysis — effective when PDFs have proper bookmarks, though many scientific papers lack them.

For a regex-based **post-processor** on already-extracted Markdown, bold lines matching numbered section patterns (`**1. Introduction**`) can be converted to headers (`## 1. Introduction`) in a single pass. This is the lowest-effort fix and handles the most common academic paper format.

For ML-powered header detection, the tools that handle this best are **GROBID** (~97% accuracy on section titles using cascaded CRF/BidLSTM-CRF models with 68 fine-grained labels), **Marker** (custom LayoutLMv3 model detecting 11 block types including `Section-header` and `Title`), and **Docling** (DocLayNet-trained model classifying `Section-header` as one of 11 layout classes). The key training datasets are **DocLayNet** (80,863 pages, 11 classes including Section-header, hand-annotated) and **PubLayNet** (360K pages from PubMed Central, 5 classes including Title). A notable limitation across all pipeline tools: **multi-level heading depth** (H1 vs H2 vs H3) remains poorly supported — MinerU only supports first-level headings, and the READOC benchmark (ACL 2025) found that "pipeline tools lack modules to assess heading depth."

---

## Equations: detect regions, then OCR to LaTeX

PDF equations garble because math fonts use specialized encodings — characters like integral signs, Greek letters, and operators map to private Unicode areas or use custom CMaps that PDF text extractors can't resolve. pymupdf4llm returns `chr(0xFFFD)` (replacement character) for unmapped glyphs. The solution is to **bypass PDF text extraction entirely for equation regions** and instead render them as images for neural LaTeX OCR.

The best open-source pipeline is **PDF-Extract-Kit** (OpenDataLab), which chains three specialized models: **DocLayout-YOLO** for layout detection (identifies equation regions on the page), a fine-tuned **YOLOv8** for formula detection (locates both inline and display equations), and **UniMERNet** for formula recognition (converts equation images to LaTeX). UniMERNet, trained on the **UniMER-1M dataset** (1M+ formulas from arXiv, Wikipedia, and StackExchange), achieves accuracy **comparable to commercial Mathpix** on the CDM metric (accepted at CVPR 2025) and is the current open-source state of the art for complex multi-line equations with fractions, integrals, and summations.

**Marker** offers simpler integration: `pip install marker-pdf` gives you a pipeline that uses Surya for layout detection and its integrated LaTeX OCR module (formerly Texify) for equations, outputting clean Markdown with `$equation$` and `$$equation$$` delimiters. It runs **4–10× faster than Nougat** with lower hallucination risk, though its equation detection has blind spots — inline math can be missed without the `--use_llm` flag. Surya's equation recognition F1 recently improved from 0.947 to **0.968**.

**Nougat** (Meta, ~9.7K stars) remains the strongest tool for converting entire arXiv-style papers end-to-end — its Vision Transformer architecture takes raw page images and outputs Mathpix Markdown with LaTeX math, excelling on equations because it was trained on 8M+ articles (88% from arXiv LaTeX sources). However, it has a critical **repetition/hallucination problem** (degenerating into repeated text on ~1.5–5% of pages), runs ~4× slower than Marker, generalizes poorly outside arXiv-style layouts, and is essentially unmaintained since 2023.

For a pipeline already using pymupdf4llm, the optimal hybrid approach is:

1. Extract text normally with pymupdf4llm (handles ~90% of content correctly)
2. Detect garbled regions (spans containing `chr(0xFFFD)` clusters)
3. For equation regions: render at 300+ DPI → run UniMERNet or Surya LaTeX OCR
4. Replace garbled spans with `$LaTeX$` in the final Markdown

**Mathpix** remains the commercial gold standard at $0.0035/page for batch processing — worth considering as a selective fallback for the ~5% of equations open-source tools mishandle, particularly matrices and multi-line aligned equations.

Newer entrants worth monitoring: **PP-FormulaNet** (Baidu, 2025) claims 6% higher BLEU than UniMERNet with a 16× faster small variant; **OlmOCR-2** (Allen AI, Oct 2025) scores 82.4 on olmOCR-Bench with strong arXiv equation handling; and **Granite-Docling** (IBM, Sept 2025) added LaTeX equation support to Docling's pipeline.

---

## Page artifacts and ligatures: solved problems with simple fixes

**Header/footer/page number removal** has multiple proven approaches. The simplest is **position-based filtering** — pymupdf4llm's `margins` parameter crops a fixed region from each page edge. More robust is **DBSCAN clustering** on text block coordinates across all pages (from a PyMuPDF community solution): cluster blocks by `(x0, y0, x1, y1, len(text))`, identify the largest cluster as body text, and classify remaining clusters as artifacts. Cross-page text deduplication — comparing the first and last 3 lines of each page and removing lines that appear identically across >50% of pages (modulo page numbers) — catches running headers reliably.

Docling handles this automatically: its DocLayNet model classifies regions as `PAGE_HEADER` or `PAGE_FOOTER` and **skips them in Markdown output by default**. Marker similarly detects `Page-footer` and `Page-header` using its LayoutLMv3 model, then applies heuristics to remove them. GROBID's segmentation model explicitly detects headnotes and footnotes as separate zones. If switching primary extractors isn't desired, a **regex-based post-processor** stripping isolated page numbers (`re.sub(r'^\s*\d+\s*$', '', line)`) combined with the DBSCAN approach handles most cases.

**Unicode ligature failures** (fi→�, fl→�) stem from incomplete ToUnicode CMaps in the PDF's font dictionaries. Three fixes, in order of increasing robustness:

- **PyMuPDF's built-in decomposition**: MuPDF splits known ligatures (fi, ff, fl, ft, st, ffi, ffl) into individual characters during extraction. Ensure `TEXT_PRESERVE_LIGATURES` flag is set to 0.
- **Post-processing replacement**: The `ftfy` library (`ftfy.fixes.fix_latin_ligatures()`) or a simple dictionary (`{"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl"}`) handles cases where ligature Unicode codepoints (U+FB00–FB04) are extracted correctly but need decomposition.
- **Dictionary-based reconstruction** for replacement characters: The `ligatures` library (github.com/adamheins/ligatures) rebuilds words from context — only 3.42% of English words contain common ligatures, and only 1.51% of those are ambiguous, making dictionary lookup highly accurate for reconstructing `di�erent` → `different`.

Chain all three: MuPDF decomposition → `replace_ligatures()` → `ftfy` → dictionary fallback. For fixing PDFs at the source, `pdf-fix-tuc` repairs ToUnicode CMaps directly in the PDF file.

---

## The 2025–2026 tool landscape and benchmarks

The field has consolidated around several major benchmarks. **OmniDocBench** (CVPR 2025, 981 pages across 9 document types) found that pipeline tools — MinerU, Marker, and Mathpix — **outperform VLMs on tables and formulas**, while VLMs are stronger on specialized documents like slides and handwritten notes. MinerU showed the most consistent reading order prediction. **READOC** (ACL Findings 2025) revealed that "understanding localized structured data such as tables and formulas is relatively difficult" for all tools, and that heading depth recognition is a universal weakness. The **Procycons benchmark** ranked Docling first for text fidelity (100%) and table extraction (97.9%), with Unstructured at 75% on complex tables and LlamaParse struggling with multi-column layouts.

The major tools ranked by primary strength:

- **MinerU** (48.8K stars, AGPL-3.0): Best overall benchmark performer. Strong on formulas (UniMERNet), reading order, and general scientific papers. Only H1 heading support is a notable limitation. Version 2.5 added a VLM backend and dramatically improved borderless table handling.
- **Docling** (52.3K stars, MIT): Best table extraction via TableFormer. Strong layout analysis via DocLayNet. Granite-Docling VLM (258M params, Sept 2025) added equation and chart support. Growing ecosystem (docling-serve, docling-graph, docling-eval). Can hang on certain PDFs.
- **Marker** (31.3K stars, GPL-3.0): Best balance of speed, quality, and ease of use. LayoutLMv3 for structure, Surya for OCR, Texify for equations. `--use_llm` mode significantly improves table and equation quality. ~25 pages/second on H100.
- **GROBID** (Apache 2.0): Unrivaled for bibliographic metadata, citation parsing, and fine-grained document structure (68 labels, ~97% section title accuracy). Used at ResearchGate, Semantic Scholar, HAL. Weak on table content and equations.
- **Nougat** (9.7K stars, MIT): Best equation-to-LaTeX for arXiv papers. Essentially dormant since 2023. Repetition loop and domain generalization issues make it unreliable as a primary extractor.

Notable lesser-known tools: **scipdf_parser** (Python wrapper around GROBID returning structured dicts), **deepdoctection** (orchestrates Detectron2/Transformers/Tesseract for layout analysis), **two-tier document parser** (Docker pipeline combining pymupdf4llm fast/CPU + MinerU accurate/GPU with REST API), **text-extract-api** (document extraction API using modern OCRs + Ollama), and **PaperQA2** (agentic RAG for scientific papers with superhuman QA performance).

A 2025 paper by Moreira-Filho et al. in *WIREs Computational Molecular Science* describes a **KNIME workflow** integrating GROBID, Marker, Docling, pymupdf4llm, and tabula-py with LLMs (Llama 3.1, Claude 3.5, GPT-4o) for automated data extraction from scientific papers — the closest published example of a comprehensive multi-tool pipeline addressing all failure modes.

---

## Recommended pipeline architecture for fusion research papers

Given the priority ordering (tables > structure > equations) and the existing pymupdf4llm investment, here is a practical layered architecture:

**Layer 1 — Fast extraction (pymupdf4llm, CPU)**. Use pymupdf4llm with the custom `hdr_info` callback for header detection and the ligature post-processor. This handles ~80% of content correctly in milliseconds. Apply DBSCAN-based header/footer removal or cross-page deduplication as post-processing.

**Layer 2 — Table extraction (GMFT or Docling TableFormer)**. Run GMFT on every page to detect and extract borderless tables into DataFrames. Replace pymupdf4llm's garbled table regions with the structured GMFT output formatted as Markdown pipe tables. For papers with especially complex tables (merged cells, multi-row headers), use Docling's TableFormer as a secondary pass.

**Layer 3 — Equation extraction (UniMERNet or Surya)**. Detect garbled regions in pymupdf4llm output (clusters of `chr(0xFFFD)`). Render those page regions at 300 DPI. Run UniMERNet (via PDF-Extract-Kit) or Surya's LaTeX OCR on the crops. Insert LaTeX back into the Markdown with `$...$` delimiters.

**Layer 4 — VLM fallback (optional, for critical papers)**. For the most important fusion techno-economic papers, run a VLM (GPT-4o, Gemini) on rendered page images to cross-validate table values and catch any extraction errors. This is the "trust but verify" layer — compare deterministic extraction against VLM output and flag discrepancies for human review.

This architecture preserves the speed advantage of pymupdf4llm for the majority of content while surgically applying ML models only where they're needed. Each layer can be enabled or disabled independently, and the pipeline degrades gracefully — if GMFT fails on a table, the pymupdf4llm output (however imperfect) is still present; if the VLM layer is disabled, deterministic extraction still provides good results.

# PDF Extraction Research — Source References

**Total unique sources: 64**


## Table Extraction

- [I Tested 12 Best-in-Class PDF Table Extraction Tools, and the Results Were Appalling](https://medium.com/@kramermark/i-tested-12-best-in-class-pdf-table-extraction-tools-and-the-results-were-appalling-f8a9991d972e) — Medium (Mark Kramer)
- [gmft: Lightweight, performant, deep table extraction](https://github.com/conjuncts/gmft) — GitHub
- [PubTabNet](https://github.com/ibm-aur-nlp/PubTabNet) — GitHub (IBM)
- [gmft - A lightweight and high-performance deep PDF table extraction tool](https://www.aibase.com/tool/32353) — AIbase
- [gmft · PyPI](https://pypi.org/project/gmft/) — PyPI
- [gmft-locally · PyPI](https://pypi.org/project/gmft-locally/) — PyPI
- [Benchmarking Table Extraction from Heterogeneous Scientific Documents](https://arxiv.org/html/2511.16134v1) — arXiv
- [Post-Processing of Text Extraction](https://pypdf.readthedocs.io/en/stable/user/post-processing-in-text-extraction.html) — pypdf Docs
- [PaddleX General Table Recognition V2](https://paddlepaddle.github.io/PaddleX/3.3/en/pipeline_usage/tutorials/ocr_pipelines/table_recognition_v2.html) — PaddlePaddle Docs

## Full Pipeline Tools

- [Docling Technical Report (v5)](https://arxiv.org/html/2408.09869v5) — arXiv
- [Docling Technical Report (v1)](https://arxiv.org/html/2408.09869v1) — arXiv
- [MinerU: Transforms complex documents like PDFs into LLM-ready markdown/JSON](https://github.com/opendatalab/MinerU) — GitHub (OpenDataLab)
- [Marker: Convert PDF to markdown + JSON quickly with high accuracy](https://github.com/datalab-to/marker) — GitHub (Datalab)
- [pymupdf4llm · PyPI](https://pypi.org/project/pymupdf4llm/) — PyPI
- [pymupdf4llm API Documentation](https://pymupdf.readthedocs.io/en/latest/pymupdf4llm/api.html) — PyMuPDF Docs
- [GROBID: ML software for extracting information from scholarly documents](https://github.com/kermitt2/grobid) — GitHub
- [GROBID Introduction](https://grobid.readthedocs.io/en/latest/Introduction/) — GROBID Docs
- [Inside Marker: A Guided Source Code Tour for an AI-powered PDF Layout Detection Engine](https://journal.hexmos.com/marker-pdf-document-ai/) — Hexmos Journal
- [Docling: Get your documents ready for gen AI](https://github.com/docling-project/docling) — GitHub (IBM)
- [Docling Technical Report](https://research.ibm.com/publications/docling-technical-report) — IBM Research
- [DocLayNet Dataset](https://huggingface.co/datasets/docling-project/DocLayNet) — Hugging Face
- [PDF-Extract-Kit: A Comprehensive Toolkit for High-Quality PDF Content Extraction](https://github.com/opendatalab/PDF-Extract-Kit) — GitHub (OpenDataLab)
- [marker-pdf · PyPI](https://pypi.org/project/marker-pdf/0.2.4/) — PyPI
- [marker-api: Easily deployable API for PDF to markdown](https://github.com/adithya-s-k/marker-api) — GitHub
- [PaddleOCR 3.0 Technical Report](https://arxiv.org/html/2507.05595v1) — arXiv
- [IBM Granite-Docling: End-to-end document understanding](https://www.ibm.com/new/announcements/granite-docling-end-to-end-document-conversion) — IBM
- [IBM's Granite Docling: A Compact VLM for End-to-End Document Conversion](https://joshuaberkowitz.us/blog/github-repos-8/ibm-s-granite-docling-a-compact-vlm-for-end-to-end-document-conversion-1156) — Joshua Berkowitz
- [Is there a way to delete headers/footers in PDF documents?](https://github.com/pymupdf/PyMuPDF/discussions/2259) — GitHub (PyMuPDF Discussion)
- [Possible to ignore headers/footers?](https://github.com/docling-project/docling/discussions/1464) — GitHub (Docling Discussion)
- [Docling: A Guide to Building a Document Intelligence App](https://www.datacamp.com/tutorial/docling) — DataCamp
- [GROBID - Information Extraction from Scientific Publications](https://ercim-news.ercim.eu/en100/r-i/grobid-information-extraction-from-scientific-publications) — ERCIM News
- [How to exclude header and footer while extracting text?](https://github.com/jsvine/pdfplumber/discussions/968) — GitHub (pdfplumber Discussion)
- [Editing CMap / ToUnicode to achieve correct character mapping](https://github.com/pymupdf/PyMuPDF/issues/530) — GitHub (PyMuPDF Issue)
- [PyMuPDF Functions Documentation](https://pymupdf.readthedocs.io/en/latest/functions.html) — PyMuPDF Docs
- [MinerU Deep Wiki](https://deepwiki.com/opendatalab/MinerU) — DeepWiki
- [text-extract-api: Document extraction and parse API using modern OCRs + Ollama](https://github.com/CatchTheTornado/text-extract-api) — GitHub

## Equation / Math OCR

- [olmOCR: Unlocking Trillions of Tokens in PDFs with Vision Language Models](https://olmocr.allenai.org/papers/olmocr.pdf) — Allen AI
- [UniMERNet: A Universal Network for Real-World Mathematical Expression Recognition](https://arxiv.org/html/2404.15254v2) — arXiv
- [UniMERNet](https://github.com/opendatalab/UniMERNet) — GitHub (OpenDataLab)
- [Nougat: Neural Optical Understanding for Academic Documents](https://ar5iv.labs.arxiv.org/html/2308.13418) — arXiv
- [Unveiling PDF Parsing: How to extract formulas from scientific PDF papers](https://medium.com/@florian_algo/unveiling-pdf-parsing-how-to-extract-formulas-from-scientific-pdf-papers-a8f126f3511d) — Medium (Florian June)
- [Mathpix Convert API: Image & PDF digitizing API for STEM](https://mathpix.com/convert) — Mathpix
- [PP-FormulaNet: Bridging Accuracy and Efficiency in Advanced Formula Recognition](https://arxiv.org/html/2503.18382v1) — arXiv
- [Texify: Math OCR model that outputs LaTeX and markdown](https://github.com/VikParuchuri/texify) — GitHub
- [Extracting Data From PDFs Using AI: Claude 3, Donut, and Nougat](https://parsio.io/blog/extracting-data-from-pdfs-using-ai-claude-3-donut-and-nougat/) — Parsio

## Benchmarks & Evaluations

- [PDF Data Extraction Benchmark 2025: Comparing Docling, Unstructured, and LlamaParse](https://procycons.com/en/blogs/pdf-data-extraction-benchmark/) — Procycons
- [OmniDocBench: Benchmarking Diverse PDF Document Parsing (CVPR 2025)](https://openaccess.thecvf.com/content/CVPR2025/papers/Ouyang_OmniDocBench_Benchmarking_Diverse_PDF_Document_Parsing_with_Comprehensive_Annotations_CVPR_2025_paper.pdf) — CVPR 2025
- [DocLayNet: A Large Human-Annotated Dataset for Document-Layout Analysis](https://github.com/DS4SD/DocLayNet) — GitHub (IBM)
- [READOC: A Unified Benchmark for Realistic Document Structured Extraction](https://arxiv.org/html/2409.05137v1) — arXiv
- [7 Best Open-Source OCR Models 2025: Benchmarks & Cost Comparison](https://www.e2enetworks.com/blog/complete-guide-open-source-ocr-models-2025) — E2E Networks
- [A Benchmark of PDF Information Extraction Tools using a Multi-Task and Multi-Domain Evaluation Framework](https://arxiv.org/abs/2303.09957) — arXiv
- [OmniDocBench: A Comprehensive Benchmark for Document Parsing (CVPR 2025)](https://github.com/opendatalab/OmniDocBench) — GitHub (OpenDataLab)
- [OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations](https://arxiv.org/html/2412.07626v2) — arXiv

## Header/Footer & Ligature Fixes

- [Missing Ligatures and How to Find Them](https://adamheins.com/blog/missing-ligatures-and-how-to-find-them) — Adam Heins
- [pdf-fix-tuc: Fix ToUnicode CMap in PDF](https://github.com/trueroad/pdf-fix-tuc) — GitHub

## Scientific Paper Parsing

- [scipdf_parser: Python PDF parser for scientific publications](https://github.com/titipata/scipdf_parser) — GitHub
- [deepdoctection: A Repo For Document AI](https://github.com/deepdoctection/deepdoctection) — GitHub
- [PaperQA: High accuracy RAG for answering questions from scientific documents](https://github.com/Future-House/paper-qa) — GitHub
- [Automating Data Extraction From Scientific Literature Using LLMs and KNIME (Moreira-Filho et al. 2025)](https://wires.onlinelibrary.wiley.com/doi/10.1002/wcms.70047) — WIREs Computational Molecular Science

## Articles & Writeups

- [MinerU Parser: High-Precision PDF Extraction](https://www.emergentmind.com/topics/mineru-parser) — Emergent Mind
- [Comparative Evaluation of 12 Open-Source PDF Parsing Tools](https://liduos.com/en/ai-develope-tools-series-2-open-source-doucment-parsing.html) — Liduos
- [PDF Parsing for LLM Input](https://nbrosse.github.io/posts/pdf-parsing/pdf-parsing.html) — Nicolas' Notebook
- [Deep Dive into Open Source PDF to Markdown Tools: Marker, MinerU, and Alternatives](https://jimmysong.io/blog/pdf-to-markdown-open-source-deep-dive/) — Jimmy Song
- [Beyond Text Extraction: The 2025 Open OCR Revolution Powered by Vision-Language Models](https://atul4u.medium.com/beyond-text-extraction-the-2025-open-ocr-revolution-powered-by-vision-language-models-89ad33d36bbf) — Medium (TechEon)