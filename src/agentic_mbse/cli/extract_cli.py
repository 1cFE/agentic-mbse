"""CLI subcommand for document extraction (PDF / DOCX → structured markdown)."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_mbse.extraction.profile import ProfileEntry

from agentic_mbse.extraction.base import (
    ExtractionResult,
    check_processing_needed,
    get_output_dir,
    write_summary,
)
from agentic_mbse.extraction.pipeline import PipelineConfig, extract_pdf
from agentic_mbse.extraction.types import CostRecord, PageDecision, PipelineResult
from agentic_mbse.validation import EXIT_FAILURE, EXIT_SUCCESS

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


# ---------------------------------------------------------------------------
# Availability helpers
# ---------------------------------------------------------------------------


def _is_available(backend: str) -> bool:
    """Check whether *backend* is usable in the current environment."""
    if backend == "pymupdf":
        try:
            import pymupdf4llm  # type: ignore[import-untyped]  # noqa: F401

            return True
        except ImportError:
            return False
    if backend == "docling":
        try:
            import docling  # type: ignore[import-untyped]  # noqa: F401

            return True
        except ImportError:
            return False
    if backend == "pandoc":
        return shutil.which("pandoc") is not None
    return False


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def discover_documents(path: Path) -> list[Path]:
    """Find all PDF/DOCX files at *path*.

    If *path* is a file, validate its extension and return a one-element
    list.  If *path* is a directory, do a flat (non-recursive) listing and
    return matching files sorted by name.  Returns an empty list when
    *path* does not exist or has an unsupported extension.
    """
    if not path.exists():
        return []

    if path.is_file():
        if path.suffix.lower() in SUPPORTED_EXTENSIONS:
            return [path]
        return []

    # Directory — flat listing, sorted
    return sorted(
        f for f in path.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def select_backend(file_path: Path, requested: str | None) -> str | None:
    """Select the extraction backend for *file_path* (DOCX only).

    If *requested* is given, return it directly (caller is responsible for
    checking availability).  In auto mode for DOCX, prefer docling then
    pandoc.  Returns ``None`` for PDFs (pipeline handles them) and when
    no suitable backend is available.
    """
    if requested is not None:
        return requested

    ext = file_path.suffix.lower()

    # PDFs always use the pipeline (extract_pdf) — no backend auto-selection
    if ext == ".docx":
        candidates = ["docling", "pandoc"]
    else:
        return None

    for name in candidates:
        if _is_available(name):
            return name
    return None


# ---------------------------------------------------------------------------
# Extraction dispatch (DOCX only)
# ---------------------------------------------------------------------------

_FALLBACK_ORDER: dict[str, list[str]] = {
    ".docx": ["docling", "pandoc"],
}


def _run_extraction(
    file_path: Path,
    output_dir: Path,
    backend: str,
    timeout: int,
) -> ExtractionResult:
    """Run the appropriate extraction backend."""
    if backend == "pymupdf":
        from agentic_mbse.extraction.pymupdf_backend import extract

        return extract(file_path, output_dir)

    if backend == "docling":
        from agentic_mbse.extraction.docling_backend import extract

        return extract(file_path, output_dir, timeout=timeout)

    if backend == "pandoc":
        from agentic_mbse.extraction.pandoc_backend import extract

        return extract(file_path, output_dir, timeout=timeout)

    return ExtractionResult(
        success=False,
        output_dir=output_dir,
        error=f"Unknown backend: {backend}",
    )


# ---------------------------------------------------------------------------
# Pipeline serialization helpers
# ---------------------------------------------------------------------------


def _decision_to_dict(d: PageDecision) -> dict:
    return {
        "page_num": d.page_num,
        "action": d.action.value,
        "reasons": d.reasons,
        "details": d.details,
    }


def _cost_to_dict(c: CostRecord) -> dict:
    return {
        "page_num": c.page_num,
        "cost_usd": c.cost_usd,
        "input_tokens": c.input_tokens,
        "output_tokens": c.output_tokens,
        "model": c.model,
        "elapsed_seconds": c.elapsed_seconds,
        "table_index": c.table_index,
    }


def _print_pipeline_summary(label: str, result: PipelineResult) -> None:
    stats = [f"{result.metrics.char_count:,} chars"]
    if result.metrics.heading_count:
        stats.append(f"{result.metrics.heading_count} headings")
    if result.metrics.table_row_count:
        stats.append(f"{result.metrics.table_row_count} table rows")
    if result.total_cost_usd > 0:
        stats.append(f"${result.total_cost_usd:.3f}")
    stats.append(f"{result.elapsed_seconds:.1f}s")
    print(f"   ok   {label} [{result.source}] ({', '.join(stats)})")
    if (
        result.claude_pages_intended > 0
        and result.claude_pages_succeeded < result.claude_pages_intended
    ):
        print(
            f"        ! Claude: {result.claude_pages_succeeded}/"
            f"{result.claude_pages_intended} pages enhanced"
        )


# ---------------------------------------------------------------------------
# URL dispatch helpers
# ---------------------------------------------------------------------------


def _extract_url(url: str, args: argparse.Namespace) -> int:
    """Handle a single URL extraction."""
    from agentic_mbse.extraction.web_backend import (
        check_web_deps,
        classify_url,
        extract_web_content,
    )

    # Check dependencies early
    try:
        check_web_deps()
    except ImportError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_FAILURE

    # Classify URL content type
    url_type = classify_url(url)

    if url_type == "pdf":
        # Download PDF to temp file, run through PDF pipeline
        return _extract_pdf_url(url, args)

    if url_type not in ("html",):
        print(f"Error: unsupported content type '{url_type}' for {url}")
        return EXIT_FAILURE

    output_base = Path(args.output) if getattr(args, "output", None) else None
    result = extract_web_content(
        url,
        output_dir=output_base,
        sanitize=not getattr(args, "no_sanitize", False),
        save_source=getattr(args, "save_source", False),
        no_frontmatter=getattr(args, "no_frontmatter", False),
        timeout=args.timeout,
    )

    if result.success:
        stats = []
        if result.char_count:
            stats.append(f"{result.char_count:,} chars")
        stats.append(f"backend: {result.backend_used}")
        print(f"   ok   {url} ({', '.join(stats)})")
        if result.markdown_path:
            print(f"        → {result.markdown_path}")
        return EXIT_SUCCESS
    else:
        print(f"  FAIL  {url}: {result.error}")
        return EXIT_FAILURE


def _extract_pdf_url(url: str, args: argparse.Namespace) -> int:
    """Download a PDF from URL and extract via the PDF pipeline."""
    import copy
    import tempfile

    from agentic_mbse.extraction.http import fetch_url

    print(f"  fetch {url} (PDF detected)")
    try:
        fetched = fetch_url(url, timeout=args.timeout)
    except Exception as exc:
        print(f"  FAIL  Download failed: {exc}")
        return EXIT_FAILURE

    # Write to temp file, then extract as normal PDF
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(fetched.content)
        tmp_pdf = Path(f.name)

    try:
        # Shallow-copy args to avoid corrupting shared state in batch mode
        pdf_args = copy.copy(args)
        pdf_args.path = str(tmp_pdf)
        pdf_args.source_url_override = fetched.final_url
        rc = cmd_extract(pdf_args)

        # Save raw PDF if requested
        if getattr(args, "save_source", False) and rc == EXIT_SUCCESS:
            output_base = Path(pdf_args.output) if getattr(pdf_args, "output", None) else None
            output_dir = get_output_dir(tmp_pdf, output_base=output_base)
            if output_dir.exists():
                shutil.copy2(tmp_pdf, output_dir / "raw.pdf")

        return rc
    finally:
        tmp_pdf.unlink(missing_ok=True)


def _extract_urls_from_file(args: argparse.Namespace) -> int:
    """Process URLs from a text file (one per line)."""
    urls_file = Path(args.urls_from)
    if not urls_file.exists():
        print(f"Error: URLs file not found: {urls_file}")
        return EXIT_FAILURE

    urls = [
        line.strip()
        for line in urls_file.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    if not urls:
        print(f"Error: no URLs found in {urls_file}")
        return EXIT_FAILURE

    print(f"Processing {len(urls)} URLs from {urls_file}")
    ok = 0
    fail = 0
    for url in urls:
        rc = _extract_url(url, args)
        if rc == EXIT_SUCCESS:
            ok += 1
        else:
            fail += 1

    print(f"\nProcessed: {ok}, Failed: {fail}")
    return EXIT_FAILURE if fail > 0 else EXIT_SUCCESS


# ---------------------------------------------------------------------------
# Main command handler
# ---------------------------------------------------------------------------


def cmd_extract(args: argparse.Namespace) -> int:
    """Main ``extract`` command handler."""
    # Deprecation warnings for legacy flags
    if getattr(args, "fix_tables", False):
        warnings.warn(
            "--fix-tables is deprecated. PDFs now use the quality-gated pipeline. "
            "Use --no-tables to disable table detection.",
            DeprecationWarning,
            stacklevel=2,
        )
    if getattr(args, "enhance", False):
        warnings.warn(
            "--enhance is deprecated. PDFs now use the quality-gated pipeline. "
            "Use --budget to control Claude spending.",
            DeprecationWarning,
            stacklevel=2,
        )
    if getattr(args, "structure_only", False):
        warnings.warn(
            "--structure-only is deprecated. PDFs now use the quality-gated pipeline. "
            "Use --dry-run to preview quality gate decisions.",
            DeprecationWarning,
            stacklevel=2,
        )
    if getattr(args, "raw_html", False):
        warnings.warn(
            "--raw-html is deprecated. Use --save-source instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        args.save_source = True

    # --check-json implies --check
    if args.check_json:
        args.check = True

    # Handle --check with no path: use built-in corpus
    if args.check and args.path is None:
        from agentic_mbse.extraction.check import (
            OverallStatus,
            format_check_json,
            get_check_corpus,
            merge_check_results,
            print_check_table,
            run_check,
        )

        corpus = get_check_corpus()
        if not corpus:
            print("Error: built-in test corpus not found", file=sys.stderr)
            return EXIT_FAILURE

        print(
            f"Using built-in test corpus ({len(corpus)} PDFs)",
            file=sys.stderr,
        )

        results = []
        for i, pdf in enumerate(corpus):
            # Only spend Claude budget on first PDF
            budget = args.budget if i == 0 else 0
            results.append(run_check(pdf, claude_model=args.model, claude_budget=budget))

        check_result = merge_check_results(results)

        if args.check_json:
            print(format_check_json(check_result))
        else:
            print_check_table(check_result)

        if check_result.overall == OverallStatus.FAIL:
            return 2
        elif check_result.overall == OverallStatus.DEGRADED:
            return EXIT_FAILURE
        return EXIT_SUCCESS

    # ---- URL and batch-URL dispatch ----

    # Batch URL mode
    if getattr(args, "urls_from", None):
        return _extract_urls_from_file(args)

    # Single URL mode
    if args.path and args.path.startswith(("http://", "https://")):
        return _extract_url(args.path, args)

    # ---- Existing file-based path (unchanged) ----

    # All non-check paths require a path argument
    if args.path is None:
        print("Error: path is required (unless using --check)")
        return EXIT_FAILURE

    path = Path(args.path)
    if not path.exists():
        print(f"Error: path does not exist: {path}")
        return EXIT_FAILURE

    docs = discover_documents(path)
    if not docs:
        print(f"Error: no PDF or DOCX files found at {path}")
        return EXIT_FAILURE

    if args.check:
        from agentic_mbse.extraction.check import (
            OverallStatus,
            format_check_json,
            print_check_table,
            run_check,
        )

        if len(docs) > 1:
            print(f"Error: --check operates on a single PDF, got {len(docs)} files")
            print("       Provide a single PDF file path, not a directory")
            return EXIT_FAILURE

        pdf = docs[0]
        if pdf.suffix.lower() != ".pdf":
            print("Error: --check only works with PDF files")
            return EXIT_FAILURE

        check_result = run_check(
            pdf,
            claude_model=args.model,
            claude_budget=args.budget,
        )

        if args.check_json:
            print(format_check_json(check_result))
        else:
            print_check_table(check_result)

        if check_result.overall == OverallStatus.FAIL:
            return 2
        elif check_result.overall == OverallStatus.DEGRADED:
            return EXIT_FAILURE
        return EXIT_SUCCESS

    output_base = Path(args.output) if args.output else None

    processed = 0
    skipped = 0
    failed = 0
    profile_entries: list[ProfileEntry] = []

    for doc in docs:
        output_dir = get_output_dir(doc, output_base=output_base)
        label = doc.name

        # ----- PDF: use pipeline -----
        if doc.suffix.lower() == ".pdf":
            # Skip check: output.md exists and not forced
            if not args.force and (output_dir / "output.md").exists():
                print(f"  skip  {label} (already processed, use --force to redo)")
                skipped += 1
                continue

            # Create output + images dirs early (pymupdf needs images dir
            # to exist before write_images=True)
            output_dir.mkdir(parents=True, exist_ok=True)
            images_dir = output_dir / "images"
            images_dir.mkdir(exist_ok=True)

            config = PipelineConfig(
                claude_budget_usd=args.budget,
                claude_model=args.model,
                enable_tables=not args.no_tables,
                enable_img2table=not args.no_img2table,
                enable_docling=args.docling,
                enable_equations=not args.no_equations,
                arxiv_html_path=Path(args.html_path) if args.html_path else None,
                dry_run=args.dry_run,
                extracted_images_dir=images_dir,
                profile=args.profile,
                save_source=getattr(args, "save_source", False),
            )
            result = extract_pdf(doc, config=config)

            if result.error:
                print(f"  FAIL  {label}: {result.error}")
                failed += 1
                continue

            # Build frontmatter for output
            markdown = result.markdown
            if not getattr(args, "no_frontmatter", False):
                from agentic_mbse.extraction.frontmatter import (
                    build_frontmatter,
                    compute_source_hash,
                )

                source_url = getattr(args, "source_url_override", None) or result.source_url
                if result.content_hash:
                    content_hash = result.content_hash
                else:
                    content_hash = compute_source_hash(doc)

                fm = build_frontmatter(
                    source=source_url or doc.name,
                    source_type="url" if source_url else "local_file",
                    backend=result.source,
                    content_hash=content_hash,
                )
                markdown = f"{fm}\n\n{markdown}"

            # Write output artifacts (output_dir already created above)
            (output_dir / "output.md").write_text(markdown)
            (output_dir / "metrics.json").write_text(json.dumps(result.metrics.to_dict(), indent=2))
            (output_dir / "decisions.json").write_text(
                json.dumps([_decision_to_dict(d) for d in result.decisions], indent=2)
            )
            if result.cost:
                (output_dir / "cost.json").write_text(
                    json.dumps([_cost_to_dict(c) for c in result.cost], indent=2)
                )

            # Save raw source if requested (arXiv shortcut populates raw_source_bytes)
            if getattr(args, "save_source", False) and result.raw_source_bytes:
                (output_dir / "raw.html").write_bytes(result.raw_source_bytes)

            if args.profile and result.profile:
                from agentic_mbse.extraction.profile import ProfileEntry, profile_to_dict

                profile_data = profile_to_dict(
                    result.profile,
                    result.decisions,
                    page_count=len(result.decisions),
                    elapsed_seconds=result.elapsed_seconds,
                )
                (output_dir / "profile.json").write_text(json.dumps(profile_data, indent=2))
                profile_entries.append(
                    ProfileEntry(
                        document=doc.stem,
                        pages=len(result.decisions),
                        route_dist=profile_data["route_distribution"],
                        elapsed=result.elapsed_seconds,
                        profile=result.profile,
                    )
                )

            _print_pipeline_summary(label, result)
            processed += 1

            # Index generation
            if args.index:
                md_path = output_dir / "output.md"
                if md_path.exists():
                    from agentic_mbse.extraction.index import generate_index

                    idx = generate_index(md_path, summarize=args.summarize, force=args.force)
                    if idx:
                        print(f"        index → {idx.name}")

            continue

        # ----- DOCX: existing backend path -----

        # Skip check (DOCX uses summary.json-based check)
        if not check_processing_needed(doc, output_dir, force=args.force):
            print(f"  skip  {label} (already processed, use --force to redo)")
            skipped += 1
            continue

        # Backend selection
        backend = select_backend(doc, requested=args.backend)
        if backend is None:
            print(f"  FAIL  {label}: no extraction backend available")
            print("        Install pymupdf4llm:  uv add agentic-mbse[extract]")
            print("        Install docling:       uv add agentic-mbse[extract-full]")
            failed += 1
            continue

        print(f"  run   {label} → {output_dir.name}/ (backend: {backend})")

        docx_result = _run_extraction(doc, output_dir, backend, timeout=args.timeout)

        # Fallback on failure
        if not docx_result.success and args.backend is None:
            ext = doc.suffix.lower()
            fallbacks = _FALLBACK_ORDER.get(ext, [])
            for fb in fallbacks:
                if fb == backend:
                    continue
                if not _is_available(fb):
                    continue
                print(f"        fallback → {fb}")
                docx_result = _run_extraction(doc, output_dir, fb, timeout=args.timeout)
                if docx_result.success:
                    break

        # Write summary
        write_summary(doc, output_dir, docx_result, docx_result.backend_used or backend)

        # Prepend frontmatter to DOCX output
        if (
            not getattr(args, "no_frontmatter", False)
            and docx_result.success
            and docx_result.markdown_path
        ):
            from agentic_mbse.extraction.frontmatter import build_frontmatter, compute_source_hash

            content_hash = compute_source_hash(doc)
            fm = build_frontmatter(
                source=doc.name,
                source_type="local_file",
                backend=docx_result.backend_used or backend,
                content_hash=content_hash,
            )
            existing = docx_result.markdown_path.read_text(encoding="utf-8")
            docx_result.markdown_path.write_text(f"{fm}\n\n{existing}", encoding="utf-8")

        if docx_result.success:
            stats = []
            if docx_result.char_count:
                stats.append(f"{docx_result.char_count:,} chars")
            if docx_result.image_count:
                stats.append(f"{docx_result.image_count} images")
            detail = f" ({', '.join(stats)})" if stats else ""
            print(f"   ok   {label}{detail}")
            processed += 1

            # Post-processing: index generation
            if args.index and docx_result.markdown_path:
                from agentic_mbse.extraction.index import generate_index

                idx = generate_index(
                    docx_result.markdown_path,
                    summarize=args.summarize,
                    force=args.force,
                )
                if idx:
                    print(f"        index → {idx.name}")
        else:
            print(f"  FAIL  {label}: {docx_result.error}")
            failed += 1

    # Profile summary table
    if args.profile and profile_entries:
        from agentic_mbse.extraction.profile import format_profile_table

        print(file=sys.stderr)
        print(format_profile_table(profile_entries), file=sys.stderr)

    # Summary line
    print()
    parts = [f"Processed: {processed}"]
    if skipped:
        parts.append(f"Skipped: {skipped}")
    if failed:
        parts.append(f"Failed: {failed}")
    print(", ".join(parts))

    return EXIT_FAILURE if failed > 0 else EXIT_SUCCESS


# ---------------------------------------------------------------------------
# Subcommand registration
# ---------------------------------------------------------------------------


def register_extract_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register the ``extract`` subcommand."""
    p = subparsers.add_parser(
        "extract",
        help="Extract PDF/DOCX/URL documents to structured markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Convert PDF, DOCX files, and URLs into structured markdown with "
            "images, metadata, and optional section indexes.\n\n"
            "URLs (http:// or https://) are auto-detected and routed by content type:\n"
            "  HTML → web extraction via trafilatura (requires agentic-mbse[web])\n"
            "  PDF  → downloaded and routed through the PDF pipeline"
        ),
        epilog=(
            "Claude Code agent note:\n"
            "  Commands that invoke Claude (--check, --budget > 0) write to\n"
            "  /dev/tty for status rendering, which can blank agent-captured\n"
            "  output. Workaround: redirect to a file and read it back:\n"
            "\n"
            "    uv run agentic-mbse extract --check f.pdf > /tmp/out.txt 2>&1\n"
            "    cat /tmp/out.txt"
        ),
    )
    p.add_argument(
        "path",
        nargs="?",
        default=None,
        help="PDF/DOCX file, directory, or URL to extract",
    )
    p.add_argument(
        "--output",
        "-o",
        default=None,
        metavar="DIR",
        help="Output base directory (default: alongside input file)",
    )
    p.add_argument(
        "--backend",
        choices=["docling", "pymupdf", "pandoc"],
        default=None,
        help="Force extraction backend (DOCX only; PDFs always use pipeline)",
    )
    p.add_argument(
        "--timeout",
        type=int,
        default=600,
        metavar="SECONDS",
        help="Timeout for DOCX backend in seconds (default: 600)",
    )
    p.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Reprocess even if already done",
    )
    p.add_argument(
        "--index",
        action="store_true",
        help="Generate INDEX.md after extraction",
    )
    p.add_argument(
        "--summarize",
        action="store_true",
        help="Include AI summaries in INDEX.md (requires --index)",
    )
    # Pipeline flags (PDF)
    p.add_argument(
        "--budget",
        type=float,
        default=2.0,
        metavar="USD",
        help="Claude budget in USD (default: 2.0, 0 = no Claude)",
    )
    p.add_argument(
        "--no-tables",
        action="store_true",
        help="Disable all table detection",
    )
    p.add_argument(
        "--no-img2table",
        action="store_true",
        help="Disable Img2Table second-pass table detection",
    )
    p.add_argument(
        "--no-equations",
        action="store_true",
        help="Disable equation region detection",
    )
    p.add_argument(
        "--docling",
        action="store_true",
        help="Enable Docling third-pass table detection",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show quality gate decisions without calling Claude",
    )
    p.add_argument(
        "--profile",
        action="store_true",
        help="Enable per-step timing and route distribution profiling",
    )
    p.add_argument(
        "--model",
        choices=["opus", "sonnet", "haiku"],
        default="sonnet",
        help="Claude model for enhancement (default: sonnet)",
    )
    p.add_argument(
        "--html-path",
        default=None,
        metavar="PATH",
        help="arXiv HTML file path for Pandoc shortcut (overrides auto-detect)",
    )
    # Web extraction flags
    p.add_argument(
        "--urls-from",
        default=None,
        metavar="FILE",
        help="Read URLs from FILE (one per line) for batch extraction",
    )
    p.add_argument(
        "--no-sanitize",
        action="store_true",
        help="Skip HTML sanitization pre-pass (web extraction only)",
    )
    p.add_argument(
        "--save-source",
        action="store_true",
        help="Save raw source artifacts for network-fetched content",
    )
    p.add_argument(
        "--no-frontmatter",
        action="store_true",
        help="Suppress YAML frontmatter in output markdown",
    )
    # Deprecated: use --save-source instead
    p.add_argument("--raw-html", action="store_true", default=False, help=argparse.SUPPRESS)
    # Check flags
    p.add_argument(
        "--check",
        action="store_true",
        help="Probe pipeline components against the PDF without extracting",
    )
    p.add_argument(
        "--check-json",
        action="store_true",
        dest="check_json",
        help="Output machine-readable JSON (implies --check)",
    )
    # Hidden legacy flags — emit deprecation warnings when used
    p.add_argument("--fix-tables", action="store_true", default=False, help=argparse.SUPPRESS)
    p.add_argument("--enhance", action="store_true", default=False, help=argparse.SUPPRESS)
    p.add_argument("--structure-only", action="store_true", default=False, help=argparse.SUPPRESS)
    p.set_defaults(func=cmd_extract)
