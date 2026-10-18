"""F1 oracle: codegen b5663c07's own occurrence/attachment/writer-selection answers.

Runs inside the isolated sysml-codegen venv. Every answer comes from codegen code:
- build_feature_slot_index / build_occurrence_index, with ONE patch: the module-level
  `_multiplicity_indices` is wrapped so a MultiplicityExpansionError is recorded and the usage
  yields no occurrences (instead of aborting the whole build). That turns fail-fast into a
  per-usage answer for criterion (e); the unpatched (strict) build is also run and its outcome
  recorded so the first-error behavior is compared too.
- _ExactElaborator._attachment / _select_writer / _build_calculation_nodes, on a bare
  instance carrying only the slot and occurrence indexes; `_typed_definition` raises a sentinel
  so the run stops after the writer-selection loop (which completes before that call).
- When codegen's full elaboration (`elaborate_model_paths(strict=False)`) succeeds, its graph's
  occurrences and calc nodes are cross-checked against the partial oracle above.

Usage: python -I oracle.py OUT.json MODEL_PATH [MODEL_PATH ...]
"""

from __future__ import annotations

import json
import sys
import traceback
from collections import defaultdict
from pathlib import Path

from agentic_mbse.sysml.syside_adapter import SysideAdapter
from sysml_codegen.elaboration import elaborate as E
from sysml_codegen.elaboration import occurrence as O
from sysml_codegen.elaboration.identity import OccurrenceId, PackageScopeId, declaration_id_for


def u(decl) -> str:
    return str(decl.value if hasattr(decl, "value") else decl)


def did(element) -> str:
    return u(declaration_id_for(element))


def path_of(occ_id: OccurrenceId) -> str:
    return "/".join(
        f"{u(step.containment_slot.root_declaration)}[{'' if step.occurrence_index is None else step.occurrence_index}]"
        for step in occ_id.steps
    )


def scope_key(scope) -> str:
    if isinstance(scope, PackageScopeId):
        return "pkg:" + u(scope.package_declaration)
    return "occ:" + path_of(scope)


class _Stop(Exception):
    pass


def error_info(error: BaseException) -> dict:
    code = getattr(error, "code", None)
    return {"type": type(error).__name__, "code": str(getattr(code, "value", code)), "detail": str(getattr(error, "detail", error))[:300]}


