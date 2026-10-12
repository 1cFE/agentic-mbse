---
name: run-goal
description: >
  Operate the goal layer: ground a goal, open or run a round, review a study reading's
  proposed dispositions before follow-up work executes, or review a closed round as a
  fresh agent. Use when asked to pursue a grounded question across rounds of modeling
  and studies, to pick up an interrupted goal run, or to check someone else's round.
  Triggers: "run the next goal round", "ground a goal", "open a round", "what should
  this goal do next", "resume the goal run", "review this round", "check these
  dispositions", "close the round", "the goal trail says", any request to work under
  work/orchestration/goals/.
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Agent]
user-invocable: true
metadata:
  kind: workflow
---

Before executing this skill, read `.agentic-mbse/claude.md` in Claude Code or `.agentic-mbse/codex.md` in Codex. Resolve supporting paths from this skill’s installed directory; keep generated outputs in the project or a temporary directory. Read referenced skills from `.agents/skills/<name>/SKILL.md` when their guidance is needed.


# Run Goal

A goal is a grounded question pursued in rounds. A round is one agent's bounded attempt at one strategy, running bounded tasks through the native workflows and ending in a written result. Review depth follows the concrete risk triggers in `GOAL_RUNBOOK.md` § Review scope and evidence reuse.

This file names the roles, picks the mode, and gives dispatch guidance. The procedure lives in `work/orchestration/GOAL_RUNBOOK.md`; the decisions behind it live in the goal-layer decision record (`GOAL_RUNBOOK.md` § The decisions behind this). A human operator and an agent follow the same runbook.

## Three roles

- **Operator** — sets the question and holds the gates. Grounds the goal, rules on reserved gates, and closes.
- **Round agent** — pursues one strategy, scopes and coordinates bounded tasks, writes the result.
- **Fresh reviewer** — a session that did not do the work. Checks the named uncertainty when independent review is required. A review can cover study dispositions and round assurance without separate sessions.

Which role you are in decides which section you read. `GOAL_RUNBOOK.md` § What "fresh" means defines the boundary, says who obtains the reviewer on each path, and gives the agent its move when it cannot start a session — read it before either review mode.

## Pick the mode

| Mode | When | Go to |
|---|---|---|
| `ground` | No `goal.md`, or it is still `draft` | `GOAL_RUNBOOK.md` § Grounding a goal |
| `round` | A grounded goal, and either no open round or an open round with work left | § Opening and closing a round, then § Running one task |
| `checkpoint` | A study reading with proposed dispositions, before any semantic follow-up | § The pre-execution disposition checkpoint |
| `review` | A round result is written | § The fresh review |

If `trail.md` shows a `T-00N start` with no return and no stop, the run was interrupted: go to § Resuming an interruption before anything else.

To tell whether a round is open, read `trail.md`'s headings — `GOAL_RUNBOOK.md` § Opening and closing a round gives the rule.

## Name the goal directory

`work/orchestration/goals/<goal-slug>/`, holding `goal.md`, `trail.md`, and `learnings.md`. Confirm the slug with the operator before creating it. Templates are at `work/orchestration/goal-templates/`; copy them rather than writing the files from scratch.

## Dispatch patterns

Follow the runbook’s task parallelism and freshness rules.

### Model changes

Read `modeling_project/REQUIREMENTS.md` and the design-choice pattern (`GOAL_RUNBOOK.md` § Grounding a goal says where it is) before grounding or dispatching a model-changing goal. Follow the design-choice steps in `GOAL_RUNBOOK.md` and `MODELING_PROCESS.md`; carry the applicable requirements and intended design choices into worker/reviewer briefs. Automatic sizing and changes to which quantities are chosen or calculated require explicit design reasoning and applicable review, even when pursuing an already approved quality target.

For a single work item, follow `modeling_project/MODELING_PROCESS.md`. Read only the stage instructions needed for the current task: the stage's installed skill. Any stage can be brief or skipped when its responsibility is already satisfied or does not apply; cite that evidence or reason in the native record. Keep native PM metadata and applicable executable validation, using the project’s prescribed launcher (`uv run` unless the project names another). Review triggers are in the runbook.

The main agent may execute directly or delegate bounded work. For eligible parallel tasks, use fresh workers with self-contained briefs: Claude Code `Agent` with `subagent_type: "general-purpose"`; Codex `spawn_agent` with `fork_turns: "none"`. Supply the exact task, entry files/sections, original evidence, shared interfaces, file ownership, and expected return. Workers preserve each other’s edits. The round agent owns the trail and integrates sequentially after workers return. Deposit briefs under `evidence/`; do not load the whole goal or all stages into each worker.

### Research

Start with internal sources: `knowledge/SOURCE_INDEX.md` (registered sources), `knowledge/KNOWLEDGE.md` (domain insights), and `knowledge/research/` (prior research). Use the research procedure the project's instructions name; otherwise `/research` and `/manage-sources`.

When external sources are needed, execute the research procedure directly or delegate independent requests to fresh agents: Claude Code `Agent` with `subagent_type: "general-purpose"`; Codex `spawn_agent` with `fork_turns: "none"`. A delegated brief names the exact question, entry sources, original evidence, and return budget; deposit it at `evidence/`. Apply any source-quarantine rule the project states before any fetch. The main agent remains free to use research skills itself.

### Fresh critics

When a risk trigger or reserved gate requires independent review, spawn a fresh agent (Claude Code `Agent`, `subagent_type: "general-purpose"`; Codex `spawn_agent`, `fork_turns: "none"`) using the bounded brief contract in `GOAL_RUNBOOK.md` § Review scope and evidence reuse. Deposit the prompt under `evidence/` before dispatch; a separate commit is unnecessary. Reuse valid review evidence and the same reviewer for changed lines. If a required fresh review cannot be obtained, park its dependent work using § What "fresh" means. A study administrator is optional unless the owner requests a cold-record reading.

## Then go here

- **`work/orchestration/GOAL_RUNBOOK.md`** — the procedure, stage by stage. Read the section for your mode before writing anything.
- **`work/orchestration/goal-templates/`** — the three copyable files.
- **The goal-layer decision record** (`GOAL_RUNBOOK.md` § The decisions behind this) — why the layer is shaped this way. Records 001–007.
