# Implementation Plan: Executable Profile — Eligibility Gates and Named Diagnostics

**Status:** Complete (Phases 1–4)
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
- [x] Add `type_units.inequality_cases`: a list of `{name, operator, left, right, decision}`.
- [x] Row `inequality_convertible_unit`: `operator="<="`, `left`/`right` a **byte-copy** of
  `quantity_convertible_unit`'s metre/centimetre operands, `decision="block_unit_conversion_required"`.
- [x] Row `inequality_integer_real`: `operator="<="`, `left`/`right` a **byte-copy** of `integer_real`'s
  integer/real operands, `decision` = the ordering **admit** marker `unit_compatibility` returns for a
  clean pair (the `ok` sentinel — align the string to the helper's actual clean return in code).
- [x] The two S1-certified `type_units.equality_cases` operands are the copy source — do not re-author
  operand facts by hand (D9). Only `decision` and `operator` are new.

#### 2. Module skeleton + gate helpers
**File:** `src/agentic_mbse/sysml/executable_profile.py` (NEW)
- [x] Module docstring: pure facts→decisions library; imports `expression_facts`/`expression_ir`/
  `constraint_facts` only; **no syside, no `ValidationCode`, no pydantic** (D2/I4).
- [x] `Eligibility` enum (`ADMIT`/`BLOCK`/`UNASSESSED`).
- [x] Frozen dataclasses `EligibilityDiagnostic`, `UsageDecision`, `ProfileResult`, `PreflightResult`
  per `design.md#component-overview`. (`evaluate_profile`/`preflight` bodies land in Phase 2 — a `...`
  stub or `NotImplementedError` is fine now; keep them import-clean.)
- [x] `REASON_CODES`: the 11 golden codes + construct blocks (`block_assert_by_reference`,
  `block_feature_chain`, `block_invocation`, `block_xor`, `block_implies`, `block_unsupported_node`) +
  default-deny codes (`block_unsupported_operator`, `block_unsupported_operand_category`,
  `block_non_predicate_root`, `block_missing_predicate`, `block_unresolved_definition`).
- [x] `PROFILE_SEMANTIC_VERSION = "executable-profile/v1"` (D8).
- [x] `unit_compatibility(left, right) -> str`: ordered guards exactly per `design.md#implementation-notes`
  (unitless-vs-dimensioned; unknown exact unit; incompatible dimensions; conversion required; else `ok`;
  integer/real/dimensionless mixes → `ok`).
- [x] `classify_equality(left, right) -> str`: precedence 1–6 layering unresolved/unknown → the shared
  `unit_compatibility` → real-tolerance → enum → same-scalar support codes.
- [x] Ordering path (the `<`/`<=`/`>`/`>=` entry) = `unit_compatibility` only, `ok` → admit.

#### 3. Import-hygiene test (I4)
**File:** `tests/test_sysml/test_executable_profile_hygiene.py` (NEW)
- [x] Structural test: `subprocess` runs `python -c "import agentic_mbse.sysml.executable_profile,
  sys; assert 'syside' not in sys.modules"`; assert exit 0. (Plain `python` subprocess — the
  CLAUDE.md blank-output caveat is about the *Claude CLI*, not this.)

### Validation
**Automated:**
- [x] `uv run pytest tests/test_sysml/test_executable_profile_matrix.py tests/test_sysml/test_executable_profile_hygiene.py` → all pass (14 equality + 2 inequality + hygiene = 18 tests, plus a golden-decisions-subset-of-REASON_CODES check).
- [x] `uv run pytest tests/` → no regressions (golden.json edit is additive; `test_constraint_fact_shapes.py` still passes — it reads `equality_cases`, untouched). Full run: 1351 passed, 1 skipped, 33 deselected.
- [x] `uv run ruff check src/ tests/` → clean (131 pre-existing errors elsewhere are unchanged from before this phase — confirmed via `git stash` diff; none in the files this phase touched).

**What we know works after this phase:** the operand-fact gate reproduces the golden answer key end to
end (B1 held), and the module is license-free. The hardest part is done and pinned.

**Deviation — the hygiene test found a real pre-existing I4 hole, fixed at the root.**
`import agentic_mbse.sysml.executable_profile` runs `agentic_mbse/__init__.py` and
`agentic_mbse/sysml/__init__.py` first (Python import semantics). Both eagerly imported syside-touching
submodules — the top-level package via `from agentic_mbse.cli import main` (which pulls in the full
validation stack), and the `sysml` package via its barrel re-export of `constraint_extraction`/
`syside_adapter`/etc. — so *any* import under `agentic_mbse`, including `constraint_facts.py`
standalone, was already silently pulling in syside despite that submodule's own "no syside" docstring.
This predates Item 3 and would have equally broken Item 8's license-free snapshot-path guarantee.
Root-caused, not worked around: converted both `__init__.py`s to PEP 562 lazy re-exports
(`__getattr__`/`__dir__`), so every existing name (`agentic_mbse.main`, `agentic_mbse.sysml.SysideAdapter`,
`agentic_mbse.sysml.ConstraintFacts`, ...) still resolves identically on first access, but nothing is
imported at package-load time. Verified: full default suite green (no behavior change for any consumer);
`from agentic_mbse.sysml import <name>` spot-checked for both a syside-touching name (`SysideAdapter`)
and a submodule-style import (`from agentic_mbse.sysml import hierarchy`, which works via Python's
own submodule-import fallback, independent of the lazy table).

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
- [x] Layer 1 form gate: dispatch on `source.form` — `satisfy`/`requirement_constraint`/`plain_usage`
  → UNASSESSED (set `unassessed_kind`); `named_usage_reference` → BLOCK `block_assert_by_reference`;
  unknown form → BLOCK (default-deny); only `inline`/`definition_typed` continue.
- [x] Resolver: build `{qn: ConstraintDefinitionFact}` index from `facts.definitions`. For
  `definition_typed`, look up `source.constraint_definition.qualified_name`; miss → BLOCK
  `block_unresolved_definition`. For `inline`, take `usage.predicate`. A resolved-`None` predicate →
  BLOCK `block_missing_predicate` (MF2). Store the resolved IR on `UsageDecision.effective_predicate`
  (the exact object — I5/D7, no copy).
- [x] Layer 2 walk: recursive classify over `ExpressionIR`. Propositions (comparison/connective
  `and`/`or`/`not`) recurse; comparisons + arithmetic invoke the gate. Emit construct-named blocks for
  feature chains (`chain_segments` non-empty), `InvocationNode`, `xor`, `implies`, `UnsupportedNode`,
  unadmitted operators (incl. `!=` → `block_unsupported_operator`, D5), unadmitted node roles, and a
  bare-Boolean predicate root (`block_non_predicate_root`, D6). Diagnostics **accumulate**; outcome is
  singular BLOCK (I2).
- [x] Layer 3 gate wiring: at each comparison recover both operands' `operand_type` (leaf/unit/arith
  carry it; a proposition in value position → `block_non_predicate_root`); `==` → `classify_equality`,
  `< <= > >=` → ordering (`unit_compatibility`); arithmetic node → `unit_compatibility`.
