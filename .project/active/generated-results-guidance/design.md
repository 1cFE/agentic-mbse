# Design: Guidance that keeps generated results honest (EXEC-SUBSET-CONTRACT Item 5, rescoped)

**Status:** Draft, revised 2026-10-22 after the spike ([spike/RESULTS.md](spike/RESULTS.md))
**Owner:** Reid Westwood
**Created:** 2026-10-22
**Git:** agentic-mbse `generated-results-guidance`; the design was first drafted at `8cb55b87` and the spike ran at `d5a26bdc`. sysml-codegen worktree `/home/reid/src/subset-conformance/sysml-codegen` at `53d3cb1b`, whose `src/` is identical to `origin/main` `6190f996`. TEAx simkit at `8d877460`. SysIDE 0.8.4.

## Overview

Give a modeller who targets generated code one command, `sysml-codegen compare`. It evaluates their model natively with SysIDE and through the generated package, checks that the generator built the part counts the model asks for, and reports which outputs differ and which could not be compared. The shipped workflow runs it and says what to do with each answer. Alongside it, fix the guidance for Risks 2 to 4 and re-run every Risk 1 case on current sysml-codegen `main`.

## Related Artifacts

- Spec: [spec.md](spec.md); spec review and its Resolutions: [spec-review.md](spec-review.md); product lens: [product-lens.md](product-lens.md)
- Spike: [spike/RESULTS.md](spike/RESULTS.md) (S1 native paths, S2 channel trace and counts, S3 positional binding), with probes in `spike/native-path/` and `spike/channel-trace/`
- Epic: `.project/backlog/epic_executable-subset-contract.md`, Item 5 (rescope note at line 258)
- Decision: `.project/adr/0004-generator-is-the-only-generation-authority.md` (invariants 1 to 3); ADR 0005 (`execution-target`)
- Prior evidence: `.project/completed/20261022_retire-subset-profile/evidence/probes.md` (format reused here); `.project/completed/20261018_positional-binding-check/evidence/upstream-codegen-finding.md` and `cross-route/eval_generated.py`

## The Point

[OWNER, 2026-10-22] "Mitigate actual risk, not ceremony." Since ADR 0004, a model the generator refuses is cheap: `sysml-codegen check` says so early and loudly. The risk that remains is a model that passes `check`, generates, and computes different numbers from the native model, or a package whose failed verdicts nobody reads. That failure looks like success.

[AGENT, ratified by owner at launch 2026-10-22] A modeller following the shipped workflow must catch a model that passes `check` and generates but computes different numbers than the native model. Better docs alone do not meet this. So the item must ship something that runs both routes on the modeller's own model.

[INHERITED: ADR 0004] Only the generator says what it builds. agentic-mbse keeps no copy of its rules and imports nothing from sysml-codegen. A tool that is missing or fails means "not compared", never "fine".

Every element below names the risk it reduces (spec Problem, Risks 1 to 4).

## Research Findings

**Nothing general exists yet for the native half.**
- sysml-codegen never calls SysIDE's evaluator. `sysml-codegen study verify` compares a package against a hand-written Python oracle (`study/verify.py:87-115`), not against SysIDE.
- dc3 wrote about 1,800 lines for its comparison. About 100 lines of it are generic. About 70% of its evaluator code checks which feature each input is bound to, which a value comparison cannot replace.

**What native evaluation by path can and cannot do (spike S1).**
- `Compiler().evaluate_feature(feature, scope=<owning usage>)` gives the right value for plain, inherited, calc-result, nested-part, computed and Boolean attributes. Inputs are the values written in the model, which matches the package's default run.
- It is silently wrong for anything that ranges over a part multiplicity. SysIDE does not expand `cells : Cell[3]` into three parts. `sum(cells.capacity)` returns one cell's value (2.5, not 7.5), and `size(cells)` returns 1, with no diagnostic. This holds for a literal count and for an attribute count.
- It cannot give a value for one index (`cells[1]`). It returns the per-definition value, so agreement on an indexed channel only shows every occurrence matches the definition.
- Constraint verdicts are available with one extra step. Evaluating the usage's own result expression, or else its definition's, with the usage as scope gives `True` or `False`. The package's per-constraint `actual_value` matched for both constraints probed.
- SysIDE evaluates a multiplicity's bound in the owning usage's scope. For the default-count reproducer it gives 3 while the generator built 2 occurrences (`probe_count.py`).

