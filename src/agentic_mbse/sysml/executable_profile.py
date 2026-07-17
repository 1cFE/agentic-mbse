"""Executable profile: a pure facts-to-decisions library, no syside.

Reads Item 1/2's `ConstraintFacts` and returns, per constraint usage, exactly one outcome —
admit, block (with named diagnostics), or unassessed — so every modeled assertion ends in one
visible place and nothing reaches codegen silently (concept Design Principle 5, "silence is
never an outcome"). Imports `expression_facts`/`expression_ir`/`constraint_facts` only: no
syside, no `ValidationCode`, no pydantic (D2/I4) — L4/L6 translate `EligibilityDiagnostic.reason`
into their own `ValidationIssue`, keeping this module reusable by codegen too.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from agentic_mbse.sysml.constraint_facts import (
    ConstraintDefinitionFact,
    ConstraintFacts,
    ConstraintUsageFact,
    IdentityFact,
    LocationFact,
)
from agentic_mbse.sysml.expression_facts import OperandTypeFact
from agentic_mbse.sysml.expression_ir import (
    ExpressionIR,
    FeatureReferenceNode,
    InvocationNode,
    LiteralNode,
    OperatorNode,
    UnitAnnotationNode,
    UnsupportedNode,
)

__all__ = [
    "PROFILE_SEMANTIC_VERSION",
    "REASON_CODES",
    "Eligibility",
    "EligibilityDiagnostic",
    "PreflightResult",
    "ProfileResult",
    "UsageDecision",
    "classify_equality",
    "evaluate_profile",
    "preflight",
    "unit_compatibility",
]

# A behavior change here (e.g. relaxing the dimension-only block) bumps this, independent of
# `CONSTRAINT_FACTS_SCHEMA_VERSION` — the fact *data* didn't change, the *decisions* did (D8).
# v2 (plan.md D-R1/D-R2/D-R3, D-R4): arithmetic facts are derived from operand facts, never
# read from the declared interior fact — mixed-unit arithmetic now blocks, scalar×quantity and
# same-unit quantity ratios are newly admitted — and malformed snapshot facts block
# (`block_malformed_operand_fact`) instead of crashing an assert.
PROFILE_SEMANTIC_VERSION = "executable-profile/v2"

# The golden's 11 decision codes (S1 findings §5) plus the construct-named and default-deny
# blocks the walk (Phase 2) emits. Every `EligibilityDiagnostic.reason` is one of these (I3).
REASON_CODES = frozenset(
    {
        # Equality/unit matrix — golden-pinned (4 support, 7 block).
        "support_enum_same_enumeration",
        "support_boolean",
        "support_string",
        "support_integer",
        "block_incompatible_enumerations",
        "block_real_equality_requires_tolerance",
        "block_unit_conversion_required",
        "block_incompatible_dimensions",
        "block_unitless_dimensioned",
        "block_unknown_exact_unit",
        "block_unresolved_operand",
        # Construct-named blocks (node-kind walk).
        "block_assert_by_reference",
        "block_feature_chain",
        "block_invocation",
        "block_xor",
        "block_implies",
        "block_unsupported_node",
        # Default-deny (no admit rule matches).
        "block_unsupported_operator",
        "block_unsupported_operand_category",
        "block_non_predicate_root",
        "block_missing_predicate",
        "block_unresolved_definition",
        # Value-operation gate (executable-profile/v2 additions, plan.md D-R1/D-R3).
        "block_derived_unit_unsupported",
        "block_malformed_operand_fact",
    }
)


class Eligibility(Enum):
    """A usage's profile outcome: exactly one per usage (I1)."""

    ADMIT = "admit"
    BLOCK = "block"
    UNASSESSED = "unassessed"


@dataclass(frozen=True)
class EligibilityDiagnostic:
    """One named reason a construct blocked: what, where, on which constraint."""

    reason: str
    construct: str
    location: LocationFact | None
    constraint_identity: IdentityFact
    message: str


@dataclass(frozen=True)
class UsageDecision:
    """The profile's outcome for one `ConstraintUsageFact`."""

    identity: IdentityFact
    location: LocationFact | None
    eligibility: Eligibility
    diagnostics: list[EligibilityDiagnostic]
    unassessed_kind: str | None
    effective_predicate: ExpressionIR | None  # the exact IR the gate walked (D7/I5)


