# Spec: Corpus Benchmark + Ship

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-08 17:41 UTC
**Complexity:** LOW
**Branch:** pdf-extract
**Epic:** EPIC-PDFV3-001, Item 4

---

## Business Goals

### Why This Matters

Items 1-3 built and wired the Claude structural backbone, but it has never been validated on real documents. Without this benchmark, we don't know whether v3 actually closes the 0/5 → 4/5 gap on unseen documents or whether it regresses the original 7-doc corpus. This is the "does it work?" step.

### Success Criteria

- [ ] `--enhance` mode: at least 4/5 new corpus docs produce usable INDEX (epic critical success factor)
- [ ] `--enhance` mode: at least 3/5 new corpus docs grade B- or better
- [ ] `--enhance` mode: all 7 original corpus docs grade equal or better than baseline
- [ ] Cost actuals within 2x of estimates ($1-4/doc acceptable, >$5/doc needs investigation)
- [ ] Results report published with per-document breakdown
- [ ] CLI `--help` text is accurate for all current flags
- [ ] Full test suite passes

### Priority

P1 — final item on critical path. Unblocked (Items 1-3 complete).

---

## Scope

### In Scope

1. **`--enhance` benchmark on all 12 docs**: Run the full v3 pipeline, record per-document: style detection result, headers inserted, correct/incorrect, INDEX section count, wall clock time, API cost
2. **Grading**: Grade each document using the same rubric as the baseline report (A through D, sub-grades for Structure/Tables/Body/Images)
3. **Comparison against baseline**: Row-by-row comparison with `.project/reports/20260208_pdfv3-baseline.md`
4. **Regression investigation**: Any original-corpus doc that degrades → investigate and fix
5. **Prompt tuning**: Up to 2 iterations if new-corpus docs fall short
6. **Results report**: `.project/reports/20260210_pdfv3-benchmark.md`
7. **CLI help text review**: Verify `--help` output is accurate for `--enhance`, `--structure-only`, `--model`
8. **Test suite**: Verify all existing + new tests pass

### Out of Scope

- ~~`--fast` mode testing~~ (flag does not exist; default mode is the fast path)
- ~~Cost confirmation prompts / `--yes` flag~~ (eliminated in Item 3)
- Quality sweep / page-level sampling (Workstream C — deferred)
- Documents over 200 pages
- Performance optimization
- Updating the `/pdf-analysis` skill (separate follow-up)

### Edge Cases

- `needs_claude_structure()` returns False for some original-corpus docs → L3 skipped, which is correct; record which docs were skipped and verify they still grade the same as baseline
- L3 failure on a real doc → record the failure, investigate, decide if prompt fix or bug fix needed
- Unexpected cost spike on large docs (2236 at 66p, 2237 at 60p, 2243 at 127p)

---

## Requirements

### Functional Requirements

1. **FR-1**: Every corpus document MUST be run through the pipeline with `--enhance --index --force` and the results recorded
2. **FR-2**: Per-document metrics MUST include: style detected, headers inserted, INDEX section count, wall clock time, API cost, overall grade, structure sub-grade
3. **FR-3**: Results MUST be compared row-by-row against the Item 1 baseline, with delta column
4. **FR-4**: Any regression on original 7-doc corpus MUST be investigated (root cause documented) and fixed before shipping
5. **FR-5**: Prompt tuning (if needed) MUST be limited to 2 iterations
6. **FR-6**: Results report MUST follow the same rubric and format as `.project/reports/20260208_pdfv3-baseline.md`
7. **FR-7**: Test suite (`uv run pytest tests/`) MUST pass at end of work

---

## Acceptance Criteria

- [ ] All 12 docs extracted with `--enhance --index --force`
- [ ] Per-document metrics table in results report (all columns populated)
- [ ] Baseline comparison table with deltas
- [ ] Critical success factor evaluated: 4/5 new corpus docs usable INDEX? (pass/fail)
- [ ] No regressions on original 7-doc corpus
- [ ] Cost actuals documented
- [ ] Known limitations documented
- [ ] `uv run pytest tests/` passes
- [ ] `uv run agentic-mbse extract --help` output reviewed and accurate

---

## Process

This item uses a **MANUAL + REVIEW** process. Each plan step will be either:
- **MANUAL**: A clear command for the operator to run and confirm
- **CLAUDE REVIEW & DOCUMENTATION**: Claude analyzes output, grades documents, writes the report

---

## Related Artifacts

- **Baseline:** `.project/reports/20260208_pdfv3-baseline.md`
- **Epic:** `.project/backlog/epic_pdf-extraction-v3.md` (Item 4)
- **Claude Structure Module:** `src/agentic_mbse/extraction/claude_structure.py`
- **Extract CLI:** `src/agentic_mbse/cli/extract_cli.py`

---

## Deliverables

- `.project/reports/20260210_pdfv3-benchmark.md` — Full results
- Any prompt adjustments committed (if tuning needed)

---

**Next Steps:** After approval, proceed to plan (MANUAL steps + CLAUDE REVIEW)
