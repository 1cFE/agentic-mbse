<!-- agentic-project-init codex rules begin -->
# AGENTS.md

Generated from `claude-pack/rules/` and `codex-overrides/rules/`. Rebuild this file instead of editing it by hand.

## From `capture-fidelity.md`

# Capture Fidelity

Four laws for the chat → artifact → artifact pipeline, where every hop is an agent writing
something a later agent treats as ground truth — honest about where its authority came from.

**Budget: this rule stays ≤ ~40 lines of substance.** A correction lands as a sharper
existing law, never as a new one — the ratchet this rule exists to stop applies to it too.

**Scope.** These laws govern decision-carrying items — settled lists, requirements, ground
rules, non-goals, referents — never ordinary prose. Enforcement is structural where it can
be (provenance, at review) and honest best-effort where it cannot (surfacing; the first
chat → concept hop, whose only checker is the owner reading the capture).

## 1. Provenance — mark who decided

Authority comes from the source, not from being written down. Grade every decision-carrying
item by who decided it, and preserve the grade across every hop.

| register | vocabulary | settled-eligible |
|---|---|---|
| shaping (concept, epic, settled lists) | `[OWNER-VERBATIM]` (quote required) `[OWNER]` `[AGENT]` `[INHERITED: src]` | owner grades only |
| spec (requirements) | `[HARD]` `[NEED]` (owner-stated) `[INFERRED]` `[INHERITED]` | `[HARD]`, `[NEED]` |
| payload (any artifact) | `[EXAMPLE]` / `[REFERENT]`, or force stated in words | force must be stated |
| design (bets, decisions) | agent-grade by construction | n/a |

**The settled rule.** Only owner-*originated* items — the owner said it, not merely
approved it — may be marked settled / do-not-relitigate. An approved agent recommendation
stays `[AGENT] (ratified by owner, date)`; challenge it by re-deriving against its recorded
reasoning, where an `[OWNER]` item is challenged by asking the owner. Inherited items are
never settled by default and, like agent-grade items, challengeable when evidence warrants.

**Absorb mapping (concept → spec).** `[OWNER-VERBATIM]` → `[NEED]` carrying the quote or a
path-cite to the concept; `[OWNER]` → `[NEED]`; `[AGENT]` → `[INFERRED]`; `[INHERITED: src]`
→ `[INHERITED]`, source carried. An inferred outcome is `[INFERRED]`, never `[NEED]`.

## 2. Compression — the owner's payload survives

Owner-given examples, referents, numbers, and named standards are payload: they survive
capture verbatim or by path, at the owner's emphasis, with their force marked — an example
illustrates the kind (`[EXAMPLE]`), a referent is the bar to match (`[REFERENT]`). An example
must not harden into the required form, nor a referent soften into a vibe. Unclear force → ask.

## 3. Correction — shrink or amend, never accrete

