# Implementation Plan: Executable-subset capability contract (EXEC-SUBSET-CONTRACT Item 1)

**Status:** In Progress (Phases 1–7 complete)
**Created:** 2026-10-18
**Last Updated:** 2026-10-18
**Branch:** `exec-subset-profile` (plan written at `1ff91e07`; `src/`, `tests/`, `scripts/` and `pyproject.toml` are unchanged since the design base `a718efec`)
**Pins (read-only):** sysml-codegen `b5663c07e987a892e27d21e68cec40d0656574ee`; dc3 `808464df…` (baseline), `60b44d53…` (repaired); SysIDE 0.8.4

## Source Documents

- **Spec:** [spec.md](spec.md), with its Change Log. SA-1 is accepted (see Settled inputs).
- **Design:** [design.md](design.md), revision 2. ← Component details, data model (Appendix A), probe list (Appendix C), ADR drafts (Appendix B) live there. This plan links to them and does not restate them.
- **Design review:** [design-review.md](design-review.md) § Resolutions (M1–M5, S1–S10, m1–m6).
- **Spike F1:** [spikes/f1-findings.md](spikes/f1-findings.md) and `spikes/f1-occurrence-port/` (the port to productionize, the oracle, the 11 edge fixtures).
- **Gates:** [briefs/align.md](briefs/align.md) (R1–R3).

## The Point

Three consumers each hold their own picture of which SysML shapes the generator (sysml-codegen) can execute: the generator itself, agentic-mbse's L6 check, and the shipped modeling guidance. The pictures drift. On dc3's baseline, L6 reported B7 and B8 and missed B1–B6, and a modeler only found those by running the generator and failing, one error at a time.

Item 1 builds the one declared contract the three will later share. It is a lookup table keyed by (shape, context) that says whether the pinned generator refuses, admits, excludes or omits each pair, and every entry carries evidence: a retained run of the real generator. It also builds the facts and the pure evaluator that apply the table to a user model, and an inventory that accounts for every refusal site in the generator. Item 1 wires no consumer: codegen adopts the contract in Item 2, L6 in Item 3, guidance in Item 5.

The governing obligation `[INHERITED: epic Item 1 objective]`: build it **without duplicating model interpretation and without broadening current refusals accidentally**. In practice the contract must be honest in both directions:

- It never calls a model clean when a check could not run (`unverified`, verdict `INCOMPLETE`).
- It never refuses a shape the pinned generator accepts (no `refused` without a probe; R2 halts on contradiction).

Every phase below is checkable against those two sentences, not only against the design.

## Settled Inputs