@dataclass(frozen=True)
class ProfileResult:
    """`evaluate_profile`'s full output: one decision per usage, plus derived counts."""

    decisions: list[UsageDecision]

    @property
    def admitted_count(self) -> int:
        return sum(1 for d in self.decisions if d.eligibility is Eligibility.ADMIT)

    @property
    def blocked_count(self) -> int:
        return sum(1 for d in self.decisions if d.eligibility is Eligibility.BLOCK)

    @property
    def unassessed_count(self) -> int:
        return sum(1 for d in self.decisions if d.eligibility is Eligibility.UNASSESSED)


@dataclass(frozen=True)
class PreflightResult:
    """The codegen gate's outcome: halt (`not ok`) or lower each admitted predicate."""

    ok: bool
    blocking: list[UsageDecision]
    admitted: list[UsageDecision]
    unassessed: list[UsageDecision]


# === Operand-fact gate (the matrix helpers — golden test seam) ===


def unit_compatibility(left: OperandTypeFact, right: OperandTypeFact) -> str:
    """The unit policy shared by ordering, arithmetic, and (as its first pass) equality.

    Ordered guards (design.md#implementation-notes): unresolved/unknown operand categories
    default-deny first; then exactly one operand a dimensioned quantity blocks
    (`block_unitless_dimensioned`); a quantity carrying no `UnitFact` at all is a malformed
    snapshot and blocks (`block_malformed_operand_fact`, D-R3 — named, never an assert); both
    quantity with an unknown exact unit blocks (`block_unknown_exact_unit`); both quantity
    with differing dimensions blocks (`block_incompatible_dimensions`); both quantity with the
    same dimension but differing exact units blocks (`block_unit_conversion_required`);
    anything else — both dimensionless, or both quantity with the identical exact unit — is
    `"ok"` (the admit sentinel).
    """
    if left.category == "unresolved" or right.category == "unresolved":
        return "block_unresolved_operand"
    if left.category == "unknown" or right.category == "unknown":
        return "block_unsupported_operand_category"

    left_quantity = left.category == "quantity"
    right_quantity = right.category == "quantity"
    if left_quantity != right_quantity:
        return "block_unitless_dimensioned"
    if left_quantity and right_quantity:
        if left.unit is None or right.unit is None:
            return "block_malformed_operand_fact"
        if left.unit.unit is None or right.unit.unit is None:
            return "block_unknown_exact_unit"
        if left.unit.dimension != right.unit.dimension:
            return "block_incompatible_dimensions"
        if left.unit.unit != right.unit.unit:
            return "block_unit_conversion_required"
    return "ok"


def classify_equality(left: OperandTypeFact, right: OperandTypeFact) -> str:
    """`==` eligibility: one of the golden's 11 decision codes (S1 §5).

    Precedence (design.md#implementation-notes): unresolved, then unknown category, then the
    shared unit policy, then real-valued equality (any quantity or real operand — quantity
    reaches here only once units are already proven compatible), then same-enumeration enums,
    then same-scalar-category booleans/strings/integers.
    """
    if left.category == "unresolved" or right.category == "unresolved":
        return "block_unresolved_operand"
    if left.category == "unknown" or right.category == "unknown":
        return "block_unsupported_operand_category"

    unit_reason = unit_compatibility(left, right)
    if unit_reason != "ok":
        return unit_reason

    if left.category == "quantity" or right.category == "quantity":
        return "block_real_equality_requires_tolerance"
    if left.category == "real" or right.category == "real":
        return "block_real_equality_requires_tolerance"

    if left.category == "enum" and right.category == "enum":
        if left.enumeration == right.enumeration:
            return "support_enum_same_enumeration"
        return "block_incompatible_enumerations"
    if left.category == "boolean" and right.category == "boolean":
        return "support_boolean"
    if left.category == "string" and right.category == "string":
        return "support_string"
    if left.category == "integer" and right.category == "integer":
        return "support_integer"

    # No admit rule matches this category pairing (e.g. enum vs integer) — default-deny.
    return "block_unsupported_operand_category"


# === The walk (layers 2+3: node-kind classification, operand-fact gate) ===

_COMPARISON_OPS = frozenset({"==", "<", "<=", ">", ">="})
_CONNECTIVE_OPS = frozenset({"and", "or", "not"})
_ARITHMETIC_OPS = frozenset({"+", "-", "*", "/", "**", "^"})

# The categories arithmetic can merge without a unit story (D-R1): integer∘integer stays
# integer, any real operand makes the result real.
_DIMENSIONLESS_NUMERIC = frozenset({"integer", "real"})


