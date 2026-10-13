# SC9 rehearsal (orchestrator step O3)

This rehearses the fusion-tea adoption runbook, `../fusion-tea-runbook.md`, on a disposable copy of fusion-tea (design Appendix H3, DD15). It runs after O4 has committed the fusion-tea texts and after Phase 6. Each step below gives the commands, run in order in one shell, and the expected observation. The runbook explains why each step exists; this file says how to rehearse it.

Mark every step **rehearsed**, **not rehearsable** (with the reason), or **not run**, and copy each observation into the runbook's "Observed in the rehearsal" line.

**Cut 1** removes step 8a: suite runs A, B and C, and `junit-diff.py`. If cut 1 applies, skip every command marked *(8a)* and mark 8a "not run (cut 1)".

## The three runs

The suite and `integrate` run three times on the one copy `$FTC`, in this order:

- **A, as-is**: fusion-tea at O4's branch tip, its own environment, nothing changed.
- **B, dependencies moved**: the two branch wheels installed into `$FTC/.venv` (step 2), nothing switched yet. Its integrate tests fall back to the old generator part-way (step 2 says why).
- **C, switched**: after steps 5, 6 and 7.

Each run passes `--continue-on-collection-errors`. fusion-tea's suite has one collection error that is not this item's: `tests/study/test_stellarator_materials_policy.py` imports `exploration/stellarator_materials/oracle_glue.py`, whose `PIN_INPUTS_PATH` (line 85) names `work/active/WI-098_whole-plant-conversion-comparison/…`, and fusion-tea `421966070` archived that item to `work/completed/20261006_WI-098_…`. Without the flag, pytest stops there and runs no test.

## Setup

```bash
CG=/home/reid/1cfe/sysml-codegen-study-layer          # this worktree, at Phase 6's tip
AM=/home/reid/1cfe/agentic-mbse-study-layer           # the agentic-mbse branch worktree
EV=$CG/.project/active/study-layer-to-codegen/evidence
FT_REPO=...                                           # the fusion-tea repository that holds O4's branch
O4=...                                                # O4's branch tip
R=/tmp/study-rehearsal-$(date +%Y%m%d-%H%M%S)
FTC=$R/ftc
mkdir -p "$R"

git -C "$FT_REPO" worktree add --detach "$FTC" "$O4"
git -C "$FTC" log --oneline b06585709..HEAD           # O4's text commits, and main's since b06585709 if O4's base is newer

bash "$EV/install/build_wheels.sh" "$R/wheels" "$CG" "$AM"
AMBSE_WHEEL=$(ls "$R"/wheels/agentic_mbse-*.whl)
CODEGEN_WHEEL=$(ls "$R"/wheels/sysml_codegen-*.whl)

cp "$EV/rehearsal/env.sh.example" "$R/env.sh"
sed -i "s|^export FTC=.*|export FTC=\"$FTC\"|" "$R/env.sh"
. "$R/env.sh"                                         # the licence, STOP_PARSER_*, TEAX_SIMKIT_PATH

cd "$FTC" && uv sync --frozen --extra e2e --python /usr/bin/python3.12   # fusion-tea's own environment and interpreter
```

The venv is built on `/usr/bin/python3.12` because fusion-tea's own `.venv` runs on it, as parity's decision Q2 found (`../parity/README.md`). uv's managed CPython has no `getrandom`, so `import random` opens `/dev/urandom`, and its zone data lies outside `sys.base_prefix`. The original observer refuses both reads, so on that interpreter runs A and B fail gate 7 on the interpreter, not the package.

Run every later command from `$FTC`, in this shell. `env.sh` unsets `PYTHONPATH` and `SYSML_CODEGEN_PROJECT_ROOT`; nothing else may set them.

## Step 1: drift check

```bash
git -C "$FT_REPO" fetch origin
git -C "$FT_REPO" diff b06585709 origin/main -- .claude/skills/run-study modeling_project/STUDY_POLICY.md scripts/study scripts/integrate.py docs/integration_seam_operator_guide.md
```

**Expected:** it prints nothing.

## Run A *(8a)*

```bash
record_env "$R/A"
uv run --no-sync pytest tests/study tests/models/test_model_family_spines.py -q -rs --continue-on-collection-errors --junitxml="$R/A/junit.xml" > "$R/A/pytest.txt" 2>&1; echo "exit $?" >> "$R/A/pytest.txt"
```

