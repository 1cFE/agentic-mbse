---
name: my-orchestrate
description: Given a concept or outcomes document, drive it to implemented, reviewed work through Codex-native pipeline stages.
---


Pack paths in this document are relative to the installed skill directory (the directory containing its SKILL.md), not the shell working directory. Resolve that directory from the skill path in the skill catalog, then resolve pack paths to absolute paths before reading, executing, or passing them to subagents. Quote resolved shell paths. Keep the project working directory; pass it explicitly with --cd when running the orchestration helper.

Generated from `codex-overrides/command-skill-replacements/orchestrate/SKILL.md`. This is a full Codex replacement for the Claude orchestrator command. Rebuild it instead of editing generated output by hand.

# Orchestrate

**Purpose:** Given a concept or outcomes document, take ownership of delivering high-quality implemented work. You are trusted to choose which pipeline stages, reviews, and checks will actually improve the result, then leave artifacts and a decision trail the human can audit afterward.

**Input:** A concept/outcomes doc path or inline outcomes.

**Output:** Pipeline artifacts and code in `.project/`, plus commits when the work and repository state call for them.

## What Matters Most

You are the quality owner for the run. The human is trusting your engineering judgment, not asking you to execute a fixed procedure.

- **Hold the engineering bar.** Do not accept stage output that is vague, untested, placeholder-heavy, or inconsistent with the repository's patterns. Resume the stage with concrete feedback when the work falls short.
- **Stay on intent.** Keep the objective and its broader context visible. Each stage should serve the real outcome, not only produce the next artifact.
- **Choose stages because they help quality.** Invoke a stage only when its output is likely to change the implementation, catch a meaningful problem, or materially increase confidence. Each invocation costs real time and money.
- **Keep context lean.** Read stage final messages first. Read artifacts or code only when you need detail to route, review, or decide.
- **De-risk before building on a shaky bet.** When a stage surfaces an unverified assumption about how something behaves and neither the objective nor your judgment can settle it, insert a de-risking stage before planning on top of it. Run `spike` for a known assumption that needs a throwaway probe; run `learning_test` for an unfamiliar surface that should leave kept tests behind. Feed the finding into the stage that needed it, then continue.

## Stage Selection Policy

The pipeline is a map, not a checklist. Your job is to decide what the work needs, then use the smallest set of stages that can produce high-quality, auditable work.

- **Skip stages that do not buy confidence.** For a small, low-risk change, you may write a spec and self-review it, skip explicit `spec_review`, skip `design`, or go straight to `plan` or `implement` when the requirement is already clear.
- **Do not seek clean verdict artifacts.** A persisted `Revise` verdict is historical evidence. If the finding is minor, localized, and objectively fixed, verify the fix yourself, record the reason, and continue.
- **Rerun a reviewer only for material judgment.** Rerun `concept_design_review`, `spec_review`, or `design_review` when the fix changes system shape, requirements, acceptance criteria, architecture, interfaces, security posture, data model, migration behavior, or another decision where an independent review could change the outcome.
- **Use design when architecture is real.** Run `design` for cross-cutting changes, new interfaces, storage changes, user-visible flows with meaningful state, or decisions that future implementers need written down. Skip it for direct mechanical edits where the implementation path is obvious from the spec and existing patterns.
- **Record skipped stages.** Put a short note in the next artifact, commit message, or final summary explaining what you skipped and why. The human should be able to audit your judgment without paying for redundant stage calls.

## Tools

Delegate each stage through the Codex helper, but keep the whole wait inside one host execution
cell. For every `run` or `resume` call:

1. Send one concise launch update that names the stage. Send no commentary about unchanged state.
2. Choose the helper timeout `T` in seconds and pass it with `--timeout T`. Set the enclosing
   `functions.exec` yield to `T + 30` seconds. The first-line execution pragma requires the
   calculated literal milliseconds; for the default `T = 600`, use
   `// @exec: {"yield_time_ms": 630000}`.
3. Inside that single `functions.exec` cell, call `tools.exec_command` with the normal helper
   command and a quoted heredoc containing the stage input. If it returns a terminal session id,
   drain that same session with `tools.write_stdin` inside the cell. Internal drains may repeat
   because they do not return control to the parent model. Cap each internal drain at 300 seconds
   and at the remaining outer deadline. Return the terminal output with `text(result.output)`.

The cell body follows this shape:

```javascript
const helperTimeoutSeconds = 600; // Use the same literal passed to --timeout.
const startedAt = Date.now();
const outerDeadlineMs = (helperTimeoutSeconds + 30) * 1000;
let result = await tools.exec_command({
  cmd: "<helper run/resume command with --timeout T and a quoted heredoc>",
  yield_time_ms: Math.min(outerDeadlineMs, 30000),
  max_output_tokens: 10000,
});

while (result.session_id !== undefined) {
  const remainingMs = outerDeadlineMs - (Date.now() - startedAt);
  if (remainingMs <= 0) {
    throw new Error("Codex stage exceeded its helper timeout and cleanup allowance");
  }
  result = await tools.write_stdin({
    session_id: result.session_id,
    chars: "",
    yield_time_ms: Math.min(remainingMs, 300000),
    max_output_tokens: 10000,
  });
}
text(result.output);
```

Use these helper command shapes inside the cell:

```bash
../../../.codex/scripts/orchestrate-stage-codex.sh run <stage> --timeout T <<'ARGS'
...
ARGS

../../../.codex/scripts/orchestrate-stage-codex.sh resume <session_id> --timeout T <<'MSG'
...
MSG
```

Normally `functions.exec` returns only when the helper is terminal. If the outer cell yields early,
call `functions.wait` only once on that cell for the remaining deadline. Do not poll or emit a
no-news update. If that one fallback yields again, stop the cell with `functions.wait` using
`terminate: true`, report a host compatibility failure, and do not route the incomplete stage
forward.

Do not schedule notifications, timers, control yields, or model-visible status checks. Keep JSONL
and stderr in their retained files; do not forward their events into the main conversation.

Each call returns compact JSON:

- `session_id`: the Codex thread id to resume.
- `result`: the stage's final message.
- `raw`: the JSONL log path.
- `stderr`: the stderr log path.
- `is_error`: whether Codex reported a failed turn.

The helper maps pipeline stages to Codex skills. For example, `spec` invokes `$my-spec`, `spec_review` invokes `$my-spec-review`, and `pre_pr` invokes `$my-pre-pr`.

## Running the Pipeline

1. **Orient.** Read the objective. Use the entry questions in the pipeline skill (how well is the problem understood; is there a UX to settle; how big is the impact; does it split into shippable pieces) to decide where to enter and whether this is a single item or an epic.
2. **Read `$my-pipeline`.** Use it as the canonical map for stages, branches, and paired reviews. Apply the stage selection policy above before invoking each stage.
3. **Start each stage with enough context.** Include the objective, relevant prior artifacts, explicit decisions already made, and the stage outcome you need.
4. **Handle questions by resuming.** If a stage asks questions, answer from the objective and your judgment. If the objective cannot settle a question, tell the stage to choose and record the decision.
5. **Run review loops deliberately.** Feed must-fix findings back to the producing stage. For minor, objectively verifiable findings, verify the correction yourself and continue. Do not chase a review loop past about two rounds without a clear reason.
6. **Commit decisions when appropriate.** Keep commits focused, with subjects that name the decision or completed stage.
7. **Finish at the right boundary.** Leave `$my-close` and the post-close `$my-pre-pr` branch gate to the human unless explicitly asked.

## Stage Result Protocol

A stage result has one of two shapes:

- It asks questions. Answer them in one resume message.
- It finishes and ends with `ARTIFACT: <relative path>`. Read that artifact when you need to route or review the next stage.

If a stage result is incomplete, ambiguous, or misses the requested outcome, resume the same session with specific feedback. Do not route a weak artifact forward just because it exists.

## Sandbox Defaults

The helper chooses the least needed sandbox for fresh stage runs:

- `read-only` for reference and review-only stages.
- `workspace-write` for artifact-producing or implementation stages.
- `danger-full-access` is never a default. Use it only when the user explicitly approves that risk.

Resume calls do not pass `--sandbox` because the current Codex CLI resume path does not accept the same flags as a fresh run.

## Related

Pipeline reference: `$my-pipeline`.

Common inputs: `$my-concept`, `$my-concept-design`, `$my-research`.

Common stages: `$my-concept-design-review`, `$my-epic-plan`, `$my-spec`, `$my-spec-review`, `$my-product-design`, `$my-design`, `$my-design-review`, `$my-plan`, `$my-implement`, `$my-audit`, `$my-pre-pr`.

De-risking stages: `$my-spike`, `$my-learning-test`.

Mechanism: `../../../.codex/scripts/orchestrate-stage-codex.sh`.
