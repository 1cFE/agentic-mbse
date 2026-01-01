# Source Index Guide

The Source Index is a markdown file (`SOURCE_INDEX.md`) that tells MBSE commands where to find domain knowledge for research and validation.

## Purpose

Instead of hardcoding references (like "PyFECONS at /path/..."), commands read the Source Index to discover what sources are available. This makes commands domain-agnostic while maintaining the same research and validation workflows.

## File Format

```markdown
# Source Index

## Primary Sources

### {Source Name}
- **Type**: {codebase | documentation | database | reference}
- **Location**: {path or URL}
- **Use for**: {what questions it answers}
- **Validation**: {how used for validation, or "N/A"}
```

## Source Types

| Type | Description | How Commands Use It |
|------|-------------|---------------------|
| `codebase` | Code repository | Launch Explore agents to analyze |
| `documentation` | PDF, markdown, text files | Read/search for relevant sections |
| `database` | API or database endpoint | Query for data (future) |
| `reference` | Books, papers, standards | Note for citations, don't deep-analyze |

## Field Details

### Type
The category of source. Determines how commands interact with it.

### Location
Path or URL to the source:
- Absolute paths: `/home/user/reference-code`
- Relative paths: `data/documents/spec.pdf`
- URLs: `https://docs.example.com/api`

### Use for
Free-text description of what questions this source can answer:
- "Physics calculations (power balance, confinement)"
- "Material properties and thermal limits"
- "Design constraints and safety margins"

### Validation
Describes how the source is used for baseline validation:
- "Compare model outputs against calculations in PowerBalance.py"
- "Verify parameters match DefineInputs.py values"
- "N/A" for reference-only sources

## Command Behavior

### When Index Exists with Sources

1. Commands read `SOURCE_INDEX.md` at startup
2. For research stages:
   - Codebase sources -> Explore agents launched
   - Documentation sources -> Files searched/read
3. For validation stages:
   - Sources with Validation entry -> Baseline comparison run
   - Sources without Validation -> Skipped for comparison

### When Index is Empty or Missing

1. Commands create template if missing
2. Ask user: "No primary sources configured. What references should I use?"
3. Proceed with user-provided references or web search
4. Optionally offer to add references to index

### When Index is Malformed

1. Commands parse what's possible
2. Warn about unparseable sections
3. Continue with partial data
4. Never fail silently

## Examples

### Fusion Reactor TEA (fusion-tea)

```markdown
# Source Index

## Primary Sources

### PyFECONS Library
- **Type**: codebase
- **Location**: /home/reid/PyFECONS
- **Use for**: Physics calculations (power balance, confinement, breeding), parameter extraction, formula verification
- **Validation**: Compare SysML model outputs against PyFECONS calculations for CATF MFE design

### ITER Physics Basis
- **Type**: documentation
- **Location**: data/documents/iter_physics_basis_1999.pdf
- **Use for**: Scaling laws, physics foundations, confinement theory
- **Validation**: N/A (reference only)
```

### Satellite TEA (hypothetical)

```markdown
# Source Index

## Primary Sources

### STK Reference Model
- **Type**: codebase
- **Location**: ~/satellite-reference/stk-model/
- **Use for**: Orbital mechanics, power budget calculations, thermal analysis
- **Validation**: Compare against STK simulation outputs

### NASA SmallSat Design Guide
- **Type**: documentation
- **Location**: data/documents/nasa_small_sat_design.pdf
- **Use for**: Subsystem sizing, mass budgets, power requirements
- **Validation**: N/A
```

### New Project (no sources yet)

```markdown
# Source Index

## Primary Sources

(No primary sources configured yet - commands will ask for references as needed)
```

## Best Practices

1. **Start minimal**: Don't over-engineer the index. Add sources as you discover them.
2. **Be specific in "Use for"**: Help commands know which source to use for which question.
3. **Mark validation sources clearly**: Commands only run baseline comparisons for sources with explicit Validation entries.
4. **Use absolute paths for reliability**: Relative paths are resolved from project root.
5. **Keep index in version control**: It documents your domain knowledge sources.
