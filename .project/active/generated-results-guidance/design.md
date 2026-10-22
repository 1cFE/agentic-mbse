# Design: Guidance that keeps generated results honest (EXEC-SUBSET-CONTRACT Item 5, rescoped)

**Status:** Draft, revised 2026-10-22 after the spike ([spike/RESULTS.md](spike/RESULTS.md)) and the design review ([design-review.md](design-review.md), verdict Revise; resolutions recorded there)
**Owner:** Reid Westwood
**Created:** 2026-10-22
**Git:** agentic-mbse `generated-results-guidance`; the design was first drafted at `8cb55b87` and the spike ran at `d5a26bdc`. sysml-codegen worktree `/home/reid/src/subset-conformance/sysml-codegen` at `53d3cb1b`, whose `src/` is identical to `origin/main` `6190f996`. TEAx simkit at `8d877460`. SysIDE 0.8.4.

## Overview

Give a modeller who targets generated code one command, `sysml-codegen compare`. It evaluates their model natively with SysIDE and through the generated package, checks that the generator built the part counts the model asks for, and reports what differs and what it could not compare. The shipped workflow runs it and says what to do with each answer. Alongside it, fix the guidance for Risks 2 to 4 and re-run every Risk 1 case on current sysml-codegen `main`.

## Related Artifacts

- Spec: [spec.md](spec.md); spec review and its Resolutions: [spec-review.md](spec-review.md); product lens: [product-lens.md](product-lens.md)
- Spike: [spike/RESULTS.md](spike/RESULTS.md) (S1 native paths, S2 channel trace and counts, S3 positional binding), with probes in `spike/native-path/` and `spike/channel-trace/`
- Design review: [design-review.md](design-review.md) (findings M1-M3, S1-S7 and minors, with § Resolutions)
- Epic: `.project/backlog/epic_executable-subset-contract.md`, Item 5 (rescope note at line 258)
- Decision: `.project/adr/0004-generator-is-the-only-generation-authority.md` (invariants 1 to 3); ADR 0005 (`execution-target`)
- Prior evidence: `.project/completed/20261022_retire-subset-profile/evidence/probes.md` (format reused here); `.project/completed/20261018_positional-binding-check/evidence/upstream-codegen-finding.md` and `cross-route/eval_generated.py`

## The Point

[OWNER, 2026-10-22] "Mitigate actual risk, not ceremony." Since ADR 0004, a model the generator refuses is cheap: `sysml-codegen check` says so early and loudly. The risk that remains is a model that passes `check`, generates, and computes different numbers from the native model, or a package whose failed verdicts nobody reads. That failure looks like success.

[AGENT, ratified by owner at launch 2026-10-22] A modeller following the shipped workflow must catch a model that passes `check` and generates but computes different numbers than the native model. Better docs alone do not meet this. So the item must ship something that runs both routes on the modeller's own model.

[INHERITED: ADR 0004] Only the generator says what it builds. agentic-mbse keeps no copy of its rules and imports nothing from sysml-codegen. A tool that is missing or fails means "not compared", never "fine".

Every element below names the risk it reduces (spec Problem, Risks 1 to 4).

## Research Findings

**Nothing general exists yet for the native half.** sysml-codegen never calls SysIDE's evaluator. `sysml-codegen study verify` compares a package against a hand-written Python oracle (`study/verify.py:87-115`), not against SysIDE. dc3 wrote about 1,800 lines for its own comparison. About 100 of them are generic, and about 70% of its evaluator code checks which feature each input is bound to, which a value comparison cannot replace.

**What native evaluation can and cannot do (spike S1, S2).**
- `Compiler().evaluate_feature(feature, scope=<usage>)` gives the right value for plain, inherited, calc-result, nested-part, computed and Boolean attributes. Inputs are the values written in the model, which matches the package's default run.
- It is silently wrong for anything that ranges over a part multiplicity. SysIDE does not expand `cells : Cell[3]` into three parts: `sum(cells.capacity)` returns one cell's value (2.5, not 7.5) and `size(cells)` returns 1, with no diagnostic. This holds for a literal count and for an attribute count.
- It has no value for one index. Asked about `cells[1]`, it returns the per-definition value.
- Constraint verdicts: evaluating the usage's own result expression, or else its definition's, with the usage as scope gives `True` or `False`. The package's `actual_value` matched for both constraints probed.
- Counts: SysIDE evaluates a multiplicity's bound in the owning usage's scope. On the default-count reproducer it gives 3 where the generator built 2 occurrences.
- Not shown by the spike: whether SysIDE sees a value redefined further out than the scope usage, for example two levels up (review M3).

