"""The positional pin list: strict parsing, root-only discovery and the pin root.

Pure file tests, no SysIDE. The pin list is TOML, schema `positional-pins/v1`, closed at every
level (design D10); it is found only at the project root (D11); and its `file` paths resolve
against a pin root, the pin file's directory unless one is given (D12).
"""

from __future__ import annotations

from datetime import date
from pathlib import Path, PurePosixPath

import pytest

from agentic_mbse.project_root import find_project_root
from agentic_mbse.validation.positional_pins import (
    PIN_FILE_NAME,
    FindingIdentity,
    Pin,
    PinList,
    PinListAbsent,
    PinListDefect,
    PinListInvalid,
    discover,
    load,
)

HEADER = """\
schema = "positional-pins/v1"
[recorded_against]
revision = "f96ad312c63e8c66695971b12feab971f3ba6eb3"
date = 2026-10-15
"""

PIN_B = """\
[[pin]]
owner = "P::q::c"
input = "b"
target = "P::Sub::a"
file = "models/b.sysml"
line = 12
"""

PIN_A = """\
[[pin]]
owner = "P::q::c"
input = "a"
target = "P::Sub::b"
file = "models/a.sysml"
line = 7
"""

VALID = HEADER + PIN_B + PIN_A


def write(directory: Path, text: str, name: str = PIN_FILE_NAME) -> Path:
    path = directory / name
    path.write_text(text)
    return path


def invalid(tmp_path: Path, text: str) -> PinListInvalid:
    result = load(write(tmp_path, text), pin_root=tmp_path)
    assert isinstance(result, PinListInvalid), result
    return result


# ---- the stencil cases -----------------------------------------------------------------------


def test_unknown_key_in_a_pin_is_invalid(tmp_path: Path) -> None:
    result = invalid(tmp_path, HEADER + PIN_B + 'note = "x"\n')
    assert result.reason_code is PinListDefect.UNKNOWN_KEY
    assert "pin[0]" in result.detail and "note" in result.detail


def test_discovery_ignores_a_pin_file_below_the_root(tmp_path: Path) -> None:
    (tmp_path / "work").mkdir()
    (tmp_path / "work" / "BACKLOG.md").write_text("")
    (tmp_path / "models" / "x").mkdir(parents=True)
    write(tmp_path / "models" / "x", VALID)
    assert discover(tmp_path / "models" / "x") == PinListAbsent(
        project_root=tmp_path, looked_at=tmp_path / PIN_FILE_NAME
    )


# ---- a valid list ----------------------------------------------------------------------------


def test_a_valid_list_round_trips_with_pins_sorted_by_identity(tmp_path: Path) -> None:
    path = write(tmp_path, VALID)
    result = load(path, pin_root=tmp_path)
    assert result == PinList(
        path=path,
        pin_root=tmp_path,
        revision="f96ad312c63e8c66695971b12feab971f3ba6eb3",
        recorded=date(2026, 10, 15),
        pins=(
            Pin(FindingIdentity("P::q::c", "a", "P::Sub::b"), PurePosixPath("models/a.sysml"), 7),
            Pin(FindingIdentity("P::q::c", "b", "P::Sub::a"), PurePosixPath("models/b.sysml"), 12),
        ),
    )


def test_entry_order_does_not_change_the_result(tmp_path: Path) -> None:
    forward = load(write(tmp_path, HEADER + PIN_A + PIN_B, "f.toml"), pin_root=tmp_path)
    backward = load(write(tmp_path, HEADER + PIN_B + PIN_A, "b.toml"), pin_root=tmp_path)
    assert isinstance(forward, PinList) and isinstance(backward, PinList)
    assert forward.pins == backward.pins


def test_a_list_with_no_pins_is_valid(tmp_path: Path) -> None:
    result = load(write(tmp_path, HEADER), pin_root=tmp_path)
    assert isinstance(result, PinList) and result.pins == ()


def test_quoted_names_survive_parsing(tmp_path: Path) -> None:
    text = HEADER + PIN_B.replace(
        'target = "P::Sub::a"',
        "target = \"integrated_heat_electricity::'Network Heat Driven Closure'::divertor_available_in\"",
    )
    result = load(write(tmp_path, text), pin_root=tmp_path)
    assert isinstance(result, PinList)
    assert result.pins[0].identity.target == (
        "integrated_heat_electricity::'Network Heat Driven Closure'::divertor_available_in"
    )


