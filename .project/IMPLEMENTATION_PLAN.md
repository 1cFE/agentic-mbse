# Implementation Plan: agentic-mbse

**Date**: 2026-02-09
**Status**: Active
**Last Updated**: 2026-02-09 (Planning iteration completed — spec-driven gap analysis)

---

## Executive Summary

**Current Sprint**: TASK-001 (PDF Skill Deployment) — Ready for implementation
**Branch**: `ralph/doc-ingest`
**Status**: Spec ✅ Design ✅ Implementation ⏳

**Critical Path**: Complete TASK-001 → Test → Merge to main → Unblocks Tier 2 (Docling MCP) extraction for all users

**Planning Methodology**:
- ✅ Parallel exploration of 1 active + 40 completed specs
- ✅ Code search for gaps (TODOs, NotImplementedError, placeholders)
- ✅ Validation against 43 Python source files in `src/agentic_mbse/`
- ✅ No false negatives (all completed specs genuinely implemented)

---

## Overview

This document tracks concrete, actionable implementation tasks derived from spec-driven gap analysis. Tasks are prioritized based on:
1. Critical path dependencies
2. User-facing value
3. Completeness (finishing in-progress work before starting new features)
4. Technical debt reduction

Each task references the spec(s) it addresses and identifies verification mechanisms.

---

## Current State Summary

### ✅ Complete Modules
- **Validation pyramid**: All 8 levels implemented (L1-L4, L6-L8 production-ready; L5 has placeholder)
- **SysML utilities**: Full binding, expression, graph analysis, syside adapter
- **Document extraction**: 4-layer pipeline complete (pymupdf/docling/pandoc → GMFT tables → Claude structure → AI repair)
  - Index generation with section parsing and checksums
  - Quality gates and cross-validation for safe AI repairs
  - 3 backend options with smart fallback chains
- **Project management**: 14 operations implemented
  - State derivation from filesystem (no separate state store)
  - Dashboard generation, epic/work-item lifecycle
  - 8 structured file parsers with Pydantic models (FR-1 through FR-8 from D4.1)
- **CLI foundation**: 5 main commands (`validate`, `init`, `extract`, `status`, `pm`) with 14 PM subcommands
- **Architecture redesign**: 4-directory model (knowledge/, project/, work/, data/)
  - 14 MBSE commands, 5 specialized agents, 10 skills deployed via init
  - User-owned vs tool-owned template classification
  - Hash-based modification detection

### 🚧 In Progress
- **PDF Skill Deployment** (ITEM-DOCLING-001): Spec + Design complete, implementation pending
  - Branch: `ralph/doc-ingest`
  - Priority: P2
  - Blocks: Tier 2 extraction (Docling MCP) functionality

### 🔍 Known Gaps (Validated 2026-02-09)

**Confirmed via code analysis (43 Python files in src/):**

1. **Level 5 semantic validation** (`validation/level5_semantic.py:50`)
   - Status: Placeholder with "needs full implementation" comment
   - Missing: `check_unit_consistency()` — SI/ISQ unit compatibility across bindings
   - Missing: Constraint coverage heuristics (critical attributes need assert/require)
   - Evidence: `grep -n "Placeholder" src/agentic_mbse/validation/level5_semantic.py`

2. **Insight supersession** (`pm/operations.py:1135`)
   - Status: `raise NotImplementedError` with TODO reference to workflows.md § 6.1
   - Prerequisite exists: `InsightStatus.SUPERSEDED` enum value (no code changes needed)
   - Evidence: `grep -A2 "def supersede_insight" src/agentic_mbse/pm/operations.py`

3. **Model-to-work-item traceability** (`pm/operations.py:849`)
   - Status: TODO comment in `impact_query()` — returns empty `affected_work_items` list
   - Missing: Mapping strategy (doc comments vs frontmatter vs heuristic)
   - Evidence: `grep -B2 -A2 "affected_work_items.*TODO" src/agentic_mbse/pm/operations.py`

4. **Test coverage gaps** (validation levels 4-7)
   - Status: Basic smoke tests exist, but fewer edge case fixtures than L2/L3/L8
   - Missing: Boundary conditions (empty models, missing manifests, partial constraints)
   - Missing: False positive/negative test scenarios
   - Evidence: `ls tests/fixtures/level{4,5,6,7}/ | wc -l` vs `ls tests/fixtures/level{2,3,8}/ | wc -l`

---

## Specification Coverage Analysis

**Methodology**: Parallel exploration of `.project/specs/`, `.project/active/`, and `.project/completed/` directories to extract requirements, then searched `src/` codebase for implementation evidence.

