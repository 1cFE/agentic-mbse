---
question: "yes, we need this capability in agentic-mbse. can you run /_my_mental_model_v2 for what the end-state agentic-mbse research process will look like?"
date: 2026-10-06 15:10
policy: carried
shape: checkpoint
evidence:
  - agentic-mbse claude/commands/research.md (current /research command)
  - agentic-mbse claude/commands/manage-sources.md (current index editor)
  - agentic-mbse src/agentic_mbse/pm/operations.py save_research, approve_research, supersede_insight
  - agentic-mbse src/agentic_mbse/cli/extract_cli.py (--save-source writes raw.pdf / raw.html into the extract output directory)
  - agentic-mbse src/agentic_mbse/cli/__init__.py (knowledge/ directories init creates)
  - agentic-mbse .project/backlog/BACKLOG.md EXTRACT-PROVENANCE-HOOK
  - agentic-mbse .project/backlog/epic_wrap-split.md (owner decisions; product-lens finding that the seam had been dropped)
  - agentic-mbse .project/research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md § 1c
  - fusion-tea .claude/commands/research-acquire.md
  - fusion-tea scripts/research_seam.py, scripts/source_registry.py, scripts/holdout_guard.py, scripts/zotero_ingest.py (append_source_index_entry), scripts/zotero_lib.py
  - fusion-tea knowledge/research/requests/REQ-036-01.json
  - fusion-tea work/orchestration/GOAL_RUNBOOK.md § The native seams; .claude/skills/run-goal/SKILL.md § Research
  - fusion-tea .project/adr/0008-source-identity-raw-bytes-sha256.md (index entry only)
code_inspected: "Function signatures, constants, the return-class mapping, request fields and outcome tables in the files above; no execution."
limits: "The end state does not exist yet. Everything labelled intended or inference is a proposal for the porting work item, not code. fusion-tea's research design record (.project/active/goal-research-seam/design.md, D1–D14) was not re-read; its decisions are known through the code docstrings that cite them."
---

# TLDR

The end-state research process has two stages and a wall between them. Acquisition brings a source into the project and proves it is there. Reading turns sources already in the project into a research document and, on the owner's approval, into numbered domain insights (`DI-XXX`). The wall is a rule: acquisition never writes an insight, and reading never fetches a source. Without it the failure is concrete. An agent quotes a page summary, registers nothing, and a number sits in a model with no file behind it.

Acquisition takes a bounded request file and returns one of four classes. `REGISTERED`: sources are in the repo and citable. `OPERATOR_QUEUE`: a person must fetch or rule. `BOUNDED_NEGATIVE`: the search ran, found nothing usable, and recorded that so nobody searches again. `BLOCKER`: the machinery failed. The class is computed from receipts the registry writes on disk, never from what the agent reports.

Today agentic-mbse ships only reading. fusion-tea built acquisition as one agent command, `research-acquire`, and two scripts: `research_seam.py` keeps the run record and computes the class; `source_registry.py` is the one registered write path into `knowledge/`. Other tools can still write there, and `verify` reports when they do. The owner decided on 2026-10-06 that acquisition is core and moves into agentic-mbse.

The port changes four things and leaves the process as it is. The scripts become `agentic-mbse research` subcommands. The registry stops importing helpers from fusion-tea's Zotero scripts; a Zotero library remains one way to feed it, outside the port. The hold-out guard, which refuses sources from a sealed list kept unread for blind validation, becomes an optional interface with a no-op default. `init` creates the request directories. The goal layer, the `/run-goal` skill that pursues a question in rounds, already hands research off as a request in and a class out, so it works in a fresh target once the port lands.

# A source is proven in before anyone reasons from it

Every research step in this toolkit answers one question: how does a fact travel from the internet or a PDF into a model's doc comment with a citation a later reader can open? The answer is two stages that write to different places and are forbidden from doing each other's job.

