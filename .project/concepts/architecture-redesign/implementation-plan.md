# Implementation Plan: Architecture Redesign

**Date**: 2026-02-01
**Status**: Draft — ready for review before implementation begins
**Parent**: [main.md](main.md) — Problem, principles, architecture overview
**Delta reference**: [delta-checklist.md](delta-checklist.md) — Exhaustive list of every individual change

---

## 1. Strategic Context

### What Exists Today

The agentic-mbse codebase has two mature layers and two immature layers:

| Layer | Status | Evidence |
|-------|--------|----------|
| **Validation pyramid** | Complete | 8 levels implemented, 2,827 LOC, comprehensive test coverage |
| **SysML utilities** | Complete | 1,742 LOC — adapter, binding, expression, graph, types |
| **Claude components** | Partially complete, poorly structured | 9 commands averaging 543 lines (target: 250), 3 of 7 skills, no PM engine |
| **Information architecture** | Designed, not implemented | Single `modeling_pm/` directory; no structured registries, no YAML frontmatter |

The validation and SysML layers require no rework. The implementation effort is concentrated in the information layer, knowledge layer (skills), and behavioral layer (commands + PM engine).

### Dependency Chain

The four epics form a strict sequential dependency with one opportunity for parallelism:

```
Epic 1: Structure ──► Epic 2: Knowledge ──► Epic 3: Commands
                                        ├──► Epic 4: PM Engine  (parallel with Epic 3)
                                        │         │
                                        │         ▼
                                        └──► /status command depends on both
```

**Why this order is mandatory**:
- Skills reference the information architecture (knowledge/ paths, entity formats, registry structures). Skills can't be written until the file structure exists.
- Commands reference skills. Commands can't be refactored until skills exist and their granularity is measured.
- The PM engine parses structured files. It can't be built until the file formats are defined (Epic 1) but doesn't need skills or commands — so it can run in parallel with Epic 3.
- The `/status` command is the one point where Epics 3 and 4 converge: it calls the PM dashboard script (Epic 4) and is a command (Epic 3).

### Integration Testbed

fusion-tea is the primary testbed. After each epic, the implementation is validated against fusion-tea:
- **Epic 1**: Does the new structure work? Does `agentic-mbse init` produce the right directories and files? Do existing tests still pass after migration?
- **Epic 2**: Do skills load correctly? Are they the right granularity? Do they fit in context windows?
- **Epic 3**: Do refactored commands work end-to-end against fusion-tea workflows?
- **Epic 4**: Does the PM dashboard produce accurate output from fusion-tea's project state?

---

## 2. Epic 1: Structure (Phase 1A)

### Goal

Establish the information architecture: file structure, entity formats, project templates, and `cmd_init()` changes. Migrate fusion-tea as proof that the structure works.

### Why This Is the Critical Path

Every subsequent epic depends on the file structure being settled. Skills reference `knowledge/KNOWLEDGE.md`, `project/REQUIREMENTS.md`, etc. The PM engine parses `work/BACKLOG.md` YAML frontmatter and `work/active/*/spec.md` metadata. If the structure changes after skills or the PM engine are built, everything downstream must be reworked.

### Deliverables

#### D1.1: New Project Templates
Create 6 new template files in `project_templates/`. Each template must be valid in the empty state (AP-1: design for 0, 1, N) with correct entity formats per [information-architecture.md](information-architecture.md) § 3.

Delta checklist: § 1.1 (6 items)

Templates: `KNOWLEDGE.md`, `ARCHITECTURE.md`, `REQUIREMENTS.md`, `VALIDATION_MATRIX.md`, `EPIC_GUIDE.md`, `epic_template.md`

#### D1.2: Revised Project Templates
Update 5 existing templates to match the architecture. The key changes: OVERVIEW.md gets Goals Registry and Analysis Questions tables; BACKLOG.md gets YAML frontmatter; MODELING_GUIDE.md gets reference material extracted (preparation for skill extraction in Epic 2).

Delta checklist: § 1.2 (5 items)

#### D1.3: Template Evaluation Decisions
4 existing templates need a keep/merge/delete decision before proceeding. These are small decisions but must not be deferred — they affect `cmd_init()` logic.

