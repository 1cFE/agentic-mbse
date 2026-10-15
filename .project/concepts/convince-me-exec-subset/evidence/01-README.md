# Claim 1 evidence: one-run screen plus differential conformance (PROTOTYPE)

Claim: a screen in agentic-mbse, using only agentic-mbse and SysIDE facts, reports every confirmed dc3 baseline category (B1–B8) in one run with locations. It is clean on the repaired tree. A differential against codegen's own route catches both a missed and an overbroad screen decision.

Everything here is throwaway prototype code. No repository source was edited.

## Environment

- Run at 2026-10-15T13:48–13:59 UTC.
- agentic-mbse `d546a00f3b26ff20aa023c8e090d7ca764a09619`. The tree is dirty only in `.project/` and `.gitignore`; no source is changed. The `.project/concepts/convince-me-exec-subset/` folder is untracked.
- sysml-codegen `b5663c07e987a892e27d21e68cec40d0656574ee`, clean. It uses editable agentic-mbse from the same checkout.
- SysIDE 0.8.4.
- dc3 trees were exported with `git archive` into the scratchpad, so no dc3 checkout was touched:
  - baseline `808464df85d50521e4fbb9ba7cceb63d382aa832`, at `…/scratchpad/dc3-base/models`;
  - repaired `60b44d53460fccd2f44811d8abfd42bc270e90b2`, at `…/scratchpad/dc3-fixed/models`.
- The scratchpad is `/tmp/claude-1000/-home-reid-src-agentic-mbse/8cecfa0f-3dca-4be9-bcbc-86b4acc4ae95/scratchpad`.

## Files

| File | What it is |
|---|---|
| `01-l6-today-base.log`, `01-l6-today-fixed.log` | Today's `agentic-mbse validate --level=6` on both trees |
| `01-codegen-today-base.log`, `01-codegen-today-fixed.log` | Today's `sysml-codegen generate` on both trees |
| `01-screen.py` | The prototype screen. It imports only agentic_mbse and syside |
| `01-screen-baseline.{log,json}`, `01-screen-repaired.{log,json}` | One screen run per tree |
| `01-independence.log` | No `sysml_codegen` import, and the module is not even installed in the agentic-mbse venv |
| `01-fixtures/*.sysml` | 22 boundary fixtures: refused cases, admitted near-neighbors, and one unmapped refusal |
| `01-codegen-oracle.py`, `01-codegen-oracle.{log,json}` | Codegen's real `generate` route per fixture, plus an omission check. Codegen has no screen today, so this is the generator with the screen bypassed |
| `01-differential.py`, `01-differential.log` | Screen versus codegen, one row per fixture |
| `01-control-missed.log` | Control run with `SCREEN_DISABLE=ES-001` |
| `01-control-overbroad.log` | Control run with `SCREEN_OVERBROAD=ES-001` (the rule also flags part-owned asserts) |
| `01-control-es003-first-cut.log` | Control run with `SCREEN_ES003_V1=1`, the first-cut B2 rule. The differential found it overbroad without any sabotage |

## Reproduce

```bash
S=/tmp/claude-1000/-home-reid-src-agentic-mbse/8cecfa0f-3dca-4be9-bcbc-86b4acc4ae95/scratchpad
E=/home/reid/src/agentic-mbse/.project/concepts/convince-me-exec-subset/evidence
cd /home/reid/src/dc3 && git archive 808464d models | tar -x -C $S/dc3-base && git archive 60b44d5 models | tar -x -C $S/dc3-fixed
cd /home/reid/src/agentic-mbse
uv run agentic-mbse validate --level=6 $S/dc3-base/models > $E/01-l6-today-base.log 2>&1
uv run python -I $E/01-screen.py $S/dc3-base/models  --json $E/01-screen-baseline.json > $E/01-screen-baseline.log
uv run python -I $E/01-screen.py $S/dc3-fixed/models --json $E/01-screen-repaired.json > $E/01-screen-repaired.log
cd /home/reid/src/sysml-codegen
uv run sysml-codegen generate --models $S/dc3-base/models --output $S/gen-out-base > $E/01-codegen-today-base.log 2>&1
uv run python $E/01-codegen-oracle.py $E/01-fixtures --json $E/01-codegen-oracle.json > $E/01-codegen-oracle.log
cd /home/reid/src/agentic-mbse
uv run python -I $E/01-differential.py > $E/01-differential.log
SCREEN_DISABLE=ES-001   uv run python -I $E/01-differential.py > $E/01-control-missed.log
SCREEN_OVERBROAD=ES-001 uv run python -I $E/01-differential.py > $E/01-control-overbroad.log
SCREEN_ES003_V1=1       uv run python -I $E/01-differential.py > $E/01-control-es003-first-cut.log
```

