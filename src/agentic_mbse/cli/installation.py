"""Ownership-aware installation of shared skills and native assistant adapters."""

import hashlib
import json
import os
import shutil
from collections.abc import Callable
from pathlib import Path

import tomllib
import yaml

MANIFEST = ".agentic-mbse/install.json"
LEGACY_MANIFEST = ".claude/.tool-hashes.json"
BUNDLE_KINDS = ("workflow", "supporting")
# Where the pre-native installer linked entries: .claude/<location>/<name>.
LEGACY_LOCATIONS = ("commands", "skills", "agents", "hooks")


def is_source_checkout(root: Path) -> bool:
    """Whether `root` is an agentic-mbse source checkout rather than packaged data."""
    return (root / "src" / "agentic_mbse").is_dir()


def frontmatter(path: Path) -> tuple[dict, str]:
    """A markdown file's YAML frontmatter mapping, and the text after its closing `---` line."""
    lines = path.read_text().splitlines(keepends=True)
    delimiters = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == "---"]
    if delimiters[:1] != [0] or len(delimiters) < 2:
        raise ValueError(f"{path} has no frontmatter")
    meta = yaml.safe_load("".join(lines[1 : delimiters[1]]))
    if not isinstance(meta, dict):
        raise ValueError(f"{path} frontmatter is not a mapping")
    return meta, "".join(lines[delimiters[1] + 1 :])


def bundle_kind(bundle: Path) -> str:
    """The `metadata.kind` a bundle's SKILL.md frontmatter declares."""
    entry = bundle / "SKILL.md"
    metadata = frontmatter(entry)[0].get("metadata")
    kind = metadata.get("kind") if isinstance(metadata, dict) else None
    if kind not in BUNDLE_KINDS:
        raise ValueError(f"{entry} declares metadata.kind {kind!r}, not one of {BUNDLE_KINDS}")
    return str(kind)


def legacy_link_target(target: Path, relative: str) -> str | None:
    """The link text, if the pre-native installer made this entry; otherwise None.

    That installer linked `.claude/<location>/<name>` to `<checkout>/claude/<location>/<name>` with
    `resolve()`, so its text is absolute, has no `.` or `..` segment, and mirrors the entry.
    The raw text is checked, never normalized, and the referent is never read.
    """
    parts = relative.split("/")
    if len(parts) != 3 or parts[0] != ".claude" or parts[1] not in LEGACY_LOCATIONS:
        return None
    path = target / relative
    if not path.is_symlink():
        return None
    text = os.readlink(path)
    segments = text.split("/")
    if segments[0] != "" or any(s in ("", ".", "..") for s in segments[1:]):
        return None
    if segments[-3:] != ["claude", parts[1], parts[2]]:
        return None
    if not is_source_checkout(Path("/" + "/".join(segments[1:-3]))):
        return None
    return text


def fingerprint(path: Path) -> str | None:
    """Identify a file's bytes or a symlink itself, never its referent."""
    if path.is_symlink():
        return "link:" + os.readlink(path)
    if path.is_file():
        return hashlib.sha256(path.read_bytes()).hexdigest()
    return None


def backup(path: Path) -> Path:
    """Move an entry to an unused sibling backup, preserving symlinks as links."""
    dest = path.with_name(path.name + ".backup")
    counter = 1
    while dest.exists() or dest.is_symlink():
        dest = path.with_name(f"{path.name}.backup.{counter}")
        counter += 1
    path.rename(dest)
    return dest


