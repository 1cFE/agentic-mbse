# Profile Corpus

Curated set of diverse PDFs for benchmarking the extraction pipeline with `--profile`.

## Usage

```bash
# Dry-run profiling (no Claude spend, fast):
uv run agentic-mbse extract profile_corpus/ --profile --budget 0 --dry-run

# Full profiling with Claude enhancement:
uv run agentic-mbse extract profile_corpus/ --profile --budget 2
```

## Size Policy

- Maximum 5 MB per PDF file
- Files are symlinks to `tests/corpus/pdfs/` to avoid duplication
- If a slot requires a larger document, replace the symlink with a truncated copy

## Specimens

| # | File | Type | Pages | Size | Source | Notes |
|---|------|------|-------|------|--------|-------|
| 01 | `01_clean_born_digital.pdf` | Clean born-digital | 25 | 0.4 MB | woodruff_2026 | Modern paper, clean text, few tables |
| 02 | `02_two_column_academic.pdf` | Two-column academic | 14 | 1.2 MB | hawker_2020 | Royal Society, two-column, 21 display equations, 3 tables |
| 03 | `03_scanned_degraded.pdf` | Scanned/degraded | 10 | 0.2 MB | schulte_1978 | 1978 document, potential OCR artifacts |
| 04 | `04_table_heavy.pdf` | Table-heavy | 9 | 1.6 MB | hsu_2020 | 3 tables with 50 data rows in 9 pages |
| 05 | `05_equation_heavy.pdf` | Equation-heavy | 24 | 1.4 MB | paischer_2025 | NeurIPS paper, 23 display equations + inline math |
| 06 | `06_short_document.pdf` | Short document | 16 | 1.4 MB | tajima | Shorter technical paper |
| 07 | `07_long_document.pdf` | Long document | 50 | 0.8 MB | araiinejad_2024 | 50-page paper, diverse content |
| 08 | `08_mixed_content.pdf` | Mixed content | 28 | 4.8 MB | hansen_2025 | APS physics: figures, tables, inline math |
| 09 | `09_technical_report.pdf` | Report/technical | 39 | 0.3 MB | delene_2001 | 11 tables, 128 data rows, report format |
| 10 | `10_overview_document.pdf` | Overview/presentation | 25 | 1.9 MB | sparc_overview | Technical overview with figures |
