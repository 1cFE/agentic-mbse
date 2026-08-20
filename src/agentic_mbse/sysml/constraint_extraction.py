"""Production constraint fact extraction.

The only module in `agentic_mbse.sysml` that touches syside for constraint facts —
`expression_facts.py` and `constraint_facts.py` stay pure. Promotes S1's frozen capture
blueprint (`tests/constraint_fact_learning.py`, retired by D7) into production code, replacing
its two banned heuristics (namespace-prefix classification, `Unit`-suffix dimension strip) with
the structural discriminators the spec makes `[HARD]`.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from agentic_mbse.errors import SemanticEvidenceCode, SemanticEvidenceError
from agentic_mbse.sysml.constraint_facts import (
    ActualFact,
    ConstraintDefinitionFact,
    ConstraintFacts,
    ConstraintSource,
    ConstraintUsageFact,
    ContextFact,
    ExtractionDiagnosticFact,
    FormalFact,
    LocationFact,
    OwnerFact,
    OwningDefinitionFact,
    RedefinitionFact,
)
from agentic_mbse.sysml.expression import (
    extract_literal_value,
    is_literal_node,
    reconstruct_expression,
)
from agentic_mbse.sysml.expression_facts import (
    FeatureReferenceFact,
    IdentityFact,
    LiteralFact,
    OperandTypeFact,
    UnitFact,
)
from agentic_mbse.sysml.expression_ir import (
    ExpressionIR,
    FeatureReferenceNode,
    InvocationNode,
    LiteralNode,
    OperatorNode,
    UnitAnnotationNode,
    UnsupportedNode,
)
from agentic_mbse.sysml.reference_use import (
    MAX_EXPRESSION_DEPTH,
    ExactReferenceUse,
    inspect_reference_uses,
    materialize_operands,
    resolved_chain_target,
    resolved_referent,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter

__all__ = [
    "extract_expression_ir",
    "extract_identified_constraint_facts",
]

# Boolean-relational and boolean-connective operators: the node they head is a proposition,
# not a value, so it carries no OperandTypeFact (Core Concept: operand_type hangs off
# value-producing nodes; a comparison/connective node is not one).
_BOOLEAN_CONNECTIVE_OPERATORS = frozenset(
    {"==", "!=", "<", ">", "<=", ">=", "and", "or", "not", "implies"}
)

# The D4 allowlist's operator-symbol set: every spelling SysIDE emits `str(operator)` as for a
# supported construct. `str(operator)` already yields the SysML symbol text directly (not an
# enum-name form), so normalization is membership-checking, not name translation; an operator
# outside this set signals "unrecognized" and routes to `UnsupportedNode` (D4) rather than
# passing the raw text through.
_OPERATOR_SYMBOLS = frozenset(
    {
        "<",
        "<=",
        ">",
        ">=",
        "==",
        "!=",
        "and",
        "or",
        "not",
        "xor",
        "implies",
        "+",
        "-",
        "*",
        "/",
        "**",
        "^",
        "[",
    }
)

# Structural MF4 anchor: the measurement-unit-definition supertype every real unit
# (`SI::metre`, `SI::kilogram`, ...) specializes. Selecting the first type in a referent's
# typing chain that conforms to this — rather than a positional index or a name-suffix strip —
# is what makes the dimension a real, structurally reachable QN.
_MEASUREMENT_UNIT_QN = ("MeasurementReferences", "MeasurementUnit")

_OWNING_DEFINITION_TYPES: tuple[tuple[str, str], ...] = (
    ("PartDefinition", "part_def"),
    ("CalculationDefinition", "calc_def"),
    ("RequirementDefinition", "requirement_def"),
    ("Package", "package"),
)


class _ExtractionContext:
    """Accumulates extraction diagnostics (D2a) across one facts-extraction sweep."""

    def __init__(self) -> None:
        self.diagnostics: list[ExtractionDiagnosticFact] = []
        # The recursion's own position in the one shared traversal budget.  It lives on the
        # context because the IR dispatch recurses through several helpers that already
        # thread it, and because no caller may choose it.
        self.depth = 0


@dataclass(frozen=True)
class IdentifiedConstraintDefinition:
    """One live definition fact paired with its exact parser identity."""

    definition_id: UUID
    fact: ConstraintDefinitionFact


@dataclass(frozen=True)
class IdentifiedConstraintUsage:
    """One live usage fact and the exact definition that supplies its predicate."""

    usage_id: UUID
    effective_definition_id: UUID | None
    fact: ConstraintUsageFact


@dataclass(frozen=True)
class IdentifiedConstraintFacts:
    """Live identity sidecars around the unchanged neutral constraint facts."""

    facts: ConstraintFacts
    definitions: tuple[IdentifiedConstraintDefinition, ...]
    usages: tuple[IdentifiedConstraintUsage, ...]


@dataclass(frozen=True)
class _ExtractedConstraintUsage:
    """One neutral fact kept beside the live element that produced it."""

    element: Any
    fact: ConstraintUsageFact


#: The forms that ask for their predicate to be enforced. Only these can be *vacuous*:
#: a bare `constraint` states a condition without asking anyone to check it, so an owner
#: nobody instantiates says nothing about it.
_ASSERTED_FORMS = frozenset({"definition_typed", "inline", "named_usage_reference"})


def _typed_part_definition_ids(model: Any) -> frozenset[UUID]:
    """Every part definition that some part usage in the model is typed by.

    This is the structural stand-in for "was anything of this ever instantiated". It is
    deliberately weaker than an occurrence walk: a part definition typed by a usage that
    is itself never instantiated counts as typed here. Reaching for the stronger answer
    would mean reimplementing occurrence resolution in this layer, and the alignment rule
    is directional rather than equal -- this trigger set is a subset of what codegen
    grades vacuous, so the advisory can only ever be missing, never false.
    """
    typed: set[UUID] = set()
    for usage in SysideAdapter.elements_of_type(model, "PartUsage", include_subtypes=True):
        for relationship, target in getattr(usage, "heritage", None) or ():
            if SysideAdapter.is_instance(
                relationship, "FeatureTyping"
            ) and SysideAdapter.is_instance(target, "PartDefinition"):
                typed.add(SysideAdapter.element_id(target))
    return frozenset(typed)


def _vacuous_asserted_gate_fact(
    constraint: Any, form: str, typed_part_definitions: frozenset[UUID]
) -> ExtractionDiagnosticFact | None:
    """The advisory for an asserted gate on a part definition nothing types, else None."""
    if form not in _ASSERTED_FORMS:
        return None
    owner = getattr(constraint, "owning_type", None) or getattr(constraint, "owner", None)
    if not SysideAdapter.is_instance(owner, "PartDefinition"):
        return None
    if SysideAdapter.element_id(owner) in typed_part_definitions:
        return None
    usage_qn = _qualified_name(constraint) or "<anonymous>"
    owner_qn = _qualified_name(owner) or "<anonymous>"
    return ExtractionDiagnosticFact(
        kind="vacuous_asserted_gate",
        message=(
            f"asserted constraint {usage_qn} can never be checked: its owner {owner_qn} "
            "is not typed by any part usage in the model, so nothing instantiates it"
        ),
        operand_source=None,
        location=_location_fact(constraint),
    )


def _extract_constraint_facts(
    model: Any,
) -> tuple[ConstraintFacts, tuple[_ExtractedConstraintUsage, ...]]:
    """Extract neutral facts and retain their live producer association internally."""
    ctx = _ExtractionContext()
    candidate_contexts = list(_candidate_contexts(model))
    typed_part_definitions = _typed_part_definition_ids(model)
    constraints = sorted(
        SysideAdapter.elements_of_type(model, "ConstraintUsage", include_subtypes=True),
        key=_constraint_sort_key,
    )

    formals_cache: dict[str, list[FormalFact]] = {}

    def formals_for(definition: Any) -> list[FormalFact]:
        qualified_name = _qualified_name(definition)
        if qualified_name is None:
            return []
        if qualified_name not in formals_cache:
            formals_cache[qualified_name] = _definition_formals(model, definition, ctx)
        return formals_cache[qualified_name]

    definitions_by_qn: dict[str, Any] = {}
    usages: list[ConstraintUsageFact] = []
    usage_records: list[_ExtractedConstraintUsage] = []
    for constraint in constraints:
        form = _classify(constraint)
        # A definitions[] entry is a *reused* predicate source: only definition_typed and
        # named_usage_reference forms actually reuse a ConstraintDefinition's predicate/formals.
        # Every form's raw constraint.constraint_definition still lands unconditionally in
        # ConstraintSource.constraint_definition (see _source_fact) — that field is a separate,
        # unfiltered attribute read, not the reused-definition set.
        if form in ("definition_typed", "named_usage_reference"):
            definition = _effective_predicate_source(constraint, form)
            definition_qn = _qualified_name(definition)
            if definition_qn is not None and SysideAdapter.is_instance(
                definition, "ConstraintDefinition"
            ):
                definitions_by_qn.setdefault(definition_qn, definition)
        advisory = _vacuous_asserted_gate_fact(constraint, form, typed_part_definitions)
        if advisory is not None:
            ctx.diagnostics.append(advisory)
        usage_fact = _usage_fact(constraint, form, candidate_contexts, formals_for, ctx)
        usages.append(usage_fact)
        usage_records.append(_ExtractedConstraintUsage(constraint, usage_fact))

    definitions = [
        ConstraintDefinitionFact(
            identity=_identity_required(definitions_by_qn[qn]),
            formals=formals_for(definitions_by_qn[qn]),
            predicate=_expression_ir(
                getattr(definitions_by_qn[qn], "result_expression", None), ctx
            ),
        )
        for qn in sorted(definitions_by_qn)
    ]

    contexts = [
        fact
        for context in sorted(candidate_contexts, key=lambda item: _qualified_name(item) or "")
        if (fact := _context_fact(model, context, ctx)) is not None
    ]

    return (
        ConstraintFacts(
            definitions=definitions,
            usages=usages,
            contexts=contexts,
            diagnostics=ctx.diagnostics,
        ),
        tuple(usage_records),
    )


def extract_identified_constraint_facts(model: Any) -> IdentifiedConstraintFacts:
    """Extract neutral facts plus live-only exact usage/definition associations.

    The neutral payload comes from the same sweep, without adding parser identity to its
    schema. Exact sidecars are captured while the live SysIDE elements are still
    available, using the adapter as the sole UUID boundary.
    """
    facts, usage_records = _extract_constraint_facts(model)

    ctx = _ExtractionContext()
    formals_by_id: dict[UUID, list[FormalFact]] = {}

    def exact_formals(definition: Any) -> list[FormalFact]:
        definition_id = SysideAdapter.element_id(definition)
        if definition_id not in formals_by_id:
            formals_by_id[definition_id] = _definition_formals(model, definition, ctx)
        return formals_by_id[definition_id]

    definitions_by_id: dict[UUID, IdentifiedConstraintDefinition] = {}
    usages_by_id: dict[UUID, IdentifiedConstraintUsage] = {}
    usage_order: list[UUID] = []
    for record in usage_records:
        constraint = record.element
        usage_id = SysideAdapter.element_id(constraint)
        if usage_id in usages_by_id:
            raise ValueError(f"duplicate identified constraint usage UUID: {usage_id}")
        form = _classify(constraint)
        predicate_source = _effective_predicate_source(constraint, form)
        effective_definition_id: UUID | None = None
        if SysideAdapter.is_instance(predicate_source, "ConstraintDefinition"):
            effective_definition_id = SysideAdapter.element_id(predicate_source)
            if effective_definition_id not in definitions_by_id:
                definitions_by_id[effective_definition_id] = IdentifiedConstraintDefinition(
                    definition_id=effective_definition_id,
                    fact=ConstraintDefinitionFact(
                        identity=_identity_required(predicate_source),
                        formals=exact_formals(predicate_source),
                        predicate=_expression_ir(
                            getattr(predicate_source, "result_expression", None), ctx
                        ),
                    ),
                )
        usages_by_id[usage_id] = IdentifiedConstraintUsage(
            usage_id=usage_id,
            effective_definition_id=effective_definition_id,
            fact=record.fact,
        )
        usage_order.append(usage_id)

    return IdentifiedConstraintFacts(
        facts=facts,
        definitions=tuple(
            definitions_by_id[item]
            for item in sorted(definitions_by_id, key=lambda value: value.int)
        ),
        usages=tuple(usages_by_id[usage_id] for usage_id in usage_order),
    )


# === Identity, type, and location helpers ===


def _qualified_name(element: Any) -> str | None:
    if element is None:
        return None
    value = str(getattr(element, "qualified_name", None) or "")
    return value or None


def _resolved_qualified_name(element: Any) -> str | None:
    qualified_name = _qualified_name(element)
    if qualified_name is None or "<placeholder" in qualified_name:
        return None
    return qualified_name


def _identity(element: Any) -> IdentityFact | None:
    if element is None:
        return None
    return IdentityFact(
        kind=type(element).__name__,
        name=getattr(element, "name", None),
        qualified_name=_qualified_name(element),
    )


def _identity_required(element: Any) -> IdentityFact:
    identity = _identity(element)
    if identity is None:
        raise ValueError("expected a resolved element, got None")
    return identity


def _direct_types(element: Any) -> list[str]:
    if element is None:
        return []
    return [
        name
        for item in getattr(element, "types", ())
        if (name := _qualified_name(item)) is not None
    ]


def _conforms(result_type: Any, *qualified_name: str) -> bool:
    try:
        return bool(result_type.conforms(list(qualified_name)))
    except (TypeError, ValueError):
        return False


def _location_fact(element: Any) -> LocationFact | None:
    location = SysideAdapter.get_source_location(element)
    node = getattr(element, "cst_node", None)
    if location is None or node is None:
        return None
    file_path, line = location
    return LocationFact(file=file_path, line=line, column=node.start_point.character + 1)


def _constraint_sort_key(constraint: Any) -> tuple[int, str, str, int]:
    """Total order for swept constraints, independent of model load order (D-R5).

    `(line, qualified_name)` alone collides for anonymous asserts at the same line number
    in different files; file and column are appended as tie-breakers (not prepended — a
    file-first re-sort would churn canonical bytes for every multi-file document).
    """
    location = SysideAdapter.get_source_location(constraint)
    line = location[1] if location is not None else 0
    file_path = location[0] if location is not None else ""
    node = getattr(constraint, "cst_node", None)
    column = node.start_point.character + 1 if node is not None else 0
    return (line, _qualified_name(constraint) or "", file_path, column)


# === Structural dimension resolution (MF4) ===


def _unit_definition_qn(unit_element: Any) -> str | None:
    """The most-specific type of `unit_element` that specializes `MeasurementUnit`.

    Selects by conformance, not position: `mRef`'s typing chain lists the generic
    `MeasurementReferences::*MeasurementReference` supertypes ahead of the domain-specific unit
    definition, so a positional `[0]` (or a name-suffix strip) is not a valid substitute.
    """
    if unit_element is None:
        return None
    for candidate in getattr(unit_element, "types", ()):
        if _conforms(candidate, *_MEASUREMENT_UNIT_QN):
            return _qualified_name(candidate)
    return None


def _quantity_feature_dimension(result_type: Any) -> str | None:
    """A quantity feature's dimension, reached by following its value type's `mRef` member."""
    for value_type in getattr(result_type, "types", ()):
        for member in getattr(value_type, "members", ()):
            if getattr(member, "name", None) != "mRef":
                continue
            dimension = _unit_definition_qn(member)
            if dimension is not None:
                return dimension
    return None


def _unit_annotation_fact(expression: Any) -> UnitFact | None:
    """The `UnitFact` for a `[` unit-annotation node, or a same-unit `+`/`-` combination."""
    operator = getattr(expression, "operator", None)
    operator_str = str(operator) if operator is not None else None
    if operator_str == "[":
        operands = list(materialize_operands(expression))
        if len(operands) != 2:
            return None
        unit_referent = resolved_referent(operands[1])
        return UnitFact(
            unit=_qualified_name(unit_referent),
            dimension=_unit_definition_qn(unit_referent),
        )
    if operator_str in {"+", "-"}:
        child_units = [
            _unit_annotation_fact(operand) for operand in materialize_operands(expression)
        ]
        if child_units and all(unit == child_units[0] for unit in child_units):
            return child_units[0]
    return None


def _operand_type_fact(expression: Any) -> OperandTypeFact:
    """The recovered category/enumeration/unit facts for a value-producing expression node."""
    result_type = getattr(expression, "cached_result_type", None)
    qualified_name = _resolved_qualified_name(result_type)
    if qualified_name is None:
        return OperandTypeFact(category="unresolved", enumeration=None, unit=None)

    unit = _unit_annotation_fact(expression)
    if unit is not None:
        return OperandTypeFact(category="quantity", enumeration=None, unit=unit)

    enumeration_type = next(
        (
            item
            for item in getattr(result_type, "types", ())
            if SysideAdapter.is_instance(item, "EnumerationDefinition")
        ),
        None,
    )
    if enumeration_type is not None:
        return OperandTypeFact(
            category="enum", enumeration=_qualified_name(enumeration_type), unit=None
        )
    if _conforms(result_type, "ScalarValues", "Boolean"):
        return OperandTypeFact(category="boolean", enumeration=None, unit=None)
    if _conforms(result_type, "ScalarValues", "String"):
        return OperandTypeFact(category="string", enumeration=None, unit=None)
    if _conforms(result_type, "ScalarValues", "Integer"):
        return OperandTypeFact(category="integer", enumeration=None, unit=None)
    if _conforms(result_type, "ScalarValues", "Real"):
        return OperandTypeFact(category="real", enumeration=None, unit=None)

    dimension = _quantity_feature_dimension(result_type)
    if dimension is not None:
        return OperandTypeFact(
            category="quantity", enumeration=None, unit=UnitFact(unit=None, dimension=dimension)
        )

    return OperandTypeFact(category="unknown", enumeration=None, unit=None)


# === Predicate-tree recovery ===


def _authored_chain_segments(expression: Any) -> list[str]:
    """The authored dotted segments of one feature chain.

    Read off the closed reference use rather than re-walked here, so the segments and the
    resolved path come from the same acquisition.  An indexed chain has no exact path;
    its authored segments still describe what the model wrote, which is what the neutral
    IR records.
    """
    uses = inspect_reference_uses(expression)
    if len(uses) != 1:
        return []
    use = uses[0]
    if isinstance(use, ExactReferenceUse):
        return list(use.authored_segments)
    return use.reference.split(".")


def _reference_node(expression: Any, *, chain: bool) -> FeatureReferenceNode:
    if chain:
        target = resolved_chain_target(expression)
        chain_segments = _authored_chain_segments(expression)
    else:
        target = resolved_referent(expression)
        chain_segments = []
    if target is None:
        raise SemanticEvidenceError(
            SemanticEvidenceCode.RESOLVED_TARGET_MISSING,
            operation="extract_expression_ir",
            detail="resolved reference has no exact target",
            location=SysideAdapter.get_source_location(expression),
            reference=_qualified_name(expression) or getattr(expression, "name", None),
        )
    reference = FeatureReferenceFact(
        source_name=reconstruct_expression(expression),
        target=_identity(target),
        target_types=_direct_types(target),
        chain_segments=chain_segments,
    )
    return FeatureReferenceNode(reference=reference, operand_type=_operand_type_fact(expression))


def _literal_node(expression: Any, ctx: _ExtractionContext) -> LiteralNode:
    result_type = getattr(expression, "cached_result_type", None)
    value = extract_literal_value(expression)
    if isinstance(value, float) and not math.isfinite(value):
        ctx.diagnostics.append(
            ExtractionDiagnosticFact(
                kind="non_finite_literal",
                message=f"Non-finite literal operand encountered during extraction: {value!r}",
                operand_source=reconstruct_expression(expression),
                location=_location_fact(expression),
            )
        )
    literal = LiteralFact(
        kind=type(expression).__name__,
        value=value,
        result_type=_resolved_qualified_name(result_type),
    )
    return LiteralNode(literal=literal, operand_type=_operand_type_fact(expression))


def _normalize_operator(expression: Any) -> str | None:
    """The expression's operator, normalized to its D4 symbol, or `None` if unrecognized."""
    operator = getattr(expression, "operator", None)
    if operator is None:
        return None
    operator_str = str(operator)
    return operator_str if operator_str in _OPERATOR_SYMBOLS else None


