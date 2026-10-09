"""Command-line interface for agentic-mbse."""

import argparse
import json
import platform
import shutil
import sys
from collections.abc import Callable
from pathlib import Path

import tomllib
from dotenv import load_dotenv

from agentic_mbse.cli.installation import (
    MANIFEST,
    Installer,
    bundle_kind,
    install_assistants,
    is_source_checkout,
    skill_bundles,
)
from agentic_mbse.validation import EXIT_FAILURE, EXIT_SUCCESS, run_all_checks

# Project templates split by ownership:
# - USER_OWNED: Only created once, never auto-updated (user customizes these)
# - TOOL_OWNED: Auto-updated on every init (tool manages these)
USER_OWNED_TEMPLATES = [
    ("README.md.template", "README.md"),
    ("OVERVIEW.md.template", "modeling_project/OVERVIEW.md"),
    ("BACKLOG.md.template", "work/BACKLOG.md"),
    ("RAW_LEARNINGS.md.template", "work/learnings/RAW_LEARNINGS.md"),
    ("KNOWLEDGE.md.template", "knowledge/KNOWLEDGE.md"),
    ("ARCHITECTURE.md.template", "modeling_project/ARCHITECTURE.md"),
    ("REQUIREMENTS.md.template", "modeling_project/REQUIREMENTS.md"),
    ("VALIDATION_MATRIX.md.template", "modeling_project/VALIDATION_MATRIX.md"),
    ("test_models_example.py.template", "tests/models/test_example.py"),
    ("conftest.py.template", "tests/conftest.py"),
]

TOOL_OWNED_TEMPLATES = [
    ("MODELING_GUIDE.md.template", "modeling_project/MODELING_GUIDE.md"),
    ("MODELING_PROCESS.md.template", "modeling_project/MODELING_PROCESS.md"),
    ("EPIC_GUIDE.md.template", "work/EPIC_GUIDE.md"),
    ("epic_template.md.template", "work/backlog/epic_template.md"),
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
    ".claude/.tool-hashes.json",
    ".agents/skills/",
    ".codex/agents/",
    ".agentic-mbse/",
    "modeling_project/MODELING_GUIDE.md",
    "modeling_project/MODELING_PROCESS.md",
    "work/EPIC_GUIDE.md",
    "work/backlog/epic_template.md",
]

# Hash file for tracking tool-owned file modifications
HASH_FILE = MANIFEST

# --dev links each bundle file to the source checkout; Codex 0.160 lists none of those skills.
DEV_CODEX_WARNING = (
    "Warning: Codex does not list skills that --dev installs as links to the source checkout, "
    "so the MBSE skills are not available in Codex here. Use plain `agentic-mbse init` "
    "(without --dev) for Codex. Claude Code is not affected."
)


def _get_data_root() -> Path:
    """Get root path for bundled data (skills/, agents/, hooks/, docs/, templates).

    Supports two installation modes:
    1. Source checkout: agentic-mbse/src/agentic_mbse/cli/__init__.py
       → Data at: agentic-mbse/skills/, agentic-mbse/docs/
    2. Pip install: site-packages/agentic_mbse/cli/__init__.py
       → Data at: site-packages/agentic_mbse_data/skills/, etc.
    """
    source_root = Path(__file__).parent.parent.parent.parent
    if is_source_checkout(source_root):
        return source_root
    pip_data_root = Path(__file__).parent.parent.parent / "agentic_mbse_data"
    if pip_data_root.is_dir():
        return pip_data_root
    raise FileNotFoundError(
        f"agentic-mbse data not found: {source_root} is not a source checkout "
        f"and {pip_data_root} does not exist"
    )


def get_template_path() -> Path:
    """Get path to SOURCE_INDEX.md template."""
    return _get_data_root() / "SOURCE_INDEX.md.template"


def get_agents_dir() -> Path:
    """Get path to bundled agents directory."""
    return _get_data_root() / "agents"


def get_skills_dir() -> Path:
    """Get path to bundled skills directory."""
    return _get_data_root() / "skills"


def get_hooks_dir() -> Path:
    """Get path to bundled hooks directory."""
    return _get_data_root() / "hooks"


def get_docs_dir() -> Path:
    """Get path to bundled docs directory."""
    return _get_data_root() / "docs"


def get_project_templates_dir() -> Path:
    """Get path to bundled project templates directory."""
    return _get_data_root() / "project_templates"


def find_project_root() -> Path | None:
    """Walk up from CWD to find a project root.

    Looks for work/BACKLOG.md, the native install manifest, or legacy .claude/.
    Returns None if neither found.
    """
    current = Path.cwd()
    while True:
        if (current / "work" / "BACKLOG.md").exists():
            return current
        if (current / MANIFEST).is_file() or (current / ".claude").is_dir():
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent


