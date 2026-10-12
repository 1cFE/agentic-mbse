# Design Review: goal-layer-port (`WRAP-SPLIT` Item 2)

**Design:** `.project/active/goal-layer-port/design.md` (at `892ba8d`)
**Spec:** `.project/active/goal-layer-port/spec.md`
**Review File:** `.project/active/goal-layer-port/design-review.md`
**Brief:** `.project/active/goal-layer-port/briefs/design_review.md`
**Date:** 2026-10-11

Each finding is graded **must-fix** or **advisory**. `design.md:N` cites the design. fusion-tea paths are at `2b1e9f9d5`, read from `.orchestrate-logs/fusion-tea-snapshot/`.

---

## The Point

This item owes two outcomes and one constraint (design.md:23-29):

- **A working goal layer for every target.** A fresh target can ground a goal and run rounds from installed files alone, with nothing pointing at fusion-tea. Authority: [OWNER] "Goals are general to the systems-engineering and concept-development process" (fusion-tea concept `:198`).
- **The design-choice rule at the right level.** [OWNER-VERBATIM] 2026-10-11: "it is important that you find the right level for this rule -- we have specific patterns which agentic-mbse is supposed to enforce, this should fit into that". The principle it generalizes, [OWNER-VERBATIM] 2026-09-20: "As soon as you start introducing 'sizing', then you are basically pre-defining which design parameters are 'free' and which are 'derived'. this is explicitly what we wanted to avoid." The owner will judge the item by whether the rule reads as one of agentic-mbse's own patterns.
- **fusion-tea loses nothing.** [INHERITED: epic, OWNER] Every consumer-specific line has a fusion-tea home before the agentic-mbse change merges, and MR-7's enforcement survives re-init without a kept edit to a tool-owned file.

## Fundamental Assessment

**Sound. Verdict Revise, not Rework.** Four must-fix edits, all to Appendix A and Appendix D3.

- **Right piece of work: yes.** A fresh product lens re-derived the same point from the repo's own sources. It found no owner-grade contradiction, and neither structural smell fired (`product-lens.md`, design block, Gate DISPOSED).
- **Right approach: yes.** The rule enters where agentic-mbse already puts construct rules: a "Process Selection" row routes review, a "Technical Patterns" row gives the one-line rule and names a `docs/patterns/` reference, and the reference is reached through `get_docs_dir()`. That is how `adr002-calculations.md` and `plant-idiom.md` ship (`MODELING_PROCESS.md.template:64-74`). Naming Equality intent as the sibling is the right link. I found no simpler shape that meets SC5.
- **The port is a port.** Appendix B's line changes match the snapshot, the runbook's method lists are untouched, and the installer facts hold.
- **Where it falls short is the pattern document itself.** As drafted, A1 is requirements text in a patterns folder. It is the only pattern doc with no SysML and no Verification section (M1), and it restates the review trigger that "Process Selection" owns (M2). Those are the first things the owner would notice against the bar above.

---

## Brief checks

### 1. Does the rule read as one of agentic-mbse's own patterns?

- **Placement: right.** See the Fundamental Assessment.
- **Routing or second statement?** The trigger condition appears three times in the same words: A1 § Review (design.md:340), the "Process Selection" row (:379) and the runbook trigger row (:444).
  - The "Process Selection" row is routing. It is agentic-mbse's one place that says which changes need independent review.
  - The runbook row is routing too. The runbook mirrors "Process Selection" by its own convention (fusion `GOAL_RUNBOOK.md:70-76`), and goal coordinators check that table.
  - A1 § Review is a second statement. No other pattern doc restates a "Process Selection" row; none even cites `MODELING_PROCESS.md` (grep of `docs/patterns/`). → **M2**.
- **Over-spread.**
  - The new Architecture bullet (design.md:383) lands directly under template `:59`, which already says to distinguish installed capacity from operating demand. → A1.
  - A5's two stage pointers re-list the read scope, and they already drop "operating-point closure". → A2.
- **Missing.**
  - A SysML rendering, and a Verification section. → **M1**.
  - `adr002-calculations.md` in Related Patterns. ADR-002 makes the violating form legal placement (`adr002-calculations.md:52-66`). → **M1**.

### 2. Wording against MR-7

