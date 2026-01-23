# Design: Model Regression Testing

**Status:** Ready for Review
**Owner:** Reid Westwood
**Created:** 2026-01-23 16:13:24 UTC
**Branch:** 1cfe_dev
**Commit:** d40ff09

---

## Overview

Add pytest-based model regression testing infrastructure to agentic-mbse, enabling modelers to detect when library definition changes break existing designs.

## Related Artifacts

- **Spec:** `.project/active/model-regression-testing/spec.md`
- **Epic:** `.project/backlog/BACKLOG.md`

---

## Research Findings

### 1. `cmd_init()` Structure (cli/__init__.py)

**Location:** Lines 308-625 (318 lines)

**Key Constants:**
- `USER_OWNED_TEMPLATES` (lines 51-56): 4 templates created once, skipped on re-init
- `TOOL_OWNED_TEMPLATES` (lines 58-61): 2 templates always updated
- `PROJECT_TEMPLATES = USER_OWNED_TEMPLATES + TOOL_OWNED_TEMPLATES` (line 64)

**Directory Creation Pattern** (lines 522-528):
```python
modeling_pm_dir = target / "modeling_pm"
modeling_pm_dir.mkdir(parents=True, exist_ok=True)
(modeling_pm_dir / "backlog").mkdir(exist_ok=True)
(modeling_pm_dir / "active").mkdir(exist_ok=True)
# ... etc
```

**Template Installation:**
- User-owned: Direct `shutil.copy()` with skip-if-exists check (lines 532-542)
- Tool-owned: Uses `_install_file()` helper for copy/symlink (lines 544-556)

**Test Coverage:** `tests/test_cli.py` (498 lines) with 42+ test cases covering init modes.

### 2. Current MBSE Commands State

**spec-model.md:**
- Has success criteria structure (lines 114-151) with Functional, Quality, Validation categories
- Lists "No regressions in existing models" as checkbox (line 269) but no test definition structure
- **Gap:** No guidance on writing evaluatable/machine-checkable criteria

**plan-model.md:**
- Has 6 phases (lines 72-86): Core Library → Extended Library → Material Library → Design Core → Design Extended → Integration & Validation
- Final phase includes validation checkpoints (lines 380-407) but only forward-looking
- **Gap:** No regression testing phase or baseline capture step

**implement-model.md:**
- References all 8 validation levels (lines 307-315)
- Has checkbox "No regressions in existing models" (line 386) but no process defined
- **Gap:** No test execution commands or `tests/models/` awareness

### 3. Project Templates State

**MODELING_GUIDE.md.template:**
- Covers modeling principles, naming conventions, documentation standards
- Has validation checklist (lines 150-158) but only parse/traceability
- **Gap:** No testing paradigm documentation

**MODELING_PROCESS.md.template:**
- Large file (23,990 bytes) with detailed MBSE methodology
- Mentions `pytest tests/test_validation.py -v` (line 771) showing pytest awareness exists
- **Gap:** No regression test execution details or `tests/models/` structure

### 4. Existing Test Patterns (tests/test_cli.py)

**MockArgs Pattern** (lines 13-17):
```python
class MockArgs:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
```

**User-Owned Preservation Pattern** (lines 95-106):
```python
def test_skips_source_index_if_exists_without_force(self, tmp_path):
    source_index = tmp_path / "SOURCE_INDEX.md"
    source_index.write_text("existing: content")
    args = MockArgs(path=str(tmp_path), force=False)
    result = cmd_init(args)
    assert source_index.read_text() == "existing: content"  # Not overwritten
```

### 5. syside Usage Pattern (from tests/test_sysml/test_adr002.py)

**Key Pattern:** Use `get_syside()` from the adapter module, which handles lazy loading and license validation:

```python
from pathlib import Path
from agentic_mbse.sysml.syside_adapter import get_syside

# Collect files (syside.load_model takes a LIST of paths)
files = list(Path("tests/fixtures/adr002_violations").glob("*.sysml"))

# Use try_load_model for robustness (tolerates parse errors)
model, diagnostics = get_syside().try_load_model([str(f) for f in files])

# Access elements via model API
for elem in model.elements(get_syside().PartUsage):
    print(elem.name)
```

**Why `try_load_model`?** It returns a partial model even when there are parse errors, allowing tests to verify structure even on invalid models.

---

## Proposed Design

### Component 1: Test Directory Structure (`cmd_init()` Enhancement)

**Purpose:** Create `tests/models/` directory with example test file during init.

**Location:** `src/agentic_mbse/cli/__init__.py`

**Changes Required:**

