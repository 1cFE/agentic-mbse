"""CLI subcommand registration for document ingestion pipeline."""

import argparse
from pathlib import Path

from doc_ingest import cli as doc_ingest_cli


def cmd_doc_extract(args: argparse.Namespace) -> int:
    """Handle 'ingest' command."""
    identifier = args.identifier
    output_dir = Path(args.output_dir) if args.output_dir else Path.cwd() / "data/ingested"
    format_override = args.format if args.format != "auto" else None

    return doc_ingest_cli.cmd_extract(
        identifier=identifier,
        output_dir=output_dir,
        format_override=format_override,
    )


def register_doc_ingest_subcommand(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'ingest' subcommand for document ingestion.

    Args:
        subparsers: Subparser action from main CLI parser
    """
    p = subparsers.add_parser(
        "ingest",
        help="Ingest scientific documents (DOI, arXiv, PMC, local files) to structured markdown",
        description=(
            "Extract and ingest scientific documents from various sources "
            "(DOI, arXiv, PMC, local files) into structured markdown with "
            "provenance tracking. The pipeline automatically discovers available "
            "sources, attempts extraction in quality-ordered fashion, and persists "
            "results with full provenance."
        ),
    )

    p.add_argument(
        "identifier",
        help="Document identifier: DOI (10.xxxx/...), arXiv ID (YYMM.NNNNN), PMC ID (PMC#####), or local file path",
    )

    p.add_argument(
        "--output-dir",
        "-o",
        default=None,
        metavar="DIR",
        help="Output directory for extracted documents (default: ./data/ingested)",
    )

    p.add_argument(
        "--format",
        choices=["auto", "pdf", "jats_xml", "arxiv_html", "publisher_html", "docx"],
        default="auto",
        help="Format override to skip discovery and attempt specific format only (default: auto)",
    )

    p.set_defaults(func=cmd_doc_extract)
