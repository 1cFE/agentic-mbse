---
date: 2026-02-27T21:00:00-05:00
researcher: Claude
topic: "PDF extraction quality failures on Araiinejad TEA paper"
tags: [research, extraction, quality-gate, pipeline]
status: complete
last_updated: 2026-02-27
---

# Research: Extraction Quality Failures

**Date**: 2026-02-27
**Researcher**: Claude
**Research Type**: Root Cause Analysis

## Research Question

Why is the extraction quality on the Araiinejad TEA paper unsatisfactory? Specifically: Table 2 is garbled and Equation 2.2 is unreadable. What are the systemic failure modes, and are there quick fixes?

## Summary

- **The quality gate didn't fail — it was never designed to catch these problems.** The gate detects character-level garbling (strikethroughs, replacement chars, bracket operators). Tables rendered as unstructured text and equations rendered as italic fragments produce NO signals.
- **GMFT_APPEND is the wrong action.** When pymupdf4llm renders a table as flowing text (no pipe separators) and GMFT detects the real table, the pipeline *appends* the good table at the end but leaves the garbled text in place. The user sees both versions.
- **Budget was NOT the constraint.** Only $0.45 of $2.00 was spent. The quality gate simply didn't flag pages 2-3 for Claude enhancement.
- **6 of 12 pages (50%) were routed to GMFT_APPEND** — all suffering from the same "garbled text + appended table" problem. This is the dominant failure mode.
- **There are concrete quick wins.** The highest-impact fix is ~20 lines of code: when GMFT finds tables that pymupdf missed, route to CLAUDE_REPLACE instead of GMFT_APPEND.

## Detailed Findings

### What the Pipeline Did

The document has 12 pages (0-indexed 0–11). Pipeline decisions:

| Page | Action | Reason | Result Quality |
|:---:|--------|--------|:---:|
| 0 | KEEP | No issues | OK |
| 1 | CLAUDE_REPLACE | 4 strikethroughs | Good |
| 2 | GMFT_APPEND | GMFT found tables not in pymupdf | **BAD** — garbled Table 2 text + appended table |
| 3 | GMFT_APPEND | GMFT found tables not in pymupdf | **BAD** — garbled Tables 3,4,5 text + appended tables |
| 4 | CLAUDE_REPLACE | 3 strikethroughs | Good |
| 5 | CLAUDE_REPLACE | 9 strikethroughs | Good |
| 6 | GMFT_APPEND | GMFT found tables not in pymupdf | **BAD** |
| 7 | KEEP | No issues | OK |
| 8 | GMFT_APPEND | GMFT found tables not in pymupdf | **BAD** |
| 9 | GMFT_APPEND | GMFT found tables not in pymupdf | **BAD** |
| 10 | GMFT_APPEND | GMFT found tables not in pymupdf | **BAD** |
| 11 | KEEP | No issues | OK |

Claude spend: $0.45 of $2.00 budget. Model: opus. 3 page replacements + 1 table enhancement.

### Failure Mode 1: GMFT_APPEND Leaves Garbled Text In Place

**The core problem.** This is the dominant failure affecting 6/12 pages.

When pymupdf4llm renders a table without pipe separators (as flowing text), the routing logic in `quality_gate.py:route_page()` rule 5 fires:

```python
# Rule 5: GMFT tables available + pymupdf has no pipe tables → GMFT_APPEND
if has_tables and not assessment.needs_gmft and not assessment.needs_claude:
    has_existing_tables = _has_pipe_tables(page_markdown)
    if not has_existing_tables:
        reasons.append("GMFT found tables not in pymupdf4llm output")
        return PageDecision(assessment.page_num, PageAction.GMFT_APPEND, reasons)
```

`insert_tables_at_end()` (`tables.py:132-143`) simply appends pipe tables after the existing page markdown. The garbled text from pymupdf4llm stays.

**Example — Table 2 in the output (page 2, 0-indexed):**

