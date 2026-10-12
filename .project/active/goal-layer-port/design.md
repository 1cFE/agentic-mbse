# Design: Port the goal layer, and fit the design-choice rule into agentic-mbse's pattern set

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-10-11
**Updated:** 2026-10-11
**Branch:** `goal-layer-port` at `75b30b3` (worktree `/home/reid/1cfe/agentic-mbse-goal-layer`); fusion-tea branch `goal-layer-mr7` in the orchestrator's worktree `/home/reid/1cfe/fusion-tea-goal-layer`, cut from `2b1e9f9d5`
**Epic:** `WRAP-SPLIT`, Item 2

## Overview

Ship `run-goal`, `narrate-goal`, the goal runbook, three goal templates, a narrative-link contract test and a goal-layer decision record from agentic-mbse, with the runbook's method unchanged. Place the design-choice rule (fusion-tea MR-7's general content) as a new pattern reference, `docs/patterns/design-choices.md`, reached the way every other agentic-mbse pattern is reached, and make fusion-tea's MR-7 that project's application of it.

## Related Artifacts

- Spec: `.project/active/goal-layer-port/spec.md` (revised after review); review and resolutions: `spec-review.md`; Align record: `briefs/align.md`; product lens: `product-lens.md`; this stage's brief: `briefs/design.md`.
- Epic: `.project/backlog/epic_wrap-split.md` § Item 2 (Items 3, 4, 5 for boundaries). Required Reading: research `.project/research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md` § 1a, § 2, § 5 (line numbers stale); fusion-tea files read from `.orchestrate-logs/fusion-tea-snapshot/` (commit `2b1e9f9d5`).
- Overlap: `.project/active/research-seam-port/spec.md:14,69,90,111` (Item 5 relabels the research wording and may add ADR-0008 to this item's decision record).
- Precedent: `.project/completed/20261009_native-skill-distribution/evidence/fusion-tea-runbook.md` (Item 1's pin move and re-init).
- Ledger: `.project/active/wrap-split-migration-ledger.md`.
- Decision records: this repo has no `.project/adr/` register, so there are no prior entries to cite and none to file.

## The Point

agentic-mbse ships general capability that a target gets from `init`. This item owes two things, and one constraint on how fusion-tea gets there.

- **A working goal layer for every target.** A fresh target can ground a goal and run rounds from installed files alone, with nothing pointing at fusion-tea. The authority for shipping it everywhere is [OWNER] "Goals are general to the systems-engineering and concept-development process" (fusion-tea concept `:198`).
- **The design-choice rule in the right place.** [OWNER-VERBATIM] 2026-10-11: "it is important that you find the right level for this rule -- we have specific patterns which agentic-mbse is supposed to enforce, this should fit into that". The principle it generalizes is [OWNER-VERBATIM] 2026-09-20: "As soon as you start introducing 'sizing', then you are basically pre-defining which design parameters are 'free' and which are 'derived'. this is explicitly what we wanted to avoid." The owner will judge this item by whether the rule reads as one of agentic-mbse's own patterns.
- **fusion-tea loses nothing.** [INHERITED: epic, OWNER 2026-10-06] Every consumer-specific line left out of the shipped copies has a fusion-tea home before the agentic-mbse change merges. [INHERITED: epic `:66`, OWNER, amended by Align] MR-7 enforcement stays intact after re-init without a kept edit to a tool-owned file.

## Research Findings

- **How a rule is placed today.** `MODELING_PROCESS.md.template:64-74` is a point-of-use table: "When changing", "Rule to preserve" (one line), "Detailed reference" (a file in `docs/patterns/`). The intro says the summaries work "without duplicating their full examples" (`:66`). Targets reach `docs/patterns/` through the `get_docs_dir()` resolver (`MODELING_GUIDE.md.template:274-282`). `adr002-calculations.md` is a decision-grade rule shipped this way.
- **Pattern doc shape.** `docs/patterns/README.md:29-34` asks for rules, examples, common mistakes and verification notes. `adr002-calculations.md` and `mbse-concepts.md` use: When to Use, Core Principle, rules, Validated Patterns or examples, Common Mistakes, Related Patterns, Verification.
- **The sibling.** Equality intent (`docs/patterns/constraints.md:46-69`, `skills/sysml-conventions/SKILL.md:200-211`) carries a grade stanza and an authority pointer. `sysml-conventions` names pattern docs as "agentic-mbse `docs/patterns/<file>`" (`:226`).
- **Review routing.** "Process Selection" (`MODELING_PROCESS.md.template:19-26`) is applied by `spec-model:15`, `design-model:15`, `plan-model:15`, `implement-model:15`, `quick-model:19` and `orchestrate-modeling:39`. The point-of-use table is read by `design-model:21`, `implement-model:25`, `quick-model:21` and `audit-models:29`. `review-model` reads only the brief and "Review Brief and Context Limits" (`:15`). `model-validation` does not cite the process file.
- **Tiering.** `requirements-tracking:24,38-43` names only `MODELING_GUIDE.md` as the baseline.
- **Installer.** Tool-owned templates go through `Installer.write` (`cli/__init__.py:538-541`). Shared bundles are copied into `.agents/skills/` for every assistant choice; Claude gets a folder link (`installation.py:429-440`). An unmanifested file that differs from the new content is kept when stdin is not a terminal (`cli/__init__.py:365-369`) and replaced under `--force`. `--force` also replaces user-owned project documents, so it is unusable on fusion-tea. The dev-mode ignore block is skipped entirely when its marker line exists (`cli/__init__.py:290-293`).
- **Shipped-text tests.** `tests/test_shipped_text.py:41-54` treats every `TOOL_OWNED_TEMPLATES` destination as runtime-neutral, so new goal templates join its no-`.claude/` and named-skill checks with no test edit.
- **fusion-tea facts** (snapshot):
  - Section headings cited by fusion records: "Review scope and evidence reuse", "Grounding a goal", "What \"fresh\" means", "The fresh review", "When a cited artifact moves", "The pre-execution disposition checkpoint", "Limits" (`STUDY_POLICY.md:162`, run-study runbook `:75,:219`, goal files).
  - The discovery log is defined in the run-study runbook (`:285-287`).
  - `AGENTS.md:5` routes Codex to `CLAUDE.md`, and `CLAUDE.md:5` routes both runtimes to MR-7. `CLAUDE.md` names no research or integration seam.
  - Goal close is written `## Goal close — YYYY-MM-DD` (`goals/burn-control/trail.md:143`).
  - Plain re-init leaves fusion's `.claude/skills/<shipped>` as ignored links into `.agents/skills/` (install manifest).

## Core Concept

The goal layer is a procedure. The design-choice rule is a modeling pattern. They ship to different homes, and each reaches the other only by pointer.

**The rule joins the pattern set as one more row and one more reference.** agentic-mbse already enforces modeling rules the same way each time. "Process Selection" says which changes need independent review. The point-of-use table gives a one-line rule and names a detailed reference in `docs/patterns/`. The stage skills read those two sections. The design-choice rule enters exactly there:

- one new "Process Selection" row, at MR-7's review scope;
- one new point-of-use row, read at the wider scope of fusion-tea's process paragraph;
- one new reference, `design-choices.md`, holding the full statement once;
- one Architecture & Design bullet;
- one cross-reference line each way with its constraint-side sibling, Equality intent.

Both siblings keep the design space open: an exact equality deletes a degree of freedom, and a binding that sets installed capacity from demand deletes a design choice. Nothing new is invented, so the rule reads as if it had always been there.

**The goal layer is ported, not redesigned.** Its files keep fusion-tea's paths, section headings and method. Only four kinds of line change:

- fusion paths become general wording;
- the MR-7 hooks become pointers to the shipped pattern and to the target's own requirements file, keeping their procedural content;
- `.project/adr/` citations become a shipped decision record;
- the goal-close heading, which fusion goals already write, is named.

**fusion-tea becomes a consumer.** MR-7 keeps its authority line and anchor and states only fusion's application. Its fusion-only goal-layer lines move to fusion's `CLAUDE.md`. Its tool-owned files return to the shipped bytes, so a re-init updates them with no prompt.

## Key Bets

- **B1. Agents read a `docs/patterns/` reference when a point-of-use row names it.** Every existing construct rule depends on this route, and the SC4 dry run checks it: a fresh agent's file list should include `design-choices.md` at grounding. *If false → only the one-line rows act, and the acceptance and evidence obligations go unread. The fallback would be a `MODELING_PROCESS.md` section (D1's rejected option).*
- **B2. MR-7's general sentences hold their force without fusion terms.** Only the conductor wording and the depth-rubric policy are fusion's. *If false → the shipped rule is weaker than MR-7, or MR-7 keeps a second copy. The SC6 crosswalk and the fresh review catch it.*
- **B3. The runbook's method is separable from its fusion references.** Every fusion path in it is a pointer or a status note, never a step. *If false → the port changes the method, and SC12 finds a hunk with no class.*
- **B4. MR-7's review scope is narrow enough that every target pays for review only where it matters.** The scope is a changed design-variable role, a new or changed sizing or selection policy, and installed capacity bound to computed demand. *If false → targets treat the trigger as noise. The orchestrator chose this scope (spec L3-3) because widening it was not authorized.*

## Key Decisions

- **D1. The full statement lives in a new `docs/patterns/design-choices.md`.** A target reaches it through the resolver, like every other pattern. *Rejected:*
  - a `MODELING_PROCESS.md` section. It would be readable without the resolver, but it would be the only full rule body in a file whose summaries deliberately omit full examples (`:66`), and it would split construct rules across two kinds of home.
  - one "preserve design freedom" family pattern inside `constraints.md`. That rewrites Equality intent's home, which the spec forbids, and puts a binding rule in a constraint-syntax document.
- **D2. The trigger is a new "Process Selection" row, worded at MR-7's scope.** *Rejected: widening the `:23` row. "Binding semantics" does not name the case, and MR-7's enforcement expects an explicit trigger.*
- **D3. "Architecture & Design" gains one bullet that names `design-choices.md`. The `:59` seed sentence stays as it is.** *Rejected: rewording the seed sentence. It is about owning quantities, and folding selection into it hides the rule.*
- **D4. Stage-skill pointers go only where the trace shows a gap: `review-model` (one question) and `model-validation` (one evidence bullet).** Every other skill reaches the rule in two hops through sections it already reads (Appendix E). *Rejected: a pointer in every skill. That restates the route and invites restating the rule.*
- **D5. `requirements-tracking` names `MODELING_PROCESS.md` and the toolkit's pattern references as the baseline, and tells a project rule that applies one to cite it.** *Rejected: leaving tiering to MR-7's example. The general instruction belongs in the tier description (SC5(e)).*
- **D6. The rule carries a grade stanza like its sibling's.** It names no project and no requirement number. Its provenance (fusion-tea MR-7) lives in the derivation record and the commit, so the shipped text reads as agentic-mbse's own. *Rejected: citing fusion-tea in the stanza. That is honest provenance, but the shipped rule would read as a renumbered fusion requirement, against the owner's direction.*
- **D7. The decision record is `docs/goal-layer-decisions.md`, reached through `get_docs_dir()`.** It is a dated snapshot of fusion-tea ADR-0001..0007 and keeps their ids, grades and amendments. It cites each record as `<path>@2b1e9f9d5`. For installed targets it is the authority; fusion-tea's live ADRs govern fusion-tea only. *Rejected:*
  - a file in the `run-goal` bundle. It would be installed and directly readable, but the records explain the runbook (a template), not the skill.
  - a tool-owned `work/orchestration/` file. It adds a rarely read file to every target.
  The ADR ids stay so that the runbook's `(ADR-000N)` citations need no hunk and Item 5 can add ADR-0008.
- **D8. The goal files are tool-owned templates at fusion-tea's exact paths.** `work/orchestration/GOAL_RUNBOOK.md` and `work/orchestration/goal-templates/{goal,trail,learnings}.md` come from flat template files (`GOAL_RUNBOOK.md.template`, `goal.md.template`, `trail.md.template`, `learnings.md.template`). Same paths keep every fusion citation resolving (B3, SC8). *Rejected: new paths. Fusion records would break.*
- **D9. The contract test installs at `tests/orchestration/test_narrative_links.py` as a tool-owned template.** It finds the project root as `Path(__file__).absolute().parents[2]`, never `.resolve()`, so a `--dev` symlink still points at the target. It carries only the narrative-link check. *Rejected:*
  - `tests/orchestration/test_goal_contract.py`. That is fusion's path, and pytest also rejects two test modules with the same basename.
  - user-owned. The test is the goal layer's contract, so it must update with `narrate-goal`.
- **D10. Interim research wording names only installed skills.** The text: "the research procedure the target installs; where none is installed, `/research` and `/manage-sources`". Item 5 replaces it. *Rejected: "the installed research procedure" alone, which gives a fresh target nothing to run.*
- **D11. The runbook and trail template name `## Goal close — YYYY-MM-DD` as a recorded-practice addition.** *Rejected: leaving it unnamed. `narrate-goal` would never see a fresh target's goal as closed.*
- **D12. `orchestrate-modeling:57` names `/run-goal`. The study wording stays generic.** This is a one-line change and the third item on the shed list.
- **D13. fusion-tea gets two commits on `goal-layer-mr7`.** F1 lands the content now. F2 switches fusion-tea to the installed copies after the agentic-mbse merge. Removing the local `run-goal`/`narrate-goal`, their `.agents/skills/` links and the `.gitignore:25,27` whitelist lines goes in F2, because only a re-init at the merged pin can install the replacements. The branch merges only after F2. *Rejected:*
  - removing the skills in F1. The branch tip would have no goal skills until F2.
  - leaving the switch to a later epic step. The local copies would stay as an unflagged fork (spec-F2).
- **D14. fusion-only goal-layer lines move to fusion's `CLAUDE.md`. The depth-rubric pointer moves into MR-7.** fusion-tea's own routing sends both runtimes through `CLAUDE.md`: `AGENTS.md:5` tells Codex to read it, and `CLAUDE.md:5` says its MR-7 pointer is shared that way. This overrules the spec's `AGENTS.md` lean, which rested on both runtimes reading `AGENTS.md`; fusion-tea routes Claude through `CLAUDE.md`. *Rejected: `AGENTS.md`, which fusion-tea's routing gives only to Codex.*
- **D15. The conductor-performance example stays in MR-7.** The shipped rule carries its general sentence about out-of-domain evaluation. *Rejected: shipping a labelled conductor example. It adds a domain-specific example for little gain.*
- **D16. A purpose-built seed, `tests/fixtures/goal_dry_run/`, seeds the SC4 dry run.** It is a sump basin and a drain pump: the library calculates required pump flow, and the design supplies the installed pump capacity separately. It gives grounding real paths to cite and a design choice to preserve. *Rejected: the existing validator fixtures. Their comments describe validator cases, not a system, so grounding would be hollow.*
- **D17. SC12 gets a sixth hunk class, "bundle envelope".** It covers the frontmatter shape and the shared preface that `tests/test_shipped_text.py:17-31` requires. That requirement is a spec [HARD], so this is not a method change. Any hunk that drops a consumer-specific instruction needs a ledger row, whatever its class.

## Architecture

```
Target project (installed)                         Toolkit (resolver: get_docs_dir())
modeling_project/MODELING_PROCESS.md               docs/patterns/design-choices.md  ← one statement
  Process Selection  ─ new row ──────────────────►   ↔ docs/patterns/constraints.md (Equality intent)
  Architecture & Design ─ new bullet ────────────►
  Technical Patterns ─ new row ──────────────────►
modeling_project/REQUIREMENTS.md (target's own rules; cite the pattern)
work/orchestration/GOAL_RUNBOOK.md ─ trigger row, 3 hooks ─► design-choices.md, REQUIREMENTS.md
  § The decisions behind this ───────────────────►  docs/goal-layer-decisions.md
work/orchestration/goal-templates/goal.md ─ invariant bullet ─► design-choices.md
.agents/skills/run-goal, narrate-goal ─► runbook, templates, tests/orchestration/test_narrative_links.py
```

- **Data flow at use.** A modeler or goal agent changing a design-variable role meets the rule in two places. "Process Selection" or the runbook trigger table routes the change to independent review. The point-of-use row, or a goal hook, sends them to `design-choices.md` for what to record and how to accept. The goal layer adds when to apply the rule: at grounding, before a role change, in every brief, and at task return.
- **Boundaries.**
  - The pattern states obligations and never procedure.
  - The runbook states procedure and never obligations.
  - A target's `REQUIREMENTS.md` states its application and cites the pattern.
  - The decision record explains the goal layer and is never cited as a rule.
- **fusion-tea after F2.** `CLAUDE.md:5` → MR-7 (application, citing the pattern) → `design-choices.md` → "Process Selection" row. The installed runbook, template and `run-goal` → `design-choices.md` and `modeling_project/REQUIREMENTS.md`. None of it rests on a kept edit to a tool-owned file.

## Required Invariants

1. Only `design-choices.md` states the rule's obligations. Every other mention is a pointer, a one-line point-of-use summary, or goal procedure that cites it (SC5(a)).
2. The runbook's H2 headings are unchanged, and so are its method lists:
   - the five surfaces;
   - the six close triggers;
   - the six task outcomes;
   - the five decision fields;
   - the limits table values;
   - the fresh-review definition, the handoff and the checkpoint cap.
3. Installed goal text names:
   - no `.claude/` path;
   - no uninstalled backticked `/skill`;
   - nothing on SC2's grep list, outside labelled examples.

   Every `ADR-000N` it names is in the decision record.
4. Equality intent's table, prose and authority stanza are unchanged. The diffs to `constraints.md` and `sysml-conventions` each add one line.
5. The shipped test never writes `tests/orchestration/test_goal_contract.py`, and its basename differs from fusion's.
6. fusion-tea's `main` never holds F1 without F2. MR-7's heading, and so its anchor, is unchanged.
7. Each tool-owned goal file in fusion-tea equals the shipped bytes before F2's re-init. The re-init therefore writes it with no prompt and records it in the manifest.

## Component Overview

**agentic-mbse, rule placement**

- `docs/patterns/design-choices.md` (new). The rule, what to record, the review trigger, acceptance, examples, common mistakes, related patterns and the grade stanza. Text: Appendix A1.
- `project_templates/MODELING_PROCESS.md.template`. Three additions (A2):
  - a "Process Selection" row;
  - an Architecture & Design bullet;
  - a Technical Patterns row.

  Plus the `:71` semicolon fix.
- `docs/patterns/constraints.md` and `skills/sysml-conventions/SKILL.md`: one cross-reference line each (A3).
- Index rows for `design-choices.md` in:
  - `docs/patterns/README.md`;
  - the `MODELING_GUIDE.md.template` Pattern Documentation Index;
  - `skills/sysml-conventions/references/stencils.md`.
- `skills/requirements-tracking/SKILL.md`: tier text (A4). `skills/review-model/SKILL.md` and `skills/model-validation/SKILL.md`: one pointer line each (A5).

**agentic-mbse, goal layer**

- `skills/run-goal/SKILL.md` and `skills/narrate-goal/SKILL.md`. Ported from fusion's files with:
  - the bundle envelope;
  - `metadata.kind: workflow`;
  - the shared preface;
  - the line changes in Appendix B.
- Project templates:
  - `GOAL_RUNBOOK.md.template`;
  - `goal.md.template`, `trail.md.template` and `learnings.md.template`;
  - `test_narrative_links.py.template`, which is fusion's `_local_link_targets` and `test_narrative_evidence_links_resolve` with a module-level root.
- `docs/goal-layer-decisions.md` (new). It opens with the authority stance and the condition from ADR-0006 (it applies where a target also runs a second PM). Each record then gets an entry:
  - title, current decision as amended, grade(s) and dates;
  - its invariants in short;
  - `fusion-tea .project/adr/000N-*.md@2b1e9f9d5`.

  A closing "Sources the runbook cites" section holds the owner statements: the critic definition, goals being general, the 2026-08-27 probe amendment and the 2026-09-14 process-sizing request.
- `src/agentic_mbse/cli/__init__.py`:
  - five `TOOL_OWNED_TEMPLATES` entries;
  - `work/orchestration/goals` and `work/narratives` in the `cmd_init` subdir list;
  - three `DEV_MODE_GITIGNORE_PATHS` lines: `work/orchestration/GOAL_RUNBOOK.md`, `work/orchestration/goal-templates/` and `tests/orchestration/test_narrative_links.py`.
- `skills/orchestrate-modeling/SKILL.md:57`: names `/run-goal`. This repo's `CLAUDE.md` (template list, Init File Ownership) is kept accurate.
- `tests/fixtures/goal_dry_run/` (new). Two small SysML files and a README line on their purpose.
- Tests:
  - `tests/test_goal_layer.py` (new) covers SC1 install for claude, codex, both and `--dev`, the narrative test failing on a broken link and passing on a fixed one, and an SC2 grep guard over installed goal text.
  - `tests/test_modeling_command_contracts.py` gets SC5(f) pins and the sibling cross-references.

**fusion-tea (`goal-layer-mr7`, orchestrator-run; Appendix D)**

- **F1.**
  - MR-7 rewrite (A6).
  - `CLAUDE.md` "Goal layer in this repository" section (A7).
  - `MODELING_PROCESS.md`, the runbook and the three goal templates set to the shipped bytes.
  - `REQUIREMENTS.md` "Last Updated".
- **F2 (after the agentic-mbse merge).**
  - Pin move and provenance-test SHA.
  - Remove the local goal skills, links and whitelist lines; `AGENTS.md:5` says "Local study skills".
  - Remove the five tool-owned files, re-init and verify.

## Non-Goals

Everything in the spec's Non-Goals. In addition:

- No change to `Installer` policy. The fusion-tea switch works with the current policy (D13).
- No fix for the dev-mode ignore marker gap (Risks). It is filed as a follow-up.
- No rewrite of Equality intent and no edit to `plant-idiom.md`.
- No change to fusion-tea's goal data, narratives, ADR files, `application-policy.md` or `repair-goal-prompt.md`.

## Implementation Notes

- Keep fusion's line structure in ported files: unwrapped prose, one paragraph per line. A rewrapped paragraph turns one hunk into many and breaks SC12. Change only the lines Appendix B lists.
- Do not resolve the narrative test's own path (D9). Run it once inside a `--dev` target in tests or evidence.
- The runbook's design-choice citation names the resolver once, in § Grounding a goal (A8). Later mentions say "the design-choice pattern". § The decisions behind this gives the `get_docs_dir()` command for the decision record.
- `SLASH_REFERENCE` (`test_shipped_text.py:13`) accepts `/run-goal`, `/research` and `/manage-sources`. It rejects `/run-study` and `/research-acquire`.
- F1 copies bytes from this worktree's final tree. If the agentic-mbse PR changes after F1, F2's remove-then-init installs the merged bytes, and `git diff` shows the late change.
- Run fusion-tea tests from this worktree's environment with `--confcutdir=<copy>/tests/orchestration` (and `-o addopts=` if fusion's config names plugins missing here). That avoids loading fusion's root `tests/conftest.py` and touching fusion's venv.

