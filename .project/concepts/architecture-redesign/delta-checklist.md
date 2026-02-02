# Delta Checklist: Architecture Redesign Implementation

**Date**: 2026-02-01
**Purpose**: Exhaustive list of every change required to move from current state to architecture vision. Reference document — epics handle status tracking.
**Derivation**: Diff of current codebase (as of `revamp-architecture` branch) against architecture concept documents.

---

## How to Read This

Each item is a single, verifiable action. Items are grouped by epoch and then by deliverable. Checkboxes are for reference only — the epics/backlog track actual status.

**Notation**:
- `[NEW]` — File or module doesn't exist yet
- `[REVISE]` — File exists, needs modification
- `[MOVE]` — File moves to a new location
- `[DELETE]` — File should be removed
- `[RENAME]` — File or directory gets renamed

---

## Epoch 1: Structure (Phase 1A)

### 1.1 Project Templates — New Files

These are new `.template` files in `project_templates/`.

- [ ] `[NEW]` `project_templates/KNOWLEDGE.md.template` — DI-XXX registry with entity format from information-architecture.md § 3 Role 2. Empty-state template (AP-1: works when empty).
- [ ] `[NEW]` `project_templates/ARCHITECTURE.md.template` — AD-XXX registry with Domain Decomposition, Package Organization table, Key Decisions sections from information-architecture.md § 3 Role 5.
- [ ] `[NEW]` `project_templates/REQUIREMENTS.md.template` — PR-XXX table with columns: ID, Requirement, Source, Enforcement, Validation Method. From information-architecture.md § 3 Role 4.
- [ ] `[NEW]` `project_templates/VALIDATION_MATRIX.md.template` — SV-XXX table with columns: ID, Description, Type, Mechanism, Expected, Tolerance, Source, Test, Status. From information-architecture.md § 3 Role 6.
- [ ] `[NEW]` `project_templates/EPIC_GUIDE.md.template` — Decomposition guidance reference. Tool-owned.
- [ ] `[NEW]` `project_templates/epic_template.md.template` — Template for `work/backlog/epic-{name}.md` files with YAML frontmatter (Status, Priority, Goal, Created, Updated).

### 1.2 Project Templates — Revised Files

- [ ] `[REVISE]` `project_templates/OVERVIEW.md.template` — Add Goals Registry table (ID, Goal, Priority, Status, Source, Traced Requirements), Analysis Questions table (ID, Question, Implies, Source, Status), Scope section, Success Criteria section. From information-architecture.md § 3 Role 3.
- [ ] `[REVISE]` `project_templates/BACKLOG.md.template` — Add YAML frontmatter structure (epics list with items, standalone list). Body becomes a rendered dashboard. From workflows.md § 3.6.
- [ ] `[REVISE]` `project_templates/MODELING_GUIDE.md.template` — Extract reference/how-to material that will move to skills. What remains is pure rules (definitions vs usages, ADR-002, package structure, naming, documentation standards, validation checklist).
- [ ] `[REVISE]` `project_templates/MODELING_PROCESS.md.template` — Update references to new directory structure (knowledge/, project/, work/), new commands (/quick-model, /review-model, /analyze-models, /status, /formalize-intent), new documents (KNOWLEDGE.md, ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md).
- [ ] `[REVISE]` `project_templates/README.md.template` — Update directory structure description to match 4-directory model.

### 1.3 Project Templates — Files to Evaluate

- [ ] `[EVALUATE]` `project_templates/data/assumption_register.md.template` — Not mentioned in architecture. Decide: keep, merge into another artifact, or delete.
- [ ] `[EVALUATE]` `project_templates/LOCAL_GUIDE.md.template` — Not mentioned in architecture. Was project-specific customizations. Decide: fold into modeling_project/REQUIREMENTS.md or keep separate.
- [ ] `[EVALUATE]` `project_templates/RAW_LEARNINGS.md.template` — Architecture puts this at `work/learnings/RAW_LEARNINGS.md`. Confirm destination path update.
- [ ] `[EVALUATE]` `project_templates/data/traceability_matrix.csv` — Architecture puts this at `data/traceability_matrix.csv`. Confirm schema matches information-architecture.md § 5.3 (Element, File, Type, Knowledge, Requirement, Source_Type, Source_Document, Source_Location, Confidence, Assumptions, Last_Verified).

