# Audit: goal-layer-port (`WRAP-SPLIT` Item 2)

**Verdict:** Certify with follow-ups
**Audited:** 2026-10-12
**Branch:** `goal-layer-port` (base `33511c4`)
**Commit:** `7429aa9`

---

## The Point

agentic-mbse ships general capability that a target gets from `init`. This item owes three things.

- **A working goal layer for every target.** A fresh target grounds a goal and runs rounds from installed files alone, with nothing pointing at fusion-tea. Authority: [OWNER] "Goals are general to the systems-engineering and concept-development process" (fusion-tea concept `:198`).
- **The design-choice rule at the right level.** [OWNER-VERBATIM] 2026-10-11: "it is important that you find the right level for this rule -- we have specific patterns which agentic-mbse is supposed to enforce, this should fit into that". The principle is [OWNER-VERBATIM] 2026-09-20: "As soon as you start introducing 'sizing', then you are basically pre-defining which design parameters are 'free' and which are 'derived'. this is explicitly what we wanted to avoid." fusion-tea's MR-7 becomes that project's application of the shipped rule.
- **fusion-tea loses nothing.** [INHERITED: epic, OWNER 2026-10-06] Every consumer-specific line left out of the shipped copies has a fusion-tea home before the agentic-mbse change merges, and [INHERITED: epic `:66`, OWNER, amended by Align] MR-7 enforcement survives a re-init without a kept edit to a tool-owned file.

## Summary

The work delivers all twelve success criteria. The rule is a normal agentic-mbse pattern: one reference doc beside Equality intent, one "Process Selection" row, one point-of-use row, and pointers. The goal files are a true port: I regenerated every diff against the fusion-tea snapshot and each hunk fits a permitted class. The test suite passes, and no touched file adds a lint or type finding. Seven advisory findings remain. None blocks; the first two are worth fixing before the rule's routing drifts.

## Product Judgment

**Yes, this is the right piece of work, and it answers the owner's central direction.** The rule reads as one of agentic-mbse's own patterns:

- Its full statement is `docs/patterns/design-choices.md`, shaped like the other pattern docs (rule, validated SysML pair, examples, common mistakes, related patterns, verification). Its SysML is a test-checked excerpt of a fixture that passes all six validation levels in both the right and wrong forms.
- It is reached the way every construct rule is reached: "Process Selection" routes the change to review (`project_templates/MODELING_PROCESS.md.template:24`), the point-of-use table names the reference (`:76`), and the stage skills reach both through sections they already read. I checked each reach-trace hop against the skill text.
- It names Equality intent as its sibling both ways, and Equality intent's text and authority stanza are untouched.
- It names no requirement number, rubric or fusion term. The fresh dry-run agent read it unprompted and recorded the pump's installed capacity as a supplied choice to preserve.
- It keeps MR-7's force. I compared MR-7 (`REQUIREMENTS.md:91-107` in the snapshot) sentence by sentence with the pattern: every MUST and must survives, including "cannot count".

**Product-lens (this audit, appended to `product-lens.md`): gate DISPOSED, no owner-grade contradiction.** Its two findings:

- audit-F1 (the runbook depends on the study record's "§ 15"): still true in the code. It is advisory finding 4.
- audit-F2 (runbook `:101` and `:140` restate obligations in other words): checked and not a finding. Spec SC5(a) classes "what to record and what to carry into briefs" as procedure, not a second statement. SC12 also forbids rewriting those hooks beyond the hook class. Its sub-point, that the runbook trigger row has already narrowed, is true and is advisory finding 1.

**Earlier lens blocks.** The spec gates closed CLEAR. The design gate closed DISPOSED, and every disposition is in the code: the SysML pair and Verification section (`design-choices.md:49-130`), the ADR-002 line (`:121`), a grade paragraph that names no path (`:134`), "every supported execution route" (`:36`), § Review naming "Process Selection" without restating the trigger (`:41`), and the amendment clause (`docs/goal-layer-decisions.md:9`). No `BLOCK` is open.

**Structural smells.**

- *Two representations kept in step by hand:* fired. The runbook's trigger row mirrors the "Process Selection" row. The spec's L2-2 call asked for this row, so it is inherited, but the mirror has already narrowed (finding 1).
- *Correctness depends on another component's internal layout:* fired, weakly. "§ 15" (finding 4).
- *A test passes only because it picks one route:* not fired.
- *A special category exempts an unchanged case:* not fired, but see finding 5 on the exemption's scope.
- *A compatibility requirement preserves contradicting behavior:* not fired.

**One decision for the owner at merge.** fusion-tea commit `1b8d6fbff` on `goal-layer-mr7` edits narrative files, which the spec's Non-Goals keep unchanged. I confirmed it changes 21 link targets and nothing else (`.project/active/demo-depth-rubric/` → `.project/completed/20261011_demo-depth-rubric/`). It repairs links that fusion-tea `main`'s own archive (PR #122) broke after the snapshot. Without it, both narrative checks fail, on `main` as well. The orchestrator surfaced it and kept it as a separate commit. The owner decides whether it rides with `goal-layer-mr7` or goes to `main` alone.

## Blockers

None.

## Advisory

Ranked by importance. All are advisory.

1. **The goal runbook's trigger row has already drifted from the row it mirrors.** `project_templates/GOAL_RUNBOOK.md.template:74` drops the definition that `MODELING_PROCESS.md.template:24` carries: "(a quantity moves between chosen and calculated, or a design choice leaves the public interface)". A goal coordinator checks the runbook table at the disposition checkpoint (`:165`). They may not read "a design choice leaves the public interface" as a trigger. The pin `tests/test_modeling_command_contracts.py:148` checks one phrase, so further drift passes. The text is design A8's, not an implementation slip. *Change:* carry the parenthetical, or have the row name the "Process Selection" design-choice row as its source; pin the scope phrases in both rows.
2. **The contract pins check that the rows exist, not what they require.** `tests/test_modeling_command_contracts.py:124` passes as long as some row names "Changed design-variable role" and `design-choices.md`, even if the row stopped requiring review. SC5(f) is met, because removing the row fails. *Change:* also assert "independent design review" in both trigger rows.
3. **`spec-model` meets the rule only at the narrow review scope.** It reads only "Process Selection" (`skills/spec-model/SKILL.md:15`), not the point-of-use table. Yet the pattern gives the spec stage a duty: "The spec names the design choices the consumer must keep" (`docs/patterns/design-choices.md:34`). A spec for a demand-based cost or an operating-point closure with no role change never meets the rule at spec time. SC5(d)'s two-hop route exists, so this is not a gap against the SC; the spec itself flagged `spec-model` as a likely gap. *Change:* add a one-line pointer to `spec-model`, or record why it is not needed.
4. **The runbook depends on a study-record section number.** "a committed record's § 15" (`project_templates/GOAL_RUNBOOK.md.template:261`, `:271`) points at nothing in a target with no study layer. With Item 3's study layer, it depends on that template's numbering. It was ported verbatim, so it is within SC12. *Change:* Item 3 or Item 4 names the section by its role ("the record's findings section").
5. **The no-fusion test exempts lines by a string, not by file.** `tests/test_goal_layer.py:73` skips any line holding `@2b1e9f9d5` in all eight goal files. So a runbook line citing "fusion-tea@2b1e9f9d5" as authority would pass. *Change:* limit the skip to `docs/goal-layer-decisions.md`.
6. **The dry-run record misstates how the agent found the pattern.** `evidence/dry-run/install.md:18` and `plan.md:839` say the agent "ran no resolver command". But `evidence/dry-run/read-files.txt:5` shows it ran `get_docs_dir()`, then read the pattern under that path (`:6`). The B1 conclusion holds, and is stronger. *Change:* correct the sentence at close.
7. **The pattern names a fixture a target cannot open.** `docs/patterns/design-choices.md:51` says "Reference fixture: agentic-mbse `tests/fixtures/sump_pump/`", but the wheel ships no `tests/`. The excerpts are inline, so nothing is lost. *Change:* say "in the agentic-mbse source repository", or drop the sentence.

Already filed for close in `evidence/README.md:31-34`: the dev-mode ignore-marker gap (an existing `--dev` target never gets the three new ignore lines), and a per-design listing of literal versus bound attributes.

## Findings Detail

### Plan completion

P1–P8 are complete. Each phase's tests exist and pass, and its commit is on the branch. O0–O3 are complete per their progress notes, and every output they name is in `evidence/`. F2 runs after the merge (design D13) and is outside this audit. The deviations the plan records are sound:

- the `model-validation` bullet's position;
- the A3 line kept unwrapped in a hard-wrapped file;
- the resolver command's quotes unescaped, because the escaped form is a SyntaxError;
- the path check widened beyond the stencil, with a mutation check;
- the SC5(a) pin following `f454835`'s "cannot count";
- MR-7's "MUST apply";
- F1 re-cut from fusion-tea `b06585709`.

No placeholder, TODO or dead text in the added lines.

### Spec conformance

- **SC1 met.** I ran `install-commands --list`: it names both skills. A fresh `init --assistant both` into a scratch folder created both bundles, the runbook, three templates, the narrative test, `work/orchestration/goals/` and `work/narratives/`. `tests/test_goal_layer.py:94-114` covers `claude`, `codex`, `both` and `--dev` (links plus ignore lines).
- **SC2 met.** I ran SC2's grep over that fresh install: no output. `.project/` appears only in the two-PM "for example" lines (runbook `:13`, record `:13`). The goal text names ADR-0001..0007 only, and the record carries all seven. The record's own hits all carry `@2b1e9f9d5`, as provenance.
- **SC3 met.** `test_installed_goal_references_resolve` and `tests/test_shipped_text.py` pass. Both resolver-reached documents exist, and `tests/test_packaged_guidance_contract.py:109` checks them in the wheel. The installed narrative test passes in the fresh target with no narratives.
- **SC4 met, on evidence.** The orchestrator ran it; I did not rerun it. `dry-run/goal.md` reads `grounded`, fills all five classes and cites the seed at `e24e41c`. `dry-run/trail.md:9,11,21,32` has the four headings. The read list includes `design-choices.md`. The wheel predates one phrase change in `MODELING_PROCESS.md.template` (`git diff 57a61c8 HEAD`), which no check uses.
- **SC5 met.**
  - (a) Only the pattern states the obligations (pinned at `tests/test_modeling_command_contracts.py:174`). Other mentions are pointers, one-line rows or goal procedure.
  - (b) Routing: `MODELING_PROCESS.md.template:24` and runbook `:74`.
  - (c) The point-of-use row is at `:76`.
  - (d) I checked each trace hop against the skill text.
  - (e) The tier text is at `skills/requirements-tracking/SKILL.md:24,38,41,43,134`.
  - (f) Seven pins pass, and the reverted edit is in evidence.
  - (g) The pattern names no project authority (`:193` pin; my grep agrees).
  - (h) The `constraints.md` and `sysml-conventions` diffs each add one line plus a blank, delete nothing, and leave Equality intent's text unchanged.
- **SC6 met.** The crosswalk covers every source sentence, with grades. Design review rounds 1 and 2 and the O1 delta check are fresh reviews. My own comparison found no lost modal force.
- **SC7 met, as far as I can see.** In the branch diff, MR-7 cites the pattern through the resolver, keeps its heading and authority line, and keeps the conductor and depth application. Every added and context line of the four tool-owned files in the diff is in this repo's templates. The rehearsal manifest hashes equal this tree's template hashes. I cannot read fusion-tea itself.
- **SC8 met, as far as I can see.** In the rehearsal outputs:
  - all six manifest entries match;
  - nothing changed under the goal and narrative directories;
  - `tests/orchestration` reports 3 passed;
  - all 16 H2 headings are kept;
  - the chain walk resolves.

  The resolver hop ran from this tree, matching SC8's "init from this item's tree". The proof in fusion-tea's own environment is F2 step 5, after the merge.
- **SC9 met.** The ledger's Item 2 section has 17 rows, each with a home, plus the merge order. Every deletion hunk in SC12 names one of these rows.
- **SC10 met.** The record has seven entries. Each quotes its fusion-tea frontmatter provenance verbatim (I checked against the snapshot) and cites `<path>@2b1e9f9d5`. The runbook gives the resolver at `:296`.
- **SC11 met at `main`'s parity.** `uv run pytest tests/`: 2215 passed, 1 skipped, 1 xfailed (run 2026-10-12). Ruff reports 118 and mypy 88 across the tree, with none in a touched file. The five touched Python files pass `ruff format --check`.
- **SC12 met.** I regenerated the diffs against the snapshot: 10, 4, 21, 1, 1, 0 and 4 hunks. Each is a consumer path, design-choice hook, decision-record citation, recorded practice, envelope or ledgered deletion. No method list, limit value or H2 heading changed.

Non-goals respected: no validator change, no Equality intent rewrite, no study or research-seam code, and fusion-tea ADR files untouched. The one exception, fusion-tea narrative data, is the owner decision under Product Judgment.

### Design conformance

The implementation follows D1–D17 and Invariants 1–8. The template rows, sibling lines, tier text, stage pointers and goal hooks match Appendix A, with the plan's carried edits. The goal files sit at fusion-tea's paths as tool-owned templates (D8). The narrative test uses `.absolute()` and a distinct basename (D9), and its `--dev` mutation check is recorded. The decision record is resolver-reached (D7). No undocumented deviation.

### Code integrity

- The installer change (`src/agentic_mbse/cli/__init__.py:45-49,67-69,510-511`) is five template entries, three ignore lines and two directories. It follows the surrounding style and needs no `Installer` change.
- The tests are focused, and the plan records a mutation check for each key one.
- Findings 2 and 5 are precision gaps in the tests.
- No silent fallbacks or broad excepts.

---

## Certification

Checked and marked:

- **Spec:** SC1–SC12 checked off.
- **Plan:** the shared-check boxes and the O0–O3 boxes checked off, each on its captured output; P1–P8 were already checked. Two boxes stay unchecked because they leave no output I can read: O1's fusion-tea "Preconditions" (`plan.md:733`) and O2's worktree removal (`:779`).
- **Epic:** Item 2's heading gets ✅, and every success criterion except one is checked. The exception is "MR-7 is byte-identical", which the owner's 2026-10-11 direction superseded; it stays unchecked with a note.
- **CURRENT_WORK.md:** the item reads "certified".

**Not checked:**

- fusion-tea itself. I saw it only through the snapshot at `2b1e9f9d5`, the captured branch diff and the rehearsal outputs.
- The dry run. I read its outputs and did not rerun it.
- F2 (pin move, re-init, resolver hop in fusion-tea's own environment). It runs after the merge.
- Codex runtime behavior beyond installation.
- `main`'s ruff and mypy counts. I took 118 and 88 from the plan; I confirmed only that touched files add none.
- The contents of `.codex/agents/*.toml`.
