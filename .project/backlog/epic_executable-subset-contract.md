# Epic: One executable-subset contract for generator, validator and guidance

**Epic ID**: EXEC-SUBSET-CONTRACT
**Status**: Draft — revised after architecture and history audit
**Priority**: Not assigned (owner)
**Created**: 2026-10-14
**Revised**: 2026-10-18 (Items 1 and 4 closed; Item 2 split into 2a and 2b); 2026-10-21 (the copied generator rules are retired: ADR 0004; Items 1, 2a, 2b, 3, 5 and 6 rewritten below)
**Estimated Effort**: Re-estimate after Item 1's capability inventory and boundary design; the original ~10-day estimate excluded snapshot integration, occurrence-aware evidence and independent differential coverage.

---

## Executive Summary

**Current design (2026-10-21, ADR 0004).** Only the generator says whether a model generates: `sysml-codegen generate`, or its no-write check `sysml-codegen check` (Item 2b). agentic-mbse keeps no copy of the generator's refusal rules. The shipped guidance states the generator's three structural limits (an assert goes on a part, not inside a calculation; part counts are exact; a calculation input receives one value), and the modelling workflow runs `sysml-codegen check` early and at each phase when a project targets generated code. The copy Item 1 built (the "subset profile") is deleted by the `retire-subset-profile` item, with the tests that kept it agreeing with the generator. The next two paragraphs are the original 2026-10-14 framing, kept as history; the phrase "L6 reports that contract without depending on codegen" is the premise ADR 0004 replaced.

The generator (sysml-codegen), validator (L6) and shipped guidance describe overlapping but incompletely reconciled execution requirements. Existing shared constraint-profile and targeted binding contracts prevent some drift; they do not establish compatibility for complete published examples or all supported model shapes. This epic extends those contracts with a versioned **executable-subset profile**, independently tested against generator behavior, and a **semantic-hazard register** for valid but surprising language behavior.

The scope is a declared structural capability contract, not a promise that a static screen predicts every generation or runtime failure. L6 reports that contract without depending on codegen. A new `sysml-codegen check` exercises the shared read-only generation preparation path, including projection and generation preflight. Guidance states which evidence supports each example and which semantics a rewrite changes.

**Critical Success Factor (current, 2026-10-21)**: a project that targets generated code gets the generator's own answer from `sysml-codegen check` early in its modelling work, and the shipped guidance and examples do not teach patterns the generator refuses.

**Critical Success Factor (original, retired 2026-10-21)**: one `agentic-mbse validate --level=6` run accounts for the confirmed dc3 baseline categories B1–B8, with locations, stable reasons, remedies and distinct outcomes for refusal, exclusion and omission. B9 is unconfirmed and requires a separate reproducer or retirement. Pinned consumer findings match an explicitly approved baseline and severity policy; fusion-tea currently has 125 positional-binding findings and must not be described as clean. Independent generator tests detect missed and overbroad profile decisions; testing the new screen against itself is not sufficient.

**Origin:** [GENERATOR-SUBSET-PATTERNS](item_generator-subset-patterns.md), filed from dc3 WI-008. Proposed absorption remains pending owner approval. That file stays as the origin record; historical claims in it must be read with the corrections below.

## Evidence and regression revisions

All local cross-repository paths below are relative to the named repository. Pin exact revisions and package/profile versions in test evidence; do not use moving HEADs as acceptance inputs.

| Repository / role | Revision |
|---|---|
| agentic-mbse at this audit | `d546a00f3b26ff20aa023c8e090d7ca764a09619` |
| sysml-codegen capability baseline | `b5663c07e987a892e27d21e68cec40d0656574ee` |
| dc3 pre-WI-008 model | `808464df85d50521e4fbb9ba7cceb63d382aa832` |
| dc3 repaired model | `60b44d53460fccd2f44811d8abfd42bc270e90b2` |
| fusion-tea regression model | `f96ad312c63e8c66695971b12feab971f3ba6eb3` |

The dc3 T-001 investigation used agentic-mbse `8b027bbc`, codegen `b5663c07` and SysIDE 0.8.4. Reproduction must record the actually imported packages, not just repository locations. Dirty overlays, if needed, must be identified explicitly. Use isolated temporary regression trees; do not change consumer checkouts or mirror their entire models into this repository.

## Prototype findings and their limits (2026-10-15)

The explainer at `.project/concepts/convince-me-exec-subset/index.html` is generated from `template.html`; its evidence folder contains throwaway scripts, fixtures and captured logs. These are feasibility observations, not completed product acceptance. Preserve raw logs and identify corrections in their accompanying notes.

- The independent generator fixtures admit an `ordered nonunique` calc input bound to a scalar and refuse a literal sequence actual `(a, b)`. ES-003 must describe actual binding shape, not ban the parameter declaration. Other plural forms still need boundary fixtures.
- `in v = rate * fuel_code` is independently refused with `SI_EXPRESSION_SOURCE_UNSUPPORTED`; classify it explicitly as ES-012, separate from dc3 B1–B8.
- The prototype screen reports 240 blocking findings and 4 excluded predicates on the dc3 baseline, plus 32 String omissions. On the repaired tree it reports 0 blocking findings and 30 String omissions. These are overlapping declaration-level findings, not 240 independently reproduced generator refusals. Its part-instantiation heuristic is not production evidence.
- The differential reports 21 agreements and 1 missed refusal across 22 fixtures. It demonstrates useful disagreement detection within that corpus, not exhaustive equivalence. Omission detection currently searches names in emitted text and needs a stronger semantic oracle.
- The scanner counts 500 candidate sites: 441 in codegen and 59 in agentic-mbse, including constructors and forwarding/plumbing sites. Of these, 137 are free-text and 130 builtin raises without site-specific stable codes. This is not a count of 500 distinct reachable public failures, and their classification is a draft rather than owner-reviewed evidence.
- Five computed profile-reason call sites exceed the scanner's resolver. Production already has an enumerable 27-member `REASON_CODES` set and rejects unknown reasons in `EligibilityDiagnostic.__post_init__`. Reuse that vocabulary and verify emitted mappings; an enum conversion is not required by this finding.
- The guidance manifest accounts for 212 fences: 9 executable, 14 native-only, 3 negative, 17 definition and 169 fragment entries. Thus 26 receive generation verdicts and 17 receive definition checks. Separately, the initial standalone/import-wrapped parser inventory loads 41 fences cleanly; that is a different measurement. Fragment hashes detect changes, not executable correctness.
- The positional prototype reports 125 fusion-tea mismatches and 0 in each dc3 tree. Under approved decision D1, the explicitly pinned legacy findings are warnings and new mismatches block acceptance. A blanket claim that these are harmless or that the pinned project passes is unsupported.

