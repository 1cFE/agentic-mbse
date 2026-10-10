# SC12 lint parity against `main`

**Rule** (`spec.md:64`, pre-PR brief `d693589`): no findings beyond `main`'s baseline, and every file this item adds or edits is clean. `main` already fails ruff and mypy, so the comparison is per file.

**Baseline:** `main` at `06ac41d`, exported with `git archive` to `.orchestrate-logs/lint-baseline/main` and synced with `uv sync --frozen` (no optional extras), plan step 1.2. Raw outputs: `.orchestrate-logs/lint-baseline/{ruff-check,ruff-format,mypy}-main.txt`.

**Branch:** the integration worktree with this item's changes through the Phase 8 docs step, re-run after the audit fixes and again after plan Phase 9 (both 2026-10-09), each with the same file list and the same numbers below. Raw outputs: `.orchestrate-logs/lint-baseline/*-branch*.txt`. Script: `.orchestrate-logs/lint-baseline/parity.py`, plus `compare_mypy.py` for the same-environment mypy comparison.

## Files this item adds or edits (vs `main`)

`git diff --name-only --diff-filter=AMR main -- 'src/*.py' 'tests/*.py'`, plus the evidence script:

- `src/agentic_mbse/cli/__init__.py`, `src/agentic_mbse/cli/installation.py`
- `tests/helpers/shipped.py`, `tests/test_cli.py`, `tests/test_installation.py`, `tests/test_modeling_command_contracts.py`, `tests/test_packaged_guidance_contract.py`, `tests/test_shipped_text.py`
- `.project/active/native-skill-distribution/evidence/reconcile.py`

All nine are clean: `ruff check` "All checks passed!", `ruff format --check` "9 files already formatted", `mypy reconcile.py` "no issues", and no mypy error names a changed `src/` file.

## Totals and the per-file comparison

| Tool | `main` | Branch | In changed files | Other files equal `main` line for line |
|---|---|---|---|---|
| `ruff check src/ tests/` | 118 | 118 | 0 | yes (118 = 118) |
| `ruff format --check src/ tests/` (files to reformat) | 78 | 77 | 0 | yes (77 = 77) |
| `mypy src/`, same no-extras environment as the baseline | 101 | 98 | 0 | yes (98 = 98) |

- **ruff format, 78 → 77:** `tests/test_cli.py` was on `main`'s list and is formatted now, because this item edits it.
- **mypy, 101 → 98:** the three gone are `main`'s errors in `src/agentic_mbse/cli/__init__.py` (`:325`, `:352`, `:1174`, all `no-any-return`, in code the native branch's rewrite of that file removed or retyped). That file is edited here and is now clean.
- **Same environment for mypy.** The orchestrator re-synced the worktree with all extras before Phase 4, and mypy's findings depend on which optional packages are installed: with extras, 14 `import-not-found` errors disappear and 4 `attr-defined` errors appear in unchanged extraction modules. Comparing a with-extras branch run against the no-extras baseline would mix tool and code differences. So the branch was checked with the baseline's own environment: `uv run --directory .orchestrate-logs/lint-baseline/main --frozen mypy ../../../src/` (61 files checked: `main`'s 60 plus `installation.py`). For reference, `mypy src/` in the all-extras worktree reports 88 errors, none in changed files.

**Result: parity holds.** No finding beyond `main`'s baseline, and every file this item adds or edits is clean.
