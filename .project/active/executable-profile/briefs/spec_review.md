# Brief: Item 3 spec review — Executable Profile

You are a fresh review session in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`. You did not write this spec; review it adversarially.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- **NEVER run `pytest tests/ -m ""` or `test_corpus_integration.py`** [OWNER instruction]. Gate = default suite.
- Artifact: `spec-review.md` in `.project/active/executable-profile/`.

## Review target
`.project/active/executable-profile/spec.md` (brief at `briefs/spec.md`).

## Ground truth
Concept (`.project/reference/constraint-execution-concept.md`): executable-profile paragraph, Non-Goals, S1/S2 carry-forwards. S1 golden matrix: `tests/fixtures/constraint_fact_shapes/golden.json` (equality_cases + decision fields — Item 3 is where those decisions now become production). Landed fact/IR types: `expression_facts.py`, `expression_ir.py`, `constraint_facts.py`. Current L4/L6: `agentic_mbse/validation/` (find the exact placeholder and blanket-warning sites). The epic's Item 3.

## What to probe hardest
1. **Matrix totality.** For every node kind × operand-fact combination the landed IR can produce, does the spec's decision procedure give exactly one outcome (admit / block-with-named-diagnostic / not-applicable)? Walk the 14 golden equality rows against the spec's gate and check each maps; check the two new inequality-unit pins are precisely stated (what fact pattern triggers them).
2. **The dimension-known-unit-unknown state.** Item 1 deliberately extracts this state (LengthValue-typed, no exact unit). Does the spec block it in every unit-sensitive position (equality AND inequality AND arithmetic), per the S1 carry-forward? What about dimensionless-vs-dimensioned mixes?
3. **Profile-strictly-precedes-compilation.** Is the ordering enforceable as specified (a structural guarantee at the preflight seam, not a convention), per S2 carry-forward (2)?
4. **The severity recommendation.** Loud-but-non-failing WARNING at the advisory seam: check it against the concept's "runs both at design review and at codegen preflight" and the epic's success criteria. Would any existing target-repo model start failing? Is the recommendation genuinely lossless to flip?
5. **Cross-repo seam.** The sysml-codegen preflight hook: is its contract specified precisely enough (input: whose facts? output: what halts generation? version pinning per coordinated-pair discipline) that the sysml-codegen wiring change is mechanical?
6. **Unused-definitions-as-inventory and satisfy/require/assume cataloging**: consistent with Item 1's landed source forms and the concept's "never appears as unassessed" rule for unused defs?

Verdict format: must-fix list (each with why), nice-to-haves, overall verdict (Approved / Approved-with-must-fixes / Rework). Verify against fixtures and code — do not take the spec's word.
