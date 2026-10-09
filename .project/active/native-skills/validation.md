# Native skill installation validation

Implemented on `native-claude-codex-skills` in `/tmp/agentic-mbse-native-skills`, based on `88e2489`. The original checkout’s uncommitted research and tracking files were preserved. Research and spike evidence were copied into this branch so the implementation contract remains traceable.

## Results

- Full default suite: **1,926 passed, one skipped, five deselected**. It used the existing licensed environment and source imports from this worktree. Six pre-existing multiprocessing fork warnings remain.
- Changed Python files: Ruff lint/format passed. Targeted mypy passed for both installer modules. `git diff --check` passed.
- Lifecycle tests cover Claude/Codex/both, relative aliases/copies, owner edits across repeated init, owner additions including empty directories, legacy hash migration, untracked and modified legacy commands, forced destination-symlink replacement, redirected parents, copy/dev/link transitions, relocation, native config preservation (including symlink and inline-table cases), and idempotent Codex role registration.
- A fresh wheel contains every shared skill, agent, and adapter resource byte-for-byte and omits the retired command tree. An isolated wheel installation under `/tmp/mbse-native-wheel` provided the CLI and payload for the fake-repository install.
- Target: `/home/reid/agentic-mbse-target`. It contains 25 shared skill bundles, 25 relative Claude aliases, five Claude roles, five Codex roles with native project registration, native entry files, and modeling templates. Re-init completed successfully.
- Native discovery: Claude Code **2.1.263** reported all 18 invocable skills and five expert roles; Codex CLI **0.153.4** reported all 25 skills. Neither reported a loader error. Claude’s seven reference-only skills are intentionally absent from its invocation catalog. See `discovery-results.json`.
- Bundled PDF extraction produced the expected text from a generated one-page PDF. The debugger completed a synthetic script and captured the requested line-2 breakpoint with local `value = 2` (plus its initial line-1 stop). Both utilities also passed their help-entry checks from installed paths.
- Live Codex role checks: a process-registered `sysml-expert` read its bundled SysML index. A final trusted-profile test used root → fresh default stage → installed `syside-expert`, which read `docs/syside/api/README.md` and returned `NESTED_ROLE_OK`. See `role-results.json`.

## Findings and limits

The first native role failures were caused by an untrusted target: Codex’s configuration-layer API explicitly reported that its project config was disabled. A command-line trust override did not enable that layer. The final test used a private temporary Codex home with the fake repository trusted, then removed that home. The installer does not edit personal trust settings. The failed untrusted test does not establish that standalone role files are unsupported.

The shared bundles retain Claude’s `user-invocable` frontmatter. The generic skill-creator validator rejects this extension in 24 bundles; both actual native clients accept it. Kept catalog tests validate YAML and inventory, and native discovery validates loader acceptance. The remaining bundle passes the generic validator unchanged.

An independent instruction walkthrough confirmed fresh implementation/audit handoffs and owner-held source conflicts and archive decisions. Its unavailable close-agent operation finding was corrected by making that action conditional on host support. Its remaining standalone `syside check` contradiction predates this migration and was already identified in the research. See `skill-forward-test.md`; this is a walkthrough, not audit certification.

Full modeling execution, a complete orchestrator repair/audit loop, interactive question widgets, `/status` TUI dispatch, hook activation, MCP setup, and macOS/Windows have not been certified. Hook registration and extraction-provider changes are outside this implementation’s scope.

## Reproduction

```bash
# From the implementation worktree, with the existing environment available:
UV_CACHE_DIR=/tmp/mbse-uv-cache UV_NO_SYNC=true UV_OFFLINE=true UV_PROJECT_ENVIRONMENT=/home/reid/1cfe/agentic-mbse/.venv PYTHONPATH="$PWD/src" uv run --project /home/reid/1cfe/agentic-mbse --env-file /home/reid/1cfe/agentic-mbse/.env --no-sync pytest tests/ -q
UV_CACHE_DIR=/tmp/mbse-uv-cache uv build --wheel --out-dir /tmp/mbse-native-dist
UV_CACHE_DIR=/tmp/mbse-uv-cache uv pip install --reinstall --no-deps --target /tmp/mbse-native-wheel /tmp/mbse-native-dist/agentic_mbse-0.1.3-py3-none-any.whl
UV_CACHE_DIR=/tmp/mbse-uv-cache PYTHONPATH=/tmp/mbse-native-wheel uv run --project /home/reid/1cfe/agentic-mbse --no-sync python -c 'from agentic_mbse.cli import main; raise SystemExit(main())' init /home/reid/agentic-mbse-target --assistant both
python3 .project/active/native-skills/discovery_probe.py /home/reid/agentic-mbse-target --output /tmp/mbse-native-discovery.json
```

For the live nested check, open Codex in a trusted fake repository and ask it to spawn one fresh default stage agent, have that stage spawn the installed syside-expert to read its configured documentation index, then wait and report the actual result. It must return a blocker rather than substitute roles on failure. This test uses model turns; the discovery probe does not.
