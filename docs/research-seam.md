# Research Seam Guide

This is the seam between "we need to know X" and "the repository now contains evidence about X."

Research runs in two stages with a wall between them. **Acquisition**, this guide's subject, proves a source is in the repository. **Reading** (`/research`, `pm save-research`, `pm approve-research`) reasons only from sources already in, and it is where domain insights are made.

The pieces:

- **`agentic-mbse research register` and `retire`** are the only way a source enters or leaves `knowledge/sources/`. Give `register` a URL or a PDF and three sentences about it. It captures the source, asks the project's hold-out hook, and commits a source directory, a manifest row and an index block together, or leaves the repository untouched. `verify` reports where the registry disagrees with itself.
- **`agentic-mbse research open`, `log` and `close`** keep the books for one research invocation. They validate the request, refuse to re-search something already answered, keep the record, and compute the outcome from what actually landed on disk.
- **`agentic-mbse research sources`, `add-entry` and `remove-entry`** list the source index and manage the entries for sources that cannot be captured.
- **The `research-acquire` skill** drives search and triage between `open` and `close`. **The `manage-sources` skill** is the front end for a person curating sources by hand.

Every subcommand runs from the project root, the directory holding `knowledge/`, and keeps the paths it prints and records relative to it. Run anywhere else, it exits 1 with one line starting `Error:`. An error the registry raises, such as a commit step that failed and was rolled back, prints the same way.

You can use the registry on its own. You do not need a request, a run or the skill to register a source you already have.

---

## Registering a source, on its own

The values below are an example:

```bash
uv run agentic-mbse research register \
    --url https://example.org/paper \
    --title "Preliminary Design of a High Current R&W TF Coil Conductor" \
    --use-for "EU DEMO Nb3Sn winding-pack geometry and current; serves RQ-1." \
    --validation "Check the 104.95 kA figure against Fig. 1 on page 2." \
    --caveat "Conference preprint, open-access on EPFL infoscience; not the journal version."
```

Or `--local-pdf path/to/file.pdf` instead of `--url`. A URL needs the web extra, `agentic-mbse[web]`.

The three prose flags are required and there is no default for them. An index entry that cannot say what a source is for, how to check its numbers, and what limits its authority is not worth writing, so the operation refuses rather than writing a blank one.

`--title` is required as well, and is not derived from anything. The slug and the index heading are built from it, and a filename-derived guess would put a wrong name on a permanent registry entry.

No text written into the index block may contain `<!--`: the title, the three prose flags, the URL or the local path. In the index it would open an HTML comment that hides every later entry from the registry, so `register` refuses it as `precondition_failed` before any capture.

It prints JSON. `outcome` is one of:

| outcome | meaning |
|---|---|
| `registered` | Committed. `location` is a repository path, cited as the source's location (see the source-traceability skill). |
| `duplicate` | Already in the registry. `existing_slug` and `existing_path` name it. |
| `holdout_hit` | The project's hold-out hook matched. Nothing was written. `rule_id` names the rule. |
| `capture_failed` | The extractor could not produce a usable extraction. |
| `precondition_failed` | Required metadata missing, a field holding `<!--`, the input file is not there, or the seam itself needs repair (below). |
| `limit_reached` | Only with `--run`: this run has spent its capture budget. |

Exit code is 0 only for `registered`.

**Three refusals mean the seam needs repair, not the source.** Each is `precondition_failed`, with a reason that starts:

- `hold-out guard unavailable:` when the project names a hold-out guard that cannot answer (see The hold-out hook).
- `URL capture needs the web extra:` when a URL is given and `agentic-mbse[web]` is not installed.
- `source index missing:` when `knowledge/SOURCE_INDEX.md` does not exist. `agentic-mbse init` creates it.

### What gets written

A registration commits four things or none:

1. `knowledge/sources/<slug>/`: the extraction, flattened
2. `knowledge/raw/<file>`: the raw artifact, for a PDF input
3. one row in `knowledge/MANIFEST.jsonl`
4. one block in `knowledge/SOURCE_INDEX.md`, just before its `## How Sources Are Used` or `## How This File Is Used` heading, or at the end of the file when it has neither

The capture is staged in `knowledge/.staging/`, and the commit runs under `knowledge/.registry.lock`, the lock every registry write takes. `init` keeps both out of git. If any step fails, all of them are undone: the manifest and the index come back byte-identical, or absent if they were absent.

