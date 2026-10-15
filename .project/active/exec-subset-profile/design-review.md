# Design Review: Executable-subset capability contract (EXEC-SUBSET-CONTRACT Item 1)

**Design:** `.project/active/exec-subset-profile/design.md` (at `9d8a3a3e`)
**Spec:** `.project/active/exec-subset-profile/spec.md` (revised), with `spec-review.md` Resolutions
**Also read:** `briefs/align.md` (owner gates R1–R3), `.project/backlog/epic_executable-subset-contract.md`, `product-lens.md`
**Review File:** `.project/active/exec-subset-profile/design-review.md`
**Date:** 2026-10-15
**Code read (read-only):** sysml-codegen at `b5663c07` (`.git/refs/heads/main`; ADRs 0004, 0007, 0012; `elaboration/occurrence.py`, `elaboration/elaborate.py`), agentic-mbse working tree. Codegen paths below are relative to `~/src/sysml-codegen/src/sysml_codegen/`.
**Not duplicated:** the F1 occurrence-port parity spike, which is running separately. Where a finding depends on F1, it says so.

---

## The Point

The generator (sysml-codegen), L6 and the shipped guidance each hold their own picture of what the generator can execute. The pictures drift, and modelers find the generator's limits one failed run at a time. On the dc3 baseline, L6 saw B7 and B8 and missed B1–B6.

Item 1 builds the one contract the three will later share. The contract says which (shape, context) pairs the pinned generator refuses, admits, excludes or omits, with evidence for each. Item 1 builds the contract, its facts, the evaluator, the 500-site inventory and the evidence. It wires no consumer.

The governing obligation `[INHERITED: epic Item 1 objective]`: build it **without duplicating model interpretation and without broadening current refusals accidentally**. The design adds the honesty test both ways: never call a model clean when a check could not run, and never refuse what the pinned generator accepts.

## Fundamental Assessment

**Concerns. The approach is sound, but the R1 section is not ready to go to the owner.**

The core design is good. Facts, a pure evaluator, and packaged records keyed by (shape, context), with a refusal allowed only when a probe of the real generator backs it, is the right shape for this problem. It makes R2 safety mostly a property of data and tests instead of reviewer care. Defaulting unknown pairs to `unconfirmed` and failed facts to `unverified` is right. The design also caught three real spec premise errors by reading code (overridden calc writers, constructs beneath refused multiplicity, the multiplicity attribute), and surfaced them instead of silently fixing them.

What is not ready is the R1 recommendation the owner will decide on. Four problems, all in how R1 is framed:

1. **A structural smell fired: Option A changes who owns an invariant and does not say so.** sysml-codegen's active ADR 0012 (`.project/adr/0012-exclusive-semantic-evidence-ownership.md`, provenance `[INHERITED]`) says: "Raw parser reads for declaration discrimination, slot construction, and multiplicity retain their narrow codegen ownership." Option A ports exactly slot construction (`FeatureSlotIndex`, `occurrence.py:222-433`) and the multiplicity reads (`occurrence.py:812-899`) into agentic-mbse. The design cites only ADR 0007 and never mentions 0012 or 0004. The owner would be approving an amendment to a codegen ADR without being told.
2. **The port is not the thing Item 2 can migrate onto.** The design ports a summary (counts per root, writer per scope). Codegen's `OccurrenceIndex` does much more: containment addresses, `resolve_address`, `consumer_domain`, and slot lookups used across all of elaboration (`occurrence.py:448-632`, `elaborate.py:832-931`). So "Item 2 migrates codegen onto it" cannot be a swap. It is a re-plumbing of codegen's elaboration, or the copy stays forever. Together with the escape hatch "or records why not", the duplication is neither bounded nor honestly priced.
3. **The rejected alternative A′ is not represented fairly.** It is described as "Option A without the port, so approximate instantiation" and dismissed with the prototype heuristic. The honest no-port option uses no heuristic at all: instantiation-dependent contexts just report `unconfirmed` until a real move lands in Item 2. That option has a real cost (several B-categories show as `unconfirmed`, not `refused`, in Item 1), but it is not "a second, partial interpretation". The owner needs to see that trade.
4. **The authority statement does not survive Item 2.** "The pinned generator's behavior is ground truth" works today. Once Item 2 makes codegen refuse *through* the contract, the generator's behavior partly is the contract, and the probes become self-referential. The epic's answer (design principle 3) is that the authority is the underlying elaboration with the screen bypassed. R1 should say so.

