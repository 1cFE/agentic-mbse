#!/usr/bin/env python3
"""Track 0: Table detection coverage — GMFT vs PyMuPDF find_tables().

Runs both detectors on all test papers. Saves cropped table images from both.
Computes detection overlap (IoU) and coverage summary.

Usage:
    python tests/corpus/pipelines/track0_detection.py
    python tests/corpus/pipelines/track0_detection.py --slugs hawker_2020
    python tests/corpus/pipelines/track0_detection.py --slugs hawker_2020,hsu_2020
"""

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared import CORPUS_DIR, RUNS_DIR, get_pdf_path, load_papers

# All 5 test papers for this spike
SPIKE_SET = [
    "hawker_2020",
    "hsu_2020",
    "hansen_2025",
    "paischer_2025",
    "aries_cost_account",
]
RUN_NAME = "table_spike_track0"

# GMFT false-positive filter thresholds (from shared.py)
GMFT_MIN_CONFIDENCE = 0.98
GMFT_MAX_AVG_CELL_LEN = 80

# PyMuPDF false-positive filter thresholds
PYMUPDF_MIN_ROWS = 2  # At least 2 rows (header + 1 data)
PYMUPDF_MIN_COLS = 2  # At least 2 columns
PYMUPDF_MIN_CELLS = 4  # At least 4 non-empty cells


# ---------------------------------------------------------------------------
# Data types (self-contained for spike)
# ---------------------------------------------------------------------------


@dataclass
class DetectedTable:
    """A table detected by either GMFT or PyMuPDF."""

    detector: str  # "gmft" or "pymupdf"
    page_num: int  # 0-indexed
    table_idx: int  # Index within page for this detector
    bbox: tuple[float, float, float, float]  # (x0, y0, x1, y1) in points
    bbox_normalized: tuple[float, float, float, float]  # (x0, y0, x1, y1) 0-1 range
    image_path: str  # Relative to run dir
    image_width: int
    image_height: int
    confidence: float | None = None  # GMFT only
    num_rows: int | None = None  # PyMuPDF: from find_tables; GMFT: from DataFrame
    num_cols: int | None = None
    avg_cell_length: float | None = None  # GMFT only
    markdown: str | None = None  # GMFT DataFrame markdown (for later tracks)
    filtered: bool = False  # True if rejected by false-positive filter
    filter_reason: str = ""


@dataclass
class OverlapMatch:
    """A pair of detections (GMFT + PyMuPDF) on the same page with IoU > threshold."""

    page_num: int
    gmft_idx: int
    pymupdf_idx: int
    iou: float
    gmft_bbox_norm: tuple[float, float, float, float]
    pymupdf_bbox_norm: tuple[float, float, float, float]


@dataclass
class PaperSummary:
    """Detection summary for one paper."""

    slug: str
    total_pages: int
    gmft_tables_raw: int
    gmft_tables_filtered: int  # After false-positive filter
    pymupdf_tables_raw: int
    pymupdf_tables_filtered: int
    overlap_matches: int  # Tables detected by both (IoU > 0.5)
    gmft_only: int  # Tables only GMFT detected (post-filter)
    pymupdf_only: int  # Tables only PyMuPDF detected (post-filter)
    union_tables: int  # Total unique tables (post-filter)
    elapsed_seconds: float


# ---------------------------------------------------------------------------
# IoU computation
# ---------------------------------------------------------------------------


def compute_iou(
    bbox_a: tuple[float, float, float, float],
    bbox_b: tuple[float, float, float, float],
) -> float:
    """Compute Intersection over Union between two bounding boxes.

    Both bboxes are (x0, y0, x1, y1) in the same coordinate space.
    """
    x0 = max(bbox_a[0], bbox_b[0])
    y0 = max(bbox_a[1], bbox_b[1])
    x1 = min(bbox_a[2], bbox_b[2])
    y1 = min(bbox_a[3], bbox_b[3])

    if x1 <= x0 or y1 <= y0:
        return 0.0

    intersection = (x1 - x0) * (y1 - y0)
    area_a = (bbox_a[2] - bbox_a[0]) * (bbox_a[3] - bbox_a[1])
    area_b = (bbox_b[2] - bbox_b[0]) * (bbox_b[3] - bbox_b[1])
    union = area_a + area_b - intersection

    return intersection / union if union > 0 else 0.0


