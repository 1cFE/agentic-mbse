"""Tests for shared SysML qualified-name utilities."""

from __future__ import annotations

import keyword
from dataclasses import dataclass

import pytest

import agentic_mbse.sysml as sysml
from agentic_mbse.sysml import qualified_names as qn
from agentic_mbse.sysml.qualified_names import (
    build_element_qualified_name,
    extract_simple_name,
    python_to_sysml_qualified_name,
    sanitize_name,
    sanitize_qualified_name,
    sysml_to_python_qualified_name,
)


@dataclass
class FakeElement:
    name: str | None
    owner: FakeElement | FakeOwnership | None = None


@dataclass
class FakeOwnership:
    owning_related_element: FakeElement | None
    owner: FakeElement | FakeOwnership | None = None
    name: str | None = None


def _build_chain(names: list[str]) -> FakeElement:
    assert names
    if len(names) == 1:
        return FakeElement(name=names[0])

    elem = FakeElement(name=names[-1])
    current_owner = None
    for name in names[:-1]:
        current_owner = FakeOwnership(
            owning_related_element=FakeElement(name=name),
            owner=current_owner,
        )
    elem.owner = current_owner
    return elem


def test_package_root_exports_qualified_name_helpers() -> None:
    assert sysml.sanitize_name is qn.sanitize_name
    assert sysml.build_element_qualified_name is qn.build_element_qualified_name
    assert sysml.sysml_to_python_qualified_name is qn.sysml_to_python_qualified_name
    assert sysml.sanitize_qualified_name is qn.sanitize_qualified_name
    assert sysml.python_to_sysml_qualified_name is qn.python_to_sysml_qualified_name
    assert sysml.extract_simple_name is qn.extract_simple_name


def test_qualified_names_all_is_exact_shared_surface() -> None:
    assert qn.__all__ == [
        "sanitize_name",
        "build_element_qualified_name",
        "sysml_to_python_qualified_name",
        "sanitize_qualified_name",
        "python_to_sysml_qualified_name",
        "extract_simple_name",
    ]


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("'Quoted Name'", "Quoted_Name"),
        ('"Double Quoted"', "Double_Quoted"),
        ("hello world", "hello_world"),
        ("Racking_&_Mounting", "Racking_Mounting"),
        ("foo$bar", "foo_bar"),
        ("a___b", "a_b"),
        ("___leading___", "leading"),
        ("'class & def'", "class_def"),
        ("", "unnamed"),
        (None, "unnamed"),
        ("$$$", "unnamed"),
        ("2nd stage", "n_2nd_stage"),
        ("class", "class_"),
    ],
)
def test_sanitize_name_inv5_outputs(raw: str | None, expected: str) -> None:
    result = sanitize_name(raw)
    assert result == expected
    assert result
    assert result.isidentifier()
    assert not keyword.iskeyword(result)


def test_build_element_qualified_name_from_owner_chain() -> None:
    elem = _build_chain(["Solar Battery", "battery_system", "cost_model"])

    assert build_element_qualified_name(elem) == "Solar_Battery__battery_system__cost_model"
    assert build_element_qualified_name(elem, use_double_underscore=False) == (
        "Solar_Battery::battery_system::cost_model"
    )


def test_build_element_qualified_name_empty_for_anonymous_element() -> None:
    assert build_element_qualified_name(FakeElement(name=None)) == ""


def test_qualified_name_separator_helpers_round_trip() -> None:
    original = "A::B::C"
    python_qn = sysml_to_python_qualified_name(original)

    assert python_qn == "A__B__C"
    assert python_to_sysml_qualified_name(python_qn) == original


def test_sanitize_qualified_name_is_apply_once_boundary() -> None:
    assert sanitize_qualified_name("Lib::'Margin Part'") == "Lib__Margin_Part"
    assert sanitize_qualified_name("Lib__Margin_Part") == "Lib_Margin_Part"


def test_extract_simple_name_for_supported_separator_forms() -> None:
    assert extract_simple_name("A::B::C") == "C"
    assert extract_simple_name("A__B__C") == "C"
    assert extract_simple_name("A.B.C") == "C"
    assert extract_simple_name("standalone") == "standalone"


def test_identifier_safe_segments_are_byte_identity() -> None:
    safe_segments = [
        "SolarBatteryDesign",
        "solar_battery_plant",
        "battery_system",
        "battery_pack",
        "cost_model",
        "CATFMFEPhysics",
        "catf_physics",
        "net_electric",
    ]
    for segment in safe_segments:
        assert sanitize_name(segment) == segment
