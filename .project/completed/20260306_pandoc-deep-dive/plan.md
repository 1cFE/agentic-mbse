# Implementation Plan: Pandoc Deep-Dive (Stage 1B)

**Status:** In Progress
**Created:** 2026-02-22 11:22 PST
**Last Updated:** 2026-02-22 11:22 PST

## Source Documents
- **Spec:** `.project/active/pandoc-deep-dive/spec.md`
- **Development Strategy:** `.project/concepts/doc-extraction-development-strategy.md` (Stage 1B, lines 75-93)

## Implementation Strategy

**Phasing Rationale:**
This is a learning test — the findings report is the primary deliverable. Phases are ordered to:
1. Do the discovery work *before* using any reference answers (Phase 1)
2. Acquire test data as a consequence of discovery (Phase 2)
3. Quickly dispose of the PDF-input question (Phase 3 — 5 minutes)
4. Spend the bulk of time on HTML experimentation (Phase 4)
5. Synthesize comparative findings only after all experiments are done (Phase 5)
6. Write code last, informed by evidence (Phase 6)

**Overall Validation Approach:**
- Each phase produces a section in `findings.md` — the report grows incrementally
- Experiments are validated by manual inspection of output quality, not just automated metrics
- Metrics infrastructure (`tests/corpus/metrics.py`) provides quantitative backup for qualitative observations

---

## Phase 1: Structured Source Discovery

### Goal
Starting from ONLY the LL7Q6PSU PDF, discover the arXiv ID and HTML link through whatever means the agent can find. Document every step, every dead end, and the time taken. Then repeat for 2-3 other corpus papers. This is the key deliverable — it directly informs Stage 5 source routing feasibility.

### Prerequisites
- [x] LL7Q6PSU PDF must be in `tests/corpus/pdfs/`. Downloaded via `fusion-tea/scripts/zotero_group_download.py LL7Q6PSU`, renamed to `paischer_2025.pdf`.

### Process (NOT a test stencil — this is a discovery process)

The agent MUST work through this process without using the reference answer:

1. **Extract identifying info from the PDF**: Open the PDF, look for arXiv ID in the text, headers, footers, metadata fields. Document what's found and where.
2. **If not found in PDF text**: Search the web using title and/or authors. Document the search queries tried.
3. **Construct the HTML URL**: Once arXiv ID is found, determine the HTML URL pattern. Verify it exists (HEAD request or fetch).
4. **Record timing**: How long did the whole discovery process take?

Then repeat for 2-3 other corpus papers:
- Try `hawker_2020` (2020, may predate arXiv HTML)
- Try `sparc_overview` (2020, physics paper — likely on arXiv)
- Try `woodruff_2026` (2026, recent — good candidate)

### What to Record in `findings.md`

```markdown
## Phase 1: Structured Source Discovery

### LL7Q6PSU (Primary Test)

**Starting point:** PDF only — `tests/corpus/pdfs/paischer_2025.pdf`
**Goal:** Find arXiv ID and HTML link

**Step 1:** [What was tried]
**Result:** [What happened]
**Time:** [How long]

**Step 2:** [Next thing tried]
...

**Final result:**
- arXiv ID found: [yes/no] — [the ID]
- HTML URL: [the URL]
- HTML exists: [yes/no — verified how?]
- Total discovery time: [X minutes]

### Generalizability Tests

#### hawker_2020
[Same structure — abbreviated]

#### sparc_overview
[Same structure]

#### woodruff_2026
[Same structure]

### Discovery Process Assessment

**Reliable methods:** [What worked consistently]
**Brittle methods:** [What sometimes failed and why]
**Automation feasibility:** [Could this be scripted? What are the hard parts?]
**Recommendation for Stage 5:** [What source routing should do based on this evidence]
```

### Validation

