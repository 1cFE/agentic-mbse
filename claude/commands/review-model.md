---
name: review-model
description: Review a design document against project requirements, architecture decisions, and SysML conventions
skills: [sysml-conventions, model-validation, project-structure, requirements-tracking]
allowed-tools: [Read, Grep, Glob, Bash, Task, Write, Edit, AskUserQuestion]
user-invocable: true
---

# Review Model Command

**Purpose:** REVIEW a design before implementing — check it against project requirements, architecture decisions, and SysML conventions.
**Input:** Work item with `design.md` and `spec.md` in `work/active/{WI-XXX}_{name}/`
**Output:** `work/active/{WI-XXX}_{name}/review.md`

This is an optional quality gate between `/design-model` and `/plan-model`. The review is advisory — the user can proceed without it (AP-5: toolkit, not pipeline). review.md is NOT a PM-tracked stage; the PM engine does not look for it.

When invoked without a work item, ask which item in `work/active/` to review.

## Skills Referenced

- **sysml-conventions**: Syntax rules, naming, definition vs usage, pitfalls. Consult when checking prototype code and SysML stencils in the design.
- **model-validation**: Quality pyramid, validation levels, regression patterns. Consult when assessing whether the design's validation plan is adequate.
- **project-structure**: Library vs designs separation, file organization, 4-directory model. Consult when checking that the design places elements correctly.
- **requirements-tracking**: PR-XXX format, compliance checking. Consult when verifying the design against project-wide rules.

## Process

### 1. Read the Design

Read the work item's `spec.md` and `design.md` fully. Understand:
- What the spec requires (MR-XXX requirements, success criteria, scope)
- What the design proposes (architecture approach, element placement, interfaces, prototype results)
- What sources were cited and what validation was performed

If `design.md` doesn't exist, stop and suggest `/design-model` first. If a previous `review.md` exists (re-review after design revision), it will be overwritten — git history preserves the previous version.

### 2. Check Against Project Standards

Run four checks in parallel using sub-agents for efficiency — they are independent of each other. For each, collect specific findings with file/section references.

**PR-XXX Compliance** — Read `modeling_project/REQUIREMENTS.md`. For each project requirement relevant to this design's scope, assess whether the design complies. Flag violations and near-misses.

**AD-XXX Adherence** — Read `modeling_project/ARCHITECTURE.md`. Check that the design respects domain decomposition, package organization, and key architectural decisions. Flag deviations — they may be intentional (document why) or accidental (fix needed).

**SysML Conventions** — Per the **sysml-conventions** skill, check naming, definition vs usage separation, doc comment format, redefines/subsets usage, import patterns, and known pitfalls. If the design includes prototype code or SysML stencils, review them for correctness.

**Validation Adequacy** — Per the **model-validation** skill, check that the design's validation plan covers the right levels. Are regression tests planned for calculations? Are cross-file dependencies accounted for? Are Level 4+ concerns (constraints, semantic consistency) addressed?

### 3. Curate Findings

Present each finding to the user with:
- **What**: the specific issue or concern
- **Where**: file path and section in design.md, or the relevant PR-XXX/AD-XXX
- **Severity**: critical (blocks implementation), concern (should address), suggestion (nice to have)

For each finding, the user decides:
- **Accept** — incorporate into the design (will need `/design-model` revision)
- **Skip** — not relevant or disagree
- **Defer** — valid but not for this work item (document for future)

### 4. Write review.md

Create `work/active/{WI-XXX}_{name}/review.md` with YAML frontmatter:

```yaml
---
Verdict: pass | concerns | fail
Created: <YYYY-MM-DD>
Related Artifacts:
  Design: ./design.md
---
```

**Verdict criteria**:
- **pass**: No critical findings. Design is ready for planning/implementation.
- **concerns**: No critical findings, but accepted findings should be addressed. Design can proceed with modifications.
- **fail**: Critical findings that must be resolved before implementation. Return to `/design-model`.

The body should contain:
- **Summary** — 2-3 sentence verdict explanation
- **Findings** — each finding with its status (accepted/skipped/deferred), severity, and detail
- **Accepted Changes** — consolidated list of what needs to change in the design
- **Deferred Items** — captured for future reference

### 5. Recommend Next Steps

Based on the verdict:
- **pass** → proceed to `/plan-model`
- **concerns** → revise with `/design-model` (review.md documents what to fix), then `/plan-model`
- **fail** → return to `/design-model` to address critical findings, optionally re-review

## Guidelines

- This is a review, not a redesign. Identify issues; don't rewrite the design yourself.
- Be specific — "PR-003 requires EXPOSE pattern for intermediate costs; design.md § Proposed Design doesn't use it for `raw_material_cost`" is useful. "Design could be better" is not.
- Distinguish between convention violations (objective, checkable) and design judgment (subjective). Flag both but label them clearly.
- The review is advisory. If the user skips all findings, that's their choice. Document what was skipped and move on.
- `/review-model` checks a single work item's design. For cross-model verification and pattern promotion across the project, use `/audit-models`.
- Don't duplicate what validation already catches. If `uv run agentic-mbse validate` would flag it, note that instead of re-analyzing.

---

**Related Commands:** Before → `/design-model` | After → `/plan-model` | Cross-model → `/audit-models`
