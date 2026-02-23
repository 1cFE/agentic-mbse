#!/usr/bin/env python3
"""Experiment harness for extraction parameter exploration.

Runs pymupdf4llm, Docling, or GMFT extraction against corpus PDFs,
computes metrics, and saves results for comparison.

Usage:
    # Run pymupdf4llm baseline config (default backend)
    python tests/corpus/experiment.py baseline

    # Run a named config with parameter overrides
    python tests/corpus/experiment.py lines_strict --params '{"table_strategy": "lines_strict"}'

    # Run Docling extraction
    python tests/corpus/experiment.py docling_baseline --backend docling

    # Run Docling with OCR enabled
    python tests/corpus/experiment.py docling_ocr --backend docling --params '{"do_ocr": true}'

    # Run Docling on a single page
    python tests/corpus/experiment.py docling_page5 --backend docling --page-range 5,5

    # Run GMFT table extraction
    python tests/corpus/experiment.py gmft_baseline --backend gmft

    # Run against specific PDFs only
    python tests/corpus/experiment.py test_config --slugs hawker_2020,hsu_2020

    # Compare against baseline
    python tests/corpus/experiment.py lines_strict --compare baseline

    # List all runs
    python tests/corpus/experiment.py --list
"""

import argparse
import json
import multiprocessing
import sys
import time
import traceback
from pathlib import Path

# Ensure imports work when run directly
sys.path.insert(0, str(Path(__file__).parent))

import re

import pymupdf4llm  # type: ignore[import-untyped]
from metrics import ExtractionMetrics, compare_metrics, compute_metrics

CORPUS_DIR = Path(__file__).parent
PAPERS_JSONL = CORPUS_DIR / "papers.jsonl"
PDFS_DIR = CORPUS_DIR / "pdfs"
RUNS_DIR = CORPUS_DIR / "runs"

# Current production config from pymupdf_backend.py
BASELINE_PARAMS = {
    "write_images": False,
    "dpi": 150,
    "page_chunks": False,
    "table_strategy": "lines",
    "force_text": True,
}


# --- Named header detectors (can't be passed as JSON) ---


def _academic_header_detector(span, page=None):
    """Custom header detector from pymupdf_backend.py.

    Uses bold flag + section numbering regex instead of font-size heuristics.
    """
    text = span["text"].strip()
    is_bold = bool(span["flags"] & 16)  # bit 4 = bold
    if not is_bold:
        return ""
    # Numbered sections: "1 Introduction", "2.1 Background", "A.1 Appendix"
    m = re.match(r"^\d+(?:\.\d+)*\.?\s+[A-Z]", text)
    if m:
        sec_num = text.split()[0].rstrip(".")
        depth = sec_num.count(".") + 1
        return "#" * min(depth + 1, 6) + " "
    # All-caps short titles (e.g., "ABSTRACT", "REFERENCES")
    if text.isupper() and len(text) < 60 and len(text.split()) <= 6:
        return "## "
    return ""


def _bold_header_detector(span, page=None):
    """Broader bold-based detector: any bold text that looks like a heading.

    Detects:
    - Numbered sections (Arabic or Roman): "1 Intro", "I. INTRODUCTION", "2.1 Methods"
    - All-caps short titles: "ABSTRACT", "REFERENCES"
    - Short bold lines (< 80 chars, < 10 words) as potential subsection headers
    """
    text = span["text"].strip()
    if not text:
        return ""
    is_bold = bool(span["flags"] & 16)
    if not is_bold:
        return ""

    # Arabic numbered sections: "1 Introduction", "2.1 Background"
    m = re.match(r"^\d+(?:\.\d+)*\.?\s+[A-Z]", text)
    if m:
        sec_num = text.split()[0].rstrip(".")
        depth = sec_num.count(".") + 1
        return "#" * min(depth + 1, 6) + " "

    # Roman numeral sections: "I. INTRODUCTION", "IV. RESULTS"
    m = re.match(r"^(X{0,3})(IX|IV|V?I{0,3})\.?\s+[A-Z]", text)
    if m and (m.group(1) or m.group(2)):  # at least one Roman char
        return "## "

    # All-caps short titles
    if text.isupper() and len(text) < 60 and len(text.split()) <= 6:
        return "## "

    return ""


