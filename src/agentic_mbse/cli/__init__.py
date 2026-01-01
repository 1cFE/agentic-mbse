"""Command-line interface for agentic-mbse."""
import argparse
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv

from agentic_mbse.validation import EXIT_FAILURE, EXIT_SUCCESS, run_all_checks

# Commands available for installation
MBSE_COMMANDS = [
    "design-model.md",
    "plan-model.md",
    "implement-model.md",
    "spec-model.md",
    "research.md",
    "audit-models.md",
]


def get_commands_dir() -> Path:
    """Get path to bundled commands directory.

    Path calculation:
    - __file__ = agentic-mbse/src/agentic_mbse/cli/__init__.py
    - parent.parent.parent.parent = agentic-mbse/
    - result = agentic-mbse/claude/commands/
    """
    package_root = Path(__file__).parent.parent.parent.parent
    return package_root / "claude" / "commands"


def get_template_path() -> Path:
    """Get path to SOURCE_INDEX.md template."""
    package_root = Path(__file__).parent.parent.parent.parent
    return package_root / "SOURCE_INDEX.md.template"

# Load environment variables from .env file (for SYSIDE_LICENSE_KEY, etc.)
load_dotenv()

__all__ = ["main"]


def cmd_validate(args: argparse.Namespace) -> int:
    """Run validation on models."""
    if not Path(args.path).exists():
        print(f"Error: Path does not exist: {args.path}")
        return EXIT_FAILURE

    result = run_all_checks(
        models_path=args.path,
        fail_fast=not args.complete,
        specific_level=args.level,
        verbose=args.verbose,
    )
    return EXIT_SUCCESS if result.overall_success else EXIT_FAILURE


def cmd_init(args: argparse.Namespace) -> int:
    """Initialize project with agentic-mbse configuration.

    Creates:
    - SOURCE_INDEX.md (domain knowledge discovery for agents)
    - .claude/commands/ with 6 MBSE commands

    NOTE: Does NOT create .agentic-mbse.yaml - that config was over-engineered.
    SOURCE_INDEX.md is the single source of domain knowledge.
    """
    target = Path(args.path or ".").resolve()

    if not target.exists():
        print(f"Error: Directory does not exist: {target}", file=sys.stderr)
        print("Create the directory first, or specify a valid path.", file=sys.stderr)
        return EXIT_FAILURE

    # === Create SOURCE_INDEX.md from template ===
    source_index_path = target / "SOURCE_INDEX.md"
    template_path = get_template_path()

    if source_index_path.exists() and not args.force:
        print(f"SOURCE_INDEX.md already exists at {source_index_path}")
        print("Use --force to overwrite")
    else:
        if template_path.exists():
            shutil.copy(template_path, source_index_path)
            print(f"Created: {source_index_path}")
        else:
            # Fallback: create minimal template inline
            minimal_template = """# Source Index

This file tells MBSE commands where to find domain knowledge sources.

## Primary Sources

(No primary sources configured yet - commands will ask for references as needed)

## How This File Is Used

MBSE commands read this file to discover what reference sources exist.
Edit this file to add your domain-specific sources.
"""
            source_index_path.write_text(minimal_template)
            print(f"Created: {source_index_path} (from fallback template)")

    # === Create .claude/commands/ and install commands ===
    commands_dir = target / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created: {commands_dir}")

    # Copy commands
    source_commands = get_commands_dir()
    installed = 0
    for cmd in MBSE_COMMANDS:
        src = source_commands / cmd
        dst = commands_dir / cmd
        if dst.exists() and not args.force:
            print(f"  Skipping (exists): {cmd}")
            continue
        if src.exists():
            shutil.copy(src, dst)
            installed += 1
            print(f"  Installed: {cmd}")
        else:
            print(f"  Warning: Command not found: {cmd}", file=sys.stderr)

    print("")
    print(f"Initialized MBSE project in {target}")
    print("  - SOURCE_INDEX.md created (edit to add your domain sources)")
    print(f"  - {installed} commands installed to .claude/commands/")
    print("")
    print("Next steps:")
    print("  1. Edit SOURCE_INDEX.md to add your reference sources")
    print("  2. Run Claude Code with /design-model to start modeling")

    return EXIT_SUCCESS


def cmd_install_commands(args: argparse.Namespace) -> int:
    """Install MBSE commands to a project.

    Copies the 6 MBSE command files to .claude/commands/ in target directory.
    """
    if args.list:
        print("Available MBSE commands:")
        for cmd in MBSE_COMMANDS:
            print(f"  - {cmd}")
        print("")
        print(f"Total: {len(MBSE_COMMANDS)} commands")
        return EXIT_SUCCESS

    target_dir = Path(args.directory).resolve()
    if not target_dir.exists():
        print(f"Error: Directory does not exist: {args.directory}", file=sys.stderr)
        return EXIT_FAILURE

    commands_target = target_dir / ".claude" / "commands"
    commands_target.mkdir(parents=True, exist_ok=True)

    source_commands = get_commands_dir()
    installed = 0
    skipped = 0

    for cmd in MBSE_COMMANDS:
        src = source_commands / cmd
        dst = commands_target / cmd

        if not src.exists():
            print(f"Warning: Source not found: {cmd}", file=sys.stderr)
            continue

        if dst.exists() and not args.force:
            print(f"Skipping (exists): {cmd} (use --force to overwrite)")
            skipped += 1
            continue

        shutil.copy(src, dst)
        print(f"Installed: {cmd}")
        installed += 1

    print("")
    print(f"Installed: {installed}, Skipped: {skipped}")
    return EXIT_SUCCESS


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="agentic-mbse",
        description="Domain-agnostic MBSE toolkit for AI-assisted systems engineering",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Run quality validation on SysML models",
    )
    validate_parser.add_argument(
        "path",
        nargs="?",
        default="models",
        help="Path to models directory (default: models)",
    )
    validate_parser.add_argument(
        "--complete",
        action="store_true",
        help="Run all levels regardless of failures",
    )
    validate_parser.add_argument(
        "--level",
        type=int,
        choices=range(1, 9),
        metavar="N",
        help="Run only level N (1-8)",
    )
    validate_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output",
    )
    validate_parser.set_defaults(func=cmd_validate)

    # init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize project with SOURCE_INDEX.md and .claude/commands/",
    )
    init_parser.add_argument(
        "path",
        nargs="?",
        help="Target directory (default: current directory)",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing SOURCE_INDEX.md and commands",
    )
    init_parser.set_defaults(func=cmd_init)

    # install-commands command
    install_parser = subparsers.add_parser(
        "install-commands",
        help="Install MBSE commands to a project",
    )
    install_parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Target directory (default: current directory)",
    )
    install_parser.add_argument(
        "--list",
        action="store_true",
        help="List available commands without installing",
    )
    install_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing command files",
    )
    install_parser.set_defaults(func=cmd_install_commands)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return EXIT_SUCCESS

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