Delta checklist: § 1.3 (4 items)

Decisions needed:
- `assumption_register.md.template` — not in architecture. Keep, merge into REQUIREMENTS.md, or delete?
- `LOCAL_GUIDE.md.template` — fold into `project/REQUIREMENTS.md` or keep as a separate project-level file?
- `RAW_LEARNINGS.md.template` — confirm destination path is `work/learnings/RAW_LEARNINGS.md`
- `traceability_matrix.csv` — confirm schema matches [information-architecture.md](information-architecture.md) § 5.3

#### D1.4: `cmd_init()` Rewiring
Update the Python init logic to create the new directory structure and install templates to their new locations. This includes updating `USER_OWNED_TEMPLATES`, `TOOL_OWNED_TEMPLATES`, `DEV_MODE_GITIGNORE_PATHS`, and the SOURCE_INDEX.md installation path.

Delta checklist: § 1.4 (~12 items)

**Coordination requirement**: `replicate_setup.sh` must be updated in lockstep (delta checklist § 1.5, ~6 items). Both files create the same structure — they must not diverge.

#### D1.5: YAML Frontmatter Schemas
Define the exact frontmatter schemas for spec.md, design.md, plan.md, review.md, BACKLOG.md, and epic files. These are the PM engine's input contracts.

**Deliverable**: [frontmatter-schemas.md](frontmatter-schemas.md) — authoritative schema reference with field tables, concrete examples, design decisions, and PM engine contract notes.

Delta checklist: § 1.6 (6 items)

#### D1.6: fusion-tea Migration
Manual, one-time migration of fusion-tea's project structure. Must be done on a git branch so it can be reviewed and reverted if needed.

Delta checklist: § 1.7 (~26 items covering file moves, new file creation, format changes, cleanup)