### Completed Specifications (40 work items in `.project/completed/`)

All completed work items have been implemented and verified. Key deliverables:

| Spec | Implementation Status | Evidence |
|------|----------------------|----------|
| **Model Regression Testing** | ✅ Complete | Tests infrastructure in `tests/models/`, spec/plan/implement workflow integration |
| **New Project Templates (D1.1)** | ✅ Complete | 6 templates in `project_templates/`: KNOWLEDGE.md, ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, EPIC_GUIDE.md, epic_template.md |
| **Tool-Owned File Safety** | ✅ Complete | Hash-based detection in `cli/__init__.py:597-622`, LOCAL_GUIDE.md template |
| **D4.1 — PM Parsers** | ✅ Complete | 8 parsers in `pm/parser.py` returning Pydantic models with warnings pattern |
| **Corpus Benchmark + Ship** | ✅ Complete | Validation rubric, baseline report, v3 pipeline benchmarked (4/5 new docs pass) |
| **D1.4 — cmd_init() Rewiring** | ✅ Complete | 4-directory architecture (`knowledge/`, `project/`, `work/`, `data/`) in init |
| **Pipeline Integration + CLI Wiring** | ✅ Complete | 4-layer extraction in `extraction/` (pymupdf → GMFT → Claude structure → AI repair) |

### Active Specifications (1 work item in `.project/active/`)

| Spec | Status | Gap Identified |
|------|--------|----------------|
| **PDF Skill Deployment** | Spec + Design complete, implementation pending | TASK-001 (P1) |

### Specifications Without Active Work Items

These specifications were referenced in completed work but don't have standalone active work items:

- **Validation Pyramid Levels 1-8**: All implemented in `validation/level*.py` (L5 has placeholder)
- **SysML Utilities**: Complete in `sysml/` module (expression, binding, graph, syside_adapter)
- **PM Operations (14 total)**: All implemented except `supersede_insight()` (NotImplementedError)

---

## Priority Definitions

- **P0 (Critical)**: Blocks core functionality, production bugs, security issues
- **P1 (High)**: User-facing features with specs drafted, blocking integration tests
- **P2 (Medium)**: Enhancements, stretch goals with designs complete
- **P3 (Low)**: Nice-to-have, technical debt, documentation improvements

---

## Task List

### P1: High Priority (Complete In-Progress Work)

#### [DONE] TASK-001: PDF Skill Deployment — Docling MCP Auto-Setup
**Addresses**: `.project/active/pdf-skill-deployment/spec.md`, `.project/active/pdf-skill-deployment/design.md`
**Spec Status**: Draft (FR-1 through FR-11 defined)
**Design Status**: Draft (8 components specified)
**Priority**: P1
**Estimated Complexity**: MEDIUM (~6 files modified)
**Branch**: `ralph/doc-ingest` (current branch)

**Problem**: The `pdf-analysis` skill ships with 3-tier pipeline but Tier 2 (Docling MCP) requires manual setup. Users get broken `mcp__docling__*` tool references.

**Requirements** (from spec.md FR-1 through FR-11):
- FR-1: `agentic-mbse init` runs Docling setup by default
- FR-2: `--no-docling` flag for opt-out
- FR-3: System resource detection → tier classification (constrained ≤8GB / moderate 9-16GB / comfortable 17GB+)
- FR-4: Wrapper script creation at `~/.local/bin/docling-mcp-wrapper.sh` with tier-appropriate thread limits
- FR-5: MCP registration via `claude mcp add --scope user`
- FR-6: Environment report generation (`~/.docling-mcp-env.md`)
- FR-7: Tier-adapted SKILL.md installation (content varies by tier — Tier 2 guidance presence, page-count limits)
- FR-8: When `--no-docling`, SKILL.md describes only Tier 1 + Tier 3 (no Docling MCP references)
- FR-9: Re-init must NOT create duplicate MCP registrations
- FR-10: `replicate_setup.sh` must call setup script in dev mode
- FR-11: Setup script must be bundled as resource (available in pip-installed packages)

**Implementation Steps** (from design.md Components 1-10):
1. **Component 2**: Move `.project/active/pdf-skill/setup-docling.sh` → `scripts/setup-docling.sh`
2. **Component 3**: Modify setup script helpers to write progress to stderr (keeps stdout clean for tier output)
3. **Component 2**: Add `get_scripts_dir()` helper to `cli/__init__.py` (follows pattern of `get_commands_dir()`)
4. **Component 1**: Add `--no-docling` argument to init parser (line ~1119)
5. **Component 4**: Implement `_read_docling_tier()` to parse tier from `~/.docling-mcp-env.md`
6. **Component 5**: Implement `_patch_skill_for_tier()` to adapt SKILL.md based on tier:
   - Strip/retain conditional blocks marked with `<!-- DOCLING_START/END -->`
   - Substitute `{DOCLING_TIER}` and `{MAX_PAGES}` placeholders
   - Update description "3-tier" → "2-tier" when no-docling
