# Goal-Layer Decisions

Why the goal layer is shaped the way the goal runbook describes. The runbook (`work/orchestration/GOAL_RUNBOOK.md` in a target) cites these records by id and does not restate them. This record explains the runbook; it is never cited as a modeling rule.

## How This Record Governs

**For installed targets, this record is the authority.** It is a dated snapshot of the goal-layer decision records of the project that first ran the layer, taken 2026-10-11 at fusion-tea@2b1e9f9d5. That project's live records govern that project only.

**Amendments.** A later amendment to the source records reaches targets only through an ordinary agentic-mbse change to this file, never by reference. Each entry keeps its source record's id, grade and dated amendments, so an id the runbook cites means the same decision here.

**Grades** follow the source records. `[OWNER]` is the owner's decision and `[OWNER-VERBATIM]` quotes it; "the owner" is the owner of the project that first ran the layer. `[AGENT]` is agent-written, marked "ratified" where the owner approved it. `[INFERRED]` is an agent's reading of other records. An `[OWNER]` decision is challenged by asking for an owner ruling; an `[AGENT]` or `[INFERRED]` one by re-deriving it against the reasoning recorded here.

**Two project-management systems are a condition, not a premise.** ADR-0006 was decided in a project that runs two: the modeling PM in `work/` and a second PM (for example a coding PM in `.project/`). Its permission to cite across them applies where a target runs a second PM. Its citation forms apply in every target; the runbook states them in § When a cited artifact moves.

## The Records

### ADR-0001 — A goal round authorizes one bounded task at a time, under one revisable strategy

**Grade:** `[AGENT]`, ratified by the owner; the coarse task grain is inferred from the owner's lean-first ruling (ADR-0003). Decided 2026-08-25. Amended 2026-09-11, `[AGENT]` ratified by the owner, who accepted the replacement text and asked for it to be implemented.

**Decision, as amended.** A round runs under one strategy revision: its approach, assumptions, abandonment conditions, intended model increment and intended study question. The revision holds no future task list. A task is one bounded objective and may span several native stages; each task records its six-line scope (Objective, Why now, Scope, Inputs, Done when, Stop when) before work begins. Strategy is revisable; authorization is not carried forward, so every successor task gets its own recorded scope.

**Amendment, 2026-09-11: bounded parallel tasks.** This replaces the original rule of at most one active task. Tasks may run in parallel when write-conflict risk is low and neither task's result is likely to invalidate the other's scope or justification. Record that judgment and file ownership before dispatch. Each task keeps its own scope, start and return; the round agent integrates results in sequence and pauses affected work when new evidence undermines its justification. Low write-conflict risk alone is not enough when one task's evidence could invalidate another's justification.

**Why.** A recorded bounded task prevents stale authority: an agent holding an open-ended mandate keeps acting on a premise the evidence may already have overtaken, and nothing shows when that happened. Re-recording a scope per task restates the premise where a reader or reviewer can see it. The grain is coarse because a prose loop cannot carry a scope review per native stage. Rejected: forward task plans inside the strategy, which grant authority before the evidence arrives; and one goal task per native stage, which re-encodes native sequencing.

**Invariants.** `GOAL_RUNBOOK.md` § Running one task (scope, write-ahead, return); the `trail.md` template's six-line scope heading; the round review checks every recorded task scope after the round closes. Scope is a reviewable record, not a sandbox: an unresolved owner gate is the one bound that prevents execution outright. `PREREQUISITE` is discovered as a return, never predicted in a scope.

**Source:** fusion-tea `.project/adr/0001-strategy-and-task.md@2b1e9f9d5`, provenance "[AGENT] ratified by owner; coarse grain inferred from lean-first ruling".

### ADR-0002 — One agent pursues one strategy for a round; a fresh agent reviews it and authors the next

**Grade:** `[OWNER]` purpose; `[AGENT]` mechanism. Decided 2026-08-25. Amended for the owner's 2026-09-14 process-simplification request; the trigger selection and coverage reuse are `[AGENT]` implementations of that request. The title records the original mechanism.

