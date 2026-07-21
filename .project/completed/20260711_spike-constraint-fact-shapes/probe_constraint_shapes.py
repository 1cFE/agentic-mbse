"""Throwaway live-SysIDE inspector for S1 constraint fact shapes.

This script deliberately uses semantic properties only. It never constructs a
``syside.Compiler`` and never invokes an evaluator.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import syside


def identity(element: Any) -> dict[str, Any] | None:
    if element is None:
        return None
    return {
        "type": type(element).__name__,
        "name": getattr(element, "name", None),
        "qualified_name": str(getattr(element, "qualified_name", None) or "") or None,
    }


def result_type(expression: Any) -> dict[str, Any] | None:
    result = getattr(expression, "cached_result_type", None)
    return identity(result)


def property_value(element: Any, name: str) -> Any:
    value = getattr(element, name, None)
    return value() if callable(value) else value


def expression_shape(expression: Any, seen: set[int] | None = None) -> Any:
    if expression is None:
        return None
    if seen is None:
        seen = set()
    if id(expression) in seen:
        return {"type": type(expression).__name__, "cycle": True}
    seen.add(id(expression))

    shape: dict[str, Any] = {
        "type": type(expression).__name__,
        "operator": getattr(expression, "operator", None),
        "value": getattr(expression, "value", None),
        "result_type": result_type(expression),
    }
    for attribute in ("referent", "target_feature", "referenced_feature_target"):
        try:
            target = getattr(expression, attribute, None)
        except Exception as error:  # pragma: no cover - exploratory visibility
            shape[f"{attribute}_error"] = repr(error)
        else:
            if callable(target):
                try:
                    target = target()
                except Exception as error:  # pragma: no cover
                    shape[f"{attribute}_error"] = repr(error)
                    continue
            if target is not None:
                shape[attribute] = identity(target)

    operands = []
    try:
        operands = list(getattr(expression, "operands", ()))
    except Exception as error:  # pragma: no cover
        shape["operands_error"] = repr(error)
    if operands:
        shape["operands"] = [expression_shape(operand, seen.copy()) for operand in operands]
    return {key: value for key, value in shape.items() if value is not None}


def parameter_shape(parameter: Any) -> dict[str, Any]:
    return {
        "identity": identity(parameter),
        "direction": str(getattr(parameter, "direction", None)),
        "types": [identity(item) for item in getattr(parameter, "types", ())],
        "redefines": [
            identity(item.redefined_feature)
            for item in getattr(parameter, "owned_redefinitions", ())
        ],
        "value": expression_shape(getattr(parameter, "feature_value_expression", None)),
    }


def constraint_shape(constraint: Any) -> dict[str, Any]:
    membership = getattr(constraint, "owning_feature_membership", None)
    asserted = getattr(constraint, "asserted_constraint", None)
    return {
        "identity": identity(constraint),
        "owner": identity(getattr(constraint, "owner", None)),
        "owning_type": identity(getattr(constraint, "owning_type", None)),
        "membership": {
            **(identity(membership) or {}),
            "kind": str(getattr(membership, "kind", None)),
            "referenced_constraint": identity(
                getattr(membership, "referenced_constraint", None)
            ),
        },
        "is_negated": getattr(constraint, "is_negated", None),
        "asserted_constraint": identity(asserted),
        "constraint_definition": identity(getattr(constraint, "constraint_definition", None)),
        "types": [identity(item) for item in getattr(constraint, "types", ())],
        "owned_parameters": [
            parameter_shape(parameter)
            for parameter in getattr(constraint, "owned_parameters", ())
        ],
        "owned_redefinitions": [
            {
                "redefining": identity(item.redefining_feature),
                "redefined": identity(item.redefined_feature),
            }
            for item in getattr(constraint, "owned_redefinitions", ())
        ],
        "referenced_feature_target": identity(
            property_value(constraint, "referenced_feature_target")
        ),
        "result_expression": expression_shape(getattr(constraint, "result_expression", None)),
    }


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name(
        "probe_source_forms.sysml"
    )
    model, diagnostics = syside.try_load_model([str(path)])
    constraints = sorted(
        model.elements(syside.ConstraintUsage, include_subtypes=True),
        key=lambda item: str(getattr(item, "qualified_name", "")),
    )
    payload = {
        "syside_version": getattr(syside, "__version__", None),
        "diagnostics": str(diagnostics).replace(str(path), path.name).splitlines(),
        "constraints": [constraint_shape(item) for item in constraints],
    }
    print(json.dumps(payload, indent=2, sort_keys=True, default=str))
    return 1 if diagnostics.contains_errors(warnings_as_errors=False) else 0


if __name__ == "__main__":
    raise SystemExit(main())
