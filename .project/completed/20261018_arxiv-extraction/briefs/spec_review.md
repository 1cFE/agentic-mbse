Review the spec for work item ARXIV-EXTRACTION: .project/active/arxiv-extraction/spec.md (worktree /home/reid/src/agentic-mbse-worktrees/arxiv-extraction, branch fix/arxiv-extraction). Write the review next to it as spec_review.md.

Intent (from orchestrator Align with owner, 2026-10-18):
- [OWNER] The goal is that downstream consumers can keep Pandoc on PATH safely: no citation-driven paper substitution, no missing figures, no arXiv chrome. The success test is that their workarounds (hiding Pandoc from PATH, stripping data-image refs) become unnecessary.
- Provenance: the spec carries no grade markers. It was agent-written from a personal-os queue report. Treat its requirements as [INFERRED] (agent-derived from the report) unless they restate observed evidence. Challenge on evidence, and recommend the spec add grade markers.
- [OWNER] Reserved for the owner: whether the shortcut stays enabled by default (spec R3 keeps it on), and any removal/rename of existing public PipelineConfig fields or CLI flags. Do not decide these; flag if the spec forces them.
- [AGENT] Orchestrator's hypothesis for R2: arXiv-stamped PDFs carry the paper's own ID as a vertical left-margin stamp "arXiv:NNNN.NNNNNvN [cat] date" on page 1; a stamp matching the candidate ID could be the trusted identity evidence. Assess whether the spec leaves room for this and whether R2 is testable as written. Do not treat this as decided.
- [AGENT] Watch for gold-plating, especially R4 cleanup breadth; requirements should be proportionate to the goal.

Focus: are requirements testable, unambiguous, consistent with the actual code (check src/agentic_mbse extraction modules and the CLI), and sufficient for the goal? Separate must-fix from suggestions. End with ARTIFACT: <path>.
