"""Command-line interface for agentic-mbse."""
import argparse
import json
import platform
import shutil
import sys
import tomllib
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
    "backlog.md",
]

# Agents available for installation
MBSE_AGENTS = [
    "python-debugger.md",
    "kerml-expert.md",
    "sysml-expert.md",
    "syside-expert.md",
    "sysmlv2-validator.md",
]

# Skills available for installation (directories, not files)
MBSE_SKILLS = [
    "python-debugger",
]

# Hooks available for installation
MBSE_HOOKS = [
    "ruff-format.sh",
]

# Project templates split by ownership:
# - USER_OWNED: Only created once, never auto-updated (user customizes these)
# - TOOL_OWNED: Auto-updated on every init (tool manages these)
USER_OWNED_TEMPLATES = [
    ("README.md.template", "README.md"),
    ("OVERVIEW.md.template", "project/OVERVIEW.md"),
    ("BACKLOG.md.template", "project/backlog/BACKLOG.md"),
]

TOOL_OWNED_TEMPLATES = [
    ("MODELING_GUIDE.md.template", "project/MODELING_GUIDE.md"),
    ("MODELING_PROCESS.md.template", "project/MODELING_PROCESS.md"),
]

# Combined for backwards compatibility
PROJECT_TEMPLATES = USER_OWNED_TEMPLATES + TOOL_OWNED_TEMPLATES

# Paths to add to .gitignore in dev mode (symlinks are machine-specific)
DEV_MODE_GITIGNORE_PATHS = [
    "# Tool-owned files (managed by agentic-mbse init --dev)",
    ".claude/commands/",
    ".claude/agents/",
    ".claude/skills/",
    ".claude/hooks/",
    "project/MODELING_GUIDE.md",
    "project/MODELING_PROCESS.md",
]


def _get_data_root() -> Path:
    """Get root path for bundled data (claude/, docs/, templates).

    Supports two installation modes:
    1. Source checkout: agentic-mbse/src/agentic_mbse/cli/__init__.py
       → Data at: agentic-mbse/claude/, agentic-mbse/docs/
    2. Pip install: site-packages/agentic_mbse/cli/__init__.py
       → Data at: site-packages/agentic_mbse_data/claude/, etc.
    """
    # Try source checkout path first (development mode)
    source_root = Path(__file__).parent.parent.parent.parent
    if (source_root / "claude").exists():
        return source_root

    # Fallback to pip-installed package data location
    pip_data_root = Path(__file__).parent.parent.parent / "agentic_mbse_data"
    if pip_data_root.exists():
        return pip_data_root

    # Last resort: return source root and let caller handle missing files
    return source_root


def get_commands_dir() -> Path:
    """Get path to bundled commands directory."""
    return _get_data_root() / "claude" / "commands"


def get_template_path() -> Path:
    """Get path to SOURCE_INDEX.md template."""
    return _get_data_root() / "SOURCE_INDEX.md.template"


def get_agents_dir() -> Path:
    """Get path to bundled agents directory."""
    return _get_data_root() / "claude" / "agents"


def get_skills_dir() -> Path:
    """Get path to bundled skills directory."""
    return _get_data_root() / "claude" / "skills"


def get_hooks_dir() -> Path:
    """Get path to bundled hooks directory."""
    return _get_data_root() / "claude" / "hooks"


def get_docs_dir() -> Path:
    """Get path to bundled docs directory."""
    return _get_data_root() / "docs"


def get_project_templates_dir() -> Path:
    """Get path to bundled project templates directory."""
    return _get_data_root() / "project_templates"


def _to_claude_permission_path(abs_path: str) -> str:
    """Convert absolute path to Claude Code permission format.

    Claude Code permission paths are format-sensitive:
    - `/path` = relative to settings.json (NOT absolute!)
    - `//path` = absolute filesystem path
    - `~/path` = from $HOME

    This function converts absolute paths to `~` format when under $HOME
    for portability, or `//` prefix otherwise.
    """
    import os

    home = os.path.expanduser("~")
    if abs_path.startswith(home + "/"):
        # Convert /home/user/foo to ~/foo
        return "~" + abs_path[len(home):]
    elif abs_path == home:
        return "~"
    else:
        # Use / prefix for absolute paths not under home
        # (Claude interprets //path as absolute filesystem path)
        return "/" + abs_path


