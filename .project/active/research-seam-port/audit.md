# Audit: Port the research acquisition seam, and bring `/manage-sources` under its rules

**Verdict:** Certify with follow-ups
**Audited:** 2026-10-12
**Branch:** `research-seam-port` (base `ac5fb1a`)
**Commit:** `bdc7cb2` (code unchanged since `1b3455e`; later commits touch `.project/` only)
**Work item:** `WRAP-SPLIT` Item 5

---

## The Point

agentic-mbse had no way for a target to bring an outside source into `knowledge/` with proof that it is there. The capability lived only in fusion-tea, as one prompt and two scripts, and Item 2's shipped `run-goal` delegates every acquisition to it. [OWNER-VERBATIM] 2026-10-06: "yes, we need this capability in agentic-mbse."

So the work has three parts:

- **One checked door.** A target captures a source, hashes it, and writes the source directory, raw copy, manifest row and index block together under one lock, after asking the project's hold-out hook. The run's class is computed from what landed on disk. All of it comes from `agentic-mbse init`.
- **Hand curation through the same door.** [OWNER-VERBATIM] 2026-10-09, on `/manage-sources`: "MORE useful as a general skill which allows direct user management while it folows and enforces the rules".
- **No loss for fusion-tea.** [INHERITED: epic, owner 2026-10-06] fusion-tea switches over with no data migration and no lost instruction. Its 123 manifest rows, 61 runs and one bounded negative are read as they are.

## Summary

The port is faithful and well built. I compared every module against the fusion-tea snapshot. The ladder, the six outcomes and their messages, class precedence, the request key, and the receipt, return, negative, manifest-row and index-block bytes are unchanged, except where the design's Behaviour Changes table or a phase note says otherwise. I found no unrecorded difference that changes fusion-tea's data or a caller's result.

The hold-out hook fails closed on every path through `register`, `retire` and `add-entry`. All nine spec criteria are met with evidence: the suite, ruff and mypy are at their baselines with no new findings, and the orchestrator's O1 and O2 evidence is consistent.

Three follow-ups are worth doing, two of them cheap enough to do before merge:

- a new parser hazard from agent prose containing `<!--`;
- a stale "manually edit SOURCE_INDEX.md" line in `init`'s output;
- a misspelled hook table name that silently switches the guard off.

## Product Judgment

**This is the right piece of work, and it delivers what the owner asked for.**

- **A fresh target acquires a source from installed files alone.** The O2a dry run took a wheel-installed scratch target, with no fusion-tea on any path, to `REGISTERED`.
- **A person curates by hand through the same rules.** `manage-sources` makes every change through the CLI. O2b's five sessions made no Write or Edit call.
- **fusion-tea's data reads the same.** In O1, `verify` reported the same findings plus exactly the two expected legacy lines. A known duplicate and the recorded negative refused exactly as the scripts did.

