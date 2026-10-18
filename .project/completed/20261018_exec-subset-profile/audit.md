# Audit: Executable-subset capability inventory and shared profile (EXEC-SUBSET-CONTRACT Item 1)

**Verdict:** Certify (with recorded limits for the owner; see Must-fix / Should-fix)
**Audited:** 2026-10-18
**Branch:** `exec-subset-profile`
**Commit:** `8b2b3a76` (implementation commits `9721bc1b`..`044e32c1`; final implementation revision `9b123cf3`; code diff against base `23d9ef32`)

---

## The Point

Three consumers each hold their own picture of which SysML shapes sysml-codegen can execute: the generator itself, L6 validation, and the shipped guidance. They drift. On the dc3 baseline, L6 reported B7 and B8 and missed B1–B6, so a modeler found the generator's limits one failed run at a time.

Item 1 builds the single declared contract the three will share: an inventory of every refusal site with an owner and a class, packaged rule records for the shared structural rules, and a pure evaluator over neutral facts in agentic-mbse. It wires no consumer. The epic's governing obligation is to do this **without duplicating model interpretation and without broadening current refusals accidentally**. The contract is worth having only if it is honest in both directions: it never calls a model clean when a check could not run, and it never refuses something the pinned generator (sysml-codegen `b5663c07`) accepts.

## Summary

The core is solid. Every `refused` outcome is gated twice: the record loader refuses any refused admission without a probe id naming its own (rule, shape, context), and the evidence tests require that probe to exist, certify against the pin, and expect the same outcome. Missing facts force `INCOMPLETE`. The decision layer imports no SysIDE and no codegen. The dc3 repaired tree is CLEAR with zero refused; the corpus floor holds; same-generator and codegen-suite runs are identical.

What is not clean is presentation and a few recorded-but-unreconciled facts: B8 appears on the dc3 baseline only as `unconfirmed` (soundly), the matrix still describes B8's malformed predicates as `refused`, an `admitted` outcome covers an expression the generator silently drops, and a `CLEAR` verdict does not carry the contract's coverage limit. None of these violates a spec requirement as written or a design invariant, so they are should-fix, not blockers.

I could not run any command that executes Python (`uv run` was denied for me and for my helpers), so the test counts, the mutation tests and the repository checks below are verified by reading code and recorded evidence, not by execution. The orchestrator must run them (see Must-fix M1).

## Product Judgment

**Is this the right piece of work? Yes.** The work builds what the epic's Item 1 asks for and nothing a later item owns: no consumer is wired, `validate` output is unchanged, no shipped asset changed, codegen is untouched. The R1 ownership decision is filed as ADR 0001 with the owner's 2026-10-18 "A (ii)" reply.

The product-lens implementation pass (appended to `product-lens.md`, gate **OPEN**, no BLOCK) raised three [DO] findings. I checked each against the code; all three are still true:

- **impl-F1: `CLEAR` does not say what the contract cannot check.** `Verdict.CLEAR` is documented as "the only clean verdict" (`src/agentic_mbse/sysml/subset_profile.py:154`), and `ScopeReport` (`subset_profile.py:692-705`) reports roots and fact kinds only. The recorded counterexample: codegen's corpus refusal fixture `deep_cross_scope_probe` evaluates CLEAR because DEEP-QUALIFIED-WIRING has no rule (`evidence/acceptance.md`). Not a blocker today because no consumer exists, but Item 3 must not render CLEAR as "generates". Should-fix S2.
- **impl-F2: `INCOMPLETE` outranks `REFUSED` in the single verdict** (`subset_profile.py:1241-1245`). The dc3 baseline has 236 probe-backed refusals and its headline is "incomplete". Nothing is hidden (findings are all present), but a verdict-only consumer softens a certain refusal. Should-fix S3.
- **impl-F3: sysml-codegen ADR 0012 still says codegen alone owns the slot and multiplicity reads,** while this branch ships the second reader. The amendment is a draft (`evidence/adr-0012-amendment-draft.md`) deferred to Item 2. Owner call on timing; recorded as S6.

No structural smell fired in a way that changes the verdict. One product-drift smell fired in a mild, approved form: two walkers must be kept in sync by hand (advisory A3).

## Must-fix before close

These are verification gaps, not code defects. They must be closed before `/_my_close`, but they do not change the verdict unless a run fails.

- **M1. Run the repository checks and the R2 mutation tests; I could not.** Every `uv` command was denied in this session, for me and for the helper agents. Run, at `8b2b3a76`:
  - `uv run pytest tests/`, `uv run mypy src/`, `uv run ruff check src/ tests/`. Recorded at `9b123cf3`: 3502 passed / 3 failed (environmental) / 1 skipped / 1 xfailed; mypy 97 errors in 19 files; ruff 118 (`evidence/repository-checks.md`). Baseline at `8b027bbc`: 118 ruff / 97–98 mypy / 3 environmental pytest failures. Any new failure, or any finding in an Item 1 file, is a blocker.
  - In a scratch copy, the mutations in § R2 safety below, each expected to fail a named test. If mutation (c) or (a′) passes the suite, that is a blocker.
