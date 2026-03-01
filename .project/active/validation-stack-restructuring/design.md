# Design: Validation Stack Restructuring (8 → 6 Levels)

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-27
**Branch:** TBD (will branch from `main`)
**Commit:** f4446b2

---

## Overview

Restructure the validation stack from 8 levels to 6 by deleting stubs, merging application-specific checks into a single architecture level, and renumbering. No validation logic changes — restructuring and renumbering only.

## Related Artifacts

- **Spec:** `.project/active/validation-stack-restructuring/spec.md`
- **Research:** `.project/research/20260227-195415_validation-stack-audit.md`

---

## Research Findings

### Current Module Structure

| File | Level | Entry Function | Lines |
|------|-------|---------------|-------|
| `level1_syntax.py` | 1 | `validate_syntax(models_path)` | 118 |
| `level2_structure.py` | 2 | `validate_structure(models_path)` | 442 |
| `level3_dataflow.py` | 3 | `validate_dataflow(models_path)` | 149 |
| `level4_constraints.py` | 4 | `analyze_constraints(models_path)` | 108 |
| `level5_semantic.py` | 5 | `validate_semantic(models_path)` | 170 |
| `level6_traceability.py` | 6 | `validate_traceability(models_path)` | 154 |
| `level7_architecture.py` | 7 | `validate_architecture(models_path)` | 171 |
| `level8_codegen.py` | 8 | `validate_codegen_readiness(models_path, design_path_filter)` | 610 |
| `adr002.py` | — | 3 check functions | 511 |
| `runner.py` | — | `run_all_checks(...)` | 221 |
| `common.py` | — | Shared utilities | 192 |
| `__init__.py` | — | Package exports | 38 |

### ADR-002 Integration in L2 (to be moved to L6)

`level2_structure.py:24-35` imports and `level2_structure.py:378-381` calls:
- `check_calc_def_locations(model)` — V1: calc defs in library/ not designs/
- `check_static_expressions(model)` — V2: design expressions statically evaluable
- `check_supported_operators(model)` — V4: only supported operators

All three produce `ValidationIssue(level=2, ...)` — see `adr002.py:63`, `adr002.py:135`, `adr002.py:495`.

L2 also counts ADR-002 metrics in its result (`level2_structure.py:410-418`).

### L5 Constraint Coverage Stub (to be absorbed into L4)

`level5_semantic.py:60-104` — `check_constraint_coverage(model)`:
- Counts `AttributeUsage` and `ConstraintUsage` elements
- `constrained_attrs` is always empty set (line 77)
- Returns `(unconstrained_list, metrics_dict)` with coverage always 0%
- Metrics: `Total attributes`, `Constrained`, `Unconstrained`, `Coverage`

### L7 Architecture Check (to merge into new L6)

`level7_architecture.py:94-152` — `validate_architecture(models_path)`:
- Looks for `manifest.yaml` in `models/designs/*/`
- Uses `load_manifest(design_path)` to parse YAML
- Uses `check_subsystem_composition(model, manifest)` to verify expected subsystems
- Returns success with warning if no manifests found
- Uses unstructured string issues (not `ValidationIssue` objects)
- Imports: `yaml`, `SysideAdapter`, `common` utilities

### L8 Codegen Readiness (to merge into new L6)

`level8_codegen.py:476-598` — `validate_codegen_readiness(models_path, design_path_filter)`:
- 5 check functions, all producing `ValidationIssue(level=8, ...)`
- `design_path_filter` parameter defaults to `"designs"` — needed for L6
- Uses `evaluate_true_static_expression` from `agentic_mbse.sysml.expression`
- Success criteria: only ERRORs cause failure (line 559)
- All 7 `L8_*` ValidationCodes referenced in metrics dict (lines 570-591)

### ValidationCode Enum

`sysml/types.py:66-95` — 7 entries with `L8_` prefix need renaming to `L6_`.

### Runner Registry

`runner.py:48-57` — `QUALITY_CHECKS` list of 8 `(name, func)` tuples.
`runner.py:82` — hardcoded `specific_level > 8` check.
`runner.py:191` — `choices=range(1, 9)` in standalone argparse.

### CLI

`cli/__init__.py:1090-1096` — `choices=range(1, 9)`, help text says "1-8".

### Tests

