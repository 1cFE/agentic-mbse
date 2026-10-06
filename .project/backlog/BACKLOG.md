# Product Backlog

Prioritized list of epics and features.

**Last Updated**: 2026-10-05

---

## Reconciliation — 2026-10-04

[INHERITED: existing backlog] Priority labels below are preserved. This refresh establishes implementation status; it does not reprioritize the backlog. See the [status report](../reports/2026-10-04-0901-status-report.md) for fresh probes and cross-repository evidence.

- July constraint-wave, GAP-CLOSE, and CONSTRAINT-EXEC compatibility blockers are resolved by merged successor work. They are not pending features.
- Docling/Pandoc research is closed; iteration-loop remains shelved. Artifact scaffolding is a draft, despite the old “spec complete” label.
- P1 OCR/deployment gaps remain unimplemented; the PDF epic's summarization guard retains explicit item-level P2. Recent P2 registry ID reuse (closed 2026-10-04 as `PM-MATRIX-ESCAPED-PIPE`; see Completed) and empty-insight approval defects are freshly reproduced. PM operation stubs and extraction provenance gaps also remain.

### Newly tracked follow-ups — priority not assigned

| Item | Status | Evidence / next step |
|------|--------|----------------------|
| `L6-LIBRARY-ALIAS-SOURCE` | [AGENT] Filed 2026-10-04 at `L6-EXPOSE-CONSISTENCY` close; recorded limitation, not a regression | An EXPOSE alias to an attribute of a part typed by a `library/` part definition passes Level 6 even when that source value is unset, because completeness path-filters the source declaration and skips the alias ([audit](../completed/20261004_l6-expose-consistency/audit.md) advisory; design R4/B4). How required values on referenced library parts get verified is undecided |
| `NATIVE-DISTRIBUTION-RECONCILIATION` | [AGENT] Draft residual-work spec; product-lens CLEAR | [Distribution spec](../active/native-skill-distribution/spec.md); existing migration requirements reused by reference |
| `CMDREF-001` | [INHERITED: epic_command-refresh.md] P2 draft; scope reconciliation needed | September simplification overlaps this July proposal; inspect remaining objectives before decomposition |
| `C4-PLAIN-SUBTYPE-DOC-TEST` | [INHERITED: ../active/c4-plain-subtype-instantiation/spec.md] Unimplemented draft | Correct stale subtype-chain docstring and add the missing behavior test; current behavior is already deliberate |

---

## Priority Legend

- **P0**: Critical - Blocking, do immediately
- **P1**: High - Important, do soon
- **P2**: Medium - Valuable, do when possible
- **P3**: Low - Nice to have, do eventually

---

## Partially Completed Epics

### [EPIC-PDFV4-002] PDF Extraction Quality & Features

**Priority**: P1
**Effort**: ~6 days (6 items)
**Status**: Items 1-4 complete and merged; Items 5-6 ready in backlog
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

### [PM-APPROVE-RESEARCH-EMPTY-INSIGHTS] `approve-research` refuses a research document that mints no insight

**Priority**: P2
**Effort**: 0.5 day
**Status**: Implemented and certified 2026-10-05 on branch `research-approval-empty-insights` ([audit](../active/research-approval-empty-insights/audit.md)); close next (spec reviewed and revised 2026-10-05; originally filed 2026-08-25)
**Spec**: [Zero-insight approval](../active/research-approval-empty-insights/spec.md)

**Problem**: `approve_research` returns `success=False, message="No insights provided"` when the insight list is empty (`src/agentic_mbse/pm/operations.py:936-940` at `c37ff53`). That treats "this research approved no new domain insight" as a caller error. It is a legitimate and common outcome: a round can approve a research document that registers sources, records a bounded negative, or confirms an existing insight without minting a DI. The refusal means such a document cannot be moved from `knowledge/research/pending/` to `approved/` through the tool at all, so the operator moves the file by hand — exactly the hand-editing the PM exists to remove.

**Goal**: An empty insight list approves the document and mints nothing. Distinguish it from a malformed call: a missing `--insights` argument is still an error; `--insights '[]'` is an explicit "no insights". A test covers both, and asserts the document lands in `approved/` with no DI written.

**Downstream**: fusion-tea `.project/active/goal-research-seam/` — the seam's research surface registers sources under an approval gate that does not mint DIs (spec R-C3, R-C4), so it hits this refusal on every source-only round.

---


