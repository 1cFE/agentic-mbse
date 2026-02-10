"""Extraction orchestrator for iterating sources and attempting conversions.

Spec 008: ExtractionOrchestrator executes the extraction loop by iterating source
candidates in quality order, fetching content, validating, attempting conversion,
and recording all attempts with outcomes.
"""

from collections.abc import Callable

from doc_ingest.converters.registry import ConverterRegistry
from doc_ingest.outcome_classifier import ExtractionAttempt
from doc_ingest.types import ConversionError, ConversionResult, SourceCandidate
from doc_ingest.web_fetcher import FetchError


class ExtractionOrchestrator:
    """Orchestrate extraction attempts across multiple source candidates.

    Iterates source candidates in quality order (sorted by tier), executing the
    fetch → validate → convert pipeline for each source. Records all attempts
    with outcomes and stops on first successful conversion (early exit optimization).

    The orchestrator handles three failure modes:
    1. Fetch failures (network errors, timeouts) → outcome="fetch_failed"
    2. Validation failures (paywall, truncation, no body) → outcome="validation_failed"
    3. Conversion failures (OCR needed, corruption) → outcome with typed failure_category

    Unexpected exceptions are caught and wrapped as ConversionError(category="unknown")
    to prevent the entire pipeline from crashing due to converter bugs.

    Example:
        >>> orchestrator = ExtractionOrchestrator(registry)
        >>> sources = [jats_source, arxiv_source, pdf_source]
        >>> attempts, result = orchestrator.orchestrate(sources, fetcher.fetch)
        >>> if result is not None:
        ...     print(f"Success: {result.markdown[:100]}")
        >>> else:
        ...     print(f"All {len(attempts)} sources failed")
    """

    def __init__(self, registry: ConverterRegistry) -> None:
        """Initialize orchestrator with converter registry.

        Args:
            registry: ConverterRegistry instance mapping formats to converters
        """
        self._registry = registry

    def orchestrate(
        self,
        sources: list[SourceCandidate],
        fetch_fn: Callable[[SourceCandidate], bytes],
    ) -> tuple[list[ExtractionAttempt], ConversionResult | None]:
        """Execute extraction loop across source candidates.

        Iterates sources in quality order (tier ascending, URL secondary sort),
        attempting fetch → validate → convert for each. Records all attempts
        and returns the first successful conversion.

        Args:
            sources: List of SourceCandidate objects to attempt
            fetch_fn: Callable that fetches content bytes from a source candidate
                     (typically WebFetcher.fetch)

        Returns:
            Tuple of (all_attempts, successful_result_or_None):
            - all_attempts: List of ExtractionAttempt records for each source tried
            - successful_result_or_None: ConversionResult if any source succeeded, else None

        Pipeline per source:
            1. Fetch content via fetch_fn
               - On FetchError → record outcome="fetch_failed", continue
            2. Get converter from registry
               - No converter → record outcome="validation_failed", continue
            3. Validate content via converter.validate_source()
               - is_valid=False → record outcome="validation_failed", continue
            4. Convert via converter.convert()
               - Success → record outcome="success", return early
               - ConversionError → record with failure_category, continue
               - Unexpected exception → wrap as category="unknown", continue

        Examples:
            >>> # Success case: JATS source succeeds, others skipped
            >>> sources = [jats, arxiv, pdf]  # sorted by quality tier
            >>> attempts, result = orchestrator.orchestrate(sources, fetch)
            >>> assert len(attempts) == 1
            >>> assert attempts[0].outcome == "success"
            >>> assert result is not None

            >>> # All fail case: record all attempts, no result
            >>> sources = [bad_jats, paywalled_html, scanned_pdf]
            >>> attempts, result = orchestrator.orchestrate(sources, fetch)
            >>> assert len(attempts) == 3
            >>> assert result is None
        """
        # Sort sources by quality tier (primary) and _sort_key (secondary)
        # SourceCandidate is @dataclass(order=True) with quality_tier and _sort_key fields
        sorted_sources = sorted(sources)

        all_attempts: list[ExtractionAttempt] = []
        successful_result: ConversionResult | None = None

        for source in sorted_sources:
            # Determine source URL for attempt record (prefer url, fallback to local_path)
            source_url = source.url if source.url is not None else source.local_path or ""

            # Step 1: Fetch content
            try:
                content = fetch_fn(source)
            except FetchError:
                # Record fetch failure and continue to next source
                all_attempts.append(
                    ExtractionAttempt(
                        source_url=source_url,
                        outcome="fetch_failed",
                        failure_category=None,
                        converter_name=None,
                    )
                )
                continue

            # Step 2: Get converter from registry
            converter = self._registry.get(source.format)
            if converter is None:
                # No converter available for this format
                # Record as validation_failed (format not supported)
                all_attempts.append(
                    ExtractionAttempt(
                        source_url=source_url,
                        outcome="validation_failed",
                        failure_category="unsupported_format",
                        converter_name=None,
                    )
                )
                continue

            # Step 3: Validate content
            try:
                validation_result = converter.validate_source(content)
            except Exception:
                # Validation raised unexpected exception
                # Wrap as ConversionError with category="unknown"
                all_attempts.append(
                    ExtractionAttempt(
                        source_url=source_url,
                        outcome="validation_failed",
                        failure_category="unknown",
                        converter_name=converter.name,
                    )
                )
                continue

            if not validation_result.is_valid:
                # Validation failed (paywall, truncation, no body, etc.)
                # Check for paywall flag to populate is_paywall field
                is_paywall = validation_result.is_paywall or False
                all_attempts.append(
                    ExtractionAttempt(
                        source_url=source_url,
                        outcome="validation_failed",
                        failure_category="source_validation_failed",
                        converter_name=converter.name,
                        is_paywall=is_paywall,
                    )
                )
                continue

            # Step 4: Attempt conversion
            try:
                result = converter.convert(content)
                # Success! Record attempt and return early
                all_attempts.append(
                    ExtractionAttempt(
                        source_url=source_url,
                        outcome="success",
                        failure_category=None,
                        converter_name=converter.name,
                    )
                )
                successful_result = result
                break  # Early exit on first success
            except ConversionError as e:
                # Conversion failed with typed category
                all_attempts.append(
                    ExtractionAttempt(
                        source_url=source_url,
                        outcome="validation_failed",  # Conversion errors also recorded as validation_failed
                        failure_category=e.category,
                        converter_name=converter.name,
                    )
                )
                continue
            except Exception:
                # Unexpected exception during conversion
                # Wrap as ConversionError with category="unknown"
                all_attempts.append(
                    ExtractionAttempt(
                        source_url=source_url,
                        outcome="validation_failed",
                        failure_category="unknown",
                        converter_name=converter.name,
                    )
                )
                continue

        return all_attempts, successful_result
