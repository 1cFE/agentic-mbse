# Spec: MODELING_GUIDE.md Restructuring

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-01-15T16:14:26+00:00
**Complexity:** MEDIUM
**Branch:** 1cfe_dev

---

## Business Goals

### Why This Matters

The current `MODELING_GUIDE.md.template` is 1,497 lines - too long for effective consumption by both AI agents and human users. Agents must load this entire document into context, consuming tokens on rarely-needed reference material. New users face an overwhelming wall of syntax that obscures the essential principles.

Progressive disclosure solves this: present essential rules first (~200-400 lines), with clear paths to detailed reference material when needed. This reduces cognitive load, improves onboarding, and makes the documentation more maintainable.

### Success Criteria

- [ ] New user/agent can read MODELING_GUIDE.md in ~10 minutes
- [ ] Agents can discover detailed patterns via grep/glob on `docs/patterns/`
- [ ] Pattern docs are self-contained and parser-verified
- [ ] No loss of documented knowledge - all content preserved or integrated

### Priority

P1 (High) per BACKLOG.md. Depends on completed ITEM-BACKPORT-001. Blocks ITEM-LEARNING-001 (which will build on the patterns/ infrastructure).

---

## Problem Statement

### Current State

`project_templates/MODELING_GUIDE.md.template` contains:
- Core principles (Definitions vs Usages, EXPOSE pattern, ADR-002)
- 10 syntax quick-reference patterns with full examples
- 4 MBSE concept patterns
- 490 lines of semantic operator documentation
- Package naming rules
- Validation requirements
- Common mistakes
- Pattern validation status (validated learnings)

Total: **1,497 lines** in a single file.

### Desired Outcome

