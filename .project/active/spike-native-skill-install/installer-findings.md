# Spike: Installer update behavior

## Summary of Findings

The existing installer does not preserve local edits across all update paths. A skipped command survives the second init but loses its stored hash; the third init overwrites it without prompting. Skills are replaced without prompting, including deletion of locally added files. The command-only forced installer follows destination symlinks and overwrites their referents. The normal hash-aware helper correctly removes the symlink before copying and preserves the referent.

For the native Claude/Codex installer design, reuse the hash-aware unlink-before-copy pattern, retain baseline hashes for skipped files, and extend explicit ownership handling to skill contents. These are agent recommendations based on the reproduced behavior, not settled owner decisions.

## Question / Goal

Does the existing installer preserve local command and skill edits across repeated updates, and does copying over a development symlink leave its source untouched? This probe serves the forthcoming native-claude-codex-skills research. It exercises the actual CLI functions in temporary directories.

## Log

- Prepared `installer_probe.py` to run three isolated cases: command modification followed by skip and another init; skill modification followed by init; and command-only forced install onto a symlink to a temporary source file. An additional helper case checks the normal hash-aware installer's unlink-before-copy behavior.
- Ran the reproduction command successfully (exit 0). The second command init prompted once and preserved the edit, but the resulting manifest omitted that command. The third init prompted zero times and restored shipped content. This confirms the map-replacement behavior at `src/agentic_mbse/cli/__init__.py:595`, `:752`, and `:967` combined with missing-hash handling at `:347`.
- The skill re-init prompted zero times, restored shipped `SKILL.md`, and removed the local note. This confirms directory replacement at `src/agentic_mbse/cli/__init__.py:471` and the skill install call at `:823`.
- Forced `cmd_install_commands` left the destination symlink intact and overwrote its temporary referent. The hash-aware helper then replaced that symlink with a regular copy while leaving its referent unchanged. These results distinguish `src/agentic_mbse/cli/__init__.py:1053` from `:431`.
- Raw observations are saved in `installer-results.json`. The summary above was written after these results were available.

## Reproduction

Run `UV_CACHE_DIR=/tmp/mbse-uv-cache uv run --no-sync python .project/active/spike-native-skill-install/installer_probe.py` from the repository root. The script prints JSON and writes `installer-results.json` beside itself. It uses temporary install destinations and temporary symlink referents, and does not modify shipped source files.

## Open Questions / Follow-ups

- This probe does not test native Claude or Codex discovery, packaging, or shell replication.
- The [native-support research](../../research/20260907-162310_native-claude-codex-skills.md) incorporates these confirmed update failures into its installation recommendation.
