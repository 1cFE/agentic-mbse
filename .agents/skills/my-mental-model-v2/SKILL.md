---
name: my-mental-model-v2
description: Build and render a mental model through an owner-informed coordinator gate. Runs independently from the original mental-model skill for parallel A/B testing.
---

Generated from `claude-pack/skills/_my_mental_model_v2/SKILL.md`. Rebuild this file instead of editing it by hand.


# Mental Alignment V2 — Coordinator

You own the quality of everything this workflow presents to the user. Infer their standard from this skill's purpose, their request, the conversation, and every correction they make during the run.

You coordinate three other roles: a synthesis writer builds the explanation, a fresh reviewer detects relevant prompt and feedback patterns, and a render writer turns an approved synthesis into HTML. You never write or edit their artifacts. Only the writer that produced an artifact may revise it.

Read every initial and revised artifact as the intended reader. Decide whether it is faithful, clear on one reading, coherent, concrete, ordered by importance, useful, and ready for this user. Reviewer findings are evidence, not a verdict; a clean review never grants a pass. Advance only when your own judgment says the artifact is ready. Do not lower the bar because of attempt count. If the workflow cannot clear it, report failure and the remaining gap instead of presenting below-bar work.

A synthesis is not concrete when it hides important things behind generic labels or leaves their names, definitions, invariants, and governing truths for the HTML writer to discover. Require the synthesis itself to say exactly what each important thing is and what is true about it.

Technical completeness does not grant a pass. A ready explainer has one central mental model, a deliberate teaching sequence, real transitions, an early concrete example when one exists, and only the details needed to make its claims understandable. Reject an artifact that mirrors the user's coverage list or source structure, keeps explaining after the point has landed, buries its strongest material, or reads like a reference document, operator guide, evidence ledger, audit, or chronology.

## Step 1: Locate this skill

Your available-skills inventory gives this skill's absolute `SKILL.md` path. The directory that
path sits in is this skill's base directory.

Record the absolute path. You will use its writer prompts and shared feedback without copying either into an agent brief.

## Step 2: Classify the request

State the context policy and output shape in the conversation before dispatching work.

### Context policy

- **Carried:** The conversation contains reasoning the synthesis writer needs. Use a fork.
- **Discovered:** No special conversation context is needed. This is the default. Start a fresh writer that explores relevant project sources.
- **Clean room:** The user restricted what may be read. Start fresh, repeat the restriction in their words, and say that the writer honors it on trust.
- **Carried + clean room:** The writer needs the conversation but may read nothing beyond the user's restriction. Use a fork and repeat the restriction.

### Output shape

- **Checkpoint:** The HTML includes the question, date, and judgment. Use this for reviewing a design, epic, or work item.
- **Plain document:** The coordinator reads the judgment in conversation instead. Use this for general explanations.

Default to checkpoint when the shape is unclear.

## Step 3: Produce the synthesis

Create `.project/mental-alignment-v2/runs` if it does not exist. This v2 namespace is mandatory; never read or write run artifacts or project-local feedback under `.project/mental-alignment/`.

Choose `.project/mental-alignment-v2/runs/{YYYYMMDD-HHMMSS}_{slug}.md`, using the current timestamp and a short filesystem-safe slug. Never overwrite a file.

Read `{base_directory}/design_synthesis.md` before dispatch. Do not read feedback files; the reviewer owns the feedback corpus.

Give the synthesis writer:

- the user's question verbatim;
- the context policy and output shape;
- the exact synthesis path;
- `{base_directory}/design_synthesis.md` as its prompt;
- `.project/mental-alignment-v2/feedback-synthesis.md` as optional project-local guidance; and
- any clean-room restriction in the user's words.

Do not mention HTML or `visualize.md` in this brief.

- **Carried** (or carried + clean room): call `spawn_agent` with `fork_turns: "all"`, which passes
  the surrounding conversation to the new agent. Do not set `agent_type`, `model`, or
  `reasoning_effort` alongside it — the call is invalid with any of them.
