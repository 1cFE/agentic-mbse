---
date: 2026-01-13T15:00:00-05:00
researcher: Claude
topic: "Progressive Disclosure Architecture for Agentic MBSE"
tags: [research, architecture, progressive-disclosure, agent-learning, development-mode]
status: complete
last_updated: 2026-01-13
---

# Research: Progressive Disclosure Architecture for Agentic MBSE

**Date**: 2026-01-13T15:00:00-05:00
**Researcher**: Claude (Opus 4.5)
**Research Type**: Architecture / Design Patterns

## Research Question

Design a scalable architecture for progressive disclosure of modeling information and tools, including feedback mechanisms for agent learning, that addresses:
- ITEM-GUIDE-001: Progressive Disclosure for Modeling Guides
- ITEM-DEVMODE-001: Development Mode for Domain Projects
- ITEM-LEARNING-001: Agent Learning Feedback Loop

---

# Part 1: MODELING_GUIDE.md Restructuring (ITEM-GUIDE-001)

## Current State Analysis

The current `MODELING_GUIDE.md.template` is **1,497 lines**. Here's the section-by-section breakdown:

| Section | Lines | Current Size | Keep/Move |
|---------|-------|--------------|-----------|
| Core Principle: Definitions vs Usages | 18-80 | 62 lines | Condense to 25 lines, move details |
| The EXPOSE Pattern | 82-141 | 59 lines | Condense to 12 lines, move details |
| Calculation Architecture (ADR-002) | 144-233 | 89 lines | Condense to 20 lines, move details |
| Package Structure | 236-242 | 6 lines | Keep as-is |
| Naming Conventions | 245-252 | 7 lines | Keep as-is |
| Documentation Standards | 255-338 | 83 lines | Condense to 15 lines, move details |
| Standard Imports | 341-372 | 31 lines | Keep condensed (20 lines) |
| SysML Syntax Quick Reference (10 patterns) | 375-598 | 223 lines | **Move entirely** → 5 line reference |
| MBSE Concept Patterns (4 patterns) | 601-693 | 92 lines | **Move entirely** → 5 line reference |
| Semantic Operators (huge section) | 696-1186 | 490 lines | **Move entirely** → 10 line reference |
| Package Naming & Multi-File | 1190-1263 | 73 lines | **Move entirely** → 5 line reference |
| Validation Requirements | 1265-1287 | 22 lines | Keep as-is |
| File Organization | 1290-1318 | 28 lines | Merge with Package Structure (10 lines) |
| Common Mistakes | 1320-1369 | 49 lines | **Move entirely** → 5 line reference |
| Tools and Scripts | 1371-1382 | 11 lines | Keep as-is |
| Questions | 1384-1391 | 7 lines | Keep as-is |
| Pattern Validation Status | 1395-1493 | 98 lines | **Move entirely** → learnings system |

**Total current**: 1,497 lines
**Target**: ≤200 lines

## The Restructured MODELING_GUIDE.md

Here's what the new document looks like (with actual line counts):

