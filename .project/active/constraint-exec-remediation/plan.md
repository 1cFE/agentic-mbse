# CONSTRAINT-EXEC PR Remediation Plan

**Created**: 2026-07-14
**Branch**: `constraint-exec-epic`
**Input**: `.project/research/20260714-064234_constraint-exec-pr-code-quality-audit.md` (audit),
plus a four-agent independent verification pass (all nine findings reproduced) and the
auditor's revised severity position after pushback.

## Agreed severity (after reviewer/author reconciliation)

| Finding | Severity | Disposition |
|---|---|---|
| F1 arithmetic bypasses unit gate | **High — merge blocker** | Fix (Phase 1) |
| F3 asserts instead of BLOCK; fragile list-length flow; 2 mypy errors | Important pre-merge | Fix (Phase 1, same seam) |
| F4 Level 4 populations don't reconcile | Important pre-merge | Fix (Phase 2) |
| F2 parsers accept/rewrite foreign schema versions | Medium latent | Fix (Phase 3) |
| F8 private codec imports, duplicated leaf decode | Low | Subsumed by Phase 3 |
| F9 sort-key collision across files | Low | Fix (Phase 4) |
| F5 public extractor drops structured diagnostics | Low | Fix (Phase 4, backward-compatible) |
| F6 stale spike with broken repro instructions | Low | Archive, don't repair (Phase 5) |
| F7 three parallel export inventories | Low | Derive + test (Phase 5) |
| L4/L6 duplicate extraction | Deferred | Recorded debt; design accepted pending profiling. No action. |

## Decisions

**D-R1 [AGENT] Unit policy for multiplicative arithmetic.** The gate admits only what it can
structurally prove without a dimensional algebra:

- `+` / `-` (binary): operands must pass `unit_compatibility` (identical exact units, or both
  dimensionless-numeric). Result: the shared unit, or the merged numeric category
  (integer∘integer → integer; any real → real).
- `-` / `+` (unary, arity 1): result is the operand's own fact (negation preserves units).
- `*`: dimensionless×dimensionless → merged numeric; dimensionless×quantity (either order) →
  that quantity's fact. quantity×quantity → `block_derived_unit_unsupported` (m·m is not
  representable without a dimensional algebra).
- `/`: quantity/dimensionless → the quantity's fact; dimensionless/dimensionless → real;
  quantity/quantity with the identical exact unit → real (a pure ratio needs no conversion);
  any other quantity pairing → `block_unit_conversion_required` (same dimension, different
  unit) or `block_derived_unit_unsupported` (different dimensions, or dimensionless/quantity —
  inverse units are not representable).
- `**` / `^`: both operands dimensionless → real; any quantity operand →
  `block_derived_unit_unsupported`.
- Non-numeric categories (boolean/string/enum) in any arithmetic →
  `block_unsupported_operand_category`.

Why: blocking scalar scaling (`2 * mass`) would block ubiquitous legitimate constraints and push
authors to fold constants into literals, hurting traceability. Everything admitted above is
provable from operand facts alone; everything else blocks with a reason that names the actual
gap. Rejected alternative: the strict literal reading (block all non-dimensionless
multiplication) — conservative but unusable in practice.

**D-R2 [AGENT] Derived interior facts are authoritative.** The gate computes arithmetic-node
facts from operand (leaf) facts and does not consult the declared `operand_type` on interior
arithmetic nodes. Leaf facts (feature refs, literals, unit annotations) remain the extraction
ground truth. Why: live extraction only stamps an arithmetic node's unit when all children
already agree, so declared interior facts are the least reliable facts in the tree, and
trusting them is exactly the F1 hole. Rejected alternative: block on declared-vs-derived
mismatch — adds a reason code and noise for no safety gain, since the derived fact already
decides.

