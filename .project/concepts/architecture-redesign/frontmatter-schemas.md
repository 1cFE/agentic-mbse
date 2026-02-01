# YAML Frontmatter Schemas

**Parent**: [workflows.md](workflows.md) — Work item lifecycle, PM engine data model
**Concern**: Exact field definitions for every YAML frontmatter block the PM engine parses

This document is the authoritative reference for YAML frontmatter schemas across all PM-tracked files. It consolidates and formalizes the schemas sketched in [workflows.md](workflows.md) § 3.1–3.3 and § 3.6. Where this document and workflows.md disagree, this document wins — it resolves ambiguities and inconsistencies in the source material.

**Audience**: PM engine implementors (Epic 4), command authors (Epic 3), template maintainers (D1.1/D1.2).

**How the PM engine uses this**: The PM engine parses YAML frontmatter from markdown files using a generic YAML-front-matter reader, then validates each file's frontmatter against the schema defined here. On validation failure, the engine produces warnings and partial results per the AP-7 input validation guarantee (see [workflows.md](workflows.md) § 4.2).

---

## 1. Conventions

### Type Definitions

| Type | Format | Examples |
|------|--------|---------|
| `date` | `YYYY-MM-DD` (ISO 8601 date only) | `2026-02-01` |
| `string` | Unquoted YAML string (quote if it contains `: ` or starts with special chars) | `Solar+Battery SysML Model` |
| `enum` | One of the listed values, case-sensitive | `active`, `P0` |
| `path` | Relative path from the file's directory, using `./` prefix | `./spec.md`, `./design.md` |
| `id` | Uppercase prefix + hyphen + zero-padded number | `WI-001`, `G-003`, `DI-017` |

### Required vs Optional

- **Required**: Field MUST be present. PM engine reports a validation warning if missing.
- **Optional**: Field MAY be omitted. PM engine uses a default or skips the field.
- **Conditional**: Field is required only when a stated condition holds (e.g., `completed` date is required when status = `completed`).

### Path Conventions

Related Artifacts use **relative paths from the file's own directory**. Since all stage artifacts for a work item live in the same directory (`work/active/{WI-XXX}_{name}/`), paths are simply `./filename.md`.

### YAML Style

All frontmatter uses YAML block style (not flow style). Lists use `- ` prefix. Nested maps use 2-space indentation.

---

## 2. Design Decisions

### DD-1: No ID or Name in spec.md Frontmatter

**Decision**: The `ID` and `Name` fields shown in workflows.md § 3.1 are **not** part of the spec.md schema.

**Rationale**: Work item identity is derived from the directory name `{WI-XXX}_{descriptive-str}/`. Duplicating the ID and name in frontmatter creates a sync problem — the directory name is the single source of truth. The PM engine derives WI-XXX by parsing directory names in `work/active/` and `work/completed/`.

**Impact**: workflows.md § 3.1 shows `ID: WI-XXX` and `Name: [human-readable name]` in its example. Those fields are illustrative, not normative. This document supersedes that example.

### DD-2: BACKLOG.md Is the WI-XXX ID Registry

**Decision**: WI-XXX IDs are assigned in `work/BACKLOG.md` frontmatter by AP-7 scripts. BACKLOG.md is the authoritative registry of which IDs have been allocated.

**Rationale**: IDs must be unique and sequential. A central registry prevents collisions. AP-7 scripts read the highest existing ID from BACKLOG.md and increment. Work item directories reference IDs but do not define them.

### DD-3: review.md Is Not a PM-Tracked Stage

**Decision**: The PM engine does NOT use review.md for stage detection or state derivation. review.md is an optional advisory artifact within the design stage.

**Rationale**: Stage detection uses file existence: spec.md only → speccing; +design.md → designing; +plan.md → planning; implementation started → implementing. review.md sits between design and plan but does not change the stage. The PM engine may read review.md's verdict for display purposes but does not track it as a lifecycle stage.

---

## 3. Schemas

### 3.1 spec.md

The state-bearing file for a work item. The PM engine reads spec.md frontmatter as the single source of truth for work item state.

**Location**: `work/active/{WI-XXX}_{name}/spec.md`

| Field | Type | Required | Allowed Values | Description |
|-------|------|----------|---------------|-------------|
| `Status` | enum | Required | `active`, `paused`, `abandoned`, `failed`, `completed` | Work item state. The PM engine uses this to override the default "active" state derived from directory existence. |
| `Scale` | enum | Required | `standard` | Work item scale. Currently always `standard` — trivial items don't get spec.md, epics are tracked separately. |
| `Epic` | string | Optional | Any string matching an epic name in BACKLOG.md | Parent epic. Empty/omitted for standalone items. |
| `Owner` | string | Optional | Free-form string | Who is working on this. |
| `Created` | date | Required | `YYYY-MM-DD` | Date the spec was created. |
| `Updated` | date | Required | `YYYY-MM-DD` | Date of the most recent edit. |

**Example**:

