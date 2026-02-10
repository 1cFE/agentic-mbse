# Spec: Pattern Documentation — Expression Taxonomy and Decision Flow

**Status:** Implementation Complete
**Owner:** Reid Westwood
**Created:** 2026-02-09 23:50 UTC
**Complexity:** LOW
**Branch:** adr004-005
**Epic:** EPIC-COMPATTR-001, Item 2

---

## Business Goals

### Why This Matters

Item 1 of the epic is complete — `check_static_expressions()` now exempts FORMULA patterns (sibling-only arithmetic). But the two pattern docs that ship with the toolkit still tell modelers the opposite: `adr002-calculations.md` lists `attribute area = length * width` as an **invalid pattern** requiring extraction to a CalcDef, and `expose-pattern.md` doesn't distinguish FORMULA from EXPOSE at all.

This means the documentation actively contradicts the validator. Modelers following the docs will perform unnecessary CalcDef ceremony for simple sibling arithmetic. Modelers who skip it will be confused when validation passes despite the docs saying it shouldn't. The docs and the validator must tell the same story.

### Success Criteria

- [ ] A modeler reading `adr002-calculations.md` understands that `attribute area = length * width` is valid when all refs are sibling attributes
- [ ] A modeler reading `expose-pattern.md` understands the distinction between FORMULA, EXPOSE_PURE, and EXPOSE_COMPUTED
- [ ] Both docs are consistent with the ADR-002 amendment, ADR-004, and ADR-005

### Priority

P1. This is the second item on the epic's critical path (Item 1 → **Item 2** → Items 3+4). Items 3 (agent commands) and 4 (project templates) are blocked on this because they reference the pattern docs.

---

## Problem Statement

### Current State

**`docs/patterns/adr002-calculations.md`:**
- Rule 3 (line 29): Says "Design attributes contain literals, bindings, or **static expressions**" — no mention of FORMULA
- Expression taxonomy (lines 35-43): Has "Derived expression" row with FAIL result for `= radius * 2.0` — doesn't distinguish sibling refs (now valid) from calc output refs (still invalid)
- "Invalid Pattern" section (lines 65-101): Shows `attribute area = length * width` as a violation with CalcDef as the only resolution
- "Supported Static Operators" section (lines 111-115): Lists "References to other design attributes" as not supported — now incorrect for sibling refs
- Decision flow (lines 202-217): Routes all expressions with design attribute refs to "EXTRACT TO CALC DEF" — misses the FORMULA branch
- Common Mistakes (lines 171-182): "Derived expressions in attributes" shows `diameter = radius * 2.0` as always wrong — now wrong guidance for sibling refs

**`docs/patterns/expose-pattern.md`:**
- No mention of FORMULA at all
- A modeler encountering both `attribute area = length * width` and `attribute result = my_calc.output` has no guidance on what distinguishes them or why they're treated differently

### Desired Outcome

Both pattern docs accurately reflect the ADR-002 amendment. FORMULA is presented as a valid option alongside EXPOSE and CalcDef. The distinction between FORMULA (sibling arithmetic → pipeline module), EXPOSE_PURE (calc output forwarding → alias), and EXPOSE_COMPUTED (calc output + arithmetic → not yet supported) is clear.

---

## Scope

### In Scope

- Modify `docs/patterns/adr002-calculations.md` (6 sections)
- Modify `docs/patterns/expose-pattern.md` (1 new section)

### Out of Scope

- Agent command updates (Item 3)
- Project template updates (Item 4)
- Other pattern docs (no changes needed)
- Code changes (Item 1 already complete)

### Edge Cases & Considerations

- The "Invalid Pattern" section is referenced by the validator's error messages (V2_DYNAMIC_EXPRESSION suggests "Consider extracting to a calc def"). The section should present CalcDef as an alternative, not remove it — some modelers may prefer CalcDef for readability even when FORMULA works.
- The "Supported Static Operators" section describes what's valid in design attributes generally, not just for the static evaluator. FORMULA permits sibling attribute references with arithmetic operators, so this section needs updating.

---

## Requirements

### Functional Requirements

> Requirements below are from user's request (epic Item 2) unless marked [INFERRED].

#### 2a. `adr002-calculations.md`

1. **FR-1**: Rule 3 description (line 29) MUST include FORMULA expressions: "Design attributes contain literals, bindings, static expressions, or **FORMULA expressions** (sibling-only arithmetic)"

