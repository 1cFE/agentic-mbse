---
date: 2026-07-03T11:21:57-07:00
researcher: Claude
topic: "What the agentic-project-init refactor actually changed, and which deltas apply to our commands"
tags: [research, commands, voice, artifacts, mental-alignment]
status: complete
last_updated: 2026-07-03
---

# Research: The workflow-v2 delta, and what applies to our commands

**Date**: 2026-07-03
**Researcher**: Claude
**Research Type**: Prompt / artifact quality — delta analysis

## Research Question

`~/agentic-project-init` went through a refactor. What did it actually change, and which of those
changes are relevant to our shipped MBSE commands (`claude/commands/`)? The goal is not to port
wholesale — it is to identify the deltas so we can pick what matters.

## Summary

- The refactor was **not** about adding capability. It was about making artifacts and prompts
  communicate *what matters* — leaner, plainer, less formal. One lesson drives all of it (their own
  words, `~/agentic-project-init/.project/research/20260419-081514_artifact-pipeline-alignment-review.md:446`):
  > A good artifact is not the one that says the most. It is the one that lets the next reader recover
  > the intended mental model fastest and safest.
- The concrete deltas are a small set of **portable primitives**: a top-level alignment snapshot, lean
  cores over exhaustive templates, output budgets, Key Bets, a Settled/Unsettled/Rejected handoff block,
  and a plain-first voice that demotes compliance jargon.
- **The trap I fell into first, corrected here:** the source *also* contains long, formal rule-blocks
  (implement-side fail-loudly, audit-side certification checkboxes). Those are the opposite of the
  refactor's point — the source's own review calls implement "machinery … optimize for concise execution
  trace" and warns its tracking guidance "risks compliance theater." They are **not** deltas to port.
- **The real work is a balance, not a strip.** A lot of our formalism is load-bearing — the PM engine
  derives state from frontmatter, and SV-XXX / `traceability_matrix.csv` / PR-XXX are the deterministic
  verification backbone. Those stay. The lean/voice pass targets the **prose and template sections** that
  exist only for a reader, not the structure the engine actually parses.

## The core model: each stage reduces a different ambiguity

The source's framing (`...alignment-review.md:37`) is the useful lens. Each artifact has two jobs: align
the human, and hand a fresh agent enough to continue cold. An artifact fails when it says a lot but lets
the reader lose the mental model in the enumeration.

Two failure modes the refactor names:
- **Bloat / low altitude** — a spec that reads like a requirements dump, a design that lists components
  before the reader knows the strategy, a plan that reads like an implementation diary.
- **Formality over framing** — compliance language (RFC-2119 / EARS) as the organizing principle instead
  of plain rationale, so the *why* is buried under the *shall*.

## The deltas — the portable primitives

These are the moves worth taking. Each is small and additive-to-clarity, not additive-to-length.

| # | Delta | What it is | Applies to us? |
|---|-------|-----------|----------------|
| 1 | **Alignment snapshot** | Every artifact opens with: why it exists · what it settles · what's open · what the next stage decides (`...alignment-review.md:373`) | Yes — none of ours lead with this |
| 2 | **Lean core over exhaustive template** | "Four things and no more"; depth tracks input; don't pad a thin item (`_my_spec.md:13`) | Yes, strongly — spec-model trends toward MR-XXX dumps |
| 3 | **Output budgets** | Hard line caps as anti-slop pressure (concept ≤300, design ≤250) | Yes — design-model / audit-models have no length discipline |
| 4 | **Key Bets + rejected alternatives** | Surface the load-bearing assumptions and what wasn't chosen | Yes — design-model has a flat "Design Decisions" list |
| 5 | **Settled / Unsettled / Rejected block** | The trace primitive at the end of each artifact (`...alignment-review.md:406`) | Yes |
| 6 | **Plain-first voice** | Lead with plain language; demote compliance jargon to optional (`...alignment-review.md:242`) | Yes — ours are procedural and compliance-toned |
| 7 | **Cut command procedural drag** | Make conditional offers conditional; skip ceremony the earlier stages already resolved (`...alignment-review.md:353`) | Yes — our commands carry long skill preambles + always-on offers |
| 8 | **Main doc + appendix** | Push file-by-file evidence to an appendix or a research doc; keep the main artifact for comprehension | Yes |

The delivery detail: in the source these are reinforced by a shared `working-voice.md` rule and
reader-comprehension checks in the review commands. We have no rules layer — we have skills. If we want the
voice to have a referent, a `working-voice` **skill** installed via `init` is the natural fit. That is a
mechanism choice, not a delta in itself.

## The balance: load-bearing vs. reader-only, per command

This is the crux. For each command, what the engine needs stays; what exists only for a reader is where the
lean/voice pass applies.

**spec-model**
- *Keep (load-bearing):* frontmatter (PM engine reads Status/ID/Epic); MR-XXX (feeds design + SV-XXX);
  the SV-XXX entries it creates in `VALIDATION_MATRIX.md`.
- *Lighten (reader-only):* the exhaustive multi-section process and the tendency to a flat MR-XXX dump.
  Add an alignment snapshot and a lean core; group requirements by decision area; make the requirement
  *rationale* foreground, the enumeration secondary.

