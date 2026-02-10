"""CLI interface for document ingestion pipeline.

Provides commands for ingesting scientific documents (DOI, arXiv, PMC, local files)
into structured markdown with provenance tracking.
"""

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
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
from doc_ingest.types import DocumentIdentifiers, ProvenanceRecord
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


def cmd_extract_batch(
    input_file: Path,
    output_dir: Path,
) -> int:
    """Handle 'extract-batch' command for batch document extraction from JSONL.

    Args:
        input_file: Path to JSONL file with document identifiers
        output_dir: Output directory for extracted documents

    Returns:
        Exit code: 0 (all success), 1 (partial success), 2 (fatal error)

    JSONL Format:
        Each line should be a JSON object with one of:
        - {"doi": "10.1234/example"}
        - {"arxiv_id": "2301.12345"}
        - {"pmc_id": "PMC1234567"}
        - {"local_path": "/path/to/file.pdf"}

    Prints:
        Progress updates to stdout
        Error messages to stderr
    """
    # Validate input file exists
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}", file=sys.stderr)
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

    # Parse JSONL and extract documents
    total = 0
    success_count = 0
    partial_count = 0
    failed_count = 0
    errors: list[str] = []

    print(f"Processing batch: {input_file}")
    print(f"Output directory: {output_dir}")

    with input_file.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue  # Skip empty lines

            total += 1

            # Parse JSON
            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON on line {line_num}: {e}"
                print(f"Error: {error_msg}", file=sys.stderr)
                errors.append(error_msg)
                failed_count += 1
                continue

            # Create DocumentIdentifiers from JSON
            try:
                doc_ids = DocumentIdentifiers(**data)
            except Exception as e:
                error_msg = f"Invalid identifier on line {line_num}: {e}"
                print(f"Error: {error_msg}", file=sys.stderr)
                errors.append(error_msg)
                failed_count += 1
                continue

            # Extract document
            display_key = doc_ids.display_key()
            print(f"[{total}] Extracting: {display_key}")

            try:
                result = router.extract(
                    identifiers=doc_ids,
                    output_dir=output_dir,
                    format_override=None,
                )
                writer.write(output_dir=output_dir, result=result)

                # Track outcome
                outcome = result.provenance.outcome
                if outcome == "success":
                    success_count += 1
                    print(f"[{total}] Success: {display_key}")
                elif outcome == "partial":
                    partial_count += 1
                    print(f"[{total}] Partial: {display_key}", file=sys.stderr)
                else:  # failed
                    failed_count += 1
                    category = result.provenance.failure_category or "unknown"
                    print(f"[{total}] Failed: {display_key} ({category})", file=sys.stderr)

            except Exception as e:
                failed_count += 1
                error_msg = f"Extraction crashed for {display_key}: {e}"
                print(f"Error: {error_msg}", file=sys.stderr)
                errors.append(error_msg)

    # Print summary
    print("\nBatch extraction complete:")
    print(f"  Total: {total}")
    print(f"  Success: {success_count}")
    print(f"  Partial: {partial_count}")
    print(f"  Failed: {failed_count}")

    # Generate triage report if there were failures
    if partial_count > 0 or failed_count > 0:
        triage_path = output_dir / "triage_report.md"
        try:
            _generate_triage_report(output_dir, triage_path)
            print(f"\nTriage report: {triage_path}")
        except Exception as e:
            print(f"Warning: Failed to generate triage report: {e}", file=sys.stderr)

    # Determine exit code
    if failed_count > 0 or partial_count > 0:
        return EXIT_PARTIAL
    return EXIT_SUCCESS


def cmd_triage_report(
    output_dir: Path,
    report_path: Path | None = None,
) -> int:
    """Handle 'triage-report' command for analyzing provenance records.

    Args:
        output_dir: Output directory containing provenance records
        report_path: Optional path for triage report (default: output_dir/triage_report.md)

    Returns:
        Exit code: 0 (success), 2 (fatal error)

    Prints:
        Status messages to stdout
        Error messages to stderr
    """
    if not output_dir.exists():
        print(f"Error: Output directory not found: {output_dir}", file=sys.stderr)
        return EXIT_FATAL

    # Default report path
    if report_path is None:
        report_path = output_dir / "triage_report.md"

    # Generate report
    try:
        _generate_triage_report(output_dir, report_path)
        print(f"Triage report generated: {report_path}")
        return EXIT_SUCCESS
    except Exception as e:
        print(f"Error: Failed to generate triage report: {e}", file=sys.stderr)
        return EXIT_FATAL


