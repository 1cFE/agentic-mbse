# Backlog

This folder contains epic definitions and the prioritized backlog.

## Contents

- `BACKLOG.md` - Prioritized list of all epics
- `epic_*.md` - Individual epic definition files

## Usage

### Adding a New Epic

1. Copy `../epic_template.md` to `epic_[name].md`
2. Fill in the template
3. Add entry to `BACKLOG.md`
4. Decompose into items (see `../EPIC_GUIDE.md`)

### Prioritizing

Edit `BACKLOG.md` to reorder epics. Use priority levels:
- **P0**: Critical, blocking other work
- **P1**: High priority, do next
- **P2**: Medium priority
- **P3**: Low priority, nice to have

### Starting an Epic

1. Mark status as "In Progress" in `BACKLOG.md`
2. Create item folders in `../active/`
3. Update `../CURRENT_WORK.md`

### Completing an Epic

When ALL items are done:
1. Move `epic_*.md` to `../completed/` using `git mv` to preserve history
2. Update `BACKLOG.md` (mark complete)
3. Update `../completed/CHANGELOG.md`
