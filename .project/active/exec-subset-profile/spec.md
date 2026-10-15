# Spec: Executable-subset capability inventory and shared profile (EXEC-SUBSET-CONTRACT Item 1)

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-10-15
**Complexity:** HIGH
**Branch:** `exec-subset-profile`

---

## Problem

Three consumers each hold their own picture of which SysML shapes the generator can execute. sysml-codegen refuses shapes at elaboration, projection and generation preparation, one at a time, and silently drops some (String metadata). L6 checks only part of that surface: on the dc3 baseline (`808464d`) it reports B7 and B8 and misses B1–B6, then passes the repaired tree. Shipped guidance teaches native-valid examples with no execution qualification. Nothing ties these together, so they drift, and a modeler finds the generator's limits one failed run at a time.

Item 1 builds the single declared contract the three consumers will share. It has three parts:

- **An inventory** of every public refusal and known silent loss on the pinned generator surface, each assigned an owner and a class.
- **Rule records** for the structural capability rules that belong in the shared contract.
- **A shared evaluator and its facts** in agentic-mbse that apply those rules to a user model.

It does not wire any consumer to the contract. Codegen integration is Item 2, L6 severity and execution-target settings are Item 3, positional binding is Item 4, and rendered guidance is Item 5.

The prototype (`.project/concepts/convince-me-exec-subset/`) showed this is feasible: a screen using only agentic-mbse and SysIDE facts found every B1–B8 category on the baseline in one run, and a 22-fixture differential against codegen agreed on 21 and caught one real gap (ES-012). Those are feasibility observations, not acceptance evidence. The prototype's ES-004 instantiation check is a heuristic, its omission oracle matches names in text, and its 500-site classification is an unreviewed draft.

The governing obligation, from the epic's Item 1 objective `[INHERITED: epic]`: define and implement the structural contract **without duplicating model interpretation and without broadening current refusals accidentally**.

## Success Criteria

Each criterion names the artifact or test that proves it. "Pinned" means sysml-codegen `b5663c07e987a892e27d21e68cec40d0656574ee`, dc3 `808464df…` (baseline) and `60b44d53…` (repaired), SysIDE 0.8.4, with the imported package versions recorded in the evidence.

**Inventory and site account**

- [ ] **Site account is total over the scanner's recognized forms.** A machine-readable site account has exactly one row per candidate site the scanner recognizes in sysml-codegen at `b5663c07` and in agentic-mbse at Item 1's final implementation revision (so sites Item 1 itself adds are counted). Each row carries a stable site ID, a D2 disposition (`in scope` / `handled elsewhere` / `explicit follow-up`), an evidence pointer and an owner. A recorded reconciliation run rescans both trees and reports zero unaccounted sites and zero rows without a site.
- [ ] **Count reconciliation is explicit.** The evidence states the final codegen and agentic-mbse site counts against the recorded 441 / 59, and lists every added or removed site by ID with its cause. A count difference without an itemized cause fails the criterion.
- [ ] **Blind spots are listed, not implied.** The account names the scanner revision and the forms it recognizes, and lists its known blind spots. The list includes at least: silent omissions (no raise site exists), computed codes beyond the resolver, unrecognized exception classes or helpers, and unproven public reachability.
- [ ] **The five computed reason sites are closed.** A pytest test exercises every reason the five computed sites in `executable_profile.py` (prototype citation `:542, :597, :660, :711, :813`, re-located at the implementation revision) can emit and asserts each is a member of `REASON_CODES`. No enum conversion is introduced for this purpose.

**Capability/refusal matrix**