class _CompositeHeaderDetector:
    """Combines font-size detection (IdentifyHeaders) with bold pattern matching.

    Re-initializes IdentifyHeaders when the underlying document changes.
    For each span:
    1. Check bold + numbering/caps patterns (catches bold-differentiated headers)
    2. Fall back to IdentifyHeaders font-size detection (catches size-differentiated headers)
    3. Return the deeper (more specific) result if both fire
    """

    def __init__(self):
        self._identify_headers = None
        self._current_doc_name = None

    def _ensure_initialized(self, page):
        """Re-initialize IdentifyHeaders when processing a new document."""
        if page is None:
            return
        doc = page.parent
        doc_name = doc.name if doc else None
        if doc_name != self._current_doc_name:
            self._current_doc_name = doc_name
            try:
                from pymupdf4llm.helpers.pymupdf_rag import IdentifyHeaders

                self._identify_headers = IdentifyHeaders(doc)
            except Exception:
                self._identify_headers = None

    def get_header_id(self, span, page=None):
        self._ensure_initialized(page)

        bold_result = _bold_header_detector(span, page)
        font_result = ""
        if self._identify_headers is not None:
            try:
                font_result = self._identify_headers.get_header_id(span, page)
            except Exception:
                font_result = ""

        # If both detect a header, use the deeper (more '#') one
        if bold_result and font_result:
            return bold_result if len(bold_result) > len(font_result) else font_result
        return bold_result or font_result

    def __call__(self, span, page=None):
        return self.get_header_id(span, page)


HDR_INFO_PRESETS = {
    "default": None,  # pymupdf4llm IdentifyHeaders (font-size)
    "off": False,  # No header detection
    "academic": _academic_header_detector,
    "bold": _bold_header_detector,
    "composite": _CompositeHeaderDetector(),
}


def load_papers(slugs: list[str] | None = None) -> list[dict]:
    """Load paper registry, optionally filtering by slug."""
    papers = []
    with PAPERS_JSONL.open() as f:
        for line in f:
            line = line.strip()
            if line:
                paper = json.loads(line)
                if slugs is None or paper["slug"] in slugs:
                    papers.append(paper)
    return papers


def run_extraction(pdf_path: Path, params: dict) -> tuple[str, float]:
    """Run pymupdf4llm.to_markdown() with given params. Returns (markdown, elapsed_seconds)."""
    start = time.time()
    md = pymupdf4llm.to_markdown(str(pdf_path), **params)
    elapsed = time.time() - start
    return md, elapsed


# --- Docling backend ---


def _docling_extract_worker(pdf_path_str: str, params: dict, queue: multiprocessing.Queue) -> None:
    """Run Docling extraction in a child process (memory safety)."""
    try:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import (
            EasyOcrOptions,
            PdfPipelineOptions,
            TesseractCliOcrOptions,
            TableStructureOptions,
            TableFormerMode,
        )
        from docling.document_converter import DocumentConverter, PdfFormatOption

        # Build PdfPipelineOptions from params
        opts_kwargs = {}
        page_range = None
        for k, v in params.items():
            if k == "page_range":
                page_range = tuple(v)  # (start, end), 1-indexed
            elif k == "table_structure_options" and isinstance(v, dict):
                mode = v.get("mode", "accurate")
                tso = TableStructureOptions(
                    mode=TableFormerMode.FAST if mode == "fast" else TableFormerMode.ACCURATE,
                    do_cell_matching=v.get("do_cell_matching", True),
                )
                opts_kwargs[k] = tso
            elif k == "ocr_options" and isinstance(v, dict):
                engine = v.get("engine", "easyocr")
                if engine == "easyocr":
                    opts_kwargs[k] = EasyOcrOptions(
                        lang=v.get("lang", ["en"]),
                        force_full_page_ocr=v.get("force_full_page_ocr", False),
                        confidence_threshold=v.get("confidence_threshold", 0.5),
                    )
                elif engine == "tesseract":
                    opts_kwargs[k] = TesseractCliOcrOptions(
                        lang=v.get("lang", ["eng"]),
                        force_full_page_ocr=v.get("force_full_page_ocr", False),
                    )
            else:
                opts_kwargs[k] = v

        pipeline_opts = PdfPipelineOptions(**opts_kwargs)
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_opts),
            }
        )

        convert_kwargs = {}
        if page_range is not None:
            convert_kwargs["page_range"] = page_range

        conv_result = converter.convert(pdf_path_str, **convert_kwargs)
        md = conv_result.document.export_to_markdown()

        # Count tables and pictures from the document model
        table_count = len(list(conv_result.document.tables)) if hasattr(conv_result.document, "tables") else 0
        picture_count = len(list(conv_result.document.pictures)) if hasattr(conv_result.document, "pictures") else 0

        queue.put(("ok", md, table_count, picture_count))
    except Exception as exc:
        queue.put(("error", f"{type(exc).__name__}: {exc}", 0, 0))


