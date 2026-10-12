# study-layer-to-codegen (WRAP-SPLIT Item 3) — pointer

The item's spec, design, plan and evidence live in sysml-codegen, because the code lands there and stage agents can only read their own repository ([AGENT] orchestrator decision 2, 2026-10-12).

- sysml-codegen branch `study-layer-to-codegen` (worktree `/home/reid/1cfe/sysml-codegen-study-layer`, base `aa35f06`), folder `.project/active/study-layer-to-codegen/`.
- This repository carries the installer API the item builds on (`installer/v1`, commit `0843fe2` on this branch), the stage brief for it in `briefs/`, and, before close, the fusion-tea adoption runbook and the Item 3 section of `../wrap-split-migration-ledger.md`.
- fusion-tea adopts the moved layer after merge, by runbook, because its sysml-codegen pin `8a758e9` is 142 commits behind `main`. Moving that pin is the owner's call.
