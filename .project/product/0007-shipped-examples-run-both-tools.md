---
id: 0007
title: Every complete SysML example in the shipped guidance is executed against validate and sysml-codegen check, and does what its text says
date: 2026-10-23
owner: Reid Westwood
status: active
amended_by: []
superseded_by: null
supersedes: null
provenance: "[OWNER] (goal, Reid, 2026-10-23); this summary is agent-written"
surfaces: [skills, agents, docs/patterns, project_templates, validate, sysml-codegen check]
checked: 2026-10-23
---

## Promise

Every SysML example shipped to target repos (`docs/`, `skills/`, `agents/`, `project_templates/`) that parses on its own or in the standard wrapper is marked `@tool-example` and run through `agentic-mbse validate` and `sysml-codegen check`. A plain example passes both; a wrong-way example (`fails="CODE"`) fails with the code it names. A new complete example without a marker fails the test.

## Authority

- [OWNER] Reid, 2026-10-23, goal 2 as relayed by the coordinating agent: "the shipped guidance teaches what the tools actually do", done when a test runs every complete example through both tools. agentic-mbse is the front half of a model-to-code pipeline, so the generator's limits count as core rules.

## Evidence

- `tests/test_validation/test_tool_examples.py`. The check half runs `sysml-codegen` as a subprocess (`SYSML_CODEGEN` or PATH) and skips when it is absent.

## Scope

A `defect="CODE"` marker pins a correct example that validate wrongly rejects (one today: the `redefines` rename in `docs/patterns/semantic-hazards.md`, reported `UNBOUND_INPUT`).
