"""The probe judge (design invariant 2) on synthetic observations. Pure: no SysIDE, no codegen."""

import dataclasses
import hashlib
import json
from pathlib import Path

import pytest

from tests.helpers.subset_probe_judge import (
    PINNED_CODEGEN_REV,
    PINNED_SYSIDE_VERSION,
    PINNED_UV_LOCK_SHA256,
    FailedCheck,
    Identity,
    Observation,
    ObservationFormatError,
    ProbeDefinitionError,
    ReportedError,
    judge,
    load_observation,
    load_probe,
    observation_to_json,
    parse_error_lines,
)

FIXTURES = Path(__file__).parent / "fixtures" / "subset_profile" / "probes"
REFUSED = FIXTURES / "binding-source__expression_source__owner_instantiated"  # construct line 7
CONDITIONAL = (
    FIXTURES
    / "conditional-expression__conditional_unresolved_branch__calc_definition_feature_value"
)
ADMITTED = FIXTURES / "invocation-callable__explicit_operator__attribute_value"
OMITTED = FIXTURES / "string-value-omission__string_value__attribute_value__redefinition_shorthand"

TREE = "/tmp/subset-profile/run-abc"
GOOD_IDENTITY = Identity(
    codegen_rev=PINNED_CODEGEN_REV,
    agentic_rev="1002997d" + "0" * 32,
    sysml_codegen_version="0.1.0",
    agentic_mbse_version="0.1.3",
    syside_version=PINNED_SYSIDE_VERSION,
    python_version="3.12.3",
    uv_lock_sha256=PINNED_UV_LOCK_SHA256,
    tree_root=TREE,
    sysml_codegen_file=f"{TREE}/sysml-codegen/src/sysml_codegen/__init__.py",
    agentic_mbse_file=f"{TREE}/agentic-mbse/src/agentic_mbse/__init__.py",
    syside_file=f"{TREE}/sysml-codegen/.venv/lib/python3.12/site-packages/syside/__init__.py",
    license_key_present=True,
)


def error_line(code: str, file: str | None, line: int | None) -> str:
    """One refusal in codegen's rendered form (`elaborate.py:134-144`)."""
    location = f" [root-0/{file}:{line}]" if file is not None else ""
    return f"ERROR: Model is not ready for the exact route: {code}: fx__Site__t.xs: reference='a, b': detail{location}"


def observation(
    *,
    probe: Path = REFUSED,
    exit: int,
    errors: list[tuple[str, str | None, int | None]] = (),  # type: ignore[assignment]
    generated: list[str] = (),  # type: ignore[assignment]
    symbols: list[str] | None = None,
    mentions: dict[str, list[str]] | None = None,
    identity: Identity = GOOD_IDENTITY,
    timed_out: bool = False,
) -> Observation:
    return Observation(
        probe_id=probe.name,
        model_sha256=hashlib.sha256((probe / "model.sysml").read_bytes()).hexdigest(),
        identity=identity,
        argv=("python", "-I", "-m", "sysml_codegen", "generate"),
        exit_code=exit,
        timed_out=timed_out,
        error_lines=tuple(error_line(*e) for e in errors),
        generated_files={path: "0" * 64 for path in generated},
        catalog_names=None if symbols is None else tuple(symbols),
        mentions={name: tuple(files) for name, files in (mentions or {}).items()},
    )


# --- refused -------------------------------------------------------------------------------


def test_refused_needs_matching_code_and_location():
    probe = load_probe(REFUSED)
    obs = observation(exit=1, errors=[("SI_SELF_BINDING", "model.sysml", 12)])
    assert judge(probe, obs).failed_check == "code_mismatch"
    obs = observation(exit=1, errors=[("SI_EXPRESSION_SOURCE_UNSUPPORTED", "model.sysml", 3)])
    assert judge(probe, obs).failed_check == "location_outside_construct"


def test_refused_certifies_on_expected_code_inside_construct():
    obs = observation(exit=1, errors=[("SI_EXPRESSION_SOURCE_UNSUPPORTED", "model.sysml", 7)])
    certification = judge(load_probe(REFUSED), obs)
    assert certification.certifies and certification.failed_check is None


