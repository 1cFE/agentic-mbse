# Concept: PDF Extraction v2 — From 2.68/5 to Shippable in 3 Days

**Author:** Reid Westwood
**Date:** 2026-02-06
**Status:** Concept
**Branch:** pdf-extract

---

## Situation

We have three converging information streams about PDF extraction quality:

| Stream | What it tells us | Key number |
|--------|-----------------|------------|
| **Pipeline evaluation** (7 docs) | Current automated extraction is usable but weak on tables, headers, and equations | **2.68/5 overall** |
| **Agent manual comparison** (2237, 7 pages) | Targeted per-page re-extraction via vision/Docling yields +79% quality at $0.31/page | **2.07 → 3.71** |
| **External research** (64 sources) | ML-based table extraction (GMFT, TableFormer) outperforms rule-based by 20-30pp; custom header detection and post-processing can solve most remaining issues | **93.6% table accuracy** (Docling) vs 67.9% (Tabula) |

The current pipeline's weaknesses are well-characterized:

| Problem | Severity | Root Cause | Docs Affected |
|---------|----------|-----------|---------------|
| Headers as bold text | CRITICAL | pymupdf4llm font-size heuristic fails on bold-same-size headers | 4/7 (empty index) |
| Tables as plain text | CRITICAL | `table_strategy="lines_strict"` needs visible borders | 6/7 |
| Page number artifacts | HIGH | No header/footer filtering | 7/7 |
| Equation garbling | MEDIUM | Math fonts use private Unicode areas | 3/7 |
| Absolute image paths | MEDIUM | pymupdf backend lacks path rewrite | 2/7 |
| Ligature failures | MEDIUM | Incomplete ToUnicode CMaps | 1/7 (199 occurrences) |

**Goal:** Within 3 days, ship the best version we can with `agentic-mbse`. Not perfect — shippable. Target: **3.5+/5 overall** on the same 7-document corpus.

---

## What the Three Streams Teach Us

### From the pipeline evaluation: the cascade of header failure

The single most damaging defect is headers rendering as `**1 Introduction**` instead of `## 1 Introduction`. This isn't just a cosmetic issue — it **cascades**:

```
Headers as bold → Index parser finds 0 sections → INDEX.md is empty
→ read_section() can't navigate → AI agents can't find content
→ The entire document intelligence layer is broken
```

For 4 of 7 documents, the extraction produced a `full_document.md` that is essentially a wall of text with no navigable structure. This is the first thing to fix and the easiest — it's a regex post-processor.

### From the agent comparison: surgical escalation works, but has limits

The manual per-page experiment revealed a clear pattern:

| Scenario | Result | Implication |
|----------|--------|-------------|
| Simple tables (building costs, DEC costs) | Vision: 5/5 table fidelity | VLM excels at well-structured tables |
| Dense numerical tables (material properties, radial build) | Vision: 2-3/5, **hallucinated values** | VLM unreliable for dense data — cross-validation needed |
| Equations (LCOE) | Vision: 5/5 equation quality | VLM is the only thing that works for equations |
| Docling on tables (page 40) | Docling: 5/5 table fidelity | Docling is best when it works — 33-row perfect table |

**Key insight:** The agent mostly skipped Tier 2 (Docling) and went straight to Tier 3 (vision). When Docling did work (page 40), it produced the best result. This suggests the skill's escalation logic is wrong — **Docling should be the preferred table extractor, not vision.**

**Key risk:** Vision hallucinated wrong numbers on page 18 (radial build table). For a costing tool in nuclear fusion engineering, wrong numbers are worse than garbled text. This means we can't blindly trust VLM table extraction for quantitative data.

### From the research: the answers exist, we just need to wire them up

The research identified specific, code-ready solutions for each failure mode:

| Problem | Best Solution | Effort | New Dependency |
|---------|--------------|--------|----------------|
| Headers as bold | Custom `hdr_info` callback (bold + numbering regex) | Small | None |
| Headers as bold (fallback) | Post-processing bold→`##` promotion | Trivial | None |
| Borderless tables | **GMFT** (Table Transformer on PubTables-1M) | Medium | `gmft` (~270MB model) |
| Borderless tables (lighter) | pymupdf4llm `table_strategy` cascade | Small | None |
| Page artifacts | Regex strip + cross-page deduplication | Small | None |
| Ligatures | `ftfy` + dictionary reconstruction | Small | `ftfy` (tiny) |
| Equations | UniMERNet / Surya LaTeX OCR | Large | Heavy models |
| Image paths | String replacement (already done for Docling) | Trivial | None |

