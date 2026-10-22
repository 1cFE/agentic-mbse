# Design: Guidance that keeps generated results honest (EXEC-SUBSET-CONTRACT Item 5, rescoped)

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-10-22
**Git:** agentic-mbse `generated-results-guidance` at `8cb55b87`. sysml-codegen read from the worktree `/home/reid/src/subset-conformance/sysml-codegen` as checked out on 2026-10-22; its commit was not recorded, because reading git refs in that worktree needed a permission this session did not have. The re-runs in Phase R record the revision they run on.

## Overview

Give a modeller who targets generated code one command, `sysml-codegen compare`, that evaluates their model natively with SysIDE and through the generated package, and reports which outputs differ. The shipped workflow runs it and says what to do when results differ. Alongside it, fix the guidance for Risks 2 to 4 and re-run every Risk 1 case on current sysml-codegen `main`.

## Related Artifacts

- Spec: [spec.md](spec.md); spec review and its Resolutions: [spec-review.md](spec-review.md); product lens: [product-lens.md](product-lens.md)
- Epic: `.project/backlog/epic_executable-subset-contract.md`, Item 5 (rescope note at line 258)
- Decision: `.project/adr/0004-generator-is-the-only-generation-authority.md` (invariants 1 to 3); ADR 0005 (`execution-target`)
- Prior evidence: `.project/completed/20261022_retire-subset-profile/evidence/probes.md` (format reused here); `.project/completed/20261018_positional-binding-check/evidence/upstream-codegen-finding.md` and `cross-route/eval_generated.py`
- Spike written by this design, not yet run: [spike/native-path/](spike/native-path/README.md)

## The Point

[OWNER, 2026-10-22] "Mitigate actual risk, not ceremony." Since ADR 0004, a model the generator refuses is cheap: `sysml-codegen check` says so early and loudly. The risk that remains is a model that passes `check`, generates, and computes different numbers from the native model, or a package whose failed verdicts nobody reads. That failure looks like success.

[AGENT, ratified by owner at launch 2026-10-22] A modeller following the shipped workflow must catch a model that passes `check` and generates but computes different numbers than the native model. Better docs alone do not meet this. So the item must ship something that runs both routes on the modeller's own model.

[INHERITED: ADR 0004] Only the generator says what it builds. agentic-mbse keeps no copy of its rules and imports nothing from sysml-codegen. A tool that is missing or fails means "not compared", never "fine".

Every element below names the risk it reduces (spec Problem, Risks 1 to 4).

## Research Findings

**Nothing general exists yet for the native half.**
- sysml-codegen has no command that evaluates a model natively. It never calls SysIDE's `Compiler`; SysIDE is used only to parse (research report, sysml-codegen `src/`, `tests/`, `scripts/`).
- `sysml-codegen study verify` compares a package against a Python oracle (`study/verify.py:87-115`, tolerance 1e-9 relative at `:55`). The oracle is hand-written and re-implements the model's arithmetic (`tests/fixtures/study_station/studies/oracle_entry.py:33-56`). It also needs a study store, a manifest and an identity doc. It is not a native comparison.
- dc3 wrote about 1,800 lines for its comparison (`scripts/models/evaluate_*.py`, `package_comparison.py`, `tests/models/test_generated_parity.py`). About 100 lines of that are generic: load the model, walk a dotted path, call `evaluate_feature`, run the package, read its gate. About 70% of dc3's evaluator code checks binding identity (its "seam S2"), which a value comparison cannot replace.

**Native evaluation of one feature is a single SysIDE call.** `syside.Compiler().evaluate_feature(feature, scope=<owning usage>, stdlib=model.lib)` returns the value and a diagnostics report. agentic-mbse already uses it at `tests/test_validation/test_positional_binding_native_values.py:30-48`, including for an inherited feature of a part usage. dc3 does the same with a dotted-path walk (`scripts/models/evaluate_paths.py:44-51, 90-94, 142-162`). Inputs are never passed in: native evaluation uses the values written in the model. That matches the generated package's default run, whose inputs are the model's defaults (`inputs/<group>.json`).