```markdown
# SysML Modeling Guide

Quick reference for SysML v2 modeling. Each section links to detailed pattern docs.

**Related Docs:**
- [models/README.md](../models/README.md) - Model catalog and navigation
- [OVERVIEW.md](OVERVIEW.md) - Project architecture

---

## Core Principle: Definitions vs Usages

| Aspect | Definitions (Library) | Usages (Designs) |
|--------|----------------------|------------------|
| **Purpose** | Reusable types | Specific instances |
| **Location** | `models/library/` | `models/designs/{name}/` |
| **Naming** | `'Title Case'` with quotes | `snake_case` |
| **Example** | `part def 'Pump'` | `part my_pump : 'Pump'` |

**Decision**: "Could this apply to multiple designs?" → Yes = Definition, No = Usage

> **Full reference**: [patterns/definitions-usages.md] - Complete examples, decision tree, specialization patterns

---

## The EXPOSE Pattern

Expose calc outputs as design attributes for cross-file access:

```sysml
part geometry {
    calc dimension_calc : DimensionCalculation { ... }
    attribute calculated_area : Real = dimension_calc.area;  // EXPOSE
}
```

Consumers bind to `geometry.calculated_area`, not `geometry.dimension_calc.area`.

> **Full reference**: [patterns/expose-pattern.md] - Anti-patterns, producer/consumer examples

---

## Calculation Architecture (ADR-002)

> `calc def` declarations in `library/` only. Design files contain values and wiring.

| In Design Files | Status |
|-----------------|--------|
| Literal: `= 3.0 [m]` | OK |
| Static expr: `= 3.14 * 2.0` | OK |
| EXPOSE: `= my_calc.output` | OK |
| Derived: `= radius * 2.0` | **VIOLATION** → extract to calc def |

> **Full reference**: [patterns/adr002-calculations.md] - Expression taxonomy, resolution patterns

---

## Package Structure

```
models/
├── library/          # All definitions (part def, calc def, etc.)
│   ├── foundation/   # Base types, materials, units
│   ├── components/   # Component definitions
│   └── analyses/     # Calc definitions
├── designs/          # All usages (specific instances)
│   └── {design_name}/
└── tests/            # Test models
```

---

## Naming Conventions

- **Definitions**: `'Title Case'` with single quotes
- **Usages**: `snake_case`
- **Attributes**: `snake_case`
- **Packages**: `lowercase_underscores`

---

## Documentation Standards

Every `part def`, `calc def`, `constraint def` requires:

```sysml
part def 'Component' {
    doc /*
    Description of component.

    **Source**: Reference document
    **Reference**: path/to/source.pdf
    **Last Updated**: YYYY-MM-DD
    */
}
```

> **Full reference**: [patterns/doc-comments.md] - Citation formats, validation, traceability

---

## Standard Imports

```sysml
package MyProject::Library::Components {
    import ScalarValues::*;    // Real, Integer, Boolean
    import ISQ::*;             // Physical quantities
    import SI::*;              // SI units

    // For cost aggregation over multiplicities:
    private import NumericalFunctions::sum;
}
```

---

## Key Syntax Patterns

One example each. See pattern docs for full syntax, variations, and common mistakes.

**Conditional expressions:**
```sysml
attribute diff : Real = if x > y? x - y else y - x;
```
> [patterns/conditionals.md]

**Constraints:**
```sysml
assert constraint TempLimit { temperature < 1000 [K] }
```
> [patterns/constraints.md]

**Cross-file binding:**
```sysml
private import OtherPackage::other_part;
calc my_calc { in value = other_part.exposed_attr; }
```
> [patterns/cross-file-binding.md]

**Semantic operators (`=` vs `default :=` vs `:>>`):**
> [patterns/semantic-operators.md] - Critical for correct AST generation

---

## Validation Checklist

```
- [ ] Model parses: `agentic-mbse validate models/`
- [ ] All definitions have doc comments with sources
- [ ] Units specified: `= 3.0 [m]` not `= 3.0`
- [ ] Naming conventions followed
- [ ] No calc defs in designs/ (ADR-002)
```

---

## Pattern Documentation Index

All pattern docs are in the agentic-mbse `docs/patterns/` directory.
Agents have read permissions via `.claude/settings.json`.

| Pattern Doc | Covers |
|-------------|--------|
| `definitions-usages.md` | Definition vs Usage distinction, decision tree |
| `expose-pattern.md` | EXPOSE pattern details, anti-patterns |
| `adr002-calculations.md` | Calculation architecture, expression taxonomy |
| `doc-comments.md` | Documentation standards, citation formats |
| `conditionals.md` | Conditional expression syntax |
| `constraints.md` | Constraint syntax and prefixes |
| `cross-file-binding.md` | Cross-file imports and bindings |
| `semantic-operators.md` | `=` vs `default :=` vs `:>>` vs `:>` |
| `package-naming.md` | Multi-file organization, unique names |
| `mbse-concepts.md` | Allocation, interfaces, cost patterns |
| `common-mistakes.md` | Anti-patterns to avoid |

**Last Updated**: 2026-01-13
```