**Where the channel trace lives (spike S2).** `ModuleOutput` (`resolution/models.py:179-196`) carries no source feature. The trace is one layer earlier, in the instance graph. The projection's private `_Projection.output_channels` (`elaboration/project.py:403-413`) maps each output port to its channel. Each port names its calc node and output declaration. The node's scope is an occurrence path with a containment declaration and an index per step. Every declaration id is the SysIDE element id (`elaboration/identity.py:70-87`). So the native feature is found by id, with no name parsing, and every channel in the probes traced. Aliases are not separate channels; the run manifest maps them onto traced channels.

**Positional binding (spike S3).** At sysml-codegen `main` code (`6190f996`), `gen_reversed` (`in b = small; in a = big;`) passes `check`, generates, wires `a ← big`, `b ← small`, and gives 7.0. Native SysIDE gives −7.0. So the generator binds unprefixed calc-usage inputs by name, as it did at `b5663c07`. The first draft of this design read `elaboration/elaborate.py:2181-2193` as positional; that reading was wrong. `docs/patterns/semantic-hazards.md:47-58` stays correct. The observed wiring still conflicts with `[POSITIONAL-FORMAL-REDEFINITION]`'s text ("current elaboration follows parser redefinition identity"). This item records the result for the codegen owner and does not rule on which reading is intended (RG-1).

**Running a generated package needs simkit, which sysml-codegen does not declare.** Generated modules import `simkit` (`templates/constraint_module.py.jinja2:8-9`, `teax_module.py.jinja2:12`). sysml-codegen's `pyproject.toml:23-28` does not list it, and sysml-codegen's own environment cannot import it (no `pandas`). Projects provide it themselves. dc3 declares `teax-simkit` as an editable path dependency on a TEAx checkout (`dc3/pyproject.toml:9,27`). sysml-codegen's tests find it through `TEAX_SIMKIT_PATH` (`tests/helpers/teax_discovery.py`), and fusion-tea sets that variable.

**Generated outputs and verdicts.** Channels are occurrence paths joined by `__`. `contracts/model_contract.json` lists them with no SysML name and no unit. Constraints record `satisfied`, `violated` or `indeterminate` and never raise (`constraint_module.py.jinja2:26-50`). Catalog entries carry `usage_qualified_name` and `owner_instance_path` (`resolution/models.py:351-381`).

**Existing homes in agentic-mbse.**
- `project_templates/MODELING_PROCESS.md.template:32-54`, "Generated code": when to run `check`, its exits, "sysml-codegen missing".
- `project_templates/MODELING_GUIDE.md.template:63-119`, the three limits. Line 106 warns about the default count. Line 216 warns about input order; validate level 2 reports it as `L2_POSITIONAL_BINDING`.
- `skills/model-validation/SKILL.md:65` says "compare generated and manual execution", with no means to do it.
- `tests/test_shipped_text.py:284-372` pins the limits and the check workflow.

## Core Concept

The comparison belongs to the generator, because only the generator knows which SysML feature each output came from and how many occurrences it built. sysml-codegen gets a read-only command, `sysml-codegen compare --models models/`. It does three checks on one build:

1. **Counts.** For every part usage with a multiplicity, SysIDE's bound for that usage is checked against the number of occurrences the generator built.
2. **Values.** Each numeric or Boolean output channel is checked against SysIDE's value for the feature it came from, unless SysIDE cannot give a trustworthy value. That happens when the value depends on something ranging over a part multiplicity, or is a per-index value. Those channels are reported "not compared", with the reason.
3. **Verdicts.** Each generated constraint verdict is checked against SysIDE's evaluation of that constraint, under the same "not compared" rule.

The command prints one line per difference and per not-compared item. It ends with a count of compared and not-compared items, and exits with a code that keeps "differ" and "not compared" apart. The modeller supplies nothing.