1. **Add directory creation** (after line 528):
   ```python
   # Create tests/models/ directory for model regression tests
   tests_models_dir = target / "tests" / "models"
   tests_models_dir.mkdir(parents=True, exist_ok=True)
   ```

2. **Add example test template** to `project_templates/`:
   - New file: `project_templates/test_models_example.py.template`
   - Destination: `tests/models/test_example.py` (user-owned)

3. **Add conftest template** to `project_templates/`:
   - New file: `project_templates/conftest.py.template`
   - Destination: `tests/conftest.py` (user-owned)
   - Contains common fixtures for model testing

**Template Ownership:** User-owned (created once, user can customize/extend)

**File: `test_models_example.py.template`** (content):
```python
"""Example model regression tests.

This file demonstrates how to write pytest-compatible tests that validate
SysML models using the syside library. Tests in tests/models/ verify that
library definition changes don't break existing designs.

Key Pattern:
- Use get_syside().try_load_model() for robustness (tolerates parse errors)
- Load library files AND design files together to test integration
- Use pytest.skip() for optional tests when directories don't exist

Usage:
    pytest tests/models/          # Run all model tests
    pytest tests/models/ -v       # Verbose output
    pytest tests/models/ -k "library"  # Run specific tests
"""
import pytest
from pathlib import Path

# Import syside via the adapter (handles lazy loading and license)
from agentic_mbse.sysml.syside_adapter import get_syside

# Path to models directory (relative to tests/models/)
MODELS_DIR = Path(__file__).parent.parent.parent / "models"


# ============================================================================
# Fixtures - Reusable model loading
# ============================================================================


@pytest.fixture
def library_model():
    """Load all library definitions."""
    library_path = MODELS_DIR / "library"
    if not library_path.exists():
        pytest.skip("No library/ directory found")

    files = list(library_path.glob("**/*.sysml"))
    if not files:
        pytest.skip("No .sysml files in library/")

    model, diagnostics = get_syside().try_load_model([str(f) for f in files])
    return model, diagnostics


@pytest.fixture
def full_model():
    """Load library AND designs together for integration testing."""
    files = list(MODELS_DIR.glob("**/*.sysml"))
    if not files:
        pytest.skip("No .sysml files found in models/")

    model, diagnostics = get_syside().try_load_model([str(f) for f in files])
    return model, diagnostics


# ============================================================================
# Parsing Tests - Verify models parse without errors
# ============================================================================


class TestModelParsing:
    """Basic tests verifying models parse without syntax errors."""

    def test_library_parses_without_errors(self, library_model):
        """Verify library definitions parse successfully.

        A failing test here means library files have syntax errors.
        """
        model, diagnostics = library_model
        syside = get_syside()

        # Check for parse errors (not warnings)
        errors = [d for d in diagnostics if d.severity == syside.DiagnosticSeverity.Error]

        assert len(errors) == 0, f"Library has {len(errors)} parse errors: {errors}"

    def test_full_model_parses_without_errors(self, full_model):
        """Verify all models (library + designs) parse successfully.

        A failing test here indicates integration issues between
        library definitions and design usages.
        """
        model, diagnostics = full_model
        syside = get_syside()

        errors = [d for d in diagnostics if d.severity == syside.DiagnosticSeverity.Error]

        assert len(errors) == 0, f"Model has {len(errors)} parse errors: {errors}"


# ============================================================================
# Structure Tests - Verify expected elements exist
# ============================================================================


class TestModelStructure:
    """Tests verifying expected model elements exist.

    Customize these tests for your specific model requirements.
    When library definitions change, these tests catch breaking changes.
    """

    def test_example_definition_exists(self, library_model):
        """Example: Verify a specific definition exists in library.

        Replace 'ExampleDef' with actual definition names from your model.
        This pattern catches accidental deletion or renaming.
        """
        model, _ = library_model
        pytest.skip("Customize this test with your actual definition names")

        # Example pattern:
        # syside = get_syside()
        # part_defs = list(model.elements(syside.PartDefinition))
        # names = [p.name for p in part_defs if p.name]
        # assert "Motor" in names, "Motor definition missing from library"


# ============================================================================
# Integration Tests - Verify designs use library correctly
# ============================================================================


class TestDesignIntegration:
    """Tests verifying designs correctly reference library definitions.

    These are the critical regression tests: when you change a library
    definition, these tests verify existing designs still work.
    """

    def test_design_references_resolve(self, full_model):
        """Verify design usages can resolve their library definitions.

        Unresolved references indicate breaking changes to library APIs.
        """
        model, diagnostics = full_model
        syside = get_syside()

        # Check for unresolved reference errors
        unresolved = [
            d for d in diagnostics
            if "unresolved" in str(d.message).lower()
        ]

        assert len(unresolved) == 0, (
            f"Found {len(unresolved)} unresolved references - "
            "library changes may have broken designs"
        )
```