### [EXTRACT-PROVENANCE-HOOK] `extract` should return provenance JSON, or expose a `--register` hook

**Priority**: P2
**Effort**: 1-2 days
**Status**: Filed 2026-08-25 (fusion-tea, goal-research-seam implementation)

**Problem**: `agentic-mbse extract` produces everything a downstream registry entry needs — source URL, the hash of the source as fetched, the output path — and returns none of it in machine-readable form. A caller has to re-derive all of it from the output directory, and the layout it must re-derive differs by input kind. Four asymmetries measured against the pinned build on 2026-08-25, each of which a downstream caller currently hard-codes:

1. **Flat vs nested output.** `<url> --output DIR` writes `DIR/output.md`, `DIR/raw.html`, `DIR/metrics.json` flat (`extract_cli.py:222-230` passes `--output` straight through as `output_dir`). A local PDF writes `DIR/<stem>/{output.md,metrics.json,decisions.json,images/}`. Callers flatten by hand.
2. **`--save-source` writes no `raw.pdf` on the local-PDF path.** The flag only persists `result.raw_source_bytes`, which the arXiv shortcut populates (`extract_cli.py:541`). A caller wanting the raw artifact for a local PDF has to copy the input itself.
3. **No `file://` support.** URL dispatch is `startswith(("http://","https://"))` only (`extract_cli.py:407`); a `file://` URL is reported as `path does not exist`. Offline test fixtures therefore need a loopback HTTP server rather than a local file.
4. **`raw.html` is written re-encoded, not as fetched.** The frontmatter `content_hash_sha256` digests the bytes as fetched (`web_backend.py:444` hashes `fetched.content`), but `raw.html` is written from `fetched.text()` — decoded with the declared charset and re-encoded UTF-8 (`web_backend.py:515`). The two agree only for a page that was already UTF-8. Measured on a loopback page served as `charset=iso-8859-1`: fetched and frontmatter both `3b6596c0…`, `raw.html` on disk `afb0c4a6…`. A downstream caller that assumes the frontmatter hash verifies the stored artifact is wrong. Related: a page whose declared charset is wrong makes `fetched.text()` raise `UnicodeDecodeError` after extraction has otherwise succeeded, so capture can die having written nothing.

**Goal**: Either (a) `extract --provenance-json PATH` writes one object carrying source URL or origin path, the hash of the source as fetched, the path and hash of the stored raw artifact, the output path and its hash, and the backend used; or (b) a `--register` hook the caller supplies. Option (a) is the smaller change and serves any downstream registry. Separately, write `raw.html` as the fetched bytes so the frontmatter hash verifies it, or document the two as different numbers with different jobs.

**Downstream**: fusion-tea `scripts/source_registry.py` carries all four workarounds today — a flatten step, a staged copy of the local PDF, a loopback HTTP fixture, and two separately recorded hashes (`raw_sha256` for identity, `raw_artifact_sha256` for integrity).

---


### [ITEM-SYNC-F2] V11 model-side mirror check (candidate)

**Priority**: P2
**Effort**: ~0.5 day (check + fixture)
**Status**: Candidate
**Source**: UPSTREAM-FINDINGS Item 12 (F2); warning-reconciliation (Item 7)

**Idea**: A design-attribute binding whose `*_params` key no parameter group provides — the
model-side mirror of codegen's V11 (hard FAIL). Recorded by Item 7 as a candidate, not floor; codegen V11 is the backstop, so this is a nice-to-have early warning at L2/L6.

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
The remaining work is the sibling-scope collector. That collector is broader than the utility move and should land with dedicated positive and unrelated-namespace negative fixtures. codegen's duplicate-path error remains the backstop until then.

**Item 9 disposition (R-C8): KEEP FILED.** Item 5 landed SC-4 sanitizer-injectivity fail-fast in
codegen, so a two-names-one-identifier collision fails loudly at generation. PUSH-DOWN Item 2 removed the shared-sanitizer blocker; this row now tracks only the Level-6 pre-warn collector.

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
1. **`src/agentic_mbse/pm/operations.py:851`**: `impact_query()` — `affected_work_items` always returns empty list (needs model→work-item mapping)
2. **`src/agentic_mbse/pm/operations.py:1189`**: `supersede_insight()` — Raises `NotImplementedError` (needs full supersession flow per `workflows.md § 6.1`)

**Goal**: Implement both operations fully, or document them as intentional limitations.

---

