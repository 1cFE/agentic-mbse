# Current Work

**Last Updated**: 2026-02-10

---

## Active Work

*No items in progress — branch `adr004-005` ready for PR.*

---

## Recently Completed

### 2026-02-10: EPIC-COMPATTR-001 Computed Attribute Integration

Integrated sysml-codegen ATTR-EXPR (Phase 2) changes into agentic-mbse. FORMULA computed attributes (`attribute area = length * width`) are now valid per ADR-002 Amendment. 886 tests passing.

Key deliverables:
- `src/agentic_mbse/validation/adr002.py` — `_is_formula_pattern()` V2 exemption with 4-layer sibling/calc-output checks
- `docs/patterns/adr002-calculations.md` — Expression taxonomy, decision flow, FORMULA section
- `docs/patterns/expose-pattern.md` — FORMULA vs EXPOSE distinction
- `claude/commands/implement-model.md` + `design-model.md` — FORMULA guidance
- `project_templates/MODELING_GUIDE.md.template` — Updated decision tree + Computed Attributes section
- 7 new test cases in `tests/test_sysml/test_adr002.py`

### 2026-02-08: EPIC-PDFV3-001 PDF Extraction v3

Claude-powered document structure detection pipeline. 4-layer extraction (pymupdf4llm base → GMFT tables → Claude structure repair → AI quality repair). Benchmarked on 12-doc corpus: 4/5 new docs produce usable INDEX files, zero regressions on original 7 docs. 881 tests passing.

Key deliverables:
- `src/agentic_mbse/extraction/` — 11 modules, ~3,000 lines
- `agentic-mbse extract` CLI subcommand with `--enhance`, `--structure-only`, `--model` flags
- `claude/skills/pdf-analysis/` — interactive PDF extraction skill
- 9 new test files, 3,824 lines of test coverage

### 2026-02-03: Architecture Redesign (4 Epics)

Complete toolkit redesign across 4 phases:

**EPIC-ARCH-001 Structure** — 4-directory architecture (`knowledge/`, `modeling_project/`, `work/`, `data/`), new/revised project templates, YAML frontmatter schemas, cmd_init rewiring, 80+ tests updated.

**EPIC-ARCH-002 Knowledge** — 9 new skills (epic-decomposition, model-validation, pdf-analysis, project-structure, record-learning, requirements-tracking, source-traceability, sysml-conventions, toolkit-awareness). Context measurement and extraction mapping complete.

**EPIC-ARCH-003 Commands** — All 9 existing commands refactored to lean ~300-line format. 5 new commands (analyze-models, formalize-intent, quick-model, review-model, status). All registered in installation pipeline. sysmlv2-doc-analyzer deprecated.

**EPIC-ARCH-004 PM Engine** — 8 typed parsers, deterministic state derivation, dashboard generator, 14 PM mutation operations, CLI subcommands (`agentic-mbse pm`, `agentic-mbse status`). 3,267 lines of PM tests.

### 2026-01-23: ITEM-SYMLINK-001 Tool-Owned File Safety

Hash-based modification detection for tool-owned files. Re-running `init` warns before overwriting local modifications.

### 2026-01-23: ITEM-REGTEST-001 Model Regression Testing

pytest-compatible testing infrastructure for SysML models. `tests/models/` with example tests.

### 2026-01-23: ITEM-RENAME-001 Rename `project/` to `modeling_pm/`

Renamed modeling project management directory for clearer semantic distinction.

---

## Up Next

1. Merge `adr004-005` branch to main (PR pending)
2. EPIC-LCOE-001: LCOE Costing Patterns (tracking — active in fusion-tea)
3. EPIC-VIZ-001: Visualization Tool Integration (tracking — active in fusion-tea)
4. PDF Skill Deployment: Docling MCP setup during init (spec drafted)

---

## Session Notes

### 2026-02-10

- EPIC-COMPATTR-001 completed: all 4 items (V2 validation, pattern docs, agent commands, modeling guide)
- Archived 3 work items to `.project/completed/`: compattr-v2-formula, pattern-docs-formula-taxonomy, formula-guidance-commands-template
- Epic closed, backlog updated, audit passed (886 tests, zero regressions)

### 2026-02-08

- Archived 31 completed active work items to `.project/completed/`
- Updated BACKLOG.md: EPIC-CMDREV-001 superseded, architecture epics complete, PDFV3 complete
- Added lingering TODOs to backlog (operations.py stubs, TASK-PDF-001 superseded)
- Prepared PR for pdf-extract → master
