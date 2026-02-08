# Plan: Corpus Benchmark + Ship

**Status:** Draft
**Created:** 2026-02-08
**Last Updated:** 2026-02-08

## Source Documents

- **Spec:** `.project/active/corpus-benchmark-ship/spec.md`
- **Baseline:** `.project/reports/20260208_pdfv3-baseline.md`
- **Epic:** `.project/backlog/epic_pdf-extraction-v3.md` (Item 4)

## Overview

This plan is a sequence of **MANUAL** steps (commands you run) and **CLAUDE REVIEW** steps (I analyze output and write documentation). No code changes expected unless prompt tuning is needed.

**Extraction order:** Start with one small known-good doc as a smoke test, then the 5 new corpus docs (the ones we care about most), then the remaining 6 original docs.

**Timing:** Each extraction wrapped in `time` to capture wall clock duration.

---

## Pre-Flight

### Step 0: Verify test suite [MANUAL] ✅

856 passed, 1 skipped, 0 failed.

### Step 1: List corpus documents [MANUAL] ✅

All 12 PDFs confirmed. 3 root-level duplicates excluded (using subdirectory copies only).

### Step 2: Note any pre-existing output [MANUAL] ✅

Baseline outputs exist from Item 1. `--force` will overwrite.

---

## Phase 1: Smoke Test (1 doc)

### Step 3: Extract 2241 (Eester ICRH, 30p, baseline A-) [MANUAL] ✅

Wall clock: 9m49s. L3 skipped (well-structured). L4 repaired 26 regions.

### Step 4: Review 2241 output [CLAUDE REVIEW] ✅

No regression. 7 ## + 8 ### + 15 INDEX sections — identical to baseline. Grade: A- (unchanged).

---

## Phase 2: New Corpus (5 docs)

These are the docs that matter most — the 0/5 → 4/5 gap.

### Step 5: Extract new corpus docs [MANUAL]

Run each one individually with timing. Copy-paste each block:

**2243 — Rider Slides (127p, baseline D+)**
```bash
cd /home/reid/1cfe/agentic-mbse && time uv run agentic-mbse extract /home/reid/1cfe/literature/2243/*.pdf --enhance --index --force 2>&1 | tee /tmp/bench-2243.log
```

**2244 — Helios Stellarator (29p, baseline C+)**
```bash
cd /home/reid/1cfe/agentic-mbse && time uv run agentic-mbse extract /home/reid/1cfe/literature/2244/*.pdf --enhance --index --force 2>&1 | tee /tmp/bench-2244.log
```

**safety — Fusion Safety Program (14p, baseline C+)**
```bash
cd /home/reid/1cfe/agentic-mbse && time uv run agentic-mbse extract "/home/reid/1cfe/literature/safety-program/Fusion Safety Program.pdf" --enhance --index --force 2>&1 | tee /tmp/bench-safety.log
```

**fusion-std — Fusion Standards (4p, baseline D+)**
```bash
cd /home/reid/1cfe/agentic-mbse && time uv run agentic-mbse extract /home/reid/1cfe/literature/fusion-standards-doc/fusion-standards.pdf --enhance --index --force 2>&1 | tee /tmp/bench-fusionstd.log
```

**hazards — Afify Hazards (8p, baseline B-)**
```bash
cd /home/reid/1cfe/agentic-mbse && time uv run agentic-mbse extract /home/reid/1cfe/literature/hazards-afify/hazards-34-paper-095-afify.pdf --enhance --index --force 2>&1 | tee /tmp/bench-hazards.log
```

**After each extraction**, note:
- Wall clock time from `time` output
- Any errors printed to console

### Step 6: Review new corpus results [CLAUDE REVIEW]

For each of the 5 new corpus docs, I'll:
1. Read the extracted `full_document.md` and `INDEX.md`
2. Read the console log from `/tmp/bench-*.log`
3. Spot-check headers against the PDF content (first 10 pages, last 5 pages)
4. Grade: Structure, Tables, Body Text, Images, Overall
5. Compare against baseline grades
6. Evaluate: usable INDEX? (yes/no — this feeds the critical success factor)

**Decision point after this step:**
- If **4/5 usable INDEX** → proceed to Phase 3
- If **<4/5 usable INDEX** → go to Phase 4 (prompt tuning) first
- If any doc had L3 failure → investigate before proceeding