- `[AGENT] (ratified by owner, 2026-10-18; reply "A (ii)")` **R1.** Option A: the summary occurrence port ships in agentic-mbse as a shared fact. End condition (ii): codegen keeps its copy and Item 2 adds a permanent parity CI test. ADR 0012 is amended. For Item 1 this means: file the agentic-mbse ADR from [design Appendix B.1](design.md#b1-agentic-mbse-adr-filed-after-owner-approval) in `.project/adr/` (Phase 11), and keep the ADR 0012 amendment as a ready-to-file draft for Item 2. **Nothing is written into sysml-codegen.**
- `[AGENT] (accepted by orchestrator, 2026-10-18)` **SA-1.** A shape the generator refuses in every context the rule can compute may carry a `no_admitted_context` statement (generator citation plus refused probes covering each computable context) instead of an admitted-context probe. It makes no rule stricter.
- `[INHERITED: briefs/align.md]` **R2 is a standing gate.** Where it can fire and what the implementer does is in [R2 surfacing map](#r2-surfacing-map).
- `[INHERITED: briefs/align.md]` **R3 is owner-only.** Phase 11 produces a disposition table marked **PROPOSED**. The implementer does not decide it.

## Implementation Strategy

### Phasing Rationale

Every `refused` the contract can emit depends on a probe, and every instantiation-dependent context depends on the occurrence port. So the order is: prove the probe harness, then prove the port's parity, then build the remaining facts, then the pure evaluator with an empty evidence table, then fill the table one probe at a time, then the inventory, then the acceptance runs at a frozen revision, then close-out.

Filling the record table only from certified probes (Phases 6–7) means the evaluator is R2-safe at every intermediate commit. Before a pair has a probe, it reports `unconfirmed`. That is the design's evidence gate ([D3](design.md#key-decisions)) used as the build order.

### Critical Path

1. Phase 1: the harness can run the pinned generator in isolation and judge a probe (invariant 2).
2. Phase 2: the occurrence port matches codegen on the parity seed inside pytest.
3. Phases 3–4: the remaining facts exist and are total.
4. Phase 5: the pure evaluator and record loader exist; records hold only the smoke-probe pairs.
5. Phases 6–7: probes fill the records. This is where R2 can fire.
6. Phases 8–9: matrix and site account, joined to the records.
7. Phase 10: acceptance runs at the final revision.
8. Phase 11: ADR, drafts, R3 proposal, re-estimate.

Phases 8 and 9 depend only on Phase 5's rule IDs and can run in parallel with Phases 6–7 if two implementers are available. Their evidence-status fields are finalized after Phase 7.

### First Proof Point

Phase 1's four smoke probes each produce an `observation.json` with `certifies = true`, judged by a pytest-tested function: one refused with a specific code, one refused with the generic `SI_EVIDENCE_INCOMPLETE` code (location check), one admitted with a positive control, and one omitted. If any judging path cannot be made to work, the contract's evidence mechanism is in question, and nothing after Phase 1 should start.

### Standing Rules (every phase)

> **Green, defined (orchestrator, 2026-10-18, [AGENT]):** the repo baseline at `main` merge `8b027bbc` already has 118 ruff errors, 98 mypy errors in 20 files, and 3 environment-dependent pytest failures (stale `/home/reid/1cfe/agentic-mbse` paths, missing PIL). "Green" means no new failures relative to that baseline, and every new or modified file passes ruff check, ruff format --check and mypy cleanly. Never run repo-wide `ruff format`. The baseline cleanup is out of scope for Item 1.

- **Green at the end of every phase:** `uv run pytest tests/`, `uv run mypy src/`, `uv run ruff check src/ tests/`. Also run `uv run ruff format --check src/ tests/`. A phase is not done until all pass.
- **Commit at the end of every phase.** The probe harness exports agentic-mbse with `git archive`, so a probe can only cite a committed revision. Commit before running probes.
- **Test-first.** Write the phase's test file from its stencil, see it fail for the right reason, then implement.
- **Check off and annotate.** Tick this plan's checkboxes as items land, and add a Phase Completion note under [Implementation Notes](#implementation-notes) with what changed, issues and deviations.
- **Sibling trees are read-only.** sysml-codegen and dc3 are only read through `git archive` into temp directories. Never run anything inside `~/src/sysml-codegen` or `~/src/dc3`.
- **Quality bar, as checks:**
  - No duplicated model interpretation beyond the approved port. Shared-code facts call the existing helpers; Phase 4 has an AST test for it.
  - Pure decision layer. `subset_profile.py` imports no SysIDE, `syside_adapter` or `reference_use` (Phase 5 hygiene test).
  - Closed, validated vocabularies. Every enum and reason set is validated at construction (Phase 5).
  - Deterministic output (Phase 5 synthetic, Phase 7 with real document-order permutation).
  - Unverified never clean. Only verdict `CLEAR` is clean (Phase 5 failure injection, Phase 4 extraction failures).

### R2 Surfacing Map

R2 fires when a probe shows the pinned generator **admitting** a (shape, context) that a rule expected to **refuse**. It can surface in these places:

| Where | What fires it |
|---|---|
| Phase 1 | A smoke refused probe exits 0. |
| Phase 6 | A model-wide refused probe (calc-owned assertion, indexed reference, invocation, conditional) is admitted. |
| Phase 7 | An instantiation-dependent refused probe or a variation probe (B5) is admitted. This is the most likely place. |
| Phase 10 | A `refused` finding on one of the 14 corpus snapshot fixtures, or on the dc3 repaired tree, which generates. |

**What the implementer does when R2 fires:**

1. **Stop that rule's pair.** Do not add the refused admission to the record. The pair stays `unconfirmed`, which is safe by construction.
2. **Do not design around it.** Do not narrow, rename or split the context to make the conflict go away, and do not change the fixture until it refuses. Splitting a context is only allowed under step 4.
3. **Write it down.** Create `evidence/r2-<rule>-<shape>.md` with the probe ID, its observation, the expected outcome, and the record entry it blocks. Add a line to Implementation Notes.
4. **Rule out a port bug first.** Run the codegen oracle (`scripts/subset_profile/occurrence_parity.py capture`) on the probe's fixture. If the oracle's occurrence facts differ from the port's, it is a port bug, not R2: fix the port, add the fixture to the parity seed, and re-probe. If they agree, it is genuine R2 (or a B5 split for a variation probe; record the split as R2 too, because the owner decides whether the narrower context ships).
5. **Continue every non-dependent rule.** A halted pair blocks only the done conditions that name it. Mark those `BLOCKED (R2)` in the phase completion note, not failed and not silently passed.
6. **End the session with the question.** When all non-dependent work in the phase is done, the implementer's final message lists each open R2 item for the owner.

The opposite direction is not R2. A probe that shows the generator **refusing** where admission was expected means the record's contexts are wrong: record the observation, correct the contexts, re-probe, and note it ([design § Probe harness, Halt direction](design.md#probe-harness)).

### Decisions This Plan Makes

These were open for the plan ([design § Next-Stage Handoff](design.md#next-stage-handoff)). All are `[AGENT]`, challengeable by re-deriving against the reason given.

- **P-1. No new `reference_use` accessors.** The spike's two raw reads are `bound.referent` and `redefined.chaining_features` (`spikes/f1-occurrence-port/occurrence_port.py:271`, `:85`). The existing `resolved_referent` (`reference_use.py:190-192`) and `resolved_chaining_features` (`reference_use.py:200-202`) are exactly those `getattr` reads with the same defaults. The port routes through them. Phase 2's parity test is the proof. Add new named accessors only if parity fails on a case that traces to these reads.
- **P-2. One probe judge, owned by the test suite.** The certification logic (invariant 2) lives in `tests/helpers/subset_probe_judge.py` (pure, stdlib only). `scripts/subset_profile/probe.py` imports it (putting the repo root on `sys.path`, as tests already import `tests.helpers.shipped`) to write `certifies` into each observation, and `tests/test_subset_probe_evidence.py` re-judges every stored observation with it. Reason: the pytest gate is the authority, so it must not depend on a script's copy of the rule.
- **P-3. One oracle-schema normalizer, owned by the test suite.** `tests/helpers/occurrence_oracle_schema.py` turns an `OccurrenceStructure` into the F1 oracle JSON schema (`spikes/f1-occurrence-port/port_run.py:27-95`). The parity test and `scripts/subset_profile/occurrence_parity.py` both use it. Same reason as P-2.
- **P-4. `OccurrenceAbort` gains `IDENTITY_UNSTABLE`.** The spike raises `id_unstable` when an element has no qualified name or a non-UUIDv5 identity (`occurrence_port.py:54-60`), mirroring codegen `identity.py:66`. Design Appendix A lists seven members and none fits. The eighth member is a recorded deviation.
- **P-5. The spike's coarse causes split into the Appendix A members.** The spike reuses `containment_recursive` for a specialization cycle and `redefinition_invalid` for six different raises. Production maps each raise site to the member that names codegen's raise at the mirrored line, and the module docstring keeps the spike's line-mapping table with a member column. Parity compares the stage and the mapped codegen code, as F1 did.
- **P-6. The pytest parity seed gains one fixture.** F1 found that only the dc3 repaired tree catches the `no_effective_decl` mutant, and dc3 is not in this repo. Phase 2 authors `f1_effective_declaration_slot.sysml` (two declarations in one redefinition slot where the effective one is not the first) so the seed alone catches all three catchable mutants.
- **P-7. Records start with no admissions beyond the smoke probes.** Phase 5 ships every rule and shape, but only the four smoke-probe pairs have admissions. Phases 6–7 add admissions only from certified probes.
- **P-8. The "final implementation revision"** is the commit at which Phase 10 starts. If any `src/` change lands after it, that commit becomes the final revision and every Phase 10 run repeats.
- **P-9. Early codegen check.** Phase 3 (the one edit codegen sees immediately, through its editable path dependency) runs codegen's pytest suite in a temp tree against agentic-mbse at that commit. Design S6 runs it only at the end; running it early catches a non-byte-faithful refactor before anything is built on it.
- **P-10. `TOML` field names** follow the Appendix A attribute names in snake_case. `ContextId` starts as the Appendix A set (plus any member P-4-style additions need). Adding a member requires a probe that motivates it; removing one requires an Implementation Notes line.

---

## Phase 1: Probe harness smoke test (design F5)

### Goal

Prove the harness runs the pinned generator in an isolated tree, captures exit, codes, error locations and generated files, and judges certification. Every refusal in Item 1 depends on this.

### Assumption Under Test

- The `generate` CLI path works in a temp tree built from `git archive` exports (F1 proved the export, `uv sync --frozen` and license steps; it did not run `generate`).
- Codegen's `ERROR:` lines carry the code and a source location that can be compared with a construct's declared line range. This is the location check that keeps ES-006's generic `SI_EVIDENCE_INCOMPLETE` honest.
- An admitted probe's positive-control sibling and an omitted element's absence can be read from the generated catalog and contract modules.

### Test Stencil (Write This First)

```python
# tests/test_subset_probe_judge.py  (pure; no SysIDE, no codegen)
from tests.helpers.subset_probe_judge import judge, load_probe

def test_refused_needs_matching_code_and_location():
    probe = load_probe(FIXTURES / "smoke_binding_tuple_instantiated")
    obs = observation(exit=1, errors=[("SI_SELF_BINDING", "model.sysml", 12)])
    assert judge(probe, obs).failed_check == "code_mismatch"
    obs = observation(exit=1, errors=[("SI_EXPRESSION_SOURCE_UNSUPPORTED", "model.sysml", 3)])
    assert judge(probe, obs).failed_check == "location_outside_construct"

def test_admitted_needs_positive_control_in_output():
    obs = observation(exit=0, generated=["catalog.py"], symbols=[])
    assert judge(load_probe(ADMITTED), obs).failed_check == "positive_control_missing"
```

Also cover: identity mismatch (wrong codegen revision, a package resolving outside the temp tree), an omitted element that appears in the output, and a fully certifying case for each outcome.

### Changes Required

**See design for:** [§ Probe harness](design.md#probe-harness) (steps 1–6), [Required Invariants 2](design.md#required-invariants), [§ Where things live](design.md#where-things-live).

- [x] **Read first:** codegen `cli/__init__.py:1026-1069` and `:857` at `b5663c07` (through `git show b5663c07:src/sysml_codegen/cli/__init__.py`) to confirm the `ERROR:` line format and where the location appears. Record the format in the judge's module docstring.
- [x] `tests/helpers/subset_probe_judge.py` (NEW, pure): `load_probe`, `judge` → `Certification(certifies, failed_check)`. Checks per invariant 2 (P-2).
- [x] `tests/test_subset_probe_judge.py` (NEW, write first): the stencil plus the cases above, on synthetic observations.
- [x] `scripts/subset_profile/probe.py` (NEW): `run --probe ID | --all --agentic-rev REV [--base]`. Steps 1–5 of the design's harness. Writes `observation.json`, or `observation.base.json` with `--base`. Imports the judge (P-2). Logs to `.project/active/exec-subset-profile/evidence/probes/`.
- [x] `scripts/subset_profile/README.md` (NEW, short): what each script does and that none is shipped.
- [x] Four smoke probes under `tests/fixtures/subset_profile/probes/<id>/{probe.toml, model.sysml, observation.json}`:
  - `binding_source/expression_source/owner_instantiated` ⇐ prototype `es003_refused_ordered_nonunique` (expected `SI_EXPRESSION_SOURCE_UNSUPPORTED`).
  - `conditional_expression/conditional_unresolved_branch/binding_value` ⇐ `es006_refused_conditional` (expected `SI_EVIDENCE_INCOMPLETE`, location check).
  - `invocation_callable` admitted neighbor ⇐ `es005_admitted_explicit_multiply` (positive control).
  - `string_value_omission/string_value` ⇐ `es010_omitted_string_value` (catalog/contract identity check with a numeric sibling, per review m3).

  Probe IDs are directory names; pick a stable `rule__shape__context` spelling and use it everywhere after.
- [x] Commit, then run `uv run python scripts/subset_profile/probe.py run --all --agentic-rev HEAD`.

### Validation

**Automated:**
- [x] `uv run pytest tests/test_subset_probe_judge.py` passes.
- [ ] Standing checks green. **Not met, and not by Phase 1:** they were red at `1002997d`, before this phase; Phase 1 adds no failure. See [Phase 1 Completion](#phase-1-completion) → Issues.

**Manual:**
- [x] All four `observation.json` files show `certifies: true`, the codegen revision `b5663c07…`, the agentic-mbse revision, SysIDE 0.8.4, the `uv.lock` sha256, and both package `__file__` paths inside the temp tree.
- [x] `git -C ~/src/sysml-codegen status` and `git -C ~/src/dc3 status` are unchanged.
- [x] Control: hand-edit a copy of the conditional probe's observation to move the error line outside the construct's range, re-judge, and see `location_outside_construct`.

**If the generator gives no usable location for `SI_EVIDENCE_INCOMPLETE`:** the ES-006 location check cannot be met. Do not weaken invariant 2. ES-006's refused pairs stay `unconfirmed`, record why in Implementation Notes, and surface it (capture-fidelity law 4). Every other rule continues.

**Done when:** the four probes certify and the judge's tests pass. Traces to spec "Every refusal has a probe record" (the mechanism) and Known Requirements → Evidence bar.

---

## Phase 2: Occurrence facts and the parity test

### Goal

Productionize the F1 summary port as a shared fact and hold it to codegen with a pytest parity test that needs no codegen checkout.

### Assumption Under Test

- B2: the port stays at parity beyond the spike once it uses production types, the split abort vocabulary (P-5), the existing accessors (P-1) and caller roots (D7).
- B6: `SysideAdapter.load_model` gives the generator's population.
- The parity seed, stored as codegen-oracle `expected.json` files, catches the three catchable F1 mutants without dc3 (P-6).

### Test Stencil (Write This First)

```python
# tests/test_sysml/test_occurrence_parity.py  (SysIDE)
SEED = sorted((FIXTURES / "subset_profile" / "occurrence").iterdir())

@pytest.mark.parametrize("case", SEED, ids=lambda p: p.name)
def test_port_matches_codegen_oracle(case):
    model, _ = SysideAdapter.load_model(model_paths(case))
    structure = extract_occurrence_structure(model)
    actual = to_oracle_schema(structure)              # tests/helpers/occurrence_oracle_schema.py
    expected = json.loads((case / "expected.json").read_text())
    assert actual == strip_oracle_only_fields(expected)   # roots, occurrences, counts, writers, aborts
```

Also write `test_default_roots_equal_generator_rule` on a fixture with nested, package-level and part-def-owned part usages (spec Roots criterion, first test), and a pure `test_occurrence_facts.py` for frozen types and the closed `OccurrenceAbort` set.

### Changes Required

**See design for:** [R1 Option A](design.md#option-a--copy-the-instantiation-logic-into-agentic-mbse-as-a-shared-fact), [D7](design.md#key-decisions), [D13–D14](design.md#key-decisions), [Appendix A occurrence types](design.md#appendix-a--data-model), F1 [Surprises 1–3](spikes/f1-findings.md#summary-of-findings).

- [x] `src/agentic_mbse/sysml/occurrence_facts.py` (NEW, pure): `OccurrenceStructure`, `OccurrenceNode`, `MultiplicityReading`, `Attachment`, `WriterSelection`, `OccurrenceAbort` (with P-4's `IDENTITY_UNSTABLE`). Counts are per parent occurrence (review S4).
- [x] `src/agentic_mbse/sysml/occurrence_extraction.py` (NEW): `extract_occurrence_structure(model, extra_roots=()) -> OccurrenceStructure | FactFailure`. Port `spikes/f1-occurrence-port/occurrence_port.py` function by function:
  - Keep the docstring's codegen line map and add the abort-member column (P-5).
  - Route the two raw reads through `resolved_referent` and `resolved_chaining_features` (P-1).
  - Writer selection records selected and overridden scope counts per usage (design Implementation Note (a)).
  - Caller roots: compute reach from extra `PartUsage` roots separately from the generator root set (D7).
  - Mirror D14's two generator behaviors exactly; do not fix them.
- [x] `tests/helpers/occurrence_oracle_schema.py` (NEW, P-3).
- [x] `scripts/subset_profile/occurrence_parity.py` (NEW): promote `oracle.py`, `compare.py` and `run_all.sh`. Subcommands: `capture CASE…` (writes `expected.json` from codegen's oracle in an isolated tree) and `compare --all` (the recorded 72-case run, plus the new seed fixture).
- [x] `tests/fixtures/subset_profile/occurrence/<case>/{model.sysml, expected.json}` (NEW): the 11 F1 edge fixtures, the 22 prototype fixtures from `.project/concepts/convince-me-exec-subset/evidence/01-fixtures/`, and P-6's new fixture. Capture every `expected.json` with `occurrence_parity.py capture`; never hand-write one.
- [x] `tests/fixtures/subset_profile/cases/roots_mixed_owners.sysml` (NEW) for the default-roots test.
- [x] `tests/test_sysml/test_occurrence_parity.py`, `tests/test_sysml/test_occurrence_facts.py`, `tests/test_sysml/test_occurrence_extraction_roots.py` (NEW).
- [x] `tests/test_sysml/test_semantic_selector_ownership.py`: **no edit.** It must stay green with the port in place; that is the evidence P-1 holds.

### Validation

**Automated:**
- [x] Parity test passes on every seed case. Abort cases match on stage and mapped code.
- [x] Selector-ownership gate green, unchanged.
- [x] Standing checks green.

**Manual:**
- [x] `occurrence_parity.py compare --all` at the committed revision: every case matches (72 plus the new fixture). Log to `evidence/occurrence-parity.log`.
- [x] Mutant control: run the spike's `mutants.py` patches against the production port on the pytest seed only. `typed_anywhere`, `writer_is_base` and `no_effective_decl` are each caught by at least one seed case. `declared_multiplicity` is not catchable (F1 Surprise 1) and is recorded as such. Log to `evidence/occurrence-parity-controls.log`.
- [x] `python -I -c "import agentic_mbse.sysml.occurrence_extraction, sys; assert not any(m.startswith('sysml_codegen') for m in sys.modules)"`.

**Done when:** the parity test passes on the seed, the recorded run matches on all cases, and the controls bite. Traces to spec "Roots are reported and generator-equivalent by default" (first test) and Requirements on specific families → ES-004 facts; design invariant 10.

---

## Phase 3: Shared invocation allowlist and `invocation_uses`

### Goal

Move the one capability decision in the fact layer to a pure module both sides import, and add the total invocation walk ES-005 needs. This is the only Item 1 edit that codegen sees immediately, so it gets its own phase and an early codegen check.

### Assumption Under Test

The refactor is byte-faithful: codegen's behavior and agentic-mbse's existing reference-use behavior are unchanged.

### Test Stencil (Write This First)

```python
# tests/test_sysml/test_invocation_uses.py  (SysIDE)
@pytest.mark.parametrize("source, expected", [
    ("product(xs)", [("ScalarFunctions::product", False)]),   # (callable, supported)
    ("sum(xs)",     [("NumericalFunctions::sum", True)]),
    ("a * b",       []),                                        # operator, not an invocation
    ("max(a, b) [SI::m]", [("...::max", False)]),             # through a unit annotation
])
def test_invocation_uses_is_total_and_matches_allowlist(source, expected): ...
```

Also: `test_invocation_allowlist.py` (pure) asserts `SUPPORTED_INVOCATION_IDS` equals the one `NumericalFunctions::sum` UUID (`reference_use.py:61`) and that importing the module pulls in no SysIDE.

### Changes Required

**See design for:** [§ Architecture, "ES-005 reuses the allowlist"](design.md#architecture), [R1 grandfathered exception](design.md#what-owning-the-contract-means-in-plain-words), review S8.

- [x] `src/agentic_mbse/sysml/invocation_allowlist.py` (NEW, pure): `SUPPORTED_INVOCATION_IDS`, `is_supported_invocation_id(uuid) -> bool`.
- [x] `src/agentic_mbse/sysml/reference_use.py` (EDIT):
  - `_STANDARD_SUM_FUNCTION_ID` (`:61`) moves to the allowlist module. `_is_plural_invocation` (`:379-392`) and `_require_supported_invocation` (`:395-428`) call the predicate. The raise stays where it is (grandfathered).
  - Add public `invocation_uses(expression) -> tuple[InvocationUse, ...]`: a total walk that resolves no references and uses the same dispatch order as `_walk` (`:302-339`). A failure raises `SemanticEvidenceError` with its existing code; the caller turns it into `InvocationFailed`.
- [x] `tests/test_sysml/test_invocation_allowlist.py`, `tests/test_sysml/test_invocation_uses.py` (NEW).
- [x] `tests/test_sysml/test_reference_use.py`: **no edit**; it must stay green.
- [x] `tests/test_sysml/test_public_api_exports.py`: update only if `invocation_uses` is exported from the package `__init__`. Not exported, so no edit; the test stays green.

### Validation

**Automated:**
- [x] New tests pass; `test_reference_use.py` unchanged and green.
- [x] Standing checks green.

**Manual (P-9):**
- [x] Commit. In a temp tree with codegen `b5663c07`, run codegen's pytest suite once with agentic-mbse at `a718efec` and once at this commit. Results must be identical. Log to `evidence/same-generator-phase3.log`.
- [x] Re-run the four smoke probes at this commit; observations must match Phase 1's.

**If codegen's results differ:** the refactor is not byte-faithful. Fix the code until they match. Never record the difference as accepted.

**Done when:** codegen's suite and the smoke probes are unchanged across the edit. Traces to spec "No duplicated interpretation" (ES-005 reuses `_require_supported_invocation`) and design invariant 9 (allowlist is versioned, enforced in Phase 5).

---

## Phase 4: Subset facts and extraction

### Goal

Extract every remaining fact kind once, from shared helpers, as a total result: each element either yields a fact or a `FactFailure`, and a kind that fails to enumerate is marked not enumerated.

### Assumption Under Test

- B1: the boundary is readable from SysIDE before elaboration.
- F3: the binding-source fact equals codegen's classifier by shared code, except the metatype test, which the probes prove later.
- The conditional operator spelling is what the design assumes (learning test).

### Test Stencil (Write This First)

```python
# tests/test_sysml/test_subset_extraction.py  (SysIDE)
def test_binding_source_kinds():
    facts = extract_subset_facts(load(CASES / "binding_kinds.sysml"))
    kinds = {b.formal.qualified_name.split("::")[-1]: b.kind for b in facts.bindings}
    assert kinds == {"lit": "literal", "ref": "single_reference", "me": "self_binding",
                     "idx": "indexed", "tup": "other_expression", "unit": "literal"}

def test_reference_walk_failure_becomes_fact_failure(monkeypatch):
    monkeypatch.setattr(subset_extraction, "inspect_reference_uses", raise_code(RESOLVED_TARGET_MISSING))
    facts = extract_subset_facts(load(CASES / "binding_kinds.sysml"))
    assert facts.bindings == () and {f.cause for f in facts.failures} == {RESOLVED_TARGET_MISSING}
```

### Changes Required

**See design for:** [Appendix A fact types](design.md#appendix-a--data-model), [§ Architecture "Facts are total"](design.md#architecture), spec [Requirements on specific families](spec.md#requirements-on-specific-families).

- [x] **Read first (codegen, read-only, through `git show b5663c07:…`):** `elaboration/expression_evidence.py:249-347` for the exact declared-feature value roles; `extraction/binding_source.py:183-207` and `elaboration/elaborate.py:1879-1950` for which members count as calc inputs (F3); `elaborate.py:1114-1118` for the reference metatype test. Record what you found as a docstring citation table in `subset_extraction.py`.
- [x] `src/agentic_mbse/sysml/subset_facts.py` (NEW, pure): `SubsetFacts`, `BindingSourceFact`, `ExpressionSiteFact`, `SiteInspection` (one total value, review S3), `AssertionOwnerFact`, `PartMultiplicityFact`, `StringValueFact`, `ElementRef`, `SafeLocation` (never raises), `FactFailure`, `FactKind`, `ScopeCause`.
- [x] `src/agentic_mbse/sysml/subset_extraction.py` (NEW): `extract_subset_facts(model, extra_roots=()) -> SubsetFacts`.
  - Binding source: `unit_annotation_value` (`reference_use.py:342`), `is_literal_node` (`expression.py:441`), the `inspect_reference_uses` count, the metatype test, self-binding as leaf identity equal to the formal.
  - Expression sites: `inspect_reference_uses` and `invocation_uses` per site; conditionals by metatype walk; `calc_result_expression` and `other_expression_site` roles.
  - Assertion owners: forms from `constraint_extraction._ASSERTED_FORMS`.
  - Part multiplicities: from the Phase 2 `OccurrenceStructure` reading, not re-read.
  - Strings: both spellings.
  - Constraints: `extract_identified_constraint_facts`, unchanged.
  - The occurrence abort becomes one `FactFailure(OCCURRENCE, OccurrenceAbort.<kind>)`.
- [x] `tests/fixtures/subset_profile/cases/` (NEW): `binding_kinds.sysml`, `expression_sites.sysml`, `assertion_owners.sysml`, `string_spellings.sysml`, `conditional.sysml`.
- [x] `tests/test_sysml/test_subset_extraction.py` (NEW): per-kind tests; failure injection at extraction (reference failure, invocation failure, enumeration failure leaves the kind out of `enumerated`, occurrence abort).
- [x] `tests/test_sysml/test_conditional_operator_spelling.py` (NEW learning test) on `es006_refused_conditional` (design Implementation Notes).
- [x] `tests/test_sysml/test_subset_extraction_no_reinterpretation.py` (NEW, AST): `subset_extraction.py` imports `is_literal_node`, `unit_annotation_value`, `inspect_reference_uses` and `invocation_uses`, and defines no function that compares against the names `"FeatureReferenceExpression"` or `"InvocationExpression"` except the one metatype test codegen also has.

### Validation

**Automated:**
- [x] New tests pass; selector-ownership gate green.
- [x] Standing checks green.

**Manual:**
- [x] Run `extract_subset_facts` on both dc3 trees (exported to a temp dir) and confirm it returns, with failures listed rather than raised. No assertions on content yet; that is Phase 10.

**Done when:** every fact kind is extracted totally and the injected failures surface as structured `FactFailure`s. Traces to spec "Failure cannot look clean" (extraction half), "No duplicated interpretation", and the binding-source and ES-006 requirements.

---

## Phase 5: Pure decision module and packaged records

### Goal

Build the evaluator, the record loader with its evidence gate, the closed vocabularies and the version digest, and test all of it without SysIDE using synthetic facts.

### Assumption Under Test

The decision layer can be pure and still express every rule, and the loader can make "no `refused` without a probe" a load-time property rather than a review habit.

### Test Stencil (Write This First)

```python
# tests/test_sysml/test_subset_profile_records.py  (pure)
def test_loader_rejects_admission_without_evidence(tmp_path):
    bad = RULES_TOML.replace('evidence = ["probe:binding_source__expression_source__owner_instantiated"]',
                             'evidence = []')
    with pytest.raises(RecordError, match="requires evidence"):
        load_rule_records(write(tmp_path, bad))

# tests/test_sysml/test_subset_profile_evaluate.py  (pure)
def test_failed_fact_is_unverified_and_others_still_report():
    facts = synthetic_facts(bindings=[tuple_binding_instantiated()],
                            failures=[FactFailure(FactKind.EXPRESSION_SITE, None, RESOLVED_TARGET_MISSING, "")])
    result = evaluate_subset_profile(facts)
    assert result.verdict is Verdict.INCOMPLETE
    assert {u.rule_id for u in result.unverified} >= {"invocation-callable", "conditional-expression"}
    assert any(f.rule_id == "binding-source" for f in result.findings)
```

### Changes Required

**See design for:** [D2–D8](design.md#key-decisions), [Required Invariants 1, 4–9](design.md#required-invariants), [Appendix A decision types, rule IDs and shapes](design.md#appendix-a--data-model), [§ Architecture ES-007](design.md#architecture).

- [x] `src/agentic_mbse/sysml/subset_profile.py` (NEW, pure): `SUBSET_PROFILE_VERSION`, `SUBSET_REASON_CODES` (disjoint from `REASON_CODES`, D4), `Outcome`, `Verdict`, `ContextId`, `EvidenceStatus`, record types and `load_rule_records` (validates every field, rejects unknown keys, enforces D3 and SA-1), the eight rule functions (recognize shape, compute context; never decide outcome), `evaluate_subset_profile(facts, rules=PACKAGED_RULES)`.
  - ES-007 calls `evaluate_identified_profile` (`executable_profile.py:1048`): BLOCK → `blocked_predicate`, NON_NUMERICAL → `excluded`, UNASSESSED counted, never `admitted`. Profile reasons travel as `detail_reasons`.
  - ES-006 is refusal-eligible only with a recognized conditional and a reference failure of `RESOLVED_TARGET_MISSING`; any other failure is `unverified`.
  - ES-005 is `unverified` whenever the site's invocations failed.
  - Roots: `BEYOND_GENERATOR_ROOTS` → `unconfirmed`; narrowed roots → `INCOMPLETE`; roots unavailable → root-dependent rules `unverified`.
  - Dedup by declaration (D6), sorting per invariant 8.
- [x] `src/agentic_mbse/sysml/subset_profile_rules.toml` (NEW, package data): all eight rules and their shapes, `verified_against`, remedy, semantic limits, doc anchor, evidence status. Admissions only for the four smoke-probe pairs (P-7). Load with `importlib.resources`.
- [x] `pyproject.toml`: no change expected, because hatch packages non-Python files under `src/agentic_mbse`. Verify with `uv build` and list the wheel; edit only if the TOML is missing.
- [x] Tests (NEW, all pure, all under `tests/test_sysml/`):
  - `test_subset_profile_records.py`: completeness of every field (spec "Records are complete"); evidence gate; `CorpusRef` only for `admitted` and only for the 14 snapshot fixture names; SA-1 statement needs a citation and refused probes for each computable context.
  - `test_subset_profile_vocabulary.py`: every enum closed; `SUBSET_REASON_CODES` disjoint from `REASON_CODES`; `SubsetFinding.__post_init__` rejects unknown reasons and detail reasons.
  - `test_executable_profile_computed_reasons.py`: drives every emission of the five computed sites (`executable_profile.py:542`, `:597`, `:660`, `:711`, `:813`) and asserts each is in `REASON_CODES`. Re-locate the line numbers first; cite them in the test docstring.
  - `test_subset_profile_coupling.py`: AST scan that no `agentic_mbse` module imports `sysml_codegen`; no rule or reason ID matches `SI_[A-Z_]+` or names `ElaborationCode`/`ReadinessCode`; `SI_*` appears in the TOML only in `expected_code` and `generator_evidence` fields.
  - `test_subset_profile_hygiene.py`: subprocess import of `subset_profile` leaves `syside`, `agentic_mbse.sysml.syside_adapter` and `agentic_mbse.sysml.reference_use` out of `sys.modules` (same shape as `test_executable_profile_hygiene.py`).
  - `test_subset_profile_version.py`: pins a digest of the records file and `SUPPORTED_INVOCATION_IDS` to `SUBSET_PROFILE_VERSION`; the result reports both versions.
  - `test_subset_profile_evaluate.py`: unlisted pair → `unconfirmed`; failure injection (a) extraction failure, (b) enumeration failure, (c) occurrence abort, each with a structured `UnverifiedCheck` and other rules still reporting; verdict derivation; root semantics (widened, narrowed, unavailable); dedup and counts; synthetic determinism (permuted fact order gives identical output).
- [x] `tests/test_subset_probe_evidence.py` (NEW): for every probe cited by a record, the observation re-judges as certified (P-2) and its identity matches the pin; every refused shape has an admitted-context probe or an SA-1 statement; stripping a pair's evidence makes the evaluator report `unconfirmed`. The SysIDE half (the evaluator reproduces each pair on the probe's own model) is added here too and grows as Phases 6–7 add probes.

### Validation

**Automated:**
- [x] All new tests pass. Standing checks green.

**Manual:**
- [x] Run the evaluator on the four smoke-probe models: each reports its probed pair with the recorded outcome, and every other finding is `unconfirmed`.

**Done when:** the evaluator and loader pass every pure test, and the only non-`unconfirmed` outcomes it can produce are the four smoke pairs. Traces to spec "Records are complete", "Every refusal has a probe record" (the gate), "Five computed reason sites are closed", "Failure cannot look clean", "Output is deterministic" (synthetic), "No consumer coupling", and "Roots" (second and third tests, synthetic).

---

## Phase 6: Probes for the model-wide rules

### Goal

Fill the records for the rules that need no instantiation facts: `calc-owned-assertion`, `indexed-reference`, `invocation-callable`, `conditional-expression`, `string-value-omission`. Also run the candidate reproductions.

### Assumption Under Test

B3: one construct per fixture, with a matching code and location, isolates one (shape, context) pair. And the model-wide contexts in spec Table 1 hold when observed.

### Test Stencil (Write This First)

```python
# tests/test_sysml/test_subset_profile_rules_modelwide.py  (SysIDE)
PROBES = probes_for_rules({"calc-owned-assertion", "indexed-reference", "invocation-callable",
                           "conditional-expression", "string-value-omission"})

@pytest.mark.parametrize("probe", PROBES, ids=lambda p: p.id)
def test_evaluator_reproduces_probe(probe):
    result = evaluate_subset_profile(extract_subset_facts(load(probe.model)))
    finding = result.only(probe.rule, probe.shape, subject=probe.construct)
    assert (finding.context_id, finding.outcome) == (probe.context, probe.recorded_outcome)
```

### Changes Required

**See design for:** [Appendix C](design.md#appendix-c--probe-list-initial) entries for these five rules and "Candidates, reproduction only"; [D12](design.md#key-decisions); spec [admitted neighbors list](spec.md#rule-records-and-evaluator).

- [x] Author each Appendix C probe for the five rules under `tests/fixtures/subset_profile/probes/`. Each declares its construct's line range; each admitted probe declares a positive control. Re-run every superseded prototype fixture through the harness (D9).
- [x] Commit, run `probe.py run` for the new probes, and judge.
- [x] For each certified probe, add its admission to `subset_profile_rules.toml`. For each rule, the refused pairs and their admitted-context pairs land together. Use SA-1's `no_admitted_context` for `calc-owned-assertion/asserted_constraint` under a calc-def owner, and for `indexed-reference` only if its calc-result probe refuses.
- [x] Candidate reproductions (ES-002, ES-008, ES-009, ES-010 refusal side): one probe each with `kind = "reproduction"`. They add no record admission. Record "reproduced" or "not reproduced" for R3.
- [x] `tests/test_sysml/test_subset_profile_rules_modelwide.py` (NEW): the stencil, plus the prototype admitted neighbors that belong to these rules (part-owned assert, explicit multiply, arithmetic `min`, numeric value).
- [x] Update `evidence_status` per rule.

### Validation

**Automated:**
- [x] New tests and `test_subset_probe_evidence.py` pass. Standing checks green.

**Manual:**
- [x] Each refused probe's observed code and location match; each admitted probe's control appears.
- [x] R2 check: any refused probe that exits 0 follows the [R2 surfacing map](#r2-surfacing-map).

**Done when:** every refused pair of these five rules has a certified probe and an admitted-context probe (or SA-1 statement), and the evaluator reproduces each on its own fixture. Traces to spec "Every refusal has a probe record", "Every refused shape has an admitted-context probe" (the ES-005 `max(a, b)` and ES-006 conditional calc-result cases), "Each implemented rule has refused and admitted fixtures".

---

## Phase 7: Probes for the instantiation-dependent rules

### Goal

Fill the records for `binding-source`, `part-multiplicity` and `constraint-predicate`, including the variation probes that test B5, and finish the end-to-end root and determinism tests.

### Assumption Under Test

- B5: the generator's outcome is constant within each context label.
- B2 in use: the port computes the context the generator would.

### Test Stencil (Write This First)

```python
# tests/test_sysml/test_subset_profile_rules_instantiation.py  (SysIDE)
def test_widened_roots_do_not_refuse():
    model = load(PROBES / "binding_source__expression_source__owner_uninstantiated" / "model.sysml")
    template = find_part_usage(model, "Templates::site")       # not a generator root
    result = evaluate_subset_profile(extract_subset_facts(model, extra_roots=(template,)))
    finding = result.only("binding-source", "expression_source")
    assert finding.context_id is ContextId.BEYOND_GENERATOR_ROOTS
    assert finding.outcome is Outcome.UNCONFIRMED and result.scope.roots_used

def test_permuted_document_order_is_identical():
    a = evaluate(load_paths(MULTI_DOC)); b = evaluate(load_paths(list(reversed(MULTI_DOC))))
    assert a == b
```

### Changes Required

**See design for:** [Appendix C](design.md#appendix-c--probe-list-initial) entries and V probes for these three rules; [B5](design.md#key-bets); [design Implementation Notes (a)–(b)](design.md#implementation-notes); [D14](design.md#key-decisions).

- [x] Author, commit, run and judge the Appendix C probes for the three rules, including every V probe. The `writer_overridden` admitted probe uses F1's `f1_calc_redefined_everywhere`.
- [x] Add certified admissions to the records. A V probe that disagrees with its label goes through the R2 map (step 4 decides port bug versus genuine split).
- [x] Record D14's two generator behaviors as observations (the "redefinition that drops bounds" admitted probe records G1). They are matrix rows G1/G2 in Phase 8, not rule changes.
- [x] `tests/fixtures/subset_profile/cases/multi_doc/` (NEW): a model split across several files with refused and admitted findings, for the permuted-order test.
- [x] `tests/test_sysml/test_subset_profile_rules_instantiation.py` (NEW): per-probe reproduction (same stencil as Phase 6); the prototype admitted neighbors for these rules (ordered nonunique input bound to a scalar, exact `[1]` ordered input, plain reference actual, uninstantiated template, exact redefinition, numeric `and`); the NON_NUMERICAL `excluded` case; widened and narrowed roots end to end; permuted document order.
- [x] Update `evidence_status` per rule.

### Validation

**Automated:**
- [x] New tests and `test_subset_probe_evidence.py` pass. Standing checks green.

**Manual:**
- [x] For each V probe, the port's context on the fixture equals what the oracle's occurrence facts imply (run `occurrence_parity.py capture` on any V fixture that surprises you).
- [x] R2 check per the map.

**Done when:** every refused pair of these three rules has a certified probe, the B5 variations agree with their labels (or are recorded as R2/splits), the admitted-context minimum set (spec: ES-003/ES-012 binding and ES-007 BLOCK inside an uninstantiated part def, ES-004 attribute-usage multiplicity) is certified, and the root and determinism tests pass end to end. Traces to spec "Every refusal has a probe record", "Every refused shape has an admitted-context probe", "Each implemented rule has refused and admitted fixtures", "Roots" (all three), "Output is deterministic".

---

## Phase 8: Capability/refusal matrix

### Goal

Write the matrix that places every named case, classifies and owns it, and joins it to the records.

### Assumption Under Test

Every case the spec names can be given exactly one class and owner, with the dc3 B/U cross-references placed exactly as the spec's mapping says.

### Test Stencil (Write This First)

```python
# tests/test_subset_matrix.py  (pure; reads tests/ and package data only)
FIXED = {f"ES-{n:03d}" for n in range(1, 13)} | {"SELF-BINDING", "INDEXED-REFERENCE",
         "DEEP-QUALIFIED-WIRING", "L6-LIBRARY-ALIAS-SOURCE", "G1", "G2"} | PUSH_DOWN_ROWS  # ten

def test_fixed_case_list_and_cross_references():
    rows = load_matrix()
    assert FIXED <= rows.keys()
    assert rows.by_dc3("B2") == {"ES-003"}            # not ES-004: T-001's attribution is wrong
    assert rows["ES-011"].outcome == "unconfirmed"     # U7/B9 never "refused"
    assert {r.rule for r in rows.values() if r.cls == "shared_rule"} == set(load_rule_records())
```

### Changes Required

**See design for:** [Appendix A matrix row schema](design.md#appendix-a--data-model), spec [matrix criteria and B/U mapping](spec.md#capabilityrefusal-matrix).

- [x] **Read first:** the ten `PUSH-DOWN-*-PROFILE-*` rows and `L6-LIBRARY-ALIAS-SOURCE` in `.project/backlog/BACKLOG.md`; dc3 `T-001-blocker-inventory.md` and `.project/active/toolkit-upstream-findings.md` (read-only).
- [x] `tests/fixtures/subset_profile/inventory/matrix.toml` (NEW): one row per fixed case, each with class, contexts, outcome, evidence status, owner, coverage limitation, sites (filled in Phase 9), dc3/upstream cross-references, `l2_relation` on SELF-BINDING (relation to `L2_SELF_NAMED_BINDING`, `validation/level2_structure.py:322-343`). B8 keeps its 4 NON_NUMERICAL and 4 MALFORMED_NUMERICAL apart. U8 points to Item 4 and is not classified. The binding-source classifier's five outcomes are all placed.
- [x] `scripts/subset_profile/render_matrix.py` (NEW): renders `matrix.toml` plus records to `.project/active/exec-subset-profile/evidence/matrix.md`.
- [x] `tests/test_subset_matrix.py` (NEW): schema and closed fields; fixed list; every B1–B9 and U1–U7 mapped exactly per the spec; matrix ↔ records both directions; `coverage_limitation` non-empty unless implemented in Item 1; SELF-BINDING `l2_relation` non-empty.

### Validation

**Automated:**
- [x] `tests/test_subset_matrix.py` passes. Standing checks green.

**Manual:**
- [x] Render `matrix.md` and read it once as a reviewer would, against the spec's fixed list.
- [x] Archive check: copy `tests/` and `src/` to a temp dir without `.project/` and run `pytest tests/test_subset_matrix.py` there.

**Done when:** the matrix test passes and survives the archive check. Traces to spec "Every named case has a matrix row", "The binding-source classifier is fully placed", "Every row is classified and owned", "Matrix and records agree".

---

## Phase 9: Site account and reconciliation

### Goal

Account for every candidate refusal site the scanner recognizes in codegen `b5663c07` and in agentic-mbse, each with a disposition, evidence, owner and (where known) role, joined to the matrix.

### Assumption Under Test

The hardened prototype scanner (D10) recognizes the same forms the prototype did, and the 441 / 59 counts reconcile with itemized causes.

### Test Stencil (Write This First)

```python
# tests/test_subset_site_account.py  (pure)
def test_sites_join_matrix():
    sites, matrix = load_site_account(), load_matrix()
    for s in sites:
        if s.disposition == "in_scope":
            assert s.matrix_row in matrix
            assert matrix[s.matrix_row].cls != "shared_rule" or s.rule == matrix[s.matrix_row].rule
        if s.disposition == "explicit_follow_up":
            assert s.owner and s.coverage_limitation
    for row in matrix.values():
        assert row.sites or row.no_raise_site
```

### Changes Required

**See design for:** [D10](design.md#key-decisions), spec [Inventory and site account criteria](spec.md#inventory-and-site-account) and [Inventory content](spec.md#inventory-content).

- [ ] `scripts/subset_profile/scan_sites.py` (NEW, hardened from `.project/concepts/convince-me-exec-subset/evidence/02-inventory.py`): runs on `git archive` exports; writes scanner revision and recognized forms to its output header; maps the five computed `executable_profile` sites to `REASON_CODES`; `--reconcile` exits non-zero on an unaccounted site or an orphan row.
- [ ] `tests/fixtures/subset_profile/inventory/scanner.toml` (NEW): scanner revision, recognized forms, blind spots. The blind spots include at least: silent omissions (no raise site), computed codes beyond the resolver, unrecognized exception classes or helpers, unproven public reachability.
- [ ] `tests/fixtures/subset_profile/inventory/site_account.csv` (NEW): one row per site with stable ID, disposition, evidence pointer, owner, role (or `unknown`), matrix row, rule. Seed from the prototype's `02-classification.csv`, which is an unreviewed draft: every row is re-inspected and gets its own evidence pointer. No `SI_EVIDENCE_INCOMPLETE` site is classified as a capability refusal by code alone, and no site reachable by valid input is an internal invariant.
- [ ] Fill each matrix row's `sites` list from the account.
- [ ] `tests/test_subset_site_account.py` (NEW): the join; unique IDs; closed disposition and role vocabularies; `scanner.toml` lists the required blind spots.
- [ ] Run `scan_sites.py --reconcile` and write `evidence/site-reconciliation.md`: final counts against 441 / 59, every added or removed site by ID with its cause.

### Validation

**Automated:**
- [ ] `tests/test_subset_site_account.py` and `tests/test_subset_matrix.py` pass. Standing checks green.

**Manual:**
- [ ] `--reconcile` exits 0 with zero unaccounted sites and zero orphan rows.
- [ ] Spot-check ten rows across roles against the cited code.

**Done when:** reconcile is clean and every count difference is itemized. The agentic-mbse count is final only after Phase 10's rescan at the final revision. Traces to spec "Site account is total", "Sites and matrix rows are joined", "Count reconciliation is explicit", "Blind spots are listed".

---

## Phase 10: Acceptance runs and the same-generator check

### Goal

At the final implementation revision (P-8), run the three acceptance trees, the before/after same-generator check, the `validate` diff and the final rescan.

### Assumption Under Test

The contract finds dc3's B1–B8, refuses nothing in a tree that generates, refuses nothing in the generator's accepted corpus, and Item 1 changed neither codegen's behavior nor `agentic-mbse validate`.

### Test Stencil (Write This First)

This phase is recorded runs, not pytest. The "test first" is the script's own self-check:

```python
# scripts/subset_profile/run_trees.py — the check it must print for each tree
report = run_tree(tree, roots="default")
assert report.roots_used and report.counts.declarations is not None and report.counts.occurrences is not None
assert report.identity.agentic_rev == FINAL_REV and report.identity.codegen_rev.startswith("b5663c07")
```

### Changes Required

**See design for:** [§ Probe harness step 6](design.md#probe-harness), [§ Validation Approach, Recorded runs](design.md#validation-approach), spec [acceptance criteria](spec.md#rule-records-and-evaluator).

- [ ] Commit. Record this commit as the final revision in Implementation Notes.
- [ ] `scripts/subset_profile/run_trees.py` (NEW): exports a tree, loads it with `SysideAdapter.load_model`, evaluates with default roots, writes JSON plus a markdown summary with roots used, declaration and occurrence counts kept separate, dedup applied, and every `unconfirmed` and `unverified` itemized with cause.
- [ ] **dc3 baseline** → `evidence/dc3-baseline.{json,md}`: every confirmed B1–B8 category with locations and rule IDs.
- [ ] **dc3 repaired** → `evidence/dc3-repaired.{json,md}`: zero `refused`; omissions counted (prototype saw 30 String omissions); `unverified` and `unconfirmed` itemized.
- [ ] **Codegen corpus** → `evidence/corpus.{json,md}`: counts read from `batch.json` stated (expected 14 / 23); zero `refused` on the 14 snapshot fixtures; on the 23 refusal fixtures, every `refused` code is in the recorded list or has a probe record. The evidence says snapshot fixtures prove elaboration and projection, not full generation.
- [ ] **Same-generator check** → `evidence/same-generator.md`: `probe.py run --all --agentic-rev a718efec --base` and `--agentic-rev FINAL`; codegen's v6 corpus and codegen's pytest suite in each temp tree. Results identical.
- [ ] **Occurrence parity** at the final revision → `evidence/occurrence-parity.log` updated.
- [ ] **Final rescan** → `scan_sites.py --reconcile` at the final revision, so sites Item 1 added are counted; update `site_account.csv` and `evidence/site-reconciliation.md`.
- [ ] **`validate` diff** → `evidence/validate-diff.md`: `agentic-mbse validate` on `tests/fixtures/` model directories and both dc3 trees, at `a718efec` and at the final revision, diffed. Identical.

### Validation

**Automated:**
- [ ] Standing checks green at the final revision.

**Manual:**
- [ ] Each evidence file states the identity it ran with.
- [ ] R2 check: a `refused` finding on a corpus snapshot fixture or on dc3 repaired follows the [R2 surfacing map](#r2-surfacing-map).

**How to decide what this phase can turn up:**
- A dc3 baseline category that appears only as `unconfirmed`: itemize it with its context and the missing probe, and list it for the owner. It does not block the other criteria.
- A dc3 repaired `unverified`: itemize the cause. The criterion fails unless the owner accepts the recorded limit, so list it for the owner.
- A corpus refusal-fixture `refused` with a code not in its list: add a probe for that (shape, context). It is not R2.
- A same-generator difference: the shared-module edits were not byte-faithful. Fix the code, which makes a new final revision (P-8), and rerun this phase.
- dc3 T-001 ran with agentic-mbse `8b027bbc`, not `a718efec`. Note it; do not reconcile it.

**Done when:** all eight recorded runs exist at one final revision with the outcomes above, or each deviation is itemized for the owner. Traces to spec "Baseline run accounts for B1–B8", "Repaired run refuses nothing", "The generator's accepted corpus still passes", "Consumer output is unchanged", "Site account is total" (final revision).

---

## Phase 11: Close-out: ADR, drafts, R3 proposal, re-estimate

### Goal

File the R1 decision, prepare Item 2's codegen amendment without filing it, propose R3, and re-estimate.

### Assumption Under Test

None technical. This phase turns Item 1's results into the durable records the next items need.

### Test Stencil (Write This First)

No new test. The repository checks are the gate. `adr.sh index` regenerates `INDEX.md`; confirm the new entry appears in it.

### Changes Required

**See design for:** [Appendix B](design.md#appendix-b--adr-drafts-r1), spec [Close-out criteria](spec.md#close-out).

- [ ] `.project/scripts/adr.sh new subset-profile-capability-ownership` and fill it from Appendix B.1. Provenance `[AGENT] (ratified by owner, 2026-10-18)`. Seams `[agentic-mbse, sysml-codegen, l6, guidance]`. Invariant 6 states end condition (ii): a permanent parity test in codegen CI. Include P-4's eighth abort member only if the ADR text names the vocabulary. Then `adr.sh index`.
- [ ] `evidence/adr-0012-amendment-draft.md` (NEW): Appendix B.2 with end condition (ii) filled in, the commands to run in sysml-codegen, and a header line saying it is for Item 2 to file. **Do not write into sysml-codegen.**
- [ ] `evidence/r3-proposal.md` (NEW), headed **PROPOSED — owner approval required**: one row per GENERATOR-SUBSET-PATTERNS section (`.project/backlog/item_generator-subset-patterns.md`) and per remaining gap (ES-002, ES-008, ES-009, ES-011, the ES-010 refusal side, every `unconfirmed` pair, any R2-halted pair, the ten PUSH-DOWN rows, G1/G2), each with a proposed destination item or follow-up and the reproduction result from Phase 6.
- [ ] `evidence/re-estimate.md` (NEW): re-estimated effort for Items 1 and 2. Item 2's estimate includes the permanent parity CI test (end condition (ii)), the code mapping, the screen-bypassing corpus, filing the ADR 0012 amendment, per-site codes and mutation tests, and the G1/G2 questions.
- [ ] `evidence/repository-checks.md` (NEW): final `pytest`/`mypy`/`ruff` results, which tests needed the SysIDE license, and which were skipped and why.
- [ ] `.project/CURRENT_WORK.md`: update status and the open owner items (R2, R3, any `unverified` acceptance).

The `.project/product/` entry for the shared-contract promise belongs to `/_my_close`, not this plan.

### Validation

**Automated:**
- [ ] Standing checks green.

**Manual:**
- [ ] `.project/adr/INDEX.md` lists the new entry; its body matches B.1 with (ii).
- [ ] `git -C ~/src/sysml-codegen status` shows no change.

**Done when:** the ADR is filed, the drafts and proposal exist and are marked as drafts/proposed, and the re-estimate is recorded. Traces to spec "R3 proposal is recorded", "Re-estimate is recorded", "Repository checks pass".

---

## Things This Plan Cannot Settle

Each item says how the implementer decides it.

1. **Whether codegen's `ERROR:` lines carry a usable location.** Phase 1 finds out. If not, ES-006 refused pairs stay `unconfirmed` and the gap is surfaced (Phase 1, "If the generator gives no usable location").
2. **Final `ContextId` membership and probe count.** Set by the probes under P-10. Record the final set and count in the Phase 7 completion note.
3. **Whether a disagreeing probe is a port bug or real R2/B5.** Decide by the oracle comparison in R2 map step 4. Port bug → fix and add to the seed. Agreement → R2.
4. **Whether `indexed-reference` needs SA-1.** Decided by its calc-result probe in Phase 6.
5. **Which inventory roles exist exactly.** Read from codegen `expression_evidence.py:249-347` in Phase 4 and cited in the module.
6. **Whether ES-002, ES-008, ES-009 reproduce.** Recorded either way in Phase 6. A failure to reproduce is a finding for R3, not a blocker.
7. **dc3 categories reported only as `unconfirmed`, and any repaired-tree `unverified`.** Itemized for the owner in Phase 10. The owner decides acceptance.
8. **Site-count drift from 441 / 59.** Itemized by ID and cause in Phase 9 and at the final revision in Phase 10.
9. **Whether new `reference_use` accessors are needed.** P-1 says no; the parity test decides.
10. **Effort.** About 70 probes and about 500 site rows are the large items (design § Potential Risks). If a phase will not fit one session, split it at a rule boundary (Phases 6–7) or a source-file boundary (Phase 9) and note the split here.

## Spec Criteria Trace

| Spec criterion | Phase(s) |
|---|---|
| Site account is total | 9, 10 (final rescan) |
| Sites and matrix rows are joined | 9 |
| Count reconciliation is explicit | 9, 10 |
| Blind spots are listed | 9 |
| Five computed reason sites are closed | 5 |
| Every named case has a matrix row | 8 |
| Binding-source classifier fully placed | 8 |
| Every row classified and owned | 8 |
| Matrix and records agree | 8 |
| Records are complete | 5 |
| Every refusal has a probe record | 1 (mechanism), 5 (gate), 6–7 (data) |
| Every refused shape has an admitted-context probe (with SA-1) | 6, 7 |
| Each implemented rule has refused and admitted fixtures | 6, 7 |
| Roots are reported and generator-equivalent | 2, 5, 7 |
| Baseline run accounts for B1–B8 | 10 |
| Repaired run refuses nothing | 10 |
| Generator's accepted corpus still passes | 10 |
| Failure cannot look clean | 4, 5 |
| Output is deterministic | 5, 7 |
| No consumer coupling | 5 |
| Consumer output is unchanged | 10 |
| R3 proposal is recorded | 11 |
| Re-estimate is recorded | 11 |
| Repository checks pass | every phase; recorded in 11 |

## Environment Setup

See CLAUDE.md. Specific to this item:

- `SYSIDE_LICENSE_KEY` in agentic-mbse `.env`. The test suite loads it through `tests/conftest.py`; the harness scripts source it and record only that a key was present.
- `uv` on the path. The harness builds temp trees under a configurable root (default `/tmp/subset-profile`), never inside a sibling checkout.
- Commands that shell out to the Claude CLI are not used here, so the CLAUDE.md blank-output workaround does not apply.

## Risk Management

See [design § Potential Risks](design.md#potential-risks). Phase-specific mitigations:

- **Phase 1:** the judge is tested on synthetic observations before any real probe is trusted.
- **Phase 2:** the parity seed is captured from the oracle, never hand-written, and the mutant controls prove it has teeth without dc3.
- **Phase 3:** codegen's own suite runs before and after the edit, before anything depends on it.
- **Phases 6–7:** records gain admissions only from certified probes, so every intermediate commit is R2-safe; the R2 map governs every contradiction.
- **Phase 9:** the prototype classification is a seed, not evidence; every row is re-inspected.
- **Phase 10:** one frozen revision for every run; any `src/` change restarts the phase.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-10-18. Harness at `9721bc1b` + `0ac48bc0`; observations committed with this note.

**Outcome:** 4 of 4 smoke probes certify. Every run: sysml-codegen `b5663c07e987a892e27d21e68cec40d0656574ee` (version 0.1.1), agentic-mbse `0ac48bc0d9333164969cebf204e79958ff2e6d2f` (version 0.1.3), SysIDE 0.8.4, Python 3.12.3, `uv.lock` sha256 `a17e9fa1…aacabee4d4`, all three package `__file__` paths inside the temp tree, license key present. No R2: both refused probes exited 1 with the expected code.

| Probe | Exit | Observed | Certifies |
|---|---|---|---|
| `binding-source__expression_source__owner_instantiated` | 1 | `SI_EXPRESSION_SOURCE_UNSUPPORTED` at `root-0/model.sysml:7` (construct line 7) | yes |
| `conditional-expression__conditional_unresolved_branch__calc_definition_feature_value` | 1 | `SI_EVIDENCE_INCOMPLETE` at `root-0/model.sysml:3` (construct line 3) | yes |
| `invocation-callable__explicit_operator__attribute_value` | 0 | positive control `fx__site__eff__eff` in the catalog outputs | yes |
| `string-value-omission__string_value__attribute_value__redefinition_shorthand` | 0 | `fx__gen__fuel_unit` absent from catalog and all generated text; sibling `fx__gen__rate` present | yes |

**Location question (Things This Plan Cannot Settle, item 1): settled, usable.** Codegen appends `[root-<slot>/<path>:<line>]` to each finding when it measured one (`elaborate.py:134-144`, `:192-200`) and omits it otherwise; `unexpected_public_failure` (`elaborate.py:170-190`) deliberately carries none. A finding without a location fails the judge (`location_missing`). Format recorded in the judge's module docstring.

**Actual Changes:**
- `tests/helpers/subset_probe_judge.py` (new, pure, stdlib only): `load_probe`, `parse_error_lines`, `judge` → `Certification(failed_check)` with `certifies` as a property, `observation_to_json` / `load_observation`. Pins (`PINNED_CODEGEN_REV`, `PINNED_SYSIDE_VERSION`, `PINNED_UV_LOCK_SHA256`) live here. `FailedCheck` is a closed enum; the first failing check is reported. Outcome expectations are a union (`Refused` / `Admitted` / `Omitted`), so no field is optional per outcome.
- `tests/test_subset_probe_judge.py` (new): 40 tests. Covers the stencil cases, each outcome certifying, R2 signal (`refused_probe_admitted`), location missing / wrong file / out of range, extra codes, identity mismatch (codegen rev, unresolved agentic rev, SysIDE version, lock hash, each package outside the tree, a `<tree>-other` prefix trap, missing key), timeout, probe-id mismatch, edited model, real codegen lines, JSON round trip, and probe-definition errors.
- `scripts/subset_profile/probe.py` (new), `scripts/subset_profile/README.md` (new).
- Four probes under `tests/fixtures/subset_profile/probes/`, models copied verbatim from the prototype fixtures, each with `observation.json`. Run logs in `evidence/probes/<id>.log`.

**Validation run:**
- Judge tests: 40 pass. Teeth check: three mutants (location range disabled, omission presence disabled, model-hash check disabled) are each caught by at least one test.
- Manual control: a copy of the conditional observation with the location moved to line 7 re-judges as `location_outside_construct`.
- New files: `ruff check`, `ruff format --check` clean; `mypy --strict` clean on the judge and the script; plain `mypy` clean on the test file.
- `git status` of `~/src/sysml-codegen` and `~/src/dc3` empty before and after the run, HEADs unchanged (`b5663c07`, `60b44d53`). No license key value in any probe file or log.

**Issues:**
- **Standing checks were already red at the phase's start (`1002997d`), and Phase 1 does not change that.** On a clean `git archive` of `1002997d`: `ruff check src/ tests/` reports 118 errors, `ruff format --check src/ tests/` would reformat 77 files, `mypy src/` reports 97 errors in 19 files. `pytest tests/` has 3 failures, all environmental: `test_index.py::TestScriptBackwardCompat` (2) points at a stale path `/home/reid/1cfe/agentic-mbse`, and `test_equations.py::TestDetectEquations::test_returns_detected_equations` needs PIL, which is not installed. Phase 1 adds no failure (2819 pass). The standing rule "a phase is not done until all pass" cannot be met by any phase without an unrelated repo-wide cleanup. **Surfaced for the owner:** either scope the rule to "no new failures, new files clean" or schedule the cleanup separately. I applied the first reading and did not touch unrelated files.
- sysml-codegen `b5663c07` commits five absolute symlinks under `.claude/` (to `/home/reid/1cfe/agentic-mbse/...`). Python's tar `data` filter refuses them. The harness skips absolute links under `.claude/` only, names each on the console, and aborts on an absolute link anywhere else (`probe.py` `_assistant_links_skipped`).
- The parser's first draft missed every finding, because the first code follows the gate's `": "`, not the line start. The test on real codegen lines caught it before any probe ran.

**Deviations:**
- **Conditional probe context is `calc_definition_feature_value`, not the plan's `binding_value`.** Codegen locates the refusal at line 3, the `return r : Real = if a < b ? a else b` in calc def `Min2`, not at the binding on line 7. The probe was refused as expected, so this is not R2 and the fixture is unchanged; the context label names where the construct actually is. Appendix C already lists this fixture under "binding or calc-definition feature value". A `binding_value` conditional probe is still needed in Phase 6.
- **Probe ID scheme:** `<rule>__<shape>__<context>[__<variant>]`, with rule IDs hyphenated as in design Appendix A. The optional variant exists because one (shape, context) pair will have several probes (spellings now, B5 variation probes in Phase 7). The string probe uses variant `redefinition_shorthand`; the attribute-declaration spelling is still to probe.
- **The admitted invocation neighbor uses shape `explicit_operator`,** which no record has yet: the plan named no shape for it. Phase 5 must decide whether a neighbor probe keys a record admission or only serves as a control that the rule does not fire.
- **"Positive control" for an admitted probe is the catalog name the construct itself generates** (`fx__site__eff__eff`). Exit 0 alone could hide a dropped construct. For omission it is the numeric sibling (`fx__gen__rate`), as review m3 asks.
- **Additions beyond the plan:** the observation records the model's sha256 and the judge fails `model_changed` when it no longer matches, so editing a probed model invalidates its evidence. The harness also snapshots codegen's `git status` and HEAD before and after the run and aborts on any difference. It refuses uncommitted or dirty probe fixtures, and `--base` refuses any revision other than `a718efec`.
- **Test-first order:** the judge and its tests were written in one pass rather than test-then-fail. The mutant check above stands in for "see it fail for the right reason".

### Phase 2 Completion
**Completed:** 2026-10-18. Port at `d244991c`, captures at `427239ae`, evidence logs with this note.

**Outcome:** the parity test passes on all 34 seed cases; the recorded run matches on **73 of 73** (34 seed, 37 codegen corpus, both dc3 trees); the controls bite. No parity case needed a port change after its first run. Run identity: codegen `b5663c07`, agentic-mbse `427239ae`, SysIDE 0.8.4, Python 3.12.3, `uv.lock` `a17e9fa1…`.

| Check | Result |
|---|---|
| `test_occurrence_parity.py` | 34/34 seed cases match their oracle capture; 34/34 captures carry the pinned oracle identity |
| `occurrence_parity.py compare --all` (`evidence/occurrence-parity.log`) | 73/73 match, and every stored `expected.json` equals today's oracle. The four abort cases match on stage and code. dc3 repaired: codegen's full graph also agrees |
| Mutant controls on the seed only (`evidence/occurrence-parity-controls.log`) | `no_effective_decl` 1/34 (only the new P-6 fixture), `writer_is_base` 1/34 (`f1_calc_redefined_everywhere`), `typed_anywhere` 12/34, `declared_multiplicity` 0/34 (not catchable, F1 Surprise 1) |
| `python -I` import check | `sysml_codegen` never imported |
| Selector-ownership gate | 20/20 green, file unchanged. P-1 holds: no new `reference_use` accessor was needed |

**Actual Changes:**
- `src/agentic_mbse/sysml/occurrence_facts.py` (new, pure): `OccurrenceAbort` (9 members), `BuildStage`, `MultiplicityResolution`, `MultiplicityReading` (resolution computed in codegen's check order; `__post_init__` refuses a reading holding bounds the generator never reads), `PathStep`, `UsageVisit` (one per usage per parent occurrence, so counts are per parent, review S4), `OccurrenceNode`, `OccurrenceScope`/`PackageScope`, `AttachmentCause`, `CalcAttachment`, `WriterSelection`, `OccurrenceStructure` (order validated at construction; `selected_scopes` / `overridden_scopes` per usage for Implementation Note (a)), `OccurrenceFailure`.
- `src/agentic_mbse/sysml/fact_refs.py` (new, pure): `ElementRef`, `SafeLocation`.
- `src/agentic_mbse/sysml/occurrence_extraction.py` (new): `extract_occurrence_structure(model, extra_roots=())`, ported function by function. The docstring keeps the codegen line map with an abort-member column (P-5) and names G1/G2 as mirrored. Also public `declaration_id`, `semantic_owner`, `safe_location` for Phase 4.
- `tests/helpers/occurrence_oracle_schema.py` (new, P-3): `to_oracle_schema`, `strip_oracle_only_fields`, `schema_differences`, and the only `SI_*` mapping tables.
- `scripts/subset_profile/occurrence_parity.py` (`capture`, `compare --all`, `controls`), `occurrence_oracle.py` (the F1 oracle, logic unchanged), `occurrence_port_run.py` (runs the exported port in the tree).
- `tests/fixtures/subset_profile/occurrence/<case>/{model.sysml, expected.json}`: 11 F1 edge + 22 prototype + `f1_effective_declaration_slot` (P-6). `tests/fixtures/subset_profile/cases/roots_mixed_owners.sysml`.
- Tests: `test_occurrence_parity.py` (69), `test_occurrence_facts.py` (26, includes a subprocess purity check), `test_occurrence_extraction_roots.py` (4).

**Validation:** standing checks green by the "Green, defined" note: `pytest tests/` 2918 pass, the same 3 environment failures; `ruff check src/ tests/` 118 (baseline); `mypy src/` 97 errors in 19 files, none in new files. New files pass `ruff check`, `ruff format --check` and `mypy --strict`. Sibling `git status` empty before and after every run.

**Issues:**
- **P-6 fixture shape.** An inherited redefinition (`part def B :> A { part :>> x; }`) does not put both declarations in `usage.usages`. The shape that does is the one dc3 uses: a usage typed by a definition and subsetting a sibling that redefines the definition's feature (`part rack_a : Rack :> racks`). The package name `f1p` was picked so the effective declaration is the smaller UUID; four other spellings made it the larger, which the mutant would have kept by luck.

**Deviations from Plan:**
- **The abort vocabulary has 9 members, not 7 + 1.** P-4's `IDENTITY_UNSTABLE` plus `EFFECTIVE_DECLARATION_AMBIGUOUS` for `occurrence.py:249-285` (no unique effective declaration for one slot), which no Appendix A member names. `REDEFINITION_ROOT_FAMILY` covers the slot-index family raises and the calc slot with ≠1 root (`elaborate.py:1209-1222`). `WRITER_AMBIGUOUS` covers both most-specific-definition raises and `_require_one_writer`.
- **`extract_occurrence_structure` returns `OccurrenceStructure | OccurrenceFailure`, not `| FactFailure`.** `FactFailure` belongs to Phase 4 (it is keyed by `FactKind`, which spans kinds this module does not know). `OccurrenceFailure` also records the `BuildStage`, which parity compares. Phase 4 wraps it as `FactFailure(OCCURRENCE, abort)`. A SysIDE adapter error (`SemanticEvidenceError`) is not a generator abort and propagates for Phase 4 to record.
- **New pure module `fact_refs.py`** holds `ElementRef` and `SafeLocation`, because both the occurrence and the subset facts need them and neither should import the other's module for it. Phase 4's `subset_facts.py` imports them from there.
- **The occurrence structure is id-based.** It holds declaration UUIDs, not `ElementRef`s; Phase 4 builds refs where a fact needs a name or location. Appendix A's `Attachment.scopes_by_root` and `WriterSelection.selected_scopes_by_root` are per-scope records instead (each scope carries its root), with counting methods on the structure.
- **Caller roots (D7):** a caller root that is already a generator root adds nothing; any other is traversed after the generator's roots in its own occurrence namespace, so its paths cannot collide with generator paths. An abort while traversing a caller root fails the whole structure (honest, and unreachable on the seed). A non-`PartUsage` extra root raises `TypeError`.
- **Duplicate occurrence identity mirrors codegen exactly:** it aborts only when the second occurrence differs from the first (`existing != occurrence`, `occurrence.py:1033`). The spike aborted on any repeat.
- **Abort cases compare `fatal` only.** In all four seed abort cases codegen's strict first error equals the abort, so nothing is hidden on the seed; a case where a multiplicity refusal precedes an abort would compare on the abort alone.
- **A writer-stage abort has no oracle equivalent** (the oracle records `writers_status: error` and keeps the occurrences). No seed or corpus case has one; if one appears, the comparison reports a mismatch.
- **Two scripts beyond the plan's one:** the oracle and the port runner execute inside the tree's codegen venv, so they are separate files that `occurrence_parity.py` starts. `controls` is a subcommand of `occurrence_parity.py` and runs in-process against the stored seed expectations.
- **Test-first order:** the port was ported before its tests, because the oracle captures are its specification and could only be taken once it was committed. The parity test then ran red (no captures) before the capture, and the controls stand in for "see it fail for the right reason".

### Phase 3 Completion
**Completed:** 2026-10-18. Edit at `83f48525`; codegen-suite runner at `1f1fa7e9`, `c347dba6`, `175dbd13`.

**Outcome:** the refactor is byte-faithful for codegen. Codegen's own pytest suite gives identical per-test results with agentic-mbse at the design base, just before the edit and at the edit; the four smoke probes are unchanged.

| Run (codegen `b5663c07`, isolated tree) | agentic-mbse | Result |
|---|---|---|
| base | `a718efec` | 2685 passed, 53 failed, 7 errors, 9 skipped |
| before the edit | `c347dba6` | 2685 passed, 53 failed, 7 errors, 9 skipped |
| after the edit | `83f48525` | 2685 passed, 53 failed, 7 errors, 9 skipped |
| `codegen_suite.py diff` base→after, before→after | | 2754 tests compared, 0 differ: IDENTICAL |

The 60 failures and errors are the same tests in every run and are environmental: codegen's study and ledger tests need a git work tree (`RootError: no project root`, `git status` / `git diff` over the exported package), and a `git archive` export has none. Logs: `evidence/same-generator-phase3.log`, per-test JSON and full output in `evidence/codegen-suite/`.

Smoke probes at `83f48525`: 4/4 certify, and every observation field except the agentic-mbse revision is identical to Phase 1's (`evidence/smoke-probes-phase3.md`). The committed `observation.json` files stay at Phase 1's revision.

**Actual Changes:**
- `src/agentic_mbse/sysml/invocation_allowlist.py` (new, pure): `STANDARD_SUM_FUNCTION_ID`, `SUPPORTED_INVOCATION_IDS`, `is_supported_invocation_id`, and `InvocationUse` (callable id and name, authored text, location; `supported` is computed from the predicate).
- `src/agentic_mbse/sysml/reference_use.py` (edit): imports the allowlist; `_require_supported_invocation` calls the predicate through `_is_supported_invocation`, and its raise and message are unchanged; the function-id and diagnostic reads are factored into `_invoked_function_id`, `_invocation_reference`, `_invoked_function_name`, shared by the raise and the new walk. New public `invocation_uses(expression)`: same dispatch order as `_walk`, resolves no reference, refuses nothing, raises the walk's named codes (`EXPRESSION_DEPTH_EXHAUSTED` with operation `invocation_uses`, `OPERAND_ITERATION_FAILED`, a malformed unit annotation). One line was reformatted by `ruff format` (`ExactSemanticPath(...)` in `_reference_use`), needed for the modified file to pass the format check.
- `scripts/subset_profile/codegen_suite.py` (new): `run --agentic-rev REV --label NAME` and `diff A B`, per-test outcomes from JUnit XML.
- Tests: `test_invocation_allowlist.py` (4, includes a subprocess purity check), `test_invocation_uses.py` (16: the stencil cases plus nested calls and a conditional, a property test that the reference walk raises exactly when `invocation_uses` reports an unsupported call, and the depth failure). `test_reference_use.py` unchanged and green; selector-ownership gate green.

**Validation:** `pytest tests/` 2938 pass, the same 3 environment failures; `ruff check src/ tests/` 118 (baseline); `mypy src/` 97 in 19 files (baseline), none in new or edited files. New and edited files pass `ruff format --check`; the new modules pass `mypy --strict`. Red check: with the `reference_use` edit stashed, both new test files fail on the missing import.

**Issues:**
- The first codegen-suite runs failed with "No module named pytest": plain `uv sync --frozen` does not install codegen's `dev` extra. The runner now adds `uv sync --frozen --extra dev` (same lock). The first `-rA` parse also lost 41 parametrized ids containing spaces; outcomes now come from JUnit XML.

**Deviations from Plan:**
- **`_is_plural_invocation` keys on `sum`'s identity, not on the allowlist predicate.** Plurality is `sum`'s collection semantics. Keying it on the allowlist would make any callable added later consume a collection. The two are the same set today, so behavior is unchanged; `_require_supported_invocation` and `invocation_uses` use the predicate, as planned.
- **`InvocationUse` lives in `invocation_allowlist.py`,** not `reference_use.py`, so Phase 4's pure `subset_facts.py` can hold it without importing a SysIDE reader.
- **Three codegen-suite runs, not two:** `a718efec` (the plan's comparison point) and `c347dba6` (immediately before the edit) as "before", `83f48525` as "after", per the brief.
- **Test-first order:** the module and tests were written in one pass; the stash check above stands in for watching them fail first.

### Phase 4 Completion
**Completed:** 2026-10-18. Code at `a171a85e`.

**Outcome:** every fact kind is extracted once, totally. Injected failures surface as structured `FactFailure`s and the other kinds keep reporting. Both dc3 trees return with failures listed, none raised (`evidence/subset-facts-dc3.log`, at `a171a85e`):

| Tree | Enumerated | Facts | Failures |
|---|---|---|---|
| dc3 baseline `808464df` | all 7 kinds | 280 bindings, 632 sites (23 with an unsupported call, 5 with a conditional and `RESOLVED_TARGET_MISSING`), 164 assertions, 139 part usages (72 unexpandable visits, as F1), 32 Strings | 22, all `BINDING_SOURCE` / `EXPRESSION_KIND_UNSUPPORTED` (bindings whose walk meets an unsupported call) |
| dc3 repaired `60b44d53` | all 7 kinds | 391 bindings (all single reference), 755 sites, 99 assertions, 167 part usages (0 unexpandable), 30 Strings (the prototype's 30) | 0 |

No content is asserted yet; that is Phase 10. The recorded parity run was repeated at `a171a85e`, because this phase touched the port (73/73 match, controls unchanged; logs overwritten at that revision).

**Read first, recorded in `subset_extraction.py`'s docstring table:**
- Inventory roles (`expression_evidence.py:281-347`): every QN-bearing feature with a value. Owner is a calc def → `calc_definition_dependency`; owner is a calc or constraint usage → `binding`; otherwise a plain reference after the unit is stripped → `alias`, anything else → `computed_attribute`. Plus each constraint definition's and usage's `result_expression` (subtypes included) → `constraint_predicate`. That answers Things This Plan Cannot Settle item 5.
- Calc inputs (F3, `elaborate.py:1878-1955`): owned members whose direction reads `in` (`:1684-1685`) and that carry a value. The unit annotation is stripped once (`:1918-1921`).
- Binding class (`elaborate.py:2130-2171`): literal first, then expression unless there is exactly one inventoried use and the expression is a reference metatype (`:1114-1118`), then indexed or exact. Self-binding is the exact leaf equal to the formal (`binding_source.py:87-89`).

**Actual Changes:**
- `src/agentic_mbse/sysml/subset_facts.py` (new, pure): `FactKind`, `ScopeCause`, `FactFailure` (cause validated as a closed code), `OwnerKind`, `BindingKind`, `BindingSourceFact`, `SiteRole` (5 inventory roles plus `calc_result_expression`, `other_expression_site`), `ReferencesWalked`/`ReferencesFailed`, `InvocationsWalked`/`InvocationsFailed`, `SiteInspection`, `ExpressionSiteFact`, `AssertionOwnerFact`, `PartMultiplicityFact`, `StringSpelling`, `StringValueFact`, `SubsetFacts` (order and enumerated-versus-present consistency validated at construction). `IdentifiedConstraintFacts` is imported for typing only, so the module stays parser-free.
- `src/agentic_mbse/sysml/subset_extraction.py` (new): `extract_subset_facts(model, extra_roots=())`. One `_Collector.collect` turns each kind's population into facts, per-element failures and enumeration failures. `_is_reference_expression` is the one metatype test. Conditionals are found by a structural walk over `reference_use`'s operand primitives (`operand_bearing_operands`, `unit_annotation_value`, `MAX_EXPRESSION_DEPTH`).
- `occurrence_facts.py` / `occurrence_extraction.py`: `PartUsageReading` and `OccurrenceStructure.part_usages`, one per user part usage, read by the port with no parent. This is where `PartMultiplicityFact.shape` comes from, so multiplicity is never re-read.
- `fact_refs.py`: `ElementRef.qualified_name` may be `None` for an anonymous element (its UUID is then session-local). `SafeLocation.sort_key`.
- Fixtures `tests/fixtures/subset_profile/cases/{binding_kinds, expression_sites, assertion_owners, string_spellings, conditional}.sysml`, all loading without diagnostics.
- Tests: `test_subset_extraction.py` (12: per-kind, the two stencil tests, invocation-walk failure, enumeration failure, occurrence abort, determinism, a mixed failing model), `test_conditional_operator_spelling.py` (learning test), `test_subset_extraction_no_reinterpretation.py` (AST gate with an anti-vacuity case).

**Validation:** `pytest tests/` 2954 pass, the same 3 environment failures; `ruff check src/ tests/` 118 (baseline); `mypy src/` 97 in 19 files (baseline), none in new files. New and edited files pass `ruff format --check`; the five fact modules pass `mypy --strict`. The selector-ownership gate is green: the new extraction reads no reviewed selector.

**Issues:**
- `ref` and `alias` are SysML keywords, so fixture names avoid them (`src`, `mirror`).
- `[SI::one]` on a `Real` value is a SysIDE type error, and `ScalarFunctions` plus `SI` makes `min` ambiguous with `SI::min` (minute). The fixtures use plain arithmetic and qualified calls.

**Deviations from Plan:**
- **`xs#(1)` bound to an input is `other_expression`, not `indexed`.** The stencil listed `idx: indexed`. The generator classifies a binding as indexed only when its one use is indexed and the expression is a reference metatype; a bare `IndexExpression` is neither a chain nor a reference, so it is an expression source (`elaborate.py:2155-2160`). A chain with an indexed head (`qs#(1).v`) is `indexed`, and the fixture now has both. In practice the inventory refuses any indexed use first, so this only matters for the fact's faithfulness. The stencil's `ref` became `src` (keyword).
- **The binding reference walk runs before classification,** including for literals, as the generator's inventory does. So a walk failure on a literal binding is a failure, not a `literal` fact (the stencil expects `bindings == ()` under an injected walk failure).
- **Assertion owners come from the constraint extractor's identified usages.** Each is a form from `_classify`, carried over without re-classification, plus `semantic_owner` of the live element. `ASSERTION_OWNER` is enumerated only when `CONSTRAINT` is.
- **Strings:** a `String`-typed (standard-library `ScalarValues::String`, through `types`) `AttributeUsage` or undirected `ReferenceUsage` that carries a value. A `ReferenceUsage` is the `:>>` shorthand spelling, as the prototype found.
- **Added roles and owner kinds** beyond Appendix A's sketch: `SiteRole` names the generator's five inventory roles rather than a shorter list, and `OwnerKind` is a closed enum, where Appendix A left `owner_kind` untyped.
- **Test-first order:** fixtures were explored against SysIDE first, then tests and code written together; the tests passed on their first run, so the anti-vacuity case in the AST gate and the injected failures are the evidence that they bite.

### Phase 5 Completion
**Completed:** 2026-10-18.

**Outcome:** the pure evaluator, the record loader with its evidence gate, the closed vocabularies and the version pin exist and pass every pure test. With the packaged records as committed, the only outcome other than `unconfirmed` the evaluator can produce is the String omission: the two refused smoke pairs cannot land until their admitted-context partners do (see Deviations). On the four smoke models (`/tmp` run, at this commit's code):

| Smoke model | Verdict | Findings |
|---|---|---|
| `binding-source__expression_source__owner_instantiated` | unconfirmed | `binding-source/expression_source @owner_instantiated` → unconfirmed, 1 occurrence |
| `conditional-expression__…__calc_definition_feature_value` | incomplete | `conditional-expression/conditional_unresolved_branch @calc_definition_feature_value` → unconfirmed; `indexed-reference` unverified on the same site (its reference walk failed, so whether it holds an index is unknown) |
| `invocation-callable__explicit_operator__attribute_value` (control) | clear | none |
| `string-value-omission__…__redefinition_shorthand` | clear | `string-value-omission/string_value @attribute_value` → omitted |

**Actual Changes:**
- `src/agentic_mbse/sysml/subset_profile.py` (new, pure): `SUBSET_PROFILE_VERSION`, `SUBSET_REASON_CODES` (16, disjoint from `REASON_CODES`), `Outcome`, `Verdict`, `ContextId` (17 members, each with its generator citation), `EvidenceStatus`, `Qualification`, the record types and `load_rule_records` / `load_packaged_rule_records`, eight rule functions that return a shape and a context and never an outcome, and `evaluate_subset_profile(facts, rules=PACKAGED_RULES, roots=GENERATOR_ROOTS)`.
  - Roots are a closed union, `GeneratorRoots | ExplicitRoots`, not a `None` sentinel. An explicit root that is neither a generator root nor an extracted caller root is a caller error (`ValueError`).
  - Placement: a calc usage's binding is `owner_instantiated` / `owner_package` where it is the selected writer under the roots in use, `writer_overridden` where it attaches but never wins, `beyond_generator_roots` where only a caller root reaches it, `owner_other` when the owner attaches nothing, and otherwise `owner_uninstantiated`. A constraint usage is placed the same way without writer selection.
  - Loader rules, all `RecordError`: unknown or missing keys; anything outside the closed vocabularies; exactly the implemented rules and shapes, in order; `fact_requirements` equal to what the rule function reads; any listed outcome without evidence; non-probe evidence for anything but `admitted`; a corpus citation outside the 14 snapshot fixtures; a probe id that names another pair; `unconfirmed` listed explicitly; an always-unconfirmed context listed; a refused shape without an `expected_code`; a refused shape without an admitted-context probe or an SA-1 statement; an SA-1 statement beside an admitted probe or not covering every computable context with a refusal; `evidence_status` disagreeing with the admissions; `example_probe` present without evidence or missing with it; `generator_evidence` empty exactly when no shape has an expected code.
- `src/agentic_mbse/sysml/subset_profile_rules.toml` (new): all eight rules and their shapes, remedy, semantic limits, doc anchor, generator citations. One admission: the String omission, citing its smoke probe. `uv build` ships it (`agentic_mbse/sysml/subset_profile_rules.toml` in the wheel); `pyproject.toml` unchanged.
- Facts: `OccurrenceStructure.constraint_attachments` (the port now runs its one `_attachment` for every constraint usage, subtypes included, as `_build_constraint_nodes` does at `elaborate.py:1325-1332`); `CalcAttachment` renamed `Attachment` (Appendix A's name) since it now serves both; `AssertionOwnerFact.asserted`, read in extraction from the constraint extractor's own `_ASSERTED_FORMS`, so no decision re-lists the asserted forms.
- Judge (`tests/helpers/subset_probe_judge.py`): a required probe `kind` (`record`, `control`, `reproduction`); an `excluded` expectation (checked like `omitted`); and the location form `SI_CONSTRAINT_BLOCKED` uses (below). The four smoke `probe.toml` files gain `kind`; their models and observations are unchanged.
- Tests: `test_subset_profile_records.py` (40), `test_subset_profile_evaluate.py` (23), `test_subset_profile_vocabulary.py` (13), `test_subset_profile_coupling.py` (5), `test_subset_profile_hygiene.py` (1), `test_subset_profile_version.py` (2), `test_executable_profile_computed_reasons.py` (5), `tests/test_subset_probe_evidence.py` (11 at this phase), five new judge tests. Helpers `tests/helpers/subset_records.py` (a small TOML writer, so every test record goes through the real loader) and `tests/helpers/subset_synthetic.py`.

**Validation:** `pytest tests/` 3059 pass, the same 3 environment failures; `ruff check src/ tests/` 118 (baseline); `mypy src/` 97 in 19 files (baseline), none in new or edited files. New and edited files pass `ruff check` and `ruff format --check`; the five fact and profile modules and the judge pass `mypy --strict`. Teeth: three evaluator mutants (ignore unverified in the verdict; default an unlisted pair to `refused`; drop the beneath-refused-multiplicity guard) are each caught. The coupling scan caught a real slip on its first run (a generator code named in a record's prose field) and the prose was reworded.

**Computed reasons:** the five sites are still at `executable_profile.py:542`, `:597`, `:660`, `:711`, `:813`. Each test drives its site through the walk over every operand fact the closed category vocabulary allows and asserts every emitted reason is in `REASON_CODES`, and that the site was reached.

**Issues:**
- **`SI_CONSTRAINT_BLOCKED` carries no finding location.** It is diagnosed without one (`elaborate.py:1353-1360`); the only location on its line is the executable profile's own measured location of the blocked construct, appended to the detail as `[model.sysml:6]` (`_render_block_reason`, `elaborate.py:448-457`), observed on the prototype fixture in a scratch tree. Under the judge as written every ES-007 refused probe would fail `location_missing`. The judge now reads that suffix for this one code, and only when the finding has no `root-N/` location, and it must name the probe's model file and fall inside the construct. This applies invariant 2's location check to the location the generator does print; it is not a weaker check, but it is a change to the certification rule, so it is recorded here for the owner.
- **The ES-006 refusal leaves `indexed-reference` unverified on the same site.** The reference walk is what fails, so whether that expression also holds an index is unknown. This is honest and makes any model with a refused conditional `INCOMPLETE`; it matters for Phase 10's dc3 baseline.

**Deviations from Plan:**
- **P-7: the two refused smoke pairs are not in the records yet.** The loader enforces invariant 3 (a refused shape needs an admitted-context probe or SA-1), and neither pair has its partner until Phases 6–7. They are named in `AWAITING_ADMITTED_PARTNER` in `tests/test_subset_probe_evidence.py`, which must be empty when Phase 7 ends. The plan's stencil citing the binding pair from the packaged records became a test on synthetic records.
- **The `invocation-callable` smoke probe is a `control`, not an admission.** Its shape `explicit_operator` is not a rule shape: the rule never recognizes an explicit multiply. A control probe certifies that the generator runs the model, and the evidence test asserts the evaluator reports no finding of its rule at the construct and no `refused` anywhere in that model. This answers Phase 1's open question; the other prototype neighbors (part-owned assert, literal and plain-reference bindings, exact multiplicity, numeric `and`) are controls for the same reason.
- **`ContextId` drops `ATTRIBUTE_USAGE` and `EVERYWHERE` (P-10).** `part-multiplicity` reads only part usages, so an attribute usage with an ordered or ranged multiplicity is a control probe, not a context. The String omission uses `attribute_value`, the context its smoke probe already names.
- **Shapes added:** `conditional-expression/conditional_resolved_branches`, for a conditional whose reference walk succeeds. No probe has observed it, so it reports `unconfirmed` rather than nothing. Reason IDs for ES-001 are `calc_owned_asserted_constraint` and `calc_owned_non_asserted_constraint`, because Appendix A's names (`constraint_owned_by_calc_definition`, `…_calc_usage`) name a context, not a shape.
- **Beneath a refused multiplicity:** "not instantiated" becomes `beneath_refused_multiplicity` (always `unconfirmed`) whenever the generator roots in use visit any multiplicity they cannot expand. This is conservative: the facts do not say which definitions sit beneath the refused usage, so no "never examined" claim is made in a model that has one. The dc3 repaired tree has none.
- **Evidence status** is computed, not authored: `probe_observed` when every shape has a probe-observed admission, `partial` when some do, `code_read_pending_item_2` when none do. The loader rejects a disagreeing value. `example_probe` is absent exactly while the status is pending.
- **"Fails at load" is split by where the evidence lives.** The packaged loader cannot see `tests/`, so it enforces that every listed outcome cites well-formed evidence of its own pair. Whether each cited probe exists, is a `record` probe expecting the recorded outcome, certifies, and ran at `verified_against` is enforced by `tests/test_subset_probe_evidence.py`, along with the evaluator reproducing it on the probe's own model.
- **Version pin:** `test_subset_profile_version.py` maps each version to one digest of the records bytes plus the allowlist ids. `subset-profile/v1` is re-pinned as Phases 6–7 add evidence (nothing has shipped).
- **"Pure" tests import SysIDE indirectly** through `IdentifiedConstraintFacts` (defined in `constraint_extraction`). They load no model and need no license. The decision module itself stays SysIDE-free (hygiene test).

### Phase 6 Completion
**Completed:** 2026-10-18. Probes authored at `47614c26`, run there (`run --all`, 33 of 34 certified first time); records at `2a37a9c4`.

**Outcome:** every refused pair of the five model-wide rules has a certified probe and an admitted-context probe, or (asserted calc-owned constraints) an SA-1 statement, and the evaluator reproduces each on its own model. **No R2:** no refused probe was admitted. 23 certified probes are cited by the records; 5 controls and 6 candidate reproductions certify and are not cited.

| Rule / shape | Refused (probe-observed) | Admitted (probe-observed) | Unconfirmed |
|---|---|---|---|
| `calc-owned-assertion/asserted_constraint` | `calc_definition_owner`, `calc_usage_owner` | none; SA-1 statement (`elaborate.py:1625`, `:794-820`) | — |
| `calc-owned-assertion/non_asserted_constraint` | `calc_usage_owner` | `calc_definition_owner` | — |
| `indexed-reference/indexed_reference` | `attribute_value`, `binding_value`, `calc_definition_feature_value`, `constraint_predicate` | `other_expression_site` | `calc_result_expression` |
| `invocation-callable/unsupported_callable` | same four (`attribute_value` by `product`, `size` and `max`) | `other_expression_site` | `calc_result_expression` |
| `conditional-expression/conditional_unresolved_branch` | same four | `other_expression_site` | `calc_result_expression` |
| `conditional-expression/conditional_resolved_branches` | — | — | every context |
| `string-value-omission/string_value` | — | omitted at `attribute_value`, both spellings | — |

Candidate reproductions (for R3, `kind = "reproduction"`, no record cites them):

| Candidate | Result | Observed |
|---|---|---|
| ES-002, constraint binding a calc usage's input (dc3 U5) | reproduced | `SI_OCCURRENCE_MISSING` at the binding, "semantic owner kind 'CalculationUsage' cannot anchor containment" |
| ES-008, named subsets nested in named subsets (dc3 U2) | reproduced, in one of five spellings | `SI_REDEFINITION_INVALID` "incomparable value writers", only when the nested subsets each redefine a value (`psu.efficiency`); plain nested subsets with exact multiplicities generate |
| ES-009, composition by subsetting a top-level usage (dc3 U6) | reproduced | `SI_OCCURRENCE_MISSING` "exact owner address has no target" on `facility.area` |
| ES-010 refusal side, a String bound to a calc input | reproduced | `SI_RENDERING_COLLISION` at projection ("the public EntryPoint seam cannot carry non-numeric default") |
| A calc def whose result is a bare expression (new) | reproduced, arithmetic and `max` | `SI_EVIDENCE_INCOMPLETE` "extracted with zero output attributes", whatever the expression holds |

**Actual Changes:**
- 30 probe directories under `tests/fixtures/subset_profile/probes/` (23 record, 1 new control per model-wide neighbor plus the existing explicit-multiply control, 6 reproductions). Prototype fixtures re-run through the harness (D9): `es001_refused_calc_def_assert`, `es001_refused_calc_usage_assert`, `es001_admitted_part_assert`, `es005_refused_product`, `es005_refused_size`, `es006_admitted_arithmetic_min`, `es010_admitted_numeric_value`, `es010_refused_string_calc_input`. The others are Phase 7's or were Phase 1's.
- `subset_profile_rules.toml`: the admissions above; `verified_against.agentic_rev = 47614c26`; the observed limits written into each site rule's `semantic_limits` and the String rule's.
- Judge: a refusal gate may have several colon-free segments (the projection gate is "Code generation failed: exact graph projection failed:"). Only the ES-010 reproduction's verdict changed under the fix; it was re-run at `2a37a9c4` and certifies.
- `tests/test_sysml/test_subset_profile_rules_modelwide.py` (35): each record probe of the five rules reproduced at its construct; each control draws no finding of its rule and no refusal; no rule refuses a candidate reproduction; the calc-usage-owned constraint is reported on the constraint; both String spellings omitted.
- `AWAITING_ADMITTED_PARTNER` now holds only the binding-source smoke probe.
- Occurrence parity re-recorded at `b2d5768d` (the port gained constraint attachments in Phase 5): 73 of 73 match (`evidence/occurrence-parity.log`).

**Validation:** `pytest tests/` 3194 pass, the same 3 environment failures; `ruff check src/ tests/` 118; `mypy src/` 97 in 19 files; touched files clean (`ruff check`, `ruff format --check`; `mypy --strict` on the profile and judge). Sibling `git status` unchanged (the harness checks codegen before and after each run).

**Issues and corrections (M5 direction, not R2):**
- **`calc_result_expression` is not an admitted stub context.** The design (F4, code-read) and the spec's minimum admitted set expected `max(a, b)` and a conditional as a calc def's bare result expression to become a handwritten stub. At `b5663c07` every calc def whose result is a bare expression is refused, with or without a declared `return` feature, because the extractor finds no output (the two `candidate-calc-result-expression` probes). That refusal is not ES-005's or ES-006's, so it cannot be recorded as their refusal either (the code differs). The context stays `unconfirmed` for all three site rules. The admitted context the probes did find is a calc **usage**'s bare result expression (`other_expression_site`), which the generator never examines and silently drops. Spec criterion "Every refused shape has an admitted-context probe" is met through that context; the spec's two named calc-def examples are the corrected ones, recorded here for the owner.
- **A silent drop worth R3's attention:** a calc usage's bare result expression produces nothing in the generated output and no diagnostic.
- **The ES-010 refusal side:** on its reproduction model the evaluator reports the String `omitted` while the generator refuses the model. The refusal side is a candidate (D11), so this is the known gap, not a rule error; it is in the String record's `semantic_limits` and goes to R3.
- **A refused conditional or invocation leaves `indexed-reference` unverified on the same site** (the shared reference walk failed). Honest, and every model with such a site is `INCOMPLETE`.
- ES-001 calc-usage owner: the generator locates the refusal at the owner's line, so those probes' construct ranges include the owner.

**Deviations from Plan:**
- Probe IDs for candidates use rule names `candidate-es-002`, `candidate-es-008`, `candidate-es-009`, `candidate-es-010-refusal`, `candidate-calc-result-expression`, since the `rule__shape__context` scheme needs a rule slot and these are not rules.
- Controls rather than admissions for the prototype neighbors (decided in Phase 5).

### Phase 7 Completion
**Completed:** 2026-10-18. Probes authored at `691f96c8` and `ecc18940`; the whole probe set re-run at `ecc18940` (80 of 80 certify), which is `verified_against.agentic_rev`.

**Outcome:** every refused pair of `binding-source`, `part-multiplicity` and `constraint-predicate` has a certified probe and an admitted-context probe, every B5 variation agrees with its context label, the spec's admitted-context minimum set is certified, and the root and determinism tests pass end to end. **No R2:** no refused probe, base or variation, was admitted (`evidence/r2-open.md`).

| Rule / shape | Refused (probes, with B5 variations) | Admitted / excluded | Unconfirmed |
|---|---|---|---|
| `binding-source/expression_source` | `owner_instantiated` (8: base, `rate * fuel_code`, constraint input, part-usage owner, subtype, nested, owner under `[2]`, selected in one scope and overridden in another); `owner_package` | `owner_uninstantiated`; `writer_overridden` (2) | `owner_other` |
| `binding-source/self_reference_source` | `owner_instantiated` (4: base, part-usage owner, subtype, under `[2]`); `owner_package` | `owner_uninstantiated` | `writer_overridden`, `owner_other` |
| `part-multiplicity/range` | `expanded_part_usage` (5: base, depth two, under `[2]`, subtype, root) | `unexpanded_part_usage` (template; non-composite `ref part`) | — |
| `part-multiplicity/unresolved_bound` | `expanded_part_usage` (3: `[*]`, an unvalued referenced bound, under `[2]`) | `unexpanded_part_usage` | — |
| `part-multiplicity/ordered` | `expanded_part_usage` (2: base, under `[2]`) | `unexpanded_part_usage` | — |
| `part-multiplicity/nonunique`, `negative_bound` | — | — | everything: not authorable (below) |
| `constraint-predicate/blocked_predicate` | `owner_instantiated` (4: base, part-usage owner, subtype, under `[2]`); `owner_package` | `owner_uninstantiated` | `owner_other` |
| `constraint-predicate/non_numerical_predicate` | — | `owner_instantiated` → **excluded** | other contexts |

Controls certified (the prototype's admitted neighbors and the observations): ordered nonunique input bound to a scalar, exact `[1]` ordered input, plain reference actuals; exact redefinition (own model and the prototype's); an ordered ranged **attribute** usage; numeric `and`; and **G1**, a part redefinition that drops `[2]` and generates one unindexed occurrence (`fx__rack__servers__t__r`), which the port mirrors (D14 a). G2 (a usage-level override of a definition-owned referenced bound) was not probed in Item 1; it stays a matrix question for Phase 8.

**Final record state (Things This Plan Cannot Settle, item 2):**
- `ContextId`: 17 members (Appendix A's 19, less `ATTRIBUTE_USAGE` and `EVERYWHERE`, Phase 5). No member was added by a probe.
- Probes: 80 (62 `record`, all cited; 12 `control`; 6 `reproduction`), all at `ecc18940`.
- Record pairs: 24 refused, 11 admitted, 1 excluded, 1 omitted. One SA-1 statement (`calc-owned-assertion/asserted_constraint`). Shapes with no admission: `conditional_resolved_branches`, `nonunique`, `negative_bound`.
- Evidence status: `probe_observed` for six rules; `partial` for `conditional-expression` and `part-multiplicity` (the three shapes above).

**V probes against the port (manual check):** every V fixture's generator outcome matched the context the port computed before the run (a pre-run evaluator check placed all 46 Phase 7 record and control probes as expected), so none surprised and `occurrence_parity.py capture` was not needed. The overridden-writer probes are the sharpest check of the port's writer selection: overridden in every scope is admitted, selected in one scope is refused, exactly as computed.

**Actual Changes:**
- 46 probe directories: 38 record (including 2 reach variations added after the first run) and 8 controls (including G1). Prototype fixtures re-run (D9): `unmapped_expression_calc_arg`, the three `es003_*` neighbors, `es004_refused_range_parts`, `es004_refused_unbounded_parts`, `es004_admitted_uninstantiated_template`, `es004_admitted_exact_redefinition`, `es007_refused_boolean_mixed`, `es007_admitted_numeric_and`. With Phases 1 and 6, every prototype fixture has now been re-run through the harness.
- `subset_profile_rules.toml`: the admissions above, `verified_against.agentic_rev = ecc18940`, and the part-multiplicity limits (nonunique and negative bounds not authorable; G1) in its `semantic_limits`. Version digest re-pinned.
- Judge: the `excluded` check now requires that nothing of the element is executed (no catalog name equals it or extends it with `__`). A whole-identifier mention check would pass vacuously, because generated constraint names carry a hash suffix. New failed check `excluded_element_executed`, with a test.
- `tests/test_sysml/test_subset_profile_rules_instantiation.py` (55): per-probe reproduction; controls; the B5 reach variations Appendix C names, checked by name; the NON_NUMERICAL `excluded` case with its profile reason; the overridden writer's scope count; default, widened and narrowed roots end to end; all six orders of a three-document model give identical results; evaluating twice is identical.
- Fixtures `tests/fixtures/subset_profile/cases/widened_roots.sysml` and `cases/multi_doc/{lib,plant,templates}.sysml`.
- `tests/test_subset_probe_evidence.py`: `AWAITING_ADMITTED_PARTNER` is empty, so every certified record probe is cited.

**Validation:** `pytest tests/` 3420 pass, the same 3 environment failures; `ruff check src/ tests/` 118; `mypy src/` 97 in 19 files; touched files clean (`ruff check`, `ruff format --check`; `mypy --strict` on the five fact and profile modules and the judge). Teeth: flipping one recorded outcome fails the evidence test. `git status` of `~/src/sysml-codegen` and `~/src/dc3` empty, HEADs `b5663c07` and `60b44d53`.

**Issues:**
- **`nonunique` and negative part multiplicities cannot be probed.** SysIDE 0.8.4 rejects both before the generator runs ("Subsetting feature cannot be nonunique if subsetted feature is unique"; "Multiplicity range [-1] must be non-negative", also for a referenced bound valued `-1`). The shapes stay `unconfirmed`. The evaluator can only meet them in a model SysIDE already rejects.
- **A unit-annotated literal binding control was not authored.** The generator rejects an `ISQ` length-typed calc input outright (`SI_TYPE_INVALID`), and SysIDE rejects `[SI::one]` on a `Real` (Phase 4). The literal binding class is still placed by the other controls; recorded here because Appendix C listed it.

**Deviations from Plan:**
- Two reach variations (`ordered` and `[*]` under `[2]`) beyond Appendix C, added because the B5 test asks every instantiation-dependent refused pair for a reach variation.
- The plan's widened-roots stencil used a probe model; the test uses a dedicated case (`widened_roots.sysml`) whose template usage `wr::Templates::site` is owned by a part def, since a package-owned part usage is already a generator root.
- The B5 variation probes are `record` probes with a variant suffix and are cited as additional evidence for their pair, rather than a separate probe kind.

### Phase 8 Completion
**Completed:** 2026-10-18.

**Outcome:** the matrix places every named case with exactly one class and an owner, and joins the packaged records both ways. `tests/test_subset_matrix.py` passes (67 tests) in the repo and in an archive copy of `src/` and `tests/` with no `.project/`. Rendered to `evidence/matrix.md`.

| Class | Rows |
|---|---|
| `shared_rule` | ES-001, ES-003, ES-004, ES-005, ES-006, ES-007, ES-010, ES-012, SELF-BINDING, INDEXED-REFERENCE (10, all eight rules) |
| `tracked_gap` | ES-002, ES-008, ES-009, ES-010-REFUSAL, ES-011, CALC-DEF-BARE-RESULT, CALC-USAGE-BARE-RESULT-DROP, G1, G2, DEEP-QUALIFIED-WIRING, L6-LIBRARY-ALIAS-SOURCE, and six PUSH-DOWN rows (17) |
| `advisory_omission_policy` | four PUSH-DOWN rows: UNSUPPORTED-SHAPE-MESSAGE, REDEF-PRECEDENCE, AMBIG-INHERITED-ATTR, WRAPPER-SHAPE |
| `codegen_check`, `internal_invariant` | none at matrix level; these classes appear in the site account (Phase 9) |

dc3 mapping, asserted per item: B1, U1 → ES-001; B2 → ES-003 (not ES-004); B3 → ES-004; B4, B5 → ES-005; B6 → ES-006; U4 → ES-005 and ES-006; B7, U3 → ES-010; B8 → ES-007 with its 4 NON_NUMERICAL (`excluded`) and 4 MALFORMED_NUMERICAL (`refused`) kept apart; B9, U7 → ES-011 (`unconfirmed`); U2 → ES-008; U5 → ES-002; U6 → ES-009. U8 is a pointer to Item 4, not a row. The binding-source classifier's five kinds are placed: literal and single reference admitted, self-binding → SELF-BINDING, indexed → INDEXED-REFERENCE, other expression → ES-003.

**Actual Changes:**
- `tests/helpers/subset_matrix.py` (new, pure): `load_matrix`, `Matrix` (a mapping with `by_dc3` / `by_upstream`), `MatrixRow`, `OutcomeSplit`, `ClassifierPlacement`, `Pointer`, closed `RowClass` / `RowOutcome` / `RowEvidence`. Rejects at load: unknown keys or members, `rule`/`shapes` on a non-shared row, a rule status on a non-shared row, an evidence string that is not a recognized reference, dc3/upstream ids outside B1-B9/U1-U7, a classifier that does not place exactly the five kinds.
- `tests/fixtures/subset_profile/inventory/matrix.toml` (new): 31 rows, the classifier placement, the U8 pointer. `sites` are empty until Phase 9.
- `tests/test_subset_matrix.py` (new): the stencil; every B and U item mapped exactly; B8 split; classifier placement against the records' expected codes; shared rows ↔ records both directions (row ids, shapes, evidence status); a shared row's contexts equal the record contexts with its outcome; every probe a row cites exists, certifies, and has the kind its status names; coverage limitation present unless implemented; SELF-BINDING `l2_relation`; eight loader rejections.
- `scripts/subset_profile/render_matrix.py` (new): renders `evidence/matrix.md`.

**Validation:** `pytest tests/` 3487 pass, the same 3 environment failures; `ruff check src/ tests/` 118 (baseline); `mypy src/` 97 in 19 files (baseline). New files pass `ruff check` and `ruff format --check`; the helper and the script pass `mypy --strict`. Teeth: three matrix mutations (narrowing ES-003's contexts, dropping the L2 code from SELF-BINDING's relation, citing a control probe on a reproduction row) each fail a test.

**Deviations from Plan:**
- **Rows beyond the fixed list:** ES-010-REFUSAL (the refusal side, kept apart from the omission rule), CALC-DEF-BARE-RESULT and CALC-USAGE-BARE-RESULT-DROP (Phase 6's findings). The orchestrator ruling sends them to R3; a row gives each an owner and a place to hang sites.
- **The matrix loader lives in `tests/helpers/`,** as the judge and the oracle schema do (P-2, P-3), so the renderer and the test read one copy.
- **`contexts` are record `ContextId`s for shared rows and words for the rest.** Non-rule rows have no closed context vocabulary to draw from.
- **`evidence_status` widens the records' three values** with `reproduction_probe`, `control_probe`, `observed_in_record_probes`, `corpus_record`, `code_read`, `reported_not_reproduced`, so a non-rule row says what its evidence actually is.
- **PUSH-DOWN-EXPR-PROFILE-CHAIN-SEGMENTS:** the backlog row names a shared helper `extract_feature_chain_segments`; no function of that name exists in agentic-mbse `src/` at this revision. Recorded in the row's coverage limitation.
- **DEEP-QUALIFIED-WIRING** cites codegen's corpus refusal record `deep_cross_scope_probe` (`SI_OCCURRENCE_MISSING`), not an Item 1 probe.

### Phase 9 Completion

### Phase 10 Completion
**Final implementation revision:**

### Phase 11 Completion

---

**Status:** Draft → In Progress → Complete

## Orchestrator rulings after Phase 7 (2026-10-18)

- [AGENT] Ratified: for `SI_CONSTRAINT_BLOCKED` only, the judge reads the profile's own `[file:line]` suffix as the error location, still requiring it to fall inside the construct. Reason: the location check is unchanged in force; only its source differs for a code whose generator line carries no `root-0/` location. ES-007 is mapped to `executable_profile` by design, so this is consistent.
- [AGENT] Calc-def bare-result context stays `unconfirmed` (generator refuses all such calc defs for having no output); the calc-usage bare-result silent drop and the ES-010 refusal side go to the R3 proposal table as candidates/gaps.
