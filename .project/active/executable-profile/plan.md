# Implementation Plan: Executable Profile — Eligibility Gates and Named Diagnostics

**Status:** Draft
**Created:** 2026-07-12
**Last Updated:** 2026-07-12
**Epic:** CONSTRAINT-EXEC, Item 3 · Branch `constraint-exec-epic`

## Source Documents
- **Spec:** `.project/active/executable-profile/spec.md`
- **Design:** `.project/active/executable-profile/design.md` ← component surface, D1–D9, invariants, gate precedence live here
- **Golden oracle:** `tests/fixtures/constraint_fact_shapes/golden.json` (`type_units.equality_cases`, 14 rows)
- **Offline neutral facts:** `tests/fixtures/constraint_fact_shapes/production_facts.json` (28 usages, all six forms — `parse()`-loadable, no syside)

## Process Constraints (read first)
- **Gate = default suite: `uv run pytest tests/`.** NEVER run `pytest tests/ -m ""` or `test_corpus_integration.py` [OWNER].
- Do NOT `git commit` — the orchestrator commits.
- Ruff clean each phase: `uv run ruff check src/ tests/` and `uv run ruff format src/ tests/`.
- The sysml-codegen wiring (Phase 4) is a **separate repo**; its commit is sequenced by the orchestrator. This plan produces a ready-to-apply change description + tests, not an edit to that tree.

## Implementation Strategy

**Phasing rationale.** De-risk the algorithmic core first. The riskiest, most falsifiable part
is reproducing the golden's 11 decision codes (B1). It is pure and offline, so Phase 1 pins it
against the golden oracle before any walk or integration exists. Phase 2 wraps the proven gate in
the three-layer walk + resolver + preflight. Phase 3 rewires the two in-repo seams (L4/L6). Phase 4
specifies the cross-repo seam. Each phase is independently green under the default suite.

**Critical path:** matrix helpers pass the golden (Ph1) → walk/evaluate_profile/preflight over
neutral facts (Ph2) → L4/L6 consume `ProfileResult` (Ph3) → sysml-codegen calls `preflight` (Ph4).

**First proof point:** Phase 1's `classify_equality` returns all 14 golden `decision` codes and the
module imports with no syside loaded. If that passes, B1 (the sufficient-basis bet) holds.

**Biggest risks:**
- **L6/L4 fixture semantics flip.** Existing L6 tests assert a WARN fires on `affordable`/`within_limit`
  (clean `<=` asserts). Under the profile those become **admitted → silent**. Phase 3 must rewrite
  those tests to the new semantics and add a deterministic blocked-construct fixture — mitigated by an
  observe-then-assert step (Ph3) so we assert what the profile actually emits, not a guess.
- **Cross-repo seam unverifiable here** (design Potential Risks). Mitigated by pinning the `preflight`
  contract and the two-arm same-IR assertion precisely (D7); wiring is mechanical.

**Overall validation:** each phase writes tests first, then code, then runs the default suite + ruff.

---

## Phase 1: Matrix core — types, gate helpers, golden matrix (pure, offline)

### Goal
Stand up `sysml/executable_profile.py` with its dataclasses, `REASON_CODES`,
`PROFILE_SEMANTIC_VERSION`, and the two operand-fact gate helpers — nothing that walks a tree yet.
Prove the gate reproduces the golden. This is the whole algorithmic bet (B1) in isolation.

### Assumption Under Test
B1: `(category, enumeration, unit)` on `OperandTypeFact` is a sufficient basis for every golden
decision — no evaluator call, no fact the neutral schema lacks.