### The two hashes

Every entry records two SHA-256 values, and they do different jobs.

- **`Raw SHA256`** (also `Source ID`) is the digest of the source **as fetched**. It is the identity: what duplicate detection compares, and what you would compare a re-fetch against.
- **`Raw Artifact SHA256`** is the digest of the artifact **as stored** in the repository. It is the integrity check you can recompute yourself with `sha256sum`.

They are the same number for a plain UTF-8 page or a PDF. They differ for a page served in another encoding, because the extractor writes `raw.html` re-encoded as UTF-8. Do not expect one to verify the other.

### Trying it without the network

The URL path can be exercised offline by serving a page from your own machine. Do it in a scratch project (a directory where `agentic-mbse init` has run), so the entry does not land in a real registry. Put any article-like HTML page in a folder; the extractor drops a page it reads as boilerplate, so give it a few paragraphs of text.

```bash
python3 -m http.server 8799 --directory <folder> &
uv run agentic-mbse research register \
    --url http://127.0.0.1:8799/<page>.html \
    --title "Widget Coil Note" \
    --use-for "Checking the seam works before I trust it." \
    --validation "Compare against the page itself." \
    --caveat "A test page. It states nothing about any real machine."
kill %1
```

That runs the real extractor, the real hold-out hook and the real commit: everything but the live fetch.

`agentic-mbse extract` rejects `file://` URLs, so a local file is not a substitute for the loopback server here.

---

## Forming a request

A request is a JSON file at `knowledge/research/requests/<request-id>.json`. An example:

```json
{
  "request_id": "REQ-031-01",
  "question": "What is the winding-pack current density for a Nb3Sn TF coil?",
  "consumer": "WI-031",
  "gap_type": "unsourced_value",
  "priority": "P1",
  "where_to_look": ["EPFL infoscience", "IEEE Trans. Appl. Supercond."],
  "limits": {"max_searches": 4, "max_captures": 2}
}
```

Every field except `limits` is required, and `open` refuses without them. The `research-acquire` skill describes each field.

`consumer` is who is waiting: a work item, a study finding as `<study-id>#<n>`, a model element, or a spec reference. It is part of what makes the request distinct.

`request_id` names the run's directory, `knowledge/research/requests/runs/<request_id>/<timestamp>/`.

**What makes two requests the same request.** The key is a hash of `question`, `consumer`, `gap_type` and `where_to_look`, with the list sorted, so naming the same places in a different order does not change it. `priority` and `limits` are deliberately outside it: raising a limit is looking harder for the same thing, not asking something new. Change the question and you have a new request with a new key, and any prior negative no longer applies.

---

## Running an invocation

Normally the `research-acquire` skill drives this. By hand:

```bash
RUN=$(uv run agentic-mbse research open knowledge/research/requests/REQ-031-01.json | tail -1)

uv run agentic-mbse research log "$RUN" --search "nb3sn winding pack current density"

# --triage takes exactly keeper or rejected.
uv run agentic-mbse research log "$RUN" --candidate https://example.org/a --triage keeper --note "has the table"
uv run agentic-mbse research log "$RUN" --candidate https://example.org/c --triage rejected --note "off topic"

# A candidate you could not bring in. This queues it for a person by default.
uv run agentic-mbse research log "$RUN" --failure https://example.org/b --reason "paywalled"

# ... unless you say nobody should chase it, which records it in the negative instead.
uv run agentic-mbse research log "$RUN" --failure https://example.org/gone \
    --reason "404, link is dead" --disposition closed

uv run agentic-mbse research register --url https://example.org/a \
    --title "..." --use-for "..." --validation "..." --caveat "..." --run "$RUN"

uv run agentic-mbse research close "$RUN" --adequacy exhausted
```

`--adequacy` says why the search was enough: `exhausted` (the default) or `limit_reached`. It matters only when the run comes back `BOUNDED_NEGATIVE`, where it is recorded in the negative. It changes neither the class nor `return.json`. When a declared limit did stop the search, `close` records `limit_reached` in the negative whatever the flag says.

