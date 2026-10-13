# Read-through record: the ported study text (SC5(b))

Every fusion-specific line of the five ported files, with one verdict each (design Appendix I). Line numbers are fusion-tea `b06585709`. The shipped files are under `src/sysml_codegen/assets/` at this branch's tip.

**How to read a row.**

- `kept: general` — the line is general after all, and ships unchanged.
- `kept: labelled example` — fusion vocabulary inside a labelled example, with no identifier; ships unchanged, or with only its label added (audit F8).
- `kept verbatim: owner-graded rule` — the line sits inside an `[OWNER]` rule, so it ships in the owner's words; any rewording goes to the owner (audit F8).
- `generalized` — rewritten in place. No fusion-tea fact left the text: a tool path became its command, LCOE became "objective", a goal-runbook path became "the installed goal runbook".
- `moved` — a fusion-specific fact left the shipped text. The row names its fusion-tea home, "exists at `b06585709:<line>`" or "added on the O4 branch", and an **anchor**: a fixed string that greps in that home (`git grep -nF '<anchor>' -- <file>`, runbook step 3). When the line itself ships in general form, the row quotes that too.

"The O4 branch" is the fusion-tea branch on which orchestrator step O4 commits the drafts in `evidence/fusion-tea/text/`. The homes it adds:

- **Policy § 6** — `modeling_project/STUDY_POLICY.md`, new subsection "### Execution routes" under § 6 (`fusion-tea/text/STUDY_POLICY.patch`).
- **Policy § 12** — the same file, new "## 12. Locations".
- **Policy § 13** — the same file, new "## 13. Provenance of the installed study text".
- **Supplement** — `docs/integration_seam_operator_guide.md`, rewritten as fusion-tea's supplement to the installed guide (`fusion-tea/text/integration_seam_operator_guide.md`).

The policy's existing text is the home of every `SP-` row: fusion-tea keeps its ratified policy, and `install-commands` never overwrites an existing one.

---

## `SKILL.md` (SK)

| Id | fusion-tea line(s) | Text (quoted, ≤ 12 words) | Class | Verdict | New text, or destination |
|---|---|---|---|---|---|
| SK-1 | :8 | "sweep R and a" (a trigger phrase) | — | kept: labelled example | Unchanged: a trigger example in fusion vocabulary, no identifier |
| SK-2 | :9 | "how sensitive is LCOE to" | objective | generalized | "how sensitive is the objective to" |
| SK-3 | :11 | "pick up the results in exploration/.../studies/" | path | generalized | "pick up the results in a studies directory" |
| SK-4 | :13-14 | `allowed-tools: …` / `user-invocable: true` | envelope | generalized | Frontmatter gains `metadata: kind: workflow`, which `install-commands --list` reads through agentic-mbse's `frontmatter` |
| SK-5 | :35 | "Review scope follows `work/orchestration/GOAL_RUNBOOK.md` § Review scope…" | goal-layer | generalized | "Review scope follows the installed goal runbook, § Review scope and evidence reuse … A project without the goal layer applies the study policy's § Process sizing instead." |
| SK-6 | :57 | "the record path is `exploration/<pkg>/studies/<study-id>/`" | path | moved | Ships "`<studies-dir>/<study-id>/` … named in the study policy's § Locations". Home: Policy § 12, added on the O4 branch; anchor `exploration/<pkg>/studies/<study-id>/` |
| SK-7 | :69 | "`modeling_project/STUDY_POLICY.md` — the rulebook" | path | kept: general | The path where `install-commands` writes the policy template in every project (design Appendix D) |
| SK-8 | :72 | "`scripts/study/` — the tools" | tool | generalized | "`sysml-codegen study` — the tools"; the bundle's other files join the list (`annex-template.md`, `integration-guide.md`) |

## `runbook.md` (RB)