## Potential Risks

- **The dev-mode ignore block is not extended on re-init.** `_update_gitignore_for_dev_mode` returns early when its marker exists (`cli/__init__.py:290-293`). An existing `--dev` target therefore shows the new goal-file links as untracked. Fresh `--dev` installs are correct (SC1). Mitigation: file a backlog item at close and note it in the Item 4 list.
- **The SC4 agent loads more than installed files.** User-level `~/.claude` rules and memory could reach a `claude -p` run. Mitigation: run with project-only setting sources or an isolated config dir, and record which in evidence. Also check its loaded-file list.
- **The resolver fails in the scratch target.** It has no project dependency on agentic-mbse. Mitigation: run the agent with this worktree's `.venv` active (`VIRTUAL_ENV`, `PATH`), as a real target's environment would provide, and record it.
- **Fusion's `repair-goal-prompt.md:18` points at stale text.** It says `MODELING_PROCESS.md` holds "MR-7 evidence and independent review obligations". After F2 that file holds the design-choice trigger and row, and MR-7 cites the pattern, so a reader still lands on the obligations. It is listed in the SC8 chain check and not edited.
- **Over budget.** Re-estimate:
  - spec about 3h, design 2h, plan 1h;
  - execute about 12.5h: rule 3h, goal files 4h, evidence 2.5h, fusion F1 and rehearsal 2h, dry run 1h;
  - total about 18.5h, about 2.3 days against the 2-day ceiling.

  The roughly 0.3–0.5 day overrun is accepted and recorded. Its causes: the Align record moved the MR-7 rewrite, the fusion branch and the rehearsal into this item (about 3h), and the review added the sibling, the runbook trigger row and the hunk diff (about 1.5h). The shed list applies to anything beyond that.