**File: `conftest.py.template`** (content):
```python
"""Pytest configuration and fixtures for model testing.

This file provides common fixtures used across all model tests.
Place in tests/ to make fixtures available to tests/models/*.
"""
import pytest
from pathlib import Path


@pytest.fixture
def models_dir():
    """Path to the models directory."""
    return Path(__file__).parent.parent / "models"


@pytest.fixture
def load_sysml():
    """Factory fixture for loading SysML models.

    Usage in tests:
        def test_my_model(load_sysml, models_dir):
            model, diagnostics = load_sysml(models_dir / "library")
            assert model is not None
    """
    from agentic_mbse.sysml.syside_adapter import get_syside

    def _load(path: Path | str):
        """Load SysML model from path (file or directory).

        Args:
            path: Single file or directory to load

        Returns:
            (model, diagnostics) tuple
        """
        path = Path(path)
        if path.is_dir():
            files = list(path.glob("**/*.sysml"))
        else:
            files = [path]

        return get_syside().try_load_model([str(f) for f in files])

    return _load
```

### Component 2: Documentation Updates (`MODELING_GUIDE.md.template`)

**Purpose:** Explain the testing paradigm and how to write model tests.

**Location:** `project_templates/MODELING_GUIDE.md.template`

**Changes Required:** Add new section explaining:
- Why regression testing matters for library/usage separation
- How to write pytest tests using syside
- Test organization patterns
- Integration with validation workflow

**Proposed Section** (to add before "Reference Information" section):

```markdown
## Model Regression Testing

### Why Regression Testing Matters

The library/usage separation pattern enables model reuse but introduces regression risk:
when you modify a library definition to support a new design, existing designs that
depend on it may break. Regression tests detect these breakages automatically.

### Test Structure

Model tests live in `tests/models/` and use pytest with the syside library:

```
tests/
├── conftest.py          # Common fixtures
└── models/
    ├── test_example.py  # Example/template
    ├── test_library.py  # Library definition tests
    └── test_designs.py  # Design integration tests
```

### Writing Model Tests

Model tests verify:
1. **Parsing** - Models parse without syntax errors
2. **Structure** - Required elements exist with expected types
3. **Interfaces** - Ports and attributes have correct types
4. **Constraints** - Constraint expressions evaluate correctly

Example test pattern:
```python
import pytest
from pathlib import Path
from agentic_mbse.sysml.syside_adapter import get_syside

MODELS_DIR = Path(__file__).parent.parent.parent / "models"

def test_motor_definition_exists():
    """Verify Motor part definition exists in actuators library."""
    files = list((MODELS_DIR / "library").glob("**/*.sysml"))
    model, diagnostics = get_syside().try_load_model([str(f) for f in files])

    # Check no parse errors
    syside = get_syside()
    errors = [d for d in diagnostics if d.severity == syside.DiagnosticSeverity.Error]
    assert len(errors) == 0, f"Parse errors: {errors}"

    # Find Motor definition
    part_defs = list(model.elements(syside.PartDefinition))
    motor_defs = [p for p in part_defs if p.name == "Motor"]
    assert len(motor_defs) == 1, "Expected exactly one Motor definition"
```

### Running Tests

```bash
# Run all model tests
pytest tests/models/

# Run with verbose output
pytest tests/models/ -v

# Run specific test file
pytest tests/models/test_library.py
```

### When to Write Tests

- **During spec phase**: Define success criteria as test assertions
- **After library changes**: Verify existing designs still work
- **Before integration**: Validate design-library compatibility
```

### Component 3: Spec Command Guidance (`spec-model.md`)

**Purpose:** Emphasize evaluatable success criteria that can inform test assertions.

**Location:** `claude/commands/spec-model.md`

**Changes Required:** Enhance the success criteria guidance to include machine-checkable criteria.

**Key Modification Points:**

1. **Stage 3: Success Criteria Section** (around lines 114-150)
   - Current structure has Functional, Quality, Validation success categories
   - Add guidance on making criteria evaluatable (machine-checkable)

2. **Presentation Template** (around lines 119-148)
   - Add test assertion examples alongside human descriptions

**Proposed Addition** (insert after line 117 "**Validation Success**..." section):

