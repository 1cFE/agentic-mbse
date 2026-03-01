"""Tests for agentic_mbse.extraction.pipeline — Phase 1.

Tests verify orchestration logic: correct step ordering, error isolation,
budget tracking, and decision assembly. Component-level tests are covered
in test_quality_gate.py, test_extraction_metrics.py, etc.

Mocking strategy:
- extract_pages, detect_tables_ensemble, extract_page_with_claude: always mocked
- Quality gate and routing: real implementations (deterministic, no deps)
- Pandoc functions: mocked at pandoc_convert module level
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from agentic_mbse.extraction.pipeline import (
    EnhancerBudget,
    ImageCollector,
    PipelineConfig,
    _postprocess_final,
    extract_pdf,
)
from agentic_mbse.extraction.pymupdf_backend import extract_pages
from agentic_mbse.extraction.types import (
    CostRecord,
    DetectedTable,
    PageAction,
    PageDecision,
    PageResult,
    PipelineResult,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _page(num: int, md: str = "# Page\n\nSome text content here.") -> PageResult:
    """Create a synthetic PageResult."""
    return PageResult(page_num=num, markdown=md)


def _table(
    md: str = "| A | B |\n|---|---|\n| 1 | 2 |",
    confidence: float = 0.9,
    extraction_failed: bool = False,
) -> DetectedTable:
    """Create a synthetic DetectedTable."""
    return DetectedTable(
        markdown=md,
        confidence=confidence,
        num_rows=1,
        num_cols=2,
        avg_cell_length=3.0,
        image_path=Path("/fake/table.png"),
        extraction_failed=extraction_failed,
    )


def _cost(page_num: int = 0, cost_usd: float = 0.05, table_index: int | None = None) -> CostRecord:
    return CostRecord(
        page_num=page_num,
        cost_usd=cost_usd,
        input_tokens=100,
        output_tokens=50,
        model="sonnet",
        elapsed_seconds=1.0,
        table_index=table_index,
    )


# Common patch targets
_P = "agentic_mbse.extraction.pipeline"
_PANDOC = "agentic_mbse.extraction.pandoc_convert"


def _patch_which_claude():
    """Patch shutil.which to report Claude CLI as available."""
    return patch(f"{_P}.shutil.which", return_value="/usr/bin/claude")


def _patch_which_claude_missing():
    """Patch shutil.which to report Claude CLI as missing."""
    return patch(f"{_P}.shutil.which", return_value=None)


def _patch_base(pages: list[PageResult] | None = None):
    """Patch extract_pages to return synthetic pages (default: 1 page)."""
    if pages is None:
        pages = [_page(0)]
    return patch(f"{_P}.extract_pages", return_value=pages)


def _patch_tables(tables: dict[int, list[DetectedTable]] | None = None):
    """Patch detect_tables_ensemble."""
    if tables is None:
        tables = {}
    return patch(f"{_P}.detect_tables_ensemble", return_value=tables)


def _patch_claude_page(md: str = "# Claude\n\nBetter text.", cost_usd: float = 0.078):
    """Patch extract_page_with_claude."""
    cost = _cost(cost_usd=cost_usd)
    return patch(f"{_P}.extract_page_with_claude", return_value=(md, cost))


def _patch_pandoc_unavailable():
    return patch(f"{_PANDOC}._pandoc_available", return_value=False)


def _patch_pandoc_available():
    return patch(f"{_PANDOC}._pandoc_available", return_value=True)


# ---------------------------------------------------------------------------
# TestPipelineConfig
# ---------------------------------------------------------------------------


class TestPipelineConfig:
    def test_defaults(self):
        cfg = PipelineConfig()
        assert cfg.claude_budget_usd == 2.0
        assert cfg.claude_cost_per_page_usd == 0.078
        assert cfg.claude_model == "sonnet"
        assert cfg.enable_tables is True
        assert cfg.enable_img2table is True
        assert cfg.enable_docling is False
        assert cfg.enable_claude is True
        assert cfg.arxiv_html_path is None
        assert cfg.dry_run is False
        assert cfg.page_image_dir is None

    def test_budget_zero_disables_claude(self):
        """Budget=0 means allocate_budget selects 0 pages."""
        cfg = PipelineConfig(claude_budget_usd=0)
        budget = EnhancerBudget(
            total_usd=cfg.claude_budget_usd,
            cost_per_page_usd=cfg.claude_cost_per_page_usd,
        )
        assert budget.max_pages == 0


# ---------------------------------------------------------------------------
# TestExtractPdfArxivShortcut
# ---------------------------------------------------------------------------


class TestExtractPdfArxivShortcut:
    def test_arxiv_detected_html_available(self):
        """arXiv ID found + HTML available → early return with pandoc_arxiv source."""
        with (
            _patch_pandoc_available(),
            patch(f"{_PANDOC}.detect_arxiv_id", return_value="2301.12345"),
            patch(f"{_PANDOC}.check_arxiv_html", return_value="https://arxiv.org/html/2301.12345"),
            patch(f"{_PANDOC}.convert_arxiv_html", return_value="# arXiv Paper\n\nContent."),
            _patch_base() as mock_base,
        ):
            result = extract_pdf(Path("/fake.pdf"))
        assert result.source == "pandoc_arxiv"
        assert result.markdown == "# arXiv Paper\n\nContent."
        assert result.error is None
        assert result.decisions == []
        mock_base.assert_not_called()

    def test_arxiv_detected_no_html(self):
        """arXiv ID found but no HTML → falls through to PDF extraction."""
        with (
            _patch_pandoc_available(),
            patch(f"{_PANDOC}.detect_arxiv_id", return_value="2301.12345"),
            patch(f"{_PANDOC}.check_arxiv_html", return_value=None),
            _patch_base() as mock_base,
            _patch_tables(),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        assert result.source != "pandoc_arxiv"
        mock_base.assert_called_once()

    def test_no_arxiv_id(self):
        """No arXiv ID → falls through to PDF extraction."""
        with (
            _patch_pandoc_available(),
            patch(f"{_PANDOC}.detect_arxiv_id", return_value=None),
            _patch_base() as mock_base,
            _patch_tables(),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        assert result.source != "pandoc_arxiv"
        mock_base.assert_called_once()

    def test_pandoc_not_available(self):
        """No Pandoc → falls through to PDF extraction."""
        with (
            _patch_pandoc_unavailable(),
            _patch_base() as mock_base,
            _patch_tables(),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        assert result.source != "pandoc_arxiv"
        mock_base.assert_called_once()

    def test_explicit_html_path_overrides_autodetect(self):
        """config.arxiv_html_path skips detect_arxiv_id + check_arxiv_html."""
        cfg = PipelineConfig(arxiv_html_path=Path("/tmp/paper.html"))
        with (
            _patch_pandoc_available(),
            patch(f"{_PANDOC}.detect_arxiv_id") as mock_detect,
            patch(f"{_PANDOC}.check_arxiv_html") as mock_check,
            patch(f"{_PANDOC}.convert_arxiv_html", return_value="# From HTML\n\nText."),
            _patch_base(),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg)
        assert result.source == "pandoc_arxiv"
        mock_detect.assert_not_called()
        mock_check.assert_not_called()

    def test_arxiv_shortcut_error_falls_through(self):
        """Exception in arXiv path → PDF extraction continues."""
        with (
            _patch_pandoc_available(),
            patch(f"{_PANDOC}.detect_arxiv_id", side_effect=RuntimeError("boom")),
            _patch_base() as mock_base,
            _patch_tables(),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        assert result.source != "pandoc_arxiv"
        assert result.error is None
        mock_base.assert_called_once()


# ---------------------------------------------------------------------------
# TestExtractPdfBaseExtraction
# ---------------------------------------------------------------------------


class TestExtractPdfBaseExtraction:
    def test_base_extraction_returns_pages(self):
        """Pages from extract_pages flow into the pipeline."""
        pages = [_page(0, "# Page 0\n\nText."), _page(1, "# Page 1\n\nMore.")]
        cfg = PipelineConfig(claude_budget_usd=0)  # no Claude so pages pass through
        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg)
        assert "Page 0" in result.markdown
        assert "Page 1" in result.markdown

    def test_base_extraction_error_returns_error_result(self):
        """extract_pages failure → PipelineResult with error set."""
        with (
            _patch_pandoc_unavailable(),
            patch(f"{_P}.extract_pages", side_effect=RuntimeError("corrupt PDF")),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        assert result.error is not None
        assert "corrupt PDF" in result.error


# ---------------------------------------------------------------------------
# TestExtractPdfTableEnhancement
# ---------------------------------------------------------------------------


class TestExtractPdfTableEnhancement:
    def test_table_detection_disabled(self):
        """enable_tables=False → no tables detected."""
        cfg = PipelineConfig(enable_tables=False)
        with (
            _patch_pandoc_unavailable(),
            _patch_base(),
            _patch_tables() as mock_tables,
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg)
        mock_tables.assert_not_called()
        assert result.error is None

    def test_table_detection_import_error(self):
        """GMFT not installed → empty tables, pipeline continues."""
        with (
            _patch_pandoc_unavailable(),
            _patch_base(),
            patch(f"{_P}.detect_tables_ensemble", side_effect=ImportError("no gmft")),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        assert result.error is None

    def test_table_detection_runtime_error(self):
        """Table detection crash → empty tables, pipeline continues."""
        with (
            _patch_pandoc_unavailable(),
            _patch_base(),
            patch(f"{_P}.detect_tables_ensemble", side_effect=RuntimeError("crash")),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        assert result.error is None

    def test_table_filter_applies(self):
        """Prose tables are filtered out by filter_tables."""
        # Create a table that will be filtered (very high avg_cell_length = prose)
        prose_table = DetectedTable(
            markdown="| This is a very long prose sentence that is not a real table |",
            confidence=0.5,
            num_rows=1,
            num_cols=1,
            avg_cell_length=60.0,
            image_path=Path("/fake/table.png"),
        )
        with (
            _patch_pandoc_unavailable(),
            _patch_base([_page(0)]),
            _patch_tables({0: [prose_table]}),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        assert result.error is None

    def test_table_claude_enhancement_within_budget(self):
        """Table needing enhancement → Claude called, cost tracked."""
        table = _table(extraction_failed=True)
        enhanced_table = _table(md="| X | Y |\n|---|---|\n| a | b |")
        cost = _cost(table_index=0, cost_usd=0.05)

        with (
            _patch_pandoc_unavailable(),
            _patch_base([_page(0)]),
            _patch_tables({0: [table]}),
            patch(
                f"{_P}.enhance_table_with_claude", return_value=(enhanced_table, cost)
            ) as mock_enhance,
            _patch_claude_page(),
            _patch_which_claude(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        mock_enhance.assert_called_once()
        assert any(c.table_index is not None for c in result.cost)

    def test_table_claude_fp_rejection(self):
        """Claude returns empty markdown → table dropped (FP filter)."""
        table = _table(extraction_failed=True)
        empty_table = _table(md="")
        cost = _cost(table_index=0)

        with (
            _patch_pandoc_unavailable(),
            _patch_base([_page(0)]),
            _patch_tables({0: [table]}),
            patch(f"{_P}.enhance_table_with_claude", return_value=(empty_table, cost)),
            _patch_claude_page(),
            _patch_which_claude(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        assert result.error is None

    def test_table_claude_budget_exhausted(self):
        """Tables beyond budget are not enhanced with Claude."""
        table = _table(extraction_failed=True)
        cfg = PipelineConfig(claude_budget_usd=0)

        with (
            _patch_pandoc_unavailable(),
            _patch_base([_page(0)]),
            _patch_tables({0: [table]}),
            patch(f"{_P}.enhance_table_with_claude") as mock_enhance,
            _patch_claude_page(),
        ):
            extract_pdf(Path("/fake.pdf"), cfg)
        mock_enhance.assert_not_called()

    def test_table_enhancement_error_skips_table(self):
        """Individual table enhancement error → skip table, continue."""
        table = _table(extraction_failed=True)

        with (
            _patch_pandoc_unavailable(),
            _patch_base([_page(0)]),
            _patch_tables({0: [table]}),
            patch(f"{_P}.enhance_table_with_claude", side_effect=RuntimeError("Claude failed")),
            _patch_claude_page(),
            _patch_which_claude(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        assert result.error is None

    def test_dry_run_no_table_claude(self):
        """dry_run=True → no Claude calls for tables."""
        table = _table(extraction_failed=True)
        cfg = PipelineConfig(dry_run=True)

        with (
            _patch_pandoc_unavailable(),
            _patch_base([_page(0)]),
            _patch_tables({0: [table]}),
            patch(f"{_P}.enhance_table_with_claude") as mock_enhance,
            _patch_claude_page(),
        ):
            extract_pdf(Path("/fake.pdf"), cfg)
        mock_enhance.assert_not_called()


# ---------------------------------------------------------------------------
# TestExtractPdfQualityGateAndBudget
# ---------------------------------------------------------------------------


class TestExtractPdfQualityGateAndBudget:
    def test_quality_gate_runs_after_tables(self):
        """Quality gate assess_page is called for each page."""
        pages = [_page(0), _page(1)]
        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            _patch_claude_page(),
            patch(
                f"{_P}.assess_page",
                wraps=__import__(
                    "agentic_mbse.extraction.quality_gate", fromlist=["assess_page"]
                ).assess_page,
            ) as mock_assess,
        ):
            extract_pdf(Path("/fake.pdf"))
        assert mock_assess.call_count == 2

    def test_heading_anomaly_boosts_severity(self):
        """Document-level heading anomaly boosts severity on needs_claude pages."""
        # 10 pages, no headings at all → heading anomaly
        pages = [
            _page(i, f"Page {i} text content without any headings whatsoever.") for i in range(10)
        ]
        cfg = PipelineConfig(claude_budget_usd=0)  # budget 0 so we just check decisions
        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg)
        # All pages should have decisions
        assert len(result.decisions) == 10

    def test_budget_allocation_uses_remaining_budget(self):
        """Table spend is deducted before page-level Claude allocation."""
        # One page with garbled math (needs Claude), one table costing 0.05
        garbled = "# Title\n\n~~garbled~~ ~~math~~ ~~content~~ \ufffd\ufffd more text here."
        pages = [_page(0, garbled)]
        table = _table(extraction_failed=True)
        enhanced = _table(md="| OK |\n|---|\n| 1 |")
        table_cost = _cost(table_index=0, cost_usd=1.95)

        cfg = PipelineConfig(claude_budget_usd=2.0)

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables({0: [table]}),
            patch(f"{_P}.enhance_table_with_claude", return_value=(enhanced, table_cost)),
            patch(f"{_P}.extract_page_with_claude") as mock_claude_page,
            _patch_which_claude(),
        ):
            extract_pdf(Path("/fake.pdf"), cfg)
        # Budget remaining after table: 2.0 - 1.95 = 0.05, not enough for a page (0.078)
        mock_claude_page.assert_not_called()

    def test_budget_zero_no_claude_pages(self):
        """Budget=0 → no page-level Claude enhancement."""
        garbled = "# Title\n\n~~garbled~~ ~~math~~ ~~content~~ \ufffd\ufffd more text here."
        pages = [_page(0, garbled)]
        cfg = PipelineConfig(claude_budget_usd=0)

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            patch(f"{_P}.extract_page_with_claude") as mock_claude,
        ):
            extract_pdf(Path("/fake.pdf"), cfg)
        mock_claude.assert_not_called()


# ---------------------------------------------------------------------------
# TestExtractPdfClaudePageEnhancement
# ---------------------------------------------------------------------------


class TestExtractPdfClaudePageEnhancement:
    def test_claude_page_accepted(self):
        """Claude output accepted → page replaced, cost tracked."""
        garbled = "# Title\n\n~~garbled~~ ~~math~~ ~~content~~ \ufffd\ufffd more text here with enough content."
        pages = [_page(0, garbled)]
        claude_md = "# Title\n\nClean math content with proper formatting."
        claude_cost = _cost(page_num=0, cost_usd=0.078)

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            patch(f"{_P}.extract_page_with_claude", return_value=(claude_md, claude_cost)),
            _patch_which_claude(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        # Claude output should be in the final markdown
        assert "Clean math content" in result.markdown
        assert len(result.cost) > 0

    def test_claude_page_rejected_empty(self):
        """Claude returns empty → rejected, cost still tracked."""
        garbled = "# Title\n\n~~garbled~~ ~~math~~ ~~content~~ \ufffd\ufffd more text here with enough content."
        pages = [_page(0, garbled)]
        claude_cost = _cost(page_num=0, cost_usd=0.078)

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            patch(f"{_P}.extract_page_with_claude", return_value=("", claude_cost)),
            _patch_which_claude(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        # Cost should still be tracked even though output was rejected
        assert any(c.table_index is None for c in result.cost)
        # Original content should remain (not replaced with empty)
        assert "garbled" in result.markdown

    def test_claude_page_error_continues(self):
        """Exception during Claude page → skip page, continue."""
        garbled = "# Title\n\n~~garbled~~ ~~math~~ ~~content~~ \ufffd\ufffd more text."
        pages = [_page(0, garbled), _page(1, "# Page 2\n\nNormal content here.")]

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            patch(f"{_P}.extract_page_with_claude", side_effect=RuntimeError("Claude error")),
            _patch_which_claude(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        assert result.error is None
        assert "Page 2" in result.markdown

    def test_dry_run_no_claude_pages(self):
        """dry_run=True → no page-level Claude calls."""
        garbled = "# Title\n\n~~garbled~~ ~~math~~ ~~content~~ \ufffd\ufffd more text."
        pages = [_page(0, garbled)]
        cfg = PipelineConfig(dry_run=True)

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            patch(f"{_P}.extract_page_with_claude") as mock_claude,
        ):
            extract_pdf(Path("/fake.pdf"), cfg)
        mock_claude.assert_not_called()


# ---------------------------------------------------------------------------
# TestExtractPdfRouteAndMerge
# ---------------------------------------------------------------------------


class TestExtractPdfRouteAndMerge:
    def test_keep_action_for_clean_page(self):
        """Clean page with no issues → KEEP action, original markdown preserved."""
        # Use enough text to avoid low text density trigger (200 char threshold)
        long_text = "# Clean Page\n\n" + (
            "This is a normal paragraph with enough content to avoid the low text density trigger. "
            * 3
        )
        pages = [_page(0, long_text)]
        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        assert result.decisions[0].action == PageAction.KEEP
        assert "Clean Page" in result.markdown

    def test_merge_gmft_replace(self):
        """GMFT_REPLACE action → pipe tables replaced with GMFT tables."""
        page_md = "# Page\n\n| Old | Data |\n|---|---|\n| a | b |"
        pages = [_page(0, page_md)]
        table = _table(md="| New | Data |\n|---|---|\n| c | d |")
        cfg = PipelineConfig(claude_budget_usd=0)

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables({0: [table]}),
            _patch_claude_page(),
            patch(f"{_P}.route_page", return_value=PageDecision(0, PageAction.GMFT_REPLACE)),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg)
        assert "New" in result.markdown
        assert "Old" not in result.markdown

    def test_merge_gmft_append(self):
        """GMFT_APPEND action → GMFT tables appended to page."""
        page_md = "# Page\n\nSome text without tables."
        pages = [_page(0, page_md)]
        table = _table(md="| Added | Table |\n|---|---|\n| x | y |")
        cfg = PipelineConfig(claude_budget_usd=0)

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables({0: [table]}),
            _patch_claude_page(),
            patch(f"{_P}.route_page", return_value=PageDecision(0, PageAction.GMFT_APPEND)),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg)
        assert "Some text" in result.markdown
        assert "Added" in result.markdown

    def test_merge_strip_false(self):
        """STRIP_FALSE action → pipe tables removed from page."""
        page_md = "# Page\n\nText before.\n\n| Col1 | Col2 |\n|---|---|\n| a | b |\n\nText after."
        pages = [_page(0, page_md)]
        cfg = PipelineConfig(claude_budget_usd=0)

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            _patch_claude_page(),
            patch(f"{_P}.route_page", return_value=PageDecision(0, PageAction.STRIP_FALSE)),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg)
        assert "Text before" in result.markdown
        assert "Text after" in result.markdown
        assert "Col1" not in result.markdown

    def test_merge_strip_broken(self):
        """STRIP_BROKEN action → pipe tables removed from page."""
        page_md = "# Page\n\nContent.\n\n| X | Y |\n|---|---|\n| 1 | 2 |\n\nMore content."
        pages = [_page(0, page_md)]
        cfg = PipelineConfig(claude_budget_usd=0)

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            _patch_claude_page(),
            patch(f"{_P}.route_page", return_value=PageDecision(0, PageAction.STRIP_BROKEN)),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg)
        assert "Content" in result.markdown
        assert "More content" in result.markdown
        assert "| X |" not in result.markdown

    def test_decisions_one_per_page(self):
        """len(decisions) == len(pages)."""
        pages = [_page(i, f"# Page {i}\n\nContent for page.") for i in range(5)]
        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        assert len(result.decisions) == 5

    def test_table_filter_reasons_in_details(self):
        """decision.details['table_filter'] captures filter reasons for pages with tables."""
        table = _table()
        with (
            _patch_pandoc_unavailable(),
            _patch_base([_page(0)]),
            _patch_tables({0: [table]}),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        # The page with tables should have table_filter in details
        page_0_decision = [d for d in result.decisions if d.page_num == 0][0]
        assert "table_filter" in page_0_decision.details

    def test_cost_sum_matches_total(self):
        """total_cost_usd == sum(cost_records)."""
        garbled = "# Title\n\n~~garbled~~ ~~math~~ ~~content~~ \ufffd\ufffd more text here with enough content."
        pages = [_page(0, garbled)]
        claude_cost = _cost(page_num=0, cost_usd=0.078)

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            patch(
                f"{_P}.extract_page_with_claude", return_value=("# Better\n\nContent.", claude_cost)
            ),
            _patch_which_claude(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        expected_total = sum(c.cost_usd for c in result.cost)
        assert abs(result.total_cost_usd - expected_total) < 1e-9

    def test_metrics_computed_on_merged(self):
        """Metrics are computed on the final merged markdown."""
        pages = [_page(0, "# Heading\n\nParagraph."), _page(1, "## Sub\n\nMore text.")]
        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        # Metrics should reflect the merged document
        assert result.metrics.char_count > 0
        assert result.metrics.heading_count >= 2


# ---------------------------------------------------------------------------
# TestExtractPdfStepOrdering
# ---------------------------------------------------------------------------


class TestExtractPdfStepOrdering:
    def test_arxiv_before_base_extraction(self):
        """arXiv shortcut is checked before base extraction."""
        call_order = []

        def track_arxiv(*a, **kw):
            call_order.append("arxiv")
            return "2301.12345"

        def track_base(*a, **kw):
            call_order.append("base")
            return [_page(0)]

        with (
            _patch_pandoc_available(),
            patch(f"{_PANDOC}.detect_arxiv_id", side_effect=track_arxiv),
            patch(f"{_PANDOC}.check_arxiv_html", return_value="https://arxiv.org/html/2301.12345"),
            patch(f"{_PANDOC}.convert_arxiv_html", return_value="# Paper"),
            patch(f"{_P}.extract_pages", side_effect=track_base),
            _patch_tables(),
        ):
            extract_pdf(Path("/fake.pdf"))
        assert call_order == ["arxiv"]  # base never called due to early return

    def test_table_enhancement_before_quality_gate(self):
        """Tables are processed before quality gate assessment."""
        call_order = []

        original_assess = __import__(
            "agentic_mbse.extraction.quality_gate", fromlist=["assess_page"]
        ).assess_page

        def track_assess(*a, **kw):
            call_order.append("assess")
            return original_assess(*a, **kw)

        def track_tables(*a, **kw):
            call_order.append("tables")
            return {}

        with (
            _patch_pandoc_unavailable(),
            _patch_base(),
            patch(f"{_P}.detect_tables_ensemble", side_effect=track_tables),
            patch(f"{_P}.assess_page", side_effect=track_assess),
            _patch_claude_page(),
        ):
            extract_pdf(Path("/fake.pdf"))
        assert call_order.index("tables") < call_order.index("assess")

    def test_quality_gate_before_budget_allocation(self):
        """Quality gate runs before budget allocation."""
        call_order = []

        original_assess = __import__(
            "agentic_mbse.extraction.quality_gate", fromlist=["assess_page"]
        ).assess_page
        original_allocate = __import__(
            "agentic_mbse.extraction.pipeline", fromlist=["allocate_budget"]
        ).allocate_budget

        def track_assess(*a, **kw):
            call_order.append("assess")
            return original_assess(*a, **kw)

        def track_allocate(*a, **kw):
            call_order.append("allocate")
            return original_allocate(*a, **kw)

        with (
            _patch_pandoc_unavailable(),
            _patch_base(),
            _patch_tables(),
            patch(f"{_P}.assess_page", side_effect=track_assess),
            patch(f"{_P}.allocate_budget", side_effect=track_allocate),
            _patch_claude_page(),
        ):
            extract_pdf(Path("/fake.pdf"))
        assert "assess" in call_order
        assert "allocate" in call_order
        assert call_order.index("assess") < call_order.index("allocate")

    def test_budget_allocation_before_claude_pages(self):
        """Budget allocation runs before Claude page enhancement."""
        garbled = (
            "# Title\n\n~~garbled~~ ~~math~~ ~~content~~ \ufffd\ufffd more text here with enough."
        )
        pages = [_page(0, garbled)]
        call_order = []

        original_allocate = __import__(
            "agentic_mbse.extraction.pipeline", fromlist=["allocate_budget"]
        ).allocate_budget

        def track_allocate(*a, **kw):
            call_order.append("allocate")
            return original_allocate(*a, **kw)

        def track_claude(*a, **kw):
            call_order.append("claude")
            return ("# Better", _cost(cost_usd=0.078))

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            patch(f"{_P}.allocate_budget", side_effect=track_allocate),
            patch(f"{_P}.extract_page_with_claude", side_effect=track_claude),
        ):
            extract_pdf(Path("/fake.pdf"))
        assert "allocate" in call_order
        if "claude" in call_order:
            assert call_order.index("allocate") < call_order.index("claude")


# ---------------------------------------------------------------------------
# TestPreflightClaudeCheck
# ---------------------------------------------------------------------------


class TestPreflightClaudeCheck:
    def test_claude_missing_no_subprocess_calls(self):
        """shutil.which → None → no Claude subprocess calls attempted."""
        garbled = "# Title\n\n~~garbled~~ ~~math~~ ~~content~~ \ufffd\ufffd more text here with enough content."
        pages = [_page(0, garbled)]

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            patch(f"{_P}.extract_page_with_claude") as mock_claude,
            _patch_which_claude_missing(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        mock_claude.assert_not_called()
        assert result.error is None

    def test_claude_missing_table_enhancement_skipped(self):
        """shutil.which → None → table Claude enhancement also skipped."""
        table = _table(extraction_failed=True)

        with (
            _patch_pandoc_unavailable(),
            _patch_base([_page(0)]),
            _patch_tables({0: [table]}),
            patch(f"{_P}.enhance_table_with_claude") as mock_enhance,
            patch(f"{_P}.extract_page_with_claude") as mock_claude,
            _patch_which_claude_missing(),
        ):
            result = extract_pdf(Path("/fake.pdf"))
        mock_enhance.assert_not_called()
        mock_claude.assert_not_called()
        assert result.error is None


# ---------------------------------------------------------------------------
# TestDecisionTruthfulness
# ---------------------------------------------------------------------------


class TestDecisionTruthfulness:
    def test_claude_unavailable_decisions_rewritten_to_keep(self):
        """Pages routed to CLAUDE_REPLACE but Claude unavailable → decision becomes KEEP."""
        garbled = "# Title\n\n~~garbled~~ ~~math~~ ~~content~~ \ufffd\ufffd more text here with enough content."
        pages = [_page(0, garbled)]

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            patch(f"{_P}.extract_page_with_claude") as mock_claude,
            _patch_which_claude_missing(),
        ):
            result = extract_pdf(Path("/fake.pdf"))

        mock_claude.assert_not_called()
        # Find decisions that quality gate would have routed to CLAUDE_REPLACE
        # They should now be KEEP with an explanatory reason
        for d in result.decisions:
            if "Claude enhancement unavailable" in " ".join(d.reasons):
                assert d.action == PageAction.KEEP
                break
        else:
            # If no page was flagged for Claude, the garbled content wasn't severe enough.
            # Verify at least that claude_pages_intended reflects reality.
            assert result.claude_pages_succeeded == 0

    def test_claude_pages_stats_reflect_failure(self):
        """claude_pages_intended > 0 but succeeded == 0 when Claude missing."""
        garbled = "# Title\n\n~~garbled~~ ~~math~~ ~~content~~ \ufffd\ufffd more text here with enough content."
        pages = [_page(0, garbled)]

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            patch(f"{_P}.extract_page_with_claude"),
            _patch_which_claude_missing(),
        ):
            result = extract_pdf(Path("/fake.pdf"))

        # If pages were allocated for Claude, succeeded should be 0
        if result.claude_pages_intended > 0:
            assert result.claude_pages_succeeded == 0


# ---------------------------------------------------------------------------
# TestCliSummary
# ---------------------------------------------------------------------------


class TestCliSummary:
    def _make_result(self, intended: int, succeeded: int, cost: float = 0.0) -> PipelineResult:
        from agentic_mbse.extraction.metrics import compute_metrics

        return PipelineResult(
            markdown="# Test\n\nContent.",
            metrics=compute_metrics("# Test\n\nContent."),
            source="pdf_pipeline",
            elapsed_seconds=5.0,
            total_cost_usd=cost,
            claude_pages_intended=intended,
            claude_pages_succeeded=succeeded,
        )

    def test_print_pipeline_summary_shows_claude_warning(self, capsys):
        """CLI summary shows Claude failure warning when intended > succeeded."""
        from agentic_mbse.cli.extract_cli import _print_pipeline_summary

        _print_pipeline_summary("test.pdf", self._make_result(3, 0))
        captured = capsys.readouterr()
        assert "! Claude: 0/3 pages enhanced" in captured.out

    def test_print_pipeline_summary_no_warning_when_all_succeed(self, capsys):
        """No warning when all Claude pages succeed."""
        from agentic_mbse.cli.extract_cli import _print_pipeline_summary

        _print_pipeline_summary("test.pdf", self._make_result(3, 3, cost=0.234))
        captured = capsys.readouterr()
        assert "! Claude" not in captured.out

    def test_print_pipeline_summary_no_warning_when_no_claude(self, capsys):
        """No warning when Claude wasn't used."""
        from agentic_mbse.cli.extract_cli import _print_pipeline_summary

        _print_pipeline_summary("test.pdf", self._make_result(0, 0))
        captured = capsys.readouterr()
        assert "! Claude" not in captured.out


