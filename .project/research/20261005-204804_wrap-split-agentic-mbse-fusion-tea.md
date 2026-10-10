---
date: 2026-10-05T20:48:04-07:00
researcher: Claude
topic: "Wrap-up audit of the agentic-mbse / fusion-tea split: skills to port, MR-7 generalization, and other boundary violations"
tags: [research, packaging, skills, distribution, fusion-tea, native-skills, wrap-up]
status: complete
last_updated: 2026-10-05
---

# Research: Wrap-up audit of the agentic-mbse / fusion-tea split

**Date**: 2026-10-05 (PDT)
**Researcher**: Claude
**Research Type**: Codebase / Architecture / Integration (two repos plus sibling worktrees, read-only)

## Research Question

[OWNER-VERBATIM] "We created a couple of skills that are general capabilities related to agentic-mbse and sysml-codegen that currently sit with fusion-tea. E.g. run-goal, narrate-goal and run-study. All these need to be ported and generalized for agentic-mbse to be packaged correctly and installed like everything else." ... "'MR-7' -- we need to make sure everything in agentic-mbse is general and not fusion-specific." ... "Anything else you find that does not obey the general split: agentic-mbse for general capabilities, fusion-tea for fusion-specific stuff."

The rule under audit, stated once: **agentic-mbse ships general capability; fusion-tea keeps fusion-specific content.** Everything below is classified against that rule.

## Summary

- **The three named skills are consumer-owned today and are not standalone.** `run-goal`, `narrate-goal` and `run-study` live in fusion-tea's `.claude/skills/`, are whitelisted in its `.gitignore` as local files, and each pulls in a bundle: a runbook, templates, a policy file, scripts, tests, and ten ADRs. The goal layer bundle is general with a dozen fusion-tea paths to parameterize. The study layer bundle is general in method but its execution route depends on sysml-codegen generated packages and the teax runtime, which agentic-mbse does not depend on. Porting the skill text is easy; porting the scripts needs a home decision (see Open Questions).
- **MR-7 is a fusion-tea modeling requirement whose enforcement text has been written into a tool-owned file.** MR-7 ("Preserve design choices; separate evaluation from design selection") is `modeling_project/REQUIREMENTS.md` in fusion-tea. Its enforcement hooks were added to fusion-tea's copies of `MODELING_PROCESS.md` (tool-owned, two inserted paragraphs), `GOAL_RUNBOOK.md`, `goal-templates/goal.md`, and `run-goal/SKILL.md`. agentic-mbse itself contains no "MR-7" string. The principle behind MR-7 is general systems engineering and belongs in the shipped process template, phrased without the fusion-tea requirement number or rubric path. The current state means a re-init of fusion-tea would silently drop the owner's MR-7 enforcement.
- **agentic-mbse's shipped surfaces carry about 96 fusion- or consumer-specific items.** Concentrated in `docs/patterns/plant-idiom.md` (16), `docs/patterns/package-naming.md` (8), `docs/source-index.md` (8), `claude/skills/sysml-conventions/SKILL.md` (6), `claude/commands/formalize-intent.md` (5), two fusion PDFs shipped in the wheel as the `extract --check` corpus, one fusion example in `README.md.template` copied into every new target repo, and about 25 test files or fixtures. `docs/` is force-included in the wheel, so the pattern docs ship.
- **The distribution channel has a direction problem that blocks any port.** Fusion-tea's installed workflow bodies match `main` exactly (only a one-line "supporting skills" preface differs), but the native Claude/Codex installer source on branch `native-claude-codex-skills` (worktree `agentic-mbse-native-skills`, at `955295b` plus uncommitted remediation) forked from `main` before 57 commits and is behind on eleven workflow bodies and the whole `MODELING_PROCESS.md` template rewrite. There are two installer shapes (legacy `claude/` symlink install on `main`; native `skills/` + `adapters/` install on the branch) and the ported skills must land in whichever one ships.
- **Feasibility: the wrap is achievable as four bounded items plus one owner decision.** Port the goal layer (skills, runbook, templates, ADRs, one test) as tool-owned templates and skills; generalize the design-choice principle into the process template; sweep the ~96 leakage hits with one cross-repo coordination point (plant-idiom pins); reconcile the native branch with `main` before any of it is distributed. The owner decides where the study execution scripts live.

## Detailed Findings

### 1. The three skills and what travels with them