7. **Component 4**: Add Docling setup subprocess call in `cmd_init()` after skills install (line ~833)
   - 10-minute timeout (first-run model download ~500MB)
   - Graceful fallback to 2-tier skill on failure
8. **Component 10**: Add pymupdf4llm availability check with guidance message
9. **Component 8**: Update `replicate_setup.sh` with `setup_docling_mcp()` function
10. **Component 6**: Add marker comments to `claude/skills/pdf-analysis/SKILL.md` and `references/extraction-details.md`
11. **Component 9**: Update `pyproject.toml` to bundle `scripts/setup-docling.sh` in wheel and sdist

**Files Modified**:
- `src/agentic_mbse/cli/__init__.py` (~150 lines added: `get_scripts_dir()`, `_read_docling_tier()`, `_patch_skill_for_tier()`, subprocess call, pymupdf4llm check)
- `scripts/setup-docling.sh` (new, moved from `.project/active/pdf-skill/`)
  - Modify helpers: `info()`, `ok()`, `warn()`, `err()` → write to stderr (>&2)
- `scripts/replicate_setup.sh` (~30 lines added: `setup_docling_mcp()` function + call in main())
- `claude/skills/pdf-analysis/SKILL.md` (add `<!-- DOCLING_START/END -->` markers, `{DOCLING_TIER}`, `{MAX_PAGES}` placeholders)
- `claude/skills/pdf-analysis/references/extraction-details.md` (add `<!-- DOCLING_START/END -->` markers)
- `pyproject.toml` (wheel + sdist bundling: `scripts/setup-docling.sh`)

**Verified By**:
- Unit tests: `_read_docling_tier()` parsing, `_patch_skill_for_tier()` logic
- Integration tests: `test_cli.py::test_init_with_no_docling`, `test_init_docling_setup`
- Manual verification: `claude mcp list` shows docling connected after init
- Manual verification: SKILL.md content varies by tier

**Blockers**: None
  - Spec: Draft (all 11 FRs defined)
  - Design: Draft (8 components detailed with integration strategy)
  - Dependencies: All available (bash, subprocess, uv/uvx, claude CLI assumed available)

**Known Risks** (from design.md):
  - Setup timeout on first run (500MB model download) → 10-min timeout + graceful fallback
  - OOM on constrained systems → Script handles OOM detection, init falls back to 2-tier
  - macOS compatibility: `/proc/meminfo` is Linux-only (document as known limitation)

**Depends On**: Nothing (can start immediately)

**Implementation-Ready Steps** (from design.md Components 1-10):
1. Add `<!-- DOCLING_START/END -->` markers to SKILL.md and extraction-details.md
2. Move `.project/active/pdf-skill/setup-docling.sh` → `scripts/setup-docling.sh`
3. Modify setup script helpers to write to stderr (keeps stdout clean for tier output)
4. Add `get_scripts_dir()` helper to `cli/__init__.py`
5. Add `--no-docling` argument to init parser
6. Implement `_read_docling_tier()` to parse tier from `~/.docling-mcp-env.md`
7. Implement `_patch_skill_for_tier()` for conditional content blocks
8. Add Docling setup subprocess call in `cmd_init()` after skills install
9. Add pymupdf4llm availability check with guidance message
10. Update `replicate_setup.sh` with `setup_docling_mcp()` function
11. Update `pyproject.toml` to bundle `scripts/setup-docling.sh`
12. Write unit tests: `_read_docling_tier()`, `_patch_skill_for_tier()`
13. Write integration tests: `test_init_with_no_docling`, `test_init_docling_setup`
14. Manual verification: `claude mcp list`, SKILL.md content varies by tier

---

### P2: Medium Priority (Enhancements & Stretch Goals)

#### TASK-002: Level 5 Semantic Validation — Full Implementation
**Addresses**: `validation/level5_semantic.py` placeholder, validation pyramid completeness
**Priority**: P2
**Estimated Complexity**: MEDIUM (~3 files)

**Problem**: Level 5 currently has placeholder checks with "needs full implementation" comments. Unit consistency and constraint coverage validation is incomplete.

