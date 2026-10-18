"""The positional-binding check as L2 runs it: extract, find the pin list, decide, render.

This is the only part of the check that touches SysIDE or the filesystem; the rule itself
(`positional_binding.decide`) is pure. :func:`check` returns the check's issues and metrics,
and :func:`is_pinned_positional_warning` is the one exception to L2's pass rule (design I1):
a pinned positional WARNING does not by itself fail L2.

Issues (design "Issues and metrics"):

- an unpinned or unpinnable mismatch is ``L2_POSITIONAL_BINDING`` at ERROR, a pinned one at
  WARNING, ``reason_code`` ``POSITIONAL_SWAP`` or ``POSITIONAL_SPECIAL_SLOT``;
- a stale pin is ``L2_POSITIONAL_PIN_STALE`` at ERROR;
- a pin list that cannot be used is ``L2_POSITIONAL_PIN_LIST_INVALID`` at ERROR, and the check
  then runs as if there were no list (D14);
- an inspection failure is ``L2_CHECK_UNVERIFIABLE`` at ERROR, ``reason_code``
  ``POSITIONAL_<cause>``; a pin never applies to it (I2).
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path, PurePosixPath
from typing import Any

from agentic_mbse.sysml.parameter_redefinition_extraction import extract_parameter_redefinitions
from agentic_mbse.sysml.parameter_redefinition_facts import ParameterRole, RedefinitionFailure
from agentic_mbse.sysml.types import Severity, ValidationCode, ValidationIssue
from agentic_mbse.validation.positional_binding import (
    FindingReason,
    PinScope,
    PositionalFinding,
    PositionalResult,
    StalePin,
    StaleReason,
    decide,
)
from agentic_mbse.validation.positional_pins import (
    PinList,
    PinListAbsent,
    PinListInvalid,
    PinListResult,
    discover,
    load,
)

__all__ = [
    "PINNED_DISCLAIMER",
    "check",
    "describe_pin_list",
    "is_pinned_positional_warning",
    "render",
]

PINNED_DISCLAIMER = (
    "Pinned as legacy; this does not show that native values are correct or that the "
    "native and generated routes agree."
)

#: Ends every unpinned, pinnable ERROR, ahead of the copyable fields (audit Advisory 4).
PIN_ELIGIBILITY = (
    "Pin these fields only for a mismatch that existed at the pin list's recorded_against "
    "revision; repair a new one"
)

_ROLE_SLOT = {
    ParameterRole.SUBJECT: "subject",
    ParameterRole.ACTOR: "actor",
    ParameterRole.STAKEHOLDER: "stakeholder",
}

_STALE_TEXT = {
    StaleReason.NOT_FOUND_IN_VALIDATED_FILE: "no such finding in the validated files",
    StaleReason.PINNED_FILE_MISSING: "the pinned file does not exist under the pin root",
}


def is_pinned_positional_warning(issue: ValidationIssue) -> bool:
    """Whether L2's pass rule ignores this issue: only a pinned positional WARNING (I1)."""
    return issue.code is ValidationCode.L2_POSITIONAL_BINDING and issue.severity is Severity.WARNING


def check(
    model: Any,
    models_path: Path,
    files: Sequence[Path],
    pins_file: Path | None,
    pin_root: Path | None,
) -> tuple[list[ValidationIssue], dict[str, object]]:
    """Run the check over one loaded model. ``files`` are the files the model was loaded from.

    ``pins_file`` is the ``--positional-pins`` option; without it the pin list is looked for
    at the project root above ``models_path`` (D11). ``pin_root`` is
    ``--positional-pins-root`` and needs ``pins_file`` (D12); the caller rejects it alone.
    """
    if pin_root is not None and pins_file is None:
        raise ValueError(
            "a pin root needs a pin file (--positional-pins-root without --positional-pins)"
        )
    facts = extract_parameter_redefinitions(model)
    pin_list = _pin_list(models_path, pins_file, pin_root)
    scope = _scope(pin_list, files) if isinstance(pin_list, PinList) else None
    result = decide(facts, scope)
    issues, metrics = render(result, report_root=_report_root(pin_list, pin_root))
    if isinstance(pin_list, PinListInvalid):
        issues.insert(0, invalid_pin_list_issue(pin_list))
    metrics["Positional pin list"] = describe_pin_list(pin_list, models_path)
    return issues, metrics


