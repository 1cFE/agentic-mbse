Review `.project/active/l6-subset-profile/spec.md` — the spec for EXEC-SUBSET-CONTRACT Item 3 (L6 integration and execution-target settings).

Context: the epic `.project/backlog/epic_executable-subset-contract.md` (Item 3 and boundaries); the align record `briefs/align.md` (owner decisions 2026-10-18; gates R3-1, R3-2; owner boundary: do not touch Item 2 or sysml-codegen); `product-lens.md`. Item 1 contract: `src/agentic_mbse/sysml/subset_profile.py`, archive `.project/completed/20261018_exec-subset-profile/`. Item 4 patterns: `.project/completed/20261018_positional-binding-check/`. Read-only: ~/src/dc3, ~/src/fusion-tea.

R3-1 and R3-2 are with the owner; review the rest and do not decide them. Review hard on: whether every criterion is checkable and covers the owner decisions exactly; the holdout-guard interaction (`research/holdout.py`); the `init` and `pyproject.toml` preservation requirements against CLAUDE.md § Init File Ownership (native settings preserved even under `--force`); presentation of CLEAR / REFUSED_INCOMPLETE / unconfirmed / unverified; the legacy L6 check audit's completeness (all broad exception sites, the stale citation); not moving `SUBSET_PROFILE_VERSION`; scope creep into Item 2 or Item 5; provenance grading.

Do not edit the spec. Produce the review artifact with a verdict and must-fix / should-fix items.
