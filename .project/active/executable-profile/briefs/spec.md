# Brief: Item 3 spec — Executable Profile: Eligibility Gates and Named Diagnostics

You are the spec stage for Item 3 in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- **NEVER run `pytest tests/ -m ""` or `test_corpus_integration.py`** [OWNER instruction]. Gate = default suite.
- Artifact: `spec.md` in `.project/active/executable-profile/`.
- An Item 2 audit session is running concurrently in this repo — do not modify any code or test files during this spec stage (spec.md and CURRENT_WORK.md only).

## Provenance
- Concept (owner-ratified): `.project/reference/constraint-execution-concept.md` — the "executable profile" paragraph + Non-Goals (no invented tolerances) + S1/S2 results and carry-forwards.
- Epic Item 3: `.project/reference/epic_constraint_execution.md`.
- **Items 1 and 2 are landed on this branch** (Item 1 certified; Item 2 implemented, audit in flight): the profile's inputs are their real fact/IR types — `expression_facts.py` (operand leaf facts: type category, enum identity, unit/dimension incl. dimension-known-unit-unknown), `expression_ir.py` (node algebra incl. UnsupportedNode), `constraint_facts.py`. Read them; the S1 equality-gate evidence is baked into the golden fixtures.
- S2 operator matrix v1 (concept Appendix B S2 result): comparisons, and/or/not, arithmetic + unary minus + `^`, defaulted formals IN; equality per S1's gate; xor/implies, invocation, feature chains, unit conversion BLOCKED with diagnostics.

## Objective (from the epic)
Publish the decision procedure for whether an assertion may run — per-construct eligibility with named diagnostics — replacing the L4 placeholder and the L6 blanket warning, enforced at design review and codegen preflight.

## Scope (epic Item 3 §1–5)
1. Admit (operator matrix v1): static scalar asserts, inline and definition-typed; comparisons; and/or/not; arithmetic in operand position; negated polarity; owner-scope references, explicit actuals, modeled defaults.
2. Equality gate (S1 evidence): Boolean/string/integer/same-enumeration in; real-valued equality, incompatible enums/dimensions, unresolved operands blocked with named diagnostics.
3. Unit policy: dimensionless or identical structurally-proven exact units; dimension-only typing (LengthValue) blocks; applies to inequalities and arithmetic, not just equality — **add the golden inequality-unit cases S1 left unpinned** (carry-forward (2)): `1 [m] <= 100 [cm]` → block; `integer <= real` → admit.
4. Block with named diagnostics: assert-by-reference, xor/implies, invocation, feature chains, unit conversion; satisfy cataloged unassessed.
5. Enforcement seams: L4/L6 validation replacement in agentic-mbse (see `level4_constraints.py` L4 placeholder, `level6_architecture.py` L6 blanket warning); preflight hook in sysml-codegen (spec the hook's contract here; its wiring is a small sysml-codegen change this item owns — note the cross-repo seam); **the profile gate strictly precedes any compilation** (S2 carry-forward (2): the compiler strip-renders units and is not a safety net).

## Out of scope
The compiler itself (Item 7); catalog persistence (Items 5, 7); where an exact-unit contract could come from (open spec question — this item blocks; a future item may relax; record as decision, not scope).

## Success criteria (from the epic)
- Every S1 golden equality case gets the matrix decision; new inequality-unit golden cases pinned.
- L4 no longer reports a 0% placeholder; L6's blanket per-constraint warning is gone; every diagnostic names construct + source location.
- A model using only supported constructs passes silently; each blocked construct fires exactly its named diagnostic (loud-on-gap, silent-on-clean).
- Both repos' suites green.
