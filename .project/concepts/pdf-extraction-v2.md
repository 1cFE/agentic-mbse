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

## Strategy: Two Parallel Tracks

### Track 1: Post-Processing Pipeline (deterministic, no new deps)

Add a `postprocess.py` module to `src/agentic_mbse/extraction/` that cleans up pymupdf4llm output. This is a pure function: `markdown_in → markdown_out`. No ML, no external tools, no network. Runs in milliseconds.

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

**Expected impact:** This alone should move the score from 2.68 to ~3.2-3.4 — fixing headers fixes indexing, and the cascade of post-processing improvements cleans up the text quality. Tables remain the weak point.

### Track 2: ML Table Extraction (GMFT integration)

GMFT wraps Microsoft's Table Transformer (DETR-based, trained on PubTables-1M — 947K scientific tables). It:
- Requires no GPU
- Installs with `pip install gmft`
- Processes at ~1.4s/page, ~1.2s/table
- Outputs Pandas DataFrames → markdown pipe tables
- Handles borderless tables (trained on PubMed Central papers)

**Integration approach:**

```
Full-document pymupdf4llm extraction (Track 1 post-processed)
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

**Expected impact:** Table scores from 2.00 to ~3.5-4.0. Combined with Track 1, overall score should reach **3.5-4.0**.

---

## What We Deliberately Defer

| Item | Why Defer | When |
|------|----------|------|
| Equation OCR (UniMERNet/Surya) | Heavy models, complex integration, affects 3/7 docs. The `<!-- equation: see original PDF page N -->` marker is good enough for now. | v3 |
| VLM fallback layer | Agent experiment showed hallucination risk on dense tables. Need cross-validation logic. Too risky to ship as default. | v3, with cross-validation |
| Full Docling MCP deployment | Already spec'd separately. Good design doc exists. Orthogonal to extraction quality. | Separate work item |
| MinerU / Marker integration | Full pipeline replacements. Too heavy for a 3-day sprint. Worth evaluating later. | v3 evaluation |
| DOCX extraction improvements | No evaluation data yet. PDF is the priority. | After PDF v2 ships |

---

## 3-Day Execution Plan

### Day 1: Post-Processing Pipeline + pymupdf4llm Upstream Fixes

**Morning — postprocess.py module:**
1. Create `src/agentic_mbse/extraction/postprocess.py`
2. Implement `promote_bold_headers(md: str) -> str` — regex to convert `**N.N Title**` patterns to `## N.N Title` with depth-aware heading levels
3. Implement `strip_page_numbers(md: str) -> str` — remove bare page numbers between blank lines
4. Implement `strip_running_headers(md: str, threshold: float = 0.5) -> str` — cross-page deduplication of repeated short lines
5. Implement `normalize_image_paths(md: str, images_dir: Path) -> str` — absolute→relative
6. Implement `repair_ligatures(md: str) -> str` — common ligature dictionary + context reconstruction
7. Implement `promote_figure_captions(md: str) -> str` — `![](img)` + adjacent `Figure N:` → `![Figure N: ...](img)`
8. Implement `postprocess(md: str, images_dir: Path | None = None) -> str` — chains all steps

**Afternoon — pymupdf_backend.py upgrades:**
1. Add custom `hdr_info` callback using bold flag + section numbering regex
2. Change default `table_strategy` to `"lines"` (less strict, catches more tables)
3. Wire `postprocess()` into the extraction pipeline (call after `to_markdown()`)
4. Test against the 7-document corpus — measure score delta

**Evening — index.py improvements:**
1. Add appendix letter-numbering pattern (`A`, `B.1`, etc.)
2. Add bold-header fallback pattern to `parse_sections()` (defense-in-depth: if post-processing missed a header, the index parser can still catch bold patterns)

**Exit criteria for Day 1:** Post-processed output scores 3.2+ on the 7-doc corpus. All 7 documents produce non-empty INDEX.md files.

### Day 2: GMFT Table Extraction + Benchmark Harness

**Morning — GMFT integration:**
1. Add `gmft` as an optional dependency (`[extract-tables]` or bundled with `[extract]`)
2. Create `src/agentic_mbse/extraction/table_extraction.py`
3. Implement `extract_tables_from_page(pdf_path, page_num) -> list[DataFrame]`
4. Implement `tables_to_markdown(tables: list[DataFrame]) -> list[str]`
5. Implement `replace_tables_in_markdown(md: str, pdf_path: Path) -> str` — the orchestrator that detects table regions, runs GMFT, and splices results

**Afternoon — wire into pipeline + benchmark:**
1. Integrate GMFT table extraction into `pymupdf_backend.py` (optional: only runs if `gmft` is importable)
2. Build a minimal benchmark script: run extraction on the 7-doc corpus, compare against stored "ground truth" ratings
3. Run the benchmark. Iterate on table region detection heuristics.

