# Design: Pipeline Integration + CLI Wiring

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-08 17:12 UTC
**Branch:** pdf-extract
**Commit:** 0d654c6

## Overview

Wire the completed `claude_structure.py` module into `extract_cli.py` as Layer 3 (between GMFT tables and AI repair), add `--structure-only` and `--model` CLI flags, and enforce correct pipeline ordering. This is a focused integration task — the core module is implemented and tested, the CLI structure is well-established, and the insertion point is clear.

## Related Artifacts

- **Spec:** `.project/active/pipeline-integration-cli-wiring/spec.md`
- **Epic:** `.project/backlog/epic_pdf-extraction-v3.md` (Item 3)
- **Core module:** `src/agentic_mbse/extraction/claude_structure.py` (684 lines, 50 tests)
- **Target file:** `src/agentic_mbse/cli/extract_cli.py` (383 lines)
- **Test file:** `tests/test_extract_cli.py` (506 lines)

## Research Findings

### Current Pipeline (extract_cli.py:219-278)

The post-processing pipeline lives inside the `for doc in docs:` loop at `extract_cli.py:219-278`. After a successful extraction (`result.success` is True and `result.markdown_path` exists), the code:

1. Reads markdown text (`extract_cli.py:225`)
2. Detects quality problems via `detect_problems()` (`extract_cli.py:229-231`)
3. Runs GMFT table enhancement — L2 (`extract_cli.py:233-250`)
4. Runs AI repair — current L3 (`extract_cli.py:252-269`)
5. Writes back modified text if any layer ran (`extract_cli.py:272-273`)
6. Reports unenhanced problem count (`extract_cli.py:276-277`)
7. Runs index generation if `--index` (`extract_cli.py:280-289`)

Key pattern: each layer reads `md_text`, modifies it, and stores metadata in `layer_metadata: dict`. The write-back condition is `if layer_metadata:` — meaning if any layer stored anything, the file is rewritten.

### Claude Structure Module API (claude_structure.py)

Two public functions needed for integration:

```python
needs_claude_structure(md: str) -> bool            # claude_structure.py:203
enhance_structure(                                  # claude_structure.py:645
    md: str,
    pdf_path: Path,
    output_dir: Path,
    phase_a_model: str = "haiku",
    phase_b_model: str = "sonnet",
) -> tuple[str, dict]
```

`enhance_structure()` handles its own error recovery internally — malformed JSON triggers retry then fallback. It returns a metadata dict with `headers_inserted`, `headers_skipped`, `warnings`, and phase details.

### Existing Test Patterns (test_extract_cli.py)

Tests use a `MockArgs` class (`test_extract_cli.py:17-22`) that builds an `argparse.Namespace` from kwargs. Every test that calls `cmd_extract()` must provide **all** args attributes. Current required attrs: `path`, `output`, `backend`, `timeout`, `force`, `index`, `summarize`, `fix_tables`, `no_tables`, `enhance`, `max_repair_pages`.

Adding `--structure-only` and `--model` means **every existing `MockArgs` instantiation** needs the new attrs added (with defaults matching the argparse defaults: `structure_only=False`, `model=None`).

### Existing `--enhance` Help Text (extract_cli.py:369)

Current help: `"Enable Layer 3 AI repair (requires 'claude' CLI, costs $$)"`. This will need updating since `--enhance` now triggers both L3 (structural) and L4 (AI repair).

---

## Proposed Design

### 1. CLI Argument Changes (extract_cli.py:311-383)

Add two new arguments to `register_extract_subcommand()`:

```python
p.add_argument(
    "--structure-only",
    action="store_true",
    help="Run structural repair only (Layer 3), skip AI quality repair (Layer 4)",
)
p.add_argument(
    "--model",
    choices=["opus", "sonnet", "haiku"],
    default=None,
    help="Override Claude model for structural repair (default: haiku for style detection, sonnet for structure)",
)
```

Update `--enhance` help text:

```python
help="Enable AI enhancement: structural repair (Layer 3) + quality repair (Layer 4)"
```

### 2. Pipeline Modification (extract_cli.py:219-278)

Insert L3 structural pass **between** GMFT (L2) and AI repair (L4). The new pipeline section sits at approximately line 252 (where current L3/AI repair begins).

**Compute enhancement flags early** (after existing line 222):

```python
enhance = args.enhance
structure_only = args.structure_only
run_structural = enhance or structure_only
run_ai_repair = enhance and not structure_only
model = args.model
```

**L3 block** (insert before current AI repair block):

```python
# Layer 3: Claude structural pass (with --enhance or --structure-only)
if run_structural:
    from agentic_mbse.extraction.claude_structure import (
        enhance_structure,
        needs_claude_structure,
    )

    if needs_claude_structure(md_text):
        phase_a_model = model or "haiku"
        phase_b_model = model or "sonnet"
        try:
            md_text, struct_meta = enhance_structure(
                md_text,
                doc,
                output_dir,
                phase_a_model=phase_a_model,
                phase_b_model=phase_b_model,
            )
            layer_metadata["structure"] = struct_meta
            inserted = struct_meta.get("headers_inserted", 0)
            skipped = struct_meta.get("headers_skipped", 0)
            style_info = struct_meta.get("phase_a", {})
            style_desc = (
                f"{style_info.get('doc_type', '?')} "
                f"({style_info.get('heading_convention', '?')})"
            )
            print(f"        structure: {style_desc}, "
                  f"{inserted} headers inserted, "
                  f"{skipped} skipped")
            for w in struct_meta.get("warnings", []):
                print(f"        warning: {w}")
        except Exception as exc:
            print(f"        structure: FAILED ({exc}), continuing")
    else:
        print("        structure: skipped (document already well-structured)")
```

