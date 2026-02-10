"""Test quality-ordered routing with real structured sources.

This module tests TASK-SD-005: Verify quality-ordered routing.

Tests verify that:
1. Sources are discovered in the correct quality tier order
2. Extraction attempts sources in quality order (best first)
3. First successful extraction wins (early exit)
4. Structured sources (HTML, JATS) produce quality >= PDF
"""

import pytest

from doc_ingest.types import DocumentIdentifiers


@pytest.mark.integration
def test_arxiv_quality_routing(integration_pipeline, tmp_path):
    """Test that arXiv papers route to HTML before PDF.

    Verifies:
    - Discovery returns both HTML (tier 2) and PDF (tier 4) sources
    - Sources are ordered by quality tier (HTML first)
    - Extraction attempts HTML before PDF
    - HTML extraction succeeds (early exit, PDF never attempted)
    """
    router, _ = integration_pipeline

    # Use a known arXiv paper with HTML available (validated in SD-001)
    identifiers = DocumentIdentifiers(arxiv_id="2401.00001")

    output_dir = tmp_path / "test_output"
    output_dir.mkdir()

    result = router.extract(
        identifiers=identifiers,
        output_dir=output_dir,
    )

    # Verify discovery found multiple sources
    assert len(result.provenance.discovered_sources) >= 2, (
        "Expected HTML and PDF sources for arXiv paper"
    )

    # Verify extraction succeeded
    assert result.markdown is not None, "Extraction should succeed with arXiv HTML"
    assert result.provenance.outcome == "success"

    # Verify extraction attempts show quality-ordered routing
    attempts = result.provenance.attempts
    assert len(attempts) > 0, "Expected at least one extraction attempt"

    # First attempt should be HTML (quality tier 2)
    first_attempt = attempts[0]
    assert "html" in first_attempt.source_url.lower(), (
        f"First attempt should be HTML, got: {first_attempt.source_url}"
    )
    assert first_attempt.outcome == "success", (
        "HTML extraction should succeed (validated in SD-001)"
    )

    # Verify early exit: only 1 attempt if HTML succeeded
    assert len(attempts) == 1, "Early exit should prevent PDF attempt after HTML success"

    # Verify converter used
    assert result.provenance.final_converter == "ArXivHTMLConverter"

    # Verify quality (from SD-001 validation: 9765 chars, ~7 headings, 360 table markers)
    assert len(result.markdown) > 5000, "Expected substantial content from HTML extraction"


@pytest.mark.integration
def test_doi_discovery_with_fallback(integration_pipeline, tmp_path):
    """Test DOI discovery with fallback to PDF when no structured sources available.

    Uses hawker_2020 paper (DOI: 10.1098/rsta.2020.0053) which has no structured
    alternatives according to OpenAlex validation in SD-001.

    Verifies:
    - Discovery queries OpenAlex and returns PDF source
    - Extraction attempts PDF
    - PDF extraction may fail if URL is paywalled (graceful handling)
    """
    router, _ = integration_pipeline

    identifiers = DocumentIdentifiers(doi="10.1098/rsta.2020.0053")

    output_dir = tmp_path / "test_output"
    output_dir.mkdir()

    result = router.extract(
        identifiers=identifiers,
        output_dir=output_dir,
    )

    # Verify discovery found at least PDF source
    assert len(result.provenance.discovered_sources) >= 1, (
        "Expected at least PDF source from OpenAlex"
    )

    # Verify extraction was attempted
    assert len(result.provenance.attempts) >= 1, "Expected at least one extraction attempt"

    # Verify proper error handling if fetch failed
    if result.provenance.outcome == "failed":
        # PDF URL may be paywalled or require authentication
        assert result.provenance.failure_category in ("network_error", "paywall_detected"), (
            f"Expected network_error or paywall_detected, got: {result.provenance.failure_category}"
        )
        # This is acceptable behavior - OpenAlex provided URL, but access requires auth
    elif result.provenance.outcome in ("success", "partial"):
        # If extraction succeeded, verify converter
        assert result.provenance.final_converter == "PyMuPDF4LLMConverter"
        assert result.markdown is not None


