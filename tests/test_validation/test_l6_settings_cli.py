"""L6 reads the execution target first; a broken setting fails L6 under every target (design D3).

Spec § Settings states bullets 4-7, § One key set bullet 3, § Where the setting is read from.
"""

import pytest

from tests.helpers.l6_projects import CLEAN_MODEL, make_project, run_cli, target_table

OVERRIDES = [None, "generated", "native"]


def _validate_l6(models, override=None, *extra):
    argv = ["validate", "--level=6", *extra, str(models)]
    if override is not None:
        argv.insert(2, f"--execution-target={override}")
    return run_cli(*argv)


@pytest.mark.parametrize("override", OVERRIDES)
def test_malformed_pyproject_exits_1_naming_file_and_parse_error(override, tmp_path):
    models = make_project(tmp_path, pyproject="[tool.agentic-mbse]\nexecution-target = \n")
    code, out = _validate_l6(models, override)
    pyproject = models.parent / "pyproject.toml"
    assert code == 1
    assert "L6 ran no checks" in out
    assert f"cannot read {pyproject}: " in out
    assert "(at line 2" in out
    assert f"Execution target: invalid ({pyproject}; see L6_SETTING_INVALID)" in out


@pytest.mark.parametrize("override", OVERRIDES)
@pytest.mark.parametrize(
    ("value", "shown"), [('"generate"', "'generate'"), ("1", "1"), ('""', "''")]
)
def test_unknown_value_exits_1_naming_value_and_allowed(override, value, shown, tmp_path):
    code, out = _validate_l6(make_project(tmp_path, pyproject=target_table(value)), override)
    assert code == 1
    assert f"execution-target = {shown} is not allowed" in out
    assert "allowed values are 'generated' and 'native'" in out


@pytest.mark.parametrize("override", OVERRIDES)
@pytest.mark.parametrize(
    ("pyproject", "named"),
    [
        ('[tool.agentic-mbse]\nexecution_target = "native"\n', "unknown key 'execution_target'"),
        ('[tool.agentic-mbse]\nexecutiontarget = "native"\n', "unknown key 'executiontarget'"),
        ('[tool.agentic-mbse.reseach]\nholdout-guard = "g.py"\n', "unknown key 'reseach'"),
        ('[tool.agentic_mbse]\nexecution-target = "native"\n', "[tool.agentic_mbse] is not read"),
    ],
)
def test_unknown_key_or_underscore_table_exits_1_naming_key(override, pyproject, named, tmp_path):
    code, out = _validate_l6(make_project(tmp_path, pyproject=pyproject), override)
    assert code == 1
    assert named in out
    assert "'execution-target'" in out and "'research'" in out


@pytest.mark.syside
@pytest.mark.parametrize(
    ("file_value", "override"), [("generated", "native"), ("native", "generated")]
)
def test_override_wins_and_output_says_so(file_value, override, tmp_path):
    models = make_project(tmp_path, pyproject=target_table(f'"{file_value}"'))
    code, out = _validate_l6(models, override)
    assert code == 0
    assert (
        f"Execution target: {override} (override --execution-target; file says {file_value})" in out
    )


@pytest.mark.syside
def test_no_root_metric_names_execution_target_option(tmp_path):
    models = tmp_path / "loose" / "models"
    models.mkdir(parents=True)
    (models / "calc.sysml").write_text(CLEAN_MODEL)
    code, out = _validate_l6(models)
    assert code == 0
    assert "Execution target: unset (no project root above models; pass --execution-target)" in out


@pytest.mark.syside
@pytest.mark.parametrize(
    ("pyproject", "metric"),
    [
        (None, "unset (no execution-target in {path})"),
        ('[project]\nname = "x"\n', "unset (no execution-target in {path})"),
        (target_table('"generated"'), "generated (from {path})"),
        (target_table('"native"'), "native (from {path})"),
    ],
)
def test_target_metric_names_source_every_run(pyproject, metric, tmp_path):
    models = make_project(tmp_path, pyproject=pyproject)
    code, out = _validate_l6(models)
    assert code == 0
    assert f"Execution target: {metric.format(path=models.parent / 'pyproject.toml')}" in out


@pytest.mark.syside
def test_subdirectory_run_reads_the_root_file(tmp_path):
    models = make_project(
        tmp_path,
        pyproject=target_table('"generated"'),
        models={"library/pump/calc.sysml": CLEAN_MODEL},
    )
    (models / "library" / "pyproject.toml").write_text(target_table('"native"'))
    code, out = _validate_l6(models / "library" / "pump")
    assert code == 0
    assert f"Execution target: generated (from {models.parent / 'pyproject.toml'})" in out


@pytest.mark.syside
def test_bad_holdout_guard_does_not_fail_validate(tmp_path):
    models = make_project(
        tmp_path, pyproject='[tool.agentic-mbse.research]\nholdout-guard = "missing.py"\n'
    )
    code, out = _validate_l6(models)
    assert code == 0
    assert "L6_SETTING_INVALID" not in out


@pytest.mark.syside
@pytest.mark.parametrize("level", [1, 2, 3, 4, 5])
def test_execution_target_with_level_1_to_5_is_accepted_and_unused(level, tmp_path):
    models = make_project(tmp_path, pyproject=target_table('"bogus"'))
    code, out = run_cli("validate", f"--level={level}", "--execution-target=native", str(models))
    assert code == 0
    assert "Execution target" not in out


def test_invalid_option_value_is_a_usage_error(tmp_path):
    with pytest.raises(SystemExit) as raised:
        run_cli("validate", "--execution-target=generate", str(make_project(tmp_path)))
    assert raised.value.code == 2
