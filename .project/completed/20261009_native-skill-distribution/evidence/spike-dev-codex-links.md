# Spike: which link shapes Codex lists (the `--dev` gap)

**Date:** 2026-10-09. Run by the orchestrator at the owner's request, after audit-F1 / B1. Codex `0.160.0`, Claude Code `2.1.296`. No model turns and no credentials: both tools were asked for their skill list (`skills/list` for Codex, the `initialize` control request for Claude), each with a fresh config home.

## Answer

Codex 0.160.0 does not list a skill whose `SKILL.md` is a file link, wherever the link points. It does list a skill whose folder is a link, wherever the folder link points: absolute or relative, inside or outside the project, and through a chain of folder links. Claude Code lists every shape tested.

So `--dev` works for both tools if each `.agents/skills/<n>` is one folder link to `<checkout>/skills/<n>`, instead of a real folder of per-file links. Claude's `.claude/skills/<n>` alias can stay as it is.

## Codex: every shape in one scratch project (`codex-shapes.json`, script `codex_shapes.py`)

| Shape of `.agents/skills/<n>` | Listed |
|---|---|
| real folder, real `SKILL.md` (control) | yes |
| folder link, relative, to a real folder in `.claude/skills/` (fusion-tea's own shape) | yes |
| `SKILL.md` file link, absolute, outside the project (today's `--dev`) | no |
| `SKILL.md` file link, relative, outside the project | no |
| `SKILL.md` file link, absolute, to a real file in `.claude/skills/` | no |
| `SKILL.md` file link, relative, to a real file in `.claude/skills/` | no |
| folder link, absolute, outside the project | yes |
| folder link, relative, outside the project | yes |
| folder link, absolute, to a real folder in `.claude/skills/` | yes |
| folder link to `.claude/skills/<n>`, which is itself an absolute folder link outside | yes |
| folder link to `.claude/skills/<n>` (real folder) whose `SKILL.md` is a file link outside | no |

Codex reported no errors for the skipped shapes; it leaves them out silently. The cause is not visible from outside, but all five file-link variants behave the same.

## Claude Code (`claude-shapes.json`, script `claude_shapes.py`)

| Shape of `.claude/skills/<n>` | Listed |
|---|---|
| alias to `.agents/skills/<n>`, a real folder whose `SKILL.md` is a file link out (today's `--dev`) | yes |
| alias to `.agents/skills/<n>`, which is an absolute folder link out (proposed `--dev`) | yes |
| absolute folder link out (`main`'s old `--dev` shape) | yes |
| real folder (control) | yes |

## End to end (`e2e-dev-today.json`, `e2e-dev-folder-links.json`)

1. `uv run agentic-mbse init --dev <scratch>` from `nsd-integration`, then `.project/active/native-skills/discovery_probe.py`: Codex 0, Claude 18, roles 5 (the B1 result).
2. Each `.agents/skills/<n>` folder replaced by hand with one absolute folder link to `/home/reid/1cfe/agentic-mbse-nsd/skills/<n>`; Claude's aliases untouched. The probe again: Codex 25, Claude 18, roles 5, no errors, all probe assertions pass.

The worktree's `git status` was clean after both runs.

## What a fix would change

- Under `--dev`, install each bundle as one folder link instead of `copy_tree` with per-file links (`installation.py:385`, which calls `write` per file at `:171-173`). `Installer.alias` (`:232-264`) already does this for Claude: it replaces a real folder only when every file in it is installer-owned, and records one `link:` entry in the manifest.
- A file someone adds inside a linked bundle lands in the checkout. Under `--dev` that is the developer's own checkout.
- The `--dev` tests that pin per-file absolute links (for example `tests/test_cli.py:418-426`, `tests/test_installation.py:178-181`) would pin the folder link instead, and the Codex warning added for B1 would go.
- The fusion-tea `--dev` row in the runbook's step 3 table would need a re-rehearsal.