**Where the trace lives (spike S2, design review).** `ModuleOutput` (`resolution/models.py:179-196`) carries no source feature. The trace is in the instance graph. The private `_Projection.output_channels` (`elaboration/project.py:403-413`) maps each output port to its channel. Each port names its calc node and output declaration. The node's scope is an occurrence path with a containment slot and an index per step, and declaration ids are SysIDE element ids (`elaboration/identity.py:70-87`).
- Each step's `containment_slot.root_declaration` is the root of a redefinition family, not the usage that applies (`identity.py:95-98`, built at `occurrence.py:1006-1015`). The spike used that root as SysIDE's scope (`probe_channels.py:43`). It worked only because no spike model redefined a containing part.
- The usage that applies is `ExactOccurrence.effective_usage_id` (`occurrence.py:1039-1050`). dc3 redefines every subsystem part (`part :>> electrical { … }` in `designs/dc_native/dc_facility.sysml`), so this matters on real models (review M2).
- The generator gives index 0 to any usage with an explicit multiplicity, `[1]` included (`occurrence.py:833-835, 918`). Every index of one usage is built from the same declarations (`occurrence.py:1008-1062`). A named subset such as `rack_1 :> racks` is its own slot, not an index.

**Positional binding (spike S3).** At sysml-codegen `6190f996`, `gen_reversed` (`in b = small; in a = big;`) passes `check`, generates, wires `a ← big`, `b ← small`, and gives 7.0. Native SysIDE gives −7.0. So the generator binds unprefixed calc-usage inputs by name, as it did at `b5663c07`.
- The first draft of this design read `elaboration/elaborate.py:2181-2193` as positional. That reading was wrong.
- `docs/patterns/semantic-hazards.md:47-58` stays correct.
- The observed wiring conflicts with `[POSITIONAL-FORMAL-REDEFINITION]`'s text ("current elaboration follows parser redefinition identity"). This item records the result for the codegen owner and does not rule on which reading is intended (RG-1).

**simkit and TEAx.** Generated modules import `simkit` (`templates/constraint_module.py.jinja2:8-9`). sysml-codegen does not declare it (`pyproject.toml:23-28`), and its own environment cannot import it (no `pandas`).
- `study verify` imports simkit from the environment it runs in and fails with a message naming TEAx (`study/verify.py:481-490`). The study seam adds `TEAX_SIMKIT_PATH` to `PYTHONPATH` only for the subprocesses it launches (`study/integrate.py:297-317`).
- dc3 declares `teax-simkit` as an editable path dependency (`dc3/pyproject.toml:9,27`).
- No production code in sysml-codegen loads or runs a generated package today. Only tests do (`tests/execution/real_teax.py:103-152`).

**dc3's shape (design review, read from code, not run).** dc3 has no `sum` anywhere in `models/`. It names each part as a subset (`rack_1 :> racks`, with `racks[2]` only to give the generator an exact count) and computes over named parts. Its generated contract has no indexed channels. It writes `[0]` eleven times in `dc_facility.sysml`. So, under this design, most dc3 values should be compared, provided the effective-usage scope (M2) is used and named subsets are their own slots. The outputs that go uncompared are mainly in a new project that follows the guide's "total over the parts with `sum`" advice.

**Existing homes in agentic-mbse.**
- `project_templates/MODELING_PROCESS.md.template:32-54`, "Generated code": when to run `check`, its exits, and "sysml-codegen missing". Exit 2 there means "fix the command line" (`:42`).
- `project_templates/MODELING_GUIDE.md.template:63-119`, the three limits. Limit 3 advises `sum(cells.capacity)` on the part, passing the total in (`:108-112`). Line 106 warns about the default count. Line 216 warns about input order; validate level 2 reports it.
- `skills/model-validation/SKILL.md:65` says "compare generated and manual execution", with no means to do it.
- `tests/test_shipped_text.py:284-372` pins the limits and the check workflow.

## Core Concept

The comparison belongs to the generator, because only the generator knows which SysML feature each output came from, which usage applies at each step, and how many occurrences it built. sysml-codegen gets a read-only command, `sysml-codegen compare --models models/`. It builds the package in a temporary folder, runs it once with the model's own values, and makes three checks:

