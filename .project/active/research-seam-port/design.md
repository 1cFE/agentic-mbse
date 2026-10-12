# Design: Port the research acquisition seam, and bring `/manage-sources` under its rules

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-10-12
**Revised:** 2026-10-12, after `design-review.md` (APPROVE WITH CHANGES)
**Branch / base:** `research-seam-port` at `e2b17a6` (spec refresh on `main` `ac5fb1a`)
**Epic:** `WRAP-SPLIT`, Item 5

## Overview

Move fusion-tea's research seam (one prompt, two scripts) into agentic-mbse as a small typed package, a `research` CLI and a `research-acquire` skill, with behaviour unchanged and fusion-tea's data read as it is. Rework `/manage-sources` so every change it makes goes through that CLI.

## Related Artifacts

- Spec: `spec.md` (Approved for design, 2026-10-12). Align record: `briefs/align.md`. Product-lens: `product-lens.md`. Brief: `briefs/design.md`.
- Design page (owner-approved 2026-10-09): `.project/mental-alignment-v2/runs/20261006-150340_research-process-end-state_fresh.html`.
- Required Reading: research `.project/research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md` § 1c; fusion-tea snapshot `.orchestrate-logs/fusion-tea-snapshot/` (fusion-tea `0a833b9f7`): the two scripts, `holdout_guard.py`, `zotero_{ingest,lib}.py`, `research-acquire.md`, operator guide, ADR-0008, `tests/research/`, and the original seam design `.project/completed/20260827_goal-research-seam/design.md` (its D1–D14 are cited below as "seam D*n*").
- Epic: `.project/backlog/epic_wrap-split.md` § Item 5. Ledger: `.project/active/wrap-split-migration-ledger.md`.
- Decision records: agentic-mbse has no `.project/adr/`; no prior decisions apply.

## The Point

A target brings an outside source into `knowledge/` through one checked door, with proof it is there, using only what `agentic-mbse init` installs; and a user managing sources by hand goes through the same door. [OWNER-VERBATIM] 2026-10-06: "yes, we need this capability in agentic-mbse." [OWNER-VERBATIM] 2026-10-09 on `/manage-sources`: "MORE useful as a general skill which allows direct user management while it folows and enforces the rules". [INHERITED: epic, owner no-loss 2026-10-06] fusion-tea switches over with no data migration and no lost instruction. The installed `run-goal` (Item 2) delegates every acquisition to this seam, so without it an installed goal layer points at a procedure no other target has.

## Research Findings

- **The two scripts are already layered.** `research_seam.py` (bookkeeping, `:70-83` request key, `:234-247` class precedence) never imports the registry; they meet only through files in the run directory (`run.json`, `receipts/`). `source_registry.py` is a seven-step ladder (`:232-260`) plus `verify` (`:748-823`), `retire` (`:898-1177`), receipts (`:1180-1240`) and a CLI (`:1246-1346`). The structure ports cleanly; the size is the problem.
- **Couplings to cut** (snapshot `source_registry.py`): `import holdout_guard` (`:44`), the index writer and `EXTRACT_OUTPUT` from `zotero_ingest.py` (`:45`), paths/manifest/slug helpers from `zotero_lib.py` (`:46-52`), `ZoteroSource` (`:127-160`) matched on `zotero_key` (`:416-417`), and `uv run agentic-mbse extract` (`:475-479`).
- **The guard already fits a three-function protocol.** fusion-tea's `holdout_guard.py` exposes `check_input_path(path)`, `scan_terms(text)`, `scan_file(path)` and `Match(rule_id, count, offsets)` (`:44-109`), imports only stdlib, and finds its repo root from `__file__` (`:130-140`). It loads from a file path unchanged.
- **The Zotero batch block needs its group id** (`zotero_ingest.py:297`, `- **Zotero Key**: 5428393:<key>`), so a neutral writer must take the key's display text from the caller.
- **The shipped index differs from fusion-tea's.** Anchor `## How This File Is Used` (`SOURCE_INDEX.md.template:36`) against `## How Sources Are Used` (`zotero_ingest.py:222`). The template also carries three example `###` blocks inside an HTML comment (`:14-32`), which the registry's block parser (`source_registry.py:989-1008`) would read as entries.
- **A fresh target has no `MANIFEST.jsonl`.** The commit rollback truncates it unconditionally (`zotero_lib.py:111-114`, called at `source_registry.py:610`), which raises on a missing file. fusion-tea never hit this; every fresh target would.
- **agentic-mbse side.** `pm` is wired as `register_pm_subcommands(subparsers)` (`cli/pm_cli.py:429`, called at `cli/__init__.py:798-800`), handlers lazy-import operations. `init` builds directories at `cli/__init__.py:496-516` and writes `.gitignore` only when absent (`:392-457`); the append precedent is `_update_gitignore_for_dev_mode` (`:278`). Skills are discovered from `skills/*/SKILL.md` (no installer edit). `extract` checks the web extra up front and prints a multi-line error (`cli/extract_cli.py:205-209`, `extraction/web_backend.py:153-174`); `pymupdf4llm` is a core dependency (`pyproject.toml:28`). There is no `src/agentic_mbse/__main__.py`. Default `pytest` skips `slow` (`pyproject.toml:102`); six ported tests carry that marker.
- **Interim wording to replace:** `skills/run-goal/SKILL.md:66,68` and `project_templates/GOAL_RUNBOOK.md.template:289` (§ The native seams). Other hand-edit instructions for the index: `skills/onboard/SKILL.md:59,63`, `docs/source-index.md` § Command Behavior.

## Core Concept

The seam is three layers with files between them, and the port keeps that shape while giving each layer one home. **The skill** is prose: it tells an agent the three things it decides (queries, triage, three sentences per keeper) and which CLI call records each. **The CLI** is a thin argparse layer that parses flags, prints JSON or text and maps outcomes to exit codes. **The package** `agentic_mbse.research` does everything else, split by what each part owns: where the registry lives and its lock, the manifest, the index file, what a source is, capture, the hold-out hook, the run directory, and then the three ladders (`register`, `retire`, `verify`) and the bookkeeper (`open`, `log`, `close`).

Two ideas make this a port rather than a rewrite. First, every on-disk shape is a contract that fusion-tea's 123 rows, 61 runs and one negative already depend on, so file formats, the request key and the refusal ladder are copied, and golden tests pin them before anything is moved. Second, each fusion-tea coupling becomes a seam the target fills: the hold-out guard is a file the target names in `pyproject.toml`; the Zotero kind becomes a keyed-file kind whose field names the caller supplies; the index anchor accepts both headings. Nothing in the package names a consumer.

`/manage-sources` becomes a hands-on front end to the same CLI. A capturable document goes through `register`; anything else becomes a hand-curated entry through `add-entry`; removal is `retire` or `remove-entry`. All writes happen under the registry lock, so a user and a background registration cannot lose each other's edits, and every addition, hand-curated or registered, passes the same hold-out guard.

## Key Bets

