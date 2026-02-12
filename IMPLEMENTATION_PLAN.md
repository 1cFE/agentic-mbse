# Implementation Plan — Iteration 2 Retry 2

## Status

This is **retry 2** after two failed attempts. Both eval reports show identical failures:
- **sparc_overview**: 57 headings (target ≤20) — Pattern 2 passes bibliographic author entries
- **delene_2001**: 58 headings (target 10-25) — Pattern 1 passes numbered references; Pattern 2 passes ORNL labels
- **energy_amplifier**: 97 headings (target 50-130) — PASS
- No math symbol regressions — PASS

### What Was Already Implemented (commits 5ba3363–6d2223f)

These guards are already in the code and working:
- Pattern 1 guard: `sec_num > 99` rejection (line 127 of pymupdf_backend.py)
- Pattern 1 guard: single-digit without period requires `font_differs` (lines 135-138)
- Pattern 2 guard: `alpha_count >= 4` before `isupper()` (lines 153-154)
- Postprocess: `_replace_plain_header()` caps section numbers > 99 (lines 107-113 of postprocess.py)
- Postprocess: `_replace_plain_header()` rejects Figure/Fig./Table/Equation titles (lines 115-117)
- Diagnostic tool: `tests/corpus/phantom_survey.py`

### Why the Existing Guards Are Insufficient

**The alpha_count guard is necessary but not sufficient for Pattern 2.** Bibliographic entries like `"AHN, J.-W., GRAY, T., HUGHES, J., et al. 2017"` have alpha_count >> 4 and pass isupper(). The ORNL label `"ORNL 99-1407 EFG"` also has alpha_count > 4. The guard only stopped sparse-letter fragments like `", D. M. 2002"` — those are fixed, but the real volume of phantoms comes from legitimate-looking all-caps text in body font.

**The footnote guard only covers single-digit-without-period for Pattern 1.** Reference entries like `"5. J.G. Delene..."` have periods (`has_period=True`) and bypass the guard entirely. The `sec_num > 99` cap doesn't help for reference numbers 1-36.

### The Core Fix: `font_differs` as Primary Discriminator

The phantom_survey.py from Task 1 (commit 5ba3363) already confirmed: **all phantom headings in sparc_overview have `font_differs=False`**. This is the key insight. Real headings use bold or a different font family; reference entries, footnotes, and ORNL labels use body font. The fix is simple: require `font_differs=True` for the remaining unguarded paths in both patterns.

---

## Task List

## Progress Summary (After Task 2)

Pattern 2 fix (font_differs for multi-word all-caps) **WORKED**:
- sparc_overview: 57 → 44 headings (eliminated ~13 author-initial phantoms)
- delene_2001: 58 → 48 headings (eliminated some all-caps phantoms)
- aries_cost_account: 64 → 44 headings (-31.2%, exceeded -30% threshold by 1.2%)

**Remaining phantoms are ALL Pattern 1**: Numbered reference entries like "1. Electric Power Annual...", "2. Annual Energy Outlook...", etc. These pass the current guard because:
1. They use body font (font_differs=False)
2. Title starts with capital letter → passes `title_text[0].isupper()` check on line 142

The issue is NOT that we need font_differs for Pattern 1. The issue is that we need to detect reference sections and exclude numbered items within them from promotion. Postprocessing already filters noise headers, but these come from the detector itself.

**New strategy for remaining phantoms**: Add Pattern 1 guard to reject numbered entries that appear to be bibliographic references. References are distinguished by:
- Follow a "REFERENCES" or "BIBLIOGRAPHY" heading
- Often have author names (initials with periods)
- Journal abbreviations
- Year patterns

### Task 1 [DONE]: Diagnostic — Verify font_differs for delene_2001 [spec-01, spec-02]

- **What**: Run `phantom_survey.py` on delene_2001 to verify that `font_differs` reliably separates real headings (sections 1-7, subsections 4.1-4.6) from phantoms (reference entries 1-36, ORNL labels). sparc_overview was already surveyed; delene_2001 was not fully characterized for font_differs in Pattern 1 matches. Log every Pattern 1 match with its `font_differs` value, section number, and title text. Also log Pattern 2 matches.
- **Why**: Before modifying Pattern 1 to require font_differs for ALL depth-1 sections (not just single-digit-without-period), we must confirm that delene_2001's real section headers (1. INTRODUCTION through 7. CONCLUSION) use a heading font. If they use body font, we need a different approach (title-word allowlist).
- **Verified by**: Survey output showing font_differs=True for all real section headers and font_differs=False for all reference entries. No code changes, just analysis.
- **Depends on**: None

