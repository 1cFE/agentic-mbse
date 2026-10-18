# subset_profile scripts

Development tooling for EXEC-SUBSET-CONTRACT Item 1. None of it is shipped: the package does not import it and `init` does not install it.

- `probe.py`: runs probes against the pinned generator (sysml-codegen `b5663c07`) in a fresh temp tree built with `git archive`, judges each run with `tests/helpers/subset_probe_judge.py`, and writes the probe's `observation.json`. Usage: `uv run python scripts/subset_profile/probe.py run --all --agentic-rev HEAD`. Commit probe fixtures first; the harness refuses uncommitted ones.

Probes live in `tests/fixtures/subset_profile/probes/<rule>__<shape>__<context>[__<variant>]/`. Run logs go to `.project/active/exec-subset-profile/evidence/probes/`.