### Test Stencil (write first)
```python
# tests/test_sysml/test_executable_profile_matrix.py
import json
from pathlib import Path
from agentic_mbse.sysml.expression_facts import OperandTypeFact, UnitFact
from agentic_mbse.sysml.executable_profile import classify_equality, unit_compatibility

GOLDEN = json.loads(Path("tests/fixtures/constraint_fact_shapes/golden.json").read_text())

def _operand(d):  # build OperandTypeFact straight from a golden left/right dict
    u = d["unit"]
    return OperandTypeFact(category=d["category"], enumeration=d["enumeration"],
                           unit=UnitFact(unit=u["unit"], dimension=u["dimension"]) if u else None)

@pytest.mark.parametrize("case", GOLDEN["type_units"]["equality_cases"],
                         ids=lambda c: c["name"])  # 14 named rows
def test_equality_matrix_reproduces_golden(case):
    got = classify_equality(_operand(case["left"]), _operand(case["right"]))
    assert got == case["decision"]
```

### Changes Required
**See design.md for:** gate precedence → `design.md#implementation-notes` (equality precedence 1–6;
`unit_compatibility` ordered guards); public surface → `design.md#component-overview`; D3/D4/D5.

**Note on the golden as oracle:** build `OperandTypeFact` directly from each row's `left`/`right`
dict. The golden's `unit.dimension` uses the retired `ISQBase::Length` spelling (MF4), not production
`ISQBase::LengthUnit` — this is harmless here because the gate only tests dimension **equality**
between two operands, and both operands in a row share the convention. Do **not** cross-reference
production dimension spellings in this test.

#### 1. Fixture: add inequality cases (D9)
**File:** `tests/fixtures/constraint_fact_shapes/golden.json` (MODIFY — additive)
- [ ] Add `type_units.inequality_cases`: a list of `{name, operator, left, right, decision}`.
- [ ] Row `inequality_convertible_unit`: `operator="<="`, `left`/`right` a **byte-copy** of
  `quantity_convertible_unit`'s metre/centimetre operands, `decision="block_unit_conversion_required"`.
