# Spec Review: Constraint-Wave Profile Semantics

**Spec:** `.project/active/constraint-wave-profile-semantics/spec.md`
**Contract:** `/home/reid/.agents/skills/my-spec/SKILL.md`
**Review File:** `.project/active/constraint-wave-profile-semantics/spec-review.md`
**Date:** 2026-07-19

---

## Reality Check

**Sound.** The revised spec still targets the two reproduced profile gaps: ordering reaches
`unit_compatibility` without a numerical-category gate, and `_evaluate_usage` does not consume
`ConstraintUsageFact.is_negated` (`src/agentic_mbse/sysml/executable_profile.py:521-525,717-783`).
It also preserves the verified downstream reality: codegen already keeps the positive predicate IR,
derives expected truth from polarity, and applies polarity to status and simple margin
(`../sysml-codegen/src/sysml_codegen/analysis/constraint_lowering.py:970-987,1083-1104`;
`../sysml-codegen/src/sysml_codegen/generation/predicate_compiler.py:232-302`). The revision is
fundamentally correct and complete enough to serve as the design contract.

---

## Prior Finding Verification

| Prior finding | Verification against the revised spec and current contracts | Status |
|---|---|---|
| L1-1, L1-2 — provenance | The spec now quotes only the owner's actual response, expressly says ratification did not make the expanded formulations owner-originated, and grades both semantic selections `[INFERRED]` with their agent recommendation and ratification source (`spec.md:51-55,63-73,151-158`). | Resolved |
| L1-3 — downstream premise | The correction remains framed as a missing profile contract and second semantic path, not a proven wrong verdict (`spec.md:41-50`). That matches lowering, catalog validation, compilation, and the existing negated execution test (`../sysml-codegen/src/sysml_codegen/analysis/constraint_lowering.py:970-987,1083-1104`; `../sysml-codegen/src/sysml_codegen/resolution/models.py:387-438,454-482`; `../sysml-codegen/tests/execution/test_constraint_execution.py:509-544`). | Resolved |
| L2-1 — total ordering policy | The acceptance matrix now names all eight actual operand categories and all 64 ordered pairs for each of the four ordering operators. It whitelists only integer/real combinations and quantity/quantity for the existing checks, so numeric/non-numeric reversals cannot fall through (`spec.md:79-86`; `src/agentic_mbse/sysml/expression_facts.py:52-62`). | Resolved |
| L2-2 — separate polarity | The spec preserves the positive source predicate, carries polarity separately, and requires one authoritative consumer path (`spec.md:71-73,98-110,155-158`). This matches the original owner concept and avoids changing raw `actual_value`. | Resolved |
| L3-1 — bool-only polarity | Admission now requires `type(is_negated) is bool`; `None`, strings, integers, and every other non-Boolean direct or codec value receive one named BLOCK before the predicate walk (`spec.md:93-97`). This closes the real codec hole where raw JSON is assigned directly (`src/agentic_mbse/sysml/constraint_facts.py:272-285`). | Resolved |
| L3-2 — exact source-IR continuity | One success criterion now traces identical serialized positive-source bytes through extraction/codec, `UsageDecision`, lowering, concrete/catalog, and compiler input for every polarity/form row (`spec.md:98-106`). The corresponding hard requirement preserves the same bytes across all seams (`spec.md:174-177`), extending the current lowering and catalog guards (`../sysml-codegen/src/sysml_codegen/analysis/constraint_lowering.py:972-987`; `../sysml-codegen/src/sysml_codegen/generation/constraint_catalog.py:146-180`). | Resolved |
| L3-3 — exact-once runtime oracle | The paired table uses one positive body under both polarities and covers true, false, strict zero, inclusive zero, and non-finite cases. It pins identical raw evidence, expected status, one margin-sign inversion, `0.0` normalization, and indeterminacy (`spec.md:111-123`). These assertions can distinguish zero, one, and two polarity applications. | Resolved |
| L3-4 — version skew | The spec requires old-codegen/new-companion rejection, new-codegen/old-companion rejection, and a passing released pair. It also checks the raised dependency floor, resolved lock, runtime versions, exact revisions, suite order, and unchanged facts/snapshot-v3 shape (`spec.md:133-147,181-187`). Current anchors are companion `0.1.1`, codegen `agentic-mbse>=0.1.1`, lock resolution `0.1.1`, and the v3 lowering pin (`../sysml-codegen/pyproject.toml:24`; `../sysml-codegen/uv.lock:6-8`; `../sysml-codegen/src/sysml_codegen/analysis/constraint_lowering.py:867-871`). | Resolved |
| L3-5 — field drift | The contract now names the exhaustive map, its failing test, the exact eleven current dataclass fields, and key equality against `dataclasses.fields(ConstraintUsageFact)` (`spec.md:124-130`; `src/agentic_mbse/sysml/constraint_facts.py:133-147`). Adding, removing, or renaming a field therefore cannot leave the inventory green. | Resolved |
| L3-6 — compound diagnostics | The revised criterion requires exactly N reason-grade diagnostics for N malformed comparisons in expression-walk order, one usage BLOCK, the same N ordered L6 ERRORs, and one preflight halt before mutation (`spec.md:87-92`). This is precise about per-comparison cardinality and preserves the walk's deterministic collection model. | Resolved |
| L4-1 — stage-neutral non-goals | The process-only restrictions are gone. The remaining Non-Goals describe product and semantic scope only (`spec.md:204-214`). | Resolved |
| L5-1 — comprehension | The semantic choices are now stated plainly after a short provenance record. The Known Requirements no longer present agent expansions as pseudo-quotes and can be understood without decoding the prior review (`spec.md:63-73,149-202`). | Resolved |