def _pin_list(models_path: Path, pins_file: Path | None, pin_root: Path | None) -> PinListResult:
    if pins_file is not None:
        return load(pins_file, pin_root if pin_root is not None else pins_file.parent)
    found = discover(models_path)
    if isinstance(found, PinListAbsent):
        return found
    return load(found, found.parent)


def _scope(pin_list: PinList, files: Sequence[Path]) -> PinScope:
    root = pin_list.pin_root.resolve()
    validated: set[PurePosixPath] = set()
    for file in files:
        relative = _relative(file, root)
        if relative is not None:  # a validated file outside the pin root cannot be pinned
            validated.add(relative)
    existing = {pin.file for pin in pin_list.pins if (pin_list.pin_root / pin.file).is_file()}
    return PinScope(pin_list, frozenset(validated), frozenset(existing))


def _relative(file: Path, root: Path) -> PurePosixPath | None:
    try:
        return PurePosixPath(file.resolve().relative_to(root).as_posix())
    except ValueError:
        return None


def _report_root(pin_list: PinListResult, pin_root: Path | None) -> Path | None:
    """What messages print files relative to, so a finding's file can be copied into a pin."""
    if pin_root is not None:
        return pin_root
    if isinstance(pin_list, PinList):
        return pin_list.pin_root
    if isinstance(pin_list, PinListInvalid):
        return pin_list.path.parent
    return pin_list.project_root


# ---- rendering ---------------------------------------------------------------------------------


def render(
    result: PositionalResult, report_root: Path | None
) -> tuple[list[ValidationIssue], dict[str, object]]:
    """The decision's findings, stale pins and failures as issues, in that order, and its counts.

    Files print relative to ``report_root`` when they are under it, else as SysIDE gave them.
    """
    root = None if report_root is None else report_root.resolve()
    issues = [_finding_issue(f, root) for f in result.findings]
    issues += [_stale_issue(s) for s in result.stale]
    issues += [_failure_issue(f, root) for f in result.failures]
    pinned = sum(1 for f in result.findings if f.pinned)
    metrics: dict[str, object] = {
        "Positional inputs inspected": result.inputs_inspected,
        "Positional input outcomes": ", ".join(
            f"{outcome.value} {count}" for outcome, count in result.outcomes.items()
        ),
        "Positional bindings (blocking)": len(result.findings) - pinned,
        "Positional bindings pinned (legacy warning)": pinned,
        "Positional pins stale": len(result.stale),
        "Positional pins out of scope": len(result.out_of_scope),
        "Positional pins not judged (inspection failed)": len(result.not_judged),
        "Positional unverifiable": len(result.failures),
    }
    return issues, metrics


def describe_pin_list(pin_list: PinListResult, models_path: Path) -> str:
    """The pin-list metric: which file was used, or where it was looked for (D11, D12)."""
    if isinstance(pin_list, PinList):
        return (
            f"{pin_list.path} (pin root {pin_list.pin_root}; recorded against "
            f"{pin_list.revision} on {pin_list.recorded.isoformat()}; {len(pin_list.pins)} pins)"
        )
    if isinstance(pin_list, PinListInvalid):
        return f"invalid: {pin_list.path} ({pin_list.reason_code.value}); checked as if absent"
    if pin_list.looked_at is None:
        return f"none (no project root above {models_path}; pass --positional-pins)"
    return f"none (looked at {pin_list.looked_at})"


def invalid_pin_list_issue(pin_list: PinListInvalid) -> ValidationIssue:
    return ValidationIssue(
        level=2,
        severity=Severity.ERROR,
        code=ValidationCode.L2_POSITIONAL_PIN_LIST_INVALID,
        message=(
            f"positional pin list {pin_list.path} cannot be used ({pin_list.reason_code.value}): "
            f"{pin_list.detail}. Every positional mismatch is reported as if no list existed"
        ),
        element_name=str(pin_list.path),
        reason_code=pin_list.reason_code.value,
    )


def _display_file(file: str | None, root: Path | None) -> str:
    if file is None:
        return "<unknown file>"
    if root is not None:
        relative = _relative(Path(file), root)
        if relative is not None:
            return str(relative)
    return file