def _diagnostic(
    reason: str,
    construct: str,
    identity: IdentityFact,
    location: LocationFact | None,
    message: str | None = None,
) -> EligibilityDiagnostic:
    return EligibilityDiagnostic(
        reason=reason,
        construct=construct,
        location=location,
        constraint_identity=identity,
        message=message or f"{construct}: {reason}",
    )


def _leaf_fact(
    operand_type: OperandTypeFact | None,
    construct: str,
    identity: IdentityFact,
    location: LocationFact | None,
) -> OperandTypeFact | list[EligibilityDiagnostic]:
    """A leaf's declared fact — extraction ground truth — or the D-R3 malformed block.

    The snapshot codec is shape-only, so a value node can arrive carrying no operand fact;
    semantic totality is this module's job, and the answer is a named BLOCK, never an assert.
    """
    if operand_type is None:
        return [
            _diagnostic(
                "block_malformed_operand_fact",
                construct,
                identity,
                location,
                f"{construct}: value node carries no operand_type fact",
            )
        ]
    return operand_type


def _merged_numeric(left: OperandTypeFact, right: OperandTypeFact) -> OperandTypeFact:
    """Merge two dimensionless-numeric facts: integer∘integer → integer, any real → real."""
    category = "integer" if left.category == "integer" and right.category == "integer" else "real"
    return OperandTypeFact(category=category, enumeration=None, unit=None)


def _real_fact() -> OperandTypeFact:
    return OperandTypeFact(category="real", enumeration=None, unit=None)


def _quantity_ratio_fact(left: OperandTypeFact, right: OperandTypeFact) -> OperandTypeFact | str:
    """`quantity / quantity` (D-R1): only an identical-exact-unit pure ratio is provable.

    Guard order mirrors `unit_compatibility`: malformed fact, then unknown exact unit, then
    the identical-unit admit (a pure ratio needs no conversion, result is dimensionless real),
    then differing dimensions (an m/s-style derived unit — not representable), then same
    dimension with differing units (conversion needed).
    """
    if left.unit is None or right.unit is None:
        return "block_malformed_operand_fact"
    if left.unit.unit is None or right.unit.unit is None:
        return "block_unknown_exact_unit"
    if left.unit.unit == right.unit.unit:
        return _real_fact()
    if left.unit.dimension != right.unit.dimension:
        return "block_derived_unit_unsupported"
    return "block_unit_conversion_required"


def _derive_arithmetic_fact(operator: str, facts: list[OperandTypeFact]) -> OperandTypeFact | str:
    """The D-R1 unit policy: admit only what operand facts prove without a dimensional algebra.

    Guard order matches `unit_compatibility`'s docstring: unresolved first, then unknown, then
    the non-numeric categories (boolean/string/enum have no arithmetic); only dimensionless
    numerics and quantities reach the per-operator rules. `facts` is the one (unary sign) or
    two operand facts — arity is already checked by `_walk_arithmetic`.
    """
    for fact in facts:
        if fact.category == "unresolved":
            return "block_unresolved_operand"
    for fact in facts:
        if fact.category == "unknown":
            return "block_unsupported_operand_category"
    for fact in facts:
        if fact.category != "quantity" and fact.category not in _DIMENSIONLESS_NUMERIC:
            return "block_unsupported_operand_category"

    if len(facts) == 1:
        return facts[0]  # unary +/- : sign preserves the operand's category and unit

    left, right = facts
    left_quantity = left.category == "quantity"
    right_quantity = right.category == "quantity"

    if operator in ("+", "-"):
        reason = unit_compatibility(left, right)
        if reason != "ok":
            return reason
        # Both quantity means the identical exact unit is proven — the shared fact carries it.
        return left if left_quantity else _merged_numeric(left, right)

    if operator == "*":
        if left_quantity and right_quantity:
            return "block_derived_unit_unsupported"  # m·m has no representable unit here
        if left_quantity:
            return left  # scalar scaling keeps the quantity's unit (either order)
        if right_quantity:
            return right
        return _merged_numeric(left, right)

    if operator == "/":
        if left_quantity and right_quantity:
            return _quantity_ratio_fact(left, right)
        if left_quantity:
            return left  # quantity / dimensionless keeps the unit
        if right_quantity:
            return "block_derived_unit_unsupported"  # 1/m is an inverse unit
        return _real_fact()

    # ** / ^ — a quantity power is a derived unit; a dimensionless power is real-valued.
    if left_quantity or right_quantity:
        return "block_derived_unit_unsupported"
    return _real_fact()


