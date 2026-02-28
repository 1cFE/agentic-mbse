# Design: v4 Claude Invocation Fix + Pipeline Observability

**Status:** Complete
**Created:** 2026-02-27
**Completed:** 2026-02-27
**Branch:** doc-ingest-clean
**Parent:** EPIC-PDFV4-001

---

## 1. Problem Summary

Three related problems, one root cause:

1. **`invoke_claude()` is broken** — Claude Code's `--output-format json` now returns a JSON array of typed events, not a single JSON object. `json.loads()` succeeds (returns a `list`), then `response.get("result", "")` throws `AttributeError` because lists don't have `.get()`. Every Claude call fails.

2. **All Claude failures are invisible** — Every failure path in the pipeline logs at `debug` level. The CLI summary line shows `ok` with `$0.000` cost. `decisions.json` records intent (`claude_replace`) not reality (fell back to `keep`). The user has no indication that Claude was requested but never delivered.

3. **No pre-flight validation** — The pipeline attempts subprocess calls to `claude` without first checking whether the binary exists, wasting time on doomed calls and producing confusing silent failures.

---

## 2. Root Cause Analysis

### 2.1 The JSON Parsing Bug

**When experiments ran** (2026-02-22/23), `claude -p --output-format json` apparently returned a single JSON object:

```json
{"result": "...", "total_cost_usd": 0.078, "usage": {...}, "model": "..."}
```

**Now** (2026-02-27, Claude Code 2.1.62), it returns a JSON array of typed events:

```json
[
  {"type": "system", "subtype": "init", ...},
  {"type": "assistant", "message": {...}},
  {"type": "rate_limit_event", ...},
  {"type": "result", "subtype": "success", "result": "...", "total_cost_usd": 0.015, "usage": {...}}
]
```

The experiment scripts (`tests/corpus/claude_extract_experiment.py:157`, `tests/corpus/pipelines/h3_pymupdf_claude_eq.py:80`) have identical parsing code to the production `invoke_claude()`. They worked at the time. The format changed between experiment execution and production deployment.

**Failure chain:**
1. `json.loads(result.stdout)` → returns a `list` (succeeds)
2. `response.get("result", "")` → `AttributeError: 'list' object has no attribute 'get'`
3. `except Exception` in pipeline.py:331 catches it
4. `logger.debug(...)` — invisible
5. `claude_results` stays empty
6. Merge step falls through to `page.markdown` (original pymupdf4llm)
7. `decisions.json` still says `claude_replace`
8. No `cost.json` written (empty cost list)
9. User sees `ok` in CLI summary

### 2.2 The Logging Gap

Current log levels in `pipeline.py`:

| Event | Current Level | Should Be |
|-------|--------------|-----------|
| Table enhancement failed (line 258) | `debug` | `warning` |
| Claude output rejected (line 330) | `debug` | `warning` |
| Claude page enhancement failed (line 332) | `debug` | `warning` |
| Table detection failed (line 166) | `debug` | `warning` |

Compare with `tables.py`, which uses `logger.warning` for all detection/extraction failures. The inconsistency means table detector failures are visible but Claude failures are hidden.

### 2.3 Decision Inaccuracy

`route_page()` in `quality_gate.py:343` returns `PageAction.CLAUDE_REPLACE` based on the quality gate assessment and budget allocation. This is the **intended** action. But when Claude fails or is unavailable, the merge step at `pipeline.py:358-370` silently falls back:

```python
if decision.action == PageAction.CLAUDE_REPLACE and pnum in claude_results:
    merged_pages.append(claude_results[pnum])
# ...
else:
    # KEEP or fallback (CLAUDE_REPLACE without result, etc.)
    merged_pages.append(page.markdown)
```

The decision object is never updated. `decisions.json` records `claude_replace` for pages that received no Claude treatment.

---

## 3. Design

### 3.1 Fix `invoke_claude()` JSON Parsing

**File:** `src/agentic_mbse/extraction/claude_enhance.py`

`invoke_claude()` MUST handle both the old format (single dict) and the new format (array of typed events). The function's contract — return a `dict` with `result`, `total_cost_usd`, `usage`, `model` keys — stays the same. Only the internal parsing changes.

**Approach:** After `json.loads()`, check the type. If `list`, find the `{"type": "result"}` entry. If `dict`, use as-is (backward compat).

