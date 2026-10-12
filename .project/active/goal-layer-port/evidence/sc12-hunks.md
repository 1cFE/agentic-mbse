# SC12: Hunk Classification of the Ported Goal Files

**Item:** goal-layer-port (`WRAP-SPLIT` Item 2), Phase 7. **Written:** 2026-10-11.

**Result.** Every hunk in every shipped goal-layer file has exactly one class. No hunk changes the method. 41 hunks across six files; `learnings.md.template` has none.

## How the diffs were made

Each shipped file is compared against its fusion-tea original in the read-only snapshot `.orchestrate-logs/fusion-tea-snapshot/` (fusion-tea `2b1e9f9d5`). The diffs are in `sc12/`, one per file:

```bash
S=.orchestrate-logs/fusion-tea-snapshot; E=.project/active/goal-layer-port/evidence/sc12
diff -U0 $S/.claude/skills/run-goal/SKILL.md          skills/run-goal/SKILL.md                         > $E/run-goal.diff
diff -U0 $S/.claude/skills/narrate-goal/SKILL.md      skills/narrate-goal/SKILL.md                     > $E/narrate-goal.diff
diff -U0 $S/work/orchestration/GOAL_RUNBOOK.md        project_templates/GOAL_RUNBOOK.md.template       > $E/runbook.diff
for t in goal trail learnings; do diff -U0 $S/work/orchestration/goal-templates/$t.md project_templates/$t.md.template > $E/$t.diff; done
diff -U0 $S/tests/orchestration/test_goal_contract.py project_templates/test_narrative_links.py.template > $E/narrative-test.diff
grep -c '^@@' $E/*.diff
```

Hunk counts: `run-goal.diff` 10, `narrate-goal.diff` 4, `runbook.diff` 21, `goal.diff` 1, `trail.diff` 1, `learnings.diff` 0, `narrative-test.diff` 4. Each count equals the row count of that file's table below.

## The six classes

From spec SC12, plus design D17:

- **Consumer path generalized.** A fusion-tea path, script or status note becomes general wording. Includes the interim research wording (D10) and the two-PM condition.
- **Design-choice hook generalized.** An MR-7 hook becomes a pointer to the design-choice pattern and the target's requirements file, keeping its procedure. Includes the trigger-table row.
- **Decision-record citation.** A `.project/adr/` or fusion record path becomes a citation of the goal-layer decision record.
- **Recorded-practice addition.** Text naming what fusion-tea goals already do, such as the goal-close heading (D11).
- **Deletion with ledger row.** Fusion-only text removed, with its fusion-tea home in the ledger.
- **Bundle envelope.** The frontmatter shape and shared preface `tests/test_shipped_text.py` requires (D17).

