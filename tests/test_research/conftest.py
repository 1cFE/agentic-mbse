"""Fixtures for the research registry suite.

Every tree is built as a fresh target has it after `agentic-mbse init`: the
shipped `SOURCE_INDEX.md` template, an empty `sources/` directory, and no
manifest. Tests always inject the tree's paths. Because `default_paths()` is
relative to the current directory, a session check fails the suite if anything
lands in this repository's own `knowledge/` directory.
"""

import json
import re
import shutil
import threading
import urllib.request
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from fnmatch import fnmatch
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from agentic_mbse.cli import get_template_path
from agentic_mbse.research import RegistryPaths
from tests.helpers.shipped import REPO_ROOT


@dataclass(frozen=True)
class KnowledgeTree:
    """A throwaway registry tree and the paths object the package takes."""

    paths: RegistryPaths

    @property
    def root(self) -> Path:
        return self.paths.knowledge_dir

    @property
    def index(self) -> Path:
        return self.paths.index

    @property
    def manifest(self) -> Path:
        return self.paths.manifest

    @property
    def sources(self) -> Path:
        return self.paths.sources

    @property
    def raw(self) -> Path:
        return self.paths.raw


@pytest.fixture
def knowledge_tree(tmp_path) -> KnowledgeTree:
    """A fresh target's registry under its own project directory."""
    paths = RegistryPaths(knowledge_dir=tmp_path / "project" / "knowledge")
    paths.sources.mkdir(parents=True)
    shutil.copyfile(get_template_path(), paths.index)
    return KnowledgeTree(paths=paths)


# --- the repository's own knowledge/ stays untouched -------------------------


def _knowledge_snapshot(knowledge_dir: Path) -> dict[str, bytes | None]:
    """Every entry under the directory: file bytes, or None for a directory."""
    if not knowledge_dir.exists():
        return {}
    return {
        path.relative_to(knowledge_dir).as_posix(): None if path.is_dir() else path.read_bytes()
        for path in sorted(knowledge_dir.rglob("*"))
    }


@pytest.fixture(scope="session", autouse=True)
def repository_knowledge_untouched() -> Iterator[None]:
    """Fail the session if the suite created or changed anything under the repo's `knowledge/`."""
    knowledge_dir = REPO_ROOT / "knowledge"
    before = _knowledge_snapshot(knowledge_dir)
    yield
    after = _knowledge_snapshot(knowledge_dir)
    added = sorted(after.keys() - before.keys())
    removed = sorted(before.keys() - after.keys())
    modified = sorted(name for name in before.keys() & after.keys() if before[name] != after[name])
    assert not (added or removed or modified), (
        f"the research suite wrote into {knowledge_dir}: "
        f"added {added}, removed {removed}, modified {modified}"
    )


# --- offline capture -----------------------------------------------------------
#
# `agentic-mbse extract` rejects `file://`, so fixture pages are served over real
# HTTP from a loopback server, and capture runs the real extractor offline.

FIXTURE_WEB = Path(__file__).parent / "fixtures" / "web"

# The fetcher decodes by the declared charset, so the Latin-1 page is served as one.
FIXTURE_CHARSET = {"latin1.html": "iso-8859-1"}


class _FixtureHandler(SimpleHTTPRequestHandler):
    def guess_type(self, path):
        charset = FIXTURE_CHARSET.get(Path(path).name)
        if charset:
            return f"text/html; charset={charset}"
        return super().guess_type(path)

    def log_message(self, *args):
        pass


@dataclass(frozen=True)
class LocalSite:
    port: int

    def url(self, name: str) -> str:
        return f"http://127.0.0.1:{self.port}/{name}"

    def fetched_bytes(self, name: str) -> bytes:
        with urllib.request.urlopen(self.url(name)) as response:
            return response.read()


@pytest.fixture(scope="session")
def local_site() -> Iterator[LocalSite]:
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        partial(_FixtureHandler, directory=str(FIXTURE_WEB)),
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield LocalSite(port=server.server_address[1])
    finally:
        server.shutdown()
        server.server_close()


PDF_LINES = (
    "Widget Coil Note (synthetic fixture)",
    "",
    "The widget winding pack measures 1000 mm by 400 mm.",
    "The invented conductor carries 100.0 kA across 150 turns.",
    "This document exists only to exercise the local-PDF capture path.",
)


@pytest.fixture(scope="session")
def generated_pdf(tmp_path_factory) -> Path:
    """A one-page text PDF, drawn with pymupdf (a core dependency)."""
    import pymupdf

    document = pymupdf.open()
    page = document.new_page()
    for i, line in enumerate(PDF_LINES):
        page.insert_text((72, 72 + 18 * i), line, fontsize=12)
    path = tmp_path_factory.mktemp("pdf") / "widget_coil_note.pdf"
    document.save(path)
    document.close()
    return path


# --- run directories -----------------------------------------------------------


@pytest.fixture
def make_run_dir(tmp_path) -> Callable[..., Path]:
    """Build a run directory with the given limits, as `open` leaves it for `register`."""

    def make(max_captures: int = 2, max_searches: int = 3, name: str = "run") -> Path:
        directory = tmp_path / name
        (directory / "receipts").mkdir(parents=True)
        (directory / "run.json").write_text(
            json.dumps(
                {
                    "request_id": "REQ-001",
                    "request_key": "k" * 64,
                    "limits": {"max_searches": max_searches, "max_captures": max_captures},
                }
            )
        )
        return directory

    return make


