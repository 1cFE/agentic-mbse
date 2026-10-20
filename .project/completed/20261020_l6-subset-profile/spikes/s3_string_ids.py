"""Spike S3: does the legacy String check see the same element id as the contract's String finding?

    uv run python .project/active/l6-subset-profile/spikes/s3_string_ids.py

Throwaway. Two parts:

1. dc3 `60b44d5` (and `808464d` for comparison), exported with `git archive`: for every
   `string-value-omission` finding, find the live element with the finding's subject id and say
   what `check_design_attr_completeness` does with it (iterated? in designs/? skipped as EXPOSE?
   static evaluation raises?).
2. A two-spelling fixture under `designs/`: `attribute s : String = "x";` and the redefinition
   shorthand `:>> s = "y";`. Run the legacy check with its evaluator wrapped and compare ids.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from s1_trees import export, string_id_match  # noqa: E402

from agentic_mbse.validation.adr002 import is_expose_binding  # noqa: E402
from agentic_mbse.sysml.subset_extraction import extract_subset_facts  # noqa: E402
from agentic_mbse.sysml.subset_profile import evaluate_subset_profile  # noqa: E402
from agentic_mbse.sysml.syside_adapter import SysideAdapter  # noqa: E402
from agentic_mbse.validation import level6_architecture as l6  # noqa: E402

DC3 = Path.home() / "src" / "dc3"

FIXTURE = """package Lib {
    private import ScalarValues::*;
    part def Rack { attribute kind : String; attribute power : Real; }
}
"""
DESIGN = """package D {
    private import ScalarValues::*;
    private import Lib::*;
    part site : Rack {
        attribute label : String = "north";
        attribute :>> kind = "liquid";
        attribute :>> power = 5.0;
    }
}
"""


def account(model: object, result: object) -> list[str]:
    live = {
        SysideAdapter.element_id(e): e
        for t in ("AttributeUsage", "ReferenceUsage")
        for e in SysideAdapter.elements_of_type(model, t, include_subtypes=True)
    }
    attribute_usage_ids = {
        SysideAdapter.element_id(e) for e in SysideAdapter.elements_of_type(model, "AttributeUsage")
    }
    lines = []
    for f in result.findings:  # type: ignore[attr-defined]
        if f.rule_id != "string-value-omission":
            continue
        e = live.get(f.subject.element_id)
        if e is None:
            lines.append(f"  {f.subject.qualified_name}: no live element with that id")
            continue
        url = str(e.document.url)
        expr = e.feature_value_expression
        try:
            l6.evaluate_true_static_expression(expr)
            evaluation = "evaluates (no legacy error)"
        except (ValueError, TypeError) as error:
            evaluation = f"raises {type(error).__name__}"
        lines.append(
            f"  {f.subject.qualified_name}: {type(e).__name__}, "
            f"legacy iterates={f.subject.element_id in attribute_usage_ids}, "
            f"in designs/={'designs' in Path(url).parts}, "
            f"expose={is_expose_binding(e, expr)}, static eval {evaluation}"
        )
    return lines


def run(label: str, models: Path) -> None:
    files = sorted(models.rglob("*.sysml"))
    model, diagnostics = SysideAdapter.load_model(files)
    result = evaluate_subset_profile(extract_subset_facts(model))
    match = string_id_match(model, result)
    print(f"== {label}: load errors {len(list(diagnostics.errors))}")
    for key in (
        "attrs_checked",
        "legacy_unextractable_issues",
        "legacy_flagged_with_id",
        "string_findings",
        "legacy_ids_in_string_ids",
        "legacy_not_string",
    ):
        print(f"  {key}: {match[key]}")
    print(f"  string findings not flagged by legacy: {len(match['string_not_legacy'])}")
    for line in account(model, result):
        print(line)


def main() -> None:
    with tempfile.TemporaryDirectory(dir="/tmp", prefix="l6-spike-s3-") as tmp:
        work = Path(tmp)
        fixture = work / "fixture" / "models"
        (fixture / "designs").mkdir(parents=True)
        (fixture / "library").mkdir()
        (fixture / "library" / "lib.sysml").write_text(FIXTURE, encoding="utf-8")
        (fixture / "designs" / "site.sysml").write_text(DESIGN, encoding="utf-8")
        run("two-spelling fixture", fixture)
        for rev in ("60b44d5", "808464d"):
            export(DC3, rev, work / rev)
            run(f"dc3 {rev}", work / rev / "models")


if __name__ == "__main__":
    main()