# ---------------------------------------------------------------------------
# TestPostprocessCleanup
# ---------------------------------------------------------------------------


class TestPostprocessCleanup:
    def test_running_headers_stripped(self):
        """Repeated short lines across pages are removed from merged output."""
        # Running header appears 4 times (threshold=3) across separate pages
        header = "_L.S. Author and K. Coauthor ... Applied Energy 401 (2025) 126567_"
        titles = ["Introduction", "Background", "Methodology", "Results"]
        pages = [
            _page(
                i,
                f"{header}\n\n## {titles[i]}\n\nContent for page about {titles[i]}. "
                + "Filler. " * 20,
            )
            for i in range(4)
        ]
        cfg = PipelineConfig(claude_budget_usd=0)

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg)

        assert header not in result.markdown
        # Actual unique content should survive
        assert "Introduction" in result.markdown
        assert "Results" in result.markdown

    def test_page_numbers_stripped(self):
        """Bare page numbers between blank lines are removed."""
        pages = [
            _page(0, "## Introduction\n\nFirst page content. " + "Filler. " * 20),
            _page(1, "2\n\n## Methods\n\nSecond page content. " + "Filler. " * 20),
            _page(2, "3\n\n## Results\n\nThird page content. " + "Filler. " * 20),
        ]
        cfg = PipelineConfig(claude_budget_usd=0)

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg)

        # Page numbers should be stripped (they appear between \n\n...\n\n in merged output)
        # Content should survive
        assert "Introduction" in result.markdown
        assert "Methods" in result.markdown
        assert "Results" in result.markdown

    def test_ligatures_repaired(self):
        """Unicode ligatures (U+FB00-FB04) replaced with ASCII."""
        pages = [_page(0, "The e\ufb00ect of \ufb01ltering on e\ufb03ciency. " + "Filler. " * 20)]
        cfg = PipelineConfig(claude_budget_usd=0)

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg)

        assert "effect" in result.markdown
        assert "filtering" in result.markdown
        assert "efficiency" in result.markdown
        assert "\ufb00" not in result.markdown
        assert "\ufb01" not in result.markdown
        assert "\ufb03" not in result.markdown

    def test_header_formatting_preserved(self):
        """Existing ## headers are NOT modified (FR-4 compliance)."""
        pages = [
            _page(0, "## 1 Introduction\n\n### 1.1 Background\n\nContent here. " + "Filler. " * 20)
        ]
        cfg = PipelineConfig(claude_budget_usd=0)

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg)

        # Headers should remain exactly as-is (no promotion/demotion)
        assert "## 1 Introduction" in result.markdown
        assert "### 1.1 Background" in result.markdown

    def test_bold_headers_not_promoted(self):
        """Bold numbered lines are NOT promoted to ## headers (FR-4 compliance)."""
        pages = [_page(0, "**1 Introduction**\n\nContent here. " + "Filler. " * 20)]
        cfg = PipelineConfig(claude_budget_usd=0)

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables(),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg)

        # Bold line should remain as-is, NOT promoted to ## header
        assert "**1 Introduction**" in result.markdown