**Critical prioritization:** GMFT is 270MB of models for dramatically better tables. Equation OCR requires 500MB+ of models for a problem that affects 3/7 docs. **Tables first, equations later.**

---

## Strategy: Three-Layer Pipeline with Automated Quality Gates

The pipeline has three layers, each progressively more expensive and more powerful. **Automated quality detection between layers** decides what needs escalation — not the user, not a blanket flag.

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 1: Deterministic Post-Processing         free, <1s/page  │
│   pymupdf4llm + header promotion + artifact removal + ligatures │
│                                                                 │
│   Quality gate: detect remaining problems                       │
│   ├── Tables without pipe delimiters?  → escalate to Layer 2    │
│   ├── chr(0xFFFD) clusters?            → tag as equation region │
│   └── Everything else                  → done                   │
├─────────────────────────────────────────────────────────────────┤
│ Layer 2: ML Table Extraction (GMFT)     free, ~1.4s/page, opt  │
│   Table Transformer on detected table regions                   │
│                                                                 │
│   Quality gate: detect what GMFT couldn't fix                   │
│   ├── Empty/malformed DataFrames?      → escalate to Layer 3    │
│   ├── Equation regions still garbled?  → escalate to Layer 3    │
│   └── Tables reconstructed             → done                   │
├─────────────────────────────────────────────────────────────────┤
│ Layer 3: AI-Assisted Repair (claude -p)   $$, ~15s/region, opt │
│   Render page → send image + broken markdown → get fixed output │
│   Cross-validate numbers against Layer 1+2 before accepting     │
└─────────────────────────────────────────────────────────────────┘
```

### Layer 1: Deterministic Post-Processing (free, no new deps)

Add a `postprocess.py` module to `src/agentic_mbse/extraction/` that cleans up pymupdf4llm output. Pure function: `markdown_in → markdown_out`. No ML, no external tools, no network. Runs in milliseconds.

**Steps in order of cascading impact:**

```
Raw pymupdf4llm output
    │
    ├── 1. Header promotion: **N.N Title** → ## N.N Title
    │      (Fixes: empty indexes for 4/7 docs)
    │
    ├── 2. Page number stripping: bare \d{1,4} on own line
    │      (Fixes: 16-66 artifacts per doc, all 7 docs)
    │
    ├── 3. Running header/footer removal: cross-page dedup
    │      (Fixes: title repeated every 2 pages, 3/7 docs)
    │
    ├── 4. Image path normalization: absolute → relative
    │      (Fixes: non-portable markdown, 2/7 docs)
    │
    ├── 5. Ligature repair: ftfy + dictionary
    │      (Fixes: fi→? failures, 1/7 docs severely)
    │
    └── 6. Figure caption promotion: ![](img) + "Figure N:" → ![Figure N: ...](img)
           (Accessibility, all docs)
```

**Additionally, upstream in pymupdf_backend.py:**

- Pass a custom `hdr_info` callback that uses bold flag + section numbering regex instead of font-size heuristics
- Try `table_strategy="lines"` before falling back to `"lines_strict"` (catches more tables, zero cost)

**Expected impact:** 2.68 → ~3.2-3.4. Fixes headers, fixes indexing cascade, cleans text. Tables remain the weak point.

### Layer 2: ML Table Extraction (GMFT, optional dependency)

GMFT wraps Microsoft's Table Transformer (DETR-based, trained on PubTables-1M — 947K scientific tables). It:
- Requires no GPU
- Installs with `pip install gmft`
- Processes at ~1.4s/page, ~1.2s/table
- Outputs Pandas DataFrames → markdown pipe tables
- Handles borderless tables (trained on PubMed Central papers)

**Integration approach:**

```
Layer 1 output (post-processed markdown)
    │
    ├── Detect pages likely to have tables
    │   (heuristic: lines with aligned whitespace columns, or "Table N:" captions)
    │
    ├── Run GMFT on candidate pages
    │   ├── AutoTableDetector → find table regions
    │   └── AutoTableFormatter → extract to DataFrames
    │
    └── Replace garbled table regions in markdown with GMFT pipe tables
