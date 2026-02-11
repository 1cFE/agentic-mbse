# Reject H1 Equation Noise Headers

## Purpose
Demote phantom H1 headings created when pymupdf4llm's font-size-based header detector misidentifies large-font equation symbols (∑, ∏, ∫, φ) as top-level headings in the energy_amplifier paper.

## Requirements
- Extend `reject_noise_headers()` to cover H1 (`#`) in addition to H2–H6 (`#{2,6}`)
- Add missing math symbols to `_is_noise_header()`'s character class: at minimum `∫` (U+222B), `φ` (U+03C6), `ψ` (U+03C8), `ε` (U+03B5), `ρ` (U+03C1), `σ` (U+03C3), `λ` (U+03BB)
- Do NOT demote legitimate H1 headings (document titles, `# 1 Introduction` style)

## Investigation Steps
1. Read `postprocess.py` lines 522–569 — understand the `_NOISE_HEADER_RE` regex and `_is_noise_header()` function
2. Write a learning test: extract the 64 H1 lines from `energy_amplifier/full_document.md`, run `_is_noise_header()` on each, and verify that:
   - All 64 equation H1s are detected as noise (currently ~59/64 are detected, 5 slip through due to missing `∫` and Greek letters)
   - A legitimate H1 like the document title or a section heading would NOT be flagged
3. Check other corpus papers for any legitimate H1 headings that must be preserved (hawker_2020, delene_2001 each have 1 H1)
4. Verify the `∫ E 2` case specifically — it currently returns False because `∫` is not in the symbol class

## Acceptance Criteria
- `_NOISE_HEADER_RE` matches `#{1,6}` instead of `#{2,6}`
- `_is_noise_header()` catches `∫ E 2`, standalone Greek letters, and equation fragments
- energy_amplifier heading count drops from 106 to ≤45 (removing ~60+ phantom H1 equation headers)
- No H1 headings removed from other corpus papers (hawker_2020 has 1 legitimate H1, delene_2001 has 1)
- All corpus tests pass (baselines must be updated for energy_amplifier)

## Verification
```bash
# Run full corpus tests
uv run pytest tests/test_corpus.py --run-corpus -v

# Check energy_amplifier H1 count (should be ≤5, was 64)
python3 -c "
with open('tests/corpus/current/energy_amplifier/full_document.md') as f:
    lines = f.readlines()
h1 = [l for l in lines if l.startswith('# ') and not l.startswith('## ')]
print(f'H1 count: {len(h1)}')
for l in h1:
    print(f'  {l.rstrip()[:100]}')
"

# Verify other papers unchanged
python3 tests/corpus/metrics.py tests/corpus/current/hawker_2020/full_document.md
python3 tests/corpus/metrics.py tests/corpus/current/delene_2001/full_document.md
```

## Constraints
- Do NOT change any extraction backend code (pymupdf_backend.py)
- Do NOT remove legitimate headings from any other corpus paper
- Heading counts for non-energy_amplifier papers must remain identical to current baselines
- The energy_amplifier baseline must be regenerated after the fix
