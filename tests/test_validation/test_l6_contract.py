"""L6 runs the subset contract first and shows it through the execution target (Item 3 Phase 5).

Spec § Presentation, § Structured report, § Both String spellings (test half), § Library
additions bullets 1, 2 and 4, § Check failures bullets 4 and 5, § Settings states bullets 1-3.
Each fixture under `tests/fixtures/l6/contract/<name>/models/` gives one verdict or shape; the
tests copy it into a project in `tmp_path` and run `validate --level=6 --json-report`.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from agentic_mbse.sysml.subset_advisories import Advisories
from agentic_mbse.sysml.subset_coverage import NO_RULE_FAMILIES, SUBSET_COVERAGE_VERSION
from agentic_mbse.sysml.subset_extraction import extract_subset_facts
from agentic_mbse.sysml.subset_facts import BindingKind
from agentic_mbse.sysml.subset_profile import (
    SUBSET_PROFILE_VERSION,
    ExplicitRoots,
    Outcome,
    SubsetProfileResult,
    Verdict,
    evaluate_subset_profile,
)
from agentic_mbse.sysml.syside_adapter import SysideAdapter
from agentic_mbse.sysml.types import ValidationCode
from agentic_mbse.validation import level6_architecture, runner
from agentic_mbse.validation.common import AggregatedResult, QualityCheckResult
from agentic_mbse.validation.execution_target import Target
from agentic_mbse.validation.report import build_report
from agentic_mbse.validation.subset_presentation import present
from tests.helpers import subset_synthetic as syn
from tests.helpers.l6_projects import make_project, run_cli, target_table

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
CONTRACT = FIXTURES / "l6" / "contract"
TARGETS = ["unset", "generated", "native"]

VERDICT_FIXTURES = sorted(path.name for path in CONTRACT.iterdir() if path.is_dir())
BANNED = [
    "generated-ready",
    "generation-ready",
    "ready to generate",
    "will generate",
    "generator accepts",
    "readiness",
]
VERDICT_KEY = f"Generator subset ({SUBSET_PROFILE_VERSION}, {SUBSET_COVERAGE_VERSION})"
NOTE = "generated compatibility not established"
NO_ADVISORIES = Advisories(findings=(), unverified=())


class Run:
    def __init__(self, code: int, out: str, report: dict[str, Any]) -> None:
        self.code, self.out, self.report = code, out, report
        (self.l6,) = report["levels"]
        self.profile = self.l6["profile"]

    @property
    def verdict_line(self) -> str:
        return self.l6["metrics"][VERDICT_KEY]

    def issues(self, code: ValidationCode | None = None) -> list[dict[str, Any]]:
        return [i for i in self.l6["issues"] if code is None or i["code"] == code.value]

    def findings(self, rule: str | None = None) -> list[dict[str, Any]]:
        return [f for f in self.profile["findings"] if rule is None or f["rule_id"] == rule]

    def printed_issue_lines(self) -> list[str]:
        return [line.strip()[2:] for line in self.out.splitlines() if line.startswith("   - ")]


def _models(name: str) -> dict[str, str]:
    root = CONTRACT / name / "models"
    return {str(p.relative_to(root)): p.read_text() for p in sorted(root.rglob("*.sysml"))}


@pytest.fixture(scope="module")
def l6(tmp_path_factory: pytest.TempPathFactory) -> Callable[[str, str], Run]:
    """`l6(name, target)`: one `validate --level=6` run of a fixture, cached per module."""
    runs: dict[tuple[str, str], Run] = {}

    def run(name: str, target: str) -> Run:
        if (name, target) not in runs:
            parent = tmp_path_factory.mktemp(f"{name}-{target}")
            pyproject = None if target == "unset" else target_table(f'"{target}"')
            models = make_project(parent, pyproject=pyproject, models=_models(name))
            path = parent / "report.json"
            code, out = run_cli("validate", "--level=6", "--json-report", str(path), str(models))
            runs[name, target] = Run(code, out, json.loads(path.read_text()))
        return runs[name, target]

    return run


# ---- wording ----------------------------------------------------------------------------------


@pytest.mark.syside
@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("name", VERDICT_FIXTURES)
def test_stdout_and_report_have_no_banned_wording(l6, name, target):  # I9
    run = l6(name, target)
    text = (run.out + json.dumps(run.report)).lower()
    assert [phrase for phrase in BANNED if phrase in text] == []


@pytest.mark.syside
@pytest.mark.parametrize("target", TARGETS)
@pytest.mark.parametrize("name", VERDICT_FIXTURES)
def test_verdict_line_fields_and_never_clean_ready_passed(l6, name, target):
    run = l6(name, target)
    line = run.verdict_line
    assert f"{VERDICT_KEY}: {line}" in run.out
    assert line.startswith(f"{run.profile['verdict']}:")
    for field in (" refused", " unverified", " unassessed constraints", "not a generation check"):
        assert field in line
    for word in ("clean", "ready", "passed"):
        assert word not in line.lower()


@pytest.mark.syside
def test_level_title_is_architecture_and_generator_subset(l6):
    run = l6("clear", "unset")
    assert "Level 6: Architecture & Generator Subset" in run.out
    assert run.l6["name"] == "Architecture & Generator Subset"
    assert runner.QUALITY_CHECKS[5][0] == "Level 6: Architecture & Generator Subset"
    assert level6_architecture.LEVEL_NAME == "Architecture & Generator Subset"


# ---- exit code, note and final line by target ------------------------------------------------


@pytest.mark.syside
@pytest.mark.parametrize(("target", "code"), [("generated", 1), ("native", 0), ("unset", 0)])
def test_one_refused_finding_exit_code_by_target(l6, target, code):
    run = l6("refused", target)
    assert run.code == code
    assert len(run.findings("binding-source")) == 1
    assert ("Execution target note:" in run.out) is (target == "unset")
    if target == "unset":
        assert f"✅ Quality checks passed with {NOTE}" in run.out


@pytest.mark.syside
def test_unset_note_printed_even_with_no_generator_findings(l6):
    run = l6("clear", "unset")
    assert run.profile["findings"] == [] or all(
        f["outcome"] == "admitted" for f in run.profile["findings"]
    )
    assert (
        "Execution target note: generator findings are shown as warnings because "
        "execution-target is not set." in run.out
    )
    assert 'execution-target = "generated" or "native" under [tool.agentic-mbse]' in run.out
    assert "agentic-mbse init --execution-target=generated|native" in run.out


@pytest.mark.syside
@pytest.mark.parametrize(
    ("name", "target", "noted"),
    [
        ("clear", "unset", True),
        ("clear", "generated", True),
        ("clear", "native", False),
    ],
)
def test_final_line_says_generated_compatibility_not_established(l6, name, target, noted):
    run = l6(name, target)
    assert run.code == 0
    assert (f"✅ Quality checks passed with {NOTE}" in run.out) is noted
    assert (run.report["pass_notes"] == [NOTE]) is noted
    if not noted:
        assert "✅ All quality checks passed!" in run.out


# ---- verdicts -------------------------------------------------------------------------------


@pytest.mark.syside
def test_refused_incomplete_puts_refused_count_before_incomplete(l6):
    run = l6("refused_incomplete", "generated")
    line = run.verdict_line
    assert line.startswith("refused_incomplete: 1 refused, then incomplete: 1 unverified;")
    assert line.index("1 refused") < line.index("then incomplete")


@pytest.mark.syside
def test_refusals_print_first_under_generated(l6):  # D13
    run = l6("refused_incomplete", "generated")
    lines = run.printed_issue_lines()
    assert lines[0].startswith(f"ERROR: refused ({SUBSET_PROFILE_VERSION}): invocation-callable/")
    assert lines[1].startswith(f"ERROR: unverified ({SUBSET_PROFILE_VERSION}): indexed-reference")


@pytest.mark.syside
def test_clear_line_and_coverage_limit_line(l6):
    run = l6("clear", "generated")
    lines = run.out.splitlines()
    (at,) = [i for i, line in enumerate(lines) if VERDICT_KEY in line]
    assert lines[at].strip() == (
        f"{VERDICT_KEY}: clear: no refusals found by the implemented rules; 0 refused; "
        "0 unverified; 0 unassessed constraints; not a generation check"
    )
    coverage = lines[at + 1].strip()
    assert coverage.startswith("Coverage limit: no rule yet for " + ", ".join(NO_RULE_FAMILIES))
    assert coverage.endswith("follow-up sites; a clear verdict says nothing about these")
    assert (
        lines[at + 2]
        .strip()
        .startswith("Generator subset scope: executable profile executable-profile/")
    )
    assert "roots used 1 of 1 (not narrowed); fact kinds not enumerated: none" in lines[at + 2]


@pytest.mark.syside
def test_incomplete_fails_under_generated_and_warns_under_unset(l6):
    generated, unset = l6("incomplete", "generated"), l6("incomplete", "unset")
    assert generated.verdict_line.startswith("incomplete: 0 refused; 1 unverified;")
    assert generated.code == 1
    assert [i["severity"] for i in generated.issues(ValidationCode.L6_SUBSET_UNVERIFIED)] == [
        "error"
    ]
    assert unset.code == 0
    assert [i["severity"] for i in unset.issues(ValidationCode.L6_SUBSET_UNVERIFIED)] == ["warning"]
    assert "Execution target note:" in unset.out


@pytest.mark.syside
@pytest.mark.parametrize("target", ["generated", "unset"])
def test_unconfirmed_is_never_error_and_names_by_design_context(l6, target):
    plain = l6("unconfirmed_calc_result", target)
    assert plain.verdict_line.startswith("unconfirmed: 1 unconfirmed; 0 refused; 0 unverified;")
    (issue,) = plain.issues(ValidationCode.L6_SUBSET_UNCONFIRMED)
    assert issue["severity"] == "warning"
    assert issue["message"].endswith("; no generator probe has observed this")
    assert "unconfirmed by design" not in issue["message"]

    beneath = l6("beneath_refused_multiplicity", target)
    (issue,) = beneath.issues(ValidationCode.L6_SUBSET_UNCONFIRMED)
    assert issue["severity"] == "warning"
    assert "in beneath_refused_multiplicity:" in issue["message"]
    assert "; context beneath_refused_multiplicity is unconfirmed by design" in issue["message"]


@pytest.mark.syside
def test_assertion_owned_by_an_action_def_is_refused(l6):
    """Item 3's first `unconfirmed` fixture; Item 2a's v2 records refuse an owner codegen cannot attach."""
    run = l6("action_owned_assertion", "generated")
    assert run.verdict_line.startswith("refused: 1 refused; 0 unverified;")
    (finding,) = run.findings("calc-owned-assertion")
    assert (finding["shape_id"], finding["context_id"], finding["outcome"]) == (
        "asserted_constraint",
        "unmapped_owner_kind",
        "refused",
    )


def _beyond_generator_roots_result() -> SubsetProfileResult:
    """The widened-roots model evaluated with a caller root: one unconfirmed finding, by design."""
    model, _ = SysideAdapter.load_model([FIXTURES / "subset_profile/cases/widened_roots.sysml"])
    template = next(
        u
        for u in SysideAdapter.elements_of_type(model, "PartUsage")
        if str(u.qualified_name) == "wr::Templates::site"
    )
    facts = extract_subset_facts(model, extra_roots=(template,))
    assert facts.occurrence is not None
    roots = {*facts.occurrence.generator_root_ids, *facts.occurrence.caller_root_ids}
    return evaluate_subset_profile(facts, roots=ExplicitRoots(frozenset(roots)))


@pytest.mark.syside
def test_unconfirmed_verdict_sets_the_pass_note_and_raises_no_error():
    """Final line for an `unconfirmed` verdict under `generated` and unset.

    Built from an evaluated result, not a CLI run: under subset-profile/v2 every unconfirmed
    pair a model can reach under the generator's roots comes with an L6 error or a refusal
    (Item 2a records each one as observed or unobservable), so no fixture run passes with it.
    """
    result = _beyond_generator_roots_result()
    assert result.verdict is Verdict.UNCONFIRMED
    for target in (Target.UNSET, Target.GENERATED):
        check = present(target, result, NO_ADVISORIES, [])
        assert check.pass_note == NOTE
        assert [i.severity.value for i in check.issues] == ["warning"]


@pytest.mark.syside
def test_beyond_generator_roots_message_names_the_context():
    """L6 evaluates with the generator's roots, so it never sees this context; the renderer does."""
    result = _beyond_generator_roots_result()
    for target in (Target.UNSET, Target.GENERATED):
        (issue,) = [
            i
            for i in present(target, result, NO_ADVISORIES, []).issues
            if i.code.value == "L6_SUBSET_UNCONFIRMED"
        ]
        assert issue.severity.value == "warning"
        assert "; context beyond_generator_roots is unconfirmed by design" in issue.message