Lines 150–228 of output.md contain the garbled text version:
```
**Table 2**
Direct costs.

COA Number and Name Description

**20** **Direct Costs**
21.1 Land & Land Rights
21.2 Structures & Site
Facilities

_Described in Section 3.2_

22 Reactor Plant
Equipment
...
```

Lines 364–385 contain the GMFT-appended pipe table:
```
| COA \n20 | Number and Name \nDirect Costs | Description |
| --- | --- | --- |
| 21.1 | Land & Land Rights |  |
| 21.2 | Structures & Site | Described in Section 3.2 |
...
```

The user sees **both**. The garbled text is the primary reading content and the pipe table is buried at the end of the page.

**Root cause in `quality_gate.py:411-415`:** Rule 5 explicitly requires `not needs_claude`, meaning it only fires when the quality gate thinks the page is fine. It was designed for "GMFT found tables that pymupdf didn't detect at all" — but the actual situation is "pymupdf detected the table content and garbled it into text."

### Failure Mode 2: Equation Rendering Invisible to Quality Gate

Equation 2.2 in the PDF is a simple scaling equation. pymupdf4llm renders it as:

```
(
_Pnew_
_C_ = _CEEDB_

) _n_

(2.2)
```

This is italic text fragments. The quality gate checks:
- `~~strikethroughs~~`: 0 found → no signal
- `\ufffd` replacement chars: 0 → no signal
- `[/]` bracket operators: 0 → no signal
- Unicode math density: 0 → no signal

The equation looks like normal italic text to every detection heuristic. The quality gate was designed to catch pymupdf4llm's specific garbling artifacts, not structural rendering failures where the content is present but in the wrong format.

**Reference:** `quality_gate.py:98-147` (`_assess_math_garbling`)

### Failure Mode 3: No Cross-Reference Between GMFT and Quality Gate

The quality gate and GMFT detection are independent steps in the pipeline:
- Step 3: Table detection (GMFT)
- Step 4: Quality gate assessment

The quality gate doesn't know about GMFT results. When GMFT finds tables on a page where pymupdf produced no pipe tables, that's a strong signal: "pymupdf failed to parse the table correctly and probably garbled surrounding content too." But this signal is never factored into the severity score.

If it were, page 2 would have received a severity boost and potentially been routed to CLAUDE_REPLACE instead of GMFT_APPEND.

**Reference:** `pipeline.py:289-301` (quality gate runs on raw pymupdf pages, before table decisions)

### Failure Mode 4: pymupdf4llm `table_strategy="lines"` Misses Borderless Tables

pymupdf4llm with `table_strategy="lines"` relies on detected grid lines to identify tables. Tables without visible borders (like Table 2 in the Araiinejad paper, which has alternating row shading but no grid lines) are rendered as flowing text.

This is a **known limitation** documented in `docs/extraction-internals.md`:
> "Space-aligned tables without grid lines. Tables that rely on column alignment rather than pipe characters or borders are invisible to all detectors."

However, in this case GMFT *does* detect the table — the problem is the pipeline's response to that detection.

## Honest Assessment

### What Went Right
- Claude-enhanced pages (1, 4, 5) look good — equations and tables are properly formatted
- GMFT correctly detected all tables in the document
- Table filtering didn't reject any real tables
- The pipeline architecture is sound — the issue is routing logic, not fundamental design

### What Went Wrong
- The quality gate was validated against the 14-document test corpus where the dominant failure mode was character-level garbling (strikethroughs). The Araiinejad paper's dominant failure mode is structural — pymupdf4llm renders tables as text. The test corpus didn't adequately cover this pattern.
- GMFT_APPEND was designed as a "bonus" action for when GMFT finds tables that pymupdf simply skipped. It wasn't designed for the case where pymupdf *attempted* to render the table and produced garbled text instead.
- The quality gate's philosophy is "pymupdf output is acceptable unless specific garbling signals fire." This is wrong for documents with borderless tables.

### Is This an Endless Cycle?

**No, but with a caveat.** The specific failure modes here are well-defined and fixable:

1. GMFT_APPEND leaving garbled text is a routing logic bug, not a fundamental limitation
2. Quality gate blind spots can be addressed by cross-referencing with GMFT results
3. The pipeline already has Claude as a "nuclear option" that works — it just wasn't triggered