def normalize_bbox(
    bbox: tuple[float, float, float, float],
    page_width: float,
    page_height: float,
) -> tuple[float, float, float, float]:
    """Normalize bbox to 0-1 range relative to page dimensions."""
    return (
        bbox[0] / page_width,
        bbox[1] / page_height,
        bbox[2] / page_width,
        bbox[3] / page_height,
    )


# ---------------------------------------------------------------------------
# GMFT detection
# ---------------------------------------------------------------------------


def detect_gmft_tables(pdf_path: Path, output_dir: Path) -> list[DetectedTable]:
    """Run GMFT AutoTableDetector and save cropped images.

    Returns list of DetectedTable with images saved to output_dir.
    """
    from gmft.auto import AutoTableDetector, AutoTableFormatter
    from gmft.pdf_bindings.pdfium import PyPDFium2Document

    detector = AutoTableDetector()
    formatter = AutoTableFormatter()

    doc = PyPDFium2Document(str(pdf_path))
    results: list[DetectedTable] = []

    try:
        for page_idx in range(len(doc)):
            page = doc.get_page(page_idx)
            tables = detector.extract(page)
            if not tables:
                continue

            # Get page dimensions for normalization
            page_width = page.page.get_width()
            page_height = page.page.get_height()

            for t_idx, table in enumerate(tables):
                bbox = tuple(table.rect.bbox)  # (x0, y0, x1, y1)
                bbox_norm = normalize_bbox(bbox, page_width, page_height)

                # Save cropped image
                img = table.image(dpi=200)
                img_name = f"gmft_p{page_idx:03d}_t{t_idx}.png"
                img_path = output_dir / img_name
                img.save(str(img_path))
                w, h = img.size

                # Try to extract DataFrame for markdown and row/col counts
                markdown = None
                num_rows = None
                num_cols = None
                avg_cell_len = 0.0
                try:
                    ft = formatter.extract(table)
                    df = ft.df()
                    if df is not None and not df.empty:
                        markdown = df.to_markdown(index=False)
                        num_rows = len(df)
                        num_cols = len(df.columns)
                        cell_lengths = []
                        for col in df.columns:
                            for val in df[col]:
                                s = str(val).strip()
                                if s and s != "nan":
                                    cell_lengths.append(len(s))
                        avg_cell_len = (
                            sum(cell_lengths) / len(cell_lengths)
                            if cell_lengths
                            else 0.0
                        )
                except Exception:
                    pass

                # Apply false-positive filter
                filtered = False
                filter_reason = ""
                conf = table.confidence_score

                if conf < GMFT_MIN_CONFIDENCE:
                    filtered = True
                    filter_reason = f"confidence {conf:.3f} < {GMFT_MIN_CONFIDENCE}"
                elif avg_cell_len > GMFT_MAX_AVG_CELL_LEN:
                    filtered = True
                    filter_reason = f"avg cell length {avg_cell_len:.0f} > {GMFT_MAX_AVG_CELL_LEN}"
                elif num_rows == 1 and num_cols is not None and num_cols > 4:
                    filtered = True
                    filter_reason = f"single row with {num_cols} cols (layout artifact)"

                results.append(DetectedTable(
                    detector="gmft",
                    page_num=page_idx,
                    table_idx=t_idx,
                    bbox=bbox,
                    bbox_normalized=bbox_norm,
                    image_path=img_name,
                    image_width=w,
                    image_height=h,
                    confidence=conf,
                    num_rows=num_rows,
                    num_cols=num_cols,
                    avg_cell_length=avg_cell_len,
                    markdown=markdown,
                    filtered=filtered,
                    filter_reason=filter_reason,
                ))
    finally:
        doc.close()

    return results


# ---------------------------------------------------------------------------
# PyMuPDF detection
# ---------------------------------------------------------------------------