**Where they are, and how they are owned.** fusion-tea `.gitignore:22-27` ignores `.claude/skills/*` (the installer-managed symlinks) and whitelists five local skills: `browser-inspect`, `concept-research-navigation`, `narrate-goal`, `run-study`, `run-goal`. `.agents/skills/{run-goal,run-study,narrate-goal}` are relative symlinks back to `.claude/skills/` (fusion-tea `AGENTS.md:3` says so). They are not in `MBSE_SKILLS` (`src/agentic_mbse/cli/__init__.py:46-57`) and not in the native worktree's `skills/` inventory, so no installer knows them.

**Owner authority for porting.** The goal concept records `[OWNER] Goals are general to the systems-engineering and concept-development process; the operator need not be the builder` (fusion-tea `.project/concepts/goal-driven-model-development-harness.md:198`). The run-study concept records `[OWNER]` "the capability factors as lightweight skill + runbook + policy rulebook + tools" (`.project/concepts/run-study-skill.md:142`) and `[AGENT] (ratified by owner, 2026-08-17)` that it was "built fusion-tea-side against delivered machinery" because package fixes were pending (`:117`). That ratified decision was about timing, not permanent home.

**Premise conflict to surface (Law 4).** The draft spec `.project/active/native-skill-distribution/spec.md` carries `[INFERRED] ... consumer-specific goal/study procedures remain owned by the target project.` The owner's request in this session says the opposite for `run-goal`, `narrate-goal` and `run-study`. The owner's statement is the higher grade; the inferred line should be amended when that spec is next touched, not silently left to contradict the port.

#### 1a. Goal layer: `run-goal` + `narrate-goal`

| Piece | fusion-tea path | Lines | Classification | Port shape |
|---|---|---|---|---|
| Skill entry | `.claude/skills/run-goal/SKILL.md` | 90 | General, with consumer paths | `MBSE_SKILLS` entry / `skills/run-goal/` |
| Procedure | `work/orchestration/GOAL_RUNBOOK.md` | 305 | General, with consumer paths | New tool-owned template to `work/orchestration/GOAL_RUNBOOK.md` |
| Templates | `work/orchestration/goal-templates/{goal,trail,learnings}.md` | 60/95/17 | General (one MR-7 line in `goal.md:29`) | Tool-owned templates |
| Narrative skill | `.claude/skills/narrate-goal/SKILL.md` | 95 | General | `MBSE_SKILLS` entry |
| Contract test | `tests/orchestration/test_goal_contract.py` | 47 | General | Ship like `test_models_example.py.template` |
| Decision records | `.project/adr/0001..0007` | — | General decisions, fusion evidence | Needs an ADR home in agentic-mbse (none exists) or carry as `docs/` rationale |

Consumer-specific lines in `run-goal/SKILL.md` to parameterize: `:49` (`.project/codex-test-setup.md`, `.codex-test/run`), `:53-55` (MR-7, `.codex-test/run`), `:61-63` (`knowledge/research/requests/`, `scripts/research_seam.py`, `scripts/source_registry.py`, `knowledge/holdout/aries-cs/PROTOCOL.md`, `docs/research_seam_operator_guide.md`), `:71-73` (`.project/adr/` 001-007).

Consumer-specific lines in `GOAL_RUNBOOK.md`: `:7, :31, :299-305` (`.project/adr/`), `:13` and ADR-0006 (assumes a two-PM split of `.project/` and `work/`), `:41` (cites a fusion-tea concept doc), `:84, :100, :139` (MR-7 and `REQUIREMENTS.md`), `:94` (a fusion-tea probe record), `:100` (`.project/active/demo-depth-rubric/application-policy.md`), `:106, :276` (run-study paths and `STUDY_POLICY.md`), `:260-270` (`exploration/<pkg>/studies/DISCOVERY_LOG.md`, `tests/study/test_records.py::test_findings_join_the_discovery_log`), `:288-289` (`source_registry.py`, `research_seam.py`, `integrate.py`, two operator guides).

`narrate-goal/SKILL.md` is the cleanest: only `:90, :96` (`work/narratives/`) and `:150` (the contract test path) are repo paths.

**What already exists upstream.** `claude/commands/orchestrate-modeling.md:21` already writes to `work/orchestration/<objective-slug>.md` and `:53` says "Preserve any interpretation checkpoints imposed by the target project's goal or study workflow." So `main` already assumes the directory and already treats the goal layer as external. `cmd_init` does not create `work/orchestration/` (`cli/__init__.py:872-876` creates `work/{backlog,active,completed,analysis,learnings}`).

