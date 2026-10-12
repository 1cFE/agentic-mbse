# SC6 Crosswalk: MR-7 and its hooks → the shipped design-choice pattern

**Item:** goal-layer-port (`WRAP-SPLIT` Item 2), Phase 2. **Written:** 2026-10-11, in the commit that adds `docs/patterns/design-choices.md` (design D6).

This is the derivation record for the design-choice rule. It maps every sentence of fusion-tea's MR-7, the two fusion-tea process paragraphs that applied it, and the goal-layer hooks to where each now lives: a shipped agentic-mbse location, or a fusion-tea home with a one-line reason the sentence is fusion-only. Every row carries its source grade, so the shipped obligations keep their provenance (capture-fidelity law 1).

**Sources.** All read from the snapshot `.orchestrate-logs/fusion-tea-snapshot/` (fusion-tea `2b1e9f9d5`):

- MR-7: `modeling_project/REQUIREMENTS.md:89-107`.
- Process paragraphs: `modeling_project/MODELING_PROCESS.md:17`, `:34`.
- Goal hooks: `.claude/skills/run-goal/SKILL.md:53`, `:55`; `work/orchestration/GOAL_RUNBOOK.md:84`, `:100`, `:139`; `work/orchestration/goal-templates/goal.md:29`.

**Grades used below.**

- **OWNER-VERBATIM** — the principle, quoted in MR-7's authority line (`:89`), 2026-09-20.
- **OWNER** — the owner's request to implement enforcement across goal and modeling agents (`:89`), 2026-09-20.
- **AGENT, ratified** — agent-written application and enforcement text, ratified by that implementation request. MR-7 says so itself (`:89`), and fusion `.project/active/modeling-intent-enforcement/spec.md:7` grades the process and goal-hook edits the same way.
- The generalization into agentic-mbse (removing fusion terms, choosing the levels) is `[AGENT]` 2026-10-11, at the owner's direction ("it is important that you find the right level for this rule"). It adds no owner-originated content. The pattern's closing grade paragraph says this in a target.

**Shipped locations.** "Pattern" is `docs/patterns/design-choices.md`. "Process template" is `project_templates/MODELING_PROCESS.md.template`. Goal-layer destinations are the Appendix A8 texts, which Phase 3 ports; Phase 7 checks those rows against the ported files.

## MR-7 (`REQUIREMENTS.md:89-107`)

The heading (`:87`) and the labels "**Application:**", "**Required evidence…**", "**Enforcement:**", "**Acceptance:**" and "**Examples:**" are not sentences. MR-7's heading and authority line stay in fusion-tea unchanged (A6).

