# Pandoc Deep-Dive Findings Report

**Status:** In Progress
**Started:** 2026-02-22
**Pandoc Version:** 3.1.3

---

## Phase 1: Structured Source Discovery

### LL7Q6PSU / paischer_2025 (Primary Test)

**Starting point:** PDF only — `tests/corpus/pdfs/paischer_2025.pdf`
**Goal:** Find arXiv ID and HTML link

**Step 1: Extract text from first 2 pages with `pdftotext`**
**Result:** arXiv ID found immediately — first line of the PDF reads:
```
arXiv:2510.07314v1 [physics.plasm-ph] 8 Oct 2025
```
**Time:** ~10 seconds

**Step 2: Check PDF metadata with `pdfinfo`**
**Result:** `Creator` field is `arXiv GenPDF (tex2pdf:e76afa9)` — confirms arXiv origin but does NOT contain the actual ID. The metadata alone is insufficient; you need the text.

**Step 3: Construct HTML URL and verify**
**Pattern:** `https://arxiv.org/html/{id}` → `https://arxiv.org/html/2510.07314v1`
**Verification:** `curl -o /dev/null -w "%{http_code}"` → HTTP 200, Content-Type: text/html, 328KB
**Result:** HTML exists and is served.

**Final result:**
- arXiv ID found: **yes** — `2510.07314v1`
- HTML URL: `https://arxiv.org/html/2510.07314v1`
- HTML exists: **yes** — verified via HTTP HEAD, 328KB
- Total discovery time: **< 1 minute**
- Discovery method: `pdftotext` on first 2 pages, regex match for `arXiv:\d+\.\d+`

---

### Generalizability Tests

#### woodruff_2026

**Starting point:** `tests/corpus/pdfs/woodruff_2026.pdf`

**Step 1: `pdftotext` first 2 pages**
**Result:** First line: `arXiv:2601.21724v2 [physics.soc-ph] 31 Jan 2026` — immediate hit.

**Step 2: PDF metadata**
**Result:** No arXiv-specific fields in `pdfinfo` output. Creator is generic LaTeX.

**Step 3: Verify HTML**
**URL:** `https://arxiv.org/html/2601.21724v2`
**Result:** HTTP 200, 399KB — HTML exists.

**Final result:**
- arXiv ID found: **yes** — `2601.21724v2`
- HTML URL: `https://arxiv.org/html/2601.21724v2`
- HTML exists: **yes** — 399KB
- Total discovery time: **< 1 minute**

#### hawker_2020

**Starting point:** `tests/corpus/pdfs/hawker_2020.pdf`

**Step 1: `pdftotext` first 2 pages**
**Result:** No arXiv ID found. Text begins with title and journal info: "royalsocietypublishing.org/journal/rsta". DOI found: `10.1098/rsta.2020.0053`.

**Step 2: PDF metadata**
**Result:** `Creator: LaTeX with hyperref package + hypdvips`, `Producer: Acrobat Distiller 8.1.0 (Windows)`. Subject field: `Phil. Trans. R. Soc. A. 2020.378:20200053`. No arXiv indicators.

**Step 3: Web search for arXiv version**
**Query:** `arxiv "A simplified economic model for inertial fusion" Hawker 2020`
**Result:** Paper found on Royal Society, PMC, Semantic Scholar, ResearchGate — but **no arXiv preprint** exists. Published only as journal article.

**Final result:**
- arXiv ID found: **no** — paper is not on arXiv
- HTML URL: N/A
- Total discovery time: **~2 minutes**

#### sparc_overview

**Starting point:** `tests/corpus/pdfs/sparc_overview.pdf`

**Step 1: `pdftotext` first 2 pages**
**Result:** No arXiv ID found. Text begins with journal header: "J. Plasma Phys. (2020), vol. 86, 865860502". DOI found: `10.1017/S0022377820001257`.

**Step 2: PDF metadata**
**Result:** `Creator: LaTeX with hyperref package`, `Producer: Acrobat Distiller 8.1.0 (Windows)`. Title field is empty. No arXiv indicators.