The value check catches wrong wiring, such as the by-name binding in `gen_reversed`. The count check catches the wrong part count (the default count), which the value check cannot see because native `sum` is wrong too. The not-compared count keeps the command honest: it never claims to have compared more than it did.

agentic-mbse's part is to put the command into the workflow and keep the guidance honest:
- `MODELING_PROCESS.md` says when to run `compare`, what each exit means, and what to do on a difference.
- The guide states what an assert does on each route (Risk 2).
- The pattern docs qualify conditional and function teaching with "run `check`" (Risk 3).
- Every guidance claim about generator behaviour has a recorded run and an upstream row that names the guidance to update (Risk 4).

## Key Bets

- **B1. SysIDE gives the right native value, by element id and owning scope, for every channel that does not depend on a part multiplicity.** S1 and S2 confirmed this for plain, inherited, calc-result, nested-part, computed and Boolean attributes. Not checked: quantities with units, Integer channels, models split across files, and calc usages nested more than one level inside indexed occurrences. *If false for one of those → the value check reports false differences there; the plan's tests cover each before release (Validation Approach).*
- **B2. The generator can tell, from its own graph, whether a channel's value depends on a part usage with more than one occurrence.** This is a reachability question over the computation graph. It asks whether any upstream node reads a slot whose occurrence set has more than one member. Not probed (RESULTS.md, Open Questions). *If false → the command cannot separate trustworthy native values from wrong ones. It would report false differences on correct packages (S2: the literal `Cell[3]` model gives generated 9.6, native 3.2), and the value check would be unusable on any model with a part multiplicity.*
- **B3. Part counts are fully described by the native bound of each part usage, evaluated in its owning scope.** Generated multiplicities are exact (limit 2), so the bound is the count. S2 confirmed one case: a redefined count of 3, against 2 built. *If false (a count that differs per index, or a bound SysIDE cannot evaluate) → the count check reports "not compared" for that usage. It must not report agreement.*
- **B4. Generate-but-wrong cases that matter show up as a value, count or verdict difference.** *If false (a loss leaves no trace in what the generator builds, like a dropped String or a dropped output) → `compare` passes over it. Those losses stay with `[SILENT-LOSSES-UNREPORTED]` and RG-2, and the command's help names that limit.*

## Key Decisions

**D1. The comparison is a new sysml-codegen command, `compare` (option (a)).**

| | (a) `sysml-codegen compare` | (b) agentic-mbse helper running the generator as a separate process | (c) template test plus guidance; modeller names outputs |
|---|---|---|---|
| What the modeller supplies | nothing | a path list, since channel names cannot be un-mangled safely | a list of output paths and their channel names |
| Can tell which values SysIDE gets wrong (B2) and check counts | yes; it holds the graph | no; it sees only the emitted package | no |
| Copies generator knowledge | no | yes: package layout, channel naming, how to run simkit | the naming rule, in each project |
| Cost (agent estimate, ±50%) | 4 to 6 days in sysml-codegen | 3 to 5 days, plus a standing two-repo sync | 2 days, plus each project's upkeep |

*Rejected: (b), because it puts a copy of generator internals in agentic-mbse, which is what ADR 0004 removed. It also cannot see the multiplicity dependence that S1 showed is needed to avoid false differences. Rejected: (c), for the same blindness, and because a per-project list goes stale.* The orchestrator may add (a), because it does not change what the generator builds (owner delegation at launch).

**D2. The trace comes from a new public, read-only accessor in sysml-codegen's elaboration layer, not from new fields on `ModuleOutput`.** For a prepared model the accessor returns:
- for each output channel: the calc node, the output declaration's element id, and the occurrence chain (containment declaration id and index per step);
- whether the channel's value depends on a multi-occurrence slot (B2);
- for each part usage with a multiplicity: the declaration id and the number of occurrences built under each owning occurrence.

It wraps what `_Projection.output_channels` already computes (`elaboration/project.py:403-413`). *Rejected: adding source ids to `ModuleOutput`. That record feeds emission and the package contract, so a new field risks changing package bytes or fingerprints, which RG-1 forbids. The accessor is checked by generating the sysml-codegen test corpus before and after the change and comparing the output byte for byte.*

