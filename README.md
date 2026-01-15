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

This creates:
- `.claude/commands/` - MBSE workflow commands (`/design-model`, `/implement-model`, etc.)
- `.claude/agents/` - Specialized AI agents for SysML and documentation
- `.claude/skills/` - Skills including `/record-learning` for capturing insights
- `project/` - Project management structure (backlog, active work, learnings)
- `SOURCE_INDEX.md` - Domain knowledge source configuration

### Learning Feedback Loop

During modeling sessions, capture insights and discoveries with `/record-learning`:

```
/record-learning
```

This triggers reflection on the current conversation, identifying:
- Import patterns discovered
- Syntax gotchas resolved
- Error interpretations learned
- Workarounds implemented
- Best practices identified

Learnings are stored in `project/learnings/RAW_LEARNINGS.md` for later review and formalization into documentation.

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
