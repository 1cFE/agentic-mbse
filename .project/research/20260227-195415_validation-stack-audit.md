---
date: 2026-02-27T19:54:15Z
researcher: Claude Opus 4.6
topic: "Validation stack distinctness and accuracy audit"
tags: [research, validation, blog-accuracy]
status: complete
last_updated: 2026-02-27
---

# Research: Validation Stack Distinctness & Blog Accuracy Audit

**Date**: 2026-02-27T19:54:15Z
**Researcher**: Claude Opus 4.6
**Research Type**: Architecture / Codebase

## Research Question

Are the 8 validation levels distinct and meaningful? Does each catch errors the others don't? Is the blog post's 6-level description accurate?

## Summary

- **Levels 1, 2, 3, 6, and 8 are genuinely distinct** — each catches a class of error no other level detects
- **Levels 4 and 5 are stubs** — L4 counts constraints and always passes; L5's constraint coverage and unit consistency are unimplemented placeholders
- **Level 7 is real but vacuous without opt-in** — requires `manifest.yaml` files that most projects won't have; passes with a warning otherwise
- **The blog post overpromises on 3 of its 6 levels** — L3 (dataflow), L4 (constraints), and L5 (traceability) describe capabilities that don't exist in the implementation
- **Recommended: reduce to 4 honest levels for the blog**, with 2 more marked as roadmap/informational

## Detailed Findings

### Level-by-Level Implementation Audit

#### Level 1: Syntax Validation — REAL, DISTINCT
**File:** `level1_syntax.py` (118 lines)
**What it checks:** Parser errors via syside's `diagnostics.parser` collection. Counts errors and warnings from the SysML parser.
**Blog accuracy:** ✅ Accurate. "Does the SysML parse correctly?" is exactly what this does.
**Catches that no other level does:** Syntax errors (missing braces, invalid keywords, malformed expressions). No other level runs the parser diagnostics.
**Example fail→pass:**
- FAIL: `calc def MissingBrace in x : Real; }` — missing opening brace
- PASS: `calc def Calc { in x : Real; return y : Real; }`

#### Level 2: Structural Completeness — REAL, DISTINCT, MOST SUBSTANTIAL
**File:** `level2_structure.py` (442 lines) + `adr002.py` (511 lines)
**What it checks (6 sub-checks):**
1. Unused calc defs in `library/` (no corresponding CalculationUsage) → WARNING
2. Unbound calc inputs (input parameter with no binding and no default) → ERROR
3. Literal bindings (input bound to literal like `42.0` instead of attribute) → WARNING
4. Undefined bindings (input bound to attribute that has no value) → ERROR
5. ADR-002 V1: Calc defs in `designs/` instead of `library/` → ERROR
6. ADR-002 V2: Derived expressions in design files (feature references in attribute expressions) → ERROR
7. ADR-002 V4: Unsupported operators in static expressions → ERROR
8. Orphaned elements — **STUB** (returns empty list, line 321-335)

**Blog accuracy:** ✅ Mostly accurate. "Unused or unconnected definitions" describes checks 1-4 well. The ADR-002 checks (5-7) go further than described.
**Catches that no other level does:** Unbound inputs, undefined bindings, ADR-002 violations. These are all structural relationships requiring a parsed AST.
**Example fail→pass:**
- FAIL: `calc power : PowerCalc { /* p_input NOT bound */ }` — unbound input
- PASS: `calc power : PowerCalc { in p_input = system_power; }` — input bound

#### Level 3: Dataflow Integrity — REAL, DISTINCT, BUT NARROW
**File:** `level3_dataflow.py` (149 lines)
**What it checks:** Circular dependencies in the **package import** graph. Builds a graph of which documents import which packages (excluding `ScalarValues`, `SI`, `ISQ`), then calls `detect_cycles()`.
**Blog accuracy:** ⚠️ **Overpromises.** Blog says "Can values propagate through the model without loops or dead ends?" The implementation ONLY detects circular package imports. It does NOT check:
- Whether values can propagate (no dead-end detection)
- Whether binding chains terminate
- Whether calculation outputs flow to all consumers

