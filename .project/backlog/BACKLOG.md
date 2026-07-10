# Product Backlog

Prioritized list of epics and features.

**Last Updated**: 2026-03-06

---

## Priority Legend

- **P0**: Critical - Blocking, do immediately
- **P1**: High - Important, do soon
- **P2**: Medium - Valuable, do when possible
- **P3**: Low - Nice to have, do eventually

---

## In Progress

### [EPIC-PDFV4-002] PDF Extraction Quality & Features

**Priority**: P1
**Effort**: ~6 days (6 items)
**Status**: In Progress (Items 1-4 complete, Items 5-6 remaining)
**Epic**: `.project/backlog/epic_pdf-extraction-improvements.md`

**Problem**: v4 pipeline shipped with quality regressions (running headers, GMFT routing, equation detection) and no image output (figures, table crops all discarded). These are the "last mile" issues before production-quality extraction.

**Goal**: Fix quality regressions, build unified image output pipeline (figures + table crops + future equation crops via single ImageCollector mechanism), add OCR for scanned PDFs.

**Items**: ~~(1) Quality gate+routing fixes~~ ✅, ~~(2) Unified image output~~ ✅, ~~(3) Pipeline profiling~~ ✅, ~~(4) Equation region detection~~ ✅, (5) OCR integration, (6) Summarize hallucination fix

---

## P0 - Critical Priority

*No P0 epics*

---

## P1 - High Priority

### [ITEM-DOCLING-002] PDF Skill Deployment — Docling MCP Setup in Init

**Priority**: P1
**Effort**: 2-3 days
**Status**: Needs design revision (spec+design from Feb 6, pre-v4)
**Active**: `.project/active/pdf-skill-deployment/`

**Problem**: The `pdf-analysis` skill ships a 3-tier extraction pipeline but Tier 2 (Docling MCP) requires manual setup. Users get references to `mcp__docling__*` tools that don't exist out of the box.

**Goal**: `agentic-mbse init` auto-configures Docling MCP server. Revisit design to align with v4 pipeline architecture and current best practices.

---

## P2 - Medium Priority

### [ITEM-SYNC-F1] SysIDE self-named-recursion vendor note (evaluation-time finding)

**Priority**: P2
**Effort**: 0.5 day (write the reproducer + report)
**Status**: Note filed — draft at `.project/research/20260706_syside-self-named-recursion-vendor-note.md`
**Source**: UPSTREAM-FINDINGS Item 12 (F1); Item 8 WI-014 toy