**Requirements**:
- Implement unit consistency checks (validate SI/ISQ unit compatibility across bindings)
- Implement constraint coverage checks (ensure critical attributes have `assert`/`require` constraints)
- Add proper error messages with ValidationCode enum entries
- Maintain consistency with Levels 1-8 reporting format

**Implementation Steps**:
1. Research unit checking approaches in syside/SysML v2 type system
2. Define unit compatibility rules (reference KerML spec via kerml-expert agent)
3. Implement unit extraction from attribute types
4. Implement cross-binding unit validation
5. Define constraint coverage heuristics (what makes an attribute "critical"?)
6. Implement constraint presence checks
7. Add `L5_UNIT_MISMATCH`, `L5_MISSING_CONSTRAINT` to ValidationCode enum
8. Update `level5_semantic.py` with full implementations
9. Add comprehensive test fixtures to `tests/fixtures/level5/`
10. Write unit tests for each check type

**Files Modified**:
- `src/agentic_mbse/validation/level5_semantic.py` (~100 lines replaced)
- `src/agentic_mbse/sysml/types.py` (new ValidationCode entries)
- `tests/test_validation/test_level5.py` (new test cases)
- `tests/fixtures/level5/` (new fixtures)

**Verified By**:
- Unit tests: `test_level5_unit_consistency`, `test_level5_constraint_coverage`
- Integration tests: Run against fusion-tea corpus, verify new issues detected
- Validation: `agentic-mbse validate --level=5 models/` produces actionable reports

**Blockers**: Requires research into SysML v2 unit system (use kerml-expert agent)

**Depends On**: Nothing (independent task)

---

#### [DONE] TASK-003: Insight Supersession Operation (D4.4 Stretch Goal)
**Addresses**: PM operations completeness, `operations.py:1135` NotImplementedError
**Spec**: D4.4 workflows.md § 6.1 (supersession flow)
**Priority**: P2
**Estimated Complexity**: SMALL (~2 files)
**Status**: Completed 2026-02-09

**Problem**: `supersede_insight()` operation is stubbed with NotImplementedError. Users cannot mark insights as outdated and provide replacements.

**Requirements** (from D4.4 workflows.md § 6.1):
- Mark insight as superseded (status update)
- Link to replacement insight(s)
- Update KNOWLEDGE.md with supersession metadata
- Preserve original insight text with "SUPERSEDED BY" annotation
- Update traceability CSV to reflect supersession

**Implementation Steps**:
1. Read D4.4 spec for supersession workflow details
2. ✅ **ALREADY EXISTS**: `InsightStatus.SUPERSEDED` enum value (types.py:64)
3. Implement KNOWLEDGE.md parsing for supersession links (extend parser.py)
4. Implement insight status update logic in `supersede_insight()` (replace NotImplementedError)
5. Add supersession metadata to insight section (e.g., `**SUPERSEDED BY**: DI-042`)
6. Update traceability CSV to mark superseded rows
7. Add unit tests for supersession operation
8. Add CLI test for `agentic-mbse pm supersede-insight`

**Files Modified**:
- `src/agentic_mbse/pm/operations.py` (~50 lines implemented at line 1135)
- `src/agentic_mbse/pm/parser.py` (extend KNOWLEDGE.md parser for supersession links)
- `tests/test_pm_operations.py` (new test cases)

**Prerequisites**:
- ✅ `InsightStatus.SUPERSEDED` already exists (types.py:64)

**Verified By**:
- Unit tests: `test_supersede_insight_updates_knowledge`, `test_supersede_insight_updates_traceability`
- Manual test: `agentic-mbse pm supersede-insight DI-001 --replacement DI-042`

**Blockers**: None (implementation is straightforward given existing operations patterns)

**Depends On**: Nothing (independent task)

---

#### TASK-004: Model-to-Work-Item Traceability in Impact Query
**Addresses**: `operations.py:849` TODO, impact analysis completeness
**Priority**: P2
**Estimated Complexity**: SMALL (~2 files)

**Problem**: `impact_query()` has a TODO: "Populate affected_work_items when a model→work-item mapping exists". Currently returns empty list for work items.

**Requirements**:
- Define model element → work item mapping (e.g., via doc comments, metadata, or heuristic)
- Parse work item specs for referenced model elements
- Implement reverse lookup: given model element, find work items that reference it
- Populate `affected_work_items` list in `ImpactQueryResult`

**Implementation Steps**:
1. Survey fusion-tea for examples of model→work-item links
2. Define mapping strategy (doc comment pattern? spec.md frontmatter?)
3. Implement work item spec parsing for model references
4. Build reverse index: element qualified name → work item IDs
5. Update `impact_query()` to populate `affected_work_items`
6. Add test fixtures with model→work-item links
7. Write unit tests for impact query with work items