- [ ] **Every named case has a matrix row.** The matrix has a row for each of: ES-001 to ES-012, all ten `PUSH-DOWN-*-PROFILE-*` backlog rows, indexed references, deep-qualified wiring, and `L6-LIBRARY-ALIAS-SOURCE`. Every dc3 T-001 item B1–B9 and every dc3 upstream finding U1–U7 is cross-referenced from exactly the rows it maps to, per the mapping below. A reviewer can check this against a fixed list in the evidence.
  - dc3 sources: `work/orchestration/goals/study-ready-baseline/evidence/T-001-blocker-inventory.md` (B1–B9, models at `808464d`) and `.project/active/toolkit-upstream-findings.md` (U1–U7, observed 2026-10-13 at codegen `b5663c07`).
  - The two lists overlap; they are not 16 separate refusals. U1 = B1 (ES-001). U3 = B7 (ES-010). U4 = B4, B5 and B6 plus `min`/`max` (ES-005, ES-006). U7 = B9 (ES-011).
  - Three upstream findings have no B number: U2 nested named subsets (ES-008), U5 a constraint binding a calc usage's input (ES-002), U6 composition by usage subsetting (ES-009). Their evidence is dc3 session-scratch prototypes (`proto4nest`, `proto3`, `conv`); only U2 has a committed reproduction (`T-002-prototype/models.diff` P8).
  - U7/B9 is not a confirmed refusal. A T-001 worker reported it; the coordinator did not reproduce it, and dc3 already uses the `out attribute` form. Its row records `unconfirmed`, never `refused`.
  - B8 is two distinct profile outcomes, 4 `NON_NUMERICAL` and 4 `MALFORMED_NUMERICAL` (`block_non_numerical_containment`). The B8 row keeps them apart.
  - B2's T-001 attribution is wrong and the row must not repeat it. T-001 says the `Real[0..*] ordered nonunique` calc input is refused by codegen's multiplicity expansion (`elaboration/occurrence.py` `_multiplicity_indices`). That function expands usages into occurrences; the retained neighbor `es003_neighbor_ordered_param_scalar_arg` declares exactly that input, binds a scalar, and generates. The refused element is the sequence actual (ES-003).
  - U8 (positional binding) is not in U1–U7 and belongs to Item 4. The matrix points to Item 4 and does not classify it.
- [ ] **Every row is classified and owned.** Each row names exactly one class: shared rule, codegen-specific check, advisory/omission policy, separately tracked gap, or evidenced internal invariant. Each row also states its context, outcome, evidence status and owner. Every row that is not implemented in Item 1 states its owner and the coverage limitation it leaves.
- [ ] **Matrix and records agree.** A pytest test asserts that every shared-rule matrix row names an existing rule record, and every rule record appears in the matrix. The test keeps passing after the item folder is archived.

**Rule records and evaluator**

- [ ] **Records are complete.** A pytest test asserts every rule record carries all fields required below (ID, applicability/context, outcome, fact requirements, remedy with semantic limits, working-example fixture, documentation anchor, evidence status), and that every reason ID it can emit is in a closed, runtime-validated vocabulary.
- [ ] **Each implemented rule has refused and admitted fixtures in agentic-mbse.** For each rule the evaluator implements, pytest fixtures include at least one refused case and at least one admitted near-neighbor, and the evaluator's outcome on each is asserted. The prototype's admitted neighbors are carried over and stay admitted: part-owned assert (ES-001); ordered nonunique input bound to a scalar and exact `[1]` ordered input (ES-003); uninstantiated template and exact redefinition (ES-004); explicit fixed-arity multiply (ES-005); arithmetic `min` identity (ES-006); numeric `and` (ES-007); numeric value (ES-010); a plain reference actual (ES-012).
- [ ] **No refused shape lacks generator evidence.** Every shape an implemented rule reports as `refused` cites evidence that the pinned generator refuses it, with the generator code. Acceptable evidence is an observed run (prototype or an Item 1 probe at `b5663c07`) or a code-path citation at `b5663c07` (file and line of the deciding branch). A shape backed only by a code-path citation carries that as its evidence status. A refused shape with neither fails review.
- [ ] **Baseline run accounts for B1–B8.** One evaluator run over the dc3 baseline tree reports every confirmed category B1–B8 with locations and rule IDs. The evidence records declaration counts and occurrence counts separately, and states the deduplication applied.
- [ ] **Repaired run refuses nothing.** One evaluator run over the dc3 repaired tree, which generates at `b5663c07`, reports zero `refused` findings. Any `unverified` result is itemized with its cause, and fails the criterion unless the owner accepts that recorded limit. Omissions are reported and counted (the prototype saw 30 String omissions).
- [ ] **The generator's accepted corpus stays admitted.** The corpus is sysml-codegen's owner-accepted batch at `b5663c07`, `tests/fixtures/v6_recapture_batch/batch.json`: 37 fixtures, each with one record. At `b5663c07` the manifest holds 14 snapshot records (the fixture elaborates and projects; `tests/fixtures/<name>/instance_graph_snapshot.json`) and 23 typed refusal records with exact code multisets. The batch README says 15 and 22; the manifest governs, and the evidence states the counts it read. A recorded read-only evaluator run over all 37 must show:
  - zero `refused` findings on the 14 snapshot fixtures;
  - on the 23 refusal fixtures, every `refused` finding names a rule whose generator code appears in that fixture's recorded multiset.
  - Any other `refused` finding is an R2 stop for the owner. The snapshot fixtures prove admission through elaboration and projection, not full generation; the evidence says so. This run also supplies generator evidence for admitted neighbors that lack it, such as ES-012's plain reference actual.
