Plan EXEC-SUBSET-CONTRACT Item 1 from `.project/active/exec-subset-profile/design.md` (revision 2, reviewed; R1 decided by owner 2026-10-18 — see the Decision line in § R1) and `spec.md` (with its Change Log; SA-1 accepted).

Output: `.project/active/exec-subset-profile/plan.md` with checkbox phases.

Read also: `design-review.md` Resolutions, `spikes/f1-findings.md` and `spikes/f1-occurrence-port/` (the port to productionize and the 11 edge fixtures that seed the parity test), `briefs/align.md` (gates). Read-only: ~/src/sysml-codegen (b5663c07), ~/src/dc3.

Settled inputs:
- [AGENT] (ratified by owner 2026-10-18) R1: Option A, the summary occurrence port as a shared fact in agentic-mbse; end condition (ii) — codegen keeps its copy, Item 2 adds permanent parity CI; ADR 0012 amendment. In Item 1 this means: file the agentic-mbse ADR from design Appendix B.1 in `.project/adr/`; keep the ADR 0012 amendment text as a ready-to-file draft for Item 2 (do not write into sysml-codegen).
- R2 stays a standing gate: any probe showing the generator admits a (shape, context) a rule expected to refuse halts that rule for the owner. The plan must say where in the phase sequence this can surface and that the implementer stops that rule rather than designing around it, while continuing non-dependent rules.
- R3 stays owner-only: the plan produces the proposed GENERATOR-SUBSET-PATTERNS / gap disposition table, marked proposed.

Plan shape I want:
- Probe harness smoke test first (design F5), because every refusal depends on it.
- Then facts (occurrence port + its parity test against codegen-captured expected outputs, the two `reference_use` accessors, other new facts), then the pure decision module and packaged records, then probes and evidence records, then inventory/site account/matrix and their cross-check tests, then the three acceptance runs (dc3 baseline, dc3 repaired, codegen corpus regression floor) and the before/after same-generator check, then ADR filing and the re-estimate for Items 1–2.
- Every phase ends with tests green (`uv run pytest tests/`, `uv run mypy src/`, `uv run ruff check src/ tests/`) and states its verifiable done condition traced to spec criteria.
- Test-first where it fits. Keep phases small enough to review; name the files each touches.
- Hold the quality bar: no duplicated model interpretation beyond the approved port, pure decision layer, closed validated vocabularies, deterministic output, unverified-never-clean.
- Record explicitly anything the plan can't settle and how the implementer should decide it.