## Step 2: agentic-mbse pin check (this makes run B's state)

```bash
uv pip install --python "$FTC/.venv/bin/python" --no-deps "$AMBSE_WHEEL" "$CODEGEN_WHEEL"
uv run --no-sync python -c "from agentic_mbse.cli.installation import INSTALLER_API_VERSION as v; print(v)"
```

**Expected:** `installer/v1`.

Run B does not keep this state. The original seam's gate 2 runs `uv run sysml-codegen generate` without `--no-sync` (`scripts/integrate.py:1006`, closed-list item B3), so the first suite test that reaches gate 2 re-syncs `.venv` to `uv.lock`, the old pins. From then on, B's integrate tests run the old generator. Step 5 therefore re-runs this install first. In the real adoption, step 4 moves the lock, so a re-sync installs the moved revision and the problem does not arise.

## Step 3: no-loss check

```bash
python3 "$EV/fusion-tea/text/check_anchors.py" "$EV/read-through.md" .
```

**Expected:** `75 anchors found, 0 missing`, exit 0, at O4's tip `aab9b9ba3` or later: 74 from O4's text commit `699b0a74d`, plus IG-43 from `aab9b9ba3`. At `699b0a74d` alone it prints `74 anchors found, 1 missing`.

## Step 4: move the sysml-codegen pin

**Not rehearsable:** it needs the merged sysml-codegen SHA. Step 2's wheel install stands in for it here.

## Run B

```bash
record_env "$R/B"                                                                     # (8a)
uv run --no-sync pytest tests/study tests/models/test_model_family_spines.py -q -rs --continue-on-collection-errors --junitxml="$R/B/junit.xml" > "$R/B/pytest.txt" 2>&1; echo "exit $?" >> "$R/B/pytest.txt"   # (8a)
python3 "$EV/rehearsal/junit-diff.py" "$R/A/junit.xml" "$R/B/junit.xml" > "$R/A-to-B.txt"   # (8a) recorded for step 9, not a gate
```

**8b, before step 5.** The chosen record is `exploration/magnet_materials/studies/20260929-magnet-material-comparison`. Of the 40 records with a results identity at `699b0a74d`, it is the only one whose sealed identity recomputes. The runbook's first choice, `20260916-primary-loop-sizing`, does not: its document declares `f52729e6…`, but its package, `exploration/stellarator_e2e/generated`, has had 10 commits since the record sealed it (`69653c9dd`), and it now recomputes to `83ea3b6c…`.

```bash
REC=exploration/magnet_materials/studies/20260929-magnet-material-comparison
IDPKG=exploration/magnet_materials/magnet_materials_tea        # the record's package, for 8b
PKG=exploration/stellarator_e2e/pkg/stellarator_tea            # 8c's package
uv run --no-sync python -c "import json, sys; from scripts.study import identity; print(identity.assert_matches(json.load(open(sys.argv[1])), sys.argv[2]))" "$REC/results/package_identity.json" "$IDPKG" | tee "$R/8b-before.txt"
```

**8c, run B** (needs teax and the licence). The arguments are the supplement's full stellarator request, `docs/integration_seam_operator_guide.md` § "The full invocation in fusion-tea", with the `--groups` the supplement names for the current interface. Only `--out-dir` differs between B and C.

```bash
INTEGRATE_ARGS=(...)       # the supplement's arguments, without --out-dir
uv run --no-sync python scripts/integrate.py "${INTEGRATE_ARGS[@]}" --out-dir "$R/B/integrate"; echo "exit $?"
```

## Step 5: switch

```bash
uv pip install --python "$FTC/.venv/bin/python" --no-deps "$AMBSE_WHEEL" "$CODEGEN_WHEEL"   # again: run B re-synced to the lock (step 2)
cp "$EV"/fusion-tea/wrappers/scripts/study/*.py scripts/study/
cp "$EV/fusion-tea/wrappers/scripts/integrate.py" scripts/integrate.py
ROUTES=(
  exploration/aries_integrated/studies/study_route.py
  exploration/component_alternatives/studies/study_route.py
  exploration/costed_loop_brayton/studies/study_route.py
  exploration/exchanger_architecture/thermal_requirements/studies/study_route.py
  exploration/ife_e2e/studies/study_route.py
  exploration/magnet_materials/studies/study_route.py
  exploration/stellarator_e2e/studies/study_route.py
  exploration/stellarator_materials/studies/study_route.py
  exploration/whole_plant_conversion/studies/study_route.py
)
sed -i -f "$EV/fusion-tea/routes.sed" "${ROUTES[@]}"
git rm -r -q scripts/study/schemas
patch -p1 < "$EV/fusion-tea/step5-tests.patch"
```

