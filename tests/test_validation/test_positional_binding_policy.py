"""The positional-binding check through L2 and the CLI: policy, scope, failures, metrics.

Each test builds a small project in a temporary directory (a project-root marker, `models/`,
and a pin list when the test needs one) and runs `validate_structure` on it, so the pin list
is found the way `validate` finds it (design D11). Inputs bind valued attributes, not literals,
so L2's literal-binding warnings do not mix into the result.
"""

from __future__ import annotations

import shutil
from collections.abc import Callable, Iterable
from functools import partial
from pathlib import Path
from typing import Any

import pytest

from agentic_mbse.cli import main as cli_main
from agentic_mbse.sysml import parameter_redefinition_extraction as extraction
from agentic_mbse.sysml.types import Severity, ValidationCode, ValidationIssue
from agentic_mbse.validation import positional_check
from agentic_mbse.validation.common import QualityCheckResult, print_result
from agentic_mbse.validation.level2_structure import validate_structure

POSITIONAL = ValidationCode.L2_POSITIONAL_BINDING
STALE = ValidationCode.L2_POSITIONAL_PIN_STALE
INVALID = ValidationCode.L2_POSITIONAL_PIN_LIST_INVALID
UNVERIFIABLE = ValidationCode.L2_CHECK_UNVERIFIABLE
ERROR = Severity.ERROR
WARNING = Severity.WARNING

FIX = Path(__file__).parent.parent / "fixtures" / "positional_binding"

PLANT = """\
package P {
    private import ScalarValues::*;
    calc def Sub { in a : Real; in b : Real; return r : Real = a - b; }
    part q {
        attribute big : Real = 10.0;
        attribute small : Real = 3.0;
        calc c : Sub {
            in b = small;
            in a = big;
        }
        attribute result : Real = c.r;
    }
}
"""
B_ON_A = ("P::q::c", "b", "P::Sub::a")
A_ON_B = ("P::q::c", "a", "P::Sub::b")
LINES = {"b": 8, "a": 9}

HEADER = """\
schema = "positional-pins/v1"
[recorded_against]
revision = "0123abc"
date = 2026-10-15
"""


def pin_text(owner: str, input_: str, target: str, file: str, line: int) -> str:
    return (
        f'[[pin]]\nowner = "{owner}"\ninput = "{input_}"\ntarget = "{target}"\n'
        f'file = "{file}"\nline = {line}\n'
    )


def pins_for(*identities: tuple[str, str, str], file: str = "models/plant.sysml") -> str:
    return HEADER + "".join(pin_text(*i, file, LINES[i[1]]) for i in identities)


def make_project(root: Path, model: str = PLANT, pins: str | None = None) -> Path:
    (root / "work").mkdir(parents=True)
    (root / "work" / "BACKLOG.md").write_text("")
    (root / "models").mkdir()
    (root / "models" / "plant.sysml").write_text(model)
    if pins is not None:
        (root / "positional-pins.toml").write_text(pins)
    return root


def l2(path: Path, **options: Any) -> QualityCheckResult:
    return validate_structure(str(path), **options)


def codes(result: QualityCheckResult) -> list[tuple[ValidationCode, Severity]]:
    return [(i.code, i.severity) for i in result.structured_issues]


def positional(result: QualityCheckResult) -> list[ValidationIssue]:
    return [i for i in result.structured_issues if i.code is POSITIONAL]


def with_code(result: QualityCheckResult, code: ValidationCode) -> list[ValidationIssue]:
    return [i for i in result.structured_issues if i.code is code]


# ---- Pol-1, Pol-2, Pol-4: the policy ----------------------------------------------------------


def test_pinned_mismatch_is_a_warning_and_l2_passes(tmp_path: Path) -> None:
    project = make_project(tmp_path, pins=pins_for(B_ON_A, A_ON_B))
    result = l2(project / "models")
    assert codes(result) == [(POSITIONAL, WARNING), (POSITIONAL, WARNING)]
    assert result.success
    for issue in result.structured_issues:
        assert "does not show that native values are correct" in issue.message
        assert "native and generated routes agree" in issue.message
    assert result.metrics["Positional bindings pinned (legacy warning)"] == 2
    assert result.metrics["Positional bindings (blocking)"] == 0


