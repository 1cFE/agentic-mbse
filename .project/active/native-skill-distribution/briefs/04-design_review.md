.project/active/native-skill-distribution/design.md

## Brief from the orchestrator

Independent review of the design for `WRAP-SPLIT` Item 1. You did not write it. The contract is the revised spec (`spec.md`, SC1–SC12); owner decisions and reserved gates are in `briefs/00-align.md`; the spec review and its resolutions are in `spec-review.md`. Write your review beside the design as your process directs; do not edit the design.

### The point, and the bar

[AGENT] (orchestrator, confirmed with the owner at Align) One place to register a skill: one tool-neutral source tree carrying `main`'s current text, installed the same way for Claude Code and Codex. The owner asked to simplify. Judge the design on engineering quality, not only on spec coverage: is the end-state installer code clean and obvious to a maintainer; is each mechanism the smallest one that works; is anything here machinery the item does not need; does anything leave the code worse-shaped than it found it.

### Already settled by the orchestrator (do not re-raise unless you find counter-evidence)

- **SC12 gate** follows the repo's parity rule (pre-PR brief `d693589`; `main` already fails ruff and mypy). The spec is amended to say so.
- **Link provenance:** fusion-tea's legacy links were made by `main`'s `init --dev` (`f92a62a`), not `replicate_setup.sh`, which always copied. Spec, epic and Align record are corrected. Link shape is unaffected.
- **Pruning:** `prune_bundle` (native `installation.py:142-146`) only prunes manifest keys under each shipped bundle, so fusion-tea's 14 `.agentic-mbse/patterns/*` manifest entries are never pruned by a re-init. [AGENT, verified by orchestrator 2026-10-09]
- **Install mode** for fusion-tea's post-merge step is the owner's (parked). The design must make both work.

### Attack these hardest

1. **The legacy-link predicate (D5, Architecture § Legacy adoption).** It normalizes `readlink` text and checks shape plus `is_source_checkout(old.parents[2])`. This repo has a recorded lesson that `os.path.normpath` collapses `symlink/..` textually, so a normalized path and the OS-resolved path can name different trees (CHANGELOG 2026-10-06, "Behavior found"). Is a textual normalization safe here, given recognition must work on dangling links? What does a false positive cost (an owner symlink unlinked and replaced, reported) versus a false negative (clutter, prompt)? Are relative link targets handled? Is "is_source_checkout = `src/agentic_mbse` exists" the right marker for a checkout root, and does the `--dev` prerequisite really need the same predicate as adoption?
2. **Invariant I2, "shipped name by construction".** Verify against the native code that `permit` and the new `remove` are reached only for source-derived entries in every path, including `install-commands`, copy mode, `--force`, and retired-bundle pruning. If any path reaches `permit` for a non-shipped entry, adoption could take an owner link.
3. **Bet B2 (`metadata.kind` in `SKILL.md` frontmatter).** Is there evidence that both Claude Code and Codex tolerate an unrecognized `metadata` map? Check the native spike (`.project/active/spike-native-skill-install/` in this checkout, and native `plan.md`) for what was actually probed. If unverified, say how cheaply it can be de-risked before implementation builds on it, and whether an alternative needs no bet.
4. **`reconcile.py` and `adaptations.yaml` (D2–D4).** Is a one-time script the right tool, and does it need its own tests or at least a negative check (one mutated byte fails `check`; a count mismatch fails)? Is the envelope transform (D3: delete `skills:` line, `Task`→`Agent`, append `metadata`) correct against the branch's real envelope for every bundle, including supporting skills? Does `check` really need no per-file judgment (SC2)? Is Appendix A's adaptation list complete and minimal against the evidence?
5. **Integration topology (D1).** A merge of the native branch into `nsd-integration` cut from `wrap-split`, with conflicts resolved by regeneration. Does the merge produce a sane history and a clean, reviewable diff for the owner's PR? Is anything on the native branch outside the regenerated paths (CLAUDE.md, README.md, tests, `.project/active/native-skills/`) left to hand-merge, and is that called out?
6. **The fusion-tea side (D10, D13, SC9, SC10).** Does putting both target-owned passages in fusion-tea's `AGENTS.md` lose anything for its Claude side? Is the rehearsal (filesystem copy of fusion-tea, links re-pointed at the integration worktree's removed `claude/`) a faithful reproduction of the post-merge state? Does the runbook ordering hold, including the claim that plain `init` can run before the owner moves `/home/reid/1cfe/agentic-mbse`, removing the broken window?
7. **Scope against 2 days.** Name anything that should be cut or deferred.

### What you can read

You cannot read sibling repos. Read-only inputs in `.orchestrate-logs/nsd-inputs/`: `native/` (branch at `86921f9`), `fusion-tea/` (at `403716ee3`), `fork-to-main.names`, `fork-to-branch.names`, `changed-on-both.txt`, `fork-to-main.shipped.diff`, `fork-to-branch.diff`. The design author's measurement scripts are in `.orchestrate-logs/nsd-design-scratch/`. `main`'s shipped content is this checkout. Read; do not run or edit those inputs. You may run read-only commands.

Classify findings by severity (must-fix before plan vs. should-fix vs. note), cite file and line for each, and end with `ARTIFACT: <path to your review>`.