**D-R3 [AGENT] Malformed snapshot facts become a named BLOCK, not a crash.** The parser stays
shape-only; the profile owns semantic totality (answers the audit's open question). A value
node with a missing `operand_type`, or a `quantity` fact with `unit=None`, yields
`block_malformed_operand_fact` for that usage. No `assert` may guard wire-reachable state.

**D-R4 [AGENT] `PROFILE_SEMANTIC_VERSION` bumps to `executable-profile/v2`.** Decisions change
(mixed-unit arithmetic now blocks; malformed facts block instead of crashing; multiplicative
admits are new), and D8 requires the bump. Wire schema versions do not change — no fact shape
changed.

**D-R5 [AGENT] F9 sort key appends tie-breakers instead of re-sorting by file.** New key:
`(line, qualified_name or "", file or "", column)`. The reviewer's `(file, line, ...)` ordering
would reshuffle every multi-file document and churn canonical bytes downstream; appending
tie-breakers only changes orderings that were previously nondeterministic.

**D-R6 [AGENT] F5 fix is backward-compatible.** `extract_expression_ir` gains a keyword-only
`diagnostics: list[ExtractionDiagnosticFact] | None = None` sink instead of a changed return
type — sysml-codegen imports this function in production
(`expression_compiler.py`, `computed_attribute_extractor.py`) and must not break in an
uncoordinated PR.

## Phases

### Phase 1 — F1 + F3: value-operation gating and totality (merge blocker)

- [x] Regression tests first (all must fail on current HEAD where marked ✗):
  - [x] ✗ mixed-unit `+` under `<=` via snapshot-valid IR → BLOCK `block_unit_conversion_required`
  - [x] ✗ `quantity` operand fact with `unit=None` under `<=` → BLOCK `block_malformed_operand_fact` (no AssertionError)
  - [x] ✗ arithmetic node with `operand_type=None` operand leaf → BLOCK, not crash
  - [x] ✗ quantity×quantity `*` → BLOCK `block_derived_unit_unsupported`
  - [x] scalar×quantity `*` → gate passes (outer comparison decides)
  - [x] quantity/quantity identical unit `/` → dimensionless result feeds outer gate
  - [x] unary minus; 0-operand and 3-operand arithmetic arity → named BLOCK
  - [x] boolean/string/enum operand in arithmetic → `block_unsupported_operand_category`
- [x] Rework the walk: value positions return a typed result
  (`OperandTypeFact | list[EligibilityDiagnostic]`) instead of the append-then-measure
  pattern; comparisons and arithmetic share one operand-recovery path; implement D-R1/D-R2/D-R3.
- [x] New reason codes `block_derived_unit_unsupported`, `block_malformed_operand_fact` added to
  `REASON_CODES`; remove the two asserts in `unit_compatibility`/`_walk_comparison`.
- [x] Bump `PROFILE_SEMANTIC_VERSION` to `executable-profile/v2` (D-R4); update its docstring.
- [x] `uv run mypy` clean over the four pure modules (`executable_profile`, `expression_facts`,
  `expression_ir`, `constraint_facts`) — the two `union-attr` errors gone, no new ones.
- [x] Existing profile/matrix/fact-shape suites green; inspect any golden decision shifts
  one-by-one (expected shifts only where D-R1 newly admits or newly blocks).
- [x] Live-path check: mixed-unit `+` now blocks with `block_unit_conversion_required`
  (correct reason), not `block_unsupported_operand_category` (the old coincidental block).

#### Phase 1 implementation notes (2026-07-14)

**What changed** (`src/agentic_mbse/sysml/executable_profile.py`):

- The old `_walk(node, expect, ...)` split into `_walk_proposition` (keeps the append style)
  and a typed `_walk_value(node, identity, location) -> OperandTypeFact |
  list[EligibilityDiagnostic]`. Value leaves return their declared fact, or
  `block_malformed_operand_fact` when it's missing (D-R3). A unit annotation walks its inner
  value for construct violations but its own declared fact wins (it carries the exact unit).
- Arithmetic goes through `_walk_arithmetic` (arity gate: 2 for all operators, 1 for `+`/`-`
  sign; all operand violations collected, not first-only) and `_derive_arithmetic_fact`
  (the D-R1 rules; guard order mirrors `unit_compatibility`). Declared interior facts are
  never consulted (D-R2). `_quantity_ratio_fact` handles the `/` quantity-pairing ladder.
- `_walk_comparison` consumes `_walk_value` for both sides; both asserts deleted.
  `unit_compatibility`'s quantity-with-no-`UnitFact` case returns
  `block_malformed_operand_fact` instead of asserting.
- `REASON_CODES` += `block_derived_unit_unsupported`, `block_malformed_operand_fact`;
  `PROFILE_SEMANTIC_VERSION` → `executable-profile/v2`.

**Tests**: new `tests/test_sysml/test_executable_profile_arithmetic.py` (34 cases). Red→green
verified on HEAD before implementing: 31 failed / 3 passed, with the four ✗ cases showing the
exact predicted modes — mixed-unit `+` and quantity×quantity ADMIT-with-no-diagnostics;
`quantity` `unit=None` → `AssertionError` at `unit_compatibility`; declared-`None` arithmetic
fact → `AssertionError` at the `_walk_comparison` assert. All green after.

**Golden decision shifts**: none in any pinned suite (matrix golden, production-facts pins,
fact-shapes) — all pre-existing tests pass unchanged. The one arithmetic fixture usage
(`unit_bearing_arithmetic`, same-unit `+` under `==`) still blocks
`block_real_equality_requires_tolerance`, now via the derived fact. Behavioral shifts outside
the pinned suites, each intended by D-R1/D-R2/D-R3:

- mixed-unit `+`: was ADMIT (F1 hole) → BLOCK `block_unit_conversion_required`.
- quantity×quantity `*` with a declared interior fact: was ADMIT → BLOCK
  `block_derived_unit_unsupported`.
- scalar×quantity `*`, quantity/dimensionless `/`, same-unit quantity ratio `/`,
  dimensionless `**`, unary sign: were crash-or-declared-fact-dependent → now derived admits.
- malformed facts (quantity without `UnitFact`; value leaf without `operand_type`): were
  `AssertionError` → BLOCK `block_malformed_operand_fact`.

**Live-path check**: `live_probe.sysml` (`assert constraint { 1 [m] + 1 [cm] <= 3 [m] }`)
loaded via syside → `extract_constraint_facts` → `evaluate_profile`:
`mixed_unit_ordering` BLOCK `[('block_unit_conversion_required', 'arithmetic')]`;
`same_unit_ordering` ADMIT. Recorded here rather than as a test — the live suites load
committed fixture files, and adding fixture files was out of Phase 1's file scope.

**Verification**: `pytest tests/test_sysml/` 317 passed / 1 skipped; fast suite
`pytest tests/` 1435 passed / 1 skipped; `mypy --no-incremental` over the four pure modules:
"Success: no issues found in 4 source files"; ruff check + `format --check` clean on all
touched files.

**Deviations**: `executable_profile.py`, `test_executable_profile.py`, and
`test_executable_profile_matrix.py` failed `ruff format --check` already on HEAD; the
format gate required formatting them (≈100 lines of pure line-wrap churn, no semantic
change). Pre-existing, untouched `tests/test_sysml/test_adr002.py` fails `ruff check`
(I001 import sort) on HEAD — left alone, out of Phase 1 scope.

### Phase 2 — F4: Level 4 population reconciliation

- [x] Keep legacy `Total constraints` (Item 4 exclusion semantics, pinned by
  `tests/test_validation/test_item4_subtype.py`) untouched.
- [x] Give the eligibility block its own named denominator, e.g.
  `Constraint usages assessed (incl. satisfy): 13` with eligible/ineligible/unassessed summing
  to it, all derived from the one `ProfileResult`.
- [x] Test: category counts reconcile with the displayed assessed total on the two-file fixture
  dir (the 27-vs-28 case) and the single file (12-vs-13 case).
- [x] Deliberately update any L4 report tests that pin the old eligibility lines.

#### Phase 2 implementation notes (2026-07-14)

**What changed** (`src/agentic_mbse/validation/level4_constraints.py`):

- `eligibility_coverage_metrics` now emits
  `"Constraint usages assessed (incl. satisfy)": len(result.decisions)` as the first
  eligibility line, from the same `ProfileResult` the category counts come from, so
  Eligible + Ineligible + Unassessed always sums to the displayed denominator. Docstring
  explains why this denominator differs from the legacy `Total constraints` (extraction
  classifies every ConstraintUsage including SatisfyRequirementUsage; the legacy count
  excludes the requirement subtree per Item 4 / `EXCLUDED_CONSTRAINT_TYPES`).
- Legacy `Total constraints` / `ConstraintUsage` / `ConstraintDefinition` lines untouched;
  `test_item4_subtype.py` passes unchanged.

**Report on `tests/fixtures/constraint_fact_shapes/`** (was 27 vs 12+12+4=28 unexplained):
`Total constraints: 27` · `Constraint usages assessed (incl. satisfy): 28` ·
`Eligible: 12` · `Ineligible: 12` · `Unassessed: 4` — categories reconcile to 28.
Single file `source_forms.sysml`: total 12, assessed 13 (8+1+4).

**Tests**: new `tests/test_validation/test_level4_reconciliation.py` — reconciliation
(sum == displayed denominator) on the single file (12-vs-13) and the fixture dir
(27-vs-28); pins both denominators (stable extraction counts) but not the
eligible/ineligible split. No existing test pinned the old eligibility lines beyond
key-presence (`test_sysml_quality_checks.py:652,1078`), so none needed updating.

**Deviations**: `level4_constraints.py` failed `ruff format --check` already on HEAD
(one pre-existing line-wrap in `main()`); formatted per the Phase 1 precedent, no
semantic change.

### Phase 3 — F2 (+F8): codec hardening

- [x] `constraint_facts.parse()` rejects unsupported envelope versions with a clear error
  naming found vs supported.
- [x] One public dict-level ExpressionIR decoder that validates each node's `schema_version`
  and `kind` (unknown kind → clean error, not KeyError); foreign version is rejected, never
  silently rewritten to v1.
- [x] `kind` and `schema_version` become non-init (`field(init=False)`) on IR node dataclasses
  and `ConstraintFacts`; update the explicit `schema_version=` call sites
  (`constraint_extraction.py`, serializer tests).
- [x] F8 fold-in: `constraint_facts` consumes only public codec surface (public dict decoder +
  public canonical-JSON helper); shared `IdentityFact` leaf decode lives in one place.
- [x] Tests: wrong-version (envelope and nested node), missing-version, wrong-kind,
  future-extra-field; byte-stability round-trip suites stay green.

#### Phase 3 implementation notes (2026-07-14)

**New public codec surface** (`src/agentic_mbse/sysml/expression_ir.py`, all in `__all__`):

- `expression_ir_from_dict(data) -> ExpressionIR` — the one dict-level decoder. Validates
  every node (recursively): missing `schema_version` → `ValueError`; foreign version →
  `ValueError` naming found vs supported (never rewritten to v1); missing or unknown `kind`
  → `ValueError` (no more `KeyError`). `parse_expression` now delegates to it.
- `canonical_json(obj)` — `_canonical_json` renamed public (D2/D5 semantics unchanged).
- `identity_fact_from_dict(data)` — the single `IdentityFact` leaf decode (F8); nullable.

`ValueError` chosen as the error type — it's what the codec already raised for unknown kind
and null operand_type; no new exception class.

**Fail-closed by construction**: `kind` and `schema_version` are `field(init=False, ...)` on
all six IR node dataclasses and `ConstraintFacts` — impossible documents can't be built
(`TypeError` at the constructor). The decoder validates the incoming tags, then constructs
normally; the init=False defaults are correct for the single supported version.
`constraint_facts.parse()` gates the envelope the same way (missing or foreign
`schema_version` → `ValueError` naming found vs supported).

**F8**: `constraint_facts` now imports only public names (`ExpressionIR`, `canonical_json`,
`expression_ir_from_dict`, `identity_fact_from_dict`); its duplicated identity decode
collapsed onto `identity_fact_from_dict` (the required variant is a thin null-check wrapper).
Layering stays one-way (`constraint_facts` → `expression_ir`).

**Call-site updates** (mechanical, `schema_version=` arg removed): `constraint_extraction.py`
`ConstraintFacts(...)` (+ dropped now-unused `CONSTRAINT_FACTS_SCHEMA_VERSION` import);
tests `test_constraint_facts_serialize.py`, `test_executable_profile.py`,
`test_executable_profile_arithmetic.py`. No explicit `kind=` call sites existed.

**Tests added**: 7 in `test_expression_ir_serialize.py` (foreign/missing node version,
foreign version on a nested operand, unknown/missing kind, future-extra-field, non-init
tags → `TypeError`) and 4 in `test_constraint_facts_serialize.py` (foreign/missing envelope
version, foreign nested node version inside a facts doc, non-init envelope version).
Extra-key stance: the decoder reads only known slots, so unknown keys are **ignored** —
pinned as existing behavior in `test_future_extra_field_is_ignored`. All pre-existing
byte-stability/round-trip assertions unmodified.

**Probes re-run**: v999 ExpressionIR doc → `ValueError` naming found vs supported; v999
facts envelope → `ValueError`; `kind=` at a constructor → `TypeError`;
`serialize(parse(production_facts.json))` byte-identical to the fixture.

**Verification**: `pytest tests/test_sysml/` 328 passed / 1 skipped; fast suite
`pytest tests/` 1448 passed / 1 skipped; `mypy --no-incremental` over the four pure modules
clean; ruff check + `format --check` clean on all touched files.

**Deviations**: `test_expression_ir_serialize.py` was not `ruff format`-clean on HEAD; the
format gate rewrapped two pre-existing long constructor lines (same pattern as Phase 1's
format-churn deviation, no semantic change).

### Phase 4 — F9 + F5: extraction ordering and diagnostics (same file, one pass)

- [x] Sort key → `(line, qualified_name or "", file or "", column)` (D-R5); two-file
  anonymous-assertion byte-stability test (serialize both load orders, assert identical bytes).
- [x] `extract_expression_ir(..., diagnostics=None)` sink (D-R6); the non-finite-literal test
  moves to the public API (no private `_ExtractionContext` imports); docstring updated.
- [x] Regenerate `tests/fixtures/constraint_fact_shapes/production_facts.json` only if bytes
  change, via the documented convention; record in the commit message if so — **bytes did not
  change**, no regeneration needed (see notes).

#### Phase 4 implementation notes (2026-07-14)

**F9 sort key** (`src/agentic_mbse/sysml/constraint_extraction.py`, `_constraint_sort_key`):
key extended to `(line, qualified_name or "", file or "", column)` per D-R5 — tie-breakers
appended, never a file-first re-sort. `file` comes from the same
`SysideAdapter.get_source_location` tuple the key already read; `column` reads
`cst_node.start_point.character + 1`, matching `_location_fact`. Missing location → line 0 /
file `""`; missing `cst_node` → column 0, keeping the key total.

**Red→green**: new `tests/test_sysml/test_constraint_extraction_ordering.py` writes two
tmp_path files, each with an anonymous `assert constraint` on line 3, loads them in both
orders, and byte-compares the serialized facts. On the pre-fix tree it failed exactly as F9
predicts (the two anonymous usages serialized in load order — the diff showed the ProbeA/ProbeB
usage blocks swapped); green after the key change.

**production_facts.json unchanged**: `test_production_golden_self_compares` passes with the
new key, so the fixture was not regenerated. Expected — the only anonymous constraints in the
fixture pair are in `source_forms.sysml` (lines 40, 46); `type_units.sysml` has none, and no
named constraint shares a `(line, qualified_name)` pair across the two files, so no old-key
tie existed for the appended tie-breakers to re-order.

**F5 diagnostics sink** (`extract_expression_ir`): keyword-only
`diagnostics: list[ExtractionDiagnosticFact] | None = None`; when a list is passed, the
call's extraction diagnostics are appended to it (`extend`); return type unchanged (D-R6,
sysml-codegen call-compatible). Docstring now documents the sink instead of the drop.
`test_non_finite_literal_yields_extraction_diagnostic` rewritten onto the public API with the
sink — no `_expression_ir`/`_ExtractionContext` imports remain in the test file (the mock
literal stays: SysML has no non-finite literal syntax, so the path is unreachable via
`try_load_model`). The public clean-expression test
(`test_extract_expression_ir_public_single_node_entry`) kept as-is.

