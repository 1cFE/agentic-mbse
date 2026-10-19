"""The two routed advisories L6 shows beside the subset contract (Item 3 design D12, D15).

Neither is a generator refusal and neither is part of `subset_profile_rules.toml` or its
digest; each is at most a WARNING (Item 1's matrix rows, class `advisory_omission_policy`).

- **Opaque expression** (matrix row `PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-SHAPE-MESSAGE`): an
  expression site where `reconstruct_expression` can render some node only as `str(node)`,
  so no message can name that node's shape. Detected by `text_fallback_nodes`, which shares
  `reconstruct_expression`'s own dispatch.
- **Wrapper** (matrix row `PUSH-DOWN-AGG-PROFILE-WRAPPER-SHAPE`): a site invoking the standard
  `sum` whose aggregation decomposition unwrapped a known wrapper (`Evaluation`, `evaluate`,
  `collect`, `select`; `aggregation.KNOWN_WRAPPER_FUNCTIONS`). Generation unwraps these
  permissively. Any other call inside `sum` (`abs`, say) is ES-005's refusal, not this.

Both walk the contract's own expression sites (`subset_extraction.expression_sites`). When a
walker raises `SemanticEvidenceError`, its own "could not inspect" signal, the site gets an
`AdvisoryUnverified` record instead (D15). Any other exception propagates to the caller, which
reports it as a check failure.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from agentic_mbse.errors import SemanticEvidenceCode, SemanticEvidenceError
from agentic_mbse.sysml.aggregation import (
    KNOWN_WRAPPER_FUNCTIONS,
    decompose_aggregation_expression,
)
from agentic_mbse.sysml.expression import text_fallback_nodes
from agentic_mbse.sysml.fact_refs import SafeLocation
from agentic_mbse.sysml.invocation_allowlist import STANDARD_SUM_FUNCTION_ID
from agentic_mbse.sysml.occurrence_extraction import safe_location
from agentic_mbse.sysml.reference_use import invocation_uses
from agentic_mbse.sysml.subset_extraction import expression_sites

__all__ = [
    "Advisory",
    "AdvisoryKind",
    "AdvisoryUnverified",
    "Advisories",
    "extract_advisories",
]


class AdvisoryKind(StrEnum):
    OPAQUE_EXPRESSION = "opaque-expression"
    WRAPPER = "wrapper"

    @property
    def matrix_row(self) -> str:
        return _MATRIX_ROW[self]


_MATRIX_ROW = {
    AdvisoryKind.OPAQUE_EXPRESSION: "PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-SHAPE-MESSAGE",
    AdvisoryKind.WRAPPER: "PUSH-DOWN-AGG-PROFILE-WRAPPER-SHAPE",
}


@dataclass(frozen=True)
class Advisory:
    """One advisory at one expression site.

    `node_kinds` are the SysIDE node types the opaque advisory found, or the wrapper functions
    the wrapper advisory found, in walk order.
    """

    kind: AdvisoryKind
    location: SafeLocation
    node_kinds: tuple[str, ...]


@dataclass(frozen=True)
class AdvisoryUnverified:
    """An advisory that could not inspect one site: its walker raised `SemanticEvidenceError`."""

    kind: AdvisoryKind
    location: SafeLocation
    code: SemanticEvidenceCode
    node_kind: str
    detail: str


@dataclass(frozen=True)
class Advisories:
    findings: tuple[Advisory, ...]
    unverified: tuple[AdvisoryUnverified, ...]


def _site_location(declaration: Any, expression: Any) -> SafeLocation:
    where = safe_location(expression)
    return SafeLocation(where.file, where.line, safe_location(declaration).qualified_name)


def _opaque(expression: Any, location: SafeLocation) -> Advisory | None:
    nodes = text_fallback_nodes(expression)
    if not nodes:
        return None
    return Advisory(
        AdvisoryKind.OPAQUE_EXPRESSION, location, tuple(type(n).__name__ for n in nodes)
    )


def _invokes_sum(expression: Any) -> bool:
    return any(use.callable_id == STANDARD_SUM_FUNCTION_ID for use in invocation_uses(expression))


def _wrapper(expression: Any, location: SafeLocation) -> Advisory | None:
    if not _invokes_sum(expression):
        return None
    wrappers = tuple(
        w.function_name
        for w in decompose_aggregation_expression(expression).wrappers
        if w.function_name in KNOWN_WRAPPER_FUNCTIONS
    )
    if not wrappers:
        return None
    return Advisory(AdvisoryKind.WRAPPER, location, wrappers)


_WALKERS = (
    (AdvisoryKind.OPAQUE_EXPRESSION, _opaque),
    (AdvisoryKind.WRAPPER, _wrapper),
)


def extract_advisories(model: Any) -> Advisories:
    """Both advisories over every contract expression site, sorted by location then kind."""
    findings: list[Advisory] = []
    unverified: list[AdvisoryUnverified] = []
    for declaration, expression in expression_sites(model):
        location = _site_location(declaration, expression)
        for kind, walk in _WALKERS:
            try:
                found = walk(expression, location)
            except SemanticEvidenceError as error:
                unverified.append(
                    AdvisoryUnverified(
                        kind, location, error.code, type(expression).__name__, error.detail
                    )
                )
                continue
            if found is not None:
                findings.append(found)
    return Advisories(
        findings=tuple(sorted(findings, key=lambda a: (a.location.sort_key(), a.kind.value))),
        unverified=tuple(
            sorted(unverified, key=lambda u: (u.location.sort_key(), u.kind.value, u.detail))
        ),
    )
