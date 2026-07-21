# Spec Review: ExpressionIR — Production Tree, Extraction, Serialization

**Spec:** `.project/active/expression-ir/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/expression-ir/spec-review.md`
**Date:** 2026-07-12

---

## Reality Check

**Sound.** The spec is about the right work item: promote Item 1's provisional `predicate-tree/v0`
tree to the concept's canonical `ExpressionIR` — full node algebra, hardened live extraction,
byte-stable JSON at a bumped sub-version. The Problem section is accurate against the landed code
(`expression_facts.py:25` really does tag the tree `predicate-tree/v0`; `constraint_extraction.py`
really does have the catch-all operator fallback). The node algebra matches the concept (line 87)
and the epic (Item 2 §1) exactly, the leaf-adoption decision is faithful to S2's carry-forward, and
the honest bounds (n-ary latent, Kleene stays in the compiler) are captured correctly. The delta
over the landed v0 tree — operator normalization, adopt Item 1's leaf dataclasses, a real
unsupported node, sub-version bump — is the right delta.

It is not a clean contract yet. Four must-fixes below: one false readability claim that misroutes
design, one provenance misattribution that silently overrides a CERTIFIED artifact, an un-named
migration surface that the "suite green" criterion makes mandatory, and an operator-spelling gap
that would surface as an Item 13 byte-identity failure two items downstream. All are targeted edits;
the underlying work item is sound. Verdict: **Revise** (brief's vocabulary: Approved-with-must-fixes).

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (must-fix):** The spec says the S2 findings are **not readable from this
repo**. Required Reading (line 180): "`spike-expression-tree-parity/findings.md` — **not readable
from this repo** (lives in sysml-codegen); substance is in concept Appendix B." Open Question #5
(lines 164–169) repeats it and tells design/plan to reconstruct fixtures "from Appendix B's
descriptions." **This is false.** The S2 spike reference copies are in-repo at
`.project/reference/s2-spike/` — both `findings.md` (the full "Facts the design can now rely on"
block, the operator matrix, the oracle envelope) and `s2_ir.py` (the proven node shapes, the
`_OPERATOR_ENUM_MAP`, the compat-render logic). They were added in the spec's own commit
(`c21d74e`, "…S2 spike reference copies"). Effect: design would work from Appendix B's summary when
the far richer probe IR and findings are sitting in the repo. **Fix:** correct the readability claim
and point Required Reading + OQ#5 at `.project/reference/s2-spike/`.
*Nuance to preserve, not delete:* the concrete `.sysml` fixture **text** for wi014/plant_values does
live in sysml-codegen, and `findings.md:147–148` records that the inline-owner-ref, negated, and
compound-Boolean predicates were **scratch-generated** (never committed). So OQ#5's underlying
question — do agentic-mbse's landed fixtures cover the five shapes, or must equivalents be authored?
— is still real. The spec just mis-states what evidence is on hand to answer it.

**L1-2 · Direct claim / provenance (must-fix):** The version name `expression-ir/v1` is tagged
`[INHERITED]` with "Source: Item 1 design D4, D9, C1; brief" (lines 107–112). Walk the cited source:
Item 1's design says `predicate-tree/v1` **everywhere** it names the future bump —
`design.md:159` (D4), `:167` and `:389` (D9), `:411` and `:416` (C1 + its Action: "Item 8 pins …
the then-current `predicate-tree/vN`"), `:507`. The epic Item 2 §3 (`epic_…:163`) says only
"versioned," no string. **The only artifact that says `expression-ir/v1` is the brief**
(`briefs/spec.md:15,23`). So the citation names as its source the one artifact that says the
opposite, and omits the one artifact that actually says it. Two problems:
- **Mis-provenance.** Correct grade is `[INHERITED: brief]` (the brief/epic name the tree
  `ExpressionIR`), not inheritance from Item 1's design.
- **Silent override of a CERTIFIED artifact.** Renaming the namespace `predicate-tree → expression-ir`
  is a change *away from* what Item 1's landed, certified design committed to — including its forward
  record that "Item 8 pins `predicate-tree/vN`" (`design.md:416`). Per capture-fidelity Law 4, this
  must be **surfaced**, not buried under an `[INHERITED]` tag pointing at the contradicting source.
  The rename itself is defensible (the production tree is `ExpressionIR`; `predicate-tree/v0` was
  explicitly provisional) and is mechanically fine under D9 (any sub-version string bump is allowed
  to change bytes). The spec's line 110–112 framing of the cross-sub-version non-goal is consistent
  with D9. **Fix:** re-tag to the brief/epic, and add one line noting this supersedes Item 1 design's
  `predicate-tree/vN` phrasing so Item 8's recorded expectation gets updated rather than silently
  contradicted.

**L1-3 · Direct claim (nice-to-have):** The unsupported node's payload is stated two different ways.
Success Criterion 3 (lines 49–53): "metaclass kind, **source text where available**, and a message."
Known Requirement (lines 76–79): "metaclass kind **and a message**" — no source text. S2's
unsupported node carried `node_type` + `diagnostic` only (`s2_ir.py:159–162`); "source text" is an
addition (defensible — it mirrors Item 1's `ExtractionDiagnosticFact.operand_source` via
`reconstruct_expression`). Pick one payload and state it in both places.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim (sound, no action):** The bet — "S2 already proved the hard part; Item 2 is
the production build-out, not new research" (lines 36–38) — is correct and well-supported by
`findings.md` (parity 22/22, byte-stable round-trips, byte-identical calc compat). The item is sized
right (one tree module + extraction + serialization tests, ~7h execute per the epic). No finding.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim (must-fix):** The migration surface for the sub-version bump is not
enumerated, yet Success Criterion "agentic-mbse suite green (default selection)" (line 61) makes
touching it mandatory. Brief probe #1 asked the spec to name every place the sub-version and tree
shape are pinned "so the transition is a defined migration and not a scavenger hunt." It doesn't.
Concrete landed sites the bump breaks, none named in the spec:
- **`tests/fixtures/constraint_fact_shapes/production_facts.json`** — 125 baked `predicate-tree/v0`
  strings plus the full v0 tree shape. `test_production_golden_self_compares`
  (`test_constraint_fact_shapes.py:54`) regenerates production output and byte-compares it to this
  golden, so the golden **must be regenerated** when the tree shape/version change or the suite goes
  red.
- **`test_schema_versions_are_pinned`** (`test_constraint_facts_serialize.py:185`) asserts
  `== "predicate-tree/v0"` — a direct hardcode of the retired name.
- **The hand-built `ExpressionFact` trees** throughout `test_constraint_facts_serialize.py`
  (`_literal_expression`, `_reference_expression`, `_hand_built_facts`) construct the *old* node type
  directly; they migrate to the new node types.
- **The constant `PREDICATE_TREE_SCHEMA_VERSION`** (`expression_facts.py:25`) and its importers:
  `constraint_extraction.py` (3 emit sites), the `sysml/__init__.py` re-export, and the serialize
  test. If the value becomes `expression-ir/v1`, decide whether the constant is renamed too and
  update all four importers.
This is the answer to probe #5's "no landed test hardcodes the retired name in a way the spec
doesn't list": `test_constraint_facts_serialize.py:185` and the 125× golden do, and the spec lists
neither. **Fix:** the spec need not carry every line number, but it must name the golden regeneration
and the pinned-version assertion as required migration steps (they are what "suite green" depends on),
and acknowledge the constant + importer surface. Right now the SC "bump to expression-ir/v1" + "suite
green" are in latent tension with a migration surface the spec doesn't admit exists.

**L3-2 · If-then tradeoff (must-fix — downstream fitness):** The extraction requirement (lines
94–95) says operator normalization maps "SysIDE's operator representation to canonical operator
strings," but never states that the source spelling distinctions the calc-compat renderer needs must
**survive** in the tree. The one that bites: `^` vs `**`. S2 deliberately kept them distinct in the
IR (`_OPERATOR_ENUM_MAP`: `Caret → "^"`, `Power → "**"`, `s2_ir.py:79,87`) and collapsed them to
Python `**` only at *compile* time (`_compile_numeric`, `s2_ir.py:218`). Item 13 renders calc compat
**byte-identically** (spec non-goal, line 136), and S2's probe 4 proved that byte-identity requires
both spellings to persist (`findings.md:74,186` — "`^`→`**`", "byte-identical calc compat"). If
design reads "normalize to canonical" as "collapse `^` to `**` at extraction," the tree still
round-trips byte-stably (SC line 46–48 passes — it stores `**` either way), but Item 13 can no longer
recover `^`. The failure is invisible to this spec's success criteria and surfaces two items
downstream. **Fix:** state that operator normalization is enum→symbol only and preserves distinct
source operator spellings (`^` ≠ `**`, unary-minus spelling, the `[`-annotation), because Item 13's
byte-identity depends on it. Same concern applies to whatever the unit-annotation node carries: the
source spelling (`m`) must survive, not only the resolved `UnitFact` QN (`SI::metre`).

**L3-3 · Direct claim (nice-to-have — asymmetric honesty):** The algebra admits **invocation** as a
first-class node (lines 67–70, and the `[INFERRED]` "tree represents; profile judges" at 80–85), but
S2 gathered **zero** live parity evidence for it — `findings.md:78`: "Invocation, feature chains |
blocked, cataloged | IR nodes exist; no live parity attempted." That is the *same* evidentiary
status as n-ary operators, which the Honest Bounds section (lines 119–126) correctly flags as
"latent … no parity evidence." Invocation gets no such flag, and no success criterion exercises an
invocation extraction. **Fix:** either add invocation to Honest Bounds (representable node kind, no
live producer/evidence in S2) or add a fixture that exercises it. Right now the spec is honest about
n-ary and silent about the equally-unexercised invocation.

**L3-4 · Rewrite request (nice-to-have — sharpen the unsupported boundary):** The *outcome* is fixed
("no silent drop or coercion," lines 49–53) and the structural-vs-profile *principle* (lines 80–85)
is sound. But the failure this item exists to kill is a specific one: the landed extractor's
catch-all coerces **anything** that is not a chain/ref/literal into a generic operator node built
from `str(operator)` + operands (`constraint_extraction.py:365–383`) — including non-operator
metaclasses (a conditional, a select/collect) and unrecognized operators, which become an operator
node with `operator="None"`. Deferring "the exact trigger boundary" *entirely* to design (OQ lines
156–160) risks design satisfying "no silent coercion" while keeping a catch-all that quietly
coerces. **Fix:** make the *inversion* a fixed requirement, not a deferred one — a recognized
operator metaclass with a normalizable operator routes to a productive node; every other metaclass,
and any unrecognized/absent operator, routes to the unsupported node. That allowlist inversion is the
mechanism that kills the silent coercion; the per-metaclass enumeration can stay deferred to design.

### Lens 4 — Hygiene

No material findings. Tags are used consistently; sections are complete; the Non-Goals and Open
Questions are appropriately scoped (module layout, node-kind-vs-field, serialize surface are genuine
design-stage deferrals, not punted spec questions).

### Lens 5 — Reader Comprehension

No material findings. The spec leads with the point, anchors each requirement to a source, and a
tired engineer can skim it once and know the work item and the bets. The one comprehension risk is
downstream, not in the prose: the false "not readable" claim (L1-1) and the mis-cited version
provenance (L1-2) would mislead the *next* agent, which is why they are Lens 1, not Lens 5.

---

## Engagement Summary

**Overall take:** The spec is pointed at the right work item and is faithful to the concept, the
epic, and S2's evidence — the node algebra, the leaf adoption, and the honest bounds are all captured
correctly. But it rests on two claims that don't survive contact with the repo (the S2 findings are
readable; the version name is *not* inherited from Item 1's design), and it leaves the sub-version
migration surface un-named while a success criterion makes touching it mandatory. Fix those and it's
a clean contract.

**Here's what I need you to weigh in on:**

1. **[L1-1]** The spec says the S2 findings are unreadable and tells design to reconstruct from
   Appendix B — but `findings.md` and `s2_ir.py` are in-repo at `.project/reference/s2-spike/` (added
   in the spec's own commit). Correct the claim and repoint design there. Keep OQ#5's real question
   (do the landed fixtures cover the five shapes, or must scratch-only ones be authored?).
2. **[L1-2]** `expression-ir/v1` is tagged inherited from Item 1's design D4/D9/C1 — but that design
   says `predicate-tree/v1` everywhere, and only the brief says `expression-ir/v1`. The rename is
   fine, but it's a silent override of a CERTIFIED artifact dressed as inheritance from it. Re-tag to
   the brief and surface the override (Item 8's "pins predicate-tree/vN" record needs updating).
3. **[L3-1]** The sub-version bump is an un-named migration: the 125× `predicate-tree/v0` golden
   (`production_facts.json`, regenerated + self-compared), the `test_schema_versions_are_pinned`
   hardcode, the hand-built old-node trees, and the constant + its importers. "Suite green" makes all
   of these mandatory; the spec names none. List the migration surface.
4. **[L3-2]** "Normalize operators to canonical strings" must preserve `^` vs `**` (and unary-minus,
   `[`-annotation spelling), or Item 13's byte-identical calc compat breaks two items downstream —
   invisibly to this spec's round-trip criterion. Pin the distinction in the extraction requirement.
5. **[L3-3, L3-4]** Two sharpenings: honest-bound **invocation** the same way n-ary is bounded (no
   live parity evidence in S2), and make the unsupported-node **allowlist inversion** a fixed
   requirement so design can't keep the coercing catch-all.

---

## Resolutions

*Incorporated by the spec agent, 2026-07-12 (orchestrated Item 2 run). All four must-fixes and three
nice-to-haves discharged.*

- **L1-1 (must-fix) — DONE.** Corrected the false "not readable" claim. Problem section now points
  design at the in-repo probe (`.project/reference/s2-spike/s2_ir.py` + `findings.md`); Required
  Reading repointed there. OQ#5's surviving nuance kept and sharpened: the probe IR/findings are on
  hand, but the `.sysml` fixture text for the inline-owner-ref, negated, and compound-Boolean shapes
  was scratch-generated (`findings.md:147-148`) and only WI-014 + IFE viability are committed
  fixtures — so "do landed fixtures cover all five?" remains a real design/plan question.
- **L1-2 (must-fix) — DONE.** Version name re-graded `[INHERITED: brief/epic]` and the namespace
  rename `predicate-tree → expression-ir` recorded as an explicit `[AGENT — recorded override of a
  CERTIFIED artifact]` (agent-grade orchestrator decision), not inheritance from Item 1's design.
  Item 1's certified `constraint-facts/design.md` amended forward (C1 Action + downstream-carry
  handoff) with the correction note; mechanism unchanged (D9 per-pair byte-stability).
- **L3-1 (must-fix) — DONE.** Added a "Migration surface (the sub-version bump)" subsection naming
  the golden regeneration + self-compare (`production_facts.json` / `test_constraint_fact_shapes.py`),
  the `test_schema_versions_are_pinned` hardcode (`test_constraint_facts_serialize.py:185`), the
  hand-built old-node trees, and the `PREDICATE_TREE_SCHEMA_VERSION` constant + its importers. "Suite
  green" now has a defined worklist.
- **L3-2 (must-fix) — DONE.** Extraction requirement now states operator normalization is enum→symbol
  only and preserves distinct source spellings (`^` ≠ `**`, unary minus, `[`-annotation source text);
  added a success criterion that round-trips and distinguishes them, so a collapse is caught here, not
  in Item 13.
- **L1-3 (nice-to-have) — DONE.** Unsupported-payload wording made consistent across SC and the Known
  Requirement: metaclass kind + diagnostic message + source text where available (the last a
  deliberate addition over S2's `node_type`+`diagnostic`).
- **L3-3 (nice-to-have) — DONE.** Invocation added to Honest Bounds with the same evidentiary framing
  as n-ary (representable node kind, no live parity evidence in S2).
- **L3-4 (nice-to-have) — DONE.** The allowlist inversion is now a fixed `[HARD]` requirement
  (allow-known metaclass+normalizable-operator → productive node; every other metaclass and any
  absent/unrecognized operator → unsupported node). The OQ now defers only the allowlist *contents*,
  not the inversion.

---

**Verdict:** Revise (brief's vocabulary: **Approved-with-must-fixes**).

**Must-fix:** L1-1 (false non-readability claim misroutes design), L1-2 (version-name provenance
misattributed + silent override of a CERTIFIED artifact), L3-1 (un-named migration surface that
"suite green" makes mandatory), L3-2 (operator/spelling preservation for Item 13 byte-identity).

**Nice-to-have:** L1-3 (unsupported-payload wording consistency), L3-3 (honest-bound invocation),
L3-4 (fix the unsupported allowlist inversion as a requirement).

**Next Steps:** Once resolutions are recorded here, re-run `/_my_spec` (or return to the spec-agent
session) and point it at this review to incorporate. The reviewer does not edit the spec.
