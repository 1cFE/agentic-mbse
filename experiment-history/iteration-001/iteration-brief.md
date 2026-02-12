# Iteration 1 Brief

This iteration focuses on **document structure fidelity** (Priority 1 from GOALS.md) — the single largest quality gap in the current pipeline. Investigation revealed that pymupdf4llm's default font-size-based header detection is fundamentally misaligned with how academic papers encode hierarchy: papers use font weight, italic styling, and font family changes rather than size differences, causing the detector to miss real headers (sparc_overview: 5 of ~13 detected; helios_design: 7 of ~24 detected) while promoting math symbols and display formulas as false headings (energy_amplifier: 64 false H1 headings). The fix is upstream — replacing the generic `IdentifyHeaders` with a custom `hdr_info` callback that reads font metadata + section numbering patterns, plus a postprocess safety net for italic-wrapped subsection headers. These changes leverage existing tool capabilities (pymupdf4llm's `hdr_info` parameter and pymupdf's font metadata) rather than adding downstream string-patching, and should generalize to unseen papers because the signals (numbered sections, font weight differentiation, math symbol rejection) are structural properties of academic documents, not publisher-specific formatting quirks.

**Specs:**
1. `01-establish-baselines.md` — Create baseline metrics so regression testing works (infrastructure, no code changes)
2. `02-custom-header-detector.md` — Replace default font-size detection with multi-signal custom detector (primary fix)
3. `03-italic-header-promotion.md` — Add postprocess rule for italic-wrapped numbered subsections (safety net)

**Success metric:** sparc_overview heading_count ≥ 10, helios_design heading_count ≥ 20, energy_amplifier H1 count ≤ 5, zero math symbols in any heading, no regressions on other papers.

**Challenge rules note:** The pool directory contains only PDFs already in the corpus (sparc_overview, energy_amplifier). No new PDF can be added this iteration. If future iterations add PDFs to the pool, the spec agent will include a corpus expansion spec.
