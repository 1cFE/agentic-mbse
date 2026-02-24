"""Tests for agentic_mbse.extraction.quality_gate and pipeline budget allocation."""

from agentic_mbse.extraction.metrics import compute_metrics
from agentic_mbse.extraction.pipeline import EnhancerBudget, allocate_budget
from agentic_mbse.extraction.quality_gate import (
    assess_heading_anomaly,
    assess_page,
    count_headings,
    prioritize_pages,
    route_page,
)
from agentic_mbse.extraction.types import DetectedTable, PageAction, PageAssessment

# ---------------------------------------------------------------------------
# Math garbling detection
# ---------------------------------------------------------------------------


class TestMathGarbling:
    def test_strikethrough_high(self):
        md = "Some ~~garbled~~ text ~~more~~ and ~~again~~ content with padding text."
        a = assess_page(md, 0)
        assert a.needs_claude
        assert a.math_garble_score >= 2.0

    def test_strikethrough_low(self):
        md = "One ~~small~~ garble in a longer page. " + "Normal filler text. " * 15
        a = assess_page(md, 0)
        assert a.math_garble_score >= 0.5
        assert a.math_garble_score < 1.0
        # Below threshold alone — should not flag needs_claude
        assert not a.needs_claude

    def test_replacement_chars(self):
        md = "Text with \ufffd and another \ufffd replacement character."
        a = assess_page(md, 0)
        assert a.needs_claude
        assert a.math_garble_score >= 2.0

    def test_bracket_operators(self):
        md = "The result is x [/] y [+] z [-] w in the formula."
        a = assess_page(md, 0)
        assert a.needs_claude
        assert a.math_garble_score >= 1.0

    def test_clean_page(self):
        md = (
            "## Introduction\n\nThis is normal text with no issues at all. " + "More content. " * 15
        )
        a = assess_page(md, 0)
        assert not a.needs_claude
        assert not a.needs_gmft
        assert a.math_garble_score == 0.0


# ---------------------------------------------------------------------------
# Table anomaly detection
# ---------------------------------------------------------------------------


class TestTableAnomaly:
    def test_br_in_tables(self):
        md = "| Header1 | Header2 |\n|---|---|\n| data<br>more | value |"
        a = assess_page(md, 0)
        assert a.needs_gmft
        assert a.table_anomaly

    def test_col_headers(self):
        md = "| Col1 | Col2 | Col3 |\n|---|---|---|\n| a | b | c |"
        a = assess_page(md, 0)
        assert a.needs_gmft
        assert a.table_anomaly


# ---------------------------------------------------------------------------
# Text density check
# ---------------------------------------------------------------------------


class TestTextDensity:
    def test_sparse_page(self):
        md = "Short."
        a = assess_page(md, 0)
        assert a.low_text_density

    def test_normal_page(self):
        md = "A" * 250
        a = assess_page(md, 0)
        assert not a.low_text_density


# ---------------------------------------------------------------------------
# Heading anomaly (document-level)
# ---------------------------------------------------------------------------


class TestHeadingAnomaly:
    def test_zero_headings_multipage(self):
        anomaly, reasons = assess_heading_anomaly(0, 10)
        assert anomaly
        assert len(reasons) > 0

    def test_high_density(self):
        anomaly, reasons = assess_heading_anomaly(40, 10)  # 4.0/page > 3.0
        assert anomaly

    def test_normal_density(self):
        anomaly, reasons = assess_heading_anomaly(10, 10)  # 1.0/page
        assert not anomaly

    def test_single_page_no_anomaly(self):
        """Single page with 0 headings is fine (e.g. title page)."""
        anomaly, reasons = assess_heading_anomaly(0, 1)
        assert not anomaly


# ---------------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------------