def cmd_status(args) -> int:
    """Show project status dashboard."""
    from agentic_mbse.cli.pm_cli import _print_warnings

    project_root = find_project_root()
    if project_root is None:
        print(
            "Error: Not inside a project (no work/BACKLOG.md found)",
            file=sys.stderr,
        )
        return EXIT_FAILURE

    if args.json_output:
        from agentic_mbse.pm.parser import parse_requirements, parse_validation_matrix
        from agentic_mbse.pm.state import derive_project_state

        warnings = []
        state_result = derive_project_state(project_root)
        warnings.extend(state_result.warnings)
        req_result = parse_requirements(project_root / "modeling_project" / "REQUIREMENTS.md")
        warnings.extend(req_result.warnings)
        val_result = parse_validation_matrix(
            project_root / "modeling_project" / "VALIDATION_MATRIX.md"
        )
        warnings.extend(val_result.warnings)

        _print_warnings(warnings)

        output = {
            "project": project_root.name,
            "state": state_result.data.model_dump(mode="json"),
            "requirements": [r.model_dump(mode="json") for r in req_result.data],
            "validation": [v.model_dump(mode="json") for v in val_result.data],
        }
        print(json.dumps(output, indent=2))
    else:
        from agentic_mbse.pm.dashboard import generate_dashboard

        result = generate_dashboard(project_root)
        _print_warnings(result.warnings)
        print(result.markdown)

    return EXIT_SUCCESS


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
        return "~" + abs_path[len(home) :]
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

    if not is_source_checkout(data_root):
        return False, (
            "Dev mode requires a source checkout of agentic-mbse.\n"
            "Pip-installed packages cannot use dev mode.\n"
            "Clone the repo and install with: pip install -e /path/to/agentic-mbse"
        )

    return True, None


def _prompt_for_modified_file(path: str) -> str:
    """Prompt user for action on modified file.

    Returns: 'skip', 'backup', 'overwrite', 'skip_all', 'overwrite_all'
    """
    print(f"\nModified: {path}")
    print("  This file has local modifications that will be lost if updated.")
    print("  Options:")
    print("    [s]kip      - Keep your version")
    print("    [b]ackup    - Save to .backup, then update")
    print("    [o]verwrite - Replace with new version")
    print("    [S]kip all  - Skip all modified files")
    print("    [O]verwrite all - Update all (like --force)")

    while True:
        choice = input("  Choice [s/b/o/S/O]: ").strip()
        if choice == "s":
            return "skip"
        elif choice == "b":
            return "backup"
        elif choice == "o":
            return "overwrite"
        elif choice == "S":
            return "skip_all"
        elif choice == "O":
            return "overwrite_all"
        else:
            print("  Invalid choice. Please enter s, b, o, S, or O.")


def _update_gitignore_for_dev_mode(target: Path) -> bool:
    """Add tool-owned paths to .gitignore for dev mode.

    Symlinks use absolute paths pointing to developer's local agentic-mbse
    checkout. If committed to git, other developers would have broken symlinks.
    This function adds tool-owned paths to .gitignore to prevent that.

    Returns True if .gitignore was modified, False if paths already present.
    """
    gitignore_path = target / ".gitignore"

    if gitignore_path.is_symlink():
        print("Preserved symlinked .gitignore; add dev-mode ignore paths manually")
        return False

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
    - knowledge/SOURCE_INDEX.md (domain knowledge discovery) [user-owned]
    - knowledge/KNOWLEDGE.md (domain insight registry) [user-owned]
    - modeling_project/ structure (OVERVIEW, ARCHITECTURE, REQUIREMENTS, etc.) [mixed]
    - work/ structure (BACKLOG, EPIC_GUIDE, epic template, active, completed, etc.) [mixed]
    - data/traceability_matrix.csv (element traceability) [user-owned]
    - .agents/skills/ with shared workflows and supporting resources [managed]
    - Native expert roles and entry instructions for selected assistants [managed]
    - .claude/skills/ with skills [tool-owned]
    - .claude/hooks/ with hooks [tool-owned]
    - .claude/settings.json with read permissions [user-owned]
    - tests/ structure with example test files [user-owned]

    File ownership behavior:
    - Managed files update when unmodified; local edits are preserved or prompt
    - User-owned files are skipped if they exist (preserves customizations)

    Use --force to replace files; existing native instructions and settings remain owner-owned.
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

    assistant = getattr(args, "assistant", "both")
    link_mode = getattr(args, "link_mode", "symlink")

    def decide(path: str) -> str:
        if not sys.stdin.isatty():
            print(f"Preserving modified or untracked file: {path} (use --force to replace)")
            return "skip"
        return _prompt_for_modified_file(path)

    installer = Installer(target, force=args.force, decide=decide)
    # The installer owns the action lists; project templates contribute to the same summary.
    created = installer.actions["created"]
    updated = installer.actions["updated"]
    skipped = installer.actions["skipped"]
    symlinked = installer.actions["symlinked"]
    backed_up = installer.actions["backed_up"]
    removed = installer.actions["removed"]
    adopted = installer.adopted

    # === Create .gitignore with standard Python ignores ===
    gitignore_path = target / ".gitignore"
    if (gitignore_path.exists() or gitignore_path.is_symlink()) and not args.force:
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