2. **FR-2**: Expression taxonomy table (lines 35-43) MUST add a FORMULA row with PASS result between "True static" and the current "Derived expression" row. The existing "Derived expression" row MUST be narrowed to clarify it means calc-output references only.

   Updated taxonomy:
   | Expression Type | Location | Feature Refs | Result | Example |
   |-----------------|----------|--------------|--------|---------|
   | Literal value | `designs/` attribute | 0 | PASS | `= 3.0 [m]` |
   | True static | `designs/` attribute | 0 | PASS | `= 3.14159 * 2.0` |
   | **FORMULA expression** | `designs/` attribute | >=1 (sibling attrs only) | **PASS** | `= length * width` |
   | EXPOSE pattern | `designs/` attribute | 1 (calc output) | PASS | `= my_calc.output` |
   | Calc def formula | `library/` calc def | N/A | N/A | `out result = input * 0.2;` |
   | Binding reference | Calc usage binding | N/A | N/A | `in value = system.property;` |
   | Derived expression | `designs/` attribute | >=1 (calc output refs) | **FAIL** | `= calc.output * 0.95` |

3. **FR-3**: "Invalid Pattern" section (lines 65-101) MUST add an amendment callout noting that `attribute area = length * width` is NOW valid when all refs are sibling attributes on the same part. The CalcDef resolution MUST be preserved as an alternative approach, not removed.

4. **FR-4**: "Supported Static Operators" section (lines 104-116) MUST update the "Not supported" list. "References to other design attributes" MUST be removed or amended to note that sibling attribute references ARE supported via FORMULA. Cross-part attribute references and calc output references remain unsupported.

5. **FR-5**: Decision flow (lines 202-217) MUST add a FORMULA branch. The flow should check for sibling-only references before the EXPOSE check:
   ```
   +-- YES: Are ALL references sibling attributes (same part)?
       |
       +-- YES: FORMULA computed attribute -> OK
       |
       +-- NO: Is it just exposing a calc output?
           |
           +-- YES: EXPOSE pattern -> OK
           |
           +-- NO: Derived expression -> EXTRACT TO CALC DEF
   ```

6. **FR-6**: Common Mistakes section MUST update "Derived expressions in attributes" to note that sibling-only arithmetic is now valid (with a pointer to FORMULA). MUST add a new mistake: "Using CalcDef when a FORMULA attribute expression suffices."

7. **FR-7**: Both the updated Rule 3 and the expression taxonomy MUST reference the ADR-002 amendment, ADR-004, and ADR-005 as authority sources.

8. **FR-8**: [INFERRED] The "Last Updated" date at the bottom of the file MUST be updated.

#### 2b. `expose-pattern.md`

9. **FR-9**: MUST add a new section distinguishing FORMULA from EXPOSE with these three categories:
   - **FORMULA** (`attribute x = a * b`): Arithmetic on sibling attributes. Generates a pipeline module. NOT an EXPOSE pattern.
   - **EXPOSE_PURE** (`attribute x = calc.output`): Pure value forwarding from a calc output. No module generated. IS the EXPOSE pattern.
   - **EXPOSE_COMPUTED** (`attribute x = calc.output * 2.0`): Calc output + arithmetic. NOT yet supported. Workaround: create a CalcDef.

10. **FR-10**: [INFERRED] The section SHOULD include a brief table or comparison showing why the distinction matters (different pipeline treatment, different validation behavior).

11. **FR-11**: [INFERRED] The "Last Updated" date at the bottom of the file MUST be updated.

---

## Acceptance Criteria

### Core Functionality

- [ ] `adr002-calculations.md` Rule 3 includes FORMULA (FR-1)
- [ ] `adr002-calculations.md` expression taxonomy has FORMULA row with PASS result (FR-2)
- [ ] `adr002-calculations.md` "Invalid Pattern" section amended with FORMULA validity note, CalcDef preserved as alternative (FR-3)
- [ ] `adr002-calculations.md` "Supported Static Operators" section updated re: sibling refs (FR-4)
- [ ] `adr002-calculations.md` decision flow includes FORMULA branch (FR-5)
- [ ] `adr002-calculations.md` Common Mistakes updated + new mistake added (FR-6)
- [ ] Authority source references present (FR-7)
- [ ] `expose-pattern.md` has FORMULA vs EXPOSE distinction section (FR-9)

### Quality & Integration

- [ ] All examples are syntactically valid SysML v2
- [ ] No contradictions between the two pattern docs
- [ ] No contradictions with the implemented `_is_formula_pattern()` logic in `adr002.py`
- [ ] Existing tests continue to pass (`uv run pytest tests/`)

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_computed-attribute-integration.md` (EPIC-COMPATTR-001, Item 2)
- **Item 1 (complete):** V2 validation fix in `src/agentic_mbse/validation/adr002.py`
- **Authority sources:**
  - `~/1cfe/sysml-codegen/docs/architecture/ADR-002-calculation-architecture.md` (Amendment section)
  - `~/1cfe/sysml-codegen/docs/architecture/ADR-004-computed-attribute-pipeline-integration.md`
  - `~/1cfe/sysml-codegen/docs/architecture/ADR-005-computed-attribute-classification.md`
- **Design:** `.project/active/pattern-docs-formula-taxonomy/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
