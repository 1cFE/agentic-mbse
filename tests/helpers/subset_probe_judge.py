"""Judge whether one probe run of the pinned generator certifies its (rule, shape, context) pair.

This is design invariant 2, the single copy of the certification rule (plan P-2). The probe
harness (`scripts/subset_profile/probe.py`) imports it to write `certifies` into each
observation, and the test suite re-judges stored observations with it. Pure and stdlib-only.

A probe is a directory `tests/fixtures/subset_profile/probes/<id>/` holding `probe.toml` (what
the run must show), `model.sysml` (one probed construct) and `observation.json` (what the run
showed). The id is `rule__shape__context`, with `__variant` appended when one (shape, context)
pair has several probes.

How the generator reports a refusal (sysml-codegen `b5663c07`). `cmd_generate` configures
logging as `%(levelname)s: %(message)s` (`cli/__init__.py:833`) and `run_codegen` logs one
line per refusal class (`cli/__init__.py:1189-1230`), then exits 1 (`cli/__init__.py:857`):

    ERROR: <gate>: <CODE>: <subject>[: reference='<text>']: <detail>[ [<referent>:<line>]]

- `<gate>` names the refusing stage, e.g. "Model is not ready for the exact route".
- Several findings in one line are joined by "; " (`elaboration/elaborate.py:130`, `:151`).
- The location suffix is present only when codegen measured one (`elaborate.py:134-144`,
  `:192-200`); `unexpected_public_failure` deliberately omits it (`elaborate.py:170-190`).
- `<referent>` is `root-<slot>/<path relative to that --models root>`
  (`analysis/source_referent.py:43-70`). The harness passes one model file, so the slot is 0
  and the path is the file name: `[root-0/model.sysml:7]`.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Any

import tomllib

PINNED_CODEGEN_REV = "b5663c07e987a892e27d21e68cec40d0656574ee"
PINNED_SYSIDE_VERSION = "0.8.4"
# sha256 of `git show b5663c07:uv.lock` in sysml-codegen.
PINNED_UV_LOCK_SHA256 = "a17e9fa120983389d45d2e2a47edbe4da38d67ffe78c07c5f048aacacabee4d4"

# The harness runs each probe with exactly one `--models` file, which codegen names root slot 0.
_PROBE_ROOT_SLOT = 0

_ERROR_PREFIX = "ERROR: "
# A finding starts after the gate ("<gate>: ", the gate has no colon) or after a "; " join.
_FINDING_START = re.compile(r"(?:^[^:]+: |; )(SI_[A-Z0-9_]+): ")
_LOCATION_SUFFIX = re.compile(r" \[(root-\d+/[^\]]+):(\d+)\]$")
_REV = re.compile(r"[0-9a-f]{40}")


class ProbeDefinitionError(ValueError):
    """A probe.toml that breaks the probe schema."""


class ObservationFormatError(ValueError):
    """An observation that breaks the schema the harness writes."""


class FailedCheck(StrEnum):
    """Why a run does not certify its probe. Closed; the first failing check is reported."""

    PROBE_ID_MISMATCH = "probe_id_mismatch"
    MODEL_CHANGED = "model_changed"  # model.sysml is not the file the run read
    CODEGEN_REV_MISMATCH = "codegen_rev_mismatch"
    AGENTIC_REV_UNRESOLVED = "agentic_rev_unresolved"
    SYSIDE_VERSION_MISMATCH = "syside_version_mismatch"
    UV_LOCK_MISMATCH = "uv_lock_mismatch"
    PACKAGE_OUTSIDE_TREE = "package_outside_tree"
    LICENSE_KEY_MISSING = "license_key_missing"
    TIMED_OUT = "timed_out"
    # refused probes
    REFUSED_PROBE_ADMITTED = "refused_probe_admitted"  # the R2 signal
    UNEXPECTED_EXIT = "unexpected_exit"
    NO_ERROR_LINES = "no_error_lines"
    CODE_MISMATCH = "code_mismatch"
    LOCATION_MISSING = "location_missing"
    LOCATION_OUTSIDE_CONSTRUCT = "location_outside_construct"
    # admitted and omitted probes
    EXPECTED_SUCCESS_REFUSED = "expected_success_refused"
    ERROR_LINES_ON_SUCCESS = "error_lines_on_success"
    CATALOG_MISSING = "catalog_missing"
    POSITIVE_CONTROL_MISSING = "positive_control_missing"
    OMITTED_ELEMENT_PRESENT = "omitted_element_present"


@dataclass(frozen=True)
class Construct:
    """The one probed construct and the source lines it is declared on (inclusive)."""

    description: str
    file: str
    first_line: int
    last_line: int


@dataclass(frozen=True)
class Refused:
    """The run must refuse with exactly this code, located inside the construct."""

    code: str


@dataclass(frozen=True)
class Admitted:
    """The run must succeed and generate `positive_control`, a catalog name the construct yields."""

    positive_control: str


@dataclass(frozen=True)
class Omitted:
    """The run must succeed, generate the numeric sibling `positive_control`, and never name `element`."""

    element: str
    positive_control: str


Expectation = Refused | Admitted | Omitted


@dataclass(frozen=True)
class Probe:
    id: str
    rule: str
    shape: str
    context: str
    variant: str | None
    supersedes: str | None
    construct: Construct
    expect: Expectation
    model_sha256: str

    def declared_names(self) -> tuple[str, ...]:
        """Catalog names the harness must report text mentions for."""
        match self.expect:
            case Refused():
                return ()
            case Admitted(positive_control=control):
                return (control,)
            case Omitted(element=element, positive_control=control):
                return (element, control)


@dataclass(frozen=True)
class Identity:
    """Who ran the probe: the exported revisions, the resolved environment and its location."""

    codegen_rev: str
    agentic_rev: str
    sysml_codegen_version: str
    agentic_mbse_version: str
    syside_version: str
    python_version: str
    uv_lock_sha256: str
    tree_root: str
    sysml_codegen_file: str
    agentic_mbse_file: str
    syside_file: str
    license_key_present: bool


@dataclass(frozen=True)
class Observation:
    """One generator run on one probe's model, as the harness captured it."""

    probe_id: str
    model_sha256: str
    identity: Identity
    argv: tuple[str, ...]
    exit_code: int
    timed_out: bool
    error_lines: tuple[str, ...]
    generated_files: Mapping[str, str]  # path relative to the output dir -> sha256
    catalog_names: tuple[str, ...] | None  # None: no contracts/model_contract.json was written
    mentions: Mapping[str, tuple[str, ...]]  # declared name -> generated files naming it