- **M2. Owner acceptance of the dc3 baseline limit.** B8 is reported only as `unconfirmed`, and the baseline verdict is INCOMPLETE (§ Spec conformance). The criterion is met as written, but the design's own reading (design § Option A′) treats an `unconfirmed` dc3 category as needing owner acceptance. It is already listed in `CURRENT_WORK.md`; it must be answered before close.

## Blockers

None found by static verification. M1 can still produce one.

## Advisory

Ranked by importance. None blocks certification.

### Should-fix

- **S1. An `admitted` outcome covers an expression the generator silently drops.** All three site rules record `other_expression_site` as `admitted` with qualification `none` (`subset_profile_rules.toml:207-210`, `:311-314`, `:358-361`). Their probe shows what that means: in `calc m : Twice { in v = x; ScalarFunctions::max(v, 1.0) }` the generator ignores the `max(...)` and emits Twice's own `2.0 * v` (`tests/fixtures/subset_profile/probes/invocation-callable__unsupported_callable__other_expression_site/`). The module's own vocabulary calls a silent drop `omitted` (`subset_profile.py:143-144`). The spec does allow "never examined" as an admitted context, so this is not a spec violation. **Impact:** a model whose only finding is this one evaluates CLEAR, and an Item 3 or Item 5 consumer that renders `admitted` as "works" tells the modeler their expression runs when it is thrown away. **Change:** mark these admissions so a consumer can tell them apart (a `Qualification` member such as `not_examined_dropped`, beside `manual_stub`), or re-probe them as `omitted`. The matrix row CALC-USAGE-BARE-RESULT-DROP and R3 already track the drop itself.
- **S2. Carry the contract's coverage limit with `CLEAR`** (product-lens impl-F1). Either have `ScopeReport` name the matrix rows with no rule (or a pointer pinned by `SUBSET_PROFILE_VERSION`), or reword the `CLEAR` docstring (`subset_profile.py:154`) and ADR 0001 invariant 2 to "clean over the implemented rules". **Impact:** without it, Item 3 must rebuild the limit from the matrix or will present CLEAR as "the generator accepts this model".
- **S3. Report completeness and the worst outcome separately** (product-lens impl-F2), or record it as an Item 3 rendering obligation. **Impact:** dc3 baseline's 236 certain refusals headline as "incomplete".
- **S4. The matrix misstates B8.** `matrix.toml` ES-007's `[[row.split]]` for MALFORMED_NUMERICAL says `count = 4`, `outcome = "refused"` (`tests/fixtures/subset_profile/inventory/matrix.toml:203-206`). The dc3 baseline run reports those constraints as **2** constraints, `unconfirmed` at `owner_other`, and the generator never reaches the predicate check for them (it refuses their calc-usage owner first, as B1). **Impact:** Item 5 renders guidance from the matrix and would state a refusal the contract does not make. **Change:** state the dc3 outcome as recorded (2 constraints, `unconfirmed`, refused by the generator through ES-001), and keep the general ES-007 outcome in the row statement.
- **S5. Record SA-1's acceptance in the spec.** The spec's Change Log still says SA-1 is "Pending owner or orchestrator acceptance. Until it is accepted, the criterion stands as written" (`spec.md:265`). The plan (`plan.md:33`) and design (`design.md:46`) record it as accepted by the orchestrator on 2026-10-18, and the loader enforces it (`subset_profile.py:451-471`). **Impact:** a reader of the spec alone sees `calc-owned-assertion/asserted_constraint` failing a criterion. **Change:** amend the Change Log entry to "accepted, 2026-10-18, by orchestrator", with its provenance.
- **S6. Decide when to file the ADR 0012 amendment** (product-lens impl-F3). Owner call. **Impact:** until it is filed, a codegen agent changing the slot or multiplicity reads is told by codegen's own ADR that it owns them alone, and the CI parity guard does not exist yet; the recorded 73/73 parity run is the only check.

### Note

