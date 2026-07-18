# Design Review: Orchestrate Modeling

**Design:** `.project/active/orchestrate-modeling/design.md`
**Spec:** `.project/active/orchestrate-modeling/spec.md`
**Review File:** `.project/active/orchestrate-modeling/design-review.md`
**Date:** 2026-07-18

---

## Fundamental Assessment

Sound. A thin, prompt-led coordinator that delegates to existing stage commands through Task
agents is the simplest design that meets the spec, and the design earns trust by what it
rejected: the shell/session helper port, a run database, automatic closure. The scope
additions beyond the spec (the `pm add-epic` repair, the audit epic scope) are forced by
verified facts — epic creation genuinely cannot work through any documented interface today
(`claude/commands/backlog.md:40` calls a nonexistent `pm add-to-backlog`; the real CLI only
accepts trivial/standard at `src/agentic_mbse/cli/pm_cli.py:496`; the operation requires a
pre-existing epic at `src/agentic_mbse/pm/operations.py:906`) — and D3 records the owner
selecting the repair on 2026-07-17. I verified the design's ~20 code citations; all are
substantively accurate (two are off by a few lines: review-model's advisory statement is at
`claude/commands/review-model.md:15`, and the MODELING_PROCESS read is at
`claude/commands/design-model.md:35`).

The concerns below are gaps inside a sound approach, not reasons to rework it.

---

## Dimensional Review

### 1. Spec Compliance

**Assessment:** Pass

Every spec requirement lands somewhere concrete: single-item and epic support (Architecture),
flow documentation (D1), thin/judgment-led (Core Concept, Non-Goals), the autonomy pattern
(decision tiers, Required Invariants), entry-point selection (Architecture), dependency
ordering (DAG), separate authoring/audit contexts (Required Invariants), registration
(Component Overview, Integration step 5). All six spec Open Questions get answers. Provenance
is carried faithfully — D3's owner ratification is dated, and the `[REFERENT]`'s stated force
("adapt, not copy") is honored by rejecting the shell-helper port.

One inherited item to note: the design treats the four-part autonomy pattern as fixed. That is
correct per the spec as written, but the spec review (its L1-1) questions whether the
enumeration is owner-stated or inherited from `_my_orchestrate.md`. If the spec's answer
changes the pattern's grade, the design's "Treat these as fixed" list should not silently
absorb it.

### 2. Pattern Consistency

**Assessment:** Pass

The design reuses what exists instead of inventing: Task agents are already the parallel-work
pattern (`claude/commands/design-model.md:54`), `pm add-epic` goes through the same
parse/render path as `add_item` (`src/agentic_mbse/pm/operations.py:892`), the flow map lands
in an already tool-owned, already-read template (`src/agentic_mbse/cli/__init__.py:80`,
`claude/commands/design-model.md:35`), and it correctly refuses to reuse `invoke_claude`,
whose read-only, no-session contract (`src/agentic_mbse/extraction/claude_enhance.py:96-100`)
is wrong for authoring.

### 3. Abstraction Quality

**Assessment:** Pass

