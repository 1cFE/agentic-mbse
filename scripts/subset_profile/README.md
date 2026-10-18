# subset_profile scripts

Development tooling for EXEC-SUBSET-CONTRACT. None of it is shipped: the package does not import it and `init` does not install it. Every script writes only to the output directory it is given.

- `isolated_tree.py`: builds a temp tree from `git archive` exports of both repositories and checks that the packages it runs resolve inside it. `codegen_suite.py` uses it.
- `codegen_suite.py`: runs sysml-codegen's tests against a chosen agentic-mbse revision in an isolated tree (Item 2a design D13).
- `run_trees.py`, `render_matrix.py`, `validate_diff.py`, `scan_sites.py`: Item 1's acceptance-tree run, matrix rendering, record diff check and site scan.

Item 1's probes retired in Item 2a. Their models are packaged conformance cases under `src/agentic_mbse/sysml/subset_cases/<case_id>/`; each case's generator answer is stored and checked live in sysml-codegen.