def _unsupported_node(expression: Any, diagnostic: str | None = None) -> UnsupportedNode:
    node_kind = type(expression).__name__
    message = diagnostic or f"unknown node type: {node_kind}"
    return UnsupportedNode(
        node_kind=node_kind,
        diagnostic=message,
        source_text=reconstruct_expression(expression) or None,
    )


def _unit_annotation_node(expression: Any, ctx: _ExtractionContext) -> UnitAnnotationNode:
    operands = list(materialize_operands(expression))
    value = _expression_ir(operands[0], ctx)
    if value is None:
        raise ValueError("unit annotation expression has no value operand")
    unit_text = _unit_text(operands[1]) if len(operands) > 1 else None
    return UnitAnnotationNode(
        value=value, unit_text=unit_text, operand_type=_operand_type_fact(expression)
    )


def _unit_text(unit_operand: Any) -> str | None:
    """The unit's source spelling (`"m"`), not its canonical name (`"metre"`).

    `short_name` is the unit definition's structural symbol slot — the spelling a `[m]`
    annotation actually resolves through — distinct from `name`, its canonical identifier.
    Reading it here (rather than re-deriving text via `reconstruct_expression`, which reads
    `referent.name`) is what keeps the source spelling and the resolved name distinct facts.
    """
    referent = resolved_referent(unit_operand)
    if referent is None:
        return reconstruct_expression(unit_operand) or None
    short_name = getattr(referent, "short_name", None)
    if short_name:
        return str(short_name)
    name = getattr(referent, "name", None)
    return str(name) if name else None