**Files Modified**:
- `src/agentic_mbse/pm/operations.py` (~30 lines added)
- `src/agentic_mbse/pm/parser.py` (add model reference extraction)
- `tests/test_pm_operations.py` (new test cases)
- `tests/fixtures/pm/` (new fixtures with model links)

**Verified By**:
- Unit tests: `test_impact_query_finds_affected_work_items`
- Integration test: Query fusion-tea element, verify work items appear
- Manual test: `agentic-mbse pm impact-query "fusion_tea::Mission::power_output"`

**Blockers**: Requires design decision on mapping strategy (defer if unclear)

**Depends On**: Nothing (can implement once strategy is defined)

---

#### TASK-005: Enhanced Test Coverage for Validation Levels 4-7
**Addresses**: Test coverage gaps, validation robustness
**Priority**: P2
**Estimated Complexity**: MEDIUM (~4 files)

**Problem**: Validation levels 4-7 have basic smoke tests but fewer detailed edge case tests compared to Level 2, 3, 8. This creates risk for false positives/negatives.

**Requirements**:
- Add edge case fixtures for each level
- Test boundary conditions (empty models, missing manifests, etc.)
- Test false positive scenarios (valid models that trigger warnings)
- Test false negative scenarios (invalid models that pass)
- Match test depth of L2/L3/L8 suites

**Implementation Steps**:
1. Audit existing L4-L7 tests, identify gaps
2. Create new fixtures for each gap category:
   - L4: Missing constraints, partial coverage, complex expressions
   - L5: (after TASK-002 completes) unit mismatches, coverage edge cases
   - L6: Missing docs, partial docs, documentation anti-patterns
   - L7: Missing manifest, invalid subsystems, boundary violations
3. Write unit tests for each new fixture
4. Add integration tests for multi-level validation runs
5. Document expected behavior in test docstrings

**Files Modified**:
- `tests/fixtures/level4/`, `tests/fixtures/level5/`, `tests/fixtures/level6/`, `tests/fixtures/level7/` (new fixtures)
- `tests/test_validation/test_level4.py` through `test_level7.py` (new test cases)

**Verified By**:
- All new tests pass
- Coverage report shows >90% for validation levels 4-7
- No regressions in existing tests

**Blockers**: TASK-002 (Level 5 implementation) should complete first for L5 edge cases

**Depends On**: TASK-002 for Level 5 tests

---

### P3: Low Priority (Technical Debt & Improvements)

#### TASK-006: Architectural Integrity Testing Walkthroughs
**Addresses**: User onboarding, validation level documentation
**Priority**: P3
**Estimated Complexity**: SMALL (~1 file)

**Problem**: Level 7 architectural integrity validation is implemented but lacks user-facing documentation and examples.

**Requirements**:
- Create walkthrough document showing how to use L7 validation
- Provide example design manifest JSON files
- Document subsystem composition patterns
- Add to `docs/validation/` directory

**Implementation Steps**:
1. Write `docs/validation/level7-walkthrough.md`
2. Create example manifest files in `docs/validation/examples/`
3. Document manifest schema and validation rules
4. Add links from README.md and CLAUDE.md

**Files Modified**:
- `docs/validation/level7-walkthrough.md` (new)
- `docs/validation/examples/manifest-example.json` (new)
- `README.md`, `CLAUDE.md` (links added)

**Verified By**:
- Manual review: Walkthrough is clear and complete
- User feedback: Document enables users to create valid manifests

**Blockers**: None

**Depends On**: Nothing

---

#### TASK-007: LCOE Costing Patterns (EPIC-LCOE-001)
**Addresses**: Backlog P2 item, fusion-tea domain patterns
**Priority**: P3 (tracking in fusion-tea)
**Estimated Complexity**: LARGE (~10+ files across repos)

**Problem**: Cost modeling patterns from fusion-tea (NumericalFunctions::sum, multiplicity aggregation, part redefinition) need extraction and generalization for agentic-mbse.

**Requirements**:
- Extract Cost Model Imports pattern
- Extract Multiplicity Cost Aggregation pattern
- Extract Part Redefinition pattern (dot notation vs redefines)
- Extract Parameterized Multiplicity pattern
- Document in `docs/patterns/`
- Add to MODELING_GUIDE.md or create new skill

**Status**: Active in fusion-tea repository. Patterns will be backported to agentic-mbse once validated.

**Files Modified**: TBD (depends on fusion-tea pattern stabilization)

**Verified By**: fusion-tea validation passes with patterns applied

**Blockers**: Requires fusion-tea pattern extraction first