**Finding**: A self-named binding (`in P = P` resolving to the calc's own parameter) trips
SysIDE into recursion at **expression-evaluation time, not extraction time** — extraction is
finite/degenerate (Item-8 probe, `timeout 150`, exit 0). The draft note records the
distinction. Out of scope for Item 12: writing the full vendor report or contacting
Sensmetry. This item is to produce a minimal reproducer and, if warranted, a report.

**Item 9 disposition (R-VENDOR): DECLINE the Sensmetry filing.** The recursion is
evaluation-time syside behavior; sysml-codegen extraction is finite/degenerate (Item-8 probe,
`timeout 150`, exit 0), so no codegen path is affected. This note stays as the durable record of
the finding, but the item is not escalated to a vendor report/contact. Revisit only if a supported
model drives syside into extraction-time recursion.

---

### [ITEM-SYNC-F2] V11 model-side mirror check (candidate)

**Priority**: P2
**Effort**: ~0.5 day (check + fixture)
**Status**: Candidate
**Source**: UPSTREAM-FINDINGS Item 12 (F2); warning-reconciliation (Item 7)

**Idea**: A design-attribute binding whose `*_params` key no parameter group provides — the
model-side mirror of codegen's V11 (hard FAIL). Recorded by Item 7 as a candidate, not
floor; codegen V11 is the backstop, so this is a nice-to-have early warning at L2/L6.

---

### [ITEM-SYNC-C7] attribute-`:>>`-with-expression WARN — ✅ BUILT (PIPELINE-TRUTH Item 9)

**Priority**: P2
**Effort**: ~0.5 day (check + fixture)
**Status**: ✅ Done — built in PIPELINE-TRUTH Item 9 (`pipeline-truth-item4`, commit `fa3b706`).
`check_attr_redef_expression_dropped` (level6_architecture.py) + `L6_ATTR_REDEF_EXPR_DROPPED`
fires on an AttributeUsage `:>>` with a non-literal RHS; stays silent on the bare `:>>` forms
(ReferenceUsage) and the `attribute :>>`-literal form. Fixtures `tests/fixtures/item9/attr_redef_expr`
(fires) + `attr_redef_literal` (silent). A live syside probe confirmed the trigger boundary is cleanly
distinguishable (AttributeUsage vs ReferenceUsage) before the check landed — the C6 defect-class risk
that deferred it is retired.
**Source**: UPSTREAM-FINDINGS Item 12 (C7); cross-part-wiring

**Idea**: WARN when `attribute :>> attr = <expression>` carries an expression RHS — this
AttributeUsage-redefinition form is silently dropped at extraction (`hierarchy_resolver.py`
`_extract_single_redefinition` scans only ReferenceUsage). Doc D5 (semantic-operators.md)
already teaches the bare-`:>>` form as the fix.

**Why filed, not built in Item 12**: the correct trigger boundary is subtle — must fire on
an *AttributeUsage* redefinition with an *expression* RHS, but NOT on the supported bare-`:>>`
(ReferenceUsage) value form nor on a literal-valued redefinition. A rushed check risks the
C6 defect class (flagging a shape codegen accepts). Build it with its own negative fixture
AND a negative-of-the-negative (bare-`:>>` literal must not fire).

---

### [ITEM-SYNC-C8] two-names-one-identifier WARN (Item 12 fileable)

**Priority**: P2
**Effort**: ~0.5–1 day (needs a shared sanitizer)
**Status**: Ready — shared sanitizer landed; sibling-scope collector still needed
**Source**: UPSTREAM-FINDINGS Item 12 (C8); identifier-sanitization (Item 5); PUSH-DOWN Item 2

**Idea**: WARN when two distinct SysML sibling names sanitize to one Python identifier, before
codegen fails on its duplicate-path error (REQ-NC-09).

**Rule**: Within one owning namespace, if two distinct raw SysML names produce the same
`agentic_mbse.sysml.qualified_names.sanitize_name(...)` result, emit a Level-6 WARNING.

**Fixture shape**: two siblings under the same owner named `'a b'` and `'a-b'` should warn;
the same pair under unrelated owners should not warn.

**Severity**: WARNING

**Rationale**: PUSH-DOWN Item 2 moved the sanitizer into agentic-mbse, removing the drift risk.
The remaining work is the sibling-scope collector. That collector is broader than the utility move
and should land with dedicated positive and unrelated-namespace negative fixtures. codegen's
duplicate-path error remains the backstop until then.

**Item 9 disposition (R-C8): KEEP FILED.** Item 5 landed SC-4 sanitizer-injectivity fail-fast in
codegen, so a two-names-one-identifier collision fails loudly at generation. PUSH-DOWN Item 2
removed the shared-sanitizer blocker; this row now tracks only the Level-6 pre-warn collector.

---

### [ITEM-EXAMPLES-001] Example Store for Modeling Agents

**Priority**: P2
**Effort**: TBD (needs design)
**Status**: Idea

**Problem**: Modeling agents lack access to successful prior examples when tackling new modeling tasks. Each session starts fresh without leveraging patterns that worked well in similar situations.

**Goal**: Build an "example store" similar to the learning feedback loop, but focused on capturing and retrieving successful model fragments, patterns, and solutions.

**Key questions to explore**:
- What constitutes a "successful example"? (validated models, user-approved patterns, etc.)
- How should examples be indexed for similarity search? (by domain, pattern type, structure?)
- What metadata is needed? (context, constraints solved, related learnings)
- How do agents query the store during workflows?
- Should examples be curated or auto-captured?

---

### [ITEM-PM-STUBS-001] Complete PM Operations Stubs

**Priority**: P2
**Effort**: 1-2 days
**Status**: Ready

**Problem**: Two PM operations in `src/agentic_mbse/pm/operations.py` have incomplete implementations:
1. **Line 849**: `impact_query()` — `affected_work_items` always returns empty list (needs model→work-item mapping)
2. **Line 1134**: `supersede_insight()` — Raises `NotImplementedError` (needs full supersession flow per `workflows.md § 6.1`)

**Goal**: Implement both operations fully, or document them as intentional limitations.

---

### [EPIC-LCOE-001] LCOE Costing Patterns

**Priority**: P2
**Effort**: TBD (needs research sync with fusion-tea)
**Status**: Tracking
**External Work**: `~/1cfe/fusion-tea`

**Problem**: The MBSE → sysml-codegen → teax-simkit pipeline needs nested cost model patterns validated and tooling upgraded.

**Tracking only** - active development happens in fusion-tea and sysml-codegen repos.

---

### [EPIC-VIZ-001] Visualization Tool Integration

**Priority**: P2
**Effort**: TBD
**Status**: Tracking
**External Work**: `~/1cfe/fusion-tea/proof_of_concept/`

**Problem**: Need to visualize SysML model structure for stakeholder communication and debugging.

**Tracking only** - active development continues in fusion-tea POC.

---


### [PUSH-DOWN-EXPR-PROFILE-CHAIN-SEGMENTS] Codegen-Compatible Chain Segment Profile Check

**Priority**: P2
**Effort**: ~0.5-1 day
**Status**: Filed by sysml-codegen PUSH-DOWN Item 1
**Source**: sysml-codegen `.project/active/expression-reconstruction-push-down/design.md` SC-G

**Rule**: Reject or warn in the codegen-compatible profile when full feature-chain segment extraction is empty, lossy, or uses an unsupported anonymous segment.

**Fixture shape**: `a.b.c` chain where `target_feature.name is None` and `target_feature.chaining_features == [b, c]`; include a clean supported chain and an anonymous/lossy segment case.

**Severity**: ERROR

**Rationale**: sysml-codegen depends on full chain segments for supported multi-hop paths. The shared `extract_feature_chain_segments` helper now exposes the fact in agentic-mbse, but wiring a profile check needs dedicated fixture work beyond the expression move.

---

### [PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-SHAPE-MESSAGE] Opaque Expression Reconstruction Profile Warning

**Priority**: P2
**Effort**: ~0.5 day
**Status**: Filed by sysml-codegen PUSH-DOWN Item 1
**Source**: sysml-codegen `.project/active/expression-reconstruction-push-down/design.md` SC-G

**Rule**: Warn when codegen-compatible validation sees an expression shape that reconstructs only through the opaque `str(node)` fallback.

**Fixture shape**: Unsupported anonymous expression form that reconstructs only via `str(node)`, plus supported FeatureReferenceExpression, FeatureChainExpression, OperatorExpression, literal, null, and invocation controls.

**Severity**: WARNING

**Rationale**: Codegen-compatible validation should produce clear diagnostics before generation when reconstruction falls back to non-semantic text. The shared `reconstruct_expression` helper makes this detectable, but the exact validation surface should be designed with fixtures.

---

### [PUSH-DOWN-EXPR-PROFILE-UNSUPPORTED-OPERATOR] Codegen-Compatible Unsupported Operator Profile Check

**Priority**: P2
**Effort**: ~0.5-1 day
**Status**: Filed by sysml-codegen PUSH-DOWN Item 1
**Source**: sysml-codegen `.project/active/expression-reconstruction-push-down/design.md` SC-G

**Rule**: Error when a codegen-targeted expression uses an operator outside the codegen-supported operator set.

**Fixture shape**: OperatorExpression with an unsupported operator, plus supported `+`, `-`, `*`, `/`, comparisons, `and`, `or`, and `not` controls.

**Severity**: ERROR

**Rationale**: agentic-mbse should flag operators codegen cannot compile before generation. The shared operator maps and precedence helpers provide the expression facts; a separate profile item should pin the supported set and user-facing diagnostic.

## P3 - Low Priority

### [ITEM-ITERATION-LOOP] Experiment Iteration Loop

**Priority**: P3
**Effort**: TBD (spec exists, needs design)
**Status**: Shelved
**Active**: `.project/active/iteration-loop/`

**Problem**: Running unattended iterative experiments (e.g., PDF extraction quality improvement) requires manual orchestration of fresh-context cycles, prompt templates, and result comparison.

**Goal**: Build an outer-loop + inner-loop shell script system with prompt templates and an IterationSpecAgent for running unattended iterative experiments with fresh context per cycle.

---

### [ITEM-ARTIFACT-SCAFFOLD] Artifact Scaffolding via PM Script

**Priority**: P2
**Effort**: 1-2 days
**Status**: Spec complete
**Active**: `.project/active/artifact-scaffolding/`

**Problem**: 5 commands tell agents to manually fill in YAML frontmatter templates. Agents don't reliably follow these: they skip fields, use wrong formats, or invent non-standard fields, silently breaking PM automation.

**Goal**: Single `agentic-mbse pm create-artifact --type <type>` command that creates files with correctly populated frontmatter and scaffolded body sections. Commands change from "write this frontmatter" to "run this script, then fill in the body."

---

### [ITEM-ARCH-WALKTHROUGHS] Architecture Validation Walkthroughs

**Priority**: P3
**Effort**: 2-3 hours
**Status**: Deferred

**Problem**: EPIC-ARCH-003 D3.5 interactive validation walkthroughs were not completed. These require running each new command in a real target project and verifying end-to-end behavior.

**Goal**: Run all 14 commands + 5 new commands in fusion-tea or a test project to verify proper behavior.

---

## Completed

| Item | Completed | Duration | Notes |
|------|-----------|----------|-------|
| EPIC-PDFV3-001: PDF Extraction v3 | 2026-02-08 | 3 days | 4-layer pipeline, Claude structure repair, 4/5 new docs pass |
| EPIC-ARCH-001: Architecture Structure | 2026-02-03 | 3 days | 4-directory architecture, templates, cmd_init rewiring |
| EPIC-ARCH-002: Architecture Knowledge | 2026-02-03 | 2 days | 9 new skills, context measurement, extraction mapping |
| EPIC-ARCH-003: Architecture Commands | 2026-02-03 | 3 days | 14 commands refactored/created, registration, agent cleanup |
| EPIC-ARCH-004: Architecture PM Engine | 2026-02-03 | 3 days | 8 parsers, state derivation, dashboard, 14 operations, CLI |
| EPIC-DOC-001: Documentation Discoverability | 2026-01-13 | 2 days | INDEX.md approach, 4 specialized agents, stdlib sync |
| ITEM-BACKPORT-001: Backport fusion-tea Patterns | 2026-01-13 | 0.5 days | Added 3 validated patterns to MODELING_GUIDE.md.template |
| ITEM-GUIDE-001: Progressive Disclosure Restructure | 2026-01-15 | 1 day | MODELING_GUIDE.md reduced from 1497→205 lines, 12 pattern docs |
| ITEM-DEVMODE-001: Development Mode (--dev flag) | 2026-01-15 | 1 day | `agentic-mbse init --dev` creates symlinks for tool-owned files |
| ITEM-LEARNING-001: Learning Feedback Loop | 2026-01-15 | 1 day | `/record-learning` skill + RAW_LEARNINGS.md template |
| ITEM-SYSIDE-001: SysIDE v0.8.4 Upgrade | 2026-01-16 | 0.5 days | CLI + Python package + versioned docs with compatibility symlinks |
| ITEM-RENAME-001: Rename `project/` to `modeling_pm/` | 2026-01-23 | 1 day | CLI, templates, commands, agents all updated |
| ITEM-REGTEST-001: Model Regression Testing | 2026-01-23 | 1 day | pytest infrastructure for SysML models |
| ITEM-SYMLINK-001: Tool-Owned File Safety | 2026-01-23 | 1 day | Hash-based modification detection |
| EPIC-PDFV4-001: PDF Extraction v4 | 2026-02-27 | ~5 days | Quality-gated per-page pipeline, 4 items, extract --check |
| EPIC-PDFV4-002 Item 1: Quality Regressions | 2026-03-01 | 3 days | Equation fragment detection, GMFT xref routing, postprocess cleanup |
| EPIC-PDFV4-002 Item 2: Unified Image Output | 2026-03-01 | 1 day | ImageCollector/ImageEntry pattern, figure+table crop pipeline |
| EPIC-PDFV4-002 Item 3: Pipeline Profiling | 2026-03-01 | 0.5 days | PipelineProfile dataclass, --profile flag, profile.json output |
| EPIC-PDFV4-002 Item 4: Equation Region Detection | 2026-03-01 | 1 day | LayoutPredictor integration, NMS, --no-equations flag |
| Subprocess TTY Fix | 2026-03-01 | 0.5 days | start_new_session=True for Claude CLI subprocess calls |
| Docling Deep-Dive | 2026-03-06 | — | Research complete (Phases 0-2). Phases 3-4 not needed. |
| Pandoc Deep-Dive | 2026-03-06 | — | Research complete (Phases 1-4). Findings integrated into v4. |
| ~~EPIC-CMDREV-001: Command System Revision~~ | — | — | **Superseded** by EPIC-ARCH-002 + EPIC-ARCH-003 |
| ~~TASK-PDF-001: Header Consistency~~ | — | — | **Superseded** by EPIC-PDFV3-001 (Claude structure repair handles this) |

---

## Ideas / Future Considerations

**Agent Improvements**:
- Enhanced error message interpretation (suggest imports automatically)
- Integration tests for agent responses
- Agent self-correction patterns (try → fail → research → retry)

**Learning System Extensions**:
- Automatic categorization of learnings via LLM
- Similarity detection to avoid duplicate learnings
- Periodic digest generation from RAW_LEARNINGS.md
- Hook-based auto-capture on debugging success

**Developer Experience**:
- Watch mode for dev symlinks (auto-reload on changes)
- `agentic-mbse diff` command to compare project vs templates
- Migration tool for updating user-owned files with new features

### [ITEM-SYNC-F6] L6 derived-expr-references-design-attrs flags supported FORMULA shapes ✅

**Found**: 2026-07-06, orchestrator cross-repo sweep during the UPSTREAM-FINDINGS Item 12 audit.
**Fixed**: 2026-07-06, on `upstream-findings-sync`.
**Symptom**: `run_all_checks` on sysml-codegen's `quoted_owner_formula` fixture fails L6 with
"Derived expression references design attributes ['revenue', ...]" — but that shape (a FORMULA
computed attribute reading design attributes) is first-class in sysml-codegen (Item 5 landed the
quoted-owner FORMULA wire; the fixture generates and resolves end-to-end).
**Class**: third L6 false-positive family, sibling to the two C6 fixed (calc-def-internal derived
expr; quoted-name EQN). Not in the Item 12 impact list — the fixture was never run through
agentic-mbse validation in any item's records.
**Fix**: `check_static_expressions` (`adr002.py`) now exempts a design computed attribute whose
feature refs all resolve to same-part owned siblings (a codegen FORMULA, verified against
`computed_attribute_extractor.py::_classify_attribute_expression`). A reference to a calc output
in a foreign namespace (`calc.out * 0.95`), a self-reference (REQ-CA-07), or a dotted path
(FeatureChainExpression) still fires. Fixture `tests/fixtures/item12/formula_computed/` carries
both directions; three pre-Item-5 tests in `test_sysml/test_adr002.py` that asserted the old
blanket rule were updated to the relaxed contract.


### [PUSH-DOWN-HIER-PROFILE-REDEF-PRECEDENCE] design-vs-type redefinition precedence WARN

**Priority**: P2
**Effort**: ~0.5-1 day
**Status**: Filed - needs codegen precedence facts or shared precedence contract
**Source**: PUSH-DOWN Item 3 hierarchy-profile close-out

**Rule**: Warn when one consumer scope has both a design-level override and a type-level literal
redefinition for the same target, and the design override wins under codegen precedence.

**Fixture shape**: Part def `Driver` has `:>> efficiency = 0.3`; design usage has
`:>> driver.efficiency = 0.35`. The warning should explain that the design-level value wins.

**Severity**: WARNING

**Rationale**: PUSH-DOWN Item 3 moved primitive redefinition facts, but precedence depends on
design override scope and supplied-value/codegen policy that intentionally remain in sysml-codegen.
This should land only after that precedence contract is available as shared facts or a profile API.

---

### [PUSH-DOWN-HIER-PROFILE-UNSUPPORTED-RHS] unsupported redefinition RHS WARN

**Priority**: P2
**Effort**: ~0.5 day
**Status**: Filed - coordinate with existing expression-profile unsupported-shape rows
**Source**: PUSH-DOWN Item 3 hierarchy-profile close-out

**Rule**: Warn when a `ReferenceUsage` redefinition classifies as `EXPRESSION` and the expression
uses a codegen-unsupported shape or operator.

**Fixture shape**: Bare `:>> cost = unsupported_fn(a.b)` warns; literal, feature-chain, and
supported arithmetic-expression redefinitions do not warn.

**Severity**: WARNING

**Rationale**: Shared hierarchy classification can expose expression RHS values early, but support
for operators/functions belongs to the existing expression-profile checks. This row keeps the
hierarchy trigger filed without duplicating or drifting expression support policy.

---

### [PUSH-DOWN-HIER-PROFILE-MULTIPLICITY-SHAPE] unresolved multiplicity shape WARN

**Priority**: P2
**Effort**: ~0.5-1 day
**Status**: Filed - needs model-level multiplicity fixture and Level-6 integration
**Source**: PUSH-DOWN Item 3 hierarchy-profile close-out

**Rule**: Warn when a child `PartUsage` multiplicity has no resolvable `cached_lower_bound`, or when
its upper-bound referent has no integer literal default.

**Fixture shape**: `part cell[pack_count]` where `pack_count` has no literal integer default warns;
`part cell[20]` or `part cell[pack_count]` with `pack_count = 20` does not warn.

**Severity**: WARNING

**Rationale**: Shared multiplicity facts are now available, but Level 6 needs a real model-level
fixture and integration path. Filing avoids a mock-only validator that would not prove the user-facing
profile behavior.

---

### [PUSH-DOWN-HIER-PROFILE-AMBIG-INHERITED-ATTR] ambiguous inherited attribute WARN

**Priority**: P2
**Effort**: ~1 day
**Status**: Filed - needs usage-type indexing or shared type-selection facts
**Source**: PUSH-DOWN Item 3 hierarchy-profile close-out

**Rule**: Warn when a usage has multiple incomparable owned typings that can supply different
inherited attribute defaults for the same target.

**Fixture shape**: A part usage has two unrelated typed targets, and both targets redefine the same
attribute literal. The profile should warn before codegen chooses sorted-first behavior.

**Severity**: WARNING

**Rationale**: Detection requires most-specific type comparison and inherited attribute selection.
Those surfaces remain in sysml-codegen for PUSH-DOWN Item 3, so the profile rule is filed rather
than implemented by importing codegen policy.

---


### [PUSH-DOWN-AGG-PROFILE-SUM-SHAPE] unsupported aggregation sum operand WARN

**Priority**: P2
**Effort**: ~0.5-1 day
**Status**: Filed - needs aggregation-profile integration over shared aggregation facts
**Source**: PUSH-DOWN Item 4 aggregation-profile close-out

**Rule**: Warn when a codegen-targeted aggregation expression uses `sum(...)` on an operand that
cannot decompose to a supported child feature chain or local reference, unless existing expression or
hierarchy profile checks already cover the rejected operand shape.

**Fixture shape**: `:>> total = sum(module.cost)` is clean; an unsupported operand shape warns only
if not already covered elsewhere.

**Severity**: WARNING

**Rationale**: Aggregation-specific unsupported sum operand diagnostics need profile integration over
shared aggregation facts. PUSH-DOWN Item 4 preserves generation behavior and avoids adding a shallow
rule that could duplicate existing expression diagnostics.

---

### [PUSH-DOWN-AGG-PROFILE-WRAPPER-SHAPE] aggregation wrapper compatibility WARN

**Priority**: P2
**Effort**: ~0.5-1 day
**Status**: Filed - profile-only warning must not change generation behavior
**Source**: PUSH-DOWN Item 4 aggregation-profile close-out

**Rule**: Preserve current generation behavior for wrapper unwrapping. Any profile-only warning for
unsupported wrappers must be explicitly separated from the behavior-preserving aggregation move.

**Fixture shape**: `sum(Evaluation(module.cost))`, `sum(collect(Evaluation(module.cost)))`,
`Evaluation(allocation.total)`, and current permissive `sum(filter(module.cost))` behavior are
controls. A future stricter wrapper warning is filed rather than implemented in PUSH-DOWN Item 4.

**Severity**: WARNING

**Rationale**: Current generation is permissive inside `sum(...)`; stricter wrapper warnings are
future profile work, not part of this behavior-preserving move.

---

### [PUSH-DOWN-AGG-PROFILE-LITERAL-SHAPE] literal aggregation operand WARN

**Priority**: P2
**Effort**: ~0.5 day
**Status**: Filed - aggregation-specific literal-term policy
**Source**: PUSH-DOWN Item 4 aggregation-profile close-out

**Rule**: Warn when a literal appears where codegen aggregation decomposition cannot use it as a
term, while preserving supported literal rendering inside otherwise valid operator expressions.

**Fixture shape**: `:>> total = sum(module.cost) + 5.0` keeps the literal in neutral operator facts;
`sum(5.0)` is the filed aggregation-specific incompatible shape.

**Severity**: WARNING

**Rationale**: `sum(5.0)` is aggregation-specific and should not be mixed with general literal
expression support. PUSH-DOWN Item 4 keeps the generation path behavior-preserving and files this
profile warning for a dedicated validation pass.

---