- [x] `is_negated=True` and a body `not` are admitted polarity — no diagnostic (`design.md#implementation-notes`).
- [x] `evaluate_profile(facts) -> ProfileResult`: one `UsageDecision` per `facts.usages` (never over
  `facts.definitions` — I1); `ProfileResult` carries derived admit/block/unassessed counts.
- [x] `preflight(facts) -> PreflightResult`: `ok` (no would-execute block), `blocking` (blocked
  asserts + diagnostics), `admitted` (decisions with `effective_predicate`), `unassessed`.

**Tests:**
**File:** `tests/test_sysml/test_executable_profile.py` (NEW)
- [x] Form-gate outcomes over `production_facts.json`: `satisfied_limit`/`named_usage`(plain)/
  requirement usages → UNASSESSED; the `named_usage_reference` usage → BLOCK
  `block_assert_by_reference`; `typed_feature_chain_and_literal` (definition_typed, chain **actual**)
  → ADMIT.
- [x] Silent-on-clean / loud-on-gap: a clean admitted assert emits zero diagnostics; synthetic facts
  with a feature-chain / `xor` / real-equality predicate each emit exactly the matching named block.
- [x] Default-deny unit tests (synthetic `ConstraintFacts`, no golden pin — mirrors how `unknown` is
  covered): operand category `unknown` → `block_unsupported_operand_category`; an operator outside the
  admit set (and not `xor`/`implies`) → `block_unsupported_operator`; `!=` → `block_unsupported_operator`
  (D5); bare-Boolean predicate root → `block_non_predicate_root` (D6).
