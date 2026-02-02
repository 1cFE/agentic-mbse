# Skill Content Extraction Mapping

**Status:** Complete
**Created:** 2026-02-02
**Epic:** EPIC-ARCH-002 (D2.5)
**Purpose:** Bridge artifact between Epic 2 (Skills) and Epic 3 (Commands). Tells Epic 3 exactly what to remove from each command and what to replace it with.

---

## How to Use This Document

For each command, sections are classified as:

- **→ SKILL** — Content already exists in a skill. Epic 3 should **remove** the inline content and add a skill reference.
- **→ STAYS** — Workflow logic that belongs in the command. Epic 3 should **keep** this (possibly refactored for brevity).
- **→ PARTIAL** — Some content extracted to a skill, some remains. Epic 3 should remove the extracted portion and keep the rest.

**Workflow categories** for STAYS sections:
- **Orchestration** — Stage progression, gates, user approval flows
- **Template** — Output document structure (spec.md, design.md, plan.md formats)
- **Interaction** — AskUserQuestion flows, confirmation patterns
- **Agent coordination** — Task tool spawning, parallel execution patterns

---

## Summary Statistics

| Command | Current Lines | Sections → Skill | Sections → Stays | Sections → Partial |
|---------|--------------|------------------|-------------------|---------------------|
| design-model.md | 1,345 | 3 | 11 | 2 |
| plan-model.md | 676 | 1 | 10 | 3 |
| implement-model.md | 493 | 1 | 7 | 3 |
| spec-model.md | 392 | 1 | 7 | 2 |
| audit-models.md | 446 | 1 | 8 | 1 |
| onboard.md | 577 | 3 | 5 | 1 |
| backlog.md | 358 | 0 | 8 | 2 |
| manage-sources.md | 357 | 1 | 5 | 1 |
| research.md | 243 | 0 | 6 | 2 |
| **Total** | **4,887** | **11** | **67** | **17** |

---

## Skill Cross-Reference

Which skills serve which commands (from skill "When to Reference" sections):

| Skill | Commands That Should Reference It |
|-------|-----------------------------------|
| sysml-conventions | design-model, implement-model, plan-model, audit-models |
| model-validation | design-model, implement-model, plan-model, audit-models, spec-model |
| project-structure | design-model, implement-model, spec-model, plan-model, onboard |
| source-traceability | design-model, implement-model, spec-model, audit-models, research, manage-sources |
| epic-decomposition | backlog, spec-model, onboard |
| requirements-tracking | design-model, implement-model, spec-model, audit-models |
| toolkit-awareness | all commands (via `uv run` prefix, CLI invocation patterns) |

---

## 1. design-model.md (1,345 lines)

### → SKILL: "Stage 5.5: Common Pitfalls & Quick Reference"

**Absorbing skill:** `sysml-conventions`
**Coverage:** Full extraction. The entire "SysML v2 Syntax Rules for This Project" subsection (attribute declarations, units notation, part definitions, material references, temperature, documentation requirements, pre-flight checklist) is captured in the skill's Naming Conventions, Common Pitfalls, Doc Comment Format, and Anti-Patterns sections.

**Epic 3 action:** Remove the entire "Stage 5.5" section. Replace with: `For SysML syntax rules and pitfalls, see the **sysml-conventions** skill.`

### → SKILL: "Stage 5.5 > Validation Commands" subsection

**Absorbing skill:** `model-validation` (CLI Invocation section) + `toolkit-awareness`
**Coverage:** Full. The `syside check` and `agentic-mbse validate` commands with flags are in model-validation. The `uv run` prefix convention is in toolkit-awareness.

**Epic 3 action:** Remove validation command block. Replace with skill references.

### → SKILL: "Guidelines > Critical Requirements" list items about MODELING_GUIDE conventions

**Absorbing skill:** `sysml-conventions` (Core Principle, Naming Conventions, Definition vs Usage Rule)
**Coverage:** Full. "MUST read MODELING_GUIDE for definitions vs usages pattern" is the core content of sysml-conventions.

**Epic 3 action:** Replace with: `Follow **sysml-conventions** skill for definitions vs usages pattern, naming, and syntax rules.`

### → PARTIAL: "Pre-Flight Check (MANDATORY)"

