---
name: research-acquire
description: Answer one research request by finding sources and registering them into knowledge/, ending in one computed return class
allowed-tools: [Bash, Read, Grep, Glob, WebSearch, WebFetch]
user-invocable: true
metadata:
  kind: workflow
---

Before executing this skill, read `.agentic-mbse/claude.md` in Claude Code or `.agentic-mbse/codex.md` in Codex. Resolve supporting paths from this skill’s installed directory; keep generated outputs in the project or a temporary directory. Read referenced skills from `.agents/skills/<name>/SKILL.md` when their guidance is needed.


# Research Acquire

**Purpose:** ACQUIRE sources — answer one bounded research request by finding sources, bringing them into the repository with proof they are there, and returning exactly one of four classes.
**Input:** A request file, `knowledge/research/requests/<request-id>.json`
**Output:** `return.json` in the run directory, plus whatever was registered

Research has two stages with a wall between them. This skill is acquisition: it proves a source is in the repository. Reading is `/research`: it reasons only from sources already in, and it is where domain insights (DI-XXX) are made.

You decide three things: the search queries, keeper or rejected for each candidate, and three sentences about each keeper. The `agentic-mbse research` CLI does everything else. It keeps the run's record, captures and checks each source, writes the registry, and computes the return class from what landed on disk.

The operator guide covers forming a request, reading the four classes and acting on what comes back. It is `research-seam.md` in the installed toolkit's docs directory (`uv run python -c 'from agentic_mbse.cli import get_docs_dir; print(get_docs_dir())'`).

When invoked without a request file, ask which request to run and wait.

## Skills Referenced

- **source-traceability**: how a registered source's location is cited.

## Standing Rules

These hold for the whole invocation.

1. **WebFetch is for triage only.** Its output is a lossy summary. It tells you whether a page is reachable and whether it looks relevant. Never quote it, cite it or paste it into a research document, and never register it. The only thing that becomes a source is what `agentic-mbse research register` captured.
2. **You do not mint domain insights.** Registering a source is not approving an insight. Insights are made only through `/research` and the owner's approval. If this round found something that should become one, say so in your report and stop there.
3. **You do not write registry files.** Not the source index, not the manifest, nothing under `knowledge/sources/`. If you find yourself wanting to, the CLI refused something, and the right move is to report it, not to route around it.
4. **A hold-out match is never yours to waive.** `register` returns `holdout_hit` with a rule id, and the candidate is queued for the operator. There is no flag that admits it, and asking for one is out of scope. The hook sees only what reaches `register`, so apply any quarantine rule the project's instructions state before you search or fetch.

Every `agentic-mbse research` call runs from the project root, the directory holding `knowledge/`. Anywhere else it exits 1 with one line starting `Error:`.

## The Request

One JSON file per question, at `knowledge/research/requests/<request-id>.json`. An example:

```json
{
  "request_id": "REQ-012-01",
  "question": "What is the density of aluminium alloy 6061 at room temperature?",
  "consumer": "WI-012",
  "gap_type": "unsourced_value",
  "priority": "P2",
  "where_to_look": ["en.wikipedia.org/wiki/6061_aluminium_alloy", "material data sheets"],
  "limits": {"max_searches": 3, "max_captures": 1}
}
```

Every field except `limits` is required, and `open` refuses a request without them.

- `request_id` names the run directories, so keep it to letters, digits and dashes.
- `question` is the value or fact sought.
- `consumer` is who is waiting: a work item, a study finding (`<study-id>#<n>`), a model element, or a spec reference.
- `gap_type` says what kind of gap the answer fills, such as `unsourced_value`.
- `priority` is the waiting work's priority.
- `where_to_look` lists the places to try first.
- `limits` caps the run: `max_searches` counts the queries you log, and `max_captures` counts the captures `register` spends.

Two requests with the same `question`, `consumer`, `gap_type` and `where_to_look` are the same request, in whatever order `where_to_look` lists its places. That is how a recorded bounded negative is found again.

## Process

### 1. Open the run

```bash
uv run agentic-mbse research open knowledge/research/requests/<request-id>.json
```

It prints a message, then the run directory on its last line. Keep the directory: every later step takes it.

**Exit 3:** a bounded negative already answers this request. Read the negative file it names and report what it says. Do not search again. If the premise has genuinely changed (a new paper, a corrected question), re-run `open` with `--override-reason "<what changed>"`, which is recorded on the negative.

**Exit 2:** the request is malformed, and `open` says what is wrong. No run directory exists, so `close` cannot compute a class. Report `BLOCKER` yourself, naming what is wrong, and stop.

### 2. Search

Work from the request's `where_to_look` first, then broaden. Respect `limits.max_searches`.

Record each query:

```bash
uv run agentic-mbse research log <run-dir> --search "<query>"
```

