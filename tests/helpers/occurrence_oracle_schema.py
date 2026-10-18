"""The F1 oracle JSON schema, and the one normalizer that turns port output into it (P-3).

The codegen oracle (`scripts/subset_profile/occurrence_oracle.py`) writes what sysml-codegen
`b5663c07` computes for one model in this schema. `to_oracle_schema` renders the port's
`OccurrenceStructure` or `OccurrenceFailure` the same way, so the parity test and
`scripts/subset_profile/occurrence_parity.py` compare like with like. Both import this module;
neither carries its own copy of the rendering.

This is the only place generator codes meet the port's neutral vocabulary: the two tables
below map a multiplicity resolution and an occurrence abort to the `SI_*` code the generator
raises for it. They are evidence for the comparison, not product vocabulary.

Schema (keys the port produces; the oracle adds `names`, `inputs`, `load_errors`, `full` and
`identity`, which `strip_oracle_only_fields` removes):

- `roots`: generator root usage ids, sorted.
- `visits`: `[usage, parent path or null]` per visit, sorted.
- `unexpandable`: `[usage, parent path or null, SI code]` per visit that does not expand.
- `occurrences`: `{path, usage, type, closure, children}` per occurrence, sorted by path.
- `counts`: occurrences per effective usage.
- `def_occurrences`: occurrences per part definition (closure membership).
- `writers`: `[scope key, base, selected, applicable]` per (scope, calc slot), sorted.
- `writers_status`: `ok` when any writer was selected, else `no_calc_usages_selected`.
- `calc_attachment`: per calc usage, `[scope keys, cause or null]`.
- `strict`: `{"ok": true}`, or `{"ok": false, "code"}` for the first unexpandable visit in
  traversal order, which is the error the unpatched generator raises.
- An abort case is `{"fatal": {"stage", "code"}}` only. Abort cases match on stage and code.

A path renders as `slot[index]/slot[index]...` with an empty index for an unindexed step; a
scope as `occ:<path>` or `pkg:<package id>`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from agentic_mbse.sysml.occurrence_facts import (
    MultiplicityResolution,
    OccurrenceAbort,
    OccurrenceFailure,
    OccurrenceScope,
    OccurrenceStructure,
    PathStep,
    Scope,
)

#: `occurrence.py:812-899`: the code `_multiplicity_indices` raises for each unexpandable class.
RESOLUTION_TO_CODE: Mapping[MultiplicityResolution, str] = {
    MultiplicityResolution.ORDERED: "SI_MULTIPLICITY_UNSUPPORTED",
    MultiplicityResolution.NONUNIQUE: "SI_MULTIPLICITY_UNSUPPORTED",
    MultiplicityResolution.RANGE: "SI_MULTIPLICITY_UNSUPPORTED",
    MultiplicityResolution.UNRESOLVED_UPPER: "SI_MULTIPLICITY_UNRESOLVED",
    MultiplicityResolution.UNRESOLVED_LOWER: "SI_MULTIPLICITY_UNRESOLVED",
    MultiplicityResolution.NEGATIVE: "SI_MULTIPLICITY_INVALID",
}

#: The code each mirrored raise carries (`InvalidRedefinitionFamilyError`,
#: `RecursiveContainmentError`, `ElaborationInvariantError`, `IdentityBoundaryError`).
ABORT_TO_CODE: Mapping[OccurrenceAbort, str] = {
    OccurrenceAbort.SPECIALIZATION_CYCLE: "SI_CONTAINMENT_RECURSIVE",
    OccurrenceAbort.RECURSIVE_CONTAINMENT: "SI_CONTAINMENT_RECURSIVE",
    OccurrenceAbort.INCOMPARABLE_TYPINGS: "SI_REDEFINITION_INVALID",
    OccurrenceAbort.REPEATED_NATIVE_DECLARATION: "SI_REDEFINITION_INVALID",
    OccurrenceAbort.DUPLICATE_OCCURRENCE_IDENTITY: "SI_REDEFINITION_INVALID",
    OccurrenceAbort.REDEFINITION_ROOT_FAMILY: "SI_REDEFINITION_INVALID",
    OccurrenceAbort.EFFECTIVE_DECLARATION_AMBIGUOUS: "SI_REDEFINITION_INVALID",
    OccurrenceAbort.WRITER_AMBIGUOUS: "SI_REDEFINITION_INVALID",
    OccurrenceAbort.IDENTITY_UNSTABLE: "SI_ID_UNSTABLE",
}

#: The keys the port's rendering carries. Everything else in a capture is the oracle's own.
PORT_FIELDS = (
    "roots",
    "visits",
    "unexpandable",
    "occurrences",
    "counts",
    "def_occurrences",
    "writers",
    "writers_status",
    "calc_attachment",
    "strict",
)


def render_path(path: tuple[PathStep, ...]) -> str:
    return "/".join(f"{step.slot}[{'' if step.index is None else step.index}]" for step in path)


def render_scope(scope: Scope) -> str:
    if isinstance(scope, OccurrenceScope):
        return "occ:" + render_path(scope.path)
    return f"pkg:{scope.package_id}"


def to_oracle_schema(result: OccurrenceStructure | OccurrenceFailure) -> dict[str, Any]:
    """Render the port's answer for one model in the oracle's schema.

    Only generator reach has an oracle equivalent, so a structure with caller roots is
    refused rather than rendered with them silently dropped.
    """
    if isinstance(result, OccurrenceFailure):
        return {"fatal": {"stage": result.stage.value, "code": ABORT_TO_CODE[result.abort]}}
    if result.caller_root_ids:
        raise ValueError("the oracle schema covers generator roots only; got caller roots")

    def parent_key(parent: tuple[PathStep, ...] | None) -> str | None:
        return None if parent is None else render_path(parent)

    unexpandable = [v for v in result.visits if v.count is None]
    first = unexpandable[0] if unexpandable else None
    return {
        "roots": sorted(str(r) for r in result.generator_root_ids),
        "visits": sorted(
            ([str(v.usage_id), parent_key(v.parent)] for v in result.visits),
            key=lambda c: (c[0] or "", c[1] or ""),
        ),
        "unexpandable": sorted(
            (
                [str(v.usage_id), parent_key(v.parent), RESOLUTION_TO_CODE[v.reading.resolution]]
                for v in unexpandable
            ),
            key=lambda c: (c[0] or "", c[1] or ""),
        ),
        "occurrences": sorted(
            (
                {
                    "path": render_path(n.path),
                    "usage": str(n.usage_id),
                    "type": None if n.type_id is None else str(n.type_id),
                    "closure": sorted(str(t) for t in n.type_closure),
                    "children": sorted(str(c) for c in n.child_ids),
                }
                for n in result.nodes
            ),
            key=lambda r: str(r["path"]),
        ),
        "counts": {str(k): v for k, v in sorted(result.occurrence_counts().items(), key=_by_str)},
        "def_occurrences": {
            str(d): result.definition_occurrence_count(d) for d in result.part_definition_ids
        },
        "writers": sorted(
            [
                render_scope(w.scope),
                str(w.base_id),
                str(w.selected_id),
                sorted(str(a) for a in w.applicable_ids),
            ]
            for w in result.writers
        ),
        "writers_status": "ok" if result.writers else "no_calc_usages_selected",
        "calc_attachment": {
            str(a.usage_id): [
                sorted(render_scope(s) for s in a.scopes),
                None if a.cause is None else a.cause.value,
            ]
            for a in result.calc_attachments
        },
        "strict": (
            {"ok": True}
            if first is None
            else {"ok": False, "code": RESOLUTION_TO_CODE[first.reading.resolution]}
        ),
    }


def _by_str(item: tuple[Any, int]) -> str:
    return str(item[0])


def strip_oracle_only_fields(expected: Mapping[str, Any]) -> dict[str, Any]:
    """The part of a codegen-oracle capture the port must reproduce exactly.

    Raises on a capture the oracle could not complete, because such a file is not evidence.
    """
    if "oracle_crash" in expected:
        raise ValueError("the capture records an oracle crash; recapture it")
    if "fatal" in expected:
        fatal = expected["fatal"]
        return {"fatal": {"stage": fatal["stage"], "code": fatal["code"]}}
    missing = [k for k in PORT_FIELDS if k not in expected]
    if missing:
        raise ValueError(f"the capture lacks port fields {missing}")
    stripped = {k: expected[k] for k in PORT_FIELDS}
    strict = expected["strict"]
    stripped["strict"] = {"ok": True} if strict["ok"] else {"ok": False, "code": strict["code"]}
    return stripped


def schema_differences(expected: Mapping[str, Any], actual: Mapping[str, Any]) -> list[str]:
    """Human-readable differences between two renderings, one line per differing item."""
    lines: list[str] = []
    for key in sorted(set(expected) | set(actual)):
        want, got = expected.get(key), actual.get(key)
        if want == got:
            continue
        if isinstance(want, list) and isinstance(got, list):
            want_set = {repr(x) for x in want}
            got_set = {repr(x) for x in got}
            lines += [f"{key}: codegen only {x}" for x in sorted(want_set - got_set)]
            lines += [f"{key}: port only {x}" for x in sorted(got_set - want_set)]
        elif isinstance(want, dict) and isinstance(got, dict):
            for sub in sorted(set(want) | set(got)):
                if want.get(sub) != got.get(sub):
                    lines.append(f"{key}[{sub}]: codegen {want.get(sub)!r} port {got.get(sub)!r}")
        else:
            lines.append(f"{key}: codegen {want!r} port {got!r}")
    return lines
