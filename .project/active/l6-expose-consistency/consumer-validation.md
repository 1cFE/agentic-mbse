# Consumer validation: fusion-tea models, before and after

**Date:** 2026-10-04. **Method:** `validate_architecture()` run read-only against fusion-tea (`goal/magnet-material-comparison` at `97fabad31`) from two agentic-mbse trees: pre-fix `5abcf70` (equivalent to fusion-tea's pinned `4433888`, whose installed copy still carries `_is_expose_pattern`) and post-fix `3f442ce`. Issues compared as (code, element, location) multisets. Scripts were scratch; this file is the record.

| Model set | Files | Design attrs checked | L6 issues before | L6 issues after | Removed | Added |
|---|---|---|---|---|---|---|
| `models/` (main) | 80 | 6180 | 7734 | 408 | 7326 | 0 |
| `exploration/stellarator_e2e/models/` (active study) | 40 | 1164 | 1848 | 196 | 1652 | 0 |

- Every removed diagnostic was either `V4_UNSUPPORTED_OPERATOR` for `.` or `L6_DESIGN_ATTR_UNEXTRACTABLE`, and every attribute that lost one carries no diagnostic afterwards (3663 attributes in `models/`, 917 in the study set). No other code changed count. Metrics are identical before and after.
- Remaining `models/` issues: 119 `L6_DESIGN_ATTR_INCOMPLETE` (101 in `designs/generic_mfe`), 96 `V2_DYNAMIC_EXPRESSION`, 85 `V4` (all `.`, every one on an attribute V2 also flags), 108 `UNEXTRACTABLE` (96 on V2-flagged attributes; the other 12 are candidates for the FORMULA-completeness follow-up recorded in design Non-Goals, e.g. `plasma_profile::edge_density`, `magnet_subsystem::subsystem::duty::turn_current`).
- The remaining V4 `.` reports all duplicate a V2 report on the same derived expression. That is the "V4 duplicates V2 on non-EXPOSE chains" non-goal, now quantified.

**What this does and does not show.** It shows the fix removes exactly the EXPOSE false positives on the real consumer corpus and changes nothing else there. It does not show that fusion-tea's workflow benefits yet: fusion-tea pins agentic-mbse by git rev in `pyproject.toml`/`uv.lock` and its venv has the pre-fix code. Fusion-tea's guides tell agents to run `agentic-mbse validate models/`, which stops at the first failing level, so L6 has been failing there with ~7700 issues; whether anyone reads past the first five lines is unknown.

## In-situ run through fusion-tea's own CLI (2026-10-04, option 1)

Owner-approved: this checkout was installed editable into fusion-tea's venv (`uv pip install --reinstall --no-deps -e /home/reid/1cfe/agentic-mbse`; `uv run --no-sync` is required, since plain `uv run` re-syncs to the lock and silently restores the pinned `4433888`). fusion-tea's import path then resolved to `/home/reid/1cfe/agentic-mbse/src/agentic_mbse`. Commands run from fusion-tea: `uv run --no-sync agentic-mbse validate --complete --verbose <path>`.

| Model set | L6 issues (CLI) | Matches library-call run | Other failing levels | Wall time |
|---|---|---|---|---|
| `models/` | 408 | yes (408) | L2: 340 (literal-bound calc inputs, pre-existing) | 10m28s |
| `exploration/stellarator_e2e/models/` | 196 | yes (196) | L2: 52 (same kind) | 1m02s |

Levels 1, 3, 4, 5 pass on both. The Level 2 warnings are unrelated to this item. The CLI still prints five issues then "and N more"; the per-code counts in the Level 6 metrics block are the readable signal.

**State left behind:** fusion-tea's venv holds the editable install until the next plain `uv run` or `uv sync` there, which restores the pinned pre-fix version. No committed fusion-tea file was changed.

## Recorded fusion-tea work-item scenarios, rerun with the fix (2026-10-04)

fusion-tea work items have been recording "inherited Level 6 debt" and hand-attributing it per item because the CLI truncates at five issues (WI-049 built its own before/after multiset comparison in `implementation/l6-before.json`). Rerunning their recorded commands through fusion-tea's CLI with the editable install (`uv run --no-sync`):

| Work item and recorded path | Recorded before | After fix | Removed | Added |
|---|---|---|---|---|
| WI-099 `exploration/magnet_materials/input_models` | 43 L6 errors, "all Unsupported operator '.' on EXPOSE attributes" (implementation-notes.md:17) | **Level 6 passes; all six levels pass** | 43 | 0 |
| WI-049 `work/active/WI-049_ife-zero-discount-repair/prototype/models` | 50 (its `l6-before.json`) | 24 | 26 (13 V4 `.` + 13 UNEXTRACTABLE on 13 EXPOSE attributes, none V2-flagged) | 0 |
| WI-100 `exploration/stellarator_materials/units/reference/input_models` | not recorded | 196 (same set as the stellarator study) | — | — |

WI-049's remaining 24: 18 `L6_DESIGN_ATTR_INCOMPLETE`, 2 `V2_DYNAMIC_EXPRESSION`, and 2 V4 `.` plus 2 UNEXTRACTABLE on those same two derived expressions. Every remaining V4/UNEXTRACTABLE element is V2-flagged, i.e. a genuine derived expression.

**Usage observation.** The owner's live goal session on `goal/magnet-material-comparison` (commits `a9683fa1d`..`58b73d402`) changed no `.sysml` files and did not run `agentic-mbse validate`; the run-goal flow has no model-validation step. Across 48 goal trails under `work/orchestration/goals/`, none mentions `agentic-mbse validate`. Validation runs in the work-item (WI) flow, where 56 item folders reference it. So the fix lands in WI audits (where L6 debt attribution was manual) rather than in goal sessions.

## Owner-run probe in fusion-tea (2026-10-04) and a coverage finding

The owner's fusion-tea agent ran a scripted probe on `exploration/magnet_materials/input_models` (the WI-099 path): baseline all six levels pass; adding `attribute probe_expose : Real = conductor.element_area_total;` to `magnet_subsystem.sysml` produced no diagnostic and Level 6 still passed. That exercises the V4 half of the fix on a real consumer file (pre-fix, that line produced `V4_UNSUPPORTED_OPERATOR` for `.`; WI-099 recorded 43 such errors).

**Finding (pre-existing, not caused by this item):** "Design attrs checked" was 0 before and after. `check_design_attr_completeness` keeps its default `design_path_filter="designs"`, and the CLI exposes no way to change it, so a flat layout with no `designs/` directory gets zero completeness coverage. In fusion-tea this applies to at least `exploration/magnet_materials/input_models` and `exploration/exchanger_architecture/thermal_requirements/input_models`. WI-099's recorded "43 errors, all `.`" were therefore V4 only; the completeness half of the fix was never reachable on that path. The completeness half is exercised on `models/`, the stellarator set, and the WI-049 prototype (all have `designs/`). Follow-up candidate for close: either a CLI flag for the filter or a warning when the filter matches no files.

## Owner-run end-to-end probe on a `designs/` layout (2026-10-04) — all expectations met

The owner's fusion-tea agent ran the scripted probe on `work/active/WI-049_ife-zero-discount-repair/prototype/models` through fusion-tea's CLI (`uv run --no-sync`, editable install confirmed), editing `designs/generic_ife/ife_plant.sysml` inside `'IFE Power Plant'` and reverting afterwards (empty `git diff`, no commits).

| Step | Design attrs checked | INCOMPLETE | UNEXTRACTABLE | Issues found |
|---|---|---|---|---|
| Baseline | 50 | 18 | 2 | 24 |
| + `attribute probe_expose : Real = hawker_price.price;` | 51 | 18 | 2 | 24 |
| + `attribute probe_derived : Real = hawker_price.price * 0.95;` | 52 | 18 | 3 | 27 |
| Both removed | 50 | 18 | 2 | 24 |

The three new diagnostics in step 3 were all on `probe_derived`: `V2_DYNAMIC_EXPRESSION`, `V4_UNSUPPORTED_OPERATOR` (`.`), `L6_DESIGN_ATTR_UNEXTRACTABLE`. `probe_expose` received none at any step. Existing diagnostic identities were unchanged throughout, and the restored run reproduced the baseline exactly. This exercises both repaired checks (V4 and completeness) and the V2 control through the consumer's own entry point on a real design file. Spec success criteria 1–3 are thereby confirmed in situ.