```

**Why GMFT over Docling for tables:**
- GMFT is 270MB, focused solely on tables. Docling is 500MB+ with broader scope.
- GMFT runs in-process (no MCP server, no subprocess). Docling needs the MCP server or the heavyweight subprocess-with-timeout pattern.
- GMFT's training data (PubTables-1M) is 94.7% scientific papers — exactly our use case.
- Docling remains valuable for other things (layout analysis, image captioning) but for *just tables*, GMFT is more surgical.

**Expected impact:** Tables from 2.00 → ~3.5-4.0. Combined with Layer 1, overall ~3.5-4.0.

### Layer 3: AI-Assisted Repair via `claude -p` (opt-in, $$)

This is the crucial layer the v1 concept was missing. The agent comparison experiment proved that vision-based repair works (+79% quality) — the question was never *if* it works but *how to use it safely*. The answer: **automated detection of what's broken, targeted repair of those regions only, and cross-validation before accepting changes.**

**This generalizes the existing `table_repair.py` into a broader "AI repair" pass.**

#### What triggers Layer 3

Quality detectors run after Layers 1+2 and produce a list of `RepairRequest` objects:

```python
@dataclass
class RepairRequest:
    page_num: int           # 0-indexed page in the PDF
    region_type: str        # "table" | "equation" | "structure"
    markdown_lines: tuple[int, int]  # line range in full_document.md
    original_text: str      # what Layers 1+2 produced (for cross-validation)
    confidence: float       # how confident we are this needs repair (0-1)
```

**Detection heuristics:**

| Problem | Detection | Confidence |
|---------|----------|------------|
| Tables that GMFT couldn't parse | GMFT returned empty DataFrame for detected table region | 0.9 |
| Tables pymupdf4llm garbled (no GMFT available) | Aligned whitespace columns without pipe delimiters, adjacent to "Table N:" caption | 0.8 |
| Garbled equations | Clusters of `chr(0xFFFD)` or bracket-soup patterns like `_[C][AC]_` | 0.9 |
| Ambiguous structure | Bold lines matching numbered section patterns that the header promoter wasn't confident about (e.g., unusual numbering schemes) | 0.5 |

#### How repair works

For each `RepairRequest`:

1. **Render the page** as a 200 DPI PNG (reuse `extract_page.py --mode image`)
2. **Build a focused prompt** that includes:
   - The page image
   - The current (broken) markdown for that region
   - A specific ask: "Fix this table as a markdown pipe table" / "Convert this equation to LaTeX" / "Identify the correct heading structure"
3. **Call `claude -p`** with the prompt (single turn, not multi-turn agent)
4. **Cross-validate** the output:
   - For tables: extract all numbers from both the original and repaired markdown. If any number in the original (even garbled) appears differently in the repair, **flag it** rather than silently accepting
   - For equations: accept the LaTeX (no deterministic baseline to compare against)
   - For structure: accept the heading hierarchy
5. **Splice** the repaired region back into `full_document.md`

#### Cross-validation: the key safety mechanism

The agent experiment showed that vision hallucinated wrong values on page 18 (radial build table — wrong inner/outer radii). For nuclear fusion costing data, wrong numbers are worse than garbled text.

Cross-validation prevents this:

```python
def cross_validate_table(original: str, repaired: str) -> tuple[bool, list[str]]:
    """Check if numerical values are preserved between original and repaired tables.

    Returns (accept, warnings) where accept=True means safe to use,
    and warnings lists any discrepancies found.
    """
    original_numbers = extract_numbers(original)  # all numeric tokens
    repaired_numbers = extract_numbers(repaired)

    # Numbers present in original but different/missing in repair
    discrepancies = []
    for num in original_numbers:
        if num not in repaired_numbers:
            discrepancies.append(f"Number {num} in original but not in repair")

    if discrepancies:
        return False, discrepancies  # Flag for human review, keep original
    return True, []
```

When cross-validation fails, the pipeline:
- Keeps the Layer 1+2 output (garbled but numerically correct)
- Inserts a marker: `<!-- AI repair flagged discrepancy on page N: [details] -->`
- Reports the discrepancy in `summary.json`

This means the pipeline **never silently introduces wrong numbers.**

#### CLI interface

```bash
# Default: Layers 1+2 only (free, fast)
agentic-mbse extract document.pdf

# With AI repair: Layers 1+2+3 (costs $$, slower, better quality)
agentic-mbse extract document.pdf --enhance

# AI repair with cost limit
agentic-mbse extract document.pdf --enhance --max-repair-pages 20

