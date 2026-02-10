# Fix Delene Baseline AI Artifacts

## Purpose
Clean the `delene_2001` baseline extraction which contains 25+ Claude Layer 3 hallucination artifacts (conversational text injected during failed "equation repair"), inflating the baseline character count and creating a misleading -6.2% "regression" that is actually an improvement.

## Requirements
- Remove all Claude AI conversational artifacts from the baseline `delene_2001/full_document.md`
- Re-compute and save baseline metrics after cleanup
- The cleaned baseline should only contain content extracted from the PDF, not AI conversation text
- After cleanup, the current extraction's -6.2% character regression should be eliminated or significantly reduced

## Investigation Steps
1. Quantify the artifacts:
   ```bash
   grep -c "I notice you mentioned\|I need to see the image\|Could you please share\|I don't see any image\|without seeing\|If you could share\|Let me look at this more carefully" tests/corpus/baseline/delene_2001/full_document.md
   ```
   Known result: 25 instances of AI conversation text.

2. Examine surrounding context to understand what the artifacts replaced (equation/table regions that Layer 3 failed to repair)

3. Determine what the correct content should be — compare against current extraction which has the actual table data (e.g., Table 1, Table 2) properly extracted

4. Also check `hsu_2020` and `hawker_2020` baselines for similar artifacts (found 1 instance each — less severe)

## Evidence
Examples of AI artifacts in `tests/corpus/baseline/delene_2001/full_document.md`:
- Line 354: "I notice you mentioned an image showing the original PDF page, but no image was actually provided..."
- Line 392: "I need to see the image to convert the equation to LaTeX..."
- Line 425: "I don't see any image attached to your message..."
- Lines 432-441: "Let me look at this more carefully..." followed by incorrect LaTeX

The current pipeline actually extracts the tables (Table 1, Table 2) correctly as plain text, while the baseline replaced these with AI conversation artifacts. The -6.2% character loss is caused by removing this garbage text.

## Acceptance Criteria
- Zero instances of AI conversational patterns in the cleaned baseline
- `char_count` regression for `delene_2001` is within -3% (was -6.2%)
- All corpus tests pass after baseline update
- Baseline still contains all legitimate content from the PDF

## Verification
```bash
# Verify no AI artifacts remain
grep -c "I notice you mentioned\|I need to see the image\|Could you please share\|I don't see any image\|without seeing\|If you could share\|Let me look at this" tests/corpus/baseline/delene_2001/full_document.md
# Expected: 0

# Check updated metrics
python3 tests/corpus/metrics.py tests/corpus/baseline/delene_2001/full_document.md

# Run regression tests
uv run pytest tests/test_corpus.py --run-corpus -v

# Check comparison report
python3 tests/corpus/compare.py
```

## Constraints
- Only modify `tests/corpus/baseline/delene_2001/full_document.md` and its `metrics.json`
- Do NOT modify the extraction pipeline
- Preserve all legitimate content from the original PDF
- The simplest approach: re-extract delene_2001 with the current pipeline and use that as the new baseline, since the current extraction is demonstrably better (has actual table data instead of AI hallucinations)
