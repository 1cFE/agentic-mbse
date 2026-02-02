---
name: source-traceability
description: >
  Use when asking about "traceability", "source", "citation", "doc comment", "SOURCE_INDEX",
  "where did this come from", "reference", "traceability matrix", "DI-XXX", "PR-XXX",
  "source type", "confidence", "authority source", "durable chain",
  or when deciding how to cite sources, write doc comments, or record traceability.
  Provides the durable traceability chain, citation patterns, and traceability matrix schema.
allowed-tools: Read, Grep, Glob
user-invocable: false
---

# Source Traceability

The durable traceability chain, citation patterns, SOURCE_INDEX format, and traceability matrix schema.

## Core Principle

Every model element traces to an authority source. Traceability is recorded during implementation as a byproduct of work, not as a separate phase. The chain uses only durable artifacts — per-work-item specs are where traceability is discovered, but durable project files are where it lives.

## When to Reference

- `/implement-model` — recording source citations in doc comments and traceability matrix
- `/design-model` — parameter extraction with source attribution
- `/spec-model` — defining traceability requirements for success criteria
- `/audit-models` — verifying traceability completeness and baseline comparison
- `/research` — domain source investigation and citation patterns
- `/manage-sources` — configuring authority sources in SOURCE_INDEX.md

## The Durable Traceability Chain

```
DI-XXX (domain insight, in KNOWLEDGE.md)
   |
   | Source column in REQUIREMENTS.md
   v
PR-XXX (promoted requirement, in REQUIREMENTS.md)
   |
   | Requirement column in traceability_matrix.csv
   v
Model element (part def, calc def, constraint)
   |
   | Source/Reference fields in doc comment
   v
Authority source (file:line in codebase, section in spec doc)
```

Each node is a durable artifact. Per-work-item spec.md files may reference these IDs but are not part of the durable chain — they are ephemeral and archived when work completes.

## SOURCE_INDEX.md Format

Location: `knowledge/SOURCE_INDEX.md`

Each source entry follows this format:

```markdown
### [Source Name]
- **Type**: codebase | documentation | database | reference
- **Location**: path or URL
- **Use For**: what questions this source answers
- **Validation**: how to verify against this source, or "N/A"
```

**Source types**:

| Type | Description | How Commands Use It |
|------|-------------|---------------------|
| `codebase` | Code repository | Launch Explore agents to analyze |
| `documentation` | PDF, markdown, text files | Read/search for relevant sections |
| `database` | API or database endpoint | Query for data |
| `reference` | Books, papers, standards | Note for citations, don't deep-analyze |

## Doc Comment Content Requirements

Every `part def`, `calc def`, and `constraint def` requires a doc comment with three fields:

| Field | What It Must Contain | Example |
|-------|---------------------|---------|
| **Source** | The authority document or codebase that justifies this element | `Reference codebase power balance module` |
| **Reference** | Specific locator within the source | `power_balance.py:94-102` |
| **Last Updated** | Date when the citation was last verified | `2026-01-28` |

For doc comment syntax and format, see the **sysml-conventions** skill.

## Citation Patterns

| Source Type | Citation Pattern | Example |
|-------------|-----------------|---------|
| Codebase | `file.py:line X-Y` or `module/file.py:function_name` | `DefineInputs.py:45-48` |
| Documentation | `Document Name, Section X.Y` | `ITER Physics Basis, Section 4.2` |
| Online | `URL (accessed YYYY-MM-DD)` | `https://example.com (accessed 2026-01-15)` |
| Standard | `Standard ID, Section/Clause` | `ISO 19514:2017, Clause 7.3` |
| Research | `knowledge/research/approved/YYYYMMDD_topic.md` | `knowledge/research/approved/20260115_thermal.md` |

**Codebase citations must include line numbers** for parameters extracted from code. This enables automated verification during audits.

## Traceability Matrix Schema

Location: `data/traceability_matrix.csv`

| Column | Description | Example |
|--------|-------------|---------|
| Element | Model element name | `ThermalSystemCostCalc` |
| File | SysML file path | `models/library/analyses/thermal_cost.sysml` |
| Type | Element kind | `calc def` |
| Knowledge | DI-XXX IDs this traces to | `DI-003, DI-012` |
| Requirement | PR-XXX IDs this satisfies | `PR-005` |
| Source_Type | Authority source kind | `codebase` |
| Source_Document | Authority source name | `ReferenceImpl` |
| Source_Location | Specific location | `thermal_cost.py:94` |
| Confidence | Assessment level | `High` |
| Assumptions | Known approximations | `Uses 2024 material costs` |
| Last_Verified | Date of last audit | `2026-01-28` |

Both `Knowledge` (DI-XXX) and `Requirement` (PR-XXX) columns may be populated. The Knowledge column enables direct impact queries when a domain insight is superseded. The Requirement column enables coverage checking.

## When to Record Traceability

Traceability is recorded **during implementation**, not after:

| When | What to Record | Where |
|------|---------------|-------|
| Writing a definition | Source and Reference in doc comment | Doc comment fields |
| Completing a model element | Element → PR-XXX and DI-XXX links | `data/traceability_matrix.csv` |
| Promoting a requirement | MR-XXX → PR-XXX with source | `modeling_project/REQUIREMENTS.md` |

The `trace-element` AP-7 script handles mechanical recording. The agent supplies content; the script enforces schema, prevents duplicates, and validates that PR-XXX and DI-XXX IDs exist.

## Confidence Assessment

| Level | Criteria |
|-------|----------|
| **High** | Direct extraction from authority source with exact values; verified by audit |
| **Medium** | Derived from authority source with interpretation or unit conversion; consistent with source |
| **Low** | Estimated, interpolated, or from secondary sources; needs verification |

## Anti-Patterns

| Instead of | Do |
|------------|-----|
| Recording traceability as a separate phase after implementation | Record during implementation — it's a byproduct of work |
| Citing "the codebase" without specifics | Cite `file.py:line X-Y` with exact locations |
| Skipping doc comments on definitions | Every def needs Source, Reference, Last Updated |
| Relying on per-work-item specs for traceability | Use durable artifacts: REQUIREMENTS.md, traceability_matrix.csv |
| Leaving Confidence blank | Assess as High/Medium/Low — enables prioritized verification |
| Omitting Last_Verified date | Always record when citation was last checked |

## Related Skills

- For doc comment syntax and format, see the **sysml-conventions** skill.
- For PR-XXX entity format and promotion path, see the **requirements-tracking** skill.