**D3. Compare at the model's own values only; no input sweeps (Risk 1).** One default run catches wrong wiring and wrong counts, because those differ at any input. *Rejected: sampled inputs. Native evaluation cannot take inputs without editing model text, and sweeps belong to `study verify`.*

**D4. Value checks cover the generator's numeric and Boolean channels only (Risk 1, RG-2).** Strings never enter, and dropped features are not listed. *Rejected: walking the model's features and reporting those with no channel. That would report dropped String values, a reporting choice reserved by RG-2.*

**D5. "Not compared" is reported per item, with its reason, and counted (ADR 0004 invariant 3).** The reasons are:

```
depends on a part multiplicity   native SysIDE does not expand Cell[n]
per-index value                  native SysIDE has no per-index value
no native value                  evaluate_feature returned no value or a diagnostic
```

The summary always reads `values: compared N of M; counts: compared P of Q; verdicts: compared R of S`. *Rejected: dropping not-compared channels from the report. A comparison that silently compares fewer outputs than it lists is a false pass (orchestrator direction, 2026-10-22).*

**D6. Exit codes.**

```
0  nothing differs, and at least one value, count or verdict was compared
1  at least one value, count or verdict differs (listed)
2  usage error (argparse; also uv's "Failed to spawn" when sysml-codegen is missing)
3  not compared at all: refused model, simkit or SysIDE unavailable, package run failed,
   or nothing comparable
```

Exit 0 with some items not compared is allowed, because the counts are printed on every run. The workflow says to record them. A package run that fails because the generator left an input null (the `[CALC-USAGE-BINDING-LOST-WITH-RESULT-EXPRESSION]` shape) exits 3, and the reason line names the input. *Rejected: `check`'s convention of one code for refusal and environment failure. "Differ" is a finding about the model; "not compared" is missing evidence.*

**D7. The count check is in (Risk 1, the default count).** It is small and general. It needs one SysIDE call per part usage with a multiplicity (the bound in the owning scope, `probe_count.py`) and the occurrence counts the instance graph already holds (D2). It is the only way the comparison catches the confirmed `[ATTRIBUTE-MULTIPLICITY-DEFAULT-COUNT]` case. The value check cannot, because native `sum` is wrong on both the buggy and the correct package. *Rejected: relying on the guide's warning at `MODELING_GUIDE.md.template:106` alone. The warning stays, but a modeller who missed it gets no signal.*

**D8. Tolerance: numbers agree when `|g − n| ≤ rel·max(|g|, |n|) + abs`, with defaults rel = 1e-9 and abs = 0, and flags `--rel-tol` and `--abs-tol`.** Booleans and integers must match exactly, and NaN never agrees. The summary prints the worst deviation. *Rejected: dc3's exact equality at zero, which fails honest near-zero residuals (dc3 `review.md:14`, 2.4e-7).*

**D9. Verdict comparison is in (Risk 2 and Risk 1).** The native verdict is the usage's own result expression, or else its definition's, evaluated with the usage as scope (S1). The two sides are joined through the catalog's `usage_qualified_name` and `owner_instance_path`. Constraints inside indexed occurrences, or reading a multiplicity, are not compared (D5). The command also prints the generated headline and lists violated verdicts. A violated verdict that agrees with native is the model's answer, not a difference, so it does not change the exit code. *Rejected: re-deriving verdicts from `predicate_ir` the way `study verify` does, because that is a partial second evaluator.* The join was only checked by eye for two constraints (RESULTS.md, Open Questions), so the plan tests it.

**D10. simkit: `compare` imports it from the environment it runs in.** Before building anything, it checks the import and stops with exit 3 if it fails: `not compared: cannot import simkit (TEAx teax-simkit); <ImportError text>`. The workflow text says how a target project provides it: declare `teax-simkit` as a dependency of the project (dc3 uses an editable path dependency on a TEAx checkout) and run `uv run sysml-codegen compare` from the project's environment. The plan checks how sysml-codegen's study layer finds simkit, and whether it honours `TEAX_SIMKIT_PATH`. `compare` follows the same rule, so a project has one way to provide simkit. *Rejected: making simkit a sysml-codegen dependency. It changes sysml-codegen's install for every user, and TEAx is not published as a package.*

