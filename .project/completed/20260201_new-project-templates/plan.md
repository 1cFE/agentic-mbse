# Plan: New Project Templates (D1.1)

**Status:** Complete
**Created:** 2026-02-01
**Updated:** 2026-02-01
**Related Artifacts:**
  Spec: ./spec.md
  Design: ./design.md

---

## Implementation Phases

### Phase 1: Registry Templates (T1-T4)

Create the 4 registry templates. These are mechanical — content is fully specified in the design document, transcribed from information-architecture.md section 3.

**Files to create:**

1. `project_templates/KNOWLEDGE.md.template` — Copy T1 content block from design.md verbatim.
2. `project_templates/ARCHITECTURE.md.template` — Copy T2 content block from design.md verbatim.
3. `project_templates/REQUIREMENTS.md.template` — Copy T3 content block from design.md verbatim.
4. `project_templates/VALIDATION_MATRIX.md.template` — Copy T4 content block from design.md verbatim.

**Verification:**
- [x] Each file exists in `project_templates/`
- [x] Each renders as valid markdown (no broken tables, unclosed comments)
- [x] Entity formats match information-architecture.md section 3 (field names, allowed values)

---

### Phase 2: Epic Template (T6)

Create the epic template. Content is fully specified in the design document.

**File to create:**

5. `project_templates/epic_template.md.template` — Copy T6 template content block from design.md verbatim.

**Verification:**
- [x] YAML frontmatter fields match workflows.md section 3.6 exactly (Status, Priority, Goal, Created, Updated)
- [x] YAML frontmatter is parseable (no HTML comments in YAML block)
- [x] All 6 body sections present (Executive Summary, Context, Authority Source Dependencies, Success Criteria, Items, Sequencing, Risks)
- [x] Placeholder syntax consistent (HTML comments in body, YAML-native in frontmatter)

---

### Phase 3: Epic Guide (T5)

Create the EPIC_GUIDE.md template. This is the only template requiring original prose — the design document specifies section structure and content guidance, but the actual text must be written.

**File to create:**

6. `project_templates/EPIC_GUIDE.md.template`

**Writing approach:**
- Follow the section structure from design.md (T5 Section Structure)
- Use the content guidance for each section as the brief
- Reference the coding-focused `.project/EPIC_GUIDE.md` for tone and structure patterns, but adapt all content per the design's delta analysis
- Keep total length under 300 lines (the coding version is 328 lines — similar scope, different content)
- Use the forward-reference convention: "direct edit + validate (planned: `/quick-model`)" for commands that don't exist yet

**Verification:**
- [x] All 6 required topics covered (scale taxonomy, Goldilocks principle, decomposition process, epic file structure, anti-patterns, BACKLOG.md relationship)
- [x] No forward references to Epic 3 commands without "(planned)" qualifier
- [x] Modeling-specific sizing indicators used (not time-based)
- [x] All 6 anti-patterns present
- [x] 5-step decomposition process present

---

### Phase 4: Final Verification

Run the validation plan from the design document against all 6 files.

- [x] **Render check**: All 6 templates render as valid markdown
- [x] **Empty-state check**: No template contains fake data that could be mistaken for real entries
- [x] **Entity format check**: DI-XXX, AD-XXX, PR-XXX, SV-XXX formats match architecture docs
- [x] **YAML frontmatter check**: epic_template.md frontmatter parseable and matches schema
- [x] **Existing tests**: `uv run pytest tests/` passes (new files only — no existing tests affected)

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| EPIC_GUIDE.md prose drifts from design intent | Compare section-by-section against design.md content guidance after writing |
| Template HTML comments break markdown rendering | Test each template in a markdown previewer |
| Entity format fields don't match architecture exactly | Field-by-field comparison against information-architecture.md section 3 during Phase 4 |

---

## Sequencing Notes

- Phases 1 and 2 can execute in parallel (no dependencies between them).
- Phase 3 depends on Phase 2 only in the sense that the EPIC_GUIDE.md references the epic template format — but the design document already specifies both, so they could be written in parallel.
- Phase 4 runs after all files exist.
- In practice, all 6 files can be created in a single implementation pass, with Phase 4 as a verification gate.

---

### Implementation Notes

#### Phase 1 & 2 Completion
**Changes Made:**
- Created `project_templates/KNOWLEDGE.md.template` (19 lines) — DI-XXX entity format with all 8 fields in HTML comment
- Created `project_templates/ARCHITECTURE.md.template` (40 lines) — 3 sections, AD-XXX format in HTML comment, Package Organization table header-only
- Created `project_templates/REQUIREMENTS.md.template` (14 lines) — PR-XXX table with 5 columns, LOCAL_GUIDE.md replacement note
- Created `project_templates/VALIDATION_MATRIX.md.template` (30 lines) — SV-XXX table with 9 columns, type/mechanism reference tables
- Created `project_templates/epic_template.md.template` (100 lines) — YAML frontmatter (5 fields, parseable), 7 body sections

**Issues Encountered:** None. Content transcribed verbatim from design.md.
**Deviations from Plan:** None.

#### Phase 3 Completion
**Changes Made:**
- Created `project_templates/EPIC_GUIDE.md.template` (184 lines, under 300 limit)

**Content Coverage:**
- Scale taxonomy table (Trivial/Standard/Epic) with modeling examples
- Goldilocks principle with modeling-specific sizing indicators (definition count, authority source scope, etc.)
- 5-step decomposition process adapted for modeling domain
- Epic file structure with YAML frontmatter field explanations
- 6 anti-patterns (validation level decomposition, authority source separation, ignoring AD-XXX, waterfall phases, vague criteria, no goal traceability)
- BACKLOG.md relationship (dashboard vs. detail, script-managed vs. user-owned)

**Forward references:** `/quick-model` referenced with "(planned:" qualifier) in scale taxonomy table.
**Issues Encountered:** None.
**Deviations from Plan:** None.

#### Phase 4 Completion
**Verification Results:**
- All 6 templates render as valid markdown
- No fake data in any template (examples only in HTML comments)
- Entity formats verified field-by-field against design.md
- YAML frontmatter parses correctly with all 5 expected fields
- 324 tests pass, 1 skipped (pre-existing skip)

**Implementation Complete.**