def run_docling_extraction(
    pdf_path: Path, params: dict, timeout: int = 600
) -> tuple[str, float]:
    """Run Docling extraction in a subprocess with timeout. Returns (markdown, elapsed_seconds).

    Raises RuntimeError on timeout or crash.
    """
    queue: multiprocessing.Queue = multiprocessing.Queue()
    proc = multiprocessing.Process(
        target=_docling_extract_worker,
        args=(str(pdf_path), params, queue),
    )

    start = time.time()
    proc.start()
    proc.join(timeout=timeout)
    elapsed = time.time() - start

    if proc.is_alive():
        proc.terminate()
        proc.join(5)
        if proc.is_alive():
            proc.kill()
        raise RuntimeError(f"Docling timed out after {timeout}s")

    if queue.empty():
        raise RuntimeError(f"Docling process crashed (exit code: {proc.exitcode})")

    status, result, table_count, picture_count = queue.get_nowait()
    if status == "error":
        raise RuntimeError(f"Docling extraction failed: {result}")

    return result, elapsed


# --- GMFT backend ---


def run_gmft_extraction(pdf_path: Path, params: dict) -> tuple[str, float]:
    """Run GMFT table detection+formatting. Returns (markdown, elapsed_seconds).

    GMFT only extracts tables, not full document text. The returned markdown
    contains detected tables organized by page.
    """
    from gmft.auto import AutoTableDetector, AutoTableFormatter, AutoFormatConfig
    from gmft.pdf_bindings.pdfium import PyPDFium2Document

    # Build configs from params
    detector_kwargs = {}
    formatter_kwargs = {}
    for k, v in params.items():
        if k == "detector_base_threshold":
            detector_kwargs[k] = v
        else:
            formatter_kwargs[k] = v

    detector_config = None
    if detector_kwargs:
        from gmft.impl.tatr.config import TATRDetectorConfig
        detector_config = TATRDetectorConfig(**detector_kwargs)

    format_config = None
    if formatter_kwargs:
        format_config = AutoFormatConfig(**formatter_kwargs)

    detector = AutoTableDetector(config=detector_config)
    formatter = AutoTableFormatter(config=format_config)

    start = time.time()
    doc = PyPDFium2Document(str(pdf_path))
    md_parts = []
    total_tables = 0

    try:
        for page_idx in range(len(doc)):
            page = doc.get_page(page_idx)
            tables = detector.extract(page)
            if tables:
                md_parts.append(f"\n<!-- PAGE:{page_idx} -->\n")
                for t_idx, table in enumerate(tables):
                    try:
                        ft = formatter.extract(table)
                        df = ft.df()
                        if df is not None and not df.empty:
                            md_parts.append(f"\n**Table {total_tables + 1}** (page {page_idx + 1}, confidence {table.confidence_score:.2f})\n\n")
                            md_parts.append(df.to_markdown(index=False))
                            md_parts.append("\n")
                            total_tables += 1
                        else:
                            md_parts.append(f"\n**Table (empty)** (page {page_idx + 1})\n")
                    except Exception as e:
                        md_parts.append(f"\n**Table (error: {e})** (page {page_idx + 1})\n")
    finally:
        doc.close()

    elapsed = time.time() - start
    md = "\n".join(md_parts) if md_parts else "(no tables detected)"
    return md, elapsed


