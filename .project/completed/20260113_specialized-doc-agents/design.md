# Design: Specialized Documentation Agents

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-01-13
**Branch:** 1cfe_dev
**Commit:** 9673064

---

## Overview

Design four specialized documentation agents to replace the monolithic `sysmlv2-doc-analyzer`, enabling focused expertise, parallel research, and syntax validation capabilities.

## Related Artifacts

- **Spec:** `.project/active/specialized-doc-agents/spec.md`
- **Research:** `.project/research/20260112-064217_sysmlv2-agent-discoverability-failure.md`
- **Epic:** `.project/backlog/epic_documentation-discoverability.md`
- **Current Agent:** `claude/agents/sysmlv2-doc-analyzer.md` (to be deprecated)

---

## Research Findings

### Existing Agent Pattern Analysis

The current `sysmlv2-doc-analyzer.md` follows this structure:
- YAML frontmatter: `name`, `description`, `tools`
- Documentation structure section describing corpus
- Search strategy with phases (Discovery, Targeted Reading)
- Response format template
- Guidelines (DO/DON'T lists)
- Edge cases

This pattern is effective and should be preserved in specialized agents.

### INDEX.md Structure

The new INDEX.md files provide:
- YAML frontmatter with document metadata (checksum, total lines, section count)
- Hierarchical section summaries with line number ranges
- Content summaries for each section

Example from KerML spec INDEX.md:
```
### 9.4.7 Numerical Functions
**Lines:** 13216-13231

Abstract functions for arithmetic operations (`+`, `-`, `*`, `/`, `**`, `^`, `%`),
comparison operators (`<`, `>`, `<=`, `>=`), utility functions (`isZero`, `isUnit`,
`abs`, `max`, `min`), and collection aggregations (`sum`, `product`) on NumericalValue
types, all specializing corresponding ScalarFunctions.
```

This enables targeted reading with precise offset/limit values.

### KerML Spec Structure (for kerml-expert)

Key sections for standard library questions:
- **Section 9.2**: Semantic Library (foundational types: Anything, DataValue, Occurrence)
- **Section 9.3**: Data Type Library (Boolean, String, numeric hierarchy)
- **Section 9.4**: Function Library (17 subsections covering all operators and functions)
  - 9.4.2: Base Functions (equality, identity, type checking)
  - 9.4.7: Numerical Functions (sum, product, abs, max, min)
  - 9.4.14: Sequence Functions (size, isEmpty, includes, head, tail)
  - 9.4.17: Control Functions (collect, select, reduce, forAll, exists)

Total: 13,958 lines across 111 sections.

### SysML Spec Structure (for sysml-expert)

**Part 1**: Not in INDEX.md yet (language constructs) - uses existing full_document.md
**Part 2**: 32,376 lines, 50 sections - v1→v2 transformation mappings
**Part 3**: 2,000 lines, 34 sections - API and Services specification

Key areas:
- Part 2 Section 7: Mappings (UML→SysML v2 transformations)
- Part 2 Section 7.8: SysML v1.7 stereotype mappings
- Part 3 Section 7: Platform Independent Model (API data structures)
- Part 3 Section 8: Platform Specific Models (REST, OSLC bindings)

### syside Documentation Structure

```
docs/syside/
├── api/
│   ├── README.md
│   └── generated/  (100+ API reference files)
├── automator/
│   ├── advanced.md (expression evaluation, execution)
│   └── syside.preview
└── examples/
```

No INDEX.md - relies on grep-based search.

### syside CLI and Python API Capabilities

**CLI Commands:**
- `syside check <file>` - Quick syntax validation
- `syside-license check` - Verify license activation

**Python API (Key Classes for Model Inspection):**

| Class | Purpose |
|-------|---------|
| `syside.load_model()` | Load model, raises on errors |
| `syside.try_load_model()` | Load model, tolerates errors for partial analysis |
| `syside.Model` | Root model object with `nodes()`, `documents`, `lib` |
| `syside.Document` | Single document with `root_node`, `all_nodes()` |
| `syside.AstNode` | Base for all AST nodes: `parent`, `owned_elements`, `try_cast()` |
| `syside.Heritage` | Type specialization chain for elements |
| `syside.Compiler` | Expression evaluation via `evaluate()`, `evaluate_feature()` |
| `syside.pprint()` | Pretty-print element back to textual syntax |

**Element Types for Querying:**
- `syside.PartUsage`, `syside.PartDefinition`
- `syside.AttributeUsage`, `syside.AttributeDefinition`
- `syside.PortUsage`, `syside.PortDefinition`
- `syside.ConnectionUsage`
- `syside.RequirementUsage`, `syside.RequirementDefinition`
- `syside.ConstraintUsage`
- `syside.ActionUsage`, `syside.StateUsage`
- `syside.Expression`

**Key Patterns from syside Examples:**
1. **Model loading with error tolerance** (`examples/type_checking.md`):
   - `try_load_model()` lets you analyze even invalid models
   - Diagnostics contain detailed type errors with line numbers

2. **AST traversal** (`examples/extract_parts.md`):
   - `element.owned_elements.for_each()` for recursive traversal
   - `try_cast()` for type-safe element inspection
   - `heritage.elements` for type hierarchy

3. **Type checking** (`examples/type_checking.md`):
   - Built into `load_model()` - type errors appear in diagnostics
   - Pattern: `"type-error"` in diagnostic string

4. **Document locking** (required for multi-threaded access):
   ```python
   for doc in model.user_docs:
       with doc.lock() as locked:
           walk(locked.root_node)
   ```

---

## Proposed Design

### Architecture Overview

```
claude/agents/
├── kerml-expert.md          (NEW - KerML spec + standard library)
├── sysml-expert.md          (NEW - SysML Parts 1-3)
├── syside-expert.md         (NEW - syside tooling)
├── sysmlv2-validator.md     (NEW - syntax validation)
├── deprecated/
│   └── sysmlv2-doc-analyzer.md  (MOVE)
└── python-debugger.md       (unchanged)
```

### Component 1: kerml-expert Agent

**File:** `claude/agents/kerml-expert.md`

**Purpose:** Expert on KerML language specification, standard library functions, type system, and language semantics.

**Corpus:**
- `{SYSML_DOCS_PATH}/SysML_KerMLSpec/INDEX.md` (primary navigation)
- `{SYSML_DOCS_PATH}/SysML_KerMLSpec/full_document.md` (source content)

**Frontmatter:**
```yaml
---
name: kerml-expert
description: KerML language expert. Use for standard library functions (sum, size, collect, reduce, etc.), type system questions, language semantics, expression operators, and KerML specification lookups. Has access to KerML spec with INDEX.md navigation.
tools: Read, Grep, Glob
---
```

**System Prompt Structure:**

1. **Role Statement**: KerML language specialist for standard library and semantics
2. **Documentation Structure**:
   - INDEX.md location and how to use line numbers
   - Key sections for common queries (9.2 Semantic, 9.3 Data Types, 9.4 Functions)
3. **Search Strategy**:
   - Phase 1: Read INDEX.md, grep for section summaries
   - Phase 2: Use offset/limit based on INDEX.md line numbers
   - Phase 3: Synthesize with citations
4. **Function Discovery Quick Reference**:
   - Section 9.4.7 for numerical (sum, product, abs)
   - Section 9.4.14 for sequences (size, isEmpty, head, tail)
   - Section 9.4.17 for control (collect, select, reduce)
5. **Import Pattern Guidance**: Always suggest import syntax
6. **Response Format**: Overview, findings with citations, recommendations
7. **Critical Rule**: NEVER say "X doesn't exist" - only "I couldn't find X in my corpus"

**Key Sections Quick Reference (embedded in prompt):**
```markdown
## Quick Section Reference

For function questions, check these INDEX.md sections FIRST:

| Topic | Section | Lines |
|-------|---------|-------|
| Numerical (sum, product, abs, max, min) | 9.4.7 | 13216-13231 |
| Sequence (size, isEmpty, includes, head) | 9.4.14 | 13316-13335 |
| Control (collect, select, reduce, forAll) | 9.4.17 | 13376-13395 |
| Boolean (not, xor, and, or) | 9.4.5 | 13188-13199 |
| String (concat, length, substring) | 9.4.6 | 13200-13215 |
| Base types (Anything, DataValue) | 9.2.2 | 8571-8788 |
| Scalar types (Boolean, Integer, Real) | 9.3.2 | 12486-12733 |
```

### Component 2: sysml-expert Agent

**File:** `claude/agents/sysml-expert.md`

**Purpose:** Expert on SysML v2 modeling constructs, patterns, requirements, and specification lookups.

**Corpus:**
- `{SYSML_DOCS_PATH}/SysML_Spec_v2_Part1/` (language constructs - when available)
- `{SYSML_DOCS_PATH}/SysML_Spec_v2_Part2/INDEX.md` + `full_document.md`
- `{SYSML_DOCS_PATH}/SysML_Spec_v2_Part3/INDEX.md` + `full_document.md`
- `{SYSML_DOCS_PATH}/SysML_IntroGuide_v2/full_document.md`
- `{SYSML_DOCS_PATH}/Cheatsheet/`

**Frontmatter:**
```yaml
---
name: sysml-expert
description: SysML v2 modeling expert. Use for modeling patterns, part/attribute/port definitions, requirements modeling, constraint patterns, connections, actions, state machines, and SysML specification lookups. Has access to SysML Parts 1-3 specs with INDEX.md navigation.
tools: Read, Grep, Glob
---
```

**System Prompt Structure:**

1. **Role Statement**: SysML v2 modeling specialist
2. **Documentation Structure**:
   - Part 1: Language constructs (not yet indexed)
   - Part 2: v1→v2 mappings (32k lines, INDEX.md available)
   - Part 3: API and Services (2k lines, INDEX.md available)
   - IntroGuide: Examples and tutorials
   - Cheatsheet: Quick syntax reference
3. **Search Strategy**:
   - Phase 1: Read INDEX.md files for relevant sections
   - Phase 2: Targeted reading with offset/limit
   - Phase 3: Cross-reference with IntroGuide for examples
4. **Key Section Reference**:
   - Part 2 Section 7.8: SysML stereotype mappings (requirements, blocks, ports)
   - Part 3 Section 7: API data model
5. **Response Format**: Overview, patterns with examples, citations
6. **Critical Rule**: NEVER say "X doesn't exist" - acknowledge corpus limitations

### Component 3: syside-expert Agent

**File:** `claude/agents/syside-expert.md`

**Purpose:** Expert on syside Python library, parser usage, expression evaluation, and automator workflows.

**Corpus:**
- `{SYSIDE_DOCS_PATH}/api/` (API reference)
- `{SYSIDE_DOCS_PATH}/automator/` (automator/execution docs)
- `{SYSIDE_DOCS_PATH}/examples/` (usage examples)

**Frontmatter:**
```yaml
---
name: syside-expert
description: SysIDE tooling expert. Use for parser usage, expression evaluation, automator workflows, syside Python API, model loading/querying, and tooling integration questions. Has access to syside documentation.
tools: Read, Grep, Glob
---
```

**System Prompt Structure:**

1. **Role Statement**: syside library and tooling specialist
2. **Documentation Structure**:
   - `api/README.md`: Overview and getting started
   - `api/generated/syside.*.md`: Class/function reference
   - `automator/advanced.md`: Expression evaluation, execution
3. **Search Strategy** (grep-based, no INDEX.md):
   - Phase 1: Grep across api/ directory for keywords
   - Phase 2: Read specific `.md` files found
   - Phase 3: Check automator/ for execution-related queries
4. **Common Query Patterns**:
   - Model loading → `syside.Model`, `syside.Document`
   - Expression evaluation → `automator/advanced.md`
   - Element querying → `syside.ElementAccessor`, `syside.MemberAccessor`
5. **Response Format**: Code examples with API references
6. **Critical Rule**: Distinguish syside API from SysML language syntax

### Component 4: sysmlv2-validator Agent

**File:** `claude/agents/sysmlv2-validator.md`

**Purpose:** Validate, analyze, and inspect SysML v2 models using the syside Python API. This agent goes far beyond simple syntax checking - it can load models, query the AST, evaluate expressions, check type conformance, and provide deep model insights.

**Tools:** `Bash`, `Write`, `Read`

**Frontmatter:**
```yaml
---
name: sysmlv2-validator
description: SysML v2 model validator and inspector. Use to validate syntax, debug errors, inspect model structure, query element types, evaluate expressions, and analyze type conformance. Can write Python scripts using the syside API for deep model analysis.
tools: Bash, Write, Read
---
```

**System Prompt Structure:**

#### 1. Role Statement

You are a SysML v2 model validator and inspector with access to the syside Python API. You can:
- Validate syntax using `syside check` (quick) or by loading models programmatically
- Load and query models to inspect their structure
- Traverse ownership trees and find elements by type
- Check type conformance and specialization hierarchies
- Evaluate expressions at compile time
- Pretty-print elements back to canonical textual syntax

#### 2. Capability Tiers

**Tier 1: Quick Validation** (CLI-based)
For simple "does this parse?" questions, use the CLI:
```bash
uv run syside check /path/to/model.sysml 2>&1
```

**Tier 2: Model Inspection** (Python scripts)
For deeper analysis, write Python scripts using the syside API.

**Tier 3: Expression Evaluation** (Python + Compiler)
For evaluating expressions or checking computed values.

#### 3. syside Python API Reference

**Loading Models:**
```python
import syside

# Load model - raises on errors
model, diagnostics = syside.load_model(["/path/to/model.sysml"])

# Load model - tolerates errors (useful for partial analysis)
model, diagnostics = syside.try_load_model(["/path/to/model.sysml"])

# Check for errors
if diagnostics.contains_errors():
    print(diagnostics)
```

**Querying Elements:**
```python
# Get all parts in the model
for part in model.nodes(syside.PartUsage, include_subtypes=True):
    print(f"Part: {part.name}")

# Get all constraints
for constraint in model.nodes(syside.ConstraintUsage, include_subtypes=True):
    print(f"Constraint: {constraint.name}")

# Get all requirements
for req in model.nodes(syside.RequirementUsage, include_subtypes=True):
    print(f"Requirement: {req.name}")
```

**Traversing Ownership:**
```python
def walk_tree(element, level=0):
    indent = "  " * level
    print(f"{indent}{element.name or 'anonymous'} ({type(element).__name__})")
    for owned in element.owned_elements:
        walk_tree(owned, level + 1)

# For each user document
for doc in model.user_docs:
    with doc.lock() as locked:
        walk_tree(locked.root_node)
```

**Checking Type Hierarchy:**
```python
# Check what a part specializes
for part in model.nodes(syside.PartUsage):
    for elem in part.heritage.elements:
        if def_ := elem.try_cast(syside.PartDefinition):
            print(f"{part.name} is typed by {def_.declared_name}")
```

**Evaluating Expressions:**
```python
compiler = syside.Compiler()

# Find an expression and evaluate it
for expr in model.nodes(syside.Expression, include_subtypes=True):
    result, report = compiler.evaluate(expr, stdlib=model.lib)
    if report:
        print(f"Expression evaluates to: {result}")
    else:
        print(f"Evaluation failed: {report.diagnostics}")
```

**Pretty-Printing Elements:**
```python
# Print an element back to textual syntax
element_text = syside.pprint(element)
print(element_text)
```

#### 4. Analysis Script Templates

**Template: Model Structure Analysis**
```python
#!/usr/bin/env python3
"""Analyze model structure and report summary."""
import syside
import sys

def analyze_model(path):
    model, diagnostics = syside.try_load_model([path])

    # Report errors/warnings
    if diagnostics.contains_errors():
        print("=== ERRORS ===")
        print(diagnostics)
        return

    # Count element types
    part_count = sum(1 for _ in model.nodes(syside.PartUsage, include_subtypes=True))
    attr_count = sum(1 for _ in model.nodes(syside.AttributeUsage, include_subtypes=True))
    port_count = sum(1 for _ in model.nodes(syside.PortUsage, include_subtypes=True))
    conn_count = sum(1 for _ in model.nodes(syside.ConnectionUsage, include_subtypes=True))
    req_count = sum(1 for _ in model.nodes(syside.RequirementUsage, include_subtypes=True))

    print(f"=== MODEL SUMMARY ===")
    print(f"Parts: {part_count}")
    print(f"Attributes: {attr_count}")
    print(f"Ports: {port_count}")
    print(f"Connections: {conn_count}")
    print(f"Requirements: {req_count}")

    # List part definitions
    print(f"\n=== PART DEFINITIONS ===")
    for def_ in model.nodes(syside.PartDefinition, include_subtypes=True):
        print(f"  - {def_.declared_name or def_.name or 'anonymous'}")

if __name__ == "__main__":
    analyze_model(sys.argv[1])
```

**Template: Find Elements by Type**
```python
#!/usr/bin/env python3
"""Find all elements of a specific type."""
import syside
import sys

def find_elements(path, element_type_name):
    model, diagnostics = syside.try_load_model([path])

    # Map type name to syside class
    type_map = {
        "part": syside.PartUsage,
        "partdef": syside.PartDefinition,
        "attribute": syside.AttributeUsage,
        "port": syside.PortUsage,
        "connection": syside.ConnectionUsage,
        "requirement": syside.RequirementUsage,
        "constraint": syside.ConstraintUsage,
        "action": syside.ActionUsage,
        "state": syside.StateUsage,
    }

    element_type = type_map.get(element_type_name.lower())
    if not element_type:
        print(f"Unknown type: {element_type_name}")
        print(f"Available: {list(type_map.keys())}")
        return

    print(f"=== {element_type_name.upper()} ELEMENTS ===")
    for elem in model.nodes(element_type, include_subtypes=True):
        name = elem.declared_name or elem.name or "anonymous"
        print(f"  - {name}")
        # Show typing if available
        if hasattr(elem, 'heritage'):
            for h in elem.heritage.elements:
                if h.declared_name:
                    print(f"      typed by: {h.declared_name}")

if __name__ == "__main__":
    find_elements(sys.argv[1], sys.argv[2])
```

**Template: Type Conformance Check**
```python
#!/usr/bin/env python3
"""Check for type conformance issues."""
import syside
import sys

def check_types(path):
    model, diagnostics = syside.try_load_model([path])

    # Type errors show up in diagnostics
    print("=== TYPE CHECKING RESULTS ===")

    type_errors = [d for d in diagnostics if "type-error" in str(d)]
    if type_errors:
        print(f"Found {len(type_errors)} type errors:")
        for err in type_errors:
            print(f"  {err}")
    else:
        print("No type errors found.")

    # Also show warnings
    warnings = [d for d in diagnostics if d.severity == syside.DiagnosticSeverity.Warning]
    if warnings:
        print(f"\n=== WARNINGS ({len(warnings)}) ===")
        for w in warnings:
            print(f"  {w}")

if __name__ == "__main__":
    check_types(sys.argv[1])
```

#### 5. Workflow Patterns

**Pattern A: Quick Syntax Check**
1. Write model to temp file (if snippet)
2. Run `uv run syside check <file>`
3. Report results
4. Cleanup temp file

**Pattern B: Deep Model Analysis**
1. Write analysis Python script to temp file
2. Run `uv run python <script> <model_path>`
3. Parse and report results
4. Cleanup script

**Pattern C: Expression Evaluation**
1. Write evaluation script targeting specific expressions
2. Run script with model path
3. Report computed values or evaluation errors

**Pattern D: "Why doesn't this work?" Investigation**
1. First run quick validation to get error messages
2. If errors are unclear, write inspection script to:
   - Check what types are defined
   - Verify import visibility
   - Trace specialization chains
3. Report findings with specific fixes

#### 6. Response Format

For validation requests:
```markdown
## Validation Result: [PASS/FAIL/PARTIAL]

**Diagnostics:**
[Error/warning messages with line numbers]

**Analysis:**
[What the errors mean in context]

**Model Insights:** (if deep analysis was performed)
- Elements found: [count by type]
- Type hierarchy issues: [if any]
- Unresolved references: [if any]

**Suggested Fixes:**
[Specific code changes with examples]

**Next Steps:**
[Recommendations for further investigation if needed]
```

#### 7. Key Principles

1. **Always validate before guessing** - Run actual parser, don't assume
2. **Use the right tier** - Quick check for simple questions, scripts for deep analysis
3. **Preserve context** - When writing scripts, include model path handling
4. **Clean up** - Remove temp files after use
5. **Explain diagnostics** - Don't just dump error output; interpret it
6. **Suggest specific fixes** - Include complete import statements, corrected syntax
7. **Know your limits** - Some issues require domain knowledge; recommend spawning kerml-expert or sysml-expert when appropriate

---

## Task-Model Command Updates

### Files to Update

1. `claude/commands/design-model.md`
2. `claude/commands/implement-model.md`
3. `claude/commands/plan-model.md`
4. `claude/commands/spec-model.md`

### Update Pattern

Replace references to `sysmlv2-doc-analyzer` with specialized agents and demonstrate parallel spawning:

**Before:**
```python
Task(
    description="Find modeling pattern",
    prompt="How do I model X?",
    subagent_type="sysmlv2-doc-analyzer"
)
```

**After:**
```python
# Spawn multiple agents in parallel for comprehensive research
Task(
    description="Find function definition",
    prompt="What is the signature of sum and how do I import it?",
    subagent_type="kerml-expert"
)
Task(
    description="Find usage pattern",
    prompt="Show examples of using aggregate functions in part definitions",
    subagent_type="sysml-expert"
)
```

### Guidance for Command Authors

Add section to each command explaining when to use which agent:

```markdown
## Documentation Agent Selection

| Question Type | Agent | Example |
|--------------|-------|---------|
| Standard library functions | `kerml-expert` | "What's the signature of sum?" |
| Modeling patterns | `sysml-expert` | "How do I model requirements?" |
| Parser/tooling | `syside-expert` | "How do I evaluate expressions?" |
| Syntax validation | `sysmlv2-validator` | "Does this code parse?" |

**For comprehensive answers, spawn multiple agents in parallel:**
- Cross-cutting questions (function + usage pattern) → kerml + sysml experts
- "Why doesn't this work?" → validator + relevant expert
```

---

## Implementation Order

1. **Create agent files** (in order of independence):
   1. `kerml-expert.md` - straightforward INDEX.md-based agent
   2. `sysml-expert.md` - similar pattern, multiple sources
   3. `syside-expert.md` - grep-based, different pattern
   4. `sysmlv2-validator.md` - unique pattern with Bash tools

2. **Deprecate old agent**:
   - Create `claude/agents/deprecated/` directory
   - Move `sysmlv2-doc-analyzer.md` with deprecation notice

3. **Update task-model commands**:
   - Add agent selection guidance
   - Update example Task calls

4. **Update CLI registration** (if needed):
   - Check `MBSE_AGENTS` list in `cli/__init__.py`
   - Add new agents, handle deprecated agent

---

## Potential Risks

| Risk | Mitigation |
|------|------------|
| Users confused by 4 agents vs 1 | Clear descriptions, task-model commands show which to use |
| Validator temp files left behind | Always cleanup in agent workflow, use timestamped names |
| INDEX.md line numbers drift | Checksums in INDEX.md metadata enable regeneration detection |
| syside CLI not available | Agent checks for command availability, suggests install |

---

## Validation Approach

### Agent Quality Testing

For each agent, test with queries from spec acceptance criteria:

1. **kerml-expert**: "What functions are in NumericalFunctions?" → Should find via section 9.4.7
2. **sysml-expert**: "How do I model a requirement constraint?" → Should find in Part 2
3. **syside-expert**: "How do I use automator to evaluate expressions?" → Should find advanced.md
4. **sysmlv2-validator**: Multiple capability tests:
   - **Tier 1 test**: Validate snippet with missing import → Quick CLI check, suggest fix
   - **Tier 2 test**: "List all parts in this model" → Write Python script, query AST
   - **Tier 3 test**: "What does this constraint evaluate to?" → Write expression evaluation script

### Integration Testing

1. Spawn kerml-expert + sysml-expert in parallel for cross-cutting question
2. Use validator to inspect model structure, then kerml-expert for function docs
3. Full workflow through task-model command with validation + deep analysis

---

**Next Step:** After approval → `/_my_implement` to create the agent files

