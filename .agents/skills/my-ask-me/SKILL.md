---
name: my-ask-me
description: Ask your questions the right way. The user invoked this because the default way agents ask — several at once, no context, no options, no opinion — doesn't work for them.
---

Generated from `claude-pack/commands/_my_ask_me.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Ask Me Command

**Purpose:** Ask your questions the right way. The user invoked this because the default way agents ask — several at once, no context, no options, no opinion — doesn't work for them.
**Input:** Optional topic to scope the questions to.
**Output:** No artifact. Decisions from the user, applied to the work in hand.

## First, work out what you actually need to ask

List every open question — requirements, design, scope, anything you'd otherwise guess at.
Then cut it down:

- Drop what you can answer yourself by reading the code or the existing artifacts.
- Drop what doesn't change the work — if every reasonable answer leads to the same result, pick
  one and say so later.
- Order what's left so the questions that change other questions come first.

Tell the user how many are left, then ask the first one.

## Then ask them one at a time

**One question per message. Wait for the answer before asking the next.**

Head each one `Q1 of 5`. Then give:

- **The question**, in one line.
- **Context** — what's going on and why this is open. Enough that they can decide without going
  and reading the code themselves.
- **What it changes** — what happens differently depending on the answer.
- **The options** — each with a real pro and con. The pros and cons are how they see why you're
  unsure, so make them honest.
- **Your recommendation**, and the reason for it.

Write it plainly. Short sentences, no jargon you haven't defined on the spot, no tag names or
coined terms. If a question needs a diagram or a code sketch to be answerable, use `/show-me`.

## As answers come in

An answer often settles more than the question you asked. After each one, re-check the
remaining questions: drop the ones now answered and say you dropped them, and add any the
answer opened up. Update the count when it changes.

When you're done, list the decisions in a few lines and carry on with the work.

User-provided arguments are supplied when this skill is invoked.