**Extracted portion:** Library structure questions ("Where should new definitions go?", "What cross-file binding patterns?") → `project-structure` skill
**Extracted portion:** "What common pitfalls should I avoid?" → `sysml-conventions` skill
**Remaining (STAYS — Orchestration):** The pre-flight *process* (read README first, verify prerequisites, checklist format) is workflow logic.

**Epic 3 action:** Keep the pre-flight *process* but replace inline knowledge references with skill pointers. The pre-flight checklist should reference skills instead of embedding the answers.

### → PARTIAL: "Stage 6: Prototype Implementation & Validation"

**Extracted portion:** 8-level validation pyramid details, blocking/non-blocking distinction, `--complete`/`--level`/`--verbose` flags → `model-validation` skill
**Remaining (STAYS — Orchestration):** The prototype creation workflow (implement, validate, check integration, generate validation report, stop-if-fail logic) is workflow logic specific to the design command.

**Epic 3 action:** Keep the Stage 6 workflow steps. Replace inline validation details with: `Run validation per the **model-validation** skill.`

### → STAYS (Orchestration): "Overview" + purpose/input/output header

Command entry point, what the command does, when invoked behavior.

### → STAYS (Orchestration): "Design Algorithm" + "Example Workflow"

Stage progression (OUTLINE → RESEARCH → ADD DETAIL → FINALIZE → PROTOTYPE → VALIDATE → ITERATE → APPROVE). This is the command's core workflow and cannot be extracted.

### → STAYS (Orchestration): "Stage 1: Initial Setup & Top-Level Outline"

Read project context, create initial design file, outline top-level structure, identify research needs. Workflow-specific.

### → STAYS (Agent coordination): "Stage 2: Research & Analysis"

Parallel agent launching patterns (Explore, kerml-expert, sysml-expert, codebase analysis), web search strategy, consolidation of findings. Agent coordination is inherently command-specific.

### → STAYS (Interaction): "Stage 3: Design Alternatives & User Guidance"

Alternative presentation format, decision solicitation, user approval flow. Interaction patterns.

### → STAYS (Orchestration): "Stage 4: Progressive Detail Addition"

Iterative detail refinement process, completeness evaluation. Workflow logic.

### → STAYS (Orchestration): "Stage 5: Design Finalization"

Document consolidation, final sections, review checklist. Workflow logic.

### → STAYS (Orchestration): "Stage 7: Iterate Design if Needed" + "Stage 8: User Approval"

Iteration categorization, re-validation loop, approval documentation. Workflow logic.

### → STAYS (Template): "Final design document structure" (design.md template)

The output document format (Model Elements, Cross-File Bindings, Constraints, Validation Plan, Implementation Checklist). This is the command's artifact template.

### → STAYS (Agent coordination): "Sub-Agent Usage (Detailed)"

kerml-expert, sysml-expert, syside-expert, sysmlv2-validator spawning patterns and when to use each. Agent coordination.

### → STAYS (Orchestration): "Guidelines" (remaining items after extraction)

Decision points, error handling, success criteria. Workflow quality standards.

---

## 2. implement-model.md (493 lines)

### → SKILL: "Stage 3: Phase Completion & Validation > Quality Validation"

**Absorbing skill:** `model-validation`
**Coverage:** Full. The 8-level pyramid description (Levels 1-8 with names, what each checks), `--complete`/`--level`/`--verbose` flags, "Levels 1-3 MUST pass" rule, ADR-002 compliance check, regression test patterns, test location conventions — all captured in model-validation skill.

**Epic 3 action:** Remove the inline validation level descriptions and test patterns. Replace with: `Run validation per the **model-validation** skill. Regression test patterns are documented there.`

### → PARTIAL: "Stage 1.4: Pre-Flight Syntax Validation"

**Extracted portion:** Syntax patterns to test (attribute declarations, units, part definitions, temperature) → `sysml-conventions` skill (Common Pitfalls section)
**Remaining (STAYS — Orchestration):** The de-risking *workflow* (create temp file, validate with syside, fix-and-retry loop, then use corrected pattern). This is a workflow technique.

**Epic 3 action:** Keep the temp-file validation workflow. Replace the inline "common patterns to pre-test" list with: `See **sysml-conventions** skill for patterns to validate.`

### → PARTIAL: "Stage 2: Sequential Implementation > Add Doc Comments"

