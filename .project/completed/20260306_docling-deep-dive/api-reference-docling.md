# Docling API Reference (v2.71.0)

**Created:** 2026-02-22
**Source:** Installed package at `.venv/lib/python3.12/site-packages/docling/`

---

## DocumentConverter

**Module:** `docling.document_converter`

### Constructor

```python
DocumentConverter(
    allowed_formats: list[InputFormat] | None = None,  # None = all formats
    format_options: dict[InputFormat, FormatOption] | None = None,
)
```

### convert() — Single Document

```python
converter.convert(
    source: Path | str | DocumentStream,  # file path, URL, or stream
    headers: dict[str, str] | None = None,  # HTTP headers for URL sources
    raises_on_error: bool = True,
    max_num_pages: int = sys.maxsize,
    max_file_size: int = sys.maxsize,
    page_range: PageRange = (1, sys.maxsize),  # 1-indexed! (start, end) inclusive
) -> ConversionResult
```

**Key discovery:** `page_range` is **1-indexed** `(start, end)` inclusive tuple. `page_range=(5, 5)` extracts only page 5. This is the mechanism for single-page extraction.

### convert_all() — Batch

Same signature but `source` is `Iterable[...]` and returns `Iterator[ConversionResult]`.

### ConversionResult

```python
conv_result.document  # DoclingDocument — the main output
conv_result.status    # ConversionStatus: SUCCESS, PARTIAL_SUCCESS, FAILURE, SKIPPED
conv_result.errors    # list[ErrorItem]
conv_result.input     # InputDocument metadata
```

---

## PdfPipelineOptions

**Module:** `docling.datamodel.pipeline_options`
**Parent chain:** `PdfPipelineOptions` → `PaginatedPipelineOptions` → `ConvertPipelineOptions` → `PipelineOptions` → `BaseOptions`

### All Parameters (with defaults)

#### From PipelineOptions (base)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `document_timeout` | `float \| None` | `None` | Max processing time in seconds. Returns partial results on timeout. |
| `accelerator_options` | `AcceleratorOptions` | `AcceleratorOptions()` | GPU device selection, memory management. |
| `enable_remote_services` | `bool` | `False` | Allow external API calls (for API-based picture description). |
| `allow_external_plugins` | `bool` | `False` | Allow third-party plugins for OCR, layout, etc. |
| `artifacts_path` | `Path \| str \| None` | `None` | Local directory for pre-downloaded model weights. |

#### From ConvertPipelineOptions

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `do_picture_classification` | `bool` | `False` | Categorize images by type (photo, diagram, chart). |
| `do_picture_description` | `bool` | `False` | Generate text descriptions of pictures via VLM. |
| `picture_description_options` | `PictureDescriptionBaseOptions` | `smolvlm_picture_description` | VLM model config for picture descriptions. |

#### From PaginatedPipelineOptions

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `images_scale` | `float` | `1.0` | Scaling factor for generated images. |
| `generate_page_images` | `bool` | `False` | Generate PNG of each page. |
| `generate_picture_images` | `bool` | `False` | Extract embedded images as separate files. |

#### PdfPipelineOptions (own parameters)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| **`do_table_structure`** | `bool` | `True` | Enable TableFormer table structure extraction. |
| **`do_ocr`** | `bool` | **`True`** | Enable OCR. **Note: default is True, our current backend sets False.** |
| `do_code_enrichment` | `bool` | `False` | Code-aware OCR for code blocks. |
| **`do_formula_enrichment`** | `bool` | `False` | **Math formula → LaTeX conversion.** Key for math-heavy docs. |
| `force_backend_text` | `bool` | `False` | Use PDF's native text instead of layout model text. |
| **`table_structure_options`** | `BaseTableStructureOptions` | `TableStructureOptions()` | TableFormer config (mode, cell matching). |
| **`ocr_options`** | `OcrOptions` | `OcrAutoOptions()` | OCR engine config. |
| `layout_options` | `BaseLayoutOptions` | `LayoutOptions()` | Layout model config (Heron default). |
| `generate_table_images` | `bool` | `False` | **Deprecated.** Use `generate_page_images` + `TableItem.get_image()`. |
| `generate_parsed_pages` | `bool` | `False` | Keep intermediate parse structures (debug). |
| `ocr_batch_size` | `int` | `4` | Batch size for OCR stage (threaded pipeline). |
| `layout_batch_size` | `int` | `4` | Batch size for layout stage. |
| `table_batch_size` | `int` | `4` | Batch size for table structure stage. |
| `batch_polling_interval_seconds` | `float` | `0.5` | Polling interval for batch collection. |
| `queue_max_size` | `int` | `100` | Max queue size between pipeline stages. |

