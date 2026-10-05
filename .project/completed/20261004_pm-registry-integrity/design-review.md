# Design Review: Escaped Pipes and Registry ID Integrity

**Design:** `.project/active/pm-registry-integrity/design.md` at `62451fa`
**Spec:** `.project/active/pm-registry-integrity/spec.md` (contract at `5c15ab1`)
**Brief:** `.project/active/pm-registry-integrity/briefs/design_review.md`
**Review File:** `.project/active/pm-registry-integrity/design-review.md`
**Date:** 2026-10-04

**Evidence used.** Code at `62451fa` (unchanged since `9b82006` in `src/`). fusion-tea copies at `.orchestrate-logs/ft-snapshot/`. Six probes, kept at `.orchestrate-logs/design-review-scratch/` (gitignored; run each with `uv run --no-sync python <script>` from the repo root, except `cmark_gfm_pipes.py`, which needs `uv run --no-project --with cmarkgfm python <script>`):

- `e3_sim.py` patches the design's splitter (D1) into the parser and diffs the fusion-tea snapshot against `baseline.json`.
- `e4_sim.py` runs the orchestrator's unmodified `e4_check.py` against a monkeypatched simulation of D1, D3, D5, and D6.
- `cmark_gfm_pipes.py` renders the escaped-pipe cases with cmark-gfm, GitHub's renderer.
- `yaml_roundtrip.py` and `loss_paths_probe.py` test the backlog write-back (D8, D9) and the token boundary (D6) on hand-edited inputs.
- `comment_value_probe.py` writes table values containing HTML comment markers through the current `add_validation`.

---

## The Point

[INHERITED: product-lens.md, from `claude/skills/project-structure/SKILL.md`] Other artifacts cite registry IDs (`SV-`, `DI-`, `PR-`, `AD-`, `WI-`, `G-`, `AQ-`) by spelling. A record that silently disappears, or an ID minted twice, makes those citations ambiguous. Today both happen:

- Reads drop valid rows because the table splitter treats `\|` as a cell boundary (`parser.py:109`).
- Writes delete or corrupt records. The backlog writer rebuilds `BACKLOG.md` from parsed data (`operations.py:155`). `update_validation` has its own splitter and writes into the wrong column (`operations.py:1148`). `add_validation` writes pipes unescaped (`operations.py:194`).
- Allocators count only parsed records (`operations.py:58`), so a dropped record's ID can be minted again.

[AGENT, from the brief] The test for every decision: does it close a path by which a record disappears or an ID is issued twice, and does the code it describes read as if it had always been there?

## Fundamental Assessment

**Sound, with four bounded gaps.** This is the right piece of work, and the approach is right.

- The three mechanisms map one-to-one onto the three defect families: one inverse pair for cells, one ID discovery path, and a backlog writer that writes back what it read. Each new helper has named callers and earns its place. Nothing is speculative.
- The D8 deviation from the brief's steer is better than the steer on its merits (see Dimension 7). Writing back the loaded document keeps rejected items, rejected epics, unknown keys, and order by construction. The steer's mechanism would need index bookkeeping across three kinds of list and a new field on `BacklogData`.
- I checked the design's load-bearing claims against the fusion-tea copies, and they hold. E3 shows only `SV-035` appearing and its warning disappearing. E4 passes end to end (`SV-136`, `DI-015`, one added line). The backlog frontmatter writes back byte-identical. cmark-gfm agrees with D2 on `\\|`.

The gaps are all the same kind of miss. The design proves its guarantees for the paths it drew, but four inputs reach a record or an ID through a side door:

1. A first-match lookup maps a valid record back to the wrong raw text when an unparsed duplicate comes first, and `add-epic` can create that duplicate itself.
2. A value containing `<!--` or `-->` breaks the round-trip, because the parser strips HTML comments before it splits cells.
3. The token regex refuses to count an ID joined by a hyphen, so `DI-001-DI-014` reserves only DI-001.
4. `parse_frontmatter` can return less than the file holds without warning, through duplicate keys or a `---` line inside a block scalar. The write-back then deletes the rest.

Each fix is a few lines and changes no decision.

**Product lens: Gate CLEAR**, appended to `product-lens.md`. No owner or `[HARD]` contradiction, and neither structural smell fired.

