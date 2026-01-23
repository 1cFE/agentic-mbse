#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sync SysML v2 standard library files from syside package to docs/sysmlv2/stdlib/.

This script copies the standard library source files (.kerml, .sysml) from the
installed syside package to a git-tracked location, and generates an INDEX.md
with AI-generated summaries for agent navigation.

Usage:
    sync_stdlib.py [OPTIONS]

Options:
    --dry-run   Preview what would be done without making changes
    --force     Overwrite existing stdlib directory
    --help      Show this help message
"""

import argparse
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# Output directory relative to repo root
STDLIB_DIR = Path("docs/sysmlv2/stdlib")


def get_syside_library_path() -> Path:
    """Locate the syside sysml.library directory."""
    try:
        import syside
    except ImportError:
        print("Error: syside package is not installed.", file=sys.stderr)
        print("Install it with: uv sync", file=sys.stderr)
        sys.exit(1)

    library_path = Path(syside.__file__).parent / "sysml.library"
    if not library_path.exists():
        print(f"Error: sysml.library not found at {library_path}", file=sys.stderr)
        sys.exit(1)

    return library_path


def get_syside_version() -> str:
    """Get the installed syside version."""
    from importlib.metadata import version
    return version("syside")


def copy_library_files(src: Path, dst: Path, dry_run: bool = False) -> list[Path]:
    """
    Copy .kerml and .sysml files from src to dst, preserving directory structure.

    Returns list of destination file paths.
    """
    copied = []

    for src_file in sorted(src.rglob("*")):
        if src_file.suffix in (".kerml", ".sysml"):
            rel_path = src_file.relative_to(src)
            dst_file = dst / rel_path

            if not dry_run:
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)

            copied.append(dst_file)

    return copied


def generate_file_summary(file_path: Path) -> str:
    """Call claude -p to generate a 1-line summary of a library file."""
    try:
        content = file_path.read_text()[:2000]  # Truncate for context limits
    except Exception as e:
        return f"[Error reading file: {e}]"

    prompt = f"""Summarize this SysML/KerML library file in ONE line (max 100 chars).
Focus on what functions, types, or definitions it provides.
Do not start with "This file" or "Defines" - just state what it contains.

File: {file_path.name}
Content:
{content}"""

    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            return "[Summary generation failed]"
        # Clean up whitespace
        summary = " ".join(result.stdout.strip().split())
        # Truncate if too long
        if len(summary) > 120:
            summary = summary[:117] + "..."
        return summary
    except subprocess.TimeoutExpired:
        return "[Summary generation timed out]"
    except FileNotFoundError:
        print("Error: 'claude' CLI not found. Install Claude Code.", file=sys.stderr)
        sys.exit(1)


def get_quick_reference() -> str:
    """Return the hardcoded Quick Reference section from the spec."""
    return """## Quick Reference

### Common Functions

| Function | Signature | Package |
|----------|-----------|---------|
| `sum` | `sum(collection: NumericalValue[0..*]) → NumericalValue` | NumericalFunctions |
| `product` | `product(collection: NumericalValue[0..*]) → NumericalValue` | NumericalFunctions |
| `abs` | `abs(x: NumericalValue) → NumericalValue` | NumericalFunctions |
| `max` | `max(x, y: NumericalValue) → NumericalValue` | NumericalFunctions |
| `min` | `min(x, y: NumericalValue) → NumericalValue` | NumericalFunctions |
| `size` | `size(seq: Anything[0..*]) → Natural` | SequenceFunctions |
| `isEmpty` | `isEmpty(seq: Anything[0..*]) → Boolean` | SequenceFunctions |
| `notEmpty` | `notEmpty(seq: Anything[0..*]) → Boolean` | SequenceFunctions |
| `head` | `head(seq: Anything[0..*]) → Anything[0..1]` | SequenceFunctions |
| `tail` | `tail(seq: Anything[0..*]) → Anything[0..*]` | SequenceFunctions |
| `includes` | `includes(seq, value) → Boolean` | SequenceFunctions |
| `union` | `union(seq1, seq2) → Anything[0..*]` | SequenceFunctions |
| `intersection` | `intersection(seq1, seq2) → Anything[0..*]` | SequenceFunctions |
| `collect` | `collection->collect { mapper }` | ControlFunctions |
| `select` | `collection->select { predicate }` | ControlFunctions |
| `reject` | `collection->reject { predicate }` | ControlFunctions |
| `reduce` | `collection->reduce operator` | ControlFunctions |
| `forAll` | `collection->forAll { test } → Boolean` | ControlFunctions |
| `exists` | `collection->exists { test } → Boolean` | ControlFunctions |
| `not` | `not(x: Boolean) → Boolean` | BooleanFunctions |
| `xor` | `xor(x, y: Boolean) → Boolean` | BooleanFunctions |
| `ToString` | `ToString(x: Anything) → String` | BaseFunctions |
| `sin` | `sin(x: Real) → Real` | TrigFunctions |
| `cos` | `cos(x: Real) → Real` | TrigFunctions |
| `sqrt` | `sqrt(x: Real) → Real` | RealFunctions |

### Core Types

| Type | Package | Description |
|------|---------|-------------|
| `Boolean` | ScalarValues | True/false values |
| `String` | ScalarValues | Text values |
| `Real` | ScalarValues | Real numbers |
| `Integer` | ScalarValues | Whole numbers |
| `Natural` | ScalarValues | Non-negative integers (≥0) |
| `Positive` | ScalarValues | Positive integers (>0) |

### Common SI Units