A correction deletes or amends the corrected content at the owner's emphasis. Deleted means
deleted: no compensating prose about the non-requirement, no emphasis markers beyond what the
owner expressed. A rejected path that must be recorded gets one line in its designated home
(Non-Goals, or a design's rejected-alternative note), phrased as a decision record, never as
an instruction to future agents. Governs every artifact write, memories and handoffs included.

- BAD: suggestion → rejection → "WE MUST NOT \<suggestion\>". The prohibition anchors future
  agents on the suggestion in a way the owner never intended.
- GOOD: suggestion → rejection → "Out of scope: \<suggestion\> is not required because
  \<reason\>". Context and color along a well-worn agent reasoning path.

## 4. Surfacing — never resolve a premise conflict silently

Trigger: following a recorded rule would work against the recorded goal, or genuine surprise
produces evidence against a premise the plan rests on. Response: surface it — to the owner
when reachable, otherwise loudly in the artifact, with dependent conclusions parked. Never
resolve it silently, in either direction.


## From `context-loading.md`

# Context Loading

## Before Starting Non-Trivial Work

1. **Read `.project/CURRENT_WORK.md`** — what is active right now and what is up next
2. **Skim `.project/product/INDEX.md` if present** — the product's implemented promises; open
   only the entries relevant to your task. An absent or empty ledger just means none recorded.
3. **Read the newest completions in `.project/completed/CHANGELOG.md` if present** — what just shipped, so you know whether the area you are about to touch was just changed. Run the bound rather than reading the file, so the cost is the same at 7 entries and at 70: `awk '/^## \[[0-9]/{n++; p=1} n>5{exit} /^### Deliverables/{p=0} /^---$/{p=0} p' .project/completed/CHANGELOG.md`. It returns the newest 5 entries, heading through `Summary`.
4. **Read the relevant docs** for the area you're working in (check CLAUDE.md for pointers)

## After Completing Work

If you discovered something that would save a future session time:
1. Suggest running `$my-wrap-up` to persist context
2. Or at minimum, update `.project/CURRENT_WORK.md` with the current status

## Durable Knowledge Goes in Project Registers, Not Memory

Before saving to the native memory store, check whether it belongs in a `.project/` knowledge home instead — decisions in `adr/`, product promises in `product/`, discovered behaviors in `execution/`, pack-prompt corrections in `feedback/`. The routing table is in `.project/README.md` under "Knowledge Homes." The memory store is device-local and not owner-reviewed; the registers are git-tracked and durable.

## Don't Re-Research What's Already Documented

Before exploring the codebase to understand how something works, check:
- Project docs (often in `docs/`) for existing documentation
- `.project/research/` for previous deep investigations
- `.project/CURRENT_WORK.md` for recent work that may already cover the area


## From `markdown-formatting.md`

# Markdown Authoring

**One line per paragraph. Never hard-wrap prose.**

When you write or edit any `.md` file — every `.project` artifact (specs, designs, plans, research, handoffs, status notes) and every other markdown file — keep each paragraph, bullet, and heading on a single source line. Do not insert line breaks to wrap text at 80, 90, or any other column width.

A newline in the middle of a markdown paragraph renders as a space anyway. Hard-wrapping buys nothing and costs plenty: it makes the source ugly, makes diffs noisy (one reworded sentence re-wraps the whole paragraph), and makes editing a chore. Let the editor soft-wrap on screen.

- Each paragraph: one line.
- Each list item: one line. (Only break if the item genuinely contains multiple paragraphs.)
- Use blank lines only where markdown needs them structurally — between paragraphs, around headings, around lists and code blocks. Not as decorative padding.


## From `pipeline.md`

# Pipeline Shape

The project workflow runs as a sequence of `$my-*` stages. This is the shape, for orientation.
It is the only place the sequence appears besides `$my-pipeline` — don't restate it elsewhere.
Stages are quality tools, not mandatory ceremony. Use the smallest set of stages that can produce
high-quality, auditable work for the risk in front of you.

<!-- pipeline-shape -->
`research`/`concept`/(`concept_design` → `concept_design_review`) → `epic_plan` → `spec` → `spec_review` → [`product_design`] → `design` → `design_review` → `plan` → `implement` → `audit` → `close` → `pre_pr`

- **Entry follows the question "how well do you understand the problem?"** Not well: shape it
  (`research`/`concept`/`concept_design`); many shippable pieces: `epic_plan`; a single clear
  item: straight to `spec`.
- **`[product_design]`** is optional — for consumer-facing surfaces; runs off a concept
  (shaping tier) or a spec (single item), same function either way.
- **`pre_pr` is the branch gate, run after `close`** — when the item is shippable on its own;
  for items that ship together, run it once at the end of the epic. Never per-phase or mid-item.
- **Reviews pair with their artifact when they add confidence:** `concept_design_review` after
  `concept_design`, `spec_review` after `spec`, and `design_review` after `design`. For minor,
  objectively verifiable fixes, record the verification and continue instead of rerunning a
  reviewer just to replace an old verdict.
- When the owner explicitly invokes `$my-quick-edit`, a small, scoped code change can skip the pipeline. Do not use it for routine documentation or `.project` artifact edits.

**For the full flow and when/how to use each stage, run `$my-pipeline`** (or read
`.agents/skills/my-pipeline/SKILL.md`).


## From `workflow-accountability.md`

# Workflow Accountability

## Before Implementing Non-Trivial Features

If the work touches multiple files, has ambiguous requirements, or will span more than one session:

1. **Requirements must be written down** before implementation starts
   - Use `$my-spec` for the full pipeline, or write an ad hoc requirements/user story doc in `.project/` or the repo root
   - If the user asks to "just build it" without written requirements, flag it: "This seems non-trivial — want me to write a quick spec or requirements doc first so we have something to review against later?"

2. **Multi-session work needs a persistent plan**
   - If implementation will take more than one session, use `$my-plan` to create `plan.md` with checkboxes
   - Do not rely on ephemeral `/plan` mode for work that spans sessions

## During Implementation

1. **Check plan progress before starting**
   - If `.project/active/{feature}/plan.md` exists, read it and resume where the checkboxes stop
   - Do not re-implement completed phases

2. **Check off plan phases as you complete them**
   - Mark checkboxes in `plan.md` immediately after completing a phase
   - Add implementation notes (what changed, issues, deviations) so the next session has context

## After Implementation

1. **Suggest `$my-audit`** after completing all phases of a plan
   - Don't self-certify — the audit catches placeholder code, TODOs, and gaps that the implementing agent misses

2. **Suggest `$my-wrap-up`** when the session is winding down
   - If significant work was done, proactively suggest it: "Want me to run `$my-wrap-up` to persist context for next time?"
   - Don't wait for the user to remember

## General Principles

- **Write things down.** A quick requirements doc beats requirements that only exist in chat history.
- **Persistent artifacts over ephemeral conversation.** Specs, plans, and research docs survive across sessions. Chat doesn't.
- **The spec is the contract.** Implementation should be auditable against written requirements, not against what someone remembers discussing.


## From `working-voice.md`

# Working Voice

How to write when working with the user, and in the artifacts they read.

## Scope

This rule governs your working voice in two places:

- Conversation with the user.
- Internal workflow artifacts they read: specs, designs, plans, research, concept docs, reviews, handoffs, status notes.

It does not govern:

- External-audience explainers. Those have their own guidance.
- What stance a command takes toward its job, like a skeptical reviewer or a faithful requirements-capturer. That stays in the command.
- What sections an artifact has, and what goes in each. That stays in the command.

In short: this rule is about how the prose reads. Not what the task is, and not how the document is organized.

## The method

Write so a tired engineer reads it once, mid-task, and knows what is going on and what to decide.

- **Plain and explicit.** Say the thing. Don't reach for an impressive word when a plain one is exact.
- **One idea per sentence.** If a sentence needs a second read, split it.
- **Lead with the point.** State the situation and the conclusion first. Add the mechanism after, and only as far as the reader needs it.
- **Lead with plain language; anchor the precise term.** Explain a term in plain words the first time you use it. When a precise or established term exists, put it in parentheses so the reader connects the plain idea to the name, like "fitting in stages (the F1 method)." Don't coin a phrase early and then reuse it as if the reader memorized it.
- **Cut caveats that aren't load-bearing.** A correct but irrelevant qualifier buries the one sentence that matters. Leave it out.
- **Keep identifiers out of the flowing prose, but always give a reference.** Don't thread `ClassName.method` through your sentences. But never name code with nowhere to find it. When you point at code, give its location (`clip_discharge.py:47`), not just the bare name. A class or method mentioned without a pointer is a dead end for the reader.
- **Decompose into points; avoid block text.** A dense block is hard to read, especially in a terminal. Most explanation breaks into discrete points, and structure shows how they relate. Reach for bullets, short paragraphs, and line breaks by default — for reasoning, not just for lists of facts. Let the structure mirror the logic so the reader sees the shape at a glance. When you do list parallel facts, lead each with its plain claim and put the reference at the end.

When the subject is genuinely complex, don't compress it into dense jargon. Give the reader a mental model first: a simple frame they can hang the details on. Then add the details against that frame. Build understanding in layers, and let each layer earn the next.

## Precision is the work behind it

You can't write something plainly until you understand it. Vague, hedged, or jargon-heavy prose is usually a sign the writer hasn't done the work, not that the topic is hard. The voice above is the output; this is what it costs.

- **Get the details right before you write them.** Verify a claim against the code, the data, or the source. Confident phrasing is not a substitute for a checked fact, and a fluent wrong claim is harder to catch than an obvious one.
- **Be exact.** Simplifying means choosing the few facts that carry the point and stating them plainly. It never means rounding a real distinction into a false one. If the simpler version erases something that matters, it's wrong, not simple.
- **If you can't explain it simply, find out why.** Either you don't understand it yet, or the thing itself is too complex. Both are worth knowing before you write a word.
- **When you're unsure, say so plainly.** Don't cover a gap with hedging or jargon. Go get the detail, or state in plain words what you don't know.

## Presenting a decision

Walking the user through a decision is the clearest case of good versus bad writing. Use this shape when a decision deserves it. It is an example of the method, not a required template. A small decision gets a sentence. A one-line answer stays one line.

Walk it through in prose. A decision that matters is not handed to the user through the multiple-choice question tool — options stripped to short labels lose the scope and the costs, and those are what the reader needs to decide. Keep that tool for small, well-scoped picks.

The shape: the situation, the crux of the decision, the options and what each costs, then your recommendation and why.

**Bad:**

> Per the conservative per-bin-init plus one-sided-shrink route, the F2 methodology suggests a sequential convex sub-fit to initialize then joint to finish, which de-risks the M0–M3 discharge-ladder failure mode noted above.

Five coined terms stacked into one sentence. The reader can't decode it without rereading everything that came before.

**Good:**

> We have to choose how to fit the curve. Two options. Fitting everything at once (the F2 method) is simpler, but it can settle on a bad answer. Fitting in stages, then refining (the F1 method), is more code but more reliable. I'd fit in stages. A bad fit is expensive to catch later, so the reliability is worth the extra code.

Situation, options with their costs, recommendation with the reason. The precise terms are there, in parentheses, anchored to the plain explanation instead of standing in for it.

## Texture to avoid

These tics make the voice grating even when the content is right. Cut them.

- **Hedging.** Not "this might possibly help in some cases." Say what is true, or say you don't know.
- **False range.** Not "from small scripts to massive systems." Name what it actually covers.
- **"Not just X, but Y."** The parallelism reads as filler. Just state Y.
- **Inflated stakes.** Not "this is critical" or "a game-changer." Say what it does and let the reader judge the weight.
- **Nominalized verbs.** Not "perform a calculation of." Calculate.
- **Em-dash pileups.** One dash in a sentence at most. Usually a period is better.
- **Resume words.** Drop "robust, seamless, leverage, utilize, comprehensive." Use "use," "strong," "thorough," or nothing.

## The test

Before you send a message or save an artifact, ask: would a tired engineer skim it once and know what's going on and what to do? If not, it failed, no matter how complete or careful it looks.


## From `codex-overrides/rules/collaboration.md`

# Codex Collaboration Calls

When calling `spawn_agent`:

- `fork_turns: "all"` inherits the parent agent type, model, and reasoning effort. Do not combine
  it with `agent_type`, `model`, or `reasoning_effort`.
- `fork_turns` defaults to `"all"`, so specifying one of those overrides without setting
  `fork_turns` is also invalid.
- To select an agent type, model, or reasoning effort, set `fork_turns` to `"none"` or a positive
  turn count.
- Use `fork_turns: "none"` for fresh explorer, reviewer, and product-lens agents unless inherited
  conversation history is specifically required.
<!-- agentic-project-init codex rules end -->
