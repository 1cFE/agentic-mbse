# Spec: Level 8 Extractability Validation

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-01 21:56:26 UTC
**Complexity:** LOW
**Branch:** revamp-architecture
**Related Epic:** EPIC-LCOE-001 (LCOE Costing Patterns)

---

## Business Goals

### Why This Matters

Level 8 validation exists to catch codegen-breaking issues *before* running codegen. During fusion-tea end-to-end pipeline testing (codegen chain spike, Item 2 of the pipeline de-risking epic), a model passed all 8 validation levels yet produced empty `design_params.json` at codegen time. The root cause: L8 checks that design attributes have a `feature_value_expression` (presence check) but never verifies that the expression can actually be evaluated to a numeric default value. This means L8 gives false confidence — "codegen ready" doesn't mean codegen will succeed.

A secondary issue: L8's path filter (`"designs" in doc_path.parts`) is hardcoded, causing it to skip design attributes in models stored outside a `designs/` directory (e.g., `models/tests/`). This means the check silently reports 0 design attributes and passes vacuously.

### Success Criteria

- [ ] A model with non-extractable design attribute expressions fails Level 8 with actionable error
- [ ] A model in `models/tests/` (not `models/designs/`) has its design attributes validated by L8
- [ ] The path filter for design attribute detection is configurable
- [ ] Existing tests continue to pass
- [ ] New synthetic test fixtures exercise the new checks

### Priority

Feeds into EPIC-LCOE-001. The sysml-codegen fixes (path filter default, crash guard) are the primary fix for the empty JSON; this spec adds the preventive safety net in agentic-mbse so that validation catches the problem before codegen is ever invoked.

---

## Problem Statement

### Current State

`check_design_attr_completeness()` in `level8_codegen.py` has two gaps:

1. **Presence-only check (line 418-421):** Verifies `feature_value_expression is not None` but never attempts evaluation. An expression like `length * width` (an OperatorExpression with feature references) passes the presence check, but `evaluate_true_static_expression()` raises `ValueError` on it. Codegen's `_extract_default_value()` hits the same error path and returns `None`, producing empty JSON.

2. **Hardcoded path filter (line 400):** `"designs" not in doc_path.parts` skips all attributes not in a directory containing `designs`. Models in `models/tests/`, `models/spike/`, or any non-standard layout are silently skipped. The check reports `Design attrs checked: 0` and passes vacuously.

### Desired Outcome

L8 validates that design attribute expressions are actually extractable as numeric defaults, and does so regardless of where the model files live. A model that would produce empty `design_params.json` gets caught at Level 8 with an error message identifying which attribute has the non-extractable expression.

---

## Scope

### In Scope

- Adding extractability check to `check_design_attr_completeness()` using `evaluate_true_static_expression()`
- Adding `L8_DESIGN_ATTR_UNEXTRACTABLE` to `ValidationCode` enum in `types.py`
- Making the path filter in `check_design_attr_completeness()` configurable (parameter with sensible default)
- Threading the path filter through `validate_codegen_readiness()` so callers can override
- Adding metric count for new validation code to `validate_codegen_readiness()` result
- Synthetic test fixtures in `tests/` that exercise both gaps

### Out of Scope

- Fixes in `sysml-codegen` (path filter default, crash guard, RootModel handler, FusionParams template)
- Changes to `evaluate_true_static_expression()` itself
- Changes to validation levels L1-L7
- Using the fusion-tea chain spike model as a test fixture (synthetic fixtures only)

### Edge Cases & Considerations

- **Library output attributes:** Expressions like `out attribute area : Real = length * width` are OperatorExpressions with feature references. These are NOT design defaults and should be skipped (they live in library files, not design files). The path filter handles this as long as it correctly distinguishes library from design files.
- **Calc usage bindings:** Attributes inside CalculationUsages are already skipped by the existing owner check (line 404-411). This is correct and unchanged.
- **Unit-annotated literals:** An expression like `3.0 [m]` is an OperatorExpression with `[` operator. `evaluate_true_static_expression()` handles this correctly (extracts 3.0, discards unit). No special handling needed.
- **Empty path filter:** If the filter is set to `""` or `None`, all files should be considered. This is the most permissive option and appropriate for test models.

