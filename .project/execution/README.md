# How to Record Execution Facts

Entries go in `ENTRIES.md`, in this directory. This file is the rules; that file is the log. `ENTRIES.md` is user data, so `init-project.sh --force` refreshes this file and never touches that one.

Two commands prompt for an entry, and nothing else does: `/_my_close`, when it scans an item's artifacts for records, and `/_my_wrap_up`, at session end, which asks the session directly. No command reads the entries back; the file exists so the owner can review what agents chose to save, and decide whether the class is worth building a reader for.

## What gets an entry — the density bar

An entry exists only if a future agent doing similar work would otherwise spend real time rediscovering it.

- **Good:** "The MCP server times out on startup because its venv imports off `/mnt/c` NTFS. Use a venv on native ext4." Cost real time, invisible in the code, still true next month.
- **Good:** "Markdown extracts of the P&IDs may carry transcription errors from low-res PDF rendering. Verify against the PDF whenever a numeral is load-bearing." A property of the data, not of the code.
- **Good:** "A skill directory left out of `NATIVE_SKILL_ALLOWLIST` is silently excluded from the Codex build." How the build behaves, learned the hard way. A decision record may sit nearby — the decision was to use an allowlist at all — but the behavior is the fact, and the fact belongs here.
- **Bad:** "The v1 data campaign is superseded; v2 locked envelope clipping option A." That is a decision with reasoning behind it. It goes in `.project/adr/`.
- **Bad:** "This repo is a personal workspace, not a shared team repo." Project context, not learned by doing. It belongs in `CLAUDE.md`.
- **Bad:** "I graded every constraint the owner mentioned as a requirement; only the ones they stated should have been." That is a correction to a pack prompt. It goes in `.project/feedback/ENTRIES.md`.
- **Bad:** "`--force` never overwrites a project's accumulated entries." That is a promise the pack makes. It goes in `.project/product/`.

## Where it does not go

Execution facts go here. The five wrong homes, and how to tell:

- **`.project/adr/`** — a decision with reasoning a future challenge re-derives against. An execution fact may sit near a decision (see the third Good example above), but the fact is the behavior, not the reasoning.
- **`.project/product/`** — a promise the product makes that a cold agent could reasonably miss or undo. Execution facts are properties of the environment, not contracts the pack upholds.
- **`.project/feedback/ENTRIES.md`** — a correction to a pack prompt. Wrong/Right/Learning about what an agent produced, not about how the world behaves.
- **`CLAUDE.md`** — project context that helps an agent orient. If the fact is about the project's identity or setup rather than a behavior discovered while working, it belongs there.
- **The native memory store** (`~/.claude/projects/.../memory/`) — execution facts go in the register, not in the memory directory. The harness instructs agents to write there, but entries in that store are not git-tracked and not owner-reviewed.

## The entry

Append to the end of `ENTRIES.md`. Never rewrite an existing entry.

```markdown
## [init-project.sh] 2026-09-10

**Fact:** `--force` never rewrites `completed/CHANGELOG.md` — it is protected user data, so template edits to it reach new projects only.
**Evidence:** `scripts/init-project.sh:122-127`; asserted by `test_init_project.sh` Test 8.
```

A triage-filed entry carries a third field:

```markdown
**Source:** migrated from the native memory store, triaged 2026-09-10.
```

- **The tag** is the surface the fact is about — the file, tool, or format name as it appears in the repo. In brackets, free-form in value, normalized to what the repo calls it (`init-project.sh`, `flow-mcp`, not "the installer"). One tag per entry.
- **The date** is today, ISO format.
- **Fact** is the durable statement — what a future agent needs to know.
- **Evidence** is how it was learned: the run, the error, the `file:line` that proved it.
- **Source** appears only on entries filed by the owner's triage of the native memory store, so agent-written and owner-migrated entries stay distinguishable.
- **No body line starts with `## [`.** That sequence marks the start of an entry.

## No reader

Nothing reads this file. The register exists so the owner can review what agents chose to save — in a diff, not through a tool — and decide whether a read path is worth building. The bracketed tag is the second whitespace-separated token on the heading line; keep it there so selection stays a one-liner if a reader is ever built.