**Running a generated package needs simkit (TEAx), which sysml-codegen does not declare.** Generated modules import `simkit` (`templates/constraint_module.py.jinja2:8-9`, `teax_module.py.jinja2:12`), but `pyproject.toml:23-28` lists only agentic-mbse, jinja2, pydantic and pyyaml. Projects that run packages provide simkit themselves (dc3's venv; fusion-tea's `TEAX_SIMKIT_PATH`). The run pattern is `ProvisionalPackageLoader`, then `execute_pipeline` or `PreparedEvaluator` (sysml-codegen `tests/execution/real_teax.py:103-152`; agentic-mbse `cross-route/eval_generated.py:156-169`).

**The generated package's outputs and verdicts.**
- Output channels are SysML occurrence paths joined by `__` (`generation/pipeline.py:255-327`). `contracts/model_contract.json` lists them, but with no SysML qualified name and no unit (`contracts/models.py:19-77`). Un-mangling `__` is lossy. Inside the generator, before emission, each module output still knows its source feature (`resolution/models.py:196`). So only sysml-codegen can map a channel back to a SysML feature without guessing.
- Each constraint records `satisfied`, `violated` or `indeterminate` and never raises (`constraint_module.py.jinja2:26-50`). The aggregator gives a headline (`report_aggregator.py.jinja2:64-73`). Catalog entries carry `usage_qualified_name` and `owner_instance_path`, so verdicts do map back to SysML.

**Facts that change the Risk 1 list.**
- Positional binding: current elaboration follows SysIDE's redefinition edges (`elaboration/elaborate.py:2181-2193`, `elaboration/occurrence.py:251-254`), which are positional. If that holds at `main`, the −7/7 split seen at `b5663c07` is gone and both routes give −7. That makes agentic-mbse's register entry `docs/patterns/semantic-hazards.md:47-58` ("The two execution routes disagree") a stale claim about generator behaviour. Only the re-run settles it.
- Conditionals: the refusal is `SI_EVIDENCE_INCOMPLETE` / `evidence_resolved_target_missing` for attribute values, bindings, predicates and calc-def results (stored case `tests/expectations/refusal_cases/cases/conditional-expression__conditional_resolved_branches__attribute_value.json:12-21`). The exception is a conditional as a calc usage's own result expression. That case generates with exit 0 and is the silent result-expression loss (RG-2).
- dc3's record shows only agreement: 126 channels, worst relative error 2.1e-15 (dc3 `work/active/WI-008_generator-idiom/audit.md:9`). There was one near-zero residual of 2.4e-7 absolute (`review.md:14`), so a purely relative tolerance with exact-zero matching would fail honest runs.

**Existing homes in agentic-mbse.**
- `project_templates/MODELING_PROCESS.md.template:32-54`, "Generated code": when to run `check`, its exit codes, and "sysml-codegen missing".
- `project_templates/MODELING_GUIDE.md.template:63-119`, "Three Structures the Code Generator Refuses". Limit 1 teaches the part-owned assert. Line 106 already warns about the default count.
- `skills/model-validation/SKILL.md:65` already says "Translation: compare generated and manual execution", but gives no means to do it.
- `tests/test_shipped_text.py:284-372` pins the three limits and the check workflow. New pins follow that pattern.

## Core Concept

The comparison belongs to the generator, because only the generator knows which SysML feature each generated output came from. sysml-codegen gets a read-only command, `sysml-codegen compare --models models/`. It builds the package into a temporary folder, as `generate` would, and runs it once with the model's own values. For each numeric or Boolean output channel, it asks SysIDE for the native value of the feature that channel came from. It then prints one line per channel (agree, differ, or not compared) and a summary, and exits with a code that keeps "differ" and "not compared" apart. The modeller supplies nothing; the outputs are the ones the generator builds.