def test_unpinned_mismatch_fails_l2_beside_a_pinned_one(tmp_path: Path) -> None:
    project = make_project(tmp_path, pins=pins_for(B_ON_A))
    result = l2(project / "models")
    assert not result.success
    assert {(i.message.split("'")[1], i.severity) for i in positional(result)} == {  # input name
        ("b", WARNING),
        ("a", ERROR),
    }


def test_no_pin_list_makes_every_mismatch_an_error(tmp_path: Path) -> None:
    project = make_project(tmp_path)
    result = l2(project / "models")
    assert not result.success
    assert codes(result) == [(POSITIONAL, ERROR), (POSITIONAL, ERROR)]
    assert result.metrics["Positional pin list"] == (
        f"none (looked at {project / 'positional-pins.toml'})"
    )


def test_no_project_root_is_named_in_the_metric(tmp_path: Path) -> None:
    (tmp_path / "models").mkdir()
    (tmp_path / "models" / "plant.sysml").write_text(PLANT)
    result = l2(tmp_path / "models")
    assert not result.success
    assert result.metrics["Positional pin list"] == (
        f"none (no project root above {tmp_path / 'models'}; pass --positional-pins)"
    )


def test_the_error_message_prints_five_copyable_fields_and_both_repairs(tmp_path: Path) -> None:
    project = make_project(tmp_path)
    (b_issue,) = [i for i in positional(l2(project / "models")) if 'input = "b"' in i.message]
    assert b_issue.reason_code == "POSITIONAL_SWAP"
    assert "a likely authoring hazard in valid SysML" in b_issue.message
    assert "in :>> <formal> = ..." in b_issue.message
    assert "in b redefines <formal> = ..." in b_issue.message
    assert (
        '[owner = "P::q::c", input = "b", target = "P::Sub::a", '
        'file = "models/plant.sysml", line = 8]'
    ) in b_issue.message
    assert "invalid" not in b_issue.message.lower()
    assert b_issue.location == "models/plant.sysml:8"


def test_a_changed_target_is_a_new_error_and_a_stale_pin(tmp_path: Path) -> None:
    pins = (
        HEADER
        + pin_text("P::q::c", "b", "P::Sub::old", "models/plant.sysml", 8)
        + pin_text(*A_ON_B, "models/plant.sysml", 9)
    )
    project = make_project(tmp_path, pins=pins)
    result = l2(project / "models")
    assert not result.success
    assert sorted(codes(result), key=str) == sorted(
        [(POSITIONAL, ERROR), (POSITIONAL, WARNING), (STALE, ERROR)], key=str
    )
    (stale,) = with_code(result, STALE)
    assert stale.reason_code == "not_found_in_validated_file"
    assert "P::Sub::old" in stale.message


def test_an_unmatched_pin_fails_l2(tmp_path: Path) -> None:
    pins = pins_for(B_ON_A, A_ON_B) + pin_text(
        "P::q::gone", "x", "P::Sub::a", "models/plant.sysml", 3
    )
    result = l2(make_project(tmp_path, pins=pins) / "models")
    assert not result.success
    assert [(i.code, i.reason_code) for i in with_code(result, STALE)] == [
        (STALE, "not_found_in_validated_file")
    ]
    assert result.metrics["Positional pins stale"] == 1


def test_a_pin_in_a_missing_file_is_stale(tmp_path: Path) -> None:
    pins = pins_for(B_ON_A, A_ON_B) + pin_text("P::q::d", "x", "P::Sub::a", "models/gone.sysml", 3)
    result = l2(make_project(tmp_path, pins=pins) / "models")
    assert [i.reason_code for i in with_code(result, STALE)] == ["pinned_file_missing"]
    assert not result.success


@pytest.mark.parametrize(
    "write, reason",
    [
        (lambda p: p.write_text(HEADER + "[[pin]\n"), "toml_syntax"),
        (lambda p: p.write_bytes(b'schema = "\xff"\n'), "unreadable"),
        (lambda p: p.mkdir(), "unreadable"),
        (lambda p: p.write_text(pins_for(B_ON_A).replace(HEADER, "")), "schema_missing"),
    ],
    ids=["malformed", "undecodable", "directory", "headerless"],
)
def test_an_invalid_pin_list_is_reported_and_the_check_runs_as_if_absent(
    tmp_path: Path, write: Callable[[Path], object], reason: str
) -> None:
    project = make_project(tmp_path)
    write(project / "positional-pins.toml")
    result = l2(project / "models")
    assert not result.success
    assert codes(result) == [(INVALID, ERROR), (POSITIONAL, ERROR), (POSITIONAL, ERROR)]
    assert result.structured_issues[0].reason_code == reason
    assert result.metrics["Positional pin list"].startswith("invalid: ")


