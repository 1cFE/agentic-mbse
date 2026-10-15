# Design: Executable-subset capability contract (EXEC-SUBSET-CONTRACT Item 1)

**Status:** Draft, revision 2 (design review M1–M5 and S1–S10 resolved, spike F1 folded in). Next: verification of the must-fixes, then **owner gate R1**. § R1 is a recommendation, not a decision.
**Owner:** Reid Westwood
**Created:** 2026-10-15 · **Revised:** 2026-10-15
**Branch / base:** `exec-subset-profile`; design base `a718efec`, revised at `8f9fd158`
**Pins (read-only):** sysml-codegen `b5663c07e987a892e27d21e68cec40d0656574ee`; dc3 `808464df…` (baseline), `60b44d53…` (repaired); SysIDE 0.8.4

## Overview

Item 1 builds one declared contract of which (shape, context) pairs the pinned generator refuses, admits, excludes or omits. It has four parts:

- **Facts:** neutral facts extracted once from SysIDE.
- **Evaluator:** a pure function that turns facts into outcomes.
- **Rule records:** packaged data holding the outcome for each (shape, context) pair together with its evidence.
- **Inventory:** a site account plus a matrix that accounts for every refusal site.

No consumer is wired.

## Related Artifacts

- Spec: [spec.md](spec.md) (revised after review; change log records the proposed amendment from this design); review and resolutions: [spec-review.md](spec-review.md); align record and owner gates R1–R3: [briefs/align.md](briefs/align.md); product lens: [product-lens.md](product-lens.md)
- Design review: [design-review.md](design-review.md) (verdict Revise; resolutions recorded there)
- Spike F1, occurrence-port parity: [spikes/f1-findings.md](spikes/f1-findings.md), with harness and fixtures in `spikes/f1-occurrence-port/`
- Epic: [epic_executable-subset-contract.md](../../backlog/epic_executable-subset-contract.md) (Item 1; boundaries with Items 2–5; D1–D3)
- Prototype (feasibility only): `.project/concepts/convince-me-exec-subset/evidence/`
- Decision records: agentic-mbse `.project/adr/` has no entries. The relevant codegen ADRs are in `~/src/sysml-codegen/.project/adr/`:
  - 0004, derive occurrences from exact evidence or refuse ([OWNER]);
  - 0007, agentic-mbse owns neutral facts;
  - 0012, exclusive semantic-evidence ownership ([INHERITED]).
- Code extended: `src/agentic_mbse/sysml/{reference_use,syside_adapter}.py`. Code reused unchanged: `executable_profile.py`, `constraint_extraction.py`, `expression.py`.

## The Point

[INHERITED: epic Item 1 objective] Define and implement the structural contract **without duplicating model interpretation and without broadening current refusals accidentally**.

[AGENT, ratified by owner 2026-10-15] The generator, L6 and shipped guidance today each hold their own picture of what the generator can execute. They drift, and a modeler finds the generator's limits one failed run at a time. On dc3, L6 saw B7 and B8 and missed B1–B6. Item 1 replaces the three pictures with one contract that later items consume: codegen in Item 2, L6 in Item 3, rendered guidance in Item 5.

The contract is only worth having if it is honest in both directions:

- it must never call a model clean when a check could not run;
- it must never refuse something the pinned generator actually accepts.

## R1 — Capability-policy ownership (owner gate, recommendation only)

### The situation

The contract needs to know which part usages the generator instantiates. Three outcomes depend on that: whether a sequence binding is refused (ES-003/ES-012, dc3 B2), whether a ranged multiplicity is refused (ES-004, B3), and whether a blocked predicate is refused (ES-007, B8). The generator only examines those shapes inside parts it instantiates.

The instantiation logic exists only in codegen today (`elaboration/occurrence.py`, `elaborate.py:759-952`). It covers roots, redefinition slots, multiplicity counts, and which redefined calc usage is the one that runs in each scope. agentic-mbse cannot import codegen. So Item 1 must either copy that logic or leave those cases undecided.

There are two things to decide:

1. **Who owns what.** The question is where the line runs between facts, decisions and consumers. ADR 0007 settles that model facts live in agentic-mbse and output facts in codegen. It does not settle who owns the admit/refuse decision.
2. **What to do about the instantiation logic.** Copy it into agentic-mbse now (Option A), or leave it in codegen and accept honest gaps until Item 2 (Option A′).

### What "owning the contract" means, in plain words

agentic-mbse would own a **published, versioned description** of the generator's refusals, plus the evaluator that applies it. Codegen keeps owning the **behavior** the description describes.

How a policy change flows depends on whether Item 2 has landed:

- **Until Item 2.** A change starts in codegen's code, or in the invocation allowlist in agentic-mbse. Then a probe shows the new behavior, the record changes, and `SUBSET_PROFILE_VERSION` bumps, all in one coordinated merge.
- **After Item 2,** codegen refuses *through* the contract, so the generator's live behavior partly is the contract. Probes of it become self-referential, so ground truth moves to **Item 2's independent corpus.** That corpus is codegen's underlying elaboration, run with the contract screen bypassed (epic design principle 3). A policy change is then a record change plus an elaboration change, verified against that corpus.

Both options below share this layering:

| Layer | Owner | Holds | Must not |
|---|---|---|---|
| Facts | agentic-mbse (reads SysIDE) | What the model declares: expression sites, binding sources, assertion owners, String values, constraint facts; under A also occurrence structure | Decide admit/refuse (one grandfathered exception, below) |
| Decisions | agentic-mbse, pure (no SysIDE) | `subset_profile.py`, packaged rule records, `SUBSET_PROFILE_VERSION`, neutral reason IDs, outcomes | Import SysIDE, codegen or a SysIDE-reading module; use `SI_*` names outside evidence fields |
| Consumers | codegen (Item 2), L6 (Item 3), docs (Item 5) | Code mapping (one-to-many), output facts, severity, rendering | Re-derive a decision the contract holds |

**The grandfathered exception.** `reference_use._require_supported_invocation` (`reference_use.py:395-428`) is a capability decision ("only `NumericalFunctions::sum`") living in the fact layer, and codegen's ES-005 refusal is that raise. Moving it would change codegen's refusal path, which is Item 2's call. Both options leave the raise in place. The allowlist itself moves to a pure module that `reference_use` and the profile both import (S8). Changing the allowlist must bump `SUBSET_PROFILE_VERSION`, and a test enforces it.

### Option A — copy the instantiation logic into agentic-mbse as a shared fact

- **What ships in Item 1.** The **summary port** spike F1 measured. It covers roots, every occurrence by full path with per-parent counts, which part definitions have occurrences, the winning calc usage per scope, and the multiplicity resolution class.
  - Size: 416 physical lines (333 of code). The spike estimates ~600 lines in production with fact types, failure vocabulary and caller roots.
  - Parity: 72 of 72 cases match codegen `b5663c07` on every criterion, including whole-model aborts. The cases are the prototype fixtures, all 37 corpus fixtures, both dc3 trees and 11 edge fixtures.
  - Controls: deliberately wrong ports are caught. The prototype heuristic is flagged on 32 of 72 cases.
