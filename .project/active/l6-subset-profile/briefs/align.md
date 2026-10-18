# Orchestration Align record — EXEC-SUBSET-CONTRACT Item 3

**Date**: 2026-10-18
**Input**: `.project/backlog/epic_executable-subset-contract.md` Item 3
**Owner instruction**: "other PR is merged. please pull it locally, and then start item 3" (Item 4 merged as `ebb3d467`).

## Reading of the work

[AGENT] (ratified by owner, 2026-10-18) `agentic-mbse validate` tells a modeler up front whether the code generator will accept the model, using the Item 1 contract, instead of the modeler finding out only by running the generator. Projects that only run natively must not be buried in generator noise, so each project declares its execution target.

## Owner decisions (2026-10-18)

The owner approved these after a plain-language walkthrough ("yes, good"). They resolve epic open decision 2.

- [AGENT] (ratified by owner, 2026-10-18) **The setting lives in the project file**: `[tool.agentic-mbse] execution-target = "generated" | "native"` in the target project's `pyproject.toml`. It is committed, so the owner, teammates and CI get the same result. An environment variable was considered and rejected for that reason: it differs per machine.
- [AGENT] (ratified by owner, 2026-10-18) **Unset (the default) shows generator findings as warnings**, with a note naming the setting. Nothing that passes today starts failing. Unset never labels a model generated-ready.
- [AGENT] (ratified by owner, 2026-10-18) **`native` turns generator-only findings into an info summary; `generated` makes confirmed refusals errors.**
- [AGENT] (ratified by owner, 2026-10-18) **A one-run command-line override**, e.g. `validate --execution-target=native`, takes precedence over the file for that run.
- [AGENT] (ratified by owner, 2026-10-18) **Under `generated`, exclusions (non-numerical predicates) and omissions (dropped String values) are warnings with their own reasons**, not errors. Neither changes a generated number; String policy itself is still open in Item 2.

## Route

[AGENT] spec → spec_review → design → design_review → plan → implement → audit → close → pre_pr and PR. Branch `l6-subset-profile` off `main` at `ebb3d467`. sysml-codegen, dc3 and fusion-tea are read-only.

## Gates

- **Owner boundary (2026-10-18):** "I am working with another agent on item 2, so do not touch that." No sysml-codegen writes; no Item 2 artifacts; describe `sysml-codegen check` only as the future boundary.
- **R3-1 (reserved to owner):** any change that makes an L6 result that errors today stop erroring for a project whose target is unset or `generated` (relaxing an existing check). The audit of existing L6 checks may replace duplicates with shared decisions, but a net relaxation goes to the owner.
- **R3-2 (reserved to owner):** any change that makes a project which passes `validate` today fail it with the target unset.
- Check and configuration failures (malformed TOML, unknown target value, inspection failures) are errors regardless of target (epic Item 3 scope 3). That is inherited, not a gate.
- Premise surprise rule applies.
