Review `.project/active/l6-subset-profile/design.md` — design for EXEC-SUBSET-CONTRACT Item 3 — against `spec.md` (with `spec-review.md` Resolutions), `briefs/align.md` (owner decisions; gate outcomes; owner boundary: no Item 2, no sysml-codegen writes), and the epic's Item 3. Read-only: ~/src/dc3, ~/src/fusion-tea.

Intent [AGENT, ratified by owner 2026-10-18]: `validate` reports the Item 1 contract with the project's `execution-target` deciding severity (unset = warnings, `native` = info, `generated` = errors for refusals), never claims "will generate", and never lets a broken check pass; String omissions warn in both forms; `L6_CONSTRAINT_MALFORMED_NUMERICAL` is kept unchanged.

Review hard on: the severity table against the owner decisions and gate outcomes (every cell); whether any legacy check is silently relaxed beyond the gate outcomes; the settings module and its interaction with the research holdout guard; `init`'s text-insert-and-reparse approach and its refuse cases; the runner crash handling and JSON report; the "shadowed by" correction; reuse of Item 1 rather than re-deriving decisions; test strategy; spec traceability.

A spike (contract on real trees, advisory shapes, String ID match, codegen citations) runs in parallel; don't duplicate it. Do not edit the design. Produce the review artifact with verdict and must-fix / should-fix items.
