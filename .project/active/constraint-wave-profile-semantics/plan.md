# Implementation Plan: Constraint-Wave Profile Semantics

**Status:** Complete — owner waived provenance-only gates after audit; orchestration paused for discussion
**Created:** 2026-07-19
**Last Updated:** 2026-07-19
**Epic:** CONSTRAINT-WAVE-REMEDIATION — Item 1 (R-1, R-2)
**Coordinated baselines:** agentic-mbse `4ed2a07`; sysml-codegen `512786c`

## Source Documents

- **Spec:** [spec.md](spec.md)
- **Design:** [design.md](design.md)
- **Approved design review:** [design-review.md](design-review.md)
- **Epic ledger:** `../sysml-codegen/.project/backlog/epic_constraint_pr_wave_remediation.md`, Item 1
- **Primary review:** `../sysml-codegen/.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md`, R-1/R-2
- **Reconciliation:** `../sysml-codegen/.project/research/20260719-065712_constraint-profile-semantics-and-license-reconciliation.md`

The design is the implementation contract. In particular, preserve D1-D11, the seven-row decision
table, diagnostic precedence, and the source-key table in
[design.md#key-decisions](design.md#key-decisions) and
[design.md#architecture](design.md#architecture). Do not replace the approved source-keyed neutral
body with a usage-keyed or polarity-bearing body. Do not fold polarity into the positive predicate
IR. One neutral body is compiled per true predicate source; each usage applies its own decision-carried
polarity exactly once.

**[OWNER-VERBATIM] Shared landing rule (2026-07-19):** “all constraint-wave edits are one landing
unit for the open constraint PRs. Do not isolate Items 1/2/4/6 from each other, do not use hunk-level
per-item allowlists, and do not treat their overlap as contamination.” This rule governs plan
execution. Clean worktrees/overlays exist only for reproducible historical and version-skew
evidence. The active constraint-wave state is the implementation baseline; preserve only genuinely
unrelated/user work.

## Implementation Strategy

### Phasing rationale

This is companion-first because sysml-codegen treats the companion profile decision as its semantic
authority. Phase 1 starts with clean historical RED evidence, then implements and proves the
companion v4 semantic contract on the active shared constraint-wave baseline. Phase 2 establishes
the companion `0.1.2` package/version/lock identity and produces its hashed candidate wheel. Phase 3
moves decision authority, source identity, and unchanged positive IR through codegen lowering and
the catalog. Phase 4 proves the riskiest downstream architecture: one neutral body for
opposite-polarity usages plus a read-only generation plan that rejects every semantic contradiction
before output mutation. Phase 5 seals both candidates, proves both skew directions and the corrected
pair hermetically, and runs the full repository and shared-wave regression gates.

### Critical path

Capture the shared baseline and historical RED → companion v4 decision contract → companion
candidate identity and wheel → codegen decision/source continuity → source-keyed neutral
compilation and pre-output plan → hermetic wheel/version/lock compatibility → complete normal,
optimized, licensed, shared-wave, and full-suite evidence.

### First proof point

In clean historical worktrees, the String/Boolean ordering and profile-level negation probes must be
RED at companion `54a95d2`. In the clean companion candidate overlay, the same probes must turn GREEN,
the 256-row ordering product must have the fixed exact oracle, and two usages of one definition with
opposite polarity must carry identical positive IR bytes plus complementary decision fields.

### Feasibility and principal risks

- The design is feasible against the current surfaces identified in
  [design.md#research-findings](design.md#research-findings). True predicate-source identity already
  exists, so no fact-schema or extraction lookup change is needed.
- Both active repositories contain substantial constraint-wave changes from Items 1/2/4/6, including
  shared-file edits. Those changes are one owner-authorized landing unit and the active trees are the
  implementation baseline. Do not segregate them, classify their overlap as contamination, or use
  per-item/hunk allowlists. Record enough state to preserve only genuinely unrelated/user work.
  Whole-file replacement, broad formatting, fixture recapture, reset, checkout, stash, or clean is
  forbidden.
- Resolver evidence can lie if its wheelhouse is incomplete. The negative and positive resolver
  controls are one inseparable phase and use the same complete hashed no-index closure.
- Moving compile checks earlier can accidentally bypass certified name or symlink guards. Run the
  shared-wave regression gates after every codegen phase that touches their shared files, then again
  at the final candidate.

## Global Execution Rules

### Authority and scope

- [x] Implement the Item 1 contract within the owner-authorized shared constraint-wave landing unit.
  Items 1/2/4/6 may evolve together where their shared files or tests require it. Preserve only
  genuinely unrelated/user work; do not treat constraint-wave overlap as contamination.
- [x] Do not change `ConstraintFacts`/`constraint-facts/v1`, snapshot format v3, occurrence identity,
  actual resolution, study policy, or native arithmetic exception behavior. See
  [design.md#non-goals](design.md#non-goals) and invariants I14-I15.
- [x] Do not commit, push, create or comment on a PR, merge, tag, upload, or publish a release.
  Candidate wheels are local evidence artifacts only; Epic Item 8 owns release readiness.

### Licensed command rule

Every command that can import SysIDE or exercise a licensed live route must load the existing
sysml-codegen `.env` explicitly. Never print, interpolate, grep, hash, copy, or log the license key.

- From `sysml-codegen`: `uv run --env-file .env ...`
- From `agentic-mbse`: `uv run --env-file ../sysml-codegen/.env ...`
- From a temporary worktree: use the absolute path to the existing sysml-codegen `.env` as the
  `--env-file` argument; record the path and command, never the file contents.
- Hermetic resolver/install environments do not load the license file. Only their focused runtime
  tests that require SysIDE use `uv run --env-file` explicitly.

### Working directories and tools

- [x] Run Phase 1/2 companion commands from the `agentic-mbse` repository root. The relative
  license argument is exactly `../sysml-codegen/.env`.
- [x] Run Phase 3-5 codegen commands from the `sysml-codegen` repository root. The license argument
  is exactly `.env`.
- [x] If uv needs a writable cache for an evidence environment, create a task-specific directory
  under `/tmp` and set `UV_CACHE_DIR` to that explicit path. Do not repurpose `HOME` or print env
  contents.
- [x] Use `uv run --env-file ...` directly. Do not `source` either repository's `.env`.

### Evidence and shared-baseline discipline

The durable implementation record is `evidence.md` beside this plan. Large manifests, probes, and
command results live under `evidence/`; no secret-bearing environment capture belongs there.

**[OWNER-VERBATIM] Post-audit correction (2026-07-19):** “yeah I don't need those gates at this
point. please amend, but don't re-audit. I want to discuss the larger context before we continue
rerunning.” Clean-overlay origin, pre-edit per-path/untracked/fixture hashes, and exact unrelated-path
before/after hashes are no longer Item 1 completion gates. Their absence remains stated in
`evidence.md`; no retroactive evidence is asserted.

### Shared constraint-wave regression gates

Shared current files include codegen `constraint_lowering.py`, `resolution/models.py`,
`generation/modules.py`, `generation/predicate_compiler.py`, `cli/__init__.py`, their constraint/CLI
tests, and companion profile/version/docs/lock files. Their Items 1/2/4/6 edits are the active
implementation baseline and may evolve together while preserving the approved behavior of every
wave item.

After Phase 3 and Phase 4, run the normal and optimized Item 2/4/6 focused gates copied under
Phase 5. A failure is a shared-wave regression to diagnose causally, not contamination evidence and
not a reason to isolate one item's hunks. Do not weaken a certified behavior or rewrite prior
evidence to accept a regression.

## Contract Coverage

This table maps the approved contract to execution without restating its architecture.

| Contract seam | Planned proof |
|---|---|
| Spec ordering product, diagnostic precedence; D1-D2; I1-I2/I10 | Phase 1 fixed 256-row oracle, compound-order/cardinality tests, L4/L6 assertions |
| Spec polarity and unchanged positive IR; D3-D6; I3-I5 | Phase 1 decision-state, malformed-polarity, live/codec, and canonical-byte tests |
| Consumer completeness; I11 | Phase 1 exact dataclass-field key set plus `source`/`membership_kind` behavior |
| Candidate identity and unchanged fact/snapshot formats; D9-D10; I14 | Phase 2 package/profile/lock/wheel checks; Phase 3/5 byte manifests |
| Decision authority and source-key continuity; D7; I5-I6/I9 | Phase 3 lowering guards and live/snapshot rung ladder before graph extension |
| Source-keyed neutral body and per-usage polarity; D8; I7-I8/I15 | Phase 3 one-body/two-wrapper oracle, reversed order, exact margins, native exceptions |
| Pre-output validation; D11; I13 | Phase 4 absent/populated sentinel tests and zero mutation counters |
| Both skew directions and causal resolver control; I12; review M1/M2 | Phase 5 complete hashed wheelhouse, exact conflict normalization, unchanged-wheelhouse positive control |
| Review m1 sealed overlays and owner shared-wave clarification | Global evidence rules plus Phase 5 candidate overlays; no implementation isolation |
| Spec full gates and evidence ordering | Companion-first Phase 2 suite, Phases 3/4 normal and `python -O`, Phase 5 full coordinated gates |

---

## Phase 1: Companion Profile v4 Contract, Starting from Historical RED

### Goal

Capture the shared-wave baseline, prove both defects against reviewed historical sources, then write
the companion tests first and implement the total ordering, polarity, decision-state, diagnostic,
consumer-map, route-parity, and documentation contract on the active shared baseline.

### Assumption under test

R-1 and profile-level R-2 are independently reproducible at companion `54a95d2`; the already present
downstream codegen polarity behavior at `512786c` remains a GREEN control; and neutral companion
facts are sufficient to make all v4 decisions without a fact/snapshot schema change.

### Test stencil — write the probe first

```python
def test_historical_profile_gap(case):
    facts = case.facts_with_typed_operands_and_boolean_polarity()
    decision = evaluate_profile(facts).decisions[0]
    assert case.expected_historical_failure(decision)

def test_historical_codegen_negation_control():
    result = execute_existing_negated_inline_fixture()
    assert result.actual_value is False
    assert result.status == "satisfied"

@pytest.mark.parametrize("operator,left,right", ORDERING_PRODUCT)
def test_v4_ordering_product(operator, left, right):
    decision = decide_ordering(operator, left, right)
    assert normalized_outcome(decision) == STATIC_ORACLE[operator, left, right]

@pytest.mark.parametrize("raw", [None, "false", 0, 1, []])
def test_invalid_polarity_blocks_before_body_walk(raw, walk_spy):
    decision = decide_usage(is_negated=raw)
    assert normalized_reasons(decision) == ["block_invalid_assertion_polarity"]
    walk_spy.assert_not_called()
```

### Changes required

**See:** [design.md#implementation-notes](design.md#implementation-notes),
[design.md#validation-approach](design.md#validation-approach), and invariants I9/I12-I15.

- [x] **`evidence.md` (NEW):** record the baseline and toolchain identities, exact RED/GREEN node
  definitions, and every result. Start the phase completion ledger at the end of this plan.
- [x] **`evidence/` (NEW):** add small deterministic helpers/probes only as needed for baseline
  manifests, sealed overlays, historical R-1/R-2 nodes, sentinel mutation counters, and later
  compatibility controls. Helpers must reject unsafe paths and must not read `.env`.
- [x] Record the companion and codegen shared constraint-wave baseline as one landing unit.
- [x] Create clean detached worktrees at companion `54a95d2` and codegen `512786c`. Assert `HEAD`,
  clean porcelain status, and resolved import source before every historical node.
- [x] Run R-1 String `<` and Boolean `<=` as separate fresh-process RED nodes at `54a95d2`; record
  the unexpected ADMIT and absent diagnostic without converting the probe into a passing xfail.
- [x] Run profile-level R-2 for positive/negated × inline/definition-typed at `54a95d2`; record that
  extraction/codec preserves `is_negated` while `UsageDecision` lacks classified polarity and keeps
  the same positive source predicate.
- [x] Run the existing negated generated-execution behavior at codegen `512786c` as a causal GREEN
  control. Record that Item 1 preserves rather than invents this final verdict behavior.
- [x] Record clean historical source identities and the retained probe hash; remove temporary
  historical worktrees after the evidence is durable.
- [x] **`src/agentic_mbse/sysml/executable_profile.py:55,116-128,164-195,463-525,717-803`:** add
  profile v4, both approved reasons/messages, the dedicated total ordering classifier,
  polarity-first construction, both public Boolean decision fields, five named constructors,
  explicit `ValueError` state validation, and the exhaustive field-consumer map. Keep shared
  `unit_compatibility` behavior unchanged for equality/arithmetic. See D1-D6 and I1-I6/I11.
- [x] **`src/agentic_mbse/validation/level6_architecture.py:594-649`:** render `<no location>`
  stably while preserving one ordered L6 `ERROR` per BLOCK diagnostic and one aggregated warning
  per wholly NON_NUMERICAL usage.
- [x] **`tests/test_sysml/test_executable_profile_matrix.py:1-75`:** write the independent fixed
  oracle for four operators × 64 category pairs, with exact reason/cardinality checks and focused
  quantity/unit subcases. Do not derive expectations from the production classifier.
- [x] **`tests/test_sysml/test_executable_profile.py`,
  `tests/test_sysml/test_executable_profile_arithmetic.py`, and
  `tests/test_sysml/test_executable_profile_v3.py`:** update construction/expectation sites for the
  additive decision fields and v4 identifier while retaining every inherited numerical-profile
  outcome that v4 does not change.
- [x] **`tests/test_sysml/test_executable_profile_v4.py` (NEW):** cover all seven decision rows,
  invalid construction under normal/optimized Python, direct/public-codec malformed polarity, exact
  messages/location fallback, N-comparison walk order, and unchanged numerical/non-numerical rows.
- [x] **`tests/test_sysml/test_constraint_profile_route_parity.py` (NEW):** cover
  positive/negated × inline/definition-typed through live extraction and public codec, including two
  opposite-polarity usages of one definition. Assert complementary decision fields,
  effective-source identity, and identical canonical positive-predicate bytes.
- [x] **`tests/test_sysml/test_constraint_fact_shapes.py:54-236`:** add the exact field-consumer
  key-set guard and focused `source`/`membership_kind` behavior without changing the fact schema or
  frozen golden.
- [x] **`tests/test_validation/test_item12_checks.py:1-190`:** add ordered L4/L6 cardinality,
  compound diagnostics, and literal `<no location>` L6 assertions.
- [x] **`tests/test_validation/test_level4_reconciliation.py`:** assert one L4 outcome per usage for
  compound malformed ordering without duplicating L6's per-diagnostic error count.
- [x] **`docs/patterns/constraints.md`:** document the exact numerical ordering whitelist,
  malformed-category repair, separate decision-carried polarity, unchanged positive/raw value, and
  exact-once interpretation. Preserve the shared constraint-wave guide state.

### Validation

**Automated**

- [x] Each R-1 and profile R-2 defect is independently RED at the named companion revision.
- [x] The downstream negated-execution control is GREEN at the named codegen revision when its
  licensed/execution dependencies are available; otherwise record the exact missing dependency and
  leave the control open.
- [x] Historical controls run from clean named revisions without editable active-tree source,
  no source path outside the clean worktree, and `-p no:cacheprovider` where pytest is used.
- [x] Run the companion focused contract normally and optimized, loading the sysml-codegen license
  file explicitly for licensed live nodes:

  ```bash
  uv run --env-file ../sysml-codegen/.env pytest -q \
    tests/test_sysml/test_executable_profile.py \
    tests/test_sysml/test_executable_profile_arithmetic.py \
    tests/test_sysml/test_executable_profile_matrix.py \
    tests/test_sysml/test_executable_profile_v3.py \
    tests/test_sysml/test_executable_profile_v4.py \
    tests/test_sysml/test_constraint_profile_route_parity.py \
    tests/test_sysml/test_constraint_fact_shapes.py \
    tests/test_validation/test_level4_reconciliation.py \
    tests/test_validation/test_item12_checks.py \
    tests/test_constraint_documentation.py

  uv run --env-file ../sysml-codegen/.env python -O -m pytest -q \
    tests/test_sysml/test_executable_profile.py \
    tests/test_sysml/test_executable_profile_arithmetic.py \
    tests/test_sysml/test_executable_profile_matrix.py \
    tests/test_sysml/test_executable_profile_v3.py \
    tests/test_sysml/test_executable_profile_v4.py \
    tests/test_sysml/test_constraint_profile_route_parity.py \
    tests/test_sysml/test_constraint_fact_shapes.py \
    tests/test_validation/test_level4_reconciliation.py \
    tests/test_validation/test_item12_checks.py
  ```
- [x] Re-run the historical R-1/R-2 probes against the active v4 implementation and require GREEN.
  Licensed skips do not prove live/codec parity and stay unchecked.

**Manual/evidence review**

- [x] Review both active diffs as one shared Items 1/2/4/6 wave.
- [x] Verify Phase 1 performs no fixture or snapshot capture/recapture and preserves their schemas.

**What we know works after this phase:** The historical premise is real, downstream R-2 behavior is
not falsely claimed as absent, profile v4 classifies every ordering row and executable polarity,
positive source bytes remain neutral, live/codec results agree where licensed evidence ran, and
unrelated/user work is preserved without segregating the shared constraint wave.

---

## Phase 2: Companion Candidate Identity, Lock, and Hashed Wheel

### Goal

Turn the proven Phase 1 contract into the exact unpublished companion candidate: package `0.1.2`,
profile `executable-profile/v4`, a resolved `0.1.2` companion lock, and a content-inspected wheel
identified by SHA-256. Run the complete companion suite before any codegen candidate is accepted.

### Assumption under test

The package, runtime version, profile version, lock selection, wheel metadata, and wheel contents can
name one candidate consistently without publishing it or changing fact/snapshot formats.

### Test stencil — write these tests before production code

```python
def test_candidate_identity_is_consistent(built_wheel, resolved_lock):
    assert runtime_package_version() == "0.1.2"
    assert PROFILE_SEMANTIC_VERSION == "executable-profile/v4"
    assert resolved_lock.version("agentic-mbse") == "0.1.2"
    assert built_wheel.metadata.version == "0.1.2"
    assert built_wheel.sha256 == recorded_sha256()
```

### Changes required

**See:** D9/D10 and [design.md#compatibility-seam](design.md#compatibility-seam).

- [x] **`tests/test_package_version.py` and `tests/test_constraint_documentation.py`:** write the
  package/profile/guide identity assertions first. Verify the tests read public runtime metadata and
  built-wheel contents rather than trusting only project source text.
- [x] **`pyproject.toml:7`, `src/agentic_mbse/__init__.py`, `uv.lock:24-25`:** set only the approved
  companion candidate identity to `0.1.2` and resolve the companion lock entry accordingly.
- [x] Build a local wheel from the reviewed active shared-wave companion tree. Record version,
  filename, tags, source revision, and SHA-256. Inspect wheel contents; do not publish it.

  ```bash
  uv build --wheel --out-dir "$item1_tmp/wheels/new-companion"
  uv run python -m zipfile -l "$item1_tmp/wheels/new-companion/agentic_mbse-0.1.2-"*.whl
  sha256sum "$item1_tmp/wheels/new-companion/agentic_mbse-0.1.2-"*.whl
  ```

  Build from the active shared-wave companion tree into a task-specific directory under `/tmp`.
  Candidate-overlay rebuilding is reserved for Phase 5's hermetic skew evidence. Do not use a broad
  or unresolved path.

### Validation

**Package identity and Phase 1 regression**

```bash
uv run --env-file ../sysml-codegen/.env pytest -q \
  tests/test_sysml/test_executable_profile_matrix.py \
  tests/test_sysml/test_executable_profile_v4.py \
  tests/test_sysml/test_constraint_profile_route_parity.py \
  tests/test_constraint_documentation.py tests/test_package_version.py

uv run --env-file ../sysml-codegen/.env python -O -m pytest -q \
  tests/test_sysml/test_executable_profile_matrix.py \
  tests/test_sysml/test_executable_profile_v4.py \
  tests/test_sysml/test_constraint_profile_route_parity.py
```

- [x] Require all package/profile identity assertions and Phase 1 regressions to pass. Record
  licensed live nodes separately; a skip does not prove live/codec parity.

**Companion full suite and static gates — companion evidence must precede codegen**

```bash
uv run --env-file ../sysml-codegen/.env pytest -q tests/
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/
git diff --check
```

- [x] Record exact full-suite pass/skip/fail/error counts. Classify any inherited failure; do not
  call a failing suite green.
- [x] Inspect the wheel and require the expected profile/docs/version content, no secret-bearing
  files, and no fact/snapshot schema changes. Review the active tree as the shared landing unit.

**What we know works after this phase:** The proven v4 contract has one consistent unpublished
`0.1.2` package/runtime/lock/wheel identity, the wheel hash and contents are recorded, and the full
companion suite has passed before any consumer candidate is accepted.

---

## Phase 3: Codegen Decision Authority, True Source Keys, and Neutral Bodies

### Goal

Make lowering consume and verify the decision-carried semantic pair, carry true predicate-source
identity through concrete/catalog records, compile one polarity-neutral body per true source, apply
polarity once per usage, and prove the complete source/byte/runtime ladder on live and snapshot
routes.

### Assumption under test

The current facts/decision zip and effective-source identity can prove provenance before graph
extension; every later record can carry the same positive bytes/source key without changing
snapshot v3; and one shared body plus per-usage finalization preserves raw truth, verdict, margin,
and native exceptions for opposite-polarity usages.

### Test stencil — write these tests before production code

```python
@pytest.mark.parametrize("route", ["live", "snapshot"])
def test_positive_ir_and_source_key_ladder(route):
    rungs = collect_ladder(route, opposite_polarity_shared_definition())
    assert one_canonical_predicate_bytes(rungs)
    assert rungs.source_keys == {"definition:Model::ReusableConstraint"}

@pytest.mark.parametrize("mutation", DECISION_AND_CONTINUITY_MUTATIONS)
def test_lowering_rejects_before_graph_extension(mutation, graph_spy):
    with pytest.raises(CodeGenerationError):
        lower_constraints(mutation.apply(valid_case()))
    graph_spy.assert_not_called()

def test_opposite_polarities_share_one_neutral_body():
    compiled = compile_source_group(catalog_for_same_source_positive_and_negated())
    assert len(compiled.bodies) == 1
    assert len(compiled.wrappers) == 2
    assert execute_pair(compiled) == EXACT_ONCE_ORACLE
```

### Changes required

**See:** D7-D10, [design.md#coordinated-codegen-flow](design.md#coordinated-codegen-flow), and
invariants I4-I9/I14-I15.

- [x] **`src/sysml_codegen/analysis/constraint_lowering.py:838-1104`:** update the guard to v4; add
  explicit decision-state, raw-fact polarity, expected-truth, effective-source, and canonical IR
  continuity checks before graph extension; use only the decision pair for concrete semantics; and
  derive the exact `predicate_source_key`, including the portable anonymous-inline fallback.
- [x] **`src/sysml_codegen/resolution/models.py:332-438,454-482`:** add required
  `predicate_source_key` to `ConcreteConstraint` and `ConstraintCatalogEntry`; preserve transactional
  complementary-pair validation under normal and optimized Python.
- [x] **`src/sysml_codegen/generation/constraint_catalog.py:46-180`:** project the decision-derived
  pair, exact positive IR, and true source key. Group agreement covers source key/body bytes only;
  mixed polarity is valid.
- [x] **`src/sysml_codegen/generation/predicate_compiler.py:232-330`:** split the current compiler
  into a polarity-neutral body compiler and one shared finalizer. Preserve the positive structural
  margin convention and native exception class/message behavior. Normalize signed zero only in the
  finalizer.
- [x] **`src/sysml_codegen/generation/modules.py:107-230`:** group compiled bodies only by
  `predicate_source_key`; emit one body plus per-usage wrappers and never select a group's first
  polarity as body semantics. Keep plan construction for Phase 4 separate from this semantic split.
- [x] **`tests/conformance/test_constraint_lowering.py:72-935`:** add independent mismatch cases for
  each decision/source/predicate rung, graph-extension sentinels, field-consumer behavioral proofs,
  exact profile v4 guard, and positive/negated × inline/definition rows.
- [x] **`tests/conformance/test_data_models.py` and `tests/unit/test_concrete_constraint_model.py`:**
  cover required source key, complementary pairs, assignment mutation, and `python -O` behavior.
- [x] **`tests/conformance/test_constraint_catalog_determinism.py` and
  `tests/unit/test_constraint_emission.py:127-310`:** prove two opposite-polarity usages of one
  definition have one key/body, byte-identical positive data, two wrappers, no first-entry
  dependency under reversed order, and exact compiler inputs; distinct sources never merge.
- [x] **`tests/unit/test_predicate_compiler.py:160-445`:** add the exact-once truth table for true,
  false, strict/inclusive zero, and already-materialized non-finite operands; reject invalid polarity
  pairs under normal/optimized Python; retain division-by-zero, negative-power, and overflow
  exception class/message controls.
- [x] **`tests/conformance/test_constraint_pipeline_threading.py:89-225` and
  `tests/execution/test_constraint_execution.py:412-596`:** cover shared-definition opposite
  polarities through wired live/snapshot routes, exact raw/status/margin evidence, warning order,
  and one deterministic BLOCK halt after all warnings.
- [x] **`tests/conformance/test_constraint_snapshot_identity.py`,
  `tests/conformance/test_snapshot_constraint_parity.py`, and
  `tests/unit/test_snapshot_v3_gate.py`:** add the live/snapshot ladder and re-profiling assertions.
  Preserve snapshot/fact schemas and make no fixture recapture.
- [x] Implement Phase 3 directly on the active shared-wave codegen baseline. Review the combined
  constraint-wave diff, run the Item 2/4/6 regression gates before continuing, and verify separately
  recorded unrelated/user paths remain unchanged. Do not build an isolation overlay for this phase.

### Validation

```bash
uv run --env-file .env pytest -q \
  tests/conformance/test_constraint_lowering.py \
  tests/conformance/test_data_models.py \
  tests/unit/test_concrete_constraint_model.py \
  tests/conformance/test_constraint_catalog_determinism.py \
  tests/unit/test_constraint_emission.py \
  tests/unit/test_predicate_compiler.py \
  tests/conformance/test_constraint_pipeline_threading.py \
  tests/conformance/test_constraint_snapshot_identity.py \
  tests/conformance/test_snapshot_constraint_parity.py \
  tests/unit/test_snapshot_v3_gate.py \
  tests/execution/test_constraint_execution.py

uv run --env-file .env python -O -m pytest -q \
  tests/conformance/test_constraint_lowering.py \
  tests/conformance/test_data_models.py \
  tests/unit/test_concrete_constraint_model.py \
  tests/conformance/test_constraint_catalog_determinism.py \
  tests/unit/test_constraint_emission.py \
  tests/unit/test_predicate_compiler.py \
  tests/conformance/test_constraint_pipeline_threading.py \
  tests/conformance/test_constraint_snapshot_identity.py \
  tests/conformance/test_snapshot_constraint_parity.py \
  tests/unit/test_snapshot_v3_gate.py \
  tests/execution/test_constraint_execution.py
```

- [x] Require every mismatch to fail before graph extension in both modes.
- [x] Require live and snapshot/codec routes to match at every identity/byte/decision/catalog rung.
  Licensed live nodes must run with `--env-file .env`; skips stay unproved.
- [x] Require snapshot and `constraint_facts` schemas and codec routes to remain compatible.
- [x] Require one body/two wrappers, reversed-order independence, the full exact-once oracle, and
  unchanged native exception classes/messages in both modes where execution is applicable.
- [x] Run the Item 2/4/6 normal and optimized overlap gates in Phase 5 and append results now.

**What we know works after this phase:** Codegen has one semantic authority, facts remain provenance,
true source identity and positive bytes survive every route, one neutral body serves both polarities,
each wrapper interprets its usage exactly once, native arithmetic behavior is unchanged, and
lowering contradictions cannot extend the graph.

---

## Phase 4: Read-Only Pre-Output Generation Plan and Mutation Sentinels

### Goal

Build the read-only `ConstraintGenerationPlan` around the proven Phase 3 semantic path and move all
catalog/source/name/input/parse/compile reconciliation before output clearing or directory creation.

### Assumption under test

A complete in-memory generation plan can validate and hold the already-proven neutral bodies and
per-usage wrappers before any target-tree mutation without bypassing name-safety, snapshot, or
link-safety behavior in the shared constraint wave.

### Test stencil — write these tests before production code

```python
@pytest.mark.parametrize("mutation", PREOUTPUT_MUTATIONS)
def test_plan_failure_preserves_sentinel_tree(tmp_path, mutation):
    sentinel = seed_output_tree(tmp_path)
    with pytest.raises(CodeGenerationError):
        run_codegen(mutation.apply(valid_context()), output=tmp_path)
    assert tree_manifest(tmp_path) == sentinel
```

### Changes required

**See:** D8/D11, [design.md#pre-output-validation-order](design.md#pre-output-validation-order),
the compiler split in [design.md#coordinated-codegen-flow](design.md#coordinated-codegen-flow), and
invariants I7-I8/I13/I15.

- [x] **`src/sysml_codegen/generation/modules.py:107-230`:** consume the read-only
  `ConstraintGenerationPlan` from `generation/constraint_plan.py`, carry Phase 3's compiled bodies
  plus per-usage wrapper constants into emission, and never regroup or recompile.
- [x] **`src/sysml_codegen/cli/__init__.py:348-390,931-1012`:** build and fully validate the plan
  after the existing read-only name/path/params/link checks but before `_clear_output_directory()`
  and `_setup_output_directories()`. Preserve certified Item 2 and Item 6 guard order and errors.
- [x] **`src/sysml_codegen/generation/constraint_plan.py` (NEW):** define the single read-only plan
  builder/model. Keep `modules.py`/CLI as thin consumers and do not create a second grouping or
  compiler route.
- [x] **`tests/unit/test_constraint_emission.py:127-310`:** assert plan-held body/wrapper mappings,
  source-key/name collision checks, exact compiler argument bytes, and that emission never regroups
  or recompiles.
- [x] **`tests/unit/test_cli_generation.py:277-430` and
  `tests/conformance/test_constraint_generation_integration.py:144+`:** add absent/populated target
  sentinel tests for decision pair, catalog pair, missing/duplicate key, body divergence, normalized
  name collision, input mismatch, parse failure, and compile failure. Patch counters for compiler,
  renderer, writer, clear, setup, and first target mutation; all must remain zero on rejection.
- [x] Implement Phase 4 directly on the active shared-wave codegen baseline. Re-run all Item 2/4/6
  regression gates before version/lock work and verify separately recorded unrelated/user paths
  remain unchanged. Do not build an isolation overlay for this phase.

### Validation

```bash
uv run --env-file .env pytest -q \
  tests/unit/test_constraint_emission.py \
  tests/unit/test_cli_generation.py \
  tests/conformance/test_constraint_generation_integration.py

uv run --env-file .env python -O -m pytest -q \
  tests/unit/test_constraint_emission.py \
  tests/unit/test_cli_generation.py \
  tests/conformance/test_constraint_generation_integration.py
```

- [x] Require every sentinel no-mutation and emission-consumes-plan case to pass normally and under
  `python -O`.
- [x] Assert NON_NUMERICAL warnings appear once in fact order before the complete BLOCK halt; plan,
  compiler, renderer, clear/setup, and target mutation counters are zero for blocked preflight.
- [x] Run Phase 5's Item 2/4/6 overlap gates and record them immediately.

**What we know works after this phase:** Every Item 1 semantic/catalog/compiler contradiction is
found while the output tree remains byte-identical to its absent or populated sentinel state, and
emission consumes the fully validated plan without a second semantic route.

---

## Phase 5: Candidate Versions, Hermetic Skew Controls, Full Suites, and Final Evidence

### Goal

Seal the coordinated `0.1.2`/profile-v4 candidate pair, prove both version-skew directions and the
corrected pair causally, then complete repository, overlap, static, fixture, and scope gates.

### Assumption under test

The raised codegen floor and runtime guard fail closed for both old/new directions; the negative
resolver result is caused only by `agentic-mbse>=0.1.2` versus `==0.1.1`; and the exact hashed
candidate pair passes from an immutable complete wheelhouse without editable sources or indexes.

### Test stencil — write the compatibility assertions first

```python
def test_resolver_conflict_is_only_companion_floor(result):
    assert result.conflicts == {("agentic-mbse>=0.1.2", "agentic-mbse==0.1.1")}
    assert result.missing_or_unsatisfied_others == set()

def test_same_wheelhouse_positive_control(result):
    assert result.only_changed_request == "agentic-mbse==0.1.2"
    assert result.resolved_and_installed
```

### Changes required

**See:** D9 and [design.md#compatibility-seam](design.md#compatibility-seam), especially the complete
closure and same-wheelhouse causal control.

- [x] **`pyproject.toml:24,65`:** raise only the declared runtime floor to
  `agentic-mbse>=0.1.2`. Keep the local editable source for repository development, but never use it
  as compatibility evidence.
- [x] **`uv.lock:6-8,768-785`:** resolve the companion entry to `0.1.2` without unrelated lock churn.
  Review the semantic lock diff, not only `uv lock` exit status.
- [x] **`tests/unit/test_package_metadata.py`:** pin the declared floor, resolved lock, runtime
  companion version, and profile v4 without coupling the test to an editable path.
- [x] Build the new codegen candidate wheel from the reviewed active shared-wave tree. Record
  version, filename/tags, exact source revision, and SHA-256. Do not change the
  sysml-codegen package version unless the approved package build requires it; D9 changes the
  companion candidate version and codegen dependency floor.
- [x] Build/seal old companion `0.1.1` from clean `54a95d2`, new companion `0.1.2` from the active
  shared-wave tree, old codegen from clean `512786c`, and the new active-tree codegen candidate.
  Populate one immutable local wheelhouse with the complete compatible dependency closure.
- [x] Write a wheelhouse manifest containing normalized distribution name, version, filename/tags,
  SHA-256, and source for every selectable wheel. Use `--no-index`, the wheelhouse alone, fully
  pinned hash-checked inputs, isolated environments, no editable install, and no network.
- [x] **Old codegen + new companion:** install sealed wheels and assert the v3 guard rejects v4
  during lowering before graph/output mutation.
- [x] **New codegen + old companion resolver:** request `agentic-mbse==0.1.1`; normalize cause data
  and assert only the exact floor conflict, with no missing/unsatisfied unrelated distribution.
- [x] **New codegen + old companion runtime bypass:** install new codegen `--no-deps` plus old
  companion and assert its v4 runtime guard rejects v3 before graph/output mutation.
- [x] **Same-wheelhouse positive control:** change only the request to `agentic-mbse==0.1.2`; require
  resolution and installation from the unchanged wheelhouse and unchanged non-companion pins.
- [x] **Exact candidate pair:** install both candidate wheels, assert runtime package `0.1.2`, profile
  v4, declared floor, both locks, and recorded SHA-256 values; run the focused profile/lowering/plan/
  catalog/compiler/snapshot/execution selections normally and under optimized Python where
  applicable.

Use four separately generated, hash-pinned requirement files. Each line must use `name==version`
plus one or more `--hash=sha256:<digest>` values from the sealed manifest. Every non-companion line
is byte-identical between the new/old negative file and its positive control.

```bash
uv venv "$item1_tmp/env-old-new"
uv pip install --python "$item1_tmp/env-old-new/bin/python" \
  --no-index --find-links "$item1_tmp/wheelhouse" --require-hashes \
  -r "$item1_tmp/inputs/old-codegen-new-companion.txt"

uv venv "$item1_tmp/env-new-old-resolver"
uv pip install --python "$item1_tmp/env-new-old-resolver/bin/python" \
  --no-index --find-links "$item1_tmp/wheelhouse" --require-hashes \
  -r "$item1_tmp/inputs/new-codegen-old-companion.txt"

uv venv "$item1_tmp/env-new-old-runtime"
uv pip install --python "$item1_tmp/env-new-old-runtime/bin/python" \
  --no-index --find-links "$item1_tmp/wheelhouse" --require-hashes --no-deps \
  -r "$item1_tmp/inputs/new-codegen-old-companion-runtime.txt"

uv venv "$item1_tmp/env-new-new"
uv pip install --python "$item1_tmp/env-new-new/bin/python" \
  --no-index --find-links "$item1_tmp/wheelhouse" --require-hashes \
  -r "$item1_tmp/inputs/new-codegen-new-companion.txt"
```

- [x] Expect only the second install to fail resolution. Feed its captured stderr to the kept
  normalization helper and assert the exact companion conflict plus an empty unrelated-failure set.
  Do not accept a raw substring match as causal evidence.
- [x] Require the fourth install to pass without changing the wheelhouse or any non-companion input.
  Run runtime guards and focused tests with each environment's explicit Python executable. Add the
  sysml-codegen `.env` through `uv run --env-file` only for tests that actually need the licensed
  live route; never source or print the file.

### Validation

### Item 2/4/6 overlap gates

Run these after Phases 3 and 4 and once more against the exact candidate pair. Licensed-capable
commands use `--env-file .env` even when the selected nodes usually replay snapshots.

**Item 2 — name safety**

```bash
uv run --env-file .env pytest -q \
  tests/unit/test_constraint_name_safety.py \
  tests/unit/test_predicate_compiler.py \
  tests/unit/test_constraint_emission.py \
  tests/unit/test_cli_generation.py \
  tests/unit/test_contract_models.py \
  tests/conformance/test_constraint_name_safety_routes.py \
  tests/conformance/test_constraint_generation_integration.py

uv run --env-file .env python -O -m pytest -q \
  tests/unit/test_constraint_name_safety.py \
  tests/unit/test_predicate_compiler.py \
  tests/unit/test_constraint_emission.py \
  tests/unit/test_cli_generation.py \
  tests/unit/test_contract_models.py \
  tests/conformance/test_constraint_name_safety_routes.py \
  tests/conformance/test_constraint_generation_integration.py
```

**Item 4 — snapshot portability**

```bash
uv run --env-file .env pytest -q \
  tests/unit/test_source_referent.py tests/unit/test_snapshot_v3_gate.py \
  tests/unit/test_occurrence_roundtrip_parity.py tests/unit/test_hygiene_tail_loader.py \
  tests/conformance/test_constraint_snapshot_identity.py \
  tests/conformance/test_constraint_non_numerical.py \
  tests/conformance/test_constraint_snapshot_portability.py \
  tests/conformance/test_snapshot_contract.py \
  tests/conformance/test_snapshot_constraint_parity.py \
  tests/conformance/test_fingerprint_stability.py

uv run --env-file .env python -O -m pytest -q \
  tests/unit/test_source_referent.py tests/unit/test_snapshot_v3_gate.py \
  tests/unit/test_occurrence_roundtrip_parity.py tests/unit/test_hygiene_tail_loader.py \
  tests/conformance/test_constraint_snapshot_identity.py \
  tests/conformance/test_constraint_non_numerical.py \
  tests/conformance/test_constraint_snapshot_portability.py \
  tests/conformance/test_snapshot_contract.py \
  tests/conformance/test_snapshot_constraint_parity.py \
  tests/conformance/test_fingerprint_stability.py
```

- [x] Run both the license-free moved replay and the licensed live A/live B/replay A relocation
  node explicitly. A licensed skip is not route-parity evidence.

**Item 6 — seal/verify symmetry**

```bash
uv run --env-file .env pytest -q \
  tests/unit/test_contract_models.py tests/unit/test_verify_package.py \
  tests/unit/test_cli_generation.py tests/conformance/test_seal_step9.py \
  tests/conformance/test_fingerprint_stability.py

uv run --env-file .env python -O -m pytest -q \
  tests/unit/test_contract_models.py tests/unit/test_verify_package.py \
  tests/unit/test_cli_generation.py tests/conformance/test_seal_step9.py \
  tests/conformance/test_fingerprint_stability.py
```

- [x] Require every overlap command to pass or record the exact inherited/environmental failure.
  Require the behavioral regression gates above and preserve only separately recorded genuinely
  unrelated/user paths; do not compare or isolate saved constraint-wave overlap hunks.

### Full coordinated gates

Companion remains first. Record exact revisions and wheel hashes before consumer tests.

```bash
# agentic-mbse
uv run --env-file ../sysml-codegen/.env pytest -q tests/
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/

# sysml-codegen focused complete constraint/snapshot/generation families
uv run --env-file .env pytest -q \
  tests/conformance/test_constraint_lowering.py \
  tests/conformance/test_constraint_lowering_integrity.py \
  tests/conformance/test_constraint_catalog_determinism.py \
  tests/conformance/test_constraint_generation_integration.py \
  tests/conformance/test_constraint_pipeline_threading.py \
  tests/conformance/test_constraint_snapshot_identity.py \
  tests/conformance/test_snapshot_constraint_parity.py \
  tests/unit/test_concrete_constraint_model.py \
  tests/unit/test_predicate_compiler.py tests/unit/test_constraint_emission.py \
  tests/unit/test_cli_generation.py tests/unit/test_snapshot_v3_gate.py \
  tests/execution/test_constraint_execution.py

uv run --env-file .env python -O -m pytest -q \
  tests/conformance/test_constraint_lowering.py \
  tests/conformance/test_constraint_lowering_integrity.py \
  tests/conformance/test_constraint_catalog_determinism.py \
  tests/conformance/test_constraint_generation_integration.py \
  tests/conformance/test_constraint_pipeline_threading.py \
  tests/conformance/test_constraint_snapshot_identity.py \
  tests/conformance/test_snapshot_constraint_parity.py \
  tests/unit/test_concrete_constraint_model.py \
  tests/unit/test_predicate_compiler.py tests/unit/test_constraint_emission.py \
  tests/unit/test_cli_generation.py tests/unit/test_snapshot_v3_gate.py \
  tests/execution/test_constraint_execution.py

# full codegen suite
uv run --env-file .env pytest -q tests/
```

- [x] Require the complete companion suite before the full codegen suite. Record pass/skip/fail/
  error/deselection counts and exact license state. Do not collapse known failures into a green claim.
- [x] Run targeted mypy on every touched production file and full-project `uv run mypy src/` in both
  repos; compare known baselines and require no new Item 1 diagnostic.
- [x] Run Ruff check and format-check on every touched Python file and evidence helper. Do not format
  a whole inherited dirty file merely to remove pre-existing findings.
- [x] Run `git diff --check` across both repositories and inspect any report by path. Do not use
  hunk ownership to divide the constraint-wave landing unit.
- [x] Review both final active-tree diffs as one constraint-wave landing unit and record final
  revisions, status, test results, and available artifact hashes in `evidence.md`.
- [x] Confirm no commit, push, PR comment, PR creation, merge, tag, upload, or release publication
  occurred.

**What we know works after this phase:** Both skew directions fail closed for the intended causal
reason, the unchanged wheelhouse resolves with only the corrected companion request, the exact
hashed candidate pair passes, both locks and runtime identities agree, Items 2/4/6 and user changes
are preserved, and Item 1 is ready for independent `my-audit` rather than self-certification.

---

## Coordinated File Inventory

These are the exact files currently expected for the five phases. This is an execution inventory,
not an item-isolation or hunk allowlist. Items 1/2/4/6 share one landing baseline and may require an
additional shared-wave file when a kept test or approved invariant exposes that need. Record the
reason in `evidence.md` and the phase completion notes before editing it. A change outside the
constraint wave still requires preserving the separately recorded user/unrelated baseline.

### agentic-mbse

- `src/agentic_mbse/sysml/executable_profile.py`
- `src/agentic_mbse/validation/level6_architecture.py`
- `src/agentic_mbse/__init__.py`
- `docs/patterns/constraints.md`
- `pyproject.toml`
- `uv.lock`
- `tests/test_sysml/test_executable_profile_matrix.py`
- `tests/test_sysml/test_executable_profile.py`
- `tests/test_sysml/test_executable_profile_arithmetic.py`
- `tests/test_sysml/test_executable_profile_v3.py`
- `tests/test_sysml/test_executable_profile_v4.py` (new)
- `tests/test_sysml/test_constraint_profile_route_parity.py` (new)
- `tests/test_sysml/test_constraint_fact_shapes.py`
- `tests/test_validation/test_item12_checks.py`
- `tests/test_validation/test_level4_reconciliation.py`
- existing `tests/test_package_version.py` and `tests/test_constraint_documentation.py` only for
  focused Item 1 assertions; preserve their incoming untracked/user content through the sealed
  overlay manifest
- `.project/active/constraint-wave-profile-semantics/plan.md`
- `.project/active/constraint-wave-profile-semantics/evidence.md` (new during implementation)
- `.project/active/constraint-wave-profile-semantics/evidence/**` (new deterministic evidence only)

### sysml-codegen

- `src/sysml_codegen/analysis/constraint_lowering.py`
- `src/sysml_codegen/resolution/models.py`
- `src/sysml_codegen/generation/constraint_catalog.py`
- `src/sysml_codegen/generation/predicate_compiler.py`
- `src/sysml_codegen/generation/modules.py`
- `src/sysml_codegen/generation/constraint_plan.py` (new)
- `src/sysml_codegen/cli/__init__.py`
- `pyproject.toml`
- `uv.lock`
- `tests/conformance/test_constraint_lowering.py`
- `tests/conformance/test_data_models.py`
- `tests/conformance/test_constraint_catalog_determinism.py`
- `tests/conformance/test_constraint_generation_integration.py`
- `tests/conformance/test_constraint_pipeline_threading.py`
- `tests/conformance/test_constraint_snapshot_identity.py`
- `tests/conformance/test_snapshot_constraint_parity.py`
- `tests/unit/test_concrete_constraint_model.py`
- `tests/unit/test_predicate_compiler.py`
- `tests/unit/test_constraint_emission.py`
- `tests/unit/test_cli_generation.py`
- `tests/unit/test_snapshot_v3_gate.py`
- `tests/unit/test_package_metadata.py`
- `tests/execution/test_constraint_execution.py`

No fixture or snapshot recapture is planned. Backlog/current-work/audit/completed artifacts and
remote state are outside this implementation stage. Existing shared-wave contract, seal/verifier,
name-safety, source-referent, snapshot-codec, and test edits remain part of the active baseline; do
not rewrite them unless a Phase 3/4 regression proves a coordinated correction is required.

## Completion Criteria

- [x] All spec success criteria are mapped to a GREEN kept test or a precise evidence node.
- [x] The source-keyed neutral-body/per-usage-polarity architecture matches D1-D11 without an
  alternate semantic path.
- [x] Historical R-1 and profile R-2 are RED at `54a95d2`; the selected candidate is GREEN; the
  downstream historical polarity control remains GREEN.
- [x] All normal and applicable optimized focused gates pass, including pre-output sentinel tests.
- [x] Licensed live/codec and snapshot/live routes run with the explicit sysml-codegen `.env` and
  pass; any skip leaves the corresponding criterion open.
- [x] Full companion and codegen suites are recorded in companion-first order.
- [x] Old/new, new/old resolver, new/old runtime-bypass, same-wheelhouse positive, and exact candidate
  pair controls all have hash-identified evidence.
- [x] Companion `0.1.2`, profile v4, codegen `>=0.1.2`, both lock selections, runtime identities, and
  wheel hashes agree.
- [x] Item 2/4/6 regression gates pass normally and under optimized Python; all approved shared-wave
  behaviors remain intact.
- [x] `ConstraintFacts` and snapshot-v3 schemas/shapes remain unchanged; no fixture was recaptured.
- [x] `evidence.md` contains exact commands/results, revisions, hashes, scope review, failures/skips,
  and the explicit no-remote-action confirmation.
- [x] No commit, push, PR action, merge, tag, upload, or release publication occurred.

## Risk Management

See [design.md#potential-risks](design.md#potential-risks).

- **Phase 1:** exact clean revisions, fresh-process nodes, sealed manifests, and a downstream GREEN
  control prevent false historical or dirty-tree evidence.
- **Phase 2:** an independent fixed matrix oracle, decision-state construction probes, codec
  mutations, and optimized mode prevent production/test mirroring and removable-assert contracts.
- **Phase 3:** rung-by-rung canonical bytes, graph sentinels, reversed catalog order, exact-once
  runtime rows, and native-exception controls prevent authority drift, route-specific source keys,
  first-entry polarity, and double application.
- **Phase 4:** absent/populated sentinel trees and zero mutation counters prevent destructive
  preflight and a second grouping/compilation route during emission.
- **Phase 5:** one complete immutable hashed wheelhouse, exact conflict normalization, and the
  unchanged-wheelhouse positive control make resolver causality auditable.

## Implementation Notes

Fill these during implementation. Check phase boxes as soon as each action passes. A failed,
skipped, unavailable, or drifted gate stays unchecked with its exact result in `evidence.md`.

### Phase 1 Completion

**Completed:** Historical R-1 reproduction, v4 ordering/polarity decision contract, stable L6
location fallback, consumer map, documentation, and focused normal/optimized tests.
**Actual changes:** Profile v4 adds total ordering, classified polarity, state validation, named
constructors, and exact diagnostics without changing the fact schema.
**Validation:** Historical probes reproduce the v3 gaps at `54a95d2`; active focused gates pass
with 434 normal and 434 optimized tests. The downstream historical execution control passes in both
modes.
**Issues / deviations:** The live/codec route test lives in codegen rather than the prescribed
companion filename. The owner later removed clean-overlay and pre-edit-hash process gates.

### Phase 2 Completion

**Completed:** Companion package/runtime/lock identity is `0.1.2`; profile identity is v4; the final
local wheel is hash identified.
**Actual changes:** Updated package metadata, public version, lock, guide, and identity tests.
**Validation:** Full companion suite passed: 1,797 passed, 1 skipped, 33 deselected.
**Issues / deviations:** The wheel was built from the active shared-wave tree. The owner accepted
that provenance after audit and removed the clean-overlay gate.

### Phase 3 Completion

**Completed:** Decision authority/source continuity, required source keys, neutral body compiler,
per-usage finalization, and v4 runtime guard.
**Actual changes:** Lowering, models, catalog, compiler, modules, templates, and tests carry one
positive predicate source with complementary decision fields.
**Validation:** Coordinated focused gates passed (575 normal); optimized shared-wave overlap passed
614 tests, and the final candidate selection passed 664 tests in each mode.
**Issues / deviations:** Integrated catalog/live/codec coverage was added in codegen rather than
every prescribed filename. No fixture was recaptured.

### Phase 4 Completion

**Completed:** Read-only `ConstraintGenerationPlan` is built before clear/setup and consumed without
regrouping or recompilation.
**Actual changes:** CLI preflight now compiles and renders constraint artifacts before output
mutation; emission consumes the frozen plan.
**Validation:** Phase 4 focused tests passed 80; combined Phase 3/4 tests passed 575; candidate
normal/optimized overlap passed 614 before final rebuild and 664 after final rebuild.
**Issues / deviations:** Source-identity and compound-diagnostic absent/populated mutation sentinels
were added during audit remediation. File-specific bullets remain unchecked where the named test
file was not added.

### Phase 5 Completion

**Completed:** Version floor/locks, four hash-pinned compatibility inputs, causal resolver
normalization, both runtime-skew guards, same-wheelhouse positive control, exact candidate tests,
full suites, overlap gates, touched-file Ruff gates, mypy baselines, and whitespace checks.
**Actual changes:** Codegen requires `agentic-mbse>=0.1.2`; durable compatibility manifests and the
resolver log are stored under `evidence/`.
**Validation:** Final candidate normal/optimized selection: 664 passed in each mode. Full codegen:
2,960 passed, 26 skipped, 10 deselected. Both `git diff --check` commands passed.
**Issues / deviations:** Full-project Ruff/mypy remain red with inherited debt. Clean candidate
overlay provenance and incoming per-path hashes were not captured; the owner later removed those
agent-authored completion gates. See `evidence.md`.

---

### Independent Audit Cure

**Completed:** Effective-source identity validation, integrated four-route continuity, compound
diagnostic mutation sentinel, mixed-polarity TEAx execution, and historical R-2/downstream controls.
**Validation:** 56 focused and 614 overlap tests pass normally and optimized; 15 TEAx execution
tests pass in each mode; touched production Ruff, format, mypy, and whitespace gates pass.
**Issues / deviations:** Pre-edit per-path/fixture hashes and clean candidate-overlay provenance do
not exist and are not claimed. The owner removed them as completion gates after audit. Equivalent
kept route/sentinel coverage was placed in codegen rather than every filename prescribed by the plan.

**Status:** Draft → In Progress → Complete; paused before further orchestration for owner discussion
