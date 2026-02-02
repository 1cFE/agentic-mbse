# Epic: Architecture Redesign — Knowledge (Phase 2B)

**Epic ID**: EPIC-ARCH-002
**Status**: Ready
**Priority**: P0
**Created**: 2026-02-02
**Concept**: `.project/concepts/architecture-redesign/` (main.md, workflows.md § 1, components.md § 2, delta-checklist.md § 2)
**Delta Checklist**: `.project/concepts/architecture-redesign/delta-checklist.md` §§ 2.1–2.4
**Depends On**: EPIC-ARCH-001 (Structure) — file structure, entity formats, and directory paths must be settled

---

## Executive Summary

Extract shared knowledge from bloated commands into reusable skills, creating the knowledge layer that sits between the information architecture (Epic 1) and the command layer (Epic 3). Seven new skills are extracted from existing commands and architecture documents; two existing skills are evaluated and revised; all skills are measured for context window impact and registered in `cmd_init()`.

**Critical Success Factor**: All 9 skills (7 new + `toolkit-awareness` revised + `record-learning` disposition decided) exist with SKILL.md files under 200 lines each, context window measurements are documented, and `agentic-mbse init` installs them correctly.

---

## Why This Epic Comes Second

Commands are too long because they embed knowledge that should be shared (P1). `design-model.md` is 1,345 lines — roughly 600 lines of SysML syntax patterns, 200 lines of validation guidance, 150 lines of file structure rules. The remaining commands average 443 lines with similar embedded knowledge.

Skills serve as the **knowledge contracts** between the architecture and the commands:

- **Skills reference the information architecture** (Epic 1). They point to `knowledge/KNOWLEDGE.md`, `modeling_project/REQUIREMENTS.md`, `work/BACKLOG.md` — paths that must be settled before skills can be written.
- **Commands reference skills** (Epic 3). Commands can't be refactored to 200–300 lines until skills exist and their granularity is measured.
- **Skills don't depend on commands or the PM engine**. They are pure knowledge — no workflow logic, no agent prompts, no project-specific data.

If skills are written after commands are refactored, the refactoring would just be rearranging the same inline content. If skills are written before the file structure is settled, they'd reference wrong paths.

---

## Open Design Questions (Must Resolve During This Epic)

Three questions from main.md § 5 are blocking. This epic must resolve all three before D2.3 (registration).

| # | Question | Impact if unresolved | Proposed resolution approach |
|---|----------|---------------------|------------------------------|
| Q9 | What's the context window impact of loading 3–4 skills simultaneously? | Commands can't be written without knowing skill loading limits | D2.4: empirical measurement — token counts per skill, simulated command loads |
| Q10 | Should skills load all content upfront or stage-by-stage? | Affects command structure and skill reference patterns | D2.4: if total skill payload for a command is <3,000 tokens, load upfront; otherwise stage |
| Q11 | What's the right granularity? If `sysml-conventions` exceeds 200 lines, one skill or two? | Affects skill count and command references | D2.1: write each skill, measure; split only if SKILL.md exceeds 200 lines after focused editing |

---

## Success Criteria

- [ ] 7 new skills exist in `claude/skills/` with SKILL.md files under 200 lines each
- [ ] `toolkit-awareness` SKILL.md revised with new PM commands, slash commands, and directory paths
- [ ] `record-learning` disposition decided and documented (keep with revisions, merge, or deprecate)
- [ ] Context window measurements documented (token counts per skill, simulated command loads)
- [ ] Skill loading strategy decided (Q9, Q10, Q11 all resolved with documented rationale)
- [ ] `agentic-mbse init` installs all skills correctly (MBSE_SKILLS updated)
- [ ] `replicate_setup.sh` installs same skill set (or divergence documented as intentional)
- [ ] All existing agentic-mbse tests pass (`uv run pytest tests/`)

---

## Deliverables

