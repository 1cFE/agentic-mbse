# Design: L6 integration and execution-target settings (EXEC-SUBSET-CONTRACT Item 3)

**Status:** Revised after design review and spike (2026-10-18)
**Owner:** Reid Westwood
**Created:** 2026-10-18
**Branch:** `l6-subset-profile` (base `main` at `ebb3d46710a4c1476bb12fa0e9decf0088ddb2c5`)

## Overview

L6 runs Item 1's contract on every model, decides how loud each result is from one project setting (`execution-target`), reports every failed inspection as a failure, and can write the full result as JSON. A small shared module owns the `[tool.agentic-mbse]` table for both L6 and the research holdout guard. One `validate` run loads the model and extracts constraint facts once, shared by L4, L6's legacy checks and the contract.

## Related Artifacts

- Spec: `spec.md` (revised after review). Spec review and resolutions: `spec-review.md`.
- Design review: `design-review.md` (Revise; M1–M3, S1–S4; resolutions recorded there).
- Spike: `spikes/findings.md` and `spikes/f4-codegen-citations.md` (contract on the three trees, advisory shapes, String ids, roots, codegen citations at `b5663c07`).
- Owner decisions, gate outcomes and the owner boundary (no Item 2, no sysml-codegen writes): `briefs/align.md`.
- Product-lens ledger: `product-lens.md`.
- Epic: `.project/backlog/epic_executable-subset-contract.md` § Item 3 and § Design principles. No Required Reading is listed for Item 3.
- Decisions: ADR 0001 (contract ownership; invariants 2 and 3 bind this design), ADR 0002 (project-root discovery for the pin list, reused here).
- Item 1 archive: `.project/completed/20261018_exec-subset-profile/`. Item 4 archive: `.project/completed/20261018_positional-binding-check/` (consumer-run scripts and evidence pattern).
- Follow-ups filed from the spike: backlog `L6-LEGACY-CHECKS-ON-ACCEPTED-SHAPES`, `CONSTRAINT-EXTRACTION-INHERITED-SCAN` (`.project/backlog/BACKLOG.md:29-30`).

## The Point

[AGENT] (ratified by owner, 2026-10-18; `briefs/align.md`) `agentic-mbse validate` should tell a modeler up front whether the code generator will refuse their model, using Item 1's contract, instead of the modeler finding out one generator run at a time. dc3 found its blockers through five sequential generation runs; the contract reports 236 refused findings on that baseline in one pass.

Each project says in its committed `pyproject.toml` how it runs (`execution-target`), so native-only projects are not buried in generator findings. Unset shows generator findings as warnings; `native` folds them into one INFO line; `generated` makes confirmed refusals errors.

Two things must hold in everything a user reads. First, nothing claims the model "will generate": `clear` means only "no refusals found by the implemented rules", and L6 is not `sysml-codegen check` (ADR 0001 invariant 2). Second, a broken check never passes: under every target a crash or a failed inspection fails the run ([AGENT] delegated by owner, 2026-10-18, gate R3-2).

## Research Findings

**What exists and is reused**

- **The contract** (`sysml/subset_profile.py`). `extract_subset_facts(model)` (`subset_extraction.py:466`) then `evaluate_subset_profile(facts)` (`subset_profile.py:1285`) returns a `SubsetProfileResult` (`:743`): verdict, scope, findings, unverified checks, counts. Each `SubsetFinding` (`:636`) has rule, shape, context, outcome, reason, subject `ElementRef`, `SafeLocation`, evidence. Remedy and semantic limits live on the rule record (`:334`). Findings and unverified checks are already sorted (`:1352-1353`).
- **Project root** (`project_root.py:19`). Item 4's pin list reads only at the root (`positional_pins.py:143`) and reports where it looked (`positional_check.py:178`). The setting copies that shape.
- **The holdout guard's reader** (`research/holdout.py:219-284`). It rejects `[tool.agentic_mbse]` and any `[tool.agentic-mbse]` key except `research`, and turns every fault into a guard that refuses at first use.
- **Editing owner TOML without a TOML writer** (`cli/installation.py:344-381`). `register_codex_agents` appends text, re-parses with `tomllib`, and refuses if it does not parse.
- **Option threading** (`runner.py:94-100`) and the **final-line qualifier** (`common.py:166-176`, `runner.py:155-159`).

**Facts that shape this design**

- **"Shadowed by" needs no owner facts.** In dc3's result each of the 6 unconfirmed `constraint-predicate` findings shares its `subject_id` with a refused `calc-owned-assertion` finding, because that rule names the constraint itself as subject (`subset_profile.py:890-902`). The spec's owner-based condition matches nothing. See D9.
- **L6 reports warnings through `issues`.** `add_issue` appends every structured issue to `issues` (`common.py:42-52`). Pass/fail is "no ERROR and no manifest issue" (`level6_architecture.py:1009-1011`).
- **Exception sites** match the spec: 17 + 9 broad sites plus 2 `AttributeError` (Appendix B).
- **Constraint extraction already runs twice per full run and is slow on fusion-tea.** L4 (`level4_constraints.py:65`) and L6 (`level6_architecture.py:650`) each call `extract_identified_constraint_facts` on a model each level loaded itself (`level4_constraints.py:105`, `level6_architecture.py:959`). The contract would call it a third time (`subset_extraction.py:452-459`). On fusion-tea one call takes about 201 s, almost all in `_inherited_into` (`constraint_extraction.py:873-882`; spike profile).
- **Facts cannot be joined across separate loads.** An anonymous element gets a session-local UUID (`fact_refs.py:21-27`), and the contract joins constraint facts to live elements by id (`subset_extraction.py:493-497`). So sharing facts means sharing the loaded model too. See D14.
- **Spike results** (`spikes/findings.md`):
  - The contract and both advisory walkers run without raising on fusion-tea `f96ad312`, dc3 `808464d` and `60b44d5`. dc3 baseline counts equal Item 1's (236 / 32 / 6 / 50).
  - fusion-tea and dc3 baseline already fail L6 today. Only dc3 `60b44d5` passes, and its verdict is `clear`.
  - Each tree resolves its own root (all three markers present). No pinned `pyproject.toml` has `[tool.agentic-mbse]` or `[tool.agentic_mbse]`.
  - String ids match wherever both checks see the attribute. No tree has a legacy-flagged String that the contract misses. The contract adds String warnings where L6 said nothing: 131 on fusion-tea, 30 on `60b44d5`, 29 on `808464d` (plus 3 that replace legacy errors).
  - Both advisories fire on load-clean models. Both walkers also raise `SemanticEvidenceError` on some valid shapes (`sum(cells.?{ in c : Cell; c.ok }.mass)`; `Cell.metadata`).
  - At `b5663c07`, of the nine "generator-only if shown" rows, four are confirmed, two are partial and three are not generator-only (Appendix A). 9 of 12 codegen citations in L6 code are stale (`spikes/f4-codegen-citations.md`).