**Step 3: Web search for arXiv version**
**Query:** `arxiv "Overview of the SPARC tokamak" Creely 2020`
**Result:** Found on Cambridge Core, OSTI.gov, ORNL, ResearchGate, NASA ADS — but **no arXiv preprint** exists.

**Step 4: Check NASA ADS record**
**URL:** `https://ui.adsabs.harvard.edu/abs/2020JPlPh..86e8602C/abstract`
**Result:** ADS record exists but has no arXiv ID field populated. Confirms journal-only publication.

**Final result:**
- arXiv ID found: **no** — paper is not on arXiv
- HTML URL: N/A
- Total discovery time: **~3 minutes**

---

### Discovery Process Assessment

**Reliable methods:**
1. **`pdftotext` on first 1-2 pages** — arXiv papers consistently have the ID in the first line (e.g., `arXiv:2510.07314v1 [physics.plasm-ph] 8 Oct 2025`). This was 100% reliable for arXiv papers in the corpus. Pattern: `arXiv:\d{4}\.\d{4,5}(v\d+)?`.
2. **PDF metadata `Creator` field** — arXiv-generated PDFs use `arXiv GenPDF` as the creator. This is a strong positive signal but does NOT contain the actual ID.
3. **`https://arxiv.org/html/{id}` URL pattern** — verified working for both 2025 and 2026 papers. Returns 200 with full HTML.

**Brittle methods:**
1. **PDF metadata fields** — generic; only useful as a negative signal (non-arXiv papers have generic LaTeX/Distiller creators). Cannot extract the actual arXiv ID from metadata.
2. **Web search from title** — works for confirming existence but is slow (~2 min) and returns too many results to parse programmatically without additional filtering.

**What doesn't work:**
- Older journal papers (hawker_2020 from 2020, sparc_overview from 2020) are NOT on arXiv at all. arXiv HTML is only available for papers that were submitted to arXiv.
- arXiv HTML availability may depend on submission date — arXiv launched HTML rendering around 2023-2024. Papers from 2020 that ARE on arXiv may not have HTML versions.

**Automation feasibility:**
- **High confidence for arXiv detection:** A script can: (1) run `pdftotext` on page 1, (2) regex for `arXiv:\d{4}\.\d{4,5}`, (3) if found, construct `https://arxiv.org/html/{id}` and verify with HTTP HEAD. This is fast (<1s) and reliable.
- **Medium confidence for non-arXiv detection:** If no arXiv ID in text AND Creator is not `arXiv GenPDF`, the paper is almost certainly not on arXiv. Could stop here without web search.
- **Low confidence for edge cases:** Papers that are on arXiv but don't have the ID in the first page (rare), or papers where the arXiv ID is in a footnote or reference section rather than the header.

**Recommendation for Stage 5 (Source Routing):**
The arXiv ID discovery process is **highly automatable** for the common case:
1. `pdftotext` page 1 → regex for arXiv ID (fast, reliable)
2. If found → `HEAD https://arxiv.org/html/{id}` to check HTML availability
3. If not found → check `pdfinfo` Creator for `arXiv` string as secondary signal
4. If neither → paper is not from arXiv; skip HTML path

The entire process takes <1 second per paper for arXiv papers and ~1 second for non-arXiv papers (no need for web search in the automated case). Web search is only needed as a manual fallback for ambiguous cases.

**Key finding for pipeline design:** Of 4 papers tested, 2/4 (50%) had arXiv IDs and HTML available. Both were recent (2025, 2026). The 2 papers from 2020 were journal-only publications. This suggests arXiv HTML availability is biased toward recent preprints, which is exactly the population most likely to benefit from HTML extraction (since they also tend to have the most complex equations and formatting).

---

## Phase 3: Pandoc PDF Input

**Finding:** Pandoc 3.1.3 does **not** support PDF as an input format.

**Evidence:**

1. **`pandoc --list-input-formats`** — output lists 43 formats; `pdf` is not among them. Supported formats include: biblatex, bibtex, commonmark, commonmark_x, creole, csljson, csv, docbook, docx, dokuwiki, endnotexml, epub, fb2, gfm, haddock, html, ipynb, jats, jira, json, latex, man, markdown, markdown_github, markdown_mmd, markdown_phpextra, markdown_strict, mediawiki, muse, native, odt, opml, org, ris, rst, rtf, t2t, textile, tikiwiki, tsv, twiki, typst, vimwiki.