The caveat: there will always be new document types that expose new failure modes. The quality gate is a heuristic system tuned to observed failure patterns. Each new failure pattern requires a new signal. This is inherent to any non-ML quality assessment approach.

The right response is NOT to try to anticipate all failure modes upfront, but to:
1. Fix the concrete routing bug (GMFT_APPEND)
2. Add the GMFT cross-reference signal
3. Add this document to the test corpus
4. Re-run and verify

## Recommendations

### Quick Win 1: Route GMFT-missed-tables pages to CLAUDE_REPLACE (Highest Impact)

**What:** When GMFT finds tables on a page where pymupdf produced no pipe tables, route to CLAUDE_REPLACE (if within budget) instead of GMFT_APPEND.

**Where:** `quality_gate.py:route_page()`, rule 5 (lines 410-415)

**Why:** If GMFT found a table and pymupdf didn't produce a pipe table, the page likely has structural rendering failures beyond just the table. Claude full-page replacement handles both the table and surrounding content (equations, text flow).

**Impact:** Fixes the dominant failure mode (6/12 pages on this document). Cost increase ~$0.47 per document (6 × $0.078/page with sonnet) — well within the $2.00 budget.

**Alternative if over budget:** Fall back to GMFT_APPEND only after Claude budget is exhausted.

**Effort:** ~20 lines changed in `route_page()`.

### Quick Win 2: Boost Severity When GMFT Finds Missed Tables

**What:** In the quality gate assessment, if GMFT detected tables on a page that pymupdf didn't produce as pipe tables, add a severity boost (e.g., +1.5).

**Where:** `pipeline.py` step 4 or a new cross-reference step between steps 3 and 4.

**Why:** This ensures these pages compete for Claude budget alongside pages with character-level garbling. A page with garbled tables AND garbled equations is worse than a page with just strikethroughs.

**Effort:** ~15 lines.

### Quick Win 3: Add Equation-Fragment Detection

**What:** Detect equation fragments: isolated `(N.N)` equation numbers preceded by lines with only italic variables like `_C_ = _CEEDB_`.

**Where:** `quality_gate.py`, new signal in `_assess_math_garbling()`.

**Pattern:** Lines matching `^\s*\(\d+(\.\d+)?\)\s*$` preceded by short lines with heavy italic/subscript usage.

**Effort:** ~30 lines. Lower priority than Quick Wins 1-2 since Claude replacement already handles equations.

### Non-Quick-Win: Add This Document to Test Corpus

**What:** Add the Araiinejad PDF to `tests/corpus/pdfs/` and ground truth to `ground_truth.jsonl`.

**Why:** Prevents regression and validates that the routing fixes actually work on this failure pattern.

**Effort:** ~1 hour of manual ground truth annotation.

## Code References

- `quality_gate.py:98-147` — `_assess_math_garbling()`: blind to equation fragments
- `quality_gate.py:343-418` — `route_page()`: rule 5 routes to GMFT_APPEND instead of CLAUDE_REPLACE
- `quality_gate.py:410-415` — The specific code path that causes GMFT_APPEND
- `tables.py:132-143` — `insert_tables_at_end()`: just appends, doesn't remove garbled text
- `pipeline.py:289-301` — Quality gate runs before table routing decisions are factored in
- `pipeline.py:406-416` — GMFT_APPEND merge: `insert_tables_at_end(page.markdown, page_tables)`
- `claude_enhance.py:23-42` — Page extraction prompt (works well when triggered)

## Open Questions

1. Should rule 5 (GMFT tables, no pymupdf tables) ALWAYS route to Claude, or only when severity > some threshold? Always-Claude is simpler but costs more.
2. Should the quality gate be refactored to accept GMFT results as input, or should cross-referencing happen as a separate pipeline step between table detection and quality assessment?
3. The document was extracted with `--model opus` ($0.45 total). With `--model sonnet` the same pages would cost ~$0.03 each. Should the default be more aggressive about Claude usage given sonnet's low cost?