def _operator_node(expression: Any, operator_str: str, ctx: _ExtractionContext) -> OperatorNode:
    operands = [
        node
        for operand in materialize_operands(expression)
        if (node := _expression_ir(operand, ctx)) is not None
    ]
    operand_type = (
        None if operator_str in _BOOLEAN_CONNECTIVE_OPERATORS else _operand_type_fact(expression)
    )
    return OperatorNode(operator=operator_str, operands=operands, operand_type=operand_type)


def _operator_expression_node(
    expression: Any, ctx: _ExtractionContext
) -> OperatorNode | UnitAnnotationNode | UnsupportedNode:
    operator_str = _normalize_operator(expression)
    if operator_str is None:
        raw_operator = getattr(expression, "operator", None)
        diagnostic = (
            f"unrecognized operator {str(raw_operator)!r}"
            if raw_operator is not None
            else "missing operator"
        )
        return _unsupported_node(expression, diagnostic)
    if operator_str == "[":
        return _unit_annotation_node(expression, ctx)
    return _operator_node(expression, operator_str, ctx)


def _invocation_node(expression: Any, ctx: _ExtractionContext) -> InvocationNode:
    function_qn_raw = getattr(expression.function, "qualified_name", None)
    function_qn = [str(part) for part in function_qn_raw] if function_qn_raw is not None else None
    arguments = [
        node
        for operand in materialize_operands(expression)
        if (node := _expression_ir(operand, ctx)) is not None
    ]
    return InvocationNode(
        function_qn=function_qn, arguments=arguments, operand_type=_operand_type_fact(expression)
    )


