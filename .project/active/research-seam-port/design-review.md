# Design Review: Port the research acquisition seam, and bring `/manage-sources` under its rules

**Design:** `.project/active/research-seam-port/design.md` (Draft, 2026-10-12, at `58af700`)
**Spec:** `.project/active/research-seam-port/spec.md`
**Review File:** `.project/active/research-seam-port/design-review.md`
**Brief:** `briefs/design_review.md` (the only review round)
**Date:** 2026-10-12
**Evidence base:** fusion-tea snapshot `.orchestrate-logs/fusion-tea-snapshot/` (fusion-tea `0a833b9f7`), read directly; agentic-mbse at `58af700`. `scripts/zotero_group_download.py` and `scripts/test_zotero_write_access.py` are not in the snapshot, so claims about them are unverified here.

---

## The Point

A target brings an outside source into `knowledge/` through one checked door, with proof it is there, using only what `agentic-mbse init` installs. [OWNER-VERBATIM] 2026-10-06: "yes, we need this capability in agentic-mbse." A user managing sources by hand goes through the same door: [OWNER-VERBATIM] 2026-10-09, `/manage-sources` should be "MORE useful as a general skill which allows direct user management while it folows and enforces the rules". [INHERITED: epic, owner no-loss 2026-10-06] fusion-tea switches over with no data migration and no lost instruction. The installed `run-goal` (Item 2) delegates every acquisition to this seam, so without it the goal layer points at a procedure no other target has.

## Fundamental Assessment

**Sound, with concerns. This is the right piece of work, and the approach is right.**

- **Right work.** The point above is owner-stated twice, and the design serves it directly. My independent read of the point matches the design's (product-lens block appended to `product-lens.md`).
- **Right approach.** It keeps the seam's three layers (skill prose, thin CLI, package) and copies every on-disk shape. Each fusion-tea coupling becomes a seam the target fills: a guard file named in `pyproject.toml`, a keyed source kind whose field names the caller supplies, and an anchor rule that accepts both headings. I checked the riskiest parts against the snapshot code. The ladder order, class precedence, request key, receipt and return shapes, and the Zotero row and block shapes all survive the split as designed.
- **Abstractions earn their place.** The twelve modules average about 150 lines each, follow the existing `pm/` + `pm_cli.py` pattern, and each owns one thing. The guard `Protocol` is structural, so fusion-tea's module conforms unchanged (`holdout_guard.py:44-109`). `KeyedFileSource` (D6) is wide (six fields), but every field is needed to reproduce the Zotero row and block byte for byte. A simpler "copy two files into `src/`" was rejected by the brief's engineering bar, and D1 records why.
- **The concerns are local.** Two paths let a source into the index without the hold-out check when a guard is meant to apply (M1, M2). One instruction the skill will ship is false (M3). One runbook step runs out of order (M4). One invariant contradicts the snapshot's receipt behaviour (M5). Each has a one-line fix. None of them changes the architecture.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

- **Criteria 1–9 each have a design element and named evidence** (Validation Approach table). Criterion 3's outcome coverage, criterion 4's parity run and criterion 6's fusion-tea branch are concrete.
- **The owner's `/manage-sources` ruling is met for four of five rules, not the fifth.** `register`, `retire`, the lock and the type rules all apply. The hold-out rule does not: `add-entry` and `add-entry --replace` (D11, design line 63) write a hand-curated block with no guard call. In fusion-tea, a user could add a hand-curated entry whose Location is `knowledge/holdout/aries-cs/…` or whose title names a sealed paper, and every agent that reads `SOURCE_INDEX.md` would be pointed at it. That lets criterion 7 pass while the owner's "follows and enforces the rules" fails. → M1.
- **The spec's fail-closed hook requirement is met for load faults, but not for a mistyped key.** Design line 105: "no `holdout-guard` key gives a guard that matches nothing." A target that writes `holdout_guard = "scripts/holdout_guard.py"` (underscore, the natural Python spelling) inside `[tool.agentic-mbse.research]` gets no guard and no warning. Product-lens spec-F3, the finding this requirement came from, names "a mistyped config" as the case to close. → M2.
- **The queued-candidate requirement ([INFERRED]: "A candidate the seam queued for the operator can be cleared from it") rests on a false claim.** Design line 222 says that after the user registers a copy they obtained, re-running the request "returns `REGISTERED` as a duplicate." The code says otherwise in the canonical queue case, a paywall. The user registers the PDF with `--local-pdf`, so the row carries `origin_path`, not `source_url`. URL dedupe matches only `source_url` (`source_registry.py:409-426`). The re-run's agent hits the same paywall and queues it again, or captures the landing page as a new source. The guide's existing flow does not re-run at all (`research_seam_operator_guide.md:178-186`: get the PDF, register it directly). → M3.
- **Capture fidelity is clean.** The [INFERRED] and [INHERITED] items the design treats as fixed are the ones the brief fixed (behaviour preservation, no fusion-tea imports). ADR-0008 keeps its `[AGENT] delegated by owner` grade. The owner's verbatim lines are carried verbatim.