def test_refused_probe_that_exits_zero_is_the_r2_signal():
    obs = observation(exit=0, generated=["contracts/model_contract.json"], symbols=[])
    assert judge(load_probe(REFUSED), obs).failed_check == FailedCheck.REFUSED_PROBE_ADMITTED


def test_refused_rejects_a_generic_code_without_a_location():
    """ES-006's generic SI_EVIDENCE_INCOMPLETE is only evidence when it points into the construct."""
    probe = load_probe(CONDITIONAL)
    obs = observation(probe=CONDITIONAL, exit=1, errors=[("SI_EVIDENCE_INCOMPLETE", None, None)])
    assert judge(probe, obs).failed_check == FailedCheck.LOCATION_MISSING
    obs = observation(
        probe=CONDITIONAL, exit=1, errors=[("SI_EVIDENCE_INCOMPLETE", "model.sysml", 3)]
    )
    assert judge(probe, obs).certifies


def test_refused_rejects_a_location_in_another_file():
    obs = observation(exit=1, errors=[("SI_EXPRESSION_SOURCE_UNSUPPORTED", "other.sysml", 7)])
    assert judge(load_probe(REFUSED), obs).failed_check == FailedCheck.LOCATION_OUTSIDE_CONSTRUCT


def test_refused_rejects_an_extra_code_alongside_the_expected_one():
    errors = [
        ("SI_EXPRESSION_SOURCE_UNSUPPORTED", "model.sysml", 7),
        ("SI_SELF_BINDING", "model.sysml", 7),
    ]
    assert (
        judge(load_probe(REFUSED), observation(exit=1, errors=errors)).failed_check
        == "code_mismatch"
    )


def test_refused_rejects_a_nonzero_exit_with_no_error_line():
    assert (
        judge(load_probe(REFUSED), observation(exit=1)).failed_check == FailedCheck.NO_ERROR_LINES
    )
    assert (
        judge(load_probe(REFUSED), observation(exit=2)).failed_check == FailedCheck.UNEXPECTED_EXIT
    )


def test_an_error_line_without_any_code_is_a_code_mismatch():
    obs = dataclasses.replace(
        observation(exit=1),
        error_lines=("ERROR: agentic-mbse is not installed. Please install it first.",),
    )
    assert judge(load_probe(REFUSED), obs).failed_check == FailedCheck.CODE_MISMATCH


# --- admitted ------------------------------------------------------------------------------


def test_admitted_needs_positive_control_in_output():
    obs = observation(probe=ADMITTED, exit=0, generated=["catalog.py"], symbols=[])
    assert judge(load_probe(ADMITTED), obs).failed_check == "positive_control_missing"


def test_admitted_certifies_when_the_construct_is_generated():
    obs = observation(
        probe=ADMITTED,
        exit=0,
        symbols=["fx__site__a", "fx__site__eff__eff"],
        mentions={"fx__site__eff__eff": ["pipelines/pipeline.yaml"]},
    )
    assert judge(load_probe(ADMITTED), obs).certifies


def test_admitted_probe_the_generator_refuses_does_not_certify():
    obs = observation(probe=ADMITTED, exit=1, errors=[("SI_EVIDENCE_INCOMPLETE", "model.sysml", 6)])
    assert judge(load_probe(ADMITTED), obs).failed_check == FailedCheck.EXPECTED_SUCCESS_REFUSED


def test_admitted_without_a_catalog_does_not_certify():
    obs = observation(probe=ADMITTED, exit=0, symbols=None)
    assert judge(load_probe(ADMITTED), obs).failed_check == FailedCheck.CATALOG_MISSING


# --- omitted -------------------------------------------------------------------------------


def omitted_observation(symbols: list[str], element_files: list[str]) -> Observation:
    return observation(
        probe=OMITTED,
        exit=0,
        symbols=symbols,
        mentions={"fx__gen__fuel_unit": element_files, "fx__gen__rate": ["schemas/fx_params.py"]},
    )


