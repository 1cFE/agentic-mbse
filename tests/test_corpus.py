"""Real-world corpus test suite.

This module provides comprehensive testing against a corpus of real academic papers.
Tests are marked with @pytest.mark.corpus and only run with --run-corpus flag to
prevent slow tests from blocking development workflow.

The test corpus measures extraction quality through metrics comparison against
baseline extractions, ensuring the pipeline maintains or improves quality across
versions.
"""

import json
import time
from pathlib import Path
from typing import Any

import pytest

from doc_ingest.converters.pdf_converter import PyMuPDF4LLMConverter
from tests.corpus.metrics import ExtractionMetrics, compare_metrics, compute_metrics

# Test corpus paths
CORPUS_DIR = Path(__file__).parent / "corpus"
PAPERS_FILE = CORPUS_DIR / "papers.jsonl"
BASELINE_DIR = CORPUS_DIR / "baseline"
CURRENT_DIR = CORPUS_DIR / "current"
PDFS_DIR = CORPUS_DIR / "pdfs"


def load_corpus_papers() -> list[dict[str, Any]]:
    """Load corpus registry from papers.jsonl.

    Returns:
        List of paper metadata dictionaries with keys:
        slug, pdf_path, source, has_tables, has_math, pages
    """
    papers = []
    with PAPERS_FILE.open() as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                papers.append(json.loads(line))
    return papers


def extract_paper_with_current_pipeline(pdf_path: Path) -> tuple[str, float]:
    """Extract a paper using the current PDF converter pipeline.

    This function measures what the current implementation produces, so we can
    compare against baseline extractions. Currently uses PyMuPDF4LLMConverter
    directly, but will be updated to use the full extraction pipeline in Phase 2.

    Args:
        pdf_path: Path to the PDF file to extract

    Returns:
        Tuple of (markdown_text, elapsed_seconds)

    Raises:
        Exception: If extraction fails
    """
    start_time = time.time()

    # Read PDF bytes
    pdf_bytes = pdf_path.read_bytes()

    # Extract using current converter
    converter = PyMuPDF4LLMConverter()
    result = converter.convert(pdf_bytes)

    elapsed = time.time() - start_time

    if result.markdown is None:
        raise ValueError(f"Extraction produced no markdown for {pdf_path}")

    return result.markdown, elapsed


def save_extraction_result(slug: str, markdown: str, metrics: ExtractionMetrics) -> None:
    """Save extraction result and metrics to current/ directory.

    Creates:
    - tests/corpus/current/{slug}/full_document.md
    - tests/corpus/current/{slug}/metrics.json

    Args:
        slug: Document slug (identifier)
        markdown: Extracted markdown text
        metrics: Computed extraction metrics
    """
    # Create output directory
    output_dir = CURRENT_DIR / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save markdown
    markdown_path = output_dir / "full_document.md"
    markdown_path.write_text(markdown, encoding="utf-8")

    # Save metrics
    metrics_path = output_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics.to_dict(), indent=2), encoding="utf-8")


def load_baseline_metrics(slug: str) -> ExtractionMetrics | None:
    """Load baseline metrics for a paper.

    Args:
        slug: Document slug (identifier)

    Returns:
        ExtractionMetrics if baseline exists, None otherwise
    """
    metrics_path = BASELINE_DIR / slug / "metrics.json"
    if not metrics_path.exists():
        return None

    with metrics_path.open() as f:
        data = json.load(f)
        return ExtractionMetrics.from_dict(data)


