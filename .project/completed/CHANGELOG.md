# Changelog

Historical record of completed work.

---

## [2026-10-09] - Native Skill Distribution

**Type**: Item (`WRAP-SPLIT` Item 1, adopts `NATIVE-DISTRIBUTION-RECONCILIATION`; branch `nsd-integration` in worktree `/home/reid/1cfe/agentic-mbse-nsd`, source last changed at `03d1510`, not yet merged)
**Duration**: 5 days (spec created 2026-10-04 09:28 PDT; closed 2026-10-09)

### Summary

agentic-mbse now has one installer source. Before this item, `main` held the current workflow text in the old shape (`claude/` plus hand-kept `MBSE_*` lists, Claude Code only), while the native branch held the new `skills/` + `agents/` + `adapters/` installer for Claude Code and Codex with text 58 commits behind. fusion-tea ran both at once, its Claude side as 31 absolute links into this checkout's `claude/`. Now one tree (`skills/`, `agents/`, `adapters/`, `hooks/`, `project_templates/`) carries `main`'s text and installs the same way for both clients; `claude/` and the `MBSE_*` lists are gone, so a skill registers by adding its folder. A script regenerated the shipped text from `main` and checks it byte for byte: 55 files, 0 mismatches, apart from the frontmatter, the shared preface and 17 reviewed runtime adaptations. Re-init over fusion-tea's old links replaces all 31 without a prompt and reports each one. Rehearsed on copies of fusion-tea in both modes: nothing target-owned lost, and `MODELING_PROCESS.md` byte-identical with both MR-7 lines. Independently audited (Needs Work on B1, then Certify), and re-checked after Phase 9: suite 2,186 passed, ruff and mypy at `main`'s parity. Not checked: a live modeling session in either client after install; discovery was probed, behaviour was not.

**Promise the product now makes.** [OWNER-VERBATIM] at Align, 2026-10-09: "can we just move all of the claude commands over to skill format, and install them in the same way? how do we simplify this". `agentic-mbse init` installs every shipped skill from one tree for Claude Code and Codex, in plain and `--dev` modes, and adding `skills/<name>/SKILL.md` is the whole registration: install, listing and tests derive from the tree.

**Decision: recognising the old installer's links.** [AGENT] (ratified by owner at Align, 2026-10-09: remove `claude/` with no shim, and the installer adopts the old links; [design](20261009_native-skill-distribution/design.md)) A `.claude/{commands,skills,agents,hooks}/<name>` link is replaced without a prompt only when its raw text is absolute, has no empty, `.` or `..` segment, ends in `claude/<location>/<name>`, and its root is an agentic-mbse source checkout. The text is never normalized and the referent is never read, so a dangling link is adopted and a link into any other tree keeps the prompt-or-preserve rule. Rejected: normalizing the text, which can name a different tree than the link resolves to.