- D8 fits "Scripts own BACKLOG.md" (`claude/commands/backlog.md:90`) and the template's "the frontmatter wins" (`BACKLOG.md.template:9-14`).
- D8 does move one invariant: the writer stops keeping the frontmatter schema-valid by deleting records. The design states this in Core Concept 3 and D9.
- The lens's three non-gating findings are dispositioned as m4 (refusal wording), m6, and n5 below.
- The lens instruction file was unreadable from this sandbox, so the lens ran on a fallback method. The ledger entry records this.

---

## Dimensional Review

### 1. Spec Compliance

**Assessment:** Concerns

**Criterion trace.** Each criterion maps to a mechanism, and none is met only on fixtures. Where a fusion-tea check applies, I ran it.

| Criterion | Mechanism | On the fusion-tea copies | Gap |
|---|---|---|---|
| 1. Escaped pipes | D1 splitter in `_parse_markdown_table`; D2 for the double-backslash case | `SV-035` parses as `baseline`/`passing` with the literal pipe-wrapped `rel dev` in Description and Expected (`e3_sim.py`, `e4_sim.py`) | none |
| 2. One escape rule | D1 + D3 + D4: `update_validation` splits, sets cell 9, re-formats; refuses an unparsed ID | Every SV row except `SV-034` re-formats byte-identical after split-then-format. A status change on `SV-035` changes only the Status cell. `SV-034` is refused. | first-match row lookup (M1) |
| 3. Round-trip (SV, PR, G, AQ) | D3 escape in `_format_table_row`; D10 multi-line refusal | E4's new row reads back identical | comment markers (M2) |
| 4. No ID minted twice | D5 + D6 at all eight `_next_id` call sites (`operations.py:312, 393, 430, 515, 694, 758, 784, 974`, verified) | `SV-136` above token max 135; `DI-015` above archive note `DI-014`; WI token max 100 equals parsed max | hyphen-joined ranges (M3); comment markers in values (M2) |
| 5. No record lost on write | D8 write-back, D9 refusals, `close_item` ordering | frontmatter writes back byte-identical | duplicate-target lookups (M1); short reads (M4) |
| 6. Nothing else changes | D1 is a no-op on rows without a backslash-pipe (I2); `_parse_backlog_mapping` is a pure extraction | E3 diff: `SV-035` added, its `row 34` warning removed, nothing else | none |

**E1 to E4.**

- **E1** follows directly from D1 and D5.
- **E2** follows from D5 and D8. The design's stated check for "exactly the one new record" is wrong for the heading registries (m1).
- **E3** holds under simulation. The orchestrator needs one harness fix, noted under Recommendations.
- **E4** passes under simulation with the unmodified harness.

**Provenance.** The design carries the spec's grades faithfully. It treats no `[INFERRED]` or `[INHERITED]` item as fixed beyond what the spec says. The one `[AGENT]` deviation (D8) is marked and reasoned. Nothing owner-given was dropped. The spec has no `[REFERENT]` items.

**Refusals in scope.** Refusing multi-line table values is required by criterion 3: no single-line row can read them back. It also prevents a real breakage today, where a newline in a description ends the table early. Refusing `update-validation` on an unparsed row is required by criterion 2: on a raw-pipe row, cell 9 is not Status. Both are correct and in scope.

### 2. Pattern Consistency

**Assessment:** Pass

- The splitter and escape sit beside `_parse_markdown_table`. ID discovery sits beside `_next_id`. `_parse_backlog_mapping` is extracted rather than rewritten.
- D10 copies `approve_research`'s "build everything, then write" shape (`operations.py:675`).
- Warnings flow through the existing `OperationResult.warnings` and `_print_warnings` (`cli/pm_cli.py:39`).
- One small departure: `operations.py` will import four underscore-named helpers from `parser.py`. Today only tests do this; `src/` has no cross-module private imports. It is acceptable under the selected ruff rules (`pyproject.toml:76`, verified), but see n1.

### 3. Abstraction Quality

**Assessment:** Pass

Every new helper earns its existence:

- **`_split_table_row` / `_escape_table_cell`.** Removing them means a second splitter, which is the defect.
- **`_id_pattern`.** It is the single token definition (I5).
- **`_registry_ids`.** It is the single discovery path. Returning a `ParseResult` is the existing idiom for "data plus warnings".
- **`_load_backlog` and `_backlog_list`.** They give D9's two refusal cases one home each.

