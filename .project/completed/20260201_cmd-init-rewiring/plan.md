# Implementation Plan: D1.4 — `cmd_init()` Rewiring

**Status:** Complete
**Created:** 2026-02-01
**Last Updated:** 2026-02-01

## Source Documents
- **Spec:** `.project/active/cmd-init-rewiring/spec.md`
- **Design:** `.project/active/cmd-init-rewiring/design.md` ← See here for component details, code snippets, exact replacement values

## Implementation Strategy

**Phasing Rationale:**
`cmd_init()` is the production code path and source of truth. It changes first so `replicate_setup.sh` can mirror it. Documentation updates last because they describe what code does.

**Overall Validation Approach:**
- Phase 1 validated by smoke-testing `agentic-mbse init` on a fresh tmpdir
- Phase 2 validated by running `replicate_setup.sh` and comparing output to Phase 1
- Phase 3 validated by grep for stale `modeling_pm/` references
- Existing test suite run after each phase to confirm failures are path-assertion only, not crashes

---

## Phase 1: CSV Template + `cli/__init__.py` Rewiring

### Goal
All Python-side changes: constants, directory creation, SOURCE_INDEX path, CSV install, docstring. After this phase, `agentic-mbse init` produces the full new 4-directory structure.

### Pre-flight
- [x] Run `uv run pytest tests/test_cli.py -v` — confirm all tests pass (baseline)

### Changes Required

**See `design.md` for:** exact replacement values for all constants and code blocks.

#### 1. CSV Template Schema
**File:** `project_templates/data/traceability_matrix.csv` (REVISE)
- [x] Replace header line with D1.3-approved schema → `design.md#change-7`

#### 2. Constants
**File:** `src/agentic_mbse/cli/__init__.py`
- [x] Replace `USER_OWNED_TEMPLATES` list (lines 54–62) → `design.md#change-2`
- [x] Replace `TOOL_OWNED_TEMPLATES` list (lines 64–67) → `design.md#change-2`
- [x] Replace `DEV_MODE_GITIGNORE_PATHS` list (lines 73–82) → `design.md#change-4`

#### 3. Directory Creation
**File:** `src/agentic_mbse/cli/__init__.py`
- [x] Replace `modeling_pm/` directory block (lines 783–789) with loop over new 16-directory list → `design.md#change-1`

#### 4. SOURCE_INDEX.md Path
**File:** `src/agentic_mbse/cli/__init__.py`
- [x] Change `source_index_path` (line 632) from `target / "SOURCE_INDEX.md"` to `target / "knowledge" / "SOURCE_INDEX.md"` → `design.md#change-5`
- [x] Update the `skipped.append` / `created.append` strings from `"SOURCE_INDEX.md"` to `"knowledge/SOURCE_INDEX.md"`

#### 5. CSV Installation Section
**File:** `src/agentic_mbse/cli/__init__.py`
- [x] Add CSV install block after user-owned templates loop (after line ~808) → `design.md#change-6`

#### 6. Docstring
**File:** `src/agentic_mbse/cli/__init__.py`
- [x] Update `cmd_init()` docstring (lines 473–489) → `design.md#change-8`

### Validation

