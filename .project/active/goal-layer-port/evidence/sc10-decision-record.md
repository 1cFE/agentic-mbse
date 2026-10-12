# SC10 evidence: the goal-layer decision record against fusion-tea ADR-0001..0007

The record is `docs/goal-layer-decisions.md`. Every source file was read from the snapshot `.orchestrate-logs/fusion-tea-snapshot/` (fusion-tea `2b1e9f9d5`). Checked 2026-10-11 in P5.

## Per record

"Provenance" is the source frontmatter's `provenance:` field. "Carried" is the record's **Grade** line; the record's **Source** line also quotes the provenance field verbatim (checked by `grep -c` of the whole Source line: 1 hit each). "Cited path" is the path the record cites, `@2b1e9f9d5`; each exists in the snapshot.

| ADR | Provenance (fusion frontmatter) | Grade the record carries | Cited path at `2b1e9f9d5` | Match |
|---|---|---|---|---|
| 0001 | [AGENT] ratified by owner; coarse grain inferred from lean-first ruling | `[AGENT]` ratified by the owner; coarse grain inferred from the owner's lean-first ruling. Amendment 2026-09-11 `[AGENT]` ratified by the owner (source `:17`) | `.project/adr/0001-strategy-and-task.md` | yes |
| 0002 | [OWNER] purpose; [AGENT] mechanism | `[OWNER]` purpose; `[AGENT]` mechanism. 2026-09-14 trigger selection and coverage reuse `[AGENT]`, implementing the owner's request (source `:17`) | `.project/adr/0002-round-boundary.md` | yes |
| 0003 | [OWNER] lean-first ruling, 2026-08-23; [AGENT] separate `learnings.md` mechanism | Same, with the owner's words quoted from source `:33`. Amendments: 2026-08-27 `[OWNER]` rule, `[AGENT]` verdict ratified (`:49`); 2026-08-28 `[OWNER]` rule, `[AGENT]` verdict audited (`:66`); 2026-09-11 `[OWNER-VERBATIM]` with the quote (`:81`) | `.project/adr/0003-lean-first-persistence.md` | yes |
| 0004 | [OWNER] 2026-08-23 | `[OWNER]` 2026-08-23 | `.project/adr/0004-finding-disposition.md` | yes |
| 0005 | [AGENT] inference (topology; owner may override) + [OWNER 2026-08-25] (pre-execution checkpoint placement) | `[AGENT]` inference for the topology, owner may override; `[OWNER]` 2026-08-25 for the checkpoint placement. 2026-09-14 topology `[AGENT]`, implementing the owner's request (source `:17`); criterion-5 placement `[AGENT]` (`:31`) | `.project/adr/0005-review-topology.md` | yes |
| 0006 | [OWNER] 2026-08-23 | `[OWNER]` 2026-08-23; the digest-meaning reconciliation `[INFERRED]`, digest requirement owner-graded (source `:43`) | `.project/adr/0006-goal-evidence-seam.md` | yes |
| 0007 | [AGENT] task-as-authority-unit half; [OWNER] 2026-08-23 finding-obligation half | `[AGENT]` task-as-authority half; `[OWNER]` 2026-08-23 finding-obligation half | `.project/adr/0007-supersession.md` | yes |

Every source record is dated 2026-08-25 in its frontmatter, and each entry says "Decided 2026-08-25".

## Titles

Six entry headings are `### ADR-000N — <source title>` verbatim (`grep -qxF`). ADR-0006's title is generalized: "Goal artifacts may cite `.project/` by path and digest; …" becomes "Goal artifacts may cite a second PM's records by path and digest; …". This is the two-PM condition (spec `[INFERRED]` on ADR-0006; runbook `:13` and `:305` use the same wording). The record's opening states the condition.

## What was generalized, and why

Each entry keeps the decision as amended, its grades and dates, its invariants and its rejected alternatives, in short. These source specifics are left out or reworded, because SC2 and the brief rule out fusion-only terms outside provenance lines:

- Invariant locations become the shipped runbook sections and templates. The study-layer invariants of ADR-0004 (fusion's run-study runbook, its discovery-log path and its join test) become "where a target installs a study layer, its runbook … its discovery log's header … its join check", as runbook `:271` and `:277` word them.
- ADR-0003's two proof-run amendments keep their measurements, verdicts and grades. Fusion's goal slugs, the item numbers, the commit `4a8de283`, the domain question and the record paths are left out. The 2026-08-27 "`GOAL_RUNBOOK.md:234`/`:244` contradiction" is described as "a contradiction between two runbook lines", because those line numbers refer to the runbook as it was then and the snapshot does not show which lines they were.
- ADR-0006's citation forms follow runbook `:233` ("an externally stored research binary", "the committed study record"). Fusion's `CLAUDE.md:73` invariant is described as "the instructions' rule against cross-referencing the two PMs was narrowed to state" in the source project.
- ADR-0004's "criterion 4 of `study-driven-model-development.md`" is described by its content, as ADR-0007 `:25` states it.

## Sources section

| Source the runbook cites | Record line | Snapshot check |
|---|---|---|
| Critic definition (runbook `:41`) | concept `:47`, `[OWNER]` | `goal-driven-model-development-harness.md:47` is success criterion 5, holding "The critic is never the author's session." |
| Goals are general | concept `:198`, `[OWNER]` | `:198` reads "- **[OWNER]** Goals are general to the systems-engineering and concept-development process; …", quoted in full |
| 2026-08-27 probe amendment (runbook `:95`) | ADR-0003 2026-08-27 amendment; probe record path | fusion runbook `:94` cites `.project/completed/20260827_goal-cold-pickup-proof/gate-probe-record.md`. The snapshot does not hold that file, so the record cites it as "the probe record fusion-tea's runbook cites", not as checked |
| 2026-09-14 process-sizing request (runbook `:66`) | ADR-0002, ADR-0005 | The snapshot holds no wording of the request. ADR-0002 `:17` and ADR-0005 `:17` call it "the owner's 2026-09-14 process-simplification request"; the record says the wording is not quoted |

## Checks run

- `tests/test_goal_layer.py::test_every_cited_adr_is_in_the_decision_record`: the record's `### ADR-` headings are exactly ADR-0001..0007, and every `ADR-NNNN` in the goal text (the two skills, runbook, three templates, the narrative test and the record) is among them. Passes.
- `tests/test_goal_layer.py::test_goal_text_points_at_nothing_in_fusion_tea` now covers the record and the narrative-test template. Every record line that names fusion-tea or `.project/` carries `@2b1e9f9d5`, except the opening's two-PM line, which uses the "for example" wording. Passes.
- Reachability: `grep -n get_docs_dir project_templates/GOAL_RUNBOOK.md.template` → `:85` (§ Grounding a goal, the pattern directory) and `:296` (§ The decisions behind this, the docs directory holding `goal-layer-decisions.md`). `test_installed_goal_references_resolve` asserts `get_docs_dir() / "goal-layer-decisions.md"` exists; `test_built_wheel_carries_the_resolver_reached_goal_layer_documents` asserts the wheel carries it with source bytes.