### 1.4 CLI: `cmd_init()` Changes (`src/agentic_mbse/cli/__init__.py`)

#### Directory structure changes

- [ ] `[REVISE]` Change directory creation from `modeling_pm/{backlog,active,research,learnings}` to:
  - `knowledge/` (top-level)
  - `knowledge/research/pending/`
  - `knowledge/research/approved/`
  - `knowledge/research/impacts/`
  - `knowledge/sources/`
  - `modeling_project/` (top-level)
  - `modeling_project/intent/`
  - `work/` (top-level)
  - `work/backlog/`
  - `work/active/`
  - `work/completed/`
  - `work/analysis/`
  - `work/learnings/`
  - `data/` (top-level)

#### Template registration changes

- [ ] `[REVISE]` `USER_OWNED_TEMPLATES` — Update destination paths:
  - `OVERVIEW.md.template` → `modeling_project/OVERVIEW.md` (was `modeling_pm/OVERVIEW.md`)
  - `BACKLOG.md.template` → `work/BACKLOG.md` (was `modeling_pm/backlog/BACKLOG.md`)
  - `RAW_LEARNINGS.md.template` → `work/learnings/RAW_LEARNINGS.md` (was `modeling_pm/learnings/RAW_LEARNINGS.md`)
- [ ] `[REVISE]` `USER_OWNED_TEMPLATES` — Add new entries:
  - `KNOWLEDGE.md.template` → `knowledge/KNOWLEDGE.md`
  - `ARCHITECTURE.md.template` → `modeling_project/ARCHITECTURE.md`
  - `REQUIREMENTS.md.template` → `modeling_project/REQUIREMENTS.md`
  - `VALIDATION_MATRIX.md.template` → `modeling_project/VALIDATION_MATRIX.md`
- [ ] `[REVISE]` `USER_OWNED_TEMPLATES` — Remove or update:
  - `LOCAL_GUIDE.md.template` → evaluate (see 1.3)
- [ ] `[REVISE]` `TOOL_OWNED_TEMPLATES` — Update destination paths:
  - `MODELING_GUIDE.md.template` → `modeling_project/MODELING_GUIDE.md` (was `modeling_pm/MODELING_GUIDE.md`)
  - `MODELING_PROCESS.md.template` → `modeling_project/MODELING_PROCESS.md` (was `modeling_pm/MODELING_PROCESS.md`)
- [ ] `[REVISE]` `TOOL_OWNED_TEMPLATES` — Add new entries:
  - `EPIC_GUIDE.md.template` → `work/EPIC_GUIDE.md`

#### SOURCE_INDEX.md location change

- [ ] `[REVISE]` `cmd_init()` — Move SOURCE_INDEX.md creation to `knowledge/SOURCE_INDEX.md` (was project root)

#### .gitignore update

- [ ] `[REVISE]` `DEV_MODE_GITIGNORE_PATHS` — Update paths from `modeling_pm/` to `modeling_project/` for tool-owned files:
  - `modeling_pm/MODELING_GUIDE.md` → `modeling_project/MODELING_GUIDE.md`
  - `modeling_pm/MODELING_PROCESS.md` → `modeling_project/MODELING_PROCESS.md`
  - Add `work/EPIC_GUIDE.md`

#### Data template installation

- [ ] `[REVISE]` `cmd_init()` — Install `data/traceability_matrix.csv` to `data/` directory (verify current behavior and update if needed)

### 1.5 CLI: `replicate_setup.sh` Changes

- [ ] `[REVISE]` `create_project_structure()` — Update directory creation from `modeling_pm/{backlog,active,research}` to `knowledge/`, `knowledge/research/{pending,approved,impacts}`, `knowledge/sources/`, `modeling_project/`, `modeling_project/intent/`, `work/`, `work/{backlog,active,completed,analysis,learnings}`, `data/`
- [ ] `[REVISE]` `create_project_structure()` — Update template copy destinations:
  - `MODELING_GUIDE.md` → `modeling_project/MODELING_GUIDE.md` (was `modeling_pm/`)
  - `MODELING_PROCESS.md` → `modeling_project/MODELING_PROCESS.md` (was `modeling_pm/`)