- **A1. The R2 guarantee lives in the loader, but the evaluator accepts unvalidated records.** `evaluate_subset_profile(facts, rules=...)` (`subset_profile.py:1260-1264`) takes any `RuleRecords`, and `RuleRecords`, `ShapeRecord` and `Admission` are public frozen dataclasses with no validation of their own. A caller who builds records directly gets `refused` with no probe. `SubsetFinding.__post_init__` (`:639-640`) checks only that evidence is non-empty. **Impact:** low today (tests use this seam on purpose); Item 2 or 3 could pass hand-built records by mistake. **Change:** validate in `RuleRecords.__post_init__`, or make `load_rule_records` the only constructor.
- **A2. One branch that decides a context has no test.** `_Instantiation.consumer_placement` returns `OWNER_OTHER` for a consumer attached as neither a calculation nor a constraint (`subset_profile.py:848`). The only `OWNER_OTHER` test reaches `_unattached` (`:813`) instead (`tests/test_sysml/test_subset_profile_evaluate.py:152-170`). Mutating `:848` to `OWNER_INSTANTIATED` would emit probe-less `refused` findings and, by reading, no test would fail. **Change:** add one synthetic case for an unattached consumer.
- **A3. Two expression walkers must stay in step by hand.** `reference_use.invocation_uses` (`src/agentic_mbse/sysml/reference_use.py:455-500`) re-implements `_walk`'s dispatch order (`:303-340`) so it can report instead of raise. The design approved this, and `tests/test_sysml/test_invocation_uses.py` checks it on fixtures. **Impact:** a new leaf kind added to `_walk` but not to `_invocations` makes the contract and the generator disagree on what an expression contains. **Change (Item 2 or later):** one walker with a visitor, or a test that asserts the two visit the same node sequence.
- **A4. `unverified` entries for failed facts carry no context.** `_element_checks` and `_missing_kind_checks` set `context_id=None` (`subset_profile.py:1194-1216`), and enumeration failures also have no subject. The spec's failure criterion asks for "rule ID, context, safe location and cause". Honest (the context cannot be computed when the fact failed), but it is a gap against the letter. **Change:** say so in the spec or the `UnverifiedCheck` docstring.
- **A5. Probe observations are at `ecc18940`, not the final revision.** The design made the final revision's `observation.json` canonical (design § Where things live); the records' `verified_against.agentic_rev` and all 80 committed observations are at `ecc18940` (`subset_profile_rules.toml:16`). The final-revision run (`evidence/same-generator.md`) shows all 80 identical except `identity.agentic_rev`, so the evidence holds. The deviation is noted in the plan's Phase 10 issues but not in the design.
- **A6. The `sump_pump` validate difference is explained by argument, not reproduced.** The single-run diff shows the final output with L2 unused 0 and L4 malformed 0 (`evidence/validate-diff.md`). The repeat runs (`evidence/validate-repeat-sump-pump.log`) show both values varying at the base revision, but never that exact combination at either revision. The nondeterminism case is convincing; the evidence would be complete with that output observed at the base.
- **A7. Count differences against T-001 are noted, not reconciled.** B3 is "(20)" in dc3 T-001 and 15 part usages here; T-001's row also mentions ranges. The run says "a grep finds exactly these 15" (`evidence/acceptance.md`). I could not re-run the grep. One line naming what T-001's 20 counted would close it.
- **A8. Private import across modules.** `subset_extraction.py:43` imports `_ASSERTED_FORMS` from `constraint_extraction`. Intended reuse (design § Implementation Notes), but it couples to a private name. Make it public.
- **A9. Four site-account rows to revisit** (`tests/fixtures/subset_profile/inventory/site_account.csv`). Item 2 classifies by these, so wrong labels cost it later.
  - CSV line 77 (`elaborate.py:1939`) also emits `SI_INDEXED_SOURCE_UNSUPPORTED`, and the matrix classifier maps `indexed` to INDEXED-REFERENCE (`matrix.toml:693-698`), but the row names only `ES-003;ES-012;SELF-BINDING` and INDEXED-REFERENCE's `sites` omits it.
  - CSV lines 256 and 258 (`calc_compat_renderer.py:115` and its sibling) are `in_scope` for the UNSUPPORTED-OPERATOR row, but they never refuse: `expression_compiler.py:291` catches them and emits a manual stub. "In scope" overstates coverage for a row with no rule.
  - CSV line 41 (`elaborate.py:595`) is an internal invariant whose guard is an earlier builtin `ValueError` on the same condition (`constraint_extraction.py:311-312`, cited as `:307`). That shows the site is unreachable, but by an earlier crash, not by valid input being impossible; its sibling at `:607` (line 42) is a follow-up. Re-check, and fix the citation.
  - Five in-scope rows (CSV lines 56, 97, 153, 189, 269) carry owner "unassigned until R3 (proposed: …)". Non-empty, but no owner is assigned until the owner rules on R3.
- **A10. The computed-reason test pins the exact reason set at two of five sites.** `test_site_597` and `test_site_813` assert the exact set; `test_site_542`, `test_site_660` and `test_site_711` assert only subset-of-`REASON_CODES` plus a few named reasons (`tests/test_sysml/test_executable_profile_computed_reasons.py:85`, `:106-110`, `:122`). **Impact:** a site that stops emitting a reason, or starts emitting a different known one, passes, and `scanner.toml`'s hand-copied lists drift silently. **Change:** assert the exact set at all five, read from `scanner.toml`.

## Findings Detail

### Plan completion

All 11 phases are marked done with completion notes, actual changes, deviations and validation. One unchecked box remains, Phase 1 "Standing checks green" (`plan.md:171`), deliberately left open with the reason: the repo-wide checks were red before Item 1, and the orchestrator later scoped "green" to "no new failures, Item 1 files clean" (`plan.md` § Standing Rules). I leave it unchecked; M1 is how it closes.