**Depends On**: fusion-tea EPIC-LCOE-001 completion

---

#### TASK-008: Visualization Tool Integration (EPIC-VIZ-001)
**Addresses**: Backlog P2 item, model visualization
**Priority**: P3 (tracking in fusion-tea)
**Estimated Complexity**: LARGE (~10+ files)

**Problem**: SysML models lack visual representation. Need integration with graphing tools (Graphviz, Mermaid, or native SysIDE viewer).

**Requirements**: TBD (awaiting design phase in fusion-tea)

**Status**: Tracking in fusion-tea repository.

**Files Modified**: TBD

**Verified By**: TBD

**Blockers**: Requires design phase completion

**Depends On**: fusion-tea EPIC-VIZ-001 design

---

## Sequencing & Dependencies

```
Current State
     │
     ├──► TASK-001 (PDF Skill Deployment) ─────► Merge to main
     │         │
     │         └──► PR #4 (ralph/doc-ingest → main)
     │
     ├──► TASK-002 (Level 5 Implementation) ────► TASK-005 (L5 Test Coverage)
     │
     ├──► TASK-003 (Insight Supersession) ──────► Independent
     │
     ├──► TASK-004 (Work-Item Traceability) ────► Independent
     │
     └──► TASK-006, TASK-007, TASK-008 ──────────► Independent (low priority)
```

**Critical Path**: TASK-001 → Merge → Release (unblocks Tier 2 extraction for users)

---

## Recommended Implementation Sequence

Based on gap analysis and dependency analysis:

### Phase 1: Complete In-Progress Work (Week 1)
**Goal**: Merge current branch to main with PDF skill fully functional

1. **TASK-001** (PDF Skill Deployment) — P1, MEDIUM
   - All design decisions made, components specified
   - 11 implementation steps mapped to 8 design components
   - Verification: Unit tests + manual MCP registration check
   - **Target**: 5-7 implementation days

### Phase 2: Fill Critical Gaps (Week 2-3)
**Goal**: Complete placeholder implementations with defined specs

2. **TASK-002** (Level 5 Semantic Validation) — P2, MEDIUM
   - Requires research into SysML v2 unit system (use kerml-expert agent)
   - Blocking TASK-005 for Level 5 test coverage
   - **Target**: 3-5 implementation days after research

3. **TASK-003** (Insight Supersession) — P2, SMALL
   - Straightforward implementation (enum exists, pattern established)
   - Independent of other tasks
   - **Target**: 1-2 implementation days

### Phase 3: Quality Improvements (Week 4+)
**Goal**: Enhance robustness and coverage

4. **TASK-004** (Work-Item Traceability) — P2, SMALL
   - Requires design decision on mapping strategy first
   - Can defer until mapping strategy is defined
   - **Target**: 2-3 implementation days

5. **TASK-005** (Enhanced Test Coverage L4-L7) — P2, MEDIUM
   - Depends on TASK-002 completion for Level 5 tests
   - Improves robustness across validation levels
   - **Target**: 3-5 implementation days

### Phase 4: Low Priority (Backlog)
**Goal**: Documentation and cross-repo patterns

6. **TASK-006** (L7 Walkthrough) — P3, SMALL (documentation)
7. **TASK-007** (LCOE Patterns) — P3, LARGE (tracking in fusion-tea)
8. **TASK-008** (Visualization) — P3, LARGE (tracking in fusion-tea)

---

## Quick Start: TASK-001 Implementation Checklist

**Before you begin**: Verify branch `ralph/doc-ingest` is current and tests pass

### Phase 1: Source Preparation (30 min)
- [ ] Add `<!-- DOCLING_START/END -->` markers to `claude/skills/pdf-analysis/SKILL.md` (Component 6)
- [ ] Add `<!-- DOCLING_START/END -->` markers to `claude/skills/pdf-analysis/references/extraction-details.md` (Component 6)
- [ ] Add `{DOCLING_TIER}` and `{MAX_PAGES}` placeholders to SKILL.md tier hint section (Component 6)
- [ ] Move `.project/active/pdf-skill/setup-docling.sh` → `scripts/setup-docling.sh` (Component 2)
- [ ] Modify setup script helpers (`info`, `ok`, `warn`, `err`) to write to stderr (>&2) (Component 3)

