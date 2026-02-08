# Design: Level 8 Extractability Validation

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-01 22:01:21 UTC
**Branch:** revamp-architecture
**Commit:** 43da445

## Overview

Add two capabilities to Level 8 codegen readiness validation: (1) verify design attribute expressions are numerically extractable, not just present, and (2) make the path filter for design file detection configurable. Three files changed, one new test file.

## Related Artifacts

- **Spec:** `.project/active/l8-extractability-validation/spec.md`
- **Findings (fusion-tea):** `/home/reid/1cfe/fusion-tea/.project/active/gap1-default-value-debug/findings.md`
- **Epic:** EPIC-LCOE-001 in `.project/backlog/BACKLOG.md`

---

## Research Findings

### Current L8 Design Attribute Check (`level8_codegen.py:372-439`)

The function `check_design_attr_completeness()` iterates all `AttributeUsage` elements, filters to those in `designs/` directories, skips calc usage bindings, then checks for `feature_value_expression` presence. The gap: it never evaluates the expression.

Key code path:
1. `SysideAdapter.elements_of_type(model, "AttributeUsage")` — discovers all attributes (line 388)
2. `"designs" not in doc_path.parts` — hardcoded path filter (line 400)
3. `SysideAdapter.is_instance(owner, "CalculationUsage")` — skip calc bindings (line 408)
4. `attr.feature_value_expression is not None` — presence-only check (line 418-421)

### `evaluate_true_static_expression()` (`expression.py:374-475`)

Returns `float` on success. Raises:
- `ValueError` for feature references, unsupported operators, division by zero, malformed expressions
- `TypeError` for `None` input or unknown expression types

The function is thoroughly tested (17 test cases in `tests/test_sysml/test_expression.py:732-964`) but has **no production callers** — only test callers and recursive self-calls. This change will be its first production use.

### Runner Architecture (`runner.py:60-151`)

All level check functions share a uniform signature: `(models_path: str) -> QualityCheckResult`. The runner calls each via `check_func(models_path)` at line 106. This means `design_path_filter` cannot be threaded through the runner without breaking the uniform calling convention.

**Implication for FR-4:** The parameter goes on `validate_codegen_readiness()` and `check_design_attr_completeness()` as optional kwargs with defaults, but the runner continues to call `validate_codegen_readiness(models_path)` without it. Direct callers (tests, scripts, programmatic API) can pass it explicitly.

### Existing Test Patterns (`tests/test_sysml_quality_checks.py:802-923`)

L8 tests use real SysML fixture files in `tests/fixtures/sample_models/` and `tests/fixtures/adr002_violations/`. Tests call `validate_codegen_readiness("tests/fixtures/sample_models/")` directly and assert on `result.structured_issues`, `result.metrics`, and `result.success`.

The existing fixture `valid_calc_usage.sysml` in `tests/fixtures/sample_models/` has design attributes with literal defaults (`input_a : Real = 1.0`). These live in the `sample_models/` directory (not `designs/`), so the current path filter skips them — confirming the spec's observation about vacuous passes.

### Test Fixture Strategy

New fixtures go in `tests/fixtures/l8_extractability/` with two subdirectories:
- `designs/` — valid model with extractable literal defaults (exercises happy path)
- `tests/` — model with non-extractable expressions (exercises error path, also proves configurable filter works on non-`designs/` directories)

The `designs/` subdirectory name matters because it matches the default path filter.

---

## Proposed Design

### Component 1: New ValidationCode (`types.py`)

**File:** `src/agentic_mbse/sysml/types.py:94`

Add one enum member after `L8_DESIGN_ATTR_INCOMPLETE`:

```python
L8_DESIGN_ATTR_UNEXTRACTABLE = "L8_DESIGN_ATTR_UNEXTRACTABLE"
```

### Component 2: Extractability Check and Configurable Filter (`level8_codegen.py`)

