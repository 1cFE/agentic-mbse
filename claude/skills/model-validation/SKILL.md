---
name: model-validation
description: >
  Use when choosing model checks, running the six-level validator, interpreting
  diagnostics, or assessing regression, source, numerical, and integration evidence.
allowed-tools: Read, Grep, Glob, Bash
user-invocable: false
---

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
| 6 — Architecture/readiness | Supported patterns and downstream execution readiness |

These checks do not establish source fidelity or sufficient engineering coverage. Interpret each diagnostic's severity and applicability; retain the actual exit status. L1–L3 errors normally block valid execution, and relevant L6 failures can block a required downstream route. A documented project-specific exception needs applicable evidence, not blanket dismissal of a level or an unchanged issue count.

## Run the Relevant Checks

Follow the project's environment instructions and **toolkit-awareness** guidance:

```bash
uv run agentic-mbse validate models/             # fail-fast default
uv run agentic-mbse validate --complete models/  # report all six levels
uv run agentic-mbse validate --level=3 models/   # focused level
uv run pytest tests/models/ -v                  # model regressions, if present
```

Use the model scope and test selection appropriate to the change. During editing or a prototype, run the checks that answer the immediate question. Before completion, assess all applicable levels and integrated regressions. After repair, rerun the affected checks; broaden when new changes or failures justify it.

## Evidence Beyond Parsing

Select evidence according to the claim:

- Source values: inspect the authoritative table, image, or code branch when needed; separate transcription, derivation, and assumption.
- Numerical behavior: use an independent identity/reference and relevant boundary or counterexample cases. Choose tolerances from the quantities and numerical risk; small percentages are not universally acceptable.
- Structure and behavior: check ownership, physical relationships, operating assumptions, and agreement with analytical bindings where relevant.
- Public consumers: change a supported input through its normal route and check intended downstream effects, including what should remain unchanged.
- Translation: compare generated and manual execution, while recognizing that shared formulas can share an error.

Write kept tests for meaningful regressions where practical. A definition-existence test verifies existence, not its physical role; a mirror test verifies agreement, not independent correctness. Avoid tests whose only expectation is the current implementation's graph or output.

Model tests normally live in `tests/models/`. When a project uses `codegen_available` for downstream tests, preserve that convention and report skips as unverified. An unavailable pipeline cannot supply a positive completion result for required executable behavior.

## Record the Result

Report examined revision and model scope, commands/environment, actual results, and evidence paths. Link checks to the applicable requirements or findings. Distinguish new failures, inherited issues, skips, and checks not run; compare issue identities when claiming an unchanged failing baseline.

Keep source, translation, numerical, engineering, and consumer claims distinct where relevant. Record known limitations and their effect on permitted use. A positive assessment requires evidence for the scoped outcome, not just a green aggregate label. Reuse current evidence with its original scope and provenance rather than rerunning or recopying it automatically.
