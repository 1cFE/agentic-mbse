#!/bin/bash
# =============================================================================
# render_pages.sh — Pre-render PDF pages to PNG images for Claude extraction
# =============================================================================
#
# Renders all pages of specified papers to PNG at 200 DPI.
# Images are saved to tests/corpus/page_images/{slug}/page_{NNN}.png
#
# Usage:
#   ./render_pages.sh                    # Render 4-paper initial subset
#   ./render_pages.sh slug1 slug2        # Render specific papers
#
# =============================================================================

set -euo pipefail

CORPUS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAGE_IMAGES_DIR="$CORPUS_DIR/page_images"
DPI=200

# Default: 4-paper initial subset
if [[ $# -eq 0 ]]; then
    SLUGS=(hawker_2020 hsu_2020 hansen_2025 paischer_2025)
else
    SLUGS=("$@")
fi

echo "Rendering pages at ${DPI} DPI"
echo "Output: $PAGE_IMAGES_DIR"
echo "Papers: ${SLUGS[*]}"
echo ""

TOTAL_PAGES=0
TOTAL_PAPERS=0

for SLUG in "${SLUGS[@]}"; do
    PDF="$CORPUS_DIR/pdfs/${SLUG}.pdf"
    if [[ ! -f "$PDF" ]]; then
        echo "SKIP: $SLUG — PDF not found at $PDF"
        continue
    fi

    OUT_DIR="$PAGE_IMAGES_DIR/$SLUG"
    mkdir -p "$OUT_DIR"

    # Get page count and render all pages
    PAGE_COUNT=$(uv run python3 -c "
import pymupdf
doc = pymupdf.open('$PDF')
print(len(doc))
doc.close()
")

    echo -n "  $SLUG (${PAGE_COUNT}pp)... "

    uv run python3 -c "
import pymupdf

doc = pymupdf.open('$PDF')
scale = $DPI / 72
matrix = pymupdf.Matrix(scale, scale)
for i in range(len(doc)):
    page = doc[i]
    pix = page.get_pixmap(matrix=matrix)
    pix.save('$OUT_DIR/page_{:03d}.png'.format(i))
doc.close()
print('done')
"

    TOTAL_PAGES=$((TOTAL_PAGES + PAGE_COUNT))
    TOTAL_PAPERS=$((TOTAL_PAPERS + 1))
done

echo ""
echo "Rendered $TOTAL_PAGES pages from $TOTAL_PAPERS papers"
echo "Output: $PAGE_IMAGES_DIR"