```yaml
---
Status: active
Scale: standard
Epic: End-to-End Pipeline De-Risking
Owner: Reid
Created: 2026-02-01
Updated: 2026-02-03
---
```

**Notes**:
- No `ID` or `Name` field — see DD-1.
- The `Scale` field exists for forward compatibility (if other scales get spec files in the future) and for explicit self-description.

### 3.2 design.md

Stage artifact for the design phase. Contains architecture decisions and prototype validation results.

**Location**: `work/active/{WI-XXX}_{name}/design.md`

| Field | Type | Required | Allowed Values | Description |
|-------|------|----------|---------------|-------------|
| `Status` | enum | Required | `draft`, `complete` | Stage-level status (not the work item status — that's in spec.md). |
| `Created` | date | Required | `YYYY-MM-DD` | Date the design was created. |
| `Updated` | date | Required | `YYYY-MM-DD` | Date of the most recent edit. |
| `Related Artifacts` | map | Required | See sub-fields | Links to related stage files. |
| `Related Artifacts.Spec` | path | Required | `./spec.md` | Path to the work item's spec. |

**Example**:

```yaml
---
Status: draft
Created: 2026-02-02
Updated: 2026-02-04
Related Artifacts:
  Spec: ./spec.md
---
```

### 3.3 plan.md

Stage artifact for the planning phase. Contains phased implementation plan.

**Location**: `work/active/{WI-XXX}_{name}/plan.md`

| Field | Type | Required | Allowed Values | Description |
|-------|------|----------|---------------|-------------|
| `Status` | enum | Required | `draft`, `complete` | Stage-level status. |
| `Created` | date | Required | `YYYY-MM-DD` | Date the plan was created. |
| `Updated` | date | Required | `YYYY-MM-DD` | Date of the most recent edit. |
| `Related Artifacts` | map | Required | See sub-fields | Links to related stage files. |
| `Related Artifacts.Spec` | path | Required | `./spec.md` | Path to the work item's spec. |
| `Related Artifacts.Design` | path | Required | `./design.md` | Path to the work item's design. |

**Example**:

```yaml
---
Status: draft
Created: 2026-02-03
Updated: 2026-02-05
Related Artifacts:
  Spec: ./spec.md
  Design: ./design.md
---
```

### 3.4 review.md

Optional advisory artifact produced by `/review-model` between design and implementation. Not tracked by the PM engine as a stage (see DD-3).

**Location**: `work/active/{WI-XXX}_{name}/review.md`

| Field | Type | Required | Allowed Values | Description |
|-------|------|----------|---------------|-------------|
| `Verdict` | enum | Required | `pass`, `concerns`, `fail` | Design review outcome. `pass` = proceed to planning. `concerns` = proceed but address issues. `fail` = return to design. |
| `Created` | date | Required | `YYYY-MM-DD` | Date the review was conducted. |
| `Related Artifacts` | map | Required | See sub-fields | Links to related stage files. |
| `Related Artifacts.Design` | path | Required | `./design.md` | Path to the design being reviewed. |

**Example**:

```yaml
---
Verdict: concerns
Created: 2026-02-04
Related Artifacts:
  Design: ./design.md
---
```

**Notes**:
- No `Updated` field — reviews are point-in-time. If the design is revised and re-reviewed, a new review replaces the old one.
- No `Status` field — the `Verdict` serves this purpose.

### 3.5 BACKLOG.md

The project backlog and WI-XXX ID registry. YAML frontmatter is the machine-readable source of truth; the markdown body is a human-readable dashboard rendered from the frontmatter.

**Location**: `work/BACKLOG.md`

| Field | Type | Required | Allowed Values | Description |
|-------|------|----------|---------------|-------------|
| `epics` | list | Required | List of epic objects (may be empty `[]`) | All epics in the project. |
| `epics[].name` | string | Required | Free-form | Epic display name. Must match the epic file's `# Epic: ` heading. |
| `epics[].goal` | id | Optional | `G-XXX` | Link to a project goal in OVERVIEW.md. |
| `epics[].priority` | enum | Required | `P0`, `P1`, `P2`, `P3` | Epic priority. P0 = critical, P3 = nice-to-have. |
| `epics[].status` | enum | Required | `draft`, `active`, `completed` | Epic-level status (derived from sub-item states — see workflows.md § 3.6). |
| `epics[].file` | path | Required | Relative from `work/` | Path to the epic file, relative to BACKLOG.md's directory. |
| `epics[].items` | list | Required | List of item objects (may be empty `[]`) | Work items belonging to this epic. |
| `epics[].items[].id` | id | Required | `WI-XXX` | Unique work item ID. Assigned by AP-7 scripts. |
| `epics[].items[].name` | string | Required | Free-form | Work item display name. |
| `epics[].items[].scale` | enum | Required | `trivial`, `standard` | Work item scale. |
| `epics[].items[].status` | enum | Required | `backlog`, `active`, `paused`, `abandoned`, `failed`, `completed` | Work item status as tracked in the backlog. |
| `epics[].items[].completed` | date | Conditional | `YYYY-MM-DD` | Completion date. **Required when status = `completed`**, omitted otherwise. |
| `standalone` | list | Required | List of item objects (may be empty `[]`) | Work items not belonging to any epic. |
| `standalone[].id` | id | Required | `WI-XXX` | Unique work item ID. |
| `standalone[].name` | string | Required | Free-form | Work item display name. |
| `standalone[].scale` | enum | Required | `trivial`, `standard` | Work item scale. |
| `standalone[].priority` | enum | Required | `P0`, `P1`, `P2`, `P3` | Item priority (standalone items carry their own priority; epic items inherit from the epic). |
| `standalone[].status` | enum | Required | `backlog`, `active`, `paused`, `abandoned`, `failed`, `completed` | Work item status. |
| `standalone[].completed` | date | Conditional | `YYYY-MM-DD` | Completion date. **Required when status = `completed`**, omitted otherwise. |

**Example**:

```yaml
---
epics:
  - name: "End-to-End Pipeline De-Risking"
    goal: G-001
    priority: P0
    status: active
    file: backlog/epic-end-to-end-pipeline-derisking.md
    items:
      - id: WI-001
        name: "Solar+Battery SysML Model"
        scale: standard
        status: completed
        completed: 2026-02-05
      - id: WI-002
        name: "Codegen Chain Spike"
        scale: standard
        status: active
      - id: WI-003
        name: "Cost Evaluation & Entry Points"
        scale: standard
        status: backlog

standalone:
  - id: WI-004
    name: "Fix cost_model redefines"
    scale: trivial
    priority: P1
    status: completed
    completed: 2026-01-28
  - id: WI-005
    name: "Add missing doc comments"
    scale: standard
    priority: P2
    status: backlog
---
```

### 3.6 Epic File (epic-{name}.md)

Working document for epic decomposition. Contains scope, sequencing, per-item requirements, and risks.

**Location**: `work/backlog/epic-{name}.md`

| Field | Type | Required | Allowed Values | Description |
|-------|------|----------|---------------|-------------|
| `Status` | enum | Required | `draft`, `active`, `completed` | Epic status. `draft` = items not yet in pipeline. `active` = at least one sub-item active. `completed` = all sub-items completed. |
| `Priority` | enum | Required | `P0`, `P1`, `P2`, `P3` | Epic priority. |
| `Goal` | id | Optional | `G-XXX` | Link to a project goal in OVERVIEW.md. |
| `Created` | date | Required | `YYYY-MM-DD` | Date the epic was created. |
| `Updated` | date | Required | `YYYY-MM-DD` | Date of the most recent edit. |

**Example**:

```yaml
---
Status: active
Priority: P0
Goal: G-001
Created: 2026-01-15
Updated: 2026-02-01
---
```

---

## 4. Template Verification

Cross-check of existing templates against the schemas defined above.

### BACKLOG.md.template

**Template frontmatter** (from `project_templates/BACKLOG.md.template`):
```yaml
---
epics: []
standalone: []
---
```

**Verdict**: Matches. Empty lists are valid per the schema — both `epics` and `standalone` are required and may be empty `[]`. This is the correct empty state (AP-1: design for 0, 1, N).

### epic_template.md.template

**Template frontmatter** (from `project_templates/epic_template.md.template`):
```yaml
---
Status: draft
Priority: P1
Goal: G-XXX  # from project/OVERVIEW.md
Created: YYYY-MM-DD
Updated: YYYY-MM-DD
---
```

**Verdict**: Matches. All fields present, correct types, valid default values. The `G-XXX` placeholder and `YYYY-MM-DD` placeholders are filled in by the user when creating an epic. The comment is acceptable — YAML comments are stripped during parsing.

---

## 5. PM Engine Contract Notes

### What the PM Engine Should Expect

1. **All frontmatter is optional at the file level** — a markdown file may have no frontmatter block at all. The PM engine must handle this gracefully (treat as "unparseable, skip with warning").

2. **Unknown fields are ignored** — commands or users may add fields not in this schema (e.g., `Tags`, `Notes`). The PM engine reads only the fields defined here.

3. **Empty string vs omitted** — for optional fields, both `Epic: ""` and omitting `Epic` entirely are equivalent. The PM engine should normalize both to "not set."

4. **Status is authoritative in spec.md** — for work items, the spec.md `Status` field is the single source of truth. If BACKLOG.md shows a different status for the same WI-XXX, spec.md wins (BACKLOG.md may be stale).

5. **Date validation** — dates must match `YYYY-MM-DD`. Invalid dates (e.g., `2026-13-45`) produce a validation warning, not a hard failure.

### Error Handling Guidance

Per AP-7 input validation guarantee ([workflows.md](workflows.md) § 4.2):
- Parse what you can, skip what you can't
- Report warnings with file path and field name: `"work/active/WI-001_solar/spec.md: Status field has invalid value 'in-progress' (expected: active|paused|abandoned|failed|completed)"`
- Produce partial results — "3 of 5 work items parsed" is better than crashing
- Never silently ignore a parse failure — always surface it in the dashboard output
