# Component Catalog

**Parent**: [main.md](main.md) — Problem, principles, implementation plan
**Concern**: What we're building — every command, skill, agent, and template with its role

This is the inventory of all components in the redesigned toolkit. For how they interact, see → [workflows.md](workflows.md). For the data they produce and consume, see → [information-architecture.md](information-architecture.md).

---

## 1. Commands (target: 200-300 lines each)

| Command | Job | Key user decision | Skills referenced |
|---------|-----|-------------------|-------------------|
| `/spec-model` | Define WHAT to model | Scope, success criteria | project-structure, source-traceability |
| `/design-model` | Decide HOW to model | Architecture approach, interfaces, where things live | sysml-conventions, project-structure, model-validation, source-traceability |
| `/plan-model` | Organize the WORK | Phase ordering, scope per phase, risk priorities | model-validation |
| `/implement-model` | BUILD it correctly | Execution approach, deviation handling, phase approval | sysml-conventions, model-validation, project-structure |
| `/audit-models` | VERIFY models + update project docs | Audit scope, which promotions to accept | model-validation, source-traceability, requirements-tracking |
| `/research` | LEARN from external sources | Research scope, insight capture | source-traceability |
| `/quick-model` | Make a SMALL change | Change scope (guard: redirect if too big) | sysml-conventions, model-validation |
| `/review-model` | REVIEW design before implementing | Which findings to accept/skip/defer | sysml-conventions, model-validation, project-structure |
| `/analyze-models` | UNDERSTAND current model state | Analysis scope | project-structure, model-validation |
| `/status` | Understand PROJECT STATE | What to do next | epic-decomposition, requirements-tracking |
| `/backlog` | Manage WORK ITEMS | Add, prioritize, decompose, close | epic-decomposition |
| `/onboard` | SET UP a project | Initial goals, architecture sketch, sources | project-structure, source-traceability, epic-decomposition |
| `/manage-sources` | Configure SOURCES | Source additions, validation criteria | source-traceability |

---

## 2. Skills (target: <200 lines SKILL.md each)

See → [workflows.md § 1.2](workflows.md#12-skill-catalog) for the full catalog with justifications. Each skill follows the pattern:

```
claude/skills/{skill-name}/
├── SKILL.md        # Principles, key rules, when to apply (~100-200 lines)
└── references/     # Optional deep reference material (loaded on demand)
    └── *.md
```

---

## 3. Agents (unchanged; standardize references)

| Agent | Question types | When to invoke |
|-------|---------------|----------------|
| `sysmlv2-doc-analyzer` | Cross-cutting SysML v2 questions, specification lookups | Broad SysML questions, pattern recommendations |
| `kerml-expert` | KerML standard library functions, base types | Import questions, standard function signatures |
| `sysml-expert` | SysML modeling patterns, part/port/connection | Structural modeling, SysML idioms |
| `syside-expert` | syside parser API, expression evaluation | Parser errors, expression tree questions |
| `sysmlv2-validator` | Syntax validation, error interpretation | Parse failures, validation error triage |
| `python-debugger` | Python debugging | Test failures, CLI issues |

**Invocation principle**: Launch relevant agents in parallel with focused prompts. Synthesize results in main context. This produces higher recall than a single unified agent.

---

## 4. Project Templates

| Template | Ownership | New/Revised |
|----------|-----------|-------------|
| `OVERVIEW.md.template` | User-owned | Revised (add Goals Registry, Analysis Questions) |
| `ARCHITECTURE.md.template` | User-owned | **New** |
| `REQUIREMENTS.md.template` | User-owned | **New** |
| `KNOWLEDGE.md.template` | User-owned | **New** |
| `VALIDATION_MATRIX.md.template` | User-owned | **New** |
| `EPIC_GUIDE.md.template` | Tool-owned | **New** |
| `epic_template.md.template` | Tool-owned | **New** |
| `BACKLOG.md.template` | User-owned | Revised (add scale column) |
| `MODELING_GUIDE.md.template` | Tool-owned | Revised (reference/how-to material extracted to skills; what remains is pure rules) |
| `MODELING_PROCESS.md.template` | Tool-owned | Revised (reference new documents) |
