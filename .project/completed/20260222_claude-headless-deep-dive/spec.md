# Spec: Claude Headless Direct Extraction (Stage 1D)

**Status:** Active
**Created:** 2026-02-22

## Source

The full specification for Stage 1D lives in the development strategy:
`../../concepts/doc-extraction-development-strategy.md` → Section "1D: Claude Headless Direct Extraction"

This spec file exists for workflow consistency. The development strategy section is the authoritative source — it contains the experiment matrix, prompt design, implementation notes, key questions, and definition of done.

## One-Sentence Summary

Render PDF pages to images, hand them to `claude -p`, and measure whether Claude's native vision produces better markdown than the library-based extractors (pymupdf4llm, Docling, GMFT).

## Key Questions

1. **Quality ceiling** — What's the best markdown Claude can produce from page images alone?
2. **Pages-per-call tradeoff** — Does 5 or 10 pages per call help or hurt?
3. **Tool-assisted vs. pure vision** — Does giving Claude pymupdf4llm text alongside images improve results?
4. **Cost/time profile** — Tokens per page, dollars per document, viable at scale?
5. **Equation transcription** — Can Claude convert page-image equations to LaTeX? (The #1 gap from Stage 1A)
6. **Hallucination risk** — Does Claude invent numerical values or content?

## Success Criteria

Per the development strategy's "Stage 1D Definition of Done":

- At least 3 experiment configurations run on the 4-paper initial subset
- Results saved in `tests/corpus/runs/claude_*/` with same format as 1A-1C runs
- Comparison table: Claude vision vs pymupdf4llm best_v1 vs Docling vs GMFT for each metric
- Specific assessment of equation extraction quality (manual check on 2+ papers)
- Specific assessment of hallucination risk (manual check: are numbers accurate?)
- Cost estimate: tokens per page, dollars per document, projected corpus cost
- Clear recommendation: where in the pipeline does Claude headless add the most value?