## Integration Strategy

- **Merge order (SC9).**
  1. The owner merges and pushes agentic-mbse `goal-layer-port` as M.
  2. F2 runs on `goal-layer-mr7` with M: either the orchestrator or the owner, following `evidence/fusion-tea-runbook.md`.
  3. The owner pushes and merges `goal-layer-mr7`.

  F1's commit message states "do not merge before the pin commit".
- **What fusion `main` sees in the meantime.** It keeps its local goal files and its pin `adbef75` until step 3, so a re-init there changes nothing. Every fusion destination exists on the branch before step 1.
- **Edits outside this item's own files, for Item 4's list:**
  - `MODELING_PROCESS.md.template` and `MODELING_GUIDE.md.template` index;
  - `docs/patterns/{README,constraints}.md`;
  - `sysml-conventions` (SKILL and stencils);
  - `requirements-tracking`, `review-model`, `model-validation`, `orchestrate-modeling`.

## Validation Approach

| SC | Check | Who |
|---|---|---|
| SC1 | `install-commands --list`; `tests/test_goal_layer.py` (claude/codex/both/`--dev`); command output captured | implement |
| SC2, SC3 | grep over a fresh install's goal text; path existence; `tests/test_shipped_text.py` green | implement |
| SC4 | dry run (Appendix D3): produced `goal.md`, `trail.md`, brief, read-file list | orchestrator |
| SC5 | (a)(g) read and grep; (b)(c)(f) contract pins plus one reverted-edit failure captured; (d) trace table (Appendix E) verified against files; (e) skill diff; (h) diff of `constraints.md` and `sysml-conventions` | implement |
| SC6 | crosswalk of MR-7 `:89-107`, fusion process `:17,:34`, goal hooks → shipped location or fusion home with reason; grades; fresh reviewer's check of the rule against MR-7 | implement; fresh review orchestrator-dispatched |
| SC7, SC8 | branch diff; rehearsal outputs (Appendix D2) | orchestrator |
| SC9 | ledger Item 2 section (Appendix C rows plus merge order) | implement |
| SC10 | decision record entries vs fusion ADR frontmatter | implement |
| SC11 | `uv run pytest tests/`, `ruff check src/ tests/`, `mypy src/` | implement |
| SC12 | `diff -u` of each shipped file vs its fusion original, every hunk classed (D17) | implement |