def _detect_editable_deps(target: Path) -> list[str]:
    """Detect editable dependencies from pyproject.toml.

    Parses [tool.uv.sources] section to find editable paths.
    Returns list of absolute paths that should be added to Claude settings.
    """
    pyproject = target / "pyproject.toml"
    if not pyproject.exists():
        return []

    try:
        data = tomllib.loads(pyproject.read_text())
        sources = data.get("tool", {}).get("uv", {}).get("sources", {})
        paths = []
        for _name, config in sources.items():
            if isinstance(config, dict) and config.get("editable"):
                rel_path = config.get("path", "")
                if rel_path:
                    abs_path = (target / rel_path).resolve()
                    if abs_path.exists():
                        paths.append(str(abs_path))
        return paths
    except Exception:
        return []


def _check_dev_mode_prerequisites(data_root: Path) -> tuple[bool, str | None]:
    """Check if dev mode can be used.

    Returns:
        (can_use, error_message) - error_message is None if can_use is True
    """
    # Check Windows
    if platform.system() == "Windows":
        return False, "Dev mode is not supported on Windows (symlinks require admin privileges)"

    # Check source checkout (claude/ directory exists at root)
    if not (data_root / "claude").exists():
        return False, (
            "Dev mode requires a source checkout of agentic-mbse.\n"
            "Pip-installed packages cannot use dev mode.\n"
            "Clone the repo and install with: pip install -e /path/to/agentic-mbse"
        )

    return True, None


def _install_file(src: Path, dst: Path, is_dev_mode: bool) -> str:
    """Install a file by copying or symlinking.

    Args:
        src: Source file path
        dst: Destination file path
        is_dev_mode: If True, create symlink; if False, copy

    Returns:
        Action taken: "created", "updated", "symlinked", or "re-symlinked"
    """
    existed = dst.exists() or dst.is_symlink()

    # Remove existing file or symlink before creating new one
    if existed:
        dst.unlink()

    if is_dev_mode:
        dst.symlink_to(src.resolve())
        return "re-symlinked" if existed else "symlinked"
    else:
        shutil.copy(src, dst)
        return "updated" if existed else "created"


def _install_directory(src: Path, dst: Path, is_dev_mode: bool) -> str:
    """Install a directory by copying or symlinking.

    Args:
        src: Source directory path
        dst: Destination directory path
        is_dev_mode: If True, create symlink; if False, copy tree

    Returns:
        Action taken: "created", "updated", "symlinked", or "re-symlinked"
    """
    existed = dst.exists() or dst.is_symlink()

    if existed:
        if dst.is_symlink():
            dst.unlink()
        else:
            shutil.rmtree(dst)

    if is_dev_mode:
        dst.symlink_to(src.resolve())
        return "re-symlinked" if existed else "symlinked"
    else:
        shutil.copytree(src, dst, dirs_exist_ok=True)
        return "updated" if existed else "created"


