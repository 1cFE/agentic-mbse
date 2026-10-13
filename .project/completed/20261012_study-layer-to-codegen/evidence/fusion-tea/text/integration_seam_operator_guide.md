# Operating the integration seam in fusion-tea

The general operator guide ships with sysml-codegen, in the run-study bundle: `.agents/skills/run-study/integration-guide.md`, also reachable as `.claude/skills/run-study/integration-guide.md`. `sysml-codegen install-commands` installs it. It holds everything that is true of the seam in any project: the ten gates, the fifteen conditions and what to do about each, the exit codes, the project's declaration, the project-root rule, the snapshot rule, and what the seam writes. Read it first.

This page is fusion-tea's supplement: what is true of the seam only here. Each section names the general guide's section it adds to. `scripts/integrate.py` is fusion-tea's alias of the installed seam, so `python scripts/integrate.py …` and `sysml-codegen study integrate …` are the same command in this repository.

---

## The full invocation in fusion-tea

Adds to the general guide's "The full invocation, first".

```bash
uv run --env-file ~/1cfe/agentic-mbse/.env --env-file .venv/integration.env \
  python scripts/integrate.py \
    --audited-work work/completed/20260822_WI-030_computed-beta-peak-field@ba5c9945 \
    --models-root  exploration/stellarator_e2e/models \
    --package      exploration/stellarator_e2e/pkg/stellarator_tea \
    --manifest     exploration/stellarator_e2e/studies/manifest.json \
    --groups       tests/study/data/axes.known_answers.json \
    --census-file  tests/models/data/mfe_census.json \
    --expected-semantic-fingerprint   1ca93d0c988c2828bb1ce3fef18be85be86947a296a33b236d77daeb0f1ab860 \
    --expected-executable-fingerprint 7447efea9f205dc64543a976e6a3c21a9fd468726f2de78aaf8d845e6f2d9a97 \
    --expected-teax-revision          744745f895677f3344b9884627369a6a47ed987f \
    --route-sys-path exploration/stellarator_e2e/studies \
    --route-module   study_route \
    --route-callable execute_baseline \
    --out-dir        /tmp/integration-run
```

For the current supplied-design stellarator interface (WI-075–078), use `--groups exploration/stellarator_e2e/studies/axes.supplied_design.json`. The older known-answer declaration in the historical example above contains the retired ampere-turn input; it belongs to its original interface. The current excitation axis supplies amperes per turn while installed turns and pack geometry remain independently chosen.

A full run takes about 15–20 seconds. Most of it is the model-family spine suite and the baseline execution.

## Where each input comes from in fusion-tea

Adds to the general guide's "Where each input comes from".

- `--audited-work`: the work item you are integrating, cited `PATH@COMMIT` — ADR-0006's citation form (`.project/adr/0006-goal-evidence-seam.md`).
- `--models-root`: for the stellarator package, `exploration/stellarator_e2e/models`.
- `--manifest`: the study-package manifest beside the route, `studies/manifest.json` in the package's studies directory (`modeling_project/STUDY_POLICY.md` § 12).
- `--groups`: the axis declaration preflight calls `--groups`. The known-answer declaration under `tests/study/data/` is the usual one.
- `--census-file`: `tests/models/data/mfe_census.json`.
- `--expected-teax-revision`: `git -C "$STOP_PARSER_TEAX_ROOT" rev-parse HEAD` at the revision the audited work ran under. It is the same revision `git -C "$TEAX_SIMKIT_PATH" rev-parse HEAD` reads, because `TEAX_SIMKIT_PATH` lies inside that checkout.

## The environment in fusion-tea

Adds to the general guide's "The environment".