- [ ] `[REVISE]` `create_overview_md()` — Write to `modeling_project/OVERVIEW.md` (was `modeling_pm/OVERVIEW.md`), update content to include Goals Registry and Analysis Questions table structure
- [ ] `[REVISE]` `create_source_index()` — Copy to `knowledge/SOURCE_INDEX.md` (was root `SOURCE_INDEX.md`)
- [ ] `[NEW]` Add creation of new template files: `knowledge/KNOWLEDGE.md`, `modeling_project/ARCHITECTURE.md`, `modeling_project/REQUIREMENTS.md`, `modeling_project/VALIDATION_MATRIX.md`, `work/BACKLOG.md` (with YAML frontmatter)

### 1.6 YAML Frontmatter Schemas (Design Artifact)

These are not files to create but specifications to document for the PM engine's input contracts. They should be recorded somewhere accessible during Phase 3D.

- [ ] `[NEW]` Define spec.md frontmatter schema: Status (active|paused|abandoned|failed|completed), Scale (standard), Epic (string), Owner (string), Created (date), Updated (date)
- [ ] `[NEW]` Define design.md frontmatter schema: Status (draft|complete), Created (date), Updated (date), Related Artifacts (Spec path)
- [ ] `[NEW]` Define plan.md frontmatter schema: Status (draft|complete), Created (date), Updated (date), Related Artifacts (Spec + Design paths)
- [ ] `[NEW]` Define review.md frontmatter schema: Verdict (pass|concerns|fail), Created (date), Related Artifacts (Design path)
- [ ] `[NEW]` Define BACKLOG.md frontmatter schema: epics list (name, goal, priority, status, file, items list), standalone list (name, scale, priority, status, completed)
- [ ] `[NEW]` Define epic file frontmatter schema: Status (draft|active|completed), Priority, Goal, Created, Updated

### 1.7 fusion-tea Migration Plan

Manual, one-time operation. Must be executed on a branch.

#### File moves

- [ ] `modeling_pm/OVERVIEW.md` → `modeling_project/OVERVIEW.md`
- [ ] `modeling_pm/MODELING_GUIDE.md` → `modeling_project/MODELING_GUIDE.md`
- [ ] `modeling_pm/MODELING_PROCESS.md` → `modeling_project/MODELING_PROCESS.md`
- [ ] `modeling_pm/LOCAL_GUIDE.md` → evaluate: fold into `modeling_project/REQUIREMENTS.md` or keep at `modeling_project/LOCAL_GUIDE.md`
- [ ] `modeling_pm/backlog/BACKLOG.md` → `work/BACKLOG.md`
- [ ] `modeling_pm/active/*` → `work/active/*`
- [ ] `modeling_pm/research/*` → `knowledge/research/approved/*` (existing research was user-reviewed)
- [ ] `modeling_pm/learnings/*` → `work/learnings/*`
- [ ] `modeling_pm/docs/COST_MODELING.md` → `knowledge/sources/COST_MODELING.md` or remain separate
- [ ] `SOURCE_INDEX.md` → `knowledge/SOURCE_INDEX.md`

#### New files to create (populated from existing content)

- [ ] `knowledge/KNOWLEDGE.md` — Extract DI-XXX entries from existing research documents and modeling knowledge
- [ ] `modeling_project/ARCHITECTURE.md` — Extract architectural decisions from existing OVERVIEW.md and research docs (domain decomposition, package organization, key decisions like CAS hierarchy)
- [ ] `modeling_project/REQUIREMENTS.md` — Extract project-specific rules from LOCAL_GUIDE.md and learned patterns (cost patterns, doc comment requirements, etc.)
- [ ] `modeling_project/VALIDATION_MATRIX.md` — Populate from existing test assertions in `tests/models/` (power balance accuracy, structural checks, etc.)
- [ ] `data/traceability_matrix.csv` — Verify/update schema to match architecture (add Knowledge and Requirement columns if missing)

#### New directories to create

- [ ] `knowledge/research/pending/`
- [ ] `knowledge/research/impacts/`
- [ ] `knowledge/sources/`
- [ ] `modeling_project/intent/`
- [ ] `work/backlog/` (for epic files)
- [ ] `work/completed/`
- [ ] `work/analysis/`

#### Format changes

