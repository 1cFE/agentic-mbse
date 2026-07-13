<!-- REFERENCE COPY. Canonical: sysml-codegen .project/backlog/epic_constraint_execution.md @ 662411a. Do not edit here. -->
# Epic: Constraint Execution and Design-Space Studies

**Epic ID**: CONSTRAINT-EXEC
**Status**: Ready
**Priority**: P1
**Created**: 2026-07-12
**Estimated Effort**: ~20 days sequential across 3 repos (15 items; three parallel tracks reduce wall-clock substantially — critical path ~13 days)

---

## Executive Summary

Modeled physical limits (`assert constraint`) currently die at a drop-report warning; every design study re-implements the judgment by hand and drifts from the model. This epic makes modeled assertions execute inside the generated forward model — as ordinary graph modules feeding an exact-schema report aggregator — and adds a crash-safe study layer that runs one point or thousands against the same sealed evidence. All six de-risking spikes (S1–S6) passed with verified re-runs; this epic is the production build-out of the proven architecture.

**Critical Success Factor**: The IFE sweep's hand-coded viability rule is replaced by the generated assertion with every existing grid classification matching — and no modeled limit anywhere ends in silence.

---

## Why This Epic?

**Current State**:
- Constraints are extracted, classified, and reported as dropped (`constraint_report.py`); their predicates, bindings, and truth values never reach generated code.
- The one demonstrated design-space sweep re-implements the viability rule by hand in its harness; nothing stops drift.
- TEAx runs one pipeline at a time from files; an infeasible design and broken code share one vocabulary (exceptions).
- Snapshots serialize `dropped_constraints` diagnostics only; a snapshot-first workflow loses constraint semantics permanently.
- Six spikes (S1–S6, 2026-07-11/12) proved every architectural bet: fact shapes are statically recoverable (S1); one neutral `ExpressionIR` serves predicates and calcs byte-identically with necessary Kleene semantics (S2); a part-structure-owned instance index finds all concrete owners with deterministic IDs (S3); the full cross-repo vertical slice generates and executes under real TEAx with byte-identical live/snapshot artifacts (S4); typed in-memory entry + scalar continuity are closed with ~4× prepare-once speedup (S5); the SQLite study store survives hard crashes at both critical seams (S6). Every spike result and review carry-forward is recorded inline in the concept.

**Future State**:
- Every supported modeled assertion executes per concrete design state, live and from snapshot; verdicts (`satisfied | violated | indeterminate`) are data beside ordinary outputs, never exceptions.
- The graph owns a constraint catalog and semantic contract; packaging seals them into an executable fingerprint; study tooling consumes the sealed contract only.
- A study layer (prepared lists and grids first) evaluates candidates through a typed in-memory evaluator with atomic, crash-resumable case records.
- The drop manifest, its blanket warnings, and the "constraints are not executable" authoring guidance retire; unsupported constructs block generation with named diagnostics; non-assert kinds are cataloged unassessed.
- Calc expression compilation migrates onto the shared `ExpressionIR` (staged, under byte-identity gates), retiring `ExpressionAST`.

---

## Success Criteria

- [ ] **Acceptance**: the IFE sweep's hand-coded viability rule is replaced by the generated assertion and every existing grid classification matches (concept Validation Strategy).
- [ ] Every assertion in the executable profile lowers to a module or blocks generation naming identity, construct, and source location; non-assert kinds appear in the catalog as unassessed; the drop manifest and both blanket warnings retire with a 1:1 migration mapping.
- [ ] Live and snapshot generation produce byte-identical artifacts and identical constraint IDs/catalog ordering; a pre-constraint-facts snapshot or a current one missing the section is rejected with a re-capture instruction — never loaded as an empty catalog.
- [ ] A violated assertion completes with ordinary outputs intact and evidence (actual value, margin where structure fixes its sign, observed operands); violation, indeterminacy (Kleene, non-finite), and execution failure are three distinct queryable outcomes at module, report, and study level.
- [ ] The report aggregator has a generated exact input schema (missing result = schema failure), exists even for zero assertions, and is a *guaranteed* exit ancestor (explicit membership or generation-time assertion, not incidental).
- [ ] `PackageContract` seals generated artifacts (content hashes, verified on load); `ModelContract` derives solely from graph fields; the study layer runs list/grid studies with atomic case commit, three-layer identity, proposal records for invalid candidates, and fingerprint-bound resume — the S6 invariants as kept tests.
- [ ] Byte-identity gates stay green everywhere the epic touches existing behavior: current fixture corpus regenerates byte-identically (timestamps excepted) until the deliberate calc-seam cutover, which lands under its own byte-identity gate.
- [ ] All existing suites pass in all three repos; new behavior is covered by the concept's validation strategy (expansion, strict resolution, ID determinism, live/snapshot parity, report precedence, crash-resume).
- [ ] Documentation: authoring guidance teaches executable constraints and the profile's block list; architecture docs cover the new pipeline phase, catalog, contracts, and study layer.

---

## Source Documents

- `.project/concepts/constraint-execution-and-design-space-studies-claude.md` — **concept-design** (primary; includes Appendix A verification sweeps, Appendix B spike results S1–S6 with [AGENT] review carry-forwards — the carry-forwards are load-bearing spec inputs)
- `~/1cfe/agentic-mbse/.project/active/spike-constraint-fact-shapes/findings.md` — **spike (S1)**: fact shapes, equality/unit gate, SysIDE 0.8.4 access quirks
- `.project/active/spike-expression-tree-parity/findings.md` — **spike (S2)**: ExpressionIR parity, Kleene necessity, extract-and-migrate decision, operator matrix v1, oracle envelope
- `.project/active/spike-concrete-expansion-instance-index/findings.md` — **spike (S3)**: subtype-closure instance index, ID determinism, snapshot strict boundary
- `.project/active/spike-vertical-slice-constraint-execution/findings.md` — **spike (S4)**: vertical slice; the four calc-shaped generation seams; module identity; exit-ancestry; sealed package
- `~/1cfe/teax/.project/active/spike-teax-typed-entry-scalar-continuity/findings.md` — **spike (S5)**: typed entry source, scalar continuity, prepare-once economics
- `~/1cfe/teax/.project/active/spike-crash-safe-study-lifecycle/findings.md` — **spike (S6)**: crash-safe store, staging protocol, three-layer identity