@dataclass(frozen=True)
class ReportedError:
    """One finding parsed from an `ERROR:` line. `code` is None when the line names no SI_ code."""

    code: str | None
    referent: str | None
    line: int | None


@dataclass(frozen=True)
class Certification:
    failed_check: FailedCheck | None

    @property
    def certifies(self) -> bool:
        return self.failed_check is None


def _take(table: Mapping[str, Any], allowed: set[str], required: set[str], where: str) -> None:
    unknown = set(table) - allowed
    missing = required - set(table)
    if unknown or missing:
        raise ProbeDefinitionError(
            f"{where}: unknown keys {sorted(unknown)}, missing keys {sorted(missing)}"
        )


def _expectation(outcome: str, expect: Mapping[str, Any], where: str) -> Expectation:
    match outcome:
        case "refused":
            _take(expect, {"code"}, {"code"}, where)
            if not re.fullmatch(r"SI_[A-Z0-9_]+", expect["code"]):
                raise ProbeDefinitionError(f"{where}: code {expect['code']!r} is not an SI_ code")
            return Refused(code=expect["code"])
        case "admitted":
            _take(expect, {"positive_control"}, {"positive_control"}, where)
            return Admitted(positive_control=expect["positive_control"])
        case "omitted":
            keys = {"omitted_element", "positive_control"}
            _take(expect, keys, keys, where)
            return Omitted(
                element=expect["omitted_element"], positive_control=expect["positive_control"]
            )
    raise ProbeDefinitionError(
        f"{where}: expected_outcome {outcome!r} is not refused, admitted or omitted"
    )