Key risks:
- fusion-tea has active work items in `modeling_pm/active/`. Each needs YAML frontmatter added to spec.md.
- Research documents move from `modeling_pm/research/` to `knowledge/research/approved/` (they've been user-reviewed).
- BACKLOG.md needs restructuring from flat markdown to YAML frontmatter + rendered body.
- Existing symlinks in `.claude/` point to agentic-mbse and need updating.

Mitigation: Do the migration on a branch. Run fusion-tea's 42 existing tests afterward to verify models still parse and validate.

#### D1.7: Test Updates
Update `tests/test_cli.py` to expect the new directory structure.

Delta checklist: § 1.9 (4 items)

### Sequencing Within Epic 1

```
D1.3 (template decisions) ─────► D1.1 (new templates) ──┐
                                  D1.2 (revised templates) ──┤
                                                              ├─► D1.4 (cmd_init) ──► D1.7 (tests)
D1.5 (frontmatter schemas) ──────────────────────────────────┘        │
                                                                       ▼
                                                              D1.6 (fusion-tea migration)
```

Template decisions (D1.3) must come first — they affect what templates exist. Templates (D1.1, D1.2) and frontmatter schemas (D1.5) can proceed in parallel. `cmd_init()` changes (D1.4) depend on templates being final. fusion-tea migration (D1.6) depends on `cmd_init()` working correctly (or can be done manually following the same structure).

### Exit Criteria

- [ ] `agentic-mbse init` on a fresh directory creates the 4-directory structure with all registry files
- [ ] `agentic-mbse init --dev` on the agentic-mbse repo creates the correct symlink structure
- [ ] fusion-tea has been migrated and all 42 existing tests pass
- [ ] All YAML frontmatter schemas are documented
- [ ] `replicate_setup.sh` produces the same structure as `cmd_init()`

---

## 3. Epic 2: Knowledge (Phase 2B)

### Goal

Extract shared knowledge from bloated commands into reusable skills. Measure context window impact. Determine the right granularity.

### Why Skills Must Come Before Commands

The current commands are too long because they embed knowledge that should be shared. `design-model.md` is 1,345 lines — roughly 600 lines of SysML syntax patterns, 200 lines of validation guidance, 150 lines of file structure rules. Refactoring commands without first extracting skills would just be rearranging the same content within each command.

Skills also serve as the **knowledge contracts** between the architecture and the commands. When a command says "reference the sysml-conventions skill," that's a precise statement about what knowledge the command has access to. Without skills, commands must be self-contained, which is exactly the P1 problem.

### Deliverables

#### D2.1: New Skills (7 skills)
Create 7 skill directories in `claude/skills/`, each with a `SKILL.md` under 200 lines and optional `references/` subdirectory.

Delta checklist: § 2.1 (7 items)

| Skill | Primary source | Key content |
|-------|---------------|-------------|
| `sysml-conventions` | Extract from `design-model.md` | Syntax rules, naming, patterns, pitfalls, stencils |
| `model-validation` | Extract from `design-model.md`, `implement-model.md` | 8-level pyramid, CLI usage, criteria, regression patterns |
| `project-structure` | Extract from `design-model.md`, `spec-model.md` | Library vs designs, file org, EXPOSE pattern, 4-directory model |
| `source-traceability` | Extract from `design-model.md`, `manage-sources.md` | SOURCE_INDEX format, citations, doc comments, traceability CSV |
| `epic-decomposition` | New (from [workflows.md](workflows.md) § 2-3) | Scale taxonomy, decomposition process, anti-patterns |
| `requirements-tracking` | New (from [information-architecture.md](information-architecture.md) § 3 Role 4) | PR-XXX format, promotion path, enforcement, compliance |
| `toolkit-awareness` | Revise existing | Add PM commands, new slash commands, updated paths |

#### D2.2: Existing Skill Evaluation
Evaluate the `record-learning` skill against the architecture. The close-flow trigger questions ([workflows.md](workflows.md) § 3.5) may subsume it.

Delta checklist: § 2.2 (2 items)

#### D2.3: Skill Registration
Update `MBSE_SKILLS` in `cli/__init__.py` and `replicate_setup.sh` to install new skills.

Delta checklist: § 2.3 (2 items)

#### D2.4: Context Window Measurement
Empirical measurement: load skill combinations in a command context, measure token consumption, determine if skills need splitting or staging.

Delta checklist: § 2.4 (5 items)

This is the primary risk for this epic. If measurement shows that loading 3-4 skills exceeds acceptable context pressure, skill granularity must change. The architecture is designed for this — skills can split without structural impact. But it could require re-doing D2.1 work.

**Measurement approach** (to be refined):
1. Count tokens in each SKILL.md
2. Simulate a command load: skill SKILL.md files + command prompt + typical project context
3. Compare against a baseline (current commands load everything inline)
4. Target: skills should not increase total context usage vs current state (they redistribute, not add)

### Sequencing Within Epic 2

```
D2.1 (new skills) ──► D2.4 (measurement) ──► Adjust if needed ──► D2.3 (registration)
D2.2 (evaluation) ─┘
```

Skills are written first, then measured. If measurement shows problems, adjust granularity before registering them in init.

### Exit Criteria

- [ ] 7 skills exist with SKILL.md files under 200 lines each
- [ ] Context window measurements documented
- [ ] Skill loading strategy decided (Q9, Q10, Q11 resolved)
- [ ] `agentic-mbse init` installs all skills correctly
- [ ] `record-learning` skill disposition decided

---

## 4. Epic 3: Commands (Phase 3C)

### Goal

Refactor 9 existing commands to use skills (reducing average from 543 to ~250 lines), create 5 new commands, and validate against fusion-tea.

### Deliverables

#### D3.1: Command Refactoring (9 commands)
Each existing command gets: embedded knowledge extracted to skill references, AP-7 script calls added where applicable, paths updated to new directory structure.

**Extraction mapping**: `.project/active/d2.5-extraction-mapping/extraction-mapping.md` — section-by-section mapping of what to remove from each command and which skill absorbs it. Use this as the primary checklist for refactoring.

Delta checklist: § 3A.1 (9 items, each with multiple sub-changes)

**Priority order** (most bloated first, since they yield the most skill content):
1. `design-model.md` (1,345 → ~250 lines) — the biggest source of skill extraction content
2. `implement-model.md` (493 → ~250) — add inline knowledge capture, traceability recording
3. `spec-model.md` (392 → ~250) — add YAML frontmatter generation, DI-XXX/G-XXX reading
4. `plan-model.md` (676 → ~250)
5. `audit-models.md` (446 → ~300) — add decision promotion flow
6. `research.md` (243 → ~250) — add approval workflow (may grow slightly)
7. `onboard.md` (577 → ~300) — add intent formalization trigger
8. `backlog.md` (358 → ~250) — add scale assessment, YAML frontmatter updates
9. `manage-sources.md` (357 → ~250) — path updates, skill reference

#### D3.2: New Commands (5 commands)
Delta checklist: § 3A.2 (5 items)

| Command | Job | Key design question |
|---------|-----|-------------------|
| `/quick-model` | Trivial-scale direct changes | Where's the guard rail that redirects to `/spec-model`? |
| `/review-model` | Design review before implementation | What's in the review.md verdict format? |
| `/analyze-models` | Model analysis reports | Script vs agent vs hybrid? (Q14) |
| `/status` | Project state dashboard | Depends on Epic 4 for the PM script; command is a thin wrapper |
| `/formalize-intent` | Extract goals from intent documents | How does it handle incremental updates? |

**Note**: `/status` is the convergence point between Epics 3 and 4. The command (Epic 3) calls the PM dashboard script (Epic 4). It should be the last command written, after both epics have their other deliverables complete.

#### D3.3: Command Registration
Update `MBSE_COMMANDS` in `cli/__init__.py` and `replicate_setup.sh`.

Delta checklist: § 3A.3 (2 items)

#### D3.4: Agent Cleanup
sysmlv2-doc-analyzer confirmed deprecated and removed (scope covered by sysml-expert + kerml-expert). Doc path references verified consistent across all 5 active agents.

Delta checklist: § 3A.4 (3 items)

#### D3.5: Validation Walkthrough
Walk each refactored command through a real fusion-tea workflow to verify no implicit knowledge was lost (Q12).

Delta checklist: § 3A.5 (6 walkthrough items)

This is a quality gate, not optional. The risk of skill extraction is losing knowledge that was implicitly embedded in long command prompts. The walkthrough catches this before shipping. Cross-reference against the extraction mapping (`.project/active/d2.5-extraction-mapping/extraction-mapping.md`) to verify no knowledge is unaccounted for.

### Sequencing Within Epic 3

```
D3.1 (refactor design-model) ──► D3.1 (refactor implement-model) ──► ... ──► D3.1 (refactor manage-sources)
                                                                                        │
D3.2 (new commands, except /status) ───────────────────────────────────────────────────┤
                                                                                        │
D3.3 (registration) ◄──────────────────────────────────────────────────────────────────┤
D3.4 (agent cleanup) ◄─────────────────────────────────────────────────────────────────┤
                                                                                        ▼
                                                                              D3.5 (validation walkthrough)
                                                                                        │
                                                                      D3.2 (/status — after Epic 4 dashboard)
```

Command refactoring is sequential because each refactored command may reveal skill content that adjusts subsequent commands. New commands (except `/status`) can proceed in parallel once at least 2-3 commands have been refactored and the skill reference pattern is established.

### Exit Criteria

- [ ] Average command length under 300 lines
- [ ] All 14 commands install correctly via `agentic-mbse init`
- [ ] Each refactored command passes a fusion-tea walkthrough
- [ ] No implicit knowledge lost (Q12 resolved)
- [ ] `/status` command works end-to-end with PM dashboard

---

## 5. Epic 4: PM Script Engine (Phase 3D)

### Goal

Build the deterministic PM layer: file parsers, state derivation, AP-7 operations, dashboard generator, and CLI subcommands. This is the largest single code addition — a new Python module in `src/agentic_mbse/pm/`.

### Why This Is a Separate Epic

The PM engine is pure Python with no dependency on skills or command prompts. It depends only on the file structure and frontmatter schemas from Epic 1. It can therefore proceed in parallel with Epic 3, which depends on Epic 2 (skills). The only convergence point is the `/status` command, which belongs to Epic 3 but calls the Epic 4 dashboard.

### Deliverables

#### D4.1: Parsers (`src/agentic_mbse/pm/parser.py`)
Structured file parsers for every file the PM engine reads. Each parser validates input per the AP-7 guarantee: malformed input produces clear error messages, partial results with warnings preferred over hard failures.

Delta checklist: § 3B.1 parser items

Files to parse:
- YAML frontmatter (generic, used by spec.md, design.md, plan.md, epic files, BACKLOG.md)
- BACKLOG.md YAML structure (epics list with items, standalone list)
- REQUIREMENTS.md markdown table
- VALIDATION_MATRIX.md markdown table
- KNOWLEDGE.md DI-XXX entries
- ARCHITECTURE.md AD-XXX entries
- traceability_matrix.csv

#### D4.2: State Derivation (`src/agentic_mbse/pm/state.py`)
Work item state machine: the two-step read from [workflows.md](workflows.md) § 3.2 (file system structure → frontmatter override). Epic state derivation (draft/active/completed from sub-item states). Stage detection (which artifact files exist).

Delta checklist: § 3B.1 state items

#### D4.3: Dashboard Generator (`src/agentic_mbse/pm/dashboard.py`)
The `agentic-mbse status` output. Plain markdown that renders in terminal and IDE. Sections: work items (epic progress, item states), project rules (REQUIREMENTS.md metrics), validation status (VALIDATION_MATRIX.md metrics).

Delta checklist: § 3B.1 dashboard items

**Design question** (Q13): What's the minimum viable dashboard? Recommend starting with work item states only, then adding requirements and validation metrics incrementally.

#### D4.4: AP-7 Operations (`src/agentic_mbse/pm/operations.py`)
14 operations spanning Tier 1 (fully deterministic) and Tier 2 (script + content). Each operation is a function that takes structured input and mutates project files deterministically.

Delta checklist: § 3B.1 operations items (10 operations)

**Recommended build order** (most immediately useful first):
1. `close-item` — needed for the close flow ([workflows.md](workflows.md) § 3.5)
2. `add-insight` — needed for inline knowledge capture (B-008)
3. `save-research` — needed for deterministic file save to `knowledge/research/pending/` (AP-7; agent must not choose file path)
4. `approve-research` — needed for the research approval flow
5. `trace-element` — needed for traceability recording during implementation
6. `promote-requirement` — needed for MR-XXX → PR-XXX promotion
7. `impact-query` — needed for knowledge evolution analysis
8. `register-decision` — needed for design-to-architecture promotion
9. `update-validation` — needed for SV-XXX status tracking
10. `register-intent` — needed for `/formalize-intent` G-XXX/AQ-XXX registration in OVERVIEW.md
11. `add-item` — needed for `/status decompose` and `/backlog add` to register work items in BACKLOG.md
12. `add-validation` — needed for `/status close` and `/spec-model` to add SV-XXX entries to VALIDATION_MATRIX.md
13. `supersede-insight` — needed for knowledge evolution (T2, more complex)
14. Work item name resolution (B-014)

#### D4.5: CLI Subcommands
Wire the operations and dashboard into the `agentic-mbse` CLI as `agentic-mbse status` and `agentic-mbse pm <operation>`.

Delta checklist: § 3B.2 (2 items covering ~10 subcommands)

#### D4.6: Tests
Unit tests for parsers, state derivation, dashboard, and every operation. Integration tests for CLI subcommands. Test fixtures with sample project structures.

Delta checklist: § 3B.3 (~6 test files)

#### D4.7: Level 6 Validation Extension
Extend `level6_traceability.py` with sub-checks per [information-architecture.md](information-architecture.md) § 5.5: format check, resolvability check, completeness check, requirement coverage check.

Delta checklist: § 3B.4 (1 item with 4 sub-checks)

### Sequencing Within Epic 4

```
D4.1 (parsers) ──► D4.2 (state) ──► D4.3 (dashboard) ──► D4.5 (CLI: status)
                │                                              ▲
                └──► D4.4 (operations, in priority order) ─────┘
                                                           D4.5 (CLI: pm subcommands)
                                                               │
D4.6 (tests) ◄── accompanies each deliverable ────────────────┘
D4.7 (Level 6) ── can proceed anytime after D4.1 parsers exist
```

Parsers are the foundation — everything else reads structured files through them. State derivation and dashboard build on parsers. Operations build on parsers independently. Tests accompany each deliverable (not a separate phase). Level 6 extension can happen anytime after parsers exist.

### Exit Criteria

- [ ] `agentic-mbse status` produces accurate dashboard from fusion-tea project state
- [ ] All 14 AP-7 operations plus save-research have unit tests and pass
- [ ] Parsers handle malformed input gracefully (warnings, not crashes)
- [ ] CLI subcommands work end-to-end (integration tests with temp directories)
- [ ] Level 6 validation extended with traceability sub-checks

---

## 6. Open Design Questions by Epic

Questions from [main.md](main.md) § 5, organized by when they must be resolved.

### Must resolve during Epic 2

| # | Question | Impact if unresolved |
|---|----------|---------------------|
| Q9 | Context window impact of loading 3-4 skills? | Commands can't be written without knowing skill loading limits |
| Q10 | Skills upfront or stage-by-stage? | Affects command structure |
| Q11 | Right granularity? If sysml-conventions is 400 lines, one skill or two? | Affects skill count and command references |

### Must resolve during Epic 3

| # | Question | Impact if unresolved |
|---|----------|---------------------|
| Q12 | How to validate refactored commands don't lose knowledge? | Risk of silent regression |
| Q15 | Formal command template (structure all commands must follow)? | Affects consistency of refactoring |

### Must resolve during Epic 4

| # | Question | Impact if unresolved |
|---|----------|---------------------|
| Q13 | Minimum viable PM dashboard? | Scope of D4.3 |
| Q14 | `/analyze-models` — script, agent, or hybrid? | Whether it's in Epic 3 or Epic 4 |

### Deferred (not blocking any epic)

Q16 (git integration), Q17 (hooks), Q18 (cross-project sharing), Q19 (prototyping command).

---

## 7. Risk Register

| Risk | Severity | Likelihood | Mitigation | Epic |
|------|----------|------------|------------|------|
| fusion-tea migration breaks existing tests | High | Low | Do on git branch; run all 42 tests before merging | 1 |
| Skills are too large for context window | Medium | Medium | Skills designed to split without structural impact; measure before committing | 2 |
| Command refactoring loses implicit knowledge | High | Medium | Mandatory walkthrough against fusion-tea (D3.5); diff before/after | 3 |
| PM engine scope creep (10 operations is a lot) | Medium | Medium | Build in priority order; defer lower-priority operations if needed | 4 |
| YAML frontmatter format needs to change after Epic 1 | High | Low | Consolidate schemas into an explicit design artifact during D1.5 | 1 |
| `replicate_setup.sh` and `cmd_init()` diverge | Medium | Medium | Update both in the same commit; add a smoke test | 1, 3 |

---

## 8. Artifact Management

### Where implementation work is tracked

| Artifact | Location | Purpose |
|----------|----------|---------|
| Architecture concept | `.project/concepts/architecture-redesign/*.md` | The destination — what we're building toward |
| Delta checklist | `.project/concepts/architecture-redesign/delta-checklist.md` | Every individual change enumerated |
| This plan | `.project/concepts/architecture-redesign/implementation-plan.md` | Epic structure, sequencing, exit criteria |
| Epic tracking | `.project/backlog/` (or existing backlog mechanism) | Status of each epic and deliverable |

### Commit discipline

Each deliverable (D1.1, D1.2, etc.) should be a reviewable unit of work. Prefer one commit per deliverable where practical. The fusion-tea migration (D1.6) should be a single commit on a branch for clean revert capability.

### Branching strategy

- Epic 1 work happens on `revamp-architecture` (current branch) or a sub-branch
- fusion-tea migration happens on a branch in the fusion-tea repo
- Epics 2-4 can continue on `revamp-architecture` or split into feature branches as needed

---

## 9. Reading Order for Contributors

1. [main.md](main.md) — Problem statement, principles, architecture overview
2. [information-architecture.md](information-architecture.md) — Data models, file structure (the "what")
3. [workflows.md](workflows.md) — Lifecycles, PM engine, skills, research (the "how")
4. [components.md](components.md) — Command/skill/agent catalog (the "inventory")
5. [delta-checklist.md](delta-checklist.md) — Every change enumerated (the "diff")
6. **This document** — Epic structure, sequencing, exit criteria (the "when and how to build it")
