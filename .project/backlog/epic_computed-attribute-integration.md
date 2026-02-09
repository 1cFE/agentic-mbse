# Epic: Computed Attribute Integration — ADR-002 Amendment for FORMULA Patterns

**Epic ID**: EPIC-COMPATTR-001
**Status**: in-progress
**Priority**: P1
**Created**: 2026-02-09
**Estimated Effort**: ~2-3 days

---

## Executive Summary

Integrate the sysml-codegen ATTR-EXPR (Phase 2) changes into the agentic-mbse validation layer, pattern documentation, agent commands, and project templates. The codegen pipeline now generates synthetic pipeline modules for FORMULA computed attributes (`attribute area = length * width`), but the agentic-mbse V2 validator still rejects these as "derived expression" violations. Without this integration, the validation pyramid actively contradicts the ADR-002 amendment — modelers who follow the new guidance will get false errors.

**Critical Success Factor**: `agentic-mbse validate` passes on models containing FORMULA computed attributes (sibling-only arithmetic) with zero false V2 violations, and pattern documentation guides modelers to use FORMULA vs CalcDef correctly.

---

## Why This Epic?

**Current State**:
- sysml-codegen ATTR-EXPR epic is complete (Items 1-4 done, 285 tests passing). Codegen generates synthetic modules for `attribute area = length * width` patterns.
- ADR-002 has been amended to permit FORMULA expressions (sibling-only arithmetic) in design attributes.
- ADR-004 and ADR-005 formalize the pipeline integration and classification scheme.
- **However**, the agentic-mbse validation layer (`adr002.py:check_static_expressions()`) still flags ALL design attributes with feature references (except EXPOSE) as V2_DYNAMIC_EXPRESSION violations. FORMULA patterns like `area = length * width` are rejected.
- Pattern doc `adr002-calculations.md` shows `attribute area = length * width` as an **invalid pattern** requiring extraction to a CalcDef.
- Agent commands (`/implement-model`, `/design-model`) don't mention FORMULA as a valid modeling option.
- `MODELING_GUIDE.md.template` decision tree routes ALL formulas to CalcDefs.

**Future State**:
- V2 check exempts FORMULA patterns (sibling-only attribute references) alongside the existing EXPOSE exemption.
- Pattern docs reflect the updated expression taxonomy with FORMULA as a valid category.
- Agent commands guide modelers on when to use attribute expressions vs CalcDefs.
- New projects get updated guidance via `MODELING_GUIDE.md.template`.
- The validation pyramid and codegen pipeline tell the same story.

---

## Authority Source Dependencies

These documents from sysml-codegen are the authoritative source for what FORMULA patterns are, how they're classified, and what the pipeline does with them. All items in this epic trace to these documents.

| Source | Use For | Items Depending On | Status |
|--------|---------|-------------------|--------|
| `sysml-codegen/docs/architecture/ADR-002-calculation-architecture.md` (Amendment section) | Rule 3 relaxation conditions, updated expression taxonomy, EXPOSE_COMPUTED UX gap | All items | Complete (amended 2026-02-09) |
| `sysml-codegen/docs/architecture/ADR-004-computed-attribute-pipeline-integration.md` | Option C architecture, Step 4.5, module naming, backtracker awareness | Item 1 (classification logic), Item 2 (pattern doc) | Accepted (2026-02-09) |
| `sysml-codegen/docs/architecture/ADR-005-computed-attribute-classification.md` | 5-way classification scheme, qualified name resolution, EXPOSE handling | Item 1 (classification logic), Item 2 (pattern doc), Item 3 (EXPOSE distinction) | Accepted (2026-02-09) |
| `sysml-codegen/.project/backlog/epic_attribute_expression_capture.md` | Complete ATTR-EXPR epic with spike findings, implementation results, lessons learned | All items (context) | Complete |
| `sysml-codegen/.project/research/20260209-165638_attr-expr-documentation-adrs-and-upstream-integration.md` | Full integration point inventory, code references, proposed logic for `_is_formula_pattern()` | Item 1 (implementation reference) | Complete |

---

## Success Criteria

- [x] `check_static_expressions()` in `adr002.py` exempts FORMULA patterns (all refs resolve to sibling attributes, no FeatureChainExpression)
- [x] FORMULA exemption uses structural checks consistent with sysml-codegen's `ComputedAttributeClassification.FORMULA` definition (ADR-005)
- [x] All existing V2 tests pass with zero regressions
- [x] New tests cover: simple FORMULA pass, chain FORMULA pass, EXPOSE_COMPUTED still fails, mixed (sibling + calc output) still fails
- [ ] `adr002-calculations.md` expression taxonomy includes FORMULA row, decision flow includes FORMULA branch
- [ ] `expose-pattern.md` distinguishes FORMULA from EXPOSE
- [ ] `/implement-model` and `/design-model` commands include FORMULA guidance
- [ ] `MODELING_GUIDE.md.template` decision tree includes FORMULA branch
- [x] All existing tests pass (`uv run pytest tests/`)