The nine route files are named, never globbed: git's pathspec `*` crosses `/` and would match the route copies inside committed records, which must not change.

`step5-guide-contract.patch` is not applied: its reduction of `tests/study/test_integrate_guide_contract.py` is already in O4's commit `699b0a74d`, and applying it again rejects both hunks.

**Expected:**

```bash
uv run --no-sync python -c "import scripts.study.manifest as m, sysml_codegen.study.manifest as n; print(m is n)"   # True
git grep -n 'from scripts.study' -- "${ROUTES[@]}"                                   # nothing
git status --porcelain --untracked-files=all -- exploration/ | cut -c4- | grep -vxF -f <(printf '%s\n' "${ROUTES[@]}")   # nothing
```

`step5-tests.patch` applies with no reject, fuzz or offset to `b06585709`, and so to O4's tip, where its 17 files are unchanged.

## Step 6: declare

```bash
cat "$EV/fusion-tea/declaration.toml" >> pyproject.toml
printf 'TEAX_SIMKIT_PATH=%s\n' "$TEAX_SIMKIT_PATH" >> .venv/integration.env
uv lock --check
```

**Expected:** `uv lock --check` reports the lock fresh.

## Step 7: re-install

```bash
git rm -r -q .claude/skills/run-study .agents/skills/run-study
sed -i '\|^!\.claude/skills/run-study/$|d' .gitignore
uv run --no-sync sysml-codegen install-commands . < /dev/null | tee "$R/install.txt"
find .agents/skills/run-study -type f | sort; readlink .claude/skills/run-study; ls .sysml-codegen/install.json
```

**Expected:** five files under `.agents/skills/run-study/`; `.claude/skills/run-study` reads `../../.agents/skills/run-study`; the output has a line starting "Preserved modeling_project/STUDY_POLICY.md"; `.sysml-codegen/install.json` exists. A "Preserved .claude/commands/teax-completion.md" line is the installer's first-run rule, not a failure; the runbook's step 7 says how to take the shipped command without `--force`.

## Run C

```bash
record_env "$R/C"                                                                     # (8a)
uv run --no-sync pytest tests/study tests/models/test_model_family_spines.py -q -rs --continue-on-collection-errors --junitxml="$R/C/junit.xml" > "$R/C/pytest.txt" 2>&1; echo "exit $?" >> "$R/C/pytest.txt"   # (8a)
python3 "$EV/rehearsal/junit-diff.py" "$R/B/junit.xml" "$R/C/junit.xml" | tee "$R/B-to-C.txt"   # (8a) C's pass rule
```

**8a expected:** B to C differs only in gate-2 refusals the generator move causes, and in nothing else. `junit-diff.py` exits 1 and reports exactly the 21 integrate tests the runbook's 8a pass rule lists, each failing in C at gate 2 (`regeneration`, `package-not-integrated`). In B, these tests ran the old generator (step 2) and got past gate 2. Any other reported line breaks the rule. A to B is classified for step 9.

**8b, after step 5:**

```bash
uv run --no-sync python -c "import json, sys; from scripts.study import identity; print(identity.assert_matches(json.load(open(sys.argv[1])), sys.argv[2]))" "$REC/results/package_identity.json" "$IDPKG" | tee "$R/8b-after.txt"
cmp "$R/8b-before.txt" "$R/8b-after.txt"
python3 -c "import json, sys; [print(s['path']) for s in json.load(open(sys.argv[1]))['stores']]" "$REC/results/verification_summary.json" | xargs ls   # the stores the record verified
# The record's own verify command, with the installed tool and a new --out:
mapfile -t VERIFY < <(python3 -c "import json, sys; c = json.load(open(sys.argv[1]))['command']; c[c.index('--out') + 1] = sys.argv[2]; print('\n'.join(c[1:]))" "$REC/results/verification_summary.json" "$R/reverify.json")
PYTHONPATH=$FTC:$TEAX_SIMKIT_PATH uv run --no-sync sysml-codegen study verify "${VERIFY[@]}"   # simkit, and the oracle module's `exploration.…` imports
python3 -c "import json, sys; a, b = (json.load(open(p)) for p in sys.argv[1:]); k = lambda d: [(s['sampling']['sampled_case_ids'], s['worst_channel_rel_dev']) for s in d['stores']] + [d['verdicts_rederived'], d['verdict_mismatches'], d['outcome']]; print('same' if k(a) == k(b) else 'DIFFERENT')" "$REC/results/verification_summary.json" "$R/reverify.json"
git status --short -- "$REC"
git grep -l '"kind": "effective"' -- '*package_identity.json' | xargs -r grep -l -F -f <(printf '%s\n' "${ROUTES[@]}")
```