def _update_gitignore_for_dev_mode(target: Path) -> bool:
    """Add tool-owned paths to .gitignore for dev mode.

    Symlinks use absolute paths pointing to developer's local agentic-mbse
    checkout. If committed to git, other developers would have broken symlinks.
    This function adds tool-owned paths to .gitignore to prevent that.

    Returns True if .gitignore was modified, False if paths already present.
    """
    gitignore_path = target / ".gitignore"

    # Read existing content
    existing_content = ""
    if gitignore_path.exists():
        existing_content = gitignore_path.read_text()

    # Check if already has dev mode section (idempotent)
    marker = DEV_MODE_GITIGNORE_PATHS[0]
    if marker in existing_content:
        return False

    # Append dev mode paths
    new_section = "\n" + "\n".join(DEV_MODE_GITIGNORE_PATHS) + "\n"
    gitignore_path.write_text(existing_content.rstrip() + new_section)
    return True


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
    - .gitignore (standard Python ignores including .env) [user-owned]
    - SOURCE_INDEX.md (domain knowledge discovery for agents) [user-owned]
    - .claude/commands/ with MBSE commands [tool-owned]
    - .claude/agents/ with AI agents [tool-owned]
    - .claude/skills/ with skills [tool-owned]
    - .claude/hooks/ with hooks [tool-owned]
    - .claude/settings.json with read permissions [user-owned]
    - project/ structure with templates [mixed ownership]

    File ownership behavior:
    - Tool-owned files are always updated (to get latest versions)
    - User-owned files are skipped if they exist (preserves customizations)

    Use --force to overwrite ALL files including user-owned ones.
    """
    target = Path(args.path or ".").resolve()

    if not target.exists():
        print(f"Error: Directory does not exist: {target}", file=sys.stderr)
        print("Create the directory first, or specify a valid path.", file=sys.stderr)
        return EXIT_FAILURE

    # Check dev mode prerequisites
    is_dev_mode = getattr(args, "dev", False)
    data_root = _get_data_root()

    if is_dev_mode:
        can_use, error_msg = _check_dev_mode_prerequisites(data_root)
        if not can_use:
            print(f"Error: {error_msg}", file=sys.stderr)
            return EXIT_FAILURE

    # Track what happens for summary
    created: list[str] = []    # New files (didn't exist before)
    updated: list[str] = []    # Tool-owned files refreshed
    skipped: list[str] = []    # User-owned files preserved
    symlinked: list[str] = []  # Dev mode symlinks

    # === Create .gitignore with standard Python ignores ===
    gitignore_path = target / ".gitignore"
    if gitignore_path.exists() and not args.force:
        skipped.append(".gitignore")
    else:
        gitignore_content = """\
# Environment and secrets
.env
.env.*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.venv/
venv/
ENV/

# Testing and coverage
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/

# Type checking
.mypy_cache/

