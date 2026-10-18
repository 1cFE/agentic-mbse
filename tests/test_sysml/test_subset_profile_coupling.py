"""No consumer coupling (design invariant 6, spec "No consumer coupling")."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import tomllib

import agentic_mbse
from agentic_mbse.sysml.subset_profile import SUBSET_REASON_CODES, rule_ids, rule_shapes
from tests.helpers.subset_records import packaged_text

PACKAGE = Path(agentic_mbse.__file__).parent
GENERATOR_CODE = re.compile(r"SI_[A-Z_]+")
CONSUMER_TYPES = ("ElaborationCode", "ReadinessCode")
#: The only record fields that may hold a generator code: evidence, never decisions.
EVIDENCE_FIELDS = {"expected_code", "code"}


def imported_modules(path: Path) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            modules |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_no_agentic_module_imports_the_generator() -> None:
    offenders = sorted(
        str(path.relative_to(PACKAGE))
        for path in PACKAGE.rglob("*.py")
        if any(m.split(".")[0] == "sysml_codegen" for m in imported_modules(path))
    )
    assert offenders == []


def test_the_import_scan_sees_a_generator_import(tmp_path: Path) -> None:
    probe = tmp_path / "x.py"
    probe.write_text("from sysml_codegen.elaboration import elaborate\n")
    assert "sysml_codegen.elaboration" in imported_modules(probe)


def test_no_rule_or_reason_id_is_a_generator_or_consumer_name() -> None:
    names = [*SUBSET_REASON_CODES, *rule_ids(), *(s for r in rule_ids() for s in rule_shapes(r))]
    for name in names:
        assert not GENERATOR_CODE.search(name) and not name.lower().startswith("si_"), name
        assert not any(t.lower() in name.lower() for t in CONSUMER_TYPES), name


def generator_codes_outside_evidence(value: object, key: str = "") -> list[str]:
    if isinstance(value, dict):
        return [hit for k, v in value.items() for hit in generator_codes_outside_evidence(v, k)]
    if isinstance(value, list):
        return [hit for v in value for hit in generator_codes_outside_evidence(v, key)]
    if isinstance(value, str) and GENERATOR_CODE.search(value) and key not in EVIDENCE_FIELDS:
        return [f"{key}={value!r}"]
    return []


def test_generator_codes_appear_in_the_records_only_in_evidence_fields() -> None:
    data = tomllib.loads(packaged_text())
    # semantic_limits and remedy are prose for modelers and may not name a code either
    assert generator_codes_outside_evidence(data) == []


def test_the_record_scan_finds_a_code_in_a_decision_field() -> None:
    assert generator_codes_outside_evidence({"reason": "SI_SELF_BINDING"}) == [
        "reason='SI_SELF_BINDING'"
    ]