The actual check is: "do any packages have circular import relationships?"

**Catches that no other level does:** Circular import cycles between packages. L2 doesn't build or analyze the import graph.
**Example fail→pass:**
- FAIL: `package Pkg1 { import Pkg2::*; }` + `package Pkg2 { import Pkg1::*; }` — circular import
- PASS: `package Pkg1 { import Pkg2::*; }` + `package Pkg2 { /* no import of Pkg1 */ }` — acyclic

**Note:** The test `test_circular_dependency_detected` (line 520-551) doesn't actually assert that the circular dependency is detected — it only checks `result.level == 3` and notes "May have issues if circular detection works." This suggests the test may not reliably exercise the cycle detection path.

#### Level 4: Constraint Satisfaction — STUB, NOT DISTINCT
**File:** `level4_constraints.py` (108 lines)
**What it checks:** Counts `ConstraintUsage` and `ConstraintDefinition` elements. Returns metrics. **Always returns `success=True`** (line 81).
**Blog accuracy:** ❌ **False.** Blog says "track the ratio of constrained to unconstrained parameters and flag models that fall below a threshold." The implementation:
- Does NOT track which parameters are constrained
- Does NOT compute a ratio
- Does NOT have a threshold
- Does NOT flag anything
- The `undocumented` list (line 74-76) is always empty (placeholder comment: "can enhance later")

**Catches that no other level does:** Nothing. No model can fail L4. It literally always passes.
**No fail→pass example is possible** — L4 cannot fail.

#### Level 5: Semantic Consistency — STUB, NOT DISTINCT
**File:** `level5_semantic.py` (170 lines)
**What it checks (nominally):**
1. `check_unit_consistency()` — **STUB** (returns empty list, lines 47-57: "Placeholder - needs full implementation")
2. `check_constraint_coverage()` — **STUB** (`constrained_attrs` is always empty set at line 77, so coverage is always 0%)

**Blog accuracy:** N/A — blog doesn't include this as a separate level (blog maps its "Level 5" to traceability). But the SKILL.md describes L5 as "Unit consistency, type matching" which is NOT implemented.
**Catches that no other level does:** Nothing currently. Unit consistency is stubbed. Constraint coverage is stubbed (hardcoded to report 0% but never fails on it).
**No fail→pass example is possible** — L5 always passes (only unit_issues cause failure, and `check_unit_consistency` always returns `[]`).

#### Level 6: Traceability & Documentation — REAL, DISTINCT, INFORMATIONAL ONLY
**File:** `level6_traceability.py` (154 lines)
**What it checks:** Whether `CalculationDefinition` and `PartDefinition` elements have `Comment` or `Documentation` owned elements. Reports missing docs as warnings. **Always returns `success=True`** (line 129).
**Blog accuracy:** ⚠️ **Overpromises.** Blog says "Every parameter value and assumption should trace to a source: a paper, a dataset, a domain expert's input." The implementation only checks for the *presence* of doc comments, NOT whether they contain source citations, paper references, or meaningful traceability content. A doc comment of `/* TODO */` would pass.
**Catches that no other level does:** Missing doc comments on definitions. No other level inspects documentation.
**Cannot fail but has meaningful warnings:**
- WARNING: `calc def UndocumentedCalc { ... }` — no doc comment
- No warning: `doc /* Source: Smith 2024 */ calc def DocumentedCalc { ... }` — has doc comment