**RESULTS**:
- **delene_2001**: Pattern 1 detected 53 matches (13 font_differs=True, 40 font_differs=False). Of the 31 phantom headings, MOST have font_differs=False (likely TOC entries and page headers that repeat). However, 11 real section headings (like "2. ANALYSIS PROCEDURES", "3. PLANT DESIGNS", "4.1 FINANCE COSTS") have font_differs=TRUE — these are the actual section headers in bold.
- **Critical finding**: TOC entries in delene_2001 use body font and have dot leaders ("2.  ANALYSIS PROCEDURES........."). These are the 40 font_differs=False matches. The real section headers appear TWICE — once in TOC (body font) and once in the document body (bold font).
- **Pattern 2 in delene_2001**: 20 matches (17 font_differs=True, 3 font_differs=False). Only 1 phantom ("U.S. DEPARTMENT OF ENERGY" with font_differs=False). Most (17) are "uncertain" multi-word all-caps with font_differs=True — these may be figure labels like "ORNL 99-1407 EFG" that use bold.
- **sparc_overview Pattern 2**: 22 matches, ALL font_differs=False. This confirms all Pattern 2 phantoms in sparc_overview use body font. The fix will work here.
- **Revised strategy**: Pattern 1 needs a TOC detection heuristic (dot leaders, page numbers). Pattern 2 font_differs guard will work for sparc_overview but NOT for delene_2001 ORNL labels (which use bold). Need to detect report-style labels differently.

### Task 2: Fix Pattern 2 — require font_differs for multi-word all-caps [spec-01]

- **What**: In `AcademicHeaderDetector.__call__()` Pattern 2 branch (lines 160-162 of pymupdf_backend.py), change the multi-word acceptance from unconditional to requiring `font_differs=True`:
  ```python
  # BEFORE (current code):
  elif len(words) <= 6:
      return "## "

  # AFTER:
  elif len(words) <= 6:
      if font_differs:
          return "## "
  ```
  Single-word known headers (line 157-159) are unchanged — `_KNOWN_ALLCAPS_HEADERS` like ABSTRACT, REFERENCES are always legitimate regardless of font.
- **Why**: This single 2-line change eliminates ~47 phantom headings in sparc_overview (all bibliographic author entries use body font) and ~6 ORNL labels in delene_2001 (also body font). It preserves real all-caps headers because they use bold/italic/different font family.
- **Verified by**: `uv run pytest tests/ -v` all pass; sparc_overview heading_count ≤ 20. Add a unit test in `tests/test_extraction.py` (or wherever detector tests live) that creates a mock span with `font_differs=False` and multi-word all-caps text and confirms it returns `""`.
- **Depends on**: Task 1 (confirms multi-word phantoms in delene_2001 have font_differs=False)

### Task 3: Fix Pattern 1 — require font_differs for ALL depth-1 numbered sections [spec-01]

- **What**: In `AcademicHeaderDetector.__call__()` Pattern 1 branch, replace the narrow footnote guard (lines 135-138) with a broader guard that covers ALL depth-1 sections:
  ```python
  # BEFORE (current code, lines 134-138):
  has_period = bool(re.match(r"^\d+\.\s", text))
  if depth == 1 and int(sec_num) <= 9 and not has_period:
      if not font_differs:
          return ""

  # AFTER:
  if depth == 1 and not font_differs:
      # Body-font numbered text is likely a reference entry or footnote.
      # Exception: title contains a recognized section keyword.
      _SECTION_KEYWORDS = {
          "introduction", "background", "methods", "methodology",
          "results", "discussion", "conclusion", "conclusions",
          "summary", "abstract", "references", "acknowledgment",
          "acknowledgments", "acknowledgement", "acknowledgements",
          "appendix", "overview", "objectives", "scope",
      }
      title_lower = title_text.lower().split()[0] if title_text.strip() else ""
      if title_lower not in _SECTION_KEYWORDS:
          return ""
  ```
  This requires `font_differs=True` for ALL depth-1 numbered sections unless the title starts with a recognized section keyword. Reference entries like `"5. J.G. Delene..."` fail because "j.g." is not a section keyword and they use body font. Real sections like `"1. INTRODUCTION"` pass either via font_differs or the keyword allowlist.
- **Why**: The current guard only covers single-digit sections without periods. Reference entries with periods (e.g., `"5. Electric Power Annual..."`) bypass it completely. Broadening to ALL depth-1 closes the gap. The keyword allowlist is a safety net for papers where section headers happen to use body font.
- **Verified by**: `uv run pytest tests/ -v` all pass; delene_2001 reference entries 1-36 no longer promoted. Add unit tests for: (a) body-font numbered reference → rejected, (b) body-font "1. Introduction" → accepted via keyword, (c) bold-font section → accepted via font_differs.
- **Depends on**: Task 1 (confirms real sections in delene_2001 have font_differs=True or match keywords)