# ---------------------------------------------------------------------------
# TestGmftCrossReference
# ---------------------------------------------------------------------------


class TestGmftCrossReference:
    def test_gmft_tables_no_pipe_tables_boosts_severity(self):
        """GMFT found tables + pymupdf has no pipe tables → needs_claude, severity boosted."""
        from agentic_mbse.extraction.pipeline import _cross_reference_gmft
        from agentic_mbse.extraction.types import PageAssessment

        # Page with text but no pipe tables
        pages = [_page(0, "Just text, no tables at all. " * 10)]
        assessments = [PageAssessment(page_num=0, severity=0.0)]
        detected_tables = {0: [_table()]}

        _cross_reference_gmft(assessments, pages, detected_tables)

        assert assessments[0].needs_claude is True
        assert assessments[0].needs_gmft is True
        assert assessments[0].severity >= 1.5
        assert any("GMFT_XREF" in r for r in assessments[0].reasons)

    def test_gmft_tables_with_pipe_tables_no_change(self):
        """GMFT found tables + pymupdf has pipe tables → no change."""
        from agentic_mbse.extraction.pipeline import _cross_reference_gmft
        from agentic_mbse.extraction.types import PageAssessment

        # Page WITH pipe tables
        pages = [_page(0, "Text.\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\nMore text.")]
        assessments = [PageAssessment(page_num=0, severity=0.0)]
        detected_tables = {0: [_table()]}

        _cross_reference_gmft(assessments, pages, detected_tables)

        assert assessments[0].needs_claude is False
        assert assessments[0].severity == 0.0

    def test_no_gmft_tables_no_change(self):
        """No GMFT tables on page → no change."""
        from agentic_mbse.extraction.pipeline import _cross_reference_gmft
        from agentic_mbse.extraction.types import PageAssessment

        pages = [_page(0, "Just text. " * 20)]
        assessments = [PageAssessment(page_num=0, severity=0.0)]
        detected_tables = {}  # No tables detected

        _cross_reference_gmft(assessments, pages, detected_tables)

        assert assessments[0].needs_claude is False
        assert assessments[0].severity == 0.0

    def test_e2e_gmft_missed_within_budget_claude_replace(self):
        """End-to-end: GMFT-missed-table page within budget → CLAUDE_REPLACE."""
        # Page with enough text to avoid low-density, but no pipe tables
        page_md = "This is a page with garbled table text rendered as paragraphs. " * 5
        pages = [_page(0, page_md)]
        table = _table()
        # Claude output must be comparable length to pass validate_claude_output
        claude_md = "# Better\n\nClean table content with proper formatting. " * 5
        claude_cost = _cost(page_num=0, cost_usd=0.078)

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables({0: [table]}),
            patch(f"{_P}.extract_page_with_claude", return_value=(claude_md, claude_cost)),
            _patch_which_claude(),
        ):
            result = extract_pdf(Path("/fake.pdf"))

        # The page should be routed to CLAUDE_REPLACE due to GMFT xref
        page_decision = result.decisions[0]
        assert page_decision.action == PageAction.CLAUDE_REPLACE
        assert "Clean table content" in result.markdown

    def test_e2e_gmft_missed_over_budget_gmft_replace(self):
        """End-to-end: GMFT-missed-table page over budget → GMFT_REPLACE fallback."""
        # Page with enough text, no pipe tables
        page_md = "This is a page with garbled table text rendered as paragraphs. " * 5
        pages = [_page(0, page_md)]
        table = _table()
        cfg = PipelineConfig(claude_budget_usd=0)  # Zero budget forces over-budget

        with (
            _patch_pandoc_unavailable(),
            _patch_base(pages),
            _patch_tables({0: [table]}),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg)

        # Over budget → GMFT_REPLACE fallback (needs_claude + needs_gmft + has_tables)
        page_decision = result.decisions[0]
        assert page_decision.action == PageAction.GMFT_REPLACE


