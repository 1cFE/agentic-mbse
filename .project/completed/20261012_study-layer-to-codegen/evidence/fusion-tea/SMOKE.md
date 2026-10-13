# Smoke test of the fusion-tea code drafts

**Result (2026-10-12): all five checks pass.** The drafts here do what runbook steps 5 and 6 need from them, in a copy of the SC12 parity layout. The layout is a git repository holding the station fixture at its root, fusion-tea's originals at `scripts/`, and fusion-tea's declaration as `pyproject.toml` (`../parity/README.md`).

- **Run:** `bash smoke.sh $S` after `parity.py … all`, with `SYSIDE_LICENSE_KEY` set. `$S` was `/tmp/study-parity-20261012-114254`: sysml-codegen `2e21955`, agentic-mbse `2894647` and teax `8d87746`, on `/usr/bin/python3.12`.
- **Setup.** `smoke.sh` copies `$S/project` to `$S/smoke/project`. It then applies step 5's code half: `wrappers/scripts/` over `scripts/`, then `git rm -r scripts/study/schemas`, then a commit. `SYSML_CODEGEN_PROJECT_ROOT` and `PYTHONPATH` are unset for every check.
- **Not covered here:** `step5-tests.patch` (fusion-tea's suite, rehearsal step 8a) and a real fusion-tea package (step 8c). The orchestrator's rehearsal covers both.

## 1. Every wrapper is the installed module

```
$ python -c "import scripts.study.manifest as m, sysml_codegen.study.manifest as n; print(m is n)"
True
```

All eight aliases are the installed modules: `scripts.study.{common,identity,manifest,indicators,preflight,verify,read_coverage}` and `scripts.integrate`. `from scripts.integrate import rederived_census`, the form five fusion-tea `build.py` files use, gives the moved function. After the imports, `roots.project_root()` is the repository the wrappers sit in, as `Path(__file__).parents[2]` was.

## 2. A wrapper run by path from /tmp writes the moved module's bytes

- `python <project>/scripts/study/indicators.py …`, run from `/tmp` with absolute arguments, wrote `indicators.json`.
- It is byte-identical to `python -m sysml_codegen.study.indicators …` run from the project.
- It is also byte-identical to the parity run's `moved` `indicators.json`, which ran in a different directory, `$S/project`. So the bytes depend on neither the working directory nor where the project sits.
- `--help` exits 0 through each tool wrapper, run by path (`preflight`, `verify`, `integrate`) and with `-m` (`scripts.study.indicators`).

## 3. `routes.sed` rewrites the route import and nothing else

- The variant is the fixture's `studies/study_route.py` with its import changed back to `from scripts.study import common, identity`. It has two lines appended: a prose line naming `scripts/study/`, and a second import in the `# noqa: E402` form that two fusion-tea routes use.
- Before the rewrite, 2 lines import `scripts.study`. After it, 0 do, and both imports read `from sysml_codegen.study import common, identity`. The prose line is unchanged.
- Without its two appended lines, the rewritten variant equals the fixture route byte for byte.

## 4. `declaration.toml` loads through `declarations.load_declaration`

```
gate pinned-packages: target 'tests/test_dependency_provenance.py'; checked 'the pinned package revisions and installed wheel artifacts'
gate model-family-spine: target 'tests/models/test_model_family_spines.py'; checked 'the canonical tree, the family twins and the tracked census'
environment: ['STOP_PARSER_WHEEL_TARGET', 'STOP_PARSER_AGENTIC_WHEEL', 'STOP_PARSER_CODEGEN_WHEEL', 'STOP_PARSER_COSTINGFE_WHEEL', 'STOP_PARSER_TEAX_ROOT']
record-distributions: {'costingfe': '1costingfe'}
backup-prefix: 'fusion-tea-integration-backup-'
```

The parity layout uses this file as its `pyproject.toml`. In all 19 integrate cases, rows 1a and 5 equal the original's (`../parity/report.md`; rule 3's `declared_rows_hold` found no difference).

## 5. integrate through the wrapper, and gate 7's driver with no project-root variable

- `python scripts/integrate.py` ran the full station request in the switched layout, with the parity `moved` environment: `TEAX_SIMKIT_PATH`, fusion-tea's five declared variables as dummies, and the licence.
  - It exited 0 and returned `CANDIDATE`, with all ten gates passing.
  - Its `tool.path` and `command[0]` are `sysml_codegen/study/integrate.py`.
- Gate 7's driver ran directly in rehearsal step 8c's form, with `PYTHONPATH=<project>:<simkit>` and relative arguments. Unlike 8c's command, it ran **without** `SYSML_CODEGEN_PROJECT_ROOT`.
  - It exited 0, and its receipt has `outcome: pass`, `violations: []` and `route_error: null`.
  - This works because `run_route` now pins the root from the package's work tree before it observes (`2e21955`, the B1 refinement). Before that change, this command refused with `unsupported integer-descriptor open: 3`.
