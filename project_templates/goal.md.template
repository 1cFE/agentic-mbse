# Goal: <one-line name>

Copy this file to `work/orchestration/goals/<goal-slug>/goal.md` and fill it in with the operator. Headings stay in this order — they are the contract. Procedure is in `work/orchestration/GOAL_RUNBOOK.md` § Grounding a goal; this file does not restate it.

Unwrapped prose, ISO dates, newest entry last. Nothing here is edited in place once the goal is grounded — corrections go in § Amendments.

## Status

`draft` — a goal is `draft` until § Grounding evidence is non-empty, and **a draft goal authorizes no task**. Change to `grounded` only when the operator agrees the evidence is there.

## Question

The question, in one sentence, written as a question.

## Consumer

Who is asking, and what they will do with the answer.

## Answered when

The condition that ends this goal, concrete enough that two people would read it the same way.

## Invariants

What a comparison must preserve for results from different rounds to mean the same thing.

- **Package:** the pin, the package identity, whatever must not move under the comparison.
- **Comparison:** what "better" means, and what would change it.
- **Modeling requirements:** applicable entries from `modeling_project/REQUIREMENTS.md`. For a model-changing goal, apply the design-choice pattern (`design-choices.md`; `GOAL_RUNBOOK.md` § Grounding a goal says where it is): identify the design choices this goal preserves or investigates and any explicitly authorized design-selection policy; do not inherit a variable's role merely because the current implementation uses it.

## Grounding evidence

Repository paths for what is already known, each cited as `<path>@<commit-sha>` for tracked artifacts. For untracked evidence, cite the tracked native record that hashes it, or write "unpinned; no native digest" (`GOAL_RUNBOOK.md` § When a cited artifact moves).

Empty means `draft`.

## Limits

Restate the numbers explicitly. Defaults come from `GOAL_RUNBOOK.md` § Limits; a declared value wins over the default, and nothing is inherited silently.

| Limit | This goal |
|---|---|
| Retry cap | 2 retries (3 attempts) |
| Checkpoint revision cap | 2 revisions (3 submissions) |
| Round limit | 6 rounds |
| Time or iteration limit | none, or state it |

## Reserved gates

The decisions the owner keeps. An unresolved reserved gate is the one bound that stops execution outright.

## Close rule

Owner-held. State who closes this goal and on what.

## Amendments

`### Amendment YYYY-MM-DD — amends <heading>` — what changed and why. Rare.