## Why This Epic?

### What the evidence establishes

Codegen was installed in dc3's initial October 3 setup. Native comparison work subsequently used constructs outside the generator's supported route. T-001 on October 13 records five sequential generation probes, additional coordinator/worker probes, and some unpinned scratch evidence. It identifies B1–B8 and explicitly labels B9 unconfirmed. Ten days describes elapsed project age, not independently established active modeling duration. The earlier claims of about 20 runs and exactly 12 non-expert dispatches are not acceptance evidence without their session records.

The native comparison was deliberately bounded. The October 5 owner amendment in dc3 `work/orchestration/goals/conversion-path-efficiency/goal.md` permits a supported native result with generated readiness explicitly parked; its October 13 closure follows that contract. Existing L6 failures were disclosed. The native reviews therefore did not certify generator compatibility, and generation deferral was not itself proof of a process violation.

During WI-008, mutation probes exposed a silent wrong-value risk: unprefixed calc-usage input declarations can redefine formals by position. The examined dc3 baseline and repaired trees have no detected mismatches. Later prototype evidence demonstrates a cross-route divergence: the reversed-input subtraction fixture evaluates to -7 natively but 7 through the pinned generator and TEAx. The fusion-tea scan finds 125 implicit mismatches; no full affected fusion-tea generation/runtime comparison was performed. Neither generated success nor opaque calc bodies establish semantic agreement across routes.

Primary consumer evidence:

- dc3 `work/orchestration/goals/study-ready-baseline/evidence/T-001-blocker-inventory.md`, especially method and B1/B6/B9.
- dc3 `.project/active/toolkit-upstream-findings.md`, U1–U7; U7 says dc3 already uses `out attribute` and the return-result claim was not reproduced by the coordinator.
- dc3 `work/orchestration/goals/conversion-path-efficiency/goal.md`, October 5 and October 13 amendments.
- dc3 WI-008 design, review and audit, plus `work/learnings/RAW_LEARNINGS.md`.

### Root causes and historical corrections

| Mechanism | Evidence and interpretation |
|---|---|
| Language-valid examples became misleading execution guidance | Examples in `constraints.md`, `syntax-reference.md`, `semantic-operators.md`, `conditionals.md`, conventions and expert guidance were not systematically qualified when the generator subset narrowed. `in x =` is valid when used correctly; its prevalence alone is not an error. |
| Parallel changes reconciled only one semantic dimension | agentic-mbse `dcb187ba` introduced the calc-owned assert comment “Executes” on August 12 while correcting prefix semantics. Codegen `0dd02728` added the calc-owner refusal later that day. The comment predates the August 13 owner ruling and was carried into coordinated integration by `1decd952`. The integration failed to reconcile prefix and attachment behavior. |
| Tests covered bounded contracts, not complete examples | Codegen `tests/conformance/test_self_binding_guidance_contract.py` checks pinned excerpts, a global self-named-binding sweep and a reviewed qualified-binding inventory. The companion change is `3e9734b3`; the codegen change is `20a8bb7a`. Those controls are useful but do not execute every example. |
| Known hazards lacked a reliable route into author guidance | Positional behavior was documented by codegen `3bdf0b74` / `936315c8` on July 20 in `tests/fixtures/modeled_default_fidelity/PROVENANCE.md`. `f0a7b0a9` filed POSITIONAL-FORMAL-REDEFINITION on August 21; `bd352744` corrected its premise October 8. The diagnostic item remains open. This was not a closed defect whose lesson disappeared. |
| Validator coverage was broader in presentation than in behavior | L6 contains useful shared constraint decisions plus hand-written readiness checks and silent inspection fallbacks. ADR-002's calc-body exemptions serve calculation-placement rules; they are not evidence of generator admission. Separate capability coverage is missing. |
| Eventual execution obligations lacked early compatibility discovery | Native scope was authorized, but the later generated route required structural rewrites. Integration evidence must follow the promised route and preserve explicit native-only scope decisions. Specialist consultation can help resolve uncertainty; dispatch counts alone do not establish correctness. |

The older guidance dates include January commits `0bb8ab4a`, `839bac08`, `f43bb079` and February 2 `206fb5bc`. Fusion-tea's actual input-positional evidence is in `modeling_project/ARCHITECTURE.md` AD-008 and WI-076 implementation notes; `RAW_LEARNINGS.md:80` concerns output-tuple ABI ordering and must not be cited for input semantics.

**Causal conclusion:** narrow changes and reviews proved their individual contracts, but integration did not test the resulting complete teaching examples across ownership, binding and execution contexts. Knowledge was recorded without a dependable promotion obligation. The architecture already calls readiness drift a bug (`.project/concepts/architecture-redesign/main.md` and `information-architecture.md` §4.1); this epic repairs that boundary contract.

## Design principles and contract boundaries

Principles 1 and 3 describe the shared capability evaluator, which ADR 0004 retired; they are kept as history. The rest still apply.

1. **Separate facts, capability decisions and consumer presentation.** Shared AST/occurrence evidence belongs in agentic-mbse. The shared capability evaluator consumes explicit facts and emits neutral stable reasons. L6 owns validation severity; codegen owns `ElaborationCode` mapping and output-specific checks. agentic-mbse must never import sysml-codegen or its types. ADR 0007's neutral-fact ownership does not alone settle capability-policy ownership: Item 1 must document that decision.
2. **Extend the existing profile rather than duplicate it.** `executable_profile.py` remains the authority for constraint-predicate eligibility, including BLOCK, NON_NUMERICAL and UNASSESSED distinctions. New structural decisions reference it where applicable.
3. **Independent behavioral evidence.** Compare the shared evaluator with the generator's underlying route with the new screen bypassed in tests. An annotation or an early-screen refusal is not proof of equivalent behavior.
4. **Explicit scope and coverage.** Inventory every public refusal stage, but distinguish shared structural rules, codegen-specific preparation checks, environmental failures and internal invariants. L6 claims only the capability coverage it implements. Valid models reaching a public refusal are not internal invariants.
5. **Report all independently evaluable findings.** Continue unrelated checks after an element inspection fails. Report missing prerequisites and unverified dependent checks; do not invent downstream findings or claim exhaustive results when evidence is unavailable.
6. **Language validity, execution support and check failure are separate.** A native-valid construct can be outside the generated subset. A tool's inability to assess it is not a confirmed refusal. Intent controls capability severity, not the truth of the underlying decision.
7. **Preserve semantics explicitly.** A proposed rewrite must state changes to guards, coverage, numerical behavior and metadata consumers. Generation success alone does not establish equivalence.
8. **One authority across live and snapshot routes.** Versions, sealed snapshot authority and package compatibility must account for the new policy, with deterministic diagnostics and source locations.
9. **Route surprises into guidance regardless of ticket disposition.** Open, corrected, deferred and closed findings can all require a hazard entry. Keep the existing proportional toolkit workflow; use specialist review for concrete unresolved questions.

