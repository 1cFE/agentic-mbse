# Brief: Item 3 audit — Executable Profile

You are a fresh audit session in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`. You did not implement this; audit it.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- **NEVER run `pytest tests/ -m ""` or `test_corpus_integration.py`** [OWNER instruction]. Gate = default suite.
- Artifact: `audit.md` in `.project/active/executable-profile/`.
- Attempt execution first (uv run pytest works here); if blocked, write "Requested live probes".

## Audit target
The four Item 3 phase commits against `spec.md` (review-revised), `design.md` (rev 2), `plan.md` (+ notes). Note: the sysml-codegen wiring (Phase 4) is deliberately a ready-to-apply brief — audit the BRIEF's completeness against the design's preflight contract (the orchestrator applies it separately; do not mark it unimplemented as a defect, but do flag anything the brief under-specifies).

## What to verify, not trust
1. **The 14+2 golden rows**: run the parametrized tests; independently spot-derive three tricky rows (quantity_feature_unknown_unit, integer_real equality-vs-ordering, the two new inequality pins) against the production code.
2. **Default-deny totality**: mutation probe — construct a synthetic usage with an unrecognized operator and one with kind='unknown' operand; both must block with named reasons, never admit or crash. Also the two absence cases (bodyless definition; lookup miss).
3. **Body-vs-actuals rule**: the typed_feature_chain_and_literal case admits (actual is chain-shaped); a chain INSIDE a predicate body blocks — both tested?
4. **L4/L6 replacement**: the 0% placeholder is gone (grep); L6 blanket warning gone; loud-on-gap fixture fires; loud-on-extraction-failure preserved; the WARN-flip is documented, not silent.
5. **The PEP 562 lazy-import change**: this touched both package __init__.py files — a wider blast radius than the item's scope. Verify nothing else regressed (full default suite; check downstream-consumed names still import: the Ir* aliases, extract_constraint_facts, data_models). Check the lazy re-export preserves `from agentic_mbse.sysml import X` for every name in __all__.
6. **Import hygiene**: the profile module imports no syside (run the structural test; also grep).
7. **Suites**: default suite, ruff — run them.

Verdict: Certify / Certify-with-notes / Fail.