---

## Items

### Item 1: V2 Validation — FORMULA Exemption in `adr002.py`

**Scale**: standard
**Dependencies**: None (sysml-codegen changes are already complete)

**Scope**:

Add a `_is_formula_pattern()` check to `check_static_expressions()` in `adr002.py` (line 487, between the EXPOSE check and the violation). This mirrors the classification logic proven in sysml-codegen's `computed_attribute_extractor.py` but uses the agentic-mbse expression utilities (`extract_feature_refs()`, AST inspection).

The FORMULA exemption fires when ALL of the following hold:
- The expression has >=1 feature reference (after standard library filtering)
- The expression is NOT a `FeatureChainExpression` (distinguishes from EXPOSE)
- All feature references resolve to sibling attributes on the same owning part (same `owner`)
- No feature reference points to a calc output (no `FeatureChainExpression` refs within operator expression)

This is the inverse of the existing EXPOSE check: EXPOSE is a pure `FeatureChainExpression` (dotted path, no operators), FORMULA is an `OperatorExpression` with sibling-only refs (operators, no dotted paths).

**Current State**:
- `_is_expose_pattern()` (lines 297-391) provides the structural model for `_is_formula_pattern()`
- `extract_feature_refs()` already returns refs with `.name` and `.qualified_name` properties
- `check_static_expressions()` (lines 418-510) has the exact insertion point
- The existing logic: no refs → OK, EXPOSE → OK, everything else → VIOLATION
- Needed logic: no refs → OK, EXPOSE → OK, **FORMULA → OK**, everything else → VIOLATION

**Key Implementation Details**:

