# SC12 parity: the original study tools against the moved ones

This directory is the evidence for spec SC12 (design Appendix G). It runs fusion-tea's original study tools (staged at `b06585709`) and the moved `sysml_codegen.study` tools, installed from a wheel, on the same inputs. It then checks that their exit codes and output documents are equal, except in the fields the closed list B1–B13 names.

**Status (2026-10-12): passes.** All 28 cases are `EQUAL` (3) or `EQUAL after closed-list fields` (25), every exit code agrees, and library parity holds, at sysml-codegen `6ad4c22` and agentic-mbse `70d78d0` (the audit-F1 re-run; first passed at `2e21955` and `2894647`). `report.md` has the per-case table.

- The first run stopped with five cases `DIFFERENT`: the cases whose route runs under read coverage (gates 7, 8 and 9, and `CANDIDATE`). They differed only in receipt entries about the installed `sysml_codegen` package. The orchestrator ratified three rules for those entries (Q1, below), and all five are now `EQUAL after closed-list fields [B1, B2, B8, B11, B13]`.
- `2e21955` then moved the project-root resolution in `run_route` ahead of observation (a B1 refinement). Re-reporting the runs made before it (`24cce2c`) under the same rules gives the same table, status for status and count for count. The committed case files changed only in content digests (the B2 source digests and the B8 dependency digest).
- **Phase 6 re-ran it** at sysml-codegen `aac1290` and agentic-mbse `db032d6`, because Phase 5's docstring commit (`f46a913`) and Phase 6's fix 2 changed five study modules after `2e21955`. agentic-mbse's only new commit is O4's ledger, and its wheel's sha256 is unchanged. The table is the same, status for status. Two counts moved, both explained: each route case now has 77 B8 installed-package declaration additions, not 76, because the wheel gained `sysml_codegen/cli/install.py`; and the `scratch-root` pattern applies 7120 times, not 7115, one more path in each of the five route cases' moved receipts. The case files otherwise changed only in content digests, on both sides, because the original route imports the moved `identity` from the wheel.
- **The audit fix pass re-ran it** at sysml-codegen `6ad4c22` and agentic-mbse `70d78d0` (F9's comment), in `/tmp/study-parity-20261012-132723`, because audit F1 changed `read_coverage.py`: B13 now reads the interpreter's build-time `TZPATH` through `sysconfig`, and the observer no longer imports `zoneinfo`. The table is the same, status for status. One count moved, as expected: the measured preload set lost the `zoneinfo` group (now 12 standard-library modules and 8 `.pyc` paths, down from 21 and 14), so each route case excludes fewer reads (`B13 preloaded standard-library read` ×8, down from ×14; gate 7's case ×6, down from ×7). Those `zoneinfo` reads now appear on both sides and compare equal. The closure check names `sysconfig`'s `TZPATH` read in place of `zoneinfo`.

## Run it

```bash
S=/tmp/study-parity-$(date +%Y%m%d-%H%M%S)
EV=.project/active/study-layer-to-codegen/evidence/parity
bash $EV/make_venv.sh $S /home/reid/1cfe/sysml-codegen-study-layer /home/reid/1cfe/agentic-mbse-study-layer /home/reid/1cfe/teax
set -a; source /home/reid/1cfe/sysml-codegen/.env; set +a        # SYSIDE_LICENSE_KEY
$S/venv/bin/python $EV/parity.py --scratch $S --staged .orchestrate-logs/src/fusion-tea@b06585709 \
    --fixture tests/fixtures/study_station --teax /home/reid/1cfe/teax all
```

Run both commands from the repository root. `all` sets up, runs every case and writes the report, in about two minutes. It exits 0 only when every case is `EQUAL…` and library parity holds. The steps also run alone: `setup`, `run [CASE…]` and `report`.

## What it builds

- **`make_venv.sh`** builds both wheels from `git archive HEAD`, never from a working tree. It creates `$S/venv` on `/usr/bin/python3.12`, fusion-tea's interpreter (plan Phase 4, decision Q2), so `sys.base_prefix` is `/usr` and neither B13 allowance fires on either side.
  - Everything installed is byte-compiled at install time, so no run writes a `.pyc` into the venv.
  - teax's simkit is importable through a `.pth` file naming `teax/packages/teax-simkit`, which is what an editable install amounts to, without building into the teax checkout.
  - `wheels/sources.json` records both commits and both wheel digests; the report copies them.
- **`$S/project`** is a git repository holding the fixture's tree at its root, the staged originals at `scripts/study/` and `scripts/integrate.py`, and two stand-in gate files at fusion-tea's paths.
  - The spine stand-in carries fusion-tea's `_contract` and `_by_entry_type` (lines 174–182) verbatim, because the original seam imports them.
  - `pyproject.toml` is `../fusion-tea/declaration.toml`, Appendix D's fusion-tea declaration. So rows 1a and 5 must reproduce fusion-tea's strings.
- **Runs.** Every case runs three times from the same base commit: `orig` (`python scripts/<tool>.py`), `orig2` (the same again) and `moved` (`python -m sysml_codegen.study.<tool>`).
  - Each case's mutation is committed with fixed dates, so its commit id is the same in every run.
  - Each run starts from a cleaned tree (`git clean -fdx`), so no run inherits another's bytecode.
  - Every path in the arguments is relative to the project, which is the working directory.
  - `out/` is `$S/out`, moved aside into `$S/runs/<case>/<mode>/` after each run.
- **The environment** is built from nothing, not inherited. Both modes get fusion-tea's four wheel variables (dummies) and `STOP_PARSER_TEAX_ROOT`. Each mode adds one variable, the harness side of a closed-list item:
  - a `uv` shim first on `PATH` runs `uv run X …` as `X …` (B3);
  - moved: `TEAX_SIMKIT_PATH` (B7);
  - orig: `SYSML_CODEGEN_PROJECT_ROOT`, which no original tool reads. The fixture route imports the moved `identity` in both modes (Appendix G), and its `build_sealed` needs a project root. The moved seam hands that root to its producers (B1, DD2), and since `2e21955` the moved `run_route` pins it before observing. The original seam and driver do neither. Without the variable, the moved `roots` would run `git` under the original observer, which refuses that child process at gate 7. That refusal, `unsupported integer-descriptor open: 3`, is what the first run showed.
- **Setup** also makes the grid store both `verify` cases read (`$S/inputs`, from the fixture's own `run_grid`). It measures the preload set (B13, and Q1 rule 3) into `preloads.json` and runs library parity.

## The comparison rules

Each rule is a constant or one small function in `parity.py`, and every application is counted in `cases/<case>/comparison.json` and `report.md`.

1. **Exit codes** must be equal across the three runs.
2. **Noise** is masked by the token patterns in `patterns.json`, never by whole field. Each pattern states its reason and scope. orig and orig2 must then be equal; any residue is reported as `NOISE` and fails the case.
3. **Determined closed-list values are mapped** from orig to moved, only in the fields named:
   - `tool.path` and `command[0]` (B2), by `TOOL_PATHS`;
   - integrate's gate and blocker `producer` strings (B2, B11), by `TOOL_PATHS` and `CENSUS_PRODUCERS`;
   - gate 1b's refusal detail, which names the simkit root `TEAX_SIMKIT_PATH` where the original named the checkout root `STOP_PARSER_TEAX_ROOT` (B7, `teax_detail_mapping`);
   - rows 1a and 5 are not mapped; they must equal the declaration's `target` and `checked` (B5, B12, `declared_rows_hold`).
4. **Content-derived closed-list values are masked by token**, on both sides:
   - `source_digest.digest`, and the `sha256` of each `.py` in `source_digest.files[]` (B2). Schema entries keep their `sha256`, which must be equal. Files only the moved tools digest (`roots.py`, `census.py`, `declarations.py`) are counted as B2 additions; any other extra file is a difference.
   - The receipt's `dependency_digest`, and the 64-hex digest inside gate 7's pass detail (B8).
   - Read-coverage receipts, by `receipt_view`. *Tool code* is orig's `$S/project/scripts/`, mapped by rule 3's table, and the installed package `TOOL_HOME/sysml_codegen/`, which the route imports in both modes.
     - Declarations of tool code are compared as path sets after mapping; category and `sha256` may differ (B8, B2). Every orig declaration must be in moved. Moved-only declarations under the installed package are counted as B8 additions (Q1 rule 1).
     - Reads of tool code are compared by module, with category and `sha256` free (Q1 rule 2, B8). `common.py` and `__pycache__/common.cpython-312.pyc` are both the module `sysml_codegen.study.common`. A read that is no module keeps its `sha256`.
     - orig's `runtime-observed` reads of modules only the moved driver preloads are dropped where moved does not record them, as measured into `preloads.json`. That covers the standard-library `.pyc` files (spec B13 consequence; each module is checked to be loaded by importing `sysml_codegen.study.roots` or by reading `sysconfig`'s build-time `TZPATH`) and the installed-package modules (Q1 rule 3; each is checked to be in `sysml_codegen`). Exactly that set is excluded.
     - Every other entry is compared whole: path, category and `sha256`.
5. **Everything else must be equal**, every `detail` string included.
   - integrate's stderr is its human summary. Each run's stderr is checked to equal `human_summary` of its own return, and the returns are then compared.
   - teax's work area `out/_work/` (SQLite stores, package links) is compared by file listing; its bytes are teax's, not tool documents.
6. **Library parity.** With the moved root pinned by `use_project_root`, these agree between the originals and the moved modules: `indicator_input_fingerprint`, `build_sealed`, `repo_relative_posix` on four paths, and `rederived_census`.

## Ratified rules beyond Appendix G

Every rule here departs from Appendix G's text. Each was surfaced at the Phase 4 pause and ratified by the orchestrator on 2026-10-12 ([AGENT], `briefs/implement-phase-4-finish.md`). Each entry gives the reason and the evidence.

**Q1, option (a): three rules for the installed package in read-coverage receipts.** Without them, the five route cases were `DIFFERENT` on exactly these entries and nothing else (the first run, `12c38b9`).

1. **Moved-only declarations under the installed `sysml_codegen` package are B8 additions.** In the original, a route's reads of the installed package were already permitted, as `runtime-observed` under the venv prefix. The moved observer declares the same files with digests. The permission is the same, and the receipt records more. Evidence: 76 additions per route case, every one a `.py` under `TOOL_HOME/sysml_codegen/`, and all 8 orig declarations map onto moved ones (`cases/integrate-*/comparison.json`, key `B8 installed-package declaration addition`).
2. **Reads of the installed package are compared by module, with category free.** orig reads the package's bytecode as runtime data; moved reads its source and bytecode as declared. Same modules, different bookkeeping (B8). Evidence: each route case's 12 reads (6 per side) compare as the same three modules on both sides, `sysml_codegen.study.common`, `identity` and `manifest`, once rule 3 has dropped orig's three preloaded ones (key `B8 installed-package read, by module`).
3. **The preload exclusion also covers the installed-package modules the moved driver preloads.** The moved observer lives in the package the route imports, so `sysml_codegen`, `sysml_codegen.study` and `sysml_codegen.study.roots` are loaded before observation starts, and the moved receipt never records them. The set is measured, not listed: the moved driver's non-standard-library preloads, less the original driver's own tool modules renamed by rule 3's table (`sysml_codegen.study.read_coverage` is the original's `scripts.study.read_coverage`). It is recorded in `preloads.json` as `installed_package_modules`. Evidence: three exclusions per route case (key `B1/B8 preloaded installed-package module`).

**Q2: the harness choices the first run made, ratified as listed.**

- **`SYSML_CODEGEN_PROJECT_ROOT` in the orig environment.** See "The environment" above. It gives the moved library, which the fixture route imports in both modes, the root the moved seam would export (B1). The original seam and driver predate it, so the original environment needs it. Since `2e21955` the moved `run_route` pins the root itself, so the variable stays only for the original side. Evidence: without it, both orig runs of `CANDIDATE` refused at gate 7 with `unsupported integer-descriptor open: 3`, while moved returned `CANDIDATE`. It masks nothing.
- **A B7 row in rule 3's table.** Gate 1b's refusal detail names the simkit root (`TEAX_SIMKIT_PATH`) where the original named the checkout root (`STOP_PARSER_TEAX_ROOT`), as Phase 3 recorded. The mapping is one exact string, scoped to gate 1b's detail. Evidence: `integrate-g1b-refused`, key `B7 gate 1b teax root` ×2.
- **Three noise patterns beyond Appendix G's list.** Each changes between orig and orig2, so each is noise by rule 2's own test.
  - `junit-clock`: pytest's junit `time` and `timestamp`, the same timing as `in N.NNs` (198 applications).
  - `atomic-write-temp`: `common.write_document`'s `mkstemp` names (24).
  - `teax-staging-directory`: teax's uuid staging directories (12).

  The last two appear only in a receipt's `attempted_new_output_creations`. Appendix G's read-coverage token pattern is matched as the run's own token, exactly, rather than as any 32-hex string.
- **Comparison choices.**
  - integrate's stderr is its human summary. Each run's stderr is checked to equal `human_summary` of its own return, and the returns are then compared.
  - teax's `out/_work/` (SQLite stores, package links) is compared by file listing; its bytes are teax's, not tool documents.
  - The preflight stale-manifest case stales `recorded_provenance`, because that is what `preflight gates`' `manifest_currency` check reads. integrate's gate-6 case stales the pin, which is what gate 6 reads.
  - **Evidence size.** `cases/<case>/{orig,moved}.json` hold each run's normalized outputs. A receipt is summarized there by category counts, and the recaptured snapshot by its length, because the full bytes (about 800 kB per receipt) stay in `$S/runs`. `comparison.json` lists every difference in full.

## Files

- `parity.py`, `make_venv.sh`, `patterns.json`: the harness.
- `preloads.json`: the measured preload set: the standard-library modules (B13 consequence) and the installed-package modules (Q1 rule 3).
- `report.md`: generated; the sources, environment, library parity, per-case status, rule and pattern counts, and every difference.
- `results.json`: the same, machine-readable, with the setup record.
- `cases/<case>/`: `comparison.json`, `orig.json` and `moved.json` per case.