### 2. Pattern Consistency
**Assessment:** Pass

- The CLI mirrors `pm`: `register_research_subcommands(subparsers)` beside `register_pm_subcommands` (`cli/__init__.py:797-799`, verified).
- The `.gitignore` append follows `_update_gitignore_for_dev_mode` (`cli/__init__.py:278-291`, verified), including its symlink message.
- Skills install from the source tree with no installer edit, as CLAUDE.md "Change Coordination" requires. `docs/` already ships in the wheel (`pyproject.toml` force-include), so `docs/research-seam.md` reaches targets.
- One small mismatch: D15 adds a "must run from the project root" check, which no other subcommand has. It is justified (relative paths in committed `run.json`), and the design says so.

### 3. Abstraction Quality
**Assessment:** Concerns (minor)

- **The module split is clean.** One detail weakens it: D10's comment masking changes where a block ends, and the design does not say how. A `###` block now runs to the next heading outside comments, so a block followed by an HTML comment swallows that comment. `retire` and `remove-entry` would then cut the comment, and `index_block_sha256` would hash it. In a fresh target this bites a user who hand-placed an entry above the template's commented examples (`SOURCE_INDEX.md.template:8-34`). `remove-entry` on that entry would delete the examples and the placeholder line too. → A4.
- **The fail-closed wrapper is the right shape.** One gap: a guard fault after capture becomes `precondition_failed`, and `_spent_a_capture` (`source_registry.py:1235-1240`) does not count that outcome. A guard whose `scan_file` always raises would let a run capture without limit. → A2.

### 4. Duplication Avoidance
**Assessment:** Pass

- D7 removes the second copy of the index and manifest writers. fusion-tea's Zotero code imports them, and `zotero_lib.py` keeps only Zotero views on `load_manifest_rows`. This resolves product-lens smell 1 for the writers.
- D17 resolves the other half of smell 1. The ADR condensation ships as a dated snapshot, fusion-tea's ADR stays live with an amendment line, and the commit-pinned citation sits in the migration ledger.
- `runs.py` replaces the two scripts' duplicate receipt readers and their two names for `run.json`. That is a real cleanup.

### 5. Data Structure Clarity
**Assessment:** Concerns (minor)

- Frozen dataclasses for results, `TypedDict` for the receipt and return, and rows kept as `dict[str, Any]` are all appropriate.
- **I1 pins key *sets*, but the Behaviour Changes table promises rows and blocks that stay "byte-identical".** JSON key order is insertion order (`source_registry.py:675-686`), so a set test passes a reordered row. The golden tests should pin key order and the exact bytes the index insertion writes (`zotero_ingest.py:276-278`: blank line, block, blank line, anchor). They should also check that `register` then `retire` restores the index byte for byte, including D9's new end-of-file fallback, whose bytes the design does not give. → A5.
- `KeyedFileSource.key` becomes a slug suffix and so a path segment (`_resolve_slug`, `source_registry.py:628-641`). `__post_init__` checks `kind` and `key_field` but not `key`. A key with `/` or `..` would escape `knowledge/sources/`, and one with `-` would mint a slug that `retire` refuses (`SLUG_RE`, `:853`). → A9.

### 6. Route Safety
**Assessment:** Concerns

- The CLI surface is explicit, with no catch-all route, and the hook defaults are named.
- **Two routes fail open and are listed under M1 and M2:** a hand-curated write with no guard, and a misspelled config key.
- **Title addressing (B3) needs an ambiguity rule.** Registered titles collide often enough that the registry carries a slug-collision suffix for exactly that reason. `remove-entry` and `add-entry --replace` must match among hand-curated entries only and refuse when more than one matches. The design implies this but does not say it. → A6.
- **The `hand-curated` test reads the Location string literally.** `./knowledge/sources/x` or an absolute path into `knowledge/sources/` would pass as hand-curated and stay invisible to `block_without_row`, whose regex is anchored on the literal prefix (`source_registry.py:861`). Normalize the Location before the check. → A6.
- **`unregistered` entries have no removal route.** These are blocks under `knowledge/sources/` with no row, such as fusion-tea's two ITER Cryoplant entries. `retire` refuses them (`unknown_slug`), `remove-entry` refuses them by D11, and the skill forbids hand edits. If the owner later decides to drop them, the shipped tools offer no path. → A7.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