**File:** `src/agentic_mbse/validation/level8_codegen.py`

#### 2a: New import

Add at the top of the file (after existing imports from `agentic_mbse.sysml`):

```python
from agentic_mbse.sysml.expression import evaluate_true_static_expression
```

#### 2b: Configurable path filter on `check_design_attr_completeness()`

Change signature from:
```python
def check_design_attr_completeness(
    model: Any,
) -> tuple[list[ValidationIssue], int]:
```

To:
```python
def check_design_attr_completeness(
    model: Any,
    design_path_filter: str | None = "designs",
) -> tuple[list[ValidationIssue], int]:
```

**Semantics:**
- `"designs"` (default) — current behavior, only files with `"designs"` in path components
- `""` or `None` — check all files (no path filtering)
- `"tests"` — only files with `"tests"` in path components

Replace the hardcoded filter at line 400:

```python
# Current:
if "designs" not in doc_path.parts:
    continue

# New:
if design_path_filter:
    if design_path_filter not in doc_path.parts:
        continue
```

When `design_path_filter` is falsy (empty string or `None`), the `if` block is skipped entirely and all files are checked. This preserves the existing behavior of skipping calc usage bindings (owner check at line 404-411) as a separate, always-active filter.

#### 2c: Extractability check after presence check

After the existing presence check block (line 417-434), add the extractability check for attributes that *do* have expressions. Insert after line 421 (`has_value` assignment), before the `if not has_value:` block:

```python
# Check extractability — can codegen get a numeric default?
if has_value:
    try:
        evaluate_true_static_expression(attr.feature_value_expression)
    except (ValueError, TypeError) as e:
        issues.append(
            ValidationIssue(
                level=8,
                severity=Severity.ERROR,
                code=ValidationCode.L8_DESIGN_ATTR_UNEXTRACTABLE,
                message=(
                    f"Design attribute '{attr_name}' has expression but codegen "
                    f"cannot extract a numeric default: {e}"
                ),
                element_name=attr_name,
                location=location,
                suggestion=(
                    "Ensure the attribute value is a literal number or "
                    "static arithmetic expression (no feature references)"
                ),
            )
        )
```

The existing `if not has_value:` block remains unchanged — it catches attributes with no expression at all (`L8_DESIGN_ATTR_INCOMPLETE`). The new block catches attributes that *have* an expression but it's not evaluable (`L8_DESIGN_ATTR_UNEXTRACTABLE`). These are mutually exclusive: an attribute either has no expression or has a non-extractable one.

#### 2d: Thread filter through `validate_codegen_readiness()`

Change signature from:
```python
def validate_codegen_readiness(models_path: str) -> QualityCheckResult:
```

To:
```python
def validate_codegen_readiness(
    models_path: str,
    design_path_filter: str | None = "designs",
) -> QualityCheckResult:
```

Pass through at the call site (line 512):
```python
design_attr_issues, num_design_attrs = check_design_attr_completeness(
    model, design_path_filter=design_path_filter
)
```

The runner at `runner.py:106` calls `check_func(models_path)` — this continues to work because `design_path_filter` has a default. No changes needed to `runner.py`.

#### 2e: Add metric for new code

In the metrics dict (after line 543), add:

```python
"L8_DESIGN_ATTR_UNEXTRACTABLE": len(
    [i for i in all_issues if i.code == ValidationCode.L8_DESIGN_ATTR_UNEXTRACTABLE]
),
```

#### 2f: Update module docstring

Update the docstring at the top of the file to include the new check:

```
4. Design attr completeness - design attrs have values or bindings (FR-7)
5. Design attr extractability - design attr expressions produce numeric defaults (FR-8)
```

### Component 3: Test Fixtures

**Directory:** `tests/fixtures/l8_extractability/`

#### `tests/fixtures/l8_extractability/designs/valid_design.sysml`

A minimal SysML file with design attributes that have extractable literal defaults:

```sysml
package ValidDesignTest {
    import ScalarValues::*;

    part def Component {
        attribute length : Real;
        attribute width : Real;
    }

    part design_instance : Component {
        attribute length : Real = 10.0;
        attribute width : Real = 5.0;
    }
}
```

This exercises: literal defaults pass both presence and extractability checks.

#### `tests/fixtures/l8_extractability/designs/unextractable_design.sysml`

A minimal SysML file with a design attribute whose expression references features:

```sysml
package UnextractableDesignTest {
    import ScalarValues::*;

    part def Component {
        attribute length : Real;
        attribute width : Real;
        attribute area : Real = length * width;
    }

    part design_instance : Component {
        attribute length : Real = 10.0;
        attribute width : Real = 5.0;
        attribute area : Real = length * width;
    }
}
```

The `area` attribute in `design_instance` has a `feature_value_expression` (passes presence check) but `evaluate_true_static_expression()` raises `ValueError` because it references `length` and `width`. This exercises the new `L8_DESIGN_ATTR_UNEXTRACTABLE` check.

**Note:** Whether syside parses `area : Real = length * width` in a `part` (not a `calc def`) as an OperatorExpression with FeatureReferences depends on syside's AST representation. If syside resolves these to concrete values at parse time, we may need a different fixture pattern. The implementation should verify the fixture produces the expected AST before committing. If the straightforward pattern doesn't work, an alternative is to use the mock fixtures from `tests/test_sysml/conftest.py` for unit tests instead.

#### `tests/fixtures/l8_extractability/tests/test_design.sysml`

Same content as `valid_design.sysml` but in a `tests/` subdirectory (not `designs/`). Proves the configurable path filter works:
- Default filter (`"designs"`) skips this file
- Filter `"tests"` or `""` picks it up

### Component 4: Test Cases

**File:** `tests/test_l8_extractability.py`

New test file with focused tests for the new functionality. Uses the fixture files above.

#### Test Cases

1. **`test_valid_design_passes_extractability`**
   - Load `tests/fixtures/l8_extractability/designs/valid_design.sysml`
   - Call `validate_codegen_readiness(path)`
   - Assert no `L8_DESIGN_ATTR_UNEXTRACTABLE` issues
   - Assert `Design attrs checked` > 0 in metrics

2. **`test_unextractable_design_produces_error`**
   - Load `tests/fixtures/l8_extractability/designs/unextractable_design.sysml`
   - Call `validate_codegen_readiness(path)`
   - Assert at least one issue with `code == ValidationCode.L8_DESIGN_ATTR_UNEXTRACTABLE`
   - Assert issue severity is `Severity.ERROR`
   - Assert issue message contains the attribute name

3. **`test_default_filter_skips_non_designs_directory`**
   - Load `tests/fixtures/l8_extractability/tests/test_design.sysml`
   - Call `validate_codegen_readiness(path)` (default filter)
   - Assert `Design attrs checked == 0` in metrics (skipped by filter)

4. **`test_custom_filter_checks_tests_directory`**
   - Load `tests/fixtures/l8_extractability/tests/test_design.sysml`
   - Call `validate_codegen_readiness(path, design_path_filter="tests")`
   - Assert `Design attrs checked` > 0 in metrics

5. **`test_empty_filter_checks_all_files`**
   - Load `tests/fixtures/l8_extractability/tests/test_design.sysml`
   - Call `validate_codegen_readiness(path, design_path_filter="")`
   - Assert `Design attrs checked` > 0 in metrics

6. **`test_none_filter_checks_all_files`**
   - Same as above but with `design_path_filter=None`

7. **`test_metrics_include_unextractable_count`**
   - Load the unextractable fixture
   - Assert `"L8_DESIGN_ATTR_UNEXTRACTABLE"` key exists in `result.metrics`
   - Assert count > 0