- [ ] `work/BACKLOG.md` — Add YAML frontmatter with epics/standalone structure
- [ ] `work/active/*/spec.md` — Add YAML frontmatter (Status, Scale, Epic, Owner, Created, Updated) to each existing spec.md
- [ ] `work/active/*/design.md` — Add YAML frontmatter (Status, Created, Updated, Related Artifacts) to each existing design.md
- [ ] `work/active/*/plan.md` — Add YAML frontmatter (Status, Created, Updated, Related Artifacts) to each existing plan.md

#### Cleanup

- [ ] Remove `modeling_pm/` directory after migration (or rename to `modeling_pm.bak/` temporarily)
- [ ] Update `.gitignore` if needed
- [ ] Update `CLAUDE.md` to reference new paths
- [ ] Update any symlinks (`.claude/` components point to agentic-mbse repo)
- [ ] Run existing tests to verify nothing breaks

### 1.8 CLAUDE.md Updates (fusion-tea)

- [ ] `[REVISE]` Update all `modeling_pm/` references to `knowledge/`, `modeling_project/`, `work/`
- [ ] `[REVISE]` Update document descriptions to match new file structure
- [ ] `[REVISE]` Add descriptions of new files (KNOWLEDGE.md, ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md)

### 1.9 Tests for Epoch 1

- [ ] `[REVISE]` `tests/test_cli.py` — Update `cmd_init()` tests to expect new directory structure (knowledge/, project/, work/, data/)
- [ ] `[REVISE]` `tests/test_cli.py` — Add tests for new template installation (KNOWLEDGE.md, ARCHITECTURE.md, etc.)
- [ ] `[REVISE]` `tests/test_cli.py` — Update path expectations from `modeling_pm/` to new locations
- [ ] Verify fusion-tea's existing 42 tests still pass after migration

---

## Epoch 2: Knowledge (Phase 2B)

### 2.1 New Skills

Each skill gets a directory in `claude/skills/{name}/` with at minimum a `SKILL.md` file and optional `references/` subdirectory.

- [ ] `[NEW]` `claude/skills/sysml-conventions/SKILL.md` — Syntax rules, naming conventions, common patterns, pitfalls, code stencils. Source: extract from `claude/commands/design-model.md` (600+ lines of embedded SysML knowledge), supplemented by `project_templates/MODELING_GUIDE.md.template` reference material.
- [ ] `[NEW]` `claude/skills/sysml-conventions/references/` — Optional deep reference files (syntax examples, pattern catalog)
- [ ] `[NEW]` `claude/skills/model-validation/SKILL.md` — Quality pyramid (8 levels), CLI commands (`agentic-mbse validate`), pass/fail criteria, regression test patterns. Source: extract from `design-model.md` and `implement-model.md`.
- [ ] `[NEW]` `claude/skills/project-structure/SKILL.md` — Library vs designs, file organization, cross-file patterns, EXPOSE pattern, information architecture summary (4 directories, what goes where). Source: extract from `design-model.md`, `spec-model.md`, `implement-model.md`.
- [ ] `[NEW]` `claude/skills/source-traceability/SKILL.md` — SOURCE_INDEX format, citation patterns, doc comment requirements (Source, Reference fields), traceability matrix schema. Source: extract from `design-model.md`, `manage-sources.md`, `research.md`.
- [ ] `[NEW]` `claude/skills/epic-decomposition/SKILL.md` — Goldilocks principle adapted for modeling, work item scale taxonomy (Trivial/Standard/Epic), decomposition process, anti-patterns. Source: new content from workflows.md § 2.1, § 3.6.
- [ ] `[NEW]` `claude/skills/requirements-tracking/SKILL.md` — REQUIREMENTS.md format (PR-XXX), promotion path from per-feature MR-XXX patterns, enforcement methods, compliance checking. Source: new content from information-architecture.md § 3 Role 4.

### 2.2 Existing Skills — Updates

- [ ] `[REVISE]` `claude/skills/toolkit-awareness/SKILL.md` — Add new PM CLI commands (`agentic-mbse status`, `agentic-mbse pm ...`), new slash commands (`/quick-model`, `/review-model`, `/analyze-models`, `/status`, `/formalize-intent`), updated directory structure.
- [ ] `[EVALUATE]` `claude/skills/record-learning/SKILL.md` — Architecture doesn't mention this skill. Evaluate: is the learning capture pattern folded into the close-flow trigger questions (workflows.md § 3.5), or does it remain standalone?

