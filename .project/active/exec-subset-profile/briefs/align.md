# Orchestration Align record — EXEC-SUBSET-CONTRACT Item 1

**Date**: 2026-10-15
**Input**: `.project/backlog/epic_executable-subset-contract.md` Item 1
**Owner reply to Align**: "go" — accepted the reading, route, reserved gates and gap handling below without amendment.

## Reading of the work

[AGENT] (ratified by owner, 2026-10-15) Item 1 establishes one declared statement of which model shapes the generator admits, refuses, excludes or silently omits, with evidence, so the generator, L6 and guidance consume one contract. Item 1 builds that contract and its evidence base; codegen integration is Item 2, L6 severity is Item 3.

## Route

[AGENT] (ratified by owner, 2026-10-15) spec → spec_review → design → design_review → **owner gate R1** → plan → implement → audit. `close` and `pre_pr` are left to the owner. Branch `exec-subset-profile`. sysml-codegen (`b5663c07`) and dc3 (`808464d`, `60b44d5`) are read-only; nothing outside agentic-mbse is written.

## Reserved gates

- **R1 — Capability-policy ownership** (epic open decision 1). Halt after design_review; present the recommended fact/decision/consumer boundary; wait before plan/implement.
- **R2 — Any shared rule stricter than current generator behavior.** Halt that rule and ask; the epic calls this a behavior change requiring explicit review.
- **R3 — Absorption of GENERATOR-SUBSET-PATTERNS and disposition of remaining gaps** (epic open decision 4). Record a proposal; owner approves.

## Gap handling (ratified)

- D2's 500-site account is built in Item 1 at the pinned revision (in scope / handled elsewhere / follow-up), because rule boundaries depend on it; per-site stable codes and mutation tests stay in Item 2.
- Item 1 cannot claim generator-verified rules: independent screen-bypassing fixtures live in codegen (Item 2). Each rule records its generator evidence status as prototype or pending Item 2.
- "ADR 0007" is cited but `.project/adr/` holds only a README; design locates it or records the absence.
- "Inventory complete relative to the pinned generator surface" is read as complete relative to the scanner's recognized forms plus an explicit list of known blind spots.