`close` writes `return.json` in the run directory and prints it. The run directory also holds `run.json` (the request's identity and limits), `run.jsonl` and `process_log.md` (the log, for code and for people), and `receipts/` (one per `register --run` attempt).

`open` exits 2 on a request it cannot use, and 3 on one a recorded negative already answers.

### Commit the run directory with the work

Everything under `knowledge/research/requests/` is **committed evidence**, not scratch: the requests, the bounded negatives, the run records, the receipts and the returns. Commit them alongside whatever the round produced.

That is what makes a negative durable. A negative that lives only in one working tree answers nobody: a fresh clone would not have it, the next operator would re-run the same fruitless search, and a goal round could not cite the return it routes on.

The receipts matter for the same reason. They are the evidence behind the class in `return.json`; without them the return is an assertion rather than a record.

**Where the return comes from.** Two places, each authoritative over what only it can know.

`register --run` drops a receipt for every attempt, and `registered[]` is built from those receipts alone. If the agent reported finding nothing but a source was registered, the return says `REGISTERED`. What landed on disk is the truth of what was registered, and nothing in the log can change it.

`queued[]` comes from both the receipts and the run record, because a candidate can be blocked in two different places. A registration that was refused (a hold-out hit, a capture failure) leaves a receipt. A candidate blocked at triage never reaches `register` at all: only the agent saw the paywall, so `log --failure` is the only record of it. Both end up in `queued[]`, in the same shape.

**A queued candidate means no bounded negative is written.** A negative exists to stop a *fruitless* search being repeated. A request with a named source somebody can still get is not fruitless, so it stays searchable while a person works the queue.

---

## The four return classes

| class | means | what you do |
|---|---|---|
| `REGISTERED` | At least one source is in the repository and citable. | Nothing. Read `registered[]` for the paths. Check `queued[]`: a run can register one source and queue another. |
| `BOUNDED_NEGATIVE` | The search ran and found nothing usable. | Read the negative file named in the return. This is an answer, not a failure. |
| `OPERATOR_QUEUE` | A named candidate is blocked on something only a person can resolve. | See Act on a queued source. |
| `BLOCKER` | The invocation could not get far enough to say anything about any candidate. | Fix what `reason` names and re-run. |

`close` computes `BLOCKER` when the agent recorded a fault with `log --fault` after `open`, nothing was queued, and nothing reached `register`. For example, the agent's session had no web search tool. A malformed request never gets that far: `open` refuses it with exit 2 and creates no run directory, so there is no `return.json`, and the agent reports `BLOCKER` itself.

The line between the last two: **the queue is about a source, the blocker is about the seam.** If a candidate is named and the obstacle is that candidate's accessibility or admissibility, it is a queue. If nothing about the search was established at all, it is a blocker.

One case reads as a queue but is about the seam. A seam-repair refusal (see Registering a source) leaves a receipt like any refused registration, so `close` queues its candidate and the run comes back `OPERATOR_QUEUE`. There is no source to obtain; see Act on a queued source.

An entry in `registered[]` carries `pre_existing: true` when the source was already in the registry and this run found it again. The request is still answered; the flag records that this run did not write it.

`limit_reached` names which declared limit stopped the search, or is null. `close` computes it from the record, not from `--adequacy`. It is `max_captures` only when a `register --run` was refused `limit_reached`, so a run that spent its last capture on a registration and tried no more reads null. It is `max_searches` when the logged searches reached that limit.

A goal round maps each class to a task outcome. The table is in the goal runbook, `GOAL_RUNBOOK.md` § The native seams.

---

## Act on a queued source

Read `queued[]` in the return. Each entry names a candidate and a reason. Entries arrive from two places and read the same: a registration the seam refused, and a candidate the agent recorded with `log --failure` before there was anything to register.

**Paywall or login wall.** Get the PDF through whatever access you have, then register it directly, or through `/manage-sources`, which makes the same call:

```bash
uv run agentic-mbse research register --local-pdf ~/Downloads/paper.pdf \
    --title "..." --use-for "..." --validation "..." --caveat "..."
```

Then tell whatever is waiting on the request where the source now is: `knowledge/sources/<slug>/`, from the printed `location`. The request does not need to run again.

**Repeated fetch failure.** Check the URL by hand. If the site is simply down, re-run the request later. If it moved, fix `where_to_look` in the request and re-run it.

**Extraction too poor to register.** Look at the run's `process_log.md`, then at the extraction the seam threw away. It is gone, so re-run the extractor by hand into a scratch directory if you want to see it. If the source is worth having, get a better copy (the publisher's PDF rather than a landing page) and register that.