### [EPIC-LCOE-001] LCOE Costing Patterns

**Priority**: P2
**Effort**: TBD (needs research sync with fusion-tea)
**Status**: External tracking only; current scope not reconciled in this refresh
**External Work**: `~/1cfe/fusion-tea`

**Problem**: The MBSE → sysml-codegen → teax-simkit pipeline needs nested cost model patterns validated and tooling upgraded.

**Tracking only** - active development happens in fusion-tea and sysml-codegen repos.

---

### [EPIC-VIZ-001] Visualization Tool Integration

**Priority**: P2
**Effort**: TBD
**Status**: External tracking only; current scope not reconciled in this refresh
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

### [ITEM-ARTIFACT-SCAFFOLD] Artifact Scaffolding via PM Script

**Priority**: P2
**Effort**: 1-2 days
**Status**: Draft spec; implementation not started
**Active**: `.project/active/artifact-scaffolding/`

**Problem**: 5 commands tell agents to manually fill in YAML frontmatter templates. Agents don't reliably follow these: they skip fields, use wrong formats, or invent non-standard fields, silently breaking PM automation.

**Goal**: Single `agentic-mbse pm create-artifact --type <type>` command that creates files with correctly populated frontmatter and scaffolded body sections. Commands change from "write this frontmatter" to "run this script, then fill in the body."

---

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
design override scope and supplied-value/codegen policy that intentionally remain in sysml-codegen. This should land only after that precedence contract is available as shared facts or a profile API.

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
for operators/functions belongs to the existing expression-profile checks. This row keeps the hierarchy trigger filed without duplicating or drifting expression support policy.

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
fixture and integration path. Filing avoids a mock-only validator that would not prove the user-facing profile behavior.

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
Those surfaces remain in sysml-codegen for PUSH-DOWN Item 3, so the profile rule is filed rather than implemented by importing codegen policy.

---

### [PUSH-DOWN-AGG-PROFILE-SUM-SHAPE] unsupported aggregation sum operand WARN

**Priority**: P2
**Effort**: ~0.5-1 day
**Status**: Filed - needs aggregation-profile integration over shared aggregation facts
**Source**: PUSH-DOWN Item 4 aggregation-profile close-out

**Rule**: Warn when a codegen-targeted aggregation expression uses `sum(...)` on an operand that
cannot decompose to a supported child feature chain or local reference, unless existing expression or hierarchy profile checks already cover the rejected operand shape.

**Fixture shape**: `:>> total = sum(module.cost)` is clean; an unsupported operand shape warns only
if not already covered elsewhere.

**Severity**: WARNING

**Rationale**: Aggregation-specific unsupported sum operand diagnostics need profile integration over
shared aggregation facts. PUSH-DOWN Item 4 preserves generation behavior and avoids adding a shallow rule that could duplicate existing expression diagnostics.

---

### [PUSH-DOWN-AGG-PROFILE-WRAPPER-SHAPE] aggregation wrapper compatibility WARN

**Priority**: P2
**Effort**: ~0.5-1 day
**Status**: Filed - profile-only warning must not change generation behavior
**Source**: PUSH-DOWN Item 4 aggregation-profile close-out

**Rule**: Preserve current generation behavior for wrapper unwrapping. Any profile-only warning for
unsupported wrappers must be explicitly separated from the behavior-preserving aggregation move.

**Fixture shape**: `sum(Evaluation(module.cost))`, `sum(collect(Evaluation(module.cost)))`,
`Evaluation(allocation.total)`, and current permissive `sum(filter(module.cost))` behavior are controls. A future stricter wrapper warning is filed rather than implemented in PUSH-DOWN Item 4.

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
expression support. PUSH-DOWN Item 4 keeps the generation path behavior-preserving and files this profile warning for a dedicated validation pass.

---

### [DOCS-DOTTED-PATH-BOUNDARY] Guide rows call dotted paths violations that Level 6 now accepts

**Priority**: P2
**Status**: Filed 2026-10-04 at `L6-EXPOSE-CONSISTENCY` close
**Source**: design-review C1; [design](../completed/20261004_l6-expose-consistency/design.md) D6 and Non-Goals; audit advisory

