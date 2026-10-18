"""PROTOTYPE executable-subset screen (throwaway evidence for EXEC-SUBSET-CONTRACT, Claim 1).

Imports agentic_mbse and syside only. It must never import sysml_codegen; it is run from the
agentic-mbse venv, where sysml_codegen is not even installed.

One run evaluates every rule, continues after a rule's inspection fails (recording the rule as
UNVERIFIED instead of clean), and prints per-rule counts with sample locations.

Usage:
    uv run python 01-screen.py <models-path> [--json out.json]

Controls (env vars, for the differential's sabotage runs):
    SCREEN_DISABLE=ES-001        rule ES-001 detects nothing (simulates a missed decision)
    SCREEN_OVERBROAD=ES-001      ES-001 also flags part-owned asserts (simulates an overbroad one)
    SCREEN_ES003_V1=1            use the FIRST-CUT ES-003 rule (flag ordered/nonunique/unbounded calc
                                 parameter declarations), which the differential found overbroad
"""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import syside

from agentic_mbse.errors import SemanticEvidenceCode, SemanticEvidenceError
from agentic_mbse.sysml.reference_use import inspect_reference_uses, resolved_referent
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.validation.level6_architecture import (
    check_constraint_executability,
    check_design_attr_completeness,
)
from agentic_mbse.sysml.types import ValidationCode

DISABLED = {r for r in os.environ.get("SCREEN_DISABLE", "").split(",") if r}
OVERBROAD = {r for r in os.environ.get("SCREEN_OVERBROAD", "").split(",") if r}
ES003_V1 = os.environ.get("SCREEN_ES003_V1") == "1"

#: rule id -> (dc3 baseline category, outcome when it fires, what it reuses)
RULES = {
    "ES-001": ("B1", "refused", "NEW fact: assertion owner metatype (syside owner)"),
    "ES-003": ("B2", "refused", "NEW fact: sequence-valued argument bound to a calc input" if not ES003_V1 else "NEW fact: calc parameter ordering/uniqueness/bounds (FIRST CUT)"),
    "ES-004": ("B3", "refused", "NEW fact: part multiplicity bounds + approximate instantiation"),
    "ES-005": ("B4/B5", "refused", "REUSED: reference_use.inspect_reference_uses admission (sum only)"),
    "ES-006": ("B6", "refused", "NEW fact: conditional operator ('if')"),
    "ES-007": ("B8", "refused/excluded", "REUSED: executable_profile via L6 check_constraint_executability"),
    "ES-010": ("B7", "omitted/refused", "NEW fact: String values (both spellings); refused when bound into a calc input"),
}


def _project(elem: Any) -> bool:
    try:
        return elem.document.document_tier == syside.DocumentTier.Project
    except Exception:
        return False


def _loc(elem: Any) -> str:
    loc = SysideAdapter.get_source_location(elem)
    if loc is None:
        return "<unknown>"
    return f"{Path(loc[0]).as_posix().split('models/')[-1]}:{loc[1]}"


def _name(elem: Any) -> str:
    return str(getattr(elem, "qualified_name", None) or getattr(elem, "name", None) or "<anonymous>")


def _is(elem: Any, *kinds: str) -> bool:
    return any(isinstance(elem, getattr(syside, k)) for k in kinds)


def _elements(model: Any, kind: str) -> list[Any]:
    return [e for e in model.elements(getattr(syside, kind), include_subtypes=True) if _project(e)]


# ---- rules -----------------------------------------------------------------------------


def rule_es001(model: Any) -> list[dict]:
    """Asserted constraint whose owner is a calculation (definition or usage)."""
    owners = ("CalculationUsage", "CalculationDefinition")
    if "ES-001" in OVERBROAD:
        owners = owners + ("PartUsage", "PartDefinition")
    out = []
    for c in _elements(model, "AssertConstraintUsage"):
        owner = c.owning_type
        if owner is not None and _is(owner, *owners):
            out.append({"location": _loc(c), "reference": _name(c), "detail": f"owner {type(owner).__name__} {_name(owner)}"})
    return out


