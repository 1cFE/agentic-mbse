#!/usr/bin/env python3
"""Extract a single page from a PDF as markdown, single-page PDF, or PNG image.

Usage:
    # Extract page as markdown via pymupdf4llm
    python extract_page.py document.pdf 5 --mode markdown

    # Extract page as single-page PDF (for Docling MCP)
    python extract_page.py document.pdf 5 --mode pdf --output /tmp/page_5.pdf

    # Render page as PNG image (fallback for visual analysis)
    python extract_page.py document.pdf 5 --mode image --dpi 200 --output /tmp/page_5.png

    # Show PDF metadata and page count
    python extract_page.py document.pdf --info

Pages are 0-indexed (first page = 0).
"""

import argparse
import json
import sys
from pathlib import Path


def get_info(pdf_path: str) -> dict:
    """Return PDF metadata and page count."""
    import pymupdf

    doc = pymupdf.open(pdf_path)
    info = {
        "path": str(Path(pdf_path).resolve()),
        "page_count": len(doc),
        "metadata": doc.metadata,
    }
    doc.close()
    return info


def extract_markdown(pdf_path: str, page_num: int) -> str:
    """Extract a single page as markdown using pymupdf4llm."""
    import pymupdf4llm
    from agentic_mbse.extraction.postprocess import postprocess
    from agentic_mbse.extraction.pymupdf_backend import _academic_header_detector

    md = pymupdf4llm.to_markdown(
        pdf_path,
        pages=[page_num],
        hdr_info=_academic_header_detector,
        table_strategy="lines",
    )
    md = postprocess(md, images_dir=None)
    return md


def extract_single_pdf(pdf_path: str, page_num: int, output: str) -> str:
    """Extract a single page as a standalone PDF file."""
    import pymupdf

    doc = pymupdf.open(pdf_path)
    single = pymupdf.open()
    single.insert_pdf(doc, from_page=page_num, to_page=page_num)
    single.save(output)
    single.close()
    doc.close()
    return output


def render_image(pdf_path: str, page_num: int, output: str, dpi: int = 200) -> str:
    """Render a single page as a PNG image."""
    import pymupdf

    doc = pymupdf.open(pdf_path)
    page = doc[page_num]
    scale = dpi / 72
    pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale))
    pix.save(output)
    doc.close()
    return output


def main():
    parser = argparse.ArgumentParser(description="Extract a single PDF page")
    parser.add_argument("pdf", help="Path to PDF file")
    parser.add_argument("page", nargs="?", type=int, help="Page number (0-indexed)")
    parser.add_argument(
        "--mode",
        choices=["markdown", "pdf", "image"],
        default="markdown",
        help="Extraction mode (default: markdown)",
    )
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--dpi", type=int, default=200, help="DPI for image mode (default: 200)")
    parser.add_argument("--info", action="store_true", help="Show PDF info and exit")

    args = parser.parse_args()

    if args.info:
        info = get_info(args.pdf)
        print(json.dumps(info, indent=2))
        return

    if args.page is None:
        parser.error("page number is required unless --info is used")

    # Validate page number
    import pymupdf

    doc = pymupdf.open(args.pdf)
    page_count = len(doc)
    doc.close()

    if args.page < 0 or args.page >= page_count:
        print(f"Error: page {args.page} out of range (0-{page_count - 1})", file=sys.stderr)
        sys.exit(1)

    if args.mode == "markdown":
        md = extract_markdown(args.pdf, args.page)
        if args.output:
            Path(args.output).write_text(md)
            print(f"Markdown written to {args.output}")
        else:
            print(md)

    elif args.mode == "pdf":
        out = args.output or f"/tmp/page_{args.page}.pdf"
        extract_single_pdf(args.pdf, args.page, out)
        print(f"Single-page PDF written to {out}")

    elif args.mode == "image":
        out = args.output or f"/tmp/page_{args.page}.png"
        render_image(args.pdf, args.page, out, args.dpi)
        print(f"PNG image written to {out}")


if __name__ == "__main__":
    main()