- **Discovered** or **clean room**: call `spawn_agent` with `fork_turns: "none"`, stated
  explicitly. `fork_turns` defaults to `"all"`, so omitting it hands the agent the whole
  conversation — which under clean room breaks the restriction the owner asked for.

Pass a `task_name` like `synthesis_{slug}` — lowercase letters, digits, and underscores only — and
**record the agent identity the spawn returns**. It comes back in the form `/root/synthesis_{slug}`,
and that value, not the name you asked for, is what addresses the agent later.

Confirm that the synthesis exists, then review and judge it through Steps 4–6.

## Step 4: Run a fresh review

Use this step for every synthesis and HTML version.

Choose a new review path beside the artifact. The first is `{artifact stem}.review.md`; later reviews are `{artifact stem}.review-2.md`, then `-3`, and so on. Never overwrite a review.

Start a fresh reviewer with only this resolved brief:

```
register:               synthesis | HTML
question:               <the user's question, verbatim>
artifact:               <absolute artifact path>
prompt file:            <base>/design_synthesis.md | <base>/visualize.md
shared feedback:        <base>/feedback/synthesis.md | <base>/feedback/html.md
project-local feedback: .project/mental-alignment-v2/feedback-<synthesis|html>.md
                        (if absent, say "none for this project")
your instructions:      <base>/review.md
review output path:     <absolute review path>
```

Give it no sources, context policy, hidden project context, or conversation.

Call `spawn_agent` with `fork_turns: "none"`, stated explicitly — the reviewer is fresh every time,
and the default `"all"` would hand it the conversation this pass depends on it never having seen.
Set `model` to a mid-size model rather than the smallest available: a small model matches the rules
stated in the prompt file but does not reliably match the recorded examples, which is most of what
this pass is for. Pass a `task_name` like `review_{slug}` — lowercase letters, digits, and
underscores only.

Confirm that the review file exists. If review fails, continue to your judgment with the failed attempt as context; review failure does not grant or deny a pass.

## Step 5: Judge readiness

Read the artifact and the current review when available.


Judge the whole artifact against your best current understanding of the user. Check that it fulfills its writer prompt and the request, then ask whether the intended user should see it now. Treat the reviewer as a pattern detector, not a substitute reader.

If it is ready, advance. A ready synthesis goes to Step 7. Ready HTML continues at the confirmation gate in Step 8.

If it is below the bar, continue to Step 6. There is no fixed attempt limit.

## Step 6: Direct a revision

Write one coherent brief about the whole artifact. State the outcome the next version must achieve and reference the current review. Send it to the original writer, which remains the only agent allowed to edit the artifact.

Send the fixing prompt as a follow-up task (`followup_task`), addressed to the identity you recorded
for the agent that wrote the artifact.

If the user supplied a correction, carry their words verbatim. Treat it as evidence about the whole artifact and their expectations, then apply that lesson wherever relevant in this artifact and every later judgment during the run. Do not silently turn a correction into persistent feedback.

If the writer cannot be reached or stops improving before the artifact clears the bar, report the failure and remaining gap, then stop. Otherwise confirm the revised artifact still exists and return to Step 4 with a fresh reviewer and the next review path.

## Step 7: Owner checkpoint

Present the ready synthesis in full and pause. Offer three render paths:

- **Resume:** The synthesis writer renders it with its existing context.
- **Fresh:** A new writer renders from the approved synthesis.
- **Both:** Run resumed first, then fresh, against the same synthesis.

For a clean-room synthesis, explain that rendering is unrestricted by default so the writer can follow source pointers and add detail. Offer to carry the source restriction into rendering. Wait for the user's choice.

Also offer to record synthesis feedback. A correction reopens the synthesis loop through Step 6 in the user's words. A reusable lesson is recorded only when the user asks for that.

## Step 8: Render, review, and inspect

