"""Spike runner: prints what native_path.evaluate returns for each probe path (run with -s)."""

import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import native_path  # noqa: E402

PATHS = [
    "probe_native::host.load",
    "probe_native::host.doubled_load",
    "probe_native::host.doubled.r",
    "probe_native::host.pack_total",
    "probe_native::host.pack.total",
    "probe_native::host.pack.cell_count",
    "probe_native::host.load_positive",
    "probe_native::host.load_negative",
]


def test_print_native_values() -> None:
    files = [str(p) for p in (HERE / "model").rglob("*.sysml")]
    model, _ = native_path.syside.load_model(files)
    for p in PATHS:
        try:
            print(p, "->", native_path.evaluate(model, p))
        except Exception as e:  # noqa: BLE001
            print(p, "-> ERROR", type(e).__name__, e)