## Next-Stage Handoff

- **Fixed:**
  - D1–D17;
  - the exact texts in Appendix A;
  - the template, test and decision-record paths;
  - the fusion commit split and merge order.
- **Open for the plan:**
  - exact generalized wording of Appendix B lines marked "gist";
  - decision-record entry prose (table form if shed);
  - the dry-run brief's wording;
  - fixture numbers.
- **De-risk first:**
  - Run the narrative test under `--dev` (D9).
  - Have the fresh reviewer check A1 against MR-7 before F1 copies template bytes.
- **Phasing:**
  - P1 rule placement.
  - P2 goal-layer files, CLI and tests.
  - P3 evidence and ledger, with the reviewer dispatched after P1.
  - P4 fusion F1 and rehearsal (orchestrator).
  - P5 dry run (orchestrator).
  - P6 runbook for F2.

  P1–P3 and P6 fit fresh implement sessions. P4 and P5 need fusion-tea, a scratch target or a live `claude -p`, so they are orchestrator-run.

---

## Appendix A — Exact texts

### A1. `docs/patterns/design-choices.md`

```markdown
# Design Choices: Evaluate the Supplied Design

A model evaluates the design it is given. Choosing that design (which equipment is installed, how much inventory, what capacity) is a separate decision. This document is the rule for keeping the two apart, and the evidence that shows they were kept apart.

## When to Use This Document

Read it before designing, changing or reviewing:
- which quantities a model or analysis takes as chosen inputs and which it calculates
- a binding that sets installed equipment, inventory or capacity
- a sizing, selection or search policy
- an operating-point closure
- a cost that scales with demand

## Core Principle

Physical relationships and performance limits evaluate a design. A policy that chooses a design is something else, and the two stay separate. A calculation or binding must not silently remove a design choice by setting installed equipment, inventory or capacity from required performance. Once a model sizes a component from demand, it has decided which design parameters are free and which are derived, and every use of the model inherits that decision without having made it.

## The Rule

1. **Evaluate the supplied design.** Keep physical demand, installed design or capacity, and any suggested design separate. When the supplied design is insufficient, report the shortfall; do not enlarge the design automatically.
2. **Keep selection policies separate and visible.** An explicitly authorized sizing or search analysis may propose a design. Its policy stays separately identifiable, and the design it selects can be evaluated without rerunning the policy. Implementation convenience does not authorize hiding a design-selection rule inside a physical component.
3. **State what each analysis specifies and what it solves for.** Each analysis's contract says which quantities it takes as given and which it calculates, with the authority for each. An existing calculation direction, a reference design or a quality target is not authority to fix that choice for every use of the component.
4. **Document calculation direction.** A numerical routine may have directional inputs and outputs. Document how its direction relates to the supported analysis and to the design choices available. This rule does not require an acausal solver, and it does not require every related quantity to be specifiable at once.
5. **Balances and identities are not automatically violations.** Ordinary physical balances, geometry identities and operating-point calculations state the independent quantities they selected and their assumptions. A calculated requirement is not evidence of installed capacity, and it is not permission to bind installed capacity to it.
6. **Report validity separately from adequacy.** An evaluation outside a performance model's supported domain is a limitation of that model. It is neither a failed physical constraint nor permission to extrapolate silently. An invalid or unsupported evaluation is never reported as a pass.
7. **Inventory and cost follow the selected design.** A supplied equipment choice stays the basis of its represented inventory and cost. A cost that scales with demand says which demand-matched equipment it assumes and that installed capacity was not evaluated; it is not presented as a fully evaluated chosen design.

The rule applies to direct edits and to patterns inherited from existing code, not only to new work. Existing code, agreement with a reference, and passing scores do not waive it. Skipping or combining stages does not waive its evidence or its review.

## What to Record

In the existing spec, design or goal record, list the affected quantities, units, physical relationships, current and proposed roles (chosen, calculated, requirement, installed capacity, policy-selected), the binding location, and the authority for any role change. A small change can use a short paragraph; several changed choices need a table. Call out any parameter that leaves the public interface or becomes a calculated binding. Defaults, mode switches and multipliers must not conceal automatic adequacy.

- The spec names the design choices the consumer must keep.
- The design records the affected roles, physical relationships, selection policies, authority and actual binding paths.
- The implementation keeps those choices through generated and native execution and through downstream costs.
- The handoff carries this evidence. A repair is not complete on scores or baseline reproduction alone.

## Review

A changed design-variable role, a new or changed automatic sizing or selection policy, or installed capacity, equipment or inventory bound to computed demand triggers focused independent design review (“Process Selection” in `modeling_project/MODELING_PROCESS.md`). The review inspects the actual equations and bindings, including downstream part attributes and cost consumers. It checks the bindings themselves, not names such as `required`, `selected` or `sizing_mode`.

## Acceptance

For each repaired or introduced capacity or fit relationship, use the supported execution route to exercise an insufficient and a sufficient supplied design within the performance model's domain. Check that the selected design is unchanged, the constraint result changes meaningfully, and inventory and cost follow the selected design. Where the intended interface lets demand vary while hardware is held fixed, test that separately. An unsupported-domain case stays explicitly unsupported, with no manufactured success. For an operating-point closure or a cost proxy where these tests do not apply, record why and check its stated assumptions instead.

A review records compliance for the affected scope as compliant, violated or unverified, with evidence. Unknown compliance does not count as completed remediation.

## Examples

| Authored | Reading |
|---|---|
| `capacity = required_flow * margin`, bound as installed capacity | An automatic design-selection rule, even when `margin` is exposed |
| `required_area` compared with an independently selected installed area | Preserves the distinction; the comparison reports fit |
| `volume = area * length` | A geometry identity, not an automatic adequacy rule |
| A calculated required flow | Not evidence of installed pump capacity |
| A calculated required exchanger area | Not permission to bind it to installed exchanger area |

## Common Mistakes

**Replacing one hidden fixed choice with another.** Swapping one margin for another, or for a sizing mode that is on by default, leaves the design selected inside the model. Make the installed value a supplied input and report the shortfall.

**Reading compliance off names.** An attribute called `selected` can still be bound to demand. Inspect the binding.

## Related Patterns

- [constraints.md](constraints.md), “When should you write an equality at all?” (equality intent) — the constraint-side sibling. An exact equality over a parameter meant to vary deletes a degree of freedom; a binding that sets installed capacity from demand deletes a design choice. Both keep the design space open.
- [plant-idiom.md](plant-idiom.md), “Binding a modelled value into a calculation” — how to write a binding once its role is decided.
- `modeling_project/MODELING_PROCESS.md`, “Process Selection” and “Technical Patterns” — where this rule is triggered and read.

## Authority

`[AGENT] (ratified by owner, 2026-09-20)` — the need is owner-stated (2026-09-20): “As soon as you start introducing ‘sizing’, then you are basically pre-defining which design parameters are ‘free’ and which are ‘derived’. this is explicitly what we wanted to avoid.” The obligations above are agent-written applications of that principle, ratified when the owner asked for their enforcement. Generalizing them for every project and placing them in this pattern set is agent work at the owner's direction (2026-10-11); the sentence-level derivation is in the agentic-mbse change that added this document (`git log -- docs/patterns/design-choices.md`). This document is the one statement of the rule. A project requirement that applies it cites this document and states only the project's own application.
```

