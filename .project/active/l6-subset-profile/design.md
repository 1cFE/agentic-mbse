# Design: L6 integration and execution-target settings (EXEC-SUBSET-CONTRACT Item 3)

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-10-18
**Branch:** `l6-subset-profile` at `08dca0d8` (base `main` at `ebb3d46710a4c1476bb12fa0e9decf0088ddb2c5`)

## Overview

L6 runs Item 1's contract on every model, decides how loud each result is from one project setting (`execution-target`), reports every failed inspection as a failure, and can write the full result as JSON. A small shared module owns the `[tool.agentic-mbse]` table for both L6 and the research holdout guard.

## Related Artifacts

- Spec: `.project/active/l6-subset-profile/spec.md` (revised after review). Review and resolutions: `spec-review.md`.
- Owner decisions, gate outcomes and the owner boundary (no Item 2, no sysml-codegen writes): `briefs/align.md`.
- Product-lens ledger: `product-lens.md`.
- Epic: `.project/backlog/epic_executable-subset-contract.md` § Item 3 and § Design principles. No Required Reading is listed for Item 3.
- Decisions: ADR 0001 (contract ownership; invariants 2 and 3 bind this design), ADR 0002 (project-root discovery for the pin list, reused here).
- Item 1 archive: `.project/completed/20261018_exec-subset-profile/` (`evidence/acceptance.md`, `evidence/dc3-baseline.json`, `evidence/matrix.md`, `evidence/r3-proposal.md`).
- Item 4 archive: `.project/completed/20261018_positional-binding-check/` (consumer-run scripts and evidence pattern).
- Spike for S1-S3, F4, F5: `spikes/findings.md` (contract runs on all three trees without raising; fusion-tea extraction takes about 226 s; advisory walkers raise on some valid shapes; most Appendix A generator-only causes do not hold at `b5663c07`, detail in `spikes/f4-codegen-citations.md`).

## The Point

[AGENT] (ratified by owner, 2026-10-18; `briefs/align.md`) `agentic-mbse validate` should tell a modeler up front whether the code generator will refuse their model, using Item 1's contract, instead of the modeler finding out one generator run at a time. dc3 found its blockers through five sequential generation runs; the contract reports 236 refused findings on that baseline in one pass.

Each project says in its committed `pyproject.toml` how it runs (`execution-target`), so native-only projects are not buried in generator findings. Unset shows generator findings as warnings; `native` folds them into one INFO line; `generated` makes confirmed refusals errors.

Two things must hold in everything a user reads. First, nothing claims the model "will generate": `clear` means only "no refusals found by the implemented rules", and L6 is not `sysml-codegen check` (ADR 0001 invariant 2). Second, a broken check never passes: under every target a crash or a failed inspection fails the run ([AGENT] delegated by owner, 2026-10-18, gate R3-2).

## Research Findings

**What exists and is reused**

- **The contract** (`sysml/subset_profile.py`). `extract_subset_facts(model)` (`subset_extraction.py:466`) then `evaluate_subset_profile(facts)` (`subset_profile.py:1285`) returns a `SubsetProfileResult` (`:743`): verdict, scope, findings, unverified checks, counts. Each `SubsetFinding` (`:636`) has rule, shape, context, outcome, reason, subject `ElementRef`, `SafeLocation`, evidence. Remedy and semantic limits live on the rule record (`RuleRecord.remedy`, `.semantic_limits`, `:334`). Findings and unverified checks are already sorted deterministically (`:1352-1353`).
- **Project root** (`project_root.py:19`). Item 4's pin list reads only at the root (`positional_pins.py:143`) and reports where it looked (`positional_check.py:178`). This design copies that shape for the setting.
- **The holdout guard's reader** (`research/holdout.py:219-284`). It reads `<root>/pyproject.toml`, rejects `[tool.agentic_mbse]` and any `[tool.agentic-mbse]` key except `research`, and turns every fault into a guard that refuses at first use.
- **A precedent for editing owner TOML without a TOML writer** (`cli/installation.py:344-381`). `register_codex_agents` appends text, re-parses with `tomllib`, and refuses to write if the result does not parse.
- **Option threading** (`runner.py:94-100`). L2's pin options reach `validate_structure` through `functools.partial`; L6 gets its override the same way.
- **Final-line qualifier precedent** (`common.py:166-176`, `runner.py:155-159`). A pass that rests on pinned warnings says so on its last line.

**Facts checked by reading that change the spec's picture**

- **"Shadowed by" needs no owner facts.** In dc3's JSON (`evidence/dc3-baseline.json`), each of the 6 unconfirmed `constraint-predicate` findings has the same `subject_id` as a refused `calc-owned-assertion/asserted_constraint` finding. The calc-owned-assertion rule names the constraint itself as its subject (`subset_profile.py:890-902`), not the calc usage. So the spec's condition ("the subject's owner is the subject of a refused finding") does not match the data. The working condition is: another rule refused the same declaration. See D9.
- **Calc-owned asserts do reach the constraint extractor.** The same 6 constraints appear under both rules, so the spec's "not checked" item is answered.
- **L6 already reports warnings through `issues`.** `add_issue` appends every structured issue, whatever its severity, to `issues` (`common.py:42-52`). L6 never uses `warnings`. Pass/fail is "no ERROR and no manifest issue" (`level6_architecture.py:1009-1011`).
- **The exception sites match the spec.** 17 `except Exception` in `level6_architecture.py`, 9 in `adr002.py`, plus `AttributeError` at `:230` and `:289`. `_get_calc_usage_names` (`adr002.py:260-270`) has no caller. `check_constraint_executability` has no swallow, so its failure today escapes L6 and is lost by the runner (`runner.py:128-137`).
- **Consumers have no `[tool.agentic-mbse]` table** in their working trees (`~/src/dc3/pyproject.toml`, `~/src/fusion-tea/pyproject.toml`; only `uv`, `ruff`, `mypy`, `pytest` tables). Not checked at the pinned revisions: see de-risk flag F5.
- **No `tomlkit`** in `pyproject.toml` or `uv.lock`.

