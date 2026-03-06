# Spec: Artifact Scaffolding via PM Script

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-03-06
**Complexity:** MEDIUM
**Branch:** doc-ingest-clean

---

## Business Goals

### Why This Matters

YAML frontmatter in work item artifacts (spec.md, design.md, plan.md, review.md, epic files) is the **authoritative state** — PM scripts read it for status tracking, close operations, and backlog management. Currently, 5 commands tell the agent to manually fill in a frontmatter template (`<YYYY-MM-DD>`, `<user>`, etc.). Agents don't reliably follow these templates: they skip fields, use wrong date formats, omit required keys, or invent non-standard fields. This silently breaks downstream automation.

### Success Criteria

- [ ] Agents never manually write YAML frontmatter for work item artifacts
- [ ] All frontmatter fields are correctly populated by a script before the agent writes body content
- [ ] Existing PM operations (close-item, status parsing) continue to work with script-generated frontmatter
- [ ] Commands that already use scripts (research, backlog items, formalize-intent) are unaffected

### Priority

Medium — quality-of-life improvement that prevents a class of silent failures. No blocking dependencies.

---

## Problem Statement

### Current State

Five commands instruct the agent to manually populate YAML frontmatter:

| Command | Output File | Frontmatter Fields |
|---------|------------|-------------------|
| `spec-model` | `work/active/{WI-XXX}_{name}/spec.md` | Status, Scale, Epic, Owner, Created, Updated |
| `design-model` | `work/active/{WI-XXX}_{name}/design.md` | Status, Created, Updated, Related Artifacts |
| `plan-model` | `work/active/{WI-XXX}_{name}/plan.md` | Status, Created, Updated, Related Artifacts |
| `review-model` | `work/active/{WI-XXX}_{name}/review.md` | Verdict, Created, Related Artifacts |
| `backlog` (epic) | `work/backlog/epic-{name}.md` | Status, Priority, Goal, Created, Updated |

Each command says something like "Create the file with this YAML frontmatter:" followed by a template. The agent must fill in `<YYYY-MM-DD>`, `<user>`, `<epic name>`, etc. This is unreliable.

### Desired Outcome

A single `agentic-mbse pm create-artifact` command that:
1. Accepts artifact type and type-specific arguments
2. Creates the directory structure if needed
3. Writes the file with correctly populated frontmatter
4. Scaffolds body sections (headings with placeholder content)
5. Prints the created file path so the agent knows where to write body content

Commands change from "write this frontmatter template" to "run this script, then fill in the body sections."

---

## Scope

### In Scope

- New `pm create-artifact` subcommand with `--type` dispatch
- Five artifact types: `spec`, `design`, `plan`, `review`, `epic`
- Auto-population of: dates (from system clock), owner (from `git config user.name`), branch (from `git branch`)
- Directory creation (`mkdir -p` for the work item directory)
- Body scaffolding (section headings matching what each command currently describes as "What Good Output Looks Like")
- Updates to the 5 affected command files to use the script instead of manual frontmatter
- Tests for the new PM operation

### Out of Scope

