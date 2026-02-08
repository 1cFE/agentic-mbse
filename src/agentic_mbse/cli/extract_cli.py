"""CLI subcommand for document extraction (PDF / DOCX → structured markdown)."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from agentic_mbse.extraction.base import (
    ExtractionResult,
    check_processing_needed,
    get_output_dir,
    write_summary,
)
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
    """Select the extraction backend for *file_path*.

    If *requested* is given, return it directly (caller is responsible for
    checking availability).  In auto mode, prefer docling, then fall back
    to pymupdf (PDF) or pandoc (DOCX).  Returns ``None`` when no suitable
    backend is available.
    """
    if requested is not None:
        return requested

    ext = file_path.suffix.lower()

    # Preference order per format
    if ext == ".pdf":
        candidates = ["docling", "pymupdf"]
    elif ext == ".docx":
        candidates = ["docling", "pandoc"]
    else:
        return None

    for name in candidates:
        if _is_available(name):
            return name
    return None


# ---------------------------------------------------------------------------
# Extraction dispatch
# ---------------------------------------------------------------------------

_FALLBACK_ORDER: dict[str, list[str]] = {
    ".pdf": ["docling", "pymupdf"],
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
# Main command handler
# ---------------------------------------------------------------------------


def cmd_extract(args: argparse.Namespace) -> int:
    """Main ``extract`` command handler."""
    path = Path(args.path)
    if not path.exists():
        print(f"Error: path does not exist: {path}")
        return EXIT_FAILURE

    docs = discover_documents(path)
    if not docs:
        print(f"Error: no PDF or DOCX files found at {path}")
        return EXIT_FAILURE

    output_base = Path(args.output) if args.output else None

    processed = 0
    skipped = 0
    failed = 0

    for doc in docs:
        output_dir = get_output_dir(doc, output_base=output_base)
        label = doc.name

        # Skip check
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

        result = _run_extraction(doc, output_dir, backend, timeout=args.timeout)

        # Fallback on failure
        if not result.success and args.backend is None:
            ext = doc.suffix.lower()
            fallbacks = _FALLBACK_ORDER.get(ext, [])
            for fb in fallbacks:
                if fb == backend:
                    continue
                if not _is_available(fb):
                    continue
                print(f"        fallback → {fb}")
                result = _run_extraction(doc, output_dir, fb, timeout=args.timeout)
                if result.success:
                    break

        # Write summary
        write_summary(doc, output_dir, result, result.backend_used or backend)

        if result.success:
            stats = []
            if result.char_count:
                stats.append(f"{result.char_count:,} chars")
            if result.image_count:
                stats.append(f"{result.image_count} images")
            detail = f" ({', '.join(stats)})" if stats else ""
            print(f"   ok   {label}{detail}")
            processed += 1

            # Post-processing: table repair (legacy --fix-tables)
            if args.fix_tables and result.markdown_path:
                from agentic_mbse.extraction.table_repair import repair_tables

                if repair_tables(result.markdown_path):
                    print("        tables repaired (legacy)")

            # Post-processing: Layer 2 + Layer 3 + Layer 4 pipeline
            no_tables = args.no_tables
            enhance = args.enhance
            structure_only = args.structure_only
            max_repair_pages = args.max_repair_pages
            run_structural = enhance or structure_only
            run_ai_repair = enhance and not structure_only
            model = args.model

            if result.markdown_path and result.markdown_path.exists():
                md_text = result.markdown_path.read_text()
                layer_metadata: dict = {}

                # Quality detection
                from agentic_mbse.extraction.quality_gates import detect_problems

                problems = detect_problems(md_text)

                # Layer 2: GMFT table extraction (unless --no-tables)
                remaining_problems = problems
                if not no_tables:
                    table_problems = [p for p in problems if p.region_type == "table"]
                    non_table_problems = [p for p in problems if p.region_type != "table"]
                    try:
                        from agentic_mbse.extraction.table_extraction import (
                            enhance_tables,
                        )

                        md_text, remaining_table = enhance_tables(md_text, doc, table_problems)
                        remaining_problems = remaining_table + non_table_problems
                        fixed_count = len(table_problems) - len(remaining_table)
                        if fixed_count > 0:
                            print(f"        tables enhanced: {fixed_count} (GMFT)")
                            layer_metadata["gmft_tables_fixed"] = fixed_count
                    except ImportError:
                        remaining_problems = problems

                # Layer 3: Claude structural pass (with --enhance or --structure-only)
                if run_structural:
                    from agentic_mbse.extraction.claude_structure import (
                        enhance_structure,
                        needs_claude_structure,
                    )

                    if needs_claude_structure(md_text):
                        phase_a_model = model or "haiku"
                        phase_b_model = model or "sonnet"
                        try:
                            md_text, struct_meta = enhance_structure(
                                md_text,
                                doc,
                                output_dir,
                                phase_a_model=phase_a_model,
                                phase_b_model=phase_b_model,
                            )
                            layer_metadata["structure"] = struct_meta
                            inserted = struct_meta.get("headers_inserted", 0)
                            skipped = struct_meta.get("headers_skipped", 0)
                            style_info = struct_meta.get("phase_a", {})
                            style_desc = (
                                f"{style_info.get('doc_type', '?')} "
                                f"({style_info.get('heading_convention', '?')})"
                            )
                            print(
                                f"        structure: {style_desc}, "
                                f"{inserted} headers inserted, "
                                f"{skipped} skipped"
                            )
                            for w in struct_meta.get("warnings", []):
                                print(f"        warning: {w}")
                        except Exception as exc:
                            print(f"        structure: FAILED ({exc}), continuing")
                    else:
                        print(
                            "        structure: skipped (document already well-structured)"
                        )

                # Layer 4: AI quality repair (only with --enhance, NOT --structure-only)
                if run_ai_repair and remaining_problems:
                    from agentic_mbse.extraction.ai_repair import repair_document

                    md_text, repair_meta = repair_document(
                        md_text,
                        doc,
                        remaining_problems,
                        max_pages=max_repair_pages,
                    )
                    layer_metadata["ai_repairs"] = repair_meta["repairs"]
                    layer_metadata["ai_rejections"] = repair_meta["rejections"]
                    if repair_meta["repairs"] > 0:
                        print(f"        AI repaired: {repair_meta['repairs']} regions")
                    if repair_meta["rejections"] > 0:
                        print(
                            f"        AI rejected: {repair_meta['rejections']} (cross-validation)"
                        )

                # Write back if any layer modified the text
                if layer_metadata:
                    result.markdown_path.write_text(md_text)

                # Report detected problems
                if problems and not layer_metadata:
                    print(f"        {len(problems)} issues detected (use --enhance)")

            # Post-processing: index generation
            if args.index and result.markdown_path:
                from agentic_mbse.extraction.index import generate_index

                idx = generate_index(
                    result.markdown_path,
                    summarize=args.summarize,
                    force=args.force,
                )
                if idx:
                    print(f"        index → {idx.name}")
        else:
            print(f"  FAIL  {label}: {result.error}")
            failed += 1

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
        help="Extract PDF/DOCX documents to structured markdown",
        description=(
            "Convert PDF and DOCX files into structured markdown with "
            "images, metadata, and optional section indexes."
        ),
    )
    p.add_argument(
        "path",
        help="PDF/DOCX file or directory containing documents",
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
        help="Force extraction backend (default: auto-detect)",
    )
    p.add_argument(
        "--timeout",
        type=int,
        default=600,
        metavar="SECONDS",
        help="Timeout for primary extractor in seconds (default: 600)",
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
    p.add_argument(
        "--fix-tables",
        action="store_true",
        help="Run two-pass table repair via Claude headless mode (legacy)",
    )
    p.add_argument(
        "--enhance",
        action="store_true",
        help="Enable AI enhancement: structural repair (Layer 3) + quality repair (Layer 4)",
    )
    p.add_argument(
        "--no-tables",
        action="store_true",
        help="Skip GMFT table extraction (Layer 2)",
    )
    p.add_argument(
        "--structure-only",
        action="store_true",
        help="Run structural repair only (Layer 3), skip AI quality repair (Layer 4)",
    )
    p.add_argument(
        "--model",
        choices=["opus", "sonnet", "haiku"],
        default=None,
        help="Override Claude model for structural repair (default: haiku for style detection, sonnet for structure)",
    )
    p.add_argument(
        "--max-repair-pages",
        type=int,
        default=None,
        metavar="N",
        help="Limit Layer 4 AI repair to N regions",
    )
    p.set_defaults(func=cmd_extract)