def detect_pymupdf_tables(pdf_path: Path, output_dir: Path) -> list[DetectedTable]:
    """Run PyMuPDF find_tables() and save cropped images.

    Returns list of DetectedTable with images saved to output_dir.
    """
    import pymupdf

    doc = pymupdf.open(str(pdf_path))
    results: list[DetectedTable] = []

    try:
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            tabs = page.find_tables()
            if not tabs.tables:
                continue

            page_width = page.rect.width
            page_height = page.rect.height

            for t_idx, tab in enumerate(tabs.tables):
                bbox = tuple(tab.bbox)  # (x0, y0, x1, y1)
                bbox_norm = normalize_bbox(bbox, page_width, page_height)

                # Save cropped image
                pix = page.get_pixmap(dpi=200, clip=tab.bbox)
                img_name = f"pymupdf_p{page_idx:03d}_t{t_idx}.png"
                img_path = output_dir / img_name
                pix.save(str(img_path))

                num_rows = tab.row_count
                num_cols = tab.col_count

                # Count non-empty cells for filtering
                non_empty_cells = 0
                try:
                    extracted = tab.extract()
                    for row in extracted:
                        for cell in row:
                            if cell is not None and str(cell).strip():
                                non_empty_cells += 1
                except Exception:
                    non_empty_cells = num_rows * num_cols  # Assume all populated

                # Apply false-positive filter
                filtered = False
                filter_reason = ""

                if num_rows < PYMUPDF_MIN_ROWS:
                    filtered = True
                    filter_reason = f"rows {num_rows} < {PYMUPDF_MIN_ROWS}"
                elif num_cols < PYMUPDF_MIN_COLS:
                    filtered = True
                    filter_reason = f"cols {num_cols} < {PYMUPDF_MIN_COLS}"
                elif non_empty_cells < PYMUPDF_MIN_CELLS:
                    filtered = True
                    filter_reason = f"non-empty cells {non_empty_cells} < {PYMUPDF_MIN_CELLS}"

                results.append(DetectedTable(
                    detector="pymupdf",
                    page_num=page_idx,
                    table_idx=t_idx,
                    bbox=bbox,
                    bbox_normalized=bbox_norm,
                    image_path=img_name,
                    image_width=pix.width,
                    image_height=pix.height,
                    num_rows=num_rows,
                    num_cols=num_cols,
                    filtered=filtered,
                    filter_reason=filter_reason,
                ))
    finally:
        doc.close()

    return results


# ---------------------------------------------------------------------------
# Overlap detection
# ---------------------------------------------------------------------------


