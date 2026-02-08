# D3.5 Interactive Walkthrough Checklist

**Status:** Pending — requires live Claude Code sessions against fusion-tea (items 1–5, 7)
**Blocked by:** Needs interactive Claude Code sessions; cannot be completed in batch
**Q12 Cross-Reference Audit:** PASS (see `q12-cross-reference-audit.md`)

---

## Walkthrough Items

Each item requires running the indicated command in a live Claude Code session against fusion-tea work items. Pass/fail criteria below.

### Item 1: `/spec-model`

**Fusion-tea scenario:** Spec a new work item (e.g., new subsystem model or a backlog item from `work/BACKLOG.md`)

**Verify:**
- [ ] Command reads `modeling_project/OVERVIEW.md` and references G-XXX goals
- [ ] Command reads `knowledge/KNOWLEDGE.md` and incorporates relevant DI-XXX insights
- [ ] YAML frontmatter generated correctly (Status, Scale, Epic, Owner, Created, Updated)
- [ ] MR-XXX requirements defined with measurable criteria
- [ ] SV-XXX entries suggested for VALIDATION_MATRIX.md
- [ ] Skill references (project-structure, source-traceability, model-validation, requirements-tracking) provide adequate guidance

### Item 2: `/design-model`

**Fusion-tea scenario:** Design against an existing spec (use a completed spec from `work/active/`)

**Verify:**
- [ ] Skill references provide equivalent SysML syntax guidance (sysml-conventions)
- [ ] Command reads `modeling_project/ARCHITECTURE.md` for existing AD-XXX decisions
- [ ] Command reads `modeling_project/REQUIREMENTS.md` for PR-XXX compliance
- [ ] Design workflow phases execute correctly (understand, analyze, design, prototype, validate, document)
- [ ] Validation skill (model-validation) provides adequate validation guidance
- [ ] Source-traceability skill provides citation patterns

### Item 3: `/implement-model`

**Fusion-tea scenario:** Implement a phase of an existing plan (use a planned work item from `work/active/`)

**Verify:**
- [ ] Command reads plan and executes phases correctly
- [ ] Inline knowledge capture: agent suggests `agentic-mbse pm add-insight` calls when discovering domain insights
- [ ] Traceability recording: agent suggests `agentic-mbse pm trace-element` for significant model elements
- [ ] Validation at each phase (Levels 1-3)
- [ ] Backward navigation handling when design issues are discovered
- [ ] Phase completion documentation

### Item 4: `/audit-models`

**Fusion-tea scenario:** Audit existing fusion-tea models in `models/`

**Verify:**
- [ ] Decision promotion flow works (agent offers to register patterns as AD-XXX)
- [ ] SV-XXX update suggestions present
- [ ] Requirements compliance checking against PR-XXX
- [ ] Validation pyramid levels applied correctly
- [ ] Numerical verification with baseline sources
- [ ] Audit report follows expected structure

### Item 5: `/research`

**Fusion-tea scenario:** Research a domain question using sources from `knowledge/SOURCE_INDEX.md`

**Verify:**
- [ ] Reads SOURCE_INDEX.md first to discover available sources
- [ ] Approval workflow: suggests `agentic-mbse pm approve-research` after findings
- [ ] DI-XXX insight candidate suggestions
- [ ] File save via `agentic-mbse pm save-research` script (not direct file write)
- [ ] Knowledge conflict detection against existing DI-XXX entries
- [ ] Agent spawning works correctly (sysml-expert, kerml-expert, Explore, general-purpose)

### Item 7: Cross-Command Pipeline

**Fusion-tea scenario:** Full pipeline on a single work item: spec -> design -> plan -> implement -> audit

**Verify:**
- [ ] Data flows correctly between stages (spec.md -> design.md -> plan.md -> models/)
- [ ] YAML frontmatter consistent across stages
- [ ] No broken references between command outputs
- [ ] Each stage correctly reads the output of the previous stage
- [ ] Validation accumulates correctly across the pipeline
- [ ] Traceability maintained from requirements through implementation

---

## Execution Notes

- Use fusion-tea repo at `/home/reid/1cfe/fusion-tea`
- Pick work items that exercise real modeling scenarios, not toy examples
- Record pass/fail for each checkbox
- For any failure, document: what was expected, what happened, and recommended fix
- After all walkthroughs, update the epic exit criteria