#### 1b. Study layer: `run-study`

| Piece | fusion-tea path | Classification | Note |
|---|---|---|---|
| Skill entry | `.claude/skills/run-study/SKILL.md` (73 lines) | General method; fusion triggers | Triggers `:160-163` ("sweep R and a", "how sensitive is LCOE to") |
| Runbook | `.claude/skills/run-study/runbook.md` (15 steps + administer) | General by construction; names teax route | Steps `:133-159` name the `teax-study` CLI and `StudyRunner`/`PreparedListStrategy`; `:251` "the LCOE result" |
| Record contract | `.claude/skills/run-study/record-template.md` (17 sections, `snapshot.json` shape) | General | `:61-62` "LCOE objective channel/result" should read "objective" |
| Rulebook | `modeling_project/STUDY_POLICY.md` (162 lines) | Mixed | General: §1-5, §9, §11. Fusion: §6 teax construct list, §7 hypotheses, §8 tripwire log, §10 1costingFE/oracle, all worked examples |
| Tools | `scripts/study/{common,identity,manifest,indicators,preflight,verify,read_coverage}.py` + 7 JSON schemas | Package-agnostic, pinned by `tests/study/test_generic.py` | Coupled to generated-package layout (`pipelines/*.yaml`, `inputs/*.json`, `contracts/*`) and to teax |
| Integrate seam | `scripts/integrate.py` (1562 lines) | General for the sysml-codegen + teax pipeline | Shells out to `sysml-codegen generate`; `TEAX_SIMKIT_SUBPATH`; backup prefix `fusion-tea-integration-backup-` at `:1506` |
| Tests | `tests/study/*` (55 files) | Split | Portable as-is: `test_common`, `test_committed_store`, `test_integrate_*`, `test_integration_workspace`, `test_read_coverage`, `test_record_template`, `test_subset_flag`. Fixtures in `conftest.py:22-23` point at `exploration/stellarator_e2e/pkg/stellarator_tea` |
| Package annex | `exploration/<pkg>/studies/ANNEX.md` | Consumer by design | The runbook's "package fact, not rule" seam. This is the right place for fusion content and stays in fusion-tea |

**The annex pattern already does the separation.** `runbook.md:14-19` defines the annex as "everything package-specific" and says "Steps without that line are package-free by construction, and that is what makes this runbook reusable." The skill was designed to be portable; what remains is the execution route (teax) and the policy's fusion examples.

**Dependency direction, verified.** `sysml-codegen/pyproject.toml:24` depends on `agentic-mbse>=0.1.3,<0.2`. `agentic-mbse/pyproject.toml:22-36` depends on neither sysml-codegen nor teax. `teax` depends on neither. `scripts/study/*` and `integrate.py` import or shell out to both. Putting those scripts into agentic-mbse core creates a reverse dependency. Options are in Open Questions.

#### 1c. Research seam (not named by the owner, same shape)

fusion-tea also carries a general research/registry seam that `run-goal` depends on: `.claude/commands/research-acquire.md` (general protocol), `scripts/research_seam.py` (463 lines, general), `scripts/source_registry.py` (1350 lines; general core, with 1cfe Zotero group and ARIES hold-out guard imported at `:44-46`), `docs/research_seam_operator_guide.md`, ADR-0008, and `tests/research/*`. `source_registry.py` already works around upstream gaps filed as `EXTRACT-PROVENANCE-HOOK` and `PM-APPROVE-RESEARCH-EMPTY-INSIGHTS` in `.project/backlog/BACKLOG.md:88-108`. Its natural home is `src/agentic_mbse/` beside `extraction/`, with Zotero and hold-out as pluggable hooks. This is a candidate port, not an owner-stated one; it is listed so the goal layer's dependency is visible.

### 2. MR-7: the fusion requirement and the general principle

**What MR-7 is.** fusion-tea `modeling_project/REQUIREMENTS.md` § MR-7, authority `[OWNER-VERBATIM, 2026-09-20]` "As soon as you start introducing 'sizing', then you are basically pre-defining which design parameters are 'free' and which are 'derived'. this is explicitly what we wanted to avoid." The requirement: distinguish physical relationships from policies that choose a design; never let a binding silently remove a design choice; record which quantities an analysis specifies and which it solves for; report empirical validity separately from physical adequacy; evaluate the supplied design and report insufficiency rather than resizing. Its spec is fusion-tea `.project/active/modeling-intent-enforcement/spec.md`.