### 2.3 Skill Registration in `cmd_init()`

- [ ] `[REVISE]` `MBSE_SKILLS` list in `cli/__init__.py` — Add new skills: `sysml-conventions`, `model-validation`, `project-structure`, `source-traceability`, `epic-decomposition`, `requirements-tracking`
- [ ] `[REVISE]` `replicate_setup.sh` — Add new skills to the install loop

### 2.4 Context Window Measurement (Design Activity)

Not a code change but a required decision gate.

- [ ] Measure token count of each SKILL.md
- [ ] Test loading 3-4 skills simultaneously in a command context
- [ ] Determine if any skill exceeds 200 lines and needs splitting
- [ ] Decide skill loading strategy: all upfront vs staged (Q10)
- [ ] Document results and decisions

---

## Epoch 3A: Commands (Phase 3C)

### 3A.1 Command Refactoring — Existing Commands

For each command: extract embedded knowledge to skill references, reduce to 200-300 lines, add AP-7 script calls where applicable.

- [ ] `[REVISE]` `claude/commands/design-model.md` (1,345 lines → target ~250)
  - Extract SysML syntax/patterns to `sysml-conventions` skill reference
  - Extract validation guidance to `model-validation` skill reference
  - Extract file structure rules to `project-structure` skill reference
  - Extract citation/source patterns to `source-traceability` skill reference
  - Add reading of `modeling_project/ARCHITECTURE.md` for existing decisions
  - Add reading of `modeling_project/REQUIREMENTS.md` for compliance
  - Add reference to `review.md` as optional output for `/review-model`

- [ ] `[REVISE]` `claude/commands/implement-model.md` (493 lines → target ~250)
  - Extract SysML syntax to `sysml-conventions` skill reference
  - Extract validation to `model-validation` skill reference
  - Extract file structure to `project-structure` skill reference
  - Add inline knowledge capture flow (call `agentic-mbse pm add-insight` when agent discovers domain insight — B-008)
  - Add traceability recording (call `agentic-mbse pm trace-element` for significant model elements)
  - Add requirement promotion (call `agentic-mbse pm promote-requirement` for durable MR-XXX → PR-XXX)

- [ ] `[REVISE]` `claude/commands/spec-model.md` (392 lines → target ~250)
  - Extract to `project-structure` skill reference
  - Extract to `source-traceability` skill reference
  - Add reading of `knowledge/KNOWLEDGE.md` for DI-XXX insights
  - Add reading of `modeling_project/OVERVIEW.md` for G-XXX goals and AQ-XXX questions
  - Add YAML frontmatter generation for spec.md (Status, Scale, Epic, Owner, Created, Updated)
  - Add SV-XXX entry creation in VALIDATION_MATRIX.md for verification criteria

- [ ] `[REVISE]` `claude/commands/plan-model.md` (676 lines → target ~250)
  - Extract to `model-validation` skill reference
  - Add YAML frontmatter generation for plan.md

- [ ] `[REVISE]` `claude/commands/audit-models.md` (446 lines → target ~300)
  - Extract to `model-validation` skill reference
  - Extract to `source-traceability` skill reference
  - Add to `requirements-tracking` skill reference
  - Add decision promotion flow: call `agentic-mbse pm register-decision` when user approves promoting a pattern to AD-XXX
  - Add SV-XXX status updates via `agentic-mbse pm update-validation`

- [ ] `[REVISE]` `claude/commands/research.md` (243 lines → target ~250)
  - Add approval workflow: call `agentic-mbse pm approve-research` after user approves findings
  - Add DI-XXX insight suggestion and capture flow
  - Add knowledge supersession detection (flag conflicts with existing DI-XXX)
  - Add file save via script (not agent choosing path): `knowledge/research/pending/YYYYMMDD-HHMMSS_topic.md`

- [ ] `[REVISE]` `claude/commands/onboard.md` (577 lines → target ~300)
  - Add trigger for `/formalize-intent` after initial documents are placed in `modeling_project/intent/`
  - Update project structure references to new directories
  - Add initial ARCHITECTURE.md population guidance

