#!/usr/bin/env python3
"""Claude headless extraction experiment harness.

Renders PDF pages to images, sends them to `claude -p` for markdown extraction,
computes metrics, and saves results for comparison against library-based extractors.

Usage:
    # Run pure vision baseline (1 page per call, 4-paper subset)
    python tests/corpus/claude_extract_experiment.py claude_vision_1pp

    # Run with 5 pages per call
    python tests/corpus/claude_extract_experiment.py claude_vision_5pp --pages-per-call 5

    # Run with supplemental pymupdf4llm text
    python tests/corpus/claude_extract_experiment.py claude_pymupdf_1pp --supplemental-text

    # Run specific papers only
    python tests/corpus/claude_extract_experiment.py test_run --slugs hsu_2020

    # Compare against pymupdf4llm best_v1
    python tests/corpus/claude_extract_experiment.py claude_vision_1pp --compare best_v1

    # List existing runs
    python tests/corpus/claude_extract_experiment.py --list
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Ensure imports work when run directly
sys.path.insert(0, str(Path(__file__).parent))

import pymupdf4llm  # type: ignore[import-untyped]

from metrics import ExtractionMetrics, compare_metrics, compute_metrics

CORPUS_DIR = Path(__file__).parent
REPO_ROOT = CORPUS_DIR.parent.parent
PAPERS_JSONL = CORPUS_DIR / "papers.jsonl"
RUNS_DIR = CORPUS_DIR / "runs"
PAGE_IMAGES_DIR = CORPUS_DIR / "page_images"
PROMPTS_DIR = CORPUS_DIR / "prompts"
DEFAULT_PROMPT = PROMPTS_DIR / "extract_baseline.txt"

# Default 4-paper subset (chosen for specific gap coverage)
DEFAULT_SLUGS = ["hawker_2020", "hsu_2020", "hansen_2025", "paischer_2025"]


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


def get_page_images(slug: str) -> list[Path]:
    """Get sorted list of pre-rendered page images for a paper."""
    img_dir = PAGE_IMAGES_DIR / slug
    if not img_dir.exists():
        return []
    return sorted(img_dir.glob("page_*.png"))


def build_prompt(
    image_paths: list[Path],
    prompt_text: str,
    supplemental_text: str | None = None,
) -> str:
    """Build the full prompt for claude -p.

    Images are referenced by absolute path so Claude's Read tool can load them.
    """
    parts = []

    # Supplemental text context (if provided)
    if supplemental_text:
        parts.append(
            "Here is the text extracted by a library-based tool for reference. "
            "Use it to cross-check your extraction, but trust the page images "
            "as the primary source:\n\n"
            "---BEGIN LIBRARY TEXT---\n"
            f"{supplemental_text}\n"
            "---END LIBRARY TEXT---\n"
        )

    # Image references
    if len(image_paths) == 1:
        parts.append(
            f"Read the image file at {image_paths[0].resolve()} and extract its content.\n"
        )
    else:
        parts.append(
            "Read each of the following page images in order and extract their content "
            "as a single continuous document:\n"
        )
        for i, p in enumerate(image_paths):
            parts.append(f"  Page {i + 1}: {p.resolve()}")
        parts.append("")

    # Extraction instructions
    parts.append(prompt_text)

    return "\n".join(parts)


def invoke_claude(
    prompt: str,
    model: str = "sonnet",
    timeout: int = 300,
) -> dict:
    """Invoke claude -p with a prompt piped via stdin.

    Returns parsed JSON response with keys: result, total_cost_usd, usage, duration_ms, etc.
    Raises RuntimeError on failure or timeout.
    """
    # Must unset CLAUDECODE to avoid nested session guard
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    cmd = [
        "claude", "-p",
        "--model", model,
        "--output-format", "json",
        "--dangerously-skip-permissions",
        "--no-session-persistence",
        "--allowedTools", "Read",
    ]

    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"claude -p timed out after {timeout}s")

    if result.returncode != 0:
        stderr = result.stderr[:500] if result.stderr else "(no stderr)"
        raise RuntimeError(f"claude -p failed (rc={result.returncode}): {stderr}")

    # Parse JSON response
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"claude -p returned non-JSON output: {result.stdout[:300]}"
        )

    return data


def extract_markdown_from_response(response: dict) -> str:
    """Extract the markdown text from a claude -p JSON response."""
    # The 'result' field contains the text output
    text = response.get("result", "")
    if not text:
        raise RuntimeError("claude -p returned empty result")
    return text


def extract_cost_from_response(response: dict, wall_clock_seconds: float) -> dict:
    """Extract cost/token data from a claude -p JSON response.

    Note: usage.input_tokens only reports direct prompt tokens, not image tokens
    consumed via the Read tool. total_cost_usd reflects the true cost including
    tool-use image token consumption.
    """
    usage = response.get("usage", {})
    cost = {
        "total_cost_usd": response.get("total_cost_usd", 0),
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "duration_ms": response.get("duration_ms", 0),
        "wall_clock_seconds": wall_clock_seconds,
        "model": response.get("model", "unknown"),
    }
    # Capture per-model cost breakdown if available
    model_usage = response.get("modelUsage")
    if model_usage:
        cost["model_usage"] = model_usage
    return cost


def get_pdf_path(slug: str) -> Path | None:
    """Resolve the PDF path for a paper from the registry."""
    papers = load_papers([slug])
    if not papers:
        return None
    pdf_path = REPO_ROOT / papers[0]["pdf_path"]
    if pdf_path.exists():
        return pdf_path
    # Fallback to pdfs/ directory
    pdf_path = CORPUS_DIR / "pdfs" / f"{slug}.pdf"
    return pdf_path if pdf_path.exists() else None


def extract_page_text(slug: str, page_nums: list[int]) -> str | None:
    """Extract pymupdf4llm text for specific pages of a paper.

    Args:
        slug: Paper slug.
        page_nums: 0-indexed page numbers to extract.

    Returns:
        Extracted markdown text for the specified pages, or None if PDF not found.
    """
    pdf_path = get_pdf_path(slug)
    if pdf_path is None:
        return None
    return pymupdf4llm.to_markdown(str(pdf_path), pages=page_nums)


def _page_num_from_image(image_path: Path) -> int:
    """Extract 0-indexed page number from an image filename like page_003.png."""
    return int(image_path.stem.split("_")[1])


def run_paper(
    slug: str,
    pages_per_call: int,
    prompt_text: str,
    model: str,
    timeout: int,
    supplemental_text_mode: bool,
    dpi: int,
    page_filter: list[int] | None = None,
) -> tuple[str, float, dict]:
    """Extract a single paper via Claude headless.

    Args:
        page_filter: If set, only process these 0-indexed page numbers.

    Returns (markdown, wall_clock_seconds, aggregated_cost).
    """
    images = get_page_images(slug)
    if not images:
        raise RuntimeError(
            f"No page images found for {slug}. "
            f"Run tests/corpus/scripts/render_pages.sh first."
        )

    # Filter to specific pages if requested
    if page_filter is not None:
        images = [img for img in images if _page_num_from_image(img) in page_filter]
        if not images:
            raise RuntimeError(
                f"No page images match --pages filter for {slug}. "
                f"Available pages: {[_page_num_from_image(p) for p in get_page_images(slug)]}"
            )

    # Batch images by pages_per_call
    batches = []
    for i in range(0, len(images), pages_per_call):
        batches.append(images[i : i + pages_per_call])

    all_markdown = []
    total_wall_clock = 0.0
    total_cost = {
        "total_cost_usd": 0.0,
        "input_tokens": 0,
        "output_tokens": 0,
        "duration_ms": 0,
        "calls": 0,
        "pages": len(images),
        "pages_per_call": pages_per_call,
        "model": model,
    }

    for batch_idx, batch in enumerate(batches):
        page_range = f"{batch[0].stem}..{batch[-1].stem}" if len(batch) > 1 else batch[0].stem
        print(f"    batch {batch_idx + 1}/{len(batches)} ({page_range})... ", end="", flush=True)

        # Extract per-batch supplemental text if requested
        supp_text = None
        if supplemental_text_mode:
            batch_page_nums = [_page_num_from_image(img) for img in batch]
            supp_text = extract_page_text(slug, batch_page_nums)
            if supp_text is None:
                if batch_idx == 0:
                    print("WARN: PDF not found, running without supplemental text... ", end="")

        prompt = build_prompt(batch, prompt_text, supp_text)

        start = time.time()
        response = invoke_claude(prompt, model=model, timeout=timeout)
        elapsed = time.time() - start

        md = extract_markdown_from_response(response)
        cost = extract_cost_from_response(response, elapsed)

        all_markdown.append(md)
        total_wall_clock += elapsed
        total_cost["total_cost_usd"] += cost["total_cost_usd"]
        total_cost["input_tokens"] += cost["input_tokens"]
        total_cost["output_tokens"] += cost["output_tokens"]
        total_cost["duration_ms"] += cost["duration_ms"]
        total_cost["calls"] += 1

        print(
            f"{elapsed:.1f}s | "
            f"in={cost['input_tokens']:,} out={cost['output_tokens']:,} "
            f"${cost['total_cost_usd']:.3f}"
        )

    total_cost["wall_clock_seconds"] = total_wall_clock

    # Concatenate all batches
    full_markdown = "\n\n".join(all_markdown)
    return full_markdown, total_wall_clock, total_cost


def run_experiment(
    config_name: str,
    slugs: list[str],
    pages_per_call: int,
    prompt_file: Path,
    model: str,
    timeout: int,
    supplemental_text: bool,
    dpi: int,
    page_filter: list[int] | None = None,
) -> Path:
    """Run the full experiment across all specified papers."""
    papers = load_papers(slugs)
    if not papers:
        print(f"ERROR: No papers found matching slugs: {slugs}")
        sys.exit(1)

    prompt_text = prompt_file.read_text().strip()

    run_dir = RUNS_DIR / config_name
    run_dir.mkdir(parents=True, exist_ok=True)

    # Save config
    config_record = {
        "config_name": config_name,
        "backend": "claude",
        "model": model,
        "pages_per_call": pages_per_call,
        "prompt_file": str(prompt_file),
        "supplemental_text": supplemental_text,
        "dpi": dpi,
        "timeout": timeout,
        "slugs": [p["slug"] for p in papers],
        "page_filter": page_filter,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    (run_dir / "config.json").write_text(json.dumps(config_record, indent=2) + "\n")

    pages_desc = f", pages {page_filter}" if page_filter else ""
    print(f"Running config '{config_name}' (claude/{model}, {pages_per_call}pp) on {len(papers)} papers{pages_desc}...")
    print(f"Prompt: {prompt_file.name}")
    if supplemental_text:
        print("Mode: vision + supplemental pymupdf4llm text (per-page)")
    print()

    total_experiment_cost = 0.0

    for paper in papers:
        slug = paper["slug"]
        n_pages = paper.get("pages", "?")
        print(f"  {slug} ({n_pages}pp):")

        try:
            md, elapsed, cost = run_paper(
                slug=slug,
                pages_per_call=pages_per_call,
                prompt_text=prompt_text,
                model=model,
                timeout=timeout,
                supplemental_text_mode=supplemental_text,
                dpi=dpi,
                page_filter=page_filter,
            )

            metrics = compute_metrics(md, elapsed)

            # Save results
            slug_dir = run_dir / slug
            slug_dir.mkdir(exist_ok=True)
            (slug_dir / "output.md").write_text(md)
            (slug_dir / "metrics.json").write_text(
                json.dumps(metrics.to_dict(), indent=2) + "\n"
            )
            (slug_dir / "cost.json").write_text(
                json.dumps(cost, indent=2) + "\n"
            )

            total_experiment_cost += cost["total_cost_usd"]

            print(
                f"    TOTAL: {elapsed:.1f}s | "
                f"chars={metrics.char_count:,} "
                f"hdrs={metrics.heading_count} "
                f"tables={metrics.table_row_count} "
                f"math={metrics.math_symbol_count} | "
                f"${cost['total_cost_usd']:.3f}"
            )

        except Exception as e:
            print(f"    ERROR: {e}")

        print()

    print(f"Results saved to {run_dir}/")
    print(f"Total experiment cost: ${total_experiment_cost:.3f}")
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

    print(f"\n{'=' * 90}")
    print(f"Comparison: {compare_to} → {config_name}")
    print(f"{'=' * 90}")
    print(
        f"{'Document':<22} {'Chars':>12} {'Headings':>12} {'Tables':>12} "
        f"{'Math':>12} {'Cost':>8}"
    )
    print("-" * 82)

    for paper in papers:
        slug = paper["slug"]
        base_path = compare_dir / slug / "metrics.json"
        curr_path = run_dir / slug / "metrics.json"

        if not base_path.exists() or not curr_path.exists():
            continue

        base = ExtractionMetrics.from_dict(json.loads(base_path.read_text()))
        curr = ExtractionMetrics.from_dict(json.loads(curr_path.read_text()))
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
            return f"({d // 1000:+d}k {pct:+.1f}%)"

        # Cost column (if available)
        cost_path = run_dir / slug / "cost.json"
        cost_str = ""
        if cost_path.exists():
            cost_data = json.loads(cost_path.read_text())
            cost_str = f"${cost_data.get('total_cost_usd', 0):.2f}"

        flag = " !!!" if delta["has_regression"] else ""
        print(
            f"{slug:<22} {fmt_chars():>12} {fmt_delta('heading_count'):>12} "
            f"{fmt_delta('table_row_count'):>12} {fmt_delta('math_symbol_count'):>12} "
            f"{cost_str:>8}{flag}"
        )


def list_runs() -> None:
    """List all experiment runs (reuse from experiment.py)."""
    if not RUNS_DIR.exists():
        print("No experiment runs yet.")
        return

    print(f"{'Config':<30} {'Backend':<12} {'PDFs':>5} {'Timestamp':<20}")
    print("-" * 72)

    for run_dir in sorted(RUNS_DIR.iterdir()):
        if not run_dir.is_dir():
            continue
        config_path = run_dir / "config.json"
        if config_path.exists():
            config = json.loads(config_path.read_text())
            n_pdfs = len(config.get("slugs", []))
            ts = config.get("timestamp", "?")
            be = config.get("backend", "?")
            if be == "claude":
                be = f"claude/{config.get('model', '?')}"
        else:
            n_pdfs = sum(1 for d in run_dir.iterdir() if d.is_dir())
            ts = "?"
            be = "?"
        print(f"{run_dir.name:<30} {be:<12} {n_pdfs:>5} {ts:<20}")


def main():
    parser = argparse.ArgumentParser(
        description="Claude headless extraction experiment harness"
    )
    parser.add_argument(
        "config_name",
        nargs="?",
        help="Name for this experiment run (e.g. claude_vision_1pp)",
    )
    parser.add_argument(
        "--slugs",
        type=str,
        default=None,
        help=f"Comma-separated paper slugs (default: {','.join(DEFAULT_SLUGS)})",
    )
    parser.add_argument(
        "--pages-per-call",
        type=int,
        default=1,
        help="Pages sent in one claude -p invocation (default: 1)",
    )
    parser.add_argument(
        "--prompt-file",
        type=str,
        default=str(DEFAULT_PROMPT),
        help=f"Path to extraction prompt (default: {DEFAULT_PROMPT.name})",
    )
    parser.add_argument(
        "--supplemental-text",
        action="store_true",
        help="Provide pymupdf4llm text alongside images (extracted per-page on-the-fly)",
    )
    parser.add_argument(
        "--pages",
        type=str,
        default=None,
        help="Comma-separated 0-indexed page numbers to process (e.g., '3,5,7')",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="Image render DPI (default: 200, must match pre-rendered images)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="sonnet",
        help="Claude model to use (default: sonnet)",
    )
    parser.add_argument(
        "--compare",
        type=str,
        default=None,
        help="Compare results against this run name",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Seconds per claude -p call (default: 300)",
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

    slugs = args.slugs.split(",") if args.slugs else DEFAULT_SLUGS
    prompt_file = Path(args.prompt_file)
    if not prompt_file.exists():
        print(f"ERROR: Prompt file not found: {prompt_file}")
        sys.exit(1)

    page_filter = None
    if args.pages:
        page_filter = [int(p.strip()) for p in args.pages.split(",")]

    run_experiment(
        config_name=args.config_name,
        slugs=slugs,
        pages_per_call=args.pages_per_call,
        prompt_file=prompt_file,
        model=args.model,
        timeout=args.timeout,
        supplemental_text=args.supplemental_text,
        dpi=args.dpi,
        page_filter=page_filter,
    )

    if args.compare:
        print_comparison(args.config_name, args.compare)


if __name__ == "__main__":
    main()