def _walk_arithmetic(
    node: OperatorNode,
    identity: IdentityFact,
    location: LocationFact | None,
) -> OperandTypeFact | list[EligibilityDiagnostic]:
    """Derive an arithmetic node's fact from its operands' facts (D-R1/D-R2).

    Admitted arities: 2 for every arithmetic operator, plus 1 for the `+`/`-` sign forms.
    Every operand is walked and all their violations are returned together (matching the
    comparison walk's both-sides behavior) before the operator rule runs.
    """
    operator = node.operator
    operands = node.operands
    unary_sign = operator in ("+", "-") and len(operands) == 1
    if len(operands) != 2 and not unary_sign:
        expected = "1 or 2" if operator in ("+", "-") else "2"
        return [
            _diagnostic(
                "block_unsupported_node",
                "arithmetic",
                identity,
                location,
                f"arithmetic {operator!r} with {len(operands)} operands, expected {expected}",
            )
        ]
    results = [_walk_value(operand, identity, location) for operand in operands]
    diagnostics = [d for result in results if isinstance(result, list) for d in result]
    if diagnostics:
        return diagnostics
    facts = [result for result in results if isinstance(result, OperandTypeFact)]
    derived = _derive_arithmetic_fact(operator, facts)
    if isinstance(derived, str):
        return [_diagnostic(derived, "arithmetic", identity, location)]
    return derived


def _walk_value(
    node: ExpressionIR,
    identity: IdentityFact,
    location: LocationFact | None,
) -> OperandTypeFact | list[EligibilityDiagnostic]:
    """Recover a value-position node's operand fact, or the named blocks that prevent it.

    Returns the proven `OperandTypeFact` — a leaf's declared fact (extraction ground truth),
    or an arithmetic node's fact *derived* from its operands (D-R2: a declared interior fact
    is never consulted; trusting it was the F1 unit-gate bypass). Anything not admitted
    returns a non-empty diagnostic list instead: construct violations, propositions sitting
    where a value was expected (`block_non_predicate_root`, D6), and malformed snapshot facts
    (`block_malformed_operand_fact`, D-R3).
    """
    if isinstance(node, FeatureReferenceNode):
        if node.reference.chain_segments:
            return [_diagnostic("block_feature_chain", "feature_chain", identity, location)]
        return _leaf_fact(node.operand_type, "feature_ref", identity, location)

    if isinstance(node, LiteralNode):
        return _leaf_fact(node.operand_type, "literal", identity, location)

    if isinstance(node, UnitAnnotationNode):
        inner = _walk_value(node.value, identity, location)
        if isinstance(inner, list):
            return inner  # e.g. a chained reference under the annotation still blocks
        # The annotation's own declared fact carries the exact unit; the inner value's fact
        # (the bare integer under `1 [m]`) is superseded, not merged.
        return _leaf_fact(node.operand_type, "unit_annotation", identity, location)

    if isinstance(node, InvocationNode):
        return [_diagnostic("block_invocation", "invocation", identity, location)]

    if isinstance(node, UnsupportedNode):
        return [
            _diagnostic(
                "block_unsupported_node", node.node_kind, identity, location, node.diagnostic
            )
        ]

    if isinstance(node, OperatorNode):
        operator = node.operator
        if operator in ("xor", "implies"):
            return [_diagnostic(f"block_{operator}", operator, identity, location)]
        if operator in _COMPARISON_OPS or operator == "!=":
            return [_diagnostic("block_non_predicate_root", "comparison", identity, location)]
        if operator in _CONNECTIVE_OPS:
            return [_diagnostic("block_non_predicate_root", operator, identity, location)]
        if operator in _ARITHMETIC_OPS:
            return _walk_arithmetic(node, identity, location)
        # A future/unexpected operator symbol (spec's default-deny bullet) — unreachable given
        # today's closed extraction allowlist, but not assumed away.
        return [_diagnostic("block_unsupported_operator", operator, identity, location)]

    # Unreachable given ExpressionIR's closed union, kept for totality (I1).
    return [_diagnostic("block_unsupported_node", type(node).__name__, identity, location)]