**D11. One home per fact.**

| Fact | Home | Pointers only from |
|---|---|---|
| When to run `compare`, its exits, not-compared counts, what to do on a difference, how to provide simkit | `MODELING_PROCESS.md.template`, "Generated code" | implement-model, model-validation, toolkit-awareness skills; the guide's checklist |
| An assert never stops a computation on either route; check verdicts before using values (Risk 2) | `MODELING_GUIDE.md.template`, limit 1 | `docs/patterns/constraints.md` near line 158; dc3's adapter cited once, in the home |
| The default-count warning | `MODELING_GUIDE.md.template:106` (exists) | none new |
| Input order across routes | `docs/patterns/semantic-hazards.md` (exists; "Verified with" gains the `6190f996` result) | none new |
| Conditionals and library functions are native teaching; run `check` before relying on them (Risk 3) | each teaching site, one qualifier line | none |
| Which guidance to update when a generator limit lifts (Risk 4) | the sysml-codegen backlog row for that change | none |

**D12. Risk 3 qualifiers name no function list.** The wording is: "Native SysIDE evaluates this. In a project that targets generated code, run `sysml-codegen check` before relying on it; the generator does not accept every expression the language allows." *Rejected: naming refused functions, which goes wrong when `[SCALAR-FUNCTION-VOCABULARY]` lands (product-lens spec-F2).*

**D13. Risk 4 is handled by upstream notes plus `compare`, not by version stamps in the guidance prose.** Each owner-held change that would lift a stated limit (`[CALCDEF-GATE-IMPLEMENTATION]` for limit 1; `[ATTRIBUTE-MULTIPLICITY-DEFAULT-COUNT]` for line 106) gets a line naming the agentic-mbse files and headings to update. Recorded runs carry the revision. *Rejected: "as of <rev>" in guide prose, because modellers cannot act on it.*

## Architecture

```
modeller ─> MODELING_PROCESS "Generated code" ─> sysml-codegen check    (does it build?)
                                             └─> sysml-codegen compare  (same results?)
compare: import simkit (else exit 3) ─> load + prepare (as generate) ─> trace accessor (D2)
         ─> emit to temp dir ─> run package once (simkit) ─> channels + verdicts
         ─> SysIDE: bound per part usage | value per channel | verdict per constraint
         ─> differ / agree / not compared (reason) ─> counts ─> exit 0/1/2/3
```

- **Boundary.** agentic-mbse ships text and tests only. The workflow tells the modeller or agent to run the command, as it does for `check` (invariant 2).
- **Writes.** Nothing in the project. The package goes to a temporary folder; `--keep <dir>` keeps it for debugging.
- **Reuse in sysml-codegen.** `run_check`'s load and prepare path (`cli/__init__.py:117-129`), `emit_package`, the `ProvisionalPackageLoader` + `execute_pipeline` pattern (`tests/execution/real_teax.py:103-152`), and the spike's `probe_channels.py` and `probe_count.py` as working references.

## Required Invariants

1. `compare` never exits 0 unless something was compared and nothing differed. Every run prints compared and not-compared counts for values, counts and verdicts (ADR 0004 invariant 3).
2. `compare` and the trace accessor change nothing the generator builds. Generating the sysml-codegen corpus is byte-identical before and after (RG-1).
3. A channel whose native value is untrustworthy (D5) is never reported as agreeing or differing.
4. No agentic-mbse module imports sysml-codegen or simkit (ADR 0004 invariant 2). This item adds no agentic-mbse code.
5. agentic-mbse guidance names no list of accepted or refused functions. Its claims about generator behaviour are limited to the three limits, the default count, the assert-verdict behaviour and input order, each with a recorded run and an upstream row (spec criterion 5).
6. No guidance line about dropped String values or dropped calc-usage result expressions is added while RG-2 is open.

## Component Overview