**8b expected:** the two `assert_matches` digests are equal; the re-run gives `same`; the record directory's `git status` prints nothing; the last command, which lists effective identity documents naming a rewritten route, prints nothing. Only `tool.path`, `tool.source_digest` and `command[0]` differ between the two summaries, from `scripts/study/verify.py` to `sysml_codegen/study/verify.py` (B2). The `verify` half is **not rehearsable** at `699b0a74d`: the chosen record's two stores (`results/native/20260929-magnet-material-comparison.db`, `results/_work/magnet-materials-baseline-point-v1.db`) are not committed, and it is the only record that recomputes. Run the `ls` to show it, and skip the three `verify` lines.

**8c, run C, and the gate-7 driver:**

```bash
uv run --no-sync python scripts/integrate.py "${INTEGRATE_ARGS[@]}" --out-dir "$R/C/integrate"; echo "exit $?"
mkdir -p "$R/rc/read-coverage-tmp"
TMPDIR="$R/rc/read-coverage-tmp" PYTHONPATH=$FTC:$TEAX_SIMKIT_PATH uv run --no-sync python -c 'import sys; from sysml_codegen.study.read_coverage import run_route; run_route(*sys.argv[1:])' exploration/stellarator_e2e/studies study_route execute_baseline "$R/rc" "$PKG" exploration/stellarator_e2e/studies/manifest.json rehearsal
python3 -c "import json, sys; r = json.load(open(sys.argv[1])); print(r['outcome'], r['violations'])" "$R/rc/read_coverage.json"
for run in B C; do python3 -c "import json, sys; r = json.load(open(sys.argv[1])); b = r['blocker'] or {}; print(sys.argv[2], r['class'], b.get('gate'), b.get('mode'), b.get('condition'))" "$R/$run/integrate/integration_return.json" "$run"; done
```

**8c expected:** B and C print the same class, gate, mode and condition, or both print `CANDIDATE`. Their returns differ only in closed-list fields, the ones SC12's comparator maps or masks (`../parity/README.md`): tool paths and source digests (B2), producers (B2, B11), gate 1b's teax root (B7), and read-coverage receipt bookkeeping (B1, B8, B13). With the supplement's historical `--expected-teax-revision`, both stop at gate 1b (`teax-revision`, `toolchain-drift`) unless the teax checkout is at that revision. The driver prints `pass []`. `TMPDIR` points inside the driver's out directory because the route's first `tempfile.mkdtemp` makes tempfile probe its directory with a new file, and that probe has to land in the out directory, where the observer admits it as new output; both seams arrange this. Without it, the probe lands in `/tmp` and is refused as an undeclared read. The driver needs no `SYSML_CODEGEN_PROJECT_ROOT`: the package is in `$FTC`'s work tree, so it finds the root itself. Design Appendix H3's form sets it; that is harmless.

## Step 9: consequence note

Record what moving the generator from `8a758e9` to the branch tip did to fusion-tea's packages: gate 2 refusals, gate 4 snapshot drift, and any test that passed in A and not in B. In the rehearsal, A to B cannot show it, because B's integrate tests fall back to the old generator (step 2); 8a's B to C list shows it instead. Count the commits with `git -C "$CG" rev-list --count 8a758e9..HEAD`. 142 of them take the pin to sysml-codegen `main` as the branch found it (`aa35f06`); the branch adds its own (214 at `310dfc6`), so the adoption's count is `8a758e9` to the merge commit.

## Clean up

```bash
cd / && git -C "$FT_REPO" worktree remove --force "$FTC"
```

The rehearsal leaves no trace in fusion-tea beyond the removed worktree. Keep `$R` until the evidence is copied into the runbook.
