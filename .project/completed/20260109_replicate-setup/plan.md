# Implementation Plan: Replicate Setup Script

**Status:** Draft
**Created:** 2026-01-09
**Last Updated:** 2026-01-09

## Source Documents
- **Spec:** `.project/active/replicate-setup/spec.md`
- **Design:** `.project/active/replicate-setup/design.md` - See here for component details, script structure, function implementations

## Implementation Strategy

**Phasing Rationale:**
1. **Phase 1 (Placeholder Migration)** - De-risk first by updating the placeholder format across existing code. This affects external users via `init`, so we validate thoroughly before proceeding.
2. **Phase 2 (Script Creation)** - With placeholder format settled, create the new script using the same substitution technique.
3. **Phase 3 (Documentation)** - Polish and document after core functionality is proven.

**Overall Validation Approach:**
- Each phase starts with tests (where applicable)
- Each phase has automated + manual validation
- Continuous verification ensures no regressions

---

## Phase 1: Placeholder Migration

### Goal
Update placeholder format from `agent_literature/...` to `{SYSML_DOCS_PATH}` and `{SYSIDE_DOCS_PATH}`. This de-risks by ensuring existing `init` command continues to work.

### Test Stencil (Update First)
```python
# tests/test_cli.py - Update existing assertions
# Find the test that checks agent path substitution

def test_init_substitutes_agent_paths(tmp_path):
    # ... existing setup ...

    # Verify placeholders are substituted (not present in output)
    agent_content = (tmp_path / ".claude/agents/sysmlv2-doc-analyzer.md").read_text()
    assert "{SYSML_DOCS_PATH}" not in agent_content  # Changed from agent_literature/SysML/
    assert "{SYSIDE_DOCS_PATH}" not in agent_content  # Changed from agent_literature/syside-docs/

    # Verify absolute paths ARE present
    assert "/docs/sysmlv2" in agent_content
    assert "/docs/syside" in agent_content
```

### Changes Required

**See `design.md#required-code-changes` for full details**

#### 1. Update Test File (First)
**File:** `tests/test_cli.py:168-169`
- [ ] Change `"agent_literature/SysML/"` to `"{SYSML_DOCS_PATH}"`
- [ ] Change `"agent_literature/syside-docs/"` to `"{SYSIDE_DOCS_PATH}"`

#### 2. Update Agent Source File
**File:** `claude/agents/sysmlv2-doc-analyzer.md`
- [ ] Replace all `agent_literature/SysML/` with `{SYSML_DOCS_PATH}/`
- [ ] Replace all `agent_literature/syside-docs/v0.8.1/` with `{SYSIDE_DOCS_PATH}/`
- [ ] Verify grep/read examples use new placeholders

#### 3. Update CLI Init Function
**File:** `src/agentic_mbse/cli/__init__.py:327-332`
- [ ] Change first replace: `"{SYSML_DOCS_PATH}"` → `f"{docs_path}/sysmlv2"`
- [ ] Change second replace: `"{SYSIDE_DOCS_PATH}"` → `f"{docs_path}/syside"`

### Validation

**Automated:**
- [ ] `pytest tests/test_cli.py -v` → All pass
- [ ] `pytest tests/` → Full suite passes (no regressions)
- [ ] `ruff check src/ tests/` → No lint errors

**Manual:**
- [ ] `agentic-mbse init /tmp/test-init --force` → Completes without error
- [ ] Check `/tmp/test-init/.claude/agents/sysmlv2-doc-analyzer.md` → Contains absolute paths, no placeholders

**What We Know Works After This Phase:**
- Placeholder format is updated consistently across codebase
- `init` command still works for external users
- Test coverage validates the substitution

---

## Phase 2: Create replicate_setup.sh Script

### Goal
Create the main setup script that replicates `init` behavior for this repo without CLI dependency.

### Test Stencil (Manual Validation)
```bash
# Manual test script - run after creating replicate_setup.sh
cd /home/reid/1cfe/agentic-mbse

# Clean slate
rm -rf .claude/ project/ models/library/ SOURCE_INDEX.md

# Run script
./scripts/replicate_setup.sh

# Verify outputs
test -f .claude/commands/design-model.md && echo "PASS: commands installed"
test -f .claude/agents/sysmlv2-doc-analyzer.md && echo "PASS: agents installed"
grep -q "{SYSML_DOCS_PATH}" .claude/agents/sysmlv2-doc-analyzer.md && echo "FAIL: placeholder not substituted" || echo "PASS: placeholders substituted"
test -f .claude/settings.json && echo "PASS: settings.json created"
test -f project/OVERVIEW.md && echo "PASS: project structure created"
test -f SOURCE_INDEX.md && echo "PASS: SOURCE_INDEX.md created"
test -d models/library && echo "PASS: models/library created"

# Verify idempotent
./scripts/replicate_setup.sh && echo "PASS: idempotent re-run"
```

### Changes Required

**See `design.md#proposed-design` for full script structure and function implementations**

