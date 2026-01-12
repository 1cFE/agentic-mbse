# EPIC-DOC-001: Documentation Discoverability Overhaul

**Priority**: P0 (Critical - User-facing failure)
**Total Effort**: ~3-5 days
**Status**: Ready
**Created**: 2026-01-12
**Research**: `.project/research/20260112-064217_sysmlv2-agent-discoverability-failure.md`

---

## Problem Statement

Our sysmlv2-doc-analyzer agent consistently fails to help users discover standard library functions like `NumericalFunctions::sum`. A team using our toolkit spent **hours** trying to find a basic function that existed all along. This happened because:

1. **Missing documentation**: We never extracted the KerML spec (which defines the standard library) from PDF
2. **No library index**: Standard library functions exist only in `.kerml` files buried in syside's package, invisible to agents
3. **Wrong agent strategy**: Agent confidently says "doesn't exist" when it simply can't find something in its corpus
4. **No validation fallback**: No agent can run `syside check` to test if code actually works

This is a product-blocking issue. If users can't discover capabilities, we don't have a useful product.

---

## Success Criteria

1. Agent can correctly answer "How do I sum values over a collection?" with `NumericalFunctions::sum` and import syntax
2. All critical SysML v2 specs (including KerML and Part1) are extracted and indexed
3. Standard library functions are documented in a greppable quick reference
4. Agent never says "doesn't exist" - only "couldn't find in my documentation"
5. Optional: Validation agent can test snippets with `syside check`

---

## Items

### P0-1: Extract Missing PDF Specifications
**Effort**: 2-4 hours
**Dependencies**: None

The following critical PDFs were never extracted to markdown:

| PDF | Location | Priority | Notes |
|-----|----------|----------|-------|
| `SysML_KerMLSpec.pdf` | `/home/reid/fusion_modeling/agent_literature/SysML/` | **Critical** | Defines standard library |
| `SysML_Spec_v2_Part1.pdf` | `/home/reid/fusion_modeling/agent_literature/SysML/` | **Critical** | Main language spec |
| `MBSE_20_TowardMoreIntegratedIntelligentMBSE.pdf` | `/home/reid/fusion_modeling/agent_literature/SysML/` | Medium | Conceptual |
| `PySysML Project Report Final.pdf` | `/home/reid/fusion_modeling/agent_literature/SysML/` | Low | Reference impl |

**Process**:
```bash
# Use m-scout pdf-processing tools
cd /home/reid/m-scout/tools/pdf-processing

# Process KerML spec (most critical)
python processors/pdf_process.py /home/reid/fusion_modeling/agent_literature/SysML/SysML_KerMLSpec.pdf

# Process Part1 spec
python processors/pdf_process.py /home/reid/fusion_modeling/agent_literature/SysML/SysML_Spec_v2_Part1.pdf
```

**Output**:
- `/home/reid/fusion_modeling/agent_literature/SysML/SysML_KerMLSpec/full_document.md`
- `/home/reid/fusion_modeling/agent_literature/SysML/SysML_Spec_v2_Part1/full_document.md`

**Then copy to agentic-mbse docs**:
```bash
cp -r /home/reid/fusion_modeling/agent_literature/SysML/SysML_KerMLSpec \
      /home/reid/1cfe/agentic-mbse/docs/sysmlv2/

cp -r /home/reid/fusion_modeling/agent_literature/SysML/SysML_Spec_v2_Part1 \
      /home/reid/1cfe/agentic-mbse/docs/sysmlv2/
```

**Acceptance Criteria**:
- [ ] KerML spec extracted to markdown
- [ ] Part1 spec extracted to markdown
- [ ] Both copied to `agentic-mbse/docs/sysmlv2/`
- [ ] Agent can grep for "NumericalFunctions" in the KerML spec

---

### P0-2: Create Standard Library Quick Reference
**Effort**: 2-3 hours
**Dependencies**: None (can be done from .kerml files directly)

Create `docs/sysmlv2/STANDARD_LIBRARY_REFERENCE.md` with:

1. **Table of all function packages** with descriptions
2. **Function signatures** for each package (NumericalFunctions, SequenceFunctions, ControlFunctions, etc.)
3. **Import examples** for common use cases
4. **Common patterns** (cost rollup, collection filtering, etc.)