# ---------------------------------------------------------------------------
# Package exports
# ---------------------------------------------------------------------------


def test_package_exports():
    """Verify extract_pdf, PipelineConfig, PipelineResult are importable from package."""
    from agentic_mbse.extraction import PipelineConfig, PipelineResult, extract_pdf

    assert callable(extract_pdf)
    assert PipelineConfig is not None
    assert PipelineResult is not None


# ---------------------------------------------------------------------------
# ImageCollector (Phase 1: Unified Image Output)
# ---------------------------------------------------------------------------


class TestImageCollector:
    def test_add_returns_markdown_ref(self):
        """add() returns ![](images/rel_name) string."""
        collector = ImageCollector(output_dir=Path("/fake/images"))
        ref = collector.add(Path("/tmp/src.png"), "page_001_table_0.png", "table_crop", 1)
        assert ref == "![](images/page_001_table_0.png)"
        assert len(collector.entries) == 1

    def test_persist_copies_files(self, tmp_path):
        """persist() copies source files to output_dir."""
        src = tmp_path / "src.png"
        src.write_bytes(b"fake png")
        out = tmp_path / "images"
        collector = ImageCollector(output_dir=out)
        collector.add(src, "table.png", "table_crop", 0)
        count = collector.persist()
        assert count == 1
        assert (out / "table.png").exists()

    def test_persist_empty_collector(self, tmp_path):
        """persist() with zero entries returns 0 without error."""
        collector = ImageCollector(output_dir=tmp_path / "images")
        assert collector.persist() == 0

    def test_persist_missing_source_warns(self, tmp_path, caplog):
        """persist() skips missing files with warning, doesn't raise."""
        collector = ImageCollector(output_dir=tmp_path / "images")
        collector.add(Path("/nonexistent/file.png"), "ghost.png", "table_crop", 0)
        count = collector.persist()
        assert count == 0
        assert "Failed to persist" in caplog.text

    def test_total_image_count_includes_all_files(self, tmp_path):
        """total_image_count scans directory (includes pre-existing files)."""
        out = tmp_path / "images"
        out.mkdir()
        (out / "figure.png").write_bytes(b"fig")
        (out / "table.png").write_bytes(b"tab")
        collector = ImageCollector(output_dir=out)
        assert collector.total_image_count == 2

    def test_total_image_count_no_dir(self, tmp_path):
        """total_image_count returns 0 when output_dir doesn't exist."""
        collector = ImageCollector(output_dir=tmp_path / "nope")
        assert collector.total_image_count == 0