# AI repair for tables only (skip equations/structure)
agentic-mbse extract document.pdf --enhance --repair tables
```

**Expected cost for `--enhance`:** Based on the agent experiment ($0.31/page with multi-turn Sonnet), a single-turn `claude -p` call should be ~$0.03-0.08/page. For a 65-page document with ~15 problem pages, total Layer 3 cost: **$0.45-$1.20.** Acceptable for high-value reference documents.

#### Why this is different from the agent experiment

| | Agent experiment | Layer 3 pipeline |
|---|---|---|
| Decision-making | Agent decides what to extract | Automated detection decides |
| Turns per page | 9-21 turns ($0.18-0.44/page) | Single turn ($0.03-0.08/page) |
| Cross-validation | None (trusted VLM output) | Automated number comparison |
| Hallucination handling | Not handled (page 18 failed) | Flagged and rejected |
| Scope | 7 hand-picked pages | All detected problem regions |
| Reproducibility | Low (agent makes different choices) | High (deterministic detection + fixed prompts) |

---

## What We Deliberately Defer

| Item | Why Defer | When |
|------|----------|------|
| Dedicated equation OCR (UniMERNet/Surya) | Heavy models (~500MB+), complex integration. Layer 3's `claude -p` vision handles equations well enough (agent experiment: 5/5 on LCOE equation). Dedicated OCR is only needed if `--enhance` cost is prohibitive for math-heavy corpora. | v3 |
| Full Docling MCP deployment | Already spec'd separately (`.project/active/pdf-skill-deployment/`). Good design doc exists. Orthogonal to extraction quality. | Separate work item |
| MinerU / Marker integration | Full pipeline replacements. Too heavy for a 3-day sprint. Worth evaluating as Layer 1 alternatives later. | v3 evaluation |
| DOCX extraction improvements | No evaluation data yet. PDF is the priority. | After PDF v2 ships |
| Multi-page table stitching | Tables spanning page breaks need cross-page context. Layer 3 can handle individual pages but not stitch them. | v3 |

---

## 3-Day Execution Plan

### Day 1: Layer 1 — Post-Processing Pipeline + pymupdf4llm Upstream Fixes

**Morning — postprocess.py module:**
1. Create `src/agentic_mbse/extraction/postprocess.py`
2. Implement `promote_bold_headers(md: str) -> str` — regex to convert `**N.N Title**` patterns to `## N.N Title` with depth-aware heading levels
3. Implement `strip_page_numbers(md: str) -> str` — remove bare page numbers between blank lines
4. Implement `strip_running_headers(md: str, threshold: float = 0.5) -> str` — cross-page deduplication of repeated short lines
5. Implement `normalize_image_paths(md: str, images_dir: Path) -> str` — absolute→relative
6. Implement `repair_ligatures(md: str) -> str` — common ligature dictionary + context reconstruction
7. Implement `promote_figure_captions(md: str) -> str` — `![](img)` + adjacent `Figure N:` → `![Figure N: ...](img)`
8. Implement `postprocess(md: str, images_dir: Path | None = None) -> str` — chains all steps

**Afternoon — pymupdf_backend.py upgrades + quality detection:**
1. Add custom `hdr_info` callback using bold flag + section numbering regex
2. Change default `table_strategy` to `"lines"` (less strict, catches more tables)
3. Wire `postprocess()` into the extraction pipeline (call after `to_markdown()`)
4. Implement `detect_problems(md: str, pdf_path: Path) -> list[RepairRequest]` — the quality gate that identifies what still needs fixing after Layer 1
5. Test against the 7-document corpus — measure score delta

**Evening — index.py improvements:**
1. Add appendix letter-numbering pattern (`A`, `B.1`, etc.)
2. Add bold-header fallback pattern to `parse_sections()` (defense-in-depth: if post-processing missed a header, the index parser can still catch bold patterns)

**Exit criteria for Day 1:** Post-processed output scores 3.2+ on the 7-doc corpus. All 7 documents produce non-empty INDEX.md files. `detect_problems()` correctly identifies remaining table/equation issues.

### Day 2: Layers 2+3 — GMFT Table Extraction + AI Repair