```markdown
4. **Define Evaluatable Success Criteria**:

   Success criteria should be **both human-readable AND machine-checkable** where possible.
   This enables automated regression testing via `pytest tests/models/`.

   **Pattern:** For each key requirement, specify:
   - **Human description**: What should be true
   - **Verification method**: Manual review OR automated test
   - **Test assertion** (if automatable): Specific programmatic check

   **Examples:**

   | Requirement | Human Description | Test Assertion |
   |-------------|-------------------|----------------|
   | Motor definition exists | Library has Motor part definition | `"Motor" in [p.name for p in model.elements(PartDefinition)]` |
   | Mass is calculated | System computes total mass | `mass_calc is not None and mass_calc.result is not None` |
   | Units consistency | All mass attrs use kg | `all(a.unit == "kg" for a in mass_attrs)` |
   | No parse errors | Model files parse cleanly | `len([d for d in diagnostics if d.severity == Error]) == 0` |

5. **Regression Safety Criteria** (for library modifications):

   When modifying existing library definitions, specify:
   - Which existing designs depend on this library (check `models/designs/` imports)
   - What interfaces must remain stable (ports, attributes, types)
   - Minimum test coverage required before proceeding

   **Example:**
   > Motor definition is used by designs/tokamak_v1 and designs/prototype.
   > Interface stability: `torque` output port type and direction must not change.
   > Test coverage: `tests/models/test_actuators.py::test_motor_interface` must pass.
```

### Component 4: Plan Command Updates (`plan-model.md`)

**Purpose:** Add explicit test-writing and test-execution phases to generated plans.

**Location:** `claude/commands/plan-model.md`

**Changes Required:**

1. **Add test phase guidance** to phase planning (Step 3)
2. **Include test-writing in phase completion criteria**
3. **Add validation checkpoint with regression test execution**

**Key Modification Points:**

1. **Step 3: Create Plan Document** (around lines 89-104)
   - Current: Defines phase structure with Deliverables, Validation Checkpoint
   - Add: Test Requirements section to each phase template

2. **Step 4: Validate Plan Feasibility** (around lines 106-150)
   - Current: Reviews planned changes for syntax validity
   - Add: Check that spec's evaluatable criteria have corresponding test tasks

**Proposed Addition** (insert after line 98 "User Review Point" item):

```markdown
7. **Test Requirements** - What tests to write or verify:
   - **New library definitions**: Create structural tests in `tests/models/`
   - **Modified definitions**: Verify existing tests still pass
   - **Design integrations**: Add/update integration tests

**Test Phase Pattern:** For features with multiple phases:

| Phase | Test Activity |
|-------|---------------|
| Library definitions | Write structural tests for new defs |
| Design instances | Write integration tests |
| Final validation | Run full regression suite |

**Example Phase with Tests:**
```markdown
### Phase 2: Motor Definition Refinement

**Deliverables:**
- [ ] Enhanced Motor part def with complete attributes
- [ ] Full doc comments with codebase source citations
- [ ] Structural test: `tests/models/test_actuators.py::test_motor_attributes`

**Validation Checkpoint:**
- [ ] Parse check passes: `syside check models/library/actuators.sysml`
- [ ] Regression tests pass: `pytest tests/models/ -v`
```

**Final Validation Phase Must Include:**
```markdown
### Phase N: Integration & Validation

**Validation Steps:**
1. Parse validation: `agentic-mbse validate models/ --level=1`
2. Quality validation: `agentic-mbse validate models/ --level=3`
3. **Regression tests: `pytest tests/models/ -v`**
4. Manual review checkpoints

**Completion Gate:**
All tests in `tests/models/` must pass before marking complete.
```
```

### Component 5: Implement Command Awareness (`implement-model.md`)

**Purpose:** Make implement phase aware of test requirements and `tests/models/` location.

**Location:** `claude/commands/implement-model.md`

**Changes Required:**

1. **Add test execution to validation workflow**
2. **Include test-writing checklist items**
3. **Add test file path conventions**

**Key Modification Points:**

1. **Stage 1: Plan Analysis** (around lines 19-37)
   - Current: Reads plan, checks prototype state
   - Add: Note any test requirements from plan phases

2. **Stage 2: Execute Phases** (need to find exact location)
   - Add: Execute test-writing tasks from plan
   - Add: Run regression tests after completing model changes

3. **Stage 3: Validation** (need to find exact location)
   - Current: Runs parse/quality validation
   - Add: Run regression test suite as validation step

**Proposed Addition** (new section after Quality Validation):

```markdown
### Regression Testing

After completing model changes in each phase, run regression tests:

```bash
# Run all model tests
pytest tests/models/ -v

