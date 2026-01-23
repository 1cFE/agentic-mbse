# Implementation Plan: SysIDE v0.8.4 Upgrade

**Status:** Complete
**Created:** 2026-01-16
**Last Updated:** 2026-01-16

## Source Documents
- **Spec:** `.project/active/syside-084-upgrade/spec.md`
- **Design:** N/A (LOW complexity - no design phase needed)

## Implementation Strategy

**Phasing Rationale:**
Phase 1 tackles CLI and Python package together as quick wins that validate v0.8.4 compatibility before investing time in documentation work. Phase 2 safely reorganizes existing docs. Phase 3 handles the longest task (scraping) last, after all foundations are in place.

**Overall Validation Approach:**
- Phase 1: Automated tests verify no API breakage
- Phase 2: Manual verification of file moves
- Phase 3: Symlink verification + agent path testing

---

## Phase 1: CLI + Python Package Update

### Goal
Install syside CLI v0.8.4 and update Python package to verify compatibility with existing codebase before investing in documentation work.

### Changes Required

#### 1. Install CLI from tarball
```bash
# Extract to ~/.local (tarball contains bin/ structure)
tar -xf ~/syside-0.8.4-x86_64-linux-glibc.tar.xz -C ~/.local/

# Verify
syside --version
# Expected: 0.8.4 (...)
```

#### 2. Update pyproject.toml
**File:** `pyproject.toml:25`
- [x] Change `"syside>=0.8.1"` to `"syside>=0.8.4"`

#### 3. Sync dependencies
```bash
uv sync
```

#### 4. Verify Python package
```bash
uv run python -c "import syside; print(syside.__version__)"
# Expected: 0.8.4
```

### Validation

**Automated:**
- [x] `syside --version` → Reports `0.8.4`
- [x] `uv run python -c "import syside; print(syside.__version__)"` → Reports `0.8.4`
- [x] `uv run pytest tests/` → All tests pass (283 passed, 1 skipped)
- [x] `uv run ruff check src/` → No errors (tests have pre-existing lint issues)

**Manual:**
- [ ] Quick smoke test: `uv run agentic-mbse validate models/` (if models exist)

**What We Know Works After This Phase:**
- syside v0.8.4 CLI is functional
- syside v0.8.4 Python package works with our codebase
- No API breakage in existing code

---

## Phase 2: Documentation Reorganization

### Goal
Move existing v0.8.1 documentation into versioned directory structure, preserving all content.

### Changes Required

#### 1. Create versioned directory and move docs
```bash
cd /home/reid/1cfe/agentic-mbse/docs/syside

# Create v0.8.1 directory
mkdir -p v0.8.1

# Move existing directories into v0.8.1
mv api v0.8.1/
mv examples v0.8.1/
mv automator v0.8.1/
```

#### 2. Verify move
```bash
# Check structure
ls -la docs/syside/
ls -la docs/syside/v0.8.1/

# Verify key file exists
cat docs/syside/v0.8.1/api/README.md | head -5
```

### Validation

**Manual:**
- [x] `docs/syside/v0.8.1/api/README.md` exists
- [x] `docs/syside/v0.8.1/examples/` exists
- [x] `docs/syside/v0.8.1/automator/` exists
- [x] No docs remain at old locations (`docs/syside/api/` etc.)

**What We Know Works After This Phase:**
- Existing v0.8.1 docs preserved in versioned directory
- Directory structure ready for v0.8.4 docs and symlinks

---

## Phase 3: Documentation Extraction + Symlinks

### Goal
Scrape v0.8.4 documentation, create compatibility symlinks, and add version tracking.

### Changes Required

#### 1. Prepare scraper
The m-scout scraper needs temporary modification to target our output directory.

**File:** `~/m-scout/tools/syside_docs/scrape_docs.py`
- [ ] Temporarily change `OUTDIR` to: `pathlib.Path("/home/reid/1cfe/agentic-mbse/docs/syside")`
- [ ] Note: Scraper auto-detects version and creates `v0.8.4/` subdirectory

#### 2. Run scraper
```bash
# Activate m-scout environment (has pypandoc)
source ~/m-scout/pdf_env/bin/activate

# Verify dependencies
python -c "import pypandoc; print('pypandoc OK')"
which pandoc

# Run scraper
cd ~/m-scout
python tools/syside_docs/scrape_docs.py

# Deactivate when done
deactivate
```

#### 3. Create compatibility symlinks
```bash
cd /home/reid/1cfe/agentic-mbse/docs/syside

# Create symlinks pointing to v0.8.4
ln -s v0.8.4/api api
ln -s v0.8.4/examples examples
ln -s v0.8.4/automator automator

# Verify symlinks
ls -la
```

#### 4. Create VERSION.md
**File:** `docs/syside/VERSION.md` (NEW)
- [ ] Create version tracking document

