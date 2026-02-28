"""Pipeline orchestration for the v4 PDF extraction pipeline.

Contains EnhancerBudget, allocate_budget() (from Item 2 stub),
PipelineConfig, and extract_pdf() (Item 3 orchestrator).
"""

from __future__ import annotations

import logging
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path

from agentic_mbse.extraction.claude_enhance import (
    extract_page_with_claude,
    validate_claude_output,
)
from agentic_mbse.extraction.metrics import compute_metrics
from agentic_mbse.extraction.pymupdf_backend import extract_pages
from agentic_mbse.extraction.quality_gate import (
    QualityGateConfig,
    assess_heading_anomaly,
    assess_page,
    count_headings,
    route_page,
)
from agentic_mbse.extraction.tables import (
    assess_table_quality,
    detect_tables_ensemble,
    enhance_table_with_claude,
    filter_tables,
    insert_tables_at_end,
    replace_tables,
    strip_pipe_tables,
)
from agentic_mbse.extraction.types import (
    CostRecord,
    DetectedTable,
    PageAction,
    PageAssessment,
    PipelineResult,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Budget allocation (from Item 2 stub)
# ---------------------------------------------------------------------------


@dataclass
class EnhancerBudget:
    total_usd: float
    cost_per_page_usd: float

    @property
    def max_pages(self) -> int:
        if self.cost_per_page_usd <= 0:
            return 0
        return int(self.total_usd / self.cost_per_page_usd)


def allocate_budget(
    assessments: list[PageAssessment],
    budget: EnhancerBudget,
    needs_field: str = "needs_claude",
) -> set[int]:
    """Select pages for enhancement within a dollar budget.

    Sorts eligible pages by severity (highest first) and takes the top N
    that fit within the budget.

    Args:
        assessments: All page assessments from the document.
        budget: Dollar budget and per-page cost.
        needs_field: Assessment attribute to check for eligibility.
            Defaults to "needs_claude". Use "needs_gmft" for table budgets.

    Returns:
        Set of 0-indexed page numbers selected for enhancement.
    """
    eligible = [a for a in assessments if getattr(a, needs_field, False)]
    ranked = sorted(eligible, key=lambda a: a.severity, reverse=True)
    selected = ranked[: budget.max_pages]
    return {a.page_num for a in selected}


# ---------------------------------------------------------------------------
# Pipeline configuration
# ---------------------------------------------------------------------------


@dataclass
class PipelineConfig:
    claude_budget_usd: float = 2.0
    claude_cost_per_page_usd: float = 0.078
    claude_model: str = "sonnet"
    enable_tables: bool = True
    enable_img2table: bool = True
    enable_docling: bool = False
    enable_claude: bool = True
    arxiv_html_path: Path | None = None
    dry_run: bool = False
    page_image_dir: Path | None = None
    quality_gate: QualityGateConfig = field(default_factory=QualityGateConfig)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _try_arxiv_shortcut(
    pdf_path: Path, config: PipelineConfig
) -> PipelineResult | None:
    """Attempt arXiv HTML shortcut via Pandoc.

    Returns PipelineResult with source="pandoc_arxiv" on success, None on failure.
    """
    from agentic_mbse.extraction.pandoc_convert import (
        _pandoc_available,
        check_arxiv_html,
        convert_arxiv_html,
        detect_arxiv_id,
    )

    try:
        if not _pandoc_available():
            return None

        if config.arxiv_html_path is not None:
            html_source = str(config.arxiv_html_path)
        else:
            arxiv_id = detect_arxiv_id(pdf_path)
            if arxiv_id is None:
                return None
            html_url = check_arxiv_html(arxiv_id)
            if html_url is None:
                return None
            html_source = html_url

        markdown = convert_arxiv_html(html_source)
        metrics = compute_metrics(markdown)
        return PipelineResult(
            markdown=markdown,
            metrics=metrics,
            source="pandoc_arxiv",
        )
    except Exception:
        logger.debug("arXiv shortcut failed, falling through to PDF extraction", exc_info=True)
        return None


def _try_detect_tables(
    pdf_path: Path, config: PipelineConfig
) -> dict[int, list[DetectedTable]]:
    """Detect tables with error isolation. Returns {} on failure."""
    try:
        return detect_tables_ensemble(
            pdf_path,
            enable_img2table=config.enable_img2table,
            enable_docling=config.enable_docling,
        )
    except Exception:
        logger.warning("Table detection failed, continuing without tables", exc_info=True)
        return {}


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------


def extract_pdf(
    pdf_path: Path,
    config: PipelineConfig | None = None,
) -> PipelineResult:
    """Extract a PDF through the 8-step pipeline.

    Args:
        pdf_path: Path to the PDF file.
        config: Pipeline configuration. Uses defaults if None.

    Returns:
        PipelineResult with markdown, metrics, decisions, cost, and source.
    """
    if config is None:
        config = PipelineConfig()

    start_time = time.time()
    all_costs: list[CostRecord] = []

    # ------------------------------------------------------------------
    # Step 1: arXiv shortcut (early return)
    # ------------------------------------------------------------------
    arxiv_result = _try_arxiv_shortcut(pdf_path, config)
    if arxiv_result is not None:
        arxiv_result.elapsed_seconds = time.time() - start_time
        return arxiv_result

    # ------------------------------------------------------------------
    # Step 2: Base extraction (only step that propagates errors)
    # ------------------------------------------------------------------
    try:
        pages = extract_pages(pdf_path)
    except Exception as exc:
        return PipelineResult(
            markdown="",
            metrics=compute_metrics(""),
            error=str(exc),
            elapsed_seconds=time.time() - start_time,
        )

    # ------------------------------------------------------------------
    # Step 3: Ensemble table detection (error-isolated)
    # ------------------------------------------------------------------
    if config.enable_tables:
        detected_tables = _try_detect_tables(pdf_path, config)
    else:
        detected_tables = {}

    # ------------------------------------------------------------------
    # Step 3b: Table filtering and enhancement
    # ------------------------------------------------------------------
    # Pre-flight: check Claude availability once for both table and page loops
    claude_available = bool(
        config.enable_claude
        and not config.dry_run
        and shutil.which("claude")
    )
    if (
        config.enable_claude
        and not config.dry_run
        and not claude_available
    ):
        logger.warning("Claude CLI not found on PATH; Claude enhancement disabled")

    table_claude_spend = 0.0
    # Final tables per page after filtering/enhancement
    final_tables: dict[int, list[DetectedTable]] = {}
    # Filter reasons per page
    table_filter_reasons: dict[int, list[str]] = {}

    for page_num, raw_tables in detected_tables.items():
        kept, reasons = filter_tables(raw_tables)
        table_filter_reasons[page_num] = reasons

        enhanced: list[DetectedTable] = []
        for i, table in enumerate(kept):
            needs_enhance, _assess_reasons = assess_table_quality(table)

            if needs_enhance and claude_available:
                remaining = config.claude_budget_usd - table_claude_spend
                if remaining >= config.claude_cost_per_page_usd:
                    try:
                        etable, ecost = enhance_table_with_claude(
                            table, model=config.claude_model
                        )
                        ecost.page_num = page_num
                        ecost.table_index = i
                        all_costs.append(ecost)
                        table_claude_spend += ecost.cost_usd

                        # FP filter: Claude returned empty → drop table
                        if not etable.markdown.strip():
                            continue
                        enhanced.append(etable)
                        continue
                    except Exception:
                        logger.warning(
                            "Table enhancement failed for page %d table %d, skipping",
                            page_num, i, exc_info=True,
                        )

            # No Claude enhancement (budget/dry_run/disabled/not needed/failed)
            if table.extraction_failed:
                # Can't use this table without Claude
                continue
            enhanced.append(table)

        if enhanced:
            final_tables[page_num] = enhanced

    # ------------------------------------------------------------------
    # Step 4: Quality gate per page + document-level heading anomaly
    # ------------------------------------------------------------------
    assessments: list[PageAssessment] = []
    for page in pages:
        assessment = assess_page(page.markdown, page.page_num, config.quality_gate)
        assessments.append(assessment)

    # Document-level heading anomaly check
    total_headings = sum(count_headings(p.markdown) for p in pages)
    has_anomaly, _anomaly_reasons = assess_heading_anomaly(
        total_headings, len(pages), config.quality_gate
    )
    if has_anomaly:
        for a in assessments:
            if a.needs_claude:
                a.severity += config.quality_gate.heading_anomaly_boost

    # ------------------------------------------------------------------
    # Step 5: Budget allocation (remaining budget after table spend)
    # ------------------------------------------------------------------
    remaining_budget = max(0.0, config.claude_budget_usd - table_claude_spend)
    page_budget = EnhancerBudget(
        total_usd=remaining_budget,
        cost_per_page_usd=config.claude_cost_per_page_usd,
    )
    claude_pages = allocate_budget(assessments, page_budget)

    # ------------------------------------------------------------------
    # Step 6: Claude page enhancement
    # ------------------------------------------------------------------
    claude_results: dict[int, str] = {}  # page_num -> claude markdown

    if claude_available and claude_pages:
        if len(claude_pages) > 0:
            logger.info(
                "Claude enhancement: processing %d pages (budget $%.2f remaining)",
                len(claude_pages), remaining_budget,
            )
        for page_num in sorted(claude_pages):
            page = pages[page_num]
            image_path = None
            if config.page_image_dir:
                candidate = config.page_image_dir / f"page_{page_num:03d}.png"
                if candidate.exists():
                    image_path = candidate

            try:
                claude_md, cost = extract_page_with_claude(
                    pdf_path,
                    page_num,
                    model=config.claude_model,
                    image_path=image_path,
                )
                cost.page_num = page_num
                all_costs.append(cost)

                accept, reason = validate_claude_output(
                    claude_md, page.markdown, page_num
                )
                if accept:
                    claude_results[page_num] = claude_md
                else:
                    logger.warning("Claude output rejected for page %d: %s", page_num, reason)
            except Exception:
                logger.warning(
                    "Claude page enhancement failed for page %d, skipping",
                    page_num, exc_info=True,
                )
    elif claude_pages and not claude_available:
        logger.warning(
            "Claude unavailable; %d pages flagged for enhancement will use fallback",
            len(claude_pages),
        )

    # Post-loop summary
    if claude_pages:
        succeeded = len(claude_results)
        total = len(claude_pages)
        if succeeded == total:
            logger.info("Claude enhancement: %d/%d pages succeeded", succeeded, total)
        elif succeeded > 0:
            failed = sorted(claude_pages - set(claude_results.keys()))
            logger.warning(
                "Claude enhancement: %d/%d pages succeeded (pages %s failed)",
                succeeded, total, failed,
            )
        else:
            logger.warning(
                "Claude enhancement: 0/%d pages succeeded", total,
            )

    # ------------------------------------------------------------------
    # Step 7: Route and merge per page
    # ------------------------------------------------------------------
    decisions = []
    merged_pages: list[str] = []

    for i, page in enumerate(pages):
        pnum = page.page_num
        page_tables = final_tables.get(pnum)
        within_budget = pnum in claude_pages

        assessment = assessments[i]
        decision = route_page(assessment, page_tables, page.markdown, within_budget)

        # Attach table filter reasons to decision details
        if pnum in table_filter_reasons:
            decision.details["table_filter"] = table_filter_reasons[pnum]

        decisions.append(decision)

        # Apply the decision
        if decision.action == PageAction.CLAUDE_REPLACE and pnum in claude_results:
            merged_pages.append(claude_results[pnum])
        elif decision.action == PageAction.CLAUDE_REPLACE and pnum not in claude_results:
            # Claude was intended but failed/unavailable — record the truth
            decision.action = PageAction.KEEP
            decision.reasons.append("Claude enhancement unavailable — kept original")
            merged_pages.append(page.markdown)
        elif decision.action == PageAction.GMFT_REPLACE and page_tables:
            merged_pages.append(replace_tables(page.markdown, page_tables))
        elif decision.action == PageAction.GMFT_APPEND and page_tables:
            merged_pages.append(insert_tables_at_end(page.markdown, page_tables))
        elif decision.action == PageAction.STRIP_FALSE:
            merged_pages.append(strip_pipe_tables(page.markdown))
        elif decision.action == PageAction.STRIP_BROKEN:
            merged_pages.append(strip_pipe_tables(page.markdown))
        else:
            # KEEP
            merged_pages.append(page.markdown)

    # ------------------------------------------------------------------
    # Step 8: Assemble final result
    # ------------------------------------------------------------------
    final_markdown = "\n\n".join(merged_pages)
    elapsed = time.time() - start_time
    metrics = compute_metrics(final_markdown, elapsed=elapsed)
    total_cost = sum(c.cost_usd for c in all_costs)

    return PipelineResult(
        markdown=final_markdown,
        metrics=metrics,
        decisions=decisions,
        cost=all_costs,
        total_cost_usd=total_cost,
        source="pdf_pipeline",
        elapsed_seconds=elapsed,
        claude_pages_intended=len(claude_pages),
        claude_pages_succeeded=len(claude_results),
    )
