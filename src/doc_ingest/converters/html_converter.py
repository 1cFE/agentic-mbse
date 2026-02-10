"""HTML document converters for arXiv and publisher HTML.

Converts HTML documents to markdown, with format-specific validation including
paywall detection, MathML preservation (arXiv), and quality flag reporting.
"""

import re
from typing import Any

from bs4 import BeautifulSoup

from doc_ingest.types import (
    ConversionError,
    ConversionResult,
    QualityFlags,
    SourceFormat,
    ValidationResult,
)


class ArXivHTMLConverter:
    """ArXiv HTML converter with MathML preservation.

    Converts arXiv HTML5 documents to markdown while preserving MathML for
    mathematical expressions. Validates for body content presence.

    ArXiv HTML uses a clean structure with semantic tags and MathML for math.
    """

    @property
    def name(self) -> str:
        """Return converter name for provenance tracking."""
        return "ArXivHTMLConverter"

    def can_convert(self, format: SourceFormat) -> bool:
        """Check if this converter handles arXiv HTML format.

        Args:
            format: Source format type

        Returns:
            True if format is "arxiv_html", False otherwise
        """
        return format == "arxiv_html"

    def validate_source(self, content: bytes) -> ValidationResult:
        """Validate arXiv HTML content for body presence.

        Checks if the HTML contains body content (article text). ArXiv HTML
        typically has a <div class="ltx_page_content"> or similar structure.

        Args:
            content: Raw HTML bytes

        Returns:
            ValidationResult with is_valid=True if body content detected
        """
        try:
            # Decode HTML
            html_text = content.decode("utf-8", errors="replace")

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_text, "html.parser")

            # Check for body content - arXiv uses class="ltx_page_content" or similar
            has_body = bool(
                soup.find("div", class_=re.compile(r"ltx_page"))
                or soup.find("article")
                or soup.find("section", class_=re.compile(r"ltx_section"))
            )

            content_length = len(content)

            # Check for truncation (< 1KB for expected full document)
            is_truncated = content_length < 1024

            return ValidationResult(
                is_valid=has_body and not is_truncated,
                content_length=content_length,
                has_body_content=has_body,
                detected_content_type="text/html",
                is_truncated=is_truncated,
            )

        except Exception:
            # Failed to parse HTML
            return ValidationResult(
                is_valid=False,
                content_length=len(content),
                has_body_content=False,
                detected_content_type="unknown",
            )

    def convert(self, content: bytes) -> ConversionResult:
        """Convert arXiv HTML to markdown with MathML preservation.

        Extracts text and structure from arXiv HTML5, preserving MathML content
        for mathematical expressions. Detects tables, figures, and headings.

        Args:
            content: Raw HTML bytes

        Returns:
            ConversionResult with markdown and quality flags

        Raises:
            ConversionError: Conversion failed with typed failure category
        """
        try:
            # Decode HTML
            html_text = content.decode("utf-8", errors="replace")

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_text, "html.parser")

            # Extract main content area
            main_content = (
                soup.find("div", class_=re.compile(r"ltx_page"))
                or soup.find("article")
                or soup.find("body")
            )

            if not main_content:
                raise ConversionError(
                    "No main content found in arXiv HTML",
                    category="unsupported_format",
                    details={"reason": "missing_content_div"},
                )

            # Initialize quality flags
            quality_flags = QualityFlags()
            warnings: list[str] = []

            # Check for MathML presence
            math_elements = main_content.find_all("math")
            if math_elements:
                quality_flags.has_math = True
                quality_flags.math_preserved = True

            # Check for tables
            tables = main_content.find_all("table")
            if tables:
                quality_flags.has_tables = True

            # Check for figures
            figures = main_content.find_all("figure")
            if figures:
                quality_flags.has_figures = True
                # Check if figures have captions
                captions = [f.find("figcaption") for f in figures]
                quality_flags.figure_captions_present = any(captions)

            # Check for heading structure
            headings = main_content.find_all(re.compile(r"^h[1-6]$"))
            if headings:
                quality_flags.heading_structure_detected = True

            # Convert to markdown-like text
            # For MathML, preserve it as text markers
            markdown_parts: list[str] = []

            # Extract title
            title_elem = soup.find("h1", class_=re.compile(r"ltx_title"))
            if title_elem:
                markdown_parts.append(f"# {title_elem.get_text().strip()}\n")

            # Extract sections recursively
            sections = main_content.find_all("section", class_=re.compile(r"ltx_section"))
            for section in sections:
                markdown_parts.append(self._extract_section(section))

            # If no sections found, extract all paragraphs
            if not sections:
                paragraphs = main_content.find_all(["p", "div"], class_=re.compile(r"ltx_para"))
                for para in paragraphs:
                    markdown_parts.append(f"{para.get_text().strip()}\n\n")

            # Extract tables
            for table in tables:
                markdown_parts.append(self._extract_table(table))

            markdown = "\n".join(markdown_parts).strip()

            if not markdown:
                raise ConversionError(
                    "Extracted markdown is empty",
                    category="unsupported_format",
                    details={"reason": "empty_extraction"},
                )

            return ConversionResult(
                markdown=markdown,
                warnings=warnings,
                quality_flags=quality_flags,
                converter_name=self.name,
            )

        except ConversionError:
            raise
        except Exception as e:
            # Wrap unexpected exceptions
            raise ConversionError(
                f"ArXiv HTML conversion failed: {e}",
                category="unknown",
                details={"error": str(e)},
            ) from e

    def _extract_section(self, section_elem: Any) -> str:
        """Extract section with heading and content.

        Args:
            section_elem: BeautifulSoup section element

        Returns:
            Markdown-formatted section text
        """
        parts: list[str] = []

        # Extract heading
        heading = section_elem.find(re.compile(r"^h[1-6]$"))
        if heading:
            level = int(heading.name[1])
            parts.append(f"{'#' * level} {heading.get_text().strip()}\n")

        # Extract paragraphs
        paragraphs = section_elem.find_all(
            ["p", "div"], class_=re.compile(r"ltx_para"), recursive=False
        )
        for para in paragraphs:
            text = para.get_text().strip()
            if text:
                parts.append(f"{text}\n")

        return "\n".join(parts) + "\n"

    def _extract_table(self, table_elem: Any) -> str:
        """Extract table as markdown.

        Args:
            table_elem: BeautifulSoup table element

        Returns:
            Markdown-formatted table
        """
        rows = table_elem.find_all("tr")
        if not rows:
            return ""

        markdown_rows: list[str] = []
        for row in rows:
            cells = row.find_all(["th", "td"])
            cell_texts = [cell.get_text().strip() for cell in cells]
            markdown_rows.append("| " + " | ".join(cell_texts) + " |")

        # Add header separator after first row if it contains th elements
        if rows and rows[0].find("th"):
            num_cols = len(rows[0].find_all(["th", "td"]))
            markdown_rows.insert(1, "|" + " --- |" * num_cols)

        return "\n".join(markdown_rows) + "\n\n"


