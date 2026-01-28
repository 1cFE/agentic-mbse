---
date: 2026-01-26T20:29:31-08:00
researcher: Claude
topic: "Requirements and Goal Tracking Through the MBSE-Codegen-TEAx Pipeline"
tags: [research, workflow, requirements, traceability, fusion-tea, architecture]
status: complete
last_updated: 2026-01-26
---

# Research: Requirements and Goal Tracking Through the MBSE-Codegen-TEAx Pipeline

**Date**: 2026-01-26 20:29 PST
**Researcher**: Claude
**Research Type**: Integration / Workflow Architecture

## Research Question

1. What is the right way for users to define and capture goals/requirements for modeling projects?
2. How do we reliably translate high-level goals to model requirements that don't get "dropped"?
3. How do we support "analysis angles" - domain insights that shape what the models need to capture?
4. How should agentic-mbse workflow commands be enhanced to preserve and propagate these requirements?

## Context: The LCOE Visibility Problem

From `/home/reid/1cfe/fusion-tea/modeling_pm/research/20260126-lcoe-visibility-requirements-analysis.md`:

> The strategy shows LCOE as the "final output" but doesn't specify the intermediate calculations (CAS70, CAS80, CAS90) needed to get there... Requirements were loosely defined - Original goals were "replicate PyFECONS" without specifying acceptance criteria for validation.

This exemplifies how goals get "dropped" when moving from high-level intent to concrete model requirements.

---

## Summary

- **Requirements are currently captured in prose** (OVERVIEW.md success criteria, backlog items, spec docs) but have **no structured link** to model elements
- **The pipeline loses semantic context** - values flow correctly but the "why" is lost at each stage (agentic-mbse → sysml-codegen → teax)
- **"Analysis Angles" are a powerful concept** - domain insights that shape model requirements but aren't captured anywhere
- **Solution: A structured requirements layer** that flows through all stages, with explicit support in agentic-mbse workflow commands

---

## Detailed Findings

### 1. Current Requirements Capture Locations

| Location | What's Captured | Problems |
|----------|-----------------|----------|
| `modeling_pm/OVERVIEW.md` | High-level project goals, success criteria | Generic checklists, not traceable to specific model elements |
| `modeling_pm/backlog/BACKLOG.md` | Work items, epics, validation targets | Good detail but no formal requirement IDs or traceability |
| `modeling_pm/active/{feature}/spec.md` | MR-XXX requirements per feature | Best structure but not aggregated or tracked across features |
| `modeling_pm/research/*.md` | Domain findings, PyFECONS mappings | Rich context but disconnected from requirements |
| SysML `doc /* */` comments | Source citations | One-way traceability, not linked to requirements |

**Key Gap**: No centralized, queryable requirements structure that persists through the workflow.

### 2. The "Dropping" Problem Illustrated

**Example: LCOE Calculation Requirements**

```
STAGE 1: Team Discussion
"We need LCOE with CapEx/OpEx breakdown for cost driver analysis"
                    ↓
STAGE 2: OVERVIEW.md
"Bottom-Up Analysis - LCOE estimation from components" ← VAGUE
                    ↓
STAGE 3: spec.md (if created)
"MR-007: The model SHALL compute LCOE" ← INCOMPLETE (no breakdown requirement)
                    ↓
STAGE 4: model implementation
calc def LCOECalc { ... } ← Missing LCOE_capital, LCOE_om, LCOE_fuel outputs
                    ↓
STAGE 5: simulation results
{ "lcoe": 45.1 } ← Can't answer "what's the capital vs O&M breakdown?"
```

**Where it got lost**: The specific requirement for breakdown visibility was never formalized. The MR-XXX requirement in spec.md was too high-level.

### 3. Analysis Angles: A New Concept

From the user prompt:
> "A key question will become the method of energy capture. A steam turbine alone accounts for 0.5 cents/kWh"
> "We should make sure we call this out in our models, and then in the analysis highlight this in the side-by-side comparisons"