None of these needs a different approach. Each is fixed inside R1 by a disclosure, a sharper boundary, or a fairer alternative. That is why the verdict is **Revise** rather than Rework. But the smell controls the R1 answer: **R1 should not go to the owner until M1 and M2 below land.**

Two further must-fixes concern R2 safety (M3–M5 below). They are cheap and mechanical.

---

## R1 advice for the owner

This is the short version of what I'd tell the owner once the design is revised.

**What Option A actually means.** agentic-mbse holds a published, versioned, probe-checked description of the generator's refusals. The generator's code still makes the refusals. A policy change (say, relaxing a refusal) still starts in codegen, or in the agentic-mbse invocation allowlist, and the records follow. So "agentic-mbse owns the decision layer" really means "agentic-mbse owns the declared contract and its evaluator; codegen owns the behavior it describes, until Item 2 makes codegen consume it". The design should state the order of change in those words.

**Is the occurrence port honest and bounded?** Honest about existing: yes. Bounded: not yet. Three changes would bound it:

- **Port the module, not a summary.** Make the agentic copy a near-verbatim move of codegen's slot index and occurrence index: same structure and API shape, neutral error types in place of `ElaborationCode`. Then Item 2's migration is an import swap plus code mapping, and parity holds because the code is the same. This is ADR 0007's own lesson: "a boundary move is byte-faithful or it is a behavior change to be reviewed as one." It will likely be larger than 500 lines (`FeatureSlotIndex` alone is about 200 lines with its builder), so F1's line count matters.
- **Remove the escape hatch.** Item 2 either deletes codegen's copy, or keeps it and runs the parity check as a permanent CI guard in codegen. "Records why not" with no guard is how two copies drift.
- **Disclose the ADR amendment.** The approved R1 amends codegen ADR 0012's ownership invariant for slot construction and multiplicity. Item 2 files that amendment, not just a pointer.

**Does the port expand Item 1 into Item 2?** The port itself writes nothing in codegen and is not observable by codegen until Item 2 adopts it. Two things do leak:

- The `reference_use` refactor is live in codegen immediately, because codegen installs agentic-mbse as an editable path dependency. The same-generator check covers it, but only on the ~40 probe fixtures (see S6).
- Item 2's real migration cost is much larger than "adopt the occurrence facts". The Item 1 close-out re-estimate must price it.

**My recommendation to the owner:** approve Option A with the three bounding changes above, or choose the honest A′ if you'd rather Item 1 report the instantiation-dependent B-categories as `unconfirmed` and let a single move happen in Item 2. Both are defensible. As written, A understates its cost and omits the ADR conflict.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Almost every spec criterion traces to a design element. Traceability table:

| Spec criterion | Design element | Status |
|---|---|---|
| Site account total; join; count reconciliation; blind spots | D10, `site_account.csv`, `scanner.toml`, `--reconcile`, Validation (join test, recorded runs) | Traced |
| Five computed reason sites closed | Implementation Notes (one test per emission) | Traced |
| Every named case has a matrix row (ES-001..012, ten PUSH-DOWN, B1–B9, U1–U7) | `matrix.toml` | **Partial:** no matrix schema, no "fixed list" check |
| Binding-source classifier fully placed, incl. relation to `L2_SELF_NAMED_BINDING` | D5; Research Findings mention L2 | **Partial:** the matrix's L2 statement is not assigned anywhere |
| Every row classified and owned | `matrix.toml` | **Partial:** row fields (class, contexts, outcome, owner, limitation) unspecified |
| Matrix and records agree | Validation (matrix ↔ records) | Traced |
| Records complete | `RuleRecord` fields, record loader | Traced |
| Every refusal has a probe | D3, invariant 1, harness | Traced (see M4 on what "observed a refusal" checks) |
| Every refused shape has an admitted-context probe | Invariant 2 | **Deviates:** adds a `no_admitted_context` escape the spec does not have (S1) |
| Refused/admitted fixtures per rule, prototype neighbors carried | Probe fixtures double as evaluator fixtures; Appendix C | Traced |
| Roots | D7, `ScopeReport`, `BEYOND_GENERATOR_ROOTS` | Traced |
| Baseline B1–B8, repaired, corpus runs | `run_trees.py`, recorded runs | Traced |
| Failure cannot look clean | Invariant 4, `UnverifiedCheck`, failure-injection tests | Traced (gaps in S3, S4) |
| Deterministic | Invariant 7 | Traced |
| No consumer coupling | Invariant 5 | Traced |
| Consumer output unchanged | `validate` diff | Traced |
| R3 proposal, re-estimate, repo checks | Evidence folder, Validation | Traced |

