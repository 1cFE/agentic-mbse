# goal-layer-port evidence

Evidence for `WRAP-SPLIT` Item 2. Files marked "O1", "O2" or "O3" are written by the orchestrator-run phases of `plan.md`, which need fusion-tea, a scratch target or a live agent; they do not exist until those phases run.

## By success criterion

- **SC1 Install:** `sc1-install.txt`; `tests/test_goal_layer.py` (install under `claude`, `codex`, `both` and `--dev`, and the narrative-link test run from a copy and from a `--dev` link).
- **SC2 Nothing points at fusion-tea:** `sc2-sc3-install.txt` (the grep over a fresh install); `tests/test_goal_layer.py::test_goal_text_points_at_nothing_in_fusion_tea` and `::test_every_cited_adr_is_in_the_decision_record`.
- **SC3 Installed references resolve:** `sc2-sc3-install.txt` (the resolver and the path tests); `tests/test_goal_layer.py::test_installed_goal_references_resolve`; `tests/test_shipped_text.py`; `tests/test_packaged_guidance_contract.py::test_built_wheel_carries_the_resolver_reached_goal_layer_documents`.
- **SC4 Fresh-target dry run:** `dry-run/` (O3; O0 may write `dry-run/install.md` earlier).
- **SC5 The rule fits the enforcement system:** (a), (b), (c), (f), (g) and (h) are pinned in `tests/test_modeling_command_contracts.py`; `sc5f-reverted-edit.txt` shows one removal failing (f); `sc5d-reach-trace.md` (d); (e) is the `skills/requirements-tracking/SKILL.md` diff in commit `312d16a`; the "adds only cross-reference lines" half of (h) is that commit's diff of `docs/patterns/constraints.md` and `skills/sysml-conventions/SKILL.md` (2 insertions, 0 deletions each, `plan.md` Phase 2).
- **SC6 Content and provenance:** `sc6-crosswalk.md`; the fresh reviews in `design-review.md` (round 1 § SC6 fresh check, and round 2); `sc6-delta-check.md` (O1).
- **SC7 fusion-tea branch:** `fusion-tea/branch-diff-F1.txt` and `fusion-tea/branch-log.txt` (O1).
- **SC8 fusion-tea rehearsal:** `fusion-tea/rehearsal/` (O2), and the "Observed in the rehearsal" slots of `fusion-tea-runbook.md` (O2). The resolver hop in fusion-tea's own environment runs in F2, after the merge (`fusion-tea-runbook.md` step 5).
- **SC9 Ledger:** `.project/active/wrap-split-migration-ledger.md` § Item 2.
- **SC10 Decisions:** `sc10-decision-record.md`. Its two sources the snapshot could not show are confirmed there by the orchestrator: the probe record exists at `2b1e9f9d5`, and the 2026-09-14 request is cited in fusion-tea but never quoted.
- **SC11 Checks:** each phase's "Shared checks" note in `plan.md`. Lint and type checks are judged as parity with `main` (118 ruff, 88 mypy), per the orchestrator note after Phase 2.
- **SC12 Method preserved:** `sc12-hunks.md`, with the diffs in `sc12/`.

## Edits outside this item's own files, for Item 4

From design § Integration Strategy. Each was made only where placing the design-choice rule required it, and Item 4's read-through should cover it:

- `project_templates/MODELING_PROCESS.md.template` (the "Process Selection" row, the "Architecture & Design" clause, the technical-pattern row and the binding-row semicolon) and the `project_templates/MODELING_GUIDE.md.template` pattern index row;
- `docs/patterns/README.md` (index row) and `docs/patterns/constraints.md` (one cross-reference line);
- `skills/sysml-conventions/SKILL.md` (one cross-reference line) and `skills/sysml-conventions/references/stencils.md` (index row);
- `skills/requirements-tracking/SKILL.md` (tier text), `skills/review-model/SKILL.md` and `skills/model-validation/SKILL.md` (one pointer each), and `skills/orchestrate-modeling/SKILL.md:57` (names `/run-goal`).

One gap for the same read-through: the repo `README.md` § Initialize Project lists what `init` installs but does not name `tests/`, where the goal layer now installs `tests/orchestration/test_narrative_links.py`.

## Follow-ups for close to file

- **Dev-mode ignore marker.** A target already initialized with `--dev` keeps its old ignore section on re-init: `_update_gitignore_for_dev_mode` returns early when the marker line is present (`src/agentic_mbse/cli/__init__.py`), so the three new goal-layer lines are never appended and the new links show as untracked. Fresh `--dev` installs are correct. (design § Potential Risks; `plan.md` Phase 4 notes.)
- **Per-design literal/bound attribute listing.** Validation levels 1–6 cannot check the design-choice rule, because a validator cannot tell a physical identity from a design-selection policy. A listing of which attributes in a design are literal inputs and which are bound expressions would support the review the rule requires. (spec § Non-Goals.)
