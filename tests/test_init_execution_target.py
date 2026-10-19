"""`init --execution-target`: the one write the toolkit makes to an owner's `pyproject.toml`.

Item 3 plan Phase 9; design D7, § `init` and its table, invariant I7. Each golden case is a
`before.toml` and the byte-exact `after.toml` that `init --execution-target=generated` must
produce from it, with and without `--force`.
"""

from __future__ import annotations

import builtins
import os
import shutil
from pathlib import Path

import pytest
import tomllib

from agentic_mbse import project_settings
from tests.helpers.l6_projects import make_project, run_cli

GOLDEN = Path(__file__).resolve().parent / "fixtures" / "l6" / "init_golden"
CASES = sorted(p.name for p in GOLDEN.iterdir())
GENERATED_LINE = 'execution-target = "generated"'


def _init(root: Path, *options: str) -> tuple[int, str]:
    return run_cli("init", "--assistant", "claude", *options, str(root))


def _project(tmp_path: Path, before: bytes | None) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    if before is not None:
        (root / "pyproject.toml").write_bytes(before)
    return root


def test_golden_cases_are_the_six_the_plan_names():
    assert CASES == sorted(
        [
            "comments_and_blank_lines",
            "existing_research_table",
            "table_present_no_key",
            "no_table",
            "crlf",
            "no_final_newline",
        ]
    )


@pytest.mark.parametrize("force", [False, True])
@pytest.mark.parametrize("case", CASES)
def test_golden_insert_is_byte_exact_and_parses(case, force, tmp_path):
    before = (GOLDEN / case / "before.toml").read_bytes()
    after = (GOLDEN / case / "after.toml").read_bytes()
    root = _project(tmp_path, before)
    code, out = _init(root, "--execution-target=generated", *(["--force"] if force else []))
    assert code == 0, out
    written = (root / "pyproject.toml").read_bytes()
    assert written == after
    expected = tomllib.loads(before.decode())
    expected.setdefault("tool", {}).setdefault("agentic-mbse", {})["execution-target"] = "generated"
    assert tomllib.loads(written.decode()) == expected
    assert f"Execution target: added {GENERATED_LINE} under [tool.agentic-mbse]" in out


def test_insert_keeps_the_file_mode(tmp_path):
    root = _project(tmp_path, (GOLDEN / "no_table" / "before.toml").read_bytes())
    (root / "pyproject.toml").chmod(0o640)
    assert _init(root, "--execution-target=native")[0] == 0
    assert (root / "pyproject.toml").stat().st_mode & 0o777 == 0o640
    assert [p.name for p in root.iterdir() if p.name.startswith(".pyproject")] == []


def test_no_file_creates_only_the_table(tmp_path):
    root = _project(tmp_path, None)
    code, out = _init(root, "--execution-target=native")
    assert code == 0, out
    assert (root / "pyproject.toml").read_bytes() == (
        b'[tool.agentic-mbse]\nexecution-target = "native"\n'
    )
    umask = os.umask(0)
    os.umask(umask)
    assert (root / "pyproject.toml").stat().st_mode & 0o777 == 0o666 & ~umask
    assert "Execution target: created with" in out


# ---- refusals --------------------------------------------------------------------------------

PLAIN = b'[project]\nname = "plant"\n'
LAYOUTS: dict[str, bytes] = {
    "bom": b"\xef\xbb\xbf" + PLAIN,
    "not_utf8": b'[project]\nname = "pl\xe4nt"\n',
    "inline_table": b'[tool]\nagentic-mbse = { research = { holdout-guard = "g.py" } }\n',
    "dotted_keys": b'[tool]\nagentic-mbse.research.holdout-guard = "g.py"\n',
    # Two header lines can only both parse when one is inside a string.
    "two_headers": b'[project]\ndescription = """\n[tool.agentic-mbse]\n"""\n\n[ tool.agentic-mbse ]\n',
    # The header line is inside a string, so the insert would change that string, not the table.
    "fails_verification": b'[project]\ndescription = """\n[tool.agentic-mbse]\n"""\n',
}
REASONS = {
    "symlink": "it is a symlink",
    "hardlink": "more than one hard link",
    "bom": "byte order mark",
    "not_utf8": "it is not UTF-8",
    "inline_table": "defined through an inline table",
    "dotted_keys": "defined through dotted keys",
    "two_headers": "2 lines match the [tool.agentic-mbse] header",
    "fails_verification": "does not parse to the original plus one key",
}