agentic-mbse's part is to put that command into the workflow and keep the guidance honest:
- `MODELING_PROCESS.md` says when to run it, what each exit means, and what to do on a difference.
- The guide states what an assert does on each route (Risk 2).
- The pattern docs qualify conditional and function teaching with "run `check`" (Risk 3).
- Every claim the guidance makes about generator behaviour has a recorded run and an upstream row that names the guidance to update (Risk 4).

The Risk 1 re-runs use the new command, so each recorded result is a native-against-generated pair, not only a `check` exit code.

Why this is the right split: the general part (path mapping, running the package, the native call) is the same for every project and needs generator internals, so it sits in the generator. The project-specific part (what to do with a difference) is workflow judgment, so it sits in agentic-mbse's shipped process. Nothing is copied across the boundary, and agentic-mbse still imports nothing from sysml-codegen.

## Key Bets

- **B1. SysIDE's `evaluate_feature` returns the native value of a feature named only by its occurrence path, with the owning usage as scope and no extra inputs, for the shapes generated models use.** These shapes are attributes, inherited attributes, calc usage results, nested part attributes and `sum` over an exact multiplicity. Evidence so far: it works for `plant.result` (inherited) and `q.v` (`test_positional_binding_native_values.py:38-48`), and dc3 walks deeper paths the same way. Not verified for nested parts or `sum` over occurrences; [spike S1](spike/native-path/README.md) checks them. *If false → the native half needs model-specific scoping, and the design falls back to D1's option (c), where the modeller names outputs and supplies the path to each.*
- **B2. sysml-codegen can trace each emitted numeric output channel to one SysML feature and the occurrence path that owns it, before emission, without parsing channel names.** Basis: `ModuleOutput` keeps source information (`resolution/models.py:196`) and constraint entries keep `owner_instance_path`. Not verified for expanded multiplicity occurrences (`host__kids[0]`), whose native path would need an index SysIDE may not evaluate. Spike S2 (in sysml-codegen, read-only) checks it. *If false for indexed occurrences → those channels report "not compared" and the summary counts them. If false in general → the command needs a channel-to-path table the modeller writes, which is option (c) again.*
- **B3. The generate-but-wrong cases that matter show up as a numeric difference in some output the generator builds.** Example: the default count builds 2 parts instead of 3, so any `sum` over the parts differs. *If false (a loss leaves no numeric trace, like a dropped String or a dropped output) → the comparison passes over it. Those losses stay with `[SILENT-LOSSES-UNREPORTED]` and RG-2, recorded as a limit of the command, not hidden.*
- **B4. Every project that sets `execution-target = "generated"` already has simkit, because it cannot run its package otherwise.** *If false → `compare` reports "not compared: simkit unavailable" in those projects. That is safe, but the comparison would not run where it is most needed. Mitigation: the "not compared" message names the missing piece.*

## Key Decisions

**D1. The native half is a new sysml-codegen command, `compare`, option (a).** The three options the brief asks about:

| | (a) `sysml-codegen compare` | (b) agentic-mbse helper running the generator as a separate process | (c) template test plus guidance; modeller names outputs |
|---|---|---|---|
| What the modeller supplies | nothing (optionally `--output` filters) | nothing, if (b) can map channels; else a path list | a list of output paths, and the mapping to channel names |
| General for any target project | yes | only by un-mangling channel names (lossy) or by restating the generator's naming rule | yes, but each project writes and keeps its list |
| Copies generator knowledge | no; the generator uses its own mapping | yes: package layout, `pipeline.yaml`, channel naming, how to run simkit. That is a second statement of generator internals, which ADR 0004 rejected for the refusal rules | the naming rule, in each project |
| Cost (agent estimate, ±50%) | 3 to 5 days in sysml-codegen, plus spikes | 3 to 5 days, plus a standing two-repo sync | 2 days, plus each project's upkeep |
| Status after the generator changes its naming | follows automatically | breaks silently | breaks each project's list |

Chosen: (a). It is the only option where the modeller supplies nothing and no generator knowledge is copied. The orchestrator may add it, because it does not change what the generator builds (owner delegation at launch). *Rejected: (b), because it puts a copy of generator internals in agentic-mbse, the same failure ADR 0004 removed. Rejected: (c), because a per-project list goes stale, and the brief's goal is a workflow the modeller follows, not code each modeller writes. (c) stays as the fallback if B1 or B2 fails.*