---

## Epic Strategy

**Value delivery path.** Item 0 buys end-to-end confidence for pennies before any schema freezes. The agentic-mbse track (1–3) freezes the neutral semantics every other repo consumes. The codegen track (4–9) builds the lowering-to-sealed-package path that S4 proved with test-only emitters. The teax track (10–12) productionizes the S5/S6 machinery. Item 13 (calc cutover) is deliberately last-of-the-codegen-track per S2's "predicates first, staged" decision. Item 14 closes the loop where the epic started: the IFE sweep's hand-coded rule dies.

**Decomposition rationale.** Items follow task-type cohesion and the repo seams the spikes proved: refactor-of-existing (6, 13 — byte-identity-gated) is separated from new-emission code (7); snapshot rejection semantics (8) are their own invariant family; evaluator (10), store/runner (11), and user surface (12) mirror the S5/S6 seam. The spike `[AGENT]` review carry-forwards in the concept's Appendix B are distributed to the items that must discharge them — each item's Required Reading names its subset.

**De-risking.** No item rests on an unverified bet: every architectural assumption was spike-tested (S1–S6), and Item 0 tests the one remaining untouched seam (real evaluator × real package × study lifecycle) before Items 9–11 commit schemas. If Item 0 surfaces an evaluator-interface mismatch, it reshapes Item 10's spec, not the architecture.

---

## Backlog Items

### Item 0: End-to-End Integration Spike — S6 Lifecycle × S5 Evaluator × S4 Sealed Package

**Type**: Spike (throwaway code, kept findings)
**Effort**: 0.5 days (no spec/design/plan cycle — `/_my_spike` protocol)
**Dependencies**: None (teax `main` ≥ `7560d65` verified present)

**Objective**: Run S6's study lifecycle against S4's sealed generated package through an S5-shaped prepared-pipeline evaluator, connecting every spike artifact end-to-end before production schemas freeze.

