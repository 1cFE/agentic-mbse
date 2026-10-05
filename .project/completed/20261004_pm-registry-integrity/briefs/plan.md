# Brief: plan — pm-registry-integrity

**Sent:** 2026-10-04 by the orchestrator. **Stage:** `/_my_plan`. **Inputs:** `spec.md` (contract, two reviews closed) and `design.md` (approved after review and re-check; see `design-review.md`). Write `plan.md` beside them.

## What this work is for

[AGENT, re-derived] Registry entries and their IDs are stable referents that other artifacts cite by spelling. The plan's job is to get the design implemented in an order where every phase leaves the suite green and each defect is proven closed by a test that was red first.

## Hard requirements on the plan

- **Red first, per defect.** E1 (three-record reproduction), the archive-note allocation test (`DI-001`..`DI-011` under a note naming `DI-014` → `DI-015`), and the `update-validation`-on-an-escaped-row test are each written and shown failing against unchanged code before the phase that fixes them. The plan says so in the phase's checklist, and the implementer records the red run's output in the Implementation Record.
- **Phases follow the design's three parts** so each is independently reviewable: (1) cell splitter and escape pair, both callers switched, `_format_table_row` escaping, R8 refusals; (2) ID discovery `_registry_ids` with the D6 boundary, all eight allocation sites, reservation warnings (D7), every Appendix A boundary case as a test; (3) backlog writer write-back (D8) with R1 refusals, `_single_match` lookups (M1), `register_intent` single-write (m2), remaining R-series refusals. A final phase runs E2 for all seven registries and the E3 suite check.
- **Each phase ends with:** `uv run pytest tests/test_pm_*.py`, `uv run ruff check src/ tests/`, `uv run ruff format --check src/ tests/`, `uv run mypy src/`. Name them in the checklist. The full suite (`uv run pytest tests/`) runs in the last phase.
- **E3 and E4 belong to the orchestrator.** The plan must not have the implementer run or edit `.orchestrate-logs/ft-snapshot/e4_check.py` or `snapshot_parse.py`; it lists them as orchestrator-run acceptance checks after the last phase. The implementer may read the fusion-tea copies there to understand real data.
- **Test placement.** Pin behaviour next to what it tests: splitter and frontmatter reader tests in `tests/test_pm_parser.py`, allocation and refusal tests in `tests/test_pm_operations.py`. A new file only if the design's `TestRegistryIds` grouping reads better there; say which.
- **No new module** unless the design says so (D11 says none).
- Keep the plan readable in one pass: a checklist per phase, one line per item, with the design decision or spec criterion each item serves in brackets. Multi-session is possible, so checkboxes and an Implementation Record section are required.

End with `ARTIFACT: .project/active/pm-registry-integrity/plan.md`.
