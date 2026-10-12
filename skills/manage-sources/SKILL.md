---
name: manage-sources
description: Add, remove, edit or review the project's sources by hand, through the source registry's rules
allowed-tools: [Read, Grep, Glob, Bash, Agent, Write, Edit, AskUserQuestion]
user-invocable: true
metadata:
  kind: workflow
---

Before executing this skill, read `.agentic-mbse/claude.md` in Claude Code or `.agentic-mbse/codex.md` in Codex. Resolve supporting paths from this skill’s installed directory; keep generated outputs in the project or a temporary directory. Read referenced skills from `.agents/skills/<name>/SKILL.md` when their guidance is needed.


# Manage Sources Command

**Purpose:** Manage SOURCES by hand — add, remove, edit or review the authority sources that MBSE commands use for domain knowledge, with every change made through the source registry so its rules hold.
**Input:** None (interactive)
**Output:** Sources registered, retired or curated through `agentic-mbse research` (and optionally native read-access settings)

`knowledge/SOURCE_INDEX.md` lists the project's authority sources. Commands like `/research`, `/design-model` and `/audit-models` read it to discover what domain knowledge is available. It holds two kinds of entry:

- **Registered** sources were captured into `knowledge/sources/<slug>/` with a raw copy, hashes and a manifest row. `agentic-mbse research register` adds them and `retire` removes them.
- **Hand-curated** entries point at sources that cannot be captured: a codebase, a database, a book, a document kept elsewhere. `agentic-mbse research add-entry` and `remove-entry` manage them.

This skill lets the user manage both by hand. The CLI enforces the rules: one lock for every write, the project's hold-out check, duplicate detection, and a record of every retirement. **This skill never edits `SOURCE_INDEX.md`, `MANIFEST.jsonl`, `RETIRED.jsonl` or anything under `knowledge/sources/`.** Every change goes through an `agentic-mbse research` call. If a call refuses, report the refusal; do not route around it.

Run every call from the project root, the directory holding `knowledge/`. When invoked, begin by reading the current state.

## Skills Referenced

- **source-traceability**: the source types, the entry fields and citation patterns. Consult it for what each type means and what a good Use for and Validation look like.

## Process

### 1. Read Current State

```bash
uv run agentic-mbse research sources
```

It prints one line per entry: `<label> <type> <title> — <location>`, where the label is `registered`, `hand-curated` or `unregistered`.

**If it reports the source index missing:** offer two options via the host question interface: run `/onboard` for full project setup (recommended for new projects), or run `agentic-mbse init` to create the index.

**Otherwise:** report the number of entries of each label with a brief listing, and ask what the user wants to do.

An `unregistered` entry has a Location under `knowledge/sources/` but no manifest row. It is drift: an entry written by hand, or a registration that was cut short. Report it, and do not change it. The owner resolves it by hand, then checks the registry with `verify`:

```bash
uv run agentic-mbse research verify
```

### 2. Determine Action

Use the host question interface with options: Add a source, Remove a source, Edit a hand-curated entry, Resolve a queued candidate, View source details.

### 3. Execute Action

#### Add a Source

Ask one question first: **can the toolkit capture it?** It can capture a web page, an online PDF, or a PDF on this machine.

**Yes: register it.** Gather a title and the same three sentences a research agent writes for a keeper:

1. **Title**: the name the index heading and the slug are built from
2. **Use for**: what it establishes, in numbers where possible, and which question it serves
3. **Validation**: how a later reader checks those numbers against the source
4. **Caveat**: what limits its authority, such as a preprint, a vendor page or a superseded edition

```bash
uv run agentic-mbse research register --url <url> \
    --title "<title>" --use-for "<use for>" --validation "<validation>" --caveat "<caveat>"
```

Use `--local-pdf <path>` instead of `--url` for a PDF on this machine. A URL needs the web extra, `agentic-mbse[web]`.

It prints JSON. On `registered`, report the `location`. On `duplicate`, the source is already registered under `existing_slug`; report that and stop. On `holdout_hit`, report the rule id; the source is barred, and there is no retry. On any other refusal, report its `reason`. A reason starting `hold-out guard unavailable:`, `URL capture needs the web extra:` or `source index missing:` means the toolkit needs repair, not the source.

**No: add a hand-curated entry.** Gather:

1. **Type**: one of `codebase`, `documentation`, `database`, `reference` (see the **source-traceability** skill)
2. **Title**: what to call this source
3. **Location**: file path or URL, anywhere except `knowledge/sources/`
4. **Use for**: what domain knowledge it provides
5. **Validation**: how to verify model outputs against it, or `N/A`

Check a local path with `ls -la <location>`. Warn but don't block if it doesn't exist: the path may be on another machine or not yet created.

```bash
uv run agentic-mbse research add-entry --title "<title>" --type <type> \
    --location "<location>" --use-for "<use for>" --validation "<validation>"
```

It prints `{"outcome": …, "reason": …}`. On `added`, confirm it. On `holdout_hit`, report the rule id and do not retry. On `precondition_failed`, report the reason; a title another hand-curated entry already has is refused, so offer to edit that entry instead.

**Offer access for local paths.** Follow the current assistant adapter’s external-source instructions. In Claude, offer to merge read permissions into existing settings. In Codex, check access under the active sandbox and use its approval path when needed; preserve owner configuration.

Confirm: report the addition and how many sources are now configured.

#### Remove a Source

List sources by number. Use the host question interface to select one (or ask conversationally if more than 4), and confirm removal.

**A registered source is retired.** Ask why; the reason is recorded. The slug is the last part of the entry's Location, `knowledge/sources/<slug>/`.

```bash
uv run agentic-mbse research retire --slug <slug> --reason "<why>"
```

It removes the manifest row, the index entry, the source directory and any raw copy together, and records the removal in `knowledge/RETIRED.jsonl`. On a refusal it prints JSON with the outcome and reason, and changes nothing. `referenced` means another entry mentions the slug; `precondition_failed` with drift in the reason means the registry disagrees with itself, so run `verify` and report what it finds.

**A hand-curated entry is removed by its title.**

```bash
uv run agentic-mbse research remove-entry --title "<title>"
```

An `unregistered` entry is neither. Report it as drift and leave it to the owner.

Report the result.

#### Edit a Hand-Curated Entry

Gather the new values, keeping the title, and rewrite the entry in one call:

```bash
uv run agentic-mbse research add-entry --replace --title "<title>" --type <type> \
    --location "<location>" --use-for "<use for>" --validation "<validation>"
```

A registered entry's text is part of its registration record and is not edited. To change it, retire the source and register it again under a new title.

#### Resolve a Queued Candidate

A research run queues a candidate it could not bring in, for a person to obtain or rule on. Find the open queues:

1. For each request under `knowledge/research/requests/runs/<request_id>/`, take only the newest run directory. An older run's queue is superseded by the newer run.
2. Read `return.json` there and list its `queued` entries: the candidate and the reason, with the request id.

For each candidate the user picks:

- **The user has since obtained a copy** (a PDF from behind a paywall, say): register it as in Add a Source, with `--local-pdf`. Then report the new `knowledge/sources/<slug>/` location so whatever waits on the request can use it. This skill does not re-run the request.
- **A hold-out hit**: its reason reads `<rule id> matched <n>x`. Show it; never register it.
- **A seam repair**: a reason starting `hold-out guard unavailable:`, `URL capture needs the web extra:` or `source index missing:`. Show it as a toolkit problem to fix, not a source to obtain.

The `research-seam.md` guide in the installed toolkit's docs directory (`uv run python -c 'from agentic_mbse.cli import get_docs_dir; print(get_docs_dir())'`) covers every kind of queued candidate under "Act on a queued source".

#### View Source Details

Display every entry with its full details. Read them from `knowledge/SOURCE_INDEX.md`; viewing is the one thing this skill does with the file itself. Offer next steps: add, edit or remove.

### 4. Next Steps

After any action, suggest:
- Add another source: run `/manage-sources` again
- Check the registry: `uv run agentic-mbse research verify`
- Start modeling: `/spec-model`
- Research sources: `/research`

## Guidelines

- Read the current state with `agentic-mbse research sources` before making changes — don't assume it
- Capture what can be captured: a registered source carries its own copy and hashes, and a hand-curated entry is only a pointer
- Warn on duplicate titles before calling the CLI; the CLI refuses them anyway
- Warn but don't block on unresolvable locations — the path may be on another machine or not yet created
- Never retry a hold-out hit, and never look for a way around one

---

**Related Commands:** For full project setup → `/onboard` | To acquire sources for a research question → `/research-acquire` | To explore sources → `/research` | To audit against sources → `/audit-models`
