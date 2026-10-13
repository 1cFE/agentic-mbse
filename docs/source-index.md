# Source Index Guide

The Source Index is a markdown file (`knowledge/SOURCE_INDEX.md`) that tells MBSE commands where to find domain knowledge for research and validation.

## Purpose

Instead of hardcoding references (like "PyFECONS at /path/..."), commands read the Source Index to discover what sources are available. This makes commands domain-agnostic while maintaining the same research and validation workflows.

## File Format

The index holds two shapes of entry under `## Primary Sources`: hand-curated entries, which point at a source kept elsewhere, and registered entries, which the registry wrote for a source it captured.

```markdown
# Source Index

## Primary Sources

### {Source Name}
- **Type**: {codebase | documentation | database | reference}
- **Location**: {path or URL}
- **Use for**: {what questions it answers}
- **Validation**: {how used for validation, or "N/A"}

### {Registered Source Title}
- **Type**: {url | local_pdf}
- **Location**: knowledge/sources/{slug}/
- **Use for**: {what it establishes, and which question it serves}
- **Validation**: {how a reader checks its numbers against it}
- **Caveat**: {what limits its authority}

#### Extended Metadata
- **Source URL**: {url}
- **Source ID**: {SHA-256 of the source as fetched}
- **Raw SHA256**: {the same digest}
- **Raw Artifact SHA256**: {SHA-256 of the stored raw copy}
- **Extracted Path**: knowledge/sources/{slug}/
- **Extract SHA256**: {SHA-256 of the extraction}
- **Date Added**: {YYYY-MM-DD}

## How This File Is Used
```

Neither shape is written by hand. `/manage-sources` adds and removes both through `agentic-mbse research`, which takes the registry's lock for every write. A registered entry goes in just before `## How This File Is Used` (or `## How Sources Are Used`), and a local PDF's entry has **Origin Path** where a URL's has **Source URL**. Anything inside an HTML comment is not an entry.

## Source Types

**Hand-curated types.** Added and removed with `/manage-sources` (`agentic-mbse research add-entry`, `remove-entry`). Location is anywhere except `knowledge/sources/`.

| Type | Description | How Commands Use It |
|---|---|---|
| `codebase` | Code repository | Launch Explore agents to analyze |
| `documentation` | PDF, markdown or text files kept outside `knowledge/sources/` | Read/search for relevant sections |
| `database` | API or database endpoint | Query for data (future) |
| `reference` | Books, papers, standards that are not captured | Note for citations, don't deep-analyze |

**Registered types.** Written and removed only by `agentic-mbse research register` and `retire`. Location is always `knowledge/sources/<slug>/`, backed by a `MANIFEST.jsonl` row.

| Type | Description | How Commands Use It |
|---|---|---|
| `url` | A web page or online PDF, captured with its raw copy and hashes | Read `output.md` under Location; cite the Location; weigh the Caveat |
| `local_pdf` | A PDF from this machine, captured with its raw copy and hashes | Same as `url` |

A registered entry also carries **Caveat** and an `#### Extended Metadata` block (origin, Source ID, hashes, date). An unattended batch caller registers entries of type `documentation` with empty Use for and Validation; they are registered all the same. `agentic-mbse research sources` lists every entry labelled registered or hand-curated.

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

### Caveat
Registered entries only. What limits the source's authority: a preprint, a vendor page, a superseded edition.

## Command Behavior

### When Index Exists with Sources

1. Commands read `knowledge/SOURCE_INDEX.md` at startup
2. For research stages:
   - Codebase sources -> Explore agents launched
   - Documentation sources -> Files searched/read
3. For validation stages:
   - Sources with Validation entry -> Baseline comparison run
   - Sources without Validation -> Skipped for comparison

### When Index is Empty or Missing

1. `agentic-mbse init` creates the index if it is missing; commands do not write it
2. Ask user: "No primary sources configured. What references should I use?"
3. Proceed with user-provided references or web search
4. Optionally offer to add the references through `/manage-sources`

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