- [ ] **Failure cannot look clean.** Pytest tests inject (a) a fact-extraction failure for one rule, (b) an enumeration failure for the model scope, and (c) missing occurrence evidence for an occurrence-dependent rule. In each case the result carries a structured `unverified` entry with rule ID, context, safe location and cause; unrelated rules still report their findings; and the overall assessment is not complete/clean.
- [ ] **Output is deterministic.** A pytest test evaluates the same model twice and with permuted document order and asserts identical, ordered output.
- [ ] **No consumer coupling.** A pytest test asserts no module in `agentic_mbse` imports `sysml_codegen`, and the shared reason vocabulary contains no `ElaborationCode` member names or other consumer-specific identifiers.
- [ ] **Consumer output is unchanged.** `agentic-mbse validate` output on the existing test fixtures and both dc3 trees is unchanged by Item 1 (diffed before and after).

**Decisions and close-out**

- [ ] **R1 decision is recorded and approved.** The design records the capability-policy ownership decision and the fact/decision/consumer boundary, with the owner's approval and date, before planning starts. It locates ADR 0007 or records that it is absent.
- [ ] **R3 proposal is recorded.** A disposition table proposes, for each section of GENERATOR-SUBSET-PATTERNS and each remaining capability gap, its destination item or follow-up. It is marked proposed until the owner approves.
- [ ] **Re-estimate is recorded.** Item 1's close-out records re-estimated effort for Items 1 and 2, as the epic requires after the inventory.
- [ ] **Repository checks pass.** `uv run pytest tests/`, `uv run mypy src/` and `uv run ruff check src/ tests/` pass. Evidence states which checks needed the SysIDE license and which were skipped.

## Known Requirements

### Ratified decisions

These bind Item 1. They are agent recommendations the owner approved, so they are challenged by re-deriving against their recorded reasoning, not relitigated casually.

- **[INFERRED]** (ratified by owner 2026-10-15; epic § Owner decisions D2; the orchestration brief records D1–D3 as owner decisions) D2: inspect and classify all 500 candidate sites in the recorded inventory (441 codegen, 59 agentic-mbse), reconciling additions and removals at the implementation revision. Each site is in scope, already handled elsewhere, or an explicit follow-up, with evidence and ownership. Implement only the scoped shared capability rules; this does not require 500 rules or recoding every exception.
- **[INFERRED]** (ratified by owner 2026-10-15, `briefs/align.md`) The full D2 site account is built in Item 1 at the pinned revision, because rule boundaries depend on it. Per-site stable codes and mutation tests remain Item 2.
- **[INFERRED]** (ratified by owner 2026-10-15, `briefs/align.md`) Item 1 does not claim generator-verified rules. Each rule record carries an evidence status such as `prototype-observed` or `pending Item 2 independent fixture`. Item 1 tests verify the agentic-mbse evaluator and facts against agentic-mbse fixtures.
- **[INFERRED]** (ratified by owner 2026-10-15, `briefs/align.md`) "Inventory complete relative to the pinned generator surface" means complete relative to the scanner's recognized forms plus an explicit list of known blind spots.

### Boundaries

