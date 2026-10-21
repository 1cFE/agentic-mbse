---
name: model-validation
description: >
  Use when choosing model checks, running the six-level validator, interpreting
  diagnostics, or assessing regression, source, numerical, and integration evidence.
allowed-tools: Read, Grep, Glob, Bash
user-invocable: false
metadata:
  kind: supporting
---

Before executing this skill, read `.agentic-mbse/claude.md` in Claude Code or `.agentic-mbse/codex.md` in Codex. Resolve supporting paths from this skill’s installed directory; keep generated outputs in the project or a temporary directory. Read referenced skills from `.agents/skills/<name>/SKILL.md` when their guidance is needed.


# Model Validation

Choose checks for the promised behavior and its actual risks. Validate early enough to catch useful failures, then validate the integrated outcome. The number of phases or model elements does not determine the strength of the evidence.

## Tool Checks and Their Limits

| Level | What the tool examines |
|---|---|
| 1 — Syntax | Parser diagnostics |
| 2 — Structural completeness | Definitions, inputs, and bindings |
| 3 — Dependency integrity | Dependency cycles |
| 4 — Constraint coverage | Authored constraints and executable coverage |
| 5 — Documentation | Documentation presence |
| 6 — Architecture & Generator Subset | ADR-002 rules, manifests, and the generator subset profile (`subset-profile/v2`); not a generation check |

Level 6's subset profile has nine implemented rules, each traced to sysml-codegen's source or to a conformance case run against it: binding sources, calculation-owned constraints, conditional expressions, constraint predicates, indexed references, unsupported function calls, part multiplicities, dropped String values and dropped calculation-usage result expressions. It is incomplete: the `Coverage limit` line names the generator refusals with no rule yet, and a clear verdict says nothing about them. It is not a generation check and never runs the generator; the generation answer comes from `sysml-codegen check`, below. `[tool.agentic-mbse] execution-target` in `pyproject.toml` (`generated` or `native`, set by `agentic-mbse init --execution-target`) decides how loud the findings are; unset shows refusals as warnings and reports "generated compatibility not established". Report that note as it stands; do not read a passing L6 as evidence the generator will build the model.

These checks do not establish source fidelity or sufficient engineering coverage. Interpret each diagnostic's severity and applicability; retain the actual exit status. L1–L3 errors normally block valid execution, and relevant L6 failures can block a required downstream route. A documented project-specific exception needs applicable evidence, not blanket dismissal of a level or an unchanged issue count.

## Run the Relevant Checks

Follow the project's environment instructions and **toolkit-awareness** guidance:

```bash
uv run agentic-mbse validate models/             # fail-fast default
uv run agentic-mbse validate --complete models/  # report all six levels
uv run agentic-mbse validate --level=3 models/   # focused level
uv run pytest tests/models/ -v                  # model regressions, if present
uv run sysml-codegen check --models models/      # generation answer, when the project targets generated code
```

Use the model scope and test selection appropriate to the change. During editing or a prototype, run the checks that answer the immediate question. Before completion, assess all applicable levels and integrated regressions. After repair, rerun the affected checks; broaden when new changes or failures justify it.

## The Generation Check

When the project targets generated code (`execution-target = "generated"`), `sysml-codegen check` is the only answer to whether the model generates. It works out what `generate` would do and writes nothing. Exit 0: `generate` would build the model. Exit 1: it would refuse, or the environment failed; the output gives the reason. Exit 2: a usage error, or `uv` could not find `sysml-codegen`.

Run it as soon as the first model pieces exist, at each phase, and before any claim that the model generates. Record the exit code and reason line. A project that has parked generation runs it once early and records the result without blocking. If sysml-codegen is unavailable, report generation as not checked, never as fine. When and why: “Generated code” in `modeling_project/MODELING_PROCESS.md`.

## Evidence Beyond Parsing

Select evidence according to the claim:

- Source values: inspect the authoritative table, image, or code branch when needed; separate transcription, derivation, and assumption.
- Numerical behavior: use an independent identity/reference and relevant boundary or counterexample cases. Choose tolerances from the quantities and numerical risk; small percentages are not universally acceptable.
- Structure and behavior: check ownership, physical relationships, operating assumptions, and agreement with analytical bindings where relevant.
- Public consumers: change a supported input through its normal route and check intended downstream effects, including what should remain unchanged.
- Design choices: where the design-choice row of the technical-pattern table in `modeling_project/MODELING_PROCESS.md` applies, check the actual bindings against `design-choices.md` and run its acceptance checks.
- Translation: compare generated and manual execution, while recognizing that shared formulas can share an error.

Write kept tests for meaningful regressions where practical. A definition-existence test verifies existence, not its physical role; a mirror test verifies agreement, not independent correctness. Avoid tests whose only expectation is the current implementation's graph or output.

Model tests normally live in `tests/models/`. When a project uses `codegen_available` for downstream tests, preserve that convention and report skips as unverified. An unavailable pipeline cannot supply a positive completion result for required executable behavior.

## Record the Result

Report examined revision and model scope, commands/environment, actual results, and evidence paths. Link checks to the applicable requirements or findings. Distinguish new failures, inherited issues, skips, and checks not run; compare issue identities when claiming an unchanged failing baseline.

Keep source, translation, numerical, engineering, and consumer claims distinct where relevant. Record known limitations and their effect on permitted use. A positive assessment requires evidence for the scoped outcome, not just a green aggregate label. Reuse current evidence with its original scope and provenance rather than rerunning or recopying it automatically.
