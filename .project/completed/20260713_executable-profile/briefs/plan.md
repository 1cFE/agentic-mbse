# Brief: Item 3 plan — Executable Profile

You are the plan stage for Item 3 in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- **NEVER run `pytest tests/ -m ""` or `test_corpus_integration.py`** [OWNER instruction]. Gate = default suite.
- Artifact: `plan.md` in `.project/active/executable-profile/`.

## Input
Design rev 2 (committed): `.project/active/executable-profile/design.md` — D1–D9, two-arm same-IR seam, absence-case default-deny, REASON_CODES, L4/L6 replacement surfaces are authoritative.

## Planning guidance (orchestrator, agent-grade)
- Implement runs on sonnet: mechanical phases, exact files, per-phase `uv run pytest` gates (default suite).
- Sequence: profile module + types + golden-table tests first (pure, offline); then L4/L6 replacement (with the deletion surface as named); then the cross-repo preflight seam. The sysml-codegen wiring commit is part of this item — plan it as its own phase with its own gates (the orchestrator will sequence the actual sysml-codegen commit to avoid tree conflicts; write the exact change as a ready-to-apply description + tests).
- The 14 golden equality rows + 2 new inequality rows + absence cases + default-deny fall-throughs each need a named test.
- Final gates: default suite green, ruff clean, license-free proof (profile tests run without syside import — structural check per the design).
- Keep phases resumable from checkboxes.
