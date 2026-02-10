"""CLI interface for document ingestion pipeline.

Provides commands for ingesting scientific documents (DOI, arXiv, PMC, local files)
into structured markdown with provenance tracking.
"""

import re
import sys
from pathlib import Path
from typing import Literal

from doc_ingest.converters.registry import ConverterRegistry
from doc_ingest.discovery_cache import DiscoveryCache
from doc_ingest.extraction_orchestrator import ExtractionOrchestrator
from doc_ingest.outcome_classifier import OutcomeClassifier
from doc_ingest.provenance_manager import ProvenanceManager
from doc_ingest.result_writer import ResultWriter
from doc_ingest.source_discoverer import SourceDiscoverer
from doc_ingest.source_router import SourceRouter
from doc_ingest.types import DocumentIdentifiers
from doc_ingest.web_fetcher import WebFetcher

# Exit codes (as per spec 011)
EXIT_SUCCESS = 0
EXIT_PARTIAL = 1  # Partial success (batch operations)
EXIT_FATAL = 2  # Fatal error


# -------------------------------------------------------------------------
# Identifier Validation
# -------------------------------------------------------------------------


def validate_doi(value: str) -> bool:
    """Validate DOI format (10.xxxx/...).

    Args:
        value: Candidate DOI string

    Returns:
        True if valid DOI format

    Examples:
        >>> validate_doi("10.1234/example")
        True
        >>> validate_doi("10.1234")
        False
        >>> validate_doi("not-a-doi")
        False
    """
    # DOI format: 10.prefix/suffix
    # Prefix: digits, Suffix: any printable characters
    return bool(re.match(r"^10\.\d+/.+$", value))


def validate_arxiv_id(value: str) -> bool:
    """Validate arXiv ID format (YYMM.NNNNN or YYMM.NNNNNVN).

    Args:
        value: Candidate arXiv ID string

    Returns:
        True if valid arXiv ID format

    Examples:
        >>> validate_arxiv_id("2301.12345")
        True
        >>> validate_arxiv_id("2301.12345v2")
        True
        >>> validate_arxiv_id("not-an-arxiv-id")
        False
    """
    # arXiv ID format: YYMM.NNNNN or YYMM.NNNNNvN
    return bool(re.match(r"^\d{4}\.\d{4,5}(v\d+)?$", value))


def validate_pmc_id(value: str) -> bool:
    """Validate PubMed Central ID format (PMC followed by digits).

    Args:
        value: Candidate PMC ID string

    Returns:
        True if valid PMC ID format

    Examples:
        >>> validate_pmc_id("PMC1234567")
        True
        >>> validate_pmc_id("pmc1234567")
        True
        >>> validate_pmc_id("1234567")
        False
    """
    # PMC ID format: PMC followed by digits (case-insensitive)
    return bool(re.match(r"^PMC\d+$", value, re.IGNORECASE))


def parse_identifier(value: str) -> tuple[Literal["doi", "arxiv", "pmc", "local"], str] | None:
    """Parse identifier string and determine type.

    Args:
        value: Identifier string to parse

    Returns:
        Tuple of (type, normalized_value) if valid, None otherwise
        Type is one of: "doi", "arxiv", "pmc", "local"

    Examples:
        >>> parse_identifier("10.1234/example")
        ('doi', '10.1234/example')
        >>> parse_identifier("2301.12345")
        ('arxiv', '2301.12345')
        >>> parse_identifier("/path/to/file.pdf")
        ('local', '/path/to/file.pdf')
        >>> parse_identifier("invalid")
        None
    """
    # Try DOI first
    if validate_doi(value):
        return ("doi", value)

    # Try arXiv ID
    if validate_arxiv_id(value):
        return ("arxiv", value)

    # Try PMC ID
    if validate_pmc_id(value):
        return ("pmc", value.upper())  # Normalize to uppercase

    # Try local file path
    path = Path(value)
    if path.exists() and path.is_file():
        return ("local", str(path.absolute()))

    return None


def create_document_identifiers(identifier: str) -> DocumentIdentifiers | None:
    """Create DocumentIdentifiers from a single identifier string.

    Args:
        identifier: Identifier string (DOI, arXiv ID, PMC ID, or file path)

    Returns:
        DocumentIdentifiers if valid, None otherwise

    Examples:
        >>> ids = create_document_identifiers("10.1234/example")
        >>> ids.doi
        '10.1234/example'
        >>> ids = create_document_identifiers("invalid")
        >>> ids is None
        True
    """
    parsed = parse_identifier(identifier)
    if parsed is None:
        return None

    id_type, value = parsed
    if id_type == "doi":
        return DocumentIdentifiers(doi=value)
    elif id_type == "arxiv":
        return DocumentIdentifiers(arxiv_id=value)
    elif id_type == "pmc":
        return DocumentIdentifiers(pmc_id=value)
    elif id_type == "local":
        return DocumentIdentifiers(local_path=value)

    return None


