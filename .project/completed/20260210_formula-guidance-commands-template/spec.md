# Spec: FORMULA Guidance in Agent Commands and Project Template

**Status:** Implementation Complete
**Owner:** Reid Westwood
**Created:** 2026-02-10 00:19 UTC
**Complexity:** LOW
**Branch:** adr004-005
**Epic:** EPIC-COMPATTR-001 (Items 3 + 4)

---

## Business Goals

### Why This Matters

The validation layer (Item 1) and pattern docs (Item 2) now recognize FORMULA computed attributes as valid. But the agent commands (`/implement-model`, `/design-model`) and the project template (`MODELING_GUIDE.md.template`) still tell modelers to always extract formulas to CalcDefs. Modelers following these guides will do unnecessary work, and the guidance contradicts the validation results they see.

### Success Criteria

- [ ] All modeler-facing guidance tells a consistent story: FORMULA is valid for sibling-only arithmetic, CalcDef is for reusable/complex/calc-output cases
- [ ] A modeler running `/implement-model` or `/design-model` learns about FORMULA as a valid option
- [ ] New projects initialized via `agentic-mbse init` get updated MODELING_GUIDE with FORMULA branch

### Priority

P1 — completes EPIC-COMPATTR-001. Items 1-2 are done; these are the remaining deliverables.

---

## Problem Statement

### Current State

- `implement-model.md` line 76 says "Check ADR-002 compliance: no calc defs in `models/designs/`" but doesn't mention FORMULA as a valid alternative to CalcDef. The command gives no guidance on when attribute expressions are acceptable.
- `design-model.md` line 66 says "Design expressions must be static-evaluable (ADR-002)" but doesn't mention the ADR-002 Amendment that permits FORMULA expressions.
- `MODELING_GUIDE.md.template` lines 48-55 show a table where `Derived: = radius * 2.0` is marked **VIOLATION**, contradicting the updated validation and pattern docs. The decision text at line 55 says to extract to calc def with no FORMULA branch.

### Desired Outcome

All three files include FORMULA as a valid modeling option, with clear guidance on when to use it vs CalcDef, consistent with the updated `adr002-calculations.md` pattern doc.

---

## Scope

### In Scope

1. `claude/commands/implement-model.md` — Add FORMULA guidance
2. `claude/commands/design-model.md` — Add FORMULA recognition criteria
3. `project_templates/MODELING_GUIDE.md.template` — Update expression table and add Computed Attributes section

### Out of Scope

- Validation code changes (Item 1 — complete)
- Pattern doc changes (Item 2 — complete)
- Other commands (`spec-model.md`, `plan-model.md`, `research.md`, etc.)
- Test changes (no testable code in this spec)

### Edge Cases & Considerations

- The MODELING_GUIDE template uses `{{` placeholder markers for project-specific substitution. New content MUST NOT introduce new placeholders — only add plain markdown.
- Agent commands reference skills and pattern docs by relative convention (e.g., `adr002-calculations.md`). New references MUST follow the same convention.

---

## Requirements

### Functional Requirements

> Requirements below are from the epic (Items 3 and 4) unless marked [INFERRED].

#### 3a. `implement-model.md`

1. **FR-1**: SHALL include guidance that FORMULA attribute expressions (`attribute x = a * b`) are valid when all references are sibling attributes on the same part (per ADR-002 Amendment).
2. **FR-2**: SHALL state when to use CalcDef instead: reusable logic, complex expressions, references to calc outputs.
3. **FR-3**: SHALL reference the `adr002-calculations.md` pattern doc for the full expression taxonomy.

#### 3b. `design-model.md`

4. **FR-4**: SHALL include FORMULA as a valid option when analyzing component interfaces and deciding calculation placement.
5. **FR-5**: SHALL include decision criteria: one-off simple formula on sibling attributes → attribute expression; reusable/complex/calc-output-dependent → CalcDef.
6. **FR-6**: SHALL reference `adr002-calculations.md` pattern doc.

#### 4. `MODELING_GUIDE.md.template`

7. **FR-7**: Expression table (Calculation Architecture section) SHALL include a FORMULA row showing it as valid (PASS), and update the Derived row to clarify it means calc-output references.
8. **FR-8**: SHALL include a "Computed Attributes" subsection with FORMULA/EXPOSE/EXPOSE_COMPUTED distinction and examples.
9. **FR-9**: SHALL show both FORMULA and CalcDef as alternatives, with guidance on when to use each.
10. **FR-10**: [INFERRED] All guidance MUST be consistent with the conditions defined in `adr002-calculations.md` (FORMULA Computed Attributes section): sibling-only refs, no FeatureChainExpression, `+`/`-`/`*`/`/` operators.

---

## Acceptance Criteria

### Core Functionality

- [ ] `implement-model.md` includes FORMULA guidance with at least one example showing when FORMULA is valid
- [ ] `implement-model.md` includes CalcDef vs FORMULA decision criteria
- [ ] `implement-model.md` references `adr002-calculations.md`
- [ ] `design-model.md` includes FORMULA as a valid calculation placement option
- [ ] `design-model.md` includes decision criteria for FORMULA vs CalcDef
- [ ] `design-model.md` references `adr002-calculations.md`
- [ ] `MODELING_GUIDE.md.template` expression table includes FORMULA row with PASS result
- [ ] `MODELING_GUIDE.md.template` Derived row clarified to mean calc-output refs only
- [ ] `MODELING_GUIDE.md.template` has Computed Attributes section with FORMULA/EXPOSE/EXPOSE_COMPUTED
- [ ] All new guidance is consistent with `adr002-calculations.md` FORMULA conditions

### Quality & Integration

- [ ] Existing tests continue to pass (`uv run pytest tests/`)
- [ ] No new template placeholders introduced in MODELING_GUIDE
- [ ] Pattern doc references follow existing conventions

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_computed-attribute-integration.md` (Items 3 + 4)
- **Design:** `.project/active/formula-guidance-commands-template/design.md` (to be created)
- **Item 1 (complete):** V2 validation FORMULA exemption in `adr002.py`
- **Item 2 (complete):** Updated `docs/patterns/adr002-calculations.md` and `docs/patterns/expose-pattern.md`

---

**Next Steps:** After approval, proceed to `/_my_design` (or skip directly to implement given low complexity — all changes are content additions to existing files with clear placement)
