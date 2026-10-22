"""Spike: can SysIDE evaluate a named output path on any model with one generic function?

Path form: `<package>::<part usage>.<feature>.<feature>...`; the scope is the feature that
owns the last name. Usage (repo root):
    uv run python .project/active/generated-results-guidance/spike/native-path/native_path.py \
        <model_dir> <path>...
"""

import sys
from pathlib import Path

from agentic_mbse.sysml.syside_adapter import get_syside

syside = get_syside()


def child(owner, name):
    feats = list(owner.owned_features.collect()) + list(owner.inherited_features.collect())
    hits = [f for f in feats if f.name == name]
    if not hits:
        raise LookupError(f"{name} not found under {owner.name}")
    return hits[0]


def evaluate(model, path):
    pkg, dotted = path.split("::", 1)
    names = dotted.split(".")
    roots = [
        p
        for p in model.elements(syside.PartUsage)
        if p.name == names[0] and p.owning_namespace is not None and p.owning_namespace.name == pkg
    ]
    scope = roots[0]
    for name in names[1:-1]:
        scope = child(scope, name)
    feature = child(scope, names[-1])
    value, report = syside.Compiler().evaluate_feature(feature, scope=scope, stdlib=model.lib)
    return value, [str(d.message) for d in report.diagnostics]


if __name__ == "__main__":
    files = [str(p) for p in Path(sys.argv[1]).rglob("*.sysml")]
    model, _ = syside.load_model(files)
    for p in sys.argv[2:]:
        try:
            print(p, "->", evaluate(model, p))
        except Exception as e:  # noqa: BLE001
            print(p, "-> ERROR", type(e).__name__, e)