The one abstraction I'd push on is `_write_backlog` accepting either a `BacklogData` or a document. Production code will only pass documents. The union exists so four test call sites stay untouched: a round-trip test at `test_pm_operations.py:163` and `:175`, and two fixtures at `:902` and `:1134`. See n2.

### 4. Duplication Avoidance

**Assessment:** Pass

The design removes the duplication that causes the bug: two splitters become one, and eight private "count parsed IDs" idioms become one path. It introduces no parallel structure.

The backlog now has two views, the document and the typed view. That is deliberate and kept in one direction: the typed view is always derived from the document. The coupling point between them is the raw lookup, which is M1.

### 5. Data Structure Clarity

**Assessment:** Concerns

- The backlog document is an untyped `dict[str, Any]` by necessity. Its whole job is to carry what validation rejects.
- The design names exactly where the untyped document is touched: append to three lists, and set two keys on one mapping. That is the right containment.
- The concern is how a typed target is mapped back to its raw mapping. The design uses "the first mapping whose `str(id)` or `str(name)` matches" (Implementation Notes, "Raw lookups"). That is not a correspondence; it is a guess that is right only when the key is unique. See M1.

### 6. Route Safety

**Assessment:** Concerns (adapted: here "routes" are the paths from an operation to the bytes it writes)

- Every write path is explicit, and I7 holds for every refusal the design lists. I checked `close_item` line by line: `_load_backlog` and the typed lookup both run before the first `_update_frontmatter_fields` call (`operations.py:1081`). Its only remaining half-close paths are exceptions, which the Non-Goals name honestly: `_update_frontmatter_fields` raising, and `shutil.move` failing.
- The two refusal cases are the right two for what `parse_frontmatter` reports. But they are not a complete list of unreadable documents, because `parse_frontmatter` can read less than the file without warning (M4).
- `register_intent` under D10 still calls `_append_table_row` once per row. A missing `## Analysis Questions` section raises after the goal rows are written (m2). That is a crash, not a refusal, so it sits outside I7's letter. But it is the exact partial write D10 was written to remove.

### 7. Bets & Decisions Integrity

**Assessment:** Concerns

**Stated bets.**

- **B1** (the file is a full record of IDs in use) is the spec's own narrowed contract, stated honestly.
- **B2** (tokens outside comments are records, citations, or archive notes) holds. Registry templates carry no tokens outside comments. The only hit is `AD-001` in `EPIC_GUIDE.md.template`, which is not a registry file. fusion-tea has no HTML comments at all.
- **B3** holds for fusion-tea byte for byte. On hand-edited YAML, every case I tried kept its values and lost only formatting: comments, block-scalar style, quoting, flow lists, indentation, line folding, and anchors renamed to `&id001`. That matches the design's "records survive, their text changes".
- **B4 is now settled true.** cmark-gfm (`cmark_gfm_pipes.py`) splits nothing in `a \\| b` and renders it `a | b`. That is D2's reading: one backslash dropped at split time, then the remaining `\|` is an ordinary escape at render time. It also renders the code-span pipe case as `p|q` and splits `` `m|n` ``. B4 can move from bet to fact, and the Potential Risks line about it can go.

**D8 on its merits.** The deviation is right.

- The steer's mechanism keeps rejected work items only. To pass E2 it must also restore each item's index in its list. It still drops rejected epics, non-mapping entries, and unknown keys unless extended. Its extra field on `BacklogData` changes E3's snapshot unless excluded from the dump.
- D8 keeps all of those with no new type.
- Its cost is the raw lookup. That cost is real (M1), but it is small and fixable, and it does not tip the comparison.

**Hidden bets.** Three load-bearing beliefs the design does not state, each false on some input:

- **HB1: "first match equals the record the typed view validated."** False when an unparsed duplicate comes first. This is M1.
- **HB2: "`_strip_html_comments` only removes comments a user wrote as comments."** False when a PM write puts `<!--` or `-->` into a value. This is M2.
- **HB3: "`parse_frontmatter` returns the whole frontmatter unless it warns."** False for duplicate keys and for a `---` line inside a block scalar. This is M4.

### 8. Reader Comprehension

**Assessment:** Pass