**sysml-codegen (branch, orchestrator-delegated):**
- The trace accessor in `elaboration/` (D2), with tests on the spike models (`spike/channel-trace/models/`).
- `cli/compare.py` and a comparison module. It holds the count, value and verdict checks, the tolerance rule and the report, with these tests:
  - `gen_reversed` exits 1, with value `diff.r` native −7, generated 7;
  - the default-count reproducer exits 1 on its count, with its `total` not compared because it depends on a part multiplicity;
  - the literal `Cell[3]` model exits 0, with `total` not compared;
  - a violated assert exits 0 and the headline is printed;
  - simkit not importable, a refused model, and a null input each exit 3.
- Backlog rows (Phase U).

**agentic-mbse:**
- `MODELING_PROCESS.md.template`, "Generated code": a "Compare results" paragraph.
  - When: once the model generates, at the end of each phase where `check` exits 0, and before any claim about generated results.
  - Exits per D6, and record the not-compared counts.
  - On a difference: the native model is the model's meaning. Reduce the case to a minimal reproducer, record it and file it upstream. Do not rewrite the model to match the package unless the native result is shown wrong.
  - How to provide simkit (D10). "Not compared" is reported, never treated as fine.
- `MODELING_GUIDE.md.template`: the Risk 2 paragraph in limit 1, and a `compare` line in the checklist.
- `skills/implement-model`, `skills/model-validation` (the "Translation" line at `:65` becomes a pointer), `skills/toolkit-awareness`: one pointer line each.
- Risk 3 qualifiers (D12) at:
  - `docs/patterns/conditionals.md` (once, under Quick Reference) and `docs/patterns/syntax-reference.md` near `:283`;
  - `skills/sysml-conventions/SKILL.md:194` and `MODELING_GUIDE.md.template:190`;
  - `docs/patterns/README.md:18`;
  - `agents/kerml-expert.md` near `:26` and `:87`, and `agents/sysmlv2-validator.md` near `:296`.
- `docs/patterns/semantic-hazards.md`: add the `6190f996` result to "Verified with" and the routes table; the draft-finding line changes to say where it was filed.
- `tests/test_shipped_text.py`: pins for the compare paragraph (exits, not-compared counts, simkit), the Risk 2 statement, the Risk 3 qualifiers, and a check that no shipped guidance names `min`, `max`, `product` or `size` as generator-accepted.

## Non-Goals

- Agree-but-wrong errors (equal-value misbindings, a shared formula error). Validate level 2 and native checks own them.
- Native values over part multiplicities, or per index. SysIDE cannot give them (S1); `compare` reports them as not compared.
- Input sweeps (D3); reporting dropped Strings or features (D4, RG-2).
- A template test in target projects. `compare` plus the workflow step meets criterion 1 with no per-project code.
- Generator fixes, and ruling on which positional reading the generator should follow (RG-1).

## Implementation Notes

**First, de-risk B2 (a few hours, sysml-codegen, read-only):** on the spike models, compute "depends on a multi-occurrence slot" from the graph. Confirm it marks `pack.total` in both default-count models and `host.pack.total` in `s1_gen`, and marks nothing else. If it cannot be computed reliably, stop and bring it to the owner. The fallback is to mark every channel downstream of any multiplicity as not compared, which is coarser but still honest.