Spec requirements that the design does not meet as written:

- **Every non-`unconfirmed` outcome needs a probe, not only `refused`.** The spec says `unconfirmed` is "the outcome for a (shape, context) a rule recognizes but has no probe record for. That includes everything known only from reading the generator's code." The design enforces probes only for `refused` (D3, invariant 1). An `admitted`, `excluded` or `omitted` entry with no probe would load and be emitted. That breaks the design's own "honest in both directions" promise: a code-read `admitted` is a clean claim nobody observed. (M3)
- **The R2 halt rule is inverted.** Spec R2: "If a probe shows a rule's intended refusal would cover a (shape, context) the pinned generator admits, design halts that rule and asks the owner." The spec's admitted-context criterion: "Where the probe shows the generator refusing after all, the rule's contexts are corrected." The design (Probe harness, last paragraph) does the opposite: a contradicted `admitted` expectation is an R2 stop, and a contradicted `refused` expectation is silently corrected. (M5)

Capture fidelity: provenance is carried well. The Point's `[INHERITED]` and `[AGENT, ratified]` grades are right. The design treats the `[INFERRED]` Table 1 contexts as challengeable and challenges them with code (Implementation Notes a–c), which is exactly right. One miss: the spec's `[INFERRED]` "Item 1 does not claim generator-verified rules" is respected, but the design's `EvidenceStatus` drops the align record's "prototype or pending Item 2" wording without saying why. Minor.

### 2. Pattern Consistency
**Assessment:** Pass, with one concern

The layering copies the existing constraint split (`constraint_facts.py` / `constraint_extraction.py` / `executable_profile.py`), the closed-vocabulary check copies `EligibilityDiagnostic.__post_init__`, and package data follows the `extraction/check_corpus/` precedent. The ownership gate (`test_semantic_selector_ownership.py`) and purity hygiene test are reused. Good.

Concern: the pure evaluator is to import "`reference_use`'s allowlist constant" (Architecture, "The evaluator is pure"). `reference_use.py:29` imports `SysideAdapter`. Today SysIDE is imported lazily inside the adapter, so the hygiene test would pass. But the decision layer would then depend on a SysIDE-reading module, against the layer table's own "must not import SysIDE". Put `SUPPORTED_INVOCATION_IDS` in a pure module that both import. (S8)

### 3. Abstraction Quality
**Assessment:** Concerns

The three-layer split earns its keep: Item 2's snapshot route needs a SysIDE-free evaluator, and `executable_profile` already proves the pattern. The rules-recognize / records-decide split is the best idea in the design.

Concerns:

- **`OccurrenceStructure` is a summary that neither the evaluator's needs nor codegen's future adoption fit exactly.** It is the wrong level for Item 2 (see M2) and slightly wrong for Item 1: codegen resolves a multiplicity bound per *parent occurrence* (`_modeled_integer_bound` filters attribute writers by `parent.type_closure`, `occurrence.py:726-761`), so one usage can have different counts under different parents. `OccurrenceNode` holds one `count` per (usage, root). (S4)
- **TOML records with a hand-written loader versus Python literals.** A frozen-dataclass literal module would get mypy checking of `ContextId` keys and outcome values for free and need no loader. TOML is defensible because Item 5 renders from it and non-Python readers may want it. Keep TOML if that is the reason, but say so in D8. (m4)

### 4. Duplication Avoidance
**Assessment:** Concerns

This is the epic's central principle, and the design handles it honestly in places and understates it in others.

- **Honest:** the binding-source fact reuses `is_literal_node`, `unit_annotation_value` and the `inspect_reference_uses` count. I confirmed the codegen classifier's only codegen-local piece is the metatype test (`elaborate.py:1114-1118`). ES-005 reuses the allowlist predicate instead of re-detecting callables. ES-007 reuses `evaluate_identified_profile`.
- **Understated:** the Core Concept says facts "agree with the generator by construction rather than by imitation." That is true for the binding and expression facts. It is not true for the occurrence port, which is imitation by definition and is exactly why F1 exists. The sentence should say which facts are shared code and which are a port.
- **Unbounded:** the occurrence copy (M1, M2).

### 5. Data Structure Clarity
**Assessment:** Concerns

The types are mostly explicit: closed `StrEnum`s, frozen dataclasses, `SafeLocation` that never raises, and causes typed as `SemanticEvidenceCode | ScopeCause`. Gaps:

- **`ExpressionSiteFact` has two overlapping failure signals.** Indexed references reach agentic-mbse as `SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED` (`errors.py:36`), raised by the same walk that would produce `invocations`. The fact carries both `has_indexed_reference: bool` and `inspection_failure`. When the walk raises partway, `invocations` is incomplete, so ES-005 on that site must be `unverified`, not `admitted`. The design does not say this. Make the inspection outcome one total value: complete (with invocations), indexed, conditional-missing-target, or other failure. (S3)
- **Occurrence build aborts are not represented.** Besides multiplicity, `build_occurrence_index` refuses the whole model on a specialization cycle (`occurrence.py:651-658`), recursive containment (`:972-981`), incomparable typings (`:683-690`), repeated native declarations (`:944-951`) and duplicate occurrence identity (`:1033-1039`). Writer selection can also raise (`_require_one_writer`, `most_specific_definition`). The design's port "never raises a generator code" and has a status only for multiplicity. Each of these must become a `FactFailure` with `OCCURRENCE_UNAVAILABLE` (or a node status), so occurrence-dependent rules go `unverified`. (S4)
- **No "clean" in the result.** `complete` means "no unverified, not narrowed, every fact kind enumerated". The ADR draft says `unconfirmed` and `unverified` are "neither clean". But the result has no field that combines them, so a consumer could read `complete=True` with `unconfirmed` findings as clean. Add a derived verdict, or document that `complete` is not clean and why. (S5)
- **`matrix.toml` has no schema.** Three spec criteria are about matrix row content. (S9)
- **`errors.py` is listed under "Code extended" but no change to it is described.** `ScopeCause` lives in `subset_facts.py`. Remove it or say what changes. (m1)

### 6. Route Safety
**Assessment:** Concerns

Read here as "R2 safety of the outcome routes": can the evaluator reach `refused` by a path the owner did not approve?

**What the mechanism guarantees.** Every `refused` the evaluator emits names a (rule, shape, context) that some probe observed refused, and the evaluator reproduces that pair on the probe's own fixture. Unknown pairs fall to `unconfirmed`. This is a real guarantee and a good one.

**What it does not guarantee, and the design claims it does.** "R2 safety comes from the data shape, not from rule authors being careful" overclaims. The probe test checks the context computation on *one* fixture per pair. On a real model, the evaluator's `ContextId` comes from the occurrence port and the rule functions. If either maps a real situation to `owner_instantiated` when the generator would not examine it, the evaluator refuses something admitted, and no probe test notices. R2 safety therefore rests on an unstated bet: **the generator's outcome is constant within each context label.** `owner_instantiated` covers a part-def owner, a part-usage owner, a subtype's occurrence, an inherited usage, and a usage reached through `[2]`. One probe per label does not show they all behave alike. (M4, part b)

**What the probe itself checks.** Observed `refused` means "exit ≠ 0 with codes". It does not require the observed code to be the rule's code. B3 (one construct per fixture isolates one pair) relies on the inventory failing fast, but readiness findings are *collected* (`elaborate.py:1937-1940`) and fixture scaffolding can trip other refusals. Self-binding is the most common refusal in codegen's own corpus (20 of 23 refusal fixtures). A probe for ES-007 that actually failed on a scaffolding self-binding would certify the wrong pair. ES-006 is worse: its code is the generic `SI_EVIDENCE_INCOMPLETE`, so any evidence failure would certify "conditional". (M4, part a)

**The three gaps the design raised:**

- **Redefined-everywhere calc usages.** The design is right, and I confirmed why: bindings are read from the selected writer's `owned_members` only (`elaborate.py:1885`), and writers are chosen per scope (`:1227-1233`). An overridden usage's binding is never classified. Missing: the precedence rule for a usage selected in some scopes and overridden in others. It should be `owner_instantiated` with the selected-scope count. State it. (S4)
- **Constructs beneath refused multiplicity.** `unconfirmed` is R2-safe. But it exposes a premise the whole design rests on and never states: the contract describes each construct *as if the rest of the model were admitted*. The generator aborts the entire occurrence build at the first multiplicity raise, so in the baseline it examines none of the other constructs either. The contract's per-construct answer is a counterfactual. That is the right semantics, and B3 depends on it too, but it should be stated in the Core Concept so consumers read findings correctly. The subtree case is the one place the counterfactual is undefined (no count), so `unconfirmed` is correct. (S2)
- **Multiplicity attribute.** Confirmed: codegen reads `usage.multiplicity`, `is_ordered`, `is_nonunique`, `upper_bound`, `lower_bound` (`occurrence.py:820-899`). F1 covers inherited and redefinition-only cases.