| Id | fusion-tea line(s) | Text (quoted, ≤ 12 words) | Class | Verdict | New text, or destination |
|---|---|---|---|---|---|
| RB-1 | :5 | "**The rulebook** is `modeling_project/STUDY_POLICY.md`." | path | kept: general | The installed policy's path (SK-7) |
| RB-2 | :9 | "**The record** is `exploration/<pkg>/studies/<study-id>/`" | path | moved | Ships "`<studies-dir>/<study-id>/`", with a new "**The studies directory**" paragraph naming the policy's § Locations. Home: Policy § 12, added on the O4 branch; anchor `exploration/<pkg>/studies/<study-id>/` |
| RB-3 | :13 | "**The annex** is `exploration/<pkg>/studies/ANNEX.md`" | path | moved | Ships "`<studies-dir>/ANNEX.md`", starting from `annex-template.md`. Home: Policy § 12, added on the O4 branch; anchor `## 12. Locations` |
| RB-4 | :57 | "**Calls:** `scripts/study/indicators.py` axis-declaration file" | tool | generalized | "the axis-declaration file `sysml-codegen study indicators` reads" |
| RB-5 | :60, :94, :108, :129, :172 | "**Annex:** `exploration/<pkg>/studies/ANNEX.md § …`" | path | generalized | "**Annex:** `§ Declared ties`" and the like: the annex path is RB-3's |
| RB-6 | :68 | "**Calls:** `scripts/study/indicators.py`" | tool | generalized | "`sysml-codegen study indicators`" |
| RB-7 | :75 | "Assess the review triggers in `work/orchestration/GOAL_RUNBOOK.md` …" | goal-layer | generalized | "… in the installed goal runbook, § Review scope and evidence reuse; a project without the goal layer applies the study policy's § Process sizing." |
| RB-8 | :91 | "**Calls:** the route under evaluation" | route | generalized | "the execution route the study policy's § Execution routes names, supplied by the package annex" |
| RB-9 | :93 | "an adapter's own self-check fails" | adapter | moved | Ships "the route cannot load the package". Home: Policy § 6, added on the O4 branch; anchor `own self-check fails` |
| RB-10 | :94 | "and `§ Loader exception and glue` when the annex has one" | adapter | moved | Ships "**Annex:** `§ Baseline pin`". Home: Policy § 6, added on the O4 branch; anchor `Step 5 reads` |
| RB-11 | :105 | "**Calls:** `scripts/study/preflight.py`" | tool | generalized | "`sysml-codegen study preflight gates`" |
| RB-12 | :123-124 | "(`20260905-stored-energy-basis`, pre-execution critique F1; goal … L-008; …)" | pointer | moved | The rule ships; its citation goes. Home: Policy § 13, added on the O4 branch; anchor `pre-execution critique F1` |
| RB-13 | :133-136 | "Two routes, and no third. The **`teax-study` CLI** runs…" | route | moved | Ships "Use a route the study policy's § Execution routes names; nothing else is a route." Home: Policy § 6, added on the O4 branch; anchor `Two routes, and no third.` |
| RB-14 | :138-141 | "If the route is the adapter route, disclose the glue…" | adapter | moved | The disclosure ships, adapter-free: "Disclose in the same place anything the harness supplies … The expected case is … 'glue ledger: none'." Home of the adapter-route rule: Policy § 6, added on the O4 branch; anchor `if the route is the adapter route` |
| RB-15 | :146 | "`…ANNEX.md § Loader exception and glue` when the annex has one…" | adapter | moved | Ships "**Annex:** none". Home: Policy § 6, added on the O4 branch; anchor `A package with no adapter has no` |
| RB-16 | :148 | "### 9. Run every point through the stock teax lifecycle" | — | kept: general | teax is the study layer's runtime in every project (spec Non-Goals) |
| RB-17 | :159 | "`…ANNEX.md § Era pin` when the annex has one (…stock teax has none)" | adapter | moved | Ships "**Annex:** none". Home: Policy § 6, added on the O4 branch; anchor `Steps 9 and 13 read` |
| RB-18 | :169 | "**Calls:** `scripts/study/verify.py`" | tool | generalized | "`sysml-codegen study verify`" |
| RB-19 | :200-203 | "While the package runs under an era pin, the report states…" | adapter | generalized | The step-13 era-pin line (design S5): "If the record's `teax.era_pin` is not null, state that pin as a reproduce prerequisite at the claim site, not only in a provenance note — …". fusion-tea's wording is restated in Policy § 6 (anchor `While the package runs under an era pin`) |
| RB-20 | :208 | "**Annex:** `…ANNEX.md § Era pin` when the annex has one" | adapter | moved | Ships "**Annex:** none". Home: Policy § 6, added on the O4 branch; anchor `Steps 9 and 13 read` |
| RB-21 | :219 | "(`work/orchestration/GOAL_RUNBOOK.md`)" | goal-layer | generalized | "(the installed goal runbook, § The discovery log; in a project without the goal layer, the same rule binds whoever dispositions a finding)" |
| RB-22 | :223 | "+ `exploration/<pkg>/studies/DISCOVERY_LOG.md`" | path | moved | Ships "`<studies-dir>/DISCOVERY_LOG.md`". Home: Policy § 12, added on the O4 branch; anchor `exploration/<pkg>/studies/DISCOVERY_LOG.md` |
| RB-23 | :230 | "deleting or editing the manifest, the adapter, or the package" | adapter | generalized | "… the manifest, the route, or the package …" |
| RB-24 | :251 | "The framing per axis, the LCOE result, …" | objective | generalized | "… the objective result, …" |
| RB-25 | :287 | "One file per package at `exploration/<pkg>/studies/DISCOVERY_LOG.md`." | path | moved | Ships "One file per package, in its studies directory: `<studies-dir>/DISCOVERY_LOG.md`." Home: Policy § 12, added on the O4 branch; anchor `exploration/<pkg>/studies/DISCOVERY_LOG.md` |
| RB-26 | :297-298 | "or a joined disposition update, written by a goal round." | goal-layer | generalized | Adds "(the installed goal runbook, § The discovery log) or, in a project without the goal layer, by whoever dispositions the finding." |
| RB-27 | :190 | "including goal dispositions; … at administration, checkpoint, and round closure" | goal-layer | generalized | "… including a goal round's dispositions where the goal layer is installed; … at administration or, under the installed goal runbook, at its checkpoint and round closure" (audit F8; it named goal-process stages with no citation and no fallback) |

## `record-template.md` (RT)

