# Spike: Item 3 de-risk checks (contract on real trees, advisory shapes, String IDs, roots, codegen citations)

**Date:** 2026-10-18. **Branch:** `l6-subset-profile`. Probes ran against `src/` at `00e2b202` (`src/` clean; `ab3b44de`, which landed during the spike, changes only `.project/`). SysIDE 0.8.4. Serves `design.md` Next-Stage Handoff S1, S2, S3, F4, F5.

## Summary of Findings

**Blocking check S1 passes: nothing raises on any of the three trees.** The contract and both advisory walkers ran cleanly on fusion-tea `f96ad312`, dc3 `808464d` and dc3 `60b44d5`. dc3 baseline counts equal Item 1's exactly. But two things in the results bear on the design:

- **The contract is slow on fusion-tea: about 226 s, almost all of it in `extract_subset_facts`.** Measured twice (225 s under load, 226 s alone). dc3 takes 14-20 s. Bet B1 says "cleanly and quickly"; it is clean, not quick. Every fusion-tea `validate` would gain about four minutes. About 201 s of it is a single loop in Item 1's constraint extractor that scales as constraint usages × context features (`constraint_extraction.py:879`); see the profile section.
- **fusion-tea's L6 already fails today** (408 issues, exit 1), as does dc3 baseline (11 issues). So the risk "fusion-tea L6 flips pass→fail under unset" cannot happen at the L6 level. Only dc3 `60b44d5` passes L6 today, and the contract gives it `clear`.

Per tree (contract with default generator roots):

| Tree | Raises? | Extract time | Verdict | refused | unconfirmed | omitted | excluded | admitted | unverified | unassessed | L6 today |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fusion-tea `f96ad312` | no | 226 s | `clear` | 0 | 0 | 131 | 0 | 0 | 0 | 0 | fail (408 issues) |
| dc3 `808464d` | no | 20 s | `refused_incomplete` | 236 | 6 | 32 | 0 | 0 | 50 | 0 | fail (11 issues) |
| dc3 `60b44d5` | no | 14 s | `clear` | 0 | 0 | 30 | 0 | 15 | 0 | 0 | pass |

dc3 baseline's 50 unverified checks have two causes, both "valid SysML the subset does not support" or a missing reference target, never a crash: 22 `binding-source` and 22 `indexed-reference` from `SequenceFunctions::size(...)` bindings (`EXPRESSION_KIND_UNSUPPORTED`), 1 `indexed-reference` from `NumericalFunctions::product` (`EXPRESSION_KIND_UNSUPPORTED`), and 5 `indexed-reference` with `RESOLVED_TARGET_MISSING` ("resolved reference has no exact target"). The 22 `size` bindings also appear as 22 fact failures (`binding_source`).

**S2, advisory shapes: both advisories can be made to fire, and both walkers also raise on valid input.**

- **WRAPPER-SHAPE fires** on load-clean models. Examples: `sum(cells.mass->collect { in m : Real; m * 2.0 })` and `sum(cells.{ in c : Cell; c.mass })` (wrapper `collect`), `sum(cells.mass->select { ... })` (`select`), `sum(abs(cells.mass))` (`abs`), and `sum((cells.mass, 1.0))` (`[`). It does not fire on `sum(cells.mass)`. Any invocation directly inside `sum`, not just the four known wrappers, fires it.
- **UNSUPPORTED-SHAPE-MESSAGE fires** (the walker reaches `return str(expr_node)` at `expression.py:356`) on `new Cell()` (`ConstructorExpression`, load-clean). It also fires on calls SysIDE cannot resolve, such as `notAFunction(1.0)` or `Evaluation(...)`, but those models already have load errors. It does not fire on `if`, `as`, `#()`, `??`, `istype`, `@`, `all`, `*`, string `+`, or a call of a calc usage.
- **The walkers raise `SemanticEvidenceError` on some load-clean models.** `decompose_aggregation_expression` raises on `sum` over a chain rooted in a select (`sum(cells.?{ in c : Cell; c.ok }.mass)`, `sum(cells->select { ... }.mass)`): "feature chain rooted in an unsupported expression kind". `reconstruct_expression` raises on `Cell.metadata`: "SysIDE could not materialize the expression operands". Under design D4 and I1, each would become `L6_CHECK_ERROR`, an ERROR under every target, on a model with no load errors. The spec caps an advisory at WARNING. **This conflicts with a recorded rule, so it is surfaced here, not resolved** (see Open Questions).
- On the three real trees, neither advisory fires and neither walker raises. fusion-tea has no `sum` sites; dc3 baseline has 4, none wrapped.

**S3, String ID match: confirmed wherever both checks see the attribute, but on dc3 `60b44d5` the legacy check flags no String at all.**

