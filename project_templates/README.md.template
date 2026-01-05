# <!-- PROJECT_NAME -->

<!-- PROJECT_DESCRIPTION -->

## Quick Start

```bash
# Install agentic-mbse (if not already installed)
pip install agentic-mbse

# Initialize project (creates commands, templates, validation)
agentic-mbse init

# Run onboarding to configure your project
/onboard
```

---

## How This Project Works

This project uses **Model-Based Systems Engineering (MBSE)** with SysML v2 to create formal, validated models. The workflow is AI-assisted through Claude Code slash commands.

### The Document System

Each document has **one clear purpose**:

| Document | Purpose | Managed By |
|----------|---------|------------|
| **README.md** | Project overview (this file) | You |
| **CLAUDE.md** | AI operating rules, environment setup | You |
| **SOURCE_INDEX.md** | Domain knowledge sources | `/manage-sources` |
| **project/OVERVIEW.md** | Project status and goals | You |
| **project/backlog/BACKLOG.md** | Work item pipeline | `/backlog` |
| **project/MODELING_GUIDE.md** | SysML syntax reference | Static (don't edit) |
| **project/MODELING_PROCESS.md** | MBSE methodology | Static (don't edit) |

### What You Edit vs What Commands Manage

**You edit directly:**
- `README.md` - Project-specific setup instructions
- `CLAUDE.md` - Environment rules (virtualenv, PYTHONPATH, lint)
- `project/OVERVIEW.md` - Project status, goals, success criteria

**Commands manage for you:**
- `SOURCE_INDEX.md` - Use `/manage-sources` to add/remove sources
- `project/backlog/BACKLOG.md` - Use `/backlog add` and `/backlog clear`
- `project/active/*` - Created by `/spec-model`, `/design-model`, `/plan-model`
- `models/**/*.sysml` - Created by `/implement-model`

**Static (from agentic-mbse, don't edit):**
- `project/MODELING_GUIDE.md` - SysML patterns and syntax
- `project/MODELING_PROCESS.md` - MBSE methodology and workflow

---

## The Toolkit

### CLI Commands

```bash
# Initialize a new project
agentic-mbse init [path]

# Validate SysML models (8-level quality checks)
agentic-mbse validate [models/]

# Just install/update slash commands
agentic-mbse install-commands [--force]
```

### Slash Commands (in Claude Code)

| Command | Purpose |
|---------|---------|
| `/onboard` | Configure project, learn workflow |
| `/research {topic}` | Deep-dive into domain knowledge |
| `/spec-model {feature}` | Define requirements |
| `/design-model {feature}` | Design model architecture |
| `/plan-model {feature}` | Plan implementation phases |
| `/implement-model {feature}` | Create SysML files |
| `/audit-models` | Validate against sources |
| `/manage-sources` | Add/remove domain sources |
| `/backlog add [source]` | Add work items |
| `/backlog clear` | Archive completed work |

### Validation Framework

Models are validated at 8 levels:

| Level | Check | Blocking? |
|-------|-------|-----------|
| 1 | Syntax - SysML parses correctly | Yes |
| 2 | Structure - No unused definitions | Yes |
| 3 | Dataflow - No circular dependencies | Yes |
| 4 | Constraints - Physics/engineering limits | No |
| 5 | Semantics - Naming, organization | No |
| 6 | Traceability - Doc comments cite sources | No |
| 7 | Architecture - Follows project patterns | No |
| 8 | Codegen - Ready for code generation | No |

```bash
# Run all validation
agentic-mbse validate models/

# Run specific level
agentic-mbse validate --level=3 models/

# Continue past failures
agentic-mbse validate --complete models/
```

---

## The MBSE Workflow

Work flows through a **pipeline** with validation at each stage:

```
/research {topic}           Optional: explore domain
       |
       v
/spec-model {feature}       Define requirements
       |
       v
/design-model {feature}     Design + prototype + validate
       |
       v
/plan-model {feature}       Plan implementation phases
       |
       v
/implement-model {feature}  Create SysML files
       |
       v
/audit-models               Validate against sources
       |
       v
/backlog clear              Archive completed work
```

---

## Project Structure

<!-- PROJECT_STRUCTURE -->

### Model Organization

```
models/
├── library/           # Reusable DEFINITIONS
│   ├── definitions/   # Part and attribute defs
│   ├── calculations/  # Calc defs
│   └── materials/     # Material properties
└── designs/           # Specific USAGES (instances)
    └── {design}/      # Your design configurations
```

**Key Principle**: Library = reusable definitions. Designs = specific instances.

### Project Management

```
project/
├── OVERVIEW.md              # Project status (you edit)
├── MODELING_GUIDE.md        # SysML reference (static)
├── MODELING_PROCESS.md      # MBSE methodology (static)
├── backlog/
│   └── BACKLOG.md           # Work items (/backlog manages)
├── active/                  # Current work (commands manage)
├── completed/               # Archived work
└── research/                # Research documents
```

---

## SysML Quick Reference

```sysml
// Definition (in library/) - Reusable template
part def 'Component Name' {
    doc /* Description with source citation */
    attribute param : Real;
}

// Usage (in designs/) - Specific instance
part my_component : 'Component Name' {
    :>> param = 42.0;
}
```

**Naming Conventions:**
- Definitions: Title Case (`part def 'Toroidal Field Coil'`)
- Usages: snake_case (`part tf_coil`)
- Files: snake_case.sysml

---

## Resources

- [MBSE Workflow](project/MODELING_PROCESS.md)
- [SysML Patterns](project/MODELING_GUIDE.md)
- [Domain Sources](SOURCE_INDEX.md)
- [Project Status](project/OVERVIEW.md)
- [Work Items](project/backlog/BACKLOG.md)