| Source sentence | Shipped location, or fusion-tea home and reason | Source grade | Note |
|---|---|---|---|
| `:89` “As soon as you start introducing ‘sizing’, then you are basically pre-defining which design parameters are ‘free’ and which are ‘derived’. this is explicitly what we wanted to avoid.” | Pattern § closing grade paragraph (quoted as the *need*); restated in general terms in Pattern § Core Principle, last sentence. MR-7 `:89` keeps it (A6). | OWNER-VERBATIM | Only this sentence is presented as owner-originated in the pattern. |
| `:89` "[OWNER] Requested implementation of enforcement across goal and modeling agents." | Pattern § closing grade paragraph ("ratified when the owner asked for their enforcement"). MR-7 `:89` keeps it. | OWNER | |
| `:89` "The application and enforcement below are [AGENT] interpretations ratified by that implementation request, not additional owner-originated requirements." | Pattern § closing grade paragraph ("The obligations are agent-written applications of that principle…"). MR-7 `:89` keeps it. | AGENT, ratified | A grade statement; carried as the pattern's grade. |
| `:89` "Source: `.project/active/modeling-intent-enforcement/spec.md`." | fusion-tea: MR-7 `:89`, unchanged. Fusion-only: a fusion path, which cannot resolve in a target (D6). | AGENT, ratified | |
| `:91` "The model MUST distinguish physical relationships and performance limits from policies that choose a design." | Pattern § Core Principle, sentences 1–2; imperative force in § The Rule, rules 1–2. | AGENT, ratified | Kept (design review round 1, SC6 check). |
| `:91` "A calculation or binding MUST NOT silently remove a design choice by setting installed equipment, inventory or capacity from required performance." | Pattern § Core Principle, sentence 3 (verbatim, "must not"). One-line summary: Process template § Technical Patterns, design-choice row. | AGENT, ratified | |
| `:91` "Which quantities a particular analysis specifies and which it solves for MUST be explicit in that analysis's contract, with their authority recorded." | Pattern § The Rule, rule 3 ("must say"). Summary: Process template § Technical Patterns row. | AGENT, ratified | Force restored by M3 (round 1). |
| `:91` "An existing calculation direction, reference design or depth target is not authority to fix that choice for every use of the component." | Pattern § The Rule, rule 3, sentence 2. | AGENT, ratified | "depth target" → "quality target". fusion's depth application: MR-7 "Depth work" (A6). |
| `:95` "Keep physical demand, installed design/capacity and any suggested design separate." | Pattern § The Rule, rule 1, sentence 1. | AGENT, ratified | |
| `:95` "Evaluate the supplied design; report insufficient capacity or fit instead of automatically enlarging it." | Pattern § The Rule, rule 1 (title and sentence 2). Summary: Process template § Technical Patterns row. | AGENT, ratified | |
| `:95` "An explicitly authorized sizing/search study may propose choices, but its policy must be separately identifiable and its selected design evaluable without rerunning that policy." | Pattern § The Rule, rule 2, sentences 1–2. | AGENT, ratified | "must stay"; "must be evaluable" (M3). |
| `:96` "A numerical routine may have directional inputs and outputs." | Pattern § The Rule, rule 4, sentence 1. | AGENT, ratified | |
| `:96` "Document how that direction relates to the supported analysis and the available design choices; implementation convenience does not authorize hiding a design-selection rule inside a physical component." | Pattern § The Rule, rule 4, sentence 2 (first clause); rule 2, sentence 3 (second clause). | AGENT, ratified | |
| `:96` "This requirement does not prescribe an acausal solver or make every mathematically related quantity independently specifiable at once." | Pattern § The Rule, rule 4, sentence 3. | AGENT, ratified | |
| `:97` "Ordinary physical balances, geometry identities and operating-point calculations are not automatically violations." | Pattern § The Rule, rule 5 (title). | AGENT, ratified | "automatically" kept. |
| `:97` "Explain their selected independent quantities and assumptions." | Pattern § The Rule, rule 5, sentence 1 ("must state"). | AGENT, ratified | Force restored by M3. |
| `:97` "In particular, calculating required flow is not evidence of installed pump capacity, and calculating required area is not permission to bind it to installed exchanger area." | Pattern § The Rule, rule 5, sentence 2 (general form); § Examples, rows 4–5 (both examples). | AGENT, ratified | |
| `:98` "Report empirical validity separately from physical adequacy." | Pattern § The Rule, rule 6 (title). | AGENT, ratified | |
| `:98` "An unsupported conductor field or temperature is a conductor-performance-model limitation." | fusion-tea: MR-7 "Conductor models" (A6), citing rule 6. Fusion-only: the conductor-performance model is fusion's domain (D15). The general clause ships as rule 6, sentence 1. | AGENT, ratified | |
| `:98` "It is neither a failed physical constraint nor permission to extrapolate silently." | Pattern § The Rule, rule 6, sentence 2. | AGENT, ratified | |
| `:98` "Invalid/unsupported evaluation must not be reported as a pass." | Pattern § The Rule, rule 6, sentence 3 ("is never reported as a pass"). | AGENT, ratified | |
| `:99` "A supplied equipment choice must remain the basis of its represented inventory and cost." | Pattern § The Rule, rule 7, sentence 1 ("must remain"). | AGENT, ratified | Carried item 1, after round 2. |
| `:99` "A demand-scaled cost proxy must disclose the assumed demand-matched equipment and missing installed-capacity evaluation; it must not be presented as a fully evaluated chosen design." | Pattern § The Rule, rule 7, sentences 2–3. | AGENT, ratified | Scope kept to cost proxies (M3). |
| `:101` "In the existing spec/design or goal record, list the affected quantities, units, physical relationships, current/proposed roles (chosen, calculated, requirement, installed capacity, policy-selected), the binding location, and authority for any role change." | Pattern § What to Record, sentence 1. | AGENT, ratified | |
| `:101` "A small change can use a short paragraph; multiple changed choices need a table." | Pattern § What to Record, sentence 2. | AGENT, ratified | |
| `:101` "A parameter disappearing from the public interface or becoming a calculated binding must be called out explicitly." | Pattern § What to Record, sentence 3 (imperative "Call out"). | AGENT, ratified | |
| `:101` "Defaults, mode switches and multipliers must not conceal automatic adequacy." | Pattern § What to Record, sentence 4 (verbatim). | AGENT, ratified | |
| `:103` "Goal grounding and each affected strategy/task carry MR-7 as an invariant." | Goal procedure: `project_templates/GOAL_RUNBOOK.md.template` § Grounding a goal (A8 `:84` hook) and `project_templates/goal.md.template` "Modeling requirements" bullet (A8 `goal.md:29`). fusion-tea: MR-7 "Invariant" (A6). | AGENT, ratified | Procedure that cites the rule, not a second statement (SC5(a)). |
| `:103` "Model design review inspects the actual equations and bindings, including downstream part attributes and cost consumers." | Pattern § Review, sentence 2. Process template § Process Selection, design-choice row, response column. | AGENT, ratified | |
| `:103` "A changed design-variable assignment or automatic selection policy triggers the independent design review required by `MODELING_PROCESS.md`." | Process template § Process Selection, design-choice row: the trigger's one home (D2). Pattern § Review, sentence 1, points at it. Goal-layer mirror: `GOAL_RUNBOOK.md.template` § Review scope and evidence reuse, trigger row (A8). | AGENT, ratified | Scope is MR-7's (spec L3-3), plus "installed capacity, equipment, or inventory bound to computed demand". |
| `:103` "Existing code and prior passing depth grades do not waive this check." | Pattern § The Rule, closing paragraph, sentence 2 ("Existing code, agreement with a reference, and passing scores do not waive it"). fusion-tea: MR-7 "Depth work" (A6) for depth grades. | AGENT, ratified | "depth grades" → "passing scores"; the depth application is fusion-only (fusion's rubric). |
| `:105` "For each repaired or introduced capacity/fit relationship, use the supported execution route to exercise an insufficient and a sufficient supplied design within the performance model's domain." | Pattern § Acceptance, sentence 1. | AGENT, ratified | |
| `:105` "Verify that the selected design is unchanged, the constraint changes meaningfully, and inventory/cost follow the selected design." | Pattern § Acceptance, sentence 2. | AGENT, ratified | |
| `:105` "Where the intended interface permits varying demand while holding hardware fixed, test that separately." | Pattern § Acceptance, sentence 3. | AGENT, ratified | |
| `:105` "An unsupported-domain case must remain explicitly unsupported, with no manufactured success." | Pattern § Acceptance, sentence 4 ("must remain"). | AGENT, ratified | Carried item 1, after round 2. |
| `:105` "For operating-point closures or cost proxies where those tests do not apply, document the reason and check their stated assumptions instead." | Pattern § Acceptance, sentence 5. | AGENT, ratified | |
| `:105` "A review must record MR-7 compliant, violated or unverified for the affected scope with evidence; unknown compliance cannot count as completed remediation." | Pattern § Acceptance, second paragraph ("A review must record compliance…"; "Unknown compliance cannot count as completed remediation"). | AGENT, ratified | "must record" is carried item 1. "cannot count" kept verbatim (orchestrator, after P2: "does not count" read as a description, the M3 slip). |
| `:107` "`capacity = required_flow * margin`, bound as installed capacity, is an automatic design-selection rule even if `margin` is exposed." | Pattern § Examples, row 1; § Validated Pattern, "Wrong" (the sump/pump form). | AGENT, ratified | |
| `:107` "`required_area` compared with independently selected installed area preserves the distinction." | Pattern § Examples, row 2. | AGENT, ratified | |
| `:107` "`volume = area * length` is a geometry identity, not an automatic adequacy rule." | Pattern § Examples, row 3; § Verification, step 1. | AGENT, ratified | Verification use is carried item 3, after round 2. |
| `:107` "Replacing one hidden fixed choice with another does not resolve the architectural issue." | Pattern § Common Mistakes, "Replacing one hidden fixed choice with another". | AGENT, ratified | |

## fusion-tea process paragraphs (`MODELING_PROCESS.md:17`, `:34`)

| Source sentence | Shipped location, or fusion-tea home and reason | Source grade | Note |
|---|---|---|---|
| `:17` "For changes to design variables, equipment/capacity bindings, sizing, operating-point closure or demand-based costing, apply [REQUIREMENTS.md MR-7](…) before selecting a process." | Process template § Technical Patterns, design-choice row ("When changing" column holds this read scope); Pattern § When to Use This Document. Review routing at MR-7's narrower scope: Process template § Process Selection row. | AGENT, ratified | "Before selecting a process" is read as "at the point of use" (spec L3-3; see Closing notes). |
| `:17` "This applies to direct edits and inherited patterns as well as new work." | Pattern § The Rule, closing paragraph, sentence 1. | AGENT, ratified | |
| `:17` "Stage compression does not waive its evidence or review obligations." | Pattern § The Rule, closing paragraph, sentence 3 ("Skipping or combining stages does not waive its evidence or its review"). | AGENT, ratified | |
| `:34` "For MR-7 work, the spec identifies the design choices the consumer must retain." | Pattern § What to Record, bullet 1. | AGENT, ratified | |
| `:34` "The design records the affected variable roles, physical relationships, selection policies, authority and actual binding paths." | Pattern § What to Record, bullet 2. | AGENT, ratified | |
| `:34` "The implementation preserves those choices through generated/native execution and downstream costs." | Pattern § What to Record, bullet 3 ("through every supported execution route"). | AGENT, ratified | "generated/native execution" is fusion vocabulary (design review round 1, A9). |
| `:34` "Review checks those bindings rather than inferring compliance from names such as `required`, `selected` or `sizing_mode`." | Pattern § Review, sentence 3; § Common Mistakes, "Reading compliance off names". | AGENT, ratified | |
| `:34` "Acceptance includes MR-7's applicable insufficient/sufficient design tests and explicit validity limits." | Pattern § Acceptance; § Verification, step 2. | AGENT, ratified | |
| `:34` "Carry the MR-7 evidence into the handoff; do not call a repair complete on depth scores or baseline reproduction alone." | Pattern § What to Record, bullet 4. | AGENT, ratified | "depth scores" → "scores". |
| `:34` "Prospective depth assessments also follow `.project/active/demo-depth-rubric/application-policy.md`; historical rubric bytes and grades remain unchanged." | fusion-tea: MR-7 "Depth work" (A6). Fusion-only: the depth rubric is a fusion-tea project policy. | AGENT, ratified | Ledger row "Depth-rubric policy pointer". |

## Goal-layer hooks

Destinations are the Appendix A8 texts and the Appendix B / plan Phase 3 rows. Phase 3 ports them; Phase 7 checks each destination against the ported text and corrects it if the text moved.

| Source sentence | Shipped location, or fusion-tea home and reason | Source grade | Note |
|---|---|---|---|
| run-goal `:53` "Read `modeling_project/REQUIREMENTS.md`, including MR-7, before grounding or dispatching a model-changing goal." | `skills/run-goal/SKILL.md`, model-changes paragraph, sentence 1 (A8): the target's requirements file and the design-choice pattern, located through `GOAL_RUNBOOK.md` § Grounding a goal. fusion-tea: MR-7 lives in its `REQUIREMENTS.md`, so "including MR-7" holds there without the words. | AGENT, ratified | |
| run-goal `:53` "Follow the MR-7 checks in `GOAL_RUNBOOK.md` and `MODELING_PROCESS.md`; carry the requirement and intended design choices into worker/reviewer briefs." | `skills/run-goal/SKILL.md`, same paragraph, sentence 2 (A8: "design-choice steps"; "applicable requirements"). | AGENT, ratified | |
| run-goal `:53` "Automatic sizing and changes to which quantities are chosen or calculated require explicit design reasoning and applicable review, even when pursuing an already approved depth target." | `skills/run-goal/SKILL.md`, same paragraph, sentence 3 (A8: "quality target"). fusion-tea: MR-7 "Depth work" (A6) for depth targets. | AGENT, ratified | |
| run-goal `:55` "For a single work item, follow `modeling_project/MODELING_PROCESS.md`." | `skills/run-goal/SKILL.md`, single-item paragraph, unchanged. The followed file now carries the Process Selection and Technical Patterns rows. | AGENT (see note) | The snapshot has no history, so which `:55` sentences the 2026-09-20 enforcement change added is not recorded. |
| run-goal `:55` "Read only the stage instructions needed for the current task: `.claude/commands/<stage>.md` in Claude Code or `.agents/skills/<stage>/SKILL.md` in Codex." | `skills/run-goal/SKILL.md`, same paragraph: "the stage's installed skill" (Appendix B, consumer path). | AGENT (see note) | Not a design-choice sentence. |
| run-goal `:55` "Any stage can be brief or skipped when its responsibility is already satisfied or does not apply; cite that evidence or reason in the native record." | `skills/run-goal/SKILL.md`, same paragraph, unchanged. Bounded by Pattern § The Rule, closing paragraph ("Skipping or combining stages does not waive its evidence or its review"). | AGENT (see note) | |
| run-goal `:55` "Keep native PM metadata and applicable executable validation, using the project’s prescribed launcher (`.codex-test/run` in this test worktree; otherwise `uv run`)." | `skills/run-goal/SKILL.md`, same paragraph: "(`uv run` unless the project names another)". fusion-tea: `CLAUDE.md` "Goal layer in this repository", "Launcher" (A7); `AGENTS.md:7,:11`. Fusion-only: `.codex-test/run` exists only in fusion's Codex test worktree. | AGENT (see note) | Ledger row "Codex test worktree setup". |
| run-goal `:55` "Review triggers are in the runbook." | `skills/run-goal/SKILL.md`, same paragraph, unchanged. The runbook's trigger table gains the design-choice mirror row (A8). | AGENT (see note) | |
| runbook `:84` "For a model-changing goal, read `modeling_project/REQUIREMENTS.md` and carry applicable requirements into its invariants." | `GOAL_RUNBOOK.md.template` § Grounding a goal, sentence 1 (A8): adds "and the design-choice pattern" to both the reading and the invariants. | AGENT, ratified | |
| runbook `:84` "MR-7 governs design-variable assignment, automatic equipment selection and demand-versus-installed-capacity meaning." | `GOAL_RUNBOOK.md.template` § Grounding a goal, sentence 2 (A8): names `design-choices.md` and its resolver command; "design-variable roles". | AGENT, ratified | The runbook's one resolver command for the pattern. |
| runbook `:84` "Grounding must identify the choices the goal is intended to preserve or investigate, not assume the current input/output split is authoritative." | `GOAL_RUNBOOK.md.template` § Grounding a goal, unchanged. | AGENT, ratified | |
| runbook `:84` "An existing grounded goal needs a dated amendment when a newly surfaced requirement changes its strategy; do not rewrite its historical contract." | `GOAL_RUNBOOK.md.template` § Grounding a goal, unchanged. | AGENT, ratified | |
| runbook `:100` "Before a strategy changes a design quantity's role, record its MR-7 justification and affected binding/consumer paths." | `GOAL_RUNBOOK.md.template` § Opening and closing a round (A8: "its justification under the design-choice pattern"). | AGENT, ratified | |
| runbook `:100` "Treat an automatic sizing policy or removal of a design choice as a modeling/interface decision, not routine arithmetic." | Same paragraph, unchanged. | AGENT, ratified | |
| runbook `:100` "Existing authorized choices can proceed; a premise conflict or an unresolved material owner choice stops only dependent work." | Same paragraph, unchanged. | AGENT, ratified | |
| runbook `:100` "Depth-target attainment and numerical regression success cannot substitute for the MR-7 assessment." | Same paragraph (A8: "Score or quality-target attainment"; "the design-choice assessment"). | AGENT, ratified | |
| runbook `:100` "For prospective depth work, also read `.project/active/demo-depth-rubric/application-policy.md`." | fusion-tea: MR-7 "Depth work" (A6). Fusion-only: the depth rubric is a fusion-tea project policy. Deleted from the shipped runbook. | AGENT, ratified | Ledger row "Depth-rubric policy pointer". |
| runbook `:139` "For tasks affecting MR-7, include the requirement and intended design choices in every delegated modeling/review brief." | `GOAL_RUNBOOK.md.template` § Running one task (A8: "For tasks affecting design choices, include the applicable requirements, the design-choice pattern and intended design choices…"). | AGENT, ratified | |
| runbook `:139` "At return, inspect the design-role record and applicable behavior-test evidence." | Same paragraph, unchanged. | AGENT, ratified | |
| runbook `:139` "Record compliance as compliant, violated or unverified; a modeled component, passing baseline or rubric score alone cannot establish it." | Same paragraph (A8: "passing baseline or score"). | AGENT, ratified | Procedure at task return; the obligation itself is Pattern § Acceptance. |
| runbook `:139` "Required independent design review covers the actual variable assignment and downstream bindings before dependent implementation; its integration recheck covers the executed behavior." | Same paragraph, unchanged. | AGENT, ratified | |
| `goal.md:29` "**Modeling requirements:** applicable entries from `modeling_project/REQUIREMENTS.md`." | `project_templates/goal.md.template`, same bullet, unchanged. | AGENT, ratified | |
| `goal.md:29` "For MR-7, identify the design choices this goal preserves or investigates and any explicitly authorized design-selection policy; do not inherit a variable's role merely because the current implementation uses it." | `project_templates/goal.md.template`, same bullet (A8: "For a model-changing goal, apply the design-choice pattern (`design-choices.md`; …)"). | AGENT, ratified | |

The runbook section names above are where the hooks sit in fusion's runbook (`:84` under "Grounding a goal", `:100` under "Opening and closing a round", `:139` under "Running one task"). Phase 7 confirms them in the ported file.

## Shipped text with no MR-7 sentence behind it

All `[AGENT]`, 2026-10-11 (design and its reviews). None is presented as owner-originated.

- Pattern § Validated Pattern: the sump/pump wrong and right forms, excerpts of `tests/fixtures/sump_pump/` (design D16, Invariant 8).
- Pattern § Related Patterns: the Equality intent sibling (spec L2-1) and the `adr002-calculations.md`, `semantic-operators.md` and `plant-idiom.md` lines (design review M1).
- Pattern § Verification: "validate cannot see this rule", and the by-hand check.
- Process template § Architecture & Design, the `:59` clause: "and do not set installed capacity, equipment, or inventory from demand; see `design-choices.md` (Technical Patterns below)" (carried item 2).
- The sibling cross-reference lines in `docs/patterns/constraints.md` and `skills/sysml-conventions/SKILL.md` (A3), the three index rows, the `requirements-tracking` tier text (A4), and the `review-model` and `model-validation` pointers (A5). These point at the rule; none states an obligation.

## Closing notes

**Changes after design review round 2.** All `[AGENT]`; none changes an obligation's scope.

1. MR-7's own force in three sentences: rule 7 "must remain the basis", Acceptance "must remain explicitly unsupported", Acceptance "A review must record compliance". `[AGENT]` (design reviewer, round 2, its own round-1 miss; carried by the plan). These restore MR-7's wording; the grade stays AGENT, ratified.
2. The process template's `:59` sentence forbids one direction only, as MR-7 does: "do not set installed capacity, equipment, or inventory from demand". It replaces A2's "do not set one from the other", which also forbade setting an operating point from installed capacity. `[AGENT]` (orchestrator call, plan brief, 2026-10-11).
3. Verification step 1 gains "An identity over supplied values, such as `volume = area * length`, passes." `[AGENT]` (design review round 2, R2-A3). It applies rule 5 and MR-7 `:107`.
4. A `---` line before the pattern's closing grade paragraph, so it reads as the document's close. `[AGENT]` (R2-A4). Layout only.

**"Before selecting a process" read as "at the point of use".** fusion `MODELING_PROCESS.md:17` asked for MR-7 to be applied "before selecting a process" across a wide scope. The shipped split is: the wide scope is the Technical Patterns row's read scope, read at the point of use; the review trigger in "Process Selection" uses MR-7's narrower enforcement scope (`:103`). `[AGENT]` (orchestrator, spec review L3-3) for the trigger scope; `[INFERRED]` (spec author) for the read scope. Reading the rule costs little; independent review does not.

**Fresh reviews of the shipped wording against MR-7.**

- `design-review.md` § "SC6 fresh check: the shipped wording against MR-7" (round 1): every general obligation present; four force or scope slips (M3), fixed in the design revision.
- `design-review.md` § "Round 2" → "SC6 re-check": Approve on A1 as revised, with the three wording misses that became carried item 1.

**Pending.** The O1 delta check: a fresh non-author reviewer checks every change after round 2 (carried items 1–4 above) against MR-7 `REQUIREMENTS.md:89-107` for force and scope, and records the verdict in `evidence/sc6-delta-check.md`. A fail is fixed in agentic-mbse before fusion-tea's F1 copies template bytes.