def extract_expression_ir(
    expression: Any,
    *,
    diagnostics: list[ExtractionDiagnosticFact] | None = None,
) -> ExpressionIR | None:
    """Public single-node entry: one live syside expression -> its ExpressionIR.

    Thin wrapper over the same dispatch the whole-model sweep uses, for
    consumers that hold a bare expression node rather than a whole model (the
    sysml-codegen calc-compat renderer, CONSTRAINT-EXEC Item 13). Pass a list as
    `diagnostics` to receive the extraction diagnostics (D2a, e.g. the
    non-finite-literal fact) that a whole-facts sweep would accumulate — they are
    appended to it; without a sink they are discarded. Unrecognized constructs
    still surface structurally as `UnsupportedNode` either way.
    """
    ctx = _ExtractionContext()
    node = _expression_ir(expression, ctx)
    if diagnostics is not None:
        diagnostics.extend(ctx.diagnostics)
    return node


def _expression_ir(expression: Any, ctx: _ExtractionContext) -> ExpressionIR | None:
    """Extract one expression's IR node under the shared traversal budget.

    Exhaustion raises the named `EXPRESSION_DEPTH_EXHAUSTED` failure rather than a bare
    `RecursionError`, which a caller cannot tell from an interpreter limit it hit some other
    way.  The dispatch itself is `_expression_ir_node`.
    """
    if expression is None:
        return None
    if ctx.depth >= MAX_EXPRESSION_DEPTH:
        raise SemanticEvidenceError(
            SemanticEvidenceCode.EXPRESSION_DEPTH_EXHAUSTED,
            operation="extract_expression_ir",
            detail="maximum expression traversal depth exhausted before the IR was built",
            location=SysideAdapter.get_source_location(expression),
            reference=_qualified_name(expression) or getattr(expression, "name", None),
        )
    ctx.depth += 1
    try:
        return _expression_ir_node(expression, ctx)
    finally:
        ctx.depth -= 1