def run_experiment(config_name: str, params: dict, slugs: list[str] | None = None,
                   backend: str = "pymupdf4llm", timeout: int = 600) -> Path:
    """Run an experiment: extract all corpus PDFs with given params, save results."""
    papers = load_papers(slugs)
    if not papers:
        print("ERROR: No papers found matching the given slugs.")
        sys.exit(1)

    run_dir = RUNS_DIR / config_name
    run_dir.mkdir(parents=True, exist_ok=True)

    # Save config for reproducibility (make params JSON-safe)
    safe_params = {}
    for k, v in params.items():
        if callable(v):
            name = getattr(v, "__name__", type(v).__name__)
            safe_params[k] = f"<callable:{name}>"
        elif v is False:
            safe_params[k] = False
        elif v is None:
            safe_params[k] = None
        else:
            safe_params[k] = v
    config_record = {
        "config_name": config_name,
        "backend": backend,
        "params": safe_params,
        "slugs": [p["slug"] for p in papers],
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    if backend == "docling":
        config_record["timeout"] = timeout
    (run_dir / "config.json").write_text(json.dumps(config_record, indent=2) + "\n")

    print(f"Running config '{config_name}' (backend={backend}) on {len(papers)} PDFs...")
    print(f"Params: {json.dumps(safe_params, indent=2)}")
    print()

    all_metrics = {}

    for paper in papers:
        slug = paper["slug"]
        pdf_path = CORPUS_DIR.parent.parent / paper["pdf_path"]
        if not pdf_path.exists():
            # Try relative to corpus dir
            pdf_path = PDFS_DIR / f"{slug}.pdf"
        if not pdf_path.exists():
            print(f"  SKIP {slug}: PDF not found at {pdf_path}")
            continue

        print(f"  {slug} ({paper.get('pages', '?')}pp)... ", end="", flush=True)

        try:
            if backend == "pymupdf4llm":
                md, elapsed = run_extraction(pdf_path, params)
            elif backend == "docling":
                md, elapsed = run_docling_extraction(pdf_path, params, timeout=timeout)
            elif backend == "gmft":
                md, elapsed = run_gmft_extraction(pdf_path, params)
            else:
                raise ValueError(f"Unknown backend: {backend}")

            metrics = compute_metrics(md, elapsed)

            # Save per-PDF results
            slug_dir = run_dir / slug
            slug_dir.mkdir(exist_ok=True)
            (slug_dir / "output.md").write_text(md)
            (slug_dir / "metrics.json").write_text(
                json.dumps(metrics.to_dict(), indent=2) + "\n"
            )

            all_metrics[slug] = metrics
            print(
                f"{elapsed:.1f}s | "
                f"chars={metrics.char_count:,} "
                f"hdrs={metrics.heading_count} "
                f"tables={metrics.table_row_count} "
                f"math={metrics.math_symbol_count}"
            )
        except Exception as e:
            print(f"ERROR: {e}")
            all_metrics[slug] = None

    print(f"\nResults saved to {run_dir}/")
    return run_dir


def print_comparison(config_name: str, compare_to: str) -> None:
    """Print a comparison table between two experiment runs."""
    run_dir = RUNS_DIR / config_name
    compare_dir = RUNS_DIR / compare_to

    if not run_dir.exists():
        print(f"ERROR: Run '{config_name}' not found at {run_dir}")
        return
    if not compare_dir.exists():
        print(f"ERROR: Run '{compare_to}' not found at {compare_dir}")
        return

    papers = load_papers()

    print(f"\n{'='*80}")
    print(f"Comparison: {compare_to} → {config_name}")
    print(f"{'='*80}")
    print(
        f"{'Document':<22} {'Chars':>12} {'Headings':>12} {'Tables':>12} {'Time':>8}"
    )
    print("-" * 70)

    regressions = []

    for paper in papers:
        slug = paper["slug"]
        base_metrics_path = compare_dir / slug / "metrics.json"
        curr_metrics_path = run_dir / slug / "metrics.json"

        if not base_metrics_path.exists() or not curr_metrics_path.exists():
            continue

        base = ExtractionMetrics.from_dict(json.loads(base_metrics_path.read_text()))
        curr = ExtractionMetrics.from_dict(json.loads(curr_metrics_path.read_text()))
        delta = compare_metrics(base, curr)

        def fmt_delta(name: str) -> str:
            d = delta[f"{name}_delta"]
            pct = delta[f"{name}_pct"]
            if d == 0:
                return "(=)"
            return f"({d:+d} {pct:+.0f}%)"

        def fmt_chars() -> str:
            d = delta["char_count_delta"]
            pct = delta["char_count_pct"]
            if abs(pct) < 1:
                return "(~)"
            return f"({d//1000:+d}k {pct:+.1f}%)"

        def fmt_time() -> str:
            d = delta["time_delta"]
            if abs(d) < 0.1:
                return "(~)"
            return f"({d:+.1f}s)"

        flag = " !!!" if delta["has_regression"] else ""
        print(
            f"{slug:<22} {fmt_chars():>12} {fmt_delta('heading_count'):>12} "
            f"{fmt_delta('table_row_count'):>12} {fmt_time():>8}{flag}"
        )

        if delta["has_regression"]:
            regressions.append(slug)

    if regressions:
        print(f"\nREGRESSIONS in: {', '.join(regressions)}")
    else:
        print("\nNo regressions detected.")


def list_runs() -> None:
    """List all experiment runs."""
    if not RUNS_DIR.exists():
        print("No experiment runs yet.")
        return

    print(f"{'Config':<25} {'Backend':<12} {'PDFs':>5} {'Timestamp':<20}")
    print("-" * 67)

    for run_dir in sorted(RUNS_DIR.iterdir()):
        if not run_dir.is_dir():
            continue
        config_path = run_dir / "config.json"
        if config_path.exists():
            config = json.loads(config_path.read_text())
            n_pdfs = len(config.get("slugs", []))
            ts = config.get("timestamp", "?")
            be = config.get("backend", "pymupdf4llm")
        else:
            n_pdfs = sum(1 for d in run_dir.iterdir() if d.is_dir())
            ts = "?"
            be = "?"
        print(f"{run_dir.name:<25} {be:<12} {n_pdfs:>5} {ts:<20}")


def main():
    parser = argparse.ArgumentParser(description="Extraction experiment harness")
    parser.add_argument(
        "config_name",
        nargs="?",
        help="Name for this experiment run",
    )
    parser.add_argument(
        "--backend",
        type=str,
        default="pymupdf4llm",
        choices=["pymupdf4llm", "docling", "gmft"],
        help="Extraction backend (default: pymupdf4llm)",
    )
    parser.add_argument(
        "--params",
        type=str,
        default=None,
        help=(
            'JSON dict of parameter overrides. '
            'pymupdf4llm: e.g. \'{"table_strategy": "lines_strict"}\'. '
            'docling: PdfPipelineOptions fields, e.g. \'{"do_ocr": true, "do_formula_enrichment": true}\'. '
            'gmft: TATRFormatConfig fields, e.g. \'{"enable_multi_header": true}\'.'
        ),
    )
    parser.add_argument(
        "--slugs",
        type=str,
        default=None,
        help="Comma-separated list of paper slugs to run (default: all)",
    )
    parser.add_argument(
        "--compare",
        type=str,
        default=None,
        help="Compare results against this run name",
    )
    parser.add_argument(
        "--hdr-info",
        type=str,
        default=None,
        choices=list(HDR_INFO_PRESETS.keys()),
        help=f"Named header detector preset (pymupdf4llm only): {list(HDR_INFO_PRESETS.keys())}",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Timeout in seconds per document for Docling backend (default: 600)",
    )
    parser.add_argument(
        "--page-range",
        type=str,
        default=None,
        help="Page range for Docling (1-indexed, inclusive), e.g. '5,5' for page 5 or '1,10' for pages 1-10",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all experiment runs",
    )

    args = parser.parse_args()

    if args.list:
        list_runs()
        return

    if not args.config_name:
        parser.error("config_name is required (or use --list)")

    backend = args.backend

    # Build params based on backend
    if backend == "pymupdf4llm":
        params = dict(BASELINE_PARAMS)
        if args.params:
            overrides = json.loads(args.params)
            params.update(overrides)
        # Apply named header detector
        if args.hdr_info is not None:
            params["hdr_info"] = HDR_INFO_PRESETS[args.hdr_info]
    elif backend == "docling":
        # Docling params are PdfPipelineOptions fields
        params = {}
        if args.params:
            params = json.loads(args.params)
        # Apply page range if specified
        if args.page_range:
            start, end = args.page_range.split(",")
            params["page_range"] = [int(start), int(end)]
    elif backend == "gmft":
        # GMFT params are TATRFormatConfig / TATRDetectorConfig fields
        params = {}
        if args.params:
            params = json.loads(args.params)
    else:
        parser.error(f"Unknown backend: {backend}")

    slugs = args.slugs.split(",") if args.slugs else None

    run_experiment(args.config_name, params, slugs, backend=backend, timeout=args.timeout)

    if args.compare:
        print_comparison(args.config_name, args.compare)


if __name__ == "__main__":
    main()