- The Core Concept gives a reader the model in one paragraph: "a tool acts on its parsed view when it should act on the file". Every decision hangs off it.
- Decisions name their rejected alternatives.
- The architecture sketches show owners and callers.
- One wording issue blocks precision rather than comprehension. I6 says "equals the loaded frontmatter", but it means "as loaded by `parse_frontmatter`". Top-level dates and booleans are stringified on load, so `flag: yes` is written back as `flag: 'True'` (`yaml_roundtrip.py`). It is not a record, but I6 should say which "loaded" it means (m5).

---

## Issues by Severity

### Critical

None.

### Major (must fix: each leaves a loss or reuse path open, per the brief's bar)

- **M1. A first-match lookup can target the wrong record, and `add-epic` can create the duplicate that causes it.** (Spec compliance, criteria 2 and 5)
  - The design maps a validated target back to raw text by first match: the first epic mapping whose name matches, the first work-item mapping whose ID matches, and the first table row whose first cell is the SV ID. Its Potential Risks section says duplicates "only happen in a backlog that already has the defect this item prevents". That is not true for epics.
  - `add-epic` checks for duplicates against the typed view (`operations.py:907`). So it will add a second epic `X` beside a rejected epic `X`, for example one with a mistyped status. A user is likely to do exactly this, because the rejected epic does not show in the dashboard.
  - Then `add-item --epic X` finds the valid `X` in the typed view, but the raw lookup picks the rejected one. The new item lands inside the rejected epic. The operation reports success, and the item is invisible to every PM view: the dashboard, `close-item`, and `parse_backlog`. Probe 3 in `loss_paths_probe.py` reproduces this.
  - `update_validation` has the same shape. It refuses only if the ID is unparsed, so a malformed duplicate row earlier in the file still receives the Status write. Its line scan also covers the whole file, while the parse covers only `## Verification Registry`.
  - **Fix:** every raw lookup must find exactly one match, or refuse before any write and name the duplicates. `add-epic`'s duplicate check should run on the raw document, so it refuses while naming the rejected epic and its parser warning. This adds one refusal rule to D9 and I7. It needs no new types.
- **M2. HTML comment markers in a written value break the round-trip and can hide records.** (Spec compliance, criteria 3 and 4)
  - I1 proves split-after-escape is the identity. But the parser runs `_strip_html_comments` over the whole file before it splits rows (`parser.py:523`, `:482`, `:735`), and the design's escape does not account for that.
  - On the shipped matrix template (`comment_value_probe.py`):
    - A description `keep the <!-- marker --> literal` reads back as `keep the  literal`. That violates criterion 3.
    - A description containing `opener only <!--` pairs with the template's own trailing `-->` (`VALIDATION_MATRIX.md.template:28-30`). The tool writes a row its own parser then drops with a warning. That is the defect class spec-review L3-3 called out for pipes.
  - Here the ID survives the scan, because the ID cell comes before the marker. But a `-->` in a later value would close an earlier unclosed `<!--` and strip every row in between, ID cells included. Those IDs then become reusable.
  - **Fix:** `_escape_table_cell` refuses `<!--` and `-->` exactly as it refuses a line break, with an escape-case test for each. The same guard is cheap for DI, AD, and backlog names if the orchestrator wants it, since the WI scan also strips comments. Criterion 3 does not require that.
- **M3. The left token boundary drops the upper end of a hyphen-joined range.** (Spec compliance, criterion 4)
  - D6's left class `[A-Za-z0-9-]` makes `DI-001-DI-014` count DI 1 only (`loss_paths_probe.py`). That is an under-count, and in exactly the archive-note case the whole-file scan exists for.
  - D6's own rule for the right side says under-counting is the direction that reuses IDs. The same reasoning applies on the left. The only thing the hyphen exclusion buys is not counting `X-SV-001`, and counting it would cost a gap at most.
  - **Fix:** change the left boundary to `(?<![A-Za-z0-9])`. `MAG-001` still does not count as G-001. Appendix A's `X-SV-001` row becomes "SV 1, a gap at most", and a `DI-001-DI-014` row should be added.
  - No fusion-tea copy has a hyphen-preceded token, so E3 and E4 are unchanged. The harness's narrower regex only lowers its own bar.
