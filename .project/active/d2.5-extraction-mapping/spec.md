# Spec: Skill Content Extraction Mapping

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-02T05:00:50Z
**Complexity:** LOW
**Branch:** revamp-architecture
**Epic:** EPIC-ARCH-002 (D2.5)

---

## Business Goals

### Why This Matters

Epic 3 (Commands) will refactor all 9 existing commands from monolithic files (averaging 543 lines, with `design-model.md` at 1,345) down to 200-300 lines by replacing inline knowledge with skill references. Without an explicit mapping showing what knowledge moved where, Epic 3 implementers would need to rediscover the overlap between commands and skills — risking knowledge loss (removing content that wasn't captured in a skill) or bloat (leaving duplicated content).

This is the bridge artifact between Epic 2 (Skills) and Epic 3 (Commands).

### Success Criteria

- [ ] Extraction mapping exists for all 9 existing commands
- [ ] Every section in each command is accounted for (moved to skill OR stays in command)
- [ ] No knowledge is unaccounted for
- [ ] Epic 3 implementers can use the mapping as a removal checklist

### Priority

Final deliverable in EPIC-ARCH-002. D2.1-D2.4 are all complete. Blocks Epic 3 start.

---

## Problem Statement

### Current State

9 skills exist in `claude/skills/` (D2.1-D2.2 complete). Context window measurements confirm all skills fit (D2.4 complete). Skills are registered in the install pipeline (D2.3 complete). But there is no explicit record of which command sections were the source material for each skill, or what remains in commands after extraction.

### Desired Outcome

A single design artifact that maps every section in every command to either a skill (extracted) or a workflow category (stays). This enables Epic 3 to mechanically remove extracted knowledge and replace it with skill references.

---

## Scope

### In Scope

- Extraction mapping for all 9 existing commands: `design-model`, `implement-model`, `spec-model`, `plan-model`, `audit-models`, `research`, `manage-sources`, `backlog`, `onboard`
- Section-by-section accounting (section names, not line numbers — resilient to drift)
- For extracted sections: which skill absorbed the content and coverage assessment
- For remaining sections: categorization of what kind of workflow logic it is
- Cross-command summary showing which skills serve which commands
- Identification of any knowledge gaps (content not fully captured by any skill)

### Out of Scope

- Command refactoring (Epic 3)
- Skill content changes
- New commands (`/quick-model`, `/review-model`, etc.)
- Token count analysis (already done in D2.4)

### Edge Cases & Considerations

- Some sections have partial extraction (e.g., a section is 80% syntax rules extracted to `sysml-conventions` but 20% workflow-specific context). These need clear annotation.
- Some command sections contain knowledge that isn't captured by any current skill but is candidate for future extraction. These should be flagged but not block the mapping.

---

## Requirements

### Functional Requirements

> Requirements below are from epic D2.5 description unless marked [INFERRED].

1. **FR-1**: Produce a per-command table mapping sections to skills or "stays" disposition
2. **FR-2**: Account for every section in all 9 commands — no gaps
3. **FR-3**: For extracted sections, identify the absorbing skill and note partial vs full coverage
4. **FR-4**: [INFERRED] For remaining sections, categorize the type of workflow logic (orchestration, artifact template, user interaction, agent coordination)
5. **FR-5**: [INFERRED] Include a cross-command summary showing skill-to-command relationships (which commands reference which skills)
6. **FR-6**: [INFERRED] Flag any knowledge gaps — content that probably should be in a skill but isn't

---

## Acceptance Criteria

### Core Functionality

- [ ] `extraction-mapping.md` exists at `.project/active/d2.5-extraction-mapping/`
- [ ] All 9 commands have per-command mapping tables
- [ ] Every section in each command maps to either a skill or a "stays" category
- [ ] Partial extractions are annotated with coverage notes
- [ ] Cross-command summary table exists
- [ ] Knowledge gaps (if any) are identified and flagged for Epic 3 or future work

### Quality & Integration

- [ ] Section references use section names (not line numbers) for drift resilience
- [ ] Mapping is usable as an Epic 3 removal checklist
- [ ] No existing tests are affected (this is a design artifact only)

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_architecture-knowledge.md` (D2.5)
- **Skills:** `claude/skills/` (all 9 SKILL.md files — the extraction targets)
- **Commands:** `claude/commands/` (all 9 command files — the extraction sources)
- **Measurement:** `.project/active/d2.4-context-measurement/measurement-report.md`
- **Design:** `.project/active/d2.5-extraction-mapping/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design` (though given LOW complexity, design and implementation may be combined — the deliverable is a single markdown artifact).
