# Implementation Plan: Update fusion-tea to Post-D4.5

**Status:** Draft
**Created:** 2026-02-02
**Last Updated:** 2026-02-02

## Source Context

- **Epic**: `.project/backlog/epic_architecture-pm-engine.md` (EPIC-ARCH-004)
- **Prior migration spec**: `.project/active/fusion-tea-migration/spec.md` (D1.6, completed)
- **Architecture concept**: `.project/concepts/architecture-redesign/`

## Situation Analysis

fusion-tea was migrated to the 4-directory architecture during Epic 1 (D1.6). Since then, Epics 2–4 have delivered:

- **Epic 2**: 6 new skills + 2 revised (9 total)
- **Epic 3**: 9 refactored commands + 5 new commands (14 total)
- **Epic 4**: PM engine with parsers, state derivation, dashboard, 14 operations, CLI

fusion-tea uses `--dev` mode (symlinks to agentic-mbse source), so:
- **Already up-to-date via symlinks**: 9 existing commands, 5 agents, 3 existing skills, 4 tool-owned templates
- **Python CLI already available**: editable install means `agentic-mbse status` and `agentic-mbse pm` work already

**What's missing/broken**:

| Gap | Detail |
|-----|--------|
| 5 missing command symlinks | `analyze-models`, `formalize-intent`, `quick-model`, `review-model`, `status` |
| 6 missing skill symlinks | `epic-decomposition`, `model-validation`, `project-structure`, `requirements-tracking`, `source-traceability`, `sysml-conventions` |
| Work item directories lack WI-XXX prefix | PM engine expects `WI-XXX_name/` but dirs are just `name/` — causes all items to derive as `backlog` |
| BACKLOG.md epic status mismatch | Warning: epic declares `active` but derives `draft` (consequence of missing WI-XXX prefixes) |
| settings.json missing Bash permission | Commands invoke `agentic-mbse pm *` via Bash; need permission for `uv run agentic-mbse` |

## Implementation Strategy

**Phasing Rationale:** Directory rename is the highest-risk step (git history, symlink integrity). Do that first in isolation so we can validate before layering on the symlink additions. Finish with verification.

---

## Phase 1: Rename Work Item Directories to WI-XXX Format

### Goal

Make the PM engine's state derivation recognize existing work items. This is the only structural change and the riskiest step (touches git history tracking).

### Directory Rename Mapping

| Current (`work/active/`) | New (`work/active/`) | WI-ID |
|--------------------------|----------------------|-------|
| `coffee-maker-pattern-fixes/` | `WI-001_coffee-maker-pattern-fixes/` | WI-001 |
| `cost-patterns-demo/` | `WI-002_cost-patterns-demo/` | WI-002 |
| `explicit-types-redefines/` | `WI-003_explicit-types-redefines/` | WI-003 |
| `foundation-package/` | `WI-004_foundation-package/` | WI-004 |
| `power-balance-calculations/` | `WI-005_power-balance-calculations/` | WI-005 |

### Steps

- [x] `cd /home/reid/1cfe/fusion-tea`
- [x] `git mv work/active/coffee-maker-pattern-fixes work/active/WI-001_coffee-maker-pattern-fixes`
- [x] `git mv work/active/cost-patterns-demo work/active/WI-002_cost-patterns-demo`
- [x] `git mv work/active/explicit-types-redefines work/active/WI-003_explicit-types-redefines`
- [x] `git mv work/active/foundation-package work/active/WI-004_foundation-package`
- [x] `git mv work/active/power-balance-calculations work/active/WI-005_power-balance-calculations`

### Validation

- [x] `ls work/active/` — all 5 dirs have `WI-XXX_` prefix
- [x] `uv run agentic-mbse status 2>&1` — no "declared status vs derived status" warning
- [x] WI-001 and WI-002 show as `active` (not `backlog`) — confirmed `active:speccing` and `active:designing`
- [x] WI-003 shows as `failed`
- [x] WI-004 and WI-005 show as `completed`
- [x] Epic "Cost Modeling Patterns De-Risking" shows `active` (not `draft`) — `[0/2 done]`

---

## Phase 2: Add Missing Command and Skill Symlinks

### Goal

Install the 5 new commands and 6 new skills that were added in Epics 2–3.

### Option A: Re-run init (recommended)

- [x] `cd /home/reid/1cfe/fusion-tea && uv run agentic-mbse init --dev`
- [x] Verify it reports: 5 new command symlinks created, 6 new skill symlinks created — confirmed (33 symlinked total)
- [x] Verify it reports: existing symlinks preserved (no overwrites) — confirmed
- [x] Verify it reports: user-owned files skipped (settings.json, OVERVIEW.md, etc.) — confirmed (14 skipped)

### Option B: Manual symlinks (fallback if init has issues)

