# Implementation Plan: Guidance that keeps generated results honest (EXEC-SUBSET-CONTRACT Item 5, rescoped)

**Status:** In Progress
**Created:** 2026-10-22
**Last Updated:** 2026-10-22

## Source Documents

- **Spec:** [spec.md](spec.md) (Risks 1 to 4, five success criteria)
- **Design:** [design.md](design.md), revised after the design review. Component detail, bets, decisions and invariants live there; this plan links to them and does not restate them.
- **Design review:** [design-review.md](design-review.md) § Resolutions (M1 to M3, S1 to S7 dispositions)
- **Spike:** [spike/RESULTS.md](spike/RESULTS.md), probes in `spike/native-path/` and `spike/channel-trace/`, runner `spike/codegen.sh`
- **Repos:** agentic-mbse `/home/reid/src/subset-conformance/agentic-mbse` (branch `generated-results-guidance`); sysml-codegen `/home/reid/src/subset-conformance/sysml-codegen` (new branch `native-generated-compare` from `origin/main`); dc3 `/home/reid/src/dc3` and TEAx `/home/reid/src/teax` are read-only.

## The Point

Since ADR 0004, a model the generator refuses is cheap: `sysml-codegen check` says so early and loudly. The risk that remains is a model that passes `check`, generates, and computes different numbers from the native model, or a package whose failed verdicts nobody reads. That failure looks like success. [OWNER, 2026-10-22] "Mitigate actual risk, not ceremony."

The obligation this work serves [AGENT, ratified by owner at launch 2026-10-22]: a modeller following the shipped workflow must catch a model that passes `check` and generates but computes different numbers than the native model. Better docs alone do not meet it, so the item ships a command that runs both routes on the modeller's own model: `sysml-codegen compare`. It checks part counts, output values and constraint verdicts, and its exit code says when it could not compare everything (exit 0 only when everything was compared and nothing differs). [INHERITED: ADR 0004] Only the generator says what it builds; agentic-mbse keeps no copy of its rules, imports nothing from sysml-codegen, and treats a missing or failed tool as "not compared", never "fine".

Alongside the command, the guidance is fixed for the other three risks: the guide says an assert never stops a computation on either route (Risk 2); teaching sites for conditionals and library functions say to run `check` first (Risk 3); and every guidance claim about generator behaviour has a recorded run and an upstream row naming the guidance to update when the generator changes (Risk 4). Each Risk 1 case is re-run on current sysml-codegen `main` and recorded.

## Implementation Strategy

**Phasing rationale.** The command rests on four bets that nobody has run (design B2, B3, B4, plus the B1 shapes the spike did not cover). If any fails, the design changes, so Phase 1 tests them all with throwaway probes before any production code exists. Phase 1 is a hard gate: a failed bet stops the work and goes back to the orchestrator. After that, sysml-codegen is built bottom-up: the read-only accessor first, guarded by the byte-identity check (RG-1), then the command, then its verdict and edge-case coverage. The agentic-mbse text comes after the command's behaviour is fixed, so the workflow text describes what the command actually does. The Risk 1 re-runs use the finished command, and the upstream rows come last because they cite the re-run results.

**Critical path.** Phase 0 (branch, baselines) → Phase 1 (bets, gate) → Phase 2 (accessor, byte identity) → Phase 3 (`compare`: counts, values, exits) → Phase 4 (verdicts, report, edge cases) → Phase 5 (agentic-mbse text and pins) → Phase 6 (Phase R re-runs and dc3 run) → Phase 7 (Phase U upstream rows). Phase 5 can start once Phase 4's exit codes and report shape are committed; it does not need Phase 6.

**First proof point.** Phase 1's probe, switched to the effective usage, gives the expected native value and count on the dc3-shaped redefinition model, and marks `pack.total` as not compared under `pack.cells (3)` on the literal `Cell[3]` model while marking nothing on the `[1]` model.

**Repos and commits.**

| Phase | Repo | Branch | Commits |
|---|---|---|---|
| 0 | both | sysml-codegen: create `native-generated-compare`; agentic-mbse: `generated-results-guidance` | agentic-mbse (baseline evidence) |
| 1 | agentic-mbse (read-only in sysml-codegen) | `generated-results-guidance` | agentic-mbse |
| 2, 3, 4 | sysml-codegen | `native-generated-compare` | sysml-codegen, one or more per phase |
| 5, 6 | agentic-mbse | `generated-results-guidance` | agentic-mbse |
| 7 | sysml-codegen (plus a one-line agentic-mbse status edit) | `native-generated-compare` | sysml-codegen, then agentic-mbse |

No pushes, PRs or merges in any phase (owner, RG-3). Do not touch sysml-codegen's `subset-profile-screen` branch: do not delete, reset or commit to it.

**Overall validation approach.**
- Each phase writes its tests (or, for Phase 1, its expected probe values) before the code.
- Each phase ends with an exit check: commands and the expected results, listed in the phase.
- Both suites stay at their recorded base failures (Phase 0). A new failure blocks the phase.
- Every phase names the spec risk it reduces.

---

## Environment Setup

**Licence.** Every SysIDE-touching command needs `SYSIDE_LICENSE_KEY`: `set -a; source /home/reid/src/subset-conformance/agentic-mbse/.env; set +a`. sysml-codegen's licensed tests skip without it, so a green run with no key is not a full run (sysml-codegen `CLAUDE.md`, Commands).

**Test commands.**
- agentic-mbse: `uv run pytest tests/` (repo `CLAUDE.md`), `uv run ruff check src/ tests/`.
- sysml-codegen default lane: from the sysml-codegen root, `uv run --extra dev pytest tests/`, `uv run --extra dev ruff check src/`, `uv run --extra dev mypy src/`. sysml-codegen's own venv cannot import simkit (no `pandas`), so every test that runs a package skips there.