@pytest.mark.syside
def test_b8_shadowed_by_names_the_refused_finding_and_outcome_stays_unconfirmed(l6):
    run = l6("b8_shadowed", "generated")
    (predicate,) = run.findings("constraint-predicate")
    (assertion,) = run.findings("calc-owned-assertion")
    assert predicate["outcome"] == "unconfirmed"
    assert predicate["subject"]["element_id"] == assertion["subject"]["element_id"]
    assert predicate["shadowed_by"] == {
        "rule_id": "calc-owned-assertion",
        "shape_id": "asserted_constraint",
        "element_id": assertion["subject"]["element_id"],
    }
    assert assertion["shadowed_by"] is None
    (issue,) = run.issues(ValidationCode.L6_SUBSET_UNCONFIRMED)
    assert issue["severity"] == "warning"
    assert (
        "shadowed by refused calc-owned-assertion/asserted_constraint on the same declaration"
        in issue["message"]
    )
    # D13: the refusal leads, then the legacy warning, then the contract's unconfirmed one.
    assert [i["code"] for i in run.issues()] == [
        "L6_SUBSET_REFUSED",
        "L6_CONSTRAINT_NON_NUMERICAL",
        "L6_SUBSET_UNCONFIRMED",
    ]


@pytest.mark.syside
def test_unverified_error_generated_warning_unset_separate_warning_native(l6):
    generated = l6("refused_incomplete", "generated")
    unset = l6("refused_incomplete", "unset")
    native = l6("refused_incomplete", "native")
    assert [i["severity"] for i in generated.issues(ValidationCode.L6_SUBSET_UNVERIFIED)] == [
        "error"
    ]
    assert [i["severity"] for i in unset.issues(ValidationCode.L6_SUBSET_UNVERIFIED)] == ["warning"]
    (aggregated,) = native.issues(ValidationCode.L6_SUBSET_UNVERIFIED)
    assert aggregated["severity"] == "warning"
    assert aggregated["message"] == (
        f"unverified ({SUBSET_PROFILE_VERSION}): 1 subset checks could not run; each is listed in "
        "--json-report"
    )
    assert not [
        i for i in native.l6["summarized"] if i["code"] == ValidationCode.L6_SUBSET_UNVERIFIED.value
    ]
    assert len(native.profile["unverified"]) == 1
    assert native.code == 0