**Line count**: ~180 lines (meets ≤200 target)

## Pattern Documents to Create

### 1. `docs/patterns/definitions-usages.md` (extract from lines 18-80)

**Content to move:**
- Full code examples for library definitions
- Full code examples for design usages
- Decision tree (lines 71-78)
- Specialization patterns

### 2. `docs/patterns/expose-pattern.md` (extract from lines 82-141)

**Content to move:**
- Why Use It (lines 101-106)
- How to Use It with producer/consumer examples (lines 108-122)
- Anti-patterns section (lines 124-140)

### 3. `docs/patterns/adr002-calculations.md` (extract from lines 144-233)

**Content to move:**
- Full expression taxonomy table (lines 164-173)
- Valid patterns in design files (lines 175-188)
- Invalid pattern example and resolution (lines 190-223)
- Supported static operators table (lines 225-232)

### 4. `docs/patterns/doc-comments.md` (extract from lines 255-338)

**Content to move:**
- Full doc comment template with all 6 sections (lines 266-296)
- Citation patterns: Physical laws, Literature, Codebase-derived (lines 298-337)

### 5. `docs/patterns/syntax-reference.md` (extract from lines 375-598)

**Content to move:**
- All 10 syntax patterns:
  - Package imports (lines 379-398)
  - Calc def definition (lines 400-429)
  - Calc def instantiation (lines 431-451)
  - Cross-file attribute binding (lines 453-476)
  - Attribute with units (lines 478-487)
  - Constraints (lines 489-508)
  - Geometry calculations (lines 510-526)
  - Part definition (lines 528-562)
  - Part instantiation (lines 564-579)
  - Conditional expressions (lines 581-597) - OR reference existing conditionals.md

### 6. `docs/patterns/mbse-concepts.md` (extract from lines 601-693)

**Content to move:**
- Pattern 1: Allocation (lines 605-624)
- Pattern 2: Parametric Constraint (lines 626-644)
- Pattern 3: Cost/Analysis Calculation (lines 646-672)
- Pattern 4: Interface Definition (lines 674-693)

### 7. `docs/patterns/semantic-operators.md` (extract from lines 696-1186)

**Content to move:**
- Assignment vs Default vs Redefinition (lines 710-827)
- Validated correct pattern: Usage-based dataflow (lines 830-900)
- Dual navigation (lines 902-956)
- Multi-level aliasing (lines 958-1010)
- Circular dependencies (lines 1012-1052)
- Binding vs Redefinitions (lines 1055-1126)
- Constraint syntax requirements (lines 1128-1162)
- Quick reference decision tree (lines 1165-1186)

### 8. `docs/patterns/package-naming.md` (extract from lines 1190-1263)

**Content to move:**
- Critical rule about unique package names (lines 1192-1196)
- Incorrect pattern example (lines 1198-1210)
- Correct patterns 1-3 (lines 1212-1261)

### 9. `docs/patterns/common-mistakes.md` (extract from lines 1320-1369)

**Content to move:**
- Don't mix definitions and usages (lines 1322-1345)
- Don't omit documentation (lines 1347-1368)

### 10. `docs/patterns/constraints.md` (NEW - consolidate)

**Content to create:**
- Constraint prefix keywords (`assert`, `require`, `assume`)
- Constraint syntax from semantic operators section
- Examples from syntax reference

## Hyperlink Strategy

**Problem**: `docs/patterns/` lives in agentic-mbse, not in the target project.

**Solution**: Use bracketed path references that agents can resolve:

```markdown
> **Full reference**: [patterns/semantic-operators.md]
```

**How it works:**
1. Agents have permissions to read `~/1cfe/agentic-mbse/docs/**` (via settings.json)
2. When agent sees `[patterns/X.md]`, it knows to look in the docs/patterns/ directory
3. The path is searchable/greppable for discovery

**For humans**: Add note in Pattern Documentation Index section explaining that pattern docs are in the agentic-mbse package docs/ directory.