Placeholder scan of the new modules (`subset_*`, `occurrence_*`, `fact_refs.py`, `invocation_allowlist.py`): no TODO, FIXME, `NotImplemented` or stub bodies. The one `...` is a `Protocol` method signature (`subset_extraction.py:98`).

### Spec conformance

**Inventory and site account**

- Site account total — met. 502 rows in `tests/fixtures/subset_profile/inventory/site_account.csv` (lines 8–509): 441 codegen, 61 agentic-mbse, matching the header and `evidence/site-reconcile-final.log` (0 unaccounted, 0 orphan, at `9b123cf3`). Every row has a closed disposition, an evidence pointer and an owner; no duplicate ID seen on a full read (not script-checked). Codegen's working tree HEAD equals `b5663c07`.
- Sites and matrix joined — met, with A9. All 44 in-scope rows name existing matrix rows, with the rule when the row is a shared rule; every matrix-listed site is in the CSV as in scope; rows without sites say `no_raise_site` or `not_located` with a reason; all 82 follow-ups carry an owner and a coverage limitation.
- Count reconciliation explicit — met. `evidence/site-reconciliation.md` itemizes 441→441 and 59→61; both added sites are Item 1's own and exist in source (`reference_use.py:472`, `subset_extraction.py:269`, both `EXPRESSION_DEPTH_EXHAUSTED`). The scanner reproduces the prototype's 500 IDs exactly at the prototype revisions (plan Phase 9).
- Blind spots listed — met. `scanner.toml` names the forms, a scanner revision label, and the four required blind spots plus dynamic dispatch and non-Python surfaces. The commit hash is in the CSV header and log, not in `scanner.toml`.
- Five computed reason sites closed — met as written, with A10. I enumerated each site's possible reasons from `executable_profile.py` (:542 eight, :597 two, :660 ten, :711 seven, :813 two); `scanner.toml` lists exactly those, and the inputs in `tests/test_sysml/test_executable_profile_computed_reasons.py` produce every one and assert `REASON_CODES` membership. No enum conversion added.

**Disposition spot-check.** 27 rows across dispositions, roles and both trees, each opened at its cited line in source. Every cited line exists and raises the stated code. Judgments: 23 clearly right; two in-scope rows that are not refusals (A9); one internal invariant with weak evidence (A9); one join that omits INDEXED-REFERENCE (A9). No valid-model public refusal is classified as an internal invariant.

**Capability/refusal matrix**

- Every named case has a row — met. `tests/test_subset_matrix.py` checks the fixed list, B1–B9/U1–U7 mapping, and the B8 split (plan Phase 8). Rows ES-001..ES-012, SELF-BINDING, INDEXED-REFERENCE, DEEP-QUALIFIED-WIRING, the ten PUSH-DOWN rows and L6-LIBRARY-ALIAS-SOURCE exist. B8's split misstates the dc3 outcome (S4).
- Binding-source classifier fully placed — met. `matrix.toml` classifier placement; SELF-BINDING carries `l2_relation`.
- Every row classified and owned — met (by test and by reading the rows I opened).
- Matrix and records agree — met. `tests/test_subset_matrix.py` joins both directions, reads only `tests/` and package data, and passed in an archive copy without `.project/` (plan Phase 8).

**Rule records and evaluator**

