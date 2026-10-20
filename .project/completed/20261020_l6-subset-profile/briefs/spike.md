Spike for EXEC-SUBSET-CONTRACT Item 3. Read `.project/active/l6-subset-profile/design.md`, especially its "Checks to run before building" (de-risk flags), Appendix A (legacy-check audit) and Appendix C (safeguard).

Answer, with throwaway code under `.project/active/l6-subset-profile/spikes/` and a findings doc `spikes/findings.md`:

1. **Contract on real trees (blocking).** Run Item 1's contract evaluator (`src/agentic_mbse/sysml/subset_profile.py` and its extraction) and the advisory walkers the design names on `git archive` copies of fusion-tea `f96ad312`, dc3 `808464d` and dc3 `60b44d5`. Report per tree: does anything raise? The verdict, counts by outcome, and any unverified entries with causes. A crash on any tree is the key finding — report it plainly with a traceback.
2. **Advisory shapes.** Find a model expression that actually triggers each of the two advisories (UNSUPPORTED-SHAPE-MESSAGE, WRAPPER-SHAPE). If none can be found, say so.
3. **String ID match.** Check that a design attribute's element ID as the legacy `L6_DESIGN_ATTR_UNEXTRACTABLE` check sees it equals the contract's String finding subject ID, on dc3 `60b44d5`.
4. **Project roots and settings at the pins.** For each archived tree, which project root does `find_project_root` resolve, and does its `pyproject.toml` already have a `[tool.agentic-mbse]` table?
5. **Codegen citations.** Export sysml-codegen at `b5663c07` with `git archive` into a scratch dir and check each codegen citation and "generator-only" claim in the design's Appendix A against it. Never run anything in or modify `~/src/sysml-codegen` (another agent works there).

Rules: no changes to `src/` or `tests/`; sibling repos read-only via `git archive`; never stage the six unrelated working-tree edits (`.gitignore`, `.project/EPIC_GUIDE.md`, `.project/README.md`, `.project/active/README.md`, `.project/backlog/README.md`, `.project/epic_template.md`). Commit only your spike files and findings with an outcome-led subject ending `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. End with the ARTIFACT line.
