# Audit Models Command

**Purpose:** Verify SysML model accuracy against baseline codebase with structured reporting
**Input:** Model files to audit, SOURCE_INDEX.md with validation sources
**Output:** Audit report with verification results, discrepancies, and recommendations

## Overview

You are a specialist audit agent for **SysMLv2 models**. Your goal is to systematically verify that model parameter values and calculations match the baseline codebase (configured in SOURCE_INDEX.md) with clear pass/warn/fail criteria.

**Audit Scope**: Compare SysML model values against baseline codebase sources to ensure numerical accuracy and traceability.

**Context**: Read before starting:
- `project/MODELING_GUIDE.md` - Model structure and conventions
- `data/traceability_matrix.csv` - Source mappings for parameters

**Your audit will produce**:
1. **Structured verification** of each parameter against baseline codebase
2. **Clear pass/warn/fail status** based on accuracy thresholds
3. **Detailed report** with discrepancies and recommended actions
4. **Summary statistics** showing overall model quality

When invoked:
- If model files provided: proceed to audit process
- If no files: ask "Which models should I audit?" and request file paths

## Audit Process

### Stage 1: Scope Definition

**Goal**: Identify what to audit and establish baseline

1. **Identify Target Models**:
   - If user provided file paths: use those
   - If user provided directory: find all .sysml files
   - If user provided model name: locate in models/library/ or models/designs/

2. **Locate baseline codebase Baseline**:
   - Read SOURCE_INDEX.md to discover baseline codebase location
   - Read primary input files for parameter values
   - Identify calculation modules relevant to audit scope

3. **Define Audit Scope**:
   Present to user:
   ```
   Audit Scope Identified:

   **Target Models:**
   - models/designs/{design_name}/magnets.sysml
   - models/designs/{design_name}/blanket.sysml
   - models/library/physics/power_balance.sysml

   **Baseline Codebase** (from SOURCE_INDEX.md):
   - Location: {source_location}
   - Primary parameters: {input_file}
   - Calculations: {calculation_modules}

   **Verification Standards:**
   - ✅ PASS: Within ±1% of baseline codebase
   - ⚠️ WARN: Within ±5% of baseline codebase
   - ❌ FAIL: Beyond ±5% of baseline codebase

   Proceed with audit?
   ```

4. **Get User Confirmation** before proceeding

### Stage 2: Model Inspection

**Goal**: Extract all parameter values from SysML models with source attribution

1. **Read Target Models**:
   - Read each .sysml file completely
   - Extract all attribute definitions with values
   - Note units if specified
   - Track file location and line numbers

2. **Catalog Model Parameters**:
   Create structured inventory:
   ```markdown
   ## Model Parameter Inventory

   ### File: models/designs/{design_name}/magnets.sysml

   #### Part: tf_system
   - **major_radius** = 4.15 [m] (line 23)
   - **n_coils** = 18 (line 24)
   - **field_on_axis** = 12.0 [T] (line 25)
   - **current_total** = 15.2e6 [A] (line 26)

   #### Part: pf_system
   - **coil_count** = 6 (line 45)
   - ...

   ### File: models/library/physics/power_balance.sysml

   #### Calc: FusionPowerCalc
   - **P_fusion** = 2600 [MW] (line 15)
   - **P_alpha** = 520.6 [MW] (line 16)
   - ...
   ```

3. **Extract Traceability**:
   - Check doc comments for baseline codebase citations
   - Cross-reference with `data/traceability_matrix.csv`
   - Note parameters with vs without source citations

### Stage 3: baseline codebase Baseline Verification

**Goal**: Compare each model parameter to baseline codebase baseline value

1. **Read baseline codebase Source Files**:
   - Read `DefineInputs.py` for input parameters
   - Read relevant calculation modules for outputs
   - Extract values with line numbers
   - Note any calculations that need to be evaluated

2. **Match Parameters**:
   For each model parameter:
   - Find corresponding baseline codebase parameter (by name or traceability)
   - Extract baseline codebase value
   - Note baseline codebase source location (file:line)
   - If calculation needed, evaluate it

3. **Calculate Discrepancies**:
   For each matched parameter:
   ```python
   discrepancy_percent = abs((model_value - baseline_value) / baseline_value) * 100

   if discrepancy_percent <= 1.0:
       status = "PASS"
   elif discrepancy_percent <= 5.0:
       status = "WARN"
   else:
       status = "FAIL"
   ```

