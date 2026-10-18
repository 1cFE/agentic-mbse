# Spec: Positional-binding hazard and check (EXEC-SUBSET-CONTRACT Item 4)

**Status:** Draft, revised after spec review (2026-10-18)
**Owner:** Reid Westwood
**Created:** 2026-10-18
**Complexity:** MEDIUM
**Branch:** `positional-binding-check` (off `main` at `ccd57d83`)

---

## Problem

In SysML v2, an unprefixed input on a calculation or constraint usage, such as `in b = 3;`, binds to the definition's parameter **by position**, not by name. KerML calls this implied redefinition (KerML 8.3.3.3.4, constraint `checkFeatureParameterRedefinition`). An author who writes correctly named inputs in a different order than the definition gets a silent swap. The model is valid SysML and nothing warns.

The swap gives wrong values, and the two execution routes disagree about it. For `calc def Sub { in a; in b; return r = a - b; }` with `a = 10, b = 3`, the reversed usage `in b = 3; in a = 10;` evaluates to **-7** in native SysIDE 0.8.4 and to **7** through sysml-codegen `b5663c07` and TEAx (prototype `04-eval.log`). Generated success therefore says nothing about native correctness, and the reverse.

The hazard is real in a consumer. The prototype detector finds 125 implicit mismatches in fusion-tea `f96ad312` across 9 files, and 0 in each dc3 tree (`808464d`, `60b44d5`). No fusion-tea route was regenerated or compared, so whether those 125 change any value is unknown.

The knowledge already existed and never reached authors. sysml-codegen recorded the positional behavior in July (`3bdf0b74` / `936315c8`, `tests/fixtures/modeled_default_fidelity/PROVENANCE.md`), filed POSITIONAL-FORMAL-REDEFINITION in August (`f0a7b0a9`), and corrected its premise in October (`bd352744`); the item is still open. agentic-mbse ships no check and no guidance for it, and `docs/patterns/plant-idiom.md:298` says "Order does not matter" about a different ordering, which reads as reassurance here.

Item 4 adds one L2 check, the fixtures that prove it, a semantic-hazard register entry and guidance edits. It does not change how either route binds.

The governing policy is decision D1 `[AGENT] (ratified by owner, 2026-10-15)` (epic "Owner decisions"): "Block new mismatches and warn on explicitly pinned legacy cases until migration. Fusion-tea migration is separate authorized work, not a prerequisite for accepting this toolkit check. Legacy warning acceptance does not certify cross-route semantic parity."

## Success Criteria

Paths below are the intended homes; design may rename them, but each criterion must keep a named artifact or test that proves it. "Finding identity" means the triple (owner qualified name, input declared name, target formal qualified name), defined in Known Requirements. A "pin list" is the project-owned file of legacy finding identities that D1 downgrades to warnings.

**Detection**

- [ ] A retained fixture set under `tests/fixtures/positional_binding/` covers, at minimum, the 17 prototype detector cases (`.project/concepts/convince-me-exec-subset/evidence/04-fixtures/detector/`), each with a header stating its expected flagged identities. A pytest module (`tests/test_validation/test_positional_binding.py`) asserts the **exact set of finding identities** per fixture, not only pass/flag. The cases include: reversed calc usage, reversed constraint usage, reversed `assert constraint`, omitted first input, defaulted trailing input, anonymous inputs, explicit by-name (`in :>> b`), the `redefines` keyword spelling, deliberate rename (`in local redefines a = ...`), untyped new parameters, in-order inputs, definition-to-definition inheritance (extending and reordering), a usage typed by a parameterless subdefinition, a usage redefined in a subpart, and a usage with multiple types.
- [ ] The same module contains the cases the prototype's name-set control got wrong (`04-detector-naive-control.log`: 9 of 17), so a detector that compared names instead of resolved redefinition targets fails the suite.
- [ ] Two spelling fixtures, against `calc def Sub { in a; in b; ... }`:
  - Mixed spelling `in b = 3; in :>> a = 10;`: **flagged** at `b` (it implicitly redefines `Sub::a`); the `:>> a` input is not flagged. Another input's explicit redefinition does not exempt `b`.
  - Reversed deliberate rename `in y redefines b = 3; in x redefines a = 10;`: **not flagged**. Each input's own explicit redefinition states its target.