### A2. `MODELING_PROCESS.md.template`

"Process Selection", new row after `:23`:

| Changed design-variable role (a quantity moves between chosen and calculated, or a design choice leaves the public interface), new or changed automatic sizing or selection policy, or installed capacity, equipment, or inventory bound to computed demand | Focused independent design review before dependent implementation. Inspect the actual equations, bindings, and downstream consumers, including costs, against the design-choice pattern (`design-choices.md`; see Technical Patterns). |

"Architecture & Design", new bullet after the "Own quantities and responsibilities" bullet:

- **Keep design selection separate from evaluation.** Physical relationships evaluate the design supplied to them; a calculation or binding does not choose installed equipment, inventory, or capacity from required performance. Apply `design-choices.md` (Technical Patterns below).

"Technical Patterns", new last row:

| Design variables, equipment or capacity bindings, sizing, operating-point closure, or demand-based costs | Evaluate the supplied design and report insufficiency; do not set installed equipment, inventory, or capacity from required performance. State which quantities each analysis specifies and which it solves for, with their authority. | `design-choices.md` |

`:71`: `A self-named \`in volume = volume\` binds to itself.` → `` `in volume = volume;` ``.

### A3. Sibling cross-references

- `docs/patterns/constraints.md`, new line after `:69`: `**Related:** the binding-side sibling is [design-choices.md](design-choices.md). An exact equality over a parameter you meant to vary deletes a degree of freedom; a binding that sets installed capacity from demand deletes a design choice. Both keep the design space open.`
- `skills/sysml-conventions/SKILL.md`, new line after `:211`: `Its binding-side sibling is agentic-mbse \`docs/patterns/design-choices.md\`: a calculation or binding that sets installed capacity from demand deletes a design choice in the same way.`

