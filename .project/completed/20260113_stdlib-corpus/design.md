# Design: Standard Library Corpus Sync

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-01-13
**Branch:** 1cfe_dev
**Complexity:** LOW

---

## Overview

A Python script to synchronize the SysML v2 standard library source files from the syside package to a git-tracked location at `docs/sysmlv2/stdlib/`, with an AI-generated INDEX.md for agent navigation.

## Related Artifacts

- **Spec:** `.project/active/stdlib-corpus/spec.md`
- **Epic:** `.project/backlog/epic_documentation-discoverability.md` (P1-3)
- **Depends on:** `kerml-expert` agent (needs searchable corpus)

---

## Research Findings

### Existing Patterns

**`scripts/generate_index.py`** (316 lines):
- Pattern for calling `claude -p` to generate summaries (`generate_summary()` at line 155)
- Uses `subprocess.run()` with timeout, error handling
- YAML frontmatter format for INDEX.md
- Checksum-based incremental updates (skip if unchanged)
- Argparse with `--force`, `--dry-run` flags

**syside Package Location**:
```python
import syside
from pathlib import Path
syside_path = Path(syside.__file__).parent / "sysml.library"
# → /home/reid/1cfe/agentic-mbse/.venv/lib/python3.12/site-packages/syside/sysml.library
```

**Library Structure (94 files)**:
```
sysml.library/
├── Kernel Libraries/
│   ├── Kernel Data Type Library/      (3 files: Collections, ScalarValues, VectorValues)
│   ├── Kernel Function Library/       (17 files: NumericalFunctions, SequenceFunctions, etc.)
│   └── Kernel Semantic Library/       (16 files: Base, Occurrences, Performances, etc.)
├── Systems Library/                   (21 files: Parts, Ports, Actions, States, etc.)
└── Domain Libraries/
    ├── Analysis/                      (4 files)
    ├── Cause and Effect/              (2 files)
    ├── Geometry/                      (2 files)
    ├── Metadata/                      (4 files)
    ├── Quantities and Units/          (23 files: SI, ISQ, ISQMechanics, etc.)
    └── Requirement Derivation/        (2 files)
```

**File Format** (from `NumericalFunctions.kerml` and `SI.sysml`):
- Files have `doc /* ... */` comment at top for description
- Package name matches filename
- Functions/types are clearly defined with signatures

**kerml-expert Agent** (`claude/agents/kerml-expert.md`):
- Uses `{SYSML_DOCS_PATH}` placeholder for docs path
- Expects INDEX.md with YAML frontmatter
- Uses grep + targeted Read with offset/limit

---

## Proposed Design

### High-Level Architecture

```
sync_stdlib.py
     │
     ├── 1. Locate syside package
     │       └── syside.__file__ → sysml.library/
     │
     ├── 2. Copy files to docs/sysmlv2/stdlib/
     │       └── Preserve directory structure (shutil.copytree)
     │
     ├── 3. Generate INDEX.md
     │       ├── Quick Reference (hardcoded curated section)
     │       └── File Index (AI-generated 1-line summaries)
     │
     └── 4. Generate VERSION.md
             └── syside version, timestamp, file count
```

### Component Details

#### 1. Script: `scripts/sync_stdlib.py`

**Location:** `scripts/sync_stdlib.py`

**Dependencies:**
- Python 3.12+ (standard library: pathlib, shutil, subprocess, argparse)
- syside package (runtime dependency for locating library)
- `claude` CLI (for generating summaries)

**Key Functions:**

```python
def get_syside_library_path() -> Path:
    """Locate syside sysml.library directory."""
    import syside
    return Path(syside.__file__).parent / "sysml.library"

def get_syside_version() -> str:
    """Get installed syside version."""
    from importlib.metadata import version
    return version("syside")

def copy_library_files(src: Path, dst: Path, dry_run: bool = False) -> list[Path]:
    """
    Copy .kerml and .sysml files preserving directory structure.
    Returns list of copied files.
    Handles spaces in directory names correctly (pathlib handles this).
    """

def generate_file_summary(file_path: Path) -> str:
    """
    Call claude -p to generate 1-line summary.
    Reads first ~2000 chars of file, asks for <100 char summary.
    Pattern from generate_index.py:155-187.
    """

def generate_index_md(files: list[Path], syside_version: str) -> str:
    """
    Generate INDEX.md content with:
    - YAML frontmatter (version, timestamp, file count)
    - Quick Reference section (hardcoded from spec)
    - File Index by directory with AI summaries
    """

def generate_version_md(syside_version: str, file_count: int) -> str:
    """Generate VERSION.md with metadata."""

def main():
    """
    CLI entry point with argparse.
    --dry-run: Show what would be done
    --force: Overwrite existing files
    --help: Show usage
    """
```

**CLI Interface:**
```bash
python scripts/sync_stdlib.py [OPTIONS]

Options:
  --dry-run   Preview without copying or generating
  --force     Overwrite existing stdlib directory
  --help      Show help message

Output:
  docs/sysmlv2/stdlib/          # All .kerml and .sysml files
  docs/sysmlv2/stdlib/INDEX.md  # Navigation index
  docs/sysmlv2/stdlib/VERSION.md # Version tracking
```

