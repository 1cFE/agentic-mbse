"""Command-line interface for agentic-mbse."""
import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from agentic_mbse.validation import EXIT_FAILURE, EXIT_SUCCESS, run_all_checks

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
    """Initialize project with agentic-mbse configuration."""
    target = Path(args.path or ".")

    # Create .agentic-mbse.yaml
    config_path = target / ".agentic-mbse.yaml"
    if config_path.exists() and not args.force:
        print(f"Config already exists: {config_path}")
        print("Use --force to overwrite")
        return EXIT_FAILURE

    config_content = '''# agentic-mbse configuration
project:
  name: "my-project"
  description: "MBSE project using agentic-mbse"

models:
  library_paths:
    - "models/library"
  design_paths:
    - "models/designs"

validation:
  levels: [1, 2, 3, 4, 5, 6, 7, 8]
  baseline_tool: null

codegen:
  output_package: "my_simkit"

domain_context:
  reference_tool: null
  reference_path: null
'''
    config_path.write_text(config_content)
    print(f"Created {config_path}")

    # Create .claude/commands/ directory
    claude_dir = target / ".claude" / "commands"
    claude_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created {claude_dir}")

    print("Run 'agentic-mbse install-commands' to install Claude commands")

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
        help="Initialize project with agentic-mbse configuration",
    )
    init_parser.add_argument(
        "path",
        nargs="?",
        help="Target directory (default: current directory)",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing configuration",
    )
    init_parser.set_defaults(func=cmd_init)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return EXIT_SUCCESS

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
