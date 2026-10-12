# SC4 dry run: install and isolation

Run by the orchestrator, 2026-10-11. `<scratch>` is the orchestrator session's scratch directory, outside any git repository.

**Toolkit (from a wheel, not the worktree).**
- `uv build /home/reid/1cfe/agentic-mbse-goal-layer --wheel` at `57a61c8` → `agentic_mbse-0.1.3-py3-none-any.whl`. `unzip -l` lists `agentic_mbse_data/docs/patterns/design-choices.md`, `agentic_mbse_data/docs/goal-layer-decisions.md` and `agentic_mbse_data/project_templates/GOAL_RUNBOOK.md.template`.
- `uv venv <scratch>/goal-dry-run/venv --python 3.12`; `uv pip install` the wheel with the syside extra index.
- The later template edit at `64ae4ed` ("from demand" → "from required performance" in one sentence of `MODELING_PROCESS.md`) is not in this wheel; no dry-run check depends on it.

**Target.** `mkdir <scratch>/goal-dry-run/target`; with `PATH` and `VIRTUAL_ENV` set to the scratch venv, `agentic-mbse init <target> --assistant claude < /dev/null` (rc 0). The seed models from `tests/fixtures/sump_pump/seed/models/` were copied in and committed as `Seed: sump/pump station` (`e24e41c` in the scratch repo). From the target, `uv run python -c 'from agentic_mbse.cli import get_docs_dir; print(get_docs_dir())'` printed `<scratch>/goal-dry-run/venv/lib/python3.12/site-packages/agentic_mbse_data/docs`. O0 also ran `agentic-mbse validate models --complete` on the seed from a wheel install: 6 of 6 checks passed.

**Agent.** `claude -p "$(cat brief.md)" --setting-sources project,local --permission-mode acceptEdits --allowedTools "Bash Read Write Edit Glob Grep Agent Skill" --output-format stream-json --verbose --max-budget-usd 15`, run in the target with `PATH`, `VIRTUAL_ENV` and `SYSIDE_LICENSE_KEY` set (the key is never written here). Model `claude-opus-5-5`; cost $0.64; result `success`.

**Isolation mechanism and what the agent could see.** `--setting-sources project,local` drops user-level settings, instructions, skills, commands and agents while keeping working authentication. `--bare` was rejected because it also drops the target's own `CLAUDE.md` and needs an API key; a separate config directory with copied credentials was rejected because a token refresh there could invalidate the owner's main session.
- A probe in an empty scratch directory with the same flag (`isolation-probe.txt`) reported no user rules ("Capture Fidelity", "Working Voice", "Markdown Authoring"), no `_my_*` commands, and no CLAUDE.md or memory contents.
- The dry run's own init message (`init-message.json`) lists no `_my_*` command. Its skills are the target's installed skills plus Claude Code's built-ins; its agents are the target's installed expert roles plus built-ins. Its memory path is new and empty.

**How the agent located the pattern.** During its grounding survey it ran the resolver itself (`uv run python -c 'from agentic_mbse.cli import get_docs_dir; print(get_docs_dir())'`, at the end of `read-files.txt:5`), as the installed runbook's § Grounding a goal tells it to, and then read `design-choices.md` under the printed path (`read-files.txt:6`). The path is the scratch venv's packaged docs, so the check that the docs come from the wheel holds (R2-A2). (Corrected 2026-10-12 after audit advisory 6; the first version of this record said the agent ran no resolver command.)
