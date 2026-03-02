"""Index generation and section reading for extracted documents.

Ported from ``scripts/generate_index.py`` and ``scripts/read_section.py``
into a callable library module.  The original scripts are reduced to thin
wrappers that delegate here.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class Section:
    """Represents a document section."""

    section_num: str  # e.g., "7.2.1"
    title: str  # e.g., "Root Overview"
    depth: int  # 1 for "7", 2 for "7.2", 3 for "7.2.1"
    line_start: int  # 1-indexed line number
    line_end: int  # 1-indexed line number (inclusive)
    content: str  # Raw content of the section
    breadcrumb: str = ""  # e.g., "7 Language > 7.2 Root"
    subsections: list[str] = field(default_factory=list)
    summary: str = ""  # AI-generated summary


# ---------------------------------------------------------------------------
# Checksum helpers
# ---------------------------------------------------------------------------


def _get_file_checksum(path: Path) -> str:
    """Calculate SHA256 checksum of a file."""
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _parse_existing_checksum(index_path: Path) -> str | None:
    """Extract ``source_checksum`` from existing INDEX.md frontmatter."""
    if not index_path.exists():
        return None
    content = index_path.read_text()
    match = re.search(r"^source_checksum:\s*(.+)$", content, re.MULTILINE)
    return match.group(1).strip() if match else None


# ---------------------------------------------------------------------------
# Section parsing
# ---------------------------------------------------------------------------


def parse_sections(content: str, max_depth: int = 3) -> list[Section]:
    """Parse numbered section headers from markdown content.

    Supports multiple header formats:
        Format A (KerML):  ``## 7.2.1 Title`` or ``## 7.2.1. Title``
        Format B (Part1):  ``### **7 Title**``
        Format C (generic): ``##### 7.2.1 Title``
        Format D (appendix): ``## A.1 Title``

    Falls back to ``_parse_unnumbered_sections()`` with synthetic section
    numbers when no numbered headers are found.
    """
    lines = content.split("\n")

    patterns = [
        # Format A: ## 7.2.1 Title  or  ## 7.2.1. Title
        re.compile(r"^##\s+(\d+(?:\.\d+)*)\.?\s+(.+)$"),
        # Format B: ### **7 Title** or ### **7. Title** (bold)
        re.compile(r"^#{2,6}\s+\*\*(\d+(?:\.\d+)*)\.?\s+(.+?)\*\*\s*$"),
        # Format C: generic levels (with optional trailing period)
        re.compile(r"^#{2,6}\s+(\d+(?:\.\d+)*)\.?\s+(.+)$"),
        # Format D: Appendix letter numbering (## A.1 Title or ## A.1. Title)
        re.compile(r"^#{2,6}\s+([A-Z](?:\.\d+)*)\.?\s+(.+)$"),
    ]

    sections: list[Section] = []

    for i, line in enumerate(lines):
        match = None
        for pattern in patterns:
            match = pattern.match(line)
            if match:
                break
        if not match:
            continue

        section_num = match.group(1)
        title = match.group(2).strip().rstrip("*").strip()
        # Depth: count dots + 1 (works for both "7.2.1" and "A.1.2")
        depth = section_num.count(".") + 1

        if depth > max_depth:
            continue

        sections.append(
            Section(
                section_num=section_num,
                title=title,
                depth=depth,
                line_start=i + 1,  # 1-indexed
                line_end=0,
                content="",
            )
        )

    # Calculate line_end and extract body content.
    #
    # line_start/line_end are 1-indexed inclusive (for INDEX.md display and
    # read_lines()).  For body content we deliberately exclude the header:
    #   header is at 0-indexed [line_start - 1]
    #   body starts at 0-indexed [line_start]  (== line_start used as-is)
    #   body ends before 0-indexed [line_end]  (== line_end used as-is)
    # This works because a 1-indexed inclusive value N equals the 0-indexed
    # exclusive bound for the *next* position, neatly skipping the header
    # and stopping before the next section.
    for i, section in enumerate(sections):
        if i + 1 < len(sections):
            section.line_end = sections[i + 1].line_start - 1
        else:
            section.line_end = len(lines)
        section.content = "\n".join(lines[section.line_start : section.line_end])

    if sections:
        return sections

    # Fallback: unnumbered headers with synthetic section numbers
    return _parse_unnumbered_sections(lines, max_depth)


def _parse_unnumbered_sections(lines: list[str], max_depth: int) -> list[Section]:
    """Parse unnumbered markdown headers and assign synthetic section numbers.

    Used as a fallback when ``parse_sections`` finds no numbered headers.
    Generates dot-notation section_nums from depth counters so that
    ``build_hierarchy``, ``format_index_md``, and ``read_section`` all work
    unchanged.
    """
    _UNNUMBERED_RE = re.compile(r"^(#{2,6})\s+(.+)$")

    # counters[depth] tracks the current counter at each depth (1-indexed depth)
    counters: list[int] = [0] * (max_depth + 1)
    sections: list[Section] = []

    for i, line in enumerate(lines):
        m = _UNNUMBERED_RE.match(line)
        if not m:
            continue
        hashes = m.group(1)
        title = m.group(2).strip()
        depth = len(hashes) - 1  # ## = depth 1, ### = depth 2, etc.

        if depth > max_depth:
            continue

        # Increment counter at this depth, reset deeper counters
        counters[depth] += 1
        for d in range(depth + 1, max_depth + 1):
            counters[d] = 0

        # Build section_num from counters: "1", "1.1", "1.1.2"
        section_num = ".".join(str(counters[d]) for d in range(1, depth + 1))

        sections.append(
            Section(
                section_num=section_num,
                title=title,
                depth=depth,
                line_start=i + 1,  # 1-indexed
                line_end=0,
                content="",
            )
        )

    # Fill line_end and content (same logic as parse_sections)
    for i, section in enumerate(sections):
        if i + 1 < len(sections):
            section.line_end = sections[i + 1].line_start - 1
        else:
            section.line_end = len(lines)
        section.content = "\n".join(lines[section.line_start : section.line_end])

    return sections


def build_hierarchy(sections: list[Section]) -> None:
    """Build breadcrumbs and subsection lists in-place."""
    section_map = {s.section_num: s for s in sections}

    for section in sections:
        parts = section.section_num.split(".")
        breadcrumb_parts = []
        for i in range(len(parts) - 1):
            parent_num = ".".join(parts[: i + 1])
            if parent_num in section_map:
                parent = section_map[parent_num]
                breadcrumb_parts.append(f"{parent.section_num} {parent.title}")
        section.breadcrumb = " > ".join(breadcrumb_parts)

        section_prefix = section.section_num + "."
        for other in sections:
            if other.section_num.startswith(section_prefix):
                remaining = other.section_num[len(section_prefix) :]
                if "." not in remaining:
                    section.subsections.append(other.section_num)


# ---------------------------------------------------------------------------
# Summary generation (AI-powered, optional)
# ---------------------------------------------------------------------------


def generate_summary(title: str, content: str, section_num: str) -> str:
    """Call Claude to generate a 1-2 sentence summary."""
    lines = content.split("\n")
    if len(lines) > 500:
        content = "\n".join(lines[:500]) + "\n\n[...truncated for summarization]"

    prompt = (
        "Summarize this documentation section in 1-2 sentences. "
        "Focus on what concepts, functions, or definitions it contains. "
        'Be concise and specific. Do not start with "This section" - '
        "just state what it covers.\n\n"
        f"Section {section_num}: {title}\n\n{content}"
    )

    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
            # Detach child from controlling terminal so claude CLI's status
            # line rendering (writes to /dev/tty) can't corrupt parent output.
            start_new_session=True,
        )
        return " ".join(result.stdout.strip().split())
    except subprocess.CalledProcessError as exc:
        print(f"  Warning: Claude failed for {section_num}: {exc}", file=sys.stderr)
        return "[Summary generation failed]"
    except subprocess.TimeoutExpired:
        print(f"  Warning: Claude timed out for {section_num}", file=sys.stderr)
        return "[Summary generation timed out]"
    except FileNotFoundError:
        print("  Warning: 'claude' CLI not found, skipping summaries", file=sys.stderr)
        return "[claude CLI not available]"


# ---------------------------------------------------------------------------
# INDEX.md formatting
# ---------------------------------------------------------------------------


def format_index_md(sections: list[Section], metadata: dict) -> str:
    """Generate the INDEX.md content string."""
    lines: list[str] = []

    # YAML frontmatter
    lines.append("---")
    for key in (
        "document",
        "generated",
        "source_checksum",
        "total_lines",
        "depth",
        "section_count",
    ):
        lines.append(f"{key}: {metadata[key]}")
    lines.append("---")
    lines.append("")

    lines.append(f"# {metadata['document']} Index")
    lines.append("")

    for section in sections:
        header_prefix = "#" * (section.depth + 1)
        lines.append(f"{header_prefix} {section.section_num} {section.title}")

        meta_parts = [f"**Lines:** {section.line_start}-{section.line_end}"]
        if section.subsections:
            meta_parts.append(f"**Subsections:** {', '.join(section.subsections)}")
        lines.append(" | ".join(meta_parts))

        lines.append("")
        if section.summary:
            lines.append(section.summary)
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Library API
# ---------------------------------------------------------------------------


def generate_index(
    doc_path: Path,
    depth: int = 3,
    summarize: bool = False,
    force: bool = False,
) -> Path | None:
    """Generate INDEX.md for a ``full_document.md`` file.

    Returns the path to INDEX.md on success, or ``None`` if skipped
    (already up-to-date).
    """
    if doc_path.is_dir():
        doc_path = doc_path / "full_document.md"

    if not doc_path.exists():
        return None

    index_path = doc_path.parent / "INDEX.md"

    current_checksum = _get_file_checksum(doc_path)
    existing_checksum = _parse_existing_checksum(index_path)

    if not force and existing_checksum == current_checksum:
        return None  # up to date

    content = doc_path.read_text()
    total_lines = len(content.split("\n"))

    sections = parse_sections(content, max_depth=depth)
    build_hierarchy(sections)

    if summarize:
        for section in sections:
            section.summary = generate_summary(section.title, section.content, section.section_num)

    metadata = {
        "document": doc_path.parent.name,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_checksum": current_checksum,
        "total_lines": total_lines,
        "depth": depth,
        "section_count": len(sections),
    }

    index_content = format_index_md(sections, metadata)
    index_path.write_text(index_content)
    return index_path


# ---------------------------------------------------------------------------
# Section reading
# ---------------------------------------------------------------------------


def parse_index_sections(index_content: str) -> dict[str, tuple[int, int, str]]:
    """Parse INDEX.md to extract section line ranges.

    Returns a dict mapping ``section_num`` to ``(start_line, end_line, title)``.
    """
    sections: dict[str, tuple[int, int, str]] = {}

    header_pattern = re.compile(r"^#{2,}\s+(\d+(?:\.\d+)*|[A-Z](?:\.\d+)*)\.?\s+(.+)$", re.MULTILINE)
    lines_pattern = re.compile(r"\*\*Lines:\*\*\s*(\d+)-(\d+)")

    headers = list(header_pattern.finditer(index_content))

    for i, match in enumerate(headers):
        section_num = match.group(1)
        title = match.group(2).strip()

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
    all_lines = path.read_text().splitlines(keepends=True)
    actual_start = max(1, start - context)
    actual_end = min(len(all_lines), end + context)
    return "".join(all_lines[actual_start - 1 : actual_end])


def read_section(
    doc_path: Path,
    section_num: str,
    context: int = 0,
) -> str | None:
    """Read a specific section from a document using its INDEX.md.

    Returns the section content, or ``None`` if the section is not found.
    """
    if doc_path.is_dir():
        doc_path = doc_path / "full_document.md"

    index_path = doc_path.parent / "INDEX.md"
    if not index_path.exists() or not doc_path.exists():
        return None

    sections = parse_index_sections(index_path.read_text())
    if section_num not in sections:
        return None

    start_line, end_line, _ = sections[section_num]
    return read_lines(doc_path, start_line, end_line, context)


# ---------------------------------------------------------------------------
# CLI entry points (used by thin script wrappers)
# ---------------------------------------------------------------------------


def cli_main() -> None:
    """CLI entry point for ``generate_index.py``."""
    parser = argparse.ArgumentParser(
        description="Generate INDEX.md from full_document.md with AI summaries.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s docs/sysmlv2/SysML_KerMLSpec/
    %(prog)s --depth 2 docs/sysmlv2/SysML_KerMLSpec/full_document.md
    %(prog)s --dry-run docs/sysmlv2/SysML_KerMLSpec/
    %(prog)s --force docs/sysmlv2/SysML_KerMLSpec/
        """,
    )
    parser.add_argument("path", type=Path, help="Path to full_document.md or containing folder")
    parser.add_argument(
        "--depth", type=int, default=3, help="Max header depth to index (default: 3)"
    )
    parser.add_argument("--force", action="store_true", help="Regenerate even if checksum matches")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show sections without generating summaries"
    )
    parser.add_argument(
        "--summarize",
        action="store_true",
        default=True,
        help="Generate AI summaries (default: True)",
    )
    parser.add_argument(
        "--no-summarize",
        dest="summarize",
        action="store_false",
        help="Skip AI summary generation",
    )

    args = parser.parse_args()

    # Resolve path
    if args.path.is_dir():
        doc_path = args.path / "full_document.md"
    else:
        doc_path = args.path

    if not doc_path.exists():
        print(f"Error: {doc_path} not found", file=sys.stderr)
        sys.exit(1)

    # Dry-run mode
    if args.dry_run:
        content = doc_path.read_text()
        sections = parse_sections(content, args.depth)
        build_hierarchy(sections)
        print(f"Found {len(sections)} sections at depth <= {args.depth}")
        print("\nSections found (dry-run mode):\n")
        for section in sections:
            indent = "  " * (section.depth - 1)
            print(f"{indent}{section.section_num} {section.title}")
            print(
                f"{indent}  Lines {section.line_start}-{section.line_end} "
                f"({section.line_end - section.line_start + 1} lines)"
            )
            if section.breadcrumb:
                print(f"{indent}  Breadcrumb: {section.breadcrumb}")
        sys.exit(0)

    # Check freshness
    index_path = doc_path.parent / "INDEX.md"
    current_checksum = _get_file_checksum(doc_path)
    existing_checksum = _parse_existing_checksum(index_path)

    if not args.force and existing_checksum == current_checksum:
        print("INDEX.md is up to date (checksum matches)")
        print("  Use --force to regenerate anyway")
        sys.exit(0)

    # Generate
    print(f"Parsing {doc_path}...")
    result = generate_index(
        doc_path,
        depth=args.depth,
        summarize=args.summarize,
        force=True,  # We already did the freshness check above
    )

    if result:
        content = doc_path.read_text()
        sections = parse_sections(content, args.depth)
        print(f"\nCreated {result}")
        print(f"  {len(sections)} sections indexed")
        print(f"  {len(content.splitlines())} total lines in source document")


