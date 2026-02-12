#!/usr/bin/env python3
"""Learning test: instrument AcademicHeaderDetector to count phantom headings.

This script runs the detector on sparc_overview and energy_amplifier, logging
which pattern (1, 2, or 3) matched for each heading, along with font_differs
metadata. Output shows per-paper phantom vs legitimate heading counts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# Import the detector and extraction function
from agentic_mbse.extraction.pymupdf_backend import AcademicHeaderDetector


@dataclass
class HeadingMatch:
    """A single heading match from the detector."""

    text: str
    pattern: int  # 1=numbered, 2=allcaps, 3=title
    result: str  # The markdown heading prefix ("## ", "### ", etc.)
    font_differs: bool
    font_family: str
    is_bold: bool
    is_italic: bool
    page_num: int | None = None


class InstrumentedHeaderDetector(AcademicHeaderDetector):
    """Version of AcademicHeaderDetector that logs all matches."""

    def __init__(self, pdf_path: str):
        super().__init__(pdf_path)
        self.matches: list[HeadingMatch] = []

    def __call__(self, span, page=None) -> str:
        """Classify a span as heading or not, logging the match."""
        text = span["text"].strip()
        if not text:
            return ""

        # Reject math symbols - equations are not headers
        if any(sym in text for sym in self._MATH_SYMBOLS):
            return ""

        # Reject short fragments that aren't section numbers
        if len(text) < 4 and not re.match(r"^\d+(?:\.\d+)*\.?$", text):
            return ""

        # Extract font metadata
        font_full = span["font"]
        font_family = font_full.split("-")[0] if "-" in font_full else font_full
        is_bold = bool(span["flags"] & 16)
        is_italic = bool(span["flags"] & 2)
        font_size = span["size"]

        # Check if font differs from body
        font_differs = font_family != self.body_font_family or is_bold or is_italic

        page_num = page.number if page is not None else None

        # Pattern 1: Numbered section headers
        m = re.match(r"^(\d+(?:\.\d+)*)\.?\s+(.+)", text)
        if m:
            sec_num = m.group(1)
            title_text = m.group(2)

            if font_differs or (title_text and title_text[0].isupper()):
                depth = sec_num.count(".") + 1
                if depth == 1:
                    result = "## "
                elif depth == 2:
                    result = "### "
                else:
                    result = "#### "

                self.matches.append(
                    HeadingMatch(
                        text=text,
                        pattern=1,
                        result=result,
                        font_differs=font_differs,
                        font_family=font_family,
                        is_bold=is_bold,
                        is_italic=is_italic,
                        page_num=page_num,
                    )
                )
                return result

        # Pattern 2: All-caps headers
        if text.isupper() and len(text) < 60:
            words = text.split()
            if len(words) == 1:
                if text in self._KNOWN_ALLCAPS_HEADERS:
                    self.matches.append(
                        HeadingMatch(
                            text=text,
                            pattern=2,
                            result="## ",
                            font_differs=font_differs,
                            font_family=font_family,
                            is_bold=is_bold,
                            is_italic=is_italic,
                            page_num=page_num,
                        )
                    )
                    return "## "
            elif len(words) <= 6:
                self.matches.append(
                    HeadingMatch(
                        text=text,
                        pattern=2,
                        result="## ",
                        font_differs=font_differs,
                        font_family=font_family,
                        is_bold=is_bold,
                        is_italic=is_italic,
                        page_num=page_num,
                    )
                )
                return "## "

        # Pattern 3: Title on first page
        if page is not None and page.number == 0 and font_size >= 14:
            if text[0].isupper() and 10 <= len(text) <= 200:
                if len(text.split()) >= 3 or len(text) >= 30:
                    self.matches.append(
                        HeadingMatch(
                            text=text,
                            pattern=3,
                            result="# ",
                            font_differs=font_differs,
                            font_family=font_family,
                            is_bold=is_bold,
                            is_italic=is_italic,
                            page_num=page_num,
                        )
                    )
                    return "# "

        return ""


def extract_with_instrumented_detector(
    pdf_path: Path,
) -> tuple[str, InstrumentedHeaderDetector]:
    """Extract a PDF using the instrumented detector.

    Returns the markdown text and the detector with logged matches.
    """
    import pymupdf4llm  # type: ignore[import-untyped]

    detector = InstrumentedHeaderDetector(str(pdf_path))

    chunks = pymupdf4llm.to_markdown(
        str(pdf_path),
        write_images=False,
        page_chunks=True,
        hdr_info=detector,
        table_strategy="lines",
    )

    # Join chunks
    page_texts = []
    for chunk in chunks:
        page_texts.append(chunk["text"])
    md_text = "\n".join(page_texts)

    return md_text, detector


def classify_heading(text: str, pattern: int) -> tuple[str, str]:
    """Classify a heading as phantom or legitimate.

    Returns (category, reason).
    """
    # Pattern 1 phantoms
    if pattern == 1:
        # Extract the section number
        m = re.match(r"^(\d+)(?:\.\d+)*\.?\s+(.+)", text)
        if m:
            sec_num = int(m.group(1))
            title = m.group(2)

            # Year numbers (2000-2099)
            if 2000 <= sec_num <= 2099:
                return ("phantom", f"year number ({sec_num})")

            # High section numbers > 99
            if sec_num > 99:
                return ("phantom", f"absurd section number ({sec_num})")

            # Table/Figure captions
            if re.match(r"^(Table|Figure|Fig\.)", title, re.IGNORECASE):
                return ("phantom", "table/figure caption")

            # Footnote-like (single digit 1-20)
            if 1 <= sec_num <= 20 and "." not in m.group(1):
                # Heuristic: if title looks like body text not a section header
                if not any(
                    kw in title.lower()
                    for kw in [
                        "introduction",
                        "background",
                        "method",
                        "result",
                        "discussion",
                        "conclusion",
                        "summary",
                        "overview",
                    ]
                ):
                    return ("phantom", f"likely footnote ({sec_num})")

        return ("legitimate", "numbered section")

    # Pattern 2 phantoms
    if pattern == 2:
        # Author initials, citation fragments
        if re.search(r"[A-Z]\.\s*[A-Z]\.", text):
            return ("phantom", "author initials")

        # Single letters or very short
        if len([c for c in text if c.isalpha()]) < 4:
            return ("phantom", "sparse letters")

        # Known legitimate all-caps
        if text in {
            "ABSTRACT",
            "INTRODUCTION",
            "CONCLUSION",
            "REFERENCES",
            "ACKNOWLEDGMENTS",
            "ACKNOWLEDGEMENTS",
            "APPENDIX",
        }:
            return ("legitimate", "known header")

        # Multi-word all-caps with reasonable content
        if len(text.split()) >= 2:
            return ("uncertain", "multi-word all-caps")

        return ("phantom", "other all-caps")

    # Pattern 3 (title) is usually legitimate
    if pattern == 3:
        return ("legitimate", "title")

    return ("uncertain", "unknown pattern")


def analyze_paper(pdf_path: Path, name: str):
    """Analyze a single paper and print results."""
    print(f"\n{'=' * 80}")
    print(f"Paper: {name}")
    print(f"Path: {pdf_path}")
    print(f"{'=' * 80}\n")

    md_text, detector = extract_with_instrumented_detector(pdf_path)

    # Count total headings in output
    heading_lines = [line for line in md_text.split("\n") if line.startswith("#")]
    print(f"Total headings in markdown output: {len(heading_lines)}")
    print(f"Total detector matches logged: {len(detector.matches)}\n")

    # Analyze by pattern
    for pattern_num in [1, 2, 3]:
        pattern_matches = [m for m in detector.matches if m.pattern == pattern_num]
        if not pattern_matches:
            continue

        pattern_name = {1: "Numbered sections", 2: "All-caps", 3: "Title"}[pattern_num]
        print(f"\n--- Pattern {pattern_num}: {pattern_name} ({len(pattern_matches)} matches) ---\n")

        # Count by font_differs
        with_font_diff = sum(1 for m in pattern_matches if m.font_differs)
        without_font_diff = len(pattern_matches) - with_font_diff
        print(f"  font_differs=True:  {with_font_diff}")
        print(f"  font_differs=False: {without_font_diff}\n")

        # Classify
        phantom_count = 0
        legitimate_count = 0
        uncertain_count = 0

        phantom_examples = []
        legitimate_examples = []

        for match in pattern_matches:
            category, reason = classify_heading(match.text, match.pattern)

            if category == "phantom":
                phantom_count += 1
                if len(phantom_examples) < 10:
                    page_info = f"page {match.page_num}" if match.page_num is not None else "page ?"
                    phantom_examples.append(
                        f"    - {match.text[:80]} ({reason}, {page_info}, font_differs={match.font_differs})"
                    )
            elif category == "legitimate":
                legitimate_count += 1
                if len(legitimate_examples) < 5:
                    page_info = f"page {match.page_num}" if match.page_num is not None else "page ?"
                    legitimate_examples.append(
                        f"    - {match.text[:80]} ({reason}, {page_info})"
                    )
            else:
                uncertain_count += 1

        print(f"  Classification:")
        print(f"    Phantom:    {phantom_count}")
        print(f"    Legitimate: {legitimate_count}")
        print(f"    Uncertain:  {uncertain_count}")

        if phantom_examples:
            print(f"\n  Sample phantom headings:")
            for ex in phantom_examples:
                print(ex)

        if legitimate_examples:
            print(f"\n  Sample legitimate headings:")
            for ex in legitimate_examples:
                print(ex)

    # Overall summary
    total_phantom = sum(
        1
        for m in detector.matches
        if classify_heading(m.text, m.pattern)[0] == "phantom"
    )
    total_legitimate = sum(
        1
        for m in detector.matches
        if classify_heading(m.text, m.pattern)[0] == "legitimate"
    )
    total_uncertain = sum(
        1
        for m in detector.matches
        if classify_heading(m.text, m.pattern)[0] == "uncertain"
    )

    print(f"\n{'=' * 80}")
    print(f"OVERALL SUMMARY for {name}")
    print(f"{'=' * 80}")
    print(f"Total phantom:    {total_phantom}")
    print(f"Total legitimate: {total_legitimate}")
    print(f"Total uncertain:  {total_uncertain}")
    print()


def main():
    """Run the phantom heading survey on corpus papers."""
    corpus_dir = Path(__file__).parent
    pdfs_dir = corpus_dir / "pdfs"

    # Papers of interest per spec
    # Note: energy_amplifier (241 pages) takes too long; focus on sparc and delene
    papers = [
        ("sparc_overview", pdfs_dir / "sparc_overview.pdf"),
        ("delene_2001", pdfs_dir / "delene_2001.pdf"),
        # ("energy_amplifier", pdfs_dir / "energy_amplifier.pdf"),  # Too slow for learning test
    ]

    print("\n" + "=" * 80)
    print("PHANTOM HEADING SURVEY - Learning Test for Iteration 2")
    print("=" * 80)
    print("\nThis script instruments AcademicHeaderDetector to identify which")
    print("patterns produce phantom headings vs legitimate headings.")
    print()

    for name, pdf_path in papers:
        if not pdf_path.exists():
            print(f"\nWARNING: {pdf_path} not found, skipping {name}")
            continue

        analyze_paper(pdf_path, name)


if __name__ == "__main__":
    main()