---

# Part 2: Development Mode (ITEM-DEVMODE-001)

## Exact Symlink Paths

### Current Behavior: Copy

```python
# Source paths (in agentic-mbse)
source_commands = Path("/home/reid/1cfe/agentic-mbse/claude/commands")
source_agents = Path("/home/reid/1cfe/agentic-mbse/claude/agents")
source_skills = Path("/home/reid/1cfe/agentic-mbse/claude/skills")
source_hooks = Path("/home/reid/1cfe/agentic-mbse/claude/hooks")
source_templates = Path("/home/reid/1cfe/agentic-mbse/project_templates")

# Target paths (in domain project, e.g., fusion-tea)
target_commands = Path("/home/reid/1cfe/fusion-tea/.claude/commands")
target_agents = Path("/home/reid/1cfe/fusion-tea/.claude/agents")
# etc.

# Current behavior: shutil.copy(src, dst)
```

### New Behavior: Symlink (--dev mode)

```python
# Same source paths, but create symlinks instead:

# TOOL-OWNED files get symlinked
dst.symlink_to(src.resolve())

# Example results (what `ls -la` shows):
# /home/reid/1cfe/fusion-tea/.claude/commands/design-model.md
#   -> /home/reid/1cfe/agentic-mbse/claude/commands/design-model.md

# USER-OWNED files still get copied (never symlinked)
```

### File Classification

| Category | Files | Behavior in --dev |
|----------|-------|-------------------|
| **TOOL-OWNED** | All files in `MBSE_COMMANDS`, `MBSE_AGENTS`, `MBSE_SKILLS`, `MBSE_HOOKS`, `TOOL_OWNED_TEMPLATES` | **Symlink** |
| **USER-OWNED** | `.gitignore`, `SOURCE_INDEX.md`, `.claude/settings.json`, `USER_OWNED_TEMPLATES` | **Copy** (always) |

### Concrete File Lists

**TOOL-OWNED (symlinked in --dev):**
```
.claude/commands/design-model.md      -> /path/to/agentic-mbse/claude/commands/design-model.md
.claude/commands/plan-model.md        -> /path/to/agentic-mbse/claude/commands/plan-model.md
.claude/commands/implement-model.md   -> /path/to/agentic-mbse/claude/commands/implement-model.md
.claude/commands/spec-model.md        -> /path/to/agentic-mbse/claude/commands/spec-model.md
.claude/commands/research.md          -> /path/to/agentic-mbse/claude/commands/research.md
.claude/commands/audit-models.md      -> /path/to/agentic-mbse/claude/commands/audit-models.md
.claude/commands/onboard.md           -> /path/to/agentic-mbse/claude/commands/onboard.md
.claude/commands/manage-sources.md    -> /path/to/agentic-mbse/claude/commands/manage-sources.md
.claude/commands/backlog.md           -> /path/to/agentic-mbse/claude/commands/backlog.md

.claude/agents/python-debugger.md     -> /path/to/agentic-mbse/claude/agents/python-debugger.md
.claude/agents/kerml-expert.md        -> /path/to/agentic-mbse/claude/agents/kerml-expert.md
.claude/agents/sysml-expert.md        -> /path/to/agentic-mbse/claude/agents/sysml-expert.md
.claude/agents/syside-expert.md       -> /path/to/agentic-mbse/claude/agents/syside-expert.md
.claude/agents/sysmlv2-validator.md   -> /path/to/agentic-mbse/claude/agents/sysmlv2-validator.md

.claude/skills/python-debugger/       -> /path/to/agentic-mbse/claude/skills/python-debugger/

.claude/hooks/ruff-format.sh          -> /path/to/agentic-mbse/claude/hooks/ruff-format.sh

project/MODELING_GUIDE.md             -> /path/to/agentic-mbse/project_templates/MODELING_GUIDE.md.template
project/MODELING_PROCESS.md           -> /path/to/agentic-mbse/project_templates/MODELING_PROCESS.md.template
```

