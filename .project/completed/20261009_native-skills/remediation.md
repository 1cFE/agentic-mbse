# Native skills audit remediation

Date: 2026-09-08. Branch: `native-claude-codex-skills`. Worktree: `/home/reid/1cfe/agentic-mbse-native-skills`.

[NEED] The owner requested fixes for accepted findings and an explanation of disagreements. Source: `audit.md`, F-A–F-K, and `product-lens.md`.

## Dispositions

All eleven code and documentation findings are accepted and addressed. This is an implementation response; the independent audit verdict remains unchanged pending review.

| Finding | Change | Evidence |
|---|---|---|
| F-A | Installation and `--list` share the actual `skills/*/SKILL.md` inventory. The catalog prints 25 bundle names. | CLI regression compares the catalog with a real install; rebuilt wheel lists 25 skills. |
| F-B | The summary uses `Symlinked (N):` for both normal aliases and development links. | Normal and development CLI tests; refreshed target prints `Symlinked (25):`. |
| F-C | CLAUDE.md identifies the common installer and shell wrapper. | Updated Change Coordination section. |
| F-D | CLAUDE.md distinguishes force-replaceable project documents, preserved native settings/instructions, and managed assets. | Updated ownership table matches the existing ownership tests. |
| F-E | Skill pointers use bundle paths ending in `SKILL.md`. | Corrected spec-model and plan-model pointers. |
| F-F | Preserving a legacy command reports the Claude command and Codex skill paths and possible version divergence. Existing Claude skill precedence is explicit. | Legacy-command preservation regression captures the warning; README explains recovery. |
| F-G | Re-init prunes retired resources only when their tracked baseline matches. Missing tracked files lose stale manifest entries. Modified retired files, owner additions, and redirected paths are preserved, including under `--force`. | Four lifecycle cases cover copy/symlink aliases and development/normal resources across repeated init; redirected-path test protects external files. |
| F-H | Removed unused agent and hook inventory constants. | Actual discovery still uses packaged directories. |
| F-I | Every installed bundle's first body paragraph must route to both runtime adapters, whose installed contents must match the package. | Coverage iterates all 25 installed bundles and resolves both adapter references. |
| F-J | Covered all five prompt choices, invalid-input retry, backup/overwrite decisions, and skip-all/overwrite-all persistence within one run. | Prompt tests and two-file installer decision tests verify callbacks, bytes, backups, and saved baselines. |
| F-K | The installer owns its action dictionary; init takes references to its lists instead of replacing the dictionary. | CLI and installer regressions exercise shared reporting, including the new removal action. |

## Pushback

[AGENT] A separate retroactive `spec.md` is unnecessary. The project rules permit an ad hoc requirements document, and `plan.md` already records requirements and their provenance. The audit is correct that the detailed implementation choices are agent-authored. They retain their existing grades; this remediation does not make them owner-originated or independently certified. For F-K, retaining installer ownership fixes the coupling without adding a constructor parameter for the action dictionary.

## Validation

- Full suite: 1,944 passed, one skipped, five deselected. Final focused rerun: 115 passed.
- Changed-file Ruff and formatting passed. Targeted mypy passed for both changed source modules. Repository-wide pre-existing lint/type debt remains outside this change.
- Rebuilt wheel: `/tmp/mbse-audit-dist/agentic_mbse-0.1.3-py3-none-any.whl`, SHA256 `544c3a8805cfed8e841221ec3767fb2c451ab1fdda55cb2a8f1faeb729cb1f42`.
- Installed that wheel into `/tmp/mbse-audit-wheel` and refreshed `/home/reid/agentic-mbse-target` with normal `init --assistant both`. Verified 25 shared bundles, 25 resolving relative Claude aliases, and five Codex role files with matching config registrations.
- Live discovery passed with Claude Code 2.1.263 and Codex CLI 0.153.4: 18 invocable Claude entries, five Claude expert roles, 25 Codex skills, no discovery errors. Evidence: `remediation-discovery.json`.
- Full modeling execution, cross-platform behavior, and the other runtime limits in `validation.md` remain unverified. The native nested-role probe was not repeated because role definitions and adapters did not change.

Reproduce the suite from this worktree with the main checkout's licensed environment: `UV_CACHE_DIR=/tmp/mbse-uv-cache UV_NO_SYNC=true UV_OFFLINE=true UV_PROJECT_ENVIRONMENT=/home/reid/1cfe/agentic-mbse/.venv PYTHONPATH=$PWD/src uv run --project /home/reid/1cfe/agentic-mbse --env-file /home/reid/1cfe/agentic-mbse/.env --no-sync pytest tests/ -q`. Discovery: `python3 .project/active/native-skills/discovery_probe.py /home/reid/agentic-mbse-target --output /tmp/mbse-remediation-discovery.json`.