- [x] Absence cases (MF2, synthetic facts): `definition_typed` usage typed by a bodyless definition
  (`predicate=None`) → `block_missing_predicate`; `definition_typed` usage whose
  `constraint_definition` QN is absent from `facts.definitions` → `block_unresolved_definition`.
- [x] Totality (I1): every usage in `production_facts.json` yields exactly one decision with a
  non-null eligibility; count of decisions == `len(facts.usages)`.

### Validation
**Automated:**
- [x] `uv run pytest tests/test_sysml/test_executable_profile.py` → pass (47 tests).
- [x] `uv run pytest tests/` → no regressions (1398 passed, 1 skipped, 33 deselected).
- [x] `uv run ruff check src/ tests/` → clean.

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
- [x] Add the eligibility WARNING code(s), e.g. `L6_CONSTRAINT_INELIGIBLE` (message wording carries
  construct + reason). `sysml/types.py` is syside-free — safe (design Research Findings). Keep or
  retire `L6_CONSTRAINT_NON_EXECUTABLE` per what the new L6 body emits.

#### 2. L4 replacement
**File:** `src/agentic_mbse/validation/level4_constraints.py` (MODIFY)
- [x] Delete `check_constraint_coverage` (lines 44–82) entirely.
- [x] Delete its caller surface: the `unconstrained, coverage_metrics = ...` call and the
  `unconstrained` → warnings loop (lines 131–138) and `metrics.update(coverage_metrics)` (line 146).
- [x] **Keep** the surviving counts `Total constraints` / `ConstraintUsage` / `ConstraintDefinition`
  (lines 141–146). Add eligibility coverage: call `extract_constraint_facts(model)` →
  `evaluate_profile(facts)` → add admit/block/unassessed counts to `metrics` (labels are design detail;
  denominator = executable-asserts / total-asserts per `spec.md#open-questions`).

#### 3. L6 replacement
**File:** `src/agentic_mbse/validation/level6_architecture.py` (MODIFY, `check_constraint_executability`
body 606–642)
- [x] Replace body: `extract_constraint_facts(model)` → `evaluate_profile(facts)`; for each blocked
  decision emit one WARNING `ValidationIssue` per diagnostic (construct + `location` + identity +
  reason). Admitted and unassessed → nothing.
- [x] Preserve loud-on-failure: let an extraction failure surface (do **not** re-introduce
  `except: constraints = []`). Keep the existing `test_fails_loud_on_extraction_error` green.

#### 4. Update affected tests to new semantics
- [x] `tests/test_validation/test_item4_subtype.py` (60–101): `TestLevel6NonExecutableWarn` — rewrite.
  `affordable` (clean `<=`) and `positive_cost` (plain) no longer warn. Assert admitted/unassessed →
  no WARN; keep `test_clean_model_silent`; keep `test_fails_loud_on_extraction_error`.
- [x] `tests/test_validation/test_item12_checks.py` (108–117): `test_c3_constraint_warns_not_fails` —
  `within_limit` (clean `<=`) now admits → no warn. Repoint to a blocked-construct fixture (below).
- [x] `tests/test_sysml_quality_checks.py` (633–653, 1073–1080): the two L4 tests assert old labels
  `Total attributes`/`Constrained`/`Coverage`. Update to the new eligibility labels; keep the
  surviving `Total constraints` assertion. Confirm `result.success is True` (informational).

#### 5. Blocked-construct fixture (deterministic loud-on-gap)
**File:** `tests/fixtures/<new>/…sysml` (NEW) — an `assert constraint` whose predicate carries a
genuinely blocked construct (e.g. `xor`, a feature chain in the predicate body, or a real-equality),
so L6 fires exactly one named WARN regardless of how bare operands resolve. Reuse for the item12 C3
test.

