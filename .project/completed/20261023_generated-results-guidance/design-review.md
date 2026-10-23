# Design Review: Guidance that keeps generated results honest (EXEC-SUBSET-CONTRACT Item 5, rescoped)

**Design:** `.project/active/generated-results-guidance/design.md` (revised 2026-10-22 after the spike)
**Spec:** `.project/active/generated-results-guidance/spec.md`, with `spec-review.md` § Resolutions
**Spike:** `.project/active/generated-results-guidance/spike/RESULTS.md`
**Review File:** `.project/active/generated-results-guidance/design-review.md`
**Date:** 2026-10-22

What I checked: the design, spec, spec review, spike results and the spike probe `channel-trace/probe_channels.py`; in sysml-codegen (read-only, worktree at `53d3cb1b`): `elaboration/identity.py`, `elaboration/occurrence.py` (occurrence building and multiplicity expansion), `elaboration/project.py:388-413`, `elaboration/__init__.py`, `cli/__init__.py:100-129`, `study/integrate.py` and `study/verify.py` (how simkit is found); in dc3: `models/` (all `.sysml` files, by search), `designs/dc_native/dc_facility.sysml`, `designs/dc_native/dc_site.sysml`, the generated contract `exploration/ac_dc_baseline/dc3_baseline/contracts/model_contract.json`, and `work/active/WI-008_generator-idiom/review.md`; in agentic-mbse: `MODELING_PROCESS.md.template:28-58` and `MODELING_GUIDE.md.template` (multiplicity and aggregation text).

What I did not check: I ran no Python, no generator and no SysIDE (Python runs were not permitted in this session). Every claim below about what SysIDE or the generator would do on a model the spike did not run is read from code, and is marked as such. I could not read the product-lens script (`~/.claude/scripts/product-lens.md`, permission denied), so the lens below was run inline against the same sources, not by a separate agent.

---

## The Point

[OWNER, 2026-10-22] "Mitigate actual risk, not ceremony." Since ADR 0004, a model the generator refuses is cheap: `sysml-codegen check` says so early. The risk that remains is a model that passes `check`, generates, and computes different numbers from the native model, or a package whose failed verdicts nobody reads. That failure looks like success.

[AGENT, ratified by owner at launch 2026-10-22] A modeller following the shipped workflow must catch a model that passes `check` and generates but computes different numbers than the native model. Better docs alone do not meet this.

[INHERITED: ADR 0004] Only the generator says what it builds. agentic-mbse keeps no copy of its rules and imports nothing from sysml-codegen. A missing or failed tool means "not compared", never "fine".

The spec's four risks: (1) patterns that generate but compute something different; (2) an assert never stops a computation and the guidance does not say so; (3) guidance teaches forms the generator refuses without saying so; (4) guidance goes stale when the generator changes.

## Fundamental Assessment

**Sound, with concerns. Verdict: Revise.**

This is the right piece of work. Putting the comparison inside sysml-codegen (D1, option (a)) is the right call. Only the generator knows which SysML feature each output came from and how many parts it built, and the spike showed both facts are needed. The design does not copy generator rules into agentic-mbse, and it is not a second evaluator: native values come from SysIDE, generated values come from running the package, and the "can SysIDE be trusted here" decision is made from the generator's own graph. The count check (D7) is a good addition; it is the only thing that catches the confirmed default-count defect.

Three things stop it from being plan-ready:

1. **Exit 0 can mean "most of what matters was not compared".** The shipped guide tells modellers to total over many parts with `sum(cells.capacity)` and pass the total on (`MODELING_GUIDE.md.template:108-112`). That is exactly the shape SysIDE gets wrong, so every output downstream of such a total is "not compared". Those are usually the system-level results the modeller cares about. The command still exits 0 if one leaf value was compared. The ratified goal says the workflow must *catch* a wrong-number model; for these outputs it cannot, and exit 0 hides that from an agent that reads exit codes.
2. **The native scope comes from the wrong declaration.** Each step of an occurrence path stores the *root* declaration of a redefinition family, not the usage that applies (`elaboration/identity.py:95-98`, built at `occurrence.py:1006-1015`). The spike used that root as SysIDE's scope (`probe_channels.py:43`). It worked because no spike model redefined a containing part. dc3 does this everywhere (`part :>> electrical { … }`, `part :>> cooling { … }` in `dc_facility.sysml`).
3. **An unstated bet: one SysIDE scope element is enough.** SysIDE evaluates a feature in the scope of a single usage. A value redefined further out (a site redefining a value inside its facility) may not be seen. If the generator has the same blind spot, both routes agree on the wrong number.

