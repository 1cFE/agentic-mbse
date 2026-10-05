# Orchestrator-run acceptance evidence — pm-registry-integrity

**Recorded:** 2026-10-04 by the orchestrator. **Code under test:** `b8bbf8d` (phases 1 to 3b committed). **Inputs:** read-only copies of fusion-tea's registry files at `.orchestrate-logs/ft-snapshot/` (gitignored), captured 2026-10-04 15:35 PDT from `~/1cfe/fusion-tea`. Scripts: `snapshot_parse.py` (E3), `e4_check.py` (E4), both in that folder; raw outputs `baseline.json`, `after_final.json`, `e4_result_b8bbf8d.txt`.

## E3 — parse snapshot of fusion-tea's real files, before vs after

Baseline captured against unchanged code at `9b82006`. Compared against `b8bbf8d`.

| File | Result |
|---|---|
| `ARCHITECTURE.md` (AD) | identical |
| `BACKLOG.md` (WI) | identical |
| `KNOWLEDGE.md` (DI) | identical |
| `OVERVIEW.md` (G, AQ) | identical |
| `REQUIREMENTS.md` (PR) | identical |
| `VALIDATION_MATRIX.md` (SV) | one record added, `SV-035`; zero removed; zero changed; one warning removed (row 34, the former `SV-035` Type error); zero warnings added |

Verdict: holds exactly as the spec requires.

## E4 — end to end on a copy of fusion-tea's real matrix and knowledge file

All 14 expectations pass:

- `SV-035` parses; its description and Expected cells hold literal `|rel dev|` with no backslash; Type `baseline`; Status `passing`.
- `SV-034` (raw pipes) is not parsed and still produces a warning.
- `add-validation` with a description containing a literal `|` succeeds, mints `SV-136` (max token in file `SV-135`), adds exactly one line, removes or rewrites none, and the new value reads back identical.
- `add-insight` on the `KNOWLEDGE.md` copy mints `DI-015`: live records end at `DI-011`, the archive note names `DI-014`. Before the fix it minted `DI-012`.

## Backlog write-back round trip (design review question 2)

`_load_backlog` then `_write_backlog` on a copy of fusion-tea's `BACKLOG.md`: frontmatter byte-identical, 4 epics and 43 standalone items parsed, zero warnings.

## Interim runs

- E4 at `e9fd8b1` (after phase 2): PASS. E3 at `e9fd8b1`: same result as final.
- E4 at `9b82006` (before any change): FAIL on three expectations, `SV-035` parses, new value reads back identical, next DI is `DI-015`. Those are the three defects.
