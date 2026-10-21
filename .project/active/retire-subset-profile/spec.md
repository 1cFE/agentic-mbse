# Spec: Retire the copied generator rules; guidance plus an early `sysml-codegen check`

**Status:** Approved by owner 2026-10-21 ("Ok go with your recommendation. implement it, and document it")
**Created:** 2026-10-21
**Repos:** agentic-mbse branch `retire-subset-profile` (worktree `/home/reid/src/subset-conformance/agentic-mbse`, base `main` `e268357f`); sysml-codegen branch `subset-profile-screen` (worktree `/home/reid/src/subset-conformance/sysml-codegen`, Item 2b)
**Design:** the architecture review in sysml-codegen `.project/active/subset-profile-screen/architecture-review/` (`index.html`, published at https://claude.ai/artifact/6FtNpSZ3N1conDFWbR8Zsv; agent reports `01-current-system.md`, `02-alternatives.md`, `03-challenge.md`). Scope inventory: [scope-report.md](scope-report.md), [codegen-part.md](codegen-part.md), [consumers-part.md](consumers-part.md).

## The point

The only thing that ever says "this model won't generate" is the generator. Modellers avoid the expensive structural mistakes because the shipped guidance states the generator's structural limits up front, and the modelling workflow runs the generator's no-write check (`sysml-codegen check`) early and at each phase when a project targets generated code. The hand-written copy of the generator's refusal rules in agentic-mbse (EXEC-SUBSET-CONTRACT Item 1, the "subset profile") is deleted, with the tests that kept it agreeing with the generator.

Why: the copy is silent on 129 of the 169 refused test models, needs a two-repo change whenever the generator's refusals move, and would tell modellers to rewrite working models once either held generator change (`CALCDEF-GATE-IMPLEMENTATION`, `SCALAR-FUNCTION-VOCABULARY`) lands. It existed only so L6 could answer without the generator installed, and a project that cares whether it generates has the generator installed.

## Requirements

- **R1** [NEED] The copy is retired: `subset_profile.py` and its TOML, `subset_facts`, `subset_extraction`, `occurrence_extraction`, `occurrence_facts`, `subset_coverage`, `subset_advisories`, `conformance_case` and `subset_cases/`, `validation/subset_presentation.py`, their tests, fixtures, helpers, scripts and the pre-merge gate. Source: owner approval of recommendation step 4, 2026-10-21.
- **R2** [NEED] `sysml-codegen generate` and `check` no longer run or print the copy's findings. `check` reports only the generator's answer and writes nothing. Source: recommendation step 1.
- **R3** [NEED] The shipped guidance states three structural limits: an `assert constraint` goes on a part, not inside a calculation; part multiplicities are exact; calculation inputs are single values, not sequences. Shipped examples that teach a refused pattern are corrected. Source: recommendation step 2.
- **R4** [NEED] When a project targets generated code, the modelling workflow runs `sysml-codegen check` as soon as the first model pieces exist and again at each phase, and treats its answer as the generation answer. Source: recommendation step 3.
- **R5** [INFERRED, owner-assumption stated in chat 2026-10-21, not contradicted] A project that has parked generation still runs `check` once early; the result is recorded and does not block.
- **R6** [INFERRED] Nothing the generator builds or refuses changes (RG-1). Byte identity of generated packages and identity of refusal records hold against the Item 2b baseline.
- **R7** [INFERRED] The Item 4 positional-binding check (L2_POSITIONAL_BINDING) behaves exactly as before; the helpers it borrows from the copy move first.
- **R8** [INFERRED] The generator regression assets built by Item 2a stay in sysml-codegen: stable refusal reasons (`SiteReason`), the refusal site account and its scan tests, the 246 case models with their generator answers, generator mutations, refusal records. The 154 case models that live in agentic-mbse move into sysml-codegen first.
- **R9** [NEED] The decision is documented: a new ADR supersedes ADR 0001; ADR 0003 and the product promises P-0001 and P-0003 are amended to match; the EXEC-SUBSET-CONTRACT epic's remaining items (5, 6) are rewritten for the new design; shipped docs (README, CLAUDE.md, model-validation skill) stop describing the copy. Source: "document it", 2026-10-21.

## Decisions taken here (agent-grade, recorded for challenge)

- **D-a** Keep the `[tool.agentic-mbse] execution-target` setting (ADR 0003). With the copy gone it does two things: under `native` it still folds the 4 legacy generator-only L6 codes into the INFO summary, as today; and it is how the workflow skills know a project targets generated code, so they run `check`. Reason: the design page kept it, it is already shipped and written by `init`, and dropping it would remove the workflow's trigger.
- **D-b** The two L6 advisories (opaque expression, sum wrapper; `subset_advisories.py`) retire with the copy. They walk the copy's extraction and report generator-support guesses, which is the copy's job.
- **D-c** L6's String-subject suppression goes with the copy, so the pre-Item-3 `L6_DESIGN_ATTR_UNEXTRACTABLE` reports for String values come back, as they did whenever the contract did not run (Item 3 design D10). Not a new behaviour.
- **D-d** Whether an attribute-valued multiplicity (`[N]`, `[child_count]`) counts as exact is settled by running `sysml-codegen check` on a probe model, and the guidance says what the generator does.
- **D-e** sysml-codegen PR #21 (ADR 0018, occurrence summary shared with agentic-mbse) is moot; closing it is the owner's (RG-3).

## Out of scope

- Any change to what the generator accepts or refuses (RG-1), including the two held generator changes.
- An L6 runner that calls `sysml-codegen check` (option C), a supported Python checker function (option D), and listing every problem per step (option E1). Out because the design page made them optional, to do only if a need shows up.
- Merges, PRs, close and pre_pr (RG-3).

## Acceptance

- agentic-mbse and sysml-codegen suites pass apart from the failures recorded on their bases (sysml-codegen: 9 base failures).
- sysml-codegen byte identity: 0 of 123 packages differ; refusal records: identical to the Item 2b HEAD baseline. TEAx 124 of 124.
- No file in either repo imports a retired module; `git grep` for the retired module names finds only history (archives, completed items, changelog).
- dc3's models: `sysml-codegen check` on dc3 gives the same answer before and after.
- A fresh-agent audit of both branches finds no blocker.
