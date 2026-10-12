"""Where a target's source registry lives, and the lock that serializes writes to it."""

from __future__ import annotations

import fcntl
import shutil
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RegistryPaths:
    """Every registry path, derived from one knowledge directory.

    Deriving them all from one directory keeps staging and sources on the same
    filesystem, which the commit's atomic rename needs.
    """

    knowledge_dir: Path

    @property
    def project_root(self) -> Path:
        """The directory holding the knowledge directory and the target's `pyproject.toml`."""
        return self.knowledge_dir.parent

    @property
    def raw(self) -> Path:
        return self.knowledge_dir / "raw"

    @property
    def sources(self) -> Path:
        return self.knowledge_dir / "sources"

    @property
    def index(self) -> Path:
        return self.knowledge_dir / "SOURCE_INDEX.md"

    @property
    def manifest(self) -> Path:
        return self.knowledge_dir / "MANIFEST.jsonl"

    @property
    def staging(self) -> Path:
        return self.knowledge_dir / ".staging"

    @property
    def lock(self) -> Path:
        return self.knowledge_dir / ".registry.lock"

    @property
    def baseline(self) -> Path:
        return self.knowledge_dir / ".registry_baseline.json"

    @property
    def retired(self) -> Path:
        return self.knowledge_dir / "RETIRED.jsonl"


def default_paths() -> RegistryPaths:
    """The registry of the project in the current directory, with relative paths."""
    return RegistryPaths(knowledge_dir=Path("knowledge"))


@contextmanager
def registry_lock(paths: RegistryPaths) -> Iterator[None]:
    """Hold the registry's exclusive lock, so no two writers interleave a read-modify-write."""
    paths.lock.parent.mkdir(parents=True, exist_ok=True)
    with open(paths.lock, "w") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def sweep_stale_staging(paths: RegistryPaths, *, older_than_s: float) -> None:
    """Remove staging entries last modified more than `older_than_s` seconds ago.

    Each attempt stages in its own directory and removes it when done, so only
    what a killed run left behind is old. The age bound, not a whole-root clear,
    is what keeps another attempt's live staging directory safe. Runs under the
    registry lock.
    """
    paths.staging.mkdir(parents=True, exist_ok=True)
    cutoff = time.time() - older_than_s
    with registry_lock(paths):
        for leftover in paths.staging.iterdir():
            if _modified_at(leftover) > cutoff:
                continue
            if leftover.is_dir():
                shutil.rmtree(leftover, ignore_errors=True)
            else:
                leftover.unlink(missing_ok=True)


def _modified_at(path: Path) -> float:
    """The entry's mtime, or now if it vanished meanwhile, so a racing attempt is never swept."""
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return time.time()
