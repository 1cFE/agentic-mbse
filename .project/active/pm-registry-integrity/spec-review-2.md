# Spec Review (round 2, bounded): Escaped Pipes and Registry ID Integrity

**Spec:** `.project/active/pm-registry-integrity/spec.md` at `1680e06`
**Round 1:** `spec-review.md` (all findings accepted)
**Brief:** `briefs/spec_review_2.md`
**Review File:** `.project/active/pm-registry-integrity/spec-review-2.md`
**Date:** 2026-10-04

**Evidence used.** Code at HEAD (unchanged since `9b82006`). fusion-tea copies at `.orchestrate-logs/ft-snapshot/`. The round-1 probe reruns at HEAD and reproduces probes 1–5. One new probe, `.orchestrate-logs/spec-review-scratch/sr2_probe.py` (gitignored), compares per-file token maxima with parsed and record-shaped maxima on the fusion-tea copies.

---

## Reality Check

**Sound.** The revision applied every round-1 resolution, and its code-facing claims hold. Two gaps remain, and both sit in the new contract. Criterion 4's deciding case has no evidence, so a weaker design passes every check. And one design option for the WI writer cannot pass the owner-ratified E2. Both are bounded text edits.

---

## Q1 — Fidelity of the revision

**Every resolution applied as recorded:** L1-1, L1-2, L1-3, L1-4, L2-1, L2-2, L2-3, L2-4 (MEDIUM kept, backlog untouched), L3-1 through L3-7, L4-1, and L5-1.

- **Provenance.** No `[NEED]` or `[HARD]` appears. The ratified grade on E1–E4 is exact. Each `[AGENT]` item carries its reasoning in one line.
- **No compensating prose.** Corrected facts were replaced, not annotated. The three Non-Goal limits and the Decisions entry read as decision records.
- **Per-registry table checked against the code.** Every "dropped by" cell matches the parse functions (`parser.py:93-130`, `:251-465`, `:468-784`). Every "writes" cell matches the operations (`operations.py:213-245`, `:404`, `:446-470`, `:530`, `:770`, `:795`, `:923`, `:1008`, `:1107`, `:1148-1168`). Two cells are slightly loose; see N4.
- **Citations checked.** All of these hold: `operations.py:58`, `:63-67`, `:70`, `:155`, `:194`, `:199-210`, `:446-451`, `:461-468`, `:514`, `:1148`; `parser.py:109`; `state.py:193`; fusion-tea `KNOWLEDGE.md:11` and `REQUIREMENTS.md:65`; the d4.4 spec `:73`; the status report `:64`.
- **Splitter coverage is complete.** `parser.py:109` and `operations.py:1148` are the only pipe splitters in `src/`.

---

## Q2 and Q3 — Findings

**L3-1 · Direct claim (must-fix): no evidence check exercises criterion 4's deciding case, and a weaker design passes them all.**

Criterion 4 counts every same-prefix token in the file. Open Question 1 also lets design choose "per-format detection of record-shaped text." The two differ only on tokens that are not record-shaped. fusion-tea's archive notes are exactly that kind of token. On the fusion-tea copies:

- `KNOWLEDGE.md`: parsed max and heading-shaped max are both `DI-011`. The whole-file token max is `DI-014`, from the archive note at `:11`.
- `REQUIREMENTS.md`: heading-shaped max is `PR-5`. The token max is `PR-007`, from the archive note.

So a record-shaped design mints `DI-012` on fusion-tea's live `KNOWLEDGE.md`. That duplicates archived `DI-012`, and it is two mints from `DI-014`, which `REQUIREMENTS.md:65` cites by spelling. The whole-file rule mints `DI-015`.

No evidence check would catch the record-shaped design:

- E1 and E2 put the max ID in a record-shaped failing record.
- E3 snapshots parse output, not allocation.
- E4's matrix has its token max equal to its row max (`SV-135`).

OQ1's guard ("Either must meet the criterion, including drifted structure…") names drift but not prose mentions. So a designer can believe per-format detection qualifies.

**Proposed resolution** (adds evidence, leaves E1–E4 as ratified):

- Add one test to criterion 4's Evidence line. The fixture holds records `DI-001`…`DI-011` and an archive note naming `DI-014`. The next ID is `DI-015`.
- Add to the E4 clarification: the orchestrator also records the next DI on the `KNOWLEDGE.md` copy, expected `DI-015`.
- Extend OQ1's "must meet" clause to name prose mentions such as fusion-tea's archive notes alongside drifted headings. Whether to drop the per-format option then is the orchestrator's call.

**L3-2 · Direct claim (must-fix): OQ3's "refuses" option cannot pass the owner-ratified E2.**

