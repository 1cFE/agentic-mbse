The independent audit is in: `.project/active/native-skill-distribution/audit.md` (committed `cbf349c`), verdict **Needs Work** on one blocker. Orchestrator dispositions [AGENT] (orchestrator, 2026-10-09):

**B1 — `init --dev` gives Codex none of the shipped skills and reports success.** Clear it by making the limitation honest and visible now, and file the fix as a follow-up. Reasoning: the gap predates this item (native `86921f9` links the same way); fusion-tea's recommended mode is plain `init`; a real fix is new installer behaviour that first needs a spike on which link shapes Codex lists. So:
- `init --dev` prints a clear warning whenever Codex is among the selected runtimes (`codex` or `both`): Codex does not list skills that `--dev` installs as links to the source checkout, and plain `init` is the mode to use for Codex. The closing "Next steps" text must not tell a `--dev` user to run `$onboard` in Codex without that caveat.
- `README.md`'s `--dev` paragraph (`README.md:49`) states the same limitation in one or two plain sentences.
- A test pins the warning (present for `codex` and `both` under `--dev`, absent for `claude` and for plain `init`).
- Add the follow-up to the plan's notes and `evidence/audit-scope.md` follow-up list: "`--dev` Codex discovery: spike which link shapes Codex 0.160+ lists (file links vs directory links, inside vs outside the project), then make `--dev` produce one."

**Advisories — fix these (they improve the code the owner keeps):**
1. Pin the two unguarded predicate checks. Make the `..` rows and a name-mirroring row use a real checkout root (one with `src/agentic_mbse`) so only the targeted check can reject them. Show that mutants M1 (drop the `..` check) and M7 (drop name mirroring) are now killed, and record that.
3. Remove the hard-coded "15 workflows and ten supporting skills" from `README.md:25` (counts go stale; SC5's spirit).
5. One frontmatter parser in `installation.py` instead of three, if the three really parse the same thing; keep behaviour, let the existing tests prove it.
6. Remove the four caller-less names in `cli/__init__.py` only if nothing in `src/`, `tests/`, shipped text (`skills/`, `agents/`, `adapters/`, `project_templates/`, `docs/`) or `CLAUDE.md`/`README.md` refers to them; `get_docs_dir()` must stay (invariant I6). If any is referenced, leave it and say where.
8. Where a test uses a specific skill name only as a sample, derive the sample from the tree; leave tests that are genuinely about one skill.
9. `reconcile.py check` compares raw bytes, not decoded text. Re-run `check` and the negative self-check, add a CRLF case to the negatives, and refresh `check.txt`/`check-negative.txt`.

**Advisories — accepted, no change:**
2. The `skills:` frontmatter key: dropped on purpose by the native branch; Claude Code treats `skills:` as subagent preloading metadata, not a command dependency loader (`.project/research/20260907-162310_native-claude-codex-skills.md:54-56`), so no runtime behaviour is lost. Note this in `dispositions.md` if it is not already there.
4. A1 (onboard writes context to `OVERVIEW.md` and the entry file): kept as reviewed; both runtimes see the context.
7. fusion-tea's `epic_template.md` link: runbook step 4 handles it.

Same permissions and rules as before: worktree and scratch only, no writes to the live checkout, the native worktree or fusion-tea; prepare commit steps with a `verify.py` run if `git` is blocked (one step for the B1 change, one for the test pins, one for the cleanups, one for the reconcile/evidence refresh, one for notes); no background tasks. Keep the full suite green and the lint parity record true (re-run ruff and mypy on changed files). Report what changed per finding and the mutant results. End with `ARTIFACT: .project/active/native-skill-distribution/plan.md`.
