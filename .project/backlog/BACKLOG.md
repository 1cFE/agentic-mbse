# Product Backlog

Prioritized list of epics and features.

**Last Updated**: 2026-01-13

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
| EPIC-DOC-001 | P0 | In Progress | 2026-01-12 | PDF extraction done, indexing done, agent prompt update next |

---

## P0 - Critical Priority

### [EPIC-DOC-001] Documentation Discoverability Overhaul

**Priority**: P0
**Effort**: 3-5 days
**Status**: In Progress

Users cannot discover standard library functions (sum, size, etc.) because our agent lacks the KerML spec and has no library quick reference. A team spent hours unable to find `NumericalFunctions::sum`. This is product-blocking.

**Completed**:
- [x] P0-1: Extract missing PDFs (KerML spec, Part1)
- [x] P0-2: Generate section indexes with AI summaries (INDEX.md approach)
  - Scripts: `scripts/generate_index.py`, `scripts/read_section.py`
  - KerML: 111 sections at depth-3
  - Part1: 52 sections at depth-2 (different header format)

**Next** (do this week):
- [ ] P0-3: Update agent system prompt (1 hour) - use INDEX.md-first strategy
- [ ] P1-1: Add validation agent for syntax checking (3-4 hours)
- [ ] P1-2: Create Standard Library Quick Reference (2-3 hours)

**Later**:
- [ ] P1-3: Add .kerml files to searchable corpus (2-3 hours)
- [ ] P2-1: Index remaining specs (Part2, Part3) (1-2 hours)
- [ ] P2-2: Investigate PDF extraction header consistency (see below)
- [ ] P3-1: Create documentation dashboard (1 day)

**File**: `epic_documentation-discoverability.md`

**Research**:
- `.project/research/20260112-064217_sysmlv2-agent-discoverability-failure.md`
- `project/research/20260112-222249_chunking-indexing-strategy.md`

---

## P1 - High Priority

*No additional epics yet*

---

## P2 - Medium Priority

### [TASK-PDF-001] Investigate PDF Extraction Header Consistency

**Priority**: P2
**Effort**: 2-4 hours
**Status**: Ready

**Problem**: Different PDF extraction tools produce different markdown header formats:
- KerML (via Docling?): `## 7.2.1 Title` - clean, enables depth-3 indexing (111 sections)
- Part1 (via PyMuPDF?): `##### **7 Title**` for depth-2, `**7.2.1 Title**` (bold only) for depth-3
  - This limits us to depth-2 indexing (52 sections)

**Goal**: Achieve consistent `## {number} Title` format across all specs to enable depth-3 indexing.

**Investigation tasks**:
- [ ] Identify which tool was used for each extraction (check m-scout processing logs)
- [ ] Compare Docling vs PyMuPDF output on same PDF
- [ ] Check if either tool has options to normalize header format
- [ ] Document recommended extraction settings for consistent output
- [ ] Re-extract Part1 if better format is achievable

**Tools to investigate**:
- `/home/reid/m-scout/tools/pdf-processing/` - current extraction scripts
- Docling: `pip install docling` - may have better structure preservation
- PyMuPDF: `pip install pymupdf` - faster but less structure-aware

**Success criteria**:
- All spec documents use `## {number} Title` format
- `generate_index.py --depth 3` works on all specs
- Consistent 100+ sections indexed per major spec

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
- Post-processing script to normalize PDF extraction headers (if tool options insufficient)
- Support for `**7.2.1 Title**` bold-only headers in generate_index.py (alternative to re-extraction)