**Morning — GMFT integration (Layer 2):**
1. Add `gmft` as an optional dependency (`[extract-tables]` or bundled with `[extract]`)
2. Create `src/agentic_mbse/extraction/table_extraction.py`
3. Implement `extract_tables_from_page(pdf_path, page_num) -> list[DataFrame]`
4. Implement `tables_to_markdown(tables: list[DataFrame]) -> list[str]`
5. Implement `replace_tables_in_markdown(md: str, pdf_path: Path) -> str` — the orchestrator that detects table regions, runs GMFT, and splices results

**Afternoon — AI repair layer (Layer 3):**
1. Generalize `table_repair.py` into `src/agentic_mbse/extraction/ai_repair.py`
2. Implement `RepairRequest` dataclass and quality detection refinements
3. Implement `repair_region(request: RepairRequest, pdf_path: Path) -> str | None` — renders page image, builds focused prompt, calls `claude -p`, returns repaired markdown
4. Implement `cross_validate_numbers(original: str, repaired: str) -> tuple[bool, list[str]]` — extracts numerical tokens from both and flags discrepancies
5. Implement `repair_document(md: str, pdf_path: Path, requests: list[RepairRequest]) -> str` — orchestrates repair of all detected problem regions, splicing results back

**Evening — wire into pipeline + benchmark:**
1. Integrate GMFT and AI repair into the extraction orchestrator
2. Build a minimal benchmark script: run extraction on the 7-doc corpus at each layer level
3. Run the benchmark at Layers 1, 1+2, and 1+2+3. Measure score deltas and costs.
4. Handle edge cases: GMFT failures (fall back to Layer 3), claude CLI not found (skip Layer 3 gracefully), cross-validation rejections (keep Layer 1+2 output with marker comment)

**Exit criteria for Day 2:** Table scores at 3.5+ with GMFT. `--enhance` produces 4.0+ on pages the agent comparison tested. Cross-validation catches at least one hallucination case (test against the page 18 scenario). Pipeline degrades gracefully when deps are missing.

### Day 3: Integration, Skill Update, Ship

**Morning — CLI integration:**
1. Wire the full 3-layer pipeline into `agentic-mbse extract` CLI command
2. Add flags: `--enhance` (enable Layer 3), `--max-repair-pages N`, `--repair tables|equations|all`
3. Add `--no-tables` to skip GMFT (for speed or when not installed)
4. Update `summary.json` to include per-layer metadata: what was detected, what was repaired, cross-validation results, cost
5. Run full end-to-end test: `agentic-mbse extract <each of 7 PDFs>` and `agentic-mbse extract --enhance <2237>`

**Afternoon — skill and evaluation:**
1. Update `.claude/skills/pdf-analysis/SKILL.md` to reference the improved backend — the skill should try Layer 1+2 first, then use its interactive capabilities (Docling MCP, vision) only for what Layers 1+2 couldn't fix
2. Update `extract_page.py` to use the post-processing pipeline for `--mode markdown`
3. Run the formal evaluation: score all 7 documents at each layer, write updated evaluation report
4. Compare v1 vs v2 scores side-by-side, including `--enhance` results

**Evening — ship:**
1. Update `pyproject.toml` dependencies
2. Run existing test suite (`uv run pytest tests/`)
3. Fix any broken tests
4. Commit and prepare PR

**Exit criteria for Day 3:** Overall score 3.5+ on the corpus (Layers 1+2). 4.0+ with `--enhance`. `agentic-mbse extract` works end-to-end. Tests pass. PR ready.

---

## Architecture Decision: Where Post-Processing Lives

The post-processing pipeline could live in several places:

| Location | Pros | Cons |
|----------|------|------|
| Inside `pymupdf_backend.py` | Self-contained, pymupdf-specific | Docling output also benefits from some fixes |
| Separate `postprocess.py` module | Reusable across backends, testable in isolation | Extra module to maintain |
| Inside the CLI orchestrator | Applied once, after any backend | Mixes orchestration with transformation |

**Decision: Separate `postprocess.py` module.** The post-processing steps are backend-agnostic (headers, page numbers, ligatures exist in any extraction). The orchestrator in `__init__.py` calls `postprocess()` after whichever backend succeeds. This also lets the `extract_page.py` skill script import and use the same pipeline.