1. **`_is_formula_pattern(attr, expr, calc_outputs)` function**:
   - Check that the expression is an `OperatorExpression` (has arithmetic operators), NOT a `FeatureChainExpression`
   - For each ref returned by `extract_feature_refs(expr)`:
     - Verify the ref's referent has the same owner as the attribute (sibling check)
     - Verify the ref is NOT a calc output reference (not in `calc_outputs` set, and not accessed via a FeatureChain)
   - If all refs are siblings and none are calc outputs → FORMULA → return True
   - Conservative: any uncertainty → return False (don't exempt)

2. **Integration point** in `check_static_expressions()`:
   ```python
   # After line 486 (EXPOSE check):
   if _is_formula_pattern(attr, expr, calc_outputs):
       continue  # OK - FORMULA computed attribute (per ADR-002 Amendment)
   ```

3. **Edge cases to handle**:
   - EXPOSE_COMPUTED (`calc.output * 2.0`): must NOT be exempted. The expression contains a FeatureChainExpression inside an OperatorExpression. The ref to `calc.output` will fail the sibling check (different owner) or be detected as a calc output.
   - Mixed references (`sibling_a + calc.output`): must NOT be exempted. Same reasoning — the calc output ref fails the sibling check.
   - Chain FORMULA (`cost = area * rate` where `area` is computed): MUST be exempted. All refs are siblings regardless of whether they are literal or computed.

**Success Criteria**:
- [x] `_is_formula_pattern()` implemented with sibling-ref + no-calc-output checks
- [x] `check_static_expressions()` calls `_is_formula_pattern()` after EXPOSE check
- [x] Test: `attribute area = length * width` (FORMULA) → no V2 violation
- [x] Test: `attribute cost = area * rate` (chain FORMULA) → no V2 violation
- [x] Test: `attribute p_net_kw = p_net_mw * 1000.0` (FORMULA with literal) → no V2 violation
- [x] Test: `attribute adj = calc.output * 0.95` (EXPOSE_COMPUTED) → still V2 violation
- [x] Test: `attribute x = sibling_a + calc.output` (mixed) → still V2 violation
- [x] Test: existing EXPOSE patterns → still pass (no regression)
- [x] Test: existing true static patterns → still pass (no regression)
- [x] `uv run pytest tests/` — all existing tests pass, zero regressions (886 passed)
- [x] `uv run mypy src/` — type check passes (pre-existing errors in runner.py only)

**Deliverables**:
- Modified: `src/agentic_mbse/validation/adr002.py` (`_is_formula_pattern()` + integration)
- Modified or new: `tests/test_sysml_quality_checks.py` or `tests/test_adr002_formula.py` (FORMULA exemption tests)

---

### Item 2: Pattern Documentation — Expression Taxonomy and Decision Flow

**Scale**: standard
**Dependencies**: Item 1 (V2 fix defines what FORMULA is; docs must match)

**Scope**:

Update two pattern docs in `docs/patterns/` that ship with the `agentic_mbse_data` package:

**2a. `adr002-calculations.md`** (highest priority):

1. **Expression taxonomy table** (line 42): Add FORMULA row between "True static" and "Derived expression":
   ```
   | **FORMULA expression** | `designs/` attribute | >=1 (sibling attrs only) | **PASS** | `= length * width` |
   ```
   Split the existing "Derived expression" row to clarify it means calc-output refs:
   ```
   | **Derived expression** | `designs/` attribute | >=1 (calc output refs) | **FAIL** | `= calc.output * 0.95` |
   ```

2. **Invalid Pattern section** (lines 65-101): Add an "Amendment" callout that `attribute area = length * width` is NOW valid when all refs are sibling attributes. Keep the CalcDef resolution as an alternative, not the only option.

3. **Decision flow** (lines 202-217): Add FORMULA branch:
   ```
   +-- YES: Are ALL references sibling attributes (same part)?
       |
       +-- YES: FORMULA computed attribute -> OK (generates pipeline module)
       |
       +-- NO: Is it just exposing a calc output?
           |
           +-- YES: EXPOSE pattern -> OK
           |
           +-- NO: Derived expression -> EXTRACT TO CALC DEF
   ```

4. **Common Mistakes section** (lines 171-182): Update "Derived expressions in attributes" to note that sibling-only arithmetic is now valid. Add a new mistake: "Using CalcDef when a FORMULA attribute expression suffices."

5. **Rule 3 description** (line 29): Update to reflect amendment:
   ```
   | **Rule 3** | Design attributes contain literals, bindings, static expressions, or **FORMULA expressions** (sibling-only arithmetic) |
   ```

**2b. `expose-pattern.md`**:

Add a section distinguishing FORMULA from EXPOSE:
- **FORMULA** (`attribute x = a * b`): Arithmetic on sibling attributes. Generates a pipeline module. NOT an EXPOSE pattern.
- **EXPOSE_PURE** (`attribute x = calc.output`): Pure value forwarding from a calc output. No module generated. This IS the EXPOSE pattern.
- **EXPOSE_COMPUTED** (`attribute x = calc.output * 2.0`): Calc output + arithmetic. NOT yet supported. Workaround: create a CalcDef.

This prevents modelers from conflating FORMULA with EXPOSE.

**Success Criteria**:
- [ ] `adr002-calculations.md` expression taxonomy has FORMULA row with "PASS" result
- [ ] `adr002-calculations.md` decision flow includes FORMULA branch
- [ ] `adr002-calculations.md` "Invalid Pattern" section amended with FORMULA validity note
- [ ] `adr002-calculations.md` Common Mistakes section updated
- [ ] `expose-pattern.md` has FORMULA vs EXPOSE distinction section
- [ ] Both docs reference ADR-002 amendment, ADR-004, and ADR-005 for authoritative details
- [ ] Examples verified with syside parser where applicable

**Deliverables**:
- Modified: `docs/patterns/adr002-calculations.md`
- Modified: `docs/patterns/expose-pattern.md`

---

### Item 3: Agent Command Updates — FORMULA Guidance

**Scale**: standard
**Dependencies**: Item 2 (pattern docs should be updated first so commands can reference them)

**Scope**:

Update modeling agent commands to guide modelers on when to use FORMULA attribute expressions vs CalcDefs.

**3a. `claude/commands/implement-model.md`** (highest priority):

Add guidance in the implementation stage referencing the ADR-002 amendment:
- When implementing a formula: if the expression references only sibling attributes on the same part, it CAN be written as `attribute x = a * b` (FORMULA pattern). The codegen pipeline auto-generates a module for it.
- When to use CalcDef instead: reusable logic, complex expressions, references to calc outputs.
- Reference the updated `adr002-calculations.md` pattern doc.

**3b. `claude/commands/design-model.md`** (medium priority):

Add guidance in the design analysis stage:
- When analyzing component interfaces, recognize FORMULA as a valid option for simple formulas.
- Decision criteria: one-off simple formula on sibling attributes → attribute expression; reusable/complex/calc-output-dependent → CalcDef.

**Success Criteria**:
- [ ] `implement-model.md` includes FORMULA guidance with examples
- [ ] `design-model.md` includes FORMULA recognition criteria
- [ ] Both commands reference `adr002-calculations.md` pattern doc
- [ ] Guidance is consistent with ADR-002 amendment conditions

**Deliverables**:
- Modified: `claude/commands/implement-model.md`
- Modified: `claude/commands/design-model.md`

---

### Item 4: Project Template Updates — MODELING_GUIDE Decision Tree

**Scale**: standard
**Dependencies**: Item 2 (pattern docs should be updated first)

**Scope**:

Update `MODELING_GUIDE.md.template` to include FORMULA as a modeling option. This template is installed by `agentic-mbse init` into new modeling projects.

1. **Decision tree** (around line 72-78 in the template): Currently says "A CALCULATION formula? → Calc def in library/ (per ADR-002)". Add a FORMULA branch:
   ```
   A SIMPLE FORMULA on sibling attributes?
   → Attribute expression on the part (per ADR-002 amendment)
   → OR Calc def in library/ (for reusable/complex formulas)
   ```

2. **Add "Computed Attributes" section**: Brief section explaining:
   - FORMULA: `attribute area = length * width` — works when all refs are siblings
   - EXPOSE: `attribute x = calc.output` — pure forwarding, works
   - EXPOSE_COMPUTED: `attribute x = calc.output * 2.0` — NOT yet supported, use CalcDef
   - When to use CalcDef vs attribute expression

**Success Criteria**:
- [ ] `MODELING_GUIDE.md.template` decision tree includes FORMULA branch
- [ ] Computed Attributes section added with FORMULA/EXPOSE/EXPOSE_COMPUTED distinction
- [ ] Examples show both FORMULA and CalcDef alternatives
- [ ] Template references pattern docs for detail

**Deliverables**:
- Modified: `project_templates/MODELING_GUIDE.md.template`

---

## Sequencing

```
Item 1: V2 Validation Fix (no dependencies — code change)
  └─> Item 2: Pattern Documentation (needs FORMULA definition from Item 1)
        ├─> Item 3: Agent Commands (references pattern docs from Item 2)
        └─> Item 4: Project Templates (references pattern docs from Item 2)
```

Items 3 and 4 can run in parallel after Item 2.

**Critical path**: Item 1 → Item 2 → (Item 3 || Item 4)

**Minimum execution rounds**: 3 (Item 1, then Item 2, then Items 3+4 in parallel)

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| `_is_formula_pattern()` sibling check doesn't cover all AST structures | Medium | High — false V2 violations on valid FORMULA patterns | Model the implementation on `_is_expose_pattern()` which already handles AST traversal robustly. Test against sysml-codegen's probe fixture patterns. Conservative default (don't exempt if uncertain). |
| Pattern docs become inconsistent with validation behavior | Low | Medium — confusing modeler experience | Item 2 depends on Item 1 completion. Single-source the FORMULA definition from ADR-005. |
| Existing V2 tests break from FORMULA exemption | Low | Medium — regression in validation coverage | The exemption is additive (new `continue` path). Existing tests for EXPOSE, true static, and derived expressions should be unaffected. Run full suite. |
| EXPOSE_COMPUTED patterns incorrectly exempted as FORMULA | Medium | High — validation misses real violations | EXPOSE_COMPUTED contains FeatureChainExpression refs inside OperatorExpression. The sibling-owner check will reject these (calc output has different owner). Explicit test case required. |
| `agentic_mbse_data` installed package becomes stale | Low | Low — affects only users who don't re-install | Updating source docs in `docs/patterns/` is sufficient. Package rebuild happens on next release. |
| Modelers adopt FORMULA for patterns that should be CalcDefs | Low | Low — suboptimal but functional | Guidance in all docs emphasizes: reusable/complex → CalcDef; one-off/simple → FORMULA. |

---

## Source Document Traceability

All work in this epic traces to these upstream documents:

| Document | Location | Relevance |
|----------|----------|-----------|
| ATTR-EXPR Epic | `~/1cfe/sysml-codegen/.project/backlog/epic_attribute_expression_capture.md` | Complete Phase 2 epic with spike findings, implementation results, 285 passing tests |
| Integration Research | `~/1cfe/sysml-codegen/.project/research/20260209-165638_attr-expr-documentation-adrs-and-upstream-integration.md` | Full integration point inventory for agentic-mbse: code refs, proposed `_is_formula_pattern()` logic, pattern doc line numbers |
| ADR-002 (Amended) | `~/1cfe/sysml-codegen/docs/architecture/ADR-002-calculation-architecture.md` | Rule 3 amendment, updated expression taxonomy, FORMULA conditions, EXPOSE_COMPUTED UX gap, modeling guidance |
| ADR-004 | `~/1cfe/sysml-codegen/docs/architecture/ADR-004-computed-attribute-pipeline-integration.md` | Option C architecture, Step 4.5 placement, module naming, backtracker awareness |
| ADR-005 | `~/1cfe/sysml-codegen/docs/architecture/ADR-005-computed-attribute-classification.md` | 5-way classification (FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE), qualified name resolution, EXPOSE handling |

---

**Last Updated**: 2026-02-09
**Next Action**: Item 1 complete. Begin Item 2 — update pattern documentation (`adr002-calculations.md`, `expose-pattern.md`)
