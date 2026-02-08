---
date: 2026-02-06T22:00:00-06:00
researcher: Claude
topic: "PDF Extraction v2 Phase 2 — Layer 2+3 Implementation Status & Learnings"
tags: [status, pdf-extraction, gmft, ai-repair, cross-validation]
status: complete
last_updated: 2026-02-06
---

# PDF Extraction v2 Phase 2 — Layer 2+3 Status & Learnings

## Summary

Phase 2 implements the remaining layers of the three-layer extraction pipeline described in `.project/concepts/pdf-extraction-v2.md`:

- **Layer 1 refinement:** Header noise rejection heuristic added to `postprocess.py`
- **Layer 2:** GMFT-based table extraction module (`table_extraction.py`)
- **Layer 3:** AI repair with cross-validation (`ai_repair.py`)
- **Quality gates:** Problem detection module (`quality_gates.py`) that identifies broken tables and garbled equations between layers
- **CLI integration:** `--enhance`, `--no-tables`, `--max-repair-pages` flags wired into `agentic-mbse extract`

All code is tested (36 new tests, 763 total passing) and linted clean.

## What Was Built

### New Modules

| Module | Purpose | Tests |
|--------|---------|-------|
| `extraction/quality_gates.py` | Detect broken tables and garbled equations in post-processed markdown | 9 tests |
| `extraction/table_extraction.py` | GMFT-based table extraction (optional dependency) | 9 tests |
| `extraction/ai_repair.py` | AI repair via `claude -p` with cross-validation | 18 tests |

### Modified Files

| File | Changes |
|------|---------|
| `extraction/postprocess.py` | Added `reject_noise_headers()` — demotes noise headers (math, table rows, page artifacts) |
| `extraction/base.py` | Added `RepairRequest` dataclass for inter-layer communication |
| `cli/extract_cli.py` | Added `--enhance`, `--no-tables`, `--max-repair-pages` flags; wired Layer 2+3 pipeline |
| `pyproject.toml` | Added `extract-tables = ["gmft>=0.3"]` optional dependency group |

### Test Coverage

| Test File | Tests Added | All Pass |
|-----------|------------|----------|
| `test_postprocess.py` | 10 (noise headers) | Yes (67 total) |
| `test_quality_gates.py` | 9 (new file) | Yes |
| `test_table_extraction.py` | 9 (new file) | Yes (6 skipped: no pandas) |
| `test_ai_repair.py` | 18 (new file) | Yes |

## Header Noise Rejection Results

The `reject_noise_headers()` function demotes `## ` headers back to plain text when they:
- Contain math operators: `=`, `+`, `[`, `]`, `{`, `}`
- Look like table rows (contain `|` or tab characters)
- Are just a number + short word under 4 chars (page artifacts)
- Have title text under 4 characters after stripping the section number

**Expected impact on corpus:**
- **2238 (Lampe & Manheimer):** Should fix ~31 of 46 noise headers (equation fragment artifacts from scanned math paper)
- **2233 (Araiinejad):** Should fix cost table rows incorrectly promoted to headers
- **2236 (FAS Market Report):** Should reduce page-number-prefixed fake headers

## Layer 2 (GMFT) Design

GMFT integration follows the concept doc's optional import pattern:

```python
try:
    from agentic_mbse.extraction.table_extraction import enhance_tables
    md_text, remaining = enhance_tables(md_text, pdf_path, table_requests)
except ImportError:
    remaining = table_requests  # GMFT not installed, pass all to Layer 3
```

Key design decisions:
- GMFT is imported lazily — no import-time cost when not installed
- Uses `PyPDFium2Document` for page rendering (GMFT's recommended binding)
- Falls back gracefully: empty DataFrames, GMFT exceptions, and missing GMFT all result in requests passing through to Layer 3
- Page number estimation via heuristic (60 lines/page) when quality gates can't determine exact page

## Layer 3 (AI Repair) Design

### Cross-Validation Safety Mechanism

The critical safety feature from the concept doc is implemented:

1. `extract_numbers()` — Extracts all numeric tokens (integers, decimals, scientific notation, negatives) and normalizes to canonical form
2. `cross_validate_numbers()` — Compares number sets between original and repaired text. Accepts only if all original numbers appear in repair. Extra numbers are fine (repair found more)
3. On rejection: keeps Layer 1/2 output, inserts `<!-- AI repair flagged ... -->` comment, reports in metadata

### Repair Prompts

Three prompt templates tuned for each region type:
- **Table:** "Fix as pipe table, preserve all numbers exactly as in PDF"
- **Equation:** "Convert to LaTeX with $$ delimiters"
- **Structure:** "Identify correct heading structure"

## CLI Integration

New flags:
- `--enhance` — Enable Layer 3 AI repair (opt-in, requires `claude` CLI)
- `--no-tables` — Skip GMFT table extraction
- `--max-repair-pages N` — Limit Layer 3 to N regions

Pipeline execution order in `cmd_extract`:
1. Extraction (pymupdf/docling/pandoc)
2. Post-processing (Layer 1, including noise rejection)
3. Quality detection (finds broken tables + garbled equations)
4. GMFT table enhancement (Layer 2, unless `--no-tables`)
5. AI repair (Layer 3, only with `--enhance`)
6. Write back modified markdown
7. Index generation (if `--index`)

## Learnings

1. **getattr with defaults for CLI args:** Existing tests use `MockArgs` that don't include new flags. Using `getattr(args, "no_tables", False)` instead of `args.no_tables` maintains backward compatibility without modifying every test fixture.

2. **Noise header heuristic tuning:** Initial implementation rejected headers under 8 characters, which caught legitimate short headers like `## 1 Title` (7 chars). Final heuristic strips the section number prefix first, then checks if the remaining title text is under 4 characters.

3. **Optional dependency testing:** Tests for GMFT use `pytest.importorskip("pandas")` for DataFrame tests and monkeypatching `builtins.__import__` for availability checks. GMFT-dependent tests are skipped when pandas isn't installed, not failed.

4. **Cross-validation is conservative by design:** Missing numbers → reject. Extra numbers → accept. This matches the concept doc's "wrong numbers are worse than garbled text" principle.

## Remaining Issues

1. **GMFT not yet tested on real PDFs:** The GMFT integration is complete and tested with mocks, but hasn't been run against the 7-doc corpus (requires `gmft` installation with its ~270MB models)
2. **Page number estimation:** Quality gates don't track which PDF page a markdown region came from. The heuristic (60 lines/page) is rough. A more precise approach would need page break markers from the extraction backend.
3. **Equation OCR:** Layer 3 handles equations via `claude -p` vision, but dedicated equation OCR (UniMERNet/Surya) remains deferred to v3
4. **Multi-page table stitching:** Tables spanning page breaks still need cross-page context beyond what any single layer provides
5. **Benchmark against corpus:** Need to install GMFT and run full benchmark to get actual quality scores for the updated score table