**Where its enforcement leaked into tool-owned files.** `diff` of fusion-tea `modeling_project/MODELING_PROCESS.md` against `project_templates/MODELING_PROCESS.md.template` shows three hunks: two inserted MR-7 paragraphs (fusion-tea `:17-18` "apply REQUIREMENTS.md MR-7 before selecting a process"; `:34-35` MR-7 obligations at spec/design/implement/review/acceptance plus `.project/active/demo-depth-rubric/application-policy.md`), and one install-mode hunk (`:70`, patterns at `.agentic-mbse/patterns/` instead of `docs/patterns/`). `MODELING_PROCESS.md` is in `TOOL_OWNED_TEMPLATES` (`cli/__init__.py:80-85`), so a re-init overwrites it and the owner's enforcement disappears. The same hooks appear in `GOAL_RUNBOOK.md:84,100,139`, `goal-templates/goal.md:29`, and `run-goal/SKILL.md:53`.

**What agentic-mbse already says.** The shipped template already carries the general seed: `MODELING_PROCESS.md.template` "Architecture & Design" bullet one, "Distinguish quantities with different meanings, such as installed capacity and operating demand." That is one sentence of what MR-7 states in a page. The process-selection table (`:21-28`) has no row for "changed design-variable role or automatic selection policy" even though fusion-tea's experience shows that is the trigger that matters.

**The general form.** The principle is domain-free: any parametric engineering model can hide a design decision inside a calculation. The generalization is a short section in the process template (name it "Preserve design choices", no requirement number) plus one row in the process-selection table making a changed variable role a design-review trigger, plus an invariants bullet in the shipped `goal.md` template that points to the target project's requirements file generically. fusion-tea keeps MR-7 itself and may keep a one-line pointer from its `REQUIREMENTS.md` entry, which is user-owned.

### 3. Fusion-specific content inside agentic-mbse's shipped surfaces

Shipped means: `claude/`, `docs/`, `project_templates/`, `SOURCE_INDEX.md.template` (force-included in the wheel, `pyproject.toml:53-57`), `src/agentic_mbse/`, and `tests/` (in the sdist). The sweep found about 96 must-generalize (A), 57 domain-flavored but acceptable (B), and 18 false positives. The A items, grouped by what to do:

**Replace the example domain (text edits, no behavior change).**
- `docs/patterns/plant-idiom.md` — 16 hits: `fusion_tea` fixture references `:55-59, :79, :81, :101, :207-208, :215, :324`; IFE/HIF driver, target factory and chamber examples `:103-104, :218-233, :246, :267-273, :280-293`; sysml-codegen test paths `:8, :70, :115`. **Coordination point:** `tests/test_packaged_guidance_contract.py:3,27-37` says this file is "the one authoritative copy of the calculation-binding" rule that "the codegen drift contract reads through," and it carries eight `<!-- @pinned fixture=... -->` excerpts compared against sysml-codegen fixtures including `tests/fixtures/fusion_tea/...`. Generalizing the pinned excerpts breaks that check unless sysml-codegen's fixtures move with it.
- `docs/patterns/package-naming.md:143-160, :260-280` — `FusionTea_*` as the canonical naming example (8 hits).
- `docs/patterns/conditionals.md:43-46, :108-120` — D-T/D-D/D-He3 fuel cycles, `alpha_fraction`, `PowerBalanceCalcDT`.
- `docs/patterns/doc-comments.md:78-79` — `major_radius` of the torus.
- `docs/patterns/constraints.md:66-71, :460-462, :479` — sysml-codegen `.project/concepts/...` authority path, `catf_mfe_gated` fixture.
- `docs/source-index.md:45-99` — a worked example titled "Fusion Reactor TEA (fusion-tea)" with `/home/reid/PyFECONS`, CATF MFE, ITER Physics Basis (8 hits).
- `claude/skills/sysml-conventions/SKILL.md:37-39, :141, :184-185, :192-193, :205-206` — `'Fusion Power Plant'`, `'HIF Driver'`, `reactor.wall_temperature_k`, sysml-codegen fixture and `.project` paths.
- `claude/commands/formalize-intent.md:40, :47, :52-54` — "compare reactor concepts", "LCOE differences between reactor types", "Compare fusion technologies side-by-side".
- `claude/commands/analyze-models.md:65` — "run /spec-model for magnet system test coverage".
- `claude/skills/record-learning/SKILL.md:136` — "Source: fusion-tea modeling session".
- `claude/skills/toolkit-awareness/SKILL.md:5` — trigger phrase "TEA pipeline"; `references/python-environment.md:41` lists `sysml-codegen, teax` as local path dependencies.
- `project_templates/README.md.template:223-224` — `part def 'Toroidal Field Coil'` / `part tf_coil`, copied into every new target repo.
- `claude/agents/python-debugger.md:75, :87, :112` — `/home/reid/my_project`.

