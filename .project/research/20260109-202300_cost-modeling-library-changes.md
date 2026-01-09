---
date: 2026-01-09T20:23:00-08:00
researcher: Claude
topic: "Required Changes to agentic-mbse for Cost Modeling Support"
tags: [research, cost-modeling, agentic-mbse, validation, tooling-gap]
status: complete
last_updated: 2026-01-09
---

# Research: Required Changes to agentic-mbse for Cost Modeling Support

**Date**: 2026-01-09 20:23 PST
**Researcher**: Claude
**Research Type**: Architecture Gap Analysis (Usage Requirements → Library Capabilities)

## Research Question

Given the cost modeling requirements identified in fusion-tea's research reports, what changes are needed to the agentic-mbse library to support:
1. Cost modeling validation (Level 9)
2. Nested cost model patterns
3. Standard cost output schema enforcement
4. LCOE calculation validation
5. Documentation of cost modeling conventions

## Summary

- **Validation Enhancement Required**: Add Level 9 cost modeling validation with 3 rules: Costed Components have calc defs, calc inputs match part attributes, cost-bearing parts have usages
- **Template Updates Required**: MODELING_GUIDE.md needs new sections for cost modeling patterns, semantic calc defs, LCOE architecture
- **No Tooling Gap in agentic-mbse**: The tooling gap is in sysml-codegen (not agentic-mbse); agentic-mbse can validate patterns today but can't enforce nested calc instantiation
- **New ValidationCodes Required**: 4 new codes for cost-specific validation rules
- **SysideAdapter May Need Extensions**: For detecting part def specialization chains

---

## Detailed Findings

### 1. Mapping Usage Needs to Library Capabilities

#### From fusion-tea Research Reports:

| Requirement | Current agentic-mbse Support | Gap |
|-------------|------------------------------|-----|
| Costed Component interface enforcement | None | Add Level 9 Rule 1 |
| Cost calc def exists for each costed part | None | Add Level 9 Rule 2 |
| Cost-bearing parts have calc usages | None | Add Level 9 Rule 3 |
| Semantic calc defs (not generic math) | Manual review only | Document in MODELING_GUIDE |
| LCOE breakdown visibility | Multi-output is sysml-codegen | No change needed |
| Standard output schema | None | Document pattern in MODELING_GUIDE |
| Nested calc instantiation | Not in agentic-mbse scope | sysml-codegen enhancement |

#### Key Insight

agentic-mbse's role is **validation and documentation**, not code generation. The nested calc instantiation gap identified in the fusion-tea research is a **sysml-codegen** concern, not agentic-mbse. However, agentic-mbse can:
1. Validate that cost modeling patterns are followed
2. Document recommended patterns in templates
3. Warn when patterns are violated

---

### 2. Required Changes

#### Change Set 1: Level 9 Cost Modeling Validation

**Files to modify:**
- `src/agentic_mbse/validation/level9_cost.py` (NEW)
- `src/agentic_mbse/validation/runner.py`
- `src/agentic_mbse/sysml/types.py`
- `src/agentic_mbse/cli/__init__.py`

**New ValidationCodes** (add to `types.py:66-95`):
```python
# Level 9: Cost Modeling Validation
L9_COSTED_NO_CALC_DEF = "L9_COSTED_NO_CALC_DEF"
L9_CALC_INPUT_NOT_IN_PART = "L9_CALC_INPUT_NOT_IN_PART"
L9_MISSING_COST_USAGE = "L9_MISSING_COST_USAGE"
L9_GENERIC_MATH_CALC = "L9_GENERIC_MATH_CALC"
```

**Rule 1: Every Costed Component has a cost calc def**

