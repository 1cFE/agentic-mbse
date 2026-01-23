# Spec: SysIDE v0.8.4 Upgrade

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-01-16 17:53 UTC
**Complexity:** LOW
**Branch:** 1cfe_dev

---

## Business Goals

### Why This Matters
Keep all syside tooling (CLI, Python package, documentation) synchronized at v0.8.4 to benefit from new features, bug fixes, and API improvements. Version consistency prevents compatibility issues between the CLI validation tool and the Python automation package.

### Success Criteria
- [x] `syside --version` reports v0.8.4
- [x] `uv run python -c "import syside; print(syside.__version__)"` reports v0.8.4
- [x] v0.8.4 documentation available at `docs/syside/python/v0.8.4/` (348 files)
- [x] Existing v0.8.1 documentation preserved at `docs/syside/v0.8.1/`
- [x] All existing tests pass with updated syside (283 passed, 1 skipped)

### Priority
Maintenance task - keeps development environment current.

---

## Problem Statement

### Current State
- **CLI**: v0.8.1 installed at `~/.local/bin/syside`
- **Python package**: `syside>=0.8.1` specified in `pyproject.toml`
- **Documentation**: v0.8.1 docs at `docs/syside/{api,examples,automator}/` (unversioned)

### Desired Outcome
- **CLI**: v0.8.4 installed and functional
- **Python package**: v0.8.4 installed via uv
- **Documentation**: Versioned directories with both v0.8.1 (preserved) and v0.8.4 (new)

---

## Scope

### In Scope
1. **CLI Installation** (Task A)
   - Extract `~/syside-0.8.4-x86_64-linux-glibc.tar.xz` to `~/.local/`
   - Verify installation with `syside --version`

2. **Python Package Update** (Task B)
   - Update `pyproject.toml` dependency from `syside>=0.8.1` to `syside>=0.8.4`
   - Run `uv sync` to update lock file and install

3. **Documentation Extraction** (Task C)
   - Reorganize existing v0.8.1 docs into versioned directory structure
   - Scrape v0.8.4 docs using `~/m-scout/tools/syside_docs/scrape_docs.py`
   - Update any code/agent references to point to versioned paths

### Out of Scope
- Updating SysML v2 specification documentation (only syside/Python docs)
- Migrating existing code that might use deprecated APIs (flag for manual review)
- Updating the syside standard library corpus (`docs/sysmlv2/stdlib/`)

### Edge Cases & Considerations
- The scraper requires `pypandoc` and system Pandoc binary
- m-scout virtual environment (`~/m-scout/pdf_env`) may have the dependencies
- Scraper output directory needs to be configured for agentic-mbse target

---

## Requirements

### Functional Requirements

1. **FR-1**: Install syside CLI v0.8.4 from provided tarball to `~/.local/bin/`
2. **FR-2**: Update `pyproject.toml` to require `syside>=0.8.4`
3. **FR-3**: Run `uv sync` to install updated Python package
4. **FR-4**: Move existing docs from `docs/syside/{api,examples,automator}/` to `docs/syside/v0.8.1/`
5. **FR-5**: Run modified scraper to extract v0.8.4 docs to `docs/syside/v0.8.4/`
6. **FR-6**: Update agent/command references from `docs/syside/api/` to `docs/syside/v0.8.4/api/`
7. **FR-7**: [INFERRED] Create `docs/syside/VERSION.md` documenting current version and update process

### Non-Functional Requirements

- Documentation scraping should complete within reasonable time (< 30 min)
- Preserve all existing documentation (no data loss)

---

## Acceptance Criteria

### Core Functionality
- [x] CLI: `syside --version` outputs `0.8.4 (...)`
- [x] Python: `import syside` works and reports v0.8.4
- [x] Docs: `docs/syside/v0.8.1/api/README.md` exists (preserved)
- [x] Docs: `docs/syside/python/v0.8.4/README.md` exists (new - structure changed)
- [x] Tests: `uv run pytest tests/` passes (283 passed, 1 skipped)

### Quality & Integration
- [x] Existing tests continue to pass
- [x] No broken references in agents/commands to old doc paths (symlinks provide compatibility)

---

## Implementation Notes

### CLI Installation Steps
```bash
# Extract to ~/.local (preserves bin/, etc. structure)
tar -xf ~/syside-0.8.4-x86_64-linux-glibc.tar.xz -C ~/.local/

# Verify
syside --version
```

### Scraper Configuration Changes
The m-scout scraper (`~/m-scout/tools/syside_docs/scrape_docs.py`) needs:
1. `OUTDIR` changed to target `docs/syside/` in agentic-mbse
2. Version auto-detection will resolve to v0.8.4
3. Run from m-scout's pdf_env which has pypandoc

### Directory Structure After
```
docs/syside/
├── VERSION.md              # NEW: version tracking
├── v0.8.1/                 # MOVED from api/, examples/, automator/
│   ├── api/
│   ├── examples/
│   └── automator/
└── v0.8.4/                 # NEW: scraped
    ├── api/
    ├── examples/
    └── automator/
```

### Path Compatibility Strategy

The `{SYSIDE_DOCS_PATH}` placeholder is substituted with `{docs_path}/syside` during init.
Current agents expect paths like `{SYSIDE_DOCS_PATH}/api/README.md`.

**Option A (Chosen):** Create symlinks for backwards compatibility
```
docs/syside/
├── api/ → v0.8.4/api/          # symlink for compat
├── automator/ → v0.8.4/automator/
├── examples/ → v0.8.4/examples/
├── v0.8.1/                     # archived version
└── v0.8.4/                     # current version
```
This avoids updating all agent references.

**Option B:** Update agent paths to include version
Would require updating `syside-expert.md` and `sysmlv2-doc-analyzer.md` (deprecated).

### Files Potentially Needing Updates (if not using symlinks)
- `claude/agents/syside-expert.md` - references `{SYSIDE_DOCS_PATH}/api/`
- `claude/agents/deprecated/sysmlv2-doc-analyzer.md` - references `{SYSIDE_DOCS_PATH}/api/`

---

## Related Artifacts

- **Research:** N/A
- **Design:** `.project/active/syside-084-upgrade/design.md` (to be created if needed)
- **Tools:** `~/m-scout/tools/syside_docs/scrape_docs.py`
- **Source:** `~/syside-0.8.4-x86_64-linux-glibc.tar.xz`

---

**Next Steps:** After approval, proceed directly to implementation (complexity is LOW, no design phase needed)