def _walk_comparison(
    node: OperatorNode,
    identity: IdentityFact,
    location: LocationFact | None,
    diagnostics: list[EligibilityDiagnostic],
) -> None:
    """Recover both operands' facts and apply the equality gate or the unit policy.

    `!=` is not in the admit set (D5): it blocks outright, regardless of operand facts. An
    operand whose own value walk names a violation (nested chain, invocation, arithmetic
    block, ...) short-circuits the gate for this comparison — the nested diagnostics already
    name the problem (I2), and both sides still report.
    """
    operator = node.operator
    if operator == "!=":
        diagnostics.append(
            _diagnostic(
                "block_unsupported_operator",
                "comparison",
                identity,
                location,
                "the != operator is not in the admitted comparison set",
            )
        )
        return
    operands = node.operands
    if len(operands) != 2:
        diagnostics.append(
            _diagnostic(
                "block_unsupported_node",
                "comparison",
                identity,
                location,
                f"comparison with {len(operands)} operands, expected 2",
            )
        )
        return
    left, right = operands
    left_facts = _walk_value(left, identity, location)
    right_facts = _walk_value(right, identity, location)
    if isinstance(left_facts, list) or isinstance(right_facts, list):
        if isinstance(left_facts, list):
            diagnostics.extend(left_facts)
        if isinstance(right_facts, list):
            diagnostics.extend(right_facts)
        return

    if operator == "==":
        reason = classify_equality(left_facts, right_facts)
        if not reason.startswith("support_"):
            diagnostics.append(_diagnostic(reason, "comparison", identity, location))
    elif operator in _COMPARISON_OPS:  # <, <=, >, >=
        reason = unit_compatibility(left_facts, right_facts)
        if reason != "ok":
            diagnostics.append(_diagnostic(reason, "comparison", identity, location))
    else:
        diagnostics.append(
            _diagnostic("block_unsupported_operator", "comparison", identity, location)
        )


def _walk_proposition(
    node: ExpressionIR,
    identity: IdentityFact,
    location: LocationFact | None,
    diagnostics: list[EligibilityDiagnostic],
) -> None:
    """Classify one proposition-position node and emit named diagnostics for anything not admitted.

    A proposition position wants a comparison or connective; operand positions go through
    `_walk_value`, which returns proven facts instead of appending. A value node sitting where
    a proposition was expected blocks `block_non_predicate_root` (D6) — the same code
    `_walk_value` emits in the opposite direction: a bare-Boolean reference standing in for a
    whole predicate, and a proposition sitting where an operand's value was expected
    (design.md#implementation-notes).
    """
    if isinstance(node, FeatureReferenceNode):
        if node.reference.chain_segments:
            diagnostics.append(
                _diagnostic("block_feature_chain", "feature_chain", identity, location)
            )
            return
        diagnostics.append(
            _diagnostic("block_non_predicate_root", "feature_ref", identity, location)
        )
        return

    if isinstance(node, LiteralNode):
        diagnostics.append(_diagnostic("block_non_predicate_root", "literal", identity, location))
        return

    if isinstance(node, UnitAnnotationNode):
        diagnostics.append(
            _diagnostic("block_non_predicate_root", "unit_annotation", identity, location)
        )
        return

    if isinstance(node, InvocationNode):
        diagnostics.append(_diagnostic("block_invocation", "invocation", identity, location))
        return

    if isinstance(node, UnsupportedNode):
        diagnostics.append(
            _diagnostic(
                "block_unsupported_node", node.node_kind, identity, location, node.diagnostic
            )
        )
        return

    if isinstance(node, OperatorNode):
        operator = node.operator
        if operator in ("xor", "implies"):
            diagnostics.append(_diagnostic(f"block_{operator}", operator, identity, location))
            return
        if operator in _COMPARISON_OPS or operator == "!=":
            _walk_comparison(node, identity, location, diagnostics)
            return
        if operator in _CONNECTIVE_OPS:
            # Arity gate (v2): a vacuous connective must not admit by walking zero operands —
            # default-deny needs something to prove. `not` is unary; `and`/`or` are n-ary
            # conjunctions/disjunctions of at least two propositions.
            arity_ok = len(node.operands) == 1 if operator == "not" else len(node.operands) >= 2
            if not arity_ok:
                expected = "1" if operator == "not" else ">= 2"
                diagnostics.append(
                    _diagnostic(
                        "block_unsupported_node",
                        operator,
                        identity,
                        location,
                        f"connective {operator!r} with {len(node.operands)} operands,"
                        f" expected {expected}",
                    )
                )
                return
            for operand in node.operands:
                _walk_proposition(operand, identity, location, diagnostics)
            return
        if operator in _ARITHMETIC_OPS:
            diagnostics.append(
                _diagnostic("block_non_predicate_root", "arithmetic", identity, location)
            )
            return
        # A future/unexpected operator symbol (spec's default-deny bullet) — unreachable given
        # today's closed extraction allowlist, but not assumed away.
        diagnostics.append(_diagnostic("block_unsupported_operator", operator, identity, location))
        return

    # Unreachable given ExpressionIR's closed union, kept for totality (I1).
    diagnostics.append(
        _diagnostic("block_unsupported_node", type(node).__name__, identity, location)
    )