def _bound_value(expr: Any) -> Any:
    if expr is None:
        return None
    if _is(expr, "LiteralInfinity"):
        return "inf"
    if _is(expr, "LiteralInteger"):
        return int(expr.value)
    return "modeled"  # e.g. a reference to a modeled Integer attribute


def _multiplicity(feature: Any) -> tuple[Any, Any] | None:
    mult = feature.declared_multiplicity
    if mult is None:
        return None
    lower_expr, upper_expr = mult.bounds
    upper = _bound_value(upper_expr)
    lower = upper if lower_expr is None else _bound_value(lower_expr)
    return lower, upper


def _exact(bounds: tuple[Any, Any] | None) -> bool:
    if bounds is None:
        return True
    lower, upper = bounds
    if upper == "inf":
        return False
    if "modeled" in (lower, upper):
        return lower == upper or lower == "modeled" and upper == "modeled"
    return lower == upper


def _is_comma(expr: Any) -> bool:
    op = getattr(expr, "operator", None)
    return _is(expr, "OperatorExpression") and getattr(op, "name", str(op)) in ("Comma", ",")


def rule_es003(model: Any) -> list[dict]:
    """Calc input bound to a sequence-valued argument `(a, b, ...)`.

    Second cut. The first cut (below, SCREEN_ES003_V1=1) flagged the parameter DECLARATION
    (ordered/nonunique/unbounded); the differential showed codegen admits those declarations
    when the argument is a scalar, so that cut was overbroad."""
    if not ES003_V1:
        out = []
        for f in _elements(model, "Feature"):
            owner = f.owning_type
            if owner is None or not _is(owner, "CalculationUsage") or f.direction is None:
                continue
            value = f.feature_value_expression
            if value is not None and _is_comma(value):
                out.append({"location": _loc(f), "reference": _name(f), "detail": "sequence argument " + SysideAdapter.authored_text(value)[:60]})
        return out
    out = []
    for f in _elements(model, "Feature"):
        owner = f.owning_type
        if owner is None or not _is(owner, "CalculationDefinition", "CalculationUsage"):
            continue
        if f.direction is None:
            continue
        bounds = _multiplicity(f)
        reasons = []
        if f.is_ordered:
            reasons.append("ordered")
        if f.is_nonunique:
            reasons.append("nonunique")
        if not _exact(bounds):
            reasons.append(f"bounds {bounds}")
        if reasons:
            out.append({"location": _loc(f), "reference": _name(f), "detail": ", ".join(reasons)})
    return out


def _types(usage: Any) -> list[Any]:
    for attr in ("part_definitions", "definitions", "types"):
        value = getattr(usage, attr, None)
        if value is not None:
            try:
                return list(value)
            except TypeError:
                continue
    return []


def rule_es004(model: Any) -> list[dict]:
    """Part multiplicity that is unbounded or a range in an instantiated context, unless a
    project redefinition states an exact count. Instantiation is APPROXIMATED here: a part
    definition counts as instantiated if any project part usage is typed by it or a subtype."""
    parts = _elements(model, "PartUsage")
    exact_redefined: set[str] = set()
    for p in parts:
        if _exact(_multiplicity(p)):
            for r in p.owned_redefinitions:
                if r.redefined_feature is not None:
                    exact_redefined.add(_name(r.redefined_feature))
    typed_by: list[Any] = [t for p in parts for t in _types(p)]

    def instantiated(definition: Any) -> bool:
        for t in typed_by:
            try:
                if t is definition or t.conforms(definition):
                    return True
            except Exception:
                if _name(t) == _name(definition):
                    return True
        return False

    out = []
    for p in parts:
        bounds = _multiplicity(p)
        if _exact(bounds):
            continue
        if _name(p) in exact_redefined:
            continue
        owner = p.owning_type
        if owner is not None and _is(owner, "PartDefinition") and not instantiated(owner):
            continue
        out.append({"location": _loc(p), "reference": _name(p), "detail": f"bounds {bounds}"})
    return out