`tests/test_sysml_quality_checks.py`:
- `TestLevel7Architecture` (lines 664-698): 2 tests, assert `result.level == 7`
- `TestLevel8CodegenReadiness` (lines 802-923): 9 tests, assert `result.level == 8`, reference `L8_*` codes
- `TestEndToEnd` (lines 700-799): 6 tests, assert 8 levels run, `levels_run == [1,2,3,4,5,6,7,8]`, `total_checks == 8`
- Tests import from specific module paths (`level7_architecture`, `level8_codegen`)

### Documentation

- `SKILL.md:15-40` — "8-level" heading, 8-row table
- `SKILL.md:19` — "Levels 4-8 are informational"
- `CLAUDE.md:84` — `--level=3` example, "1-8" in comment
- `CLAUDE.md:100-108` — 8-level list
- `project_templates/README.md.template:74` — "8-level quality checks"

---

## Proposed Design

### High-Level Architecture

The restructuring is a mechanical renumbering + module consolidation with zero logic changes. The new structure:

```
validation/
├── level1_syntax.py        # Unchanged
├── level2_structure.py      # Remove ADR-002 imports/calls
├── level3_dataflow.py       # Unchanged
├── level4_constraints.py    # Absorb constraint coverage from old L5
├── level5_traceability.py   # NEW FILE (renamed from level6_traceability.py)
├── level6_architecture.py   # NEW FILE (merged L7 + L8 + ADR-002 calls)
├── adr002.py                # Update level fields: 2→6
├── runner.py                # 6 entries, range 1-6
├── common.py                # Update comment: 1-6
├── __init__.py              # Update exports
```

### Component 1: level2_structure.py — Remove ADR-002

**What changes:**
- Remove `adr002` imports (lines 24-35)
- Remove ADR-002 calls (lines 378-381)
- Remove ADR-002 metrics from `result.metrics` (lines 410-418)
- Update success calculation: currently `success=len(all_issues) == 0` — this remains correct since ADR-002 issues won't be in the list anymore

**Impact:** L2 becomes purely generic structural checks (unused defs, unbound inputs, literal/undefined bindings, orphaned elements stub).

### Component 2: level4_constraints.py — Absorb Constraint Coverage

**What changes:**
- Add `check_constraint_coverage(model)` function (moved from `level5_semantic.py:60-104`)
- Add `get_element_location`, `get_qualified_name` imports from `.common`
- Add `SysideAdapter` is already imported
- Call `check_constraint_coverage()` in `analyze_constraints()` and merge its metrics into the result

**New function** (copied from L5, no logic change):
```python
def check_constraint_coverage(model: Any) -> tuple[list[str], dict]:
    """Calculate constraint coverage: which attributes are constrained."""
    # ... exact same code from level5_semantic.py:60-104
```

**Updated `analyze_constraints()`:**
- After constraint counting, call `check_constraint_coverage(model)`
- Merge coverage metrics into L4's existing metrics dict using coverage-specific keys (`Total attributes`, `Constrained`, `Unconstrained`, `Coverage`) — these do not collide with existing L4 keys (`Total constraints`, `ConstraintUsage`, `ConstraintDefinition`)
- Add unconstrained attrs as warnings (first 10, same as L5 did)
- `success=True` remains unchanged (informational only)

```python
# In analyze_constraints(), after existing constraint counting:
unconstrained, coverage_metrics = check_constraint_coverage(model)
result.metrics.update(coverage_metrics)
for attr in unconstrained[:10]:
    result.warnings.append(f"Unconstrained attribute: {attr}")
if len(unconstrained) > 10:
    result.warnings.append(f"... and {len(unconstrained) - 10} more")
```

### Component 3: level5_semantic.py — Delete

**Action:** Delete the entire file. All useful content (`check_constraint_coverage`) moves to `level4_constraints.py`. The `check_unit_consistency` stub returns `[]` and has no value.

### Component 4: level5_traceability.py — Renamed from level6_traceability.py

**What changes (minimal):**
- Rename file: `level6_traceability.py` → `level5_traceability.py`
- Update all `level=6` → `level=5` (lines 109, 110, 112, 120, 129, 132)
- Update `level_name` strings where they appear
- Update `print_header("Traceability & Documentation", 6)` → `5`
- Function name stays `validate_traceability()` — no signature change

### Component 5: level6_architecture.py — New Merged Module

**Purpose:** Combines all application-specific checks into one level: ADR-002 rules, manifest validation, codegen readiness.