- [ ] Row `inequality_integer_real`: `operator="<="`, `left`/`right` a **byte-copy** of `integer_real`'s
  integer/real operands, `decision` = the ordering **admit** marker `unit_compatibility` returns for a
  clean pair (the `ok` sentinel — align the string to the helper's actual clean return in code).
- [ ] The two S1-certified `type_units.equality_cases` operands are the copy source — do not re-author
  operand facts by hand (D9). Only `decision` and `operator` are new.

#### 2. Module skeleton + gate helpers
**File:** `src/agentic_mbse/sysml/executable_profile.py` (NEW)
- [ ] Module docstring: pure facts→decisions library; imports `expression_facts`/`expression_ir`/
  `constraint_facts` only; **no syside, no `ValidationCode`, no pydantic** (D2/I4).
- [ ] `Eligibility` enum (`ADMIT`/`BLOCK`/`UNASSESSED`).
- [ ] Frozen dataclasses `EligibilityDiagnostic`, `UsageDecision`, `ProfileResult`, `PreflightResult`
  per `design.md#component-overview`. (`evaluate_profile`/`preflight` bodies land in Phase 2 — a `...`
  stub or `NotImplementedError` is fine now; keep them import-clean.)
- [ ] `REASON_CODES`: the 11 golden codes + construct blocks (`block_assert_by_reference`,
  `block_feature_chain`, `block_invocation`, `block_xor`, `block_implies`, `block_unsupported_node`) +
  default-deny codes (`block_unsupported_operator`, `block_unsupported_operand_category`,
  `block_non_predicate_root`, `block_missing_predicate`, `block_unresolved_definition`).
- [ ] `PROFILE_SEMANTIC_VERSION = "executable-profile/v1"` (D8).
- [ ] `unit_compatibility(left, right) -> str`: ordered guards exactly per `design.md#implementation-notes`
  (unitless-vs-dimensioned; unknown exact unit; incompatible dimensions; conversion required; else `ok`;
  integer/real/dimensionless mixes → `ok`).
- [ ] `classify_equality(left, right) -> str`: precedence 1–6 layering unresolved/unknown → the shared
  `unit_compatibility` → real-tolerance → enum → same-scalar support codes.
- [ ] Ordering path (the `<`/`<=`/`>`/`>=` entry) = `unit_compatibility` only, `ok` → admit.

#### 3. Import-hygiene test (I4)
**File:** `tests/test_sysml/test_executable_profile_hygiene.py` (NEW)
- [ ] Structural test: `subprocess` runs `python -c "import agentic_mbse.sysml.executable_profile,
  sys; assert 'syside' not in sys.modules"`; assert exit 0. (Plain `python` subprocess — the
  CLAUDE.md blank-output caveat is about the *Claude CLI*, not this.)

### Validation
**Automated:**
- [ ] `uv run pytest tests/test_sysml/test_executable_profile_matrix.py tests/test_sysml/test_executable_profile_hygiene.py` → all pass (14 equality + 2 inequality + hygiene).
- [ ] `uv run pytest tests/` → no regressions (golden.json edit is additive; confirm
  `test_constraint_fact_shapes.py` still passes — it reads `equality_cases`, untouched).
- [ ] `uv run ruff check src/ tests/` → clean.

**What we know works after this phase:** the operand-fact gate reproduces the golden answer key end to
end (B1 held), and the module is license-free. The hardest part is done and pinned.

---

## Phase 2: The walk — resolver, form gate, node-kind walk, `evaluate_profile`, `preflight`

### Goal
Wrap the proven gate in the three ordered layers (`design.md#core-concept`): form dispatch → resolve
(+ absence cases) → node-kind walk → operand-fact gate. Deliver `evaluate_profile(facts)` and
`preflight(facts)`.

### Assumption Under Test
Totality by default-deny (I1): every `ConstraintUsageFact` — including the two absence inputs and any
unadmitted node role/operator — lands in exactly one outcome with a named reason, driven off neutral
`ConstraintFacts` with no syside.

### Test Stencil (write first)
```python
# tests/test_sysml/test_executable_profile.py
from agentic_mbse.sysml.constraint_facts import parse
from agentic_mbse.sysml.executable_profile import evaluate_profile, Eligibility

FACTS = parse(Path("tests/fixtures/constraint_fact_shapes/production_facts.json").read_text())

def _decision(name):
    return next(d for d in evaluate_profile(FACTS).decisions if d.identity.name == name)

def test_satisfy_is_unassessed():
    assert _decision("satisfied_limit").eligibility is Eligibility.UNASSESSED

def test_feature_chain_actual_is_admitted():   # spec [HARD]: actual chain does NOT trip the block
    assert _decision("typed_feature_chain_and_literal").eligibility is Eligibility.ADMIT
```

### Changes Required
**See design.md for:** three-layer order + short-circuit → `design.md#core-concept`; resolution &
absence routing → `design.md#architecture`; walk classification → `design.md#architecture` ("The walk");
I1–I3; D6 (bare-Boolean root); D7 (`effective_predicate` stored on the decision).

**File:** `src/agentic_mbse/sysml/executable_profile.py` (complete the Phase 1 stubs)
- [ ] Layer 1 form gate: dispatch on `source.form` — `satisfy`/`requirement_constraint`/`plain_usage`
  → UNASSESSED (set `unassessed_kind`); `named_usage_reference` → BLOCK `block_assert_by_reference`;
  unknown form → BLOCK (default-deny); only `inline`/`definition_typed` continue.
- [ ] Resolver: build `{qn: ConstraintDefinitionFact}` index from `facts.definitions`. For
  `definition_typed`, look up `source.constraint_definition.qualified_name`; miss → BLOCK
  `block_unresolved_definition`. For `inline`, take `usage.predicate`. A resolved-`None` predicate →
  BLOCK `block_missing_predicate` (MF2). Store the resolved IR on `UsageDecision.effective_predicate`
  (the exact object — I5/D7, no copy).
- [ ] Layer 2 walk: recursive classify over `ExpressionIR`. Propositions (comparison/connective
  `and`/`or`/`not`) recurse; comparisons + arithmetic invoke the gate. Emit construct-named blocks for
  feature chains (`chain_segments` non-empty), `InvocationNode`, `xor`, `implies`, `UnsupportedNode`,
  unadmitted operators (incl. `!=` → `block_unsupported_operator`, D5), unadmitted node roles, and a
  bare-Boolean predicate root (`block_non_predicate_root`, D6). Diagnostics **accumulate**; outcome is
  singular BLOCK (I2).
- [ ] Layer 3 gate wiring: at each comparison recover both operands' `operand_type` (leaf/unit/arith
  carry it; a proposition in value position → `block_non_predicate_root`); `==` → `classify_equality`,
  `< <= > >=` → ordering (`unit_compatibility`); arithmetic node → `unit_compatibility`.