This represents an **Analysis Angle** - a domain-informed perspective that:
1. **Originates from domain expertise** (team discussion, research)
2. **Implies model requirements** (must have steam turbine cost breakdown)
3. **Implies analysis requirements** (must compare energy capture methods)
4. **Isn't a traditional requirement** (it's a lens for interpreting results)

**Current Problem**: Analysis Angles exist only in meeting notes or researchers' heads. No workflow support for capturing and translating them.

### 4. The Three-Stage Pipeline Analysis

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     REQUIREMENTS FLOW ANALYSIS                          │
└─────────────────────────────────────────────────────────────────────────┘

STAGE 1: AGENTIC-MBSE                 STAGE 2: SYSML-CODEGEN
├─ Goals (OVERVIEW.md)                ├─ Extracts calc defs
├─ Epics (backlog/)                   ├─ Extracts attributes
├─ Specs (active/{}/spec.md)          ├─ Builds computation graph
├─ Research (research/*.md)           ├─ Generates schemas
│                                     │
│ ❌ No structured requirement IDs    │ ❌ No requirement propagation
│ ❌ No validation criteria links     │ ❌ No doc comment preservation
│ ❌ No analysis angle capture        │ ❌ No requirement tags in output
│                                     │
└─────────────────────────────────────┴─────────────────────────────────

STAGE 3: TEAX                         STAGE 4: RESULTS ANALYSIS
├─ Executes pipeline                  ├─ Produces outputs
├─ Routes data through modules        ├─ User interprets results
├─ Tracks provenance (module versions)│
│                                     │ ❌ No requirement verification
│ ❌ No requirement IDs in schemas    │ ❌ No "which goal does this answer?"
│ ❌ No traceability to model source  │ ❌ No automatic pass/fail
│                                     │
└─────────────────────────────────────┴─────────────────────────────────
```

### 5. What Should Flow Through the Pipeline

**Requirements Layer** (new):
```
┌──────────────────────────────────────────────────────────────────────┐
│ GOAL (G-001)                                                         │
│ "Compare LCOE across energy capture methods"                         │
│ Source: Team discussion 2026-01-26                                   │
├──────────────────────────────────────────────────────────────────────┤
│ ANALYSIS ANGLES                                                      │
│ - AA-001: Steam turbine cost impact                                  │
│ - AA-002: Direct conversion efficiency trade-off                     │
├──────────────────────────────────────────────────────────────────────┤
│ DERIVED MODEL REQUIREMENTS                                           │
│ - MR-001: Model SHALL include TurbinePlant.capital_cost             │
│ - MR-002: Model SHALL include DirectConverter.capital_cost          │
│ - MR-003: Model SHALL compute LCOE broken down by subsystem         │
├──────────────────────────────────────────────────────────────────────┤
│ VALIDATION CRITERIA                                                  │
│ - VC-001: LCOE_turbine + LCOE_other = LCOE_total (within 1%)       │
│ - VC-002: Subsystem costs traceable to CAS category                 │
├──────────────────────────────────────────────────────────────────────┤
│ TEST ASSERTIONS                                                      │
│ - "TurbinePlant" in model.part_names                                │
│ - model.calc_outputs contains "lcoe_by_subsystem"                   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Proposed Solution: Structured Requirements in agentic-mbse

### 6. New Entity Types for LOCAL_GUIDE.md

#### 6.1 Analysis Angle Definition

```markdown
## Analysis Angles

Analysis Angles capture domain insights that shape model requirements.
They answer: "What perspectives on the problem do our models need to support?"

### AA-001: Energy Capture Method Comparison
**Captured By**: Reid Westwood
**Date**: 2026-01-26
**Source**: Team discussion on LCOE drivers

**Context**:
Steam turbine efficiency dominates OpEx. A steam turbine alone contributes
~0.5 cents/kWh to LCOE. When comparing fusion concepts, we need to isolate
the power conversion contribution to understand its impact.

**Model Implications**:
- Must model steam turbine as separate component
- Must model direct energy converter as alternative
- Must track power conversion costs in LCOE breakdown

**Analysis Implications**:
- Side-by-side comparison should highlight energy capture method
- Sensitivity study: vary conversion efficiency, show LCOE impact

**Derived Requirements**:
- MR-042: Model SHALL include 'Turbine Plant' with capital_cost
- MR-043: Model SHALL include optional 'Direct Energy Converter'
- MR-044: LCOE calc SHALL output conversion system contribution
```

#### 6.2 Requirements Registry

```markdown
## Requirements Registry

All model requirements in one place, linked to sources and tests.

| ID | Requirement | Source | Test |
|----|-------------|--------|------|
| MR-042 | Model SHALL include 'Turbine Plant' with capital_cost | AA-001 | test_turbine_plant_exists |
| MR-043 | Model SHALL include optional 'Direct Energy Converter' | AA-001 | test_dec_exists |
| MR-044 | LCOE calc SHALL output conversion system contribution | AA-001 | test_lcoe_breakdown |
| MR-045 | p_net SHALL match PyFECONS within 1% | G-001 | test_power_balance_accuracy |
```

#### 6.3 Validation Criteria Matrix

```markdown
## Validation Criteria

| ID | Description | Tolerance | PyFECONS Source | Test |
|----|-------------|-----------|-----------------|------|
| VC-001 | p_net power output | ±1% | PowerBalance.py:94 | test_power_balance_numerical |
| VC-002 | Magnet cost rollup | ±5% | cas220103_coils.py:125 | test_magnet_cost_accuracy |
| VC-003 | LCOE total | ±5% | lcoe.py:45 | test_lcoe_accuracy |
```

### 7. Enhanced Workflow Commands

#### 7.1 `/research` Enhancement

**Current behavior**: Creates research doc, findings only.

**Enhanced behavior**:
1. At end of research, prompt: "What Analysis Angles emerged from this research?"
2. Offer to create AA-XXX entries in LOCAL_GUIDE.md
3. Auto-link research doc to Analysis Angles

**Example output**:
```
Research complete! I've created:
- `modeling_pm/research/20260126-steam-turbine-analysis.md`

Suggested Analysis Angles for LOCAL_GUIDE.md:
1. AA-005: Steam turbine OpEx contribution
   - "Steam turbine accounts for ~0.5 cents/kWh in LCOE"
   - Model implication: Track turbine costs separately

Would you like me to add these Analysis Angles to LOCAL_GUIDE.md?
```

#### 7.2 `/spec-model` Enhancement

**Current behavior**: Creates MR-XXX requirements based on user input.

**Enhanced behavior**:
1. **Read Analysis Angles first**: Check LOCAL_GUIDE.md for relevant AA-XXX entries
2. **Derive requirements from Analysis Angles**: Prompt "I found these Analysis Angles that may be relevant..."
3. **Add traceability links**: Each MR-XXX links to source (AA-XXX, G-XXX, research doc)
4. **Generate test assertions**: For each MR-XXX, suggest pytest assertion

**Enhanced spec.md template**:
```markdown
## Derived from Analysis Angles

This spec incorporates requirements from:
- AA-001: Energy Capture Method Comparison
- AA-003: Blanket Material Trade-offs

## Modeling Requirements

### MR-001: Turbine Plant Cost Model
- **Type**: Functional
- **Description**: The model SHALL include 'Turbine Plant' :> 'Costed Component'
- **Source**: AA-001 (Energy Capture Method Comparison)
- **Test Assertion**: `"'Turbine Plant'" in [p.name for p in library.part_defs]`
- **Validation**: CAS23 cost matches PyFECONS within 5%
```

#### 7.3 New `/capture-angle` Command

**Purpose**: Quickly capture an Analysis Angle from discussion.

**Usage**:
```
/capture-angle "Steam turbine OpEx matters - 0.5 cents/kWh contribution"
```

**Process**:
1. Parse the input for key insights
2. Generate structured AA-XXX entry
3. Suggest model implications
4. Offer to link to existing research
5. Append to LOCAL_GUIDE.md

**Output**:
```markdown
## AA-006: Steam Turbine OpEx Contribution
**Captured By**: Claude
**Date**: 2026-01-26
**Source**: User input

**Context**:
Steam turbine contributes approximately 0.5 cents/kWh to LCOE,
making it a significant OpEx driver for comparison.

**Model Implications**:
- [ ] Track turbine costs separately from other power conversion
- [ ] Ensure CAS23 (Turbine Plant) costs are visible in LCOE breakdown

**Derived Requirements**: (to be added in /spec-model)
```

#### 7.4 New `/audit-requirements` Command

**Purpose**: Check that all Analysis Angles and Goals have traceability.

**Output**:
```
Requirements Audit Report
=========================

Analysis Angles (LOCAL_GUIDE.md):
- AA-001: Energy Capture Method Comparison
  ✅ Linked to MR-042, MR-043, MR-044 (spec.md)
  ✅ Tests exist: test_turbine_plant_exists, test_lcoe_breakdown

- AA-002: Blanket Material Trade-offs
  ⚠️  No derived requirements yet
  Suggestion: Create /spec-model for blanket modeling

Goals (OVERVIEW.md):
- G-001: LCOE estimation from components
  ✅ Covered by 8 MR-XXX requirements
  ⚠️  3 requirements missing tests

Gaps Found:
- 2 Analysis Angles have no derived requirements
- 3 Model Requirements have no tests
- 1 Validation Criteria has no PyFECONS source

Run /spec-model to address gaps?
```

### 8. LOCAL_GUIDE.md Structure

Based on the analysis, LOCAL_GUIDE.md should be restructured:

```markdown
# Local Modeling Guide

Project-specific patterns, requirements, and domain insights.

---

## Analysis Angles

Domain insights that shape model requirements. Created via `/research` or `/capture-angle`.

### AA-001: [Title]
...

---

## Requirements Registry

All model requirements linked to sources and tests.

| ID | Requirement | Source | Test | Status |
|----|-------------|--------|------|--------|
| MR-001 | ... | AA-001 | test_xxx | ✅ |

---

## Validation Criteria

Numerical validation targets.

| ID | Description | Tolerance | Source | Test |
|----|-------------|-----------|--------|------|
| VC-001 | ... | ±5% | PyFECONS:xxx | ... |

---

## Project-Specific Patterns

Domain-specific modeling patterns discovered.

---

## Lessons Learned

Modeling gotchas and discoveries.

---

**See also**:
- [MODELING_GUIDE.md](MODELING_GUIDE.md) for standard patterns
- [OVERVIEW.md](OVERVIEW.md) for project goals
```

### 9. Integration with Downstream Pipeline

#### 9.1 SysML Doc Comments → Requirement IDs

When `/implement-model` writes SysML:
```sysml
calc def 'Turbine Plant Cost Calc' {
    doc /*
     * Cost calculation for steam turbine plant.
     * Requirements: MR-042, MR-044
     * Analysis Angle: AA-001 (Energy Capture Method Comparison)
     * Source: PyFECONS cas23_turbine_plant_equipment.py:45
     */
    ...
}
```

#### 9.2 sysml-codegen Enhancement (Future)

Extract requirement IDs from doc comments:
```python
# In sysml-codegen extraction
calc_def_info = {
    "name": "Turbine Plant Cost Calc",
    "requirements": ["MR-042", "MR-044"],  # NEW: from doc comment
    "analysis_angles": ["AA-001"],          # NEW: from doc comment
    "source": "cas23_turbine_plant_equipment.py:45"
}
```

#### 9.3 TEAx Schema Enhancement (Future)

Include requirement metadata in generated schemas:
```python
class TurbinePlantParams(BaseModel):
    """Turbine plant parameters.

    Requirements: MR-042, MR-044
    Analysis Angle: AA-001
    """
    efficiency: float = Field(description="REQ MR-042: Turbine efficiency")
    capital_cost: float = Field(description="REQ MR-044: Capital cost for LCOE")
