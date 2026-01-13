#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate INDEX.md from full_document.md with AI-generated summaries.

This script parses numbered section headers from a markdown document,
calls Claude to generate 1-2 sentence summaries for each section,
and produces a structured INDEX.md file.

Usage:
    generate_index.py [OPTIONS] <path>

Arguments:
    path    Path to full_document.md or its containing folder

Options:
    --depth INT     Max header depth to index (default: 3)
    --force         Regenerate even if checksum matches
    --dry-run       Show sections without generating summaries
    --help          Show this help message
"""

import argparse
import hashlib
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


@dataclass
class Section:
    """Represents a document section."""
    section_num: str        # e.g., "7.2.1"
    title: str              # e.g., "Root Overview"
    depth: int              # 1 for "7", 2 for "7.2", 3 for "7.2.1"
    line_start: int         # 1-indexed line number
    line_end: int           # 1-indexed line number (inclusive)
    content: str            # Raw content of the section
    breadcrumb: str = ""    # e.g., "7 Language > 7.2 Root"
    subsections: List[str] = field(default_factory=list)  # e.g., ["7.2.1", "7.2.2"]
    summary: str = ""       # AI-generated summary


def get_file_checksum(path: Path) -> str:
    """Calculate SHA256 checksum of a file."""
    content = path.read_bytes()
    return f"sha256:{hashlib.sha256(content).hexdigest()}"


def parse_existing_checksum(index_path: Path) -> Optional[str]:
    """Extract source_checksum from existing INDEX.md frontmatter."""
    if not index_path.exists():
        return None

    content = index_path.read_text()
    match = re.search(r'^source_checksum:\s*(.+)$', content, re.MULTILINE)
    return match.group(1).strip() if match else None


def parse_sections(content: str, max_depth: int) -> List[Section]:
    """Parse numbered section headers from markdown content.

    Supports multiple header formats:
        Format A (KerML): ## 7.2.1 Title
        Format B (Part1): ### **7 Title** or ##### **7.2.1 Title**
    """
    lines = content.split('\n')

    # Multiple patterns to match different document formats
    patterns = [
        # Format A: ## 7.2.1 Title (KerML spec style)
        re.compile(r'^##\s+(\d+(?:\.\d+)*)\s+(.+)$'),
        # Format B: ### **7 Title** or ##### **7.2.1 Title** (Part1 style, with bold)
        re.compile(r'^#{2,6}\s+\*\*(\d+(?:\.\d+)*)\s+(.+?)\*\*\s*$'),
        # Format C: ### 7 Title or ##### 7.2.1 Title (generic markdown levels)
        re.compile(r'^#{2,6}\s+(\d+(?:\.\d+)*)\s+(.+)$'),
    ]

    sections: List[Section] = []

    for i, line in enumerate(lines):
        match = None
        for pattern in patterns:
            match = pattern.match(line)
            if match:
                break

        if not match:
            continue

        section_num = match.group(1)
        title = match.group(2).strip()
        # Remove trailing ** if present (from bold format)
        title = title.rstrip('*').strip()
        depth = section_num.count('.') + 1

        # Only include sections up to max_depth
        if depth > max_depth:
            continue

        sections.append(Section(
            section_num=section_num,
            title=title,
            depth=depth,
            line_start=i + 1,  # 1-indexed
            line_end=0,        # Will be calculated
            content=""         # Will be calculated
        ))

    # Calculate line_end and content for each section
    for i, section in enumerate(sections):
        if i + 1 < len(sections):
            section.line_end = sections[i + 1].line_start - 1
        else:
            section.line_end = len(lines)

        # Extract content (excluding the header line itself)
        section.content = '\n'.join(lines[section.line_start:section.line_end])

    return sections


def build_hierarchy(sections: List[Section]) -> None:
    """Build breadcrumbs and subsection lists for each section."""
    # Build a map of section_num -> Section for quick lookup
    section_map = {s.section_num: s for s in sections}

    for section in sections:
        # Build breadcrumb from parent sections
        parts = section.section_num.split('.')
        breadcrumb_parts = []

        for i in range(len(parts) - 1):
            parent_num = '.'.join(parts[:i + 1])
            if parent_num in section_map:
                parent = section_map[parent_num]
                breadcrumb_parts.append(f"{parent.section_num} {parent.title}")

        section.breadcrumb = ' > '.join(breadcrumb_parts)

        # Find direct child sections (subsections)
        section_prefix = section.section_num + '.'
        for other in sections:
            # Is this a direct child? (one level deeper)
            if other.section_num.startswith(section_prefix):
                remaining = other.section_num[len(section_prefix):]
                # Direct child has no more dots
                if '.' not in remaining:
                    section.subsections.append(other.section_num)


def generate_summary(title: str, content: str, section_num: str) -> str:
    """Call Claude to generate a 1-2 sentence summary."""
    # Truncate very long sections for summarization
    lines = content.split('\n')
    if len(lines) > 500:
        content = '\n'.join(lines[:500]) + '\n\n[...truncated for summarization]'

    prompt = f"""Summarize this documentation section in 1-2 sentences.
