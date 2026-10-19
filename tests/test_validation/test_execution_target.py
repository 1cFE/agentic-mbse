"""The execution target and its severity table (Item 3 design D2, D3, invariant I2)."""

import re
from pathlib import Path

import pytest
import tomllib

from agentic_mbse.project_settings import SettingsFault
from agentic_mbse.validation.execution_target import (
    LEGACY_CATEGORY,
    Category,
    Display,
    FromFile,
    FromOverride,
    Target,
    TargetFault,
    TargetResolution,
    TargetSettingError,
    Unset,
    describe_target,
    display,
    lowered_under_native,
    resolve_target,
)

REPO = Path(__file__).resolve().parents[2]
W, E, S, C, B = (
    Display.WARNING,
    Display.ERROR,
    Display.NATIVE_SUMMARY,
    Display.COUNT_ONLY,
    Display.BASE,
)
U, G, N = Target.UNSET, Target.GENERATED, Target.NATIVE

# Copied cell by cell from design.md "The severity table".
EXPECTED = {
    (Category.REFUSED, U): W,
    (Category.REFUSED, G): E,
    (Category.REFUSED, N): S,
    (Category.UNCONFIRMED, U): W,
    (Category.UNCONFIRMED, G): W,
    (Category.UNCONFIRMED, N): S,
    (Category.EXCLUDED, U): W,
    (Category.EXCLUDED, G): W,
    (Category.EXCLUDED, N): S,
    (Category.OMITTED, U): W,
    (Category.OMITTED, G): W,
    (Category.OMITTED, N): S,
    (Category.ADMITTED, U): C,
    (Category.ADMITTED, G): C,
    (Category.ADMITTED, N): C,
    (Category.UNVERIFIED, U): W,
    (Category.UNVERIFIED, G): E,
    (Category.UNVERIFIED, N): W,
    (Category.UNASSESSED, U): W,
    (Category.UNASSESSED, G): W,
    (Category.UNASSESSED, N): S,
    (Category.ADVISORY, U): W,
    (Category.ADVISORY, G): W,
    (Category.ADVISORY, N): S,
    (Category.ADVISORY_UNVERIFIED, U): W,
    (Category.ADVISORY_UNVERIFIED, G): W,
    (Category.ADVISORY_UNVERIFIED, N): W,
    (Category.LEGACY_OWN_APPLICABILITY, U): B,
    (Category.LEGACY_OWN_APPLICABILITY, G): B,
    (Category.LEGACY_OWN_APPLICABILITY, N): B,
    (Category.LEGACY_KEPT, U): B,
    (Category.LEGACY_KEPT, G): B,
    (Category.LEGACY_KEPT, N): B,
    (Category.LEGACY_GENERATOR_ONLY, U): B,
    (Category.LEGACY_GENERATOR_ONLY, G): B,
    (Category.LEGACY_GENERATOR_ONLY, N): S,
    (Category.CHECK_FAILURE, U): E,
    (Category.CHECK_FAILURE, G): E,
    (Category.CHECK_FAILURE, N): E,
    (Category.CHECK_UNVERIFIED, U): W,
    (Category.CHECK_UNVERIFIED, G): W,
    (Category.CHECK_UNVERIFIED, N): W,
    (Category.SETTING_INVALID, U): E,
    (Category.SETTING_INVALID, G): E,
    (Category.SETTING_INVALID, N): E,
}


def test_display_matches_every_cell():
    assert {(c, t): display(c, t) for c in Category for t in Target} == EXPECTED


@pytest.mark.parametrize("category", [Category.CHECK_FAILURE, Category.SETTING_INVALID])
def test_check_failure_and_setting_invalid_are_error_everywhere(category):
    assert {display(category, t) for t in Target} == {Display.ERROR}
    summarized = {c for c in Category if display(c, Target.NATIVE) is Display.NATIVE_SUMMARY}
    assert category not in summarized


def test_legacy_category_covers_exactly_the_17_l6_codes():
    """The codes the legacy L6 checks emit, read from their source, are exactly the mapping's keys."""
    emitted = set()
    for name in ("level6_architecture.py", "adr002.py"):
        source = (REPO / "src/agentic_mbse/validation" / name).read_text()
        emitted |= set(re.findall(r"ValidationCode\.([A-Z0-9_]+)", source))
    new_codes = {"L6_CHECK_ERROR", "L6_SETTING_INVALID"} | {
        code for code in emitted if code.startswith("L6_SUBSET_")
    }
    assert {code.value for code in LEGACY_CATEGORY} == emitted - new_codes
    assert len(LEGACY_CATEGORY) == 17
    assert set(LEGACY_CATEGORY.values()) <= {
        Category.LEGACY_OWN_APPLICABILITY,
        Category.LEGACY_KEPT,
        Category.LEGACY_GENERATOR_ONLY,
    }


def test_lowered_set_equals_native_lowered_fixture():
    fixture = tomllib.loads((REPO / "tests/fixtures/l6/native_lowered.toml").read_text())
    assert lowered_under_native(LEGACY_CATEGORY) == frozenset(fixture["lowered"])


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


LOWERED = frozenset(
    {
        "L6_MISSING_QUALIFIED_NAME",
        "L6_ANONYMOUS_RETURN",
        "L6_CALC_DEF_NO_INSTANTIATION",
        "L6_BODY_ASSIGNMENT_IMPL_LOSS",
    }
)


def test_lowered_set_is_exactly_the_four_evidenced_codes():
    assert lowered_under_native(LEGACY_CATEGORY) == LOWERED
    fixture = tomllib.loads((REPO / "tests/fixtures/l6/native_lowered.toml").read_text())
    assert frozenset(fixture["lowered"]) == LOWERED


def _audit() -> Path:
    """The legacy-check audit, under `.project/active/` now and `.project/completed/` after close."""
    (path,) = REPO.glob(".project/*/*l6-subset-profile/evidence/legacy-l6-audit.md")
    return path


def test_audit_lowered_table_matches_fixture():
    text = _audit().read_text(encoding="utf-8")
    section = text.split("## Lowered under native", 1)[1].split("\n## ", 1)[0]
    codes = re.findall(r"^\| `([A-Z0-9_]+)` \|", section, flags=re.MULTILINE)
    assert frozenset(codes) == lowered_under_native(LEGACY_CATEGORY)
    assert len(codes) == len(set(codes))


def test_audit_has_one_row_per_legacy_code_plus_manifest_and_setup():
    text = _audit().read_text(encoding="utf-8")
    section = text.split("## Every legacy L6 code", 1)[1].split("\n## ", 1)[0]
    first_cells = re.findall(r"^\| ([^|]+?) \|", section, flags=re.MULTILINE)
    codes = {cell.split("`")[1] for cell in first_cells if cell.startswith("`")}
    assert codes == {code.value for code in LEGACY_CATEGORY}
    assert {"Manifest failures", "Setup failures"} <= set(first_cells)