| Stage | Question it answers | Writes to | Must never |
|---|---|---|---|
| **Acquisition** | Do we have the source, and can we prove it? | `knowledge/sources/<slug>/`, `knowledge/MANIFEST.jsonl`, one block in `knowledge/SOURCE_INDEX.md`, the run record under `knowledge/research/requests/` | Mint an insight; quote a fetched page as evidence |
| **Reading** | What do the sources we have tell us? | `knowledge/research/pending/` then `approved/`; `DI-XXX` entries in `knowledge/KNOWLEDGE.md` | Fetch a source into `knowledge/` |

The reason for the wall is traceability under agent operation. An agent that finds and interprets in one breath cites a lossy page summary and leaves a number in the model with no path back to a file. fusion-tea wrote the rule into its command as standing rule 1: WebFetch output "tells you whether a page is reachable and whether it looks relevant. Never quote it, never cite it... The only thing that becomes a source is what `source_registry.py register` captured" (`research-acquire.md:18`, current fusion-tea code). The port keeps it.

**Scope of the rule, stated honestly.** "Only the registry writes sources" is a convention the command enforces on the agent, not a filesystem lock. Two other write paths exist today in agentic-mbse: `agentic-mbse extract --save-source` writes `raw.pdf` or `raw.html` into whatever output directory the caller names, so an agent can point it at `knowledge/sources/` directly; and `/manage-sources` hand-edits `SOURCE_INDEX.md`. Both bypass deduplication, the manifest, and the hold-out check. The registry's `verify` verb already detects the first kind of bypass: a directory under `knowledge/sources/` with no manifest row is reported as an `orphan_source_dir` finding (`source_registry.py:791-794`, current fusion-tea code). So the rule's true scope is: the registry is the one *registered* write path, and `verify` reports anything that got in another way. What to do about `/manage-sources` is in Judgment.

**Visual cue:** two boxes with a wall between them, each box labelled with the `knowledge/` paths it owns, and a third small box above labelled "goal round" with one arrow into Acquisition only.

# Today the toolkit has reading with an owner gate, and no acquisition at all

This is current agentic-mbse code on `main`.

Reading is complete. `/research` reads `SOURCE_INDEX.md`, `KNOWLEDGE.md` and prior research, writes a document, and saves it through `agentic-mbse pm save-research` into `knowledge/research/pending/`. The owner approves with `pm approve-research <file> --insights '<json>'`, which moves the file to `approved/`, assigns `DI-XXX` IDs and appends them to `KNOWLEDGE.md`; an empty list approves with no insights. `pm supersede-insight` replaces an insight and writes an impact report.

Acquisition is absent. The only way to add a source is `/manage-sources`, a hand editor, or running `extract` and typing an index block. Nothing deduplicates, nothing records where bytes came from, nothing stops a second agent from re-searching a question the first one already closed, and `init` creates `knowledge/research/{pending,approved,impacts}` but no place for requests. That is the gap the next section fills.

**Visual cue:** the two-box diagram again with the Acquisition box drawn empty and dashed.

# The end state, walked through one real request

Here is how fusion-tea's request `REQ-036-01` would travel through the end-state pipeline. Only the request file was read; its actual run directory, receipts and `return.json` were not examined, and step 1's account of how the gap was found is the goal runbook's procedure, not the recorded history of this request. The request's question is "What structural design allowable stresses are used for fusion magnet support structures at 4–20 K, and are there sourced higher-strength alternatives to cryogenic AISI 316LN at its 800 MPa design limit?" and whose consumer is work item `WI-036`. The fusion content is an example; the shape is general. Each step carries its status.

