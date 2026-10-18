Design ARXIV-EXTRACTION from its spec: .project/active/arxiv-extraction/spec.md (worktree /home/reid/src/agentic-mbse-worktrees/arxiv-extraction). Write design.md beside it.

Context to use, not re-derive:
- Spec review and resolutions: .project/active/arxiv-extraction/spec_review.md
- Spike result, read it: .project/active/arxiv-extraction/spike-margin-stamp.md. [AGENT, verified on 3 real PDFs] The arXiv margin stamp comes out of pymupdf get_text("dict") as a rotated line (dir (0,-1)) in the left margin with text "arXiv:<id>v<N>  [<cat>]  <date>"; Creator metadata is useless (2 of 3 genuine papers say "LaTeX with hyperref"). Build R2's trusted evidence on the stamp (plus the arxiv.org source URL where the PDF came from a URL). Fixtures can be generated with pymupdf.
- Rules files are not in this worktree; read them from the main checkout: /home/reid/src/agentic-mbse/.claude/rules/ (capture-fidelity.md, working-voice.md, markdown-formatting.md).

Intent:
- [OWNER] Goal: consumers can keep Pandoc on PATH safely and drop their workarounds.
- [OWNER] Reserved gates: (1) shortcut default-on is OPEN; design for "on" provisionally and keep the default in exactly one place so flipping it is trivial. (2) No removal/rename of existing public PipelineConfig fields or CLI flags; additions are fine.
- [AGENT] Engineering bar: one shared arXiv module for article selection, chrome removal and image persistence used by both the PDF shortcut (pipeline.py/pandoc_convert.py) and the direct HTML route (web_backend.py); no duplicated logic between routes. Prefer small pure functions that tests can hit with real HTML/PDF bytes; stub only network and subprocess boundaries. Reuse existing helpers (e.g. web_backend._download_arxiv_images) by moving/generalizing rather than copying. Keep R4 proportionate: target the LaTeXML article container that real arXiv HTML uses; unrecognized structure falls back with a warning.
- Pin a representative real arXiv HTML fixture, trimmed to a manageable size but keeping real chrome and article structure. /tmp/arxiv-investigation-1topu2hb/raw.html is a fresh fetch of 2610.14224 you may trim from.

Decide execution details yourself and record them in the design. Ask only if a reserved gate is forced. End with ARTIFACT: <path>.
