# Epic: Wrap the agentic-mbse / fusion-tea split

**Epic ID**: WRAP-SPLIT
**Status**: Draft
**Priority**: High
**Created**: 2026-10-06
**Estimated Effort**: ~9 days across 5 items (one item lives in sysml-codegen)

---

## Executive Summary

Finish the toolkit so that every general capability built during the fusion-tea work ships from the repo that owns its dependencies and installs like everything else, and so that agentic-mbse's shipped surfaces read as general rules and practices rather than as instructions for one consumer. This is the "wrap" for the goal layer, the study layer, the research acquisition seam, the MR-7 design-choice principle, and the consumer-specific pointers that accumulated in shipped docs, skills and templates.

**Critical Success Factor**: Each of the four skills installs from its owning repo's installer into a fresh target with no hand-copying from fusion-tea: `run-goal`, `narrate-goal` and `research-acquire` (with the `agentic-mbse research` CLI it calls) from `agentic-mbse init`; `run-study` and its tools from `sysml-codegen install-commands`. Every shipped instruction reads as a general rule; fusion examples may remain where they illustrate one.

**Owner decisions carried in** ([OWNER], 2026-10-06 conversation):
- The study layer (the `run-study` skill and the tools it calls: `scripts/study/*`, `integrate.py`) ships from sysml-codegen, which already depends on agentic-mbse, owns the generated-package contracts the tools read, and already has an `install-commands` subcommand. agentic-mbse ships the goal layer.
- Fusion vocabulary is acceptable in examples. The bar is that the text reads as a general rule or practice consistent with agentic-mbse's philosophy, not that the words are absent. What must go: pointers into fusion-tea or sysml-codegen internals as authority, hard-coded machine paths, consumer requirement numbers (MR-7), and instructions that only make sense for one project.
- Keep the item count low.
- [OWNER-VERBATIM] 2026-10-06, on the research seam: "yes, we need this capability in agentic-mbse". The seam ports as Item 5 (resolves product-lens epic-F1).
- No loss of information for fusion-tea. Any instruction removed from agentic-mbse's shipped surfaces because it is consumer-specific is migrated into fusion-tea's own files (its `REQUIREMENTS.md`, `CLAUDE.md`, annexes, or local skills), not deleted.

---

## Why This Epic?

**Current State**:
- `run-goal`, `narrate-goal` and `run-study` live only in fusion-tea's `.claude/skills/`, whitelisted in its `.gitignore`, with their runbook, templates, policy, scripts, tests and ADRs scattered across fusion-tea. No installer knows them.
- MR-7 ("preserve design choices; separate evaluation from design selection") is a fusion-tea requirement whose enforcement text was hand-inserted into fusion-tea's copy of the tool-owned `MODELING_PROCESS.md`. A re-init deletes it. agentic-mbse's template carries only a one-sentence seed of the principle.
- agentic-mbse's shipped surfaces carry ~96 fusion- or consumer-specific items: the plant-idiom and package-naming pattern docs, the source-index example, the sysml-conventions skill, formalize-intent, two fusion PDFs as the `extract --check` corpus, a toroidal-field-coil example in `README.md.template`, hard-coded `/home/reid` paths, and ~25 fusion-flavoured test files.
- Content and packaging have split: `main` holds the September workflow bodies that fusion-tea runs; the native Claude/Codex installer branch (`native-claude-codex-skills`, at `955295b` plus uncommitted remediation) forked 57 commits ago and is stale on eleven workflow bodies and the process template. Any new skill registered today lands in the wrong place or twice.

**Future State**:
- One reconciled installer source: `main`'s content in the native `skills/` + `adapters/` shape.
- Goal and study layers are installed skills with tool-owned runbook/templates and a user-owned study-policy template; the design-choice principle is a general section of the shipped process template.
- Study execution tools live in sysml-codegen, which already owns the generated-package contracts they read and already depends on agentic-mbse.
- Shipped surfaces state general rules; fusion-flavoured examples are labelled as examples, and no shipped text points into a consumer repo or a developer's home directory as authority.
- The research acquisition seam (the `research-acquire` skill, its bookkeeping and registry code) ships from agentic-mbse as an installed skill plus an `agentic-mbse research` CLI.
- fusion-tea keeps only what is fusion-specific: MR-7 itself, package annexes, goal and narrative data, concept pipeline, hold-out instance, Zotero ingest.

---

## Source Documents

- `.project/research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md` (research) — the audit this epic implements; carries the leakage inventory, dependency-direction check, and open questions.
- `.project/active/native-skill-distribution/spec.md` (spec, draft, product-lens CLEAR) — existing contract for the native source reconciliation; adopted as Item 1 rather than respecified.
- `/home/reid/1cfe/agentic-mbse-native-skills/.project/active/native-skills/{plan,remediation,audit}.md` (plan/evidence) — native installer requirements and accepted remediations; inherited, not reopened.
- fusion-tea `.project/concepts/goal-driven-model-development-harness.md` (concept) — `[OWNER]` goals are general to systems engineering; owner stop rules.
- fusion-tea `.project/concepts/run-study-skill.md` and `run-study-skill-design.md` (concept, concept-design) — owner factoring of the study capability as skill + runbook + policy + tools; `[OWNER-VERBATIM]` intake and role statements.
- fusion-tea `modeling_project/REQUIREMENTS.md` § MR-7 and `.project/active/modeling-intent-enforcement/spec.md` (requirement, spec) — the `[OWNER-VERBATIM]` sizing statement and the enforcement the general principle must preserve.
- `.project/mental-alignment-v2/runs/20261006-150340_research-process-end-state_fresh.html` (mental model, owner-reviewed 2026-10-06) — the end-state research process and the port table Item 5 specs against. Supersedes its synthesis `.md` on two points (research-acquire is a skill, not a decision; the delegated-approval question).

---

## Success Criteria

