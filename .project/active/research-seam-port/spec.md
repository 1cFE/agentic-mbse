# Spec: Port the research acquisition seam, and bring `/manage-sources` under its rules

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-10-08
**Complexity:** HIGH (behaviour-preserving port of ~1,800 lines across two repos, against live registry data in fusion-tea)
**Branch:** `main` (no item branch yet)
**Epic:** `WRAP-SPLIT`, Item 5

---

## Problem

agentic-mbse has no way for a target to bring an outside source into `knowledge/` with proof that it is there. The capability exists only in fusion-tea, as one prompt file and two scripts. Item 2 of this epic ships fusion-tea's goal layer (`run-goal`) from agentic-mbse, and `run-goal` delegates every source acquisition to that seam (fusion-tea `.claude/skills/run-goal/SKILL.md:63`). Without this item, an installed `run-goal` points at a procedure no other target has.

[OWNER-VERBATIM] 2026-10-06: "yes, we need this capability in agentic-mbse."

The shipped tool for hands-on curation, `/manage-sources` (`claude/commands/manage-sources.md`, 82 lines, last changed 2026-02-02), predates the registry (fusion-tea, 2026-08-25). It was written when `SOURCE_INDEX.md` was the whole registry. It reads the index, lists entries, and adds or removes entries by editing the file directly. Once the registry ships, that breaks the registry's rules in four places:

- **Adding a document** writes a hand-made entry with no captured copy, no hash, no duplicate check and no hold-out check. fusion-tea's two ITER Cryoplant entries point into `knowledge/sources/` with no manifest row; this is how they arose. `verify` cannot see this case.
- **Removing a registered source** deletes only the index entry. The manifest row and source directory stay behind, `verify` reports a fault, and nothing records the removal in `RETIRED.jsonl`.
- **Types and headings disagree.** `/manage-sources` and the source-traceability skill know four types (codebase, documentation, database, reference; `claude/skills/source-traceability/SKILL.md:58`); the registry writes `url` and `local_pdf`. The registry's anchor heading, the shipped template's heading and the heading `/manage-sources` writes are three different strings.
- **It edits outside the registry's lock**, so a hand edit and a background registration can lose one another's write.

What it does that still fits: adding and removing sources that cannot be captured (a codebase, a database, a person, a book, an in-repo dossier), editing an entry's description, listing sources, and offering read permissions for local paths. fusion-tea's index has four such entries today.

**How the seam works.** Research is two stages with a wall between them. Acquisition proves a source is in the repo. Reading (`/research`, `pm save-research`, `pm approve-research`) reasons only from sources already proven in; it ships today and does not change. In acquisition, an LLM decides exactly three things: the search queries, keeper / rejected / failure per hit, and three sentences per keeper (use-for, validation, caveat). Code does everything else, and the result class is computed from files the code wrote. The end-state call stack, from the design page the owner approved on 2026-10-09 (Related Artifacts):

```
owner        /run-goal <goal>                                   [LLM session]
└─ goal round agent (that session)
   ├─ writes  knowledge/research/requests/REQ-036-01.json      [file]
   ├─ Agent tool → fresh subagent                               [LLM]
   │     prompt: "follow the research-acquire skill on REQ-036-01.json"
   │     ├─ Bash  agentic-mbse research open REQ-036-01.json    [code] → run dir, run.jsonl
   │     ├─ WebSearch (≤5)                                      [LLM picks queries]
   │     │     Bash  agentic-mbse research log --search "…"     [code]
   │     ├─ WebFetch each hit                                   [LLM: keeper / rejected / failure]
   │     │     Bash  agentic-mbse research log --candidate … --triage keeper --note "…"   [code]
   │     ├─ Bash  agentic-mbse research register --url … --use-for … --validation … --caveat … --run <dir>   [code]
   │     │     └─ subprocess  agentic-mbse extract --save-source --budget 0 → .staging/   [code, no LLM]
   │     │        sha256 → hold-out hook → dedup → write 4 files or refuse → receipt     [file]
   │     ├─ Bash  agentic-mbse research close <dir>             [code] → return.json {class}
   │     └─ returns a text summary                              [LLM]
   ├─ reads  return.json; appends the task return to trail.md  [file]
   └─ next task, if REGISTERED: Agent tool → subagent running /research   [LLM]
         └─ Bash  pm save-research                              [code] → research/pending/
owner        pm approve-research --insights …                   [human] → research/approved/, KNOWLEDGE.md
```

**What exists today in fusion-tea** (verified against source 2026-10-08):

