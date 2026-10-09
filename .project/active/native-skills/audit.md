# Audit: Native Claude and Codex skills

**Verdict:** Certify (re-audited 2026-10-09 with WRAP-SPLIT Item 1: F-A to F-K hold; B1 cleared on re-check, `init --dev` now warns that Codex cannot see its linked skills and the fix is a follow-up; see `.project/active/native-skill-distribution/audit.md`)
**Audited:** 2026-09-08
**Branch:** native-claude-codex-skills (worktree `/home/reid/1cfe/agentic-mbse-native-skills`)
**Commit:** 955295b

---

## The Point

A target modeling repo runs `agentic-mbse init` and gets the shipped MBSE workflows and expert roles installed in a form its assistant actually invokes, without re-init destroying the owner's work. This item extends that promise from Claude Code alone to Claude Code and Codex together: the 15 modeling workflows become SKILL bundles installed once under `.agents/skills/`, aliased for Claude, and registered as native roles for both clients.

The owner ask for this item, verbatim from the invocation: "turn all the modeling-related claude code commands into the SKILL format, which can be installed for claude code and codex."

## Summary

The migration itself is done and the evidence behind it is real. All 15 commands are now `skills/<name>/SKILL.md` bundles, both clients discover them, the installer was rebuilt around an ownership manifest that fixes three previously reproduced data-loss defects, and the test suite that pins all of it passes (1,926 passed, 1 skipped, 5 deselected — I reran it).

What holds up certification is not the migration: it is the leftovers around it. `install-commands --list` still prints 15 `.md` filenames that no longer exist anywhere in the repo. Every normal install now prints its 25 Claude aliases under a "dev mode, points to source" header. And CLAUDE.md — the file that tells the next agent where the product lives and what `--force` means — has three sections that this change invalidated and did not update.

## Product Judgment

**Is this the right piece of work?** Yes. The shape is right and the hard parts were done honestly: shared authoring with thin per-client adapters, a neutral manifest that imports the legacy Claude hashes, and a validation record that names what it did not certify rather than implying full coverage.

Product-lens ledger gate: **DISPOSED** (F1–F6, none BLOCK). No finding contradicts an owner-originated invariant — as lens finding F6 observes, because none has been written down.

Two smells fired and both are resolved here rather than left standing:

- **Smell 1, two representations manually kept synchronized.** Two instances. Against the code (`MBSE_COMMANDS`/`MBSE_SKILLS` vs. the `skills/` tree) it is disposed: `tests/test_installation.py:35` pins the equality automatically. Against the docs it is not disposed — see Findings F1/F2/F3; CLAUDE.md now instructs maintainers to keep a duplicate that no longer exists.
- **Smell 2, a consumer compensates for what the producer should guarantee.** The `status` skill collides with both clients' built-in `/status`, and the shipped fix is prose telling the human to ask for the modeling skill by name. Resolved by citation: the decline is on the record at `plan.md` ("[AGENT] Retain workflow names and existing implicit invocation"), and `validation.md` lists `/status` TUI dispatch as uncertified. It stays an agent-grade choice, challengeable later, not a gap.

**Surfacing (capture-fidelity §4): this item has no `spec.md`.** The audit contract requires one and I proceeded without it, because `plan.md` carries a provenance-graded "Requirements and decisions" section that serves the same function. The consequence is real, though: exactly one requirement is `[NEED]` (owner-stated), and everything I checked conformance against below — the `.agents/skills/` layout, relative aliases, copy mode, assistant selection, the manifest — is `[INFERRED]` or `[AGENT]`, written by the implementing agent. Lens F6 says the same thing from the product side. **Nothing here is settled scope, and the owner has not ratified any of it.** Read the conformance section as "the implementation matches what the implementer wrote down," not as "the implementation matches an approved contract."

## Findings

### Plan completion

All four phases are genuinely complete; I verified each against the code rather than the checkbox.

- Phase 1 (consolidate installer, expose runtime/copy selection): `src/agentic_mbse/cli/installation.py` is new and owns the lifecycle; `--assistant` and `--link-mode` are wired on both `init` and `install-commands` (`src/agentic_mbse/cli/__init__.py:781`, `:791`, `:816`).
- Phase 2 (migrate skills, roles, adapters, templates, docs): 25 bundles in `skills/`, 5 shared roles in `agents/`, 2 adapters, README and CLAUDE.md touched.
- Phase 3 (validate lifecycle, packaging, suite): reran the full suite — **1,926 passed, 1 skipped, 5 deselected**. Ruff on the four changed Python files passes. The 119 ruff errors and 3 mypy errors on `src/`+`tests/` are pre-existing on `main` (confirmed by running both against the base checkout), so the plan's "changed files passed" claim is accurate as scoped.
- Phase 4 (install into `/home/reid/agentic-mbse-target`): verified on disk — 25 canonical bundles, 25 relative aliases, 5 `.claude/agents/*.md`, 5 `.codex/agents/*.toml`, `.codex/config.toml` registrations, `CLAUDE.md`/`AGENTS.md`/`.agentic-mbse/*.md`. `discovery-results.json` and `role-results.json` match what the plan claims.

