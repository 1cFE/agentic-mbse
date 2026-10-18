# R3 disposition table — PROPOSED, owner approval required

> **Status: PROPOSED — owner approval required.** R3 is owner-only (`briefs/align.md`). Every destination below is an `[AGENT]` proposal from EXEC-SUBSET-CONTRACT Item 1's results. Nothing here is decided until the owner approves it, row by row or as a whole. Item numbers are the epic's (`.project/backlog/epic_executable-subset-contract.md`): Item 2 codegen conformance and readiness, Item 3 L6 integration, Item 4 positional binding, Item 5 rendered guidance, Item 6 integration.

Sources: matrix `evidence/matrix.md`; site account `tests/fixtures/subset_profile/inventory/site_account.csv`; probes under `tests/fixtures/subset_profile/probes/`; acceptance runs `evidence/acceptance.md`. "Reproduction" is the Phase 6 or Phase 7 probe result at sysml-codegen `b5663c07`.

## 1. GENERATOR-SUBSET-PATTERNS, section by section

The item (`.project/backlog/item_generator-subset-patterns.md`) was absorbed into the epic on 2026-10-14 pending owner approval. Item 1's evidence per section:

| Section | What Item 1 established | Proposed destination |
|---|---|---|
| § 1 Positional binding of calc-usage inputs | Not probed (U8 is outside U1-U7; the matrix points it to Item 4 and does not classify it) | **Item 4**, as absorbed |
| § 2 table: `assert constraint` owned by a calc def or calc usage | Rule `calc-owned-assertion` (ES-001), probe-observed refused under both owners; part-owned assert admitted (control) | Contract done (Item 1). L6 reporting **Item 3**; pattern doc **Item 5** |
| § 2 table: Boolean attributes / Boolean constraint inputs | Rule `constraint-predicate` (ES-007): BLOCK refused where the owner is instantiated or a package, admitted where not; NON_NUMERICAL excluded | Contract done. **Item 3**, **Item 5** |
| § 2 table: `product`, `size`, `min`/`max`, `if … ? … else` | Rules `invocation-callable` (ES-005) and `conditional-expression` (ES-006): refused at every inventory site, admitted (dropped) in a calc usage's bare result | Contract done. **Item 3**, **Item 5**; vocabulary widening stays sysml-codegen [SCALAR-FUNCTION-VOCABULARY] |
| § 2 table: `Real[0..*] ordered nonunique` calc inputs | The refused element is the sequence actual (rule `binding-source`, ES-003), not the declaration; the declaration bound to a scalar generates (control) | Contract done. **Item 3**, **Item 5** (the pattern doc should say the actual, not the declaration, is refused) |
| § 2 table: `[*]` collections instantiated by designs | Rule `part-multiplicity` (ES-004): refused on expanded part usages, admitted on templates; all 15 dc3 library `[*]` usages found | Contract done. **Item 3**, **Item 5** |
| § 2 table: named subset nested in a named subset | Reproduced (ES-008), but only when the nested subsets each redefine a value; plain nesting generates. No rule | **Item 2** (conformance corpus and a rule decision); pattern doc **Item 5** with the narrower boundary |
| § 2 table: composition by subsetting a top-level usage | Reproduced (ES-009). No rule | **Item 2**; **Item 5** |
| § 2 table: String design attributes | Rule `string-value-omission` (ES-010): omitted in both spellings; the refusal side is a gap (below) | Omission: **Item 3** (L6 should flag both spellings consistently), **Item 5**. Policy: **Item 2** (epic scope 6) |
| § 2 Enforce: L6 reports every row at once | The evaluator reports them in one run (dc3 baseline: B1-B7 found, B8 `unconfirmed`) | **Item 3** |
| § 3 Notes for evaluator authors (SysIDE 0.8.4) | Not in Item 1's scope | **Item 5** |
| § 4 Process gap: expert agents not consulted | Not in Item 1's scope | **Item 6** |