**Phase R: Risk 1 re-runs on sysml-codegen `main`.** Record the revision. Run each probe with `check`, `generate` and `compare` (before `compare` exists, use the spike's `probe_channels.py`). Record the results in `evidence/risk1-reruns.md` in the `probes.md` format, with each model in `evidence/probes/<case>/`.

| Case | Status going in | Guidance outcome |
|---|---|---|
| Default count | confirmed (S2: 2 built for 3) | already warned (`:106`); pin; caught by D7 |
| Positional (`gen_reversed`, `gen_byname`) | confirmed at `6190f996` (S3: native −7, generated 7) | already warned (`:216`, `L2_POSITIONAL_BINDING`, `semantic-hazards.md`); update "Verified with"; caught by the value check |
| String dropped | confirmed earlier | file and flag only (RG-2) |
| Calc-usage result expression and lost binding | confirmed earlier | file and flag only (RG-2 / RG1-3); record the exit-3 null input |
| Calc def simple-name collision | unconfirmed | warn (distinct calc def names) only if confirmed |
| Unresolved conditional branch, indexed reference, unsupported callable outside a predicate | not re-checked | if they generate and differ, warn at the Risk 3 site; if refused, record the refusal |
| Conditional and `min` refusals (Risk 3 evidence) | stored case only / backlog | a `check` run each backs the qualifier |
| Assert verdict (Risk 2 evidence) | S2 saw `violated` with outputs computed (`s1_gen`) | record as the backing run |

**Phase U: upstream rows (sysml-codegen branch, orchestrator-delegated).**
- Confirmed cases get a minimal inline reproducer and the revision. Unconfirmed cases get "not reproduced at <rev>" with the probe.
- `[POSITIONAL-FORMAL-REDEFINITION]`: record the observed result (at `6190f996`, unprefixed calc-usage inputs are wired by name; native SysIDE binds by position; `gen_reversed` gives generated 7, native −7). Note that this differs from the row's "follows parser redefinition identity". File agentic-mbse's draft finding there and mark the draft filed. No ruling on which reading is intended.
- Fix the stale `retire-subset-profile` path in `[SILENT-LOSSES-UNREPORTED]` (review L4-1).
- Add guidance pointers to `[CALCDEF-GATE-IMPLEMENTATION]` and `[ATTRIBUTE-MULTIPLICITY-DEFAULT-COUNT]` (D13).
- Add a row for `compare` if sysml-codegen's process wants one.

**Merge order.** The agentic-mbse text names a command that exists only after sysml-codegen merges. sysml-codegen merges first (RG-3, owner).

## Potential Risks

- **B2 cannot be computed reliably.** Use the coarse fallback (above); more channels show as not compared, and the count says so.
- **Not checked by the spike** (RESULTS.md, Open Questions). Each needs a test before release:
  - quantities with units;
  - Integer and Boolean output channels (none emitted in the probes);
  - calc usages nested more than one level inside indexed occurrences;
  - models split across several files;
  - whether a model can give different values per index. If it can, per-index channels stay not compared, which D5 already does.
  - the verdict join in code (D9).
- **Many models have part multiplicities**, so many value channels may be not compared. That is honest but weakens the value check. The count check still runs. The workflow tells the modeller to record the counts, and a reviewer sees them.
- **simkit is missing in a target project.** `compare` exits 3 and says how to provide it. Projects without TEAx get no comparison, and the workflow reports that as not compared.
- **A modeller loosens the tolerance until differences disappear.** The workflow says to record any `--abs-tol` and why; the summary prints the worst deviation.

## Integration Strategy

The modeller already runs `check` at the same points; `compare` is the next line in the same section. Nothing changes for projects targeting `native`. `execution-target` (ADR 0005) is the switch the workflow reads, as it is today.

## Validation Approach

- sysml-codegen tests for every exit code and every not-compared reason, built from real reproducers (`gen_reversed`, default count, literal `Cell[3]`, `s1_gen`), plus the byte-identical corpus check (invariant 2).
- agentic-mbse shipped-text tests. These protect the criteria but do not reduce risk on their own. The suite stays at its base failures.
- Evidence: `evidence/risk1-reruns.md`, with every guidance claim about generator behaviour linking to a row.
- Falsifier for criterion 1: with simkit not importable, and with the generator refusing the model, `compare` exits 3 and prints "not compared". On the literal `Cell[3]` model, it reports `total` as not compared rather than as a difference.

## Next-Stage Handoff

- **Fixed:** option (a); the trace accessor rather than `ModuleOutput` fields (D2); not-compared reasons and counts (D5); exits (D6); count check in (D7); verdict comparison in (D9); one home per fact (D11); RG-2 cases filed and flagged only.
- **Open:** how the multi-occurrence dependence is computed (B2); how the study layer finds simkit, which `compare` matches (D10); the module location in sysml-codegen.
- **De-risk first:** B2, then Phase R.
- **Proposed, not filed (RG-3):** a product promise at close: "for a model that generates, `sysml-codegen compare` reports whether native and generated results and part counts match, and counts what it could not compare" (product-lens spec-F5). No ADR is needed; D1 follows ADR 0004.

---
Next Step: After approval → `/_my_plan`
