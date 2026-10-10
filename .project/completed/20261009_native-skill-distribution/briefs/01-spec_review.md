.project/active/native-skill-distribution/spec.md

## Brief from the orchestrator

You are reviewing the spec for `WRAP-SPLIT` Item 1 (epic: `.project/backlog/epic_wrap-split.md` § Item 1). The spec was rewritten on 2026-10-09 and committed at `b2d077b`; its product-lens ledger (`product-lens.md` beside it) is CLEAR after two fixes. This is a fresh, independent review. Write `spec-review.md` beside the spec; do not edit the spec.

### The point of the item

[AGENT] (orchestrator's reading, confirmed with the owner at Align 2026-10-09) One place to register a skill. After this item, the tool-neutral source tree (`skills/` + `agents/` + `adapters/` today) is the only installer source; it carries `main`'s current workflow text; `agentic-mbse init` installs it for Claude Code, Codex, or both. The item exists so Items 2, 4 and 5 do not land twice or in the stale place. It is not a mandate to polish the native installer further.

### Owner decisions made at Align (2026-10-09) — the spec does not carry these yet

Full record with provenance: `.project/active/native-skill-distribution/briefs/00-align.md`. In short:

- [OWNER-VERBATIM] "can we just move all of the claude commands over to skill format, and install them in the same way? how do we simplify this"
- [AGENT] (ratified by owner 2026-10-09): (1) the merge removes `claude/` with no transitional shim; (2) the installer recognizes legacy symlinks pointing into an agentic-mbse `claude/` folder as its own and replaces them with the installed skills, agents and hook, tested by installing over a copy of fusion-tea; (3) after merge the owner runs `agentic-mbse init --dev` once in fusion-tea. This resolves the spec's Open Question 3 and moves one step of the epic's integration forward to Item 1's merge, which the spec's third Non-Goal currently places after Items 1–5.
- [OWNER-VERBATIM] "to be modle-agnostic, you can rename the folder hosting skills on the agentic-mbse side". Source-side folder names are tool-neutral; `claude/hooks/ruff-format.sh` (the branch's last Claude-named source folder) moves so `claude/` disappears; renaming or regrouping `skills/`/`agents/`/`adapters/` is permitted, not required.
- Reserved gates (owner keeps these): the merge to `main` and any GitHub push; any write to fusion-tea's real tree. SC8 says "The branch is merged to `main`" — check how the spec should phrase an outcome the orchestrated run will hand to the owner rather than perform.

Your review should say where the spec must change to carry these, alongside your own findings. A revision stage will apply both together.

### Facts verified by the orchestrator (2026-10-09)

Treat these as `[AGENT, verified by orchestrator]` unless you find evidence against them; if you do, say so loudly.

1. fusion-tea's Claude side is not a native install. 31 entries in its `.claude/` (15 commands, 10 skills, 5 agents, 1 hook) are absolute symlinks into `/home/reid/1cfe/agentic-mbse/claude/`. Its Codex side is native: 25 installed directories in `.agents/skills/`, plus 5 symlinks there to fusion-tea's own `.claude/skills/` (goal, study and browser skills), tracked in `.agentic-mbse/install.json`, which has no `.claude/` entries; there is no legacy `.claude/.tool-hashes.json`. The spec's Problem bullet 3 describes only the Codex side.
2. The native branch already deleted `claude/` except `claude/hooks/ruff-format.sh` (`main` has 37 files under `claude/`; the branch has 1). Its `skills/` holds 25 bundles (31 files).
3. Legacy retirement: `installation.py:202` `retire_command` removes `.claude/commands/<name>.md` only when `permit` (`installation.py:66`) accepts it, i.e. its fingerprint (`link:<target>` for a symlink) matches the manifest or the desired value, or the owner/`--force` decides; otherwise it prints "Preserved /<name>: Claude skill migration deferred". Nothing handles legacy `.claude/skills/<name>` or `.claude/agents/<name>.md` symlinks specifically (check this).
4. `init --dev` exists on the branch: "symlink tool-owned files instead of copying (requires source checkout)" (`cli/__init__.py:761`).
5. The A–K remediation is now committed on the branch at `86921f9`. `main` is at `8f43a09`, 58 commits past the fork point `88e2489`.
6. No integration work may run in `/home/reid/1cfe/agentic-mbse` (fusion-tea reads it live). If the spec's Branch line or design questions assume otherwise, flag it.

### What you can read

You cannot read sibling repos. Read-only copies are staged for you in the gitignored `.orchestrate-logs/nsd-inputs/` (snapshot details in `SNAPSHOT.txt` there):
- `native/` — the native branch at `86921f9`: `skills/`, `agents/`, `adapters/`, `claude/`, `src/agentic_mbse/cli/`, `project_templates/`, `scripts/`, `tests/test_installation.py`, `tests/test_cli.py`, `CLAUDE.md`, `README.md`, `pyproject.toml`, `.project/active/native-skills/{plan,remediation,audit,product-lens}.md`.
- `fusion-tea/` — `harness-right-size/{report.md,installed.json}`, `.agentic-mbse/{codex.md,install.json}`, `modeling_project/{MODELING_GUIDE.md,MODELING_PROCESS.md}`, and `runtime-entries.txt` (every `.claude/` and `.agents/` entry, symlink targets shown).
- `product-lens.md` — the product-lens procedure, if your process calls for it.
`main`'s side is this checkout's working tree (`claude/`, `src/`, `project_templates/` at `b2d077b`, whose shipped content equals `main`'s). Read these; do not run or edit them.

### Where I want you to push hardest

- Whether SC2's "equal `main`'s content apart from envelope and runtime adaptation" is checkable by a script without hand judgment per file, and whether the 15 + 10 count and the "five unchanged on `main`" claim are right against the two trees.
- Whether SC5 and SC6 now cover the legacy-symlink case (fact 1, 3) and the post-merge `init --dev` step, and whether they say what "replaces" means for a symlink the owner may have made on purpose.
- Whether anything in Known Requirements is graded higher than its source supports, or carries a settled marker on an agent-grade item.
- Whether the item is still 1.5 days with the legacy-symlink adoption added, or should shed something.