**Structure:**
```python
"""
Level 6: Architecture & Pipeline Readiness

Application-specific validation: ADR-002 rules, manifest subsystem
checks, and codegen readiness requirements.
"""

# Imports from old L7 and L8:
import yaml
from pathlib import Path
from agentic_mbse.sysml.expression import evaluate_true_static_expression
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.sysml.types import Severity, ValidationCode, ValidationIssue
from .adr002 import check_calc_def_locations, check_static_expressions, check_supported_operators
from .common import (QualityCheckResult, discover_sysml_files, get_element_location,
                     get_qualified_name, load_sysml_model, print_header, print_result,
                     EXIT_SUCCESS, EXIT_FAILURE)

# --- Functions from L7 (no changes) ---
def load_manifest(design_path: Path) -> dict | None: ...
def check_subsystem_composition(model, manifest) -> list[str]: ...

# --- Manifest orchestration (extracted from old L7's validate_architecture) ---
def _check_manifests(models_path: str, model) -> tuple[list[str], int]: ...

# --- Functions from L8 (level=8 → level=6 in ValidationIssue) ---
def check_qualified_names(model) -> list[ValidationIssue]: ...
def check_calc_def_structure(model) -> list[ValidationIssue]: ...
def _extract_chain_path(expr) -> str | None: ...
def _extract_reference_path(expr) -> str | None: ...
def check_binding_formats(model) -> tuple[list[ValidationIssue], int]: ...
def check_design_attr_completeness(model, design_path_filter) -> tuple[list[ValidationIssue], int]: ...

# --- New orchestrator (combines L7 + L8 + ADR-002) ---
def validate_architecture(models_path: str, design_path_filter: str | None = "designs") -> QualityCheckResult:
    """Main entry point for Level 6 validation."""
    ...
```

**Orchestrator function `validate_architecture()`:**

```python
def validate_architecture(
    models_path: str,
    design_path_filter: str | None = "designs",
) -> QualityCheckResult:
    print_header("Architecture & Pipeline Readiness", 6)

    files = discover_sysml_files(models_path)
    if not files:
        return QualityCheckResult(level=6, level_name="Architecture & Pipeline Readiness",
                                  success=True, warnings=["No SysML files found"])

    model, diagnostics = load_sysml_model(files)

    all_issues: list[ValidationIssue] = []

    # ADR-002 checks (from old L2)
    all_issues.extend(check_calc_def_locations(model))
    all_issues.extend(check_static_expressions(model))
    all_issues.extend(check_supported_operators(model))

    # Codegen readiness checks (from old L8)
    all_issues.extend(check_qualified_names(model))
    all_issues.extend(check_calc_def_structure(model))
    binding_issues, num_bindings = check_binding_formats(model)
    all_issues.extend(binding_issues)
    design_attr_issues, num_design_attrs = check_design_attr_completeness(model, design_path_filter)
    all_issues.extend(design_attr_issues)

    # Manifest checks (from old L7)
    manifest_issues, manifests_checked = _check_manifests(models_path, model)

    # Build result — ERROR-only failure criteria (see Key Decisions below)
    success = not any(i.severity == Severity.ERROR for i in all_issues)
    # Manifest issues are unstructured strings; also fail if any found
    if manifest_issues:
        success = False

    result = QualityCheckResult(
        level=6, level_name="Architecture & Pipeline Readiness",
        success=success,
        metrics={...},  # Combined metrics from ADR-002, codegen, manifest
    )

    for issue in all_issues:
        result.add_issue(issue)
    for issue_str in manifest_issues:
        result.issues.append(issue_str)

    return result
```

**`_check_manifests` implementation:**

```python
def _check_manifests(models_path: str, model) -> tuple[list[str], int]:
    """Check manifest subsystem composition. Returns (issues, manifests_checked).

    Unlike old L7's validate_architecture(), this does NOT early-return a
    QualityCheckResult. Missing designs/ or no manifests → empty list, not failure.
    The calling orchestrator handles these as "no manifest issues found."
    """
    designs_path = Path(models_path) / "designs"
    if not designs_path.exists():
        return [], 0

    manifests_found = list(designs_path.glob("*/manifest.yaml"))
    if not manifests_found:
        return [], 0

    issues = []
    for manifest_path in manifests_found:
        manifest = load_manifest(manifest_path.parent)
        if manifest:
            missing = check_subsystem_composition(model, manifest)
            for subsystem in missing:
                issues.append(
                    f"Missing subsystem '{subsystem}' in {manifest_path.parent.name}"
                )
    return issues, len(manifests_found)
```

