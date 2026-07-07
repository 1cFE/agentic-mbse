"""
Item 9 (PIPELINE-TRUTH) validation checks.

C7 — the one unbuilt check the prior epic filed (ITEM-SYNC-C7). It mirrors a
codegen silent-drop: a redefinition written WITH the `attribute` keyword and an
expression value (`attribute :>> attr = <expr>`) parses as an AttributeUsage, but
codegen's redefinition scan (hierarchy_resolver._extract_single_redefinition) reads
only ReferenceUsage members — so the override is silently dropped at extraction.

Test-first, per epic R1: the negative fixture (fires-on-shape) plus the
silent-on-clean fixture (the supported bare form + the literal AttributeUsage form)
are asserted before the check exists.

- C7 L6 `attribute :>>`-with-expression redefinition -> WARN
    (attr_redef_expr fires exactly once; attr_redef_literal does NOT — its bare
     `:>>` overrides are ReferenceUsage (captured) and its one `attribute :>>` is a
     LITERAL, which C7 scopes out and semantic-operators.md teaches instead)

Fixtures live under tests/fixtures/item9/. Models load via syside
(SYSIDE_LICENSE_KEY from .env, loaded by conftest).
"""

from pathlib import Path

from agentic_mbse.sysml.types import Severity, ValidationCode
from agentic_mbse.validation.common import discover_sysml_files, load_sysml_model
from agentic_mbse.validation.level6_architecture import (
    check_attr_redef_expression_dropped,
)

FIXTURES = Path(__file__).parent.parent / "fixtures" / "item9"

_MODEL_CACHE: dict[str, object] = {}


def load_fixture(name: str):
    """Load an item9 fixture model, cached per name."""
    if name not in _MODEL_CACHE:
        files = discover_sysml_files(str(FIXTURES / name))
        model, _ = load_sysml_model(files)
        _MODEL_CACHE[name] = model
    return _MODEL_CACHE[name]


def _codes(issues) -> list[str]:
    return [i.code.value for i in issues]


# --- C7: attribute-`:>>`-with-expression dropped (L6, WARN) ---------------------


def test_c7_attr_redef_expression_warns():
    """`part variant : 'Base Plant' { attribute :>> gain = 2.0 * 3.0; }` is an
    AttributeUsage redefinition with an expression RHS — silently dropped by codegen
    (which scans only ReferenceUsage redefinitions) -> exactly one WARN, on `gain`.
    WARNING severity, so Level 6 stays passing."""
    issues = check_attr_redef_expression_dropped(load_fixture("attr_redef_expr"))
    warns = [i for i in issues if i.code == ValidationCode.L6_ATTR_REDEF_EXPR_DROPPED]
    assert len(warns) == 1, f"Expected one C7 WARN, got {_codes(issues)}"
    assert warns[0].severity == Severity.WARNING
    assert "gain" in warns[0].element_name or "gain" in warns[0].message


def test_c7_bare_and_literal_redefs_do_not_fire():
    """Negative-of-the-negative: the supported shapes must NOT fire. The bare
    `:>> gain = 7.0` and bare `:>> rate = 2.0 * 4.0` parse as ReferenceUsage
    (captured by codegen); the one `attribute :>> level = 5.0` is an AttributeUsage
    but carries a LITERAL — C7 is scoped to the expression case, so it stays silent."""
    issues = check_attr_redef_expression_dropped(load_fixture("attr_redef_literal"))
    warns = [i for i in issues if i.code == ValidationCode.L6_ATTR_REDEF_EXPR_DROPPED]
    assert warns == [], f"Supported redefinition shapes must not fire C7: {_codes(issues)}"
