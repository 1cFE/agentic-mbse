# GMFT API Reference (v0.4.x)

**Created:** 2026-02-22
**Source:** Installed package at `.venv/lib/python3.12/site-packages/gmft/`

---

## Overview: Detection → Formatting Pipeline

```
PyPDFium2Document → page → AutoTableDetector.extract(page) → list[CroppedTable]
                                                                    ↓
                              AutoTableFormatter.extract(table) → FormattedTable
                                                                    ↓
                                                    ft.df() → pd.DataFrame
                                                    ft.df().to_markdown() → str
                                                    ft.df().to_csv() → str
                                                    ft.df().to_html() → str
```

---

## PyPDFium2Document

**Module:** `gmft.pdf_bindings.pdfium`

```python
doc = PyPDFium2Document(filename: str)
page = doc.get_page(n: int)  # 0-indexed!
len(doc)                      # number of pages
doc.close()                   # MUST call when done
```

**Key notes:**
- Pages are **0-indexed** (same as PyMuPDF)
- User is responsible for calling `doc.close()` — no context manager
- Uses pypdfium2 internally, coordinates follow PIL convention (0,0 = top-left)

---

## AutoTableDetector (→ TATRDetector)

**Module:** `gmft.core.auto_lazy` → `gmft.detectors.tatr.TATRDetector`

`AutoTableDetector` is a factory that creates `TATRDetector`.

### Constructor

```python
detector = AutoTableDetector(config: TATRDetectorConfig = None)
```

### TATRDetectorConfig

```python
@dataclass
class TATRDetectorConfig:
    image_processor_path: str = "microsoft/table-transformer-detection"
    detector_path: str = "microsoft/table-transformer-detection"
    no_timm: bool = True
    warn_uninitialized_weights: bool = False
    torch_device: str = "cuda" if torch.cuda.is_available() else "cpu"
    detector_base_threshold: float = 0.9  # minimum confidence for table detection
```

**Key parameter:** `detector_base_threshold` (default 0.9) — confidence score required for a region to be classified as a table. Lower values detect more tables but increase false positives.

### extract() — Detect Tables

```python
tables: list[CroppedTable] = detector.extract(
    page: BasePage,
    config_overrides: TATRDetectorConfig = None,
)
```

Returns a list of `CroppedTable` objects. Each has:
- `.rect.bbox` — bounding box `(x0, y0, x1, y1)`
- `.confidence_score` — detection confidence
- `.label` — 0 = table, 1 = rotated table
- `.page` — reference to source page

Uses the Microsoft Table Transformer model at DPI=72 internally.

---

## AutoTableFormatter (→ TATRFormatter)

**Module:** `gmft.core.auto_lazy` → `gmft.formatters.tatr.TATRFormatter`

`AutoTableFormatter` is a factory that creates `TATRFormatter`.

### Constructor

```python
formatter = AutoTableFormatter(config: TATRFormatConfig = None)
```

### extract() / format() — Format a Detected Table

```python
formatted_table: FormattedTable = formatter.extract(
    table: CroppedTable,
    config_overrides: TATRFormatConfig = None,
)
# .format() is an alias for .extract()
```

---

## TATRFormatConfig

**Module:** `gmft.impl.tatr.config`

This is the main configuration class with many parameters. Key categories:

### Model Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `formatter_path` | `str` | `"microsoft/table-transformer-structure-recognition"` | HuggingFace model for structure |
| `torch_device` | `str` | `"auto"` | Device: "auto", "cpu", "cuda" |
| `verbosity` | `int` | `1` | 0=errors, 1=warnings, 2=info, 3=debug |

### Confidence Thresholds

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `formatter_base_threshold` | `float` | `0.3` | Base threshold for row/column features. **Low is better** — overzealous rows create empty rows (fixable), merged cells create data loss (unfixable). |
| `cell_required_confidence` | `dict` | See below | Per-feature-type confidence thresholds |

Default `cell_required_confidence`:
```python
{
    0: 0.3,   # table
    1: 0.3,   # column
    2: 0.3,   # row
    3: 0.3,   # column header
    4: 0.5,   # projected row header
    5: 0.5,   # spanning cell
    6: 99,    # no object (effectively disabled)
}
```

