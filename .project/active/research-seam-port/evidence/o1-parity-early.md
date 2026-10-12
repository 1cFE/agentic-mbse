# O1 early parity — after P4 (`8313b71`)

**Run**: 2026-10-12 by the orchestrator in fusion-tea worktree `/home/reid/1cfe/fusion-tea-research-seam` (fusion-tea `c42ed1d8a`, unmodified), venv built with `uv sync --frozen --extra e2e` plus `syside-license==0.3.6`, this branch installed with `uv pip install --reinstall --no-deps -e /home/reid/1cfe/agentic-mbse-research-seam`. Commands run with `uv run --no-sync`. `git status` was clean before and after; only the ignored `knowledge/.staging/` and `knowledge/.registry.lock` appeared.

## verify (spec criterion 4, first half): PASS

Old: `python scripts/source_registry.py verify`, exit 0. New: the plan's one-liner through `agentic_mbse.research.verify.format_finding`, exit 0.

```
--- old
legacy  loose_file           knowledge/sources/COST_MODELING.md — not a source directory
legacy  orphan_source_dir    knowledge/sources/eu_demo_rw_tf_coil_conductor_dematte_bruzzone — source directory with no manifest row
legacy  orphan_source_dir    knowledge/sources/iter_cryoplant_iter_org — source directory with no manifest row

0 fault(s), 3 legacy entry(ies)
--- new
legacy  loose_file           knowledge/sources/COST_MODELING.md — not a source directory
legacy  orphan_source_dir    knowledge/sources/eu_demo_rw_tf_coil_conductor_dematte_bruzzone — source directory with no manifest row
legacy  orphan_source_dir    knowledge/sources/iter_cryoplant_iter_org — source directory with no manifest row
legacy  block_without_row    knowledge/sources/iter_cryoplant_iter_org — SOURCE_INDEX.md block with no manifest row
legacy  block_without_row    knowledge/sources/eu_demo_rw_tf_coil_conductor_dematte_bruzzone — SOURCE_INDEX.md block with no manifest row
```

Every old finding line is in the new output. The only extra lines are the two `legacy block_without_row` findings for the baseline orphan directories, as `evidence/o1-baseline.md` predicted. Exit codes match.

## duplicates (spec criterion 4, second half): PASS

Script `dupes.py` (Python API; the CLI lands in P5), no `--run`, so nothing is written:

```
url: progress_in_eu_breeding_blanket_design_and_integration -> duplicate | already registered as progress_in_eu_breeding_blanket_design_and_integration
keyed: PMXLGPKG tea_dt_mfe_cost_analysis -> duplicate | already registered as tea_dt_mfe_cost_analysis
```

The URL row matched before any fetch. The `zotero_key` row (written by the pre-port Zotero ingest, no `source_kind`) matched through `KeyedFileSource(..., "zotero", "zotero_key", ...)`.

## Still to run (after P6)

The negative-refusal check (`research open` on the request the recorded negative answers) needs the P5 CLI. The guard check needs the hook table in fusion-tea's `pyproject.toml` (review M4). Both run on the fusion-tea branch after P6, with the comparison re-run through the real CLI.