A restructured documentation system:
1. **MODELING_GUIDE.md** (~200-400 lines): Essential rules, decision shortcuts, pattern references
2. **docs/patterns/*.md** (11 files): Detailed reference material, self-contained, parser-verified
3. **docs/patterns/README.md**: Navigable index for pattern discovery

---

## Scope

### In Scope

1. **Restructure MODELING_GUIDE.md.template** to ≤400 lines
2. **Create 11 pattern documents** by extracting content from current guide
3. **Update docs/patterns/README.md** with complete index
4. **Integrate Pattern Validation Status** content into relevant pattern docs as accepted doctrine

### Out of Scope

- Part 2: Development Mode (`--dev` flag for symlinks)
- Part 3: Learning Feedback Loop (RAW_LEARNINGS.md system)
- Pattern versioning (open design question)
- Publishing patterns to external website

### Edge Cases & Considerations

- `conditionals.md` already exists - reference it, don't duplicate
- Pattern references use bracketed format `[patterns/X.md]` for agent discoverability
- Agents have read permissions to `docs/` via `.claude/settings.json`
- Hyperlinks won't work for humans (docs/ is in agentic-mbse, not target project) - add note explaining location

---

## Requirements

### Functional Requirements

> Requirements below are from research document and user clarification

1. **FR-1**: MODELING_GUIDE.md.template SHALL be ≤400 lines (flexible from original 200 target)

2. **FR-2**: Each major section in the guide SHALL be ≤25 lines with a reference to detailed pattern doc

3. **FR-3**: The following pattern documents SHALL be created in `docs/patterns/`:

   | Pattern Doc | Source Lines | Content |
   |-------------|--------------|---------|
   | `definitions-usages.md` | 18-80 | Full decision tree, specialization patterns |
   | `expose-pattern.md` | 82-141 | Producer/consumer examples, anti-patterns |
   | `adr002-calculations.md` | 144-233 | Expression taxonomy, resolution patterns |
   | `doc-comments.md` | 255-338 | Full template, citation patterns |
   | `syntax-reference.md` | 375-598 | 10 syntax patterns (reference conditionals.md) |
   | `mbse-concepts.md` | 601-693 | Allocation, parametric, cost, interface patterns |
   | `semantic-operators.md` | 696-1186 | All operator distinctions, dual navigation, validated patterns |
   | `package-naming.md` | 1190-1263 | Unique names rule, correct patterns |
   | `common-mistakes.md` | 1320-1369 | Anti-patterns to avoid |
   | `constraints.md` | (consolidate) | Constraint prefixes, syntax from multiple sections |
   | `cross-file-binding.md` | 453-476 | Cross-file imports and bindings |

4. **FR-4**: Pattern Validation Status content (lines 1395-1493) SHALL be integrated into relevant pattern docs as accepted doctrine:
   - Multiplicity Cost Aggregation → `adr002-calculations.md` or new `costing-patterns.md`
   - Part Redefinition Pattern → `semantic-operators.md`
   - Parameterized Multiplicity Pattern → `syntax-reference.md` or `mbse-concepts.md`

5. **FR-5**: `docs/patterns/README.md` SHALL be updated with index of all pattern docs

6. **FR-6**: Pattern references in MODELING_GUIDE SHALL use format: `> **Full reference**: [patterns/X.md]`

7. **FR-7**: Existing `conditionals.md` SHALL be referenced from `syntax-reference.md`, not duplicated

8. **FR-8**: MODELING_GUIDE SHALL include a "Pattern Documentation Index" section explaining that pattern docs are in the agentic-mbse `docs/patterns/` directory

### Non-Functional Requirements

- **NFR-1**: All code examples in pattern docs SHALL pass `syside check` (parser-verified)
- **NFR-2**: Pattern docs SHALL be self-contained (readable without needing the guide)

---

## Acceptance Criteria

### Core Functionality

- [x] MODELING_GUIDE.md.template is ≤400 lines → **205 lines**
- [x] All 11 pattern documents exist in `docs/patterns/`
- [x] Each pattern doc has examples (from verified source)
- [x] Pattern Validation Status content is integrated (not lost)
- [x] `docs/patterns/README.md` lists all patterns with descriptions

### Quality & Integration

- [x] Existing tests continue to pass → 269 passed, 1 skipped
- [x] No broken references in MODELING_GUIDE
- [x] Agents can discover patterns via `Grep("pattern-name", "docs/patterns/")`

---

## Design Notes (from Research)

### Proposed MODELING_GUIDE Structure

The research document (lines 58-235) provides a complete restructured guide template. Key sections:

1. **Header & Quick Links** (~10 lines)
2. **Core Principle: Definitions vs Usages** (~15 lines + reference)
3. **The EXPOSE Pattern** (~15 lines + reference)
4. **Calculation Architecture (ADR-002)** (~15 lines + reference)
5. **Package Structure** (~10 lines)
6. **Naming Conventions** (~8 lines)
7. **Documentation Standards** (~15 lines + reference)
8. **Standard Imports** (~15 lines)
9. **Key Syntax Patterns** (~25 lines - one example each + references)
10. **Validation Checklist** (~10 lines)
11. **Pattern Documentation Index** (~20 lines - table of all pattern docs)

### Pattern Doc Template

Each pattern doc should follow this structure:

```markdown
# Pattern: [Name]

Brief description of what this pattern covers.

## When to Use

[Guidance on when this pattern applies]

## Syntax / Rules

[Core rules and syntax]

## Examples

[Parser-verified examples]

## Common Mistakes

[Anti-patterns and corrections]

## Related Patterns

[Links to related pattern docs]

---
**Last Updated**: YYYY-MM-DD
**Parser Verified**: Yes (syside X.X.X)
```

---

## Related Artifacts

- **Research:** `project/research/20260113-150000_progressive-disclosure-architecture.md`
- **Design:** `.project/active/guide-restructuring/design.md` (to be created)
- **Backlog:** `.project/backlog/BACKLOG.md` (ITEM-GUIDE-001)

---

**Next Steps:** After approval, proceed to `/_my_design`