def _finding_issue(finding: PositionalFinding, root: Path | None) -> ValidationIssue:
    file = _display_file(finding.location.file, root)
    line = finding.location.line
    owner = finding.owner.qualified_name
    target = finding.target
    target_name = target.formal.qualified_name or f"an unnamed formal of {_type_label(finding)}"
    owner_label = f"'{owner}'" if owner else f"an anonymous {finding.owner.kind}"
    if finding.reason is FindingReason.SPECIAL_SLOT:
        slot = _ROLE_SLOT[target.role]
        text = (
            f"Input '{finding.input_name}' of {owner_label} lands by position on the {slot} slot "
            f"of {_type_label(finding)} ('{target_name}'). Declare `subject` (and any "
            f"`actor`/`stakeholder`) before ordinary inputs"
        )
    else:
        text = (
            f"Input '{finding.input_name}' of {owner_label} binds by position to '{target_name}', "
            f"a formal named '{target.name}': a likely authoring hazard in valid SysML (an "
            f"unprefixed input binds by position, KerML checkFeatureParameterRedefinition). "
            f"Choose the intended formal from the definition, then bind it by name "
            f"(`in :>> <formal> = ...`) or, for a deliberate rename, write "
            f"`in {finding.input_name} redefines <formal> = ...`"
        )
    if finding.identity is None:
        text += (
            ". This finding cannot be pinned: the owner or target has no qualified name. "
            "Name the owner or repair the binding"
        )
        fields = (
            f"owner = {owner_label}, input = {finding.input_name}, file = {file}, line = {line}"
        )
    else:
        identity = finding.identity
        fields = (
            f'owner = "{identity.owner}", input = "{identity.input}", '
            f'target = "{identity.target}", file = "{file}", line = {line}'
        )
    if finding.pinned:
        text += f". {PINNED_DISCLAIMER}"
    elif finding.identity is not None:
        text += f". {PIN_ELIGIBILITY}"
    return ValidationIssue(
        level=2,
        severity=Severity.WARNING if finding.pinned else Severity.ERROR,
        code=ValidationCode.L2_POSITIONAL_BINDING,
        message=f"{text} [{fields}]",
        element_name=owner or "<anonymous>",
        location=f"{file}:{line}",
        reason_code=finding.reason.value,
    )


def _type_label(finding: PositionalFinding) -> str:
    owning = finding.target.owning_type
    return f"'{owning.qualified_name}'" if owning.qualified_name else f"an anonymous {owning.kind}"


def _stale_issue(stale: StalePin) -> ValidationIssue:
    pin = stale.pin
    identity = pin.identity
    return ValidationIssue(
        level=2,
        severity=Severity.ERROR,
        code=ValidationCode.L2_POSITIONAL_PIN_STALE,
        message=(
            f"Positional pin {identity.owner} | {identity.input} | {identity.target} "
            f"({pin.file}:{pin.line}) matches no finding: {_STALE_TEXT[stale.reason]}. If the "
            f"binding was repaired, remove the pin; a pin records only a mismatch that existed "
            f"at the list's recorded_against revision"
        ),
        element_name=identity.owner,
        location=f"{pin.file}:{pin.line}",
        reason_code=stale.reason.value,
    )


def _failure_issue(failure: RedefinitionFailure, root: Path | None) -> ValidationIssue:
    subject = failure.subject
    if subject is None:
        where, location, name = "the model's calc and constraint owners", "", "<model>"
    else:
        name = subject.qualified_name or "<unnamed element>"
        location = f"{_display_file(subject.file, root)}:{subject.line}"
        where = f"'{name}'" if subject.qualified_name else f"an unnamed element at {location}"
    return ValidationIssue(
        level=2,
        severity=Severity.ERROR,
        code=ValidationCode.L2_CHECK_UNVERIFIABLE,
        message=(
            f"positional-binding check could not inspect {where}: {failure.cause.value}: "
            f"{failure.detail}. Its inputs are unverified; treat this as a check failure, not a "
            f"clean result, and no pin applies to it"
        ),
        element_name=name,
        location=location,
        reason_code=f"POSITIONAL_{failure.cause.name}",
    )
