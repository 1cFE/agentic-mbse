# Current Work

**Last Updated**: 2026-01-23

---

## Active Work

*No active work items*

---

## Recently Completed

### 2026-01-23: ITEM-SYMLINK-001 Tool-Owned File Safety

Added hash-based modification detection for tool-owned files. Re-running `init` now warns before overwriting local modifications, with options to skip, backup, or overwrite. Also added `LOCAL_GUIDE.md` template for project-specific customizations.

### 2026-01-23: ITEM-REGTEST-001 Model Regression Testing

Added pytest-compatible testing infrastructure for SysML models. `agentic-mbse init` creates `tests/models/` with example tests. Updated spec/plan/implement commands to include test phases. Validated end-to-end in fusion-tea.

### 2026-01-23: ITEM-RENAME-001 Rename `project/` to `modeling_pm/`

Renamed the modeling project management directory from `project/` to `modeling_pm/` for clearer semantic distinction from `.project/` (tool development). Updated CLI, templates, all commands, agents, and documentation across 4 phases.

### 2026-01-16: ITEM-SYSIDE-001 SysIDE v0.8.4 Upgrade

Upgraded syside CLI and Python package from 0.8.1 to 0.8.4. Added versioned documentation structure with compatibility symlinks. 348 new markdown files scraped from docs.sensmetry.com.

### 2026-01-15: ITEM-LEARNING-001 Agent Learning Feedback Loop

Created `/record-learning` skill for capturing session insights to `modeling_pm/learnings/RAW_LEARNINGS.md`. Agents can reflect on conversation and record validated patterns for future reference.

### 2026-01-15: ITEM-DEVMODE-001 Development Mode

Added `--dev` flag to `agentic-mbse init` that creates symlinks for tool-owned files instead of copies. Enables bidirectional editing between agentic-mbse and domain projects.

### 2026-01-15: ITEM-GUIDE-001 Progressive Disclosure Restructure

Restructured MODELING_GUIDE.md.template from 1,497 lines to 205 lines using progressive disclosure pattern. Created 12 pattern docs in `docs/patterns/` with comprehensive reference material.

---

## Up Next

1. Review external work tracking (LCOE costing, Visualization in fusion-tea)
2. Example Store for Modeling Agents (ITEM-EXAMPLES-001)
3. PDF Extraction Header Consistency (TASK-PDF-001)

---

## Session Notes

### 2026-01-23

- Archived `project-rename` and `syside-084-upgrade` from active to completed
- Added tracking items for external work in fusion-tea (LCOE, Visualization)
- Added investigation item for symlink scope (related to fusion-tea overwrite issue)
- Completed and archived ITEM-REGTEST-001 (Model Regression Testing) - 4 phases
- Completed and archived ITEM-SYMLINK-001 (Tool-Owned File Safety) - 5 phases
