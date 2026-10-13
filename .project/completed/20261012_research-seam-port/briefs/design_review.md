# Brief: /_my_design_review — research-seam-port (`WRAP-SPLIT` Item 5)

Review `.project/active/research-seam-port/design.md` against `spec.md`, and write the review to `.project/active/research-seam-port/design-review.md`. Do not edit the design. Do not commit. Start no background tasks. End with `ARTIFACT: <path>`.

## Read

- `design.md`, `spec.md`, `briefs/align.md`, `briefs/design.md` (what the designer was told) and `product-lens.md`, all beside this brief.
- fusion-tea, read-only snapshot at `.orchestrate-logs/fusion-tea-snapshot/` (fusion-tea `0a833b9f7`). The scripts there are the behaviour this port must preserve. You cannot read `/home/reid/1cfe/fusion-tea`.
- agentic-mbse's own code where the design cites it.

## This is the only review round

The owner asked for a practical run with limited design reviews. Spend your effort where a wrong design is expensive to find later, and verify claims against the snapshot's code rather than trusting the design's line cites. In priority order:

1. **Behaviour preservation.** Is the Behaviour Changes table complete? Look for anything the twelve-module split, the comment-aware index parser (D10), the two-anchor rule (D9), the relative-path CLI (D15) or `python -m` capture (D13) would change silently for fusion-tea's existing data or callers. Check the request key, receipt, return and manifest shapes, the ladder order, and class precedence.
2. **fusion-tea switches with nothing lost.** Is the thirteen-name public API (D2) enough for `zotero_ingest.py`, `zotero_group_download.py` and `scripts/test_zotero_write_access.py`? Does `KeyedFileSource` (D6) reproduce today's `ZoteroSource` rows and index blocks byte for byte? Do the Appendix C ledger rows cover every consumer line removed from the prompt, the guide and both scripts? Does the Appendix B test split leave any behaviour untested in both repos?
3. **Hold-out hook fails closed.** D3–D5 and I4: can any path register a source unchecked when a guard is configured? Does `retire`'s use of the guard match the snapshot?
4. **`/manage-sources` meets the owner's ruling and criterion 7.** [OWNER-VERBATIM] 2026-10-09: "MORE useful as a general skill which allows direct user management while it folows and enforces the rules". Can a user do all five criterion-7 actions, and do D11's commands and B3's title addressing hold up?
5. **Plan-readiness.** Phases P1–P5 each fit one implement session. Orchestrator-run steps O1–O3 are complete enough to execute.

Do not spend effort on prose style, or on decisions the Align record settled (no spec review, the fusion-tea worktree approach, malformed requests ported as is, the class-to-outcome mapping landing here).

## Verdict

End with a verdict (APPROVE, APPROVE WITH CHANGES, or REVISE) and two lists:

- **Must-fix**: a defect that would make the build wrong, lose fusion-tea data or behaviour, or let a criterion pass while its intent fails. Give each a one-line fix.
- **Advisory**: anything else worth the plan's attention.

Keep must-fix to what is truly blocking. The orchestrator feeds must-fix items back to the designer once, and there is no second full review.