# agentic-mbse tool state (machine-local)
.agentic-mbse/install.json
"""
        if gitignore_path.is_symlink():
            gitignore_path.unlink()
        gitignore_path.write_text(gitignore_content)
        created.append(".gitignore")

    # === Create knowledge/SOURCE_INDEX.md from template ===
    source_index_path = target / "knowledge" / "SOURCE_INDEX.md"
    template_path = get_template_path()

    if (source_index_path.exists() or source_index_path.is_symlink()) and not args.force:
        skipped.append("knowledge/SOURCE_INDEX.md")
    else:
        if not installer.parents("knowledge/SOURCE_INDEX.md"):
            return EXIT_FAILURE
        if source_index_path.is_symlink():
            source_index_path.unlink()
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
        created.append("knowledge/SOURCE_INDEX.md")

    install_assistants(
        installer, data_root, assistant=assistant, link_mode=link_mode, dev=is_dev_mode
    )
    docs_path = get_docs_dir()

    # === Create project structure (4-directory architecture) ===
    for subdir in [
        "knowledge",
        "knowledge/research/pending",
        "knowledge/research/approved",
        "knowledge/research/impacts",
        "knowledge/sources",
        "modeling_project",
        "modeling_project/intent",
        "work",
        "work/backlog",
        "work/active",
        "work/completed",
        "work/analysis",
        "work/learnings",
        "data",
        "models/library",
        "models/designs",
    ]:
        installer.parents(subdir + "/.directory")

    # === Create tests/models/ directory for model regression tests ===
    installer.parents("tests/models/.directory")

    templates_dir = get_project_templates_dir()

    # === User-owned templates (skip if exists) ===
    for template_name, dest_path in USER_OWNED_TEMPLATES:
        src = templates_dir / template_name
        dst = target / dest_path
        if not installer.parents(dest_path):
            continue
        if (dst.exists() or dst.is_symlink()) and not args.force:
            skipped.append(dest_path)
            continue
        if src.exists():
            if dst.is_symlink():
                dst.unlink()
            shutil.copy(src, dst)
            created.append(dest_path)

    # === Install traceability matrix CSV (USER-OWNED) ===
    csv_src = templates_dir / "data" / "traceability_matrix.csv"
    csv_dst = target / "data" / "traceability_matrix.csv"
    if (csv_dst.exists() or csv_dst.is_symlink()) and not args.force:
        skipped.append("data/traceability_matrix.csv")
    elif csv_src.exists() and installer.parents("data/traceability_matrix.csv"):
        if csv_dst.is_symlink():
            csv_dst.unlink()
        shutil.copy(csv_src, csv_dst)
        created.append("data/traceability_matrix.csv")

    # === Tool-owned templates use the shared ownership policy ===
    for template_name, dest_path in TOOL_OWNED_TEMPLATES:
        src = templates_dir / template_name
        if src.exists():
            installer.write(dest_path, src.read_bytes(), source=src, dev=is_dev_mode)

    # === Create .claude/settings.json with permissions (USER-OWNED) ===
    settings_path = target / ".claude" / "settings.json"

    if assistant in ("claude", "both") and installer.parents(".claude/settings.json"):
        if settings_path.exists() or settings_path.is_symlink():
            skipped.append(".claude/settings.json")
        else:
            permissions: list[str] = []

            # Add permissions for bundled docs (used by specialist agents)
            docs_permission_path = _to_claude_permission_path(str(docs_path))
            permissions.extend(
                [
                    f"Read({docs_permission_path}/**)",
                    f"Grep({docs_permission_path}/**)",
                    f"Glob({docs_permission_path}/**)",
                ]
            )

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

    installer.save()

    # === Print summary ===
    if is_dev_mode:
        print(f"\nInitialized MBSE project in {target} (dev mode)")
    else:
        print(f"\nInitialized MBSE project in {target}")
    print("")

    if symlinked:
        print(f"Symlinked ({len(symlinked)}):")
        for item in symlinked:
            print(f"  @ {item}")

    if adopted:
        print(f"\nAdopted ({len(adopted)}) - links from the pre-native installer replaced:")
        for item, old in adopted.items():
            print(f"  A {item} (was -> {old})")

    if created:
        print(f"\nCreated ({len(created)}):")
        for item in created:
            print(f"  + {item}")

    if updated:
        print(f"\nUpdated ({len(updated)}) - tool-managed files refreshed:")
        for item in updated:
            print(f"  ~ {item}")

    if backed_up:
        print(f"\nBacked up ({len(backed_up)}) - originals saved to .backup:")
        for item in backed_up:
            print(f"  B {item}")

    if removed:
        print(f"\nRemoved ({len(removed)}) - retired, unmodified bundle files:")
        for item in removed:
            print(f"  - {item}")

    if skipped:
        print(f"\nSkipped ({len(skipped)}) - user files preserved:")
        for item in skipped:
            print(f"  . {item}")

    onboard = "Run /onboard in Claude or $onboard in Codex to configure your project"
    if is_dev_mode and assistant in ("codex", "both"):
        print(f"\n{DEV_CODEX_WARNING}")
        onboard = (
            "Run /onboard in Claude to configure your project (Codex cannot see $onboard under --dev)"
            if assistant == "both"
            else "Re-run init without --dev, then run $onboard in Codex to configure your project"
        )

    if not (created or updated or symlinked or backed_up or removed or adopted):
        print("Everything up to date.")
    else:
        print("")
        print("Next steps:")
        print(f"  1. {onboard}")
        print(
            "  2. Or manually edit knowledge/SOURCE_INDEX.md and start with the design-model skill"
        )

    return EXIT_SUCCESS


def cmd_install_commands(args: argparse.Namespace) -> int:
    """Install MBSE commands to a project.

    Installs shared workflow skills and selected native adapters without project templates.
    """
    if args.list:
        bundles = skill_bundles(get_skills_dir())
        kinds = {bundle.name: bundle_kind(bundle) for bundle in bundles}
        print("Available MBSE skills:")
        for kind, heading in (("workflow", "Workflows"), ("supporting", "Supporting skills")):
            names = [name for name, declared in kinds.items() if declared == kind]
            print(f"\n{heading} ({len(names)}):")
            for name in names:
                print(f"  - {name}")
        print(f"\nTotal: {len(bundles)} skills")
        return EXIT_SUCCESS

    target_dir = Path(args.directory).resolve()
    if not target_dir.exists():
        print(f"Error: Directory does not exist: {args.directory}", file=sys.stderr)
        return EXIT_FAILURE

    installer = Installer(target_dir, force=args.force, decide=lambda path: "skip")
    install_assistants(
        installer,
        _get_data_root(),
        assistant=getattr(args, "assistant", "both"),
        link_mode=getattr(args, "link_mode", "symlink"),
        dev=False,
    )
    installer.save()
    actions = installer.actions
    print(
        f"Installed: {len(actions['created']) + len(actions['updated'])}, "
        f"Skipped: {len(actions['skipped'])}, Removed: {len(actions['removed'])}, "
        f"Adopted: {len(installer.adopted)}"
    )
    for item, old in installer.adopted.items():
        print(f"  A {item} (was -> {old})")
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
        choices=range(1, 7),
        metavar="N",
        help="Run only level N (1-6)",
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
        help="Initialize a modeling project with shared skills and native assistant adapters",
    )
    init_parser.add_argument(
        "path",
        nargs="?",
        help="Target directory (default: current directory)",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Replace modified assets and project templates; preserve native settings and instructions",
    )
    init_parser.add_argument(
        "--dev",
        action="store_true",
        help="Development mode: symlink tool-owned files instead of copying (requires source checkout)",
    )
    init_parser.add_argument(
        "--assistant",
        choices=("claude", "codex", "both"),
        default="both",
        help="Assistant integrations to install (default: both)",
    )
    init_parser.add_argument(
        "--link-mode",
        choices=("symlink", "copy"),
        default="symlink",
        help="Claude skill aliases: relative symlinks or copies",
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
    install_parser.add_argument("--assistant", choices=("claude", "codex", "both"), default="both")
    install_parser.add_argument("--link-mode", choices=("symlink", "copy"), default="symlink")
    install_parser.set_defaults(func=cmd_install_commands)

    # status command
    status_parser = subparsers.add_parser(
        "status",
        help="Show project status dashboard",
    )
    status_parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output as JSON instead of markdown",
    )
    status_parser.set_defaults(func=cmd_status)

    # pm command group (delegated to pm_cli module)
    from agentic_mbse.cli.pm_cli import register_pm_subcommands

    register_pm_subcommands(subparsers)

    # extract command (delegated to extract_cli module)
    from agentic_mbse.cli.extract_cli import register_extract_subcommand

    register_extract_subcommand(subparsers)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return EXIT_SUCCESS

    handler: Callable[[argparse.Namespace], int] = args.func
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