class TestRouting:
    def test_keep(self):
        a = PageAssessment(page_num=0)
        d = route_page(a, None, "Normal text content", within_claude_budget=True)
        assert d.action == PageAction.KEEP

    def test_claude_replace(self):
        a = PageAssessment(page_num=0, needs_claude=True, severity=2.0)
        d = route_page(a, None, "text", within_claude_budget=True)
        assert d.action == PageAction.CLAUDE_REPLACE

    def test_claude_over_budget_fallback_gmft(self):
        a = PageAssessment(page_num=0, needs_claude=True, needs_gmft=True, severity=2.0)
        tables = [DetectedTable("| a | b |", 0.99, 2, 2, 3.0)]
        d = route_page(a, tables, "text", within_claude_budget=False)
        assert d.action == PageAction.GMFT_REPLACE

    def test_gmft_replace(self):
        """needs_gmft + tables available + existing pipe tables → GMFT_REPLACE."""
        a = PageAssessment(page_num=0, needs_gmft=True, table_anomaly=True)
        tables = [DetectedTable("| x | y |", 0.99, 3, 2, 4.0)]
        page_md = "| old | table |\n|---|---|\n| a | b |"
        d = route_page(a, tables, page_md, within_claude_budget=True)
        assert d.action == PageAction.GMFT_REPLACE

    def test_gmft_append(self):
        """GMFT tables available but no existing pipe tables → GMFT_APPEND."""
        a = PageAssessment(page_num=0, needs_gmft=True, table_anomaly=True)
        tables = [DetectedTable("| x | y |", 0.99, 3, 2, 4.0)]
        page_md = "Just text, no tables here."
        d = route_page(a, tables, page_md, within_claude_budget=True)
        assert d.action == PageAction.GMFT_APPEND

    def test_strip_false(self):
        """needs_gmft + no GMFT tables + ColN headers → STRIP_FALSE."""
        a = PageAssessment(page_num=0, needs_gmft=True, table_anomaly=True)
        page_md = "| Col1 | Col2 | Col3 |\n|---|---|---|\n| a | b | c |"
        d = route_page(a, None, page_md, within_claude_budget=True)
        assert d.action == PageAction.STRIP_FALSE

    def test_strip_broken(self):
        """needs_gmft + no GMFT tables + <br> artifacts → STRIP_BROKEN."""
        a = PageAssessment(page_num=0, needs_gmft=True, table_anomaly=True)
        page_md = "| a<br>b | c |\n|---|---|\n| d | e |"
        d = route_page(a, None, page_md, within_claude_budget=True)
        assert d.action == PageAction.STRIP_BROKEN

    def test_claude_over_budget_no_gmft_keeps(self):
        """needs_claude, over budget, no table issues → KEEP (can't help)."""
        a = PageAssessment(page_num=0, needs_claude=True, severity=2.0)
        d = route_page(a, None, "text", within_claude_budget=False)
        assert d.action == PageAction.KEEP

    def test_needs_gmft_no_tables_no_specific_anomaly(self):
        """Table anomaly flagged but neither ColN nor <br> matched → KEEP."""
        a = PageAssessment(page_num=0, needs_gmft=True, table_anomaly=True)
        page_md = "Some text without specific table anomaly patterns"
        d = route_page(a, None, page_md, within_claude_budget=True)
        assert d.action == PageAction.KEEP

    def test_gmft_found_missed_tables(self):
        """GMFT found tables that pymupdf missed entirely → GMFT_APPEND."""
        a = PageAssessment(page_num=0)  # No issues flagged
        tables = [DetectedTable("| x | y |", 0.99, 3, 2, 4.0)]
        page_md = "Just text, no pipe tables at all."
        d = route_page(a, tables, page_md, within_claude_budget=True)
        assert d.action == PageAction.GMFT_APPEND


# ---------------------------------------------------------------------------
# count_headings
# ---------------------------------------------------------------------------


class TestCountHeadings:
    def test_atx_headings(self):
        md = "# H1\n## H2\n### H3"
        assert count_headings(md) == 3

    def test_not_heading_without_space(self):
        md = "##NoSpace"
        assert count_headings(md) == 0

    def test_agrees_with_compute_metrics(self):
        """count_headings() and compute_metrics().heading_count MUST agree."""
        md = "# H1\n## H2\nNot a heading\n### H3\n##NoSpace"
        assert count_headings(md) == compute_metrics(md).heading_count


# ---------------------------------------------------------------------------
# Budget allocation
# ---------------------------------------------------------------------------


class TestBudgetAllocation:
    def test_selects_highest_severity(self):
        assessments = [
            PageAssessment(page_num=0, needs_claude=True, severity=1.0),
            PageAssessment(page_num=1, needs_claude=True, severity=3.0),
            PageAssessment(page_num=2, needs_claude=True, severity=2.0),
        ]
        budget = EnhancerBudget(total_usd=0.16, cost_per_page_usd=0.078)  # budget for 2
        selected = allocate_budget(assessments, budget)
        assert selected == {1, 2}  # top 2 by severity

    def test_zero_budget(self):
        assessments = [
            PageAssessment(page_num=0, needs_claude=True, severity=2.0),
        ]
        budget = EnhancerBudget(total_usd=0.0, cost_per_page_usd=0.078)
        selected = allocate_budget(assessments, budget)
        assert selected == set()

    def test_no_eligible(self):
        assessments = [
            PageAssessment(page_num=0, needs_claude=False, severity=0.0),
            PageAssessment(page_num=1, needs_claude=False, severity=0.0),
        ]
        budget = EnhancerBudget(total_usd=1.0, cost_per_page_usd=0.078)
        selected = allocate_budget(assessments, budget)
        assert selected == set()

    def test_custom_needs_field(self):
        assessments = [
            PageAssessment(page_num=0, needs_gmft=True, severity=2.0),
            PageAssessment(page_num=1, needs_gmft=False, severity=3.0),
        ]
        budget = EnhancerBudget(total_usd=1.0, cost_per_page_usd=0.5)
        selected = allocate_budget(assessments, budget, needs_field="needs_gmft")
        assert selected == {0}


# ---------------------------------------------------------------------------
# prioritize_pages
# ---------------------------------------------------------------------------


class TestPrioritizePages:
    def test_returns_page_order(self):
        assessments = [
            PageAssessment(page_num=5, needs_claude=True, severity=1.0),
            PageAssessment(page_num=2, needs_claude=True, severity=3.0),
            PageAssessment(page_num=8, needs_claude=True, severity=2.0),
        ]
        result = prioritize_pages(assessments, budget_pages=3)
        assert result == [2, 5, 8]  # page order, not severity order

    def test_respects_budget(self):
        assessments = [
            PageAssessment(page_num=0, needs_claude=True, severity=1.0),
            PageAssessment(page_num=1, needs_claude=True, severity=3.0),
            PageAssessment(page_num=2, needs_claude=True, severity=2.0),
        ]
        result = prioritize_pages(assessments, budget_pages=2)
        assert len(result) == 2
        assert 1 in result  # highest severity
        assert 2 in result  # second highest