# Linting
.ruff_cache/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""
        gitignore_path.write_text(gitignore_content)
        created.append(".gitignore")

    # === Create SOURCE_INDEX.md from template ===
    source_index_path = target / "SOURCE_INDEX.md"
    template_path = get_template_path()

    if source_index_path.exists() and not args.force:
        skipped.append("SOURCE_INDEX.md")
    else:
        if template_path.exists():
            shutil.copy(template_path, source_index_path)
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
        created.append("SOURCE_INDEX.md")

    # === Create .claude/commands/ and install commands (TOOL-OWNED) ===
    commands_dir = target / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    source_commands = get_commands_dir()
    for cmd in MBSE_COMMANDS:
        src = source_commands / cmd
        dst = commands_dir / cmd
        if src.exists():
            action = _install_file(src, dst, is_dev_mode)
            if "symlink" in action:
                symlinked.append(f".claude/commands/{cmd}")
            elif action == "updated":
                updated.append(f".claude/commands/{cmd}")
            else:
                created.append(f".claude/commands/{cmd}")

    # === Install agents with path substitution (TOOL-OWNED) ===
    agents_dir = target / ".claude" / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    docs_path = get_docs_dir()
    source_agents = get_agents_dir()
    for agent in MBSE_AGENTS:
        src = source_agents / agent
        dst = agents_dir / agent
        if src.exists():
            if is_dev_mode:
                # Symlink directly - placeholders remain in source
                action = _install_file(src, dst, is_dev_mode=True)
                symlinked.append(f".claude/agents/{agent}")
            else:
                # Copy with placeholder substitution
                existed = dst.exists() or dst.is_symlink()
                if existed:
                    dst.unlink()
                content = src.read_text()
                content = content.replace("{SYSML_DOCS_PATH}", f"{docs_path}/sysmlv2")
                content = content.replace("{SYSIDE_DOCS_PATH}", f"{docs_path}/syside")
                dst.write_text(content)
                if existed:
                    updated.append(f".claude/agents/{agent}")
                else:
                    created.append(f".claude/agents/{agent}")

    # === Install skills (TOOL-OWNED) ===
    skills_dir = target / ".claude" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    source_skills = get_skills_dir()
    for skill in MBSE_SKILLS:
        src = source_skills / skill
        dst = skills_dir / skill
        if src.exists() and src.is_dir():
            action = _install_directory(src, dst, is_dev_mode)
            if "symlink" in action:
                symlinked.append(f".claude/skills/{skill}/")
            elif action == "updated":
                updated.append(f".claude/skills/{skill}/")
            else:
                created.append(f".claude/skills/{skill}/")

    # === Install hooks (TOOL-OWNED) ===
    hooks_dir = target / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    source_hooks = get_hooks_dir()
    for hook in MBSE_HOOKS:
        src = source_hooks / hook
        dst = hooks_dir / hook
        if src.exists():
            action = _install_file(src, dst, is_dev_mode)
            # Preserve execute permission (symlinks inherit from target)
            if not is_dev_mode:
                dst.chmod(src.stat().st_mode)
            if "symlink" in action:
                symlinked.append(f".claude/hooks/{hook}")
            elif action == "updated":
                updated.append(f".claude/hooks/{hook}")
            else:
                created.append(f".claude/hooks/{hook}")

    # === Create project/ structure ===
    project_dir = target / "project"
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "backlog").mkdir(exist_ok=True)
    (project_dir / "active").mkdir(exist_ok=True)
    (project_dir / "research").mkdir(exist_ok=True)

    templates_dir = get_project_templates_dir()

    # === User-owned templates (skip if exists) ===
    for template_name, dest_path in USER_OWNED_TEMPLATES:
        src = templates_dir / template_name
        dst = target / dest_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and not args.force:
            skipped.append(dest_path)
            continue
        if src.exists():
            shutil.copy(src, dst)
            created.append(dest_path)

    # === Tool-owned templates (always update) ===
    for template_name, dest_path in TOOL_OWNED_TEMPLATES:
        src = templates_dir / template_name
        dst = target / dest_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.exists():
            action = _install_file(src, dst, is_dev_mode)
            if "symlink" in action:
                symlinked.append(dest_path)
            elif action == "updated":
                updated.append(dest_path)
            else:
                created.append(dest_path)

    # === Create .claude/settings.json with permissions (USER-OWNED) ===
    settings_path = target / ".claude" / "settings.json"

    if settings_path.exists() and not args.force:
        skipped.append(".claude/settings.json")
    else:
        permissions: list[str] = []

        # Add permissions for bundled docs (used by sysmlv2-doc-analyzer agent)
        docs_permission_path = _to_claude_permission_path(str(docs_path))
        permissions.extend([
            f"Read({docs_permission_path}/**)",
            f"Grep({docs_permission_path}/**)",
            f"Glob({docs_permission_path}/**)",
        ])

        # Add permissions for editable dependencies from pyproject.toml
        editable_paths = _detect_editable_deps(target)
        for p in editable_paths:
            permissions.append(f"Read({_to_claude_permission_path(p)}/**)")

        settings = {"permissions": {"allow": permissions}}
        settings_path.write_text(json.dumps(settings, indent=2) + "\n")
        created.append(f".claude/settings.json ({len(permissions)} permissions)")

    # === Update .gitignore for dev mode ===
    if is_dev_mode:
        if _update_gitignore_for_dev_mode(target):
            updated.append(".gitignore (added dev mode paths)")

    # === Print summary ===
    if is_dev_mode:
        print(f"\nInitialized MBSE project in {target} (dev mode)")
    else:
        print(f"\nInitialized MBSE project in {target}")
    print("")

    if symlinked:
        print(f"Symlinked ({len(symlinked)}) - dev mode, points to source:")
        for item in symlinked:
            print(f"  @ {item}")

    if created:
        print(f"\nCreated ({len(created)}):")
        for item in created:
            print(f"  + {item}")

    if updated:
        print(f"\nUpdated ({len(updated)}) - tool-managed files refreshed:")
        for item in updated:
            print(f"  ~ {item}")

    if skipped:
        print(f"\nSkipped ({len(skipped)}) - user files preserved:")
        for item in skipped:
            print(f"  . {item}")

    if not created and not updated and not symlinked:
        print("Everything up to date.")
    elif created or updated or symlinked:
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
        help="Overwrite ALL files including user-owned ones (SOURCE_INDEX.md, OVERVIEW.md, settings.json, etc.)",
    )
    init_parser.add_argument(
        "--dev",
        action="store_true",
        help="Development mode: symlink tool-owned files instead of copying (requires source checkout)",
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
