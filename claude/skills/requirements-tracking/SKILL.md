---
name: requirements-tracking
description: >
  Use when asking about "requirement", "PR-XXX", "MR-XXX", "project rule", "modeling rule",
  "compliance", "enforcement", "promote requirement", "REQUIREMENTS.md", "two-tier",
  "MR-XXX to PR-XXX", "EARS format", "validation method", "design review",
  or when deciding how to write, enforce, or promote modeling requirements.
  Provides the two-tier requirements structure, PR-XXX format, and promotion path.
allowed-tools: Read, Grep, Glob
user-invocable: false
---

# Requirements Tracking

Two-tier requirements structure, PR-XXX format, promotion path, and enforcement methods.

## Core Principle

Modeling requirements exist at two tiers: tool-owned baseline rules (MODELING_GUIDE.md) that apply to all projects, and user-owned extensions (REQUIREMENTS.md) that capture project-specific rules. Per-feature MR-XXX requirements are ephemeral — only significant, durable ones are promoted to project-wide PR-XXX entries.

## When to Reference

- `/spec-model` — writing per-feature MR-XXX requirements
- `/design-model` — checking compliance against PR-XXX rules
- `/implement-model` — enforcing requirements during implementation, promoting MR-XXX → PR-XXX
- `/audit-models` — verifying compliance across features
- `/backlog` — understanding requirement-linked success criteria

## Two-Tier Requirements

| Tier | File | Owner | Contains | Stability |
|------|------|-------|----------|-----------|
| **Baseline** | `modeling_project/MODELING_GUIDE.md` | Tool (updated by `agentic-mbse init`) | Universal SysML modeling rules | Stable across versions |
| **Extensions** | `modeling_project/REQUIREMENTS.md` | User | Project-specific rules (PR-XXX) | Grows slowly, deliberately |

**What belongs in MODELING_GUIDE.md**: Rules correct for all SysML v2 projects. Example: "calc defs go in library/, not in designs/"

**What belongs in REQUIREMENTS.md**: Rules specific to this project's goals. Example: "all costed components must expose capital_cost"

## PR-XXX Entity Format

| Column | Description | Example |
|--------|-------------|---------|
| ID | Sequential identifier | PR-001 |
| Requirement | EARS format statement | All costed components SHALL expose capital_cost |
| Source | Goal or insight that motivates it | G-001 (Cost traceability) |
| Enforcement | How compliance is checked | Design review + validation rule |
| Validation Method | Specific mechanism | AST check: `:>` 'Costed Component' has cost attributes |

```markdown
| ID | Requirement | Source | Enforcement | Validation Method |
|----|-------------|--------|-------------|-------------------|
| PR-001 | All costed components SHALL expose capital_cost, raw_material_cost | G-001 (Cost traceability) | Design review + validation rule | AST check |
| PR-002 | All calc defs SHALL cite source file:line in doc comment | G-003 (Source verification) | Validation Level 6 | Doc comment parser |
| PR-003 | Intermediate cost values SHALL use EXPOSE pattern | AQ-001 (Cost breakdown visibility) | Design review | Pattern check in audit |
```

## Requirement Sub-Types

| Sub-type | Description | Example |
|----------|-------------|---------|
| **Modeling patterns** | Required SysML idioms for this project | Costed Component interface, EXPOSE pattern |
| **Structural rules** | Package organization, imports | Unidirectional imports; calc defs in library/ |
| **Documentation rules** | What elements must document | Doc comments with Source, Reference, Last Updated |
| **Enforcement rules** | Machine-checkable constraints | Validation rules for cost attribute presence |
| **Naming conventions** | Standardized element names | `cost_model` as standard calc usage name |
| **Domain requirements** | Promoted from per-feature specs | "Power balance must account for recirculating power fraction" |

## Promotion Path: MR-XXX to PR-XXX

| Aspect | MR-XXX (per-feature) | PR-XXX (project-wide) |
|--------|---------------------|----------------------|
| **Scope** | One work item | Entire project |
| **Location** | `work/active/WI-XXX_{name}/spec.md` | `modeling_project/REQUIREMENTS.md` |
| **Lifetime** | Ephemeral — archived with work item | Durable — outlives work items |
| **Created by** | `/spec-model` | Promoted from MR-XXX during `/implement-model` |
| **Tracking** | Not tracked at project level | Tracked, compliance-checked |

**Promotion criteria** — promote an MR-XXX to PR-XXX when it is:
- **Durable**: Will apply to future work items, not just this one
- **Project-wide**: Constrains all modeling work, not just one feature
- **Worth tracking**: The cost of non-compliance is high enough to justify enforcement

The `trace-element` AP-7 script handles mechanical promotion: assigns PR-XXX ID, enforces format, validates source references.

## Enforcement Methods

| Method | Description | Example |
|--------|-------------|---------|
| **Validation rule** | Machine-checkable via `agentic-mbse validate` | Level 6 checks doc comment presence |
| **Design review** | Human-checked during `/review-model` or `/audit-models` | EXPOSE pattern usage review |
| **Regression test** | pytest test that verifies compliance | `test_costed_components_have_cost_attributes` |

Each PR-XXX specifies both **criteria** (what constitutes compliance) and **method** (how to check it). This makes requirements enforceable rather than aspirational.

## Compliance Checking

Commands read `modeling_project/REQUIREMENTS.md` before executing:

| Command | How It Uses Requirements |
|---------|------------------------|
| `/design-model` | Checks proposed design against PR-XXX rules |
| `/implement-model` | Enforces rules during implementation; promotes MR-XXX |
| `/audit-models` | Verifies compliance across all features |
| `/review-model` | Checks design against project rules |

## EARS Format Reference

Write requirements using the EARS (Easy Approach to Requirements Syntax) pattern:

```
The model SHALL [action] [object] [condition].
```

**Examples**:
- "All costed components SHALL expose capital_cost and raw_material_cost attributes."
- "All calc defs SHALL include doc comments with Source and Reference fields."
- "Design files SHALL NOT contain calc def declarations."

## Anti-Patterns

| Instead of | Do |
|------------|-----|
| Promoting every MR-XXX to PR-XXX | Only promote durable, project-wide requirements |
| Aspirational requirements without enforcement methods | Specify both criteria and method for each PR-XXX |
| Tracking per-feature MR-XXX at project level | MR-XXX stays in spec.md; only PR-XXX in REQUIREMENTS.md |
| Writing vague requirements ("model should be good") | Use EARS format with specific, measurable criteria |
| Editing MODELING_GUIDE.md for project rules | Project-specific rules go in REQUIREMENTS.md |
| Skipping Source column in PR-XXX | Every requirement traces to a G-XXX goal or DI-XXX insight |

## Related Skills

- For the DI-XXX → PR-XXX traceability chain, see the **source-traceability** skill.
- For epic-level success criteria that reference PR-XXX, see the **epic-decomposition** skill.
