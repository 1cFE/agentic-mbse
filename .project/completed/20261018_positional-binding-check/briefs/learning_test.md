Learning test for EXEC-SUBSET-CONTRACT Item 4. Read the de-risk flags R1–R6 in `.project/active/positional-binding-check/design.md` (and the sections they cite), plus the spec's fixture expectations.

Map how SysIDE 0.8.4's Python API (the version this repo pins; license key in `.env`) surfaces calc/constraint input redefinitions. Write **kept** learning tests under `tests/learning/` (follow any existing convention there; otherwise create `tests/learning/test_syside_input_redefinition.py`) that pin the observed behavior, so a SysIDE upgrade that changes it fails loudly.

Must answer, with a test per question:
- **R1:** in `in b = 3; in :>> a = 10;` against a calc def with formals `a, b` (in that order), does `b` carry an implied redefinition of the def's `a`? What does `:>> a` carry? Also the reversed fully-implicit case and the reversed fully-explicit case (epic Item 4 scope 3 values).
- **R2:** can `subject`, `actor` and `stakeholder` parameters be distinguished by membership type (or another API property), and does a requirement's subject count toward the positions of its other `in` parameters?
- **R3–R6** as the design lists them (multiple typings, `out` before `in`, anonymous and inherited inputs, owner enumeration and the library flag). Record what you observe even where the rule tolerates either answer.

Rules: no changes to `src/`. Don't modify ~/src/sysml-codegen, ~/src/dc3 or ~/src/fusion-tea. Record findings in `.project/active/positional-binding-check/learning-findings.md`, stating per flag: observed behavior, the test that pins it, and whether it confirms or contradicts the design/spec. If R1 contradicts the spec's mixed-spelling criterion, say so plainly as a premise surprise; do not propose a name-based workaround. The new tests must pass and be ruff/mypy clean. Commit with an outcome-led subject ending `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. End with the ARTIFACT line (the findings file).
