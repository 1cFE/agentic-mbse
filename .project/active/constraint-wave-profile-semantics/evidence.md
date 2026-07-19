# Implementation Evidence: Constraint-Wave Profile Semantics

**Started:** 2026-07-19 PDT
**Execution:** `my-implement`, all five phases, companion-first
**Remote actions:** Forbidden. No commit, push, PR action, merge, tag, upload, publication, or close.

## Owner controls

- Items 1/2/4/6 are one constraint-wave landing unit. Their edits and overlaps are not isolated,
  allowlisted by hunk, or treated as contamination.
- Clean temporary worktrees and overlays are used only for reproducible historical RED and
  hermetic version-skew evidence.
- Genuinely unrelated/user paths remain outside the constraint-wave implementation scope.
- Licensed commands load the existing sysml-codegen `.env` explicitly with `uv --env-file`; the
  file and key are never printed, copied, hashed, or logged.

## Incoming baselines

### agentic-mbse

- Root: `/home/reid/1cfe/agentic-mbse`
- HEAD: `4ed2a0728ea49298666415cd389d9a6173a81a3e`
- Branch: `constraint-exec-epic`
- Tracked binary diff SHA-256: `5ab1c49294e6d2e678c4d9e0ee06d7453f016471ab8dde321f0bb1d031811317`
- Shared-wave baseline: all active constraint profile/version/docs/tests/lock changes and active
  Item 1/4 artifacts.
- Separately preserved unrelated/user paths: `.project/CURRENT_WORK.md`, `.orchestrate-logs/**`.
  This stage did not edit them. A durable per-path incoming hash manifest was not completed.

### sysml-codegen

- Root: `/home/reid/1cfe/sysml-codegen`
- HEAD: `512786c7dfab44fba7a0185d09e845b7494c702d`
- Branch: `constraint-exec-epic`
- Tracked binary diff SHA-256: `af7fe878023a6ddc7466e0c1080b977187cf4e48ab0e5a8a1c11b24ea087d152`
- Shared-wave baseline: all active Items 1/2/4/6 production, fixture, test, active-work,
  reconciliation, and epic-ledger paths.
- Separately preserved unrelated/user paths: `.project/CURRENT_WORK.md`,
  `.project/backlog/BACKLOG.md`, `.project/backlog/epic_gap_close.md`,
  `.project/backlog/epic_gap_close_audit_independent.md`, and `.claude/projects/**`.

The full incoming porcelain-v2 inventories and untracked-path inventories were captured in the
stage command log before edits. They were not promoted into a durable sealed overlay/per-path hash
manifest before production work. The constraint-wave fixture changes are an approved incoming Item
4 baseline; this stage did not run capture or recapture. Final fixture hashes are recorded below,
but exact before/after equality cannot be claimed from those hashes alone.

## Plan correction

The stale Phase 5 instruction to compare saved incoming overlap hunks was amended before
implementation. Phase 5 now requires behavioral Item 2/4/6 regression gates and preservation only
of separately recorded genuinely unrelated/user paths.

## Phase 1

- Historical companion worktree: `/tmp/constraint-wave-historical-companion`, clean revision
  `54a95d2`. The kept probe produced three intended failures: String `<` was unexpectedly ADMIT,
  Boolean `<=` was unexpectedly ADMIT, and `UsageDecision` had no `is_negated` field. This proves
  the two R-1 examples and the profile-level R-2 classification gap.
- Implemented `executable-profile/v4`, exact category-pair and invalid-polarity diagnostics,
  polarity-first decisions, Boolean state validation, named constructors, complete fact-field
  consumer map, and literal `<no location>` rendering.
- Final focused companion contract: 434 passed normally and 434 passed under optimized Python with
  one expected pytest `-O` configuration warning.
- Historical downstream negation and complete four-row live/codec controls were completed during
  the independent-audit cure. Pre-edit overlay and output-log provenance was not captured and is
  not claimed.

## Phase 2

- Companion package version, public runtime version, lock selection, and wheel metadata agree on
  `0.1.2`; profile identity is `executable-profile/v4`.
- Final local companion wheel:
  `agentic_mbse-0.1.2-py3-none-any.whl`, SHA-256
  `696da74feac97e72a64c18c9932fae41b95a4214d90ca0714d705bed6e6f32cf`.
- Complete companion suite ran before the complete codegen suite: 1,797 passed, 1 skipped,
  33 deselected, 6 warnings, 0 failures.
- The final wheel was built from the reviewed active shared-wave tree. It was not reconstructed from
  a clean candidate overlay; that provenance is not claimed.

## Phase 3

- Lowering requires profile v4, verifies decision/fact polarity and expected truth before graph
  extension, uses the decision pair as authority, and derives a required predicate source key.
- Concrete/catalog records carry the required source key. Catalog grouping uses source key plus
  positive body bytes and permits mixed usage polarity.
- Production compiles a polarity-neutral body and applies each usage's decision exactly once in the
  wrapper finalizer. The legacy compiler remains only for compatibility tests; production does not
  consume it.
