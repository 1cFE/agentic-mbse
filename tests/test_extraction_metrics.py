"""Tests for agentic_mbse.extraction.metrics — extraction quality metrics."""

from pathlib import Path

import pytest

from agentic_mbse.extraction.metrics import (
    ExtractionMetrics,
    GroundTruth,
    compute_metrics,
    load_ground_truth,
    score_against_ground_truth,
)


class TestComputeMetrics:
    def test_heading_count(self):
        md = "# H1\n## H2\n### H3\nNot a heading"
        m = compute_metrics(md)
        assert m.heading_count == 3
        assert m.heading_by_level == {1: 1, 2: 1, 3: 1}

    def test_heading_by_level(self):
        md = "## A\n## B\n### C"
        m = compute_metrics(md)
        assert m.heading_by_level == {2: 2, 3: 1}

    def test_table_rows(self):
        md = "| a | b |\n|---|---|\n| 1 | 2 |"
        m = compute_metrics(md)
        assert m.table_row_count == 3

    def test_math_symbols(self):
        md = "The integral \u222b and sum \u2211 of \u03b1 + \u03b2"
        m = compute_metrics(md)
        assert m.math_symbol_count >= 4

    def test_figure_refs(self):
        md = "See Figure 1 and Fig. 2 and figure 3."
        m = compute_metrics(md)
        assert m.figure_ref_count == 3

    def test_empty_string(self):
        m = compute_metrics("")
        assert m.char_count == 0
        assert m.heading_count == 0
        assert m.table_row_count == 0
        assert m.math_symbol_count == 0
        assert m.figure_ref_count == 0

    def test_extraction_time_passthrough(self):
        m = compute_metrics("hello", elapsed=1.5)
        assert m.extraction_time_seconds == 1.5


class TestExtractionMetricsSerialization:
    def test_to_dict_roundtrip(self):
        m = ExtractionMetrics(
            char_count=100,
            heading_count=3,
            heading_by_level={1: 1, 2: 2},
            table_row_count=5,
            math_symbol_count=2,
            figure_ref_count=1,
            extraction_time_seconds=0.5,
        )
        d = m.to_dict()
        m2 = ExtractionMetrics.from_dict(d)
        assert m == m2


class TestScoreAgainstGroundTruth:
    def _make_metrics(self, headings=0, table_rows=0):
        return ExtractionMetrics(
            char_count=100,
            heading_count=headings,
            heading_by_level={1: headings} if headings else {},
            table_row_count=table_rows,
            math_symbol_count=0,
            figure_ref_count=0,
            extraction_time_seconds=0.0,
        )

    def _make_gt(self, headings=None, table_rows=None):
        return GroundTruth(
            slug="test",
            pages=1,
            headings=headings,
            heading_levels=None,
            data_tables=None,
            table_data_rows=None,
            expected_metric_table_rows=table_rows,
            display_equations=None,
            has_inline_math=None,
            notes="",
        )

    def test_exact_match(self):
        scores = score_against_ground_truth(
            self._make_metrics(headings=10), self._make_gt(headings=10)
        )
        assert scores["headings"].category == "exact"

    def test_over_detection(self):
        scores = score_against_ground_truth(
            self._make_metrics(headings=20), self._make_gt(headings=10)
        )
        assert scores["headings"].category == "over"
        assert scores["headings"].delta == 10

    def test_under_detection(self):
        scores = score_against_ground_truth(
            self._make_metrics(headings=5), self._make_gt(headings=10)
        )
        assert scores["headings"].category == "under"
        assert scores["headings"].delta == -5

    def test_miss(self):
        scores = score_against_ground_truth(
            self._make_metrics(headings=0), self._make_gt(headings=10)
        )
        assert scores["headings"].category == "miss"

    def test_close_within_10pct(self):
        scores = score_against_ground_truth(
            self._make_metrics(headings=91), self._make_gt(headings=100)
        )
        assert scores["headings"].category == "close"

    def test_none_when_gt_unavailable(self):
        scores = score_against_ground_truth(
            self._make_metrics(headings=10), self._make_gt(headings=None)
        )
        assert scores["headings"] is None


class TestLoadGroundTruth:
    def test_loads_corpus_file(self):
        """Loads from actual corpus JSONL to verify format compatibility."""
        gt_path = Path(__file__).parent / "corpus" / "ground_truth.jsonl"
        if not gt_path.exists():
            pytest.skip("ground_truth.jsonl not available")
        gt = load_ground_truth(gt_path)
        assert len(gt) > 0
        # Verify at least one known entry
        first_key = next(iter(gt))
        entry = gt[first_key]
        assert isinstance(entry, GroundTruth)
        # heading_levels keys should be int, not str
        if entry.heading_levels is not None:
            assert all(isinstance(k, int) for k in entry.heading_levels)