## 2. Remaining capability gaps

| Gap | Reproduction / evidence | Proposed destination |
|---|---|---|
| **G1** part redefinition that omits bounds expands to one occurrence and loses `ordered` (design D14 a) | Control probe: generates one unindexed occurrence `fx__rack__servers__t__r`; the port mirrors it | **Item 2 / owner**: a generator-correctness question; the contract keeps mirroring until decided |
| **G2** usage-level override of a definition-owned referenced bound is ignored (D14 b) | Code-read in spike F1; not probed in Item 1 | **Item 2 / owner**, with a probe first |
| **Calc usage bare result expression is silently dropped** | Seen in the three `other_expression_site` record probes: the expression produces nothing, no diagnostic (matrix CALC-USAGE-BARE-RESULT-DROP) | **Item 2** (epic scope 5: every known silent-loss family gets a presence/absence test); guidance warning **Item 5** |
| **Calc def whose result is a bare expression is refused** (`SI_EVIDENCE_INCOMPLETE`, "zero output attributes") | Reproduced with arithmetic and `max` (matrix CALC-DEF-BARE-RESULT). The design expected a handwritten stub; none observed | **Item 2**: decide whether a rule (or the site rules' `calc_result_expression` context) records it as refused, with its own code |
| **ES-010 refusal side** (non-numeric default reaching an entry-point input, `SI_RENDERING_COLLISION` at projection) | Reproduced on one path (String bound to a calc input of an instantiated owner). On that model the contract reports the String `omitted` while the generator refuses | **Item 2** (design D11: entry-point membership is a codegen output fact) |
| **ES-002** constraint binding a calc usage's input (`SI_OCCURRENCE_MISSING`) | Reproduced. The raise site (`occurrence.py:180`) is wider than the shape | **Item 2** (conformance corpus; rule candidate once its contexts are stated) |
| **ES-008** nested named subsets (`SI_REDEFINITION_INVALID`) | Reproduced in one of five spellings | **Item 2** |
| **ES-009** composition by subsetting (`SI_OCCURRENCE_MISSING`) | Reproduced. The raise site (`elaborate.py:2345`) is wider than the shape | **Item 2** |
| **ES-011** arithmetic on a named calc return (`SI_EDGE_DANGLING`, reported) | Not probed (design D12); raise site not located | **Item 2**: reproduce or retire (epic scope 6) |
| **DEEP-QUALIFIED-WIRING** | Codegen's corpus refusal record `deep_cross_scope_probe`. The contract has no rule and calls that fixture CLEAR | Stays **sysml-codegen [DEEP-QUALIFIED-OUTPUT-WIRING]**; **Item 2** decides whether the contract needs a rule meanwhile |
| **L6-LIBRARY-ALIAS-SOURCE** | Not affected by Item 1 (no rule over EXPOSE aliases; `validate` output unchanged) | Stays in the **agentic-mbse backlog**, outside this epic |
| **82 explicit follow-up sites** (37 public-capability, 45 unknown role) | Inspected in Phase 9; no matrix row covers them. Notable: `inout` / non-attribute `out` calc parameters, quantity-typed referenced features (as `SI_EDGE_DANGLING`), untyped or multiply-typed calc usages, `null`/`*` literal bindings, expressions past the depth limit | **Item 2** (per-site stable codes and mutation tests, as D2 assigns) |
| **A CLEAR verdict does not mean the generator accepts the model** | `deep_cross_scope_probe` is CLEAR and refused by codegen; every rule-less gap above can refuse a CLEAR model | **Item 3** (L6 wording must not present CLEAR as "will generate") and **Item 5** |
| **R2-halted pairs** | None. No refused probe was ever admitted (Phases 1, 6, 7, 10) | — |

## 3. Every `unconfirmed` pair

Pairs a rule recognizes with no probe-observed outcome. Each reports `unconfirmed`, never `refused`.

| Rule / shape | Unconfirmed contexts | Why | Proposed destination |
|---|---|---|---|
| `binding-source/expression_source` | `owner_other` | No probe of an owner kind that attaches nothing | **Item 2** probe |
| `binding-source/self_reference_source` | `owner_other`, `writer_overridden` | Not probed | **Item 2** probes |
| `conditional-expression/conditional_resolved_branches` | every context | No conditional whose branch references all resolve was observed | **Item 2** probes |
| `conditional-expression`, `indexed-reference`, `invocation-callable` | `calc_result_expression` | The generator refuses every bare-result calc def for another reason (CALC-DEF-BARE-RESULT) | **Item 2**, with that gap |
| `constraint-predicate/blocked_predicate` | `owner_other` | dc3 B8's two blocked constraints sit here (calc-usage owners) | **Item 2** probe; it would show ES-001's code first |
| `constraint-predicate/non_numerical_predicate` | `owner_other`, `owner_package`, `owner_uninstantiated` | dc3 B8's four non-numerical constraints sit at `owner_other` | **Item 2** probes |
| `part-multiplicity/nonunique`, `negative_bound` | every context | SysIDE 0.8.4 rejects both shapes before the generator runs, so no probe can be authored | **Item 2 / owner**: retire the shapes or keep them as unreachable |
| every instantiation-dependent rule | `beyond_generator_roots`, `beneath_refused_multiplicity` | Unconfirmed by design (D7, Implementation Note (b)) | Keep; **Item 3** decides how L6 presents them |

## 4. The ten PUSH-DOWN profile rows

| Row | Matrix class / evidence | Proposed destination |
|---|---|---|
| PUSH-DOWN-EXPR-PROFILE-CHAIN-SEGMENTS | tracked gap; the named shared helper does not exist at this revision; candidate sites have unknown roles | **Item 2** (classify the chain-segment sites), then **Item 3** |
| PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-SHAPE-MESSAGE | advisory, no raise site | **Item 3** (L6 advisory) |
| PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-OPERATOR | tracked gap; sites `calc_compat_renderer.py:115`, `:120`, which become `MANUAL_REQUIRED` stubs, not refusals | **Item 2** (decide refusal vs stub), then **Item 3** |
| PUSH-DOWN-HIER-PROFILE-REDEF-PRECEDENCE | advisory, no raise site; needs codegen precedence facts | **Item 3**, after Item 2 publishes precedence |
| PUSH-DOWN-HIER-PROFILE-UNSUPPORTED-RHS | tracked gap; callable part covered by ES-005 at `attribute_value` | **Item 3** (consume ES-005; operator part with UNSUPPORTED-OPERATOR) |
| PUSH-DOWN-HIER-PROFILE-MULTIPLICITY-SHAPE | tracked gap; the decision is now `part-multiplicity/unresolved_bound`, probe-observed | **Item 3** (L6 consumes the rule); close the row there |
| PUSH-DOWN-HIER-PROFILE-AMBIG-INHERITED-ATTR | advisory; the port aborts as unverified where codegen's incomparable-typings check fires | **Item 3**, after Item 2 publishes type selection |
| PUSH-DOWN-AGG-PROFILE-SUM-SHAPE | tracked gap; one candidate site (`project.py:812`) of unknown role | **Item 2** (classify), then **Item 3** |
| PUSH-DOWN-AGG-PROFILE-WRAPPER-SHAPE | advisory; generation is permissive | **Item 3** (advisory only, separate from generation behavior) |
| PUSH-DOWN-AGG-PROFILE-LITERAL-SHAPE | tracked gap; no site located | **Item 2** (probe `sum(5.0)`), then **Item 3** |

## 5. Found outside the epic's scope

| Finding | Proposed destination |
|---|---|
| `agentic-mbse validate` on `tests/fixtures/sump_pump` is nondeterministic (before and after Item 1): the directory loads three variants of the same packages | New **agentic-mbse backlog** row (test-fixture hygiene), outside this epic |
