Revise the existing spec for ARXIV-EXTRACTION in place: .project/active/arxiv-extraction/spec.md. Do not start a new spec. Incorporate the review at .project/active/arxiv-extraction/spec_review.md, specifically every entry in its "Resolutions" section (decided by the orchestrator on 2026-10-18; grades given there). Keep the spec's evidence and scope; change only what the resolutions and must-fix findings require.

Key points:
- [OWNER] Goal: downstream consumers can keep Pandoc on PATH safely; their workarounds (hiding Pandoc, stripping data-image refs) become unnecessary. This is the only [NEED].
- [OWNER] Shortcut default-on is an OPEN owner gate. Record it as open, with "on" as provisional. Do not mark it settled.
- Add grade markers per the capture-fidelity rule (.claude/rules/capture-fidelity.md): spec register uses [HARD] [NEED] [INFERRED] [INHERITED]. Orchestrator [AGENT] resolutions absorb as [INFERRED].
- No compensating prose about rejected paths; trimmed items just get trimmed.
Do not ask questions the resolutions already answer. If something genuinely is unresolved, decide it, mark it [INFERRED], and note it in the spec. End with ARTIFACT: <path>.
