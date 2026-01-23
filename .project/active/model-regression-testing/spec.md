# Spec: Model Regression Testing

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-01-23 15:59:52 UTC
**Complexity:** MEDIUM
**Branch:** 1cfe_dev

---

## Business Goals

### Why This Matters

The agentic-mbse toolkit promotes a modeling paradigm where reusable **definitions** live in libraries and **usages** assemble them into designs. This separation enables model reuse across multiple designs but introduces regression risk: when a library definition is modified to support a new design, existing designs that depend on it may silently break.

This mirrors a well-understood problem in software engineering, where the solution is automated regression testing. Without similar infrastructure for SysML models, modelers have no systematic way to detect when library changes break downstream designs.

### Success Criteria

- [ ] Modelers can write pytest-compatible tests that parse and validate SysML models using syside
- [ ] When a library definition changes, running `pytest` reveals any broken designs
- [ ] The workflow (spec → design → plan → implement) naturally produces tested models
- [ ] New projects created via `agentic-mbse init` have testing infrastructure ready to use

### Priority

Foundational infrastructure - value compounds as more models are built on shared libraries.

---

## Problem Statement

### Current State

- `agentic-mbse init` creates project structure but no testing infrastructure
- Spec/plan/implement workflow focuses on model creation, not validation
- No standard location or pattern for model tests
- Modelers must manually verify that library changes don't break existing designs

### Desired Outcome

- Standard `tests/models/` directory for model regression tests
- Spec phase produces evaluatable success criteria (both human and machine-checkable)
- Plan phase explicitly includes test-writing phases
- Clear documentation explaining the testing paradigm
- Modelers get immediate feedback when library changes break designs

---

## Scope

### In Scope

1. **Project structure changes** (`agentic-mbse init`):
   - Create `tests/` directory with `models/` subdirectory
   - Include example/template test file demonstrating syside usage

2. **Documentation updates**:
   - Explain the testing paradigm in project docs (MODELING_GUIDE.md or similar)
   - Document how to write model tests using syside
   - Explain the relationship between specs, tests, and model validation

3. **Spec command guidance** (`claude/commands/spec-model.md`):
   - Emphasize evaluatable success criteria
   - Criteria should be both human-checkable and machine-checkable where possible

4. **Plan command updates** (`claude/commands/plan-model.md`):
   - Add explicit test-writing phases to generated plans
   - Outline what qualities tests should verify (structural, type/interface, constraints)
   - Planning agent takes responsibility for defining testing requirements

5. **Implement command awareness** (`claude/commands/implement-model.md`):
   - Follow test phases from plan
   - Aware of testing patterns and `tests/models/` location

### Out of Scope

- Automated test generation (AI writing tests without human guidance)
- CI/CD integration (automated test runs on commits)
- Test coverage metrics for models
- Visual/diagram regression testing
- Test result reporting beyond pytest output

### Edge Cases & Considerations

- **Behavioral models**: Tests may be organized by functionality rather than per-model
- **Library-only work items**: May need tests that validate definition interfaces without full usage assembly
- **Incremental adoption**: Existing projects without `tests/` should still work; testing is opt-in

---

## Requirements

### Functional Requirements

> Requirements below are from user's request unless marked [INFERRED]

1. **FR-1**: `agentic-mbse init` MUST create a `tests/` directory with a `models/` subdirectory
2. **FR-2**: Project documentation MUST explain the testing paradigm (pytest-compatible tests that inspect/validate models using syside)
3. **FR-3**: `/spec-model` command SHOULD emphasize evaluatable success criteria that can inform test assertions
4. **FR-4**: `/plan-model` command MUST include phases for writing and running tests to validate implementation
5. **FR-5**: `/implement-model` command MUST be aware of testing requirements and follow test phases from plan
6. **FR-6**: [INFERRED] Init SHOULD include an example/template test file demonstrating syside model inspection
7. **FR-7**: Test organization SHOULD default to one test per model/design but MAY be organized by functionality when appropriate (e.g., behavioral models)
8. **FR-8**: Tests SHOULD verify structural qualities, type/interface compatibility, and constraint satisfaction as appropriate

### Non-Functional Requirements

- **NFR-1**: Testing infrastructure MUST NOT break existing projects (backwards compatible)
- **NFR-2**: Test patterns SHOULD be simple enough for modelers unfamiliar with pytest

---

## Acceptance Criteria

### Core Functionality

- [ ] Running `agentic-mbse init` on a new project creates `tests/models/` directory
- [ ] New projects include documentation explaining model testing paradigm
- [ ] `/spec-model` output includes evaluatable success criteria guidance
- [ ] `/plan-model` output includes explicit test-writing and test-running phases
- [ ] `/implement-model` follows test phases and creates tests in `tests/models/`

### Quality & Integration

- [ ] Existing tests continue to pass
- [ ] Example test file demonstrates syside usage for model inspection
- [ ] Documentation clearly explains the definitions/usages regression risk and how tests mitigate it

---

## Related Artifacts

- **Research:** N/A
- **Design:** `.project/active/model-regression-testing/design.md` (to be created)
- **Epic:** `.project/backlog/BACKLOG.md`

---

**Next Steps:** After approval, proceed to `/_my_design` (for developing the agentic-mbse changes)
