"""The shipped research code and text name no consumer: no project, requirement id, catalogue or private record."""

import re

import pytest

from tests.helpers.shipped import REPO_ROOT

#: Names shipped research code must never contain, word-bounded so "summaries" and "boundaries" pass.
CONSUMER_NAMES = re.compile(r"fusion-tea|MR-[0-9]|\baries\b|zotero|\.project/", re.IGNORECASE)

SHIPPED = (
    REPO_ROOT / "src" / "agentic_mbse" / "research",
    REPO_ROOT / "skills" / "research-acquire",
    REPO_ROOT / "docs" / "research-seam.md",
)


def _shipped_files():
    for root in SHIPPED:
        if root.is_file():
            yield root
            continue
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


def test_the_shipped_research_code_and_text_name_no_consumer():
    missing = [str(root.relative_to(REPO_ROOT)) for root in SHIPPED if not root.exists()]
    assert missing == []
    files = list(_shipped_files())
    hits = [
        f"{path.relative_to(REPO_ROOT)}:{number}: {line.strip()}"
        for path in files
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
        if CONSUMER_NAMES.search(line)
    ]
    assert hits == []
