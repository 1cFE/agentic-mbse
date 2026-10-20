# Before/after: `validate --complete models`, base vs branch

Written by `scripts/l6_subset/run_consumers.py before-after --base ebb3d467 --branch HEAD`. Base `ebb3d46710a4c1476bb12fa0e9decf0088ddb2c5`, branch `41b14ca957a154821e76f595b8ff5a939037b18d`; SysIDE 0.8.4. Each tree and each code revision is a `git archive` export under one /tmp directory; target unset; runs one at a time. The base side is read from its text output, the branch side from its `--json-report`. Sibling checkouts unchanged: True.

## Flags (stop-and-show)

None. No level or run goes from pass to fail, L1-L5 print identically, every run resolved the expected project root, each branch run extracted constraints once, and the time criterion holds.

## Per tree

Each level cell is `status before -> after (issues before -> after)`.

| Tree | Exit | Wall time (s) | Ratio | L1 | L2 | L3 | L4 | L5 | L6 |
|---|---|---|---|---|---|---|---|---|---|
| fusion-tea | 1 -> 1 | 412.7 -> 212.0 | 0.514 | passed -> passed (0 -> 0) | failed -> failed (465 -> 465) | passed -> passed (0 -> 0) | passed -> passed (0 -> 0) | passed -> passed (0 -> 0) | failed -> failed (408 -> 539, text differs) |
| dc3-baseline | 1 -> 1 | 35.0 -> 18.1 | 0.517 | passed -> passed (0 -> 0) | passed -> passed (0 -> 0) | passed -> passed (0 -> 0) | passed -> passed (0 -> 0) | passed -> passed (0 -> 0) | failed -> failed (11 -> 332, text differs) |
| dc3-repaired | 0 -> 0 | 25.6 -> 13.3 | 0.52 | passed -> passed (0 -> 0) | passed -> passed (0 -> 0) | passed -> passed (0 -> 0) | passed -> passed (0 -> 0) | passed -> passed (0 -> 0) | passed -> passed (0 -> 30, text differs) |

Time criterion: fusion-tea branch time at most 1.1 x base. L6's text differs by design (new title, contract lines), so only L1-L5 text is compared.

## Resolved project root

| Tree | Settings input (step 5) | Base (L2 pin list) | Branch (L2 pin list) | Branch (L6 execution target) | Constraint extractions (branch) |
|---|---|---|---|---|---|
| fusion-tea | root `fusion-tea`, `fusion-tea/pyproject.toml`, tables {"agentic-mbse": "absent", "agentic_mbse": "absent"} | `trees/fusion-tea` | `trees/fusion-tea` | `trees/fusion-tea` | 1 |
| dc3-baseline | root `dc3-baseline`, `dc3-baseline/pyproject.toml`, tables {"agentic-mbse": "absent", "agentic_mbse": "absent"} | `trees/dc3-baseline` | `trees/dc3-baseline` | `trees/dc3-baseline` | 1 |
| dc3-repaired | root `dc3-repaired`, `dc3-repaired/pyproject.toml`, tables {"agentic-mbse": "absent", "agentic_mbse": "absent"} | `trees/dc3-repaired` | `trees/dc3-repaired` | `trees/dc3-repaired` | 1 |

## Expected L6 changes (step 11, not a stop)

| Tree | New `L6_SUBSET_OMITTED` WARNINGs (expected) | `L6_DESIGN_ATTR_UNEXTRACTABLE` before -> after (expected) | Branch pass notes |
|---|---|---|---|
| fusion-tea | 131 (131) | 108 -> 108 (108 -> 108) | none |
| dc3-baseline | 32 (32) | 3 -> 0 (3 -> 0) | none |
| dc3-repaired | 30 (30) | 0 -> 0 (0 -> 0) | generated compatibility not established |

UNEXTRACTABLE after is the report's issue count, shown and summarized, after the String suppression (design D10). The printed metric after is in the next table.

## Legacy L6 counts that changed

Both sides are the legacy count metrics L6 prints (`<CODE>: N`), so each pair counts the same thing. `None` means the side prints no such metric.

- fusion-tea: none
- dc3-baseline: `L6_DESIGN_ATTR_UNEXTRACTABLE` 3 -> 0
- dc3-repaired: none

## Branch L6 issue codes by display

- fusion-tea: `L6_DESIGN_ATTR_INCOMPLETE (error)` 119, `L6_DESIGN_ATTR_UNEXTRACTABLE (error)` 108, `L6_SUBSET_OMITTED (warning)` 131, `V2_DYNAMIC_EXPRESSION (error)` 96, `V4_UNSUPPORTED_OPERATOR (error)` 85
- dc3-baseline: `L6_CONSTRAINT_MALFORMED_NUMERICAL (error)` 4, `L6_CONSTRAINT_NON_NUMERICAL (warning)` 4, `L6_SUBSET_OMITTED (warning)` 32, `L6_SUBSET_REFUSED (warning)` 236, `L6_SUBSET_UNCONFIRMED (warning)` 6, `L6_SUBSET_UNVERIFIED (warning)` 50
- dc3-repaired: `L6_SUBSET_OMITTED (warning)` 30
