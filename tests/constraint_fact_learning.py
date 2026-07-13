"""Test-only neutral fact capture for the S1 live-SysIDE learning test.

This is deliberately not production schema code. It records the SysIDE 0.8.4
shapes that a later production design may rely on, without using Compiler or
any evaluator API.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.syside_adapter import get_syside

syside = get_syside()

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "constraint_fact_shapes"
SOURCE_FORMS = FIXTURE_DIR / "source_forms.sysml"
TYPE_UNITS = FIXTURE_DIR / "type_units.sysml"


def _qualified_name(element: Any) -> str | None:
    if element is None:
        return None
    value = str(getattr(element, "qualified_name", None) or "")
    return value or None


def _identity(element: Any) -> dict[str, Any] | None:
    if element is None:
        return None
    return {
        "kind": type(element).__name__,
        "name": getattr(element, "name", None),
        "qualified_name": _qualified_name(element),
    }


def _source_text(element: Any, source: str) -> str | None:
    node = getattr(element, "cst_node", None)
    if node is None:
        return None
    text = node.text(source)
    return text if text else None


def _location(element: Any, filename: str) -> dict[str, Any] | None:
    node = getattr(element, "cst_node", None)
    if node is None:
        return None
    return {
        "file": filename,
        "line": node.start_point.line + 1,
        "column": node.start_point.character + 1,
    }


def _direct_types(element: Any) -> list[str]:
    return [
        name
        for item in getattr(element, "types", ())
        if (name := _qualified_name(item)) is not None
    ]


def _property_value(element: Any, name: str) -> Any:
    value = getattr(element, name, None)
    return value() if callable(value) else value


def _expression_fact(expression: Any, source: str) -> dict[str, Any] | None:
    if expression is None:
        return None

    fact: dict[str, Any] = {
        "kind": type(expression).__name__,
        "source": _source_text(expression, source),
    }
    operator = getattr(expression, "operator", None)
    if operator is not None:
        fact["operator"] = str(operator)
    if hasattr(expression, "value"):
        fact["value"] = expression.value

    result_type = getattr(expression, "cached_result_type", None)
    if result_type is not None:
        fact["result_type"] = {
            **(_identity(result_type) or {}),
            "types": _direct_types(result_type),
        }

    referent = getattr(expression, "referent", None)
    if referent is not None:
        qualified_name = _qualified_name(referent)
        fact["reference"] = {
            "source_name": _source_text(expression, source),
            "target": _identity(referent),
            "target_types": _direct_types(referent),
            "resolved": qualified_name is not None and "<placeholder" not in qualified_name,
        }

    target_feature = getattr(expression, "target_feature", None)
    if target_feature is not None:
        fact["target_feature"] = {
            "target": _identity(target_feature),
            "target_types": _direct_types(target_feature),
        }

    operands = list(getattr(expression, "operands", ()))
    if operands:
        fact["operands"] = [_expression_fact(operand, source) for operand in operands]
    return fact


def _has_default(feature: Any) -> bool:
    return any(
        type(relationship).__name__ == "FeatureValue"
        and bool(getattr(relationship, "is_default", False))
        for relationship in getattr(feature, "owned_relationships", ())
    )


def _definition_formals(model: Any, definition: Any, source: str) -> list[dict[str, Any]]:
    formals = [
        feature
        for feature in model.elements(syside.AttributeUsage, include_subtypes=True)
        if getattr(feature, "owner", None) is definition
        and str(getattr(feature, "direction", "")) == "FeatureDirectionKind.In"
    ]
    return [
        {
            "name": formal.name,
            "qualified_name": _qualified_name(formal),
            "types": _direct_types(formal),
            "has_default": _has_default(formal),
            "default": _expression_fact(formal.feature_value_expression, source)
            if _has_default(formal)
            else None,
        }
        for formal in sorted(formals, key=lambda item: item.name or "")
    ]


def _actuals(constraint: Any, source: str) -> list[dict[str, Any]]:
    actuals = []
    for parameter in getattr(constraint, "owned_parameters", ()):
        formal_targets = sorted(
            name
            for relationship in getattr(parameter, "owned_redefinitions", ())
            if (name := _qualified_name(relationship.redefined_feature)) is not None
        )
        actuals.append(
            {
                "name": parameter.name,
                "direction": str(getattr(parameter, "direction", None)),
                "formal_targets": formal_targets,
                "value": _expression_fact(parameter.feature_value_expression, source),
            }
        )
    return sorted(actuals, key=lambda item: item["name"] or "")


def _source_form(constraint: Any) -> str:
    if isinstance(constraint, syside.SatisfyRequirementUsage):
        return "satisfy"
    if isinstance(constraint, syside.AssertConstraintUsage):
        asserted = constraint.asserted_constraint
        if asserted is not constraint:
            return "named_usage_reference"
        definition = constraint.constraint_definition
        if (_qualified_name(definition) or "").startswith("ConstraintFactShapeProbe::"):
            return "definition_typed"
        return "inline"
    if isinstance(constraint.owning_feature_membership, syside.RequirementConstraintMembership):
        return "requirement_constraint"
    return "plain_usage"


def _membership_kind(constraint: Any) -> str | None:
    membership = constraint.owning_feature_membership
    if not isinstance(membership, syside.RequirementConstraintMembership):
        return None
    return membership.kind.name.lower()


def _effective_predicate_source(constraint: Any) -> Any:
    source_form = _source_form(constraint)
    if source_form == "inline" or source_form == "requirement_constraint":
        return constraint
    if source_form == "definition_typed":
        return constraint.constraint_definition
    if source_form == "named_usage_reference":
        return constraint.asserted_constraint.constraint_definition
    return None


def _model_contexts(model: Any) -> list[Any]:
    contexts: list[Any] = []
    for kind in (syside.PartDefinition, syside.PartUsage, syside.CalculationDefinition):
        contexts.extend(model.elements(kind))
    return [
        context
        for context in contexts
        if (_qualified_name(context) or "").startswith("ConstraintFactShapeProbe::")
    ]


def _inherited_into(constraint: Any, contexts: list[Any]) -> list[str]:
    owners = []
    for context in contexts:
        if context is getattr(constraint, "owner", None):
            continue
        if any(feature is constraint for feature in getattr(context, "features", ())):
            if name := _qualified_name(context):
                owners.append(name)
    return sorted(owners)


def _omitted_defaults(model: Any, constraint: Any, source: str) -> list[str]:
    definition = constraint.constraint_definition
    if not (_qualified_name(definition) or "").startswith("ConstraintFactShapeProbe::"):
        return []
    bound = {
        target
        for actual in _actuals(constraint, source)
        for target in actual["formal_targets"]
    }
    return sorted(
        formal["qualified_name"]
        for formal in _definition_formals(model, definition, source)
        if formal["has_default"] and formal["qualified_name"] not in bound
    )


def _diagnostic_facts(diagnostics: Any, filename: str) -> list[dict[str, Any]]:
    facts = []
    for diagnostic in diagnostics.all:
        match = re.search(r":(\d+):(\d+):", str(diagnostic))
        facts.append(
            {
                "file": filename,
                "line": int(match.group(1)) if match else None,
                "column": int(match.group(2)) if match else None,
                "severity": diagnostic.severity.name.lower(),
                "code": diagnostic.code,
                "message": diagnostic.message,
            }
        )
    return facts


def _context_fact(model: Any, context: Any, source: str) -> dict[str, Any]:
    redefinitions = []
    for feature in model.elements(syside.AttributeUsage, include_subtypes=True):
        if getattr(feature, "owner", None) is not context:
            continue
        for relationship in getattr(feature, "owned_redefinitions", ()):
            redefinitions.append(
                {
                    "feature": _qualified_name(feature),
                    "redefines": _qualified_name(relationship.redefined_feature),
                    "value": _expression_fact(feature.feature_value_expression, source),
                }
            )
    return {
        "identity": _identity(context),
        "general_types": sorted(
            name
            for relationship in getattr(context, "owned_specializations", ())
            if type(relationship).__name__ in {"Subclassification", "FeatureTyping"}
            if (name := _qualified_name(getattr(relationship, "general", None))) is not None
        ),
        "types": _direct_types(context),
        "inherited_constraints": sorted(
            name
            for feature in getattr(context, "features", ())
            if isinstance(feature, syside.ConstraintUsage)
            and getattr(feature, "owner", None) is not context
            and (name := _qualified_name(feature)) is not None
            and name.startswith("ConstraintFactShapeProbe::")
        ),
        "redefinitions": sorted(redefinitions, key=lambda item: item["feature"] or ""),
    }


def capture_source_form_facts() -> dict[str, Any]:
    source = SOURCE_FORMS.read_text()
    model, diagnostics = syside.try_load_model([str(SOURCE_FORMS)])
    contexts = _model_contexts(model)
    constraints = [
        item
        for item in model.elements(syside.ConstraintUsage, include_subtypes=True)
        if (_qualified_name(getattr(item, "owner", None)) or "").startswith(
            "ConstraintFactShapeProbe::"
        )
        or (_qualified_name(item) or "").startswith("ConstraintFactShapeProbe::")
    ]
    constraints.sort(
        key=lambda item: (
            (_location(item, SOURCE_FORMS.name) or {}).get("line", 0),
            _qualified_name(item) or "",
        )
    )

    definitions = [
        definition
        for definition in model.elements(syside.ConstraintDefinition)
        if (_qualified_name(definition) or "").startswith("ConstraintFactShapeProbe::")
    ]
    constraint_facts = []
    for constraint in constraints:
        predicate_source = _effective_predicate_source(constraint)
        constraint_facts.append(
            {
                "identity": _identity(constraint),
                "location": _location(constraint, SOURCE_FORMS.name),
                "source_form": _source_form(constraint),
                "owner": _identity(getattr(constraint, "owner", None)),
                "scope": _identity(constraint),
                "membership_kind": _membership_kind(constraint),
                "is_negated": getattr(constraint, "is_negated", None),
                "constraint_definition": _identity(constraint.constraint_definition),
                "asserted_constraint": _identity(
                    getattr(constraint, "asserted_constraint", None)
                ),
                "referenced_feature_target": _identity(
                    _property_value(constraint, "referenced_feature_target")
                ),
                "actuals": _actuals(constraint, source),
                "omitted_default_formals": _omitted_defaults(
                    model, constraint, source
                ),
                "effective_predicate_source": _identity(predicate_source),
                "predicate": _expression_fact(
                    getattr(predicate_source, "result_expression", None), source
                ),
                "inherited_into": _inherited_into(constraint, contexts),
            }
        )

    named_contexts = {"DerivedProbe", "retyped_usage"}
    return {
        "diagnostics": _diagnostic_facts(diagnostics, SOURCE_FORMS.name),
        "definitions": [
            {
                "identity": _identity(definition),
                "formals": _definition_formals(model, definition, source),
                "predicate": _expression_fact(definition.result_expression, source),
            }
            for definition in sorted(definitions, key=lambda item: _qualified_name(item) or "")
        ],
        "constraints": constraint_facts,
        "contexts": [
            _context_fact(model, context, source)
            for context in sorted(contexts, key=lambda item: _qualified_name(item) or "")
            if context.name in named_contexts
        ],
    }


def _conforms(result_type: Any, *qualified_name: str) -> bool:
    if result_type is None:
        return False
    try:
        return bool(result_type.conforms(list(qualified_name)))
    except (TypeError, ValueError):
        return False


def _unit_fact(expression: Any) -> dict[str, Any] | None:
    operator_value = getattr(expression, "operator", None)
    operator = str(operator_value) if operator_value is not None else None
    if operator == "[":
        operands = list(expression.operands)
        if len(operands) != 2:
            return None
        unit = getattr(operands[1], "referent", None)
        unit_types = _direct_types(unit)
        dimension_type = next((item for item in unit_types if item.endswith("Unit")), None)
        dimension = dimension_type.removesuffix("Unit") if dimension_type else None
        return {"unit": _qualified_name(unit), "dimension": dimension}

    if operator in {"+", "-"}:
        child_units = [_unit_fact(item) for item in expression.operands]
        if child_units and all(item == child_units[0] for item in child_units):
            return child_units[0]
    return None


def _operand_fact(expression: Any, source: str) -> dict[str, Any]:
    result_type = getattr(expression, "cached_result_type", None)
    qualified_name = _qualified_name(result_type)
    types = _direct_types(result_type)
    resolved = qualified_name is not None and "<placeholder" not in qualified_name
    unit = _unit_fact(expression)

    category = "unknown"
    enumeration = None
    if not resolved:
        category = "unresolved"
    elif unit is not None:
        category = "quantity"
    else:
        enumeration_type = next(
            (
                item
                for item in getattr(result_type, "types", ())
                if type(item).__name__ == "EnumerationDefinition"
            ),
            None,
        )
        if enumeration_type is not None:
            category = "enum"
            enumeration = _qualified_name(enumeration_type)
        elif _conforms(result_type, "ScalarValues", "Boolean"):
            category = "boolean"
        elif _conforms(result_type, "ScalarValues", "String"):
            category = "string"
        elif _conforms(result_type, "ScalarValues", "Integer"):
            category = "integer"
        elif _conforms(result_type, "ScalarValues", "Real"):
            category = "real"
        elif quantity_type := next(
            (item for item in types if item.startswith("ISQBase::") and item.endswith("Value")),
            None,
        ):
            category = "quantity"
            unit = {
                "unit": None,
                "dimension": quantity_type.removesuffix("Value"),
            }
        elif qualified_name == "Quantities::TensorQuantityValue":
            category = "quantity"

    return {
        "source": _source_text(expression, source),
        "category": category,
        "result_type": qualified_name,
        "types": types,
        "enumeration": enumeration,
        "unit": unit,
    }


def _equality_decision(left: dict[str, Any], right: dict[str, Any]) -> str:
    categories = {left["category"], right["category"]}
    if "unresolved" in categories:
        return "block_unresolved_operand"
    if categories == {"enum"}:
        if left["enumeration"] == right["enumeration"]:
            return "support_enum_same_enumeration"
        return "block_incompatible_enumerations"
    if categories == {"boolean"}:
        return "support_boolean"
    if categories == {"string"}:
        return "support_string"
    if categories == {"integer"}:
        return "support_integer"
    if categories <= {"integer", "real"}:
        return "block_real_equality_requires_tolerance"
    if categories == {"quantity"}:
        left_unit = left["unit"]
        right_unit = right["unit"]
        if (
            left_unit is None
            or right_unit is None
            or left_unit["unit"] is None
            or right_unit["unit"] is None
        ):
            return "block_unknown_exact_unit"
        if left_unit["dimension"] != right_unit["dimension"]:
            return "block_incompatible_dimensions"
        if left_unit["unit"] != right_unit["unit"]:
            return "block_unit_conversion_required"
        return "block_real_equality_requires_tolerance"
    if "quantity" in categories:
        return "block_unitless_dimensioned"
    return "block_incompatible_operand_categories"


def capture_type_unit_facts() -> dict[str, Any]:
    source = TYPE_UNITS.read_text()
    model, diagnostics = syside.try_load_model([str(TYPE_UNITS)])
    constraints = {
        constraint.name: constraint
        for constraint in model.elements(syside.AssertConstraintUsage)
        if constraint.name
    }
    case_names = [
        "enum_own",
        "enum_incompatible",
        "integer_real",
        "integer_integer",
        "boolean_boolean",
        "string_string",
        "quantity_same_unit",
        "quantity_convertible_unit",
        "quantity_incompatible_dimension",
        "unit_bearing_arithmetic",
        "unitless_dimensioned",
        "quantity_feature_unknown_unit",
        "unresolved_operand",
        "inherited_alias_type",
    ]
    cases = []
    for name in case_names:
        expression = constraints[name].result_expression
        left_expression, right_expression = list(expression.operands)
        left = _operand_fact(left_expression, source)
        right = _operand_fact(right_expression, source)
        cases.append(
            {
                "name": name,
                "left": left,
                "right": right,
                "decision": _equality_decision(left, right),
            }
        )
    return {
        "diagnostics": _diagnostic_facts(diagnostics, TYPE_UNITS.name),
        "equality_cases": cases,
        "compound_boolean": _expression_fact(
            constraints["compound_boolean"].result_expression, source
        ),
    }


def capture_all_facts() -> dict[str, Any]:
    return {
        "schema": "constraint-fact-learning-test/v1",
        "syside_version": syside.__version__,
        "source_forms": capture_source_form_facts(),
        "type_units": capture_type_unit_facts(),
    }