**Extracted portion:** Doc comment format (Source, Reference, Last Updated fields) → `sysml-conventions` skill (Doc Comment Format section)
**Extracted portion:** Doc comment content requirements (what goes in Source, Reference fields) → `source-traceability` skill
**Remaining (STAYS — Orchestration):** The per-task implementation loop (create/modify → doc comments → validate → update progress).

**Epic 3 action:** Keep the loop. Replace inline doc comment format with skill references.

### → PARTIAL: "Guidelines > MODEL QUALITY (CRITICAL)"

**Extracted portion:** Naming conventions (Title Case for defs, snake_case for usages), standard imports, doc comment requirements → `sysml-conventions` skill
**Remaining (STAYS — Orchestration):** The NEVER/ALWAYS rules as implementation enforcement (these are the same knowledge but framed as mandatory workflow gates).

**Epic 3 action:** Simplify to: `Follow **sysml-conventions** skill strictly. See that skill for naming, imports, and doc comment requirements.` Keep the NEVER/ALWAYS enforcement framing but remove the duplicated content.

### → STAYS (Orchestration): "Stage 1: Plan Analysis & Scope Confirmation"

Read plan, read design, review prototype, check progress, confirm scope. Workflow-specific.

### → STAYS (Orchestration): "Stage 1.2: Efficient Reference Document Handling"

Read-once strategy, section extraction, Task agent for complex extraction. This is an implementation technique, not domain knowledge. Candidate for future "efficient-implementation" skill but not currently extracted.

### → STAYS (Orchestration): "Stage 1.3: Assess Parallelization Opportunities"

Sequential vs parallel decision, Task tool patterns, safety rules. Agent coordination.

### → STAYS (Orchestration): "Stage 2.5: Efficient Batch Editing"

Read/Write vs Script vs Individual Edits patterns. Implementation technique. Candidate for future skill but not currently extracted.

### → STAYS (Orchestration): "Stage 3 > MANDATORY: Update Plan Document" + traceability + status sync

Progress tracking enforcement. Workflow logic.

### → STAYS (Orchestration): "Stage 4: Final Validation"

Completion checklist. Workflow logic.

### → STAYS (Orchestration): "MANDATORY Progress Tracking" + error handling

Progress update pattern, error handling rules. Workflow enforcement.

---

## 3. spec-model.md (392 lines)

### → SKILL: "Guidelines > Requirement Format Standards"

**Absorbing skill:** `requirements-tracking`
**Coverage:** Full. MR-XXX format, EARS format ("The model SHALL..."), Type/Description/Priority/Rationale/Validation structure, good MR examples — all in requirements-tracking skill (PR-XXX Entity Format, EARS Format Reference, Promotion Path sections).

**Epic 3 action:** Remove inline requirement format standards. Replace with: `Format requirements per the **requirements-tracking** skill (MR-XXX format with EARS syntax).`

### → PARTIAL: "Stage 3 > Define Evaluatable Success Criteria"

**Extracted portion:** Test assertion patterns (definition exists, calculation works, units consistency, no parse errors) → `model-validation` skill (Regression Testing section)
**Remaining (STAYS — Orchestration):** The principle that criteria should be "both human-readable AND machine-checkable" and the table format for presenting them. This is spec workflow guidance.

**Epic 3 action:** Keep the human+machine principle. Replace inline test patterns with: `See **model-validation** skill for test patterns and regression testing conventions.`

### → PARTIAL: "Stage 3 > Regression Safety Criteria"

**Extracted portion:** Interface stability, test coverage requirements → `model-validation` skill
**Remaining (STAYS — Orchestration):** The process of checking which designs depend on a library (check imports in `models/designs/`). This is workflow guidance.

**Epic 3 action:** Keep the process. Reference model-validation for test coverage patterns.

### → STAYS (Orchestration): "Overview" + purpose/input/output header

Command entry point and invocation behavior.

### → STAYS (Orchestration): "Stage 1: Context and Model Landscape Understanding"

Check epic context, check existing models, read context files, identify modeling scope. Workflow-specific.

### → STAYS (Interaction): "Stage 2: Modeling Requirements Scoping"

Define required elements, identify validation requirements, establish scope boundaries, get user approval. Interaction patterns.

### → STAYS (Orchestration): "Stage 3: Modeling Requirements Definition" (minus extracted format standards)

Requirement drafting process, categorization, prioritization. Workflow logic.

### → STAYS (Template): "Stage 4: Document Creation"

