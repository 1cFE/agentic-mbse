"""Build rule-record TOML for tests, so every test record goes through the real loader.

`packaged_data()` parses the shipped records; `dump_records` writes the parsed form back as
TOML (the records schema only: strings, integers, string lists and nested arrays of tables);
`records_with` keeps every rule's metadata and replaces all admissions with the given ones.
"""

from __future__ import annotations

import copy
import json
from collections.abc import Mapping
from importlib import resources
from typing import Any

import tomllib

from agentic_mbse.sysml.subset_profile import RuleRecords, load_rule_records

RECORDS_RESOURCE = resources.files("agentic_mbse.sysml").joinpath("subset_profile_rules.toml")


def packaged_text() -> str:
    return RECORDS_RESOURCE.read_text(encoding="utf-8")


def packaged_data() -> dict[str, Any]:
    return tomllib.loads(packaged_text())


def _value(value: Any) -> str:
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list) and all(not isinstance(v, dict) for v in value):
        return "[" + ", ".join(_value(v) for v in value) + "]"
    raise TypeError(f"not a records scalar: {value!r}")


def _table(lines: list[str], path: str, table: Mapping[str, Any], array: bool) -> None:
    lines.append(f"[[{path}]]" if array else f"[{path}]")
    nested: list[tuple[str, Any, bool]] = []
    for key, value in table.items():
        if isinstance(value, dict):
            nested.append((key, value, False))
        elif isinstance(value, list) and value and all(isinstance(v, dict) for v in value):
            nested.append((key, value, True))
        else:
            lines.append(f"{key} = {_value(value)}")
    for key, value, is_array in nested:
        for item in value if is_array else [value]:
            _table(lines, f"{path}.{key}", item, is_array)


def dump_records(data: Mapping[str, Any]) -> str:
    lines = [f"schema = {_value(data['schema'])}"]
    _table(lines, "verified_against", data["verified_against"], array=False)
    for rule in data["rule"]:
        _table(lines, "rule", rule, array=True)
    return "\n".join(lines) + "\n"


Pairs = Mapping[tuple[str, str], Mapping[str, str]]


def data_with(pairs: Pairs) -> dict[str, Any]:
    """The packaged data with exactly these admissions: (rule, shape) -> {context: outcome}."""
    data = copy.deepcopy(packaged_data())
    for rule in data["rule"]:
        rule.pop("example_case", None)
        observed = 0
        for shape in rule["shape"]:
            shape.pop("admission", None)
            shape.pop("no_admitted_context", None)
            shape.pop("unobservable", None)
            chosen = pairs.get((rule["id"], shape["id"]), {})
            if chosen:
                observed += 1
                shape["admission"] = [
                    {
                        "context": context,
                        "outcome": outcome,
                        "evidence": [f"case:{rule['id']}__{shape['id']}__{context}"],
                    }
                    for context, outcome in sorted(chosen.items())
                ]
                rule["example_case"] = shape["admission"][0]["evidence"][0].removeprefix("case:")
        rule["evidence_status"] = (
            "code_read_pending_item_2"
            if observed == 0
            else "case_observed"
            if observed == len(rule["shape"])
            else "partial"
        )
    return data


def records_with(pairs: Pairs) -> RuleRecords:
    return load_rule_records(dump_records(data_with(pairs)))
