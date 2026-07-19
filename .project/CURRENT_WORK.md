# Current Work

**Last Updated**: 2026-07-18

---

## Active Work

### GAP-CLOSE Item 5: local partial wave certified; PR #11 pre-PR

The companion package/build/runtime/lock identity is `0.1.1`, paired with codegen's
`agentic-mbse>=0.1.1` floor. The shipped constraints guide now teaches all four v3 outcomes in both
its opening and detailed sections; a kept test rejects the retired three-outcome wording. The
rebuilt wheel contains the corrected guide, and the kept documentation test passes its recorded
Ruff and format checks.

The second re-audit's remaining guide contradictions are also corrected and pinned: BLOCK produces
one named L6 `ERROR` per blocked construct, and asserted predicates may be admitted, blocked, or
non-numerical. The rebuilt wheel guide matches source; sha256 is `160e7eb5…a8d4f`. The formatted
documentation regression passes, and the relevant guide/profile/L6 selection passes 119 tests.
The paired TEAx cure also moves explicit path expansion inside route-aware normalization and pins an
injected expansion `RuntimeError`; discovery passes 5 tests normally and under optimized Python,
and the established licensed environment passes the real SimKit lane 9/9.

The paired audit cures also pin exact anonymous warning bytes across live/relocated/snapshot routes
and normalize hostile TEAx discovery paths. The cross-repo audit certifies the local and in-scope
partial wave only. External `[GAP-CLOSE-F1-TEAX-NORMALIZATION]` remains open, so neither F1 nor the
full epic is complete.

The PR #11 candidate excludes the unrelated local modeling-orchestrator commit and orchestration
logs. Its fresh default suite passes 1,506 tests with 1 skipped and 5 deselected; changed-file Ruff,
format, targeted mypy, and diff checks are clean. The certified mixed local worktree suite remains
1,525 passed / 1 skipped / 33 deselected, and the codegen suite of record remains 2,516 / 26 / 9.
Repository-wide Ruff, format, and mypy still reproduce pre-existing debt outside the partial-wave
paths. All fixture manifests remain unchanged. Merge PR #11 before codegen PR #9. Do not close or
archive GAP-CLOSE while the external F1 dependency is open.

### GAP-CLOSE Item 4: Profile Default-Deny Totalization (certified in local partial wave)

Malformed codec-roundtripped xor/implies arities and contradictory equal-unit dimensions now
default-deny in executable-profile/v3. Numerical containment now promotes force, reason, and repair
message together. The only codegen Item 4 change is the coordinated conformance assertion.
Companion suite: 1,524 passed / 1 skipped / 33 deselected. Licensed codegen suite: 2,511 passed /
26 skipped / 9 deselected. The cross-repo GAP-CLOSE audit re-certifies this item. Plan:
`.project/active/gap-profile-totalization/plan.md`.

### CONSTRAINT-EXEC PR remediation (certified locally — paired compatibility pending)

A critical PR audit (`.project/research/20260714-064234_constraint-exec-pr-code-quality-audit.md`)
found nine defects on `constraint-exec-epic`; the remediation fixes those original findings. The
three gaps from the fresh certification pass are now implemented: malformed snapshot leaf facts
reach D-R3's named BLOCK through the public codec, serializers reject mutated wire tags, and the
defining module exports both public extractors. The fresh audit now certifies the local remediation:
`.project/active/constraint-exec-remediation/audit.md`. Normal suite: 1484 passed / 1 skipped /
33 deselected; targeted mypy and Ruff clean. Paired sysml-codegen profile/compiler compatibility is
the next stage.

## Remaining Active Items (Under Review)

| Item | Status | Decision Needed |
|------|--------|-----------------|
| `docling-deep-dive` | Phases 3-4 not started | Fold remaining work into new epic? |
| `pandoc-deep-dive` | Phases 5-6 not started | Close as research-complete? |
| `iteration-loop` | Spec draft only | Still relevant or shelve? |

---

## Recently Completed

### 2026-07-18: Orchestrate Modeling

- Added a thin, Task-led `/orchestrate-modeling` command for Standard and Epic model-building flows.
- Added the canonical modeling flow, explicit Epic audit scope, and supported `pm add-epic` registration.
- Verified 202 focused tests and the 1,504-test normal suite; closed without independent audit
  certification by owner decision.

### 2026-07-13: CONSTRAINT-EXEC Items 1–3 (epic closed, archived)
- Neutral constraint facts, ExpressionIR, and the executable profile all certified and archived
  to `.project/completed/20260713_{constraint-facts,expression-ir,executable-profile}/`.
