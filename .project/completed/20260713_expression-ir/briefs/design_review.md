# Brief: Item 2 design review — ExpressionIR

You are a fresh review session in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`. You did not write this design; review it skeptically.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- **NEVER run `pytest tests/ -m ""` or `test_corpus_integration.py`** [OWNER instruction]. Gate = default suite.
- Artifact: `design-review.md` in `.project/active/expression-ir/`.

## Review target
`.project/active/expression-ir/design.md` (spec, spec-review, briefs beside it).

## Ground truth
S2 probe: `.project/reference/s2-spike/s2_ir.py` + findings; Item 1 landed code (`expression_facts.py`, `constraint_facts.py`, `constraint_extraction.py`, its tests + golden `production_facts.json`); the concept's ExpressionIR paragraph.

## What to probe hardest
1. **The migration surface (7 sites claimed).** Independently grep every reader of `ExpressionFact` / `_expression_fact` / node attributes across src and tests; is 7 complete? A missed reader = broken suite discovered mid-implement.
2. **Compat-rendering fitness (Item 13's byte-identity).** Compare the designed node fields against what S2's probe4_calc_compat rendering read (see s2_ir.py + findings): does every field it consumed exist and carry the same information (operator spellings `^` vs `**`, unary minus arity, the `[`-annotation with unit_text, literal repr fidelity — int vs float forms)? Anything the compat renderer needs that the tagged union drops or renames?
3. **The allowlist enumeration.** Five metaclasses × 18 operators: check against BOTH the S2 probe's dispatch AND Item 1's landed extractor — does the enumeration cover everything the landed extractor currently emits as recognized nodes (else previously-extracted predicates become unsupported → snapshot/golden churn beyond the named migration), and nothing more?
4. **B2 (attribute-name preservation).** Does keeping `operator`/`operands`/`operand_type`/`kind` on the new union actually hold for all kinds (e.g. does a literal node still expose `kind` the way tree-walking tests expect), or does it paper over shape differences that will surface as AttributeErrors?
5. **Byte-stability across the bump.** The golden regeneration: is the new expression-ir/v1 serialization deterministic per D5 (sort_keys? field order?) and consistent with Item 1's D9 definition so Item 8 can pin (envelope, sub-version) cleanly?

Verdict format: must-fix list (each with why), nice-to-haves, overall verdict (Approved / Approved-with-must-fixes / Rework). Verify against code — do not take the design's word.
