"""Tests for agentic_mbse.extraction.profile — Phase 2.

Tests cover route distribution, profile serialization, summary table
formatting, and corpus discovery. All use synthetic data — no pipeline
execution required.
"""

from __future__ import annotations

import json
from unittest.mock import patch

from agentic_mbse.cli.extract_cli import cmd_extract
from agentic_mbse.extraction.metrics import compute_metrics
from agentic_mbse.extraction.profile import (
    ProfileEntry,
    format_profile_table,
    get_profile_corpus,
    profile_to_dict,
    route_distribution,
)
from agentic_mbse.extraction.types import (
    PageAction,
    PageDecision,
    PipelineProfile,
    PipelineResult,
)

# ---------------------------------------------------------------------------
# route_distribution
# ---------------------------------------------------------------------------


class TestRouteDistribution:
    def test_mixed_actions(self):
        decisions = [
            PageDecision(0, PageAction.KEEP),
            PageDecision(1, PageAction.CLAUDE_REPLACE),
            PageDecision(2, PageAction.KEEP),
            PageDecision(3, PageAction.GMFT_REPLACE),
        ]
        dist = route_distribution(decisions)
        assert dist == {"keep": 2, "claude_replace": 1, "gmft_replace": 1}

    def test_empty_decisions(self):
        assert route_distribution([]) == {}

    def test_all_same_action(self):
        decisions = [PageDecision(i, PageAction.KEEP) for i in range(5)]
        dist = route_distribution(decisions)
        assert dist == {"keep": 5}

    def test_all_action_types(self):
        decisions = [PageDecision(i, action) for i, action in enumerate(PageAction)]
        dist = route_distribution(decisions)
        for action in PageAction:
            assert dist[action.value] == 1


# ---------------------------------------------------------------------------
# profile_to_dict
# ---------------------------------------------------------------------------


class TestProfileToDict:
    def test_has_expected_keys(self):
        prof = PipelineProfile(base_extraction=1.5, claude_enhancement=8.0)
        decisions = [PageDecision(0, PageAction.KEEP)]
        result = profile_to_dict(prof, decisions, page_count=1, elapsed_seconds=10.0)
        assert "step_timing" in result
        assert "route_distribution" in result
        assert "page_count" in result
        assert "elapsed_seconds" in result

    def test_step_timing_values(self):
        prof = PipelineProfile(base_extraction=1.5, claude_enhancement=8.0)
        decisions = [PageDecision(0, PageAction.KEEP)]
        result = profile_to_dict(prof, decisions, page_count=1, elapsed_seconds=10.0)
        timing = result["step_timing"]
        assert timing["base_extraction"] == 1.5
        assert timing["claude_enhancement"] == 8.0
        assert timing["arxiv_shortcut"] == 0.0

    def test_route_distribution_included(self):
        prof = PipelineProfile()
        decisions = [
            PageDecision(0, PageAction.KEEP),
            PageDecision(1, PageAction.CLAUDE_REPLACE),
        ]
        result = profile_to_dict(prof, decisions, page_count=2, elapsed_seconds=5.0)
        assert result["route_distribution"] == {"keep": 1, "claude_replace": 1}

    def test_page_count_and_elapsed(self):
        prof = PipelineProfile()
        result = profile_to_dict(prof, [], page_count=12, elapsed_seconds=14.2)
        assert result["page_count"] == 12
        assert result["elapsed_seconds"] == 14.2


# ---------------------------------------------------------------------------
# format_profile_table
# ---------------------------------------------------------------------------


class TestFormatProfileTable:
    def test_single_entry(self):
        entry = ProfileEntry(
            document="test_doc",
            pages=5,
            route_dist={"keep": 3, "claude_replace": 2},
            elapsed=10.0,
            profile=PipelineProfile(base_extraction=2.0, claude_enhancement=7.0),
        )
        table = format_profile_table([entry])
        assert "test_doc" in table
        assert "Total" in table
        assert "Pipeline Profile Summary" in table

    def test_multiple_entries(self):
        entries = [
            ProfileEntry(
                document="doc_a",
                pages=12,
                route_dist={"keep": 3, "claude_replace": 6, "gmft_replace": 3},
                elapsed=14.2,
                profile=PipelineProfile(
                    base_extraction=1.1,
                    table_detection=2.0,
                    table_filter_enhance=0.3,
                    quality_gate=0.1,
                    claude_enhancement=9.8,
                    route_merge=0.1,
                    postprocess=0.1,
                    assemble_result=0.0,
                ),
            ),
            ProfileEntry(
                document="doc_b",
                pages=8,
                route_dist={"keep": 8},
                elapsed=3.1,
                profile=PipelineProfile(
                    base_extraction=2.8,
                    table_detection=0.1,
                    quality_gate=0.1,
                    postprocess=0.1,
                ),
            ),
        ]
        table = format_profile_table(entries)
        assert "doc_a" in table
        assert "doc_b" in table
        assert "Total" in table
        # Totals row should sum pages
        lines = table.split("\n")
        totals_line = [line for line in lines if line.startswith("Total")][0]
        assert "20" in totals_line  # 12 + 8 pages

    def test_empty_entries(self):
        assert format_profile_table([]) == ""

    def test_strip_actions_grouped_under_keep(self):
        entry = ProfileEntry(
            document="edge_case",
            pages=3,
            route_dist={"keep": 1, "strip_false": 1, "strip_broken": 1},
            elapsed=1.0,
            profile=PipelineProfile(base_extraction=0.5),
        )
        table = format_profile_table([entry])
        # All 3 actions should be counted under KEEP column
        lines = table.split("\n")
        data_line = [line for line in lines if "edge_case" in line][0]
        # KEEP column should show 3 (1 keep + 1 strip_false + 1 strip_broken)
        parts = data_line.split()
        # parts: [document, pages, keep, claude, gmft, time, base, tables, gate, claude_t, post]
        assert parts[0] == "edge_case"
        assert parts[2] == "3"  # KEEP column

    def test_gmft_actions_grouped(self):
        entry = ProfileEntry(
            document="gmft_test",
            pages=4,
            route_dist={"gmft_replace": 2, "gmft_append": 1, "keep": 1},
            elapsed=2.0,
            profile=PipelineProfile(),
        )
        table = format_profile_table([entry])
        lines = table.split("\n")
        data_line = [line for line in lines if "gmft_test" in line][0]
        parts = data_line.split()
        assert parts[4] == "3"  # GMFT column: 2 + 1

    def test_long_document_name_widens_column(self):
        entry = ProfileEntry(
            document="a_very_long_document_name_that_exceeds_24",
            pages=1,
            route_dist={"keep": 1},
            elapsed=1.0,
            profile=PipelineProfile(),
        )
        table = format_profile_table([entry])
        assert "a_very_long_document_name_that_exceeds_24" in table


