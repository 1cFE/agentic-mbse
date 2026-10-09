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

This installs all 15 modeling workflows and ten supporting skills for Claude Code and Codex:

- `.agents/skills/<name>/`: shared bundles, including scripts and reference files.
- `.claude/skills/<name>`: relative aliases to those bundles.
- `.claude/agents/` and `.codex/agents/`: five native expert roles rendered from shared instructions.
- `.claude/hooks/`: the formatter hook script, for Claude only and not activated.
- `CLAUDE.md` and `AGENTS.md`: native entry instructions, created only when absent.
- `knowledge/`, `modeling_project/`, `work/`, `data/`, and `models/`: modeling project structure.

```bash
agentic-mbse init /path/to/project --assistant both
agentic-mbse init /path/to/project --assistant codex
agentic-mbse init /path/to/project --assistant claude --link-mode copy
agentic-mbse install-commands /path/to/project --assistant both
```

The default is both assistants with relative Claude symlinks. Use `--link-mode copy` where symlinks are unavailable. `install-commands` remains the CLI entry point for installing skills and native adapters without project templates. Selecting an assistant adds or updates that integration; it does not uninstall previously installed integrations.

Invoke `/onboard` or `/spec-model` in Claude Code and `$onboard` or `$spec-model` in Codex. If `/status` opens Claude’s built-in status, ask it to use the installed modeling `status` skill. Trust the target repository in Codex before using project-configured custom roles; the installer does not modify your personal trust settings. Both clients use the same domain workflows; `.agentic-mbse/claude.md` and `.agentic-mbse/codex.md` explain native tools, delegation, questions, and external-source access. Reference-only Claude skills remain visible in Codex’s catalog.

Re-init updates unmodified managed files. Interactive installs ask about local edits; noninteractive installs preserve them. The neutral `.agentic-mbse/install.json` manifest imports legacy Claude hashes and retains skipped baselines. Owner-added skill files survive updates. Resources removed from an upstream bundle are pruned only when their saved baseline still matches; modified retired resources are preserved and reported, even with `--force`. A modified or untracked legacy command is preserved and defers its same-name Claude skill migration. Codex still discovers the shared skill, so the clients may run different versions; the installer reports both paths. Existing same-name Claude skills retain precedence. Back it up through the interactive prompt, or explicitly replace it with `--force`. Re-init over an install made by the pre-native `init --dev` needs neither: a link at `.claude/{commands,skills,agents,hooks}/<name>` whose name is shipped and whose absolute target is that name inside an agentic-mbse checkout's `claude/` folder is replaced by the native install, and the report lists it under "Adopted" with its old target. Any other link, file or directory keeps the rule above. Existing assistant entry files and setting values are preserved even under `--force`; missing Codex role registrations are appended without replacing existing roles or comments. Workflows load their runtime adapter directly.

Development installs (`--dev`) link individual skill resources and templates to the source checkout. Native roles are rendered with resolved documentation paths. Normal installs copy shared resources and remain usable after moving the target project; expert documentation paths still refer to the installed package location. Re-init after relocating that package.

The installer leaves hook activation, MCP server configuration, and extraction-provider selection to existing setup. Codex reference-reader sandboxes prevent writes; they do not reproduce Claude’s tool allowlists. Native discovery is tested on Linux; full modeling and nested orchestration need behavioral smoke tests in the client configuration you deploy.

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

Learnings are stored in `work/learnings/RAW_LEARNINGS.md` for later review and formalization into documentation.

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

See `.modeling_pm/backlog/epic_documentation-discoverability.md` for full documentation of the indexing approach.
