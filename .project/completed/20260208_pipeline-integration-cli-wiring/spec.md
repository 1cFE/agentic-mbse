# Spec: Pipeline Integration + CLI Wiring

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-08 17:05 UTC
**Complexity:** MEDIUM
**Branch:** pdf-extract
**Epic:** EPIC-PDFV3-001, Item 3

---

## Business Goals

### Why This Matters

The `claude_structure.py` module (684 lines, 50 tests) is complete but has zero effect on users because it's not wired into the extraction pipeline. Currently `--enhance` only triggers table/equation AI repair — it doesn't address the structural heading problem that causes 0/5 usable indexes on unseen documents. This integration is the critical path step between core implementation (Item 2, done) and benchmarking (Item 4).

### Success Criteria

- [ ] `--enhance` on any PDF triggers L3 structural pass (when gated in) followed by L4 AI repair
- [ ] `--structure-only` runs L3 without L4
- [ ] Default mode (no flags) produces identical output to current pipeline
- [ ] INDEX generation always runs after L3 when both `--enhance` and `--index` are set

### Priority

P1 — on the critical path (Item 2 → **Item 3** → Item 4). Unblocks corpus benchmarking.

---

## Problem Statement

### Current State

`extract_cli.py` (383 lines) pipeline:
1. Backend extraction → `_run_extraction()`
2. `write_summary()`
3. `detect_problems()` from quality_gates
4. Layer 2: `enhance_tables()` — if not `--no-tables`
5. Layer 3: `repair_document()` from ai_repair — if `--enhance`
6. Index generation — if `--index`

The Claude structural pass (`claude_structure.py`) exists but is not called anywhere.

### Desired Outcome

```
L1: pymupdf + postprocess (unchanged)
L2: GMFT table enhancement (unchanged)
L3: Claude structural pass (NEW — claude_structure.py)
  - needs_claude_structure() gate
  - enhance_structure() orchestrator
L4: AI quality repair (EXISTING ai_repair.py, renumbered)
  - Runs on remaining RepairRequests from quality_gates
  - Cross-validation preserved
Index generation: After all layers
```

---

## Scope

### In Scope

- Wire `claude_structure.enhance_structure()` into the pipeline between GMFT and AI repair
- Gate L3 behind `needs_claude_structure()` heuristic
- Add `--structure-only` CLI flag (run L3, skip L4)
- Add `--model` CLI flag (override Claude model for both Phase A and Phase B; values: `opus`, `sonnet`, `haiku`)
- Enforce INDEX generation runs after L3 completes
- Log what L3 did (style detected, headers inserted/skipped, warnings)
- Mocked integration tests for the new pipeline ordering
- Update `--enhance` to trigger both L3 and L4

### Out of Scope

- `--fast` flag (no value added — default behavior already skips L3/L4)
- Cost estimation or confirmation prompts (all users on Claude Code Max plan)
- Changes to `ai_repair.py` internals
- Changes to `quality_gates.py` or `postprocess.py`
- Changes to GMFT table extraction
- New CLI subcommands
- Documents over 200 pages

### Edge Cases & Considerations

