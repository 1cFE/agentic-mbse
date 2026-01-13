#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read a specific section from a document using INDEX.md.

This script parses an INDEX.md file to find the line range for a section,
then reads that portion of the full_document.md file.

Usage:
    read_section.py <path> <section> [OPTIONS]

Arguments:
    path        Path to full_document.md or its containing folder
    section     Section number (e.g., "7", "7.2", "7.2.1")

Options:
    --context INT   Extra lines before/after section (default: 0)
    --raw           Output content only without header
    --help          Show this help message
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple


def parse_index_sections(index_content: str) -> Dict[str, Tuple[int, int, str]]:
    """Parse INDEX.md to extract section line ranges.

    Returns:
        Dict mapping section_num to (start_line, end_line, title)
    """
    sections = {}

    # Pattern to match section headers like "## 7.2.1 Root Overview"
    header_pattern = re.compile(r'^#{2,}\s+(\d+(?:\.\d+)*)\s+(.+)$', re.MULTILINE)

    # Pattern to match line numbers like "**Lines:** 959-2845"
    lines_pattern = re.compile(r'\*\*Lines:\*\*\s*(\d+)-(\d+)')

    # Find all headers
    headers = list(header_pattern.finditer(index_content))

    for i, match in enumerate(headers):
        section_num = match.group(1)
        title = match.group(2).strip()

        # Find the **Lines:** entry after this header (before next header)
        start_pos = match.end()
        end_pos = headers[i + 1].start() if i + 1 < len(headers) else len(index_content)

        section_text = index_content[start_pos:end_pos]
        lines_match = lines_pattern.search(section_text)

        if lines_match:
            start_line = int(lines_match.group(1))
            end_line = int(lines_match.group(2))
            sections[section_num] = (start_line, end_line, title)

    return sections


def read_lines(path: Path, start: int, end: int, context: int = 0) -> str:
    """Read specific lines from a file (1-indexed, inclusive)."""
    with open(path, 'r') as f:
        lines = f.readlines()

    # Adjust for context
    actual_start = max(1, start - context)
    actual_end = min(len(lines), end + context)

    # Convert to 0-indexed for slicing
    return ''.join(lines[actual_start - 1:actual_end])


def main():
    parser = argparse.ArgumentParser(
        description='Read a specific section from a document using INDEX.md.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s docs/sysmlv2/SysML_KerMLSpec/ 9.4
    %(prog)s docs/sysmlv2/SysML_KerMLSpec/ 7.2.1 --context 5
    %(prog)s docs/sysmlv2/SysML_KerMLSpec/full_document.md 7 --raw
        """
    )
    parser.add_argument('path', type=Path, help='Path to full_document.md or containing folder')
    parser.add_argument('section', type=str, help='Section number (e.g., "7", "7.2", "7.2.1")')
    parser.add_argument('--context', type=int, default=0, help='Extra lines before/after (default: 0)')
    parser.add_argument('--raw', action='store_true', help='Output content only without header')

    args = parser.parse_args()

    # Resolve paths
    if args.path.is_dir():
        doc_path = args.path / 'full_document.md'
        index_path = args.path / 'INDEX.md'
    else:
        doc_path = args.path
        index_path = args.path.parent / 'INDEX.md'

    # Validate files exist
    if not doc_path.exists():
        print(f"Error: {doc_path} not found", file=sys.stderr)
        sys.exit(1)

    if not index_path.exists():
        print(f"Error: {index_path} not found", file=sys.stderr)
        print(f"  Run generate_index.py first to create the index", file=sys.stderr)
        sys.exit(1)

    # Parse index
    index_content = index_path.read_text()
    sections = parse_index_sections(index_content)

    # Find requested section
    if args.section not in sections:
        print(f"Error: Section '{args.section}' not found in index", file=sys.stderr)
        print(f"\nAvailable sections:", file=sys.stderr)
        for sec_num in sorted(sections.keys(), key=lambda x: [int(p) for p in x.split('.')]):
            _, _, title = sections[sec_num]
            print(f"  {sec_num}: {title}", file=sys.stderr)
        sys.exit(1)

    start_line, end_line, title = sections[args.section]

    # Read content
    content = read_lines(doc_path, start_line, end_line, args.context)

    # Output
    if args.raw:
        print(content, end='')
    else:
        print(f"# {args.section} {title}")
        print(f"# Lines {start_line}-{end_line} from {doc_path.name}")
        if args.context > 0:
            actual_start = max(1, start_line - args.context)
            actual_end = end_line + args.context
            print(f"# (with {args.context} lines context: {actual_start}-{actual_end})")
        print()
        print(content, end='')


if __name__ == '__main__':
    main()