**Not verified in this session** (tool access): sysml-codegen at `b5663c07` could not be read, so every codegen citation in L6 and every "generator-only cause" in the audit is still unconfirmed. git commands in dc3 and fusion-tea were not permitted, so the markers and `pyproject.toml` at `808464d`, `60b44d5` and `f96ad312` were not read. Item 4's evidence records fusion-tea `f96ad312` has all three root markers (`completed/20261018_positional-binding-check/evidence/phase1-fixture-truth.md` §5).

## Core Concept

L6 becomes three steps: **read the target, collect results, present them.**

1. **Read the target.** L6 finds the project root above the validated path, reads `[tool.agentic-mbse]` from its `pyproject.toml` through the shared settings module, and resolves one target: from the file, from `--execution-target`, or unset. A broken file or bad value is a configuration error, and L6 stops there.
2. **Collect results.** L6 runs the legacy checks, the contract, and two advisories. Each result is tagged with a *category*: a contract outcome, an unverified check, a legacy check's audited category, an advisory, or a check failure. A failure anywhere becomes a named `L6_CHECK_ERROR` for that check or element, and the other checks keep running.
3. **Present them.** One pure function maps (category, target) to how the result is shown: ERROR, WARNING, folded into the native INFO summary, or count only. L6 renders the verdict line, scope and coverage lines, issues and metrics from that, and attaches the full profile to the level result for the JSON report.

The key idea is that **the contract decides what is true, and the target decides only how loud it is.** L6 never asks "is this String?" or "is this refused?" itself; it reads the contract's findings and looks up the display in one table. That keeps L6 from re-deriving decisions (ADR 0001), makes the severity behavior testable as a single table, and keeps check failures out of the policy's reach: they are ERROR in every column.

Composes with: the contract (decisions), `find_project_root` (where to look), the holdout guard (shares the key set, keeps its own fail-closed behavior), the runner (crash handling, final line, report), and `cmd_init` (adds the key with the installer's append-and-verify pattern).

## Key Bets

- **B1. The contract runs cleanly and quickly on the consumer trees.** Item 1 ran it on dc3 and the codegen corpus, not on fusion-tea's real tree (7,654 positional inputs in Item 4's run). *If false →* a crash becomes `L6_CHECK_ERROR`, fusion-tea's L6 goes pass→fail under unset, and the stop-and-show fires late. De-risked by spike S1 before presentation work.
- **B2. Most legacy generator checks can be shown to have a generator-only cause.** The native INFO lowering of 11 rows rests on codegen evidence at `b5663c07` that this session could not read. *If false →* those rows keep today's severity under `native`, and native projects still see contradictory generator-only errors (epic scope 4). The design degrades safely: a row without evidence is not lowered.
- **B3. A text insert verified by `tomllib` is enough to add one key safely.** *If false →* `init` could corrupt a committed file. The verification compares the whole parsed document before and after, so the failure mode is a needless refusal, not a bad write.
- **B4. Nothing in today's passing consumer runs hides a crash or a swallowed failure.** *If false →* the R3-2 safeguard shows pass→fail, and implementation stops for the owner. This is the safeguard's job; the bet is only that it will usually come back clean.

## Key Decisions