```bash
# The SysIDE licence. Generation and snapshot capture will not run without it.
export SYSIDE_LICENSE_KEY=...          # in ~/1cfe/agentic-mbse/.env, which does not export it itself

# The sealed toolchain artifacts. tests/test_dependency_provenance.py reads all four.
export STOP_PARSER_WHEEL_TARGET=/home/reid/1cfe/fusion-tea/.venv/lib/python3.12/site-packages
export STOP_PARSER_AGENTIC_WHEEL=/home/reid/1cfe/stop-parser-sealed-wheels/agentic_mbse-0.1.3-py3-none-any.whl
export STOP_PARSER_CODEGEN_WHEEL=/home/reid/1cfe/stop-parser-sealed-wheels/sysml_codegen-0.1.1-py3-none-any.whl
export STOP_PARSER_COSTINGFE_WHEEL=/home/reid/1cfe/stop-parser-sealed-wheels/1costingfe-0.1.0-py3-none-any.whl

# The teax checkout, and teax's simkit root inside it. The seam reads the teax revision from
# TEAX_SIMKIT_PATH; verify imports simkit from the environment and does no sys.path work.
export STOP_PARSER_TEAX_ROOT=/home/reid/1cfe/teax
export TEAX_SIMKIT_PATH=$STOP_PARSER_TEAX_ROOT/packages/teax-simkit
```

**The sealed wheels.** `/home/reid/1cfe/stop-parser-sealed-wheels/` holds the three wheel files whose sha256 values are pinned in `tests/test_dependency_provenance.py::WHEEL_HASHES`. They are outside the repository and are not installed by `uv`. If gate 1a refuses with a hash mismatch, check that these three paths point at those files before reading it as toolchain drift — verify with `sha256sum` against `WHEEL_HASHES`.

**Two `--env-file` flags instead of `export`.** The repository keeps the six `STOP_PARSER_*` values and `TEAX_SIMKIT_PATH` in `.venv/integration.env` (gitignored), so the whole environment is two flags on `uv run`:

```bash
uv run --env-file ~/1cfe/agentic-mbse/.env --env-file .venv/integration.env python scripts/integrate.py ...
```

**All six variables are checked before any producer runs.** Gate 0 sweeps `SYSIDE_LICENSE_KEY` and the five variables fusion-tea's declaration lists. `tests/test_dependency_provenance.py` reads the four wheel variables inside its *test body*, so an absent one raises a `KeyError` that pytest records as a test failure — which any seam that let gate 1a run first would report as a genuine toolchain refusal.

## Running from a second checkout or worktree

Adds to the general guide's "The environment". Both files above are checkout-local facts, and `uv run` is not usable from a secondary checkout: it resolves that checkout's own venv, and the seam launches every producer via `sys.executable`, so the producers would run outside the sealed environment (`--no-sync` does not redirect this). The working pattern, proven by the 2026-08-29 route-equivalence exercise, is to run the primary checkout's sealed interpreter directly, from the secondary checkout's root, with the environment sourced:

```bash
set -a
source ~/1cfe/agentic-mbse/.env
source /path/to/primary-checkout/.venv/integration.env
set +a
/path/to/primary-checkout/.venv/bin/python scripts/integrate.py ...
```

`STOP_PARSER_WHEEL_TARGET` keeps naming the primary checkout's `site-packages` — that is correct, because that venv's interpreter is the one running. This is the one documented exception to the repository's always-`uv` rule, scoped to secondary checkouts (CLAUDE.md § Python Environment).

## fusion-tea's declaration

Adds to the general guide's "The project's declaration". fusion-tea's `pyproject.toml` declares both repo-scope gates, the five variables its gate-1a producer reads, the 1costingFE distribution its returns record, and its backup prefix:

```toml
[tool.sysml-codegen.integrate]
environment = ["STOP_PARSER_WHEEL_TARGET", "STOP_PARSER_AGENTIC_WHEEL", "STOP_PARSER_CODEGEN_WHEEL", "STOP_PARSER_COSTINGFE_WHEEL", "STOP_PARSER_TEAX_ROOT"]
backup-prefix = "fusion-tea-integration-backup-"
record-distributions = { costingfe = "1costingfe" }
[tool.sysml-codegen.integrate.gates.pinned-packages]
target = "tests/test_dependency_provenance.py"
checked = "the pinned package revisions and installed wheel artifacts"
[tool.sysml-codegen.integrate.gates.model-family-spine]
target = "tests/models/test_model_family_spines.py"
checked = "the canonical tree, the family twins and the tracked census"
```