- `.claude/commands/research-acquire.md` — 125 lines, a prompt only. Its six shell snippets call `uv run python scripts/research_seam.py …` and `scripts/source_registry.py register`.
- `scripts/research_seam.py` — 463 lines: `open`, `log`, `close`. Computes one of four classes from receipts and the run log, in this order: REGISTERED, OPERATOR_QUEUE, BLOCKER, BOUNDED_NEGATIVE (`research_seam.py:234-247`).
- `scripts/source_registry.py` — 1,350 lines: `register`, `verify`, `retire`. The only code that writes `knowledge/sources/`, `MANIFEST.jsonl`, `SOURCE_INDEX.md` and `RETIRED.jsonl`. Calls no LLM; it shells out to `agentic-mbse extract --save-source` with budget 0 (`source_registry.py:55-66`).
- Its fusion-tea couplings: `import holdout_guard` (ARIES-CS protocol path and term list, `holdout_guard.py:19-35`), index and manifest helpers from `zotero_ingest.py` / `zotero_lib.py` (`source_registry.py:44-52`), and a `ZoteroSource` input kind (`:128-163`) that fusion-tea's Zotero batch ingest constructs (`zotero_ingest.py:491,574`), matched on a `zotero_key` manifest field (`:416-417`).
- `docs/research_seam_operator_guide.md` (287 lines), ADR-0008 (source identity), `tests/research/` (20 test files; 10 of them import Zotero or hold-out code, including `conftest.py`).
- Live data: 123 manifest rows, 1 `RETIRED.jsonl` line, 61 run directories, 1 bounded negative, 9 request files.

## Success Criteria

- [ ] A fresh `agentic-mbse init` installs the `research-acquire` skill, `agentic-mbse install-commands --list` names it, and the target has `knowledge/research/requests/runs/` and `knowledge/research/requests/negatives/`. The target does not track `knowledge/.staging/` or `knowledge/.registry.lock`, whether freshly initialized or re-initialized.
- [ ] In a fresh target with no fusion-tea code on any path, one request runs end to end through the installed skill and `agentic-mbse research open | log | register | close`, ending in `return.json` with class REGISTERED and the four registry artifacts plus a receipt. The run is recorded in the item's evidence.
- [ ] The ported tests pass in agentic-mbse. Between them they cover each of the four classes and each `register` outcome (`registered`, `duplicate`, `holdout_hit` through a test-supplied hook, `capture_failed`, `precondition_failed`, `limit_reached`), plus `retire` and `verify`.
- [ ] On a copy of fusion-tea's `knowledge/`, the installed package behaves as the scripts do: `agentic-mbse research verify` reports the same findings as `scripts/source_registry.py verify`, plus the new index-entry-without-row findings (the two ITER Cryoplant entries, and nothing else unexpected); registering a source already in the manifest returns `duplicate` (including a Zotero row matched by `zotero_key`); `open` on the request the existing negative answers refuses.
- [ ] `grep -iE "fusion-tea|MR-[0-9]|aries|zotero|\.project/"` over the shipped skill, `docs/research-seam.md` and `src/agentic_mbse/research/` returns nothing outside text labelled as an example.
- [ ] fusion-tea after the port: `scripts/research_seam.py` and `scripts/source_registry.py` are deleted; its Zotero ingest registers through the installed package; a hold-out fixture still refuses through its own guard wired into the hook; its research and Zotero suites pass. Every consumer-specific line removed from the ported text has a migration-ledger row whose destination exists in fusion-tea before the agentic-mbse change merges.
- [ ] Using only the shipped `manage-sources` skill in a fresh target, a user adds a capturable document (it lands registered, with manifest row and hash), adds a source that cannot be captured, removes a registered source (it is retired and `verify` stays clean), removes a hand-curated entry, and lists both kinds correctly labelled. Recorded in evidence.
- [ ] The shipped `run-goal` (Item 2) cites the installed `research-acquire` skill and `agentic-mbse research` CLI instead of Item 2's interim wording.
- [ ] `uv run pytest tests/`, ruff and mypy pass in agentic-mbse.

## Known Requirements