Any hunk that drops a consumer-specific instruction names its ledger row, whatever its class. Ledger rows are named by their "Text left out" lead in `.project/active/wrap-split-migration-ledger.md` § Item 2 (design Appendix C, plus one row for the ADR-register check, added in Phase 8 at the orchestrator's call).

## `skills/run-goal/SKILL.md` (`run-goal.diff`, 10 hunks)

| Id | Hunk | Class | Change | Ledger row |
|---|---|---|---|---|
| RG-1 | `@@ -12 +12 @@` | Bundle envelope | `allowed-tools` in list form; same seven tools | — |
| RG-2 | `@@ -13,0 +14,2 @@` | Bundle envelope | `metadata:` / `kind: workflow` | — |
| RG-3 | `@@ -15,0 +18,3 @@` | Bundle envelope | The shared preface and its blank lines, as in `skills/orchestrate-modeling/SKILL.md` | — |
| RG-4 | `@@ -20 +25 @@` | Decision-record citation | "live in `.project/adr/`" → "live in the goal-layer decision record (`GOAL_RUNBOOK.md` § The decisions behind this)" | Goal-layer ADRs as the "why" |
| RG-5 | `@@ -49 +54 @@` | Deletion with ledger row | Drops the Codex sentence. Its `.agentic-mbse/codex.md` half is now in the preface (RG-3); its `.project/codex-test-setup.md` half is fusion's test worktree. The kept sentence is unchanged | Codex test worktree setup |
| RG-6 | `@@ -53 +58 @@` | Design-choice hook generalized | A8 `run-goal:53`, byte-for-byte: the requirements file and the design-choice pattern instead of "including MR-7"; "design-choice steps"; "quality target" for "depth target" | MR-7 hooks |
| RG-7 | `@@ -55 +60 @@` | Consumer path generalized | Stage instructions → "the stage's installed skill"; launcher → "(`uv run` unless the project names another)". The other three sentences are unchanged | Codex test worktree setup |
| RG-8 | `@@ -61 +66 @@` | Consumer path generalized | Interim research wording (D10): "Use the research procedure the project's instructions name; otherwise `/research` and `/manage-sources`." The internal-sources sentence is unchanged | Research seam guide, request files, scripts, `research-acquire`, clean-room screen |
| RG-9 | `@@ -63 +68 @@` | Consumer path generalized | Interim research wording. Kept: direct execution or delegation to fresh agents, both runtimes' tool names, the brief's contents and its deposit at `evidence/`, the main agent's freedom. Removed: request files, `research-acquire.md`, the two scripts, the named clean-room protocol, which becomes "any source-quarantine rule the project states" | Research seam guide, request files, scripts, `research-acquire`, clean-room screen |
| RG-10 | `@@ -73 +78 @@` | Decision-record citation | "`.project/adr/` … indexed in `INDEX.md`" → "The goal-layer decision record (`GOAL_RUNBOOK.md` § The decisions behind this) … Records 001–007." | Goal-layer ADRs as the "why" |

## `skills/narrate-goal/SKILL.md` (`narrate-goal.diff`, 4 hunks)

| Id | Hunk | Class | Change | Ledger row |
|---|---|---|---|---|
| NG-1 | `@@ -5 +5 @@` | Bundle envelope | `allowed-tools` in list form; same six tools | — |
| NG-2 | `@@ -6,0 +7,2 @@` | Bundle envelope | `metadata:` / `kind: workflow` | — |
| NG-3 | `@@ -8,0 +11,3 @@` | Bundle envelope | The shared preface and its blank lines | — |
| NG-4 | `@@ -77 +82 @@` | Consumer path generalized | Validation step: `tests/orchestration/test_goal_contract.py` → `tests/orchestration/test_narrative_links.py`, the installed test (D9). fusion's command also ran the ADR-register check, which the installed test does not carry | Narrative check path; ADR-register check |

## `project_templates/GOAL_RUNBOOK.md.template` (`runbook.diff`, 21 hunks)

| Id | Hunk | Class | Change | Ledger row |
|---|---|---|---|---|
| RB-1 | `@@ -7 +7 @@` | Decision-record citation | "is in `.project/adr/`" → "is in the goal-layer decision record" | Goal-layer ADRs as the "why" |
| RB-2 | `@@ -13 +13 @@` | Consumer path generalized | Two-PM condition: "a second PM where the target runs one (for example a coding PM in `.project/`)"; "the research procedure"; "the study procedure where one is installed" | Coding PM in `.project/` as a premise |
| RB-3 | `@@ -31 +31 @@` | Decision-record citation | Surface row: `.project/adr/` → "The goal-layer decision record (§ The decisions behind this)"; writer → "agentic-mbse, as a dated record" (D7). The surface and its question, "Why is it this way?", are unchanged | Goal-layer ADRs as the "why" |
| RB-4 | `@@ -41 +41 @@` | Decision-record citation | The critic quote's source: concept path → "goal-layer decision record, Sources". The quote and its `[OWNER]` grade are unchanged | Concept path, probe-record path, "Item 4 proof run" |
| RB-5 | `@@ -73,0 +74 @@` | Design-choice hook generalized | New trigger-table row mirroring the "Process Selection" design-choice row: its condition cell is that row's, word for word, and its response cell is A8's. A contract test keeps the two conditions identical (audit advisory 1, 2026-10-12) | — |
| RB-6 | `@@ -84 +85 @@` | Design-choice hook generalized | A8 `:84`: the first two sentences name the design-choice pattern and its resolver command; the last two are unchanged | MR-7 hooks |
| RB-7 | `@@ -94 +95 @@` | Decision-record citation | The probe-record path → "goal-layer decision record, ADR-0003 (2026-08-27 amendment)". The amendment's grade and account are unchanged | Concept path, probe-record path, "Item 4 proof run" |
| RB-8 | `@@ -100 +101 @@` | Design-choice hook generalized | A8 `:100`: "justification under the design-choice pattern"; "Score or quality-target attainment"; "the design-choice assessment". The depth-rubric sentence is deleted | MR-7 hooks; Depth-rubric policy pointer |
| RB-9 | `@@ -106 +107 @@` | Consumer path generalized | Study runbook and policy paths → "The study layer owns the term and its identity rules, where a target installs one." The round bound and the pin definition are unchanged | Study runbook and policy, discovery-log path, join test |
| RB-10 | `@@ -139 +140 @@` | Design-choice hook generalized | A8 `:139`: "For tasks affecting design choices, include the applicable requirements, the design-choice pattern …"; "passing baseline or score" | MR-7 hooks |
| RB-11 | `@@ -205 +206 @@` | Recorded-practice addition | Appends "The owner's close is recorded as `## Goal close — YYYY-MM-DD` at the end of `trail.md`, with the ruling and the disposition." (D11) | — |
| RB-12 | `@@ -232 +233 @@` | Consumer path generalized | Study-store and research-binary citations in general words; the citation rule itself is unchanged | Study-store and R2 citation specifics |
| RB-13 | `@@ -260 +261 @@` | Consumer path generalized | `exploration/<pkg>/studies/DISCOVERY_LOG.md` → "The study layer's discovery log" | Study runbook and policy, discovery-log path, join test |
| RB-14 | `@@ -262 +263 @@` | Decision-record citation | "the Item 4 proof run" → "the 2026-08-27 proof run (goal-layer decision record, ADR-0003)" | Concept path, probe-record path, "Item 4 proof run" |
| RB-15 | `@@ -270 +271 @@` | Consumer path generalized | The named join test → "the study layer's join check" | Study runbook and policy, discovery-log path, join test |
| RB-16 | `@@ -272 +273 @@` | Consumer path generalized | "an ADR" → "the target's decision record". In fusion-tea that record stays `.project/adr/` | Goal-layer ADRs as the "why" |
| RB-17 | `@@ -276 +277 @@` | Consumer path generalized | Run-study runbook and `STUDY_POLICY.md` → "the study layer's runbook … its policy, where a target installs one" | Study runbook and policy, discovery-log path, join test |
| RB-18 | `@@ -286 +287 @@` | Consumer path generalized | Status note "Every seam is native now." → "Each seam is the procedure the target installs." The no-silent-repair sentence is unchanged | Research seam guide, …; Integration seam, `integrate.py`, ADR-0009, guide, history |
| RB-19 | `@@ -288,2 +289,2 @@` | Consumer path generalized | The `research` bullet becomes D10's wording and the `integrate` bullet "the integration procedure the target installs, where it has one". Fusion's scripts, guides, ADR-0009 and repair history leave. Each seam's invocation and native return stay in the seam table above (template `:281-285`), unchanged | Research seam guide, …; Integration seam, `integrate.py`, ADR-0009, guide, history |
| RB-20 | `@@ -295 +296 @@` | Decision-record citation | Appends where the records are: `goal-layer-decisions.md` through the `get_docs_dir()` resolver | — |
| RB-21 | `@@ -299,7 +300,7 @@` | Decision-record citation | ADR links into `../../.project/adr/` → plain `ADR-000N` ids. The ADR-0006 summary also takes the two-PM wording: "Citing a second PM's records by path and digest" (plan, "Found while planning") | Goal-layer ADRs as the "why"; Coding PM in `.project/` as a premise |

## `project_templates/goal.md.template` (`goal.diff`, 1 hunk)

| Id | Hunk | Class | Change | Ledger row |
|---|---|---|---|---|
| GT-1 | `@@ -29 +29 @@` | Design-choice hook generalized | A8 `goal.md:29`, byte-for-byte: "For MR-7" → "For a model-changing goal, apply the design-choice pattern (…)" | MR-7 hooks |

## `project_templates/trail.md.template` (`trail.diff`, 1 hunk)

| Id | Hunk | Class | Change | Ledger row |
|---|---|---|---|---|
| TT-1 | `@@ -82,0 +83,5 @@` | Recorded-practice addition | Appends the `## Goal close — YYYY-MM-DD` section with **Ruling** and **Disposition** lines (D11) | — |

## `project_templates/learnings.md.template` (`learnings.diff`, 0 hunks)

Byte-identical to fusion's `goal-templates/learnings.md`; `cmp` is silent.

## `project_templates/test_narrative_links.py.template` (`narrative-test.diff`, 4 hunks)

| Id | Hunk | Class | Change | Ledger row |
|---|---|---|---|---|
| NT-1 | `@@ -1 +1 @@` | Deletion with ledger row | Docstring drops "Records remain findable", the register check's half | ADR-register check |
| NT-2 | `@@ -7 +6,0 @@` | Deletion with ledger row | `import yaml`, used only by the register check | ADR-register check |
| NT-3 | `@@ -9,23 +8,2 @@` | Deletion with ledger row | Removes `ADR_FILE`, `_frontmatter` and `test_register_is_coherent`. Its two added lines are the module-level `REPO_ROOT` and its comment, which NT-4 uses; `diff` joins them to this hunk because they are adjacent | ADR-register check |
| NT-4 | `@@ -43,3 +21,2 @@` | Consumer path generalized | fusion's `repo_root` fixture (its `tests/orchestration/conftest.py`, rooted with `resolve()`) → the module-level `REPO_ROOT`, rooted with `absolute()` so a `--dev` link still finds the target (D9). One of fusion's three blank lines before the test goes. `_local_link_targets` and the test body are unchanged | — |

## Method check

The runbook's method lists (Invariant 2) sit at these fusion lines: the five surfaces `:25-31`; the fresh-review definition and handoff `:37-62`; the six close triggers `:108-117`; the task scope, the six outcomes, the five decision fields and the retry rule `:131-156`; the checkpoint and its cap `:162-178`; the fresh review `:180-205`; the limits `:247-256`.

Three hunks fall inside those ranges, and none changes a step, a list member or a value:

- RB-3 changes where the decision-record surface lives and who writes it. There are still five surfaces, each with its question.
- RB-4 changes only the source citation of the critic quote. The definition of a fresh review is unchanged.
- RB-11 appends where the owner's close is recorded. The close rule itself is unchanged.

`tests/test_goal_layer.py::test_runbook_keeps_its_sections_and_limits` pins the sixteen H2 headings and the three limit values.

## Goal-hook rows of the SC6 crosswalk

Phase 7 re-checked the goal-hook rows of `sc6-crosswalk.md` against the ported text. Every destination holds: each sentence sits in the section the row names, with the wording the row gives. No location needed correcting. The crosswalk now records the ported line numbers.