E2's WI case needs a fixture whose highest ID sits in a work item that fails parsing. `add-item` must mint above it, and the diff must be exactly the one new record. Malformed YAML must refuse (orchestrator steer), so the fixture's failing record has to be an invalid-field work item.

OQ3 lets design refuse on an invalid-field work item. If design takes that option, `add-item` refuses on E2's fixture and E2 cannot pass. The contradiction came in through round-1's L2-2 resolution: it says both "check 2 requires this" and "design chooses." The spec copied it faithfully.

**Proposed resolution:** narrow OQ3. E2 requires the backlog writer to carry forward at least the invalid-field work item its fixture uses, such as an invalid `status`. Design still chooses:

- how to carry it (raw text or a preserved YAML node);
- which other failures refuse (an invalid epic, a non-mapping entry).

Malformed YAML still refuses. Nothing is relitigated: the owner-ratified check outranks the `[AGENT]` steer.

---

## Nits

The orchestrator can apply these directly.

- **N1 (recommended): a refusal changes no file.** Criterion 5 says a write "refuses with an error." `close_item` rewrites the `spec.md`, `design.md`, and `plan.md` frontmatter and moves the directory to `completed/` before it writes `BACKLOG.md` (`operations.py:1078-1107`). Refusal logic placed in the shared writer (`:155`) would refuse after those side effects. The item would be left half-closed, and a retry fails with "not in work/active/". Add to criterion 5: a refused write leaves every file unchanged.
- **N2: what E2's WI diff means.** `BACKLOG.md`'s body is a dashboard re-rendered from frontmatter on every write (`project_templates/BACKLOG.md.template:8-14`). Adding an item also adds a body row. A carried-forward record may also drop out of the rendered body. Add one `[AGENT]` clarification: for WI, E2's "exactly the one new record" is judged on the frontmatter, and the body is re-rendered from the kept records.
- **N3 (optional): criterion 3's scope is wider than its evidence.** "Any PM add operation" includes DI, AD, and WI writes. There, a multi-line value does not read back identical: continuation lines are joined with a space (`parser.py:179-181`). The evidence covers only the four table registries. Either narrow the criterion to table registries or add heading and frontmatter cases. Narrowing matches the Problem.
- **N4 (optional): two loose table cells.**
  - SV, escaped pipe: "Type check fails" holds when the pipe sits before the Type column. A pipe in a later column fails a later check instead.
  - G and AQ, writes: `register_intent` inserts one row per goal or question, not one row per call.

---

## Engagement Summary

**Overall take:** The revision is faithful, and the table and citations check out against the code. The new contract is right, but as written it can be met on paper by a design that still reissues fusion-tea's archived `DI-012`. One ratified check also conflicts with an open design option. Both are small edits.

**Here's what I need you to weigh in on:**

1. **[L3-1]** Add a prose-only-max test to criterion 4's evidence (archive note naming `DI-014` above records to `DI-011`, next ID `DI-015`). Have the orchestrator record the next DI on the fusion-tea copy. Name archive notes in OQ1's "must meet" clause.
2. **[L3-2]** Narrow OQ3: E2 requires carrying forward the invalid-field work item its fixture uses. Design chooses the mechanism and which other failures refuse. Malformed YAML still refuses.
3. **[N1]** State that a refused write leaves every file unchanged, so `close_item` cannot half-close an item.

---

## Resolutions

Recorded by the orchestrator, 2026-10-04, and applied directly to `spec.md` in the same commit. All `[AGENT]`-grade; none escalated.

- **L3-1 — Accept.** Archive-note test added to criterion 4's evidence; E4 clarification records the next DI on the `KNOWLEDGE.md` copy (expected `DI-015`); OQ1 now steers to the whole-file scan and names prose mentions as a case any alternative must meet.
- **L3-2 — Accept.** OQ3 narrowed: carrying forward the invalid-field work item is required because E2 needs it; design chooses mechanism and which other failures refuse; malformed YAML refuses.
- **N1 — Accept.** Criterion 5 now says a refused write leaves every file unchanged, with the `close_item` ordering cited.
- **N2 — Accept.** E2's WI case is judged on frontmatter; body is re-rendered.
- **N3 — Accept narrowing.** Criterion 3 covers the four table registries.
- **N4 — Accept** both cell fixes.

---

**Verdict:** Approve, conditional on applying L3-1 and L3-2 before design. Both are bounded text edits the orchestrator can apply directly. They need no third review. N1 is recommended; N2–N4 are optional.
**Next Steps:** The orchestrator records resolutions and applies the accepted edits to `spec.md`, then runs `/_my_design`.