**Key decisions:**
- The `design_path_filter` parameter is preserved from `validate_codegen_readiness` for backward compatibility.
- Manifest checks remain unstructured strings (legacy pattern from L7). Converting them to `ValidationIssue` is out of scope per spec ("no behavioral changes").
- Success is determined by: no structured ERROR-severity issues AND no manifest issues.
- **Success criteria vs old L2:** L6 uses ERROR-only failure (`not any(severity == ERROR)`), while old L2 used any-issue failure (`len(all_issues) == 0`). ADR-002 issues move from L2 to L6. This is safe because all three ADR-002 checks produce `severity=Severity.ERROR` (`adr002.py:64`, `adr002.py:136`, `adr002.py:496`), so they fail L6 just as they failed L2. If ADR-002 severities are changed in the future, the behavior would differ — ERRORs still fail L6, but WARNINGs would not (whereas they did fail L2).

### Component 6: adr002.py — Update Level Fields

**What changes:**
- 3 locations where `ValidationIssue(level=2, ...)` → `ValidationIssue(level=6, ...)`
  - `adr002.py:63` (in `check_calc_def_locations`)
  - `adr002.py:135` (in `check_static_expressions`)
  - `adr002.py:495` (in `check_supported_operators`)
- Update module docstring: "integrated into Level 2" → "integrated into Level 6"

### Component 7: sysml/types.py — Rename ValidationCode

**What changes:**
- Rename 7 enum members from `L8_*` to `L6_*`:
  ```python
  # Before                              # After
  L8_MISSING_QUALIFIED_NAME      →  L6_MISSING_QUALIFIED_NAME
  L8_INVALID_QUALIFIED_NAME      →  L6_INVALID_QUALIFIED_NAME
  L8_CALC_DEF_NO_OUTPUT          →  L6_CALC_DEF_NO_OUTPUT
  L8_CALC_DEF_NO_DIRECTION       →  L6_CALC_DEF_NO_DIRECTION
  L8_INVALID_BINDING_FORMAT      →  L6_INVALID_BINDING_FORMAT
  L8_DESIGN_ATTR_INCOMPLETE      →  L6_DESIGN_ATTR_INCOMPLETE
  L8_DESIGN_ATTR_UNEXTRACTABLE   →  L6_DESIGN_ATTR_UNEXTRACTABLE
  ```
- Also rename the string values: `"L8_MISSING_QUALIFIED_NAME"` → `"L6_MISSING_QUALIFIED_NAME"` etc.
- Update comment: `# Level 8: Codegen Readiness` → `# Level 6: Architecture & Pipeline Readiness`

### Component 8: runner.py — Update Registry

**What changes:**
- Update docstring: "8 quality levels" → "6 quality levels"
- Update `QUALITY_CHECKS` to 6 entries:
  ```python
  QUALITY_CHECKS = [
      ("Level 1: Syntax Validation", validate_syntax),
      ("Level 2: Structural Completeness", validate_structure),
      ("Level 3: Dependency Integrity", validate_dataflow),
      ("Level 4: Constraint Coverage", analyze_constraints),
      ("Level 5: Traceability & Documentation", validate_traceability),
      ("Level 6: Architecture & Pipeline Readiness", validate_architecture),
  ]
  ```
- Update imports: remove `validate_semantic`, `validate_codegen_readiness`; add `validate_architecture` from new module; update `validate_traceability` import path
- Update `run_all_checks()` docstring: "1-8" → "1-6"
- Update hardcoded range check: `specific_level > 8` → `specific_level > 6` (line 82)
- Update standalone `main()`: `choices=range(1, 9)` → `choices=range(1, 7)`, help text

### Component 9: __init__.py — Update Exports

**What changes:**
- Remove: `validate_semantic`, `validate_codegen_readiness` imports
- Update: `validate_traceability` import from `level5_traceability`
- Add: `validate_architecture` import from `level6_architecture`
- Update `__all__` list accordingly
- Update docstring: "8-level" → "6-level"

### Component 10: cli/__init__.py — Update CLI

**What changes:**
- `choices=range(1, 9)` → `choices=range(1, 7)` (line 1093)
- Help text: "1-8" → "1-6" (line 1095)