#### Level 7: Architectural Integrity — REAL, DISTINCT, BUT OPT-IN
**File:** `level7_architecture.py` (171 lines)
**What it checks:** Loads `manifest.yaml` from `models/designs/*/` directories. If manifest has `expected_subsystems` list, checks that named parts exist as `PartUsage` elements. **Passes with warning if no manifest exists** (lines 101-118).
**Blog accuracy:** ⚠️ **Loosely accurate but vacuous.** Blog says "structural requirements for automated cost and performance analysis." L7 only checks manifest-declared subsystems, which is a very narrow definition of "architectural integrity."
**Catches that no other level does:** Missing expected subsystems when a manifest is present. But without manifests (the default), this catches nothing.
**Example fail→pass:**
- FAIL: `manifest.yaml` lists `expected_subsystems: [turbine, generator]` but model has no `part turbine`
- PASS: Add `part turbine` and `part generator` to the model

#### Level 8: Codegen Readiness — REAL, DISTINCT, MOST SOPHISTICATED
**File:** `level8_codegen.py` (610 lines)
**What it checks (5 sub-checks):**
1. Qualified names on calc defs and usages (non-empty, valid format, EQN-derivable)
2. Calc def structure (at least one output parameter with direction)
3. Binding format correctness (chain bindings use `.`, reference bindings use `::`)
4. Design attribute completeness (attributes in `designs/` have values)
5. Design attribute extractability (values can be evaluated to numeric defaults)

**Blog accuracy:** The blog doesn't have a direct L8 equivalent. Blog's "Level 6: Architecture" partially overlaps (codegen pipeline requirements).
**Catches that no other level does:** Qualified name validity, output parameter presence, binding format issues, expression extractability. All are codegen-specific concerns.
**Example fail→pass:**
- FAIL: `attribute area : Real = length * width;` in designs/ — expression has feature references, can't extract numeric default
- PASS: `attribute area : Real = 50.0;` — literal value, extractable

### Distinctness Matrix

| Level | Can Fail? | Unique Error Class | Distinct from All Others? |
|-------|-----------|-------------------|--------------------------|
| L1 | Yes | Syntax errors | ✅ Yes |
| L2 | Yes | Structural defects (unbound, unused, ADR-002) | ✅ Yes |
| L3 | Yes | Circular imports | ✅ Yes (narrow but distinct) |
| L4 | **No** | None (always passes) | ❌ No — stub |
| L5 | **No** | None (always passes) | ❌ No — stub |
| L6 | **No** | None (always passes, warnings only) | ⚠️ Partially — produces unique warnings but can't block |
| L7 | Yes* | Missing manifest subsystems (*requires manifest) | ⚠️ Conditionally — only with opt-in manifest |
| L8 | Yes | Codegen-specific issues | ✅ Yes |

### Blog Post vs Implementation Mapping

| Blog Level | Blog Description | Impl Level | Status |
|------------|-----------------|------------|--------|
| 1. Syntax | "Does it compile" | L1 | ✅ Accurate |
| 2. Structure | "Unused or unconnected definitions" | L2 | ✅ Accurate |
| 3. Dataflow | "Circular dependencies, dead ends, value propagation" | L3 | ⚠️ Overpromises — only circular imports |
| 4. Constraints | "Ratio of constrained to unconstrained, threshold" | L4+L5 | ❌ Not implemented — stubs |
| 5. Traceability | "Sources embedded in models" | L6 | ⚠️ Overpromises — only checks doc comment existence |
| 6. Architecture | "Structural requirements for TEA pipeline" | L7+L8 | ⚠️ L7 is opt-in; L8 is real but not described |

## Recommendations

### For the Blog Post

**Option A: Honest 4+2 (recommended)**

Describe 4 levels that genuinely work, plus 2 that are informational/roadmap:

```
We have built a multi-level hierarchy of automated model validation.
Four levels actively catch errors; two more provide informational metrics.

- **Level 1: Syntax.** Does the SysML parse correctly? This is the
  equivalent of "does it compile." If the model has syntax errors,
  nothing downstream matters.

- **Level 2: Structure.** Are there unused definitions, unbound
  calculation inputs, or architectural violations? This catches
  orphaned components, missing bindings, and violations of our
  calculation placement rules — issues where the model looks like
  SysML but wouldn't execute correctly.

- **Level 3: Dependencies.** Are there circular imports between
  packages? Circular dependencies prevent deterministic model loading
  and can cause subtle evaluation order bugs.

- **Level 4: Codegen Readiness.** Can the model actually feed our
  analysis pipeline? This checks that calculation definitions have
  proper outputs, that binding formats are correct, and that design
  parameter values can be extracted as numeric defaults. A model that
  passes Levels 1-3 but fails here would compile and look complete,
  but produce empty results when we try to run cost or performance
  analysis.

In addition, we run informational checks that don't block but guide
improvement:

- **Documentation coverage.** What fraction of definitions have doc
  comments? We track this to encourage source attribution.

- **Constraint coverage.** How many parameters have physical
  constraints? (This is a metric we track; automated constraint
  validation is on our roadmap.)
```

**Option B: Aspirational 6 with honest caveats**

Keep 6 levels but add "(in progress)" markers:

```
- Level 4: Constraints (metrics only — we track constraint counts
  but automated ratio/threshold checking is in progress)
- Level 5: Traceability (we check for doc comment presence; full
  source-citation validation is planned)
```

### For the Implementation — Concrete Test Plan

To demonstrate each level's distinctness, we should have **targeted SysML fixture files** where each file passes all levels except one:

#### Test: `test_distinctness_l1_only.sysml`
```sysml
// FAILS L1 only — syntax error, cannot parse
package Broken {
    calc def MissingBrace
        in x : Real;
    }
}
```

#### Test: `test_distinctness_l2_only.sysml` (two files)
```sysml
// File 1: library/calc.sysml — valid syntax
package Library {
    calc def PowerCalc {
        in power_in : Real;
        return power_out : Real;
    }
}

// File 2: designs/design.sysml — valid syntax, but unbound input
package Design {
    private import Library::PowerCalc;
    part system {
        calc power : PowerCalc {
            // p_input deliberately NOT bound — L2 should catch
        }
    }
}
```
**Expected:** L1 PASS, L2 FAIL (unbound input), L3 PASS

#### Test: `test_distinctness_l3_only.sysml` (two files)
```sysml
// File 1: valid structure, no unbound inputs
package Pkg1 {
    import Pkg2::*;
    part def A { attribute x : Real; }
}

// File 2: creates circular import
package Pkg2 {
    import Pkg1::*;
    part def B { attribute y : Real; }
}
```
**Expected:** L1 PASS, L2 PASS, L3 FAIL (circular import)

#### Test: `test_distinctness_l8_only.sysml`
```sysml
// Valid syntax, structure, no circular deps, but L8 fails
package Library {
    calc def GoodCalc {
        in x : Real;
        return y : Real;
    }
}
// designs/design.sysml:
package Design {
    private import Library::GoodCalc;
    part system {
        attribute length : Real = 10.0;
        attribute width : Real = 5.0;
        attribute area : Real = length * width;  // L8: unextractable
        calc good : GoodCalc {
            in x = length;  // bound correctly
        }
    }
}
```
**Expected:** L1-L3 PASS, L8 FAIL (unextractable expression in designs/)

### For the Implementation — Gaps to Fix

1. **L4 should either do something or be removed.** Currently it's a counter that always passes. Either implement the constraint coverage ratio + threshold the blog describes, or drop it and renumber.

2. **L5 should either do something or be merged.** `check_unit_consistency` and `check_constraint_coverage` are both unimplemented. If L5 were to check unit dimensional analysis via syside, that would be genuinely distinct. Otherwise, merge the constraint counting into L4 and drop L5.

3. **L6 should check source citations, not just doc comment presence.** A regex scan for patterns like `Source:`, `[citation]`, DOI references, etc. within doc comments would make the traceability claim honest.

4. **L3 test should assert on the circular dependency.** The current test (`test_circular_dependency_detected`, line 520-551) doesn't assert that cycles are found — it only checks `result.level == 3`.