- **M4. `parse_frontmatter` can return less than the file without warning, and the write-back then deletes the rest.** (Route safety, criterion 5)
  - D9 refuses exactly when `parse_frontmatter` warns. D8's "keeps everything by construction" assumes that no warning means a complete read. Two hand-edit cases break that (`yaml_roundtrip.py`, `loss_paths_probe.py`):
    - **Duplicate keys.** PyYAML keeps the last one. A second top-level `standalone:` block, or a second `items:` in one epic, hides the first list. The write-back deletes it. This deletes records today too.
    - **A `---` line inside a block scalar.** The closing-delimiter check uses `.strip()` (`parser.py:219`), so an indented `---` inside `goal: |` ends the frontmatter there. That YAML still parses, with no warning. Everything after it, including later items and the whole `standalone` list, is treated as body and dropped by the write-back.
  - Tool-written multi-line names do not hit the second case. PyYAML quotes them, so the truncated text is malformed and D9 refuses. Both cases need a hand edit, which is how E2's fixtures are made too.
  - **Fix (cheap):** have `_load_backlog` load with a SafeLoader subclass that rejects duplicate keys, reported as D9 case 1. Accept only an unindented `---` as the closing delimiter: `rstrip()` in `parse_frontmatter`, and the same in `_update_frontmatter_fields` for consistency. A YAML block scalar cannot hold an unindented line under a top-level key, so this is safe, and fusion-tea's frontmatters are unaffected.
  - **Or:** name both cases in Non-Goals and drop D9's "everything else is carried forward" claim. That choice is the orchestrator's. Either way, the design should stop claiming completeness it does not have.

### Minor

- **m1. E2's stated check is wrong for DI and AD.** The Validation Approach says the added lines must be "exactly one carrying the new ID, and the rest blank separators". A heading record adds a heading plus four to six field lines. The check should read: only added lines, forming one contiguous block that is the new record plus blank separators, with exactly one line carrying the new ID. (Spec compliance)
- **m2. `register_intent` can still half-write.** D10 builds every row first but still appends one row per `_append_table_row` call. A missing `## Analysis Questions` section raises after the goal rows are written. Check both sections before the first append, or apply all inserts to one in-memory copy and write once. (Route safety)
- **m3. One reservation warning per distinct number, not per token.** fusion-tea's matrix has 156 SV tokens over 135 numbers. Its `REQUIREMENTS.md` and `ARCHITECTURE.md` have zero parsed records, so per-token warnings would repeat. D7 should say "one per distinct number". (Data clarity)
- **m4. Refusal messages should tell the user what to do.** (Reader comprehension; product lens)
  - `close-item` on a work item with `status: in-progress`, or `add-item --epic` on a rejected epic, reports "not found in BACKLOG.md". The raw document already has the target, so the message can say "present but not a valid record" and quote the parser warning.
  - `update-validation`'s new refusal on an unparsed row leaves no scripted path forward. Shipped commands route SV status changes only through it (`claude/commands/audit-models.md:33`), and repair is a Non-Goal. So the message should say the row must be fixed by hand, and why: for example, "raw pipe in a cell; escape it as a backslash-pipe".
- **m5. I6's "loaded frontmatter" should mean "as loaded by `parse_frontmatter`".** Top-level dates and booleans come back as strings, so unknown top-level scalars change type on the first write (`flag: yes` becomes `flag: 'True'`). No record is affected, and today's writer deletes such keys outright. (Data clarity)
- **m6. Say that a carried-forward invalid record stays out of the dashboard.** Under D8 the body is rendered from the typed view. A work item with an invalid field stays in the frontmatter but is missing from the rendered body and appears only as a warning. That is correct, since the template says the frontmatter wins. The design should still state it next to D8, because the spec says the body is "re-rendered from the kept records" (`spec.md:65`). (Reader comprehension; product lens)

### Nits

- **n1.** Four cross-module private imports with no `src/` precedent. Fine as designed; mention it in D11 rather than citing tests as the precedent.
- **n2.** `_write_backlog`'s `BacklogData`-or-document union exists for test fixtures only. Prefer one parameter type and convert at the two fixture call sites. Or keep the union and say in its docstring that the typed form is for tests.
- **n3.** Say that `_registry_ids` on a missing file returns the parsed IDs with no warning. The parse already warns, and `add_insight` creates the file on first write.
- **n4.** Move B4 from Key Bets to Research Findings with the cmark-gfm result, and drop its Potential Risks line.
- **n5.** Say that the parser's per-prefix record-ID regexes validate records and do not number them (`parser.py:324`, `:400`, `:488`, `:529`, `:742`, `:766`). Every ID they accept also fully matches `_id_pattern`, so they are not a second numbering authority. Saying so keeps I5 from reading as violated. (Product lens)