def test_the_options_override_discovery_and_resolve_against_the_pin_root(tmp_path: Path) -> None:
    """D12: a pin file anywhere, its paths relative to the named root."""
    tree = tmp_path / "tree"
    (tree / "models").mkdir(parents=True)
    (tree / "models" / "plant.sysml").write_text(PLANT)
    elsewhere = tmp_path / "pins.toml"
    elsewhere.write_text(pins_for(B_ON_A, A_ON_B))
    result = l2(tree / "models", positional_pins=elsewhere, pin_root=tree)
    assert result.success
    assert codes(result) == [(POSITIONAL, WARNING), (POSITIONAL, WARNING)]
    assert result.metrics["Positional pin list"] == (
        f"{elsewhere} (pin root {tree}; recorded against 0123abc on 2026-10-15; 2 pins)"
    )
    # Without the root the paths resolve against the pin file's directory, where
    # models/plant.sysml does not exist: the pins still match (matching ignores the file).
    without_root = l2(tree / "models", positional_pins=elsewhere)
    assert without_root.success


# ---- Pol-3: partial scope ----------------------------------------------------------------------


def scope_project(root: Path, extra: str = "") -> Path:
    shutil.copytree(FIX / "partial_scope" / "models", root / "models")
    (root / ".claude").mkdir()
    pins = HEADER + "".join(
        pin_text(
            f"Scope{s}::q::c", i, f"Scope{s}::Sub::{t}", f"models/{s.lower()}/{s.lower()}.sysml", n
        )
        for s in ("A", "B")
        for i, t, n in (("b", "a", 10), ("a", "b", 10))
    )
    (root / "positional-pins.toml").write_text(pins + extra)
    return root


def test_pins_outside_the_validated_subfolder_are_out_of_scope(tmp_path: Path) -> None:
    project = scope_project(tmp_path)
    result = l2(project / "models" / "a")
    assert result.success
    assert codes(result) == [(POSITIONAL, WARNING), (POSITIONAL, WARNING)]
    assert result.metrics["Positional pins out of scope"] == 2
    assert result.metrics["Positional pins stale"] == 0


def test_an_in_scope_unmatched_pin_is_still_stale(tmp_path: Path) -> None:
    project = scope_project(
        tmp_path, pin_text("ScopeA::q::gone", "x", "ScopeA::Sub::a", "models/a/a.sysml", 2)
    )
    result = l2(project / "models" / "a")
    assert not result.success
    assert [i.element_name for i in with_code(result, STALE)] == ["ScopeA::q::gone"]
    assert result.metrics["Positional pins out of scope"] == 2


def test_a_non_self_contained_subfolder_gives_unverifiable_owners(tmp_path: Path) -> None:
    shutil.copytree(FIX / "partial_run", tmp_path / "partial_run")
    (tmp_path / ".claude").mkdir()
    (tmp_path / "positional-pins.toml").write_text(
        HEADER + pin_text("Use::q::c", "b", "Defs::Sub::a", "partial_run/designs/use.sysml", 5)
    )
    result = l2(tmp_path / "partial_run" / "designs")
    assert not result.success
    assert {(i.code, i.reason_code) for i in result.structured_issues} == {
        (UNVERIFIABLE, "POSITIONAL_UNRESOLVED_OWNER_TYPE")
    }
    assert result.metrics["Positional pins not judged (inspection failed)"] == 1
    assert result.metrics["Positional pins stale"] == 0


# ---- Insp-1: inspection failures through L2 ---------------------------------------------------

TWO_OWNERS = PLANT.replace(
    "        attribute result : Real = c.r;\n",
    "        attribute result : Real = c.r;\n"
    "        calc d : Sub {\n            in b = small;\n            in a = big;\n        }\n"
    "        attribute other : Real = d.r;\n",
)


def inject(monkeypatch: pytest.MonkeyPatch, **seams: Callable[[Any], Iterable[Any]]) -> None:
    monkeypatch.setattr(
        positional_check,
        "extract_parameter_redefinitions",
        partial(extraction.extract_parameter_redefinitions, **seams),
    )