- **[HARD]** agentic-mbse never imports sysml-codegen or its types. sysml-codegen already depends on agentic-mbse, so the reverse import would make a cycle. sysml-codegen's ADR 0007 records the one-way dependency as an active invariant (`~/src/sysml-codegen/.project/adr/0007-agentic-mbse-owns-neutral-facts-codegen-owns-rendering.md`).
- **[INHERITED: epic, Design principle 1 and Item 1 scope 2]** The shared decision vocabulary uses neutral reason IDs. It does not use `ElaborationCode` or any consumer-specific identifier. Codegen keeps its own diagnostic mapping, which may be one-to-many.
- **[INHERITED: epic, Item 1 Out of Scope; `briefs/align.md` R2]** No shared rule may report `refused` for a shape the pinned generator currently admits without explicit owner approval. Where a rule's draft boundary would do so, that rule halts for the owner; it does not ship stricter.
- **[INHERITED: epic, Item 1 Out of Scope]** Item 1 implements no new language support.
- **[INFERRED]** Item 1 does not change the output of `agentic-mbse validate` or any shipped asset. Consumers adopt the contract in Items 2, 3 and 5. Reason: the epic assigns L6 integration to Item 3, and an unannounced L6 change would be exactly the uncoordinated drift this epic exists to stop.

### Inventory content

- **[INHERITED: epic, Item 1 scope 1]** The inventory covers public refusals and known silent losses across elaboration, projection and generation preparation, including indexed references, deep-qualified wiring and all ten existing `PUSH-DOWN-*-PROFILE-*` backlog rows. Each case is assigned to a shared rule, a codegen-specific check, an advisory/omission policy, a separately tracked gap, or an evidenced internal invariant.
- **[INHERITED: epic, Item 1 scope 1]** `L6-LIBRARY-ALIAS-SOURCE` is reconciled explicitly. The matrix states whether it is affected, without implying this epic fixes it.
- **[INHERITED: epic, Design principle 4]** A valid model reaching a public refusal is never classified as an internal invariant. An internal-invariant classification needs evidence that well-formed supported input cannot reach the site.
- **[INHERITED: epic, Item 1 scope 3]** The computed diagnostic sites are resolved or explicitly mapped to the existing closed vocabulary, and their possible emissions are tested. Variable arguments alone do not prove an open vocabulary.
- **[INFERRED]** The site account records, where known, each site's semantic role (public capability, malformed input, environment, snapshot compatibility/integrity, relay/plumbing, internal invariant). A role left unknown is marked unknown rather than guessed. Reason: Item 2 must classify by these roles, and recording what Item 1 learns saves re-derivation; marking unknowns keeps the draft honest.
- **[INFERRED]** The site-account reconciliation is a recorded script run against the pinned sibling trees, not a pytest test. Reason: agentic-mbse's test suite cannot assume a sysml-codegen checkout. Item 2 owns the guard that runs in codegen CI.

### Rule records

- **[INHERITED: epic, Item 1 scope 3]** Each rule record has: a stable ID; exact applicability and context; outcome; fact requirements; remedy with its semantic limits; working-example fixture; documentation anchor; evidence status.
- **[INHERITED: epic, Item 1 scope 3]** Outcomes distinguish `refused`, `admitted`, `excluded`, `omitted` and `unconfirmed`. Missing evidence produces an `unverified` check result, which is a separate thing from any outcome.
- **[INFERRED]** `unconfirmed` is the outcome for a shape a rule recognizes but whose generator behavior has neither an observation nor a code-path citation yet (for example plural actuals other than a literal sequence, if design cannot place them in the binding-source classification). Reason: reporting it `refused` would risk R2, and reporting it `admitted` would be a silent miss.
- **[INHERITED: epic, Item 1 scope 3 and Design principle 2]** `executable_profile.py` stays the authority for constraint-predicate eligibility, including the BLOCK, NON_NUMERICAL and UNASSESSED distinctions. Its 27-member `REASON_CODES` and the membership check in `EligibilityDiagnostic.__post_init__` are reused, not duplicated. New structural decisions reference it where it applies.
- **[INFERRED]** Any new reason IDs live in a closed vocabulary that is enumerable without running the evaluator and validated at construction, matching the `REASON_CODES` pattern. Reason: the epic's inventory and Item 2's mapping both depend on enumerating every possible reason.
- **[INFERRED]** The rule records are machine-readable data inside the agentic-mbse package, readable without SysIDE. Reason: Item 2 pins them and Item 5 renders `docs/patterns/generator-subset.md` from them, so they cannot live only in a `.project` document.
- **[INFERRED]** The capability decisions carry their own version identifier, separate from any fact schema version. Reason: this is the existing split between `PROFILE_SEMANTIC_VERSION` and `CONSTRAINT_FACTS_SCHEMA_VERSION`, and Item 2 must pin the decision version for snapshot authority.