| Id | fusion-tea line(s) | Text (quoted, ≤ 12 words) | Class | Verdict | New text, or destination |
|---|---|---|---|---|---|
| RT-1 | :3 | "Copy this file to `exploration/<pkg>/studies/<study-id>/record.md`" | path | moved | Ships "the study's record directory, the folder named for the study id in the package's studies directory" (worded without `<` since audit F3). Home: Policy § 12, added on the O4 branch; anchor `exploration/<pkg>/studies/<study-id>/` |
| RT-2 | :22 | "glue ledger: none — no adapter on this route" | adapter | generalized | "glue ledger: none — nothing on this route is harness-supplied" |
| RT-3 | :61 | "**LCOE objective channel(s):**" | objective | generalized | "**Objective channel(s):**" |
| RT-4 | :62 | "**LCOE result:**" | objective | generalized | "**Objective result:**" |
| RT-5 | :157 | "**Route:** `<teax-study CLI \| study-local direct-API>`" | route | moved | Ships "`<the execution route the study policy names>`". Home of the two values: Policy § 6, added on the O4 branch; anchor `names its route as` |
| RT-6 | :167-168 | "glue ledger: none. No adapter on this route, so…" | adapter | generalized | "glue ledger: none. Nothing on this route is harness-supplied." |
| RT-7 | :242 | "Deleting or editing the manifest, the adapter, or the package" | adapter | generalized | "… the manifest, the route, or the package …" |
| RT-8 | :250-251 | "Field names marked **(Item 3)** are copied from `.project/completed/…`" | pointer | moved | Ships "Field names marked **(fixed by the tool's schema)** are the study tools' own document fields …". Home: Policy § 13, added on the O4 branch; anchor `20260821_run-study-indicators` |
| RT-9 | :259-260, :268-269, :276-277, :281-283, :291, :294, :297, :301, :369-370, :382-383 | "// (Item 3)" — 17 markers in the snapshot shape | pointer | generalized | "// (fixed by the tool's schema)", the design's wording |
| RT-10 | :304-306 | "Resolved at snapshot time over the oracle's own source files…" | — | generalized | Names the recipe's call: "sysml_codegen.study.common .tool_source_digest(files, root=<project root>)" (design Appendix I) |
| RT-11 | :306-307 | "the manifest carries no digest (gap G1, run-study-cold-pickup)" | pointer | moved | Ships "the manifest carries no digest." Home: Policy § 13, added on the O4 branch; anchor `gap G1, run-study-cold-pickup` |
| RT-12 | :369 | `"path": "scripts/study/<tool>.py"` | tool | generalized | `"path": "sysml_codegen/study/<tool>.py"`, plus the one history note naming the pre-move prefixes, worded as design Appendix I gives it (the one SC5 exemption) |
| RT-13 | :377 | `"era_pin": "<the era pin and its worktree path, or null…>"` | adapter | moved | Ships `"<null, or the teax revision the route needs beyond the environment's>"`. Home of the worktree-path convention: Policy § 6, added on the O4 branch; anchor `names the era pin and its worktree path` |
| RT-14 | :401-402 | "For the schema as Item 3 accepts it" | pointer | generalized | "For the manifest schema the tools ship with" |
| RT-15 | :406-407 | "(Settled by orchestrator ruling 2026-08-19; the plan raised it…)" | pointer | moved | Removed. Home: Policy § 13, added on the O4 branch; anchor `orchestrator ruling 2026-08-19` |
| RT-16 | :331, :333-337, :421-425 | "adapter_source_digest", "the explicit nil, when no adapter exists" | adapter | kept: general | Disclosure machinery: the fields keep their names and the nil form stays (spec, Known Requirements § Instruction text) |
| RT-17 | :440-441 | "a sealed-versus-adapter A/B differs in exactly this field" | adapter | kept: general | Why the glue ledger is arm-scoped; it states disclosure, not adapter practice |
| RT-18 | :444-445 | "Item 3 sets `subset: true` when the indicator run was narrowed" | pointer | generalized | "The indicators tool sets `subset: true` …" |

## `integration-guide.md`, from `docs/integration_seam_operator_guide.md` (IG)