Done in its own section below (§ SC6 fresh check). Result: every general obligation is present. Four rules lost force or changed scope (**M3**). One fusion term reads as general (A9). A6 plus A7 keep everything fusion-tea needs. The grade stanza passes.

### 3. Port fidelity

- **Lines spot-checked** against Appendix B and A8:
  - run-goal `:20,:49-63,:73`;
  - runbook `:7, :13, :31, :41, :70-76, :84, :94, :100, :106, :139, :205, :232, :260-276, :286-305`;
  - `goal.md:29` and narrate-goal `:77`.
- **No method change.** Each change is a pointer, a path or a status note. The lists in Invariant 2 are untouched.
- **The :94 re-cite is accurate.** ADR-0003's 2026-08-27 amendment records the five-class promotion (`0003-lean-first-persistence.md:60`).
- **D11's goal-close section matches practice.** `goals/burn-control/trail.md:143-156` writes the ruling, then the disposition.
- **Two hooks shift behaviour slightly.**
  - The runbook `:84` hook no longer says to carry the rule into the goal's invariants (A4).
  - The `goal.md` bullet drops MR-7's condition, so it now applies to every goal, not only model-changing ones (A5).
- **Two fusion-flavoured lines are not in Appendix B:** `:262` "the Item 4 proof run" and `:272` "an ADR if it is a decision" (A11).

### 4. fusion-tea sequencing and the installer

- **fusion-tea stays whole at every merge point.**
  - fusion `main` keeps pin `adbef75` and its local goal files until `goal-layer-mr7` merges.
  - A re-init on `main` at the new pin would also keep them. They are unmanifested and differ, so a non-interactive init preserves them (`cli/__init__.py:365-369`, `installation.py:121-143`).
- **F2's removals are necessary.** fusion's `.agents/skills/run-goal` is a link the installer does not own. Without removal, `copy_tree` asks and, non-interactively, keeps it (`installation.py:187-189`).
- **The installer facts the design relies on all hold:**
  - tool-owned templates go through `Installer.write` (`cli/__init__.py:538-541`);
  - bundles are copied to `.agents/skills/` for every assistant, and Claude gets a folder link (`installation.py:429-440`);
  - `--force` replaces user-owned documents (`cli/__init__.py:517`);
  - the dev-mode ignore block is skipped when its marker exists (`cli/__init__.py:290-293`).
- **F1's equal bytes let F2 re-init without a prompt.** fusion's manifest holds baselines for `MODELING_PROCESS.md` and `MODELING_GUIDE.md` (snapshot `install.json:42-43`). Re-init writes the process file with no prompt and updates the guide silently. D2's expected-output list should name the guide (A10).
- **The D9 contract test is sound.**
  - Under `--dev` the installer links the destination to the `.template` source (`installation.py:171-173`). `Path(__file__).absolute().parents[2]` still lands on the target.
  - It follows the target's existing `tests/conftest.py`, which does not resolve its own path either (`project_templates/conftest.py.template`).
  - The design runs pytest against the link before building on it (design.md:281).
  - Unlike fusion's test, it needs no `yaml`.

### 5. Feasibility and checkability

- **The phasing is executable.** P1–P3 and P6 fit implement sessions. P4–P5 are correctly marked orchestrator-run.
- **SC4 is not runnable as designed** (**M4**).
- **SC5(a) cannot be graded** while the trigger condition has three equal homes (**M2**).
- **Budget.** The design already accepts 18.5h against a 16h ceiling. M1 adds about 1h. Reusing the D16 fixture as the pattern's example recovers part of that.

---

## SC6 fresh check: the shipped wording against MR-7

**Scope.** A1 (design.md:299-373), the A2 rows, A6 and A7, read against fusion `REQUIREMENTS.md:89-107` and fusion `MODELING_PROCESS.md:17,34`.

**Condition.** This check covers A1 as written plus the M3 fixes applied verbatim. Any other change to A1 during implement reopens it: a fresh reviewer diff-checks the change before F1 copies template bytes.