**Same-generator check.** Running all probes at `a718efec` and the final revision is a good guard for the `reference_use` refactor. It is narrow: ~40 single-construct fixtures. The refactor is live in codegen through the editable path dependency. Also run codegen's own v6 corpus (and ideally its test suite) in the temp tree at both revisions. Read-only, cheap, much wider. (S6)

**Admitted probes can pass vacuously.** Exit 0 is recorded as `admitted`. If the fixture was not picked up, or a model with no roots generates nothing, exit 0 proves nothing. Each admitted probe should include an instantiated, admitted sibling and assert it appears in the generated file list. This is a miss-direction risk, not R2, but the admitted probes are what calibrate the boundary. (S7)

**Probe harness isolation** is otherwise sound: `git archive` exports verified with `get-tar-commit-id`, sibling layout so codegen's `path = "../agentic-mbse"` resolves inside `$T`, identity captured with `python -I`, abort if either package resolves outside `$T`, licence presence noted but not its value. One addition: record which agentic-mbse revision counts as "the pinned generator". Generator behavior partly lives in agentic-mbse (allowlist, `executable_profile`), and dc3 T-001 ran with agentic-mbse `8b027bbc`, not `a718efec`.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

The stated bets are genuine claims with "if false" consequences. B2 has a numeric threshold and a spike. Decisions name their rejected alternatives. That is above average.

**Hidden bets, most expensive first:**

- **H1. Outcome is constant within each `ContextId`.** This carries R2 safety (see Dimension 6). Not stated. If false, the evaluator refuses admitted shapes in sub-cases no probe covered. Mitigation: state it as a bet, and add a few context-variation probes for each instantiation-dependent refused pair: part-def owner versus part-usage owner, a subtype occurrence, an inherited usage, an owner reached only through `[2]`, two nesting levels.
- **H2. Counterfactual semantics.** The contract answers "would the generator refuse this construct if everything else were admitted". Not stated (S2).
- **H3. Same model load.** The facts must be computed over the same document set the generator loads with `generate --models P` (same discovery, same standard library handling). `build_occurrence_index` starts from `elements_of_type(model, "PartUsage")` and excludes children not in the loaded user model (`occurrence.py:938-942`). A different loader changes the root set. State it, and let F1 confirm it.
- **H4. Codegen does not move under the pin.** Parity is verified at `b5663c07` only. Codegen consumes agentic-mbse unpinned. Records should carry the generator revision they were verified against, so Item 2 can tell when they are stale. (S10)

**B2 is likely optimistic.** A faithful port needs the slot index and its builder (`occurrence.py:222-433`), type closures and effective type (`:635-691`), multiplicity with modeled bounds (`:694-899`), the index build (`:902-1046`), plus attachment and writer selection from `elaborate.py:759-787` and `:901-940`, plus `semantic_owner`, `authored_site` and declaration identity helpers. That is closer to 700–800 lines than 500. F1 will measure it; the point is that R1's cost line should not anchor on 500.

**Decisions:** D1–D12 are real decisions with alternatives. D11 (keep ES-010 refusal a candidate) and D12 (reproduce ES-002/008/009 without promoting) are well reasoned. D3's alternative is stated fairly.

### 8. Reader Comprehension
**Assessment:** Concerns

The Core Concept is excellent: a lookup table keyed by (shape, context), three steps, then the key insight. A tired engineer gets the model in one read.

What blocks understanding:

- **R1 does not tell the owner what they are deciding.** "agentic-mbse owns the decision layer" while "the generator stays the ground truth" reads as a contradiction until you work out that agentic-mbse owns a *description* and codegen owns the *behavior*. Say that plainly, and say the order in which a policy change flows (see the R1 advice above).
- **Research Findings is a dense citation list.** It is useful as evidence, but a reader cannot tell which findings drive which decision. One line per finding saying "this is why D-n" would fix it.
- **Two prose claims are stronger than the mechanism** ("by construction rather than by imitation"; "R2 safety comes from the data shape"). A reader who trusts them will under-weight F1 and H1.

---

## Issues by Severity

### Critical (must fix before the owner sees R1)

