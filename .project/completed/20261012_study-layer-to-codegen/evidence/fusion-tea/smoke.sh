#!/usr/bin/env bash
# Smoke-test the fusion-tea code drafts in a copy of the SC12 parity layout (plan Phase 4).
# Usage: smoke.sh SCRATCH, where SCRATCH is a parity scratch directory after `parity.py all`.
# Prints each check's command and output; SMOKE.md records a run.
#
# The copy gets runbook step 5's code half: the wrappers replace the originals and the
# schemas directory goes. Then:
#   1. every wrapper is the installed module itself;
#   2. a wrapper run by path from /tmp writes the moved module's bytes;
#   3. routes.sed rewrites a route's scripts.study import and nothing else;
#   4. declaration.toml loads through declarations.load_declaration;
#   5. integrate run through the wrapper returns CANDIDATE, and gate 7's driver, run directly
#      with no SYSML_CODEGEN_PROJECT_ROOT, passes read coverage (needs SYSIDE_LICENSE_KEY).
set -euo pipefail
: "${SYSIDE_LICENSE_KEY:?check 5 needs SYSIDE_LICENSE_KEY}"
teax=${TEAX:-/home/reid/1cfe/teax}
scratch=$(cd "$1" && pwd)
drafts=$(cd "$(dirname "$0")" && pwd)
python="$scratch/venv/bin/python"
smoke="$scratch/smoke"
project="$smoke/project"
rm -rf "$smoke"
mkdir -p "$smoke"
cp -a "$scratch/project" "$project"
git -C "$project" reset -q --hard
git -C "$project" clean -q -fdx
cp -a "$drafts/wrappers/scripts/." "$project/scripts/"
git -C "$project" rm -q -r scripts/study/schemas
git -C "$project" add -A
git -C "$project" -c user.name=smoke -c user.email=smoke@example.invalid commit -q -m "step 5: wrappers"
export PATH="$scratch/shim:$scratch/venv/bin:/usr/bin:/bin" LC_ALL=C.UTF-8 HOME="$scratch/home"
unset SYSML_CODEGEN_PROJECT_ROOT PYTHONPATH

echo "## 1. Each wrapper is the installed module"
echo '$ python -c "import scripts.study.manifest as m, sysml_codegen.study.manifest as n; print(m is n)"'
(cd "$project" && "$python" -c "import scripts.study.manifest as m, sysml_codegen.study.manifest as n; print(m is n)")
(cd "$project" && "$python" - <<'EOF'
import importlib
from pathlib import Path
from sysml_codegen.study import roots
pairs = {f"scripts.study.{n}": f"sysml_codegen.study.{n}"
         for n in ("common", "identity", "manifest", "indicators", "preflight", "verify", "read_coverage")}
pairs["scripts.integrate"] = "sysml_codegen.study.integrate"
for alias, moved in pairs.items():
    print(f"{alias} is {moved}: {importlib.import_module(alias) is importlib.import_module(moved)}")
from scripts.integrate import rederived_census
from sysml_codegen.study.integrate import rederived_census as moved_census
print(f"from scripts.integrate import rederived_census is the moved function: {rederived_census is moved_census}")
print(f"pinned project root is this repository: {roots.project_root() == Path.cwd().resolve()}")
EOF
)

echo
echo "## 2. A wrapper run by path from /tmp writes the moved module's bytes"
args=(--package "$project/pkg/station_study" --manifest "$project/studies/manifest.json"
      --groups "$project/studies/axes.json")
(cd "$project" && "$python" -m sysml_codegen.study.indicators "${args[@]}" --out "$smoke/moved.json")
(cd /tmp && "$python" "$project/scripts/study/indicators.py" "${args[@]}" --out "$smoke/wrapper.json")
echo "\$ cmp moved.json wrapper.json   # moved run from the project; wrapper run from /tmp"
cmp "$smoke/moved.json" "$smoke/wrapper.json" && echo "identical ($(sha256sum < "$smoke/wrapper.json" | cut -c1-16)…)"
echo "\$ cmp against the parity run's moved indicators.json"
cmp "$scratch/runs/indicators-complete/moved/out/indicators.json" "$smoke/wrapper.json" && echo identical
for tool in "scripts/study/preflight.py" "scripts/study/verify.py" "scripts/integrate.py"; do
    (cd /tmp && "$python" "$project/$tool" --help > /dev/null) && echo "$tool --help: exit 0"