- [ ] `is_negated=True` and a body `not` are admitted polarity — no diagnostic (`design.md#implementation-notes`).
- [ ] `evaluate_profile(facts) -> ProfileResult`: one `UsageDecision` per `facts.usages` (never over
  `facts.definitions` — I1); `ProfileResult` carries derived admit/block/unassessed counts.
- [ ] `preflight(facts) -> PreflightResult`: `ok` (no would-execute block), `blocking` (blocked
  asserts + diagnostics), `admitted` (decisions with `effective_predicate`), `unassessed`.

**Tests:**
**File:** `tests/test_sysml/test_executable_profile.py` (NEW)
- [ ] Form-gate outcomes over `production_facts.json`: `satisfied_limit`/`named_usage`(plain)/
  requirement usages → UNASSESSED; the `named_usage_reference` usage → BLOCK
  `block_assert_by_reference`; `typed_feature_chain_and_literal` (definition_typed, chain **actual**)
  → ADMIT.
- [ ] Silent-on-clean / loud-on-gap: a clean admitted assert emits zero diagnostics; synthetic facts
  with a feature-chain / `xor` / real-equality predicate each emit exactly the matching named block.
- [ ] Default-deny unit tests (synthetic `ConstraintFacts`, no golden pin — mirrors how `unknown` is
  covered): operand category `unknown` → `block_unsupported_operand_category`; an operator outside the
  admit set (and not `xor`/`implies`) → `block_unsupported_operator`; `!=` → `block_unsupported_operator`
  (D5); bare-Boolean predicate root → `block_non_predicate_root` (D6).
- [ ] Absence cases (MF2, synthetic facts): `definition_typed` usage typed by a bodyless definition
  (`predicate=None`) → `block_missing_predicate`; `definition_typed` usage whose
  `constraint_definition` QN is absent from `facts.definitions` → `block_unresolved_definition`.
- [ ] Totality (I1): every usage in `production_facts.json` yields exactly one decision with a
  non-null eligibility; count of decisions == `len(facts.usages)`.

### Validation
**Automated:**
- [ ] `uv run pytest tests/test_sysml/test_executable_profile.py` → pass.
- [ ] `uv run pytest tests/` → no regressions.
- [ ] `uv run ruff check src/ tests/` → clean.

**What we know works after this phase:** `evaluate_profile`/`preflight` are total and reason-distinguishable
over real neutral facts and every default-deny/absence input — the profile is complete and offline.

---

## Phase 3: L4/L6 seam replacement

### Goal
Point the two in-repo seams at `ProfileResult`: L4 reports eligibility coverage alongside the surviving
counts; L6 emits one WARNING per blocked construct. Add the `ValidationCode` entries.

### Assumption Under Test
The seams consume the profile without duplicating diagnostics (L4 counts only; L6 owns per-construct
warns — `design.md#potential-risks`), and the suite stays green because WARNING never fails a level and
clean asserts now emit nothing.

### Test Stencil (write first — observe, then assert)
```python
# Run once to SEE what the profile emits on the existing fixtures, then pin the assertions:
#   uv run python -c "from agentic_mbse.validation.level6_architecture import check_constraint_executability; ..."
# affordable / within_limit are clean `<=` -> expected ADMIT -> no WARN.
def test_blocked_construct_warns():           # deterministic loud-on-gap
    issues = check_constraint_executability(_load("<blocked-construct fixture>.sysml"))
    warns = [i for i in issues if i.code == ValidationCode.L6_CONSTRAINT_INELIGIBLE]
    assert len(warns) == 1 and warns[0].severity == Severity.WARNING
```

