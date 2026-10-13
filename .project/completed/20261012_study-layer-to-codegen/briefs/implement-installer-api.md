# Brief: implement — installer API for other repositories (WRAP-SPLIT Item 3, agentic-mbse side)

Sent by the orchestrator (`/_my_orchestrate`, 2026-10-12) to `/_my_implement`, in the agentic-mbse worktree `/home/reid/1cfe/agentic-mbse-study-layer` (branch `study-layer-to-codegen`, base `ac5fb1a`).

## Context

WRAP-SPLIT Item 3 moves fusion-tea's study layer into sysml-codegen. Its tracking (spec, design, plan) lives in the sysml-codegen worktree. Read-only copies of the spec and design are at `.orchestrate-logs/src/sysml-codegen@study-layer/{spec,design}.md`. sysml-codegen's `install-commands` will install the `run-study` skill through this repo's `Installer`, keeping its own manifest. This phase makes the small public API change that needs. The design specifies it exactly in **Appendix B, "The agentic-mbse change (exact)"**. Read that appendix, plus design DD5 and premise conflict 1, which explain why the package version stays 0.1.3.

Treat Appendix B as the plan for this phase. Implement exactly what it lists:
1. `INSTALLER_API_VERSION = "installer/v1"` with its comment.
2. `Installer(..., manifest: str = MANIFEST)`. It reads the legacy and default manifests only when `manifest == MANIFEST`.
3. `save()` writes `self.manifest`.
4. Extract `install_bundle(installer, source, *, runtimes, link_mode, dev)` from the loop body of `install_assistants`. This is a pure refactor.
5. Add one sentence to the `CLAUDE.md` "Change Coordination" section.

Write the five listed tests first, in `tests/test_installation.py`, matching its existing style. Behaviour must not change for any existing caller. The existing installer tests are the guard.

## Bar

- This is now a public seam that another repository builds on. Keep it minimal, typed and documented, and expose nothing else.
- If Appendix B turns out wrong against the real code (it was written from a staged copy at `ac5fb1a`, which is this branch's base), stop and report rather than improvise. A detail that only fixes the appendix's wording is fine to adapt; say what you changed.
- Do not change the package version.

## Verification

- Record the baseline before you change anything: `uv run pytest tests/` (the environment is synced), plus `uv run ruff check src/ tests/` and `uv run mypy src/`.
- After the change: the full suite passes with the same pass count plus the new tests; ruff and mypy show no new findings against the baseline.

## Commit

Commit with explicit paths: `git commit -- <paths>`, after checking the index is otherwise empty. Two commits are fine: tests, then implementation. Or one. Each subject leads with what changed. End each message with:

`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`

Do not push. Do not start background tasks. Finish with a short report (baseline vs. after, files changed, any deviation from Appendix B) and `ARTIFACT: src/agentic_mbse/cli/installation.py`.
