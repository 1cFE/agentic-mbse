# Spec: Standard Library Corpus Sync

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-01-13
**Complexity:** LOW
**Epic:** `.project/backlog/epic_documentation-discoverability.md` (P1-3)

---

## Business Goals

### Why This Matters

The `kerml-expert` agent needs to search the SysML v2 standard library source files (`.kerml`, `.sysml`) to answer questions about:
- Available functions (`sum`, `size`, `collect`, etc.)
- Type definitions (`Real`, `Integer`, `LengthValue`, etc.)
- Unit definitions (`m`, `kg`, `W`, `K`, etc.)
- Base constructs (`Part`, `Port`, `Attribute`, etc.)

Currently these files live in the syside package (`.venv/.../syside/sysml.library/`) which:
1. Is not version-controlled with our project
2. May change when syside is upgraded
3. Is buried in a path agents may not search

### Success Criteria

- [ ] Agent can grep for `sum` and find `NumericalFunctions.kerml`
- [ ] Agent can grep for `metre` and find `SI.sysml`
- [ ] INDEX.md provides quick overview of what's available in each library
- [ ] Script can re-sync when syside is upgraded
- [ ] Library version is tracked for traceability

### Priority

P1 - Enhances `kerml-expert` agent effectiveness. Depends on P0-3 (specialized agents) being complete.

---

## Problem Statement

### Current State

Standard library files exist at:
```
.venv/lib/python3.12/site-packages/syside/sysml.library/
├── Kernel Libraries/
├── Systems Library/
└── Domain Libraries/
```

This location:
- Is not searched by agents (not in configured corpus paths)
- Is not git-tracked
- Will change location if Python version changes
- Provides no index or overview

### Desired Outcome

A synced copy at `docs/sysmlv2/stdlib/` that:
- Mirrors the syside library structure
- Is searchable by agents via grep
- Has an INDEX.md for quick navigation
- Can be refreshed via script when syside updates
- Tracks the source version

---

## Scope

### In Scope

1. **Sync script** (`scripts/sync_stdlib.py`)
   - Copies library files from syside package to `docs/sysmlv2/stdlib/`
   - Preserves directory structure
   - Records syside version in metadata
   - Generates INDEX.md

2. **INDEX.md generation**
   - Hierarchical listing of all packages/files
   - For each file: package name, brief description (from doc comment), list of exported definitions
   - Machine-parseable format for agents

3. **Integration with kerml-expert**
   - Update agent to search `{SYSML_DOCS_PATH}/stdlib/`

### Out of Scope