@pytest.mark.syside
def test_excluded_is_warning_with_reason_under_generated(l6):
    run = l6("excluded_non_numerical", "generated")
    (issue,) = run.issues(ValidationCode.L6_SUBSET_EXCLUDED)
    assert issue["severity"] == "warning"
    assert issue["reason_code"] == "constraint_predicate_non_numerical"
    assert run.code == 0


@pytest.mark.syside
@pytest.mark.parametrize("target", TARGETS)
def test_unassessed_count_in_verdict_line_and_one_warning(l6, target):
    run = l6("clear_unassessed", target)
    assert run.verdict_line.startswith("clear: no refusals found by the implemented rules;")
    assert "; 1 unassessed constraints; not a generation check" in run.verdict_line
    shown = run.issues(ValidationCode.L6_SUBSET_UNASSESSED)
    summarized = [
        i for i in run.l6["summarized"] if i["code"] == ValidationCode.L6_SUBSET_UNASSESSED.value
    ]
    if target == "native":
        assert shown == [] and len(summarized) == 1
        assert (
            "1 unassessed constraints"
            in run.l6["metrics"]["Generator-only findings (native: INFO summary)"]
        )
    else:
        assert summarized == []
        (issue,) = shown
        assert issue["severity"] == "warning"
        assert issue["message"].startswith(f"unassessed ({SUBSET_PROFILE_VERSION}): 1 constraints")


