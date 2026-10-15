#!/usr/bin/env bash
# F1 spike driver. Builds an isolated tree at pinned revisions, runs codegen's oracle and the
# port on every case, then compares. Sibling checkouts are only read (git archive).
#   usage: run_all.sh [--setup]   (license key read from agentic-mbse/.env)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(git -C "$HERE" rev-parse --show-toplevel)"
T=${F1_TMP:-/tmp/f1spike}
CODEGEN_REV=b5663c07e987a892e27d21e68cec40d0656574ee
AGENTIC_REV=${AGENTIC_REV:-9d8a3a3e}   # src/ identical to a718efec (design base)
DC3_BASE=808464d; DC3_FIXED=60b44d5

if [[ "${1:-}" == "--setup" ]]; then
  rm -rf "$T"; mkdir -p "$T/dc3-base" "$T/dc3-fixed"
  git -C ~/src/sysml-codegen archive --prefix=sysml-codegen/ "$CODEGEN_REV" | tar -x -C "$T"
  git -C "$REPO" archive --prefix=agentic-mbse/ "$AGENTIC_REV" | tar -x -C "$T"
  git -C ~/src/dc3 archive "$DC3_BASE" | tar -x -C "$T/dc3-base"
  git -C ~/src/dc3 archive "$DC3_FIXED" | tar -x -C "$T/dc3-fixed"
  (cd "$T/sysml-codegen" && uv sync --frozen)
fi

set -a; . "$REPO/.env"; set +a
PY="$T/sysml-codegen/.venv/bin/python"
OUT="$HERE/results"; rm -rf "$OUT"; mkdir -p "$OUT"
cd "$T"   # cwd is the isolated tree; scripts get absolute paths

"$PY" -I -c "
import importlib.metadata as m, sys, syside, agentic_mbse, sysml_codegen, json
assert agentic_mbse.__file__.startswith('$T') and sysml_codegen.__file__.startswith('$T'), 'isolation'
print(json.dumps({p: m.version(p) for p in ('sysml-codegen','agentic-mbse','syside')} | {'python': sys.version.split()[0], 'agentic_file': agentic_mbse.__file__, 'codegen_file': sysml_codegen.__file__}))
" > "$OUT/identity.json"
{ git -C ~/src/sysml-codegen archive "$CODEGEN_REV" | git get-tar-commit-id || true; } >> "$OUT/identity.json"
sha256sum "$T/sysml-codegen/uv.lock" >> "$OUT/identity.json"

run_case() {  # name, paths...
  local name=$1; shift
  timeout 900 "$PY" -I "$HERE/oracle.py" "$OUT/$name.oracle.json" "$@" || echo "oracle failed: $name"
  timeout 900 "$PY" -I "$HERE/port_run.py" "$OUT/$name.port.json" "$@" || echo "port failed: $name"
}

for f in "$REPO"/.project/concepts/convince-me-exec-subset/evidence/01-fixtures/*.sysml; do
  run_case "proto__$(basename "$f" .sysml)" "$f"
done
for f in "$HERE"/fixtures/*.sysml; do run_case "edge__$(basename "$f" .sysml)" "$f"; done
CAPTURED=$(python3 -c "import json;print(' '.join(json.load(open('$T/sysml-codegen/tests/fixtures/v6_recapture_batch/batch.json'))['captured']))")
ALL=$(python3 -c "import json;print(' '.join(json.load(open('$T/sysml-codegen/tests/fixtures/v6_recapture_batch/batch.json'))['fixtures']))")
for n in $ALL; do
  if [[ " $CAPTURED " == *" $n "* ]]; then pre=corpus; else pre=corpusx; fi
  run_case "${pre}__$n" "$T/sysml-codegen/tests/fixtures/$n"
done
run_case "dc3__baseline_808464d" "$T/dc3-base/models"
run_case "dc3__repaired_60b44d5" "$T/dc3-fixed/models"

python3 "$HERE/compare.py" "$OUT" | tee "$OUT/compare.log"
