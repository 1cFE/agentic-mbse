# Active Work

This folder contains work-in-progress item folders.

## Structure

```
active/
├── README.md           # This file
└── {item_name}/        # One folder per active work item
    ├── spec.md         # What needs to be done
    ├── design.md       # How to do it
    ├── plan.md         # Phased implementation plan
    └── [deliverables]  # Work products
```

## Starting a Work Item

1. Create folder: `mkdir {item_name}`
2. Create `spec.md` using `/spec` command or manually
3. Create `design.md` using `/design` command
4. Create `plan.md` with phased breakdown
5. Update `../CURRENT_WORK.md`

## During Work

1. Follow phases in `plan.md`
2. Check off completed tasks
3. Add notes and decisions

## Completing a Work Item

1. Ensure all deliverables exist
2. Validate success criteria met
3. Move folder to `../completed/` with date prefix
4. Update `../CURRENT_WORK.md`
5. Update epic in `../backlog/`

## Naming Convention

Use descriptive, lowercase names with underscores:
- `user_auth_backend`
- `api_integration`
- `performance_optimization`

Avoid generic names like `task1` or `work`.
