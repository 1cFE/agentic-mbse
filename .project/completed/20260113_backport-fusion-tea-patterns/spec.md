# Spec: Backport fusion-tea Modeling Patterns

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-01-13 05:43
**Complexity:** LOW
**Branch:** 1cfe_dev
**Backlog Item:** ITEM-BACKPORT-001

---

## Business Goals

### Why This Matters
Changes made during real modeling work in downstream projects (like fusion-tea) contain hard-won learnings. These validated patterns for cost modeling, multiplicity aggregation, and part redefinition were discovered through actual use but haven't been incorporated into the agentic-mbse source templates. Without backporting, these insights are lost and future users will repeat the same struggles.

### Success Criteria

- [x] All validated patterns from fusion-tea are in MODELING_GUIDE.md.template
- [x] Patterns use correct SysMLv2 syntax (not domain-specific modifications)
- [x] New MBSE projects created via `agentic-mbse init` receive these patterns

### Priority
P1 (High) - Listed in backlog. Blocking ITEM-GUIDE-001 (which needs full scope of content).

---

## Problem Statement

### Current State
The `~/1cfe/fusion-tea` project was initialized from agentic-mbse on Jan 5, 2026. During modeling work, the `project/MODELING_GUIDE.md` (a TOOL_OWNED file) was directly modified to add validated patterns discovered through trial and error. These patterns exist only in fusion-tea.

### Desired Outcome
Incorporate the validated patterns from fusion-tea into `project_templates/MODELING_GUIDE.md.template` so all future MBSE projects benefit from these learnings.

---

## Scope

### In Scope

**Backport FROM fusion-tea TO agentic-mbse:**

| File | Change | Lines |
|------|--------|-------|
| `MODELING_GUIDE.md.template` | Add "Cost Model Imports" section | +19 lines |
| `MODELING_GUIDE.md.template` | Add "Multiplicity Cost Aggregation Pattern" | +26 lines |
| `MODELING_GUIDE.md.template` | Add "Part Redefinition Pattern" | +30 lines |
| `MODELING_GUIDE.md.template` | Add "Parameterized Multiplicity Pattern" | +15 lines |

### Out of Scope

**NOT backporting (fusion-tea has INCORRECT syntax):**
- "Syntax 10: Conditional Logic" changes - fusion-tea uses C-style ternary (`? :`) which is WRONG
- agentic-mbse already has CORRECT SysMLv2 syntax (`if CONDITION?`)

**Forward sync (agentic-mbse → fusion-tea) - separate task:**
- Commands: design-model.md, implement-model.md, onboard.md, manage-sources.md
- Agents: kerml-expert.md, sysml-expert.md, syside-expert.md, sysmlv2-validator.md
- These are newer in agentic-mbse; fusion-tea should be re-initialized or manually updated

**Deferred to ITEM-GUIDE-001:**
- Creating `docs/patterns/costing.md` pattern doc
- Progressive disclosure restructuring of MODELING_GUIDE

### Edge Cases & Considerations

- Research reference in fusion-tea (`project/research/20260112-055807_*.md`) won't exist in template
- Pattern validation dates will be historical (2026-01-12)
- Pattern format should match existing docs conventions, not fusion-tea's ad-hoc format

---

## Requirements

### Functional Requirements

> Requirements below are from user's request and backlog item

1. **FR-1**: Add Cost Model Imports section documenting `NumericalFunctions::sum` import requirement
2. **FR-2**: Add Multiplicity Cost Aggregation Pattern to Validated Patterns section
3. **FR-3**: Add Part Redefinition Pattern (dot notation vs redefines) to Validated Patterns section
4. **FR-4**: Add Parameterized Multiplicity Pattern to Validated Patterns section
5. **FR-5**: [INFERRED] Patterns MUST use correct SysMLv2 syntax per existing documentation standards
6. **FR-6**: [INFERRED] Do NOT include domain-specific research references (e.g., fusion-tea research paths)

### Non-Functional Requirements

- Patterns SHOULD be concise and follow existing MODELING_GUIDE formatting
- Code examples MUST be syntactically valid SysMLv2

---

## Acceptance Criteria

### Core Functionality
- [x] "Cost Model Imports" section exists in MODELING_GUIDE.md.template
- [x] Section documents `NumericalFunctions::sum` import with example
- [x] Multiplicity Cost Aggregation Pattern documented with correct/anti-pattern examples
- [x] Part Redefinition Pattern documented with dot notation and redefines examples
- [x] Parameterized Multiplicity Pattern documented with example

### Quality & Integration
- [x] Existing tests continue to pass
- [x] `uv run agentic-mbse init /tmp/test-project` produces MODELING_GUIDE.md with new patterns
- [x] No domain-specific (fusion-tea) references in template

---

## Delta Analysis Summary

### Complete TOOL_OWNED File Comparison

**Commands (9 files):**
| File | Status | Direction |
|------|--------|-----------|
| design-model.md | DIFFERS (+115 lines in mbse) | mbse → fusion-tea |
| plan-model.md | SAME | - |
| implement-model.md | DIFFERS (+10 lines in mbse) | mbse → fusion-tea |
| spec-model.md | SAME | - |
| research.md | SAME | - |
| audit-models.md | SAME | - |
| onboard.md | DIFFERS (+24 lines in mbse) | mbse → fusion-tea |
| manage-sources.md | DIFFERS (+33 lines in mbse) | mbse → fusion-tea |
| backlog.md | SAME | - |

**Agents (5 files):**
| File | Status | Direction |
|------|--------|-----------|
| python-debugger.md | SAME | - |
| kerml-expert.md | MISSING in fusion-tea | mbse → fusion-tea |
| sysml-expert.md | MISSING in fusion-tea | mbse → fusion-tea |
| syside-expert.md | MISSING in fusion-tea | mbse → fusion-tea |
| sysmlv2-validator.md | MISSING in fusion-tea | mbse → fusion-tea |

**Templates (2 files):**
| File | Status | Direction |
|------|--------|-----------|
| MODELING_GUIDE.md | DIFFERS (+78 lines in fusion-tea) | **fusion-tea → mbse** |
| MODELING_PROCESS.md | SAME | - |

**Skills & Hooks:**
| File | Status |
|------|--------|
| python-debugger/ | SAME |
| ruff-format.sh | SAME |

### Key Finding

Only ONE file needs backporting: `MODELING_GUIDE.md` (fusion-tea → agentic-mbse template).

All other differences are forward changes (agentic-mbse is newer), which would be resolved by re-running `agentic-mbse init` on fusion-tea or handled separately.

---

## Related Artifacts

- **Research:** `.project/research/20260109-202300_cost-modeling-library-changes.md`
- **Design:** `.project/active/backport-fusion-tea-patterns/design.md` (to be created)
- **Epic:** `.project/backlog/BACKLOG.md` (ITEM-BACKPORT-001)

---

**Next Steps:** After approval, proceed to `/_my_design`