### Step 5 Results ✅

Pre-requisite code fixes applied (separate commit):
- `_is_noise_header()`: extended char class for Unicode math symbols + `** **` bold marker check
- `parse_sections()`: added `\.?` for period-numbered headers (`## 1. Title`)
- `parse_sections()`: added `_parse_unnumbered_sections()` fallback for docs with no numbered headers
- 881 tests passed after changes (21 new tests added)

| Doc | Wall Clock | L3 Gate | Headers Inserted | INDEX Sections | Usable? |
|-----|-----------|---------|-----------------|----------------|---------|
| safety-program | 25s | slide_deck, unnumbered_bold | 10 (1 skipped) | 10 | **YES** |
| fusion-standards | 21s | academic_paper, unnumbered_bold | 5 (1 skipped) | 5 | **YES** |
| 2244 (Helios) | 63s | academic_paper, numbered_bold | 9 | 15 | **YES** |
| hazards (Afify) | 29s | academic_paper, unnumbered_bold | 20 | 20 | **YES** |
| 2243 (Rider) | 29s | **NOT triggered** | 0 | 20 (junk) | **NO** |

**Critical success factor: 4/5 usable INDEX — PASS.** Proceeding to Phase 3.

**2243 finding:** The gate bypass didn't work because 2243's headers are slide content (dates, plain-text equations, bullet items) — not Unicode noise. The doc is legitimately a slide deck with no real document sections. A future improvement would be a final fallback in `parse_sections()`: if headers look like slide content (no numbered or unnumbered structure), call Claude to manually identify logical section boundaries. This is a separate work item, not a blocker for shipping.

---

## Phase 3: Original Corpus (6 remaining docs)

### Step 7: Extract remaining original corpus docs [MANUAL]

**2232 — Handley (17p, baseline B+)**
```bash
cd /home/reid/1cfe/agentic-mbse && time uv run agentic-mbse extract /home/reid/1cfe/literature/2232/*.pdf --enhance --index --force 2>&1 | tee /tmp/bench-2232.log
```

**2233 — Araiinejad (12p, baseline B)**
```bash
cd /home/reid/1cfe/agentic-mbse && time uv run agentic-mbse extract /home/reid/1cfe/literature/2233/*.pdf --enhance --index --force 2>&1 | tee /tmp/bench-2233.log
```

**2235 — Global Fusion (30p, baseline B+)**
```bash
cd /home/reid/1cfe/agentic-mbse && time uv run agentic-mbse extract /home/reid/1cfe/literature/2235/*.pdf --enhance --index --force 2>&1 | tee /tmp/bench-2235.log
```

**2236 — Digital Twins (66p, baseline B+)**
```bash
cd /home/reid/1cfe/agentic-mbse && time uv run agentic-mbse extract /home/reid/1cfe/literature/2236/*.pdf --enhance --index --force 2>&1 | tee /tmp/bench-2236.log
```

**2237 — LANL PJMIF (60p, baseline B+)**
```bash
cd /home/reid/1cfe/agentic-mbse && time uv run agentic-mbse extract /home/reid/1cfe/literature/2237/*.pdf --enhance --index --force 2>&1 | tee /tmp/bench-2237.log
```

**2238 — Lampe CBFR (40p, baseline C+)**
```bash
cd /home/reid/1cfe/agentic-mbse && time uv run agentic-mbse extract /home/reid/1cfe/literature/2238/*.pdf --enhance --index --force 2>&1 | tee /tmp/bench-2238.log
```

### Step 7 Results ✅

All 6 original corpus docs re-extracted + smoke test (2241 from Step 3).

| Doc | Pages | L3 Gate | Headers Inserted | INDEX Sections | Baseline Sections |
|-----|-------|---------|-----------------|----------------|-------------------|
| 2241 (ICRH) | 30 | skipped | 0 | 15 | 15 |
| 2232 (Handley) | 17 | skipped | 0 | 15 | 15 |
| 2233 (Araiinejad) | 12 | skipped | 0 | 10 | 10 |
| 2235 (Global Fusion) | 30 | skipped | 0 | 27 | 27 |
| 2236 (Digital Twins) | 66 | skipped | 0 | 67 | 67 |
| 2237 (LANL PJMIF) | 60 | skipped | 0 | 51 | 51 |
| 2238 (Lampe CBFR) | 40 | technical_report | 9 (6 skipped) | 14 | 14 |