@pytest.mark.corpus
class TestCorpus:
    """Real-world corpus test suite.

    These tests run the current extraction pipeline against real academic papers
    and compare quality metrics against baseline extractions. Tests only run when
    pytest is invoked with --run-corpus flag.
    """

    def test_all_papers_extract_successfully(self) -> None:
        """Every paper in papers.jsonl must produce non-empty output.

        This test ensures the extraction pipeline can handle all test papers
        without crashing or producing empty output. It saves extraction results
        to tests/corpus/current/{slug}/ for later analysis.
        """
        papers = load_corpus_papers()
        assert len(papers) > 0, "Corpus must contain at least one paper"

        failures = []

        for paper in papers:
            slug = paper["slug"]
            pdf_path = Path(paper["pdf_path"])

            # Check PDF exists
            if not pdf_path.exists():
                failures.append(f"{slug}: PDF not found at {pdf_path}")
                continue

            # Attempt extraction
            try:
                markdown, elapsed = extract_paper_with_current_pipeline(pdf_path)

                # Verify non-empty
                if len(markdown.strip()) == 0:
                    failures.append(f"{slug}: extraction produced empty markdown")
                    continue

                # Compute metrics
                metrics = compute_metrics(markdown, elapsed)

                # Save results
                save_extraction_result(slug, markdown, metrics)

            except Exception as e:
                failures.append(f"{slug}: extraction failed with {type(e).__name__}: {e}")

        # Report all failures together
        if failures:
            pytest.fail("Extraction failures:\n" + "\n".join(f"  - {f}" for f in failures))

    def test_no_quality_regression_vs_baseline(self) -> None:
        """Current extraction must not lose >10% on any key metric vs baseline.

        This test compares current extraction quality against baseline extractions
        from fusion-tea. Regressions exceeding 10% on char_count, heading_count,
        or table_row_count cause test failure.

        Papers without baselines are skipped (must pass test_all_papers_extract_successfully first).
        """
        papers = load_corpus_papers()
        regressions = []

        for paper in papers:
            slug = paper["slug"]

            # Load baseline metrics
            baseline_metrics = load_baseline_metrics(slug)
            if baseline_metrics is None:
                # No baseline to compare against, skip
                continue

            # Load current metrics
            current_metrics_path = CURRENT_DIR / slug / "metrics.json"
            if not current_metrics_path.exists():
                # Current extraction doesn't exist yet (previous test failed or didn't run)
                pytest.skip(
                    f"Current metrics not found for {slug} - "
                    "run test_all_papers_extract_successfully first"
                )

            with current_metrics_path.open() as f:
                current_data = json.load(f)
                current_metrics = ExtractionMetrics.from_dict(current_data)

            # Compare metrics
            comparison = compare_metrics(baseline_metrics, current_metrics)

            # Check for regressions (>10% loss)
            if comparison["has_regression"]:
                # Build detailed regression message
                issues = []
                if comparison["char_count_pct"] < -10:
                    issues.append(
                        f"char_count: {baseline_metrics.char_count} → "
                        f"{current_metrics.char_count} ({comparison['char_count_pct']:.1f}%)"
                    )
                if comparison["heading_count_pct"] < -10:
                    issues.append(
                        f"heading_count: {baseline_metrics.heading_count} → "
                        f"{current_metrics.heading_count} ({comparison['heading_count_pct']:.1f}%)"
                    )
                if comparison["table_row_count_pct"] < -10:
                    issues.append(
                        f"table_row_count: {baseline_metrics.table_row_count} → "
                        f"{current_metrics.table_row_count} ({comparison['table_row_count_pct']:.1f}%)"
                    )

                regressions.append(f"{slug}:\n    " + "\n    ".join(issues))

        # Report all regressions together
        if regressions:
            pytest.fail("Quality regressions detected (>10% loss):\n" + "\n  ".join(regressions))

    def test_table_heavy_papers_have_tables(self) -> None:
        """Papers marked has_tables=true must have table_row_count > 0.

        This test ensures the extraction pipeline preserves tables from papers
        that are known to contain tables. A paper with has_tables=true but
        table_row_count=0 indicates table extraction failure.
        """
        papers = load_corpus_papers()
        failures = []

        for paper in papers:
            # Skip papers without tables
            if not paper.get("has_tables", False):
                continue

            slug = paper["slug"]

            # Load current metrics
            current_metrics_path = CURRENT_DIR / slug / "metrics.json"
            if not current_metrics_path.exists():
                # Current extraction doesn't exist yet (previous test failed or didn't run)
                pytest.skip(
                    f"Current metrics not found for {slug} - "
                    "run test_all_papers_extract_successfully first"
                )

            with current_metrics_path.open() as f:
                current_data = json.load(f)
                current_metrics = ExtractionMetrics.from_dict(current_data)

            # Check table extraction
            if current_metrics.table_row_count == 0:
                failures.append(
                    f"{slug}: marked has_tables=true but table_row_count=0 "
                    "(table extraction failed)"
                )

        # Report all failures together
        if failures:
            pytest.fail("Table extraction failures:\n" + "\n  ".join(failures))

    def test_heading_structure_present(self) -> None:
        """Every paper must have heading_count >= 3.

        This test ensures the extraction pipeline preserves document structure.
        Academic papers should have at minimum: title + introduction + conclusion,
        so heading_count < 3 indicates structure extraction failure.
        """
        papers = load_corpus_papers()
        failures = []

        for paper in papers:
            slug = paper["slug"]

            # Load current metrics
            current_metrics_path = CURRENT_DIR / slug / "metrics.json"
            if not current_metrics_path.exists():
                # Current extraction doesn't exist yet (previous test failed or didn't run)
                pytest.skip(
                    f"Current metrics not found for {slug} - "
                    "run test_all_papers_extract_successfully first"
                )

            with current_metrics_path.open() as f:
                current_data = json.load(f)
                current_metrics = ExtractionMetrics.from_dict(current_data)

            # Check heading structure
            if current_metrics.heading_count < 3:
                failures.append(
                    f"{slug}: heading_count={current_metrics.heading_count} < 3 "
                    "(heading structure missing)"
                )

        # Report all failures together
        if failures:
            pytest.fail("Heading structure failures:\n" + "\n  ".join(failures))