class PublisherHTMLConverter:
    """Publisher HTML converter with paywall detection.

    Converts publisher HTML documents to markdown with paywall detection
    and quality flag reporting. Handles various publisher HTML structures.

    Publisher HTML varies widely in structure, so this converter is more
    heuristic-based than the arXiv converter.
    """

    # Common paywall markers across publishers
    PAYWALL_MARKERS = [
        "login required",
        "access denied",
        "subscribe",
        "subscription required",
        "purchase article",
        "institutional access",
        "sign in to access",
        "paywall",
    ]

    @property
    def name(self) -> str:
        """Return converter name for provenance tracking."""
        return "PublisherHTMLConverter"

    def can_convert(self, format: SourceFormat) -> bool:
        """Check if this converter handles publisher HTML format.

        Args:
            format: Source format type

        Returns:
            True if format is "publisher_html", False otherwise
        """
        return format == "publisher_html"

    def validate_source(self, content: bytes) -> ValidationResult:
        """Validate publisher HTML content for body presence and paywall detection.

        Checks if the HTML contains body content (article text) and detects
        paywall markers. Also checks for truncation.

        Args:
            content: Raw HTML bytes

        Returns:
            ValidationResult with paywall and truncation flags
        """
        try:
            # Decode HTML
            html_text = content.decode("utf-8", errors="replace")

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_text, "html.parser")

            # Check for paywall markers (case-insensitive)
            html_lower = html_text.lower()
            is_paywall = any(marker in html_lower for marker in self.PAYWALL_MARKERS)

            # Check for body content - look for article/main/section elements
            has_body = bool(
                soup.find("article")
                or soup.find("main")
                or soup.find("section", class_=re.compile(r"article|content|body"))
                or soup.find("div", class_=re.compile(r"article|content|body"))
            )

            content_length = len(content)

            # Check for truncation (< 1KB for expected full document)
            is_truncated = content_length < 1024

            # Invalid if paywall detected or truncated or no body
            is_valid = has_body and not is_paywall and not is_truncated

            return ValidationResult(
                is_valid=is_valid,
                content_length=content_length,
                has_body_content=has_body,
                detected_content_type="text/html",
                is_paywall=is_paywall,
                is_truncated=is_truncated,
            )

        except Exception:
            # Failed to parse HTML
            return ValidationResult(
                is_valid=False,
                content_length=len(content),
                has_body_content=False,
                detected_content_type="unknown",
            )

    def convert(self, content: bytes) -> ConversionResult:
        """Convert publisher HTML to markdown.

        Extracts text and structure from publisher HTML. Detects tables,
        figures, and headings. Does not preserve MathML (varies by publisher).

        Args:
            content: Raw HTML bytes

        Returns:
            ConversionResult with markdown and quality flags

        Raises:
            ConversionError: Conversion failed with typed failure category
        """
        try:
            # Decode HTML
            html_text = content.decode("utf-8", errors="replace")

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_text, "html.parser")

            # Extract main content area
            main_content = (
                soup.find("article")
                or soup.find("main")
                or soup.find("section", class_=re.compile(r"article|content"))
                or soup.find("div", class_=re.compile(r"article|content"))
                or soup.find("body")
            )

            if not main_content:
                raise ConversionError(
                    "No main content found in publisher HTML",
                    category="unsupported_format",
                    details={"reason": "missing_content_element"},
                )

            # Initialize quality flags
            quality_flags = QualityFlags()
            warnings: list[str] = []

            # Check for tables
            tables = main_content.find_all("table")
            if tables:
                quality_flags.has_tables = True

            # Check for figures
            figures = main_content.find_all(["figure", "img"])
            if figures:
                quality_flags.has_figures = True
                # Check if figures have captions
                captions = [
                    f.find("figcaption") or f.find_next_sibling("p", class_=re.compile(r"caption"))
                    for f in figures
                ]
                quality_flags.figure_captions_present = any(captions)

            # Check for heading structure
            headings = main_content.find_all(re.compile(r"^h[1-6]$"))
            if headings:
                quality_flags.heading_structure_detected = True

            # Check for math (MathML or LaTeX markers)
            math_elements = main_content.find_all(
                ["math", "span"], class_=re.compile(r"math|katex|mathjax")
            )
            if math_elements:
                quality_flags.has_math = True
                # Publisher HTML may not preserve math well
                quality_flags.math_preserved = False
                warnings.append("Math content detected but may not be preserved accurately")

            # Convert to markdown-like text
            markdown_parts: list[str] = []

            # Extract title
            title_elem = soup.find("h1")
            if title_elem:
                markdown_parts.append(f"# {title_elem.get_text().strip()}\n")

            # Extract paragraphs and headings
            for elem in main_content.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p"]):
                if elem.name.startswith("h"):
                    level = int(elem.name[1])
                    markdown_parts.append(f"{'#' * level} {elem.get_text().strip()}\n")
                else:
                    text = elem.get_text().strip()
                    if text:
                        markdown_parts.append(f"{text}\n")

            # Extract tables
            for table in tables:
                markdown_parts.append(self._extract_table(table))

            markdown = "\n".join(markdown_parts).strip()

            if not markdown:
                raise ConversionError(
                    "Extracted markdown is empty",
                    category="unsupported_format",
                    details={"reason": "empty_extraction"},
                )

            return ConversionResult(
                markdown=markdown,
                warnings=warnings,
                quality_flags=quality_flags,
                converter_name=self.name,
            )

        except ConversionError:
            raise
        except Exception as e:
            # Wrap unexpected exceptions
            raise ConversionError(
                f"Publisher HTML conversion failed: {e}",
                category="unknown",
                details={"error": str(e)},
            ) from e

    def _extract_table(self, table_elem: Any) -> str:
        """Extract table as markdown.

        Args:
            table_elem: BeautifulSoup table element

        Returns:
            Markdown-formatted table
        """
        rows = table_elem.find_all("tr")
        if not rows:
            return ""

        markdown_rows: list[str] = []
        for row in rows:
            cells = row.find_all(["th", "td"])
            cell_texts = [cell.get_text().strip() for cell in cells]
            markdown_rows.append("| " + " | ".join(cell_texts) + " |")

        # Add header separator after first row if it contains th elements
        if rows and rows[0].find("th"):
            num_cols = len(rows[0].find_all(["th", "td"]))
            markdown_rows.insert(1, "|" + " --- |" * num_cols)

        return "\n".join(markdown_rows) + "\n\n"