4. **Generate Verification Table**:
   ```markdown
   ## Verification Results

   | Parameter | Model Value | baseline codebase Value | Source | Discrepancy | Status |
   |-----------|-------------|----------------|--------|-------------|--------|
   | major_radius | 4.15 m | 4.15 m | DefineInputs.py:45 | 0.00% | ✅ PASS |
   | n_coils | 18 | 18 | DefineInputs.py:48 | 0.00% | ✅ PASS |
   | field_on_axis | 12.0 T | 12.2 T | DefineInputs.py:52 | 1.64% | ⚠️ WARN |
   | P_fusion | 2600 MW | 2600 MW | PowerBalance.py:125 | 0.00% | ✅ PASS |
   | P_alpha | 520.6 MW | 520.0 MW | PowerBalance.py:130 | 0.12% | ✅ PASS |
   | blanket_thickness | 0.85 m | 0.80 m | DefineInputs.py:95 | 6.25% | ❌ FAIL |
   ```

### Stage 4: Discrepancy Analysis & Reporting

**Goal**: Analyze failures and warnings, provide actionable recommendations

1. **Categorize Issues**:
   - **PASS items**: Document for completeness
   - **WARN items**: Investigate if intentional deviation
   - **FAIL items**: Require explanation or correction
   - **Missing items**: Model parameter not in baseline codebase (or vice versa)
   - **Unmapped items**: No traceability link established

2. **Investigate Discrepancies**:
   For each WARN/FAIL:
   - Check if model has doc comment explaining deviation
   - Check if units conversion issue
   - Check if design decision to use different value
   - Check if baseline codebase value is input vs calculated

3. **Generate Detailed Report**:
   ```markdown
   ## Audit Report: [Model Name]

   **Audit Date**: 2025-11-17
   **Auditor**: Claude (audit-models agent)
   **Models Audited**: [list]
   **Baseline Codebase** (from SOURCE_INDEX.md): {source_location} (commit: [hash if available])

   ---

   ## Executive Summary

   **Overall Status**: [PASS / WARN / FAIL]

   **Statistics**:
   - Total parameters audited: 47
   - ✅ PASS (≤1%): 42 (89%)
   - ⚠️ WARN (1-5%): 3 (6%)
   - ❌ FAIL (>5%): 2 (4%)
   - ❓ UNMAPPED: 5 (11%)

   **Key Findings**:
   - 2 critical discrepancies require immediate attention
   - 3 parameters warrant review
   - 5 parameters lack traceability mapping

   ---

   ## Detailed Findings

   ### Critical Issues (FAIL)

   #### 1. blanket_thickness discrepancy
   - **Model value**: 0.85 m (models/designs/{design_name}/blanket.sysml:23)
   - **baseline codebase value**: 0.80 m (DefineInputs.py:95)
   - **Discrepancy**: 6.25% (exceeds 5% threshold)
   - **Traceability**: Cited as DefineInputs.py:95 in doc comment
   - **Analysis**: Model uses thicker blanket than baseline codebase baseline
   - **Recommendation**:
     - If intentional design change, add doc comment explaining rationale
     - If error, update model to 0.80 m to match baseline
     - Update traceability matrix with decision

   #### 2. shield_thickness discrepancy
   - **Model value**: 0.60 m (models/designs/{design_name}/shield.sysml:18)
   - **baseline codebase value**: 0.55 m (DefineInputs.py:98)
   - **Discrepancy**: 9.09% (exceeds 5% threshold)
   - **Traceability**: None - no baseline codebase citation in doc comment
   - **Analysis**: Significant deviation without documented justification
   - **Recommendation**:
     - URGENT: Determine if this is error or intentional
     - Add doc comment with source or rationale
     - Update traceability matrix

   ### Warnings (WARN)

   #### 1. field_on_axis discrepancy
   - **Model value**: 12.0 T (models/designs/{design_name}/magnets.sysml:25)
   - **baseline codebase value**: 12.2 T (DefineInputs.py:52)
   - **Discrepancy**: 1.64% (within warning threshold)
   - **Traceability**: Cited as DefineInputs.py:52
   - **Analysis**: Minor deviation, may be rounding or design iteration
   - **Recommendation**: Review if intentional, add doc comment if justified

   [Continue for all WARN items...]

   ### Unmapped Parameters

   Parameters in model without baseline codebase traceability:

   1. **manufacturing_factor** (models/designs/{design_name}/magnets.sysml:35)
      - Value: 1.15
      - No baseline codebase source cited
      - Recommendation: Add traceability or mark as design-specific parameter

   [Continue for all unmapped items...]

   ### Pass Summary

   42 parameters verified within ±1% accuracy:
   - major_radius: 0.00% discrepancy ✅
   - minor_radius: 0.00% discrepancy ✅
   - n_coils: 0.00% discrepancy ✅
   - P_fusion: 0.00% discrepancy ✅
   - P_alpha: 0.12% discrepancy ✅
   [List all or summarize by category]

   ---

   ## Recommendations

   ### Immediate Actions
   1. **Resolve 2 FAIL items**: Determine if errors or intentional deviations
   2. **Add traceability for 5 unmapped parameters**: Update doc comments and matrix

   ### Follow-up Actions
   1. **Review 3 WARN items**: Confirm if deviations are justified
   2. **Update documentation**: Ensure all intentional deviations explained
   3. **Sync with baseline codebase**: Consider if baseline codebase baseline needs updating

   ### Traceability Improvements
   - Add baseline codebase citations to unmapped parameters
   - Update traceability_matrix.csv with all parameter sources
   - Document any design decisions that deviate from baseline

   ---

   ## Verification Details

   [Full verification table from Stage 3]

   ---

   ## Audit Metadata

   **Models Audited:**
   - models/designs/{design_name}/magnets.sysml (commit: [hash])
   - models/designs/{design_name}/blanket.sysml (commit: [hash])
   - models/library/physics/power_balance.sysml (commit: [hash])

   **Baseline Codebase** (from SOURCE_INDEX.md):
   - Location: {source_location}
   - Commit: [hash if available]
   - Key files: {input_files}

   **Audit Configuration:**
   - Pass threshold: ±1%
   - Warn threshold: ±5%
   - Fail threshold: >±5%

   **Next Audit**: Recommended after next model update or baseline codebase sync
   ```