def rule_es005(model: Any) -> tuple[list[dict], list[dict]]:
    """Invocation of a function outside the admitted set, via the SHARED admission."""
    out: dict[str, dict] = {}
    unverified = []
    for node in _elements(model, "InvocationExpression"):
        if _is(node, "OperatorExpression"):
            continue
        try:
            inspect_reference_uses(node)
        except SemanticEvidenceError as error:
            if error.code is SemanticEvidenceCode.EXPRESSION_KIND_UNSUPPORTED:
                loc = error.location
                key = f"{Path(loc[0]).as_posix().split('models/')[-1]}:{loc[1]}" if loc else _loc(node)
                out.setdefault(key + "|" + str(error.reference), {"location": key, "reference": str(error.reference), "detail": str(error.detail).split(":")[0][:90]})
            else:
                unverified.append({"location": _loc(node), "reference": _name(node), "detail": f"{error.code.value}"})
    return list(out.values()), unverified


def rule_es006(model: Any) -> list[dict]:
    out = []
    for node in _elements(model, "OperatorExpression"):
        op = getattr(node, "operator", None)
        if getattr(op, "name", str(op)) in ("If", "if"):
            out.append({"location": _loc(node), "reference": SysideAdapter.authored_text(node)[:80], "detail": "conditional expression"})
    return out


def rule_es007(model: Any) -> list[dict]:
    out = []
    for issue in check_constraint_executability(model):
        outcome = "refused" if issue.code == ValidationCode.L6_CONSTRAINT_MALFORMED_NUMERICAL else "excluded"
        out.append({"location": str(issue.location).split("models/")[-1], "reference": issue.element_name, "detail": f"{outcome}: {issue.reason_code}", "outcome": outcome})
    return out


def _is_string_typed(attr: Any) -> bool:
    seen = 0
    stack = [attr]
    while stack and seen < 20:
        seen += 1
        f = stack.pop()
        for t in _types(f):
            if _name(t) == "ScalarValues::String":
                return True
        for r in f.owned_redefinitions:
            if r.redefined_feature is not None:
                stack.append(r.redefined_feature)
    return False


def rule_es010(model: Any) -> list[dict]:
    out = []
    # Both spellings: `attribute x : String = ".."` is an AttributeUsage, while the shorthand
    # `:>> x = ".."` parses as a ReferenceUsage. Today's L6 only inspects the first.
    for a in _elements(model, "AttributeUsage") + [r for r in _elements(model, "ReferenceUsage") if r.direction is None]:
        value = a.feature_value_expression
        if value is None:
            continue
        if _is(value, "LiteralString") or _is_string_typed(a):
            spelling = "shorthand :>> (ReferenceUsage)" if _is(a, "ReferenceUsage") else ("attribute :>> redefinition" if list(a.owned_redefinitions) else "attribute declaration")
            out.append({"location": _loc(a), "reference": _name(a), "detail": f"String value, {spelling} spelling", "outcome": "omitted"})
    # executable dependency: a calc input whose argument resolves to a String-typed feature
    for f in _elements(model, "Feature"):
        owner = f.owning_type
        if owner is None or not _is(owner, "CalculationUsage") or f.direction is None:
            continue
        value = f.feature_value_expression
        if value is None or not _is(value, "FeatureReferenceExpression"):
            continue
        target = resolved_referent(value)
        if target is not None and (_is_string_typed(target) or _is(getattr(target, "feature_value_expression", None), "LiteralString")):
            out.append({"location": _loc(f), "reference": _name(f), "detail": f"String feature {_name(target)} bound into calc input", "outcome": "refused"})
    return out