| Symbol | Unit | Quantity |
|--------|------|----------|
| `m` | metre | Length |
| `kg` | kilogram | Mass |
| `s` | second | Duration |
| `K` | kelvin | Temperature |
| `A` | ampere | Electric current |
| `mol` | mole | Amount of substance |
| `cd` | candela | Luminous intensity |
| `W` | watt | Power |
| `J` | joule | Energy |
| `N` | newton | Force |
| `Pa` | pascal | Pressure |
| `V` | volt | Electric potential |
| `Hz` | hertz | Frequency |
| `T` | tesla | Magnetic flux density |

---
"""


def generate_index_md(
    files: list[Path],
    stdlib_dir: Path,
    syside_version: str,
    generate_summaries: bool = True
) -> str:
    """Generate INDEX.md content with Quick Reference and File Index."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines = []

    # YAML frontmatter
    lines.append("---")
    lines.append(f"syside_version: \"{syside_version}\"")
    lines.append(f"generated: \"{timestamp}\"")
    lines.append(f"total_files: {len(files)}")
    lines.append("---")
    lines.append("")

    # Title
    lines.append("# SysML v2 Standard Library Index")
    lines.append("")
    lines.append("This index provides navigation for the SysML v2 standard library source files.")
    lines.append("Use grep to search for specific functions, types, or units.")
    lines.append("")

    # Quick Reference (hardcoded)
    lines.append(get_quick_reference())

    # File Index (organized by directory)
    lines.append("## File Index")
    lines.append("")

    # Group files by parent directory
    dir_files: dict[str, list[Path]] = {}
    for f in files:
        rel_path = f.relative_to(stdlib_dir)
        parent = str(rel_path.parent)
        if parent not in dir_files:
            dir_files[parent] = []
        dir_files[parent].append(f)

    # Output by directory
    for dir_path in sorted(dir_files.keys()):
        dir_files_list = sorted(dir_files[dir_path], key=lambda p: p.name)

        # Directory header
        lines.append(f"### {dir_path}")
        lines.append("")
        lines.append("| File | Summary |")
        lines.append("|------|---------|")

        for file_path in dir_files_list:
            filename = file_path.name
            if generate_summaries:
                print(f"  Summarizing {filename}...")
                summary = generate_file_summary(file_path)
            else:
                summary = "[dry-run: summary not generated]"
            lines.append(f"| `{filename}` | {summary} |")

        lines.append("")

    return "\n".join(lines)


def generate_version_md(syside_version: str, file_count: int, source_path: Path) -> str:
    """Generate VERSION.md content."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

    return f"""# Standard Library Version

This directory contains a synced copy of the SysML v2 standard library
from the syside package for agent searchability.

| Field | Value |
|-------|-------|
| syside version | {syside_version} |
| Python version | {python_version} |
| Sync timestamp | {timestamp} |
| Files synced | {file_count} |
| Source | `{source_path}` |

## Re-syncing

After upgrading syside, re-sync with:

```bash
python scripts/sync_stdlib.py --force
```

Or check what would be copied:

```bash
python scripts/sync_stdlib.py --dry-run
```
"""


def main():
    parser = argparse.ArgumentParser(
        description="Sync SysML v2 standard library from syside to docs/sysmlv2/stdlib/.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s              # Sync library files and generate INDEX.md
    %(prog)s --dry-run    # Preview what would be done
    %(prog)s --force      # Overwrite existing stdlib directory
        """
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without making changes"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing stdlib directory"
    )

    args = parser.parse_args()

    # Locate syside library
    print("Locating syside package...")
    library_path = get_syside_library_path()
    syside_version = get_syside_version()
    print(f"  Found syside {syside_version} at {library_path}")

    # Check for existing stdlib directory
    if STDLIB_DIR.exists() and not args.force and not args.dry_run:
        print(f"\nError: {STDLIB_DIR} already exists.", file=sys.stderr)
        print("Use --force to overwrite or --dry-run to preview.", file=sys.stderr)
        sys.exit(1)

    # Count/list files
    print("\nScanning library files...")
    files = copy_library_files(library_path, STDLIB_DIR, dry_run=True)
    print(f"  Found {len(files)} files (.kerml, .sysml)")

    if args.dry_run:
        print("\n[DRY-RUN] Would copy the following files:\n")
        for f in files:
            rel_path = f.relative_to(STDLIB_DIR)
            print(f"  {rel_path}")
        print(f"\n[DRY-RUN] Would generate INDEX.md (~200 lines)")
        print(f"[DRY-RUN] Would generate VERSION.md")
        print(f"\nTo perform sync: python scripts/sync_stdlib.py")
        return

    # Remove existing directory if --force
    if STDLIB_DIR.exists() and args.force:
        print(f"\nRemoving existing {STDLIB_DIR}...")
        shutil.rmtree(STDLIB_DIR)

    # Copy files
    print("\nCopying library files...")
    files = copy_library_files(library_path, STDLIB_DIR, dry_run=False)
    print(f"  Copied {len(files)} files")

    # Generate VERSION.md
    print("\nGenerating VERSION.md...")
    version_content = generate_version_md(syside_version, len(files), library_path)
    (STDLIB_DIR / "VERSION.md").write_text(version_content)

    # Generate INDEX.md
    print("\nGenerating INDEX.md with AI summaries (this may take a few minutes)...")
    index_content = generate_index_md(files, STDLIB_DIR, syside_version, generate_summaries=True)
    (STDLIB_DIR / "INDEX.md").write_text(index_content)

    # Summary
    print(f"\nSync complete!")
    print(f"  Files: {len(files)}")
    print(f"  Location: {STDLIB_DIR}/")
    print(f"  INDEX.md: {STDLIB_DIR}/INDEX.md")
    print(f"  VERSION.md: {STDLIB_DIR}/VERSION.md")


if __name__ == "__main__":
    main()