### Changes Required
**See design.md for:** L4 deletion surface + surviving counts, L6 replacement + loud-on-failure
discipline → `design.md#component-overview`; WARNING severity → `spec.md#decisions-recorded`.

#### 1. `ValidationCode` entries
**File:** `src/agentic_mbse/sysml/types.py` (MODIFY, near line 108)
- [ ] Add the eligibility WARNING code(s), e.g. `L6_CONSTRAINT_INELIGIBLE` (message wording carries
  construct + reason). `sysml/types.py` is syside-free — safe (design Research Findings). Keep or
  retire `L6_CONSTRAINT_NON_EXECUTABLE` per what the new L6 body emits.

#### 2. L4 replacement
**File:** `src/agentic_mbse/validation/level4_constraints.py` (MODIFY)
- [ ] Delete `check_constraint_coverage` (lines 44–82) entirely.
- [ ] Delete its caller surface: the `unconstrained, coverage_metrics = ...` call and the
  `unconstrained` → warnings loop (lines 131–138) and `metrics.update(coverage_metrics)` (line 146).
- [ ] **Keep** the surviving counts `Total constraints` / `ConstraintUsage` / `ConstraintDefinition`
  (lines 141–146). Add eligibility coverage: call `extract_constraint_facts(model)` →
  `evaluate_profile(facts)` → add admit/block/unassessed counts to `metrics` (labels are design detail;
  denominator = executable-asserts / total-asserts per `spec.md#open-questions`).

#### 3. L6 replacement
**File:** `src/agentic_mbse/validation/level6_architecture.py` (MODIFY, `check_constraint_executability`
body 606–642)
- [ ] Replace body: `extract_constraint_facts(model)` → `evaluate_profile(facts)`; for each blocked
  decision emit one WARNING `ValidationIssue` per diagnostic (construct + `location` + identity +
  reason). Admitted and unassessed → nothing.
- [ ] Preserve loud-on-failure: let an extraction failure surface (do **not** re-introduce
  `except: constraints = []`). Keep the existing `test_fails_loud_on_extraction_error` green.

#### 4. Update affected tests to new semantics
- [ ] `tests/test_validation/test_item4_subtype.py` (60–101): `TestLevel6NonExecutableWarn` — rewrite.
  `affordable` (clean `<=`) and `positive_cost` (plain) no longer warn. Assert admitted/unassessed →
  no WARN; keep `test_clean_model_silent`; keep `test_fails_loud_on_extraction_error`.
- [ ] `tests/test_validation/test_item12_checks.py` (108–117): `test_c3_constraint_warns_not_fails` —
  `within_limit` (clean `<=`) now admits → no warn. Repoint to a blocked-construct fixture (below).
- [ ] `tests/test_sysml_quality_checks.py` (633–653, 1073–1080): the two L4 tests assert old labels
  `Total attributes`/`Constrained`/`Coverage`. Update to the new eligibility labels; keep the
  surviving `Total constraints` assertion. Confirm `result.success is True` (informational).

#### 5. Blocked-construct fixture (deterministic loud-on-gap)
**File:** `tests/fixtures/<new>/…sysml` (NEW) — an `assert constraint` whose predicate carries a
genuinely blocked construct (e.g. `xor`, a feature chain in the predicate body, or a real-equality),
so L6 fires exactly one named WARN regardless of how bare operands resolve. Reuse for the item12 C3
test.

### Validation
**Automated:**
- [ ] `uv run pytest tests/test_validation/test_item4_subtype.py tests/test_validation/test_item12_checks.py tests/test_sysml_quality_checks.py` → pass.
- [ ] `uv run pytest tests/` → **full default suite green** (the phase's key gate — no other L4/L6
  consumer regressed).
- [ ] `uv run ruff check src/ tests/` → clean.

**Manual:**
- [ ] `uv run agentic-mbse validate --level=4 tests/fixtures/l6_architecture` → eligibility coverage
  metrics appear; level passes.