#### 2. INDEX.md Structure

Per the spec (FR-11 through FR-16), the INDEX.md will be ~200 lines with:

**YAML Frontmatter:**
```yaml
---
syside_version: "0.8.3"
generated: "2026-01-13T12:00:00Z"
total_files: 94
---
```

**Quick Reference Section (hardcoded):**
- Curated from spec lines 239-283
- Common Functions table (~25 rows)
- Core Types table (~6 rows)
- Common SI Units table (~11 rows)

**File Index Section (AI-generated):**
- Organized by directory hierarchy
- Each directory gets a subsection header
- Each file gets: `| filename | 1-line AI summary |`
- Total ~94 rows across ~12 directory subsections

#### 3. VERSION.md Structure

```markdown
# Standard Library Version

| Field | Value |
|-------|-------|
| syside version | 0.8.3 |
| Python version | 3.12 |
| Sync timestamp | 2026-01-13T12:00:00Z |
| Files synced | 94 |
| Source | .venv/.../syside/sysml.library/ |

To re-sync after upgrading syside:
\`\`\`bash
python scripts/sync_stdlib.py --force
\`\`\`
```

#### 4. Integration with kerml-expert

The `kerml-expert` agent already uses `{SYSML_DOCS_PATH}` placeholder.

**No changes needed** - after sync, the agent can search:
```
{SYSML_DOCS_PATH}/stdlib/
├── INDEX.md              # Agent reads for navigation
├── Kernel Libraries/...  # Agent greps for function names
└── ...
```

---

## Implementation Notes

### File Copying Strategy

Use `shutil.copytree()` with a custom `copy_function`:
- Only copy files matching `*.kerml` or `*.sysml`
- Preserves directory structure
- Directory names with spaces work correctly (pathlib handles quoting)

```python
def copy_library(src: Path, dst: Path) -> list[Path]:
    copied = []

    for src_file in src.rglob("*"):
        if src_file.suffix in (".kerml", ".sysml"):
            rel_path = src_file.relative_to(src)
            dst_file = dst / rel_path
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
            copied.append(dst_file)

    return sorted(copied)
```

### AI Summary Generation

Pattern from `scripts/generate_index.py:155-187`:

```python
def generate_file_summary(file_path: Path) -> str:
    content = file_path.read_text()[:2000]  # Truncate for context
    prompt = f"""Summarize this SysML/KerML library file in ONE line (max 100 chars).
Focus on what functions, types, or definitions it provides.

File: {file_path.name}
Content:
{content}"""

    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=60
    )
    if result.returncode != 0:
        return "[Summary generation failed]"
    return result.stdout.strip()
```

### Error Handling

| Error Case | Handling |
|------------|----------|
| syside not installed | `ImportError` → exit with clear message |
| claude not found | `FileNotFoundError` → exit with message |
| Summary timeout | Return "[Summary generation timed out]" |
| Existing stdlib dir | Skip unless `--force` |

### Dry-Run Mode

In `--dry-run` mode:
1. Print syside version and path found
2. List all files that would be copied
3. Print file count and estimated INDEX.md generation time
4. Exit without modifying anything

---

## Potential Risks

| Risk | Mitigation |
|------|------------|
| syside upgrade changes file structure | VERSION.md tracks version; re-sync is easy |
| AI summaries are low quality | Can regenerate with `--force`; Quick Reference is curated |
| Large file count (94) slows summarization | Estimate ~2-3 min for all summaries; `--dry-run` to preview |
| Directory names with spaces | pathlib handles correctly; test in acceptance criteria |

---

## Validation Approach

### Testing Strategy

1. **Manual verification** (primary - low complexity script):
   - Run `python scripts/sync_stdlib.py --dry-run`
   - Verify file count matches 94
   - Run actual sync
   - Grep for known functions

2. **Acceptance test commands:**
   ```bash
   # Verify file copy
   find docs/sysmlv2/stdlib -name "*.kerml" -o -name "*.sysml" | wc -l
   # Should output: 94

   # Verify function searchability
   grep -r "function sum" docs/sysmlv2/stdlib/
   # Should find NumericalFunctions.kerml

   # Verify unit searchability
   grep -r "attribute.*metre" docs/sysmlv2/stdlib/
   # Should find SI.sysml
   ```

3. **INDEX.md validation:**
   - Check YAML frontmatter parses correctly
   - Verify ~200 lines (not 2000+)
   - Verify all 94 files listed

---

## Integration Strategy

**How it fits into workflows:**
- This is a **one-time setup script** + occasional re-sync
- Run manually after syside upgrade
- Committed to git for version tracking
- Used by `kerml-expert` agent for searching

**What it replaces:**
- P1-3 in epic: "Add Kernel Library Files to Searchable Corpus"
- The spec expanded this from just Kernel Libraries to all libraries

---

## Implementation Notes

**Implemented:** 2026-01-13

**Files created:**
- `scripts/sync_stdlib.py` - Main sync script
- `docs/sysmlv2/stdlib/` - 94 library files synced
- `docs/sysmlv2/stdlib/INDEX.md` - Navigation index (220 lines)
- `docs/sysmlv2/stdlib/VERSION.md` - Version tracking

All acceptance criteria verified.

---
