# Spec: Hash Consolidation

**Status:** Complete
**Owner:** Reid W
**Created:** 2026-03-29 08:32 PDT
**Complexity:** LOW
**Branch:** webfetch-tools

---

## Business Goals

### Why This Matters

The repo has four independent implementations of content hashing across four modules, using two different algorithms (MD5, SHA256) and three different output formats. This means hashes from different parts of the system cannot be compared — you can't ask "does this `summary.json` `file_hash` refer to the same source as this frontmatter `content_hash_sha256`?" without knowing that one is MD5 and the other is SHA256.

Beyond comparability, it's four copies of trivially identical logic that should be one import.

### Success Criteria

- [ ] One shared hash function used by all callers — no private `_compute_file_hash` or `_get_file_checksum` copies
- [ ] All hashes use SHA256 — hashes from any two contexts are directly comparable for the same input bytes
- [ ] Existing functionality unchanged — skip-checks, provenance, tool-file safety all work as before

### Priority

P3 — Code quality cleanup. No external blockers. Should be done after extraction-provenance is merged, since that feature introduces the `compute_source_hash()` function that becomes the canonical implementation.

---

## Problem Statement

### Current State

| # | Location | Function | Algorithm | Output Format | Purpose |
|---|----------|----------|-----------|---------------|---------|
| 1 | `extraction/base.py:68` | `_compute_file_hash(Path)` | MD5 | `md5:abc123...` | Extraction skip-check (`summary.json`) |
| 2 | `extraction/index.py:44` | `_get_file_checksum(Path)` | SHA256 | `sha256:abc123...` | INDEX.md freshness check |
| 3 | `cli/__init__.py:300` | `_compute_file_hash(Path)` | SHA256 | bare hex | Tool-owned file modification detection |
| 4 | `extraction/frontmatter.py:62` | `compute_source_hash(Path\|bytes)` | SHA256 | bare hex | Extraction provenance frontmatter |

Three are private (`_`-prefixed), one is public. Two share the same name (`_compute_file_hash`) but produce different output. All do the same thing: hash file bytes.

### Desired Outcome

One public function (`compute_source_hash`) in one location, returning bare SHA256 hex. All four callers import and use it. Callers that need a prefix format add it themselves.

---

## Scope

### In Scope

- Consolidate all 4 hash implementations into one shared function
- Standardize on SHA256 algorithm everywhere
- Move the canonical function to `extraction/base.py` (the existing shared utilities module)
- Update `summary.json` format from `md5:...` to `sha256:...`
- Update all callers: `base.py`, `index.py`, `cli/__init__.py`, `frontmatter.py`
- Update tests that assert on hash formats

### Out of Scope

- Changing when or where hashes are computed (each caller keeps its own usage pattern)
- Reducing recomputation of the same file for different purposes (explicitly accepted — different contexts, different purposes)
- Changing what gets hashed — only how
- Migrating existing `summary.json` files (old `md5:` hashes simply won't match, triggering one-time re-extraction — this is the desired behavior of the skip-check)

### Edge Cases & Considerations

- **Existing `summary.json` cache invalidation**: Changing from MD5 to SHA256 means all existing `summary.json` `file_hash` values won't match. `check_processing_needed()` will return `True`, causing one-time re-extraction of already-processed docs. This is acceptable — the skip-check is a convenience optimization, not a correctness guarantee.
- **`.tool-hashes.json` compatibility**: Existing tool hash files use SHA256 bare hex already. No format change needed — just swap the implementation.
- **`INDEX.md` format**: Already uses `sha256:` prefix. Just replace the private function with the shared one + prefix at the call site.

---

## Requirements

### Functional Requirements

> Requirements are from user's request unless marked [INFERRED].

1. **FR-1**: All content hashing in the repo MUST use SHA256.

2. **FR-2**: All content hashing MUST use a single shared function. No private copies of hash logic.

3. **FR-3**: The shared function MUST accept both `Path` and `bytes` inputs (the `Path` path MUST use chunked reading to avoid loading large files into memory).

4. **FR-4**: The shared function MUST return bare SHA256 hex (64-character string). Callers that need a prefix (e.g., `sha256:`) MUST add it themselves.

5. **FR-5**: The shared function SHOULD live in `extraction/base.py` — the existing shared utilities module that all extraction code already imports.

6. **FR-6**: [INFERRED] `frontmatter.py` MUST import the function from `base.py` rather than defining its own copy. (After extraction-provenance merges, `frontmatter.py` will have the implementation — this feature moves it to `base.py`.)

7. **FR-7**: [INFERRED] The `summary.json` `file_hash` field format MUST change from `md5:hex` to `sha256:hex` to reflect the algorithm change.

### Non-Functional Requirements

8. **NFR-1**: All existing tests MUST continue to pass (with updated hash format assertions where needed).

9. **NFR-2**: The one-time re-extraction triggered by hash format change in `summary.json` is acceptable and MUST NOT be worked around with backwards-compatibility shims.

---

## Acceptance Criteria

### Core Functionality
- [ ] `grep -r "_compute_file_hash\|_get_file_checksum" src/` returns zero matches (no private copies remain)
- [ ] `grep -r "hashlib.md5" src/` returns zero matches (no MD5 usage)
- [ ] `base.py` exports `compute_source_hash(Path | bytes) -> str`
- [ ] `frontmatter.py`, `index.py`, `cli/__init__.py` all import from `base.py`
- [ ] `summary.json` `file_hash` values use `sha256:` prefix
- [ ] `INDEX.md` `source_checksum` values use `sha256:` prefix (unchanged format, different implementation)
- [ ] `.tool-hashes.json` uses bare hex (unchanged format, different implementation)
- [ ] Frontmatter `content_hash_sha256` uses bare hex (unchanged format, different implementation)

### Quality & Integration
- [ ] All existing tests pass (`uv run pytest tests/`)
- [ ] Tests updated for new hash format in `summary.json` assertions
- [ ] `uv run ruff check src/ tests/` passes

---

## Related Artifacts

- **Predecessor:** `.project/active/extraction-provenance/` (introduces `compute_source_hash` in `frontmatter.py`)
- **Research:** Hash inventory from conversation on 2026-03-29 (4 implementations, 2 algorithms, 3 formats)
- **Design:** `.project/active/hash-consolidation/design.md` (to be created)

---

**Next Steps:** After extraction-provenance merges, proceed to `/_my_design`
