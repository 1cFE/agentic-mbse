"""The shared `[tool.agentic-mbse]` reader (Item 3 design D1, invariant I6).

One key set for the toolkit's table; the reader checks shapes and key membership, never values.
"""

from pathlib import Path

import pytest

from agentic_mbse.project_settings import (
    TOOLKIT_KEYS,
    SettingsDefect,
    SettingsFault,
    ToolkitTable,
    read_toolkit_table,
)


def _root(tmp_path: Path, pyproject: str | bytes | None) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    if isinstance(pyproject, bytes):
        (root / "pyproject.toml").write_bytes(pyproject)
    elif pyproject is not None:
        (root / "pyproject.toml").write_text(pyproject)
    return root


def _defect(tmp_path: Path, pyproject: str | bytes) -> SettingsDefect:
    result = read_toolkit_table(_root(tmp_path, pyproject))
    assert isinstance(result, SettingsDefect), result
    return result


def test_toolkit_keys_are_exactly_execution_target_and_research():
    assert TOOLKIT_KEYS == {"execution-target", "research"}


def test_both_keys_are_read(tmp_path):
    root = _root(
        tmp_path,
        '[tool.agentic-mbse]\nexecution-target = "generated"\n\n'
        '[tool.agentic-mbse.research]\nholdout-guard = "guard.py"\n',
    )
    assert read_toolkit_table(root) == ToolkitTable(
        root / "pyproject.toml",
        {"execution-target": "generated", "research": {"holdout-guard": "guard.py"}},
    )


@pytest.mark.parametrize("key", ["execution_target", "executiontarget"])
def test_unknown_key_is_a_defect_naming_key_and_allowed_set(tmp_path, key):
    defect = _defect(tmp_path, f'[tool.agentic-mbse]\n{key} = "generated"\n')
    assert defect.fault is SettingsFault.UNKNOWN_KEY
    assert f"unknown key '{key}' in [tool.agentic-mbse]" in defect.detail
    assert "allowed keys are 'execution-target', 'research'" in defect.detail
    assert str(defect.path) in defect.detail


def test_underscore_table_is_a_defect(tmp_path):
    defect = _defect(tmp_path, '[tool.agentic_mbse]\nexecution-target = "generated"\n')
    assert defect.fault is SettingsFault.UNDERSCORE_TABLE
    assert "[tool.agentic_mbse] is not read; the toolkit's table is [tool.agentic-mbse]" in (
        defect.detail
    )


def test_reseach_subtable_typo_is_a_defect(tmp_path):
    defect = _defect(tmp_path, '[tool.agentic-mbse.reseach]\nholdout-guard = "guard.py"\n')
    assert defect.fault is SettingsFault.UNKNOWN_KEY
    assert "unknown key 'reseach'" in defect.detail


@pytest.mark.parametrize(
    "pyproject",
    [
        pytest.param(None, id="no file"),
        pytest.param('[project]\nname = "x"\n', id="no tool table"),
        pytest.param("[tool.ruff]\nline-length = 100\n", id="no toolkit table"),
        pytest.param("[tool.agentic-mbse]\n", id="empty toolkit table"),
    ],
)
def test_absent_file_or_table_is_an_empty_table_not_a_defect(tmp_path, pyproject):
    root = _root(tmp_path, pyproject)
    assert read_toolkit_table(root) == ToolkitTable(root / "pyproject.toml", {})


def test_malformed_toml_is_a_defect_with_path_and_parse_error(tmp_path):
    defect = _defect(tmp_path, "[tool.agentic-mbse]\nexecution-target = \n")
    assert defect.fault is SettingsFault.TOML_SYNTAX
    assert defect.detail.startswith(f"cannot read {defect.path}: ")
    assert "line 2" in defect.detail


def test_non_utf8_file_is_unreadable(tmp_path):
    defect = _defect(tmp_path, b'[tool.agentic-mbse]\nexecution-target = "\xff"\n')
    assert defect.fault is SettingsFault.UNREADABLE
    assert defect.detail.startswith(f"cannot read {defect.path}: ")


@pytest.mark.parametrize(
    ("pyproject", "table"),
    [
        pytest.param("tool = 3\n", "[tool]", id="tool"),
        pytest.param("[tool]\nagentic-mbse = 3\n", "[tool.agentic-mbse]", id="toolkit"),
    ],
)
def test_non_table_is_a_defect(tmp_path, pyproject, table):
    defect = _defect(tmp_path, pyproject)
    assert defect.fault is SettingsFault.NOT_A_TABLE
    assert defect.detail == f"{defect.path}: {table} is not a table"


@pytest.mark.parametrize(
    "body",
    [
        "execution-target = 1",
        'execution-target = "generate"',
        'execution-target = ""',
        'research = "not a table"',
    ],
)
def test_reader_never_checks_values(tmp_path, body):
    root = _root(tmp_path, f"[tool.agentic-mbse]\n{body}\n")
    assert isinstance(read_toolkit_table(root), ToolkitTable)
