# Spike S1: does one generic function evaluate a named output natively?

**Status:** written during design 2026-10-22, **not run** (the design session had no permission to run commands). Run it first in plan or implement.

**Question.** Can SysIDE's `Compiler.evaluate_feature` return the native value of an output named only by its path (`<package>::<part usage>.<feature>...`), with no model-specific wrapper, for the shapes a target model uses: an attribute, an inherited attribute, a calc usage's result, an attribute bound to a calc result, a nested part's attribute, a `sum` over an exact part multiplicity, and an assert constraint usage?

**Why it matters.** The design's native half (design D1) rests on it. If a path needs model-specific scoping or inputs, the comparison command needs a per-model adapter and the design falls back to option (c).

**Run (repo root):**

```bash
uv run pytest .project/active/generated-results-guidance/spike/native-path/test_native_path.py -s -q
```

**Expected if the bet holds:** `host.load` 3.0, `host.doubled_load` 6.0, `host.doubled.r` 6.0, `host.pack_total` 7.5, `host.pack.total` 7.5, `host.pack.cell_count` 3, each with no diagnostics. The two constraint paths (`load_positive`, `load_negative`) are a side question: if they evaluate to `True` / `False`, native verdicts can be compared too; if they error or return `None`, native verdicts stay out of scope (dc3 evaluated constraints itself, `scripts/models/evaluate_paths.py:97-100`).

**Record:** paste the output below with the SysIDE version and date, then update design bet B1.

**Recorded 2026-10-22 (SysIDE 0.8.4):** ran; see [../RESULTS.md](../RESULTS.md) § S1. Attributes, inherited attributes, calc results and nested parts gave the expected values. `pack_total` and `pack.total` gave 2.5, not 7.5, because the evaluator does not expand `Cell[n]`. The constraint paths returned the usage object; evaluating the constraint's result expression with the usage as scope gives True / False.
