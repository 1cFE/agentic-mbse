# subset_profile scripts

Development tooling for EXEC-SUBSET-CONTRACT. None of it is shipped: the package does not import it and `init` does not install it. Every script writes only to the output directory it is given, with one exception: a passing gate run also writes the gate receipt, `tests/fixtures/subset_profile/codegen_gate.json`.

## The pre-merge gate (required before merging a change to a covered file)

The shared subset contract is checked against sysml-codegen's generator only when codegen's tests run against it. Neither repository has CI, so this script is that check, and a receipt makes skipping it fail this repository's own suite (Item 2a design D13).

```bash
uv run python scripts/subset_profile/codegen_suite.py run \
    --agentic-rev HEAD --codegen-rev <sysml-codegen revision> --label gate --out <dir>
```

- **When.** Before merging any change to a covered file: everything under `src/agentic_mbse/sysml/` (code, the records TOML and `subset_cases/`) and `src/agentic_mbse/errors.py`. Commit first: the run exports both repositories at the named revisions with `git archive`, so uncommitted edits never reach it.
- **What it runs.** codegen's `tests/conformance/subset_profile/` (the default `--select`), licensed, in a fresh tree built by `isolated_tree.py`. The SysIDE key comes from this checkout's `.env`.
- **Pass.** Every selected test passed. A failure, an error or a skip fails the run (exit 1); the only skip in those tests is the missing-license one, and a run with license-gated skips does not count.
- **The receipt.** A passing run of the default selection writes `codegen_gate.json`: `digest` (sha256 over the covered files' paths and bytes in the exported tree, `gate_receipt.py`), `codegen_rev`, `agentic_rev` and `case_ids` (every packaged case that a passed codegen test was parametrized with). It refuses to write a receipt if a packaged case has no passed test. A failing run writes only its report to `--out`. Commit the receipt.
- **The check.** `tests/test_subset_gate_receipt.py` recomputes the digest over the working tree and requires every packaged case in `case_ids`. Editing a covered file without rerunning the gate fails it, and its message gives the command above.
- **Limits.** A receipt forged with both the digest and every case ID passes the test. Nothing here ties `codegen_rev` to the sysml-codegen commit being merged: the coordinated merge's `pre_pr` checks that `codegen_rev` is the merging codegen head, or an ancestor whose later commits touch nothing under `src/`, `tests/conformance/subset_profile/` or `tests/expectations/subset_profile/`.
- `codegen_suite.py diff A.json B.json` compares two runs' reports test by test.

## The other scripts

- `isolated_tree.py`: builds a temp tree from `git archive` exports of both repositories and checks that the packages it runs resolve inside it. `codegen_suite.py` uses it.
- `gate_receipt.py`: the receipt's covered files, digest and case IDs, shared by `codegen_suite.py` and the receipt test.
- `run_trees.py`: runs the screen over the acceptance trees (dc3 baseline `808464df`, dc3 repaired `60b44d53`, codegen's v6 corpus), judged against `--codegen-rev`. Item 2a's rerun is in sysml-codegen's `.project` evidence (`dc3-rerun.md`).
- `scan_sites.py`: the agentic-mbse site scan (`scan_sites/2`) and its reconciliation against `tests/fixtures/subset_profile/inventory/site_account.csv`. sysml-codegen scans its own sites.
- `render_matrix.py`, `validate_diff.py`: Item 1's matrix rendering and record diff check.

Item 1's probes retired in Item 2a. Their models are packaged conformance cases under `src/agentic_mbse/sysml/subset_cases/<case_id>/`; each case's generator answer is stored and checked live in sysml-codegen.