None of these changes the approach. Each is a bounded design fix. The product-lens and the two structural smells did not fire anything that forces Rework (see the ledger block appended to `product-lens.md`).

### Answers to the orchestrator's five questions

**1. Is the `compare` architecture clean?** Mostly yes.
- Where it lives: a CLI command plus a comparison module, and a read-only accessor in `elaboration/`. This matches how `check` reuses `prepare` (`cli/__init__.py:117-129`). The design leaves the module location open; it should be a small package (for example `sysml_codegen/compare/`) with `cli/compare.py` only parsing arguments, like `cli/study.py`.
- The accessor: right idea, but it must return the effective usage per occurrence step, not only the slot root (must-fix M2). `ExactOccurrence.effective_usage_id` already holds it (`occurrence.py:1039-1050`).
- Native evaluation: SysIDE's `evaluate_feature` / `evaluate`. Not a second evaluator. The verdict rule (usage's result expression, else the definition's) is a SysIDE call, not a re-derivation from `predicate_ir`. Good.
- Exits 0/1/2/3: the split between "differ" and "not compared" is right. Exit 0 is too generous (M1). Exit 2 is ambiguous for a project with an older sysml-codegen (S4).
- Compared-of-total summary: right, and should name what was not compared by cause (M1).
- Nothing in the design is a copy of generator rules. The count check compares SysIDE's bound with what the generator built; it does not restate the generator's bound rule.

**2. Can it give a false pass?** Yes, in three ways, all fixable.
- Partial comparison exits 0 (M1).
- Root-declaration scope (M2) and single-element scope (M3) can make both routes agree on a value the model does not have.
- A gap in the "depends on a multiplicity" rule (B2) gives a false *difference*, not a false pass, with one exception: if the generator built exactly one part where the model asks for several, native SysIDE (which always reads one part) and the package agree. The count check catches that case, so the count check is load-bearing and must not become optional.

On dc3: the premise that dc3 sums over parts does not hold. There is no `sum` anywhere in `dc3/models`. dc3 names each part as a subset (`rack_1 :> racks`, with `racks[2]` written only to give the generator an exact count) and computes over named parts. Its generated contract has no indexed channels (no `[n]` in `model_contract.json`). So under this design most dc3 values would be compared, provided two things hold that nobody has run: (a) a named subset is its own slot, so B2 does not flag it (that is how `occurrence.py:973-982` reads, by slot), and (b) M2 is fixed, since dc3 redefines every subsystem part. The "mostly not compared while exiting 0" case is real, but for a *new* project following `MODELING_GUIDE.md.template:108-112`, not for dc3.

**3. Does each element reduce a named risk?** Yes for the core. Count check, value check and verdict check reduce Risk 1. The headline and violated-verdict list reduce Risk 2. The guide paragraph, D12 qualifiers and D13 upstream rows reduce Risks 2 to 4. Two items lean toward ceremony: "record the not-compared counts" in the workflow is a ritual unless the exit code carries the information (M1), and the shipped-text test "no shipped guidance names `min`, `max`, `product` or `size` as generator-accepted" cannot be checked as worded (S6). Dropping per-index channels (D5) removes real coverage for no stated gain (S1).

