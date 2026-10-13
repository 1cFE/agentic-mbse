# WRAP-SPLIT migration ledger

Item 2 owns this file; Item 1 created it for its own rows. Each row records consumer-specific text that leaves agentic-mbse-installed files, where it was, its fusion-tea home, and the evidence. The owner applied Item 1's fusion-tea changes. Item 2's are made by the orchestrator on the fusion-tea branch `goal-layer-mr7` and merged by the owner (`goal-layer-port/briefs/align.md`). Either way, fusion-tea must hold each destination before the agentic-mbse change that removes the text merges; for Item 2 the destinations are on `goal-layer-mr7`, which merges in the order given in its section.

## Item 1 — native-skill-distribution

| Text | Was in (fusion-tea) | New fusion-tea home | Evidence |
|---|---|---|---|
| The `.codex-test` worktree paragraph ("For this worktree, use `.agentic-mbse/patterns/` … Use `.codex-test/run` for toolkit/Python commands …") | `.agentic-mbse/codex.md:11`, a tool-owned file a re-init replaces with no prompt (it matches its manifest hash) | `AGENTS.md`, appended verbatim under a heading naming its source | `native-skill-distribution/evidence/fusion-tea-target-owned.patch`; rehearsal confirmations (`evidence/rehearsal/*-confirm.txt`) |
| The pattern-location note ("Pattern references such as `[patterns/plant-idiom.md]` name files in this worktree's `.agentic-mbse/patterns/` directory …") | `modeling_project/MODELING_GUIDE.md:276`, tool-owned and replaced with no prompt | `AGENTS.md`, appended verbatim | same patch and rehearsal |
| The two MR-7 paragraphs | `modeling_project/MODELING_PROCESS.md:17` and `:34` | Stay in place. The file differs from its manifest hash, so a re-init prompts for it; runbook step 4 keeps it (answer `s`). Item 2 lands the general section | rehearsal confirmations; `native-skill-distribution/evidence/fusion-tea-runbook.md` step 4 |

**Facts the pattern-note row carries (design D10).**

- After the re-init, Codex reads two conflicting instructions: the shipped guide says to locate pattern docs with the `get_docs_dir()` resolver, and `AGENTS.md` says to use `.agentic-mbse/patterns/`.
- That worktree copy equals `main`'s `docs/patterns/` today (its 14 manifest hashes match `8f43a09`), but no installer refreshes it any more.
- The note's stated reason, that the copy "is versioned separately from the pinned executable runtime", ends at runbook step 1, when the pin moves to the merged SHA and the resolver then points at same-version docs.
- **Owner choice, does not block Item 1:** after step 1, keep the note, drop it, or copy it into `CLAUDE.md`. It is fusion-tea's own text.

## Item 2 — goal-layer-port

Fusion-tea line numbers are at `2b1e9f9d5`. "F1" is the content commit on `goal-layer-mr7` and "F2" the post-merge switch (design D13); A6 and A7 are the design's MR-7 and `CLAUDE.md` texts. Evidence paths are in `goal-layer-port/evidence/` unless they start with `docs/`. "At `2b1e9f9d5`" marks a home that already exists, read in the orchestrator's snapshot of that commit. `fusion-tea/branch-diff-F1.txt` is written by orchestrator phase O1, which also checks that each destination appears in it or already exists at `2b1e9f9d5`. "SC12" ids are hunks in `sc12-hunks.md`.

