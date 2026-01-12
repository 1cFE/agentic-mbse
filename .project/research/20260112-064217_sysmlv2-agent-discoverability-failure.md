---
date: 2026-01-12T06:42:17+00:00
researcher: Claude
topic: "SysMLv2 Agent Discoverability Failure Analysis"
tags: [research, agents, sysmlv2, documentation, discoverability, critical]
status: complete
last_updated: 2026-01-12
---

# Research: SysMLv2 Agent Discoverability Failure Analysis

**Date**: 2026-01-12
**Researcher**: Claude
**Research Type**: Agent/Documentation Analysis

## Research Question

Why did our sysmlv2-doc-analyzer agent fail to help users discover the `NumericalFunctions::sum` function, and what strategic improvements are needed to prevent this class of failure?

## Summary

- **Root Cause Confirmed**: Our sysmlv2-doc-analyzer agent's documentation corpus is fundamentally incomplete - it lacks the KerML standard library `.kerml` files that define `sum`, `product`, and other essential functions
- **Agent Testing Results**: 2 of 3 test queries failed completely; 1 succeeded only because it happened to search syside's automator docs which tangentially mention these functions
- **Documentation Gap**: The actual function definitions exist in `.venv/lib/python3.12/site-packages/syside/sysml.library/Kernel Libraries/Kernel Function Library/` but are NOT indexed or referenced in our agent's searchable documentation
- **Critical Finding**: The specs we have (Part2, Part3, IntroGuide) focus on language semantics and transformation mappings, NOT the standard library function reference
- **Strategic Issue**: Our agent architecture assumes "search documentation" is sufficient, but standard library discovery requires different indexing strategies

## Detailed Findings

### 1. What Documentation We Actually Have

**Source:** `docs/sysmlv2/` directory structure

| Document | Content | Library Coverage |
|----------|---------|------------------|
| `SysML_Spec_v2_Part2/full_document.md` | SysML v1 to v2 transformation mappings | None - focuses on metamodel |
| `SysML_Spec_v2_Part3/full_document.md` | API and Services specification | None - focuses on REST API |
| `SysML_IntroGuide_v2/full_document.md` | Introductory guide with examples | Mentions `size()` once (line 214), no `sum` |
| `SysML_HoltPerryConcepts_v20/full_document.md` | Conceptual overview | None |
| `Cheatsheet/sysml_textual_notation_cheatsheet.md` | Syntax reference | Import syntax only, no function list |

**Critical Gap**: No KerML specification document with standard library reference.

### 2. Where `sum` Actually Appears in Our Docs

**Source:** `grep -r "NumericalFunctions" docs/`

Only ONE file mentions `NumericalFunctions::sum`:

```
docs/syside/automator/advanced.md:102:  - `NumericalFunctions::sum`
```

This appears in the "Expression Evaluation" section describing what syside can evaluate, NOT as a user-facing function reference.

### 3. Agent Test Results

Three identical agents were spawned with different query formulations:

| Query | Result | Reason |
|-------|--------|--------|
| "Is there a sum() function?" | **Partial success** | Agent found the automator/advanced.md reference |
| "How do I import NumericalFunctions::sum?" | **FAILED** | Agent said "NumericalFunctions does not appear in documentation" |
| "What's in the Kernel Function Library?" | **FAILED** | Agent found only SequenceFunctions references, no numerical functions |

**Key Insight**: Success was random, depending on whether the agent's grep happened to search the syside docs directory.

### 4. The Authoritative Source (Not in Agent's Corpus)

The actual function definitions live in the syside package:

```
.venv/lib/python3.12/site-packages/syside/sysml.library/
└── Kernel Libraries/
    └── Kernel Function Library/
        ├── NumericalFunctions.kerml    <- sum, product, abs, max, min
        ├── SequenceFunctions.kerml     <- size, isEmpty, includes, etc.
        ├── ControlFunctions.kerml      <- collect, select, reduce, forAll
        ├── CollectionFunctions.kerml
        ├── StringFunctions.kerml
        └── ... (17 files total)
```

**Contents of NumericalFunctions.kerml** (the smoking gun):
```kerml
standard library package NumericalFunctions {
    abstract function sum { in collection: NumericalValue[0..*]; return : NumericalValue[1]; }
    abstract function product { in collection: NumericalValue[0..*]; return : NumericalValue[1]; }
    abstract function abs{ in x: NumericalValue[1]; return : NumericalValue[1]; }
    abstract function max specializes ScalarFunctions::max { ... }
    abstract function min specializes ScalarFunctions::min { ... }
    // ... plus arithmetic operators
}
```

