"""Spike S3b: are any legacy L6_DESIGN_ATTR_UNEXTRACTABLE flags String-typed attributes?

    uv run python .project/active/l6-subset-profile/spikes/s3b_legacy_flag_types.py

Throwaway. For each tree, runs the legacy check (evaluator wrapped as in s1_trees.py) without
the contract, and prints the declared types and value expression kind of every flagged attribute.
A String-typed flag the contract has no finding for would break design-review hidden bet H1.
"""

from __future__ import annotations

import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from s1_trees import TREES, export  # noqa: E402

from agentic_mbse.sysml.syside_adapter import SysideAdapter  # noqa: E402
from agentic_mbse.validation import level6_architecture as l6  # noqa: E402


def main() -> None:
    with tempfile.TemporaryDirectory(dir="/tmp", prefix="l6-spike-s3b-") as tmp:
        for label, repo, rev in TREES:
            tree = Path(tmp) / label
            export(repo, rev, tree)
            model, _ = SysideAdapter.load_model(sorted((tree / "models").rglob("*.sysml")))
            by_expr = {
                SysideAdapter.element_id(a.feature_value_expression): a
                for a in SysideAdapter.elements_of_type(model, "AttributeUsage")
                if getattr(a, "feature_value_expression", None) is not None
            }
            flagged = []
            original = l6.evaluate_true_static_expression

            def recording(expr, _orig=original, _flagged=flagged):
                try:
                    return _orig(expr)
                except (ValueError, TypeError) as error:
                    _flagged.append((by_expr.get(SysideAdapter.element_id(expr)), str(error)))
                    raise

            l6.evaluate_true_static_expression = recording
            try:
                l6.check_design_attr_completeness(model, "designs")
            finally:
                l6.evaluate_true_static_expression = original
            types = Counter()
            kinds = Counter()
            reasons = Counter()
            for attr, reason in flagged:
                names = sorted(str(t.qualified_name) for t in (attr.types or ()))
                types[", ".join(names) or "(untyped)"] += 1
                kinds[type(attr.feature_value_expression).__name__] += 1
                reasons[reason[:90]] += 1
            print(f"== {label}: {len(flagged)} flagged")
            print("  declared types:", dict(types.most_common()))
            print("  value expression kinds:", dict(kinds.most_common()))
            print("  evaluator messages:", dict(reasons.most_common(8)))


if __name__ == "__main__":
    main()
