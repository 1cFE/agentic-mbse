# Epic: Command Refresh — Clearer Scope, Leaner Artifacts, Plainer Voice

**Epic ID**: CMDREF-001
**Status**: Draft
**Priority**: Medium (P2)
**Created**: 2026-07-03
**Estimated Effort**: ~4-5 days (decomposition pending)

---

## Executive Summary

Our shipped commands predate the `agentic-project-init` shift toward mental alignment — artifacts that let
the next reader recover the intent fastest, not that say the most. This epic applies that shift to our
existing commands (leaner artifacts, a shared "what matters" snapshot, plainer voice) without touching the
load-bearing frontmatter and registries the PM engine depends on, and explores a front-of-pipeline shaping
stage for setting clear scope and objectives before epic/spec.

**Critical Success Factor**: Commands and artifacts get leaner and clearer while every machine-read
structure (frontmatter, SV-XXX, traceability, PR-XXX) stays intact.

---

## Why This Epic?

**Current State**:
- Prompts are long and convoluted; artifacts are formal and enumeration-heavy (MR-XXX dumps, verbose
  per-phase plans, always-on ceremony).
- No artifact opens with an alignment snapshot; no Key Bets; no Settled/Unsettled/Rejected handoff.
- No voice standard ships, so there is nothing to measure "communicate what matters" against.
- No shaping stage before spec/epic. We have `formalize-intent` (G-XXX/AQ-XXX) and `backlog decompose`,
  but no concept-equivalent for setting scope and objectives up front.

**Future State**:
- A `working-voice` standard installs via `init` and is the referent for the voice pass.
- spec/design/plan artifacts open with an alignment snapshot, carry a Settled/Unsettled/Rejected handoff
  and preferred line caps; design carries Key Bets.
- Commands read plainly and drop ceremony the earlier stages already resolved; audit leads with a verdict.
- A clear, reconciled answer (and, if approved, a command) for setting scope/objectives pre-epic.

---

## Success Criteria

- [ ] A `working-voice` skill ships and installs via `init`; commands that need a voice referent point at it.
- [ ] spec/design/plan artifacts open with an alignment snapshot and carry a Settled/Unsettled/Rejected
      handoff + a preferred line cap; design-model carries Key Bets.
- [ ] Commands do a plain-first voice pass and cut always-on ceremony (conditional offers); audit-models
      leads with a verdict snapshot.
- [ ] A recommendation for a pre-epic shaping stage (concept-equivalent), reconciled with `formalize-intent`
      and `backlog decompose` — and, if approved, the command shipped.
- [ ] No load-bearing frontmatter or registry mechanics changed; existing tests pass; new skill/command
      registered in `cmd_init` + `replicate_setup.sh`.

---

## Source Documents

- `.project/research/20260703-112157_command-refresh-from-agentic-project-init.md` — **research** — the
  delta analysis: what the refactor changed, which primitives apply to us, the load-bearing-vs-bloat line
  per command, and what not to port.

Reference baseline (not in this repo):
- `~/agentic-project-init/.project/research/20260419-081514_artifact-pipeline-alignment-review.md` — the
  refactor's own rationale.
- `~/agentic-project-init/claude-pack/rules/working-voice.md`; `_my_concept.md`, `_my_concept_design.md`.

---

## Backlog Items

*Pending decomposition (Stage 2). Kept lean deliberately — items stay at objective / why-one-item /
done-state altitude; real detail waits for each item's spec.*

---

## Dependencies

**Item Dependency Graph**: *to be defined in Stage 2.*

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Lean pass strips something load-bearing | High | Frontmatter + registries are off-limits; pass targets prose/template only |
| The epic itself bloats into mini-specs | Med | Keep items at strategic altitude; detail lives in each item's spec |
| Shaping-stage item overlaps `formalize-intent` / `backlog decompose` | Med | The item's first job is to reconcile, not to add a redundant command |

---

## Timeline

*To be refined at decomposition.*

---

**Last Updated**: 2026-07-03
**Next Action**: Confirm scope, then decompose into backlog items (Stage 2)
