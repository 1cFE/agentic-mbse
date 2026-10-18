# Spec Review: Positional-binding hazard and check (EXEC-SUBSET-CONTRACT Item 4)

**Spec:** `.project/active/positional-binding-check/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/positional-binding-check/spec-review.md`
**Date:** 2026-10-18

**What I checked and how.** I read the spec, the epic (Item 4, D1, Items 1/3/5), the align record, the product-lens ledger, the prototype (`04-detector.py`, its 17 fixtures and all `04-*.log` files), the L2 code (`level2_structure.py`, `common.py`, `runner.py`, `types.py`), Item 1's shared facts (`fact_refs.py`, `subset_facts.py`, `subset_extraction.py`) and the dc3 citations. KerML and SysML semantics were checked against the vendored specs through the `kerml-expert` and `sysml-expert` roles. **Not checked:** I could not run SysIDE, `validate` or pytest in this session (commands needed approval). So nothing below is a SysIDE observation of mine; where a finding depends on what SysIDE actually emits, it says so and asks for a fixture.

---

## Reality Check

Sound. The spec is about the right work item, its Problem section matches the evidence (prototype logs, dc3 WI-008, codegen history), and its D1 policy reading, gates and non-goals match the epic and align record. Three defects are serious enough to fix before design: the finding rule has a false-negative clause the prototype did not have, the owner scope pulls in requirement and case subjects that will be flagged on ordinary models, and the fusion-tea reproduction criterion is circular. None of them changes what the item is for.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (must-fix):** The finding rule in Known Requirements ("no explicit redefinition by an input **of the same owner** targets that formal") is not the prototype's rule, and it misses a real swap. The prototype (`04-detector.py:117-141`) skips an input only when *that input* has its own explicit redefinition; it never looks at other inputs. The spec's clause exempts an input whenever *any other input* explicitly redefines its positional target.

- Failure case: `calc c : Sub { in b = 3; in :>> a = 10; }`. `b` sits at position 1, so it implicitly redefines `Sub::a` (KerML 8.3.3.3.4: position counts every directed owned feature, explicit or not). The second input explicitly redefines `a`. The spec's rule passes `b`; the prototype flags it. The author clearly meant b = 3, a = 10 by name. The native value is unknown (two features redefine `a`, and `Sub::b` gets only an implied redefinition from the `:>> a` input), and codegen wires by name, so this is the same cross-route hazard in a mixed spelling that real models will contain while authors migrate to `:>>`.
- The clause looks designed for one real subtlety: read literally, KerML gives an explicitly redefined input an implied positional redefinition too (`kerml-expert`: the only exemption is for InvocationExpression owners). If SysIDE does that, `in y redefines b = 3; in x redefines a = 10;` would carry implied mismatches. But the prototype's own skip ("the input has an explicit redefinition") already handles that case without exempting other inputs.
- What needs to be true: the rule is stated against the input's own explicit redefinitions (with multiple types handled per target as the spec intends), or the same-owner clause is kept with a stated reason and the mixed-spelling fixture above, with an expected result of FLAG. Either way, the fixture list in Success Criteria needs the mixed case (unprefixed plus `:>>` naming the unprefixed input's positional target), and a reversed deliberate-rename case (`in y redefines b; in x redefines a`), so the design can see what SysIDE emits for explicit inputs.

**L1-2 · Direct claim (should-fix):** D1 is graded `[NEED]` / `[OWNER]`. Under `.claude/rules/capture-fidelity.md` §1 it should be ratified, not owner-originated. The epic wording is agent-authored and says only "approved by the owner during the 2026-10-15 discussion". The prototype README offered this policy to the owner as an option ("unless owner decision 3 ... makes these non-blocking"). Item 1 regraded D2 from the same discussion for exactly this reason (Item 1 `product-lens.md` spec-F2). The spec asks review to confirm; my answer is that D1 should read `[INHERITED: epic D1] (ratified by owner 2026-10-15)`. This changes no requirement, because the spec does not challenge D1. It matters only for how a later agent may challenge a detail of it (by re-deriving, not by asking the owner). The align record's "Settled" label has the same issue; that file is not this spec's to fix.

**L1-3 · Direct claim (should-fix):** The scope requirement's reason, "the 125-finding baseline was measured with exactly this scope", is true of the code but does not validate requirements and cases. Neither consumer exercises them: I found no `subject`, `actor` or `stakeholder` declaration in fusion-tea or dc3 `models/`. So the baseline is silent about the subtypes the spec names. See L2-1 for what goes wrong there.

