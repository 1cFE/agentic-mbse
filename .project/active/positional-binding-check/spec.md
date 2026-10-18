# Spec: Positional-binding hazard and check (EXEC-SUBSET-CONTRACT Item 4)

**Status:** Draft
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

The governing policy is owner decision D1 `[OWNER]` (approved 2026-10-15, epic "Owner decisions"): "Block new mismatches and warn on explicitly pinned legacy cases until migration. Fusion-tea migration is separate authorized work, not a prerequisite for accepting this toolkit check. Legacy warning acceptance does not certify cross-route semantic parity."

## Success Criteria

Paths below are the intended homes; design may rename them, but each criterion must keep a named artifact or test that proves it. "Finding identity" means the triple (owner qualified name, input declared name, target formal qualified name), defined in Known Requirements.

**Detection**

- [ ] A retained fixture set under `tests/fixtures/positional_binding/` covers, at minimum, the 17 prototype detector cases (`.project/concepts/convince-me-exec-subset/evidence/04-fixtures/detector/`), each with a header stating its expected flagged identities. A pytest module (`tests/test_validation/test_positional_binding.py`) asserts the **exact set of finding identities** per fixture, not only pass/flag. The cases include: reversed calc usage, reversed constraint usage, reversed `assert constraint`, omitted first input, defaulted trailing input, anonymous inputs, explicit by-name (`in :>> b`), the `redefines` keyword spelling, deliberate rename (`in local redefines a = ...`), untyped new parameters, in-order inputs, definition-to-definition inheritance (extending and reordering), a usage typed by a parameterless subdefinition, a usage redefined in a subpart, and a usage with multiple types.
- [ ] The same module contains the cases the prototype's name-set control got wrong (`04-detector-naive-control.log`: 9 of 17), so a detector that compared names instead of resolved redefinition targets fails the suite.
- [ ] A fixture reproducing the dc3 out-of-order shape (dc3 WI-008 `design.md:63`, `RAW_LEARNINGS.md:29`) and a fixture reproducing the prototype's dc3 swap mutation (two inputs of `'Serial Path 8'`, dc3 `60b44d5` `designs/ac_coupled/ac_facility.sysml:226-227`), each reduced to a minimal model that cites its dc3 source and revision, are flagged at exactly the swapped inputs.
- [ ] A fixture where an input has an explicit redefinition of one target and an implied redefinition of another (for example, a usage with two types) has a stated expected result and is tested. The prototype skipped every implied relationship once any explicit one existed; this case decides whether that was right.

**Policy (D1)**

- [ ] A pytest with a small fixture model and a pin list shows: an unpinned mismatch is an `L2_POSITIONAL_BINDING` ERROR and fails L2; a pinned mismatch is an `L2_POSITIONAL_BINDING` WARNING and does not by itself fail L2 or the `validate` exit code; a pinned owner/input whose target changed is reported as a new ERROR plus a stale pin; a pin with no matching finding is reported as a stale pin and fails the run until the entry is removed.
- [ ] The same test shows that with no pin list every mismatch is an ERROR, and that a malformed or unreadable pin list, or one without its recorded-against header, is a reported error, never treated as an empty list.
- [ ] The pinned-WARNING message and the register entry both say that a pin does not certify correct native values or agreement between routes, and the L2 summary reports pinned findings as a separate count, never folded into a clean result. A test asserts both.
- [ ] Existing L2 pass/fail behavior for every other code is unchanged: `tests/test_validation/test_integration_regression.py` and the existing L2 tests pass without edits to their expectations.

**Inspection failures cannot pass silently**

- [ ] A pytest injects an inspection failure (a raising redefinition read) for one input, and separately for one owner's input enumeration. Each yields an `L2_CHECK_UNVERIFIABLE` ERROR naming the element, L2 fails, and mismatches on other owners in the same model are still reported. A pin list cannot downgrade it.
- [ ] A pytest covers the "no redefinition evidence although the owner inherits unredefined inputs" state and asserts it is `L2_CHECK_UNVERIFIABLE`, not a pass.
- [ ] The L2 metrics report the number of inputs inspected alongside the finding counts. A consumer reproduction (below) that inspects zero inputs fails rather than reporting zero findings.

**Pinned consumer baselines**