- Modifying the library files (read-only copy)
- Detailed per-function documentation (that's in the KerML spec)
- Automatic re-sync on syside upgrade (manual trigger)
- AI-generated summaries for INDEX.md (extract from source doc comments)

### Edge Cases & Considerations

- **Spaces in directory names**: "Kernel Libraries", "Quantities and Units" have spaces - script must handle properly
- **syside not installed**: Script should fail gracefully with clear message
- **Version tracking**: Store syside version so we know when re-sync is needed
- **File encoding**: All files should be UTF-8, but verify

---

## Requirements

### Functional Requirements

#### Sync Script

1. **FR-1**: Script MUST locate syside installation path programmatically (not hardcoded)
2. **FR-2**: Script MUST copy all `.kerml` and `.sysml` files preserving directory structure
3. **FR-3**: Script MUST record syside version in `docs/sysmlv2/stdlib/VERSION.md`
4. **FR-4**: Script MUST generate `docs/sysmlv2/stdlib/INDEX.md` with library overview
5. **FR-5**: Script MUST handle directory names with spaces correctly
6. **FR-6**: Script MUST report files copied and any errors
7. **FR-7**: Script SHOULD support `--dry-run` flag to preview without copying
8. **FR-8**: Script SHOULD support `--force` flag to overwrite existing files
9. **FR-9**: Script MUST be runnable as `python scripts/sync_stdlib.py`
10. **FR-10**: Script MUST fail with clear error if syside is not installed

#### INDEX.md Format

11. **FR-11**: INDEX.md MUST have YAML frontmatter with syside version and generation timestamp
12. **FR-12**: INDEX.md MUST include a "Quick Reference" section with key items:
    - Common functions with signatures (~50-80 items: sum, size, collect, etc.)
    - Core types (Real, Integer, Boolean, etc.)
    - Common SI units (m, kg, s, K, W, etc.)
13. **FR-13**: INDEX.md MUST list ALL files (~94) organized by directory hierarchy
14. **FR-14**: Each file entry MUST include:
    - File path (relative to stdlib/)
    - AI-generated 1-line summary (via `claude -p`)
15. **FR-15**: INDEX.md MUST be valid markdown
16. **FR-16**: Script MUST call `claude -p` to generate summaries for each file

#### VERSION.md Format

17. **FR-17**: VERSION.md MUST include:
    - syside package version
    - Python version used
    - Sync timestamp
    - Number of files synced
18. **FR-18**: VERSION.md MUST be human-readable

---

## Acceptance Criteria

### Core Functionality

- [ ] `python scripts/sync_stdlib.py` successfully copies all library files
- [ ] Directory structure at `docs/sysmlv2/stdlib/` mirrors syside package
- [ ] All ~94 files are copied (count matches source)
- [ ] `INDEX.md` generated with Quick Reference + File Index
- [ ] `VERSION.md` shows syside version and sync timestamp
- [ ] `grep -r "function sum" docs/sysmlv2/stdlib/` finds NumericalFunctions.kerml
- [ ] `grep -r "attribute.*metre" docs/sysmlv2/stdlib/` finds SI.sysml

### Script Quality

- [ ] Script handles spaces in directory names
- [ ] Script fails gracefully if syside not installed
- [ ] `--dry-run` shows what would be copied without copying
- [ ] `--force` overwrites existing files
- [ ] Script calls `claude -p` to generate file summaries
- [ ] Script has `--help` output

### INDEX.md Quality

- [ ] Quick Reference includes common functions with signatures
- [ ] Quick Reference includes core types and SI units
- [ ] File Index lists all ~94 files with 1-line AI summaries
- [ ] INDEX.md is ~200 lines (not 2000+)
- [ ] Agent can use INDEX.md to find relevant files

---

## Technical Notes

### Locating syside Package

```python
import importlib.util
import syside

# Get syside installation path
syside_path = Path(syside.__file__).parent
library_path = syside_path / "sysml.library"

# Get version
from importlib.metadata import version
syside_version = version("syside")
```

### Directory Structure After Sync

```
docs/sysmlv2/stdlib/
├── INDEX.md                    # Generated overview
├── VERSION.md                  # Source version tracking
├── Kernel Libraries/
│   ├── Kernel Data Type Library/
│   │   ├── ScalarValues.kerml
│   │   ├── VectorValues.kerml
│   │   └── Collections.kerml
│   ├── Kernel Function Library/
│   │   ├── NumericalFunctions.kerml
│   │   ├── SequenceFunctions.kerml
│   │   └── ... (17 files)
│   └── Kernel Semantic Library/
│       └── ... (13 files)
├── Systems Library/
│   ├── Parts.sysml
│   ├── Ports.sysml
│   └── ... (22 files)
└── Domain Libraries/
    ├── Quantities and Units/
    │   ├── SI.sysml
    │   ├── ISQ.sysml
    │   └── ... (23 files)
    ├── Analysis/
    ├── Geometry/
    ├── Metadata/
    └── Requirement Derivation/
```

### INDEX.md Structure (~200 lines)

```markdown
---
syside_version: "1.2.3"
generated: "2026-01-13T12:00:00Z"
total_files: 94
---

# SysML v2 Standard Library Index

## Quick Reference

### Common Functions

| Function | Signature | Package |
|----------|-----------|---------|
| `sum` | `sum(collection: NumericalValue[0..*]) → NumericalValue` | NumericalFunctions |
| `product` | `product(collection: NumericalValue[0..*]) → NumericalValue` | NumericalFunctions |
| `abs` | `abs(x: NumericalValue) → NumericalValue` | NumericalFunctions |
| `size` | `size(seq: Anything[0..*]) → Natural` | SequenceFunctions |
| `isEmpty` | `isEmpty(seq: Anything[0..*]) → Boolean` | SequenceFunctions |
| `head` | `head(seq: Anything[0..*]) → Anything[0..1]` | SequenceFunctions |
| `tail` | `tail(seq: Anything[0..*]) → Anything[0..*]` | SequenceFunctions |
| `collect` | `collection->collect { mapper }` | ControlFunctions |
| `select` | `collection->select { predicate }` | ControlFunctions |
| `reject` | `collection->reject { predicate }` | ControlFunctions |
| `reduce` | `collection->reduce operator` | ControlFunctions |
| `forAll` | `collection->forAll { test } → Boolean` | ControlFunctions |
| `exists` | `collection->exists { test } → Boolean` | ControlFunctions |
| ... | ... | ... |

### Core Types

| Type | Package | Description |
|------|---------|-------------|
| `Boolean` | ScalarValues | True/false values |
| `String` | ScalarValues | Text values |
| `Real` | ScalarValues | Real numbers |
| `Integer` | ScalarValues | Whole numbers |
| `Natural` | ScalarValues | Non-negative integers |
| `Positive` | ScalarValues | Positive integers |

### Common SI Units

| Symbol | Unit | Quantity |
|--------|------|----------|
| `m` | metre | Length |
| `kg` | kilogram | Mass |
| `s` | second | Duration |
| `K` | kelvin | Temperature |
| `A` | ampere | Electric current |
| `W` | watt | Power |
| `J` | joule | Energy |
| `N` | newton | Force |
| `Pa` | pascal | Pressure |
| `V` | volt | Electric potential |
| `T` | tesla | Magnetic flux density |

---

## File Index

### Kernel Libraries

#### Kernel Data Type Library (3 files)

| File | Summary |
|------|---------|
| `ScalarValues.kerml` | Primitive scalar types: Boolean, String, and Number hierarchy (Real, Integer, Natural, Positive) |
| `VectorValues.kerml` | Vector and matrix value types for multi-dimensional numerical data |
| `Collections.kerml` | Collection types for ordered and unordered sets of values |

#### Kernel Function Library (17 files)

| File | Summary |
|------|---------|
| `NumericalFunctions.kerml` | Arithmetic operations and aggregations (sum, product, abs, max, min) on numerical values |
| `SequenceFunctions.kerml` | Sequence operations (size, isEmpty, head, tail, includes, union, intersection) |
| `ControlFunctions.kerml` | Higher-order functions (collect, select, reject, reduce, forAll, exists) |
| `BooleanFunctions.kerml` | Boolean operations (not, xor, etc.) |
| `StringFunctions.kerml` | String manipulation functions |
| `TrigFunctions.kerml` | Trigonometric functions (sin, cos, tan, etc.) |
| ... | ... |

#### Kernel Semantic Library (16 files)

| File | Summary |
|------|---------|
| `Base.kerml` | Fundamental base types (Anything, DataValue, etc.) |
| `Occurrences.kerml` | Temporal occurrence modeling |
| ... | ... |

### Systems Library (21 files)

| File | Summary |
|------|---------|
| `Parts.sysml` | Base types for parts and structural elements |
| `Ports.sysml` | Port definitions for interface points |
| `Actions.sysml` | Action and behavior modeling |
| `States.sysml` | State machine constructs |
| `Requirements.sysml` | Requirement definition types |
| `Constraints.sysml` | Constraint modeling |
| ... | ... |

### Domain Libraries

#### Quantities and Units (23 files)

| File | Summary |
|------|---------|
| `SI.sysml` | International System of Units (metre, kilogram, second, etc.) |
| `ISQ.sysml` | International System of Quantities |
| `ISQBase.sysml` | Base quantities (Length, Mass, Duration, Temperature, etc.) |
| `ISQMechanics.sysml` | Mechanical quantities (Force, Energy, Power, Pressure) |
| `ISQThermodynamics.sysml` | Thermodynamic quantities (Heat, Entropy) |
| `ISQElectromagnetism.sysml` | Electromagnetic quantities (Voltage, Current, Resistance) |
| ... | ... |

#### Analysis (4 files)
...

#### Geometry (2 files)
...
```

### Generating File Summaries

Use `claude -p` to generate 1-line summaries for each file:

```python
import subprocess

def summarize_file(path: Path) -> str:
    content = path.read_text()
    prompt = f"""Summarize this SysML/KerML library file in ONE line (max 100 chars).
Focus on what functions, types, or definitions it provides.

File: {path.name}
Content:
{content[:2000]}  # Truncate for context limits
"""
    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()
```

### Quick Reference (Hardcoded)

The Quick Reference section is manually curated (not AI-generated) to ensure accuracy for the most commonly needed items. This section should be updated when:
- New commonly-used functions are added to syside
- User feedback indicates missing items

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_documentation-discoverability.md`
- **Depends on:** `.project/active/specialized-doc-agents/spec.md` (kerml-expert agent)
- **Source:** `.venv/lib/python3.12/site-packages/syside/sysml.library/`

---

## Design Decisions

1. **Commit to git**: `docs/sysmlv2/stdlib/` will be committed for availability and version tracking

2. **INDEX.md scope**:
   - Quick Reference: Curated ~50-80 key items with signatures (hardcoded)
   - File Index: All ~94 files with AI-generated 1-line summaries

3. **Quick Reference curation**: Focus on items users actually search for:
   - Kernel Function Library functions (most common questions)
   - Core scalar types
   - SI base + common derived units

---

**Next Steps:** After approval, proceed to implementation
