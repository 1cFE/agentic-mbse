"""Which guard a project's `pyproject.toml` names, and what a broken configuration gives.

`load_holdout_guard` reads `[tool.agentic-mbse.research]` from the registry's
project root, never the current directory. No table, or an empty one, means
nothing is held out. Every fault gives a guard whose every check raises
`HoldoutGuardError`, never one that answers.
"""

import sys
from pathlib import Path

import pytest

from agentic_mbse.research import (
    LocalPdfSource,
    SourceMetadata,
    UrlSource,
    load_holdout_guard,
    register,
)
from agentic_mbse.research.holdout import (
    HoldoutGuardError,
    HoldoutHit,
    first_file_hit,
    first_term_hit,
    input_path_hit,
)
from tests.test_research.conftest import GUARD_FILE_SOURCE, SEALED_TOKEN, write_research_config

METADATA = SourceMetadata(
    title="Widget Coil Note",
    use_for="Synthetic winding-pack geometry; exercises the hook configuration.",
    validation="Not applicable: this is a configuration fixture.",
    caveat="A test fixture.",
)

#: A guard file that bars nothing.
PERMISSIVE_GUARD_SOURCE = """\
def check_input_path(path):
    return None


def scan_terms(text):
    return []


def scan_file(path):
    return []
"""


def _project(tmp_path: Path, pyproject: str | None, files: dict[str, str]) -> Path:
    """A project root holding `pyproject` (None for no file) and the given files."""
    root = tmp_path / "project"
    root.mkdir()
    if pyproject is not None:
        (root / "pyproject.toml").write_text(pyproject)
    for name, text in files.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    return root


def _research(body: str) -> str:
    return f"[tool.agentic-mbse.research]\n{body}\n"


def _answers(guard, tmp_path: Path) -> list[HoldoutHit | None]:
    """The guard's answer to each of its three checks, on inputs a sealing guard bars."""
    sample = tmp_path / "sample.md"
    sample.write_text(f"cites {SEALED_TOKEN}.pdf")
    return [
        input_path_hit(guard, Path("knowledge/sealed/paper.pdf")),
        first_term_hit(guard, f"cites {SEALED_TOKEN}.pdf"),
        first_file_hit(guard, sample),
    ]


# --- no configuration ----------------------------------------------------------------


@pytest.mark.parametrize(
    "pyproject",
    [
        pytest.param(None, id="no pyproject"),
        pytest.param('[project]\nname = "target"\n', id="no tool table"),
        pytest.param("[tool.agentic-mbse]\n", id="no research table"),
        pytest.param("[tool.agentic-mbse.research]\n", id="empty research table"),
    ],
)
def test_no_configured_guard_holds_nothing_out(pyproject, tmp_path):
    # A guard file sits beside the config, so only the config decides that none is loaded.
    root = _project(tmp_path, pyproject, {"guard.py": GUARD_FILE_SOURCE})
    assert _answers(load_holdout_guard(root), tmp_path) == [None, None, None]


# --- a configured guard file ------------------------------------------------------------


def test_a_guard_file_loads_and_answers_with_its_matches(tmp_path):
    """The guard uses a dataclass under postponed annotations, which needs its module registered."""
    root = _project(
        tmp_path, _research('holdout-guard = "guard.py"'), {"guard.py": GUARD_FILE_SOURCE}
    )

    assert _answers(load_holdout_guard(root), tmp_path) == [
        HoldoutHit(rule_id="path:*/sealed/*", count=1, offsets=(0,)),
        HoldoutHit(rule_id=f"term:{SEALED_TOKEN}", count=1, offsets=(6,)),
        HoldoutHit(rule_id=f"term:{SEALED_TOKEN}", count=1, offsets=(6,)),
    ]


def test_a_guard_file_answers_nothing_for_a_clean_input(tmp_path):
    root = _project(
        tmp_path, _research('holdout-guard = "guard.py"'), {"guard.py": GUARD_FILE_SOURCE}
    )
    guard = load_holdout_guard(root)
    assert input_path_hit(guard, Path("docs/widget.pdf")) is None
    assert first_term_hit(guard, "Widget Coil Note") is None


