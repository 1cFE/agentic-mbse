# Implement Model Command

**Purpose:** Execute approved implementation plan for SysMLv2 models
**Input:** `project/active/{feature-name}/plan.md`
**Output:** Model files, updated plan with progress

## Overview

Execute SysMLv2 model implementation according to approved plan with validation and progress tracking.

When invoked:
- If feature name provided: begin the implementation process below. 
- If no feature: ask "Which feature should I implement?" and request feature name

You must follow this process! Make heavy usage of TODO tools to ensure you don't miss steps. 

## Process

### Stage 1: Plan Analysis & Scope Confirmation

**Context**: Implementation refines a validated prototype to production quality.
- **Design phase** produced: validated prototype (working .sysml files passing Levels 1-3)
- **Plan phase** defined: refinement roadmap with phases
- **Implementation phase** executes: refinements per plan

1. **Read Plan**: `project/active/{feature-name}/plan.md` FULLY
2. **Read Design for Prototype Context**: `project/active/{feature-name}/design.md`
   - Check "Design Validation Report" section for prototype files created
   - Note validation status (Levels 1-3 should be passing)
   - Review any Level 4-7 issues to address
3. **Review Prototype State**:
   - Read prototype files listed in design.md (in models/library/ or models/designs/)
   - Understand what's already working
   - Identify what needs refinement (per plan phases)
4. **Read MODELING_GUIDE**: Refresh conventions
5. **Check Progress**: Look for existing checkmarks in plan.md

### Stage 1.2: Efficient Reference Document Handling

**When working with large plan documents (>500 lines):**

#### DON'T: Re-read full documents repeatedly

```python
# Anti-pattern - wastes 30k tokens
Read("plan.md")  # 1200 lines
# ... create file 1 ...
Read("plan.md")  # Same 1200 lines again!
# ... create file 2 ...
Read("plan.md")  # Yet again!
```

#### DO: Read once, extract sections

```python
# Efficient - read once at start
plan_full = Read("project/active/structure/plan.md")

# Extract only this phase (e.g., lines 450-580 for Phase 3)
phase3_lines = plan_full.split('\n')[449:580]  # 0-indexed
phase3_content = '\n'.join(phase3_lines)

# Work with extracted section (much smaller context)
# Can reference multiple times without re-reading full file
```

#### DO: Use Task agent for complex extraction

```python
# For very large docs, use sub-agent to extract
Task(
    description="Extract Phase 3 details",
    prompt="""
    Read project/active/structure/plan.md, extract Phase 3 section.

    Return condensed version with:
    - Codebase source line number mappings
    - File creation specs
    - Validation criteria

    Maximum 200 lines output.
    """,
    subagent_type="general-purpose",
    model="haiku"
)
# Use returned condensed version instead of full plan
```

#### Guidelines

- Read full plan **once** at start of phase
- Extract relevant sections for current work
- Store in memory for phase duration
- Only re-read if plan is updated mid-phase
- For files >1000 lines, consider extraction sub-agent

6. **Confirm Scope** - Same as implement-code:
   ```
   Choose execution approach:
   1. One-by-one (safer)
   2. Multiple phases (specify)
   3. All phases (faster)
   ```

7. **Create TodoWrite** - Mirror plan tasks (focus on refinements, not creation)

### Stage 1.3: Assess Parallelization Opportunities

**When multiple independent files need creation:**

#### Option A: Sequential (Traditional)
Create files one by one in main agent:
- **Use when**: Files have dependencies, need careful sequencing
- **Benefits**: Direct control, easier debugging
- **Drawback**: Slower, more context usage

#### Option B: Parallel (Efficient)
Create multiple independent files concurrently using Task tool:
- **Use when**: 3+ files are independent (no cross-dependencies)
- **Benefits**: Faster execution, reduced context usage
- **Requirement**: Files can be created in any order

**Parallel Execution Pattern:**

Use the Task tool with `subagent_type="general-purpose"` to create multiple files in parallel:
1. Prepare specifications for each file from the plan
2. Launch Task agents in parallel (single message, multiple Task calls)
3. Each agent creates one file with full specification
4. Main agent collects results and validates batch

**Note**: Projects can define custom file-creation agents tailored to their validation
needs for more sophisticated parallel workflows.

**After parallel creation:**
1. Collect results from all agents
2. Run batch validation on all files
3. Commit all files together with single commit

**Safety:**
- Sub-agents create files only (NO commits)
- Main agent validates batch
- Main agent makes single commit
- No git conflicts (distinct file paths)

### Stage 1.4: Pre-Flight Syntax Validation

**BEFORE creating ANY SysML model files:**

1. **De-risk complex syntax** by testing in a temp file first:
   ```bash
   # Create a minimal test file with your snippet
   cat > /tmp/test_snippet.sysml << 'EOF'
   package TestSnippet {
       // Paste your uncertain syntax here:
       attribute test : Real = 1.0 [m];
   }
   EOF

   # Validate with syside
   syside check /tmp/test_snippet.sysml
   ```

