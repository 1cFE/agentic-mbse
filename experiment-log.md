# Experiment Log — extraction

## Goals
# Goals — Extracted Semantic Fidelity

We are building an end-to-end PDF-to-markdown pipeline that maximizes **extracted semantic fidelity** — the degree to which the output faithfully represents the source document's meaning and structure. Ground truth doesn't exist (if it did, we wouldn't need this). Goals stay qualitative because the IterationSpecAgent's job is to investigate the corpus and produce specific, measurable specs.

## Priority 1: Document Structure

Sections and headings must faithfully represent the PDF's logical hierarchy. A missed heading means a lost section boundary downstream. A phantom heading pollutes the structure. The mapping from PDF formatting (bold, font-size, numbering, all-caps) to markdown heading levels must be reliable across academic paper styles.

- Numbered headings (1.1, 1.2.3) should preserve hierarchy
- Unnumbered headings (bold, all-caps, font-size changes) should be promoted to proper markdown headings
- Table of contents entries should NOT be promoted to headings
- No phantom headings — every heading in output should correspond to a real section in the PDF

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


---

## Iteration 1 — 2026-02-10
**Brief:** # Iteration 2 Brief
**Specs:** add-energy-amplifier-to-corpus.md,broken-ligature-dictionary-repair.md,fix-plain-header-lookahead.md,promote-italic-numbered-headers.md
**Outcome:** PASS
**Key Learnings:**
- Key observations:
  - Energy amplifier paper (241 pages) successfully added with 667.9s extraction time
  - Broken ligature dictionary repair correctly preserves proper names while fixing standalone broken words
  - Plain header lookahead fix enables Section 4 and other single-newline headers to be promoted
  - Italic numbered header promotion successfully captures subsection headers in sparc_overview
  - Total corpus test time (762.89s) exceeds 5-minute mark but is acceptable given corpus now includes 7 papers with one 241-page document
  - All heading count metrics between baseline and current are identical, suggesting baselines were regenerated after fixes were applied
**Corpus:** hawker_2020, aries_cost_account, helios_design, hsu_2020, delene_2001, sparc_overview, energy_amplifier, 
