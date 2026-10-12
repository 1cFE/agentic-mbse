# Spec Review: goal-layer-port (`WRAP-SPLIT` Item 2)

**Spec:** `.project/active/goal-layer-port/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md` (not readable from this sandbox; the review used the brief, the capture-fidelity rule and the review command's lenses)
**Review File:** `.project/active/goal-layer-port/spec-review.md`
**Brief:** `.project/active/goal-layer-port/briefs/spec_review.md`
**Date:** 2026-10-11

Each finding is graded **must-fix** or **advisory**. fusion-tea paths are at `2b1e9f9d5`, read from `.orchestrate-logs/fusion-tea-snapshot/`.

---

## Reality Check

**Sound.** The spec is about the right work item, and its Problem section is accurate. I checked every code-facing claim and they hold: `cli/__init__.py:27,40,48,365-369,486-503`, `installation.py:121`, `test_shipped_text.py:17-31,41-54,57-72,75-78`, the stage-skill lines in the enforcement map, MR-7 at `REQUIREMENTS.md:87-107`, the four-place diff between fusion-tea's `MODELING_PROCESS.md` and the shipped template, and fusion-tea `.gitignore:25,27`. The owner quotes are verbatim. The grades on MR-7 (principle owner-verbatim, application agent-written and owner-ratified) are carried correctly.

The problems are in three places:

- The enforcement map misses two levels where modelers and reviewers act.
- The success criteria would not catch a port that quietly changed the runbook's method.
- Some fidelity slips in the MR-7 summary change the rule's force.

All of these can be fixed with edits.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim · must-fix:** The summary turns MR-7's "Ordinary physical balances, geometry identities and operating-point calculations are not *automatically* violations" (`REQUIREMENTS.md:97`) into "are not violations" (spec `:81`). Non-Goals repeats it: "MR-7 itself says ordinary balances are not violations" (spec `:135`). That is a blanket exemption MR-7 does not grant. An operating-point closure that binds installed capacity to demand is both an operating-point calculation and a violation. A design agent working from spec `:81` would ship the weaker rule. Restore "automatically" in both places.

**L1-2 · Direct claim · must-fix:** The spec puts general content into "what only fusion-tea needs".

- Spec `:117` keeps "its examples" in MR-7 as fusion-only. But MR-7's examples are general engineering with no fusion term: `capacity = required_flow * margin` bound as installed capacity, required versus installed area, and `volume = area * length` (`:107`); also required flow versus pump capacity and required versus exchanger area (`:97`).
- These are the worked examples a detailed pattern reference exists to carry. The template says its summaries work "without duplicating their full examples", which live in the detailed reference (`MODELING_PROCESS.md.template:66`).
- Likewise, "neither a failed physical constraint nor permission to extrapolate silently" (`:98`) is general, but it rides on the conductor example that spec `:117` keeps in fusion-tea.
- SC6 lets any sentence go to "its fusion-tea home" without giving a reason, so an auditor cannot catch a misrouted general sentence.

Narrow spec `:117` to what is actually fusion-only: the conductor-performance wording and the depth-rubric pointer. Have SC6's crosswalk give a one-line reason for every sentence it routes to fusion-tea.

**L1-3 · Rewrite request · advisory:** The obligation summary (spec `:77-87`) is labelled a summary, with SC6 as the completeness check (product-lens spec-F3). It still drops general content a design agent would need:

- the three acceptance assertions: selected design unchanged, constraint changes meaningfully, inventory and cost follow the selected design (`:105`);
- "using the supported execution route" (`:105`);
- "implementation convenience does not authorize hiding a design-selection rule inside a physical component" (`:96`);
- the five-role vocabulary: chosen, calculated, requirement, installed capacity, policy-selected (`:101`);
- "must not be presented as a fully evaluated chosen design" for cost proxies (`:99`).

It also narrows "A calculation or binding" to "A binding" (`:91`). Either add these, or state that design works from MR-7's text and not from the summary.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim · must-fix:** The map leaves out the existing shipped pattern closest to this rule, which goes to the heart of the owner's direction.

- **The pattern.** "Equality intent" in `docs/patterns/constraints.md:46-69` and `skills/sysml-conventions/SKILL.md:200-211` says: "An equality gate over a parameter you meant to vary does not judge the design, it deletes the degree of freedom."
- **Its shape.** The need is owner-stated and the classes are `[AGENT]` ratified (`constraints.md:64`).
- **Its convention.** It renders one instruction in two places with an authority note: "This is not a second authority — it is the same instruction, rendered where the instructed reader is" (`constraints.md:68-69`).
- **The relationship.** MR-7 is the binding-side twin of this constraint-side rule. Both are about not silently deleting a design choice.

The spec never maps `sysml-conventions`, though the spec brief listed it and `implement-model:25` follows it. It does not say how the new rule relates to "Equality intent". The options are to extend it into one "preserve design freedom" pattern, to cross-reference the two, or to keep them separate on purpose. It also does not say whether the shipped rule carries its grade the way `constraints.md:64` does.

Add both files to the map. Add the relationship as a design question constrained by SC5(a). Add `sysml-conventions` to SC5(d)'s trace. This is the most literal reading of "we have specific patterns which agentic-mbse is supposed to enforce, this should fit into that", and the spec does not consider it.

**L2-2 · Direct claim · must-fix:** The goal runbook has its own review-trigger table, and this item ships it. The map omits it.

- **Where it is.** Fusion `GOAL_RUNBOOK.md:70-76` holds a near-copy of "Process Selection". `STUDY_POLICY.md:162` and the run-study runbook (`:75`) restate it again.
- **Who uses it.** It is the table a goal coordinator checks at the disposition checkpoint (`:164`) and at round closure (`:184`).
- **What it lacks.** It has no design-choice row. Today `run-goal:53` and runbook `:139` stand in for one.

If the trigger lands only in the shipped "Process Selection", goal closure can certify coverage without asking about design choices. Add this level to the map and to SC5(b)/(d). Leave the choice between adding a row and deferring to "Process Selection" to design. Also say whether that change counts as "changing the runbook's method" (Non-Goals, spec `:136`). As written, the Non-Goal can be read to forbid both options.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim · must-fix:** No success criterion checks that the runbook's method is preserved.

- Spec `:106` is `[INFERRED]` and lists the method, but nothing verifies it.
- SC4 exercises only grounding and round opening.
- SC9 records only lines *left out*, not lines reworded.

A port that changed the retry cap, a close trigger or a task-outcome name would pass every SC. Add an SC: diff each ported file against its fusion-tea source at `2b1e9f9d5` and assign every hunk a class. The classes are consumer path to general wording, MR-7 hook to pointer, decision-record citation, interim research wording, two-PM condition, and goal-close heading. Any hunk with no class fails the SC. Spec `:106`'s "Only consumer paths, the design-choice hooks and the decision-record citations change wording" also omits classes the spec itself requires (`:107-108`, the goal-close heading at `:147`, and the interim research wording at `:149`). Fix the list to match.

**L3-2 · If-then tradeoff · must-fix:** SC5(a) and the port pull against each other in the goal layer.

- **What the hooks hold.** Runbook `:84`, `:100`, `:139` and `run-goal:53` hold goal-procedure steps: identify the preserved choices at grounding, record the justification before a role change, carry the rule into every brief, and record compliance at task return.
- **Strict reading.** If SC5(a) is read strictly ("every other shipped mention is a pointer … or a one-line point-of-use summary"), these steps shrink to bare pointers and the goal procedure is lost.
- **Loose reading.** If it is read loosely, they keep restating rule content. For example, `:139` says "Record compliance as compliant, violated or unverified."

Say which text is the rule, stated once, and which is the goal layer's moment of applying it, which stays in the runbook. Otherwise two designers build different things and an auditor cannot grade SC5(a).

**L3-3 · Question to the user · must-fix:** SC5(b)'s trigger list does not match MR-7, and SC5(c) inherits the mismatch.

- **Too narrow.** MR-7 `:103` triggers on "a changed design-variable assignment or automatic selection policy". SC5(b) says "a *new* automatic sizing or selection policy", so a changed policy is not routed.
- **Too broad.** SC5(b)'s "a change to which quantities are chosen or calculated" covers any quantity, not just design variables. In every target, it would send a calc-direction refactor of a geometry identity to independent design review. That cuts against the template's "scale the preparation to the uncertainty" (`MODELING_PROCESS.md.template:3,17`) and MR-7's own exemption for identities (`:97`).
- **Point-of-use row.** SC5(c) ties the row to "those changes". That drops operating-point closure and demand-based costing, which fusion's `:17` paragraph sends to the rule. Spec `:119` then claims the `:17` paragraph is "covered".

**Question:** should every target pay for independent review on any chosen-or-calculated role change, or only on design-variable assignments and selection policies, as MR-7 `:103` says? I recommend MR-7's scope for the review trigger in SC5(b), and fusion `:17`'s wider scope for where the rule is read in SC5(c). Leave the wording to design and the SC6 fresh review.

**L3-4 · Direct claim · must-fix:** SC2 and SC10 contradict each other.

- SC2 greps the decision record for `fusion-tea|\.project/|MR-[0-9]…` and requires no match outside labelled examples.
- SC10 requires the decision record to cite each ADR "by fusion-tea path at a named commit". The epic's authority stance depends on those citations (`epic_wrap-split.md:149`).

No decision record passes both. Exempt provenance citations from SC2, and say the same for the derivation record if it ships. Advisory additions to the grep while there:

- "depth target" (`run-goal:53`, runbook `:100`) is a fusion-only concept the grep misses.
- A bare `ADR-0009` (runbook `:289`) is caught by none of SC2, SC3 or SC10.

**L3-5 · Rewrite request · advisory:** SC4 leaves out two things a dry run needs.

- **The operator.** The runbook makes the operator agree to `grounded` (`GOAL_RUNBOOK.md:86,92`) and confirm the slug (`run-goal:45`). SC4 does not say who plays the operator.
- **Something to ground on.** A bare `init` holds only templates, so "repository paths for what is already known" will be thin.

Name the operator stand-in and a seed, such as a fixture model. Otherwise two auditors can disagree on whether the dry run passed.

**L3-6 · Direct claim · advisory:** The shipped contract test can collide with fusion-tea's own.

- fusion-tea keeps `tests/orchestration/test_goal_contract.py`, with the ADR-register check the Align record leaves it (`align.md:13`).
- If the shipped test installs at that path as a tool-owned file, `--force` replaces it without a backup (spec `:100`), and the ADR check is lost.
- In a fresh target the narrative-link check passes trivially, because there are no narratives (spec `:126`).

Have SC8 show two things: the installed test running over fusion-tea's 12 narratives, and fusion-tea's ADR-register check still present and passing.

**L3-7 · Question to the user · advisory:** SC7 needs two clarifications.

- **Is the file tracked?** SC7 says fusion-tea's `MODELING_PROCESS.md` "equals the shipped template" on a branch. But fusion-tea `.gitignore:30` ignores that file, and fusion-tea `CLAUDE.md` calls it "gitignored". If it is untracked, the branch diff cannot carry the change, and the no-loss end state rests on the owner's working copy. Item 1's rehearsal shows `MODELING_GUIDE.md` is tracked despite its ignore line (`.project/completed/20261009_native-skill-distribution/plan.md:861`), so this is probably fine. The orchestrator should confirm with `git ls-files modeling_project/MODELING_PROCESS.md`.
- **What does "resolves" mean?** SC7's "cites the rule at its installed location" and SC8's "chain resolves" are unclear if the rule's home is a `docs/patterns/` reference, which is the lean at spec `:141`. That file is not installed into the target and is reached only through `get_docs_dir()`. Say what "resolves" means for a resolver path.

**L3-8 · Rewrite request · advisory:** SC5(d)'s trace leaves out `model-validation`. MR-7's acceptance duty, testing an insufficient and a sufficient supplied design (`:105`), is about choosing checks. `model-validation` is where checks are chosen (`quick-model:21`, `MODELING_PROCESS.md.template:84`). Add it to the trace.

**L3-9 · If-then tradeoff · advisory:** The budget (spec `:128`) adds about an hour for the placement checks. It does not count the work the Align record moved into this item: the MR-7 rewrite, the fusion-tea branch (SC7) and the rehearsal (SC8). The epic's two days assumed MR-7 stayed unchanged and the owner applied the fusion-tea changes (`epic_wrap-split.md:156,162`). With L2-1, L2-2 and L3-1 added, the item is probably over two days.

- **If** design's re-estimate stays near the ceiling, the existing shed list is enough. The SC8 goal-skill switch already has an escape to the epic integration step.
- **If** it goes well over, split the item. Port the goal layer first, with its hooks pointing at "Process Selection" and the target's requirements file. Then place the rule as its own short item. That beats shedding inside the rule work, which is the part the owner asked to get right.

### Lens 4 — Hygiene

No material findings.

### Lens 5 — Reader Comprehension

No material findings. The enforcement map (spec `:29-37`) and the SC5 sub-checks are clear on one read. The citation run in the Problem's first paragraph (spec `:16`) is heavy, but it is evidence, not the point.

---

## Engagement Summary

**Overall take:** The spec has the right problem and an accurate map of the levels it names. But it misses the shipped pattern this rule most naturally fits ("Equality intent" in `constraints.md` and `sysml-conventions`). It also misses the goal runbook's own review-trigger table, which this item ships. Its SCs would not catch a port that drifted the runbook's method, and two SCs (SC2, SC10) cannot both pass.

**Here's what I need you to weigh in on:**

1. **[L2-1]** Decide how the design-choice rule relates to the existing "Equality intent" pattern: one "preserve design freedom" pattern, a cross-reference, or deliberately separate. This is the nearest existing pattern to "fit into".
2. **[L3-3]** Trigger breadth: does every target owe independent review for *any* change to which quantities are chosen or calculated, or only for design-variable assignments and selection policies (MR-7 `:103`)? I recommend MR-7's scope.
3. **[L2-2, L3-2]** In the goal layer: does the runbook's trigger table get a design-choice row or defer to "Process Selection"? And which goal-procedure text stays in the runbook, as opposed to being reduced to a pointer?
4. **[L3-1]** Add a hunk-level diff criterion so a method change cannot slip through the port.
5. **[L1-1, L1-2]** Restore "automatically", and keep MR-7's general examples in the shipped rule, not only in fusion-tea.
6. **[L3-4]** Exempt provenance citations from SC2's grep so the decision record can pass both SC2 and SC10.
7. **[L3-9]** Re-estimate at design. If the item runs well over two days, split rule placement from the port.

---

## Resolutions

Orchestrator calls, 2026-10-11. All `[AGENT]` (orchestrator) unless marked; none is an owner decision.

- **L2-1 Equality intent: accepted.** Map `sysml-conventions` and `docs/patterns/constraints.md` "Equality intent" as an existing pattern level. Require that the design-choice rule and equality intent are presented as related: both keep the design space open, one against removing a choice by binding it to demand, the other against removing freedom with an exact equality. Design chooses between one family pattern and a new reference with cross-references both ways. Constraint: do not rewrite equality intent's content or its authority stanza (sysml-codegen-backed guidance; its authority pointer is Item 4's). Adding a cross-reference line there is allowed. Lean: a new detailed reference that names equality intent as its sibling, plus one cross-reference line in `constraints.md` and one in `sysml-conventions`.
- **L3-3 Trigger breadth: MR-7's scope.** The "Process Selection" trigger uses MR-7's enforcement wording (fusion-tea `REQUIREMENTS.md:103`): a changed design-variable assignment (a quantity moves between chosen and calculated, or a design choice leaves the public interface), an introduced or changed automatic sizing or selection policy, and installed capacity, equipment or inventory bound to computed demand. "Changed", not only "new". Not every change to a calculation's direction. Basis: MR-7's enforcement text is agent-written and owner-ratified; widening it for every target is not authorized.
- **L2-2 / L3-2 Goal runbook: accepted.** The runbook's own review-trigger table (fusion-tea `GOAL_RUNBOOK.md:70-76`) gets a design-choice row that points at the shipped rule. Clarify SC5(a): "one statement" covers the rule's obligations (what must hold). Procedure text that says when to apply them, what to record and what to carry into briefs stays in the runbook as procedure and cites the rule. The hooks at runbook `:84`, `:100` and `:139` keep their procedural content, generalized.
- **L3-1 Method diff: accepted.** Add a criterion: a hunk-level diff of each shipped goal-layer file against its fusion-tea original at `2b1e9f9d5`, every hunk classified (consumer path generalized, design-choice hook generalized, decision-record citation, recorded-practice addition such as the goal-close heading, or deletion with ledger row). No hunk may be classified as a method change. Recorded in evidence.
- **L1-1 / L1-2 Fidelity: accepted.** Restore "not automatically violations". MR-7's general engineering examples (`capacity = required_flow * margin` bound as installed capacity; required area compared with independently selected installed area; `volume = area * length`; required flow is not evidence of installed pump capacity) ship in the shipped rule as labelled examples. A fusion-flavoured example (the conductor-performance one) may ship labelled or stay in MR-7; design decides.
- **L3-4 SC2 vs SC10: accepted.** SC2 exempts provenance citations in the decision record (and a derivation record if one ships): they cite fusion-tea as provenance, not authority. Add the advisory grep terms: "depth target" and bare decision-record numbers such as `ADR-0009`.
- **L3-9 Budget: re-estimate at design; do not split.** Rationale: the owner asked to keep the item count low; the rule's placement and the goal hooks edit the same files; and the placement is the owner's central ask, so moving it to a later item delays exactly that. An overrun is accepted and recorded with its cause (the Align record moved the MR-7 rewrite and the fusion-tea branch into this item). The shed list stays for anything else.
- **L3-5 Dry run: accepted.** The dry-run brief pre-states the operator's answers (agree to `grounded`, confirm the slug) so the orchestrator stands in for the operator without live input. Seed the scratch target with a small fixture model so grounding has something to cite. Design names the seed.
- **L3-6 Contract test: accepted.** The shipped test must not overwrite fusion-tea's `tests/orchestration/test_goal_contract.py`. SC8 shows the installed test passing over fusion-tea's 12 narratives and fusion-tea's ADR-register check still present and passing.
- **L3-7 Tracked file: verified by orchestrator 2026-10-11.** `git ls-files` at fusion-tea `2b1e9f9d5` lists `modeling_project/MODELING_PROCESS.md`, `modeling_project/MODELING_GUIDE.md`, `work/orchestration/GOAL_RUNBOOK.md`, the three goal templates, both local goal skills and `tests/orchestration/`. They are tracked despite the `.gitignore:30-31` lines, so the branch diff carries them. "Resolves" for a resolver path: the cited file exists under the installed toolkit's `get_docs_dir()`, and the citation names the resolver the way `MODELING_GUIDE.md.template:276-280` does.
- **L3-8 `model-validation`: accepted.** Add it to SC5(d)'s trace.
- Remaining advisories: apply at the spec author's judgment.

---

**Verdict:** Revise
**Next Steps:** Record resolutions above, then return to the spec agent (`/_my_spec`) and point it at this review. The reviewer does not edit the spec. The must-fix items are L1-1, L1-2, L2-1, L2-2, L3-1, L3-2, L3-3 and L3-4.