1. **Counts.** For each part usage with a multiplicity, in each owning occurrence, SysIDE's bound for the effective usage is checked against the number of occurrences built.
2. **Values.** Each numeric or Boolean output channel is checked against SysIDE's value for its source feature, evaluated with the effective usage as scope.
3. **Verdicts.** Each generated constraint verdict is checked against SysIDE's evaluation of that constraint.

An item is "not compared" when SysIDE's value cannot be trusted. That happens when it is touched by a part multiplicity other than one (including zero), or when a redefinition applies from above the scope SysIDE is given. Each not-compared item names its cause. The report groups them by cause, for example "everything downstream of `pack.cells` (`Cell[3]`)".

The exit code carries the coverage:
- 0 only when everything was compared and nothing differs;
- 1 when something differs;
- 4 when nothing compared differs but some items were not compared;
- 3 when nothing could be compared at all.

An agent that reads only the exit code cannot mistake a partial check for a full one.

**The limit this exposes.** The guide's own limit-3 advice is to total over the parts with `sum(cells.capacity)` and pass the total in. That produces exactly the outputs native SysIDE gets wrong. On a model built that way, the system-level results downstream of each total are not compared, and `compare` exits 4. The design does not hide this or change the modelling advice to suit the checker. The workflow says, in one place, what exit 4 means and what to do for an output the work relies on: check it another way, or record it as unchecked. dc3, which names its parts and has no `sum`, should mostly compare.

agentic-mbse's part is to put the command into the workflow and keep the guidance honest:
- `MODELING_PROCESS.md` says when to run `compare`, what each exit means (including exit 2 from an older sysml-codegen and exit 4), and what to do on each.
- The guide states what an assert does on each route (Risk 2).
- The pattern docs qualify conditional and function teaching with "run `check`" (Risk 3).
- Every guidance claim about generator behaviour has a recorded run and an upstream row that names the guidance to update (Risk 4).

## Key Bets

- **B1. SysIDE gives the right native value for a feature, given its element id and the effective usage as scope, whenever no part multiplicity other than one touches it.** S1 and S2 confirmed this for plain, inherited, calc-result, nested-part, computed and Boolean attributes. Not checked: quantities with units, Integer channels, models split across files. *If false for one of those → false differences there. Each gets a test before release.*
- **B2. The generator can mark, from its own graph, every node a multiplicity other than one touches.** The method (review S2): mark every node whose scope lies inside an occurrence of a slot with a count other than 1, plus every node downstream of a marked node. Separately, mark any node whose expression references a slot with zero occurrences; that needs the expression's reference, because an empty slot has no producer to draw an edge from. *If false → false differences on correct packages (S2: the literal `Cell[3]` model gives generated 9.6, native 3.2), or values passed as compared that SysIDE got wrong. Phase 1 tests it on the spike models, a `[0]` model and a dc3-shaped model.*
- **B3. The effective usage at each occurrence step is the right SysIDE scope and the right source of a multiplicity bound (review M2).** *If false → false differences on any model that redefines a containing part (all of dc3), or false agreement if the generator ignored a redefinition the same way. Phase 1 tests it on a model where a specialised part def redefines a contained part and an attribute value inside it, the `dc_facility.sysml` shape, for both a value and a count.*
- **B4. Given only the innermost effective usage as scope, SysIDE sees every redefinition that applies to the feature (review M3).** S1 shows it sees a redefinition written on the scope usage itself. Nothing shows it sees one written two levels out. *If false → both routes could agree on a wrong value. Fallback: the generator's redefinition index tells which features are redefined above the innermost scope, and those items become not compared, with the reason "redefined above the evaluation scope". Phase 1 tests it with an outer part redefining a value inside a nested part.*
- **B5. Generate-but-wrong cases that matter show up as a value, count or verdict difference.** *If false (a loss that leaves no trace in what is built, like a dropped String) → `compare` passes over it. Those losses stay with `[SILENT-LOSSES-UNREPORTED]` and RG-2, and the help names that limit.*
- **B6. TEAx's package-loading API (`ProvisionalPackageLoader`, `execute_pipeline`) is stable enough to call from production code.** `compare` is the first production caller. *If false → `compare` breaks when TEAx changes. Mitigation: the report header records the TEAx revision and the simkit path, as `study/integrate.py:369-376` does.*