| Source sentence | Shipped location | Verdict |
|---|---|---|
| `:91` distinguish physical relationships and limits from selection policies (MUST) | Core Principle | Kept |
| `:91` MUST NOT silently remove a design choice | Core Principle | Kept verbatim |
| `:91` contract MUST make specified/solved quantities explicit, with authority | Rule 3 | **Softened**: "says" (M3) |
| `:91` calculation direction, reference design or depth target is not authority | Rule 3 | Kept; "depth" generalized to "quality target" |
| `:95` keep demand, installed and suggested design separate; report insufficiency | Rule 1 | Kept |
| `:95` authorized sizing study; policy separately identifiable; selected design must be evaluable without rerun | Rule 2 | **Softened**: "can be evaluated" (M3) |
| `:96` document direction; convenience is no excuse; no acausal solver required | Rules 2 and 4 | Kept |
| `:97` balances, identities, operating points not *automatically* violations; explain chosen quantities | Rule 5 | "automatically" kept; "explain" became "state", which reads as description (M3) |
| `:97` required flow and required area examples | Examples, rows 4–5 | Kept |
| `:98` report empirical validity separately from physical adequacy | Rule 6 | Qualifiers dropped (A12) |
| `:98` conductor example | A6 "Conductor models" | fusion-only, correctly routed; restates the general clause (A8) |
| `:98` unsupported evaluation never a pass | Rule 6 | Kept |
| `:99` supplied equipment is the basis of inventory and cost | Rule 7 | Kept |
| `:99` demand-scaled cost **proxy** must disclose its assumption; must not be presented as evaluated | Rule 7 | **Widened** to every demand-scaled cost, and softened (M3) |
| `:101` evidence: quantities, units, five roles, binding, authority, proportionality, public-interface call-out, defaults/modes/multipliers | What to Record | Kept |
| `:103` goal grounding and tasks carry the rule as an invariant | runbook `:84`, `goal.md:29`, A6 "Invariant" | Procedure kept; `:84` should name the pattern (A4) |
| `:103` review inspects actual equations, downstream attributes and costs | Review | Kept |
| `:103` changed assignment or selection policy triggers independent review | "Process Selection" row | Kept at L3-3 scope; also restated in A1 § Review (M2) |
| `:103` existing code and passing depth grades do not waive | The Rule, closing paragraph; A6 "Depth work" | Kept, split correctly |
| `:105` acceptance, in full | Acceptance | Kept |
| `:107` examples; swapping one hidden choice for another | Examples; Common Mistakes | Kept |
| process `:17` read scope, direct edits and inherited patterns, stage compression | Technical Patterns row; The Rule, closing paragraph | Kept. "Before selecting a process" becomes "at the point of use", per L3-3; the crosswalk should record that |
| process `:34` per-stage contract, names are not evidence, handoff | What to Record; Review; Common Mistakes | Kept; "generated and native execution" is consumer vocabulary (A9) |
| process `:34` depth-rubric policy | A6 "Depth work" | fusion-only, correctly routed |

**Results.**

- **Completeness.** Every general obligation is present. Nothing is lost.
- **Force and scope.** Four rules slipped (M3). Rule 7's is a real scope change: an energy cost that scales with use would be told to name its "demand-matched equipment".
- **Fusion terms presented as general.** Only "native execution" (A9).
- **fusion-tea keeps what it needs.** A6 plus A7 keep the authority line, the invariant, the conductor and depth applications, and the research, integration, study, decision-record and launcher pointers. One restatement to trim (A8).
- **Grade stanza** (design.md:372). It passes the brief's test: only the principle is presented as owner-originated. The obligations are `[AGENT]` ratified, and the generalization is `[AGENT]` at the owner's direction. Two fixes remain: the pointer target and the date on the tag (A3).

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns
- Every SC has a design element and a named check (design.md:253-266).
- SC4 is not runnable as designed (M4). SC5(a) cannot be graded (M2). SC6 finds force slips (M3).
- Capture fidelity is clean. The orchestrator's `[AGENT]` calls stay labelled (B4, D2). D14 overrules the spec's `[AGENT]` `AGENTS.md` lean with a verified reason: fusion `AGENTS.md:5` sends Codex to `CLAUDE.md`.

### 2. Pattern Consistency
**Assessment:** Concerns. M1, M2, A1.

### 3. Abstraction Quality
**Assessment:** Pass
- Each new piece earns its place: one pattern doc, one decision record, five tool-owned templates and one test.
- D7's resolver home for the decision record is right. The runbook cites it rarely, and a bundle file would carry runtime paths that `test_shipped_text.py:75-78` rejects.