**The simkit lane (how sysml-codegen tests get simkit).** simkit comes from `/home/reid/src/teax/packages/teax-simkit`, as in the spike (`spike/codegen.sh`). The interpreter is the agentic-mbse worktree's venv (`/home/reid/src/subset-conformance/agentic-mbse/.venv/bin/python`), which has `pytest`, SysIDE, `pandas` and simkit's other dependencies (orchestrator-verified 2026-10-22: `import pandas, simkit, pytest, syside` succeeds with teax-simkit on `PYTHONPATH`). This matches sysml-codegen's existing `execution` marker note (`pyproject.toml:50`, "needs the agentic-mbse venv with teax-simkit on sys.path") and keeps sysml-codegen's tests independent of any consumer project. The sysml-codegen and agentic-mbse sources go first on `PYTHONPATH`, so the venv's own installed copies are not used. No bytecode is written, so dc3 and TEAx stay clean. From the sysml-codegen root:

```bash
set -a; source /home/reid/src/subset-conformance/agentic-mbse/.env; set +a
PYTHONPATH=src:/home/reid/src/subset-conformance/agentic-mbse/src:/home/reid/src/teax/packages/teax-simkit \
PYTHONDONTWRITEBYTECODE=1 \
/home/reid/src/subset-conformance/agentic-mbse/.venv/bin/python -m pytest tests/compare -p no:cacheprovider -rs
```

Call this "the simkit lane" below. It does not use sysml-codegen's existing `execution` marker lane (`tests/execution/`), because that lane's autouse fixture requires a `CODEGEN_EXECUTION_PROVENANCE` manifest (`tests/execution/conftest.py:14-24`), which this work does not build.

**What a simkit-needing test does when simkit is missing.** It skips with a stated reason; it never passes silently. `tests/compare/conftest.py` defines `requires_simkit`, a `pytest.mark.skipif` with reason `"simkit (TEAx teax-simkit) is not importable; run the simkit lane (plan.md, Environment Setup)"`, in the same style as `requires_license` (`tests/conftest.py:25-39`). The exit check of each sysml-codegen phase runs the simkit lane and requires **0 skipped** in `tests/compare`, so a lane that silently lost simkit fails the check. The test of `compare`'s own "simkit missing" exit does not depend on the environment: it forces the import to fail (`monkeypatch.setitem(sys.modules, "simkit", None)`), so it runs in both lanes.

**Running `compare` by hand** (Phases 4, 6): `spike/codegen.sh -m sysml_codegen compare --models <dir>` from agentic-mbse's `spike/` folder. `codegen.sh` puts the sysml-codegen checkout's `src` first, so it runs whatever branch that checkout has; check it is on `native-generated-compare`.

**Scratch output.** Packages, runs and byte-identity records go under `/tmp/grg-impl/`, outside every repo.

---

## Phase 0: Branch and baselines

### Goal
Create the sysml-codegen branch and record what "no regression" means before anything changes.

### Risk it reduces
None directly. It makes every later exit check decidable: base failures (all phases), the RG-1 "before" record (Phase 2), and the toolchain revisions (Phases 1 and 6).

### Steps
- [x] sysml-codegen: confirm `git -C /home/reid/src/subset-conformance/sysml-codegen status --short` is empty. If not, stop and report; do not stash or discard someone else's changes.
- [x] sysml-codegen: `git -C … fetch origin main`, then `git -C … switch -c native-generated-compare origin/main`. Record the `origin/main` SHA. The design and spike used `6190f996`; if `origin/main` has moved, record the new SHA and whether `git diff --stat 6190f996 origin/main -- src` is empty.
- [x] Record the revisions: agentic-mbse HEAD, sysml-codegen `origin/main`, TEAx HEAD (`git -C /home/reid/src/teax rev-parse HEAD`; the spike had `8d877460`), dc3 HEAD, SysIDE version.
- [x] agentic-mbse base failures: `uv run pytest tests/ -q -rf`. Expect 5 failures. Record their test IDs.
- [x] sysml-codegen base failures, licence sourced: `uv run --extra dev pytest tests/ -q -rf`. Expect 9 failures. Record their test IDs and the skip count.
- [x] If either count differs from 5 or 9, record the actual IDs and continue; the recorded IDs are the base. Say so in the notes.
- [x] Simkit lane smoke check: run the simkit-lane interpreter with `-c "import sysml_codegen, agentic_mbse, simkit, syside, pytest; print(sysml_codegen.__file__, simkit.__file__)"`. Both paths must resolve under the subset-conformance checkout and TEAx's `teax-simkit`. Then `… -m pytest tests/unit/test_teax_discovery.py -p no:cacheprovider -q` must collect and pass, which shows sysml-codegen's `tests/` package imports under that interpreter.
- [x] RG-1 "before" record (see Phase 2 for the corpus): run the three byte-identity records now, on the untouched `origin/main` code, into `/tmp/grg-impl/identity-before/`.
- [x] Write `.project/active/generated-results-guidance/evidence/baseline.md` with all of the above (revisions, both failure-ID lists, skip counts, lane smoke output, the byte-identity record paths and their own sha256).

### Exit check
- `git -C …/sysml-codegen branch --show-current` → `native-generated-compare`.
- `evidence/baseline.md` lists both failure-ID sets, the revisions and the three "before" record files.
- Commit in agentic-mbse: `evidence/baseline.md` (and nothing else).

---

## Phase 1: De-risk the bets (the gate)

### Goal
Run design bets B2, B3 and B4 together, plus the B1 shapes the spike did not cover, on real models with throwaway probes, before any production code. See [design.md § Key Bets](design.md#key-bets) and [§ Implementation Notes](design.md#implementation-notes), step 1.

### Risk it reduces
Risk 1. A wrong bet means `compare` reports false differences on correct packages, or reports agreement on a value both routes got wrong. That second failure is the one the item exists to prevent.

### The gate
**If any bet below fails, stop.** Write the result and the design's stated fallback for that bet into `spike/derisk/RESULTS.md`, commit it, and report to the orchestrator. Do not redesign, do not apply the fallback, and do not start Phase 2. "Fails" means a row's observed result contradicts its expected result in the table below and the cause is the bet, not a probe bug. If you cannot tell which, that is also a stop.

### Assumptions under test

| Bet | Assumption | Fails if |
|---|---|---|
| B2 | Marking every node whose scope is inside an occurrence of a slot with a count other than 1, plus everything downstream, finds every output SysIDE gets wrong because of a multiplicity. A zero-occurrence slot can be found from the reading expression's reference. | A wrong native value is left unmarked; a `[1]` or named-subset model gets marked; or no data in the graph identifies the `[0]` reference (then B2's zero rule has no input; design "Open" item). |
| B3 | `OccurrenceRecord.effective_usage_id` (`elaboration/graph.py:150`) is the right SysIDE scope and the right source of a multiplicity bound. | On the dc3-shaped model, native value or native bound under the effective usage differs from the model's meaning, or from the generated value and built count. |
| B4 | With only the innermost effective usage as scope, SysIDE sees a value redefined two levels further out. | Native gives the inner default where the model's meaning (and the generated value) is the outer redefinition. |
| B1 (shapes) | `evaluate_feature` gives the right value for quantities with units, Integer outputs, Boolean outputs, models split across files, and a calc usage nested two levels inside indexed occurrences (value marked by B2, but the trace must still hold). | A false difference on any of these. |

