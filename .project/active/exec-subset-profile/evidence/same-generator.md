# Same-generator check (plan Phase 10, design § Probe harness step 6)

**Result: identical.** Item 1 changed neither what the pinned generator does on any probe nor codegen's own test suite. Re-run after the audit fixes at the new final implementation revision `ce0ad1ff`; the Phase 10 run at `9b123cf3` gave the same result and is superseded (its outputs remain in git history, at `ce0ad1ff` and earlier).

- **Base:** agentic-mbse `a718efecad0ad6f31c4752f1b3f289fb83be336b` (the design base). **Final:** `ce0ad1ffbc4070004d8a7a5a1b3e834f4e483508` (the final implementation revision after the audit fixes). Both against sysml-codegen `b5663c07e987a892e27d21e68cec40d0656574ee`, SysIDE 0.8.4, Python 3.12.3, codegen `uv.lock` sha256 `a17e9fa1…abee4d4`, each in its own isolated `git archive` tree.

## Probes

| Run | Command | Result |
|---|---|---|
| canonical | `probe.py run --all --agentic-rev b1e95ec9` | 80/80 certify (`same-generator/probe-run-canonical-b1e95ec9.out`). These are the committed `observation.json` files the records cite (`verified_against.agentic_rev = b1e95ec9`) |
| base | `probe.py run --all --agentic-rev a718efec --base` | 80/80 certify (`same-generator/probe-run-base.out`) |
| final | `probe.py run --all --agentic-rev ce0ad1ff` | 80/80 certify (`same-generator/probe-run-final.out`) |

Comparing each probe's observations field by field, with the temp-tree prefix normalized: **base against final, all 80 differ in exactly one field, `identity.agentic_rev`; canonical against final, the same.** Exit code, every `ERROR:` line, generated file list and hashes, catalog names, mentions, the model hash and the certification are identical. Observations and logs: `same-generator/base-a718efec/`, `same-generator/final-ce0ad1ff/`.

The probe set includes the three `other_expression_site` probes re-authored by the audit fixes (S1) as `omitted`. Their models now hold a unique literal in the dropped expression. Against the previous `admitted` observations at `ecc18940`, their generated files are byte-identical; only the model hash and the new literal's (empty) mention list differ.

**Canonical revision.** `b1e95ec9` is the commit holding the audit-fix code and probe fixtures; `ce0ad1ff` adds the observations and re-pins `verified_against`, which changes the packaged records, so it is the final revision. A record cannot name the commit that contains it, so the cited observations sit one commit before the final revision, as they did before (A5). The final run shows they are identical apart from the revision.

The harness writes `observation.json` and the probe logs in place, so after the base and final runs the committed canonical files were restored from git and the run outputs kept only under `same-generator/`.

## Codegen's pytest suite (includes its v6 corpus conformance tests)

| Run | Result |
|---|---|
| `codegen_suite.py run --agentic-rev a718efec --label phase10-base-a718efec` (Phase 10; the base revision and inputs are unchanged, so not re-run) | 2685 passed, 53 failed, 7 errors, 9 skipped |
| `codegen_suite.py run --agentic-rev ce0ad1ff --label audit-fixes-final-ce0ad1ff` | 2685 passed, 53 failed, 7 errors, 9 skipped |
| `codegen_suite.py diff phase10-base-a718efec audit-fixes-final-ce0ad1ff` | 2754 tests compared, 0 differ: IDENTICAL (`same-generator/codegen-suite-diff.log`) |

The 60 failures and errors are the same tests in both runs and in Phase 3's runs: codegen's study and ledger tests need a git work tree, which a `git archive` export does not have. Per-test JSON and logs: `codegen-suite/phase10-base-a718efec.*`, `codegen-suite/audit-fixes-final-ce0ad1ff.*`.