- **No `tomlkit`** in `pyproject.toml` or `uv.lock`.
- **No licence-gated test marker exists.** Tests that load models read `SYSIDE_LICENSE_KEY` from `.env` (`tests/conftest.py:7`) and fail without it; nothing skips. `pyproject.toml:103-106` registers only `corpus` and `slow`.

## Core Concept

L6 becomes three steps: **read the target, collect results, present them.**

1. **Read the target.** L6 finds the project root above the validated path, reads `[tool.agentic-mbse]` through the shared settings module, and resolves one target: from the file, from `--execution-target`, or unset. A broken file or bad value is a configuration error, and L6 stops there.
2. **Collect results.** L6 runs the contract first, then the legacy checks, then two advisories, all over one loaded model and one set of constraint facts shared with L4. Each result is tagged with a *category*: a contract outcome, an unverified check, a legacy check's audited category, an advisory, or a check failure. A failure becomes a named `L6_CHECK_ERROR` for that check or element, and the other checks keep running.
3. **Present them.** One pure function maps (category, target) to how the result is shown: ERROR, WARNING, folded into the native INFO summary, count only, or the legacy check's own severity. L6 renders the verdict, scope and coverage lines, issues and metrics, and attaches the full profile for the JSON report.

The key idea: **the contract decides what is true, and the target decides only how loud it is.** L6 never asks "is this String?" or "is this refused?" itself. That keeps L6 from re-deriving decisions (ADR 0001), makes severity testable as one table, and keeps check failures out of the policy's reach: they are ERROR in every column.