`project_templates/MODELING_GUIDE.md.template:57`, `docs/patterns/adr002-calculations.md:44`, `docs/patterns/common-mistakes.md:166`, and the one-hop advice at `docs/patterns/plant-idiom.md:406-413` call part-headed and multi-hop dotted paths violations, while V2, codegen, `plant-idiom.md:347`, and Level 6 after design D6 accept them; recorded direction ([AGENT], D6 ratified by orchestrator 2026-10-04) is to reconcile the docs with the predicate boundary (`src/agentic_mbse/validation/adr002.py:339`), and the audit records that the three-or-more-member sibling chain rests on a scratch probe, so this item also adds a retained regression test for it.

---

### [VALIDATE-CLI-FULL-REPORT] `agentic-mbse validate` shows only five issues per level, even with `--verbose`

**Priority**: P2
**Status**: Filed 2026-10-04 at `L6-EXPOSE-CONSISTENCY` close
**Source**: [consumer validation](../completed/20261004_l6-expose-consistency/consumer-validation.md)

`print_result` prints the first five issues and then "... and N more" without consulting `--verbose` (`src/agentic_mbse/validation/common.py:123`, `:140-143`); fusion-tea carried ~7,700 Level 6 issues unread for months and WI-049 built its own JSON before/after diff, so the proposed shape is a per-code summary plus a `--json` dump of structured issues.

---

### [L6-COMPLETENESS-PATH-FILTER] Completeness silently checks nothing on a model set with no `designs/` directory

**Priority**: P2
**Status**: Filed 2026-10-04 at `L6-EXPOSE-CONSISTENCY` close; pre-existing, found by the owner's fusion-tea probe
**Source**: [consumer validation](../completed/20261004_l6-expose-consistency/consumer-validation.md)

`check_design_attr_completeness` keeps its default `design_path_filter="designs"` (`src/agentic_mbse/validation/level6_architecture.py:478`, `:511`) and the CLI runner passes no filter (`src/agentic_mbse/validation/runner.py:50`), so a flat layout reports "Design attrs checked: 0" with no warning (fusion-tea `exploration/magnet_materials/input_models` and `exploration/exchanger_architecture/thermal_requirements/input_models`); proposed fix is a CLI flag for the filter or a warning when the filter matches no files.

---

### [L6-FORMULA-COMPLETENESS] Completeness rejects same-part FORMULA attributes that V2 accepts

**Priority**: P2
**Status**: Filed 2026-10-04 at `L6-EXPOSE-CONSISTENCY` close; pre-existing
**Source**: [design](../completed/20261004_l6-expose-consistency/design.md) Non-Goals; audit-F2 in the product-lens ledger

Out of scope for `L6-EXPOSE-CONSISTENCY`: completeness still reports `L6_DESIGN_ATTR_UNEXTRACTABLE` for an inline same-part formula such as `area = length * width`, which V2 accepts as FORMULA and `tests/test_l8_extractability.py:58` currently asserts; the recorded path is a fail-closed FORMULA predicate beside `is_expose_binding` (`src/agentic_mbse/validation/adr002.py:339`) added to completeness's guard, and fusion-tea `models/` has about 12 candidate attributes (e.g. `plasma_profile::edge_density`).

---

## P3 - Low Priority

### [ITEM-ITERATION-LOOP] Experiment Iteration Loop

**Priority**: P3
**Effort**: TBD (spec exists, needs design)
**Status**: Shelved
**Active**: `.project/active/iteration-loop/`

**Problem**: Running unattended iterative experiments (e.g., PDF extraction quality improvement) requires manual orchestration of fresh-context cycles, prompt templates, and result comparison.

**Goal**: Build an outer-loop + inner-loop shell script system with prompt templates and an IterationSpecAgent for running unattended iterative experiments with fresh context per cycle.

---

### [ITEM-ARCH-WALKTHROUGHS] Architecture Validation Walkthroughs

**Priority**: P3
**Effort**: 2-3 hours
**Status**: Deferred

**Problem**: EPIC-ARCH-003 D3.5 interactive validation walkthroughs were not completed. These require running each new command in a real target project and verifying end-to-end behavior.

**Goal**: Run all 14 commands + 5 new commands in fusion-tea or a test project to verify proper behavior.

---

### [L6-EXPOSE-CLEANUPS] V4/V2 duplicate reports, calc-usage binding spelling, and unused EXPOSE helpers

**Priority**: P3
**Status**: Filed 2026-10-04 at `L6-EXPOSE-CONSISTENCY` close
**Source**: [design](../completed/20261004_l6-expose-consistency/design.md) Non-Goals; [consumer validation](../completed/20261004_l6-expose-consistency/consumer-validation.md)