### Phase 2: CLI Implementation (2-3 hours)
- [ ] Add `get_scripts_dir()` helper to `cli/__init__.py` (Component 2, line ~157)
- [ ] Add `--no-docling` flag to init parser (Component 1, line ~1119)
- [ ] Implement `_read_docling_tier()` function (Component 4)
- [ ] Implement `_patch_skill_for_tier()` function (Component 5)
- [ ] Add Docling setup subprocess call in `cmd_init()` after skills install (Component 4, line ~833)
- [ ] Add pymupdf4llm availability check after Docling setup (Component 10)
- [ ] Skip patching in dev mode (Component 5 logic)

### Phase 3: Replication Script (1 hour)
- [ ] Add `setup_docling_mcp()` function to `replicate_setup.sh` (Component 8)
- [ ] Call `setup_docling_mcp()` from `main()` after `install_claude_components` (Component 8)

### Phase 4: Packaging (30 min)
- [ ] Update `pyproject.toml` wheel force-include: `"scripts/setup-docling.sh"` (Component 9)
- [ ] Update `pyproject.toml` sdist include: `"scripts/setup-docling.sh"` (Component 9)

### Phase 5: Testing (2-3 hours)
- [ ] Write unit test: `test_read_docling_tier()` parsing logic
- [ ] Write unit test: `test_patch_skill_for_tier_no_docling()` (remove Docling sections)
- [ ] Write unit test: `test_patch_skill_for_tier_constrained()` (substitute placeholders)
- [ ] Write unit test: `test_patch_skill_for_tier_comfortable()` (substitute placeholders)
- [ ] Write integration test: `test_init_with_no_docling()` (end-to-end)
- [ ] Write integration test: `test_init_docling_setup()` (end-to-end with mocked subprocess)
- [ ] Run full test suite: `uv run pytest tests/`

### Phase 6: Manual Verification (1 hour)
- [ ] Test fresh init: `agentic-mbse init /tmp/test-proj` → verify `claude mcp list` shows docling
- [ ] Test no-docling: `agentic-mbse init --no-docling /tmp/test-proj2` → verify SKILL.md has no mcp__docling
- [ ] Test re-init: Run init twice → verify no duplicate MCP registrations
- [ ] Verify `~/.docling-mcp-env.md` contains correct tier info
- [ ] Invoke `/pdf-analysis` skill → verify tier-appropriate guidance appears

### Phase 7: Completion
- [ ] Commit with message referencing TASK-001 and FR-1 through FR-11
- [ ] Update `.project/IMPLEMENTATION_PLAN.md` → move TASK-001 to "Completed Tasks"
- [ ] Ready for PR review

**Estimated Total Time**: 8-12 hours (1-2 implementation days)

---

## Next Steps

1. **Immediate**: Begin TASK-001 implementation using checklist above (spec + design complete, ready for code)
2. **Week 1 target**: Complete TASK-001, test, merge `ralph/doc-ingest` → `main`, create PR #4
3. **Week 2 target**: Research SysML v2 unit system (TASK-002 prep), implement TASK-003
4. **Week 3 target**: Complete TASK-002, start TASK-005 (enhanced test coverage)
5. **Ongoing**: Monitor fusion-tea for LCOE patterns and visualization progress (TASK-007, TASK-008)

---

## Completion Tracking

### Completed Tasks
- **TASK-001**: PDF Skill Deployment (completed 2026-02-09)
  - Phase 1-4: Core integration (markers, setup script, CLI, pyproject.toml)
  - Phase 5: Unit tests (6 new tests, all passing)
  - Phase 6: Code quality checks (linting, formatting)
  - Commits: e13c80f, cbf2167, 6e2d757
  - Status: Implementation complete, ready for PR and manual verification
  - Note: Manual verification requires actual MCP server interaction (claude mcp list)

- **TASK-003**: Insight Supersession Operation (completed 2026-02-09)
  - Implemented full supersession flow per workflows.md § 6.1
  - Operations: supersede_insight() in operations.py (replaces NotImplementedError)
  - Features: Update old insight status, create new insight with supersedes link, generate impact report
  - Impact analysis: Query traceability matrix, identify affected model elements
  - Impact reports: Written to knowledge/research/impacts/{DI-XXX}_superseded.md
  - Tests: 6 comprehensive unit tests (basic flow, validation, edge cases)
  - Validation: All tests pass (pytest), no type errors (mypy), clean linting (ruff)
  - Files modified: src/agentic_mbse/pm/operations.py, tests/test_pm_operations.py
  - Status: Complete and tested

### In Progress
*None*

### Blocked
*None*

---

## Verification Matrix