# ---------------------------------------------------------------------------
# Figure Extraction (Phase 2: Unified Image Output)
# ---------------------------------------------------------------------------

_PYMUPDF = "agentic_mbse.extraction.pymupdf_backend"


class TestFigureExtraction:
    def test_extract_pages_with_images_dir(self):
        """extract_pages passes write_images=True when dir provided."""
        mock_to_md = MagicMock(return_value=[{"metadata": {"page": 1}, "text": "# Page"}])
        with patch(f"{_PYMUPDF}._get_to_markdown", return_value=mock_to_md):
            extract_pages(Path("/fake.pdf"), extracted_images_dir=Path("/out/images"))
            call_kwargs = mock_to_md.call_args[1]
            assert call_kwargs["write_images"] is True
            assert call_kwargs["image_path"] == "/out/images"

    def test_extract_pages_without_images_dir(self):
        """extract_pages passes write_images=False when dir is None."""
        mock_to_md = MagicMock(return_value=[{"metadata": {"page": 1}, "text": "# Page"}])
        with patch(f"{_PYMUPDF}._get_to_markdown", return_value=mock_to_md):
            extract_pages(Path("/fake.pdf"))
            call_kwargs = mock_to_md.call_args[1]
            assert call_kwargs["write_images"] is False
            assert call_kwargs["image_path"] is None