### 4. Duplication Avoidance
**Assessment:** Concerns. M2, A1, A2, A8.

### 5. Data Structure Clarity
**Assessment:** Pass. The template list, ignore paths and subdirectories are explicit (design.md:185-188), and they match `cli/__init__.py:27-62,486-503`.

### 6. Route Safety
**Assessment:** Concerns. Read here as reference routes and install routes.
- No install collision. The shipped test's basename differs from fusion's.
- The runbook's design-choice citation names the guide, not the resolver. Implementation Notes (design.md:220) say it "names the resolver once" (A4).
- The rehearsal and F2 chain walks do not say which environment runs the resolver hop (A10).

### 7. Bets & Decisions Integrity
**Assessment:** Concerns
- The stated bets are real claims, each with its failure mode.
- **Hidden bet: the dry-run agent sees only installed files.** It runs with this worktree's `.venv`, so `get_docs_dir()` returns the worktree root (`cli/__init__.py:74-76`). That root also holds the fusion-tea snapshot and this item's spec and design (M4).
- **Hidden bet: B1's check will fire.** The dry run is meant to show a fresh agent reading `design-choices.md` at grounding. The hook that sends it there fires only "for a model-changing goal" (design.md:441). The sample goal (design.md:536) is an evaluation question (M4).
- **Hidden bet: some target has no research procedure.** D10's fallback assumes it. But `/research` ships to every target, so "where none is installed" never fires. In fusion-tea, `/research-acquire` is then reachable only through `CLAUDE.md` (A6).
- D7 leaves out the epic's amendment clause (A7; lens smell 1).

### 8. Reader Comprehension
**Assessment:** Pass. The Point and Core Concept give the model in one read. The length is mostly exact texts the plan needs.

---

## Issues by Severity

### Critical

None.

### Major (must-fix)

**M1. The pattern doc lacks the pattern set's shape** (design.md:299-373; Pattern Consistency).

*Problem:*

- Every other doc in `docs/patterns/` has 8–23 SysML blocks. A1 has none.
- Nearly all end with "Related Patterns" then "Verification" (`adr002-calculations.md:250,259`). A1 ends with "Authority", a heading no pattern doc uses.
- `docs/patterns/README.md:32` asks for syntax rules, examples, common mistakes and verification notes.
- So a modeler sent here before editing a binding (`implement-model:25`) gets pseudo-equations, not the construct.
- It also misses the one interaction a modeler will hit. ADR-002 allows an inline formula over sibling attributes, or an EXPOSE of a calculation output (`adr002-calculations.md:52-66`). So `attribute installed_flow = sizing.required_flow;` is legal placement and still a design-choice violation.

*Fix:*

- **Validated Pattern.** Add a short wrong/right SysML pair and run it through `agentic-mbse validate`.
  - Wrong: installed capacity bound to required flow, by inline formula or EXPOSE, or hidden behind a `default :=` margin.
  - Right: installed capacity supplied as a cited literal in the design, required flow from a library calc, and a one-sided `assert constraint` reporting fit. That is the feasibility-gate move Equality intent already names (`constraints.md:55`).
  - Use the D16 sump/pump fixture, so the example and the dry-run seed are one validated model.
- **Verification section.** Say that `validate` cannot see this rule (spec Non-Goals). Say how to check by hand: read each installed-capacity, equipment or inventory attribute's value expression for a demand quantity, then run the Acceptance tests.
- **Related Patterns.** Add `adr002-calculations.md` (placement and role are separate checks) and `semantic-operators.md` (a `default :=` can hide adequacy).
- **Authority.** Close the doc with the stanza as a plain paragraph, the way Equality intent does (`constraints.md:64-69`), instead of under a new heading.

**M2. The review trigger is stated three times** (design.md:340, :379, :444; Pattern Consistency, Duplication).

*Problem:*

- "Process Selection" is where agentic-mbse says which changes need review. The runbook row is that table's goal-layer mirror.
- A1 § Review is a third copy. The three will drift.
- Invariant 1 (design.md:131) and SC5(a) cannot be graded while it is unclear whether the trigger is an obligation or routing.

*Fix:*

- A1 § Review becomes: "'Process Selection' in `modeling_project/MODELING_PROCESS.md` routes design-choice changes to focused independent design review. That review inspects the actual equations and bindings…" Keep the rest of the section.
- Invariant 1 names "Process Selection" as the trigger's one home and the runbook row as its goal-layer mirror.