---

## TableStructureOptions

```python
TableStructureOptions(
    do_cell_matching: bool = True,   # Align detected cells with content
    mode: TableFormerMode = TableFormerMode.ACCURATE,  # "accurate" or "fast"
)
```

**TableFormerMode:**
- `FAST` — prioritizes speed
- `ACCURATE` — higher quality, slower (default, recommended for production)

---

## OCR Options

### OcrAutoOptions (default)

```python
OcrAutoOptions(
    lang: list[str] = [],  # auto-detect
    force_full_page_ocr: bool = False,
    bitmap_area_threshold: float = 0.05,  # 5% of page area
)
```

### Available OCR Engines

| Engine | Class | Key Config |
|--------|-------|------------|
| Auto | `OcrAutoOptions` | Auto-selects best available |
| EasyOCR | `EasyOcrOptions` | `lang=["en"]`, `use_gpu=None`, `confidence_threshold=0.5` |
| Tesseract CLI | `TesseractCliOcrOptions` | `lang=["eng"]`, `tesseract_cmd="tesseract"`, `psm=None` |
| Tesseract (Python) | `TesseractOcrOptions` | `lang=["eng"]`, `path=None`, `psm=None` |
| RapidOCR | `RapidOcrOptions` | `backend="onnxruntime"`, `text_score=0.5` |
| macOS Vision | `OcrMacOptions` | `recognition="accurate"`, `framework="vision"` |

**OCR behavior:** When `do_ocr=True` and `force_full_page_ocr=False` (default), OCR only runs on bitmap regions larger than `bitmap_area_threshold` (5% of page). For scanned/image-only PDFs, `force_full_page_ocr=True` may be needed.

---

## Layout Options

```python
LayoutOptions(
    create_orphan_clusters: bool = True,  # Group isolated text
    keep_empty_clusters: bool = False,
    skip_cell_assignment: bool = False,
    model_spec: LayoutModelConfig = DOCLING_LAYOUT_HERON,  # Default layout model
)
```

Available layout models: `DOCLING_LAYOUT_HERON` (default), `DOCLING_LAYOUT_HERON_101`, `DOCLING_LAYOUT_EGRET_MEDIUM`, `DOCLING_LAYOUT_EGRET_LARGE`, `DOCLING_LAYOUT_EGRET_XLARGE`, `DOCLING_LAYOUT_V2`.

---

## PdfBackend

```python
class PdfBackend(str, Enum):
    PYPDFIUM2 = "pypdfium2"
    DLPARSE_V1 = "dlparse_v1"
    DLPARSE_V2 = "dlparse_v2"
    DLPARSE_V4 = "dlparse_v4"  # default, latest
```

Default backend is `DoclingParseV4DocumentBackend` (DLPARSE_V4).

---

## DoclingDocument Export

The `ConversionResult.document` is a `DoclingDocument` with these export methods:

```python
doc = conv_result.document

# Markdown export
md_text = doc.export_to_markdown()

# Dictionary/JSON export
doc_dict = doc.export_to_dict()

# Iterate over elements
for item in doc.texts:      # TextItem instances
    ...
for item in doc.tables:     # TableItem instances
    ...
for item in doc.pictures:   # PictureItem instances
    ...
```

---

## FormatOption (connecting pipeline options to converter)

```python
from docling.document_converter import PdfFormatOption
from docling.datamodel.base_models import InputFormat

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=PdfPipelineOptions(...)
        ),
    }
)
```

---

## Key Findings for Experiments

1. **`do_ocr` defaults to `True`** — our current backend explicitly sets `False`. Testing OCR mode is just removing this override.

2. **`do_formula_enrichment`** — LaTeX conversion for math. This could address the math garbling issue. Must test.

3. **`page_range`** — 1-indexed `(start, end)` inclusive. Single-page extraction is `page_range=(N, N)`. This is the API for the pipeline's per-page extraction.

4. **`document_timeout`** — Built-in timeout support. Could replace our subprocess-based timeout for some use cases.

5. **`TableFormerMode.FAST` vs `ACCURATE`** — Speed/quality knob for table extraction.

6. **`force_full_page_ocr`** — May be needed for schulte_1978 if bitmap threshold doesn't trigger.

7. **Layout model options** — Multiple models available (Heron default, Egret variants for higher accuracy). Could test if different layout models improve heading detection.