1. **A round agent finds the gap.** Under `/run-goal`, the goal layer explained in "The goal layer reads the class" below, an agent pursuing a goal in bounded rounds reads `SOURCE_INDEX.md` and `KNOWLEDGE.md`, finds no sourced allowable stress for cryogenic 316LN, and writes `knowledge/research/requests/REQ-036-01.json` with the question above, `consumer: WI-036`, `gap_type: unsourced_value`, `priority: P1`, five places to look (IEEE Transactions on Applied Superconductivity, Fusion Engineering and Design, Cryogenics, ITER magnet structural reports, ASME BPVC VIII-2 cryogenic practice), and limits of 5 searches and 2 captures. It records the task's scope and start in the goal's trail before any side effect. *Current fusion-tea code and runbook; unchanged by the port.*
2. **The request is handed to acquisition.** The round agent runs `research-acquire` itself or gives the request to a fresh agent with a self-contained brief. *Current fusion-tea skill text; the port changes only the path it cites.*
3. **The bookkeeper opens the run or refuses.** `agentic-mbse research open knowledge/research/requests/REQ-036-01.json` validates the six required fields, hashes the request into a key, and refuses if a durable negative already exists for that key unless an override reason is given. It creates `knowledge/research/requests/runs/REQ-036-01/`. *Current fusion-tea `research_seam.py open`; the CLI name is new (inference).*
4. **The agent searches, triages, and registers keepers.** It searches within the five venues and five-search limit, uses WebFetch only to judge reachability and relevance, and for each keeper writes three sentences (use-for, validation, caveat) and calls `agentic-mbse research register --url ... --use-for ... --validation ... --caveat ... --run <dir>`. The registry stages the capture, extracts it, runs the hold-out screen if this target configured one, deduplicates on the raw bytes, commits four artifacts together, and writes a receipt into the run. A paywalled paper is logged as a failure with disposition `queued`. *Current fusion-tea `source_registry.py register`; the CLI name and the optional hold-out hook are new (intended).*
5. **The bookkeeper computes the outcome.** `agentic-mbse research close <run-dir>` reads the receipts and failure log and writes `return.json` with one of `REGISTERED`, `OPERATOR_QUEUE`, `BOUNDED_NEGATIVE`, `BLOCKER`. If nothing landed, it writes `knowledge/research/requests/negatives/<key>.json` so step 3 refuses next time. *Current fusion-tea `research_seam.py close`; CLI name new.*
6. **The round agent reads the class as a task outcome** and records the return in the trail citing `return.json` by path and commit. *Current goal runbook; the class-to-outcome mapping is this synthesis's inference, see "The goal layer reads the class" below.*
7. **Only now does reading happen.** A later task runs `/research` over the newly registered sources; the document goes to `pending/`; the owner approves it with or without insights; `DI-XXX` entries land in `KNOWLEDGE.md`; the model's doc comment for the 316LN allowable cites the source path and the DI. *Current agentic-mbse code; unchanged.*

**What is unchanged and what is new.** The procedure, the request shape, the four classes, the refusal ladder, the four-artifact commit, the owner approval gate, and the goal runbook's dispatch are all current code or current instruction text and move as they are. New, and the whole of what the port changes in the process: the subcommand names under `agentic-mbse research`; the registry owning its index and manifest helpers instead of importing them from fusion-tea's Zotero scripts; the hold-out guard as an optional interface with a no-op default; and `init` creating `knowledge/research/requests/{runs,negatives}`. Everything else in the port table below is relocation of text and tests that does not change how a request travels.

**Visual cue:** a seven-step vertical sequence, steps 3–5 shaded as "acquisition", step 7 shaded as "reading", with the wall drawn between 6 and 7 and a side arrow from step 5 back to step 3 labelled "negative blocks repeat".

# The request is bounded so a delegated search is finite

Step 1 needs a request shape that a fresh agent can execute without judgment about when to stop. The six required fields are `request_id`, `question`, `consumer`, `gap_type`, `priority`, `where_to_look` (`research_seam.py:26`, current code), and `limits.max_searches` and `limits.max_captures` bound the run. `consumer` names the work item or goal task that will use the answer, so the return has an addressee. `where_to_look` is searched first, then the agent broadens. The bookkeeper counts registrations against `max_captures` through the receipts, so the limit cannot be exceeded by an agent that forgets it. `gap_type` and `priority` are copied through to the run record without validation (`research_seam.py:79`); allowed values are a spec question (see Judgment).

