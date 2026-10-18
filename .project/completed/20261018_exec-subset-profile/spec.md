# Spec: Executable-subset capability inventory and shared profile (EXEC-SUBSET-CONTRACT Item 1)

**Status:** Implementation Complete (plan Phases 1–11 done, 2026-10-18; awaiting audit and owner review of R3); revised after spec review, 2026-10-15
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

One fact shapes the whole contract. **The generator refuses a shape in a context, not a shape everywhere.** The same binding is refused inside an instantiated part and never examined inside a part def nobody instantiates. The same `max(a, b)` is refused as an attribute value and becomes a handwritten stub as a calc def's result. A rule that ignores context will refuse models the generator admits.

The governing obligation, from the epic's Item 1 objective `[INHERITED: epic]`: define and implement the structural contract **without duplicating model interpretation and without broadening current refusals accidentally**.

## Success Criteria

Each criterion names the artifact or test that proves it. "Pinned" means sysml-codegen `b5663c07e987a892e27d21e68cec40d0656574ee`, dc3 `808464df…` (baseline) and `60b44d53…` (repaired), SysIDE 0.8.4, with the imported package versions recorded in the evidence. A "probe" is a read-only run of the pinned generator on one small fixture in an isolated temp tree (see Known Requirements → Evidence bar).

**Inventory and site account**

- [x] **Site account is total over the scanner's recognized forms.** A machine-readable site account has exactly one row per candidate site the scanner recognizes in sysml-codegen at `b5663c07` and in agentic-mbse at Item 1's final implementation revision (so sites Item 1 itself adds are counted). Each row carries a stable site ID, a D2 disposition (`in scope` / `handled elsewhere` / `explicit follow-up`), an evidence pointer and an owner. A recorded reconciliation run rescans both trees and reports zero unaccounted sites and zero rows without a site.
- [x] **Sites and matrix rows are joined.** Every `in scope` site names the matrix row that covers it, and the rule record when that row is a shared rule. Every matrix row lists its sites, or states that it has none (a silent omission has no raise site). Every `explicit follow-up` site states its owner and the coverage limitation it leaves, the same as a deferred matrix row.
- [x] **Count reconciliation is explicit.** The evidence states the final codegen and agentic-mbse site counts against the recorded 441 / 59, and lists every added or removed site by ID with its cause. A count difference without an itemized cause fails the criterion.
- [x] **Blind spots are listed, not implied.** The account names the scanner revision and the forms it recognizes, and lists its known blind spots. The list includes at least: silent omissions (no raise site exists), computed codes beyond the resolver, unrecognized exception classes or helpers, and unproven public reachability.
- [x] **The five computed reason sites are closed.** A pytest test exercises every reason the five computed sites in `executable_profile.py` (prototype citation `:542, :597, :660, :711, :813`, re-located at the implementation revision) can emit and asserts each is a member of `REASON_CODES`. No enum conversion is introduced for this purpose.

**Capability/refusal matrix**

- [x] **Every named case has a matrix row.** The matrix has a row for each of: ES-001 to ES-012, self-binding, all ten `PUSH-DOWN-*-PROFILE-*` backlog rows, indexed references, deep-qualified wiring, and `L6-LIBRARY-ALIAS-SOURCE`. Every dc3 T-001 item B1–B9 and every dc3 upstream finding U1–U7 is cross-referenced from exactly the rows it maps to, per the mapping below. A reviewer can check this against a fixed list in the evidence.
  - dc3 sources: `work/orchestration/goals/study-ready-baseline/evidence/T-001-blocker-inventory.md` (B1–B9, models at `808464d`) and `.project/active/toolkit-upstream-findings.md` (U1–U7, observed 2026-10-13 at codegen `b5663c07`).
  - The two lists overlap; they are not 16 separate refusals. U1 = B1 (ES-001). U3 = B7 (ES-010). U4 = B4, B5 and B6 plus `min`/`max` (ES-005, ES-006). U7 = B9 (ES-011).
  - Three upstream findings have no B number: U2 nested named subsets (ES-008), U5 a constraint binding a calc usage's input (ES-002), U6 composition by usage subsetting (ES-009). Their evidence is dc3 session-scratch prototypes (`proto4nest`, `proto3`, `conv`); only U2 has a committed reproduction (`T-002-prototype/models.diff` P8).
  - U7/B9 is not a confirmed refusal. A T-001 worker reported it; the coordinator did not reproduce it, and dc3 already uses the `out attribute` form. Its row records `unconfirmed`, never `refused`.
  - B8 is two distinct profile outcomes, 4 `NON_NUMERICAL` and 4 `MALFORMED_NUMERICAL` (`block_non_numerical_containment`). The B8 row keeps them apart.
  - B2's T-001 attribution is wrong and the row must not repeat it. T-001 says the `Real[0..*] ordered nonunique` calc input is refused by codegen's multiplicity expansion. That expansion runs only on part usages (see ES-004), and the retained neighbor `es003_neighbor_ordered_param_scalar_arg` declares exactly that input, binds a scalar, and generates. The refused element is the sequence actual (ES-003).
  - U8 (positional binding) is not in U1–U7 and belongs to Item 4. The matrix points to Item 4 and does not classify it.