**Automated:**
- [x] `uv run pytest tests/test_cli.py -v` — expect path-assertion failures only (no import errors, no crashes, no new test classes failing that weren't path-related)

**Manual smoke test:**
```bash
tmp=$(mktemp -d)
uv run agentic-mbse init "$tmp"
```
- [x] Verify 4 top-level dirs exist: `knowledge/`, `project/`, `work/`, `data/`
- [x] Verify subdirs: `knowledge/research/{pending,approved,impacts}`, `knowledge/sources/`, `project/intent/`, `work/{backlog,active,completed,analysis,learnings}`
- [x] Verify `models/library/` and `models/designs/` exist
- [x] Verify `knowledge/SOURCE_INDEX.md` exists (not root `SOURCE_INDEX.md`)
- [x] Verify `knowledge/KNOWLEDGE.md` exists
- [x] Verify `project/{OVERVIEW.md,ARCHITECTURE.md,REQUIREMENTS.md,VALIDATION_MATRIX.md,MODELING_GUIDE.md,MODELING_PROCESS.md}` exist
- [x] Verify `work/BACKLOG.md`, `work/EPIC_GUIDE.md`, `work/backlog/epic_template.md`, `work/learnings/RAW_LEARNINGS.md` exist
- [x] Verify `data/traceability_matrix.csv` exists with correct header (`head -1`)
- [x] Verify NO `modeling_pm/` directory
- [x] Verify `--dev` mode: tool-owned files are symlinks, `.gitignore` has new paths (no `modeling_pm/`)
- [x] Verify idempotency: run init twice, second run succeeds and skips user-owned files

**What We Know Works After This Phase:**
`agentic-mbse init` (both normal and `--dev` mode) produces the correct new structure. The production code path is complete.

---

## Phase 2: `replicate_setup.sh` Rewrite

### Goal
Bring the developer convenience script into parity with the rewired `cmd_init()`: same directories, same components, same template destinations.

### Changes Required

**See `design.md#change-9` for:** all function rewrites with exact bash code.

**File:** `scripts/replicate_setup.sh`

#### 1. Agent Loop
- [x] Replace 2-agent loop (lines 62–68) with 5-agent loop (remove deprecated `sysmlv2-doc-analyzer.md`, add `kerml-expert.md`, `sysml-expert.md`, `syside-expert.md`, `sysmlv2-validator.md`)

#### 2. Skills Loop
- [x] Replace single-skill block (lines 71–74) with 3-skill loop (add `record-learning`, `toolkit-awareness`)

#### 3. `create_project_structure()` Rewrite
- [x] Replace entire function (lines 107–128) with new directory creation + template copies

#### 4. Delete `create_overview_md()`
- [x] Remove entire function (lines 130–206)

#### 5. `create_source_index()` Path
- [x] Change destination from `$REPO_ROOT/SOURCE_INDEX.md` to `$REPO_ROOT/knowledge/SOURCE_INDEX.md`

#### 6. `print_summary()` Paths
- [x] Update path references (`modeling_pm/OVERVIEW.md` → `project/OVERVIEW.md`, etc.)

### Validation

**Automated:**
```bash
./scripts/replicate_setup.sh
```
- [x] Script runs without error

**Manual comparison with Phase 1 output:**
- [x] `knowledge/`, `project/`, `work/`, `data/` structure matches `cmd_init()` output
- [x] `models/library/`, `models/designs/`, `tests/models/` exist
- [x] `knowledge/SOURCE_INDEX.md` exists (not root)
- [x] All user-owned templates installed to correct paths
- [x] All tool-owned templates installed to correct paths
- [x] `data/traceability_matrix.csv` installed
- [x] `.claude/agents/` has all 5 non-deprecated agents (no `sysmlv2-doc-analyzer.md`)
- [x] `.claude/skills/` has all 3 skills (`python-debugger`, `record-learning`, `toolkit-awareness`)
- [x] NO `modeling_pm/` directory created

**What We Know Works After This Phase:**
Both code paths produce equivalent structures. Component divergence is resolved.

---

## Phase 3: Documentation Updates

### Goal
Update `CLAUDE.md` and `docs/source-index.md` to match the new reality. No stale `modeling_pm/` references remain.

### Changes Required

#### 1. CLAUDE.md
**File:** `CLAUDE.md`

**See `design.md#change-10` for:** exact replacement content for each section.

- [x] Context B description (line 26): `modeling_pm/` → `knowledge/`, `project/`, `work/`, `data/`
- [x] Claude Integration agents list (line 122): update to 5 non-deprecated agents
- [x] Project Templates section (lines 126–134): replace with user-owned/tool-owned/data breakdown
- [x] Directory Clarification table (lines 171–176): replace `modeling_pm/` row with 4 new rows
- [x] Init File Ownership examples (line 197): update file path examples

#### 2. docs/source-index.md
**File:** `docs/source-index.md`

**See `design.md#change-11` for:** which lines need updating and which don't.

- [x] Line 3: add `knowledge/` prefix to file path reference
- [x] Line 59: add `knowledge/` prefix to runtime path reference

### Validation

**Automated:**
```bash
# No stale modeling_pm/ references in updated files
grep -n "modeling_pm" CLAUDE.md docs/source-index.md
```
- [x] Returns no matches

**Manual:**
- [x] Read through updated CLAUDE.md sections — paths are consistent with Phase 1 output
- [x] Read through docs/source-index.md — path references are correct, format examples untouched

**What We Know Works After This Phase:**
Documentation matches code. D1.4 is complete.

---

## Environment Setup

**See CLAUDE.md for full environment rules**

```bash
uv sync                              # Install dependencies
uv run pytest tests/test_cli.py -v   # Run CLI tests
uv run ruff check src/ tests/        # Lint
uv run ruff format src/ tests/       # Format
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Run test suite after changes — failures should be path-assertion only. If any test crashes or fails for non-path reasons, stop and investigate before continuing.
- **Phase 2**: Compare directory trees between `cmd_init()` output and `replicate_setup.sh` output. Any difference is a bug.
- **Phase 3**: Grep for `modeling_pm` across both files. Any remaining reference is a missed update.

---

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-02-01
**Actual Changes:**
- Replaced `USER_OWNED_TEMPLATES` list with 10 entries (new paths + 4 new templates, removed `LOCAL_GUIDE.md.template`)
- Replaced `TOOL_OWNED_TEMPLATES` list with 4 entries (new paths + `EPIC_GUIDE.md.template`, `epic_template.md.template`)
- Replaced `DEV_MODE_GITIGNORE_PATHS` with new paths (added `work/EPIC_GUIDE.md`, `work/backlog/epic_template.md`)
- Replaced `modeling_pm/` directory block with 16-directory loop (4-directory architecture)
- Changed `source_index_path` from `target / "SOURCE_INDEX.md"` to `target / "knowledge" / "SOURCE_INDEX.md"`
- Added `source_index_path.parent.mkdir(parents=True, exist_ok=True)` before copy (knowledge/ dir doesn't exist yet at that point in the function)
- Added CSV installation section after user-owned templates loop
- Updated `cmd_init()` docstring
- Updated next-steps print to reference `knowledge/SOURCE_INDEX.md`
- Replaced CSV header with D1.3-approved schema

**Issues:**
- SOURCE_INDEX.md copy failed on first smoke test because `knowledge/` dir creation happens later in the function. Fixed by adding `parent.mkdir()` before the copy.

**Deviations:**
- Added `source_index_path.parent.mkdir(parents=True, exist_ok=True)` — not in the plan but necessary because directory creation happens after SOURCE_INDEX.md copy in the function flow.

**Validation:**
- 61 passed, 9 failed (all path-assertion failures as expected)
- Smoke test: all 4 top-level dirs, all subdirs, all files present, CSV header correct, no `modeling_pm/`
- Dev mode: symlinks correct for all tool-owned templates, gitignore has new paths
- Idempotency: second run succeeds, skips user-owned files

### Phase 2 Completion
**Completed:** 2026-02-01
**Actual Changes:**
- Replaced agent loop: 5 non-deprecated agents (removed `sysmlv2-doc-analyzer.md`)
- Replaced skill loop: 3 skills (added `record-learning`, `toolkit-awareness`)
- Rewrote `create_project_structure()`: new 4-directory structure + all template copies + CSV
- Deleted `create_overview_md()` function entirely
- Updated `create_source_index()` to copy to `knowledge/SOURCE_INDEX.md`
- Updated `print_summary()` with new paths
- Updated script header comment

**Issues:** None
**Deviations:** None

**Validation:**
- Script runs without error
- All directories and files match Phase 1 output
- 5 agents installed (no deprecated agent)
- 3 skills installed

### Phase 3 Completion
**Completed:** 2026-02-01
**Actual Changes:**
- CLAUDE.md: Updated Context B description, agents list, project templates section, directory clarification table, init file ownership examples
- docs/source-index.md: Updated line 3 and line 59 with `knowledge/` prefix

**Issues:** None
**Deviations:** None

**Validation:**
- `grep -n "modeling_pm"` returns no matches in CLAUDE.md or docs/source-index.md
- `grep -n "modeling_pm"` returns no matches in cli/__init__.py or replicate_setup.sh

---

**Status**: Complete
