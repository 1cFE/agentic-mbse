# Project Management

This folder contains project planning, tracking, and documentation.

---

## Workflow Overview

### 1. Accumulating Backlog

**Collecting Needs**:
- **Research & Analysis**: Running research reports, web searches, collecting data to understand what needs to be done
- **During Development**: Issues identified while running/writing code
- **External PM**: Requirements from external project management systems

**Creating Epics**:
- Capture outcomes and goals
- Note known pieces of work (details come later during decomposition)

---

### 2. Prioritization

1. **User prioritizes** using their own methods
2. **Update BACKLOG.md** via `/_my_status` command - reorganize, set priorities
3. **Epic decomposition** (before or after prioritization, e.g., to estimate effort):
   - Organize into **parts** if needed (logical groupings)
   - Break down into **items** with numbering (e.g., `4.2` = Part 4, Item 2)

---

### 3. Epic Execution

Iterate through items in the epic. Each item runs the standard pipeline of `/_my_*` stages.

**For the canonical, current flow and when/how to use each stage, run `/_my_pipeline`** (installed
with claude-pack). This README does not carry its own copy of the sequence — `/_my_pipeline` is the
single source, so it can't go stale here.

**As the epic progresses**: Add or insert new items as you learn more. Follow the same process for each.

---

### 4. Epic Cleanup

1. **Check** for all completed active items
2. **Move items** to `completed/` using `git mv`, prefixed with date stamp (e.g., `git mv .project/active/item_name .project/completed/20251223_item_name`)
3. **Move epic** to `completed/` using `git mv` with date stamp (e.g., `git mv .project/backlog/epic_name.md .project/completed/20251223_epic_name.md`)
4. **Update docs**: `CURRENT_WORK.md`, `BACKLOG.md`, and `completed/CHANGELOG.md`

---

## Knowledge Homes

Four append-only registers hold durable knowledge that must survive across sessions and agents. Each has one routing question — ask it before reaching for the native memory store or any other location.

| Register | Routing question | What belongs |
|----------|-----------------|--------------|
| `adr/` | Would a future agent re-derive the wrong thing or relitigate this decision? | Decisions and the reasoning behind them. Contracts, invariants, mechanism choices. |
| `product/` | Is this an implemented promise a cold agent could miss or undo? | What the product guarantees — major use cases, public surfaces, cross-cutting contracts. |
| `execution/` | Would a future agent spend real time rediscovering this behavior? | How a component, tool, or environment actually behaves, learned by doing. |
| `feedback/` | Did the owner correct a pack prompt's output? | Wrong/Right/Learning entries, tagged by the pack target to fix upstream. |

Each register's README defines its density bar and entry format. When in doubt, read the "Where it does not go" section in `execution/README.md` — it cross-references all four registers with examples.

**The native memory store (`~/.claude/projects/.../memory/`) is not a knowledge home.** It is device-local, not git-tracked, and not owner-reviewed. If you're about to save something there, check whether it belongs in one of these registers first.

---

## Key Files

| File | Purpose |
|------|---------|
| `CURRENT_WORK.md` | Active Work and Up Next — what is in flight RIGHT NOW, and nothing else |
| `completed/CHANGELOG.md` | Newest-first record of completed work; session boot reads the newest five entries |
| `product/INDEX.md` | Generated index of implemented product promises — what the product is for (convention: `product/README.md`) |
| `adr/INDEX.md` | Generated index of load-bearing decisions (convention: `adr/README.md`) |
| `feedback/ENTRIES.md` | Append-only corrections to pack prompts, tagged by target (convention: `feedback/README.md`) |
| `execution/ENTRIES.md` | Append-only log of how this codebase and environment behave, discovered while working (convention: `execution/README.md`) |
| `TRIAGE_MEMORIES.md` | One-time instructions for sorting native memory entries into `.project/` homes |
| `backlog/BACKLOG.md` | Prioritized list of epics |
| `backlog/epic_*.md` | Individual epic definitions |

---

## Folder Structure

```
.project/
├── CURRENT_WORK.md           # Active work tracking
├── TRIAGE_MEMORIES.md        # One-time: sort native memory entries into .project/ homes
├── backlog/
│   ├── BACKLOG.md            # Prioritized epic list
│   └── epic_*.md             # Epic definitions
├── active/
│   └── {item_name}/          # Work-in-progress items
│       ├── spec.md
│       ├── design.md
│       └── plan.md
├── completed/
│   ├── {date}_{item_name}/   # Archived items
│   └── epic_*.md             # Archived epics
├── adr/                      # Decision records (append-only, script-managed)
├── product/                  # Product promise ledger (append-only, script-managed)
├── execution/                # Execution facts — how this codebase/environment behaves (append-only)
├── feedback/                 # Pack-prompt corrections for the owner to fix upstream (append-only)
├── scripts/                  # Utility scripts (adr.sh, product.sh, get-metadata.sh)
├── research/                 # Deep investigations
└── reports/                  # Status reports
```

---

## Item Numbering

Items within an epic use hierarchical numbering:
- `1`, `2`, `3` - Simple sequential items
- `4.1`, `4.2`, `4.3` - Items within Part 4
- Parts group related items logically

---

## Commands

This README does not carry a command catalog — a copy here would drift. Two live sources:

- **`/_my_pipeline`** — the canonical stage map and when to use each stage.
- **The toolkit README's Command Reference** (in the agentic-project-init repo) — one line per command, including shortcuts, modes, and project-management helpers.

---

**Last Updated**: Template
