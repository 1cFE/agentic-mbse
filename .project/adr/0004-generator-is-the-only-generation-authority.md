---
id: 0004
title: The generator is the only authority on whether a model generates; agentic-mbse keeps no copy of its refusal rules
date: 2026-10-21
owner: Reid Westwood
status: amended
amended_by: [0006]
superseded_by: null
provenance: "[AGENT] (ratified by owner, 2026-10-21)"
seams: [agentic-mbse, sysml-codegen, l6, guidance, modelling-workflow]
supersedes: 0001
promoted_to: null
---

## Decision

Only sysml-codegen says whether a model generates: `sysml-codegen generate`, or its no-write check `sysml-codegen check`. agentic-mbse keeps no copy of the generator's refusal rules. Instead, the shipped guidance states the generator's three structural limits up front, and the modelling workflow runs `sysml-codegen check` early and at each phase when a project targets generated code. The hand-written copy (EXEC-SUBSET-CONTRACT Item 1, the "subset profile") is deleted, with the tests that kept it agreeing with the generator.

The owner approved this on 2026-10-21 ("Ok go with your recommendation. implement it, and document it."). The recommendation was section 6 of the architecture review, so the decision is agent-originated and owner-ratified, not owner-originated.

## Context

- **What happened in dc3.** dc3 built and reviewed its models for about ten days with generation deliberately parked (owner amendment, 2026-10-05). When `generate` first ran on 2026-10-13 it refused, one problem per run. Three of the problems (an assert inside a calculation, a sequence calculation input, an open part count) were built into the model's structure, so the fix meant reworking reviewed models.
- **Why the copy was built.** The epic's opening framing was "L6 reports that contract without depending on codegen". agentic-mbse cannot import sysml-codegen, because sysml-codegen already imports agentic-mbse. So Item 1 wrote nine refusal rules and ported part of the generator's part-tree code into agentic-mbse (about 5,600 lines), and Item 2a built tests in sysml-codegen to keep the two agreeing.
- **The premise nobody examined.** Running the generator as a separate command is not an import, so it was always allowed. No design weighed "no copy at all". ADR 0001 records the owner's choice "A (ii)" on 2026-10-18, but that was a choice between ownership options for the copy (who owns it, and how the ported part tree stays in step). Not having a copy was never one of the options offered. That is why this entry supersedes ADR 0001 rather than reversing an owner call.

## Why

- **The copy is often silent.** On the 246 test models, the generator refuses 169 and the copy says nothing about 129 of them. It never reported a refusal for a model the generator builds, though it did report omissions on models that build (see Consequences). Its silence was read as "fine".
- **It goes wrong when the generator improves.** Two held generator changes (`CALCDEF-GATE-IMPLEMENTATION`, `SCALAR-FUNCTION-VOCABULARY`) would make its rules say "refused" for models the generator then builds, and modellers would rewrite working models.
- **It costs a two-repository change** every time a generator refusal is added or moved.
- **Its one unique benefit was answering without the generator installed.** A project that cares whether its model generates installs the generator to generate; dc3 and fusion-tea both have it.
- **The expensive dc3 mistakes are preventable by guidance.** Three statements (an assert goes on a part, part counts are exact, a calculation input receives one value) would have stopped B1-B3 being built. The early check catches what guidance misses while the model is still small.
- **The incident was small in the record.** About 20 minutes of agent inventory and about 80 minutes of rework (dc3 commits from 20:47 to 22:06 UTC on 2026-10-13, `7fb0cd9` to `be457a4`; architecture review `01-current-system.md`, `03-challenge.md` § 1), plus the loss of dc3's stop-on-failure guards on the generated path. The fix is sized to that.

Two assumptions sit under this decision. Both were stated to the owner on 2026-10-21 and not contradicted; neither is an owner statement. (1) A project that has parked generation still runs `check` once early, records the result, and is not blocked by it. (2) The dc3 incident cost the owner little time. If (2) is wrong, seeing every structural problem in one run is worth more, and keeping the three structural rules becomes the better answer.

## Consequences