**D2. Compare at the model's own values only; no input sweeps.** One default run catches a structural difference (wrong count, swapped binding, lost binding), because those differ at any input. *Rejected: sampled inputs. Native evaluation cannot take inputs without editing model text (dc3 patches source bytes, `oracle_entry.py:154-173`). Sweeps are `study verify`'s job.*

**D3. The command iterates over the generator's numeric and Boolean output channels, not over the model's features.** Strings never enter, and dropped features are not listed. *Rejected: walking the model's features and reporting the ones with no channel. That would report dropped String values, which is a reporting choice reserved by RG-2 (`[SILENT-LOSSES-UNREPORTED]` names "a `check` warning" as one owner option). The command's help and the workflow text state this limit, citing the backlog row rather than describing the loss.*

**D4. Exit codes keep "differ" and "not compared" apart.**

```
0  every compared channel agrees, and at least one channel was compared
1  at least one channel differs (the per-channel lines name them)
2  usage error (argparse; also uv's "Failed to spawn" when sysml-codegen is missing)
3  not compared: the generator refused, simkit or SysIDE (licence) is unavailable,
   the package run failed, or no channel could be compared
```

Channels that are individually not compared (no native value, or an indexed path) are listed. The summary line always reads `compared N of M channels; K not compared`. *Rejected: `check`'s convention of one code for refusal and environment failure. Here "differ" is a finding about the model and "not compared" is missing evidence, and ADR 0004 invariant 3 requires that missing evidence never reads as success.* A package run that fails because the generator left an input null (the `[CALC-USAGE-BINDING-LOST-WITH-RESULT-EXPRESSION]` shape) exits 3, and the reason line names the null input. The workflow treats exit 3 with a named null input as something to investigate, not as missing tooling.

**D5. Tolerance: numbers agree when `|g − n| ≤ rel·max(|g|, |n|) + abs`, with defaults rel = 1e-9 and abs = 0, and flags `--rel-tol` and `--abs-tol`.** Booleans and integers must match exactly, and NaN never agrees. The summary prints the worst relative and absolute deviation. *Rejected: dc3's rule of exact equality at zero with no floor, because it fails on honest near-zero residuals (dc3 `review.md:14`, 2.4e-7). Rejected: a built-in absolute floor, because the right floor depends on the quantity's scale; the modeller passes `--abs-tol` and records why.*

**D6. The command prints the generated constraint headline and lists violated or indeterminate verdicts, but does not change its exit code on them (Risk 2).** A violated verdict is the model's answer, not a route difference. Printing it means the one place a modeller reads generated values also shows the verdicts. If spike S1 shows that `evaluate_feature` on an `assert constraint` usage returns `True` or `False`, the command also compares native and generated verdicts per constraint, through `usage_qualified_name` and `owner_instance_path`, and a mismatch counts as a difference. If S1 shows it does not, verdict comparison is out and the help says so. *Rejected: re-deriving native verdicts the way `study verify` does (`verify.py:181-204`). That is a partial second evaluator.*

**D7. One home per fact.**

| Fact | Home | Pointers only from |
|---|---|---|
| When to run `compare`, its exits, what to do on a difference, "not compared" | `MODELING_PROCESS.md.template`, "Generated code" | implement-model, model-validation and toolkit-awareness skills; MODELING_GUIDE checklist |
| An assert never stops a computation on either route; check verdicts before using values (Risk 2) | `MODELING_GUIDE.md.template`, limit 1 | `docs/patterns/constraints.md` near line 158; dc3's adapter cited once, in the home |
| The default-count warning | `MODELING_GUIDE.md.template:106` (exists) | none new |
| Conditionals and library functions are native teaching; run `check` before relying on them in a generated model (Risk 3) | each teaching site, one qualifier line, because the reader meets the example there | none |
| Positional binding across routes | `docs/patterns/semantic-hazards.md` (exists; updated from the re-run) | none new |
| Which guidance to update when a generator limit lifts (Risk 4) | the sysml-codegen backlog row for that change | none in agentic-mbse |

