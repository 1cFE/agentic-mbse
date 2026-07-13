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

from agentic_mbse.sysml.constraint_facts import ConstraintFacts, IdentityFact, LocationFact
from agentic_mbse.sysml.expression_facts import OperandTypeFact
from agentic_mbse.sysml.expression_ir import ExpressionIR

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
PROFILE_SEMANTIC_VERSION = "executable-profile/v1"

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
    (`block_unitless_dimensioned`); both quantity with an unknown exact unit blocks
    (`block_unknown_exact_unit`); both quantity with differing dimensions blocks
    (`block_incompatible_dimensions`); both quantity with the same dimension but differing
    exact units blocks (`block_unit_conversion_required`); anything else — both dimensionless,
    or both quantity with the identical exact unit — is `"ok"` (the admit sentinel).
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
        assert left.unit is not None and right.unit is not None
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


def evaluate_profile(facts: ConstraintFacts) -> ProfileResult:
    """Decide eligibility for every usage in `facts` (Phase 2)."""
    raise NotImplementedError


def preflight(facts: ConstraintFacts) -> PreflightResult:
    """The codegen gate: run the profile and partition its decisions (Phase 2)."""
    raise NotImplementedError