```
pymupdf_backend.extract()       →  raw markdown
    or
docling_backend.extract()       →  raw markdown
    ↓
postprocess.postprocess(md)     →  cleaned markdown        [Layer 1]
    ↓
detect_problems(md, pdf_path)   →  list[RepairRequest]     [Quality Gate]
    ↓
[if gmft available]
table_extraction.replace_tables(md, pdf_path)  →  tables fixed    [Layer 2]
    ↓
[if --enhance]
ai_repair.repair_document(md, pdf_path, remaining_requests)       [Layer 3]
    ├── render problem pages as images
    ├── call claude -p with focused prompts
    ├── cross-validate numbers
    └── splice repairs (or flag discrepancies)
    ↓
write full_document.md
    ↓
index.generate_index()          →  INDEX.md (works because headers are proper)
```

---

## Architecture Decision: GMFT as Optional Layer

GMFT adds ~270MB of model weight. Not everyone needs it. The extraction should work without it (just with lower table quality).

```python
# In the pipeline orchestrator:
try:
    from agentic_mbse.extraction.table_extraction import replace_tables_in_markdown
    md_text = replace_tables_in_markdown(md_text, input_path)
except ImportError:
    pass  # GMFT not installed, tables stay as-is from pymupdf4llm
```

**Dependency structure:**
- `agentic-mbse` (base): no extraction deps
- `agentic-mbse[extract]`: `pymupdf4llm` — Tier 1 extraction + post-processing
- `agentic-mbse[extract-full]`: `pymupdf4llm` + `gmft` + `docling` — all backends

---

## How the Skill Evolves

The interactive skill and the CLI pipeline are converging, not diverging. The three layers in the CLI map directly onto what the skill does interactively:

| CLI Layer | Skill Equivalent | Key Difference |
|-----------|-----------------|----------------|
| Layer 1: postprocess.py | Tier 1: pymupdf4llm | CLI applies post-processing automatically; skill currently uses raw output |
| Layer 2: GMFT | (none currently) | New capability — skill should use it too |
| Layer 3: `claude -p` automated repair | Tier 2+3: Docling MCP + vision | CLI uses headless single-turn; skill uses interactive multi-turn with the user |

**The skill's unique value narrows but deepens.** After v2, the CLI handles ~90% of content well. The skill becomes the tool for the remaining ~10% — and for those cases, interactive multi-turn with a human in the loop is genuinely better than automated single-turn `claude -p`:

1. **Cross-validation with user judgment** — when automated cross-validation flags a discrepancy ("Layer 3 says this number is 4.2, Layer 1 says 4.7"), the skill can show both to the user and ask
2. **Complex multi-page table stitching** — tables spanning page breaks need contextual judgment about where the continuation is
3. **Diagram/figure interpretation** — "what does figure 3 show?" requires genuine visual understanding, not extraction
4. **Domain-specific validation** — "does this LCOE equation look right for a fusion plant?" is beyond extraction

**Skill update for v2:** The skill should use the improved backend as its Tier 1 (pymupdf4llm + postprocess + GMFT), then only escalate to Docling MCP or vision for what's still broken. This inverts the current escalation: instead of "start bad, escalate to good," we "start good, escalate for edge cases."

### The `--enhance` flag and the skill are complementary, not redundant