**Scope**:
1. Regenerate S4's sealed package (probe A) and wire an S5-style prepared-pipeline evaluator over it (typed in-memory entry, fresh context per case).
2. Drive S6's runner/store machinery against it: a prepared candidate list covering satisfied, violated, and indeterminate (non-finite input via typed mapping) points, an invalid proposal, and one crash-and-resume cycle.
3. Benchmark prepare-once vs rebuild on the real package (the S5 carry-forward's cross-model measurement).

**Out of Scope**:
- Any production code in any repo; any new lifecycle capability (S6's machinery is reused as-is).
- Adaptive strategies (S7 territory).

**Success Criteria**:
- [ ] All three verdict classes land as `completed` cases with correct evidence; the invalid proposal stays a `ProposalRecord`; resume reproduces the uninterrupted run.
- [ ] Any evaluator-interface mismatch between S6's fake shape and the real prepared pipeline is named precisely (it feeds Item 10's spec) — or its absence is stated.
- [ ] Prepare-once vs rebuild measured on the real package; findings recorded with reproduction commands.

**Required Reading**: concept Appendix B S4–S6 results + carry-forwards; S4/S5/S6 findings (Reproduction sections).

**Location**: `~/1cfe/teax/.project/active/constraint-study-integration-spike/`

**Deliverables**:
- `findings.md` (summary-on-top, reproduction, verdict feeding Items 9–11)

---

### Item 1: Neutral Constraint Facts — Production Schemas and Extraction

**Type**: Implementation (agentic-mbse)
**Effort**: 2 days (spec 2h, design 3h, plan 1h, execute 10h)
**Dependencies**: None

**Objective**: Land `ConstraintDefinitionFact`, `ConstraintUsageFact`, and `ConstraintSource` as production, serializable schemas with live extraction, adopting S1's frozen fact shapes.

**Scope**:
1. **Schemas**: reusable predicate + formals with defaults + source identity (definition fact); exactly one `ConstraintSource` per usage fact — inline / definition-typed / named-usage-reference / satisfy — plus the two non-asserted catalog shapes S1 surfaced (requirement-owned require/assume; plain non-asserted usages as reference targets). Membership kind read from the owning membership; polarity; owner/scope; actuals with formal targets; omitted defaulted formals; inheritance/retyping facts; source location (anonymous-assertion identity).
2. **Extraction**: base `ConstraintUsage` subtype sweep (an `AssertConstraintUsage`-rooted sweep misses satisfy); definition formals by owner-filtered `AttributeUsage` enumeration (`ConstraintDefinition.parameters` omits them in 0.8.4); **principled discriminators** — inline vs definition-typed by whether the usage owns a `result_expression`, never by namespace prefix; quantity dimensions resolved structurally, never by `Unit`-suffix stripping.
3. **Serialization + tests**: versioned JSON section shape (consumed by Item 8); golden tests re-anchored from S1's fixtures; S1's test-only capture module retired or clearly demoted to fixture tooling.

**Out of Scope**:
- Eligibility decisions (Item 3 owns the profile); expression tree internals (Item 2); any sysml-codegen consumption.

**Success Criteria**:
- [ ] All six source-form classes from S1's golden matrix extract with production code; membership kind, polarity, ownership, actuals, defaults, and inheritance facts match S1's golden values.
- [ ] Neither fixture-coupled heuristic (namespace prefix, unit-suffix strip) appears in production code — S1 carry-forward (1) discharged.
- [ ] Facts JSON round-trips byte-stably; schema carries a version.
- [ ] agentic-mbse suite green; Ruff clean.

**Required Reading**: concept "Neutral Constraint Facts" + S1 result and carry-forwards (Appendix B); S1 findings §2, §5.

**Location**: `~/1cfe/agentic-mbse/.project/active/constraint-facts/`

**Deliverables**:
- `spec.md`, `design.md`, `plan.md`, close-out report
- Production fact schemas + extractor in `agentic_mbse.sysml`; golden tests

---

### Item 2: ExpressionIR — Production Tree, Extraction, Serialization

**Type**: Implementation (agentic-mbse)
**Effort**: 1.5 days (spec 2h, design 2h, plan 1h, execute 7h)
**Dependencies**: Item 1 (feature-ref and literal field shapes adopt the frozen facts)

**Objective**: Promote S2's probe-grade `ExpressionIR` to a production agentic-mbse-owned tree: the concept's node algebra, live extraction, and byte-stable JSON.

**Scope**:
1. **Node algebra**: literal, feature reference (source name, qualified target, chain segments — never pre-classified), unary/binary/n-ary operator, invocation, unit annotation, explicit unsupported node with structural diagnostic.
2. **Extraction** from live SysIDE expression nodes (S2's `extract_ir` hardened; operator normalization; FeatureChainExpression-before-OperatorExpression dispatch).
3. **Serialization**: canonical byte-stable JSON round-trip, within and across loads; versioned.

**Out of Scope**:
- Compiling IR to Python (Item 7 owns the Kleene predicate compiler; Item 13 owns the calc compat rendering); profile eligibility (Item 3); `ExpressionAST` retirement (Item 13).

**Success Criteria**:
- [ ] All five S2 predicate shapes and the S2 stress calc expressions extract to trees that JSON-round-trip byte-identically across independent loads.
- [ ] The unsupported node carries a structural diagnostic (silence is never an outcome at the tree level).
- [ ] Field shapes visibly adopt Item 1's fact vocabulary (S2 carry-forward: probe pydantic fields were stand-ins).
- [ ] agentic-mbse suite green.

**Required Reading**: concept `ExpressionIR` paragraph + S2 result and carry-forwards; S2 findings ("Facts the design can now rely on").

**Location**: `~/1cfe/agentic-mbse/.project/active/expression-ir/`

**Deliverables**:
- `spec.md`, `design.md`, `plan.md`, close-out report
- `ExpressionIR` module + extraction + serialization tests

---

### Item 3: Executable Profile — Eligibility Gates and Named Diagnostics

**Type**: Implementation (agentic-mbse + sysml-codegen preflight hook)
**Effort**: 1.5 days (spec 2h, design 2h, plan 1h, execute 7h)
**Dependencies**: Items 1, 2

**Objective**: Publish the decision procedure for whether an assertion may run — per-construct eligibility with named diagnostics — replacing the L4 placeholder and the L6 blanket warning, enforced at design review and codegen preflight.

**Scope**:
1. **Admit** (operator matrix v1): static scalar asserts, inline and definition-typed; comparisons; `and`/`or`/`not`; arithmetic in operand position; negated polarity; owner-scope references, explicit actuals, modeled defaults.
2. **Equality gate** (S1's evidence): Boolean/string/integer/same-enumeration in; real-valued equality, incompatible enums/dimensions, unresolved operands blocked with named diagnostics.
3. **Unit policy**: dimensionless or identical *structurally proven exact* units; dimension-only typing (e.g. `LengthValue`) blocks; **applies to inequalities and arithmetic, not just equality** — add the golden inequality-unit cases S1 left unpinned (carry-forward (2)).
4. **Block with named diagnostics**: assert-by-reference, `xor`/`implies`, invocation, feature chains, unit conversion; satisfy cataloged unassessed.
5. **Enforcement seams**: L4/L6 validation replacement in agentic-mbse; preflight hook in sysml-codegen; **the profile gate strictly precedes any compilation** (S2 carry-forward (2): the compiler strip-renders units and is not a safety net).

**Out of Scope**:
- The compiler itself (Item 7); catalog persistence (Items 5, 7); resolving where an exact-unit contract could come from (open spec question — this item blocks, a future item may relax).

**Success Criteria**:
- [ ] Every S1 golden equality case gets the matrix decision; new inequality-unit golden cases pin `1 [m] <= 100 [cm]` → block and `integer <= real` → admit.
- [ ] L4 no longer reports a 0% placeholder; L6's blanket per-constraint warning is gone; every diagnostic names construct + source location.
- [ ] A model using only supported constructs passes silently; each blocked construct fires exactly its named diagnostic (loud-on-gap, silent-on-clean).
- [ ] Both repos' suites green.

**Required Reading**: concept "executable profile" paragraph + S1/S2 results and carry-forwards; S2 operator matrix table.

**Location**: `~/1cfe/agentic-mbse/.project/active/executable-profile/`

**Deliverables**:
- `spec.md`, `design.md`, `plan.md`, close-out report
- Profile module + diagnostics; L4/L6 replacement; codegen preflight hook + tests

---

### Item 4: Part-Instance Index — Subtype Closure and Cardinality Expansion

**Type**: Implementation (sysml-codegen)
**Effort**: 1 day (spec 1h, design 2h, plan 1h, execute 5h)
**Dependencies**: None (part structure only; consumes no fact schemas)

**Objective**: Build the production part-structure-owned instance index: subtype closure over a source owner, retyped-path deduplication, and concrete-cardinality expansion — independent of calc templates.

**Scope**:
1. One index derived from `PartUsage` structure and PartDefinition heritage: project a source owner over its subtype closure; deduplicate redefined/retyped paths; find constraint-only definitions' instances.
2. Fixed-multiplicity expansion **keyed by owning definition + feature** (S3 carry-forward (1): the extracted fact carries `owning_part_def_qn`; leaf-name keying collides).
3. Block parameterized, variable, ordered, and unbounded multiplicities with a named diagnostic (finite concrete cardinality required at lowering).

**Out of Scope**:
- Constraint expansion itself (Item 5 consumes the index); virtual-calc instance discovery (unchanged for calcs).

**Success Criteria**:
- [ ] S3's nine-instance fixture oracle: 9/9 found (including the plain subtype the current lookup misses), zero unexpected, with zero calculations in the model.
- [ ] Two same-named multiplicity members under different owners with different counts expand correctly (the collision case the probe asserted away).
- [ ] Non-finite cardinality blocks with a named diagnostic; index results deterministic across repeated loads.
- [ ] Existing corpus regenerates byte-identically (index addition must not disturb calc-driven discovery).

**Required Reading**: concept "Concrete Lowering" instance-index sentences + S3 result and carry-forwards; S3 findings §1–2.

**Location**: `.project/active/part-instance-index/`

**Deliverables**:
- `spec.md`, `design.md`, `plan.md`, close-out report
- Production index module + tests (S3 fixture promoted)

---

### Item 5: Concrete Lowering — New Phase, Strict Resolution, Execution IDs

**Type**: Implementation (sysml-codegen)
**Effort**: 2 days (spec 3h, design 3h, plan 1h, execute 9h)
**Dependencies**: Items 1, 2, 4

**Objective**: Land the new lowering pipeline phase: expand assertions per concrete instance, strictly resolve actuals, join constraint roots before pruning, and mint deterministic execution IDs.

**Scope**:
1. **Phase placement**: after aliases, output registry, and supplied-value materialization are final; before dependency backtracking (actual resolution needs the finished registry).
2. **`ConcreteConstraint`**: source facts, resolved actuals, expected Boolean value, deterministic `constraint_id`, optional simple-inequality response metadata. Part-def-owned and inherited assertions expand once per concrete part instance (via Item 4); calc-def-owned once per concrete calc usage; an expected instance that cannot form is a validation error.
3. **Strict resolution** through one shared resolver seam with an explicit strict mode: chain actuals via `OutputRegistry.scoped_lookup` in owner-instance scope; reference actuals against design attributes, minting `DESIGN_ATTRIBUTE` entry points in their derived groups; defaulted formals become overridable contract parameters retaining the modeled default; **unresolved = generation error, never synthesis**. Heed the EP-key collapse risk: the existing backtracker fallback is not a drop-in.
4. **Roots before pruning**: resolved constraint input channels join backtracking roots via the `_find_usage_for_channel` seam, so an assertion-only consumer keeps its producer in targeted graphs.
5. **Identity**: `constraint_id` = source-local identity + concrete owner instance + membership kind + polarity, scoped to one fingerprint; collision = generation error; deterministic catalog ordering; optional author-controlled `tracking_key`. Fixed-multiplicity siblings each get their own channels (S3 carry-forward (3)) — three occurrences are three wired modules, not copies.

**Out of Scope**:
- Module/aggregator emission (Item 7); snapshot round-trip (Item 8); the profile decisions themselves (Item 3 has already gated what reaches lowering).

**Success Criteria**:
- [ ] S4's vertical-slice behavior reproduced by production code: control run prunes `cost_calc`, lowered run retains it via the constraint root only.
- [ ] V11 coverage and channel-reference validation pass on extended graphs; no fallback path executes for constraint actuals (probe: unresolvable actual → generation error naming the actual).
- [ ] IDs and catalog ordering byte-identical across repeated live loads; multiplicity siblings independently wired.
- [ ] Existing corpus (no constraints in executable profile) regenerates byte-identically.

**Required Reading**: concept "Concrete Lowering" + Required Invariants (Semantics and Identity; Graph and Evaluation) + S3/S4 results and carry-forwards; memory: F4 cutover fallback divergence (EP-key collapse).

**Location**: `.project/active/constraint-lowering/`

**Deliverables**:
- `spec.md`, `design.md`, `plan.md`, close-out report
- Lowering phase + shared strict resolver seam + ID minting + tests

---

### Item 6: `module_kind` and the Generation-Seam Refactor

**Type**: Code/Integration (sysml-codegen)
**Effort**: 1.5 days (spec 2h, design 2h, plan 1h, execute 7h)
**Dependencies**: None (pure refactor of existing generation; can start immediately)

**Objective**: Replace the accreted Boolean flags with a real `PipelineModule.module_kind` and make the four calc-shaped generation seams kind-dispatched, byte-identically for existing kinds.

**Scope**:
1. `module_kind` enum (calculation, formula, aggregation, constraint, report_aggregator) replacing Boolean flags on `PipelineModule`; structured output schema identity becomes graph data (retiring the float-specialized wrapper assumption for structured modules).
2. The four seams S4 named: `_get_python_path`/`_check_duplicate_output_paths` (assume `calc_def_qualified_name`), `generate_registry` class naming/dedup, `_generate_modules` wrapper rendering, `_generate_stencils`.
3. Migration of every flag consumer; snapshot serialization of the new field (coordinated with Item 8's version bump if sequenced together).

**Out of Scope**:
- Emitting constraint-kind modules (Item 7); any behavior change for existing kinds (byte-identity gate is the whole point).

**Success Criteria**:
- [ ] Entire existing fixture corpus regenerates byte-identically (timestamps excepted) with flags gone.
- [ ] The four seams dispatch on `module_kind`; a constraint-kind module reaching any of them no longer mis-renders as a calc (guarded by unit tests, exercised for real in Item 7).
- [ ] mypy/Ruff clean; suite green.

**Required Reading**: concept `PipelineModule` paragraph + S4 seam findings; memory: byte-identity captured_at churn (gate mechanics).

**Location**: `.project/active/module-kind-refactor/`

**Deliverables**:
- `spec.md`, `design.md`, `plan.md`, close-out report
- Refactored models + generation seams; byte-identity evidence

---

### Item 7: Constraint Module, Kleene Compiler, Aggregator, and Catalog Generation

**Type**: Implementation (sysml-codegen)
**Effort**: 2 days (spec 3h, design 3h, plan 1h, execute 9h)
**Dependencies**: Items 2, 3, 5, 6

**Objective**: Generate the constraint execution surface: per-assertion modules compiled from `ExpressionIR` under Kleene semantics, the exact-schema report aggregator with guaranteed exit-ancestry, and the embedded two-level catalog.

**Scope**:
1. **Kleene predicate compiler** (codegen-owned, from S2): def-level compile with formal-named arguments, usage-level wiring; non-finite operand → leaf unknown; Kleene propagation; status vs expected value (negated polarity); margin only where structure fixes its sign, polarity-respecting, **boundary margin is zero with no meaningful sign** (S2 carry-forward (3)).
2. **Constraint modules**: `ConstraintEvaluation` output (ID, actual value, status, margin, bounded observed operands) on one structured channel; module identity mechanism decided at design — class-per-concrete-assertion vs id-injection — **taken together with the aggregator-schema scale limit** (S4 carry-forward (4)); never raises on a verdict.
3. **Aggregator**: generated exact input schema (one required field per concrete assertion), exists for zero assertions, headline precedence (violation > indeterminate > all-satisfied > not-assessed); **guaranteed exit ancestor** — explicit exit membership or a generation-time ancestry assertion, not the incidental capture-everything exit (S4 carry-forward (1)).
4. **Catalog**: source records (per asserted/applied usage) + concrete entries (per expansion, keyed by `constraint_id`); unused definitions are inventory, never unassessed coverage.
5. **Runtime-facing tests** including the break-the-YAML case: a missing upstream evaluation surfaces as an execution failure through the executor, not a silent gap (S4 carry-forward (2)).

**Out of Scope**:
- Contracts/sealing (Item 9); drop-manifest retirement (Item 14); calc-side IR rendering (Item 13).

**Success Criteria**:
- [ ] S4's slice reproduced by production generation end-to-end under real simkit: both truth values complete, identical ordinary outputs, correct margins, report persisted; plus the cases S4 didn't exercise — zero-assertion aggregator, indeterminate (non-finite) point, negated and inline assertions at execution, multi-instance expansion, modeled-default formals.
- [ ] Exit-ancestry holds under a deliberately narrowed exit (test); break-the-YAML test passes.
- [ ] Live/snapshot generation byte-identical for a constraint-bearing fixture.
- [ ] Suite green; byte-identity for constraint-free corpus.

**Required Reading**: concept "Catalog, Evaluation, and Report" + Required Invariants + S2/S4 results and all their carry-forwards.

**Location**: `.project/active/constraint-generation/`

**Deliverables**:
- `spec.md`, `design.md`, `plan.md`, close-out report
- Compiler, emitters, templates, catalog assembly + tests

---

### Item 8: Snapshot v3 — Constraint Facts Load-Bearing

**Type**: Implementation (sysml-codegen)
**Effort**: 1 day (spec 1h, design 2h, plan 1h, execute 5h)
**Dependencies**: Items 1, 5

**Objective**: Make constraint facts a load-bearing, versioned snapshot section: bump the format, reject stale or sectionless snapshots loudly, and prove live/snapshot ID parity.

**Scope**:
1. Serialize Item 1's fact section (+ lowering-relevant fields) into the extraction snapshot; bump `snapshot_format_version`.
2. Rejection semantics: old version rejected by the existing hard-gate; **a current-version snapshot missing the constraint-facts section fails with a re-capture instruction** — never loads as an empty catalog (a model that asserts something never quietly generates assertion-free).
3. Live/snapshot parity: IDs and catalog ordering byte-identical through `generate --from-snapshot`; serialization fidelity is a named property (S4 carry-forward (3) — facts are carried, so carriage must be lossless).
4. Corpus re-capture under the byte-identity discipline (timestamp-only churn check + revert).

**Out of Scope**:
- The facts schema itself (Item 1); graph rebuild logic beyond wiring facts in.

**Success Criteria**:
- [ ] Both rejection cases fire with re-capture messages (kept tests, mirroring S3's strict boundary).
- [ ] A constraint-bearing fixture generates byte-identically live and from snapshot.
- [ ] Re-captured corpus shows only expected diffs; conformance suite green.

**Required Reading**: concept Required Invariants (snapshot bullets) + S3/S4 results and carry-forwards; memory: byte-identity captured_at churn.

**Location**: `.project/active/snapshot-v3/`

**Deliverables**:
- `spec.md`, `design.md`, `plan.md`, close-out report
- Serializer/loader changes, version gate, parity + rejection tests, re-captured corpus

---

### Item 9: Contracts and Sealing — `ModelContract` / `PackageContract`

**Type**: Implementation (sysml-codegen)
**Effort**: 1.5 days (spec 2h, design 2h, plan 1h, execute 7h)
**Dependencies**: Item 7 (seals the full artifact set); Item 8 (snapshot-generated packages seal identically)

**Objective**: Derive `ModelContract` solely from graph fields and seal generated packages with a verified-on-load `PackageContract`.

**Scope**:
1. **`ModelContract`**: stable parameter and output IDs, constraint catalog, required evaluation semantics, semantic fingerprint — graph fields only; provided capabilities live in `PackageContract`.
2. **`PackageContract` seal**: content hashes over generated + preserved artifacts (excluding the seal and runtime outputs), generator/runtime versions; **verified on package load**, not just at packaging; coverage set, stale-file detection, environment compatibility (the S4 test-only seal's named gaps).
3. Fingerprint namespaces IDs, never feeds them (no circularity); executable fingerprint stable across live loads and snapshot generation.

**Out of Scope**:
- Study-side contract consumption (Items 10–11); signing/crypto beyond content hashes.

**Success Criteria**:
- [ ] A tampered artifact and an unhashed extra file both fail load verification with named diagnostics.
- [ ] Fingerprint reproduces byte-exactly across independent live loads, snapshot generation, and sessions (S4 demonstrated this holds — keep it).
- [ ] Contract data derives from the graph alone (test: no filesystem/YAML introspection on the `ModelContract` path).

**Required Reading**: concept "Contracts and the Evaluator" + Architectural Bets (sealing) + S4 "Not exercised" contract sentence.

**Location**: `.project/active/package-contracts/`

**Deliverables**:
- `spec.md`, `design.md`, `plan.md`, close-out report
- Contract models, sealing pass, load verification + tests

---

### Item 10: Model Evaluator and Typed Entry — Production API

**Type**: Implementation (teax)
**Effort**: 1.5 days (spec 2h, design 2h, plan 1h, execute 7h)
**Dependencies**: Item 0 (seam findings); Item 9 informs contract consumption (can start from S5's proven shape and harden when 9 lands)

**Objective**: Productionize the S5 evaluator: typed in-memory entry source, prepared-pipeline backend, immutable `ModelEvidence`, and one normalized failure outcome.

**Scope**:
1. **`MappingEntrySource` API decision**: instantiated-models-only vs validate-raw-mappings — either way, no silent coercion, and the wrong-type diagnostic naming expected and got types is required behavior (S5 carry-forward (3)).
2. **Prepared pipeline backend**: validate + build topology once, fresh execution context per case; file-backed path retained for auditable runs; case-level parity between them as a kept test.
3. **`ModelEvidence`**: immutable, runtime-owned generic envelope — responses keyed by stable IDs, selected outputs, provenance, full report as opaque artifact; runtime types never import generated classes.
4. **Normalized failure outcome**: phase, module/channel when known, cause, retryability, partial-artifact status — violation stays evidence, breakage stays failure.

**Out of Scope**:
- Study semantics (Item 11); optimizers/adaptive strategies (deferred with S7).

**Success Criteria**:
- [ ] S5's invariants as kept teax tests: mapping/file parity, pre-execution rejection of missing/extra/wrong-type, context isolation, no files in no-persist mode.
- [ ] Evaluating S4-lineage packages (via Item 0's setup, then Item 9's sealed output) returns evidence with constraint verdicts projected onto generic response keys.
- [ ] A module exception, a schema failure, and an infeasible verdict land in three distinguishable places (failure outcome vs evidence).
- [ ] S5's kept continuity test is committed (it currently exists only as a working-tree change — S5 carry-forward (1)).

**Required Reading**: concept "Contracts and the Evaluator" + S5 result and carry-forwards; Item 0 findings.

**Location**: `~/1cfe/teax/.project/active/model-evaluator/`

**Deliverables**:
- `spec.md`, `design.md`, `plan.md`, close-out report
- Evaluator + entry source + evidence types + parity/failure tests

---

### Item 11: Study Store, Runner, and Strategies (Lists/Grids)

**Type**: Implementation (teax)
**Effort**: 2 days (spec 3h, design 3h, plan 1h, execute 9h)
**Dependencies**: Item 10

**Objective**: Productionize the S6 study lifecycle: definitions, prepared strategies, the fixed-order runner, and the crash-safe SQLite store with the S6 invariants as kept tests.

**Scope**:
1. **`StudyDefinition`**: variables/domains by parameter ID, observables by output ID, objectives, response roles, failure policy, strategy, budget, retention; cannot redefine a predicate.
2. **Strategies**: prepared lists and grids implementing propose/observe; three-layer identity with the **positional candidate-minting rule documented** — resume idempotency presupposes deterministic proposal order, guaranteed for these strategies (S6 carry-forward (2)); deliberate replicates distinct.
3. **`StudyStore`**: SQLite with `WAL` + `synchronous=FULL` **as contract, not implementation detail** (S6 carry-forward (3)); compatibility binding at creation (fingerprints, schema versions, strategy identity/config with stable canonicalization); `UNIQUE(study_id, candidate_id)`; append-only cases/attempts, separated mutable operational state; content-addressed artifact staging (tmp → fsync → atomic rename → dir fsync → single-transaction commit; final-path-complete invariant stated).
4. **Runner**: validate/canonicalize → evaluate → assess → stage durably → atomic commit → advance feedback; invalid proposals persist as `ProposalRecord`s; retry under new `attempt_id`.
5. **Lifecycle hygiene**: safe GC pass (collect only artifacts unreferenced by any committed case — replicates share artifacts); attempt-history schema decision (append-only-per-transition vs last-state-wins); durability boundary stated in docs (fsync-before-return, not power-loss).
6. **Kept crash tests**: S6's regimes (crash-before-commit, crash-mid-staging, resume-identical) as CI-runnable tests.

**Out of Scope**:
- Adaptive strategies and feedback crash semantics (S7 gates them); policy/query/CLI surface (Item 12).

**Success Criteria**:
- [ ] All five S6 pass criteria hold as kept tests against the real evaluator (Item 10), not only a fake.
- [ ] Incompatible-fingerprint open fails; changed anything mid-study starts a new lineage.
- [ ] GC collects exactly the orphaned staging garbage S6 characterized, never a shared replicate artifact.

**Required Reading**: concept "Study Layer" + Study Execution invariants + S6 result and carry-forwards; Item 0 findings.

**Location**: `~/1cfe/teax/.project/active/study-store-runner/`

**Deliverables**:
- `spec.md`, `design.md`, `plan.md`, close-out report
- Store schema, runner, strategies, staging, GC + crash-test suite

---

### Item 12: Study Policy, Query, and CLI Surface

**Type**: Implementation (teax)
**Effort**: 1 day (spec 1h, design 2h, plan 1h, execute 5h)
**Dependencies**: Item 11

**Objective**: Give studies their user surface: policy assessment over immutable evidence, result queries joining the catalog, and the study CLI contracts.

**Scope**:
1. **Policy**: user-selected interpretation of evidence (reject, penalize, keep-for-boundary, feed-strategy); assessment never mutates stored evidence; `assessment_failed` preserves real evidence.
2. **Query**: cases by parameter, output, constraint ID, status, assessment; static source detail joined through the catalog; tracking-key correlation shows fingerprint boundaries (names correlate, never equate).
3. **CLI**: create/run/resume/inspect contracts; resume refuses changed fingerprints with a new-lineage message; a rejected point retains outputs and violations for boundary plots.

**Out of Scope**:
- Visualization/plotting; optimizer configuration.

**Success Criteria**:
- [ ] A grid study runs end-to-end from CLI: define → run → interrupt → resume → query, with the resumed result identical to uninterrupted.
- [ ] Policy failure yields `assessment_failed` with evidence intact; query distinguishes the three case states and three verdict classes.
- [ ] teax suite green.

**Required Reading**: concept "Study Layer" + "How It Works" (Run a Study; Inspect and Resume) + Vocabulary.

**Location**: `~/1cfe/teax/.project/active/study-policy-cli/`

**Deliverables**:
- `spec.md`, `design.md`, `plan.md`, close-out report
- Policy protocol, query API, CLI + end-to-end test

---

### Item 13: Calc-Seam Cutover — Retire `ExpressionAST`

**Type**: Code/Integration (sysml-codegen)
**Effort**: 2 days (spec 2h, design 3h, plan 1h, execute 10h)
**Dependencies**: Item 2 (the tree); Item 7 (predicates ship first — the staged-decision ordering)

**Objective**: Execute S2's extract-and-migrate decision: the shared `ExpressionIR` + compat rendering replaces `ExpressionAST` at the expression-compiler seam, then the remaining calc consumers, each under the byte-identity gates.

**Scope**:
1. **Seam cutover**: compat renderer (input/intermediate classification at render time from supplied name sets) replaces `build_expression_ast` + `compile_expression`; byte-identical output for the entire corpus is the gate (S2 proved the renderer reproduces it — keep the proof as a test until deletion).
2. **Remaining consumers, staged**: aggregation walking, computed attributes, snapshot `compilation_results` replay — each its own gated step (S2 carry-forward (1): the ~zero convergence cost was measured at the seam only).
3. **Comparand discipline**: each step's parity gate compares against the exact function it replaces, not a downstream proxy (the F4-cutover lesson).
4. Delete `ExpressionAST` when the last consumer moves; re-capture baselines byte-identically or as a reviewed capture-script diff.

**Out of Scope**:
- New expression capability (operators, invocation) — this is representation migration, not semantics change; predicate compilation (already on IR via Item 7).

**Success Criteria**:
- [ ] Every corpus calc expression renders byte-identically through the IR path before each consumer flips; generated packages byte-identical after each step.
- [ ] `ExpressionAST` deleted; no silent third representation remains (grep gate).
- [ ] Full suite + mypy green; baselines byte-identical or reviewed.

**Required Reading**: concept Architectural Bets (predicate/IR bullet) + S2 result and carry-forward (1); memory: F4 cutover fallback divergence (comparand discipline).

**Location**: `.project/active/expression-ast-cutover/`

**Deliverables**:
- `spec.md`, `design.md`, `plan.md`, close-out report
- Staged cutover commits with per-step byte-identity evidence; `ExpressionAST` removal

---

### Item 14: Migration, Docs, and IFE Acceptance

**Type**: Testing/Validation (all repos + fusion-tea)
**Effort**: 1.5 days (spec 2h, design 1h, plan 1h, execute 8h)
**Dependencies**: Items 3, 7, 8, 9, 10, 11 (the built system)

**Objective**: Retire the drop-manifest era with a proven 1:1 migration, update authoring and architecture docs, and pass the concept's acceptance test on the IFE sweep.

**Scope**:
1. **Migration**: every constraint in today's drop manifest maps to exactly one catalog source record (kept test); every source record expands to ≥1 concrete entry or is explicitly unassessed/inventory; the manifest and both blanket warnings delete; existing constraint-adjacent tests (REQ-EXT-09 family and kin) re-anchor on the catalog.
2. **Docs**: authoring guidance flips from "constraints are not executable" to teaching the executable profile and its block list (including the real-equality → two-inequality idiom); architecture docs cover the lowering phase, catalog, contracts, evaluator, and study layer; verification matrix rows added under the register discipline.
3. **Acceptance**: regenerate the fusion-tea IFE package; replace the sweep harness's hand-coded viability rule with the generated assertion via the study layer; **every existing grid classification matches**; record the cross-model prepare-once benchmark (S5 carry-forward (2)).

**Out of Scope**:
- New IFE modeling; performance tuning beyond recording the benchmark.

**Success Criteria**:
- [ ] Migration mapping test green; `grep` finds no drop-manifest emission or blanket warning.
- [ ] IFE grid classifications match 100%; the hand-coded rule is deleted from the sweep harness.
- [ ] Docs updated in all three repos; epic Success Criteria checklist fully checkable.

**Required Reading**: concept Problem + Migration invariant + Validation Strategy (Acceptance); memory: Item-3 fusion-tea acceptance facts; plant-idiom fixtures.

**Location**: `.project/active/constraint-migration-acceptance/`

**Deliverables**:
- `spec.md`, `design.md`, `plan.md`, close-out report
- Migration tests, doc updates, IFE acceptance report with classification comparison

---

## Dependencies

**External**:
- SysIDE 0.8.4 license (live extraction legs; snapshot path is license-free). License loads via script runs, not bare `python -c`.
- teax `main` ≥ `7560d65` (merged scalar-persistence work — verified present 2026-07-12).
- fusion-tea checkout (Item 14 acceptance; also hosts the venv teax items borrow).

**Internal**:
- PUSH-DOWN shared-module pattern (agentic-mbse owns neutral semantics) — landed at `430404d`.
- Supersedes the BACKLOG "Constraint-reconstruction coverage" idea; completes the constraint-serialization decision flagged in the resolved [CONSTRAINT-SILENCE] entry.
- Coordinated-pair discipline: Items 1–3 (agentic-mbse) version their schemas; sysml-codegen consumers pin the version.

**Item Dependency Graph**:
```
Item 0 (spike, immediate) ──────────────────────────┐
                                                    ▼
Item 1 (facts) ──> Item 2 (IR) ──> Item 3 (profile) │
   │                  │               │             │
   │                  │               ▼             │
   ├──────────────────┼──────> Item 5 (lowering) <── Item 4 (index, immediate)
   │                  │               │
   │                  │               ├──> Item 8 (snapshot v3)
   │                  │               ▼
   │                  │        Item 7 (generation) <── Item 6 (module_kind, immediate)
   │                  │               │
   │                  └──> Item 13 (cutover, after 7)
   │                                  ▼
   │                           Item 9 (contracts)
   │                                  ▼
   └───────────────────> Item 10 (evaluator) ──> Item 11 (store/runner) ──> Item 12 (policy/CLI)
                                                                    │
Items 3,7,8,9,10,11 ──────────────────────────────> Item 14 (migration + IFE acceptance)
```
Three parallel tracks after Item 1: agentic-mbse (2→3), sysml-codegen (4,6 immediately; then 5→7→9, 8, 13), teax (0 immediately; then 10→11→12).

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Exit-ancestry regressions if exits ever narrow (currently incidental) | High | Item 7 makes ancestry explicit + a narrowed-exit test; Required Invariant |
| Strict-resolver seam collides with backtracker EP keys (F4-cutover lesson) | High | Item 5 builds a shared seam with explicit strict mode; never reuses the fallback as-is; parity comparand = replaced function |
| Byte-identity churn from re-captures (`captured_at` timestamps) | Med | Established gate discipline: timestamp-only diff check + revert (memory: byte-identity captured_at churn) |
| Constraint-module identity × instance count (class explosion at scale) | Med | Item 7 design decides identity mechanism *with* the measured aggregator-schema limit; module fusion pre-approved past that limit (concept) |
| Exact-unit blocking bites real quantity-typed models early | Med | Deliberate first-scope block (concept); authoring guidance teaches bare-Real idiom; exact-unit contract source is a named open spec question, not scope creep |
| Cross-repo schema skew (facts/IR versions between agentic-mbse and sysml-codegen) | Med | Versioned schemas (Items 1–2); consumers pin versions; coordinated-pair release discipline |
| teax environment provisioning (borrowed venvs, sys.path grafts) | Low | Known setup recorded in S4/S5 findings + memory; Items 10–12 should provision teax's own venv as a first step |
| Snapshot v3 forces corpus-wide re-capture with unrelated latent drift (e.g. `ife_plant` stale baseline) | Low | Known pre-existing drift is documented (memory: deep_cross_scope, ife_plant stale); review diffs deliberately, don't wave through |

---

## Timeline

**Total Effort**: ~20 days sequential; critical path ≈ 13 days (1 → 2 → 3/5 → 7 → 9 → 10 → 11 → 14) with tracks in parallel.

| Item | Effort | Dependencies |
|------|--------|--------------|
| 0 — Integration spike | 0.5d | None |
| 1 — Constraint facts | 2d | None |
| 2 — ExpressionIR | 1.5d | 1 |
| 3 — Executable profile | 1.5d | 1, 2 |
| 4 — Instance index | 1d | None |
| 5 — Concrete lowering | 2d | 1, 2, 4 |
| 6 — module_kind refactor | 1.5d | None |
| 7 — Constraint generation | 2d | 2, 3, 5, 6 |
| 8 — Snapshot v3 | 1d | 1, 5 |
| 9 — Contracts + sealing | 1.5d | 7, 8 |
| 10 — Model evaluator | 1.5d | 0 (informs), 9 (hardening) |
| 11 — Study store/runner | 2d | 10 |
| 12 — Policy/query/CLI | 1d | 11 |
| 13 — ExpressionAST cutover | 2d | 2, 7 |
| 14 — Migration + acceptance | 1.5d | 3, 7, 8, 9, 10, 11 |

---

## Lessons Learned (Post-Completion)

*Fill in after epic is complete*

**What Went Well**:
- TBD

**What Could Improve**:
- TBD

**Surprises**:
- TBD

---

**Last Updated**: 2026-07-12
**Next Action**: Item 0 (integration spike) + Items 1, 4, 6 can all start immediately
