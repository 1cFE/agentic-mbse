# Spec Review: Executable-subset capability inventory and shared profile (EXEC-SUBSET-CONTRACT Item 1)

**Spec:** `.project/active/exec-subset-profile/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/exec-subset-profile/spec-review.md`
**Date:** 2026-10-15
**Code read:** sysml-codegen at `b5663c07` (paths below relative to `~/src/sysml-codegen/src/sysml_codegen/` unless stated), agentic-mbse working tree on `exec-subset-profile`.

---

## Reality Check

Sound. The spec is about the right work item, its Problem section matches the epic and the dc3 evidence, and its Item 2–5 boundaries are drawn where the epic draws them. Most code citations check out (`reference_use.py:395-428`, `elaborated_pipeline.py:389-396` and `:425`, `elaborate.py:2130-2196`, `occurrence.py:812-899`, `project.py:201-218`, the 14/23 corpus split in `batch.json`, the ten PUSH-DOWN rows).

The serious problem is narrower but goes to the heart of R2. The spec treats a generator refusal as a property of a *shape*. In the pinned code it is a property of a shape *in a context*: which expression site, whether the owner is attached to an instantiated scope, which root set. Only ES-004 is specified as context-dependent. Design built on this spec could ship rules that refuse shapes the generator admits, and the corpus criterion would not catch it. That is fixable with targeted edits, so the verdict is Revise, not Rework.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The ES-001 row swaps its two citations. It says calc-def-owned asserts are refused at `elaboration/elaborate.py:815` and calc-usage-owned asserts at `:1625`. The code does the reverse:
- A calc def is a mapped owner kind (`elaborate.py:807`). Its asserted constraints get disposition `owner_kind_unattachable`, graded `error` (`elaboration/graph.py:287-307`), and are refused at `:1625`.
- `:815` fires for an owner metatype that is *not* in the map, such as a calc usage.
- The refused scope is also narrower than "assert". Only the three asserted source forms grade `error` (`graph.py:247`: `definition_typed`, `inline`, `named_usage_reference`). An asserted constraint whose owner has no occurrences grades `warning`, not refusal (`graph.py:290`).

This matters beyond tidiness. The spec now accepts a file-and-line citation as sufficient refusal evidence (see L3-2), and its own most-cited row got the deciding branch wrong.

**L1-2 · Rewrite request:** The promotion rule (§ "Which candidates become evaluator rules") gives as its reason "this is the strongest criterion that keeps R2 safe without generator conformance tests." That overclaims. Observed-only promotion (the previous revision, commit `31b7d4b3`) was stricter. Accepting code-read evidence is a deliberate loosening made after the owner reserved R2. That may be the right call, but the reason should say plainly what was traded: fewer candidate records, in exchange for refusals that no run has observed. It should also say that the owner sees this trade at the R2 gate. Ask the spec agent to restate the reason honestly and route the loosening to R2 explicitly.

**L1-3 · Direct claim (minor, no action beyond L1-2):** Provenance grading is otherwise correct. D2 and the align gap-handling items are `[INFERRED] (ratified by owner …)`, which matches capture-fidelity's absorb mapping for an approved agent recommendation. The one `[HARD]` (no `sysml_codegen` import) is genuinely forced by the dependency cycle and ADR 0007. `[INHERITED]` items cite their epic sections. Nothing settled is below owner grade. I checked that the claimed verbatim align wording ("go") appears; it does.

### Lens 2 — Problem & Approach

**L2-1 · If-then tradeoff:** ES-010's refused scope is "a non-numeric default **reaching a generated entry-point input**" (`project.py:201-218`). Whether a value reaches an entry point is decided during projection. That makes it a fact about the generator's *output*, which ADR 0007 places in codegen, and the agentic-mbse evaluator has no non-heuristic way to compute it before projection. Two readings:
- **If** the refused shape can be restated in model terms (for example "a String-valued feature bound as a calc input"), and that restatement is shown equal to the projection boundary on the fixtures, ES-010 can stay a rule.
- **If** it cannot, ES-010 fails the spec's own second promotion test ("facts extractable … without a heuristic"). It should then be a candidate, with the String omission side left to Item 2's metadata policy (epic open decision 3).

The spec should say which, or state the restatement the rule must satisfy.

