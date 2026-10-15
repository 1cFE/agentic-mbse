Spike F1 for EXEC-SUBSET-CONTRACT Item 1. Read the de-risk flag F1 (and F2) in `.project/active/exec-subset-profile/design.md` Appendix D, plus the design's R1 section and occurrence-port description.

Question: can the occurrence facts the design needs (generator roots; instantiated part occurrences with counts; which part defs have occurrences; winning calc usage per scope, incl. redefined-everywhere calc usages; multiplicity resolution reading the same attribute codegen reads) be extracted in agentic-mbse from SysIDE before elaboration, matching sysml-codegen b5663c07's elaboration exactly — and how big is that port?

Do:
- Write throwaway code under `.project/active/exec-subset-profile/spikes/f1-occurrence-port/` (or a scratch dir if you prefer; keep the findings doc in the item folder). Do not modify `src/`, and never modify ~/src/sysml-codegen or ~/src/dc3 — use `git archive`/`git worktree` into a temp dir for pinned revisions (dc3 808464d and 60b44d5; codegen b5663c07).
- Compare your extraction against codegen's own elaboration output (import codegen from an isolated environment, or run it as a subprocess) on: the 22 prototype fixtures in `.project/concepts/convince-me-exec-subset/evidence/01-fixtures/`, the 14 snapshot fixtures in codegen `tests/fixtures/v6_recapture_batch/`, and both dc3 trees.
- Report: per-corpus match/mismatch counts with every mismatch itemized; the port's line count and which codegen functions it mirrors; any codegen dependency that can't be reproduced from neutral facts; record exact package versions used. Recall the SysIDE license key is in `.env`.

Thresholds from the design: mismatches or a port beyond ~800 lines mean R1 should be re-weighed — report plainly either way; don't tune to pass.

Findings doc: `.project/active/exec-subset-profile/spikes/f1-findings.md`. End with the ARTIFACT line.