def find_overlaps(
    gmft_tables: list[DetectedTable],
    pymupdf_tables: list[DetectedTable],
    iou_threshold: float = 0.5,
) -> list[OverlapMatch]:
    """Find overlapping detections between GMFT and PyMuPDF on same pages.

    Uses normalized bboxes and IoU > threshold to match.
    Only considers non-filtered tables.
    """
    # Group by page
    gmft_by_page: dict[int, list[DetectedTable]] = {}
    for t in gmft_tables:
        if not t.filtered:
            gmft_by_page.setdefault(t.page_num, []).append(t)

    pymupdf_by_page: dict[int, list[DetectedTable]] = {}
    for t in pymupdf_tables:
        if not t.filtered:
            pymupdf_by_page.setdefault(t.page_num, []).append(t)

    matches: list[OverlapMatch] = []
    # Track which PyMuPDF tables have been matched (greedy matching)
    matched_pymupdf: set[tuple[int, int]] = set()  # (page_num, table_idx)

    for page_num in gmft_by_page:
        if page_num not in pymupdf_by_page:
            continue

        for gt in gmft_by_page[page_num]:
            best_iou = 0.0
            best_pt = None

            for pt in pymupdf_by_page[page_num]:
                key = (pt.page_num, pt.table_idx)
                if key in matched_pymupdf:
                    continue

                iou = compute_iou(gt.bbox_normalized, pt.bbox_normalized)
                if iou > best_iou:
                    best_iou = iou
                    best_pt = pt

            if best_pt is not None and best_iou >= iou_threshold:
                matched_pymupdf.add((best_pt.page_num, best_pt.table_idx))
                matches.append(OverlapMatch(
                    page_num=page_num,
                    gmft_idx=gt.table_idx,
                    pymupdf_idx=best_pt.table_idx,
                    iou=best_iou,
                    gmft_bbox_norm=gt.bbox_normalized,
                    pymupdf_bbox_norm=best_pt.bbox_normalized,
                ))

    return matches


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def run_track0(slug: str) -> PaperSummary | None:
    """Run Track 0 detection on a single paper."""
    pdf_path = get_pdf_path(slug)
    if pdf_path is None:
        print(f"  SKIP {slug}: PDF not found")
        return None

    print(f"\n{'='*60}")
    print(f"  {slug} ({pdf_path.name})")
    print(f"{'='*60}")

    output_dir = RUNS_DIR / RUN_NAME / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    start = time.time()

    # Step 1: GMFT detection
    print(f"  GMFT detecting...", end=" ", flush=True)
    gmft_start = time.time()
    gmft_tables = detect_gmft_tables(pdf_path, output_dir)
    gmft_elapsed = time.time() - gmft_start
    gmft_kept = [t for t in gmft_tables if not t.filtered]
    gmft_rejected = [t for t in gmft_tables if t.filtered]
    print(
        f"{gmft_elapsed:.1f}s — {len(gmft_tables)} raw, "
        f"{len(gmft_kept)} kept, {len(gmft_rejected)} filtered"
    )
    for t in gmft_rejected:
        print(f"    REJECT p{t.page_num} t{t.table_idx}: {t.filter_reason}")

    # Step 2: PyMuPDF detection
    print(f"  PyMuPDF detecting...", end=" ", flush=True)
    pymupdf_start = time.time()
    pymupdf_tables = detect_pymupdf_tables(pdf_path, output_dir)
    pymupdf_elapsed = time.time() - pymupdf_start
    pymupdf_kept = [t for t in pymupdf_tables if not t.filtered]
    pymupdf_rejected = [t for t in pymupdf_tables if t.filtered]
    print(
        f"{pymupdf_elapsed:.1f}s — {len(pymupdf_tables)} raw, "
        f"{len(pymupdf_kept)} kept, {len(pymupdf_rejected)} filtered"
    )
    for t in pymupdf_rejected:
        print(f"    REJECT p{t.page_num} t{t.table_idx}: {t.filter_reason}")

    # Step 3: Overlap detection
    print(f"  Computing overlaps...", end=" ", flush=True)
    overlaps = find_overlaps(gmft_tables, pymupdf_tables)
    print(f"{len(overlaps)} overlapping detections (IoU > 0.5)")
    for m in overlaps:
        print(f"    p{m.page_num}: gmft_t{m.gmft_idx} ↔ pymupdf_t{m.pymupdf_idx} (IoU={m.iou:.2f})")

    # Step 4: Compute union
    gmft_only = len(gmft_kept) - len(overlaps)
    pymupdf_only = len(pymupdf_kept) - len(overlaps)
    union_tables = gmft_only + pymupdf_only + len(overlaps)

    total_elapsed = time.time() - start

    # Print summary
    print(f"\n  Detection Summary:")
    print(f"    GMFT:       {len(gmft_kept)} tables (post-filter)")
    print(f"    PyMuPDF:    {len(pymupdf_kept)} tables (post-filter)")
    print(f"    Both:       {len(overlaps)} tables")
    print(f"    GMFT only:  {gmft_only} tables")
    print(f"    PyMuPDF only: {pymupdf_only} tables")
    print(f"    Union:      {union_tables} tables")
    print(f"    Time:       {total_elapsed:.1f}s")

    # Per-page breakdown
    all_pages = set()
    for t in gmft_kept:
        all_pages.add(t.page_num)
    for t in pymupdf_kept:
        all_pages.add(t.page_num)

    per_page = []
    for pg in sorted(all_pages):
        g_count = sum(1 for t in gmft_kept if t.page_num == pg)
        p_count = sum(1 for t in pymupdf_kept if t.page_num == pg)
        overlap_on_page = sum(1 for m in overlaps if m.page_num == pg)
        per_page.append({
            "page": pg,
            "gmft": g_count,
            "pymupdf": p_count,
            "overlap": overlap_on_page,
        })
        both_tag = f" (overlap: {overlap_on_page})" if overlap_on_page else ""
        print(f"    p{pg:3d}: GMFT={g_count}, PyMuPDF={p_count}{both_tag}")

    # Step 5: Save outputs

    # detection_summary.json
    summary = PaperSummary(
        slug=slug,
        total_pages=len(set(t.page_num for t in gmft_tables + pymupdf_tables))
        or 0,
        gmft_tables_raw=len(gmft_tables),
        gmft_tables_filtered=len(gmft_kept),
        pymupdf_tables_raw=len(pymupdf_tables),
        pymupdf_tables_filtered=len(pymupdf_kept),
        overlap_matches=len(overlaps),
        gmft_only=gmft_only,
        pymupdf_only=pymupdf_only,
        union_tables=union_tables,
        elapsed_seconds=total_elapsed,
    )
    (output_dir / "detection_summary.json").write_text(
        json.dumps(asdict(summary), indent=2) + "\n"
    )

    # images_manifest.json — per-table details for later tracks
    all_tables = gmft_tables + pymupdf_tables
    manifest_entries = []
    for t in all_tables:
        entry = asdict(t)
        # Convert bbox tuples to lists for JSON
        entry["bbox"] = list(t.bbox)
        entry["bbox_normalized"] = list(t.bbox_normalized)
        manifest_entries.append(entry)

    (output_dir / "images_manifest.json").write_text(
        json.dumps(manifest_entries, indent=2) + "\n"
    )

    # overlaps.json
    overlap_data = [asdict(m) for m in overlaps]
    for od in overlap_data:
        od["gmft_bbox_norm"] = list(od["gmft_bbox_norm"])
        od["pymupdf_bbox_norm"] = list(od["pymupdf_bbox_norm"])
    (output_dir / "overlaps.json").write_text(
        json.dumps(overlap_data, indent=2) + "\n"
    )

    # per_page_breakdown.json
    (output_dir / "per_page_breakdown.json").write_text(
        json.dumps(per_page, indent=2) + "\n"
    )

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Track 0: Table detection coverage (GMFT vs PyMuPDF find_tables)"
    )
    parser.add_argument(
        "--slugs",
        type=str,
        default=",".join(SPIKE_SET),
        help=f"Comma-separated paper slugs (default: {','.join(SPIKE_SET)})",
    )
    args = parser.parse_args()
    slugs = [s.strip() for s in args.slugs.split(",")]

    print(f"Track 0: Table Detection Coverage")
    print(f"Papers: {', '.join(slugs)}")
    print(f"Output: runs/{RUN_NAME}/")

    summaries: list[PaperSummary] = []
    for slug in slugs:
        result = run_track0(slug)
        if result:
            summaries.append(result)

    # Print cross-paper summary
    if summaries:
        print(f"\n{'='*60}")
        print(f"  Cross-Paper Summary")
        print(f"{'='*60}")
        print(f"  {'Slug':<25} {'GMFT':>5} {'PyMu':>5} {'Both':>5} {'G-only':>6} {'P-only':>6} {'Union':>5}")
        print(f"  {'-'*25} {'-'*5} {'-'*5} {'-'*5} {'-'*6} {'-'*6} {'-'*5}")
        for s in summaries:
            print(
                f"  {s.slug:<25} {s.gmft_tables_filtered:>5} "
                f"{s.pymupdf_tables_filtered:>5} {s.overlap_matches:>5} "
                f"{s.gmft_only:>6} {s.pymupdf_only:>6} {s.union_tables:>5}"
            )
        totals_gmft = sum(s.gmft_tables_filtered for s in summaries)
        totals_pymupdf = sum(s.pymupdf_tables_filtered for s in summaries)
        totals_overlap = sum(s.overlap_matches for s in summaries)
        totals_gmft_only = sum(s.gmft_only for s in summaries)
        totals_pymupdf_only = sum(s.pymupdf_only for s in summaries)
        totals_union = sum(s.union_tables for s in summaries)
        print(f"  {'-'*25} {'-'*5} {'-'*5} {'-'*5} {'-'*6} {'-'*6} {'-'*5}")
        print(
            f"  {'TOTAL':<25} {totals_gmft:>5} {totals_pymupdf:>5} "
            f"{totals_overlap:>5} {totals_gmft_only:>6} {totals_pymupdf_only:>6} "
            f"{totals_union:>5}"
        )

    # Save cross-paper summary
    summary_dir = RUNS_DIR / RUN_NAME
    summary_dir.mkdir(parents=True, exist_ok=True)
    (summary_dir / "cross_paper_summary.json").write_text(
        json.dumps([asdict(s) for s in summaries], indent=2) + "\n"
    )

    print(f"\n{'='*60}")
    print(f"  Done. Results in runs/{RUN_NAME}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