def read_section_cli_main() -> None:
    """CLI entry point for ``read_section.py``."""
    parser = argparse.ArgumentParser(
        description="Read a specific section from a document using INDEX.md.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s docs/sysmlv2/SysML_KerMLSpec/ 9.4
    %(prog)s docs/sysmlv2/SysML_KerMLSpec/ 7.2.1 --context 5
    %(prog)s docs/sysmlv2/SysML_KerMLSpec/full_document.md 7 --raw
        """,
    )
    parser.add_argument("path", type=Path, help="Path to full_document.md or containing folder")
    parser.add_argument("section", type=str, help='Section number (e.g., "7", "7.2", "7.2.1")')
    parser.add_argument(
        "--context", type=int, default=0, help="Extra lines before/after (default: 0)"
    )
    parser.add_argument("--raw", action="store_true", help="Output content only without header")

    args = parser.parse_args()

    # Resolve paths
    if args.path.is_dir():
        doc_path = args.path / "full_document.md"
        index_path = args.path / "INDEX.md"
    else:
        doc_path = args.path
        index_path = args.path.parent / "INDEX.md"

    if not doc_path.exists():
        print(f"Error: {doc_path} not found", file=sys.stderr)
        sys.exit(1)
    if not index_path.exists():
        print(f"Error: {index_path} not found", file=sys.stderr)
        print("  Run generate_index.py first to create the index", file=sys.stderr)
        sys.exit(1)

    sections = parse_index_sections(index_path.read_text())

    if args.section not in sections:
        print(f"Error: Section '{args.section}' not found in index", file=sys.stderr)
        print("\nAvailable sections:", file=sys.stderr)
        for sec_num in sorted(sections.keys(), key=lambda x: [int(p) for p in x.split(".")]):
            _, _, title = sections[sec_num]
            print(f"  {sec_num}: {title}", file=sys.stderr)
        sys.exit(1)

    start_line, end_line, title = sections[args.section]
    content = read_lines(doc_path, start_line, end_line, args.context)

    if args.raw:
        print(content, end="")
    else:
        print(f"# {args.section} {title}")
        print(f"# Lines {start_line}-{end_line} from {doc_path.name}")
        if args.context > 0:
            actual_start = max(1, start_line - args.context)
            actual_end = end_line + args.context
            print(f"# (with {args.context} lines context: {actual_start}-{actual_end})")
        print()
        print(content, end="")
