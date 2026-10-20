Design EXEC-SUBSET-CONTRACT Item 3 from `.project/active/l6-subset-profile/spec.md` (reviewed; Resolutions in `spec-review.md`).

Output: `.project/active/l6-subset-profile/design.md`.

Read: the spec, spec-review, `briefs/align.md` (owner decisions; gate outcomes; owner boundary: no Item 2, no sysml-codegen writes), `product-lens.md`, the epic's Item 3. Code: `src/agentic_mbse/validation/` (`level6_architecture.py`, `adr002.py`, `runner.py`, `common.py`, and Item 4's `positional_check.py`/`positional_pins.py` for CLI-option and project-root patterns), `src/agentic_mbse/sysml/subset_profile.py` (Item 1 contract), `src/agentic_mbse/project_root.py`, `src/agentic_mbse/research/holdout.py`, `src/agentic_mbse/cli/` (`validate`, `init`) and `cli/installation.py` with CLAUDE.md § Init File Ownership. Read-only: ~/src/dc3, ~/src/fusion-tea.

Intent [AGENT, ratified by owner 2026-10-18]: `validate` tells a modeler up front whether the generator will accept the model, using the Item 1 contract, with the project's `execution-target` setting deciding severity (unset = warnings, `native` = info, `generated` = errors for refusals), never claiming "will generate", and never letting a broken check pass.

What I want:
- **Engineering bar:** one settings module owns `[tool.agentic-mbse]` parsing with a closed key set (shared with the research holdout guard, each validating only its own values); a pure severity-policy function maps (contract outcome or legacy finding, target) → severity with a table test; L6 consumes the contract rather than re-deriving decisions; failures are named structured results; deterministic output.
- **Concrete data model and the severity table** as types and a table, not prose.
- **The legacy-check audit** as a table: every L6/ADR-002 check, today's severity, its category with evidence, its disposition per target.
- **The runner change** for crashed levels and the JSON full report.
- **`init`:** how the key is added safely without a new heavy dependency if avoidable (justify `tomlkit` if needed), the refuse-don't-rewrite cases, and preservation under `--force`.
- **The before/after safeguard** as a script over `git archive` copies of dc3 (808464d, 60b44d5) and fusion-tea (f96ad312), running full `validate --complete` at base `ebb3d467` and at the branch, proving which code ran and which project root was resolved.
- **De-risk flags** for anything you could not verify by reading; say whether a learning test or spike is needed and what it must show.
- Decide and record what the spec left to design.