2. **Common patterns to pre-test:**
   - Attribute declarations with units
   - Material references (String vs import)
   - Part definitions (standalone vs specialized)
   - Temperature values (always Kelvin [K])
   - Any complex syntax you're uncertain about

3. **ONLY after validation passes**, proceed with file creation

4. **If validation fails:**
   - Review the syside error message
   - Fix the pattern
   - Re-test until it passes
   - Then use corrected pattern in your actual file

**This prevents:**
- Iterative syntax correction loops
- Unicode unit errors (m³ → m^3)
- Missing type declarations (recommended best practice)
- Failed parse checks after file creation

### Stage 2: Sequential Implementation

For each task in the plan:

1. **Start with Model Stencil** - Follow pattern from plan
2. **Create/Modify Models** - Use Write or Edit tools
3. **Add Doc Comments** - CRITICAL for every definition:
   ```sysmlv2
   part def 'Component Name' {
       doc /*
       Description

       **Source**: Citation with section
       **Reference**: data/documents/file.pdf
       **Assumptions**: List
       **Last Updated**: YYYY-MM-DD
       */
       // ...
   }
   ```
4. **Validate After Each Model**:
   ```bash
   # Quick syntax check on single file
   syside check models/path/to/file.sysml
   ```

   If any validations don't pass, you are having trouble resolving parsing issues, or any other modeling challenges arise, make sure of the "sysmlv2-doc-analyzer" subagent!! This agent has full knowledge of the SysMLv2 spec as well as the SysIDE parser, and can help provide guidance as to how to resolve issues. 
   
5. **IMMEDIATELY Update Progress** - CRITICAL for tracking:
   - **TodoWrite**: Mark current task as completed
   - **Plan Document**: Use Edit tool to change `- [ ]` to `- [x]` for completed items. You MUST update the task items under the appropriate `## Phase <#>: <name>` section!
   - **Do this BEFORE moving to next task** - Don't batch checkbox updates

   Example Edit:
   ```markdown
   OLD: - [ ] Define `part def 'Component Name'`
   NEW: - [x] Define `part def 'Component Name'`
   ```

### Stage 2.5: Efficient Batch Editing

**When making multiple similar changes to a file:**

#### DON'T: Sequential individual edits

```python
# Anti-pattern - 18 separate Edit calls
Edit(file, "attribute x =", "attribute x : Real =")
Edit(file, "attribute y =", "attribute y : Real =")
Edit(file, "attribute z =", "attribute z : Real =")
# ... 15 more times
# Total: 18 tool calls, 18 file reads/writes
```

#### DO: Collect patterns, apply efficiently

**Option A: Read, modify in memory, Write**

```python
# Read once
content = Read("models/file.sysml")

# Apply all replacements in memory
patterns = [
    ("attribute x =", "attribute x : Real ="),
    ("attribute y =", "attribute y : Real ="),
    ("attribute z =", "attribute z : Real ="),
    # ... all patterns
]

for old, new in patterns:
    content = content.replace(old, new)

# Write once
Write("models/file.sysml", content)
# Total: 1 read, 1 write
```

**Option B: Script for complex patterns**

```python
# Create temporary Python script
script = """
import sys
content = open(sys.argv[1]).read()

# All replacements
replacements = {
    'attribute name =': 'attribute name : String =',
    'attribute count =': 'attribute count : Real =',
    # ... all patterns
}

for old, new in replacements.items():
    content = content.replace(old, new)

open(sys.argv[1], 'w').write(content)
"""

Write("/tmp/batch_edit.py", script)
Bash("python /tmp/batch_edit.py models/file.sysml")
```

#### When to use each approach:

- **Option A (Read/Write)**: 5-20 similar changes, straightforward patterns
- **Option B (Script)**: 20+ changes, complex patterns, regex needed
- **Individual Edits**: 1-4 changes, different contexts

### Stage 3: Phase Completion & Validation

1. **Run All Validations**:
   ```bash
   # STEP 1: Comprehensive Quality Validation (8 levels)
   # This runs all quality checks on your models
   agentic-mbse validate models/

   # Quality check output explains each level:
   # Level 1: Syntax Validation (parser errors)
   # Level 2: Structural Completeness (unused definitions, unbound inputs)
   # Level 3: Dataflow Integrity (circular dependencies)
   # Level 4: Constraint Satisfaction (constraint coverage metrics)
   # Level 5: Semantic Consistency (unit consistency, constraint coverage)
   # Level 6: Traceability & Documentation (missing doc comments)
   # Level 7: Architectural Integrity (manifest validation)
   # Level 8: Codegen Readiness (qualified names, calc def structure)

   # CRITICAL: If quality checks fail:
   # - Review the failure output carefully
   # - Fix issues in your models
   # - Re-run quality checks
   # - STOP and report to user if unable to resolve
   # - DO NOT proceed to commit if Level 1-3 fail (critical errors)
   # - Levels 4-8 warnings are informational but should be reviewed

   # STEP 2: ADR-002 Compliance Check
   # Verify no calc defs in design files (per ADR-002 Rule 1)
   grep -r "calc def" models/designs/
   # Should return empty - if not, move calc defs to library/
   ```

   **Quality Check Interpretation:**
   - **Levels 1-3 MUST pass** - These are critical errors that break models
   - **Levels 4-8 provide insights** - Warnings guide improvements but don't block
   - Use `--complete` flag to see all issues: `agentic-mbse validate models/ --complete`
   - Use `--level N` to run specific level: `agentic-mbse validate models/ --level 1`
   - Use `--verbose` for detailed output: `agentic-mbse validate models/ --verbose`