spec.md file structure and content template. Artifact template.

### → STAYS (Orchestration): "Guidelines > Quality Standards" + "Model-Specific Requirements"

Location requirements (library vs designs), traceability requirements, validation requirements, epic alignment. These reference the same knowledge as skills but framed as spec-writing enforcement rules.

### → STAYS (Orchestration): "Error Handling" + "Critical Rules"

Spec-specific error conditions. Workflow logic.

---

## 4. plan-model.md (676 lines)

### → SKILL: "Step 3 > Test Requirements" + test phase pattern + example

**Absorbing skill:** `model-validation` (Regression Testing section)
**Coverage:** Full. Test phase pattern table (library defs → structural tests, design instances → integration tests, final → full regression), test stencil example, final validation phase requirements, `pytest tests/models/` convention — all in model-validation.

**Epic 3 action:** Remove inline test patterns. Replace with: `Test requirements per the **model-validation** skill. Each phase includes test activities per the skill's regression testing patterns.`

### → PARTIAL: "Step 4: Validate Plan Feasibility"

**Extracted portion:** Syntax pattern checking rules, constraint validation syntax, ADR-002 compliance (calc defs in library/ only) → `sysml-conventions` skill
**Extracted portion:** Checking against design validation report for Level 4-7 issues → `model-validation` skill
**Remaining (STAYS — Orchestration):** The feasibility assessment *process* (review planned changes, spot-check critical patterns, flag risks, document prototype baseline). This is planning workflow.

**Epic 3 action:** Keep the feasibility assessment process. Replace inline syntax rules with: `Check planned syntax patterns against the **sysml-conventions** skill.` Replace validation level references with: `Address Level 4-7 issues per the **model-validation** skill.`

### → PARTIAL: "Appendix: Quick Reference"

**Extracted portion:** Validation commands → `model-validation` skill + `toolkit-awareness` skill
**Extracted portion:** File organization tree → `project-structure` skill
**Extracted portion:** Naming conventions → `sysml-conventions` skill
**Extracted portion:** Required imports → `sysml-conventions` skill
**Remaining:** Nothing — entire appendix is extractable.

**Epic 3 action:** Remove the entire Quick Reference appendix. Replace with: `See the **sysml-conventions**, **model-validation**, and **project-structure** skills for quick reference on syntax, validation, and file organization.`

### → PARTIAL: "Guidelines > Plan Quality Standards" (partial)

**Extracted portion:** "Each phase is 1-3 hours" and validation command references → model-validation
**Remaining (STAYS — Orchestration):** Phasing principles, checklist granularity guidance, design document reference patterns. Planning methodology.

**Epic 3 action:** Keep phasing principles. Remove inline validation references.

### → STAYS (Orchestration): "Overview" + "Key Differences from Design Command"

Command entry point, planning context, design-vs-plan distinction table. Workflow-specific.

### → STAYS (Orchestration): "Step 1: Read Design Document Thoroughly"

Read design, read spec, read conventions. Workflow-specific.

### → STAYS (Orchestration): "Step 2: Identify Implementation Phases"

Phasing principles (library before instances, bottom-up, logical groupings). Planning methodology.

### → STAYS (Template): "Step 3: Create Plan Document" (document structure)

plan.md file structure, phase template, prototype context, sub-agent invocation strategy. Artifact template.

### → STAYS (Orchestration): "Guidelines > Fail-Fast Principles"

Run validation early, clear completion gates. Planning methodology.

### → STAYS (Interaction): "Phased User Review"

When to offer review, how to structure review points. Interaction patterns.

### → STAYS (Orchestration): "Task Tracking Integration" + "Error Handling" + "Success Criteria"

TodoWrite integration, error conditions, quality standards. Workflow logic.

### → STAYS (Template): "Implementation Notes" section structure

Phase completion note template. Artifact template.

---

## 5. audit-models.md (446 lines)

### → SKILL: "Stage 1 > Verification Standards" (PASS/WARN/FAIL thresholds)

**Absorbing skill:** `model-validation` (Verification Thresholds section)
**Coverage:** Full. ±1% PASS, ±5% WARN, >5% FAIL thresholds and their meanings are in the skill.

**Epic 3 action:** Remove inline threshold definitions. Replace with: `Apply verification thresholds from the **model-validation** skill (PASS ≤1%, WARN 1-5%, FAIL >5%).`