| Text | Was in (fusion-tea) | New fusion-tea home | Evidence |
|---|---|---|---|
| Goal-layer ADRs as the "why" | run-goal `:20,:73`; runbook `:7,:31,:272,:299-305` | `.project/adr/`, unchanged; `CLAUDE.md` "Goal layer in this repository", "Decision records" (A7, F1) | `fusion-tea/branch-diff-F1.txt`; SC12 RG-4, RG-10, RB-1, RB-3, RB-16, RB-21 |
| Codex test worktree setup | run-goal `:49,:55` | `AGENTS.md:7,:11` (exists); A7 "Launcher" (F1) | at `2b1e9f9d5`: `AGENTS.md:7,:11`; `fusion-tea/branch-diff-F1.txt`; SC12 RG-5, RG-7 |
| MR-7 hooks | run-goal `:53`; runbook `:84,:100,:139`; `goal.md:29` | MR-7 "Invariant" (A6, F1); the generalized hooks ship | `fusion-tea/branch-diff-F1.txt`; SC12 RG-6, RB-6, RB-8, RB-10, GT-1; `sc6-crosswalk.md` § Goal-layer hooks |
| Research seam guide, request files, scripts, `research-acquire`, clean-room screen | run-goal `:61,:63`; runbook `:286,:288` | A7 "Research" (F1); `CLAUDE.md:247` holdout line (exists) | `fusion-tea/branch-diff-F1.txt`; at `2b1e9f9d5`: `CLAUDE.md:247`; SC12 RG-8, RG-9, RB-18, RB-19 |
| Integration seam, `integrate.py`, ADR-0009, guide, history | runbook `:286,:289` | A7 "Integration" (F1); ADR-0009 (exists) | `fusion-tea/branch-diff-F1.txt`; SC12 RB-18, RB-19 |
| Study runbook and policy, discovery-log path, join test | runbook `:106,:260,:270,:276` | A7 "Studies" (F1); run-study runbook `:285-287` (exists) | `fusion-tea/branch-diff-F1.txt`; at `2b1e9f9d5`: `.claude/skills/run-study/runbook.md:285`; SC12 RB-9, RB-13, RB-15, RB-17 |
| Study-store and R2 citation specifics | runbook `:232` | `CLAUDE.md` "Research Artifact Sync (R2)" (`:302`, exists); run-study runbook (exists) | at `2b1e9f9d5`: `CLAUDE.md:302`; SC12 RB-12 |
| Coding PM in `.project/` as a premise | runbook `:13`, `:304` | `CLAUDE.md` "Project Management — Two Systems" (`:74`, exists) | at `2b1e9f9d5`: `CLAUDE.md:74`; SC12 RB-2, RB-21 |
| Concept path, probe-record path, "Item 4 proof run" | runbook `:41,:94,:262` | The concept file, the probe record and ADR-0003's amendment (exist); the decision record cites them as provenance | `docs/goal-layer-decisions.md` § Sources the Runbook Cites; `sc10-decision-record.md` (the probe record confirmed at `2b1e9f9d5`); SC12 RB-4, RB-7, RB-14 |
| Depth-rubric policy pointer | runbook `:100`; `MODELING_PROCESS.md:34` | MR-7 "Depth work" (A6, F1) | `fusion-tea/branch-diff-F1.txt`; SC12 RB-8; `sc6-crosswalk.md` |
| The two MR-7 process paragraphs | `MODELING_PROCESS.md:17,:34` | The shipped "Process Selection" row, technical-pattern row and `design-choices.md`; MR-7 cites them (A6, F1). Closes Item 1's row of the same name: fusion-tea's `MODELING_PROCESS.md` returns to the shipped template, so no re-init prompts for it | `sc6-crosswalk.md` § fusion-tea process paragraphs; `fusion-tea/branch-diff-F1.txt` |
| `.agentic-mbse/patterns/` location line | `MODELING_PROCESS.md:70` | None needed: the owner dropped fusion-tea's pattern note (`8a35c4d0f`), and the shipped resolver text applies | `fusion-tea/branch-diff-F1.txt` |
| Binding-row semicolon | `MODELING_PROCESS.md:75` | Upstreamed: `project_templates/MODELING_PROCESS.md.template:72` (A2) | `fusion-tea/branch-diff-F1.txt` (no difference left on that line) |
| MR-7 general application, evidence, enforcement, acceptance and examples | `REQUIREMENTS.md:91-107` | The shipped `design-choices.md`; MR-7 cites it and keeps its authority line and fusion-only application (A6, F1) | `sc6-crosswalk.md` § MR-7; `fusion-tea/branch-diff-F1.txt`; `sc6-delta-check.md` (O1) |
| Narrative check path | narrate-goal `:77` | fusion-tea's own `tests/orchestration/test_goal_contract.py` stays | at `2b1e9f9d5`: `tests/orchestration/test_goal_contract.py`; SC12 NG-4; `fusion-tea/rehearsal/pytest.txt` (O2) |
| ADR-register check (`test_register_is_coherent` and its `yaml` import) | `tests/orchestration/test_goal_contract.py:1,:7,:9-31`; run by narrate-goal's validation step (`:77`) | Stays in fusion-tea's `tests/orchestration/test_goal_contract.py`, unchanged, and runs with fusion-tea's suite. The installed test has another basename (D9), so no re-init writes fusion-tea's file. After F2, narrate-goal's validation step runs only the narrative-link check, the one a new narrative can break | at `2b1e9f9d5`: `tests/orchestration/test_goal_contract.py`; SC12 NG-4, NT-1, NT-2, NT-3; `fusion-tea/rehearsal/pytest.txt` (O2) |
| Local `run-goal`, `narrate-goal`, their `.agents/skills/` links, `.gitignore:25,:27`, `AGENTS.md:5` "goal and study" | `.claude/skills/`, `.agents/skills/`, `.gitignore`, `AGENTS.md` | Replaced by the installed bundles in F2; `AGENTS.md:5` reads "Local study skills" | `fusion-tea-runbook.md` step 3; `fusion-tea/rehearsal/git-status.txt` and `manifest.txt` (O2) |

**Merge order** (design § Integration Strategy):

1. The owner merges and pushes agentic-mbse `goal-layer-port`; call the merge commit M.
2. F2 runs on `goal-layer-mr7` with M, by the orchestrator or the owner, following `fusion-tea-runbook.md`.
3. The owner pushes and merges `goal-layer-mr7`.

F1's commit message says not to merge before the pin commit. Until step 3, fusion-tea `main` keeps its local goal files and its pin `adbef75`, so a re-init there changes nothing. Every F1 destination above is on `goal-layer-mr7` before step 1; the last row's replacement is F2 itself, in step 2.

