"""Orchestrator probe for Item 1 design MF4: structural dimension traversal.

Question: for a quantity feature typed only by dimension (LengthValue), does the
structural path via the value type's mRef member reach the measurement-unit
definition (LengthUnit) — and for an exact-unit feature (e.g. initialized with
[SI::m] / declared with a unit), does the unit referent's type reach the same?
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import syside

MODEL = """
package DimProbe {
    import ISQ::*;
    import SI::*;
    part def Thing {
        attribute dim_only : LengthValue;
        attribute with_unit : LengthValue = 5.0 [m];
    }
}
"""


def type_names(feature) -> list[str]:
    return [getattr(t, "qualified_name", None) or str(t) for t in feature.types]


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "dim_probe.sysml"
        p.write_text(MODEL)
        model, _diag = syside.try_load_model([str(p)])
        for attr in model.elements(syside.AttributeUsage, include_subtypes=True):
            owner = getattr(getattr(attr, "owner", None), "declared_name", None)
            if owner != "Thing":
                continue
            print(f"\n=== {attr.declared_name} ===")
            print(f"  declared types: {type_names(attr)}")
            for t in attr.types:
                tqn = getattr(t, "qualified_name", "?")
                print(f"  walking type {tqn}")
                for m in getattr(t, "members", []):
                    name = getattr(m, "declared_name", None) or getattr(m, "name", None)
                    if name and "mRef" in str(name):
                        mtypes = [
                            getattr(mt, "qualified_name", str(mt))
                            for mt in getattr(m, "types", [])
                        ]
                        print(f"    member {name}: types={mtypes}")
            fv = getattr(attr, "feature_value_expression", None)
            if fv is not None:
                print(f"  feature_value_expression: {type(fv).__name__}")
                for child in getattr(fv, "children", []) or []:
                    cn = type(child).__name__
                    ref = getattr(child, "referent", None)
                    if ref is not None:
                        rt = [
                            getattr(t, "qualified_name", str(t))
                            for t in getattr(ref, "types", [])
                        ]
                        print(
                            f"    child {cn} referent="
                            f"{getattr(ref, 'declared_name', None)} types={rt}"
                        )


if __name__ == "__main__":
    main()