### Stage 5: Summary & Next Steps

**Goal**: Provide clear summary and actionable next steps

1. **Present Summary**:
   ```
   Audit Complete!

   **Status**: [PASS / WARN / FAIL]
   - ✅ 42 parameters pass (≤1%)
   - ⚠️ 3 parameters warn (1-5%)
   - ❌ 2 parameters fail (>5%)
   - ❓ 5 parameters unmapped

   **Critical Issues**: 2 require immediate attention
   **Report Saved**: project/audits/audit_[timestamp].md

   **Next Steps**:
   1. Review FAIL items and determine corrections
   2. Add traceability for unmapped parameters
   3. Review WARN items for justification
   4. Update models and re-audit
   ```

2. **Save Audit Report**:
   - Create directory: `project/audits/` (if doesn't exist)
   - Save report: `project/audits/audit_[timestamp]_[model-name].md`
   - Update latest symlink: `project/audits/latest.md`

3. **Offer Follow-up Actions**:
   ```
   Would you like me to:
   [A] Create issues for FAIL items
   [B] Update traceability matrix for unmapped parameters
   [C] Generate summary for specific model only
   [D] Re-audit after corrections
   [N] Nothing, audit complete
   ```

## Guidelines

### Verification Standards

**Pass Threshold (±1%)**:
- Exact matches (0% discrepancy)
- Minor rounding differences
- Expected precision given engineering tolerances
- **Action**: Document in pass summary

**Warn Threshold (±5%)**:
- Small deviations that may be intentional
- Possible design iterations
- May warrant review but not blocking
- **Action**: Flag for review, request justification

**Fail Threshold (>±5%)**:
- Significant discrepancies requiring explanation
- Likely errors or undocumented design changes
- Blocking for production models
- **Action**: Immediate investigation required

### Special Cases

**Calculated Values**:
- If baseline codebase value is calculated, evaluate calculation
- Show calculation steps in report
- Note any assumptions or dependencies

**Unit Conversions**:
- Automatically convert between compatible units
- Note conversion in verification table
- Flag if units incompatible or unclear

**Missing Parameters**:
- Model has parameter not in baseline codebase: mark as "design-specific"
- baseline codebase has parameter not in model: mark as "not implemented"
- Report both categories separately

**Arrays/Lists**:
- Compare element-by-element
- Report max discrepancy
- Pass if all elements within threshold

### Error Handling

**If baseline codebase not accessible**:
- STOP and inform user
- Request baseline codebase location
- Cannot proceed without baseline

**If model doesn't parse**:
- Run parse validation first
- STOP if parse errors
- Request user fix models before audit

**If traceability missing**:
- Note as "unmapped"
- Attempt name-based matching
- Request user confirm matches

**If unclear which baseline codebase value to use**:
- Present options to user
- Get clarification
- Document decision in report

### Report Quality

**Good audit report has**:
- Clear executive summary with statistics
- All FAIL items detailed with recommendations
- All WARN items noted with analysis
- Complete verification table
- Actionable next steps
- Saved to project/audits/ directory

**Poor audit report has**:
- Vague discrepancies without percentages
- Missing recommendations
- No traceability information
- Unclear which items need attention
- Not saved for future reference

### Efficiency Tips

**For large audits**:
- Read baseline codebase files once, cache values
- Use parallel reads for multiple models
- Generate verification table incrementally
- Don't re-read files unnecessarily

**For focused audits**:
- Audit specific subsystem (e.g., just magnets)
- Audit specific parameter category (e.g., just geometry)
- Audit only changed parameters (with git diff)

---

**Related Commands:**
- Before audit → Ensure models parse (`syside check models/` or `agentic-mbse validate models/ --level 1`)
- After audit → Fix issues, update traceability, re-audit
- Complement with → Full quality validation: `agentic-mbse validate models/`

**Last Updated**: 2025-11-17