```bash
# Commands
ln -s /home/reid/1cfe/agentic-mbse/claude/commands/analyze-models.md .claude/commands/
ln -s /home/reid/1cfe/agentic-mbse/claude/commands/formalize-intent.md .claude/commands/
ln -s /home/reid/1cfe/agentic-mbse/claude/commands/quick-model.md .claude/commands/
ln -s /home/reid/1cfe/agentic-mbse/claude/commands/review-model.md .claude/commands/
ln -s /home/reid/1cfe/agentic-mbse/claude/commands/status.md .claude/commands/

# Skills
ln -s /home/reid/1cfe/agentic-mbse/claude/skills/epic-decomposition .claude/skills/
ln -s /home/reid/1cfe/agentic-mbse/claude/skills/model-validation .claude/skills/
ln -s /home/reid/1cfe/agentic-mbse/claude/skills/project-structure .claude/skills/
ln -s /home/reid/1cfe/agentic-mbse/claude/skills/requirements-tracking .claude/skills/
ln -s /home/reid/1cfe/agentic-mbse/claude/skills/source-traceability .claude/skills/
ln -s /home/reid/1cfe/agentic-mbse/claude/skills/sysml-conventions .claude/skills/
```

### Validation

- [x] `ls -la .claude/commands/` — 15 symlinks (14 agentic-mbse + 1 custom teax-completion.md)
- [x] `ls -la .claude/skills/` — 9 symlinks, all pointing to agentic-mbse source
- [x] `ls -la .claude/agents/` — 5 symlinks, unchanged
- [x] No broken symlinks: `find .claude/ -type l ! -exec test -e {} \; -print` returns empty

---

## Phase 3: Update settings.json Permissions

### Goal

Ensure Claude Code has Bash permission to run `agentic-mbse pm` operations, which the new commands invoke.

### Steps

- [x] Review current `.claude/settings.json`
- [x] Add Bash permission for `uv run agentic-mbse` (needed for `/status`, `/backlog`, `/research`, etc.)
- [x] Preserve existing custom permissions (teax-simkit, agentic-mbse, sysml-codegen, PyFECONS reads)

### Expected settings.json

```json
{
  "permissions": {
    "allow": [
      "Read(/home/reid/1cfe/teax/packages/teax-simkit/**)",
      "Read(/home/reid/1cfe/agentic-mbse/**)",
      "Write(/home/reid/1cfe/agentic-mbse/**)",
      "Read(/home/reid/1cfe/sysml-codegen/**)",
      "Read(/home/reid/PyFECONS/**)",
      "Bash(uv run agentic-mbse *)"
    ]
  }
}
```

### Validation

- [x] `cat .claude/settings.json` — Bash permission present
- [x] Permissions from before still present

### Note

This may not be strictly necessary if Bash permissions are granted interactively. Decide at execution time whether to add proactively or let Claude prompt for permission.

---

## Phase 4: End-to-End Verification

### Goal

Confirm the full PM engine works correctly against fusion-tea's live project data.

### Dashboard Verification

- [x] `uv run agentic-mbse status` — produces clean output with no warnings
- [x] Epic "Cost Modeling Patterns De-Risking" shows `[0/2 done]` with both items as `active`
- [x] Epic "sysml-codegen Upgrade" shows `[0/0 done]`
- [x] Standalone items: WI-003 `failed`, WI-004/WI-005 `completed`, rest `backlog`
- [x] Project Rules section shows `Total: 7`
- [x] Validation Status section shows `Total: 42`

### PM Operations Smoke Test

Pick 2-3 representative operations to verify they work against live data:

- [x] `uv run agentic-mbse pm impact-query WI-001` — ran, returned warning about WI-XXX not being DI/PR pattern (expected — impact-query expects DI-XXX or PR-XXX IDs)
- [x] `uv run agentic-mbse pm add-insight --title "Test insight" ...` — appended DI-015 to KNOWLEDGE.md
- [x] Reverted: working tree clean after `git checkout knowledge/KNOWLEDGE.md`

### Test Suite

- [x] `cd /home/reid/1cfe/fusion-tea && uv run pytest tests/ -v` — 42 passed, 1 skipped
- [x] `cd /home/reid/1cfe/agentic-mbse && uv run pytest tests/ -v` — 557 passed, 1 skipped

### Command Availability

- [ ] In a Claude Code session on fusion-tea, verify `/status`, `/quick-model`, `/review-model`, `/analyze-models`, `/formalize-intent` appear in slash command list *(manual verification — requires interactive Claude Code session in fusion-tea)*

---

## Phase 5: Commit

### Steps

- [ ] Stage all changes in fusion-tea
- [ ] Commit with message describing the update (directory renames + new components)
- [ ] Do NOT commit the smoke-test `add-insight` result (should already be reverted)

---

## Risk Management

| Risk | Mitigation |
|------|------------|
| `git mv` breaks something | All renames are in `work/active/` which is gitignored... **check first** whether work/ is gitignored. If so, git mv won't work and we use plain `mv`. |
| `init --dev` overwrites custom settings.json | Code confirms it skips user-owned files. Verified in source. |
| BACKLOG.md status fields become stale after rename | State derivation reads from file system + frontmatter, BACKLOG.md status is advisory. The warning disappearing confirms correctness. |
| Commands reference `add-to-backlog` but CLI has `add-item` | Known gap (epic doc notes this). Not a blocker for this update — address during Epic 3 command finalization. |

---

**Estimated scope**: ~15 git mv commands, 1 init run, 1 settings.json edit, verification steps.
