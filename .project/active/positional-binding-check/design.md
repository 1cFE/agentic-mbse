# Design: Positional-binding hazard and check (EXEC-SUBSET-CONTRACT Item 4)

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-10-18
**Branch:** `positional-binding-check` (latest commit `91742ebd`; base `ccd57d83`)
**Complexity:** MEDIUM

## Overview

Add one L2 check, `L2_POSITIONAL_BINDING`, that reports an authored calculation or constraint input whose implied (positional) redefinition lands on a differently named formal. It reads one new shared fact (each input's resolved redefinitions, marked implied or explicit), applies D1's pin-list policy, and ships with fixtures, a two-tree reproduction, a hazard register entry and guidance edits. Generator behavior and consumer projects are untouched.

## Related Artifacts

- Spec: `.project/active/positional-binding-check/spec.md` (revised after review)
- Spec review and resolutions: `.project/active/positional-binding-check/spec-review.md`
- Align record (gates R4-1..R4-3, owner boundary): `.project/active/positional-binding-check/briefs/align.md`
- Product lens: `.project/active/positional-binding-check/product-lens.md`
- Epic: `.project/backlog/epic_executable-subset-contract.md` (Item 4; D1)
- Prototype: `.project/concepts/convince-me-exec-subset/evidence/04-README.md`, `04-detector.py`, `04-fixtures/`, `04-*.log`
- Item 1 archive (fact layer and reproduction pattern): `.project/completed/20261018_exec-subset-profile/`
- Learning test for R1–R6: `.project/active/positional-binding-check/learning-findings.md`; tests in `tests/learning/test_syside_input_redefinition.py`
- Decision records: ADR 0001 (`.project/adr/0001-subset-profile-capability-ownership.md`); this design does not touch the subset contract it governs.
- Epic Required Reading for Item 4: none listed.

## The Point

[INHERITED: epic Item 4; spec Problem] An author who writes correctly named inputs on a calc or constraint usage in a different order than the definition gets a silent swap. SysML binds an unprefixed input by position (KerML 8.3.3.3.4, `checkFeatureParameterRedefinition`), so the model is valid and nothing warns. Native SysIDE 0.8.4 and generated/TEAx execution disagree on the result (-7 vs 7 on the reversed subtraction). fusion-tea `f96ad312` has 125 such mismatches whose value effect is unknown. The knowledge sat in sysml-codegen since July and never reached authors.

The obligation this design serves, under D1 `[AGENT] (ratified by owner, 2026-10-15)`: new mismatches block; explicitly pinned legacy mismatches warn, and a pinned warning does not by itself fail L2; a pin certifies neither native values nor agreement between routes; an inspection failure never reads as clean. The work must not change how either route binds (R4-2), must not edit fusion-tea (R4-3) or sysml-codegen (owner boundary), and must not describe fusion-tea as clean.

## Research Findings

**L2 today** (`src/agentic_mbse/validation/level2_structure.py`):
- Four checks append `ValidationIssue`s into one list; `success=len(all_issues) == 0` (`:450`), so any WARNING fails L2.
- The unverifiable pattern is `L2_CHECK_UNVERIFIABLE` at ERROR with a message naming the element (`:355-372`). `ValidationIssue.reason_code` (`sysml/types.py:140`) already carries a subsystem's own code next to the shared category code (DD-R10).
- Metrics are a flat dict printed by `print_result` (`validation/common.py:123-151`). Only L4 and L6 tests assert specific metric keys; no test asserts L2's metric dict as a whole.
- `run_all_checks` calls every level as `check_func(models_path)` (`validation/runner.py:43-50, 98`); `cmd_validate` (`cli/__init__.py:353-365`) has no per-level options yet.
- `discover_sysml_files` globs a directory only (`common.py:71-89`), so "partial scope" means validating a subdirectory.

**Item 1's fact layer** (`src/agentic_mbse/sysml/`):
- `ElementRef` and `SafeLocation` (`fact_refs.py:17-59`) are the pure identity and location types. `_element_ref` (`subset_extraction.py:118-127`) builds an `ElementRef` with `str(element.qualified_name)` and raises `_IdentityError` on a bad UUID. `safe_location` (`occurrence_extraction.py:126-143`) never raises.
- `subset_extraction._Collector` (`:380-427`) is the totality pattern: per element, a fact or a named failure; a population that cannot be listed is recorded once.
- No existing fact names the formal an input redefines. `BindingSourceFact.formal` is the input member itself (`subset_extraction.py:210`). `constraint_extraction._actuals` (`:774-787`) and `reference_use` (`:222-228`) read `owned_redefinitions` but never the implied/explicit distinction for parameters.
- `SubsetFacts` (`subset_facts.py:296-336`) has no consumer outside `subset_*` yet, but Item 2 is building against it in sysml-codegen.
- `SysideAdapter` resolves every metatype name through a closed map (`syside_adapter.py:172-283`); `Redefinition`, `SubjectMembership`, `ActorMembership` and `StakeholderMembership` are not in it.

**Prototype** (`04-detector.py`):
- It reads `feature.heritage.relationships`, keeps `Redefinition`s, and splits them by `is_implied` (`:117-120`). That surface gave 17/17 fixtures and the 125/0/0 tree results under SysIDE 0.8.4.
- Its "owner inherits unredefined inputs" branch (`:142-153`) is the heuristic the spec drops.
- The fusion-tea log prints, per finding, the input's qualified name, its file and line relative to `models/`, and the target's qualified name. No finding has more than one target (checked by grep). The 125 lines span 9 files.

**Guidance and a cross-repo constraint:**
- `docs/patterns/plant-idiom.md:298` "Order does not matter" is about a redefine placed after a binding.
- The self-binding advice to "rename the input" (`skills/sysml-conventions/SKILL.md:129, 222`; `project_templates/MODELING_GUIDE.md.template:150`; `plant-idiom.md:74-79`) means renaming the definition's parameter. The pinned fusion-tea example renames it in the def (`hif_economics.sysml:100`, `in attribute availability_in`). Read as "rename the usage's input", the advice produces exactly this hazard. The edits must say which side is renamed.
- `agents/sysml-expert.md:117-139` is the one role that teaches binding formals (a requirement with `subject system` and constraint formals). No other role in `agents/` shows calc-usage inputs.
- sysml-codegen's `tests/conformance/test_self_binding_guidance_contract.py` reads this repo's `agents/`, `skills/`, `docs/patterns/` and `project_templates/`. It fails if a `@pinned` block is reworded, if an unmarked `in x = x;` appears, if the per-file count of owner-qualified bindings (`in name = ...::`) changes, or if the `@authoritative` marker moves. Guidance edits must respect all four. That test is read-only for this item.

## Core Concept

The check is a fact plus a small decision.

The fact says, for each authored input of a calc or constraint (usage or definition, including requirements and cases): its declared name, its role (ordinary, subject, actor or stakeholder), and every redefinition SysIDE resolved for it. Each redefinition is marked implied or explicit and carries its target formal's identity, name and owning definition. The extractor lives in the shared fact layer beside Item 1's, uses Item 1's identity and location types, and is total: every input yields a fact or a named failure.

The decision reads only facts. An input is flagged for an implied target when the input has a declared name, the target's name differs, and the input's own explicit redefinitions do not account for that target. Each flagged (owner, input, target) triple is a finding identity.

A pin list is a strict TOML file of finding identities that the project recorded as legacy. A finding whose identity is pinned becomes a WARNING; every other finding is an ERROR. A pin that matches no finding is stale (an ERROR) when its file was validated, and out of scope (a count, not an issue) when its file exists but was not validated.

L2's pass rule changes in one place: a pinned positional WARNING is the only issue that does not count toward failure.

Why this is the right shape: the expensive and fragile part, reading SysIDE, is done once into plain data. Everything that is policy (the rule, the role exclusion, pins, scope) is pure code over that data, testable without SysIDE and without guessing. The pin list never changes what the check sees; it only changes severity for exact identities.

## Key Bets

- **B1.** SysIDE 0.8.4 exposes implied positional redefinitions as `Redefinition` relationships in `feature.heritage.relationships` with `is_implied` true, whose `redefined_feature` is the formal at the same position. Observed by the prototype on 17 fixtures and three trees. *If false (for example, on shapes the prototype did not run) → the check misses swaps, and no rule over this fact can recover them.*
- **B2.** In the mixed spelling `in b = 3; in :>> a = 10;`, SysIDE gives `b` an implied redefinition of `Sub::a` even though another input explicitly redefines `Sub::a`. Unverified (see De-risk flags, R1). *If false → the spec's mixed-spelling fixture cannot be flagged from resolved evidence; that is a premise surprise for the owner, not something to patch with a name heuristic.*
- **B3.** `subject`, `actor` and `stakeholder` parameters are distinguishable by their owning membership's metatype (`SubjectMembership`, `ActorMembership`, `StakeholderMembership`). Unverified in the Python API (R2). *If false → requirement and case owners would be flagged on ordinary models (spec review L2-1), or would need a weaker test.*
- **B4.** A finding identity spelled with `str(qualified_name)` is the same across loads and matches the prototype log's spelling, including quoted names such as `'Network Heat Driven Closure'`. Same SysIDE version, same call; the log shows quoted spellings. *If false → pins would not match their findings, and the fusion-tea comparison would show spurious differences.*
- **B5.** No owner the check enumerates lacks a readable document tier. Item 1 reads tiers on broad populations. *If false → valid models get `L2_CHECK_UNVERIFIABLE` ERRORs that no pin can clear.*

## Key Decisions

**Fact and extraction**

- **D1. A separate fact family in the shared layer, not a new `SubsetFacts` kind.** New modules `sysml/parameter_redefinition_facts.py` (pure types) and `sysml/parameter_redefinition_extraction.py` (SysIDE side), mirroring Item 1's split. *Rejected: adding `FactKind.PARAMETER_REDEFINITION` to `SubsetFacts` (L2 would run the occurrence, constraint and site extraction it does not need, and Item 2 is building against `SubsetFacts`'s shape now).* A later item can add this family to `SubsetFacts` with one field.
- **D2. Reuse Item 1's helpers by import, with no edit to Item 1's modules.** `ElementRef`, `SafeLocation`, `safe_location`, and `subset_extraction._element_ref` / `_IdentityError`. The private import follows the precedent in the same layer (`subset_extraction.py:42-46` imports `_ASSERTED_FORMS`). *Rejected: promoting them to public names (a diff to Item 1's module while Item 2 builds against it, for no behavior gain).*
- **D3. Read redefinitions from `heritage.relationships`, as the prototype did.** *Rejected: `owned_redefinitions` (what other modules read), because whether it includes implied relationships is unverified and the prototype's results rest on `heritage`.*
- **D4. The fact records role and direction; the decision excludes.** The extractor keeps `subject`/`actor`/`stakeholder` inputs, marked by role, so the exclusion is visible and tested in pure code. It leaves out standard-library owners and `out`/return parameters, as Item 1 leaves out library elements. *Rejected: filtering special parameters at extraction (hides the exclusion from the decision tests).*
- **D5. Owners enumerated:** `CalculationUsage`, `ConstraintUsage`, `CalculationDefinition`, `ConstraintDefinition`, each with `include_subtypes=True`, de-duplicated by element id. This covers requirements, cases and `assert`/`require`/`assume constraint`. This is a per-call-site opt-in, recorded in the adapter's enumeration table (`syside_adapter.py:150-169`). Adds `Redefinition` and the three membership names to the adapter's closed map.

**The rule**

- **D6. One finding per (input, implied target).** The identity includes the target, so a multiple-typed input can yield several findings. *Rejected: one finding per input listing all targets (the prototype's form; it cannot be pinned by stable identity).*
- **D7. When an explicit redefinition accounts for an implied target.** If all of the input's implied targets share one owning definition, any explicit redefinition on the input accounts for them (spec: "with one type"). Otherwise an implied target is accounted for only by an explicit redefinition whose target has the same owning definition. Defined on the fact's data alone. *Rejected: counting the owner's direct types (another read, and harder to state on inherited shapes).*
- **D8. A target with no name is not flagged.** It is counted as `anonymous_target`. An unnamed formal can only be bound by position, so there is nothing to disagree with and no by-name repair.
- **D9. A finding without a full identity is an unpinnable ERROR.** When the owner or the target has no qualified name, the finding's identity is absent, it stays an ERROR, and its message says why.

**Pin list**

- **D10. Format: TOML, schema `positional-pins/v1`, closed at every level.** Read with `tomllib`. Unknown keys, a wrong schema string, wrong types, duplicate identities, absolute paths or `..` all fail. Entry order is free; output order is sorted.
- **D11. Location and discovery.** The file is named `positional-pins.toml`. `validate` walks up from the validated path to the first directory that holds it, stopping after the project boundary (a directory with `.git`, `pyproject.toml`, `work/BACKLOG.md` or the install manifest, the markers `find_project_root` uses at `cli/__init__.py:122-136`). `validate --positional-pins FILE` overrides discovery. Entry paths are relative to the pin file's own directory. Item 3 may later move the setting under `[tool.agentic-mbse]`. *Rejected: a fixed path under `models/` (partial runs of a subdirectory would not find it); resolving entry paths against the working directory (silent misanchoring).*
- **D12. Scope by file existence.** An unmatched pin is stale if its file was among the validated files, stale (reason "pinned file not found") if the file does not exist, and out of scope if the file exists but was not validated. Matching itself ignores the file, so a moved owner still matches. A misanchored pin list therefore fails loudly instead of reading as all out of scope.
- **D13. Pin-list errors are their own code.** `L2_POSITIONAL_PIN_LIST_INVALID` at ERROR, with a `reason_code` naming the defect. When the list is invalid, the check runs as if no list existed (every mismatch an ERROR) and reports the invalid list. A stale pin is `L2_POSITIONAL_PIN_STALE` at ERROR. *Rejected: reusing `L2_CHECK_UNVERIFIABLE` (that code means the model could not be inspected).*
- **D14. `init` does not ship a starter pin list,** and the docs say how to write one. No list means every mismatch blocks, which is D1's default. A starter would invite adding entries for new mismatches.

**Integration and evidence**

- **D15. The check lives in a sibling module,** `validation/positional_binding.py` (decision and issue rendering) plus `validation/positional_pins.py` (parse and discovery). `level2_structure.py` calls one function. *Rejected: inlining into `level2_structure.py` (it would mix a file-format parser into the L2 module).*
- **D16. "L2 without the check" is measured by running the base revision's L2.** The reproduction exports `ccd57d83`'s `src/` with `git archive` and runs its L2 on the same tree, with the same interpreter. It then asserts that the new L2's non-positional issues equal the base run's issues. *Rejected: a production switch to disable the check (code that exists only for measurement).*
- **D17. agentic-mbse's own citations in the shipped register name the repository and path, without a commit.** The commit that adds the register cannot cite itself. The register's header says these paths refer to the agentic-mbse source at the release that ships the file. sysml-codegen, fusion-tea and dc3 citations carry pinned revisions (`sysml-codegen@b5663c07:path`). Recorded as a deviation from the spec's literal "each citation names its repository and pinned revision".
- **D18. The epic's "dc3 interleave mutation" is the two dc3 shapes the spec names.** These are the WI-008 out-of-order inputs and the prototype's adjacent swap in `'Serial Path 8'`. The epic and prototype record no other dc3 probe (`04-README.md` lists only the swap mutation), so the spec's reading stands.

## Architecture

```
validate PATH [--positional-pins FILE]
  └─ level2_structure.validate_structure(PATH, positional_pins=FILE|None)
       ├─ existing four checks ─────────────────────────────┐
       └─ positional_binding.check(model, PATH, files, FILE|None)
            ├─ extract_parameter_redefinitions(model) ──► ParameterRedefinitionFacts (pure)
            ├─ positional_pins.load(discover or FILE) ──► PinListResult (pure)
            ├─ decide(facts, pins, files) ──► PositionalResult (pure)
            └─ render(result) ──► ValidationIssue[] + metrics
       success = no issue other than (L2_POSITIONAL_BINDING, WARNING)
```

The extraction and the pin loader are the only parts that touch SysIDE or the filesystem. `decide` is a pure function, so policy tests build facts and pins directly.

### Data model

The fact (pure; `parameter_redefinition_facts.py`):

```python
class Origin(StrEnum): EXPLICIT = "explicit"; IMPLIED = "implied"
class ParameterRole(StrEnum): ORDINARY; SUBJECT; ACTOR; STAKEHOLDER
@dataclass(frozen=True)
class RedefinedFormal:
    formal: ElementRef; name: str | None; owning_definition: ElementRef; origin: Origin
@dataclass(frozen=True)
class InputRedefinitionFact:
    owner: ElementRef; input: ElementRef; declared_name: str | None
    role: ParameterRole; location: SafeLocation; redefinitions: tuple[RedefinedFormal, ...]
```

Failures and the aggregate:

```python
class RedefinitionFailureCause(StrEnum):
    OWNERS_UNLISTED; DOCUMENT_TIER_UNREADABLE; INPUTS_UNLISTED; ROLE_UNREADABLE
    REDEFINITIONS_UNREADABLE; TARGET_UNRESOLVED; IDENTITY_UNAVAILABLE
@dataclass(frozen=True)
class RedefinitionFailure: subject: SafeLocation | None; cause: RedefinitionFailureCause; detail: str
@dataclass(frozen=True)
class ParameterRedefinitionFacts:
    owners_enumerated: bool; owners_inspected: int
    facts: tuple[InputRedefinitionFact, ...]; failures: tuple[RedefinitionFailure, ...]
```

`OWNERS_UNLISTED` has no subject and means the whole population is missing. `TARGET_UNRESOLVED` covers a redefinition with no `redefined_feature`, or a target whose owning type or name cannot be read. Facts sort by `(location.sort_key(), input.element_id)`, failures by `(subject.sort_key(), cause, detail)`, as Item 1 does.

Pins and the decision result (pure; `positional_pins.py`, `positional_binding.py`):

```python
@dataclass(frozen=True, order=True)
class FindingIdentity: owner: str; input: str; target: str   # qualified names; input is the declared name
@dataclass(frozen=True)
class Pin: identity: FindingIdentity; file: PurePosixPath; line: int
@dataclass(frozen=True)
class PinList: path: Path; revision: str; recorded: date; pins: tuple[Pin, ...]
PinListResult = PinList | PinListAbsent | PinListInvalid   # absent: searched-from/to; invalid: path, reason_code, detail
```

```python
@dataclass(frozen=True)
class PositionalFinding:
    identity: FindingIdentity | None; input_name: str; target: ElementRef
    location: SafeLocation; pinned: bool
@dataclass(frozen=True)
class PositionalResult:
    findings: tuple[PositionalFinding, ...]; stale: tuple[StalePin, ...]
    out_of_scope: tuple[Pin, ...]; failures: tuple[RedefinitionFailure, ...]
    outcomes: Mapping[InputOutcome, int]; pin_list: PinListResult
```

`InputOutcome` is `explicit`, `anonymous`, `implicit_matching`, `implicit_mismatch`, `new_parameter`, `special_parameter`, `anonymous_target`, one per inspected input, with the prototype's names where they exist so counts compare directly. `StalePin` is a `Pin` plus `reason` (`not_found_in_validated_file` or `pinned_file_missing`).

### The pin-list file

```toml
schema = "positional-pins/v1"
[recorded_against]
revision = "f96ad312c63e8c66695971b12feab971f3ba6eb3"
date = 2026-10-15
[[pin]]
owner = "aries_integrated_plant::heat_exchangers::evaluate"
input = "pbli_available_in"
target = "integrated_heat_electricity::'Network Heat Driven Closure'::divertor_available_in"
file = "models/designs/aries_cs_integrated/plant.sysml"
line = 270
```

Required: `schema`, `recorded_against.revision` (non-empty string) and `recorded_against.date` (a TOML date). There may be zero or more `pin` tables, each with all five keys. `line` is a positive integer kept for review only.

### Issues and metrics

| Situation | Code | Severity | Fails L2 |
|---|---|---|---|
| Unpinned mismatch (or unpinnable) | `L2_POSITIONAL_BINDING` | ERROR | yes |
| Pinned mismatch | `L2_POSITIONAL_BINDING` | WARNING | no |
| Stale pin | `L2_POSITIONAL_PIN_STALE` | ERROR | yes |
| Pin list unreadable, malformed, missing header | `L2_POSITIONAL_PIN_LIST_INVALID` | ERROR | yes |
| Inspection failure | `L2_CHECK_UNVERIFIABLE`, `reason_code="POSITIONAL_<cause>"` | ERROR | yes |

Messages call the finding "a likely authoring hazard in valid SysML" and name both repairs: `in :>> <target>` (by name) and `in <name> redefines <target>` (deliberate rename). They tell the author to choose the intended formal from the definition, not to adopt the inferred target. The pinned WARNING message adds: "Pinned as legacy; this does not show that native values are correct or that the native and generated routes agree."

New L2 metrics: `Positional inputs inspected`, `Positional bindings (blocking)`, `Positional bindings pinned (legacy warning)`, `Positional pins stale`, `Positional pins out of scope`, `Positional unverifiable`, and `Positional pin list` (path with recorded revision and date, or `none found (searched <from> to <to>)`). Out-of-scope pins appear only as a count and a printed line, never as an issue, because any issue would fail L2. When L2 passes with pinned warnings, `print_result`'s header line gains "(N pinned positional warnings; not a value or route-parity check)".

### "Zero inputs inspected"

L2 reports the inspected-input count as a metric and does not turn zero into an issue. A model can honestly have no inputs (calc defs with only a return), and the spec allows `L2_CHECK_UNVERIFIABLE` only for a real evidence failure. A population that could not be listed is such a failure (`OWNERS_UNLISTED`). The zero-is-failure rule belongs to the reproduction: a consumer tree that inspects zero inputs fails the run.

## Required Invariants

- **I1.** Every other L2 code keeps its pass/fail effect. The only change to `success` is excluding `(L2_POSITIONAL_BINDING, WARNING)`, which this check emits only for pinned identities.
- **I2.** A pin never hides a finding, never applies to `L2_CHECK_UNVERIFIABLE`, `L2_POSITIONAL_PIN_STALE` or `L2_POSITIONAL_PIN_LIST_INVALID`, and changes only severity for an exact identity.
- **I3.** `validate` never writes the pin list. No code path generates pin entries, except the reproduction's builder, which reads only the prototype log.
- **I4.** Every inspected owner and input yields exactly one fact or one failure. A failure on one owner does not stop other owners from being checked.
- **I5.** Findings, stale pins, out-of-scope pins and failures are sorted deterministically; two runs on the same tree give byte-identical issue lists.
- **I6.** The decision layer imports neither SysIDE nor the filesystem; the fact types import nothing from SysIDE.
- **I7.** No agentic-mbse code or test imports sysml-codegen. No file in fusion-tea, dc3 or sysml-codegen is written; the reproduction checks each sibling's HEAD and status before and after (`scripts/subset_profile/probe.py:93-99`).
- **I8.** Guidance edits leave every `@pinned` block byte-identical, add no unmarked `in x = x;`, add no `in name = ...::` line, and keep the single `@authoritative` marker.

## Component Overview

- **`sysml/parameter_redefinition_facts.py`.** Pure fact, failure and aggregate types (Data model).
- **`sysml/parameter_redefinition_extraction.py`.** `extract_parameter_redefinitions(model) -> ParameterRedefinitionFacts`. Enumerates owners (D5), skips standard-library owners by document tier, lists `in`/`inout` owned features, reads role from the owning membership and redefinitions from `heritage` (D3). Every read is guarded and turned into a named failure. Two keyword-only seams, `read_owned_features` and `read_heritage` (defaulting to the SysIDE reads), let tests inject a raising read, as the prototype's `heritage_of` did (`04-detector.py:93-95`).
- **`sysml/syside_adapter.py`.** Four names added to the closed type map and its licence-free name set.
- **`validation/positional_pins.py`.** `discover(path) -> Path | None`, `load(path) -> PinListResult`. Strict parsing (D10).
- **`validation/positional_binding.py`.** `decide(facts, pins, validated_files) -> PositionalResult` (pure), `render(result) -> (issues, metrics)`, and `check(model, validated_path, files, explicit_pins)` that wires them (discovery starts at `validated_path` when `explicit_pins` is `None`).
- **`validation/level2_structure.py`, `runner.py`, `cli/__init__.py`.** Accept `positional_pins`; L2 calls `check`; the success rule (I1); the summary line.
- **`sysml/types.py`.** Adds `L2_POSITIONAL_BINDING`, `L2_POSITIONAL_PIN_STALE`, `L2_POSITIONAL_PIN_LIST_INVALID`.
- **Fixtures** under `tests/fixtures/positional_binding/` (Appendix A) and the fusion-tea baseline under `.../baselines/`.
- **Scripts** under `scripts/positional_binding/`: `build_reference.py` (log → pin list), `run_trees.py` (reproduction), `scan_existing_fixtures.py`.
- **Register** `docs/patterns/semantic-hazards.md` and the guidance edits (Appendix C).
- **Evidence** under `.project/active/positional-binding-check/evidence/`: tree logs, the cross-route script and log, the existing-fixture scan, the draft upstream finding.

## Non-Goals

Carried from the spec: no change to generator or SysIDE binding (R4-2); no fusion-tea edit, pin list or migration (R4-3); no proof of the 125's value effect; actions, states and output parameters; ordering among subject/actor/stakeholder; running every shipped example (Item 5); execution-target settings (Item 3). Also out: adding this fact family to `SubsetFacts` (D1), and any "intentional positional use" disposition (R4-1).

## Implementation Notes

- Read `direction` the way `subset_extraction._is_bound_input` does (`:188`): the enum's last dotted segment, lowercased, in `{"in", "inout"}`.
- Order the rule's steps exactly, so each input gets one outcome and the counts compare with the prototype (which tested explicit first, `04-detector.py:121`):
  1. Special role → `special_parameter`.
  2. No declared name → `explicit` if it has an explicit redefinition (`in :>> a`), else `anonymous`. Never flagged.
  3. No implied redefinition → `explicit` if it has an explicit one, else `new_parameter`.
  4. Otherwise apply D7 and D8 per implied target. Any finding → `implicit_mismatch`; else `explicit` if it has an explicit redefinition; else `anonymous_target` if every implied target is unnamed; else `implicit_matching`.
- The pinned-WARNING exclusion is a named predicate in `positional_binding.py`, used by `level2_structure.py`, so the rule exists in one place.
- New fixtures use unquoted package names, so expected identities do not depend on how SysIDE quotes basic names.
- `runner.QUALITY_CHECKS` keeps its shape; pass `positional_pins` to L2 with `functools.partial` when building the list for a run.
- Learning-test results (R1–R6 below) are written into fixture headers and the register as observed SysIDE 0.8.4 behavior, separate from what KerML text says.

## De-risk flags: SysIDE 0.8.4 behavior not verified by reading

Each flag names what the design relies on, what is already observed, and whether a learning test is needed before planning. One learning-test file can cover R1–R6: `tests/test_sysml/test_parameter_redefinition_surface.py`, following `test_conditional_operator_spelling.py`.

**Learning test result (2026-10-18).** All six flags were run against SysIDE 0.8.4. The kept tests are in `tests/learning/test_syside_input_redefinition.py`, and the findings are in `learning-findings.md`. R1(a) holds: in the mixed spelling, `b` implicitly redefines `Sub::a`, so B2 and the spec's criterion stand. R1(b): an input with an explicit redefinition never also gets an implied one, so `multiple_types_with_rename` expects only (q::c, b, Add::q). R2 confirms B3, and the subject, actor and stakeholder all count toward positions. R3 and R5 confirm. R4: positions count `out`, but SysIDE rejects that model with `redefinition-direction-conformance`, so `out_before_in` fails at L1 before L2 runs. R6: the sweeps reach requirement, case and `assert constraint` owners, but never standard-library owners, because `model.elements` covers only the model's own documents.

- **R1. Implied redefinitions on inputs that also have an explicit one, and on siblings of an explicit input.** Observed: the prototype never inspected implied relationships on explicit inputs (it skipped them). Must show, for `calc def Sub { in a; in b; }`: (a) `in b = 3; in :>> a = 10;` gives `b` an implied redefinition of `Sub::a` (B2); (b) for `in y redefines b = 3; in x redefines a = 10;`, whether `y` and `x` also carry implied redefinitions, and of which formals. **Needed before planning.** (a) decides whether a spec criterion is achievable from resolved evidence.
- **R2. Special parameters.** Must show: a `subject`, `actor` and `stakeholder` parameter each appears in `owned_features` with direction `in`, and its `owning_membership` is an instance of `syside.SubjectMembership` / `ActorMembership` / `StakeholderMembership`; a requirement def's `subject vehicle` carries an implied redefinition of `RequirementCheck::subj`; and in `requirement def R { subject v; in lo; in hi; }`, whether the subject counts toward the positions of `lo` and `hi`. **Needed before planning.** It sets the role field (B3) and the requirement fixtures' expected identities.
- **R3. Multiple types and owning definition.** Must show, for `calc c : Sub, Add { in b = 3; in a = 10; }`, whether each input gets one implied redefinition per type (`Sub::a` and `Add::p` for `b`), and that `redefined_feature.owning_type` is the defining type. For `calc def Sub3 :> Sub;`, it must show that the target is `Sub::a`, owned by `Sub`. Recommended, not blocking: D7 handles either answer, and the result sets two fixtures' expected identities.
- **R4. `out` before `in`.** Must show, for `calc def O { out o; in a; in b; }` used as `calc u : O { in a = 1; in b = 2; }`, whether positions count the `out` parameter. KerML text says they do (8.4.4.7.1, cited in spec review L3-4), which would flag `a → O::o` and `b → O::a`. Recommended, not blocking: the rule handles both, and the fixture records the observed result.
- **R5. Anonymous and inherited shapes.** Must show that `declared_name` is `None` for `in : Real = 10` and for `in :>> a`, and that an inherited-but-not-redeclared input does not appear in the owner's `owned_features`. Not needed before planning; the prototype's results imply both.
- **R6. Owner population and tiers.** Must show that the four sweeps with `include_subtypes=True` return requirement, case and `assert constraint` owners; that standard-library owners appear and carry the `StandardLibrary` tier; and that every enumerated owner has a readable tier (B5). Not needed before planning; plan phase 1 can assert it on fixtures and on the dc3 tree.

## Potential Risks

- **R1 fails (no implied redefinition on the mixed spelling).** Mitigation: the learning test runs before the plan. On failure, surface to the owner; the fixture stays with its spec expectation and an observed-result note. No name heuristic.
- **The fusion-tea comparison differs from the log.** Mitigation: the reproduction itemizes added, missing and changed-target identities and stops; surfacing follows the align record's premise-surprise rule.
- **An existing fixture gains a positional ERROR and an existing L2 test now fails.** Mitigation: `scan_existing_fixtures.py` runs first; each case is listed and justified in evidence before any test is updated.
- **Guidance edits break sysml-codegen's conformance test.** Mitigation: I8, plus running that test read-only from the sysml-codegen checkout against this branch as evidence.
- **Pin-list integrity depends on review.** Accepted by the owner (R4-1, "A is fine"); the register and the docs state it.

## Integration Strategy

- Target repos get the check on their next agentic-mbse upgrade. With no pin list, every mismatch blocks L2 (D1). A project with legacy mismatches writes `positional-pins.toml` at its project root by hand, from the findings.
- fusion-tea is not changed. The reproduction measures what its pin move would mean: L2 at the base revision, L2 with the check and no pins, and L2 with the check and the 125-pin list. The fusion-tea pin list and migration stay gated by R4-3.
- The register gives Items 2 and 5 a stable anchor, `semantic-hazards.md#positional-input-binding`.
- The draft upstream finding sits in evidence and is unfiled until the owner (or Item 2) files it. Close lists it in `.project/CURRENT_WORK.md`.

## Validation Approach

- **Fixture suite** (`tests/test_validation/test_positional_binding.py`): each fixture's header lists its exact expected identities and unverifiable count; the test asserts set equality. Includes the 17 prototype cases, the nine the naive control got wrong (marked), and the new cases (Appendix A).
- **Pure decision tests** (same module, no SysIDE): the rule's steps, D7, D8, D9, pin matching, stale and out-of-scope by file, invalid pin lists (unknown key at each level, wrong schema, missing header, duplicate identity, absolute or `..` path, non-date date, unreadable file), and sorted output.
- **Policy test with a model** (inputs bound to valued attributes, not literals, so `LITERAL_BINDING` warnings do not mask the result): unpinned ERROR fails L2; pinned WARNING passes L2 when nothing else is present; changed target gives a new ERROR plus a stale pin; no list gives all ERRORs; a partial-tree run reports out-of-scope pins and still judges in-scope ones stale; the pinned message and the summary line say "not a value or route-parity check".
- **Unverifiable tests**: inject a raising `heritage` read for one input and a raising `owned_features` read for one owner through a seam on the extractor. Each gives `L2_CHECK_UNVERIFIABLE` with its `reason_code`; L2 fails; findings on other owners are still reported; a pin for that input changes nothing.
- **Regression**: `test_integration_regression.py` and the existing L2 tests pass, apart from cases listed by the existing-fixture scan.
- **Cross-route**: `tests/test_validation/test_positional_binding_native_values.py` evaluates the four spellings and the two retained generator fixtures natively (7, -7, 7, 7; gen_byname 7, gen_reversed -7), using `Compiler.evaluate_feature` as `04-eval.py:46-54` does. The generated side is `evidence/cross-route/eval_generated.py` plus its log, run with the dc3 venv (codegen `b5663c07`, TEAx `8d877460`).
- **Shipped text** (`tests/test_shipped_text.py`): the register exists in the wheel, cites `checkFeatureParameterRedefinition`, and every agentic-mbse path it cites exists. Sibling-repo citations are checked with `git cat-file -e <rev>:<path>` when the sibling checkout is present, and skipped with a named reason when it is not. Guidance links and the qualification of "Order does not matter" are asserted. Every new or changed SysML example parses and has its stated positional findings.
- **Reproduction**: Appendix B.

## Next-Stage Handoff

- **Fixed:** the fact and result types, the rule and its step order, D7, the pin-list schema, discovery and anchoring, the scope rule, the issue codes and the success rule (I1), the reproduction's three L2 runs.
- **Open for the plan:** message wording within the stated content, metric label wording, and phase order. Which existing fixtures (if any) gain findings comes from the scan.
- **De-risk first:** R1 and R2, before planning. If R1(a) fails, stop and surface; do not plan around it.
- **ADR candidate at acceptance:** the pin-list file contract (D10–D12) is a target-repo-facing format that Item 3 may relocate; file it with `.project/scripts/adr.sh new` after approval if it passes the density bar.

## Appendix A: Fixture expectations

Owner `q::c` means part `q`'s calc `c`; `Sub` is `calc def Sub { in a; in b; return r = a - b; }`, `Le` is `constraint def Le { in x; in lim; }`, `Add` is `calc def Add { in p; in q; }`. Package prefixes are omitted here; fixture headers carry full qualified names. Results marked (R*n*) are KerML-text expectations to confirm by the learning test.

| Fixture | Expected identities (owner, input, target) |
|---|---|
| 17 prototype cases | As `04-detector-fixtures.log`, expanded per target: e.g. `calc_reversed` → (q::c, b, Sub::a), (q::c, a, Sub::b); `calc_omitted_first` → (q::c, b, Sub::a); `inherit_def_reordered` → (Sub2, a, Sub::b), (Sub2, b, Sub::a); passing cases → none |
| `multiple_types` (prototype) | (q::c, b, Sub::a), (q::c, b, Add::p), (q::c, a, Sub::b), (q::c, a, Add::q) (R3) |
| `mixed_spelling`: `in b = 3; in :>> a = 10;` | (q::c, b, Sub::a) (R1) |
| `reversed_deliberate_rename`: `in y redefines b = 3; in x redefines a = 10;` | none |
| `multiple_types_with_rename`: `calc c : Sub, Add { in x redefines a = 10; in b = 3; }` | (q::c, b, Add::q); plus (q::c, x, Add::p) if R1(b) shows implied targets on explicit inputs |
| `requirement_subject_renamed`, `requirement_actor`, `case_actor`, `requirement_stakeholder` | none |
| `requirement_in_param_swapped` (usage restates its subject) | (r, hi, R::lo), (r, lo, R::hi) (R2) |
| `requirement_nested_constraint_reversed` (`require constraint k : Le { in lim = 5; in x = 3; }`) | (R::k, lim, Le::x), (R::k, x, Le::lim) |
| `dc3_wi008_out_of_order` (dc3 `work/learnings/RAW_LEARNINGS.md:29`, `work/active/WI-008_generator-idiom/design.md:63`) | (c, b_in, D::a_in), (c, a_in, D::b_in) |
| `dc3_serial_path_swap` (dc3 `60b44d5` `designs/ac_coupled/ac_facility.sysml:226-227`, reduced) | the two swapped `eta_0n_in` inputs, each onto the other's formal |
| `inherit_def_extends` (must pass) | none, and no unverifiable result |
| `usage_extra_inputs`: `in a = 10; in b = 3; in extra = 1;` | none (`extra` is a new parameter) |
| `def_adds_first_input`: `calc def D :> Sub { in c; }` | (D, c, Sub::a) |
| `out_before_in` | (u, a, O::o), (u, b, O::a) if positions count `out` (R4); none otherwise |

The naive-control marker lists the nine fixtures `04-detector-naive-control.log` got wrong, so a name-set detector fails the suite.

## Appendix B: The reproduction

**Reference file.** `scripts/positional_binding/build_reference.py` reads `04-detector-tree-fusion-tea.log` only. For each `L2_POSITIONAL_BINDING` line it takes the file and line (`//designs/...:270`, made `models/designs/...`) and the input's qualified name. From the next line it takes the declared name and the target (`implicitly redefines '<target>' by position;`, taking the text between the first `'` after "redefines " and the `' by position`). The owner is the input's qualified name with its last segment removed; the script checks that segment equals the declared name, quoted or not. It asserts 125 entries, 125 distinct identities and 9 distinct files, then writes `tests/fixtures/positional_binding/baselines/fusion-tea-f96ad312.toml` with `revision = f96ad312c63e8c66695971b12feab971f3ba6eb3` and `date = 2026-10-15` (the prototype run). A test re-runs the builder and asserts the committed file is identical.

**Runs.** `scripts/positional_binding/run_trees.py --final-rev REV` imports `export_tree`, `git`, `resolve_rev` and `sibling_state` from `scripts/subset_profile/probe.py`. It records each sibling's state before and after (I7), and writes `evidence/run-trees.md` and `.json` with every revision and the SysIDE version.

- *fusion-tea `f96ad312`*: export the whole commit to `scratch/fusion-tea/`. Then:
  - Run 0: L2 from `ccd57d83`'s archived `src/` (D16), on `scratch/fusion-tea/models`.
  - Run 1: the new L2 with no pin file.
  - Run 2: copy the baseline to `scratch/fusion-tea/positional-pins.toml` and run the new L2, which exercises discovery.
  - Record each run's success and issue counts by code. Assert Run 1's non-positional issues equal Run 0's issues.
  - Compare Run 2's identities with the log's. Itemize added, missing and changed-target identities, and stop on any difference. Expected with no difference: 125 WARNINGs, 0 positional ERRORs, 0 unverifiable, 0 stale.
  - Compare outcome counts with the prototype: `implicit_matching` 5,573, `implicit_mismatch` 125, `new_parameter` 1,956. Explain any difference. Zero inspected inputs fails the run.
- *Mutation*: in a second scratch copy, swap the first pair of adjacent unprefixed inputs (by location order) on an owner whose inputs are all `implicit_matching`. Expect one or more new ERROR identities with the pin list unchanged, and L2 failing.
- *Stale*: in a third copy, rewrite the first pinned input (by identity order) whose right-hand side is not its own name from `in <name> = ...` to `in :>> <name> = ...`. Skipping self-named right-hand sides keeps the rewrite from creating an `L2_SELF_NAMED_BINDING`. Expect exactly that pin stale, every other pin matched, no new ERROR of any L2 code, and L2 failing.
- *dc3 `808464d` and `60b44d5`*: export and run the new L2 with no pins. Expect 0 findings and 0 unverifiable. Compare `implicit_matching` with 302 and 391.

**Slow test.** `tests/test_validation/test_positional_binding_trees.py` (`-m slow`) runs the fusion-tea and dc3 comparisons. It reads checkout paths from `POSITIONAL_BINDING_FUSION_TEA_REPO` and `POSITIONAL_BINDING_DC3_REPO`, exports the pinned revisions itself, and skips with a reason naming the missing variable.

## Appendix C: Register and guidance edits

- **`docs/patterns/semantic-hazards.md`**, anchor `positional-input-binding`. Covers: expected reading; actual semantics, split into KerML text (8.3.3.3.4, `checkFeatureParameterRedefinition`) and SysIDE 0.8.4 observations on named fixtures (the parameterless subdefinition `inherit_def_no_params_usage_reversed`, plus R1–R4 results); cross-route divergence, claimed for calc usages only; the check, its limits and its codes; the pin policy and that a pin certifies nothing about values or routes; fixture paths; upstream links (sysml-codegen POSITIONAL-FORMAL-REDEFINITION, `PROVENANCE.md`; the draft finding, marked unfiled). A "Candidates, not yet reproduced" list holds output override and `[*]`/`[0]`.
- **`docs/patterns/plant-idiom.md`**: qualify `:298` ("Order does not matter" here means a redefine placed after a binding; input order on a calc usage does matter); in D-5 (`:74-79`), say the definition's parameter is renamed; add a short paragraph on positional binding with the by-name and definition-order forms, linking the register. No `@pinned` block changes (I8).
- **`skills/sysml-conventions/SKILL.md`** (`:129`, `:218-226`) and **`project_templates/MODELING_GUIDE.md.template`** (`:145-152`): the same clarification of "rename", one line on order versus `:>>`, and a link to the register. Each keeps its pointer to the authoritative copy.
- **`agents/sysml-expert.md`** (`:117-139`): one sentence on binding constraint formals by name or in definition order, and the subject exclusion, with a link.
- Every new example binds a distinct, unqualified path (`in :>> a = big;`), so it adds no self-binding and no owner-qualified line.

---

**Next Step:** Decide on the R1–R2 learning test. Then `/_my_design_review` in a fresh session, then `/_my_plan`.