# ---- native ---------------------------------------------------------------------------------


@pytest.mark.syside
def test_native_summary_findings_all_in_report_with_rule_reason_location(l6):
    run = l6("refused_incomplete", "native")
    assert run.l6["metrics"]["Generator-only findings (native: INFO summary)"] == (
        "1 refused, 0 unconfirmed, 0 omitted, 0 excluded, 0 unassessed constraints, "
        "0 advisories, 0 legacy; all listed in --json-report"
    )
    assert run.issues(ValidationCode.L6_SUBSET_REFUSED) == []
    (summarized,) = [
        i for i in run.l6["summarized"] if i["code"] == ValidationCode.L6_SUBSET_REFUSED.value
    ]
    assert summarized["severity"] == "info"
    assert summarized["reason_code"] == "invocation_callable_unsupported"
    assert summarized["location"].endswith("plant.sysml:6")
    assert "invocation-callable/unsupported_callable in attribute_value" in summarized["message"]
    (finding,) = run.findings("invocation-callable")
    assert finding["display"] == "native_summary"
    assert finding["location"]["line"] == 6
    assert finding["remedy"] and finding["semantic_limits"]


@pytest.mark.syside
def test_native_correctness_error_stays_error_under_native(l6):
    run = l6("native_correctness_error", "native")
    (issue,) = run.issues(ValidationCode.L6_CALC_DEF_NO_OUTPUT)
    assert issue["severity"] == "error"
    assert run.code == 1


