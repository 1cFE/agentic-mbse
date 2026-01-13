# agentic-mbse

Domain-agnostic MBSE toolkit for AI-assisted systems engineering.

## Installation

```bash
pip install -e .
```

## Usage

### Validate SysML Models

```bash
agentic-mbse validate models/
```

### Initialize Project

```bash
agentic-mbse init
```

## Development

```bash
pip install -e ".[dev]"
pytest tests/
```

## Maintaining Documentation Corpus

The `docs/sysmlv2/` directory contains indexed specifications and standard library files that power the documentation agents. When syside or SysML v2 specs are updated, regenerate using these scripts:

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `scripts/sync_stdlib.py` | Sync standard library from syside package | After syside upgrade |
| `scripts/generate_index.py` | Generate INDEX.md for spec documents | After extracting new PDFs |

```bash
# After upgrading syside
python scripts/sync_stdlib.py --force

# After extracting new spec PDFs to docs/sysmlv2/
python scripts/generate_index.py docs/sysmlv2/SysML_KerMLSpec/
python scripts/generate_index.py docs/sysmlv2/SysML_Spec_v2_Part1/
# ... etc for each spec directory
```

See `.project/backlog/epic_documentation-discoverability.md` for full documentation of the indexing approach.