### Validation
**Automated:**
- [x] `uv run pytest tests/test_validation/test_item4_subtype.py tests/test_validation/test_item12_checks.py tests/test_sysml_quality_checks.py` → pass.
- [x] `uv run pytest tests/` → **full default suite green** (the phase's key gate — no other L4/L6
  consumer regressed).
- [x] `uv run ruff check src/ tests/` → clean.

**Manual:**
- [x] `uv run agentic-mbse validate --level=4 tests/fixtures/l6_architecture` → eligibility coverage
  metrics appear; level passes.
- [x] `uv run agentic-mbse validate --level=6 <blocked fixture>` → one named WARN, level passes.

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
**File:** `.project/active/executable-profile/sysml-codegen-wiring.md` (NEW — a ready-to-apply
change description, since the target tree is another repo; path per the orchestrator's brief for
this stage, superseding this section's original `briefs/sysml-codegen-preflight.md` — this repo's
`briefs/` directory is reserved for this item's own orchestration-stage artifacts, not deliverables)
- [x] Locate the pre-compile seam in sysml-codegen (the point that lowers a predicate to Python).
  Found by direct inspection of the sysml-codegen checkout at `/home/reid/1cfe/sysml-codegen`:
  `constraint_lowering.py:399-401` inside `lower_constraints()` — not yet wired into the
  production pipeline (currently test-only; threading is separately tracked in that repo's own
  `.project/active/constraint-lowering/plan.md`).
- [x] Insert: build facts once → run the profile **before any compilation**; if any usage blocks,
  halt generation and emit its diagnostics (construct + location + identity + reason); emit
  nothing partial. (Used `evaluate_profile` directly rather than `preflight`, so the per-usage
  `effective_predicate` is available for the lowering loop in the same pass — `preflight` is a
  thin partition over the same decisions and would need re-deriving that mapping anyway.)
- [x] For each admitted decision, lower **its** `effective_predicate` — never a re-resolved or
  re-parsed IR.
- [x] Same-IR assertion at the seam (D7): the in-process single-parse arm applies today (verified —
  no re-parse/re-serialize point exists between extraction and this seam in the current tree), so
  the brief specifies `decision.effective_predicate is usage.predicate`. Flagged, not built here:
  the serialization-equality arm becomes load-bearing once Item 7's (not-yet-built) compiler reads
  `ConcreteConstraint.predicate_ir` — a string, not a live object — downstream of this seam.
- [x] Pin the agentic-mbse package version (coordinated-pair discipline) and assert
  `PROFILE_SEMANTIC_VERSION == "executable-profile/v1"`. (Existing loose `>=0.1.0` pyproject pin
  kept; the semantic-version runtime assertion is the actual coordination check, per the brief's
  reasoning — a second, separate version-string pin would duplicate and could drift from it.)
- [x] Specify the sysml-codegen tests: preflight halts on a blocked would-execute assert (named
  diagnostic, nothing generated); admitted assert compiles; unassessed passes; the same-IR assertion
  holds on the fixture path.

### Validation
- [x] The brief is self-contained: a fresh implementer in sysml-codegen can apply it without this
  chat — grounded in direct inspection of the current sysml-codegen tree (file:line citations for
  the seam, existing imports, the halt mechanism, the version pin, and existing test conventions),
  not assumed from this repo's design docs alone.
- [x] agentic-mbse side already exports the surface `preflight`/`evaluate_profile`/
  `PROFILE_SEMANTIC_VERSION` consumes (verified in Phase 2). No agentic-mbse code change here.
- [x] **De-risk note (carried from design):** answered by direct inspection rather than deferred to
  a sysml-codegen-side spike — `lower_constraints`'s one caller builds `ConstraintFacts` once via
  `extract_constraint_facts` and passes it straight through with no re-parse point, so the
  in-process object-identity arm applies today. The brief still carries the spike question forward
  as a pre-apply check, in case sysml-codegen's own in-flight pipeline-threading work introduces a
  parse boundary before this lands.

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

### Phase 1 Completion
**Completed:** 2026-07-12
**Changes made:**
- Created `src/agentic_mbse/sysml/executable_profile.py`: `Eligibility`, `EligibilityDiagnostic`,
  `UsageDecision`, `ProfileResult`, `PreflightResult`, `REASON_CODES`, `PROFILE_SEMANTIC_VERSION`,
  `unit_compatibility()`, `classify_equality()`; `evaluate_profile()`/`preflight()` raise
  `NotImplementedError` pending Phase 2.
- Modified `tests/fixtures/constraint_fact_shapes/golden.json`: added `type_units.inequality_cases`
  (additive, 58 lines).
- Created `tests/test_sysml/test_executable_profile_matrix.py` (18 tests: 14 equality + 2 inequality +
  1 hygiene-adjacent REASON_CODES-superset check split across the two decision sets) and
  `tests/test_sysml/test_executable_profile_hygiene.py` (1 subprocess structural test).
- Modified `src/agentic_mbse/__init__.py` and `src/agentic_mbse/sysml/__init__.py` to lazy (PEP 562)
  re-exports — see the deviation note above; root-caused the hygiene test's real failure rather than
  weakening the test.

**Issues encountered / deviations:** the barrel-laziness fix described above; no other deviations from
the plan.

### Phase 2 Completion
**Completed:** 2026-07-12
**Changes made:**
- Completed `src/agentic_mbse/sysml/executable_profile.py`: `_walk`/`_walk_comparison` (the
  recursive node-kind classifier + operand-fact gate wiring), the form gate and definition-lookup
  resolver in `_evaluate_usage`, `evaluate_profile()`, `preflight()`.
- Created `tests/test_sysml/test_executable_profile.py` (47 tests): form-gate outcomes and the full
  golden equality matrix reproduced end-to-end over `production_facts.json`'s 28 real usages; nested
  and/or/not walk tests (one over real data — `compound_boolean`, one fully clean synthetic); a
  multi-violation-accumulation test; default-deny synthetic tests (`unknown` category, an
  out-of-admit-set operator, `!=`, bare-Boolean root, boolean connective operand, feature chain in
  body, `xor`, `implies`, invocation, `UnsupportedNode`); absence-case tests (bodyless definition,
  unresolved definition lookup, degenerate inline `None` predicate); an unused-definition-is-not-a-
  decision test (I1's inventory rule); totality + derived-count tests; `preflight` partition tests
  including an I5 same-object identity check.

**Issues encountered / deviations:**
- The plan's test stencil's `test_satisfy_is_unassessed` name was folded into a parametrized
  `test_non_asserted_forms_are_unassessed` covering all three UNASSESSED-routing forms
  (satisfy/requirement_constraint/plain_usage) in one table, rather than one test per form — same
  coverage, less duplication.
- Wrote a `compound_boolean` test assuming (per its docstring's own paraphrase) that every leaf was
  admitted; running it against real `production_facts.json` data caught that the third leaf
  (`length_value`, a quantity feature with a known dimension but no exact unit) genuinely blocks —
  the test's premise was wrong, not the code. Fixed the test to assert the correct
  `block_unknown_exact_unit` outcome and re-purposed it to prove the walk reaches a leaf nested two
  connective levels deep, then added a separate fully-clean synthetic nested-connective test to cover
  the silent-on-clean case the original test intended.

### Phase 3 Completion
**Completed:** 2026-07-12
**Changes made:**
- `src/agentic_mbse/sysml/types.py`: retired `L6_CONSTRAINT_NON_EXECUTABLE`, added
  `L6_CONSTRAINT_INELIGIBLE`.
- `src/agentic_mbse/validation/level4_constraints.py`: deleted `check_constraint_coverage` and its
  caller surface; added `eligibility_coverage_metrics()` (admit/block/unassessed counts + admit-rate
  percentage over admit+block, unassessed reported separately per spec's Open Questions); dropped the
  now-unused `get_qualified_name`/`get_element_location` imports.
- `src/agentic_mbse/validation/level6_architecture.py`: `check_constraint_executability` body replaced
  — `extract_constraint_facts` → `evaluate_profile`, one WARNING per blocked-decision diagnostic
  (construct + reason in the message, `_format_diagnostic_location` for the location string); admitted/
  unassessed emit nothing. No `except` around extraction (loud-on-failure preserved). Dropped the
  now-unused `EXCLUDED_CONSTRAINT_TYPES` import; updated the metrics-dict key.
- Created `tests/fixtures/item4_subtype/l6_ineligible/blocked.sysml`: a deterministic blocked-construct
  fixture (predicate-body feature chain), reused by both the item4_subtype and item12 C3 tests per the
  plan's "one fixture" instruction.
- Rewrote `tests/test_validation/test_item4_subtype.py::TestLevel6NonExecutableWarn`: `affordable`/
  `positive_cost`/`widget_budget` now silent (admitted/unassessed); new `test_blocked_construct_warns`
  against the new fixture; kept `test_clean_model_silent` and `test_fails_loud_on_extraction_error`.
- Rewrote `tests/test_validation/test_item12_checks.py`'s C3 section: `test_c3_admitted_constraint_is_
  silent` (repoints the old `constraint_model` fixture's expectation — clean `<=` now admits) plus
  `test_c3_blocked_construct_warns_not_fails` (loads the item4_subtype fixture directly via
  `discover_sysml_files`, not `load_fixture`, since it lives outside `tests/fixtures/item12/`).
- Updated the two L4 label assertions in `tests/test_sysml_quality_checks.py` (`TestLevel4Constraint
  Coverage.test_coverage_metrics_reported`, `TestLevelDistinctness.test_l4_reports_constraint_metrics`)
  to the new eligibility-metric keys.

**Issues encountered / deviations:** none beyond what the plan anticipated (the WARN-flip hazard). The
observe-then-assert step matched the plan's prediction exactly: `affordable`/`positive_cost`/
`within_limit` are all clean unitless-Real comparisons and are now silently admitted.

**Manual validation:** `uv run agentic-mbse validate --level=4 tests/fixtures/distinctness/l6_architecture`
(the plan's path didn't exist; located the real fixture) shows the eligibility metrics and passes;
`uv run agentic-mbse validate --level=6 tests/fixtures/item4_subtype/l6_ineligible` shows exactly one
named `L6_CONSTRAINT_INELIGIBLE` WARN (`block_feature_chain`) and the level still passes.

### Phase 4 Completion
**Completed:** 2026-07-12
**Changes made:**
- Created `.project/active/executable-profile/sysml-codegen-wiring.md`: the ready-to-apply brief,
  grounded in direct inspection of the sysml-codegen checkout (not written generically from this
  repo's design docs alone) — exact seam (`constraint_lowering.py:399-401` inside
  `lower_constraints()`), exact import/edit diff, the halt exception to reuse
  (`CodeGenerationError`), the version-pin reasoning, and four specified tests.
- The de-risk spike question (B2/MF1: does one parsed `ConstraintFacts` reach both gate and
  compiler, or is there a second parse/re-serialize between them?) was answered by inspection
  rather than deferred: today, yes — single build, no re-parse — so the in-process object-identity
  arm applies. The brief flags the serialization-equality arm as the one that becomes load-bearing
  once Item 7's Kleene compiler (not yet built) reads `ConcreteConstraint.predicate_ir`, a string.

**Issues encountered / deviations:**
- The plan's stated deliverable path (`briefs/sysml-codegen-preflight.md`) collided with this
  item's own `briefs/` directory, which holds the orchestrator's own stage artifacts
  (spec.md/design.md/plan.md/implement.md for this item), not deliverables. Followed the
  orchestrator's explicit brief instead, which named the correct path
  (`sysml-codegen-wiring.md`, no `briefs/` prefix) — recorded here so the discrepancy is visible,
  not silently resolved.
- Found and fixed a pre-existing formatting artifact at the end of this file (a stray
  `</content>`/`</invoke>` tail, apparently leaked from whatever tool produced an earlier revision)
  while adding this section.

**agentic-mbse-side validation:** none required — Phase 2 already exports the full surface this
brief consumes (`preflight`, `evaluate_profile`, `PROFILE_SEMANTIC_VERSION`), verified by that
phase's own tests. No code change in this repo for Phase 4.

---
**Status:** Complete