**Visual cue:** the `REQ-036-01.json` file rendered as a card with each field annotated by who reads it (bookkeeper validates; agent follows; return addresses).

# The outcome is derived from receipts, so the agent cannot misreport it

Step 5 is what makes delegation trustworthy. `close` computes the class by a fixed precedence (`research_seam.py:234-247`, current code):

| Class | Condition | What it means for the asker |
|---|---|---|
| `REGISTERED` | at least one registry receipt says `registered` | sources are in the repo and citable |
| `OPERATOR_QUEUE` | nothing registered, but something is queued: a hold-out hit, a failed capture, a missing precondition, or a logged failure with disposition `queued` | a person must fetch it or rule on it |
| `BLOCKER` | a run-scoped fault and no candidate was ever named | the seam itself failed; nothing is known about the search |
| `BOUNDED_NEGATIVE` | everything else: the search ran and found nothing usable | a durable negative is written; the next open refuses to repeat |

The data this rests on is small. Every `register` call with a `--run` argument writes one receipt file under `runs/<request_id>/receipts/`, whatever the outcome (`source_registry.py:1201-1229`, current code):

```json
{"attempt": 1, "outcome": "registered", "candidate": "<url or path>",
 "slug": "<slug>", "path": "knowledge/sources/<slug>", "source_id": "<raw sha256>",
 "triage": "keeper", "reason": "", "rule_id": null, "captured": true, "at": "<utc iso>"}
```

`captured` is what `max_captures` counts: a duplicate or hold-out hit caught before the fetch costs nothing. `close` then writes `return.json` (`research_seam.py:181-229`):

```json
{"request_id": "REQ-036-01", "run": "<run dir>", "class": "REGISTERED",
 "registered": [{"slug": "...", "path": "...", "source_id": "...", "pre_existing": false}],
 "queued": [{"candidate": "...", "reason": "..."}],
 "negative": null, "limit_reached": null, "reason": "at least one source is registered and citable"}
```

`registered[]` is built only from receipts with outcome `registered`, plus `duplicate` receipts whose candidate was triaged a keeper, marked `pre_existing: true` because the source answers the request even though this run did not write it. `queued[]` draws from both receipts (refused attempts) and the run record (failures the agent logged, because only the agent saw the paywall).

**Invariant, owned by `research_seam.py`:** `registered[]` comes from receipts alone. If the agent believed it found nothing but a receipt exists, the return is `REGISTERED`. The command text says "that is the mechanism working, not a bug" (`research-acquire.md:106`). The one judgment the agent still makes is the triage distinction: `--candidate --triage rejected` means "I saw it and it is useless" (no human action); `--failure` means "I could not bring it in and someone could" (queues it). Getting that right decides between a negative and a queue.

**Visual cue:** a decision ladder, top to bottom, with the four classes as exits and "receipts" as the only input arrow.

# The registry refuses before it writes, and writes four things or nothing

