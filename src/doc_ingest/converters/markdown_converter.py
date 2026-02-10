"""Markdown converters for JATS XML and DOCX using Pandoc.

Converts JATS XML and DOCX documents to markdown via Pandoc subprocess,
with format-specific validation, quality flag reporting, and typed error handling.
"""

import re
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

from doc_ingest.types import (
    ConversionError,
    ConversionResult,
    QualityFlags,
    SourceFormat,
    ValidationResult,
)


class JATSPandocConverter:
    """JATS XML to markdown converter using Pandoc.

    Validates JATS XML for article/body tags and converts to markdown via Pandoc.
    Raises ConversionError with category="unsupported_format" for Pandoc failures.
    """

    @property
    def name(self) -> str:
        """Return converter name for provenance tracking."""
        return "JATSPandocConverter"

    def can_convert(self, format: SourceFormat) -> bool:
        """Check if this converter handles JATS XML format.

        Args:
            format: Source format type

        Returns:
            True if format is "jats_xml", False otherwise
        """
        return format == "jats_xml"

    def validate_source(self, content: bytes) -> ValidationResult:
        """Validate JATS XML for article/body tags.

        Checks for presence of <article> and <body> tags to ensure content
        is valid JATS XML with body content.

        Args:
            content: Raw JATS XML bytes

        Returns:
            ValidationResult with is_valid=False if article/body tags missing
        """
        try:
            # Decode and check for JATS structure
            text = content.decode("utf-8", errors="ignore")

            # Check for article tag
            has_article = bool(re.search(r"<article[>\s]", text, re.IGNORECASE))

            # Check for body tag
            has_body = bool(re.search(r"<body[>\s]", text, re.IGNORECASE))

            return ValidationResult(
                is_valid=has_article and has_body,
                content_length=len(content),
                has_body_content=has_body,
                detected_content_type="application/xml",
            )

        except Exception:
            # Failed to decode or parse
            return ValidationResult(
                is_valid=False,
                content_length=len(content),
                has_body_content=False,
                detected_content_type="unknown",
            )

    def convert(self, content: bytes) -> ConversionResult:
        """Convert JATS XML to markdown using Pandoc.

        Uses Pandoc subprocess with '-f jats -t markdown' to convert JATS XML
        to markdown. Detects tables, headings, and figure captions in output.

        Args:
            content: Raw JATS XML bytes

        Returns:
            ConversionResult with markdown, warnings, and quality flags

        Raises:
            ConversionError: Pandoc failed with category="unsupported_format"
        """
        tmp_path = None
        try:
            # Write content to temp file (Pandoc needs file input)
            with NamedTemporaryFile(mode="wb", suffix=".xml", delete=False) as tmp:
                tmp.write(content)
                tmp_path = Path(tmp.name)

            # Run Pandoc: jats -> markdown
            result = subprocess.run(
                ["pandoc", "-f", "jats", "-t", "markdown", str(tmp_path)],
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout
                check=False,
            )

            # Check for Pandoc failure before cleanup
            if result.returncode != 0:
                raise ConversionError(
                    f"Pandoc conversion failed: {result.stderr}",
                    category="unsupported_format",
                    details={"exit_code": result.returncode, "stderr": result.stderr},
                )

            markdown = result.stdout
            warnings = []

            # Include stderr as warnings if present (even on success)
            if result.stderr.strip():
                warnings.append(f"Pandoc warnings: {result.stderr.strip()}")

            # Detect quality flags
            quality_flags = self._detect_quality_flags(markdown)

            return ConversionResult(
                markdown=markdown,
                warnings=warnings,
                quality_flags=quality_flags,
                converter_name=self.name,
            )

        except subprocess.TimeoutExpired:
            raise ConversionError(
                "Pandoc conversion timed out after 60 seconds",
                category="conversion_timeout",
            )
        except FileNotFoundError:
            raise ConversionError(
                "Pandoc binary not found. Please install Pandoc.",
                category="unsupported_format",
                details={"missing_dependency": "pandoc"},
            )
        except ConversionError:
            # Re-raise ConversionError without wrapping
            raise
        except Exception as e:
            # Wrap unexpected errors
            raise ConversionError(
                f"Unexpected conversion error: {e}",
                category="unknown",
            ) from e
        finally:
            # Ensure cleanup even on exception
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()

    def _detect_quality_flags(self, markdown: str) -> QualityFlags:
        """Detect quality flags from markdown output.

        Args:
            markdown: Converted markdown text

        Returns:
            QualityFlags with detected features
        """
        # Table detection (markdown table syntax)
        has_tables = bool(re.search(r"\|.*\|", markdown))

        # Heading detection (markdown headings)
        heading_structure = bool(re.search(r"^#{1,6}\s+.+$", markdown, re.MULTILINE))

        # Figure caption detection (common JATS patterns)
        figure_captions = bool(
            re.search(r"!\[.*?\]\(.*?\)", markdown)  # Image with alt text
            or re.search(r"Figure \d+", markdown, re.IGNORECASE)
        )

        # Math detection (look for LaTeX math delimiters preserved by Pandoc)
        has_math = bool(re.search(r"\$.*?\$|\\\[.*?\\\]|\\\(.*?\\\)", markdown))

        return QualityFlags(
            has_tables=has_tables,
            tables_likely_corrupted=False,  # JATS tables generally preserve well
            has_math=has_math,
            math_preserved=has_math,  # Pandoc preserves JATS math as LaTeX
            has_figures=figure_captions,
            figure_captions_present=figure_captions,
            heading_structure_detected=heading_structure,
        )