- **M1. R1 omits that Option A amends codegen ADR 0012.** ADR 0012 assigns slot construction and multiplicity raw reads to codegen. Option A ports both. The structural smell "changes who owns an invariant without saying so" fires. Fix: cite 0012 (and 0004, which Option A does honour because the port uses exact evidence) in R1 and Appendix B. State that the approved decision amends 0012, and that Item 2 files the amendment. — Dimensions 4, 7; Stage 0
- **M2. R1 does not bound the occurrence copy, and misstates A′.** Fix all three in R1:
  - (a) Port codegen's slot and occurrence index as a near-verbatim module with neutral errors that Item 2 can swap in, not a summary projection, or explain why a summary is enough for Item 2's adoption.
  - (b) Replace "or records why not" with a bound: Item 2 deletes codegen's copy, or keeps it with the parity check as a permanent codegen CI guard.
  - (c) Restate A′ as "no port, no heuristic: instantiation-dependent contexts stay `unconfirmed` until Item 2 moves the module". Give its real cost: which B-categories show as `unconfirmed` in Item 1. Also state the authority after Item 2: the underlying elaboration with the screen bypassed (epic design principle 3).
  — Stage 0, Dimensions 4, 8
- **M3. Only `refused` is probe-gated; the spec gates every outcome except `unconfirmed`.** Fix: the record loader rejects any `admitted`, `excluded` or `omitted` entry without `probe_ids`. Or, if a code-read `excluded`/`omitted` is wanted, surface it as a spec amendment. — Dimension 1
- **M4. A probe can certify the wrong pair, and the R2 claim rests on an unstated bet.**
  - (a) A `refused` observation must match the rule's `GeneratorEvidence` code. For ES-006 it must also match the cause and location in the error line. Otherwise scaffolding refusals (self-binding is the corpus's most common) or any evidence failure certify the pair.
  - (b) State H1 ("outcome is constant within each context") as a Key Bet. Add context-variation probes for the instantiation-dependent refused pairs. Soften "R2 safety comes from the data shape" to what the mechanism actually guarantees.
  — Dimensions 6, 7
- **M5. The R2 halt rule is inverted relative to the spec.** Per spec R2, a probe that contradicts a `refused` expectation (the generator admits it) halts the rule for the owner. A probe that contradicts an `admitted` expectation corrects the record's contexts. The design has these the other way round. — Dimension 1

### Major (should fix)

- **S1. `no_admitted_context` is a spec deviation, not an implementation detail.** The spec's criterion has no escape for shapes refused in every context. The design's reason is sound (asserted constraint owned by a calc def), but surface it as a spec amendment, list which shapes use it (likely ES-001 calc-def-asserted, and possibly indexed-reference), and keep its citation probe-backed. — Dimension 1
- **S2. State the counterfactual semantics in the Core Concept.** Each finding says what the generator would do with this construct if the rest of the model were admitted. B3 and the beneath-refused-multiplicity rule both depend on it. — Dimensions 6, 7
- **S3. Make the expression-site inspection outcome one total value.** Merge `has_indexed_reference`, `conditional` and `inspection_failure` into one closed outcome. Specify that rules depending on a partially inspected site (ES-005 after a mid-walk raise) report `unverified`. — Dimension 5
- **S4. Represent every occurrence-build abort, and fix count granularity.** Map the specialization-cycle, recursive-containment, incomparable-typing, repeated-declaration, duplicate-identity and writer-selection raises to `FactFailure`/`OCCURRENCE_UNAVAILABLE`. Hold counts per parent occurrence, not per (usage, root). State the precedence for a calc usage selected in some scopes and overridden in others. Add these to F1's comparison if it is still running. — Dimensions 3, 5, 6
- **S5. Distinguish complete from clean.** Add a derived verdict (or document precisely) so `complete=True` with `unconfirmed` findings is not read as clean. Itemize `unconfirmed` findings in the repaired-tree evidence, like `unverified`. — Dimension 5
- **S6. Widen the same-generator check.** Also run codegen's v6 corpus (and ideally its test suite) in the temp tree at `a718efec` and at the final revision. The `reference_use` refactor is live in codegen through the editable path. — Dimension 6
- **S7. Give admitted probes a positive control.** Include an instantiated, admitted sibling and assert it appears in the generated file list. Otherwise exit 0 can be vacuous. — Dimension 6
- **S8. Keep the decision layer free of SysIDE readers.** Move `SUPPORTED_INVOCATION_IDS` and its predicate to a pure module imported by both `reference_use` and `subset_profile`. Extend the hygiene test to `subset_profile`. — Dimension 2
- **S9. Specify the matrix schema.** Row ID, class (one of five), contexts, outcome, evidence status, owner, coverage limitation, sites, B/U cross-references, and the L2 self-binding relation. Add a test against the fixed case list (ES-001..012, self-binding, ten PUSH-DOWN rows, indexed references, deep-qualified wiring, `L6-LIBRARY-ALIAS-SOURCE`). — Dimension 1
- **S10. Version what the contract's answers actually depend on.** ES-007 outcomes depend on `executable_profile`, whose changes bump `PROFILE_SEMANTIC_VERSION`, not `SUBSET_PROFILE_VERSION`. Report both in `SubsetProfileResult`. Record in the packaged records the generator identity they were verified against (codegen revision plus agentic-mbse revision). — Dimension 7