### A4. `requirements-tracking`

- `:24`: "Modeling requirements exist at two tiers: tool-owned baseline rules that apply to all projects (`MODELING_GUIDE.md`, `MODELING_PROCESS.md`, and the toolkit pattern references they name), and user-owned extensions (`REQUIREMENTS.md`) that capture project-specific rules. A project rule that applies a baseline rule cites it and states only the project's application." The sentence on per-feature MR-XXX stays.
- `:38` Baseline row: File `modeling_project/MODELING_GUIDE.md`, `modeling_project/MODELING_PROCESS.md`, toolkit `docs/patterns/`; Contains "Universal modeling and process rules, such as design-choice preservation (`design-choices.md`)".
- `:41`: "**What belongs in the baseline**: Rules correct for all projects. Examples: \"calc defs go in library/, not in designs/\"; \"a binding does not set installed capacity from demand\"."
- `:43` gains: "A project's application of a baseline rule also belongs here, citing the baseline rule rather than restating it."
- Anti-pattern table, new row: `| Restating a baseline rule in REQUIREMENTS.md | Cite the baseline rule; record only the project's application |`.

### A5. Stage pointers

- `review-model`, new question after `:28`: "- Do calculations and bindings evaluate the supplied design rather than choose it? Where design-variable roles, capacity bindings, sizing, or demand-based costs change, check the actual bindings against `design-choices.md` (technical-pattern table in `modeling_project/MODELING_PROCESS.md`)."
- `model-validation`, new bullet after `:52`: "- Design choices: where design-variable roles, capacity bindings, sizing, or demand-based costs changed, select the acceptance checks in `design-choices.md` (technical-pattern table in `modeling_project/MODELING_PROCESS.md`)."

### A6. fusion-tea MR-7 (`modeling_project/REQUIREMENTS.md:87-107`)

```markdown
### MR-7: Preserve Design Choices; Separate Evaluation from Design Selection

**Authority:** <line 89, unchanged>

This project applies agentic-mbse's design-choice pattern without restating it: `design-choices.md` in the installed toolkit's pattern directory (`uv run python -c 'from agentic_mbse.cli import get_docs_dir; print(get_docs_dir() / "patterns")'`; `modeling_project/MODELING_GUIDE.md` § Pattern Documentation Index). The pattern states the rule, the evidence to record, the review it triggers (`modeling_project/MODELING_PROCESS.md` § Process Selection) and the acceptance tests. MR-7 records only this project's application:

- **Invariant.** Goal grounding and each affected strategy and task carry MR-7 as an invariant (`work/orchestration/GOAL_RUNBOOK.md` § Grounding a goal).
- **Conductor models.** An unsupported conductor field or temperature is a conductor-performance-model limitation. It is neither a failed physical constraint nor permission to extrapolate silently.
- **Depth work.** A depth target or a prior passing depth grade is not authority to fix a design choice and does not waive the review. Prospective depth assessments also follow `.project/active/demo-depth-rubric/application-policy.md`; historical rubric bytes and grades remain unchanged.
```

`:165` becomes `**Last Updated**: <F1 date> (MR-7 cites the shipped design-choice pattern)`.

### A7. fusion-tea `CLAUDE.md`, new section after "Design-choice preservation"

```markdown
## Goal layer in this repository

`run-goal`, `narrate-goal`, `work/orchestration/GOAL_RUNBOOK.md` and its templates are installed by agentic-mbse and name the research, integration and study procedures generally. Here they are:

- **Research:** `/research-acquire` (`.claude/commands/research-acquire.md`) drives search and triage. Form request files at `knowledge/research/requests/REQ-*.json`; `scripts/research_seam.py` keeps run bookkeeping and `scripts/source_registry.py register` ingests. Protocol: `docs/research_seam_operator_guide.md`. Every researcher applies the clean-room screen (`knowledge/holdout/aries-cs/PROTOCOL.md`) before any fetch.
- **Integration:** `scripts/integrate.py` (`.project/adr/0009-integration-is-a-fixed-point-proof.md`); guide `docs/integration_seam_operator_guide.md`.
- **Studies:** `.claude/skills/run-study/runbook.md` and `modeling_project/STUDY_POLICY.md`. Discovery logs are `exploration/<pkg>/studies/DISCOVERY_LOG.md`; `tests/study/test_records.py::test_findings_join_the_discovery_log` checks the join.
- **Decision records:** this repository's goal-layer ADRs stay in `.project/adr/` and govern it; installed targets use agentic-mbse's dated snapshot.
- **Launcher:** in the Codex test worktree use `.codex-test/run` (`AGENTS.md`); otherwise `uv run`.
```