## Success Criteria

Criteria marked "retired 2026-10-21" depended on the copied rules and no longer apply (ADR 0004).

- [ ] A reviewed capability matrix maps confirmed B1–B8 and U1–U7 to exact contexts, independent fixtures, outcomes and diagnostics. B9/ES-011 has a reproducer or explicit retirement; it is never required to occur in dc3 `808464d`. Retired 2026-10-21: the matrix served the copied rules.
- [ ] One L6 run on the baseline accounts for all confirmed in-scope categories with locations and remedies. Expected declaration/occurrence counts and duplicate handling are recorded separately from static text counts. Pinned consumer results match reviewed finding identities and outcomes, including the 125 fusion-tea positional mismatches. Under approved D1, the identified legacy mismatches remain visible warnings and new mismatches are errors; exclusions, omissions and advisories retain explicit expectations. Retired 2026-10-21 for the L6 part; the positional part was met by Item 4.
- [ ] Every known silent-loss family has a retained behavioral fixture, including intended metadata omissions; assertions check semantic identity, generated contract/catalog or runtime behavior rather than name substrings alone.
- [ ] Every shared rule has independent refused and admitted boundary fixtures. Existing generating fixtures remain admitted unless an intentional capability change is separately approved. Retired 2026-10-21: there are no shared rules; the 246 case models stay as generator regression tests.
- [ ] A refusal inventory covers elaboration, projection, generation preparation and diagnostic factories. Structural cases map to neutral rules with behavioral coverage; other public checks are explicitly owned and tested. AST annotation tests are supplementary. 2026-10-21: the refusal site account stays in sysml-codegen; the mapping to neutral rules is retired.
- [x] `generate` and `check` use the same read-only preparation path before output mutation. 2026-10-21: they report only the generator's own answer. `check` includes projection, compilation and generation preflight and clearly bounds its readiness claim. (Item 2b, closed 2026-10-22.)
- [x] Live/snapshot parity, sealed authority, supported upgrades and both package-skew directions are tested. (Item 2b, closed 2026-10-22.)
- [ ] The positional check detects unintended implicit name/target mismatches, accepts deliberate explicit redefinition and verified by-name forms, and reports inspection failures honestly.
- [ ] Every collected shipped example has appropriate definition checks, an executable test, an identified fragment exemption, or verified expected diagnostics. Complete execution examples exercise their instantiated context through the generator corpus. Approved D3 requires executable or exact expected-negative evidence for 100% of generated-use recommendations and remedies; hash-only exemptions cannot satisfy that target.
- [ ] Rendered capability guidance and hazard references agree with the records and packaged assets. Known misleading examples are corrected or qualified. 2026-10-21: the rendered-from-records part is retired; the calc-owned assert examples were corrected by `retire-subset-profile`.
- [x] Execution-target behavior is tested for generated, native, unset, malformed and unknown settings, including retained legacy readiness checks and noninteractive init.
- [ ] Repository-defined tests, type checks and lint pass in both repositories; evidence distinguishes licensed checks, skips and unrun routes.

## Backlog Items

### Item 1: Capability inventory, boundary design and shared profile ✅ (retired)

**Retired 2026-10-21** by `retire-subset-profile` (ADR 0004 supersedes ADR 0001; P-0004 supersedes P-0001). The profile, its rules TOML, the fact extraction and occurrence port, the coverage statement, the advisories and the 154 packaged cases are deleted from agentic-mbse; the cases move to sysml-codegen first. Kept as documentation: Item 1's archive, including its write-ups of where each of B1-B8 starts and stops. The record below is history.

**Status**: Complete (2026-10-18) — certified with recorded limits; archived to `.project/completed/20261018_exec-subset-profile/`. Success criteria met, with the owner-accepted limit that dc3 B8 reports `unconfirmed` (calc-usage-owned constraints are refused first under B1). Owner calls 2026-10-18: R3 disposition approved (`evidence/r3-proposal.md`), retiring the unprobeable `part-multiplicity/nonunique` and `negative_bound` shapes; G1/G2 go to Item 2 via `kerml-expert` before any codegen fix; the sysml-codegen ADR 0012 amendment files when Item 1 merges. Decision: ADR 0001. Promise: P-0001.

**Type**: Design and implementation
**Effort**: Re-estimate after inventory. [AGENT] Re-estimated 2026-10-18 at Item 1's close-out: [re-estimate](../completed/20261018_exec-subset-profile/evidence/re-estimate.md) (Item 2 ~23-37 engineer-days).
**Status**: [AGENT] Implemented 2026-10-18 (`.project/completed/20261018_exec-subset-profile/`); audited 2026-10-18 (certify with recorded limits) and audit fixes applied, final revision `ce0ad1ff`; awaiting the owner's R3 decision and B8 acceptance.
**Dependencies**: Co-developed with Item 2; Item 4 can proceed independently.

**Objective**: Define and implement the structural contract without duplicating model interpretation or broadening current refusals accidentally.