## Key Decisions

**D1. The comparison is a new sysml-codegen command, `compare` (option (a)).**

| | (a) `sysml-codegen compare` | (b) agentic-mbse helper running the generator as a separate process | (c) template test plus guidance; modeller names outputs |
|---|---|---|---|
| What the modeller supplies | nothing | a path list, since channel names cannot be un-mangled safely | a list of output paths and their channel names |
| Can see effective usages, multiplicity dependence and counts | yes; it holds the graph | no; it sees only the emitted package | no |
| Copies generator knowledge | no | yes: package layout, channel naming, how to run simkit | the naming rule, in each project |
| Cost (agent estimate, ±50%) | 5 to 7 days in sysml-codegen | 3 to 5 days, plus a standing two-repo sync | 2 days, plus each project's upkeep |

*Rejected: (b), because it puts a copy of generator internals in agentic-mbse, which is what ADR 0004 removed, and it cannot see what makes a native value untrustworthy. Rejected: (c), for the same blindness, and because a per-project list goes stale.* The orchestrator may add (a), because it does not change what the generator builds (owner delegation at launch).

**D2. The trace comes from a new public, read-only accessor in sysml-codegen's elaboration layer.** It wraps a fresh `_Projection(graph).run()` on the prepared graph; `project()`'s signature and return value are unchanged. It returns frozen, typed records:
- for each output channel: the calc node, the output declaration's element id, and the occurrence chain, with the containment slot, the index and the **effective usage id** for each step (M2);
- the not-compared marks and their causes (B2, B4);
- for each part usage with a multiplicity, in each owning occurrence: the effective usage id and the number of occurrences built.

*Rejected: adding source ids to `ModuleOutput`. That record feeds emission and the package contract, so a new field risks changing what is built (RG-1).*

**D3. Compare at the model's own values only; no input sweeps (Risk 1).** One default run catches wrong wiring and wrong counts. *Rejected: sampled inputs. Native evaluation cannot take inputs without editing model text, and sweeps belong to `study verify`.*

**D4. Value checks cover the generator's numeric and Boolean channels only (Risk 1, RG-2).** *Rejected: reporting model features with no channel. That would report dropped String values, a choice reserved by RG-2.*

**D5. Not-compared causes.** Each not-compared item carries one cause, and the report groups items by it:

```
multiplicity <path> (<count>)    touched by a slot whose count is not 1, zero included (B2)
redefined above scope <feature>  a redefinition applies outside the scope SysIDE is given (B4)
no native value                  SysIDE returned no value, or a diagnostic
```

**"Indexed" means "inside an occurrence of a slot whose count is not 1".** A `[1]` part gets index 0 but is compared.

**Per-index channels stay not compared (review S1, not accepted).** The review argued that each index is built from the same declarations, so each must equal SysIDE's one value. That holds inside the generator's occurrence model, but not in SysML. No syntax redefines `cells[1]` directly. But a named subset can give one member of a collection its own value (`part c1 :> cells { :>> capacity = 4.0; }`). SysML reads `c1` as one of `cells`' members. The generator builds `c1` as its own slot and builds every index of `cells` from the shared declarations. If that is wrong for such a model, the generated per-index values and SysIDE's per-definition value would agree on the wrong number. The spike's `packredef` probe tried this shape and did not settle it (RESULTS.md, Open Questions). Because a route exists by which members can differ, comparing per index could give a false agreement. So they stay not compared, under the multiplicity cause. Counts nested inside such occurrences follow the same rule.

**D6. Exit codes (review M1, S4).**

```
0  everything was compared and nothing differs
1  at least one value, count or verdict differs (listed)
2  usage error; uv's "Failed to spawn"; or "invalid choice: 'compare'" (sysml-codegen too old)
3  nothing compared. Reason starts "environment:" (refused model, simkit or SysIDE unavailable)
   or "package run failed:" (the run raised, for example on a null input it names)
4  nothing compared differs, but some items were not compared (grouped by cause)
```

Exit 1 takes precedence over 4. *Rejected: exit 0 on a partial comparison (the first draft). An agent reading exit 0 would not read the counts, and the outputs left uncompared are usually the headline results (review M1).* *Rejected: `check`'s one code for refusal and environment failure.* The two exit-3 prefixes separate missing tooling from a run that points at a generator defect.

