# Scope: retiring the subset profile

Read-only. No file in either repo was edited. agentic-mbse was read from `main` (`e268357f`) through a `git archive` copy in the scratchpad. The sysml-codegen detail is in `/tmp/claude-1000/-home-reid-src-agentic-mbse/757488b6-d865-4d53-baa0-842d9ebab104/scratchpad/codegen-part.md` and the consumer detail in `/tmp/claude-1000/-home-reid-src-agentic-mbse/757488b6-d865-4d53-baa0-842d9ebab104/scratchpad/consumers-part.md`. No tests were run.

## 0. Branch state

The brief's premise is wrong. `shipped-example-contract` is not "main plus 2 doc commits".

- The two branches split at `1a3d67c6` (Item 3 merge). `main` has moved 24 commits ahead since then, with PR #33 (Item 2a, `e268357f`).
- The branch adds only 2 doc commits (`6d779edc`, `359a63be`). Together they change 8 files: `.gitignore`, `.project/{CURRENT_WORK,EPIC_GUIDE,README,epic_template}.md`, `.project/active/README.md`, `.project/backlog/README.md` and `.project/execution/ENTRIES.md`. None of it is Item 5 work. There is no `.project/active/shipped-example-contract/`.
- Only `main` has `sysml/conformance_case.py` and `sysml/subset_cases/` (154 case folders, 308 files). sysml-codegen reads both.

## 1. agentic-mbse: the copy and everything that imports it

### 1a. Modules that belong to the copy (main, line counts)

| File | Lines | Notes |
|---|---|---|
| `src/agentic_mbse/sysml/subset_profile.py` | 1481 | The evaluator. Loads the TOML at `:702` through `importlib.resources`. Imports `PROFILE_SEMANTIC_VERSION, REASON_CODES, Eligibility, evaluate_identified_profile` from `executable_profile` (`:53-58`). |
| `src/agentic_mbse/sysml/subset_profile_rules.toml` | 671 | The rule records |
| `src/agentic_mbse/sysml/subset_facts.py` | 339 | |
| `src/agentic_mbse/sysml/subset_extraction.py` | 546 | Item 4 borrows `_IdentityError` (`:111`) and `_element_ref` (`:118-127`) from it |
| `src/agentic_mbse/sysml/occurrence_extraction.py` | 739 | Item 4 borrows `safe_location` (`:128-145`, which uses `_qualified_name` `:99-101`) from it |
| `src/agentic_mbse/sysml/occurrence_facts.py` | 433 | |
| `src/agentic_mbse/sysml/subset_coverage.py` | 107 | |
| `src/agentic_mbse/sysml/subset_advisories.py` | 153 | The two L6 advisories (opaque expression and sum wrapper). They are not refusals, but they walk `subset_extraction.expression_sites` (`:37`) and use `safe_location` (`:35`). |
| `src/agentic_mbse/sysml/conformance_case.py` + `subset_cases/` (154 dirs) | 312 + 308 files | Item 2a. Package data that sysml-codegen reads. |
| `src/agentic_mbse/validation/subset_presentation.py` | 578 | How L6 shows the result. It also handles the legacy categories (see 1c). |
| `src/agentic_mbse/sysml/fact_refs.py` | 59 | Shared. Item 4 uses it as well (`positional_binding.py:41`, `parameter_redefinition_facts.py:25`, `parameter_redefinition_extraction.py:38`), so **keep** it. |

These total about 5,360 lines without `fact_refs`. Adding `execution_target.py` (233) and `fact_refs` (59) gives about 5,650.

**Not part of the copy:** `executable_profile.py` (1108 lines). It is the older constraint-eligibility profile from `completed/20260713_executable-profile`. L4 uses it (`level4_constraints.py:13`) and so does L6's `check_constraint_executability` (`level6_architecture.py:24`, `:684-708`). The dependency runs one way: `subset_profile` imports from it, and it imports nothing from the copy. Also keep `invocation_allowlist.py`, which the ES-005 check in `reference_use.py:29` uses. Its docstring at `:8` mentions `SUBSET_PROFILE_VERSION` and needs editing.

