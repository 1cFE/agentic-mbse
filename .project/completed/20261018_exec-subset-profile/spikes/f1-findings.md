# Spike: F1 — occurrence-port parity (EXEC-SUBSET-CONTRACT Item 1)

**Date:** 2026-10-15
**Branch:** `exec-subset-profile` (spike written on top of `e73cf61e`; the port imports agentic-mbse `src/` at `9d8a3a3e`, which matches the design base `a718efec` exactly)
**Pins (read-only, exported with `git archive`):** sysml-codegen `b5663c07e987a892e27d21e68cec40d0656574ee`; dc3 `808464d` (baseline), `60b44d5` (repaired)
**Upstream:** [design.md](../design.md) Appendix D flags F1 and F2, Key Bets B1, B2 and B4, and R1's cost line. Brief: [briefs/spike-f1.md](../briefs/spike-f1.md). The concurrent [design-review.md](../design-review.md) asked F1 to cover the occurrence-build aborts too (S4, H3), so it does.

## Summary of Findings

**Verdict: confirmed.** The occurrence facts the design needs can be read from SysIDE before elaboration, inside agentic-mbse, and they match codegen `b5663c07` exactly. Each case is checked on criteria (a)–(e). It is also checked on codegen's first refusal and on whole-model aborts. **72 of 72 cases match, with zero mismatches.** The port is **416 physical lines (333 lines of code)**, under the design's ~800-line re-weigh threshold. On parity and size, F1 gives no reason to re-weigh R1.

That size covers the **summary port the design describes**: roots, occurrences, counts, which part defs have occurrences, the winning calc usage per scope, and the multiplicity class. The design review's M2 asks for something different, a near-verbatim *module* port that Item 2 can swap in. That would add containment addresses, `consumer_domain` and `resolve_address`. **I did not build or measure that.** My estimate is roughly 600–1,000 lines, depending on how much of codegen's diagnostic plumbing comes along. Whoever decides R1 should use 416 lines for the summary port only.

