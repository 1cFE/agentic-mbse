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
    "onboard.md",
    "manage-sources.md",
]

# Agents available for installation
MBSE_AGENTS = [
    "python-debugger.md",
    "sysmlv2-doc-analyzer.md",
]

# Skills available for installation (directories, not files)
MBSE_SKILLS = [
    "python-debugger",
]

# Hooks available for installation
MBSE_HOOKS = [
    "ruff-format.sh",
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


def get_agents_dir() -> Path:
    """Get path to bundled agents directory."""
    package_root = Path(__file__).parent.parent.parent.parent
    return package_root / "claude" / "agents"


def get_skills_dir() -> Path:
    """Get path to bundled skills directory."""
    package_root = Path(__file__).parent.parent.parent.parent
    return package_root / "claude" / "skills"


def get_hooks_dir() -> Path:
    """Get path to bundled hooks directory."""
    package_root = Path(__file__).parent.parent.parent.parent
    return package_root / "claude" / "hooks"


def get_docs_dir() -> Path:
    """Get path to bundled docs directory."""
    package_root = Path(__file__).parent.parent.parent.parent
    return package_root / "docs"

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
    - .claude/commands/ with MBSE commands (including /onboard, /manage-sources)

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
    commands_installed = 0
    for cmd in MBSE_COMMANDS:
        src = source_commands / cmd
        dst = commands_dir / cmd
        if dst.exists() and not args.force:
            print(f"  Skipping (exists): {cmd}")
            continue
        if src.exists():
            shutil.copy(src, dst)
            commands_installed += 1
            print(f"  Installed: {cmd}")
        else:
            print(f"  Warning: Command not found: {cmd}", file=sys.stderr)

    # === Install agents with path substitution ===
    agents_dir = target / ".claude" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created: {agents_dir}")

    docs_path = get_docs_dir()  # Package docs location for substitution
    source_agents = get_agents_dir()
    agents_installed = 0
    for agent in MBSE_AGENTS:
        src = source_agents / agent
        dst = agents_dir / agent
        if dst.exists() and not args.force:
            print(f"  Skipping (exists): {agent}")
            continue
        if src.exists():
            # Read, substitute paths, write
            content = src.read_text()
            content = content.replace("agent_literature/SysML/", f"{docs_path}/sysmlv2/")
            content = content.replace(
                "agent_literature/syside-docs/v0.8.1/", f"{docs_path}/syside/"
            )
            dst.write_text(content)
            agents_installed += 1
            print(f"  Installed: {agent}")
        else:
            print(f"  Warning: Agent not found: {agent}", file=sys.stderr)

    # === Install skills (recursive copy) ===
    skills_dir = target / ".claude" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created: {skills_dir}")

    source_skills = get_skills_dir()
    skills_installed = 0
    for skill in MBSE_SKILLS:
        src = source_skills / skill
        dst = skills_dir / skill
        if dst.exists() and not args.force:
            print(f"  Skipping (exists): {skill}/")
            continue
        if src.exists() and src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            skills_installed += 1
            print(f"  Installed: {skill}/")
        else:
            print(f"  Warning: Skill not found: {skill}", file=sys.stderr)

    # === Install hooks ===
    hooks_dir = target / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created: {hooks_dir}")

    source_hooks = get_hooks_dir()
    hooks_installed = 0
    for hook in MBSE_HOOKS:
        src = source_hooks / hook
        dst = hooks_dir / hook
        if dst.exists() and not args.force:
            print(f"  Skipping (exists): {hook}")
            continue
        if src.exists():
            shutil.copy(src, dst)
            # Preserve executable permission
            dst.chmod(src.stat().st_mode)
            hooks_installed += 1
            print(f"  Installed: {hook}")
        else:
            print(f"  Warning: Hook not found: {hook}", file=sys.stderr)

    print("")
    print(f"Initialized MBSE project in {target}")
    print("  - SOURCE_INDEX.md created (edit to add your domain sources)")
    print(f"  - {commands_installed} commands installed to .claude/commands/")
    print(f"  - {agents_installed} agents installed to .claude/agents/")
    print(f"  - {skills_installed} skills installed to .claude/skills/")
    print(f"  - {hooks_installed} hooks installed to .claude/hooks/")
    print("")
    print("Next steps:")
    print("  1. Run /onboard to configure your project and learn the workflow")
    print("  2. Or manually edit SOURCE_INDEX.md and start with /design-model")

    return EXIT_SUCCESS


def cmd_install_commands(args: argparse.Namespace) -> int:
    """Install MBSE commands to a project.

    Copies MBSE command files to .claude/commands/ in target directory.
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