**Decision, as amended.** A round is one agent's bounded pursuit of one strategy. It ends in a written round result, even when intent was not met, and a closure coverage record. Independent review follows `GOAL_RUNBOOK.md` § Review scope and evidence reuse; routine closure may be a coordinator check with cited evidence and a reason no further review is needed. A required independent reviewer is a fresh non-author and returns `PASS | FINDINGS | OWNER_GATE`. No review reopens a closed round. The coordinator or reviewer may propose the next strategy; the owner keeps the close rule.

**Why.** An agent asked to review its own round defends it, and self-defense costs most at the moment a strategy should be abandoned. The same freshness keeps the round result honest about unmet intent: a failed attempt is a legitimate result. The mandatory result makes rounds finite and leaves no hole in the history where the hardest judgment was. Rejected: perpetual same-agent pursuit, which has no point at which anything is re-grounded.

**Invariants.** `GOAL_RUNBOOK.md` § Opening and closing a round and § The fresh review; the `trail.md` template's round result and review headings; `learnings.md`, whose delta the result proposes and closure accepts or corrects. Every closed round accounts for task scopes, retry classification, touched-finding dispositions, cited-ref liveness, the learning delta and carry-forward. Coupled architecture, several model families or failed coverage require substantive independent integration review (ADR-0005).

**Source:** fusion-tea `.project/adr/0002-round-boundary.md@2b1e9f9d5`, provenance "[OWNER] purpose; [AGENT] mechanism".

### ADR-0003 — Begin with prose files and native facts; harden only on an observed failure

