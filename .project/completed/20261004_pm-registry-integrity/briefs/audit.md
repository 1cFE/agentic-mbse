# Brief: audit — pm-registry-integrity

**Stage:** `/_my_audit`. **Item:** `.project/active/pm-registry-integrity/`. Certify the implementation at HEAD against `spec.md` (contract), `design.md` (approved), and `plan.md` (all phases complete). Write `audit.md` beside them. You did not implement any of this; do not trust the Implementation Record's claims, re-run what you can.

## What this work is for

[AGENT, re-derived] Registry entries and their IDs are stable referents that other artifacts cite by spelling. The audit question is: can a supported registry record still disappear silently, or an ID present in a registry file still be minted twice, through any PM read or write? Answer it from the code and the tests, not the plan's prose.

## Evidence already recorded

- `acceptance-evidence.md`: the orchestrator's E3 and E4 runs at HEAD against copies of fusion-tea's real files, plus the backlog round-trip. Read it; you can rerun `e4_check.py` and `snapshot_parse.py` from `.orchestrate-logs/ft-snapshot/` yourself (`uv run python .orchestrate-logs/ft-snapshot/e4_check.py .orchestrate-logs/ft-snapshot`). Do not edit them.
- `spec-review.md`, `spec-review-2.md`, `design-review.md` carry probes that reproduce each original defect; rerunning them at HEAD should show every defect closed or refused.
- Gates run under the parity rule recorded in the plan (repo-wide ruff and mypy were already failing at base; the bar is no worse, and PM-scoped clean).

## What I want checked hardest

1. Each of the six spec criteria traced to a test that fails if the behaviour regresses. Name the test. If a criterion rests only on prose, say so.
2. Every refusal R1 to R9 in `design.md` D9: a test exists, and the file is unchanged after the refusal (not just "success is False").
3. The strict xfail markers from phase 1 are gone and E1 passes for the right reason.
4. Dead code, duplicated splitting or ID logic, leftover debug, TODOs, and whether `_write_backlog` still accepting `BacklogData` is justified or a test-only convenience that belongs elsewhere.
5. The additions-only claim: no existing test line removed or weakened against base `e5bd0db`.
6. Any behaviour change outside the spec's scope that a fusion-tea user would notice (new refusals on previously succeeding calls, warning text changes).

Verdict options: Certified, Certified with follow-ups (list them as backlog-ready one-liners), or Not certified (name the must-fix). Do not edit the backlog or tracking files; the orchestrator does. End with `ARTIFACT: .project/active/pm-registry-integrity/audit.md`.