| Task | Unit Tests | Integration Tests | Manual Verification | Documentation |
|------|------------|-------------------|---------------------|---------------|
| TASK-001 | ✅ Tier parsing, SKILL.md patching | ✅ End-to-end init tests | ✅ MCP registration, skill invocation | ✅ SKILL.md adapts |
| TASK-002 | ✅ Unit consistency, constraint coverage | ✅ Validation against corpus | ✅ Level 5 reports | ✅ ValidationCode docs |
| TASK-003 | ✅ Supersession logic | ✅ CLI command test | ✅ Manual PM operation | ❌ N/A (operation) |
| TASK-004 | ✅ Impact query with work items | ✅ Traceability lookup | ✅ Query fusion-tea element | ❌ N/A (internal) |
| TASK-005 | ✅ All new fixtures | ✅ Multi-level runs | ❌ N/A (test task) | ❌ N/A (test task) |
| TASK-006 | ❌ N/A (docs) | ❌ N/A (docs) | ✅ Walkthrough review | ✅ Level 7 guide |

---

## Notes

### Known Limitations
- **macOS support for Docling setup**: `setup-docling.sh` uses `/proc/meminfo` (Linux-only). macOS would need `sysctl` support (future enhancement).
- **Level 5 semantic validation**: Requires SysML v2 unit system research before implementation.
- **Visualization integration**: Awaiting design decisions in fusion-tea before backporting.

### Design Decisions Needed
- **TASK-004**: Model→work-item mapping strategy (doc comments vs frontmatter vs heuristic)
- **TASK-007**: Which LCOE patterns are generalizable vs fusion-tea-specific

### Archive Policy
- Completed tasks stay in "Completed Tasks" section for 30 days, then move to `.project/completed/IMPLEMENTATION_PLAN_ARCHIVE.md`
- Plan is updated after each task completion with completion date and final verification status

---

## Planning Iteration Notes

**Iteration Date**: 2026-02-09
**Methodology**: Spec-driven gap analysis with parallel exploration

### Process Followed

1. **Parallel Spec Exploration** (Explore agent, haiku model, ~60s)
   - Explored all `.project/specs/`, `.project/active/`, `.project/completed/` directories
   - Extracted requirements, success criteria, architectural constraints from 40+ work items
   - Identified cross-spec dependencies and verification mechanisms

2. **Current Implementation Survey**
   - Code search: `grep -r "NotImplementedError|TODO|FIXME|placeholder" src/agentic_mbse`
   - Found 5 files with gaps (level2, level4, level5, operations, cli, pm_cli)
   - Verified 43 Python files across 6 modules (validation, extraction, pm, sysml, cli, utils)

3. **Gap Analysis**
   - Cross-referenced spec requirements against actual source code
   - Validated no false negatives (all completed specs genuinely implemented)
   - Identified 4 confirmed gaps with line numbers and evidence

4. **Task Prioritization**
   - P1 (High): TASK-001 (in-progress work with complete spec + design)
   - P2 (Medium): TASK-002 through TASK-005 (gaps with clear scope)
   - P3 (Low): TASK-006 through TASK-008 (docs and cross-repo patterns)

### Key Findings

- **Spec coverage**: 40 completed work items, 1 active work item with spec + design ready
- **Technical debt**: Well-documented (2 NotImplementedError, 1 placeholder L5, 1 TODO)
- **Critical path clear**: TASK-001 is the only blocker for merge to main
- **No false negatives**: Completed specs verified implemented via file search (no assumed features)
- **TASK-001 ready**: 11 FR requirements defined, 8 design components specified, 14-step implementation checklist created

### Changes from Previous Plan

- Expanded TASK-001 with all 11 FR requirements and 8 design components mapped to implementation steps
- Added implementation-ready checklist with phase breakdown and time estimates
- Confirmed `InsightStatus.SUPERSEDED` exists (TASK-003 prerequisite met, verified in types.py:64)
- Added specification coverage analysis section with evidence links
- Added recommended implementation sequence with phase breakdown (Weeks 1-4+)
- Documented all gaps with grep-able evidence (file:line references)

### Verification Strategy

Each task includes:
- **Unit tests**: Specific functions/methods to test
- **Integration tests**: End-to-end CLI workflows
- **Manual verification**: User-facing validation steps
- **Documentation**: Guides or references that prove completeness

### Anti-Patterns Avoided

- ❌ Did not assume features are unimplemented without code search
- ❌ Did not create tasks for features already completed (verified via grep/read)
- ❌ Did not guess at requirements (extracted from actual spec files)
- ❌ Did not create unbounded tasks (all tasks scoped to ~2-6 files, 1-5 days)

---

**Last Review**: 2026-02-09 (Planning iteration)
**Next Review**: After TASK-001 completion (target: 2026-02-16)
**Status**: Ready for implementation — TASK-001 has complete checklist, all prerequisites validated