*Rejected: a new "generated results" pattern doc. It would be a second home for facts that already have one.*

**D8. Risk 3 qualifiers name no function list.** The wording is: "Native SysIDE evaluates this. In a project that targets generated code, run `sysml-codegen check` before relying on it; the generator does not accept every expression the language allows." *Rejected: naming refused functions or "only `sum`". That restates generator rules, and it goes wrong when `[SCALAR-FUNCTION-VOCABULARY]` lands (product-lens spec-F2).*

**D9. Risk 4 is handled by upstream notes plus the comparison, not by version stamps in the guidance prose.** Each owner-held change that would lift a stated limit (`[CALCDEF-GATE-IMPLEMENTATION]` for limit 1; `[ATTRIBUTE-MULTIPLICITY-DEFAULT-COUNT]` for line 106) gets a line naming the agentic-mbse files and headings to update. The recorded runs carry the sysml-codegen revision. *Rejected: "as of sysml-codegen <rev>" in the guide text. Modellers cannot act on a revision, and it adds a second thing to keep in sync. If a limit lifts, the guide becomes stricter than the generator, which is low harm, and the upstream note catches it.*

## Architecture

```
modeller ──> MODELING_PROCESS "Generated code" ──> sysml-codegen check   (does it build?)
                                              └─> sysml-codegen compare (same numbers?)
compare:  load model (SysIDE) ─> prepare (as generate) ─> emit to temp dir
          ─> run package once with model values (simkit) ─> channels + verdicts
          ─> for each numeric/Boolean channel: source feature + occurrence path (generator-internal)
          ─> SysIDE evaluate_feature(feature, scope=owning occurrence) ─> native value
          ─> agree / differ / not compared ─> summary + exit 0/1/2/3
```

- **Boundary.** agentic-mbse ships only text and tests. It runs nothing from sysml-codegen in its own code (invariant 2). The workflow tells the modeller or agent to run the command, exactly as it does for `check`.
- **Writes.** `compare` writes nothing in the project. The package goes to a temporary folder, which is removed afterwards. `--keep <dir>` keeps it for debugging.
- **Dependencies.** SysIDE comes through agentic-mbse, which sysml-codegen already depends on. simkit is imported lazily; when it is missing, the command exits 3 and names it.
- **Reuse in sysml-codegen.** `run_check`'s load and prepare path (`cli/__init__.py:117-129`), `emit_package`, and the `ProvisionalPackageLoader` + `execute_pipeline` pattern from `tests/execution/real_teax.py`.

## Required Invariants

1. `compare` never exits 0 unless at least one channel was compared and none differed (ADR 0004 invariant 3).
2. `compare` changes nothing the generator builds, and writes nothing outside a temporary folder unless `--keep` is given (RG-1; owner delegation).
3. No agentic-mbse module imports sysml-codegen or simkit (ADR 0004 invariant 2). No test checks this today (no test under `tests/` mentions `sysml_codegen`); this item does not add one, because it adds no agentic-mbse code.
4. agentic-mbse guidance names no list of accepted or refused functions or expressions. Its claims about current generator behaviour are limited to the three limits, the default count, the assert-verdict behaviour and the positional result, each with a recorded run and an upstream row (spec criterion 5).
5. No guidance line about dropped String values or dropped calc-usage result expressions is added while RG-2 is open (spec Known Requirements).

## Component Overview