- [x] **The binding-source classifier is fully placed.** The matrix places every outcome of the generator's one binding-source classifier: literal (admitted), single reference (admitted), self-binding (`SI_SELF_BINDING`), indexed reference (`SI_INDEXED_SOURCE_UNSUPPORTED`, refused earlier and model-wide by the expression inventory), and any other expression (`SI_EXPRESSION_SOURCE_UNSUPPORTED`). The self-binding row states how it relates to agentic-mbse's existing `L2_SELF_NAMED_BINDING` check (`validation/level2_structure.py:343`).
- [x] **Every row is classified and owned.** Each row names exactly one class: shared rule, codegen-specific check, advisory/omission policy, separately tracked gap, or evidenced internal invariant. Each row also states its contexts, outcome, evidence status and owner. Every row that is not implemented in Item 1 states its owner and the coverage limitation it leaves.
- [x] **Matrix and records agree.** A pytest test asserts that every shared-rule matrix row names an existing rule record, and every rule record appears in the matrix. The test keeps passing after the item folder is archived.

**Rule records and evaluator**

- [x] **Records are complete.** A pytest test asserts every rule record carries all fields required below (ID, refused contexts, admitted contexts, outcome, fact requirements, remedy with semantic limits, working-example fixture, documentation anchor, evidence status), and that every reason ID it can emit is in a closed, runtime-validated vocabulary.
- [x] **Every refusal has a probe record.** For every (shape, context) pair a rule can report as `refused`, the evidence holds a probe record showing the pinned generator refusing that shape in that context. A test asserts the evaluator cannot emit `refused` for a pair without one. A prototype run counts only where its fixture matches the stated context, and the record says which prototype run it reuses.
- [x] **Every refused shape has an admitted-context probe.** For each refused shape, at least one probe shows the generator admitting the same shape in a context the rule says is admitted (or omitting or excluding it there; Change Log 2026-10-18, audit S1). The minimum set: the ES-003/ES-012 binding inside a part def that is never instantiated; the same for an ES-007 BLOCK predicate; `max(a, b)` as a calc def's result expression (ES-005); a conditional as a calc def's result expression (ES-006); an ordered or ranged multiplicity on an attribute usage (ES-004). Where the probe shows the generator refusing after all, the rule's contexts are corrected before it can emit `refused` there.
- [x] **Each implemented rule has refused and admitted fixtures in agentic-mbse.** For each rule the evaluator implements, pytest fixtures mirror its probes: at least one refused case and the admitted-context cases above, with the evaluator's outcome on each asserted. The prototype's admitted neighbors carry over and stay admitted: part-owned assert (ES-001); ordered nonunique input bound to a scalar and exact `[1]` ordered input (ES-003); uninstantiated template and exact redefinition (ES-004); explicit fixed-arity multiply (ES-005); arithmetic `min` identity (ES-006); numeric `and` (ES-007); numeric value (ES-010); a plain reference actual (ES-012).
- [x] **Roots are reported and generator-equivalent by default.** A pytest test asserts the default root set equals the generator's root rule on fixtures with nested, package-level and part-def-owned part usages, and that the result always lists the roots used. A second test passes a widened root set and asserts that findings reachable only from the extra roots are not `refused`. A third passes a narrowed set and asserts the result reports incomplete scope.
- [x] **Baseline run accounts for B1–B8.** One evaluator run over the dc3 baseline tree, with default roots, reports every confirmed category B1–B8 with locations and rule IDs. The evidence records the roots used, declaration counts and occurrence counts separately, and the deduplication applied. — **Met with recorded limit, accepted by owner (2026-10-18):** [AGENT] (ratified by owner) B8 reports `unconfirmed` because all six constraints are calc-usage-owned and the generator refuses them first under B1; a "shadowed by another refusal" presentation label is an Item 3 design point.
- [x] **Repaired run refuses nothing.** One evaluator run over the dc3 repaired tree, which generates at `b5663c07`, with default roots, reports zero `refused` findings. Any `unverified` result is itemized with its cause, and fails the criterion unless the owner accepts that recorded limit. Omissions are reported and counted (the prototype saw 30 String omissions).
- [x] **The generator's accepted corpus still passes, as a regression floor.** This run proves that Item 1 does not refuse the generator's known-good models. It does not prove the rules are not overbroad: the 14 snapshot fixtures contain no function invocations, no `ordered` or `nonunique` multiplicity and no range multiplicity, so the admitted-context probes above carry that proof.
  - The corpus is sysml-codegen's owner-accepted batch at `b5663c07`, `tests/fixtures/v6_recapture_batch/batch.json`: 37 fixtures. The manifest holds 14 snapshot records (the fixture elaborates and projects) and 23 typed refusal records with code lists. The batch README says 15 and 22; the manifest governs, and the evidence states the counts it read.
  - On the 14 snapshot fixtures, a run with default roots shows zero `refused` findings. Any `refused` finding there is an R2 stop.
  - On the 23 refusal fixtures, a recorded code list is a lower bound, because the expression inventory stops at its first error. An evaluator `refused` finding whose code is in the list passes. One whose code is not in the list needs a probe record for its (shape, context); it is not an R2 stop.
  - The snapshot fixtures prove admission through elaboration and projection, not full generation; the evidence says so.