def cmd_retry_failed(
    output_dir: Path,
) -> int:
    """Handle 'retry-failed' command for retrying failed documents.

    Args:
        output_dir: Output directory containing provenance records

    Returns:
        Exit code: 0 (all success), 1 (partial success), 2 (fatal error)

    Prints:
        Progress updates to stdout
        Error messages to stderr
    """
    if not output_dir.exists():
        print(f"Error: Output directory not found: {output_dir}", file=sys.stderr)
        return EXIT_FATAL

    # Create pipeline
    try:
        router, writer = create_pipeline(output_dir)
    except Exception as e:
        print(f"Error: Failed to initialize pipeline: {e}", file=sys.stderr)
        return EXIT_FATAL

    # Find all provenance files
    provenance_manager = ProvenanceManager()
    doc_dirs = [d for d in output_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]

    retry_count = 0
    success_count = 0
    partial_count = 0
    failed_count = 0

    print(f"Scanning: {output_dir}")

    for doc_dir in doc_dirs:
        provenance_file = doc_dir / "provenance.json"
        if not provenance_file.exists():
            continue

        # Load provenance
        try:
            provenance = provenance_manager.load(output_dir, doc_dir.name)
            if provenance is None:
                continue
        except Exception:
            continue  # Skip corrupted provenance files

        # Skip successful extractions
        if provenance.outcome == "success":
            continue

        # Retry failed/partial extractions
        retry_count += 1
        display_key = provenance.document_id.display_key()
        print(f"[{retry_count}] Retrying: {display_key}")

        try:
            result = router.extract(
                identifiers=provenance.document_id,
                output_dir=output_dir,
                format_override=None,
            )
            writer.write(output_dir=output_dir, result=result)

            # Track outcome
            outcome = result.provenance.outcome
            if outcome == "success":
                success_count += 1
                print(f"[{retry_count}] Success: {display_key}")
            elif outcome == "partial":
                partial_count += 1
                print(f"[{retry_count}] Partial: {display_key}", file=sys.stderr)
            else:  # failed
                failed_count += 1
                category = result.provenance.failure_category or "unknown"
                print(f"[{retry_count}] Failed: {display_key} ({category})", file=sys.stderr)

        except Exception as e:
            failed_count += 1
            print(f"Error: Retry crashed for {display_key}: {e}", file=sys.stderr)

    # Print summary
    if retry_count == 0:
        print("No failed documents found to retry")
        return EXIT_SUCCESS

    print("\nRetry complete:")
    print(f"  Retried: {retry_count}")
    print(f"  Success: {success_count}")
    print(f"  Partial: {partial_count}")
    print(f"  Failed: {failed_count}")

    # Determine exit code
    if failed_count > 0 or partial_count > 0:
        return EXIT_PARTIAL
    return EXIT_SUCCESS


def cmd_clear_cache(
    cache_dir: Path,
    identifier: str | None = None,
    max_age_days: int | None = None,
) -> int:
    """Handle 'clear-cache' command for invalidating discovery cache entries.

    Args:
        cache_dir: Cache directory (typically output_dir/.cache)
        identifier: Optional specific identifier to clear (e.g., "doi:10.1234/foo")
        max_age_days: Optional max age in days; entries older than this are cleared

    Returns:
        Exit code: 0 (success), 2 (fatal error)

    Prints:
        Status messages to stdout
        Error messages to stderr
    """
    if not cache_dir.exists():
        print(f"Error: Cache directory not found: {cache_dir}", file=sys.stderr)
        return EXIT_FATAL

    cache = DiscoveryCache(cache_dir=cache_dir, ttl_days=max_age_days or 30)

    if identifier is not None:
        # Clear specific identifier
        try:
            cache.invalidate(identifier)
            print(f"Cleared cache entry: {identifier}")
            return EXIT_SUCCESS
        except Exception as e:
            print(f"Error: Failed to clear cache entry: {e}", file=sys.stderr)
            return EXIT_FATAL

    elif max_age_days is not None:
        # Clear entries older than max_age_days
        try:
            cleared = cache.clear(max_age_days=max_age_days)
            print(f"Cleared {cleared} expired cache entries (older than {max_age_days} days)")
            return EXIT_SUCCESS
        except Exception as e:
            print(f"Error: Failed to clear expired entries: {e}", file=sys.stderr)
            return EXIT_FATAL

    else:
        # Clear all cache entries
        try:
            cleared = cache.clear(max_age_days=None)
            print(f"Cleared all {cleared} cache entries")
            return EXIT_SUCCESS
        except Exception as e:
            print(f"Error: Failed to clear cache: {e}", file=sys.stderr)
            return EXIT_FATAL