- Coordinated Phase 3/4 focused run: 575 passed normally. Earlier focused runs passed 602 before one
  test expectation was corrected, then the coordinated selection was green. The Item 2 normal
  overlap passed 171; Item 4/6 normal overlap passed 516; the combined optimized overlap passed
  614 with one expected pytest `-O` warning.
- Final fixture hashes (approved incoming Item 4 bytes, not recaptured here):
  - catf/MFE: `9ae5cfc48a82a18ef10500909bc6bf4010f811d891cf0c201e02192079e344d6`
  - non-numerical: `605f549e8995c2ff1e843065f1d357f3ffa2f9bd0e702817e55436b4c96c4c02`
  - sample model: `d7df02a9d411fa94c133b9a30b087a34caf5bc942f4374ecfc61483fc7f128bd`

## Phase 4

- Added frozen `ConstraintGenerationPlan` with read-only mappings. It compiles and renders every
  constraint artifact before output clear/setup.
- CLI builds the plan after existing read-only guards and before target mutation. Emission consumes
  the plan without regrouping or recompiling.
- Phase 4 focused selection: 80 passed. Coordinated Phase 3/4 selection: 575 passed. Final candidate
  selections below cover plan/emission/CLI behavior normally and under optimized Python.

## Phase 5

### Final wheelhouse and pinned inputs

- Codegen declared floor and lock: `agentic-mbse>=0.1.2`, resolved companion `0.1.2`.
- Final local codegen wheel: `sysml_codegen-0.1.0-py3-none-any.whl`, SHA-256
  `291086efbd366da1a1ceeb1eefd68aa0bb61741b539f52469672b72540a7c851`.
- Historical wheels:
  - companion 0.1.1: `76db4dd04ff7feb9a22d52bb758a5ec81783a521ba18f421a71369c8c09ca087`
  - codegen 0.1.0 at `512786c`: `188020652c4baabfc168cf0135436d4aed9896e078037cfc0307c9ef2a41efa1`
- Final wheelhouse uses the repository-lock-compatible SysIDE 0.8.4 closure. An initial candidate
  probe against SysIDE 0.10.2 failed one live parse because that newer parser rejects the sample
  fixture's inherited `result` shadowing. The wheelhouse was corrected, all inputs regenerated,
  and no final claim uses the rejected closure.
- Durable manifest SHA-256:
  `401a1e8f7eb88abaff939ba13ceead9e2fd720f40aa74f7b15e561152e23e66e`.
- Pinned input SHA-256 values:
  - old codegen/new companion: `588f698b8cad88e34620ff240175c316faa640144bcbee9645124fdb50353556`
  - new codegen/old companion resolver and runtime:
    `e291ef3b2188f151fc149f05f2a1227c6122c9773ea9ddfe3a2e25946fd8ac4b`
  - new codegen/new companion: `aea1f819f23ed622cfd3a5cce9da6cf0aacd5b5eaca89fa1f70d22adb625fada`
- The old and new codegen wheels have the same distribution/version filename, so the immutable
  wheelhouse root has separate `old-codegen/` and `new-codegen/` find-link directories. Negative
  and positive new-codegen controls use the same new-codegen/common/companion directories; only the
  requested companion pin changes.

### Compatibility assertions

- Old codegen + new companion installed from 35 hash-pinned wheels. Its lowering guard rejected
  `executable-profile/v4` while expecting v3, before evaluating its deliberately null facts input.
- New codegen + old companion resolver failed. The kept normalizer produced exactly:
  `{"conflicts":[["agentic-mbse>=0.1.2","agentic-mbse==0.1.1"]],"missing_or_unsatisfied_others":[]}`.
  The raw resolver log SHA-256 is
  `5cc8a4e46f8977f897e92d4573f4b22db559d08113f2e40e3a283aeb1a2eaa6a`.
- New codegen + old companion runtime bypass installed with `--no-deps`; its guard rejected
  `executable-profile/v3` before facts evaluation.
- The same-wheelhouse positive input installed successfully. Its installed modules resolve from
  `/tmp/constraint-wave-env-new-new/.../site-packages`, report companion `0.1.2`, profile v4, and
  codegen metadata `agentic-mbse>=0.1.2`.
- All runtime commands used the environment's explicit Python through
  `uv run --no-project --env-file .env`; no environment contents were printed or copied.

### Candidate and regression gates

- Final exact installed pair, normal: 664 passed in 12.89s.
- Final exact installed pair, optimized: 664 passed in 13.01s, with one expected pytest warning
  that asserts in non-test modules are disabled under `python -O`.
- Candidate selection includes lowering, package identity, Item 2 name safety, Item 4 snapshot
  portability, Item 6 seal/verify symmetry, compiler, plan/emission/CLI, snapshot identity/parity,
  and fingerprint tests.
- Full companion suite: 1,797 passed, 1 skipped, 33 deselected, 6 warnings.
- Full codegen suite: 2,960 passed, 26 skipped, 10 deselected, 0 failures.
  These completed full suites were not rerun after formatting-only candidate rebuilds; the exact
  rebuilt wheels instead passed the 664-test normal/optimized candidate selection.

### Static and scope gates

- Touched-file Ruff check and format-check pass in both repositories, including both evidence
  helpers. `git diff --check` passes in both repositories.