```
                            CLI: agentic-mbse extract
                            ├── Layers 1+2: free, fast, automated
                            └── --enhance (Layer 3): $$, automated, single-turn
                                └── Good for: batch processing reference docs

                            Skill: /pdf-analysis
                            ├── Uses improved Layers 1+2 as its base
                            └── Interactive escalation: $$, multi-turn, user-guided
                                └── Good for: targeted analysis, validation, exploration
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| GMFT fails on some table layouts | Medium | Medium | Layer 3 AI repair catches what GMFT misses; graceful fallback chain |
| Post-processing regex matches false positives (e.g., bold text that isn't a header) | Medium | Low | Require numbered section pattern + bold to trigger promotion; test against corpus |
| GMFT model download blocks CI/testing | Low | Medium | Mock GMFT in tests; make it optional |
| 3-day timeline is too aggressive | Medium | Medium | Layers ship independently: L1 alone is valuable, L2 adds tables, L3 adds polish. Each layer works without the next. |
| Running header detection removes legitimate content | Low | High | Conservative threshold (>50% page frequency); opt-out flag |
| Layer 3 `claude -p` hallucination introduces wrong numbers | Medium | **High** | Cross-validation: compare numbers between Layer 1+2 output and Layer 3 repair. Reject repairs with discrepancies, keep original + flag. **This is the critical safety mechanism.** |
| `claude` CLI not available for Layer 3 | Medium | Low | Layer 3 is opt-in (`--enhance`). Pipeline gracefully skips it with a message. Layers 1+2 still produce good output. |
| Layer 3 cost surprises users | Low | Medium | Report estimated cost before running (`--enhance` shows "~$X for N problem pages, proceed?"), enforce `--max-repair-pages` default |
| Quality detection has false negatives (misses problems) | Medium | Low | Undetected problems stay as Layer 1+2 output, which is already an improvement over v1. Detection can be refined iteratively. |

---

## Success Metrics

| Metric | v1 (current) | v2 L1 (actual) | v2 L1+L2 (target) | v2 `--enhance` (target) |
|--------|-------------|----------------|-----------|----------------|
| Overall quality score | 2.68/5 | ~3.3/5 | 3.5/5 | 4.0+/5 |
| Markdown structure | 2.64/5 | ~3.5/5 | 3.5/5 | 4.0/5 |
| Index quality | 2.43/5 | ~3.8/5 | 4.0/5 | 4.0/5 |
| Image extraction | 3.64/5 | ~3.6/5 (unchanged) | 4.0/5 | 4.0/5 |
| Table extraction | 2.00/5 | ~2.0/5 (unchanged) | 3.5/5 | 4.0+/5 |
| Equation handling | ~1.5/5 | ~1.5/5 (unchanged) | ~2.0/5 (markers) | 4.0/5 (LaTeX via vision) |
| Docs with non-empty INDEX.md | 3/7 | **7/7** | 7/7 | 7/7 |
| Cost per 65-page document | $0 | $0 | $0 | $0.45-$1.20 |
| New required dependencies | 0 | 0 | 0 | 0 |
| New optional dependencies | 0 | 0 | 1 (gmft) | 1 (gmft) + `claude` CLI |
| Cross-validation catches | n/a | n/a | n/a | >0 (proves safety mechanism works) |

---

## v2 Layer 1 Results (2026-02-06)

Layer 1 postprocessing pipeline implemented and tested against the 7-document corpus.

### What was implemented

1. **`postprocess.py`** — 8 pure functions: `promote_bold_headers`, `promote_plain_headers`, `clean_header_artifacts`, `strip_page_numbers`, `strip_running_headers`, `normalize_image_paths`, `repair_ligatures`, `promote_figure_captions`, plus `postprocess` orchestrator.
2. **`pymupdf_backend.py`** — Custom `hdr_info` callback (bold + numbered section regex), `table_strategy="lines"`, wired postprocess into extraction pipeline.
3. **`index.py`** — Added appendix letter-numbering pattern (Format D: `## A.1 Title`).
4. **`test_postprocess.py`** — 57 unit tests, all passing.

### Per-document results

| Doc | ID | v1 Sections | v2 Sections | v1→v2 Key Improvements |
|-----|-----|-------------|-------------|------------------------|
| Handley et al. (2021) | 2232 | 7 | 15 | Headers cleaned (removed redundant bold), more subsections detected |
| Araiinejad & Shirvan (2025) | 2233 | 4 | 6 | Running headers removed (11 instances), ~2KB artifacts eliminated |
| FIA Global Fusion (2025) | 2235 | **0** | **31** | Plain-text headers now promoted — was completely broken, now fully indexed |
| FAS Market Report | 2236 | 62 | 70 | TOC page artifacts cleaned from headers |
| LANL Cost Study | 2237 | 50 | 54 | TOC page artifacts cleaned, appendix sections now detected |
| Lampe & Manheimer (1998) | 2238 | 10 | 13 | Bold page numbers stripped (12 of 13) |
| Eester et al. (2026) | 2241 | 15 | 15 | No change needed — already clean |

### What worked

1. **Bold header promotion** — Fixed the cascading failure for 4/7 docs. The `hdr_info` callback catches bold+numbered spans at extraction time; the regex catches anything the callback missed.
2. **Plain-text header promotion** — Fixed 2235 (0→31 sections) by detecting standalone `N Title` patterns between blank lines, with TOC rejection (dot leaders, trailing page numbers).
3. **Running header removal** — Correctly removed 11 whitespace-padded journal running headers from 2233. Whitespace collapse normalization was key.
4. **Bold page number stripping** — Caught `**N**` standalone lines that the plain number regex missed.
5. **Header artifact cleanup** — Removed `** **N` TOC page number remnants and redundant `## **N Title**` bold markers.
6. **All image paths relative** — 7/7 docs, zero absolute paths.

### What didn't work / remaining issues