```python
def check_costed_components_have_calcs(model: Any) -> list[ValidationIssue]:
    """Rule 1: Every PartDef specializing 'Costed Component'
    must have a corresponding CalculationDefinition.

    Naming convention: Part def 'Blanket System' → calc def 'BlanketSystemCostCalc'
    """
    issues = []
    costed_part_defs = _find_costed_part_defs(model)
    calc_def_names = {c.name for c in SysideAdapter.elements_of_type(model, "CalculationDefinition")}

    for part_def in costed_part_defs:
        expected_calc = _derive_cost_calc_name(part_def.name)
        if expected_calc not in calc_def_names:
            issues.append(ValidationIssue(
                level=9,
                severity=Severity.WARNING,  # WARNING not ERROR - pattern recommendation
                code=ValidationCode.L9_COSTED_NO_CALC_DEF,
                message=f"Costed component '{part_def.name}' has no corresponding cost calc def",
                element_name=part_def.qualified_name,
                suggestion=f"Create calc def '{expected_calc}' in models/library/calculations/costing/"
            ))
    return issues
```

**Rule 2: Cost calc inputs match part attributes**

```python
def check_cost_calc_inputs_match_part(model: Any) -> list[ValidationIssue]:
    """Rule 2: For cost calc defs, verify inputs correspond to
    attributes in the associated PartDef.

    Association determined by naming: 'BlanketSystemCostCalc' → 'Blanket System'
    """
    issues = []
    for calc_def in _find_cost_calc_defs(model):
        associated_part = _find_associated_part_def(model, calc_def)
        if not associated_part:
            continue

        calc_inputs = _extract_input_features(calc_def)
        part_attrs = {a.name for a in _extract_part_attributes(associated_part)}

        for input_feat in calc_inputs:
            if input_feat.name not in part_attrs and not _is_cost_factor(input_feat):
                issues.append(ValidationIssue(
                    level=9,
                    severity=Severity.INFO,
                    code=ValidationCode.L9_CALC_INPUT_NOT_IN_PART,
                    message=f"Cost calc input '{input_feat.name}' not found in part def attributes",
                    element_name=f"{calc_def.name}::{input_feat.name}",
                    suggestion=f"Add '{input_feat.name}' to '{associated_part.name}' or use default value"
                ))
    return issues
```

**Rule 3: Cost-bearing parts have cost calc usages**

```python
def check_cost_bearing_parts_have_usages(model: Any) -> list[ValidationIssue]:
    """Rule 3: Every PartUsage in designs/ that instantiates a
    'Costed Component' should have cost calculation wired.

    Checks for explicit calc usage OR inherited capital_cost binding.
    """
    issues = []
    for part_usage in SysideAdapter.elements_of_type(model, "PartUsage"):
        if not _is_in_designs_directory(part_usage):
            continue
        if not _instantiates_costed_component(part_usage, model):
            continue

        if not _has_cost_calc_or_binding(part_usage, model):
            issues.append(ValidationIssue(
                level=9,
                severity=Severity.WARNING,
                code=ValidationCode.L9_MISSING_COST_USAGE,
                message=f"Part '{part_usage.name}' is cost-bearing but has no cost calculation",
                element_name=get_qualified_name(part_usage),
                location=get_element_location(part_usage),
                suggestion="Wire cost calc or ensure capital_cost attribute is bound"
            ))
    return issues
```

**Rule 4 (Optional): Detect generic math calc defs**

```python
def check_semantic_cost_calcs(model: Any) -> list[ValidationIssue]:
    """Rule 4: Cost calc defs should encode domain knowledge,
    not be generic math wrappers.

    WARNING if calc def name matches pattern like 'MultiplyAndAdd', 'SumInputs'
    """
    issues = []
    generic_patterns = ['multiply', 'add', 'sum', 'divide', 'subtract']

    for calc_def in _find_cost_calc_defs(model):
        name_lower = calc_def.name.lower()
        if any(p in name_lower for p in generic_patterns):
            issues.append(ValidationIssue(
                level=9,
                severity=Severity.WARNING,
                code=ValidationCode.L9_GENERIC_MATH_CALC,
                message=f"Cost calc '{calc_def.name}' appears to be generic math",
                element_name=calc_def.qualified_name,
                suggestion="Use semantic cost calc defs (e.g., 'MagnetSystemCostCalc') not generic math"
            ))
    return issues
```

