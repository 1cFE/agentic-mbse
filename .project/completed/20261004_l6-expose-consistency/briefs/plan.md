# Brief: plan — l6-expose-consistency

Work item folder: `.project/active/l6-expose-consistency/`. Read `spec.md`, then `design.md` (Status: Revised, review incorporated), then skim `design-review.md` for the implementer notes the design cites. The design's Next-Stage Handoff lists what is fixed and what is open.

## Intent (orchestrator, provenance marked)

[INHERITED: spec] Make the supported-operator check and the design-attribute completeness check agree with the static-expression check on pure EXPOSE bindings, by consulting the one existing EXPOSE predicate. No widening, no new expression support.

[AGENT] The design is small and fully decided (D1–D6). The plan's job is a short, test-first sequence an implementer can execute and check off in one session, with the proof the spec demands landing as committed tests. Do not re-open design decisions; if you find one that cannot be implemented as written, say so in the plan under a clearly marked note and plan around it rather than silently changing it.

## What the plan must contain

- Phases with checkboxes, each ending in a runnable validation step (`uv run pytest <path>`), test-first: fixtures and failing tests before the production change.
- Expected shape, from the design: (1) fixtures under `tests/fixtures/l6_expose_consistency/{shapes,controls}/{library,designs}/` with the Appendix A contents verbatim, plus the new test module `tests/test_validation/test_l6_expose_consistency.py` asserting the pre-fix failure is observed, then (2) rename `_is_expose_pattern` → `is_expose_binding(attr, expr)` with the Invariant-3 docstring, drop `calc_outputs`, delete `_build_calc_output_catalog`, update `check_static_expressions` and `tests/test_sysml/test_adr002.py`, then (3) the V4 guard and the completeness guard, then (4) the full gate: `uv run pytest tests/`, `uv run ruff check src/ tests/`, `uv run ruff format --check src/ tests/`, `uv run mypy src/`.
- The exact assertions from the design's Validation Approach: shapes `issues == []`, success true, "Design attrs checked" == 3; controls `Counter` of (code, element) over every structured issue equals the 13 pairs and `len(result.issues) == 13`, with `powered`'s V4 message naming `^`; the referent through individual checks (`design_path_filter=None`, assertions scoped to `exposed_output` and `combined`) and through `validate_architecture(tmp_path)` after copying into `designs/` + `library/`; the parametrized predicate boundary test.
- A note that the full suite takes a while and that the slow corpus tests are skipped by default (see CLAUDE.md).
- Nothing about documentation changes; the dotted-path doc rows are a recorded follow-up, not this item.

Quality bar: the plan should be short. The implementer should never have to guess an assertion value or a file path. Produce `.project/active/l6-expose-consistency/plan.md`.
