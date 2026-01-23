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
2. **Update BACKLOG.md** via `/project-manage` command - reorganize, set priorities
3. **Epic decomposition** (before or after prioritization, e.g., to estimate effort):
   - Organize into **parts** if needed (logical groupings)
   - Break down into **items** with numbering (e.g., `4.2` = Part 4, Item 2)

---

### 3. Epic Execution

Iterate through items in the epic:

| Step | Action | Output |
|------|--------|--------|
| **1. Start** | Create item folder under `active/` | `active/{item_name}/` |
| **2. Spec** | Define what needs to be done | `spec.md` |
| **3. Design** | Research codebase, identify all code changes | `design.md` |
| **4. Plan** | Plan implementation in Phases, include tests | `plan.md` |
| **5. Implement** | Execute plan, one phase at a time | Code changes |
| **6. Review** | Review work (can happen at any stage) | Feedback/approval |

**As the epic progresses**: Add or insert new items as you learn more. Follow the same process for each.

---

### 4. Epic Cleanup

1. **Check** for all completed active items
2. **Move items** to `completed/`, prefixed with date stamp (e.g., `20251223_item_name/`)
3. **Move epic** to `completed/` with date stamp (e.g., `20251223_epic_name.md`)
4. **Update docs**: `CURRENT_WORK.md`, `BACKLOG.md`, and `completed/CHANGELOG.md`

---

## Key Files

| File | Purpose |
|------|---------|
| `CURRENT_WORK.md` | What's active RIGHT NOW - single source of truth |
| `backlog/BACKLOG.md` | Prioritized list of epics |
| `backlog/epic_*.md` | Individual epic definitions |

---

## Folder Structure

```
.project/
├── CURRENT_WORK.md           # Active work tracking
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

| Command | When to Use |
|---------|-------------|
| `/project-manage` | Status review, update BACKLOG, reorganize priorities |
| `/project-find` | Quick lookup of project context |
| `/spec` | Create specification for current item |
| `/design` | Research codebase, create design doc |
| `/implement` | Execute implementation plan |
| `/review` | Review work at any stage |

---

**Last Updated**: Template
