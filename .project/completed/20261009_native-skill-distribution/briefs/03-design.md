.project/active/native-skill-distribution/spec.md

## Brief from the orchestrator

Design `WRAP-SPLIT` Item 1 from the revised spec (`spec.md`, revised after `spec-review.md`; Align decisions in `briefs/00-align.md`). Write `design.md` beside the spec.

### The point, and the bar

[AGENT] (orchestrator's reading, confirmed with the owner at Align 2026-10-09) One place to register a skill: after this item, the tool-neutral source tree is the only installer source, it carries `main`'s current text, and `agentic-mbse init` installs it the same way for Claude Code and Codex. Hold that point against every choice. The owner asked to simplify ("how do we simplify this", `briefs/00-align.md:19`).

What I will hold the design to:
- **Simplicity over machinery.** Prefer deleting code to adding it. The installer already has an ownership model (`permit`, fingerprints, manifest); legacy adoption should be a small, well-named extension of it, not a parallel mechanism. Name what you remove as well as what you add.
- **Clean architecture in the result.** After this item a maintainer should find one inventory (the source tree), one installer path, and installer code whose responsibilities are obvious. If the branch's installer has accreted awkward shapes (the `claude/`-keyed source-checkout test, hook discovery under `claude/hooks`, `retire_command` gating alias creation), fix the shape rather than patch around it — within this item's scope.
- **Mechanical, auditable content reconciliation.** Taking `main`'s bodies and applying the envelope must be a scripted transform plus a short reviewed adaptation list (SC2), not 25 hand edits. The same script or a sibling should produce the SC2 check.
- **Tests that pin behaviour, not inventories.** SC5 forbids hand-maintained lists; tests should derive the inventory from the tree and assert properties.

### Decisions design owns (spec Open Questions)

Bring the branch onto `main` (rebase vs merge, in a worktree); how to apply the envelope; how the SC2 check is built and where the adaptation list lives; how legacy links are recognized once `claude/` is gone; where the workflow-vs-supporting classification lives and whether a deletion guard exists; where the hook moves (owner permission: tool-neutral source folder names; renaming `skills/`/`agents/`/`adapters/` allowed, not required); which fusion-tea-owned file receives each target-owned passage (SC9); how the SC11 audit is bounded. Record each as a decision with the rejected alternative in one line.

Not yours: the post-merge install mode (parked for the owner; the design must make both modes work and the rehearsal must report both).

### Facts verified by the orchestrator (2026-10-09)

1. **Overlap since the fork** (`88e2489`), precomputed in `.orchestrate-logs/nsd-inputs/`:
   - `fork-to-main.names` (120 paths) and `fork-to-branch.names` (73 paths): `git diff --name-status` from the fork to `main` (`8f43a09`) and to the branch (`86921f9`).
   - `changed-on-both.txt` (14 paths). Outside `.project/`, only four: `claude/commands/orchestrate-modeling.md` (branch moved it to `skills/`, `main` edited it), `project_templates/MODELING_GUIDE.md.template`, `project_templates/MODELING_PROCESS.md.template`, `tests/test_modeling_command_contracts.py`. The branch's other moves (`claude/commands/*.md` → `skills/*/SKILL.md`) collide with `main`'s edits to the old paths through rename detection, which the branch's reflow weakens.
   - `fork-to-main.shipped.diff` (shipped and installer paths only) and `fork-to-branch.diff` (everything).
   - `main`'s other changes (e.g. `src/agentic_mbse/pm/*`, `validation/*`) do not touch branch files.
2. fusion-tea pins agentic-mbse in two places: `pyproject.toml:36` (`[tool.uv.sources]`, `rev = "c37ff53…"`) and `uv.lock`. Project memory: re-locking fails under uv 0.10, so the pin moves by hand-editing both and running `uv sync --frozen`. The runbook (SC10) should name both files.
3. fusion-tea `.gitignore:17-33` holds an old dev-mode block (ignores `.claude/{commands,agents,skills,hooks}` with whitelist lines for its own `manage-concept`, `research-acquire`, and five skills, plus the four tool-owned templates). Its Codex install (`.agents/skills/*`, `.agentic-mbse/*`) is tracked in git.
4. [Not independently verified] The native installer's own message (native `installation.py:209-213`) says a same-name Claude skill takes precedence over a legacy `.claude/commands/<name>.md`. So a legacy entry left beside an installed alias is at best shadowed and at worst dangling; either way it is clutter SC8 removes.
5. Stage agents cannot read sibling repos. Read-only copies: `.orchestrate-logs/nsd-inputs/native/` (branch at `86921f9`) and `.orchestrate-logs/nsd-inputs/fusion-tea/` (at `403716ee3`, with `runtime-entries.txt`). `main`'s side is this checkout (shipped content identical to `main`). Do not run or edit the inputs.

### Where implementation will run

[HARD] Not in `/home/reid/1cfe/agentic-mbse` (fusion-tea reads its `claude/` live). The implement stage will run in a separate worktree: either the existing native worktree (`/home/reid/1cfe/agentic-mbse-native-skills`, branch `native-claude-codex-skills`) or a fresh worktree on a new integration branch. Pick one in the design and say why; the planning artifacts on `wrap-split` (this item's spec, design, plan, briefs, the epic) must be present in that worktree before implement starts, so state how they get there (e.g. the integration brings `wrap-split` in).

### Output

`design.md` with decisions (each with rejected alternative and reasoning), the file-level change list, the content-reconciliation procedure, the legacy-adoption rule as code-level behaviour, the test strategy mapped to SC1–SC12, and risks. End with `ARTIFACT: .project/active/native-skill-distribution/design.md`. If a premise in the spec turns out wrong against the code, say so loudly in your final message rather than designing around it silently.
