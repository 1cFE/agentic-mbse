# Spike: S2 — Expression-Tree Parity and the IR Relationship Decision

## Summary of Findings

**Both assumptions confirmed. The IR relationship decision is: extract-and-migrate, staged.**

1. **Parity holds.** A single neutral tree (provisional `ExpressionIR`, `s2_ir.py`) was
   extracted from live SysIDE for all five scoped predicates (WI-014 `cost <= budget`, IFE
   viability `eta * gain >= threshold` with a defaulted formal, an inline owner-reference
   predicate, a negated assertion, a compound Boolean), in both source forms (typed usage via
   the proven two-step; inline via its own `result_expression`). Compiled Python agreed with
   the live oracle on **all 22 live evaluations** that SysIDE itself could complete
   (5 assertions × 4 points, plus wi014 committed + probe-1); every tree JSON round-tripped
   byte-identically within a load and across independent loads; margin signs held under
   negation (positive ⇔ satisfied, negated inequality flips); and the compiled Kleene
   three-valued semantics matched the documented truth table at every non-finite case,
   including non-finite values in every Boolean position of the compound predicate.

2. **The Kleene divergence is not just by design — it is necessary.** Live SysIDE, given a
   predicate whose operand is `1.0/0.0`, returns a confident `False` with **zero
   diagnostics** (probe 3). Raw SysIDE evaluation therefore cannot be the oracle at
   non-finite points, exactly as the concept states.

3. **Two oracle-envelope boundaries found** (probe 5/7, informative for S3/S4):
   - The known WI-014 self-named-binding trap is live in the committed `plant_values`
     fixture: `viability` carries `in gain = gain`, and the two-step hits SysIDE's
     step-limit ("infinite recursion") — the oracle returns `(None, diagnostic)`. Not a
     tree defect: the committed predicate's IR is structurally identical to the scratch
     replica whose parity passed on all points.
   - No SysIDE scope resolves cross-part, usage-supplied values (mechanisms a/b/c) for a
     def-owned assertion: every alternative scope fails with `Invalid operator '*' for
     types 'element' and 'element'`, and `evaluate_feature` returns the usage element
     itself (consistent with WI-014). **Consequence:** the live oracle is a development
     oracle for owner-literal shapes only; concrete-instance verdicts must come from the
     generated code path — which is the architecture's whole point, and reinforces S4's
     lowering-based (never evaluator-based) actual resolution.

### The relationship decision: extract-and-migrate, staged

`ExpressionIR` becomes a new agentic-mbse-owned tree with the concept's node algebra, and
sysml-codegen's expression-compiler seam **migrates onto it, retiring `ExpressionAST`** —
staged so predicates ship first and the calc cutover runs under the existing byte-identity
gates. Grounds:

- **"Extend" is rejected on structure and ownership.** Today's `ExpressionAST`
  (`src/sysml_codegen/extraction/expression_compiler.py:56`) pre-classifies references as
  input/intermediate at construction (the concept forbids pre-classification), left-folds
  n-ary at build, is never serialized, and lives in the wrong repo (the concept requires
  semantics-library ownership). "Extending" it would rewrite all of that in place — a
  migration wearing an extension's name.
- **"Permanently predicate-focused" is rejected on measured convergence cost: ~zero.**
  Probe 4 rendered the shared IR through a ~40-line compat renderer and reproduced today's
  compiler output **byte-identically for every calc output expression** in wi014_toy,
  plant_values, and a stress model (4-term left-fold, unary minus, `^`→`**`, nested and
  chained arithmetic). One tree demonstrably serves both consumers; keeping two semantic
  trees would create exactly the silent-third-IR risk the concept forbids.
- **Staging aligns with S1, which concluded in parallel the same day** (verdict recorded in
  the concept and in `agentic-mbse/.project/active/spike-constraint-fact-shapes/findings.md`):
  all needed facts are statically recoverable, and S1's equality/unit gates match this
  spike's blocked rows. With S1 and S2 both concluded, the concept's schema-freeze
  precondition is met; the IR field shapes committed at spec time must adopt S1's frozen
  fact shapes (this spike's pydantic fields are probe-grade, its topology and renderers are
  the proven part).
- Display reconstruction (`agentic-mbse/src/agentic_mbse/sysml/expression.py:420`) stays a
  display aid — it was never a candidate for the IR and nothing here touches it.

### Operator/type matrix fixed for executable-profile v1

| Construct | v1 | Evidence |
|---|---|---|
| `<, <=, >, >=` | in | 22/22 live parity; boundary points exact (margin 0.0) |
| `and, or, not` (incl. n-ary and/or) | in | compound + negated parity; Kleene table verified |
| Negated assertion polarity | in | `is_negated` exposed directly on `AssertConstraintUsage`; verdict/margin flip verified |
| Arithmetic `+ - * / ** ^`, unary minus | in (operand position) | byte-identical calc compat; `*` inside predicates live-verified |
| Defaulted formal | in | live two-step resolves the default through usage scope (probe 2, `viability`) |
| `==`, `!=` | blocked here; categories are S1's gate | this spike gathered no equality parity evidence, so its compiler raises; S1 (concluded same day) admits Boolean/string/integer/same-enum equality and blocks real equality, incompatible or unresolved operands, and unproven units |
| `xor`, `implies` | blocked | extractable but zero parity evidence gathered |
| Invocation, feature chains | blocked, cataloged | IR nodes exist; named diagnostic; no live parity attempted |
| Unit annotation | node exists; strip-render only | unit *policy* evidence is S1's matrix, not S2's |
| Non-finite operands | leaf-unknown + Kleene | full table verified; raw SysIDE gives silent confident `False` — excluded as oracle there |