The differential exits 1 on any row that is not `AGREE`.

## Results

### Today versus the prototype, on the dc3 baseline

**Today, codegen stops at the first error**: `product(...)` at `path_efficiency.sysml:52`, exit 1. On the repaired tree it generates (exit 0).

**Today, L6 sees only two of the categories:**
- B7, as 3 `L6_DESIGN_ATTR_UNEXTRACTABLE`.
- B8, as 4 `MALFORMED_NUMERICAL` and 4 `NON_NUMERICAL`.
- It misses B1–B6 entirely, and it passes on the repaired tree.

**The prototype finds all categories in one run, with no rule unverified:**

| Rule | Category | Findings | Outcome |
|---|---|---|---|
| ES-001 | B1 | 164 | refused |
| ES-003 | B2 | 29 sequence arguments | refused |
| ES-004 | B3 | 15 | refused |
| ES-005 | B4/B5 | 23 (1 `product`, 22 `size`) | refused |
| ES-006 | B6 | 5 | refused |
| ES-007 | B8 | 8 (4 BLOCK, 4 excluded) | as shown |
| ES-010 | B7 | 32 | omitted |

That makes 240 blocking findings. On the repaired tree there are 0 blocking findings and 30 String omissions, which are non-blocking; codegen also drops them silently there.

### Differential

21 of 22 fixtures agree. The one disagreement is `unmapped_expression_calc_arg`: codegen refuses an arithmetic expression bound to a calc input (`in v = rate * fuel_code`) with `SI_EXPRESSION_SOURCE_UNSUPPORTED`. No B1–B8 rule covers this. The differential reports it as MISSED, which is a real gap that the end-state inventory (Item 1) must classify.

### Controls

- **Missed control.** Disabling ES-001 adds 2 MISSED rows, the calc-def and calc-usage assert fixtures.
- **Overbroad control.** Making ES-001 overbroad adds 2 OVERBROAD rows: the part-owned assert and the numeric-`and` assert.
- **Natural catch.** The first-cut B2 rule follows the epic table's wording, "ordered/nonunique parameters". Codegen admits both near-neighbors (an ordered nonunique param bound to a scalar, and an exact `[1]` ordered param), so the differential gives 2 OVERBROAD rows. The actual boundary is the sequence-valued argument `(a, b)`.

## Rules that needed new fact extraction

| Rule | Facts |
|---|---|
| ES-005 | Reuses the shared admission in `reference_use.inspect_reference_uses` |
| ES-007 | Reuses `executable_profile` through L6 `check_constraint_executability` |
| ES-001 | New: assertion owner metatype |
| ES-003 | New: comma-operator argument on a calc-usage input |
| ES-004 | New: multiplicity bounds and redefinitions. Instantiation is only approximated: a part definition counts as instantiated if any project part usage is typed by it |
| ES-006 | New: the `if` operator |
| ES-010 | New: String values in both spellings, and String referents of calc inputs |

## Limits

- The fixtures are one construct each. Codegen stops at the first error, so a combined fixture would hide later refusals.
- The ES-004 instantiation check is a heuristic. It is not the occurrence-aware evidence the epic requires.
- The omission check matches attribute leaf names in the generated text, which is a crude test.
- The differential's code mapping is hand-written here. In the end state, codegen owns that mapping.

## Audit clarification (2026-10-15)

The production L6 implementation was not replaced by this screen. Its 240 blocking findings can overlap and use an approximate part-instantiation detector; they are not 240 independently reproduced generator refusals. The repaired tree still has 30 reported String omissions. The finite differential proves disagreement detection on its 22 fixtures, not exhaustive agreement. The codegen omission oracle searches emitted text for attribute leaf names; production acceptance requires semantic presence/absence assertions. The arithmetic-actual miss is now explicitly included as ES-012 in the revised epic.
