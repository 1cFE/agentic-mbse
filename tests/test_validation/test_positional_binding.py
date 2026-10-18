"""The positional-binding fixture suite: every fixture gives exactly its header's results.

Each fixture under `tests/fixtures/positional_binding/` states what it must produce in a comment
header: one `// finding: owner | input | target [| SPECIAL_SLOT]` line per expected finding
(`<none>` for an owner without a qualified name), one `// unverifiable: CAUSE @ file:line` line
per expected failure, or `none` for either. A single `.sysml` file is a fixture; a directory
holding an `expect.txt` is a multi-file fixture loaded whole, with its header in that file.
`native_values/`, `l1/` and `baselines/` hold no L2 fixtures and are skipped.

The 17 `prototype/` fixtures reproduce `04-detector-fixtures.log` (spec Det-1). The 9 marked
`naive-control: wrong` are the ones a detector comparing name sets gets wrong (Det-2).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from agentic_mbse.sysml.parameter_redefinition_extraction import extract_parameter_redefinitions
from agentic_mbse.sysml.syside_adapter import SysideAdapter, get_syside
from agentic_mbse.sysml.types import Severity, ValidationCode
from agentic_mbse.validation.level1_syntax import validate_syntax
from agentic_mbse.validation.level2_structure import validate_structure
from agentic_mbse.validation.positional_binding import (
    FindingReason,
    InputOutcome,
    PositionalResult,
    decide,
)

syside = get_syside()

FIX = Path(__file__).parent.parent / "fixtures" / "positional_binding"
NOT_L2_FIXTURES = ("native_values", "l1", "baselines")
NO_OWNER = "<none>"

Finding = tuple[str, str, str, FindingReason]
Unverifiable = tuple[str, str]


@dataclass(frozen=True)
class Fixture:
    load_root: Path
    header: Path

    @property
    def base(self) -> Path:
        """What a failure's file is reported relative to."""
        return self.load_root if self.load_root.is_dir() else self.load_root.parent

    def __str__(self) -> str:
        return str(self.load_root.relative_to(FIX))


@dataclass(frozen=True)
class Expectation:
    findings: frozenset[Finding]
    unverifiable: frozenset[Unverifiable]
    naive_control_wrong: bool


def all_fixtures() -> list[Fixture]:
    directories = sorted(p.parent for p in FIX.rglob("expect.txt"))
    fixtures = [Fixture(d, d / "expect.txt") for d in directories]
    for path in sorted(FIX.rglob("*.sysml")):
        relative = path.relative_to(FIX)
        if relative.parts[0] in NOT_L2_FIXTURES:
            continue
        if any(d in path.parents for d in directories):
            continue
        fixtures.append(Fixture(path, path))
    return sorted(fixtures, key=str)


_FINDING = re.compile(r"^// finding: (.*)$")
_UNVERIFIABLE = re.compile(r"^// unverifiable: (.*)$")


def parse_header(fixture: Fixture) -> Expectation:
    findings: set[Finding] = set()
    unverifiable: set[Unverifiable] = set()
    saw_finding = saw_unverifiable = False
    naive = False
    for line in fixture.header.read_text().splitlines():
        if not line.startswith("//"):
            break
        if match := _FINDING.match(line):
            saw_finding = True
            if match[1].strip() == "none":
                continue
            parts = [part.strip() for part in match[1].split("|")]
            reason = (
                FindingReason.SPECIAL_SLOT if parts[3:] == ["SPECIAL_SLOT"] else FindingReason.SWAP
            )
            assert parts[3:] in ([], ["SPECIAL_SLOT"]), line
            findings.add((parts[0], parts[1], parts[2], reason))
        elif match := _UNVERIFIABLE.match(line):
            saw_unverifiable = True
            if match[1].strip() == "none":
                continue
            cause, where = (part.strip() for part in match[1].split("@"))
            unverifiable.add((cause, where))
        elif line.startswith("// naive-control: wrong"):
            naive = True
    assert saw_finding and saw_unverifiable, (
        f"{fixture} header states no finding or unverifiable line"
    )
    return Expectation(frozenset(findings), frozenset(unverifiable), naive)


def load(fixture: Fixture) -> Any:
    model, _ = SysideAdapter.load_model([fixture.load_root])
    return model


def run(fixture: Fixture) -> PositionalResult:
    return decide(extract_parameter_redefinitions(load(fixture)), None)


def found(result: PositionalResult) -> set[Finding]:
    return {
        (
            f.owner.qualified_name or NO_OWNER,
            f.input_name,
            f.target.formal.qualified_name or NO_OWNER,
            f.reason,
        )
        for f in result.findings
    }


def unverifiable(result: PositionalResult, fixture: Fixture) -> set[Unverifiable]:
    reported: set[Unverifiable] = set()
    for failure in result.failures:
        assert failure.subject is not None and failure.subject.file is not None
        path = Path(failure.subject.file).resolve().relative_to(fixture.base.resolve())
        reported.add((failure.cause.value, f"{path}:{failure.subject.line}"))
    return reported


FIXTURES = all_fixtures()