- **What it is not.** It is not a near-verbatim move of codegen's `OccurrenceIndex`. That class also carries containment addresses, `resolve_address`, `consumer_domain` and slot lookups used throughout elaboration (`occurrence.py:448-632`). A module port is unmeasured; the spike estimates 600–1,000 lines.
  - **I recommend the summary port** for Item 1. It is measured, it is everything the contract needs, and the spike's parity harness is independent of the port's shape. So the module question can be decided in Item 2 with the same safety net.
  - The cost is that Item 2 cannot just swap codegen onto the summary. A swap needs the module port plus re-plumbing of codegen's elaboration.
- **The end condition (the owner picks one now, so the copy is bounded):**
  - **(i) One copy.** Item 2 grows the port into the module, swaps codegen onto it and deletes codegen's copy. Highest Item 2 cost; no lasting duplication.
  - **(ii) Two copies, mechanically held together.** Codegen keeps its copy. Item 2 makes the parity check a permanent codegen CI test over the corpus and the edge fixtures. The spike's run takes ~70 s. The extra Item 2 cost is a CI test; the cost that lasts is two copies that cannot drift silently.
  - *My lean is (ii)* unless Item 2 is re-plumbing elaboration anyway. "Records why not", the earlier escape hatch, is removed.
- **What it amends: codegen ADR 0012.** Its third invariant reads: "Raw parser reads for declaration discrimination, slot construction, and multiplicity retain their narrow codegen ownership; reviewed manifests guard the acquisition operations rather than banning all raw reads."
  - Option A puts slot construction and the multiplicity reads in agentic-mbse too. **Approving A amends that invariant.**
  - The amendment is drafted in [Appendix B](#appendix-b--adr-drafts-r1). It is filed in sysml-codegen, the repository that upholds 0012, when Item 2 starts, or earlier if the owner prefers.
  - ADR 0004 is honored. The port derives occurrences from exact evidence and turns every abort into a named fact failure, never an approximation.
  - In agentic-mbse, the port's two raw reads (`referent` of a referenced bound, `chaining_features` of a redefined endpoint; spike Surprise 3) go through `reference_use` accessors, so the selector-ownership gate stays green.

### Option A′ — no port, no heuristic

- **What it does.** The evaluator decides only contexts that need no instantiation facts: owner kind, package-owned usages, expression sites, root-level part usages (the root rule is one line), and attribute usages. Every instantiation-dependent context reports `unconfirmed` until Item 2 moves the logic once. This option has no second interpretation and no approximation.
- **What it costs on dc3 baseline:**
  - **Still `refused`:** B1 (calc-usage-owned assert; the owner-kind check is model-wide), B4 and B5 (`product`, `size`), and B6 (conditional). These are inventory sites, model-wide.
  - **Still `omitted`:** B7 (String).
  - **`unconfirmed` instead of `refused`:**
    - B2 (sequence actual, ES-003), except in package-owned calc usages;
    - B3 (the 20 facility-library `[*]` parts, ES-004), except root part usages;
    - B8, the 4 BLOCK predicates (ES-007), except package-owned constraints. Its 4 NON_NUMERICAL predicates also become `unconfirmed` rather than `excluded`.
  - The baseline criterion ("reports every confirmed category B1–B8") would need the owner to accept B2, B3 and B8 as `unconfirmed`. The repaired-tree criterion (zero `refused`) still passes.
  - It also loses the ES-003 `writer_overridden` and multiplicity-beneath cases, because those can't be computed without the port.
- **What it amends.** Nothing. ADR 0012 stands, and Item 2 does the single move.

### Rejected outright

- **B. Codegen owns policy; agentic-mbse ships facts only.** L6 and guidance could consume it only by importing codegen, which is a [HARD] violation, or by re-implementing it, which is the drift this epic exists to stop.
- **C. Decisions inside the fact layer** (generalizing the allowlist pattern). Capability refusals would arrive as evidence errors, indistinguishable from real evidence failures; ES-006 already shows the harm. Per-node facts cannot see instantiation context, and decisions could not be versioned or evaluated without SysIDE.
- **D. Shared records, each consumer implements them.** That means two implementations per decision, held together by review alone.

### Recommendation

**Approve Option A with the summary port, end condition (ii), and the ADR 0012 amendment.** The reason: A′ leaves three of the eight dc3 categories (B2, B3, B8) undecided in Item 1. Those are the categories L6 missed and modelers hit most. The cost of A is measured, not guessed: ~600 production lines that matched codegen on 72 of 72 cases, plus a permanent CI parity test. A′ is defensible if the owner would rather not amend ADR 0012 before Item 2, and the design supports switching to it. The only change would be that occurrence-dependent contexts report `unconfirmed`.

## Research Findings

Verified at sysml-codegen `b5663c07` and agentic-mbse `a718efec`. Codegen paths are relative to `src/sysml_codegen/`. Each finding names the decision it drives.

- **Roots** (`elaboration/occurrence.py:902-923`) are every `PartUsage` whose `owning_type` (or `owner`) is neither a part def nor a part usage. → D7, root tests.
- **Reach** (`occurrence.py:927-1046`). Children are the composite user-model `PartUsage`s in `usage.usages`, with one effective declaration per redefinition slot (`:249`). They are visited once per multiplicity index, so `[0]` instantiates nothing. `occurrences_for_type` includes subtypes (`:505-508`). → R1, the port.
- **Multiplicity** (`occurrence.py:812-899`) reads `usage.multiplicity`, `is_ordered`, `is_nonunique`, `upper_bound` and `lower_bound`. In SysIDE 0.8.4, `multiplicity` and `declared_multiplicity` return the same element on every usage in all 72 spike cases. Neither is inherited through `:>>`, and neither is `is_ordered` (F1 Surprise 1). A bound is evaluated with agentic's `evaluate_true_static_expression` or through one referenced writer chosen by owner kind (`:694-788`). Counts are per parent occurrence. → `part-multiplicity`, matrix rows G1/G2.
- **Attachment and writers** (`elaborate.py:759-787`, `:901-952`, `:1195-1233`). A part-def owner gets the occurrences of its type; a part-usage owner gets its own; a package always gets one scope; anything else gets none. Calc usages in one redefinition slot share scopes, and only the winning writer's bindings are classified (`:1885`). → contexts `writer_overridden`, `owner_instantiated`.
- **Occurrence aborts.** The build refuses the whole model on any of these:
  - a specialization cycle (`:651-658`);
  - recursive containment (`:972-981`);
  - incomparable typings (`:683-690`);
  - repeated native declarations (`:944-951`);
  - duplicate occurrence identity (`:1033-1039`);
  - a writer-selection ambiguity.

  The port reproduces each one (F1). → `OccurrenceAbort` vocabulary.
- **Binding classifier** (`elaborate.py:2130-2196`). It strips a unit annotation, tests `is_literal_node`, then requires exactly one inventoried use and a chain or reference metatype. Self-binding is `leaf.element_id == formal.element_id` (`extraction/binding_source.py:87-89`). → D5; this fact is shared code, not a port.
- **Expression inventory** (`elaboration/expression_evidence.py:249-347`) covers declared-feature values (four roles) and constraint predicates. It runs before any occurrence work and fails fast (`orchestration/elaborated_pipeline.py:272-278`). A calc def's bare result expression becomes a `MANUAL_REQUIRED` stub (`extraction/expression_compiler.py:285-303`). → expression-site contexts, B3 (single construct per probe).
- **Code mapping** (`elaborated_pipeline.py:389-396`, `:425`). Two evidence codes have named codes; everything else is `SI_EVIDENCE_INCOMPLETE`. → M4 code matching; the ES-006 location check.
- **CLI** (`cli/__init__.py:1026-1069`, `:857`). `generate --models P --output D`, exit 1 on failure, codes in `ERROR:` lines. agentic-mbse resolves through `[tool.uv.sources] path = "../agentic-mbse"`. → probe harness.
- **agentic precedent.** `constraint_facts.py` (pure types) / `constraint_extraction.py` (SysIDE) / `executable_profile.py` (pure decisions, `REASON_CODES` validated at `:123-132`). There is a selector-ownership gate (`tests/test_sysml/test_semantic_selector_ownership.py:24-32`), a purity hygiene test, and a package-data precedent (`extraction/check_corpus/`). `reference_use` already exposes `resolved_referent` (`:190`) and `resolved_chaining_features` (`:200`). → D1, S8, the accessors.
- **L2 self-binding** (`validation/level2_structure.py:322-336`) checks calc usages and bare references in every context. It answers a native-correctness question, not the generator-refusal question. → matrix row SELF-BINDING, `l2_relation`.

## Core Concept

The contract is a **lookup table keyed by (shape, context), whose entries must carry evidence.**

1. **Facts** say what the model contains and where. "This calc input is bound to `(a, b)`." "Its owner `Site` has 2 occurrences under generator roots, and this usage wins in both." Two kinds of fact must not be confused:
   - **Shared-code facts** (binding sources, expression sites, the allowlist, constraint facts) call the same agentic helpers the generator calls, so they agree by construction.
   - **The occurrence facts** are a port of codegen logic. They agree by imitation, and the recorded parity check is what holds them to it.
2. **Rules** are small pure functions. Each recognizes a *shape* in the facts and computes its *context* from a closed vocabulary. A rule never decides the outcome.
3. **Records** decide. Each rule record maps (shape, context) to an outcome. Every outcome except `unconfirmed` must cite evidence, either a probe or, for `admitted`, a corpus fixture. A probe is a retained run of the pinned generator on a single-construct fixture whose observed code matches the rule's expected code. Any pair the record does not list reports `unconfirmed`.

**Counterfactual semantics.** Each finding states what the generator does with *this construct as if the rest of the model were admitted*. The generator itself fails fast. On the dc3 baseline it stops at `product(…)` and never reports its 72 unresolved multiplicities (F1 Surprise 4). A finding is therefore not "the next error the generator will print". The one place the counterfactual is undefined is beneath a refused multiplicity: there is no count, so findings there are `unconfirmed`.

**What the mechanism guarantees, and what it does not.**

- **Guaranteed:** every `refused` names a (rule, shape, context) that a probe observed refused with the expected code, and the evaluator reproduces that pair on the probe's own fixture.
- **Not guaranteed:** that every real situation the evaluator files under a context behaves the way the probed one did. That rests on bet B5 (outcome is constant within a context) and on the port's parity (B2). Both are tested, not assumed: variation probes for B5, the parity test for B2.

Missing facts are handled separately. A rule whose required facts failed cannot look anything up. It emits `unverified`, and the result's verdict is `incomplete`.

## Key Bets

- **B1. The generator's capability boundary is determined by model facts readable from SysIDE before elaboration.** *If false → some contexts are decidable only after elaboration and stay `unconfirmed`/`unverified`.* (F1 confirmed this for occurrence facts.)
- **B2. The summary port stays at parity with codegen on models beyond the spike's 72 cases.** *If false → the evaluator files a construct under the wrong context. The parity test (edge fixtures plus corpora) and, under end condition (ii), codegen CI are the guard.* The real corpora barely exercise redefinition paths (F1 controls), so the edge fixtures carry the weight.
- **B3. A single-construct fixture whose observed code equals the rule's expected code isolates one (shape, context) pair.** The inventory fails fast and codegen reports its first error class. *If false → a probe certifies the wrong pair.* Code matching (M4) checks this on every probe.
- **B4. Reading the same SysIDE attributes as codegen gives the same answers, whatever SysIDE's semantics are.** F1 found the semantics differ from what this design first assumed: nothing is inherited through `:>>`. Parity held anyway, because the port reads `usage.multiplicity` as codegen does. *If false → facts diverge on inherited shapes; the parity test catches it.*
- **B5. The generator's outcome is constant within each context label.** `owner_instantiated` covers a part-def owner, a part-usage owner, a subtype occurrence, an inherited usage and a usage reached through `[2]`. *If false → the evaluator refuses an admitted sub-case no probe covered.* Variation probes (Appendix C) test it for each instantiation-dependent refused pair. A failing variant splits the context; it is never absorbed.
- **B6. The facts are computed over the same document set the generator loads.** F1 confirmed this on 54 elaborating cases: `SysideAdapter.load_model` gives codegen's population. *If false → the root set differs.*

## Key Decisions

- **D1. Three layers mirror the constraint split.** Pure fact types, SysIDE extraction, and a pure decision module. *Rejected: one module (it breaks the SysIDE-free purity Item 2's snapshot route needs).*
- **D2. Outcomes come from records keyed by (rule, shape, context); unlisted pairs are `unconfirmed`.** *Rejected: outcomes hard-coded in rule functions.*
- **D3. Every non-`unconfirmed` outcome requires evidence, checked when records load.**
  - `refused`, `excluded` and `omitted` need ≥1 probe.
  - `admitted` needs ≥1 probe or a corpus citation (`corpus:v6_recapture_batch/<fixture>`, snapshot fixtures only).
  - A record that violates this fails to load, the same way `EligibilityDiagnostic` rejects an unknown reason.
  - *Rejected: gating only `refused` (a code-read `admitted` is a clean claim nobody observed; spec Evidence bar).*
- **D4. Reasons are a sibling closed set, `SUBSET_REASON_CODES`, disjoint from `REASON_CODES`.** ES-007 findings carry their executable-profile reasons as `detail_reasons`. *Rejected: extending `REASON_CODES` (it would bump `PROFILE_SEMANTIC_VERSION` with no predicate change).*
- **D5. One `binding-source` rule over one binding-source fact** (matrix rows ES-003, ES-012, SELF-BINDING). A separate `indexed-reference` rule covers indexed references, which the inventory refuses model-wide. *Rejected: separate ES-003/ES-012 rules over one classifier.*
- **D6. Identity and dedup are by declaration.** A finding is keyed by (rule, shape, context, subject UUID), and carries `occurrence_count` and `via_roots`. Declaration and occurrence counts are reported separately. *Rejected: per-occurrence findings (they inflate counts).*
- **D7. Roots are an extraction input; their meaning is decided in the evaluator.** Extraction always computes the generator root set plus the reach of any caller-supplied `PartUsage` roots.
  - A finding reachable only from extra roots gets context `beyond_generator_roots`, which is `unconfirmed`.
  - Narrowing the roots sets the verdict to `incomplete`.
  - *Rejected: evaluator-only roots (computing reach needs SysIDE).*
- **D8. Location.** Rule records are package data in TOML. Probes, matrix and site account are test data. Run logs live in `.project`.
  - TOML over a typed Python literal: Item 5 renders guidance from the records, non-Python readers review them, and diffs stay readable. A ~60-line validated loader buys that.
  - *Rejected: everything in `.project` (archival would break tests).*
- **D9. Every prototype fixture is re-run through the new harness.** *Rejected: reusing prototype runs (not isolated, no identity).*
- **D10. Harden the prototype scanner** (`02-inventory.py` → `scripts/subset_profile/scan_sites.py`). The hardened version:
  - runs on pinned `git archive` exports;
  - writes its revision and recognized forms into its output header;
  - maps the 5 computed `executable_profile` sites to `REASON_CODES`;
  - has a `--reconcile` mode that exits non-zero on unaccounted sites or orphan rows.
  - *Rejected: a rewrite.*
- **D11. The ES-010 refusal side stays a candidate.** Its projection boundary has three entry paths, and entry-point membership is an output fact. *Rejected: promoting the one-path restatement.*
- **D12. Probe scope.** Probe every pair a rule can report as anything but `unconfirmed`. Add variation probes for B5. Reproduce ES-002, ES-008 and ES-009 once each without promoting them (they go to R3). ES-011 is not probed; Item 2 owns it.
- **D13. The occurrence port is the measured summary port, not a module port** (R1). *Rejected for Item 1: the near-verbatim module port (unmeasured, 600–1,000 lines, only pays off if the owner picks end condition (i)).*
- **D14. The port mirrors codegen's two multiplicity behaviors; it does not fix them** (F1 Surprise 2).
  - (a) A part redefinition that omits bounds expands to one occurrence and loses `ordered`.
  - (b) A usage-level override of a definition-owned referenced bound is ignored.
  - Both go into the matrix as generator-correctness questions, class "separately tracked gap", owned by Item 2/owner.
  - *Rejected: correcting them in the contract (the contract would then disagree with the generator, which is R2-adjacent and not Item 1's call).*

## Architecture

```
SysIDE model ─► occurrence_extraction ─► OccurrenceStructure ───┐
             ─► subset_extraction ─────► SubsetFacts ───────────┼─► subset_profile.evaluate ─► SubsetProfileResult
             ─► constraint_extraction ─► IdentifiedConstraintFacts ┘        ▲                (verdict, findings,
                    (existing)                                    rules.toml (package data)    unverified, scope)
```

- **Facts are total.** Extraction runs per fact kind and per element.
  - An element failure becomes a `FactFailure`, carrying the closed `SemanticEvidenceCode` where one applies.
  - An occurrence-build abort becomes one `FactFailure(OCCURRENCE, OccurrenceAbort.<kind>)`, and every occurrence-dependent rule reports `unverified`.
  - A kind that fails to enumerate is marked not enumerated.
- **The evaluator is pure.** `evaluate_subset_profile(facts, rules=PACKAGED_RULES) -> SubsetProfileResult`. It imports fact types, `executable_profile` and the pure allowlist module, never `reference_use` or SysIDE. The hygiene test covers it.
- **ES-007 reuses the executable profile.** The evaluator calls `evaluate_identified_profile`.
  - BLOCK in an attached scope → shape `blocked_predicate`.
  - NON_NUMERICAL → `excluded`.
  - UNASSESSED → counted in coverage, never `admitted`.
- **ES-005 reuses the allowlist.** `reference_use` gains a public `invocation_uses(expression)`: a total walk that resolves no references and uses the same dispatch order as `_walk`. Both it and `_require_supported_invocation` call the one allowlist predicate. The change is byte-faithful, and the same-generator check confirms it.
- **Consumers are untouched.** `agentic-mbse validate` output is diffed before and after.

## Required Invariants

1. The record loader rejects any non-`unconfirmed` admission without the evidence D3 requires.
2. A probe certifies a pair only if all of the following hold:
   - its fixture declares one probed construct;
   - for `refused`, the observed code set equals the shape's expected `GeneratorEvidence` code, and the error line's location falls in the construct's declared line range. ES-006's generic `SI_EVIDENCE_INCOMPLETE` is the case this location check guards;
   - for `admitted`, exit is 0 and a declared positive-control sibling appears in the generated output;
   - its identity matches the pin.

   `test_subset_probe_evidence.py` checks this for every cited probe, and checks that the evaluator reproduces each pair on the probe's own fixture.
3. Every refused shape has an admitted-context probe, or a `no_admitted_context` statement whose cited refused probes span every context the rule can compute (proposed spec amendment SA-1, below).
4. Any (shape, context) not listed in a record yields `unconfirmed`.
5. A missing required fact kind, an occurrence abort or a failed element yields `UnverifiedCheck`, never an empty clean result. Rules whose facts are available still report.
6. No `agentic_mbse` module imports `sysml_codegen`. No rule or reason ID matches `SI_[A-Z_]+` or names a consumer type. `SI_*` appears in packaged records only in evidence fields.
7. Every emitted reason is in `SUBSET_REASON_CODES`, and every `detail_reason` is in `REASON_CODES` (`SubsetFinding.__post_init__`).
8. Findings are sorted by (rule, file, line, qualified name, context, shape, UUID). Permuting the document order gives identical output.
9. A change to the allowlist or the records changes `SUBSET_PROFILE_VERSION`; a test pins a digest of both. The result reports both `SUBSET_PROFILE_VERSION` and `PROFILE_SEMANTIC_VERSION`. The records carry `verified_against` (codegen and agentic-mbse revisions).
10. The port's output equals the stored codegen-oracle expectations on the parity seed (§ Validation).

## Component Overview

All under `src/agentic_mbse/sysml/` unless stated.

- **`occurrence_facts.py`** (pure types): `OccurrenceStructure`, `OccurrenceNode` (per occurrence path, with parent), `MultiplicityReading`, `Attachment`, `WriterSelection`, `OccurrenceAbort`.
- **`occurrence_extraction.py`** (SysIDE): the summary port from F1 (`spikes/f1-occurrence-port/occurrence_port.py`), productionized. Its raw `referent`/`chaining_features` reads go through `reference_use.resolved_referent`/`resolved_chaining_features`. If those differ from codegen's raw reads, the plan adds two named accessors in `reference_use`.
- **`subset_facts.py`** (pure types): `SubsetFacts`, per-kind facts, `SiteInspection`, `ElementRef`, `SafeLocation`, `FactFailure`.
- **`subset_extraction.py`** (SysIDE): builds `SubsetFacts` with `inspect_reference_uses`, `invocation_uses`, `unit_annotation_value`, `is_literal_node`, `extract_identified_constraint_facts` and `SysideAdapter`.
- **`invocation_allowlist.py`** (pure): `SUPPORTED_INVOCATION_IDS` and the predicate. Imported by `reference_use` and `subset_profile`.
- **`subset_profile.py`** (pure): versions, `SUBSET_REASON_CODES`, the `ContextId`/`Outcome`/`Verdict` enums, the record loader and validator, the rule functions, and `evaluate_subset_profile`.
- **`subset_profile_rules.toml`** (package data).
- **`reference_use.py`** (edit): `invocation_uses()`; the allowlist import; accessors if needed.
- **`scripts/subset_profile/`** (dev tooling, not shipped): `probe.py`, `scan_sites.py`, `run_trees.py`, `occurrence_parity.py` (the F1 oracle and compare, promoted), `render_matrix.py`.

## Where things live

| Artifact | Location | Why |
|---|---|---|
| Rule records | `src/agentic_mbse/sysml/subset_profile_rules.toml` | Runtime contract; Item 2 pins it, Item 5 renders it |
| Probes | `tests/fixtures/subset_profile/probes/<id>/{probe.toml, model.sysml, observation.json, observation.base.json}` | One fixture serves the probe and the evaluator test. `observation.json` (Item 1's final agentic revision, what ships) is canonical; `observation.base.json` (at `a718efec`) is the same-generator comparison |
| Matrix | `tests/fixtures/subset_profile/inventory/matrix.toml` (schema in Appendix A) | Cross-check tests read it; holds codegen paths (evidence, not product) |
| Site account, scanner manifest | `tests/fixtures/subset_profile/inventory/{site_account.csv, scanner.toml}` | Join test; `scanner.toml` names the revision, recognized forms and blind spots |
| Occurrence parity seed | `tests/fixtures/subset_profile/occurrence/` (the 11 F1 edge fixtures plus the prototype fixtures, each with `expected.json` captured from the codegen oracle at `b5663c07`) | Lets pytest check port parity without importing codegen; F1 showed these fixtures, not the corpora, catch the wrong-writer and wrong-slot ports |
| Other evaluator cases | `tests/fixtures/subset_profile/cases/` | Roots, determinism, failure injection |
| Run logs and reports | `.project/active/exec-subset-profile/evidence/` | Probe logs; reconciliation; dc3, corpus and parity runs; rendered `matrix.md`; R3 proposal; re-estimate |

Every pytest test reads only package data and `tests/`.

## Probe harness

`scripts/subset_profile/probe.py run [--probe ID | --all] --agentic-rev REV`. All writes go to a fresh temp directory and to `tests/fixtures/subset_profile/probes/`. F1 ran this exact setup successfully.

1. **Isolated tree.** `git archive` exports codegen `b5663c07` into `$T/sysml-codegen` and agentic-mbse `<REV>` into `$T/agentic-mbse`. Each export is checked with `get-tar-commit-id`; tolerate SIGPIPE under `pipefail`, a gotcha F1 hit. The sibling layout makes `path = "../agentic-mbse"` resolve inside `$T`.
2. **Environment.** `uv sync --frozen` against codegen's `uv.lock`. `SYSIDE_LICENSE_KEY` comes from agentic-mbse `.env`; the record notes that a key was present, never its value.
3. **Identity.** `python -I` emits the package versions, `syside.__version__`, the Python version, both packages' `__file__`, and the sha256 of `uv.lock`. The probe aborts if either package resolves outside `$T`.
4. **Run.** Each probe runs `python -m sysml_codegen generate --models … --output $T/probes/<id>/out` with a timeout. The harness captures the exit code, `ERROR:` lines, codes, error-line locations and the generated file list with hashes.
5. **Judge.** The certification test is invariant 2. The observation records `certifies: bool` with the failing check named. Omission and exclusion probes check the element's exact display path against the generated catalog and contract modules, with a numeric sibling as positive control. Item 2's semantic oracle replaces this later (m3).
6. **Same generator.** `--all` runs at `a718efec` and at Item 1's final revision. Codegen's v6 corpus and its pytest suite also run in each temp tree. Identical results show that Item 1's edits to shared modules did not change codegen (S6).

**Which agentic-mbse revision counts as "the pinned generator".** Codegen `b5663c07` with agentic-mbse at Item 1's final revision. `a718efec` is the comparison point. dc3 T-001 ran with `8b027bbc`; the evidence notes that difference and does not reconcile it.

**Halt direction (spec R2):**

- **Expected `refused`, generator admits.** The rule's intended refusal covers an admitted pair. **Stop that rule and take it to the owner (R2 track).** Nothing ships stricter.
- **Expected `admitted`, generator refuses.** The record's contexts are wrong. Record the observation, correct the contexts, and re-probe.
- **A variation probe that disagrees with its label** splits the context (B5). Its direction then follows the two cases above.

## Proposed spec amendment

**SA-1 [AGENT], proposed, not applied.** The spec criterion "Every refused shape has an admitted-context probe" gains one exception. A shape that the pinned generator refuses in every context the rule can compute may carry instead a `no_admitted_context` statement, with:

- the generator citation;
- refused probes covering each computable context.

Likely users: `calc-owned-assertion/asserted_constraint` under a calc-def owner (`elaborate.py:1625` via `owner_kind_unattachable`), and possibly `indexed-reference` if the calc-result probe refuses. The matrix lists every shape that uses it. This is recorded in the spec's change log as proposed; the owner or orchestrator accepts or rejects it.

## Non-Goals

- Codegen integration, code mapping, the screen-bypassing conformance corpus, mutation tests, per-site codes, `check`, snapshot and version integration; the module port; the end condition's implementation. All are Item 2.
- A wire codec for `SubsetFacts`.
- L6 wiring and severity (Item 3); positional binding (Item 4); rendered guidance (Item 5).
- Reproducing ES-011; String metadata policy; promoting ES-002, ES-008, ES-009 or the ES-010 refusal side.
- Correcting the two generator multiplicity behaviors (D14).
- Fixing `L6-LIBRARY-ALIAS-SOURCE`; relaxing any refusal; new language support.

## Implementation Notes

- **Spec premise refinements (surfaced, not silent):**
  - (a) ES-003's refused context is the **selected writer** in an instantiated scope. A calc usage selected in some scopes and overridden in others is `owner_instantiated`, with its selected-scope count. One overridden in every scope is `writer_overridden`. F1's `f1_calc_redefined_everywhere` is the reference case.
  - (b) A construct beneath a refused multiplicity is `beneath_refused_multiplicity`, and records as `unconfirmed`.
  - (c) ES-004 reads `usage.multiplicity`, as codegen does. In SysIDE 0.8.4 this is the same element as `declared_multiplicity`, and neither is inherited through `:>>` (F1 Surprise 1). The first revision's claim that they differ was wrong.
- **ES-001** splits asserted and non-asserted forms (`constraint_extraction._ASSERTED_FORMS`).
- **Expression-site contexts are per inventory role,** plus `calc_result_expression` (admitted, `manual_stub`) and `other_expression_site` (`unconfirmed`).
- **The ownership gate stays green** (see Component Overview).
- **The conditional operator spelling** is confirmed by a learning test on `es006_refused_conditional`.
- **Computed `executable_profile` reasons** (`:542`, `:597`, `:660`, `:711`, `:813`): one test drives each emission and asserts membership in `REASON_CODES`.

## Potential Risks

| Risk | Mitigation |
|---|---|
| Port drifts from codegen beyond the spike's cases | Parity seed in pytest; recorded parity run; end condition (ii) puts it in codegen CI |
| A context hides an admitted sub-case (B5) | Variation probes per instantiation-dependent refused pair; a failing variant splits the context |
| A dc3 category appears only as `unconfirmed` | Itemized with context in evidence; goes to the owner |
| `reference_use` refactor changes codegen | Byte-faithful; probes, v6 corpus and codegen pytest at both revisions |
| ~70 probes plus ~500 site rows inflate effort | Scripted single-construct probes; re-estimate at close, including Item 2's end-condition cost |

## Integration Strategy

Item 1 merges as new modules, an additive public read and one pure allowlist module. Nothing consumes the contract yet.

- **Item 2** pins `SUBSET_PROFILE_VERSION` and the records, maps reasons to `ElaborationCode`, implements the chosen end condition, and files the ADR 0012 amendment in sysml-codegen.
- **Item 3** maps verdicts and outcomes to L6 severity.
- **Item 5** renders from the records.

The R1 decision is filed as an agentic-mbse ADR after approval (Appendix B).

## Validation Approach

- **Pytest without SysIDE:**
  - record evidence gating (invariant 1);
  - closed vocabularies;
  - matrix ↔ records;
  - matrix schema and the fixed case list (S9);
  - the sites ↔ matrix join;
  - probe certification (invariants 2–3);
  - coupling;
  - version digest;
  - purity hygiene for `subset_profile`;
  - computed-reason closure.
- **Pytest with SysIDE:**
  - per-rule refused, admitted and variation fixtures;
  - occurrence parity against the stored oracle expectations;
  - roots (default equals the generator rule; widened gives `unconfirmed`; narrowed gives `incomplete`);
  - failure injection: extraction failure, enumeration failure, missing occurrence evidence, plus each `OccurrenceAbort`;
  - determinism.
- **Recorded runs:**
  - probes at both revisions, with the codegen v6 corpus and codegen pytest;
  - site reconciliation against 441/59, every change itemized;
  - occurrence parity on all corpora;
  - dc3 baseline and repaired, with `unconfirmed` and `unverified` both itemized;
  - the codegen corpus (manifest 14/23);
  - the `validate` diff;
  - `pytest`/`mypy`/`ruff`, with licensed and skipped checks named.

## Next-Stage Handoff

- **Fixed (after R1 approval):** layers; evidence-gated records; certification rule; halt direction; locations; D1–D14.
- **Open for the plan:** exact `ContextId` membership after the probes land; final probe count; TOML field names; whether the two `reference_use` accessors are needed.
- **De-risk first:** the probe-harness smoke (F5). F1 is done.
- **If the owner picks A′:** drop `occurrence_*` and the parity seed, and record instantiation-dependent contexts as `unconfirmed`. Everything else stands.

---
Next Step: verify the must-fixes (no fresh review needed per the review), then **owner gate R1** with F1's findings, then `/_my_plan`.

## Appendix A — Data model

Pure types. All are frozen dataclasses.

```python
class Outcome(StrEnum): REFUSED; ADMITTED; EXCLUDED; OMITTED; UNCONFIRMED
class Verdict(StrEnum): INCOMPLETE; REFUSED; UNCONFIRMED; CLEAR   # CLEAR: only admitted/excluded/omitted
class ContextId(StrEnum):  # closed; each member documented with its generator citation
    OWNER_INSTANTIATED; OWNER_PACKAGE; OWNER_UNINSTANTIATED; WRITER_OVERRIDDEN; OWNER_OTHER
    BINDING_VALUE; CALC_DEFINITION_FEATURE_VALUE; ATTRIBUTE_VALUE; CONSTRAINT_PREDICATE
    CALC_RESULT_EXPRESSION; OTHER_EXPRESSION_SITE; CALC_DEFINITION_OWNER; CALC_USAGE_OWNER
    EXPANDED_PART_USAGE; UNEXPANDED_PART_USAGE; ATTRIBUTE_USAGE
    BEYOND_GENERATOR_ROOTS; BENEATH_REFUSED_MULTIPLICITY; EVERYWHERE
```

```python
class ElementRef:  element_id: UUID; qualified_name: str; kind: str
class SafeLocation: file: str | None; line: int | None; qualified_name: str | None   # never raises
class FactFailure:  fact_kind: FactKind; subject: SafeLocation | None
                    cause: SemanticEvidenceCode | ScopeCause | OccurrenceAbort; detail: str
class ScopeCause(StrEnum): ENUMERATION_FAILED; ROOTS_UNAVAILABLE; ADAPTER_ERROR
class OccurrenceAbort(StrEnum): SPECIALIZATION_CYCLE; RECURSIVE_CONTAINMENT; INCOMPARABLE_TYPINGS
    REPEATED_NATIVE_DECLARATION; DUPLICATE_OCCURRENCE_IDENTITY; REDEFINITION_ROOT_FAMILY; WRITER_AMBIGUOUS
class FactKind(StrEnum): OCCURRENCE; BINDING_SOURCE; EXPRESSION_SITE; ASSERTION_OWNER; PART_MULTIPLICITY; STRING_VALUE; CONSTRAINT
```

```python
class MultiplicityReading: lower: int | None; upper: int | None; unbounded: bool; ordered: bool; nonunique: bool
    resolution: Literal["exact","range","unresolved","negative","absent"]
class OccurrenceNode: path: tuple[tuple[UUID, int | None], ...]; parent: tuple[...] | None; usage: ElementRef
    type_closure: frozenset[UUID]; root_id: UUID; reading: MultiplicityReading; count: int | None
    status: Literal["expanded","unexpandable","beneath_unexpandable"]
class Attachment: owner: ElementRef | None; owner_kind: OwnerKind; scopes_by_root: Mapping[UUID, int]
class WriterSelection: usage_id: UUID; selected_scopes_by_root: Mapping[UUID, int]; overridden_scopes: int
class OccurrenceStructure: generator_root_ids: frozenset[UUID]; selected_root_ids: frozenset[UUID]
    nodes: tuple[OccurrenceNode, ...]; attachments: Mapping[UUID, Attachment]; writers: Mapping[UUID, WriterSelection]
```

```python
ReferenceOutcome = Exact(use_count: int, indexed: bool) | ReferenceFailed(code: SemanticEvidenceCode)
InvocationOutcome = Walked(uses: tuple[InvocationUse, ...]) | InvocationFailed(code: SemanticEvidenceCode)
class SiteInspection: references: ReferenceOutcome; invocations: InvocationOutcome
    conditionals: tuple[SafeLocation, ...]          # recognized `if` nodes, found by the metatype walk
class ExpressionSiteFact: feature: ElementRef; role: SiteRole; location: SafeLocation; inspection: SiteInspection
# ES-005 is unverified iff invocations failed. ES-006 is refused-eligible iff a conditional is present
# and references failed with RESOLVED_TARGET_MISSING; any other failure leaves ES-006/indexed unverified.
```

```python
class BindingSourceFact: consumer: ElementRef; formal: ElementRef; location: SafeLocation; authored: str
    kind: Literal["literal","single_reference","self_binding","indexed","other_expression"]
class AssertionOwnerFact: constraint: ElementRef; form: str; owner_kind: OwnerKind
class PartMultiplicityFact: usage: ElementRef; reading: MultiplicityReading; composite: bool
class StringValueFact: feature: ElementRef; spelling: Literal["attribute_declaration","redefinition_shorthand"]
class SubsetFacts: occurrence: OccurrenceStructure | None; bindings; sites; assertions; multiplicities; strings
    constraints: IdentifiedConstraintFacts | None; enumerated: frozenset[FactKind]; failures: tuple[FactFailure, ...]
```

```python
EvidenceRef = ProbeRef(probe_id: str) | CorpusRef(fixture: str)       # CorpusRef only for ADMITTED
class Admission: outcome: Outcome; evidence: tuple[EvidenceRef, ...]; qualification: Literal["none","manual_stub"]
class ShapeRecord: shape_id; reason_id; expected_code: GeneratorEvidence | None   # evidence field
    admissions: Mapping[ContextId, Admission]; no_admitted_context: str | None      # SA-1
class RuleRecord: rule_id; title; matrix_rows; fact_requirements: frozenset[FactKind]; shapes: tuple[ShapeRecord, ...]
    remedy; semantic_limits; example_probe; doc_anchor; evidence_status: EvidenceStatus
    generator_evidence: tuple[GeneratorEvidence, ...]; verified_against: GeneratorIdentity
class GeneratorEvidence: code: str; site: str          # e.g. ("SI_SELF_BINDING", "elaborate.py:2187-2196")
class EvidenceStatus(StrEnum): PROBE_OBSERVED; PARTIAL; CODE_READ_PENDING_ITEM_2   # align record's wording
```

```python
class SubsetFinding: rule_id; shape_id; context_id: ContextId; outcome: Outcome; reason: str
    detail_reasons: tuple[str, ...]; subject: ElementRef; location: SafeLocation
    occurrence_count: int | None; via_roots: tuple[str, ...]; evidence: tuple[EvidenceRef, ...]
class UnverifiedCheck: rule_id; context_id: ContextId | None; subject: SafeLocation | None
    cause: SemanticEvidenceCode | ScopeCause | OccurrenceAbort; detail: str
class SubsetProfileResult: subset_profile_version: str; executable_profile_version: str
    scope: ScopeReport; verdict: Verdict; findings; unverified; counts   # counts: declarations vs occurrences
# verdict: INCOMPLETE if any unverified, narrowed roots or unenumerated required kind; else REFUSED if any
# refused; else UNCONFIRMED if any unconfirmed; else CLEAR. CLEAR is the only verdict a consumer may call clean.
```

**Matrix row schema** (`matrix.toml`, S9). A test checks the closed fields and the fixed case list: ES-001…ES-012, SELF-BINDING, INDEXED-REFERENCE, DEEP-QUALIFIED-WIRING, the ten `PUSH-DOWN-*-PROFILE-*` rows and `L6-LIBRARY-ALIAS-SOURCE`, plus G1/G2 (D14).

```toml
[[row]]
id = "ES-003"                  # stable row ID
class = "shared_rule"          # shared_rule | codegen_check | advisory_omission_policy | tracked_gap | internal_invariant
rule = "binding-source"        # required iff class = shared_rule
contexts = ["owner_instantiated", "owner_package"]; outcome = "refused"; evidence_status = "probe_observed"
owner = "agentic-mbse Item 1"; coverage_limitation = ""   # required non-empty unless implemented in Item 1
sites = ["sysml_codegen/elaboration/elaborate.py::_binding_evidence::…"]; no_raise_site = false
dc3 = ["B2"]; upstream = []; l2_relation = ""   # SELF-BINDING row states the L2_SELF_NAMED_BINDING relation here
```

Rule IDs and shapes (rule ← matrix rows):

| Rule ID | Matrix rows | Shapes (reason ID) |
|---|---|---|
| `calc-owned-assertion` | ES-001 | `asserted_constraint`, `non_asserted_constraint` (`constraint_owned_by_calc_definition`, `constraint_owned_by_calc_usage`) |
| `binding-source` | ES-003, ES-012, SELF-BINDING | `expression_source` (`binding_source_expression`), `self_reference_source` (`binding_source_self_reference`) |
| `indexed-reference` | INDEXED-REFERENCE | `indexed_reference` (`indexed_reference_unsupported`) |
| `part-multiplicity` | ES-004 | `ordered`, `nonunique`, `range`, `unresolved_bound`, `negative_bound` (`part_multiplicity_*`) |
| `invocation-callable` | ES-005 | `unsupported_callable` (`invocation_callable_unsupported`) |
| `conditional-expression` | ES-006 | `conditional_unresolved_branch` (`conditional_expression_unsupported`) |
| `constraint-predicate` | ES-007 | `blocked_predicate`, `non_numerical_predicate` (`constraint_predicate_blocked`, `…_non_numerical`) |
| `string-value-omission` | ES-010 (omission) | `string_value` (`string_value_not_generated`), both spellings |

## Appendix B — ADR drafts (R1)

### B.1 agentic-mbse ADR (filed after owner approval)

Command: `.project/scripts/adr.sh new subset-profile-capability-ownership`. Provenance `[AGENT] (ratified by owner, <date>)`. Seams `[agentic-mbse, sysml-codegen, l6, guidance]`.

**Decision.** agentic-mbse owns the declared executable-subset contract: a published, versioned, evidence-backed description of the generator's refusals, and the pure evaluator that applies it (`sysml/subset_profile.py`, `SUBSET_PROFILE_VERSION`, neutral reason IDs, packaged rule records). It also owns the neutral facts the contract needs, including a summary of the occurrence structure the generator instantiates. sysml-codegen owns the behavior the contract describes, the diagnostic-code mapping, output facts and rendering. L6 and guidance consume the contract and own presentation.

**Why.** L6 and guidance must consume the contract without importing codegen. Separate implementations of a decision drift (the dc3 B1–B6 miss). ADR 0007 places model facts in agentic-mbse, and occurrence reach is a model fact. A pure decision layer keeps capability refusals distinct from evidence failures and versions them separately.

**Invariants established.**

1. The contract reports any outcome other than `unconfirmed` only with retained evidence: a probe of the pinned generator whose observed code matches, or a corpus citation for `admitted`.
2. Pairs without evidence report `unconfirmed`; missing facts report `unverified`; only verdict `CLEAR` is clean.
3. No agentic-mbse module imports sysml-codegen; `SI_*` codes appear only as evidence.
4. The invocation allowlist is the one capability decision reached from the fact layer; changing it changes `SUBSET_PROFILE_VERSION`.
5. Ground truth is the pinned generator until EXEC-SUBSET-CONTRACT Item 2. After Item 2 it is Item 2's independent corpus: elaboration with the contract screen bypassed.
6. The occurrence summary and codegen's occurrence index are held together by the end condition the owner chose: <(i) codegen swaps onto a shared module and deletes its copy | (ii) a permanent parity test in codegen CI>.

**Rejected alternatives.** Codegen-owned policy: L6 and guidance could not consume it without a reverse dependency. Decisions in the fact layer: they would be indistinguishable from evidence failures and context-blind. Per-consumer implementations: decisions drift. No port with `unconfirmed` instantiation contexts (A′): leaves dc3 B2, B3 and B8 undecided until Item 2.

### B.2 sysml-codegen ADR 0012 amendment (filed in sysml-codegen by Item 2, or earlier at owner direction)

Command, run in sysml-codegen: `.project/scripts/adr.sh new occurrence-summary-shared-with-agentic` then `adr.sh amend 0012 <new-id>`. Provenance `[AGENT] (ratified by owner, <date>)`. Seams `[elaboration, agentic-mbse]`.

**Decision.** ADR 0012's invariant "Raw parser reads for declaration discrimination, slot construction, and multiplicity retain their narrow codegen ownership" is amended. These reads now have two reviewed owners. Codegen keeps them for elaboration. agentic-mbse's `occurrence_extraction` performs the same reads for the shared executable-subset contract, through its own reviewed accessors. The two are held together by <end condition (i) or (ii)>. Every other 0012 invariant is unchanged.

**Why.** L6 and the shared contract need instantiation facts, and agentic-mbse cannot import codegen. Spike F1 (agentic-mbse `exec-subset-profile`, 2026-10-15) showed a summary port matching codegen `b5663c07` on 72 of 72 cases. 0012's concern, that a weaker alternate read could drop evidence, is answered by parity on exact evidence (ADR 0004), not by exclusive location.

**Rejected alternatives.** Keeping exclusive codegen ownership (option A′): it leaves the contract unable to decide instantiation-dependent refusals until a single move.

## Appendix C — Probe list (initial)

`R` = expected refused, `A` = expected admitted, `V` = variation probe (B5), `⇐` = the prototype fixture it supersedes. Every probe declares its construct's line range, and every `A` declares a positive-control sibling.

- **calc-owned-assertion:**
  - R calc-def asserted ⇐ `es001_refused_calc_def_assert`; R calc-usage asserted ⇐ `es001_refused_calc_usage_assert`; R calc-usage non-asserted (owner-kind raise at `elaborate.py:813-820`).
  - A calc-def non-asserted; A part-owned asserted ⇐ `es001_admitted_part_assert`.
- **binding-source:**
  - R `(a, b)` instantiated ⇐ `es003_refused_ordered_nonunique`; R `rate * fuel_code` ⇐ `unmapped_expression_calc_arg`; R `(a, b)` package-owned; R self-binding; R constraint input bound to an expression.
  - A uninstantiated owner; A writer overridden ⇐ F1 `f1_calc_redefined_everywhere`; A ordered nonunique input bound to a scalar ⇐ `es003_neighbor_ordered_param_scalar_arg`; A exact `[1]` ordered input ⇐ `es003_neighbor_exact_ordered_param`; A plain reference actual; A unit-annotated literal.
  - V, for `(a, b)` and for self-binding: part-usage owner; subtype occurrence; inherited calc usage; owner reached through `[2]`; two nesting levels; a usage selected in one scope and overridden in another.
- **indexed-reference:**
  - R binding value; R attribute value; R constraint predicate.
  - A indexed reference in a calc def's bare result expression. If the run refuses it, the shape uses SA-1.
- **part-multiplicity:**
  - R range ⇐ `es004_refused_range_parts`; R unbounded ⇐ `es004_refused_unbounded_parts`; R ordered part; R nonunique part; R referenced bound without a literal writer.
  - A uninstantiated template ⇐ `es004_admitted_uninstantiated_template`; A exact redefinition ⇐ `es004_admitted_exact_redefinition`; A ordered or ranged attribute usage; A non-composite part usage; A redefinition that drops bounds (records the G1 behavior).
  - V, for range: nested under a root at depth two; under `[2]`; via a subtype's inherited part.
- **invocation-callable:**
  - R `product` binding ⇐ `es005_refused_product`; R `size` ⇐ `es005_refused_size`; R `max` attribute value; R invocation in `return r : Real = …`; R invocation in a constraint predicate.
  - A `max(a, b)` as a calc def's bare result expression (stub); A explicit multiply ⇐ `es005_admitted_explicit_multiply`.
- **conditional-expression:**
  - R binding or calc-definition feature value ⇐ `es006_refused_conditional`; R constraint predicate.
  - A calc def bare result expression; A arithmetic min ⇐ `es006_admitted_arithmetic_min`.
- **constraint-predicate:**
  - R BLOCK instantiated ⇐ `es007_refused_boolean_mixed`; R BLOCK package-owned.
  - A BLOCK uninstantiated; A numeric `and` ⇐ `es007_admitted_numeric_and`; excluded NON_NUMERICAL (exit 0, predicate absent from the generated contract, numeric sibling present).
  - V, for BLOCK: part-usage owner; subtype occurrence; owner under `[2]`.
- **string-value-omission:**
  - Omitted, both spellings ⇐ `es010_omitted_string_value` (catalog and contract identity check, numeric sibling as control).
  - A numeric value ⇐ `es010_admitted_numeric_value`.
- **Candidates, reproduction only:** ES-002, ES-008, ES-009, and the ES-010 refusal side ⇐ `es010_refused_string_calc_input`.

## Appendix D — De-risk flags

- **F1. Occurrence-port parity. Done.** 72 of 72 cases match; the summary port is 416 lines. Results are folded into R1, B2, B4, D13, D14 and the parity seed. Not measured: the module port (only relevant if the owner picks end condition (i)), and D7's caller roots (a plan item).
- **F2. Multiplicity facts before elaboration. Closed by F1.** `multiplicity` and `declared_multiplicity` are the same element, neither inherits through `:>>`, and the port reads what codegen reads.
- **F3. Binding-shape fact equivalence. No spike.** Equivalence holds by shared code. The residual check is which members codegen treats as inputs (`elaborate.py:1879-1950`, `binding_source.py:183-207`); the probes prove it.
- **F4. A calc def bare result expression is not an inventory site. No spike.** It is code-read, and the minimum probe set observes it.
- **F5. Probe environment. Smoke test as the first plan step.** F1 already ran the same `git archive`, `uv sync --frozen` and license setup successfully. What remains is the generate-CLI path and the code-match judging.