This file EXISTS in our project's venv but is completely invisible to the agent.

### 5. The Agent's Configuration

**Source:** `claude/agents/sysmlv2-doc-analyzer.md`

The agent is configured to search:
- `{SYSML_DOCS_PATH}/*/full_document.md` - High-level specs
- `{SYSIDE_DOCS_PATH}/api/` - API documentation

Missing from search paths:
- Standard library `.kerml` files
- Any quick reference or index of available functions

## Architecture/Agent Insights

### Why This Failure Class is Critical

1. **Negative assertions are easy, positive discovery is hard**: When the agent can't find something, it confidently says "doesn't exist" rather than "I couldn't find it in my corpus"

2. **Import errors are misinterpreted**: When users see `No Type named 'sum' found`, both they AND the agent interpret this as "doesn't exist" rather than "not imported"

3. **Documentation structure mismatch**: Our docs explain WHAT things mean, not WHERE to find functions

4. **Single point of failure**: All SysML questions route to one agent that can only grep documentation it can see

### The User's Discovery Journey (Broken)

```
User wants: "sum values across parts"
    ↓
Tries: sum(parts.values)
    ↓
Gets: "No Type named 'sum' found"
    ↓
Asks agent: "Does sum exist?"
    ↓
Agent searches docs → finds nothing → "sum doesn't exist"
    ↓
User wastes hours trying workarounds
    ↓
Finally: User provides working example (if lucky)
```

## Recommendations

### TIER 1: Immediate Fixes (< 1 day effort)

#### 1.1 Create Standard Library Quick Reference

Create `docs/sysmlv2/STANDARD_LIBRARY_REFERENCE.md`:

```markdown
# SysML v2 Standard Library Quick Reference

## Numerical Functions (import from `NumericalFunctions`)

| Function | Signature | Description |
|----------|-----------|-------------|
| `sum` | `sum(collection: NumericalValue[*]) → NumericalValue` | Sum all values |
| `product` | `product(collection: NumericalValue[*]) → NumericalValue` | Multiply all values |
| `abs` | `abs(x: NumericalValue) → NumericalValue` | Absolute value |
| `max` | `max(x, y: NumericalValue) → NumericalValue` | Maximum of two |
| `min` | `min(x, y: NumericalValue) → NumericalValue` | Minimum of two |

**Import pattern:**
\`\`\`sysml
private import NumericalFunctions::sum;
// or import all:
private import NumericalFunctions::*;
\`\`\`

## Sequence Functions (import from `SequenceFunctions`)

| Function | Signature | Description |
|----------|-----------|-------------|
| `size` | `size(seq: Anything[*]) → Natural` | Count elements |
| `isEmpty` | `isEmpty(seq: Anything[*]) → Boolean` | Check if empty |
| `notEmpty` | `notEmpty(seq: Anything[*]) → Boolean` | Check if not empty |
| `includes` | `includes(seq, values) → Boolean` | Check if contains |
| `head` | `head(seq) → Anything[0..1]` | First element |
| `tail` | `tail(seq) → Anything[*]` | All but first |

## Control Functions (import from `ControlFunctions`)

| Function | Signature | Description |
|----------|-----------|-------------|
| `collect` | `seq->collect { mapper }` | Map over sequence |
| `select` | `seq->select { predicate }` | Filter sequence |
| `reduce` | `seq->reduce operator` | Fold sequence |
| `forAll` | `seq->forAll { test }` | All match predicate |
| `exists` | `seq->exists { test }` | Any match predicate |
```

#### 1.2 Update Agent System Prompt

Add to `sysmlv2-doc-analyzer.md`:

```markdown
## CRITICAL: Standard Library Searches

When users ask about functions (sum, size, collect, etc.):

1. **FIRST check** `{SYSML_DOCS_PATH}/STANDARD_LIBRARY_REFERENCE.md`
2. **If not found**, search the Kernel Function Library files
3. **NEVER say "doesn't exist"** - say "I couldn't find this in my documentation"

### Common Import Errors

If a user reports "No Type named 'X' found":
- This usually means X needs to be imported
- Check which package contains X in the quick reference
- Suggest: `private import PackageName::X;`
```

