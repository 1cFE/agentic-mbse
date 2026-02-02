# <!-- PROJECT_NAME -->

## Project Summary

<!-- Describe your project in 2-3 paragraphs:
     - What system are you modeling and why?
     - What engineering questions must the models answer?
     - What is the validation baseline? -->

---

## Goals Registry

Goals drive the modeling effort. Each goal traces to requirements it implies.

| ID | Goal | Priority | Status | Source | Traced Requirements |
|----|------|----------|--------|--------|---------------------|

<!-- Format example:
| G-001 | Validate thermal performance against baseline | P0 | active | stakeholder interview | REQ-001, REQ-003 |
| G-002 | Enable design trade studies for component sizing | P1 | backlog | project charter | REQ-005 |
-->

---

## Analysis Questions

Questions the models must be able to answer. Each question implies modeling scope.

| ID | Question | Implies | Source | Status |
|----|----------|---------|--------|--------|

<!-- Format example:
| AQ-001 | What is the steady-state thermal margin? | Thermal model with boundary conditions | G-001 | open |
| AQ-002 | How does component mass scale with power? | Parametric mass model | G-002 | open |
-->

---

## Scope

### In Scope

<!-- What the models will cover -->

### Out of Scope

<!-- What the models will NOT cover (and why) -->

### Future Phases

<!-- Work deferred to later phases -->

---

## Success Criteria

<!-- Define what "done" looks like for this project.
     Check these off as you achieve them. -->

- [ ] <!-- Criterion 1 -->
- [ ] <!-- Criterion 2 -->
- [ ] <!-- Criterion 3 -->

---

## Project Risks

| Risk | Mitigation |
|------|-----------|
| <!-- Risk description --> | <!-- Mitigation approach --> |

---

## Getting Started

**For new collaborators:**
1. Read this overview
2. Review [MODELING_GUIDE.md](MODELING_GUIDE.md) for SysML syntax
3. Review [MODELING_PROCESS.md](MODELING_PROCESS.md) for workflow
4. Check `../work/BACKLOG.md` for work items
5. Examine example models in `models/library/`

**For agents working on this project:**
1. Read this overview and MODELING_GUIDE.md first
2. Check `../work/active/` for current priorities
3. Follow modeling conventions strictly
4. Document sources and traceability
5. Validate incrementally

---

## Resources

**Project documents:**
- [MODELING_GUIDE.md](MODELING_GUIDE.md) - SysML syntax and patterns
- [MODELING_PROCESS.md](MODELING_PROCESS.md) - MBSE methodology and workflow
- [ARCHITECTURE.md](ARCHITECTURE.md) - Model architecture decisions
- [REQUIREMENTS.md](REQUIREMENTS.md) - Project-specific modeling rules
- [VALIDATION_MATRIX.md](VALIDATION_MATRIX.md) - System verification criteria
- `../knowledge/SOURCE_INDEX.md` - Domain knowledge sources
- `CLAUDE.md` - Project instructions for Claude Code

**Related repositories:**
<!-- List any related repos -->