Six components, each with a one-line ownership statement, and no new subsystem. The design's
main abstraction discipline is negative — no state machine, no run database, no session
tracking — and each refusal is justified with a fallback trigger ("if dogfooding shows
repeated work or lost gates, add one small run manifest"). That is the right shape for a
first version.

### 4. Duplication Avoidance

**Assessment:** Pass

D1 makes `MODELING_PROCESS.md` the single flow source and demotes other surfaces to local
predecessor/successor facts, which addresses the verified existing drift (the stale `Levels
4-8` at `claude/commands/plan-model.md:111` and `/backlog clear` at
`project_templates/README.md.template:148`). One residue: `README.md.template` is user-owned,
so its corrected flow diagram will not propagate to existing installs on re-init. Minor, but
the plan should not assume it does.

### 5. Data Structure Clarity

**Assessment:** Concerns

The `pm add-epic` interface is fully specified (flags, validation, rejection rules). The weak
structure is the **Alignment record**:

- **Chicken-and-egg for fresh standalone items.** The invariant says the "governing epic or
  standalone spec records the launch alignment and reserved gates **before dependent stages
  proceed**." But for a fresh standalone objective the canonical route enters at `spec-model`
  — no spec exists at Align time, so there is nowhere to persist the alignment before the
  first dependent stage runs. If the orchestrator crashes between Align and spec completion,
  the reserved gates are lost, which is exactly the failure B2 claims to survive. The design
  needs to name the home for the pre-spec window (e.g., the work-item directory) or state
  that the first stage is exempt from the invariant.
- **Dual ownership of the spec artifact.** Writing an `Orchestration Alignment` section into
  a spec that `spec-model` authors (and may later regenerate) makes the file dual-owned.
  Say who wins on regeneration, or put the section somewhere only the orchestrator writes.

### 6. Route Safety

**Assessment:** Concerns

The three-tier decision policy and the explicit list of what the overlay does *not* supersede
are well-drawn. Two mechanism gaps:

- **"Continues with that context" is ambiguous, and the ambiguity is load-bearing.** D2 says
  a stage that returns a question is answered by the orchestrator, which "continues with that
  context." Continuing a returned Task agent with its context intact is a capability the
  harness only recently gained and target-repo environments may lack; the software reference
  needed a session protocol (`orchestrate-stage.sh resume`) precisely because plain headless
  invocations can't be continued. If continuation actually means "launch a fresh agent with
  the answer folded into the brief," the stage loses its working context mid-thought, and
  stage prompts must be written to survive that. The design must state which mechanism it
  means, because the plan and the orchestrator prompt differ materially between the two.
- **The audit-repair loop is unbounded.** D4 says the orchestrator "repairs and re-audits
  failures, then reports completion." The software reference caps reviewer ping-pong at ~2
  rounds. Without a bound or an escalation rule (park and surface after N failed repairs), a
  persistent audit failure loops silently — the one behavior an autonomous overlay must not
  have.

### 7. Bets & Decisions Integrity

**Assessment:** Concerns

B1–B3 are genuine bets, each with a real "if false" consequence, and B2 is honestly the
riskiest with a named fallback. Decisions each record a rejected alternative. But two
load-bearing beliefs go unstated:

- **Hidden bet: the orchestrator's own context survives a multi-item epic run.** The
  orchestrator carries the alignment, every recorded decision, and the evaluation of every
  returned artifact across N items × ~5 stages. The software reference addresses this
  explicitly ("keep your context light; their `result` is your main signal"). The design
  never mentions context budget; if the orchestrator compacts or restarts mid-run, B2's
  artifact-only resume is the recovery path — which makes finding 5's alignment-record gap
  more expensive, since the alignment is the one thing artifacts don't yet reliably hold.
- **Hidden bet: a prompt overlay reliably suppresses stage interactivity.** Risk 1 covers
  the mechanism (stage prompt declares non-interactive), but the belief that every stage
  command's `AskUserQuestion` checkpoints degrade gracefully under that instruction is
  untested until the tabletop scenarios run. Fine to bet — but state it, so the tabletop is
  understood as testing it.

### 8. Reader Comprehension

**Assessment:** Pass

Core concept before mechanism, bets before decisions, one skim gives the model. Research
Findings double as evidence for the decisions, which is the right use of the section. The
densest prose ("write surfaces," "owner-grade decisions") is house vocabulary with a
referent, not coinage.

---

## Issues by Severity

### Critical

*(none)*

### Major

- **Alignment record has no home before the first spec exists**, breaking its own invariant
  for fresh standalone items — Data Structure Clarity
- **Stage continuation mechanism unstated** (resume-with-context vs fresh relaunch with
  augmented brief); the orchestrator prompt and plan differ materially between them — Route
  Safety
- **Audit-repair loop unbounded**; needs a round cap or park-and-surface rule — Route Safety
- **Orchestrator context growth over long epic runs is an unstated bet** with no stated
  working style to mitigate it — Bets & Decisions

### Minor

- `Orchestration Alignment` section makes spec.md dual-owned; state who wins on regeneration
  — Data Structure Clarity
- `README.md.template` is user-owned, so its flow-diagram fix won't reach existing installs
  on re-init — Duplication Avoidance
- Two line cites drifted (`review-model.md:15`, `design-model.md:35`) — cosmetic
- Interactivity-suppression bet should be named so the tabletop scenarios are read as its
  test — Bets & Decisions

---

## Recommendations

1. Name the alignment record's home for the pre-spec window (work-item directory is the
   obvious candidate) and reconcile the "before dependent stages proceed" invariant with it.
2. State the continuation mechanism in D2 explicitly. If it is fresh-relaunch-with-brief,
   require stage briefs to be self-contained; if it is agent continuation, name the
   capability dependency.
3. Bound the audit-repair loop (e.g., two repair rounds, then park and surface).
4. Add the context-budget working style to the orchestrator's design (subagent results as
   primary signal, read artifacts only to make a call), mirroring the reference.

---

## Resolutions

- **Pre-spec alignment and spec ownership:** Accepted. The design now uses an orchestrator-owned
  `work/orchestration/<objective-slug>.md` brief written immediately after Align. Specs and epics link
  to it; stage-owned artifacts do not duplicate or regenerate its content.
- **Stage continuation:** Accepted. Every Task call uses a self-contained brief. A returned question is
  answered through a fresh Task launch with the original brief plus the answer; no session-resume
  capability is assumed.
- **Audit loop:** Accepted with a narrower bound. Two unsuccessful repair-and-audit rounds for the same
  finding, or any round with no material progress, cause the dependent work to park and surface. A new
  finding begins a new cycle.
- **Long-run context growth:** Accepted as a working-style correction, not a load-bearing bet. Stage
  results are the parent's primary signal; artifact detail is read only for decisions. Durable recovery
  comes from the alignment brief and pipeline artifacts.
- **Interactivity suppression:** Accepted and added as B4. Tabletop validation now tests the
  non-interactive contract and fresh-relaunch behavior.
- **README ownership and citation drift:** Accepted. The design distinguishes new-project README updates
  from the tool-owned flow delivered to existing projects, and corrects the two citations.

---

**Overall:** Approve — the accepted resolutions are incorporated in the design; no critical or major
issues remain.
**Next Steps:** Proceed to planning.