## Item 5 — research-seam-port

Fusion-tea line numbers are at `0a833b9f7`, the snapshot the port was made from (its seam files equal `c42ed1d8a`'s). "Command" is `.claude/commands/research-acquire.md` and "guide" is `docs/research_seam_operator_guide.md`; both are deleted on the fusion-tea branch `research-seam-port`, and their shipped successors are `skills/research-acquire/SKILL.md` and `docs/research-seam.md`. "Pending O1 branch" marks a home the orchestrator writes on that branch in O1 (design Appendix D); "at `0a833b9f7`" marks a home that already exists. O1 step 5 checks each home appears in the branch diff or exists at `0a833b9f7`, and records it in `research-seam-port/evidence/o1-fusion-tea-branch.md`. As with Item 2, every home is on the branch before the owner merges this agentic-mbse change; the branch itself merges after it, when O3 moves fusion-tea's pin.

| Text removed from the ported copy | Was in (fusion-tea) | fusion-tea home | Evidence |
|---|---|---|---|
| "citable under MR-4" | command `:93`; guide `:38` | `CLAUDE.md` § Traceability (at `0a833b9f7`); `CLAUDE.md:11` "Registered locations are cited under MR-4" (fusion-tea branch `research-seam-port` at `940500788`) | O1 branch diff |
| Script paths and `uv run python scripts/…` snippets | command `:9-10,28-103`; guide passim | `CLAUDE.md:11` (fusion-tea branch `research-seam-port` at `940500788`): the `agentic-mbse research` subcommands and the installed guide replace the scripts | O1 branch diff |
| Hold-out route via PROTOCOL §6, and the example rule id `term:aries-cs` | guide `:191-193`, `:274` | `CLAUDE.md:11` (fusion-tea branch `research-seam-port` at `940500788`); `scripts/holdout_guard.py:9-10` (at `0a833b9f7`) | O1 branch diff |
| The term list as the blind spot (ARIES-CS, the program's old host, the four sealed stems) | guide `:247-251` | `scripts/holdout_guard.py:26-35` (at `0a833b9f7`); `CLAUDE.md:11` "a term scan that misses barred content which never names a barred term" (fusion-tea branch `research-seam-port` at `940500788`) | O1 branch diff |
| The `--local-pdf` breaking change of `zotero_ingest.py` | guide `:30-32` | `scripts/zotero_ingest.py` `process_local_pdf` docstring (at `0a833b9f7`) | snapshot `zotero_ingest.py:567-573` |
| "Three legacy entries" and the WI-031 sources | guide `:239` | `knowledge/.registry_baseline.json` (at `0a833b9f7`) | O1 `verify` output (`research-seam-port/evidence/o1-parity-early.md`) |
| The pointer to the test suite's loopback server (`tests/research/conftest.py` over `tests/research/fixtures/web/`) | guide `:69` | Not needed in fusion-tea: the fixture moved to agentic-mbse `tests/test_research/conftest.py` (`local_site`) and `tests/test_research/fixtures/web/`; the shipped guide tells a target to serve its own page | this branch, P1 |
| Design-record and requirement pointers: the seam design's D1–D14, T-010 R1–R5, the guide's `R-D5`/`R-D6`, and the scripts' inline `R-*`, `audit F*` and `WI-033` ids | script docstrings `research_seam.py:13`, `source_registry.py:23-24` and inline comments; guide `:144` | The completed seam spec and design (`.project/completed/20260827_goal-research-seam/`, at `0a833b9f7`); fusion-tea git history of the deleted scripts | at `0a833b9f7` |
| `ZoteroSource` and its rationale (an unattended batch has no per-item prose) | `source_registry.py:127-160` | `scripts/zotero_ingest.py` `process_zotero_item` docstring (fusion-tea branch `research-seam-port` at `940500788`); the package's `KeyedFileSource` carries the general form | O1 branch diff |
| ADR-0008's Zotero-specific wording, its `.project/` citations and the WI-031 example | `.project/adr/0008-source-identity-raw-bytes-sha256.md` | Stays live in fusion-tea, with a dated amendment line saying the installed `agentic_mbse.research` now holds its invariants (fusion-tea branch `research-seam-port` at `940500788`). The shipped `docs/research-seam.md` § Decisions is a 2026-10-12 condensation of record 0008 at `0a833b9f7` | O1 branch diff |
| Upstream filings section | guide `:282-287` | Not needed in fusion-tea: both items are agentic-mbse backlog entries. The shipped guide drops the closed `PM-APPROVE-RESEARCH-EMPTY-INSIGHTS` bullet and describes the open capture gaps in words (§ Known capture gaps) | agentic-mbse `.project/backlog/BACKLOG.md:100` (`EXTRACT-PROVENANCE-HOOK`, open) and `:735` (`PM-APPROVE-RESEARCH-EMPTY-INSIGHTS`, completed) |
