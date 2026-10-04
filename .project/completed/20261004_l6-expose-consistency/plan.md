# Implementation Plan: L6 EXPOSE Validation Consistency

**Status:** Complete; independently certified by [audit](audit.md) 2026-10-04 (implementation phases verified; this pass's wheel-build check blocked by DNS)
**Created:** 2026-10-04
**Last Updated:** 2026-10-04
**Branch:** harness-right-size (source unchanged since design commit `2d4b165`)

## Source Documents

- **Spec:** [spec.md](spec.md)
- **Design:** [design.md](design.md) (Revised, review incorporated). Decisions D1–D6, the fixture texts (Appendix A), and the expected results (Appendix B) are fixed. This plan does not restate them.
- **Review notes the design cites:** [design-review.md](design-review.md)

## The Point

[INHERITED: spec, design] A design attribute bound directly to a calculation output (`attribute x : Real = my_calc.scaled;`) is the documented EXPOSE pattern. Today Level 6 contradicts itself on it. The static-expression check (V2) accepts it. The supported-operator check (V4) rejects it with `V4_UNSUPPORTED_OPERATOR` for `.`. The completeness check rejects it with `L6_DESIGN_ATTR_UNEXTRACTABLE`. Level 6 is the codegen-readiness gate, so a modeler following the docs is told their supported dataflow is broken.

The fix makes V4 and completeness ask the one existing EXPOSE predicate first and skip what it accepts. Nothing else changes: every non-EXPOSE expression keeps exactly the diagnostics it gets today, and no new expression shape is supported. Per D6, the predicate's existing boundary also covers part-headed sibling chains (`x = sibling_part.attr`), which V2 and codegen already accept.

## Implementation Strategy

**Phasing rationale.** Tests first, then a pure rename, then the two guards. The rename (Phase 2) changes no behavior, so it lands green on its own. That isolates the only behavior change (Phase 3) to two small guards that turn the Phase 1 red tests green.

**Critical path.** Fixtures + test module (red) → rename predicate → V4 guard → completeness guard (green) → gate.

**First proof point.** The `controls/` `Counter` test passes *before* any production change (design Next-Stage Handoff). That is the direct proof of Invariant 4. If it does not pass pre-fix, stop: the fixture or the environment differs from the design's probe.

**Pre-fix values are re-verified.** A planning probe on 2026-10-04 ran the Appendix A fixtures and the referent through the current code. Every pre-fix number below matched: shapes 6 issues / 3 attrs, controls 13 pairs / 6 attrs, referent in `designs/` + `library/` 6 issues, and the predicate verdicts for all six boundary cases.

> **NOTE: gate baseline conflict (surfaced, not resolved silently).** [INHERITED: brief] The brief's final gate is `uv run ruff check src/ tests/`, `uv run ruff format --check src/ tests/`, and `uv run mypy src/`. All three already fail on the untouched tree (2026-10-04): ruff check finds 119 errors, ruff format would reformat 78 files, and mypy finds 91 errors in 19 files. The three existing files this item edits already fail `ruff format --check`, and `adr002.py:31` already carries 3 mypy errors. Run literally, the gate fails no matter what this item does.
> [AGENT] Plan-around: run the commands as given, and judge them against the baseline (no new findings). Add file-scoped checks that must be fully clean (Phase 4). Do not reformat the three existing files wholesale; that would bury a ~20-line change in unrelated churn. If the orchestrator wants the repo-wide gate green, that is a separate item.

---

## Phase 1: Fixtures and failing tests

### Goal

Commit the proof before the fix. Controls pass now and must keep passing. Shapes and the referent fail now, for exactly the reported false positives.

### Assumption Under Test

The Appendix A fixtures, laid out under `tests/fixtures/`, reproduce the design's pre-fix results through the public combined route, and nothing unrelated fires on them.

### Test Stencil (write this first)

`tests/test_validation/test_l6_expose_consistency.py` (NEW). The helper structure is open (design Next-Stage Handoff); the assertion values are not.

```python
import shutil
from collections import Counter
from pathlib import Path

from agentic_mbse.sysml.types import ValidationCode
from agentic_mbse.validation.adr002 import check_static_expressions, check_supported_operators
from agentic_mbse.validation.common import load_sysml_model
from agentic_mbse.validation.level6_architecture import (
    check_design_attr_completeness,
    validate_architecture,
)

FIXTURES = Path(__file__).parent.parent / "fixtures"
SHAPES = FIXTURES / "l6_expose_consistency" / "shapes"
CONTROLS = FIXTURES / "l6_expose_consistency" / "controls"
REFERENT = FIXTURES / "adr002_violations" / "v2_expose_pattern.sysml"
REFERENT_LIB = FIXTURES / "adr002_violations" / "library" / "simple_calc.sysml"

V2 = ValidationCode.V2_DYNAMIC_EXPRESSION
V4 = ValidationCode.V4_UNSUPPORTED_OPERATOR
UNX = ValidationCode.L6_DESIGN_ATTR_UNEXTRACTABLE
INC = ValidationCode.L6_DESIGN_ATTR_INCOMPLETE

D = "ExposeControlsDesign::"
EXPECTED_CONTROLS = Counter(
    [(code, D + "remote_reader::remote") for code in (V2, V4, UNX)]
    + [(code, D + "item_head_reader::payload_mass") for code in (V2, V4, UNX)]
    + [(code, D + "derived_part::derated") for code in (V2, V4, UNX)]
    + [(V4, D + "controls::powered"), (UNX, D + "controls::powered")]
    + [(INC, D + "controls::missing"), (UNX, D + "controls::divzero")]
)  # 13 pairs, design Appendix B

EXPOSED = "ExposePatternTest::expose_test_part::exposed_output"
COMBINED = "ExposePatternTest::multi_ref_test::combined"
EXPECTED_COMBINED = Counter({V2: 1, V4: 2, UNX: 1})  # two V4 '.', one per chain operand


def _assert_referent(issues):
    assert [i for i in issues if i.element_name == EXPOSED] == []
    assert Counter(i.code for i in issues if i.element_name == COMBINED) == EXPECTED_COMBINED


def test_shapes_pass_combined_route():
    result = validate_architecture(str(SHAPES))
    assert result.issues == [], result.issues
    assert result.success is True
    assert result.metrics["Design attrs checked"] == 3


def test_controls_keep_every_diagnostic():
    result = validate_architecture(str(CONTROLS))
    pairs = Counter((i.code, i.element_name) for i in result.structured_issues)
    assert pairs == EXPECTED_CONTROLS
    assert len(result.issues) == 13  # also catches unstructured manifest strings
    assert result.metrics["Design attrs checked"] == 6
    powered_v4 = [
        i for i in result.structured_issues
        if i.code == V4 and i.element_name == D + "controls::powered"
    ]
    assert len(powered_v4) == 1 and "'^'" in powered_v4[0].message


def test_referent_individual_checks():
    model, _ = load_sysml_model([REFERENT_LIB, REFERENT])  # Path objects, not str
    issues = (
        check_static_expressions(model)
        + check_supported_operators(model)
        + check_design_attr_completeness(model, design_path_filter=None)[0]
    )
    _assert_referent(issues)


def test_referent_combined_route(tmp_path):
    (tmp_path / "designs").mkdir()
    (tmp_path / "library").mkdir()
    shutil.copy(REFERENT, tmp_path / "designs")
    shutil.copy(REFERENT_LIB, tmp_path / "library")
    result = validate_architecture(str(tmp_path))
    _assert_referent(result.structured_issues)
```

### Changes Required

- [x] Create the four fixture files with the design's [Appendix A](design.md#appendix-a--control-fixtures-probe-verified) text verbatim (do not rename `scaled`, see `design.md#implementation-notes`):
  - `tests/fixtures/l6_expose_consistency/shapes/library/expose_calc.sysml`
  - `tests/fixtures/l6_expose_consistency/shapes/designs/expose_shapes.sysml`
  - `tests/fixtures/l6_expose_consistency/controls/library/expose_calc.sysml`
  - `tests/fixtures/l6_expose_consistency/controls/designs/expose_controls.sysml`
- [x] Create `tests/test_validation/test_l6_expose_consistency.py` from the stencil, with a module docstring pointing at the spec.

Gotchas:

- `load_sysml_model` (`src/agentic_mbse/validation/common.py:95`) needs `Path` objects. Strings raise `AttributeError: 'str' object has no attribute 'is_dir'`.
- With `design_path_filter=None`, completeness also reports `V2TestLibrary::SimpleCalc::input_val` (INCOMPLETE) and `V2TestLibrary::SimpleCalc::output_val` (UNEXTRACTABLE). That is expected. Keep the referent assertions scoped to `EXPOSED` and `COMBINED` (`design.md#implementation-notes`).

### Validation

- [x] `uv run pytest tests/test_validation/test_l6_expose_consistency.py -v` → **2 passed, 2 failed**, and the failures are exactly these:
  - `test_controls_keep_every_diagnostic` **passes** (first proof point).
  - `test_shapes_pass_combined_route` **fails**: 6 issues, V4 `'.'` and `L6_DESIGN_ATTR_UNEXTRACTABLE` on each of `ExposeShapesDesign::ExposingModule::module_result`, `ExposeShapesDesign::expose_test_part::exposed_output`, `ExposeShapesDesign::relay_part::relayed`.
  - `test_referent_individual_checks` and `test_referent_combined_route` **fail** on the first assertion: V4 `'.'` and `L6_DESIGN_ATTR_UNEXTRACTABLE` on `EXPOSED`. The `COMBINED` assertion would already hold.
- [x] Any other failure (a load warning, an unrelated code, a different count) means the fixture differs from Appendix A. Fix the fixture, not the assertion.
- [x] Record the observed red output in Implementation Notes below.

**What we know after this phase:** the proof reproduces the defect through the public route, and the controls pin today's non-EXPOSE diagnostics.

---

## Phase 2: Rename the predicate (no behavior change)

### Goal

Make the EXPOSE predicate a public, honestly documented helper that all three checks can import (D4). V2 behavior stays identical.

### Assumption Under Test

Dropping the unused `calc_outputs` parameter and deleting its only feeder changes nothing V2 reports.

### Test Stencil (write this first)

Add to the new module, merging the imports into its top import block. The import fails until the rename lands; that collection error is the red step.

```python
import pytest

from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.validation.adr002 import is_expose_binding
from agentic_mbse.validation.common import discover_sysml_files, get_qualified_name

_MODELS: dict[Path, object] = {}


def _attr(root: Path, qualified_name: str):
    if root not in _MODELS:
        _MODELS[root], _ = load_sysml_model(discover_sysml_files(str(root)))
    for attr in SysideAdapter.elements_of_type(_MODELS[root], "AttributeUsage"):
        if get_qualified_name(attr) == qualified_name:
            return attr
    raise AssertionError(f"{qualified_name} not found under {root}")


@pytest.mark.parametrize(
    ("root", "qualified_name", "expected"),
    [
        (SHAPES, "ExposeShapesDesign::ExposingModule::module_result", True),
        (SHAPES, "ExposeShapesDesign::expose_test_part::exposed_output", True),
        (SHAPES, "ExposeShapesDesign::relay_part::relayed", True),  # part-headed, D6
        (CONTROLS, "ExposeControlsDesign::remote_reader::remote", False),  # not a sibling
        (CONTROLS, "ExposeControlsDesign::item_head_reader::payload_mass", False),  # item head
        (CONTROLS, "ExposeControlsDesign::derived_part::derated", False),  # arithmetic
    ],
)
def test_is_expose_binding_boundary(root, qualified_name, expected):
    attr = _attr(root, qualified_name)
    assert is_expose_binding(attr, attr.feature_value_expression) is expected
```

### Changes Required

See `design.md#key-decisions` (D4) and Invariant 3 in `design.md#required-invariants`.

- [x] `src/agentic_mbse/validation/adr002.py:389`: rename `_is_expose_pattern` → `def is_expose_binding(attr: Any, expr: Any) -> bool`. Drop `calc_outputs`. Keep the body unchanged. Rewrite the docstring to state Invariant 3 exactly: top-level feature chain; head resolves to a `CalculationUsage` or `PartUsage`; head's owner is the attribute's owner; chain length and final target unconstrained; never raises, returns `False` on any analysis failure. Name its consumers: `check_static_expressions`, `check_supported_operators`, `check_design_attr_completeness`. Remove the "single attribute/output target" and "transitive EXPOSE" claims.
- [x] `adr002.py:599-600`: delete the catalog comment and `calc_outputs, _ = _build_calc_output_catalog(model)`.
- [x] `adr002.py:644`: call `is_expose_binding(attr, expr)`.
- [x] `adr002.py:253-307`: delete `_build_calc_output_catalog`.
- [x] `tests/test_sysml/test_adr002.py:12-18`: import `is_expose_binding`; drop `_build_calc_output_catalog`. Sort the import block as you edit it; that clears the file's one existing ruff finding (I001).
- [x] `test_adr002.py:186` and `:216`: rename to `test_is_expose_binding_detects_simple_case` and `test_is_expose_binding_rejects_operator_expression`. Delete the catalog lines (`:193`, `:223`). Update the calls (`:208`, `:238`), docstrings, and assertion messages to the new name.

### Validation

- [x] `uv run pytest tests/test_validation/test_l6_expose_consistency.py -v` → the 6 boundary cases pass. Phase 1 results are unchanged (controls pass; shapes and both referent tests still fail the same way).
- [x] `uv run pytest tests/test_sysml/test_adr002.py tests/test_validation/test_v2_false_positive.py tests/test_l8_extractability.py` → all pass.
- [x] `grep -rn "_is_expose_pattern\|_build_calc_output_catalog" src/ tests/` → no hits (Invariant 1).

**What we know after this phase:** the predicate is importable under its contract name, its boundary is pinned by test, and V2 is unaffected.

---

## Phase 3: The two guards

### Goal

The behavior change. V4 and completeness skip what the predicate accepts and treat everything else as before.

### Assumption Under Test

A guard placed after each check's existing scope filters removes exactly the EXPOSE false positives and no other diagnostic.

### Test Stencil

Already written: `test_shapes_pass_combined_route`, `test_referent_individual_checks`, and `test_referent_combined_route` are the red tests from Phase 1. `test_controls_keep_every_diagnostic` must stay green.

### Changes Required

See `design.md#architecture` and `design.md#implementation-notes` for placement.

- [x] **V4 guard**, `adr002.py`, in `check_supported_operators`: after `expr = attr.feature_value_expression` (`:147`) and before `extract_operators(expr)` (`:150`), add `if is_expose_binding(attr, expr): continue` with a one-line comment (an EXPOSE alias has no arithmetic, so it is outside V4's scope). Add one docstring line saying the same.
- [x] Run the module once. `test_shapes_pass_combined_route` should now show only the 3 `L6_DESIGN_ATTR_UNEXTRACTABLE` issues.
- [x] **Completeness guard**, `src/agentic_mbse/validation/level6_architecture.py`: add `is_expose_binding` to the `from .adr002 import (...)` block (`:34-39`). Inside `if has_value:` (`:530`), before the `try:` around `evaluate_true_static_expression`, add `if is_expose_binding(attr, attr.feature_value_expression): continue` with a one-line comment (complete: codegen wires the alias to its source). `attrs_checked` has already incremented at `:521`, which keeps Invariant 6.
- [x] Do not touch `extract_operators`, `SUPPORTED_OPERATORS`, `STATIC_OPERATORS`, or `evaluate_true_static_expression` (Invariant 5).

### Validation

- [x] `uv run pytest tests/test_validation/test_l6_expose_consistency.py -v` → **10 passed**.
- [x] `uv run pytest tests/test_sysml_quality_checks.py -k adr002 tests/test_l8_extractability.py tests/test_sysml/test_adr002.py` → all pass. The V4 orchestrator test (`tests/test_sysml_quality_checks.py:1087`) still finds `**`. The FORMULA rejection (`tests/test_l8_extractability.py:58`) is unchanged (Invariant 7).

**What we know after this phase:** all three spec success criteria are proven by committed tests.

---

## Phase 4: Full gate

### Goal

No regressions, and no new lint, format, or type findings.

### Validation

The default suite skips the 33 slow corpus tests (CLAUDE.md; `-m ""` runs them, not required here). On this machine the default suite ran in about 22 s; allow longer elsewhere.

- [x] `uv run pytest tests/` → baseline was **1922 passed, 1 skipped, 33 deselected**. Expect 1922 + the new module's tests (10 with the stencils above) passed, 1 skipped, 33 deselected, 0 failed.
- [x] `uv run ruff check src/agentic_mbse/validation/adr002.py src/agentic_mbse/validation/level6_architecture.py tests/test_sysml/test_adr002.py tests/test_validation/test_l6_expose_consistency.py` → **clean**.
- [x] `uv run ruff format tests/test_validation/test_l6_expose_consistency.py`, then `uv run ruff format --check` on the same file → **clean**. New lines in the three existing files should already be in ruff's style; the files themselves still report "would reformat", as they did before this item.
- [x] `uv run mypy src/ 2>&1 | grep -E "validation/(adr002|level6_architecture)\.py"` → only the 3 pre-existing errors at `adr002.py:31`.
- [x] Brief's repo-wide commands, judged against the baseline (see the gate note above): `uv run ruff check src/ tests/` reports ≤ 119 errors; `uv run ruff format --check src/ tests/` reports ≤ 78 files; `uv run mypy src/` reports ≤ 91 errors in 19 files.
- [x] Scope check: `git status --short` shows only `adr002.py`, `level6_architecture.py`, `tests/test_sysml/test_adr002.py`, the new test module, the four fixture files, and this plan. `git diff src/agentic_mbse/sysml/ tests/test_l8_extractability.py` is empty.

**What we know after this phase:** the item is ready for `/_my_audit`.

---

## Risk Management

See `design.md#potential-risks` (R1–R4). Phase-specific:

- **Phase 1:** If `shapes/` shows anything beyond the 6 listed issues, a fixture was mistyped or a Level 6 check changed since 2026-10-04 (design R2). Diff the file against Appendix A before touching assertions.
- **Phase 1:** The `divzero` control depends on the evaluator raising on division by zero (design R3). If that control is missing from the actual pairs, apply the design's documented swap (a string default on a `String` attribute) rather than dropping the control.
- **Phase 3:** If a control pair disappears after a guard, the guard is wider than the predicate or placed before a scope filter. Re-check placement against `design.md#implementation-notes`; do not edit `EXPECTED_CONTROLS`.

## Implementation Notes

[To be filled during implementation.]

### Phase 1 Completion
**Completed:** 2026-10-04
**Actual Changes:**
- Created the four fixture files under `tests/fixtures/l6_expose_consistency/{shapes,controls}/{library,designs}/`, text copied verbatim from design Appendix A.
- Created `tests/test_validation/test_l6_expose_consistency.py` from the stencil: module docstring pointing at the spec, tests grouped under one comment banner per spec criterion.

**Observed red output:** `1 passed, 3 failed`.
- `test_controls_keep_every_diagnostic` passed before any production change (first proof point, Invariant 4).
- `test_shapes_pass_combined_route` failed with exactly 6 issues: V4 `'.'` and `L6_DESIGN_ATTR_UNEXTRACTABLE` on each of `ExposingModule::module_result`, `expose_test_part::exposed_output`, `relay_part::relayed`.
- `test_referent_individual_checks` and `test_referent_combined_route` failed on the first assertion with exactly two issues on `exposed_output`: V4 `'.'` and `L6_DESIGN_ATTR_UNEXTRACTABLE`. No load warnings, no unrelated codes.

**Deviations:**
- The validation headline "2 passed, 2 failed" is an arithmetic slip in the plan; its own bullet list (controls pass; shapes and both referent tests fail) describes 1 passed, 3 failed, which is what ran.
- Stencil cosmetics only: the `powered` V4 check is two asserts instead of one `and`, and `_assert_referent` has a one-line docstring.

### Phase 2 Completion
**Completed:** 2026-10-04
**Actual Changes:**
- Added `test_is_expose_binding_boundary` (6 parametrized cases) to the new module; it failed at collection on the missing import before the rename (red step).
- `adr002.py`: `_is_expose_pattern(attr, expr, calc_outputs)` → `is_expose_binding(attr: Any, expr: Any) -> bool`. Docstring rewritten to Invariant 3: top-level feature chain, head resolves to `CalculationUsage` or `PartUsage`, head's owner is the attribute's owner, chain length and final target not checked, never raises (returns `False` on failure). Names its three consumers. The "single attribute/output target" and "transitive EXPOSE" claims are gone.
- `adr002.py`: deleted `_build_calc_output_catalog` and the V2 catalog build plus its comment; V2 now calls `is_expose_binding(attr, expr)`.
- `tests/test_sysml/test_adr002.py`: import block sorted (clears the file's one I001), `_build_calc_output_catalog` import and calls dropped, the two predicate tests renamed to `test_is_expose_binding_*` with docstrings, comments, and messages updated.

**Validation:** new module 7 passed, 3 failed (the same 3 as Phase 1, same issues). `test_adr002.py` + `test_v2_false_positive.py` + `test_l8_extractability.py`: 41 passed, 1 skipped. Invariant 1 grep: no hits.

**Deviations:**
- One body comment in the predicate changed: `# For PartUsage: transitive EXPOSE (...)` → `# For PartUsage: part-headed EXPOSE (...)`. The plan says keep the body unchanged; this is comment-only, no logic touched. It was the last place still claiming the "transitive" check that D4 removes, and it would have contradicted the new docstring.

### Phase 3 Completion
**Completed:** 2026-10-04
**Actual Changes:**
- `adr002.py` `check_supported_operators`: after `expr = attr.feature_value_expression` and before `extract_operators(expr)`, added `if is_expose_binding(attr, expr): continue` under a comment naming D2 (an alias has no arithmetic, so it is outside V4's scope). Docstring gained one line saying EXPOSE bindings are skipped.
- After the V4 guard alone, `shapes/` showed exactly the 3 `L6_DESIGN_ATTR_UNEXTRACTABLE` issues, as predicted.
- `level6_architecture.py`: `is_expose_binding` added to the `from .adr002 import (...)` block. Inside `if has_value:`, before the `try:` around `evaluate_true_static_expression`, added `if is_expose_binding(attr, attr.feature_value_expression): continue` under a comment naming D3 (codegen wires the alias to its source, so no numeric default is needed). `attrs_checked` increments before this point (Invariant 6).

**Validation:** new module 10 passed. `test_sysml_quality_checks.py -k adr002` + `test_l8_extractability.py` + `test_adr002.py`: 21 passed, 1 skipped. The filter selects `test_adr002_v4_in_orchestrator`, which still finds `**`.

**Deviations:**
- The completeness docstring's "Checks" bullet ("Design attrs with values produce extractable numeric defaults") gained a clause: "except EXPOSE bindings (see is_expose_binding), which are complete as written". Not in the plan; without it the docstring would state a rule the code no longer enforces. Parallels the V4 docstring line the plan asked for.

### Phase 4 Completion
**Completed:** 2026-10-04
**Gate results vs baseline:**

| Check | Before | After |
|---|---|---|
| `uv run pytest tests/` | 1922 passed, 1 skipped, 33 deselected | 1932 passed, 1 skipped, 33 deselected, 0 failed |
| `uv run ruff check src/ tests/` | 119 errors | 118 errors (the I001 in `test_adr002.py` is cleared) |
| `uv run ruff format --check src/ tests/` | 78 would reformat, 76 formatted | 78 would reformat, 77 formatted (the new test file is formatted) |
| `uv run mypy src/` | 91 errors in 19 files | 91 errors in 19 files |
| mypy findings in `adr002.py` / `level6_architecture.py` | 3, all at `adr002.py:31` | the same 3 |
| `ruff check` on the four touched Python files | 1 (I001, `test_adr002.py`) | clean |
| `ruff format --check` on the new test file | n/a | clean |

- No `ruff format --diff` hunk in `adr002.py`, `level6_architecture.py`, or `test_adr002.py` touches a changed line; none of the three was reformatted wholesale.
- The 6 pytest warnings are pre-existing `fork()` DeprecationWarnings from `tests/test_extraction.py`. The new module and `test_adr002.py` emit none.
- Scope: `git status` under `src/` and `tests/` shows only `adr002.py`, `level6_architecture.py`, `tests/test_sysml/test_adr002.py`, the new test module, and the four fixture files. `git diff src/agentic_mbse/sysml/ tests/test_l8_extractability.py` is empty (Invariants 5 and 7).
- Deleted the gitignored scratch directory `build/l6probe/` (design/plan probe output, nothing tracked).

**Deviations:**
- `ruff check --fix --select I001` on `test_adr002.py` also removed one of the two blank lines after the import block. That is part of the same I001 finding the plan says to clear.
- Two more doc-only lines in V2 (`check_static_expressions`) now point at `is_expose_binding` instead of describing EXPOSE as a "single reference to sibling calc output": the docstring bullet and the comment above the renamed call. Same class of overstated boundary claim as D4, on lines beside the call this item already edits. No logic change.

**Follow-ups noticed (not acted on):** none beyond the design's Non-Goals.

---

**Status:** Draft → In Progress → Complete