**D7. The count check is in and is load-bearing (Risk 1, the default count).** It runs once per (effective usage, owning occurrence) pair. SysIDE's bound is taken from the effective usage's multiplicity, in the owning occurrence's effective-usage scope. It is the only check that catches `[ATTRIBUTE-MULTIPLICITY-DEFAULT-COUNT]`. It also covers the one case where B2 could give a false pass: the generator building one part where the model asks for several, which native SysIDE also reads as one. *Rejected: relying on the guide warning at `MODELING_GUIDE.md.template:106` alone.*

**D8. Tolerance: numbers agree when `|g − n| ≤ rel·max(|g|, |n|) + abs`, with defaults rel = 1e-9 and abs = 0, and flags `--rel-tol` and `--abs-tol`.** Booleans and integers must match exactly, and NaN never agrees. The summary prints the worst deviation. `--abs-tol` is for a channel whose true value is near zero, such as a balance residual. There, rounding noise is large relative to the value. dc3's 2.38e-7 absolute difference was on values around 1e9 Wh, which the relative tolerance already passes (`WI-008_generator-idiom/review.md:14`).

**D9. Verdict comparison is in (Risks 1 and 2).** The native verdict is the usage's own result expression, or else its definition's, evaluated with the effective usage as scope. The two sides are joined through the catalog's `usage_qualified_name` and `owner_instance_path`; the join is in the first test set. Verdicts touched by a multiplicity are not compared (D5). The command prints the generated headline and lists violated verdicts. A violated verdict that agrees with native is the model's answer, not a difference. *Rejected: re-deriving verdicts from `predicate_ir`, because that is a second evaluator.*

**D10. simkit is imported from the environment only, as `study verify` does (`study/verify.py:481-490`).** `compare` does no `sys.path` or `TEAX_SIMKIT_PATH` work. If the import fails, it exits 3 with: `environment: cannot import simkit (TEAx teax-simkit). Declare teax-simkit in the project's dependencies, or put a simkit root on PYTHONPATH, and run sysml-codegen from the project's environment.` The report header records the TEAx revision and simkit path (B6). *Rejected: making simkit a sysml-codegen dependency, because TEAx is not published and every user's install would change.*

**D11. `compare` takes live `--models` only, not `--from-snapshot`.** SysIDE needs the source files.

**D12. Per-item report line.** Each line gives: kind (value, count or verdict), the SysML qualified name, the occurrence path, the native value, the generated value, the result (agree, differ or not compared) and the cause. Agreeing items are hidden unless `--verbose` is given. The summary always reads `values: compared N of M; counts: P of Q; verdicts: R of S`.

**D13. One home per fact.**

| Fact | Home | Pointers only from |
|---|---|---|
| When to run `compare`; every exit, including exit 2 from an older sysml-codegen and exit 4; what to do on each; how to provide simkit | `MODELING_PROCESS.md.template`, "Generated code" | implement-model, model-validation, toolkit-awareness skills; the guide's checklist |
| Outputs computed from a total over a part multiplicity are not compared, and what to do about it | the same `MODELING_PROCESS` paragraph, under exit 4 | one sentence after the guide's limit-3 `sum` advice (`MODELING_GUIDE.md.template:108-112`) |
| An assert never stops a computation on either route; check verdicts before using values (Risk 2) | `MODELING_GUIDE.md.template`, limit 1 | `docs/patterns/constraints.md` near line 158 |
| The default-count warning | `MODELING_GUIDE.md.template:106` (exists) | none new |
| Input order across routes | `docs/patterns/semantic-hazards.md` (exists; "Verified with" gains the `6190f996` result) | none new |
| Conditionals and library functions are native teaching; run `check` before relying on them (Risk 3) | each teaching site, one qualifier line | none |
| Which guidance to update when a generator limit lifts (Risk 4) | the sysml-codegen backlog row for that change | none |

**D14. What the guidance says about the limit-3 tension.** In the `MODELING_PROCESS` exit-4 text: "Native SysIDE evaluates a part with a multiplicity as one part, so it cannot check a total over the parts (`sum(cells.capacity)`) or anything computed from it. `compare` lists these under the part they depend on. For each one the work relies on, check it another way (a hand calculation, or a kept test of the generated value against an independent figure), or record it as unchecked." This is a fact about native SysIDE, not a generator rule. The limit-3 advice is unchanged, because it is still how a model over many parts generates. *Rejected: advising modellers to name each part (the dc3 shape) so values compare. It makes models longer to suit a checker, and nobody has run whether SysIDE handles a total over named subsets.*