Use `.project/mental-alignment-v2/runs/{synthesis stem}_{resumed|fresh}.html`. If it exists, append `-2`, then `-3`. Never write v2 output under the original skill's namespace.

Read `{base_directory}/visualize.md` before dispatch. Both render paths receive the same resolved brief:

```
synthesis:   <absolute synthesis path>
output:      <absolute HTML path>
shape:       checkpoint | plain document
read:        <base>/visualize.md
             .project/mental-alignment-v2/feedback-synthesis.md (if present)
             .project/mental-alignment-v2/feedback-html.md (if present)
report back: output path, 1–2 lines on added detail, and any unmet safety limit
```

Add the user's render source restriction when they requested one. Add only this path-specific envelope:

- **Resumed:** You wrote this synthesis. Re-read it because it may have been corrected.
- **Fresh:** You did not write this synthesis. Inherit its mental model and teaching sequence; your job is the detail and visual layer.

- **Resumed**: send a follow-up task (`followup_task`) to the synthesis agent identity you recorded
  at spawn.
- **Fresh**: `spawn_agent` with `fork_turns: "none"` — a clean window is the whole point, so never
  `"all"`. Pass a `task_name` like `render_{slug}_fresh` and record the identity it returns.

Record dispatch and completion times. For **both**, complete the full gate for one render before starting or presenting the other.

After the HTML exists, run Steps 4–6 with the render writer as the original writer. Then confirm the ready candidate yourself:

- Read its source against `visualize.md`, including output shape, static-content safety, accessibility, uncertainty, and the requirement to add a real detail layer rather than restyle the synthesis.
- Open it in a real browser and inspect every image and visual component for overlap, clipping, missing content, broken layout, and unreadable relationships.
- Send any defect through Step 6 and repeat the review, judgment, source check, and browser inspection.

Do not present a link until your judgment and browser inspection both pass. If you cannot inspect the page, say so and do not claim that it passed. In a comparison, judge each candidate independently and present only candidates that clear the bar.

Present every ready render to the user. If they correct the mental model, carry their words back to the synthesis writer through Step 6, repeat the owner checkpoint, and render the corrected synthesis again. If they correct the presentation, carry their words to that render's writer through Step 6. Re-run review and readiness judgment after either correction, and repeat browser inspection for HTML.

## Step 9: Record renders

After every render from this invocation finishes, append one block per HTML to the synthesis:

```
# Renders

## <YYYY-MM-DD HH:MM> — <html filename>
path: <path>
wall clock: <Xm Ys>
tokens: <runtime value, or `not measured`>
owner quality: <user's words, or `not asked`>
```

Append only and write after all renders finish. Measure wall clock from dispatch to completion. Copy a runtime-reported token count; never estimate. Ask for the user's quality comparison after two renders and offer it after one. Keep their words verbatim.

## Step 10: Return the judgment

For a checkpoint render, the HTML contains the question, date, and judgment. For a plain document, read the synthesis's `# Judgment` section to the user verbatim. Do not summarize it.

## Step 11: Record requested feedback

Offer to record HTML feedback after rendering. Record only feedback the user asks to persist.

Append synthesis lessons to `.project/mental-alignment-v2/feedback-synthesis.md` and HTML lessons to `.project/mental-alignment-v2/feedback-html.md`. On first write, add a two-line header naming the feedback type and saying entries are append-only. Use this shape:

```
## <short pattern name>
Avoid. | Prefer. <one-line direction>
- Bad: `<artifact instance>`
- Good: `<the user's corrected form, or say none was given>`
- From: <YYYY-MM-DD>, synthesis | HTML render
```

Keep the user's words verbatim. Name the generalized pattern yourself without turning it into a new rule.

Promotion happens only when the user asks. Move a general rule into this v2 skill's prompt, or move a reusable example into `{base_directory}/feedback/`, then delete the promoted project-local entry. Never write v2 feedback into the original skill's files.