8. **`test_existing_l8_behavior_preserved`**
   - Run `validate_codegen_readiness("tests/fixtures/sample_models/")`
   - Assert result structure is unchanged (same keys in metrics, same overall behavior)

**Test Pattern:** Follow the existing pattern in `test_sysml_quality_checks.py:802-923` — direct calls to `validate_codegen_readiness()` with assertions on `result.structured_issues`, `result.metrics`, and `result.success`.

---

## Potential Risks

1. **Fixture AST uncertainty:** syside may not produce OperatorExpressions with FeatureReferences for `area = length * width` in a part definition (it might resolve them or represent them differently). **Mitigation:** Verify the fixture AST during implementation. If the straightforward SysML pattern doesn't produce the expected AST, create a simpler fixture or add a unit test using mock objects from `tests/test_sysml/conftest.py` instead.

2. **False positives on valid expressions:** Some design attributes may legitimately have non-literal expressions (e.g., computed defaults that reference sibling attributes). The check would flag these as `L8_DESIGN_ATTR_UNEXTRACTABLE`. **Mitigation:** This is correct behavior — codegen can't extract these as numeric defaults. The error message explains what's wrong and what to do. The calc usage owner filter (line 404-411) already handles the most common case of non-literal expressions (bindings inside calc usages).

3. **Backward compatibility of default filter:** Changing the default filter from hardcoded to parameterized `"designs"` preserves behavior, but callers relying on the current return type signature need no changes since the new parameter is optional with a default.

---

## Integration Strategy

- **Runner (`runner.py`):** No changes. The runner calls `validate_codegen_readiness(models_path)` which continues to work with the default `design_path_filter="designs"`.
- **CLI (`cli/__init__.py`):** No changes needed now. A future enhancement could add `--design-path-filter` to the `validate` subcommand, but this is out of scope.
- **Direct callers (tests, scripts):** Can pass `design_path_filter` explicitly. This is the primary use case — test models not in `designs/`.

---

## Validation Approach

### Automated Tests

All 8 test cases described in Component 4 above, run via `uv run pytest tests/test_l8_extractability.py -v`.

### Manual Verification

After implementation, run against the fusion-tea chain spike model to confirm the new check catches the issue:

```bash
cd /home/reid/1cfe/agentic-mbse
uv run python -c "
from agentic_mbse.validation.level8_codegen import validate_codegen_readiness
result = validate_codegen_readiness(
    '/home/reid/1cfe/fusion-tea/models/tests/codegen_chain_spike/',
    design_path_filter=''
)
print(f'Success: {result.success}')
print(f'Design attrs checked: {result.metrics.get(\"Design attrs checked\", 0)}')
for issue in result.structured_issues:
    if 'UNEXTRACTABLE' in str(issue.code):
        print(f'  {issue}')
"
```

### Regression

- `uv run pytest tests/` — all existing tests pass
- `uv run ruff check src/ tests/` — clean
- `uv run mypy src/` — no new type errors

---

## File Change Summary

| File | Change | Lines Affected |
|------|--------|----------------|
| `src/agentic_mbse/sysml/types.py` | Add `L8_DESIGN_ATTR_UNEXTRACTABLE` to `ValidationCode` | ~1 line after line 94 |
| `src/agentic_mbse/validation/level8_codegen.py` | Add import, configurable filter, extractability check, thread filter, add metric | ~25 lines changed/added |
| `tests/fixtures/l8_extractability/designs/valid_design.sysml` | New fixture | ~12 lines |
| `tests/fixtures/l8_extractability/designs/unextractable_design.sysml` | New fixture | ~14 lines |
| `tests/fixtures/l8_extractability/tests/test_design.sysml` | New fixture | ~12 lines |
| `tests/test_l8_extractability.py` | New test file | ~80-100 lines |

**Total:** ~2 existing files modified, 4 new files created. No changes to `runner.py`, `cli/__init__.py`, or any other validation level.

---

**Next Step:** After approval, proceed to `/_my_implement`