| Id | fusion-tea line(s) | Text (quoted, ≤ 12 words) | Class | Verdict | New text, or destination |
|---|---|---|---|---|---|
| IG-1 | :3 | "`scripts/integrate.py` answers one question" | tool | generalized | "`sysml-codegen study integrate` answers one question" |
| IG-2 | :27-43 | "uv run --env-file ~/1cfe/agentic-mbse/.env … python scripts/integrate.py …" | project | moved | Ships a placeholder invocation. Home: Supplement § The full invocation in fusion-tea, added on the O4 branch; anchor `20260822_WI-030_computed-beta-peak-field@ba5c9945` |
| IG-3 | :45 | "For the current supplied-design stellarator interface (WI-075–078), use…" | project | moved | Supplement, same section; anchor `axes.supplied_design.json` |
| IG-4 | :47 | "A full run takes about 15–20 seconds." | project | moved | Supplement, same section; anchor `about 15–20 seconds` |
| IG-5 | :57 | "— ADR-0006's citation form." | pointer | moved | Ships "cited `PATH@COMMIT`". Home: Supplement § Where each input comes from in fusion-tea; anchor `ADR-0006` |
| IG-6 | :58 | "For the stellarator package: `exploration/stellarator_e2e/models`." | project | moved | Supplement, same section; anchor `for the stellarator package` |
| IG-7 | :60 | "The study-package manifest beside the route, `studies/manifest.json`." | path | generalized | "… in the package's studies directory, `<studies-dir>/manifest.json`" |
| IG-8 | :61 | "The known-answer declaration under `tests/study/data/` is the usual one." | project | moved | Supplement, same section; anchor `known-answer declaration under` |
| IG-9 | :62, :139, :251, :253 | "resolve from the repository root" | path | generalized | "the project root" throughout (B1); :139's depth-four example becomes "one `..` per level of the project root's path" |
| IG-10 | :64 | "`tests/models/data/mfe_census.json`." (`--census-file`) | project | moved | Ships "The project's tracked entry-point census", plus the census file's shape. Home: Supplement § Where each input comes from in fusion-tea; anchor `mfe_census.json` |
| IG-11 | :67 | "`git -C "$STOP_PARSER_TEAX_ROOT" rev-parse HEAD`" | project | moved | Ships `git -C "$TEAX_SIMKIT_PATH" rev-parse HEAD` (B7). Home: Supplement, same section; anchor `It is the same revision` |
| IG-12 | :76-77 | "export SYSIDE_LICENSE_KEY=... # in ~/1cfe/agentic-mbse/.env…" | project | moved | Ships the variable without the path. Home: Supplement § The environment in fusion-tea; anchor `which does not export it itself` |
| IG-13 | :79-86 | "export STOP_PARSER_WHEEL_TARGET=…" and the other four `STOP_PARSER_*` | project | moved | Ships `TEAX_SIMKIT_PATH` and "every variable the project's declaration lists". Home: Supplement, same section; anchor `STOP_PARSER_WHEEL_TARGET=/home/reid/1cfe/fusion-tea` |
| IG-14 | :89 | "**The sealed wheels.** `/home/reid/1cfe/stop-parser-sealed-wheels/` holds…" | project | moved | Supplement, same section; anchor `stop-parser-sealed-wheels` |
| IG-15 | :91-95 | "**Two `--env-file` flags instead of `export`.** …integration.env…" | project | moved | Ships "A file holding these lines works as well: `uv run --env-file <file> …`". Home: Supplement, same section; anchor `flags instead of` |
| IG-16 | :97 | "the repository root and `$STOP_PARSER_TEAX_ROOT/packages/teax-simkit` on…" | project | generalized | "the project root and `$TEAX_SIMKIT_PATH` on `PYTHONPATH`; the project root … as `SYSML_CODEGEN_PROJECT_ROOT`" (B7, the seam's environment) |
| IG-17 | :99-109 | "**Running from a second checkout or worktree.** …" | project | moved | The general fact ships ("The seam's interpreter is every producer's interpreter"). Home of the procedure: Supplement § Running from a second checkout or worktree (the heading fusion-tea's `CLAUDE.md` § Python Environment cites); anchor `## Running from a second checkout or worktree` |
| IG-18 | :111 | "**All six variables are checked…** …reads the four wheel variables…" | project | moved | Ships "Every variable is checked before any producer runs: `SYSIDE_LICENSE_KEY`, then each variable the declaration lists, then teax." Home of fusion-tea's six and its provenance test: Supplement § The environment in fusion-tea; anchor `reads the four wheel variables inside its` |
| IG-19 | :141 | "The tracked stellarator root is a symlink: pass `--package …`" | project | moved | Ships "If the package root you pass is a symlink, the candidate names its target." Home: Supplement § Reading a fusion-tea answer; anchor `exploration/stellarator_e2e/generated` |
| IG-20 | :179 | "all six environment variables are exported" (gate 0) | project | generalized | "`SYSIDE_LICENSE_KEY` and every declared variable are exported"; fusion-tea's six are IG-18's |
| IG-21 | :180 | "`tests/test_dependency_provenance.py` — the pinned revisions and the installed wheel artifacts." | project | moved | Ships "The pytest target the project declares under `gates.pinned-packages` …". Home: Supplement § fusion-tea's declaration (and fusion-tea's `pyproject.toml` at runbook step 6); anchor `the pinned revisions and the installed wheel artifacts` |
| IG-22 | :181 | "`git -C $STOP_PARSER_TEAX_ROOT rev-parse HEAD` … the gap is filed." | pointer | moved | Ships "`git -C $TEAX_SIMKIT_PATH rev-parse HEAD` … Without `TEAX_SIMKIT_PATH` it could not run." Home of "the gap is filed": Supplement § Open rows fusion-tea tracks against the seam; anchor `the gap is filed` |
| IG-23 | :185 | "`tests/models/test_model_family_spines.py` — the canonical tree, the family twins…" | project | moved | Ships "The pytest target the project declares under `gates.model-family-spine` …". Home: Supplement § fusion-tea's declaration; anchor `the canonical tree, the family twins, the tracked census` |
| IG-24 | :186-188 | "`scripts/study/manifest.py`", "`scripts/study/preflight.py gates`", "`scripts/study/verify.py`" | tool | generalized | The manifest check (`sysml_codegen/study/manifest.py`), `sysml-codegen study preflight gates`, `sysml-codegen study verify` |
| IG-25 | :197 | "the provenance suite reads `pyproject.toml`, `uv.lock` and the installed wheels…" | project | moved | Ships a labelled example: "For example, a pin test reads the project's `pyproject.toml`, its lock file and the installed distributions…". Home: Supplement § fusion-tea's declaration; anchor `The spine suite generates from` |
| IG-26 | :207 | "Gate 5 reads the **tracked** `tests/models/data/mfe_census.json` whatever you passed." | project | moved | Ships "Gate 5 runs the declared target, which reads whatever census the project tracks for it …". Home: Supplement § fusion-tea's declaration; anchor `It is the spine suite` |
| IG-27 | :220 | "Check the sealed-wheel paths first, **and** that `STOP_PARSER_WHEEL_TARGET` names…" | project | moved | Ships "Check the inputs the declared pin gate reads first … **and** that `TEAX_SIMKIT_PATH` names the checkout you meant." Home: Supplement § Reading a fusion-tea answer; anchor `of the interpreter actually running` |
| IG-28 | :223 | "Re-derive `tests/models/data/mfe_census.json` from the new package." | project | moved | Ships "Re-derive the tracked census from the new package …". Home: Supplement § fusion-tea's declaration; anchor `refusal means: re-derive` |
| IG-29 | :225 | "The model-family spine suite refused: the canonical tree, the twins…" | project | generalized | "The declared model-family-spine target refused."; what fusion-tea's target checks is IG-23's |
| IG-30 | :229 | "`verify.py` returned non-zero." | tool | generalized | "`verify` returned non-zero." |
| IG-31 | :233 | "That shortfall is filed against `scripts/study/verify.py`." | pointer | moved | Ships "…`verify_stderr.txt` names teax when that is the cause." (B9). Home: Supplement § Open rows; anchor `That shortfall is filed against` |
| IG-32 | :242-248 | "uv run --env-file … python scripts/study/preflight.py gates \\" | project | moved | Ships `sysml-codegen study preflight gates \`. Home: Supplement § Reading a fusion-tea answer; anchor `python scripts/study/preflight.py gates` |
| IG-33 | :261 | "Study import aliases also use temporary directories and are removed…" | project | moved | Removed; the moved tools make no import alias. Home: Supplement § Reading a fusion-tea answer; anchor `Study import aliases` |
| IG-34 | :266 | "`preflight.py clean`'s own result" | tool | generalized | "`preflight clean`'s own result" |
| IG-35 | :282 | "exact declarations cover route/scripts/teax Python sources" | path | generalized | "… the Python sources of the route directory, of the installed study tools and of teax under `TEAX_SIMKIT_PATH` …" (B8), plus the runtime reads B13 adds |
| IG-36 | :283 | "**Gate 5's refusal path is not covered by a test.** …" | project | moved | Removed: a fact about fusion-tea's suite. Home: Supplement § Open rows; anchor `refusal path is not covered by a test` |
| IG-37 | :284 | "…does **not** discharge the open row against `verify.py`." | pointer | moved | Ships "`verify` records `teax.revision: "unrecorded"` … that does not change what `verify` records." Home: Supplement § Open rows; anchor `the open row against` |
| IG-38 | :290 | "`.project/adr/0009-integration-is-a-fixed-point-proof.md` — why the seam proves…" | pointer | moved | Ships a pointer to `runbook.md`. Home: Supplement § Related; anchor `0009-integration-is-a-fixed-point-proof.md` |
| IG-39 | :291 | "`scripts/study/preflight.py`, … — the producers, each with its own module docstring." | tool | generalized | "The producers, `sysml-codegen study preflight` and `verify` and the manifest check — each module's docstring …" |
| IG-40 | :292 | "`tests/study/test_integrate_*.py` — … five real refusals from real producers." | project | moved | Removed: fusion-tea's tests. Home: Supplement § Related; anchor `five real refusals from real producers` |
| IG-41 | :294 | "## Keep disposable execution files outside the repository" | path | generalized | "… outside the project" |
| IG-42 | :296 | "For historical reproduction scripts with an `--out` option, … frozen scripts…" | project | moved | The general hygiene ships. Home: Supplement § Historical reproduction scripts; anchor `old archive review` |
| IG-43 | :175 | "The numbering is the requirements' — step 1 splits into two producers" | pointer | moved | Ships "The numbers are the seam's step numbers." Home: Supplement § The gate numbers in fusion-tea, added by `fusion-tea/text/audit-f8-supplement.patch` against the O4 branch tip `699b0a74d` (audit F8); anchor `step numbers of fusion-tea's integration-seam requirements` |

## `STUDY_POLICY.md.template`, from `modeling_project/STUDY_POLICY.md` (SP)

Every `moved` row's home is fusion-tea's own policy, which exists at `b06585709` and stays in place.

| Id | fusion-tea line(s) | Text (quoted, ≤ 12 words) | Class | Verdict | New text, or destination |
|---|---|---|---|---|---|
| SP-1 | :3 | "**Status**: Ratified whole — [OWNER] 2026-08-21 (RUN-STUDY Item 6 Align…" | project | moved | Template: "**Status**: Template, not ratified by this project." Home exists at `b06585709:3`; anchor `Ratified whole` |
| SP-2 | :4 | "**Created**: 2026-08-02" | — | generalized | Folded into the template's "**Snapshot**" line: "first written 2026-08-02 and ratified whole by its owner on 2026-08-21, as they stood on 2026-10-12" |
| SP-3 | :5 | "Written for the stellarator MBSE demo (`.project/concepts/…`, criteria 5–6…)" | project | moved | Template keeps a general "**Consumers**" line. Home exists at `b06585709:5`; anchor `Written for the stellarator MBSE demo` |
| SP-4 | :7 | "Owner concern (2026-08-02): … the demo … (`~/1cfe/sysml-codegen/.project/research/02-…`)" | project | moved | Template keeps the concern in general words. Home exists at `b06585709:7`; anchor `relational/DM-decomposition proposal` |
| SP-5 | :15 | "(beta ≤ limit, wall load ≤ limit, TBR ≥ floor, rec_frac ≤ knee)" | — | kept: labelled example | Labelled in place: "(in a fusion plant model, for example: beta ≤ limit, …)" (audit F8; it was unlabelled) |
| SP-6 | :20 | "Current state (verified 2026-08-02): all five executing asserts (`net_positive`…" | project | moved | Template: a typed slot, "Current state (verified `<YYYY-MM-DD>`): `<the model's executing asserts, and which of them are equalities>`". Home exists at `b06585709:20`; anchor `zero equality pressure in the model today` |
| SP-7 | :28 | "geometry (R, a, kappa), field, density (or density-limit fraction)…" | — | kept verbatim: owner-graded rule | Unchanged. It sits inside § 2's `[OWNER]` axis rule and is not labelled as an example; its words stay the owner's (audit F8) |
| SP-8 | :29 | "(R feeds both `'Plasma Geometry'` and `'MFE Radial Build'`, `mfe_plasma_scaling.sysml:24,66`)" | project | moved | Template: "(for example, a major radius that feeds both a plasma-geometry calculation and a radial-build calculation)". Home exists at `b06585709:29`; anchor `mfe_plasma_scaling.sysml:24,66` |
| SP-9 | :30 | "…the demo's differentiation evidence … 1costingFE … (precedent: WI-024's p_cryo…)" | project | moved | Template: "… this is the intended direction of travel: each internalization replaces a value a reference tool takes as given (or inverse-solves) with physics the model derives." Home exists at `b06585709:30`; anchor `WI-024` |
| SP-10 | :40 | "Add an **inequality assert** in `mfe_viability.sysml` style, MR-4-cited." | project | moved | Template: "Add an **inequality assert**, with its bound cited to a source." Home exists at `b06585709:40`; anchor `MR-4-cited` |
| SP-11 | :43 | "converts today's manual LCOE-eyeballing detection … (no-fallbacks rule)" | objective | moved | Template: "converts manual eyeballing of the objective into verdict data. No unsourced bounds: …". Home exists at `b06585709:43`; anchor `LCOE-eyeballing` |
| SP-12 | :45 | "the burned points are the collapse the owner is worried about." | project | moved | Template: "… the collapse this policy exists to prevent." Home exists at `b06585709:45`; anchor `the owner is worried about` |
| SP-13 | :47 | "(failure class A′, `.project/research/20260725-110828_study-failure-classes-…`)" | pointer | moved | Template drops the citation. Home exists at `b06585709:47`; anchor `study-failure-classes-and-mechanisms` |
| SP-14 | :53 | "the WI-022/CAS72 pattern … (later epic items / refinement rounds)" | pointer | moved | Template: "(routes to the handwritten rung: …)" and "(later refinement rounds)". Home exists at `b06585709:53`; anchor `WI-022/CAS72`. Since audit F8 the rung's "oracle mirror" is stated generally: "+ an independent check of the handwritten body" |
| SP-15 | :59 | "the field the designer specifies (Stellaris: B₀ = 9.0 T)" | project | moved | Template: "(say, B₀ = 9.0 T)". Home exists at `b06585709:59`; anchor `Stellaris: B` |
| SP-16 | :67 | "The current balance (`mfe_power_balance.sysml`) has `p_th = …`" | project | moved | Template: "Take a power balance of the form `p_th = …`." Home exists at `b06585709:67`; anchor `mfe_power_balance.sysml` |
| SP-17 | :73 | "**In-model precedent**: … the WI-019 derivation in its doc comment…" | project | moved | Removed from the template. Home exists at `b06585709:73`; anchor `WI-019 derivation` |
| SP-18 | :77 | "a handwritten iteration on the WI-022 rung" | pointer | moved | Template: "on the handwritten rung". Home exists at `b06585709:77`; anchor `on the WI-022 rung`. Since audit F8 "oracle-mirrored at 1e-9" is labelled: "checked independently at a stated tolerance (for example, by an oracle that mirrors it to 1e-9)" |
| SP-19 | :79 | "(ISS04), the likeliest first real case … `mfe_plasma_scaling.sysml` (or sibling)" | project | moved | Template: "(ISS04)" and "in the plasma-scaling file (or a sibling)". Home exists at `b06585709:79`; anchor `likeliest first real case` |
| SP-20 | :91 | "### If the ladder runs out — the tripwire (§7)" | — | generalized | "(§8)": the cross-reference corrected (Evidence B) |
| SP-21 | :93 | "the relational/DM proposal would need anyway; per that report's own bar" | pointer | moved | Template: "… the evidence any heavier solving machinery would need anyway, and such machinery should be adopted on *specific observed demand* …". Home exists at `b06585709:93`; anchor `relational/DM proposal would need anyway` |
| SP-22 | :97 | "## 5. Anti-patterns (barred in demo studies)" | project | moved | Template: "## 5. Anti-patterns". Home exists at `b06585709:97`; anchor `barred in demo studies` |
| SP-23 | :101 | "criterion 5 bars it ("no hand-rolled sweep loops or harness code")" | pointer | moved | Template restates the rule: "a study runs its points through the runtime's own lifecycle, with no hand-rolled sweep loops or harness code." Home exists at `b06585709:101`; anchor `criterion 5 bars it` |
| SP-24 | :104 | "screens enter as constraints only with a defensible source (no-fallbacks rule)." | pointer | moved | Template drops the rule's name. Home exists at `b06585709:104`; anchor `defensible source (no-fallbacks rule)` |
| SP-25 | :108-120 | "## 6. teax machinery in scope" … IFE harness path; "To confirm at Item 5" | project | moved | Template: slot "## 6. Execution routes". Home exists at `b06585709:108`; anchor `## 6. teax machinery in scope` |
| SP-26 | :124-130 | "## 7. Hypotheses the first study round tests — [AGENT]" (H1–H3) | project | moved | Template: slot "## 7. Hypotheses". Home exists at `b06585709:124`; anchor `H1 (parameterization holds)` |
| SP-27 | :132-137 | "## 8. Tripwire record" (empty table) | — | kept: general | Unchanged: § 4 sends an unresolved cycle there (Evidence B) |
| SP-28 | :139 | "(concept `run-study-skill.md` SC-2/SC-3, Settled; ratified here 2026-08-21)" | pointer | moved | Template: "— [OWNER] (2026-08-21)" and a provenance line naming the run-study concept. Home exists at `b06585709:139`; anchor `SC-2/SC-3` |
| SP-29 | :143 | "the deterministic facts `scripts/study/indicators.py` derives" | tool | generalized | "the installed indicators tool (`sysml-codegen study indicators`)" |
| SP-30 | :152-156 | "## 10. Verification — [OWNER]" (1costingFE reference; the oracle's retirement) | project | moved | No verification section (DD16, spec Non-Goals); the template's § 10 is the Locations slot. Home exists at `b06585709:152`; anchor `1costingFE is the validation reference` |
| SP-31 | :160 | "The owner's process-simplification request permits brief or skipped stages" | project | moved | Template: "This rule permits brief or skipped stages …". Home exists at `b06585709:160`; anchor `process-simplification request` |
| SP-32 | :162 | "Review follows `work/orchestration/GOAL_RUNBOOK.md` § Review scope…" | goal-layer | generalized | "Where the goal layer is installed, review follows the installed goal runbook, § Review scope and evidence reuse. Without it, the rest of this paragraph is the review rule." |
| SP-33 | :16 | "(a confinement scaling must hold; a balance must close)" | — | kept: labelled example | Labelled in place: "(for example, a balance must close; in a fusion plant model, a confinement scaling must hold)" (audit F8) |
| SP-34 | :79 | "rewires `p_nrl`/`p_input` from design-instance constants" | — | kept: labelled example | Unchanged: inside "**Example — confinement ⇄ power balance (ISS04).**" (audit F8 found no row) |
| SP-35 | :81 | "the analyses layer already takes inputs from many subsystems" | project | generalized | "the calculations already take inputs from many subsystems" (audit F8) |
| SP-36 | :160 | "owner rulings, source quarantine, executable gates" | project | generalized | "owner rulings, any rules the project keeps on admissible sources, executable gates": the template has no source-quarantine rule (audit F8) |

---

## Every LCOE instance

LCOE appears five times in the five sources. Each has its row: SK-2, RB-24, RT-3, RT-4 and SP-11. The step-13 era-pin line is RB-19, `generalized`.

## Ported docstring labels (DL)

The orchestrator's Phase 5 brief put Phase 1's and Phase 3's label proposals in scope. Each fusion-tea design label in a ported comment or docstring either states its meaning inline or goes. Line numbers are at `f0f9351`, before the edit; commit `f46a913` made it.

| Id | Site | Label | Verdict | Why |
|---|---|---|---|---|
| DL-1 | `common.py:17` | "(design Risks, L5c)" | dropped | The sentence already says what the rule is for: "so a record can tell whose revision it is reading" |
| DL-2 | `identity.py:86` | "(design S1)" | dropped | The docstring's next paragraph states the reason |
| DL-3 | `indicators.py:27` | "(Invariant 6)" | dropped | The sentence states the invariant: no package, key prefix or adapter |
| DL-4 | `indicators.py:48` | "(D5)" | dropped | "fixed text versioned with the schema" is the decision |
| DL-5 | `indicators.py:231-233, :246` | "R1" … "R4" | kept: defined in place | The same docstring defines each rule where it names it; `:246`'s "R3:" points two lines up |
| DL-6 | `indicators.py:256` | "(M3)" | dropped | "the read-set coverage check" names it, and `manifest.assert_read_set_covered` states it |
| DL-7 | `indicators.py:274` | "(R11)" | dropped | The sentence states the rule |
| DL-8 | `indicators.py:317` | "# R11: neither participates in the closure" | meaning stated | "# an EntryPoint or ExitPoint never participates in the closure" |
| DL-9 | `indicators.py:366` | "(R10)" | dropped | The docstring states the closure rule |
| DL-10 | `indicators.py:443` | "(R7, R8)" | dropped | The docstring states what is read and what raises |
| DL-11 | `indicators.py:676` | "(R12)" | dropped | "Advisory only" and the docstring say it |
| DL-12 | `indicators.py:817` | "(D8)" | dropped | The fixed order follows on the same line |
| DL-13 | `indicators.py:819` | "(M3)" | dropped | As DL-6 |
| DL-14 | `manifest.py:17` | "(Invariant 6)" | dropped | As DL-3 |
| DL-15 | `manifest.py:36` | "the seam Items 2 and 4 cite" | meaning stated | "the document contract records and the other tools cite" |
| DL-16 | `manifest.py:47` | "(M1)" | dropped | "its presence is a failure" is the rule |
| DL-17 | `manifest.py:498` | "(M3)" | dropped | The docstring states the check |
| DL-18 | `integrate.py:583-584` | "the gitignored test workspace … (D8)" | meaning stated | "Inside a git-ignored directory git has nothing to say, which is why the byte gates run on the seam's own digest instead." |
| DL-19 | `integrate.py:939` | "an absent wheel variable" | generalized | "an absent environment variable": B4 moved the wheel variables into one project's declaration (Phase 3's proposal) |
| DL-20 | `indicators.py:233` | "65 edges depend on the strip" | generalized | "real pipelines depend on the strip": the count was one fusion-tea package's. Phase 5 left it as a fact, not a label; the orchestrator's Phase 6 brief (fix 2) put it in scope, and Phase 6 made the edit |

## Corrections and additions that are not fusion-specific

These have no fusion-tea home to find, because nothing fusion-specific left with them.

- **Phase 6 (orchestrator's fix 4).** The runbook's "The tools" and the guide's "Where the project root is" state how a route under read coverage finds its root: from the package's work tree with no variable, and a refusal naming `SYSML_CODEGEN_PROJECT_ROOT` when the package is in no work tree. The guide's line on invoking a producer by hand no longer implies the variable is always needed.
- **Guide.** "one of fourteen stable slugs" (`:159`) said fourteen beside a table of fifteen; it now says fifteen. "Nine inputs. Four of them are optional to `argparse`…" (`:53`) miscounted, and every flag is optional to `argparse`; it now reads "Four inputs are optional to the request but **not** optional to the answer". New sections: "The project's declaration", "Where the project root is", "The snapshot rule", the census file's shape, and "teax at gate 0". The exit-2 row names the two exits that write no document.
- **Runbook.** New: the "studies directory" paragraph, "The tools", "What a package annex supplies", and the Check lines of steps 14 and 15 (DD12). The Check commands carry no literal `<`, so recording them in `record.md` § 14 leaves the placeholder check true; the design's `grep -c '<' record.md` would fail once recorded.
- **Record template.** § 14 says the Check commands are recorded there. The history note is new (D7). Audit F3: the preamble above § 1 holds no `<`, because the template copies it into every record and step 15's first Check counts every `<`; its `<axis>`, `<...>` and `<YYYY-MM-DD>` tokens are now worded, and the placeholder rule says the preamble holds none (`tests/study/test_run_study_bundle.py::test_a_literal_copy_of_the_record_template_passes_the_placeholder_check`).
- **Annex template.** New file (DD18).
- **Policy template.** New header lines "**Snapshot**" and "**This project fills in**"; new slots § 6, § 7 and § 10. Audit F8: "**This project fills in**" also names the current-state line that closes § 1.
- **Audit F8's smaller slips.** The runbook's annex table gives `--print-fingerprint` its required `--package DIR`. The shipped `teax-completion.md` command (outside SC5's five files) named `generate_scenario.py --generate-inputs`, which sysml-codegen does not have; it now says to run `sysml-codegen generate` and give every input a value.

## Totals

| File | Rows | kept: general | kept: labelled example | kept verbatim: owner-graded rule | generalized | moved |
|---|---|---|---|---|---|---|
| `SKILL.md` | 8 | 1 | 1 | 0 | 5 | 1 |
| `runbook.md` | 27 | 2 | 0 | 0 | 13 | 12 |
| `record-template.md` | 18 | 2 | 0 | 0 | 10 | 6 |
| integration guide | 43 | 0 | 0 | 0 | 12 | 31 |
| policy template | 36 | 1 | 3 | 1 | 6 | 25 |
| **All five** | **132** | **6** | **4** | **1** | **46** | **75** |

Every one of the 74 `moved` anchors was checked mechanically: it greps in its named home on a copy of fusion-tea `b06585709` with the four patches in `fusion-tea/text/` applied, and each "exists at" anchor greps at `b06585709` itself. Audit F8 added the 75th, IG-43. On the O4 branch tip `699b0a74d` (rebuilt as the staged `b06585709` copy plus the branch diff) with `fusion-tea/text/audit-f8-supplement.patch` applied, `check_anchors.py` prints `75 anchors found, 0 missing`.

Docstring labels: 20 rows — 14 dropped, 3 meaning stated, 2 generalized, 1 kept (defined in place).