1. **Scanned PDF header noise (2238)** — OCR-extracted equation fragments get classified as section headers because they start with numbers. The `hdr_info` callback sees bold+number→header, but in scanned math papers, bold-numbered equation fragments are common. ~31 of 46 headers in 2238 are noise. **Fix: Layer 2/3, or a "minimum header text length" heuristic.**
2. **Page-number-prefixed fake headers (2236, 2237)** — Some pages have bold text that starts with a page number (e.g., bold "18 Fusion Developer...") where 18 is a page number, not a section number. This creates `## 18 Fusion Developer...` which looks like section 18. **Hard to distinguish programmatically without knowing the document's actual numbering scheme.**
3. **Table rows as headers (2233)** — Cost accounting table rows like "20 Direct Costs" match the numbered section pattern. Need table-context awareness to reject these.
4. **Tables unchanged** — Still at 2.0/5. Need GMFT (Layer 2) for table improvement.
5. **Equations unchanged** — Still garbled in math-heavy papers. Need Layer 3 vision for reconstruction.

### Revised Layer 2/3 priority

The Layer 1 results shift the priority ranking:

| Priority | Item | Rationale |
|----------|------|-----------|
| **1** | GMFT table extraction (Layer 2) | Tables are now the biggest quality gap (2.0/5 vs 3.5/5 structure). 6/7 docs would benefit. |
| **2** | Header noise rejection heuristic | Affects 2238 badly, 2233/2236 moderately. Simple: reject `## ` headers shorter than 8 chars or containing `=`, `+`, `[`, `]` operators. |
| **3** | AI repair for equations (Layer 3) | Only 3/7 docs have equations. Vision-based LaTeX reconstruction via `--enhance`. |
| **Defer** | TOC detection/removal | Affects 2236/2237 TOC pages. Complex: requires identifying page ranges that are TOC vs content. Low ROI vs other fixes. |

---

## Relationship to Existing Work Items

| Work Item | Status | Relationship to This Concept |
|-----------|--------|------------------------------|
| Document Extraction spec | Implemented (73a20d5) | This concept is the quality improvement pass on top of that implementation |
| PDF Skill Deployment spec | Draft | Orthogonal — that handles Docling MCP setup during `init`. This concept improves the extraction quality regardless of Docling availability |
| PDF Skill Deployment design | Draft | No conflicts. The adaptive SKILL.md work in that design complements this concept's skill improvements |
| Evaluation report | Complete | This concept directly addresses every issue identified in the evaluation |

---

## Decision Points for Review

1. **GMFT vs pymupdf4llm table_strategy cascade only?** — GMFT gives dramatically better results but adds a 270MB dependency. The cascade is free but has a lower ceiling. **Recommendation: Both.** Cascade is Layer 1 (free improvement), GMFT is Layer 2 (major improvement). Pipeline tries GMFT first, falls back to cascade.

2. **Should `--enhance` be opt-in or default?** — Layer 3 costs money and requires `claude` CLI. **Recommendation: Opt-in.** Users who want free/fast extraction get Layers 1+2 by default. Users who want maximum quality for important documents use `--enhance`. The flag should report estimated cost before proceeding.

3. **Equation handling: marker vs Layer 3 vision?** — With Layer 3 in the pipeline, equations become a natural `--enhance` target. The agent experiment showed 5/5 quality on the LCOE equation via vision. **Recommendation: Equations get markers at Layers 1+2 (zero cost), and get LaTeX reconstruction via Layer 3 with `--enhance`.** This is better than the v1 concept's "defer entirely" approach.

4. **Cross-validation strictness?** — When Layer 3 produces a number that doesn't match Layer 1+2, we could (a) reject and keep original, (b) keep repair but add a warning comment, or (c) ask the user. **Recommendation: (a) reject by default.** For `agentic-mbse extract --enhance`, automated rejection is safest. The interactive skill can do (c) because it has a human in the loop.

5. **Should the skill use the improved backend directly?** — Currently the skill calls `extract_page.py` which does raw pymupdf4llm. After v2, it should call the post-processed version. **Recommendation: Yes.** Update `extract_page.py` to import and apply `postprocess()`.

6. **Test corpus size?** — We have 7 documents. Is this enough? **Recommendation: Yes for v2 ship.** The 7 documents cover diverse layouts (text-heavy, table-heavy, equation-heavy, mixed). Expand corpus in v3.