def load_probe(directory: Path) -> Probe:
    """Read and validate `<directory>/probe.toml`. The directory name must equal the probe id."""
    where = str(directory / "probe.toml")
    data = tomllib.loads((directory / "probe.toml").read_text(encoding="utf-8"))
    top = {
        "rule",
        "shape",
        "context",
        "variant",
        "expected_outcome",
        "supersedes",
        "construct",
        "expect",
    }
    _take(data, top, top - {"variant", "supersedes"}, where)
    _take(
        data["construct"], {"description", "file", "lines"}, {"description", "file", "lines"}, where
    )
    lines = data["construct"]["lines"]
    if not (
        len(lines) == 2
        and all(isinstance(n, int) and n > 0 for n in lines)
        and lines[0] <= lines[1]
    ):
        raise ProbeDefinitionError(
            f"{where}: construct.lines must be [first, last] with 0 < first <= last"
        )
    if not (directory / data["construct"]["file"]).is_file():
        raise ProbeDefinitionError(
            f"{where}: construct.file {data['construct']['file']!r} does not exist"
        )
    variant = data.get("variant")
    probe_id = "__".join(
        part for part in (data["rule"], data["shape"], data["context"], variant) if part is not None
    )
    if probe_id != directory.name:
        raise ProbeDefinitionError(
            f"{where}: id {probe_id!r} does not match directory {directory.name!r}"
        )
    return Probe(
        id=probe_id,
        rule=data["rule"],
        shape=data["shape"],
        context=data["context"],
        variant=variant,
        supersedes=data.get("supersedes"),
        construct=Construct(
            description=data["construct"]["description"],
            file=data["construct"]["file"],
            first_line=lines[0],
            last_line=lines[1],
        ),
        expect=_expectation(data["expected_outcome"], data["expect"], where),
        model_sha256=hashlib.sha256(
            (directory / data["construct"]["file"]).read_bytes()
        ).hexdigest(),
    )


def parse_error_lines(error_lines: tuple[str, ...]) -> tuple[ReportedError, ...]:
    """Split codegen `ERROR:` lines into findings, each with its code and location if present."""
    findings: list[ReportedError] = []
    for raw in error_lines:
        if not raw.startswith(_ERROR_PREFIX):
            raise ObservationFormatError(f"not an ERROR line: {raw!r}")
        body = raw[len(_ERROR_PREFIX) :]
        starts = list(_FINDING_START.finditer(body))
        if not starts:
            findings.append(ReportedError(code=None, referent=None, line=None))
            continue
        for match, following in zip(starts, [*starts[1:], None], strict=True):
            segment = body[match.end() : following.start() if following else len(body)]
            location = _LOCATION_SUFFIX.search(segment)
            findings.append(
                ReportedError(
                    code=match.group(1),
                    referent=location.group(1) if location else None,
                    line=int(location.group(2)) if location else None,
                )
            )
    return tuple(findings)


def _inside(path: str, root: str) -> bool:
    return PurePosixPath(root).is_absolute() and PurePosixPath(path).is_relative_to(root)


def _identity_failure(identity: Identity) -> FailedCheck | None:
    if identity.codegen_rev != PINNED_CODEGEN_REV:
        return FailedCheck.CODEGEN_REV_MISMATCH
    if not _REV.fullmatch(identity.agentic_rev):
        return FailedCheck.AGENTIC_REV_UNRESOLVED
    if identity.syside_version != PINNED_SYSIDE_VERSION:
        return FailedCheck.SYSIDE_VERSION_MISMATCH
    if identity.uv_lock_sha256 != PINNED_UV_LOCK_SHA256:
        return FailedCheck.UV_LOCK_MISMATCH
    files = (identity.sysml_codegen_file, identity.agentic_mbse_file, identity.syside_file)
    if not all(_inside(f, identity.tree_root) for f in files):
        return FailedCheck.PACKAGE_OUTSIDE_TREE
    if not identity.license_key_present:
        return FailedCheck.LICENSE_KEY_MISSING
    return None


def _refusal_failure(construct: Construct, expect: Refused, obs: Observation) -> FailedCheck | None:
    if obs.exit_code == 0:
        return FailedCheck.REFUSED_PROBE_ADMITTED
    if obs.exit_code != 1:
        return FailedCheck.UNEXPECTED_EXIT
    errors = parse_error_lines(obs.error_lines)
    if not errors:
        return FailedCheck.NO_ERROR_LINES
    if {e.code for e in errors} != {expect.code}:
        return FailedCheck.CODE_MISMATCH
    if any(e.line is None for e in errors):
        return FailedCheck.LOCATION_MISSING
    referent = f"root-{_PROBE_ROOT_SLOT}/{construct.file}"
    for e in errors:
        assert e.line is not None
        if e.referent != referent or not construct.first_line <= e.line <= construct.last_line:
            return FailedCheck.LOCATION_OUTSIDE_CONSTRUCT
    return None