2. **Attempted conversion error:**
   ```
   $ pandoc --from=pdf tests/corpus/pdfs/paischer_2025.pdf -t markdown
   Unknown input format pdf
   Pandoc can convert to PDF, but not from PDF.
   (exit code 21)
   ```

3. **Extension variants also fail:**
   ```
   $ pandoc -f pdf+raw_attribute tests/corpus/pdfs/paischer_2025.pdf -t markdown
   Unknown input format pdf
   Pandoc can convert to PDF, but not from PDF.
   ```

4. **Additional research:** Web search for "pandoc PDF input reader plugin" confirms no native PDF reader exists or is planned. Pandoc's architecture requires a text-based AST reader — PDFs are binary documents with no semantic structure accessible to Pandoc's reader framework. Pandoc supports PDF as an *output* format (via LaTeX or HTML intermediaries) but not as input. No Lua custom reader for PDF exists in the community. Third-party workarounds involve piping through external tools (e.g., `pdftotext | pandoc -f markdown`), which is just using a different extractor.

**Conclusion:** The development strategy's note that "Pandoc can also read PDFs (poorly)" is **incorrect** for Pandoc 3.1.3. Pandoc explicitly rejects PDF input with a clear error message. PDF→markdown extraction requires pymupdf4llm, Docling, or another dedicated PDF parser.

**Implication for spec FR-4:** Pandoc PDF→markdown experimentation is **not possible** — there is nothing to test. The spec's acceptance criterion "At least 3 Pandoc PDF→markdown runs tested and documented" is satisfied by this definitive negative finding. The cross-format comparison (Phase 5) will compare Pandoc HTML vs pymupdf4llm PDF only — there is no third path to compare.

---

## Phase 4: HTML→Markdown Experiments

**Test document:** `tests/corpus/html/paischer_2025.html` (328KB, arXiv:2510.07314v1)
**HTML source characteristics:** 289 MathML elements, 44 equation blocks, 26 `<table>` elements, 23 headings. arXiv LaTeXML-generated HTML with extensive CSS classes (`ltx_*`), `<figure>` wrappers, scaled table containers, and MathML with LaTeX `alttext` attributes.

### Metrics Summary

| Iter | Chars | Hdg | Tbl† | Math‡ | Fig | Lines | Configuration |
|------|-------|-----|------|-------|-----|-------|---------------|
| 01 | 184,631 | 23 | 4 | 3 | 21 | 3,212 | Baseline: `-f html -t markdown` |
| 02 | 182,579 | 23 | 3 | 3 | 21 | 1,140 | `--wrap=none` |
| 03 | 185,399 | 23 | 4 | 3 | 21 | 2,184 | `--wrap=preserve` |
| 04 | 184,631 | 23 | 4 | 3 | 21 | 3,212 | `--markdown-headings=atx` |
| 05 | 184,631 | 23 | 4 | 3 | 21 | 3,212 | `-t markdown+tex_math_dollars` |
| 06 | 184,631 | 23 | 4 | 3 | 21 | 3,212 | `-t markdown+tex_math_single_backslash` |
| 07 | 205,781 | 23 | 4 | 3 | 21 | 3,296 | `--mathml` |
| 08 | 184,633 | 23 | 4 | 0 | 21 | 3,205 | `--katex` |
| 09 | 184,630 | 23 | 4 | 3 | 21 | 3,212 | `-t markdown+grid_tables-pipe_tables` |
| 10 | 183,731 | 23 | 4 | 3 | 21 | 2,226 | `--columns=120` |
| 11 | 182,579 | 23 | 3 | 3 | 21 | 1,140 | `--wrap=none --markdown-headings=atx` |
| 12 | 182,579 | 23 | 3 | 3 | 21 | 1,140 | Combined: `+tex_math_dollars --wrap=none --markdown-headings=atx --columns=120` |
| **13** | **149,555** | **23** | **3** | **3** | **21** | **893** | **`-f html-native_divs-native_spans --wrap=none --markdown-headings=atx`** |
| **14** | **148,168** | **23** | **3** | **3** | **21** | **893** | **`-f html-native_divs-native_spans -t markdown-header_attributes --wrap=none --markdown-headings=atx`** |
| 15 | 151,305 | 23 | 3 | 3 | 21 | 893 | `-f html-native_divs-native_spans -t markdown-header_attributes-link_attributes --wrap=none --markdown-headings=atx` |