**M3. Four rules in A1 lose force or change scope** (design.md:320-325; SC6 check).

- **Rule 7 widens a proxy rule to every cost.** MR-7's "demand-scaled cost proxy" (`REQUIREMENTS.md:99`) became "A cost that scales with demand". Fix: "A cost proxy that scales equipment cost with demand, instead of costing the installed equipment, must say which demand-matched equipment it assumes and that installed capacity was not evaluated. It must not be presented as a fully evaluated chosen design."
- **Rules 2, 3 and 5 read as descriptions.** They use present tense where MR-7 says "must" (`:91`, `:95`, `:97`): "can be evaluated", "says", "state". A description can be read as already true, not as a duty.
  - Fix: "must be evaluable without rerunning the policy"; "Each analysis's contract must say…"; "…must state the independent quantities they selected and their assumptions".
  - Normative words are house style: `adr002-calculations.md:27` uses SHALL.

**M4. The SC4 dry run is not isolated, and may not test B1** (design.md:529-540; Feasibility).

- **Isolation.** With this worktree's `.venv`, the resolver returns the worktree root (`cli/__init__.py:74-76`). That root holds fusion's original runbook and skills in `.orchestrate-logs/fusion-tea-snapshot/`, and this item's design. "Nothing from fusion-tea is on disk" cannot be shown.
  - Fix: `uv build`, then install the wheel into a scratch venv outside the repo. Run `init` and the agent from that venv. `get_docs_dir()` then returns the packaged `agentic_mbse_data/docs`, which also tests the packaged data path that no other SC touches.
  - Prefer an isolated `CLAUDE_CONFIG_DIR` to "project-only settings". The owner's user-level rules and skills would otherwise shape a supposedly fresh agent.
- **Operator answers.** The brief pre-states only the slug, `grounded` and the stop point. Grounding also needs owner-held fields: the consumer, the reserved gates, the close rule, and acceptance of the default limits (fusion runbook `:88,:92`). A `claude -p` agent that stops to ask ends the run.
  - Fix: pre-state every operator-owned answer. Tell the agent to write a `### Stop` of kind `handoff` instead of asking.
- **B1.** If the fixture already holds a fit check, grounding may find the question answered, and the model-changing hook never fires.
  - Fix: give the fixture no overflow or fit check. Make the goal one that needs a model change, and say so in the brief.
  - Evidence should show `goal.md` § Invariants naming the preserved choice: installed pump capacity stays a supplied input.

### Minor (advisory)

- **A1. Two adjacent statements of the same distinction** (design.md:383). The new Architecture bullet sits directly under template `:59`. Consider appending "do not set one from the other; see `design-choices.md` (Technical Patterns below)" to `:59` and dropping the bullet. If the bullet stays for visibility, D3 should say why two adjacent statements beat one.
- **A2. Stage pointers re-list a scope that is already drifting** (design.md:406-407). Reword both: "Where the design-choice row of the technical-pattern table applies, check the actual bindings against `design-choices.md`."
- **A3. The authority stanza's pointer and date** (design.md:372).
  - Pointer: `git log` cannot run in an installed target, and it may land on a commit that lacks the crosswalk. Name the record instead: "the SC6 crosswalk in agentic-mbse's goal-layer-port work record". Or make the commit that adds the doc carry the crosswalk.
  - Date: tag it "obligations `[AGENT]` ratified 2026-09-20; generalization `[AGENT]` 2026-10-11, owner-read at PR".
- **A4. The runbook `:84` hook** (design.md:441).
  - Carry the pattern into the invariants: "carry applicable requirements and the design-choice pattern into its invariants".
  - Either add the one-line resolver command, or fix Implementation Notes (design.md:220). SC3 tests for the resolver.