Composes with: the contract (decisions), `find_project_root` (where to look), the holdout guard (shares the key set), the runner (crash handling, the run-scoped model and fact sharing, final line, report), and `cmd_init` (adds the key with the installer's append-and-verify pattern).

## Key Bets

- **B1. The contract runs cleanly on the consumer trees.** *Spike: holds* on all three trees. *If false on a future tree →* `L6_CHECK_ERROR`, so the run fails loudly rather than passing.
- **B2. Some legacy generator checks have a generator-only cause.** *Spike: four do* (Appendix A). *If false for a row →* the row keeps today's severity under `native`. Three rows turned out to error on shapes the generator accepts; they stay unchanged under every target and go to backlog `L6-LEGACY-CHECKS-ON-ACCEPTED-SHAPES`.
- **B3. A text insert verified by `tomllib` is enough to add one key safely.** *If false →* `init` could corrupt a committed file. The whole parsed document is compared before and after, so the failure mode is a needless refusal.
- **B4. Nothing in today's passing consumer runs hides a crash or a swallowed failure.** *If false →* the safeguard shows pass→fail and implementation stops for the owner.
- **B5. Levels 2–6 only read the loaded model.** So one shared load gives each level the same results it gets from its own load. *If false →* a level's results would depend on what an earlier level did. Tested by running each level with and without the shared session, and by the safeguard comparing L1–L5 issue lists before and after on the three trees.
- **B6. The contract reports every String value the legacy design-attribute check would flag.** The String suppression (D10) needs it. *Spike: holds* on all three trees and the two-spelling fixture. *If false at some position →* that String keeps its legacy ERROR (safe, but it breaks the "every folder" criterion there). A test covers a String attribute outside every generator root.

## Key Decisions

- **D1. Shared settings module at `src/agentic_mbse/project_settings.py`.** It holds `TOOLKIT_KEYS = {"execution-target", "research"}` and one reader that returns the `[tool.agentic-mbse]` table or a named defect. It checks key membership only, never values. It lives at package top level for the same reason as `project_root.py`: `research`, `validation` and `cli` all import it. *Rejected:* defining the set in `holdout.py` (validation would import research); a reader per package (the set would drift).
- **D2. Execution target and severity policy in one module, `validation/execution_target.py`.** Target types, `resolve_target()` and the pure `display()` table. *Rejected:* a separate policy module for one table.
- **D3. A setting error stops L6.** L6 reports `L6_SETTING_INVALID` and the target metric, runs no checks, and fails. Levels 1–5 run as usual. Unknown keys and the underscore table are configuration errors under the R3-2 check-failure outcome (`spec.md:139`). *Rejected:* running L6 "as if unset" (the fallback the spec forbids).
- **D4. Every escaped exception becomes a named result at the narrowest safe scope.** Per element where the loop can continue; per check where enumeration failed; per level in the runner. Always ERROR. One exception: D15. *Rejected:* one broad try around L6 (one failure would hide every other result).
- **D5. Native summary is a metric line; unverified checks under `native` are one aggregated WARNING issue.** Summarized findings are kept as `summarized` (INFO), not in `issues`. *Rejected:* one INFO issue per finding (236 lines of noise); one WARNING per unverified check under native.
- **D6. JSON report via `validate --json-report PATH`.** One file per run, levels in run order, written after the run, including crashed levels. It carries every level's `warnings` and the run's pass notes (schema in Implementation Notes). *Rejected:* changing text truncation (spec non-goal).
- **D7. `init` adds the key by text insertion plus whole-document verification, no `tomlkit`.** It first runs the settings reader and refuses on any existing defect. It inserts after the single `[tool.agentic-mbse]` header, or appends a new table, and refuses on two or more header matches. It re-parses and requires the result to equal the original plus exactly one key. *Rejected:* `tomlkit` (a new dependency for a one-line insert, still needing every refusal case).
- **D8. Contract issue codes per outcome**, not per reason: `L6_SUBSET_REFUSED`, `_UNCONFIRMED`, `_EXCLUDED`, `_OMITTED`, `_UNVERIFIED`, `_UNASSESSED`, `_ADVISORY`, `_ADVISORY_UNVERIFIED`, each carrying the contract reason or walker code in `reason_code`. Plus `L6_CHECK_ERROR`, `L6_SETTING_INVALID`, and `LEVEL_CRASHED`. *Rejected:* one code per reason (the argument `types.py` records for `reason_code`).
- **D9. "Shadowed by" = another rule's `refused` finding has the same subject declaration (same `ElementRef.element_id`).** Computed in presentation for every finding that is not itself refused by that rule; the outcome never changes; the report's `shadowed_by` is null when none applies. If a second consumer (Item 5's guidance) needs it, it moves to an additive field on the contract result instead of being computed again. *Rejected:* the spec's owner-based condition (matches nothing in dc3).
- **D10. The String replacement consumes the contract, which runs first.** L6 runs the contract before the legacy checks and passes the set of `string-value-omission` subject ids into `check_design_attr_completeness` as a parameter. An attribute in that set gets no `L6_DESIGN_ATTR_UNEXTRACTABLE`. If the contract failed, the parameter is `None` and every legacy error stays (and the run fails on the contract's `L6_CHECK_ERROR` anyway). Coverage assumption B6 is stated and evidenced by the spike. *Rejected:* L6 testing "is the value a String literal" itself (re-deriving the decision); a presentation post-filter (the orchestrator chose ordering, and passing the set keeps the dependency visible in the check's signature).
- **D11. Coverage list as a Python module `sysml/subset_coverage.py`** with `SUBSET_COVERAGE_VERSION = "subset-coverage/v1"`. *Rejected:* adding it to `subset_profile_rules.toml` (moves `SUBSET_PROFILE_VERSION`).
- **D12. Advisories in `sysml/subset_advisories.py`, detected through the walkers' own code.** (a) **Opaque expression (UNSUPPORTED-SHAPE-MESSAGE):** a pure predicate `falls_to_text_fallback(node) -> bool` is extracted from `reconstruct_expression`'s dispatch (`expression.py:298-356`), and `reconstruct_expression` itself calls it to choose its last branch. A sibling `text_fallback_nodes(expr)` in `expression.py` returns the nodes reconstruction reaches for which the predicate is true. `reconstruct_expression`'s output is unchanged, proven by a test over every expression in the existing fixtures (Item 2's agent depends on this function). (b) **Wrapper (WRAPPER-SHAPE):** on sites that invoke `sum`, `decompose_aggregation_expression(...).wrappers` (`aggregation.py:233`, `:383-398`), filtered to `KNOWN_WRAPPER_FUNCTIONS` (`aggregation.py:72`). Any other call inside `sum` (`abs`, say) is already ES-005's refusal. *Rejected:* a line tracer or a second classifier of expression kinds.
- **D13. Text order inside L6.** Tiers: setting error, check errors, ERROR, WARNING. Within a tier: legacy issues in check order, then contract findings ordered refused, unverified, unconfirmed, excluded, omitted and then the contract's own sort, then advisories. So the first five printed lines lead with failures and refusals: incompleteness must not hide refusals (Item 1 product-lens impl-F2). *Rejected:* today's check-call order.
- **D14. One model load and one constraint extraction per `validate` run.** The runner opens a run-scoped `ValidationSession` (`validation/session.py`). Inside it, `load_sysml_model(files)` returns the cached `(model, diagnostics)` for the same file set (key: each resolved path with its size and `mtime_ns`). `session.constraint_facts(model)` memoizes `extract_identified_constraint_facts(model)` per model object, storing either the facts or the raised exception and re-raising it on every later call. L4, L6's `check_constraint_executability` and the contract call it; the contract receives it through a new keyword on `extract_subset_facts(model, extra_roots=(), constraint_facts=extract_identified_constraint_facts)`, which defaults to today's behaviour. Outside a session (direct level calls, tests, Item 2) nothing changes. L1 is untouched: it does not use `load_sysml_model`. *Rejected:* sharing the facts across separate loads (anonymous ids differ per load); fixing `_inherited_into` here (backlog `CONSTRAINT-EXTRACTION-INHERITED-SCAN`, and it changes a file Item 2 consumes).
- **D15. A walker's own "could not inspect" signal is an advisory-unverified WARNING.** When an advisory walker raises `SemanticEvidenceError` (the closed evidence-failure vocabulary, `errors.py:25-39`), L6 reports `L6_SUBSET_ADVISORY_UNVERIFIED`, a WARNING under every target, naming the advisory, the code, the node kind and the location. Any other exception from a walker is `L6_CHECK_ERROR`. Reason: the advisory is at most a WARNING, and a known "unsupported shape" on a load-clean model is "could not decide", like the contract's unverified checks, not a crash. *Rejected:* `L6_CHECK_ERROR` for every walker exception (fails valid models over a WARNING-level check); silence (would hide that the advisory did not run).
- **D16. The legacy unextractable error catches only the evaluator's own signal.** `expression.py` gains a marker base `Unextractable` with `UnextractableValueError(ValueError, Unextractable)` and `UnextractableTypeError(TypeError, Unextractable)`. Each deliberate raise in `evaluate_true_static_expression` (`expression.py:466-567`) uses the subclass of its current type, so existing `except ValueError`/`except TypeError` callers are unaffected. `check_design_attr_completeness` catches only `Unextractable`; anything else is `L6_CHECK_ERROR`. *Rejected:* keeping `except (ValueError, TypeError)` (an evaluator bug or accessor failure would read as a model defect).

## Architecture

```
validate CLI ──(--execution-target, --json-report)──> runner.run_all_checks
   runner: with ValidationSession(): for each level → result | LEVEL_CRASHED ; final line
      L2–L6 load_sysml_model(files) ── session cache (one load per run)
      L4 analyze_constraints ── session.constraint_facts(model)
      L6 validate_architecture(models_path, execution_target=override)
         1 resolve_target ── find_project_root ── project_settings.read_toolkit_table
            └─ TargetSettingError → L6_SETTING_INVALID, stop
         2 model (shared) ─> extract_subset_facts(model, constraint_facts=session.constraint_facts)
                           ─> evaluate_subset_profile ─> String subject ids
                         ─> legacy checks (level6_architecture, adr002; string_subjects=ids)
                         ─> subset_advisories.extract_advisories (D12, D15)
         3 subset_presentation.present(result, advisories, legacy issues, target)
              uses execution_target.display(category, target), subset_coverage, PACKAGED_RULES
            → issues, summarized, metrics, pass_note, report_detail
cmd_validate ── report.write_report(path, aggregated, run_info) after the run
cmd_init ── read_toolkit_table → add_execution_target | prompt | print the line
holdout.load_holdout_guard ── read_toolkit_table (membership) + its own value check
```

Facts and decisions stay in `sysml/`. Severity, wording, the session and the report stay in `validation/`. The settings module knows the table's shape and key set, not what any value means. The runner knows nothing about targets; it carries the override to L6, owns the session, and prints the qualifier L6 hands back.

### Data model

```python
class Target(StrEnum): UNSET = "unset"; GENERATED = "generated"; NATIVE = "native"
TargetSource = FromFile(path) | FromOverride(file_path | None, file_value | None) | Unset(looked_at | None)
@dataclass class TargetResolution: target: Target; source: TargetSource; root: Path | None
class SettingsFault(StrEnum): UNREADABLE; TOML_SYNTAX; NOT_A_TABLE; UNDERSCORE_TABLE; UNKNOWN_KEY
class TargetFault(StrEnum): SETTINGS (wraps a SettingsFault); INVALID_VALUE
@dataclass class TargetSettingError: path: Path; fault: TargetFault; settings_fault: SettingsFault | None; detail: str
class Category(StrEnum): REFUSED; UNCONFIRMED; EXCLUDED; OMITTED; ADMITTED; UNVERIFIED; UNASSESSED; ADVISORY
    ADVISORY_UNVERIFIED; LEGACY_OWN_APPLICABILITY; LEGACY_KEPT; LEGACY_GENERATOR_ONLY; CHECK_FAILURE; SETTING_INVALID
class Display(StrEnum): ERROR; WARNING; NATIVE_SUMMARY; COUNT_ONLY; BASE   # BASE = the legacy check's own severity
def display(category: Category, target: Target) -> Display
```

`LEGACY_CATEGORY: Mapping[ValidationCode, Category]` maps each of the 17 L6 codes to a legacy category. Every generator-only candidate starts as `LEGACY_KEPT`. A code moves to `LEGACY_GENERATOR_ONLY` only in the same change that adds its row to `evidence/legacy-l6-audit.md` and to the fixture `tests/fixtures/l6/native_lowered.toml`; a test requires the mapping's lowered set to equal that fixture.

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
| `ADVISORY_UNVERIFIED` | WARNING | WARNING | WARNING (outside the summary) |
| `LEGACY_OWN_APPLICABILITY` | BASE | BASE | BASE |
| `LEGACY_KEPT` | BASE | BASE | BASE |
| `LEGACY_GENERATOR_ONLY` | BASE | BASE | NATIVE_SUMMARY |
| `CHECK_FAILURE` | **ERROR** | **ERROR** | **ERROR** |
| `SETTING_INVALID` | **ERROR** | **ERROR** | **ERROR** |

Under unset and `generated` no legacy row changes. The only legacy relaxation in this item is the String case, done by suppression (D10).

### What a user sees in L6

Metrics print in this order (wording is fixed by the tests; exact text by the plan):

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

- **Session.** `run_all_checks` wraps the level loop in `ValidationSession()` (D14) and closes it after the last level, releasing the model.
- **Crash.** A level's exception becomes a failed `QualityCheckResult` with one ERROR issue `LEVEL_CRASHED` (`Level N crashed: <type>: <message>`), printed, and fail-fast stops. The traceback still prints with `--verbose`. The level number comes from the check's position in `QUALITY_CHECKS`.
- **Override.** `validate --execution-target {generated,native}`, validated by argparse (bad value: exit 2), passed to L6 through `functools.partial`. With `--level` 1–5 it is accepted and unused.
- **Report.** `cmd_validate` checks the report's parent directory exists before running (else exit 2). After the run it calls `report.write_report(path, aggregated, run_info)`. A write failure prints an error and exits 1.

### `init`

`cmd_init` gains `--execution-target {generated,native}`. After the installer saves, it runs one settings step on `<init target>/pyproject.toml`:

| State | Option given | Terminal, no option | Neither |
|---|---|---|---|
| Table readable, no `execution-target`, layout permits | write it | prompt: generated / native / leave unset (default); write the choice | write nothing; print the unset note with the TOML line and the `init` form |
| No file | create a file holding only the table | same | same |
| Key present, valid, same value | report "already set" | report value, no prompt | report value |
| Key present, different or invalid value | never change; report both values and the allowed values; **exit 1** | never change; report | never change; report |
| Existing defect: the settings reader returns any `SettingsDefect` (unknown key such as `execution_target`, `[tool.agentic_mbse]`, `[tool.agentic-mbse]` not a table, unparseable) | write nothing; print the defect; **exit 1** | print the defect | print the defect |
| Refused layout (below) | print the line and reason; **exit 1** | print the line and reason | print the line and reason |

Refused layouts, each with a test: the file is a symlink; it has more than one hard link (`os.replace` would split it); it starts with a UTF-8 BOM or is not UTF-8; `agentic-mbse` is an inline table; `agentic-mbse` is defined through dotted keys; two or more lines match the `[tool.agentic-mbse]` header pattern; the verification after insertion fails for any other reason. `--force` changes no row. The rest of `init` always completes. `install-commands` never calls this step.

`init` writes `<init target>/pyproject.toml`, while L6 reads `find_project_root(models)/pyproject.toml`. They are the same file because `init` writes `.agentic-mbse/install.json`, a root marker, into the target.

## Required Invariants

- **I1.** No path through L6 turns an exception or a failed inspection into "no issue", a zero count, or a model-defect finding. Every one becomes `L6_CHECK_ERROR` (ERROR, every target) naming the check, or `LEVEL_CRASHED`. The one named exception is D15: a walker's `SemanticEvidenceError` is reported as `L6_SUBSET_ADVISORY_UNVERIFIED` (WARNING, never silent, never in the native summary).
- **I2.** `display(CHECK_FAILURE, t)` and `display(SETTING_INVALID, t)` are ERROR for every `t`, and no check failure appears in the `NATIVE_SUMMARY` set (test).
- **I3.** L6 contains no outcome logic: the only inputs to severity are `SubsetFinding.outcome`, `UnverifiedCheck`, `counts.unassessed_constraints`, advisory records, `LEGACY_CATEGORY` and the target.
- **I4.** `SUBSET_PROFILE_VERSION`, its digest, the rule records and every existing result field are unchanged from `ebb3d467`. Library changes only add: `extract_subset_facts`'s keyword with today's default, `falls_to_text_fallback` and `text_fallback_nodes` beside `reconstruct_expression` with its output unchanged, the `Unextractable` subclasses, and two new modules.
- **I5.** Under unset and `generated`, for every site, the combined severity of legacy plus contract issues is not lower than today's, except the String case (D10).
- **I6.** Each `[tool.agentic-mbse]` reader rejects any key outside `TOOLKIT_KEYS` and validates only its own key's value.
- **I7.** `init` never changes an existing `execution-target` value, never writes when the table has a defect, and never rewrites any byte outside the inserted text. The written file parses, and its parsed value equals the original plus one key.
- **I8.** For the same tree, path and target, the text output and the JSON report are byte-identical across runs.
- **I9.** No line in `validate` stdout or in the JSON report contains "generated-ready", "generation-ready", "ready to generate", "will generate", "generator accepts" or "readiness". The verdict line never contains "clean", "ready" or "passed".
- **I10.** With the session, each level's result equals its result without the session (B5). Inside one run, `extract_identified_constraint_facts` runs at most once per loaded model.

## Component Overview

- **`src/agentic_mbse/project_settings.py` (new).** The key set; `read_toolkit_table(root) -> ToolkitTable | SettingsDefect`; `add_execution_target(file, value) -> SettingWrite` (D7). Standard library only.
- **`src/agentic_mbse/research/holdout.py` (changed).** `_research_table` calls `read_toolkit_table` and turns a defect into `HoldoutGuardError`. Still fails closed; still validates only `holdout-guard`.
- **`src/agentic_mbse/validation/execution_target.py` (new).** Target types, `resolve_target`, `Category`, `Display`, `display()`, `LEGACY_CATEGORY`.
- **`src/agentic_mbse/validation/session.py` (new).** `ValidationSession`: the run's model cache and constraint-fact memo (D14).
- **`src/agentic_mbse/validation/subset_presentation.py` (new).** Turns the contract result, advisories and legacy issues into L6 issues, `summarized`, metrics, `pass_note` and the report detail. Computes "shadowed by".
- **`src/agentic_mbse/validation/level6_architecture.py`, `adr002.py` (changed).** Exception sites per Appendix B; contract-first order; `string_subjects` parameter (D10); `Unextractable` catch (D16); renamed title; citations corrected per `spikes/f4-codegen-citations.md`.
- **`src/agentic_mbse/validation/level4_constraints.py` (changed).** Calls the session's constraint facts. Results unchanged.
- **`src/agentic_mbse/validation/common.py` (changed).** `load_sysml_model` consults the active session; `QualityCheckResult` gains `summarized`, `pass_note`, `report_detail` (default empty); `AggregatedResult` collects pass notes; `check_error_issue()`; the `common.py:82` citation is removed.
- **`src/agentic_mbse/validation/runner.py` (changed).** Session, crash recording, override threading, final line, renamed title.
- **`src/agentic_mbse/validation/report.py` (new).** Builds and writes the JSON report.
- **`src/agentic_mbse/sysml/expression.py` (changed, additive).** `falls_to_text_fallback`, `text_fallback_nodes` (D12a); `Unextractable` subclasses (D16).
- **`src/agentic_mbse/sysml/subset_extraction.py` (changed, additive).** The `constraint_facts` keyword (D14).
- **`src/agentic_mbse/sysml/subset_coverage.py`, `subset_advisories.py` (new).** Coverage version and list; the two advisories and their unverified records.
- **`src/agentic_mbse/sysml/types.py` (changed).** New `ValidationCode` members (D8); the L6 comment rename.
- **`src/agentic_mbse/cli/__init__.py` (changed).** `validate --execution-target`, `--json-report`; `init --execution-target`, prompt, summary.
- **`pyproject.toml` (changed).** Registers a label-only `syside` test marker (S4).
- **`scripts/l6_subset/run_consumers.py` (new).** The before/after safeguard and the dc3 evidence runs (Appendix C).
- **Docs.** README, `skills/model-validation/SKILL.md`, CLAUDE.md § Architecture L6 line, `docs/research-seam.md:350` and `:414-415`. P-0001 at close.

## Non-Goals

- Changing generator behavior or anything in sysml-codegen or Item 2 (owner boundary, 2026-10-18).
- Deciding String metadata policy (Item 2), the PUSH-DOWN rows that wait on Item 2, the pattern doc and fence harness (Item 5), workflow gates (Item 6).
- Changing other levels' checks or truncation. Only crash handling and the shared session reach them, and their results stay identical.
- Speeding up `_inherited_into`. Out, because it changes a file Item 2 consumes; filed as `CONSTRAINT-EXTRACTION-INHERITED-SCAN`.
- Retiring or reclassifying `L6_INVALID_QUALIFIED_NAME`, `L6_INVALID_BINDING_FORMAT`, `L6_ATTR_REDEF_EXPR_DROPPED`. Out, because they are not generator-only and changing them is a rules decision; filed as `L6-LEGACY-CHECKS-ON-ACCEPTED-SHAPES`.
- Fixing the simple-name collision in `L6_CALC_DEF_NO_INSTANTIATION`. The audit records it.
- A per-path target, or a record of an earlier "leave unset" answer (the spec chose re-asking over new state).

## Implementation Notes

- **Settings reader.** Absent file or absent table → empty table, not a defect. Keep the guard's message shapes except "its only key is 'research'", which becomes the allowed set; update the research tests that assert it.
- **Insert algorithm (D7).** Refuse a symlink or `st_nlink > 1` before reading. Refuse a BOM. Decode UTF-8 strictly. Run `read_toolkit_table`; on any defect, refuse. If `execution-target` exists, stop and report. Find header lines matching `[tool.agentic-mbse]` (any spacing, bare or quoted key, optional comment). Two or more → refuse. Exactly one → insert `execution-target = "<v>"` on the next line, with that line's newline bytes. None → append the table, using the file's newline style (the first line ending found, else `\n`) and adding one first if the file lacks a final newline. Verify (parse and compare), then write atomically (temp file in the same directory, `fsync`, copy the mode, `os.replace`). TOML 1.0 allows a super-table header after its sub-table; the golden test proves it with `tomllib`. The plan's `init` phase also checks that a `pyproject.toml` holding only `[tool.agentic-mbse]` does not disturb `uv` in that directory (design review m9).
- **Exception-site pattern.** Inside element loops: `except Exception as error: issues.append(check_error_issue(check, element, error)); continue`. Failed enumeration: one `L6_CHECK_ERROR`, no findings from that check. Helpers that "return False on failure" stop catching, so the caller's element handler reports. Keep the display-only fallbacks in `get_qualified_name` and `get_element_location`. `validate_architecture` wraps each top-level check call so an escaped exception becomes `L6_CHECK_ERROR` naming that check.
- **The reconstruction predicate (D12a).** Move the branch conditions of `reconstruct_expression` into one ordered dispatch that both callers use. `falls_to_text_fallback(node)` is true exactly when no earlier branch applies. `text_fallback_nodes` descends only where reconstruction descends (operator and invocation operands, through `materialize_operands`), so it raises the same `SemanticEvidenceError` reconstruction would. The output-unchanged test runs `reconstruct_expression` on every value expression in `tests/fixtures/**/*.sysml` before and after the refactor (texts recorded once from `ebb3d467` into a fixture) and compares the texts exactly.
- **Session details (D14).** The session is a context variable set by the runner, so nested or concurrent tests without it see today's behaviour. The memo is keyed by `id(model)` and holds a strong reference to the model, so the id cannot be reused within the run. A cached load is returned only if every file's size and `mtime_ns` still match.
- **JSON report schema** (`validate-report/v1`): `{schema, agentic_mbse: {version, source}, command: {path, mode, level, execution_target}, run_info: {constraint_extractions, wall_time_s}, overall_success, exit_code, pass_notes: [str], levels: [{level, name, status: passed|failed|crashed, metrics, issues: [ValidationIssue.model_dump(mode="json") + display], unstructured: [str], warnings: [str], summarized: [...], profile: {...}|null}]}`. `unstructured` is `issues` minus the `str()` of each structured issue, as a multiset. That works because `add_issue` always appends `str(issue)` (`common.py:42-52`); a test asserts `len(unstructured) + len(structured) == len(issues)` for every level. `run_info.constraint_extractions` counts the memo's real extractions (the evidence for I10). L6's `profile` holds target resolution, versions, coverage version and list, scope, verdict, counts, every finding (rule, shape, context, outcome, reason, detail_reasons, subject name and id, location, occurrence_count, remedy, semantic_limits, display, shadowed_by), every unverified check, advisories, advisory-unverified records and check errors. Lists keep contract order; fixed key order.
- **Matrix row closing.** MULTIPLICITY-SHAPE is closed by editing `tests/fixtures/subset_profile/inventory/matrix.toml` to cite the new L6 test, then regenerating `matrix.md` with `scripts/subset_profile/render_matrix.py`. Check `tests/test_subset_matrix.py` still holds (`PUSH_DOWN_ROWS`, `:28-39`).
- **Codegen citations.** Correct or delete each per `spikes/f4-codegen-citations.md` (read at `b5663c07` from a `git archive` export). Never cite a working-tree line. Where a comment explains a check that is now known not to be generator-only, say so and point at `L6-LEGACY-CHECKS-ON-ACCEPTED-SHAPES`.

## Potential Risks

- **Sharing the model changes a level's results** (B5 false). Mitigation: I10's with/without test, and the safeguard compares L1–L5 issue lists before and after on all three trees.
- **Retyping the evaluator's raises misses one**, so a deliberate "cannot extract" turns into `L6_CHECK_ERROR`. Mitigation: the safeguard counts `L6_DESIGN_ATTR_UNEXTRACTABLE` per tree before and after (expected: fusion-tea 108 and 108; dc3 baseline 3 → 0, the String suppression), and any new `L6_CHECK_ERROR` is a pass→fail stop.
- **A future tree hits a walker exception outside the evidence vocabulary.** It becomes `L6_CHECK_ERROR`, as intended; the message names the walker and site so it can be classified.
- **Text output changes** (issue order, new metric lines, title, many new String warnings) break scripts that grep L6 output. Mitigation: grep the repo's tests and skills for the old title and strings first.
- **The holdout guard now allows `execution-target`.** Today that key makes every `register` fail closed. That relaxation is intended and is recorded in the docs change.

## Integration Strategy

L6 keeps its entry point and gains one keyword argument. Existing tests that call checks directly keep working; tests that asserted a swallowed failure is clean now see `L6_CHECK_ERROR`, the intended change. Consumers adopt by adding one line to `pyproject.toml` or running `init --execution-target`. Until they do they run as unset: same pass/fail as today unless a hidden failure is now reported (R3-2, measured by the safeguard). They will see new String WARNINGs (131 on fusion-tea, 30 on dc3 `60b44d5`), as the owner's omissions-are-warnings decision intends. A full `validate --complete` on fusion-tea should get faster, because L6 no longer extracts constraint facts a second time.

## Validation Approach

- **Table tests.** `display()` over every (category, target) cell; `LEGACY_CATEGORY` covers exactly the 17 L6 codes, and its lowered set equals `tests/fixtures/l6/native_lowered.toml`; `TOOLKIT_KEYS` rejects a key outside the set in both readers.
- **Spec criteria.** Each Success Criterion maps to a test or evidence file; the plan carries that map. Fixture projects are built in `tmp_path` with a `work/BACKLOG.md` marker, so the root is never the test runner's checkout or `$HOME`.
- **Exception sites.** One test per site in Appendix B under each target. Most force the exception by monkeypatching `SysideAdapter.elements_of_type`, `SysideAdapter.is_instance` or the wrapped helper to return fake elements or raise; those need no licence. Sites that need a real parsed model carry a label-only `syside` marker (registered in `pyproject.toml`, never a skip), following the repo's existing practice that a model-loading test fails without `SYSIDE_LICENSE_KEY` rather than skipping. The evidence lists them with `uv run pytest -m syside --collect-only -q`.
- **Advisories.** Firing and non-firing fixtures for each advisory, plus the spike's `sum(cells.?{ in c : Cell; c.ok }.mass)` and `Cell.metadata` shapes, which must give `L6_SUBSET_ADVISORY_UNVERIFIED` WARNINGs and a passing L6 under unset. The output-unchanged test for `reconstruct_expression` (D12a).
- **String.** Both spellings inside and outside `designs/`, and a String attribute outside every generator root, are `omitted` subjects with no `L6_DESIGN_ATTR_UNEXTRACTABLE` (B6).
- **Session.** Each of L2–L6 on the fixture models gives equal results with and without the session; one full run reports `constraint_extractions == 1`.
- **Golden files** for `init`: byte comparison of the whole file, with and without `--force`, including CRLF.
- **Evidence.** `run_consumers.py` writes `evidence/before-after.{md,json}`, `dc3-baseline-l6.md`, `dc3-repaired-l6.md`. `legacy-l6-audit.md` is written from Appendix A and `spikes/f4-codegen-citations.md`.
- **Repository checks.** `uv run pytest tests/`, `uv run mypy src/`, `uv run ruff check src/ tests/`; the evidence lists the `syside`-marked tests and whether the licence was present.

## Next-Stage Handoff

**Fixed:** the three-step L6 shape with the contract first; the severity table; the module split; the issue codes; D9; D3; D7 and its refusal list; D12's predicate approach; D14 sharing; D15; D16; the report schema; the safeguard in Appendix C.

**Open for the plan:** exact wording within the tested phrases; the prompt text; phase order. Recommended order: session and shared extraction first (it changes L4 and must be proven identical before anything else lands), then settings and `init`, then L6 failures and presentation, then advisories, docs and evidence.

**Risk to retire first:** B5. Land the session with the with/without test and one fusion-tea timing before building on it.

**De-risk results already in hand** (`spikes/findings.md`): the contract runs on all three trees; both advisories have firing shapes; String ids match; roots and settings are as expected; codegen citations are classified. Nothing further needs a spike.

## Appendix A: Legacy-check audit

Codegen evidence is from `spikes/f4-codegen-citations.md` (read at `b5663c07`). The native column takes effect for a row only in the change that adds that row to `legacy-l6-audit.md` and `tests/fixtures/l6/native_lowered.toml` (S3). Unset and `generated` never change.

| Code | Today | Codegen at `b5663c07` | Category | unset | generated | native |
|---|---|---|---|---|---|---|
| `V1_CALC_DEF_LOCATION` | ERROR | not a generator check (ADR-002 placement) | own applicability | ERROR | ERROR | ERROR |
| `V2_DYNAMIC_EXPRESSION` | ERROR | ADR-002 rule 3 | own applicability | ERROR | ERROR | ERROR |
| `V4_UNSUPPORTED_OPERATOR` | ERROR | ADR-002; no codegen "V4" exists | own applicability | ERROR | ERROR | ERROR |
| `V4_STATIC_FUNCTION_INVOCATION` | WARNING | partial: non-`sum` calls refused (`project.py:806-810`), `sum` accepted | kept | WARNING | WARNING | WARNING |
| `L6_MISSING_QUALIFIED_NAME` | ERROR | confirmed (weak): graph identity needs it (`elaboration/identity.py:71-76`) | generator-only | ERROR | ERROR | INFO |
| `L6_INVALID_QUALIFIED_NAME` | ERROR | not generator-only: codegen sanitizes names | kept (follow-up) | ERROR | ERROR | ERROR |
| `L6_CALC_DEF_NO_OUTPUT` | ERROR | native correctness | kept | ERROR | ERROR | ERROR |
| `L6_CALC_DEF_NO_DIRECTION` | WARNING | native correctness | kept | WARNING | WARNING | WARNING |
| `L6_INVALID_BINDING_FORMAT` | ERROR | not generator-only: bindings resolve by identity | kept (follow-up) | ERROR | ERROR | ERROR |
| `L6_DESIGN_ATTR_INCOMPLETE` | ERROR | not generator-only: codegen accepts a valueless input (`project.py:565-579`) | kept | ERROR | ERROR | ERROR |
| `L6_DESIGN_ATTR_UNEXTRACTABLE` (String) | ERROR | replaced (gate R3-1) | replaced by `omitted` | WARNING | WARNING | INFO |
| `L6_DESIGN_ATTR_UNEXTRACTABLE` (other) | ERROR | partial: codegen accepts references, `^`, `sum` | kept | ERROR | ERROR | ERROR |
| `L6_ANONYMOUS_RETURN` | ERROR | confirmed: V8 (`extraction/extractor.py:191-215`) | generator-only | ERROR | ERROR | INFO |
| `L6_BODY_ASSIGNMENT_IMPL_LOSS` | WARNING | confirmed (`extractor.py:249-264`, `expression_compiler.py:265-274`) | generator-only | WARNING | WARNING | INFO |
| `L6_CONSTRAINT_MALFORMED_NUMERICAL` | ERROR | gate R3-1 | kept | ERROR | ERROR | ERROR |
| `L6_CONSTRAINT_NON_NUMERICAL` | WARNING | decision is agentic's shared profile (`elaborate.py:296`) | kept | WARNING | WARNING | WARNING |
| `L6_CALC_DEF_NO_INSTANTIATION` | ERROR | confirmed (`elaborate.py:771-777`); a native route has no instances either | generator-only | ERROR | ERROR | INFO |
| `L6_ATTR_REDEF_EXPR_DROPPED` | WARNING | not generator-only: `hierarchy_resolver` deleted; both spellings alike (`elaborate.py:832-898`) | kept (follow-up) | WARNING | WARNING | WARNING |
| Manifest failures | fail | own applicability | own applicability | fail | fail | fail |
| Setup failures | fail | own applicability | own applicability | fail | fail | fail |
| New: contract findings | — | the contract | by outcome | WARNING | by outcome | INFO |

Native lowerings: 3 ERROR→INFO (`L6_MISSING_QUALIFIED_NAME`, `L6_ANONYMOUS_RETURN`, `L6_CALC_DEF_NO_INSTANTIATION`) and 1 WARNING→INFO (`L6_BODY_ASSIGNMENT_IMPL_LOSS`). The spec proposed up to 7 and 4; the other rows keep today's severity because the spike did not confirm a generator-only cause. "Kept (follow-up)" rows error on shapes the generator accepts and go to `L6-LEGACY-CHECKS-ON-ACCEPTED-SHAPES`, unchanged under every target.

## Appendix B: Exception sites

"Element" = `L6_CHECK_ERROR` for that element and continue; "check" = one `L6_CHECK_ERROR`, no findings from that check; "count" = metric `not computed` plus `L6_CHECK_ERROR`. Lines are at `ebb3d467`.

| Site | Today | Change |
|---|---|---|
| `level6_architecture.py:191`, `:246`, `:320`, `:418`, `:502` (enumeration) | empty list | check |
| `:230`, `:289` (`AttributeError`) | false `L6_MISSING_QUALIFIED_NAME` | element, no finding |
| `:374`, `:470`, `:572`, `:623`, `:759`, `:832`, `:907` (per element) | skip silently | element |
| `:520` (`is_instance` on owner) | skip bypassed, false finding possible | element, attribute not checked |
| `:540` (`except (ValueError, TypeError)`) | any failure reads as UNEXTRACTABLE | `Unextractable` only; other → element (D16) |
| `:723` (instantiated-set enumeration) | partial or empty set, false `NO_INSTANTIATION` | check, no findings |
| `:960` (model load) | reported | kept |
| `:973`, `:978` (counts) | 0 | count |
| `adr002.py:87`, `:177`, `:254`, `:624` (per element) | skip silently | element |
| `adr002.py:207` (`_is_invocation`) | node treated as not a call | propagate to `:254`'s element handler |
| `adr002.py:268` (`_get_calc_usage_names`) | no caller | delete |
| `adr002.py:277`, `:335` (`_is_calc_usage`, `_is_part_usage`) | False | propagate to the caller's element handler |
| `adr002.py:423` (`is_expose_binding`) | False, so not exempt: false V2/V4/UNEXTRACTABLE | propagate; caller reports element, no finding |
| New: `check_constraint_executability`, the contract, any check call | escapes L6, lost by the runner | check |
| New: advisory walkers | — | `SemanticEvidenceError` → advisory-unverified WARNING; other → check (D15) |
| `runner.py:128-137` (any level) | level not recorded, run passes | `LEVEL_CRASHED`, level failed |

Count: 17 + 9 broad sites plus 2 `AttributeError` = 28, matching the spec; `:540` is a narrow catch added to the list by S1.

## Appendix C: The before/after safeguard

`scripts/l6_subset/run_consumers.py before-after --base ebb3d467 --branch HEAD` writes `evidence/before-after.{json,md}`:

1. **Refuse a dirty branch.** `git status --porcelain -- src pyproject.toml uv.lock` must be empty, and `--branch` must equal `git rev-parse HEAD`.
2. **Export both code revisions.** `git archive` agentic-mbse at the base and the branch into `code-base/` and `code-branch/` in one `TemporaryDirectory` under `/tmp` (outside `$HOME`). Check each with `git get-tar-commit-id`.
3. **Export each consumer tree.** dc3 `808464d`, dc3 `60b44d5`, fusion-tea `f96ad312`, with Item 4's export rules: verify the tar commit id, extract with `tarfile`'s `data` filter, skip and list absolute symlinks outside `models/` (`scripts/positional_binding/run_trees.py`).
4. **Check the extraction parent is not a project root.** `find_project_root(start=<tmp parent>)` must be None.
5. **Record each tree's settings input.** Root from `find_project_root(start=<tree>/models)`, the `pyproject.toml` path, and its `[tool.agentic-mbse]` table or "absent".
6. **Run full validation six times** (3 trees × 2 code revisions), one at a time on an otherwise idle machine: the venv's Python with `PYTHONPATH=<code export>/src`, `cwd=<tree>`, `-m agentic_mbse validate --complete models`, target unset. Branch runs add `--json-report`. Each run first prints `agentic_mbse.__file__`, and the script fails unless it lies inside that run's code export. Capture stdout, stderr, exit code and wall time.
7. **Prove the root each run resolved.** Base: L2's `Positional pin list: none (looked at <root>/positional-pins.toml)`. Branch: L6's `Execution target` metric and the report. Both must agree with step 5.
8. **Per-level status and issues.** Base: parse `✅/❌ Level N:` lines and `❌ Error running Level N` (`crashed, recorded as pass`). Branch: from the report. Record the SysIDE version and the branch's `run_info.constraint_extractions` (must be 1).
9. **Compare.** For each tree and level: before → after status, exit codes, and whether L1–L5 issue lines are identical (B5). Any pass→fail (level or run) or any L1–L5 difference is flagged first in the Markdown, and the script exits 1.
10. **Time criterion.** fusion-tea's branch wall time must be at most 1.10 × its base wall time; otherwise the criterion fails and the script exits 1. Both times are recorded for every tree. (`--level=6` alone is not held to this: it already ran one extraction at the base, and the contract's other fact kinds add about 13 s plus evaluation on fusion-tea.)
11. **Expected new warnings.** List every new `L6_SUBSET_OMITTED` WARNING per tree (expected 131 on fusion-tea, 30 on `60b44d5`, 32 on `808464d`, of which 3 replace legacy errors), and the `L6_DESIGN_ATTR_UNEXTRACTABLE` count before and after (expected fusion-tea 108 → 108, dc3 baseline 3 → 0). These are expected under the owner's omissions-are-warnings decision and do not trigger the stop.
12. **Sibling repos untouched.** Record HEAD and `git status --porcelain` of dc3 and fusion-tea before and after; fail if either changed.

Steps 9 and 10 are the stop-and-show: on exit 1, implementation stops, and the orchestrator shows the owner before merge.

`run_consumers.py l6-evidence` reuses steps 1–5 and writes `dc3-baseline-l6.md` (branch, `--level=6 --execution-target=generated --json-report`, plus a run with the target unset) and `dc3-repaired-l6.md` (`60b44d5` under `generated`), reading every count from the report.

---
Next Step: record verification of M1–M3 in `design-review.md` (no re-review needed per the reviewer), then `/_my_plan`. Candidate decision records after approval: D7 (append-and-verify for owner TOML, no `tomlkit`) and D14 (one load and one constraint extraction per run), if they pass the density bar in `.project/adr/README.md`.
