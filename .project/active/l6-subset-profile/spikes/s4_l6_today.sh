#!/usr/bin/env bash
# Spike S4: today's L6 (this checkout, src/ unchanged) on each pinned tree, from a git archive export.
#   bash .project/active/l6-subset-profile/spikes/s4_l6_today.sh   (run from the agentic-mbse root)
set -euo pipefail
ROOT=$(pwd)
PY="$ROOT/.venv/bin/python"
WORK=$(mktemp -d /tmp/l6-spike-s4-XXXXXX)
trap 'rm -rf "$WORK"' EXIT
for spec in "fusion-tea:$HOME/src/fusion-tea:f96ad312" "dc3-baseline:$HOME/src/dc3:808464d" "dc3-repaired:$HOME/src/dc3:60b44d5"; do
  IFS=: read -r label repo rev <<<"$spec"
  "$PY" -I -c "
import sys; sys.path.insert(0, '$ROOT/.project/active/l6-subset-profile/spikes')
from pathlib import Path; from s1_trees import export
export(Path('$repo'), '$rev', Path('$WORK/$label'))" >/dev/null
  echo "== $label ($rev): validate --level=6 models"
  set +e
  (cd "$WORK/$label" && "$PY" -m agentic_mbse validate --level=6 models) > "$WORK/$label.out" 2>&1
  code=$?
  set -e
  grep -E "Level 6|Issues found|Quality checks|❌|✅|Error running" "$WORK/$label.out" | head -8
  echo "exit code: $code"
done