**Register in runner.py:**

```python
# Add import
from .level9_cost import validate_cost_modeling

# Add to QUALITY_CHECKS (line ~57)
QUALITY_CHECKS = [
    ("Level 1: Syntax Validation", validate_syntax),
    ("Level 2: Structural Completeness", validate_structure),
    ("Level 3: Dataflow Integrity", validate_dataflow),
    ("Level 4: Constraint Satisfaction", analyze_constraints),
    ("Level 5: Semantic Consistency", validate_semantic),
    ("Level 6: Traceability", validate_traceability),
    ("Level 7: Architecture", validate_architecture),
    ("Level 8: Codegen Readiness", validate_codegen_readiness),
    ("Level 9: Cost Modeling", validate_cost_modeling),  # NEW
]
```

**Update CLI argument parser:**

```python
# In cli/__init__.py, update choices
validate_parser.add_argument("--level", type=int, choices=range(1, 10))  # Was range(1, 9)
```

---

#### Change Set 2: MODELING_GUIDE.md Template Update

**File to modify:** `project_templates/MODELING_GUIDE.md.template`

**New sections to add:**

```markdown
## Cost Modeling Patterns

### Costed Component Interface

All cost-bearing parts MUST specialize the `'Costed Component'` abstract part def:

```sysml
abstract part def 'Costed Component' {
    doc /* Base interface for all cost-bearing components. */

    attribute capital_cost : Real;                    // Required
    attribute annual_operating_cost : Real default := 0.0;
    attribute replacement_cost : Real default := 0.0;
    attribute replacement_interval_years : Real default := 40.0;
}

part def 'Magnet System' :> 'Costed Component' {
    // Inherits cost interface, must define capital_cost
}
```

### Semantic Cost Calc Defs (NOT Generic Math)

**WRONG** - Generic math wrappers:
```sysml
// BAD: meaningless abstraction
calc def MultiplyAndAdd {
    in a : Real; in b : Real; in c : Real;
    out result : Real = a * b + c;
}
```

**RIGHT** - Semantic domain models:
```sysml
// GOOD: encodes domain knowledge
calc def MagnetSystemCostCalc {
    doc /* Cost model for magnet system per PyFECONS CAS220103 */

    in attribute field_strength : Real;
    in attribute coil_volume : Real;
    in attribute n_tf_coils : Integer;
    in attribute conductor_cost_per_m3 : Real default := 150.0e6;

    out attribute conductor_cost : Real;
    out attribute manufacturing_cost : Real;
    out attribute total_capital : Real;
    out attribute conductor_fraction : Real;
}
```

### Hierarchical Cost Rollup Pattern

```sysml
// Each part exposes capital_cost
part def 'Wheel' :> 'Costed Component' {
    attribute hub_mass : Real;
    attribute tire_diameter : Real;

    part hub : 'Hub' { :>> mass = hub_mass; }
    part tire : 'Tire' { :>> diameter = tire_diameter; }

    :>> capital_cost = hub.capital_cost + tire.capital_cost;
}

