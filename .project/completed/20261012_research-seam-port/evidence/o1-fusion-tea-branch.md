# O1 — fusion-tea branch (Appendix A, D steps 2–3)

**Run**: 2026-10-12. The orchestrator delegated the edits to a general-purpose subagent from its own session (stage subagents cannot reach fusion-tea), then verified the result itself.

**Where**: fusion-tea worktree `/home/reid/1cfe/fusion-tea-research-seam`, branch `research-seam-port`, base `c42ed1d8a`, commit `940500788` "Register through the installed agentic_mbse.research package; delete the seam scripts". Not pushed. The owner's main checkout was not touched. The venv was built with `uv sync --frozen --extra e2e` plus `syside-license==0.3.6`, and this branch was installed editable. Commands ran with `uv run --no-sync`.

## Changes (32 files, +256 / −4,540)

- **Modified:**
  - `pyproject.toml` gains the hook table (`[tool.agentic-mbse.research] holdout-guard = "scripts/holdout_guard.py"`).
  - `scripts/zotero_ingest.py` builds `KeyedFileSource(path, "zotero", "zotero_key", key, "Zotero Key", f"{GROUP_ID}:{key}")`, with the `ZoteroSource` rationale moved into the `process_zotero_item` docstring. The index and block writers are deleted.
  - `scripts/zotero_lib.py` reads its manifest views through `agentic_mbse.research.load_manifest_rows`, and the registry helpers are deleted.
  - `CLAUDE.md:11` is the design's Appendix A text.
  - ADR-0008 gets a dated amendment line.
  - `.gitignore` loses the line-20 whitelist; lines 35–36 are kept.
  - `tests/research/conftest.py` is trimmed.
- **Deleted:** `scripts/research_seam.py`, `scripts/source_registry.py`, `.claude/commands/research-acquire.md`, `docs/research_seam_operator_guide.md`, 16 test files (moved to agentic-mbse or retired per Appendix B), and their web fixtures.
- **Added:** `tests/research/test_holdout_wiring.py` and `tests/research/test_zotero_manifest_views.py`.

## Checks

- **Guard (D step 2, after the hook table):** `agentic-mbse research register --url https://example.org/mirror/08-FST-Lyon.pdf …` gives `{"outcome": "holdout_hit", "reason": "term:08-fst-lyon matched 1x", "rule_id": "term:08-fst-lyon", "offsets": [27]}`, exit 1, no staging entry, no fetch.
- **Suites:** `pytest tests/research -m ""` went from 167 passed before to 34 passed after. The difference is the 140 tests now in agentic-mbse's `tests/test_research/` (or retired with `test_hermetic_paths.py`), plus 7 new tests. The orchestrator re-ran it independently: 34 passed. Only `tests/research/` imports the seam or Zotero modules.
- **Imports:** `zotero_ingest`, `zotero_lib`, `zotero_group_download` and `test_zotero_write_access` all import cleanly.
- **Live references:** a grep over `scripts/ tests/ CLAUDE.md AGENTS.md docs/ .claude/ .codex/` for the deleted files and names returns nothing, except `docs/exploratory-modeling/part-3-harness.html`. That is the published write-up (1cf.energy/exploratory-modeling), which names the old scripts in narrative and layout tables. The orchestrator classed it as a historical publication and left it unchanged; whether to refresh it is the owner's call (outward-facing content). Historical records (goal evidence, `VALIDATION_MATRIX.md:63`, `WI-045` spec) keep their references, per design Appendix A.
- **Ledger:** every Appendix C home marked "new" or "(O1)" is in the commit's diff. The ledger's Item 5 rows now cite `940500788`.

## Notes for O3 (post-merge)

- The branch cannot run on the pinned agentic-mbse (`ac5fb1a` has no `agentic_mbse.research`). It merges only after the pin moves, as the runbook says.
- `zotero_ingest.run_extraction` (`--re-extract`) still calls `uv run agentic-mbse extract`. Before the pin move, that re-syncs the venv and reverts an editable install. After the pin move the pinned version carries the package, so there's no effect.
- Collecting fusion-tea's whole suite shows 4 errors unrelated to this change: untracked `work/active/WI-098` and `WI-099` inputs, and an unset `STOP_PARSER_TEAX_ROOT`. These are the known environment gaps of a fusion-tea worktree.