### Facts the design can now rely on (syside 0.8.4)

- Predicate access: `constraint_def.result_expression` / inline `usage.result_expression`
  — the `OperatorExpression` directly, no membership walking.
- Two-step oracle: `syside.Compiler().evaluate(expr, scope=usage)` →
  `(bool | None, CompilationReport)`; `scope` must be a keyword; `evaluate_feature` on the
  usage returns the usage element, not the Boolean.
- No value injection at evaluation time (per syside docs + API): varying points requires
  per-point model text (what probe 2 does) or in-memory model mutation.
- `str(operator)` yields clean symbols (`<=`, `>=`, `>`, `and`); referents carry name +
  full qualified name — everything the feature-ref node needs, with no evaluator calls.
- Chained infix arithmetic arrives as **nested binary** nodes (probe 6): the IR's n-ary
  capacity is latent, not exercised by live extraction of ordinary infix.

## Question / Goal

Two assumptions under test, from the upstream concept
(`.project/concepts/constraint-execution-and-design-space-studies-claude.md`, Appendix B, S2):

1. **Parity:** one neutral, serializable expression tree can be extracted from live SysIDE
   predicates, round-trip JSON byte-stably, and compile to Python whose verdicts match live
   SysIDE on every supported point, with the documented Kleene table governing non-finite
   points (the IEEE divergence is by design).
2. **Relationship:** decide on evidence how `ExpressionIR` relates to the two existing
   expression representations — extend / extract-and-migrate / predicate-focused with an
   explicit convergence path.

Dependency note: S1 (`agentic-mbse/.project/active/spike-constraint-fact-shapes/`) started
the same day and had no findings when S2's probes ran, so S2 used provisional probe shapes.
S1 concluded (passing) while S2 was being written up; its results were checked against this
spike's blocked rows before close-out and agree (see Summary).

Metadata at start:

- Date: 2026-07-11 12:57 PDT
- Repo: sysml-codegen, branch `main`, commit `430404d`
- Companion repo: agentic-mbse at `/home/reid/1cfe/agentic-mbse` (HEAD `d340c8e`)
- syside 0.8.4

## The two existing representations (read-only baseline)

- **Representation A — `ExpressionAST`**
  (`src/sysml_codegen/extraction/expression_compiler.py:56`): semantic IR compiled to
  Python strings. Arithmetic-only (`+ - * / ** ^`, `[` stripped), binary tree with n-ary
  left-fold at construction, references pre-classified as input/intermediate at build time,
  explicit UNSUPPORTED node. **Never serialized** — built, compiled, discarded; only the
  Python string survives into snapshots (`compilation_results`).
- **Representation B — `reconstruct_expression`**
  (`agentic-mbse/src/agentic_mbse/sysml/expression.py:420`): display-text reconstruction.
  Wide operator coverage (comparisons, `and/or/not/implies`, Boolean/string literals,
  invocation catch-all, precedence-aware parens) but output is a string — a display/debug
  aid by charter.

Neither is both semantic **and** serializable; that is the gap `ExpressionIR` fills.

## Log

### 1. Context and baseline (read-only)

- Concept S2 scope read; S1 status checked (started, no findings).
- Two-step oracle recipe confirmed from WI-014 findings
  (`fusion-tea/work/completed/20260705_WI-014_sysml-wiring-construct-validation/findings.md`).
- Fixture predicates located: `tests/fixtures/wi014_toy/toy_library.sysml:58`
  (`cost <= budget`), `tests/fixtures/plant_values/library.sysml:37` /
  `fusion-tea/models/library/analyses/fusion_cycle.sysml:48` (`eta * gain >= threshold`,
  defaulted formal). Inline owner-reference, negated, and compound-Boolean predicates are
  not in committed fixtures — the spike authors them in scratch models.
- syside evaluation API confirmed against bundled docs
  (`agentic-mbse/docs/syside/python/v0.8.4/`): `Compiler.evaluate` signature, `Value`
  union, no value-injection parameter, non-finite semantics undocumented (hence probe 3's
  live check).

### 2. Probe 1 — structure discovery + two-step (`probe1_structure_and_twostep.py`)

- `constraint_def.result_expression` is the predicate `OperatorExpression` directly.
- Referents carry name + qualified name on the `FeatureReferenceExpression`.
- Two-step reproduced on committed wi014_toy: `evaluate(predicate, scope=affordable)` →
  `(True, report)` (3000 ≤ 5000).