**Extraction from result event:** The result event contains:
- `result` — the text output (same key name, same semantics)
- `total_cost_usd` — total cost
- `usage` — token counts (slightly different nesting than before)
- `modelUsage` — per-model breakdown including `costUSD`

The `model` field is NOT on the result event — it's on the init event. But the caller already passes the model name, and `CostRecord` falls back to the passed model. So we can extract model from `modelUsage` keys if available, or leave it to the caller.

**Error cases to handle:**
- No `{"type": "result"}` entry in the array → `RuntimeError`
- `result` event has `"is_error": true` → `RuntimeError` with the error content
- Array is empty → `RuntimeError`

**Test update:** The existing tests mock `invoke_claude` at the call site, so they don't test the parsing itself. Add a unit test for `invoke_claude`'s parsing logic with the actual JSON array format, using a mock for `subprocess.run`.

### 3.2 Pre-flight Claude Availability Check

**File:** `src/agentic_mbse/extraction/pipeline.py`

Before the Claude enhancement loop (Step 6), if `claude_pages` is non-empty and Claude is enabled and not dry-run:

1. Check `shutil.which("claude")`
2. If not found: `logger.warning(...)`, set `claude_pages` to empty set, skip the loop

This avoids N doomed subprocess calls (one per page) and gives the user a single clear warning.

**Also applies to Step 3b** (table enhancement loop) — same check before attempting `enhance_table_with_claude`.

Since both loops share the same Claude binary, do the check once and store in a local `claude_available: bool`.

### 3.3 Escalate Claude Failure Logging

**File:** `src/agentic_mbse/extraction/pipeline.py`

Change log levels:

| Line | Current | New | Message |
|------|---------|-----|---------|
| 258 | `debug` | `warning` | Table enhancement failed |
| 330 | `debug` | `warning` | Claude output rejected |
| 332 | `debug` | `warning` | Claude page enhancement failed |
| 166 | `debug` | `warning` | Table detection failed |

These are all recoverable failures (pipeline continues), but they represent lost quality that the user should know about.

### 3.4 Post-Loop Claude Summary

**File:** `src/agentic_mbse/extraction/pipeline.py`

After the Claude enhancement loop (Step 6), before Step 7:

```python
if claude_pages:
    succeeded = len(claude_results)
    total = len(claude_pages)
    if succeeded == total:
        logger.info("Claude enhancement: %d/%d pages", succeeded, total)
    else:
        failed_pages = sorted(claude_pages - set(claude_results.keys()))
        logger.warning(
            "Claude enhancement: %d/%d pages succeeded (pages %s failed)",
            succeeded, total, failed_pages,
        )
```

### 3.5 Decision Truthfulness

**File:** `src/agentic_mbse/extraction/pipeline.py`

In the merge step (Step 7), when `CLAUDE_REPLACE` falls through because the page is not in `claude_results`:

```python
if decision.action == PageAction.CLAUDE_REPLACE and pnum not in claude_results:
    decision.action = PageAction.KEEP
    decision.reasons.append("Claude enhancement unavailable — kept original")
```

This makes `decisions.json` reflect what actually happened, not what was intended. Downstream consumers (users reading decisions.json, integration tests checking actions) get truthful data.

### 3.6 CLI Summary Warning

**File:** `src/agentic_mbse/cli/extract_cli.py`

Add Claude enhancement stats to `PipelineResult` so the CLI can report them.

**File:** `src/agentic_mbse/extraction/types.py`

Add to `PipelineResult`:
```python
claude_pages_intended: int = 0
claude_pages_succeeded: int = 0
```

Set these in pipeline.py after Step 6. Then in `_print_pipeline_summary`:

```python
if result.claude_pages_intended > 0 and result.claude_pages_succeeded < result.claude_pages_intended:
    print(
        f"        ! Claude: {result.claude_pages_succeeded}/"
        f"{result.claude_pages_intended} pages enhanced"
    )
```

---

## 4. Files Changed

| File | Change |
|------|--------|
| `src/agentic_mbse/extraction/claude_enhance.py` | Fix JSON array parsing in `invoke_claude()` |
| `src/agentic_mbse/extraction/pipeline.py` | Pre-flight check, log escalation, post-loop summary, decision truthfulness, set claude stats on result |
| `src/agentic_mbse/extraction/types.py` | Add `claude_pages_intended` / `claude_pages_succeeded` to `PipelineResult` |
| `src/agentic_mbse/cli/extract_cli.py` | Surface Claude failure in `_print_pipeline_summary` |
| `tests/test_claude_enhance.py` | Add test for JSON array parsing |
| `tests/test_pipeline.py` | Update tests for decision truthfulness, add test for pre-flight check |