- Changing commands that don't create frontmatter (implement-model, manage-sources, quick-model, status, formalize-intent, analyze-models, onboard)
- Changing commands that already use scripts correctly (research via `pm save-research`, backlog items via `pm add-item`)
- Modifying the frontmatter schema itself (fields stay the same)
- Adding WI-XXX assignment to this command (that's already handled by `pm add-item` which creates the backlog entry; spec-model reads the assigned ID)

### Edge Cases & Considerations

- **File already exists**: Error out with a clear message. Don't overwrite. Agent should be told to use `Edit` if the file already exists (re-runs, resuming work).
- **Missing work item directory**: For spec, the directory won't exist yet — script creates it. For design/plan/review, it should already exist (spec created it). If missing, error with guidance.
- **Missing prerequisite artifacts**: design requires spec.md to exist; plan requires design.md; review requires design.md. Script should validate prerequisites exist and error if not (the commands already check this, but defense-in-depth).
- **Epic file already exists**: Backlog command already handles re-entry ("if an epic file already exists, read it and continue refining"). Script should error; command already has the re-entry logic.

---

## Requirements

### Functional Requirements

> Requirements below are from user's request unless marked [INFERRED].

1. **FR-1**: A single `agentic-mbse pm create-artifact --type <type>` command MUST handle all 5 artifact types (spec, design, plan, review, epic).

2. **FR-2**: The command MUST auto-populate date fields (`Created`, `Updated`) from the system clock in `YYYY-MM-DD` format.

3. **FR-3**: The command MUST auto-populate the `Owner` field (spec type) from `git config user.name`.

4. **FR-4**: The command MUST create the parent directory if it does not exist (e.g., `work/active/{WI-XXX}_{name}/` for spec).

5. **FR-5**: The command MUST scaffold body sections (markdown headings) appropriate to each artifact type, not just frontmatter.

6. **FR-6**: The command MUST print the absolute or relative path of the created file to stdout so the agent can reference it.

7. **FR-7**: The command MUST NOT overwrite an existing file. If the file exists, it MUST exit with an error and a descriptive message.

8. **FR-8**: [INFERRED] For design, plan, and review types, the command SHOULD validate that prerequisite artifacts exist in the same directory (spec.md for design; design.md for plan; design.md for review) and warn if missing.

9. **FR-9**: [INFERRED] The command MUST accept type-specific arguments:
   - `spec`: `--wi-id`, `--name`, `--epic`, `--scale` (default: standard)
   - `design`: `--wi-dir` (path to existing `work/active/{WI-XXX}_{name}/`)
   - `plan`: `--wi-dir`
   - `review`: `--wi-dir`
   - `epic`: `--name`, `--priority`, `--goal`

10. **FR-10**: [INFERRED] The 5 affected command files (spec-model.md, design-model.md, plan-model.md, review-model.md, backlog.md) MUST be updated to invoke the script instead of instructing manual frontmatter creation.

### Non-Functional Requirements

- The command MUST follow the existing PM CLI patterns: `_dispatch` → `_op_*` → `operations.py` function → `OperationResult`.
- The command MUST be testable without a real git repository (mock git config).

---

## Acceptance Criteria

### Core Functionality

- [ ] `agentic-mbse pm create-artifact --type spec --wi-id WI-005 --name "my-feature" --epic "My Epic" --scale standard` creates `work/active/WI-005_my-feature/spec.md` with correct frontmatter and body scaffolding
- [ ] `agentic-mbse pm create-artifact --type design --wi-dir work/active/WI-005_my-feature` creates `design.md` with frontmatter linking to `./spec.md`
- [ ] `agentic-mbse pm create-artifact --type plan --wi-dir work/active/WI-005_my-feature` creates `plan.md` with frontmatter linking to `./spec.md` and `./design.md`
- [ ] `agentic-mbse pm create-artifact --type review --wi-dir work/active/WI-005_my-feature` creates `review.md` with frontmatter linking to `./design.md`
- [ ] `agentic-mbse pm create-artifact --type epic --name "my-epic" --priority P1 --goal G-001` creates `work/backlog/epic-my-epic.md` with correct frontmatter
- [ ] All auto-populated fields are correct (date format, git username, Related Artifacts paths)
- [ ] Running on an existing file exits with error, does not overwrite
- [ ] Missing prerequisite artifacts produce a warning (not error — agent may create them out of order intentionally)

### Quality & Integration

- [ ] Existing tests continue to pass
- [ ] New tests cover all 5 artifact types, overwrite protection, prerequisite warnings
- [ ] PM operations that parse frontmatter (close-item, status) work correctly with script-generated files

---

## Related Artifacts

- **Research:** N/A
- **Design:** `.project/active/artifact-scaffolding/design.md` (to be created)
- **Backlog:** `.project/backlog/BACKLOG.md`

---

**Next Steps:** After approval, proceed to `/_my_design`
