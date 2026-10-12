# Brief: /_my_spec — goal-layer-port (`WRAP-SPLIT` Item 2)

You are writing the spec for Item 2 of the `WRAP-SPLIT` epic, run by an orchestrator. Write it to `.project/active/goal-layer-port/spec.md`. Do not commit; the orchestrator commits. Start no background tasks. End your final message with `ARTIFACT: <path>`.

## Read first

- The work item: `.project/backlog/epic_wrap-split.md`, the header's owner decisions and "Item 2" in full. Items 4 and 5 for boundaries.
- The Align record: `.project/active/goal-layer-port/briefs/align.md`. It amends the epic. Where they differ, the Align record wins.
- The research audit: `.project/research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md` § 1a, § 2, § 5, "Architecture Insights". Its fusion-tea line numbers are stale; use the snapshot below.
- Item 5's spec, `.project/active/research-seam-port/spec.md`, lines 14, 69, 90–91 and 111 (its overlap with this item).
- The shared ledger: `.project/active/wrap-split-migration-ledger.md` (this item owns it; Item 1 added its rows).

## The fusion-tea snapshot

You cannot read `/home/reid/1cfe/fusion-tea`. The orchestrator copied what you need, at fusion-tea commit `2b1e9f9d5` (its `main`, 2026-10-11), into `.orchestrate-logs/fusion-tea-snapshot/` with paths preserved. Read it; do not edit or run anything there. Cite fusion-tea files by their fusion-tea path at `2b1e9f9d5`, not by the snapshot path. It holds: the `run-goal` and `narrate-goal` skills, `work/orchestration/GOAL_RUNBOOK.md`, `goal-templates/`, one real goal (`goals/burn-control/`), `work/narratives/`, `tests/orchestration/`, `.project/adr/` (all 12 records), `modeling_project/{REQUIREMENTS,MODELING_PROCESS,STUDY_POLICY}.md`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `.agentic-mbse/{install.json,codex.md,claude.md}`, the `run-study` runbook, the MR-7 spec (`.project/active/modeling-intent-enforcement/`), the depth-rubric application policy, and the goal-harness concept.

## Intent

[AGENT] (owner did not object at Align, 2026-10-11) Three outcomes, in this order of weight:

1. A target that is not fusion-tea gets a working goal layer from `agentic-mbse init`. The test is a fresh scratch target grounding a goal and opening a round with only installed files, and no installed text pointing at fusion-tea.
2. The design-choice rule (MR-7's principle) lives in agentic-mbse's shipped enforcement system, so fusion-tea's MR-7 enforcement no longer depends on paragraphs hand-pasted into a tool-owned file that a re-init replaces.
3. fusion-tea can move to the installed copies without losing any instruction.

This is a port that preserves behaviour. Replace consumer paths with general wording; do not redesign the runbook's method. It has run about a dozen goals and eleven narratives in fusion-tea.

## The central question: the right level for the design-choice rule

[OWNER-VERBATIM] 2026-10-11, on editing MR-7: "yes. in fact, it is important that you find the right level for this rule -- we have specific patterns which agentic-mbse is supposed to enforce, this should fit into that".

What this changes against the epic:
- fusion-tea's MR-7 may be edited. The epic's criterion that it stays byte-identical, and its out-of-scope line about MR-7 text, are superseded.
- The epic's proposed shape ("a short section in `MODELING_PROCESS.md.template` plus a process-selection row plus a `goal.md` invariant bullet") is a starting proposal graded `[INHERITED: research]`, not the answer. The spec must require that the rule fits agentic-mbse's existing enforcement system, and must say what "fits" means in checkable terms.

agentic-mbse already enforces modeling rules at several levels. The spec should map them, and state as requirements which levels must carry this rule. Placement details are for design, but the spec must constrain them. Levels the orchestrator found (verify each, and look for others):
- **Process rules** in `project_templates/MODELING_PROCESS.md.template`: "Architecture & Design" (its first bullet already seeds the idea: "Distinguish quantities with different meanings, such as installed capacity and operating demand"), and the "Process Selection" table, which sets the review each kind of change needs.
- **Point-of-use pattern table** in the same template ("Technical Patterns: Read at the Point of Use": when changing X, the rule to preserve, the detailed reference), backed by `docs/patterns/*.md` and navigated from `MODELING_GUIDE.md.template`.
- **Skills that apply the rules**: at least `skills/{spec-model,design-model,review-model,audit-models,implement-model,sysml-conventions,model-validation,requirements-tracking}`. Find where each checks patterns or requirements today.
- **Project requirements**: `REQUIREMENTS.md.template` (user-owned, PR-XXX entries for project rules) and the `requirements-tracking` skill's promotion path. A target's own rule, such as MR-7, lives at this level.
- **Automated validation** (levels 1–6 in `src/agentic_mbse/validation/`). Do not assume the rule can be machine-checked. If you judge some part could be, record it as a candidate follow-up, not scope, unless it is clearly small.

The rule should be stated once, with one authoritative home, and reached from the points where a modeler or reviewer acts. Avoid several hand-synchronized copies. The rule must be stated generally, with no requirement number, rubric path or fusion-only term as authority; fusion examples may appear if labelled as examples. MR-7's own text (fusion-tea `modeling_project/REQUIREMENTS.md:87-107`) is the owner-grade source: its Authority line is `[OWNER-VERBATIM, 2026-09-20]`, and its application and enforcement text is `[AGENT]` ratified by an implementation request. Preserve that grading when you derive the general rule.

What happens to MR-7 in fusion-tea is part of this item: it becomes fusion-tea's application of the shipped rule. Say what stays in MR-7 (its fusion examples and fusion-specific application, the owner quote) and what it now cites. The two paragraphs in fusion-tea's `modeling_project/MODELING_PROCESS.md` (lines 17 and 34 at `2b1e9f9d5`) are covered by the shipped rule or re-homed. [AGENT] (orchestrator recommendation; the owner allowed MR-7 edits instead) the fusion-only remainder goes to MR-7 or to fusion-tea's `AGENTS.md`, which Claude and Codex both read; fusion-tea `CLAUDE.md:5` already points at MR-7 from there.

## Other owner decisions you inherit

- Epic header ([OWNER], 2026-10-06): fusion vocabulary is acceptable in examples; what must go is pointers into fusion-tea or sysml-codegen internals as authority, hard-coded machine paths, consumer requirement numbers, and instructions that only make sense for one project. No loss of information for fusion-tea: every removed consumer-specific instruction gets a ledger row and a fusion-tea home. Keep the item count low.
- [OWNER-VERBATIM] 2026-10-11, on fusion-tea writes: "just do it yourself." The orchestrator makes the fusion-tea change in its own fusion-tea worktree and branch; the owner pushes and merges. So the fusion-tea side is in scope as a deliverable on a fusion-tea branch, not only as a proposed patch. Subagents cannot reach fusion-tea; write fusion-tea work so the orchestrator can carry it out (exact file changes, destinations, checks).
- [AGENT] (ratified by owner 2026-10-11, "fine"): the shipped contract-test template carries only the narrative-link check from fusion-tea `tests/orchestration/test_goal_contract.py`. The ADR-register check stays fusion-tea's.
- [AGENT] (ratified by owner 2026-10-11, "fine"): the research-result → task-outcome table that Item 5's spec (line 91) assigns to this item lands with Item 5's relabel step. This item uses interim wording for research references, per the epic.

## Facts the orchestrator verified (2026-10-11)

- fusion-tea line counts at `2b1e9f9d5`: `run-goal/SKILL.md` 73, `narrate-goal/SKILL.md` 79, `GOAL_RUNBOOK.md` 305, `goal-templates/{goal,trail,learnings}.md` 58/82/15, `test_goal_contract.py` 47. `735a5d801` ("Enforce design-choice preservation in goal and modeling workflows") is the commit that added the MR-7 hooks.
- MR-7's Enforcement paragraph (fusion-tea `REQUIREMENTS.md:103`) already says a changed design-variable assignment or automatic selection policy "triggers the independent design review required by `MODELING_PROCESS.md`". The shipped template has no such trigger today.
- fusion-tea's `MODELING_PROCESS.md` differs from the shipped template in four places: the two MR-7 paragraphs, a pattern-location line (`.agentic-mbse/patterns/` instead of the toolkit's `docs/patterns/`), and a one-character fix in the binding row (`in volume = volume;` gains its semicolon). The last two are not this item's MR-7 work. The semicolon fix is a candidate correction to the shipped template; decide and record it.
- The decision records the runbook cites are fusion-tea ADR-0001..0007. ADR-0009 (integration as a fixed-point proof) is cited by runbook line 289 and belongs to the study side (Item 3). ADR-0008 (source identity) is Item 5's. ADR-0010..0012 are fusion-specific.
- `cmd_init` (`src/agentic_mbse/cli/__init__.py`, `USER_OWNED_TEMPLATES` at :27, `TOOL_OWNED_TEMPLATES` at :40, the directory list near :486) creates neither `work/orchestration/` nor `work/narratives/`. Tool-owned templates go through `Installer.write` (`src/agentic_mbse/cli/installation.py:150`), whose `permit` decides what happens to an existing file the manifest does not know. fusion-tea already has untracked-by-manifest files at `work/orchestration/GOAL_RUNBOOK.md` and `work/orchestration/goal-templates/`. The spec should require a defined, loss-free outcome when a target already holds its own copies.
- `skills/orchestrate-modeling/SKILL.md` already writes `work/orchestration/<objective-slug>.md` and defers to "the target project's goal or study workflow". Once `run-goal` ships, decide whether that text names it.
- Adding a skill is adding `skills/<name>/SKILL.md` with `metadata.kind`; tests derive the inventory from the tree (CLAUDE.md "Change Coordination").

## Constraints on the spec

- Grade every requirement per the capture-fidelity rule: `[HARD]`, `[NEED]` (owner-stated), `[INFERRED]`, `[INHERITED]`. Owner-verbatim items above absorb as `[NEED]` with the quote. Do not mark agent recommendations as owner needs.
- Every success criterion must be checkable by the auditor from files and commands, including the fresh-target dry run and the fusion-tea side.
- Keep the item inside its two-day budget. If the right-level work pushes it over, say so and propose what to shed rather than silently growing.
- Item 4 owns the read-through sweep of other shipped files; Item 3 owns everything study-side; Item 5 owns the research seam. Touch their files only where this rule's placement requires it, and say so.
