# Brief: spec_review — pm-registry-integrity

**Sent:** 2026-10-04 by the orchestrator. **Stage:** `/_my_spec_review`. **Target:** `.project/active/pm-registry-integrity/spec.md`.

## What this work is for

[AGENT, re-derived from the spec and product lens] Registry entries and their IDs are stable referents. Other artifacts cite `SV-`, `DI-`, `PR-`, `AD-`, `WI-`, `G-`, `AQ-` IDs by spelling. A row that silently disappears, or an ID minted twice, makes those citations ambiguous. The two concrete repairs (honor the GFM `\|` escape in the shared table parser; stop every allocator from minting an ID that is still textually present in its file) serve that outcome. Review the spec against that outcome, not against "the parser handles backslashes."

## Owner rulings (2026-10-04, in the Align exchange)

- [OWNER] No reserved gates. The orchestrator decides and records; the owner is consulted only on an unexpected issue needing their judgement.
- [AGENT] (ratified by owner, 2026-10-04) The acceptance evidence for the item is the following four checks. The owner's words were "those hold. proceed."
  1. The spec's three-record reproduction becomes a pytest test that is red before the fix (one row parses; allocator mints `SV-034` again) and green after (escaped row parses, malformed row still warned, next ID `SV-036`).
  2. Each of the seven registries gets a fixture whose highest ID sits in a record that fails parsing. The add operation mints above it and the file diff is exactly the one new record. Table (SV, PR, G, AQ), heading (DI, AD), and frontmatter (WI) each get their own case.
  3. No regression: the existing PM suite stays green, and a parse snapshot of copies of fusion-tea's real registry files is identical before and after except for `SV-035` appearing.
  4. End-to-end on a copy of fusion-tea's real matrix, run by the orchestrator: `SV-035` present with literal `|rel dev|` in the right columns and status `passing`; `SV-034` still warned; the new row minted above every ID in the file with nothing else rewritten.

## Orchestrator decisions (execution detail, recorded here so the trail shows them)

- [AGENT] The historical operations contract ("IDs are never reused", `.project/completed/20260203_d4.4-operations/spec.md:73`) was never implemented: the allocator is max-plus-one over parsed records, so deleting the highest ID has always reused it. This item narrows the guarantee to IDs present in the registry file. No persistent high-water mark. The spec should close its third open question with that decision rather than leave it open.
- [AGENT] Branch is `pm-registry-integrity` cut from `main` at `9b82006`. The spec header's `harness-right-size` is stale (that PR merged).
- [AGENT] Write-side escaping (emit `\|` when a new cell contains a literal pipe) is a design decision, not a spec question.

## Facts verified by the orchestrator that you cannot check yourself

Stage subagents cannot read sibling repositories. Read-only copies of fusion-tea's registry files are at `.orchestrate-logs/ft-snapshot/` (gitignored), with `baseline.json` = what the current parser returns for them and `snapshot_parse.py` = the script that produced it.

- In the real `VALIDATION_MATRIX.md`, **SV-034 is the malformed row** (raw unescaped `|rel dev|` in two cells) and **SV-035 is the valid GFM row** (`\|rel dev\|`). The backlog and spec describe both as escaped; that is wrong for SV-034. After the fix, SV-035 should parse and SV-034 should stay diagnosed. Repairing SV-034 means editing fusion-tea's file, outside this item.
- The real matrix holds 135 `SV-` rows, max `SV-135`, no duplicate IDs. The current parser returns 133 records and two warnings ("Invalid Type 'rel dev'" at rows 33 and 34). So the real file reproduces the **row loss** but not the **ID reuse**; the next real ID today is `SV-136`. Reuse is reproduced only when the dropped record holds the maximum ID, which is what the spec's three-record fixture does. The spec's Problem statement should be accurate about this.
- fusion-tea's `ARCHITECTURE.md` uses `## AD-001: ...` H2 headings with no `## Key Decisions` section. `parse_architecture` (`src/agentic_mbse/pm/parser.py:653`) scopes to `## Key Decisions` then `### AD-`, so it returns **zero** records for a file holding AD-001 onward. `add-decision` on that project would mint `AD-001`. This is a second live instance of the hazard, in a heading registry, caused by section-structure drift rather than a malformed record. It bears directly on how "omitted by parsing" is worded in success criterion 3.
- fusion-tea's `REQUIREMENTS.md` also parses to zero `PR-` records. I have not determined whether it holds unparsed PR rows or is genuinely empty of rows; treat as unverified.

## Points I want the review to attack

- Is "all seven prefixes" real exposure or ceremony for `WI`, whose IDs come from BACKLOG frontmatter via a different path (`operations.py:965`)? Say which registries actually have a parse-then-omit failure mode.
- Criterion 3 says an ID "still present in its registry." Present how: parsed, or textually present anywhere in the file (prose mentions, archived-ID notes like fusion-tea's "Previous decisions (AD-001 through AD-005) archived")? The spec should state the contract precisely enough that design cannot pick a weaker reading.
- Criterion 1's escape semantics: does the spec say what `\\|` (escaped backslash before a pipe) means, and whether escapes inside backtick code spans are honored? GFM says `\|` is an escape even in code spans inside tables. Leaving it to design is acceptable if the spec says so explicitly.
- Criterion 4's "externally referenced ID spelling" is vague. What concretely must not change?
- Whether the four acceptance checks above belong in the spec as success criteria or evidence requirements, and whether the corrected fusion-tea facts should replace the current Problem wording.
- Standard devil's-advocate pass per your command: faithfulness of the INHERITED tags to `../../backlog/BACKLOG.md`, code-facing claims (line numbers cited are `parser.py:109`, `operations.py:58`, `:514`), sizing (backlog says 0.5 day; spec says MEDIUM).

You own the review doc only; do not edit `spec.md`. There is no live spec-authoring session; the orchestrator will apply resolutions through a fresh `/_my_spec` session fed with your review. Record each finding with an ID and a proposed resolution the orchestrator can accept or override.