Other non-copy code that names the copy:
- `src/agentic_mbse/sysml/types.py:111-125`: `L6_SUBSET_REFUSED/UNCONFIRMED/EXCLUDED/OMITTED/UNVERIFIED/UNASSESSED/ADVISORY/ADVISORY_UNVERIFIED` and `L6_SETTING_INVALID`.
- `src/agentic_mbse/sysml/__init__.py` exports nothing from the copy.
- `pyproject.toml` has no package-data entry for the TOML or the cases. Hatch's `packages = ["src/agentic_mbse"]` (`:49-50`) includes them because they sit under the package. Nothing needs removing there.

### 1b. Every import of the copy's modules

src:
- `validation/level6_architecture.py:35-37` (advisories, `extract_subset_facts`, `evaluate_subset_profile`) and `:68` (`present`, `string_subjects`). The call sites:
  - `_run_contract` `:1019-1030`
  - `_run_advisories` `:1033-1039`
  - in `validate_architecture` (`:1111-1270`): `:1199` the contract runs first; `:1210` `string_subjects(contract)` feeds `check_design_attr_completeness`; `:1216-1218` the advisories; `:1227` `present(...)`; `:1245` `shown.profile` goes into the JSON report.
  - `check_design_attr_completeness` takes a `string_subjects` parameter (doc at `:513-516`). With the copy gone, every legacy `L6_DESIGN_ATTR_UNEXTRACTABLE` error for String values comes back. Design D10 already does this when the contract did not run.
- `cli/__init__.py:26` imports `UNSET_NOTE` from `subset_presentation`. It is printed at `:734` by `init`.
- `sysml/parameter_redefinition_extraction.py:39` (`safe_location`) and `:53` (`_element_ref`, `_IdentityError`). This is Item 4; see 1d.

tests: dedicated to the copy (about 5,000 lines across the main test and helper files):
- `tests/test_subset_case_citations.py`, `test_subset_coverage.py`, `test_subset_gate_receipt.py`, `test_subset_matrix.py`, `test_subset_profile_scripts.py`, `test_subset_site_account.py`, `test_l6_run_consumers.py`
- `tests/test_sysml/test_subset_profile_{coupling,evaluate,hygiene,records,rules_instantiation,rules_modelwide,version,vocabulary}.py`, `test_subset_extraction.py`, `test_subset_extraction_no_reinterpretation.py`, `test_occurrence_extraction_{constraints,roots}.py`, `test_occurrence_facts.py`, `test_conformance_case.py`
- `tests/test_validation/test_l6_contract.py` (619) and `test_l6_advisories.py` (163)
- helpers: `tests/helpers/subset_{cases,matrix,records,site_account,synthetic}.py`
- fixtures: `tests/fixtures/subset_profile/` (`cases/` with 13 models, `codegen_gate.json`, `inventory/{matrix.toml,scanner.toml,site_account.csv}`) and `tests/fixtures/l6/{contract,advisories}/`