- Full-project static baselines are red with inherited debt and were not cleaned up:
  - companion Ruff: 127 errors; format-check: 60 files would reformat, 85 already formatted;
    mypy: 104 errors in 22 files.
  - codegen Ruff: 331 errors; format-check: 139 files would reformat, 114 already formatted;
    mypy: 77 errors in 17 files.
- Targeted mypy still follows imports into inherited modules. Companion reported 22 errors in nine
  files, with the only touched file diagnostic at the pre-existing
  `level6_architecture.py:64`. Codegen reported 61 errors in 13 files, including pre-existing
  untyped helpers in `modules.py` and CLI diagnostics outside the Item 1 edits. It reported no
  diagnostic in the new `constraint_plan.py`, profile decision implementation, lowering changes,
  catalog changes, predicate compiler changes, or models changes.
- Final HEADs are unchanged: companion `4ed2a0728ea49298666415cd389d9a6173a81a3e` and codegen
  `512786c7dfab44fba7a0185d09e845b7494c702d`. The trees retain the owner-authorized shared
  Items 1/2/4/6 wave and the previously inventoried unrelated paths. No reset, stash, clean,
  fixture recapture, per-item isolation, or hunk allowlist was used.

## Independent audit remediation

- Lowering now verifies `effective_predicate_source` before source-key minting. Inline identity
  must equal the asserted usage identity. Definition-typed identity must equal the referenced
  definition identity, and the usage's definition reference must agree with that definition.
  Forged inline and definition identities fail before owner expansion, constraint-ID minting,
  graph extension, output clear/setup, or target-tree mutation.
- The forged-identity tests were written before the guard and failed in both normal and optimized
  Python because owner expansion was reached. After the guard, the two lowering cases pass in both
  modes. The integrated absent/populated-tree matrix adds four more kept cases.
- A kept licensed route test now carries positive/negated inline and definition-typed assertions
  through live extraction, the public facts codec, profile v4, lowering, catalog assembly, and the
  in-memory generation plan. Live and codec records are equal; all four positive predicate byte
  sequences are equal; the two definition usages share one source key/body; and the four decisions
  retain complementary polarity/expected-truth pairs.
- A kept compound sentinel proves two malformed ordering leaves remain ordered through profile and
  become two Level 6 errors. Codegen reports both before mutation and preserves a populated target
  tree byte-for-byte. The approved malformed-arity text is now exactly
  `comparison has 1 operands; expected 2`.
- The final integrated execution file ran in the prescribed agentic-mbse environment with pandas
  2.3.3 and TEAx SimKit from `/home/reid/1cfe/teax/packages/teax-simkit`. All 15 tests passed
  normally and all 15 passed under `python -O` (one standard pytest optimized-mode warning). The
  new five-row shared-definition test covers true, false, strict boundary, inclusive boundary, and
  non-finite values with reversed usage order, one neutral body, two wrappers, identical raw values,
  and complementary final verdicts.
- Historical R-2 ran from clean companion revision
  `54a95d2ffe18f8e7b437a7f895843e0c89c98c27`. Live extraction and codec retained all four source
  and polarity rows and one positive predicate byte set, while profile v3 had no decision polarity
  fields. The same helper passed against active v4 with complementary decision fields. Final helper
  SHA-256: `beffb8bde2661f23c147771c18549c1ac97c080d0dacf6c7d0db5beda3dd202c`.
- The historical downstream negated generated-execution control ran from clean codegen revision
  `512786c7dfab44fba7a0185d09e845b7494c702d` in the same pandas/TEAx environment: 1 passed normally
  and 1 passed under `python -O` (one standard warning). This establishes that v4 preserves the
  downstream negated verdict behavior.
- Final audit-cure focused gate: 56 passed normally; 56 passed under `python -O` with one standard
  warning. The broader semantic selection passed 665 in each mode before the final annotation-only
  typing correction. The companion profile/validation selection passed 434 in each mode. The exact
  Items 2/4/6 overlap union was rerun last: 614 passed normally and 614 passed under `python -O`
  with one standard warning.
- Touched-file Ruff check and format-check pass in both repositories. Targeted mypy passes with no
  issues for the changed lowering and profile production files. `git diff --check` passes in both
  repositories. The inherited full-project Ruff/mypy baselines recorded above remain unchanged and
  were not expanded into unrelated cleanup.

## Owner disposition of provenance gates

After implementation and re-audit, the owner said: “yeah I don't need those gates at this point.
please amend, but don't re-audit. I want to discuss the larger context before we continue
rerunning.” The agent-authored clean-overlay and pre-edit-hash gates therefore do not block Item 1.

No durable pre-edit per-path/untracked/fixture manifest exists, and the candidate wheels were built
from the active shared-wave trees rather than reconstructed clean reviewed overlays. Those facts
remain recorded; no retroactive evidence or historical byte-equality claim is made. Equivalent kept
behavioral coverage satisfies filename-specific test stencils.

## Remote-action confirmation

No commit, push, PR creation/comment/state change, merge, tag, upload, publish, release, close, or
self-audit occurred.