---

## Recommendations

1. **Close the four side doors (M1 to M4).** Each is a few lines and a test, and none changes a decision: unambiguous raw lookups plus a raw-document duplicate check in `add-epic`; refuse comment markers in table cells; drop the hyphen from the left token boundary; and either guard or explicitly scope out the two short-read cases.
2. **Fix E2's added-lines check for heading registries (m1),** and make `register_intent` check both sections before writing (m2).
3. **Tidy D7's warning count, the refusal wording, I6's wording, the dashboard note, and B4 (m3 to m6, n1 to n5).**
4. **For the orchestrator, outside the design:** `baseline.json`'s `file` fields hold an absolute scratchpad path from the session that made it. E3's comparison must normalise `file` or regenerate the baseline from the same path. Otherwise every warning reads as changed.

A bounded re-check of the revised sections is enough. The fixes are local and objectively verifiable, so a full second design review would not add confidence.

---

## Resolutions

Recorded by the orchestrator, 2026-10-04. All `[AGENT]`-grade; none escalated to the owner.

- **M1 — Accept.** Record lookups for `add-item --epic`, `update-validation`, and `add-epic`'s duplicate check require exactly one match in the file, else refuse. `add-epic` checks duplicates against the raw document, not parsed data.
- **M2 — Accept.** `_escape_table_cell` refuses `<!--` and `-->` the same way it refuses a line break.
- **M3 — Accept.** Left boundary becomes `(?<![A-Za-z0-9])`. Update Appendix A with the `DI-001-DI-014` case and confirm `SV-034-x` still counts as 34 and `MAG-001` still does not count as `G-001`.
- **M4 — Accept both fixes.** The frontmatter reader rejects duplicate top-level keys (refuse, naming the key) and treats only an unindented `---` line as the closing delimiter. In YAML a block scalar's content is indented, so an unindented `---` is never scalar content; this is a correctness fix, not a convention. Keep the "everything else is carried forward" claim, now true.
- **m1 — Accept.** E2 wording: for DI and AD the "one new record" is the whole multi-line record block plus its separators.
- **m2 — Accept.** `register_intent` verifies every section it will write exists before its first write.
- **m3 to m6 — Accept** as written.
- **n1 to n5 — Accept** where they are text edits; skip any that would change a decision.
- **Baseline paths — Fixed by the orchestrator.** `snapshot_parse.py` now records the warning `file` as a basename; `baseline.json` was regenerated against unchanged code (`.orchestrate-logs/ft-snapshot/`).

After the revision the orchestrator runs the bounded re-check the reviewer scoped (D6, D9, raw lookups, escape cases, E2 wording) by resuming the review session.

---

**Overall:** Revise
**Next Steps:** The orchestrator records resolutions above, then returns to `/_my_design` pointed at this review to incorporate them. The reviewer does not edit the design. After the revision, a bounded check of D6, D9, the raw-lookup note, the escape cases, and the E2 wording is enough before `/_my_plan`.

---

## Re-check (bounded) — 2026-10-04

**Design:** `design.md` at `06678c7`. **Scope:** D6 with Appendix A, D9's refusal table, the raw lookups, the escape cases, the E2 wording, and the design session's four extra calls. Accepted resolutions were not reopened.

**Verdict: Approve, conditional on one text edit (RC1).** RC1 is a sentence in D4, a word in R7, and one test row. The orchestrator can apply it directly; no further review is needed. Everything else in scope is sound.

### What landed, checked

