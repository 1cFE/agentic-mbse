# Audit: Executable Profile — Eligibility Gates and Named Diagnostics

**Verdict:** Certify-with-notes
**Audited:** 2026-07-12
**Branch:** `constraint-exec-epic`
**Commit:** bf16b8c

---

## Summary

The in-repo work (Phases 1–3) is solid and delivers what the spec and design require. The
matrix gate reproduces the 14+2 golden rows, default-deny totality holds under independent
mutation probing, the L4 0% placeholder and L6 blanket warning are gone and replaced by the
profile-driven seams, the license-free guarantee is intact, and the full default suite is green
(1400 passed). One real defect is in the **Phase 4 ready-to-apply brief** (not applied by this
item): its same-IR assertion is wrong for admitted `definition_typed` usages and would raise on
apply. That is a brief bug, not shipped code — hence Certify-with-notes rather than Fail.

## Findings

### Plan completion

All four phases verified complete.

- **Phase 1 (matrix core):** `executable_profile.py` dataclasses, `REASON_CODES` (22 codes),
  `PROFILE_SEMANTIC_VERSION`, and the two gate helpers exist and are golden-pinned. The
  additive `inequality_cases` block is present (2 rows).
- **Phase 2 (the walk):** form gate, resolver, `_walk`/`_walk_comparison`, `evaluate_profile`,
  `preflight` all implemented; 47-test file passes.
- **Phase 3 (L4/L6):** both seams rewired; `L6_CONSTRAINT_INELIGIBLE` added,
  `L6_CONSTRAINT_NON_EXECUTABLE` retired; the blocked-construct fixture exists.
- **Phase 4 (brief):** `sysml-codegen-wiring.md` is self-contained and grounded in direct
  inspection of the sysml-codegen tree (seam at `constraint_lowering.py:399-401`, halt
  mechanism, version-pin reasoning, four specified tests). One defect — see Code integrity.

No placeholder code, TODOs, or partial implementations in the shipped modules.

### Spec conformance

- **SC1 — golden matrix observable through reason** ✓. Parametrized matrix test passes; the
  seven distinct `block_*` reasons are distinct values in `REASON_CODES` and reproduced through
  the walk. Independently spot-derived against the production code:
  - `quantity_feature_unknown_unit` (`==`, dim-only vs metre) → `block_unknown_exact_unit` ✓
  - `integer_real` — `==` → `block_real_equality_requires_tolerance`; `<=` → `ok` (admit) ✓
    (integer/real promotion poisons equality, not ordering — spec [HARD])
  - `inequality_convertible_unit` (`1 [m] <= 100 [cm]`) → `block_unit_conversion_required` ✓
  - `inequality_integer_real` (`integer <= real`) → `ok` (admit) ✓
- **SC2 — L4 reports eligibility, not 0% placeholder** ✓. `check_constraint_coverage` deleted
  (the name survives only in a docstring explaining the removal); `eligibility_coverage_metrics`
  reports admit/block/unassessed with denominator = admit+block per spec Open Questions;
  surviving counts kept (`level4_constraints.py:110-121`).
- **SC3 — L6 blanket warning gone, per-construct named diagnostic** ✓. The old per-usage
  blanket warn is replaced by one WARNING per blocked diagnostic naming construct + location +
  identity + reason (`level6_architecture.py:600-641`); admitted/unassessed emit nothing.
- **SC4 — silent-on-clean, loud-on-gap** ✓. `test_clean_model_silent` (no WARN);
  `test_blocked_construct_warns` fires exactly one named WARN (`block_feature_chain`).
- **SC5 — codegen preflight contract** — specified in the brief; contract shape is correct
  (runs profile before compilation, halts on blocked would-execute assert, same named
  diagnostic, PROFILE_SEMANTIC_VERSION assertion). Same-IR arm has a defect (below).
- **SC6 — suites green** ✓ agentic-mbse side (1400 passed, 1 skipped, 33 deselected). The
  sysml-codegen suite is not runnable here (separate repo, brief not applied).
- **`[HARD]` body-vs-actuals** ✓. `typed_feature_chain_and_literal` (chain *actual*) is
  ADMITTED (`test_feature_chain_actual_is_admitted`, line 68); a chain *in the predicate body*
  blocks (`test_feature_chain_in_predicate_body_blocks`, line 305; the `blocked.sysml` fixture).
- **`[HARD]` default-deny totality** ✓. Independent mutation probe (not the shipped tests):
  a novel operator `<=>`, an n-ary `..`, and an `unknown` operand each BLOCK with a named
  `REASON_CODES` reason; bodyless definition → `block_missing_predicate`; lookup miss →
  `block_unresolved_definition`. No admit, no crash, in every case.
- **Non-Goals respected** ✓. No compiler, no catalog persistence, no lowering/resolution, no
  predicate rewriting — the module reads facts and decides only.

### Design conformance

- **D1** module placement ✓ (`sysml/executable_profile.py`).
- **D2/I4** license-free ✓. Profile imports only `constraint_facts`/`expression_facts`/
  `expression_ir` (grep + runtime: `import agentic_mbse.sysml.executable_profile` loads no
  syside). L4/L6 do the `ValidationIssue` translation.