**D15. Risk 3 qualifiers name no function list.** The wording is: "Native SysIDE evaluates this. In a project that targets generated code, run `sysml-codegen check` before relying on it; the generator does not accept every expression the language allows." *Rejected: naming refused functions, which goes wrong when `[SCALAR-FUNCTION-VOCABULARY]` lands (product-lens spec-F2).* The proposed test "no guidance names `min`/`max`/`product`/`size` as generator-accepted" is dropped (review S6). No text test can decide "as accepted", and a plain search would fail on the native teaching sites that rightly keep the names. Pinning the qualifier next to each teaching site proves the criterion instead.

**D16. Risk 4 is handled by upstream notes plus `compare`, not by version stamps in guidance prose.** Each owner-held change that would lift a stated limit (`[CALCDEF-GATE-IMPLEMENTATION]` for limit 1; `[ATTRIBUTE-MULTIPLICITY-DEFAULT-COUNT]` for line 106) gets a line naming the agentic-mbse files and headings to update. Recorded runs carry the revision.

## Architecture

```
modeller ─> MODELING_PROCESS "Generated code" ─> sysml-codegen check    (does it build?)
                                             └─> sysml-codegen compare  (same results?)
compare: import simkit (else exit 3) ─> load + prepare (as generate) ─> trace accessor (D2)
         ─> emit to temp dir ─> run package once (simkit) ─> channels + verdicts
         ─> SysIDE, scope = effective usage: bound per (usage, owner) | value | verdict
         ─> agree / differ / not compared (cause) ─> grouped report ─> exit 0/1/3/4
```

- **Boundary.** agentic-mbse ships text and tests only (invariant 2).
- **Writes.** Nothing in the project. The package goes to a temporary folder; `--keep <dir>` keeps it.
- **Layout in sysml-codegen.** A small `sysml_codegen/compare/` package. `cli/compare.py` only parses arguments, like `cli/study.py`.
- **Reuse.** `run_check`'s load-and-prepare path (`cli/__init__.py:117-129`), `emit_package`, and the loader pattern in `tests/execution/real_teax.py:103-152`. The spike's `probe_channels.py` and `probe_count.py` are working references; they must switch from the slot root to the effective usage.

## Required Invariants

1. `compare` exits 0 only when every value, count and verdict was compared and none differed. Any not-compared item gives exit 4, or 1 if something also differs (ADR 0004 invariant 3; review M1).
2. `compare` and the accessor change nothing the generator builds. The whole generated tree, `contracts/` and fingerprints included, is byte-identical before and after the accessor change. The corpus is sysml-codegen's test fixtures, the spike models and dc3 `models/` (RG-1).
3. An item whose native value is untrustworthy (D5) is never reported as agreeing or differing.
4. No agentic-mbse module imports sysml-codegen or simkit (ADR 0004 invariant 2). This item adds no agentic-mbse code.
5. agentic-mbse guidance names no list of accepted or refused functions. Its claims about generator behaviour are limited to the three limits plus each behaviour confirmed in Phase R, each with a recorded run and an upstream row (spec criteria 3 and 5; review S5).
6. No guidance line about dropped String values or dropped calc-usage result expressions is added while RG-2 is open.

## Component Overview

**sysml-codegen (branch from `origin/main`, orchestrator-delegated):**
- The accessor in `elaboration/` (D2).
- `sysml_codegen/compare/` and `cli/compare.py`, with tests:
  - `gen_reversed` exits 1 on value `diff.r` (native −7, generated 7);
  - the default-count reproducer exits 1 on its count, with `total` not compared under `pack.cells`;
  - the literal `Cell[3]` model exits 4, with `total` grouped under `pack.cells (3)`;
  - a `[0]` model exits 4, not 1;
  - the dc3-shaped redefinition model compares value and count (B3);
  - the two-levels-out redefinition is compared, or not compared with its cause (B4);
  - a `[1]` part compares;
  - a violated assert exits 0, with the headline printed;
  - the verdict join;
  - simkit not importable and a refused model each exit 3 with `environment:`;
  - a null input exits 3 with `package run failed:` and names the input.
- Backlog rows (Phase 7).