# === Form gate, resolution, and the top-level entry points ===


def _unassessed(usage: ConstraintUsageFact, kind: str) -> UsageDecision:
    return UsageDecision(
        identity=usage.identity,
        location=usage.location,
        eligibility=Eligibility.UNASSESSED,
        diagnostics=[],
        unassessed_kind=kind,
        effective_predicate=None,
    )


def _blocked(usage: ConstraintUsageFact, diagnostic: EligibilityDiagnostic) -> UsageDecision:
    return UsageDecision(
        identity=usage.identity,
        location=usage.location,
        eligibility=Eligibility.BLOCK,
        diagnostics=[diagnostic],
        unassessed_kind=None,
        effective_predicate=None,
    )


def _evaluate_usage(
    usage: ConstraintUsageFact, definitions_by_qn: dict[str, ConstraintDefinitionFact]
) -> UsageDecision:
    form = usage.source.form
    identity, location = usage.identity, usage.location

    if form in ("satisfy", "requirement_constraint", "plain_usage"):
        return _unassessed(usage, form)
    if form == "named_usage_reference":
        return _blocked(
            usage,
            _diagnostic("block_assert_by_reference", "assert_by_reference", identity, location),
        )
    if form not in ("inline", "definition_typed"):
        return _blocked(
            usage,
            _diagnostic(
                "block_unsupported_node",
                "unknown_form",
                identity,
                location,
                f"unrecognized constraint source form: {form!r}",
            ),
        )

    if form == "definition_typed":
        constraint_definition = usage.source.constraint_definition
        qn = constraint_definition.qualified_name if constraint_definition else None
        definition = definitions_by_qn.get(qn) if qn is not None else None
        if definition is None:
            return _blocked(
                usage,
                _diagnostic("block_unresolved_definition", "definition_lookup", identity, location),
            )
        predicate = definition.predicate
    else:
        predicate = usage.predicate

    if predicate is None:
        return _blocked(
            usage, _diagnostic("block_missing_predicate", "missing_predicate", identity, location)
        )

    diagnostics: list[EligibilityDiagnostic] = []
    _walk_proposition(predicate, identity, location, diagnostics)
    if diagnostics:
        return UsageDecision(
            identity=identity,
            location=location,
            eligibility=Eligibility.BLOCK,
            diagnostics=diagnostics,
            unassessed_kind=None,
            effective_predicate=predicate,
        )
    return UsageDecision(
        identity=identity,
        location=location,
        eligibility=Eligibility.ADMIT,
        diagnostics=[],
        unassessed_kind=None,
        effective_predicate=predicate,
    )


def evaluate_profile(facts: ConstraintFacts) -> ProfileResult:
    """Decide eligibility for every usage in `facts.usages` (I1) — never over `facts.definitions`.

    `facts.definitions` is read solely as the `definition_typed` predicate-lookup index; an unused
    `ConstraintDefinition` never becomes a decision (the concept's inventory rule, by construction).
    """
    definitions_by_qn = {
        definition.identity.qualified_name: definition
        for definition in facts.definitions
        if definition.identity.qualified_name is not None
    }
    decisions = [_evaluate_usage(usage, definitions_by_qn) for usage in facts.usages]
    return ProfileResult(decisions=decisions)


def preflight(facts: ConstraintFacts) -> PreflightResult:
    """The codegen gate: run the profile and partition its decisions by outcome."""
    result = evaluate_profile(facts)
    blocking = [d for d in result.decisions if d.eligibility is Eligibility.BLOCK]
    admitted = [d for d in result.decisions if d.eligibility is Eligibility.ADMIT]
    unassessed = [d for d in result.decisions if d.eligibility is Eligibility.UNASSESSED]
    return PreflightResult(
        ok=not blocking, blocking=blocking, admitted=admitted, unassessed=unassessed
    )
