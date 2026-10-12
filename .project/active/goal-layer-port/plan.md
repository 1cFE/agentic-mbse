# Implementation Plan: goal-layer-port (`WRAP-SPLIT` Item 2)

**Status:** Implementation in progress (P1–P7 done)
**Created:** 2026-10-11
**Last Updated:** 2026-10-11

## Source Documents

- **Spec:** `.project/active/goal-layer-port/spec.md`
- **Design:** `.project/active/goal-layer-port/design.md`, approved in round 2 of `design-review.md`. The exact texts are its appendices: A (texts), B (line changes), C (ledger rows), D (fusion-tea work), E (reach trace), F (fixture model). This plan sequences them and does not restate them.
- **Review and calls:** `design-review.md` (rounds 1 and 2, and the Resolutions); Align record `briefs/align.md`; this stage's brief `briefs/plan.md`.
- **fusion-tea sources:** `.orchestrate-logs/fusion-tea-snapshot/` in this worktree, a read-only copy of fusion-tea at `2b1e9f9d5` (gitignored). "fusion `:N`" below means a line in that snapshot. Implement sessions read fusion-tea only there; they never open `/home/reid/1cfe/fusion-tea*`.

## The Point

agentic-mbse ships general capability that a target gets from `init`. This item owes two things, and one constraint on how fusion-tea gets there.

- **A working goal layer for every target.** A fresh target grounds a goal and runs rounds from installed files alone, with nothing pointing at fusion-tea. The authority for shipping it to every target is [OWNER] "Goals are general to the systems-engineering and concept-development process" (fusion-tea concept `:198`).
- **The design-choice rule at the right level.** [OWNER-VERBATIM] 2026-10-11: "it is important that you find the right level for this rule -- we have specific patterns which agentic-mbse is supposed to enforce, this should fit into that". The principle it generalizes is [OWNER-VERBATIM] 2026-09-20: "As soon as you start introducing 'sizing', then you are basically pre-defining which design parameters are 'free' and which are 'derived'. this is explicitly what we wanted to avoid." The owner will judge the item by whether the rule reads as one of agentic-mbse's own patterns.
- **fusion-tea loses nothing.** [INHERITED: epic, OWNER 2026-10-06] Every consumer-specific line left out of the shipped copies has a fusion-tea home before the agentic-mbse change merges. [INHERITED: epic `:66`, OWNER, amended by Align] MR-7 enforcement survives a re-init without a kept edit to a tool-owned file.

## Carried into this plan

**From design review round 2, plus one orchestrator call.** Apply these as written; each changes a design text.

1. `design-choices.md` takes MR-7's own force in three sentences (round 2, the reviewer's own round-1 miss):
   - rule 7: "A supplied equipment choice must remain the basis of its represented inventory and cost."
   - Acceptance: "An unsupported-domain case must remain explicitly unsupported, with no manufactured success."
   - Acceptance: "A review must record compliance for the affected scope as compliant, violated or unverified, with evidence."
2. [AGENT] (orchestrator call, plan brief) The template's `:59` seed sentence forbids one direction only, as MR-7 does. The whole sentence becomes: "Distinguish quantities with different meanings, such as installed capacity and operating demand, and do not set installed capacity, equipment, or inventory from demand; see `design-choices.md` (Technical Patterns below)." This replaces A2's "do not set one from the other", which also forbade setting an operating point from installed capacity. The SC6 crosswalk records the call.
3. Verification step 1 gains, after "A supplied value passes.": "An identity over supplied values, such as `volume = area * length`, passes." (R2-A3)
4. A `---` line, with a blank line on each side, goes before the closing grade paragraph of `design-choices.md`. (R2-A4)
5. Dry run: `mkdir` the target before `init` (R2-A1). Set `VIRTUAL_ENV` as well as `PATH`, and check the agent's first resolver call in the transcript (R2-A2, unverified by the reviewer).

**Found while planning.** None changes a design decision.

- fusion `GOAL_RUNBOOK.md:304`, the ADR-0006 row, says "Citing `.project/` by path and digest". Appendix B misses it, and SC2 allows `.project/` only in the two-PM wording. P3 rewords it (class: consumer path, two-PM).
- No existing test proves that a new `docs/` file reaches the wheel. The wheel's `docs` comparison is a strict xfail for an unrelated gap (`tests/test_packaged_guidance_contract.py:38-42`). P5 adds one assertion, and O3 lists the wheel.
- D6 puts the SC6 crosswalk in the commit that adds `design-choices.md`. So it lands in P2, not with the later evidence. P7 re-checks its goal-hook rows against the ported text.
- The wheel-installed CLI cannot find this worktree's `.env`. `load_dotenv()` (`src/agentic_mbse/cli/__init__.py:302`) searches upward from the installed module's folder, not the working directory. O0 and O3 pass `SYSIDE_LICENSE_KEY` in the environment and never write it into evidence.
- Equality intent's stanza ends a paragraph (`docs/patterns/constraints.md:64-69`, `skills/sysml-conventions/SKILL.md:210-211`). Each A3 line goes in as its own paragraph: the line plus one blank separator, no other change. SC5(h) reads "only cross-reference lines"; a blank line carries no content.

## Implementation Strategy

**Phasing rationale.** The fixture comes first because it is both the pattern's validated example and the dry-run seed (D16). The rule's placement comes next, because the goal hooks point at it. The port follows, then the installer, which makes the ported files real in a target. The decision record and the resolution checks follow, because the port names the record. The contract pins come once every pinned line exists. The evidence phases come last in this repo, so they read final text. The orchestrator's fusion-tea and dry-run phases follow, because they copy or install that final text.

**Critical path.** P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8 → O1 → O2. O3 needs P1–P8 but not O1 or O2, so it can run beside them. After the owner merges agentic-mbse, F2 runs from the runbook P8 writes.

**First proof point.** P1's kept test passes all six validation levels on the three fixture trees in place. The riskiest proofs follow: the `--dev` narrative-test run in P4 (D9), the SC12 hunk classification in P7 (the port is a port), and in O3 whether a fresh agent reads `design-choices.md` unprompted (B1).

**Each agentic-mbse phase:**

- is sized for one fresh implement session, because a resumed session cannot commit;
- writes its tests first;
- ends with the shared checks below and exactly one commit.

**Shed list** (spec L3-9), if the budget runs out: (1) write the decision record as a table (P5); (2) stage-skill pointers already follow the trace only (D4, P2); (3) leave the `orchestrate-modeling:57` line to Item 4 (P4). The placement checks, the fusion-tea no-loss evidence and the dry run are never shed.

### Shared checks

Run from the worktree root. Every agentic-mbse phase ends with:

- [ ] `uv run pytest tests/` → all pass, no new xfail
- [ ] `uv run ruff check src/ tests/` → clean
- [ ] `uv run mypy src/` → clean
- [ ] From P3 on, the SC2 grep over the goal-layer files that exist so far → no output:

```bash
SC2='fusion-tea|MR-[0-9]|\.codex-test|stellarator|exploration/|\.claude/|/home/|research_seam|source_registry|integrate\.py|STUDY_POLICY|holdout|ARIES|aries-cs|demo-depth-rubric|depth target|GSTH|WI-0[0-9]'
GOAL_TEXT="skills/run-goal/SKILL.md skills/narrate-goal/SKILL.md project_templates/GOAL_RUNBOOK.md.template project_templates/goal.md.template project_templates/trail.md.template project_templates/learnings.md.template project_templates/test_narrative_links.py.template docs/goal-layer-decisions.md"
grep -nE "$SC2" $GOAL_TEXT 2>/dev/null | grep -v '@2b1e9f9d5'          # → no output
grep -n '\.project/' $GOAL_TEXT 2>/dev/null | grep -v '@2b1e9f9d5'     # → only the two-PM "for example" wording
```

Lines carrying `@2b1e9f9d5` are provenance citations in the decision record, which SC2 exempts.

**Orchestrator note (after P2, 2026-10-11).** The worktree venv now has every extra (`uv sync --all-extras`, matching the main checkout); with it the full suite passes (2192 passed, 1 skipped, 1 xfailed). `ruff check src/ tests/` (118) and `mypy src/` (98 before the extras were installed; 88 with them, re-measured after P3 with `src/` still equal to `main`) fail on `main` at `57644b9` before any change here, so SC11's lint and type checks are judged as parity with `main`, as Item 1 did: no new finding in a file this item touches, and the counts do not rise.

Evidence goes in `.project/active/goal-layer-port/evidence/` (written `evidence/` below).

---

## Phase 1: The sump/pump fixture and its kept test

### Goal

Put the Appendix F model in the repo as `tests/fixtures/sump_pump/{seed,right,wrong}/models/`, with a kept test that validates all three trees.

### Assumption under test

The three trees validated in the design session still pass all six levels when they sit in `tests/fixtures/`, and the seed has no fit check, so the dry run's goal needs a model change.

### Test stencil (write first)

```python
# tests/test_design_choices_example.py
"""The design-choice pattern's validated example and the goal-layer dry-run seed (design D16)."""
from pathlib import Path
import pytest
from agentic_mbse.validation.runner import run_all_checks

FIXTURE = Path(__file__).parent / "fixtures" / "sump_pump"

def sysml(tree: str) -> str:
    return "\n".join(p.read_text() for p in sorted((FIXTURE / tree).rglob("*.sysml")))

@pytest.mark.parametrize("tree", ["seed", "right", "wrong"])
def test_tree_passes_all_six_levels(tree):
    result = run_all_checks(str(FIXTURE / tree / "models"), fail_fast=False)
    assert result.total_checks == 6 and result.overall_success

def test_only_right_reports_fit_and_only_wrong_sizes_the_pump():
    assert "assert constraint pump_fit" in sysml("right")
    assert "sizing.capacity" in sysml("wrong")
    assert "pump_fit" not in sysml("seed") and "PumpSizing" not in sysml("seed")
```

