"""Presentation links resolve.

Editorial wording and document layout belong to document review, not pytest.
"""
import re
from pathlib import Path

# absolute(), not resolve(): under `init --dev` this file is a link into the toolkit.
REPO_ROOT = Path(__file__).absolute().parents[2]


def _local_link_targets(path: Path, text: str):
    for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        relative = target.split("#", 1)[0]
        if relative:
            yield (path.parent / relative).resolve(), target


def test_narrative_evidence_links_resolve():
    for path in (REPO_ROOT / "work/narratives").glob("*.md"):
        for target, written_target in _local_link_targets(path, path.read_text()):
            assert target.exists(), f"{path}: unresolved link {written_target}"
