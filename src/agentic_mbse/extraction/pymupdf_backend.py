"""PyMuPDF4LLM extraction backend (PDF only).

Fast, reliable fallback. Requires the ``pymupdf4llm`` package
(installed via the ``extract`` optional dependency).
"""

from __future__ import annotations

import re
from pathlib import Path

from agentic_mbse.extraction.base import ExtractionResult
from agentic_mbse.extraction.postprocess import postprocess


def _get_to_markdown():
    """Lazy-import ``pymupdf4llm.to_markdown`` and return it."""
    import pymupdf4llm  # type: ignore[import-untyped]

    return pymupdf4llm.to_markdown


class AcademicHeaderDetector:
    """Custom header detector using font metadata + section numbering.

    Replaces pymupdf4llm's default font-size-only IdentifyHeaders with a
    multi-signal approach that works better for academic papers:
    - Rejects math symbols and equations
    - Detects numbered section headers (e.g., "1. Introduction", "2.3 Methods")
    - Uses font differentiation (family, weight, italic) from body text
    - Maps section depth to heading levels (top-level → H2, subsections → H3/H4)
    """

    # Math symbols that indicate equations, not headers
    _MATH_SYMBOLS = "∫∑∏∂√≈≠≤≥±×÷→←∞•"

    # Known single-word all-caps headers
    _KNOWN_ALLCAPS_HEADERS = {
        "ABSTRACT",
        "INTRODUCTION",
        "BACKGROUND",
        "METHODS",
        "RESULTS",
        "DISCUSSION",
        "CONCLUSION",
        "CONCLUSIONS",
        "REFERENCES",
        "ACKNOWLEDGMENTS",
        "APPENDIX",
        "NOMENCLATURE",
        "NOTATION",
    }

    def __init__(self, doc_path: str):
        """Pre-scan PDF to identify body text font."""
        try:
            import pymupdf

            doc = pymupdf.open(doc_path)

            # Count character occurrences by font family (ignoring size/weight/italic)
            font_counts: dict[str, int] = {}
            for page in doc:
                blocks = page.get_text("dict")["blocks"]
                for block in blocks:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span["text"].strip()
                            if not text:
                                continue
                            # Extract base font family (before hyphen, e.g., "NimbusRomNo9L-Regu" → "NimbusRomNo9L")
                            font_family = (
                                span["font"].split("-")[0] if "-" in span["font"] else span["font"]
                            )
                            font_counts[font_family] = font_counts.get(font_family, 0) + len(text)

            doc.close()

            # Most-frequent font family = body text
            self.body_font_family = max(font_counts, key=font_counts.get) if font_counts else ""
        except Exception:
            # If we can't open the PDF for pre-scan (e.g., in tests), use empty body font
            # The detector will still work based on other signals (section numbering, caps, etc.)
            self.body_font_family = ""

    def __call__(self, span, page=None) -> str:
        """Classify a span as heading or not.

        Returns heading prefix (e.g., "## ") or empty string if not a heading.
        """
        text = span["text"].strip()
        if not text:
            return ""

        # Reject math symbols - equations are not headers
        if any(sym in text for sym in self._MATH_SYMBOLS):
            return ""

        # Reject short fragments that aren't section numbers
        # (e.g., single-char math symbols like "ρ", "σ")
        if len(text) < 4 and not re.match(r"^\d+(?:\.\d+)*\.?$", text):
            return ""

        # Extract font metadata
        font_full = span["font"]
        font_family = font_full.split("-")[0] if "-" in font_full else font_full
        is_bold = bool(span["flags"] & 16)  # bit 4 = bold
        is_italic = bool(span["flags"] & 2)  # bit 1 = italic
        font_size = span["size"]

        # Check if font differs from body (different family, or same family but bold/italic)
        font_differs = font_family != self.body_font_family or is_bold or is_italic

        # Pattern 1: Numbered section headers
        # Match patterns like "1. Introduction", "2.3 Methods", "1.2.1 Details"
        # Allow optional period after number, require space before title
        m = re.match(r"^(\d+(?:\.\d+)*)\.?\s+(.+)", text)
        if m:
            sec_num = m.group(1)
            title_text = m.group(2)

            # Map section depth to heading level
            depth = sec_num.count(".") + 1

            # Guard 1: Reject absurd top-level section numbers (e.g., year 2020, address 5285)
            # Real academic papers don't have section "140" or "2020"
            if depth == 1 and int(sec_num) > 99:
                return ""

            # Guard 2: Distinguish footnotes/bib entries from real section headers
            # For top-level sections, require font_differs to reject body-font numbered text
            # Exception: single-digit sections with trailing period (1-9) are allowed
            # (handles papers with "1. Introduction" format in body font)
            if depth == 1:
                has_period = bool(re.match(r"^\d+\.\s", text))
                single_digit_with_period = int(sec_num) <= 9 and has_period
                if not single_digit_with_period and not font_differs:
                    # Body-font numbered text (footnotes, captions, bib entries) rejected
                    return ""

            # Require either font differentiation OR title starts with capital letter
            # (some papers use same font for headers but rely on capitalization)
            if font_differs or (title_text and title_text[0].isupper()):
                if depth == 1:
                    return "## "  # Top-level section (1, 2, 3) → H2
                elif depth == 2:
                    return "### "  # Subsection (1.1, 2.3) → H3
                else:
                    return "#### "  # Sub-subsection (1.1.1) → H4

        # Pattern 2: All-caps headers (ABSTRACT, REFERENCES, etc.)
        # Guard: Require minimum alphabetic characters to reject sparse-letter fragments
        # like ", D. M. 2002" (only 2 letters) or "(3P1), 1050–1055." (only 1 letter)
        alpha_count = sum(c.isalpha() for c in text)
        if alpha_count >= 4 and text.isupper() and len(text) < 60:
            # Single-word all-caps must be in known set
            words = text.split()
            if len(words) == 1:
                if text in self._KNOWN_ALLCAPS_HEADERS:
                    return "## "
            elif len(words) <= 6:
                # Multi-word all-caps: require font differentiation
                # Body-font all-caps are likely reference entries (e.g., "AHN, J.-W., GRAY, T., et al. 2017")
                if font_differs:
                    return "## "

        # Pattern 3: Title on first page (largest font)
        # This is conservative - only promote if significantly larger than body (>= 14pt)
        # and appears to be a title (capitalized, reasonable length)
        if page is not None and page.number == 0 and font_size >= 14:
            if text[0].isupper() and 10 <= len(text) <= 200:
                # Additional check: title should have multiple words or be long
                if len(text.split()) >= 3 or len(text) >= 30:
                    return "# "

        # Default: not a header - let postprocess promoters handle edge cases
        return ""


