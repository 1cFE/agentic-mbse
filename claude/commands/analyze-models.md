---
name: analyze-models
description: Analyze current model state and produce structured reports on structure, compliance, and health
skills: [project-structure, model-validation]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Analyze Models Command

**Purpose:** UNDERSTAND current model state — structure, compliance, and health indicators.
**Input:** User-specified analysis scope (which models, which aspects)
**Output:** `work/analysis/YYYYMMDD-HHMMSS_topic.md`

This is internal analysis — examining what's already built, not exploring external sources (that's `/research`). It produces operational intelligence: reports that inform what to work on next, where debt is accumulating, and whether the models meet project standards.

When invoked without a scope, ask what the user wants to analyze and suggest options: full project health, a specific package, compliance audit, or debt inventory.

## Skills Referenced

- **project-structure**: Library vs designs separation, file organization, 4-directory model. Consult when analyzing package structure and cross-file dependencies.
- **model-validation**: Quality pyramid, validation levels, CLI usage. Consult when computing health indicators and running validation checks.

## Process

### 1. Define Scope

Ask the user what to analyze. Three common scopes:

- **Full project health**: All models, all aspects — structure, compliance, health
- **Package-focused**: A specific directory (e.g., `models/library/calculations/power_balance/`)
- **Aspect-focused**: One concern across all models (e.g., "which PR-XXX rules are violated?", "what has no test coverage?")

Confirm scope before proceeding. For large projects, a focused scope produces more actionable results.

### 2. Analyze

Run the applicable analyses in parallel using sub-agents for efficiency — spawn Explore agents to inventory model files, check compliance, and scan for debt markers concurrently. Not all analyses apply to every scope — pick the relevant ones.

**Structure** — Parse `models/` to inventory:
- Files, packages, and their organization (library/ vs designs/)
- Definitions (part defs, calc defs, port defs, etc.) and usages
- Cross-file dependencies (imports, bindings between files)
- Orphaned files or definitions with no usages

**Compliance** — Read `modeling_project/REQUIREMENTS.md` and check each PR-XXX rule against the models in scope. Read `modeling_project/ARCHITECTURE.md` and check AD-XXX adherence. Categorize as: compliant, violated, or not applicable to this scope.

**Health indicators** — Per the **model-validation** skill:
- Run validation and report per-level results:
  ```bash
  uv run agentic-mbse validate models/
  ```
- Check test coverage: which calc defs in scope have corresponding tests in `tests/models/`?
- Check traceability coverage: which definitions have entries in `data/traceability_matrix.csv`? Which are missing?
- Identify debt markers: TODO/FIXME comments, missing doc comments, placeholder values, incomplete bindings
- Check `modeling_project/VALIDATION_MATRIX.md` for SV-XXX entries relevant to this scope — how many are passing, failing, pending?

### 3. Synthesize

Combine findings into a coherent report. Don't just list everything — interpret:
- What's in good shape and why
- What needs attention and what the impact is
- What's blocking downstream work (codegen readiness, missing tests, failing validation)
- Trends compared to previous analysis reports in `work/analysis/` (if any exist)
- Recommended next actions (specific: "run `/spec-model` for magnet system test coverage" not "improve testing")

### 4. Write Report

Write the report to `work/analysis/` with a timestamped filename:

```bash
# Filename format: YYYYMMDD-HHMMSS_topic.md
# Example: 20260202-143022_power_balance_health.md
```

The report should contain:
- **Scope** — what was analyzed
- **Summary** — 3-5 bullet executive summary
- **Structure** — file/definition inventory, dependency map (when applicable)
- **Compliance** — PR-XXX and AD-XXX check results
- **Health** — validation levels, test coverage, debt markers
- **Recommendations** — prioritized next actions with specific commands to run

Present the summary and key findings to the user. The full report is in the file for reference.

## Guidelines

- Analysis is read-only. Don't modify model files — report what you find.
- Be quantitative where possible: "7 of 12 calc defs have tests" not "some calc defs lack tests."
- Reference specific files and line numbers so findings are actionable.
- If the analysis reveals something that should be a project-wide rule, suggest it — but the promotion happens through `/audit-models`, not here.
- Reports accumulate in `work/analysis/`. They are operational artifacts, not PM-tracked work items.
- For cross-model verification and pattern promotion, use `/audit-models`. This command reports state; `/audit-models` drives changes.

---

**Related Commands:** For external research → `/research` | To act on findings → `/spec-model`, `/audit-models` | Project overview → `/status`