**Hold-out hit.** The reason reads `<rule id> matched <n>x`, and the rule id is the guard's own, such as `term:<t>` or `path:<glob>`. Nothing was written and nothing is recoverable from the seam. That is by design, so barred content cannot reach a repository artifact through a log line.

There is no flag that admits it anyway, and there will not be one. If the project's hold-out rule has an exception process, that is the route, and it runs outside this seam.

**A seam repair.** A reason starting `hold-out guard unavailable:`, `URL capture needs the web extra:` or `source index missing:` names something wrong with the seam, not with the candidate. There is nothing to obtain. Repair what it names, then re-run the request; a queued run filed no negative, so `open` needs no override.

---

## Act on a bounded negative

The return names a file under `knowledge/research/requests/negatives/<request-key>.json`. It records the queries that were run, every candidate seen with its triage decision, every failure with its reason, and why the search was considered adequate: `exhausted` or `limit_reached`.

Three things you can do with it:

**Accept it.** The value is not available from the sources we can reach. Record that in whatever is waiting on it, and cite the negative file.

**Re-open it, deliberately.** Something changed: a new paper, a new mirror, a corrected question. Re-run `open` with `--override-reason "<what changed>"`. The reason is appended to the negative's `reopened[]` along with the new run, so the history stays.

```bash
uv run agentic-mbse research open knowledge/research/requests/REQ-031-01.json --override-reason "new preprint, 2026-08"
```

**Change the request.** If the question itself was wrong, edit it. That produces a different request key, and the old negative no longer applies to it.

A negative never expires on a clock. It is keyed on the request, and a changed premise is a changed request.

---

## Read a `verify` report

```bash
uv run agentic-mbse research verify
```

It checks that every source directory has one manifest row and one index block, and the reverse. It writes nothing, ever.

Each line is `<class> <kind> <path> — <detail>`, and the report ends with the number of faults and legacy entries.

| kind | means |
|---|---|
| `orphan_source_dir` | A source directory with no manifest row. |
| `row_without_block` | A manifest row with no index block. |
| `block_without_row` | An index block whose Location is under `knowledge/sources/`, with no manifest row. Usually an entry written by hand. |
| `unresolvable_path` | A manifest row whose source directory is gone. |
| `loose_file` | Something in `knowledge/sources/` that is not a source directory. |
| `retired_reappeared` | An artifact of a retired slug is back: its row, a block whose Location names it, or its directory. |

Hand-curated entries, whose Location is anywhere but `knowledge/sources/`, are not findings. Neither is anything inside an HTML comment in the index.

The class is what matters:

- **`legacy`**: drift recorded in `knowledge/.registry_baseline.json` as predating the registry. Expected, not repaired by this tooling, and not a sign of anything wrong now. The file lists `orphan_source_dirs` and `loose_files` as paths like `knowledge/sources/<slug>`. A project with no baseline file expects no legacy drift, so every finding there is a fault.
- **`fault`**: real drift. Exit code is 1 when any fault is present.

A fault means one of two things. Either something wrote into `knowledge/` outside the registry (find it and stop it), or a registration was killed mid-commit, in the narrow window inside the commit lock. Neither is repaired automatically. Decide what the right state is and fix it deliberately.

---

## What this does not protect you from

**The hold-out check is only as good as the project's guard.** With no guard configured, nothing is held out. A guard written as a term scan matches a fixed list, so a source that carries barred content but never spells a barred term registers cleanly.

The path check does not cover for this. A registration mints a new slug, so a destination path never matches a barred path. The input-path check's real job is narrower and still worth having: refusing a barred file handed in as a `--local-pdf` input.

So: **read what you register.** The scan catches the obvious case. Judgement is still yours.

**Extraction quality is not scored.** A cookie wall over a hundred characters "extracts" fine. The triaging agent is supposed to notice and queue it. Check the `output.md` of anything you rely on.

**A changed source is refused, not superseded.** Re-registering a URL whose bytes have changed comes back `duplicate`, naming the existing entry. There is no supersession path.

