# Ready-to-apply brief: wire `executable_profile.preflight` into sysml-codegen

**Owner:** agentic-mbse CONSTRAINT-EXEC Item 3 (this item owns this change; the orchestrator
applies and gates it in the sysml-codegen tree — this file does not touch that repo).
**Target repo:** `sysml-codegen` (sibling checkout, path-dependency on this repo — see Pin below).
**Consumes:** `agentic_mbse.sysml.executable_profile.{preflight, evaluate_profile, Eligibility,
PROFILE_SEMANTIC_VERSION}` — landed on `constraint-exec-epic` (this repo), Phases 1–3.

## Facts this brief is grounded in (verified against the current sysml-codegen tree)

- **The seam.** `src/sysml_codegen/analysis/constraint_lowering.py`, function
  `lower_constraints(facts, *, occ_index, registry, design_attrs, calc_usages)`
  (`constraint_lowering.py:336`). The exact line that turns a predicate into what
  `ConcreteConstraint` stores:
  ```python
  # constraint_lowering.py:399-401
  predicate_ir = (
      serialize_expression(usage.predicate) if usage.predicate is not None else None
  )
  ```
  `ConcreteConstraint.predicate_ir: str | None` (`resolution/models.py:318`) — the object is
  serialized and discarded immediately; nothing downstream holds the live `ExpressionIR`.