Three small items left out of `L6-EXPOSE-CONSISTENCY`: V4 still reports `.` on non-EXPOSE chains that V2 already flags (85 duplicates in fusion-tea `models/`); `in attribute x = source.y` inside a calc usage still gets V4 `.` because V4 does not skip calc-usage owners while V2 and completeness do; and `_get_calc_usage_names` (`src/agentic_mbse/validation/adr002.py:260`) and `_is_calc_output_reference` (`:292`) have no production callers, though the latter is still exercised by `tests/test_validation/test_v2_false_positive.py`.

---

### [PM-DASHBOARD-REPEATED-KEY] `status` silently shows only the last list when a `BACKLOG.md` frontmatter key repeats

**Priority**: P3
**Status**: Filed 2026-10-04 at `PM-MATRIX-ESCAPED-PIPE` close
**Source**: [audit](../completed/20261004_pm-registry-integrity/audit.md) advisory A2; product-lens audit block, smells ii and v

**Problem**: `parse_backlog` (`src/agentic_mbse/pm/parser.py:554`) loads the frontmatter with YAML's default last-wins rule, so when a key such as `standalone:` appears twice, `agentic-mbse status` shows only the second list and gives no warning. PM writes already refuse such a file (refusal R1), so no record is deleted, but the dashboard misstates what the file holds. Design D9 kept read-only consumers unchanged on purpose, and `test_default_keeps_last_wins` (`tests/test_pm_parser.py:123`) pins the silent default.

**Goal**: Read-only callers warn, not refuse, on a repeated frontmatter key, so `status` tells the user the file holds a list it is not showing.

---

### [PM-UPDATE-VALIDATION-COMMENT] `update-validation` refuses a valid SV row that holds an inline HTML comment

**Priority**: P3
**Status**: Filed 2026-10-04 at `PM-MATRIX-ESCAPED-PIPE` close
**Source**: [audit](../completed/20261004_pm-registry-integrity/audit.md) advisory A3; product-lens audit finding (c)

**Problem**: When an SV row the parser reads as valid carries an inline HTML comment, `update-validation` refuses it because the row writer rejects comment markers (`src/agentic_mbse/pm/operations.py:1460-1473`, pinned by `test_refuses_row_with_inline_comment_and_leaves_file_unchanged`). Before `PM-MATRIX-ESCAPED-PIPE`, such a row updated correctly, so this is the one new refusal on a call that used to succeed without damage. `claude/commands/audit-models.md:33` routes SV status changes only through this command, so the user must move the comment out by hand; the message says so and the file is untouched. fusion-tea is not exposed: all 134 parsed rows on its real matrix copy update cleanly.

**Goal**: Decide whether `update-validation` should carry an inline comment in a non-Status cell through unchanged instead of refusing the row, and implement that decision with a test.

---

### [PM-WRITE-BACKLOG-TYPED-FORM] `_write_backlog` keeps a `BacklogData` branch that only tests use

**Priority**: P3
**Status**: Filed 2026-10-04 at `PM-MATRIX-ESCAPED-PIPE` close
**Source**: [audit](../completed/20261004_pm-registry-integrity/audit.md) advisory A5

**Problem**: `_write_backlog` (`src/agentic_mbse/pm/operations.py:227`) still accepts a typed `BacklogData` (branch at `:235`), but every production caller passes the loaded frontmatter document. The branch exists so six base test call sites stayed unchanged under the item's additions-only test rule. As a result, the base `TestWriteBacklogRoundTrip` tests (`tests/test_pm_operations.py:238`) exercise only this test branch, not the production write path; production write-back is covered by the newer carry-forward tests and the fusion-tea round trip.

**Goal**: Move the typed form into a test helper and point `TestWriteBacklogRoundTrip` at the document write path, so `_write_backlog` has one production signature.

---

### [PM-R7-MESSAGE] `update-validation`'s refusal blames pipes or comments when Status is not the ninth column

**Priority**: P3
**Status**: Filed 2026-10-04 at `PM-MATRIX-ESCAPED-PIPE` close
**Source**: [audit](../completed/20261004_pm-registry-integrity/audit.md) advisory A6; product-lens audit smell iv

**Problem**: `update-validation` writes the ninth cell of the matched row and refuses (refusal R7) when that cell is not the parsed Status (`src/agentic_mbse/pm/operations.py:1449`). On a matrix with a custom header, where Status sits in another column, the refusal is correct but its message (`:1453-1455`) tells the user to escape pipes or move an HTML comment, which is not the cause.

