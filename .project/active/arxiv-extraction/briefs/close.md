Close work item ARXIV-EXTRACTION (worktree /home/reid/src/agentic-mbse-worktrees/arxiv-extraction, branch fix/arxiv-extraction). The owner asked to close it on 2026-10-18. Audit is certified (.project/active/arxiv-extraction/audit.md, final section). Artifacts: spec.md, design.md (incl. D17, D17a, D18), plan.md, audit.md, spike-margin-stamp.md in the same folder.

Carry forward, with grades:
- [OWNER] open gate: should the arXiv shortcut stay on by default? It ships on (ARXIV_SHORTCUT_DEFAULT in pandoc_convert.py). Record this as an open owner decision, not a settled one.
- [AGENT] follow-ups for the backlog: the title logo inside a saved SVG doesn't resolve offline; PDF-URL provenance (frontmatter names the PDF URL while the hash covers the converted HTML) predates this work and belongs with the existing provenance backlog item.
- Changelog-worthy behavior changes: convert_arxiv_html raises ArxivConversionError instead of CalledProcessError; web warnings go to stderr, not stdout; fewer PDFs take the shortcut (stamp or arxiv.org URL required); the --urls-from PDF URL recursion bug is fixed; metrics.json carries image_count.
Do not commit the untracked ref/ folder or .claude/rules/. Commit the close (decision-led subject, ending with "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"). End with ARTIFACT: <path>.
