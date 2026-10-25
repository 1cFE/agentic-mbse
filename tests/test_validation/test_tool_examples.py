"""Every complete SysML example in the shipped guidance runs through both tools and does what it says.

A complete example is a fence that parses on its own, or inside the standard wrapper below. Each
one carries a marker directly above it (other `<!-- ... -->` markers may sit between):

    <!-- @tool-example -->                       passes both tools
    <!-- @tool-example fails="CODE[,CODE]" -->   a wrong-way example; each code must appear
    <!-- @tool-example dir="designs" ... -->     the file goes under models/designs/, not library/
    <!-- @tool-example defect="CODE" -->         a correct example validate wrongly rejects with
                                                 CODE; pinned so the fix flips this test

Passing means: `agentic-mbse validate --complete` reports no ERROR-severity issue (an unused
definition is only a warning, which an isolated example always has), and `sysml-codegen check`
exits 0 with no "manual stub" warning, or reports there is nothing to generate. A code starting
`SI_`, `block_` or `REGISTRY_` is the generator's and is looked for in the check output; any other
code is looked for among validate's ERROR codes.

The check half runs `sysml-codegen` as a subprocess, found by the `SYSML_CODEGEN` environment
variable or on PATH, and skips when it is absent. agentic-mbse never imports sysml_codegen.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

from agentic_mbse.cli import main as cli_main
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from tests.helpers.shipped import REPO_ROOT

SHIPPED_TREES = ("docs", "skills", "agents", "project_templates")
TEXT_SUFFIXES = (".md", ".template")
FENCE = re.compile(r"```sysml\n(.*?)```", re.S)
MARKED = re.compile(
    r"<!--\s*@tool-example(?P<attrs>[^>]*?)-->\n(?:<!--[^\n]*-->\n)*```sysml\n(?P<source>.*?)```",
    re.S,
)
ATTR = re.compile(r'(\w+)="([^"]*)"')
WRAP_HEAD = (
    "package example {\n"
    "    private import ScalarValues::*;\n"
    "    private import SI::*;\n"
    "    private import NumericalFunctions::*;\n"
)
NOTHING_TO_GENERATE = "There is nothing to generate"
GENERATOR_PREFIXES = ("SI_", "block_", "REGISTRY_")


@dataclass(frozen=True)
class Example:
    path: str
    line: int
    source: str
    fails: tuple[str, ...]
    subdir: str
    defects: frozenset[str] = frozenset()

    @property
    def generator_codes(self) -> list[str]:
        return [c for c in self.fails if c.startswith(GENERATOR_PREFIXES)]

    @property
    def validate_codes(self) -> list[str]:
        return [c for c in self.fails if not c.startswith(GENERATOR_PREFIXES)]


def shipped_text_files() -> list[Path]:
    return sorted(
        path
        for tree in SHIPPED_TREES
        for path in (REPO_ROOT / tree).rglob("*")
        if path.is_file() and path.name.endswith(TEXT_SUFFIXES)
    )


def wrap(source: str) -> str:
    body = "\n".join(f"    {line}" for line in source.splitlines())
    return f"{WRAP_HEAD}{body}\n}}\n"


def loads_cleanly(text: str, root: Path) -> bool:
    path = root / "probe.sysml"
    path.write_text(text, encoding="utf-8")
    _, diagnostics = SysideAdapter.load_model([path])
    return not diagnostics.contains_errors()


def complete_form(source: str, root: Path) -> str | None:
    """The source as it loads (standalone, else wrapped), or None for a fragment."""
    if loads_cleanly(source, root):
        return source
    wrapped = wrap(source)
    return wrapped if loads_cleanly(wrapped, root) else None


def marked_examples(paths: list[Path]) -> list[Example]:
    examples = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for match in MARKED.finditer(text):
            attrs = dict(ATTR.findall(match["attrs"]))
            fails = tuple(c.strip() for c in attrs.get("fails", "").split(",") if c.strip())
            examples.append(
                Example(
                    path=path.relative_to(REPO_ROOT).as_posix(),
                    line=text.count("\n", 0, match.start("source")),
                    source=match["source"],
                    fails=fails,
                    subdir=attrs.get("dir", "library"),
                    defects=frozenset(c for c in attrs.get("defect", "").split(",") if c),
                )
            )
    return examples


FILES = shipped_text_files()
EXAMPLES = marked_examples(FILES)


def write_models(example: Example, root: Path) -> Path:
    form = complete_form(example.source, root)
    assert form is not None, "a marked example must parse on its own or in the standard wrapper"
    models = root / "models"
    (models / example.subdir).mkdir(parents=True)
    (models / example.subdir / "example.sysml").write_text(form, encoding="utf-8")
    return models


def codegen() -> str | None:
    return os.environ.get("SYSML_CODEGEN") or shutil.which("sysml-codegen")


def test_every_marker_heads_a_fence_and_every_complete_fence_is_marked(tmp_path: Path) -> None:
    markers = sum(path.read_text(encoding="utf-8").count("@tool-example") for path in FILES)
    assert markers == len(EXAMPLES), "a @tool-example marker is not directly above a fence"
    marked = {(e.path, e.source) for e in EXAMPLES}
    unmarked_complete = []
    for path in FILES:
        rel = path.relative_to(REPO_ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        for match in FENCE.finditer(text):
            if (rel, match[1]) in marked:
                continue
            if complete_form(match[1], tmp_path) is not None:
                unmarked_complete.append(f"{rel}:{text.count(chr(10), 0, match.start()) + 1}")
    assert unmarked_complete == [], "complete examples without a @tool-example marker"


@pytest.mark.syside
@pytest.mark.parametrize("example", EXAMPLES, ids=lambda e: f"{e.path}:{e.line}")
def test_example_under_validate(example: Example, tmp_path: Path) -> None:
    models = write_models(example, tmp_path)
    report = tmp_path / "report.json"
    cli_main(
        [
            "validate",
            "--complete",
            "--execution-target=generated",
            f"--json-report={report}",
            str(models),
        ]
    )
    levels = json.loads(report.read_text(encoding="utf-8"))["levels"]
    errors = {i["code"] for lvl in levels for i in lvl["issues"] if i["severity"] == "error"}
    syntax_ok = next(lvl for lvl in levels if lvl["level"] == 1)["status"] == "passed"
    assert syntax_ok
    if example.fails:
        assert set(example.validate_codes) <= errors, errors
    else:
        assert errors == example.defects


@pytest.mark.syside
@pytest.mark.parametrize("example", EXAMPLES, ids=lambda e: f"{e.path}:{e.line}")
def test_example_under_generator_check(example: Example, tmp_path: Path) -> None:
    tool = codegen()
    if tool is None:
        pytest.skip("sysml-codegen not found (set SYSML_CODEGEN or put it on PATH)")
    models = write_models(example, tmp_path)
    run = subprocess.run(
        [tool, "check", "--models", str(models)], capture_output=True, text=True, check=False
    )
    output = run.stdout + run.stderr
    if example.generator_codes:
        assert run.returncode == 1, output
        for code in example.generator_codes:
            assert code in output, output
    elif not example.fails:
        built = run.returncode == 0 or (run.returncode == 1 and NOTHING_TO_GENERATE in output)
        assert built, output
        assert "manual stub" not in output, output