- [ ] Fixtures for requirement and case parameters:
  - One per special parameter kind, each **not flagged**: a requirement def with a differently named `subject`, a requirement or case with an `actor`, and a requirement with a `stakeholder`.
  - An ordinary `in` parameter of a requirement or case definition, positionally swapped in a usage: **flagged**.
  - A reversed constraint usage nested in a requirement (`assert`/`require`/`assume constraint`): **flagged**.
- [ ] A fixture reproducing the dc3 out-of-order shape (dc3 WI-008 `design.md:63`, `RAW_LEARNINGS.md:29`) and a fixture reproducing the prototype's dc3 swap mutation (two inputs of `'Serial Path 8'`, dc3 `60b44d5` `designs/ac_coupled/ac_facility.sysml:226-227`), each reduced to a minimal model that cites its dc3 source and revision, are flagged at exactly the swapped inputs.
- [ ] Valid shapes near the old prototype heuristic, each with a stated expected result: the prototype's first-run misfire `inherit_def_extends` (**must pass**, no finding and no unverifiable result; `04-README.md` surprise 3); a usage with more inputs than its definition (extra inputs are new parameters, not flagged); a definition that adds a new first input without redeclaring the inherited ones (`calc def D :> Sub { in c; }`, flagged `c → Sub::a`); and a definition with an `out` declared before an `in` (expected result recorded in design from SysIDE output).
- [ ] The multiple-types fixture (an input with an explicit redefinition of one type's formal and an implied redefinition of another type's formal) has a stated expected result per the finding rule, confirmed against SysIDE in design.
- [ ] Existing fixtures under `tests/fixtures/` are run through the check. Any new positional finding there is listed and justified in the evidence, not suppressed to keep existing expectations unchanged.

**Policy (D1)**

- [ ] A pytest with a small fixture model and a pin list shows: an unpinned mismatch is an `L2_POSITIONAL_BINDING` ERROR and fails L2; a pinned mismatch is an `L2_POSITIONAL_BINDING` WARNING and does not by itself fail L2; a pinned owner/input whose target changed is reported as a new ERROR plus a stale pin; a pin with no matching finding is reported as a stale pin and fails the run until the entry is removed.
- [ ] The same test shows that with no pin list every mismatch is an ERROR, and that a malformed or unreadable pin list, or one without its recorded-against header, is a reported error, never treated as an empty list.
- [ ] A pytest validates only part of a pinned fixture tree. Pins whose owners lie outside the validated scope are counted and reported as out-of-scope, not stale, and do not fail the run. A pin inside the scope with no matching finding is still stale.
- [ ] The pinned-WARNING message and the register entry both say that a pin does not certify correct native values or agreement between routes, and the L2 summary reports pinned findings as a separate count, never folded into a clean result. A test asserts both.
- [ ] Every other L2 code keeps its current pass/fail behavior (`level2_structure.py:450`): `tests/test_validation/test_integration_regression.py` and the existing L2 tests pass, apart from any justified new positional finding listed under Detection.

**Inspection failures cannot pass silently**

- [ ] A pytest injects an inspection failure (a raising redefinition read) for one input, and separately for one owner's input enumeration. Each yields an `L2_CHECK_UNVERIFIABLE` ERROR naming the element, L2 fails, and mismatches on other owners in the same model are still reported. A pin list cannot downgrade it.
- [ ] `L2_CHECK_UNVERIFIABLE` comes only from a real evidence failure (a read that raises, or a fact that cannot be resolved, such as a redefinition with no resolvable target). The prototype's "owner inherits inputs no redefinition covers" heuristic is not carried over. The must-pass `inherit_def_extends` fixture above proves it.
- [ ] The L2 metrics report the number of inputs inspected alongside the finding counts. A consumer reproduction (below) that inspects zero inputs fails rather than reporting zero findings.

