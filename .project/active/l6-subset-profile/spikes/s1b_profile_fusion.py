"""Spike S1b: where does extract_subset_facts spend its time on fusion-tea f96ad312?

    uv run python .project/active/l6-subset-profile/spikes/s1b_profile_fusion.py

Throwaway. Exports the tree, loads it, and runs extract_subset_facts under cProfile; prints the
top functions by cumulative time inside agentic_mbse.
"""

from __future__ import annotations

import cProfile
import pstats
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from s1_trees import TREES, export  # noqa: E402

from agentic_mbse.sysml.subset_extraction import extract_subset_facts  # noqa: E402
from agentic_mbse.sysml.syside_adapter import SysideAdapter  # noqa: E402

label, repo, rev = TREES[0]
with tempfile.TemporaryDirectory(dir="/tmp", prefix="l6-spike-s1b-") as tmp:
    tree = Path(tmp) / label
    export(repo, rev, tree)
    model, _ = SysideAdapter.load_model(sorted((tree / "models").rglob("*.sysml")))
    profiler = cProfile.Profile()
    profiler.enable()
    extract_subset_facts(model)
    profiler.disable()
stats = pstats.Stats(profiler).sort_stats("cumulative")
stats.print_stats(r"agentic_mbse", 35)
