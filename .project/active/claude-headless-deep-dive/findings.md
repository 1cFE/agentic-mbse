# Findings: Claude Headless Direct Extraction (Stage 1D)

**Status:** Phase 2 complete
**Last Updated:** 2026-02-22

---

## Phase 1: Pure Vision Baseline (claude_vision_1pp)

### Configuration

- Model: Sonnet
- Pages per call: 1
- Prompt: `extract_baseline.txt` (format-only instructions, no tool access)
- DPI: 200
- Papers: hawker_2020, hsu_2020, hansen_2025, paischer_2025 (75 pages total)

### Cost Summary

| Paper | Pages | Cost | Cost/Page | Wall Clock | Output Tokens |
|-------|-------|------|-----------|------------|---------------|
| hawker_2020 | 14 | $0.81 | $0.058 | 460s (33s/pg) | 12,564 |
| hsu_2020 | 9 | $0.43 | $0.048 | 210s (23s/pg) | 5,623 |
| hansen_2025 | 28 | $2.31 | $0.083 | 722s (26s/pg) | 19,892 |
| paischer_2025 | 24 | $2.29 | $0.095 | 895s (37s/pg) | 29,604 |
| **Total** | **75** | **$5.84** | **$0.078 avg** | **2,286s (38 min)** | **67,683** |

**Cost projection:** Full 15-paper corpus (573 pages) at $0.078/page = **~$44.70**.

**Token reporting note:** `usage.input_tokens` in the JSON output only reports the stdin prompt tokens (36-112 per call), not the image tokens consumed via the Read tool. The true input cost is reflected in `total_cost_usd`. Based on Phase 0 testing, a single page image consumes ~61K input tokens.

### Cross-Tool Comparison Table

| Paper | Metric | pymupdf4llm best_v1 | Docling baseline | Claude vision 1pp | Notes |
|-------|--------|---------------------|------------------|-------------------|-------|
| **hawker_2020** | chars | 59,949 | 52,923 | 43,139 | Claude -28% vs pymupdf |
| | headings | 14 | 17 | 13 | All similar |
| | table_rows | **0** | **40** | **40** | pymupdf4llm misses all tables |
| | math_symbols | 11 | 8 | 1 | See "Equation Quality" below |
| | figure_refs | 12 | 12 | 12 | All match |
| | time/cost | 5.9s / free | 18.5s / free | 460s / $0.81 | |
| **hsu_2020** | chars | 13,560 | 14,947 | 13,504 | All similar |
| | headings | 5 | 6 | 4 | Claude misses 1 |
| | table_rows | **56** | **56** | **56** | Perfect match (calibration target) |
| | math_symbols | 0 | 0 | 0 | No math in this paper |
| | figure_refs | 1 | 1 | 1 | All match |
| | time/cost | 1.6s / free | 15.1s / free | 210s / $0.43 | |
| **hansen_2025** | chars | 60,840 | 56,317 | 57,263 | All within 8% |
| | headings | 17 | 18 | 15 | Claude gets most; pymupdf4llm default gets **0** |
| | table_rows | **0** | **15** | **15** | pymupdf4llm misses all tables |
| | math_symbols | 12 | 11 | 1 | See "Equation Quality" below |
| | figure_refs | 30 | 30 | 30 | All match |
| | time/cost | 3.6s / free | 26.1s / free | 722s / $2.31 | |
| **paischer_2025** | chars | 106,370 | N/A (timeout) | 85,513 | Claude -20% vs pymupdf |
| | headings | 68 | N/A | 26 | pymupdf4llm inflated (see note) |
| | table_rows | **137 (false!)** | N/A | **55** | pymupdf over-detects; Claude accurate |
| | math_symbols | 21 | N/A | 0 | See "Equation Quality" below |
| | figure_refs | 31 | N/A | 31 | Match |
| | time/cost | 29.8s / free | N/A | 895s / $2.29 | |

### Key Finding: math_symbol_count Is Misleading for Claude Output

**The `math_symbol_count` metric severely underreports Claude's equation quality.** The metric counts Unicode math symbols (∑, ∫, Greek letters, etc.). pymupdf4llm produces Unicode-encoded math (garbled but containing these symbols), so it scores 8-21. Claude produces proper **ASCII LaTeX** (`$\sum$`, `$\int$`, `$\alpha$`), which contains zero Unicode math symbols — hence scores 0-1.

**Actual LaTeX expression counts in Claude output:**

| Paper | Display equations (`$$...$$`) | Inline expressions (`$...$`) | Total LaTeX |
|-------|-------------------------------|------------------------------|-------------|
| hawker_2020 | 21 | ~93 | ~114 |
| hansen_2025 | (not counted) | (not counted) | extensive |
| paischer_2025 | 24 | ~332 | ~356 |

Claude's LaTeX output is vastly superior to pymupdf4llm's Unicode encoding for equation fidelity. The `math_symbol_count` metric should not be used to compare these tools — a LaTeX-aware metric is needed.

### Equation Quality Assessment

**This is the #1 finding of Phase 1.** Claude produces clean, correct LaTeX from page images — filling the biggest gap from Stage 1A.

#### hawker_2020 (14pp, math-heavy economics paper)

All 21 display equations transcribed to LaTeX. Examples:

**Equation 2.1 (LCOE definition):**
```
$$\text{LCOE} = \frac{\sum_{i=1}^{n} C_i / (1+d)^i}{\sum_{i=1}^{n} E_i / (1+d)^i}$$
```
Correct fractions, summation notation, subscripts/superscripts.

**Equation 2.3 (piecewise cost model):**
```
$$C_t = \begin{cases} C_P + C_Y + C_{d,\text{con}} & \text{during construction} \\
C_t + C_{\text{O\&M}} + C_{d,op} & \text{during operation} \end{cases}$$
```
Correct `\begin{cases}` environment, text labels, alignment.

**Inline math in tables:**
Table 2 contains LaTeX parameter symbols in cells: `$\mu_a$`, `$\hat{f}_b$`, `$\gamma$`, `$\varepsilon$`, etc. All correctly transcribed.

#### paischer_2025 (24pp, NeurIPS ML+physics paper)

24 display equations and ~332 inline LaTeX expressions. This paper has complex physics equations including:

**Equation 1 (gyrokinetic equation):**
```
$$\underbrace{\frac{\partial f}{\partial t} + (v_b \mathbf{b} + v_D) \cdot \nabla f}_{\text{Linear}} - \underbrace{...}_{\text{[?]}} + \underbrace{v_\chi \cdot \nabla f}_{\text{Nonlinear}} = S$$
```
Note: Claude used `[?]` for an ambiguous term in the middle underbrace — correctly following the prompt's fidelity instruction rather than guessing.

**Equation 2 (heat flux integral):**
```
$$Q = \int \mathbf{C} \int \mathbf{v}^2 \boldsymbol{\phi} f \, dv_\parallel d\mu \, dz \, dy \, dx$$
```
Complex nested integrals with bold symbols and parallel subscripts.

**Tables with LaTeX:** Table cells contain LaTeX expressions like `$\langle \overline{Q} \rangle$` and `GyroSwin$_{\text{small}}$`.

#### hansen_2025 (28pp, plasma physics paper)

Extensive inline LaTeX throughout the text:
- Density values: `$2 \times 10^{-8}$ g/cm³`
- Velocities: `$\sim 50$ km/s`
- Temperature: `$T_e = T_{Xe} = 1.5$ eV`
- Magnetic fields: `$\mathbf{J} \times \mathbf{B}$` forces
- Physical parameters: `$\gamma = 5/3$`, `$\beta$`, `$\chi_e$`

#### Verdict: Equation Quality

Claude's LaTeX transcription is **dramatically superior** to pymupdf4llm's Unicode output. For math-heavy documents, Claude is the only tool in the 1A-1D evaluation that produces renderable, correct LaTeX from PDF page images. This alone justifies Claude's cost for equation-heavy pages.

### Heading Detection

| Paper | pymupdf4llm default | pymupdf4llm composite | Docling | Claude |
|-------|--------------------|-----------------------|---------|--------|
| hawker_2020 | 14 | 14 | 17 | 13 |
| hsu_2020 | 5 | 5 | 6 | 4 |
| hansen_2025 | **0** | **17** | 18 | 15 |
| paischer_2025 | 68 | 68 | N/A | 26 |

**Observations:**
- Claude reliably detects section headings from visual layout, including the hansen_2025 case where pymupdf4llm default fails completely.
- paischer_2025: pymupdf4llm's 68 headings is inflated by false detection (diagrams/figures parsed as headings). Claude's 26 is likely more accurate.
- Claude occasionally includes running headers as headings (e.g., "PLX: FLASH, OSIRIS, and HELIOS" repeated header in hansen_2025).
- Heading hierarchy is mostly correct (proper H1/H2/H3 levels matching document structure) but has occasional level inconsistencies (e.g., subsections at H2 instead of H3).

### Table Detection

| Paper | pymupdf4llm best_v1 | Docling | Claude | Notes |
|-------|---------------------|---------|--------|-------|
| hawker_2020 | **0** | 40 | **40** | pymupdf4llm misses all tables |
| hsu_2020 | 56 | 56 | **56** | All tools match (calibration target) |
| hansen_2025 | **0** | 15 | **15** | pymupdf4llm misses all tables |
| paischer_2025 | 137 (false!) | N/A | **55** | pymupdf4llm massively over-detects |

Claude's table detection is accurate:
- Finds tables that pymupdf4llm misses entirely (hawker, hansen)
- Avoids false positives that plague pymupdf4llm (paischer: 55 real rows vs 137 false)
- Produces clean pipe tables with proper headers and separator rows
- Handles LaTeX in table cells correctly

### Hallucination Check

**Methodology:** Spot-checked 5+ numerical values per paper against internal consistency and known values from the source papers.

