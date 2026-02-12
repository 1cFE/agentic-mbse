"""Font metadata survey to understand header patterns across corpus."""
import pymupdf
from collections import Counter

for pdf_name in ['sparc_overview', 'helios_design', 'energy_amplifier', 'aries_cost_account', 'delene_2001']:
    doc = pymupdf.open(f"tests/corpus/pdfs/{pdf_name}.pdf")
    font_counter = Counter()
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if "lines" not in b:
                continue
            for l in b["lines"]:
                for s in l["spans"]:
                    text = s["text"].strip()
                    if not text:
                        continue
                    key = (s["font"], round(s["size"]), bool(s["flags"] & 16), bool(s["flags"] & 2))
                    font_counter[key] += len(text)
    print(f"\n{pdf_name}: top 10 font combos (font, size, bold, italic) -> char_count")
    for (font, size, bold, italic), count in font_counter.most_common(10):
        print(f"  {font}, {size}pt, bold={bold}, italic={italic}: {count} chars")
    doc.close()