# ---- Strings (D10, B6) ----------------------------------------------------------------------


@pytest.mark.syside
@pytest.mark.parametrize("target", TARGETS)
def test_both_string_spellings_inside_and_outside_designs_are_omitted_no_unextractable(l6, target):
    run = l6("strings_both_spellings", target)
    strings = run.findings("string-value-omission")
    assert {f["subject"]["qualified_name"] for f in strings} == {
        "gd::Gen::fuel",
        "gd::Gen::label",
        "gd::gen::fuel",
        "gl::Gen::fuel",
        "gl::Gen::label",
        "gl::gen::fuel",
    }
    assert {f["subject"]["kind"] for f in strings} == {"AttributeUsage", "ReferenceUsage"}
    assert {(f["outcome"], f["reason"]) for f in strings} == {
        ("omitted", "string_value_not_generated")
    }
    expected = "native_summary" if target == "native" else "warning"
    assert {f["display"] for f in strings} == {expected}
    assert run.issues(ValidationCode.L6_DESIGN_ATTR_UNEXTRACTABLE) == []
    assert run.code == 0


@pytest.mark.syside
def test_string_outside_every_generator_root_is_still_omitted(l6):  # B6
    run = l6("string_outside_roots", "unset")
    assert {f["subject"]["qualified_name"] for f in run.findings("string-value-omission")} == {
        "orphan::Orphan::label",
        "orphan::Tag::name",
    }
    assert run.issues(ValidationCode.L6_DESIGN_ATTR_UNEXTRACTABLE) == []
    assert run.code == 0