If you cannot search at all, for example because this session has no web search tool, record why and go to step 5. A run with a logged fault, nothing queued and no registration attempt comes back `BLOCKER`.

```bash
uv run agentic-mbse research log <run-dir> --fault "<what stopped the search>"
```

### 3. Triage

For each candidate, use WebFetch to judge reachability and relevance only (rule 1). Decide keeper or rejected, and record it:

```bash
uv run agentic-mbse research log <run-dir> --candidate <url> --triage keeper --note "<why>"
uv run agentic-mbse research log <run-dir> --candidate <url> --triage rejected --note "<why not>"
uv run agentic-mbse research log <run-dir> --failure <url> --reason "paywalled"
```

`--triage` takes exactly `keeper` or `rejected`.

The difference between a rejection and a failure decides the return class, so get it right:

- **`--candidate … --triage rejected`**: you saw it and it is not useful. Off topic, superseded, no numbers. Nothing for a person to do.
- **`--failure`**: you could not bring it in, and somebody could: paywalled, behind a login wall, repeatedly unreachable. This queues the candidate for the operator, and it stops the run filing a bounded negative over a source a person can still get. That is the default, and it is the right default.
- **`--failure … --disposition closed`**: you could not bring it in and nobody should try, such as a dead link. It is recorded in the negative, not routed to a person.

A keeper is a source you can say three things about, because registration requires all three:

- **Use for**: what it establishes, in numbers where possible, and which question it serves
- **Validation**: how a later reader checks those numbers against the source
- **Caveat**: what limits its authority, such as a preprint, a vendor page or a superseded edition

If you cannot write those three sentences, it is not a keeper yet. Look at the source more closely first.

### 4. Capture and register

One call per keeper:

```bash
uv run agentic-mbse research register \
    --url <url> \
    --title "<title>" \
    --use-for "<what it establishes>" \
    --validation "<how to check it>" \
    --caveat "<what limits it>" \
    --run <run-dir>
```

Use `--local-pdf <path>` instead of `--url` for a file already on disk. `--run` receipts the attempt and counts it against `limits.max_captures`.

It prints JSON, and exits 0 only for `registered`. Read the `outcome`:

| Outcome | What to do |
|---|---|
| `registered` | Done. The `location` is citable as the source's location (see the **source-traceability** skill). |
| `duplicate` | The source is already registered under `existing_slug`. Use it; do not try again. |
| `holdout_hit` | Stop on that candidate. It is queued for the operator, rule id and all. |
| `capture_failed` | Try once more if the reason looks transient. Otherwise it is already receipted and queued for the operator; move on. |
| `precondition_failed` | You left out metadata, or named a file that is not there. Fix and retry. |
| `precondition_failed`, reason starting `hold-out guard unavailable:`, `URL capture needs the web extra:` or `source index missing:` | The seam needs repair, not the source. Report the reason; do not retry, and do not hand the candidate on as a source to obtain. |
| `limit_reached` | The run has spent its captures. Go to step 5. |

If `register` prints one `Error:` line instead of JSON, nothing was registered and no receipt was written. Report the line.

### 5. Close

```bash
uv run agentic-mbse research close <run-dir> --adequacy exhausted
```

Use `--adequacy limit_reached` if you stopped because of a declared limit rather than because you ran out of places to look.

`close` computes the class; you do not declare it. `registered` comes from the receipts alone, so if you believed the search found nothing but a source was registered, the return says `REGISTERED`. That is the mechanism working. `queued` comes from the receipts and from your `log --failure` entries, because a paywall is something only you saw.

### 6. Report

State the class. For each registered source, give its repository path. Point at the run directory. If the class is `BOUNDED_NEGATIVE`, point at the negative file. If anything was queued, name each candidate and its reason, and say which reasons are seam repairs.

Everything under `knowledge/research/requests/` is committed evidence, not scratch: the request, the run record, the receipts, `return.json` and any bounded negative. Commit the run directory with the work it serves. A negative that lives only in one working tree does not stop the next search, and a return nobody can read is not a return.

Then hand off. A research document written from these sources goes through `/research` and its approval, like any other. That is where insights are made.

## The Four Return Classes

| Class | Means |
|---|---|
| `REGISTERED` | At least one source is in the repository and citable. Queued candidates ride inside the return. |
| `BOUNDED_NEGATIVE` | The search ran and found nothing usable. This is an answer, and it is recorded so nobody repeats it. |
| `OPERATOR_QUEUE` | A named candidate is blocked on something a person must resolve. |
| `BLOCKER` | The invocation could not get far enough to say anything about any candidate. |

A goal round maps the class to a task outcome (`GOAL_RUNBOOK.md` § The native seams).

---

**Related Commands:** To read registered sources → `/research` | To manage sources by hand → `/manage-sources`