### A8. Goal-layer hooks (design-choice hook class)

- Runbook `:84`: "For a model-changing goal, read `modeling_project/REQUIREMENTS.md` and the design-choice pattern, and carry applicable requirements into its invariants. The design-choice pattern — `design-choices.md` in the installed toolkit's pattern directory, located as `modeling_project/MODELING_GUIDE.md` § Pattern Documentation Index shows — governs design-variable roles, automatic equipment selection and demand-versus-installed-capacity meaning." The remaining two sentences are unchanged.
- Runbook `:100`: "record its MR-7 justification" → "record its justification under the design-choice pattern"; "Depth-target attainment" → "Score or quality-target attainment"; "the MR-7 assessment" → "the design-choice assessment". The depth-rubric sentence is deleted (ledger).
- Runbook `:139`: "For tasks affecting MR-7, include the requirement" → "For tasks affecting design choices, include the applicable requirements, the design-choice pattern"; "passing baseline or rubric score" → "passing baseline or score". The rest is unchanged.
- Runbook trigger table, new row after `:73`: `| Changed design-variable role, new or changed automatic sizing or selection policy, or installed capacity, equipment, or inventory bound to computed demand | Focused independent design review of the actual equations, bindings, and downstream consumers against the design-choice pattern, before dependent implementation |`
- `goal.md:29`: "- **Modeling requirements:** applicable entries from `modeling_project/REQUIREMENTS.md`, and the design-choice pattern (`design-choices.md`; `GOAL_RUNBOOK.md` § Grounding a goal says where it is). Identify the design choices this goal preserves or investigates and any explicitly authorized design-selection policy; do not inherit a variable's role merely because the current implementation uses it."
- `run-goal:53`: "Read `modeling_project/REQUIREMENTS.md` and the design-choice pattern (`GOAL_RUNBOOK.md` § Grounding a goal says where it is) before grounding or dispatching a model-changing goal. Follow the design-choice steps in `GOAL_RUNBOOK.md` and `MODELING_PROCESS.md`; carry the applicable requirements and intended design choices into worker/reviewer briefs. Automatic sizing and changes to which quantities are chosen or calculated require explicit design reasoning and applicable review, even when pursuing an already approved quality target."

## Appendix B — Other line changes in ported files (class; wording gist unless quoted)

| File:line (fusion) | Change | Class |
|---|---|---|
| run-goal frontmatter, `:1-14` | list-form `allowed-tools`, `metadata.kind: workflow`, shared preface | envelope |
| run-goal `:20`, `:73` | `.project/adr/` → the goal-layer decision record (`GOAL_RUNBOOK.md` § The decisions behind this) | decision record |
| run-goal `:49` | drop "In Codex, read `.agentic-mbse/codex.md` … and `.project/codex-test-setup.md` …" (the preface covers the adapter) | envelope / deletion |
| run-goal `:55` | "`.claude/commands/<stage>.md` … `.agents/skills/<stage>/SKILL.md` in Codex" → "the stage's installed skill"; "(`.codex-test/run` in this test worktree; otherwise `uv run`)" → "(`uv run` unless the project names another)" | consumer path |
| run-goal `:61` | "Use `docs/research_seam_operator_guide.md` …" → "Use the research procedure the target installs; where none is installed, `/research` and `/manage-sources`." | consumer path (interim) |
| run-goal `:63` | request files, `research-acquire.md`, scripts and the clean-room screen → "When external sources are needed, execute the research procedure directly or delegate independent requests to fresh agents (…runtime tool names kept…). A delegated brief names …; deposit it at `evidence/`. Apply any source-quarantine rule the project states before any fetch." | consumer path (interim) |
| narrate-goal frontmatter | as run-goal | envelope |
| narrate-goal `:77` | `tests/orchestration/test_goal_contract.py` → `tests/orchestration/test_narrative_links.py` | consumer path |
| runbook `:7` | "is in `.project/adr/` — seven records" → "is in the goal-layer decision record — seven records" | decision record |
| runbook `:13` | "the coding PM in `.project/`, the modeling PM in `work/`, the research pipeline, the study runbook" → "the modeling PM in `work/`, a second PM where the target runs one (for example a coding PM in `.project/`), the research procedure, and the study procedure where one is installed" | consumer path (two-PM) |
| runbook `:31` | surface row `.project/adr/` → "the goal-layer decision record (§ The decisions behind this)", who: "agentic-mbse, as a dated record" | decision record |
| runbook `:41` | concept path → "goal-layer decision record, Sources" | decision record |
| runbook `:70-76`, `:84`, `:100`, `:139` | A8 | design-choice hook |
| runbook `:94` | probe-record path → "goal-layer decision record, ADR-0003 (2026-08-27 amendment)" | decision record |
| runbook `:106` | study runbook and policy paths → "The study layer owns the term and its identity rules, where a target installs one." | consumer path |
| runbook `:205` | add, after the close-rule sentence: "The owner's close is recorded as `## Goal close — YYYY-MM-DD` at the end of `trail.md`, with the ruling and the disposition." | recorded practice |
| runbook `:232` | "committed record directory … `snapshot.json`" → "the committed study record that carries the store's identity"; "R2-synced research binary … extracted markdown" → "an externally stored research binary … its tracked extracted text" | consumer path |
| runbook `:260`, `:270` | `exploration/<pkg>/studies/DISCOVERY_LOG.md` → "the study layer's discovery log"; the join test → "the study layer's join check" | consumer path |
| runbook `:276` | run-study runbook and STUDY_POLICY → "the study layer's runbook and its policy, where a target installs one" | consumer path |
| runbook `:286-289` | "Every seam is native now." → "Each seam is the procedure the target installs." The research and integrate bullets become one sentence each naming the target's procedure (research per D10). Fusion history (GSTH, WI-033, ADR-0009, scripts, guides) is deleted. | consumer path / deletion |
| runbook `:299-305` | link targets `../../.project/adr/…` → plain `ADR-000N` ids. The section intro gives `uv run python -c 'from agentic_mbse.cli import get_docs_dir; print(get_docs_dir())'` and `goal-layer-decisions.md` | decision record |
| trail template, end | `## Goal close — YYYY-MM-DD` section: **Ruling** (owner, quoted or cited) and **Disposition** (closed on § Answered when, or closed by redirect, and why) | recorded practice |
| goal template `:29` | A8 | design-choice hook |

## Appendix C — Ledger rows (Item 2 section)