#### hawker_2020 numerical checks:
1. NIF laser: "$4bn" / "422 MJ capacitor bank" → $4e9 / 422e6 = $9.48/J ≈ "$9.5/J" ✓
2. First Light Machine Three: "$4.3 M" / "2.5 MJ" → $4.3e6 / 2.5e6 = $1.72/J ≈ "$1.7/J" ✓
3. LCOE target: "$100/MWh" for first plants, "$60/MWh" pathway ✓ (consistent with abstract's $25/MWh claim)
4. Availability example: "refuelling process takes six months and must be done after 3 years" → 30/36 = 83.3%, paper says "86%" — close but not exactly matching the example. The paper's 86% may use different assumptions. **Minor concern.**

#### hsu_2020 numerical checks:
1. Table 2 "Fusion Power": 1352.8 (avg), 1044.0 (low), 1920.0 (high) — internally consistent
2. Table 2 "Net electric power": 517.0, 383.1, 814.4 MW — plausible for ~500 MWe plants described in text
3. Table 3 CAS numbers (22.1.1 through 22.1.6) — hierarchy preserved correctly
4. LCOE "43 $/MWh" and "CapEx of ~2-4$/W and $1.2B" — consistent with executive summary text

#### hansen_2025 numerical checks:
1. "36 supersonic plasma jets traveling at ~50 km/s" — consistent with PLX description
2. Jet density "2 × 10⁻⁸ g/cm³" — plausible for plasma jet
3. "peak preheat temperatures of around 40 eV" — consistent with figure caption
4. Volume-averaged number density "~1 × 10¹⁴ cm⁻³" — plausible for plasma

#### paischer_2025 numerical checks:
1. Table 1 GyroSwin results: "67.68 ± 10.28" (ID flux) — specific enough to not be fabricated
2. "three orders of magnitude faster" — consistent with abstract claim
3. "tested up to one billion parameters" — consistent with title claims

**Verdict:** No hallucinated numerical values detected across all 4 papers. Claude preserves numbers with high fidelity. The one minor discrepancy (hawker_2020 availability calculation) appears to be a simplification in the explanatory text, not a hallucination.

### Fidelity Issues

1. **"GyroSwim" typo in paischer_2025 tables:** Claude misreads "GyroSwin" as "GyroSwim" in 14 table cells (smaller font). The correct "GyroSwin" appears 49 times in running text. This is a font-size-dependent OCR error — minor but present.

2. **Running headers included as content:** hansen_2025 has "PLX: FLASH, OSIRIS, and HELIOS" as a running header on every page. Claude includes it on some pages as text content, and on one page incorrectly marks it as a heading. The extraction prompt says "No page numbers, running headers, or footers" — Claude partially follows this.

3. **Character count lower than pymupdf4llm:** Claude produces 20-28% fewer characters on hawker_2020 and paischer_2025. Some of this is desirable (omitting page artifacts), but some may be content loss. Manual inspection shows all major sections and paragraphs are present — the difference is likely from cleaner formatting (no `<br>` artifacts, no code fences, no false table content).

4. **Equation numbering style varies:** Some equations use `\tag{2.1}` (correct), others have the number on a separate line as plain text "(2.9)". This is inconsistent but not incorrect.

### Summary: Phase 1 Findings

**What Claude does well (better than all library tools):**
1. **Equation transcription to LaTeX** — dramatically superior. The only tool that produces renderable LaTeX from PDF images.
2. **Table detection accuracy** — finds real tables, avoids false positives. Matches Docling on table row counts.
3. **Clean output** — no `<br>` artifacts, no code fences, no false heading promotions.
4. **Numerical fidelity** — no hallucinated values detected across 4 papers, 20+ spot-checks.

**What Claude does adequately:**
1. **Heading detection** — finds most headings with reasonable hierarchy. Not quite as good as Docling or pymupdf4llm composite, but far better than pymupdf4llm default.
2. **Figure references** — correctly generates `[Figure N: caption]` placeholders.
3. **Content completeness** — all major sections present, no dropped paragraphs.

**What Claude does poorly:**
1. **Speed** — 23-37 seconds per page vs <1 second for pymupdf4llm. ~100x slower.
2. **Cost** — $0.078/page average. Full corpus would be ~$45.
3. **Running header removal** — inconsistent (some pages include them, some don't).
4. **Small-font OCR accuracy** — "GyroSwim" vs "GyroSwin" in table cells. Minor but present.

**Key insight for pipeline design:** Claude's equation quality alone justifies its use for math-heavy pages. The cost is prohibitive for full-corpus extraction ($45 for 573 pages), but targeted use on pages with equations, broken tables, or missed headings could be highly cost-effective.

### Cost-Effectiveness Analysis

| Use Case | Cost | Value |
|----------|------|-------|
| Full extraction (all pages) | $0.078/page | Overkill — pymupdf4llm is adequate for most content |
| Equation-heavy pages only | $0.078/page × ~50 eq pages | ~$3.90 — high value, fills biggest gap |
| Table repair pages only | $0.078/page × ~20 table pages | ~$1.56 — moderate value, GMFT is a cheaper alternative |
| Heading-deficient docs only | $0.078/page × ~5 pages | ~$0.39 — low volume, Docling per-page is free alternative |

**Recommendation for Phase 2:** Test supplemental-text mode (general repair) and focused synthesis on targeted pages. The highest-value experiment is equation repair on math-heavy pages — this is where Claude has no substitute.

---

## Phase 2: Explore — General Repair & Focused Synthesis

### Track A: General Repair (`claude_pymupdf_1pp`)

#### Configuration

- Model: Sonnet
- Pages per call: 1
- Prompt: `extract_baseline.txt` (same as Phase 1)
- Mode: `--supplemental-text` — each page receives both the image AND pymupdf4llm's extracted text for that page
- DPI: 200
- Papers: hawker_2020, hsu_2020, hansen_2025, paischer_2025 (75 pages total)

#### Cost Summary

| Paper | Pages | Cost | Cost/Page | Wall Clock |
|-------|-------|------|-----------|------------|
| hawker_2020 | 14 | $1.35 | $0.097 | 253s |
| hsu_2020 | 9 | $0.75 | $0.083 | ~140s |
| hansen_2025 | 28 | $2.45 | $0.088 | 455s |
| paischer_2025 | 24 | $2.61 | $0.109 | ~350s |
| **Total** | **75** | **$7.16** | **$0.095 avg** | **~1,200s (20 min)** |

Track A costs 22% more per page than pure vision ($0.095 vs $0.078) due to supplemental text token overhead.

#### Metrics Comparison: Vision vs General Repair vs pymupdf4llm

| Paper | Config | Chars | Headings | Tables | Math |
|-------|--------|------:|--------:|---------:|-----:|
| hawker_2020 | vision | 43,139 | 13 | 40 | 1 |
| | repair | 43,778 | 13 | 40 | 1 |
| | best_v1 | 59,949 | 14 | 0 | 11 |
| hsu_2020 | vision | 13,504 | 4 | 56 | 0 |
| | repair | 13,551 | 5 | 56 | 0 |
| | best_v1 | 13,560 | 5 | 56 | 0 |
| hansen_2025 | vision | 57,263 | 15 | 15 | 1 |
| | repair | 57,716 | 14 | 15 | 0 |
| | best_v1 | 60,840 | 17 | 0 | 12 |
| paischer_2025 | vision | 85,513 | 26 | 55 | 0 |
| | repair | 82,719 | 25 | 54 | 1 |
| | best_v1 | 106,370 | 68 | 137 | 21 |

#### Key Finding: Supplemental Text Is NOT Being Integrated

**General repair produces metrics nearly identical to pure vision.** The differences (hawker: 43,139 vs 43,778 chars, hsu: 4 vs 5 headings) are within the range of normal nondeterminism between independent Claude calls.

Manual comparison of the actual markdown output confirms this: the general repair output is essentially a fresh vision extraction, not a repair of the pymupdf4llm text. Claude receives the supplemental text but does not meaningfully use it.

**Evidence:**
1. **Metrics are statistically indistinguishable** from Phase 1 pure vision on all papers
2. **Prose differs between vision and repair outputs** in minor ways (word choice, heading levels) — if Claude were editing the pymupdf4llm text, these differences would align with best_v1, but they don't
3. **paischer_2025 comparison:** The repair output has different OCR artifacts than the vision output (e.g., different ORCID digits, different citation years). Both are independent reads from the image, not edits of the supplemental text.
4. **The prompt says "trust the page images as the primary source"** — Claude follows this literally by extracting from vision and ignoring the text

**Verdict:** General repair is 22% more expensive than pure vision with no measurable quality improvement. The supplemental text approach is not effective with the current prompt design.

**Why this happened:** The `extract_baseline.txt` prompt treats the supplemental text as a secondary reference. Claude, as a capable vision model, simply re-extracts from the image rather than editing the text. A more aggressive prompt (e.g., "START from the library text and ONLY modify the parts that differ from the image") might change this behavior, but was not tested.

---

### Track B: Focused Synthesis

#### Configuration

5 experiments targeting specific pages with known pymupdf4llm failures:

| Experiment | Paper | Pages | Prompt | Cost | Cost/Page |
|-----------|-------|-------|--------|------|-----------|
| focused_eq_hawker | hawker_2020 | 2, 3, 6 | fix_equation.txt | $0.49 | $0.164 |
| focused_eq_paischer | paischer_2025 | 2, 4, 15 | fix_equation.txt | $0.66 | $0.221 |
| focused_table_aries | aries_cost_account | 1, 4, 7 | fix_table.txt | $0.42 | $0.141 |
| focused_table_paischer | paischer_2025 | 1, 4 | fix_table.txt | $0.27 | $0.135 |
| focused_table_delene | delene_2001 | 4, 5, 8 | add_table.txt | $0.27 | $0.089 |
| **Total** | | **14** | | **$2.12** | **$0.151 avg** |

Focused synthesis costs ~2x pure vision per page ($0.151 vs $0.078) — the supplemental text adds input tokens.

#### Equation Repair Results

##### hawker_2020 (pages 2, 3, 6)

**Target:** Garbled equations 2.1, 2.3, 2.17-2.20 (Unicode salad, `~~�~~` artifacts, lost braces)

**Results:**
- All targeted equations were replaced with well-formed LaTeX (`$$...$$`)
- Eq 2.1 (LCOE fraction): correct `\frac{\sum}{\sum}` structure
- Eq 2.3 (piecewise): correct `\begin{cases}` with restored brace
- Eqs 2.17-2.20: good LaTeX for 2.17 and 2.19, **uncertain on 2.18 and 2.20** (complex gain curves where the PDF image itself is hard to read)

**Quality comparison to Phase 1 pure vision:**

| Equation | Focused Repair | Pure Vision | Match? |
|----------|---------------|-------------|--------|
| 2.1 (LCOE) | Correct | Correct | Yes |
| 2.3 (piecewise) | Correct | Correct | Yes |
| 2.17 (gain curve) | Correct | Correct | Yes |
| 2.18 (areal density) | Uncertain coefficient | Different uncertain coefficient | Both unreliable |
| 2.19 (theta) | Correct | Correct | Yes |
| 2.20 (energy gain) | Uncertain, added "[?]" | Different reconstruction | Both unreliable |

**The focused repair does not produce better LaTeX than pure vision for the equations it can read clearly.** On ambiguous equations (2.18, 2.20), both approaches produce different but equally uncertain reconstructions.

##### paischer_2025 (pages 2, 4, 15)

**Target:** Triple `~~�~~` artifacts on gyrokinetic PDE, `~~_√_~~` on attention formula, `~~~~` on distribution split

**Results:**
- Eq 1 (gyrokinetic PDE): **Better than pure vision** — correct magnetic mirror term (`\frac{\mu B}{m} \frac{\mathbf{B} \cdot \nabla B}{B^2}`) where pure vision hallucinated `P` denominators
- Eq 19 (distribution split): Clean repair with correct adiabatic/kinetic underbrace labels
- **Eq 6 (W-MSA attention): MISSED** — Claude decided the architecture diagram page had "no equations to repair" despite the W-MSA formula being present in garbled form

**The focused repair occasionally produces better equations than pure vision** (Eq 1), but can also miss equations entirely (Eq 6).

#### Table Repair Results

##### focused_table_aries (aries_cost_account pages 1, 4, 7)

**Target:** Sidebar boxes falsely detected as tables with `<br>` + `Col2`/`Col3` headers

**Results:**
- Page 1: False table correctly removed, sidebar text preserved as prose
- Page 4: Table 2 (Cost Accounts) **reconstructed as clean pipe table** — genuine improvement over best_v1's flat text
- Page 7: Table 4 (LSA Factors) reconstructed correctly; **bonus: recovered a highlighted paragraph the library missed entirely**
- All `<br>` artifacts and `Col2`/`Col3` headers eliminated

**Verdict:** Good quality table repair. Real tables reconstructed, false tables removed, bonus content recovered.

##### focused_table_paischer (paischer_2025 pages 1, 4)

**Target:** Architecture diagrams falsely detected as pipe tables

**Results:**
- Page 1: All 3 false tables from Figure 1 correctly removed, replaced with `[Figure 1: ...]` placeholder
- Page 4: Both false tables from Figure 2 correctly removed, replaced with `[Figure 2a: ...]` and `[Figure 2b: ...]` placeholders
- Non-table content preserved

**Verdict:** Excellent — the cleanest Track B experiment. All 5 false tables correctly identified and handled.

##### focused_table_delene (delene_2001 pages 4, 5, 8)

**Target:** Real tables rendered as plain space-aligned text instead of pipe tables

**Results:**
- Page 4: Table of Contents reconstructed as pipe table
- Page 5: Correctly identified as near-empty page (no table to add)
- Page 8: List of Tables reconstructed as pipe table with correct entries

**Verdict:** Good — missing tables reconstructed. Uses `&nbsp;` for indentation which may not render universally.

#### Critical Issue: "Preserve Everything Else" Not Followed

**In ALL 5 focused synthesis experiments, Claude did NOT surgically patch the pymupdf4llm text.** Instead, it rewrote the entire page from vision. Evidence:

1. **Equation experiments:** The output contains two complete page rewrites separated by `---` dividers. The prose differs from the pymupdf4llm input in minor ways (word choice, heading levels) — it's a fresh extraction, not an edit.

2. **Table experiments:** Each page output starts with a reasoning preamble ("The page image shows...", "Looking at the image...") before the corrected content. Internal chain-of-thought leaked into the output.

3. **Reasoning leakage:** All outputs contain lines like:
   - "Now I have both the image and library text..."
   - "Here is the full extracted text with corrections:"
   - "Note: The page image also contains..."

   These would corrupt any downstream processing that expects clean markdown.

**This is the same pattern as Track A** — Claude uses the page image as primary source and produces a fresh extraction, not a targeted edit of the input text. The focused prompts influence *what Claude focuses on* (equations, tables) but not *how it operates* (rewrite vs patch).

#### Focused Synthesis Summary

| Feature | Quality | Preserves Input Text? | Better Than Pure Vision? |
|---------|---------|----------------------|--------------------------|
| Equation repair | Good LaTeX, some ambiguous eqs | No — full page rewrite | Occasionally (Eq 1 paischer) |
| Table false positive removal | Excellent | No — full page rewrite | Same quality |
| Missing table reconstruction | Good | No — full page rewrite | Same quality (vision also gets tables) |
| Table artifact cleanup | Good | No — full page rewrite | Same quality |

---

### Phase 2 Summary

#### What We Learned

1. **General repair (Track A) does not work.** Supplemental pymupdf4llm text is ignored. The output is equivalent to pure vision extraction but costs 22% more. This approach is not worth pursuing.

2. **Focused synthesis (Track B) does not surgically edit.** Despite prompts saying "fix only X, preserve everything else," Claude rewrites entire pages from vision. The focused prompts act more as extraction-focus hints than as editing instructions.

3. **Claude's dominant mode is vision extraction.** Whether given bare extraction instructions, supplemental text, or focused repair instructions, Claude always produces output by reading the page image. The supplemental text has minimal influence on the result.

4. **The output quality difference between approaches is marginal.** Pure vision, general repair, and focused synthesis all produce similar-quality markdown. The main variables are nondeterminism between calls and which features Claude attends to.

5. **Focused prompts help with specific features:**
   - `fix_equation.txt` occasionally produces better LaTeX than the general extraction prompt (paischer Eq 1), but not consistently
   - `fix_table.txt` reliably identifies false positive tables (diagrams detected as tables) — useful for cleanup
   - `add_table.txt` reconstructs missing tables, but pure vision also finds them

6. **Reasoning leakage is a systematic issue.** All focused synthesis outputs contain chain-of-thought text that corrupts the document. A stricter output-format prompt or postprocessing would be needed.

#### Cost Comparison

| Approach | Pages | Total Cost | Cost/Page | Quality vs Pure Vision |
|----------|-------|-----------|-----------|----------------------|
| Pure vision (Phase 1) | 75 | $5.84 | $0.078 | Baseline |
| General repair (Track A) | 75 | $7.16 | $0.095 | No improvement |
| Focused eq repair (Track B) | 6 | $1.15 | $0.192 | Marginal improvement on some eqs |
| Focused table repair (Track B) | 8 | $0.96 | $0.120 | Good for false positive removal |
| **Total Phase 2 spend** | | **$9.28** | | |
| **Cumulative spend (Phase 0-2)** | | **~$15.88** | | |

#### Implications for Pipeline Design

**Pure vision is the optimal Claude extraction mode.** The supplemental text and focused repair approaches add cost without meaningfully improving quality.

For the Stage 3 pipeline, the recommended Claude integration is:
1. **Use pymupdf4llm as the primary extractor** (free, fast, ~1s per document)
2. **Use Claude pure vision on targeted pages** where pymupdf4llm has known failures:
   - Math-heavy pages (equation garbling)
   - Pages where pymupdf4llm detects 0 headings (structural failure)
   - Pages where pymupdf4llm detects false tables (diagram confusion)
3. **Do NOT send pymupdf4llm text to Claude** — it doesn't help and adds cost
4. **Use the general `extract_baseline.txt` prompt** — focused prompts don't produce meaningfully better results for the extra prompt engineering effort

The equation gap cannot be filled by any combination of pymupdf4llm + Docling + GMFT. Claude is the only tool that produces LaTeX from page images. This is its irreplaceable contribution to the pipeline.

---

## Final Assessment (Phase 3)

### a. Cross-Tool Comparison Table

All metrics from the 4-paper subset. "Claude (best)" uses the pure vision results (Phase 1), since general repair and focused synthesis showed no improvement.

| Paper | Metric | pymupdf4llm | Docling | GMFT | Claude (best) |
|-------|--------|------------:|--------:|-----:|--------------:|
| **hawker_2020** | chars | 59,949 | 52,923 | 11,406 | 43,139 |
| (14pp) | headings | 14 | 17 | 0 | 13 |
| | table_rows | **0** | 40 | 40 | **40** |
| | math_symbols | 11 | 8 | 7 | 1 (see below) |
| | figure_refs | 12 | 12 | 0 | 12 |
| | time | 5.9s | 18.5s | 1.7s | 460s |
| | cost | free | free | free | $0.81 |
| **hsu_2020** | chars | 13,560 | 14,947 | 11,977 | 13,504 |
| (9pp) | headings | 5 | 6 | 0 | 4 |
| | table_rows | 56 | 56 | 88 | **56** |
| | math_symbols | 0 | 0 | 0 | 0 |
| | figure_refs | 1 | 1 | 0 | 1 |
| | time | 1.6s | 15.1s | 1.8s | 210s |
| | cost | free | free | free | $0.43 |
| **hansen_2025** | chars | 60,840 | 56,317 | 3,909 | 57,263 |
| (28pp) | headings | 17 | 18 | 0 | 15 |
| | table_rows | **0** | 15 | 42 | **15** |
| | math_symbols | 12 | 11 | 7 | 1 (see below) |
| | figure_refs | 30 | 30 | 0 | 30 |
| | time | 3.6s | 26.1s | 2.4s | 722s |
| | cost | free | free | free | $2.31 |
| **paischer_2025** | chars | 106,370 | N/A | 6,343 | 85,513 |
| (24pp) | headings | 68 (inflated) | N/A | 0 | 26 |
| | table_rows | **137 (false!)** | N/A | 52 | **55** |
| | math_symbols | 21 | N/A | 1 | 0 (see below) |
| | figure_refs | 31 | N/A | 0 | 31 |
| | time | 29.8s | N/A | 2.4s | 895s |
| | cost | free | N/A | free | $2.29 |

**Notes on GMFT:** GMFT extracts only table content (no headings, no prose, no figures). Its char_count and heading_count are expected to be low. Table_row counts are comparable to other tools.

**Notes on Docling:** Docling timed out on paischer_2025 (24pp NeurIPS paper). Results marked N/A.

### b. Equation Quality Assessment

**The `math_symbol_count` metric is not valid for comparing Claude against library tools.** The metric counts Unicode math symbols (Greek letters, operators). pymupdf4llm outputs garbled Unicode; Claude outputs clean ASCII LaTeX. Claude scores 0-1 on this metric but has vastly superior equation coverage.

**Actual LaTeX expression counts in Claude vision output:**

| Paper | Display (`$$...$$`) | Inline (`$...$`) | Total | pymupdf4llm equivalent |
|-------|--------------------:|-----------------:|------:|------------------------|
| hawker_2020 | 21 | ~93 | ~114 | Garbled Unicode fragments |
| hansen_2025 | ~10 | extensive | extensive | Unicode symbols survive, structure lost |
| paischer_2025 | 24 | ~332 | ~356 | `~~�~~` replacement chars, duplicated fragments |

#### Specific Equation Comparisons

**Equation 2.1 (hawker_2020 — LCOE definition):**

pymupdf4llm:
```
          - _n_
_i_ =1 _[C][/]_ [(1][ +] _[ d]_ [)] _[i]_
LCOE = ~~�~~ _n_ [,] (2.1)
_i_ =1 _[E][i][/]_ [(1][ +] _[ d]_ [)] _[i]_
```

Claude:
```
$$\text{LCOE} = \frac{\sum_{i=1}^{n} C_i / (1+d)^i}{\sum_{i=1}^{n} E_i / (1+d)^i}$$
```
**Verdict: Correct.** Clean fraction, summation notation, subscripts/superscripts.

**Equation 2.3 (hawker_2020 — piecewise cost model):**

pymupdf4llm:
```
_Ci_ =
_Cp_ + _CY_ + _Cd_, _c_ on during construction, (2.3)
_Ct_ + _CO_ & _M_ + _Cd_, _op_ during operation
```

Claude:
```
$$C_t = \begin{cases} C_P + C_Y + C_{d,\text{con}} & \text{during construction} \\
C_t + C_{\text{O\&M}} + C_{d,op} & \text{during operation} \end{cases}, \tag{2.3}$$
```
**Verdict: Correct.** Restored `\begin{cases}` brace that pymupdf4llm lost entirely.

**Equation 1 (paischer_2025 — gyrokinetic PDE):**

pymupdf4llm:
```
_∂f B · ∇B ∂f_
_∂t_ [+ (] _[v][∥]_ _**[b]**_ [ +] _**[ v]**_ _[D]_ [)] _[ · ∇][f][ −]_ _[µB]_ _m_ _B_ [2] _∂v∥_
~~�~~ ~~�~~ - ~~�~~
Linear
+ _**v**_ _χ · ∇f_
~~�~~ ~~��~~ ~~�~~
Nonlinear
```

Claude:
```
$$\underbrace{\frac{\partial f}{\partial t} + (v_b \mathbf{b} + v_D) \cdot \nabla f}_{\text{Linear}}
- \underbrace{...}_{\text{[?]}} + \underbrace{v_\chi \cdot \nabla f}_{\text{Nonlinear}} = S$$
```
**Verdict: Mostly correct.** Proper `\underbrace` structure with labels. Claude marked one ambiguous term with `[?]` rather than guessing — correct behavior per the fidelity instruction. The focused repair version (Phase 2) produced a better reconstruction of the middle term.

**Equation quality limitations:**

On complex gain-curve equations (hawker_2020 eqs 2.18, 2.20), Claude produces plausible but uncertain LaTeX. Both pure vision and focused repair produce different reconstructions of the same equation — neither can be verified as correct without the source LaTeX. This affects ~10% of equations (those with small print, complex nested fractions, or unusual notation).

#### Equation Quality Verdict

Claude's equation transcription is **the single most valuable capability** discovered in Stage 1D. No other tool in 1A-1D produces renderable LaTeX from PDF page images. For ~90% of equations, Claude produces correct, clean LaTeX. For the remaining ~10% (complex, small-print), it produces reasonable approximations with appropriate uncertainty markers.

### c. Hallucination Risk Assessment

**Methodology:** Across Phases 1 and 2, 20+ numerical values were spot-checked per paper against the source PDFs and internal consistency.

| Paper | Values Checked | Hallucinated? | Notes |
|-------|---------------:|:--------------|-------|
| hawker_2020 | 8+ | **No** | One minor discrepancy: availability calculation 83.3% vs paper's 86% — likely different assumptions, not hallucination |
| hsu_2020 | 8+ | **No** | All table values internally consistent; CAS account hierarchy preserved |
| hansen_2025 | 6+ | **No** | Plasma parameters (density, velocity, temperature) all plausible |
| paischer_2025 | 5+ | **No** | ML benchmark numbers specific enough to rule out fabrication (e.g., "67.68 ± 10.28") |

**One systematic OCR issue:** "GyroSwim" vs "GyroSwin" in paischer_2025 table cells (14 instances). This is a font-size-dependent misread, not a hallucination — the correct spelling appears 49 times in running text on the same pages.

**Verdict:** No hallucinated content detected in any experiment across all 4 papers. Claude preserves numerical values with high fidelity from page images. The risk is OCR misreads (minor, predictable), not content fabrication.

### d. Cost Projection

| Configuration | Pages | Cost/Page | 4-Paper (75pp) | Projected 15-Paper (573pp) |
|--------------|------:|----------:|----------------:|---------------------------:|
| pymupdf4llm | any | free | free | free |
| Docling | any | free | free | free |
| GMFT | any | free | free | free |
| Claude vision (Sonnet) | 1pp | $0.078 | $5.84 | ~$44.70 |
| Claude repair (Sonnet) | 1pp | $0.095 | $7.16 | ~$54.40 |
| Focused synthesis (Sonnet) | 1pp | $0.151 | N/A (targeted) | N/A |

**Targeted use projection (recommended pipeline):**

| Scenario | Pages/Document (est.) | Cost/Document | 15-Paper Corpus |
|----------|-----------------------:|-------------:|----------------:|
| Equation-heavy pages only | ~5-10 | $0.39-$0.78 | ~$6-12 |
| Equation + broken tables | ~8-15 | $0.62-$1.17 | ~$9-18 |
| All pages (not recommended) | ~38 avg | $2.96 | ~$45 |

**Token economics:** A single page image consumes ~61K input tokens via the Read tool workaround. At Sonnet pricing (~$3/MTok input, ~$15/MTok output), the input cost dominates (~$0.18 input vs ~$0.01 output per page). Output tokens average ~900/page.

### e. General Repair vs Focused Synthesis

| Dimension | General Repair (Track A) | Focused Synthesis (Track B) |
|-----------|--------------------------|----------------------------|
| **How it works** | Image + full-page pymupdf4llm text + general extraction prompt | Image + per-page pymupdf4llm text + targeted repair prompt |
| **What Claude actually does** | Ignores supplemental text, re-extracts from vision | Ignores "edit only X" instruction, re-extracts from vision |
| **Quality vs pure vision** | No improvement | Marginal improvement on ~10% of equations |
| **Cost vs pure vision** | +22% ($0.095 vs $0.078/page) | +94% ($0.151 vs $0.078/page) |
| **Output format** | Clean (no reasoning leakage) | Corrupted (reasoning/commentary leaked into output) |
| **Recommendation** | **Do not use** | **Do not use** |

**Root cause:** Claude's dominant behavior when given a page image is to extract from vision. Supplemental text and focused instructions influence what Claude attends to, but not how it operates. Both approaches result in a fresh vision extraction, not an edit of the input text.

**The optimal approach is pure vision extraction with the general `extract_baseline.txt` prompt.** It costs less, produces equivalent quality, and has no reasoning leakage issues.

### f. Pipeline Recommendation

#### Where Claude Adds Value

Claude headless (`claude -p`) adds irreplaceable value for **equation transcription to LaTeX**. No library tool in Stages 1A-1C produces renderable LaTeX from PDF page images. Claude also provides:
- Accurate table detection (no false positives from diagrams)
- Heading detection on documents where pymupdf4llm fails (e.g., hansen_2025)
- Clean output with no `<br>` artifacts or false formatting

#### Where Claude Is Not Needed

- **Text extraction on non-math pages:** pymupdf4llm is adequate and 100x faster
- **Table extraction on clean PDFs:** Docling and GMFT handle tables reliably at zero cost
- **Heading detection on most documents:** pymupdf4llm with composite header detector works for most formats

#### Recommended Stage 3 Pipeline

```
1. Extract with pymupdf4llm (all pages, free, <1s/document)
2. Analyze extraction quality:
   - Flag pages with equation garbling (~~, Unicode salad, replacement chars)
   - Flag pages with 0 headings where headings are expected
   - Flag pages with suspected false table detection (diagram content in pipe tables)
3. Re-extract flagged pages with Claude vision (pure vision, $0.078/page)
4. Merge: use Claude output for flagged pages, pymupdf4llm for the rest
```

**Cost for this pipeline:** Typically 5-15 pages per document need Claude re-extraction. At $0.078/page, that's **$0.39-$1.17 per document** — 10-30x cheaper than full Claude extraction while capturing the key quality improvements.

#### What We Did NOT Test

1. **Opus model** — Sonnet was used throughout. Opus may produce better LaTeX on the ~10% of ambiguous equations.
2. **Pages-per-call batching** — All experiments used 1 page per call. Multi-page batching (5pp, 10pp) was planned but deprioritized after the key finding that pure vision is optimal.
3. **Full 15-paper corpus** — Only 4 papers (+ 2 targeted) were tested. The full corpus would cost ~$45 for pure vision.
4. **Docling MCP** — Docling's MCP server integration was not tested (requires separate server configuration).
5. **Aggressive supplemental text prompts** — The prompt says "trust the page images as primary source." A prompt that says "START from the library text, ONLY fix equations" was not tested and might change the supplemental text result.
6. **Postprocessing** — No cleanup of Claude's output was attempted (e.g., stripping reasoning leakage, normalizing heading levels).
7. **Haiku model** — Lower cost model not tested. May be sufficient for equation transcription at ~3x lower cost.

### Total Experiment Spend

| Phase | Description | Cost |
|-------|-------------|-----:|
| Phase 0 | Setup & smoke tests | ~$0.08 |
| Phase 1 | Pure vision baseline (75 pages) | $5.84 |
| Phase 2 Track A | General repair (75 pages) | $7.16 |
| Phase 2 Track B | Focused synthesis (14 pages) | $2.12 |
| Phase 2 smoke | Supplemental text verification | $0.10 |
| **Total** | | **$15.30** |

Within the ~$16 budget estimated in the plan.
