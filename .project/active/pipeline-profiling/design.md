# Design: Pipeline Profiling & Route Instrumentation

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-03-01 15:37 PST
**Complexity:** MEDIUM
**Branch:** doc-ingest-clean
**Commit:** 2af27b3

---

## Overview

Add per-step timing instrumentation and route distribution summaries to the extraction pipeline, exposed via a `--profile` CLI flag. A curated `profile_corpus/` provides diverse PDFs for benchmarking.

## Related Artifacts

- **Spec:** `.project/active/pipeline-profiling/spec.md`
- **Epic:** `.project/backlog/epic_pdf-extraction-improvements.md` (Item 3)
- **Dependency:** `.project/active/unified-image-output/` (Item 2)
- **Reference:** `src/agentic_mbse/extraction/check.py` — corpus/probe pattern

---

## Research Findings

### Pipeline Step Boundaries

`extract_pdf()` (`pipeline.py:275-566`) is a single ~290-line function with 11 clearly delimited steps via `# Step N:` comments:

| Step | Lines | What it does | Expected cost |
|------|-------|-------------|---------------|
| 1. arXiv shortcut | 299-305 | Pandoc early return | ~0s or 1-2s |
| 2. Base extraction | 307-318 | `extract_pages()` via pymupdf4llm | 1-3s |
| 3. Table detection | 320-326 | `detect_tables_ensemble()` | 1-5s |
| 3b. Table filter/enhance | 328-388 | Filter + Claude table enhancement | 0-10s (Claude) |
| 4. Quality gate | 390-407 | `assess_page()` per page + heading anomaly | <0.1s |
| 4b. GMFT xref | 408-417 | `_cross_reference_gmft()` | <0.01s |
| 5. Budget allocation | 419-427 | `allocate_budget()` | <0.01s |
| 6. Claude enhancement | 429-494 | `extract_page_with_claude()` per page | 5-30s (dominant) |
| 7. Route + merge | 496-534 | `route_page()` + apply decisions | <0.1s |
| 7b. Postprocess | 536-545 | Image persist + `_postprocess_final()` | <0.1s |
| 8. Assemble result | 547-566 | `compute_metrics()` + build `PipelineResult` | <0.01s |

### Early Return Paths

Two early returns produce incomplete profiles:

1. **arXiv shortcut** (`pipeline.py:302-305`): Returns `PipelineResult` directly after Step 1. Profile would only have `arxiv_shortcut` timing.
2. **Base extraction error** (`pipeline.py:312-318`): Returns error result after Step 2. Profile would have `arxiv_shortcut` (0.0) + `base_extraction` timing.

Both paths already set `elapsed_seconds` on the result; the profile just needs to be attached before return.

### Existing Patterns

- **Dataclasses in `types.py`**: All pipeline data types (`PipelineResult`, `PageDecision`, `PageAction`, `CostRecord`) live here. `PipelineProfile` follows this pattern. (`types.py:1-93`)
- **JSON serialization in `extract_cli.py`**: Existing `_decision_to_dict()` and `_cost_to_dict()` helpers at `extract_cli.py:146-164`. Profile serialization follows the same pattern.
- **Summary printing**: `_print_pipeline_summary()` at `extract_cli.py:167-184` formats per-document output. Profile summary table follows a similar approach.
- **Config threading**: `PipelineConfig` at `pipeline.py:146-158` already threads flags like `dry_run`, `enable_tables`, etc. Adding `profile: bool = False` is identical.
- **Test mocking**: Tests use `_patch_base()`, `_patch_tables()`, `_patch_claude_page()` helpers at `test_pipeline.py:89-106`. Profile tests use the same infrastructure.
- **Corpus pattern**: `check.py:115-120` has `get_check_corpus()` returning `list[Path]` from a sibling directory. Profile corpus follows the same discovery pattern.

### Timing Overhead Analysis

`time.perf_counter()` is ~50ns per call on Linux. With 11 steps (22 calls: start + stop), that's ~1.1 microseconds total — well under the <1ms threshold. However, the spec says "no timing calls in default path." The design uses conditional guards (`if prof:`) that evaluate to False when profiling is off — no `perf_counter()` calls occur.

---

## Proposed Design

### Component 1: `PipelineProfile` Dataclass

**Location:** `src/agentic_mbse/extraction/types.py`

**Purpose:** Store per-step wall-clock durations. Separate from `PipelineResult` per FR-2.