### Test stencil (write the expected values first)

Write `spike/derisk/EXPECTED.md` before running anything: one row per (model, item) with the model's intended value, the expected generated value, the expected native value, and the expected mark. Then the probe compares against it:

```python
# spike/derisk/probe_derisk.py — sketch; reuse spike/channel-trace/probe_channels.py
rows = trace(models)                      # channel -> calc node, output decl, chain
for row in rows:
    occ = [graph.occurrences[OccurrenceId(scope.steps[: i + 1])] for i in range(len(scope.steps))]
    row["scope_decl"] = occ[-1].effective_usage_id.value      # B3: not containment_slot.root_declaration
    row["mark"] = multiplicity_mark(graph, row)                # B2: slot count != 1, plus downstream; [0] via reference
counts = count_rows(graph)                # per (effective usage, owning occurrence): bound vs built
native(models, rows, counts); generated(models, scratch, name, rows)
assert_against(EXPECTED, rows, counts)    # prints PASS/FAIL per row; exit 1 on any FAIL
```

### Changes required (agentic-mbse only; read-only in sysml-codegen)

#### 1. Models — `spike/derisk/models/<case>/model.sysml` (NEW)
- [x] Reuse: `s1_gen`, `default_count`, `default_count_literal` from `spike/channel-trace/models/`; `gen_reversed`, `gen_byname` from `tests/fixtures/positional_binding/native_values/`.
- [x] `zero_slot`: a part with `x : X[0]` and an attribute `total = sum(x.v)` (expected: generated 0; marked "multiplicity … (0)").
- [x] `one_slot`: `cell : Cell[1]` with a value read through it (expected: index 0 in the graph, compared, not marked).
- [x] `named_subsets`: `racks : Rack[2]` with `rack_1 :> racks`, `rack_2 :> racks`, one of them redefining a value (`:>> capacity = 4.0`), and a total computed from the named parts, the dc3 shape (`/home/reid/src/dc3/models/designs/`). Expected: named-part values compared and not marked; anything reading `racks` itself marked.
- [x] `dc3_redefinition`: a specialised part def that redefines a contained part and an attribute value inside it (`part :>> electrical { attribute :>> load = 5.0; part :>> racks[3]; }`), mirroring `dc3/designs/dc_native/dc_facility.sysml`. Expected: native value under the effective usage = 5.0 = generated; native bound 3 = built 3. Also record, for contrast, the native result with the slot root as scope (this shows why M2 mattered; it is not a pass condition).
- [x] `outer_redefinition`: an outer part redefining a value inside a nested part two levels down (B4). Expected: generated and native both give the outer value.
- [x] `units_int_bool`, `split_files` (two `.sysml` files), `nested_indexed` (calc usage two levels inside `[3]` occurrences): B1 shapes.
- [x] Ask the `sysml-expert` or `sysmlv2-validator` agent when unsure how to write a shape; every model must load in SysIDE and pass `sysml-codegen check` (exit 0) before it counts. A model that `check` refuses is recorded as such and replaced with a shape that generates.

#### 2. Probe — `spike/derisk/probe_derisk.py` (NEW)
- [x] Copy `spike/channel-trace/probe_channels.py` and `probe_count.py`; switch the native scope from `containment_slot.root_declaration` (`probe_channels.py:43`) to `OccurrenceRecord.effective_usage_id`.
- [x] Implement the B2 mark from the instance graph: slot counts per (parent occurrence, containment slot); nodes scoped inside an occurrence of a slot with count ≠ 1; downstream closure over consumer edges. For `[0]`, find what the graph records for the reading expression's reference to an empty slot, and record which field it is (this closes the design's Open item "the exact data for the zero-occurrence mark").
- [x] Count rows: per (effective usage, owning occurrence), SysIDE's bound from the effective usage's multiplicity in the owner's effective-usage scope, against built occurrences.
- [x] Run through `spike/codegen.sh`; scratch under `/tmp/grg-impl/derisk/`.

#### 3. Record — `spike/derisk/RESULTS.md` (NEW)
- [x] Same shape as `spike/RESULTS.md`: revisions, commands, output, a verdict per bet (holds / fails), and the zero-slot data source.

### Exit check
- `spike/codegen.sh spike/derisk/probe_derisk.py` exits 0, with every row PASS against `EXPECTED.md`.
- `git -C /home/reid/src/subset-conformance/sysml-codegen status --short` is empty, and so is TEAx's and dc3's.
- No `__pycache__` left under `spike/` (delete it if `uv run` made one).
- Commit in agentic-mbse: `spike/derisk/`.
- **Gate:** all four bet verdicts "holds". Otherwise stop and report (above).