Product-lens (block appended to `product-lens.md`, run inline because the lens script is outside this stage's sandbox): **CLEAR**, with three `[DO]` findings that become follow-ups below (F1–F3).

- **impl-F1 is owner-graded, and it does not contradict the owner's ask.** It is the stale `init` line that points users at a hand edit (F2 below). The skill the owner ruled on does what the ruling says. The stale line is a pointer elsewhere, and one edit fixes it. It does not reach a "do not certify" verdict, but I recommend fixing it before merge.
- **No open `BLOCK` in the ledger.** Every earlier finding (spec-F1..F4, design-F1..F3) is resolved, and I checked each fix in the code: the anchor fallback (`index.py:176-188`), the guarded `add-entry` (`index.py:431-469`), the unknown-key fault (`holdout.py:225-231`), and the queue action with no re-run (`manage-sources/SKILL.md:141`).

Structural smells:

- **Fired, accepted: seam repairs are told apart by reason text.** The skills, the guide and `manage-sources` recognise a seam repair by the prefix of the reason string (`hold-out guard unavailable:`, `URL capture needs the web extra:`, `source index missing:`). That is downstream code depending on an internal representation. The design review accepted it (A1): keeping `close` unchanged keeps the receipt and return shapes byte-identical for fusion-tea. Tests pin the prefixes (`test_holdout.py`, `test_command_contract.py`). Not escalated.
- **Fired, advisory: a seam fault reaches the goal layer as an owner gate.** It arrives as `OPERATOR_QUEUE` → `OWNER_GATE`. The runbook's own rule says a seam repair is a `PREREQUISITE` (`GOAL_RUNBOOK.md.template:294` against `:302`). The goal still stops for the owner, and the skill's report names the seam repair, so nothing is silent. See A3.

## Must-fix before merge

None.

## Follow-up

Ranked by importance. Each is worth a backlog line.

**F1. A registration whose prose contains `<!--` breaks how the index parses from then on.**

- **What is wrong.** The new comment-aware parser masks from any `<!--` to the next `-->`, or to the end of the file when there is none (`research/index.py:53`, `:120-148`). `add-entry` refuses `<!--` and line breaks in every field (`index.py:472-473`). `register` checks neither: it checks only for blank fields (`register.py:264-276`).
- **Failure scenario.** I checked this in memory against the package (no files written). An agent registers a page with `--caveat "page shows a stray <!-- marker"`.
  - Every later block becomes invisible to the parser, so `research sources` does not list them.
  - `retire` of any later slug refuses with "0 SOURCE_INDEX.md blocks locate …".
  - `verify` no longer sees those blocks, so it misses `block_without_row` and `retired_reappeared` findings for them. Rows still pass `row_without_block`, which reads the raw text, so `verify` stays clean.
  - The anchor heading is masked too, so every later registration is appended at the end of the file, below `## How Sources Are Used`. In fusion-tea's index, that moves where new blocks land.
- **Why it is new.** The snapshot never parsed comments, so this hazard comes from D10. It is not listed: P1's note covers only `<!--` inside inline code.
- **Likelihood.** Low. Titles and prose are agent-written sentences, and fusion-tea's index has no `<!--` today. The damage can be repaired by hand and shows in `git diff`.
- **What should change.** `register` refuses `<!--` and line breaks in the title, Use for, Validation and Caveat as `precondition_failed`, as `add-entry` does. Add a row to the Behaviour Changes table. This is a few lines, and I would do it before merge.

**F2. `init` still tells every new user to edit the index by hand.**

- **What is wrong.** `src/agentic_mbse/cli/__init__.py:687-689` prints "2. Or manually edit knowledge/SOURCE_INDEX.md and start with the design-model skill" at the end of every `init` that changed anything.
- **Failure scenario.** A new user follows the first instruction they see and hand-writes entries: no lock, no hold-out check, no types. A hand-written entry under `knowledge/sources/` then shows as `unregistered` drift.
- **Why it matters.** This is the path the owner's ruling replaced, and the spec's problem statement names it as one of the four breaks. P6 fixed the fallback index text in the same file (`1b3455e`) but missed this line. I6 and B4 cover shipped skills, and this is CLI output, so no criterion catches it.
- **What should change.** Point step 2 at `/manage-sources`. One line.

**F3. A misspelled hook table name switches the guard off with no warning.**

- **What is wrong.** `load_holdout_guard` returns the no-op guard when `[tool.agentic-mbse.research]` is absent (`research/holdout.py:240-252`).
- **Failure scenario.** I verified this on temp directories. A target writes `[tool.agentic-mbse.reseach]` or `[tool.agentic_mbse.research]` with a correct `holdout-guard = "…"` line. Every `register`, `retire` and `add-entry` then runs unguarded. The same typo inside the table (`holdout_guard`) does fail closed: review M2 covered keys, not table names.
- **Scope.** fusion-tea's table is spelled correctly. O1 confirmed it: a barred URL refused as `holdout_hit` through the CLI.
- **What should change.** Treat any key under `[tool.agentic-mbse]` other than `research` as a fault, since the toolkit owns that namespace and uses no other key there. Optionally, also fault on a `[tool.agentic_mbse]` table.

## Advisory

**A1. `register`'s rollback does not restore an index whose own write failed partway.**

- `_roll_back` restores the manifest, the raw copy and the source directory, but not `SOURCE_INDEX.md` (`register.py:531-542`).
- If `insert_block`'s `write_text` fails partway, for example on a full disk, the index is left truncated.
- This is the snapshot's behaviour (`source_registry.py:602-613`), so it ported faithfully. But I3 and the guide (`docs/research-seam.md:67`, "the manifest and the index come back byte-identical") say more than the code does. `retire` does snapshot and restore the index bytes (`retire.py:348-356`).
- Snapshotting the index bytes in `_commit` would make I3 true.

**A2. Evidence pointers are stale.**

- The ledger preamble (`wrap-split-migration-ledger.md:54`) and the plan (`plan.md:524`, `:768`) name `evidence/o1-parity.md`, which does not exist.
- The content is in `evidence/o1-parity-early.md` and `evidence/o1-fusion-tea-branch.md`.
- The O2 plan lines name `o2a-dry-run.md` and `o2b-dry-run.md`. The record is `evidence/dry-run/README.md`.

**A3. The runbook's class table has no seam-repair note.**

- `OPERATOR_QUEUE` → `OWNER_GATE` (`GOAL_RUNBOOK.md.template:294`) is unconditional. A queued reason with a seam-repair prefix is, by the runbook's own rule (`:302`), a `PREREQUISITE`.
- One clause under the table would align them. The table is the design's exact text (D16), so this is a design-level touch.

**A4. The O2a request differs from the design's runbook, and the evidence does not say why.**

- Design Appendix D specifies an aluminium 6061 density request on `en.wikipedia.org/wiki/6061_aluminium_alloy`. The dry run used copper's thermal conductivity on `…/wiki/Copper` (`evidence/dry-run/o2a-request.json`).
- The README says the request "holds the specified fields" and "no swap was needed", without noting the change.
- Criterion 2 only needs one request end to end, so this does not affect the verdict. The evidence should say who changed the request and why.

**A5. `--adequacy limit_reached` has no effect on a run that registered something.**

- The O2a agent spent 1 of 1 captures and closed with `--adequacy limit_reached`, yet `return.json` has `"limit_reached": null`.
- This is the snapshot's behaviour: `--adequacy` only feeds a filed negative (`seam.py:268-276`), and `max_captures` shows only after a refused `register` (`seam.py:366-377`).
- `research-acquire/SKILL.md:162` could say so.

**A6. The guide says capture runs "at budget 0", but the CLI exposes `--budget`.**

- `docs/research-seam.md:451` says "at budget 0". That is only the default: `register --budget` (`research_cli.py:359-364`, ported from the snapshot) passes any value to `extract`, and `extract --budget > 0` starts a Claude session.
- The skill never passes it, and a test pins that. Saying "by default" in the guide would be exact.

**A7. Small text leftovers from P6's own list.**

- `skills/project-structure/SKILL.md:80` still spells the field "Use For".
- The epic's Item 5 grep line (`epic_wrap-split.md:307`) still has the unbounded `aries`, which matches "boundaries" in `research/index.py:124,131,132`. The spec's corrected, word-bounded pattern returns nothing.

## Findings Detail

### Behaviour preservation (brief priority 1)

I compared `src/agentic_mbse/research/` with the snapshot scripts by reading both, not from the design's table.

**Unchanged.** These match the snapshot exactly:

- **Ladder order.** Sweep, metadata, input file, hold-out on input path, identity and title, pre-fetch dedupe, `max_captures`, capture, hold-out on extract and raw, `source_id` dedupe, commit (`register.py:198-261`, `:335-355` against `source_registry.py:241-386`).
- **Every refusal message**, word for word.
- **Class precedence** (`seam.py:309-315` against `research_seam.py:241-247`).
- **The request key**, byte for byte (`seam.py:131-145`). O1 got the same refusal output from the CLI and from the script for the same request.
- **Bytes on disk.** The receipt's key order and file name (`runs.py:104-122`), the return and negative shapes, the manifest row's key order (`register.py:175-185`), the seam block, and the insertion bytes at an anchor (`index.py:183-186`, equal to `content.replace(...)` at `zotero_ingest.py:276-278`). Golden tests pin each of these against data derived from the snapshot.
- **The commit.** Four artifacts under one lock, rungs in the same order, rollback in reverse.
- **`retire`.** Refusal order, guard argument shapes (`Path(slug)`, the literal `knowledge/sources/<slug>`, then the slug as text), the references rule, park-then-rewrite, the `RETIRED.jsonl` line, and its rollback.
- **`verify`.** Its three passes, `format_finding`, and the raw-text `row_without_block` check.

**Listed in the design's Behaviour Changes table.** The no-op default guard. The fail-closed guard faults, with their receipt and capture count. The two anchors and the end-of-file fallback. Comment masking and blocks ending where a comment opens. `block_without_row`. A missing web extra or missing index as `precondition_failed` before capture. The class consequence of those refusals. The absent-aware rollback. Capture through `sys.executable -m agentic_mbse`. The project-root check and one-line CLI errors. `KeyedFileSource` and the `batch` profile.

**Recorded in phase notes.**

- *Parser and index:* a Location's slug no longer needs the trailing `/`; Locations are normalized; the batch block always carries the key line; an anchor on line 1 counts; an empty index gets no leading newline.
- *Guard:* a malformed guard answer is a fault; the guard loads on every call; keyed sources validate `key` (review A9).
- *CLI:* `register --run` refuses a directory that is not a run; `log` prints its usage errors to stderr and accepts an empty value.
- *In memory only:* `RetirementResult.removed` is None on a refusal; findings are a tuple; `OpenResult` carries an outcome, not an exit code; files are read and written as explicit UTF-8.

**Unrecorded.** None of these changes fusion-tea's data or a caller's result:

- **U1. Index writes now go where the caller's paths say.** The snapshot's index writer always wrote the cwd's `knowledge/SOURCE_INDEX.md` (`zotero_ingest.py:270,276`), whatever `paths` the caller passed. The port writes `paths.index` (`register.py:438-449`). This only matters to a Python caller with non-default paths. fusion-tea's Zotero ingest passes none. It is a fix.
- **U2. `register` no longer prints an extra line.** The snapshot's writer printed `  Appended SOURCE_INDEX.md entry: <title>` (`zotero_ingest.py:279`), so `source_registry.py register` printed that line before its JSON. The port prints JSON only, so output is now parseable as-is. fusion-tea's batch ingest loses that per-item line, and its suite passes (34) on the branch.
- **U3. Registered prose can now change how the index parses.** See F1. This is the one unrecorded consequence with a data-structure effect, and it is improbable.
- **U4. `retire`'s rollback no longer skips a vanished file.** It moves parked artifacts back without first checking they still exist (`retire.py:357-358`). The snapshot skipped a missing one (`source_registry.py:1172,1176`). This only matters if something outside deletes a parked file during a failed retirement.

### Hold-out hook fails closed (brief priority 2)

Every guard call and every read of a match goes through `_ask` (`holdout.py:107-121`), which turns any exception or malformed answer into `HoldoutGuardError`. Loading never raises: every configuration or load fault gives `_UnavailableGuard`, whose every check raises (`holdout.py:195-209`).

- **`register`.** The pre-capture fault refuses `precondition_failed` (`register.py:244-249`). The post-capture fault refuses with the captured `source_id`, so it counts against `max_captures` (`register.py:339-346`, `:557-560`). The CLI passes no guard, so the project's guard always loads (`research_cli.py:166-168`).
- **`retire`.** The fault refuses under the lock, before the slug check (`retire.py:133-136`).
- **`add-entry` and `--replace`.** Both are guarded before the lock (`index.py:458-468`). `remove-entry` has no guard, which is right: a removal admits nothing.
- **The rejected paths.** I found no path that proceeds unchecked while a correctly named guard is configured. `KeyboardInterrupt` and `SystemExit` propagate, and nothing registers. A guard that reads its own protocol relative to the cwd (fusion-tea's `holdout_guard.py:19`) and fails from the wrong directory fails closed, where it used to crash.
- **The one residual is F3:** a misspelled table name.

### Spec conformance (brief priority 3)

1. **Met.** Install, list, directories and ignore lines. `tests/test_cli.py` covers this: `TestDirectoryStructure`, `TestResearchRegistryGitignore` (fresh init, re-init appends once, a symlinked `.gitignore` is left with a message), and `TestResearchAcquireInstall`. The O2 setup checks confirm it from the wheel: both directories, `.gitignore:59-60`, and line 17 of `install-commands --list`. A clone does not carry the two empty directories, but `open` and `close` create them (`runs.py:48`, `seam.py:392`), so nothing depends on them.
2. **Met.** One request end to end in a fresh target. In `evidence/dry-run/README.md`, the O2a run, from the wheel with no fusion-tea on any path, ended `REGISTERED` with the source directory, manifest row, index block and receipt. `verify` exits 0. The stream shows only `open | log | register | close` and no direct edits. (The request differs from the design's runbook: A4.)
3. **Met.** `uv run pytest tests/test_research -m ""`: 531 passed. The tests reach all four classes (`BLOCKER` computed in `test_return_contract.py:205`), all six `register` outcomes (`holdout_hit` through `FakeGuard`, `ScriptedGuard` and a guard file), and `retire` and `verify`. I found no skip, `xfail`, `type: ignore`, `noqa` or TODO in the new code or tests.
4. **Met.** Parity on fusion-tea data, in `evidence/o1-parity-early.md`:
   - `verify` lines match, plus exactly the two `legacy block_without_row` lines, and both exit 0, through Python and then the CLI.
   - The URL duplicate and the `zotero_key` duplicate both refuse before any fetch.
   - `open` on the negative's request gives byte-identical output from the CLI and the script.
   - I could not read fusion-tea; this rests on that evidence, which is consistent with the baseline record (`o1-baseline.md`).
5. **Met.** I ran the criterion's grep, `grep -rniE "fusion-tea|MR-[0-9]|\baries\b|zotero|\.project/"`, over `skills/research-acquire`, `docs/research-seam.md` and `src/agentic_mbse/research`. It prints nothing. `test_no_consumer_names.py` runs the same pattern.
6. **Met on the fusion-tea branch; live after O3.** In `evidence/o1-fusion-tea-branch.md` (fusion-tea `940500788`, not pushed):
   - The scripts, the command and the old guide are deleted.
   - `zotero_ingest.py` registers through `KeyedFileSource`.
   - The guard named in `pyproject.toml` refuses a barred URL as `holdout_hit`.
   - `tests/research` passes, 34 tests: the 167 before, minus the 140 moved here, plus 7 new.
   - Every ledger home is on the branch or at `0a833b9f7`.

   fusion-tea `main` is unchanged until the owner merges after O3, as Align decided. The ledger's evidence pointer is stale (A2).
7. **Met.** `/manage-sources` by hand, in `evidence/dry-run/README.md`, O2b: register a local PDF (manifest row and hashes), add a codebase entry, list both correctly labelled, retire with a `RETIRED.jsonl` line while `verify` exits 0, and remove the hand-curated entry so the index returns to its init blob. None of the five sessions used Write or Edit. `--replace` and the queue action were not exercised; the criterion does not name them.
8. **Met.** `skills/run-goal/SKILL.md:66,68` and `GOAL_RUNBOOK.md.template:289-298` carry the design's exact texts, with the four-row class table. `test_shipped_contracts.py` pins them, and `tests/test_goal_layer.py` passes.
9. **Met.** All four commands ran at `bdc7cb2`:
   - `uv run pytest tests/`: 2,748 passed, 1 skipped, 1 xfailed, 14 deselected, 0 failed. The baseline was 2,217 passed; the 9 more deselected are the new `slow` tests.
   - `uv run pytest tests/test_research -m ""`: 531 passed.
   - `uv run ruff check src/ tests/`: 118, the baseline. The files this item adds or edits are clean.
   - `uv run mypy src/`: 88 in 18 files, the baseline. No finding in `research/`, `research_cli.py`, `cli/__init__.py` or `__main__.py`.

**Tagged requirements.**

- **[HARD] no imports from fusion-tea, sysml-codegen or teax:** met. Grep and the wheel install with no fusion-tea on any path both confirm it.
- **[INHERITED] data valid with no migration:** met (criterion 4).
- **[INHERITED] never `--index`/`--summarize`:** met (`capture.py:33`, `test_capture.py`).
- **[INHERITED] ADR-0008 identity and dedupe order:** met.
- **[INFERRED] behaviour preserved:** met, with U1–U4 above.
- **[NEED] owner's `/manage-sources` ruling:** met.
- **[INFERRED] (a) cases:** met. Capture through `register`, hand-curated entries legal, removal by `retire` or `remove-entry`, labelled listing, queue resolution, and every write under the lock.
- **[INFERRED] `verify` reports index entry without row:** met (`verify.py:149-173`).
- **[INFERRED] hook fails closed:** met, except F3.
- **[INFERRED] works against the shipped index:** met. Both anchors and the fallback, and tests build from the live template with no manifest.
- **[INFERRED] class mapping in the goal layer:** met.

**Non-goals respected.** Zotero ingest and the ARIES-CS material stay in fusion-tea. `/research`, `pm save-research` and `pm approve-research` are untouched. `EXTRACT-PROVENANCE-HOOK` is ported as a workaround and described in the guide.

### Design conformance

The implementation follows D1–D18 and I1–I8.

- **Module layout.** The twelve modules sit where the Component Overview puts them. `seam.py` imports only `runs.py` (I7), and the registry modules never import `seam.py`.
- **Public API.** `__all__` is the thirteen D2 names (`test_public_api.py`).
- **Retire rungs.** They are module-level, and the guard sees the literal `knowledge/sources/<slug>`.
- **D13 and D15.** The CLI root check and the interpreter-based capture are as designed.
- **Deviations.** Each is recorded in its phase's notes, for example `replace_entry` as its own function and the `[AGENT]` refusals in `add-entry`.
- **I3 is slightly overstated for one failure mode** (A1).

### Code integrity (brief priority 4)

- **Typing and boundaries.**
  - Frozen dataclasses hold results, `TypedDict`s hold receipts and returns, and `Literal`s hold outcomes. mypy is clean on every new file.
  - `index.py` is the largest module (555 lines). It holds the parser, the renderers and the guarded hand-curated writers, as the design assigns. It imports `holdout.py` for those writers, which is acceptable.
  - The one `assert` (`research_cli.py:217`) only narrows a type on the `retired` path.
- **Failure honesty.** The broad `except Exception` blocks are deliberate and documented. `_ask` must not let any guard exception read as "nothing barred". `_load_guard_file` turns a load error into a fail-closed guard. `_commit` and `_remove` roll back and re-raise. No silent fallback.
- **Dead code.** None found. The snapshot's keyless batch block and its one-line rung wrappers were dropped, and the notes say so.
- **Tests.**
  - The tests check behaviour, not names. Byte-level goldens come from the snapshot, frozen in `tests/test_research/golden/` and never recomputed from ported code.
  - Every phase records mutation checks, and each mutation failed at least one test.
  - A session check fails the suite if anything is written under the repository's own `knowledge/`.
  - I found no loosened golden value. The one golden-adjacent edit, `test_a_block_ends_where_a_comment_opens` after P6's template change, keeps its byte-for-byte cut assertion.

### Shipped text (brief priority 5)

- **They read as general rules.** The skill and guide name no consumer. Examples are labelled: the Nb3Sn request, the EPFL preprint, the widget guard.
- **They match the CLI.** I checked every flag, output shape, refusal and exit code in `research-acquire/SKILL.md`, `manage-sources/SKILL.md` and `docs/research-seam.md` against `research_cli.py`:
  - `open` exits 0/2/3;
  - `register` exits 0 only for `registered`;
  - entry writes exit 0 only for added, replaced or removed;
  - `Error:` lines go to stderr;
  - `sources` prints its line format;
  - `retire` prints JSON on refusal and text on success.

  `test_command_contract.py` parses every CLI call shown in the skill and the guide. The exceptions are A5 and A6.
- **`manage-sources` meets the owner's ruling.** A person can do every hands-on action: add with capture, add without, remove either kind, edit, list, and resolve a queue. Every change goes through a CLI call that takes the lock and asks the guard. The skill states it never edits the four registry artifacts, and the O2b dry run showed an agent following it with no direct edits.
- **`docs/source-index.md`, `source-traceability`, the template, `onboard` and `toolkit-awareness`** match the design's exact texts and the CLI. The remaining hand-edit pointer is in `init`'s output (F2), not in a skill.

---

## Certification

**Checked:**

- Every source module and the CLI, against the snapshot's `source_registry.py`, `research_seam.py`, `zotero_ingest.py`, `zotero_lib.py`, `holdout_guard.py` and `research-acquire.md`.
- The hold-out paths through all three writers.
- The four checks for criterion 9, which I ran myself.
- The criterion 5 grep, which I ran myself.
- Two edge cases, run in memory: F1 against the package, and F3 on temp directories.
- The evidence for criteria 2, 4, 6 and 7, for consistency and completeness.
- The shipped text against the CLI.

**Marked:**

- `spec.md`: criteria 1–9.
- `plan.md`: the orchestrator's O1 and O2 checkboxes the evidence supports, with a note on the evidence file names.
- The epic's Item 5 heading and its six success checkboxes.
- `CURRENT_WORK.md`: certified with follow-ups F1–F3.

**Not checked:**

- **fusion-tea itself.** I cannot read it. Criteria 4 and 6 rest on the orchestrator's evidence; I did not re-run them.
- **The O3 post-merge pin move and re-init.** These are owner-paced and not run.
- **The O2 dry runs.** I did not re-run them. I read their record and its artifacts, not every line of the six streams.
- **Codex.** I did not exercise it; the dry runs ran Claude only.
- **Two `manage-sources` paths.** `--replace` and "Resolve a queued candidate" are covered by unit tests only, not by a dry run.
- **Concurrency.** I did not stress-test the registry lock under real concurrent writers beyond the ported `test_staging_concurrency.py`.