5. **L6 and L7 always pass** — consider whether "informational only" levels should be clearly distinguished from "blocking" levels in the runner output.

## Code References

- `src/agentic_mbse/validation/level1_syntax.py:33-95` — L1 implementation
- `src/agentic_mbse/validation/level2_structure.py:64-421` — L2 implementation (6 checks + ADR-002)
- `src/agentic_mbse/validation/level3_dataflow.py:38-129` — L3 import graph + cycle detection
- `src/agentic_mbse/validation/level4_constraints.py:36-88` — L4 stub (always passes)
- `src/agentic_mbse/validation/level5_semantic.py:41-150` — L5 stubs (unit: empty, coverage: 0%)
- `src/agentic_mbse/validation/level6_traceability.py:40-135` — L6 doc comment presence
- `src/agentic_mbse/validation/level7_architecture.py:39-152` — L7 manifest subsystem check
- `src/agentic_mbse/validation/level8_codegen.py:55-598` — L8 codegen readiness (5 checks)
- `src/agentic_mbse/validation/adr002.py:28-510` — ADR-002 checks (integrated into L2)
- `src/agentic_mbse/sysml/types.py:66-95` — ValidationCode enum
- `tests/test_sysml_quality_checks.py:85-923` — existing test coverage
- `claude/skills/model-validation/SKILL.md:29-41` — user-facing pyramid description

## Open Questions

1. **Unit dimensional analysis**: Where does this future capability live? It was L5's second intended purpose (checking units flow correctly through calculations). It's genuinely distinct from everything else but requires syside unit parsing that doesn't exist. Could be a future L4 enhancement or a new level added later.

2. **L3 blog language**: The blog's "dead ends / value propagation" framing overpromises. Needs tightening to "circular import detection" specifically.

3. **Threshold behavior for WIP levels**: L4 (constraints) and L5 (traceability) currently never fail. Should they optionally fail above a configurable threshold once implemented (e.g., >50% undocumented → fail)?

---

## Agreed Direction (2026-02-27)

After discussion, the following restructuring was agreed upon. The goal is 6 honest levels that match the blog post, with WIP levels clearly identified.

### New 6-Level Structure

| New Level | Name | Source | Status |
|-----------|------|--------|--------|
| **1. Syntax** | Parser errors | Current L1 (unchanged) | Real, blocking |
| **2. Structure** | Unused defs, unbound inputs, literal/undefined bindings | Current L2 minus ADR-002 checks | Real, blocking |
| **3. Dependencies** | Circular package imports | Current L3 (tighten blog language) | Real, blocking |
| **4. Constraints** | Constraint counts + coverage metrics | Current L4 + L5's constraint coverage stub | WIP, informational |
| **5. Traceability** | Doc comment coverage → future source citation parsing | Current L6 (renumbered) | WIP, informational |
| **6. Architecture** | ADR-002 rules + manifest validation + codegen readiness | Current L2's ADR-002 + L7 + L8 | Real, customizable/opt-in |

### Key Decisions

**Drop Level 5 (Semantic Consistency).** Original intent was two things:
- Constraint coverage analysis → merge into new L4 (natural extension of constraint counting)
- Unit dimensional analysis → defer; no near-term path to implementation. Can be a future L4 enhancement or new level.

**Move ADR-002 checks from L2 to L6.** The three ADR-002 checks (V1: calc def locations, V2: static expressions, V4: supported operators) are application-specific architectural rules for the TEA pipeline, not generic structural completeness. Moving them:
- Makes L2 purely generic ("is this well-formed SysML with all inputs connected?")
- Makes L6 the application-specific layer ("does this model conform to patterns needed for *our* pipeline?")
- Aligns with the blog's framing of L6 as "our method of model execution places additional structural requirements"

**Combine L7 + L8 into new L6.** The manifest-driven subsystem checks (L7) and codegen readiness checks (L8) are both pipeline-specific architectural requirements. Together with ADR-002 rules, they form a coherent "architecture" level that's opt-in and customizable per application.