def test_a_guard_path_may_be_absolute(tmp_path):
    guard_file = tmp_path / "guards" / "guard.py"
    guard_file.parent.mkdir()
    guard_file.write_text(GUARD_FILE_SOURCE)
    root = _project(tmp_path, _research(f'holdout-guard = "{guard_file}"'), {})
    assert first_term_hit(load_holdout_guard(root), SEALED_TOKEN) is not None


# --- every fault gives a guard that raises ------------------------------------------------

FAULTS = [
    pytest.param(
        _research('holdout_guard = "guard.py"'),
        {"guard.py": GUARD_FILE_SOURCE},
        "unknown key 'holdout_guard' in [tool.agentic-mbse.research]",
        id="misspelled key",
    ),
    pytest.param(
        _research('holdout-guard = "guard.py"\nstrict = true'),
        {"guard.py": GUARD_FILE_SOURCE},
        "unknown key 'strict' in [tool.agentic-mbse.research]",
        id="unknown key beside the guard",
    ),
    pytest.param(
        _research('holdout-guard = ""'), {}, "holdout-guard must be a non-empty path", id="empty"
    ),
    pytest.param(
        _research('holdout-guard = "  "'), {}, "holdout-guard must be a non-empty path", id="blank"
    ),
    pytest.param(
        _research("holdout-guard = 3"), {}, "holdout-guard must be a non-empty path", id="integer"
    ),
    pytest.param(
        _research('holdout-guard = ["guard.py"]'),
        {"guard.py": GUARD_FILE_SOURCE},
        "holdout-guard must be a non-empty path",
        id="list",
    ),
    pytest.param(
        "[tool.agentic-mbse.research]\nholdout-guard = \n", {}, "cannot read", id="invalid TOML"
    ),
    pytest.param(
        '[tool.agentic-mbse]\nresearch = "guard.py"\n',
        {"guard.py": GUARD_FILE_SOURCE},
        "[tool.agentic-mbse.research] is not a table",
        id="research is not a table",
    ),
    pytest.param(
        '[tool.agentic-mbse.reseach]\nholdout-guard = "guard.py"\n',
        {"guard.py": GUARD_FILE_SOURCE},
        "unknown key 'reseach' in [tool.agentic-mbse]; its only key is 'research'",
        id="misspelled research table",
    ),
    pytest.param(
        '[tool.agentic-mbse]\nstrict = true\n\n[tool.agentic-mbse.research]\nholdout-guard = "guard.py"\n',
        {"guard.py": GUARD_FILE_SOURCE},
        "unknown key 'strict' in [tool.agentic-mbse]",
        id="unknown key beside the research table",
    ),
    pytest.param(
        '[tool.agentic_mbse.research]\nholdout-guard = "guard.py"\n',
        {"guard.py": GUARD_FILE_SOURCE},
        "[tool.agentic_mbse] is not read; the toolkit's table is [tool.agentic-mbse]",
        id="underscore toolkit table",
    ),
    pytest.param(
        '[tool.agentic_mbse]\nstrict = true\n\n[tool.agentic-mbse.research]\nholdout-guard = "guard.py"\n',
        {"guard.py": GUARD_FILE_SOURCE},
        "[tool.agentic_mbse] is not read",
        id="underscore table beside the right one",
    ),
    pytest.param("tool = 3\n", {}, "[tool] is not a table", id="tool is not a table"),
    pytest.param(
        "[tool]\nagentic-mbse = 3\n",
        {},
        "[tool.agentic-mbse] is not a table",
        id="toolkit table is not a table",
    ),
    pytest.param(_research('holdout-guard = "missing.py"'), {}, "no file at", id="missing file"),
    pytest.param(
        _research('holdout-guard = "guards"'),
        {"guards/keep.txt": ""},
        "no file at",
        id="a directory",
    ),
    pytest.param(
        _research('holdout-guard = "guard.txt"'),
        {"guard.txt": GUARD_FILE_SOURCE},
        "is not a Python module",
        id="not a Python file",
    ),
    pytest.param(
        _research('holdout-guard = "guard.py"'),
        {"guard.py": "raise RuntimeError('protocol file unreadable')\n"},
        "failed to load: RuntimeError: protocol file unreadable",
        id="raises on import",
    ),
    pytest.param(
        _research('holdout-guard = "guard.py"'),
        {"guard.py": "def scan_terms(:\n"},
        "failed to load: SyntaxError",
        id="syntax error",
    ),
    pytest.param(
        _research('holdout-guard = "guards/guard.py"'),
        {
            "guards/guard.py": GUARD_FILE_SOURCE + "\nimport guard_helpers_sibling\n",
            "guards/guard_helpers_sibling.py": "",
        },
        "failed to load: ModuleNotFoundError",
        id="imports a sibling module",
    ),
    pytest.param(
        _research('holdout-guard = "guard.py"'),
        {"guard.py": GUARD_FILE_SOURCE.replace("def scan_file", "def _scan_file")},
        "lacks scan_file",
        id="missing function",
    ),
    pytest.param(
        _research('holdout-guard = "guard.py"'),
        {"guard.py": GUARD_FILE_SOURCE + "\nscan_terms = None\n"},
        "lacks scan_terms",
        id="function is not callable",
    ),
]