class Installer:
    """Reconcile managed entries while retaining the baseline of skipped edits."""

    def __init__(self, target: Path, *, force: bool, decide: Callable[[str], str]):
        self.target = target
        self.force = force
        self.decide = decide
        self.default_action: str | None = None
        self.actions: dict[str, list[str]] = {
            k: [] for k in ("created", "updated", "skipped", "backed_up", "symlinked", "removed")
        }
        self.adopted: dict[str, str] = {}  # legacy entry -> the link text it replaced
        self.files: dict[str, str] = {}
        for name in (LEGACY_MANIFEST, MANIFEST):
            path = target / name
            if path.exists():
                self.files.update(json.loads(path.read_text())["files"])

    def parents(self, relative: str) -> bool:
        """Create destination parents only when none redirects through a symlink."""
        parent = self.target
        for part in Path(relative).parts[:-1]:
            parent = parent / part
            if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                print(f"Skipped {relative}: parent {parent} is not a real directory")
                self.actions["skipped"].append(relative)
                return False
            parent.mkdir(exist_ok=True)
        return True

    def permit(self, relative: str, desired: str | None = None) -> bool:
        """Resolve a conflict before replacing an existing destination entry."""
        path = self.target / relative
        if not path.exists() and not path.is_symlink():
            return True
        current = fingerprint(path)
        if current is not None and current in (self.files.get(relative), desired):
            return True
        legacy = legacy_link_target(self.target, relative)
        if legacy is not None:
            self.adopted[relative] = legacy
            return True
        action = "overwrite" if self.force else self.default_action or self.decide(relative)
        if action in ("skip_all", "overwrite_all"):
            action = action.removesuffix("_all")
            self.default_action = action
        if action == "skip":
            self.actions["skipped"].append(relative)
            return False
        if action == "backup":
            backup(path)
            self.actions["backed_up"].append(relative)
        return True

    def report(self, action: str, relative: str) -> None:
        """List an installed entry under `action`, unless it is already listed as adopted."""
        if relative not in self.adopted:
            self.actions[action].append(relative)

    def write(
        self, relative: str, content: bytes, *, source: Path | None = None, dev: bool = False
    ) -> bool:
        """Install one payload file, optionally linking its development source."""
        if not self.parents(relative):
            return False
        path = self.target / relative
        desired = (
            "link:" + str(source.resolve())
            if dev and source
            else hashlib.sha256(content).hexdigest()
        )
        if not self.permit(relative, desired):
            return False
        if path.is_dir() and not path.is_symlink():
            # A directory at a file path can contain owner data even with --force.
            backup(path)
            self.actions["backed_up"].append(relative)
        existed = path.exists() or path.is_symlink()
        if existed:
            path.unlink()
        if dev and source:
            path.symlink_to(source.resolve())
            self.report("symlinked", relative)
        else:
            path.write_bytes(content)
            if source:
                path.chmod(source.stat().st_mode)
            self.report("updated" if existed else "created", relative)
        self.files[relative] = desired
        return True

    def copy_tree(self, source: Path, relative: str, *, dev: bool = False) -> bool:
        """Reconcile individual bundle resources without deleting owner additions."""
        path = self.target / relative
        if not self.parents(relative):
            return False
        if path.is_symlink() or (path.exists() and not path.is_dir()):
            if not self.permit(relative):
                return False
            path.unlink()
            self.files.pop(relative, None)
        expected = set()
        for src in sorted(source.rglob("*")):
            if src.is_file() and "__pycache__" not in src.parts:
                destination = f"{relative}/{src.relative_to(source).as_posix()}"
                expected.add(destination)
                self.write(
                    destination,
                    src.read_bytes(),
                    source=src,
                    dev=dev,
                )
        self.prune_bundle(relative, expected)
        return True

    def prune_bundle(self, relative: str, expected: set[str]) -> None:
        """Remove retired bundle files only when the saved baseline still matches."""
        retired = sorted(
            key for key in self.files if key.startswith(relative + "/") and key not in expected
        )
        for key in retired:
            path = self.target / key
            # Manifest entries must stay inside the bundle, and ancestors must not redirect.
            if ".." in Path(key).parts or any(
                parent.is_symlink()
                for parent in path.parents
                if parent != self.target and self.target in parent.parents
            ):
                print(f"Preserved retired resource {key}: redirected path")
                self.actions["skipped"].append(key)
                continue
            if not path.exists() and not path.is_symlink():
                del self.files[key]
            elif fingerprint(path) == self.files[key]:
                path.unlink()
                del self.files[key]
                self.actions["removed"].append(key)
            else:
                print(f"Preserved retired resource {key}: local modifications")
                self.actions["skipped"].append(key)

    def link_directory(self, relative: str, link: str) -> bool:
        """Make an entry a directory link with text `link`, if it can be safely replaced."""
        if not self.parents(relative):
            return False
        path = self.target / relative
        if path.is_dir() and not path.is_symlink():
            entries = [p for p in path.rglob("*") if not p.is_dir() or p.is_symlink()]
            empty_dirs = [
                p
                for p in path.rglob("*")
                if p.is_dir() and not p.is_symlink() and not any(p.iterdir())
            ]
            owned = not empty_dirs and all(
                fingerprint(p) == self.files.get(p.relative_to(self.target).as_posix())
                and fingerprint(p) is not None
                for p in entries
            )
            # Empty, untracked owner directories are not evidence of ownership.
            if not entries or not owned:
                return False
            shutil.rmtree(path)
            for key in list(self.files):
                if key.startswith(relative + "/"):
                    del self.files[key]
        elif not self.permit(relative, "link:" + link):
            return False
        if path.is_symlink() or path.exists():
            path.unlink()
        path.symlink_to(link, target_is_directory=True)
        self.files[relative] = "link:" + link
        self.report("symlinked", relative)
        return True

    def retire_command(self, name: str) -> bool:
        """Retire a legacy command only after resolving its ownership conflict."""
        relative = f".claude/commands/{name}.md"
        path = self.target / relative
        if not path.exists() and not path.is_symlink():
            return True
        if not self.parents(relative) or not self.permit(relative):
            print(
                f"Preserved /{name}: Claude skill migration deferred. "
                f"Claude retains {relative}; Codex discovers .agents/skills/{name}/SKILL.md. "
                "The clients may run different versions; an existing same-name Claude skill still takes precedence."
            )
            return False
        if path.exists() or path.is_symlink():
            if path.is_dir() and not path.is_symlink():
                backup(path)
            else:
                path.unlink()
        self.files.pop(relative, None)
        return True

    def save(self) -> None:
        """Atomically save ownership, including unchanged baselines for skipped files."""
        if not self.parents(MANIFEST):
            raise ValueError("Cannot save installation manifest through a redirected parent")
        path = self.target / MANIFEST
        temporary = path.with_suffix(".tmp")
        if temporary.exists() or temporary.is_symlink():
            temporary.unlink()
        temporary.write_text(json.dumps({"version": 2, "files": self.files}, indent=2) + "\n")
        temporary.replace(path)