**Goal**: When the row parses but Status is not its ninth cell, the refusal says that Status must be the ninth column.

---

### [PM-APPROVE-RESEARCH-MOVE-SAFETY] `approve-research` can duplicate insights after a failed move, silently overwrites a same-name approved file, and trusts symlinks inside `pending/`

**Priority**: P3
**Status**: Filed 2026-10-05 at `PM-APPROVE-RESEARCH-EMPTY-INSIGHTS` spec review; case (c) added at its audit the same day
**Source**: [spec review](../active/research-approval-empty-insights/spec-review.md) finding L3-4 (a) and (b); [audit](../active/research-approval-empty-insights/audit.md) A2 and A5

**Problem**: Three gaps in how `approve_research` (`src/agentic_mbse/pm/operations.py:910` at `c37ff53`) moves the document. (a) and (b) fall short of the original contract, "File move and KNOWLEDGE.md appends are all-or-nothing" (FR-9, [PM operations spec](../completed/20260203_d4.4-operations/spec.md):181) and of the shipped claim that PM mutations "succeed fully or not at all" (`claude/skills/toolkit-awareness/SKILL.md:85`).

- **(a) Failed move after appends.** The operation appends insights to `knowledge/KNOWLEDGE.md` before it moves the file (`operations.py:983-991` at `c37ff53`). If the move raises, the new DIs stay and the research stays pending, so a retry mints duplicates. Found by reading the code; affects only non-empty approvals.
- **(b) Silent overwrite on a name collision.** If `knowledge/research/approved/` already holds a file with the same name, `shutil.move` replaces it without a warning. A probe at `c37ff53` confirmed the earlier approved file's content was replaced. Affects empty and non-empty approvals. Zero-insight approvals make it more likely to come up, since approval no longer needs an insight (audit A5, from the audit-stage product-lens finding audit-F1).
- **(c) Symlinks inside `pending/` are trusted.** A symlinked directory inside `pending/` lets a call move a file that lives outside `pending/` into `approved/`. Audit A2's probe: with `pending/sub` linked to `<root>/outside/`, `approve-research pending/sub/secret.md` with `[]` succeeds and moves `outside/secret.md` into `approved/`, with nothing written to show it. At `c37ff53` the same move needed a non-empty list and left a visible DI. It follows from that item's design choice not to resolve symlinks (D5), and setting it up needs write access to `pending/`. The same audit observed one tightening: a symlink to a directory given as the document, which `c37ff53` approved with one insight (moving the link and minting a DI), is now refused as `Not a regular file`.

`PM-APPROVE-RESEARCH-EMPTY-INSIGHTS` causes none of the three, but makes (b) and (c) cheaper to reach. It brought only the directory-as-file case (spec review L3-4 (c)) and `..` escapes from `pending/` (its design D5) into its own scope.

**Goal**: Decide how approval handles a failed move after appends, a name collision in `approved/`, and symlinks inside `pending/`, so that approval neither duplicates insights, destroys an approved document, nor moves a file from outside `pending/`, and implement that decision with tests.

---

## Disposition Records

### [ITEM-SYNC-F1] SysIDE self-named-recursion vendor note (evaluation-time finding)

**Priority**: P2
**Effort**: 0.5 day (write the reproducer + report)
**Status**: Vendor filing declined; retained finding at `.project/research/20260706_syside-self-named-recursion-vendor-note.md`
**Source**: UPSTREAM-FINDINGS Item 12 (F1); Item 8 WI-014 toy