All 7 docs: L3 correctly skipped for 6/7 well-structured docs, fired for 2238 (which needed it). INDEX section counts match baseline in all cases. **Zero regressions.** Proceeding to Phase 5.

Note: 2238 L3 inserted 9 headers but also has 2 junk entries (reference line as header, "160 MW" body text promoted). These were present in baseline too — no regression.

### Step 8: Review original corpus results [CLAUDE REVIEW]

For each of the 6 docs + the smoke test doc (2241):
1. Read extracted output + console log
2. Grade using same rubric
3. Compare against baseline — **any regression is a blocker**
4. If regression found → document root cause, determine if prompt fix or code fix needed

**Decision point:**
- If **zero regressions** → proceed to Phase 5
- If **regression found** → investigate, fix, re-extract affected doc(s)

---

## Phase 4: Prompt Tuning (conditional)

*Only if Phase 2 shows <4/5 usable INDEX or Phase 3 shows regressions.*

### Step 9: Analyze failure patterns [CLAUDE REVIEW]

I'll analyze all failed/underperforming docs to identify:
- Common failure patterns (style detection miss? anchor mismatch? level errors?)
- Which prompt to adjust (Phase A style detection vs Phase B structural repair)
- Specific fix (e.g., add example for slide decks, tighten anchor matching)

### Step 10: Apply prompt fix [CLAUDE CODE CHANGE]

Edit the relevant prompt in `claude_structure.py`. Commit the change.

### Step 11: Re-extract affected docs [MANUAL]

Re-run only the affected docs (same commands from Steps 5/7, adjusted). Delete cached `style.json` first if Phase A prompt changed:

```bash
# Example: clear style cache for a doc before re-extract
rm /path/to/output_dir/style.json
```

### Step 12: Re-review [CLAUDE REVIEW]

Grade the re-extracted docs. Maximum 2 tuning iterations total.

---

## Phase 5: Documentation + Ship

### Step 13: Final test suite [MANUAL]

```bash
cd /home/reid/1cfe/agentic-mbse && uv run pytest tests/ -q --tb=short
```

**Expected:** 856+ passed, 0 failed.

### Step 14: CLI help text review [CLAUDE REVIEW]

```bash
uv run agentic-mbse extract --help
```

I'll review for accuracy. Current help text looks correct based on Item 3 wiring — no changes expected.

### Step 15: Write benchmark report [CLAUDE DOCUMENTATION]

I'll write `.project/reports/20260210_pdfv3-benchmark.md` containing:

1. **Executive summary** — critical success factor pass/fail, headline results
2. **Per-document metrics table** — columns: ID, Short Name, Pages, Style Detected, Headers Inserted, INDEX Sections, Wall Clock Time, Structure Grade, Overall Grade, Baseline Grade, Delta
3. **Per-document notes** — spot-check findings, FP/FN counts, specific issues
4. **Baseline comparison table** — row-by-row delta from Item 1 baseline
5. **Cost actuals** — estimated per-doc based on model/tokens (Haiku Phase A + Sonnet Phase B)
6. **Critical success factor evaluation** — 4/5 new corpus docs usable INDEX?
7. **Known limitations** — docs >200p, document types not tested, etc.
8. **Prompt tuning log** — if any iterations were needed, what changed and why

### Step 16: Update epic status [CLAUDE DOCUMENTATION]

Update `.project/backlog/epic_pdf-extraction-v3.md`:
- Check off Item 4 success criteria
- Fill in Lessons Learned section
- Update status and next action

---

## Risk Management

| Risk | Mitigation |
|------|-----------|
| PDF paths differ from what explorer found | Step 1 confirms exact paths before extraction |
| 2243 (127p) takes very long or costs too much | Monitor during extraction; `--max-repair-pages` available as escape hatch |
| `needs_claude_structure()` skips a doc that needs help | Log output will show; can re-run with `--structure-only` to force L3 |
| L3 produces worse results than baseline on an original doc | Step 8 catches this; Phase 4 addresses it |
| Prompt tuning exceeds 2 iterations | Hard stop at 2; document remaining issues as known limitations |

---

**Estimated duration:** ~3-4 hours (extraction time dominates; large docs may take 2-5 min each with Claude calls)
