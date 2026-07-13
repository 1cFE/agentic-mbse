# Brief: Item 2 audit — ExpressionIR

You are a fresh audit session in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`. You did not implement this; audit it.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- **NEVER run `pytest tests/ -m ""` or `test_corpus_integration.py`** [OWNER instruction]. Gate = default suite.
- Artifact: `audit.md` in `.project/active/expression-ir/`.
- Attempt execution first (uv run pytest works); if blocked, write "Requested live probes".

## Audit target
The Item 2 commits (`b05d41e..e352fd8`, incl. the mid-stream `unit_text` fix and the orchestrator's `Ir*` alias rename) against `spec.md` (review-revised), `design.md` (rev 2), `plan.md` (+ notes).

## What to verify, not trust
1. **The epic's success criteria**: all five S2 predicate shapes + stress calc expressions extract and JSON-round-trip byte-identically across independent loads (run the round-trip tests; check "across independent loads" is genuinely tested — two separate model loads, not one load serialized twice).
2. **The unsupported node**: exercised live (the conditional-expression fixture) with a structural diagnostic; the allowlist inversion means NO silent catch-all remains — trace the extractor's fallback path and confirm the design's inversion (mutation probe candidate: add a fake unrecognized metaclass name to a fixture expression → unsupported node, never a generic operator).
3. **The `unit_text` fix** (`48a61ee`): source spelling (`"m"`) not canonical name (`"metre"`) — verify against the golden and the design's B1 fidelity bet; check the fix is structural (short_name), not a string hack.
4. **Operator-spelling fidelity**: `^` vs `**` distinct in extracted trees + serialization (the spec's added criterion); unary minus arity.
5. **Migration completeness**: the 8 sites; no `ExpressionFact`/`predicate-tree` references anywhere (grep); golden diff matched the design checklist (unit-node operands[1] the only subtree deletion) — verify via git show of the golden regen.
6. **Version discipline**: (constraint-facts/v1, expression-ir/v1) pinned; Item 1's byte-stability definition holds at the new pair.
7. **Suite/gates**: default suite, ruff — run them.

Verdict: Certify / Certify-with-notes / Fail.