**L1-4 · Direct claim (should-fix):** Two semantic claims in the register need to separate the KerML text from what SysIDE 0.8.4 does. The prototype flags `inherit_def_no_params_usage_reversed` (`calc def Sub3 :> Sub;` with no owned parameters). Read literally, KerML counts only the *owned* parameters of each direct supertype (`kerml-expert`, OCL at KerML 8.3.3.3.4), so Sub3 offers no position targets and nothing would be implied. SysIDE evidently resolves through to `Sub`. The detector reads SysIDE, so it is right to flag. But the register's "actual semantics" entry should not claim the KerML constraint predicts every flagged case. It should say which behavior is KerML text and which is SysIDE 0.8.4 behavior observed on a named fixture.

### Lens 2 — Problem & Approach

**L2-1 · If-then tradeoff (must-fix):** Including requirement and case subtypes will flag correct, idiomatic models. Subject, actor and stakeholder parameters are `in` parameters (SysML 7.21.2: "A subject parameter is always an `in` parameter"; Actor/StakeholderMembership are ParameterMemberships). They are redefined by the same positional rule (SysML 8.4.17.2 says so directly). Every requirement definition implicitly specializes the library `RequirementCheck`, which owns `subject subj`. So `requirement def MassReq { subject vehicle : Vehicle; }` gives `vehicle` an implied redefinition of `RequirementCheck::subj`, a different name. That would be an `L2_POSITIONAL_BINDING` ERROR on nearly every requirement and analysis case written in the spec's own style. The spec's "user-model elements only" requirement does not stop it: the owner and input are user elements; only the target is in the library.

- **If** the target projects that adopt this check never write requirements or cases, excluding subject/actor/stakeholder parameters costs nothing and removes the risk.
- **If** they do, the exclusion is required, and the remaining hazard (a stakeholder landing on an actor slot, say) is a different check.
- My recommendation: exclude parameters owned through subject, actor and stakeholder memberships, keep the `in` parameters of constraint usages nested in requirements (`assert`/`require`/`assume constraint`), and add two fixtures that pin this: a requirement with a differently named subject (PASS) and a requirement-nested reversed constraint usage (FLAG). Whether to also drop requirements and cases from the owner scope entirely is a design call once those fixtures exist. Either way the reproduction counts should be unaffected, since neither consumer has subjects.

**L2-2 · Question to the user (should-fix, owner):** The spec makes pinned positional WARNINGs not fail L2, but leaves every other L2 WARNING failing L2 (`level2_structure.py:450`; `UNUSED_DEFINITION` at `:96` and `LITERAL_BINDING` at `:172` are WARNINGs today). The exemption itself is minimal and safe for other codes. The consequence is that D1's "warn" only produces a passing L2 in a project that has no other L2 warnings. I could not run L2 on fusion-tea, so I do not know whether fusion-tea's L2 passes today. **Does the owner want the D1 warning to mean "L2 can still pass" (which may not happen in fusion-tea anyway), or only "reported as a warning, separately counted"?** If fusion-tea's L2 already fails on other warnings, the R4-3 consequence paragraph ("fails L2 with 125 ERRORs, and ... stops before L3–L6") overstates what the pin move changes. Either way the reproduction log should record fusion-tea's current L2 result without this check, so the consequence is stated from evidence.

**L2-3 · Question to the user (should-fix):** A stale pin fails the run, and pin identity carries no file. When an author validates a subset of the tree (`validate models/designs/x.sysml`, or a subdirectory), every pin whose owner lives outside that subset has no matching finding and reads as stale. The check cannot tell "fixed" from "not loaded". **Should stale-pin judgment apply only when the validated path covers the pin list's whole recorded scope, or should pins record the model root they were recorded against?** The spec should state the required behavior; how to implement it is design. Today the spec's rule would make partial validation fail in any pinned project, fusion-tea included.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim (must-fix):** The fusion-tea reproduction criterion is circular as written. It expects "finding identities equal to the stored pin list". Nothing says where the 125-entry pin list comes from, and the spec forbids `validate` from generating it. The likely path is to build it from the production check's own output, which makes the comparison prove nothing. The independent reference is the prototype's log (`04-detector-tree-fusion-tea.log`), which records the input's qualified name and the target formal's qualified name for all 125 findings. The criterion needs to say the stored pin list is reconciled against that log (owner, input and target per entry), and that any difference is surfaced under the align record's premise-surprise rule, not absorbed into the pin list. The same applies to the dc3 zero results, which already have this form.

**L3-2 · Rewrite request (should-fix):** The register criterion requires every evidence citation to use the post-close `.project/completed/` path, and a test asserts each cited path exists. During implement and audit that folder does not exist yet, so the test fails until close moves the work folder. The criterion should say when the test is expected to pass, or what it checks before close.

