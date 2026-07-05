# Implementation Plan: Hash Consolidation

**Status:** Complete
**Created:** 2026-03-29
**Last Updated:** 2026-03-29

## Source Documents
- **Spec:** `.project/active/hash-consolidation/spec.md`

## Implementation Strategy

**Phasing Rationale:**
Phase 1 establishes the canonical function and updates the primary consumer (extraction skip-check) plus its tests. Phase 2 wires up the remaining three callers. This order means Phase 1 is self-contained and testable before touching callers in other modules.

**Overall Validation Approach:**
- Update tests alongside implementation (no separate test-only phase — the existing test suite already covers the behavior; we're changing hash format, not logic)
- Full test suite + linting after each phase
- Acceptance criteria grep checks at the end

---

## Phase 1: Canonical Function in `base.py` + Extraction Tests

### Goal
Replace `_compute_file_hash` (MD5) in `base.py` with the chunked SHA256 `compute_source_hash` from `frontmatter.py`. Update `check_processing_needed` and `write_summary` to use it with `sha256:` prefix. Fix test assertions.

### Test Stencil (Update Existing)
```python
# tests/test_extraction.py — change md5 → sha256 in hash assertions
file_hash = "sha256:" + hashlib.sha256(b"fake pdf content").hexdigest()
summary = {"file_hash": file_hash, "processing_completed": True}
```

### Changes Required

#### 1. `src/agentic_mbse/extraction/base.py`
- [ ] Remove `_compute_file_hash` (lines 68-71)
- [ ] Add `_CHUNK_SIZE = 65_536` constant
- [ ] Add public `compute_source_hash(source: Path | bytes) -> str` (moved from `frontmatter.py`, same implementation)
- [ ] Update `check_processing_needed` (line 101): `current_hash = f"sha256:{compute_source_hash(input_path)}"`
- [ ] Update `write_summary` (line 121): `"file_hash": f"sha256:{compute_source_hash(input_path)}"`
- [ ] Remove `hashlib` import if no longer needed directly (it won't be — `compute_source_hash` handles it internally). Keep `hashlib` import since `compute_source_hash` uses it.

#### 2. `tests/test_extraction.py`
- [ ] Line 92: Change `"md5:" + hashlib.md5(...)` → `"sha256:" + hashlib.sha256(...)`
- [ ] Line 104: Change `"md5:oldhash"` → `"sha256:oldhash"` (just needs to not match)
- [ ] Line 115: Change `"md5:" + hashlib.md5(...)` → `"sha256:" + hashlib.sha256(...)`
- [ ] Line 127: Change `"md5:" + hashlib.md5(...)` → `"sha256:" + hashlib.sha256(...)`

### Validation

**Automated:**
- [ ] `uv run pytest tests/test_extraction.py -v` → All pass
- [ ] `uv run pytest tests/test_frontmatter.py -v` → All pass (not yet changed, should still pass)
- [ ] `uv run ruff check src/agentic_mbse/extraction/base.py`

**What We Know Works After This Phase:**
- `compute_source_hash` exists as a public function in `base.py`
- Extraction skip-check and summary use SHA256
- All extraction tests pass with new hash format

---

## Phase 2: Wire Up Remaining Callers

### Goal
Replace private hash functions in `frontmatter.py`, `index.py`, and `cli/__init__.py` with imports from `base.py`.

### Changes Required

#### 1. `src/agentic_mbse/extraction/frontmatter.py`
- [ ] Remove `_CHUNK_SIZE` constant (line 13)
- [ ] Remove `compute_source_hash` function (lines 62-78)
- [ ] Remove `hashlib` import (line 9)
- [ ] Add: `from agentic_mbse.extraction.base import compute_source_hash`
- [ ] Re-export `compute_source_hash` in module (callers like `web_backend.py`, `pipeline.py` import from here)

#### 2. `src/agentic_mbse/extraction/index.py`
- [ ] Remove `_get_file_checksum` function (lines 44-46)
- [ ] Remove `hashlib` import (line 11)
- [ ] Add: `from agentic_mbse.extraction.base import compute_source_hash`
- [ ] Line 328: Change `_get_file_checksum(doc_path)` → `f"sha256:{compute_source_hash(doc_path)}"`
- [ ] Line 496: Same change

#### 3. `src/agentic_mbse/cli/__init__.py`
- [ ] Remove `_compute_file_hash` function (lines 300-302)
- [ ] Remove `hashlib` import (line 4)
- [ ] Add: `from agentic_mbse.extraction.base import compute_source_hash`
- [ ] Update all call sites: `_compute_file_hash(path)` → `compute_source_hash(path)` (bare hex, no prefix — matches current CLI format)

### Validation

**Automated:**
- [ ] `uv run pytest tests/ -v` → All pass
- [ ] `uv run ruff check src/ tests/`

**Acceptance criteria greps (from spec):**
- [ ] `grep -r "_compute_file_hash\|_get_file_checksum" src/` → zero matches
- [ ] `grep -r "hashlib.md5" src/` → zero matches
- [ ] `grep -r "hashlib" src/agentic_mbse/extraction/frontmatter.py src/agentic_mbse/extraction/index.py src/agentic_mbse/cli/__init__.py` → zero matches (hash logic consolidated)

**What We Know Works After This Phase:**
- Single shared hash function, all callers wired up
- All acceptance criteria from spec satisfied

---

## Risk Management

- **Circular imports**: Verified — `base.py` does not import `frontmatter.py` and vice versa. Safe to move function to `base.py` and have `frontmatter.py` import from it.
- **Re-export from frontmatter.py**: External callers (`web_backend.py`, `pipeline.py`) import `compute_source_hash` from `frontmatter.py`. Re-exporting via import keeps them working without changes.
- **CLI hashlib removal**: Need to verify no other `hashlib` usage in `cli/__init__.py` before removing the import.

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-03-29
**Actual Changes:**
- Replaced `_compute_file_hash` (MD5) in `base.py` with `compute_source_hash` (SHA256, chunked, accepts Path|bytes)
- Updated `check_processing_needed` and `write_summary` to use `sha256:` prefix
- Updated 4 test assertions in `test_extraction.py` from `md5:` to `sha256:`
**Issues:** None
**Deviations:** None

### Phase 2 Completion
**Completed:** 2026-03-29
**Actual Changes:**
- `frontmatter.py`: Removed local `compute_source_hash` + `_CHUNK_SIZE` + `hashlib` import; re-exports from `base.py`
- `index.py`: Removed `_get_file_checksum` + `hashlib` import; inlined `f"sha256:{compute_source_hash(...)}"` at call sites
- `cli/__init__.py`: Removed `_compute_file_hash` + `hashlib` import; imports `compute_source_hash` from `base.py`
- Updated 3 test methods in `test_cli.py` to import `compute_source_hash` from `base.py` instead of `_compute_file_hash` from `cli`
- Updated 1 assertion in `test_extraction.py` (`startswith("md5:")` → `startswith("sha256:")`)
**Issues:** None
**Deviations:** None

---

**Status**: Complete
