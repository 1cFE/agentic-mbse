# Brief: /_my_design — research-seam-port (`WRAP-SPLIT` Item 5)

Write the design for `.project/active/research-seam-port/spec.md` to `.project/active/research-seam-port/design.md`. Do not commit; the orchestrator commits. Start no background tasks. End with `ARTIFACT: <path>`.

## Read first

- `spec.md` (refreshed 2026-10-12), `briefs/align.md` and `product-lens.md`, beside this brief. There is no spec review; Align skipped it.
- The design page the owner approved: `.project/mental-alignment-v2/runs/20261006-150340_research-process-end-state_fresh.html` (port table, "Rules the scripts enforce", call stack).
- `.project/research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md` § 1c.
- fusion-tea, read-only snapshot at `.orchestrate-logs/fusion-tea-snapshot/` (fusion-tea `0a833b9f7`): `scripts/{research_seam,source_registry,holdout_guard,zotero_ingest,zotero_lib}.py`, `.claude/commands/research-acquire.md`, `docs/research_seam_operator_guide.md`, `.project/adr/0008-*.md`, `tests/research/`, `CLAUDE.md`, `.gitignore`, `pyproject.toml`, and the original seam work at `.project/completed/20260827_goal-research-seam/{spec,design}.md`. You cannot read `/home/reid/1cfe/fusion-tea`. Registry data and hold-out material were deliberately not copied.

## What matters most

Two things, in this order.

1. **Behaviour stays the same.** This is a port. Classes and their precedence, the refusal ladder and its six outcomes, one receipt per attempt, four-files-or-nothing under one lock, the request-key formula, and the receipt, return and manifest shapes all carry over. fusion-tea's 123 manifest rows, run directories and negatives must keep working with no migration. Any behaviour change needs a named reason in the design. A fusion-tea-only behaviour that becomes a hook default (no hold-out guard configured) is the expected kind.
2. **It reads as agentic-mbse code, not as two scripts pasted into `src/`.** Hold the engineering bar. The 1,350-line registry should become a small package of coherent modules with a thin CLI over a typed Python API, in the style of `src/agentic_mbse/pm/` and `cli/pm_cli.py`. New code adds zero ruff and mypy findings (baseline at `ac5fb1a`: ruff 118, mypy 88). Restructure where it buys clarity, and let the ported tests pin behaviour while you do. Do not redesign the mechanism.

## Orchestrator facts ([AGENT], verified 2026-10-12)