// Parent sums child costs
part def 'Bike' :> 'Costed Component' {
    part front_wheel : 'Wheel';
    part rear_wheel : 'Wheel';
    part frame : 'Frame';
    attribute assembly_cost : Real = 20.0;

    :>> capital_cost =
        front_wheel.capital_cost +
        rear_wheel.capital_cost +
        frame.capital_cost +
        assembly_cost;
}
```

### LCOE Calculation Pattern

Master LCOE calc def should expose ALL intermediate values for sensitivity analysis:

```sysml
calc def LCOECalculation {
    doc /* LCOE with full breakdown visibility */

    // CAPITAL INPUTS (by CAS category)
    in attribute cas22_reactor : Real;
    in attribute cas23_turbine : Real;
    // ... other CAS categories

    // FINANCIAL PARAMETERS
    in attribute capital_recovery_factor : Real default := 0.09;
    in attribute plant_lifetime : Real default := 40.0;

    // INTERMEDIATE OUTPUTS (for visibility)
    out attribute cas20_direct : Real = cas22_reactor + cas23_turbine + ...;
    out attribute total_capital : Real = ...;
    out attribute cas90_annualized : Real = ...;

    // FINAL LCOE
    out attribute lcoe : Real = total_annual / annual_energy_mwh;

    // BREAKDOWN METRICS (for comparison)
    out attribute capital_lcoe_fraction : Real = ...;
    out attribute overnight_cost_per_kw : Real = ...;
}
```

### Cost Modeling Validation

Run cost modeling validation:

```bash
# Check cost modeling patterns
agentic-mbse validate --level=9 models/

# Run all levels including cost modeling
agentic-mbse validate --complete models/
```

**Validation Rules:**
- Rule 1: Every `'Costed Component'` specialization has a corresponding cost calc def
- Rule 2: Cost calc inputs align with part def attributes
- Rule 3: Cost-bearing parts in designs have cost calculations wired
- Rule 4: Cost calc defs use semantic names, not generic math
```

---

#### Change Set 3: Helper Functions for SysideAdapter

**File to modify:** `src/agentic_mbse/sysml/syside_adapter.py`

**New functions needed:**

```python
@classmethod
def get_specialization_chain(cls, elem: Any) -> list[Any]:
    """Get the chain of specialized types for an element.

    Returns list from most specific to most general.
    """
    chain = []
    if not hasattr(elem, 'type'):
        return chain

    for type_ref in elem.type:
        chain.append(type_ref)
        # Recursively get parent specializations
        if hasattr(type_ref, 'owned_specializations'):
            for spec in type_ref.owned_specializations:
                if hasattr(spec, 'general'):
                    for general in spec.general:
                        chain.extend(cls.get_specialization_chain(general))
    return chain


@classmethod
def specializes(cls, elem: Any, target_name: str) -> bool:
    """Check if element specializes a type with the given name.

    Args:
        elem: Element to check (PartDef or PartUsage)
        target_name: Name of type to check for (e.g., 'Costed Component')

    Returns:
        True if elem specializes target_name directly or transitively
    """
    chain = cls.get_specialization_chain(elem)
    return any(getattr(t, 'name', '') == target_name for t in chain)
```

---

#### Change Set 4: Documentation Updates

**Files to update:**

1. **CLAUDE.md** - Add Level 9 to validation section
2. **project_templates/README.md.template** - Update validation level count
3. **project_templates/MODELING_PROCESS.md.template** - Add cost modeling phase guidance

**CLAUDE.md updates:**

```markdown
- **validation/**: 9-level quality validation pyramid for SysML models:
  ...
  - Level 9: Cost modeling conventions (interface compliance, calc pairing)
```

---

### 3. Implementation Dependencies

| Change | Dependencies | Priority |
|--------|--------------|----------|
| Level 9 validation module | None | HIGH |
| ValidationCode additions | None | HIGH |
| Runner registration | Level 9 module | HIGH |
| CLI argument update | None | MEDIUM |
| MODELING_GUIDE updates | None | HIGH |
| SysideAdapter extensions | None | MEDIUM |
| CLAUDE.md updates | Level 9 module | LOW |
| Other template updates | MODELING_GUIDE | LOW |

---

### 4. What Does NOT Need to Change

1. **sysml-codegen integration** - Not in agentic-mbse scope
2. **teax-simkit integration** - Not in agentic-mbse scope
3. **Multi-output handling** - Already works in codegen pipeline
4. **Existing validation levels** - No modifications needed
5. **Claude commands** - May benefit from new validation but no changes required

---

### 5. Testing Requirements

**New test file:** `tests/test_validation/test_level9_cost.py`