**sysml-codegen (branch, orchestrator-delegated):**
- `cli/__init__.py` plus a new `cli/compare.py`: the `compare` subcommand, which takes `--models`, the tolerance flags, `--keep` and an optional repeated `--output <channel>` filter.
- A small comparison module (location chosen by sysml-codegen's plan) holding the channel-to-feature trace (B2), the native call (B1), the tolerance rule (D5) and the report. It has tests in sysml-codegen: agree, differ (the default-count reproducer), simkit missing (exit 3), refused model (exit 3), and a null-input run (exit 3 with the input named).
- Backlog rows updated (Phase U below).

**agentic-mbse:**
- `project_templates/MODELING_PROCESS.md.template`, "Generated code": a "Compare results" paragraph. Run `compare` once the model generates, at the end of each phase where `check` exits 0, and before any claim about generated results. Exit meanings follow D4.
- On a difference: the native model is the model's meaning. Keep the model as written, reduce the case to a minimal reproducer, record it, and file it upstream. Do not rewrite the model to match the package unless the native result is shown to be wrong. "Not compared" is reported, never treated as fine.
- `project_templates/MODELING_GUIDE.md.template`: limit 1 gains the Risk 2 paragraph. The validation checklist gains a `compare` line.
- `skills/implement-model`, `skills/model-validation` (replace the bare "Translation" line at `:65` with a pointer), `skills/toolkit-awareness`: one line each, pointing at the home.
- Risk 3 qualifier lines (D8): `docs/patterns/conditionals.md` (once, under Quick Reference, covering all its examples), `docs/patterns/syntax-reference.md` near `:283`, `skills/sysml-conventions/SKILL.md:194`, `MODELING_GUIDE.md.template:190`, `docs/patterns/README.md:18` (table text), `agents/kerml-expert.md` near `:26` and `:87`, `agents/sysmlv2-validator.md` near `:296`.
- `docs/patterns/semantic-hazards.md`: the "two execution routes" section rewritten from the positional re-run result.
- `tests/test_shipped_text.py`: pins for the compare paragraph (exits, "not compared"), the Risk 2 statement, and the Risk 3 qualifier at each site. Also a test that no shipped guidance names `min`, `max`, `product` or `size` as generator-accepted.

## Non-Goals

- Agree-but-wrong errors (equal-value misbindings, a shared formula error). The comparison cannot see them. Validate level 2 and native checks own them (spec Non-Goals).
- Input sweeps or study-style sampling (D2); `study verify` covers that.
- Reporting dropped String values or dropped features (D3, RG-2).
- A shipped template test in target projects. It is out because `compare` plus the workflow step meets criterion 1 with less code per project. If B1 or B2 fails, it comes back as option (c).
- Generator fixes; deciding which positional reading the generator should follow (RG-1).

## Implementation Notes

**Spikes first (each a few hours).**
- **S1, native paths (agentic-mbse, written):** `uv run pytest .project/active/generated-results-guidance/spike/native-path/test_native_path.py -s -q`. The expected values are in its README.
- **S2, channel trace (sysml-codegen, read-only):** generate S1's model and the default-count reproducer. For each emitted channel, confirm the pre-emission data names a SysML feature and an occurrence path, and that `evaluate_feature` on that path gives the same number. Include one indexed occurrence. If S1 or S2 fails, stop and bring the fallback (option (c)) to the owner before building.

**Phase R: Risk 1 re-runs on current sysml-codegen `main`.** Record the revision. Run each probe with `check`, then `generate`, then `compare` (or, before `compare` exists, a script on the `eval_generated.py` pattern). Record the results in `evidence/risk1-reruns.md` in the `probes.md` table format (case, model, exit, generated value, native value, verdict), with each probe in `evidence/probes/<case>/model.sysml` and its outputs beside it.

| Case | Probe | Guidance outcome |
|---|---|---|
| Default count (`[ATTRIBUTE-MULTIPLICITY-DEFAULT-COUNT]`) | backlog reproducer, with a `sum` output | already warned (`:106`); confirm and pin |
| String dropped (`[SILENT-LOSSES-UNREPORTED]`) | String attribute beside a Real | file and flag only (RG-2) |
| Calc-usage result expression and lost binding | `calc m : Twice { in v = x; v * 3.0 }` | file and flag only (RG-2 / RG1-3); record the exit-3 null input |
| Positional | `tests/fixtures/positional_binding/native_values/gen_reversed/`, `gen_byname/` | update `semantic-hazards.md` to the observed result; mark the draft finding superseded or filed |
| Calc def simple-name collision (`[REGISTRY-CALC-DEF-SIMPLE-NAME-DEDUP]`) | two packages, each `calc def Area`, both used | warn only if confirmed, as a one-line "give calc defs distinct names" in the guide's naming section |
| Unresolved conditional branch, indexed reference, unsupported callable outside a predicate | one probe each | if they generate and differ, warn at the Risk 3 site; if refused, record the refusal |
| Conditional refusal (Risk 3 evidence) | `attribute diff : Real = if x > y? x - y else y - x;` | backs the qualifier |
| `min` refusal (Risk 3 evidence) | `attribute m : Real = min(a, b);` | backs the qualifier |
| Assert verdict (Risk 2 evidence) | limit 1's correct example with a violated value | `compare` (or the run script) shows outputs computed while the headline is `violation` |

**Phase U: upstream rows (sysml-codegen branch, orchestrator-delegated).** For each confirmed case, give the row a minimal inline reproducer and the revision. For each unconfirmed case, record "not reproduced at <rev>" with the probe. Fix the stale `retire-subset-profile` path in `[SILENT-LOSSES-UNREPORTED]` (review L4-1). Add the agentic-mbse guidance pointers to `[CALCDEF-GATE-IMPLEMENTATION]` and `[ATTRIBUTE-MULTIPLICITY-DEFAULT-COUNT]` (D9). Add a row for `compare` itself if sysml-codegen's process wants one. Update `[POSITIONAL-FORMAL-REDEFINITION]` with the observed result; which reading is right stays with the codegen owner.

**Merge order.** The agentic-mbse text names a command that exists only after sysml-codegen merges. The two merge together, sysml-codegen first (RG-3, owner).

**Observation, out of scope.** The conditional refusal comes from agentic-mbse code that sysml-codegen calls (`agentic_mbse/sysml/reference_use.py`, relayed at sysml-codegen `orchestration/elaborated_pipeline.py:452-479`). That is evidence extraction, not a rules copy. Not pursued here.

## Potential Risks

- **S1 or S2 fails.** Fall back to option (c) and ask the owner first; the cost roughly doubles per project.
- **The run needs inputs the model leaves unset.** The package cannot run, so `compare` exits 3 and names the input. Native evaluation of the same model would fail as well, so this is not a false pass.
- **A modeller loosens the tolerance until differences disappear.** The workflow says to record any `--abs-tol` and why. The summary prints the worst deviation so a reviewer sees it.
- **Large models are slow.** SysIDE evaluates per channel. Not measured on dc3 (about 126 channels). If it is slow, `--output` filters the run.

## Integration Strategy

The modeller already runs `check` at the same points; `compare` is the next line in the same section. Nothing changes for projects targeting `native`. `execution-target` (ADR 0005) is the switch the workflow reads, as it is today.

## Validation Approach

- sysml-codegen tests for every exit code, including a differ case built from a real generate-but-wrong reproducer.
- agentic-mbse shipped-text tests (protection, not risk reduction), with the suite at its base failures.
- Evidence: `evidence/risk1-reruns.md`, where every guidance claim about generator behaviour links to a row.
- Falsifier for criterion 1: in an environment without simkit, and in one with the generator refusing the model, `compare` exits 3 and prints "not compared".

## Next-Stage Handoff

- **Fixed:** option (a); exit codes (D4); one home per fact (D7); no function lists (D8); RG-2 cases filed and flagged only.
- **Open:** verdict comparison depends on S1 (D6); the module location inside sysml-codegen; the `--output` filter's name.
- **De-risk first:** S1, then S2, then Phase R. The positional result decides whether `semantic-hazards.md` changes.
- **Proposed, not filed (RG-3):** a product promise, "for a model that generates, `sysml-codegen compare` reports whether native and generated results match" (product-lens spec-F5, at close). No ADR is needed. D1 follows ADR 0004 rather than changing it.

---
Next Step: After approval → `/_my_plan`