```python
@dataclass
class PipelineProfile:
    """Per-step wall-clock timing from a pipeline run."""
    arxiv_shortcut: float = 0.0
    base_extraction: float = 0.0
    table_detection: float = 0.0
    table_filter_enhance: float = 0.0
    quality_gate: float = 0.0
    gmft_xref: float = 0.0
    budget_allocation: float = 0.0
    claude_enhancement: float = 0.0
    route_merge: float = 0.0
    postprocess: float = 0.0
    assemble_result: float = 0.0
```

Named float fields rather than a `dict[str, float]` because:
- Auto-complete and type-checking catch typos
- Fields double as documentation of what steps exist
- `dataclasses.asdict()` produces clean JSON

**`PipelineResult` change:** Add `profile: PipelineProfile | None = None` field.

### Component 2: Timing Instrumentation in `extract_pdf()`

**Location:** `src/agentic_mbse/extraction/pipeline.py:275-566`

**Approach:** Inline conditional timing. Create `PipelineProfile` at function start when `config.profile` is True. Wrap each step with `if prof:` guards.

```python
def extract_pdf(pdf_path, config=None):
    if config is None:
        config = PipelineConfig()

    start_time = time.time()
    prof = PipelineProfile() if config.profile else None
    all_costs = []
    # ...

    # Step 1: arXiv shortcut
    if prof:
        _t = time.perf_counter()
    arxiv_result = _try_arxiv_shortcut(pdf_path, config)
    if prof:
        prof.arxiv_shortcut = time.perf_counter() - _t
    if arxiv_result is not None:
        arxiv_result.elapsed_seconds = time.time() - start_time
        arxiv_result.profile = prof  # attach partial profile
        return arxiv_result

    # Step 2: Base extraction
    if prof:
        _t = time.perf_counter()
    try:
        pages = extract_pages(...)
    except Exception as exc:
        if prof:
            prof.base_extraction = time.perf_counter() - _t
        return PipelineResult(..., profile=prof)
    if prof:
        prof.base_extraction = time.perf_counter() - _t

    # ... same pattern for remaining 9 steps (through assemble_result) ...
```

This adds 2 lines per step (~22 lines total for 11 steps). When `config.profile` is False, `prof` is `None` and all `if prof:` branches are skipped. Zero `perf_counter()` calls in the non-profiling path.

Step 8 (`assemble_result`) wraps `compute_metrics()` and the final `PipelineResult` assembly. This ensures `sum(all step timings) ≈ elapsed_seconds` with only framework overhead (variable assignments, `if` checks) in the gap.

**Why not a context manager?** A `with step_timer(prof, "step_name"):` approach would be cleaner visually, but: (a) context manager objects are created even when profiling is off unless we add a no-op variant, and (b) the step boundaries don't always align with clean `with` block scoping (early returns, exception handling). Inline conditionals match the existing code style better.

### Component 3: `PipelineConfig.profile` Field

**Location:** `src/agentic_mbse/extraction/pipeline.py:146-158`

Add one field:

```python
@dataclass
class PipelineConfig:
    # ... existing fields ...
    profile: bool = False
```

### Component 4: Route Distribution Helper

**Location:** New file `src/agentic_mbse/extraction/profile.py`

**Purpose:** Compute route distribution from decisions and format profiling output. Separate from `extract_cli.py` to keep the CLI module focused on argument parsing/dispatch (parallels `check.py`).

```python
def route_distribution(decisions: list[PageDecision]) -> dict[str, int]:
    """Count occurrences of each PageAction across decisions."""
    from collections import Counter
    return dict(Counter(d.action.value for d in decisions))
```

Returns `{"keep": 8, "claude_replace": 3, "gmft_replace": 1}` etc.

### Component 5: Profile Serialization

**Location:** `src/agentic_mbse/extraction/profile.py`

```python
def profile_to_dict(
    profile: PipelineProfile,
    decisions: list[PageDecision],
    page_count: int,
    elapsed_seconds: float,
) -> dict:
    """Serialize profile + route distribution to dict for JSON output."""
    from dataclasses import asdict
    return {
        "page_count": page_count,
        "elapsed_seconds": elapsed_seconds,
        "step_timing": asdict(profile),
        "route_distribution": route_distribution(decisions),
    }
```

Written to `profile.json` by `cmd_extract()` when `--profile` is active.

### Component 6: Summary Table Formatting

**Location:** `src/agentic_mbse/extraction/profile.py`

**Purpose:** Print a multi-document profile summary table to stderr.

The table collapses the 11 timing steps into 5 display columns for readability, and collapses 6 route actions into 3 display columns:

| Display Column | Source Steps |
|---------------|-------------|
| **Base** | `arxiv_shortcut` + `base_extraction` (mutually exclusive: arXiv shortcut replaces base extraction) |
| **Tables** | `table_detection` + `table_filter_enhance` |
| **Gate** | `quality_gate` + `gmft_xref` + `budget_allocation` |
| **Claude** | `claude_enhancement` |
| **Post** | `route_merge` + `postprocess` + `assemble_result` |

| Route Column | Source Actions |
|-------------|---------------|
| **KEEP** | `keep` |
| **CLAUDE** | `claude_replace` |
| **GMFT** | `gmft_replace` + `gmft_append` |

(`strip_false` + `strip_broken` are rare edge cases; they appear in `profile.json` but not the summary table. If present, they're grouped under KEEP for display.)

```python
@dataclass
class ProfileEntry:
    """One row in the profile summary table."""
    document: str
    pages: int
    route_dist: dict[str, int]
    elapsed: float
    profile: PipelineProfile


def format_profile_table(entries: list[ProfileEntry]) -> str:
    """Format profile entries as a human-readable table."""
    ...
```

Output format (matching the epic):

```
Pipeline Profile Summary
════════════════════════════════════════════════════════════════════════════════

Document                  Pages  KEEP  CLAUDE  GMFT  Time(s)  Base  Tables  Gate  Claude  Post
────────────────────────  ─────  ────  ──────  ────  ───────  ────  ──────  ────  ──────  ────
araiinejad_2024              12     3       6     3    14.2   1.1     2.3   0.1     9.8   0.2
schulte_1978                  8     8       0     0     3.1   2.8     0.1   0.1     0.0   0.1
────────────────────────  ─────  ────  ──────  ────  ───────  ────  ──────  ────  ──────  ────
Total                        20    11       6     3    17.3   3.9     2.4   0.2     9.8   0.3
```

A totals row sums all columns, providing the corpus-wide view.

### Component 7: CLI Integration

**Location:** `src/agentic_mbse/cli/extract_cli.py`

**Changes:**

1. **Add `--profile` flag** in `register_extract_subcommand()`:
   ```python
   p.add_argument(
       "--profile",
       action="store_true",
       help="Enable per-step timing and route distribution profiling",
   )
   ```

2. **Thread to PipelineConfig** in `cmd_extract()`:
   ```python
   config = PipelineConfig(
       # ... existing fields ...
       profile=args.profile,
   )
   ```

3. **Write `profile.json`** after pipeline completes (alongside `decisions.json`):
   ```python
   if args.profile and result.profile:
       from agentic_mbse.extraction.profile import profile_to_dict
       profile_data = profile_to_dict(
           result.profile, result.decisions,
           page_count=len(result.decisions),
           elapsed_seconds=result.elapsed_seconds,
       )
       (output_dir / "profile.json").write_text(
           json.dumps(profile_data, indent=2)
       )
   ```

4. **Collect profile entries** across documents and **print summary table** to stderr after the main loop:
   ```python
   # After all documents processed:
   if args.profile and profile_entries:
       from agentic_mbse.extraction.profile import format_profile_table
       print(format_profile_table(profile_entries), file=sys.stderr)
   ```

### Component 8: Profile Corpus

**Location:** `profile_corpus/` (repository root)

**Why repo root, not in-package:** The check corpus (`src/agentic_mbse/extraction/check_corpus/`) is shipped in the package because `--check` needs it at runtime. The profile corpus is benchmark data for developers — it's not needed by end users and PDFs may be large (30+ pages). Repo root keeps it out of the installed package.

**Target diversity (~10 PDFs):**

| Slot | Type | Characteristics | Target Pages |
|------|------|----------------|--------------|
| 1 | Clean born-digital | Modern paper, clean text, few tables | 8-12 |
| 2 | Two-column academic | Standard IEEE/ACM format | 10-15 |
| 3 | Scanned/degraded | Older document, OCR artifacts | 5-10 |
| 4 | Table-heavy | Multiple complex data tables per page | 5-10 |
| 5 | Equation-heavy | Dense mathematical content, display equations | 8-15 |
| 6 | Short document | Simple, few pages | 2-3 |
| 7 | Long document | Many pages, varied content | 30+ |
| 8 | Mixed content | Figures, tables, equations, text | 10-15 |
| 9 | Report/technical manual | Wide tables, appendices | 15-25 |
| 10 | Minimal/edge case | Nearly empty, single page, or unusual layout | 1-3 |

**Discovery function** in `profile.py`:
```python
def get_profile_corpus() -> list[Path]:
    """Return paths to profile corpus PDFs.

    Dev-only: walks 4 parents up from this file to reach repo root.
    Assumes: profile.py is at src/agentic_mbse/extraction/profile.py.
    Returns [] if the directory doesn't exist (e.g., installed package).
    """
    # 4 levels: extraction/ → agentic_mbse/ → src/ → repo_root/
    corpus_dir = Path(__file__).parent.parent.parent.parent / "profile_corpus"
    if not corpus_dir.exists():
        return []
    return sorted(p for p in corpus_dir.iterdir() if p.suffix == ".pdf")
```

Note: This uses a relative path from the source file to repo root. This works in development but not from an installed package — which is fine, since profiling is a developer activity. The depth assumption is documented in the docstring so future readers can update it if the module moves.

**Corpus size policy:** Maximum 5MB per PDF file. This keeps the total corpus under ~50MB without requiring git-lfs. If a slot requires a larger document, use a truncated version or document acquisition instructions in `profile_corpus/README.md` instead of committing the file.

### Data Flow

```
CLI (--profile)
  │
  ├─ PipelineConfig(profile=True)
  │     │
  │     └─ extract_pdf()
  │          │
  │          ├─ prof = PipelineProfile()
  │          ├─ Step 1: time + _try_arxiv_shortcut() → prof.arxiv_shortcut
  │          ├─ Step 2: time + extract_pages() → prof.base_extraction
  │          ├─ ... (9 more steps through assemble_result)
  │          │
  │          └─ PipelineResult(profile=prof)
  │
  ├─ profile_to_dict() → profile.json (per document)
  ├─ route_distribution() → included in profile.json
  │
  └─ format_profile_table() → stderr (after all documents)
```

---

## Potential Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Profile corpus PDFs are too large for git | Medium | Repo bloat | 5MB per-file limit enforced by convention; total corpus <50MB. No git-lfs needed. Larger specimens get acquisition instructions instead. |
| Timing noise on short steps (<10ms) | Low | Misleading data | Document that sub-10ms steps have high relative variance; `perf_counter()` is sufficient |
| `profile_corpus/` path resolution from installed package | Low | `get_profile_corpus()` returns empty | Only used in dev; document this. Could add CLI `--corpus` override if needed later. |
| Inline `if prof:` clutter in `extract_pdf()` | Low | Readability | ~20 lines added to a 290-line function. Each is a 1-line conditional at a step boundary, next to existing comments. |

---

## Integration Strategy

- **No changes to existing behavior**: When `--profile` is absent, `config.profile` defaults to `False`, `prof` is `None`, all timing branches are skipped, `PipelineResult.profile` is `None`. Byte-identical output.
- **Complements `--check`**: `--check` probes component availability; `--profile` measures full pipeline performance. Different purposes, different corpora.
- **Complements `--dry-run`**: `--dry-run --profile` shows the cost of assessment (gate, table detection) without Claude enhancement timing.
- **Future extension**: When equation detection (Item 4) adds a new pipeline step, adding one field to `PipelineProfile` and two `if prof:` lines in `extract_pdf()` is trivial.

---

## Validation Approach

### Unit Tests (`tests/test_pipeline.py`)

1. **Profile populated when enabled**: Run `extract_pdf()` with mocked steps and `config.profile=True`. Assert `result.profile` is not None and all 11 step fields are `>= 0.0`. Verify `sum(all fields) ≈ result.elapsed_seconds` (within reasonable tolerance for framework overhead).
2. **Profile None when disabled**: Run `extract_pdf()` with `config.profile=False`. Assert `result.profile is None`.
3. **ArXiv early return has partial profile**: Mock arXiv shortcut to succeed. Assert `result.profile.arxiv_shortcut > 0` and other fields are `0.0`.
4. **Error early return has partial profile**: Mock `extract_pages()` to raise. Assert `result.profile.base_extraction > 0`.
5. **Route distribution**: Create synthetic decisions, assert `route_distribution()` returns correct counts.

### Unit Tests (`tests/test_profile.py`)

1. **`profile_to_dict()` serialization**: Verify output dict has expected keys and types.
2. **`format_profile_table()` formatting**: Verify table output with known entries, check column alignment.
3. **`route_distribution()` edge cases**: Empty decisions, all same action, mixed actions.

### Integration Test (optional, corpus-dependent)

Run `agentic-mbse extract profile_corpus/ --profile --budget 0 --dry-run` and verify:
- `profile.json` written for each document
- Summary table printed to stderr
- All step timing fields present

---

**Next Steps:** After approval, proceed to `/_my_plan`