- [ ] `[REVISE]` `claude/commands/manage-sources.md` (357 lines → target ~250)
  - Update SOURCE_INDEX.md path reference to `knowledge/SOURCE_INDEX.md`
  - Extract to `source-traceability` skill reference

- [ ] `[REVISE]` `claude/commands/backlog.md` (358 lines → target ~250)
  - Add scale assessment (Trivial/Standard/Epic) to work item creation
  - Add epic decomposition flow (call `epic-decomposition` skill)
  - Update BACKLOG.md path to `work/BACKLOG.md`
  - Add YAML frontmatter updates via AP-7 scripts

### 3A.2 New Commands

- [ ] `[NEW]` `claude/commands/quick-model.md` — Trivial-scale changes. No work item directory. Direct change + validate. Guard rail: if scope exceeds trivial, redirect to `/spec-model`. Skills: `sysml-conventions`, `model-validation`.
- [ ] `[NEW]` `claude/commands/review-model.md` — Design review before implementation. Produces optional `review.md` with verdict (pass/concerns/fail) in YAML frontmatter. Skills: `sysml-conventions`, `model-validation`, `project-structure`, `requirements-tracking`.
- [ ] `[NEW]` `claude/commands/analyze-models.md` — Model analysis reports to `work/analysis/YYYYMMDD-HHMMSS_topic.md`. Parse model structure, check rules compliance, compute health indicators. Skills: `project-structure`, `model-validation`.
- [ ] `[NEW]` `claude/commands/status.md` — Thin wrapper: call `agentic-mbse status` script, present dashboard, add interpretation and recommendations. Skills: `epic-decomposition`, `requirements-tracking`.
- [ ] `[NEW]` `claude/commands/formalize-intent.md` — Extract G-XXX goals and AQ-XXX analysis questions from `modeling_project/intent/` documents. User reviews and approves each. Calls AP-7 script to register in OVERVIEW.md. Skills: `project-structure`.

### 3A.3 Command Registration in `cmd_init()`

- [ ] `[REVISE]` `MBSE_COMMANDS` list in `cli/__init__.py` — Add: `quick-model.md`, `review-model.md`, `analyze-models.md`, `status.md`, `formalize-intent.md`
- [ ] `[REVISE]` `replicate_setup.sh` — Add new commands to the install loop

### 3A.4 Agents

- [ ] `[EVALUATE]` `claude/agents/deprecated/sysmlv2-doc-analyzer.md` — Architecture lists this as active agent. Decide: restore from deprecated/ to agents/, or confirm deprecation is intentional and remove from architecture.
- [ ] `[REVISE]` `MBSE_AGENTS` list in `cli/__init__.py` — Add `sysmlv2-doc-analyzer.md` if restored; or add any other agent changes
- [ ] `[REVISE]` All agent files — Standardize doc path references (verify {SYSML_DOCS_PATH} and {SYSIDE_DOCS_PATH} placeholders are consistent)

### 3A.5 Validation Walkthrough (Quality Gate)

Not code changes — verification activities.

- [ ] Walk through `/spec-model` against a fusion-tea work item with refactored command
- [ ] Walk through `/design-model` against a fusion-tea work item with refactored command
- [ ] Walk through `/implement-model` against a fusion-tea work item with refactored command
- [ ] Walk through `/audit-models` against fusion-tea models with refactored command
- [ ] Walk through `/research` with approval flow against fusion-tea knowledge sources
- [ ] Verify no implicit knowledge was lost in the refactoring (Q12)

---

## Epoch 3B: PM Script Engine (Phase 3D)

### 3B.1 New Python Module: `src/agentic_mbse/pm/`

- [ ] `[NEW]` `src/agentic_mbse/pm/__init__.py` — Module init, public API exports
- [ ] `[NEW]` `src/agentic_mbse/pm/parser.py` — Structured file parsers:
  - YAML frontmatter parser (extract from markdown files)
  - BACKLOG.md parser (YAML frontmatter with epics/standalone structure)
  - REQUIREMENTS.md parser (markdown table rows)
  - VALIDATION_MATRIX.md parser (markdown table rows)
  - KNOWLEDGE.md parser (DI-XXX entries)
  - ARCHITECTURE.md parser (AD-XXX entries)
  - traceability_matrix.csv parser
  - Input validation per AP-7 guarantee: malformed input → clear error, partial results with warnings preferred over hard failures