### Spec conformance

Against `plan.md`'s "Requirements and decisions" (there is no `spec.md` — see Product Judgment):

- `[NEED]` native-support changes on a branch, test-installed into `/home/reid/agentic-mbse-target` — **met**, verified on disk.
- `[INFERRED]` 15 workflows + 10 supporting bundles, `.agents/skills/` canonical, relative Claude aliases — **met**. `tests/test_installation.py:31` parametrizes claude/codex/both × symlink/copy and asserts non-absolute link targets.
- `[INFERRED]` explicit copy mode and claude/codex/both selection, default both — **met** (`__init__.py:781`, `:787`).
- `[INFERRED]` five native roles rendered from shared source, tool mappings in adapters — **met**. `render_agent` (`installation.py:207`) resolves `{SYSML_DOCS_PATH}`/`{SYSIDE_DOCS_PATH}` and emits Claude Markdown or Codex TOML with `sandbox_mode = "read-only"` for the three reference readers.
- `[INFERRED]` neutral manifest, legacy hash import, preserved baselines and owner additions, never write through destination symlinks — **met**. Legacy import is hash-compatible: `compute_source_hash` is plain sha256 of file bytes, identical to `fingerprint`'s digest, so real legacy installs migrate without false "modified" verdicts.
- `[AGENT]` retain workflow names and implicit invocation; extraction providers and inactive hook registration unchanged — **met**.
- `[AGENT]` the `syside check` contradiction stays out of scope — **respected, and genuinely pre-existing**: `skills/implement-model/SKILL.md:47` and `skills/toolkit-awareness/SKILL.md:72` both carried this text at `88e2489`.

### Design conformance

No `design.md` exists. Not evaluated.

### Code integrity

**F-A. `install-commands --list` prints a catalog of files that do not exist.** `src/agentic_mbse/cli/__init__.py:696` iterates `MBSE_COMMANDS` and prints 15 `.md` filenames under "Available MBSE commands". I ran it: it reports `analyze-models.md` … `status.md`, "Total: 15 commands". None of those files exist — `claude/commands/` is empty. Meanwhile the command actually installs 25 bundles. The product's own catalog output now names nonexistent files and under-reports what it does by ten. Should print the installed skill bundle names from `skills/`.

**F-B. Every normal install claims to be in dev mode.** `src/agentic_mbse/cli/__init__.py:652` prints `Symlinked (N) - dev mode, points to source:` unconditionally. Before this change `symlinked` was only populated under `--dev`, so the label was true. Now the 25 relative Claude aliases land in that same list on every non-dev install, so a plain `agentic-mbse init` prints 25 paths under a "dev mode" header. I reproduced it on a fresh target with `dev=False`. The header needs to be conditional on `is_dev_mode`, or the aliases need their own bucket.

**F-C. CLAUDE.md's Change Coordination section mandates maintaining a file that no longer exists** (lens F1). `CLAUDE.md:212-221` tells maintainers to keep `scripts/replicate_setup.sh` in sync with `cmd_init()` across `MBSE_COMMANDS/AGENTS/SKILLS/HOOKS`, and documents each doing its own placeholder substitution. `scripts/replicate_setup.sh` is now six lines that `exec` the CLI. The whole section is stale, and it is aimed squarely at the next agent to touch the installer.

**F-D. CLAUDE.md and README.md now state different `--force` contracts** (lens F2). `CLAUDE.md:232` says "Use `--force` to overwrite user-owned files." The implementation deliberately does not: `.claude/settings.json`, `CLAUDE.md` and `AGENTS.md` survive `--force` (`installation.py:280`, `__init__.py:604`; pinned by `tests/test_installation.py::test_native_owner_configuration_preserved_with_force`). README.md states the new rule. The most user-visible promise in the product has two durable homes that disagree.

**F-E. CLAUDE.md's file pointers are wrong** (lens F3). `CLAUDE.md:45` says to modify `skills/spec-model.md` / `skills/plan-model.md`; the files are `skills/spec-model/SKILL.md` / `skills/plan-model/SKILL.md`. That line exists only to route an agent to the right file.

