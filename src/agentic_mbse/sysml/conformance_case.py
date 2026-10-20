"""Packaged conformance cases: small models, each with the screen's stored answer.

A conformance case (EXEC-SUBSET-CONTRACT Item 2a, design D14) is a model that pins one
(rule, shape, context) pair, or a neighbor of one, together with what the subset screen
reports on it. The cases a rule record cites, and the cases that test a rule's recognizer,
ship here as package data, so agentic-mbse's tests can run the screen on them and
sysml-codegen can read them through this package. What the generator does on each case is
sysml-codegen's fact, stored and checked there; nothing here describes the generator.

Each case is a directory ``subset_cases/<case_id>/`` beside this module, holding the model's
``.sysml`` files and ``case.json``:

- ``schema``: ``subset-case/1``;
- ``kind``: a ``record`` case backs a record pair, a ``control`` case is an admitted
  neighbor no rule recognizes, and a ``reproduction`` case reproduces a candidate refusal
  family that has no rule;
- ``construct``: the file and the inclusive lines of the one construct the case is about;
- ``screen``: the verdict and every finding the screen reports, not only the construct's,
  so an unrelated rule change also shows as a difference;
- ``agentic_site_witnesses``: the agentic-mbse raise sites the case shows firing;
- ``provenance``: the Item 1 probe the case was moved from, if any, and a note.

:func:`screen_answer` turns a live result into the stored form, so a test compares the two
with ``==``. This module reads files and imports no SysIDE.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from importlib import resources
from pathlib import Path
from typing import Any, TypeVar

from agentic_mbse.sysml.subset_profile import ContextId, Outcome, SubsetProfileResult, Verdict

__all__ = [
    "CASE_SCHEMA",
    "CaseFormatError",
    "CaseKind",
    "Construct",
    "PackagedCase",
    "ScreenAnswer",
    "ScreenFinding",
    "load_case",
    "load_packaged_case",
    "packaged_case_dir",
    "packaged_case_ids",
    "screen_answer",
    "screen_answer_from_json",
    "screen_answer_to_json",
]

CASE_SCHEMA = "subset-case/1"
_CASE_FILE = "case.json"

_E = TypeVar("_E", bound=StrEnum)


class CaseFormatError(ValueError):
    """A packaged case directory or its ``case.json`` breaks the case format."""


class CaseKind(StrEnum):
    #: Backs a (rule, shape, context) pair; a record cites it.
    RECORD = "record"
    #: An admitted neighbor of a rule's shape that the rule does not recognize.
    CONTROL = "control"
    #: Reproduces a candidate refusal family with no rule.
    REPRODUCTION = "reproduction"


@dataclass(frozen=True)
class Construct:
    """The one construct a case is about: its file and inclusive source lines."""

    file: str
    first_line: int
    last_line: int
    description: str

    def contains(self, line: int) -> bool:
        return self.first_line <= line <= self.last_line


@dataclass(frozen=True)
class ScreenFinding:
    """One finding as stored: the decided pair, its outcome, and what it is about.

    ``subject`` is the finding's qualified name, or ``<anonymous KIND>`` for an element
    SysIDE gives no name; ``line`` then tells such subjects apart.
    """

    rule: str
    shape: str
    context: ContextId
    outcome: Outcome
    subject: str
    line: int | None


@dataclass(frozen=True)
class ScreenAnswer:
    verdict: Verdict
    #: Sorted, so two answers compare equal exactly when the screen reports the same things.
    findings: tuple[ScreenFinding, ...]


@dataclass(frozen=True)
class PackagedCase:
    case_id: str
    kind: CaseKind
    #: The case's directory; every ``.sysml`` file in it is part of the model.
    directory: Path
    construct: Construct
    screen: ScreenAnswer
    agentic_site_witnesses: tuple[str, ...]
    #: The Item 1 probe this case was moved from, if any.
    from_probe: str | None
    note: str

    def model_files(self) -> tuple[Path, ...]:
        return tuple(sorted(self.directory.glob("*.sysml")))


def _finding_key(finding: ScreenFinding) -> tuple[str, str, str, str, int, str]:
    line = -1 if finding.line is None else finding.line
    return (
        finding.rule,
        finding.shape,
        finding.context.value,
        finding.subject,
        line,
        finding.outcome.value,
    )


def screen_answer(result: SubsetProfileResult) -> ScreenAnswer:
    """The stored form of a live screen result."""
    findings = [
        ScreenFinding(
            rule=f.rule_id,
            shape=f.shape_id,
            context=f.context_id,
            outcome=f.outcome,
            subject=f.subject.qualified_name or f"<anonymous {f.subject.kind}>",
            line=f.location.line,
        )
        for f in result.findings
    ]
    return ScreenAnswer(verdict=result.verdict, findings=tuple(sorted(findings, key=_finding_key)))


def _fields(
    value: Any, where: str, required: frozenset[str], optional: frozenset[str] = frozenset()
) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise CaseFormatError(f"{where}: expected an object, got {type(value).__name__}")
    missing = required - value.keys()
    unknown = value.keys() - required - optional
    if missing or unknown:
        raise CaseFormatError(f"{where}: missing {sorted(missing)}, unknown {sorted(unknown)}")
    return value


def _text(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CaseFormatError(f"{where}: expected non-empty text, got {value!r}")
    return value


def _line(value: Any, where: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise CaseFormatError(f"{where}: expected a line number, got {value!r}")
    return value


def _member(enum: type[_E], value: Any, where: str) -> _E:
    try:
        return enum(value)
    except ValueError:
        raise CaseFormatError(f"{where}: {value!r} is not a {enum.__name__}") from None


def _list(value: Any, where: str) -> list[Any]:
    if not isinstance(value, list):
        raise CaseFormatError(f"{where}: expected a list, got {type(value).__name__}")
    return value


def screen_answer_from_json(value: Any, where: str) -> ScreenAnswer:
    """Read a stored screen answer; its findings must already be in sorted order."""
    data = _fields(value, where, frozenset({"verdict", "findings"}))
    findings = []
    for i, item in enumerate(_list(data["findings"], f"{where}.findings")):
        at = f"{where}.findings[{i}]"
        finding = _fields(
            item, at, frozenset({"rule", "shape", "context", "outcome", "subject", "line"})
        )
        line = finding["line"]
        findings.append(
            ScreenFinding(
                rule=_text(finding["rule"], f"{at}.rule"),
                shape=_text(finding["shape"], f"{at}.shape"),
                context=_member(ContextId, finding["context"], f"{at}.context"),
                outcome=_member(Outcome, finding["outcome"], f"{at}.outcome"),
                subject=_text(finding["subject"], f"{at}.subject"),
                line=None if line is None else _line(line, f"{at}.line"),
            )
        )
    if findings != sorted(findings, key=_finding_key):
        raise CaseFormatError(f"{where}.findings: not in sorted order")
    return ScreenAnswer(
        verdict=_member(Verdict, data["verdict"], f"{where}.verdict"), findings=tuple(findings)
    )


def screen_answer_to_json(answer: ScreenAnswer) -> dict[str, Any]:
    return {
        "verdict": answer.verdict.value,
        "findings": [
            {
                "rule": f.rule,
                "shape": f.shape,
                "context": f.context.value,
                "outcome": f.outcome.value,
                "subject": f.subject,
                "line": f.line,
            }
            for f in answer.findings
        ],
    }


def _cases_root() -> Path:
    root = resources.files("agentic_mbse.sysml").joinpath("subset_cases")
    if not isinstance(root, Path):
        raise CaseFormatError(
            f"the packaged cases are not on the file system ({root!r}); "
            "a case is a model directory, so the package must be installed unzipped"
        )
    return root


def packaged_case_ids() -> tuple[str, ...]:
    """Every packaged case, by directory name, sorted."""
    return tuple(sorted(d.name for d in _cases_root().iterdir() if d.is_dir()))


def packaged_case_dir(case_id: str) -> Path:
    directory = _cases_root() / case_id
    if not (directory / _CASE_FILE).is_file():
        raise CaseFormatError(f"no packaged case {case_id!r}")
    return directory


def load_packaged_case(case_id: str) -> PackagedCase:
    """Read and check ``subset_cases/<case_id>/case.json``."""
    return load_case(packaged_case_dir(case_id))


def load_case(directory: Path) -> PackagedCase:
    """Read and check ``<directory>/case.json``; the directory name is the case id."""
    case_id = directory.name
    where = f"{case_id}/{_CASE_FILE}"
    data = _fields(
        json.loads((directory / _CASE_FILE).read_text(encoding="utf-8")),
        where,
        frozenset(
            {"schema", "kind", "construct", "screen", "agentic_site_witnesses", "provenance"}
        ),
    )
    if data["schema"] != CASE_SCHEMA:
        raise CaseFormatError(f"{where}.schema: expected {CASE_SCHEMA!r}, got {data['schema']!r}")
    construct = _fields(
        data["construct"], f"{where}.construct", frozenset({"file", "lines", "description"})
    )
    lines = _list(construct["lines"], f"{where}.construct.lines")
    if len(lines) != 2:
        raise CaseFormatError(f"{where}.construct.lines: expected [first, last], got {lines!r}")
    first, last = (_line(n, f"{where}.construct.lines") for n in lines)
    if first > last:
        raise CaseFormatError(f"{where}.construct.lines: first {first} is after last {last}")
    file = _text(construct["file"], f"{where}.construct.file")
    if not (file.endswith(".sysml") and (directory / file).is_file()):
        raise CaseFormatError(f"{where}.construct.file: {file!r} is not a model file of the case")
    provenance = _fields(
        data["provenance"], f"{where}.provenance", frozenset({"note"}), frozenset({"from_probe"})
    )
    from_probe = provenance.get("from_probe")
    return PackagedCase(
        case_id=case_id,
        kind=_member(CaseKind, data["kind"], f"{where}.kind"),
        directory=directory,
        construct=Construct(
            file=file,
            first_line=first,
            last_line=last,
            description=_text(construct["description"], f"{where}.construct.description"),
        ),
        screen=screen_answer_from_json(data["screen"], f"{where}.screen"),
        agentic_site_witnesses=tuple(
            _text(s, f"{where}.agentic_site_witnesses")
            for s in _list(data["agentic_site_witnesses"], f"{where}.agentic_site_witnesses")
        ),
        from_probe=None
        if from_probe is None
        else _text(from_probe, f"{where}.provenance.from_probe"),
        note=_text(provenance["note"], f"{where}.provenance.note"),
    )