**Replace shipped data.**
- `src/agentic_mbse/extraction/check_corpus/arxiv_probe.pdf` is "GyroSwin: 5D Surrogates for Gyrokinetic Plasma Turbulence Simulations" and `test_features.pdf` is Woodruff Scientific "Revisit of the 2017 Costing for Four ARPA-E ALPHA Concepts". Both ship in the wheel and drive `extract --check`. The check only needs a PDF with tables, equations and figures; any open-licence document works.

**Fix hard-coded paths (correctness, not just domain).**
- `tests/test_index.py:355, :365` — `cwd="/home/reid/1cfe/agentic-mbse"`; fails on any other machine.
- `scripts/benchmark_corpus.py:18` — `/home/reid/1cfe/literature`; `scripts/README.md:148-231` — `/home/reid/m-scout`, `/home/reid/fusion_modeling/...`.
- `tests/test_sysml/test_adr002.py:281` — a test skipped with "Requires fusion_modeling CATF models not in this repo"; dead code that names a consumer.

**Rename test data (cosmetic, lowest priority).** About 25 test files use `p_fusion`, `catf_physics`, `major_radius`, `MagnetCostCalc`, `HTS magnets`, `IfeDriver/HifDriver`, `tmp_path / "fusion-tea"`: `tests/test_sysml/test_{binding,expression,qualified_names,types}.py`, `tests/test_validation/test_{quality_check_result,v2_false_positive,item12_checks}.py`, `tests/test_pm_{operations,parser,dashboard}.py`, `tests/fixtures/adr002_violations/v2_derived_multi.sysml`, `tests/fixtures/item12/retype_instantiation/*`, `tests/corpus/papers.jsonl` ("source": "fusion-tea"). These do not reach users; they are listed for completeness and can be deferred or skipped.

**Code comments naming sysml-codegen as the downstream** (`sysml/data_models.py:3,64`, `sysml/aggregation.py:4`, `sysml/hierarchy.py:5`, `sysml/qualified_names.py:5`, `syside_adapter.py:40,611`, `validation/adr002.py:470,517`, `docs/constraint-facts-and-expression-ir.md:3,22,52`) describe a real seam and are acceptable (B). `sysml/helpers.py:8` (`sysml_to_teax.py`) and `validation/level4_constraints.py:6` ("handled by syside/TEAx") name a specific runtime and should say "the execution runtime."

### 4. Distribution state: two installer shapes, one behind

| Surface | `main` (`c37ff53`) | native branch (`955295b` + uncommitted) | fusion-tea installed |
|---|---|---|---|
| Workflow bodies (15) | current | 11 behind (60-110 changed lines each, e.g. `spec-model` 89, `plan-model` 110) | matches `main` (1-line preface differs) |
| `MODELING_PROCESS.md.template` | current (rewritten in Sept) | 865 lines behind | matches `main` plus two MR-7 paragraphs and one patterns-path hunk |
| Supporting skills | `sysml-conventions`, `pdf-analysis`, `python-debugger`, `record-learning` differ from native only by paragraph reflow | reflowed, otherwise same | matches native |
| Installer | `claude/` symlinks, `MBSE_*` lists in `cli/__init__.py` | `skills/` + `adapters/` + `agents/`, `skill_bundles()` discovery in `cli/installation.py:298-312` | installed from native wheel `d20069b`-era payloads, then 13 payloads hand-updated to `main` bodies (`.project/active/harness-right-size/installed.json`) |
| Codex adapter | none | `adapters/codex.md` | `.agentic-mbse/codex.md` adds a general author-continuity sentence at `:7` and a worktree-specific paragraph at `:11` |