**Scope**:
1. Inventory public refusals and known silent losses across elaboration, projection and generation preparation. Include indexed references, deep-qualified wiring and all existing PUSH-DOWN expression/hierarchy/aggregation profile rows. Assign each case to a shared rule, a codegen-specific check, an advisory/omission policy, a separately tracked gap, or an evidenced internal invariant. Reconcile adjacent `L6-LIBRARY-ALIAS-SOURCE` explicitly rather than implying this epic fixes it.
2. Record the capability-policy ownership decision and dependencies. Recommended: pure `sysml/subset_profile.py` with `SUBSET_PROFILE_VERSION`, neutral reason IDs and separate extraction of required facts. Reuse existing reference, hierarchy, aggregation and constraint evidence. Do not import `ElaborationCode` or use consumer-specific identifiers as the shared decision vocabulary.
3. Define rule records: stable ID, exact applicability/context, outcome, fact requirements, remedy with semantic limits, working-example fixture, documentation anchor and evidence status. Reuse `executable_profile.REASON_CODES` and its runtime membership validation. The inventory must resolve or explicitly map computed diagnostic sites to that existing closed vocabulary and test possible emissions; variable arguments alone do not prove an open vocabulary. Distinguish `refused`, `admitted`, `excluded`, `omitted` and `unconfirmed`; missing evidence yields an unverified check result. Codegen maintains its own diagnostic mapping, which may be one-to-many.
4. Treat the following as candidate families to refine with fixtures, not universal construct bans:

   | Candidate | Boundary to establish | Historical evidence |
   |---|---|---|
   | ES-001 | Calc-definition/usage-owned assertions and effective attachment | `SI_CONSTRAINT_UNATTACHED` |
   | ES-002 | Constraint actuals targeting calc inputs in a concrete occurrence | `SI_OCCURRENCE_MISSING` |
   | ES-003 | Sequence/plural actuals bound to calc inputs: literal `(a, b)` is refused; ordered/nonunique declarations with scalar actuals are admitted in the retained neighbors | `SI_EXPRESSION_SOURCE_UNSUPPORTED` for the literal sequence; reproduce other plural forms separately |
   | ES-004 | Unresolved bounds or unsupported effective multiplicity in instantiated part occurrences; admit resolved specializations and unused templates | `SI_MULTIPLICITY_UNRESOLVED` / `SI_MULTIPLICITY_UNSUPPORTED` by effective shape |
   | ES-005 | Invocation context and exact callable identity; sum operands/wrappers have their own boundaries | `SI_EXPRESSION_SOURCE_UNSUPPORTED` |
   | ES-006 | Conditional expression forms and the actual missing evidence | `SI_EVIDENCE_INCOMPLETE`; reproduce cause |
   | ES-007 | Separate Boolean data/output capabilities, non-numerical exclusion and malformed predicates | Existing executable-profile decisions; do not collapse into one refusal |
   | ES-008 | Nested subsetting/value-writer conflicts in effective occurrences | `SI_REDEFINITION_INVALID` |
   | ES-009 | Usage-subsetting composition and occurrence availability | `SI_OCCURRENCE_MISSING` |
   | ES-010 | String metadata versus executable dependencies; both redefinition spellings | Silent omission and inconsistent existing L6 diagnostics |
   | ES-011 | Arithmetic using a named return result | Unconfirmed `SI_EDGE_DANGLING`; reproduce or retire |
   | ES-012 | Arithmetic expression actual bound directly to a calc input, e.g. `in v = rate * fuel_code`; contrast supported references and other actual forms | Confirmed `SI_EXPRESSION_SOURCE_UNSUPPORTED` on the retained fixture |

5. Evaluate over selected user-model scope, including calc bodies where the relevant capability applies. Specify template versus instantiated evidence, standard-library exclusion, stable ordering, declaration/occurrence identity, location fallback and diagnostic deduplication. ES-004 must use effective reachable occurrences and their resolved bounds. A globally observed typing or an exact redefinition elsewhere does not discharge another occurrence; do not carry the prototype heuristic into production.
6. Detector failures produce structured unverified results with rule/context and safe location, not a false unsupported-construct finding. Enumeration/extraction failures must not become empty clean results. Continue checks whose facts remain available.

**Out of Scope**: implementing new language support. Stricter policy is a behavior change requiring explicit review, not a side effect of screening.

**Success Criteria**: the inventory is complete relative to the pinned generator surface; every deferred case has an owner and coverage limitation; independently accepted near-neighbors remain accepted; detector failures and incomplete scope cannot produce a clean assessment.

**Deliverables**: `.project/completed/20261018_exec-subset-profile/{spec,design,plan}.md`; capability/refusal matrix; shared facts/evaluator, records and tests.

### Item 2 (sysml-codegen): Independent conformance and read-only readiness check — split

**Split** 2026-10-18 into Item 2a (conformance) and Item 2b (readiness check). [AGENT] (ratified by owner, 2026-10-18). Reason: the combined estimate was 23–37 engineer-days, and the readiness check's preparation-path and snapshot scopes were the least examined third of it. 2a goes first: `check` is only as trustworthy as the conformance evidence behind it. Item 1 routed its open gaps here ([R3 table](../completed/20261018_exec-subset-profile/evidence/r3-proposal.md)); they belong to 2a. The original six scope points are kept verbatim below, assigned to one half or split between them.

**2026-10-21:** both halves lose their copy-related parts (ADR 0004); see each half.

**Owner gates for both halves** [OWNER] (2026-10-18): any change to what the generator accepts or refuses, including a G1/G2 fix after the `kerml-expert` check; the String metadata policy (open decision 3); merges, PRs and the ADR 0012 amendment filing.

### Item 2a (sysml-codegen): Independent conformance corpus and per-site codes ✅

**Status**: Complete (2026-10-20) — certified (final-audit re-check 2026-10-19, every spec success criterion met), then integrated with merged Item 3 after the rebase onto PR #32 (this repo `e2bff13f`, gate receipt `3bb043ea`; sysml-codegen `ceb6796e`). Not merged yet: branch `subset-conformance` in both repos, for a coordinated merge. Integration changes L6 output two ways: the verdict line names `subset-profile/v2, subset-coverage/v2`, and the coverage line says 70 follow-up sites instead of 85. Owner gates still pending: RG-1 (12 candidate accept/refuse changes, `rg1-recommendations.md`), RG-2 (String policy, `rg2-string-policy.md`), RG-3 (the merge, and filing the staged ADR 0001, sysml-codegen ADR 0012 and ADR 0016, and P-0001 amendments; check the owner's sysml-codegen branch `adr-0012-occurrence-summary-amendment` for overlap first). The epic-level Success Criteria above were not re-ticked at this close; they span several items.