### Which candidates become evaluator rules

The rule for promotion, **[INFERRED]**: Item 1 implements a candidate family as an evaluator rule when two things hold. First, its refused shape has generator evidence at `b5663c07`: an observed refusal, or a code-path citation of the deciding branch. Second, its required facts can be extracted from shared agentic-mbse facts without a heuristic. Otherwise it stays a candidate record. Reason: this is the strongest criterion that keeps R2 safe without generator conformance tests, which are Item 2's. A code-path citation counts because it reads the pinned generator's actual decision; it stays marked as code-read until Item 2 adds a fixture. The design may also promote a candidate by recording a new read-only probe.

Applied to today's evidence (prototype fixtures in `01-fixtures/`, codegen oracle in `01-codegen-oracle.log`, codegen source at `b5663c07`; codegen paths below are relative to `~/src/sysml-codegen/src/sysml_codegen/`):

| Family | Item 1 disposition | Refused scope from evidence | Admitted neighbors from evidence | Not established |
|---|---|---|---|---|
| ES-001 | Rule | Assert owned by a calc def (`elaboration/elaborate.py:815`) or a calc usage (`:1625`, owner metatype unsupported), both `SI_CONSTRAINT_UNATTACHED`; observed | Part-owned assert | Effective attachment through inheritance |
| ES-002 | Candidate | dc3 U5 observed `SI_OCCURRENCE_MISSING` "cannot anchor containment" (`elaboration/occurrence.py:181`) in session scratch; no retained fixture | Binding a calc output (dc3 U5, unretained) | Whole boundary; the code has at least 11 other `SI_OCCURRENCE_MISSING` sites, so the code alone does not fix the shape |
| ES-003 | Rule, one decision with ES-012 | Any calc or constraint input binding whose source is neither a literal nor a single reference becomes an expression source and is refused at readiness (`elaboration/elaborate.py:2130-2161`, `:2195`, `SI_EXPRESSION_SOURCE_UNSUPPORTED`). Observed for the literal sequence `(a, b)` | `Real[0..*] ordered nonunique` input bound to a scalar; exact `[1]` ordered input | Plural actuals that are single references (T-001 cites `SI_OCCURRENCE_AMBIGUOUS`, `elaboration/occurrence.py:576-620`) |
| ES-004 | Rule, occurrence-aware | Occurrence expansion (`elaboration/occurrence.py:812-899`) refuses ordered (`:827`) and nonunique (`:835`) multiplicity and ranges (`:894`) as `SI_MULTIPLICITY_UNSUPPORTED`, and unresolved upper or lower bounds (`:859`, `:886`) as `SI_MULTIPLICITY_UNRESOLVED`. Range and unbounded observed; ordered and nonunique code-read | Uninstantiated template; exact redefinition | Which usage kinds reach expansion; see requirement below |
| ES-005 | Rule, reusing the shared admission | Every ordinary invocation except `NumericalFunctions::sum`. agentic-mbse already decides this (`reference_use.py:395-428`, `EXPRESSION_KIND_UNSUPPORTED`), and codegen maps it to `SI_EXPRESSION_SOURCE_UNSUPPORTED` (`orchestration/elaborated_pipeline.py:389-396`). `product` and `size` observed; `min`/`max` code-read | Explicit fixed-arity multiply | Which expression contexts run that inspection (the epic's "invocation context"); sum operands and wrappers stay with the PUSH-DOWN aggregation rows |
| ES-006 | Rule, narrowed | `if … ? … else` conditional; observed as `SI_EVIDENCE_INCOMPLETE` "resolved reference has no exact target". See the requirement below on why this code is an evidence failure | Arithmetic `min` identity | Other conditional forms |
| ES-007 | Mapped to `executable_profile`, no new detector | BLOCK decisions, surfaced by codegen as `SI_CONSTRAINT_BLOCKED` (`elaboration/elaborate.py:1354`) | Numeric `and` | — |
| ES-008 | Candidate | dc3 U2 observed `SI_REDEFINITION_INVALID` "incomparable value writers" (`elaboration/elaborate.py:947`); committed reproduction only as dc3 `T-002-prototype/models.diff` P8 | One level of named subsetting (dc3 U2) | Whole boundary; at least 7 other `SI_REDEFINITION_INVALID` sites |
| ES-009 | Candidate | dc3 U6 observed `SI_OCCURRENCE_MISSING` on `dc_site.facility.<attr>` in an intermediate scratch run; no retained fixture | None retained | Whole boundary |
| ES-010 | Rule | A non-numeric default reaching a generated entry-point input is refused at projection (`elaboration/project.py:201-218`, `_float_default`, `SI_RENDERING_COLLISION`; Booleans are coerced, not refused). Observed via a calc input bound to a String attribute with a String value. A String value not reaching an entry point is `omitted`, in both spellings | Numeric value | Final String metadata policy (Item 2) |
| ES-011 | Candidate, `unconfirmed` | — (dc3 U7/B9, a worker report the coordinator did not reproduce) | — | Reproduce or retire in Item 2 |
| ES-012 | Rule, one decision with ES-003 | Same readiness decision as ES-003; observed for `in v = rate * fuel_code` | Plain reference actual (agentic-mbse fixture; generator evidence from the corpus run) | — |

- **[INFERRED]** ES-003 and ES-012 share one generator decision: the binding-source classification at `elaboration/elaborate.py:2130-2161`. The shared contract reproduces that one boundary from one fact (binding source kind: literal, single reference, indexed, other expression). It does not keep two detectors that could disagree. Whether that is one rule record or two records over one fact is a design choice.
- **[INFERRED]** ES-005 reuses `reference_use._require_supported_invocation` (`reference_use.py:395`) for callable identity. It does not re-detect callables. Reason: that function already is the generator's callable boundary, so a second detector is the duplicated interpretation the epic forbids.
- **[INFERRED]** The generator reports ES-006 with its generic evidence-gap code. The conditional's branch reference has no exact target, so `inspect_reference_uses` raises `RESOLVED_TARGET_MISSING`. Codegen maps every evidence code it does not name to `SI_EVIDENCE_INCOMPLETE` (`orchestration/elaborated_pipeline.py:425`). Two consequences follow. ES-006 reports `refused` only on a positively recognized conditional shape; any other `RESOLVED_TARGET_MISSING` or `SI_EVIDENCE_INCOMPLETE` stays `unverified`. And the inventory does not classify `SI_EVIDENCE_INCOMPLETE` sites as capability refusals by code alone. Reason: otherwise a real evidence failure would surface as a construct refusal, which Item 1 scope 6 forbids.

- **[INHERITED: epic, Item 1 scope 4]** These families are candidates to refine with fixtures, not universal construct bans. ES-003 describes the actual binding shape and does not ban the parameter declaration.
- **[INHERITED: epic, Item 1 scope 4]** ES-007 keeps Boolean data/output capability, non-numerical exclusion and malformed predicates as distinct decisions. NON_NUMERICAL maps to `excluded`, not `refused`. UNASSESSED never maps to `admitted`.
- **[INHERITED: epic, Item 1 scope 5]** ES-004 uses effective reachable occurrences and their resolved bounds. A typing observed elsewhere, or an exact redefinition elsewhere, does not discharge another occurrence. The prototype's "typed anywhere" heuristic is not carried into production.
- **[INFERRED]** If the design finds that occurrence facts for ES-004 cannot be extracted from SysIDE before elaboration for some context, the rule reports `unverified` for that context and records the limit. It does not fall back to the heuristic and does not report clean. Reason: this is the epic's honesty principle applied to the one rule whose facts are least certain.

### Evaluation scope and result shape

- **[INHERITED: epic, Item 1 scope 5]** Evaluation covers the selected user-model scope, including calc bodies where the capability applies, and excludes the standard library. It distinguishes template from instantiated evidence and specifies declaration/occurrence identity, location fallback, stable ordering and diagnostic deduplication.
- **[INFERRED]** Occurrence-dependent rules evaluate against an explicit set of roots. The result states which roots were used. When no roots are known, those rules report `unverified` rather than guessing what is instantiated. Reason: the epic forbids the instantiation heuristic, and an unstated root choice would make "instantiated" mean different things to L6 and codegen.
- **[INHERITED: epic, Item 1 scope 6 and Design principle 5]** A detector failure produces a structured `unverified` result carrying the rule, the context and a safe location. It never produces a false unsupported-construct finding. An enumeration or extraction failure never produces an empty clean result. Checks whose facts remain available still run.
- **[INFERRED]** `unverified` results carry the closed `SemanticEvidenceCode` cause (`errors.py:25`) when the failure came from shared evidence extraction. Reason: that vocabulary already exists for exactly this, and a second one would duplicate it.
- **[INHERITED: epic, Design principle 5]** The evaluator reports missing prerequisites and the dependent checks left unverified. It does not invent downstream findings or claim exhaustive results when evidence is missing.

### No duplicated interpretation

- **[INHERITED: epic, Item 1 objective and scope 2; Risks row 1]** New decisions reuse the existing shared facts in `reference_use.py`, `hierarchy.py`, `aggregation.py`, `constraint_facts.py` and `expression_facts.py`. Where a rule needs a new fact (the prototype needed assertion owner metatype, sequence actuals, multiplicity bounds and redefinitions, the `if` operator, and String values/referents), it is extracted once, in a shared fact module, and not re-derived inside a decision.
- **[INHERITED: epic, Design principle 1]** Facts, capability decisions and consumer presentation stay separate. Decisions consume explicit facts and emit neutral reasons. L6 owns severity; codegen owns its code mapping.

## Non-Goals

- Codegen integration, `ElaborationCode` mapping, the independent conformance corpus in `tests/conformance/subset_profile/`, detector-disable mutation tests, per-site stable codes, the `check` command, and snapshot/version integration. These are Item 2.
- Reproducing or retiring ES-011, and deciding String metadata policy. These are Item 2 (epic open decision 3).
- L6 wiring, target-specific severity, the `execution-target` setting, and the audit of existing L6 checks. These are Item 3.
- The positional-binding check and hazard register. These are Item 4.
- Rendering `docs/patterns/generator-subset.md` and correcting shipped examples. These are Item 5. Item 1 supplies the documentation anchor field only.
- Fixing `L6-LIBRARY-ALIAS-SOURCE`. Item 1 reconciles it in the matrix only.
- Implementing new language support, or relaxing a current generator refusal.

## Open Questions / Deferred to design

- **R1 — owner gate, not decided here.** Who owns capability policy, and where the fact/decision/consumer boundary sits. `[INFERRED]` recommended direction for design to evaluate, from epic Item 1 scope 2: a pure module `sysml/subset_profile.py` (no SysIDE import, like `executable_profile.py`) with `SUBSET_PROFILE_VERSION`, neutral reason IDs, and fact extraction kept separate. The owner approves after design review and before planning.
  - ADR 0007 is sysml-codegen's `.project/adr/0007-agentic-mbse-owns-neutral-facts-codegen-owns-rendering.md` (active, `[AGENT] (ratified by owner, 2026-07-10)`). agentic-mbse's `.project/adr/` has no ADRs; dc3's and fusion-tea's ADR 0007 are unrelated supersession records.
  - What it settles: facts about the model are computed in agentic-mbse, facts about the output in codegen, and the dependency runs codegen → agentic-mbse only. What it does not settle: which side owns the admit/refuse decision. That is the R1 question, as the epic says.
  - Existing code already blurs that line, and design should account for it. `reference_use._require_supported_invocation` (`reference_use.py:395`) is a capability decision ("only `NumericalFunctions::sum` is supported") living in agentic-mbse's fact layer, and codegen consumes it as its own refusal. `executable_profile.py` is the other precedent, a pure decision module in agentic-mbse.
  - No durable product statement yet records the shared-contract promise, so the approved R1 decision should land as an ADR, and the implemented promise as a `.project/product/` entry at close.
- **R2 — owner gate, standing.** If any rule's evidence-backed boundary would still refuse a shape the pinned generator admits, design halts that rule and asks the owner.
- **R3 — owner gate, proposal only.** Absorption of GENERATOR-SUBSET-PATTERNS and the disposition of remaining capability gaps (ES-002, ES-008, ES-009, ES-011, the `unconfirmed` shapes, and the ten PUSH-DOWN rows). Item 1 records a proposed disposition; the owner approves it. Current refusal does not imply permanent exclusion.
- **Where the inventory and site account live.** Design picks a location the matrix/record cross-check test can read after the item folder is archived (package data or `tests/` data), and where the human-readable matrix lives.
- **How new reason IDs relate to `REASON_CODES`.** Extend the existing set, or add a sibling closed set with the same runtime validation. Design decides; either must stay enumerable and validated.
- **Root selection for occurrence-dependent rules.** How a caller supplies roots, and what default L6 and codegen will use. Design specifies the evaluator input; Items 2 and 3 choose their defaults.
- **Deduplication and identity policy.** How one declaration reached through several occurrences is reported, and which identity (declaration vs occurrence) each rule keys on.
- **ES-004 fact feasibility.** Whether effective reachable occurrences and resolved bounds can be extracted from SysIDE before elaboration in all contexts, and where the `unverified` boundary falls if not.
- **Promotion probes.** Whether design runs read-only generator probes at `b5663c07` to promote ES-002, ES-008 or ES-009 into rules (each has a dc3 observation but no retained fixture, and its code is shared by other sites), or to observe code-read shapes such as `min`/`max` and ordered part multiplicity.
- **Corpus manifest discrepancy.** sysml-codegen's batch README says 15 snapshots and 22 refusals; its `batch.json` at `b5663c07` holds 14 and 23. The corpus criterion uses the manifest. Reporting the mismatch upstream is an Item 2 or owner call, not an Item 1 edit.
- **Scanner hardening.** Whether Item 1 reuses the prototype scanner (`02-inventory.py`) as is or hardens it, and how its recognized forms are recorded.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_executable-subset-contract.md` (Item 1; boundaries Items 2–5; D1–D3)
- **Origin record:** `.project/backlog/item_generator-subset-patterns.md` (read through the epic's corrections)
- **Align record:** `.project/active/exec-subset-profile/briefs/align.md`
- **Prototype evidence:** `.project/concepts/convince-me-exec-subset/` (`template.html`; `evidence/01-README.md`, `evidence/02-README.md`, `evidence/01-fixtures/`, `evidence/02-inventory.csv`, `evidence/02-classification.csv`) — feasibility observations only
- **PUSH-DOWN profile rows:** `.project/backlog/BACKLOG.md` (`PUSH-DOWN-EXPR-PROFILE-*`, `PUSH-DOWN-HIER-PROFILE-*`, `PUSH-DOWN-AGG-PROFILE-*`) and `L6-LIBRARY-ALIAS-SOURCE`
- **Code extended:** `src/agentic_mbse/sysml/executable_profile.py`, `reference_use.py`, `hierarchy.py`, `aggregation.py`, `constraint_facts.py`, `expression_facts.py`; `src/agentic_mbse/errors.py` (`SemanticEvidenceCode`)
- **Cross-repository sources (read-only):** dc3 `work/orchestration/goals/study-ready-baseline/evidence/T-001-blocker-inventory.md` and `.project/active/toolkit-upstream-findings.md`; sysml-codegen at `b5663c07`: `tests/fixtures/v6_recapture_batch/{batch.json,README.md}`, `.project/adr/0007-agentic-mbse-owns-neutral-facts-codegen-owns-rendering.md`, and the refusal sites cited in the candidate table
- **Product-lens:** `.project/active/exec-subset-profile/product-lens.md`
- **Design:** `.project/active/exec-subset-profile/design.md` (to be created)

---

**Next Steps:** `/_my_spec_review`, then `/_my_design`, then owner gate R1 before `/_my_plan`.