**L3-3 · Rewrite request (should-fix):** "Every new or changed SysML example ... parses and passes L2 with zero `L2_POSITIONAL_BINDING` and zero `L2_SELF_NAMED_BINDING` findings." A teaching example with `in a = 10` raises `LITERAL_BINDING`, and a standalone `calc def` raises `UNUSED_DEFINITION`. Both are WARNINGs, so the example "fails L2" for reasons unrelated to this item. The criterion should require parse success and zero findings of the two named codes, not an L2 pass. Otherwise implementers will either bend examples to dodge unrelated warnings or reinterpret the criterion.

**L3-4 · If-then tradeoff (should-fix):** The "no redefinition evidence although the owner inherits unredefined inputs" state becomes an `L2_CHECK_UNVERIFIABLE` ERROR that no pin can downgrade. This is a prototype heuristic, and it misfired on a valid model in the prototype's first run (README surprise 3: SysIDE's `inherited_features` still lists redefined parent inputs). **If** it can fire on valid models, target projects get an ERROR they cannot clear. **If** it is only reachable through injected failures, it is safe. The spec should require fixtures for the valid shapes nearest to it, so design shows they do not trigger it: a usage with more inputs than its definition, a definition that adds a new first input without redeclaring the inherited ones (`calc def D :> Sub { in c; }`, which correctly flags `c → a`), and a definition with an `out` declared before an `in` (position counts `out` parameters, KerML 8.4.4.7.1).

**L3-5 · Rewrite request (minor):** "Canonical qualified-name spelling for keys" is deferred to design, but Item 1 already has one: `ElementRef.qualified_name` is `str(element.qualified_name)` (`subset_extraction.py:118-127`), and the spec already commits to reusing `ElementRef`. The deferral should say the key uses Item 1's spelling unless design shows it is unstable for quoted names, so design does not invent a second spelling. The spec's other reuse claim is accurate: `BindingSourceFact.formal` is the bound input member itself (`subset_extraction.py:210`), so the redefined-formal fact is genuinely new.

**L3-6 · Rewrite request (minor):** "Existing L2 tests pass without edits to their expectations" is right in intent. But if an existing fixture under `tests/fixtures/` happens to contain an implicit mismatch, the correct outcome is a new finding, not an unchanged expectation. I could not run the check against them. The criterion should say such a case is surfaced and justified in the evidence, not suppressed to keep expectations unchanged.

### Lens 4 — Hygiene

No material findings. Code citations I checked are accurate: `level2_structure.py:355-372` (the unverifiable pattern), `:450` (`success=len(all_issues) == 0`), `types.py:30-38` (the WARNING contract), `plant-idiom.md:298` (the "Order does not matter" line, about a redefine placed after a binding), `scripts/subset_profile/run_trees.py`, `tests/test_shipped_text.py`, docs packaged via `pyproject.toml:58`, and dc3 `design.md:63` / `RAW_LEARNINGS.md:29`.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request (minor):** The finding-condition bullet in Known Requirements is the core of the item but is one dense sentence with no example. After L1-1 is resolved, it should show one flagged and one passing example inline (for instance reversed unprefixed = FLAG, `in local redefines a` = PASS), so a reader can check the rule without opening the fixtures.

---

## Engagement Summary

**Overall take:** The spec is faithful to the epic and honest about its limits, gates and the fusion-tea consequence. Its weak point is the detection rule itself. It changed the prototype's rule in a way that misses mixed spellings, and it widened scope to requirements and cases that no evidence covers and that would be flagged on ordinary models. The fusion-tea reproduction also needs an independent reference, or it proves nothing.

**Must-fix before design:**

1. **[L1-1]** Restate the finding rule against the input's own explicit redefinitions (or justify the same-owner clause), and add the mixed-spelling fixture `in b = 3; in :>> a = 10;` (expected FLAG) plus a reversed deliberate-rename fixture.
2. **[L2-1, L1-3]** Exclude subject, actor and stakeholder parameters (or justify keeping them), with a differently-named-subject fixture (PASS) and a requirement-nested reversed constraint fixture (FLAG).
3. **[L3-1]** Make the fusion-tea reproduction compare against the prototype log's 125 identities, not against a pin list derived from the same check.

**Should-fix:**

4. **[L1-2]** Regrade D1 as ratified (`[INHERITED: epic D1] (ratified by owner 2026-10-15)`), matching Item 1's D2.
5. **[L2-2]** Record fusion-tea's current L2 result in the reproduction and restate the R4-3 consequence from it; owner question on what D1's "warn" should mean for L2 pass/fail.
6. **[L2-3]** State the required stale-pin behavior when only part of the tree is validated.
7. **[L3-2, L3-3, L3-4]** Fix the three criteria that will fail or mislead during implementation: post-close citation timing, "passes L2" for examples, and fixtures around the unverifiable heuristic.
8. **[L1-4, L3-5, L3-6, L5-1]** Minor: KerML-text vs SysIDE-observed wording in the register, reuse Item 1's qualified-name spelling, surface rather than suppress any existing-fixture finding, add an inline example to the finding rule.

