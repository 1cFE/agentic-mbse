---
name: my-pre-pr
description: Run project-defined quality checks, fix issues, and submit a PR. Branch gate, run after closing the items that ship in the PR — per item when it ships alone, once at epic end otherwise. Not an item stage.
---

Generated from `claude-pack/commands/_my_pre_pr.md`. This is a command-derived Codex skill. Rebuild it instead of editing it by hand.

# Pre-PR Command

**Purpose:** Run project-defined quality checks and submit a PR
**Input:** None required — operates on the current branch state
**Output:** Clean checks, resolved issues, and (optionally) a submitted PR

## Overview

You are a pre-PR quality gate. Your job is to scope the PR, run the project's quality checks, fix what you can, work with the user to resolve what you can't, and offer to submit.

You do not check spec/design conformance — that is ``my-audit``. You run the project's own tooling and catch mechanical issues.

**When to run: after ``my-close``, once per PR — not per item, phase, or session.** This is a
branch gate, not a pipeline stage. Run it when the branch actually has something to ship:

- after closing an item that is shippable on its own, or
- once at the end of an epic, when its items ship together as one branch.

By this point the items shipping in the PR have been audited and closed. If they haven't — no
audit, or still sitting unarchived in `active/` — surface that to the user before proceeding.

## Step 1: Scope the PR

1. Review git state: `git log`, `git diff`, `git status`. Understand what commits and files will be in this PR, and what branch it targets.
2. Present a brief summary to the user: what's in scope, how many commits, what areas of the codebase are touched.
3. If anything is unclear — uncommitted changes, ambiguous base branch, commits that look unrelated — ask the user before proceeding.

## Step 2: Run Quality Checks

Read CLAUDE.md (and any project config it references) to discover what checks the project defines: test commands, linters, formatters, type checkers.

Run each check the project specifies. If the project defines no checks, fall back to reasonable defaults for the detected ecosystem:

**Python fallback** (if pyproject.toml, setup.py, or .py files are present):
- `pytest` (or `python -m pytest`) for tests
- `ruff check .` for linting
- `ruff format --check .` for formatting

For other ecosystems, inspect package.json, Makefile, Cargo.toml, etc. for standard check commands. If nothing is discoverable, tell the user and ask what to run.

Also scan changed files for:
- Debug artifacts (breakpoints, print statements used for debugging, TODO/FIXME left from this PR's work)
- Files that look like secrets (.env, credentials, API keys)
- Large binary files that shouldn't be committed

**Open product-lens findings.** Each work item in this PR's scope that reached spec or later usually has a `product-lens.md` — in `.project/active/{item}/`, or in `.project/completed/{date}_{item}/` once ``my-close`` has archived it. If one records a `BLOCK` that no later block resolves, name it in the summary so the user sees it before submitting. It does not stop the PR.

## Step 3: Fix and Resolve

**Low-risk issues** — fix directly without asking:
- Formatting (run the formatter)
- Import sorting
- Simple lint auto-fixes (unused imports, trailing whitespace)

These don't change behavior. Apply them, re-run checks to confirm, and note what you fixed.

**Medium and high-risk issues** — work through with the user:
- Test failures
- Type errors
- Lint violations that require judgment (e.g., complexity warnings, naming)
- Pattern violations or code smells in the changed files

For each issue: show what's wrong (`file:line`), explain the concern, and work with the user to resolve it. Don't just list problems and stop — this is interactive.

Re-run checks after fixes to confirm everything is clean.

## Step 4: Submit PR

Once checks pass (or the user decides remaining issues are acceptable):

1. Offer to submit the PR.
2. Follow the project's CLAUDE.md conventions for PR creation — title format, body structure, attribution (e.g., `Co-Authored-By` trailers), target branch.
3. If CLAUDE.md has no PR conventions, use a sensible default: short title, summary body with what changed and why, and ask the user about attribution preferences.
4. Create the PR using `gh pr create` and return the URL.

If the user declines submission, that's fine — the checks are done and the branch is clean.

---

**Related Commands:**
- Before pre-PR: ``my-audit`` to certify, then ``my-close`` to archive the items shipping in this PR
- After pre-PR: the PR merges; ``my-wrap-up`` to persist session state

**Last Updated**: 2026-08-08 — pre-PR is the branch gate and runs after close: per item when the item ships on its own, once at epic end otherwise (owner decision).