def _layout(tmp_path: Path, layout: str) -> Path:
    root = _project(tmp_path, LAYOUTS.get(layout))
    if layout == "symlink":
        (tmp_path / "real.toml").write_bytes(PLAIN)
        (root / "pyproject.toml").symlink_to(tmp_path / "real.toml")
    elif layout == "hardlink":
        (tmp_path / "real.toml").write_bytes(PLAIN)
        os.link(tmp_path / "real.toml", root / "pyproject.toml")
    return root


@pytest.mark.parametrize("force", [False, True])
@pytest.mark.parametrize("layout", sorted(REASONS))
def test_refused_layout_writes_nothing_prints_line_and_exits_1(layout, force, tmp_path):
    root = _layout(tmp_path, layout)
    before = (root / "pyproject.toml").read_bytes()
    code, out = _init(root, "--execution-target=generated", *(["--force"] if force else []))
    assert code == 1
    assert (root / "pyproject.toml").read_bytes() == before
    if layout in ("symlink", "hardlink"):
        assert (root / "pyproject.toml").is_symlink() == (layout == "symlink")
        assert (tmp_path / "real.toml").stat().st_nlink == (2 if layout == "hardlink" else 1)
    assert REASONS[layout] in out
    assert f"Add this line under [tool.agentic-mbse] by hand: {GENERATED_LINE}" in out


DEFECTS = {
    "unknown_key": b'[tool.agentic-mbse]\nexecution_target = "native"\n',
    "underscore_table": b'[tool.agentic_mbse]\nexecution-target = "native"\n',
    "not_a_table": b'[tool]\nagentic-mbse = "native"\n',
    "unparseable": b"[tool.agentic-mbse\n",
}


@pytest.mark.parametrize("defect", sorted(DEFECTS))
def test_existing_defect_writes_nothing_prints_it_and_exits_1(defect, tmp_path):
    root = _project(tmp_path, DEFECTS[defect])
    code, out = _init(root, "--execution-target=generated")
    assert code == 1
    assert (root / "pyproject.toml").read_bytes() == DEFECTS[defect]
    reader = project_settings.read_toolkit_table(root)
    assert isinstance(reader, project_settings.SettingsDefect)
    assert f"Execution target: {reader.detail}" in out


@pytest.mark.parametrize("defect", sorted(DEFECTS))
def test_existing_defect_without_option_is_printed_and_exits_0(defect, tmp_path):
    root = _project(tmp_path, DEFECTS[defect])
    code, out = _init(root)
    assert code == 0
    assert (root / "pyproject.toml").read_bytes() == DEFECTS[defect]
    assert "Execution target: " in out and str(root / "pyproject.toml") in out


def test_rest_of_install_completes_when_setting_step_refuses(tmp_path):
    root = _layout(tmp_path, "two_headers")
    code, _out = _init(root, "--execution-target=native")
    assert code == 1
    for installed in ("work/BACKLOG.md", "knowledge/SOURCE_INDEX.md", ".claude/settings.json"):
        assert (root / installed).exists(), installed


# ---- existing values -------------------------------------------------------------------------

SET_NATIVE = b'[tool.agentic-mbse]\nexecution-target = "native"\n'