Six deliverables with a dependency structure (see [Sequencing](#sequencing) below).

### D2.1: New Skills (6 skills)

**Type**: Implementation
**Status**: Complete
**Dependencies**: Epic 1 complete (directory paths settled)
**Delta checklist**: § 2.1 (7 items + optional reference subdirectories)

**Objective**: Create 7 skill directories in `claude/skills/`, each with a `SKILL.md` under 200 lines and optional `references/` subdirectory.

**Design constraints**:
- Each SKILL.md follows the existing frontmatter pattern: `name`, `description`, `allowed-tools`, `user-invocable`
- Skills contain **knowledge** (principles, rules, patterns, formats) — NOT workflow logic (that stays in commands) or project-specific data (that's in the information architecture)
- Skills reference new directory paths from Epic 1 (`knowledge/`, `modeling_project/`, `work/`, `data/`)
- Content is extracted from existing commands (primary source) and architecture documents (supplementary source)

#### Skill 1: `sysml-conventions`

| Field | Value |
|-------|-------|
| Primary source | Extract from `design-model.md` (~600 lines of embedded SysML knowledge) |
| Supplementary | `MODELING_GUIDE.md.template` reference material (flagged for extraction in D1.2) |
| Key content | SysML v2 syntax rules, naming conventions, common patterns and idioms, pitfalls/gotchas, code stencils for definitions/usages/connections/constraints |
| Commands that reference it | `design-model`, `implement-model`, `audit-models`, `quick-model`, `review-model` |
| Allowed tools | `Read, Grep, Glob` (read-only — knowledge reference) |
| User-invocable | No |

**Content outline for SKILL.md**:
1. When to reference (designing, implementing, reviewing SysML models)
2. Naming conventions (definitions, usages, attributes, ports)
3. Definition vs usage patterns (library/ vs designs/ separation)
4. Common structural patterns (part defs with ports, connection defs, calc defs with constraints)
5. Pitfalls to avoid (qualified names in expressions, missing imports, redefines vs specializes)
6. Code stencils (optional — may move to `references/stencils.md` if SKILL.md exceeds 200 lines)

**Risk**: This is the highest-volume extraction. If the distilled SKILL.md exceeds 200 lines, split into `sysml-conventions/SKILL.md` (principles + rules) and `sysml-conventions/references/patterns.md` (examples + stencils). The SKILL.md is always loaded; references are loaded on demand.

#### Skill 2: `model-validation`

| Field | Value |
|-------|-------|
| Primary source | Extract from `design-model.md` and `implement-model.md` |
| Supplementary | Validation pyramid code in `src/agentic_mbse/validation/` |
| Key content | 8-level quality pyramid summary, CLI usage (`agentic-mbse validate`), per-level criteria, regression test patterns, when to run which levels |
| Commands that reference it | `design-model`, `implement-model`, `audit-models`, `plan-model`, `quick-model`, `review-model`, `analyze-models` |
| Allowed tools | `Read, Grep, Glob, Bash` (needs Bash to run `agentic-mbse validate`) |
| User-invocable | No |

**Content outline for SKILL.md**:
1. The 8-level pyramid (one-line summary per level with blocking status)
2. CLI invocation patterns (validate, --level, --complete, --verbose)
3. When to validate during workflow (after prototype, after each implementation phase, final)
4. Reading validation output (interpreting errors, warnings, info)
5. Regression test patterns (pytest markers, skip conditions for codegen-dependent tests)

#### Skill 3: `project-structure`

| Field | Value |
|-------|-------|
| Primary source | Extract from `design-model.md`, `spec-model.md`, `implement-model.md` |
| Supplementary | `information-architecture.md` § 2 (file structure), Epic 1 templates |
| Key content | 4-directory model (knowledge/, modeling_project/, work/, data/), library/ vs designs/ separation, file organization conventions, EXPOSE pattern, cross-file dependency rules |
| Commands that reference it | `design-model`, `implement-model`, `spec-model`, `onboard`, `review-model`, `analyze-models`, `formalize-intent` |
| Allowed tools | `Read, Grep, Glob` |
| User-invocable | No |

**Content outline for SKILL.md**:
1. The 4-directory information architecture (what goes where, with paths)
2. Model file organization (library/ subdivisions, designs/ per-config)
3. Library vs designs separation rule (definitions in library/, usages in designs/)
4. Cross-file dependency rules (unidirectional imports, package boundaries)
5. EXPOSE pattern (when and how to expose intermediate values)
6. Key project files and their roles (OVERVIEW.md, ARCHITECTURE.md, REQUIREMENTS.md, etc.)

#### Skill 4: `source-traceability`

| Field | Value |
|-------|-------|
| Primary source | Extract from `design-model.md`, `manage-sources.md`, `research.md` |
| Supplementary | `information-architecture.md` § 5 (traceability model), `docs/source-index.md` |
| Key content | SOURCE_INDEX.md format, citation patterns for doc comments (Source/Reference fields), traceability_matrix.csv schema, doc comment requirements, traceability chain (DI-XXX → PR-XXX → model element → authority source) |
| Commands that reference it | `design-model`, `spec-model`, `audit-models`, `research`, `manage-sources`, `implement-model` |
| Allowed tools | `Read, Grep, Glob` |
| User-invocable | No |

**Content outline for SKILL.md**:
1. The durable traceability chain (DI-XXX → PR-XXX → element → source)
2. SOURCE_INDEX.md format (entity format from information-architecture.md § 3 Role 1)
3. Doc comment requirements (Source, Reference, Last Updated fields)
4. Citation patterns (file:line for codebases, section for specs, URL for online)
5. Traceability matrix schema (`data/traceability_matrix.csv` columns and their meaning)
6. When to record traceability (during implementation, not after)

#### Skill 5: `epic-decomposition`

| Field | Value |
|-------|-------|
| Primary source | New content from `workflows.md` § 2.1 (scale taxonomy), § 3.6 (epic tracking) |
| Supplementary | `EPIC_GUIDE.md.template` (created in D1.1), `information-architecture.md` § 3 Role 3 (goals) |
| Key content | Scale taxonomy (Trivial/Standard/Epic), Goldilocks principle for modeling work, decomposition process (5 steps), anti-patterns, epic file structure, relationship to BACKLOG.md |
| Commands that reference it | `backlog`, `status`, `onboard` |
| Allowed tools | `Read, Grep, Glob` |
| User-invocable | No |

**Content outline for SKILL.md**:
1. Scale taxonomy (Trivial → /quick-model, Standard → /spec-model, Epic → /backlog decompose)
2. Goldilocks principle (too large / too small / just right indicators for modeling work)
3. Decomposition by domain concern (NOT by workflow phase, NOT by validation level)
4. Authority source dependency surfacing
5. Item independence checking
6. Anti-patterns (phase-as-item, validation-level decomposition, vague criteria, no goal traceability)

**Note**: Much of this content already exists in `EPIC_GUIDE.md.template`. The skill is a concise distillation for command context; EPIC_GUIDE.md remains the detailed reference for users writing epics.

#### Skill 6: `requirements-tracking`

| Field | Value |
|-------|-------|
| Primary source | New content from `information-architecture.md` § 3 Role 4 |
| Supplementary | `workflows.md` § 3.5 (close flow trigger questions), main.md AP-7 operations table |
| Key content | REQUIREMENTS.md format (PR-XXX table), two-tier structure (MODELING_GUIDE.md baseline + REQUIREMENTS.md extensions), promotion path from per-feature MR-XXX to project-wide PR-XXX, enforcement methods, compliance checking patterns |
| Commands that reference it | `design-model`, `audit-models`, `review-model`, `status`, `implement-model` |
| Allowed tools | `Read, Grep, Glob` |
| User-invocable | No |

**Content outline for SKILL.md**:
1. Two-tier requirements (MODELING_GUIDE.md baseline + REQUIREMENTS.md extensions)
2. PR-XXX entity format (ID, Requirement, Source, Enforcement, Validation Method)
3. Promotion path: when a per-feature MR-XXX becomes a project-wide PR-XXX
4. Sub-types (modeling patterns, structural rules, documentation rules, enforcement rules, naming, domain requirements)
5. Enforcement methods (validation rule vs design review vs regression test)
6. Compliance checking (how commands verify against REQUIREMENTS.md)

#### Skill 7: `formalize-intent` (reference material)

**Note**: After reviewing the architecture, the `/formalize-intent` command needs knowledge about the intent formalization flow (modeling_project/intent/ → OVERVIEW.md G-XXX/AQ-XXX extraction). This is not listed as a separate skill in the original components.md catalog. However, the `project-structure` skill already covers the 4-directory model and key file roles. The intent formalization knowledge fits naturally within `project-structure` rather than requiring its own skill.

**Resolution**: No separate `formalize-intent` skill. The `project-structure` skill includes intent formalization context (where intent docs live, what OVERVIEW.md contains, the G-XXX/AQ-XXX entity formats). This keeps the skill count at **6 new skills** (not 7) — sysml-conventions, model-validation, project-structure, source-traceability, epic-decomposition, requirements-tracking.

**Reconciliation with implementation-plan.md**: The plan lists 7 skills. Six are extracted as above. The seventh slot was `toolkit-awareness` (revision of existing) — which is handled in D2.2. The net new skill count is 6; the total skill count including revisions is 9 (6 new + toolkit-awareness revised + record-learning evaluated + python-debugger unchanged).

**Exit criteria**:
- [x] 6 new skill directories exist in `claude/skills/`
- [x] Each has a `SKILL.md` under 200 lines with correct frontmatter
- [x] Each SKILL.md contains only knowledge (no workflow logic, no project-specific data)
- [x] Skills reference new directory paths from Epic 1 (knowledge/, modeling_project/, work/, data/)
- [x] Content extracted from commands is identified and marked for removal in Epic 3

---

### D2.2: Existing Skill Evaluation

**Type**: Evaluation + Implementation
**Status**: Complete
**Dependencies**: D2.1 (new skills establish the patterns)
**Delta checklist**: § 2.2 (2 items)

**Objective**: Evaluate and update the two existing non-debugger skills against the architecture.

#### `toolkit-awareness` — REVISE

**Current state**: 103 lines. References `README.md` and `CLAUDE.md` as authority. Lists validation CLI and slash commands.

**Required changes**:
1. Add new PM CLI commands: `agentic-mbse status`, `agentic-mbse pm <operation>` (close-item, approve-research, trace-element, promote-requirement, register-decision, update-validation, add-insight, impact-query, supersede-insight)
2. Add new slash commands: `/quick-model`, `/review-model`, `/analyze-models`, `/status`, `/formalize-intent`
3. Update directory structure references from `modeling_pm/` to `knowledge/`, `modeling_project/`, `work/`, `data/`
4. Add key project files and their roles (SOURCE_INDEX.md at `knowledge/`, KNOWLEDGE.md, ARCHITECTURE.md, REQUIREMENTS.md, VALIDATION_MATRIX.md, BACKLOG.md)
5. Update validation invocation patterns if any CLI flags change

**Size risk**: Low — additions are structured lists. Should remain under 200 lines.

#### `record-learning` — EVALUATE

**Current state**: 155 lines. Records process learnings (syntax gotchas, import patterns, workarounds) to `modeling_pm/learnings/RAW_LEARNINGS.md`. User-invocable.

**Evaluation questions**:
1. **Scope overlap with inline knowledge capture**: The architecture introduces `add-insight` (AP-7 T1) for capturing domain insights (DI-XXX entries in KNOWLEDGE.md) during any command. Does `record-learning` overlap?
2. **Path update**: Currently writes to `modeling_pm/learnings/RAW_LEARNINGS.md` — must update to `work/learnings/RAW_LEARNINGS.md`.
3. **Role clarity**: Domain insights (DI-XXX) capture *what the domain teaches us* (e.g., "HTS magnets cost 3x LTS at scale"). Process learnings capture *what the tooling teaches us* (e.g., "sum() needs explicit import"). These are different concerns with different consumers.

**Proposed disposition**: **KEEP with revisions**.
- Update file path to `work/learnings/RAW_LEARNINGS.md`
- Update `syside check` reference to `agentic-mbse validate`
- Add scope clarification: `record-learning` is for **process/tooling learnings** (SysML syntax, parser behavior, workflow patterns); **domain insights** go through `add-insight` → KNOWLEDGE.md
- Consider: should `record-learning` also suggest DI-XXX candidates when a learning has domain implications? (e.g., "this SysML limitation means we need a different modeling approach for X" is both a process learning and a domain insight)

**Decision gate**: Disposition must be confirmed before D2.3 (registration). If deprecated, remove from MBSE_SKILLS. If kept, update and include.

**Exit criteria**:
- [x] `toolkit-awareness` SKILL.md updated with all new commands, paths, and project files
- [x] `record-learning` disposition decided with documented rationale (KEEP — see design.md § Disposition Rationale)
- [x] If kept: `record-learning` paths updated, scope clarified, DI-XXX cross-suggestion added
- [N/A] If deprecated: removal plan documented (what replaces it)

---

### D2.3: Skill Registration

**Type**: Implementation
**Status**: Pending
**Dependencies**: D2.1 (skills exist), D2.2 (existing skills evaluated), D2.4 (measurement confirms no granularity changes needed)
**Delta checklist**: § 2.3 (2 items)

**Objective**: Register all skills in the installation pipeline so `agentic-mbse init` and `replicate_setup.sh` install them to target projects.

**Changes to `src/agentic_mbse/cli/__init__.py`**:

Update `MBSE_SKILLS` list to include new skills:
```python
MBSE_SKILLS = [
    "python-debugger",
    "record-learning",       # or remove if deprecated in D2.2
    "toolkit-awareness",
    "sysml-conventions",     # NEW
    "model-validation",      # NEW
    "project-structure",     # NEW
    "source-traceability",   # NEW
    "epic-decomposition",    # NEW
    "requirements-tracking", # NEW
]
```

**Changes to `scripts/replicate_setup.sh`**:

Add new skills to the install loop. Must match `MBSE_SKILLS` exactly (reconciliation from D1.4 ensures these are aligned).

**Verification**: After registration, run:
1. `uv run agentic-mbse init /tmp/test-project` — verify all skill directories appear in `.claude/skills/`
2. `uv run agentic-mbse init --dev` on agentic-mbse repo — verify symlinks for all skills
3. Check each skill directory has at minimum `SKILL.md`

**Exit criteria**:
- [ ] `MBSE_SKILLS` list updated with all new skills
- [ ] `replicate_setup.sh` updated with matching skill set
- [ ] `agentic-mbse init` installs all skills to `.claude/skills/`
- [ ] `agentic-mbse init --dev` creates symlinks for all skills
- [ ] All existing tests pass (`uv run pytest tests/`)

---

### D2.4: Context Window Measurement

**Type**: Design activity (empirical measurement + decision)
**Status**: Pending
**Dependencies**: D2.1 (skills must exist to measure them)
**Delta checklist**: § 2.4 (5 items)

**Objective**: Measure the context window impact of loading skills, resolve Q9/Q10/Q11, and determine if any skills need splitting or if the loading strategy needs to change.

**Measurement protocol**:

1. **Token count per skill**: Count tokens in each SKILL.md using a tokenizer (Claude tokenizer or tiktoken approximation). Record in a table.

2. **Skill combination loads**: For each command in the component catalog (components.md § 1), compute the total token load from its declared skill dependencies:

   | Command | Skills | Total skill tokens |
   |---------|--------|--------------------|
   | `/design-model` | sysml-conventions, project-structure, model-validation, source-traceability | ? |
   | `/implement-model` | sysml-conventions, model-validation, project-structure | ? |
   | `/spec-model` | project-structure, source-traceability | ? |
   | `/audit-models` | model-validation, source-traceability, requirements-tracking | ? |
   | `/review-model` | sysml-conventions, model-validation, project-structure, requirements-tracking | ? |
   | `/quick-model` | sysml-conventions, model-validation | ? |
   | `/status` | epic-decomposition, requirements-tracking | ? |
   | `/backlog` | epic-decomposition | ? |
   | `/onboard` | project-structure, source-traceability, epic-decomposition | ? |
   | `/research` | source-traceability | ? |
   | `/manage-sources` | source-traceability | ? |
   | `/formalize-intent` | project-structure | ? |
   | `/analyze-models` | project-structure, model-validation | ? |

3. **Baseline comparison**: Current commands embed all knowledge inline. Measure the token count of the current `design-model.md` (1,345 lines) as the baseline. Skills should **redistribute** tokens, not add to total. The combined payload of a refactored command + its skills should be comparable to or less than the current monolithic command.

4. **Context pressure assessment**: Determine the highest skill load (likely `/design-model` with 4 skills or `/review-model` with 4 skills). If the total exceeds ~4,000 tokens for skills alone, consider:
   - Moving examples and stencils to `references/` (loaded on demand, not upfront)
   - Splitting the largest skill(s)
   - Staging skills by command phase rather than loading all upfront

5. **Document results**: Record measurements and decisions in a measurement report at `.project/active/architecture-knowledge/measurement-report.md` (or similar work item location).

**Decision criteria**:

| Condition | Action |
|-----------|--------|
| All SKILL.md files < 200 lines AND max command skill load < 4,000 tokens | Load all skills upfront. Q9/Q10/Q11 resolved. |
| Some SKILL.md files > 200 lines BUT max load < 4,000 tokens | Move overflow content to `references/`. Keep loading upfront. |
| Max command skill load > 4,000 tokens | Stage skills by command phase. Document which skills load at which stage. |
| A single skill > 300 lines even after reference extraction | Split the skill. Update command references. |

**Note**: The 4,000-token threshold is a starting estimate. The actual constraint is that skills + command prompt + typical project context (files being read) must leave sufficient context for the agent's working memory. This may need adjustment based on empirical experience in Epic 3 walkthroughs.

**Exit criteria**:
- [ ] Token count measured for each SKILL.md
- [ ] Skill combination loads computed for each command
- [ ] Baseline comparison documented (current vs proposed)
- [ ] Q9 resolved: context window impact quantified
- [ ] Q10 resolved: loading strategy decided (upfront vs staged)
- [ ] Q11 resolved: granularity confirmed or adjusted
- [ ] Measurement report documented

---

### D2.5: Skill Content Extraction Mapping

**Type**: Design artifact
**Status**: Pending
**Dependencies**: D2.1 (skills written), D2.4 (granularity confirmed)

**Objective**: Produce an explicit mapping from skill content back to the command lines it was extracted from. This is the bridge artifact between Epic 2 and Epic 3 — it tells Epic 3 exactly what to remove from each command.

**Format**: A table per command listing:
- Line ranges in the current command that move to skills
- Which skill absorbs each range
- What remains after extraction (the command's own workflow logic)

**Example**:
```
design-model.md (1,345 lines):
  Lines 45-280:  SysML syntax patterns     → sysml-conventions
  Lines 281-380: Validation guidance         → model-validation
  Lines 381-450: File structure rules        → project-structure
  Lines 451-520: Citation/source patterns    → source-traceability
  Lines 521-1345: Design workflow logic      → STAYS (refactored in Epic 3)
```

This artifact prevents knowledge loss during Epic 3 refactoring (addresses Q12 risk). The walkthrough (D3.5) can verify against this mapping.

**Exit criteria**:
- [ ] Extraction mapping exists for all 9 existing commands
- [ ] Every line range in current commands is accounted for (moved to skill OR stays in command)
- [ ] No knowledge is unaccounted for

---

## Sequencing

```
D2.1 (new skills, 6 skills) ──► D2.4 (measurement) ──► Adjust if needed ──► D2.3 (registration)
D2.2 (existing skill eval) ──┘                                            │
                                                                           │
                                        D2.5 (extraction mapping) ◄────────┘
```

- **D2.1** and **D2.2** can proceed in parallel — new skills and existing skill evaluation are independent
- **D2.4** depends on skills being written (can't measure what doesn't exist)
- **D2.3** depends on D2.4 (if measurement forces granularity changes, those changes affect what gets registered)
- **D2.5** depends on D2.1 and D2.4 (need final skill content and confirmed granularity to map extraction)
- If D2.4 measurement forces skill splits, loop back to D2.1 for affected skills before proceeding to D2.3

---

## Risks

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| Skills too large for context window (Q9) | Medium | Medium | Skills designed to split without structural impact. SKILL.md is the concise entry point; `references/` holds overflow. Measure before committing (D2.4). |
| Extraction loses implicit knowledge from commands | High | Medium | D2.5 produces explicit mapping. Epic 3's D3.5 walkthrough verifies no loss. |
| `sysml-conventions` is too large (Q11) | Medium | Medium | Expected — this skill covers the most ground. Plan for `references/patterns.md` from the start. |
| Skill granularity needs multiple iterations | Low | Medium | Each iteration is small (editing markdown files). No downstream dependencies break if a skill splits — only the command reference list changes. |
| `record-learning` evaluation reveals a deeper design issue | Low | Low | Scope is contained. Worst case: deprecate and rely on close-flow trigger questions + `add-insight` for all knowledge capture. |
| New skills interact poorly with Claude Code's skill loading | Medium | Low | Test with `agentic-mbse init` on a fresh project and verify skills appear in Claude Code's skill discovery. |

---

## What This Epic Does NOT Include

Explicitly out of scope (handled in later epics):

- **Command refactoring** — Epic 3 removes extracted knowledge from commands and adds skill references. This epic writes the skills; Epic 3 rewires the commands.
- **New commands** (`/quick-model`, `/review-model`, `/analyze-models`, `/status`, `/formalize-intent`) — Epic 3
- **PM engine code** — Epic 4 builds the Python parsers, state derivation, and CLI subcommands
- **Agent changes** — Epic 3 (D3.4: agent cleanup)
- **Detailed command template** — Epic 3 (Q15: formal command structure)

This epic produces the **knowledge layer** that Epic 3 and Epic 4 build on. It creates skills and measures their impact, but does not refactor the commands that consume them.

---

## Relationship to Epic 1

Epic 1 (Structure) established the information architecture: 4-directory model, entity formats, YAML frontmatter schemas, `cmd_init()` rewiring. This epic builds on that foundation:

- Skills reference the directory paths created in Epic 1 (`knowledge/SOURCE_INDEX.md`, `modeling_project/REQUIREMENTS.md`, etc.)
- Skills reference the entity formats defined in Epic 1 (DI-XXX, PR-XXX, AD-XXX, SV-XXX, G-XXX, AQ-XXX)
- `toolkit-awareness` skill update (D2.2) adds the new project files created in Epic 1
- Skill registration (D2.3) extends the same `MBSE_SKILLS` and `replicate_setup.sh` mechanisms updated in D1.4

Epic 1's D1.2 flagged `MODELING_GUIDE.md.template` reference material for extraction — that extraction happens here, feeding into the `sysml-conventions` and `model-validation` skills.

---

## Relationship to Epic 3

Epic 3 (Commands) is the primary consumer of this epic's output:

- Each refactored command replaces inline knowledge with skill references
- The extraction mapping (D2.5) is Epic 3's primary input — it specifies exactly what to remove
- The context window measurements (D2.4) determine whether commands load skills upfront or stage them
- Epic 3's validation walkthrough (D3.5) verifies no knowledge was lost by cross-referencing against D2.5

The `/status` command (Epic 3) also depends on Epic 4 (PM engine), but that is not this epic's concern.

---

**Last Updated**: 2026-02-02
**Next Action**: D2.1 (write new skills) and D2.2 (evaluate existing skills) in parallel
