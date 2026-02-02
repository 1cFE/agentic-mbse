---
name: project-structure
description: >
  Use when asking about "project structure", "where does this go", "library vs designs",
  "file organization", "directory", "EXPOSE pattern", "project files", "4-directory model",
  "knowledge directory", "modeling_project", "work directory", "data directory",
  "OVERVIEW.md", "ARCHITECTURE.md", "REQUIREMENTS.md", "BACKLOG.md",
  or when deciding where to place new files or model elements.
  Provides the 4-directory information architecture and model file organization rules.
allowed-tools: Read, Grep, Glob
user-invocable: false
---

# Project Structure

The 4-directory information architecture, model file organization, and key project files.

## Core Principle

Every file has exactly one home determined by its information role. The 4-directory model answers four questions: "What do we know?" (`knowledge/`), "What are we building?" (`modeling_project/`), "What's in progress?" (`work/`), and "What are the models?" (`models/`).

## When to Reference

- `/onboard` — setting up project structure for new projects
- `/design-model` — placing definitions in library vs designs
- `/implement-model` — creating files in correct locations
- `/plan-model` — planning file creation phases (library before designs)
- `/spec-model` — understanding existing model landscape
- `/backlog` — understanding work item structure

## The 4-Directory Model

| Directory | Question | Contains |
|-----------|----------|----------|
| `knowledge/` | "What do we know?" | SOURCE_INDEX.md, KNOWLEDGE.md (DI-XXX), research pipeline |
| `modeling_project/` | "What are we building?" | OVERVIEW.md (G-XXX, AQ-XXX), ARCHITECTURE.md (AD-XXX), REQUIREMENTS.md (PR-XXX), VALIDATION_MATRIX.md (SV-XXX) |
| `work/` | "What's in progress?" | BACKLOG.md, active/completed work items, learnings |
| `data/` | Machine-readable evidence | traceability_matrix.csv |

```
project-root/
├── knowledge/
│   ├── SOURCE_INDEX.md         # Authority sources registry
│   ├── KNOWLEDGE.md            # Curated domain insights (DI-XXX)
│   └── research/               # Research pipeline (pending → approved)
├── modeling_project/
│   ├── OVERVIEW.md             # Goals (G-XXX), questions (AQ-XXX)
│   ├── ARCHITECTURE.md         # Structural decisions (AD-XXX)
│   ├── REQUIREMENTS.md         # Project-specific rules (PR-XXX)
│   ├── VALIDATION_MATRIX.md    # Verification criteria (SV-XXX)
│   ├── MODELING_GUIDE.md       # Baseline modeling rules (tool-owned)
│   ├── MODELING_PROCESS.md     # Workflow reference (tool-owned)
│   └── intent/                 # Raw user documents
├── work/
│   ├── BACKLOG.md              # Work dashboard
│   ├── EPIC_GUIDE.md           # Decomposition guide (tool-owned)
│   ├── backlog/                # Epic decomposition files
│   ├── active/                 # In-progress work items
│   ├── completed/              # Archived work
│   └── learnings/              # Process knowledge
├── models/
│   ├── library/                # Reusable definitions
│   └── designs/                # Specific configurations
├── tests/models/               # Model validation tests
├── data/
│   └── traceability_matrix.csv
├── CLAUDE.md
└── README.md
```

## Key Project Files

| File | Role | Entity Format |
|------|------|--------------|
| `knowledge/SOURCE_INDEX.md` | Authority sources registry | Name, Type, Location, Use For, Validation |
| `knowledge/KNOWLEDGE.md` | Curated domain insights | DI-XXX entries with Source, Context, Model implications |
| `modeling_project/OVERVIEW.md` | Project goals and questions | G-XXX goals, AQ-XXX analysis questions |
| `modeling_project/ARCHITECTURE.md` | Structural decisions | AD-XXX decisions with Rationale, Status |
| `modeling_project/REQUIREMENTS.md` | Project-specific rules | PR-XXX entries with Source, Enforcement, Validation Method |
| `modeling_project/VALIDATION_MATRIX.md` | Verification criteria | SV-XXX criteria with Type, Mechanism, Tolerance |
| `work/BACKLOG.md` | Work dashboard | Work items with status, priority |

## Model File Organization

```
models/
├── library/                # All definitions (part def, calc def, etc.)
│   ├── foundation/         # Base types, materials, units
│   ├── components/         # Component definitions
│   └── analyses/           # Calc definitions (ADR-002)
└── designs/                # All usages (specific instances)
    └── {config-name}/      # Per-configuration directories
```

## Library vs Designs Separation

**Definitions** live in `library/`, **usages** live in `designs/`:

| Aspect | Library (`models/library/`) | Designs (`models/designs/`) |
|--------|---------------------------|----------------------------|
| Contains | `part def`, `calc def`, `constraint def` | `part`, `calc`, specific instances |
| Naming | `'Title Case'` with quotes | `snake_case` |
| Purpose | Reusable across designs | Specific configuration |

**ADR-002 structural consequence**: `calc def` declarations belong exclusively in `library/analyses/`. Design files contain values and wiring only (literals, static expressions, EXPOSE bindings).

**Library-first phasing**: Always design and implement library definitions before design usages. Bottom-up dependency order: foundation → components → analyses → designs.

For definition vs usage SysML syntax, see the **sysml-conventions** skill.

## Cross-File Dependencies

**Unidirectional imports rule**: Designs import from library, never the reverse.

```
designs/ ──imports──> library/    ✓
library/ ──imports──> designs/    ✗ NEVER
```

Package boundaries align with directory structure. Each directory maps to a SysML package.

## EXPOSE Pattern

Expose calc outputs as design attributes for cross-file access:

```sysml
part geometry {
    calc dimension_calc : DimensionCalculation { ... }
    attribute calculated_area : Real = dimension_calc.area;  // EXPOSE
}
```

Consumers bind to `geometry.calculated_area`, not `geometry.dimension_calc.area`. Use EXPOSE any time a calc output needs cross-file access.

## Intent Formalization

Raw user documents (project charters, stakeholder notes) live in `modeling_project/intent/`. The `/formalize-intent` command extracts structured G-XXX goals and AQ-XXX analysis questions into `modeling_project/OVERVIEW.md`.

```
modeling_project/intent/          →  modeling_project/OVERVIEW.md
  (raw prose documents)               (structured G-XXX, AQ-XXX)
```

## Anti-Patterns

| Instead of | Do |
|------------|-----|
| Putting calc defs in `designs/` | Place all `calc def` in `library/analyses/` (ADR-002) |
| Importing from designs into library | Keep imports unidirectional: designs → library |
| Mixing definitions and usages in one directory | Definitions in `library/`, usages in `designs/` |
| Creating files without checking structure | Read existing structure first; follow conventions |
| Putting domain insights in `modeling_project/` | Domain knowledge belongs in `knowledge/` |
| Storing work items outside `work/` | Active/completed work tracked under `work/` |

## Related Skills

- For definition vs usage SysML syntax, see the **sysml-conventions** skill.
- For validation of model files, see the **model-validation** skill.
