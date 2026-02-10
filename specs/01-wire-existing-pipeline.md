# Spec 01: Wire Existing Extraction Pipeline Into PDF Converter

## Priority: SECOND — This is the whole point

## Problem

The `doc_ingest` PDF converter (`converters/pdf_converter.py`) calls raw `pymupdf4llm.to_markdown()`. The existing extraction pipeline in `src/agentic_mbse/extraction/` has 4 layers of quality improvement that are simply not used. Real-world test results:

| Paper | Old Pipeline | New Pipeline | Gap |
|-------|-------------|-------------|-----|
| ARIES Cost Account | 137 tables | 0 tables | Total loss |
| Helios Design | 52 headings | 1 heading | 98% loss |
| Hawker 2020 | 11 headings | 14 headings | Slight improvement (pymupdf4llm header detector) |

## Approach: Incremental Layering

Wire in one layer at a time. Measure after each. Stop when quality matches or exceeds baseline.

### Step 1: Replace raw pymupdf4llm with pymupdf_backend.extract()

The existing backend (`pymupdf_backend.py`) already:
- Uses a custom `_academic_header_detector` for section numbering
- Emits `<!-- PAGE:N -->` markers for downstream processing
- Writes images to `images/` directory
- Calls `postprocess()` automatically

**Change**: `PyMuPDF4LLMConverter.convert()` should call `pymupdf_backend.extract()` and read back the resulting `full_document.md`.

**Expected improvement**: Headings should improve dramatically (postprocessing promotes bold headers, strips noise). Tables unchanged at this step.

**Measure**: Run test harness, compare.

### Step 2: Add GMFT table extraction (if available)

The existing `table_extraction.py` can be called on the postprocessed markdown + source PDF:
1. Run `quality_gates.detect_problems()` to find broken tables
2. If `gmft` is installed, run `table_extraction.enhance_tables()` on the repair requests
3. Splice repaired tables back into markdown

**Change**: After Layer 1 extraction, check for GMFT and run table enhancement.

**Expected improvement**: Table-heavy documents (ARIES, Hsu) should show dramatic improvement.

**Measure**: Run test harness, compare.

**Unknown**: Is `gmft` installed in this environment? If not, what's the install story? This needs to be checked empirically.

### Step 3: Claude structure repair (optional, flag-gated)

`claude_structure.py` uses Claude CLI to detect and repair heading structure. This is expensive (API calls) and requires the Claude CLI.

**Change**: Add `--enhance` flag to doc_ingest CLI that enables Layer 3.

**Expected improvement**: Documents with poor heading detection get better structure. But this is already partially handled by postprocessing.

**Decision needed**: Is this worth wiring in for the doc_ingest use case, or is it only needed for the `agentic-mbse extract` command? Measure the gap after Steps 1-2 first.

### Step 4: AI repair (optional, flag-gated)

`ai_repair.py` uses Claude to fix individual broken regions with cross-validation.

**Same question as Step 3**: Measure first, decide whether to wire in.

## Implementation Details

### PyMuPDF4LLMConverter changes

The converter currently does this:
```python
def convert(self, content: bytes) -> ConversionResult:
    # writes content to temp file, calls pymupdf4llm.to_markdown(), returns markdown
```

It should do this:
```python
def convert(self, content: bytes) -> ConversionResult:
    # 1. Write content to temp PDF file
    # 2. Call pymupdf_backend.extract(temp_pdf, temp_output_dir)
    # 3. Read back full_document.md
    # 4. Optionally run GMFT table enhancement
    # 5. Compute quality flags from the actual output
    # 6. Return ConversionResult with real quality flags
```

### Quality flags must be real

The current converter guesses at quality flags using regex heuristics. After wiring in the real pipeline:
- `has_tables` = quality_gates found table regions OR markdown has pipe tables
- `tables_likely_corrupted` = quality_gates found broken tables that weren't repaired
- `heading_structure_detected` = postprocessing promoted headers
- `has_math` = Unicode math symbols present (same heuristic, this is fine)

### Dependency management

`pymupdf_backend` imports from `agentic_mbse.extraction`. The `doc_ingest` package currently has no dependency on `agentic_mbse`. Options:
1. **Import directly**: `from agentic_mbse.extraction.pymupdf_backend import extract` — simplest, works since both are in the same repo
2. **Copy the functions**: Duplicate `pymupdf_backend.py` and `postprocess.py` into `doc_ingest` — avoid cross-package dependency but maintain two copies
3. **Extract shared library**: Move extraction utilities to a shared package — over-engineered for now

**Recommendation**: Option 1 (direct import). These packages are in the same repo and installed together. Cross-package imports are fine.

## Acceptance Criteria

After each step, run the test harness (Spec 00). Criteria per step:

### After Step 1 (backend + postprocess)
- [ ] Heading counts match or exceed baseline for all 5 papers
- [ ] No table regression (tables shouldn't get worse)
- [ ] Character counts within 5% of baseline

### After Step 2 (GMFT)
- [ ] Papers marked `has_tables=true` have table_row_count > 0
- [ ] ARIES Cost Account has >100 table rows (was 137 in baseline)
- [ ] Table content matches (spot-check: numbers in tables are correct)

### After Steps 3-4 (Claude layers, if pursued)
- [ ] Defined based on gap remaining after Steps 1-2

## What We Don't Know

- Whether `gmft` is installed or installable in this environment
- Whether direct imports from `agentic_mbse.extraction` cause circular dependency issues
- Whether `pymupdf_backend.extract()` works when called from a `bytes` input (it currently takes a `Path`) — we'll need to write to temp file first
- How much quality gap remains after Steps 1-2 without Claude layers
- Whether the page marker format from pymupdf_backend is compatible with quality_gates expectations in the doc_ingest context