- [ ] A clean install from the reconciled source exposes the same 15 workflow bodies and process template that `main` holds today; the native worktree's eleven stale bodies are gone.
- [ ] `run-goal` and `narrate-goal` are listed by `agentic-mbse install-commands --list`, install into a fresh target, and their runbook and templates resolve from installed paths with no reference to fusion-tea, MR-7, `.codex-test`, or `exploration/stellarator_e2e`.
- [ ] `run-study` (skill, runbook, record template, study-policy template) installs from `sysml-codegen install-commands` into a fresh target, and its runbook names the package annex and the installed tools rather than fusion-tea paths.
- [ ] The shipped `MODELING_PROCESS.md.template` carries a general "preserve design choices" section and a process-selection row for changed variable roles; fusion-tea's two inserted MR-7 paragraphs become redundant and fusion-tea's `REQUIREMENTS.md` MR-7 is unchanged.
- [ ] `scripts/study/*`, its schemas, and `integrate.py` run from sysml-codegen against a neutral fixture package; fusion-tea's copies are retired or thin wrappers; `tests/study/test_generic.py`'s invariant (tools name no package) still holds in the new home.
- [ ] Every shipped surface in agentic-mbse (`claude/` or `skills/`, `docs/`, `project_templates/`, `src/`) passes a read-through against the owner's bar: general rule or practice, examples labelled as examples. Concretely: no shipped text cites a fusion-tea or sysml-codegen `.project/`, `tests/fixtures/` or `exploration/` path as authority; no shipped or test file hard-codes `/home/reid`; `docs/source-index.md`'s worked example does not point at a developer's local PyFECONS checkout; the one skipped test that requires consumer models is removed. Fusion-flavoured examples (plant-idiom pins, `FusionTea_*` naming, check-corpus PDFs, `'Toroidal Field Coil'`) may stay where they are presented as examples.
- [ ] Full suites pass in agentic-mbse and sysml-codegen; fusion-tea re-installs from both installers with its protected files preserved and its three local skills removed in favour of the installed ones.
- [ ] [OWNER] No loss of information for fusion-tea: every consumer-specific instruction removed from agentic-mbse during the sweep or the ports is recorded in a migration ledger with its new fusion-tea location, and fusion-tea's working tree holds it at that location before the agentic-mbse removal merges.
- [ ] [OWNER] fusion-tea's MR-7 enforcement is intact after re-init: its `REQUIREMENTS.md` MR-7 is unchanged, and the hooks that lived in the tool-owned `MODELING_PROCESS.md`, `GOAL_RUNBOOK.md` and `goal.md` template are either covered by the shipped general section or re-homed in fusion-tea's user-owned files.
- [x] The `[INFERRED]` line in `native-skill-distribution/spec.md` saying goal/study procedures stay target-owned is amended to the owner's 2026-10-06 decision (Item 1 spec update, 2026-10-09).
- [ ] `research-acquire` installs from `agentic-mbse init`; `agentic-mbse research open | log | close | register | retire | verify` runs against fusion-tea's existing `knowledge/` with no data migration; fusion-tea's two seam scripts are deleted and its Zotero ingest registers through the installed package.

---

## Backlog Items

Owner decisions in the header apply to every item. Each item's spec inherits the two owner success criteria (no loss of information for fusion-tea; MR-7 enforcement intact) and writes to the shared migration ledger at `.project/active/wrap-split-migration-ledger.md` (Item 2 creates and owns the file; Items 3 and 4 append under their own headings).

### Item 1: Reconcile native installer source with `main`

**Type**: Code/Integration
**Effort**: 1.5 days (spec: adopted, updated to this scope 2026-10-09; design 2h; plan 1h; execute 8h)
**Dependencies**: None

**Objective**: Make the native Claude/Codex installer branch carry `main`'s current workflow content so there is one installer source to register new skills in.

