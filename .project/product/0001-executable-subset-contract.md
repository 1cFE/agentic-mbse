---
id: 0001
title: agentic-mbse publishes a versioned executable-subset contract: refused only with a recorded generator probe, CLEAR only over the implemented rules
date: 2026-10-18
owner: Reid Westwood
status: superseded
amended_by: []
superseded_by: 0004
supersedes: null
provenance: "[AGENT] (ratified by owner, 2026-10-18)"
surfaces: [agentic_mbse.sysml.subset_profile, sysml-codegen, l6, guidance]
checked: 2026-10-18 @ cff1203e
---

## Promise

agentic-mbse ships one versioned record (`SUBSET_PROFILE_VERSION`) of which model shapes, in which contexts, the pinned sysml-codegen generator refuses, excludes, omits or admits, plus a pure evaluator that applies it to a user model. A shape is reported `refused` only when a retained probe of the pinned generator observed that refusal in that context; anything else is `unconfirmed`, missing facts are `unverified`, and `CLEAR` means clean over the implemented rules only, not "will generate".

## Authority

- [AGENT] (ratified by owner, 2026-10-18) `.project/adr/0001-subset-profile-capability-ownership.md` — ownership, invariants 1–6.
- [INHERITED: epic] `.project/backlog/epic_executable-subset-contract.md` Item 1 objective and success criteria.
- `.project/completed/20261018_exec-subset-profile/spec.md` (reviewed; Change Log) and `.project/completed/20261018_exec-subset-profile/design.md` § R1 (owner decision "A (ii)").

## Evidence

- Loader gate and evidence tests: `tests/test_sysml/test_subset_profile_records.py`, `tests/test_subset_probe_evidence.py`; 14 R2 mutations caught (`.project/completed/20261018_exec-subset-profile/evidence/r2-mutations.md`).
- 80/80 probes certify at sysml-codegen `b5663c07`; occurrence parity 73/73; acceptance runs in `.project/completed/20261018_exec-subset-profile/evidence/acceptance.md`.

## Scope

Library-level contract only as of 2026-10-18: no consumer is wired yet. Codegen integration is epic Item 2, L6 is Item 3, rendered guidance is Item 5.
