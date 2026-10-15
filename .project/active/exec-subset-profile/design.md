# Design: Executable-subset capability contract (EXEC-SUBSET-CONTRACT Item 1)

**Status:** Draft — awaiting design review, then **owner gate R1** (§ R1 below is a recommendation, not a decision)
**Owner:** Reid Westwood
**Created:** 2026-10-15
**Branch / base:** `exec-subset-profile` at `a718efec`
**Pins (read-only):** sysml-codegen `b5663c07e987a892e27d21e68cec40d0656574ee`; dc3 `808464df…` (baseline), `60b44d53…` (repaired); SysIDE 0.8.4

## Overview

Item 1 builds one declared contract of which (shape, context) pairs the pinned generator refuses, admits, excludes or omits. It has four parts: neutral facts extracted once from SysIDE, a pure evaluator that turns facts into outcomes, packaged rule records that carry the outcome for each (shape, context) pair together with its evidence, and an inventory (site account plus matrix) that accounts for every refusal site. No consumer is wired.

## Related Artifacts

- Spec: [spec.md](spec.md) (revised after review); review and resolutions: [spec-review.md](spec-review.md); align record and owner gates R1–R3: [briefs/align.md](briefs/align.md); product lens: [product-lens.md](product-lens.md)
- Epic: [epic_executable-subset-contract.md](../../backlog/epic_executable-subset-contract.md) (Item 1; boundaries with Items 2–5; D1–D3)
- Prototype (feasibility only): `.project/concepts/convince-me-exec-subset/evidence/` (`01-codegen-oracle.py`, `01-screen.py`, `02-inventory.py`, `01-fixtures/`)
- Decision records: agentic-mbse `.project/adr/` has no entries (README only). The cited ADR is sysml-codegen `.project/adr/0007-agentic-mbse-owns-neutral-facts-codegen-owns-rendering.md` (active, 2026-08-23).
- Code extended: `src/agentic_mbse/sysml/{executable_profile,reference_use,expression,constraint_extraction,syside_adapter}.py`; `src/agentic_mbse/errors.py`

## The Point

[INHERITED: epic Item 1 objective] Define and implement the structural contract **without duplicating model interpretation and without broadening current refusals accidentally**.

[AGENT, ratified by owner 2026-10-15] The generator, L6 and shipped guidance today each hold their own picture of what the generator can execute. They drift, and a modeler finds the generator's limits one failed run at a time (dc3: L6 saw B7 and B8, missed B1–B6). Item 1 replaces the three pictures with one contract that later items consume: codegen in Item 2, L6 in Item 3, rendered guidance in Item 5. The contract is only worth having if it is honest in both directions. It must never call a model clean when a check could not run, and it must never refuse something the pinned generator actually accepts.

## R1 — Capability-policy ownership (owner gate, recommendation only)

**The question.** Which repository owns the decision "the generator refuses shape S in context C", and where is the line between facts, decisions and consumers? ADR 0007 settles that model facts live in agentic-mbse and output facts in codegen, with dependency codegen → agentic-mbse only. It does not settle who owns the admit/refuse decision.

**Recommendation (Option A): agentic-mbse owns the declared contract in a pure decision layer. The generator stays the ground truth the contract is checked against.**

| Layer | Owner | Holds | Must not |
|---|---|---|---|
| Facts | agentic-mbse (reads SysIDE) | What the model declares: occurrence structure, expression sites, binding sources, assertion owners, String values, constraint facts | Decide admit/refuse (one grandfathered exception, below) |
| Decisions | agentic-mbse, pure (no SysIDE) | `subset_profile.py`, packaged rule records, `SUBSET_PROFILE_VERSION`, neutral reason IDs, outcomes | Import SysIDE or codegen; use `SI_*` names outside evidence fields |
| Consumers | codegen (Item 2), L6 (Item 3), docs (Item 5) | Code mapping (one-to-many), output facts, severity, rendering | Re-derive a decision the contract holds |

Three statements make the boundary operational:

- **Authority.** The pinned generator's behavior is ground truth. The contract is a declared, probe-evidenced reproduction of it. A divergence is a contract defect, or an R2 behavior change that needs the owner. It is never a silent policy change.
- **Occurrence structure is a model fact.** Which part usages the generator instantiates (roots, redefinition slots, multiplicity counts, which redefined calc usage writes in each scope) is a fact about the model. Today it exists only in codegen (`elaboration/occurrence.py:902-1046`, `elaborate.py:901-931`). Under ADR 0007 it belongs in agentic-mbse. Item 1 ports it faithfully as a shared fact. Item 2 then migrates codegen onto it or records why not. Until then the two copies are held together by a recorded parity check.
- **The invocation allowlist is a grandfathered exception.** `reference_use._require_supported_invocation` (`reference_use.py:395-428`) is a capability decision living in the fact layer, and codegen's ES-005 refusal is that raise. Moving it would change codegen's refusal path, which is Item 2's call. Item 1 leaves it in place, exposes the allowlist through one public predicate, and the profile consumes that predicate's answer as a fact. A change to the allowlist must bump `SUBSET_PROFILE_VERSION`, and a test enforces this.

**How the epic's suggested direction fares.** The suggestion (pure `sysml/subset_profile.py`, `SUBSET_PROFILE_VERSION`, neutral reasons, separate fact extraction) holds on its merits, and Option A adopts it. It needs two amendments. First, "separate extraction of required facts" understates the work. The occurrence facts ES-003, ES-004 and ES-007 need are not in agentic-mbse at all, so Item 1 must port them, and that port is temporary duplication until Item 2 retires codegen's copy. Second, the existing allowlist exception has to be named, not ignored.

**Rejected alternatives and what each costs**