```markdown
# Syside Documentation

**Current Version:** v0.8.4
**Last Updated:** 2026-01-16

## Available Versions

| Version | Directory | Status |
|---------|-----------|--------|
| v0.8.4 | `v0.8.4/` | Current (symlinked from `api/`, `examples/`, `automator/`) |
| v0.8.1 | `v0.8.1/` | Archived |

## Updating Documentation

To update to a new syside version:

1. Run the scraper from m-scout:
   ```bash
   source ~/m-scout/pdf_env/bin/activate
   # Edit OUTDIR in scrape_docs.py if needed
   python ~/m-scout/tools/syside_docs/scrape_docs.py
   deactivate
   ```

2. Update symlinks:
   ```bash
   cd docs/syside
   rm api examples automator
   ln -s v0.X.Y/api api
   ln -s v0.X.Y/examples examples
   ln -s v0.X.Y/automator automator
   ```

3. Update this VERSION.md file.

## Source

Documentation scraped from: https://docs.sensmetry.com/python/latest/
```

#### 5. Restore scraper (cleanup)
**File:** `~/m-scout/tools/syside_docs/scrape_docs.py`
- [ ] Restore original `OUTDIR` value: `pathlib.Path("/home/reidw/m-scout/Literature/syside-docs")`

### Validation

**Automated:**
- [x] `uv run pytest tests/` → Still passes (283 passed, 1 skipped)

**Manual:**
- [x] `docs/syside/python/v0.8.4/README.md` exists (new scraped content)
- [x] `docs/syside/api/README.md` → symlink to `python/v0.8.4/README.md`
- [x] `docs/syside/api/generated/` → symlink to `python/v0.8.4/syside/`
- [x] `docs/syside/examples/` exists (scraped directly, not symlink)
- [x] `docs/syside/automator/` exists (scraped directly, not symlink)
- [x] `docs/syside/VERSION.md` exists
- [x] Agent paths work: `api/README.md`, `api/generated/`, `automator/advanced.md`, `examples/`

**What We Know Works After This Phase:**
- v0.8.4 documentation extracted and available
- Symlinks provide backwards compatibility for agents
- Version tracking in place for future updates

---

## Final Validation (All Phases Complete)

### Success Criteria from Spec
- [x] `syside --version` reports v0.8.4
- [x] `uv run python -c "import syside; print(syside.__version__)"` reports v0.8.4
- [x] v0.8.4 documentation available at `docs/syside/python/v0.8.4/` (348 markdown files)
- [x] Existing v0.8.1 documentation preserved at `docs/syside/v0.8.1/`
- [x] All existing tests pass with updated syside (283 passed, 1 skipped)
- [x] Symlinks work for agent compatibility (`api/` → `python/v0.8.4/`)

---

## Risk Management

| Risk | Mitigation |
|------|------------|
| Python package API changes | Run full test suite in Phase 1 before proceeding |
| Scraper dependencies missing | Verify pypandoc/Pandoc in m-scout env before running |
| Symlinks not working in git | Verify symlinks are relative, test after creation |
| Scraper output structure different | Check first few files before full run |

---

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-01-16 ~18:05 UTC
**Actual Changes:**
- Extracted `~/syside-0.8.4-x86_64-linux-glibc.tar.xz` to `~/.local/` (CLI now v0.8.4)
- Modified `pyproject.toml:25` from `"syside>=0.8.1"` to `"syside>=0.8.4"`
- Ran `uv sync --extra dev` to install updated package and dev dependencies
- Python package upgraded from 0.8.3 → 0.8.4

**Issues:**
- Initial `uv sync` didn't install dev deps; needed `uv sync --extra dev` to get pytest/ruff

**Deviations:**
- None. Plan executed as written.

**Test Results:**
- 283 passed, 1 skipped in 14.51s
- Source code (`src/`) passes ruff check
- Pre-existing lint issues in `tests/` (40 errors, unrelated to upgrade)

### Phase 2 Completion
**Completed:** 2026-01-16 ~18:07 UTC
**Actual Changes:**
- Created `docs/syside/v0.8.1/` directory
- Moved `api/`, `examples/`, `automator/` into `v0.8.1/`
- Verified `v0.8.1/api/README.md` exists with content

**Issues:**
- None

**Deviations:**
- None. Plan executed as written.

### Phase 3 Completion
**Completed:** 2026-01-16 ~18:35 UTC
**Actual Changes:**
- Scraper was updated (separately) to handle new docs.sensmetry.com structure
- Scraper ran and extracted 348 markdown files to `docs/syside/python/v0.8.4/`
- Created `docs/syside/api/` directory with compatibility symlinks:
  - `api/README.md` → `python/v0.8.4/README.md`
  - `api/generated/` → `python/v0.8.4/syside/`
- `automator/` and `examples/` scraped directly at root (no symlinks needed)
- Created `docs/syside/VERSION.md` documenting structure
- Restored scraper OUTDIR to original value

**Issues:**
- Initial scraper run failed (404s) due to changed docs site structure
- Scraper was updated in separate session to handle new URL patterns
- New structure puts Python API at `/python/v0.8.4/` instead of `/v0.8.4/api/`

**Deviations:**
- Docs structure different than originally planned (see VERSION.md for actual structure)
- Created `api/` as directory with internal symlinks (not direct symlink to v0.8.4/api)

---

**Status**: Draft → In Progress → Complete