**What We Know Works After This Phase:**
- Whether arXiv ID discovery from PDF is reliable or fragile
- Which corpus papers have arXiv HTML available
- A documented, reproducible discovery method (or documented evidence that it's unreliable)

---

## Phase 2: Test Data Acquisition

### Goal
Download the arXiv HTML for LL7Q6PSU and set up the test data directory. Quick mechanical step.

### Changes Required

- [x] Create `tests/corpus/html/` directory
- [x] Download arXiv HTML for LL7Q6PSU (URL discovered in Phase 1)
- [x] Save as `tests/corpus/html/paischer_2025.html` (328KB)
- [x] LL7Q6PSU PDF already in corpus from Phase 1 prerequisite (`paischer_2025.pdf`)
- [x] Update `papers.jsonl` — added `html_path` and `arxiv_id` fields to existing paischer_2025 entry
- [x] Add `tests/corpus/html/` to `.gitignore`

### Validation

**Manual:**
- [ ] `tests/corpus/html/paischer_2025.html` exists and is non-empty
- [ ] HTML file opens in browser and shows the paper content
- [ ] `papers.jsonl` has an entry with both `pdf_path` and `html_path`

**What We Know Works After This Phase:**
- Both HTML and PDF sources for the same paper are available for comparison

---

## Phase 3: Pandoc PDF Input — Quick Disposition

### Goal
Document that Pandoc 3.1.3 does NOT support PDF as an input format. This resolves FR-4 with a clean, evidence-backed finding in under 5 minutes.

**Discovery already made during planning:** `pandoc --list-input-formats` does not include `pdf`. But the agent should verify this and attempt a conversion to confirm the error behavior.

### Process

- [x] Run `pandoc --list-input-formats` and confirm `pdf` is absent
- [x] Attempt `pandoc --from=pdf` on a corpus PDF and capture the error message
- [x] Check if there's a pandoc PDF reader that requires additional dependencies (web search if needed)
- [x] Record finding in `findings.md`

### What to Record

```markdown
## Phase 3: Pandoc PDF Input

**Finding:** Pandoc 3.1.3 does not support PDF as an input format.

**Evidence:**
- `pandoc --list-input-formats` output: [list — no pdf]
- Attempted conversion error: [exact error message]
- Additional research: [any info about PDF support in other Pandoc versions or via plugins]

**Conclusion:** The development strategy's note that "Pandoc can also read PDFs (poorly)"
is incorrect for Pandoc 3.1.3. PDF→markdown requires pymupdf4llm or Docling.
```

### Validation

**What We Know Works After This Phase:**
- Pandoc PDF input is definitively ruled out with evidence
- No one needs to revisit this question

---

## Phase 4: Pandoc HTML→Markdown Experimentation

### Goal
The bulk of the learning. Run many iterations of Pandoc converting arXiv HTML to markdown, varying configuration each time. Inspect output after each run. Document everything.

### Experiment Design

**Approach:** Change one parameter at a time from a baseline, observe the effect. Then combine the best individual settings into a final config.

**Baseline command:**
```bash
pandoc tests/corpus/html/paischer_2025.html -f html -t markdown -o output.md
```

**Iteration plan (minimum — extend as findings suggest):**

| # | What to change | Command variant | What to look for |
|---|---------------|-----------------|------------------|
| 1 | Baseline | Default flags | Overall quality, structure, math handling |
| 2 | Wrap mode | `--wrap=none` | Line breaks, paragraph formatting |
| 3 | Wrap mode | `--wrap=preserve` | vs baseline and none |
| 4 | Heading style | `--markdown-headings=atx` | Heading formatting (should be ATX for our pipeline) |
| 5 | Math: tex_math_dollars | `-f html+tex_math_dollars` | Does it find LaTeX `$...$` in the HTML? |
| 6 | Math: tex_math_single_backslash | `-f html+tex_math_single_backslash` | `\(...\)` math notation |
| 7 | Math: --mathml flag | `--mathml` | MathML passthrough vs conversion |
| 8 | Math: --katex flag | `--katex` | KaTeX rendering references |
| 9 | Tables: pipe | Default (pipe tables enabled) | Table formatting quality |
| 10 | Tables: grid | `-t markdown+grid_tables-pipe_tables` | Grid tables vs pipe tables |
| 11 | Columns | `--columns=120` | Wide output vs default wrapping |
| 12 | Combined best | Best settings from 1-11 together | Does the combination work? |

This is a minimum — if any iteration reveals a surprising parameter interaction, add more iterations.

### Per-Iteration Process

For EACH iteration:

1. Record the exact command in `findings.md`
2. Run it, save output to `tests/corpus/pandoc-experiments/iter-{N}/`
3. Inspect the output manually — open the markdown and read it:
   - Are headings correct? (count, levels, text)
   - Are tables formatted correctly? (pipe syntax, alignment, spanning)
   - Are equations readable? (LaTeX, MathML, garbled?)
   - Are links preserved?
   - Are images referenced?
   - Is the overall structure sensible?
4. Run `python tests/corpus/metrics.py` on the output for quantitative metrics
5. Record observations in `findings.md` — quote specific output snippets
6. Note what to try next based on what you see

### What to Record

```markdown
## Phase 4: HTML→Markdown Experiments

### Experiment 1: Baseline
**Command:** `pandoc ... -f html -t markdown`
**Output:** `tests/corpus/pandoc-experiments/iter-01/paischer_2025.md`

**Metrics:**
- Chars: [N], Headings: [N], Tables: [N rows], Math symbols: [N]

**Observations:**
- Headings: [quality assessment — quote example]
- Tables: [quality assessment — quote example]
- Equations: [quality assessment — quote example]
- Structure: [overall assessment]

**Verdict:** [Good / Usable / Poor] — [one-line summary]

---

### Experiment 2: --wrap=none
[Same structure]
...
```

### Validation

**Automated:**
- [x] At least 8 experiment iterations completed with output saved (15 iterations completed)
- [x] Metrics computed for each iteration

**Manual:**
- [x] Each iteration has quality observations with quoted snippets in `findings.md`
- [x] At least one "combined best" iteration that merges the best individual findings (iter-14 = best)

**What We Know Works After This Phase:**
- Which Pandoc HTML settings matter and which don't
- Best-known configuration for arXiv HTML→markdown
- Specific quality examples (equations, tables, headings) for each configuration

---

## Phase 5: Cross-Format Comparison & Final Report

### Goal
Side-by-side comparison of Pandoc HTML→markdown vs pymupdf4llm PDF→markdown for the same paper (LL7Q6PSU). Compute metrics, quote output snippets, assess math handling. Write cumulative conclusions and final recommendations.

### Process

- [ ] Run pymupdf4llm on LL7Q6PSU PDF with current best config (from Stage 1A or existing backend)
- [ ] Take the best Pandoc HTML→markdown output from Phase 4
- [ ] Compare side-by-side:
  - Quantitative: metrics from `metrics.py` for both
  - Qualitative: pick 3-5 sections of the paper and quote both outputs side by side
  - Focus areas: equations, tables, headings, figure references, overall readability
- [ ] Write the comparative analysis section of `findings.md`
- [ ] Write final recommendations

### What to Record

```markdown
## Phase 5: Cross-Format Comparison

### Quantitative Comparison

| Metric | Pandoc HTML | pymupdf4llm PDF | Delta |
|--------|-------------|-----------------|-------|
| Characters | | | |
| Headings | | | |
| Table rows | | | |
| Math symbols | | | |
| Figure refs | | | |

### Qualitative Comparison

#### Example 1: Section Heading
**Pandoc HTML:**
> [quoted output]

**pymupdf4llm PDF:**
> [quoted output]

**Assessment:** [which is better and why]

#### Example 2: Equation
[Same structure]

#### Example 3: Table
[Same structure]

### Math Handling Deep-Dive
[Detailed comparison of how each path handles equations — this is a known weakness of PDF extraction]

---

## Conclusions & Recommendations

### When to Use Pandoc HTML
[Evidence-backed recommendation]

### When to Use pymupdf4llm PDF
[Evidence-backed recommendation]

### Recommended Pandoc Configuration for arXiv HTML
```
pandoc -f [best format] -t markdown [best flags]
```
**Why these settings:** [Reference specific experiment iterations]

### Implications for Pipeline (Stage 3)
[How this changes the pipeline design]

### Implications for Source Routing (Stage 5)
[How this informs the JATS → arXiv HTML → PDF quality ordering]
```

### Validation

**Manual:**
- [ ] Comparative table with metrics for both extraction paths
- [ ] At least 3 side-by-side qualitative examples with quoted output
- [ ] Math handling explicitly compared
- [ ] Final recommendation is specific and evidence-backed

**What We Know Works After This Phase:**
- Whether arXiv HTML extraction is actually better than PDF extraction (with numbers)
- The best Pandoc configuration (with evidence)
- Clear guidance for Stages 3 and 5

---

## Phase 6: Updated PandocConverter

### Goal
Evolve `pandoc_backend.py` to support HTML input alongside existing DOCX, using the best configuration discovered in Phases 4-5.

### Test Stencil (Write This First)
```python
# tests/test_pandoc_html.py

def test_pandoc_html_extraction_produces_markdown():
    """Pandoc HTML backend produces non-empty markdown from arXiv HTML."""
    html_path = Path("tests/corpus/html/paischer_2025.html")
    if not html_path.exists():
        pytest.skip("Test corpus HTML not available")

    result = pandoc_backend.extract(html_path, tmp_path / "output")
    assert result.success
    assert result.char_count > 1000


def test_pandoc_html_uses_recommended_config():
    """Pandoc HTML backend uses the configuration from findings."""
    # Verify the subprocess call uses the flags we determined were best
    ...


def test_pandoc_detects_input_format():
    """Backend selects correct --from flag based on file extension."""
    ...
```

### Changes Required

**File:** `src/agentic_mbse/extraction/pandoc_backend.py` (MODIFY)
- [ ] Add input format detection (`.html` → `--from=html+{extensions}`, `.docx` → `--from=docx`)
- [ ] Apply best-discovered Pandoc flags for HTML input (from Phase 4-5 findings)
- [ ] Add code comments referencing specific findings (e.g., "See findings.md Phase 4 Experiment 5")
- [ ] Keep existing DOCX path working (no regressions)

**File:** `tests/test_extraction.py` (MODIFY) or `tests/test_pandoc_html.py` (NEW)
- [ ] Add test for HTML extraction
- [ ] Add test for format detection
- [ ] Add test for recommended config flags

**File:** `src/agentic_mbse/cli/extract_cli.py` (MODIFY — if needed)
- [ ] Add `.html` to recognized extensions for pandoc backend selection

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_extraction.py` — all pass, no regressions
- [ ] New HTML extraction tests pass
- [ ] `uv run ruff check src/ tests/` — clean

**Manual:**
- [ ] Run `agentic-mbse extract tests/corpus/html/paischer_2025.html` — produces markdown output
- [ ] Output quality matches the best configuration from Phase 4

**What We Know Works After This Phase:**
- Pandoc backend handles both DOCX and HTML input programmatically
- Configuration is evidence-backed and documented

---

## Environment Setup

See `CLAUDE.md` for full environment rules. Key commands:
```bash
uv run pytest tests/                    # Run all tests
uv run ruff check src/ tests/           # Lint
uv run ruff format src/ tests/          # Format
python tests/corpus/metrics.py <file>   # Compute extraction metrics
```

Pandoc 3.1.3 is already installed and verified.

---

## Risk Management

- **arXiv HTML download may require handling embedded assets**: If the HTML references external CSS/images, we may need `wget --page-requisites` or similar. Mitigation: try simple `curl` first, escalate if needed.
- **MathML representation may vary between papers**: Our single test paper may not be representative. Mitigation: note this limitation in findings, flag for Stage 5 when more papers are tested.
- **Phase 1 discovery could take too long**: Timebox to 30 minutes per paper. If it's hard, that's a finding.
- **Pandoc version sensitivity**: Our findings are specific to 3.1.3. Mitigation: record version in findings; note if newer versions add capabilities.

---

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-02-22 ~12:15 PST
**Actual Changes:**
- Downloaded `paischer_2025.pdf` from Zotero via `fusion-tea/scripts/zotero_group_download.py` (plan didn't know about this utility)
- Created `findings.md` with full Phase 1 discovery documentation
- Tested 4 papers: paischer_2025 (arXiv, HTML available), woodruff_2026 (arXiv, HTML available), hawker_2020 (not on arXiv), sparc_overview (not on arXiv)

**Issues:**
- Plan referenced Zotero API directly for download but the group returns 404 on public API. Used the `fusion-tea` repo's `zotero_group_download.py` utility instead.
- PDF was downloaded with Zotero's long filename; renamed to `paischer_2025.pdf` to match corpus naming convention.

**Deviations:**
- The plan's Zotero download mechanism assumed direct API access. The existing `fusion-tea` utility worked perfectly.
- Discovery was faster than expected — arXiv IDs are always in the first line of `pdftotext` output for arXiv papers. No need for complex fallback methods.

### Phase 2 Completion
**Completed:** 2026-02-22 ~12:20 PST
**Actual Changes:**
- Created `tests/corpus/html/` directory
- Downloaded `paischer_2025.html` (328KB) from `https://arxiv.org/html/2510.07314v1`
- Added `tests/corpus/html/` to `.gitignore`
- Updated `papers.jsonl` — added `html_path` and `arxiv_id` fields to existing paischer_2025 entry (entry already existed from Stage 1A)

**Issues:** None — straightforward mechanical step.

**Deviations:**
- Plan said to create a new papers.jsonl entry, but paischer_2025 already had one from Stage 1A corpus expansion. Added fields to existing entry instead.

### Phase 3 Completion
**Completed:** 2026-02-22 ~12:30 PST
**Actual Changes:**
- Ran `pandoc --list-input-formats` — confirmed 43 formats, no `pdf`
- Ran `pandoc --from=pdf` — got explicit error: "Unknown input format pdf / Pandoc can convert to PDF, but not from PDF." (exit code 21)
- Tested extension variant (`pdf+raw_attribute`) — same error
- Web searched for community PDF reader plugins — none exist
- Wrote Phase 3 section in `findings.md` with all evidence

**Issues:** None — this was the expected quick disposition.

**Deviations:**
- Also tested extension syntax variant (`-f pdf+raw_attribute`) to be thorough — same result.
- Added an "Implication for spec FR-4" note in findings explaining that the cross-format comparison in Phase 5 will be 2-way (Pandoc HTML vs pymupdf4llm PDF) rather than 3-way, since Pandoc PDF is impossible.

### Phase 4 Completion
**Completed:** 2026-02-22 ~13:00 PST
**Actual Changes:**
- Ran 15 experiment iterations (plan called for 12 minimum)
- Created `tests/corpus/pandoc-experiments/iter-{01..15}/` with output, metrics, and command logs
- Created `tests/corpus/run_pandoc_experiments.sh` experiment runner script
- Wrote comprehensive Phase 4 section in `findings.md` with per-iteration observations, cross-cutting findings, recommended configuration, and known limitations

**Key Findings:**
- **Best config:** `-f html-native_divs-native_spans -t markdown-header_attributes --wrap=none --markdown-headings=atx`
- **Math conversion is excellent:** MathML → LaTeX `$...$` / `$$...$$` works reliably. This is the biggest advantage of HTML over PDF extraction.
- **Tables don't convert:** All 5 data tables pass through as raw HTML. arXiv's `<figure>`-wrapped, CSS-scaled tables can't be parsed by Pandoc.
- **Most flags have no effect:** tex_math_dollars, tex_math_single_backslash, grid_tables, markdown-headings=atx all change nothing because Pandoc already defaults to the desired behavior.
- **Stripping native_divs/native_spans is the most impactful setting:** 35KB savings, removes all `::: {.class}` and `[text]{.class}` wrappers.

**Issues:**
- `python` not found on system — used `python3` for metrics computation.
- The metrics module counts unique Unicode math symbols, not LaTeX commands, so the "math_symbol_count" metric understates the math quality of the HTML→markdown path (which preserves LaTeX notation).

**Deviations:**
- Added 3 extra iterations (13-15) beyond the plan's 12, because experiments 1-12 showed that the biggest improvement wasn't from any planned flag, but from disabling native_divs/native_spans (an extension discovered during the process).
- Added iter-16 after user review flagged tables as surprising. Root cause analysis revealed `<figure>` wrappers block Pandoc's table parser. Simple HTML pre-processing (strip `<figure>` tags and CSS transform wrappers) fixes both tables AND figures — a major finding that changes the recommended configuration.
- Did not run `metrics.py` comparison mode between iterations — used the raw metrics JSON for comparison instead. The `compare.py` tool is designed for baseline vs current comparison on the same document, not cross-configuration comparison.

### Phase 5 Completion
**Completed:** [Timestamp]
**Actual Changes:** [What actually changed]
**Issues:** [Problems encountered and solutions]
**Deviations:** [How this differed from plan and why]

### Phase 6 Completion
**Completed:** [Timestamp]
**Actual Changes:** [What actually changed]
**Issues:** [Problems encountered and solutions]
**Deviations:** [How this differed from plan and why]

---

**Status**: Draft → In Progress → Complete