### Minor (consider)

- **m1.** `errors.py` is listed under Code extended with no described change. — Dimension 5
- **m2.** The harness runs `--all` at two agentic-mbse revisions but `observation.json` is one file per probe. Say which run is canonical and where the other lives. — Dimension 6
- **m3.** The ES-010 omission probe uses a name oracle, which the epic calls insufficient. Prefer checking the generated contract or catalog for the attribute's identity. — Dimension 6
- **m4.** Say why TOML beats a typed Python literal for records (D8), or switch. — Dimension 3
- **m5.** Raise B2's size anchor from ≈500 to "F1 measures it; expect 700–800". — Dimension 7
- **m6.** Add one line per Research Finding naming the decision it drives. — Dimension 8

---

## Recommendations

1. Revise R1 (M1, M2) before it reaches the owner. Cite ADR 0012 and 0004. Make the port a swappable module. Remove the "or records why not" escape. Restate A′ honestly with its cost. Say who changes policy, and in what order, before and after Item 2.
2. Tighten the probe mechanism (M3, M4, M5): gate every non-`unconfirmed` outcome, match observed codes, add context-variation probes, state H1, and fix the inverted R2 halt rule.
3. Close the honesty gaps in the data model (S3, S4, S5): one inspection outcome per site, every occurrence abort as a fact failure, and an explicit clean verdict.
4. Fold F1's result into R1's cost line when the spike reports. If F1 fails its thresholds, A′ (honest form) becomes the recommendation.
5. Take the remaining should-fixes into the plan: matrix schema, wider same-generator check, positive controls, versioning.

---

## Resolutions

Resolved 2026-10-15. Every call below is `[AGENT]`: an orchestrator decision, applied by the design agent in design revision 2. None is an owner decision. R1 itself stays open for the owner.

- **M1 — `[AGENT]` accepted.**
  - R1 now has a subsection, "What it amends: codegen ADR 0012", quoting the third invariant verbatim. It states that approving Option A amends that invariant.
  - The ADR 0012 amendment is drafted in Appendix B.2, next to the agentic-mbse ADR in B.1. It is filed in sysml-codegen by Item 2, or earlier at owner direction.
  - ADR 0004 is cited as honored.
- **M2 — `[AGENT]` accepted.**
  - **A′ restated honestly.** It now reads: no port, no heuristic; instantiation-dependent contexts report `unconfirmed` until Item 2. Its dc3 cost is given:
    - B1, B4, B5 and B6 stay `refused`, and B7 stays `omitted`;
    - B2, B3 and B8 become `unconfirmed`, apart from package-owned or root cases;
    - B8's NON_NUMERICAL predicates also lose `excluded`.
  - **Option A ships the measured summary port** (F1: 416 lines, 72/72, about 600 lines in production). The near-verbatim module port (unmeasured, 600–1,000 lines) is rejected for Item 1, as D13.
  - **The copy is bounded.** The owner picks an end condition: (i) Item 2 grows the port into the module and swaps codegen onto it, or (ii) a permanent parity test runs in codegen CI. The agent leans to (ii), and "records why not" is removed.
  - **Ground truth after Item 2** is Item 2's screen-bypassing independent corpus.
  - **Order of policy change** is stated before and after Item 2.
- **M3 — `[AGENT]` accepted.**
  - D3 and invariant 1: every outcome except `unconfirmed` needs evidence.
  - `refused`, `excluded` and `omitted` need a probe. `admitted` needs a probe or a corpus snapshot citation.
  - The loader enforces this.
