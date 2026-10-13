"""`verify`: report where the registry's artifacts disagree. It repairs nothing and writes nothing.

Every source directory should have one manifest row and one index block, and
every row and every registry block a directory. A slug recorded in
`RETIRED.jsonl` is expected absent: its absence is no finding, and any of its
artifacts coming back is a fault. Hand-curated entries point outside
`knowledge/sources/` and are never findings.

Drift that predates the registry is listed in the project's checked-in baseline
(`knowledge/.registry_baseline.json`) and reported as `legacy`, so a first run
does not read as a broken tool.
"""

from __future__ import annotations

import json
from collections.abc import Collection, Set
from dataclasses import dataclass
from typing import Any, Literal

from agentic_mbse.research.index import SOURCES_PREFIX, parse_index
from agentic_mbse.research.manifest import Row, load_manifest_rows
from agentic_mbse.research.paths import RegistryPaths, default_paths

FindingKind = Literal[
    "loose_file",
    "orphan_source_dir",
    "retired_reappeared",
    "block_without_row",
    "unresolvable_path",
    "row_without_block",
]
FindingClass = Literal["legacy", "fault"]


@dataclass(frozen=True)
class Finding:
    """One thing `verify` noticed. `klass` says whether the baseline already accounts for it."""

    kind: FindingKind
    klass: FindingClass
    path: str
    detail: str


@dataclass(frozen=True)
class VerifyReport:
    """Every finding of one `verify` run, in report order."""

    findings: tuple[Finding, ...]

    @property
    def has_faults(self) -> bool:
        return any(finding.klass == "fault" for finding in self.findings)


@dataclass(frozen=True)
class Baseline:
    """The drift a project recorded before its registry existed, as `knowledge/sources/<name>` paths."""

    orphan_source_dirs: frozenset[str]
    loose_files: frozenset[str]


def verify(paths: RegistryPaths | None = None) -> VerifyReport:
    """Every disagreement among source directories, manifest rows and index blocks.

    Findings come in three passes: source directories, then index blocks, then
    manifest rows. `paths` defaults to the project in the current directory.
    """
    paths = paths if paths is not None else default_paths()
    baseline = load_baseline(paths)
    rows = load_manifest_rows(paths)
    index_text = paths.index.read_text(encoding="utf-8") if paths.index.exists() else ""
    retired = load_retired(paths).keys()
    slugs_with_rows = {row["slug"] for row in rows if "slug" in row}
    return VerifyReport(
        findings=(
            *_source_dir_findings(paths, baseline, retired, slugs_with_rows),
            *_block_findings(paths, index_text, baseline, retired, slugs_with_rows),
            *_row_findings(paths, rows, index_text, baseline, retired),
        )
    )


def format_finding(finding: Finding) -> str:
    """The finding as one report line: class, kind, path, then what is wrong."""
    return f"{finding.klass:7} {finding.kind:20} {finding.path} — {finding.detail}"


def load_baseline(paths: RegistryPaths) -> Baseline:
    """The project's recorded pre-registry drift. No baseline file means none is expected."""
    if not paths.baseline.exists():
        return Baseline(orphan_source_dirs=frozenset(), loose_files=frozenset())
    recorded = json.loads(paths.baseline.read_text(encoding="utf-8"))
    return Baseline(
        orphan_source_dirs=frozenset(
            entry.rstrip("/") for entry in recorded.get("orphan_source_dirs", [])
        ),
        loose_files=frozenset(entry.rstrip("/") for entry in recorded.get("loose_files", [])),
    )


def load_retired(paths: RegistryPaths) -> dict[str, dict[str, Any]]:
    """Every `RETIRED.jsonl` line, keyed by slug. No file means nothing is retired."""
    if not paths.retired.exists():
        return {}
    lines = [
        json.loads(line)
        for line in paths.retired.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {line["slug"]: line for line in lines}


def _source_dir_findings(
    paths: RegistryPaths,
    baseline: Baseline,
    retired: Set[str],
    slugs_with_rows: Set[str],
) -> list[Finding]:
    findings = []
    entries = sorted(paths.sources.iterdir()) if paths.sources.exists() else []
    for entry in entries:
        location = f"{SOURCES_PREFIX}{entry.name}"
        if not entry.is_dir():
            findings.append(
                Finding(
                    kind="loose_file",
                    klass=_klass(location, baseline.loose_files),
                    path=location,
                    detail="not a source directory",
                )
            )
        elif entry.name in retired:
            findings.append(_reappeared(entry.name, "source directory"))
        elif entry.name not in slugs_with_rows:
            findings.append(
                Finding(
                    kind="orphan_source_dir",
                    klass=_klass(location, baseline.orphan_source_dirs),
                    path=location,
                    detail="source directory with no manifest row",
                )
            )
    return findings


def _block_findings(
    paths: RegistryPaths,
    index_text: str,
    baseline: Baseline,
    retired: Set[str],
    slugs_with_rows: Set[str],
) -> list[Finding]:
    """Registry blocks for a retired slug, or for a slug no row carries. Hand-curated blocks pass."""
    findings = []
    for block in parse_index(index_text, project_root=paths.project_root):
        if block.slug is None:
            continue
        if block.slug in retired:
            findings.append(_reappeared(block.slug, "SOURCE_INDEX.md block"))
        elif block.slug not in slugs_with_rows:
            location = f"{SOURCES_PREFIX}{block.slug}"
            findings.append(
                Finding(
                    kind="block_without_row",
                    klass=_klass(location, baseline.orphan_source_dirs),
                    path=location,
                    detail="SOURCE_INDEX.md block with no manifest row",
                )
            )
    return findings


def _row_findings(
    paths: RegistryPaths,
    rows: list[Row],
    index_text: str,
    baseline: Baseline,
    retired: Set[str],
) -> list[Finding]:
    """Rows for a retired slug, with no directory, or with no block.

    "No block" is judged on the raw index text, not the parser: a row is backed
    when its `knowledge/sources/<slug>/` path appears anywhere in the file.
    """
    findings = []
    for row in rows:
        slug = row.get("slug")
        if slug is None:
            continue
        location = f"{SOURCES_PREFIX}{slug}"
        if slug in retired:
            findings.append(_reappeared(slug, "manifest row"))
        elif not (paths.sources / slug).is_dir():
            findings.append(
                Finding(
                    kind="unresolvable_path",
                    klass=_klass(location, baseline.orphan_source_dirs),
                    path=location,
                    detail="manifest row whose source directory does not exist",
                )
            )
        elif f"{location}/" not in index_text:
            findings.append(
                Finding(
                    kind="row_without_block",
                    klass=_klass(location, baseline.orphan_source_dirs),
                    path=location,
                    detail="manifest row with no SOURCE_INDEX.md block",
                )
            )
    return findings


def _reappeared(slug: str, what: str) -> Finding:
    return Finding(
        kind="retired_reappeared",
        klass="fault",
        path=f"{SOURCES_PREFIX}{slug}",
        detail=f"{what} for a slug retired in knowledge/RETIRED.jsonl",
    )


def _klass(location: str, recorded: Collection[str]) -> FindingClass:
    return "legacy" if location in recorded else "fault"
