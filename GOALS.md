# Goals — Extracted Semantic Fidelity

We are building an end-to-end PDF-to-markdown pipeline that maximizes **extracted semantic fidelity** — the degree to which the output faithfully represents the source document's meaning and structure. Ground truth doesn't exist (if it did, we wouldn't need this). Goals stay qualitative because the IterationSpecAgent's job is to investigate the corpus and produce specific, measurable specs.

## Overarching Goal: Robust Generalization

The pipeline must work well on papers it has never seen. This is the most important property of the system. A fix that improves one paper but requires another fix for the next paper is not converging — it's accumulating maintenance burden.

**Think about it this way:** if someone drops 50 new PDFs from different publishers, journals, and decades into the corpus tomorrow, how many of them will extract well without code changes? That number is the real measure of pipeline quality. Every improvement should increase it.

This means:
- Fixes that leverage the extraction tools' built-in capabilities (library parameters, ML models, backend selection) are high-value because they generalize by design
- Fixes that add format-specific pattern matching (this publisher uses italic headers, that paper uses bold-allcaps) are low-value because each new format needs another pattern
- When the extraction layer already has the information needed (font size, weight, position) but produces bad output, the right fix is upstream — adjusting how the tool is called, not patching its output with string manipulation
- The codebase already contains multiple extraction backends, ML-based table detection, vision-based structure detection, and quality gates. Investigate what's available and underutilized before writing new code.

## Priority 1: Document Structure

Sections and headings must faithfully represent the PDF's logical hierarchy. A missed heading means a lost section boundary downstream. A phantom heading pollutes the structure.

- Numbered headings (1.1, 1.2.3) should preserve hierarchy
- Unnumbered headings (bold, all-caps, font-size changes) should be promoted to proper markdown headings
- Table of contents entries should NOT be promoted to headings
- No phantom headings — every heading in output should correspond to a real section in the PDF

The extraction tools (pymupdf4llm, Docling) have font metadata, layout analysis, and ML models that can identify headings. The question is whether we're using them well, not whether we can regex-match another formatting variant after the fact.

## Priority 2: Text Content Fidelity

Extracted text must be semantically faithful to the source. Equations, numeric values, units, and special characters are critical — errors here propagate directly to downstream reasoning.

- High-severity: values like "beta = 5.7" becoming "b = 5.7", or "10^6" becoming "106"
- High-severity: ligatures (fi, fl, ff) not resolved to component characters
- High-severity: unicode characters replaced with placeholders or dropped
- Low-severity: extra whitespace, formatting inconsistencies, minor stylistic differences

## Priority 3: Tables and Structured Data

Tables carry quantitative data (parameters, costs, specifications) that downstream consumers parse. Row/column structure must be preserved.

- Missing rows or scrambled columns corrupt data — these are high-severity
- Multi-page tables should be detected and merged where possible
- Table captions should be preserved and associated with their tables
- Complex layouts (merged cells, nested headers) should degrade gracefully

## Priority 4: Regression Safety

No change should degrade what already works. The corpus tests are the gate.

- All corpus tests must pass after every change
- Per-paper heading thresholds accommodate known limitations of text-based detection

## Lower Priority (don't optimize ahead of the above)

- **Image extraction** — currently reliable, but should not regress
- **Visual formatting** — bold/italic preservation is nice-to-have, not a fidelity concern
- **Whitespace and readability** — output shouldn't be junk, but extra blank lines and minor inconsistencies are not worth spending iterations on when higher-priority gaps remain