**Source files** (authoritative definitions):
```
.venv/lib/python3.12/site-packages/syside/sysml.library/
├── Kernel Libraries/
│   ├── Kernel Function Library/
│   │   ├── NumericalFunctions.kerml    # sum, product, abs, max, min
│   │   ├── SequenceFunctions.kerml     # size, isEmpty, includes, head, tail
│   │   ├── ControlFunctions.kerml      # collect, select, reduce, forAll, exists
│   │   ├── CollectionFunctions.kerml   # array indexing
│   │   ├── StringFunctions.kerml       # Length, Substring
│   │   └── ... (17 files total)
│   ├── Kernel Data Type Library/
│   │   ├── ScalarValues.kerml          # Boolean, Integer, Real, String
│   │   ├── Collections.kerml           # Array, etc.
│   │   └── ...
│   └── Kernel Semantic Library/
│       └── ...
└── Domain Libraries/
    ├── Quantities and Units/           # ISQ, SI units
    └── ...
```

**Template structure**:
```markdown
# SysML v2 Standard Library Quick Reference

> Auto-generated from KerML standard library files. Last updated: [DATE]

## Numerical Functions

**Package**: `NumericalFunctions`
**Import**: `private import NumericalFunctions::*;`

| Function | Signature | Description |
|----------|-----------|-------------|
| `sum` | `sum(collection: NumericalValue[*]) → NumericalValue` | Sum all values in collection |
| `product` | `product(collection: NumericalValue[*]) → NumericalValue` | Multiply all values |
| `abs` | `abs(x: NumericalValue) → NumericalValue` | Absolute value |
| `max` | `max(x, y: NumericalValue) → NumericalValue` | Maximum of two values |
| `min` | `min(x, y: NumericalValue) → NumericalValue` | Minimum of two values |

**Example - Cost Rollup**:
```sysml
package CostExample {
    private import NumericalFunctions::sum;
    private import ISQ::*;

    part def Component {
        attribute cost : Real;
    }

    part def Assembly {
        part components : Component[*];
        attribute totalCost : Real = sum(components.cost);
    }
}
```

## Sequence Functions
...
```

**Acceptance Criteria**:
- [ ] Reference file created at `docs/sysmlv2/STANDARD_LIBRARY_REFERENCE.md`
- [ ] All 17 Kernel Function Library packages documented
- [ ] Each function has signature and one-line description
- [ ] Import patterns shown for each package
- [ ] At least 3 practical examples included

---

### P0-3: Update Agent System Prompt
**Effort**: 1 hour
**Dependencies**: P0-2

Update `claude/agents/sysmlv2-doc-analyzer.md` to:

1. **Check quick reference FIRST** for function/library queries
2. **Never say "doesn't exist"** - say "I couldn't find this in my documentation"
3. **Include import troubleshooting** guidance
4. **Add search paths** for new documentation

**Changes to make**:

```markdown
## Documentation Structure (UPDATED)

You have access to:
- **Standard Library Reference**: `{SYSML_DOCS_PATH}/STANDARD_LIBRARY_REFERENCE.md` ← CHECK FIRST for function queries
- **KerML Specification**: `{SYSML_DOCS_PATH}/SysML_KerMLSpec/full_document.md` ← Standard library definitions
- **SysML Specifications**: `{SYSML_DOCS_PATH}/*/full_document.md`
- **Syside Python API**: `{SYSIDE_DOCS_PATH}/api/`

## Search Strategy (UPDATED)

### For Function/Library Questions

When user asks about functions (sum, size, collect, etc.) or imports:

1. **FIRST**: Check `STANDARD_LIBRARY_REFERENCE.md` - it has all function signatures
2. **SECOND**: Search KerML spec for detailed semantics
3. **THIRD**: Search other specs for usage examples

### CRITICAL: Never Claim Something Doesn't Exist

If you cannot find something in documentation:
- SAY: "I couldn't find [X] in my documentation corpus"
- DO NOT SAY: "[X] doesn't exist in SysML v2"

### Import Error Troubleshooting

If user reports "No Type named 'X' found":
1. This usually means X needs to be imported
2. Check STANDARD_LIBRARY_REFERENCE.md for which package contains X
3. Suggest: `private import PackageName::X;`

Common packages:
- Math functions → `NumericalFunctions`
- Collection ops → `SequenceFunctions`
- Higher-order → `ControlFunctions`
- Units → `SI`, `ISQ`
```

**Acceptance Criteria**:
- [ ] Agent prompt updated with new search strategy
- [ ] "Never claim doesn't exist" rule added
- [ ] Import troubleshooting section added
- [ ] New documentation paths added

---

### P1-1: Generate Library Index Automatically
**Effort**: 4-6 hours
**Dependencies**: P0-2

Create script to auto-generate `STANDARD_LIBRARY_REFERENCE.md` from `.kerml` files:

**Location**: `scripts/generate_library_reference.py`

**Features**:
1. Parse all `.kerml` files in syside library
2. Extract function signatures, doc comments
3. Generate markdown tables
4. Update on each release

**Basic algorithm**:
```python
def extract_functions_from_kerml(file_path: Path) -> List[FunctionDef]:
    """Parse .kerml file and extract function definitions"""
    content = file_path.read_text()
    functions = []

    # Pattern for function definitions
    # abstract function sum { in collection: NumericalValue[0..*]; return : NumericalValue[1]; }
    pattern = r'(abstract\s+)?function\s+(\S+)\s*\{([^}]+)\}'

    for match in re.finditer(pattern, content):
        is_abstract = bool(match.group(1))
        name = match.group(2)
        body = match.group(3)

        # Extract parameters and return type
        params = extract_params(body)
        return_type = extract_return(body)

        functions.append(FunctionDef(
            name=name,
            params=params,
            return_type=return_type,
            is_abstract=is_abstract
        ))

    return functions
```

**Acceptance Criteria**:
- [ ] Script can parse all 17 Kernel Function Library files
- [ ] Generates valid markdown table for each package
- [ ] Includes doc comments where available
- [ ] Can be run as CI step or pre-release task

---

### P1-2: Add Validation Agent
**Effort**: 3-4 hours
**Dependencies**: None

Create new agent `claude/agents/sysmlv2-validator.md`:

**Purpose**: Test SysML v2 code snippets with `syside check` to verify syntax

**Agent Definition**:
```markdown
---
name: sysmlv2-validator
description: Test SysML v2 code snippets for validity. Use when user asks "does this work?" or reports syntax errors.
tools: Bash, Write, Read
---

You validate SysML v2 syntax by running syside check on code snippets.

## Process

1. Write the snippet to a temp file: `/tmp/sysml_test_<timestamp>.sysml`
2. Run: `uv run syside check <file>`
3. Interpret the results:
   - If success: Report "Syntax valid"
   - If "No Type named X found": Suggest likely import
   - If other error: Explain and suggest fix

## Import Suggestions

When you see "No Type named X found", check these packages:
- sum, product, abs, max, min → NumericalFunctions
- size, isEmpty, includes → SequenceFunctions
- collect, select, reduce → ControlFunctions
- Real, Integer, Boolean → ScalarValues

## Example Response

"The error 'No Type named sum found' means you need to import the sum function:

```sysml
private import NumericalFunctions::sum;
```

Let me test the corrected version..."
```

**Acceptance Criteria**:
- [ ] Agent can write temp files and run syside check
- [ ] Agent correctly interprets common error messages
- [ ] Agent suggests imports for "No Type named X" errors
- [ ] Agent cleans up temp files

---

### P1-3: Add Kernel Library Files to Searchable Corpus
**Effort**: 2-3 hours
**Dependencies**: None

Option A: Copy `.kerml` files to docs directory
```bash
mkdir -p docs/sysmlv2/kernel_library
cp -r .venv/lib/python3.12/site-packages/syside/sysml.library/Kernel\ Libraries/* \
      docs/sysmlv2/kernel_library/
```

Option B: Add dynamic search path in agent configuration

**Acceptance Criteria**:
- [ ] Agent can grep for function names in .kerml source files
- [ ] When agent searches for "sum", it finds NumericalFunctions.kerml
- [ ] Kernel library files are versioned/tracked appropriately

---

### P2-1: Split Agent into Specialists
**Effort**: 1-2 days
**Dependencies**: P0-1, P0-2, P1-2

Current single agent handles too many different query types. Split into:

| Agent | Purpose | Corpus |
|-------|---------|--------|
| `sysmlv2-concepts` | Language semantics, modeling patterns | Specs, guides |
| `sysmlv2-library` | Standard library lookup | .kerml files, quick ref |
| `sysmlv2-validator` | Syntax validation | syside CLI |
| `sysmlv2-examples` | Working code examples | Test files |

**Routing logic** (in main agent or triage):
- "How do I use X?" → sysmlv2-library
- "What is X?" → sysmlv2-concepts
- "Does this work?" → sysmlv2-validator
- "Show me an example of X" → sysmlv2-examples

**Acceptance Criteria**:
- [ ] At least 2 specialized agents created
- [ ] Each agent has focused, smaller corpus
- [ ] Queries route to appropriate specialist
- [ ] Overall answer quality improves

---

### P2-2: Improve PDF Chunking with Headers
**Effort**: 4-6 hours
**Dependencies**: P0-1

The m-scout pdf-processing tools support hierarchical chunking. Improve our doc extraction:

**Location**: `/home/reid/m-scout/tools/pdf-processing/`

**Goals**:
1. Extract with section headers preserved
2. Create index of sections for faster grep
3. Enable offset-based reading of specific sections

**Process**:
```bash
# Reprocess with chunking enabled
cd /home/reid/m-scout/tools/pdf-processing
python processors/pdf_process.py --force \
    /home/reid/fusion_modeling/agent_literature/SysML/SysML_KerMLSpec.pdf
```

**Output structure**:
```
SysML_KerMLSpec/
├── full_document.md        # Complete document
├── section_index.json      # Section → line number mapping
├── chunks/
│   ├── 001_introduction.md
│   ├── 002_kernel_libraries.md
│   ├── 003_standard_library.md
│   └── ...
└── summary.json            # Processing metadata
```

**Acceptance Criteria**:
- [ ] Documents chunked by section
- [ ] Section index JSON created
- [ ] Agent can read specific sections efficiently

---

### P3-1: Create Documentation Dashboard
**Effort**: 1 day
**Dependencies**: P1-1

Script to audit documentation coverage:

**Output**: `docs/COVERAGE_REPORT.md`

```markdown
# Documentation Coverage Report

Generated: 2026-01-12

## SysML v2 Specifications

| Document | Status | Lines | Last Updated |
|----------|--------|-------|--------------|
| KerML Spec | Extracted | 15,234 | 2026-01-12 |
| Part 1 | Extracted | 22,456 | 2026-01-12 |
| Part 2 | Extracted | 32,375 | 2024-11-08 |
| Part 3 | Extracted | 1,999 | 2024-11-08 |
| IntroGuide | Extracted | 481 | 2024-11-08 |

## Standard Library Coverage

| Package | Functions | Documented | Missing |
|---------|-----------|------------|---------|
| NumericalFunctions | 14 | 14 | 0 |
| SequenceFunctions | 23 | 23 | 0 |
| ControlFunctions | 15 | 15 | 0 |
...

## Agent Corpus Gaps

- [ ] No examples for `reduce` function
- [ ] Missing domain library docs (Quantities, Units)
```

**Acceptance Criteria**:
- [ ] Script audits all expected documentation
- [ ] Report shows gaps clearly
- [ ] Can be run in CI to catch regressions

---

## Implementation Order

```
Week 1 (Critical Path):
├── P0-1: Extract missing PDFs (2-4 hours)
├── P0-2: Create quick reference (2-3 hours)
└── P0-3: Update agent prompt (1 hour)
    └── [Milestone: Agent can answer "how do I use sum?"]

Week 1-2 (Stabilization):
├── P1-1: Auto-generate library index (4-6 hours)
├── P1-2: Add validation agent (3-4 hours)
└── P1-3: Add .kerml to corpus (2-3 hours)
    └── [Milestone: Self-healing documentation pipeline]

Week 2+ (Enhancement):
├── P2-1: Split into specialist agents (1-2 days)
├── P2-2: Improve PDF chunking (4-6 hours)
└── P3-1: Documentation dashboard (1 day)
    └── [Milestone: Production-ready documentation system]
```

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| PDF extraction fails | High | Use PyMuPDF fallback, manual cleanup |
| .kerml files change on syside update | Medium | Pin syside version, regenerate on update |
| Agent still hallucinates | Medium | Validation agent as safety net |
| Quick reference becomes stale | Low | Auto-generation script in CI |

---

## References

- Research: `.project/research/20260112-064217_sysmlv2-agent-discoverability-failure.md`
- External feedback: `/home/reid/1cfe/fusion-tea/project/research/20260112-061548_sysmlv2-discovery-reflection.md`
- PDF processing tools: `/home/reid/m-scout/tools/pdf-processing/`
- Source PDFs: `/home/reid/fusion_modeling/agent_literature/SysML/`
- Standard library source: `.venv/lib/python3.12/site-packages/syside/sysml.library/`
