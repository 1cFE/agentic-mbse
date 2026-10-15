"""Negative controls: deliberately wrong ports. The comparison must flag each one.

Usage: python -I mutants.py MUTANT OUT.json MODEL_PATH [...]
  declared_multiplicity  read `declared_multiplicity` (the prototype's attribute) not `multiplicity`
  no_effective_decl      keep every redefinition candidate as a child (skip effective-declaration)
  writer_is_base         every scope classifies the slot's base calc usage (spec's literal reading)
  typed_anywhere         a part def "has occurrences" if any user usage is typed by it (prototype)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import occurrence_port as P  # noqa: E402
import port_run  # noqa: E402

mutant = sys.argv.pop(1)

if mutant == "declared_multiplicity":
    original = P.OccurrenceStructure.reading

    def reading(self, usage, parent):
        class View:
            def __getattr__(_s, name):
                if name == "multiplicity":
                    return getattr(usage, "declared_multiplicity", None)
                return getattr(usage, name)

        return original(self, View(), parent)

    P.OccurrenceStructure.reading = reading

elif mutant == "no_effective_decl":
    P.SlotIndex.effective_declaration = lambda self, candidates: max(candidates)

elif mutant == "writer_is_base":
    P.OccurrenceStructure.select_writer = lambda self, base, candidates, scope: base

elif mutant == "typed_anywhere":
    original_run = port_run.run

    def run(model):
        out = original_run(model)
        typed = set()
        for usage in P.SysideAdapter.elements_of_type(model, "PartUsage"):
            for t in getattr(usage, "types", None) or ():
                if P.qn(t) is not None:
                    typed.add(str(P.decl(t)))
        out["def_occurrences"] = {d: (1 if d in typed else 0) for d in out.get("def_occurrences", {})}
        return out

    port_run.run = run
else:
    raise SystemExit(f"unknown mutant {mutant}")

sys.exit(port_run.main())