2. **MANDATORY: Update Plan Document**:
   ```markdown
   ### Phase [N] Completion
   **Completed:** 2025-10-27 15:00
   **Models Created:**
   - `models/library/components/magnets.sysml`
     - Defined `part def 'TF Coil'` with 12 attributes
     - Added constraints FieldLimit, TemperatureLimit
     - All doc comments include sources
   - Updated `models/designs/{design_name}/magnets.sysml`
     - Created instance tf_system with specific values

   **Traceability Updates:**
   - Added 5 entries to traceability_matrix.csv
   - Documented 2 assumptions in assumption_register.md

   **Validation Results:**
   - All models parse successfully
   - Traceability check passed
   - Baseline comparison: geometry matches within 0.1%

   **Issues Encountered:**
   - Initial parse error due to typo in attribute type
   - Fixed: Changed `Lenght` to `Length`

   **Deviations from Plan:**
   - Added extra constraint MaterialCompatibility
   - Reason: Found in ITER design docs during implementation
   ```

3. **MANDATORY: Update Traceability Files**:
   - Update `data/traceability_matrix.csv`
   - Update `data/assumption_register.md` if assumptions made
   - Update `data/documents/bibliography.bib` if new sources

4. **MANDATORY: Synchronize Status**:
   - Mark spec status: "Implementation Complete"
   - Update epic deliverables
   - Update CURRENT_WORK.md
   - Update CHANGELOG.md

### Stage 4: Final Validation

If all phases complete:
- [ ] **Quality validation passes** (Levels 1-3 with no failures)
- [ ] All models parse without errors
- [ ] All definitions have doc comments with sources
- [ ] Traceability check passes
- [ ] Baseline comparison passes (if applicable)
- [ ] Constraints properly defined
- [ ] Naming conventions followed
- [ ] Epic deliverables marked complete
- [ ] Quality check warnings reviewed and addressed where appropriate

## Guidelines

### MODEL QUALITY (CRITICAL - NEVER VIOLATE)
**NEVER create:**
- Definitions without doc comments
- Doc comments without **Source** citation
- Usages with Title Case (should be snake_case)
- Definitions with snake_case (should be Title Case)
- Models without standard imports (ScalarValues, ISQ, SI)

**ALWAYS ensure:**
- Every `part def`, `attribute def`, `calc def`, `constraint def` has doc comment
- Doc comment includes Source and Reference
- Naming follows MODELING_GUIDE exactly
- Traceability matrix updated
- Parse validation passes

### MANDATORY Progress Tracking
**You MUST (after completing each task):**
1. **Update TodoWrite** - Mark task as completed
2. **Update Plan Checkboxes** - Use Edit tool to change `- [ ]` to `- [x]` in plan.md
   - Do NOT batch updates - update immediately after each task
   - Update all sub-items under a completed task
3. **Update Traceability** - Add entries to traceability_matrix.csv as you create definitions
4. **Update Assumptions** - Document in assumption_register.md if making assumptions
5. **Document Issues** - Add to plan's "Implementation Notes" section

**Progress Update Pattern (use after EVERY completed task):**
```
1. Mark TodoWrite item complete
2. Edit plan.md to check off boxes: - [ ] → - [x]
3. Add any traceability entries
4. Continue to next task
```

### Implementation Standards
- Follow MODELING_GUIDE conventions exactly
- Definitions vs usages distinction critical
- Include units with values: `= 4.15 [m]`
- Cite codebase sources (from SOURCE_INDEX.md) with line numbers in comments
- Validate parse after each model file
- Check traceability before completing phase

### Validation Requirements
After implementation:
1. **Parse validation** - All models must parse
2. **Traceability validation** - check_traceability.py passes
3. **Convention validation** - Manual check of naming
4. **Baseline validation** - Comparison if applicable (from SOURCE_INDEX.md)
5. **Constraint validation** - Constraints evaluatable

### Error Handling
- STOP if model doesn't parse
- STOP if traceability check fails
- STOP if Baseline comparison fails significantly
- Document ALL deviations in plan
- Get approval before continuing if major issues

---

**Related Commands:**
- Before implement → `/plan-model` (plan must include prototype baseline and refinement roadmap)
- After implement → Verify, update epic, move to completed

**Workflow Notes:**
- Implementation refines an existing validated prototype (from design phase)
- Prototype files already exist in models/ and pass Levels 1-3 validation
- Focus on adding: complete documentation, full constraints, comprehensive integration
- Plan defines what refinements to make, not what to create from scratch

**Last Updated**: 2025-11-17
