# study-layer-to-codegen (WRAP-SPLIT Item 3)

fusion-tea's study layer now ships from sysml-codegen. `sysml-codegen install-commands` installs the `run-study` skill and a study-policy template, and `sysml-codegen study indicators|preflight|verify|integrate` runs the tools from the `sysml_codegen.study` package. Certified with follow-ups (all twelve spec criteria met; every audit finding closed or filed). Closed 2026-10-12.

## Where everything is

- **The item's artifacts** (spec, design, plan, reviews, audit, product lens, briefs, dry run, parity cases, install transcript) are in sysml-codegen git at `4dfe275`, under `.project/active/study-layer-to-codegen/`. sysml-codegen closes an item by deleting its folder, so the commit is the archive ([AGENT] orchestrator decision 2, 2026-10-12: the item lived there because the code lands there and stage agents read only their own repository).
- **This folder** holds what outlives sysml-codegen's close (design D10):
  - `evidence/fusion-tea-runbook.md`, the adoption runbook, with the kit it cites: `evidence/fusion-tea/` (wrappers, `routes.sed`, `declaration.toml`, the step-5 patches, the text drafts and `check_anchors.py`), `evidence/read-through.md`, `evidence/ledger-rows.md`, `evidence/rehearsal/` and `evidence/parity/` (the comparator and its report, without the cases);
  - `evidence/adoption-20261012.md`, the record of the real adoption;
  - `briefs/implement-installer-api.md`, the brief for this repository's part.
- **The ledger rows** are in `../../active/wrap-split-migration-ledger.md` § Item 3.

## What merged where

| Repo | Change | PR |
|---|---|---|
| agentic-mbse | `installer/v1`: `Installer(manifest=...)`, `install_bundle()`, `INSTALLER_API_VERSION` (`0843fe2`, `70d78d0`); Item 3 tracking and ledger rows | [#24](https://github.com/1cFE/agentic-mbse/pull/24), merged as `d42c8b9`, on top of #23 |
| sysml-codegen | `sysml_codegen.study`, `install-commands`, `sysml-codegen study`, the shipped skill text, ADRs 0015–0017, P-007, the close | [#20](https://github.com/1cFE/sysml-codegen/pull/20), merged as `b5663c0` |
| fusion-tea | agentic-mbse pin to `d42c8b9` (one move for Items 3 and 5) with Item 5's switch | [#127](https://github.com/1cFE/fusion-tea/pull/127), merged as `91c06cd4d` |
| fusion-tea | `study-layer-adoption`: the 75 moved lines' homes, the sysml-codegen pin move and the study-layer switch (`d58a899c1`), pinned to `b5663c0` (`d2f1aef20`); record in `evidence/adoption-20261012.md` | [#128](https://github.com/1cFE/fusion-tea/pull/128), stacked on #127; on `main` through [#129](https://github.com/1cFE/fusion-tea/pull/129) as `47b4c612d` |

## Key decisions

- **One distribution** ([AGENT], design D6). The tools are `sysml_codegen.study` inside sysml-codegen, so the contract reader always matches the generator that wrote the contract. Rejected: a separate distribution, and copying tool files into each target.
- **No agentic-mbse version bump** ([AGENT], ADR-0016 in sysml-codegen). sysml-codegen's committed snapshots refuse a different agentic-mbse version, so a bump would break 22 of them. `install-commands` checks `INSTALLER_API_VERSION` instead and names the first revision that has it (`d42c8b9`).
- **Schemas byte-identical** ([AGENT], D7). Tool identity is `tool.path` plus the source digest, so a pre-move record names `scripts/study/` and a post-move one `sysml_codegen/study/`.
- **A closed list of behaviour changes** (B1–B13 in the spec). Parity with fusion-tea's originals holds for 28 of 28 cases outside them.
- **fusion-tea adopts by runbook, after merge** ([AGENT], D1), because its sysml-codegen pin was 214 commits behind. The owner merged agentic-mbse #24 on top of #23 so fusion-tea's agentic-mbse pin moves once ([OWNER] 2026-10-12).

## Follow-ups

In sysml-codegen's backlog, § "Study Layer (WRAP-SPLIT Item 3 follow-ups)": `STUDY-RECORD-RESUME`, `STUDY-ROUTE-POINT-RUNNER`, `INTEGRATE-CALLER-ERROR-AS-SEAM-FAULT`, `VERIFY-MISSING-STORE-TRACEBACK`, `STUDY-PORTED-MYPY-OVERRIDES`, `STUDY-CHECK-RECORD`, `STUDY-PORTED-SMELLS`, `READ-COVERAGE-STALE-BYTECODE` (found at adoption), and `STUDY-GLUE-LEDGER-SEMANTICS` (the owner's call).