**Verification**: final runs `pytest tests/test_sysml/` 334 passed / 1 skipped;
`pytest tests/` 1454 passed / 1 skipped — fully green. (Mid-phase runs showed one failure in
`test_public_api_exports.py::test_every_exported_name_resolves` — Phase 5's in-flight work,
outside Phase 4's file scope; it tripped on the runtime-`None` TYPE_CHECKING aliases at
`syside_adapter.py:95-105`, independent of any Phase 4 change, and the Phase 5 work resolved
it before Phase 4 closed.) `mypy --no-incremental` over `constraint_extraction.py` + the four
pure modules: "Success: no issues found in 5 source files" (no pre-existing syside noise to
ignore). ruff check + `format --check` clean on the three touched files.

**Deviations**: `ruff format` collapsed one pre-existing multi-line `next(...)` in the
untouched clean-expression test (same pre-existing format-churn pattern as Phases 1–3; no
semantic change). Nothing else.

### Phase 5 — F6 + F7: hygiene

- [x] Archive `.project/active/spike-constraint-fact-shapes/` →
  `.project/completed/20260711_spike-constraint-fact-shapes/` with a close-out note in
  `findings.md`: D7 retired the capture module; `generate_golden.py` is a historical artifact;
  `golden.json` is the frozen S1 oracle; `production_facts.json` is the regeneratable golden.
  Fix the `CURRENT_WORK.md` pointer. Do not repair or delete the dead generator.