- **B. Codegen owns policy; agentic-mbse ships facts only.** L6 and guidance could only consume the policy by importing codegen, which is a [HARD] violation, or by re-implementing it, which is the drift this epic exists to stop.
- **C. Put decisions in the fact layer (generalize the allowlist pattern).** Capability refusals would arrive as evidence errors, indistinguishable from real evidence failures. ES-006 already shows the harm: a conditional surfaces as `RESOLVED_TARGET_MISSING`. Per-node facts also cannot see instantiation context, the decisions cannot be versioned separately, and a pure snapshot-route evaluation becomes impossible.
- **D. Shared records, each consumer implements the decisions.** Two implementations of every decision, kept in step by review alone. That is the status quo with better documentation.
- **A′. Option A without the occurrence port (approximate instantiation).** The prototype's "typed anywhere" heuristic shows the cost. Either rules refuse in contexts the generator never instantiates (an R2 breach), or every uncertain case reports `unverified` and the repaired-tree criterion fails. Either way it is still a second interpretation, only a partial one.

**What approving A commits the owner to.** Item 2 inherits two obligations: migrate codegen onto the shared occurrence facts, and decide the allowlist's home. Item 1's effort grows by the occurrence port (≈500 lines plus parity evidence; see de-risk flag F1). The ADR text to file after approval is drafted in [Appendix B](#appendix-b--adr-draft-r1).

## Research Findings

Verified at sysml-codegen `b5663c07` (`.git/refs/heads/main`; working tree read directly) and agentic-mbse `a718efec`. Codegen paths are relative to `src/sysml_codegen/`.

- **Roots** (`elaboration/occurrence.py:902-923`): every `PartUsage` from `elements_of_type(model, "PartUsage")` whose `owning_type` (falling back to `owner`) is neither a `PartDefinition` nor a `PartUsage`.
- **Reach** (`occurrence.py:927-963`, `965-1046`): an occurrence's children are the `usage.usages` that are composite user-model `PartUsage`s. For each redefinition slot only the effective declaration is kept (`FeatureSlotIndex.effective_declaration`, `:249`). Children are visited once per multiplicity index, so `[0]` instantiates nothing beneath it. The type closure comes from `owned_specializations[].superclassifier` (`:635-664`). `occurrences_for_type` matches any occurrence whose type closure contains the definition (`:505-508`), so subtypes count.
- **Multiplicity** (`occurrence.py:812-899`): reads `usage.multiplicity` (KerML: own or inherited from supertypes), `usage.is_ordered`, `usage.is_nonunique`, `upper_bound` and `lower_bound`. Ordered or nonunique gives `SI_MULTIPLICITY_UNSUPPORTED`. A missing or non-integer upper bound gives `…_UNRESOLVED`. A negative bound gives `…_INVALID`, and lower ≠ upper gives `…_UNSUPPORTED`. A bound is evaluated with agentic's `evaluate_true_static_expression`, or through a referenced attribute's single writer (`:694-788`). The prototype read `declared_multiplicity`, a different attribute.
- **Attachment** (`elaborate.py:759-787`): a part def owner gets every occurrence of its type, a part usage owner gets its own occurrences, a package always gets one scope, and anything else gets none. **Calc usages also go through writer selection** (`:1195-1233`, `_select_writer` `:901-931`). Usages in one redefinition slot share scopes, and each scope classifies only the winning writer.
- **Binding classifier** (`elaborate.py:2130-2171`, `:2187-2196`): it strips a unit annotation (agentic `unit_annotation_value`), then tests `is_literal_node`. Next it requires exactly one inventoried reference use and a `FeatureChainExpression` or `FeatureReferenceExpression` metatype (`:1114-1118`); anything else is an expression source. Self-binding means `use.path.leaf.element_id == formal.element_id` (`extraction/binding_source.py:87-89`). Every primitive except the metatype test is already agentic code.
- **Expression inventory** (`elaboration/expression_evidence.py:280-347`): sites are (a) every `Feature` with a `feature_value_expression`, with roles `CALC_DEFINITION_DEPENDENCY`, `BINDING`, `ALIAS` and `COMPUTED_ATTRIBUTE` by owner; and (b) the `result_expression` of every `ConstraintDefinition`/`ConstraintUsage`. It fails fast. A calc def's bare result expression is not a site; it goes to the compiler and becomes `MANUAL_REQUIRED` (`extraction/calc_compat_renderer.py:75`, `expression_compiler.py:285-303`).
- **Code mapping** (`orchestration/elaborated_pipeline.py:389-396`, `:425`): `INDEXED_REFERENCE_UNSUPPORTED` and `EXPRESSION_KIND_UNSUPPORTED` map to named codes, and every other evidence code maps to `SI_EVIDENCE_INCOMPLETE`.
- **CLI** (`cli/__init__.py:1026-1069`, `:857`): `generate --models P --output D`. Exit 1 on any failure; codes appear only in `ERROR:` log lines. Codegen resolves agentic-mbse through `[tool.uv.sources] agentic-mbse = { path = "../agentic-mbse", editable = true }`.
- **Agentic precedent:** `constraint_facts.py` (pure types) with `constraint_extraction.py` (SysIDE) and `executable_profile.py` (pure decisions, closed `REASON_CODES` validated in `EligibilityDiagnostic.__post_init__` `:123-132`, `PROFILE_SEMANTIC_VERSION` `:62`). The static ownership gate (`tests/test_sysml/test_semantic_selector_ownership.py:24-32`) confines raw reads of `operands`/`referent`/`target_feature`/`chaining_features` to `reference_use.py` and `syside_adapter.py`. The purity check is `tests/test_sysml/test_executable_profile_hygiene.py`. Package data precedent: `src/agentic_mbse/extraction/check_corpus/*.pdf`.
- **L2 self-binding** (`validation/level2_structure.py:322-336`): calc usages only, bare references only, `referent` UUID = member UUID, every context. It is a native-correctness check, which is a different question from the generator's refusal.
- **Prototype limits:** `01-codegen-oracle.py` ran inside the sysml-codegen venv against the live editable agentic-mbse tree and recorded no package identity. Its results are useful as fixtures, not as probe records.

## Core Concept

The contract is a **lookup table keyed by (shape, context), whose refused entries must carry evidence.**

Three steps, each in its own layer:

1. **Facts** say what the model contains and where. "This calc input is bound to `(a, b)`." "Its owner `Site` has 2 occurrences reachable from generator roots, and this usage is the selected writer in both." Facts are extracted once, with the same SysIDE reads and agentic helpers the generator uses, so they agree with the generator by construction rather than by imitation.
2. **Rules** are small pure functions that recognize a *shape* in the facts and compute its *context* from a closed vocabulary. A rule never decides the outcome.
3. **Records** decide. Each rule record maps (shape, context) to an outcome. A `refused` entry must cite at least one probe, which is a retained run of the pinned generator on a fixture of exactly that pair. Any pair the record does not list reports `unconfirmed`.

The key insight is that **R2 safety comes from the data shape, not from rule authors being careful.** A rule author can get a context computation wrong. But the evaluator can only emit `refused` through a record entry that cites a probe, and a test re-runs the evaluator on that probe's own fixture and checks that the pair matches. A new or unforeseen context defaults to `unconfirmed`, never to `refused`.

The same structure gives the other honesty property. A rule whose required facts failed to extract cannot look up anything, so it emits a structured `unverified` entry, and the result cannot be marked complete.

## Key Bets

- **B1. The generator's capability boundary is determined by model facts readable from SysIDE before elaboration.** This covers occurrence reach, writer selection, multiplicity readings, expression sites and binding shapes. *If false → some contexts can only be decided after codegen elaborates; those pairs stay `unverified`/`unconfirmed`, and ES-003/ES-004/ES-007 cannot reach the repaired-tree criterion.*
- **B2. A faithful port of codegen's occurrence reach and writer selection fits in agentic-mbse at proportionate size (≈500 lines) and reproduces codegen exactly on the corpus, the fixtures and dc3.** *If false → Option A's cost changes materially, and R1 should be re-weighed before planning (see F1).*
- **B3. One construct per fixture isolates one (shape, context) pair.** The generator fails fast at the first inventory error (`expression_evidence.py:249-276`), so a single-construct fixture's observed code belongs to that construct. *If false → probe records misattribute refusals, and the "refused requires probe" invariant certifies the wrong pair.*
- **B4. Reading the same SysIDE attributes as codegen gives the same answers, without our needing to understand SysIDE's semantics for them.** Examples: `usage.multiplicity` rather than `declared_multiplicity`, and `is_ordered`/`is_nonunique` through redefinitions. *If false → facts diverge on inherited or redefined shapes; the parity run (F1) would show it.*

## Key Decisions

- **D1. Three new layers mirror the existing constraint split.** Pure fact types, SysIDE extraction, and a pure decision module. *Rejected: one combined module (it breaks the license-free, SysIDE-free purity that `executable_profile` already proves and Item 2's snapshot route needs).*
- **D2. Outcomes come from records keyed by (rule, shape, context); unlisted pairs are `unconfirmed`.** *Rejected: outcomes hard-coded inside rule functions (the R2 guard would then depend on code review, not data plus test).*
- **D3. Refused entries require `probe_ids`, checked when records load.** A record with a refused entry and no probes fails to load, the same way `EligibilityDiagnostic` rejects an unknown reason. *Rejected: a test-only convention (the evaluator could still emit an unbacked refusal in a consumer that skips tests).*
- **D4. Reason vocabulary: a sibling closed set, `SUBSET_REASON_CODES`, disjoint from `REASON_CODES`.** ES-007 findings carry their executable-profile reasons as `detail_reasons`, validated against `REASON_CODES`. *Rejected: extending `REASON_CODES` (it would bump `PROFILE_SEMANTIC_VERSION` with no predicate change, and would let structural reasons be built as eligibility diagnostics).*
- **D5. One `binding-source` rule over one binding-source fact.** Matrix rows ES-003, ES-012 and self-binding all name it, with one reason per refused classifier outcome. Indexed references get their own `indexed-reference` rule over expression sites, because the inventory refuses them model-wide before the classifier ever runs. *Rejected: separate ES-003/ES-012 rules (two detectors over one generator classifier can disagree).*
- **D6. Identity and dedup are by declaration.** A finding is keyed by (rule, shape, context, subject declaration UUID). Occurrence-dependent findings carry `occurrence_count` and the root IDs they are reachable from. Counts are reported as declarations and occurrences separately. *Rejected: one finding per occurrence (it inflates counts, which is the prototype's 240-overlap problem, and the remedy is per declaration anyway).*
- **D7. Roots are an extraction input, and their meaning is decided in the evaluator.** Extraction always computes the generator root set, plus the reach from any caller-supplied `PartUsage` roots. The evaluator labels findings reachable only from extra roots with context `beyond_generator_roots`, which records as `unconfirmed`. A narrowed selection marks the scope incomplete. *Rejected: roots as an evaluator-only input (the pure evaluator cannot compute reach without SysIDE).*
- **D8. Location: rule records are package data; probes, matrix and site account are test data; run logs live in `.project`.** Details are in § Where things live. *Rejected: everything in `.project` (archival would break the cross-check tests); everything in package data (codegen file paths and 500 site rows are evidence, not product).*
- **D9. Re-run every prototype fixture through the new probe harness instead of reusing prototype runs.** Each record notes the prototype fixture it supersedes. *Rejected: reuse (the prototype run was not isolated and captured no package identity, so it cannot meet the spec's evidence bar).*
- **D10. Harden the prototype scanner rather than rewrite it.** Promote `02-inventory.py` to `scripts/subset_profile/scan_sites.py`. Hardening adds four things: it reads `git archive` exports at pinned revisions, writes its revision and recognized forms into its output header, maps the 5 computed `executable_profile` sites to `REASON_CODES`, and gains a `--reconcile site_account.csv` mode that exits non-zero on unaccounted sites or orphan rows. *Rejected: a rewrite (more risk, and the stdlib-AST scanner's 500-site result is already known).*
- **D11. The ES-010 refusal side stays a candidate.** The projection boundary (`project.py:490`, `:571-608`) has three entry paths (a String design attribute, a literal String binding, an unbound formal with a String default), and which attributes become entry points is an output fact. *Rejected: promoting the spec's restatement (it covers one of the three paths, so it is either incomplete or an R2 risk).*
- **D12. Probe scope beyond the minimum.** Probe every code-read pair a rule can report, so it stops being `unconfirmed`. Also probe ES-002, ES-008 and ES-009 once each, to *reproduce* the dc3 observations. Do not promote those three: their facts need occurrence-domain or value-writer analysis that Item 1 does not build. They go to the R3 proposal with their probe results. ES-011 is not probed (Item 2 owns reproduction). The probe list is in Appendix C.

## Architecture

```
SysIDE model ──► occurrence_extraction ──► OccurrenceStructure ─┐
             ──► subset_extraction ──────► SubsetFacts ─────────┼─► subset_profile.evaluate ─► SubsetProfileResult
             ──► constraint_extraction ──► IdentifiedConstraintFacts ┘        ▲            (findings, unverified, scope)
                    (existing)                                  rules.toml (package data, loaded + validated)
```

- **Facts are total.** Extraction runs per fact kind and per element. An element failure becomes a `FactFailure` carrying the closed `SemanticEvidenceCode` where one applies, and the walk continues. A whole-kind enumeration failure marks that kind as not enumerated. Nothing is dropped silently.
- **The evaluator is pure.** `evaluate_subset_profile(facts, rules=PACKAGED_RULES) -> SubsetProfileResult`. It imports only fact types, `executable_profile` and `reference_use`'s allowlist constant. It never imports SysIDE (hygiene test, as for `executable_profile`).
- **ES-007 reuses the executable profile.** The evaluator calls `evaluate_identified_profile` on the existing constraint facts. A BLOCK in an attached scope maps to the `constraint-predicate` rule's `blocked_predicate` shape. NON_NUMERICAL maps to `excluded`. An UNASSESSED usage is outside the rule's shape and is counted in the coverage summary, never reported as `admitted`.
- **ES-005 reuses the allowlist.** `reference_use` gains one public read, `invocation_uses(expression)`. It walks with the same dispatch order as `_walk` and returns each ordinary invocation with its callable identity and a `supported` bit, computed by the same predicate `_require_supported_invocation` now calls. The change is byte-faithful, and the probe re-run with Item 1's final agentic revision shows identical generator outcomes.
- **Consumers are untouched.** No L6, CLI or codegen wiring. `agentic-mbse validate` output is diffed before and after.

## Required Invariants

1. `refused` is emitted only through a record entry whose `probe_ids` is non-empty. Record loading enforces this, and `test_subset_probe_evidence.py` checks that every cited probe exists, matches its (rule, shape, context), observed a refusal at the pinned identity, and that the evaluator reproduces the pair on the probe's own fixture.
2. Every refused shape has at least one admitted-context probe, and the evaluator reports no `refused` on it. A shape the generator refuses in every context it reaches (for example an asserted constraint owned by a calc def) instead carries a `no_admitted_context` statement with its generator citation. The test accepts either, never neither, and the matrix shows which.
3. Any (shape, context) not listed in a record yields `unconfirmed`.
4. A missing required fact kind or a failed element yields `UnverifiedCheck`, never an empty clean result; `complete` is false. Rules whose facts are available still report.
5. No `agentic_mbse` module imports `sysml_codegen`. No rule ID or reason ID matches `SI_[A-Z_]+` or names a consumer type. `SI_*` strings appear in packaged records only in fields marked as evidence.
6. Every reason the evaluator can emit is in `SUBSET_REASON_CODES` (validated in `SubsetFinding.__post_init__`), and every `detail_reason` is in `REASON_CODES`.
7. Output is a deterministic function of the facts: findings are sorted by (rule, file, line, qualified name, context, shape) with the UUID as last tiebreak. Permuted document order gives identical output.
8. A change to the invocation allowlist or to any record changes `SUBSET_PROFILE_VERSION`. The test pins a digest of the allowlist and the records.
9. Facts read the same SysIDE attributes and agentic helpers as the generator. No new interpretation exists where an agentic helper already does the job.

## Component Overview

All under `src/agentic_mbse/sysml/` unless stated.

- **`occurrence_facts.py`** (pure types): `OccurrenceStructure`, `OccurrenceNode`, `MultiplicityReading`, `Attachment`, `WriterSelection`. These are neutral facts Item 2 can adopt.
- **`occurrence_extraction.py`** (SysIDE): a faithful port of codegen's root rule, redefinition slots, effective child declarations, multiplicity reading and count resolution, type closures, attachment, and calc-usage writer selection. It never raises a generator code. An unexpandable multiplicity becomes a status on that node, and its subtree is marked `beneath_unexpandable`.
- **`subset_facts.py`** (pure types): `SubsetFacts` and per-kind facts (`BindingSourceFact`, `ExpressionSiteFact`, `AssertionOwnerFact`, `PartMultiplicityFact`, `StringValueFact`), plus `ElementRef`, `SafeLocation`, `FactFailure`. The constraint facts are referenced through `TYPE_CHECKING`, as `executable_profile` does.
- **`subset_extraction.py`** (SysIDE): builds `SubsetFacts` from the model, the root request and the occurrence structure. It reuses `inspect_reference_uses`, `invocation_uses`, `unit_annotation_value`, `is_literal_node`, `extract_identified_constraint_facts`, `SysideAdapter`, and the inventory's site enumeration and roles.
- **`subset_profile.py`** (pure): `SUBSET_PROFILE_VERSION = "subset-profile/v1"`, `SUBSET_REASON_CODES`, `ContextId`/`Outcome` enums, record loader and validator, the rule functions, and `evaluate_subset_profile`.
- **`subset_profile_rules.toml`** (package data): one record per rule.
- **`reference_use.py`** (edit): public `invocation_uses()` and `SUPPORTED_INVOCATION_IDS`; `_require_supported_invocation` calls the shared predicate.
- **`scripts/subset_profile/`** (dev tooling, not shipped): `probe.py` (harness), `scan_sites.py` (D10), `run_trees.py` (evaluator over dc3/corpus exports, recorded runs), `occurrence_parity.py` (F1 parity, recorded run), `render_matrix.py`.
- **Tests:** under `tests/test_sysml/test_subset_*.py`, with data under `tests/fixtures/subset_profile/`.

## Where things live

| Artifact | Location | Why |
|---|---|---|
| Rule records | `src/agentic_mbse/sysml/subset_profile_rules.toml` | Runtime contract; Item 2 pins it, Item 5 renders from it. TOML via stdlib `tomllib`, so loading needs no SysIDE and has no implicit typing |
| Probe declarations, fixtures and observations | `tests/fixtures/subset_profile/probes/<probe_id>/{probe.toml, model.sysml, observation.json}` | One fixture serves both the generator probe and the evaluator test, so "fixtures mirror probes" holds by construction |
| Capability/refusal matrix | `tests/fixtures/subset_profile/inventory/matrix.toml` | Cross-check tests read it; contains codegen paths (evidence, not product) |
| Site account and scanner manifest | `tests/fixtures/subset_profile/inventory/{site_account.csv, scanner.toml}` | Join test (sites ↔ rows) reads both; `scanner.toml` names the scanner revision, recognized forms and blind spots |
| Evaluator fixtures beyond probes | `tests/fixtures/subset_profile/cases/` | Roots, determinism, failure-injection cases |
| Run logs and reports | `.project/active/exec-subset-profile/evidence/` | Probe run logs, reconciliation run, dc3/corpus runs, parity run, rendered `matrix.md`, R3 proposal, re-estimate. Archived with the item |

Every pytest test reads only package data and `tests/`, so the tests keep passing after the item folder is archived.

## Probe harness

`scripts/subset_profile/probe.py run [--probe ID | --all] --agentic-rev REV`. All writes happen in a fresh temp directory and under `tests/fixtures/subset_profile/probes/`. Sibling checkouts are only read.

1. **Isolated tree.** `T=$(mktemp -d)`. Export with `git -C ~/src/sysml-codegen archive b5663c07` into `$T/sysml-codegen` and `git archive <agentic-rev>` of this repo into `$T/agentic-mbse`. Both commit IDs are verified with `git get-tar-commit-id`. The sibling layout makes codegen's `path = "../agentic-mbse"` source resolve inside `$T`.
2. **Environment.** Run `uv sync --frozen` in `$T/sysml-codegen` against codegen's own `uv.lock`. `SYSIDE_LICENSE_KEY` is passed through from the environment; the record notes that a key was present, never its value.
3. **Identity capture.** Run `$T/sysml-codegen/.venv/bin/python -I` to emit `importlib.metadata` versions for sysml-codegen, agentic-mbse and syside, `syside.__version__`, the Python version, both packages' `__file__`, and the sha256 of `uv.lock`. **Isolation check:** the probe aborts if either package resolves outside `$T`.
4. **Run.** For each probe, copy `model.sysml` into `$T/probes/<id>/model/` and run `python -m sysml_codegen generate --models … --output $T/probes/<id>/out` with cwd `$T` and a timeout. Capture the exit code, `ERROR:` lines, the codes (prototype regex), and the generated file list with hashes. Observed outcome: `refused` (exit ≠ 0 with codes), `admitted` (exit 0), otherwise `inconclusive`.
5. **Record.** Write `observation.json`: identity, command, exit, codes, error lines (≤3), observed outcome, `matches_expectation`, fixture sha256, harness revision, timestamp. Append the raw log to `evidence/probes/<timestamp>.log`.
6. **Same-generator check.** Run `--all` twice: once with the pre-Item-1 agentic revision (`a718efec`) and once with Item 1's final revision. Identical observations show that Item 1's edits to shared modules did not change codegen.

`probe.toml` is authored by hand and states the claim: `probe_id`, `rule_id`, `shape_id`, `context_id`, `expect` (`refused`|`admitted`), and `supersedes_prototype` where it applies. The harness never edits it. A probe whose observation contradicts an `admitted` expectation is an R2 stop for that rule: it halts and goes to the owner. A contradicted `refused` expectation means the record's context is wrong and must be corrected.

## Non-Goals

- Codegen integration, code mapping, the `tests/conformance/subset_profile/` corpus, mutation tests, per-site stable codes, `check`, snapshot and version integration (Item 2). Migrating codegen onto the occurrence facts is Item 2 under R1.
- A wire codec or schema version for `SubsetFacts`; Item 2 adds one if the snapshot route needs it.
- L6 wiring, severity, execution-target settings (Item 3); positional binding (Item 4); rendering `generator-subset.md` (Item 5).
- Reproducing ES-011, String metadata policy, promoting ES-002/ES-008/ES-009 or the ES-010 refusal side.
- Fixing `L6-LIBRARY-ALIAS-SOURCE`; relaxing any generator refusal; new language support.

## Implementation Notes

- **Spec premise refinements, surfaced rather than silently resolved:**
  - (a) Spec Table 1 gives ES-003's refused context as "the owner is instantiated". The generator classifies only the **selected writer** per scope, so a calc usage overridden by a redefinition in every instantiated scope is never examined. The record lists `writer_overridden` as not-refused, and a probe covers it. Reading the spec literally would have refused an admitted shape.
  - (b) A construct beneath a part usage whose multiplicity the generator refuses is never reached by the generator. Its context is `beneath_refused_multiplicity`, which records as `unconfirmed`, because no probe can observe a refusal there.
  - (c) ES-004 must read `usage.multiplicity`, as codegen does, not the prototype's `declared_multiplicity`.
- **ES-001 shapes** split asserted and non-asserted forms (`constraint_extraction._ASSERTED_FORMS`). The calc-usage owner context is probed for both.
- **Expression-site contexts are per inventory role** (binding value, calc-definition feature value, attribute value, constraint predicate), plus `calc_result_expression` (admitted, qualification `manual_stub`) and `other_expression_site` (unconfirmed). One probe per refused role.
- **The ownership gate stays green.** New SysIDE readers call `reference_use`/`syside_adapter` functions and never read `operands`/`referent`/`target_feature`/`chaining_features` directly.
- **The conditional operator spelling** (`if`) is confirmed by a learning test on `es006_refused_conditional`, not assumed.
- **The `executable_profile` computed reasons** (`:542`, `:597`, `:660`, `:711`, `:813` at `a718efec`) get one test that drives each emission and asserts membership in `REASON_CODES`.

## Potential Risks

| Risk | Mitigation |
|---|---|
| Occurrence port diverges from codegen on redefinition-heavy models | F1 spike before planning; recorded parity run on corpus, fixtures and dc3; Item 2 migration under R1 |
| dc3 baseline shows a B-category only as `unconfirmed` (e.g. ES-003 bindings nested under B4 unbounded racks) | Evidence itemizes these with context; a category that appears only as `unconfirmed` goes to the owner, not hidden |
| Probe environment cannot sync (private SysIDE index, license) | First plan step is a harness smoke on one probe; the failure is recorded, never worked around inside sibling checkouts |
| `reference_use` refactor changes codegen behavior | Byte-faithful refactor; same-generator check (harness step 6); existing reference-use tests |
| ≈40 probes plus ≈500 site rows inflate effort | Re-estimate at close per epic; probes are single-construct and scripted |

## Integration Strategy

Item 1 merges as new modules plus one additive public read in `reference_use`. Nothing consumes the contract yet. Item 2 pins `SUBSET_PROFILE_VERSION` and the records, maps reasons to `ElaborationCode`, and adopts the occurrence facts. Item 3 maps outcomes to L6 severity. Item 5 renders from the records. The R1 decision is filed as an agentic-mbse ADR after approval. Item 2 files the pointer entry in sysml-codegen (cross-seam placement rule).

## Validation Approach

- **Pytest without SysIDE:** record completeness and closed vocabularies; matrix ↔ records; sites ↔ matrix join (every `in scope` site names a row, every row lists sites or `no_raise_site`, every `explicit follow-up` site has an owner and a limitation); probe evidence (invariants 1–2); coupling (invariant 5); version digest (invariant 8); purity hygiene; computed-reason closure.
- **Pytest with SysIDE:** per-rule refused and admitted fixtures (the probe fixtures plus the carried-over prototype neighbors); roots (default equals the generator rule on nested, package-level and part-def-owned usages; widened gives `unconfirmed`; narrowed gives incomplete); failure injection (a) extraction, (b) enumeration, (c) missing occurrence evidence; determinism under permuted document order.
- **Recorded runs** (evidence folder): probe runs at both agentic revisions; site reconciliation, with counts against 441/59 and every added or removed site itemized; occurrence parity; dc3 baseline and repaired; codegen corpus (manifest counts as read: 14/23); `validate` diff before and after; `pytest`/`mypy`/`ruff`, with licensed and skipped checks named.

## Next-Stage Handoff

- **Fixed (after R1 approval):** the layer boundary; records keyed by (rule, shape, context) with probe-gated refusal; locations; D1–D12.
- **Open for the plan:** exact `ContextId` membership once the probes land; the probe list's final size; the TOML field names.
- **De-risk first:** F1 (occurrence port parity), then the probe-harness smoke. See Appendix D.

---
Next Step: `/_my_design_review` in a fresh session, then **owner gate R1**, then `/_my_plan`.

## Appendix A — Data model

Pure types (`subset_facts.py`, `occurrence_facts.py`, `subset_profile.py`). All are frozen dataclasses.

```python
class Outcome(StrEnum): REFUSED; ADMITTED; EXCLUDED; OMITTED; UNCONFIRMED
class ContextId(StrEnum):  # closed; each member documented with its generator citation
    OWNER_INSTANTIATED; OWNER_PACKAGE; OWNER_UNINSTANTIATED; WRITER_OVERRIDDEN; OWNER_OTHER
    BINDING_VALUE; CALC_DEFINITION_FEATURE_VALUE; ATTRIBUTE_VALUE; CONSTRAINT_PREDICATE
    CALC_RESULT_EXPRESSION; OTHER_EXPRESSION_SITE
    CALC_DEFINITION_OWNER; CALC_USAGE_OWNER
    EXPANDED_PART_USAGE; UNEXPANDED_PART_USAGE; ATTRIBUTE_USAGE
    BEYOND_GENERATOR_ROOTS; BENEATH_REFUSED_MULTIPLICITY; EVERYWHERE
```

```python
class ElementRef:  element_id: UUID; qualified_name: str; kind: str
class SafeLocation: file: str | None; line: int | None; qualified_name: str | None  # never raises
class FactFailure:  fact_kind: FactKind; subject: SafeLocation | None
                    cause: SemanticEvidenceCode | ScopeCause; detail: str
class ScopeCause(StrEnum): ENUMERATION_FAILED; OCCURRENCE_UNAVAILABLE; ROOTS_UNAVAILABLE; ADAPTER_ERROR
class FactKind(StrEnum): OCCURRENCE; BINDING_SOURCE; EXPRESSION_SITE; ASSERTION_OWNER;
                         PART_MULTIPLICITY; STRING_VALUE; CONSTRAINT
```

```python
class MultiplicityReading: lower: int | None; upper: int | None; unbounded: bool
    ordered: bool; nonunique: bool; resolution: Literal["exact","range","unresolved","negative","absent"]
class OccurrenceNode: usage: ElementRef; type_closure: frozenset[UUID]; root_id: UUID
    count: int | None; status: Literal["expanded","unexpandable","beneath_unexpandable"]
class Attachment: owner: ElementRef | None; owner_kind: OwnerKind
    scopes_by_root: Mapping[UUID, int]          # root id -> attached scope count
class WriterSelection: usage_id: UUID; selected_scopes_by_root: Mapping[UUID, int]
class OccurrenceStructure: generator_root_ids: frozenset[UUID]; selected_root_ids: frozenset[UUID]
    nodes: tuple[OccurrenceNode, ...]; attachments: Mapping[UUID, Attachment]; writers: Mapping[UUID, WriterSelection]
```

```python
class BindingSourceFact: consumer: ElementRef; formal: ElementRef; location: SafeLocation
    kind: Literal["literal","single_reference","self_binding","indexed","other_expression"]; authored: str
class ExpressionSiteFact: feature: ElementRef; role: SiteRole; location: SafeLocation
    invocations: tuple[InvocationUse, ...]; has_indexed_reference: bool
    conditional: bool; inspection_failure: SemanticEvidenceCode | None
class AssertionOwnerFact: constraint: ElementRef; form: str; owner_kind: OwnerKind
class PartMultiplicityFact: usage: ElementRef; reading: MultiplicityReading; composite: bool
class StringValueFact: feature: ElementRef; spelling: Literal["attribute_declaration","redefinition_shorthand"]
class SubsetFacts: occurrence: OccurrenceStructure | None; bindings: tuple[BindingSourceFact, ...]; sites: ...
    assertions: ...; multiplicities: ...; strings: ...; constraints: IdentifiedConstraintFacts | None
    enumerated: frozenset[FactKind]; failures: tuple[FactFailure, ...]
```

```python
class Admission: outcome: Outcome; probe_ids: tuple[str, ...]; qualification: Literal["none","manual_stub"]
class ShapeRecord: shape_id: str; reason_id: str; admissions: Mapping[ContextId, Admission]
    no_admitted_context: str | None   # required when no admission is ADMITTED (invariant 2)
class RuleRecord: rule_id: str; title: str; matrix_rows: tuple[str, ...]; fact_requirements: frozenset[FactKind]
    shapes: tuple[ShapeRecord, ...]; remedy: str; semantic_limits: str; example_probe: str
    doc_anchor: str; evidence_status: EvidenceStatus; generator_evidence: tuple[GeneratorEvidence, ...]  # SI_* only here
class GeneratorEvidence: code: str; site: str   # evidence field, e.g. ("SI_SELF_BINDING", "elaborate.py:2187-2196")
class EvidenceStatus(StrEnum): PROBE_OBSERVED; PARTIAL; CODE_READ   # rule-level summary of its admissions
```

```python
class SubsetFinding: rule_id; shape_id; context_id: ContextId; outcome: Outcome; reason: str
    detail_reasons: tuple[str, ...]; subject: ElementRef; location: SafeLocation
    occurrence_count: int | None; via_roots: tuple[str, ...]; probe_ids: tuple[str, ...]
    # __post_init__: reason in SUBSET_REASON_CODES; detail_reasons ⊆ REASON_CODES; REFUSED ⇒ probe_ids
class UnverifiedCheck: rule_id: str; context_id: ContextId | None; subject: SafeLocation | None
    cause: SemanticEvidenceCode | ScopeCause; detail: str
class ScopeReport: generator_roots: tuple[ElementRef, ...]; selected_roots: tuple[ElementRef, ...]; narrowed: bool; widened: bool
class SubsetProfileResult: profile_version: str; scope: ScopeReport; findings: tuple[SubsetFinding, ...]
    unverified: tuple[UnverifiedCheck, ...]; counts: tuple[RuleCount, ...]   # declarations vs occurrences
    complete: bool          # no unverified, not narrowed, every required FactKind enumerated
```

Rule IDs and shapes (rule ID ← matrix rows):

| Rule ID | Matrix rows | Shapes (reason ID) |
|---|---|---|
| `calc-owned-assertion` | ES-001 | `asserted_constraint`, `non_asserted_constraint` (reasons `constraint_owned_by_calc_definition`, `constraint_owned_by_calc_usage`) |
| `binding-source` | ES-003, ES-012, SELF-BINDING | `expression_source` (`binding_source_expression`), `self_reference_source` (`binding_source_self_reference`) |
| `indexed-reference` | INDEXED-REFERENCE | `indexed_reference` (`indexed_reference_unsupported`) |
| `part-multiplicity` | ES-004 | `ordered`, `nonunique`, `range`, `unresolved_bound`, `negative_bound` (`part_multiplicity_*`) |
| `invocation-callable` | ES-005 | `unsupported_callable` (`invocation_callable_unsupported`) |
| `conditional-expression` | ES-006 | `conditional_unresolved_branch` (`conditional_expression_unsupported`) |
| `constraint-predicate` | ES-007 | `blocked_predicate` (`constraint_predicate_blocked`), `non_numerical_predicate` (`constraint_predicate_non_numerical`) |
| `string-value-omission` | ES-010 (omission) | `string_value` (`string_value_not_generated`), both spellings |

A record entry, in TOML:

```toml
[[rule]]
rule_id = "binding-source"
matrix_rows = ["ES-003", "ES-012", "SELF-BINDING"]
fact_requirements = ["binding_source", "occurrence"]
[[rule.shape]]
shape_id = "expression_source"
reason_id = "binding_source_expression"
admissions.owner_instantiated = { outcome = "refused", probe_ids = ["bs-expr-inst-seq", "bs-expr-inst-arith"] }
admissions.owner_uninstantiated = { outcome = "admitted", probe_ids = ["bs-expr-uninst"] }
admissions.writer_overridden = { outcome = "admitted", probe_ids = ["bs-expr-overridden"] }
```

## Appendix B — ADR draft (R1)

To be filed in agentic-mbse with `.project/scripts/adr.sh new subset-profile-capability-ownership` after owner approval. Provenance `[AGENT] (ratified by owner, <date>)`. Seams `[agentic-mbse, sysml-codegen, l6, guidance]`.

**Decision.** agentic-mbse owns the declared executable-subset contract: neutral model facts, including the occurrence structure the generator instantiates, plus a pure, versioned decision layer (`sysml/subset_profile.py`, `SUBSET_PROFILE_VERSION`, neutral reason IDs, packaged rule records). sysml-codegen owns diagnostic-code mapping, output facts and rendering, and remains the behavioral ground truth the contract is checked against. L6 and guidance consume the contract and own presentation.

**Why.** L6 and guidance must use the contract without importing codegen, and two implementations of a decision drift (the dc3 B1–B6 miss). ADR 0007 already places model facts in agentic-mbse; occurrence reach is a model fact that had lived only in codegen. A pure decision layer keeps capability refusals distinct from evidence failures, versions them separately from fact schemas, and evaluates without SysIDE. The generator remains the authority because the contract describes it; a contract/generator disagreement is a defect or a reviewed behavior change.

**Invariants established.** (1) The contract may report `refused` for a (shape, context) only with a retained probe of the pinned generator observing that refusal. (2) Pairs without evidence report `unconfirmed`; missing facts report `unverified`; neither is clean. (3) No agentic-mbse module imports sysml-codegen; `SI_*` codes appear only as evidence. (4) The invocation allowlist in `reference_use` is the one capability decision in the fact layer; changing it changes `SUBSET_PROFILE_VERSION`. (5) Codegen's occurrence reach migrates onto the shared facts (EXEC-SUBSET-CONTRACT Item 2), or Item 2 records why it cannot; until then a recorded parity check holds them together.

**Rejected alternatives.** Codegen-owned policy: L6 and guidance could not consume it without a reverse dependency. Decisions inside the fact layer: refusals would be indistinguishable from evidence failures and context-blind. Per-consumer implementations of shared records: duplicated decisions drift. Approximated occurrence facts: either overbroad refusals or pervasive `unverified`.

## Appendix C — Probe list (initial)

Each line is one probe. `R` expects refused, `A` expects admitted. "⇐ proto" names the prototype fixture it supersedes.

- **calc-owned-assertion:** R calc-def asserted ⇐ `es001_refused_calc_def_assert`; R calc-usage asserted ⇐ `es001_refused_calc_usage_assert`; R calc-usage non-asserted (code read: the owner-kind raise at `elaborate.py:813-820` fires for every form; if the run admits it, the record lists it as admitted); A calc-def non-asserted; A part-owned asserted ⇐ `es001_admitted_part_assert`.
- **binding-source:** R `(a, b)` instantiated owner ⇐ `es003_refused_ordered_nonunique`; R `rate * fuel_code` instantiated ⇐ `unmapped_expression_calc_arg`; R `(a, b)` package-owned calc usage; R self-binding instantiated; R constraint-usage input bound to an expression; A uninstantiated owner; A writer overridden by a redefinition; A ordered nonunique input bound to a scalar ⇐ `es003_neighbor_ordered_param_scalar_arg`; A exact `[1]` ordered input ⇐ `es003_neighbor_exact_ordered_param`; A plain reference actual (ES-012 neighbor); A unit-annotated literal.
- **indexed-reference:** R binding value; R attribute value; R constraint predicate; A indexed reference in a calc def's bare result expression (not an inventory site; if the run refuses it, the record lists it as refused and the shape carries `no_admitted_context`).
- **part-multiplicity:** R range ⇐ `es004_refused_range_parts`; R unbounded ⇐ `es004_refused_unbounded_parts`; R ordered part; R nonunique part; R referenced bound without a literal writer; A uninstantiated template ⇐ `es004_admitted_uninstantiated_template`; A exact redefinition ⇐ `es004_admitted_exact_redefinition`; A ordered/ranged attribute usage; A non-composite (reference) part usage.
- **invocation-callable:** R `product` binding value ⇐ `es005_refused_product`; R `size` ⇐ `es005_refused_size`; R `max` attribute value; R invocation in `return r : Real = …` (calc-definition feature value); R invocation in a constraint predicate; A `max(a, b)` as a calc def's bare result expression (stub); A explicit multiply ⇐ `es005_admitted_explicit_multiply`.
- **conditional-expression:** R binding or calc-definition feature value ⇐ `es006_refused_conditional`; R constraint predicate; A calc def bare result expression; A arithmetic min ⇐ `es006_admitted_arithmetic_min`.
- **constraint-predicate:** R BLOCK, instantiated owner ⇐ `es007_refused_boolean_mixed`; R BLOCK, package owner; A BLOCK, uninstantiated owner; A numeric `and` ⇐ `es007_admitted_numeric_and`.
- **string-value-omission** (omitted, recorded with a name oracle plus a numeric sibling as positive control): both spellings ⇐ `es010_omitted_string_value`; A numeric value ⇐ `es010_admitted_numeric_value`.
- **Candidates, reproduction only:** ES-002 (constraint binding a calc usage's input), ES-008 (nested named subset), ES-009 (usage-subsetting composition), ES-010 refusal ⇐ `es010_refused_string_calc_input`.

## Appendix D — De-risk flags (owner decides whether to run)

- **F1. Occurrence port parity. Spike recommended before planning.** This is an assumption I could not verify by reading. Codegen's reach depends on SysIDE behavior: `usage.usages` exposing inherited features, `Type.multiplicity` falling back to supertypes, `is_ordered`/`is_nonunique` through redefinitions, and slot grouping. A port that reads the same attributes should match, but only a run proves it, and the port's size drives R1's cost. The spike must show the following, using a throwaway script that may import both packages in a temp tree, on the 22 prototype fixtures, the 14 corpus snapshot fixtures and both dc3 trees: (a) an identical root set; (b) an identical set of expanded declarations with occurrence counts; (c) identical "has occurrences" per part definition; (d) the identical selected calc-usage writer per scope; (e) for each unexpandable usage, the same resolution class as codegen's `SI_MULTIPLICITY_*` code. Add fixtures for inherited `ordered` through `:>>` and a multiplicity only on the redefinition. It must also report the port's line count. If (a)–(e) fail or the port exceeds about 800 lines, re-weigh R1 before planning.
- **F2. ES-004 occurrence and multiplicity facts before elaboration.** This collapses into F1. Because the port reads `usage.multiplicity` exactly as codegen does, no separate learning test is needed. If F1 is skipped, a learning test should at least show what `usage.multiplicity` returns for a redefinition without its own bounds, and for an inherited ordered declaration.
- **F3. Binding-shape fact equivalence. No spike.** Equivalence holds by construction: same `unit_annotation_value`, `is_literal_node`, `inspect_reference_uses` count, adapter metatype test and leaf-UUID comparison. The residual risk is which members codegen treats as inputs (`_collect_bound_members` `elaborate.py:1879-1950`, `bound_formal` `binding_source.py:183-207`). The plan reads those before writing the fact, and the probes (Appendix C) prove it.
- **F4. Calc def bare result expression is not an inventory site. No spike.** It is code-read (`expression_evidence.py:280-347`), and the minimum probe set observes it.
- **F5. Probe environment. Smoke test as the first plan step, not a spike.** `uv sync --frozen` must work in an archived temp tree: the private SysIDE index or cache, and the license. One probe end to end proves it.