def oracle(model) -> dict:
    out: dict = {"names": {}}
    for kind in ("PartUsage", "PartDefinition", "CalculationUsage", "Package"):
        for element in SysideAdapter.elements_of_type(model, kind):
            if getattr(element, "qualified_name", None) is not None:
                out["names"][did(element)] = str(element.qualified_name)

    try:
        slots = O.build_feature_slot_index(model)
    except Exception as error:  # codegen invariant error: whole-model outcome
        out["fatal"] = {"stage": "slots", **error_info(error)}
        return out

    # strict (unpatched) occurrence build: success, or the first error codegen raises
    try:
        O.build_occurrence_index(model, slots)
        out["strict"] = {"ok": True}
    except Exception as error:
        out["strict"] = {"ok": False, **error_info(error)}

    # lenient: record per-usage multiplicity outcome, continue
    original = O._multiplicity_indices
    calls: list[tuple] = []
    unexpandable: list[tuple] = []

    def recording(usage, *, parent, **kwargs):
        calls.append((did(usage), path_of(parent.occurrence_id) if parent else None))
        try:
            return original(usage, parent=parent, **kwargs)
        except O.MultiplicityExpansionError as error:
            unexpandable.append((did(usage), path_of(parent.occurrence_id) if parent else None, error.code.value))
            return ()

    O._multiplicity_indices = recording
    try:
        index = O.build_occurrence_index(model, slots)
    except Exception as error:
        out["fatal"] = {"stage": "occurrences", **error_info(error)}
        return out
    finally:
        O._multiplicity_indices = original

    out["roots"] = sorted({usage for usage, parent in calls if parent is None})
    out["visits"] = sorted([list(c) for c in calls], key=lambda c: (c[0], c[1] or ""))
    out["unexpandable"] = sorted([list(x) for x in unexpandable], key=lambda c: (c[0], c[1] or ""))
    out["occurrences"] = sorted(
        [
            {
                "path": path_of(o.occurrence_id),
                "usage": u(o.effective_usage_id),
                "type": u(o.effective_type_id) if o.effective_type_id else None,
                "closure": sorted(u(t) for t in o.type_closure),
                "children": sorted(u(c) for c in o.child_declaration_ids),
            }
            for o in index.occurrences()
        ],
        key=lambda r: r["path"],
    )
    counts: dict[str, int] = defaultdict(int)
    for o in index.occurrences():
        counts[u(o.effective_usage_id)] += 1
    out["counts"] = dict(sorted(counts.items()))
    out["def_occurrences"] = {
        did(d): len(index.occurrences_for_type(declaration_id_for(d)))
        for d in SysideAdapter.elements_of_type(model, "PartDefinition")
        if getattr(d, "qualified_name", None) is not None
    }

    # writer selection for calc usages, on codegen's own elaborator methods
    elab = E._ExactElaborator.__new__(E._ExactElaborator)
    elab._model = model
    elab._slots = slots
    elab._occurrences = index
    elab._scope_display = {o.occurrence_id: o.display_path for o in index.occurrences()}
    selections: list[list] = []
    original_select = elab._select_writer

    def select(base, applicable, scope):
        chosen = original_select(base, applicable, scope)
        selections.append([scope_key(scope), did(base), did(chosen), sorted(did(a) for a in applicable)])
        return chosen

    elab._select_writer = select

    def stop(*_a, **_k):
        raise _Stop

    elab._typed_definition = stop
    try:
        elab._build_calculation_nodes()
        writers_status = "no_calc_usages_selected"
    except _Stop:
        writers_status = "ok"
    except Exception as error:
        writers_status = "error"
        out["writers_error"] = error_info(error)
    out["writers_status"] = writers_status
    out["writers"] = sorted(selections)
    # attachment per calc-usage owner (scope count), from codegen's _attachment
    attach = {}
    for usage in SysideAdapter.elements_of_type(model, "CalculationUsage"):
        scopes, cause = elab._attachment(O.semantic_owner(usage))
        attach[did(usage)] = [sorted(scope_key(s) for s in scopes), cause]
    out["calc_attachment"] = dict(sorted(attach.items()))
    return out


def full_crosscheck(paths: list[Path], partial: dict) -> dict:
    from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths

    try:
        graph = elaborate_model_paths(paths, strict=False)
    except Exception as error:
        return {"ran": False, **error_info(error)}
    occ = sorted(path_of(k) for k in graph.occurrences)
    # graph.calcs also holds computed-attribute nodes (keyed by slot); keep calc-usage nodes only
    calcs = sorted(
        [scope_key(key.scope), u(key.declaration)]
        for key, n in graph.calcs.items()
        if key.kind.value == "calculation" and not hasattr(key.declaration, "root_declaration")
    )
    want_occ = [o["path"] for o in partial.get("occurrences", [])]
    want_calcs = sorted([w[0], w[2]] for w in partial.get("writers", []))
    return {"ran": True, "occurrences_equal": occ == want_occ, "calcs_equal": calcs == want_calcs, "n_occ": len(occ), "n_calcs": len(calcs)}


def main() -> int:
    out_path = Path(sys.argv[1])
    paths = [Path(p) for p in sys.argv[2:]]
    model, diagnostics = SysideAdapter.load_model(paths)
    result: dict = {"inputs": [str(p) for p in paths], "load_errors": bool(diagnostics is not None and diagnostics.contains_errors())}
    try:
        result.update(oracle(model))
    except Exception:
        result["oracle_crash"] = traceback.format_exc()
    result["full"] = full_crosscheck(paths, result)
    out_path.write_text(json.dumps(result, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