---

## Resolutions

Resolved 2026-10-18. Decisions for the owner questions (L2-2, L2-3) were made by the orchestrator as execution of D1.

- **L1-1** `[AGENT]` — accepted. The finding rule now exempts an input only when its own declaration carries an explicit redefinition accounting for its positional target; another input's explicit redefinition never exempts it (the prototype's rule). Added the mixed-spelling fixture `in b = 3; in :>> a = 10;` (flagged at `b`) and the reversed deliberate-rename fixture `in y redefines b = 3; in x redefines a = 10;` (not flagged), with expected outcomes stated.
- **L1-2** `[AGENT]` — accepted. D1 regraded `[AGENT] (ratified by owner, 2026-10-15)`, matching Item 1's D2, in Problem and Known Requirements.
- **L1-3** `[AGENT]` — accepted. The scope reason now says neither consumer declares `subject`, `actor` or `stakeholder` parameters, so the baseline is silent on requirements and cases, which the new fixtures cover.
- **L1-4** `[AGENT]` — accepted. The register criterion requires "actual semantics" to separate KerML text from SysIDE 0.8.4 behavior observed on a named fixture, citing the parameterless-subdefinition case.
- **L2-1** `[AGENT]` — accepted. `subject`, `actor` and `stakeholder` parameters are excluded as a scoped exclusion with its reason (intended positional redefinition of library parameters). Ordinary `in` parameters of requirement and case definitions, and inputs of requirement-nested constraints, stay in scope. Added one not-flagged fixture per kind, a flagged swapped ordinary `in` parameter, and a flagged requirement-nested reversed constraint. Subject/actor/stakeholder ordering is listed as a non-goal.
- **L2-2** `[AGENT]` — decided as execution of D1: a pinned positional warning does not by itself make L2 fail; every other L2 code keeps its current pass/fail behavior (`level2_structure.py:450`). The R4-3 consequence no longer claims the pin move by itself changes fusion-tea's L2 outcome; it states that fusion-tea's current L2 status is unverified, and the reproduction criterion now records fusion-tea's L2 result without the check and with it, with and without the pin list.
- **L2-3** `[AGENT]` — decided: on partial validation a pin is stale only if its owner lies within the validated scope; pins outside are counted and reported as out-of-scope, never stale. Added a requirement and a partial-scope pytest criterion; how scope membership is decided is deferred to design.
- **L3-1** `[AGENT]` — accepted. The fusion-tea reference is the prototype's recorded log (`04-detector-tree-fusion-tea.log`). The pin list is built from that log, not from the check's output; every difference is itemized and surfaced as a premise surprise, never tuned away.
- **L3-2** `[AGENT]` — accepted. Register evidence citations use `.project/active/positional-binding-check/...` paths, which close rewrites; the existence test therefore passes during implement and audit.
- **L3-3** `[AGENT]` — accepted. The guidance-example criterion now requires parse success and the exact positional findings (none, or the stated identities for deliberate hazard examples), plus no self-named binding for by-name examples; other L2 warnings are excluded from it.
- **L3-4** `[AGENT]` — accepted. `L2_CHECK_UNVERIFIABLE` comes only from a real evidence failure (a raising read or an unresolvable fact); the prototype heuristic is dropped. Added `inherit_def_extends` (the prototype's first-run misfire) as a must-pass fixture, plus the reviewer's nearby valid shapes with stated or design-recorded expectations.
- **L3-5** `[AGENT]` — accepted. The identity key uses Item 1's qualified-name spelling (`ElementRef.qualified_name`) unless design shows it is unstable for quoted names; the separate deferral was removed.
- **L3-6** `[AGENT]` — accepted. Existing fixtures are run through the check, and any new positional finding is listed and justified in the evidence rather than suppressed.
- **L5-1** `[AGENT]` — accepted. The finding rule is now a numbered three-part condition with flagged and passing examples inline.
- **R4-1 (pin-list integrity, product-lens spec-F1)** `[AGENT] (ratified by owner 2026-10-18, "A is fine")` — pin-list integrity rests on review of the pin file; no digest. Recorded in Known Requirements; the open question was removed.

---

**Verdict:** Revise
**Next Steps:** Record the owner's answers to L2-2 and L2-3 here, then return to the spec agent (or re-run `/_my_spec`) and point it at this review. The reviewer does not edit the spec. L1-1 and L2-1 depend on what SysIDE 0.8.4 actually emits for explicit and subject parameters; the spec agent should write the fixtures' expected results from KerML/SysML text and let design confirm them against SysIDE, surfacing any disagreement.
