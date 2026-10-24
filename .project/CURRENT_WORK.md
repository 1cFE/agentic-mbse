# Current Work

**Last Updated**: 2026-10-23
**Checkout**: branch `wrap-up` (from `generated-results-guidance`, 20 commits past `origin/main` `47e65089`), not pushed. sysml-codegen: branch `wrap-up-docs` in `/home/reid/src/subset-conformance/sysml-codegen` (2 commits past its `origin/main` `6190f996`), not pushed.

## Current state

[OWNER] 2026-10-23: two goals, each with a test for done.

- **Each check lives in one repo.** Only sysml-codegen decides what the generator accepts; the validator checks only what holds for any SysML model. Done: L6 and L2 hold no copied generator checks and `tests/test_validation/test_no_generator_copies.py` refuses new ones ([ADR 0006](adr/0006-each-check-lives-in-one-repo.md), [P-0006](product/0006-l6-no-generator-copies.md)).
- **The shipped guidance teaches what the tools actually do.** Done: every complete shipped example is marked and `tests/test_validation/test_tool_examples.py` runs it through `agentic-mbse validate` and `sysml-codegen check` (60 examples: 50 pass, 9 wrong-way, 1 pinned validate defect) ([P-0007](product/0007-shipped-examples-run-both-tools.md)). The check half skips unless `SYSML_CODEGEN` points at the generator and its licence is loaded. sysml-codegen's `docs/architecture/modeling-assumptions.md` was corrected to the same probed behaviour.

The `EXEC-SUBSET-CONTRACT` epic is finished with these two goals; its Item 6 is not planned. The `WRAP-SPLIT` epic is closed (all items merged).

## Active Work

None. Next is merging.

## To merge (owner)

1. sysml-codegen `wrap-up-docs` (backlog rows `b08bbfee` and the doc fix `8e53dc3c`): push and merge.
2. agentic-mbse `wrap-up`: push and merge. It carries the Item 5 close (`generated-results-guidance`, never pushed), the agentic-project-init update, and both goals. The L6 JSON report schema moves to `validate-report/v3` (the fold's `summarized` field is gone); nothing in sysml-codegen or the shipped skills reads it.
3. Delete the stale branch `shipped-example-contract`; its commits are superseded by `wrap-up`.

## Open owner decisions

- RG-1 (sysml-codegen): should the count overrides the generator ignores (no `attribute` keyword, or in a part usage) be refused instead of silently building the default count? The guidance states today's behaviour.
- RG-2 (sysml-codegen): should the guidance warn about String values and calc-usage result expressions that generation drops without a report?
- R4-3: fusion-tea adopts its 125-entry positional pin list when it moves its agentic-mbse pin.
- arXiv extraction: should the shortcut stay on by default (`ARXIV_SHORTCUT_DEFAULT`, `pandoc_convert.py:22`)?

## Known gaps left

- Validate L2 reports `UNBOUND_INPUT` on the `redefines` rename that `docs/patterns/semantic-hazards.md` recommends; the generator builds it. Pinned in `test_tool_examples.py` with `defect="UNBOUND_INPUT"`, so a fix flips the test.
- 6 test failures predate this work, all environmental (pandoc and PIL missing; `/home/reid/1cfe/agentic-mbse` path absent in `test_index.py`).
- `.project/active/` holds 12 old folders; six are finished but not archived ([active/README.md](active/README.md)).
