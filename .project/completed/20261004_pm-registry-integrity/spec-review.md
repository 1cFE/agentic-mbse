# Spec Review: Escaped Pipes and Registry ID Integrity

**Spec:** `.project/active/pm-registry-integrity/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md` (not readable from this stage's sandbox; structural conformance to it was not checked)
**Review File:** `.project/active/pm-registry-integrity/spec-review.md`
**Brief:** `.project/active/pm-registry-integrity/briefs/spec_review.md`
**Date:** 2026-10-04

**Evidence used.** Code at `9b82006` plus the working tree. fusion-tea registry copies at `.orchestrate-logs/ft-snapshot/` (gitignored). Four probes against the current code, kept at `.orchestrate-logs/spec-review-scratch/probe.py` (gitignored, rerun with `uv run --no-sync python .orchestrate-logs/spec-review-scratch/probe.py`). The existing PM suite passes today: 224 tests across `tests/test_pm_*.py`.

---

## Reality Check

**Concerns.** The spec is about the right work item and its two repairs point the right way. But it misses two write paths that defeat its own outcome. The validation status update has its own pipe splitter that corrupts escaped rows (`operations.py:1148`). The backlog writer deletes work-item records it could not parse (`operations.py:155`). Its central contract, an ID "still present in its registry," can be read three ways, and they give different next IDs on fusion-tea's real files. These are targeted edits, not a rework.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The Problem section misstates the real-file facts and mixes two defects that have different evidence.
- In fusion-tea's real `VALIDATION_MATRIX.md`, `SV-034` is the malformed row (raw `|rel dev|`, no backslashes). `SV-035` is the valid escaped row (`\|rel dev\|`, 9 cells under GFM splitting, status `passing`). The backlog describes both as escaped. That is wrong for `SV-034`. I verified both rows in the snapshot.
- The real file has 135 `SV-` rows with max `SV-135`. It parses to 133 records with 2 warnings. So the real file shows **row loss**, not **ID reuse**: the next real ID is `SV-136`. Reuse shows up only when the dropped row holds the highest ID. That is what the three-record fixture builds (probe 1 confirms: parses only `SV-033`, `add-validation` mints `SV-034`).
- The reproduction sentence comes from the status report (`.project/reports/2026-10-04-0901-status-report.md:64`), not the backlog. Yet it sits under a single `[INHERITED: ../../backlog/BACKLOG.md]` tag.
- **Proposed resolution:** Rewrite Problem to name the two defects separately: row loss (seen on real data) and ID reuse (seen when the dropped row holds the max, shown by the fixture). Use the corrected `SV-034`/`SV-035` facts. Cite the status report for the reproduction. Note that the fixture's labels are the reverse of the real file's (fixture: `SV-034` escaped, `SV-035` malformed). That is fine, but say so, so nobody "corrects" the fixture to mirror fusion-tea.

**L1-2 · Direct claim:** The `[INHERITED]` source for criterion 3 and the first Known Requirement is partly self-authored.
- The backlog Goal the spec cites was rewritten on 2026-10-04 in commit `6960ae4`. That commit landed at the same timestamp as the commit that added this spec (`67c4d23`, 14:33:23), in the same status-refresh session.
- The original Goal, filed 2026-08-21 from fusion-tea's WI-030 session (first visible in `35fa2b6`), named the seven prefixes and a raw `^\| (PREFIX-\d+) \|` scan.
- So the seven-prefix **scope** does trace to the original filing and is faithful. The "native representation" wording is the spec agent's own.
- The rewrite was justified by the report's claim that "DI/AD/G/AQ use headings" (`status-report.md:107`). That claim is wrong for G and AQ. Both are tables (`parser.py:738`, `:762`), and the original scan would have covered them.
- **Proposed resolution:** Cite both the original Goal and the 2026-10-04 rewrite. Grade the "native representation" sentence `[INFERRED]`. Scope stays as is.

**L1-3 · Direct claim:** One orchestrator fact needs a correction before it reaches the spec. fusion-tea's `ARCHITECTURE.md` does parse to zero AD records. But `register-decision` (the command; there is no `add-decision`) **refuses to write**. It returns "'## Key Decisions' section not found" (`operations.py:446-451`). Probe 4 confirms this on the snapshot copy. So no `AD-001` is minted today. The hazard is latent: it goes live as soon as someone adds a `## Key Decisions` heading to that file. PR, G, and AQ have the same shape on fusion-tea: their append helper raises when the section heading is missing (`operations.py:225-226`), and fusion-tea has no `## Requirements`, `## Goals Registry`, or `## Analysis Questions` section. **Live allocation exposure on fusion-tea today is SV, DI, and WI.** **Proposed resolution:** If the spec cites the AD case, cite it as latent, caused by the file's section structure drifting from what the parser expects.

**L1-4 · Question (premise conflict; owner-judgement candidate):** fusion-tea has already restarted ID numbering after archiving, in three registries:
- `KNOWLEDGE.md:11`: "Previous entries (DI-001 through DI-014) archived". The file then holds a fresh `DI-001`…`DI-011`.
- `REQUIREMENTS.md:5`: "Previous requirements (PR-001 through PR-007) archived". The file then holds `### PR-1`…`### PR-5`.
- `ARCHITECTURE.md:5`: "Previous decisions (AD-001 through AD-005) archived". The file then holds `## AD-001`…`## AD-008`.
- `REQUIREMENTS.md:65` cites "archived DI-014" by spelling.

The orchestrator narrowed the guarantee to IDs present in the registry file, with no persistent high-water mark. The reasoning recorded for that was "max-plus-one has always reused a deleted highest ID." The real data shows that archiving, not deletion, is how IDs actually leave these files, and it has already produced duplicate IDs across archive generations.

The contract reading decides what happens next:
- If only records count, fusion-tea's next DI is `DI-012`. That collides with archived `DI-012` and is two steps from the cited "archived DI-014".
- If every ID token in the file counts (see L3-1), the archive note's endpoint pushes the next DI to `DI-015`.

I can't see fusion-tea's history, so whether those restarts came from this allocator or were deliberate is my inference, not a checked fact. Whether fusion-tea means each archive generation as its own namespace is a fusion-tea convention question. I note it and do not resolve it.

**Proposed resolution:** Adopt the whole-file reading (L3-1). It covers this case at no extra cost for as long as the archive notes exist. Add one line to the spec saying that IDs moved to an archive file are protected only while the registry file still names them. Escalate to the owner only if the orchestrator wants the stronger guarantee, a persistent high-water mark. That would reverse the orchestrator's no-high-water-mark decision, which is `[AGENT]`-grade and so open to challenge on this evidence.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim:** "All seven prefixes" is real exposure, including WI. But each registry fails differently, and the spec treats them as one. This answers the brief's question about which registries really have a "parsed, then left out" failure:

| Registry | Format | What drops a record today | What an escaped pipe does | What the add operation does to the file |
|---|---|---|---|---|
| SV | table under `## Verification Registry` | invalid ID, Type, Mechanism, or Status (warned); rows after a prose line or outside the section (silent) | row dropped (Type check fails) | inserts one row |
| PR, G, AQ | tables | invalid ID cell only (warned), e.g. `**PR-007**`, or a header spelled `Id` so the ID reads as empty; rows outside the scanned table (silent) | row **not** dropped: later columns shift silently, with no warning | inserts one row; raises if the section heading is missing |
| DI | `### DI-NNN: title` headings | invalid Status (warned); heading shape drift such as `## DI-` or a missing colon (silent) | n/a | appends at end of file |
| AD | `### AD-NNN:` under `## Key Decisions` | invalid Status (warned); headings outside that section (silent; fusion-tea's case) | n/a | refuses if the section is missing, else inserts |
| WI | BACKLOG YAML frontmatter | invalid id, scale, status, or priority (warned); one invalid epic drops all its items; malformed YAML drops the whole registry (warned) | n/a | **rewrites the whole file from parsed data, deleting dropped records** (L2-2) |

Two consequences for the spec:
- For PR, G, and AQ, the escaped pipe is not what drops a row. It silently corrupts values. Criterion 1 fixes that, so criterion 4 must allow those rows' parsed values to change (L3-5).
- For PR, G, and AQ, the check-2 fixture must drop a row some other way than an escaped pipe, e.g. a decorated ID cell.

**Proposed resolution:** Put a per-registry exposure summary in the spec, either this table or the spec agent's own.

**L2-2 · If-then tradeoff:** The work-item writer deletes records. Probe 3 and probe 5 show two cases:
- **One bad record.** A record with `status: in-progress` is dropped by the parser. `add-item` then mints that record's ID (`WI-002`) again and deletes the record from the file.
- **Broken YAML.** With malformed YAML in `BACKLOG.md`, `add-item` succeeds, mints `WI-001`, and **erases every existing work item**.
- `add-epic` and `close-item` share the same writer (`_write_backlog`, `operations.py:155`).

This is the product lens's falsifier, "a supported registry entry disappears silently," in its worst form. Fixing ID allocation alone would protect the ID and still delete the record. The historical operations spec already required "fail with a clear error, not corrupt the file" for a malformed backlog (`.project/completed/20260203_d4.4-operations/spec.md`, Edge Cases). The ratified check 2's WI case ("file diff is exactly the one new record") cannot pass without changing this writer. So the owner has already ratified a write-path change, probably without seeing it.

Two options:
- **(A) Keep it in scope.** Outcome: no PM write deletes or alters an existing record. When the tool cannot keep a record, it refuses and names the record. Check 2 stands as ratified. Cost: the WI writer must carry forward records it cannot validate, and the broken-YAML case must refuse.
- **(B) Split it.** File a separate item for the WI writer and amend check 2's WI case. That changes an owner-ratified check, and it leaves the worst data-loss path open while this item claims WI is protected.

**Proposed resolution:** (A). It is the same outcome, and check 2 already requires it. Design chooses whether the tool keeps the bad record or refuses.

**L2-3 · Direct claim:** Open Question 1 frames the fix as "format-aware discovery" and says a table-only scan cannot cover every registry. That is true, but it skips over the simplest mechanism that does cover them: scan the whole registry file for same-prefix ID tokens outside HTML comments. One scan works for tables, headings, and frontmatter alike. It also catches files whose structure has drifted (fusion-tea's `## AD-001` H2 headings, `### PR-1` headings), which a per-format record detector would have to anticipate shape by shape. Design should stay free to choose. **Proposed resolution:** Once L3-1 fixes the contract, drop OQ1 or reword it to name both mechanisms neutrally.

**L2-4 · Direct claim:** The sizing conflict resolves toward the spec. The backlog's 0.5 day was sized for the original recipe: one splitter fix plus a raw table scan. Current scope is two splitters (L3-2), seven allocators across three formats, the WI writer (L2-2 option A), seven fixtures, and snapshot plus end-to-end verification. MEDIUM fits. 0.5 day is stale; 1.5 to 2 days is closer. **Proposed resolution:** Keep MEDIUM. The orchestrator updates the backlog's Effort line when it next touches the backlog. Under option A this is not a split candidate.

### Lens 3 — Pipeline Risk

**L3-1 · Too vague (the core contract):** Criterion 3 protects "a syntactically valid ID still present in its registry because the enclosing record was omitted by parsing." Three strong engineers could build three things:
- **(a) Parsed records only.** This is today's behavior and fails the item.
- **(b) Record-shaped text the parser rejected.** A table row with a valid ID cell, a `### DI-NNN` heading, or a YAML `id:` line. This protects the fixtures. It misses structural drift unless each drift shape is listed. It does not count archive notes, so fusion-tea's next DI is `DI-012`.
- **(c) Any same-prefix ID token in the registry file outside HTML comments.** This protects everything (b) does, plus drift and archive notes, so fusion-tea's next DI is `DI-015`.

HTML comments must be excluded:
- Every shipped template carries example IDs inside HTML comments: `| SV-001 |`, `| SV-002 |`, `| PR-001 |`, `| PR-002 |`, `| G-001 |`, `| G-002 |`, `| AQ-001 |`, `| AQ-002 |` (`project_templates/*.md.template`).
- Existing tests build fixtures from those templates and assert the first IDs are `PR-001`, `SV-001`, and `G-002` (`tests/test_pm_operations.py:497`, `:577`, `:845`).
- A scan that included comments would break the existing suite (ratified check 3) and the historical empty-project contract. I verified the templates have zero ID tokens outside comments.

The ratified check 4 already says "minted above every ID in the file", which is reading (c).

**Proposed resolution:** State reading (c) as the contract, as an observable outcome: a new ID is numerically greater than every same-prefix ID that appears in the registry file outside HTML comments, whether or not the parser accepted its record. Record its costs:
- A prose mention of a high number permanently skips numbers. That leaves a gap, never a reuse.
- An ID that appears only inside an HTML comment, such as a commented-out retired row, is not protected.

Keep allocation strictly above the max with no gap filling, because the archive-note protection depends on it. A token must stand alone: `MAG-001` is not `G-001`. `PR-1` and `PR-001` both count as 1 under today's allocator (`operations.py:63-67`). Whether they are the same ID in fusion-tea is that project's convention question; note it, don't resolve it.

**L3-2 · Missing content (a second splitter):** `update_validation` re-splits rows on every `|` (`operations.py:1148`) and rewrites the row. Probe 2, on an escaped row: `update-validation SV-034 passing` reports success. It then writes `passing` into the Source column, leaves Status at `pending`, and rewrites `\|rel dev\|` as `\ | rel dev\ |`. After this item's parser fix, fusion-tea's `SV-035` becomes visible. The next status update on it would corrupt it while reporting success. The spec's Related Artifacts cites only `parser.py:109`. **Proposed resolution:** Add a criterion. Every operation that reads or rewrites a registry table row applies the same escape rule. Updating a row changes only the targeted cell. Add a test on an escaped row.

**L3-3 · Missing content (write/read round-trip):** OQ2 ends with "Read/write behavior should agree without requiring hand edits". That is an outcome hidden among the deferrals. Today `add-validation` with a description containing `|` writes an unescaped row (`_format_table_row`, `operations.py:194`), which the parser then drops. The tool creates the row-loss defect itself. The orchestrator ruled that the escaping mechanism belongs to design. The outcome still belongs in Success Criteria. **Proposed resolution:** Add a criterion: a value written by any PM add operation reads back identical through the parser. The mechanism stays in design.

**L3-4 · Explicit deferral needed (escape edge cases):** OQ2 defers "consecutive backslashes" but names no reference behavior and doesn't say whether code spans are in scope. GFM treats `\|` as an escape inside code spans in table cells too. On real data the risk is low. fusion-tea's registry files contain exactly one line with `\|` (`SV-035`), no `\\|`, and no code span containing a pipe. **Proposed resolution:** The spec says splitting follows GitHub's GFM table behavior, including inside code spans, and that `\\|` behavior is chosen in design and pinned by a test. That makes the deferral explicit, which the brief accepts.

**L3-5 · Too vague (criterion 4):** "Externally referenced ID spelling" doesn't say what must not change. **Proposed resolution:** Make it concrete:
1. No operation renumbers, re-pads, or re-spells an existing ID; `PR-1` stays `PR-1`.
2. New IDs keep the `PREFIX-NNN` form with three-digit minimum padding (`operations.py:70`).
3. Parsed values of rows without `\|` are unchanged.
4. Rows containing `\|` change to the unescaped value. That change is the fix, and it includes PR, G, and AQ rows that today parse with shifted columns (L2-1).
5. Whether new diagnostics are allowed is decided under L3-6.

**L3-6 · Placement of the ratified acceptance checks:** Checks 1 to 3 map onto criteria 2, 3, and 4.
- **Grade.** They should enter the spec as the evidence each criterion requires, graded `[INFERRED] (ratified by owner, 2026-10-04: "those hold. proceed.")`. Not `[NEED]`: the owner approved them but did not originate them.
- **Where they run.** Check 4 and the snapshot half of check 3 run on gitignored copies of a private sibling repo. They are verification the orchestrator runs and records in the audit, not CI tests. The spec should say so.
- **Check 3 wording.** "Identical except SV-035 appearing" must also allow SV-035's warning to disappear. As written it freezes the warning list, which would forbid a useful new diagnostic such as "SV-034 present but not parsed; its ID is reserved". I'd allow new diagnostics, since they serve the outcome.
- **Check 2 wording.** Appends to the heading registries add blank separator lines (`operations.py:199-210`, `:461-468`). So "diff is exactly the one new record" should allow whitespace separators. Check 2's WI case depends on L2-2 option A.

**L3-7 · Deferral accuracy:** OQ3 (the historical "IDs are never reused" contract) is closed by the orchestrator's decision. **Proposed resolution:** Close it in the spec as `[AGENT]` (orchestrator, 2026-10-04): the historical contract was never implemented and is narrowed to IDs present in the registry file. State the limits plainly, one line each:
- Deleted IDs are not protected.
- Archived IDs are protected only while the registry file still names them (L1-4).
- WI IDs also live in directory names (`work/active/WI-NNN_*`, `work/completed/*_WI-NNN_*`). A reused WI ID makes `resolve_work_item` raise on ambiguity (`state.py:155-180`). The narrowed guarantee does not cover those directories.

### Lens 4 — Hygiene

**L4-1 · Rewrite request:** Three small fixes:
- The header's `**Branch:** harness-right-size` is stale; the branch is `pm-registry-integrity`, cut from `main` at `9b82006`.
- Next Steps says `$my-design`, which is Codex syntax; in this repo it is `/_my_design`.
- Related Artifacts should add `operations.py:1148` (the second splitter) and `operations.py:155` (the backlog writer).

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** A reader can't tell from the spec that there are two separate defects with different evidence, or that each registry is exposed differently. Criterion 3 packs the contract, the evidence, and a behavior rule into two sentences. Ask the spec agent to:
- Open the Problem with the two defects, one line each.
- Add the per-registry exposure summary (L2-1).
- Split criterion 3 into the contract (L3-1) and the evidence that proves it (L3-6).

---

## Engagement Summary

**Overall take:** The spec aims at the right defect, but as written it would ship a fix that still loses data. The status-update splitter would corrupt the very row this item rescues. The backlog writer would keep deleting records whose IDs are now "protected." And the core contract is loose enough that design could pick a reading that misses fusion-tea's real archive-driven reuse. All of this is fixable with edits.

**Here's what I need you to weigh in on:**

1. **[L3-1, L1-4]** Pin "present" to any same-prefix ID token in the registry file outside HTML comments. This matches ratified check 4's wording, keeps the existing tests green, and protects fusion-tea's archived DI, PR, and AD ranges for as long as the archive notes exist. Escalate to the owner only if you want a persistent high-water mark instead.
2. **[L2-2]** Keep the WI writer in scope (option A). Ratified check 2 already requires it, and today `add-item` erases the whole backlog when its YAML is broken.
3. **[L3-2]** Add the second splitter (`update_validation`, `operations.py:1148`) to scope. Without it, the next status update on fusion-tea's `SV-035` corrupts it while reporting success.
4. **[L3-3]** Promote "what the tool writes reads back identically" from an open question to a success criterion. The mechanism stays in design.
5. **[L3-6, L3-5]** Absorb checks 1 to 3 as evidence, graded `[INFERRED]` (ratified). Mark check 4 and the snapshot as verification the orchestrator runs. Reword check 3 to allow SV-035's warning to disappear and to allow new diagnostics. Make criterion 4 concrete.
6. **[L1-1, L1-3]** Correct the Problem facts: on the real file `SV-034` is malformed and `SV-035` is escaped, the real file shows row loss but not reuse, and the AD case is latent, not live.

---

## Resolutions

Recorded by the orchestrator, 2026-10-04. Every call below is `[AGENT]`-grade unless marked otherwise. The owner reserved no gates and asked to be consulted only on an unexpected issue needing their judgement; none of these meets that bar, reasoning given where it was close.

- **L1-1 — Accept.** Rewrite Problem with the two defects separated and the corrected `SV-034`/`SV-035` facts. Keep the fixture's reversed labels and say so.
- **L1-2 — Accept.** Cite both the original 2026-08-21 Goal and the 2026-10-04 rewrite; grade "native representation" `[INFERRED]`.
- **L1-3 — Accept.** The AD case is latent (refused write), not live. Cite it as structure drift. Live exposure on fusion-tea today is SV, DI, WI.
- **L1-4 — Accept the proposed resolution; not escalated.** Reading (c) from L3-1 protects the archived ranges for as long as the registry file names them, which is the conservative outcome (a gap, never a reuse) and the one that keeps the cited "archived DI-014" unambiguous. This does not reverse the no-high-water-mark decision: the guarantee is still bounded by the file's contents. A persistent high-water mark would be new machinery for a case the archive notes already cover; if fusion-tea later deletes those notes, that is a fusion-tea decision about its own namespace. Spec adds the one-line limit.
- **L2-1 — Accept.** Put the per-registry exposure table in the spec. Check-2 fixtures for PR, G, AQ drop their row by a decorated ID cell, not an escaped pipe.
- **L2-2 — Accept option A (keep the WI writer in scope).** Outcome: no PM write deletes or alters an existing record; when the tool cannot keep a record it refuses and names it. Steer for design, not a spec rule: malformed YAML must refuse; a record with an invalid field may be carried forward raw or refused, design chooses. The ratified check 2 requires this, and the 2026-02 operations spec already promised it.
- **L2-3 — Accept.** Reword OQ1 to name both mechanisms neutrally; design chooses.
- **L2-4 — Accept.** Complexity stays MEDIUM. The orchestrator updates the backlog Effort line when tracking is next touched; the spec session does not edit the backlog.
- **L3-1 — Accept reading (c).** Contract: a newly minted ID is numerically greater than every same-prefix ID token that appears in the registry file outside HTML comments, whether or not the parser accepted its record. A token stands alone (`MAG-001` is not `G-001`; code spans count). Strictly above the max, no gap filling. Record the two costs (prose mention skips numbers; comment-only IDs are unprotected) and the `PR-1`/`PR-001` convention note.
- **L3-2 — Accept.** New criterion: every operation that reads or rewrites a registry table row applies the same escape rule, and updating a row changes only the targeted cell. Test on an escaped row.
- **L3-3 — Accept.** New criterion: a value written by any PM add operation reads back identical through the parser. Mechanism stays in design.
- **L3-4 — Accept.** Splitting follows GFM table behaviour including inside code spans; `\\|` behaviour is chosen in design and pinned by a test.
- **L3-5 — Accept** the five concrete points for criterion 4.
- **L3-6 — Accept.** Checks 1 to 3 enter as evidence requirements graded `[INFERRED] (ratified by owner, 2026-10-04: "those hold. proceed.")`. Check 4 and the snapshot half of check 3 are orchestrator-run verification recorded in the audit, not CI. Check 3 allows SV-035's warning to disappear and allows new diagnostics. Check 2 allows whitespace separators and, for WI, depends on L2-2.
- **L3-7 — Accept.** Close OQ3 as `[AGENT]` (orchestrator, 2026-10-04) with the three one-line limits (deleted IDs; archived IDs; WI directory names).
- **L4-1 — Accept** all three.
- **L5-1 — Accept.**

A second, bounded spec review runs after the revision because the contract changed and scope grew.

---

**Verdict:** Revise
**Next Steps:** The orchestrator records resolutions above, then runs `/_my_spec` in a fresh session pointed at this review to incorporate them. The reviewer does not edit the spec. Because the revision adds scope (L2-2, L3-2, L3-3) and changes the core contract (L3-1), a short second spec review is worth running before design.
