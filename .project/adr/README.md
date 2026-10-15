# Decision Records

**Unlike the rest of `.project/`, this directory is durable and load-bearing.** The rest
of `.project/` is working state — useful for tracing intent, not meant to be relied on.
Entries here are meant to be read and trusted sessions or months later.

This is an append-only log of **decisions, not descriptions**. A doc describing how the
system works starts rotting the day it is written, and nobody can tell stale from current
by reading it. A dated "we decided X, because Y" stays true forever as a historical fact —
the worst that happens is supersession, which, unlike staleness, is markable. So: never
maintain a current-state description here. Reconstructions of current truth (a lifecycle
contract, a consolidated invariant register) are themselves dated entries, superseded when
they drift.

## What gets an entry — the density bar

> An entry exists only if, without it, a future agent would plausibly **re-derive the
> wrong thing** or **relitigate the decision**.

High density comes from what you exclude. Routine choices, anything obvious from the code,
and anything the pipeline artifacts already settle for their own item do not get entries.
Load-bearing decisions do — especially contracts and invariants across large seams (major
components, repos, consumers).

- **Bad entry:** "We use pytest for testing." (Nobody would re-derive otherwise; the code
  shows it.)
- **Good entry:** "Late-fill entry injection is a supported evaluator capability; the
  generated package must accept inputs wired after graph construction." (A future agent
  auditing 'unresolved input' errors would plausibly rule the opposite.)

## Lifecycle

Entries are **append-only**: a body is immutable after filing. The single permitted
mutation is a frontmatter status flip, and only via the script:

```
.project/scripts/adr.sh new <slug> [--title "..."]   # create next entry, print path
.project/scripts/adr.sh supersede <old-id> <new-id>  # old is dead, new replaces it
.project/scripts/adr.sh amend <old-id> <new-id>      # new adjusts old without killing it
.project/scripts/adr.sh index                        # regenerate INDEX.md
```

Numbers are allocated and statuses flipped **only** by the script — never by hand.
`INDEX.md` is a generated artifact; hand edits to it are lost by design. To change a
recorded decision, file a new entry and `supersede` or `amend` the old one. An old entry
that doesn't know it is dead will be faithfully applied by a future agent — that is why
the flip is not optional.

**Amendment care** follows the provenance grade (see
`claude-pack/rules/capture-fidelity.md`): an `[OWNER]` entry is challenged by asking the
owner; an `[AGENT]` entry by re-deriving against its recorded Why. That is why the Why
section is required.

## Entry format

`adr.sh new` writes the skeleton. Frontmatter (flat key/value — keep it that way):

| Field | Meaning |
|---|---|
| `id`, `title`, `date`, `owner` | Stamped by the script |
| `status` | `active` \| `amended` \| `superseded` (script-managed) |
| `amended_by`, `superseded_by`, `supersedes` | Entry links (script-managed) |
| `provenance` | `"[OWNER]"` \| `"[AGENT] (ratified by owner, date)"` \| `"[INHERITED: src]"` — how the decision was actually made |
| `seams` | Components/repos the decision binds, e.g. `[generation, fusion-tea]` |
| `promoted_to` | Optional path if copied into repo-official docs; the entry remains the provenance record |

Body sections: **Decision** (1–3 sentences) · **Why** (required — the reasoning a future
challenge re-derives against) · **Invariants established** (may be omitted) · **Rejected
alternatives** (one-liners, phrased as decision records, never as instructions to future
agents).

## Cross-seam placement

**A decision lives in the repo that must uphold it, not the repo that discovered it.**
A consumer repo that discovers a constraint or workaround against another repo's behavior
files the ruling entry in the upholding repo's `.project/adr/` (the script bootstraps the
directory if absent) and a **pointer entry** locally — a one-line citation of the
upstream repo and entry id, never a restatement. If the upholding repo is unreachable,
file the pointer locally and surface the gap to the owner.

## Who reads and writes this

- **Read:** `/_my_concept_design` sweeps this index (plus the repo's official docs) and
  must produce a Prior Art section; `/_my_design` skims the index at setup and cites
  entries whose seams overlap the item.
- **Write:** design acceptance files the settled load-bearing decisions (zero entries is
  the common case); `/_my_close` files decisions that emerged during implementation.
- One decision, one entry — filed at the stage that settled it; later artifacts cite,
  never re-file.

An absent or empty directory means "no prior decisions yet" — never an error.