def render_agent(source: Path, docs: Path, assistant: str, adapter: str) -> str:
    """Render shared expert instructions into a native Claude or Codex envelope."""
    meta, body = frontmatter(source)
    body = body.replace("{SYSML_DOCS_PATH}", str(docs / "sysmlv2")).replace(
        "{SYSIDE_DOCS_PATH}", str(docs / "syside")
    )
    body = adapter + "\n\n" + body.lstrip()
    if assistant == "claude":
        return "---\n" + yaml.safe_dump(meta, sort_keys=False) + "---\n\n" + body
    role = {
        "name": meta["name"],
        "description": meta["description"],
        "developer_instructions": body,
    }
    if "Bash" not in meta["tools"]:
        role["sandbox_mode"] = "read-only"
    return (
        "\n".join(f"{key} = {json.dumps(value, ensure_ascii=False)}" for key, value in role.items())
        + "\n"
    )


def register_codex_agents(installer: Installer, agents: Path) -> None:
    """Append missing native role registrations while preserving owner TOML and values."""
    relative = ".codex/config.toml"
    if not installer.parents(relative):
        return
    path = installer.target / relative
    if path.is_symlink():
        print(
            "Preserved symlinked .codex/config.toml; register MBSE roles in its owner-managed source"
        )
        installer.actions["skipped"].append(relative)
        return
    content = path.read_text() if path.exists() else ""
    existing = tomllib.loads(content).get("agents", {})
    additions = []
    for source in sorted(agents.glob("*.md")):
        meta = frontmatter(source)[0]
        if meta["name"] in existing:
            continue
        name = json.dumps(meta["name"])
        description = json.dumps(meta["description"], ensure_ascii=False)
        config_file = json.dumps(f"agents/{source.stem}.toml")
        additions.append(
            f"[agents.{name}]\ndescription = {description}\nconfig_file = {config_file}\n"
        )
    if additions:
        separator = "\n" if not content or content.endswith("\n") else "\n\n"
        updated = content + separator + "\n".join(additions)
        try:
            tomllib.loads(updated)
        except tomllib.TOMLDecodeError:
            print(
                "Preserved .codex/config.toml: its table layout cannot be extended; merge MBSE role registrations manually"
            )
            installer.actions["skipped"].append(relative)
            return
        path.write_text(updated)
        installer.actions["updated" if content else "created"].append(relative)


def skill_bundles(skills: Path) -> list[Path]:
    """Return installable bundles from the packaged skill tree."""
    return sorted(entry.parent for entry in skills.glob("*/SKILL.md") if entry.is_file())


