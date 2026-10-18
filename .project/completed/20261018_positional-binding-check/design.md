# Design: Positional-binding hazard and check (EXEC-SUBSET-CONTRACT Item 4)

**Status:** Draft, revision 1 (after design review and learning test, 2026-10-18)
**Owner:** Reid Westwood
**Created:** 2026-10-18
**Branch:** `positional-binding-check` (base `ccd57d83`)
**Complexity:** MEDIUM

## Overview

Add one L2 check, `L2_POSITIONAL_BINDING`, that reports an authored calculation or constraint input whose implied (positional) redefinition lands on a differently named formal. It reads one new fact (each input's resolved redefinitions, marked implied or explicit), applies D1's pin-list policy, and ships with fixtures, a two-tree reproduction, a hazard register entry and guidance edits. Generator behavior and consumer projects are untouched.

**Revision 1 in one paragraph.** The learning test confirmed the rule and the fact shape (R1–R6). It also showed two gaps, now closed. First, an owner whose type did not resolve looked like a clean owner of new parameters; the extractor now detects SysIDE's placeholder types and reports such owners as unverifiable (D19). Second, an input on a requirement or case that lands on a subject slot now gets its own reason and remedy (D20). Pin discovery is reduced to the project root (D11), and pin paths resolve against an explicit pin root (D12). Resolutions for every review finding are in `design-review.md`.

## Related Artifacts

- Spec: `.project/active/positional-binding-check/spec.md` (revised after review)
- Spec review and resolutions: `.project/active/positional-binding-check/spec-review.md`
- Design review and resolutions: `.project/active/positional-binding-check/design-review.md`
- Align record (gates R4-1..R4-3, owner boundary): `.project/active/positional-binding-check/briefs/align.md`
- Product lens: `.project/active/positional-binding-check/product-lens.md`
- Epic: `.project/backlog/epic_executable-subset-contract.md` (Item 4; D1)
- Prototype: `.project/concepts/convince-me-exec-subset/evidence/04-README.md`, `04-detector.py`, `04-fixtures/`, `04-*.log`
- Item 1 archive (fact layer and reproduction pattern): `.project/completed/20261018_exec-subset-profile/`
- Learning test for R1–R6, M1, M4, S4: `.project/active/positional-binding-check/learning-findings.md`; tests in `tests/learning/test_syside_input_redefinition.py`
- Decision records: ADR 0001 (`.project/adr/0001-subset-profile-capability-ownership.md`); this design does not touch the subset contract it governs.
- Epic Required Reading for Item 4: none listed.

## The Point

[INHERITED: epic Item 4; spec Problem] An author who writes correctly named inputs on a calc or constraint usage in a different order than the definition gets a silent swap. SysML binds an unprefixed input by position (KerML 8.3.3.3.4, `checkFeatureParameterRedefinition`), so the model is valid and nothing warns. Native SysIDE 0.8.4 and generated/TEAx execution disagree on the result (-7 vs 7 on the reversed subtraction). fusion-tea `f96ad312` has 125 such mismatches whose value effect is unknown. The knowledge sat in sysml-codegen since July and never reached authors.

The obligation this design serves:
- D1 `[AGENT] (ratified by owner, 2026-10-15)`: new mismatches block; explicitly pinned legacy mismatches warn until migration; a pin certifies neither native values nor agreement between routes.
- `[AGENT]` (spec review L2-2, decided by the orchestrator as execution of D1, not part of D1's ratified text): a pinned warning does not by itself fail L2.
- `[INHERITED: epic principle 5]`: an inspection failure never reads as clean.
- The work must not change how either route binds (R4-2), must not edit fusion-tea (R4-3) or sysml-codegen or Item 2 (owner boundary), and must not describe fusion-tea as clean.

## Research Findings

**L2 today** (`src/agentic_mbse/validation/level2_structure.py`):
- Four checks append `ValidationIssue`s into one list; `success=len(all_issues) == 0` (`:450`), so any WARNING fails L2.
- The unverifiable pattern is `L2_CHECK_UNVERIFIABLE` at ERROR with a message naming the element (`:355-372`). `ValidationIssue.reason_code` (`sysml/types.py:140`) carries a subsystem's own code next to the shared category code (DD-R10).
- The model is loaded with `syside.try_load_model` (`syside_adapter.py:307-323`), which returns a model even when SysIDE reports semantic errors. L1 reads only `diagnostics.parser` (`level1_syntax.py:74`); no level reads `diagnostics.sema`.
- Metrics are a flat dict printed by `print_result` (`validation/common.py:123-151`). No test asserts L2's metric dict as a whole.
- `run_all_checks` calls every level as `check_func(models_path)` (`validation/runner.py:43-50, 98`); `cmd_validate` (`cli/__init__.py:353-365`) has no per-level options yet.
- `discover_sysml_files` globs a directory only (`common.py:71-89`), so "partial scope" means validating a subdirectory.
- `find_project_root` (`cli/__init__.py:122-136`) walks up from the current directory and stops at the first directory holding `work/BACKLOG.md`, the install manifest file `.agentic-mbse/install.json` (`cli/installation.py:13`), or a `.claude/` directory. It does not check `.git` or `pyproject.toml`. Revision 0 misquoted this set.

**Item 1's fact layer** (`src/agentic_mbse/sysml/`):
- `ElementRef` and `SafeLocation` (`fact_refs.py:17-59`) are the pure identity and location types. An anonymous element has qualified name `None` (`fact_refs.py:21-25`). `_element_ref` (`subset_extraction.py:118-127`) builds an `ElementRef` with `str(element.qualified_name)` and raises `_IdentityError` on a bad UUID. `safe_location` (`occurrence_extraction.py:126-143`) never raises.
- `subset_extraction._Collector` (`:380-427`) is the totality pattern: per element, a fact or a named failure; a population that cannot be listed is recorded once.
- No existing fact names the formal an input redefines. `BindingSourceFact.formal` is the input member itself (`subset_extraction.py:210`).
- `constraint_extraction._actuals` (`:774-787`) records `ActualFact.formal_targets` for each constraint-usage parameter from `owned_redefinitions`. The learning test shows `owned_redefinitions` returns the same list as `heritage`, implied entries included (R1). So `formal_targets` is the positional reading, without the implied/explicit mark. See D21.
- `SubsetFacts` (`subset_facts.py:296-336`) has no consumer outside `subset_*` yet, but Item 2 is building against it in sysml-codegen.
- `SysideAdapter` resolves every metatype name through a closed map (`syside_adapter.py:172-283`); `Redefinition`, `SubjectMembership`, `ActorMembership` and `StakeholderMembership` are not in it.

**Learning test** (`learning-findings.md`, SysIDE 0.8.4). The design relies on these observations, each pinned by a test in `tests/learning/test_syside_input_redefinition.py`:
- R1: in `in b = 3; in :>> a = 10;`, `b` implicitly redefines `Sub::a`. An input with an explicit redefinition never also carries an implied one, even under several types. An explicit input still takes its position.
- R2: subject, actor and stakeholder parameters appear in `owned_features` with direction `In`, and are told apart by `owning_membership` type. They count toward positions. An ordinary input's membership is plain `FeatureMembership`.
- R3: an input gets one implied redefinition per type; each target's `owning_type` is the type that declares the formal.
- R4: positions count an `out` parameter, and SysIDE then reports `redefinition-direction-conformance`. A trailing `return` does not shift positions.
- R5: `declared_name` is `None` for `in : Real = 10` and for `in :>> b`, but `name` falls back to the redefined formal's name. The rule must use `declared_name`.
- R6: the four owner sweeps reach requirement, case and `assert constraint` owners, never return standard-library owners, and every owner returned had a readable tier (also on dc3's tree, 159 owners).
- M1: when an owner's type does not resolve, its inputs get no implied redefinition and look like new parameters. The owner's explicit typing points at a shared placeholder (`<placeholder Classifier>`) with `owning_relationship is None`. Unresolved supertypes and unresolved explicit redefinitions point at placeholders the same way (`<placeholder Feature>` for features). Checked on these shapes only.
- M4: in a requirement, case, use case, analysis or verification definition with no subject, the first ordinary input implicitly redefines the library `subj`. SysIDE reports that model as an error ("Subject must be the first input parameter"), in `diagnostics.sema`.
- S4: when a parent usage restates its inputs, the formals are owned by that usage; when the redefining usage also restates its type, each input gets two implied targets, one owned by the parent usage and one by the definition.

**Prototype** (`04-detector.py`):
- It reads `feature.heritage.relationships`, keeps `Redefinition`s, and splits them by `is_implied` (`:117-120`). That surface gave 17/17 fixtures and the 125/0/0 tree results.
- Its "owner inherits unredefined inputs" branch (`:142-153`) is the heuristic the spec drops.
- The fusion-tea log prints, per finding, the input's qualified name, its file and line relative to `models/`, and the target's qualified name. No finding has more than one target. The 125 lines span 9 files.

**Guidance and a cross-repo constraint:**
- `docs/patterns/plant-idiom.md:298` "Order does not matter" is about a redefine placed after a binding.
- The self-binding advice to "rename the input" (`skills/sysml-conventions/SKILL.md:129, 222`; `project_templates/MODELING_GUIDE.md.template:150`; `plant-idiom.md:74-79`) means renaming the definition's parameter (the pinned example, `hif_economics.sysml:100`, renames it in the def). Read as "rename the usage's input", it produces exactly this hazard.
- `agents/sysml-expert.md:117-139` is the one role that teaches binding formals. No other role in `agents/` shows calc-usage inputs.
- sysml-codegen's `tests/conformance/test_self_binding_guidance_contract.py` reads this repo's guidance text. Its rules are listed in invariant I8. Codegen's environment imports agentic-mbse as an editable install of `/home/reid/src/agentic-mbse/src` (`_editable_impl_agentic_mbse.pth` in sysml-codegen's `.venv`; `pyproject.toml:122`), so the test reads whatever branch this checkout has checked out.

## Core Concept

The check is a fact plus a small decision.

The fact says, for each authored input of a calc or constraint (usage or definition, including requirements and cases): its declared name, its direction, its role (ordinary, subject, actor or stakeholder), and every redefinition SysIDE resolved for it. Each redefinition is marked implied or explicit and carries its target formal's identity, name, owning type and role. The extractor sits beside Item 1's fact layer, uses Item 1's identity and location types, and is total: every owner and input yields a fact or a named failure. An owner or input whose type, supertype or redefinition target did not resolve is a failure, never a fact.

The decision reads only facts. An input is flagged for an implied target when the input has a declared name, the target's name differs, and the input's own explicit redefinitions do not account for that target. Each flagged (owner, input, target) triple is a finding identity. When the target is a subject, actor or stakeholder slot, the finding keeps its code and identity but gets its own reason and remedy.

A pin list is a strict TOML file of finding identities that the project recorded as legacy. A finding whose identity is pinned becomes a WARNING; every other finding is an ERROR. The file lives at the project root, or is named on the command line. Its paths resolve against a pin root. A pin that matches no finding is stale (an ERROR) when its file was validated or is missing, and out of scope (a count, not an issue) when its file exists but was not validated.

L2's pass rule changes in one place: a pinned positional WARNING is the only issue that does not count toward failure.

Why this is the right shape: reading SysIDE, the fragile part, happens once into plain data. Everything that is policy (the rule, the role exclusion, pins, scope) is pure code over that data, testable without SysIDE. The pin list never changes what the check sees; it only changes severity for exact identities.

## Key Bets

- **B1.** SysIDE 0.8.4 exposes implied positional redefinitions as `Redefinition` relationships in `heritage.relationships` with `is_implied` true. Confirmed by the prototype and the learning test (R1, R3). *If false on an untested shape → the check misses swaps there.*
- **B2.** In the mixed spelling `in b = 3; in :>> a = 10;`, `b` implicitly redefines `Sub::a`. Confirmed (R1a). *If a later SysIDE drops it → the mixed-spelling fixture fails; surface, do not patch with a name test.*
- **B3.** Special parameters are told apart by owning-membership type. Confirmed for user definitions (R2). Not yet observed for library formals such as `RequirementCheck::subj`, which D20 reads. *If false for library formals → the special-slot reason falls back to the generic swap text; the finding itself is unaffected.*
- **B4.** A finding identity spelled with `str(qualified_name)` is the same across loads and matches the prototype log's spelling, including quoted names. Same SysIDE version and call. Not tested on quoted names (learning-findings "Not checked"). *If false → pins would not match, and the fusion-tea comparison shows spurious differences.*
- **B5.** Every owner the sweeps return has a readable tier. Observed on fixtures and dc3 (R6).
- **B6.** An unresolved type, supertype or redefinition target shows up as a target with `owning_relationship is None`, and no resolved target has that. Observed on the M1 shapes only (typo type, unresolved supertype, unresolved `:>> zz`, unresolved usage `:>>`, partial run). *If false on another shape → an owner with an unresolved reference could still read as clean. The limit is stated in the register.*

## Key Decisions

**Fact and extraction**

- **D1. A separate fact family, L2-internal, not a new `SubsetFacts` kind.** New modules `sysml/parameter_redefinition_facts.py` (pure types) and `sysml/parameter_redefinition_extraction.py` (SysIDE side), mirroring Item 1's split. The family has no version marker, is not part of `SubsetFacts`, and is not a surface Item 2 or sysml-codegen should consume; promoting it needs its own item. Module docstrings say so. *Rejected: adding a kind to `SubsetFacts` (L2 would run extraction it does not need, and Item 2 is building against that shape now).*
- **D2. Reuse Item 1's helpers by import, with no edit to Item 1's modules.** `ElementRef`, `SafeLocation`, `safe_location`, and `subset_extraction._element_ref` / `_IdentityError`, following the private-import precedent at `subset_extraction.py:42-46`. A test in this item asserts those two names still exist, so a rename in Item 1 fails here first. *Rejected: promoting them to public names (a diff to Item 1's module while Item 2 builds against it).*
- **D3. Read redefinitions from `heritage.relationships`, filtered to `Redefinition`.** `owned_redefinitions` returns the same list (R1), so either works; `heritage` is what the prototype and learning test used. Filtering matters: `heritage` also holds implied `FeatureTyping` and `Subsetting` entries.
- **D4. The fact records role and direction; the decision excludes.** Special-role inputs stay in the fact, marked by role, so the exclusion is tested in pure code. `out` and return parameters are not recorded. List inputs with `owned_features` filtered to `in`/`inout`, not `owned_parameters` (which Item 1's constraint facts use), because the learning test verified `owned_features` on all special roles (R2). The standard-library filter uses `SysideAdapter.document_tier` directly; the sweeps never return library owners (R6), so the filter is a guard, tested with a stub owner.
- **D5. Owners enumerated:** `CalculationUsage`, `ConstraintUsage`, `CalculationDefinition`, `ConstraintDefinition`, each with `include_subtypes=True`, de-duplicated by element id. Covers requirements, cases and `assert`/`require`/`assume constraint` (R6). This per-call-site opt-in is recorded in the adapter's enumeration table (`syside_adapter.py:150-169`). Adds `Redefinition` and the three membership names to the adapter's closed map.
- **D19. Unresolved references are failures, detected by placeholder targets.** For each owner, the extractor reads the targets of its explicit `FeatureTyping`, `Subclassification` and `Redefinition` relationships. If any target has `owning_relationship is None`, the owner yields one failure (`UNRESOLVED_OWNER_TYPE`) and none of its inputs become facts. For each input, a placeholder target on one of its own explicit redefinitions (`in :>> zz`) yields an input failure (`UNRESOLVED_INPUT_REDEFINITION`); the owner's other inputs are still judged. Each becomes `L2_CHECK_UNVERIFIABLE` with `reason_code` `POSITIONAL_UNRESOLVED_OWNER_TYPE` or `POSITIONAL_UNRESOLVED_INPUT_REDEFINITION`. The discrimination is pinned by the M1 learning tests it came from (`test_m1_the_owner_keeps_an_explicit_typing_to_a_shared_placeholder_classifier`, `test_m1_unresolved_supertypes_and_redefinitions_also_target_placeholders`), and its limit (verified only on those shapes) is stated in the register. *Rejected: reading `diagnostics.sema` (out of scope; see the follow-up in Next-Stage Handoff); matching the placeholder's name or `memory://` URL (a name test, which the adapter's rules exclude).* An owner whose own `:>>` did not resolve has no qualified name, so its failure is located but unnamed.

**The rule**

- **D6. One finding per (input, implied target).** The identity includes the target, so a multiple-typed input yields one finding per type (R3). The same holds for a redefining usage that also restates its type (S4 row 3): a swapped input there gets two targets, one owned by the parent usage and one by the definition, so a two-input swap gives four findings. *Rejected: deduplicating to one finding per input.* Reasons: the two targets are different formals with different identities; picking a "primary" one would be an arbitrary rule over the redefinition graph; and pins must match exact facts. The cost is that such a swap needs two pins per input to downgrade. No fusion-tea finding has two targets, so the baseline is unaffected.
- **D7. When an explicit redefinition accounts for an implied target, stated over the target's owning type.** If all of the input's implied targets share one owning type, any explicit redefinition on the input accounts for them. Otherwise an implied target is accounted for only by an explicit redefinition whose target has the same owning type. Re-checked against the learning test: in SysIDE 0.8.4 an explicit input never carries implied targets (R1b, R3, S4), so the second branch has no observed case. It stays, because it states the spec's multiple-types rule and costs nothing; pure tests cover it. A deliberate rename inside a redefining usage is not flagged (S4).
- **D8. A target with no name is not flagged.** It is counted as `anonymous_target`. An unnamed formal can only be bound by position.
- **D9. A finding without a full identity is an unpinnable ERROR.** When the owner or target has no qualified name (anonymous `assert constraint : Le { ... }`, anonymous `require constraint`, an owner whose `:>>` did not resolve), the finding stays an ERROR and its message says why. Consequence under D1: a legacy mismatch on an anonymous owner always blocks and must be migrated or the owner named. An anonymous-assert fixture pins this.
- **D20. Subject-slot findings get their own reason and remedy.** When an implied target's role is `subject`, `actor` or `stakeholder` (the library `RequirementCheck::subj`, `Cases::Case::subj`, or a definition's own subject), the finding's `reason_code` is `POSITIONAL_SPECIAL_SLOT` and its message says: "this input lands on the subject (or actor/stakeholder) slot of <type>; declare `subject` (and any `actor`/`stakeholder`) before ordinary inputs". It remains an `L2_POSITIONAL_BINDING` finding with the usual identity, so pinning works the same way. Ordinary swaps carry `reason_code` `POSITIONAL_SWAP`. The learning test shows SysIDE rejects these models (M4), so flagging is correct. The rule applies to any special-role target, user or library, because the remedy is the same; the orchestrator's call names library formals, and this generalization is recorded here. Neither consumer has requirements, so the baseline is unaffected.

**Pin list**

- **D10. Format: TOML, schema `positional-pins/v1`, closed at every level.** Read with `tomllib`. Unknown keys, a wrong schema string, wrong types, duplicate identities, absolute paths or `..` all fail. Entry order is free; output order is sorted.
- **D11. Discovery: the project root only.** `validate` finds the project root with `find_project_root`'s markers (`work/BACKLOG.md`, `.agentic-mbse/install.json`, a `.claude/` directory), starting from the validated path rather than the current directory. `find_project_root` gains an optional `start` argument; its default stays `Path.cwd()`, so existing callers are unchanged. If a root is found, the only file looked for is `<root>/positional-pins.toml`. There is no walk-up for the pin file itself and no search of subdirectories. A `positional-pins.toml` anywhere else is ignored; the metric prints the one path looked at, so a misplaced file is visible. If no root is found (for example, a `git archive` export with no markers), nothing is discovered and every mismatch is an ERROR; the metric reads `none (no project root above <path>; pass --positional-pins)`. Item 3 may later move the setting under `[tool.agentic-mbse]`. *Rejected: the revision-0 walk to the first folder holding a pin file (verdicts depended on the path given, and an unmarked tree walked to `/`).*
- **D12. Pin paths resolve against a pin root: the pin file's directory by default, overridable with `--positional-pins-root DIR`.** A discovered file sits at the project root, so its pin root is the project root. `--positional-pins FILE` names a file anywhere; `--positional-pins-root DIR` says which tree its paths describe. `--positional-pins-root` without `--positional-pins` is a usage error, and a root that is not a directory is a usage error. The metric prints the pin root. *Rejected: always resolving against the validated path's project root (it fails on exactly the unmarked exported trees the reproduction uses, and hides the anchor from the command line).*
- **D13. Scope by file existence under the pin root.** An unmatched pin is stale if its file was among the validated files, stale (reason `pinned_file_missing`) if the file does not exist, and out of scope if it exists but was not validated. Matching ignores the file, so a moved owner still matches. The file is still load-bearing for scope: on a partial run, an owner moved into an unvalidated file reads as stale. The pin-list docs say so.
- **D14. Pin-list errors are their own code.** `L2_POSITIONAL_PIN_LIST_INVALID` at ERROR with a `reason_code` naming the defect. When invalid, the check runs as if no list existed and reports the invalid list. A stale pin is `L2_POSITIONAL_PIN_STALE` at ERROR.
- **D15. `init` ships no starter pin list.** Shipped docs explain the format and say: a pin records a mismatch that existed at `recorded_against`; a new mismatch is fixed with `in :>> name` or `in name redefines target`, not pinned; and pinning a new mismatch is the disposition reserved to the owner under R4-1. The ERROR message prints the five fields (owner, input, target, file, line) so a legacy entry can be copied exactly; the docs say entries are copied for legacy findings only.

**Integration and evidence**

- **D16. The check lives in sibling modules,** `validation/positional_binding.py` (decision and rendering) and `validation/positional_pins.py` (parse and discovery). `level2_structure.py` calls one function.
- **D17. "L2 without the check" is measured by running the base revision's L2,** from `ccd57d83`'s archived `src/`, with the same interpreter. Run 0 records `agentic_mbse.__file__` and asserts it resolves inside the archive, because the venv's editable install could otherwise shadow it. The reproduction then asserts the new L2's non-positional issues equal Run 0's issues. *Rejected: a production switch to disable the check.*
- **D18. agentic-mbse's own citations in the shipped register name the repository and path, without a commit.** The commit that adds the register cannot cite itself; the register's header says these paths refer to the source at the release that ships the file. Other repositories carry pinned revisions (`sysml-codegen@b5663c07:path`).
- **D21. Relation to Item 1's `ActualFact.formal_targets`.** For a constraint-usage input, Item 1's `formal_targets` should equal the set of all target qualified names in this fact, both origins, because both read the same relationship list (R1). A consistency test on the constraint fixtures asserts it, reading Item 1's facts without editing them. The observation to surface (to the owner and Item 2's agent, through the evidence and close notes): Item 1's constraint facts carry the positional reading without the implied/explicit mark, so a consumer of `formal_targets` gets native-SysIDE semantics. That agrees with native SysIDE and disagrees with codegen's by-name wiring on the calc case (`04-eval.log`). This item does not change either.
- **D22. The epic's "dc3 interleave mutation" is the two dc3 shapes the spec names** (WI-008 out-of-order inputs and the adjacent swap in `'Serial Path 8'`). No other dc3 probe is recorded.

## Architecture

```
validate PATH [--positional-pins FILE [--positional-pins-root DIR]]
  └─ level2_structure.validate_structure(PATH, positional_pins=FILE|None, pin_root=DIR|None)
       ├─ existing four checks
       └─ positional_binding.check(model, PATH, files, FILE|None, DIR|None)
            ├─ extract_parameter_redefinitions(model) ──► ParameterRedefinitionFacts (pure)
            ├─ positional_pins.load(FILE or <project root>/positional-pins.toml, DIR) ──► PinListResult
            ├─ decide(facts, pins, files) ──► PositionalResult (pure)
            └─ render(result) ──► ValidationIssue[] + metrics
       success = no issue other than (L2_POSITIONAL_BINDING, WARNING)
```

The extractor and the pin loader are the only parts that touch SysIDE or the filesystem.

### Data model

The fact (pure; `parameter_redefinition_facts.py`):

```python
class Origin(StrEnum): EXPLICIT; IMPLIED
class ParameterRole(StrEnum): ORDINARY; SUBJECT; ACTOR; STAKEHOLDER
class Direction(StrEnum): IN; INOUT
@dataclass(frozen=True)
class RedefinedFormal:
    formal: ElementRef; name: str | None; owning_type: ElementRef; role: ParameterRole; origin: Origin
@dataclass(frozen=True)
class InputRedefinitionFact:
    owner: ElementRef; input: ElementRef; declared_name: str | None; direction: Direction
    role: ParameterRole; location: SafeLocation; redefinitions: tuple[RedefinedFormal, ...]
```

Failures and the aggregate:

```python
class RedefinitionFailureCause(StrEnum):
    OWNERS_UNLISTED; DOCUMENT_TIER_UNREADABLE; UNRESOLVED_OWNER_TYPE; INPUTS_UNLISTED
    ROLE_UNREADABLE; REDEFINITIONS_UNREADABLE; UNRESOLVED_INPUT_REDEFINITION
    TARGET_UNREADABLE; IDENTITY_UNAVAILABLE
@dataclass(frozen=True)
class RedefinitionFailure: subject: SafeLocation | None; cause: RedefinitionFailureCause; detail: str
@dataclass(frozen=True)
class ParameterRedefinitionFacts:
    owners_enumerated: bool; owners_inspected: int
    facts: tuple[InputRedefinitionFact, ...]; failures: tuple[RedefinitionFailure, ...]
```

`OWNERS_UNLISTED` has no subject and means the population is missing. `TARGET_UNREADABLE` covers a redefinition with no `redefined_feature`, or a target whose owning type, name or role cannot be read. Facts sort by `(location.sort_key(), input.element_id)`, failures by `(subject.sort_key(), cause, detail)`.

Pins and the decision result (pure; `positional_pins.py`, `positional_binding.py`):

```python
@dataclass(frozen=True, order=True)
class FindingIdentity: owner: str; input: str; target: str   # qualified names; input is the declared name
@dataclass(frozen=True)
class Pin: identity: FindingIdentity; file: PurePosixPath; line: int
@dataclass(frozen=True)
class PinList: path: Path; pin_root: Path; revision: str; recorded: date; pins: tuple[Pin, ...]
@dataclass(frozen=True)
class PinListAbsent: project_root: Path | None; looked_at: Path | None   # None, None: no project root
@dataclass(frozen=True)
class PinListInvalid: path: Path; reason_code: str; detail: str
```

```python
class FindingReason(StrEnum): SWAP = "POSITIONAL_SWAP"; SPECIAL_SLOT = "POSITIONAL_SPECIAL_SLOT"
@dataclass(frozen=True)
class PositionalFinding:
    identity: FindingIdentity | None; input_name: str; target: RedefinedFormal
    location: SafeLocation; reason: FindingReason; pinned: bool
@dataclass(frozen=True)
class PositionalResult:
    findings: tuple[PositionalFinding, ...]; stale: tuple[StalePin, ...]; out_of_scope: tuple[Pin, ...]
    failures: tuple[RedefinitionFailure, ...]; outcomes: Mapping[InputOutcome, int]; pin_list: PinListResult
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

Required: `schema`, `recorded_against.revision` (non-empty string) and `recorded_against.date` (a TOML date). Zero or more `pin` tables, each with all five keys. `line` is a positive integer kept for review. `file` is relative to the pin root.

### Issues and metrics

| Situation | Code | Severity | `reason_code` | Fails L2 |
|---|---|---|---|---|
| Unpinned or unpinnable mismatch | `L2_POSITIONAL_BINDING` | ERROR | `POSITIONAL_SWAP` / `POSITIONAL_SPECIAL_SLOT` | yes |
| Pinned mismatch | `L2_POSITIONAL_BINDING` | WARNING | same | no |
| Stale pin | `L2_POSITIONAL_PIN_STALE` | ERROR | `not_found_in_validated_file` / `pinned_file_missing` | yes |
| Pin list unreadable, malformed, missing header | `L2_POSITIONAL_PIN_LIST_INVALID` | ERROR | the defect | yes |
| Inspection failure, unresolved reference | `L2_CHECK_UNVERIFIABLE` | ERROR | `POSITIONAL_<cause>` | yes |

Swap messages call the finding "a likely authoring hazard in valid SysML" and name both repairs, `in :>> <target>` (by name) and `in <name> redefines <target>` (deliberate rename), telling the author to choose the intended formal from the definition. Special-slot messages carry D20's text instead. The pinned WARNING adds: "Pinned as legacy; this does not show that native values are correct or that the native and generated routes agree."

New L2 metrics: `Positional inputs inspected`, `Positional bindings (blocking)`, `Positional bindings pinned (legacy warning)`, `Positional pins stale`, `Positional pins out of scope`, `Positional unverifiable`, and `Positional pin list` (path, pin root, recorded revision and date; or the absent text from D11). Out-of-scope pins appear only as a count and a printed line, never as an issue. When L2 passes with pinned warnings, `print_result`'s header line gains "(N pinned positional warnings; not a value or route-parity check)".

L2 does not turn zero inspected inputs into an issue: a model can honestly have none, and the spec allows `L2_CHECK_UNVERIFIABLE` only for real evidence failures. The reproduction fails a consumer tree that inspects zero inputs.

## Required Invariants

- **I1.** `[AGENT]` (spec review L2-2). Every other L2 code keeps its pass/fail effect. The only change to `success` is excluding `(L2_POSITIONAL_BINDING, WARNING)`, which this check emits only for pinned identities.
- **I2.** A pin never hides a finding, never applies to `L2_CHECK_UNVERIFIABLE`, `L2_POSITIONAL_PIN_STALE` or `L2_POSITIONAL_PIN_LIST_INVALID`, and changes only severity for an exact identity.
- **I3.** `validate` never writes the pin list. No code path generates pin entries except the reproduction's builder, which reads only the prototype log.
- **I4.** Every inspected owner and input yields exactly one fact or one failure. An owner with an unresolved type, supertype or `:>>` target yields a failure, and its inputs are never counted as new parameters. A failure on one owner does not stop other owners from being checked.
- **I5.** Findings, stale pins, out-of-scope pins and failures are sorted deterministically; two runs on the same tree give byte-identical issue lists.
- **I6.** The decision layer imports neither SysIDE nor the filesystem; the fact types import nothing from SysIDE.
- **I7.** No agentic-mbse code or test imports sysml-codegen. No file in fusion-tea, dc3 or sysml-codegen is written; the reproduction checks each sibling's HEAD and status before and after (`scripts/subset_profile/probe.py:93-99`).
- **I8.** Guidance edits keep everything sysml-codegen's `tests/conformance/test_self_binding_guidance_contract.py` enforces:
  - Exactly one `@authoritative calculation-binding-rule` marker, in `docs/patterns/plant-idiom.md`.
  - At least seven `@pinned` blocks in `plant-idiom.md`, none reworded (each stays an ordered line subsequence of its codegen fixture), and exactly one pinning the `SI_SELF_BINDING` refusal.
  - No unmarked `in x = x;` / `in x = x}` anywhere in `agents/`, `skills/`, `.claude/`, `docs/patterns/` or `project_templates/`.
  - Owner-qualified binding counts unchanged per file (`expose-pattern.md` 6, `cross-file-binding.md` 2, `adr002-calculations.md` 2, `syntax-reference.md` 1, `plant-idiom.md` 4, all four inside pinned blocks) and no new file with a match. The pattern `\bin\s+[\w']+\s*=\s*[^;=\n]*::` matches prose lines too, so no new line of prose or code may contain `in <name> = ...::`. In practice: write qualified targets in prose as "`b` lands on `Sub::a`", never as "`in b = 3` binds `Sub::a`".
  - The three "Won't resolve" negatives stay, one line each (`common-mistakes.md`, `cross-file-binding.md`, `syntax-reference.md`).
  - The pointer surfaces `skills/sysml-conventions/SKILL.md`, `project_templates/MODELING_GUIDE.md.template` and `project_templates/MODELING_PROCESS.md.template` keep the text `plant-idiom.md` and the phrase "Binding a modelled value into a calculation", and carry no `@authoritative` marker.
  - No file under `.claude/` contains a line matching `\bin\s+[\w']+\s*=`. The scan is on disk and skips symlinks, so copied installs count. This checkout installs with `--link-mode symlink`; the evidence records the install mode.

## Component Overview

- **`sysml/parameter_redefinition_facts.py`.** Pure fact, failure and aggregate types; docstring states the L2-internal status (D1).
- **`sysml/parameter_redefinition_extraction.py`.** `extract_parameter_redefinitions(model) -> ParameterRedefinitionFacts`. Enumerates owners (D5), skips library owners by tier, checks placeholder targets (D19), lists `in`/`inout` owned features, reads role from the owning membership and redefinitions from `heritage` (D3), and reads each target's owning type and role. Keyword-only seams `list_owners`, `read_owned_features` and `read_heritage` (defaulting to the SysIDE reads) let tests inject failures, as the prototype's `heritage_of` did (`04-detector.py:93-95`).
- **`sysml/syside_adapter.py`.** Four names added to the closed type map and its licence-free name set.
- **`cli/__init__.py`.** `find_project_root(start=None)`; `validate --positional-pins FILE --positional-pins-root DIR`.
- **`validation/positional_pins.py`.** `discover(validated_path) -> Path | PinListAbsent`, `load(path, pin_root) -> PinListResult`. Strict parsing (D10).
- **`validation/positional_binding.py`.** `decide(facts, pins, validated_files) -> PositionalResult` (pure), `render(result) -> (issues, metrics)`, `check(...)` wiring them, and the named predicate `is_pinned_positional_warning(issue)` used by L2's success rule.
- **`validation/level2_structure.py`, `runner.py`.** Accept and pass the two options (via `functools.partial`); call `check`; apply the success rule (I1); the summary line.
- **`sysml/types.py`.** Adds `L2_POSITIONAL_BINDING`, `L2_POSITIONAL_PIN_STALE`, `L2_POSITIONAL_PIN_LIST_INVALID`.
- **Fixtures** under `tests/fixtures/positional_binding/` (Appendix A) and the fusion-tea baseline under `.../baselines/`.
- **Scripts** under `scripts/positional_binding/`: `build_reference.py` (log → pin list), `run_trees.py` (reproduction), `scan_existing_fixtures.py`.
- **Register** `docs/patterns/semantic-hazards.md` and the guidance edits (Appendix C).
- **Evidence** under `.project/active/positional-binding-check/evidence/`: tree logs, the cross-route script and log, the existing-fixture scan, the codegen conformance run, the draft upstream finding.

## Non-Goals

Carried from the spec: no change to generator or SysIDE binding (R4-2); no fusion-tea edit, pin list or migration (R4-3); no proof of the 125's value effect; actions, states and output parameters; ordering among subject/actor/stakeholder; running every shipped example (Item 5); execution-target settings (Item 3). Also out:
- Adding this fact family to `SubsetFacts` (D1).
- Any "intentional positional use" disposition (R4-1).
- Reporting SysIDE semantic diagnostics (`diagnostics.sema`), because it is an L1 gap wider than this item; proposed as a follow-up (Next-Stage Handoff).
- Searching the tree for misplaced pin files (D11).

## Implementation Notes

- Read `direction` the way `subset_extraction._is_bound_input` does (`:188`): the enum's last dotted segment, lowercased, in `{"in", "inout"}`.
- Read the input's name with `declared_name`, never `name` (R5).
- Order the rule's steps exactly, so each input gets one outcome and counts compare with the prototype (which tested explicit first, `04-detector.py:121`):
  1. Special role → `special_parameter`.
  2. No declared name → `explicit` if it has an explicit redefinition, else `anonymous`. Never flagged.
  3. No implied redefinition → `explicit` if it has an explicit one, else `new_parameter`.
  4. Otherwise apply D7 and D8 per implied target. Any finding → `implicit_mismatch`; else `explicit` if it has an explicit redefinition; else `anonymous_target` if every implied target is unnamed; else `implicit_matching`.
- D19 runs before step 1: an owner with a placeholder target never reaches the rule.
- New fixtures use unquoted package names. Requirement and case usage fixtures restate the subject, and any actor or stakeholder, before ordinary inputs; otherwise SysIDE reports a subject-position error (R2) and the fixture tests something else.
- Learning-test results go into fixture headers and the register as observed SysIDE 0.8.4 behavior, separate from what KerML text says.
- Plan phase 1 adds two learning-test lines: that a library formal such as `RequirementCheck::subj` reads `SubjectMembership` (B3, needed by D20), and an `inout` input's redefinitions (not yet checked).

## Potential Risks

- **The fusion-tea comparison differs from the log.** The reproduction itemizes added, missing and changed-target identities and stops; surfacing follows the align record's premise-surprise rule.
- **An existing fixture gains a positional ERROR, or an unverifiable result from an unresolved type.** `scan_existing_fixtures.py` runs first; each case is listed and justified in evidence before any test is updated. Multi-file fixtures must be loaded as their whole directory, or they will read as unresolved (D19).
- **Partial-tree runs of a non-self-contained subfolder report unverifiable owners.** That is correct (its definitions are not loaded) and documented. The spec's partial-scope test uses a self-contained subfolder, and a second case shows the unverifiable result for a non-self-contained one.
- **The placeholder test is verified on five shapes only (B6).** Stated in the register; a later SysIDE that resolves differently is caught by the M1 learning tests.
- **The owner sweep silently returning nothing** (a SysIDE change) is guarded only by the retained R6 learning test and the reproduction's zero-inspected rule.
- **Guidance edits break sysml-codegen's conformance test.** I8, plus running that test read-only from the sysml-codegen checkout as evidence, recording `agentic_mbse.__file__` from codegen's environment and this checkout's HEAD.
- **Pin-list integrity depends on review.** Accepted by the owner (R4-1, "A is fine"); the register and docs state it.

## Integration Strategy

- Target repos get the check on their next agentic-mbse upgrade. With no pin list, every mismatch blocks L2 (D1). A project with legacy mismatches writes `positional-pins.toml` at its project root by hand, from the findings that existed at the revision it records.
- fusion-tea is not changed. The reproduction measures what its pin move would mean. The fusion-tea pin list and migration stay gated by R4-3.
- The register gives Items 2 and 5 a stable anchor, `semantic-hazards.md#positional-input-binding`.
- The draft upstream finding sits in evidence and is unfiled until the owner (or Item 2) files it. Close lists it, and D21's observation, in `.project/CURRENT_WORK.md`.

## Validation Approach

- **Fixture suite** (`tests/test_validation/test_positional_binding.py`): each fixture's header lists its exact expected identities, reasons and unverifiable results; the test asserts set equality. Includes the 17 prototype cases, the nine the naive control got wrong (marked), and the new cases (Appendix A).
- **Pure decision tests** (no SysIDE): the rule's steps, D6, D7 (both branches), D8, D9, D20, pin matching, stale and out-of-scope by file, the pin root, invalid pin lists (unknown key at each level, wrong schema, missing header, duplicate identity, absolute or `..` path, non-date date, unreadable file), and sorted output.
- **Discovery tests**: a project root found from the validated path (each of the three markers), no root above the path, a pin file below the root ignored, `--positional-pins` with and without `--positional-pins-root`, and the two usage errors.
- **Policy test with a model** (inputs bound to valued attributes, not literals, so `LITERAL_BINDING` warnings do not mask the result): unpinned ERROR fails L2; pinned WARNING passes L2 when nothing else is present; changed target gives a new ERROR plus a stale pin; no list gives all ERRORs; a partial run of a self-contained subfolder reports out-of-scope pins and still judges in-scope ones stale; the pinned message and summary line say "not a value or route-parity check".
- **Unverifiable tests**: inject a raising owner sweep (`OWNERS_UNLISTED`), a raising `owned_features` read for one owner, and a raising `heritage` read for one input, through the extractor seams. Load the M1 shapes (typo type, unresolved supertype, unresolved `:>> zz`, partial run). Each gives `L2_CHECK_UNVERIFIABLE` with its `reason_code`; L2 fails; findings on other owners are still reported; a pin for an affected input changes nothing.
- **Item 1 relation**: the D21 consistency test, and a test that `_element_ref` and `_IdentityError` still exist (D2).
- **Regression**: `test_integration_regression.py` and the existing L2 tests pass, apart from cases listed by the existing-fixture scan.
- **Cross-route**: `tests/test_validation/test_positional_binding_native_values.py` evaluates the four spellings and the two retained generator fixtures natively (7, -7, 7, 7; gen_byname 7, gen_reversed -7), using `Compiler.evaluate_feature` as `04-eval.py:46-54` does; the mixed spelling evaluates to no value (R1). The generated side is `evidence/cross-route/eval_generated.py` plus its log, run with the dc3 venv (codegen `b5663c07`, TEAx `8d877460`).
- **Shipped text** (`tests/test_shipped_text.py`): the register exists in the wheel, cites `checkFeatureParameterRedefinition`, states the legacy-only rule (D15) and the placeholder limit (B6), and every agentic-mbse path it cites exists. Sibling-repo citations are checked with `git cat-file -e <rev>:<path>` when the sibling checkout is present, else skipped with a named reason. Guidance links and the qualification of "Order does not matter" are asserted.
- **Changed examples**: each SysML fence this item adds or changes carries a marker comment directly above it, `<!-- @positional-example expect="none" -->` or `expect="<owner>|<input>|<target>; ..."`. A test collects every marked fence in the shipped trees, loads it, and asserts parse success and exactly the stated positional findings, plus no `L2_SELF_NAMED_BINDING` on by-name examples. The marker is not one codegen's test parses, so those fences stay subject to I8's scans.
- **Repository checks**: `uv run pytest tests/`, `uv run mypy src/`, `uv run ruff check src/ tests/` pass. The evidence lists which tests needed the SysIDE licence and which slow tests ran or skipped.
- **Reproduction**: Appendix B.

## Next-Stage Handoff

- **Fixed:** the fact and result types, D19's placeholder test, the rule and its step order, D6, D7, D20, the pin-list schema, discovery (D11), the pin root (D12), the scope rule, the issue codes and the success rule (I1), the reproduction's runs.
- **Open for the plan:** message wording within the stated content, metric label wording, phase order. Which existing fixtures gain findings comes from the scan.
- **First plan phase:** the two learning-test lines in Implementation Notes, and confirming that `validate` rejects `out_before_in` at L1 (see Appendix A). If L1 passes it (the R4 diagnostic may be semantic, which L1 does not read), surface it rather than change the fixture's role.
- **Follow-up proposal for the backlog (orchestrator files):** `VALIDATE-SEMA-DIAGNOSTICS` — no validation level reports SysIDE semantic diagnostics (`diagnostics.sema`), so unresolved names, subject-position and direction-conformance errors pass `validate`; add them at L1.
- **ADR candidate at acceptance:** the pin-list file contract (D10–D13). File with `.project/scripts/adr.sh new` after approval if it passes the density bar.

## Appendix A: Fixture expectations

`Sub` is `calc def Sub { in a; in b; return r = a - b; }`, `Le` is `constraint def Le { in x; in lim; }`, `Add` is `calc def Add { in p; in q; }`. Owner `q::c` means part `q`'s calc `c`. Package prefixes are omitted; fixture headers carry full qualified names. Reason is `SWAP` unless stated. Every expectation below is confirmed by the learning test unless marked.

| Fixture | Expected result |
|---|---|
| 17 prototype cases | As `04-detector-fixtures.log`, expanded per target: `calc_reversed` → (q::c, b, Sub::a), (q::c, a, Sub::b); `calc_omitted_first` → (q::c, b, Sub::a); `inherit_def_reordered` → (Sub2, b, Sub::a), (Sub2, a, Sub::b); `inherit_def_no_params_usage_reversed` → (q::c, b, Sub::a), (q::c, a, Sub::b); passing cases → none |
| `multiple_types` | (q::c, b, Sub::a), (q::c, b, Add::p), (q::c, a, Sub::b), (q::c, a, Add::q) |
| `mixed_spelling`: `in b = 3; in :>> a = 10;` | (q::c, b, Sub::a) |
| `reversed_deliberate_rename`: `in y redefines b = 3; in x redefines a = 10;` | none |
| `multiple_types_with_rename`: `calc c : Sub, Add { in x redefines a = 10; in b = 3; }` | (q::c, b, Add::q) |
| `subpart_restated_type_swap` (S4 row 3): `calc :>> c : Sub { in b = 3; in a = 10; }` in `Q4 :> Q1`, `Q1` has `calc c : Sub { in a; in b; }` | (Q4::c, b, Q1::c::a), (Q4::c, b, Sub::a), (Q4::c, a, Q1::c::b), (Q4::c, a, Sub::b) |
| `subpart_deliberate_rename`: `calc :>> c { in local redefines a = 10; in b = 3; }` | none |
| `requirement_subject_renamed`, `requirement_actor`, `case_actor`, `requirement_stakeholder` (subjects, actors and stakeholders restated in usages) | none |
| `requirement_in_param_swapped`: `requirement r : R { subject v : V; in hi = 3; in lo = 1; }` | (r, hi, R::lo), (r, lo, R::hi) |
| `requirement_nested_constraint_reversed` | (R::k, lim, Le::x), (R::k, x, Le::lim) |
| `requirement_def_without_subject`: `requirement def X { in lo; in hi; }` | (X, lo, Requirements::RequirementCheck::subj), reason `SPECIAL_SLOT` |
| `case_def_without_subject` | (X, lo, Cases::Case::subj), reason `SPECIAL_SLOT` |
| `anonymous_assert_reversed`: `assert constraint : Le { in lim = 5; in x = 3; }` | two unpinnable ERRORs (identity absent), even with a pin list present |
| `dc3_wi008_out_of_order` (dc3 `work/learnings/RAW_LEARNINGS.md:29`, `work/active/WI-008_generator-idiom/design.md:63`) | (c, b_in, D::a_in), (c, a_in, D::b_in) |
| `dc3_serial_path_swap` (dc3 `60b44d5` `designs/ac_coupled/ac_facility.sysml:226-227`, reduced) | the two swapped `eta_0n_in` inputs, each onto the other's formal |
| `inherit_def_extends` (must pass) | none, and no unverifiable result |
| `usage_extra_inputs`: `in a = 10; in b = 3; in extra = 1;` | none |
| `def_adds_first_input`: `calc def D :> Sub { in c; }` | (D, c, Sub::a) |
| `unresolved_type`: `calc c : Sbu { in b = 3; in a = 10; }`; same for `constraint k : Lee` | `L2_CHECK_UNVERIFIABLE`, `POSITIONAL_UNRESOLVED_OWNER_TYPE`; no finding, no `new_parameter` |
| `unresolved_supertype`: `calc def D :> Missing { in c; }` | unverifiable, `POSITIONAL_UNRESOLVED_OWNER_TYPE` |
| `unresolved_input_redefinition`: `calc c : Sub { in :>> zz = 1; in b = 3; }` | unverifiable for `zz`'s input, `POSITIONAL_UNRESOLVED_INPUT_REDEFINITION`; `b` judged normally |
| `partial_run/` (`designs/` validated without its sibling `defs/`) | unverifiable per owner; validating the parent finds the swap |
| `out_before_in`: `calc def O { out o; in a; in b; }`, `calc u : O { in a = 1; in b = 2; }` | Level-1 rejection fixture: the test asserts `validate` fails at L1; L2 never runs. Not an L2 pass/flag fixture. The facts (a → O::o, b → O::a) stay recorded in the learning test only |

## Appendix B: The reproduction

**Reference file.** `scripts/positional_binding/build_reference.py` reads `04-detector-tree-fusion-tea.log` only. For each `L2_POSITIONAL_BINDING` line it takes the file and line (`//designs/...:270`, made `models/designs/...`) and the input's qualified name. From the next line it takes the declared name and the target (the text between the first `'` after "redefines " and the `' by position`). The owner is the input's qualified name without its last segment; the script checks that segment equals the declared name, quoted or not. It asserts 125 entries, 125 distinct identities and 9 distinct files, then writes `tests/fixtures/positional_binding/baselines/fusion-tea-f96ad312.toml` with `revision = f96ad312c63e8c66695971b12feab971f3ba6eb3` and `date = 2026-10-15`. A test re-runs the builder and asserts the committed file is identical.

**Runs.** `scripts/positional_binding/run_trees.py --final-rev REV` imports `export_tree`, `git`, `resolve_rev` and `sibling_state` from `scripts/subset_profile/probe.py`, records each sibling's state before and after (I7), and writes `evidence/run-trees.md` and `.json` with every revision and the SysIDE version.

- *fusion-tea `f96ad312`*, exported whole to `scratch/fusion-tea/`:
  - Run 0: L2 from `ccd57d83`'s archived `src/` (D17), recording and asserting `agentic_mbse.__file__` inside the archive.
  - Run 1: the new L2, no pin options. Record the discovery result: whatever `find_project_root` finds from `scratch/fusion-tea/models`, and that no pin file is there. Assert the pin-list metric says "none".
  - Run 2 (override, no copy): `--positional-pins tests/fixtures/positional_binding/baselines/fusion-tea-f96ad312.toml --positional-pins-root scratch/fusion-tea`.
  - Run 3 (discovery): in a separate copy, verify a project-root marker exists at the copy's root. If none does, create an empty `work/BACKLOG.md` there and record that in the evidence. Copy the baseline to `<copy>/positional-pins.toml`, run with no pin options, and assert the discovered path and that the result equals Run 2's.
  - Assert Run 1's non-positional issues equal Run 0's issues. Record each run's success and issue counts by code.
  - Compare Run 2's identities with the log's: itemize added, missing and changed-target identities, and stop on any difference. Expected: 125 WARNINGs, 0 positional ERRORs, 0 unverifiable, 0 stale.
  - Compare outcome counts with the prototype: `implicit_matching` 5,573, `implicit_mismatch` 125, `new_parameter` 1,956. Explain any difference. Zero inspected inputs fails the run.
- *Mutation*, with Run 2's override options against a fresh copy. The site is chosen from source text, without the check: in sorted file order, the first `calc` or `constraint` usage line `<kw> <name> : <Def> {` followed by two adjacent lines matching `^\s*in\s+([A-Za-z_]\w*)\s*=[^;]*;\s*$` whose names appear in the same order as two consecutive `in <name>` lines in the text of `<Def>`'s declaration in the tree. The chosen file and lines are written to the evidence before the check runs. Swap the two lines. Expect one or more new ERROR identities, the pin list unchanged, and L2 failing.
- *Stale*, with Run 2's override options against a fresh copy: rewrite the first pinned input (by identity order in the reference file) whose right-hand side is not its own name from `in <name> = ...` to `in :>> <name> = ...`. Expect exactly that pin stale, every other pin matched, no new ERROR of any L2 code, and L2 failing.
- *dc3 `808464d` and `60b44d5`*: export and run the new L2 with no pin options. Expect 0 findings and 0 unverifiable. Compare `implicit_matching` with 302 and 391.

**Slow test.** `tests/test_validation/test_positional_binding_trees.py` (`-m slow`) runs the fusion-tea and dc3 comparisons. It reads checkout paths from `POSITIONAL_BINDING_FUSION_TEA_REPO` and `POSITIONAL_BINDING_DC3_REPO`, exports the pinned revisions itself, uses the override options, and skips with a reason naming the missing variable.

**Codegen conformance evidence.** Run sysml-codegen's `tests/conformance/test_self_binding_guidance_contract.py` read-only from its checkout, with this branch checked out here. Record codegen's resolved `agentic_mbse.__file__`, this checkout's HEAD and install mode, and the test output.

## Appendix C: Register and guidance edits

- **`docs/patterns/semantic-hazards.md`**, anchor `positional-input-binding`. Covers:
  - the expected reading;
  - actual semantics, split into KerML text (8.3.3.3.4, `checkFeatureParameterRedefinition`) and SysIDE 0.8.4 observations on named fixtures (the parameterless subdefinition, the mixed spelling evaluating to no value, the `out`-before-`in` rejection, subject-slot positions);
  - cross-route divergence, claimed for calc usages only;
  - the check, its limits (including B6's placeholder limit) and its codes;
  - the pin policy: pins are only for mismatches that existed at `recorded_against`, and a pin certifies nothing about values or routes;
  - fixture paths and upstream links (sysml-codegen POSITIONAL-FORMAL-REDEFINITION, `PROVENANCE.md`; the draft finding, marked unfiled);
  - a "Candidates, not yet reproduced" list with output override and `[*]`/`[0]`.
- **`docs/patterns/plant-idiom.md`**: qualify `:298` ("Order does not matter" here means a redefine placed after a binding; input order on a calc usage does matter); in D-5 (`:74-79`), say the definition's parameter is renamed; add a short paragraph on positional binding with the by-name and definition-order forms, linking the register. No `@pinned` block changes.
- **`skills/sysml-conventions/SKILL.md`** (`:129`, `:218-226`) and **`project_templates/MODELING_GUIDE.md.template`** (`:145-152`): the same clarification of "rename", one line on order versus `:>>`, and a link to the register. Each keeps `plant-idiom.md` and the phrase "Binding a modelled value into a calculation".
- **`agents/sysml-expert.md`** (`:117-139`): one sentence on binding constraint formals by name or in definition order, and on declaring `subject` first, with a link.
- Every new example binds a distinct, unqualified path (`in :>> a = big;`) and carries the `@positional-example` marker. All edits obey I8.

---

**Next Step:** `/_my_design_review` on revision 1 (fresh session), then `/_my_plan`.
