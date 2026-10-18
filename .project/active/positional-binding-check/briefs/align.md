# Orchestration Align record — EXEC-SUBSET-CONTRACT Item 4

**Date**: 2026-10-18
**Input**: `.project/backlog/epic_executable-subset-contract.md` Item 4
**Owner instruction**: "merged. continue" after Item 1 (PR #30) merged. The owner has asked that the run not stall on avoidable checkpoints ("what the fuck else am I going to wait for?"). Item 4 starts without a separate Align round because the epic already records its owner decision (D1) and its scope limits; this record states the gates the orchestrator applies.

## Reading of the work

[AGENT] Item 4 detects a demonstrated silent wrong-value hazard: an unprefixed calc-usage input whose implicit redefinition targets a differently named formal by position. Native SysIDE and generated/TEAx routes disagree on the reversed-subtraction fixture (-7 vs 7). The check reports the hazard in valid SysML; it does not change generator binding behavior.

## Route

[AGENT] spec → spec_review → design → design_review → plan → implement → audit, combining artifacts where proportionate (epic Item 4 Deliverables). `close` follows; `pre_pr` and PR per item, since Item 4 ships on its own. Branch `positional-binding-check` off `main` at `ccd57d83`. sysml-codegen, dc3 and fusion-tea are read-only.

## Gates

- [OWNER] D1 (approved 2026-10-15): new mismatches block; explicitly pinned legacy mismatches warn until migration. Settled.
- **R4-1 (reserved to owner):** any narrow suppression or "intentional positional use" disposition mechanism beyond what D1 states.
- **R4-2 (reserved to owner):** any change to generator binding behavior. Out of scope; the discrepancy is recorded upstream only.
- **R4-3 (reserved to owner):** any fusion-tea edit or migration. Not authorized by this epic.
- Premise surprise rule applies: if the 125 fusion-tea findings or the dc3 zero-finding result do not reproduce, surface it rather than tune the detector.

## Owner boundary (2026-10-18)

- [OWNER] "I am working with another agent on item 2, so do not touch that." Item 4 must not modify sysml-codegen or any Item 2 artifact. It records the generator semantic discrepancy as a finding for upstream only. sysml-codegen PR #21 (ADR 0018, `.project/adr/` only) was opened before this instruction.
