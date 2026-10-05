Revise `design.md` to incorporate the design review at `.project/active/pm-registry-integrity/design-review.md`. Its Resolutions section records the orchestrator's call on every finding: all accepted, with M4 taking both fixes (reject duplicate top-level keys; only an unindented `---` closes the frontmatter). Apply M1 to M4, m1 to m6, and the n-series where they are text edits. Do not reopen D8; the reviewer endorsed it.

Specifics to land:
- M1: exactly-one-match-or-refuse for `add-item --epic`, `update-validation`, and `add-epic`'s duplicate check, against the file not parsed data. Say where the check lives so there is one implementation, not three.
- M2: the escape helper refuses `<!--` and `-->` alongside line breaks; the refusal message says what to change.
- M3: boundary `(?<![A-Za-z0-9])PREFIX-(\d+)(?!\d)`; extend Appendix A with `DI-001-DI-014`, and keep `SV-034-x` → 34 and `MAG-001` ≠ `G-001`.
- M4: both fixes, as refusals before any file is touched, listed in D9 so D9 names every refusal case in one place.
- m1: fix the E2 wording for DI and AD.
- m2: `register_intent` checks every target section before its first write.
- Update the Validation Approach so each new refusal and the boundary cases have a named test.

Keep the design's length under control: amend in place, do not append a changelog. End with `ARTIFACT: .project/active/pm-registry-integrity/design.md`.
