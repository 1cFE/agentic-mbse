#!/usr/bin/env bash
# Build the SC12 parity environment: both wheels from clean exports, one venv on fusion-tea's
# interpreter. Usage: make_venv.sh SCRATCH CODEGEN_REPO AGENTIC_REPO TEAX_CHECKOUT
#
# - Each wheel is built from `git archive HEAD`, never from a working tree, so no uncommitted
#   edit reaches it. sources.json records the two commits and the wheels' sha256.
# - The venv runs on /usr/bin/python3.12, fusion-tea's own interpreter (plan Phase 4, decision
#   Q2). Its sys.base_prefix is /usr, so neither B13 allowance fires on either side.
# - Every installed module is byte-compiled at install, so no run writes a .pyc into the venv
#   and a read-coverage receipt sees the same cache files in every run.
# - teax's simkit is importable through a .pth file naming its source root, which is what an
#   editable install amounts to, without building anything into the teax checkout. Its
#   declared dependencies are installed beside it.
set -euo pipefail
scratch=$1 codegen=$2 agentic=$3 teax=$4
simkit="$teax/packages/teax-simkit"
mkdir -p "$scratch/src/codegen" "$scratch/src/agentic" "$scratch/wheels"
git -C "$codegen" archive HEAD | tar -x -C "$scratch/src/codegen"
git -C "$agentic" archive HEAD | tar -x -C "$scratch/src/agentic"
(cd "$scratch/src/codegen" && uv build --wheel --out-dir "$scratch/wheels")
(cd "$scratch/src/agentic" && uv build --wheel --out-dir "$scratch/wheels")
codegen_wheel=$(ls "$scratch"/wheels/sysml_codegen-*.whl)
agentic_wheel=$(ls "$scratch"/wheels/agentic_mbse-*.whl)
uv venv "$scratch/venv" --python /usr/bin/python3.12
uv pip install --python "$scratch/venv/bin/python" --compile-bytecode \
    "$codegen_wheel" "$agentic_wheel" jsonschema pytest \
    "pydantic>=2.5" "numpy>=1.23" "pandas>=1.5" "pyarrow>=12" "PyYAML>=6.0" "python-dotenv>=1.0"
echo "$simkit" > "$scratch/venv/lib/python3.12/site-packages/teax_simkit_source.pth"
cat > "$scratch/wheels/sources.json" <<EOF
{
  "sysml_codegen": {"commit": "$(git -C "$codegen" rev-parse HEAD)", "wheel": "$(basename "$codegen_wheel")", "sha256": "$(sha256sum "$codegen_wheel" | cut -d' ' -f1)"},
  "agentic_mbse": {"commit": "$(git -C "$agentic" rev-parse HEAD)", "wheel": "$(basename "$agentic_wheel")", "sha256": "$(sha256sum "$agentic_wheel" | cut -d' ' -f1)"},
  "teax": {"commit": "$(git -C "$teax" rev-parse HEAD)", "simkit_root": "$simkit"}
}
EOF
cat "$scratch/wheels/sources.json"
