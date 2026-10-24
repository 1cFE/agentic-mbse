#!/usr/bin/env bash
# Usage: identity_record.sh <before|after>
# Generates the spike models and dc3 models/ with the sysml-codegen checkout's own uv env,
# into /tmp/grg-impl/identity-<tag>/{spike,dc3}/<case>, recording each exit and output.
set -uo pipefail
TAG=$1
CG=/home/reid/src/subset-conformance/sysml-codegen
AM=/home/reid/src/subset-conformance/agentic-mbse
G=$AM/.project/active/generated-results-guidance
OUT=/tmp/grg-impl/identity-$TAG
set -a; source "$AM/.env"; set +a
mkdir -p "$OUT/spike" "$OUT/dc3" "$OUT/log"
declare -A CASES=(
  [native_path_model]=$G/spike/native-path/model
  [native_path_model_extra]=$G/spike/native-path/model_extra
  [s1_gen]=$G/spike/channel-trace/models/s1_gen
  [s1_native]=$G/spike/channel-trace/models/s1_native
  [default_count]=$G/spike/channel-trace/models/default_count
  [default_count_literal]=$G/spike/channel-trace/models/default_count_literal
  [gen_reversed]=$AM/tests/fixtures/positional_binding/native_values/gen_reversed
  [gen_byname]=$AM/tests/fixtures/positional_binding/native_values/gen_byname
)
if [ -d "$G/spike/derisk/models" ]; then
  for d in "$G"/spike/derisk/models/*/; do c=$(basename "$d"); CASES[derisk_$c]=$d; done
fi
cd "$CG"
for c in $(printf '%s\n' "${!CASES[@]}" | sort); do
  uv run sysml-codegen generate --models "${CASES[$c]}" --output "$OUT/spike/$c" --package-name "$c" > "$OUT/log/spike_$c.txt" 2>&1
  echo "spike $c exit $?" | tee -a "$OUT/log/summary.txt"
done
uv run sysml-codegen generate --models /home/reid/src/dc3/models --output "$OUT/dc3/dc3_models" --package-name dc3_models > "$OUT/log/dc3.txt" 2>&1
echo "dc3 exit $?" | tee -a "$OUT/log/summary.txt"
