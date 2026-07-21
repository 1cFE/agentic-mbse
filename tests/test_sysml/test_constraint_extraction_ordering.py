"""Canonical-order stability across model load order (F9 regression, live SysIDE).

Two anonymous assert constraints at the same line number in *different* files used to share
a sort key `(line, "")`, so serialized order — and therefore canonical bytes — depended on
the order files were passed to `try_load_model`. The extended key breaks the tie with file
path and column.
"""

from __future__ import annotations

from pathlib import Path

from agentic_mbse.sysml.constraint_extraction import extract_constraint_facts
from agentic_mbse.sysml.constraint_facts import serialize
from agentic_mbse.sysml.syside_adapter import get_syside

syside = get_syside()

# Both files put an anonymous assert on the same line number (line 3) so the old
# `(line, qualified_name or "")` key collides: anonymous asserts have no qualified name.
_FILE_A = """package OrderProbeA {
    part def ProbeA {
        assert constraint { 1 <= 2 }
    }
}
"""

_FILE_B = """package OrderProbeB {
    part def ProbeB {
        assert constraint { 3 <= 4 }
    }
}
"""


def _serialize_for(paths: list[str]) -> str:
    model, diagnostics = syside.try_load_model(paths)
    assert not list(diagnostics.all), list(diagnostics.all)
    return serialize(extract_constraint_facts(model))


def test_two_file_anonymous_asserts_serialize_identically_for_both_load_orders(
    tmp_path: Path,
) -> None:
    file_a = tmp_path / "order_probe_a.sysml"
    file_b = tmp_path / "order_probe_b.sysml"
    file_a.write_text(_FILE_A)
    file_b.write_text(_FILE_B)

    forward = _serialize_for([str(file_a), str(file_b)])
    reverse = _serialize_for([str(file_b), str(file_a)])

    assert forward == reverse
