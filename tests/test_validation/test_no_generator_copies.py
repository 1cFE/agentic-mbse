"""ADR 0006: sysml-codegen alone decides what the generator accepts, so no validation module
cites a generator diagnostic or commit. A pointer to `sysml-codegen check` is allowed."""

import re
from pathlib import Path

import agentic_mbse.validation

GENERATOR_CITATION = re.compile(r"(?i:codegen)(?! check)|\bSI_[A-Z_]+|\bSRC-\d+")


def test_validation_modules_cite_no_generator_behaviour() -> None:
    root = Path(agentic_mbse.validation.__file__).parent
    hits = [
        f"{path.name}:{number}: {line.strip()}"
        for path in sorted(root.rglob("*.py"))
        for number, line in enumerate(path.read_text().splitlines(), start=1)
        if GENERATOR_CITATION.search(line)
    ]
    assert hits == [], "generator checks belong in sysml-codegen (ADR 0006):\n" + "\n".join(hits)