Focus on what concepts, functions, or definitions it contains. Be concise and specific.
Do not start with "This section" - just state what it covers.

Section {section_num}: {title}

{content}"""

    try:
        result = subprocess.run(
            ['claude', '-p', prompt],
            capture_output=True,
            text=True,
            check=True,
            timeout=60
        )
        summary = result.stdout.strip()
        # Clean up any extra whitespace or newlines
        summary = ' '.join(summary.split())
        return summary
    except subprocess.CalledProcessError as e:
        print(f"  Warning: Claude failed for {section_num}: {e}", file=sys.stderr)
        return f"[Summary generation failed]"
    except subprocess.TimeoutExpired:
        print(f"  Warning: Claude timed out for {section_num}", file=sys.stderr)
        return f"[Summary generation timed out]"


def format_index_md(sections: List[Section], metadata: dict) -> str:
    """Generate the INDEX.md content."""
    lines = []

    # YAML frontmatter
    lines.append('---')
    lines.append(f"document: {metadata['document']}")
    lines.append(f"generated: {metadata['generated']}")
    lines.append(f"source_checksum: {metadata['source_checksum']}")
    lines.append(f"total_lines: {metadata['total_lines']}")
    lines.append(f"depth: {metadata['depth']}")
    lines.append(f"section_count: {metadata['section_count']}")
    lines.append('---')
    lines.append('')

    # Title
    lines.append(f"# {metadata['document']} Index")
    lines.append('')

    # Sections
    for section in sections:
        # Header level based on depth (## for depth 1, ### for depth 2, etc.)
        header_prefix = '#' * (section.depth + 1)
        lines.append(f"{header_prefix} {section.section_num} {section.title}")

        # Metadata line
        meta_parts = [f"**Lines:** {section.line_start}-{section.line_end}"]
        if section.subsections:
            meta_parts.append(f"**Subsections:** {', '.join(section.subsections)}")
        lines.append(' | '.join(meta_parts))

        # Summary
        lines.append('')
        if section.summary:
            lines.append(section.summary)
        lines.append('')

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Generate INDEX.md from full_document.md with AI summaries.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s docs/sysmlv2/SysML_KerMLSpec/
    %(prog)s --depth 2 docs/sysmlv2/SysML_KerMLSpec/full_document.md
    %(prog)s --dry-run docs/sysmlv2/SysML_KerMLSpec/
    %(prog)s --force docs/sysmlv2/SysML_KerMLSpec/
        """
    )
    parser.add_argument('path', type=Path, help='Path to full_document.md or containing folder')
    parser.add_argument('--depth', type=int, default=3, help='Max header depth to index (default: 3)')
    parser.add_argument('--force', action='store_true', help='Regenerate even if checksum matches')
    parser.add_argument('--dry-run', action='store_true', help='Show sections without generating summaries')

    args = parser.parse_args()

    # Resolve path to full_document.md
    if args.path.is_dir():
        doc_path = args.path / 'full_document.md'
    else:
        doc_path = args.path

    if not doc_path.exists():
        print(f"Error: {doc_path} not found", file=sys.stderr)
        sys.exit(1)

    index_path = doc_path.parent / 'INDEX.md'

    # Check if regeneration is needed
    current_checksum = get_file_checksum(doc_path)
    existing_checksum = parse_existing_checksum(index_path)

    if not args.force and not args.dry_run and existing_checksum == current_checksum:
        print(f"INDEX.md is up to date (checksum matches)")
        print(f"  Use --force to regenerate anyway")
        sys.exit(0)

    # Parse document
    print(f"Parsing {doc_path}...")
    content = doc_path.read_text()
    lines = content.split('\n')

    sections = parse_sections(content, args.depth)
    build_hierarchy(sections)

    print(f"Found {len(sections)} sections at depth <= {args.depth}")

    if args.dry_run:
        print("\nSections found (dry-run mode):\n")
        for section in sections:
            indent = "  " * (section.depth - 1)
            print(f"{indent}{section.section_num} {section.title}")
            print(f"{indent}  Lines {section.line_start}-{section.line_end} ({section.line_end - section.line_start + 1} lines)")
            if section.breadcrumb:
                print(f"{indent}  Breadcrumb: {section.breadcrumb}")
        sys.exit(0)

    # Generate summaries
    print(f"\nGenerating summaries (this may take a few minutes)...")
    for i, section in enumerate(sections, 1):
        print(f"  [{i}/{len(sections)}] {section.section_num} {section.title[:40]}...")
        section.summary = generate_summary(section.title, section.content, section.section_num)

    # Build metadata
    metadata = {
        'document': doc_path.parent.name,
        'generated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source_checksum': current_checksum,
        'total_lines': len(lines),
        'depth': args.depth,
        'section_count': len(sections)
    }

    # Generate and write INDEX.md
    index_content = format_index_md(sections, metadata)
    index_path.write_text(index_content)

    print(f"\nCreated {index_path}")
    print(f"  {len(sections)} sections indexed")
    print(f"  {len(lines)} total lines in source document")


if __name__ == '__main__':
    main()