# ---- every defect is invalid with its own reason ---------------------------------------------


def test_an_unreadable_file_is_invalid(tmp_path: Path) -> None:
    result = load(tmp_path / "missing.toml", pin_root=tmp_path)
    assert isinstance(result, PinListInvalid)
    assert result.reason_code is PinListDefect.UNREADABLE


def test_a_directory_in_place_of_the_file_is_unreadable(tmp_path: Path) -> None:
    (tmp_path / "dir.toml").mkdir()
    result = load(tmp_path / "dir.toml", pin_root=tmp_path)
    assert isinstance(result, PinListInvalid)
    assert result.reason_code is PinListDefect.UNREADABLE


def test_non_utf8_bytes_are_unreadable(tmp_path: Path) -> None:
    path = tmp_path / PIN_FILE_NAME
    path.write_bytes(b'schema = "\xff"\n')
    result = load(path, pin_root=tmp_path)
    assert isinstance(result, PinListInvalid)
    assert result.reason_code is PinListDefect.UNREADABLE


def test_a_toml_syntax_error_is_invalid(tmp_path: Path) -> None:
    assert invalid(tmp_path, HEADER + "[[pin]\n").reason_code is PinListDefect.TOML_SYNTAX


def test_a_missing_schema_is_invalid(tmp_path: Path) -> None:
    text = HEADER.replace('schema = "positional-pins/v1"\n', "")
    assert invalid(tmp_path, text).reason_code is PinListDefect.SCHEMA_MISSING


def test_a_wrong_schema_is_invalid(tmp_path: Path) -> None:
    text = VALID.replace("positional-pins/v1", "positional-pins/v2")
    assert invalid(tmp_path, text).reason_code is PinListDefect.SCHEMA_UNSUPPORTED


def test_a_non_string_schema_is_a_wrong_type(tmp_path: Path) -> None:
    text = VALID.replace('schema = "positional-pins/v1"', "schema = 1")
    assert invalid(tmp_path, text).reason_code is PinListDefect.WRONG_TYPE


@pytest.mark.parametrize(
    "text",
    [
        'schema = "positional-pins/v1"\n' + PIN_B,
        HEADER.replace('revision = "f96ad312c63e8c66695971b12feab971f3ba6eb3"\n', ""),
        HEADER.replace("date = 2026-10-15\n", ""),
    ],
    ids=["table", "revision", "date"],
)
def test_a_missing_recorded_against_part_is_invalid(tmp_path: Path, text: str) -> None:
    assert invalid(tmp_path, text).reason_code is PinListDefect.RECORDED_AGAINST_MISSING


def test_recorded_against_as_a_string_is_a_wrong_type(tmp_path: Path) -> None:
    text = 'schema = "positional-pins/v1"\nrecorded_against = "f96ad312"\n'
    assert invalid(tmp_path, text).reason_code is PinListDefect.WRONG_TYPE


def test_an_empty_revision_is_invalid(tmp_path: Path) -> None:
    text = VALID.replace('revision = "f96ad312c63e8c66695971b12feab971f3ba6eb3"', 'revision = ""')
    assert invalid(tmp_path, text).reason_code is PinListDefect.REVISION_EMPTY


def test_a_non_string_revision_is_a_wrong_type(tmp_path: Path) -> None:
    text = VALID.replace('revision = "f96ad312c63e8c66695971b12feab971f3ba6eb3"', "revision = 5")
    assert invalid(tmp_path, text).reason_code is PinListDefect.WRONG_TYPE


@pytest.mark.parametrize("value", ['"2026-10-15"', "2026-10-15T10:00:00", "10:00:00", "20261015"])
def test_a_date_that_is_not_a_toml_date_is_invalid(tmp_path: Path, value: str) -> None:
    text = VALID.replace("date = 2026-10-15", f"date = {value}")
    assert invalid(tmp_path, text).reason_code is PinListDefect.DATE_NOT_A_DATE


