# Brief: Item 2 spec review — ExpressionIR

You are a fresh review session in the orchestrated CONSTRAINT-EXEC epic run. Repo: agentic-mbse, branch `constraint-exec-epic`. You did not write this spec; review it adversarially.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- **NEVER run `pytest tests/ -m ""` or `test_corpus_integration.py`** [OWNER instruction]. Gate = default suite.
- Artifact: `spec-review.md` in `.project/active/expression-ir/`.

## Review target
`.project/active/expression-ir/spec.md` (brief at `briefs/spec.md`).

## Ground truth (all readable in-repo now)
- S2 spike: `.project/reference/s2-spike/` (findings + the probe IR `s2_ir.py` — the proven node shapes).
- Concept: `.project/reference/constraint-execution-concept.md` (ExpressionIR paragraph, S2 result + carry-forwards).
- Item 1 landed code (CERTIFIED): `src/agentic_mbse/sysml/expression_facts.py`, `constraint_facts.py`, `constraint_extraction.py` + its design.md D4/D9/C1 (the sub-version carve-out).

## What to probe hardest
1. **The v0→v1 transition contract.** The spec bumps `predicate-tree/v0` → `expression-ir/v1`. Walk Item 1's landed serializer/tests: does the spec name every place the sub-version and tree shape are pinned (golden files, round-trip tests, PREDICATE_SCHEMA_VERSION constant), so the transition is a defined migration and not a scavenger hunt? Is the namespace change (predicate-tree → expression-ir) consistent with Item 1's D9 byte-stability definition (per (envelope, sub-version) pair)?
2. **Node algebra completeness vs S2.** Compare the spec's algebra against `s2_ir.py` and the concept's required list: literal, feature ref (source name, qualified target, chain segments, never pre-classified), unary/binary/n-ary, invocation, unit annotation, unsupported-with-diagnostic. Anything S2's parity evidence covered that the spec dropped, or anything added without evidence?
3. **The unsupported-node trigger boundary.** The spec's [INFERRED] line (structurally un-extractable vs profile-ineligible) — is the boundary stated precisely enough that the extractor author knows, for each SysIDE node type, which side it falls on? The current silent catch-all is the failure mode this item kills; a vague boundary reintroduces it.
4. **Downstream fitness.** Item 7 compiles this IR (Kleene, margins); Item 13 renders calc compat byte-identically. Does the spec preserve everything the compat renderer needed in S2 (operator normalization, the `[`-annotation handling, `**`/unary-minus spellings)? A field dropped here surfaces as a byte-identity failure in Item 13.
5. **Sub-version naming discrepancy** — the spec records expression-ir/v1 vs Item 1 design's predicate-tree/v1 phrasing as [INHERITED]. Confirm that's the right resolution (brief governs) and that no landed test hardcodes the retired name in a way the spec doesn't list.

Verdict format: must-fix list (each with why), nice-to-haves, overall verdict (Approved / Approved-with-must-fixes / Rework). Verify against code and the probe — do not take the spec's word.
