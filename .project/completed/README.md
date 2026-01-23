# Completed Work

Archive of completed epics and work items.

## Structure

```
completed/
├── README.md                    # This file
├── CHANGELOG.md                 # Historical record of completions
├── {YYYYMMDD}_epic_{name}.md    # Completed epic definitions
└── {YYYYMMDD}_{item}/           # Completed work item folders
    ├── spec.md
    ├── design.md
    ├── plan.md
    └── [final report]
```

## Adding Completed Work

### Work Items

When a work item is complete:

```bash
mv ../active/{item_name} ./$(date +%Y%m%d)_{item_name}
```

### Epics

When ALL items in an epic are complete:

```bash
mv ../backlog/epic_{name}.md ./$(date +%Y%m%d)_epic_{name}.md
```

Then update `CHANGELOG.md` with a completion entry.

## CHANGELOG Format

Each completion entry should include:
- Date
- Epic/Item name
- Brief summary of what was accomplished
- Key deliverables
- Duration (actual vs estimated)
- Any lessons learned

## Why Archive?

1. **Institutional memory** - Know what was done and why
2. **Reuse** - Reference past designs and decisions
3. **Metrics** - Track velocity and accuracy of estimates
4. **Audit trail** - Evidence of completed work
