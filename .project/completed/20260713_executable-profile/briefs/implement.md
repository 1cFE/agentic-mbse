# Brief: Item 3 implement — Executable Profile

You are the implement stage for Item 3 in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents or schedule check-backs.
- You ARE allowed to commit in this repo — you are the only session writing to this tree. Commit at each completed plan phase; check off plan.md checkboxes with implementation notes. End commit messages with: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Do NOT touch `.project/` outside `.project/active/executable-profile/`. Do NOT commit `uv.lock`.
- **NEVER run `pytest tests/ -m ""` or `test_corpus_integration.py`** [OWNER instruction]. All gates use the default suite.

## Input — execute the plan
`.project/active/executable-profile/plan.md` (Phases 1–4) is authoritative; `design.md` rev 2 holds D1–D9, REASON_CODES, the two-arm same-IR seam, and the L4/L6 surfaces.

## Phase 4 scoping (orchestrator)
Phase 4 (sysml-codegen wiring) is a READY-TO-APPLY BRIEF, not code you write in that repo — another implement session owns the sysml-codegen tree right now. Write the brief exactly as the plan specifies (file, change, tests, two-arm assertion, version pin) into `.project/active/executable-profile/sysml-codegen-wiring.md`; the orchestrator will apply and gate it in sysml-codegen afterward.

## Quality bar
- The 14+2 golden rows are the item's heart: parametrized tests, ids = case names, every row's reason code asserted.
- The WARN-flip hazard the plan flagged: the observe-then-assert + blocked-construct fixture must land with the L6 replacement in the same phase.
- Import-hygiene proof: profile module imports no syside (structural test).
- Final gates: default suite green, ruff clean.
- If a gate fails and the fix is outside plan scope, STOP and report precisely.
