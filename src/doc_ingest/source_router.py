"""Top-level orchestrator coordinating discovery, extraction, and persistence.

Spec 007: SourceRouter coordinates the complete document extraction pipeline:
discovery → extraction → classification → persistence, with support for resumability
and format overrides.
"""

import time
from datetime import datetime, timezone
from pathlib import Path

from doc_ingest.extraction_orchestrator import ExtractionOrchestrator
from doc_ingest.outcome_classifier import OutcomeClassifier
from doc_ingest.provenance_manager import ProvenanceManager
from doc_ingest.source_discoverer import SourceDiscoverer
from doc_ingest.types import (
    ConversionResult,
    DocumentIdentifiers,
    ExtractionResult,
    ProvenanceRecord,
    SourceCandidate,
)
from doc_ingest.web_fetcher import WebFetcher

# Pipeline version for provenance tracking
PIPELINE_VERSION = "0.1.0"


class SourceRouter:
    """Coordinate document extraction pipeline from discovery to persistence.

    Top-level orchestrator that manages the complete extraction workflow:
    1. Check existing provenance for resumability
    2. Discover source candidates (or use format override)
    3. Orchestrate extraction attempts
    4. Classify final outcome
    5. Persist provenance (crash-safe via try/finally)

    Supports resumability: documents with outcome="success" are skipped on re-run,
    while failed/partial documents are retried.

    Example:
        >>> router = SourceRouter(discoverer, orchestrator, classifier, prov_manager)
        >>> identifiers = DocumentIdentifiers(doi="10.1234/example")
        >>> result = router.extract(identifiers, Path("output/"))
        >>> if result.markdown is not None:
        ...     print(f"Success: {len(result.markdown)} chars")
        >>> else:
        ...     print(f"Failed: {result.provenance.failure_category}")
    """

    def __init__(
        self,
        discoverer: SourceDiscoverer,
        orchestrator: ExtractionOrchestrator,
        classifier: OutcomeClassifier,
        provenance_manager: ProvenanceManager,
        fetcher: WebFetcher,
    ) -> None:
        """Initialize router with injected dependencies.

        Args:
            discoverer: SourceDiscoverer for finding source candidates
            orchestrator: ExtractionOrchestrator for extraction attempts
            classifier: OutcomeClassifier for outcome determination
            provenance_manager: ProvenanceManager for persistence
            fetcher: WebFetcher for content retrieval
        """
        self._discoverer = discoverer
        self._orchestrator = orchestrator
        self._classifier = classifier
        self._provenance_manager = provenance_manager
        self._fetcher = fetcher

    def extract(
        self,
        identifiers: DocumentIdentifiers,
        output_dir: Path,
        format_override: str | None = None,
    ) -> ExtractionResult:
        """Coordinate extraction for a document.

        Executes the complete extraction pipeline:
        1. Check for existing provenance (resumability)
        2. Discover sources (or use format override)
        3. Orchestrate extraction
        4. Classify outcome
        5. Persist provenance (try/finally for crash safety)

        Args:
            identifiers: Document identifiers to extract
            output_dir: Base output directory for results
            format_override: Optional format to force (skips discovery)

        Returns:
            ExtractionResult with markdown (if successful) and provenance

        Examples:
            >>> # Normal extraction with discovery
            >>> result = router.extract(
            ...     DocumentIdentifiers(doi="10.1234/example"),
            ...     Path("output/")
            ... )

            >>> # Format override (skip discovery, force PDF)
            >>> result = router.extract(
            ...     DocumentIdentifiers(local_path="paper.pdf"),
            ...     Path("output/"),
            ...     format_override="pdf"
            ... )
        """
        start_time = time.time()

        # Step 1: Check for existing provenance (resumability)
        document_hash = self._provenance_manager._compute_hash(identifiers)
        existing_provenance = self._provenance_manager.load(output_dir, document_hash)

        if existing_provenance is not None and existing_provenance.outcome == "success":
            # Skip extraction, return cached result
            # Try to load existing markdown from output.md
            doc_dir = output_dir / document_hash
            markdown_path = doc_dir / "output.md"
            markdown = None
            if markdown_path.exists():
                try:
                    markdown = markdown_path.read_text(encoding="utf-8")
                except OSError:
                    pass  # Failed to read, treat as missing

            return ExtractionResult(
                markdown=markdown,
                provenance=existing_provenance,
            )

        # Initialize extraction state
        discovered_sources: list[SourceCandidate] = []
        discovery_errors: list[str] = []
        discovery_cached = False
        extraction_result: ConversionResult | None = None
        attempts: list = []

        try:
            # Step 2: Discovery (or format override)
            if format_override is not None:
                # Format override: skip discovery, create single source candidate
                # Use local_path if present, otherwise create stub URL
                if identifiers.local_path is not None:
                    source_location = identifiers.local_path
                    discovered_sources = [
                        SourceCandidate(
                            quality_tier=1,  # Single source, tier doesn't matter
                            format=format_override,  # type: ignore[arg-type]
                            local_path=source_location,
                            discovered_via="format_override",
                        )
                    ]
                else:
                    # No local path, create stub URL (for testing or remote sources)
                    primary_type, primary_value = identifiers.primary_identifier()
                    source_location = f"stub://{primary_type}/{primary_value}"
                    discovered_sources = [
                        SourceCandidate(
                            quality_tier=1,
                            format=format_override,  # type: ignore[arg-type]
                            url=source_location,
                            discovered_via="format_override",
                        )
                    ]
            else:
                # Normal discovery
                discovered_sources, discovery_errors = self._discoverer.discover(identifiers)
                # Check if sources came from cache
                # (simplified: assume cached if discoverer returned quickly)
                discovery_cached = False  # TODO: Add cache hit tracking to discoverer

            # Step 3: Orchestrate extraction
            if discovered_sources:
                attempts, extraction_result = self._orchestrator.orchestrate(
                    discovered_sources,
                    self._fetcher.fetch,
                )

            # Step 4: Classify outcome
            outcome, failure_category = self._classifier.classify(attempts, discovery_errors)

            # Determine final converter name
            final_converter = None
            if extraction_result is not None:
                final_converter = extraction_result.converter_name

            # Calculate elapsed time
            elapsed_seconds = time.time() - start_time

            # Build provenance record
            provenance = ProvenanceRecord(
                document_id=identifiers,
                discovered_sources=discovered_sources,
                discovery_errors=discovery_errors,
                discovery_cached=discovery_cached,
                attempts=attempts,
                outcome=outcome,
                final_converter=final_converter,
                failure_category=failure_category,
                created_at=datetime.now(timezone.utc).isoformat(),
                pipeline_version=PIPELINE_VERSION,
                total_elapsed_seconds=elapsed_seconds,
            )

            return ExtractionResult(
                markdown=extraction_result.markdown if extraction_result else None,
                provenance=provenance,
            )

        finally:
            # Step 5: Always persist provenance (crash-safe)
            # Build provenance record even if extraction failed/crashed
            elapsed_seconds = time.time() - start_time

            # If we haven't classified yet (exception during extraction), classify now
            if "outcome" not in locals():
                outcome, failure_category = self._classifier.classify(attempts, discovery_errors)
                final_converter = None
                if "extraction_result" in locals() and extraction_result is not None:
                    final_converter = extraction_result.converter_name

            # Build final provenance record
            final_provenance = ProvenanceRecord(
                document_id=identifiers,
                discovered_sources=discovered_sources,
                discovery_errors=discovery_errors,
                discovery_cached=discovery_cached,
                attempts=attempts,
                outcome=outcome,
                final_converter=final_converter,
                failure_category=failure_category,
                created_at=datetime.now(timezone.utc).isoformat(),
                pipeline_version=PIPELINE_VERSION,
                total_elapsed_seconds=elapsed_seconds,
            )

            # Write provenance atomically
            try:
                self._provenance_manager.write(output_dir, final_provenance)
            except OSError:
                # Best effort: if provenance write fails, don't crash the whole pipeline
                pass