- Canonical epic close-out + independent findings audit live in sysml-codegen
  `.project/completed/20260713_epic_constraint_execution*.md`; suite at close 1401/1.

### 2026-07-11: S1 Constraint Fact-Shape Learning Test

Live SysIDE 0.8.4 fixture matrix, golden JSON, and five kept tests now pin all four constraint
source forms, membership/polarity/ownership, actuals/defaults, inheritance/retyping, compound
expressions, and the equality type/unit gate. S1 passed with one explicit restriction: a
dimensioned quantity feature does not prove one exact runtime unit. Full suite: 1,295 passed,
1 skipped, 33 deselected. Findings:
`.project/completed/20260711_spike-constraint-fact-shapes/findings.md`.

### 2026-07-05: Web Source Capture + arXiv Extraction Pipeline (PR #6, merged)

Five standalone items shipped together on `webfetch-tools` → `main` and archived
to `.project/completed/20260705_*`:

- **Web Source Capture** — `extract <url>` → sanitized markdown (trafilatura +
  Pandoc fallback, CSS-hidden-content stripping, batch mode, `--save-source`).
- **Extraction Provenance** — universal frontmatter (source/backend/hash),
  `--no-frontmatter`.
- **Hash Consolidation** — single SHA256 `compute_source_hash` in `base.py`.
- **Web Extraction Quality** — arXiv HTML routed through Pandoc; figures
  downloaded locally; download failures surfaced as warnings. (Remaining
  non-arXiv-HTML-quality and fusion-tea re-extraction scope dropped at close.)
- **arXiv Latest-Version** — pinned ids/URLs resolve to newest version; served
  version recorded in `source`. **Certified** (`audit.md`), verified live
  (`1706.03762v1` → `v7`).

### 2026-03-29: arXiv HTML Routing Fix

arXiv HTML URLs (`arxiv.org/html/...`) extracted via `agentic-mbse extract <url>` were going through trafilatura, producing broken tables and lost equations. Fixed by detecting arXiv URLs and routing through the existing Pandoc pipeline from `pandoc_convert.py` (same one the PDF arXiv shortcut uses). ~50 lines in `web_backend.py`. Verified on arxiv-2411-06644: Table 3 now has all parameter names, scientific notation, and correct alignment.

### 2026-03-28–29: Web Source Capture

Added URL-to-markdown extraction to `agentic-mbse extract`. Trafilatura backend with Pandoc fallback, HTML sanitization (CSS-hidden content stripping), batch mode via `--urls-from`, frontmatter provenance, and `--save-source` flag. Four commits on `webfetch-tools` branch.

### 2026-03-01: Validation Stack Restructuring (8 → 6 Levels)

Restructured validation pyramid from 8 to 6 levels. Deleted stubs (L5 Semantic, L7 Architecture), merged into L6, renumbered. Post-audit fixed 7 stale references, added 8 L6 negative tests. 895 tests passing.

### 2026-02-27: EPIC-PDFV4-001 PDF Extraction Pipeline v4

Complete rewrite of extraction pipeline. Per-page quality-gated orchestration replacing v3 document-level approach. Includes:
- Research phase: 4 tool deep-dives (pymupdf4llm, Docling/GMFT, Claude vision, Pandoc) + pipeline experimentation + table image spike
- Implementation: Types/metrics/quality-gate → enhancement modules → pipeline orchestration/CLI → integration tests/cleanup
- Bug fixes: Claude invocation silent failures, `extract --check` with built-in test corpus
- All 4 epic items complete, 13 work items archived

### 2026-02-08: EPIC-PDFV3-001 PDF Extraction v3

Claude-powered document structure detection pipeline. 4-layer extraction, 12-doc corpus benchmarked.

---

## Session Notes

### 2026-03-01

- Archived 13 completed work items from `.project/active/` to `.project/completed/`
- Marked EPIC-PDFV4-001 as complete in epic file and backlog
- Updated CHANGELOG with v4 epic and validation restructuring entries
- Cleaned up BACKLOG.md: PDFV4-001 → completed, QUALREG-001 folded into new epic, DOCLING-001 promoted to P1
- 5 active items remain: pdf-skill-deployment, v4-output-quality-regressions, docling-deep-dive, pandoc-deep-dive, iteration-loop

### 2026-02-22

- Completed Phase 3 (Synthesize) of pymupdf4llm deep-dive
- Added Final Recommendation section to findings.md
- Fixed stale test `test_extract_passes_hdr_info_and_table_strategy`
- `uv sync` without `--extra dev` strips pytest — use `uv sync --extra dev`