### TIER 2: Structural Improvements (1-3 day effort)

#### 2.1 Add `.kerml` Files to Agent Corpus

Option A: Copy library files into docs
```bash
cp -r .venv/.../syside/sysml.library/Kernel\ Libraries/ docs/sysmlv2/kernel_library/
```

Option B: Add search path to agent configuration
```markdown
- **Kernel Library Source**: `{VENV_PATH}/syside/sysml.library/Kernel Libraries/`
```

#### 2.2 Create Specialized "Library Lookup" Agent

New agent: `sysmlv2-library-lookup.md`

```markdown
---
name: sysmlv2-library-lookup
description: Find standard library functions in SysML v2. Use when user asks about functions like sum, size, collect, etc.
tools: Read, Grep, Glob
---

You search the KerML standard library files to find function signatures and usage patterns.

## Search Strategy

1. Grep the .kerml files for the function name
2. Return: package name, function signature, required import
3. Include working example if available
```

#### 2.3 Add Validation Agent

New agent: `sysmlv2-validator.md`

```markdown
---
name: sysmlv2-validator
description: Test SysML v2 code snippets with syside. Use to verify if syntax is valid.
tools: Bash, Write, Read
---

When asked to verify SysML syntax:
1. Write snippet to temp file
2. Run: uv run syside check <file>
3. Report results with interpretation
4. If "No Type named X", suggest likely imports
```

### TIER 3: Strategic Improvements (1+ week effort)

#### 3.1 Generate Comprehensive Index

Script to auto-generate library index:

```python
# scripts/generate_library_index.py
def extract_functions_from_kerml(file_path):
    """Parse .kerml file and extract function signatures"""
    # Return list of (name, signature, package, doc_comment)

def generate_markdown_reference():
    """Generate STANDARD_LIBRARY_REFERENCE.md from .kerml files"""
```

Run on each release to keep docs in sync.

#### 3.2 Split Agent Responsibilities

Current: One agent handles all SysMLv2 questions

Proposed:
| Agent | Responsibility | Corpus |
|-------|----------------|--------|
| `sysmlv2-concepts` | Language semantics, patterns | Specs, guides |
| `sysmlv2-library` | Standard library functions | .kerml files, quick ref |
| `sysmlv2-validator` | Syntax validation | syside CLI |
| `sysmlv2-examples` | Working code examples | Test files, examples |

#### 3.3 Error Message Enhancement

Hook into syside error messages to suggest fixes:

```python
# When "No Type named 'sum' found"
def suggest_import(error_msg):
    type_name = extract_type_from_error(error_msg)
    if type_name in KNOWN_FUNCTIONS:
        return f"Try: private import {KNOWN_FUNCTIONS[type_name]}::{type_name};"
```

## Open Questions

1. **Licensing**: Can we redistribute the .kerml files in our docs, or must they stay in syside package?

2. **Version sync**: How do we ensure our library reference stays in sync with syside updates?

3. **Agent routing**: Should we add a "triage" agent that routes to specialized agents, or keep one general agent with better prompting?

4. **Validation mandate**: Should we require all research reports about "X doesn't exist" to include validation test results?

## Implementation Priority

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| **P0** | Create STANDARD_LIBRARY_REFERENCE.md | 2 hours | Fixes immediate discovery problem |
| **P0** | Update agent prompt to check reference first | 30 min | Fixes agent behavior |
| **P1** | Add validation agent | 4 hours | Prevents false negatives |
| **P1** | Generate library index from .kerml | 1 day | Automation, sustainability |
| **P2** | Split into specialized agents | 2-3 days | Better accuracy, maintainability |
| **P3** | Error message enhancement | 1 week | Best UX, highest effort |

## Conclusion

The fusion-tea team's failure wasn't a documentation problem - it was an **indexing and discoverability problem**. Our agent has the right strategy (grep docs, read context, synthesize answer) but the wrong corpus (no standard library reference).

The fix is straightforward:
1. Create a human-readable standard library reference
2. Update the agent to check it first
3. Add validation as a failsafe

The deeper lesson: **Agents need different documentation structures than humans**. Humans can browse, scan, and infer. Agents need explicit, greppable indexes with exact function names and package locations.

---

**Prepared for**: agentic-mbse development team
**Action requested**: Implement P0 items immediately, schedule P1 for this week