def _success_failure(obs: Observation) -> FailedCheck | None:
    if obs.exit_code != 0:
        return FailedCheck.EXPECTED_SUCCESS_REFUSED
    if obs.error_lines:
        return FailedCheck.ERROR_LINES_ON_SUCCESS
    if obs.catalog_names is None:
        return FailedCheck.CATALOG_MISSING
    return None


def _mentions(obs: Observation, name: str) -> tuple[str, ...]:
    if name not in obs.mentions:
        raise ObservationFormatError(
            f"{obs.probe_id}: observation reports no mentions for {name!r}"
        )
    return obs.mentions[name]


def judge(probe: Probe, obs: Observation) -> Certification:
    """Certify `obs` against `probe` (invariant 2), or name the first check it fails."""
    if obs.probe_id != probe.id:
        return Certification(FailedCheck.PROBE_ID_MISMATCH)
    if obs.model_sha256 != probe.model_sha256:
        return Certification(FailedCheck.MODEL_CHANGED)
    failure = _identity_failure(obs.identity)
    if failure is None and obs.timed_out:
        failure = FailedCheck.TIMED_OUT
    if failure is not None:
        return Certification(failure)
    match probe.expect:
        case Refused() as expect:
            return Certification(_refusal_failure(probe.construct, expect, obs))
        case Admitted(positive_control=control):
            failure = _success_failure(obs)
            if failure is None and control not in (obs.catalog_names or ()):
                failure = FailedCheck.POSITIVE_CONTROL_MISSING
            return Certification(failure)
        case Omitted(element=element, positive_control=control):
            failure = _success_failure(obs)
            if failure is None and control not in (obs.catalog_names or ()):
                failure = FailedCheck.POSITIVE_CONTROL_MISSING
            if failure is None and (
                element in (obs.catalog_names or ()) or _mentions(obs, element)
            ):
                failure = FailedCheck.OMITTED_ELEMENT_PRESENT
            return Certification(failure)


def observation_to_json(obs: Observation, certification: Certification) -> dict[str, Any]:
    """The `observation.json` document: the run, plus the judge's verdict on it."""
    return {
        "probe_id": obs.probe_id,
        "model_sha256": obs.model_sha256,
        "identity": vars(obs.identity),
        "run": {
            "argv": list(obs.argv),
            "exit_code": obs.exit_code,
            "timed_out": obs.timed_out,
            "error_lines": list(obs.error_lines),
            "generated_files": dict(sorted(obs.generated_files.items())),
            "catalog_names": None if obs.catalog_names is None else list(obs.catalog_names),
            "mentions": {name: list(files) for name, files in sorted(obs.mentions.items())},
        },
        "certifies": certification.certifies,
        "failed_check": None
        if certification.failed_check is None
        else str(certification.failed_check),
    }


def load_observation(path: Path) -> tuple[Observation, Certification]:
    """Read an `observation.json`; returns the run and the verdict recorded with it."""
    data = json.loads(path.read_text(encoding="utf-8"))
    try:
        identity = Identity(**data["identity"])
        run = data["run"]
        obs = Observation(
            probe_id=data["probe_id"],
            model_sha256=data["model_sha256"],
            identity=identity,
            argv=tuple(run["argv"]),
            exit_code=run["exit_code"],
            timed_out=run["timed_out"],
            error_lines=tuple(run["error_lines"]),
            generated_files=run["generated_files"],
            catalog_names=None if run["catalog_names"] is None else tuple(run["catalog_names"]),
            mentions={name: tuple(files) for name, files in run["mentions"].items()},
        )
        recorded = Certification(
            None if data["failed_check"] is None else FailedCheck(data["failed_check"])
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ObservationFormatError(f"{path}: {error}") from error
    if recorded.certifies != data["certifies"]:
        raise ObservationFormatError(f"{path}: certifies disagrees with failed_check")
    return obs, recorded