```

---

## Feasibility Assessment

### What Can Be Done Now (in agentic-mbse)

1. **Enhance LOCAL_GUIDE.md template** - Add Analysis Angles section
2. **Enhance `/research` command** - Prompt for Analysis Angles at end
3. **Enhance `/spec-model` command** - Read Analysis Angles, derive requirements
4. **Add `/capture-angle` command** - Quick capture during discussions
5. **Add `/audit-requirements` command** - Check traceability gaps

**Effort**: Medium (command changes, template updates)
**Impact**: High (prevents requirement dropping)

### What Requires sysml-codegen Changes (Future)

1. Extract requirement IDs from doc comments
2. Propagate to ComputationGraph
3. Include in generated Pydantic schemas

**Effort**: Medium
**Impact**: Medium (full traceability through codegen)

### What Requires TEAx Changes (Future)

1. Store requirement metadata in schemas
2. Report which requirements were exercised
3. Link results to validation criteria

**Effort**: Low-Medium
**Impact**: High (closes the loop)

---

## Recommendations

### Immediate (This Week)

1. **Update LOCAL_GUIDE.md template** in `project_templates/`
   - Add Analysis Angles section structure
   - Add Requirements Registry table
   - Add Validation Criteria table

2. **Create `/capture-angle` command**
   - Simple command to capture domain insights
   - Appends to LOCAL_GUIDE.md

3. **Enhance `/research` command**
   - At end, prompt for Analysis Angles
   - Offer to add to LOCAL_GUIDE.md

### Short-Term (Next Sprint)

4. **Enhance `/spec-model` command**
   - Read LOCAL_GUIDE.md Analysis Angles before starting
   - Prompt "These Analysis Angles may be relevant..."
   - Auto-link MR-XXX to source AA-XXX

5. **Create `/audit-requirements` command**
   - Parse LOCAL_GUIDE.md, active specs, test files
   - Report coverage gaps

### Medium-Term (Next Month)

6. **Enhance `/implement-model`**
   - Include requirement IDs in SysML doc comments
   - Standard format for requirement traceability

7. **Document the full workflow**
   - Add section to MODELING_PROCESS.md on requirements flow
   - Add examples of Analysis Angle → MR → Test

---

## Open Questions

1. **Granularity**: How detailed should Analysis Angles be? One per insight, or aggregated by topic?

2. **Persistence**: Should Analysis Angles live in LOCAL_GUIDE.md (per-project) or a separate file?

3. **Automation**: How much should be automated (auto-derive MR from AA) vs prompted?

4. **Cross-Project**: Can Analysis Angles be shared across projects (e.g., common fusion modeling angles)?

---

## Code/Model References

### agentic-mbse Files
- `claude/commands/research.md` - Research command (to be enhanced)
- `claude/commands/spec-model.md` - Spec command (to be enhanced)
- `project_templates/LOCAL_GUIDE.md.template` - Template to enhance
- `project_templates/OVERVIEW.md.template` - Goals template

### fusion-tea Files
- `modeling_pm/LOCAL_GUIDE.md` - Currently minimal
- `modeling_pm/OVERVIEW.md` - Has high-level goals
- `modeling_pm/research/20260126-lcoe-visibility-requirements-analysis.md` - Illustrates the problem
- `modeling_pm/research/20260123-pyfecons-library-mapping-strategy.md` - Example of rich research without requirement links

### Pipeline References
- `sysml-codegen/src/sysml_codegen/extraction/` - Where requirement extraction would happen
- `teax/packages/teax-simkit/simkit/core/` - Where requirement metadata would flow

---

**Last Updated**: 2026-01-26
