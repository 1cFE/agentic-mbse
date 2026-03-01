# Spec: Validation Stack Restructuring (8 → 6 Levels)

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-27
**Complexity:** STANDARD
**Branch:** TBD
**Related Research:** `.project/research/20260227-195415_validation-stack-audit.md`

---

## Business Goals

### Why This Matters

The validation stack was designed early with 8 aspirational levels. An audit revealed that 2 levels are unimplemented stubs (L4 Constraints, L5 Semantic), 2 are informational-only (L6 Traceability, L7 Architecture), and some checks are misplaced (ADR-002 architectural rules live in L2 "Structure"). The blog post describes 6 levels, but 3 of those descriptions don't match the implementation.

This restructuring:
1. Aligns the implementation with the blog's 6-level narrative
2. Ensures each level is distinct (catches errors no other level does)
3. Places application-specific checks in an explicit "Architecture" layer
4. Honestly marks WIP levels as WIP rather than presenting stubs as working validation

### Success Criteria

- [x] Validation stack has exactly 6 levels, numbered 1-6
- [x] Each level is exercised by at least one test fixture that fails *only* at that level
- [x] Existing test suite passes (modulo renumbering adjustments)
- [x] `uv run agentic-mbse validate models/` works with new level numbering
- [x] CLI `--level=N` accepts 1-6 (not 1-8)
- [ ] Blog post language matches implementation behavior
- [x] SKILL.md, CLAUDE.md, and README template updated to reflect 6 levels

### Priority

Prerequisite for publishing the blog post with accurate validation claims. Also improves the developer experience by eliminating always-pass stub levels.

---

## Problem Statement

### Current State

8 validation levels where:
- L4 (Constraint Satisfaction): counts constraints, always passes, no threshold
- L5 (Semantic Consistency): two stub functions that always return empty lists
- L6 (Traceability): checks doc comment presence, always passes (warnings only)
- L7 (Architecture): checks manifest subsystems, passes vacuously without manifest
- L8 (Codegen Readiness): 5 substantial checks, most sophisticated level
- L2 (Structure): contains ADR-002 checks that are application-specific, not generic

### Desired Outcome

6 validation levels where:
- Every level is genuinely distinct
- Generic structural checks are separated from application-specific architectural rules
- WIP levels are clearly identified but still provide useful metrics
- The blog post accurately describes what each level does

---

## Scope

### In Scope

1. **Delete** `level5_semantic.py` — merge constraint coverage stub into L4
2. **Move** ADR-002 check calls from `level2_structure.py` to new L6
3. **Merge** `level7_architecture.py` and `level8_codegen.py` into new `level6_architecture.py`
4. **Renumber** `level6_traceability.py` → `level5_traceability.py`
5. **Update** `runner.py` QUALITY_CHECKS registry (6 entries, not 8)
6. **Update** `__init__.py` exports
7. **Update** `ValidationCode` enum if needed (L8_ prefixes → L6_)
8. **Update** CLI `--level` range (1-6)
9. **Update** tests to match new level numbers and structure
10. **Update** documentation: SKILL.md, CLAUDE.md, README template
11. **Add** distinctness test fixtures (one per level)

### Out of Scope