- [x] `sysml/__init__.py`: `__all__ = sorted(_LAZY)`; add an export-consistency test (every
  `__all__` name getattr-resolves; `set(__all__) == set(_LAZY)`).
- [x] Do NOT rename `parse`/`serialize` — coordinated cross-repo change, recorded as deferred
  (see Cross-repo coordination notes; no rename made).

#### Phase 5 implementation notes (2026-07-14)

**F6 archive** (git rename, R status preserved): spike moved to
`.project/completed/20260711_spike-constraint-fact-shapes/`. Close-out note added at the top
of its `findings.md` (dated 2026-07-14): the S1 capture module was retired by D7, so
`generate_golden.py` and the repro instructions are historical and do not run; `golden.json`
is the frozen S1 semantic oracle (never regenerated); `production_facts.json` is the
regenerable byte-stability golden. Generator and duplicate `probe_*.sysml` files kept
untouched as the frozen record.

**Pointer updates** (live documents only): `.project/CURRENT_WORK.md:34`, plus two live
source docstrings that cited the old path (`constraint_facts.py:4`, `expression_facts.py:3`).
Left as-is: references inside `.project/completed/`, `.project/research/`, and
`.project/reference/` (the latter are marked "REFERENCE COPY... Do not edit here"), and the
spike's own findings.md body (covered by the close-out note).