---

## Audit

### Lens 1 — Faithfulness

No new finding. Owner-originated needs, ratified agent recommendations, inherited contracts, and
hard code/interface constraints are now distinguished honestly. The owner's quote is preserved at
its actual force: approval to proceed, not owner authorship of the expanded matrix or rationale.

### Lens 2 — Problem & Approach

No new finding. The numerical whitelist is consistent with the retained IEEE-double runtime and
default-deny profile. Separate polarity is the only approach among the recorded alternatives that
preserves both the original negation scope and the positive-source-IR invariant.

### Lens 3 — Pipeline Risk

No new finding. The revision makes totality, byte continuity, exact-once behavior, skew rejection,
field completeness, and compound diagnostic behavior objectively falsifiable. Exact diagnostic
names, public polarity field representation, and version identifiers remain correctly deferred to
design without reopening the selected semantics.

### Lens 4 — Hygiene

No material hygiene finding. The Non-Goals now describe the work item's boundary rather than this
stage agent's operating restrictions.

### Lens 5 — Reader Comprehension

No new finding. A reviewer can now identify the two defects, the approved agent-recommended
semantics, the acceptance oracles, and the remaining design choices in one pass.

---

## Engagement Summary

**Overall take:** The revision addresses every prior L1-L5 finding and is ready to become the
design contract. The highest-risk properties are no longer aspirational prose: the full 8×8
ordering policy, bool-only polarity, exact IR continuity, paired runtime oracle, version-skew
matrix, field-drift guard, and compound diagnostic cardinality all have explicit failing
conditions.

**Here's what I need you to weigh in on:** Nothing at spec stage. The remaining choices are the
diagnostic spellings, polarity field representation, test organization, documentation wording, and
new version identifiers already filed under design deferrals.

---

## Resolutions

- **[Prior L1-1, L1-2]** Resolved in the revised spec: the owner's agreement is quoted accurately;
  the expanded recommendations and rationale remain agent-grade after ratification.
- **[Prior L1-3, L2-1, L2-2]** Resolved in the revised spec and verified against current code and
  the original owner concept.
- **[Prior L3-1 through L3-6]** Resolved with explicit acceptance oracles and guards, verified
  against the current fact schema, profile, lowering, catalog, compiler, package metadata, and lock.
- **[Prior L4-1, L5-1]** Resolved by removing process leakage and rewriting the decisions in plain,
  provenance-honest language.

---

**Verdict:** Approve
**Next Steps:** Proceed to `my-design` using this spec as the contract. Preserve the spec's design
deferrals rather than selecting their mechanisms here.