def test_omitted_certifies_when_the_element_is_absent_and_the_sibling_present():
    assert judge(load_probe(OMITTED), omitted_observation(["fx__gen__rate"], [])).certifies


def test_omitted_element_that_appears_in_the_output_does_not_certify():
    probe = load_probe(OMITTED)
    in_catalog = omitted_observation(["fx__gen__rate", "fx__gen__fuel_unit"], [])
    assert judge(probe, in_catalog).failed_check == FailedCheck.OMITTED_ELEMENT_PRESENT
    in_text = omitted_observation(["fx__gen__rate"], ["schemas/fx_params.py"])
    assert judge(probe, in_text).failed_check == FailedCheck.OMITTED_ELEMENT_PRESENT


def test_omitted_without_the_numeric_sibling_does_not_certify():
    """Absence only means something if the search would have found a present name."""
    obs = omitted_observation([], [])
    assert judge(load_probe(OMITTED), obs).failed_check == FailedCheck.POSITIVE_CONTROL_MISSING


def test_omitted_observation_missing_mentions_is_a_harness_bug():
    obs = dataclasses.replace(omitted_observation(["fx__gen__rate"], []), mentions={})
    with pytest.raises(ObservationFormatError):
        judge(load_probe(OMITTED), obs)


# --- identity ------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("change", "check"),
    [
        ({"codegen_rev": "f" * 40}, FailedCheck.CODEGEN_REV_MISMATCH),
        ({"agentic_rev": "HEAD"}, FailedCheck.AGENTIC_REV_UNRESOLVED),
        ({"syside_version": "0.8.5"}, FailedCheck.SYSIDE_VERSION_MISMATCH),
        ({"uv_lock_sha256": "0" * 64}, FailedCheck.UV_LOCK_MISMATCH),
        (
            {"agentic_mbse_file": "/home/reid/src/agentic-mbse/src/agentic_mbse/__init__.py"},
            FailedCheck.PACKAGE_OUTSIDE_TREE,
        ),
        (
            {"sysml_codegen_file": "/home/reid/src/sysml-codegen/src/sysml_codegen/__init__.py"},
            FailedCheck.PACKAGE_OUTSIDE_TREE,
        ),
        ({"syside_file": "/usr/lib/python3/syside/__init__.py"}, FailedCheck.PACKAGE_OUTSIDE_TREE),
        ({"license_key_present": False}, FailedCheck.LICENSE_KEY_MISSING),
    ],
)
def test_identity_mismatch_does_not_certify(change: dict[str, object], check: FailedCheck):
    identity = dataclasses.replace(GOOD_IDENTITY, **change)  # type: ignore[arg-type]
    obs = observation(
        exit=1, errors=[("SI_EXPRESSION_SOURCE_UNSUPPORTED", "model.sysml", 7)], identity=identity
    )
    assert judge(load_probe(REFUSED), obs).failed_check == check


def test_a_sibling_directory_named_like_the_tree_is_outside_it():
    identity = dataclasses.replace(
        GOOD_IDENTITY, agentic_mbse_file=f"{TREE}-other/agentic_mbse/__init__.py"
    )
    obs = observation(
        exit=1, errors=[("SI_EXPRESSION_SOURCE_UNSUPPORTED", "model.sysml", 7)], identity=identity
    )
    assert judge(load_probe(REFUSED), obs).failed_check == FailedCheck.PACKAGE_OUTSIDE_TREE


def test_an_edited_model_invalidates_the_observation():
    obs = observation(exit=1, errors=[("SI_EXPRESSION_SOURCE_UNSUPPORTED", "model.sysml", 7)])
    obs = dataclasses.replace(obs, model_sha256="0" * 64)
    assert judge(load_probe(REFUSED), obs).failed_check == FailedCheck.MODEL_CHANGED