- **D3/D4** shared `unit_compatibility` helper, equality layers real-tolerance/enum on top ✓;
  precedence matches the design's Implementation Notes exactly.
- **D5** `!=` blocks `block_unsupported_operator` ✓. **D6** bare-Boolean root blocks
  `block_non_predicate_root` ✓.
- **D8** `PROFILE_SEMANTIC_VERSION = "executable-profile/v1"` ✓.
- **I1 totality / I2 silent-on-clean-loud-on-gap / I3 reason-distinguishable** all verified.
- **PEP 562 lazy re-export (blast radius):** both `__init__.py` files converted; verified all
  94 `agentic_mbse.sysml.__all__` names resolve, top-level `__all__` resolves, and the
  downstream-consumed names import (`Ir*` aliases, `extract_constraint_facts`, `AttributeInfo`,
  `ExpressionRef`, `ConstraintFacts`, `serialize_expression`). Pure-submodule imports load no
  syside. Full suite green confirms no consumer regressed.

### Code integrity

**Finding 1 — Phase 4 brief: same-IR assertion is wrong for `definition_typed` usages
(`sysml-codegen-wiring.md:103`).** The brief's in-process same-IR check is:

```python
assert decision.effective_predicate is usage.predicate or decision.eligibility is not Eligibility.ADMIT
```

For a `definition_typed` admitted usage, `effective_predicate` resolves to the *definition's*
predicate (spec [HARD]: "the effective predicate lives on the `ConstraintDefinitionFact.predicate`,
not the usage"), which is a **different object** than `usage.predicate`. Verified against
`production_facts.json`: for the admitted `typed_feature_chain_and_literal` and
`typed_omitted_default` usages, `decision.effective_predicate is usage.predicate` is **False**.
Applying the brief verbatim would raise `AssertionError` on any admitted definition-typed
assert — a whole form class, including the golden's own flagship-shaped fixtures.

The correct in-process rendering: step 3 already lowers `decision.effective_predicate` directly
(brief line 99), so gated-IR and compiled-IR are the same object *by construction*; the
meaningful check is that no re-resolution reintroduces a second object, not equality against
`usage.predicate`. The assert should compare the object actually being serialized to
`decision.effective_predicate`, or be dropped in favor of the by-construction guarantee. This
is a brief defect, not shipped-code — flagged per the audit brief's instruction to surface
under-specification in the Phase 4 deliverable; the orchestrator applies the brief separately
and should fix this line before or during apply.

**No other integrity issues.** No god functions, no policy-in-utility (L4/L6 own their
severity/translation; the profile emits neutral reasons), no broad `except: return default`
(the L6 loud-on-failure discipline is preserved and tested), no compat shims.

**Low-severity observation (not a finding):** `_walk_comparison` asserts
`left_facts is not None and right_facts is not None` (`executable_profile.py:284`) after the
operand walk passes clean. This relies on leaf/unit/arithmetic nodes always carrying
`operand_type` (a documented extraction invariant). If a future extraction change ever produced
a value-position node with `operand_type=None` that walks clean, this would crash rather than
BLOCK — a theoretical totality edge. Not reachable under the current landed types; noted for
awareness, no change required now.

---

## Certification

**Checked and verified:**
- Golden 14 equality + 2 inequality rows: parametrized tests pass; four tricky rows
  independently spot-derived against the production gate code.
- Default-deny totality: independent runtime mutation probe (novel operator, n-ary operator,
  unknown operand, bodyless definition, definition-lookup miss) — all BLOCK with named reasons,
  none admit, none crash.
- Body-vs-actuals rule tested both directions (chain actual admits; chain in body blocks).
- L4 placeholder removed; L6 blanket warning removed; loud-on-gap fixture fires one named WARN;
  loud-on-extraction-failure preserved (raises, not swallowed); WARN-flip documented in spec
  Decisions.
- PEP 562 blast radius: all `__all__` names in both packages resolve; downstream names import;
  pure imports load no syside.
- Import hygiene (grep + runtime), default suite (1400 passed), ruff on all touched files.

**Marked:** plan Phases 1–4 verified complete; spec SC1–SC4 and SC6 marked met on the
agentic-mbse side; SC5 contract shape correct with one brief defect noted.

**Not checked:**
- The sysml-codegen suite and the Phase 4 wiring in situ — separate repo, brief deliberately
  not applied by this item. SC5's "sysml-codegen suite green" is therefore unverified here, and
  the same-IR assertion defect (Finding 1) is un-exercised until apply.
- The slow corpus / full-marker suites (`pytest -m ""`, `test_corpus_integration.py`) — barred
  by OWNER instruction; gate is the default suite only.
- Runtime behavior of the eligibility metrics under a live multi-file validate beyond the
  plan's recorded manual spot-checks (re-reading, not re-running, those).
- The two-arm same-IR guarantee across a real serialization boundary (Item 8's snapshot path) —
  not yet a live code path anywhere on this branch.

ARTIFACT: .project/active/executable-profile/audit.md