- **[INHERITED: epic header, owner 2026-10-06]** No loss of information for fusion-tea. Anything removed from the ported text because it is consumer-specific is migrated into fusion-tea's own files and recorded in `.project/active/wrap-split-migration-ledger.md`.
- **[INHERITED: epic header, owner 2026-10-06]** Shipped text reads as a general rule or practice. Fusion examples may stay when labelled as examples. Pointers into fusion-tea internals as authority (`.project/` design docs, `MR-4`, the ARIES-CS protocol path) must go.
- **[HARD]** agentic-mbse imports nothing from fusion-tea, sysml-codegen or teax. It depends on none of them (`pyproject.toml`); dependency runs the other way.
- **[INHERITED: epic Item 5 criterion, resting on the owner's no-loss decision 2026-10-06]** fusion-tea's existing registry and request data stays valid with no migration. Manifest rows (including `zotero_key`), `RETIRED.jsonl`, `.registry_baseline.json`, run directories, and negatives keyed by request hash are read as they are. A change to the request-key formula (`research_seam.py:70-83`) would silently reopen a recorded negative.
- **[INHERITED: `source_registry.py:63-66`]** `register` never passes `--index` or `--summarize` to `extract`. Those flags run the `claude` CLI, which the code comment says refuses to run inside a Claude Code session, and the seam is always run by an agent.
- **[INHERITED: fusion-tea ADR-0008, `[AGENT]` delegated by owner]** A source's durable identity is the SHA-256 of its raw bytes as fetched, kept separate from the digest of the stored copy. Dedupe order: external key when supplied, then `source_id`, then normalized URL before fetch.
- **[INFERRED]** The port preserves behaviour: the four classes and their precedence, the register refusal ladder and its six outcomes, one receipt per register attempt, the four-files-or-nothing commit under one lock, the request-key rule, and the receipt, return and manifest shapes. The LLM's three decisions stay the only LLM decisions.
- **[INFERRED]** `research-acquire` ships as a skill (a prompt file) installed by `agentic-mbse init` like every other shipped skill, on whichever installer layout Item 1 leaves as the single source. The code ships as `agentic-mbse research open | log | close | register | retire | verify`. Source: the page's port table (page approved by owner 2026-10-09).
- **[NEED]** [OWNER-VERBATIM] 2026-10-09, on `/manage-sources`: "it seems like it would be MORE useful as a general skill which allows direct user management while it folows and enforces the rules the rules. i.e. (a)". The outcome: a user manages sources directly, by hand, through a shipped skill, and every change it makes follows the same rules the registry enforces.
- **[INFERRED]** (option (a) as presented to the owner 2026-10-09) That skill covers each hands-on case. A document that can be captured is registered through the registry, with the user writing the same three sentences an agent writes. A source that cannot be captured stays a legal hand-curated entry. A registered source is removed through `retire`; a hand-curated entry is removed directly. Listing shows which entries are registered and which are hand-curated. A candidate the seam queued for the operator can be cleared from it. Hand-curated entries and registry writes cannot lose each other's changes.
- **[INFERRED]** `verify` reports an index entry whose location is under `knowledge/sources/` but has no manifest row. Hand-curated entries pointing anywhere else are not findings.
- **[INFERRED]** A hold-out check is a hook the target supplies. With none configured, nothing is held out. With one supplied, a hit refuses the candidate and queues it for the operator, and nothing in the seam can waive it. A guard that is configured but fails to load refuses every registration with a receipt rather than registering unchecked; today a missing `holdout_guard` fails the import loudly (`source_registry.py:44`), and the hook must not make that failure silent.
- **[INFERRED]** `register` works against the source index a target actually has. Today the index writer refuses any `SOURCE_INDEX.md` without the heading `## How Sources Are Used` (fusion-tea `zotero_ingest.py:222,271-275`). The index `init` ships has `## How This File Is Used` instead (`SOURCE_INDEX.md.template:36`), and the file is user-owned, so existing targets never receive a new heading on re-init. The blocks the registry writes (`**Type**: url | local_pdf`, a caveat, extended metadata) must also be a source type `docs/source-index.md` defines; today it defines only codebase, documentation, database and reference. The ported tests use the index `init` ships, not fusion-tea's.
- **[INHERITED: CLAUDE.md "Change Coordination"; epic-F2]** The `cmd_init` changes land under Item 1's ruling on `scripts/replicate_setup.sh`, which on `main` still creates `knowledge/research/*` itself (`replicate_setup.sh:116-118`).
- **[INFERRED]** Zotero ingest stays in fusion-tea and keeps registering through the same door, so the registry accepts an externally keyed local file without naming Zotero.
- **[INFERRED]** `retire` and `verify` ship in this item. The page's port table lists them; its summary names only four subcommands. They share the registry's lock and data, and splitting them off would leave fusion-tea needing the deleted script for maintenance.
- **[INFERRED]** This item, not Item 2, relabels the shipped `run-goal`'s research references, because this item creates the names they point at. Recorded in the epic under both items.
- **[INFERRED]** The seam defines the classes; the goal layer maps them to task outcomes and never defines classes. The mapping itself (REGISTERED → COMPLETE, OPERATOR_QUEUE → OWNER_GATE, BLOCKER → PREREQUISITE, BOUNDED_NEGATIVE → BOUNDED_NEGATIVE) is the page's proposal and belongs to Item 2's runbook.

## Non-Goals

- Zotero ingest and the ARIES-CS hold-out term list and protocol stay in fusion-tea.
- Reading and approval are unchanged: `/research`, `pm save-research`, `pm approve-research`.
- Out of scope: folding `research-acquire` into `/research`, because `/research` is the reading stage and does not acquire (rejected in the synthesis, 2026-10-06).
- Out of scope: the extraction provenance gap (`EXTRACT-PROVENANCE-HOOK`). The registry's current workaround ports as it is.

## Open Questions / Deferred to design

- **Owner: may a goal delegate insight approval, with `pm approve-research` recording the approver?** Yes allows unattended goals with agent-approved insights; no stalls unattended goals at each research task. This changes `pm approve-research`, which this item does not touch; a yes becomes its own backlog item.
- **Surfaced conflict: a malformed request has no computed class.** The page says `close` always writes `return.json` and gives "request file missing its consumer field" as its BLOCKER example. In the code, `open` refuses a malformed request with exit 2 and creates no run directory (`research_seam.py:104-106`), so `close` cannot run and the skill tells the agent to report BLOCKER itself. A computed BLOCKER exists only for a fault logged after `open` with no receipts. Lean: port as is, and correct the example in the shipped guide. The alternative, having `open` write a return, is a behaviour change.
- **Design: the neutral external source kind** that replaces `ZoteroSource`. It must keep the stored `zotero_key` field matching existing rows and keep the batch index profile. Whether fusion-tea's Zotero scripts then import `RegistryPaths` and the manifest helpers from the package (one owner) or keep their own copies (two copies of the same code in fusion-tea) is a design call; lean: import.
- **Design: how the registry finds its place in a user-owned index** (accept the shipped heading, append at end, or another anchor) and whether `url` / `local_pdf` join the type table in `docs/source-index.md` or the blocks conform to an existing type. The registry and the `manage-sources` skill must agree on the answer.
- **Design: how a target supplies the hold-out hook.** The registry calls three functions and one result type (`check_input_path`, `scan_terms`, `scan_file`, `Match`; `source_registry.py:346-389,933-979`). Mechanism (config path, entry point, module setting) is open.
- **Design: the test split.** "Move everything minus Zotero and hold-out-term tests" does not divide cleanly: `conftest.py` and eight other files import Zotero or hold-out code. Design assigns each of the 20 files: move with a fake hook, stay in fusion-tea, or split.
- **Design: ignoring `.staging/` and the lock on existing targets.** A target's `.gitignore` is user-owned (created once). Precedent for appending missing lines exists (`src/agentic_mbse/cli/__init__.py:498`).
- **Design: the `manage-sources` skill's shape.** How a hand-curated entry is written so it cannot race a registration (through a CLI call under the registry's lock, or otherwise); how the user is asked whether a source can be captured; how the queued-candidate case is presented. Today `verify` checks a source directory without a row, a row without a directory, and a row without an index entry (`source_registry.py:748-823`); the new check is the missing direction.
- **fusion-tea: the two ITER Cryoplant entries.** Once `verify` sees them, fusion-tea registers them properly or records them in its baseline as legacy. The owner's call, on the fusion-tea side.
- **Design: sequencing with fusion-tea.** fusion-tea pins agentic-mbse by SHA; its scripts can only be deleted after the pin moves to a commit carrying the package. Where the ADR-0008 decision record lands (`docs/research-seam.md` or Item 2's `docs/goal-layer-decisions.md`) under the epic's snapshot-authority stance.
- **Design: two copies kept in sync by hand** (product-lens smell 1, same as epic smell 1). The shipped condensation of ADR-0008 beside fusion-tea's live ADR, and the index and manifest writers copied into the package beside fusion-tea's Zotero copies. Design names which copy is authority for installed targets.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_wrap-split.md` § Item 5
- **Design page ([AGENT], approved by owner 2026-10-09):** `.project/mental-alignment-v2/runs/20261006-150340_research-process-end-state_fresh.html`; its synthesis `20261006-150340_research-process-end-state.md` is superseded on two points (see epic Source Documents)
- **Required Reading:** `.project/research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md` § 1c; fusion-tea `.claude/commands/research-acquire.md`, `scripts/{research_seam,source_registry,holdout_guard}.py`, `docs/research_seam_operator_guide.md`, `.project/adr/0008-source-identity-raw-bytes-sha256.md`
- **Migration ledger:** `.project/active/wrap-split-migration-ledger.md` (created by Item 2)
- **Product-lens:** `.project/active/research-seam-port/product-lens.md`
- **Design:** `.project/active/research-seam-port/design.md` (to be created)

---

**Next Steps:** Owner rules on the three owner questions above; then `/_my_spec_review` in a fresh session, then `/_my_design`.