def test_timeout_and_probe_id_mismatch_do_not_certify():
    obs = observation(
        exit=1, errors=[("SI_EXPRESSION_SOURCE_UNSUPPORTED", "model.sysml", 7)], timed_out=True
    )
    assert judge(load_probe(REFUSED), obs).failed_check == FailedCheck.TIMED_OUT
    obs = observation(
        probe=ADMITTED, exit=1, errors=[("SI_EXPRESSION_SOURCE_UNSUPPORTED", "model.sysml", 7)]
    )
    assert judge(load_probe(REFUSED), obs).failed_check == FailedCheck.PROBE_ID_MISMATCH


# --- parsing and schemas -------------------------------------------------------------------


def test_parse_error_lines_reads_real_codegen_lines():
    """Lines as `b5663c07` printed them for the prototype fixtures."""
    lines = (
        "ERROR: Model is not ready for the exact route: SI_EXPRESSION_SOURCE_UNSUPPORTED: fx__Site__t.xs: "
        "reference='a, b': unsupported exact source form expression_source ('a, b') [root-0/model.sysml:7]",
        "ERROR: Model failed exact-route validation: SI_EVIDENCE_INCOMPLETE: if a < b ? a else b: "
        "reference='if a < b ? a else b': inspect_reference_uses: resolved reference has no exact target "
        "[root-0/model.sysml:3]; SI_INTERNAL_DEFECT: <internal defect>: unexpected internal failure: x",
    )
    assert parse_error_lines(lines) == (
        ReportedError("SI_EXPRESSION_SOURCE_UNSUPPORTED", "root-0/model.sysml", 7),
        ReportedError("SI_EVIDENCE_INCOMPLETE", "root-0/model.sysml", 3),
        ReportedError("SI_INTERNAL_DEFECT", None, None),
    )


def test_parse_error_lines_rejects_a_non_error_line():
    with pytest.raises(ObservationFormatError):
        parse_error_lines(("INFO: Generating code",))


def test_observation_round_trips_through_json(tmp_path: Path):
    obs = omitted_observation(["fx__gen__rate"], [])
    certification = judge(load_probe(OMITTED), obs)
    path = tmp_path / "observation.json"
    path.write_text(json.dumps(observation_to_json(obs, certification)))
    assert load_observation(path) == (obs, certification)


def test_observation_whose_certifies_disagrees_with_failed_check_is_rejected(tmp_path: Path):
    obs = observation(exit=1, errors=[("SI_SELF_BINDING", "model.sysml", 7)])
    document = observation_to_json(obs, judge(load_probe(REFUSED), obs))
    document["certifies"] = True
    path = tmp_path / "observation.json"
    path.write_text(json.dumps(document))
    with pytest.raises(ObservationFormatError):
        load_observation(path)


def test_every_shipped_probe_definition_loads():
    probes = [load_probe(d) for d in sorted(FIXTURES.iterdir()) if d.is_dir()]
    assert {p.id for p in probes} == {d.name for d in FIXTURES.iterdir() if d.is_dir()}


def write_probe(directory: Path, text: str) -> Path:
    directory.mkdir(parents=True)
    (directory / "model.sysml").write_text("package fx {}\n")
    (directory / "probe.toml").write_text(text)
    return directory


GOOD_PROBE = """\
kind = "record"
rule = "r"
shape = "s"
context = "c"
expected_outcome = "refused"
[construct]
description = "d"
file = "model.sysml"
lines = [1, 1]
[expect]
code = "SI_X"
"""


def test_a_well_formed_probe_loads(tmp_path: Path):
    assert load_probe(write_probe(tmp_path / "r__s__c", GOOD_PROBE)).id == "r__s__c"