**L4 block** (modify the existing AI repair guard):

```python
# Layer 4: AI quality repair (only with --enhance, NOT --structure-only)
if run_ai_repair and remaining_problems:
    # ... existing ai_repair code, unchanged ...
```

### 3. Write-Back and Ordering

The existing write-back logic (`if layer_metadata:` at line 272) already handles this correctly — if L3 adds `layer_metadata["structure"]`, the file gets rewritten. No change needed.

Index generation (`if args.index` at line 280) already runs after all enhancement layers in the current code structure, since it's outside and after the enhancement block. The linear flow guarantees L3 completes before INDEX runs.

### 4. Test Changes (test_extract_cli.py)

**MockArgs update:** Add `structure_only=False` and `model=None` defaults to every existing `MockArgs(...)` call. There are ~10 instantiation sites. This is mechanical but required to avoid `AttributeError` at runtime.

**New test cases** (add to `TestCmdExtract` class):

1. **`test_enhance_triggers_structural_pass`** — `--enhance` with markdown that triggers `needs_claude_structure()=True`. Mock both `enhance_structure` and `repair_document`. Assert both called, in order.

2. **`test_enhance_skips_structure_when_not_needed`** — `--enhance` with mock `needs_claude_structure()=False`. Assert `enhance_structure` not called, `repair_document` still called.

3. **`test_structure_only_skips_ai_repair`** — `--structure-only` flag. Mock `enhance_structure`. Assert `enhance_structure` called, `repair_document` not called.

4. **`test_model_flag_passed_through`** — `--model sonnet` with `--enhance`. Assert `enhance_structure` called with `phase_a_model="sonnet", phase_b_model="sonnet"`.

5. **`test_structure_failure_continues_pipeline`** — `--enhance` with `enhance_structure` raising `Exception`. Assert pipeline continues (doesn't crash), `repair_document` still called for L4.

6. **`test_default_mode_unchanged`** — No `--enhance`, no `--structure-only`. Assert neither `enhance_structure` nor `repair_document` called. (Existing tests already cover this implicitly, but worth an explicit test for the new code paths.)

**Mocking approach:** Patch `agentic_mbse.extraction.claude_structure.needs_claude_structure` and `agentic_mbse.extraction.claude_structure.enhance_structure` at the module level. Since `extract_cli.py` uses lazy imports (`from ... import ...` inside the function body), the patches target the source module.

**Test fixture pattern:** Each test needs a mock `ExtractionResult` with a real `markdown_path` that contains actual markdown text (so `md_text = result.markdown_path.read_text()` works). Create a helper or use a shared fixture:

```python
def _make_extraction_result(tmp_path, md_content="# Test\n\nSome content."):
    output_dir = tmp_path / "report"
    output_dir.mkdir(exist_ok=True)
    md_path = output_dir / "full_document.md"
    md_path.write_text(md_content)
    return ExtractionResult(
        success=True,
        output_dir=output_dir,
        markdown_path=md_path,
        backend_used="pymupdf",
    )
```

---

## Potential Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Adding `structure_only`/`model` attrs to MockArgs breaks existing tests | Medium | Low | Mechanical fix — add defaults to every instantiation. Run tests after each change. |
| `enhance_structure()` exception not caught cleanly | Low | Medium | Broad `except Exception` around the L3 call. Module already handles JSON/subprocess errors internally; this is a safety net. |
| `needs_claude_structure()` import side-effects | Very Low | Low | Module has no import-time side effects — only imports `re`, `json`, `subprocess`, `dataclass`. |

---

## Integration Strategy

This is a **pure insertion** — no existing code is modified (except help text and the `if enhance` guard becoming `if run_ai_repair`). The new L3 block slots between existing L2 and L4 blocks. The flag refactor (`run_structural`, `run_ai_repair`) makes the intent clearer without changing behavior for existing flag combinations.

**Backward compatibility:** Default behavior (no flags) is unchanged. `--enhance` alone now does more (L3+L4 vs just L4), which is the intended upgrade. No existing user workflow produces different results unless they opt in with `--enhance`.

---

## Validation Approach

1. **Unit tests:** 6 new tests in `test_extract_cli.py` covering all flag combinations and failure paths
2. **Existing test suite:** All 799+ tests must pass — run `uv run pytest tests/` after changes
3. **CLI smoke test:** `uv run agentic-mbse extract --help` shows new flags
4. **Manual verification** (deferred to Item 4): Run `--enhance` on a real corpus document to verify end-to-end

---

**Next Step:** After approval → `/_my_plan` for implementation steps
