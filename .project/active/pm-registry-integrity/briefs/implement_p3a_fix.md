Orchestrator decision on your two open issues:

1. **Fix it now, under R9.** A row written into a later section's table with a success message is a record-loss path, and closing those is the point of this item. The design's "keep the loop verbatim" governed the extraction mechanics, not the preservation of this bug; R9 ("a missing table under the heading refuses") is the governing rule. In `_insert_table_row`, stop the search at the next `## ` heading (or end of file) so a heading with no table under it refuses, and add the test that pins it: heading present, no table, later section has a table; the operation refuses, names the heading, and the file is unchanged. Record this in the plan's Phase 3a Completion as an R9 case and add it to the plan's R-series test table.
2. **Leave as is.** A missing `VALIDATION_MATRIX.md` or `OVERVIEW.md` raising is pre-existing, not on the design's refusal list, and not a loss path. Record it in the Completion notes as a known pre-existing behaviour so the audit sees it.

Rerun G1 to G4 and update the gate table. Do not commit. End with `ARTIFACT: .project/active/pm-registry-integrity/plan.md`.