### Component 11: common.py — Update Comments

**What changes:**
- `QualityCheckResult.level` comment: `# 1-8` → `# 1-6` (line 24)

### Component 12: Tests — Update for 6 Levels

**Test file: `tests/test_sysml_quality_checks.py`**

Changes:
1. **Rename `TestLevel7Architecture`** → `TestLevel6Architecture`
   - Update imports: `level7_architecture` → `level6_architecture`
   - Update assertions: `result.level == 7` → `result.level == 6`
   - Update function import: `validate_architecture` (name stays the same)

2. **Rename `TestLevel8CodegenReadiness`** → merge into `TestLevel6Architecture` or rename to `TestLevel6CodegenReadiness`
   - Update imports: `level8_codegen` → `level6_architecture`
   - Update assertions: `result.level == 8` → `result.level == 6`
   - Update `level_name` assertions: `"Codegen Readiness"` → `"Architecture & Pipeline Readiness"`
   - Update `L8_*` references → `L6_*`

3. **Update `TestEndToEnd`:**
   - `total_checks == 8` → `total_checks == 6`
   - `levels_run == [1,2,3,4,5,6,7,8]` → `levels_run == [1,2,3,4,5,6]`
   - `len(result.results) == 8` → `len(result.results) == 6`
   - Remove L8-specific integration tests or update to L6
   - `specific_level=8` → `specific_level=6`

4. **Update `TestLevel6Traceability`:**
   - Import from `level5_traceability` instead of `level6_traceability`
   - `result.level == 6` → `result.level == 5`
   - The class name should update to `TestLevel5Traceability`

5. **Add distinctness fixtures** (per spec FR-8): one SysML fixture per level where only that level fails. These are new additions — see Validation Approach section.

### Component 13: Documentation Updates

**SKILL.md** (`claude/skills/model-validation/SKILL.md`):
- "8-level" → "6-level" in heading and description
- Table: 8 rows → 6 rows with new names
- "Levels 4-8" → "Levels 4-6"
- CLI examples: "1-8" → "1-6"

**CLAUDE.md**:
- Line 84: `# Run specific validation level (1-8)` → `(1-6)`
- Lines 100-108: Replace 8-level list with 6-level list

**README.md.template** (`project_templates/README.md.template`):
- Line 74: "8-level quality checks" → "6-level quality checks"

---

## File Change Summary

| File | Action | Effort |
|------|--------|--------|
| `validation/level5_semantic.py` | **Delete** | Trivial |
| `validation/level6_traceability.py` | **Rename** → `level5_traceability.py`, update level numbers | Small |
| `validation/level7_architecture.py` | **Delete** (merged into new L6) | Trivial |
| `validation/level8_codegen.py` | **Delete** (merged into new L6) | Trivial |
| `validation/level6_architecture.py` | **New** — combined L7+L8+ADR-002 orchestration | Medium |
| `validation/level2_structure.py` | Remove ADR-002 imports/calls/metrics | Small |
| `validation/level4_constraints.py` | Add constraint coverage from old L5 | Small |
| `validation/adr002.py` | `level=2` → `level=6` (3 places) + docstring | Trivial |
| `sysml/types.py` | Rename 7 `L8_*` → `L6_*` enum members | Trivial |
| `validation/runner.py` | 6 entries, range 1-6, update imports | Small |
| `validation/__init__.py` | Update exports | Trivial |
| `validation/common.py` | Update comment | Trivial |
| `cli/__init__.py` | `range(1, 9)` → `range(1, 7)` | Trivial |
| `tests/test_sysml_quality_checks.py` | Renumber, rename classes, update imports | Medium |
| `SKILL.md` | 6-level table and text | Small |
| `CLAUDE.md` | Update validation section | Small |
| `project_templates/README.md.template` | "8-level" → "6-level" | Trivial |

**Estimated:** ~14 files in this repo.

**FR-10 downstream (fusion-tea):** Documentation-only updates in the fusion-tea repo, tracked separately. Exact files from the spec:
- `fusion-tea/README.md` — "8-level" → "6-level", `--level` examples
- `fusion-tea/knowledge/research/approved/20260106-065431_cost-architecture-patterns.md` — `--level 9` reference
- `fusion-tea/.project/active/gap1-default-value-debug/fix-plan.md` — `L8_DESIGN_ATTR_UNEXTRACTABLE`, `level8_codegen.py` refs
- `fusion-tea/.project/active/gap1-default-value-debug/findings.md` — `level8_codegen.py` refs
- `fusion-tea/.project/active/gap1-default-value-debug/spec.md` — "levels 1-8" → "levels 1-6"