@pytest.mark.parametrize(
    ("directory", "text", "message"),
    [
        ("wrong_name", GOOD_PROBE, "does not match directory"),
        ("r__s__c", 'colour = "red"\n' + GOOD_PROBE, "unknown keys \\['colour'\\]"),
        (
            "r__s__c",
            GOOD_PROBE.replace('"refused"', '"maybe"'),
            "is not refused, admitted, omitted or excluded",
        ),
        ("r__s__c", GOOD_PROBE.replace('"record"', '"guess"'), "is not a probe kind"),
        (
            "r__s__c",
            GOOD_PROBE.replace('"record"', '"control"'),
            "a control probe expects the generator to admit",
        ),
        ("r__s__c", GOOD_PROBE.replace("[1, 1]", "[3, 2]"), "construct.lines"),
        ("r__s__c", GOOD_PROBE.replace('"model.sysml"', '"absent.sysml"'), "does not exist"),
        ("r__s__c", GOOD_PROBE.replace("SI_X", "X"), "is not an SI_ code"),
        (
            "r__s__c",
            GOOD_PROBE.replace('code = "SI_X"', 'positive_control = "p"'),
            "missing keys \\['code'\\]",
        ),
    ],
)
def test_probe_definition_errors_are_loud(tmp_path: Path, directory: str, text: str, message: str):
    with pytest.raises(ProbeDefinitionError, match=message):
        load_probe(write_probe(tmp_path / directory, text))


# --- the block-reason location and the excluded outcome ----------------------------------------

BLOCKED_LINE = (
    "ERROR: Model failed exact-route validation: SI_CONSTRAINT_BLOCKED: fx__site__c: constraint "
    "profile blocked execution: block_non_numerical_containment: the numerical assertion contains "
    "a non-numerical feature_ref and generation stops; separate it into its own assertion or "
    "rewrite it as a numerical comparison [model.sysml:6]"
)


def test_parse_error_lines_reads_the_block_reason_location_for_blocked_constraints_only():
    """`elaborate.py:448-457`: SI_CONSTRAINT_BLOCKED is located by the profile, as a basename."""
    assert parse_error_lines((BLOCKED_LINE,)) == (
        ReportedError("SI_CONSTRAINT_BLOCKED", "model.sysml", 6),
    )
    other = BLOCKED_LINE.replace("SI_CONSTRAINT_BLOCKED", "SI_EVIDENCE_INCOMPLETE")
    assert parse_error_lines((other,)) == (ReportedError("SI_EVIDENCE_INCOMPLETE", None, None),)


BLOCKED_PROBE = GOOD_PROBE.replace("SI_X", "SI_CONSTRAINT_BLOCKED").replace("[1, 1]", "[6, 6]")


def test_a_blocked_constraint_certifies_inside_the_construct_and_not_outside(tmp_path: Path):
    probe = load_probe(write_probe(tmp_path / "r__s__c", BLOCKED_PROBE))
    obs = dataclasses.replace(
        observation(exit=1, errors=[]), probe_id=probe.id, model_sha256=probe.model_sha256
    )
    inside = dataclasses.replace(obs, error_lines=(BLOCKED_LINE,))
    assert judge(probe, inside).certifies
    outside = dataclasses.replace(
        obs, error_lines=(BLOCKED_LINE.replace("model.sysml:6", "model.sysml:9"),)
    )
    assert judge(probe, outside).failed_check is FailedCheck.LOCATION_OUTSIDE_CONSTRUCT
    elsewhere = dataclasses.replace(
        obs, error_lines=(BLOCKED_LINE.replace("model.sysml:6", "other.sysml:6"),)
    )
    assert judge(probe, elsewhere).failed_check is FailedCheck.LOCATION_OUTSIDE_CONSTRUCT


EXCLUDED_PROBE = GOOD_PROBE.replace('"refused"', '"excluded"').replace(
    'code = "SI_X"', 'excluded_element = "fx__site__c"\npositive_control = "fx__site__x"'
)


def test_excluded_certifies_like_omitted(tmp_path: Path):
    probe = load_probe(write_probe(tmp_path / "r__s__c", EXCLUDED_PROBE))
    assert probe.expected_outcome == "excluded"
    base = dataclasses.replace(
        omitted_observation(["fx__site__x"], []),
        probe_id=probe.id,
        model_sha256=probe.model_sha256,
        mentions={"fx__site__c": (), "fx__site__x": ("catalog.py",)},
    )
    assert judge(probe, base).certifies
    present = dataclasses.replace(base, mentions={**base.mentions, "fx__site__c": ("contract.py",)})
    assert judge(probe, present).failed_check is FailedCheck.OMITTED_ELEMENT_PRESENT