def test_the_suite_covers_every_appendix_a_group() -> None:
    groups = Counter(Path(str(f)).parts[0] for f in FIXTURES)
    assert groups == {
        "prototype": 17,
        "spelling": 2,
        "types": 5,
        "requirements": 9,
        "dc3": 2,
        "unresolved": 4,
        "partial_run": 2,
        "partial_scope": 1,
    }


@pytest.mark.parametrize("fixture", FIXTURES, ids=str)
def test_fixture_gives_exactly_its_header_results(fixture: Fixture) -> None:
    expected = parse_header(fixture)
    result = run(fixture)
    assert found(result) == expected.findings
    assert unverifiable(result, fixture) == expected.unverifiable


def test_the_prototype_fixtures_reproduce_the_prototype_outcome_totals() -> None:
    """`04-detector-fixtures.log`: explicit 9, new_parameter 75, implicit_mismatch 15,
    anonymous 2, implicit_matching 9. None of the 17 has a special role or unnamed target."""
    totals: Counter[InputOutcome] = Counter()
    for fixture in FIXTURES:
        if str(fixture).startswith("prototype/"):
            totals.update(run(fixture).outcomes)
    assert +totals == {
        InputOutcome.EXPLICIT: 9,
        InputOutcome.NEW_PARAMETER: 75,
        InputOutcome.IMPLICIT_MISMATCH: 15,
        InputOutcome.ANONYMOUS: 2,
        InputOutcome.IMPLICIT_MATCHING: 9,
    }


def test_inherit_def_extends_gives_no_finding_and_no_unverifiable_result() -> None:
    """Spec Insp-2: unverifiable only from a real evidence failure."""
    (fixture,) = [f for f in FIXTURES if str(f) == "prototype/inherit_def_extends.sysml"]
    result = run(fixture)
    assert result.findings == ()
    assert result.failures == ()
    assert result.inputs_inspected > 0


def test_unresolved_owners_never_count_their_inputs_as_new_parameters() -> None:
    (fixture,) = [f for f in FIXTURES if str(f) == "unresolved/unresolved_type.sysml"]
    result = run(fixture)
    # Only the resolved Sub and Le definitions' own inputs are judged.
    assert result.outcomes[InputOutcome.NEW_PARAMETER] == 4
    assert result.inputs_inspected == 4


# ---- the naive control (spec Det-2) -----------------------------------------------------------


_IN = {syside.FeatureDirectionKind.In, syside.FeatureDirectionKind.Inout}


def naive_flags(model: Any) -> bool:
    """The prototype's control (`04-detector.py:naive_scan`): a usage input whose name is not
    among its types' input names. It compares name sets and never reads redefinitions."""
    for kind in (syside.CalculationUsage, syside.ConstraintUsage):
        for usage in model.elements(kind, include_subtypes=True):
            formal_names = {
                f.name
                for typ in usage.types.collect()
                for f in typ.features.collect()
                if f.direction in _IN and f.name
            }
            if not formal_names:
                continue
            for f in usage.owned_features.collect():
                if f.direction in _IN and f.declared_name and f.declared_name not in formal_names:
                    return True
    return False


def test_a_name_set_detector_fails_exactly_the_nine_marked_fixtures() -> None:
    wrong = set()
    for fixture in FIXTURES:
        if not str(fixture).startswith("prototype/"):
            continue
        expected_flag = bool(parse_header(fixture).findings)
        if naive_flags(load(fixture)) != expected_flag:
            wrong.add(str(fixture))
    marked = {str(f) for f in FIXTURES if parse_header(f).naive_control_wrong}
    assert wrong == marked
    assert len(wrong) == 9


def test_out_before_in_passes_l1_and_fails_l2_on_two_positional_errors(tmp_path: Path) -> None:
    """Current behavior the register states (`semantic-hazards.md`, "An `out` parameter counts").

    The design expected `validate` to reject this model at L1 (Det-6 row, open for the owner).
    SysIDE's direction error is in `diagnostics.validation`, which no level reads
    (backlog VALIDATE-SEMA-DIAGNOSTICS), so L2's positional check is what catches it.
    """
    source = FIX / "l1" / "out_before_in.sysml"
    _, diagnostics = SysideAdapter.load_model([source])
    assert list(diagnostics.parser) == []
    assert list(diagnostics.sema) == []
    assert "redefinition-direction-conformance" in {
        str(d.code) for d in diagnostics.validation if d.severity == syside.DiagnosticSeverity.Error
    }

    models = tmp_path / "models"
    models.mkdir()
    (models / source.name).write_text(source.read_text())
    assert validate_syntax(str(models)).success
    level2 = validate_structure(str(models))
    assert not level2.success
    positional = [
        (i.severity, i.reason_code, re.search(r'input = "(\w+)", target = "([^"]+)"', i.message))
        for i in level2.structured_issues
        if i.code is ValidationCode.L2_POSITIONAL_BINDING
    ]
    assert sorted((severity, reason, m.groups()) for severity, reason, m in positional if m) == [
        (Severity.ERROR, "POSITIONAL_SWAP", ("a", "out_before_in::O::o")),
        (Severity.ERROR, "POSITIONAL_SWAP", ("b", "out_before_in::O::a")),
    ]
    assert len(positional) == 2