- [ ] `[NEW]` `src/agentic_mbse/pm/state.py` — Work item state derivation:
  - Two-step read: file system structure → spec.md frontmatter
  - Epic state derivation (draft/active/completed from sub-item states)
  - Stage detection (which artifact files exist)
- [ ] `[NEW]` `src/agentic_mbse/pm/dashboard.py` — Dashboard generator:
  - Work items section (epic progress, item states)
  - Project rules section (REQUIREMENTS.md metrics)
  - Validation status section (VALIDATION_MATRIX.md metrics)
  - Plain markdown output (renders in terminal and IDE)
- [ ] `[NEW]` `src/agentic_mbse/pm/operations.py` — AP-7 operations:

#### AP-7 Tier 1 Operations (fully deterministic)

  - [ ] `close-item`: Move `work/active/{item}/` → `work/completed/YYYYMMDD_{item}/`, update BACKLOG.md YAML frontmatter status, re-render BACKLOG.md body
  - [ ] `trace-element`: Append row to `data/traceability_matrix.csv`. Validate schema, prevent duplicates, validate PR-XXX exists in REQUIREMENTS.md and DI-XXX exists in KNOWLEDGE.md
  - [ ] `promote-requirement`: Append PR-XXX row to `modeling_project/REQUIREMENTS.md`. Validate format, assign ID, record Source (DI-XXX or G-XXX)
  - [ ] `register-decision`: Append AD-XXX entry to `modeling_project/ARCHITECTURE.md`. Validate format, assign ID
  - [ ] `update-validation`: Update Status column in `modeling_project/VALIDATION_MATRIX.md` for specified SV-XXX
  - [ ] `add-insight` (T1 mechanics, T3 invocation): Assign DI-XXX ID, format entry from agent-supplied fields, append to `knowledge/KNOWLEDGE.md`. Validate all required fields present. Source uses `work-item:{name}/{artifact}` convention
  - [ ] `impact-query`: Given DI-XXX or PR-XXX, traverse `data/traceability_matrix.csv` to find affected model elements and work items. Return structured result
  - [ ] `status` (dashboard): Parse all structured files, produce dashboard markdown

#### AP-7 Tier 2 Operations (script + headless LLM)

  - [ ] `approve-research`: Move `knowledge/research/pending/` → `approved/`, assign DI-XXX IDs, format entries, append to `knowledge/KNOWLEDGE.md`. Accepts `--insights` JSON argument with pre-formed content
  - [ ] `supersede-insight`: Mark old DI-XXX as superseded, create new DI-XXX, query traceability_matrix.csv for affected elements, produce impact report to `knowledge/research/impacts/DI-XXX_superseded.md`

#### Work item name resolution (B-014)

  - [ ] `[NEW]` Name resolution mechanism: given a work item name (possibly partial), resolve to `work/active/{item}/` path. Handle ambiguity (multiple matches → error with candidates). Handle completed items (`work/completed/YYYYMMDD_{item}/`)

#### Error model (B-015)

  - [ ] `[NEW]` Define per-operation error model: which operations are atomic (all-or-nothing) vs tolerant (partial results with warnings). Document in module docstrings

### 3B.2 CLI Subcommands

- [ ] `[REVISE]` `src/agentic_mbse/cli/__init__.py` — Add `status` subcommand:
  - `agentic-mbse status` → call dashboard generator, print output
  - Optional: `--json` flag for programmatic consumption
- [ ] `[REVISE]` `src/agentic_mbse/cli/__init__.py` — Add `pm` subcommand group:
  - `agentic-mbse pm close-item <name>`
  - `agentic-mbse pm approve-research <file> --insights '<json>'`
  - `agentic-mbse pm trace-element --element <name> --file <path> --type <kind> [--knowledge DI-XXX] [--requirement PR-XXX] [--source-type <type>] [--source-doc <name>] [--source-location <loc>]`
  - `agentic-mbse pm promote-requirement --requirement <text> --source <ID>`
  - `agentic-mbse pm register-decision --title <text> --decision <text> --rationale <text>`
  - `agentic-mbse pm update-validation <SV-XXX> --status <status>`
  - `agentic-mbse pm add-insight --title <text> --source <source> --context <text> --model-implications <text> --analysis-implications <text> [--rationale <text>]`
  - `agentic-mbse pm impact-query <ID>`
  - `agentic-mbse pm supersede-insight <DI-XXX> --new-insight '<json>' --reason '<text>'`