# -------------------------------------------------------------------------
# Pipeline Construction
# -------------------------------------------------------------------------


def create_pipeline(
    output_dir: Path, cache_dir: Path | None = None
) -> tuple[SourceRouter, ResultWriter]:
    """Create extraction pipeline components.

    Args:
        output_dir: Output directory for extracted documents
        cache_dir: Cache directory for discovery cache (default: output_dir/.cache)

    Returns:
        Tuple of (SourceRouter, ResultWriter) for extraction and persistence

    Note:
        This function constructs all pipeline components with default settings.
        For custom configurations, construct components individually.
    """
    # Set up cache directory
    if cache_dir is None:
        cache_dir = output_dir / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Create components
    cache = DiscoveryCache(cache_dir=cache_dir, ttl_days=30)  # 30-day cache
    discoverer = SourceDiscoverer(cache=cache)
    fetcher = WebFetcher()
    registry = ConverterRegistry()
    orchestrator = ExtractionOrchestrator(registry=registry)
    classifier = OutcomeClassifier()
    provenance_manager = ProvenanceManager()
    result_writer = ResultWriter(provenance_manager=provenance_manager)

    # Create router
    router = SourceRouter(
        discoverer=discoverer,
        orchestrator=orchestrator,
        classifier=classifier,
        provenance_manager=provenance_manager,
        fetcher=fetcher,
    )

    return router, result_writer


# -------------------------------------------------------------------------
# Command Handlers
# -------------------------------------------------------------------------


def cmd_extract(
    identifier: str,
    output_dir: Path,
    format_override: str | None = None,
) -> int:
    """Handle 'extract' command for single document extraction.

    Args:
        identifier: DOI, arXiv ID, PMC ID, or local file path
        output_dir: Output directory for extracted documents
        format_override: Optional format override (pdf, jats_xml, arxiv_html, etc.)

    Returns:
        Exit code: 0 (success), 2 (fatal error)

    Prints:
        Status messages to stdout
        Error messages to stderr
    """
    # Validate identifier
    doc_ids = create_document_identifiers(identifier)
    if doc_ids is None:
        print(
            f"Error: Invalid identifier format: {identifier}",
            file=sys.stderr,
        )
        print(
            "Expected DOI (10.xxxx/...), arXiv ID (YYMM.NNNNN), PMC ID (PMC#####), or local file path",
            file=sys.stderr,
        )
        return EXIT_FATAL

    # Create output directory
    output_dir = output_dir.absolute()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create pipeline
    try:
        router, writer = create_pipeline(output_dir)
    except Exception as e:
        print(f"Error: Failed to initialize pipeline: {e}", file=sys.stderr)
        return EXIT_FATAL

    # Extract document
    print(f"Extracting: {identifier}")
    if format_override:
        print(f"Format override: {format_override}")

    try:
        result = router.extract(
            identifiers=doc_ids,
            output_dir=output_dir,
            format_override=format_override,
        )
    except Exception as e:
        print(f"Error: Extraction failed: {e}", file=sys.stderr)
        return EXIT_FATAL

    # Write results
    try:
        writer.write(output_dir=output_dir, result=result)
    except Exception as e:
        print(f"Error: Failed to write results: {e}", file=sys.stderr)
        return EXIT_FATAL

    # Report outcome
    outcome = result.provenance.outcome

    # Compute document hash from identifiers (same logic as ProvenanceManager)
    import hashlib

    id_type, id_value = result.provenance.document_id.primary_identifier()
    hash_input = f"{id_type}:{id_value}".encode()
    doc_hash = hashlib.sha256(hash_input).hexdigest()[:16]
    doc_dir = output_dir / doc_hash

    if outcome == "success":
        # Calculate output path
        markdown_path = doc_dir / "output.md"
        print(f"Success: {markdown_path}")
        print(f"Provenance: {doc_dir / 'provenance.json'}")

        # Report statistics
        if result.markdown:
            char_count = len(result.markdown)
            print(f"Content: {char_count:,} characters")

        return EXIT_SUCCESS

    elif outcome in ("partial", "failed"):
        failure_category = result.provenance.failure_category or "unknown"
        print(f"Failed: {outcome} (category: {failure_category})", file=sys.stderr)

        # Show attempted sources
        attempt_count = len(result.provenance.attempts)
        print(f"Tried {attempt_count} source(s)", file=sys.stderr)

        # Write provenance even on failure
        print(f"Provenance: {doc_dir / 'provenance.json'}", file=sys.stderr)

        return EXIT_FATAL

    else:
        print(f"Error: Unknown outcome: {outcome}", file=sys.stderr)
        return EXIT_FATAL
