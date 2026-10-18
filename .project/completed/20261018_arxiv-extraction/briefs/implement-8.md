Audit round 2 (audit.md "Round 2") clears the code. Final fixes:
1. The three doc sentences it lists (docs/extraction-internals.md:306 and :316, docs/extraction.md:107) must match the code: in-article data: images are saved under images/ when an images directory is set and stay inline otherwise; selection removes LaTeXML listing download buttons and nothing else.
2. Add one line to spec R4 naming the listing-button removal, graded [INFERRED] (orchestrator call, 2026-10-18; owner has not ruled).
3. Audit suggestion 2: a test on the real fixture's converted output asserting no `data:` link of any media type remains when an images dir is set (so a LaTeXML markup change can't silently bring the listing copies back).
Leave suggestion 3 as is. Commit (decision-led subject, Co-Authored-By line), note in Post-audit fixes, stop. End with ARTIFACT: <plan path>.