### What we know after this phase
The scope, count and marking rules `compare` will use are correct on the shapes that matter (dc3's redefinitions and named subsets, `[0]`, `[1]`, `Cell[3]`, two-level redefinition), and we know which graph field gives the zero-slot mark.

---

## Phase 2: The read-only trace accessor, and byte identity

### Goal
Give `compare` a public, read-only view of the generator's trace (design D2), without changing anything the generator builds (invariant 2, RG-1).

### Risk it reduces
Risk 1 (the trace is what lets `compare` find each output's SysML feature, scope and count). The byte-identity check guards RG-1: no change to what the generator builds.

### Assumption under test
A fresh `_Projection(graph).run()` on the decoded instance graph gives the same channel names the shipped package has, and exposing it changes no generated byte.

### Test stencil (write first)

```python
# tests/conformance/test_output_trace.py   (licensed: pytestmark = requires_license)
def test_every_output_channel_traces_to_a_declaration_and_effective_usages():
    trace = trace_for(FIXTURES / "compare" / "default_count_literal")
    assert {row.channel for row in trace.channels} == set(public_channels_of(generated_contract))
    total = trace.channel("Packs__pack__total__total")
    assert [step.effective_usage_id for step in total.chain] == [pack_usage_id]
    assert total.not_compared.cause == "multiplicity" and total.not_compared.slot_display == "pack.cells"
    assert total.not_compared.count == 3

def test_one_slot_is_indexed_but_not_marked(): ...
def test_dc3_redefinition_uses_effective_usage_for_scope_and_bound(): ...   # bound 3, built 3
def test_zero_slot_marks_the_reader(): ...
```

### Changes required
**See design:** [D2](design.md#key-decisions) (record contents), [D5](design.md#key-decisions) (causes, "indexed" means count ≠ 1), [B2 to B4](design.md#key-bets), invariant 2 in [Required Invariants](design.md#required-invariants). Phase 1's `probe_derisk.py` is the working reference for every rule.

- [ ] **Fixtures** — `tests/fixtures/compare/<case>/model.sysml` (NEW): copy Phase 1's models (including `gen_reversed` and `gen_byname`, which sysml-codegen cannot read from agentic-mbse's tree). Add a short `README.md` naming each case and its expected result. These are not part of the committed corpus batch (`tests/fixtures/v6_recapture_batch/batch.json`); do not add them there.
- [ ] **Tests** — `tests/conformance/test_output_trace.py` (NEW, licensed), per the stencil. Add a case for a named subset as its own slot.
- [ ] **Accessor** — `src/sysml_codegen/elaboration/project.py` (beside `_Projection`, `:260`): a public function that takes an `InstanceGraph`, runs a fresh `_Projection(graph).run()`, and returns frozen dataclass records for channels, not-compared marks and counts. `project()`'s signature and return value do not change. `_Projection` stays private. Export the function and record types from `elaboration/__init__.py`.
  - `project.py` is a guarded boundary file (`tests/unit/test_elaboration_import_boundaries.py:12-19`): the new functions must not select by string prefix/suffix or parse names. Identity comes from `OccurrenceId`, `DeclarationId` and `effective_usage_id`; display strings come only from the graph's display helpers (`graph.occurrence_display_path`, `graph.py:1018`). Do not add an exemption.
- [ ] **Read path for the instance graph** — `src/sysml_codegen/orchestration/exact_pipeline_context.py`: the instance graph is sealed inside `ExactPipelineContext` (`:158-216`) and `prepare()` keeps only the `ComputationGraph` (`cli/prepare.py:209-230`). Add one public read on the context that decodes the instance bytes after the same fingerprint check `_verified_projection` makes (`:200-216`), and returns the decoded `InstanceGraph`. It must not mutate the context. Search `tests/` for tests that pin the context's public surface and update them with a reason if needed.
  - Design gap noted, not a deviation: design D2 says "on the prepared graph", but `Prepared` has no instance graph. This read path is the smallest way to give the accessor its input without touching `prepare()`.
- [ ] Run `ruff` and `mypy` on `src/`.

### Byte-identity check (RG-1; phase exit criterion)
The corpus, per design invariant 2: sysml-codegen's test fixtures, the spike and Phase 1 models, and dc3 `models/`. The comparison covers the whole generated tree, `contracts/` and fingerprints included, with nothing normalised.
1. **sysml-codegen fixtures:** `uv run --all-extras python scripts/package_manifest.py record /tmp/grg-impl/identity-before/fixtures.json` (Phase 0, on untouched code), and after the change `… package_manifest.py compare /tmp/grg-impl/identity-before/fixtures.json`. That script already records every 2a case the generator builds and every committed v6 snapshot, live and replayed, as relative path → sha256 for every written file (`scripts/package_manifest.py:1-19`).
2. **Spike and Phase 1 models:** for each model directory, `uv run sysml-codegen generate --models <dir> --output /tmp/grg-impl/identity-<before|after>/spike/<case> --package-name <case>`; then `diff -r` before against after.
3. **dc3:** the same for `/home/reid/src/dc3/models` (package name `dc3_models`). If dc3 refuses, the before and after refusal output must be identical; record which.

Expected: `package_manifest.py compare` exits 0; both `diff -r` runs print nothing. Record the commands and results in the sysml-codegen commit message and in Phase 2's implementation notes.

### Exit check
- `uv run --extra dev pytest tests/conformance/test_output_trace.py` (licensed) → all pass.
- `uv run --extra dev pytest tests/` → failures equal the Phase 0 sysml-codegen IDs, no new ones.
- `uv run --extra dev ruff check src/` and `uv run --extra dev mypy src/` → clean.
- Byte-identity: as above, zero differences.
- Commit in sysml-codegen on `native-generated-compare`.

### What we know after this phase
The generator exposes, read-only, everything `compare` needs, and the generated tree for the whole named corpus is byte-identical.

---

## Phase 3: `sysml-codegen compare` — counts, values and exit codes

### Goal
The command itself: load and prepare like `check`, build into a temporary folder, run once with simkit, and check counts and values against SysIDE, with exits 0/1/2/3/4. See [Core Concept](design.md#core-concept), [D6, D7, D8, D10, D11](design.md#key-decisions), [Architecture](design.md#architecture).

### Risk it reduces
Risk 1: a model that generates but computes different numbers or builds the wrong part count is caught, and a partial comparison never exits 0.

### Assumption under test
The Phase 1 rules hold when run end to end through the real package run, on every model in `tests/fixtures/compare/`.

### Test stencil (write first)

```python
# tests/compare/test_compare_exits.py   (simkit lane; pytestmark = [requires_license, requires_simkit])
@pytest.mark.parametrize(("case", "code", "expect"), [
    ("gen_reversed",          1, "differ value diff.r native -7.0 generated 7.0"),
    ("default_count",         1, "differ count pack.cells native 3 built 2"),
    ("default_count_literal", 4, "multiplicity pack.cells (3)"),
    ("zero_slot",             4, "(0)"),
    ("one_slot",              0, "values: compared"),
    ("dc3_redefinition",      0, "counts: 1 of 1"),
])
def test_compare_exit_and_reason(case, code, expect, capsys):
    assert run_compare_cli(["--models", str(FIXTURES / case)]) == code
    assert expect in capsys.readouterr().out
```

```python
# tests/conformance/test_compare_command.py   (default lane; licensed, no simkit needed)
def test_simkit_not_importable_exits_3_environment(monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "simkit", None)
    assert cli_main(["compare", "--models", str(FIXTURES / "one_slot")]) == 3
    assert capsys.readouterr().out.startswith("environment: cannot import simkit")
def test_refused_model_exits_3_environment(): ...
def test_from_snapshot_is_a_usage_error(): ...   # argparse exit 2
```

Unit tests for the tolerance rule (D8) go in `tests/unit/test_compare_tolerance.py`: relative and absolute tolerance, Booleans and integers exact, NaN never agrees, worst deviation reported.

### Changes required
- [ ] **Package** — `src/sysml_codegen/compare/` (NEW), a small package per the design's Architecture "Layout". A split that keeps each step testable: native evaluation with SysIDE; running the package with simkit; judging (tolerance, agree/differ/not compared, grouping by cause); the report; and one entry function that composes them and returns a result with its exit code.
  - Load and prepare by reusing `prepare.load_source` and `refused_at_construction` (`cli/prepare.py:65-71`, `:209-230`), building the context with `exact_pipeline_context.build_exact_pipeline_context_from_live_load`, then `prepare.prepare_graph(context.computation_graph, name)`. This is `prepare()`'s own sequence, called step by step so `compare` keeps the context; `prepare()` itself does not change. A refusal gives exit 3 with `environment:` and the generator's refusal line (D6).
  - Build with `emit_package` into a `tempfile` folder (`--keep <dir>` keeps it). Load and run with TEAx's `ProvisionalPackageLoader` and `execute_pipeline`, following `tests/execution/real_teax.py:103-152` and the spike's `generated()` (channel values through the run manifest, since files are named by alias).
  - Import simkit lazily, inside the run step, from the environment only (D10). No `sys.path`, `PYTHONPATH` or `os.environ` work anywhere in `compare/`: `tests/conformance/test_public_authority_switch.py` (`_reads_the_environment`, `:578`) fails if a CLI-reachable module reads the environment. The error text is D10's, verbatim.
  - Native values: `syside.Compiler().evaluate_feature(feature, scope=<effective usage>)`, features found by element id, as Phase 1's probe does. A SysIDE diagnostic or no value gives "no native value" (D5).
- [ ] **CLI** — `src/sysml_codegen/cli/compare.py` (NEW): argument parsing only, like `cli/study.py`. Flags: `--models` (required), `--package-name`, `--keep`, `--verbose`, `--rel-tol`, `--abs-tol` (D8, D11, D12). Register the subcommand in `cli/__init__.py` `main()` (`:292-440`), next to `check`. `compare` takes no `--from-snapshot`.
- [ ] **Tests** — `tests/compare/__init__.py`, `tests/compare/conftest.py` (`requires_simkit`, Environment Setup above), `tests/compare/test_compare_exits.py`; `tests/conformance/test_compare_command.py`; `tests/unit/test_compare_tolerance.py`.
- [ ] Exit 1 takes precedence over 4 (D6): add one fixture-level test where a model has both a difference and a not-compared item (`default_count` already has both: the count differs and `total` is not compared).

### Exit check
- Simkit lane: `tests/compare` → all pass, **0 skipped** (`-rs` shows none).
- Default lane: `uv run --extra dev pytest tests/` → only the Phase 0 failure IDs; the `tests/compare` tests show as skipped with the `requires_simkit` reason, not as passed.
- `ruff` and `mypy` on `src/` → clean.
- Byte identity re-run (Phase 2 commands) → zero differences. `compare` adds no generation code, so this is a cheap confirmation.
- Commit in sysml-codegen.

### What we know after this phase
`compare` catches the two confirmed Risk 1 defects it can see (positional binding as a value difference, the default count as a count difference), reports multiplicity-dependent outputs as not compared, and only exits 0 on a full comparison.

---

## Phase 4: Verdicts, the report, and the remaining shapes

### Goal
Add verdict comparison (D9), the full report (D12, report header for B6), and tests for the shapes the design lists under "Not checked by the spike" in [Potential Risks](design.md#potential-risks).

### Risk it reduces
Risk 1 (verdict differences, untested shapes) and Risk 2 (the command prints the generated headline and lists violated verdicts, so a violated verdict is visible).

### Assumption under test
The native verdict (the usage's own result expression, else the definition's, with the effective usage as scope) joins to the generated verdict through the catalog's `usage_qualified_name` and `owner_instance_path` (`resolution/models.py:351-381`). The spike compared two verdicts by eye; this is the first join in code.

### Test stencil (write first)

```python
# tests/compare/test_compare_verdicts.py   (simkit lane)
def test_violated_assert_that_agrees_exits_0_and_prints_headline(capsys):
    assert run_compare_cli(["--models", str(FIXTURES / "s1_gen")]) == 0
    out = capsys.readouterr().out
    assert "violated" in out and "load_negative" in out          # headline + violated list
    assert "verdicts: 2 of 2" in out

def test_verdict_join_covers_every_catalog_entry(): ...          # no generated verdict left unjoined
def test_null_input_exits_3_package_run_failed_and_names_input(): ...
def test_units_integer_boolean_split_files_nested_indexed(): ...  # one parametrised test over Phase 1's B1 models
def test_report_header_records_teax_revision_and_simkit_path(): ...
def test_agreeing_items_hidden_unless_verbose(): ...
```

### Changes required
**See design:** [D9](design.md#key-decisions) (verdict rule and join), [D12](design.md#key-decisions) (per-item line, summary line), [D6](design.md#key-decisions) (exit 3 prefixes), [B6](design.md#key-bets) (header).
- [ ] Verdict comparison in `compare/`: native verdict per D9; generated verdict from the package's evaluation files (`actual_value`); join through the catalog. Verdicts marked by B2 are not compared. A generated verdict with no native partner, or the reverse, is a test failure, not a silent drop.
- [ ] Null input: the `CALC-USAGE-BINDING-LOST-WITH-RESULT-EXPRESSION` reproducer (sysml-codegen backlog `:29`, case `calc-usage-result__bare_result__other_expression_site`) as fixture `tests/fixtures/compare/result_expression_null_input/`. Expected: exit 3, reason starting `package run failed:` and naming the input. This records the run failure only; it adds no guidance about result expressions (RG-2).
- [ ] Report header: TEAx revision and simkit path. Reuse `study/integrate.py:344` (`teax_revision(teax_root)`), with the TEAx root found from `simkit.__file__`, not from the environment.
- [ ] B1 shape fixtures from Phase 1 (`units_int_bool`, `split_files`, `nested_indexed`, `named_subsets`, `outer_redefinition`) into `tests/fixtures/compare/` with tests. **If one of them gives a false difference, stop and report**, as in Phase 1: it is a failed design bet (B1), not something to tune away or reclassify.
- [ ] `--help` text names the limit from B5: losses that leave no trace in what is built (such as a dropped String) are not checked. No wording about String or result-expression guidance beyond that (RG-2).
- [ ] sysml-codegen `CLAUDE.md`, Commands: one line for `sysml-codegen compare --models …` and one for the simkit lane test command. Match the existing comment style in that block.

### Exit check
- Simkit lane: `tests/compare` → all pass, 0 skipped.
- Default lane: only the Phase 0 failure IDs.
- `ruff` and `mypy` on `src/` → clean. Byte identity re-run → zero differences.
- By hand, from agentic-mbse's `spike/` folder: `./codegen.sh -m sysml_codegen compare --models /home/reid/src/subset-conformance/sysml-codegen/tests/fixtures/compare/default_count_literal` → exit 4, summary line `values: compared N of M; counts: P of Q; verdicts: R of S`, `total` listed under `multiplicity pack.cells (3)`.
- Commit in sysml-codegen. This is the last sysml-codegen code phase; the branch now carries the whole command.

### What we know after this phase
Every exit and every not-compared cause has a test built from a real model, including the verdict join and the shapes the spike did not cover.

---

## Phase 5: agentic-mbse workflow text and pins

### Goal
Put `compare` into the shipped workflow and fix the guidance for Risks 2 and 3, one home per fact ([D13](design.md#key-decisions)). The Component Overview's "agentic-mbse" list ([design.md § Component Overview](design.md#component-overview)) is the file list; this phase does not restate the wording, which is in D13, D14 and D15.

### Risk it reduces
Risk 1 (the workflow runs `compare` and says what each exit means), Risk 2 (the assert statement in limit 1), Risk 3 (the `check` qualifier at each teaching site).

### Assumption under test
The text can say all of this without naming a list of accepted or refused functions (invariant 5) and without any line about dropped Strings or result expressions (invariant 6).

### Test stencil (write first, in `tests/test_shipped_text.py`)

```python
COMPARE_COMMAND = "uv run sysml-codegen compare --models models/"

def test_modeling_process_says_when_and_how_to_run_compare():
    section = _generated_code_section()      # same split as test_modeling_process_says_when_and_how_to_run_the_generation_check
    assert COMPARE_COMMAND in section
    for marker in ("**Exit 0:**", "**Exit 1:**", "**Exit 2:**", "**Exit 3:**", "**Exit 4:**"):
        assert marker in compare_paragraph(section)
    assert "invalid choice: 'compare'" in section and "not compared" in section
    assert "environment:" in section and "package run failed:" in section
    assert "sum(cells.capacity)" in section      # D14 exit-4 text

@pytest.mark.parametrize(("relative", "anchor"), RISK3_SITES)
def test_conditional_and_function_teaching_carries_the_check_qualifier(relative, anchor): ...
def test_limit_1_says_no_route_stops_on_a_failed_assert(): ...
def test_limit_3_sum_advice_points_at_compare_exit_4(): ...
```

### Changes required
- [ ] Tests first: extend `tests/test_shipped_text.py` next to the existing check-workflow pins (`:341-375`). Pin each Risk 3 site with a short anchor near the teaching line, not a line number. Extend `WORKFLOW_POINTERS`-style coverage for the three skills that gain a `compare` pointer (implement-model, model-validation, toolkit-awareness).
- [ ] `project_templates/MODELING_PROCESS.md.template`, "Generated code" (`:32-54`): the "Compare results" paragraph per the design's Component Overview, including how to provide simkit (D10) and the D14 exit-4 text.
- [ ] `project_templates/MODELING_GUIDE.md.template`: the Risk 2 paragraph in limit 1 (cite dc3's adapter, `dc3/scripts/models/package_comparison.py:93-103`, as the worked pattern); one pointer sentence after the limit-3 `sum` advice (`:108-112`); a `compare` line in the checklist.
- [ ] `docs/patterns/constraints.md` near `:158`: a pointer to limit 1's Risk 2 statement.
- [ ] Risk 3 qualifiers (D15 wording, verbatim) at the sites listed in the Component Overview. Re-find each by searching for the teaching text; the line numbers in the spec and design may have moved.
- [ ] `skills/implement-model`, `skills/model-validation` (`:65` "Translation" line becomes a pointer), `skills/toolkit-awareness`: one pointer line each.
- [ ] `docs/patterns/semantic-hazards.md`: add the `6190f996` positional result (spike S3) to "Verified with" and the routes table. The "where the draft finding was filed" sentence waits for Phase 7.
- [ ] Re-install for development only if needed to read the result: `uv run agentic-mbse install-commands --assistant claude` (repo `CLAUDE.md`, Change Coordination).

### Exit check
- `uv run pytest tests/test_shipped_text.py -q` → the new tests pass.
- `uv run pytest tests/ -q -rf` → only the Phase 0 agentic-mbse failure IDs.
- `uv run ruff check src/ tests/` → clean.
- Read this phase's `git diff -- project_templates skills docs agents`: no added line mentions dropped String values or dropped calc-usage result expressions (invariant 6), and no added line names a list of accepted or refused functions (invariant 5).
- No `import sysml_codegen` or `import simkit` added under `src/` (invariant 4): `git diff --stat -- src/` is empty.
- Commit in agentic-mbse.

### What we know after this phase
A target project that sets `execution-target = "generated"` gets the comparison from the shipped workflow, with every exit mapped to an action, and the guidance no longer teaches refused forms without a `check` qualifier.

---

## Phase 6: Phase R — Risk 1 re-runs on current `main`, and the dc3 run

### Goal
Re-run every Risk 1 case and record the result, per the design's "Phase R" table in [Implementation Notes](design.md#implementation-notes). Run `compare` on dc3 `models/` and record how much was compared ([Validation Approach](design.md#validation-approach)).

### Risk it reduces
Risk 1 (each generate-but-wrong case is confirmed or not at current `main`) and Risk 4 (every guidance claim about generator behaviour links to a recorded run). It also backs Risk 2 (the assert verdict run) and Risk 3 (a `check` run for the conditional and `min` refusals).

### Assumption under test
The results recorded in the spike and in earlier items still hold at current `main`, and dc3 mostly compares (design "dc3's shape").

### Test stencil (expected results first)
Write the "expected" column of `evidence/risk1-reruns.md` before running, from the design's Phase R table: for each case, the expected `check` exit, `generate` exit, `compare` exit and the expected guidance outcome. Then run and fill the "observed" column. A mismatch is a finding to record, not to fix.

### Changes required (agentic-mbse)
- [ ] Revisions: `check` and `generate` results stand for sysml-codegen `origin/main` (Phase 0 SHA), because Phase 2 to 4 showed the generated tree byte-identical on the branch. Record both SHAs and say this.
- [ ] `evidence/probes/<case>/` (NEW): one model per case, in the `probes.md` format of `.project/completed/20261022_retire-subset-profile/evidence/probes.md`.
- [ ] `evidence/risk1-reruns.md` (NEW): one row per case in the design's Phase R table, with commands, exits, the reason or difference line, and the guidance outcome.
  - String dropped and calc-usage result expression: record and flag only (RG-2). No guidance text.
  - Calc def simple-name collision and the three formerly `omitted` places: if confirmed (generates and differs), add a warning at the Risk 3 site per the design's Phase R table and a pin in `tests/test_shipped_text.py`; if refused, record the refusal; if not reproduced, record "not reproduced at <rev>".
- [ ] `evidence/dc3-compare.md` (NEW): `spike/codegen.sh -m sysml_codegen compare --models /home/reid/src/dc3/models`, with the exit code, the summary line, and the not-compared groups. A low share compared is a finding to report, not to tune. Confirm dc3's `git status --short` is still empty.
- [ ] Link every guidance claim about generator behaviour (Phase 5 text and any warning added here) to its row in `risk1-reruns.md` (invariant 5, spec criterion 5).

### Exit check
- Every row in the design's Phase R table has an observed result in `evidence/risk1-reruns.md`.
- `uv run pytest tests/ -q -rf` → only the Phase 0 failure IDs (matters only if this phase added a warning and pin).
- `git status --short` in sysml-codegen, TEAx and dc3 → empty.
- Commit in agentic-mbse.

---

## Phase 7: Phase U — upstream rows in sysml-codegen

### Goal
File the upstream rows per the design's "Phase U" list in [Implementation Notes](design.md#implementation-notes), on the `native-generated-compare` branch (orchestrator-delegated).

### Risk it reduces
Risk 4 (each owner-held change that would lift a stated limit names the guidance to update) and Risk 1 (confirmed cases carry reproducers and revisions upstream).

### Test stencil
Before editing, list in the phase notes each row to touch and the one fact it gains. After editing, `grep -n` for each row ID in `.project/backlog/BACKLOG.md` and check the fact is there.

### Changes required (sysml-codegen `.project/backlog/BACKLOG.md`)
- [ ] `[POSITIONAL-FORMAL-REDEFINITION]` (`:21`): the observed wiring at the recorded `main` SHA (by name; `gen_reversed` native −7, generated 7), that this differs from the row's "follows parser redefinition identity" text, and the agentic-mbse draft finding (`.project/completed/20261018_positional-binding-check/evidence/upstream-codegen-finding.md`) filed here. No ruling on which reading is intended (RG-1).
- [ ] `[SILENT-LOSSES-UNREPORTED]` (`:53`): fix the stale `retire-subset-profile` path (spec review L4-1); add the Phase R results for the three formerly `omitted` places. Flag only; no proposed guidance wording (RG-2).
- [ ] `[CALC-USAGE-BINDING-LOST-WITH-RESULT-EXPRESSION]` (`:29`): add the `compare` exit-3 `package run failed:` result with its revision.
- [ ] `[REGISTRY-CALC-DEF-SIMPLE-NAME-DEDUP]` (`:37`) and `[ATTRIBUTE-MULTIPLICITY-DEFAULT-COUNT]` (`:49`): the Phase R result with revision and reproducer, or "not reproduced at <rev>".
- [ ] `[CALCDEF-GATE-IMPLEMENTATION]` (`:111`) and `[ATTRIBUTE-MULTIPLICITY-DEFAULT-COUNT]`: a line naming the agentic-mbse files and headings to update when the change lands (D16).
- [ ] A row for `compare` only if sysml-codegen's backlog process wants one (check `.project/backlog/README.md`).
- [ ] Commit in sysml-codegen. Then, in agentic-mbse: mark `upstream-codegen-finding.md` as filed, finish the `semantic-hazards.md` "filed at" sentence, and commit.

### Exit check
- Each row ID in the list above shows its new fact on `grep`.
- sysml-codegen default lane unchanged from Phase 4 (backlog edits only; no need to re-run if `git diff --stat` touches only `.project/`).
- Both repos clean after their commits.

---

## Risk Management

**See [design.md § Potential Risks](design.md#potential-risks) for the full list.** Phase-specific handling:

- **Phase 1:** a failed bet stops the work (gate above). Every design fallback moves items to "not compared", never to "agree", but applying one is a design change and is the orchestrator's call.
- **Phase 2:** the accessor touches a guarded boundary file. Keep it identity-based so `test_elaboration_import_boundaries.py` passes without new exemptions. If byte identity fails, revert the change and find what touched emission; do not update the baseline.
- **Phase 3:** `compare` is the first production caller of TEAx's package loader (B6). The report header's TEAx revision is the trace if TEAx changes. The environment-read guard (`test_public_authority_switch.py`) keeps `compare` from growing its own simkit discovery.
- **Phase 3 and 4:** a simkit lane that silently skips would look green. The "0 skipped in `tests/compare`" exit condition prevents that.
- **Phase 4:** a B1 shape failing (units, Integer, split files) is a stop-and-report, not a tolerance change. A modeller-facing `--abs-tol` exists only for near-zero true values (D8).
- **Phase 5:** text describing an unmerged command. Exit 2 with "invalid choice: 'compare'" maps to "not compared", so a target project on an older sysml-codegen reads the right answer.
- **Phase 6:** a re-run that contradicts an earlier finding is recorded as observed, and the guidance follows the new result.

## Handoff Notes (for the orchestrator and owner, not steps)

- **Merge order:** sysml-codegen `native-generated-compare` first, then agentic-mbse `generated-results-guidance`, because the shipped workflow text names `compare`. Both merges are the owner's (RG-3).
- **Proposed at close, not filed (RG-3):** the product promise in design § Next-Stage Handoff.
- **Follow-up at close:** file in the agentic-mbse backlog that native SysIDE's one-part reading of `sum` over a multiplicity also misleads native-target projects, a candidate `semantic-hazards.md` entry (design, "Follow-up, not in this item").
- **Not checked by this plan's author:** I did not run either test suite, so the 5 and 9 base-failure counts come from the brief and are confirmed in Phase 0. I did not confirm that the agentic-mbse venv's pytest runs sysml-codegen's `tests/` package cleanly; Phase 0's lane smoke check does. I did not check whether dc3 `models/` currently generates; Phase 2 records it either way.

## Implementation Notes

[To be filled during implementation.]

### Phase 0 Completion
**Completed:** 2026-10-22
**Actual Changes:**
- sysml-codegen: branch `native-generated-compare` created from `origin/main` `6190f996` (unchanged since the design; `src` diff empty). `subset-profile-screen` untouched. Working tree was clean.
- `evidence/baseline.md`: revisions, both base-failure ID lists (agentic-mbse 5, sysml-codegen 9, as expected; skips 8 and 9), simkit-lane smoke output, the three byte-identity "before" records and their sha256.
- Byte identity: `package_manifest.py record` gave 122 subjects (116 generated); dc3 `models/` generates (exit 0, 183 files); 5 of 8 spike models generate, the other 3 are refused as in the spike.
**Issues:**
- dc3 has an untracked folder that predates this work (`.project/active/toolkit-update-generator-check/`). "dc3 clean" in later checks means no change from that.
**Deviations:**
- The Phase 1 models did not exist yet, so their "before" generation is taken at the end of Phase 1 on the same untouched code (sysml-codegen code does not change in Phase 1).
- agentic-mbse suite was run with `-p no:randomly` added; it does not change the test set.

### Phase 1 Completion
**Completed:** 2026-10-22. **Gate FAILED: stopped before Phase 2.** Full record: [spike/derisk/RESULTS.md](spike/derisk/RESULTS.md).
**Bet verdicts:**
- B2 holds. Every multiplicity-wrong native value was marked; `[1]` and named subsets were not.
- B3 holds. On `dc3_redefinition` the effective usage gives 10.0 and bound 3, matching generated 10.0 and 3 built; the slot root gives 2.0 and 1.
- **B4 fails.** `evaluate_feature` misses redefinitions that are not in its scope element's own body, giving false differences on correct packages:
  - `outer_retyping`: a value redefined in the effective usage's type, reached by a re-typing two levels out. Native 3.0, generated 21.0.
  - calc usages inside a part that redefines one of their inputs (`named_subsets rack_2.d.y`: native 4.0, generated 8.0; `split_files cart.motor.t.y`: native 6.0, generated 12.0). No single scope gives the right value.
- **B1 fails for units.** SysIDE returns no value for any unit annotation (`Operator '[' is not model-level evaluable`), so those values fall to "no native value". With `experimental_quantities` it converts to SI base units (500 [g] → 0.5) while the generator keeps 500, a false difference. B1 holds for Integer, split files and two indexed levels. Boolean is right on the native side.
- Design gap, not a bet: every output port is typed `float`, so a Boolean output is written `1.0` against native `True`. D8 needs a rule for this.
**Zero-slot data source:** none needed. `check` refuses all six `[0]` read forms tried, and graph validation forbids a zero-edge aggregation reference, so no projectable graph reads an empty slot. Gap: count rows cannot see a `[0]` slot (no occurrence records).
**Issues:**
- `check` refused some first-draft shapes (computed attribute inside an indexed part: `REGISTRY_CLASS_NAME_COLLISION`; `t.y` read in an expression: `elaboration_feature_declaration_unindexed`; `ISQ::MassValue`). The models were switched to accepted shapes before the probe ran; `EXPECTED.md` lists every change.
- Observation (RG-1, not ruled on): `named_subsets rack_sum` is generated as 4.0 where SysML means 6.0 (named members' own values ignored). It is marked, so it is not reported as agreement.
**Deviations:**
- The byte-identity "before" records for the Phase 1 models were taken at the end of this phase on the untouched code, as Phase 0's notes said. `identity_record.sh` was committed under `spike/derisk/`.
- Exit check not met: the probe exits 1. sysml-codegen and TEAx `git status` are empty; dc3 shows only its pre-existing untracked folder. No `__pycache__` under `spike/`.

### Phase 2 Completion
**Completed:**
**Byte-identity results:**
**Issues:**
**Deviations:**

### Phase 3 Completion
**Completed:**
**Issues:**
**Deviations:**

### Phase 4 Completion
**Completed:**
**Issues:**
**Deviations:**

### Phase 5 Completion
**Completed:**
**Issues:**
**Deviations:**

### Phase 6 Completion
**Completed:**
**Issues:**
**Deviations:**

### Phase 7 Completion
**Completed:**
**Issues:**
**Deviations:**

---

**Status:** Draft → In Progress → Complete