```python
"""Tests for Level 9 cost modeling validation."""

import pytest
from agentic_mbse.validation.level9_cost import (
    check_costed_components_have_calcs,
    check_cost_calc_inputs_match_part,
    check_cost_bearing_parts_have_usages,
    check_semantic_cost_calcs,
)

class TestCostedComponentRule:
    def test_costed_component_with_calc_passes(self):
        """Part def specializing 'Costed Component' with matching calc def passes."""
        ...

    def test_costed_component_without_calc_warns(self):
        """Part def without matching cost calc def generates warning."""
        ...

class TestCalcInputMatchRule:
    def test_inputs_matching_attributes_passes(self):
        """Calc inputs that match part attributes pass."""
        ...

class TestCostUsageRule:
    def test_part_usage_with_cost_calc_passes(self):
        """Part usage with wired cost calc passes."""
        ...

class TestSemanticCalcRule:
    def test_semantic_calc_name_passes(self):
        """Calc def with semantic name passes."""
        ...

    def test_generic_math_name_warns(self):
        """Calc def named 'MultiplyAndAdd' generates warning."""
        ...
```

**Test fixtures needed:**
- `tests/fixtures/cost_modeling/costed_with_calc.sysml`
- `tests/fixtures/cost_modeling/costed_without_calc.sysml`
- `tests/fixtures/cost_modeling/generic_math_calc.sysml`
- `tests/fixtures/cost_modeling/semantic_cost_calc.sysml`

---

## Implementation Roadmap

### Phase 1: Core Validation (Immediate Priority)

1. Add ValidationCodes to `types.py`
2. Create `level9_cost.py` with 4 rules
3. Register in `runner.py`
4. Update CLI argument parser
5. Add tests

### Phase 2: Documentation (After Phase 1)

6. Update MODELING_GUIDE.md template
7. Update CLAUDE.md
8. Update README.md template

### Phase 3: Helper Functions (As Needed)

9. Add SysideAdapter extensions if needed for specialization chain detection

---

## Feasibility Assessment

**Overall: HIGH FEASIBILITY**

- All changes are additive (no breaking changes)
- Existing validation infrastructure provides clear patterns
- Level 9 follows same pattern as Levels 2-8
- Template updates are documentation only
- No external dependencies required

**Risks:**
- Specialization chain detection may be complex with syside
- Cost calc naming convention requires standardization
- Users may find validation too strict initially (use WARNING not ERROR)

---

## Recommendations

1. **Start with Level 9 validation** - Most impactful change for cost modeling support
2. **Use WARNING severity initially** - Let patterns stabilize before enforcing as ERROR
3. **Document patterns in MODELING_GUIDE first** - Users need guidance before enforcement
4. **Consider opt-in flag** - `--level=9` explicitly or `--include-cost` flag
5. **Test with fusion-tea models** - Real-world validation of rules

---

## Open Questions

1. **Naming convention strictness**: Should `'Blanket System'` require exactly `BlanketSystemCostCalc` or allow variants like `BlanketCostCalc`?

2. **Default values for cost factors**: Should cost factor inputs (like `conductor_cost_per_m3`) be exempt from the "input matches attribute" rule?

3. **Nested calc instantiation**: Should agentic-mbse warn when patterns suggest the sysml-codegen enhancement is needed?

4. **Cost output schema validation**: Should there be a rule checking for required LCOE outputs?

---

## Code References

**agentic-mbse validation:**
- `src/agentic_mbse/validation/runner.py:48-57` - QUALITY_CHECKS registry
- `src/agentic_mbse/validation/level2_structure.py:118-219` - Rule implementation pattern
- `src/agentic_mbse/sysml/types.py:66-95` - ValidationCode enum
- `src/agentic_mbse/sysml/syside_adapter.py:110-303` - Element iteration

**fusion-tea research:**
- `project/research/20260107-final-cost-architecture.md` - Complete cost architecture
- `project/research/20260106-065431_cost-architecture-patterns.md` - Validation rule specs

---

**Last Updated**: 2026-01-09
