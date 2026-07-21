# CONSTRAINT-EXEC: neutral constraint facts, ExpressionIR, executable profile (Items 1–3)

**⚠️ Merge order: this PR merges FIRST.** sysml-codegen's `constraint-exec-epic` PR imports the
symbols added here (coordinated pair); merging that one before this breaks its `main`. teax's PR
is independent; fusion-tea's `main` push comes last.

## What this delivers

The agentic-mbse third of the CONSTRAINT-EXEC epic — modeled `assert constraint` executing as
generated graph modules (canonical epic + close-out archived in sysml-codegen
`.project/completed/20260713_epic_constraint_execution*.md`):

- **Item 1 — Neutral constraint facts.** Production `ConstraintFacts` schemas and extraction:
  constraint usages, owning-definition facts, location facts, membership kinds — the neutral
  substrate sysml-codegen's lowering consumes.
- **Item 2 — ExpressionIR.** The production expression tree with syside extraction and
  serialization; one IR serves constraint predicates and calc expressions byte-identically
  (sysml-codegen's Item 13 retired `ExpressionAST` onto it).
- **Item 3 — Executable profile.** Eligibility gates + named diagnostics: every supported
  assertion shape lowers; unsupported constructs block generation with a named diagnostic,
  never silence.

## Post-review remediation (2026-07-14)

A critical code-quality audit (`.project/research/20260714-064234_constraint-exec-pr-code-quality-audit.md`)
found nine defects; an independent four-agent verification confirmed all nine, and every fix
landed on this branch (plan + per-phase notes:
`.project/active/constraint-exec-remediation/plan.md`):

- **F1 (High, was the merge blocker):** the unit-safety gate now runs at every arithmetic
  node. Interior arithmetic facts are *derived* from operand facts, never trusted from the
  declared fact; mixed-unit arithmetic blocks with `block_unit_conversion_required`. Scalar
  scaling and same-unit ratios are provable and admit; derived/inverse units block with the
  new `block_derived_unit_unsupported`. `PROFILE_SEMANTIC_VERSION` → `executable-profile/v2`.
- **F3:** malformed snapshot facts now yield `block_malformed_operand_fact` instead of
  crashing an assert; the append-then-measure walk replaced by typed value results; the two
  mypy `union-attr` errors are gone (four pure modules + extraction now mypy-clean).
  A residual audit probe (zero-operand `and` admitted vacuously) closed with a connective
  arity gate.
- **F4:** the L4 eligibility block reports its own denominator
  (`Constraint usages assessed (incl. satisfy)`), so categories reconcile by construction;
  the legacy Item-4 `Total constraints` semantics are unchanged.
- **F2/F8:** the wire codec fails closed — foreign `schema_version` (envelope or node) raises
  a `ValueError` naming found vs supported instead of silently rewriting to v1; `kind`/
  `schema_version` are non-init; `constraint_facts` consumes only public codec names.
- **F9:** canonical constraint ordering gained `(file, column)` tie-breakers — two-file
  anonymous assertions now serialize byte-stably regardless of load order
  (`production_facts.json` bytes unchanged).
- **F5:** `extract_expression_ir` gained an optional `diagnostics` sink (signature stays
  call-compatible for sysml-codegen).
- **F6/F7:** the fact-shapes spike archived with a close-out note (`golden.json` is the
  frozen S1 oracle; `production_facts.json` is the regenerable golden); `sysml/__init__.py`
  derives `__all__` from the lazy registry with an export-consistency test (372 → 276 lines).

A fresh certification pass on 2026-07-17 found and closed three final wire-boundary gaps:

- malformed literal, feature-reference, and unit-annotation leaves now survive the public
  facts codec and reach D-R3's named `block_malformed_operand_fact` profile decision;
- serializers reject post-construction mutation of every ExpressionIR `kind` /
  `schema_version`, the facts envelope version, and nested IR tags;
- `constraint_extraction.__all__` now includes the public `extract_expression_ir` API.

The rerun certifies the local remediation at
`.project/active/constraint-exec-remediation/audit.md`.

Deferred by decision: barrel `parse`/`serialize` rename (coordinated cross-repo change) and
L4/L6 duplicate extraction (design-accepted pending profiling).

## Evidence

- Every item audit-certified with orchestrator-executed probes; independent findings audit
  (owner session, 2026-07-13) re-ran the final gates to exact counts.
- Latest normal suite: **1484 passed / 1 skipped / 33 deselected**. The prior remediation
  all-markers run passed **1496 / 1** before the final wire-boundary cures; paid Claude-budget
  cases were not rerun after those cures. Focused final set: **92 passed**. Targeted mypy over
  the five constraint-exec modules and Ruff over the final touched files are clean.
- Item artifacts archived under `.project/completed/20260713_{constraint-facts,expression-ir,executable-profile}/`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
