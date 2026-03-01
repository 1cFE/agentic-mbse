---
name: model-validation
description: >
  Use when asking about "validate", "validation levels", "quality checks", "run checks",
  "test models", "regression test", "Level 1", "Level 6", "validation pyramid",
  "model quality", "parse error", "verification thresholds", "PASS WARN FAIL",
  or when deciding what validation to run and how to interpret results.
  Provides the 6-level validation methodology, timing, thresholds, and regression testing patterns.
allowed-tools: Read, Grep, Glob, Bash
user-invocable: false
---

# Model Validation

The 6-level validation pyramid, when to validate, how to interpret results, and regression testing patterns.

## Core Principle

Validate early and often. Every modeling phase ends with a validation checkpoint. Levels 1-3 are blocking (must pass before proceeding); Levels 4-5 are informational WIP (guide improvements but don't block progress); Level 6 is application-specific (ADR-002, manifests, codegen readiness).

## When to Reference

- `/implement-model` — validation after each implementation phase
- `/design-model` — prototype validation during design
- `/plan-model` — planning validation checkpoints per phase
- `/audit-models` — comprehensive verification against baselines
- `/spec-model` — defining evaluatable success criteria

## The 6-Level Validation Pyramid

| Level | Name | Checks | Blocking |
|-------|------|--------|----------|
| 1 | Syntax Validation | Parser errors (via syside) | Yes |
| 2 | Structural Completeness | Unused definitions, unbound inputs | Yes |
| 3 | Dependency Integrity | Circular dependencies | Yes |
| 4 | Constraint Coverage | Constraint counts, coverage metrics | No (WIP) |
| 5 | Traceability & Documentation | Doc comment presence on definitions | No (WIP) |
| 6 | Architecture & Pipeline Readiness | ADR-002 rules, manifest subsystems, codegen readiness | Configurable |

## CLI Invocation

For `uv run` prefix and environment rules, see the **toolkit-awareness** skill.

```bash
# All levels, fail-fast (default)
uv run agentic-mbse validate models/

# All levels, continue past failures
uv run agentic-mbse validate --complete models/

# Specific level only
uv run agentic-mbse validate --level=N models/

# Verbose diagnostics
uv run agentic-mbse validate --verbose models/
```

## When to Validate

| Timing | Levels | Purpose |
|--------|--------|---------|
| After prototype (design phase) | 1-3 | Verify architecture works |
| After each implementation phase | 1-5 | Catch issues early |
| Final validation | All (1-6) | Full quality assessment |
| After audit | Focused (specific levels) | Verify fixes |
| ADR-002 compliance check | Manual | `grep -r "calc def" models/designs/` should return empty |

## Verification Thresholds

For baseline comparison audits (comparing model values to authority source values):

| Status | Threshold | Action |
|--------|-----------|--------|
| PASS | Deviation ≤ 1% | Proceed — model matches baseline |
| WARN | Deviation 1-5% | Investigate — may be intentional, document if justified |
| FAIL | Deviation > 5% | Stop and fix — update model or document rationale |

## Reading Validation Output

**Level 1-3 errors are critical** — these break models:
- **Parse errors** (L1): Syntax mistakes, missing imports, unicode unit symbols
- **Structural issues** (L2): Definitions declared but never used, unbound inputs
- **Dataflow errors** (L3): Circular dependencies between files

**Level 4-6 provide insights** — guide improvements:
- **Constraint gaps** (L4): Constraint coverage metrics
- **Documentation gaps** (L5): Missing doc comments, incomplete source citations
- **Architecture & codegen** (L6): ADR-002 rules, manifest subsystems, codegen readiness

Use `--complete` to see all issues across all levels (default stops at first blocking failure). Use `--verbose` for detailed diagnostic output.

### Validation Report Structure

When reporting validation results, structure as:

1. **Header**: Model path, levels run, date
2. **Per-level summary**: Level name, issue count (error/warning/info), blocking status
3. **Issue details**: Level, severity, file:line, message, suggested fix
4. **Outcome**: PASS (all blocking levels clean) or FAIL (blocking errors remain)

## Regression Testing

### Test Structure

Model tests live in `tests/models/` and use pytest with the syside library:

```
tests/
├── conftest.py          # Common fixtures
└── models/
    ├── test_library.py  # Library definition tests
    └── test_designs.py  # Design integration tests
```

### Test Pattern

```python
from pathlib import Path
from agentic_mbse.sysml.syside_adapter import get_syside

MODELS_DIR = Path(__file__).parent.parent.parent / "models"

def test_definition_exists():
    """Verify part definition exists in library."""
    files = list((MODELS_DIR / "library").glob("**/*.sysml"))
    model, diagnostics = get_syside().try_load_model([str(f) for f in files])

    syside = get_syside()
    errors = [d for d in diagnostics if d.severity == syside.DiagnosticSeverity.Error]
    assert len(errors) == 0, f"Parse errors: {errors}"

    part_defs = list(model.elements(syside.PartDefinition))
    names = [p.name for p in part_defs]
    assert "Motor" in names, "Expected Motor definition"
```

### When to Write Tests

| Phase | Test Activity |
|-------|---------------|
| Library definitions | Write structural tests for new defs |
| Design instances | Write integration tests |
| Final validation | Run full regression suite |

### Running Tests

```bash
uv run pytest tests/models/ -v          # All model tests
uv run pytest tests/models/test_library.py -v  # Specific file
```

### Codegen Skip Convention

Tests requiring the downstream pipeline (sysml-codegen) use a pytest marker:

```python
@pytest.mark.codegen_available
def test_codegen_output():
    """Only runs when codegen pipeline is available."""
```

## Anti-Patterns

| Instead of | Do |
|------------|-----|
| Skipping validation until the end | Validate after every phase (L1-3 minimum) |
| Ignoring Level 4-6 warnings | Review and document — they guide improvements |
| Running `syside check` directly | Use `uv run agentic-mbse validate` (wraps syside + more) |
| Proceeding when L1-3 fail | Stop, fix blocking errors before continuing |
| Writing tests after all implementation | Write tests alongside each phase |
| Guessing validation commands | Read README.md for current CLI (see toolkit-awareness) |

## Related Skills

- For `uv run` prefix and environment rules, see the **toolkit-awareness** skill.
- For SysML syntax rules that prevent validation errors, see the **sysml-conventions** skill.
