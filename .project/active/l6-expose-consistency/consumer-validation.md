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