**L2-2 · Direct claim (endorsement, no action):** Unifying ES-003 and ES-012 into one binding-source decision is correct. The generator has exactly one classifier (`elaborate.py:2130-2171`) and one disposition (`:2188-2196`), and two detectors could disagree. Reusing `_require_supported_invocation` for ES-005 is also right; it already is the generator's callable boundary.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim (must-fix, R2):** Generator refusals depend on context, and the spec specifies context for only one rule. At `b5663c07`:
- **ES-003/ES-012 (binding source) and ES-007 (BLOCK):** classified only inside `for scope in scopes` (`elaborate.py:1227`, `:1337-1360`). Scopes come from `_attachment` (`:759-787`). A calc or constraint usage owned by a part def with no occurrences has no scopes, so its binding is never classified and the model generates. The ES-003 row instead says "*Any* calc or constraint input binding whose source is neither a literal nor a single reference … is refused." Taken literally, that refuses a shape the generator admits.
- **ES-005 (invocation) and ES-006 (conditional):** the eager expression inventory (`elaboration/expression_evidence.py:233-324`) inspects only (a) declared features' `feature_value_expression` and (b) constraint predicates. It does not inspect a calc def's bare result expression. That body goes to the expression compiler. There an invocation raises `CompilationError` (`extraction/calc_compat_renderer.py:75`), which is caught and becomes `MANUAL_REQUIRED` (`extraction/expression_compiler.py:291-296`): a handwritten stub, not a refusal. The epic asks the evaluator to cover "calc bodies where the capability applies." A design that applies ES-005 to calc bodies, as the spec currently reads, refuses `calc def F { in a; in b; max(a, b) }`, which the generator admits.
- **ES-004:** expansion runs only on composite, user-model `PartUsage`s reachable from package-level roots (`elaboration/occurrence.py:911-918`, `:928-940`, `:989`). Attribute usages with `ordered` multiplicity never reach it. The spec lists this as "not established." It is established by the code, and leaving it open invites an overbroad rule.
- **ES-001:** global, but only for asserted forms (L1-1).

What needs to be true: every rule record's "exact applicability and context" names the generator site role and attachment condition under which the refusal fires. The admitted-neighbor list gains the out-of-context variants: an uninstantiated owner for ES-003/ES-012 and ES-007, and a calc-def result-expression body for ES-005 and ES-006. Each neighbor carries observed generator evidence (see L3-2). The epic's design principle 4 and Item 1 scope 5 already require this. The spec's success criteria do not test it.

**L3-2 · Direct claim (must-fix, R2):** A code-path citation is good evidence that a branch refuses. It is weak evidence that a shape *reaches* that branch in a given context, and reachability is where R2 risk lives (L3-1). Three facts make the current standard too weak:
- The spec's own ES-001 citations are wrong (L1-1).
- The spec's corpus criterion cannot catch an overbroad code-read rule. I scanned the 14 snapshot fixtures: they contain no function invocations at all, no `ordered` or `nonunique` multiplicity, and no range multiplicity. A rule that over-refuses `min`/`max`, ordered or nonunique parts, or calc-body invocations passes the corpus run untouched.
- Observation is cheap here. The prototype's read-only oracle (`.project/concepts/convince-me-exec-subset/evidence/01-codegen-oracle.py`) already runs fixtures through the pinned generator.

My recommendation: keep code-read evidence as enough to *promote* a family to a rule and to design its facts. But the evaluator may emit `refused` for a shape only after an Item 1 read-only probe has observed the refusal in the stated context. Until then that shape reports `unconfirmed`. This costs a handful of probe fixtures. It also turns the "No refused shape lacks generator evidence" criterion into something a reviewer can check by rerunning, not by re-reading code. The alternative, if the owner prefers the current standard: require each code-read citation to include the call path from the public entry point and the context condition, not just the deciding line. That is more review burden for weaker evidence.

**L3-3 · Direct claim (must-fix):** Root selection is under-specified in a way that blocks the spec's own criteria and opens an R2 path.
- The generator's root rule is fixed and computable: every `PartUsage` whose semantic owner is not a part def or part usage (`occurrence.py:911-918`).
- The spec instead makes roots caller-supplied, defers defaults to Items 2 and 3, and says occurrence-dependent rules report `unverified` when no roots are known.
- Consequence 1: the baseline, repaired and corpus runs do not say which roots they use. The repaired-tree criterion fails on any `unverified` result, so either it fails or the runs use roots chosen ad hoc.
- Consequence 2: a caller who supplies a part def, or any root outside the generator's set, gets `refused` findings for occurrences the generator never expands.

What needs to be true: the spec names the generator-equivalent root rule as the scope against which `refused` is decided. A caller may narrow it, and narrowing must be reported as incomplete scope. A caller may not widen it into `refused`. The three acceptance runs use that rule and record it. Items 2 and 3 still own consumer defaults and presentation.

**L3-4 · Rewrite request (should-fix):** The corpus criterion's refusal-fixture clause will raise false R2 stops. The expression inventory fails fast: it raises on the first `SemanticEvidenceError` (`expression_evidence.py:249`, `:259-276`). Readiness findings, by contrast, are collected. So a refusal fixture's recorded multiset can omit a code the generator never reached. An evaluator that correctly reports two refusals then "names a rule whose code is not in the multiset," which the criterion treats as an R2 stop. The criterion should allow a finding whose generator evidence comes from elsewhere (probe or other fixture). It should also state plainly what the corpus run proves and what it does not (L3-2), so design does not lean on it as the R2 guard.

**L3-5 · Rewrite request (should-fix):** The site account and the matrix are not joined. Sites carry D2 dispositions (`in scope` / `handled elsewhere` / `explicit follow-up`). Matrix rows carry the five classes. Nothing requires an `in scope` site to name the matrix row or rule that covers it, or a matrix row to name its sites. Without that join, "inventory complete relative to the pinned surface" cannot be checked: a site could be marked in scope with no rule behind it. Separately, the epic's Item 1 criterion "every deferred case has an owner and coverage limitation" is enforced for matrix rows but not for `explicit follow-up` sites, which need only "evidence pointer and owner." Ask for both gaps to close in the criteria.