- **Gate 1a** runs `tests/test_dependency_provenance.py` — the pinned revisions and the installed wheel artifacts. The provenance suite reads `pyproject.toml`, `uv.lock` and the installed wheels.
- **Gate 5** runs `tests/models/test_model_family_spines.py` — the canonical tree, the family twins, the tracked census. The spine suite generates from the repository's canonical `models/` tree and compares against the tracked `tests/models/data/mfe_census.json`.
- Gate 5 reads the **tracked** `tests/models/data/mfe_census.json` whatever you passed. It is the spine suite's own input and the flag does not reach it.
- A `census-stale` refusal means: re-derive `tests/models/data/mfe_census.json` from the new package. Never hand-patch it to match.

## Reading a fusion-tea answer

Adds to the general guide's "Reading the answer" and its conditions table.

- **The stellarator package root is a symlink.** Pass `--package exploration/stellarator_e2e/pkg/stellarator_tea` and the candidate names `exploration/stellarator_e2e/generated`. Both paths name the same package.
- **`toolchain-drift`.** Check the sealed-wheel paths first, **and** that `STOP_PARSER_WHEEL_TARGET` names the `site-packages` of the interpreter actually running — from a second checkout or worktree the default venv fails that check as a path mismatch, which is environment misconfiguration, not drift (see § Running from a second checkout or worktree). Only if both are right has the toolchain genuinely moved and the audited work's lineage no longer held.
- **Citing a candidate**, in this repository's form:

```bash
uv run --env-file ~/1cfe/agentic-mbse/.env --env-file .venv/integration.env \
  python scripts/study/preflight.py gates \
    --package  "$(jq -r .candidate.package  <out-dir>/integration_return.json)" \
    --manifest "$(jq -r .candidate.manifest <out-dir>/integration_return.json)" \
    --groups   "$(jq -r .request.groups     <out-dir>/integration_return.json)" \
    --identity "$(jq -r .candidate.identity_document <out-dir>/integration_return.json)" \
    --baseline-result "$(jq -r .candidate.baseline_result <out-dir>/integration_return.json)"
```

- **Temporary files.** Study import aliases also use temporary directories and are removed at normal process exit.

## Open rows fusion-tea tracks against the seam

- Gate 1b has no producer anywhere; the gap is filed.
- **`verification-refused`.** A teax import failure the gate-0 probe did not predict arrives labelled `refused`. That shortfall is filed against `scripts/study/verify.py`.
- **`verify.py` records `teax.revision: "unrecorded"`.** The seam records the checkout's git revision in the return's `toolchain` block, but that does **not** discharge the open row against `verify.py`.
- **Gate 5's refusal path is not covered by a test.** Its pass path and its could-not-run path are; driving a real refusal out of it would need an edit to a tracked file or to a frozen producer. The shared junit-to-refusal mapping *is* proven, by gate 1a's wheel-hash fixture.

## Related

- `.project/adr/0009-integration-is-a-fixed-point-proof.md` — why the seam proves rather than performs.
- `tests/study/test_integrate_*.py` — the seam's own tests, including five real refusals from real producers.
- `modeling_project/STUDY_POLICY.md` § 12 — where each package's studies directory is.

## Historical reproduction scripts

Adds to the general guide's "Keep disposable execution files outside the project". For historical reproduction scripts with an `--out` option, choose a new external directory; retain the resulting native stores, artifact JSON and verification receipts deliberately, rather than committing copied package/tool trees. Do not rewrite frozen scripts to change their temporary paths. Narrow ignore rules cover import aliases and the old archive review's pytest workspace if those historical scripts are replayed.