**Evening — edge cases and fallbacks:**
1. Handle GMFT failures gracefully (fall back to pymupdf4llm table output)
2. Handle multi-page tables (heuristic: detect table continuation patterns)
3. Update `table_repair.py` to work with the new pipeline (the Claude-based repair becomes a third-tier fallback for tables that GMFT also can't handle)

**Exit criteria for Day 2:** Table scores at 3.5+ on the corpus. GMFT runs without errors on all 7 documents. The extraction pipeline gracefully degrades when `gmft` is not installed.

### Day 3: Integration, Skill Update, Ship

**Morning — CLI integration:**
1. Wire the full pipeline into `agentic-mbse extract` CLI command
2. Add `--no-tables` flag to skip GMFT (for speed or when not installed)
3. Update `summary.json` to include post-processing metadata and table extraction stats
4. Run full end-to-end test: `agentic-mbse extract <each of 7 PDFs>`

**Afternoon — skill and evaluation:**
1. Update `.claude/skills/pdf-analysis/SKILL.md` to reference the improved backend
2. Update `extract_page.py` to use the new post-processing pipeline for `--mode markdown`
3. Run the formal evaluation: score all 7 documents, write updated evaluation report
4. Compare v1 vs v2 scores side-by-side

**Evening — ship:**
1. Update `pyproject.toml` dependencies
2. Run existing test suite (`uv run pytest tests/`)
3. Fix any broken tests
4. Commit and prepare PR

**Exit criteria for Day 3:** Overall score 3.5+ on the corpus. `agentic-mbse extract` works end-to-end. Tests pass. PR ready.

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
pymupdf_backend.extract()     →  raw markdown
    or
docling_backend.extract()     →  raw markdown
    ↓
postprocess.postprocess(md)   →  cleaned markdown
    ↓
[optional] table_extraction.replace_tables(md, pdf_path)  →  tables fixed
    ↓
write full_document.md
    ↓
index.generate_index()        →  INDEX.md (now works because headers are proper)
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

The interactive skill (`.claude/skills/pdf-analysis/`) and the CLI pipeline (`agentic-mbse extract`) serve different use cases:

| | CLI Pipeline | Interactive Skill |
|---|---|---|
| **Use case** | Batch extraction of reference docs | Ad-hoc analysis during Claude sessions |
| **Speed** | Fast, fully automated | Slow, agent-guided |
| **Scope** | Full document | Per-page, targeted |
| **Cost** | ~$0 (local compute) | $0.31/page (API costs) |
| **Quality** | 3.5+/5 (after v2) | 3.7/5 (agent comparison) |

With v2 post-processing, the CLI pipeline's quality approaches the agent's manual quality — **without the $0.31/page cost.** The skill becomes most valuable for:
1. Pages where even GMFT can't reconstruct tables (rare, complex merged cells)
2. Equation-heavy pages (until we add equation OCR)
3. Scanned/image-only pages
4. Interactive exploration ("what does figure 3 show?")

**Skill update:** The skill should first try the improved CLI-style extraction (pymupdf4llm + post-processing + GMFT), and only escalate to Docling MCP or vision for pages that still have problems. This inverts the current escalation: instead of "start bad, escalate to good," we "start good, escalate for edge cases."

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| GMFT fails on some table layouts | Medium | Medium | Graceful fallback to pymupdf4llm output; table_repair.py as backup |
| Post-processing regex matches false positives (e.g., bold text that isn't a header) | Medium | Low | Require numbered section pattern + bold to trigger promotion; test against corpus |
| GMFT model download blocks CI/testing | Low | Medium | Mock GMFT in tests; make it optional |
| 3-day timeline is too aggressive | Medium | Medium | Track 1 (post-processing) ships independently and is valuable alone. Track 2 (GMFT) can ship in a follow-up if needed. |
| Running header detection removes legitimate content | Low | High | Conservative threshold (>50% page frequency); opt-out flag |

---

## Success Metrics

| Metric | Current (v1) | Target (v2) | Stretch |
|--------|-------------|------------|---------|
| Overall quality score | 2.68/5 | 3.5/5 | 4.0/5 |
| Markdown structure | 2.64/5 | 3.5/5 | 4.0/5 |
| Index quality | 2.43/5 | 4.0/5 | 4.5/5 |
| Image extraction | 3.64/5 | 4.0/5 | 4.5/5 |
| Table extraction | 2.00/5 | 3.5/5 | 4.0/5 |
| Docs with non-empty INDEX.md | 3/7 | 7/7 | 7/7 |
| New dependencies (required) | 0 | 0 | 0 |
| New dependencies (optional) | 0 | 1 (gmft) | 1 |

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

1. **GMFT vs pymupdf4llm table_strategy cascade only?** — GMFT gives dramatically better results but adds a 270MB dependency. The cascade is free but has a lower ceiling. **Recommendation: Both.** Cascade is Day 1 (free improvement), GMFT is Day 2 (major improvement). Pipeline tries GMFT first, falls back to cascade.

2. **Where does equation handling land?** — The concept defers equation OCR entirely. We add a `<!-- equation region: see original PDF page N -->` marker for garbled regions. Is this acceptable for the v2 ship? **Recommendation: Yes.** Equations affect 3/7 docs and the workaround is transparent. Equation OCR is a v3 feature.

3. **Should the skill use the improved backend directly?** — Currently the skill calls `extract_page.py` which does raw pymupdf4llm. After v2, it should call the post-processed version. **Recommendation: Yes.** Update `extract_page.py` to import and apply `postprocess()`.

4. **Test corpus size?** — We have 7 documents. Is this enough? **Recommendation: Yes for v2 ship.** The 7 documents cover diverse layouts (text-heavy, table-heavy, equation-heavy, mixed). Expand corpus in v3.