def _expression_ir_node(expression: Any, ctx: _ExtractionContext) -> ExpressionIR | None:
    """Dispatch a live syside expression node to its ExpressionIR node (D4 allowlist).

    Fixed order — `FeatureChainExpression` before `OperatorExpression` (FCE subtypes OE) —
    matching the proven S2 dispatch. Every unrecognized metaclass or operator routes to
    `UnsupportedNode`; nothing is silently coerced.
    """
    if SysideAdapter.is_instance(expression, "FeatureChainExpression"):
        return _reference_node(expression, chain=True)
    if SysideAdapter.is_instance(expression, "OperatorExpression"):
        return _operator_expression_node(expression, ctx)
    if SysideAdapter.is_instance(expression, "FeatureReferenceExpression"):
        return _reference_node(expression, chain=False)
    if is_literal_node(expression):
        return _literal_node(expression, ctx)
    if hasattr(expression, "function") and hasattr(expression.function, "name"):
        return _invocation_node(expression, ctx)
    return _unsupported_node(expression)


# === Formals, actuals, membership, classification ===


def _direction(feature: Any) -> str | None:
    direction = getattr(feature, "direction", None)
    if direction is None:
        return None
    return str(direction.name).lower()


def _has_default(feature: Any) -> bool:
    return any(
        SysideAdapter.is_instance(relationship, "FeatureValue")
        and bool(getattr(relationship, "is_default", False))
        for relationship in getattr(feature, "owned_relationships", ())
    )