**F7 collapse** (`sysml/__init__.py`, 372 → 276 lines): the 105-line hand-written `__all__`
deleted; `__all__: list[str] = sorted(_LAZY)` derived after the registry. Set-compared old
vs new before the change: identical (95 names, no dupes), so the public API is unchanged.
Ruff consequence: with `__all__` dynamic, every TYPE_CHECKING import trips F401, so the file
suppresses F401 file-wide with a comment; the compensating guard is the new AST test below.

**New test** `tests/test_sysml/test_public_api_exports.py` (6 tests): `__all__` is a sorted
list of str; `set(__all__) == set(_LAZY)`; every name getattr-resolves non-None;
`from agentic_mbse.sysml import *` yields exactly `__all__`; TYPE_CHECKING imports (by AST)
name exactly `set(_LAZY)` — the F401 backstop.

**Deviation — `syside_adapter.py` runtime-`None` aliases**: gate 2 (every export resolves
non-None) failed on HEAD too: `Model`/`Diagnostics`/`Element` were exported but bound to
`None` at runtime (type-only aliases, `syside_adapter.py:95-105`). No runtime consumer
existed (internal code uses `_get_*_type()`). Fixed by a module-level PEP 562 `__getattr__`
in `syside_adapter` that resolves the three names from `get_syside()` on first access —
import stays syside-free for these names; accessing them without syside now raises the
adapter's ImportError instead of silently yielding `None`.