**agentic-mbse:**
- `MODELING_PROCESS.md.template`, "Generated code": a "Compare results" paragraph.
  - When to run it: once the model generates, at the end of each phase where `check` exits 0, and before any claim about generated results.
  - Exit 1: the native model is the model's meaning. Reduce the case to a minimal reproducer, record it and file it upstream. Do not rewrite the model to match the package unless the native result is shown wrong.
  - Exit 2: with "invalid choice: 'compare'", report "not compared: sysml-codegen does not have `compare`; update it", never a command line to fix. Otherwise as for `check`.
  - Exit 3: `environment:` is missing tooling, reported as "not compared" and never as fine. `package run failed:` is a finding to record and file.
  - Exit 4: the D14 text.
  - How to provide simkit (D10).
- `MODELING_GUIDE.md.template`: the Risk 2 paragraph in limit 1; one pointer sentence after the limit-3 `sum` advice; a `compare` line in the checklist.
- `skills/implement-model`, `skills/model-validation` (the "Translation" line at `:65` becomes a pointer) and `skills/toolkit-awareness`: one pointer line each.
- Risk 3 qualifiers (D15) at:
  - `docs/patterns/conditionals.md` (once, under Quick Reference) and `docs/patterns/syntax-reference.md` near `:283`;
  - `skills/sysml-conventions/SKILL.md:194` and `MODELING_GUIDE.md.template:190`;
  - `docs/patterns/README.md:18`;
  - `agents/kerml-expert.md` near `:26` and `:87`, and `agents/sysmlv2-validator.md` near `:296`.
- `docs/patterns/semantic-hazards.md`: add the `6190f996` result to "Verified with" and the routes table, and say where the draft finding was filed.
- `tests/test_shipped_text.py`: pins for the compare paragraph (every exit, including "invalid choice" and exit 4), the limit-3 pointer, the Risk 2 statement, and the Risk 3 qualifier at each site.

## Non-Goals

- Agree-but-wrong errors (equal-value misbindings, a shared formula error); validate level 2 and native checks own them.
- Native values over part multiplicities, or per index (D5). They are reported, grouped by cause.
- Changing the limit-3 modelling advice to suit the checker (D14).
- Input sweeps (D3); reporting dropped Strings or features (D4, RG-2).
- A template test in target projects.
- Generator fixes, and ruling on which positional reading the generator should follow (RG-1).

## Implementation Notes

**Build order (review S7).** The B2 to B4 test models in Phase 1 are new. The others reuse spike models.

1. **De-risk (sysml-codegen, read-only, about a day).** Test B2, B3 and B4 together on these models: the spike models, a `[0]` model, a `[1]` model, a dc3-shaped model (a specialised part def redefining a contained part and a value inside it), and a two-levels-out redefinition. Use the spike's probe scripts, switched to the effective usage. **If any bet fails, stop and report to the orchestrator with the result and the fallback, before building.**
2. **Accessor plus byte-identity check** on the named corpus (invariant 2).
3. **`compare` and its tests** (Component Overview).
4. **sysml-codegen merge** (owner, RG-3).
5. **agentic-mbse text and pins.**
6. **Phase R** (below), using `compare` once it exists, or the probe scripts before then.
7. **Phase U** (below).

**Phase R: Risk 1 re-runs on sysml-codegen `main`.** Record the revision. Run each probe with `check`, `generate` and `compare`. Record the results in `evidence/risk1-reruns.md` in the `probes.md` format, with each model in `evidence/probes/<case>/`.

| Case | Status going in | Guidance outcome |
|---|---|---|
| Default count | confirmed (S2: 2 built for 3) | already warned (`:106`); pin; caught by D7 |
| Positional (`gen_reversed`, `gen_byname`) | confirmed at `6190f996` (S3: native −7, generated 7) | already warned (`:216`, `L2_POSITIONAL_BINDING`, `semantic-hazards.md`); update "Verified with"; caught by the value check |
| String dropped | confirmed earlier | file and flag only (RG-2) |
| Calc-usage result expression and lost binding | confirmed earlier | file and flag only (RG-2 / RG1-3); record the exit-3 `package run failed:` |
| Calc def simple-name collision | unconfirmed | warn (distinct calc def names) only if confirmed |
| Unresolved conditional branch, indexed reference, unsupported callable outside a predicate | not re-checked | if they generate and differ, warn at the Risk 3 site; if refused, record the refusal |
| Conditional and `min` refusals (Risk 3 evidence) | stored case only / backlog | a `check` run each backs the qualifier |
| Assert verdict (Risk 2 evidence) | S2 saw `violated` with outputs computed (`s1_gen`) | record as the backing run |

