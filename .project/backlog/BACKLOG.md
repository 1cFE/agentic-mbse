# Product Backlog

Prioritized list of epics and features.

**Last Updated**: 2026-01-12

---

## Priority Legend

- **P0**: Critical - Blocking, do immediately
- **P1**: High - Important, do soon
- **P2**: Medium - Valuable, do when possible
- **P3**: Low - Nice to have, do eventually

---

## In Progress

| Epic | Priority | Status | Started | Notes |
|------|----------|--------|---------|-------|
| [None yet] | - | - | - | - |

---

## P0 - Critical Priority

### [EPIC-DOC-001] Documentation Discoverability Overhaul

**Priority**: P0
**Effort**: 3-5 days
**Status**: Ready

Users cannot discover standard library functions (sum, size, etc.) because our agent lacks the KerML spec and has no library quick reference. A team spent hours unable to find `NumericalFunctions::sum`. This is product-blocking.

**P0 Items** (do immediately):
- [ ] P0-1: Extract missing PDFs (KerML spec, Part1) (2-4 hours)
- [ ] P0-2: Create Standard Library Quick Reference (2-3 hours)
- [ ] P0-3: Update agent system prompt (1 hour)

**P1 Items** (do this week):
- [ ] P1-1: Generate library index automatically (4-6 hours)
- [ ] P1-2: Add validation agent for syntax checking (3-4 hours)
- [ ] P1-3: Add .kerml files to searchable corpus (2-3 hours)

**P2/P3 Items** (do when possible):
- [ ] P2-1: Split agent into specialists (1-2 days)
- [ ] P2-2: Improve PDF chunking with headers (4-6 hours)
- [ ] P3-1: Create documentation dashboard (1 day)

**File**: `epic_documentation-discoverability.md`

**Research**: `.project/research/20260112-064217_sysmlv2-agent-discoverability-failure.md`

---

## P1 - High Priority

*No additional epics yet*

---

## P2 - Medium Priority

*No epics yet*

---

## P3 - Low Priority

*No epics yet*

---

## Completed

| Epic | Completed | Duration | Notes |
|------|-----------|----------|-------|
| [None yet] | - | - | - |

---

## Ideas / Future Considerations

- Enhanced error message interpretation (suggest imports automatically)
- Integration tests for agent responses
- User feedback collection on agent accuracy
- Documentation versioning aligned with syside releases
