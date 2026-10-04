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