**Grade:** `[OWNER]` lean-first ruling, 2026-08-23, choosing option (a), lean first and harden on evidence (the owner's words: "yeah I agree with (a)."); `[AGENT]` the separate `learnings.md` mechanism. Decided 2026-08-25. Amended 2026-08-27, 2026-08-28 and 2026-09-11, below.

**Decision.** The first build is three prose files per goal (`goal.md`, `trail.md`, `learnings.md`), plus the review coverage of ADR-0002 and ADR-0005 and the joined discovery-log dispositions of ADR-0004. `trail.md` is append-oriented, corrections are dated amendments, and git supplies history; there is no sealing scheme. Accepted cross-round meaning goes in `learnings.md`, so a new round reads it without scanning the whole trail. The 2026-09-14 amendments to ADR-0002 and ADR-0005 replace unconditional fresh-round review with risk-based coverage.

Every control-plane mechanism stays on the hardening path and is promoted only when a run shows prose failing. Each promotion records the observed failure and the smaller alternatives tried.

| Mechanism | Promote only when |
|---|---|
| Immutable task envelope and authority digests | Unattended dispatch needs a stale-authority guard |
| Append-only event ledger | A real resume or replay cannot be reconstructed from the trail |
| Denser per-stage trail events | Task-grain logging fails to reconstruct a real run |
| Idempotency keys and effect queries | A native mutating procedure cannot resolve interrupted unattended work — repair its owner first |
| Hand-run or dispatched reconciliation | Both routes exist and need one machine-consumed return |

**Why.** The machinery catches drift, replay ambiguity and concurrent mutation. A single-operator, serialized, git-tracked layer with no concurrent goal runs and no unattended dispatch already covers most of that with git and a fresh reviewer. Building the control plane first would cost the whole first build and prove nothing, because there is no failure yet to measure it against. Rejected: a first-build control plane, whose cost is certain and benefit hypothetical; and learning inline in the trail, readable only by scanning everything.

**Invariants.** The three goal templates; the whole runbook is prose and native facts by this ruling; no mechanism from the table enters without a recorded failure. That evidence must be recorded, not routed around. First unattended dispatch is a pressure test, not permission to pre-build every mechanism.

**Amendment, 2026-08-27: the proof run promoted nothing.** `[OWNER]` hardening rule unchanged; the verdict is `[AGENT]` measurement, ratified by the owner's criteria ruling of 2026-08-27. Thirteen cold sessions ran the prose route against a real goal: grounding, a real mid-task process kill and a resume from disk, a bounded round close, a fresh round review, and a standalone reader. The route failed in ten recorded places; a cold session, the fresh review or the operator caught every one, and none needed a mechanism from the table. The event-ledger row was exercised and did not trigger: the interruption was reconstructed from native facts with no repeat of the landed effect. The idempotency row is untested, not passed, because the resume was attended. The one recorded cost: an interrupted session's in-flight goal-level decisions die with it. Two findings went to the owner as written-rule repairs and were taken: the grounding gate defended too few field classes (measured reach 2 of 5), so the five-class grounding rule was promoted into the runbook (§ Grounding a goal), and a contradiction between two runbook lines was corrected. Amending prose on recorded evidence is what this decision asks for; it is not a hardening promotion.

**Amendment, 2026-08-28: a second run, on a live open question, promoted nothing.** `[OWNER]` hardening rule unchanged; the verdict is `[AGENT]` measurement, audited 2026-08-28. Eight cold sessions ran a full round on an open modeling question the project actually had, through grounding, a bounded task, a pre-execution checkpoint that refused and then released, joined discovery-log dispositions, a fresh round review and an owner close. Eight recorded prose failures were each caught without any mechanism from the table. The trail held an owner-visible disagreement between critic and author, adjudicated by a second fresh critic, with nothing edited in place. A sandbox that degraded three times mid-run was absorbed by clean, recorded stops. A future round that reopens the hardening question starts from both measurements.

**Amendment, 2026-09-11: native fresh-reviewer dispatch.** `[OWNER-VERBATIM]` "yeah I am fine with the automatic reviewer, as long as it is a subagent with fresh context". A goal agent may use the host's native subagent tool to obtain a reviewer with no inherited conversation context. This replaces the operator-only dispatch restriction; the recorded handoff remains the fallback when a fresh session cannot be obtained. The runbook's § What "fresh" means applies this boundary.

**Source:** fusion-tea `.project/adr/0003-lean-first-persistence.md@2b1e9f9d5`, provenance "[OWNER] lean-first ruling, 2026-08-23; [AGENT] separate `learnings.md` mechanism".

### ADR-0004 — A goal round dispositions every discovery row its evidence touched, by appending a joined row

**Grade:** `[OWNER]` 2026-08-23. Decided 2026-08-25. The owner ruled that the earlier settled criterion holds: the discovery log carries finding, disposition and what changed across rounds, with nothing dangling.

**Decision.** Every open discovery row a round's evidence touches receives a disposition recording `model fix | research | declared seam | upstream filing`, its status, the responsible task or owner, and what changed or the concrete next reference. No touched row returns as `unrouted`. The study executor writes first-sighting rows. A goal round records a disposition by appending a row joined by `<study-id>#<n>`; it never edits a first-sighting row and never mints a finding id. An administrator role stays read-only and never appends. Row kind is positional: for an id, the earliest row in file order is the sighting, later rows are disposition updates, and the newest is the finding's current state.

**Why.** A finding with no consumer silently loses a study's most expensive output; in the source project, rows sat in the log with no consumer, several of them `unrouted`. Putting the accounting in the round result and its review places it where someone already reads the evidence, at the cost of one checklist line. Appending keeps the log append-only and the executor's sighting intact. Rejected: a shadow finding log owned by the goal layer, which would disagree with the real one; silently retiring the obligation, which an agent grade cannot do to an owner-settled criterion; and editing the sighting in place.

**Invariants.** `GOAL_RUNBOOK.md` § The discovery log. Where a target installs a study layer, its runbook carries the sole-writer rule, the read-only administrator and the one-row-per-finding schema, its discovery log's header carries the writer and cardinality rules, and its join check tolerates several rows under one id by intent. A goal round may append only under an id a committed study record already carries. A finding the round discovers itself is not a log row; it goes to `learnings.md`, a native work item, the research procedure or the target's decision record, and the trail cites that home. The one-row-per-finding rule means one row per sighting, plus joined disposition rows; a disposition row carries a disposition, never a second account of the finding.

**Source:** fusion-tea `.project/adr/0004-finding-disposition.md@2b1e9f9d5`, provenance "[OWNER] 2026-08-23".

### ADR-0005 — One fresh round critic, plus one pre-execution disposition checkpoint

**Grade:** `[AGENT]` inference for the topology (the owner may override); `[OWNER]` 2026-08-25 for the pre-execution checkpoint's placement. Decided 2026-08-25. Amended for the owner's 2026-09-14 process-simplification request; the risk-based topology is an `[AGENT]` implementation of that request. The title records the original mechanism.

**Decision, as amended.** Review coverage follows `GOAL_RUNBOOK.md` § Review scope and evidence reuse. Independent reviews are required for concrete source, math, design and integration risks; routine work may close with a reasoned coordinator check. Coverage includes native evidence, goal and strategy fidelity, task scope, retries, touched-finding dispositions, learnings and carry-forward. Native, study, checkpoint and round reviews reuse valid evidence rather than checking the same claim in separate sessions. Review of uncovered triggered risks in a study reading and its proposed dispositions happens before dependent follow-up executes; this keeps the owner's pre-execution placement. A required independent reviewer is a fresh non-author, reused for corrective diffs. The declared cap stops unresolved dependent work and never permits execution. Owner-reserved scientific decisions stay with the owner. Reasoning before dependent execution and remaining coverage after closure need separate sessions only when the risks or evidence demand them.

**Why.** A fresh critic at every native stage would duplicate the technical reviews the native workflows already run, and duplicate criticism teaches agents that reviews are ceremony. Independent judgment changes an outcome at the round boundary, where a strategy is continued or abandoned. The checkpoint exists because the round review is too late for one failure: wrong dispositions get executed before anyone independent reads them, and follow-up work compounds on the misread. The post-execution check that each disposition landed and the finding moved sits inside the round review, which already walks every touched row; that placement is `[AGENT]` and the owner may override it. Rejected: per-stage fresh critics; a third critic for the post-execution audit, reading the same evidence twice; and deferring required pre-execution coverage to closure.

**Invariants.** `GOAL_RUNBOOK.md` § The pre-execution disposition checkpoint, § The fresh review and § Timing of review coverage; the `trail.md` template's checkpoint and round review headings; native review coverage is cited, not repeated. Task scope and retry classification stay recorded checks, written at the time and audited at round end. The checkpoint cap and the retry cap are declared limits in each goal's own Limits section.

**Source:** fusion-tea `.project/adr/0005-review-topology.md@2b1e9f9d5`, provenance "[AGENT] inference (topology; owner may override) + [OWNER 2026-08-25] (pre-execution checkpoint placement)".

### ADR-0006 — Goal artifacts may cite a second PM's records by path and digest; each PM is still mutated only through its own operations

**Grade:** `[OWNER]` 2026-08-23. Decided 2026-08-25. The reconciliation of the two digest meanings, under Invariants, is `[INFERRED]`; the digest requirement stays owner-graded. This record applies where a target runs a second PM (How This Record Governs).

**Decision.** Goal input references may cite the second PM's artifacts by path and digest, and the reverse direction is equally permitted. Each PM stays mutable only through its own native operations. The digest is `<path>@<commit-sha>` for a tracked artifact, since git already supplies a content digest. Where no native hash exists, the citation says so rather than inventing one: an untracked study store is cited through its committed record, which carries the store's identity; an externally stored research binary through its tracked extracted text; anything else by path with the words "unpinned; no native digest". Citing is not mirroring: no goal artifact copies or restates the other system's state.

**Why.** A blanket rule against cross-referencing two PMs exists to stop their state being mirrored, which produces two records of one work item that disagree. Read literally, it also forbids the goal layer from citing the evidence it exists to reason about. The digest makes a citation honest: a path says where to look, a path with a commit says which version was read. Reserving mutation to native operations keeps the original purpose of the ban. Rejected: mirrored PM state; a blanket citation ban; and a goal-layer digest scheme for untracked evidence, which the hardening path covers (ADR-0003).

**Invariants.** `GOAL_RUNBOOK.md` § When a cited artifact moves, which says how a citation is written and read; both PMs' operations are unchanged. In the source project, the instructions' rule against cross-referencing the two PMs was narrowed to state, naming this record. A citation digest is read by a person to see which version was cited. It is not the hardening path's authority digest, which a procedure would compare to decide whether work is still authorized; no goal procedure compares or recomputes a cited digest.

**Source:** fusion-tea `.project/adr/0006-goal-evidence-seam.md@2b1e9f9d5`, provenance "[OWNER] 2026-08-23".

### ADR-0007 — The task is the authority unit; the finding stays the traceability unit

**Grade:** `[AGENT]` for the task-as-authority half; `[OWNER]` 2026-08-23 for the finding-obligation half. Decided 2026-08-25.

**Decision.** Two things, filed together because one earlier candidate entangled them. (i) The task is the orchestration authority unit, `[AGENT]`: what may be worked on next is decided by the round's strategy and recorded in a task scope, not derived from a finding queue. A finding does not authorize work. (ii) The finding stays the traceability unit and its cross-round obligation holds, `[OWNER]` 2026-08-23: every open discovery row a round's evidence touches gets a joined disposition. The mechanism is ADR-0004.

**Why.** "What am I authorized to do next" and "where did this finding end up" are separate questions. Collapsing them produced a finding-as-work-queue, which orders work by discovery order rather than by strategy. Splitting the candidate also fixes its grade: filed whole at `[AGENT]`, it would have made an owner ruling challengeable by re-derivation. Rejected: finding-as-authorization queues; filing the candidate unsplit at `[AGENT]` grade.

**Invariants.** Task selection is driven by strategy and evidence and recorded in the task scope (ADR-0001). Finding disposition follows ADR-0004. The runbook states both halves in different sections and does not conflate them: a reader asking why something was worked on reads the strategy and scope, and a reader asking what happened to a finding reads the discovery log. The goal round writes a finding's disposition; the study executor keeps the sighting.

**Source:** fusion-tea `.project/adr/0007-supersession.md@2b1e9f9d5`, provenance "[AGENT] task-as-authority-unit half; [OWNER] 2026-08-23 finding-obligation half".

## Sources the Runbook Cites

Owner statements the runbook quotes or rests on, beyond the records above.

- **The critic definition.** `[OWNER]`, the goal-layer concept's success criterion 5: "The critic is never the author's session." The runbook quotes it as its definition of a fresh review (§ What "fresh" means). Source: fusion-tea `.project/concepts/goal-driven-model-development-harness.md@2b1e9f9d5`, line 47.
- **Goals are general.** `[OWNER]`: "Goals are general to the systems-engineering and concept-development process; the operator need not be the builder and is not limited to pre-defined items." This is why agentic-mbse ships the goal layer to every target. Source: fusion-tea `.project/concepts/goal-driven-model-development-harness.md@2b1e9f9d5`, line 198.
- **The 2026-08-27 probe amendment.** `[OWNER]` amendment to § Grounding a goal. A five-session probe measured cold sessions running full tasks on goals that lacked invariants, limits or reserved gates, so the grounding gate now defends all five field classes. The measurement is ADR-0003's 2026-08-27 amendment. Source: the probe record fusion-tea's runbook cites at fusion-tea@2b1e9f9d5, `.project/completed/20260827_goal-cold-pickup-proof/gate-probe-record.md`.
- **The 2026-09-14 process-sizing request.** `[OWNER]` request to reduce harness overhead, recorded in the source records as the owner's process-simplification request; they do not quote its wording. The triggers in § Review scope and evidence reuse and the 2026-09-14 amendments to ADR-0002 and ADR-0005 are `[AGENT]` implementations of it. Source: fusion-tea `.project/adr/0002-round-boundary.md@2b1e9f9d5` and `.project/adr/0005-review-topology.md@2b1e9f9d5`.