- **A5. The `goal.md` bullet now applies to every goal** (design.md:445). Prefix it "For a model-changing goal,".
- **A6. D10's research fallback never fires** (design.md:95, :456). Every target has `/research`. Reword: "the research procedure the project's instructions name; otherwise `/research` and `/manage-sources`."
- **A7. D7 lacks the epic's amendment clause** (`epic_wrap-split.md:148`). Add it to D7 and the decision record's opening: a later fusion-tea amendment reaches targets by an ordinary toolkit change, not by reference. This closes lens smell 1.
- **A8. A6 restates a general clause** (design.md:419). The conductor bullet repeats rule 6's clause, which is the anti-pattern A4 adds. Trim it to the application plus "(`design-choices.md`, rule 6)".
- **A9. A fusion term reads as general** (design.md:335). "Generated and native execution" → "every supported execution route".
- **A10. Name the environment for each resolver hop.**
  - D2 must use this worktree's environment, since fusion's pin lacks the file. Record that.
  - D4 step 5 must run the hop in fusion's own environment after the pin move (`uv run --no-sync python -c …`). That run is the real proof that MR-7's chain resolves.
  - Add `MODELING_GUIDE.md` (updated silently) to D2's expected output.
- **A11. Two runbook lines Appendix B misses.**
  - `:262` "the Item 4 proof run": cite ADR-0003's amendment instead.
  - `:272` "an ADR if it is a decision": say "the target's decision record".
- **A12. Rule 6 drops two qualifiers.** Restore "empirical validity" and "physical adequacy".

---

## Recommendations

1. **Make A1 read as a pattern (M1).** Add the validated SysML pair, the Verification section and the two Related Patterns lines. Close the doc with the stanza as a paragraph.
2. **Give the trigger one home (M2).** A1 § Review points at "Process Selection"; Invariant 1 says so.
3. **Restore force and scope in rules 2, 3, 5 and 7 (M3).** These are the conditions of the SC6 check.
4. **Rebuild the SC4 dry run (M4).** Use a wheel-installed venv, an isolated config, pre-stated answers for every operator-owned field, and a goal that needs a model change.
5. **Apply the advisories.** A3, A4, A7 and A10 matter most: they make the provenance, resolver and fusion chain checkable.

---

## Resolutions

Orchestrator calls, 2026-10-11. All `[AGENT]` (orchestrator); none is an owner decision.

- **M1 Pattern shape: accepted as proposed.** Validated wrong/right SysML pair built on the D16 sump/pump fixture (one model serves the example and the dry-run seed), a Verification section (validate cannot see the rule; how to check by hand), `adr002-calculations.md` and `semantic-operators.md` under Related Patterns, and the authority stanza as a closing plain paragraph like Equality intent's.
- **M2 One trigger home: accepted as proposed.** "Process Selection" is the trigger's one home; the runbook row is its goal-layer mirror; A1 § Review points at "Process Selection".
- **M3 Force and scope: accepted, reviewer's wording verbatim** for rules 2, 3, 5 and 7.
- **M4 Dry run: accepted.** Wheel built with `uv build` and installed into a scratch venv outside any repo; `init` and the agent run from there. Every operator-owned answer pre-stated, with an instruction to write a `### Stop` of kind `handoff` rather than ask. A fixture with no fit check and a goal that needs a model change; evidence shows the preserved choice in `goal.md` § Invariants. On config isolation: the agent must keep working authentication, so specify the requirement (no user-level instructions, skills or memory reach the agent) rather than one mechanism; the orchestrator picks the mechanism at run time and the evidence records what user-level config the agent could see.
- **A1: fold into `:59`.** Append the pointer clause to the seed sentence and drop the separate bullet. One statement beats two adjacent ones; D3 is updated.
- **A2, A4, A5, A6, A7, A9, A10, A11, A12: accepted as proposed.**
- **A3: drop the pointer.** The authority paragraph carries grades and dates only ("obligations `[AGENT]` ratified 2026-09-20; generalization `[AGENT]` 2026-10-11 at the owner's direction"). It cites no `git log` and no `.project/` path, since neither exists in an installed target. The SC6 crosswalk is item evidence and goes in the commit that adds the document.
- **A8: accepted.** Trim the conductor bullet to the application plus "(`design-choices.md`, rule 6)".
- **SC6 re-check:** after the revision, the reviewer re-checks the revised A1, A2 and A6 against its SC6 table before the plan is written (round 2).

---

**Overall:** Revise

**Next Steps:**

1. Record resolutions above.
2. Return to `/_my_design` and point it at this review. The reviewer does not edit the design.
3. Once the design is revised, M3's exact wording is the condition of the SC6 check. If A1 changes beyond these fixes, a fresh reviewer diff-checks it before F1 copies template bytes.