### 3. Probe 2 — five shapes × four points, live parity (`probe2_parity.py`)

Scratch model per point (satisfied / violated / boundary / mixed-branch), since syside has
no value injection. All **20 evaluations agree** (typed two-step and inline forms); JSON
round-trips byte-stable per load and across the four independent loads; `is_negated=True`
observed only on the `assert not` usage; the defaulted `threshold` resolved live through
usage scope; boundary points exact (`<=`/`>=` true at equality, margin 0.0; negated `>` at
equality: raw false → satisfied, margin −0.0).

### 4. Probe 3 — non-finite Kleene table + margins (`probe3_nonfinite_kleene.py`)

- 72 leaf checks: every comparison × {NaN, +inf, −inf} × both operand positions →
  unknown/indeterminate/margin-None. (+inf deliberately unknown where IEEE would answer.)
- Connectives: `false and unknown = false`, `true and unknown = unknown`,
  `true or unknown = true`, `false or unknown = unknown`, `not unknown = unknown`.
- Compound with non-finite in every Boolean position, including the case where a NaN branch
  is rescued to an overall **satisfied** (`unknown or true = true`).
- Margin sign under negation: satisfied ⇒ positive, violated ⇒ negative, non-finite ⇒ None.
- **Informative live check:** `(1.0/0.0) <= 5000.0` in live SysIDE → `False`, `fatal=False`,
  zero diagnostics. A silent confident verdict from a broken value.

### 5. Probe 4 — calc-side compat, the decision evidence (`probe4_calc_compat.py`)

Every CalcDef output expression in wi014_toy, plant_values, and a stress scratch model
(4-term product, `-x + y`, `x ^ 2.0`, `(x+y)/(x-2.0)`, `x+y+2.0+x`) rendered through
IR + compat renderer **byte-identical** to today's `build_expression_ast` +
`compile_expression` output. Zero divergences.

### 6. Probes 5–7 — committed fixtures + oracle envelope
(`probe5_committed_fixtures.py`, `probe6_arity.py`, `probe7_oracle_scope.py`)

- wi014_toy `affordable`: live True, compiled True at hand-transcribed operands
  (cost 3000 = 4·3·250, budget 5000), margin 2000.
- plant_values `viability`: live two-step hits the **step-limit recursion** — the known
  WI-014 self-named-binding trap (`in gain = gain`, deliberately in this fixture). Probe 7
  swept scopes: assert usage → step-limit; part def / every part usage → type-error
  `'element' * 'element'`; `evaluate_feature` → returns the usage element. No scope
  resolves usage-supplied cross-part values for a def-owned assertion.
- Committed predicate trees are structurally identical (QNs stripped) to the scratch
  replicas whose parity passed — the boundary is the oracle's, not the tree's.
- Probe 6: `a * b * c * d` arrives from syside as nested binary, not one 4-operand node.

## Reproduction

From the sysml-codegen repo root (syside license loads for script runs, not bare `python -c`):

```bash
uv run python .project/active/spike-expression-tree-parity/probe1_structure_and_twostep.py
uv run python .project/active/spike-expression-tree-parity/probe2_parity.py        # exit 0, ALL PARITY CHECKS PASSED
uv run python .project/active/spike-expression-tree-parity/probe3_nonfinite_kleene.py  # exit 0, ALL KLEENE-TABLE CHECKS PASSED
uv run python .project/active/spike-expression-tree-parity/probe4_calc_compat.py   # exit 0, ALL CALC RENDERINGS BYTE-IDENTICAL
uv run python .project/active/spike-expression-tree-parity/probe5_committed_fixtures.py # exit 0 (plant_values live=None is the expected oracle boundary)
uv run python .project/active/spike-expression-tree-parity/probe6_arity.py
uv run python .project/active/spike-expression-tree-parity/probe7_oracle_scope.py  # prints the scope sweep; no pass/fail
```

Scratch models are generated into temp dirs by the probes; `s2_ir.py` holds the provisional
IR/extractor/compilers all probes share. All scripts are throwaway spike code.

## Open Questions / Follow-ups

- **S1 alignment (resolved during close-out):** S1 concluded the same day and agrees with
  every blocked row here. Remaining action for spec: adopt S1's frozen fact shapes for the
  IR's `feature_ref` fields and literal typing — this spike's pydantic fields are
  probe-grade stand-ins.
- **Oracle envelope for later spikes:** S4's live/snapshot comparisons should not lean on
  the SysIDE evaluator for any usage carrying self-named bindings or usage-supplied
  cross-part values; hand-transcribed fixture literals are the oracle there.
- **Untested constructs:** `xor`/`implies` parity, unit-annotation policy (S1's matrix),
  invocation compilation (blocked in v1 anyway), n-ary operator nodes from live syside
  (none observed for infix arithmetic).
- **Calc-migration surface beyond the seam:** probe 4 covers the expression-compiler seam
  only; aggregation walking, computed attributes, and snapshot `compilation_results`
  replay are separate consumers to bring over under the byte-identity gates during the
  staged cutover.