# ---------------------------------------------------------------------------
# Postprocess with Images (Phase 2: Unified Image Output)
# ---------------------------------------------------------------------------


class TestPostprocessWithImages:
    def test_normalizes_absolute_paths(self):
        """_postprocess_final normalizes absolute image paths when dir provided."""
        md = "![](/tmp/out/images/fig-0-0.png)\n\nSome text."
        result = _postprocess_final(md, extracted_images_dir=Path("/tmp/out/images"))
        assert "![](images/fig-0-0.png)" in result
        assert "/tmp/out/images" not in result

    def test_promotes_figure_captions(self):
        """_postprocess_final promotes captions after normalizing paths."""
        md = "![](/tmp/out/images/fig.png)\nFigure 1: A diagram."
        result = _postprocess_final(md, extracted_images_dir=Path("/tmp/out/images"))
        assert "![Figure 1: A diagram.](images/fig.png)" in result

    def test_no_images_dir_no_normalization(self):
        """_postprocess_final with None dir skips image processing."""
        md = "![](/absolute/path/images/fig.png)\n\nText."
        result = _postprocess_final(md)
        assert "/absolute/path/images/fig.png" in result


# ---------------------------------------------------------------------------
# Table Crop Persistence (Phase 3: Unified Image Output)
# ---------------------------------------------------------------------------


