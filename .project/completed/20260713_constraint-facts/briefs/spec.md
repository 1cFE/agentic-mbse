# Brief: Item 1 — Neutral Constraint Facts: Production Schemas and Extraction (spec stage)

You are one stage of the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously. Never pause for background agents, never schedule check-backs.
- Do NOT run `git commit` — the orchestrator commits. Leave files in the working tree.
- Artifact: `spec.md` in `.project/active/constraint-facts/`.

## Provenance of what you're given
- The concept (`~/1cfe/sysml-codegen/.project/concepts/constraint-execution-and-design-space-studies-claude.md`) is the owner-ratified design. Its Design Principles and Non-Goals are settled — do not relitigate (notably: silence is never an outcome; structure survives, reconstructed text does not; no invented tolerances).
- The S1 spike result and its review carry-forwards (concept Appendix B, S1 section + Next-Stage Handoff `[AGENT]` blocks) are verified agent-grade evidence — treat as binding inputs unless you find contradicting evidence, in which case surface it loudly in the spec rather than resolving silently.
- The epic item text below is the orchestrator's transmission of the epic plan (agent-grade, owner-approved epic).

## Intent
This item freezes the neutral fact vocabulary every other repo consumes (sysml-codegen lowering, snapshot v3, the executable profile). agentic-mbse owns neutral SysML semantics (PUSH-DOWN pattern); transformation policy stays downstream. The facts exist to fix a known limitation: today's type-level classification collapses membership kinds to "plain" and drops predicates entirely.

## Objective
Land `ConstraintDefinitionFact`, `ConstraintUsageFact`, and `ConstraintSource` as production, serializable schemas with live extraction, adopting S1's frozen fact shapes.

## Scope
1. **Schemas**: reusable predicate + formals with defaults + source identity (definition fact); exactly one `ConstraintSource` per usage fact — inline / definition-typed / named-usage-reference / satisfy — plus the two non-asserted catalog shapes S1 surfaced (requirement-owned require/assume; plain non-asserted usages as reference targets — the spec must pin both so neither falls between "assertion" and "authoring inventory"). Membership kind read from the owning membership; polarity; owner/scope; actuals with formal targets; omitted defaulted formals; inheritance/retyping facts; source location (anonymous-assertion identity).
2. **Extraction**: base `ConstraintUsage` subtype sweep (an `AssertConstraintUsage`-rooted sweep misses satisfy); definition formals by owner-filtered `AttributeUsage` enumeration (`ConstraintDefinition.parameters` omits them in SysIDE 0.8.4); **principled discriminators** — inline vs definition-typed by whether the usage owns a `result_expression`, never by namespace prefix; quantity dimensions resolved structurally, never by `Unit`-suffix stripping (S1 carry-forward (1) — both fixture-coupled heuristics are banned from production).
3. **Serialization + tests**: versioned JSON section shape (consumed downstream by sysml-codegen snapshot v3); golden tests re-anchored from S1's fixtures (committed at `tests/fixtures/constraint_fact_shapes/`, learning tests at `tests/test_sysml/test_constraint_fact_shapes.py`); S1's test-only capture module retired or clearly demoted to fixture tooling.

## Out of scope
- Eligibility decisions (Item 3 owns the executable profile); expression tree internals (Item 2 owns ExpressionIR — but coordinate: Item 2's feature-ref/literal field shapes adopt this item's fact vocabulary); any sysml-codegen consumption.

## Success criteria (from the epic)
- All six source-form classes from S1's golden matrix extract with production code; membership kind, polarity, ownership, actuals, defaults, and inheritance facts match S1's golden values.
- Neither fixture-coupled heuristic (namespace prefix, unit-suffix strip) appears in production code.
- Facts JSON round-trips byte-stably; schema carries a version.
- agentic-mbse suite green; Ruff clean.

## Required reading
1. Concept: "Neutral Constraint Facts — agentic-mbse" section + Appendix B S1 result and carry-forwards + Next-Stage Handoff S1 `[AGENT]` blocks.
2. `.project/active/spike-constraint-fact-shapes/findings.md` — §2 (fact shapes), §5 (access quirks).
3. Existing adapter: `agentic_mbse/sysml/syside_adapter.py` (subtype sweep + droppability live here today).
