# Brief: /_my_design_review — goal-layer-port (`WRAP-SPLIT` Item 2)

Review `.project/active/goal-layer-port/design.md` as a fresh, independent reviewer. You did not write it. Write your review to `.project/active/goal-layer-port/design-review.md`. Do not edit the design and do not commit. Start no background tasks. End with `ARTIFACT: <path>`.

Context: `spec.md`, `spec-review.md` (with its Resolutions), `briefs/align.md`, `briefs/design.md`, all beside the design. fusion-tea files are in the read-only snapshot `.orchestrate-logs/fusion-tea-snapshot/` (fusion-tea commit `2b1e9f9d5`); you cannot read `/home/reid/1cfe/fusion-tea`.

This review also discharges SC6's "fresh reviewer's check of the shipped wording against MR-7" (Align record, "Reserved gates"). Do that check explicitly and record it in its own section.

Weigh these hardest, in order:

1. **Does the rule read as one of agentic-mbse's own patterns?** The owner's direction ([OWNER-VERBATIM] 2026-10-11): "it is important that you find the right level for this rule -- we have specific patterns which agentic-mbse is supposed to enforce, this should fit into that". Compare Appendix A1 (`design-choices.md`) and A2–A5 against the existing pattern docs (`docs/patterns/README.md`, `adr002-calculations.md`, `constraints.md` Equality intent, `plant-idiom.md`) and the existing rows of `project_templates/MODELING_PROCESS.md.template`. Is the placement right, is anything over-spread (the trigger condition appears in Process Selection, the runbook trigger table and the pattern's Review section: is that routing or a second statement?), is anything missing?
2. **Wording against MR-7.** Sentence by sentence against fusion-tea `modeling_project/REQUIREMENTS.md:87-107` and fusion-tea `modeling_project/MODELING_PROCESS.md:17,34`: is every general obligation kept at its force, is nothing fusion-specific presented as general, and does the A6 MR-7 rewrite plus A7 keep everything fusion-tea needs? Check the grade stanza (A1 "Authority") against capture-fidelity: nothing beyond the principle presented as owner-originated.
3. **Port fidelity.** Do the Appendix B classes and A8 hooks keep the runbook's method? Spot-check against the snapshot runbook and skills. Would any change alter what a goal agent does?
4. **fusion-tea sequencing and the installer.** Do F1/F2 (Appendix D) keep fusion-tea whole at every merge point? Do the installer facts the design relies on hold in `src/agentic_mbse/cli/installation.py` and `cli/__init__.py`? Is the contract test (D9) sound under plain and `--dev` installs?
5. **Feasibility and checkability.** Can the plan execute this, and can an auditor verify each SC? Is the SC4 dry run (D16 seed, operator stand-in) runnable as designed?

Grade each finding must-fix or advisory, with a file:line basis. Keep the review short and plain.