- **Not yet wired into the production pipeline.** `lower_constraints` is currently called only
  from tests (`tests/conformance/test_constraint_lowering.py`). `orchestration/pipeline_builder.py`
  does not call it. Threading it in is separately tracked, unchecked, in
  `.project/active/constraint-lowering/plan.md:197-233` (sysml-codegen's own plan) — that plan
  text already anticipates "filter to the executable-profile assert usages" as a step. **This
  brief's edit belongs inside `lower_constraints` itself**, so it's correct on day one of that
  threading landing, not contingent on it.
- **Facts source today.** The one caller (`_load()` in the conformance test,
  `test_constraint_lowering.py:32-36`) calls `extract_constraint_facts(model)` once and passes
  the resulting `facts` straight into `lower_constraints`. No snapshot/re-parse boundary exists
  between extraction and this seam.
- **No existing import of `executable_profile`.** `constraint_lowering.py:17` already imports
  `serialize_expression` from `expression_ir`; `constraint_facts`/`expression_facts` types are
  imported under `TYPE_CHECKING` only (`:31-32`). `executable_profile` is imported nowhere in
  sysml-codegen yet.
- **Halt mechanism.** `CodeGenerationError` (`orchestration/pipeline_context.py:48-57`) is the
  repo's uniform "raise, name the offending element, halt" exception — already used throughout
  `constraint_lowering.py` for other invariant violations (e.g. `assert_unique_constraint_ids`,
  `guard_polarity`). Use it, not a new exception type. A separate log-only mechanism
  (`report_dropped_constraints()`, `pipeline_builder.py:744`) exists for *excluded* usages — do
  **not** route a preflight block through that; a blocked would-execute assert must halt, not log.
- **Version pin today.** `pyproject.toml:22`: `"agentic-mbse>=0.1.0"` (loose floor), overridden in
  dev via `[tool.uv.sources]` (`:47-48`) as an editable path dependency on this sibling checkout.
  There is currently no runtime check of any agentic-mbse version/semantic marker anywhere in
  sysml-codegen.

## The change

**File:** `src/sysml_codegen/analysis/constraint_lowering.py`

1. **Import.**
   ```python
   from agentic_mbse.sysml.executable_profile import (
       Eligibility,
       PROFILE_SEMANTIC_VERSION,
       evaluate_profile,
   )
   ```
   (`evaluate_profile`, not `preflight`, so the per-usage `UsageDecision`s — including each
   `effective_predicate` — are available for the lowering loop below; `preflight` is a thin
   partition over the same decisions and would require re-deriving that per-usage mapping anyway.)

2. **At the top of `lower_constraints`, before its existing per-usage loop:**
   ```python
   assert PROFILE_SEMANTIC_VERSION == "executable-profile/v1", (
       f"agentic-mbse executable-profile semantics changed ({PROFILE_SEMANTIC_VERSION}); "
       "review before re-pinning"
   )
   profile = evaluate_profile(facts)
   blocking = [d for d in profile.decisions if d.eligibility is Eligibility.BLOCK]
   if blocking:

       def _describe(d, diag):
           name = d.identity.qualified_name or d.identity.name or "<anonymous>"
           where = f"{d.location.file}:{d.location.line}" if d.location else "<no location>"
           return f"  - {name} at {where}: {diag.construct} ({diag.reason})"

       lines = [_describe(d, diag) for d in blocking for diag in d.diagnostics]
       raise CodeGenerationError(
           "Constraint generation halted — the following asserted constraints are not "
           "executable:\n" + "\n".join(lines)
       )
   ```
   One line per diagnostic, naming identity + location + construct + reason. **Halting must emit
   nothing partial** — this check runs and raises before any `ConcreteConstraint` is built, not
   per-usage inline, so a single blocked assert stops the whole batch.

3. **In the existing per-usage loop, replace the iteration source and the operand at line 399.**
   Today the loop iterates `facts.usages` directly (verify the exact current loop head — this
   brief was written against `:399-401`'s immediate context, not the full function body). Change
   it to zip against `profile.decisions` (order-aligned 1:1 with `facts.usages` — a guarantee of
   `evaluate_profile`, not incidental):
   ```python
   for usage, decision in zip(facts.usages, profile.decisions, strict=True):
       ...
       predicate_ir = (
           serialize_expression(decision.effective_predicate)
           if decision.effective_predicate is not None
           else None
       )
       assert decision.effective_predicate is usage.predicate or decision.eligibility is not Eligibility.ADMIT, (
           "same-IR violation (I5/D7): the profile walked a different object than the one "
           "about to compile"
       )
   ```
   This is the **in-process, single-parse arm** of the same-IR guarantee (D7): today `facts` is
   built once and never re-parsed before this point, so `decision.effective_predicate is
   usage.predicate` holds by construction for every admitted usage — the assert makes that
   invariant checkable, not just assumed. **This is not yet the arm that matters for Item 7's
   future Kleene compiler**: once that compiler reads `ConcreteConstraint.predicate_ir` (a
   *string*, not a live object — see Facts above), object identity is no longer available at that
   later seam, and the check there must become
   `serialize_expression(compiled_ir) == predicate_ir` (the serialization-equality arm). That is
   out of scope for this brief (Item 7 doesn't exist yet); flag it in that item's design instead
   of building it here.
   - Non-`ADMIT` usages (`UNASSESSED`, and `BLOCK` — though blocking already halted the whole
     batch above, so none reach here) should **not** produce a `ConcreteConstraint` with a
     predicate at all if they didn't before; verify against the current loop body whether
     unassessed usages already skip this branch (e.g. via a `usage.predicate is None` check) or
     whether this needs an explicit `if decision.eligibility is not Eligibility.ADMIT: continue`
     added. Do not change existing non-assert handling beyond what's needed to source the
     predicate from `decision.effective_predicate` instead of `usage.predicate`.

## Tests to add

**File:** `tests/conformance/test_constraint_lowering.py` (extend the existing suite — matches its
established style: `_load()` for live-license fixture tests, hand-built `ConstraintFacts` for
synthetic cases).

- **Preflight halts on a blocked would-execute assert.** A synthetic `ConstraintFacts` (or a new
  fixture under `tests/fixtures/`, following `constraint_blocked_owner`/`constraint_inline`'s
  layout) whose one assert predicate carries a blocked construct (reuse agentic-mbse's shape: a
  feature chain in the predicate body, or a real-equality `==`). Assert `lower_constraints(...)`
  raises `CodeGenerationError`, and the message names the construct + reason. Assert **nothing**
  was generated (no partial `ConcreteConstraint` list) — if `lower_constraints` returns a list,
  the exception must fire before any element is appended, not after a partial batch.
- **Admitted assert still compiles.** A clean `<=`/`==`-on-matching-scalars predicate produces the
  same `ConcreteConstraint.predicate_ir` as before this change (byte-identical
  `serialize_expression` output) — proves the wiring doesn't change behavior for the golden path.
- **Unassessed usage passes through unaffected.** A `satisfy`/plain usage in the same facts batch
  as an admitted assert does not affect the halt decision and is not itself lowered to a predicate.
- **Same-IR assertion holds on the fixture path.** Not a new test per se — the `assert
  decision.effective_predicate is usage.predicate` above already covers this for every existing
  passing test; add one explicit test that would fail if that line were removed (e.g. mock/patch
  `evaluate_profile` to return a decision whose `effective_predicate` is a *copy* rather than the
  same object, and assert the wiring catches it) if the team wants an explicit regression pin
  rather than relying on the inline assert alone.

## Version pin

Keep `pyproject.toml`'s existing `"agentic-mbse>=0.1.0"` (already present, `:22`) — no version
bump needed here; the coordinated-pair discipline is now satisfied by the `PROFILE_SEMANTIC_VERSION`
runtime assertion added above (step 2), which fails loudly if a future agentic-mbse release changes
profile *behavior* (D8) even under a semver-compatible package bump. Do not add a second,
separate version-string pin — that would duplicate what the semantic-version assertion already
checks and could drift out of sync with it.

## De-risk note (carried from design, still open)

Before applying: confirm via a `/_my_spike` in sysml-codegen (or equivalent quick check) that no
change lands between this brief being written and applied that introduces a second parse /
re-serialize of `facts` between extraction and `lower_constraints` — the in-process object-identity
arm above depends on that still being true. If sysml-codegen's own Phase 4 threading work (cited
above) introduces a snapshot/parse boundary before `lower_constraints` is called, switch the
assertion in step 3 to the serialization-equality arm instead.