def extract(input_path: Path, output_dir: Path) -> ExtractionResult:
    """Extract a PDF using PyMuPDF4LLM.

    Creates *output_dir*/``full_document.md`` and *output_dir*/``images/``.
    """
    try:
        to_markdown = _get_to_markdown()

        output_dir.mkdir(parents=True, exist_ok=True)
        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)

        # Initialize custom header detector
        detector = AcademicHeaderDetector(str(input_path))

        chunks = to_markdown(
            str(input_path),
            write_images=True,
            image_path=str(images_dir),
            image_format="png",
            dpi=150,
            page_chunks=True,
            hdr_info=detector,
            table_strategy="lines_strict",
        )

        # Join page chunks with page markers for downstream page resolution
        page_texts = []
        for chunk in chunks:
            page_num = chunk.get("metadata", {}).get("page", None)
            if page_num is not None:
                page_texts.append(f"<!-- PAGE:{page_num} -->")
            page_texts.append(chunk["text"])
        md_text: str = "\n".join(page_texts)

        # Apply deterministic post-processing
        md_text = postprocess(md_text, images_dir=images_dir)

        md_path = output_dir / "full_document.md"
        md_path.write_text(md_text)

        image_count = sum(1 for f in images_dir.iterdir() if f.is_file())

        return ExtractionResult(
            success=True,
            output_dir=output_dir,
            markdown_path=md_path,
            image_count=image_count,
            char_count=len(md_text),
            backend_used="pymupdf",
        )
    except Exception as exc:
        return ExtractionResult(
            success=False,
            output_dir=output_dir,
            error=str(exc),
            backend_used="pymupdf",
        )