Step 4 is safe because `register` is a ladder of refusals followed by one atomic commit (`source_registry.py:206-260`, current code). Refusals come back as a `RegistrationResult` with an `outcome`: `precondition_failed` (metadata missing or file absent), `limit_reached` (the run's captures are spent), `holdout_hit` (path or extracted text matches the sealed list), `duplicate` (same raw bytes already registered; returns `existing_slug`), `capture_failed`. Only if none fires does commit run, under one lock, writing together: the source directory `knowledge/sources/<slug>/` with the extracted markdown and its raw copy, one `MANIFEST.jsonl` row, and one `### ` block in `SOURCE_INDEX.md` carrying the three sentences. Staging under `knowledge/.staging/` is removed either way.

The manifest row that commit appends is one JSON line (`source_registry.py:675-685`, current code):

```json
{"source_id": "<raw sha256>", "source_kind": "url | local_pdf", "slug": "<slug>", "title": "...",
 "raw_sha256": "<same as source_id>", "raw_artifact_sha256": "<sha256 of saved copy>",
 "extract_sha256": "<content_hash from extract frontmatter>", "date_extracted": "YYYY-MM-DD"}
```

plus per-kind extras such as the URL or origin path. `source_id` and `raw_sha256` are the same value; the duplicate check compares incoming raw bytes against this column.

**Invariant, owned by the registry:** a source's identity is the SHA-256 of its raw bytes as fetched (fusion-tea ADR-0008). Two sources with the same bytes are one source.

**Dropdown candidate: why the manifest row carries two hashes.** `raw_sha256` is identity (the bytes as fetched). `raw_artifact_sha256` is the integrity of the saved copy, which can differ because the web backend decodes and re-encodes HTML before saving (`extraction/web_backend.py:444` vs `:515`). This is one of four workarounds the registry carries for gaps in `agentic-mbse extract`, filed upstream as `EXTRACT-PROVENANCE-HOOK`.

**Dropdown candidate: the hold-out hook.** fusion-tea's `holdout_guard.py` parses one protocol file (`knowledge/holdout/aries-cs/PROTOCOL.md`) for barred paths and carries a hard-coded list of terms that mark ARIES-CS material; it fails closed if the protocol does not parse, and there is no waiver. The shape is general: a sealed set of sources kept unread so a model can later be validated blind against them. The instance is fusion-tea's. *Intended:* the registry gains a guard interface with a no-op default; a target that runs a hold-out points the guard at its own protocol file.

**Visual cue:** a ladder of five refusal rungs leading to one "commit four artifacts" box, with a side door labelled "hold-out guard (optional)" on the two rungs that call it.

# The goal layer reads the class; it does not define it

Steps 1, 2 and 6 belong to the goal runbook, which lists `research` as one of five native seams, a seam being a boundary where a goal round hands bounded work to another workflow and reads back a typed result: invoke with "question, evidence, source and search limits"; native return is "registered sources, a queued candidate, or a bounded negative"; the goal-level question is "Is the evidence enough?" (`GOAL_RUNBOOK.md` § The native seams, current fusion-tea text). The `run-goal` skill's research section tells the round agent to start from `SOURCE_INDEX.md`, `KNOWLEDGE.md` and prior research, then form `REQ-*.json` files and run or delegate `research-acquire` (`run-goal/SKILL.md:59-63`).

How a class becomes a task outcome is the round agent's reading. The outcome names come from the runbook's task-return table (`GOAL_RUNBOOK.md` § Running one task: `COMPLETE`, `BOUNDED_NEGATIVE`, `PREREQUISITE`, `STRATEGY_BLOCKER`, `OWNER_GATE`, `MECHANICAL_FAILURE`). The runbook does not fix the mapping from seam class to task return; this table is **inference**:

| Seam class | Task return in the trail | Why |
|---|---|---|
| `REGISTERED` | `COMPLETE` | sources citable; a reading task may follow |
| `BOUNDED_NEGATIVE` | `BOUNDED_NEGATIVE` | a real "no"; the negative blocks repeats |
| `OPERATOR_QUEUE` | `OWNER_GATE` | a human fetches or rules on the hold-out hit |
| `BLOCKER` | `PREREQUISITE` naming the seam | the seam needs repair, which is not the round's job |

The runbook does fix one rule that makes this safe: "a goal round still may not silently absorb a seam repair." A task that finds itself fixing the registry instead of calling it returns `PREREQUISITE`.

**Visual cue:** three swimlanes (goal round, acquisition, reading) with one request arrow down into acquisition, `return.json` back up, and a reading arrow that starts only after a `REGISTERED` return.

# The port changes homes and makes two couplings optional; it does not change the pipeline

The epic that wraps the agentic-mbse / fusion-tea split (`.project/backlog/epic_wrap-split.md`) gains a fifth work item for this port. Three owner decisions from 2026-10-06 fix its shape: research is core and ports into agentic-mbse; fusion vocabulary may remain as examples if the text reads as a general rule; nothing removed from either repo is lost, with a migration ledger recording destinations. The table is this synthesis's **inference** about the design, to be settled in that item's spec.

| fusion-tea today | agentic-mbse end state | Why it moves this way |
|---|---|---|
| `scripts/research_seam.py` | `src/agentic_mbse/research/seam.py`, as `agentic-mbse research open \| log \| close` | No fusion coupling beyond the default requests path; sits beside `pm` as a CLI family |
| `scripts/source_registry.py` core | `src/agentic_mbse/research/registry.py`, as `agentic-mbse research register \| retire \| verify` | It already shells out to `agentic-mbse extract`; the dependency points downhill |
| Index and manifest helpers imported from `zotero_ingest.py` / `zotero_lib.py` | Lifted into the registry module; the registry stops importing anything Zotero | The registry needs an index-block writer and manifest readers; those functions were written for fusion-tea's unattended Zotero ingest and reused, so the import is an accident of history, not a dependency on Zotero. *Dropdown candidate:* Zotero is a reference manager; fusion-tea's `zotero_ingest.py` diffs its 1cfe group library against the manifest and ingests new items, and remains one feed into `register` |
| `holdout_guard.py` with ARIES terms and a fixed protocol path | Guard interface, no-op default, target-supplied protocol | The fail-closed check is useful to any project running a blind validation; the term list and protocol path are fusion-tea's and would refuse the wrong sources elsewhere |
| `.claude/commands/research-acquire.md` | `skills/research-acquire/` or a mode of `/research` (Judgment) | The command is the agent's protocol between the two scripts; without it an installed target has the tools but no procedure for using them in order |
| `docs/research_seam_operator_guide.md` | `docs/research-seam.md`, examples relabelled | A human operator forms requests and reads returns too; the guide is the only place that explains the four classes to a person rather than an agent |
| `tests/research/*` minus hold-out-term and Zotero tests | `tests/test_research/` | The return-class and receipt tests pin the mechanism the whole model rests on; the hold-out-term and Zotero tests pin fusion-tea's instance and stay with it |
| `init` directory set | adds `knowledge/research/requests/{runs,negatives}`; gitignores `knowledge/.staging/` | `open` writes the run directory and `close` may write a negative; without these directories a fresh target's first request fails on a missing path |

Stays in fusion-tea: the Zotero ingestion scripts and the 1cfe group ID (a Zotero library is one feed into the registry, not part of it); the ARIES-CS protocol and its term list; every existing request, run, negative and receipt; `register` wrappers under `scripts/` if fusion-tea wants to keep its entry points for a while.

**Visual cue:** a two-column "before / after" with arrows, Zotero and hold-out drawn as plugs on the side of the registry box.

# Judgment

- **Separate command or a mode of `/research`?** Keeping `research-acquire` separate matches fusion-tea's proven shape and keeps the wall visible as two commands. Merging gives one entry point and avoids a third research-named command next to `/research` and `/manage-sources`. I lean separate: the wall is the point, and a merged command invites fetching and interpreting in one breath. Owner decision at spec time.
- **What happens to the other two write paths.** `/manage-sources` hand-edits the index the registry was built to protect; the spec should retire it, reduce it to view and retire, or keep it only for sources that need no capture (a codebase, a person). `extract --save-source` is a general tool and stays. The end-state rule is already what the code enforces: the registry is the one *registered* write path, and `verify` reports a source directory with no manifest row as `orphan_source_dir` (`source_registry.py:791-794`). The spec should state the rule that way and add the index side: an index block with no manifest row is the `/manage-sources` bypass, and `verify` should report it if it does not already.
- **Dependency direction is downhill here**, unlike the study layer. The registry depends on `agentic-mbse extract`, which is agentic-mbse's own. No teax or sysml-codegen import.
- **Absorbing `EXTRACT-PROVENANCE-HOOK` is tempting and should wait.** In-process capture could return provenance directly and delete the flatten step, staged copy, loopback fixture and second hash. Doing it inside the port widens "move and generalize" into "redesign capture." Port with the shell-out intact; fix the hook as the filed item.
- **`gap_type`, `priority` and `consumer` carry fusion-tea's vocabulary.** `consumer` is a work-item or goal-task id; the only `gap_type` seen is `unsourced_value`. The bookkeeper stores `gap_type` without validating it (`research_seam.py:79` copies it through). The spec should either enumerate allowed values or declare them free text.
- **Not re-read:** fusion-tea's design record D1–D14. Decisions known only from docstrings: two index-block profiles with one writer (D6), the stale-staging sweep margin (D7), receipts counted against `max_captures` (D8), negatives (D9), the class mapping (D13). The spec should read the record before restating them.
- **Spot checks for spec time:** count `holdout_guard` call sites in `source_registry.py` (two seen: input path, extracted text) to size the hook; run fusion-tea's `tests/research/` and list which tests import `zotero_lib` or read `PROTOCOL.md`; check whether `verify` reports an index block that has no manifest row.

# Appendix

**Registry maintenance verbs (current fusion-tea code, not needed for the main model).** `retire --slug --reason` removes a source's four artifacts together under the same lock and leaves one line in `knowledge/RETIRED.jsonl`; `verify` checks that every manifest row has its index block and directory and that retired slugs have not reappeared. Both move with the registry.

**Run directory contents (current fusion-tea code).** `knowledge/research/requests/runs/<request_id>/` holds `run.jsonl` (searches, candidates, failures), `run.json` (metadata and request key), `process_log.md` (prose log), `receipts/` (one file per registration attempt), and `return.json` after close. Everything under `requests/` is committed evidence, not scratch; a negative that lives only in one working tree blocks nothing.

**Capture mechanics (current fusion-tea code).** Capture shells out to `agentic-mbse extract` with a 900 s timeout into `knowledge/.staging/<uuid>/`; staging older than four times that bound is swept as stale (D7).

**The four `research-acquire` standing rules (current fusion-tea text, `research-acquire.md:14-21`).** WebFetch is triage only. You do not mint domain insights. You do not write registry files. A hold-out match is never yours to waive.

# Renders

## 2026-10-06 15:48 — 20261006-150340_research-process-end-state_fresh.html
path: .project/mental-alignment-v2/runs/20261006-150340_research-process-end-state_fresh.html
wall clock: 20m 9s (dispatched 15:28:10; final write 15:48:19, after one correction round for a clipped SVG, a label overlap, step numbering, and phone-width overflow)
tokens: 135,064 (initial render) + 222,079 (correction round), as reported by the runtime for the render agent
owner quality: not asked

## 2026-10-08 — 20261006-150340_research-process-end-state_fresh.html (rebuilt)
path: .project/mental-alignment-v2/runs/20261006-150340_research-process-end-state_fresh.html
wall clock: 23m 11s of render-agent time across two dispatches (16m 43s rebuild after the owner rejected the first render; 6m 28s correction round); queue time between dispatches not measured
tokens: 332,829 (rebuild) + 369,353 (correction round), as reported by the runtime for the render agent
owner quality: owner rejected the first render ("WAY TOO MUCH TEXT ... zero understanding of who is doing what ... IT IS SUPPOSED TO BE A COMPRESSION"); not yet asked on the rebuild

## 2026-10-08 — 20261006-150340_research-process-end-state_fresh.html (rebuilt again: call stack)
path: .project/mental-alignment-v2/runs/20261006-150340_research-process-end-state_fresh.html
wall clock: 1m 50s render-agent time for this rebuild (dispatched after the owner's "fix it"); earlier rounds recorded above
tokens: 388,944, as reported by the runtime for the render agent
owner quality: owner rejected the swimlane version ("THE DIAGRAM FUCKING SUCKS ... SHOW ME what the actual call stack would look like"); not yet asked on this version
note: the synthesis's Judgment is superseded by the page for decision 1 (deleted: research-acquire is a skill, not a command-vs-mode choice) and adds the delegated-approval decision