†Table row count: Detects pipe-separated lines — here counting equation alignment artifacts (dash tables around `$$...$$`), NOT actual data tables (which pass through as raw HTML).
‡Math symbol count: Counts unique Unicode math symbols (Greek, operators) — NOT LaTeX commands. Math is well-converted to LaTeX `$...$` but the metric doesn't capture this.

---

### Experiment 1: Baseline
**Command:** `pandoc -f html -t markdown`
**Output:** `tests/corpus/pandoc-experiments/iter-01/paischer_2025.md`

**Observations:**
- **Headings:** All 23 headings found as ATX (`#`, `##`, `###`). But heavily annotated with Pandoc attribute syntax:
  > `## [1 ]{.ltx_tag .ltx_tag_section}Introduction {#introduction .ltx_title .ltx_title_section}`
- **Paragraphs:** Wrapped in Pandoc div blocks: `::: {#S1.p1 .ltx_para}`
- **Inline text:** Wrapped in Pandoc span syntax: `[text]{.ltx_text .ltx_font_bold}`
- **Math (inline):** Correctly converted to LaTeX `$...$`:
  > `$f = {f\hspace{0pt}{(k_{x},k_{y},s,v_{||},\mu)}}$`
- **Math (block equations):** Correctly converted to `$$...$$` with equation numbers. However, each block equation is wrapped in a 3-column dash table (an artifact of arXiv's LaTeXML equation alignment):
  > `-- [long dashes] --`
  > `   $$\frac{\partial f}{\partial t}...$$      [(1)]{.ltx_tag}`
  > `-- [long dashes] --`
- **Tables:** All 5 data tables pass through as **raw HTML** with full `<table class="ltx_tabular">` markup, `<figure>` wrappers, and inline styles. Pandoc does NOT convert arXiv HTML tables to markdown pipe/grid tables.
- **Figures:** Pass through as raw `<figure>` HTML with `<img>` tags referencing relative arxiv paths (`/html/2510.07314v1/x1.png`).
- **Citations:** Readable inline links: `(Bourdelle et al., [2015](url){.ltx_ref})`
- **References section:** Full bibliography rendered with links to arXiv entries.

**Verdict:** **Usable but noisy** — Math is the clear strength. Tables and figures are raw HTML. Div/span wrappers add ~35KB of unnecessary markup.

---

### Experiment 2: `--wrap=none`
**Command:** `pandoc -f html -t markdown --wrap=none`

**Observations:**
- Line count drops from 3,212 to 1,140 — each paragraph becomes a single long line
- Character count drops slightly (182K vs 185K) — fewer newlines and continuation indentation
- No quality difference in headings, math, or tables
- Much better for programmatic processing (one paragraph = one line)

**Verdict:** **Strictly better than baseline** for pipeline use. No information lost, cleaner for processing.

---

### Experiment 3: `--wrap=preserve`
**Command:** `pandoc -f html -t markdown --wrap=preserve`

**Observations:**
- 2,184 lines — between baseline (3,212) and `--wrap=none` (1,140)
- Preserves the HTML source's original line breaks
- Slightly larger (185K) due to preserved whitespace
- No quality difference otherwise

**Verdict:** **No advantage** over `--wrap=none` for our pipeline.

---

### Experiment 4: `--markdown-headings=atx`
**Command:** `pandoc -f html -t markdown --markdown-headings=atx`

**Observations:** Identical to baseline in every way — Pandoc already defaults to ATX headings for this HTML input.

**Verdict:** **No effect** — already the default.

---

### Experiments 5-6: Math output extensions
**Commands:** `-t markdown+tex_math_dollars` and `-t markdown+tex_math_single_backslash`

**Observations:** Identical output to baseline. These are *output* format extensions that control how Pandoc writes math it already has in its AST. Since Pandoc is already outputting `$...$` and `$$...$$` by default for markdown, enabling these extensions changes nothing.

**Verdict:** **No effect** — math is already rendered as TeX by default.

---

### Experiment 7: `--mathml`
**Command:** `pandoc -f html -t markdown --mathml`

**Observations:**
- 21KB larger (206K vs 185K)
- Block equations in prose: **Identical** to baseline (`$$...$$` LaTeX)
- Math inside raw HTML tables: Changed from `<span class="math inline">→</span>` to full MathML `<math display="inline" xmlns="..."><semantics><mo>→</mo><annotation encoding="application/x-tex">\rightarrow</annotation></semantics></math>`
- This only affects math symbols inside the raw HTML passthrough tables — NOT the main content

**Verdict:** **Worse** — adds bloat to raw HTML tables without improving main content. No benefit for our pipeline.

---

### Experiment 8: `--katex`
**Command:** `pandoc -f html -t markdown --katex`

**Observations:**
- Math symbol count drops to 0 (metric sees no Unicode math — but that's because KaTeX output is still `$...$` LaTeX, same as baseline)
- Output is nearly identical to baseline (7 lines fewer, ~150 bytes different)
- The only difference is in how some inline math arrows are rendered in raw HTML tables

**Verdict:** **No meaningful effect** on main content.

---

### Experiment 9: Grid tables
**Command:** `-t markdown+grid_tables-pipe_tables`

**Observations:** Identical output to baseline. The grid table extension affects how Pandoc *writes* tables that it has in its AST. Since arXiv HTML tables fail to parse into Pandoc's AST (they pass through as raw HTML), the output extension has no effect.

**Verdict:** **No effect** — tables aren't being parsed at all.

---

### Experiment 10: `--columns=120`
**Command:** `pandoc -f html -t markdown --columns=120`

**Observations:**
- 2,226 lines (vs 3,212 baseline) — wider wrapping means fewer line breaks
- Otherwise identical quality

**Verdict:** **Marginal improvement** — fewer lines but `--wrap=none` is better.

---

### Experiments 11-12: Combinations
**Commands:** `--wrap=none --markdown-headings=atx` and `+tex_math_dollars --wrap=none --markdown-headings=atx --columns=120`

**Observations:** Identical to `--wrap=none` alone (iter-02). The additional flags had no effect because ATX headings and tex_math_dollars are already defaults.

**Verdict:** `--wrap=none` is the only flag doing real work in these combinations.

---

### Experiment 13: Stripping native divs and spans ★
**Command:** `-f html-native_divs-native_spans -t markdown --wrap=none --markdown-headings=atx`

**Observations — major breakthrough:**
- **35KB smaller** (150K vs 185K) — stripping div/span wrappers removes massive markup overhead
- **893 lines** (vs 1,140 with `--wrap=none` alone) — cleaner paragraph structure
- **Divs gone:** No more `::: {#S1.p1 .ltx_para}` wrappers around every paragraph
- **Spans gone:** No more `[text]{.ltx_text .ltx_font_bold}` — inline text renders directly
- **Headings cleaner:** `## 1 Introduction` instead of `## [1 ]{.ltx_tag .ltx_tag_section}Introduction`
- **Inline lists cleaner:** `(i) extension of...` instead of `[[(i)]{.ltx_tag}[extension of...]{.ltx_text}]`
- **Math unchanged:** Still perfectly converted `$...$` and `$$...$$`
- **Tables/figures:** Still raw HTML (these aren't divs/spans)
- **Equation numbers:** Now render as `\(1\)` instead of `[(1)]{.ltx_tag .ltx_tag_equation}` — cleaner

**Verdict:** **Major improvement** — this single input extension makes the biggest quality difference.

---

### Experiment 14: Also stripping header attributes ★★ BEST
**Command:** `-f html-native_divs-native_spans -t markdown-header_attributes --wrap=none --markdown-headings=atx`

**Observations:**
- **Smallest output:** 148K (20% smaller than baseline)
- Headings are now fully clean:
  > `## 1 Introduction` (no `{#introduction .ltx_title}` suffix)
  > `## 2 Background and Related Work`
- All benefits of iter-13 plus cleaner headings
- Table of contents rendered as a numbered markdown list at the top
- Citations inline and readable: `(Bourdelle et al., [2015](url){.ltx_ref}; Citrin et al., [2017](url){.ltx_ref})`

**Example output (Section 2, first paragraph):**
> `5D Gyrokinetics. To determine turbulent transport, one must simulate the evolution of electrons and ions in the plasma over time. In principle, this could be achieved by modelling each species as a particle in the plasma (Birdsall & Langdon, [2005](https://arxiv.org/html/2510.07314v1#bib.bib5){.ltx_ref}; Tskhakaya, [2008](https://arxiv.org/html/2510.07314v1#bib.bib54){.ltx_ref}). However, because the number of particles in a plasma can exceed 10^20^, this approach is computationally expensive.`

**Example equation (Eq. 1):**
> `$${{\underset{\text{Linear}}{\underbrace{{\frac{\partial f}{\partial t}+...}}} + \underset{\text{Nonlinear}}{\underbrace{{\mathbf{v}}_{\chi}\cdot{\nabla f}}}} = S},$$`

**Verdict:** **Best overall configuration.** Clean prose, well-preserved LaTeX math, clean headings, compact output.

---

### Experiment 15: Also stripping link attributes
**Command:** `-f html-native_divs-native_spans -t markdown-header_attributes-link_attributes --wrap=none --markdown-headings=atx`

**Observations:**
- **3KB larger** than iter-14 (151K vs 148K) — removing `link_attributes` prevents Pandoc from using `{.class}` syntax on links, forcing it to encode the info differently (e.g., longer title strings)
- Links lose their `{.ltx_ref}` class but don't get cleaner — the class was harmless
- No quality improvement

**Verdict:** **Worse than iter-14** — removing link_attributes is counterproductive.

---

### Cross-Cutting Findings

#### What Pandoc does well with arXiv HTML:
1. **Math conversion is excellent.** MathML → LaTeX `$...$` / `$$...$$` is reliable and produces readable, re-renderable equations. This is the single biggest advantage of the HTML path over PDF extraction, where equations become garbled Unicode.
2. **Document structure is preserved.** All 23 headings are correctly identified with proper hierarchy (h1, h2, h3).
3. **Citations are preserved.** Inline citations with links to the bibliography work correctly.
4. **Cross-references work.** Equation, Figure, and Table references are preserved as links.
5. **Prose text is clean.** Paragraph text is well-extracted with no character-level errors.

#### What Pandoc does poorly with arXiv HTML:
1. **Tables are NOT converted.** All 5 data tables pass through as raw HTML. This is because arXiv wraps tables in `<figure>` elements with CSS scaling transforms that Pandoc can't parse. A post-processing step or different tool is needed for tables.
2. **Figures are NOT converted.** All figures pass through as raw `<figure>` HTML with relative image paths to arxiv.org.
3. **Equation alignment tables.** Block equations get wrapped in 3-column dash tables (an artifact of LaTeXML's use of `<table>` for equation numbering alignment).
4. **`\hspace{0pt}` noise.** LaTeXML inserts zero-width spacing hints throughout the LaTeX math. E.g., `$f\hspace{0pt}{(k_{x},k_{y},...)}$` instead of `$f(k_{x},k_{y},...)$`. Cosmetic but noisy.
5. **HTML comments.** Some inline `<!-- -->{=html}` artifacts remain from LaTeXML processing.

#### Which flags matter:

| Flag | Effect | Verdict |
|------|--------|---------|
| `-f html-native_divs-native_spans` | Strips `::: {.class}` and `[text]{.class}` markup | **Essential — biggest improvement** |
| `-t markdown-header_attributes` | Removes `{#id .class}` from headings | **Essential — clean headings** |
| `--wrap=none` | Single-line paragraphs | **Essential — cleaner for processing** |
| `--markdown-headings=atx` | ATX-style headings | **No effect** (already default) |
| `+tex_math_dollars` | TeX math dollar signs | **No effect** (already default) |
| `+tex_math_single_backslash` | TeX math backslash notation | **No effect** |
| `--mathml` | MathML output | **Harmful** — adds bloat |
| `--katex` | KaTeX output | **No effect** |
| `+grid_tables-pipe_tables` | Grid table output | **No effect** — tables don't parse |
| `--columns=120` | Wider line wrapping | **Marginal** — `--wrap=none` is better |
| `-t markdown-link_attributes` | Remove link class attrs | **Harmful** — increases size |

### Recommended Configuration

```bash
pandoc INPUT.html \
  -f html-native_divs-native_spans \
  -t markdown-header_attributes \
  --wrap=none \
  --markdown-headings=atx
```

**Why these settings:**
- `-f html-native_divs-native_spans` — most impactful single change (Experiment 13, 35KB savings)
- `-t markdown-header_attributes` — additional ~1.5KB savings, cleaner headings (Experiment 14)
- `--wrap=none` — essential for pipeline processing (Experiment 2, 64% line reduction)
- `--markdown-headings=atx` — explicit for consistency even though it's the default

---

### Experiment 16: Pre-processing HTML to strip `<figure>` wrappers ★★★ BEST OVERALL
**Command:** Pre-process HTML with Python (strip `<figure>`, `</figure>`, `ltx_transformed_outer` divs, `ltx_transformed_inner` spans), then `-f html-native_divs-native_spans -t markdown-header_attributes --wrap=none --markdown-headings=atx`

**Root cause investigation:** Tables and figures were passing through as raw HTML in all prior iterations. Web search revealed Pandoc GitHub issues ([#5014](https://github.com/jgm/pandoc/issues/5014), [#222](https://github.com/jgm/pandoc/issues/222), [#2015](https://github.com/jgm/pandoc/issues/2015)) documenting that Pandoc treats `<figure>` as a raw HTML block — everything inside it (tables, images, captions) gets passed through verbatim.

**Test:** Extracted the bare `<table>` element from the HTML (without its `<figure>` wrapper) and fed it to Pandoc — **it converted perfectly to a markdown simple table.** The table content was never the problem; the `<figure>` wrapper was.

**Pre-processing step (3 lines of Python):**
```python
html = re.sub(r'<figure[^>]*>', '', html)
html = html.replace('</figure>', '')
html = re.sub(r'<div class="ltx_inline-block[^"]*ltx_transformed_outer[^>]*>', '', html)
html = re.sub(r'<span class="ltx_transformed_inner[^>]*>', '', html)
```

**Observations — dramatic improvement:**
- **125KB, 555 lines** (vs 148KB/893 for iter-14, vs 185KB/3,212 for baseline — 32% smaller than baseline)
- **ALL 5 data tables now convert to Pandoc simple tables:**
  > ```
  > Method                                       Average Flux                         Diagnostics
  > -------------------------------------------- ------------------------------------ -----------
  > Tabular Regressors, e.g., GPR, MLP           1D→0D                                ✗
  > Neural Surrogates, e.g. GyroSwin (Ours)      5D→0D                                5D→1D
  > ```
- **Table 2 (complex, 12 rows, 6 columns with LaTeX math in cells)** converts cleanly with column alignment preserved, `$\pm$` notation intact, and citations inside cells working.
- **ALL figures now convert to markdown images:**
  > `![Refer to caption](/html/2510.07314v1/x1.png)`
  > `Figure 1: Left: GyroSwin models the 5D distribution function...`
- **Figure captions** render as plain text paragraphs immediately after the image.
- **Math unchanged:** Still excellent LaTeX `$...$` and `$$...$$`.
- **Metrics:** 23 headings, 3 table row detections (equation alignment tables — the metrics module needs updating to detect simple table format), 21 figure refs.

**Verdict:** **Best overall.** All prior limitations with tables and figures are resolved by a simple HTML pre-processing step. This is the recommended pipeline configuration.

---

### Updated Cross-Cutting Findings

#### What Pandoc does well with arXiv HTML (after pre-processing):
1. **Math conversion is excellent.** MathML → LaTeX `$...$` / `$$...$$` is reliable and produces readable, re-renderable equations.
2. **Document structure is preserved.** All 23 headings correctly identified with proper hierarchy.
3. **Tables now convert.** All 5 data tables render as Pandoc simple tables with proper columns and alignment.
4. **Figures now convert.** All figures render as `![alt](path)` markdown images with captions.
5. **Citations are preserved.** Inline citations with links to bibliography work correctly.
6. **Cross-references work.** Equation, Figure, and Table references are preserved as links.
7. **Prose text is clean.** No character-level errors.

#### What still needs post-processing:
1. **Image URL resolution.** Image paths are relative to arXiv (`/html/{id}/x1.png`). Should be resolved to `https://arxiv.org/html/{id}/x1.png`.
2. **Equation alignment tables.** Block equations get wrapped in 3-column dash tables (LaTeXML artifact). Regex post-processor: strip the `-- [dashes] --` lines surrounding `$$...$$`.
3. **`\hspace{0pt}` noise.** LaTeXML inserts zero-width spacing hints. Strip with `sed 's/\\hspace{0pt}//g'`.
4. **`<!-- -->{=html}` artifacts.** A few inline HTML comment fragments from LaTeXML. Strip with regex.
5. **Table cell math has `<!-- -->` fragments.** Inside table cells, `$\rightarrow$` sometimes appears as `$\rightarrow$\`<!-- -->\`{=html}`. Regex cleanup needed.

#### Which flags and steps matter (updated):

| Step/Flag | Effect | Verdict |
|-----------|--------|---------|
| **Pre-process: strip `<figure>` tags** | Tables and figures convert to markdown | **Essential — fixes the two biggest problems** |
| **Pre-process: strip CSS transform wrappers** | Removes scaling artifacts around tables | **Essential — companion to figure stripping** |
| `-f html-native_divs-native_spans` | Strips `::: {.class}` and `[text]{.class}` markup | **Essential — biggest Pandoc flag improvement** |
| `-t markdown-header_attributes` | Removes `{#id .class}` from headings | **Essential — clean headings** |
| `--wrap=none` | Single-line paragraphs | **Essential — cleaner for processing** |
| `--markdown-headings=atx` | ATX-style headings | **No effect** (already default) |
| All math-related flags | Various math output modes | **No effect** (LaTeX output already default) |
| All table-related output flags | Grid/pipe table output | **No effect** (tables must be parsed first) |

### Updated Recommended Configuration

**Step 1: Pre-process HTML (Python)**
```python
import re
html = open(input_path).read()
html = re.sub(r'<figure[^>]*>', '', html)
html = html.replace('</figure>', '')
html = re.sub(r'<div class="ltx_inline-block[^"]*ltx_transformed_outer[^>]*>', '', html)
html = re.sub(r'<span class="ltx_transformed_inner[^>]*>', '', html)
open(preprocessed_path, 'w').write(html)
```

**Step 2: Pandoc conversion**
```bash
pandoc PREPROCESSED.html \
  -f html-native_divs-native_spans \
  -t markdown-header_attributes \
  --wrap=none \
  --markdown-headings=atx
```

**Step 3: Post-process markdown (optional cleanup)**
```bash
# Strip LaTeXML spacing noise
sed -i 's/\\hspace{0pt}//g' output.md
# Strip HTML comment artifacts
sed -i 's/`<!-- -->`{=html}//g' output.md
# Resolve image URLs (if needed)
sed -i 's|/html/|https://arxiv.org/html/|g' output.md
```

**Why these settings:**
- `<figure>` stripping — fixes tables and figures (Experiment 16, confirmed by isolated table test and GitHub issues #5014, #222)
- `-f html-native_divs-native_spans` — most impactful Pandoc flag (Experiment 13, 35KB savings)
- `-t markdown-header_attributes` — clean headings (Experiment 14)
- `--wrap=none` — essential for pipeline processing (Experiment 2)

### Known Limitations of the Recommended Configuration

1. **Equation alignment artifacts** still present (dash-table wrappers around `$$...$$`). Need regex post-processing.
2. **`\hspace{0pt}` noise** cosmetic but pervasive. Simple sed fix.
3. **Results are specific to Pandoc 3.1.3** and arXiv LaTeXML HTML. Non-arXiv HTML or newer Pandoc versions may behave differently.
4. **Simple table format** has limitations — very wide tables or tables with complex cell content (multi-line) may not render perfectly. For this paper's tables, it works well.