**USER-OWNED (always copied, never symlinked):**
```
.gitignore                            (copied)
SOURCE_INDEX.md                       (copied)
.claude/settings.json                 (copied)
README.md                             (copied from README.md.template)
project/OVERVIEW.md                   (copied from OVERVIEW.md.template)
project/backlog/BACKLOG.md            (copied from BACKLOG.md.template)
```

### Implementation Details

```python
# In src/agentic_mbse/cli/__init__.py

def cmd_init(args: argparse.Namespace) -> int:
    # ... existing setup ...

    # Detect dev mode
    is_dev_mode = getattr(args, 'dev', False)
    dev_repo_path = getattr(args, 'repo', None)

    # Validate dev mode prerequisites
    if is_dev_mode:
        data_root = _get_data_root()
        # Check if we're in a source checkout (not pip-installed)
        if not (data_root / "claude").exists():
            print("Error: --dev mode requires agentic-mbse source checkout",
                  file=sys.stderr)
            print("Pip-installed packages cannot use dev mode.", file=sys.stderr)
            return EXIT_FAILURE

        # If explicit repo path provided, use it
        if dev_repo_path:
            data_root = Path(dev_repo_path).resolve()
            if not (data_root / "claude").exists():
                print(f"Error: {dev_repo_path} is not an agentic-mbse repo",
                      file=sys.stderr)
                return EXIT_FAILURE

    # ... for each TOOL-OWNED file ...
    for cmd in MBSE_COMMANDS:
        src = source_commands / cmd
        dst = commands_dir / cmd
        if src.exists():
            existed = dst.exists()
            if is_dev_mode:
                # Remove existing file/symlink before creating new symlink
                if dst.exists() or dst.is_symlink():
                    dst.unlink()
                dst.symlink_to(src.resolve())
                action = "symlinked" if not existed else "re-symlinked"
            else:
                shutil.copy(src, dst)
                action = "created" if not existed else "updated"
            # ... tracking ...
```

### CLI Interface

```bash
# Standard mode (for production domain projects)
agentic-mbse init /path/to/project

# Development mode (for testing agentic-mbse changes)
agentic-mbse init --dev /path/to/project

# Development mode with explicit repo path
agentic-mbse init --dev --repo ~/1cfe/agentic-mbse /path/to/project

# Check what mode was used
ls -la /path/to/project/.claude/commands/design-model.md
# If symlink: lrwxrwxrwx ... design-model.md -> /home/.../agentic-mbse/...
# If copy: -rw-r--r-- ... design-model.md
```

### Edge Cases

| Scenario | Handling |
|----------|----------|
| Pip-installed package + `--dev` | Error: "Dev mode requires source checkout" |
| Target file exists as regular file | Remove and replace with symlink |
| Target file exists as symlink | Remove and create new symlink |
| Source file missing | Skip with warning (existing behavior) |
| Windows | Use `os.symlink()` with `target_is_directory` for skill dirs; may need admin rights |

---

# Part 3: Learning Feedback Loop (ITEM-LEARNING-001)

## Directory Structure

```
project/learnings/
├── RAW_LEARNINGS.md          # Append-only capture file
├── INDEX.md                   # Auto-generated category index
└── REVIEWED.md                # Human-verified, ready for formalization
```

## RAW_LEARNINGS.md Format

```markdown
# Raw Learnings

Append-only log of agent discoveries. Each entry is a potential pattern.

---

## 2026-01-13T14:32:00-05:00

**Category**: Import Pattern
**Severity**: Critical
**Source**: fusion-tea modeling session
**Trigger**: Parse error "No Type named 'sum' found"

### Problem
Tried to use `sum(collection)` for cost aggregation but got unresolved reference error.

### Solution
```sysml
private import NumericalFunctions::sum;
attribute total : Real = sum(costs);
```

### Generalization
All stdlib functions need explicit imports. Can't use qualified names directly in expressions without import statement.

### Verification Status
- [x] Parser tested (`syside check` passes)
- [ ] Doc verified (matches spec)
- [ ] Formalized to pattern doc

---

## 2026-01-13T15:45:00-05:00

**Category**: Syntax Gotcha
**Severity**: Important
**Source**: fusion-tea modeling session
**Trigger**: Unexpected parse behavior

### Problem
Used C-style ternary `condition ? true : false` but it failed to parse.

### Solution
```sysml
// Correct SysML v2 syntax:
attribute diff : Real = if x > y? x - y else y - x;
```

### Generalization
SysML v2 uses `if COND? TRUE else FALSE` syntax. The `?` comes AFTER the condition, not as a separator.

### Verification Status
- [x] Parser tested
- [x] Doc verified
- [x] Formalized to pattern doc → docs/patterns/conditionals.md

---
```