- [ ] The 125 fusion-tea findings are stored as a pin list in the same format target projects use, at `tests/fixtures/positional_binding/baselines/fusion-tea-f96ad312.<ext>`, one entry per finding identity, with the source location recorded for review but not part of the key. It holds 125 distinct identities.
- [ ] A reproduction script (`scripts/positional_binding/run_trees.py`, following Item 1's `scripts/subset_profile/run_trees.py`) runs the production check on `git archive` copies of fusion-tea `f96ad312` `models/` and dc3 `808464d` and `60b44d5` `models/`, and writes a log with all repository revisions and the SysIDE version to `.project/active/positional-binding-check/evidence/`. Expected: fusion-tea, finding identities equal to the stored pin list, 125 WARNINGs, 0 ERRORs and 0 unverifiable from this check; dc3, 0 findings and 0 unverifiable in each tree. The log records inputs inspected per tree and compares them with the prototype's counts (dc3 302 and 391 implicit same-name inputs; fusion-tea 5,573 matching plus 125 mismatches); any difference is explained there, not ignored.
- [ ] A slow pytest (`-m slow`) wraps the same comparison. It runs when a pinned tree path is supplied by environment variable and otherwise skips with a reason that names the missing tree; a skip is never reported as a pass.
- [ ] The reproduction also swaps two in-order inputs in a scratch copy of the fusion-tea tree and shows one or more new ERROR identities while the pin list is unchanged, and removes one legacy mismatch by rewriting it to `in :>>` form in a scratch copy and shows a stale-pin failure. Both are in the evidence log.

**Cross-route counterexample**

- [ ] The four-spelling native evaluation is a pytest in this repo: in-order unprefixed 7, reversed unprefixed -7, reversed `in :>>` 7, explicit rename 7, under SysIDE 0.8.4, using retained copies of the prototype models (`04-fixtures/gen_reversed/`, `04-fixtures/gen_byname/` and the `Sub` calc).
- [ ] The generated/TEAx side (reversed 7, by-name 7 at codegen `b5663c07`, TEAx `8d877460`) is retained as a re-runnable script plus captured log in the item's evidence folder, run from an environment that has codegen installed. agentic-mbse code does not import codegen.

**Register and guidance**

- [ ] `docs/patterns/semantic-hazards.md` exists and ships in the wheel (existing packaged-guidance contract). Its positional entry states the expected reading, the actual semantics, KerML 8.3.3.3.4 `checkFeatureParameterRedefinition`, the verified tool versions, the detector and its limits, the retained fixture paths, and the upstream links. Because the register ships to target repos where this repo's tests and `.project/` do not exist, each citation names its repository and pinned revision, and evidence citations use the post-close `.project/completed/` path. A test in `tests/test_shipped_text.py` asserts that every cited path exists at that form and that the KerML constraint name is cited.
- [ ] `docs/patterns/plant-idiom.md`, `skills/sysml-conventions/SKILL.md`, `project_templates/MODELING_GUIDE.md.template` and the expert roles in `agents/` that teach calc-usage inputs teach the by-name form or definition order, distinguish deliberate renaming, qualify "Order does not matter" (`plant-idiom.md:298`) by its actual context, and link the register entry. They link the existing self-binding contract rather than restating it. A shipped-text test asserts the links and the qualification.
- [ ] Every new or changed SysML example in those files parses and passes L2 with zero `L2_POSITIONAL_BINDING` and zero `L2_SELF_NAMED_BINDING` findings, checked by a test. (A by-name example such as `in :>> x = x` would be a self-binding; the examples must bind a distinct path.)
- [ ] A draft upstream finding for sysml-codegen sits in the item's evidence folder, linked from the register. It records the observed name-based wiring at `b5663c07`, the native positional result, the fixtures, and its relation to POSITIONAL-FORMAL-REDEFINITION, without proposing a binding change. The register says the finding is unfiled until it is filed. Filing it in sysml-codegen is the owner's call (or Item 2's, which links that item to the register); at close it is listed as an open item in `.project/CURRENT_WORK.md`.

**Repository checks**

- [ ] `uv run pytest tests/`, `uv run mypy src/` and `uv run ruff check src/ tests/` pass. The evidence states which tests needed the SysIDE licence and which slow tests ran or skipped.

## Known Requirements

**Policy and wording**

- **[NEED]** D1 as quoted in Problem `[OWNER]`. New or changed mismatch identities block; explicitly pinned legacy identities warn until migration. Graded owner per the align record and the spec brief. Item 1 graded D2, approved in the same 2026-10-15 discussion, as ratified rather than owner-originated (Item 1 `product-lens.md` spec-F2); spec review should confirm which applies to D1. This spec does not challenge D1 either way.
- **[INHERITED: epic Item 4 scope 1]** The finding is described as a likely authoring hazard in valid SysML. No message, code name or doc calls the construct invalid.
- **[INHERITED: epic Item 4 audit clarification, prototype `04-README.md`]** The suggestion names both repairs, by-name (`in :>> target`) and deliberate rename (`in name redefines target`), and tells the author to choose the intended formal from the source, not to adopt the currently inferred positional target.

**What the check inspects**

- **[INHERITED: epic Item 4 scope 1]** Detection uses resolved redefinition relationships and whether each is implied or explicit, never equality of name sets.
- **[INHERITED: epic Item 4 scope 2]** Cover calculation and constraint usages, inheritance, explicit renaming, anonymous features, omitted and defaulted inputs, multiple targets and unavailable evidence.
- **[INFERRED]** The finding condition, per authored input and per implied redefinition target: the input has a declared name, the target's name differs from it, and no explicit redefinition by an input of the same owner targets that formal. Reason: this is the epic's wording ("without an explicit redefinition accounting for the target") made per-target, so multiple types are handled one target at a time.
- **[INFERRED]** Owners scanned are calculation and constraint usages and definitions, including their SysML subtypes (requirements, cases, `assert constraint`). Reason: the KerML rule applies to them alike, and the 125-finding baseline was measured with exactly this scope; a narrower scope would break the baseline comparison for a reason unrelated to the hazard.
- **[INFERRED]** Directions inspected are `in` and `inout`; `out` and return parameters are not. Reason: the epic and the prototype both scope to inputs, and output ordering is a different hazard (fusion-tea `RAW_LEARNINGS.md:80` concerns output-tuple ordering and is not evidence here).
- **[INFERRED]** An input with no declared name passes. Reason: it expresses no name that could disagree with its target.
- **[INFERRED]** Findings are reported only on user-model elements, never on standard-library elements. Reason: Item 1's extraction already excludes the standard library, and an author cannot act on a library finding.
- **[INFERRED]** The check reuses Item 1's identity and location types (`ElementRef`, `SafeLocation` in `src/agentic_mbse/sysml/fact_refs.py`) and its defensive-read conventions. Item 1 has no fact for the formal an input redefines (`BindingSourceFact.formal` in `subset_facts.py` is the input itself), so the check adds that one fact rather than re-deriving anything Item 1 already extracts.

**Identity and the pin list**

- **[INHERITED: epic Item 4 scope 5]** Legacy findings are recorded by stable owner/input/target identity, not by count. Adding a mismatch fails; a disappearing legacy finding requires baseline reconciliation.
- **[INFERRED]** Finding identity is (owner qualified name, input declared name, target formal qualified name), in one canonical spelling of qualified names. File and line are recorded for review but excluded from the key. Reason: lines move on unrelated edits; names change only when the binding itself changes.
- **[INFERRED]** A finding whose owner has no qualified name cannot be pinned and stays an ERROR, with a message saying why. Reason: without a stable key it cannot be matched to a pin.
- **[INFERRED]** A stale pin (no matching finding) fails the run. Reason: a stale entry would silently whitelist the same mismatch if it were reintroduced later, which defeats "new mismatches block".
- **[INFERRED]** The pin list is a project-owned, reviewable text file. `validate` never writes or extends it, and nothing in this item generates entries automatically. Reason: the epic says intentional positional use needs a documented disposition "rather than an automatic new baseline entry".
- **[INFERRED]** The pin list carries a header naming the model revision and date it was recorded against, and each entry is a finding identity that existed at that revision. Reason: D1 warns only on *legacy* cases, so a pin must say what it is legacy relative to. Limit: the check cannot see version history, so a pin added by hand later for a new mismatch is caught only by review of the pin file. That limit goes to the owner under R4-1 (Open Questions).
- **[INFERRED]** The pin list can be supplied from outside the model tree (for example, by an explicit CLI option). Reason: the fusion-tea baseline must be applied to a read-only pinned tree, and fusion-tea edits are reserved (R4-3).
- **[INFERRED]** A pin only downgrades a matching mismatch from ERROR to WARNING. It never hides a finding, never applies to `L2_CHECK_UNVERIFIABLE`, and carries no "intentional" meaning. Anything that does more is gate R4-1.

**Inspection failures**

- **[INHERITED: epic Item 4 scope 2; principle 5]** Unverifiable inspections are reported separately using the existing L2 failure pattern: `L2_CHECK_UNVERIFIABLE` at ERROR (`level2_structure.py:355-372`). Unrelated owners continue to be checked.
- **[INFERRED]** A pinned legacy WARNING does not fail L2, while every other L2 code keeps its current effect on pass/fail. Reason: today L2 fails on any issue at all, warnings included (`level2_structure.py:450`, `success=len(all_issues) == 0`), which contradicts the `Severity.WARNING` contract ("validation passes with warnings", `types.py:30-38`) and would turn every D1 warning into a block. Changing that rule for other codes is a separate behavior change.

**Fixtures and evidence**

- **[INHERITED: epic Item 4 scope 3]** The audit probes become retained minimal fixtures, and the cross-route subtraction counterexample (native -7, generated/TEAx 7) and the SysIDE 0.8.4 observations listed in scope 3 are retained as durable fixtures. `/tmp/consumer-audit-byname/` artifacts are not acceptance evidence.
- **[INHERITED: epic "Evidence and regression revisions"]** Consumer trees are read through `git archive` of pinned revisions into scratch directories. Consumer checkouts are never modified and whole consumer models are not mirrored into this repo.
- **[INHERITED: align record]** If the 125 fusion-tea identities or the dc3 zero-finding results do not reproduce, surface the difference to the owner rather than tune the detector.
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
- Executing every shipped SysML example (Item 5's fence harness). Item 4 checks only the examples it adds or changes.
- Execution-target settings and L6 severity routing (Item 3).

## Open Questions / Deferred to design

**Owner gates, recorded open (align record)**

- **R4-1:** any narrow suppression or "intentional positional use" disposition beyond D1's legacy pin. Until it is decided, a new deliberate positional use has to be written explicitly (`in name redefines target`), which valid SysML always allows, so no author is blocked. **Question for the owner within R4-1** (product-lens spec-F1): the pin list cannot itself prove an entry is legacy, so someone could hand-add a pin for a new mismatch and turn it into a warning. Is review of the pin file, plus its recorded-against header, enough? Or should the toolkit refuse pins it cannot tie to the recorded revision, for example by recording a digest of the pinned set that the check verifies? I'd accept review for now: the pin file is small, rarely changes and is visible in diffs, and a digest only moves the trust to whoever regenerates it.
- **R4-2:** any change to generator binding behavior.
- **R4-3:** any fusion-tea edit. **Consequence to know:** once fusion-tea moves its agentic-mbse pin to a release with this check, its `validate` fails L2 with 125 ERRORs, and without `--complete` it stops before L3–L6, unless the same fusion-tea change adds the pin list (or migrates the bindings). Both are fusion-tea edits under this gate.

**Surfaced conflict, not resolved here**

- sysml-codegen's backlog entry for POSITIONAL-FORMAL-REDEFINITION (as corrected by `bd352744`) says "Current elaboration follows parser redefinition identity". The prototype shows codegen `b5663c07` wiring the reversed calc usage by declared name (`04-eval.log`: `a` wired to `big`, result 7), while the parser's redefinition is positional (-7). These cannot both describe the same case. The draft upstream finding records both; the codegen owner decides which is right. The check does not depend on the answer.

**Deferred to design**

- Pin-list location, file format and how `validate` finds it in a target project, with an explicit override. It must work before Item 3's `[tool.agentic-mbse]` settings exist; whether it later moves under them is Item 3's call.
- Whether `init` mentions the pin list. If it ships a starter, it is a user-owned document and stays absent by default (no pins means every mismatch blocks).
- Canonical qualified-name spelling for keys (quoted names such as `'MFE Power Plant'`).
- The exact result for the explicit-plus-implied multiple-target case (the fixture is required; its expectation is a design decision informed by `sysml-expert`/`kerml-expert` if needed).
- Message text, metric names and whether the check lives in `level2_structure.py` or a sibling module.
- The epic's "dc3 interleave mutation" is read here as the two dc3 shapes above (WI-008 out-of-order inputs and the prototype's adjacent swap). If it meant a different probe, design should name it.
- Which `agents/` roles carry calc-usage input guidance.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_executable-subset-contract.md` (Item 4; D1; Prototype findings; Root causes)
- **Align record:** `.project/active/positional-binding-check/briefs/align.md`
- **Spec brief:** `.project/active/positional-binding-check/briefs/spec.md`
- **Required Reading:** none listed for Item 4 in the epic. Prototype evidence used: `.project/concepts/convince-me-exec-subset/evidence/04-README.md`, `04-detector.py`, `04-fixtures/`, `04-*.log`
- **Item 1 archive:** `.project/completed/20261018_exec-subset-profile/` (reproduction pattern: `scripts/subset_profile/run_trees.py`)
- **Upstream:** sysml-codegen `.project/backlog/BACKLOG.md` POSITIONAL-FORMAL-REDEFINITION; `tests/fixtures/modeled_default_fidelity/PROVENANCE.md`; fusion-tea `modeling_project/ARCHITECTURE.md` AD-008; dc3 `work/active/WI-008_generator-idiom/design.md:63`
- **Product lens:** `.project/active/positional-binding-check/product-lens.md`
- **Design:** `.project/active/positional-binding-check/design.md` (to be created)

---

**Next Steps:** `/_my_spec_review`, then `/_my_design`.