**Rename `L8_` → `L6_` in ValidationCode.** The only downstream consumer is fusion-tea, which has no Python references to these codes — only `.project/` docs. fusion-tea doc updates are included in the scope.

**L4 and L5 are WIP.** They stay in the stack with honest descriptions:
- L4: "We track constraint counts; automated coverage/threshold checking is in progress"
- L5: "We check doc comment presence; automated source citation parsing is planned"

**L5 future vision.** The traceability level should eventually:
1. For a given component, grab the doc comment
2. Parse → extract source type and location (selective, not entire doc)
3. Retrieve source text (selective passage, not full document)
4. Pass component code + source text to a small LLM for verification

### Migration Mapping

| Current File | Action | New Location |
|---|---|---|
| `level1_syntax.py` | Keep as-is | `level1_syntax.py` |
| `level2_structure.py` | Remove ADR-002 imports/calls | `level2_structure.py` |
| `level3_dataflow.py` | Keep as-is | `level3_dataflow.py` |
| `level4_constraints.py` | Absorb L5's `check_constraint_coverage()` | `level4_constraints.py` |
| `level5_semantic.py` | **Delete** | — |
| `level6_traceability.py` | Renumber to level 5 | `level5_traceability.py` |
| `level7_architecture.py` | Merge into new L6 | `level6_architecture.py` |
| `level8_codegen.py` | Merge into new L6 | `level6_architecture.py` |
| `adr002.py` | Move integration from L2 to L6 | Called by `level6_architecture.py` |

### Updated Blog Post Language

```
To that end, we have built a six-level hierarchy of automated model
validation. Each level catches a different class of error, and together
they provide a reasonable (though not complete) check on model quality.

- **Level 1: Syntax.** Does the SysML parse correctly? This is the
  equivalent of "does it compile." If the model has syntax errors,
  nothing downstream matters.

- **Level 2: Structure.** Are there unused definitions, unbound
  calculation inputs, or incomplete bindings? Orphaned components
  often indicate that the model is incomplete or that an agent
  created something redundant. Inputs bound to undefined attributes
  indicate broken data flow.

- **Level 3: Dependencies.** Are there circular imports between
  packages? Circular dependencies prevent deterministic model loading
  and indicate architectural problems in how packages reference each
  other.

- **Level 4: Constraints.** What fraction of elements and signals
  have physical constraints? If too many parameters are unconstrained,
  the model is too theoretical to produce meaningful cost or
  performance estimates. We track constraint coverage metrics;
  automated threshold enforcement is on our roadmap.

- **Level 5: Traceability.** Are sources documented in the models?
  Every parameter value and assumption should trace to a source: a
  paper, a dataset, a domain expert's input, or an explicit
  assumption. We currently check documentation coverage; automated
  source citation verification is planned.

- **Level 6: Architecture.** Our method of model execution places
  additional structural requirements on how models are organized.
  This level verifies that calculation definitions are in the right
  places, that expressions follow supported patterns, that design
  parameter values are extractable, and that models conform to the
  conventions needed for automated cost and performance analysis.
  This is the layer where application-specific rules live.
```

### Test Plan for Distinctness

Each level needs a fixture that fails *only* at that level:

| Level | Fixture Description | Fails Because |
|---|---|---|
| L1 | Broken syntax (`calc def MissingBrace in x`) | Parser error |
| L2 | Valid syntax but unbound calc input | Unbound input (no ADR-002 violation) |
| L3 | Two packages with circular imports, all inputs bound | Circular import cycle |
| L4 | No constraints in a model with attributes | 0% constraint coverage (once threshold is added) |
| L5 | Valid model, all definitions lack doc comments | 0% documentation coverage (once threshold is added) |
| L6 | Valid structure, no circular deps, but calc def in `designs/` or unextractable design attr expression | ADR-002 violation or codegen readiness failure |