- **Deleted in agentic-mbse:** the subset profile and its rules TOML, the fact extraction and occurrence port it needed, the coverage statement, the two L6 advisories, the conformance-case format and the 154 packaged cases (moved to sysml-codegen first), L6's presentation of the copy's findings, and their tests, scripts and pre-merge gate (spec R1).
- **Deleted in sysml-codegen:** the step that printed the copy's findings after `generate` and `check` (Item 2b's screen step), and the tests that compared the copy with the generator (Item 2a's agreement half).
- **Kept:** `sysml-codegen check` and the load / check / write split from Item 2b; the generator's stable refusal reasons, its refusal site account and the 246 case models as generator regression tests (Item 2a's generator half); the `execution-target` setting (ADR 0005); Item 4's positional-binding check, whose helpers move out of the copy first.
- **What the workflow does now:** `MODELING_PROCESS.md` and the design, plan, implement, model-validation and toolkit-awareness skills run `sysml-codegen check --models <path>` when the first model pieces exist, at each phase, and before any claim that the model generates. Its exit code is the generation answer. A missing generator is reported as "not checked", never as fine.
- **The cost:** structural problems are found one generator step at a time, cheaper problems first, because the generator stops after its first failing step. The bet is that the guidance stops modellers building the structural ones in the first place. dc3 is the only incident, so there is no evidence yet either way.
- **Silent losses no longer reported:** the copy also reported things the generator silently drops from models it builds: String values, and calculation usages' result expressions (`check` exits 0 on both). Nothing reports these now, apart from L6's `L6_DESIGN_ATTR_UNEXTRACTABLE` for attributes under `designs/`. What to do about String values is the owner's open RG-2 question; both losses are recorded in sysml-codegen `.project/backlog/BACKLOG.md`.
- **Optional, only if a need shows up:** L6 running `check` as a separate command (option C), a supported Python checker function (option D), and the generator listing every problem within its expression step (option E1, step 1 only).

## Invariants established

1. agentic-mbse keeps no copy of the generator's refusal rules and makes no generation claim. L6 keeps a few legacy convention checks that overlap generator behaviour (such as `L6_ANONYMOUS_RETURN` and `L6_ATTR_REDEF_EXPR_DROPPED`, and the four codes folded under `native`); they are conventions, not a prediction of what the generator does. A generation answer comes from running sysml-codegen.
2. No agentic-mbse module imports sysml-codegen (unchanged from ADR 0001 invariant 3).
3. A missing or failed generator run means "generation not checked", never "generates".

## Rejected alternatives

The options weighed, from the architecture review (sysml-codegen `.project/research/2026-10-21-generator-check-architecture-review/index.html` § 5, published at https://claude.ai/artifact/6FtNpSZ3N1conDFWbR8Zsv; reports `01-current-system.md`, `02-alternatives.md`, `03-challenge.md` beside it). Day figures are agent estimates, plus or minus 50%.

- **A. Keep everything as built:** not chosen; high two-repository upkeep, silent on 129 of 169 refusals, and wrong once a held generator change lands.
- **B. Copy stays in L6, out of `generate` and `check`:** not chosen as a design, because it keeps A's upkeep. Its one change, taking the copy out of `check`, is part of this decision.
- **C. L6 runs `sysml-codegen check` as a separate command:** not chosen now. It adds a runner and machine-readable output (3-5 days) to show the answer the workflow already gets from `check`. Optional later if modellers skip the workflow step.
- **D. A supported Python checker function in sysml-codegen:** not chosen now. L6 cannot use it, and no project has asked for a "this model generates" test. Optional later.
- **E1. Generator lists every problem within a step:** not chosen as the fix. Measured on dc3, it still shows the structural problems last, after four or more runs (8-12 days for every step). Step 1 alone (half a day) stays optional.
- **E2. Generator continues past failed steps:** rejected. It cannot be explained simply, and it risks false errors across about 4,000 lines of the generator's core (15+ days).
- **F. Generate the copy from the generator's code:** rejected. Only names and fix texts can be generated, not the checks.
- **G. Guidance plus an early `check` in the workflow:** chosen, with the copy retired.
- **H. Move the generator's checks into agentic-mbse:** rejected. 25-40 days at the highest risk, and the 33 generator-only checks could not move, so L6 would still be incomplete. It would be right only if a generation answer were needed without the generator installed, and no such case is known.
- **Keep only the three structural rules:** not chosen. It still needs the ported part tree and agreement tests, so most of the upkeep remains for a third of the coverage.

Evidence: spec `.project/completed/20261022_retire-subset-profile/spec.md`; guidance probes `.project/completed/20261022_retire-subset-profile/evidence/probes.md`.
