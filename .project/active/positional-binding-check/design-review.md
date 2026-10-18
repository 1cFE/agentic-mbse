# Design Review: Positional-binding hazard and check (EXEC-SUBSET-CONTRACT Item 4)

**Design:** `.project/active/positional-binding-check/design.md`
**Spec:** `.project/active/positional-binding-check/spec.md` (with `spec-review.md` Resolutions)
**Review File:** `.project/active/positional-binding-check/design-review.md`
**Date:** 2026-10-18

**What I checked and how.** I read the design, the spec, the spec review and its Resolutions, the align record, the epic's Item 4 and owner decisions, and the product-lens ledger. I checked the design's code citations against the source: `level2_structure.py` (the unverifiable pattern and `success=len(all_issues) == 0`), `validation/common.py` (`discover_sysml_files`, `QualityCheckResult`, `print_result`), `runner.py`, `level1_syntax.py`, `cli/__init__.py` (`find_project_root`, `cmd_validate`), `subset_extraction.py`, `occurrence_extraction.py`, `constraint_extraction.py` (`_actuals`, `_redefinitions`, `_is_standard_library_element`), `syside_adapter.py`, the prototype `04-detector.py`, Item 1's `scripts/subset_profile/`, and sysml-codegen's `tests/conformance/test_self_binding_guidance_contract.py` and `tests/helpers/source_roots.py`. An independent product-lens subagent re-derived the point (appended to `product-lens.md`). **Not checked:** I ran no SysIDE code, no tests and no `validate`. The R1–R6 learning test is running separately and I did not duplicate it. Every finding below that depends on what SysIDE emits says so and asks for a learning-test question or fixture rather than asserting the behavior. I could not list fusion-tea's root at `f96ad312` (command needed approval), so I do not know which project-root markers its archive carries.

---

## The Point

An author who writes correctly named inputs on a calc or constraint usage in a different order than the definition gets a silent swap. SysML binds an unprefixed input by position (KerML 8.3.3.3.4, `checkFeatureParameterRedefinition`), so the model is valid and nothing warns. Native SysIDE 0.8.4 and generated/TEAx execution disagree on the result (-7 vs 7 on the reversed subtraction). fusion-tea `f96ad312` has 125 such mismatches whose value effect is unknown, and the knowledge sat in sysml-codegen since July without reaching authors.

Item 4 adds one L2 check, fixtures, a hazard register entry and guidance. Under D1 `[AGENT] (ratified by owner, 2026-10-15)`: new mismatches block, explicitly pinned legacy mismatches warn, a pin certifies neither native values nor route agreement, and an inspection failure never reads as clean. That a pinned warning does not by itself fail L2 is `[AGENT]`, decided by the orchestrator as execution of D1 (spec review L2-2). The item must not change how either route binds (R4-2), edit fusion-tea (R4-3), or touch sysml-codegen or Item 2 (owner boundary).

## Fundamental Assessment

**Sound, with four must-fix gaps.** This is the right piece of work, and the overall shape is right: read SysIDE once into plain data, then decide policy in pure code. The product lens found no owner or `[HARD]` contradiction and neither structural smell fired (gate OPEN; its six findings are dispositioned below). Keeping the fact as a separate family rather than a new `SubsetFacts` kind is the right call while Item 2 builds against `SubsetFacts`.

