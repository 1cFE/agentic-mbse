---
id: 0002
title: Legacy positional mismatches are pinned only in a project-root positional-pins.toml, trusted by review, and only pinned positional warnings are exempt from L2's pass rule
date: 2026-10-18
owner: Reid Westwood
status: active
amended_by: []
superseded_by: null
provenance: "[AGENT] (ratified by owner: D1 2026-10-15, R4-1 2026-10-18)"
seams: [l2, validate-cli, target-projects]
supersedes: null
promoted_to: null
---

## Decision

Legacy positional-binding mismatches (D1) are recorded in one strict TOML file, `positional-pins.toml` (schema `positional-pins/v1`, closed at every level), discovered only at the project root that `find_project_root` finds, with `--positional-pins FILE` and `--positional-pins-root DIR` as explicit overrides. A pin matches one exact (owner, input, target) identity. Only a pinned `L2_POSITIONAL_BINDING` warning is exempt from L2's pass rule; every other L2 code keeps its existing behavior. Unmatched pins are reported as stale (error), out of scope (count only) or not judged (owner failed inspection, which is itself an error). The pin list's integrity rests on review of changes to the file; the toolkit does not verify a digest.

## Why

- D1 (owner, 2026-10-15): new mismatches block; pinned legacy mismatches warn until migration. "Warn" is meaningless if a pinned warning still fails L2, so exactly one exemption is needed, and a wider one would weaken unrelated checks.
- Root-only discovery makes the outcome independent of which subdirectory is validated; a walk-up to the first pin file, or to `/`, made results path-dependent (design review M2).
- A stale pin must fail, or a removed mismatch could return already pinned. A pin outside the validated scope must not, or partial validation would always fail (spec review L2-3).
- R4-1 (owner, "A is fine", 2026-10-18): the list only shrinks as consumers migrate, and its changes go through PR review.

## Invariants established

1. Without a pin list, every positional mismatch is an error.
2. A malformed pin list fails the run; it is never read as empty.
3. A pin downgrades only its exact identity; it never suppresses an unverifiable result.
4. A passing run with pinned warnings says so on its final line; it is not a value or route-parity check.

## Rejected alternatives

- A toolkit-verified digest of the pinned set: not chosen by the owner (R4-1), because review of a shrinking file suffices.
- Walking up from the validated path to the first pin file: rejected because results depended on the validated path.
- Exempting all L2 warnings, or all positional findings, from the pass rule: rejected as wider than D1.

Evidence: `.project/completed/20261018_positional-binding-check/design.md` D10–D13, `.project/completed/20261018_positional-binding-check/spec-review.md`, `.project/completed/20261018_positional-binding-check/design-review.md`, `.project/completed/20261018_positional-binding-check/briefs/align.md`.