**Per-corpus results** (a case is one `generate --models` input; counts are codegen's own, summed over the cases):

| Corpus | Cases | Match | Roots | Occurrences | Calc writers (scope, winner) | Unexpandable (usage, parent) | Codegen full graph agreed |
|---|---:|---:|---:|---:|---:|---:|---:|
| Prototype fixtures (`01-fixtures/`) | 22 | 22 | 26 | 30 | 18 | 2 | 16 of 16 that elaborate |
| Codegen corpus, captured snapshots (14) | 14 | 14 | 15 | 38 | 23 | 0 | 14 of 14 |
| Codegen corpus, the other 23 (extra) | 23 | 23 | 46 | 165 | 155 | 0 | 21 of 21 that elaborate |
| dc3 baseline `808464d` + repaired `60b44d5` | 2 | 2 | 14 | 367 | 81 | 72 (all `UNRESOLVED`, baseline) | 1 of 1 (repaired) |
| New edge fixtures (`f1-occurrence-port/fixtures/`) | 11 | 11 | 17 | 45 | 13 | 5 | 2 of 2 that elaborate |
| **Total** | **72** | **72** | | | | | **54 of 54** |

**Mismatches: none.** No case needed a fix to the port after its first full run. The only changes made after the first run were to the harness and the fixtures:

- A pipefail bug in the driver.
- An oracle cross-check that had counted computed-attribute nodes as calc usages.
- Fixtures I rewrote because SysIDE refused to load them.

The [Log](#log) records each one.

**How the comparison was kept honest:**

- **The oracle is codegen's own code.** It calls codegen's functions on codegen's own data structures, with one patch: a multiplicity refusal is recorded and the build continues, instead of aborting. The unpatched build also runs, and its first error is compared separately.
- **The oracle was checked against codegen's real pipeline.** Wherever codegen's `elaborate_model_paths` completes (54 cases), the oracle's occurrences and calc nodes equal the real instance graph. That also confirms the review's H3 for these corpora: the port's model load (`SysideAdapter.load_model`) yields the same population as codegen's loader.
- **Deliberately wrong ports are caught.** Each mutant below is a deliberately wrong port run through the same comparison:

  | Mutant | What it gets wrong | Cases flagged |
  |---|---|---|
  | `typed_anywhere` | The prototype's "typed anywhere" rule for "has occurrences" | 32 of 72 |
  | `writer_is_base` | The spec's literal reading: always classify the base calc usage | 2 of 72 |
  | `no_effective_decl` | Skips redefinition-slot selection | 1 of 72 |
  | `declared_multiplicity` | Reads the prototype's attribute instead of `multiplicity` | 0 of 72 (explained under Surprises, item 1) |

**What the controls say about coverage.** The real corpora barely exercise redefinition-dependent selection. Only dc3 repaired catches `no_effective_decl`. Only `retype_model` and one new edge fixture catch `writer_is_base`. Parity on these paths therefore rests mostly on the new edge fixtures. The parity test Item 1 ships should keep those fixtures, not just the corpora.

**Criteria (a)–(e), all identical on every case:**

- (a) The root set.
- (b) Every occurrence, by its full path (slot and index at each level), with its usage, effective type, type closure and child declarations. Counts are compared per parent occurrence, not per root, which answers the review's S4 granularity point. `Site::racks` gets 4, 2 and 2 under three different parents in `f1_referenced_bounds`, and the port matches.
- (c) Occurrence count, and has/has-not, for every part definition.
- (d) The selected calc usage for every (slot, scope), including calc usages redefined in every scope (`f1_calc_redefined_everywhere`: `Base::c` is never the winner), plus each calc usage's attached scopes.
- (e) For every unexpandable (usage, parent), the port's neutral class maps to codegen's `SI_MULTIPLICITY_*` code.

Whole-model aborts also match. The cases are an unrelated redefinition-root family, recursive containment, a specialization cycle and incomparable typings. Each matches on the stage and on the mapped code.

**Codegen dependencies that neutral facts cannot reproduce: none for (a)–(e).** The port imports only `agentic_mbse` (the `SysideAdapter` and `evaluate_true_static_expression`). It asserts at exit that `sysml_codegen` was never imported. Codegen's identity rule (QN-bearing UUIDv5) is one line to reproduce. It left out only what codegen uses for messages: display names, `written_reference_text` and `authored_site`, plus the `ElaborationCode` enum. A ten-line table in `compare.py` maps the neutral classes to `SI_*` codes.

**Surprises (surfaced, not resolved):**

1. **The design's multiplicity premise is wrong for SysIDE 0.8.4, though the port is unaffected.**
   - What the design says: the Research Findings line says `usage.multiplicity` is "own or inherited from supertypes". It calls the prototype's `declared_multiplicity` "a different attribute". B4, Implementation Note (c) and F2 build on that.
   - What the run shows: on every part and attribute usage in all 72 cases, `multiplicity` and `declared_multiplicity` return the same element. That includes 66–67 redefinitions without their own bounds in each dc3 tree.
   - Neither attribute is inherited through `:>>`, and neither is `is_ordered`. Example: `part :>> racks;` redefining `racks : Rack[2] ordered` reads multiplicity `None`, ordered `False` (`results/probe_multiplicity_attrs.log`).
   - The port reads `multiplicity`, as codegen does, so parity holds either way. But the design text that rests on this premise should be corrected rather than carried into the plan.
2. **Codegen does things the port reproduces faithfully, so the contract will report them too.** Neither is an R2 risk, because the contract follows the generator. Both are generator-correctness questions for the owner or Item 2:
   - (a) A part redefinition that omits bounds expands to **one** occurrence, and it loses `ordered`. `site : BigSite` with `part :>> racks;` over `Rack[2] ordered` gets a single, admitted `racks`, so ES-004's `ordered` shape cannot be reached through inheritance. Neither dc3 tree contains this shape (`results/probe_redef_drops_bounds.log` is empty).
   - (b) A usage-level override of a definition-owned referenced bound is ignored. In `f1_referenced_bounds`, `tuned : Site { attribute :>> n default 3; }` gets 2 racks, not 3. The cause: `_modeled_integer_bound` (`occurrence.py:726-763`) looks only at definition-owned writers when the multiplicity's owner is a part def.
3. **The port breaks agentic-mbse's selector-ownership gate as written.** It reads raw `referent` (the referenced bound) and `chaining_features` (the redefined endpoint), exactly as codegen does (`occurrence.py:399`, `:708`). `tests/test_sysml/test_semantic_selector_ownership.py` allows those reads only in `reference_use.py` and `syside_adapter.py`. The production port needs two small accessors there. This lands in agentic-mbse code, alongside the codegen ADR 0012 ownership point the review raised (M1).
4. **On dc3 baseline, the generator never reports the multiplicity refusals.** Codegen builds the expression inventory before any occurrence work (`orchestration/elaborated_pipeline.py:272-278`). So dc3 baseline's real run refuses on `product(efficiencies_in)` (`SI_EXPRESSION_SOURCE_UNSUPPORTED`), and its 72 unexpandable multiplicities never surface. The occurrence facts still find all 72. This fits the review's S2 "counterfactual" framing, and it is one more reason a probe must be single-construct.

**Production size estimate (summary port, not measured):** about 470 lines of code. That is the 333 here, plus about 60 for the neutral fact types, about 30 for the closed failure vocabulary and safe locations, about 25 for D7's caller-supplied roots (not ported here) and about 15 for the two gate accessors. It comes to roughly 600 physical lines with docstrings.

**Package versions used:** sysml-codegen 0.1.1 (`b5663c07`, verified with `git get-tar-commit-id`), agentic-mbse 0.1.3 (exported at `9d8a3a3e`, with `src/` identical to `a718efec`), syside 0.8.4, Python 3.12.3. Codegen's `uv.lock` sha256 is `a17e9fa1…4d4`, synced with `uv sync --frozen`. Both packages resolved inside `/tmp/f1spike`, and the run asserts this (`results/identity.json`). `SYSIDE_LICENSE_KEY` came from agentic-mbse `.env`; its value is not recorded.

## Question / Goal

**Assumption under test:** a port inside agentic-mbse can compute the occurrence facts the contract needs, before elaboration, and match codegen `b5663c07` exactly, at about 500 lines. Those facts are:

- Generator roots.
- Instantiated part occurrences, with counts.
- Which part defs have occurrences.
- The winning calc usage per scope.
- The multiplicity resolution class.

**Confirmed if:** criteria (a)–(e) from design Appendix D F1 are identical on the 22 prototype fixtures, the 14 snapshot fixtures and both dc3 trees, and the port stays at or under about 800 lines.

**Disproved if:** any mismatch appears, or the port goes past about 800 lines. Either result would mean R1 gets re-weighed.

## Log

1. **Read the code.** I read codegen `occurrence.py` (all 1,053 lines) and `elaborate.py` (`_attachment` :759-787, `_select_writer` :901-952, `_build_calculation_nodes` :1195-1233), both at `b5663c07`. Fact: `build_occurrence_index` fails fast on the first multiplicity raise. A per-usage criterion (e) therefore needs an oracle that records each raise and keeps going.
2. **Isolated tree.** `git archive` exports of codegen `b5663c07`, agentic-mbse `9d8a3a3e` and dc3 `808464d`/`60b44d5` went into `/tmp/f1spike`, followed by `uv sync --frozen` in the codegen export. The first identity check failed because no license was in the environment; sourcing `.env` fixed it.
3. **Oracle (`oracle.py`).** It runs in the codegen venv and calls codegen's functions directly. To get per-usage multiplicity answers, it wraps the module-level `_multiplicity_indices`: a `MultiplicityExpansionError` is recorded and returns `()`. To get the writer selection, it builds a bare `_ExactElaborator` that carries only the slot and occurrence indexes, and records calls to `_select_writer`. A sentinel on `_typed_definition` stops the run after the selection loop; that loop completes before the call. The unpatched build is also run, to capture the strict first error. The smoke test on `es004_admitted_exact_redefinition` agreed with the full graph.
4. **Port (`occurrence_port.py`).** It is a function-by-function mirror (the module docstring maps each function to its codegen lines). It returns neutral multiplicity classes and raises a `FactFailure` with a neutral cause. `port_run.py` emits the oracle's JSON schema and asserts that `sysml_codegen` was never imported.
5. **Edge fixtures, first pass.** Four of the seven failed to load in SysIDE. The causes were `feature-value-overriding` (`= v` redefined), a nonunique part subsetting a unique feature, and a Real bound. I rewrote them as valid models using `default`, unbound inputs and `ordered`. The fixture with unrelated redefinition roots was kept on purpose, as an abort case; it still has a load error. Result: 7 of 7 matched.
6. **First full run.** The driver died after writing the identity file: `git archive | git get-tar-commit-id` hits SIGPIPE under `pipefail`. Fixed with `|| true`. The second run gave 68 of 68 matches.
7. **Oracle self-check.** On 6 cases, codegen's full graph `calcs` disagreed with the oracle. The cause: `graph.calcs` also holds computed-attribute nodes, keyed by slot (`elaborate.py:1023`). I filtered to `NodeId.declaration` that is not a `FeatureSlotId`. After that, the full graph agreed on every case where elaboration ran.
8. **Controls (`mutants.py`, `controls.sh`).** Three of the four mutants were caught. `declared_multiplicity` was not, so I probed it (`probe_multiplicity_attrs.py`, `probe_multiplicity_identity.py`): the two attributes are the same element everywhere, and neither inherits through `:>>`. That is Surprise 1. `probe_redef_drops_bounds.py` found no dropped-bound part redefinitions in either dc3 tree.
9. **Pipeline order.** Reading `elaborated_pipeline.py:261-288` confirmed that the inventory runs before the elaborator. That explains dc3 baseline's observed code (Surprise 4).
10. **Review follow-ups.** `e73cf61e` landed mid-spike and asks F1 to cover the occurrence aborts. I added `f1_abort_recursive_containment`, `f1_abort_incomparable_typings` and `f1_abort_specialization_cycle`, all of which match. The per-parent count check is in step 11.
11. **Final run: 72 of 72 match** (`results/run_all.stdout.log`, `results/summary.json`). Controls: `typed_anywhere` 40/72, `writer_is_base` 70/72, `no_effective_decl` 71/72, `declared_multiplicity` 72/72 (`results/controls.log`). The per-parent counts for `Site::racks` are 4, 2 and 2, which is Surprise 2(b). Wall time is about 70 seconds for the whole parity run.

## Reproduction

Everything is in `.project/active/exec-subset-profile/spikes/f1-occurrence-port/`:

- `occurrence_port.py`: the port.
- `oracle.py`: codegen's answers.
- `port_run.py`: the port's answers.
- `compare.py`: criterion-by-criterion comparison.
- `run_all.sh`: driver.
- `mutants.py` and `controls.sh`: negative controls.
- `probe_*.py`: the SysIDE learning probes.
- `fixtures/`: the 11 new edge fixtures.
- `results/`: the last run, including per-case JSON, `summary.json`, `identity.json` and the logs. `results-controls/*/compare.log` holds the controls' output.

```bash
cd .project/active/exec-subset-profile/spikes/f1-occurrence-port
./run_all.sh --setup      # exports pins into /tmp/f1spike, uv sync --frozen, runs all cases (~1 min after sync)
./controls.sh             # needs results/ from run_all.sh
# expected: last line of results/run_all.stdout.log = "TOTAL 72/72 match"
# expected controls: declared_multiplicity 72/72, no_effective_decl 71/72, writer_is_base 70/72, typed_anywhere 40/72
```

Requirements:

- `~/src/sysml-codegen` and `~/src/dc3` must contain the pinned commits. They are only read, through `git archive`.
- agentic-mbse `.env` must hold `SYSIDE_LICENSE_KEY`.
- `uv` must be on the path.

`F1_TMP` overrides the temp root, and `AGENTIC_REV` overrides the exported agentic-mbse revision.

## Open Questions / Follow-ups

- **R1 cost line.** The summary port measured 416 lines (333 of code) with no mismatches. The review's module-port alternative (M2) was not measured. If the owner prefers it, a follow-up spike should move `occurrence.py` near-verbatim with neutral errors and rerun this same harness against it. The harness is independent of how the port is shaped.
- **Design text to correct:** the multiplicity-inheritance premise (Research Findings "Multiplicity", B4's example, Implementation Note (c), F2). In SysIDE 0.8.4, `multiplicity` and `declared_multiplicity` are the same element, and neither inherits through `:>>`.
- **Generator-correctness questions for the owner or Item 2, outside F1:**
  - A redefinition that drops bounds yields one unordered occurrence.
  - A usage-level override of a definition-owned bound is ignored.
  - The contract will mirror both while codegen does.
- **Not covered here:**
  - D7's caller-supplied extra roots.
  - Attribute value-writer selection (`_build_value_nodes`), which ES-002/008/009 might need later.
  - Containment addresses and `resolve_address`.
  - Constraint-owner attachment beyond the shared `_attachment`. It is the same function, but only calc owners were compared.
- **The ownership-gate accessors** for `referent` and `chaining_features` are a plan item. They are not a spike result.
- **The parity test should carry the edge fixtures.** The real corpora alone would let a wrong effective-declaration or writer rule pass on 70 or more of the 72 cases.