**design-model**
- *Keep:* the working prototype + validation report — in our system this *is* the design gate, not
  formality (domain-specific, stays).
- *Lighten:* no length cap today; the flat "Design Decisions" list. Add a line budget, add **Key Bets**
  (the assumption and what breaks if it's false), and a "what the plan must decide next" handoff.

**plan-model**
- *Keep:* validation checkpoints and completion gates tied to the levels / SV-XXX.
- *Lighten:* the verbose per-phase template. Reduce each phase to goal · why now · key actions · exit
  checks · assumption under test; add a one-screen top summary (critical path, first proof point);
  ban exhaustive file-by-file checklists unless coordination-sensitive.

**implement-model**
- *Keep:* understand-before-acting and deviation tracking.
- *Lighten:* this is machinery — make the exploration offer and phase-choice confirmation *conditional*
  (skip when the user said "all" or "resume"), and standardize a compact execution journal. **Do not** add
  the source's long fail-loudly rule-blocks — they pull the wrong way.

**audit-models**
- *Keep:* almost all of it. Numerical accuracy, SV-XXX evaluation, traceability, PR-XXX/AD-XXX compliance
  are the deterministic verification backbone — load-bearing, not formality.
- *Lighten:* lead with a short verdict/summary snapshot instead of a wall of obligations. **Do not** add
  checkbox "certification" — our verification model (SV-XXX + traceability + the validate pyramid) is
  already richer than the source's checkbox marking, and the engine ignores body checkboxes by design.

**review-model**
- *Keep:* it already exists and is advisory with a verdict in frontmatter (per `workflows.md:212`).
- *Optional, secondary:* the source's review-not-artifact boundary and finding IDs would sharpen it, but
  this is lower priority than the spec/design/plan lean pass.

## What NOT to port (and why)

- **Implement-side fail-loudly / anti-slop rule-blocks** — long and formal; the source itself treats
  implement as machinery to keep concise. Detection of fabricated values already lives in audit (Numerical
  Accuracy) and the validate pyramid.
- **Audit-side "certify by marking checkboxes"** — a regression here. Our state is derived from files +
  frontmatter + SV-XXX; marking body checkboxes would create a second, drifting source of truth that our
  "frontmatter wins, body is rendered" design (`workflows.md:304`) exists to prevent.
- **Whole new commands as a bundle** (epic/orchestrate/concept/close/product-design) — out of scope for a
  refresh whose goal is *leaner*, not *more*.

## Why our formalism is load-bearing (the constraint that shapes the balance)

Our system's governing principle (`.project/concepts/architecture-redesign/workflows.md:395`): state queries
are deterministic Python; state changes are agent-guided; it is a toolkit, not a pipeline (no structural
gates). Consequences that bound the lean pass:
- Work-item state is **derived** from the file system + `spec.md` frontmatter `Status` (`state.py:86`). The
  frontmatter is not decoration — the dashboard reads it.
- Verification is **registry-based**: SV-XXX (`VALIDATION_MATRIX.md`), `traceability_matrix.csv`, PR-XXX,
  and the validate pyramid. This is the machine layer.
- The engine parses YAML frontmatter only; markdown bodies are for humans (`workflows.md:446`). That line —
  frontmatter is the machine layer, body is the reader layer — is exactly where the lean/voice pass applies.

## Recommendations

- Treat this as a **voice + leanness pass over existing commands**, not new capability. The unit of work is:
  add the alignment snapshot + Settled/Unsettled/Rejected block, a lean core, and an output budget to each
  artifact-producing command; do a plain-first voice edit; cut always-on ceremony — all while leaving the
  frontmatter and registry mechanics untouched.
- Decide the voice referent early: a `working-voice` **skill** installed via `init` (recommended) so any
  "measure against the voice standard" instruction has something to point at in a target repo.
- Sequence by leverage: spec-model and plan-model are the worst offenders on bloat (the source's own review
  rated them weakest); design-model needs Key Bets + a cap; audit-models needs only a leading snapshot;
  implement-model needs de-ceremony, not rules.

## Open Questions

- **Voice delivery:** skill vs. a `.claude/rules/`-via-`init` mechanism vs. inline. (Recommend skill.)
- **How hard are the budgets?** Preferred caps with an appendix carve-out, or firm limits?
- **review-model:** leave as-is for this pass, or fold in the review-not-artifact boundary + finding IDs?
- **Snapshot vs. frontmatter overlap:** the alignment snapshot is reader-facing prose; make sure it
  complements, not duplicates, the machine-read frontmatter.

## Source References

- `~/agentic-project-init/.project/research/20260419-081514_artifact-pipeline-alignment-review.md` — the
  refactor's own rationale (the primary source for this delta analysis)
- `~/agentic-project-init/claude-pack/rules/working-voice.md` — the voice standard
- `~/agentic-project-init/claude-pack/commands/_my_spec.md`, `_my_design.md`, `_my_plan.md` — the leaned commands
- `.project/concepts/architecture-redesign/workflows.md` — our system's state/verification model (the load-bearing constraint)
- `src/agentic_mbse/pm/state.py`, `types.py` — how our state is actually derived
