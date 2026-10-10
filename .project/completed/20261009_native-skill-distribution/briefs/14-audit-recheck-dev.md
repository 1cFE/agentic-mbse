.project/active/native-skill-distribution/audit.md

## Brief from the orchestrator

Targeted independent re-check of Phase 9 on branch `nsd-integration` (worktree `/home/reid/1cfe/agentic-mbse-nsd`), the change from `b2ff7cf` to `d314b6e`. You did not write it. Add a dated "Re-check: Phase 9 (`--dev` folder links)" section to `audit.md`, update its verdict line if your verdict changes, and run product-lens and append its block to `product-lens.md`.

### What changed and why

- The first audit's B1 (product-lens audit-F1): under `init --dev`, Codex listed none of the 25 shipped skills. The orchestrator cleared B1 with a warning and deferred the fix; the lens kept audit-F1 BLOCKED, owner disposition only.
- **Owner disposition of audit-F1: fix it.** [OWNER] 2026-10-09, in chat: the owner asked for a spike ([OWNER-VERBATIM] "can you run a spike to figure it out? … would symlinking directly to .claude in the same repo work?"), then answered "yes" to the orchestrator's "Want me to run the fix?". Record this as the authority for audit-F1's resolution if the fix holds.
- The spike, by the orchestrator: `evidence/spike-dev-codex-links.md` (`e202396`). Codex 0.160.0 never lists a skill whose `SKILL.md` is a file link; it lists a skill whose folder is a link.
- Phase 9 (`briefs/13-dev-folder-links.md`; commits `a42c4c9` code/tests/README, `5b93cac` evidence and rehearsal, `d314b6e` plan/design D14/spec status): under `--dev` each `.agents/skills/<n>` is one absolute folder link to the checkout's `skills/<n>` (`installation.py:365-383`), through the generalized ownership check `Installer.link_directory` (`:232`); a real folder holding unowned files gets a plain copy instead, with a printed line; the B1 warning and its next-steps branch are deleted.

### Check

1. **The fix, independently.** Run `.project/active/native-skills/discovery_probe.py` yourself on a fresh `init --dev` scratch target under `.orchestrate-logs/audit-scratch/` (Codex 25, Claude 18, roles 5 expected), and for each `--assistant` choice if you judge it worth it. Compare with `evidence/probe-dev-folder-links.json`.
2. **The code.** Is `link_directory` a true generalization (the Claude alias behaves exactly as before)? Is `install_dev_bundle`'s fallback right: owner files never lost, never per-file links, the printed reason accurate in every case that reaches it (including an empty real folder)? Transitions both ways (fresh; over the earlier per-file `--dev` install; over a plain install; plain over `--dev`; `--assistant codex`; `--link-mode copy`; second run): read the tests and try the ones you doubt in scratch.
3. **Mutations.** For example: make `--dev` link per file again; drop the fallback so `install_dev_bundle` returns False on an unowned folder; fall back to per-file links; make `link_directory` skip the ownership check; drop the manifest key cleanup. Record which the suite kills. Revert every mutation.
4. **The tests** pin the property Codex needs, derived from the tree (SC5, I4), not a sample or an inventory.
5. **Evidence and docs.** The re-run rehearsal (`evidence/rehearsal.md`, `evidence/rehearsal/`): the stage reports plain mode unchanged in substance and dev mode now listing 25 + 5 in Codex; it also extended `.orchestrate-logs/rehearsal/provenance.py` to see folder links. Check that extension did not weaken the check (dev mode should flag the same lines as before). Check `fusion-tea-runbook.md` step 3 and step 5 against the raw outputs, and that the install-mode choice is still presented as the owner's. `README.md:47`, `design.md` D14, `plan.md` Phase 9, `evidence/audit-scope.md`, `evidence/lint-parity.md`. Grep the tree for leftovers of the removed warning or of "Codex cannot see" claims that are now false.
6. **Gate.** Full `uv run pytest tests/`; ruff check, ruff format --check and mypy against the parity record in `evidence/lint-parity.md`.

### Product-lens

Run it for this re-check (foreground, no background tasks). Resolve audit-F1 with the owner's authority above if the fix holds, or keep it open and say why. Note anything new.

### Rules

Read-only on tracked files except `audit.md` (and its verdict line) and `product-lens.md`. Scratch under `.orchestrate-logs/audit-scratch/`. No writes to `/home/reid/1cfe/agentic-mbse`, the native worktree or `/home/reid/1cfe/fusion-tea`. Do not commit (the orchestrator commits). No background tasks. End with a summary: verdict, findings by severity with file:line, the probe numbers you got, mutation results, gate numbers. Then `ARTIFACT: .project/active/native-skill-distribution/audit.md`.
