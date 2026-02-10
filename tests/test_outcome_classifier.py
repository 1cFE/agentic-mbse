"""Tests for OutcomeClassifier (spec 006).

Verifies outcome classification logic and failure category assignment based on
extraction attempts and discovery errors.
"""

import pytest

from doc_ingest.outcome_classifier import ExtractionAttempt, OutcomeClassifier


class TestOutcomeClassifier:
    """Test suite for OutcomeClassifier.classify()."""

    @pytest.fixture
    def classifier(self) -> OutcomeClassifier:
        """Create a fresh OutcomeClassifier instance."""
        return OutcomeClassifier()

    # Success cases

    def test_classify_success_with_one_successful_attempt(
        self, classifier: OutcomeClassifier
    ) -> None:
        """Given at least one attempt with outcome="success", when classified, then return ("success", None)."""
        attempts = [
            ExtractionAttempt(
                source_url="http://example.com/paper.pdf",
                outcome="success",
                converter_name="pdf_converter",
            )
        ]
        outcome, category = classifier.classify(attempts, [])
        assert outcome == "success"
        assert category is None

    def test_classify_success_with_multiple_attempts_one_succeeds(
        self, classifier: OutcomeClassifier
    ) -> None:
        """Given multiple attempts where at least one succeeds, then return ("success", None)."""
        attempts = [
            ExtractionAttempt(
                source_url="http://example.com/bad.pdf",
                outcome="validation_failed",
                failure_category="needs_ocr",
            ),
            ExtractionAttempt(
                source_url="http://example.com/good.html",
                outcome="success",
                converter_name="html_converter",
            ),
        ]
        outcome, category = classifier.classify(attempts, [])
        assert outcome == "success"
        assert category is None

    # Failure category assignment

    def test_classify_failed_with_needs_ocr_category(self, classifier: OutcomeClassifier) -> None:
        """Given all attempts failed and most recent has failure_category="needs_ocr", then return ("failed", "needs_ocr")."""
        attempts = [
            ExtractionAttempt(
                source_url="http://example.com/paper.pdf",
                outcome="validation_failed",
                failure_category="needs_ocr",
            )
        ]
        outcome, category = classifier.classify(attempts, [])
        assert outcome == "failed"
        assert category == "needs_ocr"

    def test_classify_failed_with_table_corruption_category(
        self, classifier: OutcomeClassifier
    ) -> None:
        """Given failure_category="table_corruption", then return it."""
        attempts = [
            ExtractionAttempt(
                source_url="http://example.com/paper.pdf",
                outcome="validation_failed",
                failure_category="table_corruption",
            )
        ]
        outcome, category = classifier.classify(attempts, [])
        assert outcome == "failed"
        assert category == "table_corruption"

    def test_classify_prioritizes_most_recent_non_unknown_category(
        self, classifier: OutcomeClassifier
    ) -> None:
        """Given multiple failures, prioritize most recent non-"unknown" category."""
        attempts = [
            ExtractionAttempt(
                source_url="http://example.com/old.pdf",
                outcome="validation_failed",
                failure_category="needs_ocr",
            ),
            ExtractionAttempt(
                source_url="http://example.com/middle.html",
                outcome="validation_failed",
                failure_category="unknown",  # Should be skipped
            ),
            ExtractionAttempt(
                source_url="http://example.com/recent.xml",
                outcome="validation_failed",
                failure_category="table_corruption",  # Most recent non-unknown
            ),
        ]
        outcome, category = classifier.classify(attempts, [])
        assert outcome == "failed"
        assert category == "table_corruption"

    # Edge cases from spec

    def test_classify_no_attempts_no_errors_returns_no_source_found(
        self, classifier: OutcomeClassifier
    ) -> None:
        """Given no attempts and no discovery errors, then return ("failed", "no_source_found")."""
        outcome, category = classifier.classify([], [])
        assert outcome == "failed"
        assert category == "no_source_found"

    def test_classify_no_attempts_with_discovery_errors_returns_api_error(
        self, classifier: OutcomeClassifier
    ) -> None:
        """Given no attempts and discovery_errors is non-empty, then return ("failed", "api_error")."""
        discovery_errors = ["Failed to fetch metadata from API"]
        outcome, category = classifier.classify([], discovery_errors)
        assert outcome == "failed"
        assert category == "api_error"

    def test_classify_all_validation_failed_with_paywall_returns_source_validation_failed(
        self, classifier: OutcomeClassifier
    ) -> None:
        """Given all attempts have outcome="validation_failed" and at least one has is_paywall=True, then return ("failed", "source_validation_failed")."""
        attempts = [
            ExtractionAttempt(
                source_url="http://example.com/paper.pdf",
                outcome="validation_failed",
                failure_category="source_validation_failed",
                is_paywall=True,
            )
        ]
        outcome, category = classifier.classify(attempts, [])
        assert outcome == "failed"
        assert category == "source_validation_failed"

    def test_classify_multiple_validation_failures_one_paywall(
        self, classifier: OutcomeClassifier
    ) -> None:
        """Given multiple validation failures where one is a paywall, then return source_validation_failed."""
        attempts = [
            ExtractionAttempt(
                source_url="http://example.com/ok.pdf",
                outcome="validation_failed",
                failure_category="needs_ocr",
                is_paywall=False,
            ),
            ExtractionAttempt(
                source_url="http://example.com/blocked.html",
                outcome="validation_failed",
                failure_category="source_validation_failed",
                is_paywall=True,
            ),
        ]
        outcome, category = classifier.classify(attempts, [])
        assert outcome == "failed"
        assert category == "source_validation_failed"

    def test_classify_all_fetch_failed_returns_network_error(
        self, classifier: OutcomeClassifier
    ) -> None:
        """Given all attempts have outcome="fetch_failed", then return ("failed", "network_error")."""
        attempts = [
            ExtractionAttempt(
                source_url="http://example.com/paper.pdf",
                outcome="fetch_failed",
                failure_category="network_error",
            ),
            ExtractionAttempt(
                source_url="http://example.com/backup.html",
                outcome="fetch_failed",
                failure_category="network_error",
            ),
        ]
        outcome, category = classifier.classify(attempts, [])
        assert outcome == "failed"
        assert category == "network_error"

    def test_classify_all_timeout_returns_conversion_timeout(
        self, classifier: OutcomeClassifier
    ) -> None:
        """Given all attempts have outcome="timeout", then return ("failed", "conversion_timeout")."""
        attempts = [
            ExtractionAttempt(
                source_url="http://example.com/slow.pdf",
                outcome="timeout",
                failure_category="conversion_timeout",
            )
        ]
        outcome, category = classifier.classify(attempts, [])
        assert outcome == "failed"
        assert category == "conversion_timeout"

    def test_classify_all_unknown_returns_unknown(self, classifier: OutcomeClassifier) -> None:
        """Given all attempts have failure_category="unknown", then return ("failed", "unknown")."""
        attempts = [
            ExtractionAttempt(
                source_url="http://example.com/mysterious.pdf",
                outcome="validation_failed",
                failure_category="unknown",
            ),
            ExtractionAttempt(
                source_url="http://example.com/mysterious2.html",
                outcome="validation_failed",
                failure_category="unknown",
            ),
        ]
        outcome, category = classifier.classify(attempts, [])
        assert outcome == "failed"
        assert category == "unknown"

    # Failure category variety

    def test_classify_all_failure_categories(self, classifier: OutcomeClassifier) -> None:
        """Verify all FailureCategory values can be returned."""
        test_cases = [
            ("needs_ocr", "needs_ocr"),
            ("table_corruption", "table_corruption"),
            ("unsupported_format", "unsupported_format"),
            ("api_error", "api_error"),
            ("network_error", "network_error"),
            ("unknown", "unknown"),
        ]

        for input_category, expected_category in test_cases:
            attempts = [
                ExtractionAttempt(
                    source_url="http://example.com/test.pdf",
                    outcome="validation_failed",
                    failure_category=input_category,  # type: ignore[arg-type]
                )
            ]
            outcome, category = classifier.classify(attempts, [])
            assert outcome == "failed"
            assert category == expected_category

    # Mixed outcome types

    def test_classify_mixed_outcomes_fetch_and_validation_failures(
        self, classifier: OutcomeClassifier
    ) -> None:
        """Given mixed fetch_failed and validation_failed outcomes, use most recent category."""
        attempts = [
            ExtractionAttempt(
                source_url="http://example.com/first.pdf",
                outcome="fetch_failed",
                failure_category="network_error",
            ),
            ExtractionAttempt(
                source_url="http://example.com/second.html",
                outcome="validation_failed",
                failure_category="needs_ocr",  # Most recent
            ),
        ]
        outcome, category = classifier.classify(attempts, [])
        assert outcome == "failed"
        # Should prioritize most recent non-unknown category
        assert category == "needs_ocr"

    def test_classify_ignores_discovery_errors_when_attempts_exist(
        self, classifier: OutcomeClassifier
    ) -> None:
        """Discovery errors are only used when no attempts exist."""
        attempts = [
            ExtractionAttempt(
                source_url="http://example.com/paper.pdf",
                outcome="validation_failed",
                failure_category="needs_ocr",
            )
        ]
        discovery_errors = ["Some discovery error"]
        outcome, category = classifier.classify(attempts, discovery_errors)
        assert outcome == "failed"
        # Should use attempt category, not api_error from discovery
        assert category == "needs_ocr"