**4. Is the RG-1 boundary held?** Yes in intent. `compare` emits to a temp folder and changes nothing in emission, and the accessor is read-only. The byte-identity check is the right guard, but it is not specified enough to run: name the corpus (the sysml-codegen test fixtures, the spike models and dc3's models) and say it compares the whole generated tree, including `contracts/` and any fingerprints (S7). The accessor should wrap a fresh `_Projection(graph).run()` on the prepared graph rather than changing `project()`'s signature or return value.

**5. Is the handoff plan-ready?** Not quite (S7).
- The build phases for `compare` itself are not ordered.
- The B2 fallback is not easier than B2 as written. A concrete method exists (S2).
- The simkit question can be closed now (S3).
- Merge order covers this branch but not target projects pinned to an older sysml-codegen (S4).

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

- Criterion 1 (Risk 1): met in form (a sysml-codegen command plus a workflow step), and the falsifier is designed in (exit 3 when simkit, SysIDE or the generator is unavailable). But for models following the shipped aggregation advice, the comparison does not catch a wrong number in the outputs that matter, and the exit code says success (M1). The `[INFERRED]`, owner-ratified goal says "would catch". The design treats "printed the count" as enough; a tired agent reading exit 0 will not read the count.
- Criterion 2 (Risk 2): met. The guide paragraph and the `s1_gen` backing run are there.
- Criterion 3 (Risk 1 re-runs): met by Phase R.
- Criterion 4 (Risk 3): met by D12. The shipped-text test that backs it is not checkable as worded (S6).
- Criterion 5 (Risk 4): met by D13. Invariant 5 is narrower than the spec allows: it lists only the limits, the default count, the assert behaviour and input order, while Phase R says to warn about a confirmed simple-name collision or a confirmed conditional-branch loss (S5).
- Provenance: the design carries the `[INFERRED]` ratified goal at agent grade and the ADR 0004 items as inherited, as it should. It does not harden a challengeable item into a fixed constraint.

### 2. Pattern Consistency
**Assessment:** Concerns

- Reuse of `run_check`'s load-and-prepare path is right.
- The design's reuse list points at `tests/execution/real_teax.py:103-152` for loading and running a package. No production code in `sysml-codegen/src` loads or runs a generated package through TEAx today (a search for `ProvisionalPackageLoader` and `execute_pipeline` in `src/` finds nothing). So `compare` becomes the first production code to depend on TEAx's package-loading API. That is a new coupling and should be stated as one, with the TEAx revision recorded in the report the way `study/integrate.py:369-376` records it (S3).
- simkit: the design says `compare` should follow the study layer's rule but leaves that rule open. I checked it. `study/verify.py:481-490` imports simkit from whatever environment it runs in and fails with a message naming teax. The study seam puts `TEAX_SIMKIT_PATH` on `PYTHONPATH` only for the subprocesses it launches (`study/integrate.py:297-317`). So "the same rule" for an in-process command means: import from the environment only, and do no `sys.path` work. Close D10 on that (S3).
- `check` also accepts `--from-snapshot`. `compare` cannot use a snapshot, because SysIDE needs the live files. Say `compare` takes `--models` only.

### 3. Abstraction Quality
**Assessment:** Concerns

- The accessor bundles three views: channel trace, multiplicity dependence and part counts. That is acceptable, because all three come from one prepared graph and `compare` is their only consumer. Return frozen, typed records, and keep `_Projection` private behind it.
- The occurrence chain must carry the effective usage id per step, not only `containment_slot.root_declaration` (M2). This is the one place the accessor's shape is wrong as described in D2.
- "Indexed occurrence" needs a definition. The generator gives index 0 to any usage with an explicit multiplicity, including `[1]` (`occurrence.py:833-835, 918`). A rule keyed on "the step has an index" would mark everything under a `[1]` part as not compared, though SysIDE is right there. The rule should key on "the slot has a count other than 1" (S1, S2).

### 4. Duplication Avoidance
**Assessment:** Pass

No copy of generator rules in agentic-mbse. No second evaluator: native values come from SysIDE, and verdicts are not re-derived from `predicate_ir`. D11's one-home-per-fact table is clear. `study verify` and `compare` stay distinct: `study verify` compares against a hand-written oracle over sampled inputs, `compare` compares against SysIDE at the model's own values.

### 5. Data Structure Clarity
**Assessment:** Concerns

- The report format is described only by its summary line. The plan needs the per-item line shape: kind (value, count or verdict), the SysML element (qualified name), the occurrence path, native value, generated value, verdict (agree, differ or not compared) and reason.
- For not-compared values, the report should say *which* part multiplicity caused it (for example "depends on `pack.cells` (`Cell[3]`)"), and group by that cause. That turns "48 not compared" into "everything downstream of `pack.cells` was not compared", which a modeller can act on (M1).
- The count check's unit is unclear: "per part usage" in the Core Concept, "under each owning occurrence" in D2. State that it runs once per (effective usage, owning occurrence) pair, with SysIDE's bound taken from the effective usage's multiplicity.

### 6. Route Safety
**Assessment:** Concerns

Read here as "every path through the command ends in a defined answer".

- Exit 2 has two meanings for a target project. A sysml-codegen without `compare` exits 2 through argparse ("invalid choice"), and the shipped workflow today says exit 2 means "fix the command line and run again" (`MODELING_PROCESS.md.template:43`). A modeller on an older sysml-codegen would loop on a correct command. The workflow text for `compare` must say exit 2 with "invalid choice: 'compare'" means "not compared: sysml-codegen too old" (S4).
- Exit 3 lumps environment failures (no simkit, no SysIDE licence) with a package that fails to run because the generator left an input null. The second points at a generator defect. The design already names the input in the reason line; the workflow text should tell the modeller that a package-run failure is a finding to record and file, not an environment fix. This stays inside RG-2: it reports that the run failed, and adds no guidance about dropped result expressions.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

- B1 to B4 are real bets with "if false" consequences. Good.
- **Hidden bet H1 (must-fix, M2): the slot root is a valid native scope.** It is not, in general. It worked in the spike only because no containing part was redefined.
- **Hidden bet H2 (must-fix, M3): one innermost scope element is enough for SysIDE to see every redefinition that applies.** S1 shows SysIDE resolves a redefinition written on the scope usage itself (`evaluate_feature(Pack::cell_count, scope=pack) -> 3`). Nothing shows it sees a value redefined two levels out. Neither does the generator's handling of that case have a recorded test here. If both miss it, they agree on the wrong value.
- **Hidden bet H3 (should-fix): TEAx's package-loading API is stable enough to call from production code** (S3).
- **B2 is stated too narrowly.** "A slot whose occurrence set has more than one member" misses a slot with zero occurrences. dc3 writes `[0]` eleven times in `dc_facility.sysml`. SysIDE does not expand multiplicities, so it would likely read `sum(x.v)` over a `[0]` slot as one value; the package gives 0. That is a false difference, not a false pass, but it would hit real models (S2).
- B2's fallback ("mark every channel downstream of any multiplicity") needs the same reachability as B2 itself. It is not a cheaper fallback as written (S2 gives a concrete method).
- Decisions D1 to D13 each name a rejected alternative. D5's "per-index value" exclusion is presented as forced by SysIDE. It is not: in the generator's occurrence model, every index of one usage is built from the same declarations, so at the model's own values each index must equal SysIDE's one value (S1).
- D8's rationale cites dc3's "near-zero residual (2.4e-7)". dc3's record says 2.38e-7 *absolute* across 112 channels of values around 1e9 Wh (`WI-008_generator-idiom/review.md:14`), which relative tolerance 1e-9 already passes. The real case for `--abs-tol` is a channel whose true value is near zero, such as a balance residual. Fix the rationale so the workflow's "record any `--abs-tol` and why" has the right example (minor).

### 8. Reader Comprehension
**Assessment:** Pass

The Point, Core Concept and the three-check list give a clear mental model. Decisions are in plain words with tables where they help. One gap: the design never says, in one sentence, what share of a typical model's outputs will be compared. A reader cannot tell from it that the shipped aggregation advice leaves headline outputs uncompared; that fact sits under Potential Risks ("Many models have part multiplicities") rather than in the Core Concept. Moving it up is part of M1.

---

## Issues by Severity

### Critical (must-fix before planning)

- **M1. Exit 0 on a partial comparison.** On a model that follows `MODELING_GUIDE.md.template:108-112` (`sum(cells.capacity)` on the part, total passed on), every output downstream of the total and every verdict that reads it is "not compared". `compare` still exits 0 if any one value was compared. Required: exit 0 only when everything was compared and nothing differed; a distinct exit (for example 4: "nothing differs where compared; some items not compared") otherwise. Group not-compared items by the multiplicity that caused them, so the modeller sees which outputs went unchecked. Update invariant 1 and D6 to match, and move the coverage limit into the Core Concept. The workflow then says what to do on exit 4: record the list, and for an output the work relies on, check it another way or say it is unchecked. This removes the "record the counts" ritual, because the exit code carries the information. — Spec Compliance, Route Safety, Bets
- **M2. Native scope must be the effective usage, not the slot root.** The accessor (D2) must return `effective_usage_id` per occurrence step (`occurrence.py:1039-1050`), and the count check must read the bound from the effective usage's multiplicity. The spike used `containment_slot.root_declaration` (`probe_channels.py:43`), which is the base declaration a `part :>> x { … }` redefines. On dc3, which redefines every subsystem part, that would likely give false differences. If the generator ever ignored a redefinition the same way, it would give a false agreement. Add a test model: a specialised part def that redefines a contained part and an attribute value inside it (the `dc_facility.sysml` shape), checked for both value and count. — Abstraction Quality, Bets (H1)
- **M3. State and test the single-scope bet.** Add a bet: SysIDE, given only the innermost usage as scope, sees every redefinition that applies to the feature. Test it with a value redefined two levels out (an outer part redefining a value inside a nested part). If it fails, the generator can tell from its own redefinition index which features are redefined above the innermost scope, and those go to "not compared" with a new reason. Do not assume it holds. — Bets (H2)

### Major (should-fix)

- **S1. Compare per-index channels instead of dropping them.** Every index of one usage is built from the same declarations (`occurrence.py:1008-1062`; a named subset such as `rack_1 :> racks` is its own slot, not an index). At the model's own values each index must therefore equal SysIDE's single value. A per-index difference would be a generator wiring fault, which is what the command is for. Keep "not compared" only for channels that also depend on a multiplicity (B2). Also define "indexed" as "in a slot whose count is not 1", since `[1]` gets index 0 (`occurrence.py:918`). If the design keeps the exclusion, it must say what model could give different values per index in the generator's occurrence model. — Bets, Abstraction
- **S2. Make B2 concrete and include empty slots.** A method that needs only the instance graph's edges and scopes: mark every node that consumes a producer inside an indexed occurrence while itself sitting outside that occurrence's subtree, then take all downstream consumers. That replaces the vague fallback. Separately, treat a slot with zero occurrences as untrustworthy natively. This likely needs the expression's reference rather than an edge, because there is no producer to draw an edge from. Add a `[0]` test model. — Bets
- **S3. Close D10 and state the TEAx coupling.** Import simkit from the environment only, mirroring `study/verify.py:481-490` (no `TEAX_SIMKIT_PATH` handling inside `compare`; the study seam's `PYTHONPATH` work is for its subprocesses, `study/integrate.py:297-317`). The error message names both ways to provide it: declare `teax-simkit` in the project, or put a simkit root on `PYTHONPATH`. State that `compare` is the first production code to call `ProvisionalPackageLoader` and `execute_pipeline`, and record the TEAx revision and simkit path in the report header. — Pattern Consistency
- **S4. Handle `compare` on an older sysml-codegen.** The workflow text must map exit 2 with "invalid choice: 'compare'" to "not compared: sysml-codegen does not have `compare`; update it", so it is never read as a usage error to fix. Merge order (sysml-codegen first) does not cover target projects pinned to an older version. — Route Safety
- **S5. Align invariant 5 with the spec and Phase R.** Invariant 5 lists four behaviours. Spec criteria 3 and 5 allow a warning for each confirmed Risk 1 case, and Phase R plans warnings for the simple-name collision and the conditional-branch loss if confirmed. Reword: "the three limits, plus each behaviour confirmed in Phase R, each with a recorded run and an upstream row". — Spec Compliance
- **S6. Make the `min`/`max`/`product`/`size` test checkable, or drop it.** As worded ("names … as generator-accepted"), no text test can decide it, and a plain search for those names would fail on the native teaching sites that keep them. Either pin the D12 qualifier next to each teaching site (which already proves the criterion), or drop the test. — Ceremony check
- **S7. Complete the handoff.** Order the build: (1) de-risk B2, M2 and M3 together on the spike models plus a dc3-shaped model; (2) the accessor and the byte-identity check, with the corpus named (sysml-codegen test fixtures, the spike models, dc3 `models/`) and the comparison covering the whole generated tree including `contracts/`; (3) `compare` and its tests; (4) sysml-codegen merge (owner, RG-3); (5) agentic-mbse text and pins; (6) Phase R using `compare` itself where it exists; (7) Phase U. Also: branch the sysml-codegen work from `origin/main`; the spike's worktree is on `subset-profile-screen`. — Handoff

### Minor (consider)

- Exit 3 reason lines should separate "environment" from "package run failed". The workflow says the second is a finding to record and file (Route Safety).
- Define the per-item report line and the count check's unit (Data Structure Clarity).
- Fix D8's rationale: dc3's 2.38e-7 is absolute on ~1e9 values; the `--abs-tol` case is a near-zero true value (Bets).
- Say `compare` takes live `--models` only, not `--from-snapshot` (Pattern Consistency).
- The verdict join through `usage_qualified_name` and `owner_instance_path` is still untested in code. The design already sends it to the plan; keep it in the first test set.

---

## Recommendations

1. Change exit 0 to mean "everything compared, nothing differs", add a distinct exit for partial comparison, and group not-compared items by cause (M1).
2. Carry the effective usage per occurrence step in the accessor and use it as SysIDE's scope and as the source of the multiplicity bound (M2). Add the dc3-shaped redefinition test.
3. Add and test the single-scope bet (M3), and de-risk it in the same few hours as B2.
4. Compare per-index channels; define "indexed" as count ≠ 1; give B2 a concrete edge-based method plus an empty-slot rule (S1, S2).
5. Close D10 on "import from the environment, like `study verify`", state the TEAx coupling, and cover the older-sysml-codegen exit 2 in the workflow (S3, S4).
6. Align invariant 5, fix or drop the `min`/`max` test, and order the phases with a named byte-identity corpus (S5 to S7).

---

## Resolutions

Dispositions by the orchestrator, 2026-10-22 (execution detail); applied to `design.md` by the design agent the same day.

- **M1:** accepted. Exit 0 now means everything was compared and nothing differs. Exit 4 means nothing compared differs but some items were not compared; exit 1 takes precedence. Not-compared items are grouped by cause, such as "multiplicity `pack.cells` (3)" (design D5, D6, invariant 1). The tension is stated in the Core Concept: the guide's limit-3 advice (total over the parts with `sum`) produces outputs native SysIDE cannot check. The guidance says it in one place, the `MODELING_PROCESS` exit-4 text (D14), with one pointer sentence after the limit-3 advice. It is a fact about native SysIDE, not a generator rule. The modelling advice is unchanged, and advising named parts to suit the checker was rejected.
- **M2:** accepted. The accessor returns `effective_usage_id` per occurrence step. It is SysIDE's scope and the source of the count bound (D2, D7, bet B3). The dc3-shaped redefinition model is in Phase 1.
- **M3:** accepted. This is bet B4, with a two-levels-out test in Phase 1. Fallback: features redefined above the innermost scope are not compared, with the cause "redefined above scope".
- **S1:** partly accepted. Accepted: "indexed" means a slot whose count is not 1, so `[1]` parts compare. Not accepted: comparing per-index channels. SysML has no syntax to redefine one index directly. But a named subset (`part c1 :> cells { :>> capacity = 4.0; }`) gives one member of the collection its own value. The generator builds that subset as its own slot, and every index from shared declarations. So per-index generated values and SysIDE's per-definition value could agree on a wrong number. The spike's `packredef` probe did not settle this shape. Because a route exists, per-index items stay not compared. The argument is recorded in design D5.
- **S2:** accepted. B2 uses the concrete method (scope inside an occurrence of a slot with a count other than 1, plus everything downstream), plus a separate zero-occurrence mark from expression references. Phase 1 adds a `[0]` test model.
- **S3:** accepted. simkit is imported from the environment only, like `study/verify.py:481-490`. The message names both ways to provide it. The TEAx coupling is bet B6, and the report header records the revision and path (D10).
- **S4:** accepted. The workflow text maps exit 2 with "invalid choice: 'compare'" to "not compared: sysml-codegen does not have `compare`; update it" (D6, Component Overview).
- **S5:** accepted. Invariant 5 now covers the three limits plus each behaviour confirmed in Phase R.
- **S6:** accepted by dropping the `min`/`max`/`product`/`size` test. It cannot be decided mechanically, and the per-site qualifier pins prove the criterion (D15).
- **S7:** accepted. The build order is in Implementation Notes. Phase 1 de-risks B2, B3 (M2) and B4 (M3) together, with stop-and-report. The byte-identity corpus is named, and the comparison covers the whole generated tree (invariant 2). sysml-codegen work branches from `origin/main`.
- **Minors:** all accepted. Exit 3 reasons are prefixed `environment:` or `package run failed:`. The per-item line and the count check's unit are defined (D12, D7). D8's `--abs-tol` rationale is corrected. `--models` only (D11). The verdict join is in the first test set.
- **dc3 premise:** corrected in the design. dc3 names parts as subsets and has no `sum`, so most of its values should compare. The uncompared-headline case applies to new projects following limit 3. The Validation Approach adds a run on dc3 `models/` to record the actual share compared.

---

**Overall:** Revise
**Next Steps:** Once resolutions are recorded, re-run `/_my_design` (or return to the design-agent session) and point it at this review to incorporate. The reviewer does not edit the design. M1 changes the shipped workflow text as well as the command, so the design's agentic-mbse component list must change with it.