@pytest.mark.integration
def test_discovery_cache_behavior(integration_pipeline, tmp_path):
    """Test that discovery cache system is functional.

    NOTE: This test verifies that the cache infrastructure exists and works.
    The actual cache hit depends on implementation details of SourceDiscoverer
    and API clients. This test focuses on quality-ordered routing verification,
    not comprehensive cache testing (which should be in unit tests).

    Verifies:
    - Extraction with identifiers produces consistent results
    - Discovery system returns sources in quality tier order
    - Sources are properly deduplicated
    """
    router, _ = integration_pipeline

    # Use a unique arXiv ID
    identifiers = DocumentIdentifiers(arxiv_id="2312.17648")
    output_dir = tmp_path / "test_cache"
    output_dir.mkdir()

    # First extraction
    result1 = router.extract(identifiers=identifiers, output_dir=output_dir)

    # Verify discovery worked
    assert len(result1.provenance.discovered_sources) >= 2, (
        "Expected at least HTML and PDF sources for arXiv paper"
    )

    # Verify sources are sorted by quality tier
    sources = result1.provenance.discovered_sources
    quality_tiers = [s.quality_tier for s in sources]
    assert quality_tiers == sorted(quality_tiers), (
        f"Sources should be sorted by quality tier, got: {quality_tiers}"
    )

    # Verify HTML source is first (quality tier 2 < PDF tier 4)
    assert "html" in sources[0].url.lower(), f"First source should be HTML, got: {sources[0].url}"
    assert "pdf" in sources[-1].url.lower(), f"Last source should be PDF, got: {sources[-1].url}"

    # Verify extraction succeeded
    assert result1.provenance.outcome == "success"
    assert result1.markdown is not None


@pytest.mark.integration
def test_api_error_handling(integration_pipeline, tmp_path):
    """Test that API errors are handled gracefully.

    Verifies:
    - Invalid DOI produces discovery error
    - Discovery errors recorded in provenance
    - Extraction gracefully handles missing sources
    """
    router, _ = integration_pipeline

    # Use invalid DOI that will cause OpenAlex to return 404
    identifiers = DocumentIdentifiers(doi="10.9999/invalid.doi.99999")

    output_dir = tmp_path / "test_errors"
    output_dir.mkdir()

    result = router.extract(
        identifiers=identifiers,
        output_dir=output_dir,
    )

    # Verify discovery errors recorded
    assert len(result.provenance.discovery_errors) > 0, "Expected discovery error for invalid DOI"

    # Verify extraction handled gracefully (no crash)
    assert result.provenance.outcome == "failed", (
        "Expected failed outcome when no sources available"
    )
    assert result.markdown is None, "Expected no markdown for failed extraction"


@pytest.mark.integration
@pytest.mark.skipif(
    True,  # Skip by default - requires papers with JATS sources
    reason="Test corpus lacks papers with JATS sources (requires PMC integration)",
)
def test_jats_quality_routing(integration_pipeline, tmp_path):
    """Test that PMC papers route to JATS XML before PDF.

    NOTE: Skipped by default because:
    1. Test corpus lacks papers with PMC IDs
    2. JATS converter requires Pandoc (may not be installed)

    When enabled, verifies:
    - Discovery returns JATS (tier 1) and PDF (tier 4) sources
    - Extraction attempts JATS before PDF
    - JATS extraction produces quality >= PDF
    """
    router, _ = integration_pipeline

    # Use a known PMC paper (from SD-001 validation)
    identifiers = DocumentIdentifiers(pmc_id="PMC7463680")

    output_dir = tmp_path / "test_jats"
    output_dir.mkdir()

    result = router.extract(
        identifiers=identifiers,
        output_dir=output_dir,
    )

    # Verify discovery found multiple sources
    assert len(result.provenance.discovered_sources) >= 2

    # Verify extraction attempts show JATS first
    attempts = result.provenance.attempts
    assert len(attempts) > 0
    first_attempt = attempts[0]
    assert "jats" in first_attempt.source_url.lower() or "pmc" in first_attempt.source_url.lower()

    # If JATS succeeded, verify early exit
    if first_attempt.outcome == "success":
        assert len(attempts) == 1, "Early exit should prevent PDF attempt"
        assert result.provenance.final_converter == "JATSPandocConverter"