- Records complete — met. The loader requires every field, closed vocabularies and `SUBSET_REASON_CODES` membership (`subset_profile.py:426-562`); `tests/test_sysml/test_subset_profile_records.py` and `_vocabulary.py` test it.
- Every refusal has a probe record — met (statically). 24 refused pairs, each citing probes named for that pair (loader, `subset_profile.py:379-392`); `tests/test_subset_probe_evidence.py:73-92` requires each to exist, be a `record` probe of the pair, expect the recorded outcome, certify, match the pinned identity, and carry the shape's expected code. The judge requires exit 1, code set equal to the expected code, and every error location inside the construct's lines (`tests/helpers/subset_probe_judge.py:401-419`).
- Every refused shape has an admitted-context probe — met with SA-1 and a recorded correction. The loader enforces it (`subset_profile.py:467-471`). One shape uses SA-1 (`calc-owned-assertion/asserted_constraint`). The spec's named ES-005 and ES-006 examples ("a calc def's result expression") turned out refused by a different mechanism (zero outputs, `SI_EVIDENCE_INCOMPLETE`), so that context stays `unconfirmed` and the admitted context is a calc usage's bare result. This uses the criterion's own correction clause and is recorded for the owner (plan Phase 6, orchestrator ruling). See S1 on what that admitted context means.
- Each implemented rule has refused and admitted fixtures — met. Every prototype admitted neighbor is a control probe, and `test_control_probe_models_draw_no_finding_of_their_rule_and_no_refusal` (`tests/test_subset_probe_evidence.py:163-170`) asserts it draws no finding of its rule and no refusal.
- Roots reported and generator-equivalent — met. `tests/test_sysml/test_occurrence_extraction_roots.py:48` on `cases/roots_mixed_owners.sysml` (nested, package-level, part-def-owned, item-def-owned, nested-package); widened and narrowed at `tests/test_sysml/test_subset_profile_rules_instantiation.py:162-193` and `test_subset_profile_evaluate.py:202-227`.
- **Baseline run accounts for B1–B8 — met as written, with a recorded limit (M2).** The run at `9b123cf3` reports every category with locations and rule IDs (`evidence/dc3-baseline.md`, `evidence/acceptance.md`): B1 164, B2 29 bindings, B3 15 usages / 72 occurrences, B4 1, B5 22, B6 5 refused; B7 32 omitted; B8 4 non-numerical and 2 blocked constraints `unconfirmed`. Roots, declaration and occurrence counts and the dedup rule are recorded. The criterion says "reports ... with locations and rule IDs", not "as refused", so the letter is met. **The reason B8 is `unconfirmed` is sound:** all six constraints are owned by calc usages; the generator refuses them first for their owner (they appear in the B1 refused list, e.g. `baseline_annual.sysml:57, 84, 97, 124`, `baseline_costs.sysml:74`), so it never reaches the predicate check. A probe of a blocked predicate under a calc-usage owner would show ES-001's code and could not certify as ES-007, so no honest outcome other than `unconfirmed` exists. Put plainly: on dc3, B8 is an L6 report, not a generator refusal; the generator's refusal of those constraints is already reported as B1. The verdict is INCOMPLETE because of 50 `unverified` checks, all at locations the contract already refuses (itemized in `acceptance.md`); the spec does not ask for a complete verdict on the baseline.
- Repaired run refuses nothing — met. CLEAR, 0 refused, 0 unverified, 0 unconfirmed; 30 String omissions; 15 template `[*]` usages admitted (`evidence/dc3-repaired.md`).
- Corpus regression floor — met. Manifest read as 37 / 14 / 23; 14 snapshot fixtures CLEAR with zero refused; refusal fixtures pass, the one out-of-list code (`SI_SELF_BINDING` on `plant_value_shapes`) is a probe-recorded pair; the snapshot-proves-projection-not-generation limit is stated (`evidence/acceptance.md`).
- Failure cannot look clean — met, with A4. Synthetic-fact injection tests for (a) extraction, (b) enumeration, (c) occurrence abort (`tests/test_sysml/test_subset_profile_evaluate.py:230-304`) assert the rule ID, cause, subject, unrelated findings still present, and `INCOMPLETE`.
- Output deterministic — met. Permuted fact order (`test_subset_profile_evaluate.py:478`), all six orders of a three-document model and a repeated run (`test_subset_profile_rules_instantiation.py:195-217`). Findings sort by a total key (`subset_profile.py:642-651`), duplicates raise (`:1310-1313`).
- No consumer coupling — met. `tests/test_sysml/test_subset_profile_coupling.py` scans every package module's imports for `sysml_codegen`, rule/reason/shape IDs for `SI_` and consumer type names, and the records for `SI_` outside `expected_code`/`code`. My own grep finds `sysml_codegen` only in docstrings and `SI_` in `src/` Python only in one pre-existing L2 docstring (`validation/level2_structure.py:301`). The hygiene test asserts the decision module loads no SysIDE or SysIDE-reading module (`tests/test_sysml/test_subset_profile_hygiene.py`).
- Consumer output unchanged — met with a recorded limit (A6). 15 of 16 inputs identical, both dc3 trees included; `sump_pump` is nondeterministic at both revisions (`evidence/validate-diff.md`). Item 1 changes one pre-existing `src/` file, `reference_use.py`; I read the diff and it is behavior-preserving for the refusal path (the allowlist moved to `invocation_allowlist.py`; plurality still keys on `sum`'s identity).

**Close-out**

- R3 proposal recorded — met. `evidence/r3-proposal.md`, headed PROPOSED, owner approval required.
- Re-estimate recorded — met. `evidence/re-estimate.md`, Items 1 and 2 in engineer-days with the basis.
- Repository checks pass — **not verified by me** (M1). Recorded evidence says "no new failures" against the orchestrator's definition, with license-dependent tests named.

**Tagged requirements spot-checked:** [HARD] no codegen import — met. Neutral reason IDs — met. `SI_*` only as evidence — met. No `refused` without owner approval for an admitted shape (R2) — no R2 fired; no refused probe exited 0 (`evidence/r2-open.md`, plan Phases 6–7). `REASON_CODES` reused, not duplicated; ES-007 findings carry them as `detail_reasons`, validated (`subset_profile.py:636-638`). Closed `SUBSET_REASON_CODES`, validated at load and at finding construction. Records are package data readable without SysIDE. Separate `SUBSET_PROFILE_VERSION`, pinned to a digest of records and allowlist (`tests/test_sysml/test_subset_profile_version.py`). Non-goals respected: no consumer wiring, no new language support, no refusal relaxed, codegen untouched.

### R2 safety

**Can the evaluator emit `refused` for a (shape, context) without a certifying probe?** For the packaged records: no, provided the test suite runs. Two layers hold it:

1. **The loader, at import** (`PACKAGED_RULES = load_packaged_rule_records()`, `subset_profile.py:1175`). It rejects a listed outcome with no evidence, non-probe evidence for anything but `admitted`, a probe id that does not name its own pair, a refused shape without `expected_code`, and a refused shape with neither an admitted-context probe nor an SA-1 statement. A bad record makes the module fail to import, so every dependent test errors.
2. **The evidence tests** (`tests/test_subset_probe_evidence.py`): re-judge every stored observation; require each cited probe to exist and certify its own pair at the pinned identity with the shape's expected code; require the evaluator to reproduce each pair on the probe's own model, and to emit no `refused` at all on a model the generator ran.

Mutations, predicted from the code (not executed; M1 asks for the run):

| Mutation | Caught by |
|---|---|
| Refused admission citing an unrelated probe | Loader ("does not probe") |
| New refused admission with no evidence | Loader |
| Refused citing a nonexistent probe whose id has the right prefix | `test_cited_probe_certifies_its_own_pair_at_the_pinned_identity` (`:77`) |
| An admitted pair flipped to refused, keeping its own probe (a′) | Same test (`expected_outcome` mismatch) and `test_evaluator_reproduces_each_cited_probe`; the version digest also changes |
| Observed code changed in an observation | `test_stored_observation_re_judges_as_recorded` (judge gives `code_mismatch`) |
| Observation deleted or `certifies` flipped | `load_observation` raises; both tests error |
| Error line moved outside the construct | Re-judge test (`location_outside_construct`) |
| Rule function places an uninstantiated owner as instantiated (`:791`) | `test_subset_profile_evaluate.py:152-205` and the admitted probes' reproduction |
| `consumer_placement`'s fallback (`:848`) changed to `OWNER_INSTANTIATED` | **No test found** (A2) |

What the mechanism does not guarantee, as the design says: that every real situation filed under a context behaves like the probed one (bet B5). Variation probes cover the instantiation-dependent refused pairs (8 for binding-source `owner_instantiated`, 5 for range, and so on), and none disagreed.

### Design conformance

Implementation follows the design: three layers (pure facts, SysIDE extraction, pure decisions), records decide and rules only recognize, unlisted pairs `unconfirmed`, D3 evidence gating at load, SA-1, D4 sibling reason set, D5 one binding-source rule, D6 declaration-keyed findings with occurrence counts, D7 roots as extraction input with `beyond_generator_roots` never decided, D8 locations, D10 hardened scanner, D11 ES-010 refusal side kept a candidate, D13 summary port, D14 generator multiplicity behaviors mirrored (G1 control probe). The occurrence port mirrors codegen function by function; I compared `_constant_integer` (`occurrence_extraction.py:284-293`) with codegen's (`elaboration/occurrence.py:779-788`) and it is identical, including the caught exceptions. Parity 73/73 at the final revision.

Recorded deviations, all documented in the plan: `OccurrenceAbort` gained members beyond Appendix A (P-4); `ContextId` dropped `ATTRIBUTE_USAGE` and `EVERYWHERE` (attribute usages are simply not part-multiplicity facts; the attribute-usage control probe covers the admitted case); the matrix's `site_status` replaces `no_raise_site`; a site may name several rows. Undocumented in the design: A5.

### Code integrity

- **Failure honesty: good.** Broad catches are narrow and justified: `safe_location` is documented never-raise and degrades to less, not false (`occurrence_extraction.py:126-143`); `_constant_integer` mirrors codegen; `_authored` drops only display text. Invariant violations raise instead of defaulting (`subset_profile.py:1042-1045`, `:1304-1313`). No `except Exception`.
- **Vocabularies: closed and validated.** `Outcome`, `Verdict`, `ContextId`, `EvidenceStatus`, `Qualification`, `FactKind`, `ScopeCause`, `OccurrenceAbort`, `SUBSET_REASON_CODES`; record loading and finding construction both validate.
- **Duplicated interpretation:** the occurrence port is the approved copy. One further hand-synced walker exists (A3). The reference-metatype test lives once in agentic-mbse (`subset_extraction.py:149-153`), mirroring codegen's, as the spec required.
- **Abstraction:** no god functions or sentinel modes found. `evaluate_subset_profile` takes an optional `rules` parameter that bypasses validation (A1).
- **Nondeterminism:** none found in the evaluator; ordering is total and tested.

---

## Certification

**Checked:** spec, design (rev 2, R1 decision), plan (all phases, notes, orchestrator rulings); site account totals, joins, reconciliation, scanner manifest and 27 dispositions against source; the five computed reason sites enumerated from source; `subset_profile.py` in full; `subset_profile_rules.toml` in full; the probe judge's certification logic; `test_subset_probe_evidence.py`, `_coupling.py`, `_hygiene.py`, `_version.py` in full and the failure-injection tests; the `reference_use.py` diff; imports, `SI_*`, TODO and `except` scans over the new modules; one occurrence-port function against codegen; one admitted probe model; the acceptance, dc3, same-generator, validate-diff and repository-check evidence; R3 proposal and re-estimate headers; ADR 0001's presence; the product-lens pass.

**Marked:** 22 of 24 spec success criteria ticked in `spec.md`, verified by reading code and recorded evidence. Two left unticked: "Baseline run accounts for B1–B8" (met as written, but waits on owner acceptance of B8 as `unconfirmed`, M2) and "Repository checks pass" (not run, M1). Plan: no change; phases 2–11 were already ticked and their artifacts exist and say what the notes claim; Phase 1's "Standing checks green" box stays open until M1. Epic: heading not marked ✅, because two criteria are open. `CURRENT_WORK.md` updated.

**Not checked:** I executed no Python. No pytest, mypy or ruff run, no mutation test, no probe, scanner, parity or acceptance re-run; all such numbers are the implementer's recorded evidence (M1). I did not read `occurrence_extraction.py` beyond the parts cited, `subset_extraction.py` beyond its first 160 lines, or the matrix and records tests in full. I did not re-grep the dc3 baseline for B3's count (A7). I did not check the B5 variation probes' models individually, nor the codegen-suite per-test JSON. The sysml-codegen working tree I compared against was read from disk, not from `git show b5663c07`.

---

## Audit fixes (2026-10-18)

Applied from `briefs/implement-audit-fixes.md` and `briefs/implement-audit-fixes-2.md`. Commits `b1e95ec9` (code, fixtures, records) and `ce0ad1ff` (canonical probe observations and re-pins). **`ce0ad1ff` is the new final implementation revision;** every recorded run below was repeated there. Implementation notes: plan § Audit fixes.

**Orchestrator answers to the previous session's questions**, each `[AGENT]`, 2026-10-18:

1. Execution is available in this session.
2. **S1 approved: generalize the load-time gate.** A refused shape needs at least one certified probe in a context whose outcome is not refused (`admitted`, `omitted` or `excluded`), or an SA-1 statement. Reason: the gate proves a rule is not a universal ban; a certified omission proves that equally. A deviation from design invariant 3. The three `other_expression_site` probes are re-authored as `omitted`.
3. **S3 approved:** a closed `Verdict.REFUSED_INCOMPLETE`; `INCOMPLETE` then means no refusals. **S4 approved:** correct both B8 splits to what the dc3 run reports, with the reason, cross-checked against the records.

### What changed, by item

| Item | Change | Status |
|---|---|---|
| **M1** repository checks | At `ce0ad1ff`: `pytest tests/` 3507 passed, the same 3 environment failures (stale `/home/reid/1cfe` paths, missing PIL), 1 skipped, 1 xfailed; `ruff check` 118; `mypy src/` 97 in 19 files. All equal the baseline; changed files are clean (`evidence/repository-checks.md`) | Closed |
| **M1** R2 mutations | 14 mutations in a scratch copy at `ce0ad1ff`, **all caught**, including (a′) and the `consumer_placement` fallback (`evidence/r2-mutations.md`) | Closed |
| **M2** owner acceptance of B8 | Not an implementer's call. The B8 evidence is now consistent everywhere (S4) | **Open for the owner** |
| **S1** silently dropped expression called `admitted` | The loader gate accepts any probe-backed non-refused partner (`subset_profile.py`, `_shape`). The three `other_expression_site` probes each hold a unique literal (`4271.5`, `4272.5`, `4273.5`) in the dropped expression, use the calc usage's result as positive control, and certify `omitted`: the literal appears in no generated file. A throwaway probe confirmed the check can fail: with the literal in a compiled expression, it appears in `modules/fx/twice.py` and the judge reports `omitted_element_present`. Records, `semantic_limits`, the matrix rows ES-005, ES-006, INDEXED-REFERENCE and CALC-USAGE-BARE-RESULT-DROP, and the R3 proposal say `omitted`. A bare result holding none of the three shapes (plain arithmetic) still draws no finding; the matrix row says so | Fixed |
| **S2** CLEAR's coverage limit | The module docstring and `Verdict.CLEAR` state that CLEAR is relative to the implemented rules and name the unruled families: DEEP-QUALIFIED-WIRING (`deep_cross_scope_probe` is refused and evaluates CLEAR), ES-002, ES-008, ES-009, ES-010's refusal side, CALC-DEF-BARE-RESULT, the unconfirmed rows, the follow-up sites. The R3 row "CLEAR is not 'generates'" points at it. L6 wording stays Item 3's | Fixed (docstring and records; consumer wording is Item 3) |
| **S3** INCOMPLETE hides refusals | `Verdict.REFUSED_INCOMPLETE` when refusals and an unrun check (or narrowed roots) coexist. dc3 baseline now reads `refused_incomplete` (236 refused, 50 unverified, every count unchanged); so does the corpus refusal fixture `invocation_binding_probe` | Fixed |
| **S4** matrix misstates B8 | ES-007's splits: NON_NUMERICAL 4 and MALFORMED_NUMERICAL 2, both `unconfirmed` at `owner_other`, each with the reason (calc-usage owners; the generator refuses them first through ES-001, B1). The matrix test cross-checks each split's outcome against the records at that context. Matches `evidence/dc3-baseline.md` | Fixed |
| **S5** SA-1 still "pending" in the spec | Change Log: accepted by the orchestrator, 2026-10-18; plus an entry for the S1 generalization | Fixed |
| **S6** ADR 0012 amendment timing | Owner call; unchanged | Open for the owner |
| **A2** `consumer_placement` fallback untested | The previous session's test was run and kept; mutation m9 shows it catches the `OWNER_INSTANTIATED` mutation | Fixed |
| **A9** four site-account rows | `elaborate.py:1939` joins INDEXED-REFERENCE (the account's `rule` column may now list several rules). `calc_compat_renderer.py:115`, `:120` are explicit follow-ups, since they never refuse; PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-OPERATOR is `no_raise_site`. `elaborate.py:595` is an explicit follow-up with role unknown, its guard citation corrected to `constraint_extraction.py:311-312`. The five "unassigned until R3" owners stay, because R3 is owner-only. Counts: 42 in scope / 375 handled elsewhere / 85 follow-up (was 44 / 376 / 82) | Fixed, except the R3-dependent owners |
| **A10** exact reason sets | All five computed sites assert the exact set from `scanner.toml`. The three helper-backed sites read the helper's own returns, so another site's reason on the same walk is not counted | Fixed |
| A1, A3–A8 | Not in the fix brief; unchanged. A5's shape recurs: the cited observations are at `b1e95ec9`, one commit before the final revision, because a record cannot name the commit that contains it. The final run differs from them only in `identity.agentic_rev` | Unchanged |

### Mutation results (`evidence/r2-mutations.md`)

| Mutation | Caught by |
|---|---|
| Refused admission cites an unrelated probe | Loader at import ("does not probe") |
| New refused admission with no evidence | Loader ("requires evidence") |
| Refused admission cites a nonexistent probe with the right prefix | `test_cited_probe_certifies_its_own_pair_at_the_pinned_identity`, evaluator reproduction, version digest |
| (a′) admitted pair flipped to refused, keeping its probe | `test_cited_probe_certifies_…`, `test_evaluator_reproduces_probe`, the matrix contexts test, version digest |
| S1: the omitted partner flipped to refused | Loader ("needs a probe of a context it is not refused in") |
| Observation code changed / observation deleted / `certifies` flipped / error line moved | `test_stored_observation_re_judges_as_recorded`, `test_cited_probe_certifies_…`, the matrix certify test |
| `_unreached` places an unreached owner as instantiated | 11 tests (placement, roots, evaluator reproduction of the `owner_uninstantiated` probes) |
| `consumer_placement` fallback → `OWNER_INSTANTIATED` | `test_a_consumer_attached_as_neither_calculation_nor_constraint_is_owner_other`, `test_an_unverified_check_does_not_hide_a_refusal` |
| The dropped literal reported as present in the output | Re-judge (`omitted_element_present`) and the certify tests |
| The non-refused-partner gate removed | `test_a_refused_shape_needs_a_probe_of_a_context_it_is_not_refused_in` |
| INCOMPLETE outranks REFUSED again | the S3 test and three failure-injection tests |

### Reruns at `ce0ad1ff`

| Run | Result |
|---|---|
| Probes | 80/80 certify at base `a718efec`, canonical `b1e95ec9` and final `ce0ad1ff`; observations differ only in `identity.agentic_rev` (`evidence/same-generator.md`) |
| Codegen suite | 2754 tests compared against the Phase 10 base, 0 differ |
| Occurrence parity | 73/73 match |
| dc3 baseline | REFUSED_INCOMPLETE; 274 declarations / 101 occurrences, 236 refused, 32 omitted, 6 unconfirmed, 50 unverified; identical to the `9b123cf3` run apart from the verdict name |
| dc3 repaired | CLEAR, 0 refused, 0 unverified, 0 unconfirmed |
| Corpus | 37/37 pass; 14/14 snapshot fixtures CLEAR |
| `validate` diff | 16/16 inputs identical (`sump_pump` matched this time; it is nondeterministic at both revisions) |
| Site rescan | 502 sites, 0 unaccounted, 0 orphan, identical to Phase 9's scan |

Siblings: `~/src/sysml-codegen` (HEAD `b5663c07`) and `~/src/dc3` (HEAD `60b44d53`) have empty `git status` and unchanged HEADs.

**Still open before `/_my_close`:** the owner's answer on M2 (B8 reported only as `unconfirmed`), R3 and S6. The spec criterion "Repository checks pass" is now ticked; "Baseline run accounts for B1–B8" stays open on M2.
