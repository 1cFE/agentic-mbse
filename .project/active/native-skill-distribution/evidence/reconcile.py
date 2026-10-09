"""One-time tooling for WRAP-SPLIT Item 1: regenerate the shipped text from `main`, and check it.

    check --main REV TARGET   compare a fresh install in TARGET against main's text
    write --main REV          regenerate skills/, agents/ and the tool-owned templates from main

`check` shares no envelope or adaptation code with `write`, so it can disagree with it.
Both read `main` through git, never through a working-tree `claude/`. Retires with this item.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

HERE = Path(__file__).resolve().parent
REPO = Path(
    subprocess.run(
        ["git", "-C", str(HERE), "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
)
ADAPTATIONS = HERE / "adaptations.yaml"
NATIVE = "86921f9"

# The four tool-owned templates and where `init` installs each.
TEMPLATES = {
    "project_templates/MODELING_GUIDE.md.template": "modeling_project/MODELING_GUIDE.md",
    "project_templates/MODELING_PROCESS.md.template": "modeling_project/MODELING_PROCESS.md",
    "project_templates/EPIC_GUIDE.md.template": "work/EPIC_GUIDE.md",
    "project_templates/epic_template.md.template": "work/backlog/epic_template.md",
}


# --- Shared helpers: git reads, the list, and the frontmatter split ---


def show(rev: str, path: str) -> str:
    """The file's text at a revision."""
    return subprocess.run(
        ["git", "-C", str(REPO), "show", f"{rev}:{path}"],
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8")


def tree(rev: str, *paths: str) -> dict[str, bool]:
    """Every file under `paths` at a revision, mapped to whether git records it executable."""
    listing = subprocess.run(
        ["git", "-C", str(REPO), "ls-tree", "-r", rev, "--", *paths],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    files = {}
    for line in listing.splitlines():
        meta, path = line.split("\t", 1)
        files[path] = meta.split()[0] == "100755"
    return files


def load_adaptations(path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = yaml.safe_load(path.read_text(encoding="utf-8"))
    return entries


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """(frontmatter, body). The frontmatter is the text between an opening "---" line and the
    next line equal to "---"; the body is everything after that line. No frontmatter: (None, text).
    """
    if not text.startswith("---\n"):
        return None, text
    lines = text.splitlines(keepends=True)
    for i in range(1, len(lines)):
        if lines[i].rstrip("\n") == "---":
            return "".join(lines[1:i]), "".join(lines[i + 1 :])
    raise ValueError("frontmatter opens with --- but never closes")


# --- check ---


class Checker:
    """Compares files against main's text plus the list, and collects every mismatch."""

    def __init__(self, entries: list[dict[str, Any]]) -> None:
        self.entries = entries
        self.applied: set[str] = set()
        self.problems: list[str] = []
        self.rows: list[str] = []
        self.compared = 0

    def expected(self, path: str, main_text: str) -> str:
        """main's text with the list's entries for `path` applied to its body."""
        frontmatter, body = split_frontmatter(main_text)
        for entry in self.entries:
            if entry["file"] != path:
                continue
            found = body.count(entry["old"])
            if found != entry["count"]:
                self.problems.append(
                    f"{entry['id']} {path}: `old` occurs {found}x, list says {entry['count']}"
                )
            body = body.replace(entry["old"], entry["new"])
            self.applied.add(entry["id"])
        return body if frontmatter is None else f"---\n{frontmatter}---\n{body}"

    def file(self, label: str, actual: Path, expected: str, executable: bool) -> None:
        self.compared += 1
        if not actual.is_file():
            self.problems.append(f"{label}: missing at {actual}")
            return
        if actual.read_text(encoding="utf-8") != expected:
            self.problems.append(f"{label}: bytes differ from main + adaptations")
        self.mode(label, actual, executable)

    def skill(self, path: str, actual: Path, main_text: str, kind: str, preface: str) -> None:
        """An installed SKILL.md: frontmatter compared as data, everything after it as bytes."""
        self.compared += 1
        if not actual.is_file():
            self.problems.append(f"{path}: missing at {actual}")
            return
        frontmatter, body = split_frontmatter(actual.read_text(encoding="utf-8"))
        main_frontmatter, _ = split_frontmatter(main_text)
        if frontmatter is None or main_frontmatter is None:
            self.problems.append(f"{path}: no frontmatter")
            return

        expected = yaml.safe_load(main_frontmatter)
        if "metadata" in expected:
            self.problems.append(f"{path}: main already has a metadata key")
        expected.pop("skills", None)
        tools = expected.get("allowed-tools")
        if isinstance(tools, list):
            expected["allowed-tools"] = ["Agent" if tool == "Task" else tool for tool in tools]
        elif isinstance(tools, str):
            expected["allowed-tools"] = re.sub(r"\bTask\b", "Agent", tools)
        expected["metadata"] = {"kind": kind}
        if yaml.safe_load(frontmatter) != expected:
            self.problems.append(f"{path}: frontmatter is not main's plus the envelope")

        _, adapted_body = split_frontmatter(self.expected(path, main_text))
        if body != "\n" + preface + "\n\n" + adapted_body:
            self.problems.append(f"{path}: body is not the preface plus main's adapted body")
        self.mode(path, actual, False)

    def mode(self, label: str, actual: Path, executable: bool) -> None:
        if bool(actual.stat().st_mode & 0o111) != executable:
            self.problems.append(f"{label}: executable bit differs from main's ({executable})")

    def same_set(self, label: str, actual: set[str], expected: set[str]) -> None:
        for extra in sorted(actual - expected):
            self.problems.append(f"{label}: extra {extra}")
        for missing in sorted(expected - actual):
            self.problems.append(f"{label}: missing {missing}")

    def row(self, path: str, source: str, envelope: bool) -> None:
        ids = [entry["id"] for entry in self.entries if entry["file"] == path]
        disposition = f"merge: main + {', '.join(ids)}" if ids else "take main"
        self.rows.append(
            f"| `{path}` | `{source}` | {'yes' if envelope else 'no'} | {disposition} |"
        )


def native_preface(rev: str) -> str:
    """The paragraph after the frontmatter, which must be one string across every bundle at `rev`."""
    prefaces = set()
    for path in tree(rev, "skills"):
        if path.endswith("/SKILL.md"):
            _, body = split_frontmatter(show(rev, path))
            prefaces.add(body.lstrip("\n").split("\n\n", 1)[0])
    if len(prefaces) != 1:
        raise ValueError(f"{len(prefaces)} distinct prefaces at {rev}")
    return prefaces.pop()


def check(main: str, target: Path, adaptations: Path, preface_from: str, rows: Path | None) -> int:
    checker = Checker(load_adaptations(adaptations))
    preface = native_preface(preface_from)
    main_files = tree(main, "claude", "docs/patterns", *TEMPLATES)

    # Bundles: claude/commands/<n>.md is a workflow, claude/skills/<n>/** a supporting bundle.
    bundles: dict[str, dict[str, str]] = {}  # name -> {path inside the bundle: main path}
    kinds: dict[str, str] = {}
    for path in main_files:
        parts = path.split("/")
        if parts[:2] == ["claude", "commands"]:
            name = parts[2].removesuffix(".md")
            bundles.setdefault(name, {})["SKILL.md"] = path
            kinds[name] = "workflow"
        elif parts[:2] == ["claude", "skills"]:
            bundles.setdefault(parts[2], {})["/".join(parts[3:])] = path
            kinds[parts[2]] = "supporting"

    installed = target / ".agents" / "skills"
    checker.same_set("bundles", {p.name for p in installed.iterdir() if p.is_dir()}, set(bundles))
    for name, files in sorted(bundles.items()):
        bundle = installed / name
        if bundle.is_dir():
            actual = {p.relative_to(bundle).as_posix() for p in bundle.rglob("*") if p.is_file()}
            checker.same_set(f"bundle {name}", actual, set(files))
        for inside, source in sorted(files.items()):
            path = f"skills/{name}/{inside}"
            if inside == "SKILL.md":
                checker.skill(path, bundle / inside, show(main, source), kinds[name], preface)
            else:
                expected = checker.expected(path, show(main, source))
                checker.file(path, bundle / inside, expected, main_files[source])
            checker.row(path, source, inside == "SKILL.md")

    for template, destination in TEMPLATES.items():
        expected = checker.expected(template, show(main, template))
        checker.file(template, target / destination, expected, main_files[template])
        checker.row(template, template, False)

    # Agents are rendered at install time, so the source tree is compared.
    agents = {
        p.removeprefix("claude/agents/"): p for p in main_files if p.startswith("claude/agents/")
    }
    checker.same_set("agents", {p.name for p in (REPO / "agents").glob("*.md")}, set(agents))
    for name, source in sorted(agents.items()):
        path = f"agents/{name}"
        checker.file(
            path, REPO / path, checker.expected(path, show(main, source)), main_files[source]
        )
        checker.row(path, source, False)

    hooks = {
        p.removeprefix("claude/hooks/"): p for p in main_files if p.startswith("claude/hooks/")
    }
    installed_hooks = target / ".claude" / "hooks"
    checker.same_set("hooks", {p.name for p in installed_hooks.iterdir()}, set(hooks))
    for name, source in sorted(hooks.items()):
        checker.file(f"hook {name}", installed_hooks / name, show(main, source), main_files[source])

    # Pattern docs are packaged, not installed, so the source tree is compared.
    patterns = {p for p in main_files if p.startswith("docs/patterns/")}
    in_source = {
        p.relative_to(REPO).as_posix() for p in (REPO / "docs/patterns").rglob("*") if p.is_file()
    }
    checker.same_set("pattern docs", in_source, patterns)
    for path in sorted(patterns):
        checker.file(path, REPO / path, show(main, path), main_files[path])

    for entry in checker.entries:
        if entry["id"] not in checker.applied:
            checker.problems.append(f"{entry['id']} {entry['file']}: names no compared file")

    if rows is not None:
        header = ["| Path | `main` source | Envelope applied | Disposition |", "|---|---|---|---|"]
        rows.write_text("\n".join(header + checker.rows) + "\n", encoding="utf-8")
    for problem in checker.problems:
        print(problem)
    print(
        f"check --main {main}: {checker.compared} files compared, "
        f"{len(checker.problems)} mismatches"
    )
    return 1 if checker.problems else 0


# --- write ---

# The native branch's preface, verbatim (typographic apostrophe included).
PREFACE = (
    "Before executing this skill, read `.agentic-mbse/claude.md` in Claude Code or "
    "`.agentic-mbse/codex.md` in Codex. Resolve supporting paths from this skill’s installed "
    "directory; keep generated outputs in the project or a temporary directory. Read referenced "
    "skills from `.agents/skills/<name>/SKILL.md` when their guidance is needed."
)


def destination(path: str) -> str:
    """The path rule: where a file of main's lives in the tool-neutral tree."""
    parts = path.split("/")
    if parts[:2] == ["claude", "commands"] and len(parts) == 3:
        return f"skills/{parts[2].removesuffix('.md')}/SKILL.md"
    if parts[:2] == ["claude", "skills"] and len(parts) > 3:
        return "skills/" + "/".join(parts[2:])
    if parts[:2] == ["claude", "agents"] and len(parts) == 3:
        return f"agents/{parts[2]}"
    if path in TEMPLATES:
        return path
    raise ValueError(f"no path rule for main's {path}")


def envelope(frontmatter: str, kind: str) -> str:
    """D3: drop `skills:`, grant Agent where main grants Task, record the kind last, then the
    preface. A text transform, so folded descriptions keep main's exact bytes."""
    lines = frontmatter.splitlines(keepends=True)
    kept = []
    for i, line in enumerate(lines):
        if line.startswith("skills:"):
            if i + 1 < len(lines) and lines[i + 1][:1] in (" ", "\t"):
                raise ValueError("`skills:` continues onto indented lines")
            continue
        if line.startswith("allowed-tools:"):
            line = re.sub(r"\bTask\b", "Agent", line)
        kept.append(line)
    kept.append(f"metadata:\n  kind: {kind}\n")
    return "---\n" + "".join(kept) + "---\n\n" + PREFACE + "\n\n"


def adapt(path: str, body: str, entries: list[dict[str, Any]]) -> str:
    """Apply the list's entries for `path`, in order, each at exactly its count."""
    for entry in entries:
        if entry["file"] != path:
            continue
        found = body.count(entry["old"])
        if found != entry["count"]:
            raise ValueError(
                f"{entry['id']} {path}: `old` occurs {found}x, list says {entry['count']}"
            )
        body = body.replace(entry["old"], entry["new"])
    return body


def write(main: str, adaptations: Path) -> int:
    entries = load_adaptations(adaptations)
    outputs: dict[str, tuple[str, bool]] = {}  # destination -> (text, executable)
    for path, executable in tree(main, "claude", *TEMPLATES).items():
        if path.startswith("claude/hooks/"):
            continue  # commit 3 moves the hook with `git mv`
        target = destination(path)
        frontmatter, body = split_frontmatter(show(main, path))
        body = adapt(target, body, entries)
        if target.endswith("/SKILL.md"):
            if frontmatter is None:
                raise ValueError(f"{path} has no frontmatter")
            kind = "workflow" if path.startswith("claude/commands/") else "supporting"
            text = envelope(frontmatter, kind) + body
        elif frontmatter is not None:
            text = f"---\n{frontmatter}---\n{body}"
        else:
            text = body
        outputs[target] = (text, executable)

    unused = [entry["id"] for entry in entries if entry["file"] not in outputs]
    if unused:
        raise ValueError(f"entries name no regenerated file: {unused}")

    for target, (text, executable) in sorted(outputs.items()):
        file = REPO / target
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(text.encode("utf-8"))
        file.chmod(0o755 if executable else 0o644)
    print(f"write --main {main}: {len(outputs)} files regenerated")

    in_tree = {
        p.relative_to(REPO).as_posix()
        for folder in ("skills", "agents")
        for p in (REPO / folder).rglob("*")
        if p.is_file()
    }
    for orphan in sorted(in_tree - set(outputs)):
        print(f"no counterpart in main, left in place (needs a disposition): {orphan}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    commands = parser.add_subparsers(dest="command", required=True)

    check_parser = commands.add_parser("check", help="compare a fresh install against main")
    check_parser.add_argument("--main", required=True, help="main's revision")
    check_parser.add_argument(
        "--preface-from", default=NATIVE, help="revision whose bundles carry the preface"
    )
    check_parser.add_argument("--adaptations", type=Path, default=ADAPTATIONS)
    check_parser.add_argument("--rows", type=Path, help="write one markdown row per compared file")
    check_parser.add_argument("target", type=Path, help="a fresh `init --assistant both` install")

    write_parser = commands.add_parser("write", help="regenerate the shipped text from main")
    write_parser.add_argument("--main", required=True, help="main's revision")
    write_parser.add_argument("--adaptations", type=Path, default=ADAPTATIONS)

    args = parser.parse_args()
    if args.command == "check":
        return check(args.main, args.target, args.adaptations, args.preface_from, args.rows)
    return write(args.main, args.adaptations)


if __name__ == "__main__":
    sys.exit(main())
