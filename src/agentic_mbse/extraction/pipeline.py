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
from agentic_mbse.extraction.equations import detect_equations
from agentic_mbse.extraction.metrics import compute_metrics
from agentic_mbse.extraction.postprocess import (
    normalize_image_paths,
    promote_figure_captions,
    repair_ligatures,
    strip_page_numbers,
    strip_running_headers,
)
from agentic_mbse.extraction.pymupdf_backend import extract_pages
from agentic_mbse.extraction.quality_gate import (
    QualityGateConfig,
    assess_heading_anomaly,
    assess_page,
    count_headings,
    has_pipe_tables,
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
    DetectedEquation,
    DetectedTable,
    ImageEntry,
    PageAction,
    PageAssessment,
    PageResult,
    PipelineProfile,
    PipelineResult,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Image collector
# ---------------------------------------------------------------------------


@dataclass
class ImageCollector:
    """Accumulate images from temp directories and copy to output."""

    output_dir: Path
    entries: list[ImageEntry] = field(default_factory=list)

    def add(self, source_path: Path, rel_name: str, kind: str, page_num: int) -> str:
        """Register an image for persistence. Returns markdown ref."""
        self.entries.append(ImageEntry(source_path, rel_name, kind, page_num))
        return f"![](images/{rel_name})"

    def persist(self) -> int:
        """Copy all registered images to output_dir. Returns count."""
        if not self.entries:
            return 0
        self.output_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        for entry in self.entries:
            dest = self.output_dir / entry.rel_name
            try:
                shutil.copy2(entry.source_path, dest)
                count += 1
            except (FileNotFoundError, OSError) as exc:
                logger.warning("Failed to persist %s: %s", entry.rel_name, exc)
        return count

    @property
    def total_image_count(self) -> int:
        """Count all image files in output_dir (figures + collected)."""
        if not self.output_dir.exists():
            return 0
        return sum(1 for f in self.output_dir.iterdir() if f.is_file())


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
    enable_equations: bool = True
    enable_claude: bool = True
    arxiv_html_path: Path | None = None
    dry_run: bool = False
    page_image_dir: Path | None = None
    extracted_images_dir: Path | None = None
    quality_gate: QualityGateConfig = field(default_factory=QualityGateConfig)
    profile: bool = False
    save_source: bool = False  # carry raw bytes on PipelineResult for --save-source


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _try_arxiv_shortcut(pdf_path: Path, config: PipelineConfig) -> PipelineResult | None:
    """Attempt arXiv HTML shortcut via Pandoc.

    Returns PipelineResult with source="pandoc_arxiv" on success, None on failure.
    """
    from agentic_mbse.extraction.frontmatter import compute_source_hash
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

        markdown, raw_bytes = convert_arxiv_html(html_source)
        metrics = compute_metrics(markdown)
        content_hash = compute_source_hash(raw_bytes)
        return PipelineResult(
            markdown=markdown,
            metrics=metrics,
            source="pandoc_arxiv",
            source_url=html_source if html_source.startswith("http") else None,
            content_hash=content_hash,
            raw_source_bytes=raw_bytes if config.save_source else None,
        )
    except Exception:
        logger.debug("arXiv shortcut failed, falling through to PDF extraction", exc_info=True)
        return None


def _try_detect_tables(pdf_path: Path, config: PipelineConfig) -> dict[int, list[DetectedTable]]:
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


def _try_detect_equations(pdf_path: Path, config: PipelineConfig) -> dict[int, list[DetectedEquation]]:
    """Detect equations with error isolation. Returns {} on failure."""
    try:
        return detect_equations(pdf_path)
    except Exception:
        logger.warning("Equation detection failed, continuing without equations", exc_info=True)
        return {}


def _insert_equation_refs(
    page_md: str,
    equations: list[DetectedEquation],
    page_num: int,
    collector: ImageCollector,
) -> str:
    """Insert equation crop image references into page markdown.

    Places each equation's image reference at the line closest to its
    vertical position on the original page, preferring insertion after
    blank lines to avoid breaking paragraphs.
    """
    lines = page_md.split("\n")
    if not lines:
        return page_md

    # Process equations sorted by y_fraction (top to bottom).
    # Track insertions so later offsets account for earlier inserts.
    offset = 0
    for eq_idx, eq in enumerate(sorted(equations, key=lambda e: e.y_fraction)):
        if eq.image_path is None:
            continue

        rel_name = f"page_{page_num:03d}_eq_{eq_idx}.png"
        ref = collector.add(eq.image_path, rel_name, "equation_crop", page_num)

        target = int(eq.y_fraction * len(lines)) + offset
        target = max(0, min(target, len(lines) - 1))

        # Search forward from target for nearest blank line (within 5 lines)
        insert_at = target
        for scan in range(target, min(target + 5, len(lines))):
            if not lines[scan].strip():
                insert_at = scan
                break

        lines.insert(insert_at + 1, ref)
        offset += 1

    return "\n".join(lines)


def _postprocess_final(
    markdown: str,
    extracted_images_dir: Path | None = None,
) -> str:
    """Apply deterministic cleanup to the final merged markdown.

    Selectively applies ONLY the safe str→str transforms from
    postprocess.py. Does NOT apply header promotion/demotion (FR-4).

    When *extracted_images_dir* is provided, normalizes absolute image
    paths to relative ``images/`` and promotes figure captions to alt-text.
    """
    markdown = strip_page_numbers(markdown)
    markdown = strip_running_headers(markdown)
    markdown = repair_ligatures(markdown)
    if extracted_images_dir is not None:
        markdown = normalize_image_paths(markdown, extracted_images_dir)
        markdown = promote_figure_captions(markdown)
    return markdown


def _cross_reference_gmft(
    assessments: list[PageAssessment],
    pages: list[PageResult],
    detected_tables: dict[int, list[DetectedTable]],
    severity_boost: float = 1.5,
) -> None:
    """Boost severity on pages where GMFT found tables pymupdf missed.

    Mutates assessments in-place. When GMFT detected tables on a page
    but pymupdf4llm produced no pipe tables, this is a strong signal of
    structural failure (table rendered as flowing paragraphs). Sets
    needs_claude=True and needs_gmft=True so the page competes for
    Claude budget and falls back to GMFT_REPLACE if over budget.
    """
    for assessment in assessments:
        pnum = assessment.page_num
        if pnum not in detected_tables:
            continue
        page_md = pages[pnum].markdown
        if has_pipe_tables(page_md):
            continue  # pymupdf produced pipe tables — no structural failure
        # GMFT found tables but pymupdf produced only flat text
        assessment.needs_claude = True
        assessment.needs_gmft = True  # fallback if Claude over budget
        assessment.severity += severity_boost
        assessment.reasons.append(
            f"GMFT_XREF: GMFT found {len(detected_tables[pnum])} table(s) "
            f"but pymupdf produced no pipe tables (severity +{severity_boost})"
        )


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
    prof = PipelineProfile() if config.profile else None
    all_costs: list[CostRecord] = []

    # Create collector if images dir is configured
    collector: ImageCollector | None = None
    if config.extracted_images_dir:
        collector = ImageCollector(output_dir=config.extracted_images_dir)

    # ------------------------------------------------------------------
    # Step 1: arXiv shortcut (early return)
    # ------------------------------------------------------------------
    if prof:
        _t = time.perf_counter()
    arxiv_result = _try_arxiv_shortcut(pdf_path, config)
    if prof:
        prof.arxiv_shortcut = time.perf_counter() - _t
    if arxiv_result is not None:
        arxiv_result.elapsed_seconds = time.time() - start_time
        arxiv_result.profile = prof
        return arxiv_result

    # ------------------------------------------------------------------
    # Step 2: Base extraction (only step that propagates errors)
    # ------------------------------------------------------------------
    if prof:
        _t = time.perf_counter()
    try:
        pages = extract_pages(pdf_path, extracted_images_dir=config.extracted_images_dir)
    except Exception as exc:
        if prof:
            prof.base_extraction = time.perf_counter() - _t
        return PipelineResult(
            markdown="",
            metrics=compute_metrics(""),
            error=str(exc),
            elapsed_seconds=time.time() - start_time,
            profile=prof,
        )
    if prof:
        prof.base_extraction = time.perf_counter() - _t

    # ------------------------------------------------------------------
    # Step 3: Ensemble table detection (error-isolated)
    # ------------------------------------------------------------------
    if prof:
        _t = time.perf_counter()
    if config.enable_tables:
        detected_tables = _try_detect_tables(pdf_path, config)
    else:
        detected_tables = {}
    if prof:
        prof.table_detection = time.perf_counter() - _t

    # ------------------------------------------------------------------
    # Step 3b: Table filtering and enhancement
    # ------------------------------------------------------------------
    if prof:
        _t = time.perf_counter()
    # Pre-flight: check Claude availability once for both table and page loops
    claude_available = bool(config.enable_claude and not config.dry_run and shutil.which("claude"))
    if config.enable_claude and not config.dry_run and not claude_available:
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
                        etable, ecost = enhance_table_with_claude(table, model=config.claude_model)
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
                            page_num,
                            i,
                            exc_info=True,
                        )

            # No Claude enhancement (budget/dry_run/disabled/not needed/failed)
            if table.extraction_failed:
                # Can't use this table without Claude
                continue
            enhanced.append(table)

        # Register table crop images with the collector
        if collector is not None:
            for j, etbl in enumerate(enhanced):
                if etbl.image_path is not None:
                    rel_name = f"page_{page_num:03d}_table_{j}.png"
                    img_ref = collector.add(etbl.image_path, rel_name, "table_crop", page_num)
                    etbl.markdown = f"{img_ref}\n\n{etbl.markdown}"

        if enhanced:
            final_tables[page_num] = enhanced

    if prof:
        prof.table_filter_enhance = time.perf_counter() - _t

    # ------------------------------------------------------------------
    # Step 3c: Equation detection (error-isolated)
    # ------------------------------------------------------------------
    if prof:
        _t = time.perf_counter()
    detected_equations: dict[int, list[DetectedEquation]] = {}
    if config.enable_equations and config.extracted_images_dir:
        detected_equations = _try_detect_equations(pdf_path, config)
    if prof:
        prof.equation_detection = time.perf_counter() - _t

    # ------------------------------------------------------------------
    # Step 4: Quality gate per page + document-level heading anomaly
    # ------------------------------------------------------------------
    if prof:
        _t = time.perf_counter()
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

    if prof:
        prof.quality_gate = time.perf_counter() - _t

    # ------------------------------------------------------------------
    # Step 4b: GMFT cross-reference (boost pages where GMFT found
    #          tables that pymupdf missed)
    # ------------------------------------------------------------------
    if prof:
        _t = time.perf_counter()
    _cross_reference_gmft(
        assessments,
        pages,
        final_tables,
        severity_boost=config.quality_gate.gmft_xref_severity_boost,
    )
    if prof:
        prof.gmft_xref = time.perf_counter() - _t

    # ------------------------------------------------------------------
    # Step 5: Budget allocation (remaining budget after table spend)
    # ------------------------------------------------------------------
    if prof:
        _t = time.perf_counter()
    remaining_budget = max(0.0, config.claude_budget_usd - table_claude_spend)
    page_budget = EnhancerBudget(
        total_usd=remaining_budget,
        cost_per_page_usd=config.claude_cost_per_page_usd,
    )
    claude_pages = allocate_budget(assessments, page_budget)
    if prof:
        prof.budget_allocation = time.perf_counter() - _t

    # ------------------------------------------------------------------
    # Step 6: Claude page enhancement
    # ------------------------------------------------------------------
    if prof:
        _t = time.perf_counter()
    claude_results: dict[int, str] = {}  # page_num -> claude markdown

    if claude_available and claude_pages:
        if len(claude_pages) > 0:
            logger.info(
                "Claude enhancement: processing %d pages (budget $%.2f remaining)",
                len(claude_pages),
                remaining_budget,
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

                accept, reason = validate_claude_output(claude_md, page.markdown, page_num)
                if accept:
                    claude_results[page_num] = claude_md
                else:
                    logger.warning("Claude output rejected for page %d: %s", page_num, reason)
            except Exception:
                logger.warning(
                    "Claude page enhancement failed for page %d, skipping",
                    page_num,
                    exc_info=True,
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
                succeeded,
                total,
                failed,
            )
        else:
            logger.warning(
                "Claude enhancement: 0/%d pages succeeded",
                total,
            )

    if prof:
        prof.claude_enhancement = time.perf_counter() - _t

    # ------------------------------------------------------------------
    # Step 7: Route and merge per page
    # ------------------------------------------------------------------
    if prof:
        _t = time.perf_counter()
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
            page_md = claude_results[pnum]
        elif decision.action == PageAction.CLAUDE_REPLACE and pnum not in claude_results:
            # Claude was intended but failed/unavailable — record the truth
            decision.action = PageAction.KEEP
            decision.reasons.append("Claude enhancement unavailable — kept original")
            page_md = page.markdown
        elif decision.action == PageAction.GMFT_REPLACE and page_tables:
            page_md = replace_tables(page.markdown, page_tables)
        elif decision.action == PageAction.GMFT_APPEND and page_tables:
            page_md = insert_tables_at_end(page.markdown, page_tables)
        elif decision.action == PageAction.STRIP_FALSE:
            page_md = strip_pipe_tables(page.markdown)
        elif decision.action == PageAction.STRIP_BROKEN:
            page_md = strip_pipe_tables(page.markdown)
        else:
            # KEEP
            page_md = page.markdown

        # Insert equation crop references
        if collector is not None and pnum in detected_equations:
            page_md = _insert_equation_refs(page_md, detected_equations[pnum], pnum, collector)

        merged_pages.append(page_md)

    if prof:
        prof.route_merge = time.perf_counter() - _t

    # ------------------------------------------------------------------
    # Step 7b: Postprocess cleanup (running headers, page numbers, ligatures)
    # ------------------------------------------------------------------
    if prof:
        _t = time.perf_counter()
    if collector is not None:
        collector.persist()

    final_markdown = "\n\n".join(merged_pages)
    final_markdown = _postprocess_final(
        final_markdown, extracted_images_dir=config.extracted_images_dir
    )
    if prof:
        prof.postprocess = time.perf_counter() - _t

    # ------------------------------------------------------------------
    # Step 8: Assemble final result
    # ------------------------------------------------------------------
    if prof:
        _t = time.perf_counter()
    elapsed = time.time() - start_time
    metrics = compute_metrics(final_markdown, elapsed=elapsed)
    total_cost = sum(c.cost_usd for c in all_costs)
    image_count = collector.total_image_count if collector else 0
    if prof:
        prof.assemble_result = time.perf_counter() - _t

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
        image_count=image_count,
        profile=prof,
    )