### → PARTIAL: "Guidelines > Special Cases"

**Extracted portion:** Calculated values requiring evaluation, unit conversions, citation patterns → `source-traceability` skill (Citation Patterns, Confidence Assessment)
**Remaining (STAYS — Orchestration):** Audit-specific comparison logic (element-by-element array comparison, max discrepancy reporting, design-specific vs not-implemented categorization). This is audit methodology.

**Epic 3 action:** Keep audit-specific comparison logic. Reference source-traceability for citation patterns.

### → STAYS (Orchestration): "Overview" + purpose/input/output

Command entry point. Workflow-specific.

### → STAYS (Interaction): "Stage 1: Scope Definition"

Identify target models, locate baseline, present audit scope, get user confirmation. Interaction patterns.

### → STAYS (Orchestration): "Stage 2: Model Inspection"

Read target models, catalog parameters, extract traceability. Audit methodology.

### → STAYS (Orchestration): "Stage 3: Baseline Verification"

Read baseline files, match parameters, calculate discrepancies, generate verification table. Audit methodology.

### → STAYS (Template): "Stage 4: Discrepancy Analysis & Reporting"

Audit report structure (Executive Summary, Detailed Findings, Recommendations, Verification Details, Audit Metadata). Artifact template.

### → STAYS (Interaction): "Stage 5: Summary & Next Steps"

Present summary, save report, offer follow-up actions. Interaction patterns.

### → STAYS (Orchestration): "Guidelines > Verification Standards" (prose guidance beyond thresholds)

Pass/Warn/Fail action descriptions. Audit methodology.

### → STAYS (Orchestration): "Error Handling"

Baseline not accessible, model doesn't parse, traceability missing. Workflow logic.

### → STAYS (Orchestration): "Efficiency Tips"

Cache baseline values, parallel reads, incremental generation. Audit methodology.

---

## 6. research.md (243 lines)

### → PARTIAL: "Stage 1 > read SOURCE_INDEX.md" + "Stage 2 > For Domain Research"

**Extracted portion:** SOURCE_INDEX.md as authority sources registry, source types (codebase/documentation/database/reference), what each type provides → `source-traceability` skill (SOURCE_INDEX.md Format, Source Types table)
**Remaining (STAYS — Orchestration):** The research *process* of reading SOURCE_INDEX, then launching agents based on source types. This is workflow logic.

**Epic 3 action:** Keep the research process. Replace inline source type definitions with: `See **source-traceability** skill for source types and SOURCE_INDEX.md format.`

### → PARTIAL: "Sub-Agent Usage > sysmlv2-doc-analyzer"

