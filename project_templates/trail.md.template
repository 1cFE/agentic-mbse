# Trail: <goal name>

What happened, and what was decided. Copy to `work/orchestration/goals/<goal-slug>/trail.md`.

Append-only, newest entry last, ISO dates. **No entry is ever edited in place.** A correction is `### Amendment YYYY-MM-DD — amends <entry heading>`, stating what changed and why.

This file logs judgment, not routine stage motion. Native workflows keep their own stage records; entries here cite them by path or native id and never restate their content. Procedure is in `work/orchestration/GOAL_RUNBOOK.md`.

The entry headings below are the contract. They appear under a round in the order they occur.

## Round 1 — <strategy-slug>

### Strategy revision — YYYY-MM-DD

- **Approach:** what this round will try.
- **Assumptions:** what it rests on.
- **Abandonment conditions:** what would make you stop trying this.
- **Intended model increment:** what should change in the model.
- **Intended study question:** what the study should answer.

**No future task list.** The next task is chosen from evidence after the previous one returns.

### T-001 scope

- **Objective:** one question or change.
- **Why now:** the connection to the strategy, and the triggering evidence.
- **Scope:** what is authorized; what is explicitly excluded.
- **Inputs:** native refs. Cite `goal.md` and state only any *narrower* constraint.
- **Done when:** a useful positive or a bounded negative.
- **Stop when:** prerequisite, strategy blocker, owner gate, or declared limit. `PREREQUISITE` is discovered as a return and is never predicted here.

### T-001 start — YYYY-MM-DD

One line, written before the first native side effect: task · native target · expected artifact.

A retry is **not** a new entry kind. It is another `### T-001 start` under the same task id carrying "retry N of 2; task, inputs, scope, and meaning identical" plus the operational correction.

### T-001 return — YYYY-MM-DD

- **Outcome:** one of `COMPLETE | BOUNDED_NEGATIVE | PREREQUISITE | STRATEGY_BLOCKER | OWNER_GATE | MECHANICAL_FAILURE`.
- **Evidence:** native refs, by path and digest.
- **Reading:** what that evidence means at goal level.
- **Decision:** trigger · decision and reason · tier (`execution detail | reserved gate | premise surprise`) · decided by · what changed (paths, ids, commits, or `none`).

One `Decision` block per goal-level decision made during the task.

### Checkpoint C-001.r1 — YYYY-MM-DD

- **Reviewer:** fresh non-author when triggered; otherwise coordinator, with a reason no additional independent review was needed and cited valid coverage.
- **Reading reviewed:** the study reading.
- **Dispositions reviewed:** the proposed dispositions.
- **Verdict:** `PASS | REVISE`.
- **Revision:** K of 2. What the author changed.

Each submission is a **new** entry — `r1`, `r2`, `r3` — never an amendment to the previous one. The sequence of verdicts is the record of the disagreement. Past the cap, write a `### Stop` of kind `cap`; the round stops and execution is not permitted.

### Round 1 result — YYYY-MM-DD

- **Intent:** met or unmet. Unmet is a legitimate result.
- **Task sequence:** the tasks in order, with their outcomes.
- **Last semantic outcome:** the outcome that ended the round.
- **Stop reason:** written as a derivation, not a label — "last outcome `<X>` + `<limit or none>` → round closes". The only legal right-hand sides are the six close triggers.
- **Evidence refs:** by path and digest.
- **Learning delta:** proposed, not yet accepted.
- **Finding dispositions:** every discovery row this round's evidence touched, with its joined `<study-id>#<n>` id.

Mandatory, even when the intent failed.

### Round 1 review — YYYY-MM-DD

- **Reviewer:** fresh non-author for uncovered triggered risks; otherwise coordinator. Record the reason and reused evidence; do not label coordinator closure an independent pass.
- **Verdict:** `PASS | FINDINGS | OWNER_GATE`.
- **Checks:** native evidence by citation · goal and strategy fidelity · every recorded task scope · retry classification · every touched discovery row and what changed · cited-ref liveness · the learning delta · constraints carried forward.
- **Next:** closure recommended, or the next strategy.

The review never resumes the closed round.

### Stop — YYYY-MM-DD

- **Kind:** `interruption | limit | cap | owner gate | handoff | external mutation`. `handoff` is an agent that reached a gate needing a fresh session it cannot start (`GOAL_RUNBOOK.md` § What "fresh" means).
- **What is true on disk:** the native state, read as truth.
- **What the owner must see:** the decision or the unresolved item.

## Goal close — YYYY-MM-DD

- **Ruling:** the owner's close ruling, quoted or cited.
- **Disposition:** closed on § Answered when, or closed by redirect, and why.