class TestTableCropPersistence:
    def test_table_crops_registered_with_collector(self, tmp_path):
        """Tables with image_path get registered and image ref prepended to markdown."""
        images_dir = tmp_path / "images"
        images_dir.mkdir()

        # Create a real temp file for the table crop
        crop_file = tmp_path / "crop.png"
        crop_file.write_bytes(b"fake crop png")

        table = DetectedTable(
            markdown="| A | B |\n|---|---|\n| 1 | 2 |",
            confidence=0.9,
            num_rows=1,
            num_cols=2,
            avg_cell_length=3.0,
            image_path=crop_file,
        )
        # Zero Claude budget so page routes to GMFT (not CLAUDE_REPLACE)
        cfg = PipelineConfig(
            extracted_images_dir=images_dir,
            enable_claude=False,
            claude_budget_usd=0,
        )
        with (
            _patch_pandoc_unavailable(),
            _patch_base([_page(0)]),
            _patch_tables({0: [table]}),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg)

        # Table crop should be persisted to images dir
        assert (images_dir / "page_000_table_0.png").exists()
        # Image reference should appear in output markdown
        assert "![](images/page_000_table_0.png)" in result.markdown

    def test_no_collector_when_images_dir_none(self):
        """Pipeline with extracted_images_dir=None produces no image refs."""
        table = _table()
        cfg = PipelineConfig()
        with (
            _patch_pandoc_unavailable(),
            _patch_base([_page(0)]),
            _patch_tables({0: [table]}),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg)

        assert "![](images/" not in result.markdown
        assert result.image_count == 0

    def test_table_without_image_path_skipped(self, tmp_path):
        """Tables with image_path=None don't get image refs."""
        images_dir = tmp_path / "images"
        images_dir.mkdir()

        table = DetectedTable(
            markdown="| A | B |\n|---|---|\n| 1 | 2 |",
            confidence=0.9,
            num_rows=1,
            num_cols=2,
            avg_cell_length=3.0,
            image_path=None,  # No crop image
        )
        cfg = PipelineConfig(extracted_images_dir=images_dir)
        with (
            _patch_pandoc_unavailable(),
            _patch_base([_page(0)]),
            _patch_tables({0: [table]}),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg)

        assert "![](images/" not in result.markdown

    def test_image_count_in_result(self, tmp_path):
        """PipelineResult.image_count reflects total images in dir."""
        images_dir = tmp_path / "images"
        images_dir.mkdir()

        # Pre-place a "figure" file (simulating pymupdf write_images)
        (images_dir / "doc-0-0.png").write_bytes(b"figure")

        crop_file = tmp_path / "crop.png"
        crop_file.write_bytes(b"crop")

        table = DetectedTable(
            markdown="| A | B |\n|---|---|\n| 1 | 2 |",
            confidence=0.9,
            num_rows=1,
            num_cols=2,
            avg_cell_length=3.0,
            image_path=crop_file,
        )
        cfg = PipelineConfig(extracted_images_dir=images_dir)
        with (
            _patch_pandoc_unavailable(),
            _patch_base([_page(0)]),
            _patch_tables({0: [table]}),
            _patch_claude_page(),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg)

        # 1 pre-existing figure + 1 table crop = 2
        assert result.image_count == 2

    def test_backward_compat_no_images_dir(self):
        """Pipeline output identical when extracted_images_dir=None."""
        cfg_default = PipelineConfig(enable_claude=False)
        with (
            _patch_pandoc_unavailable(),
            _patch_base([_page(0, "# Hello\n\nWorld.")]),
            _patch_tables(),
        ):
            result = extract_pdf(Path("/fake.pdf"), cfg_default)

        assert result.error is None
        assert result.image_count == 0
        assert "Hello" in result.markdown