@pytest.mark.parametrize("force", [False, True])
def test_existing_value_never_changed_by_reinit_force_or_disagreeing_option(force, tmp_path):
    root = _project(tmp_path, SET_NATIVE)
    extra = ["--force"] if force else []
    code, out = _init(root, "--execution-target=native", *extra)
    assert code == 0 and "Execution target: already set" in out
    code, out = _init(root, "--execution-target=generated", *extra)
    assert code == 1
    assert "--execution-target=generated not written" in out
    assert "execution-target = 'native'" in out and "allowed values are" in out
    code, out = _init(root, *extra)
    assert code == 0 and "already set" in out
    assert (root / "pyproject.toml").read_bytes() == SET_NATIVE


def test_invalid_existing_value_is_reported_never_changed(tmp_path):
    invalid = b'[tool.agentic-mbse]\nexecution-target = "python"\n'
    root = _project(tmp_path, invalid)
    code, out = _init(root, "--execution-target=native")
    assert code == 1
    assert "execution-target = 'python', which is not allowed" in out
    code, out = _init(root)
    assert code == 0 and "which is not allowed" in out
    assert (root / "pyproject.toml").read_bytes() == invalid


# ---- without the option ----------------------------------------------------------------------


def test_noninteractive_no_option_writes_nothing_and_prints_line_and_init_form(tmp_path):
    root = _project(tmp_path, PLAIN)
    code, out = _init(root)
    assert code == 0
    assert (root / "pyproject.toml").read_bytes() == PLAIN
    assert 'Add execution-target = "generated" or "native" under [tool.agentic-mbse]' in out
    assert "agentic-mbse init --execution-target=generated|native" in out


def test_noninteractive_no_option_no_file_creates_none(tmp_path):
    root = _project(tmp_path, None)
    assert _init(root)[0] == 0
    assert not (root / "pyproject.toml").exists()


def _answer(monkeypatch: pytest.MonkeyPatch, *answers: str) -> list[str]:
    asked: list[str] = []
    replies = iter(answers)

    def reply(prompt: str = "") -> str:
        asked.append(prompt)
        return next(replies)

    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr(builtins, "input", reply)
    return asked


def test_interactive_prompt_default_leaves_unset(monkeypatch, tmp_path):
    root = _project(tmp_path, PLAIN)
    asked = _answer(monkeypatch, "")
    code, out = _init(root)
    assert code == 0 and len(asked) == 1
    assert "(default: unset)" in asked[0]
    assert (root / "pyproject.toml").read_bytes() == PLAIN
    assert "Execution target: left unset" in out


def test_interactive_prompt_writes_the_choice_after_a_bad_answer(monkeypatch, tmp_path):
    root = _project(tmp_path, None)
    asked = _answer(monkeypatch, "python", "native")
    code, out = _init(root)
    assert code == 0 and len(asked) == 2
    assert "not 'python'" in out
    assert tomllib.loads((root / "pyproject.toml").read_text()) == {
        "tool": {"agentic-mbse": {"execution-target": "native"}}
    }


def test_interactive_reinit_with_value_set_does_not_prompt(monkeypatch, tmp_path):
    root = _project(tmp_path, SET_NATIVE)
    asked = _answer(monkeypatch)
    code, out = _init(root)
    assert code == 0 and asked == [] and "already set" in out


def test_install_commands_leaves_pyproject_untouched(tmp_path):
    root = _project(tmp_path, PLAIN)
    code, out = run_cli("install-commands", "--assistant", "claude", str(root))
    assert code == 0, out
    assert (root / "pyproject.toml").read_bytes() == PLAIN
    assert "Execution target" not in out


@pytest.mark.syside
def test_init_writes_the_file_l6_reads(tmp_path):
    models = make_project(tmp_path)
    root = models.parent
    shutil.rmtree(root / "work")  # init's own root marker must be what finds the file
    assert _init(root, "--execution-target=native")[0] == 0
    code, out = run_cli("validate", "--level=6", str(models))
    assert f"Execution target: native (from {root / 'pyproject.toml'})" in out, out