## /record-learning Command

**File**: `claude/commands/record-learning.md`

```markdown
# Record Learning Command

**Purpose:** Capture an insight or pattern discovered during modeling work
**Input:** Learning description, optional category
**Output:** Appends to `project/learnings/RAW_LEARNINGS.md`

## Usage

```
/record-learning <description>
/record-learning --category "Import Pattern" <description>
```

## Process

1. **Parse input** - Extract learning description and optional category
2. **Prompt for details** if not provided:
   - Category: Import Pattern | Syntax Gotcha | Error Interpretation | Workaround | Best Practice
   - Severity: Critical | Important | Nice-to-know
   - Problem: What was attempted and failed
   - Solution: The working code/approach
   - Generalization: Broader principle
3. **Format entry** using RAW_LEARNINGS.md template
4. **Append to file** at `project/learnings/RAW_LEARNINGS.md`
5. **Confirm** with preview of what was added

## Categories

| Category | When to Use |
|----------|-------------|
| Import Pattern | Missing imports, stdlib function access |
| Syntax Gotcha | Valid-looking syntax that doesn't parse |
| Error Interpretation | Parser errors and their meanings |
| Workaround | Alternative approaches when direct approach fails |
| Best Practice | Preferred patterns over alternatives |

## Example

```
/record-learning The sum() function requires importing NumericalFunctions::sum,
not just using NumericalFunctions::sum in the expression directly.
```

Creates entry with:
- Auto-detected category: "Import Pattern" (from keyword "import")
- Timestamp: Current ISO timestamp
- Source: Current project context
- Prompts for Problem/Solution/Generalization if not clear from description
```

## record-learning Skill (for agent self-invocation)

**File**: `claude/skills/record-learning/prompt.md`

```markdown
---
name: record-learning
description: Capture a modeling insight or pattern discovery for future reference
---

# Record Learning Skill

Use this skill when you discover something during modeling that should be remembered:
- A workaround that solved a tricky problem
- An import that was required but not obvious
- Syntax that looked right but didn't work
- A pattern that's more effective than the documented approach

## When to Invoke

Invoke this skill when:
1. You tried something that failed, then found the correct approach
2. You spent multiple iterations solving a parsing/syntax issue
3. You discovered behavior that differs from expectations
4. You found a pattern worth codifying

## How to Invoke

From your response, include:

```
I discovered something worth recording for future sessions.

Learning: [The insight]
Category: [Import Pattern | Syntax Gotcha | Error Interpretation | Workaround | Best Practice]
Problem: [What was attempted]
Solution: [What worked]
```

Then invoke: `/record-learning`

## What Happens

1. Entry is appended to `project/learnings/RAW_LEARNINGS.md`
2. Future agents can discover it via grep/search
3. Human review process formalizes valuable learnings into pattern docs
```

## INDEX.md Auto-Generation

**File**: `project/learnings/INDEX.md`

Generated by scanning RAW_LEARNINGS.md:

```markdown
# Learnings Index

Auto-generated from RAW_LEARNINGS.md entries.

## By Category

### Import Pattern
- [2026-01-13] sum() requires NumericalFunctions import → [formalized](../../../docs/patterns/imports.md)
- [2026-01-12] collect() from ControlFunctions

### Syntax Gotcha
- [2026-01-13] Conditional syntax is `if COND?` not ternary → [formalized](../../../docs/patterns/conditionals.md)
- [2026-01-11] Constraint requires `assert` prefix

### Error Interpretation
- [2026-01-10] "subsetting-featuring-types" warning meaning

## By Severity

### Critical
- sum() import pattern
- Conditional syntax

### Important
- assert constraint prefix
- subsetting warning interpretation

## Formalization Status

| Entry | Status | Pattern Doc |
|-------|--------|-------------|
| sum() import | Formalized | patterns/imports.md |
| Conditional syntax | Formalized | patterns/conditionals.md |
| assert prefix | Pending review | - |

---
*Last regenerated: 2026-01-13T16:00:00*
```

## Human Review Process

1. **Periodic review** (weekly or after major modeling sessions)
2. **Verify correctness**:
   - Run `syside check` on code examples
   - Cross-reference with spec if applicable
3. **Move to REVIEWED.md** with verification status
4. **Formalize if valuable**:
   - Create/update pattern doc in `docs/patterns/`
   - Add reference in MODELING_GUIDE.md Pattern Documentation Index
5. **Regenerate INDEX.md** with updated status

---

# Part 4: Integration - How It All Works Together

