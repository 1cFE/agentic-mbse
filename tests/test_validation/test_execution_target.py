"""The execution target: how it is resolved."""

from pathlib import Path

import pytest

from agentic_mbse.project_settings import SettingsFault
from agentic_mbse.validation.execution_target import (
    FromFile,
    FromOverride,
    Target,
    TargetFault,
    TargetResolution,
    TargetSettingError,
    Unset,
    describe_target,
    resolve_target,
)

REPO = Path(__file__).resolve().parents[2]


# --- resolving the target ---------------------------------------------------------------


def _project(tmp_path: Path, pyproject: str | None) -> Path:
    """A project root (marked by work/BACKLOG.md) with a models/ folder; returns models/."""
    root = tmp_path / "project"
    (root / "work").mkdir(parents=True)
    (root / "work" / "BACKLOG.md").write_text("# Backlog\n")
    (root / "models").mkdir()
    if pyproject is not None:
        (root / "pyproject.toml").write_text(pyproject)
    return root / "models"


def _table(value: str) -> str:
    return f"[tool.agentic-mbse]\nexecution-target = {value}\n"


@pytest.mark.parametrize("value", ["generated", "native"])
def test_resolve_target_from_file(tmp_path, value):
    models = _project(tmp_path, _table(f'"{value}"'))
    pyproject = models.parent / "pyproject.toml"
    resolution = resolve_target(models, None)
    assert resolution == TargetResolution(Target(value), FromFile(pyproject), models.parent)
    assert describe_target(resolution) == f"{value} (from {pyproject})"


@pytest.mark.parametrize("pyproject", [None, '[project]\nname = "x"\n', "[tool.agentic-mbse]\n"])
def test_resolve_target_unset_names_the_file_looked_at(tmp_path, pyproject):
    models = _project(tmp_path, pyproject)
    path = models.parent / "pyproject.toml"
    resolution = resolve_target(models, None)
    assert resolution == TargetResolution(Target.UNSET, Unset(path), models.parent)
    assert describe_target(resolution) == f"unset (no execution-target in {path})"


@pytest.mark.parametrize(
    ("file_value", "override"), [("generated", Target.NATIVE), ("native", Target.GENERATED)]
)
def test_override_wins_and_says_what_the_file_says(tmp_path, file_value, override):
    models = _project(tmp_path, _table(f'"{file_value}"'))
    resolution = resolve_target(models, override)
    assert resolution == TargetResolution(
        override, FromOverride(models.parent / "pyproject.toml", file_value), models.parent
    )
    assert describe_target(resolution) == (
        f"{override.value} (override --execution-target; file says {file_value})"
    )


def test_override_with_no_value_in_the_file(tmp_path):
    models = _project(tmp_path, None)
    resolution = resolve_target(models, Target.NATIVE)
    path = models.parent / "pyproject.toml"
    assert describe_target(resolution) == f"native (override --execution-target; {path} sets none)"


@pytest.mark.parametrize("override", [None, Target.GENERATED, Target.NATIVE])
def test_override_with_malformed_file_is_still_an_error(tmp_path, override):
    models = _project(tmp_path, "[tool.agentic-mbse]\nexecution-target = \n")
    error = resolve_target(models, override)
    assert isinstance(error, TargetSettingError)
    assert error.fault is TargetFault.SETTINGS
    assert error.settings_fault is SettingsFault.TOML_SYNTAX
    assert str(models.parent / "pyproject.toml") in error.detail


@pytest.mark.parametrize("override", [None, Target.NATIVE])
@pytest.mark.parametrize(
    ("value", "shown"), [('"generate"', "'generate'"), ("1", "1"), ('""', "''")]
)
def test_invalid_value_names_value_and_both_allowed(tmp_path, value, shown, override):
    models = _project(tmp_path, _table(value))
    error = resolve_target(models, override)
    assert isinstance(error, TargetSettingError)
    assert error.fault is TargetFault.INVALID_VALUE
    assert f"execution-target = {shown} is not allowed" in error.detail
    assert "allowed values are 'generated' and 'native'" in error.detail


@pytest.mark.parametrize(
    "pyproject",
    [
        '[tool.agentic-mbse]\nexecution_target = "native"\n',
        '[tool.agentic_mbse]\nexecution-target = "native"\n',
        '[tool.agentic-mbse.reseach]\nholdout-guard = "g.py"\n',
    ],
)
def test_unknown_key_or_underscore_table_is_an_error(tmp_path, pyproject):
    error = resolve_target(_project(tmp_path, pyproject), Target.GENERATED)
    assert isinstance(error, TargetSettingError)
    assert error.fault is TargetFault.SETTINGS


def test_bad_holdout_guard_is_not_a_target_error(tmp_path):
    models = _project(tmp_path, '[tool.agentic-mbse.research]\nholdout-guard = "missing.py"\n')
    resolution = resolve_target(models, None)
    assert isinstance(resolution, TargetResolution)
    assert resolution.target is Target.UNSET


def test_no_root_resolves_unset_with_looked_at_none(tmp_path):
    models = tmp_path / "loose" / "models"
    models.mkdir(parents=True)
    resolution = resolve_target(models, None)
    assert resolution == TargetResolution(Target.UNSET, Unset(None), None)
    assert describe_target(resolution) == (
        "unset (no project root above models; pass --execution-target)"
    )
    overridden = resolve_target(models, Target.GENERATED)
    assert overridden == TargetResolution(Target.GENERATED, FromOverride(None, None), None)
    assert describe_target(overridden) == (
        "generated (override --execution-target; no project root above models)"
    )


def test_subdirectory_reads_root_file_and_ignores_nested_pyproject(tmp_path):
    models = _project(tmp_path, _table('"generated"'))
    nested = models / "designs" / "pump"
    nested.mkdir(parents=True)
    (models / "designs" / "pyproject.toml").write_text(_table('"native"'))
    resolution = resolve_target(nested, None)
    assert resolution == TargetResolution(
        Target.GENERATED, FromFile(models.parent / "pyproject.toml"), models.parent
    )


def test_unset_is_not_an_override(tmp_path):
    with pytest.raises(ValueError, match="unset is no override"):
        resolve_target(_project(tmp_path, None), Target.UNSET)