### DataFrame Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `remove_null_rows` | `bool` | `True` | Remove rows with no text |
| **`enable_multi_header`** | `bool` | `False` | Enable multi-indices in DataFrame. If false, multiple headers merged vertically. |
| **`semantic_spanning_cells`** | `bool` | `False` | [Experimental] Detect hierarchical multi-level indices from spanning cells. |
| `semantic_hierarchical_left_fill` | `"algorithm" \| "deep" \| None` | `"algorithm"` | How to handle left header groups when spanning cells enabled. |

### Large Table Handling

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `large_table_if_n_rows_removed` | `int` | `8` | N rows removed by NMS → classify as large table |
| `large_table_threshold` | `int` | `10` | Min rows for large table assumption |
| `large_table_row_overlap_threshold` | `float` | `0.2` | Min overlap fraction to trigger large table mode |
| `large_table_maximum_rows` | `int` | `1000` | Max rows before refusing to proceed (memory safety) |
| `force_large_table_assumption` | `bool \| None` | `None` | True=force, False=disable, None=heuristic |

### Rejection and Warnings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `total_overlap_reject_threshold` | `float` | `0.9` | Reject if overlap > 90% of table area |
| `total_overlap_warn_threshold` | `float` | `0.1` | Warn if overlap > 10% |
| `nms_warn_threshold` | `int` | `5` | Warn if NMS removes > 5 rows |
| `iob_reject_threshold` | `float` | `0.05` | Reject if IoB < 5% |
| `iob_warn_threshold` | `float` | `0.5` | Warn if IoB < 50% |

### Technical (Private)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `_nms_overlap_threshold` | `float` | `0.1` | NMS overlap threshold for row deduplication |
| `_large_table_merge_distance` | `float` | `0.6` | Merge distance for large table row estimation |
| `_smallest_supported_text_height` | `float` | `0.1` | Minimum text height (prevents huge arrays) |

---

## FormattedTable Output Methods

`FormattedTable` extends `CroppedTable`. Key methods:

```python
ft = formatter.extract(table)

# Get pandas DataFrame
df = ft.df(recalculate=False, config_overrides=None)

# Export via pandas
df.to_markdown()   # pipe table markdown
df.to_csv()        # CSV string
df.to_html()       # HTML table
df.to_latex()      # LaTeX table

# Recalculate with different config
df = ft.df(recalculate=True, config_overrides=TATRFormatConfig(enable_multi_header=True))

# Visualization
ft.visualize()  # renders detected structure overlay

# Serialization
d = ft.to_dict()
ft2 = TATRFormattedTable.from_dict(d, page)
```

**Note:** `df.to_markdown()` requires the `tabulate` package.

---

## Complete Usage Example

```python
from gmft.auto import AutoTableDetector, AutoTableFormatter, AutoFormatConfig
from gmft.pdf_bindings.pdfium import PyPDFium2Document

detector = AutoTableDetector()
formatter = AutoTableFormatter()

doc = PyPDFium2Document("paper.pdf")
try:
    for page_idx in range(len(doc)):
        page = doc.get_page(page_idx)
        tables = detector.extract(page)
        for table in tables:
            ft = formatter.extract(table)
            df = ft.df()
            print(f"Page {page_idx}, table: {df.shape}")
            print(df.to_markdown())
finally:
    doc.close()
```

---

## Key Findings for Experiments

1. **`enable_multi_header=True`** — Critical for documents with multi-row headers (aries_cost_account, helios_design). Default merges headers vertically.

2. **`semantic_spanning_cells=True`** — Experimental but could help with merged cells that pymupdf4llm shows as `<br>` artifacts.

3. **`detector_base_threshold=0.9`** — Very conservative. May miss tables in low-contrast documents. Worth testing lower values (0.7, 0.8).

4. **Output is DataFrame** — Export to markdown via `df.to_markdown()` (requires tabulate). This means GMFT tables are always pipe-formatted, never HTML artifacts.

5. **Large table handling** — Built-in heuristics for tables with many rows. energy_amplifier's large tables might trigger this.

6. **No full-document extraction** — GMFT only extracts tables. For full-document comparison, GMFT tables would need to be merged with pymupdf4llm text.

7. **0-indexed pages** — Same as PyMuPDF, no offset issues.