# ---- UNSUPPORTED-RHS and MULTIPLICITY-SHAPE -------------------------------------------------


@pytest.mark.syside
def test_invocation_callable_at_attribute_and_part_multiplicity_unresolved_reported(l6):
    run = l6("invocation_rhs_and_multiplicity", "generated")
    refused = {
        (f["rule_id"], f["shape_id"], f["context_id"], f["subject"]["qualified_name"])
        for f in run.findings()
        if f["outcome"] == "refused"
    }
    assert refused == {
        ("invocation-callable", "unsupported_callable", "attribute_value", "fx::Site::eff"),
        ("part-multiplicity", "unresolved_bound", "expanded_part_usage", "fx::Rack::servers"),
    }
    messages = [i["message"] for i in run.issues(ValidationCode.L6_SUBSET_REFUSED)]
    assert any("part-multiplicity/unresolved_bound in expanded_part_usage" in m for m in messages)
    assert any("invocation-callable/unsupported_callable in attribute_value" in m for m in messages)
    assert run.code == 1


# ---- contract crash -------------------------------------------------------------------------


@pytest.mark.syside
@pytest.mark.parametrize("target", TARGETS)
def test_contract_crash_is_check_error_under_every_target(monkeypatch, tmp_path, target):
    def boom(*args: object, **kwargs: object) -> None:
        raise RuntimeError("boom")

    monkeypatch.setattr(level6_architecture, "evaluate_subset_profile", boom)
    pyproject = None if target == "unset" else target_table(f'"{target}"')
    models = make_project(tmp_path, pyproject=pyproject, models=_models("strings_both_spellings"))
    path = tmp_path / "report.json"
    code, out = run_cli("validate", "--level=6", "--json-report", str(path), str(models))
    run = Run(code, out, json.loads(path.read_text()))
    assert code == 1
    (error,) = run.issues(ValidationCode.L6_CHECK_ERROR)
    assert error["severity"] == "error"
    assert (
        error["message"] == "subset_profile could not inspect the loaded model: RuntimeError: boom"
    )
    assert run.issues()[0] == error  # check errors print first (D13)
    assert run.verdict_line == "not computed (see L6_CHECK_ERROR)"
    assert run.profile["verdict"] is None and run.profile["check_errors"] == [
        {k: v for k, v in error.items() if k != "display"}
    ]
    # With no contract result, the legacy String errors stay (D10).
    assert run.issues(ValidationCode.L6_DESIGN_ATTR_UNEXTRACTABLE)
    assert run.l6["summarized"] == []


# ---- the report at dc3's size ---------------------------------------------------------------


def _dc3_sized() -> syn.SubsetFacts:
    """236 refused bindings, each in its own instantiated calc usage, and 32 String values."""
    scope = syn.occ("fx::p")
    usages = [f"fx::P::t{n}" for n in range(236)]
    return syn.facts(
        occurrence=syn.structure(
            roots=["fx::p"],
            calc=[syn.attached(u, "fx::P", [scope]) for u in usages],
            writers=[syn.writer(u, scope, u, [u]) for u in usages],
        ),
        bindings=[
            syn.binding(u, f"{u}::xs", BindingKind.OTHER_EXPRESSION, 10 + n)
            for n, u in enumerate(usages)
        ],
        strings=[syn.string(f"fx::P::s{n}", 400 + n) for n in range(32)],
    )


