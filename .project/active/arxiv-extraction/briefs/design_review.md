Review the design for ARXIV-EXTRACTION: .project/active/arxiv-extraction/design.md, against its spec (spec.md) and spec_review.md resolutions in the same folder. Write design_review.md beside it.

Context:
- [AGENT, verified] Spike + addendum: .project/active/arxiv-extraction/spike-margin-stamp.md. The margin stamp is distinguishable (3 of 3 PDFs); article.ltx_document is a single container holding the whole paper and no chrome on 3 of 3 pages. Real pages are in .project/active/arxiv-extraction/ref/ (untracked) if you want to check claims.
- Rules: .claude/rules/ (capture-fidelity, working-voice, markdown-formatting).
- [OWNER] Goal: consumers keep Pandoc on PATH safely and drop workarounds. [OWNER] Reserved gates: default-on is open (design must keep it a one-line flip); no removal/rename of public PipelineConfig fields or CLI flags.
- [AGENT] Bar: clean, well-architected code. Look hard at: duplication between routes, module boundaries (is arxiv_html.py the right seam; do pandoc_convert/web_backend/pipeline each keep a coherent job), testability with real bytes, whether warning plumbing (PipelineResult.warnings, metrics.json, stderr) is coherent rather than bolted on, behavior changes users will see (web warnings stdout→stderr), and anything over-engineered for the goal.
Separate must-fix from suggestions. End with ARTIFACT: <path>.