@pytest.mark.parametrize(
    "text, where",
    [
        (VALID + 'extra = "x"\n', "pin[1]"),
        ('note = "x"\n' + VALID, "top level"),
        (
            VALID.replace("date = 2026-10-15\n", 'date = 2026-10-15\nnote = "x"\n'),
            "recorded_against",
        ),
    ],
    ids=["pin", "top", "recorded_against"],
)
def test_an_unknown_key_at_any_level_is_invalid(tmp_path: Path, text: str, where: str) -> None:
    result = invalid(tmp_path, text)
    assert result.reason_code is PinListDefect.UNKNOWN_KEY
    assert where in result.detail


@pytest.mark.parametrize("key", ["owner", "input", "target", "file", "line"])
def test_a_missing_pin_key_is_invalid(tmp_path: Path, key: str) -> None:
    lines = [line for line in PIN_B.splitlines(keepends=True) if not line.startswith(f"{key} =")]
    result = invalid(tmp_path, HEADER + "".join(lines))
    assert result.reason_code is PinListDefect.PIN_KEY_MISSING
    assert key in result.detail


@pytest.mark.parametrize(
    "old, new",
    [
        ('owner = "P::q::c"', "owner = 1"),
        ('input = "b"', "input = true"),
        ('target = "P::Sub::a"', "target = []"),
        ('file = "models/b.sysml"', "file = 3"),
        ("line = 12", 'line = "12"'),
        ("line = 12", "line = 12.0"),
        ("line = 12", "line = true"),
    ],
)
def test_a_pin_key_of_the_wrong_type_is_invalid(tmp_path: Path, old: str, new: str) -> None:
    text = HEADER + PIN_B.replace(old, new)
    assert invalid(tmp_path, text).reason_code is PinListDefect.WRONG_TYPE


def test_pin_as_a_plain_value_is_a_wrong_type(tmp_path: Path) -> None:
    text = HEADER.replace("[recorded_against]", "pin = 3\n[recorded_against]")
    assert invalid(tmp_path, text).reason_code is PinListDefect.WRONG_TYPE


@pytest.mark.parametrize("line", ["0", "-4"])
def test_a_non_positive_line_is_invalid(tmp_path: Path, line: str) -> None:
    text = HEADER + PIN_B.replace("line = 12", f"line = {line}")
    assert invalid(tmp_path, text).reason_code is PinListDefect.LINE_NOT_POSITIVE


@pytest.mark.parametrize("key", ["owner", "input", "target"])
def test_an_empty_identity_part_is_invalid(tmp_path: Path, key: str) -> None:
    lines = [
        f'{key} = ""\n' if line.startswith(f"{key} =") else line
        for line in PIN_B.splitlines(keepends=True)
    ]
    assert invalid(tmp_path, HEADER + "".join(lines)).reason_code is (
        PinListDefect.IDENTITY_PART_EMPTY
    )


def test_a_duplicate_identity_is_invalid_even_with_another_file_and_line(tmp_path: Path) -> None:
    again = PIN_B.replace("models/b.sysml", "models/c.sysml").replace("line = 12", "line = 3")
    result = invalid(tmp_path, HEADER + PIN_B + again)
    assert result.reason_code is PinListDefect.DUPLICATE_IDENTITY
    assert "pin[1]" in result.detail


def test_an_absolute_file_is_invalid(tmp_path: Path) -> None:
    text = HEADER + PIN_B.replace("models/b.sysml", "/models/b.sysml")
    assert invalid(tmp_path, text).reason_code is PinListDefect.FILE_ABSOLUTE


@pytest.mark.parametrize("file", ["../models/b.sysml", "models/../../b.sysml", "models/.."])
def test_a_parent_reference_in_file_is_invalid(tmp_path: Path, file: str) -> None:
    text = HEADER + PIN_B.replace("models/b.sysml", file)
    assert invalid(tmp_path, text).reason_code is PinListDefect.FILE_PARENT_REFERENCE


@pytest.mark.parametrize("file", ["", ".", "./"])
def test_a_file_naming_no_file_is_invalid(tmp_path: Path, file: str) -> None:
    text = HEADER + PIN_B.replace("models/b.sysml", file)
    assert invalid(tmp_path, text).reason_code is PinListDefect.FILE_EMPTY


