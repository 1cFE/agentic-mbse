# Spike: Native skill installation

## Summary of Findings

Both installed clients discover shared skill directories through relative symlinks. Discovery and Python filesystem reads through the supporting-file links survive moving the fixture project. Copying the bundles works too. Codex accepts all 15 command files unchanged as `SKILL.md`, together with the ten existing skills, without loader errors. Claude exposes all 15 workflows and the three invocable supporting skills; its seven reference-only skills stay out of the command catalog. This proves installation feasibility, not full workflow parity.

Claude's catalog selects the skill when a legacy command has the same name. The five rendered Claude expert agents register. Codex custom-agent registration remains documented rather than experimentally verified: `debug prompt-input` succeeds but does not show a role catalog, so absence of role names there is inconclusive.

The separate [installer spike](installer-findings.md) confirms that local edits and symlink referents need explicit migration protection. These findings feed [the native-support research](../../research/20260907-162310_native-claude-codex-skills.md).

## Question / Goal

[AGENT] Test whether project-local relative directory symlinks expose one shared skill bundle to both installed clients, including supporting files, and survive project relocation. Discovery must be reported by each real client. The upstream owner request is research into native Claude/Codex support; the installation layouts are agent-proposed examples.

## Log

- Installed clients: Codex CLI 0.153.4 and Claude Code 2.1.263 on Linux. Read local help and the official Codex app-server protocol before probing.
- Created isolated fixture Git projects and client configuration inside this folder. The probe makes no model turns. It uses Codex app-server `initialize` then `skills/list`, and Claude's SDK control-channel `initialize` response. The latter is an observed local protocol, not a promised stable public installation API.
- Initial `uv run` failed because the default cache was read-only. Re-ran with `UV_CACHE_DIR=/tmp/mbse-uv-cache uv run --no-sync` using the existing environment. No dependency installation was needed.
- `shared-relative`: canonical `.agents/skills/mbse-probe/`, with `.claude/skills/mbse-probe -> ../../.agents/skills/mbse-probe`. Both clients reported one project sentinel.
- `relocated`: renamed the entire project, restarted discovery, and both reported the sentinel at the new project. A Python filesystem read through the Claude link still returned `MBSE_REFERENCE_SENTINEL`.
- `both-symlinked`: moved the canonical bundle to `shared/mbse-probe`, linked `.agents/skills/mbse-probe -> ../../shared/mbse-probe`, and kept the Claude alias. Both loaders followed this chain.
- `legacy-duplicate`: added a same-name `.claude/commands/mbse-probe.md` with a different description. Claude reported one project entry with the skill description, not the legacy description.
- `full-catalog`: copied every shipped command unchanged to its own `SKILL.md`, copied all ten shipped skill trees, and added per-skill Claude aliases. Codex reported 26 entries including the sentinel and zero errors. Claude reported 19 invocable entries including the sentinel. The difference is precisely the seven `user-invocable: false` reference skills. Codex's listing includes these; discovery does not establish equivalent hiding behavior.
- `copy-fallback`: replaced the Claude aliases with copies. Counts stayed 26/19, and the Python reference-file read passed.
- The sentinel includes `skills: [missing-probe-dependency]`. Neither discovery API rejects it. This proves tolerant loading, not dependency loading or invocation semantics.
- `role_probe.py`: rendered all five agents into native Claude Markdown and candidate Codex TOML files. Claude registered all five. An initial `--strict-config` attempt failed because that flag is unsupported by `codex debug`. Without it, `debug prompt-input` returned successfully but none of the role names appeared. The tool reports prompt messages, so it is insufficient evidence about the runtime's tool-schema role catalog. No unsupported-agent conclusion follows.
- Client-home overrides do not hide Codex's `$HOME/.agents/skills`; the result filter retains project skills only. Unrelated personal skill descriptions, account metadata and model catalogs are not retained in the final result files.

## Reproduction

Run from the repository root with the existing project environment and both client executables on PATH:

```bash
UV_CACHE_DIR=/tmp/mbse-uv-cache uv run --no-sync python .project/active/spike-native-skill-install/probe.py
UV_CACHE_DIR=/tmp/mbse-uv-cache uv run --no-sync python .project/active/spike-native-skill-install/role_probe.py
UV_CACHE_DIR=/tmp/mbse-uv-cache uv run --no-sync python .project/active/spike-native-skill-install/installer_probe.py
```

Scripts and results live together here. Fixture projects are temporary and removed after each run. Expected discovery counts, including the sentinel, are 1/1 for the first four cases and 26/19 for full catalog and copy fallback (Codex/Claude). `results.json`, `role-results.json`, and `installer-results.json` retain observations. The source checkout and real target installations are not modified.

## Open Questions / Follow-ups

- Discovery is confirmed on these Linux versions only. Windows, macOS, Git checkout symlink settings, live reload, and wheel installations were not tested.
- Run a native Codex custom-role spawn and an orchestrator → stage → expert smoke test before claiming end-to-end support. The current research session successfully used fresh Codex agents, but it is not a test of installed MBSE role adapters.
- Test actual user invocation for reserved command names, especially `/status`; catalog registration alone cannot establish which TUI handler wins.
- Supporting resources were read by the probe through filesystem paths, not by an agent tool under its sandbox. Agent-authorized resource access remains untested.
- Hook dispatch, question widgets, tool grants, implicit invocation policy, Docling MCP, and external-doc sandbox access require behavioral tests during implementation.