def _definition_formals(model: Any, definition: Any, ctx: _ExtractionContext) -> list[FormalFact]:
    formals = [
        feature
        for feature in SysideAdapter.elements_of_type(
            model, "AttributeUsage", include_subtypes=True
        )
        if getattr(feature, "owner", None) is definition and _direction(feature) == "in"
    ]
    return [
        FormalFact(
            name=formal.name,
            qualified_name=_qualified_name(formal),
            types=_direct_types(formal),
            has_default=_has_default(formal),
            default=_expression_ir(getattr(formal, "feature_value_expression", None), ctx)
            if _has_default(formal)
            else None,
        )
        for formal in sorted(formals, key=lambda item: item.name or "")
    ]


def _actuals(constraint: Any, ctx: _ExtractionContext) -> list[ActualFact]:
    actuals = [
        ActualFact(
            name=parameter.name,
            direction=_direction(parameter),
            formal_targets=sorted(
                name
                for relationship in getattr(parameter, "owned_redefinitions", ())
                if (name := _qualified_name(relationship.redefined_feature)) is not None
            ),
            value=_expression_ir(getattr(parameter, "feature_value_expression", None), ctx),
        )
        for parameter in getattr(constraint, "owned_parameters", ())
    ]
    return sorted(actuals, key=lambda item: item.name or "")