- Two-spelling fixture under `designs/` (`attribute label : String = "north";` and `attribute :>> kind = "liquid";`): the legacy check flags both, and both ids equal the contract's `string-value-omission` subject ids (2 of 2).
- dc3 `808464d`: the legacy check flags 3 Strings; all 3 ids equal contract subject ids. The other 29 String findings are not flagged by the legacy check.
- dc3 `60b44d5`: the legacy check flags 0 Strings; the contract has 30. All 30 are the bare shorthand `:>> name = "..."`, which SysIDE makes a `ReferenceUsage`. The legacy check only lists `AttributeUsage` (`level6_architecture.py:501`), so it never sees them. The spike's premise (a legacy String flag to compare on `60b44d5`) does not hold there. The comparison was made on `808464d` and the fixture instead.
- fusion-tea: the legacy check flags 108 attributes, all typed `ScalarValues::Real` with reference or operator values; none is a String. The contract's 131 String findings are all unflagged by the legacy check. So no tree has a String the legacy check flags and the contract misses. That is evidence for design-review hidden bet H1 on these trees, not a proof for all positions.
- Consequence for D10: suppression removes 3 legacy ERRORs on dc3 baseline and nothing elsewhere. The String findings mostly add new WARNINGs under unset where L6 said nothing before: 131 on fusion-tea, 30 on `60b44d5`.

**F5, roots and settings: no surprise.** For every tree, `find_project_root(start=<tree>/models)` returns the tree's own root, which holds all three markers (`work/BACKLOG.md`, `.agentic-mbse/install.json`, `.claude/`). The extraction parent under `/tmp` resolves to no root. No `pyproject.toml` has `[tool.agentic-mbse]` or `[tool.agentic_mbse]`. The `[tool]` tables are `mypy, pytest, ruff, uv` (fusion-tea) and `pytest, ruff, uv` (both dc3 revisions).

**F4, codegen citations: most of Appendix A's "generator-only" causes do not hold at `b5663c07`.** Full table in `f4-codegen-citations.md`. Codegen now builds an instance graph (`elaboration/elaborate.py`, `elaboration/project.py`). `hierarchy_resolver`, `usage_extractor` and `computed_attribute_extractor.py` are deleted. Of the nine "generator-only if shown" rows:

- Confirmed: `L6_ANONYMOUS_RETURN` (codegen V8, `extraction/extractor.py:191-215`) and `L6_BODY_ASSIGNMENT_IMPL_LOSS` (`extractor.py:249-264`, `expression_compiler.py:265-274`).
- Confirmed with a caveat: `L6_CALC_DEF_NO_INSTANTIATION` (`elaborate.py:771-777`; a native route would have no instances either). `L6_MISSING_QUALIFIED_NAME` is confirmed only weakly: codegen needs the name for graph identity (`elaboration/identity.py:71-76`), not for EQN.
- Partial: `V4_STATIC_FUNCTION_INVOCATION` and `L6_DESIGN_ATTR_UNEXTRACTABLE` (other). Codegen refuses calls other than `sum` (`project.py:806-810`). It accepts references, `^` and `sum`, which these checks flag.
- Not generator-only: `L6_INVALID_QUALIFIED_NAME` (codegen sanitizes names), `L6_INVALID_BINDING_FORMAT` (bindings resolve by element identity), and `L6_ATTR_REDEF_EXPR_DROPPED` (the cited scan is deleted; the current scan at `elaborate.py:832-898` treats both spellings alike).
- The two "kept unless shown" rows stay kept. Codegen accepts a valueless design attribute (`project.py:565-579`). The non-numerical exclusion comes from agentic's shared profile (`elaborate.py:296`).

So under the design's rule ("a row without evidence keeps today's severity"), at most 4 rows can be lowered under `native`. The three "not generator-only" rows are a different case: under unset and `generated` they are ERRORs on shapes the generator accepts. The design has no category for that, so it is surfaced below. Of the 12 codegen citations in agentic-mbse L6 code and messages, 3 are accurate (alias wiring at `level6_architecture.py:533`, V8 at `:583-584`, auto-impl loss at `:771`). The rest are stale, partly true, or not codegen citations (listed in `f4-codegen-citations.md`).

## Question / Goal

The design (`design.md` Next-Stage Handoff) asked for these checks before building:

1. **S1 (blocking).** Do `extract_subset_facts` + `evaluate_subset_profile` and the two advisory walkers run without raising on fusion-tea `f96ad312`, dc3 `808464d` and dc3 `60b44d5`? Do dc3 counts equal Item 1's (236 / 32 / 6 / 50)? A raise on any tree disproves bet B1.
2. **S2.** Is there a SysML expression that fires each advisory (UNSUPPORTED-SHAPE-MESSAGE through `reconstruct_expression`'s `str(node)` branch; WRAPPER-SHAPE through `decompose_aggregation_expression(...).wrappers`)?
3. **S3.** Does the element id of an attribute that the legacy `L6_DESIGN_ATTR_UNEXTRACTABLE` check flags equal the contract's String finding subject id, on dc3 `60b44d5`? D10 depends on it.
4. **F5.** Which project root does `find_project_root` resolve in each archived tree, and does its `pyproject.toml` already have `[tool.agentic-mbse]`?
5. **F4.** Does each codegen citation and "generator-only" claim in Appendix A hold at sysml-codegen `b5663c07`?

## Log

All probes are throwaway scripts in this folder. Sibling repos were only read with `git archive`. Every export checks `git get-tar-commit-id` against the full commit and extracts with `tarfile`'s `data` filter. Absolute symlinks are skipped and listed (fusion-tea has 64: 27 under `exploration/`, 23 under `work/`, 13 under `.project/`, 1 under `archive/`; none under `models/`, where one would abort the export). `s1_trees.py` records each sibling's `HEAD` and `git status --porcelain` before and after; all three were unchanged.

1. **`s1_trees.py` (S1, S2 on trees, S3, F5).** For each tree, it exports into a `TemporaryDirectory` under `/tmp`, records the root and settings, loads `models/**/*.sysml`, and times and wraps (catching any exception with its traceback) `load_model`, `extract_subset_facts`, `evaluate_subset_profile`, the String ID comparison and the advisory walkers. The advisory walkers run over the contract's own expression sites (`subset_extraction._site_candidates`). Opaque detection uses a line tracer on `reconstruct_expression`'s `return str(expr_node)` line (`expression.py:356`), so the walker's own dispatch decides; no second classifier. Wrapper detection calls `decompose_aggregation_expression` on sites whose tree invokes `sum` and reads `.wrappers`. The String comparison wraps `level6_architecture.evaluate_true_static_expression` to record which attribute each legacy flag came from (keyed by the value expression's element id), runs `check_design_attr_completeness(model, "designs")`, and compares ids. Output: `s1-results.json`, log `s1-run.log`, compact view `s1_summarize.py`.
   - First run: killed and rerun after adding progress output. A field-name bug in the spike (`WrapperFact.context` instead of `.reason`) was fixed before the recorded run.
   - Recorded run: no exception at any stage on any tree (table above).
   - fusion-tea re-timed alone (`s1-fusion-retime.log`): extract 226.36 s, same results.
2. **`s2_advisory_shapes.py` (S2).** It writes 27 one-line candidates into a small package (`P::Pack` with `cells : Cell[3]`) and runs the same walkers. Output: `s2-run.log`. Results are in the summary.
3. **`s3_string_ids.py` (S3).** This ran the two-spelling fixture and, on dc3 `60b44d5` and `808464d`, accounted for every String finding: metatype, whether the legacy loop iterates it, whether it is in `designs/`, whether it is an EXPOSE binding, and the static evaluation result. Output: `s3-run.log`. Every dc3 `60b44d5` String is a `ReferenceUsage` the legacy loop never iterates. Static evaluation would raise on all of them.
4. **`s3b_legacy_flag_types.py` (S3 / hidden bet H1).** This printed the declared types and value kinds of every legacy-flagged attribute. Output: `s3b-run.log`. fusion-tea: 108, all `Real`, values 61 `FeatureChainExpression`, 28 `FeatureReferenceExpression`, 19 `OperatorExpression` (messages: "Feature reference ... violates ADR-002 Rule 3"). dc3 baseline: 3, all `String` literals. dc3 repaired: 0.
5. **`s4_l6_today.sh` (context for B1 and the flip risk).** This ran today's `validate --level=6 models` from this checkout in each exported tree. Output: `s4-run.log`. fusion-tea fails (408 issues), dc3 baseline fails (11), dc3 repaired passes.
6. **F4.** sysml-codegen `b5663c07` was exported to `/tmp/l6-spike-codegen` (`git get-tar-commit-id` = `b5663c07e987a892e27d21e68cec40d0656574ee`) and read with grep and sed only; nothing ran in it or in `~/src/sysml-codegen`. A subagent read the rows. Four claims were spot-checked by hand. Output: `f4-codegen-citations.md`.
7. **`s1b_profile_fusion.py` (S1 timing).** This ran `extract_subset_facts` on fusion-tea under cProfile. Output: `s1b-profile.log`. See the profile section.

## Profile of fusion-tea extraction