- [ ] `uv run agentic-mbse validate --level=6 <blocked fixture>` → one named WARN, level passes.

**What we know works after this phase:** both in-repo seams read the profile; the blanket L6 warning and
the L4 0% placeholder are gone; the suite is green under the new semantics.

---

## Phase 4: sysml-codegen preflight wiring (ready-to-apply, separate repo)

### Goal
Produce the exact, mechanical change for sysml-codegen: build `ConstraintFacts` once, call
`preflight(facts)` **before any compilation**, branch on `.ok`, lower `admitted[].effective_predicate`,
and assert the same-IR seam (two arms, D7). This item **owns** this commit; the orchestrator sequences
it to avoid tree conflicts.

### Assumption Under Test
B2: one `ConstraintFacts` value feeds both preflight and the compiler. Which same-IR arm applies
depends on whether one parse reaches both sides (object identity) or a serialization boundary sits
between them (serialization-equality) — the de-risk spike question in `design.md#next-stage-handoff`.

### Deliverable (this repo)
**File:** `.project/active/executable-profile/briefs/sysml-codegen-preflight.md` (NEW — a ready-to-apply
change description, since the target tree is another repo)
- [ ] Locate the pre-compile seam in sysml-codegen (the point that lowers a predicate to Python).
- [ ] Insert: build facts once → `result = preflight(facts)`; if `not result.ok`, halt generation and
  emit `result.blocking` diagnostics (construct + location + identity + reason); emit nothing partial.
- [ ] Else, for each `admitted` decision, lower **its** `effective_predicate` — never a re-resolved or
  re-parsed IR.
- [ ] Same-IR assertion at the seam (D7): in-process single-parse arm → `gated_ir is compiled_ir`;
  snapshot/parse-boundary arm → `serialize_expression(compiled_ir) == serialize_expression(gated_ir)`
  (`serialize_expression` at `expression_ir.py:133`). State which arm applies per the spike finding.
- [ ] Pin the agentic-mbse package version (coordinated-pair discipline) and assert
  `PROFILE_SEMANTIC_VERSION == "executable-profile/v1"`.
- [ ] Specify the sysml-codegen tests: preflight halts on a blocked would-execute assert (named
  diagnostic, nothing generated); admitted assert compiles; unassessed passes; the same-IR assertion
  holds on the fixture path.

### Validation
- [ ] The brief is self-contained: a fresh implementer in sysml-codegen can apply it without this chat.
- [ ] agentic-mbse side already exports the surface `preflight`/`PROFILE_SEMANTIC_VERSION` consumes
  (verified in Phase 2). No agentic-mbse code change here.
- [ ] **De-risk note (carried from design):** before wiring, a `/_my_spike` in sysml-codegen answers
  "does one parsed `ConstraintFacts` reach both gate and compiler, or is there a second parse /
  re-serialize between them?" — the answer selects the arm and where the assertion sits.

**What we know works after this phase:** the cross-repo seam is specified precisely enough to apply
mechanically, with the same-IR guarantee expressed as a checkable assertion on both construction paths.

---

## Environment Setup
See CLAUDE.md. All commands via `uv run`. Gate = default suite (`uv run pytest tests/`); never
`-m ""` or the corpus test.

## Risk Management
See `design.md#potential-risks`. Phase-specific mitigations:
- **Ph1:** golden dimension-spelling artifact (MF4) — build operands from the golden dict directly;
  gate only compares dimension equality, so the artifact is harmless.
- **Ph2:** `unknown` category and true n-ary nodes have no golden row — covered by default-deny unit
  tests, not golden pins (design Potential Risks; B3).
- **Ph3:** clean-`<=` asserts flip from WARN to silent — observe-then-assert + a dedicated
  blocked-construct fixture make loud-on-gap deterministic.
- **Ph4:** cross-repo seam unverifiable from here — pin the contract + two-arm assertion; wiring is
  mechanical.

## Implementation Notes
[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
### Phase 2 Completion
### Phase 3 Completion
### Phase 4 Completion

---
**Status:** Draft → In Progress → Complete
</content>
</invoke>