- **B1.** fusion-tea's live registry is fully described by the shapes the two scripts read and write: rows with and without `source_kind`, `zotero_key` rows, its anchor heading, and no `###` heading inside an HTML comment. The O1 baseline (`evidence/o1-baseline.md`) confirms the index part: no `<!--`, two row-less blocks, both baseline orphans. *If false → parity (criterion 4) shows different findings, and the port needs a migration or a compatibility rule.*
- **B2.** A target's hold-out rule can be stated as three checks: an input path, a text, a file. *If false → a target with, say, a domain allow-list cannot express its rule, and the hook protocol must grow.*
- **B3.** Hand-curated entries are few and change rarely (fusion-tea has four), so addressing them by their heading title is enough. *If false → titles collide and `add-entry`/`remove-entry` need stable ids.*
- **B4.** The only remaining unlocked writer of `SOURCE_INDEX.md` is a person in an editor, and that is rare and visible in `git diff`. *If false → agents still hand-edit the index and the lock protects nothing; the skill rule would need enforcement, not prose.*

## Key Decisions

- **D1. Package `src/agentic_mbse/research/`, twelve modules by responsibility (Component Overview), CLI in `cli/research_cli.py`.** *Rejected: the page's `seam.py` + `registry.py` (keeps a 1,350-line file).*
- **D2. Public API is `agentic_mbse.research.__all__`, thirteen names:** `register`, `SourceMetadata`, `UrlSource`, `LocalPdfSource`, `KeyedFileSource`, `RegistrationResult`, `RegistrationError`, `RegistryPaths`, `default_paths`, `load_manifest_rows`, `HoldoutGuard`, `HoldoutMatch`, `load_holdout_guard`. The CLI is the contract for `retire`, `verify` and the seam. *Rejected: exporting every module function (makes internals a contract with fusion-tea).*
- **D3. Hold-out hook = a Python file the target names in `pyproject.toml`, loaded with `importlib.util.spec_from_file_location` and checked for three callables.** *Rejected: entry points (fusion-tea's `scripts/` is not a package); a module name on `sys.path` (the CLI does not put `scripts/` on it).*
- **D4. A guard that is configured but missing, unloadable, incomplete, or raises during a check refuses as `precondition_failed` with a receipt; so does any key in `[tool.agentic-mbse.research]` other than `holdout-guard`, because a misspelled key would otherwise disable the guard silently (review M2, spec-F3).** *Rejected: `holdout_hit` (claims a match that never happened); propagating the exception (today's crash writes no receipt, so the run cannot see it); ignoring unknown keys.*
- **D5. The guard config is read from `<knowledge dir>/../pyproject.toml`, i.e. the registry tree's project root.** *Rejected: the current directory (a test on a temp tree would load the developer's real guard).*
- **D6. `KeyedFileSource` replaces `ZoteroSource`; the caller names the kind, the manifest key field, and the index label and display text.** *Rejected: a generic `external_key` field read with a `zotero_key` alias (an alias in shipped code that names a consumer).*
- **D7. One owner for the writers.** fusion-tea's Zotero ingest registers through `register(KeyedFileSource(...))`; `zotero_lib.py` keeps Zotero API code and Zotero views built on `load_manifest_rows`. *Rejected: two copies of the index and manifest writers.*
- **D8. `RegistryPaths` holds one knowledge directory and derives the eight paths.** Staging and sources then always share a filesystem, which the commit's atomic rename needs. *Rejected: eight free fields (a caller can split them across filesystems).*
- **D9. Index anchor: insert before the first `## How Sources Are Used` or `## How This File Is Used` heading; with neither, append at the end of the file.** *Rejected: seam D5's single anchor or raise (every shipped target refuses every registration); end of `## Primary Sources` (moves fusion-tea's insertion point).*
- **D10. The index parser ignores headings inside `<!-- -->` comments, and a block ends at the first later line that is a `#`/`##`/`###` heading outside a comment or that opens a comment (`<!--` at line start), whichever comes first.** A block therefore never swallows a comment that follows it, so `retire` and `remove-entry` never cut one. *Rejected: parse as before (the template's commented examples would list as sources, and `retire` could cut a block through a comment); ending blocks only at headings (a hand-placed entry above the template's commented examples would take them with it).*
- **D11. Hand-curated writes are `add-entry` (with `--replace`) and `remove-entry`; `sources` lists every entry, labelled.** A hand-curated entry is one whose normalized Location is not under `knowledge/sources/`; these commands refuse any other. `add-entry` and `--replace` run the hold-out guard like `register` (review M1): `check_input_path` on a Location that is not a URL, and `scan_terms` on the title, Location, Use for and Validation. A hit refuses `holdout_hit` with its rule id; a guard fault refuses as D4. *Rejected: the skill editing the file (no lock, no rules); a separate `edit-entry` (`--replace` does it in one locked write); hand-curated writes without the guard (would let a sealed path or title into the index every agent reads).*
- **D12. `verify` adds `block_without_row`: a block whose normalized Location directory is under `knowledge/sources/` with no manifest row and no retirement. It is `legacy` when that directory is in the baseline's `orphan_source_dirs`, `fault` otherwise.** In fusion-tea both such blocks (`iter_cryoplant_iter_org`, `eu_demo_rw_tf_coil_conductor_dematte_bruzzone`) sit in baseline orphan directories, so its `verify` stays at exit 0 (`evidence/o1-baseline.md`). *Rejected: a new baseline list (needs a fusion-tea data change).*
- **D13. Capture runs `[sys.executable, "-m", "agentic_mbse", "extract", …]`, via a new three-line `src/agentic_mbse/__main__.py`.** *Rejected: `uv run agentic-mbse` (requires uv, and `uv run` re-syncs the environment, which reverts the editable install the pre-merge checks rely on).*
- **D14. A URL registration checks the web extra (`check_web_deps()`) just before capture and refuses `precondition_failed` naming `agentic-mbse[web]`.** *Rejected: let `extract` fail (spends a capture, and the receipt's reason is the last line of a multi-line message).*
- **D15. The CLI runs only from the project root (`knowledge/` in the current directory) and keeps paths relative.** *Rejected: resolving the root to absolute paths (writes machine paths into committed `run.json` files).*
- **D16. The seam-class to task-outcome table lives in the runbook's § The native seams; `run-goal` points to it.** *Rejected: the table in `run-goal` (outcomes are defined in the runbook; two homes drift).*
- **D17. ADR-0008 is condensed into `docs/research-seam.md` § Decisions under the snapshot-authority stance; provenance there is by date and record id, and the commit-pinned citation goes in the migration ledger.** *Rejected: `docs/goal-layer-decisions.md` (identity is a seam rule the goal layer only consumes); naming the source repo and path in the guide (criterion 5's grep covers the guide).* This overrides the brief's lean to cite by fusion-tea path; the spec criterion wins.
- **D18. Ported tests live in `tests/test_research/`, built from the index `init` ships and with no manifest file, as a fresh target has.** Assignments: Appendix B. *Rejected: fusion-tea's `MINIMAL_INDEX` fixture (passes while a fresh target fails, product-lens spec-F1(c)).*

## Behaviour Changes

Everything not listed here ports byte for byte: six outcomes, ladder order, four classes and their precedence, one receipt per returned register outcome (none when an error propagates, as today), four-files-or-nothing under one lock, the request key, and the receipt, return, negative, manifest and index-block shapes.

| Change | Reason |
|---|---|
| No guard configured → nothing held out | The hook's default, for targets with no hold-out (the expected kind) |
| Broken or raising guard, or an unknown config key → `precondition_failed` + receipt (was: crash, no receipt). A fault after capture carries the captured `source_id`, and `captured` counts it, so `max_captures` still bounds the run | D4, spec-F3, review A2 |
| Two anchors, then end of file (was: one anchor or raise) | D9 |
| Headings inside HTML comments ignored; a block also ends where a comment opens | D10 |
| `verify` reports `block_without_row` | Spec [INFERRED] requirement |
| URL `register` without the web extra → `precondition_failed` (was: `capture_failed`) | D14 |
| Missing `SOURCE_INDEX.md` → `precondition_failed` before capture (was: a failed commit and `RegistrationError`) | Do not spend a capture on a write that cannot land |
| Class consequence of the three rows above: `close` queues `precondition_failed` unchanged (`research_seam.py:35`), so a broken guard, a missing web extra or a missing index makes the run `OPERATOR_QUEUE` → `OWNER_GATE`. Their reasons start `hold-out guard unavailable:`, `URL capture needs the web extra:` and `source index missing:`; the skill and guide say a queued candidate with such a reason is a seam repair, not a source the owner must obtain | Review A1; `close` stays as it is |
| Rollback removes a manifest that did not exist before the attempt (was: raise) | Fresh targets have no manifest (Research Findings) |
| Extractor started with the running interpreter | D13; same extractor code |
| CLI refuses outside the project root; `RegistrationError`, `RetirementError`, a capture timeout and `SeamError` print one line and exit non-zero (was: traceback). The Python API still raises them, as today | D15; a traceback is not an operator message |
| `ZoteroSource` → `KeyedFileSource`; profile renamed `batch` (in memory only) | D6; rows and blocks fusion-tea writes stay byte-identical |
| Docstrings and messages drop consumer citations | Spec criterion 5 |

## Architecture

```
skill (research-acquire | manage-sources)      prose: what the agent or user decides
  └─ Bash: uv run agentic-mbse research <sub>  cli/research_cli.py: flags, root check, print, exit code
       └─ agentic_mbse.research                package: every rule and every write
            ├─ seam.py      open | log | close  → knowledge/research/requests/{runs,negatives}/
            ├─ register.py  ladder → capture.py → python -m agentic_mbse extract → .staging/<uuid>/
            ├─ retire.py, verify.py, index.py (entries)
            └─ files: sources/, raw/, MANIFEST.jsonl, SOURCE_INDEX.md, RETIRED.jsonl, .registry.lock
```

- **The seam and the registry still meet only through the run directory.** `runs.py` owns its layout (`run.json`, `run.jsonl`, `process_log.md`, `receipts/`, `return.json`): `register` writes receipts and reads `limits`; `close` reads receipts and the run log. Neither imports the other. This replaces the two scripts' duplicate readers and their two names for `run.json`.
- **The register ladder, unchanged in order:** sweep stale staging → metadata → input file → index exists (new) → hold-out on input path, identity, title → pre-fetch dedupe (keyed field, or URL exact then normalized) → `max_captures` → web extra for URLs (new) → capture → hold-out on extract and raw artifact → dedupe on `source_id` → commit (source dir, raw copy, manifest row, index block) under the lock, or roll back. With `--run`, every returned outcome writes one receipt. A raised `RegistrationError` (a commit rung failed and was rolled back) or `subprocess.TimeoutExpired` (capture overran) writes no receipt and propagates, as today (review M5).
- **The hook.** `register`, `retire` and `add_entry` take `guard: HoldoutGuard | None = None`. `None` means `load_holdout_guard(paths.project_root)`: no `[tool.agentic-mbse.research]` table, or that table empty, gives a guard that matches nothing; a `holdout-guard` value that is not a non-empty string, any other key in the table, unreadable TOML, or any load fault gives a guard whose every check raises. Every guard call, and every read of a match it returns, runs inside one wrapper that turns an exception into the D4 refusal. Tests pass a fake guard; fusion-tea's Zotero ingest passes none and so gets its configured guard, as it does today.
- **The index file** has one parser (`index.py`): `###` blocks bounded as D10 says, each with its title, Type, Location and slug. `register`, `retire`, `verify`, `sources`, `add-entry` and `remove-entry` all use it. Every write is a read-modify-write under `registry_lock`.
- **Insertion bytes.** At an anchor, the writer inserts `<block>\n\n` at the start of the anchor's line, which is byte-identical to the snapshot's `replace("\n## How Sources Are Used", "\n<block>\n\n## How Sources Are Used", 1)` (`zotero_ingest.py:276-278`). With no anchor, it appends `<block>\n`, first adding `\n` if the file does not end with one. A block's span runs to where D10 ends it, so right after either insertion the span is exactly the inserted text, and removing it restores the file byte for byte (when the file ended with a newline).
- **Locations and titles.** A Location is normalized before any `knowledge/sources/` test: strip whitespace, drop a leading `./`, and turn an absolute path under the project root into a relative one. Titles match exactly after stripping surrounding whitespace. `remove-entry` and `add-entry --replace` match among hand-curated entries only and refuse when none or more than one matches; `add-entry` without `--replace` refuses a title an existing hand-curated entry has. A registered entry may share a title with a hand-curated one.
- **CLI surface:** `agentic-mbse research open | log | close | register | retire | verify` (flags as the scripts have them), plus `sources`, `add-entry`, `remove-entry`. `register`/`retire` print the scripts' JSON and text; `add-entry`/`remove-entry` print `{"outcome": …, "reason": …}` with outcome `added`, `replaced`, `removed`, `holdout_hit` (plus `rule_id` and `offsets`) or `precondition_failed`, and exit 0 only for the first three. `sources` prints one line per entry: `<registered|hand-curated|unregistered> <type> <title> — <location>`.

### Exact wording

**Hook configuration** (target's `pyproject.toml`; path relative to the project root):

```toml
[tool.agentic-mbse.research]
holdout-guard = "scripts/holdout_guard.py"
```

**The guard protocol** (`holdout.py`; structural, so fusion-tea's module conforms unchanged):

```python
class HoldoutMatch(Protocol):
    @property
    def rule_id(self) -> str: ...      # e.g. "term:<t>" or "path:<glob>"; never the content
    @property
    def count(self) -> int: ...
    @property
    def offsets(self) -> tuple[int, ...]: ...

class HoldoutGuard(Protocol):
    def check_input_path(self, path: Path) -> HoldoutMatch | None: ...
    def scan_terms(self, text: str) -> Sequence[HoldoutMatch]: ...
    def scan_file(self, path: Path) -> Sequence[HoldoutMatch]: ...
```

**The keyed kind** (`sources.py`; fusion-tea builds it as `KeyedFileSource(path, "zotero", "zotero_key", key, "Zotero Key", f"{GROUP_ID}:{key}")`):

```python
@dataclass(frozen=True)
class KeyedFileSource:
    path: Path         # local file to capture; staged like a local PDF
    kind: str          # row `source_kind`; receipt identity is f"{kind}:{key}"
    key_field: str     # row field holding `key`; pre-fetch dedupe matches it
    key: str           # also the slug-collision suffix
    key_label: str     # Extended Metadata label in the batch index block
    key_display: str   # its value
```

`__post_init__` rejects `kind` in `{"url", "local_pdf"}`, a `key_field` the registry itself writes, and a `key` outside `[A-Za-z0-9_]+`, because the key becomes a slug suffix and a path segment that `retire` must accept (review A9).

**`skills/run-goal/SKILL.md:66`** becomes:

> Start with internal sources: `knowledge/SOURCE_INDEX.md` (registered and hand-curated sources), `knowledge/KNOWLEDGE.md` (domain insights), and `knowledge/research/` (prior research). New sources come in only through the installed `research-acquire` skill, which runs `agentic-mbse research open | log | register | close`; reading registered sources is `/research`.

**`skills/run-goal/SKILL.md:68`** becomes:

> When external sources are needed, write one request file per question at `knowledge/research/requests/<request-id>.json` (fields in the `research-acquire` skill) and run the skill on it directly, or delegate independent requests to fresh agents: Claude Code `Agent` with `subagent_type: "general-purpose"`; Codex `spawn_agent` with `fork_turns: "none"`. A delegated brief names the request file, the original evidence, and the return budget; deposit it at `evidence/`. Apply any source-quarantine rule the project states before any fetch. Record the task outcome that the class in the run's `return.json` maps to (`GOAL_RUNBOOK.md` § The native seams). The main agent remains free to use research skills itself.

**`project_templates/GOAL_RUNBOOK.md.template:289`** becomes this bullet and table:

> - **`research`** is the installed `research-acquire` skill and the `agentic-mbse research` CLI it calls; reading what it registers is `/research`. The seam computes one class per request and writes it to `return.json`. The goal layer maps the class to a task outcome and never defines classes:
>
> | Seam class | Task outcome | Next step |
> |---|---|---|
> | `REGISTERED` | `COMPLETE` | Schedule a reading task (`/research`) on the registered paths |
> | `OPERATOR_QUEUE` | `OWNER_GATE` | The owner obtains, or rules on, each queued candidate |
> | `BLOCKER` | `PREREQUISITE` | Repair the seam or the request as its own scoped task |
> | `BOUNDED_NEGATIVE` | `BOUNDED_NEGATIVE` | A real no; cite the negative file |
>
> When `open` refuses there is no `return.json`. A malformed request is `BLOCKER`; a request a recorded negative already answers is `BOUNDED_NEGATIVE`, citing that negative.

**`docs/source-index.md` § Source Types** becomes two tables (mirrored in `skills/source-traceability/SKILL.md:69-76`, which also corrects "Use For" to "Use for"):

> **Hand-curated types.** Added and removed with `/manage-sources` (`agentic-mbse research add-entry`, `remove-entry`). Location is anywhere except `knowledge/sources/`.
>
> | Type | Description | How Commands Use It |
> |---|---|---|
> | `codebase` | Code repository | Launch Explore agents to analyze |
> | `documentation` | PDF, markdown or text files kept outside `knowledge/sources/` | Read/search for relevant sections |
> | `database` | API or database endpoint | Query for data (future) |
> | `reference` | Books, papers, standards that are not captured | Note for citations, don't deep-analyze |
>
> **Registered types.** Written and removed only by `agentic-mbse research register` and `retire`. Location is always `knowledge/sources/<slug>/`, backed by a `MANIFEST.jsonl` row.
>
> | Type | Description | How Commands Use It |
> |---|---|---|
> | `url` | A web page or online PDF, captured with its raw copy and hashes | Read `output.md` under Location; cite the Location; weigh the Caveat |
> | `local_pdf` | A PDF from this machine, captured with its raw copy and hashes | Same as `url` |
>
> A registered entry also carries **Caveat** and an `#### Extended Metadata` block (origin, Source ID, hashes, date). An unattended batch caller registers entries of type `documentation` with empty Use for and Validation; they are registered all the same. `agentic-mbse research sources` lists every entry labelled registered or hand-curated.

## Required Invariants

- **I1.** Golden tests pin bytes, not sets (review A5): the request key of a fixed request (value computed by the snapshot's `research_seam.request_key`); the key *order* of a receipt, a return, a negative, and a `url`, `local_pdf` and keyed manifest row; the exact index bytes after an insertion at each anchor and at the end-of-file fallback, and after a hand-curated `add-entry`; a keyed batch block equal to the snapshot's Zotero block for the same inputs; and a `register` then `retire` round trip that leaves `SOURCE_INDEX.md` and `MANIFEST.jsonl` byte-identical, at each anchor and at the fallback. Each lands in the phase that moves the code it protects, before that code.
- **I2.** With `--run`, every outcome `register` returns writes exactly one receipt, with an outcome among the six. A raised `RegistrationError` or `subprocess.TimeoutExpired` writes none, as today. `retire`, `add-entry` and `remove-entry` refusals write nothing.
- **I3.** After a failed commit or retire rung, `MANIFEST.jsonl`, `SOURCE_INDEX.md` and `RETIRED.jsonl` are byte-identical to before, or absent if they were absent.
- **I4.** A configured guard that cannot be loaded, lacks a function, raises, or sits beside an unknown key never lets a `register`, `retire` or `add-entry` through.
- **I5.** A keyed source matches existing rows on its named field before any fetch; old `zotero_key` rows without `source_kind` match.
- **I6.** In agentic-mbse's shipped code and skills, only `agentic_mbse.research` writes `knowledge/sources/`, `MANIFEST.jsonl`, `RETIRED.jsonl` and `SOURCE_INDEX.md`, every index write holds the registry lock, and no shipped skill instructs a direct edit of those files. (Consumer code is outside this claim: fusion-tea's Zotero ingest downloads into `knowledge/raw/`, and its `re_extract_sources` rewrites `knowledge/sources/<slug>/` in place.)
- **I7.** The class comes only from receipts and the run log. Capture never passes `--index` or `--summarize`.
- **I8.** `grep -iE "fusion-tea|MR-[0-9]|\baries\b|zotero|\.project/"` (spec criterion 5, word-bounded 2026-10-12) over `skills/research-acquire/`, `docs/research-seam.md` and `src/agentic_mbse/research/` returns nothing; a test runs that pattern.

## Component Overview

| Module | Owns |
|---|---|
| `research/__init__.py` | The D2 public API, nothing else |
| `research/paths.py` | `RegistryPaths` (knowledge dir → eight paths, `project_root`), `default_paths()` (cwd-relative `knowledge`), `registry_lock`, the stale-staging sweep |
| `research/manifest.py` | Row loading, append, rollback to a mark (absent-aware), rewrite-without-slug, first-row matching |
| `research/index.py` | The block parser (comment-aware, D10 block ends), insertion anchor rule and bytes, seam/batch/hand-curated block rendering, cut and replace of a block, Location normalization, title matching, entry labels; `add_entry` (guarded), `remove_entry`, `list_entries` |
| `research/sources.py` | `UrlSource`, `LocalPdfSource`, `KeyedFileSource`, `SourceMetadata`, `slugify`, URL normalization |
| `research/capture.py` | The extractor subprocess, flattening, provenance read-off (`source_id`, raw artifact, hashes): the one place that works around extractor gaps |
| `research/holdout.py` | `HoldoutMatch`, `HoldoutGuard`, the no-op and failing guards, `load_holdout_guard`, the fail-closed call wrapper |
| `research/runs.py` | Run-directory layout, receipt write/read, `limits`, run-log append/read |
| `research/register.py` | The ladder, commit and rollback, `RegistrationResult`, `RegistrationError` |
| `research/retire.py` | The retire ladder, references check, `RetirementResult`, `RetirementError` |
| `research/verify.py` | Findings, baseline and retired loading, the new `block_without_row` |
| `research/seam.py` | `SeamHome`, `request_key`, `open_run`, `log_*`, `close`, class precedence, negatives |
| `cli/research_cli.py` | `register_research_subcommands`, root check, output and exit codes |
| `skills/research-acquire/SKILL.md` | The acquisition procedure (workflow kind) |
| `docs/research-seam.md` | Operator guide, hook guide, Decisions (condensed ADR-0008) |

`skills/manage-sources/SKILL.md` keeps its four stages (read state, choose action, act, next steps). Read state is `research sources`. Add asks one question first: can the toolkit capture it (a web page, an online PDF, a PDF on this machine)? Yes → `register` with title and the same three sentences an agent writes. No → `add-entry`, with one of the four hand-curated types, and the existing offer of read access for local paths; a `holdout_hit` refusal is reported with its rule id and not retried. Remove is `retire --slug --reason` for a registered entry and `remove-entry` for a hand-curated one. Edit is `add-entry --replace`, hand-curated only. An `unregistered` entry (Location under `knowledge/sources/`, no row) is drift for the owner to resolve by hand and then check with `verify`; the skill reports it and does not change it (review A7). A new action, "resolve a queued candidate", lists `queued[]` from the latest run of each `request_id` only (newest run directory under `knowledge/research/requests/runs/<request_id>/`). For a candidate the user has since obtained, it registers the copy and reports the new `knowledge/sources/<slug>/` location for whatever waits on the request, as the guide's "Act on a queued source" does; it does not re-run the request (review M3). Hold-out hits are shown, never registered. A reason starting `hold-out guard unavailable:`, `URL capture needs the web extra:` or `source index missing:` is shown as a seam repair, not a source to obtain. The skill states one rule: it never edits `SOURCE_INDEX.md`, `MANIFEST.jsonl`, `RETIRED.jsonl` or `knowledge/sources/`.

`skills/research-acquire/SKILL.md` is fusion-tea's `research-acquire.md` with the shared preface and frontmatter (`kind: workflow`, tools Bash, Read, Grep, Glob, WebSearch, WebFetch). Its snippets call `uv run agentic-mbse research …`; "citable under MR-4" becomes "citable as the source's location (see the source-traceability skill)"; the guide is located with `get_docs_dir()` as the runbook does; it keeps telling the agent to report `BLOCKER` itself when `open` refuses a malformed request (Align). Its outcome table adds one line under `precondition_failed`: a reason naming the hold-out guard, the web extra or the source index is a seam repair; report it, and do not retry or hand it on as a source to obtain (review A1). The guide's "Act on a queued source" says the same to the operator.

## Non-Goals

- Out of scope: Zotero ingest and the ARIES-CS guard, term list and protocol, which stay in fusion-tea.
- Out of scope: `/research`, `pm save-research` and `pm approve-research`, which are unchanged.
- Out of scope: `EXTRACT-PROVENANCE-HOOK`; `capture.py` ports today's workaround as it is.
- Out of scope: reusing a retired slug. Re-registering a retired source under the same title reuses the slug, and `verify` reports `retired_reappeared`, as it does in fusion-tea today; the guide says so.
- Out of scope: editing a registered entry's prose; it is part of the registration record.
- Out of scope: Item 4's hygiene of `docs/source-index.md` examples (the fusion example and its `/home` path).

## Implementation Notes

- **Copy, then split.** Land the golden tests (I1) and the moved behaviour tests against the snapshot's behaviour first, then move code module by module with those tests green. Do not change ladder order or messages while splitting. Port `_spent_a_capture` (`source_registry.py:1235-1240`) exactly, including its quirk that a pre-fetch duplicate of a row carrying a `source_id` counts as captured; the only addition is A2's post-capture guard fault.
- **`retire`'s guard calls keep their argument shapes:** `check_input_path(Path(slug))`, then `check_input_path(Path("knowledge/sources") / slug)` with that literal relative path (not `paths.sources`, which a temp tree changes), then `scan_terms(slug)`, all under the lock and before the slug pattern check (`source_registry.py:932-940`). fusion-tea's guard globs exactly those forms.
- **Rollback tests patch rung functions by name** (`test_rollback.py`, `test_retire.py` `RUNGS`). Keep each rung a module-level function in `register.py`/`retire.py` so the tests can still target them.
- **Comment masking must keep offsets.** Replace comment content with same-length filler for heading search only; spans and block text are cut from the original string, so `index_block_sha256` stays the hash of what the writer wrote.
- **`row_without_block` keeps its raw-text substring check** (`source_registry.py:815`) for parity, even though the new check uses the parser.
- **Test fixtures:** the tree uses the shipped template (`get_template_path()`) and no manifest file; "nothing written" helpers accept absent or empty. Generate the test PDF with `pymupdf` (a core dependency), not matplotlib. Replace `marker.html`'s sealed-paper token with a neutral token the fake guard bars. Keep the six `slow` markers; criterion 3's evidence runs `uv run pytest tests/test_research -m ""`. URL-chain tests need the `web` extra, like the 18 existing ones; do not skip them. Because `default_paths()` is cwd-relative, `tests/test_research/conftest.py` keeps a session check that the suite creates nothing under the repository root's `knowledge/` (no `.staging/`, `.registry.lock`, `MANIFEST.jsonl`, `RETIRED.jsonl` or new `sources/` entry), replacing the dropped `test_hermetic_paths.py` (review A13).
- **Init:** add `knowledge/research/requests/runs` and `…/negatives` to the directory list; add the two ignore lines to the fresh `.gitignore` under `# agentic-mbse research registry (machine-local)`; on every init, append any missing line to an existing regular `.gitignore` under that header, and leave a symlinked one with a message, as `cli/__init__.py:289-291` does. Report it under Updated. Do not touch `installation.py` (Item 3's branch edits it).
- **mypy and ruff:** frozen dataclasses for results; `TypedDict` for the receipt and return shapes; rows stay `dict[str, Any]`. New code adds zero findings over the `ac5fb1a` baseline (ruff 118, mypy 88).
- **Hook loading:** use the standard importlib recipe: build the spec from the resolved absolute path, insert the module into `sys.modules` under a private name before `exec_module` (a guard using dataclasses with postponed annotations needs it), and remove it if loading fails (review A3). Its `__file__`-based root then works. A guard that imports a sibling module fails to load. The hook guide says a guard must import on its own, and that its own relative paths resolve against the current directory, which the CLI fixes to the project root (D15); Python callers must run from there too. Import `check_web_deps` lazily inside the URL check; `web_backend` imports only the standard library at module level.
- **The guide keeps the operator guide's request and registration examples** (the Nb3Sn request, the EPFL preprint), labelled as examples. None contains a criterion-5 term, and keeping them needs no ledger row.

## Potential Risks

- **The new parser reads fusion-tea's index differently.** Largely retired by the O1 baseline: the index has no `<!--`, and exactly two blocks point into `knowledge/sources/` without a row, both in baseline orphan directories (`evidence/o1-baseline.md`). Location normalization (A6) could still surface a `./` or absolute form; run O1's `verify` comparison as soon as `verify.py` lands, not at the end.
- **The dry-run source refuses non-browser fetches.** O2 pre-checks the URL with `agentic-mbse extract --save-source` before the agent run, with a named fallback.
- **Command/skill name clash in fusion-tea.** Its local `/research-acquire` command and the installed skill share a name once it re-inits. The fusion-tea branch deletes the command in the same change that moves the pin and re-inits (O3).
- **Codex web tools.** The skill names WebSearch/WebFetch, as `/research` does; the Codex adapter maps tool names. No new risk, but O2 runs Claude only.
- **Effort overrun** (Next-Stage Handoff).

## Integration Strategy

- Installs like every skill: `skills/research-acquire/` is found by the source-tree inventory, so `init` and `install-commands --list` pick it up with no installer edit. `docs/research-seam.md` ships in the wheel's docs.
- `run-goal` and the runbook name the skill and CLI (exact text above). `/research` is untouched and still the reading stage.
- `onboard` (`:59,63`) adds listed sources through the `/manage-sources` procedure instead of writing the index. `toolkit-awareness` gains one `uv run agentic-mbse research <sub>` line and one skill-table row. `docs/source-index.md` § Command Behavior says `init` creates a missing index and that sources are added through `/manage-sources`. The template's type comment, placeholder line and "Adding New Sources" section say the same for new targets.
- fusion-tea switches after the owner merges this branch (Appendix A, D): its Zotero ingest imports the package, its guard is named in `pyproject.toml`, its scripts and local command are deleted, and every removed consumer line has a ledger row (Appendix C).

## Validation Approach

| Spec criterion | Evidence |
|---|---|
| 1. Install, list, directories, ignore lines | `tests/test_cli.py` and new init tests: fresh init, re-init on an existing `.gitignore`, symlinked `.gitignore`; `install-commands --list` names `research-acquire` |
| 2. End to end in a fresh target | O2a dry run from a built wheel |
| 3. Ported tests | `uv run pytest tests/test_research -m ""`: four classes, six outcomes through a fake guard, `retire`, `verify`, plus hook fail-closed cases, anchors, comments, entries, golden shapes |
| 4. Parity on fusion-tea data | O1: `verify` finding lines and exit codes, duplicate URL, duplicate `zotero_key`, negative refusal, guard wiring |
| 5. No consumer names | I8 test |
| 6. fusion-tea after the port | O1 branch: scripts deleted, Zotero and research suites pass on the editable install; ledger destinations exist on the branch |
| 7. `/manage-sources` by hand | O2b dry run |
| 8. run-goal relabel and mapping | Contract test: `run-goal` names `research-acquire` and `agentic-mbse research`, not the interim sentence; the runbook table has the four classes |
| 9. Suite, ruff, mypy | `uv run pytest tests/`, `uv run ruff check src/ tests/`, `uv run mypy src/` against the baseline counts |

## Next-Stage Handoff

- **Fixed:** D1–D18, the public API, the behaviour-change table, the exact texts above, the test assignments (Appendix B) and the file list (Appendix A).
- **Open to the plan:** function names inside modules, CLI help strings, the guide's prose, the skills' prose within the shapes above.
- **De-risk first:** byte-level golden tests and the rollback-without-manifest fix (I1, I3); then the hook's fail-closed paths, including the unknown-key case (I4); then run O1's `verify` comparison as soon as `verify.py` lands.
- **Phases** (each one implement session; review A10): P1 support modules (`paths`, `manifest`, `sources`, `runs`, the `index` writer and parser) plus `src/agentic_mbse/__main__.py` and their golden tests. P2 `capture` and the `register` ladder with the no-op guard, plus the moved chain, duplicate, receipt, rollback and staging tests. P3 the hook and its tests. P4 hand-curated entries and `sources`, `retire`, `verify`, and the register-then-retire round trips. P5 `seam`, the CLI, init. P6 skills, docs, templates, contract tests. Orchestrator: O1 fusion-tea branch and parity (step 1 already done), O2 dry runs, O3 post-merge runbook. Stage subagents cannot reach fusion-tea, a scratch target or `claude -p`; O1–O3 are orchestrator-run.
- **Effort.** Epic estimate 2.5 days, execute 14h. Re-estimate for execution: P1 3h, P2 3h, P3 2h, P4 3.5h, P5 3h, P6 4h, O1 1.5h, O2 1.5h, O3 (owner-paced) 0.5h, about 22h, so about 3.5 days in total. Overrun about 8h. Causes: restructuring into a typed, lint-clean package instead of copying two files (brief priority 2); the `/manage-sources` CLI surface, now with the guard and the matching rules the review added; and the fusion-tea branch plus two dry runs, which the 14h did not count.

## Appendix A — File-level changes

**agentic-mbse, new:** `src/agentic_mbse/__main__.py`; `src/agentic_mbse/research/{__init__,paths,manifest,index,sources,capture,holdout,runs,register,retire,verify,seam}.py`; `src/agentic_mbse/cli/research_cli.py`; `skills/research-acquire/SKILL.md`; `docs/research-seam.md`; `tests/test_research/` (Appendix B).

**agentic-mbse, changed:** `src/agentic_mbse/cli/__init__.py` (wire `register_research_subcommands` beside `pm`; two directories; `.gitignore` lines and append helper; `cmd_init` docstring) · `skills/manage-sources/SKILL.md` (rewrite to the shape above) · `skills/run-goal/SKILL.md:66,68` · `project_templates/GOAL_RUNBOOK.md.template:289` · `skills/source-traceability/SKILL.md:55-76` · `docs/source-index.md` (File Format shows both entry shapes; Source Types; Command Behavior steps 1 and 4) · `SOURCE_INDEX.md.template` (type comment names registered types; placeholder line becomes a comment saying entries are added at the end of the section; "Adding New Sources" points at `/manage-sources` and the CLI) · `skills/onboard/SKILL.md:59,63` · `skills/toolkit-awareness/SKILL.md` · `tests/test_cli.py` (directory list) · `.project/active/wrap-split-migration-ledger.md` (Item 5 section).

**agentic-mbse, unchanged:** `cli/installation.py`, `pyproject.toml` (no new dependency or extra), `scripts/replicate_setup.sh`.

**fusion-tea branch `research-seam-port`, own worktree, orchestrator-run:**
- Delete `scripts/research_seam.py`, `scripts/source_registry.py`, `.claude/commands/research-acquire.md`, `docs/research_seam_operator_guide.md`; `.gitignore:20` (`!.claude/commands/research-acquire.md`). Lines 35-36 stay.
- `pyproject.toml`: add the hook table above.
- `scripts/zotero_ingest.py`: import `register`, `RegistrationError`, `SourceMetadata`, `LocalPdfSource`, `KeyedFileSource` from `agentic_mbse.research`; `process_zotero_item` builds the keyed source; delete `append_source_index_entry`, `SEAM_ANCHOR`, both block builders and `resolve_slug` (no caller outside this file, orchestrator-verified); keep its own `EXTRACT_OUTPUT` for re-extraction; the `ZoteroSource` rationale (unattended batch, no per-item prose) moves to `process_zotero_item`'s docstring.
- `scripts/zotero_lib.py`: delete `RegistryPaths`, `default_paths`, `load_manifest_rows`, `truncate_manifest`, `append_manifest_entry` and `slugify` (no caller outside this file; the `slugify` in `exploration/` scripts is their own definition), and the path constants only those used, after a grep for each constant; keep `RAW_DIR`, `SOURCES_DIR` and `GROUP_ID`, which Zotero code uses; rebuild `load_manifest`/`manifest_keys` on `agentic_mbse.research.load_manifest_rows(default_paths())`.
- `scripts/zotero_group_download.py` and `scripts/test_zotero_write_access.py` stay unchanged: they import only Zotero API names that stay (orchestrator-verified). O1 import-checks both after the change.
- Historical records keep their references to the deleted files, because git history holds them: `modeling_project/VALIDATION_MATRIX.md:63` (SV-037 evidence), `work/active/WI-045_primary-loop-and-cycle/spec.md:99`, and goal-trail evidence and briefs under `work/orchestration/goals/`. The only live instruction references are `CLAUDE.md:11` (rewritten) and the deleted guide; no `AGENTS.md` hit.
- `CLAUDE.md:11` becomes: "**Research:** the installed `research-acquire` skill drives search and triage; `uv run agentic-mbse research open|log|register|close` keeps the run and writes the registry, and `retire`/`verify` maintain it. Form request files at `knowledge/research/requests/REQ-*.json`. Operator guide: `docs/research-seam.md` in the installed toolkit's docs directory. The ARIES-CS guard `scripts/holdout_guard.py` is the registry's hold-out hook (`pyproject.toml` `[tool.agentic-mbse.research]`); a hit is adjudicated only through PROTOCOL §6, outside the seam, and the guard is a term scan that misses barred content which never names a barred term. Every researcher applies the clean-room screen (`knowledge/holdout/aries-cs/PROTOCOL.md`) before any fetch. Zotero ingest registers through the same package. Registered locations are cited under MR-4."
- `.project/adr/0008-*.md`: a dated amendment line saying the invariants it lists are now held by the installed `agentic_mbse.research`.
- `tests/research/`: per Appendix B.

## Appendix B — Test assignments (fusion-tea `tests/research/`, 20 files)

| File | Assignment |
|---|---|
| `__init__.py` | Move |
| `conftest.py` | Split. agentic-mbse: shipped-template tree with no manifest, `local_site`, pymupdf `generated_pdf`, `run_dir`, `FakeGuard`. fusion-tea: a trimmed tree fixture that uses `monkeypatch.chdir(tmp_path)` (the package's `default_paths()` is cwd-relative and holds no constants to patch), plus `generated_pdf` |
| `test_command_contract.py` | Move, rewritten for `skills/research-acquire/SKILL.md` and `docs/research-seam.md`; the `.gitignore` negation test is dropped with the command; the upstream-filings test becomes a check that the guide names the capture gaps |
| `test_duplicate.py`, `test_negative.py`, `test_return_contract.py`, `test_triage_queue.py`, `test_register_url_chain.py`, `test_register_pdf_chain.py`, `test_staging_concurrency.py`, `test_rollback.py` | Move; imports and rung names updated; `zotero_key` absence assertions read "no key field"; rollback gains the no-manifest case |
| `test_receipts.py` | Move; the pre-capture refusal uses the fake guard's term |
| `test_holdout.py` | Split. Moves with the fake guard (content, URL, title, input path, no waiver flag) plus new: no config → registers; missing file, missing function, raising guard, unknown config key → `precondition_failed` with a receipt; a post-capture fault counts as captured. fusion-tea keeps `test_holdout_wiring.py` (new): `load_holdout_guard(repo root)` loads its guard; on a temp tree, a sealed-stem URL and a barred local-PDF input path refuse through `register`, and a barred slug refuses through `retire` |
| `test_retire.py` | Move with the fake guard barring a path and a term; a recording fake guard asserts `retire` passes `Path(slug)`, then the literal `knowledge/sources/<slug>`, then the slug to `scan_terms` |
| `test_verify.py` | Move, plus `block_without_row`, hand-curated entries not reported, commented blocks ignored |
| `test_index_writer.py` | Move, rewritten: both anchors, end-of-file fallback (replaces "missing anchor raises"), comment masking, keyed batch block |
| `test_zotero_path_contract.py` | Split. Batch-block field order and values, and keyed dedupe, move with a neutral key. `test_load_manifest_rows_returns_every_row` and `test_truncate_manifest_restores_recorded_byte_length` move to the package's manifest tests. `load_manifest`/`manifest_keys` tolerance stays in fusion-tea as `test_zotero_manifest_views.py`. Tests of `append_manifest_entry` go with that writer |
| `test_zotero_paths_are_callers.py` | Stays; imports updated |
| `test_holdout_guard_parse.py` | Stays unchanged (ARIES protocol parser) |
| `test_hermetic_paths.py` | Not moved: the package has no path constants to redirect; the conftest session check (Implementation Notes) replaces it. fusion-tea deletes it with its constant patching |

New in agentic-mbse: `test_golden_shapes.py` (I1); `test_entries.py` (`sources` labels; `add-entry`, `--replace` and `remove-entry` refusals for duplicate, missing and ambiguous titles, a normalized `./knowledge/sources/…` Location, and guard hits and faults; and removing a hand-placed entry above the template's commented examples, which leaves the examples and the placeholder line byte for byte, review A4); `test_research_cli.py` (root check, exit codes, one-line errors); `test_hook_config.py`; init tests in `tests/test_cli.py`; and the shipped-text contract tests for `manage-sources`, `run-goal`, the runbook table and I8.

## Appendix C — Ledger rows (Item 5 section)

| Text removed from the ported copy | Was in (fusion-tea `0a833b9f7`) | fusion-tea home | Evidence |
|---|---|---|---|
| "citable under MR-4" | `research-acquire.md:93`; guide `:38` | `CLAUDE.md` § Traceability (exists) and the new `:11` | O1 branch diff |
| Script paths and `uv run python scripts/…` snippets | command `:9-10,28-103`; guide passim | `CLAUDE.md:11` (new text) | O1 branch diff |
| Hold-out route via PROTOCOL §6 | guide `:191-193`, `:274` | `CLAUDE.md:11` (new); `holdout_guard.py:9-10` (exists) | O1 branch diff |
| The term list as the blind spot (ARIES-CS, host, four stems) | guide `:247-251` | `holdout_guard.py:26-35` (exists); `CLAUDE.md:11` (new) | O1 branch diff |
| `--local-pdf` breaking change of `zotero_ingest.py` | guide `:30-32` | `zotero_ingest.py` `process_local_pdf` docstring (exists) | snapshot `:567-573` |
| "Three legacy entries" and the WI-031 sources | guide `:239` | `knowledge/.registry_baseline.json` (exists) | O1 `verify` output |
| Design-record and requirement pointers: the design record's D1–D14, T-010 R1–R5, the guide's `R-D5`/`R-D6` (`:144`), and the scripts' inline `R-*`, `audit F*` and `WI-033` ids | script docstrings `research_seam.py:13`, `source_registry.py:23-24` and inline comments; guide `:144` | The completed seam spec and design records (`.project/completed/20260827_goal-research-seam/`, exist); fusion-tea git history of the deleted scripts | at `0a833b9f7` |
| `ZoteroSource` and its rationale | `source_registry.py:127-160` | `zotero_ingest.py` `process_zotero_item` (O1) | O1 branch diff |
| ADR-0008's Zotero-specific wording | `.project/adr/0008-*.md` | Stays live; amendment line (O1). Shipped condensation in `docs/research-seam.md` § Decisions is a 2026-10-12 snapshot of record 0008 at `0a833b9f7` | O1 branch diff |
| Upstream filings section | guide `:282-287` | Not needed in fusion-tea: both items are agentic-mbse backlog entries. The shipped guide drops the `PM-APPROVE-RESEARCH-EMPTY-INSIGHTS` bullet (closed) and describes the open capture gaps in words | agentic-mbse `.project/backlog/BACKLOG.md:735` |

## Appendix D — Orchestrator runbooks

**O1, fusion-tea branch and parity** (worktree `/home/reid/1cfe/fusion-tea-research-seam`, branch `research-seam-port` from fusion-tea `c42ed1d8a`, whose seam files equal the snapshot's; this branch installed with `uv pip install --reinstall --no-deps -e <worktree>`; commands with `uv run --no-sync`).
1. **Baseline, done** (`evidence/o1-baseline.md`): the old `verify` exits 0 with three `legacy` findings; the index has no `<!--`; exactly two blocks point into `knowledge/sources/` with no row, `iter_cryoplant_iter_org/` and `eu_demo_rw_tf_coil_conductor_dematte_bruzzone/`, both in `orphan_source_dirs`.
2. **Add the hook table** to fusion-tea's `pyproject.toml` first (review M4), so every later check runs with the guard configured.
3. **Parity**, with the scripts still present: `uv run --no-sync python scripts/source_registry.py verify > old.txt; echo $?` and `uv run --no-sync agentic-mbse research verify > new.txt; echo $?`. Compare finding lines only, not the summary line. Pass: every finding line of `old.txt` is in `new.txt`; the only extra lines are two `legacy block_without_row` lines, for `knowledge/sources/iter_cryoplant_iter_org` and `knowledge/sources/eu_demo_rw_tf_coil_conductor_dematte_bruzzone`; both commands exit 0. fusion-tea's `verify` therefore stays at exit 0, and nothing that gates on it changes (review A14).
4. **Duplicates and the guard**, each refusing before any fetch and writing nothing: `agentic-mbse research register --url <source_url of an existing url row> …` → `duplicate`; in Python, `register(KeyedFileSource(<any existing raw PDF>, "zotero", "zotero_key", <existing key>, "Zotero Key", "x"), SourceMetadata(title="x"))` → `duplicate`; `agentic-mbse research open <the request the negative answers>` → exit 3; `register --url https://example.org/mirror/08-FST-Lyon.pdf …` → `holdout_hit` with a `term:` rule id. `git status` shows only the `pyproject.toml` change afterwards.
5. **The rest of Appendix A.** Before deleting, re-grep for each deleted `zotero_lib` constant. After, import-check `scripts/zotero_group_download.py` and `scripts/test_zotero_write_access.py`; run `pytest tests/research` and the Zotero tests; confirm each Appendix C home is in the branch diff or exists at `0a833b9f7`.

**O2, dry runs** (scratch target outside any repo; a minimal uv project with the built wheel and its `web` extra, and `[tool.uv] extra-index-url` set to the GitLab index in agentic-mbse's `pyproject.toml` so `syside==0.8.4` resolves (review A17); `uv run agentic-mbse init . < /dev/null`; `claude -p --setting-sources project,local`).
- **O2a, criterion 2.** Request `REQ-001-01`: question "What is the density of aluminium alloy 6061?", consumer `WI-001`, gap type `unsourced_value`, priority `P2`, where to look `["en.wikipedia.org/wiki/6061_aluminium_alloy"]`, limits `{"max_searches": 2, "max_captures": 1}`. Pre-check the page with `agentic-mbse extract <url> --save-source --output /tmp/precheck --budget 0`; if it fails, use another open-access page with a stated density and note the swap. Prompt: "Follow the research-acquire skill on knowledge/research/requests/REQ-001-01.json." Pass: `return.json` class `REGISTERED`; source directory, manifest row, index block and a receipt exist; `agentic-mbse research verify` exits 0.
- **O2b, criterion 7.** Place a one-page PDF at `docs/widget_note.pdf` and create `/tmp/ref-code/`. Five `claude -p` calls, each starting `/manage-sources` and carrying every detail so nothing needs asking: (1) add `docs/widget_note.pdf`, title "Widget Note", with use-for, validation and caveat sentences; (2) add the codebase at `/tmp/ref-code`, title "Reference Code", type codebase, validation N/A; (3) list sources; (4) remove "Widget Note", reason "dry-run cleanup"; (5) remove "Reference Code". After each, check with the CLI: (1) registered, with a manifest row and hashes; (2) hand-curated block; (3) both labelled correctly; (4) a `RETIRED.jsonl` line and `verify` exits 0; (5) the block is gone. Also confirm `SOURCE_INDEX.md` changed only through those calls.

**O3, post-merge** (owner merges agentic-mbse first). On the fusion-tea branch: set the pin `rev` to the merged SHA in `pyproject.toml`; replace the SHA in `uv.lock` by hand (re-locking fails under uv 0.10); `uv sync --frozen --extra e2e`; `uv pip install --no-deps syside-license==0.3.6`; update the SHA in `tests/test_dependency_provenance.py`; `uv run --no-sync agentic-mbse init . < /dev/null` (installs the skill; the two ignore lines already exist); run the research, Zotero and provenance suites; commit; the owner merges.

---

**Revised** 2026-10-12 after `design-review.md` (APPROVE WITH CHANGES): M1–M5 and advisories A1–A18 applied; see the review's Resolutions.

**Next step:** `/_my_plan`. No decision records are filed at acceptance: this repo has no `.project/adr/` and no `adr.sh`, so D1–D18 live here.