**Current State**:
- ✅ `main` (`c37ff53`) holds the September workflow bodies and the rewritten `MODELING_PROCESS.md.template`; fusion-tea's installed copies match them.
- ✅ Branch `native-claude-codex-skills` (worktree `/home/reid/1cfe/agentic-mbse-native-skills`, `955295b` + uncommitted A–K remediation) holds the `skills/` + `agents/` + `adapters/` layout, `skill_bundles()` discovery, hash manifest, Codex role registration.
- ⚠️ The branch forked at `88e2489`, 58 commits behind `main` as of 2026-10-09 (PR #16 added `/research` and toolkit-awareness changes); eleven workflow bodies differ by 30–110 lines and the process template by 865 lines.
- ⚠️ `adapters/{claude,codex}.md` still say "fresh stages require new agents"; fusion-tea's `.agentic-mbse/codex.md:7` carries the September author-continuity rule.
- ⚠️ `MODELING_GUIDE.md.template:279` documents only the legacy `get_docs_dir()` pattern resolver; the native installer copies patterns to `.agentic-mbse/patterns/`.
- ❌ Independent re-review of the A–K remediations has not happened (`audit.md` still "Needs Work").

**Scope**:
1. **Content rebase**: replace the branch's workflow bodies and templates with `main`'s content, keeping the branch's envelope changes (frontmatter, "Before executing this skill" preface, paragraph reflow) and its runtime adaptation (body rewrites that make a skill work under both Claude Code and Codex, such as `.agents/skills/` script paths). Classify each of the sixteen observed differences per the existing spec: portable (take `main`), target-owned (leave in fusion-tea), intentional.
2. **Adapter text**: carry the author-continuity sentence into both adapters; describe both pattern-directory modes in `MODELING_GUIDE.md.template`.
3. **Integrate**: bring the branch onto `main` (rebase or merge; design decides) with the uncommitted remediation committed first. State the fate of `scripts/replicate_setup.sh`: on the branch it is already a thin wrapper around `init` (native `CLAUDE.md:212`); confirm that holds after the merge and update CLAUDE.md "Change Coordination" so Item 2's `cmd_init` changes have one place to land (product-lens epic-F2).
4. **Verify**: fresh install into a scratch target in both runtimes; inventory test ties `skills/*/SKILL.md` to installed files; the A–K remediation re-review the existing audit asked for, bounded to installer behaviour.

**Out of Scope**:
- New workflow names, new runtimes, token-savings measurement, fusion-tea's full study suite.
- Registering `run-goal`, `narrate-goal` (Item 2) or anything study-related (Item 3).

**Success Criteria**:
- [ ] Every one of the sixteen bundle differences has a recorded disposition (spec criterion 1).
- [ ] After install, the fifteen workflow bodies and the process template equal `main`'s content modulo envelope; a diff script in the item's evidence shows it.
- [ ] Both adapters carry the author-continuity rule; the guide template names both pattern locations.
- [ ] Fresh Claude and Codex installs discover all workflows and expert roles; re-init preserves protected files and does not write through symlinks.
- [ ] Branch merged to `main`; `uv run pytest tests/` passes; the inferred fresh-stage-context rule in the native plan is reconciled with the September risk-based review (spec open question 3).

**Required Reading**: `.project/active/native-skill-distribution/spec.md`; `/home/reid/1cfe/agentic-mbse-native-skills/.project/active/native-skills/{plan,remediation,audit}.md`; `/home/reid/1cfe/fusion-tea/.project/active/harness-right-size/{report.md,installed.json}`; research § 4.

**Deliverables**:
- `.project/active/native-skill-distribution/{design,plan}.md` (spec already exists)
- Difference-disposition table and install verification record under `.project/active/native-skill-distribution/evidence/`
- Merged branch

---

### Item 2: Port the goal layer and the design-choice principle

**Type**: Implementation (instruction text, templates, installer registration)
**Effort**: 2 days (spec 2h, design 2h, plan 1h, execute 10h)
**Dependencies**: Item 1 (register once, on the reconciled `skills/` layout)

**Objective**: Ship `run-goal` and `narrate-goal` with their runbook, templates and contract test from agentic-mbse, and ship MR-7's principle as a general section of the process template.

**Current State**:
- ✅ fusion-tea `.claude/skills/{run-goal,narrate-goal}/SKILL.md`, `work/orchestration/GOAL_RUNBOOK.md` (305 lines), `goal-templates/{goal,trail,learnings}.md`, `tests/orchestration/test_goal_contract.py` exist and are exercised by eleven narratives and a dozen goal runs.
- ✅ `claude/commands/orchestrate-modeling.md:21,53` on `main` already writes `work/orchestration/` and defers to the target's goal/study workflow.
- ✅ `MODELING_PROCESS.md.template` "Architecture & Design" already says "Distinguish quantities with different meanings, such as installed capacity and operating demand."
- ⚠️ The runbook, `goal.md` template and `run-goal` skill cite fusion-tea paths at the lines listed in research § 1a (`.project/adr/`, MR-7, `.codex-test/run`, research-seam scripts, `exploration/<pkg>/studies/`, a probe record, the depth-rubric policy).
- ⚠️ fusion-tea's tool-owned `MODELING_PROCESS.md` carries two inserted MR-7 paragraphs that re-init deletes.
- ❌ No ADR home, no `work/orchestration/goals/` or `work/narratives/` in `cmd_init`, no inventory entries.
- ❓ ADR-0006 assumes a two-PM split (`.project/` + `work/`); needs stating as a condition, not a premise.

**Scope**:
1. **Skills**: add `run-goal` and `narrate-goal` to `skills/`; parameterize consumer paths to "the target project's requirements file", "the package annex / study procedure the target installs", "the installed research procedure"; delete `.codex-test` lines; point research-seam references at "the installed research procedure" as interim wording, which Item 5 replaces with the shipped skill and CLI names.
2. **Templates**: `GOAL_RUNBOOK.md` and the three goal templates as tool-owned templates to `work/orchestration/`; `cmd_init` creates `work/orchestration/goals/` and `work/narratives/`; add to `TOOL_OWNED_TEMPLATES` and `DEV_MODE_GITIGNORE_PATHS` (or the native equivalents); `test_goal_contract.py` as a template beside `test_models_example.py.template`, with the ADR-register half conditional on an ADR directory existing.
3. **Decisions doc**: one shipped `docs/goal-layer-decisions.md` condensing fusion-tea ADR-0001..0007 with their `[OWNER]`/`[AGENT]` grades and fusion-tea provenance; the runbook cites it instead of `.project/adr/`. Design must settle authority (product-lens smell 1, two hand-synchronized copies): proposed stance is that the shipped doc is a dated snapshot cited by fusion-tea path and commit and is the authority for installed targets; fusion-tea's live ADRs govern fusion-tea only, and a later fusion-tea amendment reaches targets through an ordinary toolkit change, not by reference.
4. **Design-choice principle**: a short "Preserve design choices" section in `MODELING_PROCESS.md.template` and a process-selection row ("Changed design-variable role, automatic sizing or selection policy, or demand-derived installed capacity → focused independent design review of actual bindings and downstream consumers; insufficient/sufficient supplied-design tests where applicable"); an invariants bullet in the shipped `goal.md` pointing at the target's requirements file.
5. **Migration ledger**: create `.project/active/wrap-split-migration-ledger.md`; record each removed MR-7 hook with its fusion-tea destination (fusion-tea `REQUIREMENTS.md` MR-7 "Enforcement" paragraph, or `CLAUDE.md`). The `[INFERRED]` line in `native-skill-distribution/spec.md` was already amended in Item 1's spec update (2026-10-09).

**Out of Scope**:
- `run-study`, `STUDY_POLICY.md`, `scripts/study/*`, `integrate.py` (Item 3).
- The research seam (`research-acquire`, `research_seam.py`, `source_registry.py`): Item 5.
- Changing fusion-tea's `REQUIREMENTS.md` MR-7 text or its goal/narrative data.

**Success Criteria**:
- [ ] `agentic-mbse install-commands --list` names `run-goal` and `narrate-goal`; a fresh init contains the runbook, three templates, the two directories and the contract test template.
- [ ] `grep -E "fusion-tea|MR-7|\.codex-test|stellarator|exploration/" ` over the shipped runbook, templates and the two skills returns nothing; every former consumer path has a generic replacement or a ledger row.
- [ ] A fresh target can ground a goal and open a round following only installed files (dry run recorded in evidence).
- [ ] The process template carries the new section and table row; fusion-tea's two inserted paragraphs are covered by it or re-homed, and fusion-tea's `REQUIREMENTS.md` MR-7 is byte-identical.
- [ ] `docs/goal-layer-decisions.md` preserves each ADR's grade and cites fusion-tea by path and commit.
- [ ] Ledger rows exist for every removed consumer-specific line; fusion-tea's working tree holds each destination before the agentic-mbse change merges.
- [ ] `uv run pytest tests/` passes.

**Required Reading**: research § 1a, § 2, § 5; fusion-tea `work/orchestration/GOAL_RUNBOOK.md`; fusion-tea `.project/concepts/goal-driven-model-development-harness.md` (owner stop rules, line 198); fusion-tea `modeling_project/REQUIREMENTS.md` § MR-7 and `.project/active/modeling-intent-enforcement/spec.md`; `project_templates/MODELING_PROCESS.md.template`; CLAUDE.md "Init File Ownership".

**Deliverables**:
- `.project/active/goal-layer-port/{spec,design,plan}.md`
- `skills/run-goal/`, `skills/narrate-goal/`, four new templates, `docs/goal-layer-decisions.md`, installer and test changes
- `.project/active/wrap-split-migration-ledger.md` (created here)

---

### Item 3: Move the study layer to sysml-codegen

**Type**: Code/Integration (external work in `/home/reid/1cfe/sysml-codegen`; tracked here)
**Effort**: 2 days (spec 2h, design 3h, plan 1h, execute 10h; the installer ownership work is inside this budget, at the expense of fixture breadth)
**Dependencies**: None on Items 1–2 (different repo). Loose coupling: `run-study` cites the goal runbook's review-scope section; the ported text cites "the installed goal runbook" and works whether or not Item 2 has landed.

**Objective**: Ship `run-study` and the study tools from sysml-codegen, which owns the generated-package contracts they read and already depends on agentic-mbse.

**Current State**:
- ✅ fusion-tea `.claude/skills/run-study/{SKILL,runbook,record-template}.md`; `scripts/study/{common,identity,manifest,indicators,preflight,verify,read_coverage}.py` + 7 schemas; `scripts/integrate.py`; `modeling_project/STUDY_POLICY.md`; 55 study tests of which about twelve are package-agnostic.
- ✅ `tests/study/test_generic.py` already pins the invariant that tools name no package.
- ✅ sysml-codegen has `claude/commands/teax-completion.md` and an `install-commands` subcommand (`src/sysml_codegen/cli/__init__.py:1112`).
- ⚠️ Runbook steps 8–9 name the teax route and `StudyRunner`; `SKILL.md:160-163` and `record-template.md:61-62` say "LCOE" where "objective" is meant.
- ⚠️ `scripts/study/*` imports as `scripts.study` (repo root on `sys.path`); `integrate.py` reads `tests/test_dependency_provenance.py` and uses a `fusion-tea-integration-backup-` prefix.
- ⚠️ `STUDY_POLICY.md` §6–8 and §10 and all worked examples are fusion/demo-specific; §1–5, §9, §11 are general.
- ❓ Whether the tools import cleanly as a package without the `scripts.` convention (first check in the spec stage).

**Scope**:
1. **Skill and installer**: `run-study` SKILL, runbook, record template into sysml-codegen's installable commands/skills; "LCOE" → "objective"; route step rewritten to "the execution route the target's study policy names, supplied by the package annex". Extend `sysml-codegen install-commands` with the tool-owned/user-owned distinction agentic-mbse uses (CLAUDE.md "Init File Ownership"): skill files refresh on re-install, the policy template is created once and preserved (product-lens epic-F3). Today that subcommand installs one helper command with no ownership semantics.
2. **Policy template**: `STUDY_POLICY.md.template` (user-owned) holding §1–5, §9, §11 with placeholders where worked examples were; fusion-tea's copy keeps everything. Same authority rule as Item 2's decisions doc (product-lens smell 1): the template is a dated snapshot of the general sections; fusion-tea's ratified policy is not authority for other targets, and because the template is user-owned a target's filled copy diverges by design.
3. **Tools**: `scripts/study/*` and schemas as a sysml-codegen package with console entry points; `integrate.py` likewise, with the provenance-test read and backup prefix parameterized.
4. **Tests and fixture**: move the package-agnostic test subset; add a neutral fixture package; keep `test_generic`'s invariant.
5. **fusion-tea side**: replace local copies with thin wrappers or remove them; keep `exploration/<pkg>/studies/ANNEX.md` and fusion-specific tests; ledger rows for every fusion-specific line removed from the ported text.

**Out of Scope**:
- Changing study semantics, teax APIs, or any study record already committed in fusion-tea.
- Resolving fusion-tea's recorded policy §10 vs runbook steps 7/10 oracle conflict (stays a fusion-tea decision; the template carries no oracle obligation).
- The goal layer (Item 2).

**Success Criteria**:
- [ ] `sysml-codegen install-commands` installs `run-study` (skill, runbook, record template) and the policy template into a fresh target.
- [ ] The tools run from the installed package against the neutral fixture: indicators, preflight, verify and integrate each complete or fail closed as documented; the moved tests pass in sysml-codegen.
- [ ] fusion-tea's study suite passes with its copies replaced by wrappers or removed, and one existing study record re-verifies unchanged.
- [ ] The ported runbook and skill contain no fusion-tea path, package name or key prefix (the `test_generic` grep, extended to the instruction files).
- [ ] Ledger rows exist for every fusion-specific line removed from the ported text, with its fusion-tea destination (policy §6–8/§10, annex, or CLAUDE.md).
- [ ] sysml-codegen and agentic-mbse full suites pass.

**Required Reading**: research § 1b and Open Question 1; fusion-tea `.claude/skills/run-study/*`; fusion-tea `modeling_project/STUDY_POLICY.md`; fusion-tea `.project/concepts/run-study-skill.md` (owner factoring, lines 19–27, 142–143); fusion-tea `tests/study/test_generic.py` and `conftest.py`; `/home/reid/1cfe/sysml-codegen/src/sysml_codegen/cli/__init__.py` install-commands.

**Deliverables**:
- `.project/active/study-layer-to-codegen/{spec,design,plan}.md` (in this repo, tracking the external work)
- sysml-codegen: skill files, policy template, `study` package, entry points, fixture, tests
- fusion-tea: wrappers/removals, ledger citations by commit
- Appended section in `.project/active/wrap-split-migration-ledger.md`

---

### Item 4: Read-through sweep of agentic-mbse's shipped surfaces

**Type**: Implementation (docs and instruction text)
**Effort**: 1 day (spec 1h, design 1h, plan 0.5h, execute 5h)
**Dependencies**: Item 1 (edit the reconciled `skills/` layout once). May run in parallel with Item 2; coordinate on `MODELING_PROCESS.md.template`, which Item 2 owns.

**Objective**: Make every shipped surface read as a general rule or practice, with fusion examples kept only as labelled examples, and stop regressions with a guard test.

**Current State**:
- ✅ The leakage inventory in research § 3 lists about 96 hits by file and line; the owner's bar reclassifies most as acceptable examples.
- ⚠️ Authority pointers into other repos' internals: `claude/skills/sysml-conventions/SKILL.md:184-206`, `docs/patterns/constraints.md:66-71,460-479`, `docs/patterns/plant-idiom.md:8,70,115` (sysml-codegen `.project/concepts/` and `tests/fixtures/` paths); `docs/source-index.md:83-99` (a developer's `/home/reid/PyFECONS` checkout).
- ⚠️ Hard-coded machine paths: `tests/test_index.py:355,365`, `scripts/benchmark_corpus.py:18`, `scripts/README.md:148-231`, `claude/agents/python-debugger.md:75-112`.
- ⚠️ Consumer-only instructions: `claude/commands/analyze-models.md:65` ("magnet system test coverage"), `claude/skills/toolkit-awareness/references/python-environment.md:41` (lists `sysml-codegen, teax` as dependencies), `claude/skills/record-learning/SKILL.md:136`, `tests/test_sysml/test_adr002.py:281` (skipped test needing consumer models), `sysml/helpers.py:8` and `validation/level4_constraints.py:6` naming a specific runtime.
- ✅ Acceptable as examples under the owner's bar: plant-idiom pins, `FusionTea_*` naming, check-corpus PDFs, `'Toroidal Field Coil'`, fusion-flavoured test data, sysml-codegen named as a downstream in seam docs and code comments.