tests: mixed, edit rather than delete:
- `tests/test_shipped_text.py`: `:12` and `:14` import `SUBSET_PROFILE_VERSION` and `PACKAGED_RULES`; `:16` imports `BANNED` from `test_l6_contract`. `:206-227` assert README and model-validation state the profile version, "nine implemented rules", "coverage limit", "not a generation check", "future step ... does not exist yet" and **`"sysml-codegen check" not in lowered`** (`:219`). That last assertion directly blocks the new guidance and must be inverted or removed. `:230-238` (L6 title row, CLAUDE.md Level 6 line) and `:241-246` (research seam names `execution-target`).
- `tests/test_validation/test_session.py:21`, `:246-254`: one test of `extract_subset_facts`.
- `tests/test_validation/test_l6_check_errors.py:483`: one assertion on `L6_SUBSET_REFUSED`.
- `tests/test_sysml/test_parameter_redefinition_extraction.py:17`, `:372-373`: asserts the borrowed helpers exist (Item 4).
- `tests/learning/test_syside_input_redefinition.py:950`: imports `_element_ref`.
- `tests/test_sysml/test_executable_profile_computed_reasons.py:53`: reads `tests/fixtures/subset_profile/inventory/scanner.toml` to check executable_profile reason sites. This is not a copy test, so it needs that file kept or moved.
- `tests/test_sysml/test_conditional_operator_spelling.py:18-25`: a SysIDE learning test that uses `tests/fixtures/subset_profile/cases/conditional_operator.sysml`. Its docstring cites `subset_extraction._is_conditional`.
- Execution-target tests: `tests/test_validation/test_execution_target.py`, `test_l6_settings_cli.py`, `tests/test_init_execution_target.py` (+ `tests/fixtures/l6/init_golden/`), `tests/test_project_settings.py:35,51`, `tests/test_cli.py:45,71,90,690,740`, `tests/test_validation/test_json_report.py:58`, `tests/test_research/test_holdout.py:376,386`, and `tests/fixtures/l6/native_lowered.toml`. Whether these stay depends on the decision in 1c.

scripts (development only, not shipped):
- `scripts/subset_profile/`: `codegen_suite.py`, `gate_receipt.py`, `isolated_tree.py`, `render_matrix.py`, `run_trees.py`, `scan_sites.py`, `validate_diff.py`, `README.md`
- `scripts/l6_subset/run_consumers.py` (1074 lines). `record_reconstruct_texts.py` is the reconstruct-texts recorder used by `tests/helpers/reconstruct_texts.py`. I did not check whether that one touches the copy.
- **Catch:** `scripts/positional_binding/run_trees.py:53-55` (Item 4) puts `scripts/subset_profile` on `sys.path` and imports `isolated_tree`. Deleting the folder breaks Item 4's evidence script unless `isolated_tree.py` moves.
- **Catch:** the pre-merge gate (`scripts/subset_profile/README.md`, `tests/test_subset_gate_receipt.py`) hashes everything under `src/agentic_mbse/sysml/` plus `errors.py`. Any change there without a rerun fails that test. The retirement change has to delete the gate and its test in the same commit, or it fails its own check.

### 1c. L6 (Item 3) and the execution-target setting

What L6 calls: see 1b. The contract runs first, the legacy checks next, then the advisories. `present()` then sets every issue's severity through `execution_target.display()`.

What `[tool.agentic-mbse] execution-target` does:
- It is read by `validation/execution_target.py:85-125` (`resolve_target`). The key is defined at `project_settings.py:27-28`, and `init` writes it through `add_execution_target` (`project_settings.py:250`).
- Its CLI surface: `validate --execution-target` (`cli/__init__.py:368-384`, `:897-900`) and `init --execution-target` with an interactive prompt (`:718-800`, `:945-948`).
- It changes display severity only. One table does it, `execution_target.py:165-181`.

Is it independent of the profile? **Partly.**
- 9 of its 15 categories are profile or advisory outcomes: refused, unconfirmed, excluded, omitted, admitted, unverified, unassessed, advisory, advisory_unverified.
- One part is independent: `LEGACY_GENERATOR_ONLY` (`:204-222`). Under `native` it folds 4 legacy L6 codes into the INFO summary: `L6_MISSING_QUALIFIED_NAME`, `L6_ANONYMOUS_RETURN`, `L6_BODY_ASSIGNMENT_IMPL_LOSS` and `L6_CALC_DEF_NO_INSTANTIATION`. The evidence for that is `tests/fixtures/l6/native_lowered.toml`, plus the Item 3 audit. CURRENT_WORK says two of the four rest on reasoning rather than a native run.
- `L6_SETTING_INVALID` (a broken table stops L6, `level6_architecture.py:969-1000`) is also independent.

