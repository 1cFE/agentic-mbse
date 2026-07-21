"""Historical/current live+codec probe for the four executable polarity/source rows."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from agentic_mbse.sysml.constraint_extraction import extract_constraint_facts
from agentic_mbse.sysml.constraint_facts import parse, serialize
from agentic_mbse.sysml.executable_profile import PROFILE_SEMANTIC_VERSION, evaluate_profile
from agentic_mbse.sysml.expression_ir import serialize_expression
from agentic_mbse.sysml.syside_adapter import get_syside

MODEL = """\
package HistoricalPolarity {
    private import ScalarValues::*;
    constraint def FixedLimit { 1.0 <= 2.0 }
    assert constraint inline_positive { 1.0 <= 2.0 }
    assert not constraint inline_negative { 1.0 <= 2.0 }
    assert constraint definition_positive : FixedLimit;
    assert not constraint definition_negative : FixedLimit;
}
"""


def _rows(facts):
    decisions = evaluate_profile(facts).decisions
    return [
        {
            "name": usage.identity.name,
            "form": usage.source.form,
            "fact_is_negated": usage.is_negated,
            "source": usage.source.effective_predicate_source.qualified_name,
            "decision_is_negated": getattr(decision, "is_negated", "<absent>"),
            "decision_expected_value": getattr(decision, "expected_value", "<absent>"),
            "predicate_ir": serialize_expression(decision.effective_predicate),
        }
        for usage, decision in zip(facts.usages, decisions, strict=True)
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-profile", required=True)
    args = parser.parse_args()
    if PROFILE_SEMANTIC_VERSION != args.expected_profile:
        raise RuntimeError(f"loaded {PROFILE_SEMANTIC_VERSION}, expected {args.expected_profile}")

    with tempfile.TemporaryDirectory(prefix="constraint-wave-r2-") as directory:
        model_path = Path(directory) / "polarity.sysml"
        model_path.write_text(MODEL)
        model, diagnostics = get_syside().try_load_model([str(model_path)])
        if diagnostics.contains_errors():
            raise RuntimeError("historical polarity probe model did not parse")
        live = extract_constraint_facts(model)
        codec = parse(serialize(live))

    live_rows = _rows(live)
    codec_rows = _rows(codec)
    if live_rows != codec_rows:
        raise AssertionError("live and codec polarity/source rows diverged")
    if [row["fact_is_negated"] for row in live_rows] != [False, True, False, True]:
        raise AssertionError("extraction did not preserve the four polarity rows")
    if len({row["predicate_ir"] for row in live_rows}) != 1:
        raise AssertionError("positive predicate bytes differ across polarity/source rows")

    if args.expected_profile.endswith("/v3"):
        if any(row["decision_is_negated"] != "<absent>" for row in live_rows):
            raise AssertionError("historical profile unexpectedly classified polarity")
    else:
        for row in live_rows:
            if row["decision_is_negated"] is not row["fact_is_negated"]:
                raise AssertionError("profile polarity differs from source fact")
            if row["decision_expected_value"] is not (not row["fact_is_negated"]):
                raise AssertionError("profile expected truth is not complementary")

    print(
        json.dumps(
            {
                "profile": PROFILE_SEMANTIC_VERSION,
                "rows": [
                    {key: value for key, value in row.items() if key != "predicate_ir"}
                    for row in live_rows
                ],
                "positive_predicate_byte_sets": 1,
                "live_codec_equal": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