**Scope**:
1. **Authority pointers**: replace cross-repo `.project/` and `tests/fixtures/` citations with the rule stated in place plus "measured against a reference model" wording; keep `@pinned` excerpts in `plant-idiom.md` untouched (they are the drift contract's data).
2. **Machine paths**: `/home/reid` → relative or placeholder paths; the `test_index.py` cwd becomes the repo root fixture.
3. **Consumer-only instructions**: generalize or delete the lines above; remove the skipped CATF test.
3a. **README.md**: bring the repo README's "what `init` creates" list in line with `cmd_init` (it still names `modeling_pm/` and a root `SOURCE_INDEX.md`, `README.md:29-30,47,75`) and include the goal-layer directories Item 2 adds; README is in the read-through record (product-lens epic-F4).
4. **Example labelling**: where a fusion example stands as the only illustration of a rule (`package-naming.md`, `source-index.md`, `README.md.template:223`), add a one-line "example" marker or a second neutral example so the rule reads as general.
5. **Guard**: a pytest over shipped surfaces that fails on `/home/<user>` paths and on citations of `fusion-tea/`, `sysml-codegen/.project`, `sysml-codegen/tests/fixtures` as authority; vocabulary is not checked.
6. **Ledger**: every removed consumer-specific line gets a row with its fusion-tea destination (usually `CLAUDE.md` or `knowledge/SOURCE_INDEX.md`).

**Out of Scope**:
- Renaming fusion-flavoured test data (`p_fusion`, `MagnetCostCalc`, `IfeDriver`); replacing the check-corpus PDFs; editing `plant-idiom.md` pinned excerpts; `docs/sysmlv2`, `docs/syside`.
- Files Item 2 or Item 3 own (`MODELING_PROCESS.md.template`, the goal and study bundles).

**Success Criteria**:
- [ ] The guard test exists, passes, and fails when a `/home/reid` path or a cross-repo internal citation is reintroduced (demonstrated by one reverted edit in evidence).
- [ ] Each line listed under Current State has a disposition in the item record: generalized, deleted with ledger row, or kept as labelled example.
- [ ] A read-through record covers every shipped file (`claude/` or `skills/`, `docs/*.md`, `docs/patterns/`, `project_templates/`, `src/agentic_mbse/`) plus `README.md` with a one-word verdict per file against the owner's bar; README's init list matches `cmd_init` after Item 2.
- [ ] `uv run pytest tests/` passes on a machine other than the developer's (CI or a scratch user; the `test_index.py` fix is what this proves).
- [ ] Ledger rows exist for every deleted line; fusion-tea holds each destination before merge.

**Required Reading**: research § 3 (the A/B inventory) and the owner's bar in this epic's header; `tests/test_packaged_guidance_contract.py` (why plant-idiom pins stay); CLAUDE.md "Critical: Two Contexts".

**Deliverables**:
- `.project/active/shipped-surface-sweep/{spec,design,plan}.md`
- Read-through record and guard test
- Appended section in `.project/active/wrap-split-migration-ledger.md`

---

### Item 5: Port the research acquisition seam

**Type**: Code/Integration (Python package code, two skills, installer)
**Effort**: 2.5 days (spec 2h, design 3h, plan 1h, execute 14h). Over the two-day ceiling by the `/manage-sources` rework ([OWNER] 2026-10-09), kept in this item rather than a sixth because both touch the same index rules.
**Dependencies**: Item 1 (register the skill once, on the reconciled `skills/` layout). Item 2 only for scope step 6 (relabel the shipped `run-goal`'s research references); the rest of the item does not wait on it.

**Objective**: Ship the research acquisition seam from agentic-mbse: the `research-acquire` skill (a prompt file) as an installed skill, and its bookkeeping and registry code as `agentic-mbse research` subcommands, so a target can bring a source into `knowledge/` through one checked door without fusion-tea's scripts.

**Current State** (verified against fusion-tea source 2026-10-08):
- ✅ fusion-tea `.claude/commands/research-acquire.md` (125 lines, prompt only); `scripts/research_seam.py` (463 lines: `open`, `log`, `close`); `scripts/source_registry.py` (1,350 lines: `register`, `verify`, `retire`); `docs/research_seam_operator_guide.md` (287 lines); `tests/research/` (20 test files). Live in fusion-tea: 123 manifest rows, 61 run directories, 1 bounded negative.
- ✅ `run-goal` delegates research by spawning a fresh agent carrying the prompt (fusion-tea `.claude/skills/run-goal/SKILL.md:63`). Neither script calls an LLM; `register` shells out to `agentic-mbse extract --save-source` with zero budget (`source_registry.py:63-66`).
- ⚠️ `source_registry.py:44-52` imports `holdout_guard` (ARIES-CS protocol path and term list) and index/manifest helpers from `zotero_ingest.py` / `zotero_lib.py`; it also defines a `ZoteroSource` input kind (`:128-163`) that fusion-tea's batch ingest constructs, and matches duplicates on a `zotero_key` manifest field (`:416-417`).
- ⚠️ The prompt and guide cite fusion-tea's requirement number (`MR-4`) and hold-out protocol; both scripts' docstrings cite fusion-tea `.project/active/goal-research-seam/design.md`.
- ❌ agentic-mbse has no `research` subcommand; `cmd_init` creates `knowledge/research/{pending,approved,impacts}` only (`src/agentic_mbse/cli/__init__.py:864-876`).

**Scope**:
1. **Code**: `research_seam.py` → `src/agentic_mbse/research/seam.py`; `source_registry.py` → `src/agentic_mbse/research/registry.py`, with the index and manifest helpers it imports copied in. CLI `agentic-mbse research open | log | close | register | retire | verify`. Imports nothing from fusion-tea.
2. **Hooks**: the hold-out guard becomes a hook with a no-op default that a target supplies; the Zotero input kind becomes a neutral externally-fed source kind that fusion-tea's Zotero ingest constructs. Existing manifest rows (including `zotero_key`) keep matching.
3. **Skill**: `research-acquire` added to the skills list; its shell snippets call `agentic-mbse research …`; consumer citations generalized.
4. **Docs and tests**: operator guide → `docs/research-seam.md`, with fusion-tea ADR-0008 (source identity) condensed in under the same snapshot-authority stance as Item 2's decisions doc; `tests/research/*` minus Zotero and hold-out-term tests → `tests/test_research/`.
5. **Init**: `cmd_init` creates `knowledge/research/requests/{runs,negatives}`; targets do not track `knowledge/.staging/` or `knowledge/.registry.lock`.
6. **run-goal relabel**: the shipped `run-goal` (Item 2) cites the installed skill and CLI instead of Item 2's interim wording.
6a. **`/manage-sources`** ([OWNER] 2026-10-09: direct user management that follows and enforces the registry's rules): documents go through `register`, registered sources leave through `retire`, hand-curated entries stay legal for sources that cannot be captured; `verify` flags an index entry under `knowledge/sources/` with no manifest row.
7. **fusion-tea side**: delete the two scripts; Zotero ingest imports the registry from the package; the ARIES-CS guard is wired into the hook; re-init receives the skill; ledger rows for every consumer-specific line removed from the ported text.

**Out of Scope**:
- Zotero ingest and the ARIES-CS term list and protocol (stay in fusion-tea).
- `/research`, `pm save-research`, `pm approve-research` (reading and approval are unchanged).
- Changing the seam's behaviour: outcome classes, refusal ladder, request-key rule, receipt and manifest shapes port as they are.

**Success Criteria**:
- [ ] `agentic-mbse install-commands --list` names `research-acquire`; a fresh init contains it and the two request directories.
- [ ] The ported tests pass in agentic-mbse with no fusion-tea on the path; `agentic-mbse research verify` on a copy of fusion-tea's `knowledge/` reports the same findings as `scripts/source_registry.py verify` does today.
- [ ] A fresh target runs one request end to end through the installed skill and CLI (dry run recorded in evidence).
- [ ] `grep -iE "fusion-tea|MR-[0-9]|aries|zotero|\.project/"` over the shipped skill, guide and `src/agentic_mbse/research/` returns nothing outside labelled examples.
- [ ] Using only the shipped `manage-sources`, a user adds a capturable document (registered), adds a non-capturable source, removes a registered source (retired), and lists both kinds.
- [ ] fusion-tea's research and Zotero suites pass against the installed package with its two scripts deleted; ledger rows exist for every removed line.

**Required Reading**: research § 1c; the mental-model page above; fusion-tea `.claude/commands/research-acquire.md`, `scripts/{research_seam,source_registry,holdout_guard}.py`, `docs/research_seam_operator_guide.md`, `.project/adr/0008-source-identity-raw-bytes-sha256.md`.

**Deliverables**:
- `.project/active/research-seam-port/{spec,design,plan}.md`
- `src/agentic_mbse/research/`, CLI subcommands, `research-acquire` skill, `docs/research-seam.md`, `tests/test_research/`, installer changes
- Appended section in `.project/active/wrap-split-migration-ledger.md`

---

## Epic Strategy

**Value delivery path.** Item 1 unblocks everything by giving one installer source. Item 2 delivers the owner-stated ask (goal layer installable) and closes the MR-7 re-init hazard, which is the most likely silent loss today. Item 3 delivers the second owner-stated ask in the repo that owns its dependencies. Item 4 is the hygiene pass and the regression guard. Item 5 ports the research seam the goal layer delegates to, so an installed `run-goal` can acquire sources without fusion-tea's scripts.

**Critical path.** 1 → 2 → Item 5's run-goal relabel → fusion-tea re-install check (the epic's integration evidence). Item 3 runs in parallel from day one. Item 4 runs after Item 1, alongside Item 2. Item 5's code, skill and tests run after Item 1, alongside Item 2; only its relabel step waits for Item 2.

**Decomposition rationale.** Five items, one per repo-and-type boundary: installer packaging (1), agentic-mbse instruction text (2), sysml-codegen code plus its skill (3), agentic-mbse hygiene (4), agentic-mbse code plus its skill (5). Item 5 was the research's proposed fifth item; the owner ruled it in on 2026-10-06 (epic-F1). It stays separate from Item 2 because Item 2 is at the two-day ceiling and Item 5 is Python code with its own tests, not instruction text. Item 2 is at the two-day ceiling because the design-choice principle touches the same templates the goal port touches; splitting it would create two items editing one file.

**De-risking.** The only untested bet is Item 3's import repackaging of `scripts.study`; it is a half-hour check at the top of that item's spec. Item 1 carries the known risk that the sixteen bundle differences hide a consumer customization; the existing spec already requires a per-difference disposition.

**Integration evidence for the epic.** After Items 1–4: re-init fusion-tea from the agentic-mbse installer and `sysml-codegen install-commands`, remove its three local skills, run its study and orchestration suites, and confirm every ledger destination exists. That is the epic-level check; no separate epic audit if the item evidence covers it.

---

## Dependencies

**External**:
- sysml-codegen repo (`/home/reid/1cfe/sysml-codegen`): receives Item 3; its `install-commands` subcommand is the distribution channel.
- teax (`/home/reid/1cfe/teax`): runtime the study tools execute against; unchanged.
- fusion-tea (`/home/reid/1cfe/fusion-tea`): receives migrated instructions and re-installs at the end; pin moves per `.project/` memory (`uv.lock` hand-edit, `uv sync --frozen`).

**Internal**:
- `NATIVE-DISTRIBUTION-RECONCILIATION` spec (adopted as Item 1).
- `EXTRACT-PROVENANCE-HOOK` and `PM-APPROVE-RESEARCH-EMPTY-INSIGHTS` (closed) bear on Item 5: the registry works around both today. Not blocking.

**Item Dependency Graph**:
```
Item 1 (none)
  ├─> Item 2 (goal layer + principle) ──┬───────────────┐
  ├─> Item 4 (sweep)                    │ (relabel step)├─> fusion-tea re-install check
  └─> Item 5 (research seam) <──────────┘               │
Item 3 (study → sysml-codegen; none) ───────────────────┘
```

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| A branch "difference" in Item 1 is a fusion-tea customization, and taking `main` deletes it | Med | Per-difference disposition table is a spec criterion; ledger row for anything target-owned |
| Removing MR-7 hooks from tool-owned files loses enforcement before the general section lands | High | Item 2 lands the general section and the fusion-tea re-home in the same change; owner criterion checks `REQUIREMENTS.md` byte-identity |
| `scripts.study` repackaging breaks path-relative behaviour (`repo_root()`, schema lookup) | Med | First check in Item 3 spec; keep `manifest.repo_root()` semantics behind an explicit package-root argument |
| Items 2 and 4 both edit the process template | Low | Item 2 owns the file; Item 4 lists its process-template lines as out of scope |
| The ported registry stops matching fusion-tea's existing manifest rows (`zotero_key`, slugs, hashes) and re-registers or orphans sources | High | Item 5 criterion: `verify` on a copy of fusion-tea's `knowledge/` reports the same findings before and after; the input-kind rename keeps the stored field |
| Sweep over-generalizes and strips useful examples | Med | Owner's bar is written in the header; read-through record requires a per-file verdict, and "kept as labelled example" is a legal disposition |
| fusion-tea ends the epic with both local and installed copies of a skill | Med | Epic integration step removes the three local skills and the gitignore whitelist lines only after the installed ones pass |

---

## Timeline

**Total Effort**: ~9 days

| Item | Effort | Dependencies |
|------|--------|--------------|
| Item 1: Reconcile native source | 1.5 d | None |
| Item 2: Goal layer + principle | 2 d | Item 1 |
| Item 3: Study layer → sysml-codegen | 2 d | None (parallel) |
| Item 4: Shipped-surface sweep | 1 d | Item 1 |
| Item 5: Research seam port + `/manage-sources` | 2.5 d | Item 1; Item 2 for the relabel step |
| Epic integration: fusion-tea re-install | 0.5 d | Items 1–5 |

---

## Product-Lens

Latest verdict: **CLEAR**. epic-F1 resolved by the owner's 2026-10-06 ruling (Item 5 added 2026-10-08); epic-F2, epic-F3, epic-F4 disposed by item edits on 2026-10-06. Full ledger below; item specs carry unresolved findings into their per-item ledgers.

```
## epic — 2026-10-06 — rev .project/backlog/epic_wrap-split.md (untracked; main @ 8f43a09)
Point (re-derived): agentic-mbse ships general, domain-agnostic MBSE capability that a target gets from `agentic-mbse init` like everything else (tool-owned refreshed on re-init, user-owned preserved); fusion-specific content stays in fusion-tea; general capabilities stranded in fusion-tea (run-goal, narrate-goal, run-study, and "anything else that does not obey the split") are ported and generalized.   [source: .project/research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md § Research Question, grade: owner (verbatim); README.md:3 and docs/source-index.md:7 "domain-agnostic", CLAUDE.md "Two Contexts"/"Init File Ownership"/"Change Coordination", grade: INHERITED; fusion-tea harness concept :198 "goals are general", run-study concept "skill + runbook + policy + tools", grade: owner. No .project/adr/ and no .project/product/ exist in this repo.]
Falsifier: (A) a fresh `init` into a non-fusion target lacks run-goal/narrate-goal, or an installed surface carries an instruction that only works for fusion-tea (authority pointer into fusion-tea/sysml-codegen internals, machine path, MR-7 number); (B) an instruction fusion-tea relied on exists in neither agentic-mbse's shipped surfaces nor fusion-tea's own files after the epic, or fusion-tea re-init drops MR-7 enforcement.
Findings:
- epic-F1 [DO]    The research seam (fusion-tea `research-acquire.md`, `scripts/research_seam.py`, `scripts/source_registry.py` general core) is dropped from the epic "because the owner did not request it" (Epic Strategy), but the owner's verbatim instruction is open-ended: "Anything else you find that does not obey the general split". Research § 1c classifies it as general capability sitting in fusion-tea, and run-goal depends on it (research :51, :288-289). The epic resolves the conflict between that instruction and "keep the item count low" ([OWNER]) silently, in the agent's favour — research doc § Research Question (owner-verbatim) — disposition: BLOCK until the owner says port-now (Item 5 or fold into Item 2) or defer (one backlog line, filed as an owner decision, with Item 2's "point at the target's research procedure" wording recorded as the interim).
- epic-F2 [DO]    No item names `scripts/replicate_setup.sh`, which CLAUDE.md requires be reviewed alongside every `cmd_init()` change; Item 2 adds skills, templates and two directories to `cmd_init`, and Item 1 replaces the installer layout without saying whether the script is retired or updated — CLAUDE.md "Change Coordination" (INHERITED) — disposition: Item 1 states the script's fate; Item 2 inherits it.
- epic-F3 [DO]    Item 3 ships a user-owned `STUDY_POLICY.md.template` through `sysml-codegen install-commands`, but that subcommand today installs one helper command (`sysml-codegen/src/sysml_codegen/cli/__init__.py:1112`, "Install teax-completion helper command") with no user-owned/tool-owned semantics; the epic's criterion "fusion-tea re-installs from both installers with its protected files preserved" assumes the ownership rule without listing the work — CLAUDE.md "Init File Ownership" (INHERITED) — disposition: add "ownership semantics for installed files (preserve existing policy on re-install)" to Item 3 scope and effort.
- epic-F4 [DO]    README.md, the product's own statement of what `init` creates, is already wrong (`modeling_pm/`, root `SOURCE_INDEX.md` vs CLAUDE.md's `work/`, `modeling_project/`, `knowledge/SOURCE_INDEX.md`) and will be wrong again after Item 2 adds the goal layer; Item 4's read-through covers shipped surfaces only — README.md vs CLAUDE.md (INHERITED) — disposition: add README.md to Item 4's read-through record or Item 2's deliverables.
Smell fired: (1) two representations kept synchronized by hand — Item 2's shipped `docs/goal-layer-decisions.md` copies fusion-tea ADR-0001..0007, which stay live in fusion-tea; Item 3's policy template copies fusion-tea `STUDY_POLICY.md` §1–5/§9/§11. Must escalate into the Item 2 and Item 3 design judgments: name which copy is authoritative for installed targets (the epic's own intent, removing `.project/adr/` pointers, implies the shipped copy is a dated snapshot cited by path+commit and fusion-tea's ADRs are not authority for shipped text), and say what happens when fusion-tea amends an ADR.
No DON'T findings: Item 3's third home (sysml-codegen) and the vocabulary-tolerant bar in Items 2 and 4 both rest on the owner's 2026-10-06 decisions, which post-date and refine the verbatim ask; nothing in the four items narrows the point.
Gate: BLOCKED (epic-F1); DISPOSE epic-F2, epic-F3, epic-F4 before the first item spec.
```

```
## epic — 2026-10-06 — rev .project/backlog/epic_wrap-split.md (after item edits)
Resolves:
- epic-F2: FIXED — authority: INHERITED (CLAUDE.md Change Coordination) — basis: Item 1 scope 3 now states `replicate_setup.sh`'s fate and updates CLAUDE.md; Item 2 inherits.
- epic-F3: FIXED — authority: INHERITED (CLAUDE.md Init File Ownership) — basis: Item 3 scope 1 adds ownership semantics to `sysml-codegen install-commands`, inside the 2-day budget.
- epic-F4: FIXED — authority: INHERITED (README vs CLAUDE.md) — basis: Item 4 scope 3a and criterion add README.md to the read-through and tie its init list to `cmd_init`.
- epic-F1: OPEN — authority: owner — basis: Epic Strategy now states the two options; Item 2 spec carries it as a reserved gate until the owner rules.
- smell 1: ESCALATED — authority: AGENT — basis: Items 2 and 3 scope now carry the proposed snapshot-authority stance as a design question; design review decides.
Gate: BLOCKED (epic-F1)
```

```
## epic — 2026-10-08 — rev .project/backlog/epic_wrap-split.md (Item 5 added)
Resolves:
- epic-F1: FIXED — authority: owner ([OWNER-VERBATIM] 2026-10-06, "yes, we need this capability in agentic-mbse") — basis: option (a) ruled; the seam is Item 5; Item 2's reserved gate becomes interim wording that Item 5's relabel step replaces.
Gate: CLEAR
```

---

## Lessons Learned (Post-Completion)

*Fill in after epic is complete*

**What Went Well**:
- TBD

**What Could Improve**:
- TBD

**Surprises**:
- TBD

---

**Last Updated**: 2026-10-08
**Next Action**: `/_my_spec` on Item 5 (in progress 2026-10-08); `/_my_design` on Item 1 (spec exists) and `/_my_spec` on Item 3 in parallel.
