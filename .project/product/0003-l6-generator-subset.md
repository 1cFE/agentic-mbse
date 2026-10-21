---
id: 0003
title: validate L6 reports, in one run, which model shapes the pinned generator refuses, at a loudness set by the project's execution-target, and never claims the model will generate
date: 2026-10-20
owner: Reid Westwood
status: superseded
amended_by: []
superseded_by: 0005
supersedes: null
provenance: "[AGENT] (ratified by owner, 2026-10-18)"
surfaces: [validate L6, validate --execution-target, validate --json-report, init --execution-target, "pyproject.toml [tool.agentic-mbse]"]
checked: 2026-10-20 @ 92b9a9b5
---

## Promise

`agentic-mbse validate` L6 runs the executable-subset contract (`subset-profile/v1`) and reports refused, omitted, excluded, unconfirmed and unverified findings with locations, in one pass. How loud they are follows `execution-target`: warnings when unset, an INFO summary under `native`, errors for confirmed refusals under `generated`. Every verdict line says it is not a generation check, and a pass under unset or `generated` says generated compatibility is not established. A broken check fails the run under every target.

## Authority

- [AGENT] (ratified by owner, 2026-10-18) `.project/completed/20261020_l6-subset-profile/briefs/align.md` § Owner decisions.
- `.project/adr/0003-execution-target-setting.md`; `.project/adr/0001-subset-profile-capability-ownership.md`; P-0001.
- `.project/completed/20261020_l6-subset-profile/spec.md` (reviewed), `design.md` (rev 1, reviewed), `audit.md` (Certify).

## Evidence

- `tests/test_validation/test_l6_contract.py`, `test_l6_check_errors.py`, `test_l6_advisories.py`, `test_l6_settings_cli.py`, `tests/test_init_execution_target.py`, `tests/test_shipped_text.py`.
- dc3 `808464d`: 236 refused, 32 omitted, 6 unconfirmed, 50 unverified in one run; dc3 `60b44d5` clear; no consumer tree went from pass to fail (`.project/completed/20261020_l6-subset-profile/evidence/`).

## Scope

The contract is incomplete (its coverage line names what it does not assess) and L6 never runs the generator; asking sysml-codegen itself is Item 2.
