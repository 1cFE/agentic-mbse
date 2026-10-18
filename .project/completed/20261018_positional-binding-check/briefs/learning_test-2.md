The design review (`.project/active/positional-binding-check/design-review.md`) raised two more SysIDE questions. Add kept tests to `tests/learning/test_syside_input_redefinition.py` and a section to `learning-findings.md` for each:

- **M1 (unresolved type):** a calc usage whose type does not resolve (typo in the type name; and, separately, validating a subdirectory whose definitions live outside the loaded files). Do its inputs get any implied redefinition? What diagnostics does the loader return, and are they distinguishable as "unresolved type of this owner" from the API? Same for a constraint usage.
- **M4 (requirement/case without subject):** a requirement def (and a case def) with ordinary `in` inputs and no declared `subject`/`actor`/`stakeholder`. Does the first ordinary input implicitly redefine the library's `RequirementCheck::subj` (or the case's subject)? Do the others shift? Also a requirement usage typed by such a def.

Also add the review's question on **formal ownership**: for a calc usage redefined in a subpart, what owns the formals the implied redefinitions target (definition or usage)?

Same rules as before: no `src/` changes, sibling repos read-only, tests pass and are ruff/mypy clean, commit with an outcome-led subject ending `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. State plainly whether each result confirms or contradicts the design/spec. End with the ARTIFACT line.