**Phase U: upstream rows (sysml-codegen branch, orchestrator-delegated).**
- Confirmed cases get a minimal inline reproducer and the revision. Unconfirmed cases get "not reproduced at <rev>" with the probe.
- `[POSITIONAL-FORMAL-REDEFINITION]`: record that at `6190f996` unprefixed calc-usage inputs are wired by name, native SysIDE binds by position, and `gen_reversed` gives generated 7, native −7. Note that this differs from the row's "follows parser redefinition identity". File agentic-mbse's draft finding there and mark the draft filed. No ruling on which reading is intended.
- Fix the stale `retire-subset-profile` path in `[SILENT-LOSSES-UNREPORTED]` (spec review L4-1).
- Add guidance pointers to `[CALCDEF-GATE-IMPLEMENTATION]` and `[ATTRIBUTE-MULTIPLICITY-DEFAULT-COUNT]` (D16).
- Add a row for `compare` if sysml-codegen's process wants one.

**Follow-up, not in this item.** Native SysIDE's one-part reading of `sum` over a multiplicity also misleads projects that evaluate natively (`execution-target = "native"`). It is a candidate entry for `docs/patterns/semantic-hazards.md`. File it in the agentic-mbse backlog at close; this item's risks are about the generated route.

## Potential Risks

- **A de-risk bet fails (B2 to B4).** Phase 1 stops and reports. The fallback for each is in its bet, and every fallback moves items to "not compared" with a cause, never to "agree".
- **Many outputs end up not compared on models that follow limit 3.** Exit 4 makes this visible, and D14 says what to do. The value check is then weak on those models. The count and verdict checks still run, and leaf values still compare.
- **Not checked by the spike** (RESULTS.md, Open Questions). Each needs a test before release:
  - quantities with units;
  - Integer and Boolean output channels;
  - calc usages nested more than one level inside indexed occurrences;
  - models split across several files;
  - whether a named subset gives a member its own value (D5);
  - the verdict join in code.
- **TEAx changes its loading API (B6).** The report header records the revision, so a break is traceable.
- **simkit is missing in a target project.** Exit 3 with `environment:` and how to provide it.
- **A modeller loosens the tolerance until differences disappear.** The workflow says to record any `--abs-tol` and why; the summary prints the worst deviation.

## Integration Strategy

The modeller already runs `check` at the same points; `compare` is the next line in the same section. Nothing changes for projects targeting `native`. `execution-target` (ADR 0005) is the switch the workflow reads.

## Validation Approach

- sysml-codegen tests for every exit code and every not-compared cause, built from real reproducers, plus the byte-identity check on the named corpus (invariant 2).
- A run on dc3 `models/`, recording how many values, counts and verdicts were compared. Expect most values compared (dc3 names its parts). A low share is a finding to report, not to tune away.
- agentic-mbse shipped-text tests (protection, not risk reduction), with the suite at its base failures.
- Evidence: `evidence/risk1-reruns.md`, with every guidance claim about generator behaviour linking to a row.
- Falsifiers for criterion 1:
  - with simkit not importable, or the generator refusing the model, `compare` exits 3;
  - on the literal `Cell[3]` model it exits 4, not 0, with `total` grouped under `pack.cells`;
  - on an older sysml-codegen, the workflow text maps exit 2 with "invalid choice" to "not compared".

## Next-Stage Handoff

- **Fixed:**
  - option (a), with the accessor carrying effective usages (D2);
  - not-compared causes, with per-index items kept not compared (D5);
  - exits 0/1/2/3/4 (D6);
  - the count check, which is load-bearing (D7);
  - verdict comparison (D9);
  - simkit from the environment (D10);
  - the limit-3 text (D14);
  - one home per fact (D13);
  - RG-2 cases filed and flagged only;
  - the build order above.
- **Open:** the exact data for the zero-occurrence mark (expression reference); the fallback for B4 if it fails.
- **De-risk first:** Phase 1, with stop-and-report.
- **Proposed, not filed (RG-3):** a product promise at close: "for a model that generates, `sysml-codegen compare` reports whether native and generated results and part counts match, and its exit code says when it could not compare everything" (product-lens spec-F5). No ADR is needed; D1 follows ADR 0004.

---
Next Step: After approval → `/_my_plan`