**F-F. A preserved legacy command splits the two clients silently** (lens F5). `installation.py:172` preserves a modified or untracked `.claude/commands/<name>.md` and skips only the Claude alias — but `.agents/skills/<name>` is still installed, so Claude keeps running the owner's old command while Codex runs the new skill. `tests/test_installation.py:78` pins exactly this. The preservation is right; the message at `installation.py:180` ("legacy command remains active; Claude skill migration deferred") does not tell the owner that the two clients now diverge. One clause on that message closes it.

**F-G. Nothing prunes managed files that leave a bundle.** `copy_tree` (`installation.py:118`) writes every source file and never removes a manifest-tracked file whose source is gone, and `save` (`installation.py:191`) rewrites the stale key too. When an upstream skill drops or renames a reference doc, the old one stays in every installed target forever and the assistant reads it as current guidance. The manifest already holds exactly the information needed to prune — managed, unmodified, no longer in the bundle. This is the cost side of "never delete owner additions," and it is not stated anywhere.

**F-H. `MBSE_AGENTS` and `MBSE_HOOKS` are dead.** `src/agentic_mbse/cli/__init__.py:37` and `:60`. Nothing reads them; `install_assistants` globs `agents/*.md` and `claude/hooks/*` instead. `MBSE_COMMANDS`/`MBSE_SKILLS` survive as the pinned inventory in `tests/test_installation.py:35`, which is a legitimate role — these two have none.

**F-I. The adapter preamble is 25 hand-maintained copies with no test.** Every `skills/*/SKILL.md` opens with the same paragraph pointing at `.agentic-mbse/claude.md` / `codex.md`; I confirmed all 25 are byte-identical. That pointer is the entire mechanism by which a skill reaches its runtime adapter, and no test asserts a bundle carries it. A hand-added skill silently loses the adapter and nothing fails.

**F-J. The interactive prompt's non-skip branches lost their tests.** `tests/test_cli.py` deleted `TestPromptForModifiedFile` (5 cases) with the helpers it covered, but `_prompt_for_modified_file` (`__init__.py:299`) is still live. The surviving coverage exercises `"s"` only (`tests/test_cli.py:611`, `:660`), so `b`/`o`/`S`/`O` and the `skip_all`/`overwrite_all` handling in `permit` are now untested through any path.

**F-K, minor. `cmd_init` swaps the installer's action dict from outside.** `__init__.py:439` replaces `installer.actions` wholesale with five externally-owned lists. It works because the five keys match `installation.py:47` exactly, and breaks with a `KeyError` the moment either side adds a bucket. Passing the lists into the constructor would make the coupling checkable.

---

## Certification

**Not certified.** Verdict is Needs Work on F-A and F-B (user-visible output that is now false on every install) and F-C/F-D/F-E (durable docs contradicting the shipped behavior). F-F through F-K are real but would not on their own block.

What I checked and marked: all four plan phases are verified complete and stay `- [x]`. No spec success criteria exist to mark. The product-lens ledger was written to `.project/active/native-skills/product-lens.md` with gate DISPOSED.

What I verified myself rather than accepting from the record: the full test suite (reran, 1,926 passed), ruff and mypy scoping against the `main` baseline, the legacy-hash compatibility claim, the `syside check` contradiction's pre-existence, the installed state of `/home/reid/agentic-mbse-target`, the `--list` output, and the false dev-mode header on a fresh install.

**Not checked:**
- Any modeling behavior. No workflow was executed end to end; no model was built or validated through the migrated skills.
- Whether the SKILL bodies still read correctly as skills. I diffed them for content loss and confirmed the orchestrate-modeling change is line-unwrapping plus `Task`→subagent renaming, but I did not review the other 24 bodies for prose that assumes Claude-only affordances.
- The adapters' accuracy as instructions. `adapters/claude.md` and `adapters/codex.md` are 9 lines of dense platform guidance each; I read them but verified none of their tool, delegation, permission, or `fork_turns` claims against the live clients.
- Codex role spawning beyond the recorded evidence. I read `role-results.json`; I did not rerun the trusted-profile nested probe, which costs model turns.
- macOS and Windows. `--dev` is refused on Windows; nothing else about non-Linux was exercised, here or in the record.
- Hook activation, MCP setup, `/status` TUI dispatch, and the interactive question widgets — all listed as uncertified in `validation.md` and still uncertified.
- The `.project/` artifacts copied onto this branch (`spike-native-skill-install/`, the research file) for accuracy; I used them as context, not as claims under audit.
