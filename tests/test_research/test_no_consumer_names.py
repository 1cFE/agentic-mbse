"""The shipped research code names no consumer: no project, requirement id, catalogue or private record."""

import re

import pytest

from tests.helpers.shipped import REPO_ROOT

#: Names shipped research code must never contain, word-bounded so "summaries" and "boundaries" pass.
CONSUMER_NAMES = re.compile(r"fusion-tea|MR-[0-9]|\baries\b|zotero|\.project/", re.IGNORECASE)

SHIPPED = (REPO_ROOT / "src" / "agentic_mbse" / "research",)


def _shipped_files():
    for root in SHIPPED:
        yield from sorted(
            path for path in root.rglob("*") if path.is_file() and "__pycache__" not in path.parts
        )


@pytest.mark.parametrize(
    ("text", "names_a_consumer"),
    [
        ("see fusion-tea", True),
        ("cited under MR-4", True),
        ("the ARIES protocol", True),
        ("- **Zotero Key**: 1:A", True),
        ("in .project/adr/", True),
        ("summaries and boundaries", False),
        ("a catalog key", False),
    ],
)
def test_the_pattern_is_the_criterion(text, names_a_consumer):
    assert bool(CONSUMER_NAMES.search(text)) is names_a_consumer


def test_the_research_package_names_no_consumer():
    files = list(_shipped_files())
    assert files, "the research package is missing"
    hits = [
        f"{path.relative_to(REPO_ROOT)}:{number}: {line.strip()}"
        for path in files
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        if CONSUMER_NAMES.search(line)
    ]
    assert hits == []