**L3-6 · Rewrite request (should-fix):** The spec does not say where generator codes may appear. The corpus criterion needs each rule to name the generator code it corresponds to, and the evidence criterion requires refused shapes to cite "the generator code." The "No consumer coupling" criterion forbids `ElaborationCode` member names in the shared reason vocabulary. Both can hold if `SI_*` strings live only in evidence fields of the records (or in evidence files), never in reason IDs or decision logic. The spec should state that line so design neither violates the coupling rule nor drops the mapping the corpus check needs. The coupling test's scope (reason vocabulary only, or all package data) should be explicit.

**L3-7 · Rewrite request (should-fix):** The unified ES-003/ES-012 decision has four refused outcomes, not one. The generator's `_unsupported_code` (`elaborate.py:2188-2196`) yields `SI_SELF_BINDING`, `SI_INDEXED_SOURCE_UNSUPPORTED` and `SI_EXPRESSION_SOURCE_UNSUPPORTED`. The eager inventory separately refuses indexed references earlier (`expression_evidence.py:274-276`). Indexed references have a named matrix row; self-binding has none, though four corpus refusal fixtures carry `SI_SELF_BINDING`. The spec should require the matrix to place every outcome of this one classifier. It should also require the binding-source fact to reuse the generator's own primitives rather than re-derive them. Those primitives are `is_literal_node` (`agentic_mbse/sysml/expression.py:441`), the unit-annotation unwrap, the `inspect_reference_uses` count, and the `FeatureChainExpression`/`FeatureReferenceExpression` test (`elaborate.py:1115-1118`). A re-derived "single reference" test is the likeliest place for the two to drift.

**L3-8 · Question to the user (low stakes):** "R1 decision is recorded and approved … before planning starts" is a process gate written as a success criterion. It is harmless, and it matches the align route. Do you want it kept as a criterion the audit checks, or moved to the route so the criteria list only product outcomes?

### Lens 4 — Hygiene

No material findings.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** The candidate table (§ "Which candidates become evaluator rules") carries the spec's highest-stakes content: the refused scope each rule may report. Its cells pack citations, codes, evidence status and caveats into one run-on clause each. A reviewer cannot see at a glance which shapes are observed and which are code-read, or in what context each refusal applies. After L3-1 and L3-2 land, ask the spec agent to give context and evidence status their own columns, and to move the line citations out of the prose cells.

---

## Engagement Summary

**Overall take:** The spec is faithful to the epic and the align record, the provenance is clean, and most code claims hold. But it describes refusals as shapes when the pinned generator refuses shapes in specific contexts. Combined with code-read evidence and a corpus that contains none of the risky shapes, this leaves real paths to an R2 breach that no criterion would catch.

**Here's what I need you to weigh in on:**

1. **[L3-1]** Must-fix. Require each rule's applicability to state the generator context (expression site role, attachment to an instantiated scope) and add out-of-context admitted neighbors for ES-003/ES-012, ES-005, ES-006 and ES-007. Without this, ES-003 as written refuses bindings in uninstantiated parts, and ES-005 can refuse calc-body invocations the generator turns into handwritten stubs.
2. **[L3-2, L1-2]** Must-fix. Decide the evidence bar for emitting `refused`. Recommended: code-read promotes a rule, but `refused` is emitted only after an Item 1 read-only probe observes the shape in context; until then the shape is `unconfirmed`. The alternative keeps code-read as sufficient but requires call-path and context citations. Either way, the promotion rule's reason should stop claiming to be the strongest R2-safe option, and the loosening should surface at the R2 gate.
3. **[L3-3]** Must-fix. Pin the generator-equivalent root rule (package-level part usages) as the scope for `refused`, let callers only narrow it, and have the three acceptance runs use and record it.
4. **[L2-1]** Decide whether ES-010 stays a rule. Its boundary ("reaches a generated entry point") is an output fact owned by codegen under ADR 0007.
5. **[L3-5, L3-4]** Join site rows to matrix rows, require coverage limits on follow-up sites, and fix the corpus criterion so fail-fast refusal fixtures do not produce false R2 stops.
6. **[L1-1, L3-7, L3-6]** Correct the ES-001 citations and scope, place self-binding in the matrix, require the binding fact to reuse the generator's primitives, and state where `SI_*` codes may live.

---

## Resolutions

[None yet. This review ran non-interactively for the orchestrator; owner resolutions are to be recorded here keyed by finding ID.]

---

**Verdict:** Revise

**Must-fix:** L3-1, L3-2, L3-3.
**Should-fix:** L1-1, L1-2, L2-1, L3-4, L3-5, L3-6, L3-7, L5-1.
**Optional:** L3-8.

**Next Steps:** Record resolutions above, then return to the spec agent (`/_my_spec`) and point it at this review to incorporate. The reviewer does not edit the spec. If the owner takes the L3-2 recommendation, a fresh spec review is not required after the edits; it is enough to verify that the must-fix items landed.