### Task 4: Strengthen postprocess `_is_noise_header()` for structural phantoms [spec-02]

- **What**: Add patterns to `_is_noise_header()` in postprocess.py (lines 308-333) to catch structural phantoms that survive the detector or are introduced by postprocess promoters. Add these checks:
  1. **Report/figure labels**: `r"^[A-Z]{2,}\s+\d{2,}[-–]\d+"` (e.g., "ORNL 99-1407 EFG")
  2. **Address indicators**: `r"\b\d{5}\b"` (ZIP codes) or contains "Road" / "Avenue" / "Street" / "Drive"
  3. **Distribution lists**: text contains "DISTRIBUTION" preceded by "INTERNAL" or "EXTERNAL"
  4. **Section number > 99 in heading text**: `r"^(\d+)(?:\.\d+)*\s"` where int(group 1) > 99 — catches any heading that somehow still has an absurd section number

  Also add unit tests for each new pattern.
- **Why**: `_is_noise_header()` is the last line of defense. After Tasks 2-3, most phantoms will be eliminated at the detector level. But some may survive from `promote_plain_headers` or `promote_bold_headers` (which don't have font_differs access). The noise filter catches these without needing font information.
- **Verified by**: `uv run pytest tests/test_postprocess.py -v` all pass including new tests. Manual inspection of delene_2001 headings after full pipeline.
- **Depends on**: None (can be done in parallel with Tasks 2-3, but testing with corpus requires those to be done first)

### Task 5: Corpus re-extraction and full validation [spec-01, spec-02]

- **What**: Re-extract all 7 corpus papers. Verify ALL acceptance criteria from both specs:
  - `sparc_overview`: heading_count ≤ 20 (was 57)
  - `energy_amplifier`: heading_count in 50-130 (was 97)
  - `delene_2001`: heading_count in 10-25 (was 58)
  - `hawker_2020`, `aries_cost_account`, `helios_design`, `hsu_2020`: no decrease > 20%
  - Zero math symbols in headings
  - All unit tests pass
  - All 4 corpus tests pass

  Run:
  ```bash
  uv run pytest tests/test_corpus.py --run-corpus -v
  uv run pytest tests/ -v
  grep -P '^#{1,6} .*[∫∑∏∂√≈≠≤≥±×÷→←∞•]' tests/corpus/current/*/full_document.md
  ```

  If any paper fails, diagnose the specific headings causing the problem (grep `^#` on the output file) and adjust guards accordingly.
- **Why**: Final acceptance gate. Both specs must pass simultaneously.
- **Verified by**: All commands above return green / empty as expected.
- **Depends on**: Tasks 2, 3, 4

---

## Risk Assessment

**Risk 1: font_differs may not work for delene_2001 real sections.**
If sections like "1. INTRODUCTION" in delene_2001 use body font (not bold, same font family), requiring font_differs would suppress them. Task 1 validates this. The keyword allowlist in Task 3 mitigates this — "INTRODUCTION" matches regardless of font.

**Mitigation**: The keyword allowlist ensures common section titles pass even without font differentiation. If delene_2001 uses body font for ALL headings, expand the allowlist.

**Risk 2: aries_cost_account further regression.**
Current count is 46 (baseline 64, -28%, threshold -30%). Adding font_differs guards could drop it further if some of its headings use body font.

**Mitigation**: Monitor in Task 5. The heading_regression_pct for aries_cost_account is -30 in papers.jsonl, giving 2% margin. If it drops below 44, investigate which headings were lost.

**Risk 3: Known all-caps headers in _KNOWN_ALLCAPS_HEADERS might need expansion.**
If a paper has a legitimate single-word all-caps header not in the set (e.g., "NOMENCLATURE", "NOTATION"), it won't be promoted.

**Mitigation**: Review the `_KNOWN_ALLCAPS_HEADERS` set during Task 2 and add any missing entries observed in corpus papers. This is low risk because single-word all-caps headers are a small, well-defined set.

## Critical Path

```
Task 1 (diagnostic)
  ├→ Task 2 (Pattern 2 font_differs)  ─┐
  └→ Task 3 (Pattern 1 font_differs)  ─┤
Task 4 (noise filter) ─────────────────┤
                                        └→ Task 5 (corpus validation)
```

Tasks 2, 3, and 4 can proceed in parallel after Task 1. Task 5 requires all three.