**Decision: `--dev` links skill folders, not files.** [OWNER] 2026-10-09 chose to fix rather than defer audit B1; the shape is [AGENT] from the orchestrator's spike ([design D14](20261009_native-skill-distribution/design.md), [spike](20261009_native-skill-distribution/evidence/spike-dev-codex-links.md)). Under `--dev` each `.agents/skills/<n>` is one absolute folder link into the checkout; Claude's `.claude/skills/<n>` alias still links to it. A real folder holding files the installer does not own gets a plain copy instead, with one line saying what happened. Rejected: per-file links (the native branch's shape), which Codex skips.

**Behavior found.**
- Codex 0.160.0 never lists a skill whose `SKILL.md` is a file link (absolute or relative, inside or outside the project) and reports no error; it lists a skill whose folder is a link, wherever the link points and through chains of folder links. Claude Code 2.1.296 lists both shapes ([spike](20261009_native-skill-distribution/evidence/spike-dev-codex-links.md)).
- `codex app-server --stdio` answers `skills/list` with no login and no model turn, and `claude -p` answers the stream-json `initialize` control request the same way; `completed/20261009_native-skills/discovery_probe.py` uses both to probe discovery.
- The hatchling wheel build omits `docs/syside/python/v0.8.4/syside/` (340 files) with no matching ignore rule; the cause was not found (`WHEEL-DOCS-SYSIDE-GAP`).

**Downstream (fusion-tea, the owner's).** After the merge: move the pin, apply the `AGENTS.md` patch that carries fusion-tea's two target-owned passages, re-init (plain `init` recommended; `--dev` would commit machine-specific links), answer `s` for `MODELING_PROCESS.md` ([runbook](20261009_native-skill-distribution/evidence/fusion-tea-runbook.md)). This checkout then runs `uv run agentic-mbse install-commands --assistant claude`.

### Deliverables

- `src/agentic_mbse/cli/installation.py` (tree-derived bundles and kinds, `is_source_checkout`, legacy-link adoption in `permit`, `link_directory`, `install_dev_bundle`, `expose_to_claude`, report-once) and `src/agentic_mbse/cli/__init__.py` (`MBSE_*` lists and dead names removed, `--list` by kind, Adopted report); `pyproject.toml` wheel includes.
- The shipped tree: `skills/` (25 bundles), `agents/`, `adapters/` (author-continuity rule), `hooks/ruff-format.sh` (moved), `project_templates/`; `claude/` removed; this repo's tracked `.claude/` copies untracked.
- Tests: `tests/test_shipped_text.py` and `tests/helpers/shipped.py` (new); `tests/test_installation.py`, `tests/test_cli.py`, `tests/test_packaged_guidance_contract.py` updated to tree-derived properties.
- Docs: `CLAUDE.md`, `README.md`, `scripts/README.md`.
- `.project/completed/20261009_native-skill-distribution/`: `spec.md`, `spec-review.md`, `design.md`, `design-review.md`, `plan.md` (9 phases), `audit.md`, `product-lens.md`, `briefs/` (00–15), `evidence/` (`reconcile.py`, `adaptations.yaml`, dispositions, check and probe results, rehearsal and raw outputs, `fusion-tea-target-owned.patch`, `fusion-tea-runbook.md`, `lint-parity.md`, the `--dev` link spike).
- `.project/completed/20261009_native-skills/`: the native branch's item (plan, A–K remediation, validation, `discovery_probe.py`), re-certified by this item's audit.
- `.project/active/wrap-split-migration-ledger.md` (created; Item 1 rows; Item 2 owns it).
- Backlog follow-ups (P3): `NATIVE-DISCOVERY-LIVE-TEST`, `WHEEL-DOCS-SYSIDE-GAP`, `INSTALL-DEV-GITIGNORE-STALE`, `INSTALL-REPORT-UNCHANGED-UPDATED`, `REPO-INIT-SCAFFOLD-STALE`.

---

## [2026-10-06] - Approve Research with No New Insights

**Type**: Item (standalone `PM-APPROVE-RESEARCH-EMPTY-INSIGHTS`, filed 2026-08-25; branch `research-approval-empty-insights`, source last changed at `8e8d26a`, not yet merged)
**Duration**: 2 days (spec created 2026-10-04 09:28 PDT; closed 2026-10-06)

### Summary

Research approved with no new domain insight now goes through the supported operation. Before this item, `approve-research` refused an explicit empty insight list with `No insights provided`, so a source-registration round, a bounded negative result, or a confirmation of existing knowledge left its document in `knowledge/research/pending/` and operators moved it by hand. Now `--insights '[]'` approves the document, moves it to `approved/`, and never reads or writes `KNOWLEDGE.md`; the result says `No insights created` and lists only the approved path. Omitting `--insights` and `--insights null` stay usage errors, and in Python `None` or a non-list returns a failure that names `[]`. The shipped `/research` approval step and the toolkit-awareness row tell agents to make the `[]` call when no insight is accepted, whether every candidate was skipped or none was proposed. Non-empty approvals are unchanged from the base for ordinary inputs. Independently certified, then re-checked after audit fixes: all seven spec criteria met, full suite 2,079 passed, and ruff and mypy finding sets identical to the base. Not checked: an agent following the new `/research` text in a live session.

**Promise the product now makes.** [AGENT] (orchestrator, 2026-10-05; item spec criteria are `[INHERITED]` from the backlog or `[INFERRED]`) `approve-research` accepts an explicit empty list as "report approved, no insights." Emptiness must be stated: an omitted list is a caller error on both the CLI and the Python surface.

**Decision: how the pending-path check works.** [AGENT] (orchestrator, 2026-10-05; [design D5](20261006_research-approval-empty-insights/design.md)) Removing the empty-list refusal would have let the `[]` call move the whole `pending/` directory, or reach `KNOWLEDGE.md` through a `..` path, so the path checks were tightened in this item. The project root is used exactly as the caller gave it. `..` is collapsed only in the part of the path below `pending/`, and the rebuilt path serves the exists check, the regular-file check, and the move. A path that is not a regular file, or whose `..` climbs above `pending/` (even if it comes back, such as `pending/../pending/doc.md`), is refused before anything is written. Rejected: normalizing the root, because it can name a different project than the OS resolves; and `Path.resolve()`, because it would start refusing symlinked pending documents.

**Behavior found.** `os.path.normpath` collapses a symlink followed by `..` as text. For `A/link/..` where `link` points to `X/Y`, it returns `A` while the OS resolves `X`. A containment check on normalized paths beside file operations on raw paths can therefore act on two different trees ([audit](20261006_research-approval-empty-insights/audit.md) A1, probe and fix).

**Downstream (fusion-tea, not in this item's scope).** After merge, fusion-tea moves its agentic-mbse pin and re-runs init to receive the changed `/research` command and toolkit-awareness skill.

### Deliverables

- `src/agentic_mbse/pm/operations.py` (`approve_research`: zero-insight path, list type check, regular-file and below-`pending/` refusals, derived result; helper `_path_below`) and `src/agentic_mbse/cli/pm_cli.py` (two help strings).
- `claude/commands/research.md` (approval step) and `claude/skills/toolkit-awareness/SKILL.md` (`approve-research` row).
- `tests/test_pm_operations.py` and `tests/test_pm_cli.py`: 23 test cases added, including three CLI tests through the real parser.
- `.project/completed/20261006_research-approval-empty-insights/`: `spec.md`, `spec-review.md`, `design.md`, `plan.md`, `audit.md`, `product-lens.md`, `briefs/`.
- Backlog follow-up (P3): `PM-APPROVE-RESEARCH-MOVE-SAFETY` (failed move after append, same-name overwrite in `approved/`, symlinked directory inside `pending/`).

---

## [2026-10-04] - Escaped Pipes and Registry ID Integrity

**Type**: Item (standalone `PM-MATRIX-ESCAPED-PIPE`, filed 2026-08-21; branch `pm-registry-integrity`, source last changed at `c3f3517`, not yet merged)
**Duration**: <1 day (spec created 2026-10-04 09:28 PDT; closed 2026-10-04)

### Summary

PM reads and writes no longer lose registry records or mint an ID twice. Before this item, the table splitter treated GFM's `\|` escape as a cell boundary (fusion-tea's valid `SV-035` vanished from the parse), `update-validation` wrote into the wrong column, the backlog writer deleted every work item it could not parse, and all seven allocators numbered only parsed records. Now one splitter and escape pair serves every table reader and writer; every allocator (SV, DI, PR, AD, WI, G, AQ) mints above every same-prefix ID the registry file names outside HTML comments; backlog writes edit the loaded frontmatter and carry rejected records forward; and nine refusals (R1 to R9) stop a write before any file changes. A post-audit fix makes table inserts skip commented example tables. Independently certified with follow-ups: 25 source mutations caught, full suite 2,056 passed, and E3/E4 pass on copies of fusion-tea's files (`SV-035` parses; next IDs `SV-136` and `DI-015`). Users will see new stderr reservation warnings and clean refusals where calls used to corrupt or crash; the one new refusal on a previously harmless call is `update-validation` on a row with an inline HTML comment (filed as `PM-UPDATE-VALIDATION-COMMENT`).

**Contract change.** The PM operations promise "IDs are never reused" ([2026-02 operations spec](20260203_d4.4-operations/spec.md), line 73) was never implemented. Per this item's spec Decisions ([AGENT], orchestrator 2026-10-04), it is narrowed to IDs present in the registry file, with no persistent high-water mark: a deleted ID can be minted again once the file no longer names it, and archived IDs are protected only while the file names them.

**Downstream (fusion-tea, not in this item's scope).** After merge, fusion-tea's agentic-mbse pin must move. Its `SV-034` row still holds two raw pipes and stays warned until they are escaped by hand.

### Deliverables

- `src/agentic_mbse/pm/parser.py` (GFM cell splitter, unique-key frontmatter loader, unindented closing delimiter) and `src/agentic_mbse/pm/operations.py` (escape pair, whole-file ID discovery, document write-back, refusals R1 to R9, comment-aware table insert).
- `tests/test_pm_parser.py` and `tests/test_pm_operations.py`: 124 tests added, no base test line removed.
- `.project/completed/20261004_pm-registry-integrity/`: `spec.md`, `spec-review.md`, `spec-review-2.md`, `design.md`, `design-review.md`, `plan.md`, `acceptance-evidence.md`, `audit.md`, `product-lens.md`, `briefs/`.
- Backlog follow-ups (P3): `PM-DASHBOARD-REPEATED-KEY`, `PM-UPDATE-VALIDATION-COMMENT`, `PM-WRITE-BACKLOG-TYPED-FORM`, `PM-R7-MESSAGE`.

---

## [2026-10-04] - L6 EXPOSE Validation Consistency

**Type**: Item (standalone `L6-EXPOSE-CONSISTENCY`; implementation `3f442ce` on `harness-right-size`)
**Duration**: <1 day (spec created 2026-10-04 09:28; closed 2026-10-04)

### Summary

Level 6 no longer rejects the documented EXPOSE pattern. The supported-operator check (V4) and design-attribute completeness now use the same EXPOSE predicate as the static-expression check (V2), so a design attribute bound directly to a calculation output gets neither `V4_UNSUPPORTED_OPERATOR` for `.` nor `L6_DESIGN_ATTR_UNEXTRACTABLE`. Arithmetic over a calc output keeps all three diagnostics, and 13 pinned controls are unchanged. Independently certified. On fusion-tea `models/`, Level 6 issues fell from 7,734 to 408 with none added, and an owner-run probe through fusion-tea's CLI confirmed all three spec criteria in situ. Per design D6 ([AGENT], ratified by orchestrator), part-headed and multi-hop sibling chains also pass, which conflicts with three guide rows; that reconciliation and five other follow-ups are filed in the backlog.

### Deliverables

- `src/agentic_mbse/validation/adr002.py` (shared `is_expose_binding`, V4 guard) and `src/agentic_mbse/validation/level6_architecture.py` (completeness guard).
- `tests/test_validation/test_l6_expose_consistency.py` and `tests/fixtures/l6_expose_consistency/{shapes,controls}/`.
- `.project/completed/20261004_l6-expose-consistency/`: `spec.md`, `design.md`, `design-review.md`, `plan.md`, `audit.md`, `product-lens.md`, `consumer-validation.md`, `briefs/`.
- Backlog follow-ups: `DOCS-DOTTED-PATH-BOUNDARY`, `VALIDATE-CLI-FULL-REPORT`, `L6-COMPLETENESS-PATH-FILTER`, `L6-FORMULA-COMPLETENESS`, `L6-EXPOSE-CLEANUPS`, `L6-LIBRARY-ALIAS-SOURCE`.

---

## [2026-09-14] - Modeling Harness Right-Sizing

**Type**: Change (implemented on `harness-right-size`; tracking backfilled 2026-10-04)

### Summary

Commit `ce80472` replaces unconditional process/review requirements with concrete risk triggers, evidence reuse, and bounded review scope. The implementation record reports 91 command/installer checks passing and a bounded independent review with no material defects in five core process files. Fusion TEA's September 15 harness revision `94cf6973f` carries consumer adaptations. Full native installer certification and source-distribution synchronization remain separate work; no measured token-savings claim is made.

### Deliverables

- `.project/active/harness-right-size/requirements.md` and `review.md`; evidence retained at original paths.
- Revised shipped modeling commands, canonical process, and epic guidance.

---

## [2026-09-13] - Modeling Workflow Repairs and Focused Trials

**Type**: Change (implemented on `harness-simplify`, inherited by `harness-right-size`; tracking backfilled 2026-10-04)

### Summary

Commit `d20069b` simplifies modeling workflows and repairs source discovery, installed pattern navigation, durable-record ownership, and missing-audit closure. The recorded 91-test selection and three fresh-context trials pass within their scope. Installation `ed1ec5cd2` is in Fusion TEA's history, followed by successful native consumer work. Two reproduced L6 EXPOSE false positives are a separate validator defect; native-source synchronization remains a distribution gap.

### Deliverables

- `.project/active/modeling-workflow-outcomes/{draft,plan}.md` and referenced Fusion TEA trial evidence.

---

## [2026-09-12] - Native Skill Installation Research Capture

**Type**: Change (research capture; tracking backfilled 2026-10-04)

### Summary

Commit `35fa2b6`, titled “Ported to codex,” captures native Claude/Codex discovery and installer research in this checkout. Production migration lives in sibling branch `native-claude-codex-skills` (`955295b` with uncommitted remediation). Its accepted audit repairs are implemented and tested in the recorded evidence, but independent re-review and distribution reconciliation remain pending. The commit title alone is not evidence that native installation is shipped from this branch.

### Deliverables

- `.project/research/20260907-162310_native-claude-codex-skills.md` and `.project/active/spike-native-skill-install/` probes.

---

## [2026-08-20] - Parser Evidence and Validation Integration (PR #13)

**Type**: Integration (tracking backfilled 2026-10-04)

### Summary

Local `main` merged `stop-parser-evidence-r2` as `88e2489`. The integrated work tightens expression/declaration and invocation evidence, centralizes unit annotations, and fixes return-parameter membership. Fusion TEA's companion pin `4433888` contains this work. This entry records integration from git history; this tracking refresh did not rerun its full suite.

---

## [2026-08-14] - Exact Identity and Identified Constraint Route (PR #12)

**Type**: Integration (tracking backfilled 2026-10-04)

### Summary

Commit `1decd95` integrates ELABORATE-FIRST identity evidence and identified constraint extraction/profile evaluation, migrates validation consumers, and retires the neutral live route. This supersedes transitional July constraint-route descriptions. Historical certification and recovery details remain in git and the companion codegen records.

---

## [2026-07-20] - Constraint Lifecycle Integration (PR #11)

**Type**: Integration (tracking backfilled 2026-10-04)

### Summary

Companion `f4ebdce`, codegen `936315c`, and TEAx `fa0e06a` integrate the constraint lifecycle, including certified remediation, profile semantics/default-deny fixes, authoring docs, and external failure normalization. The later codegen record reports paired post-merge smoke of 3,115 passed / 47 skipped and a 41/41 public lifecycle proof. These records discharge the old compatibility, external F1, and pre-PR blockers; current ancestry checks confirm delivery. Fresh October 4 focused TEAx checks passed 15/15.

### Deliverables

- Historical local evidence remains in `.project/active/{constraint-exec-remediation,constraint-wave-profile-semantics,gap-profile-totalization,constraint-exec-docs}/`.
- sysml-codegen `.project/CURRENT_WORK.md:904` records the composed merge and paired smoke; TEAx `.project/active/gap-close-f1-normalization/audit.md` records its independent certification.

---

## [2026-07-18] - Orchestrate Modeling

**Type**: Item (standalone)
**Duration**: 1 day (created 2026-07-17; archived 2026-07-18)

### Summary

Added a thin, judgment-led modeling orchestrator that carries either one Standard work item or an Epic through the existing modeling stages after one owner alignment. The shipped workflow now has one canonical flow map, durable pre-stage alignment, independent item and Epic audits, bounded repair, and a supported deterministic path for registering new Epics.

### Deliverables

- `.project/completed/20260718_orchestrate-modeling/` — spec, reviews, design, and implementation plan.
- `claude/commands/orchestrate-modeling.md` — Task-only orchestration command.
- `project_templates/MODELING_PROCESS.md.template` and `EPIC_GUIDE.md.template` — canonical Standard and Epic flow documentation.
- `agentic-mbse pm add-epic` — validated operation and CLI registration.
- Command contract, PM operation, CLI dispatch, installation, hash, and manifest-parity tests.

### Lessons Learned

- A newly registered Epic must start in `draft` so declared and derived PM state agree.
- Prompt safety contracts are usefully pinned with kept structural tests, while judgment-led routing still needs tabletop scenarios and dogfooding.
- Closed without an independent audit by owner decision; focused and normal regression suites passed.

---

## [2026-07-13] - [CONSTRAINT-EXEC] Items 1-3 (agentic-mbse side)

**Type**: Epic (3 items in this repo; canonical epic archived in sysml-codegen)
**Duration**: ~1 day (created 2026-07-12; archived 2026-07-13)

### Summary
The three agentic-mbse items of the CONSTRAINT-EXEC epic: neutral `ConstraintFacts` production schemas + extraction (Item 1), the production `ExpressionIR` tree with extraction and serialization (Item 2), and the executable profile's eligibility gates + named diagnostics (Item 3). All certified; suite at close 1401 passed / 1 skipped.

### Deliverables
- `.project/completed/20260713_constraint-facts/`, `20260713_expression-ir/`, `20260713_executable-profile/` (spec/design/plan/audit + briefs each).
- Epic close-out and independent findings audit: sysml-codegen `.project/completed/20260713_epic_constraint_execution*.md`.

---

## [2026-07-10] - Shared SysML Primitives (PR #10)

**Type**: Integration (tracking backfilled 2026-10-04)

### Summary

Merge `6a69e13` brings shared expression reconstruction, qualified names, hierarchy primitives, and aggregation decomposition into agentic-mbse, including independent-audit remediation `d340c8e`. These shared utilities underpin later codegen integration; this record does not claim the separately filed profile-warning candidates were implemented.

---

## [2026-07-06] - Validation and Teaching Alignment (PRs #7 and #8)

**Type**: Integration (tracking backfilled 2026-10-04)

### Summary

Merges `f3b19ba` and `d582940` integrate upstream validation/teaching corrections, subtype-aware adapter enumeration, and the C7 attribute-redefinition warning. FORMULA teaching reconciliation `9cf6b3c` shipped with these changes. C8 remains filed and the vendor-report escalation was declined; C4 plain-subtype documentation/test work remains a separate draft.

---

## [2026-07-05] - Web Source Capture + arXiv Extraction Pipeline

**Type**: Items (5, standalone — shipped together in PR #6, `webfetch-tools` → `main`)
**Duration**: episodic, 2026-03-28 to 2026-07-05

### Summary

Built out `agentic-mbse extract` for the web: URL-to-markdown capture with injection-safe sanitization, consistent provenance across all pipelines, and an arXiv path that produces clean, current papers. Five standalone work items that landed as one branch.

**Web Source Capture** (`web-source-capture`): `extract <url>` fetches, sanitizes, and extracts web content to markdown using the same CLI, output format, and type system as PDF/DOCX. trafilatura backend with Pandoc fallback; an HTML sanitization pre-pass strips CSS-hidden content (the indirect-prompt-injection vector); batch mode and `--save-source`. Optional dependency extra to keep the base install light.

**Extraction Provenance** (`extraction-provenance`): universal YAML frontmatter (source, backend, content hash) across the three extraction pipelines, which previously recorded provenance inconsistently; `--no-frontmatter` and `--save-source`.

**Hash Consolidation** (`hash-consolidation`): replaced three divergent hash implementations (MD5 vs SHA256, differing output formats) with a single SHA256 `compute_source_hash` in `base.py`.

**Web Extraction Quality** (`web-extraction-quality`): arXiv HTML URLs route through the proven Pandoc pipeline instead of trafilatura, preserving tables, equations, and scientific notation; arXiv figures are downloaded locally with markdown refs rewritten, and image-download failures surface as `ExtractionResult` warnings. Remaining scope (non-arXiv scientific HTML quality, fusion-tea source re-extraction) was dropped from this item at close.

**arXiv Latest-Version** (`arxiv-latest-version`): a version-pinned arXiv id/URL now resolves to the newest version arXiv serves (the bare `/html/{id}` URL) instead of fetching a stale v1, across both the web and PDF-derived paths; the served version is recorded in frontmatter `source`, with a fallback to the requested version if the bare fetch fails. **Certified** (`audit.md`) — all four spec criteria met, verified live (`1706.03762v1` → recorded `v7`).

### Deliverables

- `web-source-capture`: spec, design, plan
- `extraction-provenance`: spec, design, plan
- `hash-consolidation`: spec, plan
- `web-extraction-quality`: spec, design, plan (+ arXiv-images sub-spec/design/plan)
- `arxiv-latest-version`: spec, design, plan, **audit**

### Lessons Learned

[TODO: Add lessons learned]

---

## [2026-03-06] - EPIC-PDFV4-002 Items 1-4: Quality & Features

**Type**: Items (from EPIC-PDFV4-002)
**Duration**: ~3 days (2026-02-27 to 2026-03-01)

### Summary

Four items completing the quality regression fixes and new features for the v4 extraction pipeline. Items 5 (OCR integration) and 6 (summarize hallucination fix) remain in the backlog.

**Item 1 — Quality Regressions** (`v4-output-quality-regressions`): Three phases — equation-fragment detection in quality gate, GMFT cross-reference routing (boost severity when GMFT finds tables pymupdf missed), postprocess cleanup (strip running headers, page numbers, ligatures). Phase 4 (image extraction) superseded by Item 2.

**Item 2 — Unified Image Output** (`unified-image-output`): `ImageCollector`/`ImageEntry` pattern for figures and table crops. Three phases: pymupdf4llm `write_images=True`, table crop persistence via collector, CLI wiring with `output_dir/images/` creation.

**Item 3 — Pipeline Profiling** (`pipeline-profiling`): `PipelineProfile` dataclass with 11-step timing, `--profile` CLI flag, `profile.json` per-document output, 5-group summary table to stderr.

**Item 4 — Equation Region Detection** (`equation-region-detection`): `detect_equations()` via `docling-ibm-models` `LayoutPredictor` with lazy import, NMS, crop saving, `--no-equations` CLI flag.

**Bug Fix — Subprocess TTY** (`subprocess-tty-fix`): Added `start_new_session=True` to Claude CLI subprocess calls fixing terminal blanking from Claude Code's Bash tool.

### Research Closed

**Docling Deep-Dive** (`docling-deep-dive`): Phases 0-2 complete (API evaluation, experiment harness, OCR comparison). Phases 3-4 deemed unnecessary — findings sufficient for OCR integration item.

**Pandoc Deep-Dive** (`pandoc-deep-dive`): Phases 1-4 complete (HTML acquisition, 15 experiments, best config found). Findings already integrated into v4 arXiv shortcut.

---

## [2026-03-01] - Validation Stack Restructuring (8 → 6 Levels)

**Type**: Item
**Duration**: 3 days (2026-02-27 to 2026-03-01)

### Summary

Restructured the validation pyramid from 8 levels to 6 by deleting stubs (L5 Semantic, L7 Architecture), merging application-specific checks into L6, and renumbering L6 Traceability to L5. Aligns implementation with the published blog post's 6-level narrative while preserving all validation logic. Post-implementation audit found and fixed 7 stale "8-level" references, and added 8 new L6 negative tests. Final: 895 tests passing.

---

## [2026-02-27] - EPIC-PDFV4-001: PDF Extraction v4 Pipeline

**Type**: Epic
**Duration**: ~2 weeks (2026-02-06 to 2026-02-27)
**Priority**: P0

### Summary

Complete rewrite of the PDF extraction pipeline from the v3 4-layer post-processing chain to a quality-gated, per-page orchestrated pipeline. The new system assesses each page independently, routes to appropriate enhancement actions (GMFT tables, Claude vision, Pandoc for arXiv), tracks budgets, and logs decisions. Includes comprehensive `extract --check` CLI feature for environment readiness verification.

### Research Phase (Stages 1-3)

**Stage 0 — Prerequisites** (`doc-extract-prerequisites`): Migrated 8 test corpus PDFs (~28MB), corpus metadata, and extraction infrastructure from worktree to `doc-ingest-clean` branch.

**Stage 1A — pymupdf4llm Deep-Dive** (`pymupdf4llm-deep-dive`): Systematic investigation of pymupdf4llm configuration across 7 PDFs. Found CompositeHeaderDetector outperforms baseline, `ignore_code=True` eliminates code fence spam.

**Stage 1B — Pandoc Deep-Dive** (`pandoc-deep-dive`): Evaluated Pandoc for arXiv HTML→markdown. Key finding: pre-processing HTML to strip `<figure>` tags enables table/figure conversion.

**Stage 1C — Docling Deep-Dive** (`docling-deep-dive`): Investigated Docling & GMFT. Found Docling best for heading detection in single-page mode; GMFT best for fast clean table extraction.

**Stage 1D — Claude Headless Deep-Dive** (`claude-headless-deep-dive`): Tested Claude vision for PDF page→markdown. Key finding: Claude's equation→LaTeX transcription is irreplaceable. Recommended as selective enhancement at $0.39-$1.17/doc.

**Stage 3 — Pipeline Experimentation** (`pipeline-experimentation`): Tested 6 pipeline hypotheses (H1-H6) against ground truth. Identified winning composition for production.

**Table Image Spike** (`table-image-spike`): Tested cropped table images vs full-page for extraction quality. Claude achieves exact match on 4/5 papers from crops.

### Implementation Phase (Items 1-4)

**Item 1 — Types, Metrics & Quality Gate** (`types-metrics-quality-gate`): Foundation layer — `PageAction`, `PageResult`, `PageAssessment`, `PageDecision` types, quality metrics, quality gate routing, budget allocation. 47+ tests.

**Item 2 — Enhancement Modules** (`pdf-extraction-v4-item2`): Four modules — `tables.py` (GMFT+Img2Table+Docling ensemble), `claude_enhance.py` (vision with validation), `pandoc_convert.py` (arXiv detection), refactored `pymupdf_backend.py`. ~850 lines of new code.

**Item 3 — Pipeline Orchestration & CLI** (`pipeline-orchestration-cli`): Wired 8-step pipeline into `extract_pdf()` entry point, rewrote `extract_cli.py`, replaced legacy 4-layer chain.

**Item 4 — Integration Tests & Cleanup** (`integration-tests-cleanup-ship`): Deleted 10 deprecated files, added deprecation stubs for legacy CLI flags, wrote integration tests with AST analysis for dormant code detection.

### Bug Fixes & Polish

**Claude Invocation & Logging** (`v4-claude-invocation-and-logging`): Fixed silent `invoke_claude()` failures from Claude Code output format change, added pre-flight availability checks, escalated logging.

**Extract --check** (`extract-check`): New `agentic-mbse extract --check` CLI feature probing all 6 pipeline components with human-readable table + JSON output. 44 tests.

**Built-in Test Corpus** (`check-pdfs`): Bundled 2 purpose-built PDFs exercising all 6 validation probes so `extract --check` works without user-provided PDFs. 177 tests passing.

---

## [2026-02-08] - EPIC-PDFV3-001: PDF Extraction v3

**Type**: Epic
**Duration**: 3 days (2026-02-06 to 2026-02-08)
**Priority**: P1

### Summary

Built a 4-layer document extraction pipeline that converts PDF/DOCX to structured, indexed markdown. Uses Claude as the structural authority for header detection and repair, solving the heuristic fragility that caused v2 to fail on unseen documents.

### Deliverables

**Extraction Pipeline** (`src/agentic_mbse/extraction/`, 11 modules, ~3,000 lines):
- Layer 1: Base backends (pymupdf4llm, Docling, Pandoc) with automatic selection and fallback
- Layer 1.5: Deterministic post-processing (ligature replacement, header promotion, TOC removal, footer detection)
- Layer 2: GMFT table enhancement (Microsoft Table Transformer for complex tables)
- Layer 3: Claude-powered structure detection and repair (style detection + text-anchored header insertion)
- Layer 4: Vision-based AI quality repair with cross-validation safety
- Quality gates between layers (malformed table/equation/structure detection)
- INDEX.md generation with section hierarchy and optional AI summaries

**CLI** (`agentic-mbse extract`):
- `--enhance` for full 4-layer pipeline
- `--structure-only` for Layer 3 only
- `--model` to override Claude model
- `--no-tables` to skip GMFT
- Backend selection, timeout, force, output flags

**Skill**: `claude/skills/pdf-analysis/` — interactive 3-tier extraction for Claude Code sessions

**Tests**: 9 new test files, 3,824 lines of extraction test coverage

### Benchmark Results

- 12-document corpus: 4/5 new docs produce usable INDEX files (target met)
- Zero regressions on original 7-document corpus
- 881 total tests passing

---

## [2026-02-03] - Architecture Redesign (4 Epics)

**Type**: Epic (x4)
**Duration**: ~8 days (2026-01-27 to 2026-02-03)
**Priority**: P1

### Summary

Complete toolkit redesign replacing the monolithic command/template system with a layered architecture: Knowledge → Behavioral → Structural → PM Engine.

### EPIC-ARCH-001: Structure (Phase 1A)

4-directory architecture replacing `modeling_pm/`:
- `knowledge/` — domain insights, research, source index
- `modeling_project/` — architecture, requirements, overview, guides
- `work/` — backlog, active/completed work items, learnings
- `data/` — traceability matrix, structured data

6 new + 5 revised project templates. YAML frontmatter schemas for design artifacts. `cmd_init()` rewired for new structure. 80+ tests updated.

### EPIC-ARCH-002: Knowledge (Phase 2B)

9 new skills: epic-decomposition, model-validation, pdf-analysis, project-structure, record-learning, requirements-tracking, source-traceability, sysml-conventions, toolkit-awareness. Context measurement report and extraction mapping complete.

### EPIC-ARCH-003: Commands (Phase 3C)

All 9 existing commands refactored to lean ~300-line format. 5 new commands: analyze-models, formalize-intent, quick-model, review-model, status. sysmlv2-doc-analyzer agent deprecated. All commands registered in installation pipeline.

### EPIC-ARCH-004: PM Engine (Phase 3D)

8 typed Pydantic parsers for project files. Deterministic state derivation (work item state machine, epic aggregation). Dashboard generator. 14 mutation operations (add-item, close-item, add-validation, trace-element, etc.). CLI subcommands (`agentic-mbse pm`, `agentic-mbse status`). 3,267 lines of PM tests.

---

## [2026-01-23] - ITEM-SYMLINK-001: Tool-Owned File Safety

**Type**: Item
**Duration**: 1 day
**Priority**: P2

### Summary

Added hash-based modification detection for tool-owned files. Re-running `agentic-mbse init` now warns users before overwriting files that have local modifications, offering options to skip, backup, or overwrite. Also added `LOCAL_GUIDE.md` template for project-specific customizations that won't be touched by init.

### Deliverables

**Phase 1 - Hash Utilities + LOCAL_GUIDE.md**:
- Added `_compute_file_hash()`, `_load_tool_hashes()`, `_save_tool_hashes()` functions
- Created `project_templates/LOCAL_GUIDE.md.template` (user-owned)
- Added reference from MODELING_GUIDE.md to LOCAL_GUIDE.md

**Phase 2 - Modification Detection + Backup**:
- Added `_check_modification()` function comparing current hash to stored hash
- Added `_backup_file()` function with collision handling (.backup, .backup.1, etc.)

**Phase 3 - User Prompts + Install Function**:
- Added `_prompt_for_modified_file()` with options: skip, backup, overwrite, skip_all, overwrite_all
- Added `_install_file_with_hash()` function returning (action, hash) tuples

**Phase 4 - Integration**:
- Integrated modification detection into `cmd_init()`
- Hash file (`.claude/.tool-hashes.json`) created on normal init, skipped in dev mode
- Added `backed_up` tracking in summary output

**Phase 5 - Verification**:
- Audited fusion-tea content (all 4 patterns found in docs/patterns/)
- 70 tests passing

### Lessons Learned

- Hash-based detection is simpler than marker comments or template comparison
- User prompt flow with skip_all/overwrite_all improves UX for multiple files
- Dev mode intentionally skips hashes since files are symlinks

---

## [2026-01-23] - ITEM-REGTEST-001: Model Regression Testing

**Type**: Item
**Duration**: 1 day
**Priority**: P1

### Summary

Added pytest-compatible testing infrastructure for SysML models. When library definitions change, running `pytest tests/models/` reveals if existing designs break. The spec/plan/implement workflow now naturally produces tested models.

### Deliverables

**Phase 1 - CLI + Templates**:
- `agentic-mbse init` creates `tests/models/` directory
- Created `project_templates/test_models_example.py.template` with syside usage examples
- Created `project_templates/conftest.py.template` with `load_sysml()` fixture

**Phase 2 - Documentation**:
- Added "Model Regression Testing" section to `MODELING_GUIDE.md.template`
- Explains library/usage regression risk and testing paradigm

**Phase 3 - MBSE Commands**:
- Updated `spec-model.md` with evaluatable success criteria guidance
- Updated `plan-model.md` with test phase pattern and examples
- Updated `implement-model.md` with regression testing section and pytest checklist

**Phase 4 - Target Repo Validation**:
- Validated end-to-end in fusion-tea
- Fixed template API mismatch (syside `Diagnostics` iteration)
- Tests correctly detected real model issue (unresolved reference)

### Lessons Learned

- Template tests should use `pytest.skip()` for graceful handling of missing models
- syside `Diagnostics` requires accessing `.parser` and `.sema` properties, not direct iteration
- Real-world validation (Phase 4) caught issues unit tests missed

---

## [2026-01-23] - ITEM-RENAME-001: Rename `project/` to `modeling_pm/`

**Type**: Item
**Duration**: 1 day
**Priority**: P1

### Summary

Renamed the modeling project management directory from `project/` to `modeling_pm/` for clearer semantic distinction. The old name was ambiguous with `.project/` (tool development).

### Deliverables

**Phase 1 - Core Code**:
- Updated `src/agentic_mbse/cli/__init__.py` - All template paths and comments
- Updated `scripts/replicate_setup.sh` - Directory creation and user instructions
- Updated `tests/test_cli.py` - Test expectations for new paths

**Phase 2 - Documentation & Templates**:
- Updated `CLAUDE.md` - Directory clarification table
- Updated all 4 project templates with new path references

**Phase 3 - Claude Commands** (8 files):
- `research.md`, `onboard.md`, `audit-models.md`, `backlog.md`
- `design-model.md`, `plan-model.md`, `implement-model.md`, `spec-model.md`

**Phase 4 - Agents & Physical Rename**:
- Updated `python-debugger.md` agent
- `git mv project/ modeling_pm/`
- Updated additional discovered files (README.md, record-learning skill, docs/patterns/)

### Lessons Learned

- Comprehensive grep before starting revealed scope accurately
- `replace_all` edit mode efficient for systematic string replacement
- Need to check both `claude/` (source) and `.claude/` (installed copies) directories

---

## [2026-01-16] - ITEM-SYSIDE-001: SysIDE v0.8.4 Upgrade

**Type**: Item
**Duration**: 0.5 days
**Priority**: Maintenance

### Summary

Upgraded syside tooling (CLI, Python package, documentation) from v0.8.1 to v0.8.4. Created versioned documentation structure with compatibility symlinks for existing agent paths.

### Deliverables

**CLI & Package**:
- Extracted `syside-0.8.4-x86_64-linux-glibc.tar.xz` to `~/.local/`
- Updated `pyproject.toml` dependency from `>=0.8.1` to `>=0.8.4`

**Documentation**:
- Reorganized existing docs into `docs/syside/v0.8.1/`
- Scraped 348 new files to `docs/syside/python/v0.8.4/`
- Created compatibility symlinks (`api/` → `python/v0.8.4/`)
- Added `docs/syside/VERSION.md` for version tracking

### Lessons Learned

- Scraper needed updates for changed docs.sensmetry.com URL structure
- New structure puts Python API at `/python/v0.8.4/` instead of `/v0.8.4/api/`
- Symlinks provide backwards compatibility without updating all agents

---

## [2026-01-15] - ITEM-LEARNING-001: Agent Learning Feedback Loop

**Type**: Item
**Duration**: 1 day
**Priority**: P1

### Summary

Created a lightweight system for agents to record insights when they discover solutions, building institutional memory that improves future agent performance.

### Deliverables

- `claude/skills/record-learning/SKILL.md` - Skill for capturing learnings
- `project_templates/RAW_LEARNINGS.md.template` - Template for learnings storage
- Updated `cmd_init()` to create `project/learnings/` directory

### Key Features

- User-invocable via `/record-learning` command
- Agent can self-invoke when discovering noteworthy patterns
- Requires user approval before recording (never autonomous)
- Structured entry format: timestamp, category, problem, solution, generalization

---

## [2026-01-15] - ITEM-DEVMODE-001: Development Mode for Init

**Type**: Item
**Duration**: 1 day
**Priority**: P1

### Summary

Added `--dev` flag to `agentic-mbse init` that creates symlinks for tool-owned files instead of copies, enabling bidirectional editing between agentic-mbse source and domain projects.

### Deliverables

- `--dev` CLI flag for init subcommand
- Symlink creation for all tool-owned files (commands, agents, skills, hooks, templates)
- Source checkout detection (errors if used with pip-installed package)
- Platform detection (errors on Windows)
- Auto-updates `.gitignore` with tool-owned paths

### Lessons Learned

- Symlinks must use absolute paths for reliability
- Need to detect pip-installed vs source checkout via `__file__` inspection

---

## [2026-01-15] - ITEM-GUIDE-001: Progressive Disclosure Restructure

**Type**: Item
**Duration**: 1 day
**Priority**: P1

### Summary

Restructured `MODELING_GUIDE.md.template` from 1,497 lines to 205 lines using progressive disclosure pattern. Detailed reference material extracted to 12 pattern docs in `docs/patterns/`.

### Deliverables

**Pattern Documents Created** (12 total):
- `semantic-operators.md` (568 lines) - Assignment, redefinition, binding semantics
- `syntax-reference.md` (364 lines) - 10 core syntax patterns
- `mbse-concepts.md` (270 lines) - Allocation, parametric, cost patterns
- `definitions-usages.md` (260 lines) - Core def vs usage principle
- `expose-pattern.md` (287 lines) - The EXPOSE pattern for interfaces
- `adr002-calculations.md` (241 lines) - Calculation architecture
- `doc-comments.md` (298 lines) - Documentation standards
- `package-naming.md` (251 lines) - Naming conventions
- `common-mistakes.md` (353 lines) - Anti-patterns to avoid
- `constraints.md` (291 lines) - Constraint expressions
- `cross-file-binding.md` (297 lines) - Multi-file imports

**Updated Files**:
- `project_templates/MODELING_GUIDE.md.template` - Reduced from 1,497→205 lines
- `docs/patterns/README.md` - Index of all 12 pattern docs

### Lessons Learned

- Progressive disclosure significantly improves readability
- Extracting to separate pattern docs enables better discoverability via grep
- Pattern docs are larger than source sections due to added structure (examples, common mistakes)

---

## [2026-01-13] - ITEM-BACKPORT-001: Backport fusion-tea Patterns

**Type**: Item
**Duration**: 0.5 days
**Priority**: P1

### Summary

Backported validated modeling patterns from the fusion-tea domain project into agentic-mbse templates.

### Deliverables

Added to `MODELING_GUIDE.md.template`:
- Cost Model Imports section (NumericalFunctions::sum)
- Multiplicity Cost Aggregation Pattern
- Part Redefinition Pattern (dot notation vs redefines)
- Parameterized Multiplicity Pattern

### Lessons Learned

- Bidirectional sync between source and domain projects needs automation (→ ITEM-DEVMODE-001)
- Validated patterns should flow from real usage, not theoretical design

---

## [2026-01-13] - EPIC-DOC-001: Documentation Discoverability Overhaul

**Type**: Epic
**Duration**: 2 days (2026-01-12 to 2026-01-13)
**Priority**: P0 (Critical)

### Summary

Complete overhaul of documentation discoverability infrastructure. Users were unable to find standard library functions like `NumericalFunctions::sum` because the KerML spec wasn't extracted and agents had no navigable index. This epic fixed the root causes through PDF extraction, INDEX.md-based navigation, specialized agents, and stdlib sync.

### Deliverables

**Scripts**:
- `scripts/generate_index.py` - Generate INDEX.md with AI summaries from full_document.md
- `scripts/read_section.py` - Read specific sections by number using INDEX.md
- `scripts/sync_stdlib.py` - Sync syside standard library to docs/sysmlv2/stdlib/

**Documentation**:
- `docs/sysmlv2/SysML_KerMLSpec/INDEX.md` - 111 sections indexed
- `docs/sysmlv2/SysML_Spec_v2_Part1/INDEX.md` - Part 1 indexed
- `docs/sysmlv2/SysML_Spec_v2_Part2/INDEX.md` - Part 2 indexed
- `docs/sysmlv2/SysML_Spec_v2_Part3/INDEX.md` - Part 3 indexed
- `docs/sysmlv2/stdlib/` - 94 library files with INDEX.md

**Agents**:
- `claude/agents/kerml-expert.md` - KerML spec + standard library
- `claude/agents/sysml-expert.md` - SysML Parts 1-3
- `claude/agents/syside-expert.md` - syside tooling
- `claude/agents/sysmlv2-validator.md` - Syntax validation
- `claude/agents/deprecated/sysmlv2-doc-analyzer.md` - Old monolithic agent

### Items Completed

| Item | Completed | Notes |
|------|-----------|-------|
| extract-missing-pdf-specs | 2026-01-12 | KerML + Part1 extracted via PyMuPDF |
| doc-index-tooling | 2026-01-13 | INDEX.md approach, scripts created |
| specialized-doc-agents | 2026-01-13 | 4 new agents, old agent deprecated |
| stdlib-corpus | 2026-01-13 | 94 files synced with INDEX.md |
| markdown-chunker-indexer | 2026-01-13 | DEPRECATED - superseded by INDEX.md approach |

### Lessons Learned

- INDEX.md with line numbers is simpler and more effective than physical document chunking
- PyMuPDF produces better output than Docling for structured PDFs (faster, less memory)
- Specialized agents enable parallel research and focused expertise
- AI-generated summaries scale well for documentation indexes

---

## [2026-01-10] - Init File Ownership

**Type**: Item
**Duration**: 1 day

### Summary

Modified `agentic-mbse init` to distinguish between user-owned files (preserved on re-init) and tool-owned files (always updated). Users can now safely re-run `init` to get latest tool improvements without losing customizations.

### Deliverables

- Updated `src/agentic_mbse/cli/__init__.py` with user/tool file categorization
- `USER_OWNED_TEMPLATES` and `TOOL_OWNED_TEMPLATES` constants
- Three-way output: Created / Updated / Skipped
- Updated CLAUDE.md with file ownership documentation

### Lessons Learned

- Clear separation of ownership prevents user frustration
- Explicit feedback (created/updated/skipped) builds trust

---

## [2026-01-09] - Replicate Setup Script

**Type**: Item
**Duration**: 1 day

### Summary

Created `scripts/replicate_setup.sh` to replicate `agentic-mbse init` behavior for development in this repo without requiring the CLI to be installed. Enables dogfooding the MBSE commands.

### Deliverables

- `scripts/replicate_setup.sh` - ~210 lines, installs commands/agents/skills/hooks
- Updated `.gitignore` for generated files (project/, models/library/, SOURCE_INDEX.md)
- Updated CLAUDE.md with directory clarification (.project/ vs project/)

### Lessons Learned

- Placeholder substitution pattern (`{SYSML_DOCS_PATH}`) works well for portability
- Clear documentation of directory purposes prevents confusion

---

## [2026-01-09] - Conditional Expression Pattern Documentation

**Type**: Item
**Duration**: 1 day

### Summary

Created single source of truth for SysML v2 conditional expression syntax at `docs/patterns/conditionals.md`. Fixed incorrect C-style ternary syntax in MODELING_GUIDE.md.template.

### Deliverables

- `docs/patterns/README.md` - Pattern directory purpose
- `docs/patterns/conditionals.md` - Comprehensive conditional syntax reference
- Updated `project_templates/MODELING_GUIDE.md.template` Syntax 10

### Lessons Learned

- Single source of truth prevents documentation drift
- Parser-verified examples prevent incorrect syntax from propagating

---