def run(paths: list[Path]) -> dict:
    model, diagnostics = SysideAdapter.load_model(paths)
    model = getattr(model, "value", model)
    results: dict[str, dict] = {}

    def record(rule: str, fn) -> None:
        bcat, outcome, reuse = RULES[rule]
        if rule in DISABLED:
            results[rule] = {"category": bcat, "status": "checked", "outcome": outcome, "findings": [], "unverified": [], "reuse": reuse, "note": "DISABLED by control"}
            return
        try:
            found = fn(model)
            unverified: list[dict] = []
            if isinstance(found, tuple):
                found, unverified = found
            results[rule] = {"category": bcat, "status": "checked", "outcome": outcome, "findings": found, "unverified": unverified, "reuse": reuse}
        except Exception as error:  # principle 5: a failed rule is UNVERIFIED, never clean
            results[rule] = {"category": bcat, "status": "UNVERIFIED", "outcome": outcome, "findings": [], "unverified": [{"detail": f"{type(error).__name__}: {error}"}], "reuse": reuse}

    for rule, fn in [("ES-001", rule_es001), ("ES-003", rule_es003), ("ES-004", rule_es004), ("ES-005", rule_es005), ("ES-006", rule_es006), ("ES-007", rule_es007), ("ES-010", rule_es010)]:
        record(rule, fn)

    # comparison: what today's L6 says about String attributes
    try:
        l6_issues, _ = check_design_attr_completeness(model)
        results["ES-010"]["l6_today_unextractable"] = sum(1 for i in l6_issues if i.code == ValidationCode.L6_DESIGN_ATTR_UNEXTRACTABLE)
    except Exception as error:
        results["ES-010"]["l6_today_unextractable"] = f"check failed: {error}"
    return results


def blocking(results: dict) -> int:
    n = 0
    for rule, r in results.items():
        if r["status"] != "checked":
            n += 1
            continue
        for f in r["findings"]:
            if f.get("outcome", r["outcome"]).startswith("refused"):
                n += 1
    return n


def main() -> int:
    args = sys.argv[1:]
    out_json = None
    if "--json" in args:
        i = args.index("--json")
        out_json = args[i + 1]
        del args[i : i + 2]
    paths = [Path(a) for a in args]
    results = run(paths)
    print(f"PROTOTYPE subset screen — one run over {', '.join(map(str, paths))}")
    print(f"controls: disable={sorted(DISABLED) or '-'} overbroad={sorted(OVERBROAD) or '-'}")
    print(f"{'rule':7} {'dc3':6} {'status':10} {'outcome':16} {'findings':>8}  reuse")
    for rule, r in results.items():
        print(f"{rule:7} {r['category']:6} {r['status']:10} {r['outcome']:16} {len(r['findings']):>8}  {r['reuse']}")
    print()
    for rule, r in results.items():
        if r["findings"]:
            by_file = defaultdict(int)
            for f in r["findings"]:
                by_file[f["location"].rsplit(":", 1)[0]] += 1
            print(f"--- {rule} ({r['category']}): {len(r['findings'])} findings in {len(by_file)} files")
            for f in r["findings"][:4]:
                print(f"    {f['location']}  {f['reference']}  [{f['detail']}]")
            if len(r["findings"]) > 4:
                print(f"    ... {len(r['findings']) - 4} more")
        for u in r["unverified"][:3]:
            print(f"    UNVERIFIED {rule}: {u}")
    if "l6_today_unextractable" in results.get("ES-010", {}):
        print(f"\nES-010 comparison: today's L6 L6_DESIGN_ATTR_UNEXTRACTABLE = {results['ES-010']['l6_today_unextractable']} vs screen String-valued attributes = {len(results['ES-010']['findings'])}")
    print(f"\nblocking (refused or unverified) total: {blocking(results)}")
    if out_json:
        Path(out_json).write_text(json.dumps(results, indent=1))
    return 1 if blocking(results) else 0


if __name__ == "__main__":
    sys.exit(main())
