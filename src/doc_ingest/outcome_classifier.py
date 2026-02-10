"""Classify document extraction outcomes and failure categories.

Spec 006: OutcomeClassifier determines the final extraction outcome (success, partial,
failed) based on extraction attempts and discovery errors, with typed failure categories.
"""

from dataclasses import dataclass
from typing import Literal

from doc_ingest.types import FailureCategory

# Outcome types
DocumentOutcome = Literal["success", "partial", "failed"]


@dataclass
class ExtractionAttempt:
    """Record of a single extraction attempt from a source.

    Attributes:
        source_url: URL or path of the source attempted
        outcome: Result of this specific attempt (success, validation_failed, fetch_failed, timeout)
        failure_category: Typed category if this attempt failed (None if successful)
        converter_name: Name of the converter used for this attempt
        is_paywall: Whether paywall detection triggered (relevant for validation failures)
    """

    source_url: str
    outcome: Literal["success", "validation_failed", "fetch_failed", "timeout"]
    failure_category: FailureCategory | None = None
    converter_name: str | None = None
    is_paywall: bool = False


class OutcomeClassifier:
    """Classify final extraction outcome and assign failure category.

    Determines the overall document extraction result based on individual extraction
    attempts and any discovery-level errors. Uses typed failure categories from
    ConversionError rather than parsing error strings.

    Prioritization logic:
    - If any attempt succeeded → ("success", None)
    - If all failed, use most recent non-"unknown" failure category
    - Fallback to heuristic categorization for discovery errors
    """

    def classify(
        self,
        attempts: list[ExtractionAttempt],
        discovery_errors: list[str],
    ) -> tuple[DocumentOutcome, FailureCategory | None]:
        """Determine outcome and failure category.

        Args:
            attempts: List of extraction attempts (may be empty)
            discovery_errors: List of errors from source discovery phase

        Returns:
            Tuple of (outcome, failure_category_or_None)
            - outcome is "success", "partial", or "failed"
            - failure_category is None for success, otherwise a FailureCategory

        Examples:
            >>> classifier = OutcomeClassifier()
            >>> # Successful extraction
            >>> attempts = [ExtractionAttempt(source_url="http://example.com", outcome="success")]
            >>> classifier.classify(attempts, [])
            ("success", None)
            >>> # All failed with OCR needed
            >>> attempts = [ExtractionAttempt(
            ...     source_url="http://example.com",
            ...     outcome="validation_failed",
            ...     failure_category="needs_ocr"
            ... )]
            >>> classifier.classify(attempts, [])
            ("failed", "needs_ocr")
        """
        # Edge case: No attempts and no discovery errors
        if not attempts and not discovery_errors:
            return ("failed", "no_source_found")

        # Edge case: No attempts but discovery errors exist
        if not attempts and discovery_errors:
            return ("failed", "api_error")

        # Check for any successful attempts
        if any(attempt.outcome == "success" for attempt in attempts):
            return ("success", None)

        # All attempts failed — determine failure category
        return self._classify_failure(attempts)

    def _classify_failure(
        self, attempts: list[ExtractionAttempt]
    ) -> tuple[DocumentOutcome, FailureCategory]:
        """Determine failure category from failed attempts.

        Strategy:
        1. Check for paywall detection in validation failures
        2. Check for fetch failures → network_error
        3. Check for timeout → conversion_timeout
        4. Use most recent non-"unknown" failure category
        5. Fallback to "unknown" if all categories are unknown

        Args:
            attempts: List of extraction attempts (all assumed to have failed)

        Returns:
            Tuple of ("failed", failure_category)
        """
        # Check for paywall detection in any validation failure
        if any(
            attempt.outcome == "validation_failed" and attempt.is_paywall for attempt in attempts
        ):
            return ("failed", "source_validation_failed")

        # Check for fetch failures → network_error
        if all(attempt.outcome == "fetch_failed" for attempt in attempts):
            return ("failed", "network_error")

        # Check for timeouts → conversion_timeout
        if all(attempt.outcome == "timeout" for attempt in attempts):
            return ("failed", "conversion_timeout")

        # Find most recent non-"unknown" failure category
        # Iterate in reverse (most recent first)
        for attempt in reversed(attempts):
            if attempt.failure_category is not None and attempt.failure_category != "unknown":
                return ("failed", attempt.failure_category)

        # Fallback: all categories are unknown
        return ("failed", "unknown")
