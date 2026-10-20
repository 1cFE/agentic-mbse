Write the spec for EXEC-SUBSET-CONTRACT **Item 3: L6 integration and execution-target settings**.

Output: `.project/active/l6-subset-profile/spec.md`.

## Source of truth

- The epic `.project/backlog/epic_executable-subset-contract.md`: Item 3 in full, Design principles, Success Criteria (the execution-target bullet), and Items 1, 2, 5, 6 for boundaries.
- Align record: `.project/active/l6-subset-profile/briefs/align.md` — the owner's decisions of 2026-10-18 (setting in `pyproject.toml`, unset = warnings, `native` = info, `generated` = errors for refusals, CLI override, exclusions/omissions = warnings under `generated`) and gates R3-1, R3-2 and the Item 2 boundary.
- Item 1 (merged): the contract and evaluator in `src/agentic_mbse/sysml/subset_profile.py` with its packaged records; archive `.project/completed/20261018_exec-subset-profile/` (spec, design, ADR 0001 at `.project/adr/0001-*.md`, P-0001 at `.project/product/0001-*.md`, R3 table in `evidence/r3-proposal.md` with the Item 3 obligations routed there, product-lens impl-F1/F2 about how `CLEAR` and `REFUSED_INCOMPLETE` must be presented).
- Item 4 (merged): L2 positional check; archive `.project/completed/20261018_positional-binding-check/` — reuse its CLI option and project-root discovery patterns (`find_project_root`, strict TOML) rather than inventing new ones.
- Existing code: `src/agentic_mbse/validation/level6_architecture.py`, `adr002.py`, `runner.py`, `common.py`; `src/agentic_mbse/cli/` (`validate`, `init`); `src/agentic_mbse/cli/installation.py` and CLAUDE.md § Init File Ownership (native settings are preserved even under `--force`).
- Read-only consumers for evidence: `~/src/dc3` (`808464d`, `60b44d5`), `~/src/fusion-tea` (`f96ad312`). Never modify them; use `git archive` copies. Do not touch `~/src/sysml-codegen` or any Item 2 artifact.

## Settled items

The owner decisions in the align record, graded as recorded there. Inherited from the epic: malformed TOML and unknown values are errors, not unset; check failures remain errors for checks actually requested regardless of target, never downgraded into a native summary; native correctness errors remain errors; ADR-002 placement and manifests keep their own applicability; the 27 broad exception sites in `level6_architecture.py` and `adr002.py` report `L6_CHECK_ERROR` and distinguish failed metrics from clean counts; fix the stale resolver citation; README, model-validation guidance and CLI output state the profile version, assessed scope, incompleteness and the L6 vs `sysml-codegen check` boundary.

## Gates — record as open, do not decide

R3-1 (relaxing an existing L6 error) and R3-2 (a passing project starting to fail with target unset). The audit of existing L6 checks must list every check, what it does today, and its disposition, so any R3-1/R3-2 case is visible.

## What I want from the spec

- Requirements graded per `.claude/rules/capture-fidelity.md`.
- Evaluatable success criteria naming the artifact or test, including: every settings state (generated, native, unset, malformed, unknown, CLI override), project-root discovery from the validated path and behavior outside a project, `init` (explicit option, interactive choice, noninteractive leaves it unset with actionable output, preservation of unrelated TOML and comments under `--force`), one explicit L6 run on dc3 baseline showing the confirmed categories, both String spellings agreeing, and native summaries never hiding check failures.
- How `CLEAR`, `REFUSED_INCOMPLETE`, `unconfirmed` and `unverified` are presented so no state reads as "will generate" when it is not (Item 1 impl-F1/F2).
- Decide and record ambiguities as `[INFERRED]` with reasoning, unless they touch R3-1, R3-2 or Item 2.
- Proportionate: this is L6 wiring, a setting, init support, a legacy-check audit and docs.