- **The stated bets are honest.** B1 is tested early by O1. B2 matches the guard's actual surface. B3 and B4 name their failure modes.
- **Hidden bets I found:**
    - **H1. A re-run after a manual registration returns `REGISTERED`.** This is false for the paywall case (M3).
    - **H2. Every guard fault is an exception.** A misspelled key is silent (M2).
    - **H3. A register attempt always writes a receipt.** The snapshot writes none when `RegistrationError` or a capture timeout propagates (`source_registry.py:206-229`, `:475-479`). I2 and the ladder note ("Every exit writes one receipt") state otherwise. An implementer who follows I2 has to invent an outcome for a commit failure. That outcome then changes the class `close` computes, and the Behaviour Changes table does not list it (M5).
    - **H4. fusion-tea's `verify` stays at zero faults.** The guide records three legacy entries and zero faults (`research_seam_operator_guide.md:239`). Under D12, the ITER Cryoplant blocks are `fault` unless their paths are already in `orphan_source_dirs`. If they are faults, fusion-tea's `verify` goes from exit 0 to exit 1 after the switch. The Align ruling keeps them as visible findings, which is fine, but the exit-code change should be stated and checked against anything in fusion-tea that runs `verify` (A14). The WI-031 hand-registered sources may also yield `legacy block_without_row` lines, which O1's "ITER only" pass rule would reject (A11).
    - **H5. The three fusion-tea scripts that stay use none of the names deleted from `zotero_lib.py`.** Two of them are not in the snapshot, and the design's grep guard covers only two of the deleted names (A12).
    - **H6. A guard loaded from a file path behaves like an imported module.** It does for fusion-tea's guard. A guard that uses dataclasses with postponed annotations fails to load unless the module is put in `sys.modules` before `exec_module`. It would fail closed, but confusingly (A3).
