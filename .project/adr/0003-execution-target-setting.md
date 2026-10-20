---
id: 0003
title: Each target project declares execution-target in its pyproject.toml; the target sets how loud generator findings are, and only a real inspection failure fails a run regardless of target
date: 2026-10-20
owner: Reid Westwood
status: active
amended_by: []
superseded_by: null
provenance: "[AGENT] (ratified by owner 2026-10-18; gate outcomes and audit decisions delegated by owner 2026-10-18)"
seams: [l6, validate-cli, init, target-projects, research-holdout-guard]
supersedes: null
promoted_to: null
---

## Decision

A target project declares `[tool.agentic-mbse] execution-target = "generated" | "native"` in the `pyproject.toml` at the root that `find_project_root` finds; `validate --execution-target` overrides it for one run. The target only changes display severity, through one pure table (`src/agentic_mbse/validation/execution_target.py`): unset shows generator findings as warnings and never labels a model generated-ready, `native` folds generator-only findings into an INFO summary, `generated` makes confirmed refusals errors while exclusions and omissions stay warnings. Check and setting failures (malformed TOML, unknown value or key, a crash, a failed inspection) are errors under every target; a shared walker's own deliberate refusal inside a legacy check is the `L6_CHECK_UNVERIFIED` WARNING, not a check failure.

## Why

- The setting is committed, so the owner, teammates and CI get the same result. An environment variable was rejected because it differs per machine (owner, 2026-10-18).
- Unset must not make a passing project fail, and native projects must not be buried in generator noise or left with generator-only errors (epic Item 3 scope 3 and 4).
- A crash or failed inspection that passes would let a broken check read as a clean model, so it fails everywhere (gate R3-2, delegated).
- A walker refusing a shape on purpose (e.g. a non-`sum` call, ES-005) is "could not decide", not a crash. Treating it as `L6_CHECK_ERROR` failed models that pass today, including native ones, for a generator-only reason (audit B1). Under `generated` the contract's own refusal still fails the same site, so nothing is relaxed.
- `init` writes the line byte-preservingly and refuses to create a `pyproject.toml` under a parent one, because the new file would split the folder off from the parent's uv environment (audit impl-F2).

## Invariants established

1. The settings key set is closed and shared with the research holdout guard (`src/agentic_mbse/project_settings.py`); any defect is an error, never "unset".
2. No target makes an inspection failure pass or hides it in the native summary.
3. Under `native`, only the four legacy codes with a shown generator-only cause are lowered to INFO; every other code keeps its own severity.
4. The target never changes an outcome, only how it is shown.

## Rejected alternatives

- An environment variable for the target: not chosen, because results would differ per machine.
- `L6_CHECK_ERROR` for every walker exception: rejected because it fails valid models over a deliberate subset refusal (design D15, audit B1).
- Never creating `pyproject.toml` in `init`: not chosen; a standalone folder takes no harm, and `init` says uv will treat it as its own project.

Evidence: `.project/completed/20261020_l6-subset-profile/briefs/align.md` (owner decisions, gate outcomes, audit decisions), `design.md`, `audit.md`, `evidence/legacy-l6-audit.md`, `evidence/before-after.md`.
