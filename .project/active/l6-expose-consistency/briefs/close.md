# Brief: close — l6-expose-consistency

Close the item in `.project/active/l6-expose-consistency/`. Audit verdict: certified, no blockers (`audit.md`). Consumer validation complete and recorded in `consumer-validation.md` (fusion-tea corpus diffs, work-item reruns, and an owner-run end-to-end probe through fusion-tea's CLI; all spec criteria confirmed in situ). Implementation commit: `3f442ce`. Owner has approved close and asked for it to be executed now.

## Follow-ups to file as backlog items (one line each, decision-record phrasing, P2 unless noted)

1. **Dotted-path doc rows** — `project_templates/MODELING_GUIDE.md.template:57`, `docs/patterns/adr002-calculations.md:44`, `docs/patterns/common-mistakes.md:166`, and `docs/patterns/plant-idiom.md:406-413` call part-headed / multi-hop dotted paths violations; V2, codegen, `plant-idiom.md:347`, and now L6 (design D6) accept them. Reconcile the docs with the predicate boundary. Source: design-review C1 / design D6.
2. **Validate CLI truncation** — `agentic-mbse validate` prints five issues then "and N more" even with `--verbose`; fusion-tea carried ~7700 Level 6 issues unread for months and WI-049 built its own JSON diff. Add a per-code summary and a `--json` dump. Source: consumer-validation.md.
3. **Flat-layout completeness coverage** — `check_design_attr_completeness` keeps `design_path_filter="designs"` and the CLI cannot change it, so a model set with no `designs/` directory gets "Design attrs checked: 0" silently (fusion-tea `exploration/magnet_materials/input_models`, `exploration/exchanger_architecture/thermal_requirements/input_models`). Add a CLI flag or a warning when the filter matches nothing. Source: owner probe in consumer-validation.md.
4. **FORMULA completeness** — completeness still rejects same-part FORMULA attributes that V2 accepts; path is a fail-closed predicate beside `is_expose_binding`. Source: design Non-Goals. Also note the minor cleanups the design lists (V4 duplicating V2 on non-EXPOSE chains; `in attribute x = source.y` calc-usage binding spelling getting V4 `.`; dead helpers `_get_calc_usage_names`, `_is_calc_output_reference`) as one combined low-priority item.

## Tracking constraints

- `.project/CURRENT_WORK.md`, `.project/backlog/BACKLOG.md`, `.project/active/README.md`, `.project/completed/CHANGELOG.md`, and `.project/README.md` carry the owner's uncommitted edits from today's status refresh. Edit them in place; do not revert or rewrite unrelated content. In CURRENT_WORK.md, the "Concrete remaining work" table row for L6 EXPOSE and the Active Work bullet must reflect closure; the `[AGENT]` recommendation paragraph should drop its L6 clause.
- Do not change code, tests, or docs. Do not commit; the orchestrator commits.
- Finish with the ARTIFACT line pointing at the archived item folder.