@pytest.mark.parametrize("target", [Target.GENERATED, Target.NATIVE])
def test_dc3_sized_report_holds_every_evaluator_finding(target, capsys):
    result = evaluate_subset_profile(_dc3_sized())
    assert result.verdict is Verdict.REFUSED
    counts = dict(result.counts.by_outcome)
    assert (counts[Outcome.REFUSED], counts[Outcome.OMITTED]) == (236, 32)

    shown = present(target, result, NO_ADVISORIES, [])
    level = QualityCheckResult(
        level=6,
        level_name=level6_architecture.LEVEL_NAME,
        success=not shown.issues,
        summarized=shown.summarized,
        report_detail=shown.profile,
        metrics=shown.metrics,
    )
    for issue in shown.issues:
        level.add_issue(issue)
    aggregated = AggregatedResult([level], 1, 0, 1, 0, 0.0)
    report = build_report(aggregated, {"path": "models"}, 1)
    (l6,) = report["levels"]
    assert len(l6["profile"]["findings"]) == len(result.findings) == 268
    listed = l6["issues"] if target is Target.GENERATED else l6["summarized"]
    assert len(listed) == 268
    assert {f["display"] for f in l6["profile"]["findings"]} == (
        {"error", "warning"} if target is Target.GENERATED else {"native_summary"}
    )

    # The text output keeps its truncation; the report does not.
    from agentic_mbse.validation.common import print_result

    print_result(level)
    printed = capsys.readouterr().out
    if target is Target.GENERATED:
        assert "Issues found: 268" in printed and "... and 263 more" in printed


# ---- legacy codes under native (Phase 8) --------------------------------------------------


def _legacy(code: ValidationCode, severity: str) -> Any:
    from agentic_mbse.sysml.types import Severity, ValidationIssue

    return ValidationIssue(
        level=6, severity=Severity(severity), code=code, message=f"legacy {code.value}"
    )


@pytest.mark.parametrize(
    ("code", "severity"),
    [
        (ValidationCode.L6_MISSING_QUALIFIED_NAME, "error"),
        (ValidationCode.L6_ANONYMOUS_RETURN, "error"),
        (ValidationCode.L6_CALC_DEF_NO_INSTANTIATION, "error"),
        (ValidationCode.L6_BODY_ASSIGNMENT_IMPL_LOSS, "warning"),
    ],
)
def test_lowered_code_is_native_summary_under_native_and_unchanged_under_others(code, severity):
    issue = _legacy(code, severity)
    for target in (Target.UNSET, Target.GENERATED):
        shown = present(target, None, NO_ADVISORIES, [issue])
        assert [(i.code, i.severity.value) for i in shown.issues] == [(code, severity)]
        assert shown.summarized == []
    shown = present(Target.NATIVE, None, NO_ADVISORIES, [issue])
    assert [i.code for i in shown.issues] == []
    assert [(i.code, i.severity.value) for i in shown.summarized] == [(code, "info")]
    assert ", 1 legacy;" in shown.metrics["Generator-only findings (native: INFO summary)"]


@pytest.mark.parametrize(
    ("code", "severity"),
    [
        (ValidationCode.L6_INVALID_QUALIFIED_NAME, "error"),
        (ValidationCode.L6_INVALID_BINDING_FORMAT, "error"),
        (ValidationCode.L6_DESIGN_ATTR_INCOMPLETE, "error"),
        (ValidationCode.L6_DESIGN_ATTR_UNEXTRACTABLE, "error"),
        (ValidationCode.L6_CALC_DEF_NO_OUTPUT, "error"),
        (ValidationCode.L6_ATTR_REDEF_EXPR_DROPPED, "warning"),
        (ValidationCode.V4_STATIC_FUNCTION_INVOCATION, "warning"),
        (ValidationCode.L6_CONSTRAINT_NON_NUMERICAL, "warning"),
        (ValidationCode.V2_DYNAMIC_EXPRESSION, "error"),
    ],
)
def test_kept_code_unchanged_under_every_target(code, severity):
    issue = _legacy(code, severity)
    for target in Target:
        shown = present(target, None, NO_ADVISORIES, [issue])
        assert [(i.code, i.severity.value) for i in shown.issues] == [(code, severity)]
        assert shown.summarized == []
