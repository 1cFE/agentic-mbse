#!/usr/bin/env bash
# C3 controls: break the guidance contract three ways on scratch copies and show the
# harness failing each time. The repo tree and the real manifest are never touched.
#   bash .project/concepts/convince-me-exec-subset/evidence/03-controls.sh   (from the agentic-mbse root)
set -u
REPO=$(git rev-parse --show-toplevel)
E="$REPO/.project/concepts/convince-me-exec-subset/evidence"
S=${C3_SCRATCH:-/tmp/claude-1000/-home-reid-src-agentic-mbse/8cecfa0f-3dca-4be9-bcbc-86b4acc4ae95/scratchpad/c3}
TEST="$E/03-harness-test.py"

copy_tree() {  # $1 = destination
  rm -rf "$1"; mkdir -p "$1/docs"
  cp -r "$REPO"/{skills,agents,adapters,project_templates} "$1/"
  cp -r "$REPO/docs/patterns" "$1/docs/"
  cp "$REPO"/docs/*.md "$1/docs/"
}

run() {  # $1 = log name, $2 = tree, $3 = manifest, $4 = description
  {
    echo "# control: $4"
    echo "# tree=$2 manifest=$3"
    echo "\$ C3_ROOT=$2 C3_MANIFEST=$3 uv run pytest -q -p no:cacheprovider $TEST"
    C3_ROOT="$2" C3_MANIFEST="$3" uv run pytest -q -p no:cacheprovider "$TEST" 2>&1 \
      | grep -E "^(FAILED|E  |=+ .*(passed|failed))" | cut -c1-400
    echo "# pytest exit: ${PIPESTATUS[0]}"
  } > "$E/03-control-$1.log"
  tail -3 "$E/03-control-$1.log"
}

# (a) Claim the calc-owned assert example in constraints.md executes.
copy_tree "$S/tree-a"
python3 - "$E/03-manifest.yaml" "$S/manifest-a.yaml" <<'PY'
import sys, yaml
m = yaml.safe_load(open(sys.argv[1]))
for e in m["fences"]:
    if e["id"].startswith("docs/patterns/constraints.md#in-calc-definitions@"):
        e["category"] = "executable"; e.pop("expect_codes", None); print("relabelled", e["id"])
yaml.safe_dump(m, open(sys.argv[2], "w"), sort_keys=False, width=200)
PY
run a-relabel-executable "$S/tree-a" "$S/manifest-a.yaml" "calc-owned assert example relabelled executable"

# (b) Edit an exempt fragment's content (one character) without touching the manifest.
copy_tree "$S/tree-b"
python3 - "$S/tree-b/docs/patterns/conditionals.md" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
old = "attribute diff : Real = if x > y? x - y else y - x;"
assert s.count(old) >= 1
s = s.replace(old, "attribute diff : Real = if x >= y? x - y else y - x;", 1)
open(p, "w").write(s); print("edited fragment in", p)
PY
run b-edit-fragment "$S/tree-b" "$E/03-manifest.yaml" "exempt fragment content edited, manifest unchanged"

# (c) Delete a checked (executable) example and add an unchecked one: fence count stays 212.
copy_tree "$S/tree-c"
python3 - "$S/tree-c/docs/patterns/adr002-calculations.md" <<'PY'
import re, sys
p = sys.argv[1]; s = open(p).read()
# The checked example is the fence that starts "// library/geometry.sysml".
m = re.search(r"```sysml\n// library/geometry\.sysml.*?```", s, re.S)
assert m, "checked example not found"
new = "```sysml\ncalc def Unchecked {\n    in x : Real;\n    out y : Real = x * 3.0;\n}\n```"
s = s[: m.start()] + new + s[m.end():]
open(p, "w").write(s); print("swapped checked example for unchecked one in", p)
PY
run c-swap-keep-count "$S/tree-c" "$E/03-manifest.yaml" "checked example replaced by unchecked one, count unchanged"
