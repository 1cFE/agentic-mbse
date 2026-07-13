# Brief: Item 1 design — Neutral Constraint Facts

You are the design stage for Item 1 in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `design.md` in `.project/active/constraint-facts/`.

## Input
- Spec (committed, review-revised, orchestrator-accepted): `.project/active/constraint-facts/spec.md`. Its `[HARD]` requirements are fixed; Open Questions are yours to decide and record.
- Spec review (what was contested): `.project/active/constraint-facts/spec-review.md`.
- Concept (readable in-repo): `.project/reference/constraint-execution-concept.md` — "Neutral Constraint Facts" section + Required Invariants.
- S1 ground truth: `.project/active/spike-constraint-fact-shapes/findings.md`, golden fixtures, kept tests, and the capture module the spec says to retire/demote.

## Design guidance (orchestrator, agent-grade)
- Follow the PUSH-DOWN shared-module pattern for placement: neutral semantics live in `agentic_mbse.sysml`; look at how existing shared modules (e.g. aggregation, expression) are laid out and mirror that idiom.
- Decide and record: schema technology (match what downstream consumers already deserialize — check how sysml-codegen consumes existing agentic-mbse types before choosing), version scheme + where the version lives, byte-stable canonical JSON mechanism (sort keys? separators? — make it a stated contract), extractor module shape, and the retire-vs-demote call for S1's capture module.
- Design the fact schemas so Item 2 (ExpressionIR) can adopt the feature-ref/literal leaf vocabulary without circular imports — name the intended import direction explicitly.
- Item 5 (sysml-codegen lowering) needs `owning_part_def_qn`-grade ownership facts; confirm `owner` + `inherited_into` shapes give it that (the spec's N2 note), and state the answer.
- A skeptical design_review follows; make extraction-order and dispatch choices explicit with rejected alternatives.