- **Decisions name their rejected alternatives**, and the reasons hold up against the code. D13's reason (`uv run` re-syncs and reverts the editable install) and D5's reason (a temp tree must not load the developer's guard) are both correct and non-obvious.

### 8. Reader Comprehension
**Assessment:** Pass

The Overview, Core Concept and Architecture give a reader the model in one pass: three layers, files between them, and each coupling turned into a seam. The decisions are one line each with the rejected alternative. The text is dense in places (Research Findings, Appendix A), but it is reference material and is cited precisely. Nothing hides behind a coined label.

---

## Brief priorities, answered

1. **Behaviour preservation.** The table is nearly complete. I verified that the split, D9, D10, D13 and D15 leave the request key (`research_seam.py:70-83`), class precedence (`:234-247`), the return and negative shapes, and the manifest row order unchanged. Three behaviour changes are unlisted or unstated: receipts on raised errors (M5); the class consequence of D4, D14 and the missing-index refusal, which all now land in `OPERATOR_QUEUE` because `precondition_failed` is a queueing outcome (`research_seam.py:35`) (A1); and D10's effect on block spans (A4).
2. **fusion-tea switches with nothing lost.**
    - **`KeyedFileSource` reproduces `ZoteroSource`.** I checked it field by field: row keys and order, the receipt candidate `zotero:<key>`, the batch block (`zotero_ingest.py:282-304`), key dedupe, the slug suffix, and no raw-copy removal on retire.
    - **The thirteen-name API covers `zotero_ingest.py`.** It uses `register`, `RegistrationError`, `SourceMetadata`, `LocalPdfSource` and `KeyedFileSource`, and it reads `RegistrationResult` only through attributes. The API also covers `zotero_lib.py`'s rebuilt views.
    - **I could not check the other two scripts** (A12).
    - **Appendix C covers the consumer lines I found,** except the guide's spec-requirement ids (A15).
    - **The test split has three small gaps** (A13).
3. **Hold-out hook fails closed.**
    - **Load, missing-function and raise paths are covered** (D4, I4).
    - **Two fail-open paths remain:** M1 (`add-entry`) and M2 (misspelled key).
    - **`retire`'s guard calls match the snapshot**, given "do not change ladder order": `check_input_path` on `Path(slug)` and on `knowledge/sources/<slug>`, then `scan_terms(slug)`, all under the lock and before `SLUG_RE` (`source_registry.py:932-940`). The canonical path must stay the literal `knowledge/sources`, not `paths.sources`, because fusion-tea's guard globs that form (A13).
    - **One caveat outside D15:** fusion-tea's guard reads `PROTOCOL.md` relative to the current directory (`holdout_guard.py:19`). D15 makes that safe for the CLI. Python callers such as Zotero ingest still depend on being run from the repo root, as they do today.
4. **`/manage-sources`.**
    - **A user can do all five criterion-7 actions** with `register --local-pdf`, `add-entry`, `retire --slug`, `remove-entry` and `sources`, and O2b exercises each.
    - **The gaps are the guard (M1), the queue claim (M3), ambiguity and normalization (A6), and the `unregistered` dead end (A7).**
    - **The queued-candidate listing needs a filter.** As designed it reads every `return.json` ever written; fusion-tea has 61 run directories. It should show only the latest run per request (A8).
5. **Plan-readiness.**
    - **P1 cannot pass its own tests as ordered.** The URL and PDF chain tests capture through `python -m agentic_mbse`, but `__main__.py` lands in P4 (A10).
    - **P1 is the largest phase** (eight modules plus about ten moved test files) and may not fit one session.
    - **O1 needs fixes before it can run.** Step 2's guard check runs before step 3 adds the hook table, so it would fetch the barred URL with no guard and report `capture_failed` (M4). Step 1's line-diff would fail on the summary line (A11).
    - **O2 and O3 are executable as written**, apart from naming the syside index for the scratch target (A17).

---

## Resolutions

[Filled in during Stage 4. This run is non-interactive; the orchestrator feeds the must-fix items to the design author once.]

---

## Verdict

**APPROVE WITH CHANGES.** The architecture, decisions and behaviour-preservation plan are sound. Apply M1–M5 in the design. None of them changes the architecture, so the Align rule needs no second review; the orchestrator can verify each fix against its one-line description.

### Must-fix

- **M1. `add-entry` (and `--replace`) bypasses the hold-out guard** (design line 63, line 222; owner ruling 2026-10-09). Fix: `add-entry` runs the configured guard, using `check_input_path` on a path-like Location and `scan_terms` on the title, Location, Use for and Validation. A hit refuses with `holdout_hit`, and a guard fault refuses the same way D4 does.
- **M2. A misspelled key in `[tool.agentic-mbse.research]` silently disables the guard** (design line 105; spec-F3). Fix: any key in that table other than `holdout-guard` is a configuration fault, which gives the failing guard.
- **M3. The "resolve a queued candidate" action promises that a re-run returns `REGISTERED` as a duplicate, which is false for a paywalled URL resolved with `--local-pdf`** (design line 222; `source_registry.py:409-426`). Fix: drop the re-run claim. After registering the obtained copy, the skill reports the new `knowledge/sources/<slug>/` location for whatever waits on the request, as the guide's "Act on a queued source" does.
- **M4. O1 step 2 tests the guard before step 3 adds the hook table to fusion-tea's `pyproject.toml`** (design line 340). Fix: add the `[tool.agentic-mbse.research]` table before the guard check, or move the guard check after step 3.
- **M5. I2 and the ladder note say every `--run` attempt writes one receipt, but the snapshot writes none when `RegistrationError` or a capture timeout propagates** (design lines 104, 194; `source_registry.py:206-229`). Fix: state that a raised `RegistrationError` or `subprocess.TimeoutExpired` writes no receipt and propagates, as today, and that I2 covers returned outcomes. Or, if a receipt is wanted, add the change to the Behaviour Changes table with its outcome and its class effect.

### Advisory

**Major (plan should address):**

- **A1. State the class consequence of D4, D14 and the missing-index refusal.** All three return `precondition_failed`, which `close` queues (`research_seam.py:35`). A broken guard, a missing web extra and a missing index therefore surface as `OPERATOR_QUEUE`, which maps to `OWNER_GATE`, where a seam fault used to map to `BLOCKER` → `PREREQUISITE`. Add this to the Behaviour Changes table. The skill and guide should tell the agent and operator that such a reason is a seam repair.
- **A4. Define how a block ends under D10, and test it.** Either a block also ends where an HTML comment starts, or the design states that `retire` and `remove-entry` cut through trailing comments. Add a `test_entries` case: removing a hand-placed entry above the template's commented examples leaves the examples.
- **A5. Make the golden tests pin byte-identical output.** They should check manifest key order, not key sets. They should pin the exact insertion bytes for both anchors and for the end-of-file fallback (and state the fallback's bytes). They should check that `register` then `retire` restores `SOURCE_INDEX.md` byte for byte.
- **A6. Give `remove-entry` and `add-entry --replace` an ambiguity and normalization rule.** Match among hand-curated entries only, and refuse when more than one matches. `add-entry` without `--replace` refuses an existing hand-curated title. Normalize Location (`./`, absolute paths under the project root) before the `knowledge/sources/` check.
- **A10. Move `src/agentic_mbse/__main__.py` into P1.** The P1 chain tests capture through it. Consider splitting P1 into the support modules plus golden tests, then the register ladder plus chain tests.
- **A11. Fix O1 step 1's comparison.** Compare finding lines only, because the summary line's counts change. Accept `legacy block_without_row` lines whose paths are already in `.registry_baseline.json` (the WI-031 hand-registered sources may produce them). Record `verify`'s exit code before and after. Run the old script with `uv run --no-sync python`, per fusion-tea's CLAUDE.md.
- **A12. Widen O1 step 3's checks before deleting anything.** Grep fusion-tea for every name deleted from `zotero_lib.py`, not only `slugify` and `append_manifest_entry`. Grep for live references to the deleted files: `research_seam.py`, `source_registry.py`, `research_seam_operator_guide.md` and `.claude/commands/research-acquire.md` (including `AGENTS.md` and docs). Import-check `zotero_group_download.py` and `scripts/test_zotero_write_access.py`, which this review could not read.
- **A13. Close the test-split gaps.**
    - Assign `test_load_manifest_rows_returns_every_row` and `test_truncate_manifest_restores_recorded_byte_length` (`test_zotero_path_contract.py`) to the package's manifest tests.
    - Keep a hermeticity check in agentic-mbse: the suite never creates `knowledge/` under the repo root. `test_hermetic_paths.py` is dropped, and `default_paths()` is cwd-relative.
    - In the fake-guard `retire` test, assert the guard receives the literal `knowledge/sources/<slug>`. Or add a barred-slug `retire` case and a barred local-PDF case to fusion-tea's `test_holdout_wiring.py`, since those two calls' argument shapes are what fusion-tea's real guard matches.
- **A14. Say what happens to fusion-tea's `verify` exit code.** State whether the ITER Cryoplant findings are `fault` or `legacy` under D12, and whether `verify` then exits 1. Check that nothing in fusion-tea gates on it.

**Minor:**

- **A2.** A guard fault after capture should count as a spent capture (receipt `captured: true`), so `max_captures` still bounds the run.
- **A3.** Load the guard with the standard importlib recipe: insert it into `sys.modules` under the private name before `exec_module`. Otherwise a guard using dataclasses with postponed annotations fails to load. Note in the hook guide that a guard's own relative paths resolve against the current directory.
- **A7.** Give `unregistered` entries a removal route. Either let `remove-entry` remove a block under `knowledge/sources/` that has no row and no directory, or have the skill say that this case is a hand edit followed by `verify`.
- **A8.** The queued-candidate listing should show only the latest run per `request_id`, and only queued candidates from that run.
- **A9.** `KeyedFileSource.__post_init__` should check `key` against `[A-Za-z0-9_]+`, because it becomes a slug suffix and a path segment.
- **A15.** Extend Appendix C's "Design-record pointers" row:
    - Add the guide's spec-requirement ids (`R-D5`, `R-D6` at guide `:144`) and the scripts' inline `R-*`, `audit F*` and `WI-033` ids.
    - `PM-APPROVE-RESEARCH-EMPTY-INSIGHTS` is already closed (`.project/backlog/BACKLOG.md:735`), so the shipped guide drops that bullet. It should not carry it forward.
- **A16.** I8's `aries` matches inside "summaries", "boundaries" and "binaries", which agentic-mbse code already uses. Keep the literal criterion-5 grep as evidence, and keep those words out of the scanned files, or word-bound the test.
- **A17.** O2's scratch project needs the GitLab extra index so `syside==0.8.4` resolves from the built wheel.
- **A18.** I6 claims more than fusion-tea makes true: `zotero_ingest.re_extract_sources` writes `knowledge/sources/<slug>/` directly. Scope I6 to agentic-mbse's shipped code and skills.

**Overall:** Approve with changes (M1–M5).
**Next Steps:** The orchestrator feeds M1–M5 back to the design author once; the reviewer does not edit the design. Advisory items go to `/_my_plan`.