def _omitted_default_formals(
    constraint: Any,
    actuals: list[ActualFact],
    formals_for: Callable[[Any], list[FormalFact]],
) -> list[str]:
    definition = getattr(constraint, "constraint_definition", None)
    if definition is None:
        return []
    bound = {target for actual in actuals for target in actual.formal_targets}
    return sorted(
        formal.qualified_name
        for formal in formals_for(definition)
        if formal.has_default
        and formal.qualified_name is not None
        and formal.qualified_name not in bound
    )


def _membership_kind(constraint: Any) -> str | None:
    membership: Any = getattr(constraint, "owning_feature_membership", None)
    if not SysideAdapter.is_instance(membership, "RequirementConstraintMembership"):
        return None
    return str(membership.kind.name).lower()


def _classify(constraint: Any) -> str:
    """Classify one swept `ConstraintUsage` into one of the six source forms (MF2).

    Membership is checked first, then the assert type gate, then satisfy — keeping the branches
    type-disjoint so the `result_expression`-ownership test (the `[HARD]` replacement for the
    banned namespace-prefix test) only ever runs *inside* the assert branch, never as a
    whole-population classifier.
    """
    membership = getattr(constraint, "owning_feature_membership", None)
    if SysideAdapter.is_instance(membership, "RequirementConstraintMembership"):
        return "requirement_constraint"
    if SysideAdapter.is_instance(constraint, "AssertConstraintUsage"):
        asserted = getattr(constraint, "asserted_constraint", None)
        if asserted is not constraint:
            return "named_usage_reference"
        if getattr(constraint, "result_expression", None) is None:
            return "definition_typed"
        return "inline"
    if SysideAdapter.is_instance(constraint, "SatisfyRequirementUsage"):
        return "satisfy"
    return "plain_usage"


def _effective_predicate_source(constraint: Any, form: str) -> Any:
    if form in ("inline", "requirement_constraint"):
        return constraint
    if form == "definition_typed":
        return getattr(constraint, "constraint_definition", None)
    if form == "named_usage_reference":
        asserted = getattr(constraint, "asserted_constraint", None)
        return getattr(asserted, "constraint_definition", None)
    return None


def _source_fact(constraint: Any, form: str) -> ConstraintSource:
    return ConstraintSource(
        form=form,
        effective_predicate_source=_identity(_effective_predicate_source(constraint, form)),
        constraint_definition=_identity(getattr(constraint, "constraint_definition", None)),
        referenced_feature_target=_identity(getattr(constraint, "referenced_feature_target", None)),
        asserted_constraint=_identity(getattr(constraint, "asserted_constraint", None)),
    )


