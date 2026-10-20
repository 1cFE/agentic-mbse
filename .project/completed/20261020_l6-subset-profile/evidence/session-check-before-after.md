# Before/after: `validate --complete models`, base vs branch

Written by `scripts/l6_subset/run_consumers.py before-after --base ebb3d467 --branch HEAD`. Base `ebb3d46710a4c1476bb12fa0e9decf0088ddb2c5`, branch `00adb1024f5d2e7bbf06e97e44d23183a3891d26`; SysIDE 0.8.4. Each tree and each code revision is a `git archive` export under /tmp; target unset; runs one at a time. Sibling checkouts unchanged: True.

## Flags

None. No level or run goes from pass to fail, L1-L5 print identically, and the time criterion holds.

## Per tree

| Tree | Exit base -> branch | Wall time base -> branch (s) | Ratio | L1 | L2 | L3 | L4 | L5 | L6 |
|---|---|---|---|---|---|---|---|---|---|
| fusion-tea | 1 -> 1 | 411.4 -> 206.0 | 0.501 | passed -> passed | failed -> failed | passed -> passed | passed -> passed | passed -> passed | failed -> failed |

Time criterion: fusion-tea branch time at most 1.1 x base.