**A retired title comes back under its old slug.** Registering a source under a retired source's title reuses the retired slug, and `verify` then reports `retired_reappeared` as a fault. Give the new registration a different title.

---

## Retiring a source

```bash
uv run agentic-mbse research retire --slug <slug> --reason "<why>"
```

It is the one removal door, the counterpart of `register`. Under the same lock it removes exactly one entry's four artifacts together, or removes nothing: the manifest row, the `SOURCE_INDEX.md` block, `knowledge/sources/<slug>/`, and the `knowledge/raw/` copy when the row records one (local PDFs; a URL source keeps its `raw.html` inside its directory). A failure at any step puts everything back byte for byte.

**What it leaves.** One line appended to `knowledge/RETIRED.jsonl`: `slug`, `retired_at` (UTC), `reason` verbatim, `index_block_sha256` (the removed block as the writer wrote it, heading through last metadata line), and the removed manifest row verbatim under `row`. The command prints the row, the block, the paths and the line, so the removal is in your terminal as well as on disk.

**When it refuses.** Non-zero exit, nothing written:

| outcome | means |
|---|---|
| `unknown_slug` | No manifest row carries that slug. |
| `holdout_hit` | The slug names a barred path or term. It is the same hook `register` asks, on the slug as a path, on `knowledge/sources/<slug>`, and on the slug as text. |
| `referenced` | Another entry mentions the slug, in a manifest field or in its index block. One exception: a line saying the other entry **supersedes** the retiree is the announcement that it was replaced, and retiring it completes that announcement, so it does not block. Any other mention does. |
| `precondition_failed` | A blank reason, a slug that is not a registry slug, a hold-out guard that cannot answer, or drift: no block, two blocks, or no directory for the slug. Run `verify` first. |

**What `verify` does with it.** A retired slug is expected absent: its absence is no finding. If any of its artifacts comes back, `verify` reports `retired_reappeared` as a fault. A superseding entry's caveat still naming the retired path is prose, not reappearance.

---

## Hand-curated entries

Some sources cannot be captured: a codebase, a database, a book, a person, a document kept elsewhere in the repository. They stay in the source index as hand-curated entries, with one of four types (`codebase`, `documentation`, `database`, `reference`; see `source-index.md` in this directory) and a Location anywhere except `knowledge/sources/`. The values below are an example:

```bash
uv run agentic-mbse research sources
uv run agentic-mbse research add-entry --title "Reference Code" --type codebase \
    --location /srv/reference/widget-model \
    --use-for "Cross-checking widget sizing formulas" --validation "N/A"
uv run agentic-mbse research add-entry --replace --title "Reference Code" --type codebase \
    --location /srv/reference/widget-model \
    --use-for "Cross-checking widget sizing formulas" \
    --validation "Compare model outputs against its sizing routine"
uv run agentic-mbse research remove-entry --title "Reference Code"
```

- `sources` prints one line per entry, `<label> <type> <title> — <location>`. The label is `registered`, `hand-curated`, or `unregistered`: a Location under `knowledge/sources/` with no manifest row, which `verify` reports as `block_without_row`.
- `add-entry` writes the entry where `register` writes its block, under the same lock. It asks the hold-out hook first, like `register` does. It refuses a title another hand-curated entry already has.
- `add-entry --replace` rewrites the one hand-curated entry with that title, and `remove-entry` removes it. Titles match exactly, after trimming surrounding spaces.
- Each prints `{"outcome": …, "reason": …}`. The outcome is `added`, `replaced` or `removed`, which exit 0, or a refusal: `holdout_hit` (with `rule_id` and `offsets`) or `precondition_failed`. A refusal writes nothing.

These commands touch hand-curated entries only. A registered entry is removed with `retire`, and its prose is part of the registration record.

---

## The hold-out hook

Some projects hold material out of the repository: a sealed paper, a validation set kept blind, data under a use restriction. The registry asks the project's hook before it takes anything in. With no hook configured, nothing is held out.

**Configure it** in the project's `pyproject.toml`, with the guard's path relative to the project root:

```toml
[tool.agentic-mbse.research]
holdout-guard = "scripts/holdout_guard.py"
```

