# Spike: does the arXiv margin stamp survive text extraction?

**Date:** 2026-10-18 · **By:** orchestrator `[AGENT]` · **Question:** Can pymupdf tell the paper's own arXiv stamp apart from prose citations on page 1?

**Answer: yes.** In all three real arXiv PDFs the stamp comes out as one text line that is rotated 90° (pymupdf `get_text("dict")` line `dir == (0.0, -1.0)`), sits in the left margin (bbox x0 ≈ 11–24, x1 ≤ 44 pt), and reads `arXiv:<id>v<N>  [<category>]  <date>`. A prose citation in the generated citation-only PDF comes out horizontal (`dir == (1.0, 0.0)`) in the body (x0 = 72).

| PDF | Creator metadata | Stamp line dir | Stamp bbox (x0, y0, x1, y1) | Text |
|---|---|---|---|---|
| 1706.03762 | LaTeX with hyperref | (0, -1) | (11, 214, 38, 555) | `arXiv:1706.03762v7  [cs.CL]  2 Aug 2023` |
| 2310.06825 | LaTeX with hyperref | (0, -1) | (11, 214, 38, 560) | `arXiv:2310.06825v1  [cs.CL]  10 Oct 2023` |
| 2610.14224 | arXiv GenPDF (tex2pdf:07e334b) | (0, -1) | (24, 255, 44, 587) | `arXiv:2610.14224v1  [cs.AI]  9 Oct 2026` |
| citation-only.pdf (generated) | (empty) | (1, 0) | (72, 75, 214, 90) | `Prior work: arXiv:2610.14224` |

**Implications for design:**
- A rotated left-margin line matching the full stamp shape (`id`, `vN`, `[category]`, date) is good evidence of the paper's own ID. The bracketed category and date make a body citation unlikely to match even if rotated.
- Creator metadata is not a usable signal: two of three genuine arXiv PDFs say `LaTeX with hyperref`.
- Limits: PDFs not downloaded from arXiv (publisher versions, author preprints) have no stamp, so they fall to normal PDF extraction. That is the accepted false negative. The sample is three papers; exact margin coordinates vary, so match on rotation plus left-margin position plus text shape, not exact numbers.
- Fixtures can be generated with pymupdf (`insert_text(..., rotate=90)` in the left margin) rather than committing downloaded papers.

Sample PDFs were fetched to a session scratchpad and are not kept.
