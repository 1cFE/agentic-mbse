# study-layer-to-codegen (WRAP-SPLIT Item 3) — pointer

The item's spec, design, plan and evidence live in sysml-codegen, because the code lands there and stage agents can only read their own repository ([AGENT] orchestrator decision 2, 2026-10-12).

- sysml-codegen branch `study-layer-to-codegen` (worktree `/home/reid/1cfe/sysml-codegen-study-layer`, base `aa35f06`), folder `.project/active/study-layer-to-codegen/`.
- This repository carries the installer API the item builds on (`installer/v1`, commit `0843fe2` on this branch), the stage brief for it in `briefs/`, and, before close, the fusion-tea adoption runbook and the Item 3 section of `../wrap-split-migration-ledger.md`.
- fusion-tea adopts the moved layer after merge, by runbook, because its sysml-codegen pin `8a758e9` is 142 commits behind `main`. Moving that pin is the owner's call.

## State at hand-off (2026-10-12)

**Certified with follow-ups.** All twelve spec criteria met; every audit finding closed. Evidence: wheel install 25/25 (SC1), fresh-target dry run with a cold administrator reading (SC4), parity 28/28 against fusion-tea's originals (SC12), fusion-tea adoption rehearsed on a disposable copy (SC9), 75 moved lines with fusion-tea homes and ledger rows (SC10). sysml-codegen suite 2744 passed plus the one pre-existing failure; agentic-mbse at its baseline.

| Repo | Branch | Worktree | Head |
|---|---|---|---|
| sysml-codegen | `study-layer-to-codegen` (base `aa35f06`) | `/home/reid/1cfe/sysml-codegen-study-layer` | see `git log` |
| agentic-mbse | `study-layer-to-codegen` (base `ac5fb1a`) | `/home/reid/1cfe/agentic-mbse-study-layer` | see `git log` |
| fusion-tea | `study-layer-adoption` (base `c42ed1d8a`) | `/home/reid/1cfe/fusion-tea-study-layer` | `aab9b9ba3` |

**Merge order.** agentic-mbse first (sysml-codegen's `install-commands` needs `installer/v1`). Then set sysml-codegen's `INSTALLER_API_REVISION` (`cli/install.py`) and the README's minimum revision to the agentic-mbse merge SHA, run `adr.sh index` when merging sysml-codegen `main` (ADRs 0011–0014 landed there), and merge sysml-codegen. fusion-tea's `study-layer-adoption` merges only after the adoption runbook's switch (steps 5–7).

**Close checklist** (from the re-audit):
- Move the adoption runbook into this folder **together with what it cites**: sysml-codegen `evidence/fusion-tea/` (wrappers, `routes.sed`, patches, `check_anchors.py`), `evidence/read-through.md` and `evidence/rehearsal/`. sysml-codegen deletes item folders at close, and the runbook's `$EV` paths point there.
- File DD12's `study check-record` and DD19's kept smells (gate 4's `--snapshot` flag) in sysml-codegen's backlog; six other follow-ups are already there.
- Write the study-layer product-ledger entry in sysml-codegen `.project/product/` (backlog `STUDY-LAYER-PRODUCT-ENTRY`).
- Product-lens audit-F5 (one README sentence) to file; audit-F6 (the glue-ledger question) is the owner's.
- Moving fusion-tea's sysml-codegen pin is the owner's call: the generator moves from `8a758e9` to the merge commit, and gate 2 then refuses fusion-tea packages until they are regenerated (runbook step 9).