### Steps

- [x] Write the test above; run it and see it fail (no fixture yet).
- [x] Copy `.orchestrate-logs/design-scratch/{seed,right,wrong}/models/` to `tests/fixtures/sump_pump/{seed,right,wrong}/models/`. If the scratch copies are missing, rebuild them from Appendix F.
- [x] Add `tests/fixtures/sump_pump/README.md` holding Appendix F's README line.
- [x] Run `uv run agentic-mbse validate tests/fixtures/sump_pump/<tree>/models --complete` once per tree. Expect all six levels green, and one admitted numerical constraint in `right/`.

### Checks

- [x] The test passes, then the shared checks (see Progress notes: no new failure; the baseline is not green).

**Commit:** `Add the sump/pump fixture: seed, right and wrong trees, validated at all six levels`

**What we know works:** the pattern's example and the dry-run seed are one validated model in the repo.

**Progress notes:**

- **Done 2026-10-11.** Added `tests/test_design_choices_example.py` and `tests/fixtures/sump_pump/{seed,right,wrong}/models/` plus `README.md`. The trees are byte copies of `.orchestrate-logs/design-scratch/` (`diff -r` silent), which match Appendix F.
- **Validation.** `agentic-mbse validate <tree>/models --complete`: all three trees pass six levels. Level 4 reports `Admitted numerical: 1` for `right/` and 0 for `seed/` and `wrong/`. The seed has no fit check, so the dry run's goal needs a model change.
- **Test, beyond the stencil.** The six-level test asserts the level list `[1..6]`, `overall_success` and no issues as three assertions, so a failure names what broke. One added test runs Level 4 on `right/` and asserts one admitted and no malformed numerical constraint: the right form's fit check is one an execution route can evaluate. The stencil's text test is kept as written.
- **Shared checks, baseline not green (pre-existing, not this item).** `uv run pytest tests/`: 18 failures before and after this phase, the same set. All come from optional extras this worktree's venv lacks: `PIL` (`tests/test_equations.py::TestDetectEquations::test_returns_detected_equations`) and `trafilatura`/`bs4` (17 in `tests/test_web_backend.py`). `uv sync --locked` reports nothing to change. `ruff check src/ tests/` reports 118 errors and `mypy src/` 98, the same counts on a clean checkout of `57644b9`; this branch has no `src/` or `tests/` diff against `main`. The new test file passes `ruff check` and `ruff format --check`. Later phases compare against this baseline.

---

## Phase 2: Place the design-choice rule

### Goal

Add `docs/patterns/design-choices.md` and reach it the way every pattern is reached: the "Process Selection" row, the point-of-use row, the `:59` clause, sibling links, index rows, the tier text and two stage pointers. The SC6 crosswalk goes in the same commit (D6).

### Assumption under test

A1's text, with the carried edits, is a pattern doc whose SysML is an excerpt of the validated fixture (Invariant 8).

### Test stencil (write first)

```python
# tests/test_design_choices_example.py, added
import re
DOC = Path(__file__).parents[1] / "docs" / "patterns" / "design-choices.md"

def test_pattern_sysml_is_an_excerpt_of_the_fixture():
    wrong, right = re.findall(r"```sysml\n(.*?)```", DOC.read_text(), re.S)
    for block, tree in ((wrong, "wrong"), (right, "right")):
        lines = {line.strip() for line in sysml(tree).splitlines()}
        for line in block.splitlines():
            if line.strip() and not line.strip().startswith("//"):
                assert line.strip() in lines, (tree, line)
```

### Steps

See `design.md` § Component Overview "agentic-mbse, rule placement" and Appendix A1–A5.

- [x] Write the test; see it fail.
- [x] `docs/patterns/design-choices.md`: copy A1 verbatim (`design.md:332-463`, the text between the `~~~~` fences). Then apply carried items 1, 3 and 4, and nothing else.
- [x] `project_templates/MODELING_PROCESS.md.template` (line numbers are before any edit, so work bottom-up):
  - the A2 "Process Selection" row after `:23`;
  - carried item 2's sentence at `:59`;
  - the A2 Technical Patterns row after `:74`;
  - the A2 `:71` semicolon.
- [x] A3, one paragraph each: in `docs/patterns/constraints.md` after `:70`, and in `skills/sysml-conventions/SKILL.md` after `:212`.
- [x] One index row each. Description: "Design choices: evaluate the supplied design; sizing and selection policies stay separate".
  - `docs/patterns/README.md`, its pattern table (rows around `:15-21`);
  - `project_templates/MODELING_GUIDE.md.template`, the Pattern Documentation Index (rows around `:288-293`);
  - `skills/sysml-conventions/references/stencils.md`, its pattern table (rows around `:87-93`).
- [x] `skills/requirements-tracking/SKILL.md`: A4.
- [x] `skills/review-model/SKILL.md`: A5 after `:28`. `skills/model-validation/SKILL.md`: A5 after `:52`.
- [x] `evidence/sc6-crosswalk.md`, the derivation record. One row per sentence:
  - Sources: MR-7 fusion `REQUIREMENTS.md:89-107`, process paragraphs fusion `MODELING_PROCESS.md:17,:34`, goal hooks fusion `run-goal/SKILL.md:53,:55`, `GOAL_RUNBOOK.md:84,:100,:139`, `goal.md:29`.
  - Columns: source sentence | shipped location (`file` § section), or fusion-tea home with a one-line reason it is fusion-only | source grade | note.
  - Goal-hook rows name their A8 destinations. P7 verifies them against the ported text.
  - A closing section lists:
    - the changes after round 2 (carried items 1–4, with their grades);
    - "before selecting a process" read as "at the point of use" (spec L3-3);
    - the fresh reviews: `design-review.md` round 1 § SC6 fresh check and round 2;
    - the pending O1 delta check.

### Checks

- [x] `grep -c 'design-choices.md' project_templates/MODELING_PROCESS.md.template` → 3 (row, clause, row).
- [x] `git diff --stat docs/patterns/constraints.md skills/sysml-conventions/SKILL.md` → 2 insertions each, 0 deletions.
- [x] The shared checks (`tests/test_shipped_text.py` covers the template as runtime-neutral text). Same baseline as P1; see Progress notes.

**Commit:** `Add the design-choice pattern and place it: Process Selection row, point-of-use row, sibling links, tier text; SC6 crosswalk`

**What we know works:** the rule has one statement and the routes the existing skills already follow.

**Progress notes:**

