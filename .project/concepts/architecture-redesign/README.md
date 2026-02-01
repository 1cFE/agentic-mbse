# Architecture Redesign

## Project Pipeline Context

This architecture redesign is for **agentic-mbse**, which is part of a four-project ecosystem for AI-assisted Model-Based Systems Engineering. Understanding the full ecosystem is essential context for architectural decisions.

### The Ecosystem

Three **infrastructure repos** form a pipeline; **application repos** (like fusion-tea) use all three to build and analyze domain models.

```
                    ┌─────────────────────────────────────────────────────┐
                    │  fusion-tea  (& future application repos)           │
                    │  SysML v2 models + domain knowledge + analysis      │
                    └──────┬──────────────────┬───────────────┬──────────┘
                           │ models/          │ generated/    │ results
                           v                  v               v
                    ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
                    │ agentic-mbse │──>│ sysml-codegen│──>│     teax     │
                    │              │   │              │   │              │
                    │ Model +      │   │ SysML v2 →   │   │ Pipeline     │
                    │ Validate     │   │ Python code  │   │ execution    │
                    └──────────────┘   └──────────────┘   └──────────────┘
                      MBSE toolkit       Code generator     Simulation engine
```

All four repos live in `~/1cfe/` and depend on each other as local editable packages. The infrastructure repos are domain-agnostic; fusion-tea is the first domain application.

### agentic-mbse — MBSE Toolkit (this repo)

Domain-agnostic toolkit providing:
- **8-level SysML v2 validation pyramid** (syntax → structural → dataflow → constraints → semantics → traceability → architecture → codegen readiness)
- **Claude Code commands** for guided modeling workflows (`/spec-model`, `/design-model`, `/plan-model`, `/implement-model`, `/audit-models`, `/research`, etc.)
- **Specialist agents** for SysML v2, KerML, syside parser, and validation questions
- **Skills** extracting shared knowledge so commands stay focused
- **Project templates** bootstrapping new MBSE projects via `agentic-mbse init`
- **CLI** for validation (`agentic-mbse validate`) and project setup (`agentic-mbse init`)

Key dependency: **syside** (≥0.8.4) — SysML v2 parser from GitLab PyPI, requires `SYSIDE_LICENSE_KEY`.

### sysml-codegen — Code Generator (`~/1cfe/sysml-codegen/`)

Transforms validated SysML v2 models into executable Python code for TEAx. Alpha (v0.1.0).

**Processing pipeline**:
1. **Extraction**: Parses SysML via agentic-mbse's `SysideAdapter` — produces `CalculationDefinitionData` with inputs, outputs, constraints
2. **Analysis**: `DependencyBacktracker` traces calculation dependencies and resolves port bindings
3. **Resolution**: `graph_builder` converts analysis into a `ComputationGraph` — the single source of truth for module interconnections and execution order
4. **Generation**: Jinja2 templates render the graph into TEAx module wrappers, Pydantic schemas, pipeline YAML, implementation stencils, and test scaffolding

**Depends on**: `agentic-mbse>=0.1.0` (uses `SysideAdapter`, `AttributeInfo`, `BindingType`).
**Produces**: TEAx-compatible Python packages ready for pipeline execution.

### teax — Simulation Engine (`~/1cfe/teax/`)

Modular, type-safe pipeline framework for techno-economic analysis. Production-ready (v0.1).

**Core capabilities** (in `teax-simkit` package):
- Typed module pipeline execution with Pydantic models
- Channel-based DAG system for data routing (including field-level referencing)
- YAML-driven pipeline specifications
- Provenance tracking (module versions, config hashes, execution metadata)
- I/O system with pluggable loaders/writers (JSON, Parquet)

**Design**: Zero built-in domain modules. Domain packages (like `battery-tea-demo` or fusion-tea's generated code) provide modules via `create_registry()` functions. TEAx executes them.

**Key pattern**: Modules are `ModuleBase[InputModel, OutputModel]` with `validate_and_fill_default()` and `run()` methods. Multi-output modules route different types to different downstream consumers.

### fusion-tea — Reference Application (`~/1cfe/fusion-tea/`)

SysML v2 modeling project for LCOE (Levelized Cost of Electricity) analysis of nuclear fusion power plants. Serves as both a real project and the primary testbed for agentic-mbse.

**Domain**: Multi-concept fusion reactor cost modeling (starting with CATF MFE — Compact Advanced Tokamak). Plans for stellarators, magnetic mirrors, IFE, MIF.

**Current models**:
- `models/library/foundation/` — 13 enum defs (ReactorType, FuelType, etc.), 6 custom units, 12 material defs, CAS cost account structure
- `models/library/calculations/power_balance/` — Generic + MFE-specific power balance calcs (16 inputs, 15 outputs, 25 regression tests)

**Reference implementation**: PyFECONS (`~/PyFECONS`) — Python codebase with 37 CAS cost categories. Every fusion-tea model element cites its PyFECONS source in doc comments for traceability.

**Role in agentic-mbse development**: Patterns discovered in fusion-tea (cost aggregation, multiplicity rollup, part redefinition, conditional expressions) are backported to agentic-mbse for all future projects.

The downstream pipeline boundary (how codegen/simulation results feed back into the modeling workflow) is an open architectural concern — see [backlog.md](backlog.md) B-004.

---

## Reading Order

1. **[main.md](main.md)** — Problem, principles, open questions
2. **[information-architecture.md](information-architecture.md)** — Data models, file structure, role definitions
3. **[workflows.md](workflows.md)** — Work item lifecycle, PM engine, skills, research
4. **[components.md](components.md)** — Command/skill/agent/template catalog
5. **[backlog.md](backlog.md)** — Open items to resolve before implementation
6. **[delta-checklist.md](delta-checklist.md)** — Every change enumerated (~111 items)
7. **[implementation-plan.md](implementation-plan.md)** — Epic structure, sequencing, exit criteria, risk register

## Status

Concept phase complete. All backlog items closed. Implementation plan drafted with 4 epics and ~111 enumerated changes. See [implementation-plan.md](implementation-plan.md) for the build strategy and [delta-checklist.md](delta-checklist.md) for the exhaustive change list.

## Archive

`archive/` contains the original monolithic documents for reference:
- `unified-toolkit-architecture.md` — The original 1,127-line concept document
- `architecture-backlog.md` — The original backlog