- `--enhance` without `--structure-only`: runs both L3 and L4
- `--structure-only` without `--enhance`: SHOULD imply `--enhance` behavior for L3 only (don't require both flags)
- `needs_claude_structure()` returns False: L3 is skipped even with `--enhance`, log the reason
- L3 fails (malformed JSON, subprocess error): fall back gracefully, continue to L4 with warning
- `--enhance --no-tables`: skip L2, still run L3 and L4
- `--model` without `--enhance` or `--structure-only`: no effect (no Claude calls made)

---

## Requirements

### Functional Requirements

> Requirements below are from user's request and epic unless marked [INFERRED].

1. **FR-1**: `--enhance` MUST trigger L3 (structural pass gated by `needs_claude_structure()`) followed by L4 (AI repair on remaining quality problems), in that order
2. **FR-2**: `--structure-only` MUST run L3 without L4. It MUST NOT require `--enhance` to also be set
3. **FR-3**: `--model {opus,sonnet,haiku}` MUST override the Claude model for both Phase A (style detection) and Phase B (structural repair). Default: haiku for Phase A, sonnet for Phase B (per epic design decision D7)
4. **FR-4**: [INFERRED] When `--model` is provided, both Phase A and Phase B use the same specified model, overriding the default split
5. **FR-5**: INDEX generation (`--index`) MUST run after L3 completes when both `--enhance`/`--structure-only` and `--index` are set
6. **FR-6**: When `needs_claude_structure()` returns False, L3 MUST be skipped even with `--enhance`, and a log message SHOULD explain why
7. **FR-7**: L3 MUST use the `-p` (headless) method for Claude CLI invocation, consistent with existing `ai_repair.py` patterns
8. **FR-8**: Pipeline MUST log L3 results: document style detected, headers inserted count, headers skipped count, running headers stripped count, and any warnings
9. **FR-9**: L3 failure (malformed JSON, subprocess error) MUST NOT abort the pipeline; it MUST fall back gracefully and continue to L4 with a warning
10. **FR-10**: Default mode (no `--enhance`, no `--structure-only`) MUST produce identical output to the current pipeline — zero behavioral change

---

## Acceptance Criteria

### Core Functionality

- [x] `--enhance` on a document where `needs_claude_structure()` returns True triggers style detection → structural repair → AI quality repair (in order)
- [x] `--enhance` on a document where `needs_claude_structure()` returns False skips L3, proceeds to L4, logs skip reason
- [x] `--structure-only` runs L3 without L4
- [x] `--structure-only` does not require `--enhance` to be set
- [x] `--model sonnet` overrides both Phase A and Phase B to use sonnet
- [x] `--index` runs after L3 when combined with `--enhance`
- [x] Default mode (no enhancement flags) produces identical output to current pipeline
- [x] L3 failure → warning printed, pipeline continues to L4

### Quality & Integration

- [x] Existing tests continue to pass (all 855)
- [x] New mocked integration test: full pipeline with `--enhance`, mocked Claude returns, verifies L3→L4 ordering
- [x] New test: `--structure-only` runs L3 only
- [x] New test: `--model` flag passed through to `enhance_structure()`
- [x] New test: `needs_claude_structure()` gate skip path
- [x] New test: L3 failure graceful fallback

---

## Integration Details

### `claude_structure.py` Public API (from Item 2)

```python
# Gate heuristic
needs_claude_structure(md: str) -> bool

# Full orchestrator — returns (modified_md, metadata_dict)
enhance_structure(
    md: str,
    pdf_path: Path,
    output_dir: Path,
    phase_a_model: str = "haiku",
    phase_b_model: str = "sonnet",
) -> tuple[str, dict]
```

Metadata dict shape:
```python
{
    "phase_a": DocumentStyle.to_dict(),  # or None
    "phase_b": None,                      # or repair details
    "headers_inserted": int,
    "headers_skipped": int,
    "warnings": list[str],
}
```

### Integration Point in `extract_cli.py`

Insert between current L2 (GMFT, lines ~233-250) and current L3/future L4 (ai_repair, lines ~252-269):

```python
# L3: Claude structural pass
if (enhance or structure_only) and needs_claude_structure(md_text):
    phase_a_model = model or "haiku"
    phase_b_model = model or "sonnet"
    md_text, struct_meta = enhance_structure(
        md_text, doc, output_dir,
        phase_a_model=phase_a_model,
        phase_b_model=phase_b_model,
    )
    # log results, store metadata
elif enhance or structure_only:
    # log: skipping structural pass, document already well-structured

# L4: AI quality repair (skip if --structure-only)
if enhance and not structure_only and remaining_problems:
    md_text, repair_meta = repair_document(...)
```

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_pdf-extraction-v3.md` (Item 3)
- **Item 2 (dependency):** `src/agentic_mbse/extraction/claude_structure.py` + `tests/test_claude_structure.py`
- **Design:** `.project/active/pipeline-integration-cli-wiring/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