The weak points are at the edges, not the core:
- One evidence gap can let a swap pass silently (an input whose owner's type did not resolve looks like a clean new parameter).
- Pin-list discovery and path anchoring have failure modes that give different verdicts for the same model, or make the explicit override unusable for the job the spec gives it.
- One unexamined shape (a requirement or case definition with ordinary inputs and no declared subject) could put an ERROR on correct models that no pin should be needed to clear.

None of these changes the approach. Detailed review follows.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Most criteria trace cleanly. The fixture table (Appendix A), pure decision tests, policy test, unverifiable tests, reproduction runs, cross-route split, register and shipped-text test each map to a named spec criterion. D17 (no commit on agentic-mbse's own citations) is a stated, reasoned deviation, and I accept it.

Gaps:
- **The spec's "a fact that cannot be resolved" is only partly covered.** The spec makes `L2_CHECK_UNVERIFIABLE` come from "a read that raises, or a fact that cannot be resolved". The design's `TARGET_UNRESOLVED` covers a redefinition whose target cannot be read. It does not cover an owner whose type or supertype did not resolve, which yields no implied redefinition at all. See M1.
- **"Every new or changed SysML example parses and has its stated positional findings"** has no mechanism. Item 5's fence harness does not exist yet, so the test needs an explicit list of which examples it checks (file plus a marker or heading). Otherwise "changed" is decided by memory. See S9.
- **Repository checks** (pytest, mypy, ruff; which tests needed the licence; which slow tests ran or skipped) are a spec criterion but are absent from Validation Approach. Minor (N1).
- **Multiple types and `out`-before-`in`**: the spec asks design to confirm against SysIDE. The design defers both to the learning test (R3, R4) as "recommended, not blocking". That is a reasonable call because D7 and the step order handle either answer, but it means the fixture expectations are not yet confirmed.
- **Provenance.** The Point folds the L2 pass rule into D1's ratified grade. The spec grades it `[AGENT]` (`spec.md:91`). See S1.

### 2. Pattern Consistency
**Assessment:** Concerns

Good reuse: `ElementRef`, `SafeLocation`, `safe_location`, the `_Collector`-style totality rule, the seam injection the prototype used, `L2_CHECK_UNVERIFIABLE` with `reason_code`, Item 1's `probe.py` helpers, and `git archive` exports.

Concerns:
- **D11 misquotes the marker set.** It says discovery stops at "a directory with `.git`, `pyproject.toml`, `work/BACKLOG.md` or the install manifest, the markers `find_project_root` uses". `find_project_root` (`cli/__init__.py:122-136`) checks `work/BACKLOG.md`, the install manifest and a `.claude/` directory. It does not check `.git` or `pyproject.toml`. Which set is used decides which pin file applies to a run. Folded into M2.
- **Standard-library filtering.** `constraint_extraction._is_standard_library_element` (`:939-948`) already does the document-tier test. The design says the extractor "skips standard-library owners by document tier" without naming it. Reuse it (or `SysideAdapter.document_tier` directly) rather than writing a third copy. Minor (N2).
- **Parameter listing.** Item 1's constraint facts list parameters with `owned_parameters` (`constraint_extraction.py:786`). The design lists `owned_features` filtered by direction. Either may be right, but the choice should be stated, since the two may differ on subject and return parameters. Minor (N3); a cheap learning-test line.

### 3. Abstraction Quality
**Assessment:** Pass, with one naming fault

The split is clean: a pure fact module, a SysIDE extractor, a pin parser, a pure `decide`, and a `render` step, with L2 calling one function. Each piece earns its place, mainly because `decide` becomes testable without SysIDE. `functools.partial` keeps `QUALITY_CHECKS` unchanged.

The naming fault matters for correctness: `RedefinedFormal.owning_definition` is not always a definition. See S4.

### 4. Duplication Avoidance
**Assessment:** Concerns

The new fact is not a re-derivation of anything Item 1 extracts as a *redefined-formal* fact; the design is right that `BindingSourceFact.formal` is the input itself.

But Item 1 already holds a neighbouring reading of the same question. `constraint_extraction._actuals` (`:774-787`) records, for each parameter of a constraint usage, `ActualFact.formal_targets` from `owned_redefinitions`. `_omitted_default_formals` then treats any formal no actual targets as omitted. That is Item 1's answer to "which formal does this actual bind?", for constraint usages. The design picks `heritage` because "whether `owned_redefinitions` includes implied relationships is unverified" (D3). So the two readings may disagree on exactly the positional shapes this item is about, and nothing will notice. See S5. This is a question to answer and record, not something to fix in Item 1's code here.

### 5. Data Structure Clarity
**Assessment:** Concerns

The types are explicit and frozen, sorting is stated, and failures are named causes rather than strings. Issues:
- **`owning_definition`** (S4).
- **D4 says "the fact records role and direction"**, but `InputRedefinitionFact` has no direction field. Either add it (`in` vs `inout`) or fix D4's text. Minor (N6).
- **`PinListAbsent` and `PinListInvalid`** have their fields only in a comment (`absent: searched-from/to; invalid: path, reason_code, detail`). The plan will need them spelled out; the "none found (searched <from> to <to>)" metric depends on them. Minor (N7).
- **Unpinnable owners.** D9 makes a finding on an owner with no qualified name an ERROR that can never be pinned. Anonymous `assert constraint : Le { ... }` and `require constraint { ... }` are common. A project with legacy mismatches on such owners cannot use D1's legacy warning at all and must migrate them. That may be acceptable, but the design should state the consequence, add an anonymous-assert fixture, and confirm what `str(qualified_name)` gives for an anonymous owner (it may not be `None`). See S8.

### 6. Route Safety
**Assessment:** Concerns

There are no HTTP routes. The analogue here is how `validate` finds the pin list and anchors its entries, and that is where the risks are.
- **Path-dependent verdicts.** D11 walks up from the validated path to the *first* directory holding `positional-pins.toml`. A pin file placed in `models/designs/x/` is found when validating `models/designs/x/` and not when validating `models/`. The same model then gets different severities depending on the path given. M2.
- **No boundary found.** An archive exported without project-root markers walks up to the filesystem root, and can pick up a stray `positional-pins.toml` in `/tmp` or `$HOME`. Item 1's run script exports into `tempfile` directories (`scripts/subset_profile/run_trees.py:435`), so this case is real for the reproduction. M2.
- **The override cannot serve its stated purpose.** Entry paths are relative to the pin file's own directory (D11). The spec's reason for the override is to apply the fusion-tea baseline to a read-only tree from outside it. With `--positional-pins tests/fixtures/positional_binding/baselines/fusion-tea-f96ad312.toml` against an exported tree, every entry's `file` resolves under `baselines/` and does not exist. A full run still works because all pins match. But any unmatched pin reads as "pinned file missing" rather than "not found in validated file", and a partial run cannot judge scope at all. The reproduction sidesteps this by copying the file into the scratch tree, which hides the defect instead of testing the override. M3.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

B1–B5 are genuine claims about SysIDE with stated failure consequences. The decisions name rejected alternatives. D16 (run the base revision's L2 rather than add a disable switch) is a good call.

Hidden bets the design rests on but does not state:
- **H1. A failed name resolution shows up somewhere.** No validation level fails on unresolved names today. L1 reads only `diagnostics.parser` (`level1_syntax.py:74`), and L2 ignores the diagnostics `load_sysml_model` returns (`level2_structure.py:427`). If a calc usage's type does not resolve (a typo, or a partial run whose definitions live outside the validated subdirectory), its inputs likely get no implied redefinition and classify as `new_parameter`. The swap then passes clean. That is the falsifier "an inspection failure yields a clean L2". Whether SysIDE leaves the typing absent, or records it with a null target, is a SysIDE question. M1.
- **H2. Library supertypes of requirement and case definitions add no position for ordinary inputs.** Every requirement definition specializes the library `RequirementCheck`, which owns `subject subj` (spec review L2-1). If a user's `requirement def R { in lo; in hi; }` declares no subject, the positional rule may make `lo` implicitly redefine `RequirementCheck::subj`. `lo` is an ordinary input, so the role exclusion does not apply, and the check would put an ERROR on a correct model. The same may hold for case and analysis definitions. R2 asks whether a declared subject counts toward positions, but not this shape. Neither consumer exercises requirements (spec review L1-3), so the baseline cannot reveal it. M4.
- **H3. An implied target's owner is a definition, and "several owning types" means "several types".** D7 groups implied targets by owning definition and treats more than one owner as the multiple-types case. A usage that redefines a parent usage (the spec's "usage redefined in a subpart" case) has the redefined usage as a direct supertype as well as its type. Its inputs may get implied targets owned by a *usage*, possibly alongside targets owned by the definition. Then a deliberate rename (`in local redefines a`) accounts only for one owner's target, and the other could be flagged. S4.
- **H4. Item 1's `owned_redefinitions` reading agrees with the `heritage` reading on explicit redefinitions.** See S5.
- **H5. sysml-codegen's conformance test reads this branch.** It finds agentic-mbse through `agentic_mbse.__file__` in codegen's environment (`tests/helpers/source_roots.py:15-22`). Running it "against this branch" is only evidence if that resolves to this checkout. S6.

The riskiest stated bet is B2 (the mixed spelling carries an implied redefinition). The design handles it well: R1(a) is a stop-and-surface gate before planning, with no name heuristic as fallback.

### 8. Reader Comprehension
**Assessment:** Pass

Core Concept states the model plainly before the mechanism: a fact, a small decision, a pin list that only changes severity, one change to the pass rule. The step order in Implementation Notes makes the outcome counts checkable. Appendix B is dense but is a procedure, and reads as one. The one comprehension fault is The Point folding the pass rule into D1's grade (S1), which misleads a later reader about how to challenge it.

---

## Issues by Severity

### Critical (must fix before planning)

- **M1. An owner whose type did not resolve passes clean** (Spec Compliance, Bets H1). Inputs of a calc or constraint usage whose typing or supertype did not resolve likely carry no implied redefinition, so they classify as `new_parameter` and a swap passes silently. No level reads semantic diagnostics today, and partial-scope runs (which the design supports) make this the normal case rather than a typo case. *Fix:* treat an owner whose typing, subclassification or redefined-feature relationship has no resolvable target as a failure (`TARGET_UNRESOLVED`, or a new `SUPERTYPE_UNRESOLVED` cause) and report it as unverifiable. Add a learning-test line for what SysIDE 0.8.4 emits for `calc c : Missing { in b = 3; }`, and a fixture for it. State in the partial-scope test that the validated part must be self-contained, or that a non-self-contained part reports unverifiable.
- **M2. Pin discovery gives path-dependent verdicts and can escape the project** (Route Safety, Pattern Consistency, lens F5). The first-ancestor walk lets a nested pin file apply to some validated paths and not others, and a tree without markers walks to `/`. The marker set is misquoted. *Fix:* recognise one location only, the project root, found from the validated path with one stated marker set. Either match `find_project_root`'s set exactly or state the new set and why. If no project root is found, discover nothing and say so in the metric ("no project root above <path>; pass --positional-pins"). Make it an error if a `positional-pins.toml` exists below the root, or state why it is ignored. In the reproduction, assert the discovered path (Run 2) and the "none found" result (Run 1, dc3) rather than assume them.
- **M3. The explicit override misanchors entry paths for the job the spec gives it** (Route Safety). Entry paths are relative to the pin file, so an outside pin file applied to an exported tree cannot resolve any `file`. *Fix:* anchor entry paths to the project root of the validated path (the same root M2 finds) for both discovered and explicit files, or add an explicit anchor. If no root is found under the override, report the pin list as unanchorable rather than judging scope. Make Run 2 use the override against the unmodified scratch tree, plus a separate discovery run, so both paths are tested.
- **M4. Ordinary inputs of requirement and case definitions without a subject may land on the library `subj`** (Bets H2). This could put an ERROR on correct, ordinary requirement definitions. *Fix:* add `requirement def R { in lo; in hi; }` (no subject) and the case and analysis equivalents to the R2 learning test, before planning. If SysIDE gives `lo` an implied redefinition of `RequirementCheck::subj` (or a case library parameter), surface it to the owner as a premise surprise, as R1(a) does. The candidate rule is that an implied target that is itself a subject, actor or stakeholder parameter is not a finding, with fixtures. Do not choose that rule silently.

### Major (should fix)

- **S1. Grade the L2 pass rule as `[AGENT]` in The Point and beside I1** (lens F1; capture-fidelity §1). It was decided as execution of D1 (spec review L2-2), not ratified with D1.
- **S2. The shipped text must say pins are for legacy only** (lens F2). The register and the "how to write a pin list" docs (D14) should say: a pin records a mismatch that existed at `recorded_against`; a new mismatch is fixed with `in :>> name` or `in name redefines target`, not pinned; and a pin added for a new mismatch is the R4-1-reserved disposition. Make the ERROR message print the five fields (owner, input, target, file, line) so an author can write an entry without guessing, and say in the docs that entries are copied for legacy findings only.
- **S3. State the fact family's status** (lens F3). Say it is L2-internal for now: no version marker, not part of `SubsetFacts`, not a surface Item 2 or codegen should consume, and promotion needs its own item. This keeps Item 2's agent from adopting an unversioned surface by accident, without touching Item 2.
- **S4. Rename `owning_definition` to `owning_type` and re-check D7 for redefining usages** (Data Structures, Bets H3). D7 should be stated over the target's owning type. Add a fixture for a deliberate rename inside a subpart-redefined usage (`calc :>> c { in local redefines a = 10; in b = 3; }`), with the expected result. Add to the learning test whether such inputs carry implied targets owned by both the redefined usage and its definition.
- **S5. Record how the new fact relates to Item 1's `ActualFact.formal_targets`** (Duplication, Bets H4). Add a learning-test line for whether `owned_redefinitions` includes implied redefinitions. Then state the relationship in the design. One option is "for constraint-usage inputs, `formal_targets` equals the explicit subset of this fact", with a consistency test on the constraint fixtures. If `_omitted_default_formals` reports the formals of a positional constraint usage as omitted, that is a finding about Item 1's facts. Surface it to the owner and Item 2's agent; do not edit Item 1 or Item 2 here.
- **S6. I8 is incomplete against codegen's conformance test, and the evidence must bind to this checkout** (Bets H5). The test enforces more than the four rules I8 lists:
  - The three pointer surfaces (`skills/sysml-conventions/SKILL.md`, `project_templates/MODELING_GUIDE.md.template` and `project_templates/MODELING_PROCESS.md.template`) must keep the text "plant-idiom.md" and the phrase "Binding a modelled value into a calculation". Two of those files are ones this item edits.
  - At least seven `@pinned` blocks must remain, each an ordered subsequence of its codegen fixture, and exactly one must pin the `SI_SELF_BINDING` refusal.
  - The three "Won't resolve" negatives must remain (`common-mistakes.md`, `cross-file-binding.md`, `syntax-reference.md`).
  - The qualified-binding regex (`\bin\s+[\w']+\s*=\s*[^;=\n]*::`) matches **prose lines too**. A register or plant-idiom line such as "`in b = 3` binds to `Sub::a`" counts as an owner-qualified site. The per-file counts are exact, and a new file with any match adds a key, so a line like that in `semantic-hazards.md` fails the test.
  - The `.claude` tree must contain no `in x =` line. It is scanned on disk (`rglob`), so installed copies count.

  *Fix:* list all of these in I8. For the evidence, record codegen's resolved `agentic_mbse.__file__` and this branch's HEAD alongside the test output.
- **S7. Choose the mutation site independently of the check** (reproduction independence). Appendix B selects "an owner whose inputs are all `implicit_matching`", which is the check's own classification. Choose it from source text instead (two adjacent unprefixed `in` lines whose names match the definition's order, found by a stated rule), or name a fixed, cited site. Record it in the evidence. Also say where the pin file lives for the mutation and stale copies (copied, or passed by override after M3).
- **S8. Unpinnable anonymous owners** (Data Structures). State the D1 consequence (legacy mismatches on anonymous owners always block), add an anonymous `assert constraint` fixture, and confirm what `str(qualified_name)` gives for one.
- **S9. Name the mechanism for "every new or changed example"** (Spec Compliance). For example: a marker comment on each fence this item adds or changes, and a test that collects the marked fences and asserts their stated findings.
- **S10. D16 must prove which code ran** (reproduction). The editable install in the venv can shadow the archived `ccd57d83` `src/`. Run 0 should record and assert `agentic_mbse.__file__` resolves inside the archive.

### Minor

- **N1.** Add the repository-checks criterion (pytest, mypy, ruff; licence-dependent tests; slow tests run or skipped) to Validation Approach.
- **N2.** Reuse `constraint_extraction._is_standard_library_element` or `SysideAdapter.document_tier` for the library filter.
- **N3.** State why inputs are listed from `owned_features` rather than `owned_parameters`, which Item 1's constraint facts use.
- **N4.** Record in Item 1's module, or in a test, that L2 depends on `_element_ref` and `_IdentityError` (lens F4). If that would mean editing Item 1's module, record it in this item's test instead.
- **N5.** Name in Risks that the owner sweep silently returning nothing is guarded only by the retained learning test (lens F6).
- **N6.** D4 says the fact records direction, but the data model has no direction field.
- **N7.** Spell out the fields of `PinListAbsent` and `PinListInvalid`.
- **N8.** Add an `OWNERS_UNLISTED` test (population failure) alongside the per-owner and per-input injections.
- **N9.** D12: on a partial run, an owner moved out of its pinned file into an unvalidated file reads as stale. The recorded `file` is therefore load-bearing for scope, despite "not part of the key". Say so in the pin-list docs.

---

## Recommendations

1. Before planning, add M1's unresolved-type shape, M4's subject-less requirement and case shapes, S4's redefining-usage shapes and S5's `owned_redefinitions` question to the learning test. These run alongside R1 and R2, and the same stop-and-surface rule applies.
2. Collapse pin discovery to the project root, with one stated marker set, and anchor every entry path to that root (M2, M3). This is simpler than the current walk and removes both failure modes.
3. Make the unresolved-supertype case an unverifiable failure (M1).
4. Rewrite I8 from codegen's actual test (S6), and fix The Point's grading (S1) and the legacy-only text (S2).
5. Tighten the reproduction's independence and provenance (S7, S10).

---

## Resolutions

(None yet. The orchestrator or owner records resolutions here; the design agent reads them to incorporate.)

---

**Overall:** Revise
**Next Steps:** Record resolutions here, then return to the design agent (or re-run `/_my_design`) and point it at this review. M1, M4 and the learning-test additions in Recommendation 1 should be resolved before `/_my_plan`. The reviewer does not edit the design.