@pytest.mark.parametrize(("pyproject", "files", "fragment"), FAULTS)
def test_every_fault_gives_a_guard_whose_every_check_raises(pyproject, files, fragment, tmp_path):
    guard = load_holdout_guard(_project(tmp_path, pyproject, files))

    sample = tmp_path / "sample.md"
    sample.write_text("nothing barred here")
    checks = [
        lambda: input_path_hit(guard, Path("docs/widget.pdf")),
        lambda: first_term_hit(guard, "Widget Coil Note"),
        lambda: first_file_hit(guard, sample),
    ]
    for check in checks:
        with pytest.raises(HoldoutGuardError) as raised:
            check()
        assert str(raised.value).startswith("hold-out guard unavailable: ")
        assert fragment in str(raised.value)


@pytest.mark.parametrize(
    "guard_source",
    [
        pytest.param("raise RuntimeError('protocol file unreadable')\n", id="raises on import"),
        pytest.param(
            GUARD_FILE_SOURCE.replace("def scan_file", "def _scan_file"), id="missing function"
        ),
        pytest.param("import guard_helpers_sibling\n", id="imports a sibling module"),
    ],
)
def test_a_failed_load_leaves_no_module_behind(guard_source, tmp_path):
    root = _project(
        tmp_path,
        _research('holdout-guard = "guard.py"'),
        {"guard.py": guard_source, "guard_helpers_sibling.py": ""},
    )
    before = set(sys.modules)
    load_holdout_guard(root)
    assert set(sys.modules) - before == set()


# --- whose configuration is read ----------------------------------------------------------


def test_the_config_is_read_from_the_registry_project_root_not_the_cwd(
    local_site, knowledge_tree, tmp_path, monkeypatch
):
    """A broken config in the current directory would refuse; the tree's project has none."""
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    write_research_config(elsewhere, 'holdout_guard = "guard.py"')
    monkeypatch.chdir(elsewhere)

    result = register(
        UrlSource(url=local_site.url("utf8.html")), METADATA, paths=knowledge_tree.paths
    )
    assert result.outcome == "registered", result.reason


def test_a_relative_guard_path_resolves_against_the_project_root(
    knowledge_tree, generated_pdf, tmp_path, monkeypatch
):
    """The current directory holds a permissive `guard.py`; the project's own one bars the title."""
    root = knowledge_tree.paths.project_root
    write_research_config(root, 'holdout-guard = "guard.py"')
    (root / "guard.py").write_text(GUARD_FILE_SOURCE)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (elsewhere / "guard.py").write_text(PERMISSIVE_GUARD_SOURCE)
    monkeypatch.chdir(elsewhere)

    result = register(
        LocalPdfSource(path=generated_pdf),
        SourceMetadata(
            title=f"Notes on {SEALED_TOKEN}",
            use_for=METADATA.use_for,
            validation=METADATA.validation,
            caveat=METADATA.caveat,
        ),
        paths=knowledge_tree.paths,
    )
    assert result.outcome == "holdout_hit"
    assert result.rule_id == f"term:{SEALED_TOKEN}"