# ---------------------------------------------------------------------------
# get_profile_corpus
# ---------------------------------------------------------------------------


class TestGetProfileCorpus:
    def test_discovers_corpus_pdfs(self):
        result = get_profile_corpus()
        assert isinstance(result, list)
        # If running from repo root, corpus should have 10 PDFs
        if result:
            assert len(result) == 10
            assert all(p.suffix == ".pdf" for p in result)


# ---------------------------------------------------------------------------
# CLI integration
# ---------------------------------------------------------------------------

class _MockArgs:
    """Minimal mock argparse namespace for CLI tests."""

    def __init__(self, **kwargs):
        defaults = dict(
            path=None,
            output=None,
            backend=None,
            timeout=600,
            force=False,
            index=False,
            summarize=False,
            budget=0,
            no_tables=False,
            no_img2table=False,
            docling=False,
            model="sonnet",
            html_path=None,
            dry_run=False,
            profile=False,
            check=False,
            check_json=False,
        )
        defaults.update(kwargs)
        for k, v in defaults.items():
            setattr(self, k, v)


def _mock_pipeline_result(num_pages=1, with_profile=True):
    """Create a PipelineResult with optional profile attached."""
    decisions = [PageDecision(i, PageAction.KEEP) for i in range(num_pages)]
    prof = PipelineProfile(base_extraction=1.0, quality_gate=0.05) if with_profile else None
    return PipelineResult(
        markdown="# Test\n\nContent.",
        metrics=compute_metrics("# Test\n\nContent."),
        decisions=decisions,
        source="pdf_pipeline",
        elapsed_seconds=2.5,
        profile=prof,
    )


class TestProfileCLIIntegration:
    def test_profile_json_written(self, tmp_path):
        """profile.json written alongside output.md when --profile active."""
        pdf = tmp_path / "doc.pdf"
        pdf.write_bytes(b"fake")
        out = tmp_path / "out"

        args = _MockArgs(path=str(pdf), output=str(out), profile=True)
        result = _mock_pipeline_result()

        with patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=result):
            rc = cmd_extract(args)

        assert rc == 0
        profile_path = out / "doc" / "profile.json"
        assert profile_path.exists()
        data = json.loads(profile_path.read_text())
        assert "step_timing" in data
        assert "route_distribution" in data
        assert data["page_count"] == 1
        assert data["step_timing"]["base_extraction"] == 1.0

    def test_profile_json_not_written_without_flag(self, tmp_path):
        """No profile.json when --profile not set."""
        pdf = tmp_path / "doc.pdf"
        pdf.write_bytes(b"fake")
        out = tmp_path / "out"

        args = _MockArgs(path=str(pdf), output=str(out), profile=False)
        result = _mock_pipeline_result(with_profile=False)

        with patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=result):
            cmd_extract(args)

        assert not (out / "doc" / "profile.json").exists()

    def test_profile_summary_table_printed(self, tmp_path, capsys):
        """Summary table printed to stderr for multi-document profiling run."""
        # Create a directory with 2 PDFs
        pdf_dir = tmp_path / "pdfs"
        pdf_dir.mkdir()
        (pdf_dir / "a.pdf").write_bytes(b"fake")
        (pdf_dir / "b.pdf").write_bytes(b"fake")
        out = tmp_path / "out"

        args = _MockArgs(path=str(pdf_dir), output=str(out), profile=True)
        result = _mock_pipeline_result()

        with patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=result):
            cmd_extract(args)

        captured = capsys.readouterr()
        assert "Pipeline Profile Summary" in captured.err
        assert "Total" in captured.err

    def test_profile_flag_threads_to_config(self, tmp_path):
        """--profile sets config.profile=True."""
        pdf = tmp_path / "doc.pdf"
        pdf.write_bytes(b"fake")
        out = tmp_path / "out"

        args = _MockArgs(path=str(pdf), output=str(out), profile=True)
        result = _mock_pipeline_result()

        with patch("agentic_mbse.cli.extract_cli.extract_pdf", return_value=result) as mock_pipe:
            cmd_extract(args)
        _, kwargs = mock_pipe.call_args
        assert kwargs["config"].profile is True