class DOCXPandocConverter:
    """DOCX to markdown converter using Pandoc.

    Validates DOCX binary format (ZIP header) and converts to markdown via Pandoc.
    Raises ConversionError with category="unsupported_format" for Pandoc failures.
    """

    @property
    def name(self) -> str:
        """Return converter name for provenance tracking."""
        return "DOCXPandocConverter"

    def can_convert(self, format: SourceFormat) -> bool:
        """Check if this converter handles DOCX format.

        Args:
            format: Source format type

        Returns:
            True if format is "docx", False otherwise
        """
        return format == "docx"

    def validate_source(self, content: bytes) -> ValidationResult:
        """Validate DOCX binary format (ZIP header magic bytes).

        DOCX files are ZIP archives, so we check for the ZIP magic bytes (PK).

        Args:
            content: Raw DOCX bytes

        Returns:
            ValidationResult with is_valid=False if not a valid ZIP/DOCX
        """
        # DOCX files are ZIP archives, check for ZIP magic bytes
        is_zip = content[:2] == b"PK"

        return ValidationResult(
            is_valid=is_zip,
            content_length=len(content),
            has_body_content=is_zip,  # Assume body content if valid ZIP
            detected_content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            if is_zip
            else "unknown",
        )

    def convert(self, content: bytes) -> ConversionResult:
        """Convert DOCX to markdown using Pandoc.

        Uses Pandoc subprocess with '-f docx -t markdown' to convert DOCX
        to markdown. Detects tables, headings, and figure captions in output.

        Args:
            content: Raw DOCX bytes

        Returns:
            ConversionResult with markdown, warnings, and quality flags

        Raises:
            ConversionError: Pandoc failed with category="unsupported_format"
        """
        tmp_path = None
        try:
            # Write content to temp file (Pandoc needs file input)
            with NamedTemporaryFile(mode="wb", suffix=".docx", delete=False) as tmp:
                tmp.write(content)
                tmp_path = Path(tmp.name)

            # Run Pandoc: docx -> markdown
            result = subprocess.run(
                ["pandoc", "-f", "docx", "-t", "markdown", str(tmp_path)],
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout
                check=False,
            )

            # Check for Pandoc failure before cleanup
            if result.returncode != 0:
                raise ConversionError(
                    f"Pandoc conversion failed: {result.stderr}",
                    category="unsupported_format",
                    details={"exit_code": result.returncode, "stderr": result.stderr},
                )

            markdown = result.stdout
            warnings = []

            # Include stderr as warnings if present (even on success)
            if result.stderr.strip():
                warnings.append(f"Pandoc warnings: {result.stderr.strip()}")

            # Detect quality flags
            quality_flags = self._detect_quality_flags(markdown)

            return ConversionResult(
                markdown=markdown,
                warnings=warnings,
                quality_flags=quality_flags,
                converter_name=self.name,
            )

        except subprocess.TimeoutExpired:
            raise ConversionError(
                "Pandoc conversion timed out after 60 seconds",
                category="conversion_timeout",
            )
        except FileNotFoundError:
            raise ConversionError(
                "Pandoc binary not found. Please install Pandoc.",
                category="unsupported_format",
                details={"missing_dependency": "pandoc"},
            )
        except ConversionError:
            # Re-raise ConversionError without wrapping
            raise
        except Exception as e:
            # Wrap unexpected errors
            raise ConversionError(
                f"Unexpected conversion error: {e}",
                category="unknown",
            ) from e
        finally:
            # Ensure cleanup even on exception
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()

    def _detect_quality_flags(self, markdown: str) -> QualityFlags:
        """Detect quality flags from markdown output.

        Args:
            markdown: Converted markdown text

        Returns:
            QualityFlags with detected features
        """
        # Table detection (markdown table syntax)
        has_tables = bool(re.search(r"\|.*\|", markdown))

        # Heading detection (markdown headings)
        heading_structure = bool(re.search(r"^#{1,6}\s+.+$", markdown, re.MULTILINE))

        # Figure caption detection
        figure_captions = bool(
            re.search(r"!\[.*?\]\(.*?\)", markdown)  # Image with alt text
            or re.search(r"Figure \d+", markdown, re.IGNORECASE)
        )

        # Math detection (less common in DOCX, but Pandoc may preserve)
        has_math = bool(re.search(r"\$.*?\$|\\\[.*?\\\]|\\\(.*?\\\)", markdown))

        return QualityFlags(
            has_tables=has_tables,
            tables_likely_corrupted=False,  # DOCX tables generally convert well
            has_math=has_math,
            math_preserved=has_math,  # Pandoc attempts to preserve math
            has_figures=figure_captions,
            figure_captions_present=figure_captions,
            heading_structure_detected=heading_structure,
        )