**2026-10-21, after ADR 0004:** 2a keeps its generator half: the stable refusal reasons (`SiteReason`), the refusal site account and its scan tests, the 246 case models with their generator answers, the generator mutations and the refusal records. Its agreement half (the tests comparing the copy with the generator, `disagreements.json`, the occurrence-parity CI test, the profile version pin) is deleted by `retire-subset-profile`. Scope 1 (mapping the copy's reasons to `ElaborationCode`) and the parity test in scope 6 are retired. The staged ADR 0001 and P-0001 amendments listed under RG-3 are moot; RG-1 and RG-2 stand as generator questions.

**Location**: archived in sysml-codegen git at `c381fb00eb8e51248f68701e00ac997ebf2cd413:.project/active/subset-profile-conformance/` (sysml-codegen closes by deleting the folder; git history is its archive)
**Type**: Integration
**Effort**: [AGENT] ~25–35 engineer-days, revised at spec review 2026-10-18 (sysml-codegen `c381fb00:.project/active/subset-profile-conformance/spec-review.md` L2-2); the first figure, 17–27, omitted silent-loss, String-fixture and fixture-classification work.
**Dependencies**: Item 1 (merged, PR #30). Item 4 supplies hazard references; until it does, scope 6's link is recorded as pending.

**Scope**:
1. From original scope 1: codegen adapters own diagnostic-code and remedy rendering. Map the neutral reason IDs to `ElaborationCode` (one-to-many by design). Pin the profile and declare compatible package requirements. Adopting the decisions inside `generate` before output mutation is 2b.
2. Original scope 2: Build `tests/conformance/subset_profile/` with independent elaboration tests that bypass the new screen. Include each refusal condition, accepted near-neighbors, inherited/redefined contexts, alternate spellings, templates versus instances, and dc3 proto3/proto4nest/conv shapes. Exercise all existing successful fixtures against the profile.
3. Original scope 3: Supplement behavior tests with an AST/factory inventory contract. Adding an unclassified public refusal fails inventory tests. Merely naming a rule does not establish coverage: each relevant condition needs a witness, and a mutation that disables its detector must fail conformance. Classify the 137 free-text and 130 builtin candidate sites per site or justified family: public capability, malformed input, environment, snapshot compatibility/integrity, relay/plumbing or internal invariant. Reachable public capability refusals need stable reasons/codes; not every Python exception needs a new enum member. Internal-invariant exemptions need evidence that a well-formed supported input cannot reach them. Scanner completeness is bounded by its recognized syntax/factories; add mutation cases for new exception classes, helpers and computed mappings, and report unresolved coverage instead of declaring all 500 sites public refusals.
4. From original scope 5, the silent-loss part: for every known silent-loss family, keep a model with explicit expected semantic presence/absence at the appropriate seam and an admitted control; cover both accepted metadata omission and loss that must block. [AGENT] (ratified by owner, 2026-10-18): the requirement applies to the known families. A general detector for unknown losses ("a newly missing declaration even when generation exits successfully") is a recorded limit, not an acceptance gate, because name search over output is not a strong enough oracle (Item 1 finding).
5. Original scope 6: Resolve String metadata policy and reproduce or retire ES-011. Update `modeling-assumptions.md` with actual admitted/excluded behavior. Link the still-open POSITIONAL-FORMAL-REDEFINITION item to the hazard entry without changing its disposition artificially.
6. Item 1's routed work: the permanent occurrence-parity test in codegen CI; the R3 gaps (ES-002, ES-008, ES-009, ES-010 refusal side, ES-011, calc-def bare result, calc-usage bare-result drop, DEEP-QUALIFIED-WIRING rule decision, PUSH-DOWN rows routed to Item 2); the unconfirmed-pair probes; the 85 follow-up sites; G1/G2 semantics checks via `kerml-expert` (any resulting generator change is an owner gate).

**Success Criteria**: independent corpus and detector-disable mutations pass; a new unclassified refusal fails the inventory; historical baseline findings match the matrix; every known silent-loss family has a presence/absence fixture and an admitted control; every R3 row routed to Item 2 is resolved, reproduced, retired or explicitly deferred with an owner.

**Deliverables**: sysml-codegen `c381fb00:.project/active/subset-profile-conformance/{spec,design,plan}.md`; diagnostic mapping, inventory contract, conformance corpus, parity CI test and evidence.

### Item 2b (sysml-codegen): Read-only readiness check and snapshot authority ✅

**Closed 2026-10-22** in sysml-codegen PR #23; promise sysml-codegen P-0008. Record retained at sysml-codegen `d7366431:.project/active/subset-profile-screen/`.

**2026-10-21, after ADR 0004:** 2b keeps `check`, the load / check / write split and refusing before writing. The screen step that ran the copy after `generate` and `check` and printed its findings is removed (sysml-codegen branch `subset-profile-screen`), so `check` reports only the generator's answer and writes nothing. Scope 1 below is retired; scopes 2 and 3 stand. sysml-codegen PR #21 (ADR 0018, an occurrence summary shared with agentic-mbse) is moot.

**Type**: Integration
**Effort**: [AGENT] ~6–10 engineer-days; not examined by Item 1, so the least certain estimate in the epic.
**Dependencies**: Item 2a.

**Scope**:
1. From original scope 1: Integrate shared decisions where required facts are available, collecting independent findings before output mutation. Do not assume all occurrence-aware facts exist before elaboration. Uses 2a's diagnostic adapters and profile pin.
2. Original scope 4: Factor the actual read-only preparation path for `generate` and `check`: admission, facts/capability assessment, elaboration, projection, generation metadata/type/name/collision/totality checks, body/plan compilation and coverage checks. Keep destination mutation and emission outside it. State any destination/environment checks that require separate assessment. `check` writes no generated package or clears no directory; use sentinel tests. Readiness does not certify runtime behavior or handwritten implementation correctness.
3. From original scope 5, the snapshot part: integrate the new policy with snapshot authority, certifiability, receipts and version checks. Decide how existing snapshots can be assessed, rejected or upgraded if required facts are absent; no fallback to a silent live-only screen. Test live/replay decision parity, supported historical snapshots, unsupported authority versions and both package-skew directions using isolated artifacts.

**Success Criteria**: check and generate fail at the same preparation seam without mutating a sentinel destination; replay and compatibility evidence pass.

**Deliverables**: sysml-codegen `d7366431:.project/active/subset-profile-screen/{spec,design,plan}.md`; preparation API/CLI and compatibility evidence.

### Item 3: L6 integration and execution-target settings ✅

**2026-10-21, after ADR 0004:** L6's display of the copy's findings, the two L6 advisories and the String-subject suppression are removed by `retire-subset-profile`, so L6 makes no generation claim (P-0005 supersedes P-0003). The `execution-target` setting stays with two jobs: under `native` it folds the four legacy generator-only codes into one INFO summary, and it tells the workflow a project targets generated code (ADR 0005 amends ADR 0003). Scope 6's profile-version wording is retired. The record below is history.

**Type**: Implementation
**Effort**: Re-estimate after Item 1
**Dependencies**: Item 1

**Scope**:
1. Add `[tool.agentic-mbse] execution-target = "generated" | "native"` to target-project settings. Define project-root discovery from the validated model path, behavior outside a project, and precedence if an explicit override is provided. Malformed TOML and unknown values are errors, not unset defaults.
2. `init` offers an explicit target option and an interactive choice where appropriate. Noninteractive init preserves existing values and leaves the target unset with actionable output when none is supplied. Preserve unrelated TOML, comments, existing settings and symlink ownership even under `--force`; use the established explicit settings-preservation rule.
3. Separate semantic outcomes from display severity:
   - `generated`: confirmed unsupported capabilities are errors. Exclusions and omissions retain distinct outcomes; their blocking policy must be stated, not inferred from NON_NUMERICAL alone.
   - `native`: generator-only capability findings summarize at INFO, with detailed structured results available. Native correctness errors remain errors.
   - Unset: warn that generated compatibility is not certified; expose findings without labeling the model generated-ready.
   - Check/configuration failures remain errors for checks actually requested, regardless of target. Do not downgrade an inspection failure into a native capability summary.
4. Audit every existing L6 check. Replace duplicates with shared decisions and route retained generator-specific checks through target policy. Keep ADR-002 placement and manifests under their own documented applicability. Native settings must not leave contradictory legacy generator-only errors in place.
5. Review the 27 broad exception sites in `level6_architecture.py` and `adr002.py`: report failed checks as `L6_CHECK_ERROR`, retain safe display-only fallbacks, and distinguish failed metrics from clean counts. Fix the stale resolver citation. Report all independent failures without fabricating dependent conclusions.
6. Update README, model-validation guidance and CLI output to state the profile version, assessed scope, incompleteness and the boundary between L6 and full `sysml-codegen check`.

**Success Criteria**: CLI tests cover all settings states, root discovery, retained checks, inspection failures and preservation behavior. Baseline confirmed categories appear in one explicit L6 run, both String spellings agree, and native capability summaries do not hide check failures.

**Location**: `.project/completed/20261020_l6-subset-profile/`
**Deliverables**: `.project/completed/20261020_l6-subset-profile/{spec,design,plan}.md`; L6/settings/CLI changes and managed guidance updates.

### Item 4: Positional-binding hazard and check ✅

**Status**: Complete (2026-10-18) — certified; archived to `.project/completed/20261018_positional-binding-check/`. Success criteria met; the `out_before_in` row is met with a recorded limit (L1 does not read `diagnostics.validation`; backlog `VALIDATE-SEMA-DIAGNOSTICS`). fusion-tea `f96ad312` reproduces exactly the prototype's 125 identities; both dc3 trees are zero. Decision: ADR 0002 (pin-list contract; R4-1 by review). Promise: P-0002. Open for the owner: R4-3 (fusion-tea adopts the pin list with its pin move) and routing the draft codegen by-name-wiring finding to Item 2.

**Type**: Implementation
**Effort**: Re-estimate for semantic boundary cases
**Dependencies**: None

**Scope**:
1. Add `L2_POSITIONAL_BINDING` for an authored input whose **implicit** redefinition targets a differently named formal without an explicit redefinition accounting for the target. Use resolved identities and implied/explicit relationship evidence, not equality of name sets. Describe it as a likely authoring hazard in valid SysML. Apply approved D1: new mismatches are blocking authoring-policy findings; explicitly pinned legacy mismatches are warnings until migration. Intentional positional use needs a narrow, documented disposition rather than an automatic new baseline entry; do not introduce an unconditional language-validity error contrary to the design principles.
2. Cover CalculationUsage and ConstraintUsage, inheritance, explicit renaming, anonymous features, omitted/defaulted inputs, multiple targets and unavailable evidence. A deliberately renamed `in local redefines a = ...` is not a swap. Report unverifiable inspections separately using the existing L2 failure pattern.
3. Promote the audit probes into retained minimal fixtures. Also retain the cross-route subtraction counterexample: reversed unprefixed inputs produce native -7 and generated/TEAx 7 at the pinned versions. Record the generator semantic discrepancy upstream and its disposition; this epic adds evidence/detection without silently changing generator binding behavior. SysIDE 0.8.4 evaluated `in local redefines a = 10; in b = 3;` as 7 for `a-b`; reversed unprefixed `in b = 3; in a = 10;` evaluated as -7. Reversed explicit `in :>> b = 3; in :>> a = 10;` evaluated as 7 and generated correctly with codegen `b5663c07`. Audit scratch artifacts under `/tmp/consumer-audit-byname/` are supporting observations, not durable acceptance fixtures.
4. Create `docs/patterns/semantic-hazards.md`: expected reading, actual semantics, precise spec section, verified tool versions, detector/limits and upstream links. Cite KerML `checkFeatureParameterRedefinition` for positional semantics. The nearby constructor named-argument passage is about constructor notation, not proof of calc-usage syntax. Scope output-override and `[*]`/`[0]` entries to reproduced forms rather than universal claims.
5. Record the 125 pinned fusion-tea findings by stable owner/input/target identity, not just count. Approved D1 accepts those explicitly pinned legacy findings as visible warnings until migration; new or changed mismatch identities block acceptance. Test that adding a mismatch fails and that a disappearing legacy finding requires baseline reconciliation. This policy does not establish correct native values. Migration requires a separate authorized fusion-tea work item and before/after generated behavior evidence; no consumer edits are implicitly authorized by this toolkit epic. Any suppression must be narrow, justified and regression-tested.
6. Update `plant-idiom.md`, conventions, MODELING_GUIDE and expert roles: use verified explicit by-name redefinition where appropriate, or preserve definition order for implicit declarations; distinguish explicit renaming. Qualify “Order does not matter” by its actual context. Link the existing self-binding contract instead of replacing it.

**Success Criteria**: swapped toy and dc3 interleave mutations are detected; explicit rename/by-name and ordinary in-order cases pass; the dc3 trees remain clean, and fusion-tea matches the explicitly approved D1 policy and recorded finding baseline; inability to inspect cannot silently pass. A blanket clean-pass assertion is not an acceptance criterion. The register and guidance cite retained fixtures and correct specification sections.

**Deliverables**: `.project/completed/20261018_positional-binding-check/{spec,design,plan}.md` (combine artifacts where proportionate); check, fixtures, register and guidance.

### Item 5: Executable guidance contracts

**2026-10-22, rescoped by owner:** "not ceremony, actual risk". Item 5 is now `generated-results-guidance` ([spec](../active/generated-results-guidance/spec.md)): four risks (patterns that generate but compute something different; part-owned asserts report instead of stopping; guidance still teaching refused functions; guidance going stale when held generator changes land). Scopes 1-3 and 8 (the fence inventory, categories, exemption manifest and the 100% D3 target) and scope 7 are out. [AGENT] proposal, ratified by owner 2026-10-22. The text below is the original scope, kept for history.

**Type**: Testing and documentation
**Effort**: Re-estimate after example inventory
**Dependencies**: Item 4; Item 2 for generator execution evidence (2026-10-21: no longer depends on Item 1)

**2026-10-21, after ADR 0004:** Item 5 no longer renders a doc from rule records and no longer runs profile checks; executable-example evidence comes from sysml-codegen's case models and `sysml-codegen check`. `retire-subset-profile` already stated the three structural limits in the guidance and corrected the four calc-owned assert examples, each run through `sysml-codegen check`.

**Scope**:
1. Inventory authored SysML fences in shipped patterns, relevant top-level docs, skills, agents and templates using the packaged asset inventory. Distinguish vendored language/reference corpus from authored guidance explicitly; published SysML references are not promises of generator support. Handle nested fences in template examples correctly.
2. Give each collected example a stable identity and one evidence category:
   - Syntax fragment: an identified exemption with reason and context needed for testing.
   - Complete definition: parse/semantic and applicable L2 checks, without claiming its unused body generated.
   - Executable example: fixture supplies required definitions, selected root/instantiation and relevant bindings; codegen's independent corpus exercises generation preparation.
   - Deliberate negative/native-only example: verify exact expected findings/outcomes and reject unexpected diagnostics.
3. Wrappers/imports must be explicit and semantically justified. `native-only` markers list exact capability reasons, not language-invalid errors. Fragment exemptions use an identity/content/reason manifest; additions or changes require explicit review. A constant count cannot hide replacing a checked example with an unchecked one.
4. Retired 2026-10-21: rendering `docs/patterns/generator-subset.md` from the rule records, because the records are deleted (ADR 0004). Tested working patterns link to sysml-codegen case models at recorded revisions instead.
5. Correct misleading calc-owned assert, conditional, metadata and function guidance. The calc-owned assert corrections are done (`retire-subset-profile` Phase 2); conditional, metadata and function guidance remain. Preserve native-valid teaching where useful, with an explicit execution qualification. Test the ownership × assertion-form combinations that escaped the August integration.
6. Remedies must state preservation obligations. Part-owned generated verdicts do not by themselves preserve fail-closed native guards. Numeric predicate rewrites must preserve the intended domain. The arithmetic min identity needs numerical-domain, cancellation/overflow and tolerance evidence; it is not an identical universal replacement. Metadata moves must account for native consumers. Keep changed behavior visible in the docs.
7. Add evaluator-author notes to `adr002-calculations.md`, with versioned evidence and scoped claims; prose claims need a fixture/reference even when outside the fence harness.
8. Record the prototype coverage baseline (26 generation verdicts, 17 definitions, 169 fragments out of 212) and define a stable inventory of generated-use recommendations and remedies, including repeated instances and their context. Approved D3 target: 100% of that inventory has retained executable or exact expected-negative evidence at completion, with justified pure teaching fragments remaining exempt. Reuse canonical fixtures only when each snippet/context is checked against them; a hash alone is insufficient. Report converted and remaining entries by identity and category. Making every pure teaching fragment runnable is not required by D3.

**Success Criteria**: every inventoried fence is accounted for; removing a marker, adding an exemption, changing an expected diagnostic, breaking instantiation or disabling a relevant detector fails the appropriate test. Adding an unrelated rule need not invalidate unrelated examples. Packaged-guidance checks pass and complete execution examples agree with independent generator evidence.

**Deliverables**: `.project/active/shipped-example-contract/{spec,design,plan}.md`; example inventory/harness and corpus links, and corrected assets.

### Item 6: Proportional workflow gates and knowledge routing

**Type**: Implementation
**Effort**: Re-estimate after integration design
**Dependencies**: Item 2b (`sysml-codegen check`) and Item 5 (2026-10-21: no longer depends on Item 3's profile display)

**2026-10-21, after ADR 0004:** scope 1 is done by `retire-subset-profile` Phase 3: `MODELING_PROCESS.md` and the design, plan, implement, model-validation and toolkit-awareness skills run `sysml-codegen check` from the first model pieces, at each phase and before any claim that the model generates, and report a missing generator as "not checked". The evidence is the generator's answer, not L6. A parked project runs the check once early without blocking, which covers the probe half of scope 2. The remaining scopes are restated below without the profile.

**Scope**:
1. Done 2026-10-21 (see above). Original text: update modeling skills and MODELING_PROCESS to record the promised execution route and evidence for affected behavior; generated model changes need `sysml-codegen check` evidence before claiming readiness; missing codegen means generation is unverified, not successful; research-only or unrelated work does not require irrelevant generation runs.
2. Preserve authorized native-only scope and existing owner amendments. When later work requires generation, make the parked seam and first compatibility probe explicit. Changes to a promised route or reserved gate require the applicable owner decision; routine implementation and already-authorized native scope do not require repeated approvals.
3. For new execution-sensitive structural patterns, cite an admitted tested pattern or probe the unresolved capability early. Use `kerml-expert`/`sysml-expert` for unresolved semantics and `syside-expert` for API questions when consultation can resolve the uncertainty. Do not make a standing specialist roster or consultation for every routine binding edit an acceptance gate. Roles read the hazard register and the modelling guide's generator limits but still verify uncertain claims.
4. Ship an upstream-findings starter as a **user-owned project document**, preserving populated records on re-init. `/record-learning` gains a Toolkit category and links approved learnings to findings with evidence, affected versions and disposition. Keep existing approval/curation behavior. Do not silently copy or overwrite owner evidence or auto-file upstream messages.
5. Raw-learning review names the hazard register and the modelling guide's generator limits as formalization destinations. A semantics surprise must have a guidance disposition even if its defect premise is corrected or its support item stays open.
6. Propose a Context A Change Coordination line requiring a generator capability change to include its guidance and hazard disposition in a coordinated merge. Editing CLAUDE.md remains a separately reviewed deliverable; this epic does not silently alter it.

**Success Criteria**: shipped-text tests cover route-aware evidence and scoped expert routing. Fresh and repeated init preserve the target and populated findings. The installed MODELING_PROCESS/MODELING_GUIDE and skills describe the gate; no nonexistent generated plan template is assumed.

**Deliverables**: skill/role/template updates, user-owned findings starter and tests; proposed CLAUDE.md coordination change.

## Epic Strategy

- 2026-10-21: ADR 0004 replaces the strategy for Items 1-3 below (there is no shared profile to merge first). Remaining order: `retire-subset-profile` merges with Item 2b (sysml-codegen first), then Item 5, then the rest of Item 6.
- Corrected Item 4 can start independently. It addresses a demonstrated silent-value hazard, not the only possible silent failure.
- Items 1 and 2 begin with inventory and boundary design together. Re-estimate and resolve policy decisions before implementing the shared screen.
- Merge companion facts/profile first, then compatible codegen integration with explicit version and snapshot behavior. Keep temporary skew fail-closed and test both directions.
- Items 3 and 5 consume the agreed contract; executable-example completion depends on Item 2 (2a for conformance evidence, 2b for `check`). Item 6 integrates the final behavior.
- At each relevant audit, reuse pinned regression evidence where still applicable and rerun affected checks. Completion requires confirmed baseline categories, consumer expectations consistent with D1, independent boundary fixtures, full read-only check parity, D3 guidance coverage and honest reporting of exclusions/unverified scope.

## Dependencies and related work

- SysIDE 0.8.4; existing shared facts and executable-profile contracts; codegen live/snapshot authority, certifiability and generation preparation APIs.
- Proposed absorption: GENERATOR-SUBSET-PATTERNS. Item 1 reconciles **all** PUSH-DOWN profile rows and identifies which are absorbed or remain explicit gaps.
- Adjacent: L6-LIBRARY-ALIAS-SOURCE and DOCS-DOTTED-PATH-BOUNDARY; account for their effect on claims without automatically expanding scope.
- Support changes such as CALCDEF-GATE-IMPLEMENTATION and SCALAR-FUNCTION-VOCABULARY require reviewed guidance updates (the three structural limits, examples), not an assumption that current exclusions are permanent. With the copy gone (ADR 0004) they need no agentic-mbse rule change.

## Risks

| Risk | Mitigation |
|---|---|
| Shared policy duplicates occurrence interpretation | Reuse/extract neutral effective facts; test inherited, specialized and template contexts |
| Conformance becomes circular | Exercise underlying generator decisions with the screen bypassed; mutation-test detectors |
| Annotation coverage is mistaken for semantic completeness | Per-condition witnesses and explicit ownership for non-profile public checks |
| Snapshot route bypasses new decisions | Authority/compatibility design and live/replay parity tests |
| “Check passed” overstates readiness | Use the actual read-only preparation path; bound runtime and environment claims |
| Native projects receive contradictory errors | Audit legacy checks and distinguish native correctness, capability and check failures |
| Guidance exemptions hide regressions | Stable example identities and reviewed exemption manifest, not count alone |
| A rewrite changes safety or numerical meaning | Preservation evidence and explicit limitations alongside each remedy |
| Cross-repository evidence drifts | Pin revisions and imported package identity; use isolated reproducible fixtures |

## Owner decisions and remaining questions

D1, D2 and D3 were approved by the owner during the 2026-10-15 discussion. Other design decisions listed below remain open.

- **D1 — Approved: positional findings.** Block new mismatches and warn on explicitly pinned legacy cases until migration. Fusion-tea migration is separate authorized work, not a prerequisite for accepting this toolkit check. Legacy warning acceptance does not certify cross-route semantic parity.
- **D2 — Approved: full candidate investigation.** Inspect and classify all 500 candidate sites in the recorded inventory (441 codegen, 59 agentic-mbse), reconciling additions and removals at the implementation revision. Account for each site as in scope, already handled elsewhere, or explicit follow-up, with evidence and ownership. Implement only the scoped shared capability rules; this does not require 500 rules or recoding every exception.
- **D3 — Approved: guidance coverage.** Require executable or exact expected-negative evidence for every generated-use recommendation and remedy (100% of the identified inventory), while retaining justified pure teaching fragments.
- **2026-10-21 — Retire the copy; guidance plus an early `sysml-codegen check`.** [AGENT] (ratified by owner, 2026-10-21). The owner's words: "Ok go with your recommendation. implement it, and document it." The recommendation is section 6 of the architecture review (sysml-codegen `.project/research/2026-10-21-generator-check-architecture-review/index.html`). This is an approved agent recommendation, not an owner-originated decision, so it is challenged by re-deriving against ADR 0004's Why. It rests on two agent assumptions stated to the owner and not contradicted: a project that has parked generation still runs one non-blocking early check, and the dc3 incident cost the owner little time. It supersedes ADR 0001, whose owner choice "A (ii)" was between ownership options for the copy; not having a copy was never one of the options offered.

Other decisions remain:

1. Approve shared capability-policy ownership and the fact/decision/consumer boundary after Item 1's design. ADR 0007 alone is not that decision. Moot 2026-10-21: there is no shared capability policy (ADR 0004).
2. Confirm unset-target behavior and blocking policy for exclusions/omissions. Proposed: no generated-readiness claim when unset; keep check failures distinct and visible.
3. Decide String metadata policy using the concrete fixtures; positional-use severity and legacy handling are covered by D1.
4. Approve proposed absorption and disposition of remaining capability gaps. Current refusal does not imply permanent exclusion.
5. Review the CLAUDE.md coordination proposal separately when its exact text is ready.

## Timeline

Re-estimate after the capability inventory, ownership decision and snapshot/preparation design. Retain six delivery items, with incremental acceptance evidence; do not use the original ten-day estimate as a completion constraint.

## Product-Lens

Not yet run.