The table's only key is `holdout-guard`. Any other key is a fault, because a misspelled key would otherwise switch the guard off without a word. The table's name is checked the same way: `[tool.agentic-mbse]` holds only `research` and `execution-target` (validation's setting), so any other key there (a misspelled `[tool.agentic-mbse.reseach]`, say) is a fault, and so is a `[tool.agentic_mbse]` table. The guard never reads `execution-target`'s value, so a bad value there is validation's error, not the guard's.

**Write the guard** as a Python file with three functions:

- `check_input_path(path)` returns a match or `None`: is this input path barred?
- `scan_terms(text)` returns a list of matches: does this text name something barred?
- `scan_file(path)` returns a list of matches: does this file?

A match has three attributes. `rule_id` is a string naming the rule, and never the content that fired it, such as `term:<t>` or `path:<glob>`. `count` is an integer. `offsets` are the integer positions where the rule fired. An example guard that bars one term and two path patterns:

```python
"""Hold-out guard: bars sealed widget material from the source registry."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path

BARRED_TERMS = ("sealed-widget-report",)
BARRED_PATHS = ("knowledge/sealed/*", "*/sealed/*")


@dataclass(frozen=True)
class Match:
    rule_id: str
    count: int
    offsets: tuple[int, ...]


def check_input_path(path: Path) -> Match | None:
    for pattern in BARRED_PATHS:
        if fnmatch.fnmatch(path.as_posix(), pattern):
            return Match(f"path:{pattern}", 1, ())
    return None


def scan_terms(text: str) -> list[Match]:
    folded = text.lower()
    matches = []
    for term in BARRED_TERMS:
        offsets = tuple(found.start() for found in re.finditer(re.escape(term), folded))
        if offsets:
            matches.append(Match(f"term:{term}", len(offsets), offsets))
    return matches


def scan_file(path: Path) -> list[Match]:
    return scan_terms(path.read_text(encoding="utf-8", errors="replace"))
```

**What it is asked.**

- `register`: `check_input_path` on a local input file; `scan_terms` on the input's identity (the URL, the local path, or a keyed source's `kind:key`) and on the title; after capture, `scan_file` on the extraction and on the raw artifact.
- `retire`: `check_input_path` on the slug and on `knowledge/sources/<slug>`, then `scan_terms` on the slug.
- `add-entry`, with or without `--replace`: `check_input_path` on a Location that is not a URL, then `scan_terms` on the title, Location, Use for and Validation.

A match refuses as `holdout_hit` with the rule id, and nothing in the seam can waive it.

**How it loads.** The file is loaded by its path, as a module of its own, on every registry call, so an edit takes effect on the next call. It must import on its own: the standard library and installed packages only. A guard that imports a sibling file from its own directory fails to load. Paths the guard opens itself resolve against the current directory, which the CLI always holds at the project root; a Python caller must run from the project root too.

**It fails closed.** If the guard cannot answer, nothing it would check gets through. Each of these faults refuses every `register`, `retire` and `add-entry` as `precondition_failed`, with a reason that starts `hold-out guard unavailable:` and names the fault:

- `pyproject.toml` cannot be read, or `[tool]`, `[tool.agentic-mbse]` or `[tool.agentic-mbse.research]` is not a table
- a key other than `research` or `execution-target` in `[tool.agentic-mbse]`, or a `[tool.agentic_mbse]` table
- a key other than `holdout-guard` in the research table, or a value that is not a non-empty path
- no file at the path, or a file that is not a Python module
- the file raises while loading, or lacks one of the three functions
- a check raises, or answers in the wrong shape: a scan that is not a list, or a match without a `rule_id`, an integer `count` or integer `offsets`

With `--run`, the refusal leaves a receipt, so the run sees it, and `close` queues it as a seam repair. A fault after capture counts against the run's `max_captures`, like the capture it spent.

---

## Using the registry from Python

`agentic_mbse.research` exports the registration API for a program that registers sources in bulk, such as an ingest from an outside catalogue: `register`, `SourceMetadata`, `UrlSource`, `LocalPdfSource`, `KeyedFileSource`, `RegistrationResult`, `RegistrationError`, `RegistryPaths`, `default_paths`, `load_manifest_rows`, `HoldoutGuard`, `HoldoutMatch` and `load_holdout_guard`. Everything else goes through the CLI.

A `KeyedFileSource` is a local file that an outside catalogue identifies by a key. The caller names its kind, the manifest field that holds the key, and how the key reads in the index block. The values below are an example:

```python
from pathlib import Path

from agentic_mbse.research import KeyedFileSource, SourceMetadata, register

source = KeyedFileSource(
    path=Path("downloads/ABCD1234.pdf"),
    kind="catalog",
    key_field="catalog_key",
    key="ABCD1234",
    key_label="Catalog Key",
    key_display="lab-library:ABCD1234",
)
result = register(source, SourceMetadata(title="Widget Handbook, 3rd edition"))
```

- A key already in the manifest's `key_field` comes back `duplicate` before any capture, including rows written before the registry recorded a `source_kind`.
- A keyed entry is written with type `documentation` and empty Use for and Validation, since a batch run has no per-item prose to give. It is registered all the same.
- `register` returns every outcome. It raises `RegistrationError` when a commit step failed and the registry was put back, and `subprocess.TimeoutExpired` when capture overran.
- `paths` defaults to the project in the current directory, and `guard` to the hook its `pyproject.toml` names.

---

## Known capture gaps

`register` captures with `agentic-mbse extract --save-source`, at budget 0 by default. `register --budget <usd>` passes another value to `extract`; above 0, the PDF pipeline may call Claude to improve tables and pages, spending up to that amount. The `research-acquire` skill never passes it. `register` never passes `--index` or `--summarize`, which start a model session, because the seam is run by an agent. The extractor does not yet hand back provenance in the shape the registry needs, so the capture step works around four gaps:

- The PDF pipeline writes nested output, which the registry flattens into `knowledge/sources/<slug>/`.
- `--save-source` writes no `raw.pdf` for a local PDF, so the registry keeps a copy of the input in `knowledge/raw/` itself.
- `file://` URLs are rejected, so a local HTML page needs the loopback server shown above.
- `raw.html` is written re-encoded as UTF-8, not as the bytes fetched. The source id is therefore read from the extraction's `content_hash_sha256` field, and a page can carry two different hashes.

---

## Decisions

This section is the authority for installed targets. It condenses, on 2026-10-12, the decision record of the project that first ran the seam; that project's live record governs that project only. A later change to the source record reaches targets only through an ordinary change to this file.

### A source's durable identity is the SHA-256 of its raw bytes as fetched

**Grade:** `[AGENT]`, delegated by that project's owner. Decided 2026-08-25 as its decision record 0008.

**Decision.** Every registered source carries `source_id`, the SHA-256 of the raw source bytes **as fetched**, taken from the extraction's `content_hash_sha256` field, and a separate `raw_artifact_sha256`, the digest of the raw artifact **as stored** in the repository. The two are different bytes by construction for any non-UTF-8 page, because the extractor re-encodes `raw.html`, and they are never compared to each other. Dedupe order: the caller's key field, for a keyed source; then `source_id`; then `source_url`, exact and then with scheme and host lowercased and the fragment dropped, before any fetch. A key field appears only on its own kind's rows.

**Why.** A registry keyed only on an outside catalogue's key gives a source that never passed through the catalogue (a URL capture, a hand-supplied PDF) no durable identity: duplicates cannot be detected and provenance cannot be re-verified. Identity from the extractor's hash of the fetched bytes makes duplicate detection and re-fetch verification the same check, with no service call and no manual step, so the whole registration can be proven offline. The stored artifact's digest gives any later reader an integrity check they can recompute from the repository alone. A single hash was the first proposal; measured on a non-UTF-8 page, the frontmatter hash and the `raw.html` digest differed, and the split is what survived that measurement.

**Invariants.** The manifest row schema: `source_id`, `source_kind`, `source_url` or `origin_path`, `raw_sha256`, `raw_artifact_sha256`, `extract_sha256`. Manifest readers tolerate rows without a key field (`load_manifest_rows`). The index block's extended metadata carries `Source ID`, `Raw SHA256` and `Raw Artifact SHA256`. Duplicates are detected before a second entry is written. A re-fetch whose bytes changed is refused as a duplicate rather than superseded. The identity hash is trusted from the extractor; the stored artifact's digest is the only hash a reader recomputes.

**Rejected.** A URL-derived key: it gives no identity to a local PDF, and it breaks on redirects and mirrors. Routing every source through an outside catalogue first: it puts a network and credential step into a path that must be provable offline.