**Finding**: A self-named binding (`in P = P` resolving to the calc's own parameter) trips
SysIDE into recursion at **expression-evaluation time, not extraction time** — extraction is finite/degenerate (Item-8 probe, `timeout 150`, exit 0). The draft note records the distinction. Out of scope for Item 12: writing the full vendor report or contacting Sensmetry. This item is to produce a minimal reproducer and, if warranted, a report.

**Item 9 disposition (R-VENDOR): DECLINE the Sensmetry filing.** The recursion is
evaluation-time syside behavior; sysml-codegen extraction is finite/degenerate (Item-8 probe, `timeout 150`, exit 0), so no codegen path is affected. This note stays as the durable record of the finding, but the item is not escalated to a vendor report/contact. Revisit only if a supported model drives syside into extraction-time recursion.

---

## Completed

### [ITEM-SYNC-C7] attribute-`:>>`-with-expression WARN — ✅ BUILT (PIPELINE-TRUTH Item 9)

**Priority**: P2
**Effort**: ~0.5 day (check + fixture)
**Status**: ✅ Done — built in PIPELINE-TRUTH Item 9 (`pipeline-truth-item4`, commit `fa3b706`).
`check_attr_redef_expression_dropped` (level6_architecture.py) + `L6_ATTR_REDEF_EXPR_DROPPED` fires on an AttributeUsage `:>>` with a non-literal RHS; stays silent on the bare `:>>` forms (ReferenceUsage) and the `attribute :>>`-literal form. Fixtures `tests/fixtures/item9/attr_redef_expr` (fires) + `attr_redef_literal` (silent). A live syside probe confirmed the trigger boundary is cleanly distinguishable (AttributeUsage vs ReferenceUsage) before the check landed — the C6 defect-class risk that deferred it is retired.
**Source**: UPSTREAM-FINDINGS Item 12 (C7); cross-part-wiring

**Idea**: WARN when `attribute :>> attr = <expression>` carries an expression RHS — this
AttributeUsage-redefinition form is silently dropped at extraction (`hierarchy_resolver.py` `_extract_single_redefinition` scans only ReferenceUsage). Doc D5 (semantic-operators.md) already teaches the bare-`:>>` form as the fix.

**Why filed, not built in Item 12**: the correct trigger boundary is subtle — must fire on
an *AttributeUsage* redefinition with an *expression* RHS, but NOT on the supported bare-`:>>` (ReferenceUsage) value form nor on a literal-valued redefinition. A rushed check risks the C6 defect class (flagging a shape codegen accepts). Build it with its own negative fixture AND a negative-of-the-negative (bare-`:>>` literal must not fire).

---

### [ITEM-SYNC-F6] L6 derived-expr-references-design-attrs flags supported FORMULA shapes ✅

**Found**: 2026-07-06, orchestrator cross-repo sweep during the UPSTREAM-FINDINGS Item 12 audit.
**Fixed**: 2026-07-06, on `upstream-findings-sync`.
**Symptom**: `run_all_checks` on sysml-codegen's `quoted_owner_formula` fixture fails L6 with
"Derived expression references design attributes ['revenue', ...]" — but that shape (a FORMULA computed attribute reading design attributes) is first-class in sysml-codegen (Item 5 landed the quoted-owner FORMULA wire; the fixture generates and resolves end-to-end).
**Class**: third L6 false-positive family, sibling to the two C6 fixed (calc-def-internal derived
expr; quoted-name EQN). Not in the Item 12 impact list — the fixture was never run through agentic-mbse validation in any item's records.
**Fix**: `check_static_expressions` (`adr002.py`) now exempts a design computed attribute whose
feature refs all resolve to same-part owned siblings (a codegen FORMULA, verified against `computed_attribute_extractor.py::_classify_attribute_expression`). A reference to a calc output in a foreign namespace (`calc.out * 0.95`), a self-reference (REQ-CA-07), or a dotted path (FeatureChainExpression) still fires. Fixture `tests/fixtures/item12/formula_computed/` carries both directions; three pre-Item-5 tests in `test_sysml/test_adr002.py` that asserted the old blanket rule were updated to the relaxed contract.

### FORMULA teaching reconciliation

Implemented in `9cf6b3c`; the retained [spec](../active/formula-teaching-reconciliation/spec.md) records the surgical teaching change. Independent recertification was not performed by this tracking refresh.

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
| L6-EXPOSE-CONSISTENCY: L6 EXPOSE Validation Consistency | 2026-10-04 | <1 day | V4 and completeness share V2's EXPOSE predicate (`3f442ce`); fusion-tea `models/` Level 6 issues 7,734 → 408, none added. Archived to `completed/20261004_l6-expose-consistency/` |
| PM-MATRIX-ESCAPED-PIPE: Escaped Pipes and Registry ID Integrity | 2026-10-04 | <1 day (filed 2026-08-21) | GFM `\|` escape honoured; all seven allocators reserve every ID the registry file names; backlog writes keep unparsed records; nine refusals before any write. Certified with follow-ups. Archived to `completed/20261004_pm-registry-integrity/`. Downstream: fusion-tea fixes its `SV-034` cells by hand |
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