---

## Requirements

### Functional Requirements

1. **FR-1: Extractability check.** After confirming `feature_value_expression is not None`, `check_design_attr_completeness()` MUST call `evaluate_true_static_expression()` on the expression. If it raises `ValueError` or `TypeError`, the check MUST emit a `ValidationIssue` with severity ERROR and code `L8_DESIGN_ATTR_UNEXTRACTABLE`.

2. **FR-2: New ValidationCode.** `L8_DESIGN_ATTR_UNEXTRACTABLE` MUST be added to the `ValidationCode` enum in `types.py`.

3. **FR-3: Configurable path filter.** `check_design_attr_completeness()` MUST accept an optional `design_path_filter` parameter. When provided and non-empty, only files whose path contains the filter string (as a path component) are checked. When empty or `None`, all files are checked. The default SHOULD remain `"designs"` for backward compatibility.

4. **FR-4: Path filter threading.** `validate_codegen_readiness()` MUST accept an optional `design_path_filter` parameter and pass it through to `check_design_attr_completeness()`.

5. **FR-5: Metrics.** The result metrics dict in `validate_codegen_readiness()` MUST include the count of `L8_DESIGN_ATTR_UNEXTRACTABLE` issues.

6. **FR-6: Error message quality.** The `L8_DESIGN_ATTR_UNEXTRACTABLE` issue message MUST include the attribute name and the exception message from `evaluate_true_static_expression()`, so the user knows which attribute failed and why.

### Non-Functional Requirements

- **NFR-1:** The extractability check MUST NOT import syside or any external parser. It uses only `evaluate_true_static_expression()` from `agentic_mbse.sysml.expression`, which operates on already-parsed AST nodes.
- **NFR-2:** The extractability check SHOULD add negligible overhead. `evaluate_true_static_expression()` is a pure in-memory tree walk.

---

## Acceptance Criteria

### Core Functionality

- [ ] A design attribute with `feature_value_expression` that raises `ValueError` in `evaluate_true_static_expression()` produces an `L8_DESIGN_ATTR_UNEXTRACTABLE` ERROR
- [ ] A design attribute with a valid literal expression (e.g., `10.0`) passes both the presence and extractability checks
- [ ] A design attribute with a unit-annotated literal (e.g., `3.0 [m]`) passes extractability
- [ ] `check_design_attr_completeness(model, design_path_filter="")` checks attributes in all files, not just `designs/`
- [ ] `check_design_attr_completeness(model, design_path_filter="designs")` preserves current behavior
- [ ] `validate_codegen_readiness(models_path, design_path_filter="tests")` validates test model attributes

### Tests

- [ ] Synthetic test fixture with a non-extractable design attribute expression triggers `L8_DESIGN_ATTR_UNEXTRACTABLE`
- [ ] Synthetic test fixture with valid design attributes passes L8
- [ ] Synthetic test fixture in a non-`designs/` directory is validated when path filter is adjusted
- [ ] Existing L8 tests continue to pass

### Quality & Integration

- [ ] `uv run pytest tests/` passes (all existing tests)
- [ ] `uv run ruff check src/ tests/` passes
- [ ] `uv run mypy src/` passes (no new type errors)

---

## Related Artifacts

- **Research (fusion-tea):** `/home/reid/1cfe/fusion-tea/.project/active/gap1-default-value-debug/findings.md`
- **Fix plan (fusion-tea):** `/home/reid/1cfe/fusion-tea/.project/active/gap1-default-value-debug/fix-plan.md`
- **Gaps report (fusion-tea):** `/home/reid/1cfe/fusion-tea/.project/reports/codegen-runtime-gaps-2026-02-01-2047.md`
- **Design:** `.project/active/l8-extractability-validation/design.md` (to be created)
- **Epic:** EPIC-LCOE-001 in `.project/backlog/BACKLOG.md`

---

**Next Steps:** After approval, proceed to `/_my_design`
