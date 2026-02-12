# Custom Header Detector Using Font Metadata

## Purpose
Replace pymupdf4llm's default font-size-only header detection with a custom `hdr_info` callback that uses font family, weight, italic flags, AND section-number patterns to classify headings — eliminating false positives from math symbols and false negatives from medium-weight/italic headings.

## Requirements
- Math symbols, display equations, and inline formulas must NOT be promoted to headings
- Numbered section headers (e.g., "4. SPARC scenarios") using medium-weight fonts must be detected as headings
- Bold numbered sections (e.g., "1. Introduction" in helios) must be detected as headings
- Italic numbered subsections (e.g., "3.1. Scoping studies" in helios) must be detected as headings
- The custom detector must be passed as `hdr_info` to `pymupdf4llm.to_markdown()`, replacing the default `IdentifyHeaders`
- The detector should generalize: it should work based on structural cues (numbering + font differentiation from body text), not paper-specific patterns

## Investigation Steps

### Learning test 1: Font metadata survey
Before implementing, the build agent must run this experiment to understand what font properties differentiate headers from body text across corpus papers:

```python
import pymupdf
from collections import Counter

for pdf_name in ['sparc_overview', 'helios_design', 'energy_amplifier', 'aries_cost_account', 'delene_2001']:
    doc = pymupdf.open(f"tests/corpus/pdfs/{pdf_name}.pdf")
    font_counter = Counter()
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" not in b:
                continue
            for l in b["lines"]:
                for s in l["spans"]:
                    text = s["text"].strip()
                    if not text:
                        continue
                    key = (s["font"], round(s["size"]), bool(s["flags"] & 16), bool(s["flags"] & 2))
                    font_counter[key] += len(text)
    print(f"\n{pdf_name}: top 10 font combos (font, size, bold, italic) -> char_count")
    for (font, size, bold, italic), count in font_counter.most_common(10):
        print(f"  {font}, {size}pt, bold={bold}, italic={italic}: {count} chars")
    doc.close()
```

This will reveal the body text font for each paper and show what distinguishes headers.

### Learning test 2: Candidate detector on sparc_overview
Write a candidate `hdr_info` callback and extract sparc_overview pages 0-5 to verify that:
- Section "1. Introduction" gets `## `
- Section "2. SPARC and the high-field path..." gets `## `
- Regular body text gets `""`
- The title "Overview of the SPARC tokamak" gets `# `

### Learning test 3: Candidate detector on energy_amplifier
Extract energy_amplifier pages 10-15 to verify that:
- Math symbols (∫, ∑, ρ) do NOT get heading prefixes
- Body text does NOT get heading prefixes
- Section headings DO get appropriate prefixes

### Design notes from investigation

The current `IdentifyHeaders` class in pymupdf4llm works by:
1. Scanning all pages for font sizes
2. Finding the most frequent font size = body text
3. Any font size > body_limit gets a heading level

This fails because:
- **sparc_overview**: body_limit=16 (inflated by large decorative text), section headers are only 10pt
- **energy_amplifier**: body_limit=12, so 13pt+ math symbols get H1-H6
- **helios_design**: body_limit=13, italic subsections at 10pt are invisible

The custom detector should use a multi-signal approach:
1. **Section number pattern** (`\d+\.?\s+[A-Z]` or `\d+\.\d+\.?\s+`) at span start — strong header signal regardless of font
2. **Font differentiation**: if the span's font family differs from the dominant body font AND the text is short (<120 chars) AND on a line by itself — likely a header
3. **Bold flag** (flags & 16) for bold section headers
4. **Italic flag** (flags & 2) combined with section numbering for italic subsections
5. **Reject math**: if the text contains math operators (∫∑∏∂√≈≠≤≥±×÷→←∞) it is NOT a header, regardless of font size
6. **Reject short fragments**: single-word spans under 4 characters that aren't section numbers are not headers

The depth mapping:
- Top-level numbered sections (1, 2, 3...) → `## ` (H2)
- Sub-sections (1.1, 2.3...) → `### ` (H3)
- Sub-sub-sections (1.1.1...) → `#### ` (H4)
- Title (detected by largest font size, first page only, or bold + long text) → `# ` (H1)

## Acceptance Criteria

### Quantitative targets (measured by `python3 tests/corpus/metrics.py`)
- **sparc_overview**: heading_count >= 10 (was 5; sections 1-6 + title = at minimum 7, plus subsections)
- **helios_design**: heading_count >= 20 (was 7; 7 main sections + ~15 italic subsections)
- **energy_amplifier**: H1 heading count <= 5 (was 64; eliminate math-as-header noise). Total heading_count should be between 30 and 80 (section + subsection headers without noise)
- **No regressions** on hawker_2020, aries_cost_account, hsu_2020, delene_2001 heading counts (must stay within -10% of current values)

### Structural quality
- No heading in any corpus paper should contain math operators (∫∑∏∂√≈≠≤≥±×÷→←∞•)
- No heading should be a table row (containing | or tab)
- All papers must still pass `test_heading_structure_present` (heading_count >= 3)

## Verification
```bash
# Run corpus tests (extracts all papers fresh)
uv run pytest tests/test_corpus.py --run-corpus -v

# Check sparc_overview headings
python3 tests/corpus/metrics.py tests/corpus/current/sparc_overview/full_document.md
# heading_count should be >= 10

# Check helios_design headings
python3 tests/corpus/metrics.py tests/corpus/current/helios_design/full_document.md
# heading_count should be >= 20

# Check energy_amplifier headings (noise reduction)
python3 tests/corpus/metrics.py tests/corpus/current/energy_amplifier/full_document.md
# heading_count should be 30-80, with H1 count <= 5

# Verify no math in headings
grep -P '^#{1,6} .*[∫∑∏∂√≈≠≤≥±×÷→←∞•]' tests/corpus/current/*/full_document.md
# Should return empty (no matches)

# Full test suite
uv run pytest tests/ -v
```

## Constraints
- The custom detector must be implemented in `src/agentic_mbse/extraction/pymupdf_backend.py`
- It must be passed as `hdr_info=` to `pymupdf4llm.to_markdown()`
- The existing `_academic_header_detector` function can be replaced/evolved (it's commented out anyway)
- Do NOT add publisher-specific patterns — the detector must work based on structural cues (numbering, font weight, font family)
- Existing postprocess functions (`promote_bold_headers`, `promote_plain_headers`, etc.) remain as safety nets — they should continue to work but the primary heading detection should happen in `hdr_info`
- Do NOT break existing unit tests in `tests/`