- **M4 — `[AGENT]` accepted.**
  - **(a) Certification.** A probe certifies a pair only if its observed code set equals the shape's expected code and the error location falls in the construct's declared line range. That location check matters most for ES-006's generic code. An admitted probe also needs a positive-control sibling in the output (invariant 2).
  - **(b) Within-context homogeneity.** This is now stated as bet B5, and Appendix C adds variation probes for each instantiation-dependent refused pair. The "R2 safety comes from the data shape" claim is replaced by a guaranteed / not-guaranteed statement in the Core Concept.
- **M5 — `[AGENT]` accepted.** The halt direction now follows the spec:
  - generator admits where a refusal was expected → stop the rule for the owner (R2 track);
  - generator refuses where admission was expected → record the observation and correct the contexts;
  - a variation that disagrees splits the context.
- **S1 — `[AGENT]` accepted.** `no_admitted_context` is recorded as proposed spec amendment SA-1, in the design and in the spec change log. It is not applied silently. Likely users are listed.
- **S2 — `[AGENT]` accepted.** The counterfactual semantics are stated in the Core Concept, with F1 Surprise 4 (the dc3 baseline stops at `product`) as the example.
- **S3 — `[AGENT]` accepted.** `SiteInspection` is now one total value: a reference outcome and an invocation outcome, each either complete or failed, plus the recognized conditionals. The rule consequences are spelled out.
- **S4 — `[AGENT]` accepted.**
  - Occurrence aborts get a closed `OccurrenceAbort` vocabulary. These are the cases F1 matched, plus writer ambiguity, and each makes the occurrence-dependent rules `unverified`.
  - Counts are held per parent occurrence; F1 matched `Site::racks` at 4, 2 and 2.
  - A writer selected in some scopes is `owner_instantiated`, with its count.
- **S5 — `[AGENT]` accepted.** A derived `Verdict` (INCOMPLETE / REFUSED / UNCONFIRMED / CLEAR) is added; only CLEAR is clean. The repaired-tree evidence itemizes `unconfirmed` findings as well as `unverified` ones.
- **S6 — `[AGENT]` accepted.** The same-generator check also runs codegen's v6 corpus and its pytest suite in the temp tree, at both agentic revisions.
- **S7 — `[AGENT]` accepted.** Admitted probes declare a positive-control sibling that must appear in the generated output.
- **S8 — `[AGENT]` accepted.**
  - The allowlist moves to a pure `invocation_allowlist.py`, imported by both `reference_use` and `subset_profile`.
  - The evaluator no longer imports `reference_use`, and the hygiene test covers `subset_profile`.
- **S9 — `[AGENT]` accepted.**
  - The matrix row schema is in Appendix A, including `l2_relation` for SELF-BINDING.
  - A test checks the fixed case list.
- **S10 — `[AGENT]` accepted.**
  - The result reports both `SUBSET_PROFILE_VERSION` and `PROFILE_SEMANTIC_VERSION`.
  - Records carry `verified_against`.
  - The pinned generator is defined as codegen `b5663c07` with agentic-mbse at Item 1's final revision; dc3 T-001's `8b027bbc` is noted.
- **Minor m1–m6 — `[AGENT]` accepted.**
  - m1: `errors.py` is removed from the code-extended list.
  - m2: `observation.json` (final revision) is canonical and `observation.base.json` holds the comparison.
  - m3: the omission oracle checks catalog/contract identity with a numeric control; Item 2's semantic oracle replaces it.
  - m4: TOML is justified in D8.
  - m5: B2's size is now the measured F1 figure.
  - m6: each Research Finding names the decision it drives.
- **Spike F1 folded in — `[AGENT]`.**
  - The false premise that `declared_multiplicity` differs from `multiplicity` is corrected in Research Findings, B4, Implementation Note (c) and F2.
  - The two generator multiplicity behaviors the port copies are mirrored, not fixed (D14). They are matrix rows G1 and G2, class tracked gap, routed to Item 2/owner.
  - The two `referent`/`chaining_features` accessors are on the plan surface. The existing `resolved_referent`/`resolved_chaining_features` are tried first.
  - The 11 edge fixtures seed the shipped parity test, together with stored codegen-oracle expectations.

**Status:** must-fixes M1–M5 have landed in design revision 2. Per this review's Next Steps, they need verifying, not a fresh review. R1 then goes to the owner with F1's findings.

---

**Overall:** Revise. The structure is sound. R1 is not ready for the owner until M1 and M2 land, and M3–M5 must land before planning.
**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the design-agent session) and point it at this review. The reviewer does not edit the design. After the revision, present R1 to the owner together with the F1 spike findings. A fresh design review is not needed if the must-fixes land as described. Verifying them is enough.