- **D1. Shared settings module at `src/agentic_mbse/project_settings.py`.** It holds `TOOLKIT_KEYS = {"execution-target", "research"}` and one reader that returns the `[tool.agentic-mbse]` table or a named defect. It checks key membership only, never values. It lives at package top level for the same reason as `project_root.py`: `research`, `validation` and `cli` all import it. *Rejected:* defining the set in `holdout.py` (validation would import research); a reader in each package (the set would drift).
- **D2. Execution target and severity policy in one module, `validation/execution_target.py`.** It holds the target types, `resolve_target()` (filesystem) and the pure `display()` table. *Rejected:* a separate `severity_policy.py` (one more module for one table; both answer "what does the target mean").
- **D3. A setting error stops L6.** L6 reports `L6_SETTING_INVALID` and the target metric, runs no checks, and fails. Levels 1–5 run as usual. *Rejected:* running L6 "as if unset" with the error on top. That is the fallback the spec forbids, and its warnings would read as an unset run.
- **D4. Every escaped exception becomes a named result at the narrowest scope that is safe.** Per element where the loop can continue; per check where enumeration failed; per level in the runner. Check failures are always ERROR. *Rejected:* one broad try around all of L6 (one failure would hide every other result, against epic principle 5).
- **D5. Native summary is a metric line; unverified checks under `native` are one aggregated WARNING issue.** Summarized findings are kept on the level result as `summarized` (INFO), not in `issues`, so "Issues found: N" counts what needs attention. *Rejected:* one INFO `ValidationIssue` per finding (236 lines of noise in the first-five list); one WARNING per unverified check under native (50 lines for "could not decide").
- **D6. JSON report via `validate --json-report PATH`.** One file per run, levels in run order, written after the run, including crashed levels. Schema in Implementation Notes. *Rejected:* changing text truncation (spec non-goal); `--verbose` (prints to the terminal, still truncated).
- **D7. `init` adds the key by text insertion plus whole-document verification, no `tomlkit`.** Insert right after an existing `[tool.agentic-mbse]` header, or append a new table at the end. Then re-parse with `tomllib` and require the parsed result to equal the original plus exactly one key. Otherwise refuse and print the line. *Rejected:* `tomlkit` (a new dependency for a one-line insert; it would still need the symlink and layout refusals, and its round-trip is not byte-exact for every file).
- **D8. Contract issue codes per outcome**, not per reason: `L6_SUBSET_REFUSED`, `_UNCONFIRMED`, `_EXCLUDED`, `_OMITTED`, `_UNVERIFIED`, `_UNASSESSED`, `_ADVISORY`, each carrying the contract reason in `reason_code`. Plus `L6_CHECK_ERROR`, `L6_SETTING_INVALID`, and `LEVEL_CRASHED` for the runner. *Rejected:* one code per reason (16 more members; the same argument `types.py` records for `reason_code`).
- **D9. "Shadowed by" = another rule's `refused` finding has the same subject declaration (same `ElementRef.element_id`).** Computed in presentation from the findings alone; the outcome never changes. This corrects the spec's `[INFERRED]` condition against the dc3 data (Research Findings). *Rejected:* the spec's owner-based condition (it matches nothing in dc3); adding owner facts to the result (not needed).
- **D10. The String replacement consumes the contract.** `check_design_attr_completeness` skips the "unextractable" error for an attribute whose element id is the subject of a `string-value-omission` finding. If the contract did not run, the legacy error stays. *Rejected:* L6 testing "is the value a String literal" itself (re-deriving the contract's decision).
- **D11. Coverage list as a Python module `sysml/subset_coverage.py`** with `SUBSET_COVERAGE_VERSION = "subset-coverage/v1"` and a tuple of uncovered families. *Rejected:* a TOML resource (no schema needs loading; a constant is pinned by a digest test just as well); adding it to `subset_profile_rules.toml` (moves `SUBSET_PROFILE_VERSION`).
- **D12. Advisories in `sysml/subset_advisories.py`, detected with the existing walkers' own dispatch.** The opaque-expression advisory hooks the last-resort branch of `reconstruct_expression` (`expression.py:357`); the wrapper advisory reads `decompose_aggregation_expression(...).wrappers` (`aggregation.py:233`, `:383-398`) on sites that invoke `sum`. *Rejected:* a second classifier of expression kinds (would drift from the walker the matrix rows cite).
- **D13. Text order inside L6: setting error, check errors, then ERROR, then WARNING; contract findings ordered refused, unverified, unconfirmed, excluded, omitted, then the contract's own sort.** So the first five printed lines lead with failures and refusals (impl-F2). *Rejected:* today's check-call order (refusals could fall below the fold).

## Architecture

```
validate CLI ──(--execution-target, --json-report)──> runner.run_all_checks
   runner: for each level → result | LEVEL_CRASHED result ; final line ; AggregatedResult
   L6 validate_architecture(models_path, execution_target=override)
      1 resolve_target(models_path, override) ── project_root.find_project_root
                                               └─ project_settings.read_toolkit_table(root)
         └─ TargetSettingError → L6_SETTING_INVALID, stop
      2 load model ─> legacy checks (level6_architecture, adr002) ─> issues + check errors
                  ─> extract_subset_facts ─> evaluate_subset_profile ─> SubsetProfileResult
                  ─> subset_advisories.extract_advisories ─> advisories + failures
      3 subset_presentation.present(result, advisories, legacy issues, target)
            uses execution_target.display(category, target, base)
            uses subset_coverage + PACKAGED_RULES (remedy, limits)
         → issues, summarized, metrics, pass_note, report_detail
cmd_validate ── report.write_report(path, AggregatedResult) after the run
cmd_init ── project_settings.add_execution_target(root, value) | prompt | print the line
holdout.load_holdout_guard ── project_settings.read_toolkit_table (membership) + its own value check
```

**Data flow and boundaries.** Facts and decisions stay in `sysml/`. Severity, wording and the report stay in `validation/`. The settings module knows the table's shape and key set, not what any value means. The runner knows nothing about targets; it only carries the override to L6 and prints the qualifier L6 hands back.

### Data model

```python
class Target(StrEnum): UNSET = "unset"; GENERATED = "generated"; NATIVE = "native"
TargetSource = FromFile(path) | FromOverride(file_path | None, file_value | None) | Unset(looked_at | None)
@dataclass class TargetResolution: target: Target; source: TargetSource; root: Path | None
@dataclass class TargetSettingError: path: Path; fault: SettingsFault | Literal["invalid_value"]; detail: str
class SettingsFault(StrEnum): UNREADABLE; TOML_SYNTAX; NOT_A_TABLE; UNDERSCORE_TABLE; UNKNOWN_KEY
class Category(StrEnum): REFUSED; UNCONFIRMED; EXCLUDED; OMITTED; ADMITTED; UNVERIFIED; UNASSESSED
    ADVISORY; LEGACY_OWN_APPLICABILITY; LEGACY_KEPT; LEGACY_GENERATOR_ONLY; CHECK_FAILURE; SETTING_INVALID
class Display(StrEnum): ERROR; WARNING; NATIVE_SUMMARY; COUNT_ONLY
def display(category: Category, target: Target, base: Severity | None = None) -> Display
```

`LEGACY_CATEGORY: Mapping[ValidationCode, Category]` (in `execution_target.py`) maps each of the 17 L6 codes to one legacy category, from the audit (Appendix A). `base` is the severity the legacy check emitted.

### The severity table

`display()` is exactly this table; the table test enumerates every cell.

| Category | unset | generated | native |
|---|---|---|---|
| `REFUSED` | WARNING | **ERROR** | NATIVE_SUMMARY |
| `UNCONFIRMED` (never ERROR) | WARNING | WARNING | NATIVE_SUMMARY |
| `EXCLUDED` | WARNING | WARNING | NATIVE_SUMMARY |
| `OMITTED` | WARNING | WARNING | NATIVE_SUMMARY |
| `ADMITTED` | COUNT_ONLY | COUNT_ONLY | COUNT_ONLY |
| `UNVERIFIED` | WARNING | **ERROR** | WARNING (one aggregated line, outside the summary) |
| `UNASSESSED` (only when count > 0) | WARNING | WARNING | NATIVE_SUMMARY |
| `ADVISORY` | WARNING | WARNING | NATIVE_SUMMARY |
| `LEGACY_OWN_APPLICABILITY` | base | base | base |
| `LEGACY_KEPT` | base | base | base |
| `LEGACY_GENERATOR_ONLY` | base | base | NATIVE_SUMMARY |
| `CHECK_FAILURE` | **ERROR** | **ERROR** | **ERROR** |
| `SETTING_INVALID` | **ERROR** | **ERROR** | **ERROR** |

Under unset and `generated` no legacy row changes: the only legacy relaxation in this item is the String case, and it happens by suppression (D10), not through this table.

### What a user sees in L6

Metrics print in this order (wording is fixed by the tests, exact text by the plan):

1. `Execution target: <target> (<source>)`, e.g. `unset (no execution-target in /p/pyproject.toml)`, `generated (from /p/pyproject.toml)`, `native (override --execution-target; file says generated)`, `unset (no project root above models; pass --execution-target)`.
2. Unset only: `Execution target note: generator findings are shown as warnings because execution-target is not set. Add execution-target = "generated" or "native" under [tool.agentic-mbse] in pyproject.toml, or run agentic-mbse init --execution-target=generated|native.`
3. The verdict line: `Generator subset (subset-profile/v1, subset-coverage/v1): refused_incomplete: 236 refused, then incomplete: 50 unverified; 0 unassessed constraints; not a generation check`. For `clear`: `clear: no refusals found by the implemented rules; 0 refused; 0 unverified; N unassessed constraints; not a generation check`. If the contract failed: `not computed (see L6_CHECK_ERROR)`.
4. `Coverage limit: no rule yet for DEEP-QUALIFIED-WIRING, ES-002, ES-008, ES-009, ES-010-REFUSAL, CALC-DEF-BARE-RESULT, and <n> follow-up sites; a clear verdict says nothing about these.`
5. `Generator subset scope: executable profile <v>; roots used <k> of <g> (not narrowed); fact kinds not enumerated: none`.
6. Native only: `Generator-only findings (native: INFO summary): 236 refused, 6 unconfirmed, 32 omitted, 0 excluded, 0 unassessed constraints, 0 advisories, <m> legacy; all listed in --json-report`.
7. The existing counts, with `not computed` for any count whose check reported `L6_CHECK_ERROR`.

Each contract issue reads `<outcome> (subset-profile/v1): <rule>/<shape> in <context>: <reason>: <subject>`, with the record's remedy and semantic limits as the suggestion. An `unconfirmed` message adds `no generator probe has observed this`, plus `context <id> is unconfirmed by design` for the two contexts in `ALWAYS_UNCONFIRMED_CONTEXTS` (`subset_profile.py:221`), plus `shadowed by refused <rule>/<shape> on the same declaration` when D9 applies.

**Final line.** L6 sets `pass_note = "generated compatibility not established"` when the target is unset, or `generated` with a verdict other than `refused`. The runner prints `✅ Quality checks passed with <notes joined by "; ">` when the run passes and any note exists. The pinned note joins the same list.

### Runner and report

- **Crash.** `run_all_checks` catches a level's exception as today, but now appends a failed `QualityCheckResult` for that level with one ERROR issue `LEVEL_CRASHED` (`Level N crashed: <type>: <message>`), prints it, and stops under fail-fast. The traceback still prints with `--verbose`. The level number comes from the check's position in `QUALITY_CHECKS`.
- **Override.** `validate --execution-target {generated,native}` is parsed by argparse (a bad value is a usage error, exit 2) and passed to L6 through `functools.partial`, as L2's pin options are. With `--level` 1–5 it is accepted and unused.
- **Report.** `cmd_validate` checks that the report's parent directory exists before running (usage error, exit 2, otherwise). After the run it calls `report.write_report(path, aggregated, run_info)`. A write failure prints an error and exits 1. Schema in Implementation Notes.

### `init`

`cmd_init` gains `--execution-target {generated,native}`. After the installer saves, it runs one settings step and adds one summary block:

| State at `<target dir>/pyproject.toml` | Option given | Stdin a terminal, no option | Neither |
|---|---|---|---|
| No `execution-target` key, layout permits | write it | prompt: generated / native / leave unset (default); write the choice | write nothing; print unset note with the TOML line and the `init` form |
| No file | create a file holding only the table | same as above | same as above |
| Key present, valid, same value | report "already set" | report value, no prompt | report value |
| Key present, different or invalid value | never change; report both values and the allowed values; **exit 1** | never change; report | never change; report |
| Refused layout (below) | print line and reason; **exit 1** | print line and reason | print line and reason |

Refused layouts, each with a test: the file is a symlink; it is not UTF-8 or does not parse; `agentic-mbse` is an inline table; `agentic-mbse` is defined through dotted keys; the verification after insertion fails for any other reason (for example a header-like line inside a multi-line string). `--force` does not change any row. The rest of `init` always completes. `install-commands` never calls the settings step.

The settings step targets `<init target>/pyproject.toml`, not `find_project_root`: `init` defines the root it is initializing.

## Required Invariants

- **I1.** No path through L6 turns an exception or a failed inspection into "no issue", a zero count, or a model-defect finding. Every one becomes `L6_CHECK_ERROR` (ERROR, every target) naming the check, or `LEVEL_CRASHED`.
- **I2.** `display(CHECK_FAILURE, t)` and `display(SETTING_INVALID, t)` are ERROR for every `t`, and nothing in the `NATIVE_SUMMARY` set is a check failure (test).
- **I3.** L6 imports no outcome logic: the only inputs to severity are `SubsetFinding.outcome`, `UnverifiedCheck`, `counts.unassessed_constraints`, advisory records, `LEGACY_CATEGORY` and the target.
- **I4.** `SUBSET_PROFILE_VERSION`, its digest, the rule records and every existing result field are unchanged from `ebb3d467`. Library changes only add.
- **I5.** Under unset and `generated`, for every site, the combined severity of legacy plus contract issues is not lower than today's, except the String case (D10).
- **I6.** Each `[tool.agentic-mbse]` reader rejects any key outside `TOOLKIT_KEYS` and validates only its own key's value.
- **I7.** `init` never changes an existing `execution-target` value and never rewrites any byte outside the inserted text; the written file parses and its parsed value equals the original plus one key.
- **I8.** For the same tree, path and target, the text output and the JSON report are byte-identical across runs.
- **I9.** No user-visible line contains "generated-ready", "generation-ready", "ready to generate", "will generate", "generator accepts" or "readiness"; the verdict line never contains "clean", "ready" or "passed".

## Component Overview

- **`src/agentic_mbse/project_settings.py` (new).** The key set; `read_toolkit_table(root) -> ToolkitTable | SettingsDefect`; `add_execution_target(file, value) -> SettingWrite` (insert and verify, D7). Standard library only.
- **`src/agentic_mbse/research/holdout.py` (changed).** `_research_table` calls `read_toolkit_table` and turns a defect into `HoldoutGuardError`. Still fails closed, still validates only `holdout-guard`.
- **`src/agentic_mbse/validation/execution_target.py` (new).** Target types, `resolve_target`, `Category`, `Display`, `display()`, `LEGACY_CATEGORY`.
- **`src/agentic_mbse/validation/subset_presentation.py` (new).** Turns the contract result, advisories and legacy issues into L6 issues, `summarized`, metrics, `pass_note` and the report detail, using `display()`. Computes "shadowed by".
- **`src/agentic_mbse/validation/level6_architecture.py`, `adr002.py` (changed).** Exception sites per Appendix B; `validate_architecture` follows the three steps; String suppression (D10); renamed title; stale citations fixed.
- **`src/agentic_mbse/validation/common.py` (changed).** `QualityCheckResult` gains `summarized`, `pass_note`, `report_detail` (all default empty); `AggregatedResult` collects pass notes; a `check_error_issue()` helper; the `common.py:82` citation is removed.
- **`src/agentic_mbse/validation/runner.py` (changed).** Crash recording, L6 override threading, final line, renamed title.
- **`src/agentic_mbse/validation/report.py` (new).** Builds and writes the JSON report.
- **`src/agentic_mbse/sysml/subset_coverage.py` (new).** Coverage version and list.
- **`src/agentic_mbse/sysml/subset_advisories.py` (new).** The two advisories and their failures.
- **`src/agentic_mbse/sysml/types.py` (changed).** New `ValidationCode` members (D8); the L6 comment rename.
- **`src/agentic_mbse/cli/__init__.py` (changed).** `validate --execution-target`, `--json-report`; `init --execution-target`, prompt, summary.
- **`scripts/l6_subset/run_consumers.py` (new).** The before/after safeguard and the dc3 evidence runs (Appendix C).
- **Docs.** README, `skills/model-validation/SKILL.md` (row and statements), CLAUDE.md § Architecture L6 line, `docs/research-seam.md:350` and `:414-415`. P-0001 at close.

## Non-Goals

- Changing generator behavior or anything in sysml-codegen or Item 2 (owner boundary, 2026-10-18).
- Deciding String metadata policy (Item 2), the PUSH-DOWN rows that wait on Item 2, the pattern doc and fence harness (Item 5), workflow gates (Item 6).
- Changing other levels' checks or truncation. Only the runner's crash handling reaches them.
- Fixing the simple-name collision in `L6_CALC_DEF_NO_INSTANTIATION`. The audit records it.
- A per-path or per-package target. One target per project.
- A record of an earlier "leave unset" answer. Out, because the spec chose re-asking over new state.

## Implementation Notes

- **Settings reader behavior.** Absent file or absent table → empty table, not a defect. A defect never depends on values. Keep the guard's existing message shapes except "its only key is 'research'", which becomes the allowed set; update the research tests that assert it.
- **Insert algorithm (D7).** Refuse a symlink before reading. Decode UTF-8 strictly. Parse. If `tool.agentic-mbse.execution-target` exists, stop (report). Find header lines matching `[tool.agentic-mbse]` (any spacing, bare or quoted key, optional comment). Exactly one → insert `execution-target = "<v>"` on the next line, using that line's newline bytes. None → append `\n[tool.agentic-mbse]\nexecution-target = "<v>"\n`, adding a newline first if the file lacks one. Verify, then write atomically (temp file in the same directory, `fsync`, copy the mode, `os.replace`). TOML 1.0 allows a super-table header after its sub-table, so `[tool.agentic-mbse.research]` followed by an appended `[tool.agentic-mbse]` is valid; the golden test proves it with `tomllib`.
- **Exception-site pattern.** Inside element loops: `except Exception as error: issues.append(check_error_issue(check, element, error)); continue`. Enumeration that fails: one `L6_CHECK_ERROR` for the check, no findings from it. Helpers that "return False on failure" (`_is_calc_usage`, `_is_part_usage`, `is_expose_binding`'s outer catch, `_is_invocation`) stop catching, so the caller's element handler reports. Keep `get_qualified_name` and `get_element_location` fallbacks: they only affect display text. `validate_architecture` wraps each top-level check call so an escaped exception becomes `L6_CHECK_ERROR` naming that check and the next check still runs.
- **JSON report schema** (`validate-report/v1`): `{schema, agentic_mbse: {version, source}, command: {path, mode, level}, overall_success, exit_code, levels: [{level, name, status: passed|failed|crashed, metrics, issues: [ValidationIssue.model_dump(mode="json") + display], unstructured: [str], summarized: [...], profile: {...}|null}]}`. `unstructured` is `issues` minus the `str()` of each structured issue, as a multiset, so other levels need no change. L6's `profile`: target resolution, versions, coverage version and list, scope, verdict, counts, every finding (rule, shape, context, outcome, reason, detail_reasons, subject name and id, location, occurrence_count, remedy, semantic_limits, display, shadowed_by), every unverified check (rule, context, location, cause, detail, display), advisories, and check errors. Lists keep contract order; `json.dumps(..., indent=2, ensure_ascii=False)` with fixed key order.
- **Matrix row closing.** MULTIPLICITY-SHAPE is closed by editing `tests/fixtures/subset_profile/inventory/matrix.toml` to cite the new L6 test, then regenerating `matrix.md` with `scripts/subset_profile/render_matrix.py`. Check `tests/test_subset_matrix.py` still holds (`PUSH_DOWN_ROWS`, `:28-39`).
- **Codegen citations** must be read with `git -C <sysml-codegen> show b5663c07:<path>` in a session that can read sysml-codegen. Correct or delete each; never cite a working-tree line.

## Potential Risks

- **fusion-tea L6 flips under unset** because the contract or an advisory walker crashes on a shape no fixture had. Mitigation: spike S1 first; the stop-and-show rule.
- **Native lowering stays mostly empty** because codegen evidence is not gathered. Mitigation: the table degrades to "keep severity"; the audit lists each unlowered row so the gap is visible.
- **The opaque-expression advisory may have no reachable SysML shape.** Mitigation: learning test S2; if none is found, record that, ship only the wrapper advisory, and surface the row as still open.
- **Text output changes** (issue order, new metric lines, title) break tests or scripts that grep L6 output. Mitigation: grep the repo's tests and skills for the old title and strings before changing them.
- **The holdout guard's behavior shifts** for projects that set `execution-target`: today that key makes every `register` fail closed. After this item it is allowed. That is intended and is a relaxation of a research fault; it is recorded in the docs change.

## Integration Strategy

L6 keeps its entry point (`validate_architecture(models_path, design_path_filter)`) and gains one keyword argument. Existing tests that call checks directly keep working; tests that asserted a swallowed failure is clean will now see `L6_CHECK_ERROR`, which is the intended change. Consumers adopt by adding one line to `pyproject.toml` or re-running `init --execution-target`. Until they do, they run as unset: same pass/fail as today unless a hidden failure is now reported (R3-2, measured by the safeguard).

## Validation Approach

- **Table tests.** `display()` over every (category, target) cell; `LEGACY_CATEGORY` covers exactly the 17 L6 codes; `TOOLKIT_KEYS` rejects a key outside the set in both readers.
- **Spec criteria.** Each Success Criterion in the spec maps to a test or evidence file; the plan carries that map. Fixture projects are built in `tmp_path` with a `work/BACKLOG.md` marker so the project root is the fixture, never the test runner's checkout or `$HOME`.
- **Exception sites.** One test per site in Appendix B, forcing the exception with `monkeypatch` on the SysIDE adapter call or helper the site wraps, under each target.
- **Golden files** for `init`: byte comparison of the whole file, with and without `--force`.
- **Evidence.** `scripts/l6_subset/run_consumers.py` writes `evidence/before-after.{md,json}`, `dc3-baseline-l6.md`, `dc3-repaired-l6.md`; `legacy-l6-audit.md` is written by hand from Appendix A plus the gathered codegen evidence.
- **Repository checks.** `uv run pytest tests/`, `uv run mypy src/`, `uv run ruff check src/ tests/`; the evidence notes which tests needed the SysIDE licence.

## Next-Stage Handoff

**Fixed:** the three-step L6 shape; the severity table; the module split; the issue codes; "shadowed by" per D9; D3 (setting error stops L6); D7 (no `tomlkit`); the report option and schema shape; the safeguard procedure in Appendix C.

**Open for the plan:** exact wording of each line within the tested phrases; the prompt text; how many plan phases.

**De-risk first (plan Phase 0), each a spike or kept learning test:**

- **S1 (spike, blocking).** Run `extract_subset_facts` + `evaluate_subset_profile` and both advisory walkers on `git archive` exports of fusion-tea `f96ad312`, dc3 `808464d` and `60b44d5` at the branch base. Must show: no exception, the run time, and dc3 counts equal to Item 1's (236 / 32 / 6 / 50). If fusion-tea raises, show the owner before building presentation. *Spike result (`spikes/findings.md`):* nothing raised on any tree, and dc3 baseline counts equal Item 1's. But fusion-tea extraction takes about 226 s (dc3: 14-20 s), so B1 holds for "cleanly" and not for "quickly". About 201 s of that is one loop, `_inherited_into` (`constraint_extraction.py:873-882`), which scales as constraint usages × context features. fusion-tea's and dc3 baseline's L6 already fail today, so neither can flip pass→fail.
- **S2 (learning test, kept).** Find a SysML expression that parses in SysIDE 0.8.4 and reaches `reconstruct_expression`'s `str(node)` branch; confirm `sum(filter(...))` or `sum(Evaluation(...))` parses and fills `wrappers`. Must show a firing and a non-firing fixture for each advisory, or record that a shape is unreachable. *Spike result (`spikes/findings.md`):* both fire on load-clean models. Wrapper fires on `sum(cells.mass->collect {...})`, `sum(abs(...))` and similar, and not on `sum(cells.mass)`. Opaque fires on `new Cell()`. Both walkers also raise `SemanticEvidenceError` on some valid shapes (`sum(cells.?{...}.mass)`, `Cell.metadata`). Under I1 that is an ERROR from a WARNING-at-most advisory; surfaced as an open question there.
- **S3 (learning test, kept).** On a two-spelling String fixture, `SysideAdapter.element_id(attr)` equals the String finding's `subject.element_id`. D10 depends on it. *Spike result (`spikes/findings.md`):* ids match wherever both checks see the attribute (fixture 2/2, dc3 `808464d` 3/3). On dc3 `60b44d5` the legacy check flags no String: all 30 are bare `:>> x = "..."` `ReferenceUsage`s, which it never iterates. No tree has a legacy-flagged String the contract misses.
- **F4 (read, not code).** Read sysml-codegen at `b5663c07` for each citation and each "generator-only cause" row in Appendix A. Needs a session with read access to sysml-codegen. Rows not confirmed keep today's severity under `native`. *Spike result (`spikes/f4-codegen-citations.md`):* confirmed: `L6_ANONYMOUS_RETURN`, `L6_BODY_ASSIGNMENT_IMPL_LOSS`; `L6_CALC_DEF_NO_INSTANTIATION` with a caveat; `L6_MISSING_QUALIFIED_NAME` weakly. Partial: V4, UNEXTRACTABLE (other). Not generator-only: `L6_INVALID_QUALIFIED_NAME`, `L6_INVALID_BINDING_FORMAT`, `L6_ATTR_REDEF_EXPR_DROPPED`. `hierarchy_resolver` is deleted. Several L6 comments cite code that no longer exists.
- **F5 (read, not code).** At dc3 `808464d`, `60b44d5` and fusion-tea `f96ad312`: root markers in the archive, and the root `pyproject.toml`'s `[tool]` tables. The safeguard script records both; read them before Phase 0 so a stray `[tool.agentic-mbse]` key is not a surprise. *Spike result (`spikes/findings.md`):* each tree's root is the tree itself, with all three markers. No `[tool.agentic-mbse]` or `[tool.agentic_mbse]` at any pin.

## Appendix A: Legacy-check audit (provisional; the evidence file confirms or corrects each row)

"Cause" is from reading agentic-mbse's own code and comments. "Evidence needed" is what `legacy-l6-audit.md` must hold before the native column takes effect. Every "native" entry other than "unchanged" is conditional on that evidence (spec: a row without evidence keeps today's severity).

| Code | What it checks | Today | Cause as written | Category | unset | generated | native | Evidence needed |
|---|---|---|---|---|---|---|---|---|
| `V1_CALC_DEF_LOCATION` | calc def in `designs/` | ERROR | ADR-002 placement rule (`adr002.py:42-91`) | own applicability | ERROR | ERROR | ERROR | none (not a generator check) |
| `V2_DYNAMIC_EXPRESSION` | design expression references a foreign value | ERROR | ADR-002 rule 3 as relaxed for FORMULA (`adr002.py:506-627`) | own applicability | ERROR | ERROR | ERROR | none |
| `V4_UNSUPPORTED_OPERATOR` | operator outside `+ - * / [` in a design expression | ERROR | ADR-002 (`adr002.py:94-180`) | own applicability | ERROR | ERROR | ERROR | none; S1 also records whether `if` reaches it |
| `V4_STATIC_FUNCTION_INVOCATION` | any call in a static design expression | WARNING | codegen cannot extract a static default (`adr002.py:183-198`) | generator-only if shown | WARNING | WARNING | INFO | codegen extraction site; boundary fixture: an allowlisted call (`sum`) fires V4 and no contract finding, so not a duplicate |
| `L6_MISSING_QUALIFIED_NAME` | calc def/usage without a qualified name | ERROR | codegen naming (EQN, ADR-001) (`level6_architecture.py:175-302`) | generator-only if shown | ERROR | ERROR | INFO | codegen naming site |
| `L6_INVALID_QUALIFIED_NAME` | unquoted space, leading `::` or `_` in a segment | ERROR | codegen EQN derivation and quoted-name sanitizing (`:163-173`) | generator-only if shown | ERROR | ERROR | INFO | codegen sanitizer and EQN site |
| `L6_CALC_DEF_NO_OUTPUT` | calc def with no out/return | ERROR | a calc with no result | kept (native correctness) | ERROR | ERROR | ERROR | none |
| `L6_CALC_DEF_NO_DIRECTION` | typed parameter without direction | WARNING | ambiguous parameter | kept | WARNING | WARNING | WARNING | none |
| `L6_INVALID_BINDING_FORMAT` | chain path with `::`, reference path with `.` | ERROR | codegen binding paths (`:400-473`) | generator-only if shown | ERROR | ERROR | INFO | codegen binding-path site |
| `L6_DESIGN_ATTR_INCOMPLETE` | design attr with no value | ERROR | "bind to calc output" (`:559-570`) | kept unless shown | ERROR | ERROR | ERROR, or INFO with evidence | native fixture: what SysIDE evaluation does with a valueless design attr a calc reads; otherwise kept |
| `L6_DESIGN_ATTR_UNEXTRACTABLE` (String value) | String literal value | ERROR | replaced (gate R3-1) | replaced by `omitted` | WARNING | WARNING | INFO | the String tests |
| `L6_DESIGN_ATTR_UNEXTRACTABLE` (other) | value the static evaluator cannot reduce | ERROR | codegen numeric default (`:538-557`) | generator-only if shown | ERROR | ERROR | INFO | codegen default-extraction site |
| `L6_ANONYMOUS_RETURN` | anonymous `return` in a calc def | ERROR | "codegen's V8": no output channel (`:578-590`) | generator-only if shown | ERROR | ERROR | INFO | codegen V8 site |
| `L6_BODY_ASSIGNMENT_IMPL_LOSS` | output set by body assignment | WARNING | codegen auto-impl lost (`:765-775`) | generator-only if shown | WARNING | WARNING | INFO | codegen capture site |
| `L6_CONSTRAINT_MALFORMED_NUMERICAL` | executable profile BLOCK | ERROR | executable profile (`:635-697`) | kept (gate R3-1) | ERROR | ERROR | ERROR | none |
| `L6_CONSTRAINT_NON_NUMERICAL` | executable profile NON_NUMERICAL | WARNING | "will not execute" | kept unless shown | WARNING | WARNING | WARNING, or INFO with evidence | whether the native route executes the predicate; the profile is not generator-only by construction |
| `L6_CALC_DEF_NO_INSTANTIATION` | calc-bearing part def never instantiated | ERROR | calcs dropped at extraction (`:700-712`) | generator-only if shown | ERROR | ERROR | INFO | codegen extraction site; record the simple-name collision |
| `L6_ATTR_REDEF_EXPR_DROPPED` | `attribute :>> x = <expr>` | WARNING | codegen redefinition scan (`:843-860`) | generator-only if shown | WARNING | WARNING | INFO | `hierarchy_resolver` at `b5663c07` |
| Manifest failures | `manifest.yaml` unusable or subsystem missing | fail | own applicability (`:125-157`) | own applicability | fail | fail | fail | none |
| Setup failures | missing path, model load failure | fail | `:938-966` | own applicability | fail | fail | fail | none |
| New: contract findings | ES-001/003/004/005/006/007/010, indexed reference | — | the contract | by outcome | WARNING | by outcome | INFO | contract tests |

Compared with the spec's provisional table: `L6_DESIGN_ATTR_INCOMPLETE` and `L6_CONSTRAINT_NON_NUMERICAL` default to kept under `native`. Their stated causes are not generator-only on their face, so they need a native-route result, not only a codegen citation. The proposed native lowerings are therefore at most 7 ERROR→INFO and 4 WARNING→INFO, as in the spec, and at least 0, each conditional.

## Appendix B: Exception sites

Lines are at `08dca0d8`. "Element" = report `L6_CHECK_ERROR` for that element and continue; "check" = one `L6_CHECK_ERROR`, no findings from that check; "count" = metric `not computed` plus `L6_CHECK_ERROR`.

| Site | Today | Change |
|---|---|---|
| `level6_architecture.py:191`, `:246`, `:320`, `:418`, `:502` (enumeration) | empty list | check |
| `:230`, `:289` (`AttributeError`) | false `L6_MISSING_QUALIFIED_NAME` | element, no finding |
| `:374`, `:470`, `:572`, `:623`, `:759`, `:832`, `:907` (per element) | skip silently | element |
| `:520` (`is_instance` on owner) | skip bypassed, false finding possible | element, attribute not checked |
| `:723` (instantiated-set enumeration) | partial or empty set, false `NO_INSTANTIATION` | check, no findings |
| `:960` (model load) | reported | kept |
| `:973`, `:978` (counts) | 0 | count |
| `adr002.py:87`, `:177`, `:254`, `:624` (per element) | skip silently | element |
| `adr002.py:207` (`_is_invocation`) | node treated as not a call | propagate to `:254`'s element handler |
| `adr002.py:268` (`_get_calc_usage_names`) | no caller | delete |
| `adr002.py:277`, `:335` (`_is_calc_usage`, `_is_part_usage`) | False | propagate to the caller's element handler |
| `adr002.py:423` (`is_expose_binding`) | False, so not exempt: false V2/V4/UNEXTRACTABLE | propagate; caller reports element, no finding |
| New: `check_constraint_executability`, contract, advisories, any check call | escapes L6, lost by the runner | check |
| `runner.py:128-137` (any level) | level not recorded, run passes | `LEVEL_CRASHED`, level failed |

Count: 17 + 9 broad sites plus 2 `AttributeError` = 28, matching the spec. The epic's "27" is not reconciled further; this table is per site.

## Appendix C: The before/after safeguard

`scripts/l6_subset/run_consumers.py before-after --base ebb3d467 --branch HEAD` does this, and writes `evidence/before-after.{json,md}`:

1. **Refuse a dirty branch.** `git status --porcelain -- src pyproject.toml uv.lock` must be empty, and `--branch` must equal `git rev-parse HEAD`.
2. **Export both code revisions.** `git archive` agentic-mbse at the base and at the branch into `code-base/` and `code-branch/` in one `TemporaryDirectory` under `/tmp` (outside `$HOME`). Check each with `git get-tar-commit-id`.
3. **Export each consumer tree.** dc3 `808464d`, dc3 `60b44d5`, fusion-tea `f96ad312`, each into its own folder, with Item 4's export rules: verify the tar commit id, extract with `tarfile`'s `data` filter, skip absolute symlinks outside `models/` and list them (`scripts/positional_binding/run_trees.py`).
4. **Check the extraction parent is not a project root.** `find_project_root(start=<tmp parent>)` must be None, so a tree without markers resolves to "no root", never to a stray `/tmp/.claude`.
5. **Record each tree's settings input.** The script calls `find_project_root(start=<tree>/models)` and records the root, the `pyproject.toml` path and its `[tool.agentic-mbse]` table (or "absent").
6. **Run full validation six times** (3 trees × 2 code revisions): the venv's Python with `PYTHONPATH=<code export>/src`, `cwd=<tree>`, `-m agentic_mbse validate --complete models`, target unset (no option). The branch runs add `--json-report`. Each run first prints `agentic_mbse.__file__`, and the script fails unless it lies inside that run's code export. Capture stdout, stderr, exit code and wall time.
7. **Prove the root each run resolved.** Base: L2's `Positional pin list: none (looked at <root>/positional-pins.toml)` metric. Branch: L6's `Execution target` metric and the report's target resolution. Both must agree with step 5.
8. **Per-level status.** Base: parse `✅/❌ Level N:` lines, and `❌ Error running Level N` as `crashed (recorded as pass)`. Branch: read from the report. Record the SysIDE version.
9. **Compare.** For each tree and level, before → after status, and the exit codes. Any pass→fail (level or run) is flagged, the Markdown leads with it, and the script exits 1. That is the stop-and-show: implementation stops, and the orchestrator shows the owner before merge.
10. **Sibling repos untouched.** Record HEAD and `git status --porcelain` of dc3 and fusion-tea before and after; fail if either changed (Item 4's pattern).

`run_consumers.py l6-evidence` reuses steps 1–5 and writes `dc3-baseline-l6.md` (branch, `--level=6 --execution-target=generated --json-report`, and a second run unset) and `dc3-repaired-l6.md` (`60b44d5` under `generated`), reading every count from the report.

---
Next Step: design review (`/_my_design_review`, fresh session), then `/_my_plan`. Candidate decision records after approval: D7 (append-and-verify for owner TOML, no `tomlkit`), if it passes the density bar in `.project/adr/README.md`.
