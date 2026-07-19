"""Build deterministic hashed wheelhouse manifests and compatibility inputs."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from packaging.utils import canonicalize_name, parse_wheel_filename


def _record(path: Path, root: Path) -> dict[str, str]:
    name, version, build, tags = parse_wheel_filename(path.name)
    return {
        "name": canonicalize_name(name),
        "version": str(version),
        "filename": path.name,
        "relative_path": path.relative_to(root).as_posix(),
        "build": str(build),
        "tags": ",".join(sorted(str(tag) for tag in tags)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _line(record: dict[str, str]) -> str:
    return f"{record['name']}=={record['version']} --hash=sha256:{record['sha256']}"


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2]).resolve()
    output.mkdir(parents=True, exist_ok=True)
    records = [_record(path, root) for path in sorted(root.rglob("*.whl"))]
    (output / "wheelhouse-manifest.json").write_text(
        json.dumps(records, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    common: dict[str, dict[str, str]] = {}
    for record in records:
        if record["relative_path"].startswith("common/") and record["name"] not in {
            "agentic-mbse",
            "sysml-codegen",
        }:
            common[record["name"]] = record

    def select(relative_prefix: str, name: str, version: str) -> dict[str, str]:
        matches = [
            record
            for record in records
            if record["relative_path"].startswith(relative_prefix)
            and record["name"] == name
            and record["version"] == version
        ]
        if len(matches) != 1:
            raise RuntimeError(f"expected one {relative_prefix} {name}=={version}, got {matches}")
        return matches[0]

    old_codegen = select("old-codegen/", "sysml-codegen", "0.1.0")
    new_codegen = select("new-codegen/", "sysml-codegen", "0.1.0")
    old_companion = select("companions/", "agentic-mbse", "0.1.1")
    new_companion = select("companions/", "agentic-mbse", "0.1.2")
    cases = {
        "old-codegen-new-companion.txt": (old_codegen, new_companion),
        "new-codegen-old-companion.txt": (new_codegen, old_companion),
        "new-codegen-old-companion-runtime.txt": (new_codegen, old_companion),
        "new-codegen-new-companion.txt": (new_codegen, new_companion),
    }
    for filename, (codegen, companion) in cases.items():
        chosen = {**common, codegen["name"]: codegen, companion["name"]: companion}
        (output / filename).write_text(
            "\n".join(_line(chosen[name]) for name in sorted(chosen)) + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
