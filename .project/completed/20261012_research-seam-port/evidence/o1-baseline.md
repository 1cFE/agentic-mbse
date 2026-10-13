# O1 baseline — fusion-tea registry before the port

**Run**: 2026-10-12 by the orchestrator, in fusion-tea worktree `/home/reid/1cfe/fusion-tea-research-seam` (branch `research-seam-port`, cut from fusion-tea `origin/main` `c42ed1d8a`), with fusion-tea's main-checkout interpreter (`/home/reid/1cfe/fusion-tea/.venv/bin/python`). The worktree stayed clean.

## Snapshot drift

`git diff --stat 0a833b9f7 c42ed1d8a` over the seam scripts, `holdout_guard.py`, both Zotero modules, `tests/research/`, the command, the guide and `CLAUDE.md`: empty. The stage snapshot is current.

## `python scripts/source_registry.py verify` (exit 0)

```
legacy  loose_file           knowledge/sources/COST_MODELING.md — not a source directory
legacy  orphan_source_dir    knowledge/sources/eu_demo_rw_tf_coil_conductor_dematte_bruzzone — source directory with no manifest row
legacy  orphan_source_dir    knowledge/sources/iter_cryoplant_iter_org — source directory with no manifest row

0 fault(s), 3 legacy entry(ies)
```

## Facts for bet B1 and the new check

- `knowledge/SOURCE_INDEX.md` contains no `<!--`. The comment-aware parser (D10) reads it the same as today's parser. Headings: `## Primary Sources` (line 7) and `## How Sources Are Used` (line 2012). 131 `###` blocks.
- `knowledge/.registry_baseline.json` lists `orphan_source_dirs` (`eu_demo_rw_tf_coil_conductor_dematte_bruzzone`, `iter_cryoplant_iter_org`) and `loose_files` (`COST_MODELING.md`).
- Index blocks whose Location is under `knowledge/sources/` and whose directory has no manifest row: **two**, one per baseline orphan directory.
  - `### ITER Cryoplant — iter.org pages (Cryogenics; "As cold as it gets")`, line 192, Location `knowledge/sources/iter_cryoplant_iter_org/` (one block covering two extractions).
  - `### Preliminary Design of a High Current R&W TF Coil Conductor for the EU DEMO (Demattè & Bruzzone, SPC/EPFL)`, line 206, Location `knowledge/sources/eu_demo_rw_tf_coil_conductor_dematte_bruzzone/`.
- **Correction to the spec.** Criterion 4 says the new findings are "the two ITER Cryoplant entries". The data shows one ITER Cryoplant block and one Demattè & Bruzzone block. Both directories are baseline legacy orphans, so if `block_without_row` is classed by the block's Location directory against `orphan_source_dirs`, both are `legacy` and fusion-tea's `verify` keeps exiting 0.