done
(cd "$project" && "$python" -m scripts.study.indicators --help > /dev/null) && echo "-m scripts.study.indicators --help: exit 0"

echo
echo "## 3. routes.sed rewrites the route import and nothing else"
route="$smoke/study_route_variant.py"
sed 's/^from sysml_codegen\.study import /from scripts.study import /' \
    "$project/studies/study_route.py" > "$route"
printf '%s\n' '"""Prose that names scripts/study/ stays as written."""' \
    'from scripts.study import common, identity  # noqa: E402' >> "$route"
echo "before: $(grep -c '^from scripts\.study import' "$route") line(s) import scripts.study"
sed -i -f "$drafts/routes.sed" "$route"
echo "after:  $(grep -c '^from scripts\.study import' "$route" || true) line(s) import scripts.study"
grep -n 'sysml_codegen\.study import\|scripts/study/' "$route"
echo "\$ diff <the fixture route> <the rewritten variant, less its two appended lines>"
diff "$project/studies/study_route.py" <(head -n -2 "$route") && echo "no difference"

echo
echo "## 4. declaration.toml loads through declarations.load_declaration"
mkdir -p "$smoke/declared"
cp "$drafts/declaration.toml" "$smoke/declared/pyproject.toml"
"$python" - "$smoke/declared" <<'EOF'
import sys
from pathlib import Path
from sysml_codegen.study.declarations import load_declaration
d = load_declaration(Path(sys.argv[1]))
for gate, declared in d.gates.items():
    print(f"gate {gate}: target {declared.target!r}; checked {declared.checked!r}")
print(f"environment: {list(d.environment)}")
print(f"record-distributions: {dict(d.record_distributions)}")
print(f"backup-prefix: {d.backup_prefix!r}")
EOF

echo
echo "## 5. integrate through the wrapper, and gate 7's driver with no project-root variable"
lineage=$("$python" -c "import json,sys; p=json.load(open(sys.argv[1]))['fingerprints']['recorded_provenance']; print(p['semantic_fingerprint'], p['executable_fingerprint'])" "$project/studies/manifest.json")
read -r semantic executable <<< "$lineage"
mkdir -p "$smoke/tmp"
(cd "$project" && env TMPDIR="$smoke/tmp" TEAX_SIMKIT_PATH="$teax/packages/teax-simkit" \
    STOP_PARSER_WHEEL_TARGET=smoke-dummy STOP_PARSER_AGENTIC_WHEEL=smoke-dummy \
    STOP_PARSER_CODEGEN_WHEEL=smoke-dummy STOP_PARSER_COSTINGFE_WHEEL=smoke-dummy \
    STOP_PARSER_TEAX_ROOT="$teax" \
    "$python" scripts/integrate.py --audited-work models@HEAD --models-root models \
    --package pkg/station_study --manifest studies/manifest.json --groups studies/axes.json \
    --census-file census.json --route-sys-path studies --route-module study_route \
    --route-callable execute_baseline --out-dir "$smoke/out" \
    --expected-teax-revision "$(git -C "$teax" rev-parse HEAD)" \
    --expected-semantic-fingerprint "$semantic" --expected-executable-fingerprint "$executable" \
    > /dev/null 2> "$smoke/integrate_stderr.txt") && echo "integrate exit 0"
head -n 1 "$smoke/integrate_stderr.txt"
"$python" -c "import json,sys; r=json.load(open(sys.argv[1])); print('class', r['class'], '| tool.path', r['tool']['path'], '| command[0]', r['command'][0])" "$smoke/out/integration_return.json"
echo '$ PYTHONPATH=<project>:<simkit> python -c <run_route> studies study_route execute_baseline <out> pkg/station_study studies/manifest.json smoke   # no SYSML_CODEGEN_PROJECT_ROOT'
(cd "$project" && env PYTHONPATH="$project:$teax/packages/teax-simkit" \
    TEAX_SIMKIT_PATH="$teax/packages/teax-simkit" \
    "$python" -c 'import sys; from sysml_codegen.study.read_coverage import run_route; run_route(*sys.argv[1:])' \
    studies study_route execute_baseline "$smoke/rc" pkg/station_study studies/manifest.json smoke) \
    && echo "driver exit 0"
"$python" -c "import json,sys; r=json.load(open(sys.argv[1])); print('outcome', r['outcome'], '| violations', r['violations'], '| route_error', r['route_error'])" "$smoke/rc/read_coverage.json"