| Text left out | Was in (fusion-tea) | Fusion-tea home |
|---|---|---|
| Goal-layer ADRs as the "why" | run-goal `:20,:73`; runbook `:7,:31,:299-305` | `.project/adr/` unchanged; A7 "Decision records" (F1) |
| Codex test worktree setup | run-goal `:49,:55` | `AGENTS.md:7,:11` (exists); A7 "Launcher" (F1) |
| MR-7 hooks | run-goal `:53`; runbook `:84,:100,:139`; `goal.md:29` | MR-7 (A6, F1); generalized hooks ship |
| Research seam guide, request files, scripts, `research-acquire`, clean-room screen | run-goal `:61,:63`; runbook `:288` | A7 "Research" (F1); `CLAUDE.md` ⛔ holdout line (exists) |
| Integration seam, `integrate.py`, ADR-0009, guide, history | runbook `:289` | A7 "Integration" (F1); ADR-0009 (exists) |
| Study runbook and policy, discovery-log path, join test | runbook `:106,:260,:270,:276` | A7 "Studies" (F1); run-study runbook `:285-287` (exists) |
| Study-store and R2 citation specifics | runbook `:232` | `CLAUDE.md` "Research Artifact Sync (R2)" (exists); run-study runbook (exists) |
| Coding PM in `.project/` as a premise | runbook `:13` | `CLAUDE.md` "Project Management — Two Systems" (exists) |
| Concept and probe-record paths | runbook `:41,:94` | fusion files (exist); cited as provenance in the decision record |
| Depth-rubric policy pointer | runbook `:100`; process `:34` | MR-7 "Depth work" (A6, F1) |
| The two MR-7 process paragraphs | `MODELING_PROCESS.md:17,:34` | Shipped row, rule and trigger; MR-7 cites them (F1). Crosswalk in SC6 |
| `.agentic-mbse/patterns/` location line | `MODELING_PROCESS.md:70` | None needed: the owner dropped the pattern note (`8a35c4d0f`); the shipped resolver text applies |
| Binding-row semicolon | `MODELING_PROCESS.md:75` | Upstreamed (A2) |
| MR-7 general application, evidence, enforcement, acceptance and examples | `REQUIREMENTS.md:91-107` | Shipped `design-choices.md`; MR-7 cites it (A6) |
| Narrative check path | narrate-goal `:77` | fusion's own `tests/orchestration/test_goal_contract.py` stays |
| Local `run-goal`, `narrate-goal`, their `.agents/skills/` links, `.gitignore:25,:27`, `AGENTS.md:5` "goal and study" | fusion `.claude/skills/`, `.agents/skills/` | Replaced by the installed bundles in F2 |

Merge order: as in Integration Strategy.

## Appendix D — fusion-tea work (orchestrator-run)

**D1. F1 on `goal-layer-mr7`** (after P1–P2 are final and the fresh review has passed):

1. Apply A6 to `modeling_project/REQUIREMENTS.md` and A7 to `CLAUDE.md`.
2. Copy this worktree's `project_templates/MODELING_PROCESS.md.template` over `modeling_project/MODELING_PROCESS.md`.
3. Copy `GOAL_RUNBOOK.md.template` and the three goal templates over `work/orchestration/GOAL_RUNBOOK.md` and `goal-templates/`.
4. Check that the `CLAUDE.md:5` and `application-policy.md:3` anchors still match the MR-7 heading.
5. Commit with the message "do not merge before the pin commit".
6. Capture `git diff 2b1e9f9d5..HEAD` into `evidence/fusion-tea/branch-diff-F1.txt`.

**D2. Rehearsal (SC8)** on a detached worktree of the F1 tip in scratch space:

1. Simulate F2 without the pin:
   - `git rm -r` the local `.claude/skills/{run-goal,narrate-goal}` and the `.agents/skills/` links;
   - drop `.gitignore:25,:27`;
   - edit `AGENTS.md:5`;
   - `rm` the five tool-owned files.
2. `uv run --project /home/reid/1cfe/agentic-mbse-goal-layer agentic-mbse init <copy> < /dev/null`.
3. Capture:
   - the init output (expect no "Preserving" line for goal or process files);
   - `git status --short`;
   - manifest entries vs `sha256sum` of the runbook, the three goal templates, the narrative test and `MODELING_PROCESS.md`;
   - `git status -- work/orchestration/goals work/narratives` (expect empty);
   - pytest over `<copy>/tests/orchestration` with `--confcutdir` (Implementation Notes). Both tests should pass over the 12 narratives;
   - a grep showing the cited runbook headings exist;
   - the SC8 chain walk, each link with its resolved file.

   Outputs go to `evidence/fusion-tea/rehearsal/`.

**D3. Dry run (SC4)** in `/tmp/goal-dry-run-<stamp>/target`, outside any repo:

1. `init --assistant claude`, then copy `tests/fixtures/goal_dry_run/` models into `models/`. `git init` and commit, so grounding can cite `@sha`.
2. Run `claude -p` in the target with:
   - this worktree's `.venv` active;
   - project-only settings;
   - stream-json output.
3. The brief names the goal question, for example "Does the supplied drain pump keep the sump basin from overflowing at the design inflow?", and the consumer. It gives the operator's answers in advance:
   - the slug `sump-overflow` is confirmed;
   - the operator agrees to `grounded` when proposed;
   - stop after writing `### T-001 start`.
4. Capture into `evidence/dry-run/`: `goal.md`, `trail.md`, the brief, and the read-file list extracted from the transcript.

**D4. F2 runbook** (`evidence/fusion-tea-runbook.md`, written in P6, run after the merge). Item 1's step 1 applies with the merged SHA:

1. Move the pin: `rev`, `uv.lock` by hand, `uv sync --frozen --extra e2e`, and `uv pip install --no-deps syside-license==0.3.6` (plus any package the sync removed).
2. Update the SHA in `tests/test_dependency_provenance.py`.
3. Do D2 step 1 for real.
4. `uv run --no-sync agentic-mbse init . < /dev/null`.
5. Verify as in D2.
6. Commit. The owner pushes and merges.

## Appendix E — Reach trace (SC5(d)); every hop is a named section or file

| From | Hop 1 | Hop 2 |
|---|---|---|
| `spec-model` | `:15` "Process Selection" (new row) | `design-choices.md` |
| `design-model` | `:21` "Architecture & Design" bullet or technical-pattern row | `design-choices.md` |
| `implement-model` | `:25` technical-pattern row | `design-choices.md` |
| `quick-model` | `:21` technical-pattern row | `design-choices.md` |
| `review-model` | new question (A5) | `design-choices.md` |
| `audit-models` | `:29` pattern rules → technical-pattern row | `design-choices.md` |
| `model-validation` | new bullet (A5) | `design-choices.md` |
| `sysml-conventions` | cross-reference line (A3) | `design-choices.md` |
| `orchestrate-modeling` | `:39` "Process Selection" (new row) | `design-choices.md` |
| goal template | invariant bullet (A8) | `design-choices.md` |
| goal runbook | § Grounding a goal hook; trigger-table row | `design-choices.md` |
| `run-goal` | Model changes paragraph (A8) | `design-choices.md` |

---

Next Step: after approval → `/_my_design_review` in a fresh session, then `/_my_plan`.
