# fusion-tea destination texts (Phase 5 drafts, for orchestrator step O4)

Each file is the fusion-tea home of text the shipped run-study files no longer carry. `../../read-through.md` gives every removed line its verdict and anchor, and `../../ledger-rows.md` groups them for the shared ledger. Every patch is against fusion-tea `b06585709`, except `audit-f8-supplement.patch`, which is against the O4 branch tip `699b0a74d`; all have `a/` and `b/` paths from the repository root.

| File | Applies to | What it adds |
|---|---|---|
| `STUDY_POLICY.patch` | `modeling_project/STUDY_POLICY.md` | § 6 subsection "Execution routes" (the two routes; the adapter, glue and era-pin rules); "## 12. Locations" (`exploration/<pkg>/studies/`); "## 13. Provenance of the installed study text" |
| `integration_seam_operator_guide.patch` | `docs/integration_seam_operator_guide.md` | Rewrites the guide as fusion-tea's supplement to the installed `integration-guide.md`. `integration_seam_operator_guide.md` beside it is the same text as a whole file |
| `CLAUDE.patch` | `CLAUDE.md` | A "## Study layer" section, after "## Installed Tools": where the installed text and each fusion-tea home are, and that `scripts/study/*.py` are aliases |
| `check_anchors.py` | — | Runbook step 3: greps every `moved` row's anchor from `read-through.md` in its home, in a fusion-tea working tree. On `b06585709` with the four patches applied it prints `74 anchors found, 0 missing`; on the branch tip `699b0a74d` with `audit-f8-supplement.patch` applied, `75 anchors found, 0 missing` |
| `stellarator_e2e-ANNEX.patch` | `exploration/stellarator_e2e/studies/ANNEX.md` | Line 5 names the policy's § 6, not the runbook, as the place the two adapter-only annex sections are defined |
| `audit-f8-supplement.patch` | `docs/integration_seam_operator_guide.md`, as the O4 branch tip `699b0a74d` leaves it | A section "## The gate numbers in fusion-tea": the gate table's numbers are the step numbers of fusion-tea's integration-seam requirements (read-through IG-43, audit F8). Unlike the four above, it is against the branch tip, not `b06585709`: it applies after the supplement rewrite |

**Applying.** From the fusion-tea worktree root on the O4 branch: `cat <this directory>/*.patch | patch -p1`. On a fresh copy of `b06585709`, each patch applies alone and all four apply together (checked in Phase 5 with `patch -p1 --dry-run`). If the branch already carries Item 2's `CLAUDE.md` section "Goal layer in this repository", the `CLAUDE.md` hunk still applies: it anchors on "## Installed Tools", and Item 2's section's study and integration bullets stay true after the switch.

**With the supplement goes a test change.** fusion-tea's `tests/study/test_integrate_guide_contract.py` checks the whole guide against `scripts/integrate.py`. Once the guide is the supplement, that test must shrink to the supplement's own facts: the sealed-wheel home, `WHEEL_HASHES` and ADR-0009. `../step5-guide-contract.patch` is that change. Apply it with the supplement, or at runbook step 5 with Phase 4's `step5-tests.patch`; the runbook draft applies both there.

**Ordering.** The texts land on the O4 branch before the sysml-codegen change merges, so every ledger home exists first (SC10). The branch merges into fusion-tea `main` only after the switch (runbook steps 5–7): the supplement, the policy's § 6 opening sentence and the `CLAUDE.md` section describe the installed study layer.
