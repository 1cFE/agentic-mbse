---
name: my-learning-test
description: Write real, kept tests to discover how an unfamiliar surface behaves, then feed the learning back into the pipeline. Use when the goal is fuzzy and you are mapping a surface to understand it.
---

Generated from `claude-pack/commands/_my_learning_test.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Learning Test Command

**Purpose:** *Discover* how an unfamiliar surface behaves by writing real tests, and feed the learning back into the pipeline
**Input:** A surface to map (e.g. "how does this library's retry/backoff actually behave under errors?")
**Output:** Real tests in the repo's own test directory + a findings doc in `.project/research/`

## Overview

Use ``my-learning-test`` when the goal is **fuzzy and you're mapping an unfamiliar surface** to
understand how it behaves. You write real tests that pin down the behavior, and you *keep* them —
they become part of the repo's test suite and guard the behavior you just learned. (If instead
you have a clear goal and one specific assumption to confirm with throwaway code, use
``my-spike`` — its output is a scratch script, not kept tests.)

This is the write-code-to-learn counterpart to ``my-research``, which is read-only. Research
reads existing code to understand it; a learning test writes new tests to find out how something
behaves.

When invoked:
- If a surface/question is provided: proceed to Stage 1.
- If none: ask "What surface do you want to map?" and wait.

## Process

### Stage 1: Understand the surface

1. **Frame what you're mapping.** Name the surface and what you want to understand about it —
   the behaviors, edge cases, or contract you're unsure of. A learning test is open-ended by
   nature, but you still need to know what you're trying to learn.
2. **Note the source.** Identify the upstream artifact this serves — the concept, spec, design,
   or epic you paused out of. You'll write the learning back there in Stage 5, so find it now.
   If you can't tell what triggered this, ask the user before probing.

### Stage 2: Locate the repo's real test directory

The durable output of a learning test is **real tests in the repo's own test suite** — never
scratch scripts, never under `.project/`.

1. **Find where this repo keeps its tests.** Inspect the project: look for the existing test
   directory and framework (e.g. `tests/`, `test/`, `spec/`, `__tests__/`, a language-specific
   convention). Match how tests are already organized and named here.
2. **Do not hardcode a path and do not invent one.** Repos differ; use the location this repo
   already uses. If you genuinely cannot find one, ask the user where tests belong.
3. **The findings doc is separate.** It goes in `.project/research/` (Stage 3), not with the
   tests — the tests are the durable artifact, the doc is the investigation write-up.

### Stage 3: Probe by writing real tests, with a living findings doc

Probe how the surface actually behaves — take your time, try different approaches. Write real
tests that exercise the behavior and assert what you observe. As you go, keep a **living findings
doc**, updating it as you learn rather than writing a report at the end.

1. **Write real, runnable tests** in the repo's test directory. They must pass and assert actual
   behavior — not mock-only tests that prove nothing. Each test captures something you learned
   about the surface.
2. **Keep everything reproducible.** A reader must be able to run your tests and see what you saw.
3. **Keep the findings doc** at `.project/research/{YYYYMMDD-HHMMSS}_{topic-kebab-case}.md` with
   this shape (leave the summary blank until Stage 4):

   ```markdown
   # Learning Test: {topic}

   ## Summary of Findings
   <!-- written last, in Stage 4 -->

   ## Question / Goal
   The surface being mapped and what you wanted to understand.

   ## Log
   Living record, appended as you go: each behavior probed, the test written,
   and what it revealed. Reproducible.

   ## Tests Written
   Where the kept tests live (path) and what each one pins down.

   ## Reproduction
   How to run the tests from scratch.

   ## Open Questions / Follow-ups
   What this did not settle.
   ```

### Stage 4: Write the summary, on top

Just before you finish, write a **Summary of Findings** at the *top* of the doc, so the next
reader gets the answer first. Lead with what you learned about the surface and what it means for
the upstream work. Then the supporting detail.

### Stage 5: Close the loop

A learning test that dead-ends in an orphan doc taught the pipeline nothing. Feed the learning
back.

1. **Write a back-reference into the triggering upstream artifact** (the one you found in
   Stage 1). Prefer the spot where the reader meets the question the tests answered — the
   specific decision, bet, or bullet it resolved, so the answer sits in context. If there's no
   such spot, fall back to where that doc type keeps links:
   - spec / design → **Related Artifacts**
   - concept → **Next-Stage Handoff**
   - epic → **Source Documents** (or the item's Required Reading)
2. **Note what the tests revealed and where they live** — e.g. "Learning test mapped the
   library's retry behavior; kept tests in `tests/test_retry.py`; see
   `.project/research/{ts}_retry.md`." The reader should learn the answer from the back-reference
   alone.
3. **If there genuinely is no upstream doc to link**, tell the user there was nothing to link
   and why, so the gap is visible rather than silently skipped.

## Guidelines

### Metadata
For any dated artifact, get metadata the standard way:
```bash
.project/scripts/get-metadata.sh
```
If that script is absent, fall back to `git` for branch/hash and the system date.

### Required Invariants (never violate)
- **Real tests in the real test dir.** The durable output is kept tests in the repo's own test
  location — never scratch scripts, never under `.project/`. The agent locates the dir; no
  hardcoded path.
- **Reproducible.** A reader can run the tests and see what you saw.
- **Summary-on-top, written last.** The doc's first section is the answer, written in Stage 4.
- **Loop closed.** A completed learning test always leaves a back-reference in the triggering
  doc, or tells the user why there was nothing to link.

### Scope
- The tests are real and kept. Write them to the repo's quality bar — they'll guard this
  behavior going forward.
- If you find you only wanted to confirm one known assumption with throwaway code, that's a
  ``my-spike``, not a learning test.

---

**Related Commands:**
- Clear goal, one assumption to confirm with throwaway code → ``my-spike``
- Read-only investigation of existing code → ``my-research``

**Last Updated**: 2026-07-06