# Run specific test file (if plan specifies)
pytest tests/models/test_library.py -v

# Run with coverage (optional)
pytest tests/models/ --cov=models/ -v
```

**Test Phase Deliverables** (from plan):
- [ ] New library definitions have structural tests in `tests/models/`
- [ ] Modified definitions pass existing tests (no regressions)
- [ ] Integration tests verify design-library compatibility
- [ ] All tests pass before marking phase complete

**Test Location Convention:**
```
tests/
└── models/
    ├── conftest.py          # Shared fixtures
    ├── test_example.py      # Example/template
    ├── test_library.py      # Library definition tests
    └── test_designs.py      # Design integration tests
```
```

**Add to Final Validation Checklist** (update existing checklist):

```markdown
### Final Validation Checklist

- [ ] Parse validation passes: `agentic-mbse validate models/ --level=1`
- [ ] Quality validation passes: `agentic-mbse validate models/ --level=3`
- [ ] **Regression tests pass: `pytest tests/models/ -v`**
- [ ] No regressions in existing models (verified by test suite)
- [ ] All spec acceptance criteria met
- [ ] Plan checkboxes complete
```

---

## Implementation Summary

| Component | Files Changed | Type | Lines Affected | Owner |
|-----------|---------------|------|----------------|-------|
| Test directory structure | `src/agentic_mbse/cli/__init__.py` | Code | ~20 lines | Tool |
| Test example template | `project_templates/test_models_example.py.template` | New file | ~120 lines | User |
| Conftest template | `project_templates/conftest.py.template` | New file | ~40 lines | User |
| Documentation | `project_templates/MODELING_GUIDE.md.template` | Edit | ~60 lines | Tool |
| Spec command | `claude/commands/spec-model.md` | Edit | ~50 lines | Tool |
| Plan command | `claude/commands/plan-model.md` | Edit | ~50 lines | Tool |
| Implement command | `claude/commands/implement-model.md` | Edit | ~40 lines | Tool |
| Tests | `tests/test_cli.py` | Edit | ~50 lines | N/A |

**Template Ownership Mapping:**
- `test_models_example.py.template` → User-owned (add to `USER_OWNED_TEMPLATES`)
- `conftest.py.template` → User-owned (add to `USER_OWNED_TEMPLATES`)

---

## Potential Risks

1. **syside API Changes**: Test templates depend on syside API. If syside changes, templates may need updates.
   - *Mitigation*: Keep test examples simple; document syside version requirements.

2. **Test Template Staleness**: User-owned test files won't receive updates on re-init.
   - *Mitigation*: Put detailed documentation in MODELING_GUIDE.md (tool-owned) rather than in templates.

3. **pytest Dependency**: Target repos need pytest installed.
   - *Mitigation*: Document pytest as required dependency in README template.

4. **agentic-mbse Import Dependency**: Test templates import from `agentic_mbse.sysml.syside_adapter`. Target repos must have agentic-mbse installed (not just initialized).
   - *Mitigation*: Document in conftest.py that agentic-mbse must be pip-installable. Alternative: Use direct syside import pattern in templates (trade-off: lose license error handling).

5. **Empty Model Directories**: Tests skip gracefully when `models/` doesn't exist, but this may mask issues.
   - *Mitigation*: Example test file includes comments explaining skip behavior.

---

## Integration Strategy

1. **Backwards Compatibility**: Existing projects without `tests/` continue to work; testing is opt-in.
2. **Workflow Integration**: Tests fit naturally into existing spec → plan → implement cycle.
3. **Incremental Adoption**: Projects can add tests gradually as models mature.

---

## Validation Approach

### Testing Strategy

1. **Unit tests for init changes** (`tests/test_cli.py`):
   - `test_init_creates_tests_models_directory()`
   - `test_init_creates_example_test_file()`
   - `test_init_skips_example_test_if_exists()`
   - `test_init_creates_conftest()`

2. **Integration test**: Run init on fresh directory, verify structure.

3. **Manual verification**:
   - Run init, verify `tests/models/test_example.py` exists
   - Run `pytest tests/models/` in initialized project (should pass or skip gracefully)

### Success Criteria Verification

- [ ] `agentic-mbse init` creates `tests/models/` directory
- [ ] Example test file demonstrates syside usage
- [ ] Documentation explains testing paradigm
- [ ] Spec command includes evaluatable criteria guidance
- [ ] Plan command includes test phases
- [ ] Implement command includes test execution

---

**Next Step:** After approval → `/_my_implement`
