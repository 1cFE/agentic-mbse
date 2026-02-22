#!/usr/bin/env python3
"""Experiment harness for pymupdf4llm parameter exploration.

Runs pymupdf4llm.to_markdown() with a given parameter configuration against
all (or selected) corpus PDFs, computes metrics, and saves results.

Usage:
    # Run baseline config
    python tests/corpus/experiment.py baseline

    # Run a named config with parameter overrides
    python tests/corpus/experiment.py lines_strict --params '{"table_strategy": "lines_strict"}'

    # Run against specific PDFs only
    python tests/corpus/experiment.py test_config --slugs hawker_2020,hsu_2020

    # Compare against baseline
    python tests/corpus/experiment.py lines_strict --compare baseline

    # List all runs
    python tests/corpus/experiment.py --list
"""

import argparse
import json
import sys
import time
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


def run_experiment(config_name: str, params: dict, slugs: list[str] | None = None) -> Path:
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
        "params": safe_params,
        "slugs": [p["slug"] for p in papers],
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    (run_dir / "config.json").write_text(json.dumps(config_record, indent=2) + "\n")

    print(f"Running config '{config_name}' on {len(papers)} PDFs...")
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
            md, elapsed = run_extraction(pdf_path, params)
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

    print(f"{'Config':<25} {'PDFs':>5} {'Timestamp':<20}")
    print("-" * 55)

    for run_dir in sorted(RUNS_DIR.iterdir()):
        if not run_dir.is_dir():
            continue
        config_path = run_dir / "config.json"
        if config_path.exists():
            config = json.loads(config_path.read_text())
            n_pdfs = len(config.get("slugs", []))
            ts = config.get("timestamp", "?")
        else:
            n_pdfs = sum(1 for d in run_dir.iterdir() if d.is_dir())
            ts = "?"
        print(f"{run_dir.name:<25} {n_pdfs:>5} {ts:<20}")


def main():
    parser = argparse.ArgumentParser(description="pymupdf4llm experiment harness")
    parser.add_argument(
        "config_name",
        nargs="?",
        help="Name for this experiment run",
    )
    parser.add_argument(
        "--params",
        type=str,
        default=None,
        help='JSON dict of pymupdf4llm.to_markdown() parameter overrides (e.g. \'{"table_strategy": "lines_strict"}\')',
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
        help=f"Named header detector preset: {list(HDR_INFO_PRESETS.keys())}",
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

    # Build params: start with baseline, apply overrides
    params = dict(BASELINE_PARAMS)
    if args.params:
        overrides = json.loads(args.params)
        params.update(overrides)

    # Apply named header detector
    if args.hdr_info is not None:
        params["hdr_info"] = HDR_INFO_PRESETS[args.hdr_info]

    slugs = args.slugs.split(",") if args.slugs else None

    run_experiment(args.config_name, params, slugs)

    if args.compare:
        print_comparison(args.config_name, args.compare)


if __name__ == "__main__":
    main()