- **D6 and Appendix A (M3).** The new boundary `(?<![A-Za-z0-9])` counts both 1 and 14 in `DI-001-DI-014` (`loss_paths_probe.py`). `MAG-001` still counts as no G, and `SV-034-x` still counts as SV 34. No fusion-tea copy has a hyphen-preceded token, so its maxima are unchanged. The E4 harness's narrower regex only lowers its own bar, as D6 says.
- **D9 and R1 to R9.** Every refusal is listed in one place, says what to change, and runs before the first write. I traced `add-item`, `add-epic`, `close-item`, `update-validation`, `promote-requirement`, `add-validation`, and `register-intent`. The `close-item` ordering section still holds: `_load_backlog`, R3, and R4 all run before the first `_update_frontmatter_fields` call.
- **Raw lookups (M1).**
  - `_single_match` is the only "exactly one" rule, and both R3 and R6 go through it. `_raw_epics` and `_raw_work_items` are the only definitions of a backlog match, and `add-epic` reuses `_raw_epics` for R5.
  - Because the raw match is unique, "valid" is exact: the target is valid if and only if the typed view holds that ID or name. R4 therefore cannot misfire.
  - The existing `test_epic_not_found` still sees "not found".
- **Escape cases (M2).** `\n`, `\r`, `<!--`, and `-->` each raise, and I1 now excludes comment markers. The pass-through cases are unchanged. R8 covers all three table add operations.
- **E2 wording (m1).** For DI and AD, the added lines must form one contiguous block (the heading and its field lines, plus separators), with exactly one line carrying the new ID. Correct.
- **Minors and nits.** m2 to m6 and n1 to n5 landed as text edits without changing a decision.

### The four extra calls

1. **Repeated keys rejected at any depth, on the write path only: sound.**
   - The resolution named top-level keys. But a second `items:` inside one epic hides records exactly the same way, and a repeated field inside one item would be silently collapsed on write-back. That is an alteration criterion 5 forbids.
   - Read-only callers keep last-wins, so `parse_backlog`, `state.py`, the dashboard, and E3 are unchanged.
   - The implementation note about merge keys (check each mapping node before `<<:` is flattened) is right for PyYAML's `SafeConstructor`.
2. **`close-item` through `_single_match`: sound.** It closes the duplicate-ID wrong-target case, and the lookup runs before any file is touched.
3. **`update-validation` skipping HTML comments: sound, and required.**
   - `TestUpdateValidation::test_happy_path` builds its matrix from the template. The template's commented example row `SV-001` (`VALIDATION_MATRIX.md.template:28-30`) would otherwise be a second candidate, so R6 would refuse the existing happy-path test.
   - The candidate region is the whole `## Verification Registry` section, which is slightly wider than the table the parser reads. The difference only adds candidates, which R6 or R7 then refuse, so it errs safe.
   - See RC1 for the one gap this call opens.
4. **Missing sections refuse for `promote-requirement` and `add-validation` (R9): sound.**
   - No existing test expects the old `ValueError`. The only `pytest.raises` in the PM operation tests is for `supersede_insight`.
   - `_append_table_row` keeps its signature and its raise, so `TestAppendTableRow` is unaffected.
   - The ID is minted before the refusal, but nothing is written.

### Remaining must-fix

- **RC1. D4 must say which line text it rewrites, and R7 must cover a comment marker in the target row.**
  - D4 finds candidates on comment-blanked text but does not say whether the write splits the blanked line or the file line. Both readings go wrong on a row with an inline comment, for example a description `Energy balance <!-- confirm tolerance with owner -->` (`recheck_d4_probe.py`):
    - **Split the blanked line.** The write silently deletes the comment from a non-target cell. Criterion 2 forbids changing anything but the targeted cell.
    - **Split the file line.** `_format_table_row` raises R8's `ValueError` inside `update-validation`, which has no refusal mapped for it. The user gets a traceback.
  - The same raise happens for a stray `-->`, or for an unclosed `<!--` that `_strip_html_comments` leaves in place.
  - **Fix:**
    - D4 splits and rewrites the original file line, at the index the candidate search found. Comment blanking keeps line numbers, so the indices match.
    - If formatting that line raises, `update-validation` refuses under R7 with "the row holds an HTML comment marker; edit it by hand".
    - Add `TestUpdateValidation::test_refuses_row_with_comment_marker`, asserting the file is unchanged.

### Nits (optional)

- In Component Overview, "`keep_lines=False` option" and "`unique_keys=False` option" read as if `False` were the option. Say "new keyword `keep_lines` (default `False`)", and the same for `unique_keys`.
- In D4, "That is the region the parser reads" should be "it contains the region the parser reads". The section is wider than the parser's table, which errs safe.

**Next Steps:** The orchestrator applies RC1 to `design.md` directly, then proceeds to `/_my_plan`. The reviewer does not edit the design.
