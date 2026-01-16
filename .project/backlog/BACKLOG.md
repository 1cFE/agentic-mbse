# Product Backlog

Prioritized list of epics and features.

**Last Updated**: 2026-01-15 (archived completed P1 items)

---

## Priority Legend

- **P0**: Critical - Blocking, do immediately
- **P1**: High - Important, do soon
- **P2**: Medium - Valuable, do when possible
- **P3**: Low - Nice to have, do eventually

---

## In Progress

*No epics currently in progress*

---

## P0 - Critical Priority

*No P0 epics*

---

## P1 - High Priority

*All P1 items completed - see Completed section below*

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

| Item | Completed | Duration | Notes |
|------|-----------|----------|-------|
| EPIC-DOC-001: Documentation Discoverability | 2026-01-13 | 2 days | INDEX.md approach, 4 specialized agents, stdlib sync |
| ITEM-BACKPORT-001: Backport fusion-tea Patterns | 2026-01-13 | 0.5 days | Added 3 validated patterns to MODELING_GUIDE.md.template |
| ITEM-GUIDE-001: Progressive Disclosure Restructure | 2026-01-15 | 1 day | MODELING_GUIDE.md reduced from 1497→205 lines, 12 pattern docs created |
| ITEM-DEVMODE-001: Development Mode (--dev flag) | 2026-01-15 | 1 day | `agentic-mbse init --dev` creates symlinks for tool-owned files |
| ITEM-LEARNING-001: Learning Feedback Loop | 2026-01-15 | 1 day | `/record-learning` skill + RAW_LEARNINGS.md template |

---

## Ideas / Future Considerations

**Agent Improvements**:
- Enhanced error message interpretation (suggest imports automatically)
- Integration tests for agent responses
- Agent self-correction patterns (try → fail → research → retry)

**Learning System Extensions** (after ITEM-LEARNING-001):
- Automatic categorization of learnings via LLM
- Similarity detection to avoid duplicate learnings
- Periodic digest generation from RAW_LEARNINGS.md
- Hook-based auto-capture on debugging success

**Documentation**:
- Documentation versioning aligned with syside releases
- Post-processing script to normalize PDF extraction headers
- Support for `**7.2.1 Title**` bold-only headers in generate_index.py

**Developer Experience**:
- Watch mode for dev symlinks (auto-reload on changes)
- `agentic-mbse diff` command to compare project vs templates
- Migration tool for updating user-owned files with new features