@pytest.fixture
def run_dir(make_run_dir) -> Path:
    return make_run_dir()


# --- hold-out guards -----------------------------------------------------------


@dataclass(frozen=True)
class FakeMatch:
    rule_id: str
    count: int
    offsets: tuple[int, ...]


@dataclass(frozen=True)
class FakeGuard:
    """A hold-out guard that bars fixed terms, case-insensitively, and input-path globs."""

    terms: tuple[str, ...] = ()
    path_globs: tuple[str, ...] = ()

    def check_input_path(self, path: Path) -> FakeMatch | None:
        for glob in self.path_globs:
            if fnmatch(path.as_posix(), glob):
                return FakeMatch(rule_id=f"path:{glob}", count=1, offsets=(0,))
        return None

    def scan_terms(self, text: str) -> list[FakeMatch]:
        matches = []
        for term in self.terms:
            offsets = tuple(
                found.start() for found in re.finditer(re.escape(term), text, re.IGNORECASE)
            )
            if offsets:
                matches.append(
                    FakeMatch(rule_id=f"term:{term}", count=len(offsets), offsets=offsets)
                )
        return matches

    def scan_file(self, path: Path) -> list[FakeMatch]:
        return self.scan_terms(path.read_text(encoding="utf-8", errors="replace"))


#: A guard that bars nothing, for tests that are not about the hold-out.
NO_GUARD = FakeGuard()

#: The token `fixtures/web/marker.html` carries for the fake guard to bar.
SEALED_TOKEN = "sealed-widget-07"


#: A guard file as a target writes one: standard library only, a dataclass match,
#: postponed annotations. It bars `SEALED_TOKEN` in text and files, and input
#: paths with a `sealed` directory in them.
GUARD_FILE_SOURCE = f'''\
from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path

BARRED_TERM = "{SEALED_TOKEN}"
BARRED_PATH = "*/sealed/*"


@dataclass(frozen=True)
class Match:
    rule_id: str
    count: int
    offsets: tuple[int, ...]


def check_input_path(path: Path) -> Match | None:
    if fnmatch(path.as_posix(), BARRED_PATH):
        return Match(rule_id=f"path:{{BARRED_PATH}}", count=1, offsets=(0,))
    return None


def scan_terms(text: str) -> list[Match]:
    lowered = text.lower()
    offsets = []
    start = lowered.find(BARRED_TERM)
    while start != -1:
        offsets.append(start)
        start = lowered.find(BARRED_TERM, start + 1)
    if not offsets:
        return []
    return [Match(rule_id=f"term:{{BARRED_TERM}}", count=len(offsets), offsets=tuple(offsets))]


def scan_file(path: Path) -> list[Match]:
    return scan_terms(path.read_text(encoding="utf-8", errors="replace"))
'''


def write_research_config(project_root: Path, table_body: str) -> None:
    """Write the project's `pyproject.toml` with `table_body` under `[tool.agentic-mbse.research]`."""
    (project_root / "pyproject.toml").write_text(
        f"[tool.agentic-mbse.research]\n{table_body}\n", encoding="utf-8"
    )


@dataclass
class RecordingGuard:
    """Records every call in order, then answers as `inner` does."""

    inner: FakeGuard = NO_GUARD
    calls: list[tuple[str, object]] = field(default_factory=list)

    def check_input_path(self, path: Path) -> FakeMatch | None:
        self.calls.append(("check_input_path", path))
        return self.inner.check_input_path(path)

    def scan_terms(self, text: str) -> list[FakeMatch]:
        self.calls.append(("scan_terms", text))
        return self.inner.scan_terms(text)

    def scan_file(self, path: Path) -> list[FakeMatch]:
        self.calls.append(("scan_file", path))
        return self.inner.scan_file(path)


# --- what a tree holds -----------------------------------------------------------


def _entry_names(directory: Path) -> list[str]:
    """The entries of a directory, sorted. An absent directory has none."""
    return sorted(path.name for path in directory.iterdir()) if directory.is_dir() else []


def registry_state(tree: KnowledgeTree) -> tuple[bytes | None, bytes | None, list[str], list[str]]:
    """The index and manifest bytes (None when absent), and the source and raw entries."""
    return (
        tree.index.read_bytes() if tree.index.exists() else None,
        tree.manifest.read_bytes() if tree.manifest.exists() else None,
        _entry_names(tree.sources),
        _entry_names(tree.raw),
    )


def assert_nothing_written(tree: KnowledgeTree) -> None:
    """Assert a fresh tree still holds no registration and no leftover staging.

    The manifest and staging may be absent or empty, as a refusal may leave them.
    The index must still be the shipped template, byte for byte.
    """
    assert _entry_names(tree.sources) == []
    assert _entry_names(tree.raw) == []
    assert _entry_names(tree.paths.staging) == []
    assert not tree.manifest.exists() or tree.manifest.read_bytes() == b""
    assert tree.index.read_bytes() == get_template_path().read_bytes()