Fork point: `88e2489` (merge of PR #13); 57 commits on `main` since. The `harness-right-size` and `harness-simplify` branches are merged into `main`. So the content fusion-tea runs is on `main`; what is missing is the native packaging of it. `.project/active/native-skill-distribution/spec.md` already tracks this as `NATIVE-DISTRIBUTION-RECONCILIATION`.

**Why this gates the port.** A ported skill must be registered in one inventory: `MBSE_SKILLS` on `main`, or a `skills/<name>/SKILL.md` directory on the native branch (discovered by `skill_bundles()`, checked by `tests/test_cli.py:271` against shipped files). Doing it twice is waste; doing it on the branch first strands it behind the 57-commit gap.

### 5. Smaller boundary items found along the way

- `.agentic-mbse/codex.md:7` in fusion-tea adds "Keep a continuing author across stages and clarifications while its context remains useful. Independent criticism requires a fresh non-author agent" — general; should flow into `adapters/codex.md` and `adapters/claude.md`, which still say "Fresh stages and independent audits require new agents" (the pre-September rule).
- `MODELING_GUIDE.md` in fusion-tea `:198` replaces the `get_docs_dir()` resolver with a pointer to `.agentic-mbse/patterns/`; the template `:198-202` only knows the legacy resolver. The native installer copies patterns to `.agentic-mbse/patterns/` (fusion-tea `install.json` lists 14), so the template should describe both install modes.
- `knowledge/holdout/aries-cs/PROTOCOL.md` plus `scripts/holdout_guard.py` is a general sealed-hold-out pattern with an ARIES-CS instance; the guard hard-codes terms at `:26-35`. Candidate for a `HOLDOUT_PROTOCOL.md.template` and a guard that reads its lists from the protocol. Not owner-requested; listed as a boundary observation.
- fusion-tea local items that are correctly fusion-specific and should stay: `manage-concept.md`, `memory-handler.md`, `concept-research-navigation`, `settings.json`, `work/orchestration/*.md` pre-goal briefs, `work/narratives/`, every `exploration/<pkg>/studies/ANNEX.md`. `browser-inspect` and `html-explainer` are general but not MBSE; they fit a user-level skill home better than agentic-mbse.

## Code References

- `src/agentic_mbse/cli/__init__.py:18-105` — `MBSE_COMMANDS`, `MBSE_AGENTS`, `MBSE_SKILLS`, `MBSE_HOOKS`, `USER_OWNED_TEMPLATES`, `TOOL_OWNED_TEMPLATES`, `DEV_MODE_GITIGNORE_PATHS`; the lists a port must extend on `main`.
- `src/agentic_mbse/cli/__init__.py:872-876` — directories `cmd_init` creates under `work/`; no `work/orchestration/`.
- `/home/reid/1cfe/agentic-mbse-native-skills/src/agentic_mbse/cli/installation.py:298-312` — `skill_bundles()` discovery; the native inventory a port must extend on the branch.
- `tests/test_cli.py:271` — inventory test tying `MBSE_COMMANDS` to shipped files.
- `tests/test_packaged_guidance_contract.py:3, 27-37` — `plant-idiom.md` as the one authoritative copy read by sysml-codegen's drift contract.
- `pyproject.toml:49-66` — wheel force-includes `claude/`, `docs/`, `project_templates/`; sdist includes `tests/`.
- `project_templates/MODELING_PROCESS.md.template:21-28` — process-selection table lacking a design-role-change row; "Architecture & Design" bullet one carries the one-sentence seed of the general principle.
- `claude/commands/orchestrate-modeling.md:21, :53` — already writes `work/orchestration/` and already defers to the target's goal/study workflow.
- fusion-tea `.gitignore:18-27` — whitelist of the five local skills and two local commands.
- fusion-tea `.claude/skills/run-study/runbook.md:14-19` — the annex seam that makes the runbook package-free.
- fusion-tea `modeling_project/REQUIREMENTS.md` § MR-7 — the owner's requirement and its `[OWNER-VERBATIM]` authority.
- fusion-tea `.project/concepts/goal-driven-model-development-harness.md:198` — `[OWNER]` goals are general to systems engineering.
- fusion-tea `.project/concepts/run-study-skill.md:117, :142` — ratified decision to build fusion-tea-side for timing; owner's factoring of the capability.
- `.project/active/native-skill-distribution/spec.md` — residual reconciliation spec; carries the `[INFERRED]` line that conflicts with this request.
- `.project/reports/2026-10-04-0901-status-report.md` § "What is actually broken or missing" item 4 — the sixteen-bundle drift finding.

## Architecture Insights

- **Three layers, three homes.** fusion-tea's own documents already factor the capability as: procedure (skill + runbook + templates, pure instruction), rules (a policy the target project ratifies), and tools (scripts bound to a runtime). Instruction belongs in agentic-mbse like every other skill. Rules belong in a user-owned template the target fills in, like `REQUIREMENTS.md.template`. Tools follow the dependency graph: anything importing teax or calling `sysml-codegen generate` cannot sit below sysml-codegen.
- **The annex and the invariants bullet are the existing extension points.** `run-study` separates package facts into `ANNEX.md`; `goal.md` separates project requirements into "Invariants / Modeling requirements". Generalizing means pointing those at "the target project's requirements file" and "the package annex" rather than at MR-7 and `stellarator_tea`.
- **Tool-owned means overwritten.** The MR-7 paragraphs in fusion-tea's `MODELING_PROCESS.md` are the clearest case of why consumer edits to tool-owned files must flow upstream in general form or be lost. The native installer's hash manifest (`install.json`) detects the modification but cannot merge it.
- **`main` is the content source of truth; the native branch is the packaging source of truth.** Reconciliation is a one-directional rebase of packaging onto content, not a merge of two content streams. The eleven workflow bodies and the process template on the branch should be replaced by `main`'s, keeping only the branch's envelope changes (frontmatter, the "Before executing this skill" preface, reflowed paragraphs).
- **Convention alignment.** CLAUDE.md "Init File Ownership" rules fit the port: `GOAL_RUNBOOK.md` and the three goal templates are tool-owned (procedure, updated on re-init); `STUDY_POLICY.md` is user-owned (ratified rules). `work/orchestration/goals/` and `work/narratives/` are user data and need `.gitignore` handling like the other `work/` subdirectories.

## Feasibility Assessment

**Can it be done?** Yes. Every piece is text or Python the owner already controls, and the skills were designed with package-free seams. The one structural obstacle is where `scripts/study/*` and `integrate.py` live, and that is an owner decision, not a technical blocker.

**Risks.**
- Editing `plant-idiom.md` without moving sysml-codegen's pinned fixtures breaks `test_packaged_guidance_contract.py` and sysml-codegen's drift contract. Do it as one coordinated change or leave the pinned excerpts and rename only prose.
- Porting onto the native branch before reconciling it with `main` ships old workflow bodies next to new skills.
- Over-generalizing `STUDY_POLICY.md` loses owner-ratified rulings. Keep §1-5, §9, §11 as the template body and leave fusion-tea's §6-8, §10 and all worked examples in fusion-tea's own copy.
- Dropping MR-7 from fusion-tea when the general section lands. fusion-tea keeps MR-7 in its user-owned `REQUIREMENTS.md`; only the duplicated enforcement text in tool-owned files is replaced by the general section.

**Prerequisites.** None technical. `NATIVE-DISTRIBUTION-RECONCILIATION` should land first or alongside, otherwise the port is done twice.

## Recommendations

Proposed as five items. Grades are `[AGENT]` unless marked; the owner's request supplies the `[OWNER]` scope for items 1 to 3.

1. **Port the goal layer (`run-goal`, `narrate-goal`)** — `[OWNER]` scope. Add `run-goal` and `narrate-goal` to the skill inventory; add `GOAL_RUNBOOK.md` and `goal-templates/{goal,trail,learnings}.md` as tool-owned templates targeting `work/orchestration/`; create `work/orchestration/goals/` and `work/narratives/` in `cmd_init`; ship `test_goal_contract.py` as a template beside `test_models_example.py.template`. Parameterize the lines listed in § 1a: ADR references become a `docs/goal-layer-decisions.md` (or an ADR directory, see Open Questions); MR-7 lines become "the target project's modeling requirements"; research-seam lines become "the target project's research procedure" until item 5 lands; `.codex-test` lines are deleted. ADR-0006's two-PM premise is stated as a condition ("where the target also runs a coding PM") rather than assumed.
2. **Port the study procedure (`run-study`)** — `[OWNER]` scope, with one `[AGENT]` split. Ship `SKILL.md`, `runbook.md`, `record-template.md` as a skill, with "LCOE" replaced by "objective" (`SKILL.md:160-163`, `record-template.md:61-62`, `runbook.md:251`) and the route step (`runbook.md:133-159`) rewritten to "the execution route the target's study policy names" with the annex supplying the route. Ship a user-owned `STUDY_POLICY.md.template` holding the general sections (§1-5, §9, §11) with placeholders where fusion-tea had worked examples. Where the tools go is Open Question 1; the skill text should not block on it, because the runbook already names tools through the annex and `scripts/study/` paths can be stated as "the installed study tools".
3. **Generalize MR-7 into the process template** — `[OWNER]` principle, `[AGENT]` placement. Add a short "Preserve design choices" section to `MODELING_PROCESS.md.template` and a row to its process-selection table: "Changed design-variable role, automatic sizing or selection policy, or demand-derived installed capacity | Focused independent design review of actual bindings and downstream consumers; insufficient/sufficient supplied-design tests where applicable." Add an invariants bullet to the shipped `goal.md` template pointing at the target's requirements file. fusion-tea then drops its two inserted paragraphs on the next re-init and keeps MR-7 itself. Record the amendment to the `[INFERRED]` line in `native-skill-distribution/spec.md` while there.
4. **Leakage sweep of shipped surfaces** — `[OWNER]` "everything in agentic-mbse is general". Work the A list in § 3 in this order: (a) `README.md.template:223-224` and the two check-corpus PDFs (reach every user); (b) `toolkit-awareness`, `record-learning`, `formalize-intent`, `analyze-models`, `sysml-conventions`, `python-debugger` text; (c) `docs/source-index.md` example; (d) `package-naming.md`, `conditionals.md`, `doc-comments.md`, `constraints.md`; (e) `plant-idiom.md` as a coordinated change with sysml-codegen's fixtures, or prose-only if coordination is deferred; (f) hard-coded `/home/reid` paths in `tests/test_index.py`, `scripts/`; (g) test-data renames last or never. One pytest guard, modelled on fusion-tea's `tests/study/test_generic.py`, that greps shipped surfaces for a short term list would keep it from recurring.
5. **Reconcile native packaging with `main` first** — already specified as `NATIVE-DISTRIBUTION-RECONCILIATION`. Replace the branch's eleven stale workflow bodies and process template with `main`'s content, keep its envelope and installer, carry the `codex.md:7` author-continuity sentence into both adapters, and describe both pattern-directory modes in `MODELING_GUIDE.md.template`. Items 1 and 2 then register their skills once, on the reconciled source.

Sequence: 5 → (1, 3 in parallel) → 2 → 4. Items 3 and 4(a) are small enough to go first if the owner wants visible progress before reconciliation.

**Alternatives considered.** Porting only the three `SKILL.md` files and leaving runbook, templates and policy in fusion-tea: rejected because the skills are entry points that cite those files by path and would not work in a fresh target. Porting everything including `scripts/study/` into agentic-mbse core: rejected because it inverts the dependency graph (§ 1b).

## Open Questions

1. **Where do the study tools live?** Three options. (a) sysml-codegen: it already depends on agentic-mbse, already generates the package the tools read, and already ships a `claude/commands/teax-completion.md`; the tools become `sysml-codegen study ...` or a `scripts/` directory it installs. (b) An optional extra in agentic-mbse (`agentic-mbse[study]`) that pulls teax and sysml-codegen; keeps one installer but makes agentic-mbse's extras depend on its own dependent. (c) teax itself, since `teax-study` CLI already exists there (`packages/teax-simkit/pyproject.toml:21`) and the tools are teax-package checks. Recommendation: (a), because the tools read generated-package contracts that sysml-codegen owns, and the `integrate.py` seam already calls `sysml-codegen generate`. The owner decides; the skill text ports either way.
2. **ADR home in agentic-mbse.** The runbook cites seven decision records by path and the goal contract test checks an ADR register. Options: ship a `docs/goal-layer/decisions.md` that condenses ADR-0001..0007 with their `[OWNER]`/`[AGENT]` grades and fusion-tea provenance, or add a `.project/adr/` register to agentic-mbse's own dev tracking and have the runbook cite the shipped docs. The former keeps the shipped artifact self-contained.
3. **Does the research seam port too?** Not owner-requested, but `run-goal` depends on it and it duplicates work already filed upstream (`EXTRACT-PROVENANCE-HOOK`). If not now, item 1 points at "the target's research procedure" and fusion-tea's copy keeps working.
4. **`plant-idiom.md` pinned excerpts.** Keep the `fusion_tea` fixture pins (they are evidence that the rule was measured against a real model) and generalize only the prose, or move the pins to a neutral fixture in sysml-codegen in the same change? The second is cleaner and needs a sysml-codegen PR.
5. **Test-data renames.** The ~25 fusion-flavored test files never reach a user. Skip, or do as a mechanical last pass?
