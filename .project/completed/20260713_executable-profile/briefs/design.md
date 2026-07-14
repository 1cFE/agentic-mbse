# Brief: Item 3 design — Executable Profile

You are the design stage for Item 3 in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- **NEVER run `pytest tests/ -m ""` or `test_corpus_integration.py`** [OWNER instruction]. Gate = default suite.
- Artifact: `design.md` in `.project/active/executable-profile/`.

## Input
- Spec (committed, review-revised): `.project/active/executable-profile/spec.md` — the ordered three-layer procedure, default-deny, body-vs-actuals rule, reason-grade diagnostics, same-IR guarantee, WARNING severity decision are fixed.
- Landed inputs: `expression_facts.py`, `expression_ir.py`, `constraint_facts.py` (certified). L4/L6 sites in `agentic_mbse/validation/`.
- S1 golden matrix + decision fields: `tests/fixtures/constraint_fact_shapes/golden.json` — Item 3 is where those decision fields become production truth (Item 1 deliberately excluded them).

## Design guidance (orchestrator, agent-grade)
- Decide and record: profile module placement + API (a pure function over ConstraintFacts → per-usage eligibility decisions with reason-grade diagnostics — decide the decision/diagnostic types), the two new inequality-unit golden fixtures' authoring, how the L4/L6 replacements consume the profile (and what exactly is deleted), the sysml-codegen preflight hook contract (this repo publishes; the wiring change in sysml-codegen is a separate small commit this item owns — design it here so implement is mechanical in both repos), and the same-IR seam assertion mechanism.
- The profile is pure data-in/decisions-out — no syside imports (it must run license-free over parsed facts). Make that a structural guarantee (import-hygiene test like Item 10's isolation pattern, if cheap).
- A skeptical design_review follows; make matrix-encoding choices explicit (table-driven vs code-branch) with rejected alternatives.
