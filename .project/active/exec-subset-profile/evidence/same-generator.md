# Same-generator check (plan Phase 10, design § Probe harness step 6)

**Result: identical.** Item 1 changed neither what the pinned generator does on any probe nor codegen's own test suite.

- **Base:** agentic-mbse `a718efecad0ad6f31c4752f1b3f289fb83be336b` (the design base). **Final:** `9b123cf323e5dfc2af56ebf9144cec86d1eeac9b` (the final implementation revision). Both against sysml-codegen `b5663c07e987a892e27d21e68cec40d0656574ee`, SysIDE 0.8.4, Python 3.12.3, codegen `uv.lock` sha256 `a17e9fa1…abee4d4`, each in its own isolated `git archive` tree.

## Probes

| Run | Command | Result |
|---|---|---|
| base | `probe.py run --all --agentic-rev a718efec --base` | 80/80 certify (`same-generator/probe-run-base.out`) |
| final | `probe.py run --all --agentic-rev 9b123cf3` | 80/80 certify (`same-generator/probe-run-final.out`) |

Comparing each probe's two observations field by field, with the temp-tree prefix normalized: **all 80 differ in exactly one field, `identity.agentic_rev`.** Exit code, every `ERROR:` line, generated file list and hashes, catalog names, mentions, the model hash and the certification are identical. Observations and logs: `same-generator/base-a718efec/`, `same-generator/final-9b123cf3/`.

The harness writes `observation.json` and the probe logs in place. The committed ones are the records' cited evidence at `ecc18940`, so after the runs they were restored from git and the run outputs kept only under `same-generator/`.

## Codegen's pytest suite (includes its v6 corpus conformance tests)

| Run | Result |
|---|---|
| `codegen_suite.py run --agentic-rev a718efec --label phase10-base-a718efec` | 2685 passed, 53 failed, 7 errors, 9 skipped |
| `codegen_suite.py run --agentic-rev 9b123cf3 --label phase10-final-9b123cf3` | 2685 passed, 53 failed, 7 errors, 9 skipped |
| `codegen_suite.py diff phase10-base-a718efec phase10-final-9b123cf3` | 2754 tests compared, 0 differ: IDENTICAL (`same-generator/codegen-suite-diff.log`) |

The 60 failures and errors are the same tests in both runs and in Phase 3's runs: codegen's study and ledger tests need a git work tree, which a `git archive` export does not have. Per-test JSON and logs: `codegen-suite/phase10-*.{json,log}`.

## A revision note

The final revision first frozen was `38b63b1b`. The corpus run then stopped on `run_trees.py`'s own self-check (it required a non-empty root set, and `sample_model` has no generator roots, which is the honest answer). The fix touched only `scripts/`, but it moved HEAD, so every Phase 10 run was repeated at `9b123cf3`. `src/`, `pyproject.toml` and `uv.lock` are identical at the two commits. A probe run at `38b63b1b` also gave 80/80 with only the revision differing; it is superseded and not kept.