Also update experiment scripts (not blocking, these are research code):
| `tests/corpus/claude_extract_experiment.py` | Same JSON array fix |
| `tests/corpus/pipelines/h3_pymupdf_claude_eq.py` | Same JSON array fix |
| `tests/corpus/pipelines/track1_cropped_extraction.py` | Same JSON array fix |
| `tests/corpus/pipelines/track3_sequential_review.py` | Same JSON array fix |

---

## 5. Test Strategy

### 5.1 Unit: `invoke_claude()` JSON Parsing

Test with mock `subprocess.run` returning the actual JSON array format captured from Claude Code 2.1.62. Verify:
- Returns a dict with `result`, `total_cost_usd`, `usage` keys
- Handles the old single-dict format (backward compat)
- Raises `RuntimeError` on `is_error: true`
- Raises `RuntimeError` on empty array
- Raises `RuntimeError` on no result event

### 5.2 Unit: Pre-flight Check

Mock `shutil.which` returning `None`. Verify:
- `logger.warning` called with page count
- `claude_results` is empty after Step 6
- No subprocess calls attempted

### 5.3 Unit: Decision Truthfulness

Existing pipeline tests mock Claude to succeed. Add a test where Claude is unavailable (mock `shutil.which` → None):
- Pages routed to `CLAUDE_REPLACE` by quality gate
- After merge, those decisions have `action == PageAction.KEEP`
- Reasons include "Claude enhancement unavailable"

### 5.4 Unit: CLI Summary

Mock a `PipelineResult` with `claude_pages_intended=3, claude_pages_succeeded=0`. Verify the warning line is printed.

### 5.5 Integration (manual)

Re-run extraction on the TEA cost analysis PDF with the fix. Verify:
- `cost.json` is written (Claude was actually called)
- `decisions.json` shows `claude_replace` for pages where Claude succeeded
- Equations on pages 1, 4, 5 are clean LaTeX, not garbled Unicode
- CLI summary shows cost > $0

---

## 6. Risk

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Claude Code output format changes again | Medium | Medium | Parse defensively — check type, find result event by `type` key, not by array index. Add the actual JSON fixture to tests so future format changes are caught. |
| Old-format Claude Code still in use somewhere | Low | Low | Handle both formats (dict or array). |
| `shutil.which("claude")` succeeds but Claude still fails (auth, network) | Low | Low | Pre-flight only catches the binary-missing case. Per-call failures are caught by the existing try/except + the new warning-level logging. |

---

## 7. Implementation Status

All sections implemented and tested on branch `doc-ingest-clean`:

| Section | Status | Notes |
|---------|--------|-------|
| 3.1 Fix `invoke_claude()` JSON parsing | **Done** | `_extract_result_event()` in `claude_enhance.py` |
| 3.2 Pre-flight Claude availability check | **Done** | `claude_available` flag in `pipeline.py` |
| 3.3 Escalate Claude failure logging | **Done** | All 4 sites → `logger.warning` |
| 3.4 Post-loop Claude summary | **Done** | Lines 361-376 in `pipeline.py` |
| 3.5 Decision truthfulness | **Done** | Lines 401-404 in `pipeline.py` |
| 3.6 CLI summary warning | **Done** | `types.py` fields + `extract_cli.py` print |
| 5.1 Test: JSON parsing | **Done** | `TestExtractResultEvent` (6 tests) + `TestInvokeClaude` (5 tests) |
| 5.2 Test: Pre-flight check | **Done** | `TestPreflightClaudeCheck` (2 tests) |
| 5.3 Test: Decision truthfulness | **Done** | `TestDecisionTruthfulness` (2 tests) |
| 5.4 Test: CLI summary | **Done** | `TestCliSummary` (3 tests) |

Total: 70 tests in `test_pipeline.py` + `test_claude_enhance.py` (up from 52). 197 tests pass across all core files.

Experiment scripts (Section 4, non-blocking research code) were **not updated** — they are dead code from Stage 1/2 experiments and would need manual verification against real Claude output.
