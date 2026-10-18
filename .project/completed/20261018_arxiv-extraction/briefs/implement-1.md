Implement ARXIV-EXTRACTION Phases 0, 1 and 2 of .project/active/arxiv-extraction/plan.md (design.md, spec.md beside it). Stop after Phase 2; later phases run in a separate session.

- [OWNER] Goal: consumers keep Pandoc on PATH safely and drop workarounds. [OWNER] Reserved: default-on is open (one constant); no removal/rename of public PipelineConfig fields or CLI flags.
- [AGENT] Bar: clean, well-factored code that reads like the surrounding code. No duplicated logic between routes, no dead code, no TODO placeholders. Tests hit real HTML/PDF bytes; stub only network and subprocess boundaries.
- [AGENT] Accepted plan deviation: convert_arxiv_html's non-missing-Pandoc failures may raise ArxivConversionError instead of CalledProcessError; record it in Implementation Notes so it lands in the changelog.
- Commit each phase separately once green (subject leads with what the phase decided/achieved; end with the line "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"). Check off plan boxes and fill that phase's Implementation Notes before committing it. Do not commit the untracked .project/active/arxiv-extraction/ref/ or .claude/rules/.
- Use `uv run` for everything. If something in the plan turns out wrong against the code, decide, record it in Implementation Notes, and continue; stop only on evidence against a design premise.
Report per phase: what landed, test counts, deviations. End with ARTIFACT: <plan path>.