**Pinned consumer baselines**

- [ ] The fusion-tea reference is the prototype's recorded log, `.project/concepts/convince-me-exec-subset/evidence/04-detector-tree-fusion-tea.log`, which gives the input and target qualified names for all 125 findings. The fusion-tea pin list at `tests/fixtures/positional_binding/baselines/fusion-tea-f96ad312.<ext>` is built from that log, not from the production check's output. It holds 125 distinct identities, each with its source location recorded for review and scope but not part of the key.
- [ ] A reproduction script (`scripts/positional_binding/run_trees.py`, following Item 1's `scripts/subset_profile/run_trees.py`) runs the production check on `git archive` copies of fusion-tea `f96ad312` `models/` and dc3 `808464d` and `60b44d5` `models/`, and writes a log with all repository revisions and the SysIDE version to `.project/active/positional-binding-check/evidence/`.
  - fusion-tea: the check's finding identities are compared with the 125 log identities. Every difference (added, missing, or changed target) is itemized in the log. Any difference is a premise surprise to surface to the owner, not something to tune the detector or the pin list toward. Expected with no difference: 125 WARNINGs, 0 ERRORs and 0 unverifiable from this check.
  - dc3: 0 findings and 0 unverifiable in each tree.
  - Inspected-input counts per tree are compared with the prototype's (dc3 302 and 391 implicit same-name inputs; fusion-tea 5,573 matching plus 125 mismatches), and any difference is explained.
  - fusion-tea's current L2 result is recorded **without** this check, and its L2 result with the check, with and without the pin list. This measures what the check actually changes for fusion-tea.
- [ ] A slow pytest (`-m slow`) wraps the same comparison. It runs when a pinned tree path is supplied by environment variable and otherwise skips with a reason that names the missing tree; a skip is never reported as a pass.
- [ ] The reproduction also swaps two in-order inputs in a scratch copy of the fusion-tea tree and shows one or more new ERROR identities while the pin list is unchanged, and removes one legacy mismatch by rewriting it to `in :>>` form in a scratch copy and shows a stale-pin failure. Both are in the evidence log.

**Cross-route counterexample**

- [ ] The four-spelling native evaluation is a pytest in this repo: in-order unprefixed 7, reversed unprefixed -7, reversed `in :>>` 7, explicit rename 7, under SysIDE 0.8.4, using retained copies of the prototype models (`04-fixtures/gen_reversed/`, `04-fixtures/gen_byname/` and the `Sub` calc).
- [ ] The generated/TEAx side (reversed 7, by-name 7 at codegen `b5663c07`, TEAx `8d877460`) is retained as a re-runnable script plus captured log in the item's evidence folder, run from an environment that has codegen installed. agentic-mbse code does not import codegen.

**Register and guidance**

- [ ] `docs/patterns/semantic-hazards.md` exists and ships in the wheel (existing packaged-guidance contract). Its positional entry states the expected reading, the actual semantics, KerML 8.3.3.3.4 `checkFeatureParameterRedefinition`, the verified tool versions, the detector and its limits, the retained fixture paths, and the upstream links. Its "actual semantics" text separates what the KerML text says from what SysIDE 0.8.4 was observed to do on a named fixture (for example, the parameterless-subdefinition case, where SysIDE resolves through to the supertype's parameters). Because the register ships to target repos where this repo's tests and `.project/` do not exist, each citation names its repository and pinned revision. Evidence citations use `.project/active/positional-binding-check/...` paths, which close rewrites to the archive path. A test in `tests/test_shipped_text.py` asserts that every cited path exists and that the KerML constraint name is cited.
- [ ] `docs/patterns/plant-idiom.md`, `skills/sysml-conventions/SKILL.md`, `project_templates/MODELING_GUIDE.md.template` and the expert roles in `agents/` that teach calc-usage inputs teach the by-name form or definition order, distinguish deliberate renaming, qualify "Order does not matter" (`plant-idiom.md:298`) by its actual context, and link the register entry. They link the existing self-binding contract rather than restating it. A shipped-text test asserts the links and the qualification.
- [ ] Every new or changed SysML example in those files parses, and a test asserts its exact positional findings: none for ordinary examples, and the stated identities for any example that deliberately shows the hazard. By-name examples also have no `L2_SELF_NAMED_BINDING` finding (`in :>> x = x` would be a self-binding; examples bind a distinct path). Other L2 warnings, such as `LITERAL_BINDING` or `UNUSED_DEFINITION`, are not part of this criterion.
- [ ] A draft upstream finding for sysml-codegen sits in the item's evidence folder, linked from the register. It records the observed name-based wiring at `b5663c07`, the native positional result, the fixtures, and its relation to POSITIONAL-FORMAL-REDEFINITION, without proposing a binding change. The register says the finding is unfiled until it is filed. Filing it in sysml-codegen is the owner's call (or Item 2's, which links that item to the register); at close it is listed as an open item in `.project/CURRENT_WORK.md`.

**Repository checks**

- [ ] `uv run pytest tests/`, `uv run mypy src/` and `uv run ruff check src/ tests/` pass. The evidence states which tests needed the SysIDE licence and which slow tests ran or skipped.

## Known Requirements

**Policy and wording**

- **[INFERRED]** D1 `[AGENT] (ratified by owner, 2026-10-15)`, quoted in Problem. New or changed mismatch identities block; explicitly pinned legacy identities warn until migration. Graded ratified, matching Item 1's grading of D2 from the same discussion (Item 1 `product-lens.md` spec-F2). A later agent challenges a detail of it by re-deriving against its reasoning.
- **[INFERRED]** "Warn" means a pinned positional warning does not by itself make L2 fail. Every other L2 code keeps its current effect on pass/fail: today L2 fails on any issue, warnings included (`level2_structure.py:450`, `success=len(all_issues) == 0`). So a project that has other L2 warnings still fails L2 for those. Graded `[AGENT]`, decided by the orchestrator as execution of D1 (spec review L2-2).
- **[INHERITED: epic Item 4 scope 1]** The finding is described as a likely authoring hazard in valid SysML. No message, code name or doc calls the construct invalid.
- **[INHERITED: epic Item 4 audit clarification, prototype `04-README.md`]** The suggestion names both repairs, by-name (`in :>> target`) and deliberate rename (`in name redefines target`), and tells the author to choose the intended formal from the source, not to adopt the currently inferred positional target.

**What the check inspects**

- **[INHERITED: epic Item 4 scope 1]** Detection uses resolved redefinition relationships and whether each is implied or explicit, never equality of name sets.
- **[INHERITED: epic Item 4 scope 2]** Cover calculation and constraint usages, inheritance, explicit renaming, anonymous features, omitted and defaulted inputs, multiple targets and unavailable evidence.
- **[INFERRED]** The finding rule. An authored input is flagged for an implied redefinition target when all three hold:
  1. the input has a declared name;
  2. the target's name differs from it;
  3. the input's **own** declaration carries no explicit redefinition that accounts for that target.

  Another input's explicit redefinition never exempts it. With one type, any explicit redefinition on the input's own declaration accounts for its positional target, because it states the author's chosen target. With several types, an implied target is accounted for only by the input's own explicit redefinition of a formal of the same definition; design confirms this against SysIDE on the multiple-types fixture. Examples: `in b = 3; in a = 10;` flags both inputs; `in b = 3; in :>> a = 10;` flags `b`; `in local redefines a = 10; in b = 3;` and `in y redefines b = 3; in x redefines a = 10;` flag nothing. Graded `[AGENT]` (spec review L1-1). Reason: this is the prototype's rule (`04-detector.py:117-141`). It also covers the case where KerML gives an explicitly redefined input an implied positional redefinition too.
- **[INFERRED]** Owners scanned are calculation and constraint usages and definitions, including their SysML subtypes (requirements, cases, `assert constraint`). Reason: the KerML rule applies to them alike, and the 125-finding baseline was measured with this scope. Neither consumer declares `subject`, `actor` or `stakeholder` parameters, so the baseline says nothing about requirements and cases; the requirement and case fixtures cover them.
- **[INFERRED]** Parameters declared with the `subject`, `actor` or `stakeholder` keyword are excluded. Graded `[AGENT]` (spec review L2-1). Reason: they are special parameters whose positional redefinition of library parameters is intended. For example, every requirement def specializes the library `RequirementCheck`, so `subject vehicle` implicitly redefines `RequirementCheck::subj` on nearly every requirement (SysML 7.21.2, 8.4.17.2). The exclusion covers only those three kinds. Ordinary `in` parameters of requirement and case definitions, and inputs of constraints nested in requirements, stay in scope.
- **[INFERRED]** Directions inspected are `in` and `inout`; `out` and return parameters are not. Reason: the epic and the prototype both scope to inputs, and output ordering is a different hazard (fusion-tea `RAW_LEARNINGS.md:80` concerns output-tuple ordering and is not evidence here).
- **[INFERRED]** An input with no declared name passes. Reason: it expresses no name that could disagree with its target.
- **[INFERRED]** Findings are reported only on user-model elements, never on standard-library elements. Reason: Item 1's extraction already excludes the standard library, and an author cannot act on a library finding.
- **[INFERRED]** The check reuses Item 1's identity and location types (`ElementRef`, `SafeLocation` in `src/agentic_mbse/sysml/fact_refs.py`) and its defensive-read conventions. Item 1 has no fact for the formal an input redefines (`BindingSourceFact.formal` in `subset_facts.py` is the input itself), so the check adds that one fact rather than re-deriving anything Item 1 already extracts.

**Identity and the pin list**

- **[INHERITED: epic Item 4 scope 5]** Legacy findings are recorded by stable owner/input/target identity, not by count. Adding a mismatch fails; a disappearing legacy finding requires baseline reconciliation.
- **[INFERRED]** Finding identity is (owner qualified name, input declared name, target formal qualified name), using Item 1's qualified-name spelling (`ElementRef.qualified_name`, `str(element.qualified_name)`, `subset_extraction.py:118-127`) unless design shows it is unstable for quoted names. File and line are recorded but excluded from the key. Reason: lines move on unrelated edits; names change only when the binding itself changes.
- **[INFERRED]** A finding whose owner has no qualified name cannot be pinned and stays an ERROR, with a message saying why. Reason: without a stable key it cannot be matched to a pin.
- **[INFERRED]** A stale pin (no matching finding) fails the run. Reason: a stale entry would silently whitelist the same mismatch if it were reintroduced later, which defeats "new mismatches block".
- **[INFERRED]** When only part of a tree is validated, a pin is judged stale only if its owner lies within the validated scope. Pins outside the scope are counted and reported as out-of-scope, never as stale. A full-tree run judges every pin. How scope membership is decided (for example, from the pin's recorded file) is design. Graded `[AGENT]` (spec review L2-3).
- **[INFERRED]** The pin list is a project-owned, reviewable text file. `validate` never writes or extends it, and nothing in this item generates entries automatically. Reason: the epic says intentional positional use needs a documented disposition "rather than an automatic new baseline entry".
- **[INFERRED]** The pin list carries a header naming the model revision and date it was recorded against, and each entry is a finding identity that existed at that revision. Reason: D1 warns only on *legacy* cases, so a pin must say what it is legacy relative to.
- **[INFERRED]** Pin-list integrity rests on review of the pin file. There is no digest or other tamper check. The check cannot see version history, so a pin hand-added later for a new mismatch is caught only by review. Graded `[AGENT] (ratified by owner 2026-10-18, "A is fine")`; this decides the R4-1 question raised by product-lens spec-F1.
- **[INFERRED]** The pin list can be supplied from outside the model tree (for example, by an explicit CLI option). Reason: the fusion-tea baseline must be applied to a read-only pinned tree, and fusion-tea edits are reserved (R4-3).
- **[INFERRED]** A pin only downgrades a matching mismatch from ERROR to WARNING. It never hides a finding, never applies to `L2_CHECK_UNVERIFIABLE`, and carries no "intentional" meaning. Anything that does more is gate R4-1.

**Inspection failures**

- **[INHERITED: epic Item 4 scope 2; principle 5]** Unverifiable inspections are reported separately using the existing L2 failure pattern: `L2_CHECK_UNVERIFIABLE` at ERROR (`level2_structure.py:355-372`). Unrelated owners continue to be checked.
- **[INFERRED]** An unverifiable result comes only from a real evidence failure: a read that raises, or a fact that cannot be resolved. A shape-based guess about missing redefinitions is not evidence failure. Graded `[AGENT]` (spec review L3-4). Reason: an ERROR no pin can clear must not fire on valid models; the prototype heuristic misfired on `inherit_def_extends` because SysIDE's `inherited_features` still lists redefined parent inputs.

**Fixtures and evidence**

- **[INHERITED: epic Item 4 scope 3]** The audit probes become retained minimal fixtures, and the cross-route subtraction counterexample (native -7, generated/TEAx 7) and the SysIDE 0.8.4 observations listed in scope 3 are retained as durable fixtures. `/tmp/consumer-audit-byname/` artifacts are not acceptance evidence.
- **[INHERITED: epic "Evidence and regression revisions"]** Consumer trees are read through `git archive` of pinned revisions into scratch directories. Consumer checkouts are never modified and whole consumer models are not mirrored into this repo.
- **[INHERITED: align record]** If the 125 fusion-tea identities or the dc3 zero-finding results do not reproduce, surface the difference to the owner rather than tune the detector.
- **[INFERRED]** The fusion-tea comparison uses the prototype log as its independent reference. Graded `[AGENT]` (spec review L3-1). Reason: a pin list built from the production check's own output would make the comparison prove nothing.
- **[INFERRED]** The generator side of the counterexample is evidence (script and log), not a pytest. Reason: agentic-mbse must never import sysml-codegen (epic principle 1), and TEAx is not a dependency here.

**Register and guidance**

- **[INHERITED: epic Item 4 scope 4]** The register cites KerML `checkFeatureParameterRedefinition` for positional semantics. The nearby constructor named-argument passage is about constructor notation and is not cited as proof of calc-usage syntax.
- **[INHERITED: epic Item 4 scope 4]** Output-override and `[*]`/`[0]` entries are scoped to reproduced forms, not universal claims.
- **[INFERRED]** Item 4 writes the positional entry in full. It adds an output-override or `[*]`/`[0]` entry only where a retained reproduction exists; otherwise the register lists it as a candidate with "not yet reproduced". Reason: scope 4 forbids unreproduced claims, and reproducing those hazards is not otherwise in Item 4.
- **[INFERRED]** The register claims cross-route divergence only for calculation usages. Reason: only the calc case was run through both routes; codegen's `PROVENANCE.md` "Authoring note" says constraint actuals bind positionally in codegen, so the constraint-usage routes may agree.
- **[INHERITED: epic Item 4 scope 6]** Guidance updates use verified by-name redefinition where appropriate or preserve definition order, distinguish explicit renaming, qualify "Order does not matter" by its actual context, and link the existing self-binding contract instead of replacing it.
- **[INFERRED]** The positional register entry has a stable anchor. Reason: Items 2 and 5 link to it (epic Item 2 dependencies, Item 5 dependencies).
- **[INFERRED]** The upstream record is a draft in this item's evidence folder. Reason: sysml-codegen is read-only for this work, and the epic asks to record the discrepancy, not to change generator behavior.

## Non-Goals

- Changing how sysml-codegen or SysIDE binds inputs (gate R4-2).
- Editing or migrating fusion-tea, including adding a pin list to it (gate R4-3).
- Proving whether the 125 fusion-tea mismatches change any value. D1 does not require it, and it needs regeneration and comparison in fusion-tea.
- Action, state or other behavior parameters, and output or return parameters. The KerML rule also covers actions; extending the check there is possible follow-up work, not required by the epic.
- Ordering hazards among `subject`, `actor` and `stakeholder` parameters (a stakeholder landing on an actor slot, say). That is a different check.
- Executing every shipped SysML example (Item 5's fence harness). Item 4 checks only the examples it adds or changes.
- Execution-target settings and L6 severity routing (Item 3).

## Open Questions / Deferred to design

**Owner gates (align record)**

- **R4-1:** any narrow suppression or "intentional positional use" disposition beyond D1's legacy pin stays reserved to the owner. Until one is decided, a new deliberate positional use has to be written explicitly (`in name redefines target`), which valid SysML always allows, so no author is blocked. The pin-list integrity question within R4-1 is decided (review of the pin file; see Known Requirements).
- **R4-2:** any change to generator binding behavior.
- **R4-3:** any fusion-tea edit. **What is known about the consequence:** without a pin list, the check adds 125 `L2_POSITIONAL_BINDING` ERRORs to fusion-tea's L2 once fusion-tea moves its agentic-mbse pin to a release with this check. With the pin list, those become warnings that do not by themselves fail L2. **Unverified:** whether fusion-tea's L2 passes today. If it already fails on other warnings, the pin list does not make it pass. The reproduction measures this (Success Criteria, "Pinned consumer baselines"). Adding the pin list to fusion-tea, or migrating its bindings, are fusion-tea edits under this gate.

**Surfaced conflict, not resolved here**

- sysml-codegen's backlog entry for POSITIONAL-FORMAL-REDEFINITION (as corrected by `bd352744`) says "Current elaboration follows parser redefinition identity". The prototype shows codegen `b5663c07` wiring the reversed calc usage by declared name (`04-eval.log`: `a` wired to `big`, result 7), while the parser's redefinition is positional (-7). These cannot both describe the same case. The draft upstream finding records both; the codegen owner decides which is right. The check does not depend on the answer.

**Deferred to design**

- Pin-list location, file format and how `validate` finds it in a target project, with an explicit override. It must work before Item 3's `[tool.agentic-mbse]` settings exist; whether it later moves under them is Item 3's call.
- How the check decides whether a pin's owner lies within the validated scope.
- Whether `init` mentions the pin list. If it ships a starter, it is a user-owned document and stays absent by default (no pins means every mismatch blocks).
- Expected results that depend on what SysIDE 0.8.4 emits: the multiple-types case, the `out`-before-`in` case, and whether explicitly redefined inputs also carry implied positional redefinitions. Write expectations from KerML/SysML text first, confirm against SysIDE, and surface any disagreement (`kerml-expert`/`sysml-expert` if needed).
- Message text, metric names and whether the check lives in `level2_structure.py` or a sibling module.
- The epic's "dc3 interleave mutation" is read here as the two dc3 shapes above (WI-008 out-of-order inputs and the prototype's adjacent swap). If it meant a different probe, design should name it.
- Which `agents/` roles carry calc-usage input guidance.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_executable-subset-contract.md` (Item 4; D1; Prototype findings; Root causes)
- **Align record:** `.project/active/positional-binding-check/briefs/align.md`
- **Spec brief:** `.project/active/positional-binding-check/briefs/spec.md`
- **Spec review:** `.project/active/positional-binding-check/spec-review.md` (verdict Revise; resolutions recorded there)
- **Required Reading:** none listed for Item 4 in the epic. Prototype evidence used: `.project/concepts/convince-me-exec-subset/evidence/04-README.md`, `04-detector.py`, `04-fixtures/`, `04-*.log`
- **Item 1 archive:** `.project/completed/20261018_exec-subset-profile/` (reproduction pattern: `scripts/subset_profile/run_trees.py`)
- **Upstream:** sysml-codegen `.project/backlog/BACKLOG.md` POSITIONAL-FORMAL-REDEFINITION; `tests/fixtures/modeled_default_fidelity/PROVENANCE.md`; fusion-tea `modeling_project/ARCHITECTURE.md` AD-008; dc3 `work/active/WI-008_generator-idiom/design.md:63`
- **Product lens:** `.project/active/positional-binding-check/product-lens.md`
- **Design:** `.project/active/positional-binding-check/design.md` (to be created)

---

**Next Steps:** `/_my_design`.