**Not extracted:** The sysmlv2-doc-analyzer agent usage patterns are not in any skill (they're agent coordination, not domain knowledge).
**STAYS (Agent coordination):** Agent spawning patterns for research contexts.

### → STAYS (Orchestration): "Overview" + purpose/input/output

Command entry point. Workflow-specific.

### → STAYS (Orchestration): "Stage 1: Context Gathering"

Read project context, check existing research, check related epics. Workflow-specific.

### → STAYS (Agent coordination): "Stage 2: Parallel Research"

Agent spawning patterns for codebase, model, and domain research. Agent coordination.

### → STAYS (Orchestration): "Stage 3: Analysis and Synthesis"

Read files, cross-reference, extract insights. Research methodology.

### → STAYS (Template): "Stage 4: Document Creation"

Research document template (frontmatter, sections). Artifact template.

### → STAYS (Orchestration): "Guidelines" + "Error Handling" + "Critical Rules"

Quality standards, research type guidelines, error conditions. Workflow logic.

---

## 7. manage-sources.md (357 lines)

### → SKILL: "SOURCE_INDEX.md Format Reference" section

**Absorbing skill:** `source-traceability` (SOURCE_INDEX.md Format section)
**Coverage:** Full. Source entry format (Name, Type, Location, Use For, Validation), source types — all in the skill.

**Epic 3 action:** Remove inline format reference. Replace with: `Format entries per the **source-traceability** skill.`

### → PARTIAL: "Stage 3 > Option A > Step 6: Permission path format rules"

**Extracted portion:** `~/path` vs `//path` vs `/path` semantics → `toolkit-awareness` skill
**Remaining (STAYS — Orchestration):** The *workflow* of offering to add permissions, reading settings.json, merging permissions. This is interaction logic.

**Epic 3 action:** Keep the permission workflow. Replace inline format rules with: `See **toolkit-awareness** skill for permission path format rules.`

### → STAYS (Orchestration): "Overview" + purpose

Command entry point. Workflow-specific.

### → STAYS (Orchestration): "Stage 1: Read Current State"

Check if SOURCE_INDEX.md exists, parse sources, report to user. Workflow-specific.

### → STAYS (Interaction): "Stage 2: Determine Action" + "Stage 3: Execute Action"

Add/remove/view flows with AskUserQuestion. Interaction patterns.

### → STAYS (Interaction): "Stage 4: Offer Next Steps"

Follow-up suggestions. Interaction patterns.

### → STAYS (Template): "Minimal SOURCE_INDEX.md Template"

Bootstrap template content. Artifact template.

---

## 8. backlog.md (358 lines)

### → PARTIAL: "Stage 4 > Format and Add Work Items"

**Extracted portion:** Feature vs Epic format distinction, scope-appropriate structure → `epic-decomposition` skill (Scale Taxonomy section: Trivial/Standard/Epic)
**Remaining (STAYS — Template):** The actual markdown format templates for BACKLOG.md entries. These are output format, not domain knowledge.

**Epic 3 action:** Keep the format templates. Add: `See **epic-decomposition** skill for scale taxonomy (when to use Feature vs Epic format).`

### → PARTIAL: "Mode: Clear > Stage 1: Scan Active Work"

**Partially related:** Completion assessment criteria (checkboxes checked, "COMPLETE" status, final sign-off) are related to `epic-decomposition` but not directly extracted. The skill covers decomposition, not completion assessment.
**STAYS (Orchestration):** Completion scanning logic, Explore agent for assessment. Workflow-specific.

**Epic 3 action:** Keep as-is. This is workflow logic not captured by any skill. Flagged as candidate for future "work-lifecycle" skill.

### → STAYS (Orchestration): "Mode: Add > Stage 1: Gather Work Items"

Source parsing, user description gathering. Workflow-specific.

### → STAYS (Orchestration): "Stage 2: Check for Duplicates"

Fuzzy matching against existing items. Workflow logic.

### → STAYS (Interaction): "Stage 3: Prioritize Work Items"

Priority selection with AskUserQuestion. Interaction patterns.

### → STAYS (Orchestration): "Stage 5: Confirm Addition"

Summary presentation. Workflow logic.

### → STAYS (Orchestration): "Mode: Clear > Stage 2-4"

Present assessment, archive process (mv, update BACKLOG.md, update OVERVIEW.md), summary. Workflow logic.

### → STAYS (Orchestration): "Guidelines" (work item quality, priority guidance, archive criteria)

Quality standards for work items. These overlap conceptually with epic-decomposition's Goldilocks indicators but are framed as backlog management rules rather than decomposition knowledge.

### → STAYS (Orchestration): "Error Handling"

Missing files, conflicts. Workflow logic.

---

## 9. onboard.md (577 lines)

### → SKILL: "Stage 2.5 > Permission path format rules"

**Absorbing skill:** `toolkit-awareness`
**Coverage:** Full. `~/path` vs `//path` vs `/path` semantics, conversion from absolute paths.

**Epic 3 action:** Remove inline format rules. Replace with: `See **toolkit-awareness** skill for permission path format.`

### → SKILL: "Stage 3.3 > SOURCE_INDEX.md template" (source entry format + source types)

**Absorbing skill:** `source-traceability` (SOURCE_INDEX.md Format, Source Types)
**Coverage:** Full. Source entry structure, type definitions, "How MBSE Commands Use This File" section.

**Epic 3 action:** Remove inline SOURCE_INDEX.md format documentation. Replace with: `Format per the **source-traceability** skill.`

### → SKILL: "Stage 3.4 > models/ directory structure + README"

**Absorbing skill:** `project-structure` (Model File Organization, Library vs Designs Separation)
**Coverage:** Full. library/ vs designs/ distinction, what goes where.

**Epic 3 action:** Remove inline directory structure explanation. Replace with: `See **project-structure** skill for model file organization.`

### → PARTIAL: "Stage 3.5 > Update Project Templates"

**Extracted portion:** modeling_pm/ directory structure and file roles → `project-structure` skill (4-Directory Model, Key Project Files)
**Remaining (STAYS — Orchestration):** The placeholder replacement workflow (which placeholders map to which user answers). This is onboarding workflow.

**Epic 3 action:** Keep the placeholder mapping. Reference project-structure for directory roles.

### → STAYS (Orchestration): "Stage 0: Version Control Safety"

Git repo check, uncommitted changes check. Workflow-specific.

### → STAYS (Orchestration): "Stage 1: Directory Discovery"

List contents, report findings, determine state. Workflow-specific.

### → STAYS (Interaction): "Stage 2: Project Context"

3-question interactive flow (what modeling, goals, sources). Interaction patterns.

### → STAYS (Template): "Stage 3.1: Create README.md" + "Stage 3.2: Create CLAUDE.md"

File templates with placeholder tables. Artifact templates.

### → STAYS (Orchestration): "Stage 4: Summary & Education"

Completion summary, workflow diagram, suggested first steps. Workflow-specific.

---

## Knowledge Gap Analysis

### Fully Extracted (no gaps)

These knowledge domains are completely covered by skills:

1. **SysML syntax conventions** → `sysml-conventions` — naming, definition vs usage, pitfalls, imports, doc comments, anti-patterns
2. **8-level validation pyramid** → `model-validation` — levels, CLI, thresholds, timing, regression testing
3. **4-directory project structure** → `project-structure` — directory model, file organization, library vs designs, EXPOSE pattern
4. **Source traceability** → `source-traceability` — durable chain, SOURCE_INDEX format, citation patterns, traceability matrix
5. **Requirements tracking** → `requirements-tracking` — two-tier model, PR-XXX format, EARS, promotion path, enforcement
6. **Epic decomposition** → `epic-decomposition` — scale taxonomy, Goldilocks indicators, decomposition process

### Partially Extracted (minor gaps, acceptable)

7. **Verification thresholds** — PASS/WARN/FAIL percentages are in `model-validation`, but audit-specific comparison logic (arrays, calculated values, unit conversions) stays in `audit-models` appropriately.
8. **Permission path format** — Core rules in `toolkit-awareness`, but the *workflow* of adding permissions stays in commands appropriately.

### Not Extracted (intentionally remains in commands)

These are **not knowledge** — they are workflow patterns that belong in commands:

1. **Efficient reference document handling** (implement-model) — implementation technique for managing context
2. **Efficient batch editing** (implement-model) — implementation technique for file modifications
3. **Completion assessment** (backlog) — workflow logic for determining if work is done
4. **Agent spawning patterns** (design-model, research, implement-model) — command-specific coordination
5. **Artifact templates** (all commands) — output document structures

**Assessment:** No knowledge is unaccounted for. All domain knowledge has been extracted to skills. What remains in commands is workflow logic, interaction patterns, agent coordination, and artifact templates — exactly what should stay.

---

## Epic 3 Action Summary

For each command, Epic 3 should:

1. **Remove** sections marked "→ SKILL" (replace with 1-line skill reference)
2. **Trim** sections marked "→ PARTIAL" (remove extracted content, keep workflow logic, add skill reference)
3. **Refactor** sections marked "→ STAYS" for brevity (these are already where they belong, but may benefit from tightening)
4. **Add skill loading declarations** to command frontmatter (which skills each command needs)

Expected line count reduction per command (rough estimate based on extracted content):

| Command | Current | Estimated After | Reduction |
|---------|---------|-----------------|-----------|
| design-model.md | 1,345 | ~600-800 | ~40-55% |
| plan-model.md | 676 | ~400-500 | ~25-40% |
| implement-model.md | 493 | ~300-350 | ~30-40% |
| spec-model.md | 392 | ~280-320 | ~18-28% |
| audit-models.md | 446 | ~380-400 | ~10-15% |
| onboard.md | 577 | ~400-450 | ~22-30% |
| backlog.md | 358 | ~320-340 | ~5-10% |
| manage-sources.md | 357 | ~300-320 | ~10-16% |
| research.md | 243 | ~210-230 | ~5-14% |

**Note:** design-model.md has the largest reduction because it has the most embedded knowledge (Stage 5.5 alone is ~60 lines of pure syntax reference). Commands like audit-models and research have less extractable content because they're already mostly workflow logic.

To reach the Epic 3 target of 200-300 lines per command, the STAYS sections will also need refactoring for conciseness — that's Epic 3 work, not extraction.