# -------------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------------


def _generate_triage_report(output_dir: Path, report_path: Path) -> None:
    """Generate triage report from provenance records.

    Args:
        output_dir: Output directory containing provenance records
        report_path: Path to write triage report

    Raises:
        Exception: If report generation fails
    """
    provenance_manager = ProvenanceManager()
    doc_dirs = [d for d in output_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]

    # Collect provenance records
    records: list[tuple[str, ProvenanceRecord]] = []
    for doc_dir in doc_dirs:
        provenance_file = doc_dir / "provenance.json"
        if not provenance_file.exists():
            continue

        try:
            provenance = provenance_manager.load(output_dir, doc_dir.name)
            if provenance is not None:
                records.append((doc_dir.name, provenance))
        except Exception:
            continue  # Skip corrupted files

    # Group by outcome
    success = [r for r in records if r[1].outcome == "success"]
    partial = [r for r in records if r[1].outcome == "partial"]
    failed = [r for r in records if r[1].outcome == "failed"]

    # Group failures by category
    failure_by_category: dict[str, list[tuple[str, ProvenanceRecord]]] = {}
    for doc_hash, record in partial + failed:
        category: str = record.failure_category if record.failure_category else "unknown"
        if category not in failure_by_category:
            failure_by_category[category] = []
        failure_by_category[category].append((doc_hash, record))

    # Generate report
    with report_path.open("w", encoding="utf-8") as f:
        f.write("# Document Extraction Triage Report\n\n")
        f.write(f"**Generated**: {datetime.now(timezone.utc).isoformat()}\n\n")

        f.write("## Summary\n\n")
        f.write(f"- **Total documents**: {len(records)}\n")
        f.write(f"- **Successful**: {len(success)}\n")
        f.write(f"- **Partial**: {len(partial)}\n")
        f.write(f"- **Failed**: {len(failed)}\n\n")

        # Failures by category
        if failure_by_category:
            f.write("## Failures by Category\n\n")
            for category, category_records in sorted(failure_by_category.items()):
                f.write(f"### {category} ({len(category_records)})\n\n")
                for doc_hash, record in category_records:
                    display_key = record.document_id.display_key()
                    f.write(f"- `{display_key}` (hash: {doc_hash})\n")
                    # Show attempted sources
                    if record.attempts:
                        f.write(f"  - Attempted {len(record.attempts)} source(s)\n")
                        for attempt in record.attempts:
                            f.write(f"    - {attempt['format']} ({attempt['outcome']})\n")
                f.write("\n")

        # Discovery errors
        records_with_discovery_errors = [
            (doc_hash, record) for doc_hash, record in records if record.discovery_errors
        ]
        if records_with_discovery_errors:
            f.write("## Discovery Errors\n\n")
            for doc_hash, record in records_with_discovery_errors:
                display_key = record.document_id.display_key()
                f.write(f"### {display_key}\n\n")
                for error in record.discovery_errors:
                    f.write(f"- {error}\n")
                f.write("\n")

        f.write("## Next Steps\n\n")
        f.write("1. Review failures by category to identify common issues\n")
        f.write("2. For `needs_ocr` failures, consider OCR preprocessing\n")
        f.write("3. For `paywall` failures, check access permissions\n")
        f.write("4. For `no_sources` failures, verify identifier validity\n")
        f.write("5. Use `retry-failed` command after addressing issues\n")