#### 1. Create Script File
**File:** `scripts/replicate_setup.sh` (NEW)
- [ ] Create file with shebang and `set -euo pipefail`
- [ ] Add `SCRIPT_DIR`, `REPO_ROOT`, `DOCS_PATH` variables
- [ ] Add color output helpers (`log_created`, `log_skipped`)
- [ ] Implement `check_prerequisites()` per `design.md#1-prerequisites-check`
- [ ] Implement `install_claude_components()` per `design.md#2-install-claude-components`
- [ ] Implement `create_settings_json()` per `design.md#3-create-claudesettingsjson`
- [ ] Implement `create_project_structure()` and `create_overview_md()` per `design.md#4-create-project-structure`
- [ ] Implement `create_source_index()` per `design.md#5-create-source_indexmd`
- [ ] Implement `print_summary()` per `design.md#6-print-summary`
- [ ] Add `main` function calling all steps
- [ ] Make executable: `chmod +x scripts/replicate_setup.sh`

### Validation

**Automated:**
- [ ] `./scripts/replicate_setup.sh` → Completes without error
- [ ] `pytest tests/` → Existing tests still pass

**Manual:**
- [ ] Verify `.claude/commands/` contains all 9 commands
- [ ] Verify `.claude/agents/sysmlv2-doc-analyzer.md` has absolute paths (no `{SYSML_DOCS_PATH}`)
- [ ] Verify `.claude/settings.json` has `~/...` format permissions
- [ ] Verify `project/OVERVIEW.md` describes coffee maker
- [ ] Verify `SOURCE_INDEX.md` matches template
- [ ] Re-run script → No errors, files updated
- [ ] Start new Claude Code session → `/design-model` command available

**What We Know Works After This Phase:**
- Script installs all Claude components correctly
- Placeholder substitution works identically to `init`
- Project structure created for dogfooding
- Script is idempotent

---

## Phase 3: Documentation & Cleanup

### Goal
Update documentation and gitignore to complete the feature.

### Changes Required

**See `design.md#claudemd-updates` for content to add**

#### 1. Update CLAUDE.md
**File:** `CLAUDE.md`
- [ ] Add "Directory Clarification" section after "Testing Structure"
- [ ] Add "Change Coordination" section with table

#### 2. Update .gitignore
**File:** `.gitignore`
- [ ] Add `project/` (generated by replicate_setup.sh)
- [ ] Add `models/library/` (generated by replicate_setup.sh)
- [ ] Add `SOURCE_INDEX.md` (generated by replicate_setup.sh)

### Validation

**Automated:**
- [ ] `pytest tests/` → All pass
- [ ] `git status` → Only expected files modified

**Manual:**
- [ ] Read CLAUDE.md → Directory clarification is clear
- [ ] Read CLAUDE.md → Change coordination documented
- [ ] `git status` after running script → Generated files not shown (gitignored)

**What We Know Works After This Phase:**
- Documentation explains the setup
- Generated files don't clutter git status
- All acceptance criteria from spec met

---

## Environment Setup

**See CLAUDE.md for full environment rules**

Key commands:
```bash
# Run tests
pytest tests/

# Run specific test
pytest tests/test_cli.py -v

# Lint
ruff check src/ tests/

# Install in dev mode (if needed)
pip install -e ".[dev]"
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Run full test suite after changes; manual verification of `init` output
- **Phase 2**: Clean slate test (remove `.claude/` etc.) before validating script
- **Phase 3**: Verify gitignore patterns work before committing

---

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-01-09 23:12 UTC
**Actual Changes:**
- Modified `tests/test_cli.py:167-169` - Updated assertions to check for `{SYSML_DOCS_PATH}` and `{SYSIDE_DOCS_PATH}` placeholders
- Modified `claude/agents/sysmlv2-doc-analyzer.md` - Replaced all `agent_literature/SysML/` with `{SYSML_DOCS_PATH}/` and `agent_literature/syside-docs/v0.8.1/` with `{SYSIDE_DOCS_PATH}/`
- Modified `src/agentic_mbse/cli/__init__.py:327-330` - Updated substitution logic to use new placeholders

**Issues:** None
**Deviations:** None - followed plan exactly

### Phase 2 Completion
**Completed:** 2026-01-09 23:12 UTC
**Actual Changes:**
- Created `scripts/replicate_setup.sh` (~210 lines) with all functions as designed
- Made script executable

**Validation Results:**
- All 9 commands installed to `.claude/commands/`
- Agent files have absolute paths (no placeholders remaining)
- `.claude/settings.json` has `~/...` format permissions
- `project/OVERVIEW.md` contains coffee maker test subject
- `SOURCE_INDEX.md` copied from template
- Script is idempotent (re-runs without errors)

**Issues:** None
**Deviations:** None - followed design exactly

### Phase 3 Completion
**Completed:** 2026-01-09 23:12 UTC
**Actual Changes:**
- Modified `CLAUDE.md` - Added "Directory Clarification" and "Change Coordination" sections after "Testing Structure"
- Modified `.gitignore` - Added `project/`, `models/library/`, `SOURCE_INDEX.md` under new comment section

**Validation Results:**
- All 269 tests pass (1 skipped)
- Generated files (`project/`, `models/library/`, `SOURCE_INDEX.md`) correctly gitignored
- `.claude/` directory created (expected - for local Claude component installation)

**Issues:** None
**Deviations:** None - followed plan exactly

---

**Status**: Complete