**Verification**: `test_public_api_exports.py` + `test_executable_profile_hygiene.py` +
`test_adapter.py` — 26 passed; gate 2 one-liner passes (95 exports, all non-None);
ruff check + `format --check` clean on the five touched Python files; the 4 mypy
`no-any-return` errors in `syside_adapter.py` pre-exist identically on HEAD (line shifts
only; not in the four-pure-module gate). Format churn: `syside_adapter.py` was not
format-clean on HEAD (same pattern as Phases 1–4); formatted, pure line-wrap churn.

### Phase 6 — Close-out verification

- [x] Full suite: `uv run pytest tests/ -m ""` — **1496 passed, 1 skipped** (was 1401/1 at
  epic close; +95 from the remediation's regression tests).
- [x] `uv run ruff check` + `format --check` over touched files.
- [x] Targeted mypy over the four pure modules + `constraint_extraction.py`: clean.
- [x] Re-run the audit's five mutation probes; all now produce named BLOCKs/errors.
- [x] Update `.project/CURRENT_WORK.md`; append remediation summary to the PR body staging file.

#### Phase 6 implementation notes (2026-07-14)

**Residual hole found and closed — connective arity.** The audit's "Validation Performed"
list included a probe no numbered finding carried: a zero-operand `and` walked as a
proposition was ADMITTED (vacuous loop emits nothing, default-deny had nothing to prove).
Re-running it against the remediated tree confirmed the hole survived Phases 1–5 (a
two-operand `not` admitted the same way). Fixed in `_walk_proposition`'s connective branch:
`not` requires exactly 1 operand, `and`/`or` at least 2; wrong arity →
`block_unsupported_node` with the count in the message (same style as the arithmetic and
comparison arity gates). 9 regression tests appended to
`test_executable_profile_arithmetic.py` (6 blocking arities red on the pre-fix tree, 3
admitted arities pinned). Covered by the already-bumped `executable-profile/v2`.

**Audit probes re-run** (`scratchpad probe_audit_final.py`): mixed-unit arithmetic → BLOCK
`block_unit_conversion_required`; ExpressionIR v999 → `ValueError` naming found vs supported;
facts envelope v999 → `ValueError`; zero-operand `and` → BLOCK `block_unsupported_node`;
L4 categories reconcile against the new assessed denominator (Phase 2 CLI verification,
28 = 12 + 12 + 4 beside legacy total 27).

### Phase 7 — Fresh audit cures: snapshot totality, invariant tags, module export

- [x] D-R3 end-to-end regressions through `ConstraintFacts` serialize/parse → profile for
  literal, feature-reference, and unit-annotation leaves with both `operand_type: null` and an
  absent `operand_type`; all return `block_malformed_operand_fact`.
- [x] Serializer-side tag invariants reject post-construction `kind` / `schema_version` mutation
  for all six ExpressionIR node families, the facts envelope, and nested IR inside facts.
- [x] Add `extract_expression_ir` to `constraint_extraction.__all__` and pin the defining-module
  star-import surface.
- [x] Normal suite, targeted mypy, Ruff check, and Ruff format check green.

#### Phase 7 implementation notes (2026-07-17)

**D-R3 snapshot path** (`expression_ir.py`): literal, feature-reference, and unit-annotation
`operand_type` fields now truthfully allow `None`. Their decoder branches use the optional leaf
decoder and treat either JSON `null` or an absent field as the same malformed semantic fact. Wire
tags remain required and version-checked. Two full-facts regressions serialize a malformed leaf,
parse it with the public facts codec, and evaluate the profile; both shapes reach D-R3's named
`block_malformed_operand_fact` instead of raising `ValueError` / `KeyError`.

**Mutation invariant** (`expression_ir.py`, `constraint_facts.py`): serialization recursively
checks every ExpressionIR instance against its class's fixed `kind` and the supported schema
version before converting the dataclass aggregate to canonical JSON. The facts serializer also
checks its envelope version. Valid documents retain the same `dataclasses.asdict` + canonical JSON
encoding; malformed semantic leaf facts remain serializable so the profile owns semantic totality.
Freezing was not used because the shared structures intentionally contain mutable lists.

**Defining-module export** (`constraint_extraction.py`): `__all__` now names both public extractors.
The focused test asserts the exact inventory and verifies star import resolution.

**Tests added**: 12 parameterized IR mutation cases (six node families × two tags), facts-envelope
and nested-IR mutation cases, six public-codec/profile malformed-leaf cases (three leaf families ×
two wire shapes), and one module-export case. Initial red run: 17 failures matching the fresh audit
findings; the expanded green focused run covers 92 tests.

**Verification**: normal suite `1484 passed, 1 skipped, 33 deselected`; targeted mypy over the five
core extraction/facts/IR/profile modules: clean; Ruff check and format check over the seven touched
Python files: clean. The paid/slow all-markers corpus was not rerun, per the project gate and handoff.

**Deviations**: none. The implementation follows D-R3's recorded parser/profile boundary and uses
the handoff's recommended serializer-side invariant rather than creating a new immutability contract.

## Cross-repo coordination notes (sysml-codegen)

- `extract_expression_ir` signature stays call-compatible (D-R6).
- Foreign-version documents now *fail* to parse here; sysml-codegen's Item 8 pins versions, so
  no live flow regresses, but its tests that construct facts JSON must use v1 strings.
- If Phase 4 changes `production_facts.json` bytes, note it in the PR body for the paired
  snapshot work.
- Deferred: rename barrel `parse`/`serialize` → `parse_constraint_facts`/`serialize_constraint_facts`
  in a coordinated pair of PRs.