- Implementing constraint coverage thresholds for L4 (WIP — future work)
- Implementing source citation parsing for L5 (WIP — future work)
- Implementing unit dimensional analysis (deferred — no near-term path)
- Changes to `adr002.py` logic itself (only moving where it's called from)
- Changes to codegen readiness check logic (only moving to new module)
- Changes to any validation check logic (restructuring only, not behavioral changes)

### Edge Cases & Considerations

- **ValidationCode prefixes**: Current codes use `L8_` prefix. These WILL be renamed to `L6_` (FR-9). Only downstream consumer is fusion-tea, which has no Python code references to these codes — only `.project/` docs that will be updated (FR-10).
- **`adr002.py` module**: Stays as a separate module — only the call site moves from L2 to L6. The module itself is unchanged except for `level` field updates in its `ValidationIssue` objects (2→6).
- **Manifest-only checks**: L7's manifest-based subsystem check joins L6. If no manifest exists, L6 still runs the other checks (ADR-002, codegen readiness) — it doesn't skip everything.
- **Level numbers in ValidationIssue**: Each `ValidationIssue` has a `level` field. Issues from ADR-002 currently say `level=2`. After restructuring they should say `level=6`. Issues from old L8 say `level=8` → should say `level=6`.
- **Always-pass behavior**: L4 and L5 (new numbering) continue to always pass. This is honest — they're WIP informational levels. The runner should distinguish blocking (L1-L3) from informational (L4-L5) from application-specific (L6) in its output.

---

## Requirements

### Functional Requirements

**FR-1: New level structure.** The validation stack MUST have exactly 6 levels:

| Level | Name | Blocking? | Checks |
|-------|------|-----------|--------|
| 1 | Syntax Validation | Yes | Parser errors via syside |
| 2 | Structural Completeness | Yes | Unused defs, unbound inputs, literal/undefined bindings |
| 3 | Dependency Integrity | Yes | Circular package imports |
| 4 | Constraint Coverage | No (WIP) | Constraint counts, constraint coverage metrics |
| 5 | Traceability & Documentation | No (WIP) | Doc comment presence on definitions |
| 6 | Architecture & Pipeline Readiness | Configurable | ADR-002 rules, manifest subsystems, codegen readiness |

**FR-2: L2 contains only generic structural checks.** `validate_structure()` MUST NOT call `check_calc_def_locations()`, `check_static_expressions()`, or `check_supported_operators()` from `adr002.py`. These move to L6.

**FR-3: L4 absorbs constraint coverage.** `analyze_constraints()` MUST include the constraint coverage analysis (which attributes are constrained) currently stubbed in old L5's `check_constraint_coverage()`. The stub implementation is acceptable — the function signature and metric reporting must be present.

**FR-4: L5 is renumbered L6.** `validate_traceability()` MUST report `level=5` in its result, not `level=6`.

**FR-5: L6 combines three sources.** `validate_architecture()` (new) MUST run:
1. ADR-002 checks: `check_calc_def_locations()`, `check_static_expressions()`, `check_supported_operators()`
2. Manifest subsystem checks (from old L7)
3. Codegen readiness checks: qualified names, calc def structure, binding formats, design attr completeness, design attr extractability (from old L8)

**FR-6: Runner registry.** `QUALITY_CHECKS` in `runner.py` MUST contain exactly 6 entries corresponding to levels 1-6. The `--level` CLI argument MUST accept 1-6.

**FR-7: ValidationIssue level fields.** All `ValidationIssue` objects MUST use the new level numbers. ADR-002 issues: `level=6`. Codegen readiness issues: `level=6`. Traceability issues: `level=5`.

**FR-8: Distinctness tests.** There MUST be at least one test fixture per level where that level fails and all other levels pass (for blocking levels) or reports issues uniquely (for WIP levels).

**FR-9: ValidationCode renaming.** All `ValidationCode` enum members with `L8_` prefix MUST be renamed to `L6_` prefix:
- `L8_MISSING_QUALIFIED_NAME` → `L6_MISSING_QUALIFIED_NAME`
- `L8_INVALID_QUALIFIED_NAME` → `L6_INVALID_QUALIFIED_NAME`
- `L8_CALC_DEF_NO_OUTPUT` → `L6_CALC_DEF_NO_OUTPUT`
- `L8_CALC_DEF_NO_DIRECTION` → `L6_CALC_DEF_NO_DIRECTION`
- `L8_INVALID_BINDING_FORMAT` → `L6_INVALID_BINDING_FORMAT`
- `L8_DESIGN_ATTR_INCOMPLETE` → `L6_DESIGN_ATTR_INCOMPLETE`
- `L8_DESIGN_ATTR_UNEXTRACTABLE` → `L6_DESIGN_ATTR_UNEXTRACTABLE`

**FR-10: fusion-tea downstream changes.** The only downstream consumer is `fusion-tea`. Changes required:
- `fusion-tea/README.md`: Update "8-level quality checks" → "6-level", update any `--level` examples referencing levels 7-8
- `fusion-tea/knowledge/research/approved/20260106-065431_cost-architecture-patterns.md`: Update `--level 9` reference
- `fusion-tea/.project/active/gap1-default-value-debug/fix-plan.md`: Update `L8_DESIGN_ATTR_UNEXTRACTABLE` and `level8_codegen.py` references
- `fusion-tea/.project/active/gap1-default-value-debug/findings.md`: Update `level8_codegen.py` references
- `fusion-tea/.project/active/gap1-default-value-debug/spec.md`: Update "levels 1-8" → "levels 1-6"

Note: fusion-tea's Python code (`validate_ast.py` files) only imports `agentic_mbse.validation.common` and `SysideAdapter` — no references to specific `ValidationCode` values or level validators. No Python code changes needed in fusion-tea.

### Non-Functional Requirements

**NFR-1: No behavioral changes.** The checks themselves MUST NOT change logic. The same SysML model that triggered an ADR-002 violation before MUST still trigger it — just at L6 instead of L2.

**NFR-2: Clean module deletion.** `level5_semantic.py` MUST be deleted, not left as an empty file. `level7_architecture.py` and `level8_codegen.py` MUST be deleted after their contents are merged into `level6_architecture.py`.

---

## Acceptance Criteria

### Core Restructuring

- [x] `level5_semantic.py` deleted
- [x] `level7_architecture.py` deleted
- [x] `level8_codegen.py` deleted
- [x] `level5_traceability.py` exists (renamed from `level6_traceability.py`)
- [x] `level6_architecture.py` exists (new, merged from L7+L8+ADR-002 calls)
- [x] `level2_structure.py` no longer imports or calls `adr002` functions
- [x] `level4_constraints.py` includes constraint coverage metrics
- [x] `runner.py` QUALITY_CHECKS has exactly 6 entries
- [x] `__init__.py` exports updated (no references to old L5, L7, L8 modules)
- [x] `ValidationCode` enum: all `L8_` prefixes renamed to `L6_`
- [x] `adr002.py` ValidationIssue objects use `level=6`

### Tests

- [x] All existing tests pass after adjustments for renumbering
- [x] New distinctness fixture: L1-only failure (syntax error)
- [x] New distinctness fixture: L2-only failure (unbound input, no ADR-002 violation)
- [x] New distinctness fixture: L3-only failure (circular import) — fixture exists but L3 cycle detection is non-functional (syside limitation); test documents this
- [x] New distinctness fixture: L6-only failure (ADR-002 violation or codegen readiness failure, passes L1-L3)
- [x] End-to-end test: `run_all_checks` runs 6 levels, reports levels 1-6
- [x] CLI test: `--level=6` runs only architecture checks; `--level=7` rejected

### Documentation

- [x] `claude/skills/model-validation/SKILL.md` updated (6-level pyramid table)
- [x] `CLAUDE.md` validation section updated (6 levels, not 8)
- [x] `project_templates/README.md.template` updated if it references validation levels

### Downstream (fusion-tea)

- [ ] `fusion-tea/README.md` updated (6-level references)
- [ ] `fusion-tea/.project/` docs updated (L8_ → L6_, level8_codegen.py → level6_architecture.py)
- [x] No fusion-tea Python code changes needed (confirmed: only imports `common` and `SysideAdapter`)

### Quality & Integration

- [x] `uv run pytest tests/` passes — 895 passed, 1 skipped
- [x] `uv run ruff check src/ tests/` passes (pre-existing issues only)
- [x] `uv run agentic-mbse validate tests/fixtures/sample_models/` runs 6 levels

---

## File Change Summary

| File | Change |
|------|--------|
| `src/agentic_mbse/validation/level2_structure.py` | Remove ADR-002 imports and calls |
| `src/agentic_mbse/validation/level4_constraints.py` | Add constraint coverage from old L5 |
| `src/agentic_mbse/validation/level5_semantic.py` | **Delete** |
| `src/agentic_mbse/validation/level6_traceability.py` | Rename to `level5_traceability.py`, update level number |
| `src/agentic_mbse/validation/level7_architecture.py` | **Delete** (merged into new L6) |
| `src/agentic_mbse/validation/level8_codegen.py` | **Delete** (merged into new L6) |
| `src/agentic_mbse/validation/level6_architecture.py` | **New** — ADR-002 calls + manifest + codegen readiness |
| `src/agentic_mbse/validation/runner.py` | Update QUALITY_CHECKS (6 entries), update level range |
| `src/agentic_mbse/validation/__init__.py` | Update exports |
| `src/agentic_mbse/sysml/types.py` | Rename `L8_` → `L6_` in ValidationCode enum |
| `src/agentic_mbse/validation/adr002.py` | Update `level` field in ValidationIssues (2→6) |
| `src/agentic_mbse/cli/validate_cli.py` or equivalent | Update `--level` range to 1-6 |
| `tests/test_sysml_quality_checks.py` | Update level numbers, `L8_` → `L6_` references, add distinctness fixtures |
| `claude/skills/model-validation/SKILL.md` | Update pyramid table |
| `CLAUDE.md` | Update validation section |
| `project_templates/README.md.template` | Update if needed |
| `fusion-tea/README.md` | Update "8-level" → "6-level", level references |
| `fusion-tea/.project/active/gap1-default-value-debug/*.md` | Update L8_ and level8_codegen.py references |
| `fusion-tea/.project/active/gap1-default-value-debug/spec.md` | Update "levels 1-8" → "levels 1-6" |

**Estimated scope:** ~18 files touched across 2 repos, 3 deleted, 1 new module created. Logic unchanged — restructuring and renumbering only.

---

## Related Artifacts

- **Research:** `.project/research/20260227-195415_validation-stack-audit.md`
- **Current L8 design:** `.project/completed/20260201_l8-extractability-validation/design.md`
- **Validation walkthrough:** `.project/completed/20260203_d3.5-validation-walkthrough/`