- **Done 2026-10-11.** Added `docs/patterns/design-choices.md` and `evidence/sc6-crosswalk.md`. Edited `project_templates/MODELING_PROCESS.md.template`, `project_templates/MODELING_GUIDE.md.template`, `docs/patterns/{README,constraints}.md`, `skills/sysml-conventions/{SKILL.md,references/stencils.md}`, `skills/requirements-tracking/SKILL.md`, `skills/review-model/SKILL.md`, `skills/model-validation/SKILL.md`. Added `test_pattern_sysml_is_an_excerpt_of_the_fixture` to `tests/test_design_choices_example.py`.
- **`design-choices.md`.** Copied byte-for-byte from `design.md:332-463`, then carried items 1, 3 and 4 as exact-match replacements. `diff` against the A1 text shows only those five changed spots (three "must" sentences, the identity sentence, the `---`). The owner quote in the grade paragraph matches fusion `REQUIREMENTS.md:89` with its curly quotes.
- **Template.** A2 rows taken from `design.md:470` and `:476` by line, carried item 2's sentence at `:59`, the `:71` semicolon. `grep -c` → 3.
- **Excerpt test.** A mutation check (changing `0.25` to `0.30` in the doc's right block, in memory) makes the test report the drifted line.
- **Deviation: `model-validation` placement.** In the file as it stands (unchanged since the design), `:52` is the "Public consumers" bullet, not the last one. I inserted the A5 bullet literally after `:52`, so it sits between "Public consumers" and "Translation" in the same evidence list. Both the design and the plan say "after `:52`".
- **Choice: A3 line in `constraints.md` is one line.** That file's prose is hard-wrapped at about 100 columns, and the brief says to match an existing file. I kept A3 as one line because Invariant 4 says the diff adds one line, this phase's check expects 2 insertions, and A3 is given as one line. Flag for the auditor if wrapping is wanted; wrapping would make the diff 5 insertions.
- **Choice: index rows sit after the `constraints.md` row** in all three tables, beside the sibling. The plan names the tables, not the position.
- **Choice: `requirements-tracking:43`.** The existing example ends at a closing quote with no period. I added the period so A4's appended sentence starts a new sentence. No other change to that line.
- **Crosswalk.** 74 rows; every quoted source sentence is checked verbatim against the snapshot, and a reverse check shows no sentence of MR-7 `:89-107`, process `:17`/`:34` or the goal hooks is left out (only MR-7's grade tag remains, carried in the grade column). Grades: the principle OWNER-VERBATIM, the enforcement request OWNER, everything else AGENT, ratified (MR-7 `:89`; fusion `modeling-intent-enforcement/spec.md:7`). `run-goal:55` is graded AGENT with a note: the snapshot has no history, so which of its sentences the 2026-09-20 change added is not recorded.
- **For P3 and P7.** Goal-hook rows name their A8 destinations by runbook section: `:84` § Grounding a goal, `:100` § Opening and closing a round, `:139` § Running one task (checked in the snapshot). P7 confirms them in the ported file.
- **For O1.** The delta check covers carried items 1–4 (listed with grades in the crosswalk's closing notes). One older wording note for the reviewer's context: Acceptance says "Unknown compliance does not count" where MR-7 says "cannot count"; both review rounds judged it kept.
- **For O2.** `MODELING_GUIDE.md.template` changed (one index row), so fusion's re-init updates `MODELING_GUIDE.md`; the rehearsal expects that.
- **Shared checks.** `uv run pytest tests/`: 18 failed, 2174 passed; the failure set is identical to P1's (missing optional extras). `ruff check src/ tests/` 118 and `mypy src/` 98, unchanged from `57644b9`. The test file passes `ruff check` and `ruff format --check`. `tests/test_shipped_text.py`, `tests/test_modeling_command_contracts.py` and `tests/test_packaged_guidance_contract.py` pass.

---

## Phase 3: Port the goal-layer files

### Goal

Ship `run-goal`, `narrate-goal`, the goal runbook and three goal templates, changed only by the lines Appendix A8 and B list plus the settled wording below.

### Assumption under test

The method separates from its fusion references (B3). After the edits, no SC2 term remains, and the runbook keeps its sixteen H2 headings and its limits.

### Test stencil (write first)

```python
# tests/test_goal_layer.py
import re
from tests.helpers.shipped import REPO_ROOT

GOAL_SOURCES = ["skills/run-goal/SKILL.md", "skills/narrate-goal/SKILL.md",
                "project_templates/GOAL_RUNBOOK.md.template", "project_templates/goal.md.template",
                "project_templates/trail.md.template", "project_templates/learnings.md.template"]
SC2 = re.compile(r"fusion-tea|MR-[0-9]|\.codex-test|stellarator|exploration/|\.claude/|/home/|research_seam"
                 r"|source_registry|integrate\.py|STUDY_POLICY|holdout|ARIES|aries-cs|demo-depth-rubric"
                 r"|depth target|GSTH|WI-0[0-9]")
RUNBOOK_H2 = [  # fusion GOAL_RUNBOOK.md's H2s, in order (Invariant 2)
    "What this is, and what it is not", "The five surfaces", 'What "fresh" means',
    "Review scope and evidence reuse", "Grounding a goal", "Opening and closing a round", "Running one task",
    "The pre-execution disposition checkpoint", "The fresh review", "Timing of review coverage",
    "When a cited artifact moves", "Resuming an interruption", "Limits", "The discovery log",
    "The native seams", "The decisions behind this"]

def test_goal_text_points_at_nothing_in_fusion_tea():
    for path in GOAL_SOURCES:
        for n, line in enumerate((REPO_ROOT / path).read_text().splitlines(), 1):
            if "@2b1e9f9d5" in line:  # a provenance citation in the decision record (P5)
                continue
            assert not SC2.search(line), f"{path}:{n}"
            assert ".project/" not in line or "for example" in line, f"{path}:{n}"

def test_runbook_keeps_its_sections_and_limits():
    text = (REPO_ROOT / "project_templates/GOAL_RUNBOOK.md.template").read_text()
    assert re.findall(r"^## (.+)$", text, re.M) == RUNBOOK_H2
    assert all(v in text for v in ("**2 retries**", "**2 revisions**", "**6 rounds**"))

def test_goal_close_heading_is_named():
    assert "## Goal close — YYYY-MM-DD" in (REPO_ROOT / "project_templates/trail.md.template").read_text()
```

### Steps

See `design.md` D8, D10, D11, D17, Appendix A8, Appendix B and § Implementation Notes (keep fusion's line structure).

- [x] Write the test; see it fail.
- [x] Copy the bytes first, then edit only the listed lines:
  - fusion `.claude/skills/run-goal/SKILL.md` → `skills/run-goal/SKILL.md`;
  - fusion `.claude/skills/narrate-goal/SKILL.md` → `skills/narrate-goal/SKILL.md`;
  - fusion `work/orchestration/GOAL_RUNBOOK.md` → `project_templates/GOAL_RUNBOOK.md.template`;
  - fusion `work/orchestration/goal-templates/{goal,trail,learnings}.md` → `project_templates/{goal,trail,learnings}.md.template`.
- [x] Bundle envelope, both skills:
  - list-form `allowed-tools`;
  - `metadata:` / `kind: workflow`;
  - the shared preface and blank-line layout copied from `skills/orchestrate-modeling/SKILL.md:9-12`;
  - fusion's multi-line `description` kept.
- [x] Apply A8: runbook `:84`, `:100`, `:139`, the trigger row after `:73`, `goal.md:29`, `run-goal:53`.
- [x] Apply the Appendix B rows quoted there. Use the table below where B gives only a gist. Find each line by its text, since the inserted trigger row shifts later line numbers by one.
- [x] `learnings.md.template` stays byte-identical.

| fusion line | New text | Class |
|---|---|---|
| run-goal `:20` | "`.project/adr/`" → "the goal-layer decision record (`GOAL_RUNBOOK.md` § The decisions behind this)" | decision record |
| run-goal `:49` | keep "Follow the runbook’s task parallelism and freshness rules."; delete the Codex sentence | envelope / deletion |
| run-goal `:55` | "…for the current task: the stage's installed skill." and "(`uv run` unless the project names another)" | consumer path |
| run-goal `:63` | "When external sources are needed, execute the research procedure directly or delegate independent requests to fresh agents: Claude Code `Agent` with `subagent_type: "general-purpose"`; Codex `spawn_agent` with `fork_turns: "none"`. A delegated brief names the exact question, entry sources, original evidence, and return budget; deposit it at `evidence/`. Apply any source-quarantine rule the project states before any fetch. The main agent remains free to use research skills itself." | consumer path (interim) |
| run-goal `:73` | "- **The goal-layer decision record** (`GOAL_RUNBOOK.md` § The decisions behind this) — why the layer is shaped this way. Records 001–007." | decision record |
| runbook `:31` | "\| The goal-layer decision record (§ The decisions behind this) \| Why is it this way? \| agentic-mbse, as a dated record \|" | decision record |
| runbook `:41` | the concept path → "goal-layer decision record, Sources" | decision record |
| runbook `:94` | the probe-record path → "goal-layer decision record, ADR-0003 (2026-08-27 amendment)" | decision record |
| runbook `:205` | append to the same line: " The owner's close is recorded as `## Goal close — YYYY-MM-DD` at the end of `trail.md`, with the ruling and the disposition." | recorded practice |
| runbook `:232` | second sentence: "For evidence that is not tracked, cite the tracked native record that already hashes it: a study store is cited through the committed study record that carries the store's identity `@<sha>`; an externally stored research binary is cited through its tracked extracted text `@<sha>`." | consumer path |
| runbook `:260` | "`exploration/<pkg>/studies/DISCOVERY_LOG.md` is" → "The study layer's discovery log is" | consumer path |
| runbook `:270` | "fails `tests/study/test_records.py::…` for that record" → "fails the study layer's join check for that record" | consumer path |
| runbook `:276` | "are in `.claude/skills/run-study/runbook.md`, and its rules are in `modeling_project/STUDY_POLICY.md`" → "are in the study layer's runbook, and its rules are in its policy, where a target installs one" | consumer path |
| runbook `:286` | "**Each seam is the procedure the target installs. A goal round still may not silently absorb a seam repair.**" | consumer path |
| runbook `:288` | "- **`research`** is the research procedure the project's instructions name; otherwise `/research` and `/manage-sources`." | consumer path / deletion |
| runbook `:289` | "- **`integrate`** is the integration procedure the target installs, where it has one." | consumer path / deletion |
| runbook `:295` | append: " The records are `goal-layer-decisions.md` in the installed toolkit's docs directory (`uv run python -c 'from agentic_mbse.cli import get_docs_dir; print(get_docs_dir())'`)." | decision record |
| runbook `:299-305` | "[ADR-000N](../../.project/adr/…)" → "ADR-000N" | decision record |
| runbook `:304` (not in B) | "Citing `.project/` by path and digest" → "Citing a second PM's records by path and digest" | consumer path (two-PM) |
| trail template, end | append a blank line, `## Goal close — YYYY-MM-DD`, a blank line, "- **Ruling:** the owner's close ruling, quoted or cited." and "- **Disposition:** closed on § Answered when, or closed by redirect, and why." | recorded practice |

### Checks

- [x] `diff -U0` each ported file against its fusion original. Every hunk is one of the rows above, A8, or a quoted Appendix B row, and nothing else. P7 classes them formally.
- [x] `tests/test_shipped_text.py` passes. The two new bundles join its envelope and preface checks with no test edit.
- [x] The shared checks, including the SC2 grep.

**Commit:** `Port run-goal, narrate-goal, the goal runbook and goal templates with the method unchanged`

**What we know works:** the shipped goal text is general, keeps fusion's sections, and is installable as bundles.

**Progress notes:**

- **Done 2026-10-11.** Added `skills/run-goal/SKILL.md`, `skills/narrate-goal/SKILL.md`, `project_templates/{GOAL_RUNBOOK,goal,trail,learnings}.md.template` and `tests/test_goal_layer.py` (the stencil's three tests, unchanged apart from a module docstring). Each file started as a byte copy of its snapshot original; the edits were exact-match replacements that each had to hit once.
- **Hunks** (`diff -U0` against the snapshot). run-goal 10: three envelope, `:20`, `:49`, `:53`, `:55`, `:61`, `:63`, `:73`. narrate-goal 4: three envelope, `:77`. Runbook 21: `:7`, `:13`, `:31`, `:41`, the trigger row after `:73`, `:84`, `:94`, `:100`, `:106`, `:139`, `:205`, `:232`, `:260`, `:262`, `:270`, `:272`, `:276`, `:286`, `:288-289` (one hunk), `:295`, `:299-305` (one hunk, holding the `:304` rewording). goal 1 (`:29`). trail 1 (the appended close section). learnings 0 (`cmp` silent). Every hunk is a row of the table above, an A8 hook, a quoted Appendix B row or the envelope. P7 classes them formally.
- **A8 checked by script against `design.md`.** `goal.md:29`, `run-goal:53` and the trigger row match byte-for-byte.
- **Interpretation: the resolver command at runbook `:84`.** A8 writes `print(get_docs_dir() / \"patterns\")` because the whole new sentence sits inside double quotes in the design. Shipped as written, the backslashes are a Python `SyntaxError` (checked). The runbook carries `"patterns"` unescaped, the way A6 and D4 write the same command. Otherwise `:84` matches A8 byte-for-byte. The command runs and prints a `patterns` directory holding `design-choices.md`.
- **Envelope.** List-form `allowed-tools` with fusion's tool lists unchanged (no tool added); `metadata.kind: workflow` after `user-invocable`; the shared preface copied byte-for-byte from `orchestrate-modeling:10`, with the same one blank line before and two after. Fusion's multi-line `description` blocks are kept.
- **Wording notes.** New text uses straight apostrophes, as the plan and design quote it; fusion's own text keeps its curly ones, so `run-goal:55` now holds both ("the stage's installed skill" beside "project’s prescribed launcher"). `run-goal:73` drops "indexed in `INDEX.md`" along with the path, as this plan's row gives it.
- **For P4.** `narrate-goal` (`:82` now) names `tests/orchestration/test_narrative_links.py`, which P4 installs. In a fresh `init` today, the only repo paths the goal text names that are missing are `work/narratives/`, `work/orchestration/GOAL_RUNBOOK.md` and `work/orchestration/goal-templates/`, all P4's; `knowledge/research/` and the rest exist. The two bundles already install into `.agents/skills/` with no installer change, and `install-commands --list` names both.
- **For P5.** The goal text names ADR-0001..0007 only. The record must carry a "Sources" section (runbook `:41`) and ADR-0003's 2026-08-27 amendment (`:94`, `:262`); § The decisions behind this gives the `get_docs_dir()` command at `:296`.
- **For P7.** The goal hooks now sit at runbook `:74` (trigger row), `:85` (§ Grounding a goal), `:101` (§ Opening and closing a round) and `:140` (§ Running one task), each one line below fusion's because of the inserted row; `goal.md:29`; `run-goal:58` (five lines below fusion's `:53`, from the envelope).
- **Shared checks.** `uv run pytest tests/`: 2197 passed, 1 skipped, 1 xfailed. The baseline after P2 was 2192 passed: three new tests, plus the two new bundles in the per-skill envelope test. `tests/test_shipped_text.py` passes with no edit. `ruff check src/ tests/`: 118, unchanged; the new test passes `ruff check` and `ruff format --check`. `mypy src/`: 88 errors in 18 files, below the 98 recorded at P1; this phase changes no `src/` file, so the drop comes from the all-extras venv. SC2 grep: no output. `.project/` grep: runbook `:13` only, the two-PM "for example" wording.

---

## Phase 4: Install the goal layer

### Goal

Register the goal files with the installer, add the narrative-link contract test, and prove the install under `claude`, `codex`, `both` and `--dev`. The `--dev` case includes running the installed test through its link (D9).

### Assumption under test

`Path(__file__).absolute().parents[2]` lands on the target when the test is a `--dev` link into `project_templates/`. The test also fails on a broken narrative link and passes on a fixed one.

### Test stencil (write first)

```python
# tests/test_goal_layer.py, added
import subprocess
import sys
from argparse import Namespace

import pytest

from agentic_mbse.cli import cmd_init

GOAL_FILES = ["work/orchestration/GOAL_RUNBOOK.md", "work/orchestration/goal-templates/goal.md",
              "work/orchestration/goal-templates/trail.md", "work/orchestration/goal-templates/learnings.md",
              "tests/orchestration/test_narrative_links.py"]

def init(target, assistant="both", dev=False):
    assert cmd_init(Namespace(path=str(target), force=False, dev=dev, assistant=assistant)) == 0

@pytest.mark.parametrize("assistant", ["claude", "codex", "both"])
def test_init_installs_the_goal_layer(tmp_path, assistant):
    init(tmp_path, assistant)
    assert all((tmp_path / ".agents/skills" / s / "SKILL.md").is_file() for s in ("run-goal", "narrate-goal"))
    assert all((tmp_path / f).is_file() for f in GOAL_FILES)
    assert (tmp_path / "work/orchestration/goals").is_dir() and (tmp_path / "work/narratives").is_dir()

def test_dev_links_goal_files_and_ignores_them(tmp_path):
    init(tmp_path, dev=True)
    assert all((tmp_path / f).is_symlink() for f in GOAL_FILES)
    ignored = (tmp_path / ".gitignore").read_text().splitlines()
    assert {"work/orchestration/GOAL_RUNBOOK.md", "work/orchestration/goal-templates/",
            "tests/orchestration/test_narrative_links.py"} <= set(ignored)

def run_narrative_test(target) -> int:
    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
               "tests/orchestration/test_narrative_links.py"]
    return subprocess.run(command, cwd=target, capture_output=True).returncode

@pytest.mark.parametrize("dev", [False, True])
def test_narrative_link_test_fails_then_passes_in_the_target(tmp_path, dev):
    init(tmp_path, dev=dev)
    (tmp_path / "work/narratives/n.md").write_text("[e](../orchestration/goals/g/e.md)\n")
    assert run_narrative_test(tmp_path) == 1
    (tmp_path / "work/orchestration/goals/g").mkdir(parents=True)
    (tmp_path / "work/orchestration/goals/g/e.md").write_text("e\n")
    assert run_narrative_test(tmp_path) == 0
```

Under `--dev` the test file is a link into this repo. If its root resolved through the link, it would read this repo's (absent) `work/narratives/`, and the first assertion would fail.

### Steps

See `design.md` D9, D12, § Component Overview "agentic-mbse, goal layer", and § Implementation Notes on the narrative test.

- [x] Write the tests; see them fail.
- [x] `project_templates/test_narrative_links.py.template`. Start from fusion `tests/orchestration/test_goal_contract.py`:
  - keep `_local_link_targets` and `test_narrative_evidence_links_resolve`;
  - drop the ADR-register check and the `yaml` import;
  - replace the `repo_root` fixture with a module-level `REPO_ROOT = Path(__file__).absolute().parents[2]`, never `.resolve()`.
- [x] `src/agentic_mbse/cli/__init__.py`:
  - five `TOOL_OWNED_TEMPLATES` entries (`:40-45`): `GOAL_RUNBOOK.md.template` → `work/orchestration/GOAL_RUNBOOK.md`; `goal.md.template`, `trail.md.template`, `learnings.md.template` → `work/orchestration/goal-templates/*.md`; `test_narrative_links.py.template` → `tests/orchestration/test_narrative_links.py`;
  - `work/orchestration/goals` and `work/narratives` in the `cmd_init` subdirectory list (`:486-503`);
  - the three `DEV_MODE_GITIGNORE_PATHS` lines (`:48-62`), as in the design.
- [x] `skills/orchestrate-modeling/SKILL.md:57` (D12; shed item 3): "…imposed by the goal workflow (`/run-goal`) or the target project's study workflow."
- [x] This repo's `CLAUDE.md`: add the five templates to the "Tool-owned" list, and the goal runbook and templates to the "Managed assets" examples in "Init File Ownership".
- [x] Capture SC1 into `evidence/sc1-install.txt`:
  - `uv run agentic-mbse install-commands --list`;
  - for each of `claude`, `codex` and `both`, `uv run agentic-mbse init <tmp> --assistant <a> < /dev/null`, then `ls` of the two bundles, five goal files and two directories;
  - the same for `init --dev`, with `ls -l` of the goal files and the three ignore lines.

### Checks

- [x] The new tests pass, including both `dev` cases of the narrative test.
- [x] The shared checks. `tests/test_shipped_text.py` now reads the five new destinations as runtime-neutral text.

**Commit:** `Install the goal layer: tool-owned templates, goal directories, dev ignore lines, narrative-link test`

**What we know works:** SC1, and the contract test runs correctly from a copy and from a `--dev` link.

**Progress notes:**

- **Done 2026-10-11.** Added `project_templates/test_narrative_links.py.template` and `evidence/sc1-install.txt`. Edited `src/agentic_mbse/cli/__init__.py`, `skills/orchestrate-modeling/SKILL.md`, `CLAUDE.md` and `tests/test_goal_layer.py`.
- **Installer.** Five `TOOL_OWNED_TEMPLATES` entries after `epic_template`, the three `DEV_MODE_GITIGNORE_PATHS` lines at the end of the list, and `work/orchestration/goals` and `work/narratives` after `work/learnings` in the `cmd_init` subdirectory list. No `Installer` change: the goal files go through the existing tool-owned loop, so `--dev` links them and a plain init copies them. I also brought the `cmd_init` docstring's "Creates" list up to date (goal runbook and templates under `work/`, the narrative-link test as tool-owned under `tests/`); the plan did not name this.
- **Narrative-link template.** Four hunks against fusion `tests/orchestration/test_goal_contract.py`: the docstring's first line ("Records remain findable and presentation links resolve." → "Presentation links resolve.", because the register check is gone); the `yaml` import; the ADR-register block (`ADR_FILE`, `_frontmatter`, `test_register_is_coherent`) replaced by `REPO_ROOT = Path(__file__).absolute().parents[2]` with a one-line comment saying why not `resolve()`; and the test's `repo_root` fixture replaced by `REPO_ROOT`. That last hunk also drops one of fusion's three blank lines before the test, so the file has the usual two; it sits inside the fixture hunk and adds none. `_local_link_targets` is byte-identical. The template passes `ruff check`.
- **Tests, beyond the stencil.** `run_narrative_test` returns the completed process, not only its exit code, so a failure prints pytest's output. The broken-link case also asserts that the output names `unresolved link ../orchestration/goals/g/e.md`, so exit code 1 cannot come from some other failing test. The fixed case uses `mkdir()` without `parents`, so it also needs `work/orchestration/goals/` from init. The install test asserts each file in its own loop so a failure names the missing path.
- **D9 mutation check.** With the template's root switched to `.resolve()`, `test_narrative_link_test_fails_then_passes_in_the_target[True]` fails (`assert 0 == 1`: the linked test read the checkout's parent folder, found no narratives, and passed) and `[False]` still passes. Restored to `.absolute()`; both pass.
- **`orchestrate-modeling:57`** now reads "…imposed by the goal workflow (`/run-goal`) or the target project's study workflow." `/run-goal` is an installed bundle, so `test_installed_references_name_installed_skills` accepts it.
- **`CLAUDE.md`.** Three Tool-owned lines (the three goal templates on one line) and "the goal runbook and templates" in the Managed assets examples.
- **SC1 evidence.** `install-commands --list` names `narrate-goal` and `run-goal` as workflows (27 skills). Each of `claude`, `codex`, `both` creates the two bundles, the five goal files and the two directories; `--dev` links the bundles and the five goal files into this checkout, and its `.gitignore` carries the three lines (`:70-72`). Each init's output is filtered to goal-layer lines; the header of the file says so.
- **For P5.** `GOAL_FILES` is defined, and the test file has the `init` helper P5's stencil calls. The new template is not yet in `GOAL_SOURCES`; P5's stencil adds it with the record.
- **For P7.** The narrative-test diff has the four hunks above. The ADR-register check's removal has no Appendix C row of its own: Appendix C's "Narrative check path" row and spec `:99` cover it (fusion's own test, with that check, stays). P7 should decide whether that row is enough or whether P8 adds one.
- **Known gap, unchanged (design § Non-Goals).** A target already initialized with `--dev` keeps its old ignore section: `_update_gitignore_for_dev_mode` returns early when the marker line is present, so the three new lines are not appended on re-init. This is the dev-mode ignore-marker follow-up P8 lists.
- **Shared checks.** `uv run pytest tests/`: 2203 passed, 1 skipped, 1 xfailed (P3: 2197; plus six new tests). The 6 warnings all come from `tests/test_extraction.py` (fork in a threaded process), not this phase. `ruff check src/ tests/`: 118, unchanged; the touched files pass `ruff check`, and `tests/test_goal_layer.py` passes `ruff format --check`. `mypy src/`: 88, unchanged, with none in `cli/__init__.py`. SC2 grep over the goal text including the new template: no output; `.project/` only at runbook `:13`, the two-PM "for example" wording.

---

## Phase 5: The decision record, and installed references that resolve

### Goal

Write `docs/goal-layer-decisions.md` (D7) and prove SC2's ADR clause, SC3 and SC10.

### Assumption under test

Every `ADR-000N` and every repo path the installed goal text names resolves in a fresh target, or through the resolver.

### Test stencil (write first)

```python
# tests/test_goal_layer.py, added; also add the narrative-test template and the record to GOAL_SOURCES
from agentic_mbse.cli import get_docs_dir
RECORD = REPO_ROOT / "docs/goal-layer-decisions.md"
PATH_REF = re.compile(r"`((?:work|modeling_project|knowledge|tests|models|data)/[^`\s<>*]*)`")

def test_every_cited_adr_is_in_the_decision_record():
    carried = set(re.findall(r"^### (ADR-\d{4})", RECORD.read_text(), re.M))
    assert carried == {f"ADR-000{n}" for n in range(1, 8)}
    for path in GOAL_SOURCES:
        assert set(re.findall(r"ADR-\d{4}", (REPO_ROOT / path).read_text())) <= carried, path

def test_installed_goal_references_resolve(tmp_path):
    init(tmp_path)
    for path in GOAL_FILES + [".agents/skills/run-goal/SKILL.md", ".agents/skills/narrate-goal/SKILL.md"]:
        for ref in PATH_REF.findall((tmp_path / path).read_text()):
            assert (tmp_path / ref).exists(), f"{path} names {ref}"
    assert (get_docs_dir() / "patterns/design-choices.md").is_file() and RECORD.is_file()
```

The SC2 test from P3 now covers the two added sources. Its `@2b1e9f9d5` skip exempts the record's provenance lines. A path with a `<placeholder>` never matches `PATH_REF`.

### Steps

See `design.md` D7, § Component Overview "docs/goal-layer-decisions.md", and Appendix B's decision-record rows.

- [x] Write the tests; see them fail.
- [x] `docs/goal-layer-decisions.md`, written from fusion `.project/adr/0001-0007` and the concept file:
  - the opening: the authority stance, the amendment clause, and ADR-0006's two-PM condition;
  - one `### ADR-000N — <title>` entry each: the current decision as amended, its grade(s) and dates, its invariants in short, and `fusion-tea .project/adr/000N-<slug>.md@2b1e9f9d5`;
  - the amendments the runbook cites: ADR-0003's 2026-08-27 five-class promotion (runbook `:94`, `:262`) and its 2026-09-11 independence boundary (runbook `:48`);
  - a closing "Sources the runbook cites": the critic definition (concept `:47`), goals being general (`:198`), the 2026-08-27 probe amendment, the 2026-09-14 process-sizing request.
  - Shed item 1: if the budget is short, write the entries as one table (decision | grade | provenance).
- [x] If `test_installed_goal_references_resolve` names a path a fresh target lacks, reword the goal text so it marks the path as supplied by the target or by another procedure (SC3). Do not add an allowlist that hides it.
- [x] `tests/test_packaged_guidance_contract.py`: add `test_built_wheel_carries_the_resolver_reached_goal_layer_documents(wheel)`. It asserts that `agentic_mbse_data/docs/patterns/design-choices.md`, `agentic_mbse_data/docs/goal-layer-decisions.md` and `agentic_mbse_data/project_templates/GOAL_RUNBOOK.md.template` are in the wheel, with source bytes.
- [x] `evidence/sc10-decision-record.md`, one row per ADR: the `provenance` from the fusion frontmatter (snapshot) | the grade the record carries | the cited path at `2b1e9f9d5` | match.

### Checks

- [x] The new tests pass. The runbook names the resolver for both documents: `grep -n "get_docs_dir" project_templates/GOAL_RUNBOOK.md.template` → `§ Grounding a goal` and `§ The decisions behind this`.
- [x] The shared checks.

**Commit:** `Add the goal-layer decision record and check that installed goal references resolve`

**What we know works:** SC2's ADR clause, SC3 and SC10, and the wheel carries both resolver-reached documents.

**Progress notes:**

- **Done 2026-10-11.** Added `docs/goal-layer-decisions.md` and `evidence/sc10-decision-record.md`. Edited `tests/test_goal_layer.py` (the narrative-test template and the record join `GOAL_SOURCES`; `RECORD`, `PATH_REF` and the two stencil tests) and `tests/test_packaged_guidance_contract.py` (the wheel test). Before the record existed, the three affected tests failed on the missing file only.
- **The record.** An opening section, "How This Record Governs": the authority stance, the amendment clause (a later source amendment reaches targets only through an ordinary agentic-mbse change to this file, never by reference), how grades are read, and ADR-0006's two-PM condition. Then one `### ADR-000N — <title>` entry each, with Grade, Decision as amended, each dated amendment, Why (with rejected alternatives in one sentence), Invariants and Source. The Source line quotes the fusion frontmatter's provenance field verbatim and cites `fusion-tea .project/adr/000N-<slug>.md@2b1e9f9d5`. A closing "Sources the Runbook Cites" holds the critic definition (concept `:47`), goals being general (`:198`), the 2026-08-27 probe amendment and the 2026-09-14 process-sizing request. Not shed: full entries, not a table.
- **Choice: a "Why" line per entry.** The plan lists decision, grades, dates, invariants and provenance. I added a short Why with the rejected alternatives because the runbook sends a reader to the record "when you want to challenge the rule", and an `[AGENT]` decision is challenged against its recorded reasoning (capture fidelity).
- **Generalized, not copied.** ADR-0006's title becomes "…may cite a second PM's records…" (the runbook's two-PM wording). Study-layer invariants become "where a target installs a study layer". The proof-run amendments keep their measurements, verdicts and grades but drop fusion's goal slugs, item numbers, domain question and record paths. The 2026-08-27 "`:234`/`:244` contradiction" is written as "a contradiction between two runbook lines", because the snapshot does not show which lines those were. The full list is in `evidence/sc10-decision-record.md`.
- **Two sources the snapshot cannot confirm**, recorded as such in the record and the evidence: the probe record (cited as the path fusion's runbook names at `2b1e9f9d5`; the file is not in the snapshot), and the 2026-09-14 request's wording (no source in the snapshot quotes it; the record says so).
- **Deviation: the path check is wider than the stencil.** The stencil's `PATH_REF` matched only a path that fills a whole backtick span, so it missed paths inside commands, such as `narrate-goal`'s `uv run pytest tests/orchestration/test_narrative_links.py -q`. The test now matches a repo path anywhere in the installed text, skips paths holding a `<placeholder>` (a goal creates those), and strips a sentence-ending period. It finds 11 distinct fixed paths across the seven installed files; all exist in a fresh target. Mutation check: renaming that path in `skills/narrate-goal/SKILL.md` fails the test with `.agents/skills/narrate-goal/SKILL.md names tests/orchestration/test_narrative_link.py`; restored.
- **SC3: no rewording needed.** Every fixed path the installed goal text names exists after `init`. The placeholder paths are under `work/orchestration/goals/<goal>/` and `work/narratives/<…>`, both directories `init` creates.
- **Wheel test.** Parametrized over the three files; each must be in the wheel under `agentic_mbse_data/` with the source bytes. Passes. The whole-`docs` comparison stays the known strict xfail.
- **For P6.** `GOAL_SOURCES` now has eight entries, including the record. P6's `test_design_choice_obligations_are_stated_once` searches `skills/`, `project_templates/` and `docs/patterns/`; the record is in `docs/`, not `docs/patterns/`, and states none of the three obligation phrases.
- **For P8.** The install grep's resolver line should show both `design-choices.md` and `goal-layer-decisions.md` existing; they do in this checkout.
- **Shared checks.** `uv run pytest tests/`: 2208 passed, 1 skipped, 1 xfailed (P4: 2203; plus two goal-layer tests and three wheel cases). `ruff check src/ tests/`: 118, unchanged; both touched test files pass `ruff check` and `ruff format --check`. `mypy src/`: 88, unchanged (no `src/` change). SC2 grep over the eight goal-text files: no output. `.project/` grep: runbook `:13` and record `:13`, both the two-PM "for example" wording. `get_docs_dir` in the runbook: `:85` (§ Grounding a goal) and `:296` (§ The decisions behind this).

---

## Phase 6: Contract pins (SC5(f)), with one reverted edit shown

### Goal

Pin the four placement lines and the sibling links in `tests/test_modeling_command_contracts.py`, and show one removal failing.

### Assumption under test

Removing any pinned line fails a named test.

### Test stencil (write first)

```python
# tests/test_modeling_command_contracts.py, added
def section(text: str, heading: str) -> str:
    return text.split(f"## {heading}\n", 1)[1].split("\n## ", 1)[0]

def test_process_selection_routes_design_choice_changes():
    rows = section(read_repo_file("project_templates/MODELING_PROCESS.md.template"), "Process Selection")
    assert any("Changed design-variable role" in r and "design-choices.md" in r for r in rows.splitlines())

def test_point_of_use_table_has_the_design_choice_row():
    rows = section(read_repo_file("project_templates/MODELING_PROCESS.md.template"), "Technical Patterns: Read at the Point of Use")
    assert any(r.startswith("| Design variables, equipment or capacity bindings") and r.endswith("`design-choices.md` |") for r in rows.splitlines())

def test_goal_runbook_trigger_table_mirrors_the_design_choice_row():
    rows = section(read_repo_file("project_templates/GOAL_RUNBOOK.md.template"), "Review scope and evidence reuse")
    assert any("Changed design-variable role" in r and "design-choice pattern" in r for r in rows.splitlines())

def test_goal_template_points_at_the_design_choice_pattern():
    assert "apply the design-choice pattern (`design-choices.md`" in read_repo_file("project_templates/goal.md.template")
```

### Steps

- [x] Add the four tests above, plus:
  - `test_design_choice_pattern_and_equality_intent_name_each_other`: `[design-choices.md](design-choices.md)` in `docs/patterns/constraints.md`; `docs/patterns/design-choices.md` in `skills/sysml-conventions/SKILL.md`; `[constraints.md](constraints.md)` in `design-choices.md`.
  - `test_design_choice_obligations_are_stated_once` (SC5(a)): "must be evaluable without rerunning the policy", "Unknown compliance does not count as completed remediation" and "must not conceal automatic adequacy" each occur in `docs/patterns/design-choices.md` and in no other file under `skills/`, `project_templates/` or `docs/patterns/`.
  - `test_design_choice_pattern_names_no_project_authority` (SC5(g)): `design-choices.md` matches neither `MR-[0-9]`, `fusion`, `rubric`, `depth` nor `\.project/`.
- [x] Show the reverted edit in `evidence/sc5f-reverted-edit.txt`:
  - delete the design-choice row from "Process Selection" in `project_templates/MODELING_PROCESS.md.template`;
  - capture `git diff` and `uv run pytest tests/test_modeling_command_contracts.py -q` (expect `test_process_selection_routes_design_choice_changes` to fail);
  - `git restore project_templates/MODELING_PROCESS.md.template`, rerun, and append the passing output.
- [x] Confirm `git status --short project_templates/` is empty before committing.

### Checks

- [x] The shared checks.

**Commit:** `Pin the design-choice placement in the contract tests`

**What we know works:** SC5(a), (f), (g) and (h) are enforced by tests, and a removal is shown failing.

**Progress notes:**

- **Done 2026-10-11.** Added seven tests and a `section()` helper to `tests/test_modeling_command_contracts.py`, and `evidence/sc5f-reverted-edit.txt`. No shipped file changed.
- **Deviation: the SC5(a) phrase follows the pattern as committed.** The plan's step names "Unknown compliance does not count as completed remediation". Commit `f454835` (after P2) restored MR-7's wording in the pattern, which now reads "Unknown compliance cannot count as completed remediation". The test pins the current sentence; the old one is in no shipped file.
- **Tests, beyond the stencil.** `test_design_choice_obligations_are_stated_once` reads every file under `skills/`, `project_templates/` and `docs/patterns/` (all UTF-8) and asserts that the pattern is the only file holding each phrase. `test_design_choice_pattern_names_no_project_authority` ignores case, so "Fusion" or "Depth" also fail it; the pattern is clean either way. The stencil's four tests are as written, apart from `ruff format` line breaks.
- **Reverted edit.** Deleting the "Process Selection" design-choice row fails `test_process_selection_routes_design_choice_changes` (1 failed, 14 passed); after `git restore`, 15 passed. The capture has the diff and both runs. I also mutated each other pin once (point-of-use row, runbook trigger row, goal-template pointer, each sibling line, an obligation restated in `review-model`, "MR-7" added to the pattern); each fails its named test. The list is at the end of the evidence file. `git status --short project_templates/` was empty before the commit.
- **SC5(h).** The sibling test pins the two cross-reference lines and the pattern's link back. The "adds only cross-reference lines" half stays a diff check: P2 recorded 2 insertions and 0 deletions in each file, and P7 or the audit re-reads the diff.
- **For P7.** P6 touched no ported goal file, so the hunk counts P3 and P4 recorded still stand.
- **Shared checks.** `uv run pytest tests/`: 2215 passed, 1 skipped, 1 xfailed (P5: 2208; plus seven). `ruff check src/ tests/`: 118, unchanged; the touched test file passes `ruff check` and `ruff format --check`. `mypy src/`: 88, unchanged. SC2 grep: no output. `.project/` grep: runbook `:13` and record `:13`, the two-PM "for example" wording.

---

## Phase 7: SC12 hunk classification

### Goal

Show that the port is a port: every hunk in every shipped goal file has exactly one class.

### Assumption under test

No hunk is a method change (B3).

### Test stencil (write first)

This phase writes evidence, not code. The executable check is a hunk count:

```bash
S=.orchestrate-logs/fusion-tea-snapshot; E=.project/active/goal-layer-port/evidence/sc12
mkdir -p $E
diff -U0 $S/.claude/skills/run-goal/SKILL.md          skills/run-goal/SKILL.md                         > $E/run-goal.diff
diff -U0 $S/.claude/skills/narrate-goal/SKILL.md      skills/narrate-goal/SKILL.md                     > $E/narrate-goal.diff
diff -U0 $S/work/orchestration/GOAL_RUNBOOK.md        project_templates/GOAL_RUNBOOK.md.template       > $E/runbook.diff
for t in goal trail learnings; do diff -U0 $S/work/orchestration/goal-templates/$t.md project_templates/$t.md.template > $E/$t.diff; done
diff -U0 $S/tests/orchestration/test_goal_contract.py project_templates/test_narrative_links.py.template > $E/narrative-test.diff
grep -c '^@@' $E/*.diff   # each count must equal that file's rows in sc12-hunks.md
```

### Steps

- [x] Produce the diffs above. `diff` exits 1 when files differ; that is expected.
- [x] `evidence/sc12-hunks.md`: one row per hunk, giving file, `@@` header and class. The six classes (spec SC12 plus D17): consumer path generalized; design-choice hook generalized; decision-record citation; recorded-practice addition; deletion with ledger row (name the Appendix C row); bundle envelope. Any hunk that drops a consumer-specific instruction names its ledger row, whatever its class.
- [x] A hunk with no class fails the phase. Fix the shipped file, rerun P3–P6's tests, and regenerate the diffs.
- [x] Re-check the goal-hook rows of `evidence/sc6-crosswalk.md` against the ported text, and correct their locations if the text moved.

### Checks

- [x] `grep -c '^@@'` per file equals that file's row count in `sc12-hunks.md`. No row has an empty class.
- [x] The shared checks.

**Commit:** `Evidence: SC12 hunk classification of every ported goal file`

**What we know works:** SC12, and the method-preservation half of the spec.

**Progress notes:**

- **Done 2026-10-11.** Added `evidence/sc12-hunks.md` and the seven diffs in `evidence/sc12/`, made with the stencil's commands. Amended three sentences of `evidence/sc6-crosswalk.md`. No shipped file changed.
- **Result.** 41 hunks, each with exactly one class: run-goal 10, narrate-goal 4, runbook 21, goal 1, trail 1, learnings 0, narrative test 4. By class: consumer path 14, decision-record citation 9, bundle envelope 6, design-choice hook 6, deletion with ledger row 4, recorded practice 2. No hunk is a method change, so no shipped file needed fixing. The counts match P3's and P4's notes.
- **Hunk ids.** Each row has an id (`RG-n`, `NG-n`, `RB-n`, `GT-1`, `TT-1`, `NT-n`) so the P8 ledger's evidence column can cite them. A script confirmed that each file's rows carry the diff's `@@` headers in order, that the row count equals `grep -c '^@@'`, and that no class is empty.
- **One-class calls.** Three hunks hold two kinds of change, and each is classed by what it mostly does, with the other part named in the row. RG-5 (fusion `:49`, the dropped Codex sentence) is "deletion with ledger row": its `.agentic-mbse/codex.md` half now sits in the preface (RG-3). RB-21 (the ADR table) is "decision-record citation": it also holds the `:304` two-PM rewording. NT-3 is "deletion with ledger row" for the ADR-register block: `diff` joins the two added `REPO_ROOT` lines to it because they are adjacent, and NT-4 is the consumer-path hunk they belong to.
- **Method check.** Three hunks fall inside the runbook's method lists, and none changes a step, list member or value: RB-3 (the decision-record surface's location and writer; still five surfaces), RB-4 (the critic quote's source only) and RB-11 (appends where the close is recorded). The integrate seam's dropped description (RB-19) is fusion's implementation; the seam table, which carries each seam's invocation and native return, is unchanged.
- **Crosswalk.** Every goal-hook destination holds in the ported text; no location needed correcting. The three sentences that said Phase 7 would check now record the confirmation and the ported line numbers: runbook `:74`, `:85`, `:101`, `:140`; `run-goal:58`, `:60`; `goal.md:29`.
- **For P8.** Ledger rows are named in `sc12-hunks.md` by Appendix C's "Text left out" lead, plus "ADR-register check" (NG-4, NT-1–NT-3), the row the orchestrator asked P8 to add. P8's ledger must use those names. Rows with no hunk of their own: "The two MR-7 process paragraphs", "`.agentic-mbse/patterns/` location line", "Binding-row semicolon", "MR-7 general application…" (fusion's process and requirements files, not ported goal files) and "Local `run-goal`, `narrate-goal`…" (F2). Their evidence is the crosswalk and the fusion branch diff.
- **Shared checks.** `uv run pytest tests/`: 2215 passed, 1 skipped, 1 xfailed (unchanged from P6). `ruff check src/ tests/`: 118, unchanged. `mypy src/`: 88, unchanged. SC2 grep: no output. `.project/` grep: runbook `:13` and record `:13`, the two-PM "for example" wording.

---

## Phase 8: Ledger, reach trace, install evidence, F2 runbook

### Goal

Write the evidence that lives in this repo and that fusion-tea work depends on: the ledger section (SC9), the reach trace (SC5(d)), the install grep (SC2, SC3), and the F2 runbook that O2 rehearses.

### Assumption under test

Every left-out line has a named fusion-tea destination, and every skill in Appendix E reaches the rule in at most two named hops in the final files.

### Test stencil (write first)

Evidence again. The executable check is the SC2/SC3 grep over a fresh install:

```bash
T=$(mktemp -d); uv run agentic-mbse init $T < /dev/null > /dev/null
grep -rnE "$SC2" $T/.agents/skills/run-goal $T/.agents/skills/narrate-goal $T/work/orchestration $T/tests/orchestration   # → no output ($SC2 from Shared checks)
uv run python -c 'from agentic_mbse.cli import get_docs_dir as d; print([(p, p.exists()) for p in (d()/"patterns/design-choices.md", d()/"goal-layer-decisions.md")])'
```

### Steps

- [ ] `evidence/sc2-sc3-install.txt`: the commands above with their output, plus `ls -R` of the installed goal files.
- [ ] `evidence/sc5d-reach-trace.md`: Appendix E's table, each hop verified against the final files and given its current `file:line`. A hop that does not hold is a gap. Add a one-line pointer only where the trace shows one (D4), then rerun the shared checks.
- [ ] `.project/active/wrap-split-migration-ledger.md`, new "Item 2 — goal-layer-port" section:
  - Appendix C's rows in Item 1's four columns. Evidence column: `goal-layer-port/evidence/fusion-tea/branch-diff-F1.txt` (O1 creates it) and the SC12 hunk ids;
  - the merge order from `design.md` § Integration Strategy;
  - amend the header sentence "The owner applies every fusion-tea change": Item 2's fusion-tea changes are made by the orchestrator on `goal-layer-mr7` and merged by the owner (Align record).
- [ ] `evidence/fusion-tea-runbook.md`, the F2 runbook, written from Appendix D4 in the shape of Item 1's (`.project/completed/20261009_native-skill-distribution/evidence/fusion-tea-runbook.md`):
  - Before you start: agentic-mbse `goal-layer-port` merged as M; record M's SHA.
  - Step 1, pin move: `rev` and `uv.lock` by hand; `uv sync --frozen --extra e2e`; diff `uv pip list` before and after and restore anything removed (earlier moves restored `syside-license==0.3.6` with `uv pip install --no-deps`, and `greenlet`).
  - Step 2: the SHA in `tests/test_dependency_provenance.py`.
  - Step 3: D2 step 1 for real (the removals, `.gitignore:25,:27`, `AGENTS.md:5` "Local goal and study skills" → "Local study skills", `rm` of the five tool-owned files).
  - Step 4: `uv run --no-sync agentic-mbse init . < /dev/null`.
  - Step 5: the O2 verification list, with the resolver hop in fusion's own environment: `uv run --no-sync python -c 'from agentic_mbse.cli import get_docs_dir; p = get_docs_dir() / "patterns" / "design-choices.md"; print(p, p.exists())'`.
  - Step 6: commit; the owner pushes and merges.
  - Leave one "Observed in the rehearsal" slot per step for O2 to fill.
- [ ] `evidence/README.md`:
  - one line per SC naming its evidence file, or the orchestrator phase that creates it;
  - the list of edits outside this item's files, for Item 4 (`design.md` § Integration Strategy);
  - the two follow-ups for close to file: the dev-mode ignore-marker gap, and the per-design literal/bound attribute listing.

### Checks

- [ ] The install grep prints nothing, and both resolver paths exist.
- [ ] Every Appendix C row is in the ledger with a destination.
- [ ] The shared checks.

**Commit:** `Evidence and ledger: Item 2 ledger section, reach trace, install grep, F2 runbook`

**What we know works:** everything this repo can prove without fusion-tea or a live agent.

**Progress notes:**

---

## Orchestrator-run phases

These need fusion-tea, a scratch target or a live `claude -p`, so implement sessions cannot run them. `AM=/home/reid/1cfe/agentic-mbse-goal-layer`, `FT=/home/reid/1cfe/fusion-tea-goal-layer`, `E=$AM/.project/active/goal-layer-port/evidence`. Use `git -C`, never `cd` into fusion-tea, and never touch the owner's main fusion-tea checkout (Align record). Each phase ends with one agentic-mbse commit of its evidence.

If the permission classifier blocks writes under `$FT`, write the phase's fusion-tea commands as a script under `$E/fusion-tea/` and ask the owner to run it. That happened in earlier fusion-tea work.

### O0 (optional, any time after P1): wheel smoke check

Runs D3 step 1 early, so a dependency or license failure surfaces before O3.

- [ ] `D=/tmp/goal-dry-run-smoke-$(date +%Y%m%d-%H%M%S)`; `mkdir -p $D`; `uv build $AM --wheel --out-dir $D/dist`
- [ ] `uv venv $D/venv --python 3.12`; `uv pip install --python $D/venv/bin/python $D/dist/agentic_mbse-*.whl --extra-index-url https://gitlab.com/api/v4/projects/69960816/packages/pypi/simple`
- [ ] `mkdir $D/target`; `env PATH=$D/venv/bin:$PATH VIRTUAL_ENV=$D/venv agentic-mbse init $D/target --assistant claude < /dev/null`
- [ ] With the same `PATH` and `VIRTUAL_ENV`, from `$D/target` (`uv run --directory $D/target …`): `uv run python -c 'from agentic_mbse.cli import get_docs_dir; print(get_docs_dir())'` must print `$D/venv/…/agentic_mbse_data/docs` (R2-A2).
- [ ] `SYSIDE_LICENSE_KEY=<from $AM/.env> agentic-mbse validate <seed models copy> --complete` passes.
- [ ] Record the commands and outcomes in `$E/dry-run/install.md` for O3. No commit needed until O3.

### O1: fresh delta check, then the fusion-tea F1 commit (SC6, SC7)

Needs P1–P8 committed. F1 copies template bytes, so a later template change means repeating steps 3–6 as a second F1 commit.

- [ ] **Delta check (SC6 condition, `design.md` § Validation Approach).** Dispatch a fresh non-author reviewer with a focused brief: six tool calls, 300 words.
  - Inputs: `docs/patterns/design-choices.md`, the template's three design-choice lines, `design.md` A1/A2, this plan's "Carried into this plan" items 1–4, and MR-7 at snapshot `REQUIREMENTS.md:89-107`.
  - Question: does each change after round 2 keep MR-7's force and scope?
  - Record the verdict in `$E/sc6-delta-check.md`. A fail is fixed in agentic-mbse before step 3.
- [ ] Preconditions:
  - `git -C $FT rev-parse --abbrev-ref HEAD` → `goal-layer-mr7`;
  - `git -C $FT status --short` → empty;
  - `git -C $FT merge-base --is-ancestor 2b1e9f9d5 HEAD`.
  - If `$FT` is absent: `git -C /home/reid/1cfe/fusion-tea worktree add -b goal-layer-mr7 $FT 2b1e9f9d5`.
- [ ] 1. Apply A6 to `$FT/modeling_project/REQUIREMENTS.md`. The `:87` heading and the `:89` authority line stay byte-identical. A6's body replaces `:91-107`, and whatever separates MR-7 from `## Process Requirements` stays. `:165` changes per A6, with today's date.
- [ ] 2. Insert A7 into `$FT/CLAUDE.md` after the "Design-choice preservation" section (`:5`), before `## Project Overview`.
- [ ] 3. Copy the templates:
  - `cp $AM/project_templates/MODELING_PROCESS.md.template $FT/modeling_project/MODELING_PROCESS.md`
  - `cp $AM/project_templates/GOAL_RUNBOOK.md.template $FT/work/orchestration/GOAL_RUNBOOK.md`
  - for `t` in goal, trail, learnings: `cp $AM/project_templates/$t.md.template $FT/work/orchestration/goal-templates/$t.md`
- [ ] 4. Anchors:
  - `grep -nx '### MR-7: Preserve Design Choices; Separate Evaluation from Design Selection' $FT/modeling_project/REQUIREMENTS.md`;
  - `grep -n 'mr-7-preserve-design-choices-separate-evaluation-from-design-selection' $FT/CLAUDE.md $FT/.project/active/demo-depth-rubric/application-policy.md` → both hit.
- [ ] 5. `cmp` each copied file against its template → silent (SC7).
- [ ] 6. `git -C $FT add` exactly the seven paths, then commit. Subject: "MR-7 applies agentic-mbse's design-choice pattern; goal files at the shipped bytes". Body: "Do not merge before the pin commit (F2)." and the agentic-mbse SHA the bytes came from. No push.
- [ ] 7. Capture to `$E/fusion-tea/`:
  - `git -C $FT diff 2b1e9f9d5..HEAD > branch-diff-F1.txt`;
  - `git -C $FT log --oneline 2b1e9f9d5..HEAD > branch-log.txt`.
  - Check each ledger destination appears in the diff, or already exists at `2b1e9f9d5`.

**Commit (agentic-mbse):** `Evidence: SC6 delta check and fusion-tea F1 branch diff`

**Progress notes:**

### O2: SC8 rehearsal on a disposable copy of the F1 tip

Follows `design.md` Appendix D2, and records each output into the F2 runbook's "Observed" slots.

- [ ] `R=/tmp/ft-rehearsal-$(date +%Y%m%d-%H%M%S)`; `git -C $FT worktree add --detach $R HEAD`
- [ ] Simulate F2 without the pin:
  - `git -C $R rm -r -q .claude/skills/run-goal .claude/skills/narrate-goal .agents/skills/run-goal .agents/skills/narrate-goal`;
  - delete the `!.claude/skills/narrate-goal/` and `!.claude/skills/run-goal/` lines from `$R/.gitignore`;
  - in `$R/AGENTS.md:5`, "Local goal and study skills" → "Local study skills";
  - `rm $R/modeling_project/MODELING_PROCESS.md $R/work/orchestration/GOAL_RUNBOOK.md $R/work/orchestration/goal-templates/{goal,trail,learnings}.md`.
- [ ] `uv run --project $AM agentic-mbse init $R < /dev/null > $E/fusion-tea/rehearsal/init.txt 2>&1`. Expect no "Preserving" line for goal or process files, and `MODELING_GUIDE.md` updated silently.
- [ ] Capture into `$E/fusion-tea/rehearsal/`:
  - `git -C $R status --short` → `git-status.txt`;
  - manifest entries in `$R/.agentic-mbse/install.json` against `sha256sum` of the runbook, three goal templates, the narrative test and `MODELING_PROCESS.md` → `manifest.txt`;
  - `git -C $R status --short -- work/orchestration/goals work/narratives` → `goal-data-status.txt` (expect empty);
  - `uv run --project $AM --directory $R pytest tests/orchestration --confcutdir=$R/tests/orchestration -o addopts= -p no:cacheprovider -q` → `pytest.txt`. Both tests must pass over the 12 narratives. On an import clash with this repo's `tests` package, add `--import-mode=importlib` and record it;
  - `grep -n '^## ' $R/work/orchestration/GOAL_RUNBOOK.md`, against the headings cited by `STUDY_POLICY.md:162`, the run-study runbook `:75,:219` and the goal files → `headings.txt`;
  - the SC8 chain walk → `chain.md`, each link with its resolved file. The links: `CLAUDE.md:5` → MR-7 heading → `design-choices.md`, through the resolver in this worktree's environment (record that fusion's pin `adbef75` lacks the file, so this shows the chain's shape, not fusion's runtime) → the "Process Selection" row in `$R/modeling_project/MODELING_PROCESS.md`. Then the installed goal template, runbook and `.agents/skills/run-goal/SKILL.md` → `design-choices.md` and `modeling_project/REQUIREMENTS.md`. Then `repair-goal-prompt.md:18`, listed and not edited.
- [ ] Fill the F2 runbook's "Observed in the rehearsal" slots from these files.
- [ ] `git -C $FT worktree remove --force $R`

**Commit (agentic-mbse):** `Evidence: fusion-tea re-init rehearsal (SC8)`

**Progress notes:**

### O3: SC4 dry run from a wheel

Follows `design.md` Appendix D3 and needs P1–P8. Independent of O1 and O2.

- [ ] Toolkit: repeat O0's first two steps in a fresh `D=/tmp/goal-dry-run-<stamp>`. Then `unzip -l $D/dist/*.whl | grep -E 'docs/patterns/design-choices.md|docs/goal-layer-decisions.md|GOAL_RUNBOOK.md.template'` → three hits.
- [ ] Target:
  - `mkdir $D/target`, then init with `PATH` and `VIRTUAL_ENV` set as in O0;
  - `cp -r $AM/tests/fixtures/sump_pump/seed/models/. $D/target/models/`;
  - `git -C $D/target init -q`, `git -C $D/target add -A`, `git -C $D/target -c user.name=dry-run -c user.email=dry-run@example.invalid commit -qm "Seed: sump/pump station"`;
  - repeat O0's resolver check from `$D/target`. If it does not print the scratch venv's packaged docs, stop and record; do not run the agent.
- [ ] Agent: run `claude -p "$(cat $D/brief.md)" --output-format stream-json --verbose > $D/transcript.jsonl` in `$D/target`, with:
  - `PATH=$D/venv/bin:$PATH`, `VIRTUAL_ENV=$D/venv` and `SYSIDE_LICENSE_KEY` set;
  - no user-level instructions, skills or memory reaching the agent, and authentication still working. The orchestrator picks the mechanism and the permission flags, and records both.
- [ ] The brief, saved as `$D/brief.md` and `$E/dry-run/brief.md`. This is the final wording within D3, and it names neither design choices nor the pattern:

```text
You are working in a SysML modeling project. Use the project's installed goal workflow, the run-goal skill, to ground a new goal and open its first round. Follow the installed files. No one is available to answer questions.

Question: Can the station model report whether the supplied drain pump keeps the sump basin from overflowing at the design inflow?

The operator's answers, given in advance:
- Goal slug: sump-overflow. Confirmed.
- Consumer: the station's design reviewer, who decides whether to keep the supplied pump.
- Answered when: the model reports, for the supplied pump, whether its installed capacity covers the flow needed at the design inflow.
- Limits: the runbook defaults.
- Reserved gates: the goal close, and any change to the goal's question.
- Close rule: the owner closes on § Answered when.
- Status: the operator agrees to `grounded` once all five field classes are filled.

Stop after writing `### T-001 start` in trail.md. If you reach any other point where the operator would have to answer, write a `### Stop` entry of kind `handoff` in trail.md saying what is needed, and stop.
```

- [ ] Evidence into `$E/dry-run/`:
  - `goal.md` and `trail.md` from `$D/target/work/orchestration/goals/sump-overflow/`;
  - `read-files.txt`: `jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") | [.name, (.input.file_path // .input.command // .input.pattern // "")] | @tsv' $D/transcript.jsonl`;
  - `init-message.json`: `jq 'select(.type=="system" and .subtype=="init")' $D/transcript.jsonl`, the user-level config the agent could see;
  - `install.md`: the wheel name, install command, isolation mechanism and permission flags. Never the license key.
- [ ] `$E/dry-run/checks.md`, pass or fail per line:
  - `goal.md` reads `grounded`, with all five field classes filled, and its grounding evidence cites the fixture;
  - `trail.md` holds `## Round 1`, `### Strategy revision`, `### T-001 scope` and `### T-001 start`;
  - `goal.md` § Invariants names the installed pump capacity as a supplied choice the goal preserves;
  - `read-files.txt` includes `design-choices.md` (B1);
  - the first resolver call printed the scratch venv's path (R2-A2);
  - no read path points into `$AM` or at fusion-tea.
- [ ] Failure handling:
  - If the agent stopped on a gap in the brief, fix that operator answer, re-run once, and keep both runs' evidence.
  - If B1 fails (`design-choices.md` was never read), record it and surface it to the owner as evidence against B1. Do not change D1 in this run.

**Commit (agentic-mbse):** `Evidence: fresh-target dry run from a wheel (SC4)`

**Progress notes:**

---

## Post-merge (not executed in this run): F2

After the owner merges `goal-layer-port`, F2 runs on `goal-layer-mr7` from `evidence/fusion-tea-runbook.md` (P8, rehearsed in O2): pin move, local goal skills removed, re-init, and the resolver hop in fusion-tea's own environment. Then the owner pushes and merges `goal-layer-mr7`. fusion `main` keeps its local goal files and pin `adbef75` until then (Invariant 6).

## Risk management

See `design.md` § Potential Risks. By phase:

- **P2:** A1 drifts from the approved text. Copy it verbatim and apply only carried items 1, 3 and 4. O1's delta check covers anything beyond that.
- **P3:** a rewrapped paragraph turns one hunk into many. Copy the bytes first and check `diff -U0` before committing.
- **P4:** the `--dev` link resolves the test's root to this repo. The narrative test's `dev=True` case catches it.
- **P5:** a goal-text path missing in a fresh target. Reword it as target-supplied; never allowlist it silently.
- **O1/O2:** writes to the fusion-tea worktree blocked. Fall back to an owner-run script. On a pytest import clash, use `--import-mode=importlib`.
- **O3:** the wheel's dependencies, the syside license, `uv run` venv discovery, or an agent that stops to ask. O0's smoke check, the resolver pre-check and the `handoff` instruction cover these. A false B1 goes to the owner.

## After this plan

`/_my_audit` against the spec, then `/_my_close`, which files the two follow-ups in `evidence/README.md` and moves the Item 4 list to the epic. Then `/_my_pre_pr`. The owner merges agentic-mbse, F2 runs, and the owner merges fusion-tea.

---

**Status**: Implementation in progress (P1–P7 done)
