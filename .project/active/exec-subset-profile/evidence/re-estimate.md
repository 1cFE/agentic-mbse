# Re-estimate: EXEC-SUBSET-CONTRACT Items 1 and 2

**Status:** `[AGENT]` estimate, recorded at Item 1's close-out (2026-10-18), as the epic requires after the inventory. The epic's original ~10-day figure covered all six items and excluded snapshot integration, occurrence-aware evidence and independent differential coverage; the epic says not to use it as a constraint. Units are focused engineer-days (one person who knows the codebase), not calendar days.

## The basis

What Item 1 measured, which the estimate leans on:

- **Size of the surface.** 502 candidate sites (441 codegen, 61 agentic-mbse). 42 are in scope, 375 handled elsewhere, 85 explicit follow-ups (39 public capability, 46 unknown role). 154 are internal invariants with a cited guard. (After audit A9 re-classified three rows; before: 44 / 376 / 82, 155 invariants. The estimate is unchanged by three rows.)
- **Evidence cost.** 80 probes (62 record, 12 control, 6 reproduction). A full probe run takes under ten minutes in an isolated tree; codegen's suite about two minutes plus sync. Probing is cheap; deciding contexts is not.
- **Occurrence port.** 725 lines in production (`occurrence_extraction.py`), above the spike's ~600 estimate. Parity held at 73/73 from its first run to the final revision.
- **Item 1 actuals.** Spec, design and spike on 2026-10-15; plan and all eleven phases on 2026-10-18, agent-implemented. 38 commits on the branch since the design base, about 22,700 lines across `src/`, `tests/` and `scripts/` (most of it probe fixtures, observations and the account). Agent wall-clock is not a reliable guide to human effort, so the figure below is an engineer-day judgment of the same work.

## Item 1

| Part | Estimate |
|---|---|
| Done: facts, port, evaluator, records, 80 probes, matrix, site account, acceptance runs, close-out drafts | ~12-15 engineer-days of equivalent work |
| Left: `/_my_audit`, owner review of R3 and of the open acceptance items (dc3 baseline INCOMPLETE, B8 unconfirmed, the `sump_pump` nondeterminism), `/_my_close` | ~1-2 days, plus owner time |

The epic gave Item 1 no number ("re-estimate after inventory"). The large items were the ones the design predicted: about 70 probes (80 in the end) and about 500 site rows (502).

## Item 2 (sysml-codegen): independent conformance and read-only readiness

| Work | Basis | Estimate (days) |
|---|---|---|
| Permanent parity CI test (end condition (ii)): run agentic-mbse's occurrence summary against codegen's index on the 34-case seed plus the corpus in codegen CI; fail on any difference | The comparison and normalizer exist (`occurrence_parity.py`, `tests/helpers/occurrence_oracle_schema.py`); they move into codegen's test tree and CI | 1.5-2.5 |
| File the ADR 0012 amendment | Ready-to-file draft (`adr-0012-amendment-draft.md`) | 0.25 |
| Code mapping: neutral reason IDs → `ElaborationCode`, and codegen adopting the contract where facts exist before elaboration | 16 subset reasons; mapping is one-to-many by design | 1.5-2.5 |
| Screen-bypassing independent corpus (`tests/conformance/subset_profile/`): each refusal condition, admitted near-neighbors, inherited and redefined contexts, templates vs instances, dc3 proto shapes | 80 Item 1 probes are a seed, but they run through the public CLI, not with the screen bypassed; each needs a conformance-test form | 4-6 |
| Per-site stable codes and mutation tests | 44 in-scope sites plus the 37 public-capability follow-ups need stable codes; 45 unknown-role sites need a reachability verdict; each relevant condition needs a witness and a detector-disable mutation | 6-9 |
| The gaps R3 proposes for Item 2 | ES-002, ES-008, ES-009, ES-010 refusal side, ES-011 reproduce-or-retire, calc-def bare result, calc-usage silent drop, unconfirmed-pair probes | 3-5 |
| G1 / G2 generator-correctness questions | Two owner decisions; G2 needs a probe first; any fix changes codegen behavior and the contract together | 1-2 + owner |
| Read-only preparation path for `generate` and `check` (epic Item 2 scope 4) and snapshot-authority integration (scope 5) | Not measured by Item 1; carried from the epic's scope with no new evidence | 6-10 |
| **Item 2 total** | | **~23-37** |

The range is wide for two reasons, both stated rather than averaged away:

- **The unknown-role sites.** 45 sites could not be settled from the code. Each one that turns out reachable by valid input adds a code, a witness and a mutation test.
- **Scopes 4 and 5** (preparation path, snapshot authority) are the epic's, unexamined by Item 1. They are the least certain third of the estimate.

## What would change this

- If the owner retires the G1/G2 questions or the `nonunique`/negative-bound shapes, about 1-2 days come off Item 2.
- If the owner moves the read-only preparation path out of Item 2, the total drops to ~17-27.
- If Item 2's per-site work finds many of the 155 internal-invariant guards weaker than cited, the per-site line grows.
