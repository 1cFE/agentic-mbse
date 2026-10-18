# R2 items: open

**None open** as of plan Phase 7 (2026-10-18).

R2 fires when a probe shows the pinned generator admitting a (shape, context) a rule expected to refuse (plan § R2 Surfacing Map). Phases 1, 6 and 7 ran every refused probe, including the B5 variation probes, and none exited 0.

| Run | agentic-mbse revision | Probes | Certify | Refused probes admitted |
|---|---|---|---|---|
| Phase 1 smoke | `0ac48bc0` | 4 | 4 | 0 |
| Phase 6 | `47614c26` | 34 | 33 (the miss was a judge parse gap, fixed and re-run) | 0 |
| Phase 7, final set | `ecc18940` | 80 | 80 | 0 |

Every observation the records cite is from the `ecc18940` run. Phase 10 (dc3 repaired tree, corpus snapshot fixtures) is the next place R2 can fire; record any item here with the probe or run ID, the observation, the rule and the context.

The opposite direction (generator refuses where a record expected admission) is not R2. Phase 6 found one: a calc def whose result is a bare expression is refused for having no output, so `calc_result_expression` is not the admitted stub context the design assumed. It is recorded in the plan's Phase 6 completion note and stays `unconfirmed`.