def _owning_definition(constraint: Any) -> OwningDefinitionFact:
    """Walk `owner` up to the first enclosing definition or package (D6/MF3, total)."""
    current = getattr(constraint, "owner", None)
    while current is not None:
        for type_name, kind in _OWNING_DEFINITION_TYPES:
            if SysideAdapter.is_instance(current, type_name):
                return OwningDefinitionFact(
                    kind=kind, qualified_name=_qualified_name(current) or ""
                )
        current = getattr(current, "owner", None)
    raise ValueError(f"owning_definition walk fell through for {constraint!r}")


def _inherited_into(constraint: Any, candidate_contexts: list[Any]) -> list[str]:
    owner = getattr(constraint, "owner", None)
    owners = [
        name
        for context in candidate_contexts
        if context is not owner
        and any(feature is constraint for feature in getattr(context, "features", ()))
        and (name := _qualified_name(context)) is not None
    ]
    return sorted(owners)


def _usage_fact(
    constraint: Any,
    form: str,
    candidate_contexts: list[Any],
    formals_for: Callable[[Any], list[FormalFact]],
    ctx: _ExtractionContext,
) -> ConstraintUsageFact:
    identity = _identity_required(constraint)
    owner = OwnerFact(
        owner=_identity(getattr(constraint, "owner", None)),
        owning_definition=_owning_definition(constraint),
    )
    predicate_source = _effective_predicate_source(constraint, form)
    predicate = _expression_ir(getattr(predicate_source, "result_expression", None), ctx)
    actuals = _actuals(constraint, ctx)
    return ConstraintUsageFact(
        identity=identity,
        location=_location_fact(constraint),
        source=_source_fact(constraint, form),
        owner=owner,
        scope=identity,
        membership_kind=_membership_kind(constraint),
        is_negated=getattr(constraint, "is_negated", None),
        actuals=actuals,
        omitted_default_formals=_omitted_default_formals(constraint, actuals, formals_for),
        predicate=predicate,
        inherited_into=_inherited_into(constraint, candidate_contexts),
    )


# === Context (inheritance/retyping) facts ===


def _candidate_contexts(model: Any) -> Iterator[Any]:
    for type_name in ("PartDefinition", "PartUsage", "CalculationDefinition"):
        yield from SysideAdapter.elements_of_type(model, type_name)


def _redefinitions(model: Any, context: Any, ctx: _ExtractionContext) -> list[RedefinitionFact]:
    redefinitions = [
        RedefinitionFact(
            feature=_qualified_name(feature),
            redefines=_qualified_name(relationship.redefined_feature),
            value=_expression_ir(getattr(feature, "feature_value_expression", None), ctx),
        )
        for feature in SysideAdapter.elements_of_type(
            model, "AttributeUsage", include_subtypes=True
        )
        if getattr(feature, "owner", None) is context
        for relationship in getattr(feature, "owned_redefinitions", ())
    ]
    return sorted(redefinitions, key=lambda item: item.feature or "")


def _is_standard_library_element(element: Any) -> bool:
    """Whether `element` is owned by a document under syside's own standard library.

    Every SysML v2 part/calc definition implicitly specializes a kernel type (`Parts::Part`,
    `Items::Item`, ...) and inherits the kernel features that come with it. Those facts are true
    of every model and carry no user-authored information, so they are excluded from
    `ContextFact` — a structural (document-origin) filter, not a fixture-coupled one.
    """
    tier = SysideAdapter.document_tier(element)
    return tier is SysideAdapter.document_tier_type().StandardLibrary


def _context_fact(model: Any, context: Any, ctx: _ExtractionContext) -> ContextFact | None:
    general_types = sorted(
        name
        for relationship in getattr(context, "owned_specializations", ())
        if (
            SysideAdapter.is_instance(relationship, "Subclassification")
            or SysideAdapter.is_instance(relationship, "FeatureTyping")
        )
        and not getattr(relationship, "is_implied", False)
        if (name := _qualified_name(getattr(relationship, "general", None))) is not None
    )
    inherited_constraints = sorted(
        name
        for feature in getattr(context, "features", ())
        if SysideAdapter.is_instance(feature, "ConstraintUsage")
        and getattr(feature, "owner", None) is not context
        and not _is_standard_library_element(feature)
        and (name := _qualified_name(feature)) is not None
    )
    redefinitions = _redefinitions(model, context, ctx)
    if not general_types and not inherited_constraints and not redefinitions:
        return None
    return ContextFact(
        identity=_identity_required(context),
        general_types=general_types,
        types=_direct_types(context),
        inherited_constraints=inherited_constraints,
        redefinitions=redefinitions,
    )
