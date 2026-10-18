"""Every marked SysML example in the shipped text has exactly its stated positional findings.

A fence this item adds or changes in the shipped trees carries a marker directly above it
(design "Validation Approach", Reg-3):

    <!-- @positional-example expect="none" -->
    <!-- @positional-example expect="<owner>|<input>|<target>; ..." -->

Every marked fence is a fragment. The test wraps it in `package example { private import
ScalarValues::*; ... }`, so the names in `expect` are written relative to that package
(`p::c|b|Sub::a` means `example::p::c | b | example::Sub::a`). The fence must parse, the
positional check must give exactly the stated findings, and an `expect="none"` example (a
by-name or definition-order form) must not be a self-named binding either.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pytest

from agentic_mbse.sysml.parameter_redefinition_extraction import extract_parameter_redefinitions
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.sysml.types import ValidationCode
from agentic_mbse.validation.level1_syntax import validate_syntax
from agentic_mbse.validation.level2_structure import validate_structure
from agentic_mbse.validation.positional_binding import decide
from tests.helpers.shipped import REPO_ROOT

SHIPPED_TREES = ("docs", "skills", "agents", "project_templates")
TEXT_SUFFIXES = (".md", ".template")
MARKER = "@positional-example"
MARKED_FENCE = re.compile(
    r"<!--\s*@positional-example\s+expect=\"(?P<expect>[^\"]*)\"\s*-->\n```sysml\n(?P<source>.*?)```",
    re.S,
)
WRAPPER = "example"

Identity = tuple[str, str, str]


@dataclass(frozen=True)
class Example:
    path: str
    line: int
    source: str
    expected: frozenset[Identity]


def shipped_text_files() -> list[Path]:
    return sorted(
        path
        for tree in SHIPPED_TREES
        for path in (REPO_ROOT / tree).rglob("*")
        if path.is_file() and path.name.endswith(TEXT_SUFFIXES)
    )


def parse_expect(expect: str) -> frozenset[Identity]:
    if expect.strip() == "none":
        return frozenset()
    identities = set()
    for entry in expect.split(";"):
        owner, input_, target = (part.strip() for part in entry.split("|"))
        identities.add((f"{WRAPPER}::{owner}", input_, f"{WRAPPER}::{target}"))
    return frozenset(identities)


def marked_fences(paths: list[Path]) -> list[Example]:
    examples = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for match in MARKED_FENCE.finditer(text):
            examples.append(
                Example(
                    path=path.relative_to(REPO_ROOT).as_posix(),
                    line=text.count("\n", 0, match.start()) + 1,
                    source=match["source"],
                    expected=parse_expect(match["expect"]),
                )
            )
    return examples


FILES = shipped_text_files()
EXAMPLES = marked_fences(FILES)


def write_wrapped(example: Example, root: Path) -> Path:
    models = root / "models"
    models.mkdir()
    body = "\n".join(f"    {line}" for line in example.source.splitlines())
    source = f"package {WRAPPER} {{\n    private import ScalarValues::*;\n{body}\n}}\n"
    (models / "example.sysml").write_text(source)
    return models


def positional_identities(models: Path) -> frozenset[Identity]:
    model, _ = SysideAdapter.load_model([models])
    result = decide(extract_parameter_redefinitions(model), None)
    assert not result.failures, result.failures
    return frozenset(
        (f.owner.qualified_name or "<none>", f.input_name, f.target.formal.qualified_name or "")
        for f in result.findings
    )


def test_marked_fences_exist_and_every_marker_heads_a_fence() -> None:
    marked_files = {e.path for e in EXAMPLES}
    assert {"docs/patterns/semantic-hazards.md", "docs/patterns/plant-idiom.md"} <= marked_files
    markers = sum(path.read_text(encoding="utf-8").count(MARKER) for path in FILES)
    assert markers == len(EXAMPLES), "a @positional-example marker is not directly above a fence"


@pytest.mark.parametrize("example", EXAMPLES, ids=lambda e: f"{e.path}:{e.line}")
def test_marked_example_has_exactly_its_stated_positional_findings(
    example: Example, tmp_path: Path
) -> None:
    models = write_wrapped(example, tmp_path)
    assert validate_syntax(str(models)).success
    assert positional_identities(models) == example.expected
    if not example.expected:
        codes = {issue.code for issue in validate_structure(str(models)).structured_issues}
        assert ValidationCode.L2_SELF_NAMED_BINDING not in codes
        assert ValidationCode.L2_POSITIONAL_BINDING not in codes
