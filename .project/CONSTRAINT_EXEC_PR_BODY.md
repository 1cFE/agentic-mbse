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

## Evidence

- Every item audit-certified with orchestrator-executed probes; independent findings audit
  (owner session, 2026-07-13) re-ran the final gates to exact counts.
- Suite: **1401 passed / 1 skipped**. ruff: 1 pre-existing N806 (identical on `main`).
  mypy: 106 errors (`main` has 107 — net improvement).
- Item artifacts archived under `.project/completed/20260713_{constraint-facts,expression-ir,executable-profile}/`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