- [x] **Failure cannot look clean.** Pytest tests inject (a) a fact-extraction failure for one rule, (b) an enumeration failure for the model scope, and (c) missing occurrence evidence for an occurrence-dependent rule. In each case the result carries a structured `unverified` entry with rule ID, context, safe location and cause; unrelated rules still report their findings; and the overall assessment is not complete/clean.
- [x] **Output is deterministic.** A pytest test evaluates the same model twice and with permuted document order and asserts identical, ordered output.
- [x] **No consumer coupling.** A pytest test asserts three things:
  - no module in `agentic_mbse` imports `sysml_codegen`;
  - no reason ID or rule ID matches `SI_[A-Z_]+` or names a consumer type such as `ElaborationCode` or `ReadinessCode`;
  - in the packaged rule data, `SI_*` strings appear only in fields designated as evidence (for example a probe record's observed code), never in a reason, outcome or decision field.
- [x] **Consumer output is unchanged.** `agentic-mbse validate` output on the existing test fixtures and both dc3 trees is unchanged by Item 1 (diffed before and after).

**Close-out**

- [x] **R3 proposal is recorded.** A disposition table proposes, for each section of GENERATOR-SUBSET-PATTERNS and each remaining capability gap, its destination item or follow-up. It is marked proposed until the owner approves.
- [x] **Re-estimate is recorded.** Item 1's close-out records re-estimated effort for Items 1 and 2, as the epic requires after the inventory.
- [x] **Repository checks pass.** `uv run pytest tests/`, `uv run mypy src/` and `uv run ruff check src/ tests/` pass. Evidence states which checks needed the SysIDE license and which were skipped. *(Met under the orchestrator's definition of green, plan § Standing Rules: no new failures against the pre-existing baseline, Item 1's files clean. Run at `ce0ad1ff` after the audit fixes: 3507 passed, the same 3 environment failures, ruff 118, mypy 97 in 19 files; `evidence/repository-checks.md`.)*

## Known Requirements

### Ratified decisions

These bind Item 1. They are agent recommendations the owner approved, so they are challenged by re-deriving against their recorded reasoning, not relitigated casually.

- **[INFERRED]** (ratified by owner 2026-10-15; epic § Owner decisions D2; the orchestration brief records D1–D3 as owner decisions) D2: inspect and classify all 500 candidate sites in the recorded inventory (441 codegen, 59 agentic-mbse), reconciling additions and removals at the implementation revision. Each site is in scope, already handled elsewhere, or an explicit follow-up, with evidence and ownership. Implement only the scoped shared capability rules; this does not require 500 rules or recoding every exception.
- **[INFERRED]** (ratified by owner 2026-10-15, `briefs/align.md`) The full D2 site account is built in Item 1 at the pinned revision, because rule boundaries depend on it. Per-site stable codes and mutation tests remain Item 2.
- **[INFERRED]** (ratified by owner 2026-10-15, `briefs/align.md`) Item 1 does not claim generator-verified rules. Each rule record carries an evidence status. Item 1 tests verify the agentic-mbse evaluator and facts against agentic-mbse fixtures; Item 2 adds the independent conformance corpus.
- **[INFERRED]** (ratified by owner 2026-10-15, `briefs/align.md`) "Inventory complete relative to the pinned generator surface" means complete relative to the scanner's recognized forms plus an explicit list of known blind spots.

### Boundaries

- **[HARD]** agentic-mbse never imports sysml-codegen or its types. sysml-codegen already depends on agentic-mbse, so the reverse import would make a cycle. sysml-codegen's ADR 0007 records the one-way dependency as an active invariant (`~/src/sysml-codegen/.project/adr/0007-agentic-mbse-owns-neutral-facts-codegen-owns-rendering.md`).
- **[INHERITED: epic, Design principle 1 and Item 1 scope 2]** The shared decision vocabulary uses neutral reason IDs. It does not use `ElaborationCode` or any consumer-specific identifier. Codegen keeps its own diagnostic mapping, which may be one-to-many.
- **[INFERRED]** (spec review L3-6) Generator code names (`SI_*`) appear in Item 1's artifacts only as evidence: in a probe record's observed code, an evidence field of a rule record, or evidence files. They never appear in reason IDs, rule IDs, outcomes or decision logic. Reason: the corpus check and probe records need the mapping, and the coupling rule forbids it in the vocabulary; this line keeps both.
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
- **[INFERRED]** (spec review L3-1) "Applicability and context" is two explicit lists. The refused contexts say where the pinned generator refuses the shape: for example, inside a scope that is instantiated, in an attribute value expression, or on a part usage reachable from a root. The admitted contexts say where the same shape is admitted, never examined, or turned into a handwritten stub (`MANUAL_REQUIRED`). A rule reports `refused` only in a listed refused context.
- **[INHERITED: epic, Item 1 scope 3]** Outcomes distinguish `refused`, `admitted`, `excluded`, `omitted` and `unconfirmed`. Missing evidence produces an `unverified` check result, which is a separate thing from any outcome.
- **[INFERRED]** `unconfirmed` is the outcome for a (shape, context) a rule recognizes but has no probe record for. That includes everything known only from reading the generator's code. Reason: reporting it `refused` would risk R2, and reporting it `admitted` would be a silent miss.
- **[INHERITED: epic, Item 1 scope 3 and Design principle 2]** `executable_profile.py` stays the authority for constraint-predicate eligibility, including the BLOCK, NON_NUMERICAL and UNASSESSED distinctions. Its 27-member `REASON_CODES` and the membership check in `EligibilityDiagnostic.__post_init__` are reused, not duplicated. New structural decisions reference it where it applies.
- **[INFERRED]** Any new reason IDs live in a closed vocabulary that is enumerable without running the evaluator and validated at construction, matching the `REASON_CODES` pattern. Reason: the epic's inventory and Item 2's mapping both depend on enumerating every possible reason.
- **[INFERRED]** The rule records are machine-readable data inside the agentic-mbse package, readable without SysIDE. Reason: Item 2 pins them and Item 5 renders `docs/patterns/generator-subset.md` from them, so they cannot live only in a `.project` document.
- **[INFERRED]** The capability decisions carry their own version identifier, separate from any fact schema version. Reason: this is the existing split between `PROFILE_SEMANTIC_VERSION` and `CONSTRAINT_FACTS_SCHEMA_VERSION`, and Item 2 must pin the decision version for snapshot authority.

### Evidence bar

- **[INFERRED]** (spec review L3-2, L1-2) Reading the generator's code is enough to make a family a rule and to design its facts. It is not enough to emit `refused`. The evaluator emits `refused` for a (shape, context) only when a probe at `b5663c07` has observed the generator refusing that shape in that context. Until then, that pair reports `unconfirmed`. Reason: a code citation shows a branch refuses, not that a shape reaches it in a given context, and that reachability is where R2 risk lives. The spec's own earlier ES-001 citations had the two branches swapped. Probes are cheap: the prototype oracle (`01-codegen-oracle.py`) already runs fixtures through the pinned generator. Because code reading alone can no longer produce a refusal, this bar needs no R2 decision.
- **[INFERRED]** Probes run read-only against the pinned trees, in isolated temp directories, never inside a sibling checkout. Each probe is retained as evidence: the fixture, the command, the generator exit and codes, and the exact imported package identity (sysml-codegen revision, agentic-mbse revision, SysIDE version). A prototype run counts as a probe only where its fixture matches the stated context, and the record says which run it reuses.

### Roots

- **[INFERRED]** (spec review L3-3) The evaluator's default roots reproduce the generator's root rule. A root is every user-model part usage whose owner is not a part def or a part usage, so in practice every package-level part usage (`elaboration/occurrence.py:916-923`). The rule is recorded with that citation. Reason: a refusal that depends on instantiation is only true relative to what the generator instantiates.
- **[INFERRED]** A caller may pass an explicit root set. The result always reports the roots used.
  - A narrower set is allowed and the result reports incomplete scope.
  - A wider set is allowed, but a finding that is reachable only from a root outside the generator's set reports `unconfirmed`, not `refused`. Design may choose an equivalent label, provided it is distinct from `refused` and honest about why.
  - When the roots cannot be computed, root-dependent rules report `unverified`.
- **[INFERRED]** The baseline, repaired and corpus runs use the default roots and record them.

### Which candidates become evaluator rules

A family becomes an evaluator rule in Item 1 when two things hold. **[INFERRED]**

- The generator's code shows a refusal branch for the shape, and the contexts that reach it can be stated.
- Its facts can be extracted from shared agentic-mbse facts without a heuristic.

Otherwise it stays a candidate record. A rule still emits `refused` only where the evidence bar above is met; everywhere else it reports `unconfirmed`.

The two tables below apply this to today's evidence. Codegen paths are relative to `~/src/sysml-codegen/src/sysml_codegen/`, at `b5663c07`. "Probe pending" means the shape reports `unconfirmed` in that context until a probe records it.

**Table 1. Boundaries by context**

| Family | Item 1 disposition | Shape | Refused contexts | Admitted or not-examined contexts |
|---|---|---|---|---|
| ES-001 | Rule | Asserted constraint (`definition_typed`, `inline`, `named_usage_reference`) owned by a calc def | Everywhere: a calc def cannot attach a constraint | A non-asserted form owned by a calc def (graded info) |
| ES-001 | Rule | Constraint owned by a calc usage | Wherever the owner-kind check runs; asserted forms observed, other forms probe pending | Not established. For contrast, the same asserted constraint on a part with occurrences is admitted, and on a part def with no occurrences it is graded warning, not refused (`graph.py:290`) |
| ES-002 | Candidate | Constraint binding a calc usage's input | Not established | Binding a calc output (dc3 U5, unretained) |
| ES-003 / ES-012 | Rule (one decision) | Calc or constraint input bound to an expression that is neither a literal nor a single reference, e.g. `(a, b)` or `rate * fuel_code` | The consuming usage's owner is instantiated (part def or part usage with occurrences) or is a package | The owner has no occurrences: the binding is never classified. Literal and single-reference sources |
| Self-binding | Rule (same decision) | Input bound to a reference to itself | Same as ES-003 | Same as ES-003 |
| Indexed reference | Rule (same fact) | Input or value bound to `x#(i)` | Model-wide: the expression inventory refuses it before any instantiation | — |
| ES-004 | Rule | Ordered, nonunique, ranged or unresolved multiplicity | A part usage the generator expands: a root, or a composite user-model part usage reachable from one | Attribute usages, non-composite part usages, and part usages not reachable from a root (templates) |
| ES-005 | Rule, reusing the shared admission | Any ordinary invocation except `NumericalFunctions::sum` | Model-wide at expression-inventory sites: the value expression of any declared feature (including input bindings and `return r = …`) and constraint predicates, instantiated or not | A calc def's bare result expression: the compiler emits a handwritten stub (probe pending) |
| ES-006 | Rule | `if … ? … else` conditional | Same sites as ES-005 | A calc def's bare result expression (probe pending) |
| ES-007 | Mapped to `executable_profile` | Constraint predicate the profile BLOCKs | The constraint usage's owner is instantiated or is a package | The owner has no occurrences (probe pending). NON_NUMERICAL is `excluded`, not refused |
| ES-008 | Candidate | Named subset nested in a named subset | Not established | One level of named subsetting (dc3 U2) |
| ES-009 | Candidate | Composition by subsetting a top-level usage | Not established | Not established |
| ES-010 (omission) | Rule, outcome `omitted` | String-valued attribute, both spellings | — | Dropped from generated output in every observed context |
| ES-010 (refusal) | Candidate unless restated | Non-numeric default reaching a generated entry-point input | Decided at projection; see requirement below | Booleans are coerced, not refused |
| ES-011 | Candidate | Arithmetic on a named calc return result | Not established | — |

**Table 2. Generator sites and current evidence**

| Family | Deciding generator site | Generator code | Observed today | Code-read only |
|---|---|---|---|---|
| ES-001 calc def | `elaboration/elaborate.py:1625`; grading `elaboration/graph.py:247`, `:287-292`; attachment `elaborate.py:759-787` | `SI_CONSTRAINT_UNATTACHED` | Prototype `es001_refused_calc_def_assert` | Non-asserted forms |
| ES-001 calc usage | `elaboration/elaborate.py:802-820` (owner kind not in the map) | `SI_CONSTRAINT_UNATTACHED` | Prototype `es001_refused_calc_usage_assert` | Non-asserted forms |
| ES-002 | `elaboration/occurrence.py:181` ("cannot anchor containment"); 11 other sites share the code | `SI_OCCURRENCE_MISSING` | dc3 U5, session scratch | — |
| ES-003 / ES-012 / self-binding | Classifier `elaboration/elaborate.py:2130-2171`, disposition `:2188-2196`; reached only per scope (`:1195-1235`, `:1322`, `:1337-1360`) | `SI_EXPRESSION_SOURCE_UNSUPPORTED`, `SI_SELF_BINDING` | Prototype `(a, b)` and `rate * fuel_code`, instantiated owner; 20 of the 23 corpus refusal fixtures carry `SI_SELF_BINDING` (to be matched to probes) | Uninstantiated owner |
| Indexed reference | `elaboration/expression_evidence.py:274-276`; also `elaborate.py:2192` | `SI_INDEXED_SOURCE_UNSUPPORTED` | None: no corpus record carries it | Whole row (probe pending) |
| ES-004 | Expansion `elaboration/occurrence.py:812-899`; reach `:916-923`, `:927-942`, `:989` | `SI_MULTIPLICITY_UNSUPPORTED`, `SI_MULTIPLICITY_UNRESOLVED` | Prototype range and unbounded parts | Ordered and nonunique parts; attribute usages |
| ES-005 | agentic-mbse `reference_use.py:395-428`, run by `elaboration/expression_evidence.py:233-324`; mapped at `orchestration/elaborated_pipeline.py:389-396`. Calc body: `extraction/calc_compat_renderer.py:75`, `extraction/expression_compiler.py:285-300` | `SI_EXPRESSION_SOURCE_UNSUPPORTED` | Prototype `product`, `size` | `min`/`max`; calc-body stub |
| ES-006 | agentic-mbse `reference_use.py` (`RESOLVED_TARGET_MISSING`); mapped by default at `orchestration/elaborated_pipeline.py:425` | `SI_EVIDENCE_INCOMPLETE` | Prototype `es006_refused_conditional` | Calc-body behavior |
| ES-007 | `elaboration/elaborate.py:1337-1360` | `SI_CONSTRAINT_BLOCKED` | Prototype `es007_refused_boolean_mixed` | Uninstantiated owner |
| ES-008 | `elaboration/elaborate.py:947` ("incomparable value writers"); 7 other sites share the code | `SI_REDEFINITION_INVALID` | dc3 U2; committed only as dc3 `T-002-prototype/models.diff` P8 | — |
| ES-009 | Not located | `SI_OCCURRENCE_MISSING` | dc3 U6, intermediate scratch run | — |
| ES-010 refusal | `elaboration/project.py:201-218` (`_float_default`) | `SI_RENDERING_COLLISION` | Prototype `es010_refused_string_calc_input` | — |
| ES-010 omission | No raise site | — | Prototype name-based oracle | — |
| ES-011 | Not located | `SI_EDGE_DANGLING` (reported) | Worker report, not reproduced | — |

The expression inventory stops at its first error (`elaboration/expression_evidence.py:249`, `:259-276`), so one run of the generator shows at most one inventory refusal. Probes therefore use one construct per fixture.

### Requirements on specific families

- **[INFERRED]** ES-003, ES-012, self-binding and the indexed-reference row share one generator classifier. The shared contract reproduces it from one binding-source fact with these kinds: literal, single reference, self-binding, indexed, other expression. Whether that is one rule record or several over one fact is a design choice.
- **[INFERRED]** (spec review L3-7) The binding-source fact reuses agentic-mbse's shared helpers wherever the generator's logic already lives in agentic-mbse: `is_literal_node` (`sysml/expression.py:441`), `unit_annotation_value` (`reference_use.py:342`), and the `inspect_reference_uses` count. Self-binding compares the reference path's leaf with the bound formal, which codegen computes from agentic-mbse's `ExactReferenceUse` (codegen `extraction/binding_source.py:88-89`); the shared fact uses the same reading. One piece lives only in codegen: the reference-metatype test (`elaboration/elaborate.py:1115-1118`, `FeatureChainExpression` or `FeatureReferenceExpression`). agentic-mbse cannot import it, so the shared fact must be equivalent, and the probes prove the equivalence.
- **[INFERRED]** ES-005 reuses `reference_use._require_supported_invocation` (`reference_use.py:395`) for callable identity. It does not re-detect callables. Reason: that function already is the generator's callable boundary, so a second detector is the duplicated interpretation the epic forbids.
- **[INFERRED]** The generator reports ES-006 with its generic evidence-gap code. The conditional's branch reference has no exact target, so `inspect_reference_uses` raises `RESOLVED_TARGET_MISSING`. Codegen maps every evidence code it does not name to `SI_EVIDENCE_INCOMPLETE` (`orchestration/elaborated_pipeline.py:425`). Two consequences follow. ES-006 reports `refused` only on a positively recognized conditional shape; any other `RESOLVED_TARGET_MISSING` or `SI_EVIDENCE_INCOMPLETE` stays `unverified`. And the inventory does not classify `SI_EVIDENCE_INCOMPLETE` sites as capability refusals by code alone. Reason: otherwise a real evidence failure would surface as a construct refusal, which Item 1 scope 6 forbids.
- **[INFERRED]** (spec review L2-1) ES-010 is split. The omission side stays a rule with outcome `omitted`: a String-valued attribute, in both spellings, is dropped from generated output, and saying so needs only model facts. The refusal side defaults to a candidate. The generator decides it at projection, by whether a value reaches a generated entry-point input, and ADR 0007 places that output fact in codegen. Design may promote it only by restating it in model terms (the proposed form: a String-valued feature bound to an input of a calc usage whose owner is instantiated) and showing, with refused-context and admitted-context probes, that the restatement matches the projection boundary. Reason: this keeps the useful omission finding without guessing at an output fact the evaluator cannot compute.
- **[INHERITED: epic, Item 1 scope 4]** These families are candidates to refine with fixtures, not universal construct bans. ES-003 describes the actual binding shape and does not ban the parameter declaration.
- **[INHERITED: epic, Item 1 scope 4]** ES-007 keeps Boolean data/output capability, non-numerical exclusion and malformed predicates as distinct decisions. NON_NUMERICAL maps to `excluded`, not `refused`. UNASSESSED never maps to `admitted`.
- **[INHERITED: epic, Item 1 scope 5]** ES-004 uses effective reachable occurrences and their resolved bounds. A typing observed elsewhere, or an exact redefinition elsewhere, does not discharge another occurrence. The prototype's "typed anywhere" heuristic is not carried into production.
- **[INFERRED]** (spec review L3-1) Which usages ES-004 applies to is settled by the code, not open. The generator expands only roots and the composite user-model part usages reachable from them (`elaboration/occurrence.py:916-942`, `:989`). Attribute usages, non-composite part usages and unreachable part usages never reach multiplicity expansion.
- **[INFERRED]** If the design finds that occurrence facts for ES-004 cannot be extracted from SysIDE before elaboration for some context, the rule reports `unverified` for that context and records the limit. It does not fall back to the heuristic and does not report clean. Reason: this is the epic's honesty principle applied to the one rule whose facts are least certain.

### Evaluation scope and result shape

- **[INHERITED: epic, Item 1 scope 5]** Evaluation covers the selected user-model scope, including calc bodies where the capability applies, and excludes the standard library. It distinguishes template from instantiated evidence and specifies declaration/occurrence identity, location fallback, stable ordering and diagnostic deduplication.
- **[INHERITED: epic, Item 1 scope 6 and Design principle 5]** A detector failure produces a structured `unverified` result carrying the rule, the context and a safe location. It never produces a false unsupported-construct finding. An enumeration or extraction failure never produces an empty clean result. Checks whose facts remain available still run.
- **[INFERRED]** `unverified` results carry the closed `SemanticEvidenceCode` cause (`errors.py:25`) when the failure came from shared evidence extraction. Reason: that vocabulary already exists for exactly this, and a second one would duplicate it.
- **[INHERITED: epic, Design principle 5]** The evaluator reports missing prerequisites and the dependent checks left unverified. It does not invent downstream findings or claim exhaustive results when evidence is missing.

### No duplicated interpretation

- **[INHERITED: epic, Item 1 objective and scope 2; Risks row 1]** New decisions reuse the existing shared facts in `reference_use.py`, `hierarchy.py`, `aggregation.py`, `constraint_facts.py` and `expression_facts.py`. Where a rule needs a new fact (the prototype needed assertion owner metatype, sequence actuals, multiplicity bounds and redefinitions, the `if` operator, and String values/referents), it is extracted once, in a shared fact module, and not re-derived inside a decision.
- **[INHERITED: epic, Design principle 1]** Facts, capability decisions and consumer presentation stay separate. Decisions consume explicit facts and emit neutral reasons. L6 owns severity; codegen owns its code mapping.

## Non-Goals

- Codegen integration, `ElaborationCode` mapping, the independent conformance corpus in `tests/conformance/subset_profile/`, detector-disable mutation tests, per-site stable codes, the `check` command, and snapshot/version integration. These are Item 2.
- Reproducing or retiring ES-011, and deciding String metadata policy. These are Item 2 (epic open decision 3).
- L6 wiring, target-specific severity, consumer root defaults, the `execution-target` setting, and the audit of existing L6 checks. These are Item 3.
- The positional-binding check and hazard register. These are Item 4.
- Rendering `docs/patterns/generator-subset.md` and correcting shipped examples. These are Item 5. Item 1 supplies the documentation anchor field only.
- Fixing `L6-LIBRARY-ALIAS-SOURCE`. Item 1 reconciles it in the matrix only.
- Implementing new language support, or relaxing a current generator refusal.

## Open Questions / Deferred to design

- **R1 — owner gate, not decided here.** Who owns capability policy, and where the fact/decision/consumer boundary sits. `[INFERRED]` recommended direction for design to evaluate, from epic Item 1 scope 2: a pure module `sysml/subset_profile.py` (no SysIDE import, like `executable_profile.py`) with `SUBSET_PROFILE_VERSION`, neutral reason IDs, and fact extraction kept separate. The owner approves after design review and before planning (see Next Steps).
  - ADR 0007 is sysml-codegen's `.project/adr/0007-agentic-mbse-owns-neutral-facts-codegen-owns-rendering.md` (active, `[AGENT] (ratified by owner, 2026-07-10)`). agentic-mbse's `.project/adr/` has no ADRs; dc3's and fusion-tea's ADR 0007 are unrelated supersession records.
  - What it settles: facts about the model are computed in agentic-mbse, facts about the output in codegen, and the dependency runs codegen → agentic-mbse only. What it does not settle: which side owns the admit/refuse decision. That is the R1 question, as the epic says.
  - Existing code already blurs that line, and design should account for it. `reference_use._require_supported_invocation` (`reference_use.py:395`) is a capability decision ("only `NumericalFunctions::sum` is supported") living in agentic-mbse's fact layer, and codegen consumes it as its own refusal. `executable_profile.py` is the other precedent, a pure decision module in agentic-mbse.
  - No durable product statement yet records the shared-contract promise, so the approved R1 decision should land as an ADR, and the implemented promise as a `.project/product/` entry at close.
- **R2 — owner gate, standing.** If a probe shows a rule's intended refusal would cover a (shape, context) the pinned generator admits, design halts that rule and asks the owner.
- **R3 — owner gate, proposal only.** Absorption of GENERATOR-SUBSET-PATTERNS and the disposition of remaining capability gaps (ES-002, ES-008, ES-009, ES-011, the ES-010 refusal side, the `unconfirmed` pairs, and the ten PUSH-DOWN rows). Item 1 records a proposed disposition; the owner approves it. Current refusal does not imply permanent exclusion.
- **Where the inventory, site account and probe records live.** Design picks a location the matrix/record cross-check test can read after the item folder is archived (package data or `tests/` data), and where the human-readable matrix lives.
- **How new reason IDs relate to `REASON_CODES`.** Extend the existing set, or add a sibling closed set with the same runtime validation. Design decides; either must stay enumerable and validated.
- **Root input shape.** How a caller passes roots and how the wider-than-generator label is spelled. The default rule is settled above; consumer defaults belong to Items 2 and 3.
- **Deduplication and identity policy.** How one declaration reached through several occurrences is reported, and which identity (declaration vs occurrence) each rule keys on.
- **ES-004 fact feasibility.** Whether effective reachable occurrences and resolved bounds can be extracted from SysIDE before elaboration in all contexts, and where the `unverified` boundary falls if not.
- **Probe scope beyond the minimum.** Whether design probes ES-002, ES-008 and ES-009 to promote them to rules (each has a dc3 observation but no retained fixture, and its code is shared by other sites), and which other code-read pairs to probe so they stop reporting `unconfirmed`.
- **Corpus manifest discrepancy.** sysml-codegen's batch README says 15 snapshots and 22 refusals; its `batch.json` at `b5663c07` holds 14 and 23. The corpus criterion uses the manifest. Reporting the mismatch upstream is an Item 2 or owner call, not an Item 1 edit.
- **Scanner hardening.** Whether Item 1 reuses the prototype scanner (`02-inventory.py`) as is or hardens it, and how its recognized forms are recorded.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_executable-subset-contract.md` (Item 1; boundaries Items 2–5; D1–D3)
- **Origin record:** `.project/backlog/item_generator-subset-patterns.md` (read through the epic's corrections)
- **Align record:** `.project/active/exec-subset-profile/briefs/align.md`
- **Spec review:** `.project/active/exec-subset-profile/spec-review.md` (verdict Revise; resolutions recorded there)
- **Prototype evidence:** `.project/concepts/convince-me-exec-subset/` (`template.html`; `evidence/01-README.md`, `evidence/02-README.md`, `evidence/01-fixtures/`, `evidence/01-codegen-oracle.py`, `evidence/02-inventory.csv`, `evidence/02-classification.csv`) — feasibility observations only
- **PUSH-DOWN profile rows:** `.project/backlog/BACKLOG.md` (`PUSH-DOWN-EXPR-PROFILE-*`, `PUSH-DOWN-HIER-PROFILE-*`, `PUSH-DOWN-AGG-PROFILE-*`) and `L6-LIBRARY-ALIAS-SOURCE`
- **Code extended:** `src/agentic_mbse/sysml/executable_profile.py`, `reference_use.py`, `expression.py`, `hierarchy.py`, `aggregation.py`, `constraint_facts.py`, `expression_facts.py`; `src/agentic_mbse/errors.py` (`SemanticEvidenceCode`); `src/agentic_mbse/validation/level2_structure.py` (`L2_SELF_NAMED_BINDING`, reconciled in the matrix)
- **Cross-repository sources (read-only):** dc3 `work/orchestration/goals/study-ready-baseline/evidence/T-001-blocker-inventory.md` and `.project/active/toolkit-upstream-findings.md`; sysml-codegen at `b5663c07`: `tests/fixtures/v6_recapture_batch/{batch.json,README.md}`, `.project/adr/0007-agentic-mbse-owns-neutral-facts-codegen-owns-rendering.md`, and the generator sites in Table 2
- **Product-lens:** `.project/active/exec-subset-profile/product-lens.md`
- **Design:** `.project/active/exec-subset-profile/design.md` (to be created)

---

## Change Log

- **2026-10-15 — SA-1, proposed, not applied `[AGENT]`.** Origin: design revision 2, following design review S1.
  - **Change.** The criterion "Every refused shape has an admitted-context probe" would gain one exception. A shape that the pinned generator refuses in every context the rule can compute may carry a `no_admitted_context` statement instead. The statement must give the generator citation and cite refused probes covering each computable context.
  - **Likely users.** An asserted constraint owned by a calc def (`elaborate.py:1625`). Possibly `indexed-reference`, if its calc-result probe refuses.
  - **Why.** Without the exception, the criterion cannot be met for shapes the generator refuses everywhere.
  - **Decision.** `[AGENT] (accepted by orchestrator, 2026-10-18)`. Applied: the record loader enforces it (`subset_profile.py`, `_shape`), and one shape uses it (`calc-owned-assertion/asserted_constraint`). Recorded in the plan's Settled Inputs and the design. Audit S5 found this entry still read "pending"; corrected 2026-10-18.
- **2026-10-18 — Non-refused partner, accepted `[AGENT]` (orchestrator, audit S1).** The criterion "Every refused shape has an admitted-context probe" is met by a certified probe of any context whose outcome is not refused: `admitted`, `omitted` or `excluded`. Reason: the partner probe proves the rule is not a universal ban, and a certified omission proves that as well as an admission. Applied so the three site rules' calc-usage bare-result context, which the generator silently drops, is recorded as `omitted` instead of an unqualified `admitted`. A deviation from design invariant 3, recorded in the plan.

---

**Next Steps:** `/_my_design`, then `/_my_design_review`. Then **owner gate R1**: the design records the capability-policy ownership decision and the fact/decision/consumer boundary, and the owner approves it with a date before `/_my_plan` starts. The spec review says a fresh spec review is not needed after these edits; it is enough to verify that the must-fix items landed.