So once the profile is gone, the setting only controls whether 4 legacy codes are folded under `native`. The fold is currently applied by `subset_presentation.present()` (`:258`, `:267`), which would need a much smaller replacement. The setting could also mark that a project targets generated code, which is exactly when the skills should run `sysml-codegen check`. That is a decision for the owner, flagged in the summary.

### 1d. Item 4 (L2_POSITIONAL_BINDING): what it borrows from the copy

- `sysml/parameter_redefinition_extraction.py:39` imports `safe_location` from `occurrence_extraction` (`:128-145`, plus its helper `_qualified_name` `:99-101`). It is used at `:143`, `:260`, `:300`, `:364` and `:372`.
- `:53` imports `_element_ref` and `_IdentityError` from `subset_extraction` (`:111-127`). They are used at `:137-138`.
- `fact_refs.ElementRef` and `SafeLocation` are used across Item 4.

That is about 35 lines in all. They can move into `fact_refs.py` or a small `sysml/element_refs.py`. Then update `test_parameter_redefinition_extraction.py:372-373` and `learning/test_syside_input_redefinition.py:950`. The Item 4 modules `validation/positional_{binding,check,pins}.py` import nothing else from the copy. (sysml-codegen's `03-challenge.md:52` makes the same point.)

### 1e. Docs, ADRs, product promises, epic, changelog

Shipped or top-level docs:
- `README.md:19-30`: L6, the profile, `subset-profile/v2`, nine rules, "a future step ... does not exist yet", and the `execution-target` block
- `CLAUDE.md:124` (Level 6 line)
- `skills/model-validation/SKILL.md:28` and `:30`
- `docs/research-seam.md:350` and `:415` (`execution-target` as a key)

.project:
- `adr/0001-subset-profile-capability-ownership.md` (42 lines, `status: active`). Its decision at `:15-17` is that agentic-mbse owns the contract, the TOML, `subset_profile.py` and `occurrence_extraction.py`. Retiring the copy needs it superseded.
- `adr/0003-execution-target-setting.md` (40 lines). Amend it or supersede it, depending on 1c.
- `adr/INDEX.md:5` and `:7`.
- `product/0001-executable-subset-contract.md` (promise `:15-17`), `product/0003-l6-generator-subset.md` (promise `:15-17`), and `product/INDEX.md:5,7`. `product/0002-positional-binding-check.md` is unaffected.
- `backlog/epic_executable-subset-contract.md` (329 lines): Item 1 `:110-149`, Item 2/2a/2b `:151-191`, Item 3 `:193-214`, Item 5 `:236-258`, Item 6 `:260-276`, strategy `:278-284`, owner decisions `:307-321`.
- `backlog/BACKLOG.md:21-22` (epic and GENERATOR-SUBSET-PATTERNS rows), `:244-260` (`SUBSET-PROFILE-TYPING-AND-LITERAL-CANDIDATES`, which is moot once the copy is gone), and `:29-30` (Item 3 spike follow-ups, which stay).
- `backlog/item_generator-subset-patterns.md` (68 lines; § 2 `:30` is the problem this replacement now solves).
- `completed/CHANGELOG.md:7-32` (Item 3) and `:61-85` (Item 1). There is **no Item 2a entry** on main.
- `CURRENT_WORK.md:20-22`.
- Archives, history only: `completed/20261018_exec-subset-profile/`, `completed/20261020_l6-subset-profile/` and `concepts/convince-me-exec-subset/`.

What gets installed into target repos that mentions the profile:
- `skills/model-validation/SKILL.md:28,30` (installed under `.agents/skills/`)
- `init --execution-target` writing `pyproject.toml`
- the `UNSET_NOTE` text printed by `init`

No installed pattern doc, template, agent or adapter mentions the profile.

## 2. Shipped guidance and the three refused patterns

Where the guidance lives:
- `project_templates/MODELING_GUIDE.md.template` and `MODELING_PROCESS.md.template`, tool-owned and installed to `modeling_project/`
- `skills/sysml-conventions/SKILL.md` and `references/stencils.md`
- `docs/patterns/*.md`. These ship through the wheel's `force-include "docs"` and land in target repos under `.agentic-mbse/patterns/`, as seen in dc3.
- `agents/sysml-expert.md`

No skill folder holds `.sysml` example files.

**Assertion inside a calculation.** Found with a brace-tracking scan over the sysml fences. All four hits are `assert constraint` inside a `calc def`. None is inside a calc usage owned by a part:
- `docs/patterns/constraints.md:157-169`: section "### In Calc Definitions", `calc def PowerCalculation` with `assert constraint ReasonablePower` at `:164`. It sits beside "In Part Definitions" (`:142-153`), which is the correct form.
- `docs/patterns/syntax-reference.md:58-77`: the `calc def MyCalculation` template with `assert constraint Reasonable` at `:65`. "Key Points" at `:76` says "`assert constraint` for validation rules".
- `docs/patterns/semantic-operators.md:466-474`: `calc def ExtendedCalculation` with `assert constraint ReasonableOutput` at `:471`.
- `docs/patterns/semantic-operators.md:497-517`: "Correct: assert prefix", `calc def CorrectConstraint` at `:509-517` (assert at `:511`), shown against the "WrongConstraint" calc def at `:497-503`. This teaches the calc-owned assert as the *correct* form.
- `skills/model-validation/SKILL.md:30` names "calculation-owned constraints" only as an L6 rule.

**Open part multiplicity (`[*]`, `[0..*]`).** No shipped example uses one. The only text hit is `docs/patterns/semantic-hazards.md:153`, a hazard candidate, not an example. Exact counts appear at `docs/patterns/plant-idiom.md:396` (`Cell[3]`) and `definitions-usages.md:77` (`[12]`). Symbolic counts appear at `mbse-concepts.md:128`, `adr002-calculations.md:160` and `semantic-operators.md:584` (`[N]`), and at `mbse-concepts.md:199-221`: "Parameterized Multiplicity Pattern" `[child_count]`, marked "Validated CORRECT", but only by `syside check`. **Not checked:** whether the generator treats a multiplicity given by an attribute (`[N]`, `[child_count]`) as exact. The new rule "part multiplicities are exact" has to say so either way.

**Sequence calc inputs (`Real[0..*]`).** No shipped example declares a `[0..*]` or other multiplicity on a calc `in` parameter. Nothing teaches it, so the new guidance adds the rule without having to correct any example.

### What Items 5 and 6 say (epic file on main)

- **Item 5** (`:236-258`, "Executable guidance contracts", depends on Items 1 and 4 and on Item 2 for generator evidence):
  - inventory every authored SysML fence in the shipped assets, and give each a stable identity and one evidence category (syntax fragment, complete definition, executable example, deliberate negative)
  - render `docs/patterns/generator-subset.md` **from the rule records** (scope 4, `:248`)
  - correct the misleading calc-owned assert, conditional, metadata and function guidance (scope 5, `:249`)
  - state what each remedy must preserve (scope 6)
  - add evaluator-author notes to `adr002-calculations.md` (scope 7)
  - record the 212-fence coverage baseline with a D3 target (scope 8)
  - Deliverables: `.project/active/shipped-example-contract/{spec,design,plan}.md`.
  - Scope 4 depends on the rule records that are being retired. Scopes 2 and 8 assume "applicable L2/profile checks".
- **Item 6** (`:260-276`, depends on Items 2, 3 and 5):
  - update the modeling skills and MODELING_PROCESS so generated-model changes "need applicable L6 and `sysml-codegen check` evidence before claiming readiness; missing codegen means ... unverified"
  - probe an unresolved capability early (scope 3: "Roles read the profile and hazard register")
  - ship an upstream-findings starter, record-learning changes, and a proposed CLAUDE.md coordination line
  - Item 6 scope 1 is close to the replacement, but it says "L6 and `sysml-codegen check`", and L6 will no longer contain the profile.

## 3. Workflow skills: where to add an early `sysml-codegen check`

Today no shipped skill, agent, adapter or template mentions `sysml-codegen generate`, `sysml-codegen check` or `execution-target`. The one exception is `skills/model-validation/SKILL.md:30`, which says asking sysml-codegen "does not exist yet". `toolkit-awareness/SKILL.md:5` lists "codegen readiness" as a trigger phrase, and `references/python-environment.md:41` mentions sysml-codegen as a path dependency.

Candidates, best first:
- `project_templates/MODELING_PROCESS.md.template`: the "Process Selection" table `:15-27` and "Technical Patterns" table `:65-77`. Every workflow skill points here (`spec/design/plan/implement/quick-model` all say "Use Process Selection"). One row ("project targets generated code: run `sysml-codegen check` on the first model that builds, and again before a readiness claim") reaches every route. This is also where Item 6 scope 1 says the gate goes.
- `skills/design-model/SKILL.md:25-27` ("Resolve the Actual Uncertainty", which already says "prototype an uncertain language/execution capability"). This is the natural place for "probe early".
- `skills/plan-model/SKILL.md:23-35` ("Write an Executable Checklist"). Put the check as an early checkpoint row and a final row.
- `skills/implement-model/SKILL.md:23-29` ("Implement and Check"; `:29` already says "For unfamiliar syntax or execution behavior, use a small probe").
- `skills/model-validation/SKILL.md:19-45`: replace `:28-30` and add the command beside `validate` at `:36-45`.
- `skills/toolkit-awareness/SKILL.md:55-87` (Validation Framework and CLI Tools).
- `skills/orchestrate-modeling/SKILL.md:37-41` (Standard route) only needs the Process Selection pointer it already has.
- `skills/quick-model/SKILL.md:21` uses MODELING_PROCESS, so it is covered.
- The three limits themselves belong in `MODELING_GUIDE.md.template` (with `skills/sysml-conventions/SKILL.md`, which mirrors its sections), in `docs/patterns/constraints.md`, and in `docs/patterns/adr002-calculations.md`.

## 4. sysml-codegen

Full detail is in `codegen-part.md`. The key points:
- **The dependency on agentic-mbse:**
  - `pyproject.toml:24` requires `agentic-mbse>=0.1.3,<0.2`, and `:121-122` points it at the editable path `../agentic-mbse`. `uv.lock:6-8` records 0.1.3 from that path.
  - `_upstream_pins.py:65-69` pins `SUBSET_PROFILE_VERSION = "subset-profile/v2"`.
  - Main and the branch are the same here.
  - sysml-codegen also uses agentic-mbse for syside loading, `SemanticEvidenceCode`, the installer and `executable_profile.PROFILE_SEMANTIC_VERSION` (`:62`). The dependency stays.
- **The 2b screen step (branch only):**
  - `src/sysml_codegen/subset_screen.py` (181, `assess_screen` `:84-110`) and `src/sysml_codegen/cli/report.py` (218).
  - In `cli/__init__.py`: `run_check` `:126-142` (screen at `:142`), `cmd_check` `:122`, `run_codegen` `:504` → `_report_after_the_seal` `:508-523`, and comments `:26-32` and `:356`.
  - The help string at `:358` does not mention the screen.
  - Docs: `CLAUDE.md:77` and `docs/architecture/reference/02-orchestration.md:83,87`.
  - Screen-only tests: `test_subset_screen.py`, `test_report.py`, `test_assess_screen.py`, `test_shared_load_screen.py`, `test_check_screen_faults.py`, `test_screen_import_failure.py` and `helpers/blocked_screen_import.py`.
  - Mixed tests: `test_check_command.py`, `test_check_snapshots.py`, `test_cli_module_boundary.py`, `test_report_form.py` and `test_check_matches_stored_answers.py`.
  - The generator-only 2b work stays: `cli/prepare.py`, `cli/emit.py`, `cli/destination.py`, `test_refusal_before_first_write.py` and `test_emit_*`.
- **The Item 2a agreement-test system:**
  - 246 stored answers in `tests/expectations/subset_profile/cases/` (169 refused, 77 generated).
  - `disagreements.json` holds 136 entries. 0 of them are the screen refusing a model the generator builds.
  - `site_account.csv` has 502 lines on main. `SiteReason` is at `elaboration/diagnostics.py:40` and `Refusal` at `cli/refusal.py`. `refusal_records.json` (3224 lines) is on the branch only.
  - Copy-only, delete: `subset_profile_adapter.py`, the screen half of each case, `disagreements.json`, and the agreement, reason-mapping, screen-mutation, tripwire, record-coverage and occurrence-parity tests.
  - Keep as generator regression tests: the generator half of each case, `SiteReason`, `Refusal`, the site account and its scan tests, the generator mutations, the fixture classes and the refusal records.
- **Blocker:** 154 of the 246 case models live in agentic-mbse `src/agentic_mbse/sysml/subset_cases/` and are read through `conformance_case.packaged_case_dir` (sysml-codegen `tests/helpers/subset_profile/cases.py:415-418`). They have to be copied into sysml-codegen `tests/fixtures/` before agentic-mbse deletes them, or the kept generator tests lose their models.

## 5. Consumers

Neither consumer uses the profile or the setting.
- **fusion-tea** (`/home/reid/src/fusion-tea`, main `f96ad312c`): pins agentic-mbse at git rev `443388823` (`pyproject.toml:36`), which predates every subset module. It has no `[tool.agentic-mbse]` table. There is no `/home/reid/1cfe/fusion-tea`.
- **dc3** (`/home/reid/src/dc3`, branch `goal/study-ready-baseline`, `60b44d5`):
  - It uses editable path dependencies on `../agentic-mbse` and `../sysml-codegen` (`pyproject.toml:25-26`). It therefore runs whatever those two checkouts have checked out.
  - It has no `execution-target` setting and does not import the copy.
  - It already records the three limits in its own words: `work/learnings/RAW_LEARNINGS.md:162`, `work/orchestration/goals/study-ready-baseline/learnings.md:47` (L-005) and `trail.md:334`. That wording could seed the new guidance.

## 6. sysml-codegen ADR 0018

- ADR 0018 (`.project/adr/0018-occurrence-summary-shared-with-agentic.md`, "Occurrence summary has a second reviewed owner in agentic-mbse, held by a parity test") is **on neither sysml-codegen main nor `subset-profile-screen`**.
- It exists only on the unmerged branch `adr-0012-occurrence-summary-amendment` (`8396cb23`, checked out in `/home/reid/src/sysml-codegen`, sysml-codegen PR #21). That branch was cut before Item 2a merged.
- Its decision (`:17`) amends ADR 0012 so that agentic-mbse's `occurrence_extraction.py` makes the same occurrence reads, held to the generator by `test_occurrence_parity.py`. Retiring the copy removes both, so PR #21 should be closed unmerged. ADR 0012 on main has `amended_by: []`.
- No ADR 0001-0017 on sysml-codegen main mentions the subset profile.
- The recommendation to retire the copy is in sysml-codegen `.project/active/subset-profile-screen/architecture-review/` (`02-alternatives.md:196` option G; `03-challenge.md:52,59,64`; `index.html`).

## Not found or not checked

- No Item 2a entry in the agentic-mbse CHANGELOG on main.
- Whether the generator treats an attribute-valued multiplicity (`[N]`, `[child_count]`) as exact.
- Whether `scripts/l6_subset/record_reconstruct_texts.py` touches the copy.
- No test runs; line counts are from `wc -l` on main.
