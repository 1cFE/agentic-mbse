# Product Promises

**Like `.project/adr/`, this directory is durable and load-bearing** — entries are meant to
be read and trusted sessions or months later. It is an append-only ledger of the product's
major **implemented promises**: what the product guarantees, in plain language, with
references to where each promise's authority lives. `INDEX.md` (generated) is the one
orientation surface a cold agent skims to learn what the product is for before touching it.

**Orientation, not proof.** An entry says a promise was implemented and when it was last
reasonably checked. It is not a certification and it does not detect drift. The code and
tests remain the source of truth for every detailed behavior; nothing anywhere gates on
this ledger.

## What is a promise — and what gets an entry

A promise is what the product guarantees to its users or consumers: a major use case, a
public surface, or a cross-cutting contract. Only **implemented** behavior belongs here —
proposed or planned behavior never enters the ledger.

The density bar is a judgment standard, not a checklist:

> Record a promise when it is a major use case, public surface, or cross-cutting contract
> **and** a cold agent changing related code could reasonably miss or undo it.

Sparseness is the point — this is not a feature inventory. Routine features, local
implementation behavior, and anything obvious from one code path stay in code and tests.
"Zero promises to record" is the common answer at close.

**The title is the promise's one-liner.** The index is only as orienting as its titles.

- **Bad title:** "CLI flags" (a surface label, not a promise — states nothing a cold agent
  could miss or undo)
- **Good title:** "One modeled source produces one public input" (a contract; an agent
  merging source handling could silently break it)

## Register boundary: promises here, decisions in `.project/adr/`

A **promise** is what the product guarantees and why it matters — it lives here. A
**decision** is the chosen mechanism, with the reasoning a future challenge re-derives
against — it lives in `.project/adr/`. "The evaluator supports late-fill entry injection"
is a promise; "we generate the package with inputs wired after graph construction" is a
decision. When one change produces both, file both — each register, its own entry; cite,
don't restate.

## Entry format

`product.sh new` writes the skeleton. Frontmatter (flat key/value — keep it that way):

| Field | Meaning |
|---|---|
| `id`, `title`, `date`, `owner` | Stamped by the script |
| `status` | `active` \| `amended` \| `superseded` (script-managed) |
| `amended_by`, `superseded_by`, `supersedes` | Entry links (script-managed) |
| `provenance` | `"[OWNER]"` \| `"[AGENT] (ratified by owner, date)"` \| `"[INHERITED: src]"` — grades the **summary itself**; cited sources keep their own grades |
| `surfaces` | The surfaces/components the promise binds, e.g. `[generation, cli]` |
| `checked` | When the promise was last reasonably verified as implemented: `YYYY-MM-DD` or `YYYY-MM-DD @ <short-sha>` (script-managed via `check`) |

Body sections:

- **Promise** (required, 1–3 sentences) — restate the promise in plain language.
- **Authority** (required) — graded citations to the durable sources that make it a
  promise (spec, concept, ADR, docs). Every entry rests on at least one durable authority
  source or a first-capture owner quote (below). Implementation evidence establishes that
  the behavior *exists*; it never creates product *authority*.
- **Evidence** (optional, proportional) — paths, test names, or "exercised manually
  <date>". Tests are nice to have, never mandatory. Evidence never substitutes for
  Authority.
- **Scope** (optional, one or two sentences) — partial rollout or flags. Never a catalog.

**Summaries are discovery; citations are authority.** An entry's summary carries only its
own `provenance` grade and never inherits the authority of what it cites. Agents deriving
product truth (e.g., the product-lens) locate promises via the index, then follow the
Authority citations and derive their oracle from those sources at their own grades.

## First capture

Rarely, an entry is the first durable capture of an owner-stated promise with no existing
artifact home (stated in chat, or surfaced by a lens can't-find). Then the Authority
section carries the `[OWNER-VERBATIM]` quote itself, with date and context. This should be
rare — normally at least a spec exists; the normal entry cites an existing artifact.

## Lifecycle

Entries are **append-only**: a body is immutable after filing. The permitted mutations are
script-managed frontmatter changes only — status flips and the `checked` stamp:

```
.project/scripts/product.sh new <slug> [--title "..."]   # create next entry, print path
.project/scripts/product.sh supersede <old-id> <new-id>  # promise materially changed; new replaces old
.project/scripts/product.sh amend <old-id> <new-id>      # new adjusts old without killing it
.project/scripts/product.sh check <id> [ref]             # stamp last-verified date (+ optional git ref)
.project/scripts/product.sh index                        # regenerate INDEX.md
```

Numbers are allocated and statuses flipped **only** by the script — never by hand.
`INDEX.md` is a generated artifact; hand edits to it are lost by design. When a promise
materially changes or disappears, file the successor and `supersede` (or `amend`) the old
entry — never silently rewrite. Superseded entries remain readable; the index lists them
below active entries with their successor id.

`new` leaves `checked` at `null` — a skeleton is not a verified promise. Stamp it with
`check` once the entry is filled and the behavior confirmed (at close, the audit is that
confirmation). `check` is the honest-state stamp: "I looked; the promise still holds as of
this date/ref."
A stale `checked` date is honest staleness, not an error — there is no re-verification
duty. If a check finds the promise no longer holds, the honest move is to supersede it or
surface the gap to the owner.

## Cross-seam placement

**A promise lives in the repo that must uphold it, not the repo that discovered it.** A
consumer repo that depends on another repo's promise files the ruling entry in the
upholding repo's `.project/product/` (the script bootstraps the directory if absent) and a
**pointer entry** locally: its title restates the promise's one-liner — so the local index
still orients a cold agent — and its body is a one-line citation of the upstream repo and
entry id. The full restatement lives only in the ruling entry, so the two repos cannot
drift. If the upholding repo is unreachable, file the pointer locally and surface the gap
to the owner.

## Who reads and writes this

- **Read:** every session skims `INDEX.md` at session start (context-loading rule) and
  opens only the entries relevant to its task; the product-lens uses the index as an
  index-first discovery surface.
- **Write:** `/_my_close` scans for promises crossing the density bar, confirms with the
  owner, and files before archiving. Zero entries is the common case. Nothing gates on the
  answer.

An absent or empty directory means "no major promises recorded" — never an error. Agents
fall back to README, docs, ADRs, and concepts.