No fusion-tea Python code changes needed (confirmed: only imports `common` and `SysideAdapter`). These changes should be applied after the main restructuring lands on `main`.

---

## Potential Risks

1. **Missing a hardcoded `8`**: A grep for `level.*8`, `1-8`, `range(1, 9)` across the codebase should catch all. The research phase found the exhaustive list above.

2. **Manifest issues as unstructured strings**: L7 uses `list[str]` for issues, not `ValidationIssue`. The new L6 needs to handle both. Design above accounts for this by appending manifest strings to `result.issues` directly.

3. **Import path changes in tests**: Tests import from specific module names (`level7_architecture`, `level8_codegen`). All need updating. A search for these import paths will catch them all.

4. **`validate_architecture` function name collision**: Both old L7 and new L6 use `validate_architecture`. Since old L7 is deleted, there's no collision — but callers of the old `validate_architecture` (runner.py) need to point to the new module. The runner imports by function name, and the new module uses the same name, so the import source just changes.

5. **`design_path_filter` parameter**: The new `validate_architecture()` must accept this parameter (from old L8's `validate_codegen_readiness`). However, runner.py calls validation functions with just `models_path` — so the parameter needs a default value of `"designs"` (which it already has in L8). The runner call `check_func(models_path)` will work fine since `design_path_filter` has a default.

---

## Integration Strategy

This is a restructuring within the `validation/` package. No external API changes beyond:
- `--level=7` and `--level=8` are no longer accepted (CLI and programmatic)
- `ValidationCode.L8_*` names change to `L6_*` (enum values also change)
- Import paths change for consumers of `validate_architecture` or `validate_codegen_readiness`

The spec confirmed that the only downstream consumer (fusion-tea) imports only `common` and `SysideAdapter` — no Python code changes needed there.

---

## Validation Approach

### Automated Testing

1. **Run existing test suite after each phase** — `uv run pytest tests/test_sysml_quality_checks.py`
2. **Run linter** — `uv run ruff check src/ tests/`
3. **End-to-end CLI test** — `uv run agentic-mbse validate tests/fixtures/sample_models/`
4. **Verify level count** — end-to-end test asserts 6 levels run

### Distinctness Fixtures (FR-8)

New test fixtures where each level fails uniquely. These verify the restructuring preserved the right checks at each level. **Detailed fixture design deferred to `/_my_plan`** — the planning phase should specify exact SysML content and test structure.

**Location:** `tests/fixtures/distinctness/` — one subdirectory per level.

**Fixture concepts:**

- **L1 only** (`tests/fixtures/distinctness/l1_syntax_error/`): A `.sysml` file with invalid syntax (e.g., unclosed brace). Passes no levels.
- **L2 only** (`tests/fixtures/distinctness/l2_unbound_input/`): Valid syntax, but a `CalculationUsage` with an unbound input. No ADR-002 violation (calc defs in `library/`, expressions are static, operators supported). L1 passes, L2 fails.
- **L3 only** (`tests/fixtures/distinctness/l3_circular_import/`): Valid syntax, complete structure, but two packages that import each other. L1-L2 pass, L3 fails.
- **L6 only** (`tests/fixtures/distinctness/l6_architecture/`): Valid syntax, complete structure, no circular imports, but a calc def placed in `designs/` (ADR-002 V1 violation). L1-L3 pass, L6 fails.

**Test structure:** Each fixture gets a test that runs `run_all_checks(fixture_path, fail_fast=False)` and asserts:
- Exactly the target level has `success=False`
- All other blocking levels have `success=True`

**L4 and L5** are WIP/informational and cannot fail. Distinctness is demonstrated by asserting unique metrics/warnings are present (e.g., L4 reports constraint counts, L5 reports doc coverage) rather than by failure.

### Manual Verification

- `uv run agentic-mbse validate --level=6 tests/fixtures/sample_models/` — should run architecture checks
- `uv run agentic-mbse validate --level=7 tests/fixtures/sample_models/` — should be rejected

---

Next Step: After approval → `/_my_plan` for phased implementation plan