def install_dev_bundle(installer: Installer, source: Path) -> bool:
    """Install a shared bundle for --dev as one folder link to its source checkout folder.

    Codex lists a linked skill folder but skips a SKILL.md that is a file link. So a real folder
    the installer cannot replace, because it holds owner files or edits, gets a plain copy, and
    one line says what the copy did.
    """
    relative = f".agents/skills/{source.name}"
    # Checked once here, so the copy below cannot report a redirected .agents/skills again.
    if not installer.parents(relative):
        return False
    if installer.link_directory(relative, str(source.resolve())):
        return True
    destination = installer.target / relative
    # A link or file that permit refused is not retried as a copy, which would ask again.
    if not destination.is_dir() or destination.is_symlink():
        return False
    was_empty = not any(destination.iterdir())
    # The plain copy lists every file it writes as created or updated.
    written = (installer.actions["created"], installer.actions["updated"])
    before = sum(map(len, written))
    if not installer.copy_tree(source, relative):
        return False
    if (destination / "SKILL.md").is_symlink():
        print(
            f"Warning: Codex will not list the {source.name} skill: {relative}/SKILL.md is a file "
            f"link, which Codex skips. Remove {relative} and re-run init --dev, "
            "or re-run it with --force"
        )
    elif sum(map(len, written)) == before:
        print(
            f"Kept {relative} instead of linking it to the source checkout: "
            "the installer does not own everything in that folder and wrote no file into it"
        )
    elif was_empty:
        print(
            f"Copied {relative} instead of linking it to the source checkout: "
            "an empty folder was already there. The next --dev run links it"
        )
    else:
        print(
            f"Copied {relative} instead of linking it to the source checkout: "
            "the installer does not own everything in that folder"
        )
    return True


def expose_to_claude(installer: Installer, source: Path, *, link_mode: str, dev: bool) -> None:
    """Give Claude a skill alias for an installed bundle, once its legacy command is retired."""
    if not installer.retire_command(source.name):
        return
    alias = f".claude/skills/{source.name}"
    # Checked once here, so the copy fallback cannot report a redirected .claude/skills again.
    if not installer.parents(alias):
        return
    destination = installer.target / alias
    shared = installer.target / ".agents/skills" / source.name
    if link_mode == "copy":
        installer.copy_tree(source, alias, dev=dev)
    elif not installer.link_directory(alias, os.path.relpath(shared, destination.parent)):
        if destination.is_dir() and not destination.is_symlink():
            installer.copy_tree(source, alias, dev=dev)


def install_assistants(
    installer: Installer, data: Path, *, assistant: str, link_mode: str, dev: bool
) -> None:
    """Install shared bundles and selected native roles, instructions, and inactive hooks."""
    runtimes = ("claude", "codex") if assistant == "both" else (assistant,)
    for source in skill_bundles(data / "skills"):
        if dev:
            shared_ready = install_dev_bundle(installer, source)
        else:
            shared_ready = installer.copy_tree(source, f".agents/skills/{source.name}")
        if shared_ready and "claude" in runtimes:
            expose_to_claude(installer, source, link_mode=link_mode, dev=dev)
    for runtime in runtimes:
        adapter = (data / "adapters" / f"{runtime}.md").read_text()
        installer.write(f".agentic-mbse/{runtime}.md", adapter.encode())
        entry = "CLAUDE.md" if runtime == "claude" else "AGENTS.md"
        entry_path = installer.target / entry
        # Native entry files belong to the owner, including under --force.
        if not entry_path.exists() and not entry_path.is_symlink():
            installer.write(
                entry,
                f"# Modeling project\n\nRead `.agentic-mbse/{runtime}.md` for assistant-specific tools and `modeling_project/OVERVIEW.md` for project context. Follow `modeling_project/MODELING_GUIDE.md` and `modeling_project/MODELING_PROCESS.md` when modeling.\n".encode(),
            )
        else:
            print(f"Preserved {entry}; skills load .agentic-mbse/{runtime}.md directly")
        for source in sorted((data / "agents").glob("*.md")):
            suffix = ".md" if runtime == "claude" else ".toml"
            content = render_agent(source, data / "docs", runtime, adapter)
            installer.write(f".{runtime}/agents/{source.stem}{suffix}", content.encode())
    if "codex" in runtimes:
        register_codex_agents(installer, data / "agents")
    if "claude" in runtimes:
        for source in sorted((data / "hooks").glob("*")):
            installer.write(
                f".claude/hooks/{source.name}", source.read_bytes(), source=source, dev=dev
            )
