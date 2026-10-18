"""The committed fusion-tea pin list is exactly what the builder makes from the prototype log.

Spec Base-1, design Appendix B "Reference file". The pin list is generated only by
`scripts/positional_binding/build_reference.py`, from `04-detector-tree-fusion-tea.log` alone
(design I3); this test re-runs the builder and compares bytes.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

from agentic_mbse.validation.positional_pins import PinList, load

REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "scripts" / "positional_binding" / "build_reference.py"
PROTOTYPE_LOG = (
    REPO / ".project/concepts/convince-me-exec-subset/evidence/04-detector-tree-fusion-tea.log"
)
BASELINE = REPO / "tests/fixtures/positional_binding/baselines/fusion-tea-f96ad312.toml"


def builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("build_reference", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # dataclasses look their module up while being built
    spec.loader.exec_module(module)
    return module


def test_reference_builder_reproduces_the_committed_pin_list(tmp_path: Path) -> None:
    out = tmp_path / "fusion-tea-f96ad312.toml"
    builder().build_reference(PROTOTYPE_LOG, out)
    assert out.read_bytes() == BASELINE.read_bytes()


def test_the_committed_pin_list_has_125_distinct_identities_in_9_files(tmp_path: Path) -> None:
    pins = load(BASELINE, pin_root=tmp_path)
    assert isinstance(pins, PinList), pins
    assert len(pins.pins) == 125
    assert len({p.identity for p in pins.pins}) == 125
    assert len({p.file for p in pins.pins}) == 9
    assert pins.revision == "f96ad312c63e8c66695971b12feab971f3ba6eb3"
    assert pins.recorded.isoformat() == "2026-10-15"
    assert all(p.file.parts[0] == "models" for p in pins.pins)


def test_a_quoted_target_keeps_its_inner_quotes(tmp_path: Path) -> None:
    pins = load(BASELINE, pin_root=tmp_path)
    assert isinstance(pins, PinList)
    targets = {p.identity.target for p in pins.pins}
    assert (
        "integrated_heat_electricity::'Network Heat Driven Closure'::divertor_available_in"
        in targets
    )


def test_the_builder_rejects_a_log_whose_input_name_disagrees(tmp_path: Path) -> None:
    log = tmp_path / "bad.log"
    log.write_text(
        "  L2_POSITIONAL_BINDING  //designs/x.sysml:3  P::q::c::b\n"
        "      input 'a' implicitly redefines 'P::Sub::a' by position; write ...\n"
    )
    module = builder()
    try:
        module.parse_log(log)
    except module.LogFormatError as error:
        assert "P::q::c::b" in str(error)
    else:
        raise AssertionError("a mismatched declared name must be rejected")