### 3B.3 Tests for PM Engine

- [ ] `[NEW]` `tests/test_pm_parser.py` — Unit tests for each parser (YAML frontmatter, BACKLOG.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, KNOWLEDGE.md, traceability CSV)
- [ ] `[NEW]` `tests/test_pm_state.py` — Unit tests for state derivation (file system → state, frontmatter override, epic state)
- [ ] `[NEW]` `tests/test_pm_dashboard.py` — Unit tests for dashboard generation (empty project, partial data, full data)
- [ ] `[NEW]` `tests/test_pm_operations.py` — Unit tests for each AP-7 operation:
  - close-item: verify file move, BACKLOG.md update, BACKLOG.md body re-render
  - trace-element: verify CSV append, duplicate prevention, ID validation
  - promote-requirement: verify REQUIREMENTS.md append, ID assignment
  - register-decision: verify ARCHITECTURE.md append, ID assignment
  - update-validation: verify VALIDATION_MATRIX.md status update
  - add-insight: verify KNOWLEDGE.md append, ID assignment, field validation
  - impact-query: verify CSV traversal, result structure
  - approve-research: verify file move, KNOWLEDGE.md append
  - supersede-insight: verify status update, new entry, impact report generation
- [ ] `[NEW]` `tests/test_pm_cli.py` — Integration tests for CLI subcommands (end-to-end with temp directories)
- [ ] `[NEW]` `tests/fixtures/pm/` — Test fixtures: sample BACKLOG.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, KNOWLEDGE.md, ARCHITECTURE.md, traceability_matrix.csv, spec.md with frontmatter

### 3B.4 Validation Pyramid Updates

- [ ] `[REVISE]` `src/agentic_mbse/validation/level6_traceability.py` — Extend with sub-checks per information-architecture.md § 5.5:
  1. Format check: doc comments contain Source and Reference fields
  2. Resolvability check: referenced source documents exist in SOURCE_INDEX.md
  3. Completeness check: traceability_matrix.csv has entry for each definition
  4. Requirement coverage check: every PR-XXX has at least one satisfying element
  - Note: sub-checks 1-3 extend Level 6; sub-check 4 may belong in Level 7 or as a `--traceability` flag. Decide during implementation.

---

## Cross-Cutting Concerns

### Documentation Updates

- [ ] `[REVISE]` `CLAUDE.md` (agentic-mbse repo) — Update architecture section, add PM module description, update directory descriptions, add new CLI commands
- [ ] `[REVISE]` `docs/source-index.md` — Update path references if SOURCE_INDEX.md moves to `knowledge/`

### Downstream Coordination

- [ ] `[EVALUATE]` Verify sysml-codegen still works with any agentic-mbse API changes (unlikely — validation and sysml modules are unchanged)
- [ ] `[EVALUATE]` Level 8 validation alignment with sysml-codegen extraction requirements (existing contract, verify no drift)

### Test Infrastructure

- [ ] `[NEW]` `tests/conftest.py` updates — Add pytest fixtures for PM test scenarios (temp project directories with full structure)

### Backlog Items Still Open (from architecture backlog)

- [ ] B-014: Work item name resolution — addressed in 3B.1 above
- [ ] B-015: AP-7 error model (atomic vs tolerant) — addressed in 3B.1 above

---

## Summary Counts

| Category | New | Revised | Evaluate | Total |
|----------|-----|---------|----------|-------|
| Templates | 6 | 5 | 4 | 15 |
| CLI (`cmd_init`) | 0 | ~12 changes | 0 | 12 |
| CLI (`replicate_setup.sh`) | 1 | ~5 changes | 0 | 6 |
| Skills | 7 | 2 | 0 | 9 |
| Commands | 5 | 9 | 0 | 14 |
| Agents | 0 | 2 | 1 | 3 |
| PM Module (Python) | ~8 files | 0 | 0 | 8 |
| PM CLI subcommands | ~10 | 0 | 0 | 10 |
| Tests | ~6 files | ~2 | 0 | 8 |
| fusion-tea migration | ~15 moves | ~8 format changes | ~3 | 26 |
| **Total** | | | | **~111 items** |