def test_a_backslash_file_is_invalid(tmp_path: Path) -> None:
    """The file is a POSIX path relative to the pin root; a Windows spelling would never match."""
    text = HEADER + PIN_B.replace("models/b.sysml", "models\\\\b.sysml")
    assert invalid(tmp_path, text).reason_code is PinListDefect.FILE_NOT_POSIX


def test_every_defect_has_its_own_reason_code() -> None:
    values = [defect.value for defect in PinListDefect]
    assert len(values) == len(set(values))


def test_load_never_writes(tmp_path: Path) -> None:
    """Design I3: reading a pin list changes nothing on disk."""
    path = write(tmp_path, VALID)
    before = {p: p.stat().st_mtime_ns for p in tmp_path.rglob("*")}
    load(path, pin_root=tmp_path)
    load(tmp_path / "missing.toml", pin_root=tmp_path)
    discover(tmp_path)
    assert {p: p.stat().st_mtime_ns for p in tmp_path.rglob("*")} == before


# ---- the pin root ----------------------------------------------------------------------------


def test_the_pin_root_is_carried_as_given(tmp_path: Path) -> None:
    """D12: `file` is relative to the pin root, which the caller chooses."""
    (tmp_path / "pins").mkdir()
    (tmp_path / "tree").mkdir()
    path = write(tmp_path / "pins", VALID)
    by_default = load(path, pin_root=path.parent)
    explicit = load(path, pin_root=tmp_path / "tree")
    assert isinstance(by_default, PinList) and isinstance(explicit, PinList)
    assert by_default.pin_root == tmp_path / "pins"
    assert explicit.pin_root == tmp_path / "tree"
    assert explicit.pin_root / explicit.pins[0].file == tmp_path / "tree" / "models" / "a.sysml"


# ---- discovery --------------------------------------------------------------------------------


@pytest.mark.parametrize("marker", ["work/BACKLOG.md", ".agentic-mbse/install.json", ".claude/"])
def test_each_marker_makes_a_project_root_found_from_the_validated_path(
    tmp_path: Path, marker: str
) -> None:
    root = tmp_path / "project"
    target = root / marker
    if marker.endswith("/"):
        target.mkdir(parents=True)
    else:
        target.parent.mkdir(parents=True)
        target.write_text("")
    (root / "models" / "designs").mkdir(parents=True)
    pins = write(root, VALID)
    assert discover(root / "models" / "designs") == pins


def test_no_project_root_above_the_path_is_absent_with_nothing_looked_at(tmp_path: Path) -> None:
    (tmp_path / "models").mkdir()
    write(tmp_path, VALID)  # a pin file with no marker beside it is not a project root
    assert discover(tmp_path / "models") == PinListAbsent(project_root=None, looked_at=None)


def test_a_root_without_a_pin_file_is_absent_and_names_the_path_looked_at(tmp_path: Path) -> None:
    (tmp_path / ".claude").mkdir()
    (tmp_path / "models").mkdir()
    assert discover(tmp_path / "models") == PinListAbsent(
        project_root=tmp_path, looked_at=tmp_path / PIN_FILE_NAME
    )


def test_a_pin_file_in_a_parent_of_the_project_root_is_ignored(tmp_path: Path) -> None:
    write(tmp_path, VALID)
    project = tmp_path / "project"
    (project / ".claude").mkdir(parents=True)
    (project / "models").mkdir()
    assert discover(project / "models") == PinListAbsent(
        project_root=project, looked_at=project / PIN_FILE_NAME
    )


def test_a_relative_validated_path_is_walked_from_the_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "work").mkdir()
    (tmp_path / "work" / "BACKLOG.md").write_text("")
    (tmp_path / "models").mkdir()
    pins = write(tmp_path, VALID)
    monkeypatch.chdir(tmp_path / "models")
    assert discover(Path(".")) == pins


def test_find_project_root_without_a_start_still_walks_from_the_working_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / ".claude").mkdir()
    (tmp_path / "deep" / "er").mkdir(parents=True)
    monkeypatch.chdir(tmp_path / "deep" / "er")
    assert find_project_root() == tmp_path
    assert find_project_root(start=tmp_path / "deep") == tmp_path


def test_the_cli_name_is_the_shared_function() -> None:
    from agentic_mbse.cli import find_project_root as cli_find

    assert cli_find is find_project_root