def raising_owned_features(owner_name: str) -> Callable[[Any], Iterable[Any]]:
    def read(owner: Any) -> Iterable[Any]:
        if owner.declared_name == owner_name:
            raise RuntimeError(f"simulated owned_features failure on {owner_name}")
        return extraction.owned_features(owner)

    return read


def raising_heritage(owner_name: str, input_name: str) -> Callable[[Any], Iterable[Any]]:
    def read(element: Any) -> Iterable[Any]:
        owner = getattr(element, "owner", None)
        if (
            element.declared_name == input_name
            and owner is not None
            and owner.declared_name == owner_name
        ):
            raise RuntimeError(f"simulated heritage failure on {owner_name}::{input_name}")
        return extraction.heritage_relationships(element)

    return read


def test_a_raising_owner_sweep_is_unverifiable_and_fails_l2(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def no_owners(model: Any) -> Iterable[Any]:
        raise RuntimeError("simulated owner sweep failure")

    inject(monkeypatch, list_owners=no_owners)
    result = l2(make_project(tmp_path, pins=pins_for(B_ON_A, A_ON_B)) / "models")
    assert not result.success
    assert [(i.code, i.reason_code) for i in result.structured_issues] == [
        (UNVERIFIABLE, "POSITIONAL_OWNERS_UNLISTED")
    ]
    assert result.metrics["Positional pins not judged (inspection failed)"] == 2


def test_a_raising_owned_features_read_fails_one_owner_and_keeps_the_other(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inject(monkeypatch, read_owned_features=raising_owned_features("d"))
    result = l2(make_project(tmp_path, TWO_OWNERS) / "models")
    assert not result.success
    (failure,) = with_code(result, UNVERIFIABLE)
    assert failure.reason_code == "POSITIONAL_INPUTS_UNLISTED"
    assert failure.element_name == "P::q::d"
    assert {i.element_name for i in positional(result)} == {"P::q::c"}


def test_a_raising_heritage_read_fails_one_input_and_a_pin_on_it_changes_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inject(monkeypatch, read_heritage=raising_heritage("c", "b"))
    without_pin = l2(make_project(tmp_path / "no_pin", pins=pins_for(A_ON_B)) / "models")
    with_pin = l2(make_project(tmp_path / "pin", pins=pins_for(A_ON_B, B_ON_A)) / "models")
    for result in (without_pin, with_pin):
        assert not result.success
        (failure,) = with_code(result, UNVERIFIABLE)
        assert failure.reason_code == "POSITIONAL_REDEFINITIONS_UNREADABLE"
        assert failure.element_name == "P::q::c::b"
        assert [(i.severity, i.element_name) for i in positional(result)] == [(WARNING, "P::q::c")]
    assert codes(with_pin) == codes(without_pin)
    assert [i.message for i in with_pin.structured_issues] == [
        i.message for i in without_pin.structured_issues
    ]
    assert with_pin.metrics["Positional pins not judged (inspection failed)"] == 1


@pytest.mark.parametrize(
    "fixture, reason",
    [
        ("unresolved_type.sysml", "POSITIONAL_UNRESOLVED_OWNER_TYPE"),
        ("unresolved_supertype.sysml", "POSITIONAL_UNRESOLVED_OWNER_TYPE"),
        ("unresolved_input_redefinition.sysml", "POSITIONAL_UNRESOLVED_INPUT_REDEFINITION"),
    ],
)
def test_the_m1_fixtures_are_unverifiable_through_l2(
    tmp_path: Path, fixture: str, reason: str
) -> None:
    (tmp_path / "models").mkdir()
    shutil.copy(FIX / "unresolved" / fixture, tmp_path / "models" / fixture)
    result = l2(tmp_path / "models")
    assert not result.success
    assert {i.reason_code for i in with_code(result, UNVERIFIABLE)} == {reason}


# ---- Insp-3: metrics and the summary line -----------------------------------------------------


def test_every_positional_metric_is_present(tmp_path: Path) -> None:
    result = l2(make_project(tmp_path, pins=pins_for(B_ON_A, A_ON_B)) / "models")
    assert {k: v for k, v in result.metrics.items() if k.startswith("Positional")} == {
        # The definition's own `a` and `b` are inspected too, as new parameters.
        "Positional inputs inspected": 4,
        "Positional input outcomes": (
            "explicit 0, anonymous 0, implicit_matching 0, implicit_mismatch 2, "
            "new_parameter 2, special_parameter 0, anonymous_target 0"
        ),
        "Positional bindings (blocking)": 0,
        "Positional bindings pinned (legacy warning)": 2,
        "Positional pins stale": 0,
        "Positional pins out of scope": 0,
        "Positional pins not judged (inspection failed)": 0,
        "Positional unverifiable": 0,
        "Positional pin list": (
            f"{tmp_path / 'positional-pins.toml'} (pin root {tmp_path}; recorded against "
            "0123abc on 2026-10-15; 2 pins)"
        ),
    }


def test_the_summary_line_says_pins_are_not_a_value_check(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    result = l2(make_project(tmp_path, pins=pins_for(B_ON_A, A_ON_B)) / "models")
    capsys.readouterr()
    print_result(result)
    header = capsys.readouterr().out.strip().splitlines()[0]
    assert header == (
        "✅ Level 2: Structural Completeness "
        "(2 pinned positional warnings; not a value or route-parity check)"
    )


def test_the_summary_line_has_no_note_when_l2_fails(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    result = l2(make_project(tmp_path, pins=pins_for(B_ON_A)) / "models")
    capsys.readouterr()
    print_result(result)
    assert capsys.readouterr().out.strip().splitlines()[0] == "❌ Level 2: Structural Completeness"


# ---- Pol-5: the pass rule ---------------------------------------------------------------------


def test_a_pinned_warning_beside_another_l2_warning_still_fails(tmp_path: Path) -> None:
    model = PLANT.replace(
        "        attribute result : Real = c.r;\n",
        (
            "        attribute result : Real = c.r;\n"
            "        calc lit : Sub { in a = 1.0; in b = 2.0; }\n"
        ),
    )
    result = l2(make_project(tmp_path, model, pins=pins_for(B_ON_A, A_ON_B)) / "models")
    assert not result.success
    assert (ValidationCode.LITERAL_BINDING, WARNING) in codes(result)
    assert [i.severity for i in positional(result)] == [WARNING, WARNING]


def test_a_model_without_positional_findings_passes_as_before(tmp_path: Path) -> None:
    clean = PLANT.replace(
        "in b = small;\n            in a = big;", "in a = big;\n            in b = small;"
    )
    result = l2(make_project(tmp_path, clean) / "models")
    assert result.success and codes(result) == []


# ---- I5: determinism --------------------------------------------------------------------------


def test_two_runs_give_identical_issue_lists(tmp_path: Path) -> None:
    pins = pins_for(B_ON_A) + pin_text("P::q::gone", "x", "P::Sub::a", "models/plant.sysml", 3)
    project = make_project(tmp_path, TWO_OWNERS, pins=pins)
    first, second = l2(project / "models"), l2(project / "models")
    assert [i.model_dump() for i in first.structured_issues] == [
        i.model_dump() for i in second.structured_issues
    ]
    assert first.metrics == second.metrics


# ---- the CLI ------------------------------------------------------------------------------------


def test_both_options_reach_l2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    tree = tmp_path / "tree"
    (tree / "models").mkdir(parents=True)
    (tree / "models" / "plant.sysml").write_text(PLANT)
    pins = tmp_path / "pins.toml"
    pins.write_text(pins_for(B_ON_A, A_ON_B))
    argv = ["validate", "--level=2", "--positional-pins", str(pins)]
    argv += ["--positional-pins-root", str(tree), str(tree / "models")]
    assert cli_main(argv) == 0
    out = capsys.readouterr().out
    assert f"Positional pin list: {pins} (pin root {tree};" in out
    assert "(2 pinned positional warnings; not a value or route-parity check)" in out


def test_pins_root_without_pins_is_a_usage_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "models").mkdir()
    argv = ["validate", "--positional-pins-root", str(tmp_path), str(tmp_path / "models")]
    assert cli_main(argv) == 2
    assert "--positional-pins-root needs --positional-pins" in capsys.readouterr().err


def test_a_pins_root_that_is_not_a_directory_is_a_usage_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "models").mkdir()
    pins = tmp_path / "pins.toml"
    pins.write_text(HEADER)
    argv = ["validate", "--positional-pins", str(pins), "--positional-pins-root", str(pins)]
    assert cli_main([*argv, str(tmp_path / "models")]) == 2
    assert "is not a directory" in capsys.readouterr().err