## Knowledge Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AGENT MODELING SESSION                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│  TIER 1: CORE   │      │  TIER 2: INDEX  │      │  TIER 3: DETAIL │
│  (Always Read)  │      │ (On Discovery)  │      │  (When Needed)  │
├─────────────────┤      ├─────────────────┤      ├─────────────────┤
│ MODELING_GUIDE  │ ──── │ patterns/       │ ──── │ patterns/       │
│ (~200 lines)    │  │   │ README.md       │  │   │ semantic-       │
│                 │  │   │                 │  │   │ operators.md    │
│ - Core rules    │  │   │ learnings/      │  │   │ (~500 lines)    │
│ - Decision      │  │   │ INDEX.md        │  │   │                 │
│   shortcuts     │  │   │                 │  │   │ learnings/      │
│ - Pattern refs  │  │   │ sysmlv2/*/      │  │   │ RAW_LEARNINGS   │
│                 │  │   │ INDEX.md        │  │   │ .md             │
└─────────────────┘  │   └─────────────────┘  │   └─────────────────┘
                     │                        │
                     │   "See patterns/X.md"  │   Grep INDEX.md →
                     └────────────────────────┘   Read specific lines
```

## Agent Discovery Pattern (Concrete)

### When agent needs to know about semantic operators:

1. **Read MODELING_GUIDE.md** (always loaded)
   - Sees: `> [patterns/semantic-operators.md] - Critical for correct AST generation`

2. **Read patterns/README.md** (grep for "semantic")
   ```bash
   # Agent runs:
   Grep("semantic", "docs/patterns/README.md")
   ```
   - Finds: `semantic-operators.md | = vs default := vs :>> vs :>`

3. **Read patterns/semantic-operators.md** (targeted read)
   ```bash
   # Agent runs:
   Read("docs/patterns/semantic-operators.md")
   ```
   - Gets full 500-line reference with all examples

### When agent encounters unfamiliar error:

1. **Check learnings/INDEX.md** first (grep for error message)
   ```bash
   Grep("subsetting-featuring-types", "project/learnings/INDEX.md")
   ```

2. **If found**: Read the specific learning entry
3. **If not found**: Spawn specialized agent (sysmlv2-validator)
4. **After solving**: Invoke record-learning skill

## File Locations Summary

### In agentic-mbse repo:
```
agentic-mbse/
├── claude/
│   ├── commands/
│   │   ├── record-learning.md        # NEW
│   │   └── ... (existing commands)
│   ├── agents/
│   │   └── ... (existing agents)
│   └── skills/
│       ├── record-learning/          # NEW
│       │   └── prompt.md
│       └── python-debugger/
├── docs/
│   └── patterns/
│       ├── README.md                  # EXISTS (update)
│       ├── conditionals.md            # EXISTS
│       ├── definitions-usages.md      # NEW (extract from MODELING_GUIDE)
│       ├── expose-pattern.md          # NEW (extract from MODELING_GUIDE)
│       ├── adr002-calculations.md     # NEW (extract from MODELING_GUIDE)
│       ├── doc-comments.md            # NEW (extract from MODELING_GUIDE)
│       ├── syntax-reference.md        # NEW (extract from MODELING_GUIDE)
│       ├── mbse-concepts.md           # NEW (extract from MODELING_GUIDE)
│       ├── semantic-operators.md      # NEW (extract from MODELING_GUIDE)
│       ├── package-naming.md          # NEW (extract from MODELING_GUIDE)
│       ├── constraints.md             # NEW (consolidate)
│       ├── cross-file-binding.md      # NEW (extract from syntax-reference)
│       └── common-mistakes.md         # NEW (extract from MODELING_GUIDE)
├── project_templates/
│   ├── MODELING_GUIDE.md.template     # REWRITE (shrink to ~200 lines)
│   └── ... (existing templates)
└── src/agentic_mbse/cli/__init__.py   # UPDATE (add --dev flag)
```

### In target domain project:
```
domain-project/
├── .claude/
│   ├── commands/                      # symlinked or copied
│   ├── agents/                        # symlinked or copied
│   ├── skills/                        # symlinked or copied
│   └── settings.json                  # copied (has permissions to docs/)
├── project/
│   ├── MODELING_GUIDE.md              # symlinked or copied (~200 lines)
│   ├── MODELING_PROCESS.md            # symlinked or copied
│   └── learnings/                     # NEW directory structure
│       ├── RAW_LEARNINGS.md
│       ├── INDEX.md
│       └── REVIEWED.md
└── models/
```

---

# Part 5: Success Criteria Checklist

## ITEM-GUIDE-001: Progressive Disclosure

- [ ] MODELING_GUIDE.md.template ≤200 lines
- [ ] Each major section has max 20 lines + pattern doc reference
- [ ] 11 new pattern docs created in docs/patterns/
- [ ] docs/patterns/README.md updated with index
- [ ] Pattern references use consistent format: `> [patterns/X.md]`
- [ ] All pattern docs are parser-verified (syside check passes on examples)

## ITEM-DEVMODE-001: Development Mode

- [ ] `--dev` flag added to `cmd_init()`
- [ ] `--repo` flag added for explicit source path
- [ ] TOOL_OWNED files symlinked in dev mode
- [ ] USER_OWNED files always copied
- [ ] Error message if dev mode used with pip-installed package
- [ ] Summary output shows symlink vs copy status
- [ ] `ls -la` shows correct symlink targets

## ITEM-LEARNING-001: Learning Feedback Loop

- [ ] `project/learnings/` directory created by init
- [ ] RAW_LEARNINGS.md format defined with all fields
- [ ] INDEX.md auto-generation logic documented
- [ ] /record-learning command created
- [ ] record-learning skill created
- [ ] Integration with MODELING_GUIDE.md Pattern Documentation Index
- [ ] Human review process documented

## Integration

- [ ] Pattern docs accessible from MODELING_GUIDE references
- [ ] Agents can grep pattern docs (via permissions)
- [ ] Learnings discoverable via INDEX.md
- [ ] Formalized learnings appear in pattern docs
- [ ] Dev mode enables rapid pattern doc iteration

---

# Appendix: Open Design Questions

1. **Pattern versioning**: Should pattern docs track syside version compatibility in frontmatter?
   - Proposal: Yes, add `syside_version: >=0.8.1` to pattern doc frontmatter

2. **Cross-project learnings**: Should RAW_LEARNINGS.md sync back to agentic-mbse?
   - Proposal: Not automatically. Human review process should manually extract valuable learnings.

3. **INDEX.md regeneration**: Manual or hook-based?
   - Proposal: Add hook that regenerates on session end if RAW_LEARNINGS.md changed

4. **Pattern doc publishing**: Should docs be published to a website for human access?
   - Proposal: Defer. For now, humans can access via agentic-mbse repo.