`s1b-profile.log`: 214 s under cProfile, of which **about 201 s is one generator expression**, `constraint_extraction.py:879`, inside `_inherited_into` (`:873-882`). For each of fusion-tea's 345 constraint usages, it walks every candidate context's whole `features` list, testing `feature is constraint`. That is 34,099,251 iterations: the cost is the number of constraint usages times the total features across contexts. Everything else in extraction takes about 13 s (constraint contexts 5.4 s, the other fact kinds 3.3 s, occurrences 1.2 s).

So the slowness has one cause in Item 1's constraint extractor, not in the contract or L6. One way to fix it is to build the feature → contexts map once per extraction. That is a library change shared with the contract's inputs. Whether and where to make it is for the design (see Open Questions 3). The spike changed nothing in `src/`.

## Reproduction

From the agentic-mbse root, with `SYSIDE_LICENSE_KEY` in `.env` and `~/src/fusion-tea`, `~/src/dc3` and `~/src/sysml-codegen` holding the pinned commits:

```bash
D=.project/active/l6-subset-profile/spikes
uv run python $D/s1_trees.py --out $D/s1-results.json > $D/s1-run.log 2>&1   # ~5 min
python3 $D/s1_summarize.py $D/s1-results.json
uv run python $D/s2_advisory_shapes.py > $D/s2-run.log 2>&1
uv run python $D/s3_string_ids.py > $D/s3-run.log 2>&1
uv run python $D/s3b_legacy_flag_types.py > $D/s3b-run.log 2>&1
bash $D/s4_l6_today.sh > $D/s4-run.log 2>&1
uv run python $D/s1b_profile_fusion.py > $D/s1b-profile.log 2>&1        # ~4 min
# F4: export codegen and read it (no execution)
git -C ~/src/sysml-codegen archive b5663c07 > /tmp/l6-spike-codegen.tar
git get-tar-commit-id < /tmp/l6-spike-codegen.tar
python3 -I -c "import tarfile,os; tarfile.open('/tmp/l6-spike-codegen.tar').extractall('/tmp/l6-spike-codegen', filter=lambda m,p: None if m.issym() and os.path.isabs(m.linkname) else tarfile.data_filter(m,p))"
```

Expected: the table in the Summary. Timings vary with machine load. Temp paths (`/tmp/l6-spike-*`) differ per run and appear in locations inside `s1-results.json`.

## Open Questions / Follow-ups

These are surfaced for the design agent and owner, not resolved here.

1. **Advisory walker failures on valid models vs. I1 (premise conflict).** I1 and D4 turn every failed inspection into `L6_CHECK_ERROR` (ERROR, every target). The advisory walkers raise `SemanticEvidenceError` on load-clean shapes (`sum(cells.?{...}.mass)`, `Cell.metadata`). Following I1 would make a WARNING-at-most advisory fail L6 on a valid model. One option is to treat a walker's own "unsupported kind" signal (a `SemanticEvidenceError`) as "advisory could not inspect this site", shown at advisory severity. Any other exception would stay a check error. That needs an owner or design decision, because R3-2 says a broken check never passes. None of the three real trees hits this today.
2. **Legacy rows that are not generator-only and not the project's own rule.** `L6_INVALID_QUALIFIED_NAME`, `L6_INVALID_BINDING_FORMAT` and `L6_ATTR_REDEF_EXPR_DROPPED` (and part of `V4_STATIC_FUNCTION_INVOCATION` and UNEXTRACTABLE "other") are ERRORs, or WARNINGs for V4 and REDEF, under every target, for shapes codegen at `b5663c07` accepts. The design's categories only allow "keep" or "lower under native". Whether to keep them, retire them, or reclassify them is outside this spike. The 108 fusion-tea UNEXTRACTABLE flags (Real references) are this case.
3. **fusion-tea extraction time (B1).** About 226 s per run. Whether that is acceptable for `validate`, or needs a fix in extraction before Item 3 ships, is a decision. The profile names the hot path: `_inherited_into` at `constraint_extraction.py:873-882`. Fixing it is a change to a library file the contract reads, so it touches I4's "library changes only add" and possibly the Item 2 agent's surface.
4. **Wrapper advisory breadth.** `.wrappers` records any invocation directly under `sum` (`abs`, the sequence operator `[`), not just `Evaluation`/`evaluate`/`collect`/`select`. The advisory's wording should match, or it should filter to `KNOWN_WRAPPER_FUNCTIONS` (`aggregation.py:72`).
5. **Not checked.** The full `validate --complete` before/after (that is the Appendix C safeguard's job). Advisory firing through the reviewed "pure predicate" mechanism (design-review M1): the spike traced the existing function and changed nothing. Whether a String attribute outside every generator root is still an `omitted` subject (design-review H1 test). All F4 verdicts come from reading, not running.
