#!/usr/bin/env bash
# Negative controls: run each mutant port over every case already in results/ and compare
# against the same oracle outputs. A control passes when the comparison flags mismatches.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; REPO="$(git -C "$HERE" rev-parse --show-toplevel)"
T=${F1_TMP:-/tmp/f1spike}; PY="$T/sysml-codegen/.venv/bin/python"
set -a; . "$REPO/.env"; set +a
cd "$T"
for mutant in declared_multiplicity no_effective_decl writer_is_base typed_anywhere; do
  OUT="$HERE/results-controls/$mutant"; rm -rf "$OUT"; mkdir -p "$OUT"
  for o in "$HERE"/results/*.oracle.json; do
    name=$(basename "$o" .oracle.json)
    cp "$o" "$OUT/"
    inputs=$(python3 -c "import json,sys;print('\n'.join(json.load(open(sys.argv[1]))['inputs']))" "$o")
    mapfile -t args <<< "$inputs"
    timeout 900 "$PY" -I "$HERE/mutants.py" "$mutant" "$OUT/$name.port.json" "${args[@]}" 2>/dev/null || echo "mutant failed: $mutant $name"
  done
  python3 "$HERE/compare.py" "$OUT" > "$OUT/compare.log"
  echo "$mutant: $(tail -1 "$OUT/compare.log")"
done