- fusion-tea modules that import the Zotero helpers and stay in fusion-tea: `scripts/zotero_ingest.py`, `scripts/zotero_group_download.py`, `scripts/test_zotero_write_access.py`. Whatever names the package exports for them is a public API, so keep it small and name it.
- fusion-tea tracks `knowledge/` in git (8,494 files) and ignores `knowledge/.staging/` and `knowledge/.registry.lock` (`.gitignore:35-36`). Spec criterion 4 (parity on fusion-tea's data) therefore runs in a fusion-tea worktree with this branch installed editable, comparing `scripts/source_registry.py verify` with `agentic-mbse research verify` over the same tree. Orchestrator-run.
- fusion-tea names its research procedure in `CLAUDE.md:11` (in the snapshot). That line is the main fusion-tea instruction that changes.
- `register` shells out to `agentic-mbse extract --save-source`, which needs the optional `web` extra for URLs and `extract` for PDFs. Without `web`, 18 existing tests fail on import. Say what `register` does when the capture extra is missing.
- agentic-mbse reads no target-side runtime configuration today; `tomllib` is used only for install-time checks. The hook mechanism is a new decision.
- The index `init` ships: `SOURCE_INDEX.md.template:36` at the repo root (`## How This File Is Used`), with an inline fallback copy in `src/agentic_mbse/cli/__init__.py:473-485`. Ignore-line precedent: `_update_gitignore_for_dev_mode`, `cli/__init__.py:278`.
- Parallel work: Item 3's branch `study-layer-to-codegen` edits `src/agentic_mbse/cli/installation.py`, so don't touch that file unless you must. Item 4 has not started; it will read `manage-sources`, `source-traceability` and `docs/source-index.md` after this item, and this item owns the registry-related changes to them.
- fusion-tea pin, for the fusion-tea side and its runbook: pinned by full SHA in `pyproject.toml` and `uv.lock` (`ac5fb1a` today). A pin can only point at a pushed commit, and pushing is the owner's, so the pin move is a post-merge step. Moving it means editing the `rev`, replacing the SHA in `uv.lock` by hand (re-locking fails under uv 0.10), `uv sync --frozen --extra e2e`, `uv pip install --no-deps syside-license==0.3.6`, updating the SHA in fusion-tea `tests/test_dependency_provenance.py`, then `uv run --no-sync agentic-mbse init . < /dev/null`. Before merge, in-situ checks install this checkout editable (`uv pip install --reinstall --no-deps -e <worktree>`) and run with `uv run --no-sync`.

## Orchestrator leans (all [AGENT]; overrule them with reasons if the code says otherwise)

1. **Package shape.** `src/agentic_mbse/research/` with modules split by responsibility: paths and lock, manifest, index writer, identity and capture, the register ladder, retire and verify, the hold-out hook, and the seam bookkeeping (open, log, close, classes). Subcommands in their own `cli/research_cli.py`, wired from `cli/__init__.py` the way `pm` is. You choose the exact split and names.
2. **Hold-out hook.** A target names a Python module in config, and the registry loads it with `importlib` and checks it against a typed protocol (`check_input_path`, `scan_terms`, `scan_file`, `Match`). With none configured, nothing is held out. Configured but unloadable, or not matching the protocol, means every registration is refused with a receipt (spec-F3). Lean on where the config lives: `[tool.agentic-mbse.research]` in the target's `pyproject.toml`, which needs no new file. Entry points rejected because fusion-tea's scripts are not a package. You pick.
3. **External source kind.** Replace `ZoteroSource` with a neutral externally keyed local-file kind. Existing rows store `zotero_key`, so either the caller names the key field (the registry stays neutral and fusion-tea rows match unchanged) or the registry stores a generic field and reads the old one as an alias. Lean: caller-named field, because it needs no alias rule in shipped code. Keep the batch index profile.
4. **One owner for the shared writers.** fusion-tea's Zotero scripts import `RegistryPaths`, the manifest helpers and the index writer from the package, and `zotero_lib.py` keeps only Zotero API code. Rejected: two copies of the same writers in two repos.
5. **The index the registry writes into.** `register` works with the index `init` ships and with existing user-owned indexes. Choose an anchor rule that accepts both shipped and fusion-tea headings, with a fallback. `docs/source-index.md` gains registered types (`url`, `local_pdf`), separate from the hand-curated types, and says how commands treat each. The registry, the `manage-sources` skill and the doc must all agree.
6. **`manage-sources` never edits `SOURCE_INDEX.md` directly.** Every write goes through a CLI call under the registry's lock: `register` for a capturable document, `retire` for a registered source, plus the smallest surface that adds, edits and removes a hand-curated entry. Listing labels registered and hand-curated entries. Name the subcommands, and keep the new CLI surface minimal.
7. **Test split.** Assign each of the 20 files in `tests/research/`: move with a fake hook, stay in fusion-tea, or split. Moved tests use the index `init` ships, not fusion-tea's. Where a test exists to pin fusion-tea's live data or the ARIES-CS term list, it stays in fusion-tea.
8. **Docs and the decision record.** `docs/research-seam.md` is the generalized operator guide, with ADR-0008 condensed into it. It is a dated snapshot cited by fusion-tea path and commit, using the same authority stance as `docs/goal-layer-decisions.md`. Lean: put it in the seam guide, not the goal-layer decisions doc, because identity is a seam rule the goal layer only consumes.
9. **run-goal relabel.** Give the exact replacement for `skills/run-goal/SKILL.md:66-68` and the class-to-outcome table, and say whether the table lives in `run-goal` or the runbook. Keep the existing delegation sentence's Claude and Codex forms.
10. **fusion-tea side.** Design it as orchestrator-run work with exact file changes: delete the two scripts and the local `research-acquire` command and its `.gitignore` whitelist line; rewrite `CLAUDE.md:11` to point at the installed skill and CLI; set the hook config to its guard; point Zotero ingest at the package; cut `tests/research/` down to what stays; add ledger rows. Also a post-merge runbook (pin move, re-init, suites). The orchestrator cuts the fusion-tea worktree.
11. **Dry runs (spec criteria 2 and 7).** Orchestrator-run, each with `claude -p --setting-sources project,local` in a scratch target outside any repo, toolkit installed from a built wheel. Name a small open-access source for the end-to-end request, and a short script of user actions for the `manage-sources` run.

## Execution constraints the plan will inherit

- Stage subagents cannot read or write fusion-tea, `~/.claude/`, or anything outside this worktree. Mark every step that needs fusion-tea, a scratch target outside the repo, or a live `claude -p` run as orchestrator-run.
- An implement stage started fresh can commit; a resumed one cannot. Size phases so each fits one implement session.

## Keep it tight

The design should be as short as its decisions allow. Give each decision with its rejected alternative in one line. Give exact text where wording is the decision: the run-goal replacement, the class table, the `docs/source-index.md` type rows, the hook config. List changes at file level. Do not restate the spec. Re-estimate effort against the epic's 2.5 days and record any overrun with its cause.
