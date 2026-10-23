---
id: 0006
title: validate L6 never says whether a model generates and holds no copy of a generator check; execution-target changes no result, and a broken check or setting fails under every target
date: 2026-10-23
owner: Reid Westwood
status: active
amended_by: []
superseded_by: null
supersedes: null
provenance: "[OWNER] (goal, Reid, 2026-10-23); this summary is agent-written"
surfaces: [validate L2, validate L6, validate --execution-target, init --execution-target, validate --json-report]
checked: 2026-10-23
---

## Promise

`agentic-mbse validate` checks only what holds for any SysML model and the project's own conventions (ADR-002, manifests, design-attribute completeness). It holds no copy of a generator check and makes no claim about whether the generator will build the model; `sysml-codegen check` answers that. `execution-target` changes no result under any target; `generated` tells the workflow to run `sysml-codegen check`. A broken check or an invalid setting (`L6_SETTING_INVALID`) is an error under every target.

## Authority

- [OWNER] Reid, 2026-10-23: "each check lives in one repo". Recorded in `.project/adr/0006-each-check-lives-in-one-repo.md`, which amends ADR 0004 and ADR 0005.

## Evidence

- `tests/test_validation/test_no_generator_copies.py` fails if a validation module cites a generator diagnostic, rule or commit.
