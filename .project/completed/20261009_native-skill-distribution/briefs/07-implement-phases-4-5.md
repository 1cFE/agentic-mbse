Phases 1–3 accepted. Orchestrator notes before you continue:

- **Environment fixed.** The worktree is now synced with `uv sync --all-extras`, matching the main checkout's venv (which has `web` and `extract-full`). The 18 environment-only failures should be gone; confirm with a quick run before Phase 4 and record the new red set.
- **`main` at `06ac41d` is already in this branch's history** through `wrap-split`'s merge `40bfca6`, so SC12's "carries `main`'s full history" holds as of now. If `main` moves again before Phase 8, Phase 8 merges it and re-runs `check`.
- **mypy baseline 101** (measured) is accepted for the parity comparison.

Now do **Phases 4 and 5** (the tree is the inventory; legacy adoption and the adapters' agent rule), then stop and report as before: per phase, commits, checks and results, deviations. The bar is highest here, because this is the code the owner keeps: delete more than you add, keep `permit` readable, keep the legacy predicate exactly as the design states (absolute raw text, no `.`/`..`, no normalization, checkout root has `src/agentic_mbse`), and make the tests pin properties derived from the tree, not inventories. Same hard rules as before (worktree only, no push, no writes to the live checkout, native worktree or fusion-tea, no background tasks). End with `ARTIFACT: .project/active/native-skill-distribution/plan.md`.
